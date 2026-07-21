"""reflection_facet_memory_routing.py — the ``knowledge_routing`` reflection facet.

PORTABLE example facet. Reflection dimension: *knowledge-routing (memory vs runbook)*.

When the operator banks a private-memory topic file, this facet reflects: is this a
true contextual one-off, or is it durable, generalizable know-how that belongs in a
SHARED, committed, discoverable home (a runbook, a design doc, a house-rules rule)?
And — the no-home clause — if NO existing shared home fits, the *absence* of a home
may itself be a structural-gap signal (→ surface to the user / add to a backlog),
not automatically a one-off.

Fires on the ON_MEMORY_WRITE tempo (a PostToolUse ``Write|Edit`` into a memory
dir), a DISTINCT window from the ON_TURN_END facets — a memory write is a discrete,
operator-initiated bank moment, not a recurring tick.

**Classification:** the written path resolves against the configured memory dir(s):

  - a ``Write`` to a topic path  → NEW_TOPIC_FILE   → NUDGE (route-check).
  - an ``Edit`` to a topic path  → EDIT_TOPIC_FILE  → NUDGE (a rewrite can be a new
    learning).
  - a write to the index file    → MEMORY_INDEX_EDIT → PROCEED (bookkeeping, not a
    learning; nudging it is noise).
  - not under a memory dir       → PROCEED (the cheap early-return).

To adapt: set ``REFLECTION_MEMORY_DIRS`` (os.pathsep-joined absolute dirs) to YOUR
private-memory store(s), and re-word ``ROUTE_CHECK_TEXT`` for your shared homes.
"""

from __future__ import annotations

import os
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
# Config — the memory dir(s) this facet covers (portable: set via env var)
# ---------------------------------------------------------------------------

# The private-memory store roots. Facts banked here are per-user / un-committed /
# un-indexed, so they are invisible to every shared-doc read — that invisibility is
# exactly what makes the route-check worth a nudge. Set REFLECTION_MEMORY_DIRS to
# your absolute memory dir(s), os.pathsep-joined. Default: none (the facet is a
# no-op until you point it at your store — a safe zero-config default).
_ENV_MEMORY_DIRS = "REFLECTION_MEMORY_DIRS"

# The index-file basename — a write to it is a pointer/bookkeeping edit, not a
# learning. Set REFLECTION_MEMORY_INDEX to change it.
_MEMORY_INDEX_BASENAME = os.environ.get("REFLECTION_MEMORY_INDEX", "MEMORY.md")

# The tool names this facet reacts to (the settings.json matcher is "Write|Edit";
# this in-hook echo guards a settings drift that widens the matcher).
_MEMORY_TOOLS: frozenset[str] = frozenset({"Write", "Edit"})

# Per-facet kill switch.
ENV_NUDGE_OFF = "REFLECTION_KNOWLEDGE_ROUTING_OFF"


def _memory_dir_roots() -> tuple[str, ...]:
    """The configured memory-dir roots (from ``REFLECTION_MEMORY_DIRS``), read at call time."""
    raw = os.environ.get(_ENV_MEMORY_DIRS, "").strip()
    if not raw:
        return ()
    return tuple(p for p in raw.split(os.pathsep) if p)


# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------


class MemoryWriteKind(str, Enum):
    """The closed classification of a written ``file_path`` against the memory dir(s)."""

    NEW_TOPIC_FILE = "new_topic_file"        # a Write to a topic path (fresh bank) → nudge.
    EDIT_TOPIC_FILE = "edit_topic_file"      # an Edit to a topic path (refine) → nudge.
    MEMORY_INDEX_EDIT = "memory_index_edit"  # a write to the index → no-op (bookkeeping).

    @property
    def nudges(self) -> bool:
        """True iff this kind warrants the route-check nudge (both topic-file kinds)."""
        return self in (MemoryWriteKind.NEW_TOPIC_FILE, MemoryWriteKind.EDIT_TOPIC_FILE)


