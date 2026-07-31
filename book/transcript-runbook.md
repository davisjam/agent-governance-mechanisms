# Runbook — turning a new audio note into book material

The book is sourced partly from spoken notes (voice memos, talks). This is the sequence from a raw
recording to integrated book material. It is **executable** for the mechanical steps
(`tools/transcribe_audio.py`) and **judgment** for the rest (repair, integration).

## Where things live

- **Raw source audio/video** → `transcript-sources/` — **gitignored** (multi-MB binaries; the transcript
  is the shipped artifact, not the audio). Co-locate every source here, including talk recordings.
- **Raw transcripts** → `book/transcripts/<stem>.txt` — **tracked**. The untouched source of record.
- **Repaired transcripts** → `book/transcripts/<stem>.repaired.md` — **tracked**. Lexicon-aligned,
  de-noised; the author's words/meaning preserved (de-noising, not rewriting).
- **Lexicon** → `plugin/agent-governance/skills/self-communicate/writing/lexicon.md` — the house
  vocabulary the repair pass aligns terminology to.

## The sequence

1. **Archive.** Copy the source into `transcript-sources/` (never move — leave the original where it
   was). If the archive or its gitignore entry is missing, create them.

2. **Split if > 10 minutes.** whisper degrades on very long single passes, so a long recording is cut
   into ~equal chunks on time boundaries. `transcribe_audio.py` does this automatically
   (`--split-minutes`, default 10); short notes pass through whole.

3. **Transcribe.** Decode each chunk to 16 kHz mono WAV (ffmpeg) and run whisper.cpp
   (`whisper-cli`, model `~/.whisper-models/ggml-large-v3-turbo.bin`). One command does steps 2–4:

   ```
   python3 tools/transcribe_audio.py transcript-sources/*.m4a --outdir book/transcripts
   ```

4. **Merge if split.** The chunk texts are stitched back in order into one `<stem>.txt` with a
   provenance header (done by the driver).

5. **Repair with the lexicon** (judgment). Produce `<stem>.repaired.md` from the raw `.txt`: fix
   whisper mis-hearings (house terms — MAGE, DocAble, MBSE, the thesis names — go through the lexicon),
   add light paragraph breaks, align terminology. **De-noise, do not rewrite:** the author's exact
   words, phrasing, jokes, and meaning are preserved. The raw `.txt` stays the untouched source of
   record. (Model this on `book/anl-talk-transcript.cleaned.md`'s provenance header.)

6. **Ponder integration** (judgment). Each note is usually about one concept. Decide where it belongs:
   which chapter/section, which existing concept it deepens or which gap it fills, whether it becomes
   prose, a figure, an inset, or a lexicon/concept-model entry. Record the disposition; do not force a
   note in where it doesn't earn its place.

## Notes

- **Model selection.** `large-v3-turbo` is the default (accurate + fast on Apple Silicon). The older
  ANL transcript used `base.en`; the turbo model is the current standard.
- **Determinism.** whisper is not bit-deterministic, so a re-transcribe may differ slightly; the raw
  `.txt` is committed once and treated as the source of record thereafter.
