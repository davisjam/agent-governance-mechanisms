"""reflection_facet.py — the reflection-nudge substrate (Template-Method base).

PORTABLE. Stdlib-only. This is the CORE of the reflection-hook library — the
realization of the catalogue's ``reflection-facet-substrate`` mechanism
(agent/lifecycle-and-observability/reflection-facet-substrate.md). Copy this whole
``hooks/`` directory into your ``.claude/`` and adapt.

A conservative, tempo-gated, default-silent family of nudges. Each **facet**
reflects the operator's running context against ONE policy dimension it
*references* (never copies), at a tempo slow enough for repeated issues to become
visible, and the whole family emits **at most one reflection per window** — so
several soft reflections can't compound into the alarm fatigue that would kill
them all (the tower-of-governance guard applied to the substrate itself).

## The Template Method

A ``ReflectionFacet`` is an abstract base carrying the FIXED **Algorithm** — the
invariant reflect-nudge sequence — with **virtual methods** each concrete facet
specializes. The base fixes the sequence AND the *allowed surfaces* (the closed
set of virtual hooks a facet may implement), so:

  1. Uniformity holds by construction — a facet fills the sanctioned virtuals and
     touches nothing else; it cannot re-implement or bypass the shared tempo /
     anti-overwhelm / telemetry machinery.
  2. The abstract Algorithm names what a "reflection facet" IS; a new facet author
     fills in the blanks, not the control flow.

The FIXED Algorithm (``ReflectionFacet.reflect``), in order:

    classify → snapshot → check_policy_material → build_payload → route_followup

  - ``classify(hook_input)`` — is this facet ELIGIBLE on this event? A token when
    eligible, or ``None`` ⇒ not eligible → silent PROCEED (the cheap early-return).
  - ``snapshot(hook_input, classification)`` — read the substrate into a frozen,
    I/O-free payload so the later steps are pure/testable.
  - ``check_policy_material(snapshot)`` — the facet's policy branch: does the
    context CLEARLY warrant a reflection? Returns a ``RoutedFollowup`` (PROCEED ⇒
    stay silent). MUST err HARD toward PROCEED.
  - ``build_payload(snapshot, followup)`` — render the conservative payload text,
    or ``None`` (⇒ silent). Bias-away / default-silence wording is the core work.
  - ``route_followup(...)`` — package into a ``ReflectionResult``; a follow-up
    outside the facet's declared vocabulary fails loud.

The base's ``reflect()`` OWNS the sequence (Template Method); a facet overrides
only the virtual hooks. This module has NO Claude Code I/O of its own — the
emitter drives facets through the ``REFLECTION_FACETS`` registry.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


# ---------------------------------------------------------------------------
# Types (named before decomposition)
# ---------------------------------------------------------------------------


class FacetKey(str, Enum):
    """The closed set of reflection-facet identity keys (telemetry + registry key).

    A typed namespace: a typo in a facet key cannot silently create an unqueryable
    telemetry value or a duplicate registration. Grow it on measured need — the
    interface is the durable investment, the population is not. The two below are
    the shipped generic examples; add your own dimensions here.
    """

    FAILURE_CONTROL = "failure_control"      # recurrence-nudge (failure → control).
    KNOWLEDGE_ROUTING = "knowledge_routing"  # memory-vs-runbook routing.
    BANK_CONSISTENCY = "bank_consistency"    # paired-status-artifact freshness (bank the pair).
    # Add your own, e.g.:
    #   ARCHITECTURE = "architecture"        # DRY / structural drift.
    #   OPERATIONS = "operations"            # runbook / playbook gaps.


class ReflectionTempo(str, Enum):
    """When a facet is ELIGIBLE to reflect (its trigger genre).

    NOT a per-fire guarantee — the substrate's window-gate still caps to ≤1
    reflection per window across all facets of a tempo class.
    """

    ON_TURN_END = "on_turn_end"          # Stop (failure_control, etc.).
    ON_MEMORY_WRITE = "on_memory_write"  # PostToolUse Write|Edit into a knowledge store.


class RoutedFollowup(str, Enum):
    """What a facet MAY emit BESIDES a plain nudge (the hand-off seam).

    A facet's policy branch returns one of these; the facet's
    ``followup_vocabulary`` declares which subset it MAY emit. A facet returning a
    follow-up outside its declared vocabulary is a construction error (closed
    surface).
    """

    PROCEED = "proceed"              # the default — a silent no-op.
    NUDGE = "nudge"                  # inject the conservative reflection payload.
    USER_QUESTION = "user_question"  # surface to the user as a question.
    BACKLOG_ADD = "backlog_add"      # add to a standing backlog.


@dataclass(frozen=True)
class MaterialPointer:
    """A resolvable pointer into a canonical policy material (a ``path#anchor`` ref).

    ``path`` is repo-relative and MUST exist; ``anchor`` (optional) is a
    GitHub-style slug of a markdown heading. The facet REFERENCES the canonical
    material; it never duplicates it — a moved / renamed / deleted policy doc trips
    a resolve check rather than rotting silently inside a hook string. (Wire that
    check as a lint over your facet registry — see the README.)
    """

    path: str
    anchor: str | None = None

    def as_ref(self) -> str:
        """The ``path[#anchor]`` ref string."""
        return f"{self.path}#{self.anchor}" if self.anchor else self.path

    def resolves(self, repo_root: Path) -> bool:
        """True iff ``path`` exists under ``repo_root`` (the pointer-resolve check)."""
        return (repo_root / self.path).exists()


@dataclass(frozen=True)
class ReflectionResult:
    """The Template Method's output — a rendered reflection or a silent PROCEED.

    ``followup is PROCEED`` (or ``payload is None``) ⇒ the facet stays silent this
    fire (the common case). Otherwise ``payload`` is the conservative nudge text
    and ``followup`` is what the operator MAY do about it.
    """

    facet_key: FacetKey
    followup: RoutedFollowup
    payload: str | None

    @property
    def is_silent(self) -> bool:
        """True iff this fire produces no reflection (PROCEED or no payload)."""
        return self.followup is RoutedFollowup.PROCEED or self.payload is None


# ---------------------------------------------------------------------------
# The Template-Method base (the FIXED Algorithm + the virtual hooks)
# ---------------------------------------------------------------------------


class ReflectionFacet(ABC):
    """One policy dimension the substrate reflects against — a Template-Method base.

    A concrete facet subclasses this and implements EXACTLY the four abstract hooks
    (``classify`` / ``snapshot`` / ``check_policy_material`` / ``build_payload``)
    plus the four declaration properties (``key`` / ``tempo`` / ``policy_material``
    / ``followup_vocabulary``). It MUST NOT override ``reflect`` or
    ``route_followup`` — the control flow the base OWNS.

    A facet is a stateless policy DECLARATION (its snapshot carries the per-fire
    state); the tempo/window state lives in the emitter's flag file, not the facet.
    """

    # ---- Declaration surface (the four facet properties) ----

    @property
    @abstractmethod
    def key(self) -> FacetKey:
        """The facet's identity key (telemetry + registry key)."""

    @property
    @abstractmethod
    def tempo(self) -> ReflectionTempo:
        """When this facet is ELIGIBLE to reflect (its trigger genre)."""

    @property
    @abstractmethod
    def policy_material(self) -> tuple[MaterialPointer, ...]:
        """The canonical policy material(s) this facet reflects against — RESOLVABLE.

        Single-sourced: the facet REFERENCES the material; the payload MAY quote a
        line, but the source of truth is the pointer.
        """

    @property
    @abstractmethod
    def followup_vocabulary(self) -> frozenset[RoutedFollowup]:
        """The subset of ``RoutedFollowup`` this facet MAY emit (closed surface)."""

    # ---- The four virtual ALGORITHM hooks (facet-specialized) ----

    @abstractmethod
    def classify(self, hook_input: object) -> object | None:
        """Is this facet ELIGIBLE on this event? (Algorithm step 1).

        A facet-specific token when eligible, or ``None`` when the event is not
        this facet's moment (⇒ silent PROCEED). Pure of policy judgment.
        """

    @abstractmethod
    def snapshot(self, hook_input: object, classification: object) -> object:
        """Read the substrate into a frozen, I/O-free payload (Algorithm step 2).

        Do ALL the facet's I/O here so the later steps are pure functions of the
        snapshot (testable, no clock/fs dependency).
        """

    @abstractmethod
    def check_policy_material(self, snapshot: object) -> RoutedFollowup:
        """The facet's POLICY branch (Algorithm step 3) — bias HARD toward PROCEED.

        ``PROCEED`` (the common case — stay silent) or one of the facet's declared
        follow-ups. Default-silence discipline lives here.
        """

    @abstractmethod
    def build_payload(self, snapshot: object, followup: RoutedFollowup) -> str | None:
        """Render the conservative payload text (Algorithm step 4), or ``None``.

        Called ONLY for a non-PROCEED follow-up. Wording is the core design work —
        disarm-open, concrete-actionable, explicit-escape, anti-manufacture.
        """

    # ---- The FIXED Algorithm (Template Method — a facet MUST NOT override) ----

    def reflect(self, hook_input: object) -> ReflectionResult:
        """THE TEMPLATE METHOD — the fixed reflect-nudge Algorithm.

        classify → snapshot → check_policy_material → build_payload → route_followup.

        Returns a silent PROCEED or a rendered reflection. I/O-free w.r.t. Claude
        Code (no stdout / emit); the emitter turns a non-silent result into a hook
        decision.
        """
        classification = self.classify(hook_input)
        if classification is None:
            return self._proceed()  # not this facet's moment → silent.

        snap = self.snapshot(hook_input, classification)
        followup = self.check_policy_material(snap)
        if followup is RoutedFollowup.PROCEED:
            return self._proceed()  # policy branch says nothing clear → silent.

        payload = self.build_payload(snap, followup)
        return self.route_followup(followup, payload)

    def route_followup(
        self, followup: RoutedFollowup, payload: str | None
    ) -> ReflectionResult:
        """Package a (followup, payload) into a ``ReflectionResult`` (Algorithm step 5).

        Part of the fixed control flow (a facet MUST NOT override it). Fail-loud
        closed surface: a follow-up outside the facet's declared vocabulary raises;
        a ``None`` payload collapses to a silent PROCEED.
        """
        if payload is None:
            return self._proceed()
        if followup not in self.followup_vocabulary:
            raise ReflectionFacetError(
                f"facet {self.key!r} emitted follow-up {followup!r} not in its "
                f"declared vocabulary {sorted(f.value for f in self.followup_vocabulary)} "
                f"— the closed-surface discipline forbids an undeclared follow-up."
            )
        return ReflectionResult(facet_key=self.key, followup=followup, payload=payload)

    def _proceed(self) -> ReflectionResult:
        """The silent-PROCEED result (the common case)."""
        return ReflectionResult(
            facet_key=self.key, followup=RoutedFollowup.PROCEED, payload=None
        )


class ReflectionFacetError(RuntimeError):
    """Raised on a closed-surface violation (an undeclared follow-up / duplicate key).

    The fail-loud belt: a facet that violates the base's closed surface RAISES
    rather than silently emitting an off-contract reflection.
    """


# ---------------------------------------------------------------------------
# The facet registry (state-bearing → a class)
# ---------------------------------------------------------------------------


class ReflectionFacetRegistry:
    """The typed registry — the single place "what reflection facets exist" lives.

    Facets self-register at import. The emitter reads the registry to enumerate the
    facets of a tempo class + round-robin among them; a pointer-resolve lint reads
    it to verify every facet's ``policy_material`` resolves.
    """

    def __init__(self) -> None:
        self._facets: dict[FacetKey, ReflectionFacet] = {}

    def register(self, facet: ReflectionFacet) -> ReflectionFacet:
        """Register ``facet`` under its ``key``. A duplicate key is fail-loud."""
        if facet.key in self._facets:
            raise ReflectionFacetError(
                f"duplicate reflection-facet registration for key {facet.key!r} — "
                f"each facet key is registered exactly once (the registry is the SSOT)."
            )
        self._facets[facet.key] = facet
        return facet

    def get(self, key: FacetKey) -> ReflectionFacet | None:
        """Return the facet registered under ``key``, or None."""
        return self._facets.get(key)

    def all_facets(self) -> list[ReflectionFacet]:
        """Every registered facet, registration-order stable."""
        return list(self._facets.values())

    def facets_for_tempo(self, tempo: ReflectionTempo) -> list[ReflectionFacet]:
        """Every registered facet whose ``tempo`` matches, registration-order stable.

        The emitter uses this to enumerate the facets competing for one tempo
        window's single reflection budget (round-robin, ≤1 reflection/window).
        """
        return [f for f in self._facets.values() if f.tempo is tempo]

    def __len__(self) -> int:
        return len(self._facets)


# The module-level registry — the substrate's consumption seam. Facets self-register
# at import (see reflection_facet_recurrence.py / reflection_facet_memory_routing.py).
REFLECTION_FACETS: ReflectionFacetRegistry = ReflectionFacetRegistry()


__all__ = [
    "REFLECTION_FACETS",
    "FacetKey",
    "MaterialPointer",
    "ReflectionFacet",
    "ReflectionFacetError",
    "ReflectionFacetRegistry",
    "ReflectionResult",
    "ReflectionTempo",
    "RoutedFollowup",
]
