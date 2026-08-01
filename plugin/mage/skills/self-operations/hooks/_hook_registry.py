"""_hook_registry.py — the typed orchestrator-hook registry.

PORTABLE. Stdlib-only. The ONE way to declare a Claude Code hook, so that "what hooks
exist + what each is ALLOWED to output" lives in a single typed place. Copy this whole
``hooks/`` directory into your ``.claude/`` and adapt.

────────────────────────────────────────────────────────────────────────────────
SCHEMA DEPENDENCY (read this before running)

This module imports a sibling ``_claude_hook_output_schema`` for the event-capability
facts. It is authored separately and MAY NOT be on disk yet in a partial checkout —
that is expected; do not run this file to test the import until the schema module
lands. The interface this module codes against (the whole contract it needs):

  - ``KNOWN_EVENTS``: a set/collection of the known Claude Code event names
    (e.g. ``"Stop"``, ``"PostToolUse"``, ``"SubagentStop"``, ``"PreCompact"``, …).
  - ``hook_specific_output_allowed(event: str) -> bool``: True iff ``event`` supports a
    ``hookSpecificOutput`` block (an INJECT-capable event); False for the top-level-only
    events that can ONLY veto (BLOCK).

That single lookup is the source of truth for the INJECT-vs-BLOCK derivation below.

────────────────────────────────────────────────────────────────────────────────
THE DRIFT HAZARD IT KILLS

Without a registry, each hook independently decides inject-vs-block, and a hook can
claim it will INJECT context on an event that is block-only (the "SubagentStop can
inject" bug class — a top-level-only event silently ignores an inject in production).
Here that distinction is **structural, not prose**: ``HookOutputKind`` is DERIVED from
the schema, and an ``OrchestratorHook`` that declares ``INJECT`` on a block-only event
RAISES a ``HookCapabilityError`` at CONSTRUCTION — a bug caught when you wire the hook,
not when it silently no-ops in production.

The ``HookRegistry.run`` driver owns the cross-cutting concerns in ONE place —
kill-switch honoring, the fail-open belt, telemetry tagging — so each hook's read→nudge
pair is not re-hand-wired per script.
"""

from __future__ import annotations

import os
import sys
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

# _claude_hook_output_schema + _hook_harness are sibling modules. Insert this dir on
# sys.path so the bare imports resolve when a hook script is exec'd directly by the
# Claude Code harness (no hooks/ dir on sys.path by default) — same bootstrap the other
# hook modules use.
_HOOKS_DIR = str(Path(__file__).resolve().parent)
if _HOOKS_DIR not in sys.path:
    sys.path.insert(0, _HOOKS_DIR)

from _claude_hook_output_schema import (  # noqa: E402 — sibling module after sys.path insert
    KNOWN_EVENTS,
    hook_specific_output_allowed,
)
from _hook_harness import (  # noqa: E402 — sibling module after sys.path insert
    HookDecision,
    HookInput,
)


class HookOutputKind(str, Enum):
    """The closed capability set for a hook's output — DERIVED, never hand-typed.

    ``INJECT`` — the hook can add context (a ``hookSpecificOutput`` block): the
    inject-capable events.
    ``BLOCK`` — the hook can ONLY veto (top-level ``decision:"block"`` + ``reason``):
    the top-level-only events (Stop / SubagentStop / PreCompact / Notification).

    A caller NEVER picks a member by hand for a given event — ``for_event`` reads the
    schema and decides.
    """

    INJECT = "inject"
    BLOCK = "block"

    @classmethod
    def for_event(cls, event: str) -> HookOutputKind:
        """DERIVE the output kind for a Claude Code event from the vendored schema.

        The single source of truth is ``_claude_hook_output_schema``:
        ``hook_specific_output_allowed(event)`` True ⇒ INJECT-capable; else BLOCK-only.
        An unknown event raises ``HookCapabilityError`` (fail-loud) — a typo must not
        silently pick a capability.
        """
        if event not in KNOWN_EVENTS:
            raise HookCapabilityError(
                f"unknown Claude Code event {event!r} "
                f"(known: {', '.join(sorted(KNOWN_EVENTS))})"
            )
        return cls.INJECT if hook_specific_output_allowed(event) else cls.BLOCK


class HookCapabilityError(RuntimeError):
    """Raised when an ``OrchestratorHook`` declares a capability its event forbids.

    The fail-loud construction belt: a hook that claims ``INJECT`` on a block-only
    event (the SubagentStop-inject bug class) RAISES at construction rather than
    emitting an inject that Claude Code silently ignores in production. Also raised on
    an unknown event and a duplicate registration.
    """


