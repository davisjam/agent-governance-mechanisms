"""State-machine model starter — the PROCESS view of the 4+1 model (adopt & adapt).

This is the highest-leverage MBSE view: it realizes the *process view* — the concurrent runtime — as
one typed, queryable surface. Author it ONLY where a real concurrency failure lives (a data race, a
torn multi-step mutation, a stale-state read). Do NOT model stateless request/response parts: they
have no interleaving to catch, and a view with no failure to justify it is pure carrying cost.

The model composes, per subsystem under contention:
  - one `StateMachineSpec` per concurrent actor/lifecycle (its states + transitions);
  - one `SeamConnector` per inter-actor handoff (the edges where interleavings happen);
  - one `ConstraintBlock` per cross-actor invariant (a predicate that must hold across the race);
  - `VerifyRef` pointers to WHERE each invariant is proven.

SysML vocabulary (for legibility to an MBSE reader):
  - `ConstraintBlock`  ≈  «constraint»  — a named predicate the composition must satisfy.
  - `VerifyRef`        ≈  «verify»       — a traceability link from a constraint to its proof.
  - `SatisfyRef`       ≈  «satisfy»      — a traceability link from a constraint to the code that upholds it.

TWO load-bearing disciplines this file demonstrates:
  (a) LOOK UP, DON'T COPY — `_load_transitions_from_code()` reads the authoritative state table from
      the code at import time; the model never re-types state names. See the stub below.
  (b) DERIVE, DON'T HAND-TYPE — `derive_verification_tier()` computes each invariant's checker from
      its own shape; no per-invariant tier is authored by hand. See the stub below.

Pairs with the *formal-invariant-verification* mechanism: an invariant's temporal shape (`[]P` safety
vs. `P ~> Q` liveness) derives which EXHAUSTIVE checker proves it — a state-space model-check, not a
sampled test. The `__main__` at the bottom sketches the drift-lint that keeps the model equal to the
code; wire it into your build.

Stdlib-only. Fill every `# TODO:` with your project's own instances.
"""
from __future__ import annotations

import importlib.util
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from types import ModuleType

# ---------------------------------------------------------------------------
# Discipline (a): LOOK UP, DON'T COPY.
# The authoritative state/transition tables live in the *code*, not here. Read
# them at import time so the model is always a projection of the code — never a
# hand-copied snapshot that silently desyncs the first time someone edits one
# and not the other.
# ---------------------------------------------------------------------------

# TODO: point this at the code module that OWNS your state machines' transition
# tables (the module whose enums + `*_TRANSITIONS` dicts are the source of truth).
_AUTHORITATIVE_SM_SOURCE = Path(__file__).resolve().parent / "TODO_state_source.py"


