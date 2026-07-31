#!/usr/bin/env python3
"""transcribe_audio.py — the "new transcript" runbook, made executable (dogfooded).

The sequence (see `book/transcript-runbook.md`):

  1. PROBE   each source's duration (ffprobe).
  2. SPLIT   if longer than --split-minutes (default 10) into ~equal chunks on silence-agnostic
             time boundaries (ffmpeg segment) — whisper degrades on very long single passes.
  3. TRANSCRIBE each chunk: decode to 16 kHz mono WAV (ffmpeg), run whisper.cpp large-v3-turbo.
  4. MERGE   the chunk texts back in order into one <stem>.txt (+ a provenance header).
  5. (human, next) REPAIR against the lexicon, then PONDER integration.

stdlib-only; shells out to `ffprobe` / `ffmpeg` / `whisper-cli` (whisper.cpp). No pip deps.

Usage:
  python3 tools/transcribe_audio.py transcript-sources/*.m4a --outdir book/transcripts
"""
from __future__ import annotations

import argparse
import pathlib
import subprocess
import sys
import tempfile

MODEL = pathlib.Path("~/.whisper-models/ggml-large-v3-turbo.bin").expanduser()


def _run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True)


def duration_s(src: pathlib.Path) -> float:
    r = _run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
              "-of", "default=nw=1:nk=1", str(src)])
    return float(r.stdout.strip() or 0.0)


def to_wav(src: pathlib.Path, dst: pathlib.Path, ss: float | None = None, t: float | None = None) -> None:
    cmd = ["ffmpeg", "-y", "-v", "error", "-i", str(src)]
    if ss is not None:
        cmd += ["-ss", f"{ss:.3f}"]
    if t is not None:
        cmd += ["-t", f"{t:.3f}"]
    cmd += ["-ar", "16000", "-ac", "1", str(dst)]  # whisper.cpp wants 16 kHz mono
    r = _run(cmd)
    if r.returncode:
        raise SystemExit(f"ffmpeg failed on {src}: {r.stderr[-500:]}")


def whisper_txt(wav: pathlib.Path, out_prefix: pathlib.Path) -> str:
    r = _run(["whisper-cli", "-m", str(MODEL), "-f", str(wav), "-l", "en",
              "-otxt", "-osrt", "-of", str(out_prefix), "-np"])
    if r.returncode:
        raise SystemExit(f"whisper-cli failed on {wav}: {r.stderr[-500:]}")
    txt = out_prefix.with_suffix(".txt")
    return txt.read_text(encoding="utf-8").strip() if txt.exists() else r.stdout.strip()


def transcribe_one(src: pathlib.Path, outdir: pathlib.Path, split_minutes: float) -> pathlib.Path:
    dur = duration_s(src)
    split_s = split_minutes * 60
    n_chunks = max(1, -(-int(dur) // int(split_s)))  # ceil
    chunk_len = dur / n_chunks if n_chunks > 1 else dur
    parts: list[str] = []
    with tempfile.TemporaryDirectory() as td:
        tdp = pathlib.Path(td)
        for i in range(n_chunks):
            wav = tdp / f"chunk{i}.wav"
            ss = i * chunk_len if n_chunks > 1 else None
            t = chunk_len if n_chunks > 1 else None
            to_wav(src, wav, ss=ss, t=t)
            parts.append(whisper_txt(wav, tdp / f"chunk{i}"))
    body = "\n\n".join(p for p in parts if p)
    header = (
        f"<!-- Provenance: RAW auto-transcript of '{src.name}'. whisper.cpp large-v3-turbo, "
        f"{dur/60:.1f} min"
        + (f", {n_chunks} chunks stitched in order" if n_chunks > 1 else "")
        + ". NOT repaired, NOT integrated — the untouched source of record. Repair pass produces a "
          "sibling .repaired.md aligned to the lexicon; integration is pondered separately. -->\n\n"
        f"# {src.stem}\n\n"
    )
    out = outdir / f"{src.stem}.txt"
    out.write_text(header + body + "\n", encoding="utf-8")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Transcribe audio via the new-transcript runbook.")
    ap.add_argument("sources", nargs="+", type=pathlib.Path)
    ap.add_argument("--outdir", type=pathlib.Path, default=pathlib.Path("book/transcripts"))
    ap.add_argument("--split-minutes", type=float, default=10.0)
    args = ap.parse_args()
    if not MODEL.exists():
        raise SystemExit(f"whisper model not found: {MODEL}")
    args.outdir.mkdir(parents=True, exist_ok=True)
    for src in args.sources:
        dur = duration_s(src)
        print(f"[transcribe] {src.name} ({dur/60:.1f} min)"
              + (" — SPLIT" if dur > args.split_minutes * 60 else ""), flush=True)
        out = transcribe_one(src, args.outdir, args.split_minutes)
        print(f"[done] {out}", flush=True)
    print(f"[all done] {len(args.sources)} transcript(s) in {args.outdir}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
