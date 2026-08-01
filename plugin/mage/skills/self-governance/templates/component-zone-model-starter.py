"""Component-zone model starter — the LOGICAL / DEVELOPMENT view of the 4+1 model (adopt & adapt).

This realizes two 4+1 views at once from a single typed catalogue:
  - the LOGICAL view (what the parts ARE and how they group), and
  - the DEVELOPMENT view (how the code is ORGANIZED — focus-dirs, owner, tags).

It is the backbone an operating agent reasons through when it asks "which module owns X?", "what is
the boundary of this subsystem?", or "which zone should this audit sweep?". Author it when agents keep
mis-scoping ownership, or when you want per-zone audit sweeps that don't drift as directories move.

The single source of truth is a list of typed `Component`s. Every OTHER tool that needs "what are our
parts" (per-zone audits, LoC accounting, boundary lints, report generation) reads THIS list rather
than re-deriving it — a hardcoded list elsewhere drifts; this one keeps paying dividends.

Discipline (a) LOOK UP, DON'T COPY applies here as the drift-test contract at the bottom: the model's
declared `focus_dirs` must still EXIST on disk, and every top-level source directory should be CLAIMED
by exactly one component — a directory the model forgot, or a `focus_dir` that no longer exists, is a
finding. That is what keeps the logical map equal to the code territory.

Stdlib-only. Fill every `# TODO:` with your project's own zones.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class ComponentKind(Enum):
    """How a component participates in the tools that read this catalogue.

    Keeping the kind explicit lets a consumer filter precisely (e.g. an audit sweeps `LEAF` + `GROUP`
    but skips `META`; a LoC report counts `LEAF` + `META` but skips `GROUP` to avoid double-counting).
    """
    LEAF = "leaf"    # a single coherent subsystem — the unit an audit sweeps
    GROUP = "group"  # a cross-cutting bundle of leaves swept as one zone (excluded from LoC to avoid double-count)
    META = "meta"    # an accounting bucket that is not an audit zone (tests, docs, deploy infra, tooling)


class BoundaryKind(Enum):
    """The trust/architecture boundary a component sits behind — the sole-seam story.

    Marks whether a component is reached through a single sanctioned seam (a typed client, a canonical
    library wrapper) or is an internal zone. A boundary lint can then assert "nobody crosses into this
    component except through its declared seam."
    """
    # TODO: tailor to your architecture. Example members:
    INTERNAL = "INTERNAL"          # an in-process zone, no special boundary
    SERVICE_SEAM = "SERVICE_SEAM"  # reached only via a typed cross-service client
    LIBRARY_SEAM = "LIBRARY_SEAM"  # reached only via a canonical library wrapper


@dataclass(frozen=True)
class Component:
    """One part of the system — the unit of the logical/development view.

    `focus_dirs` are repo-relative source directories this component OWNS; they are what the drift-test
    resolves against disk and what a per-zone audit sweeps. `zone` groups components into higher-level
    regions (e.g. "runtime", "product-core", "infra"). `tags` carry orthogonal facets a consumer
    filters on (language, "service", "public-api", …).
    """
    name: str                       # canonical name — the lookup key other tools cite
    kind: ComponentKind
    focus_dirs: tuple[str, ...]     # repo-relative dirs this component owns (drift-checked against disk)
    zone: str                       # higher-level region this component belongs to
    boundary_kind: BoundaryKind = BoundaryKind.INTERNAL
    owner: str = ""                 # the team/individual responsible (development view)
    tags: tuple[str, ...] = ()      # orthogonal facets: language, "service", "public-api", …
    description: str = ""
    exclude_subdirs: tuple[str, ...] = field(default=())  # sub-paths to omit from sweeps/LoC


@dataclass(frozen=True)
class ComponentCatalogue:
    """The whole logical/development view — every component, queryable."""
    components: tuple[Component, ...]

    def leaves(self) -> tuple[Component, ...]:
        return tuple(c for c in self.components if c.kind is ComponentKind.LEAF)

    def audit_zones(self) -> tuple[Component, ...]:
        """What a per-zone audit sweeps: leaves + groups (not accounting buckets)."""
        return tuple(c for c in self.components if c.kind in (ComponentKind.LEAF, ComponentKind.GROUP))

    def by_name(self, name: str) -> Component | None:
        for c in self.components:
            if c.name == name:
                return c
        return None

    def all_focus_dirs(self) -> frozenset[str]:
        return frozenset(d for c in self.components for d in c.focus_dirs)


# ---------------------------------------------------------------------------
# THE CATALOGUE — fill in your project's zones.
# ---------------------------------------------------------------------------

# TODO: one Component per real part of your system. Example shape:
#   Component(
#       name="worker",
#       kind=ComponentKind.LEAF,
#       focus_dirs=("worker/",),
#       zone="runtime",
#       boundary_kind=BoundaryKind.INTERNAL,
#       owner="platform",
#       tags=("python", "runtime"),
#       description="the job-processing loop",
#   ),
#   Component(
#       name="tests",
#       kind=ComponentKind.META,          # accounting bucket, not an audit zone
#       focus_dirs=("test/",),
#       zone="infra",
#   ),

CATALOGUE = ComponentCatalogue(
    components=(
        # TODO: your Component(...) instances here.
    )
)


# ---------------------------------------------------------------------------
# THE LOADER STUB — a thin helper so consumers query the catalogue, not re-derive.
# ---------------------------------------------------------------------------


def load_catalogue() -> ComponentCatalogue:
    """Return the single-source-of-truth catalogue.

    Every consumer (audits, LoC accounting, boundary lints, report generation) calls THIS instead of
    re-deriving "what are our parts" — a hardcoded list elsewhere drifts; this one stays authoritative.
    """
    return CATALOGUE


# ---------------------------------------------------------------------------
# THE DRIFT-TEST CONTRACT — wire into your build so the logical map == the code.
# ---------------------------------------------------------------------------


def _check_drift(catalogue: ComponentCatalogue, repo_root: Path) -> list[str]:
    """Return drift findings; empty == the catalogue matches the tree.

    Two checks:
      (1) EXISTENCE — every declared `focus_dir` still exists on disk. A renamed/deleted directory the
          model still claims is a finding.
      (2) COVERAGE — every top-level source directory is CLAIMED by some component. A new directory
          nobody added to the catalogue is a finding (this is the check that forces the model to grow
          WITH the code instead of silently falling behind).
    """
    findings: list[str] = []

    # (1) EXISTENCE
    for comp in catalogue.components:
        for d in comp.focus_dirs:
            if not (repo_root / d).exists():
                findings.append(f"{comp.name}: focus_dir '{d}' does not exist on disk")

    # (2) COVERAGE — every top-level source dir must be claimed.
    claimed_tops = {d.split("/", 1)[0] for d in catalogue.all_focus_dirs()}
    # TODO: adjust the ignore set to your repo's non-source top-level entries.
    _IGNORE = {".git", ".github", "node_modules", "__pycache__", "venv", ".venv"}
    for entry in sorted(repo_root.iterdir()):
        if not entry.is_dir() or entry.name in _IGNORE or entry.name.startswith("."):
            continue
        if entry.name not in claimed_tops:
            findings.append(f"UNCLAIMED: top-level dir '{entry.name}/' is in no component")

    return findings


if __name__ == "__main__":
    # TODO: point this at your repo root (e.g. the parent of this model's directory).
    _root = Path(__file__).resolve().parent
    _findings = _check_drift(CATALOGUE, _root)
    for _f in _findings:
        print(f"DRIFT: {_f}")
    raise SystemExit(1 if _findings else 0)