@dataclass(frozen=True)
class OrchestratorHook:
    """A typed declaration of one hook — its event, its DERIVED capability, its callables.

    The ``output_kind`` is validated against the vendored schema at construction
    (``__post_init__``): a mismatch is a ``HookCapabilityError``, so an
    inject-on-block-only-event is impossible to declare.

    - ``name`` — the telemetry / registry tag (a stable id for this hook).
    - ``event`` — the Claude Code event ("PostToolUse" | "Stop" | "SubagentStop" | …).
    - ``output_kind`` — INJECT | BLOCK, DERIVED via ``HookOutputKind.for_event`` (prefer
      ``build`` so it is derived, not hand-picked).
    - ``read_substrate`` — the "read" step: ``HookInput -> snapshot`` (opaque payload).
    - ``build_nudge`` — the "nudge" step: ``snapshot -> HookDecision``.
    - ``kill_switch_env`` — the env var (``"1"`` ⇒ disabled) that turns this hook off.
    """

    name: str
    event: str
    output_kind: HookOutputKind
    read_substrate: Callable[[HookInput], object]
    build_nudge: Callable[[object], HookDecision]
    kill_switch_env: str

    def __post_init__(self) -> None:
        expected = HookOutputKind.for_event(self.event)
        if self.output_kind != expected:
            raise HookCapabilityError(
                f"hook {self.name!r} declares output_kind={self.output_kind.value} for "
                f"event {self.event!r}, but the vendored schema DERIVES "
                f"{expected.value} for that event. "
                + (
                    f"{self.event} supports a hookSpecificOutput block (INJECT-capable)."
                    if expected is HookOutputKind.INJECT
                    else f"{self.event} is top-level-only — it can ONLY veto (BLOCK), "
                    "never inject. This is the SubagentStop-inject bug class the "
                    "framework structurally prevents."
                )
            )

    @classmethod
    def build(
        cls,
        *,
        name: str,
        event: str,
        read_substrate: Callable[[HookInput], object],
        build_nudge: Callable[[object], HookDecision],
        kill_switch_env: str,
    ) -> OrchestratorHook:
        """Construct a hook with its ``output_kind`` DERIVED from ``event`` (the ergonomic path).

        Callers never hand-pick the capability; ``build`` looks it up from the vendored
        schema, so the only way to get a wrong capability is to pass a wrong ``event``
        (still fail-loud via ``HookOutputKind.for_event``).
        """
        return cls(
            name=name,
            event=event,
            output_kind=HookOutputKind.for_event(event),
            read_substrate=read_substrate,
            build_nudge=build_nudge,
            kill_switch_env=kill_switch_env,
        )


class HookRegistry:
    """The typed registry — the single place "what hooks exist" lives.

    State-bearing (a mutable name→hook map) → a class. Hooks register here; a
    conformance check can read the registry to verify every wired hook is declared.
    The ``run`` driver owns kill-switch honoring + the fail-open belt in ONE place.
    """

    def __init__(self) -> None:
        self._hooks: dict[str, OrchestratorHook] = {}

    def register(self, hook: OrchestratorHook) -> OrchestratorHook:
        """Register ``hook`` under its ``name``. A duplicate name is fail-loud."""
        if hook.name in self._hooks:
            raise HookCapabilityError(
                f"duplicate hook registration for name {hook.name!r} — each hook name "
                f"is registered exactly once (the registry is the single source of truth)."
            )
        self._hooks[hook.name] = hook
        return hook

    def register_once(self, hook: OrchestratorHook) -> OrchestratorHook:
        """Register ``hook``, or return the EXISTING one already registered under its name.

        Reload-safe: a hook script loaded by path in multiple test files re-executes its
        module against the shared module-level registry singleton, so a bare ``register``
        would fail-loud on the second load. ``register_once`` treats a same-name
        re-registration as a no-op (returns the incumbent) — the correct semantics for a
        module reload (the hook's identity IS its name; re-executing its module does not
        create a second, different hook). It does NOT weaken the duplicate-guard for two
        GENUINELY DIFFERENT hooks claiming one name — that stays on the ``register`` path.
        """
        existing = self._hooks.get(hook.name)
        if existing is not None:
            return existing
        return self.register(hook)

    def get(self, name: str) -> OrchestratorHook | None:
        """Return the hook registered under ``name``, or None."""
        return self._hooks.get(name)

    def all_hooks(self) -> list[OrchestratorHook]:
        """Every registered hook, registration-order stable (dict insertion order)."""
        return list(self._hooks.values())

    def run(self, name: str, hook_input: HookInput) -> HookDecision:
        """Drive one registered hook end-to-end: look up ``name``, read→nudge, return the decision.

        The single caller of a hook's read/nudge pair — so the cross-cutting concerns
        live HERE, once, not re-hand-wired per hook:

          - **Unknown name** → fail-loud ``HookCapabilityError`` (a typo must not
            silently no-op — a construction-class error, not a per-request one).
          - **Kill switch** — if the hook's ``kill_switch_env`` is ``"1"``, return
            ``HookDecision.noop()`` (disabled).
          - **Fail-open** — ``read_substrate`` / ``build_nudge`` are wrapped so ANY
            unexpected error → ``HookDecision.noop()``. A driver that raised would turn a
            fail-loud tool call into a fail-quiet blocked one — the worst outcome for a
            hook firing on every interaction.

        The returned ``HookDecision`` carries the wire shape its ``build_nudge`` chose;
        the DERIVED ``output_kind`` on the looked-up hook is what a telemetry sink or a
        conformance check reads (this portable driver does not manufacture the inject
        wire form — the harness's ``HookDecision`` owns that).
        """
        key = str(name)
        hook = self.get(key)
        if hook is None:
            raise HookCapabilityError(
                f"no hook registered under name {key!r} — registered: "
                f"{sorted(self._hooks)}. A hook must register before it can run."
            )
        if os.environ.get(hook.kill_switch_env) == "1":
            return HookDecision.noop()  # killed → noop (no output).
        try:
            return hook.build_nudge(hook.read_substrate(hook_input))
        except Exception:  # noqa: BLE001 — FAIL-OPEN driver: read_substrate/build_nudge raising must NOT block a legitimate tool call. Any unexpected error → noop so the interaction proceeds with no nudge. This is the load-bearing safety property for the single read→nudge caller (a justified swallow, never a silent one — the intent is documented here).
            return HookDecision.noop()

    def __len__(self) -> int:
        return len(self._hooks)


# The module-level registry — the consumption seam a hook script registers into and a
# conformance check reads. Ships EMPTY: the framework + the seam, no hooks migrated here.
ORCHESTRATOR_HOOKS: HookRegistry = HookRegistry()


__all__ = [
    "ORCHESTRATOR_HOOKS",
    "HookCapabilityError",
    "HookOutputKind",
    "HookRegistry",
    "OrchestratorHook",
]
