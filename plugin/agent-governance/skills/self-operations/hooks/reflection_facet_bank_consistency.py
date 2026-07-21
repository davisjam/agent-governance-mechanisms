"""reflection_facet_bank_consistency.py — the ``bank_consistency`` reflection facet.

PORTABLE example facet. Reflection dimension: *paired-artifact consistency*.

This facet demonstrates a shape the two shipped facets (recurrence, memory-routing)
do NOT cover: the trigger is a Write/Edit to ONE member of a PAIRED status set, and
the reflection asks about the OTHER member's freshness. You just banked artifact A of
a pair (say a strategy file); artifact B (say a handoff file) is now STALE relative to
A — a resume that reads the pair gets a torn picture. So:

  - **other STALE** (or its mtime is unreadable) → FINISH-THE-BANK nudge: bank the
    OTHER now (ideally via the atomic dual-write banker, which moves both together),
    then keep going.
  - **both FRESH** (the other was banked within the freshness window) → PROCEED
    (silent): the pair is consistent, nothing to say.

This is the SOFT complement to the HARD ``StatusBanker`` (bank_status.py), which makes
the torn state impossible in the happy path by writing both atomically. Because the
atomic banker moves both mtimes together, "both fresh" is the common case and this
facet's nudge narrows to the DEGRADED path — a raw hand-edit of one file that bypassed
the atomic tool.

Fires on the ON_MEMORY_WRITE tempo (a PostToolUse ``Write|Edit``), the same discrete
operator-initiated-write window the memory-routing facet uses — distinct from the
recurring ON_TURN_END tick. Edge-triggered / deduped per the base's window discipline:
the emitter's per-path/per-branch dedupe absorbs a rapid same-branch repeat, and a
branch CHANGE (finish → consistent) is the useful edge that is never suppressed.

PARAMETERIZED. The artifact PAIR is not hardcoded to any project's two files. Set
``REFLECTION_BANK_PAIR`` to two ``os.pathsep``-joined absolute paths (the two files
this project banks together); the freshness window is ``REFLECTION_BANK_FRESH_S``.
Until you point it at a pair it is a safe no-op (a zero-config default).

ADOPTER NOTE — this facet uses a ``FacetKey.BANK_CONSISTENCY`` identity key. Add that
one line to the ``FacetKey`` enum in reflection_facet.py (a new dimension is a new key,
never a free string). Until you do, this module resolves the key defensively so it
still imports; the ``_bank_consistency_key`` shim below is the seam to delete once the
member exists.
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass
from enum import Enum

from reflection_facet import (
    REFLECTION_FACETS,
    FacetKey,
    MaterialPointer,
    ReflectionFacet,
    ReflectionTempo,
    RoutedFollowup,
)

# ---------------------------------------------------------------------------
# Config — the artifact PAIR + the freshness window (portable: set via env var)
# ---------------------------------------------------------------------------

# The two status artifacts this project banks TOGETHER, os.pathsep-joined absolute
# paths. A write to one triggers the consistency check on the OTHER. Default: none
# (the facet is a no-op until you point it at your pair — a safe zero-config default).
_ENV_BANK_PAIR = "REFLECTION_BANK_PAIR"

# A paired artifact written within this many seconds counts as FRESH (both-fresh →
# silent). Default 900s (15 min) — a typical banking-staleness window.
_ENV_BANK_FRESH_S = "REFLECTION_BANK_FRESH_S"
_DEFAULT_FRESH_S = 900

# The tool names this facet reacts to (the settings.json matcher is "Write|Edit";
# this in-hook echo guards a settings drift that widens the matcher).
_BANK_TOOLS: frozenset[str] = frozenset({"Write", "Edit"})

# Per-facet kill switch (an env var → "1" suppresses just this facet).
ENV_NUDGE_OFF = "REFLECTION_BANK_CONSISTENCY_OFF"


def _bank_consistency_key() -> FacetKey | None:
    """Resolve the facet's ``FacetKey`` — ``BANK_CONSISTENCY`` once the adopter adds it.

    Returns the member if it exists, else ``None``. This module imports BEFORE the
    one-line enum edit lands; a ``None`` here means "not yet wired" — the facet stays
    UNREGISTERED (see the bottom of the file) rather than colliding on an existing key.
    Add ``BANK_CONSISTENCY = "bank_consistency"`` to the ``FacetKey`` enum in
    reflection_facet.py, then this resolves and the facet self-registers.
    """
    return getattr(FacetKey, "BANK_CONSISTENCY", None)


def _bank_pair() -> tuple[str, ...]:
    """The configured artifact-pair paths (from ``REFLECTION_BANK_PAIR``), read at call time."""
    raw = os.environ.get(_ENV_BANK_PAIR, "").strip()
    if not raw:
        return ()
    return tuple(p for p in raw.split(os.pathsep) if p)


def _fresh_window_s() -> int:
    """The freshness window in seconds (from ``REFLECTION_BANK_FRESH_S``), read at call time."""
    raw = os.environ.get(_ENV_BANK_FRESH_S, "").strip()
    if not raw:
        return _DEFAULT_FRESH_S
    try:
        return int(raw)
    except ValueError:
        return _DEFAULT_FRESH_S  # a malformed value falls back to the default (fail-open).


# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------


class BankFreshness(str, Enum):
    """The branch selector — drives FINISH-THE-BANK vs a silent PROCEED.

    ``OTHER_STALE`` — the paired artifact is stale (or its mtime is unreadable, treated
    conservatively as stale) → nudge to finish the pair.
    ``BOTH_FRESH`` — the paired artifact was written within the window → silent.
    """

    OTHER_STALE = "other_stale"
    BOTH_FRESH = "both_fresh"


@dataclass(frozen=True)
class BankConsistencySnapshot:
    """The I/O-free snapshot the facet's ``snapshot`` step returns.

    ``freshness is None`` ⇒ the write was not to a paired artifact (→ PROCEED). Pure —
    the mtime reads happened in ``snapshot``, so ``check_policy_material`` /
    ``build_payload`` are pure functions of this record.
    """

    freshness: BankFreshness | None
    written_name: str | None  # basename of the artifact just written.
    other_name: str | None    # basename of the OTHER (paired) artifact.
    other_age_s: float | None  # seconds since the other was modified, or None (unreadable).


def classify_bank_write(file_path: str) -> BankConsistencySnapshot:
    """Classify a written ``file_path`` against the configured pair → a snapshot.

    Returns a snapshot with ``freshness=None`` (→ PROCEED) when the write is not to a
    paired artifact — the cheap early-return that fires on every unrelated Write/Edit.
    When the write IS a paired artifact, reads the OTHER member's mtime and picks the
    branch: within the freshness window ⇒ ``BOTH_FRESH``; stale or unreadable ⇒
    ``OTHER_STALE`` (conservative — better to over-ask than silently skip).
    """
    empty = BankConsistencySnapshot(
        freshness=None, written_name=None, other_name=None, other_age_s=None
    )
    if not file_path:
        return empty
    pair = _bank_pair()
    if len(pair) < 2:
        return empty  # not configured (or mis-configured) → safe no-op.
    try:
        resolved = os.path.realpath(file_path)
    except OSError:
        return empty
    written: str | None = None
    other: str | None = None
    for i, member in enumerate(pair[:2]):
        try:
            member_resolved = os.path.realpath(member)
        except OSError:
            continue
        if resolved == member_resolved:
            written = member
            other = pair[1] if i == 0 else pair[0]
            break
    if written is None or other is None:
        return empty  # the write was not to a paired member.

    now = time.time()
    try:
        other_age: float | None = now - os.path.getmtime(other)
    except OSError:
        other_age = None  # unreadable → treat as stale (conservative).

    if other_age is not None and other_age < _fresh_window_s():
        freshness = BankFreshness.BOTH_FRESH
    else:
        freshness = BankFreshness.OTHER_STALE
    return BankConsistencySnapshot(
        freshness=freshness,
        written_name=os.path.basename(written),
        other_name=os.path.basename(other),
        other_age_s=other_age,
    )


# ---------------------------------------------------------------------------
# The payload — the FINISH-THE-BANK nudge
# ---------------------------------------------------------------------------

# WORDING IS THE CORE DESIGN WORK. Disarm-open ("soft; usually a no-op — the atomic
# banker keeps both fresh"), concrete (name the stale member + its age), explicit-escape
# (re-word your own banker), anti-manufacture ("don't invent staleness"). Only the
# OTHER_STALE branch renders a payload; BOTH_FRESH stays silent (no text).


def _finish_the_bank_text(snapshot: BankConsistencySnapshot) -> str:
    """Render the FINISH-THE-BANK nudge for a just-written member, other stale."""
    other = snapshot.other_name or "the paired artifact"
    written = snapshot.written_name or "one status artifact"
    if snapshot.other_age_s is None:
        stale_clause = f"`{other}` has no readable bank timestamp (treat as stale)"
    else:
        stale_clause = f"`{other}` is ~{int(snapshot.other_age_s // 60)}m stale"
    return (
        "🔗 BANK-CONSISTENCY CHECK (soft; usually a no-op — proceed by default). "
        f"You just banked `{written}`, but its paired artifact is out of sync: "
        f"{stale_clause}. A resume that reads the PAIR would get a torn picture — "
        "fresh state on one side, stale on the other. Before you move on, finish the "
        "pair: re-bank the OTHER now so the set is consistent (ideally via your atomic "
        "dual-write banker, which writes both together so this can't happen), then keep "
        "going. If the paired artifact is genuinely current and the staleness is only a "
        "clock artifact, proceed — do NOT invent an inconsistency to justify a rewrite."
    )


class BankConsistencyFacet(ReflectionFacet):
    """The ``bank_consistency`` facet — reflect on whether a paired status set is torn."""

    @property
    def key(self) -> FacetKey:
        resolved = _bank_consistency_key()
        if resolved is None:
            # Not-yet-wired: the enum member is missing. Registration is skipped below,
            # so this branch is only reached if a caller drives an unregistered facet
            # directly. Fail-loud rather than borrow another facet's identity key.
            raise RuntimeError(
                "FacetKey.BANK_CONSISTENCY is not defined — add it to the FacetKey enum "
                "in reflection_facet.py before using the bank-consistency facet "
                "(see this module's ADOPTER NOTE)."
            )
        return resolved

    @property
    def tempo(self) -> ReflectionTempo:
        return ReflectionTempo.ON_MEMORY_WRITE

    @property
    def policy_material(self) -> tuple[MaterialPointer, ...]:
        # Point at YOUR banking discipline + the atomic banker. These illustrative refs
        # resolve inside this catalogue; swap for yours.
        return (
            MaterialPointer(
                path="plugin/agent-governance/skills/self-operations/examples/lifecycle-L2-manage-context.md"
            ),
            MaterialPointer(
                path="plugin/agent-governance/skills/self-operations/hooks/bank_status.py"
            ),
        )

    @property
    def followup_vocabulary(self) -> frozenset[RoutedFollowup]:
        # A finish-the-bank self-check — no user-surface / backlog hand-off.
        return frozenset({RoutedFollowup.NUDGE})

    # ---- The four virtual Algorithm hooks ----

    def classify(self, hook_input: object) -> object | None:
        """Eligible iff the written path is one member of the configured pair.

        Returns a sentinel when the write is a paired-artifact write, or ``None`` when
        it is not (a non-paired path, or an unconfigured pair) → the cheap early-return.
        The freshness read happens in ``snapshot``, not here, so ``classify`` stays a
        cheap eligibility gate.
        """
        tool_name = getattr(hook_input, "tool_name", "")
        file_path = getattr(hook_input, "file_path", "")
        if tool_name and tool_name not in _BANK_TOOLS:
            return None
        snap = classify_bank_write(file_path)
        return snap if snap.freshness is not None else None

    def snapshot(self, hook_input: object, classification: object) -> object:
        """Reuse the classification snapshot (the I/O already happened in ``classify``).

        ``classify`` did the path + mtime reads to decide eligibility, so it hands the
        frozen ``BankConsistencySnapshot`` straight through — no second read.
        """
        _ = hook_input
        if isinstance(classification, BankConsistencySnapshot):
            return classification
        return BankConsistencySnapshot(
            freshness=None, written_name=None, other_name=None, other_age_s=None
        )

    def check_policy_material(self, snapshot: object) -> RoutedFollowup:
        """NUDGE iff the paired artifact is stale; otherwise PROCEED (both fresh → silent).

        This is the policy branch: the ONE case that warrants a reflection is a torn
        pair (``OTHER_STALE``). A consistent pair (``BOTH_FRESH``) stays silent — the
        default. Biased hard toward PROCEED, as the base requires.
        """
        if not isinstance(snapshot, BankConsistencySnapshot):
            return RoutedFollowup.PROCEED  # defensive: mis-shaped snapshot → silent.
        if snapshot.freshness is BankFreshness.OTHER_STALE:
            return RoutedFollowup.NUDGE
        return RoutedFollowup.PROCEED

    def build_payload(self, snapshot: object, followup: RoutedFollowup) -> str | None:
        """Render the FINISH-THE-BANK text (only reached on the OTHER_STALE branch)."""
        _ = followup
        if not isinstance(snapshot, BankConsistencySnapshot):
            return None
        return _finish_the_bank_text(snapshot)


# Self-register at import — but ONLY once the FacetKey member exists (the ADOPTER NOTE
# one-liner). Until then the facet is constructed-but-unregistered, so this module
# imports cleanly without colliding on another facet's key. Add BANK_CONSISTENCY to the
# FacetKey enum and this registers on next import.
BANK_CONSISTENCY_FACET: ReflectionFacet | None = None
if _bank_consistency_key() is not None:
    BANK_CONSISTENCY_FACET = REFLECTION_FACETS.register(BankConsistencyFacet())


__all__ = [
    "BANK_CONSISTENCY_FACET",
    "ENV_NUDGE_OFF",
    "BankConsistencyFacet",
    "BankConsistencySnapshot",
    "BankFreshness",
    "classify_bank_write",
]