def _load_authoritative_module() -> ModuleType:
    """Import the code module that owns the transition tables, by file path.

    Loaded by path (not a package import) so this model file has no package-import
    dependency on the subsystem it models — keep the authoritative source a
    side-effect-free, low-I/O module so importing it in isolation is safe.
    """
    if not _AUTHORITATIVE_SM_SOURCE.exists():
        raise ImportError(f"authoritative SM source absent: {_AUTHORITATIVE_SM_SOURCE}")
    spec = importlib.util.spec_from_file_location("_sm_source", _AUTHORITATIVE_SM_SOURCE)
    if spec is None or spec.loader is None:
        raise ImportError(f"could not build import spec for {_AUTHORITATIVE_SM_SOURCE}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["_sm_source"] = module  # private name; never shadow a real package
    spec.loader.exec_module(module)
    return module


def _load_transitions_from_code(table_symbol: str) -> dict[str, frozenset[str]]:
    """Read a `*_TRANSITIONS` table from the code, projected to `.value` strings.

    Discipline (a) in one function: the model NEVER re-types the states. It reads
    the live `dict[EnumState, set[EnumState]]` table and projects it to a
    JSON-friendly `dict[str, frozenset[str]]` so both the model surface and the
    drift-lint can set-diff against the SAME source.
    """
    module = _load_authoritative_module()
    raw = getattr(module, table_symbol)  # dict[Enum, set[Enum]] in the code
    out: dict[str, frozenset[str]] = {}
    for from_state, targets in raw.items():
        out[from_state.value] = frozenset(t.value for t in targets)
    return out


def _load_states_from_code(enum_symbol: str) -> tuple[str, ...]:
    """Read every state `.value` for an actor's state enum from the code (discipline a)."""
    module = _load_authoritative_module()
    enum_cls = getattr(module, enum_symbol)
    return tuple(member.value for member in enum_cls)


# ---------------------------------------------------------------------------
# Typed vocabulary — closed enums, not free-form strings.
# TODO: replace these members with your project's own kinds. Keep them CLOSED
# (an enum) so a typo can't silently invent a new seam-kind or primitive.
# ---------------------------------------------------------------------------


class SeamKind(Enum):
    """The inter-actor handoff channels — the edges where interleavings happen."""
    # TODO: e.g. QUEUE = "QUEUE"  (a shared queue between producer and consumer)
    # TODO: e.g. RPC   = "RPC"    (a synchronous cross-service call)
    TODO_SEAM = "TODO_SEAM"


class CoordPrimitive(Enum):
    """Coordination primitives whose FAILURE MODE is a race (the (H2) hairiness test).

    An invariant is "hairy" (⇒ exhaustive model-check MANDATORY) only if it references a race-shaped
    primitive here — everything but `NONE`. `NONE` marks a LINEAR invariant (one ordered sequence, no
    interleaving) that a property test suffices for.
    """
    # TODO: e.g. COMPARE_AND_SWAP = "COMPARE_AND_SWAP"   (a claim/lease CAS)
    # TODO: e.g. POP_THEN_MOVE    = "POP_THEN_MOVE"      (a non-atomic pop-then-enqueue gap)
    # TODO: e.g. STALE_HEARTBEAT  = "STALE_HEARTBEAT"    (a sweep reading stale liveness then acting)
    NONE = "NONE"  # LINEAR — no race primitive


class TemporalOperator(Enum):
    """The closed set of temporal SHAPES an invariant may carry.

    Adopts TLA+ operator syntax (a genre-check win: a real temporal-logic notation, not a bespoke
    DSL). The shape is the sole ROUTING KEY — `derive_verification_tier` reads THIS enum, never the
    prose description. `[]` is safety (holds in every reachable state); `[]<>` and `~>` are liveness
    (progress obligations).
    """
    ALWAYS            = "[]P"     # safety   — P holds in every reachable state
    EVENTUALLY_ALWAYS = "[]<>P"   # liveness — P holds infinitely often (progress)
    LEADS_TO          = "P~>Q"    # liveness — every P is eventually followed by Q


class VerificationTier(Enum):
    """The DERIVED routing key — which exhaustive checker proves an invariant.

    Never hand-typed per invariant; computed by `derive_verification_tier`.
    """
    SAFETY_BFS      = "SAFETY_BFS"       # hairy safety   ⇒ exhaustive state-space BFS ("simworld")
    LIVENESS_TLC    = "LIVENESS_TLC"     # hairy liveness ⇒ temporal model checker (e.g. TLC / a .tla spec)
    LINEAR_PROPERTY = "LINEAR_PROPERTY"  # linear         ⇒ a property test suffices


class VerifyKind(Enum):
    """The kind of checker a `VerifyRef` points at."""
    STATE_SPACE_BFS = "STATE_SPACE_BFS"
    TEMPORAL_MODEL  = "TEMPORAL_MODEL"
    PROPERTY_TEST   = "PROPERTY_TEST"


# ---------------------------------------------------------------------------
# Typed entities — frozen dataclasses (immutable, hashable model nodes).
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class VerifyRef:
    """«verify» — a drift-anchored pointer to WHERE an invariant is proven.

    The drift-lint resolves `path` (repo-relative) + `symbol`; a moved or deleted checker trips a
    finding. `symbol` may be empty for a file-level reference (e.g. a whole formal spec).
    """
    kind: VerifyKind
    path: str
    symbol: str = ""


@dataclass(frozen=True)
class SatisfyRef:
    """«satisfy» — a pointer to WHERE an invariant is upheld/watched in the running code."""
    path: str
    symbol: str = ""
    description: str = ""


@dataclass(frozen=True)
class TemporalForm:
    """The load-bearing temporal predicate of an invariant.

    `operator` is the ROUTING KEY — a plain enum lookup, NO string parsing on the routing path.
    `predicate` carries the human-readable TLA+ body (`P` / `P ~> Q`) and is NEVER read by the
    derivation — only `operator` routes. Required, non-defaulted: every invariant HAS a temporal
    shape, so there is no valid empty state (omitting it is a construction error).
    """
    operator: TemporalOperator
    predicate: str               # e.g. "NoLoss"  or  "DemandExceedsCapacity ~> CapacityMeetsDemand"


@dataclass(frozen=True)
class StateMachineSpec:
    """One concurrent actor/lifecycle. `states`/`transitions` are LOOKED UP (discipline a).

    Construct via `from_code(...)` so the states + transitions are read from the authoritative source
    rather than re-typed here.
    """
    name: str
    states: tuple[str, ...]
    transitions: dict[str, frozenset[str]]
    owning_participant: str      # the code site that registers/drives this SM
    enum_ref: str                # the state-enum symbol the drift-lint reconciles against
    code_ref: str                # the `*_TRANSITIONS` symbol the drift-lint reconciles against
    description: str = ""

    @classmethod
    def from_code(
        cls, *, name: str, owning_participant: str, enum_ref: str, code_ref: str,
        description: str = "",
    ) -> StateMachineSpec:
        """Build the spec by READING the code (discipline a) — not by re-typing states."""
        return cls(
            name=name,
            states=_load_states_from_code(enum_ref),
            transitions=_load_transitions_from_code(code_ref),
            owning_participant=owning_participant,
            enum_ref=enum_ref,
            code_ref=code_ref,
            description=description,
        )


@dataclass(frozen=True)
class SeamConnector:
    """One inter-actor edge — a handoff between two state machines (where races live)."""
    seam_kind: SeamKind
    carrier: str                 # the concrete channel (queue key / client / endpoint)
    from_participant: str
    to_participant: str
    message: str
    sync: bool                   # True for a blocking call; False for a queued/async handoff
    description: str = ""


@dataclass(frozen=True)
class ConstraintBlock:
    """«constraint» — one cross-actor invariant.

    `verification_tier` + `hairy` are DERIVED (discipline b) from `participant_lanes` and
    `coord_primitive` + the `temporal_form.operator` shape — NOT hand-typed. Store the derived value
    for queryability, but the derivation owns the truth (the drift-lint asserts they match).
    """
    inv_id: str
    description: str
    participant_lanes: tuple[str, ...]   # which SMs touch the same coordination point
    coord_primitive: CoordPrimitive
    temporal_form: TemporalForm          # REQUIRED — the sole liveness-routing input
    verification_tier: VerificationTier
    hairy: bool
    verify_refs: tuple[VerifyRef, ...] = ()
    satisfy_refs: tuple[SatisfyRef, ...] = ()

    @classmethod
    def build(
        cls, *, inv_id: str, description: str,
        participant_lanes: tuple[str, ...], coord_primitive: CoordPrimitive,
        temporal_form: TemporalForm,
        verify_refs: tuple[VerifyRef, ...] = (),
        satisfy_refs: tuple[SatisfyRef, ...] = (),
    ) -> ConstraintBlock:
        """Build an invariant, DERIVING its tier (discipline b) rather than accepting a hand-typed one."""
        tier, hairy = derive_verification_tier(
            participant_lanes=participant_lanes,
            coord_primitive=coord_primitive,
            temporal_operator=temporal_form.operator,
        )
        return cls(
            inv_id=inv_id, description=description,
            participant_lanes=participant_lanes, coord_primitive=coord_primitive,
            temporal_form=temporal_form, verification_tier=tier, hairy=hairy,
            verify_refs=verify_refs, satisfy_refs=satisfy_refs,
        )


@dataclass(frozen=True)
class ComposedStateMachineModel:
    """The whole process view — the actors + seams + invariants, composed."""
    state_machines: tuple[StateMachineSpec, ...]
    seams: tuple[SeamConnector, ...]
    invariants: tuple[ConstraintBlock, ...]

    def participant_lanes(self) -> frozenset[str]:
        return frozenset(sm.owning_participant for sm in self.state_machines)


# ---------------------------------------------------------------------------
# Discipline (b): DERIVE, DON'T HAND-TYPE.
# The verification tier is a FUNCTION of the invariant's own shape. A hand-typed
# tier goes stale the moment the inputs change; a derivation stays honest.
# ---------------------------------------------------------------------------


def _is_liveness_operator(op: TemporalOperator) -> bool:
    """`[]` is safety; `[]<>` and `~>` are liveness. Closed over the enum."""
    return op in (TemporalOperator.EVENTUALLY_ALWAYS, TemporalOperator.LEADS_TO)


def derive_verification_tier(
    *, participant_lanes: tuple[str, ...], coord_primitive: CoordPrimitive,
    temporal_operator: TemporalOperator,
) -> tuple[VerificationTier, bool]:
    """Derive `(verification_tier, hairy)` from the invariant's shape — the (H1)+(H2) test.

    HAIRY (⇒ an EXHAUSTIVE model-check is MANDATORY, not a sampled test) iff BOTH:
      - (H1) ≥2 participant lanes touch the same coordination point, AND
      - (H2) the invariant references a race-shaped `CoordPrimitive` (anything but `NONE`).

    Tier routing:
      - HAIRY safety   → SAFETY_BFS      (exhaustive state-space BFS proves it across every interleaving)
      - HAIRY liveness → LIVENESS_TLC    (a temporal model checker proves the progress obligation)
      - LINEAR         → LINEAR_PROPERTY (one ordered sequence — a property test suffices)

    Load-bearing move: the liveness-vs-safety decision reads ONLY the `temporal_operator` shape — the
    SAME `[]` / `~>` symbol a reader sees — so there is no separable boolean to leave stale.
    """
    h1 = len(participant_lanes) >= 2
    h2 = coord_primitive is not CoordPrimitive.NONE
    hairy = h1 and h2
    if not hairy:
        return VerificationTier.LINEAR_PROPERTY, False
    if _is_liveness_operator(temporal_operator):
        return VerificationTier.LIVENESS_TLC, True
    return VerificationTier.SAFETY_BFS, True


# ---------------------------------------------------------------------------
# THE MODEL — fill in your project's instances.
# ---------------------------------------------------------------------------

# TODO: build each SM by READING the code (discipline a). Example shape:
#   SM_WORKER = StateMachineSpec.from_code(
#       name="worker-job",
#       owning_participant="worker-loop",
#       enum_ref="JobState",             # the state enum symbol in your authoritative source
#       code_ref="JOB_TRANSITIONS",      # the transition-table symbol in your authoritative source
#       description="one job's lifecycle inside a single worker",
#   )

# TODO: declare the seams where interleavings happen. Example shape:
#   SEAM_DISPATCH = SeamConnector(
#       seam_kind=SeamKind.TODO_SEAM,
#       carrier="<queue key / client>",
#       from_participant="dispatcher", to_participant="worker-loop",
#       message="job-id handoff", sync=False,
#   )

# TODO: declare each cross-actor invariant with `.build(...)` so its tier DERIVES (discipline b).
#   Example shape:
#   INV_NO_DOUBLE_CLAIM = ConstraintBlock.build(
#       inv_id="INV-1",
#       description="a job is claimed by at most one worker",
#       participant_lanes=("worker-loop", "dispatcher"),
#       coord_primitive=CoordPrimitive.NONE,          # TODO: your race primitive
#       temporal_form=TemporalForm(TemporalOperator.ALWAYS, predicate="AtMostOneClaim"),
#       verify_refs=(VerifyRef(VerifyKind.STATE_SPACE_BFS, "TODO/path/to/checker.py", "test_no_double_claim"),),
#   )

MODEL = ComposedStateMachineModel(
    state_machines=(),   # TODO: (SM_WORKER, ...)
    seams=(),            # TODO: (SEAM_DISPATCH, ...)
    invariants=(),       # TODO: (INV_NO_DOUBLE_CLAIM, ...)
)


# ---------------------------------------------------------------------------
# THE DRIFT-LINT SKETCH — wire this into your build so the model CANNOT drift.
# Run on every build; exit non-zero on any divergence between model and code.
# ---------------------------------------------------------------------------


def _check_drift(model: ComposedStateMachineModel) -> list[str]:
    """Return a list of drift findings; empty list == model equals code.

    Two checks, one per discipline:
      (a) LOOK-UP drift — every SM's declared states/transitions still equal the code they were read
          from. (Re-reads via `from_code`'s path and set-diffs — a moved/renamed state trips it.)
      (b) DERIVE drift — every invariant's STORED `verification_tier`/`hairy` still equals what the
          derivation computes from its current inputs. A hand-edit that lies is caught here.
    """
    findings: list[str] = []

    # (a) LOOK-UP drift: re-read each SM from code and set-diff against the model.
    for sm in model.state_machines:
        try:
            code_states = set(_load_states_from_code(sm.enum_ref))
            code_trans = _load_transitions_from_code(sm.code_ref)
        except (ImportError, AttributeError) as exc:  # authoritative source moved/renamed
            findings.append(f"{sm.name}: cannot re-read authoritative source ({exc})")
            continue
        if set(sm.states) != code_states:
            findings.append(f"{sm.name}: states drifted from {sm.enum_ref}")
        if sm.transitions != code_trans:
            findings.append(f"{sm.name}: transitions drifted from {sm.code_ref}")

    # (b) DERIVE drift: re-derive each invariant's tier and compare to the stored value.
    for inv in model.invariants:
        tier, hairy = derive_verification_tier(
            participant_lanes=inv.participant_lanes,
            coord_primitive=inv.coord_primitive,
            temporal_operator=inv.temporal_form.operator,
        )
        if (tier, hairy) != (inv.verification_tier, inv.hairy):
            findings.append(
                f"{inv.inv_id}: stored tier {(inv.verification_tier, inv.hairy)} "
                f"!= derived {(tier, hairy)}"
            )

    return findings


if __name__ == "__main__":
    _findings = _check_drift(MODEL)
    for _f in _findings:
        print(f"DRIFT: {_f}")
    # Exit non-zero on any finding so the build blocks a divergent model.
    raise SystemExit(1 if _findings else 0)