@dataclass(frozen=True)
class MemoryRoutingSnapshot:
    """The opaque, I/O-free snapshot the facet's ``snapshot`` step returns.

    ``kind is None`` ⇒ not a memory topic-file write (→ PROCEED). Pure — no I/O of
    its own, so ``check_policy_material`` / ``build_payload`` are pure functions.
    """

    kind: MemoryWriteKind | None
    memory_basename: str | None


def classify_memory_write(tool_name: str, file_path: str) -> MemoryWriteKind | None:
    """Classify a written ``file_path`` (+ the tool that wrote it) as a ``MemoryWriteKind``.

    Returns ``None`` if the path is not under any configured memory dir (the cheap
    early-return that fires on every unrelated Write/Edit). A path that cannot be
    resolved is treated as "not a memory write" (fail-open no-op).

    NEW vs EDIT heuristic: under PostToolUse the file already exists on disk, so the
    signal is the TOOL. A ``Write`` is create-or-overwrite (≈ fresh bank → NEW); an
    ``Edit`` is modify-existing (≈ refine → EDIT). A soft nudge does not need
    perfect precision, and the per-path dedupe (in the hook) absorbs an over-fire.
    """
    if not file_path:
        return None
    try:
        resolved = os.path.realpath(file_path)
    except OSError:
        return None
    under_memory = False
    for root in _memory_dir_roots():
        try:
            root_resolved = os.path.realpath(root)
        except OSError:
            continue
        if resolved == root_resolved or resolved.startswith(root_resolved + os.sep):
            under_memory = True
            break
    if not under_memory:
        return None
    if os.path.basename(resolved) == _MEMORY_INDEX_BASENAME:
        return MemoryWriteKind.MEMORY_INDEX_EDIT
    return (
        MemoryWriteKind.NEW_TOPIC_FILE
        if tool_name == "Write"
        else MemoryWriteKind.EDIT_TOPIC_FILE
    )


# ---------------------------------------------------------------------------
# The payload — the route-check with the no-existing-home clause
# ---------------------------------------------------------------------------

# WORDING IS THE CORE DESIGN WORK. Every clause biases toward the memory being a
# legitimate one-off + the operator proceeding; the re-home is an INVITATION to
# reconsider, never a demand. The no-home clause (2nd para) is the hand-off seam:
# absence of a home may be a structural gap (→ user-question / backlog-add), but
# STILL "usually proceed".
ROUTE_CHECK_TEXT = (
    "🧭 MEMORY-VS-RUNBOOK ROUTING CHECK (soft; usually a no-op — proceed by default). "
    "You just banked a private-memory topic file. Private memory is per-user + "
    "un-committed + un-indexed, so a fact banked there is invisible to every other "
    "agent and every shared-doc read. BEFORE moving on, ask ONCE: is this a true "
    "contextual one-off (a session-specific observation, a transient state note, a "
    "personal-preference reminder) — or is it durable, generalizable know-how that "
    "belongs in a SHARED, committed, discoverable home instead (or in addition)? "
    "Concretely — a reusable how-to keyed by a symptom → a runbook or a pointer "
    "catalog; an architectural rule/invariant → a design doc or a house-rules rule; "
    "a recurring failure→control → your hardening discipline. If it is genuinely a "
    "one-off, proceed — this is usually the case, and re-homing a true one-off just "
    "clutters the shared docs. Only if you can NAME the shared doc it clearly "
    "belongs in, consider adding it there (the memory can stay as a pointer). Do "
    "NOT invent a runbook home to justify acting; a false re-route is worse than a "
    "missed one.\n\n"
    "If NO existing shared document fits, do NOT force one — but do NOT reflexively "
    "treat it as a one-off either. PONDER: maybe it genuinely IS a one-off "
    "(proceed), OR the absence of a home is itself the signal — an "
    "architectural/structural gap. In that case, consider surfacing it to the user "
    "as a question, OR adding it to a standing backlog for consideration. This is "
    "still \"usually proceed\" — reach for the user-question / backlog-add only when "
    "the learning clearly has durable value AND no home exists AND you judge the gap "
    "real."
)


