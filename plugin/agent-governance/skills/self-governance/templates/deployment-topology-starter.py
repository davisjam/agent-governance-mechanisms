"""Deployment-topology starter — the PHYSICAL view of the 4+1 model (adopt & adapt).

This realizes the PHYSICAL view: what is deployed where, and at what scale. Author it when deploy
facts (replica counts, scale factors, per-service placement) keep drifting out of sync with the deploy
manifest — a stale "we run 3 replicas" note in a doc is exactly the lie a live model prevents.

THE LOAD-BEARING DISCIPLINE HERE: DERIVE from the manifest, don't re-annotate. The replica count and
scaling posture already live authoritatively in your deploy manifest (Kubernetes Deployment
`spec.replicas`, a Helm value, a Terraform var). This model READS that manifest at load time and
derives the fields — it never carries a second hand-typed copy that drifts the moment the manifest
changes. A per-service annotation duplicating `spec.replicas` is the anti-pattern this view exists to
avoid.

Uses PyYAML (`pip install pyyaml`) to read the manifest — declared at module scope. Fill every `# TODO:`.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class DeployedUnit:
    """One deployed unit in the physical view.

    `base_replicas` and `is_load_scaled` are DERIVED from the manifest at load time (see
    `derive_from_manifest`) — never hand-typed. `deployment_name` is the manifest's own
    `metadata.name`; keep it distinct from the logical component name so conflating the two is
    impossible.
    """
    deployment_name: str            # the manifest metadata.name — the physical identity
    component_ref: str              # the LOGICAL-view component this unit runs
    base_replicas: int              # DERIVED from manifest spec.replicas
    is_load_scaled: bool            # DERIVED — does it scale with load, or is it a singleton?
    scale_factor: float = 1.0       # optional per-unit multiplier (default; hot-overridable at runtime)


@dataclass(frozen=True)
class DeploymentTopology:
    """The whole physical view — every deployed unit, queryable."""
    units: tuple[DeployedUnit, ...]

    def unit_by_component(self, component_ref: str) -> DeployedUnit | None:
        for u in self.units:
            if u.component_ref == component_ref:
                return u
        return None


# ---------------------------------------------------------------------------
# DERIVE FROM THE MANIFEST — the load-bearing discipline. Read replicas/scale from
# the authoritative deploy manifest; never carry a hand-typed copy.
# ---------------------------------------------------------------------------


def derive_from_manifest(manifest_path: Path, *, component_ref: str) -> DeployedUnit:
    """Build a `DeployedUnit` by READING the deploy manifest — not by re-annotating replica counts.

    Reads `spec.replicas` and any scaling annotation straight from the manifest, so the model is a
    projection of the deploy truth. When the manifest changes replicas, this value changes with it —
    there is no second copy to leave stale.
    """
    doc = yaml.safe_load(manifest_path.read_text())
    spec = doc.get("spec", {})
    meta = doc.get("metadata", {})
    annotations = meta.get("annotations", {})

    base_replicas = int(spec.get("replicas", 1))  # DERIVED — the manifest owns this number
    # TODO: change the annotation key to your project's own namespace/convention.
    is_load_scaled = annotations.get("example.dev/is-load-scaled", "false") == "true"
    scale_factor = float(annotations.get("example.dev/scale-factor", "1.0"))

    return DeployedUnit(
        deployment_name=str(meta.get("name", "")),
        component_ref=component_ref,
        base_replicas=base_replicas,
        is_load_scaled=is_load_scaled,
        scale_factor=scale_factor,
    )


def load_topology(unit_specs: tuple[tuple[Path, str], ...]) -> DeploymentTopology:
    """Build the topology by deriving every unit from its manifest.

    `unit_specs` is a tuple of `(manifest_path, component_ref)` pairs — the only thing you author by
    hand is the MAPPING from a manifest to the logical component it runs; the replica/scale FACTS are
    derived.
    """
    return DeploymentTopology(
        units=tuple(derive_from_manifest(p, component_ref=ref) for p, ref in unit_specs)
    )


# ---------------------------------------------------------------------------
# THE MODEL — fill in your manifest → component mapping.
# ---------------------------------------------------------------------------

# TODO: one (manifest_path, component_ref) pair per deployed unit. Example:
#   _UNIT_SPECS = (
#       (Path("deploy/k8s/worker.yaml"), "worker"),
#       (Path("deploy/k8s/api.yaml"), "api"),
#   )
_UNIT_SPECS: tuple[tuple[Path, str], ...] = ()


# ---------------------------------------------------------------------------
# THE DRIFT-TEST CONTRACT — wire into your build so the physical map == the manifests.
# ---------------------------------------------------------------------------


def _check_drift(unit_specs: tuple[tuple[Path, str], ...]) -> list[str]:
    """Return drift findings; empty == every referenced manifest still exists and parses.

    Because the model DERIVES from the manifest rather than copying it, replica-count drift is
    impossible by construction — the remaining drift class is a manifest that MOVED or was DELETED
    while the model still points at it, which this check catches.
    """
    findings: list[str] = []
    for manifest_path, component_ref in unit_specs:
        if not manifest_path.exists():
            findings.append(f"{component_ref}: manifest '{manifest_path}' does not exist")
            continue
        try:
            yaml.safe_load(manifest_path.read_text())
        except yaml.YAMLError as exc:
            findings.append(f"{component_ref}: manifest '{manifest_path}' does not parse ({exc})")
    return findings


if __name__ == "__main__":
    _findings = _check_drift(_UNIT_SPECS)
    for _f in _findings:
        print(f"DRIFT: {_f}")
    raise SystemExit(1 if _findings else 0)