class MemoryRoutingFacet(ReflectionFacet):
    """The ``knowledge_routing`` facet — reflect on whether a banked memory has a shared home."""

    @property
    def key(self) -> FacetKey:
        return FacetKey.KNOWLEDGE_ROUTING

    @property
    def tempo(self) -> ReflectionTempo:
        return ReflectionTempo.ON_MEMORY_WRITE

    @property
    def policy_material(self) -> tuple[MaterialPointer, ...]:
        # Point at YOUR memory-vs-runbook policy + the runbook home. These
        # illustrative refs resolve inside this catalogue; swap for yours.
        return (
            MaterialPointer(
                path="plugin/agent-governance/skills/self-operations/examples/lifecycle-L6-govern-your-own-loop.md"
            ),
            MaterialPointer(
                path="plugin/agent-governance/skills/self-operations/SKILL.md"
            ),
        )

    @property
    def followup_vocabulary(self) -> frozenset[RoutedFollowup]:
        # NUDGE (the route-check) + the no-home hand-off seam: the payload PONDERS
        # user-question / backlog-add, so those follow-ups are in the vocabulary.
        return frozenset(
            {
                RoutedFollowup.NUDGE,
                RoutedFollowup.USER_QUESTION,
                RoutedFollowup.BACKLOG_ADD,
            }
        )

    # ---- The four virtual Algorithm hooks ----

    def classify(self, hook_input: object) -> object | None:
        """Eligible iff the written path is a memory TOPIC-file write (NEW or EDIT).

        Returns the ``MemoryWriteKind`` when eligible, or ``None`` when the write is
        not nudge-worthy (an index edit, or a non-memory path) → the cheap
        early-return. Reads ``tool_name`` / ``file_path`` off the hook input.
        """
        tool_name = getattr(hook_input, "tool_name", "")
        file_path = getattr(hook_input, "file_path", "")
        if tool_name and tool_name not in _MEMORY_TOOLS:
            return None
        kind = classify_memory_write(tool_name, file_path)
        if kind is None or not kind.nudges:
            return None  # non-memory write OR an index edit → silent.
        return kind

    def snapshot(self, hook_input: object, classification: object) -> object:
        """Freeze the classification + basename into an I/O-free snapshot."""
        kind = classification if isinstance(classification, MemoryWriteKind) else None
        file_path = getattr(hook_input, "file_path", "")
        basename = os.path.basename(file_path) if file_path else None
        return MemoryRoutingSnapshot(kind=kind, memory_basename=basename)

    def check_policy_material(self, snapshot: object) -> RoutedFollowup:
        """A nudge-worthy topic-file write always warrants the route-check NUDGE.

        ``classify`` already filtered to the nudge-worthy kinds. The payload carries
        the "usually a one-off, proceed" bias + the no-home ponder — so the actual
        routing decision is the operator's, delegated via the wording.
        """
        if not isinstance(snapshot, MemoryRoutingSnapshot) or snapshot.kind is None:
            return RoutedFollowup.PROCEED  # defensive: mis-shaped snapshot → silent.
        return RoutedFollowup.NUDGE

    def build_payload(self, snapshot: object, followup: RoutedFollowup) -> str | None:
        """Return the ``ROUTE_CHECK_TEXT`` (with the no-home clause)."""
        _ = (snapshot, followup)
        return ROUTE_CHECK_TEXT


# Self-register at import.
MEMORY_ROUTING_FACET: ReflectionFacet = REFLECTION_FACETS.register(MemoryRoutingFacet())


__all__ = [
    "ENV_NUDGE_OFF",
    "MEMORY_ROUTING_FACET",
    "ROUTE_CHECK_TEXT",
    "MemoryRoutingFacet",
    "MemoryRoutingSnapshot",
    "MemoryWriteKind",
    "classify_memory_write",
]
