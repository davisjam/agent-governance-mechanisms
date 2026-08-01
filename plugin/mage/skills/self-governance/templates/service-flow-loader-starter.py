"""Service-flow loader starter — reads the SCENARIOS (+1) view into a typed model (adopt & adapt).

Companion to `service-flow-model-starter.yaml`. It reads every Backstage-dialect entity file in a
directory and projects them into typed, queryable model nodes — so an operating agent asks the model
"what calls this service, with what timeout / auth / request cap?" instead of grepping call sites.

THE GENRE-CHECK PAYOFF, code side: the YAML adopts the canonical Backstage schema; this loader is the
thin projection that turns that schema into your project's typed nodes. You skipped the Backstage
runtime and kept its dialect — you inherited the constraints at parse-cost only.

DISCIPLINE — the model-drift-lint contract lives at the bottom: every `component-ref` annotation must
resolve to a real component in your component-zone model, and every declared caller/`providesApis`
must resolve to a real entity. That cross-reference check is what keeps the scenarios view coherent
with the logical view instead of drifting into a fictional call graph.

Uses PyYAML (`pip install pyyaml`) — the one non-stdlib dependency, declared here so a fresh checkout
knows to install it. Fill every `# TODO:`.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Runtime-only dep declared at module scope so a fresh checkout fails loud (not request-time) if it is
# missing — and so an auto-derived dependency manifest can see it.
import yaml


@dataclass(frozen=True)
class EndpointContract:
    """One endpoint's typed contract — the facts an agent needs to reason about a call."""
    path: str
    request_body_cap: str
    latency_p99_ms: int
    client_timeout_ms: int
    server_timeout_ms: int
    requires_auth: bool


@dataclass(frozen=True)
class ApiEntity:
    """A `kind: API` entity — one service's provided endpoint contract."""
    name: str
    owner: str
    expected_callers: tuple[str, ...]
    endpoints: tuple[EndpointContract, ...]


@dataclass(frozen=True)
class ServiceEntity:
    """A `kind: Component` entity — one service and its collaboration edges."""
    name: str
    component_ref: str              # the LOGICAL-view component this maps to (drift-checked)
    auth_header: str
    expected_callers: tuple[str, ...]
    owner: str
    provides_apis: tuple[str, ...]
    depends_on: tuple[str, ...]


@dataclass(frozen=True)
class ServiceFlowModel:
    """The whole scenarios view — every service + API, queryable."""
    services: tuple[ServiceEntity, ...]
    apis: tuple[ApiEntity, ...]

    def service_by_name(self, name: str) -> ServiceEntity | None:
        for s in self.services:
            if s.name == name:
                return s
        return None


# ---------------------------------------------------------------------------
# Parsing — project the Backstage-dialect YAML into typed nodes.
# ---------------------------------------------------------------------------


def _anno(entity: dict[str, Any], key: str, default: str = "") -> str:
    """Read a `metadata.annotations.<key>` string.

    TODO: change the annotation namespace prefix (`example.dev/`) to your project's own.
    """
    return str(entity.get("metadata", {}).get("annotations", {}).get(key, default))


def _parse_callers(raw: str) -> tuple[str, ...]:
    """Parse an `expected-callers` annotation of the form "[a, b, c]" into a tuple."""
    inner = raw.strip().lstrip("[").rstrip("]")
    return tuple(part.strip() for part in inner.split(",") if part.strip())


def _parse_endpoints(api_entity: dict[str, Any]) -> tuple[EndpointContract, ...]:
    """Parse the embedded OpenAPI `paths` block into typed `EndpointContract`s."""
    definition = api_entity.get("spec", {}).get("definition", "")
    if not definition:
        return ()
    doc = yaml.safe_load(definition)
    out: list[EndpointContract] = []
    for path, methods in (doc.get("paths", {}) or {}).items():
        for _method, op in methods.items():
            out.append(EndpointContract(
                path=str(path),
                request_body_cap=str(op.get("x-request-body-cap", "")),
                latency_p99_ms=int(op.get("x-expected-latency-p99-ms", 0)),
                client_timeout_ms=int(op.get("x-client-timeout-ms", 0)),
                server_timeout_ms=int(op.get("x-server-timeout-ms", 0)),
                requires_auth=bool(op.get("x-requires-auth", False)),
            ))
    return tuple(out)


def load_service_flow_model(services_dir: Path) -> ServiceFlowModel:
    """Read every `*.yaml` in `services_dir` and project into the typed model.

    Every consumer that needs "the inter-service call graph + contracts" calls THIS — never re-derives
    it from call sites (which drift). Auto-discovery: dropping a new entity file in the directory
    registers it, no central list to edit.
    """
    services: list[ServiceEntity] = []
    apis: list[ApiEntity] = []

    for path in sorted(services_dir.glob("*.yaml")):
        for entity in yaml.safe_load_all(path.read_text()):
            if not entity:
                continue
            kind = entity.get("kind")
            meta = entity.get("metadata", {})
            spec = entity.get("spec", {})
            if kind == "Component":
                services.append(ServiceEntity(
                    name=str(meta.get("name", "")),
                    component_ref=_anno(entity, "example.dev/component-ref"),  # TODO: your namespace
                    auth_header=_anno(entity, "example.dev/auth-header"),
                    expected_callers=_parse_callers(_anno(entity, "example.dev/expected-callers")),
                    owner=str(spec.get("owner", "")),
                    provides_apis=tuple(spec.get("providesApis", []) or ()),
                    depends_on=tuple(spec.get("dependsOn", []) or ()),
                ))
            elif kind == "API":
                apis.append(ApiEntity(
                    name=str(meta.get("name", "")),
                    owner=str(spec.get("owner", "")),
                    expected_callers=_parse_callers(_anno(entity, "example.dev/expected-callers")),
                    endpoints=_parse_endpoints(entity),
                ))

    return ServiceFlowModel(services=tuple(services), apis=tuple(apis))


# ---------------------------------------------------------------------------
# THE MODEL-DRIFT-LINT CONTRACT — wire into your build so the scenarios view stays coherent.
# ---------------------------------------------------------------------------


def _check_drift(model: ServiceFlowModel, known_components: frozenset[str]) -> list[str]:
    """Return drift findings; empty == the scenarios view is coherent.

    `known_components` is the set of component names from your component-zone model (the LOGICAL view).
    Passing it in is the cross-view join: the scenarios view is only trustworthy if every service it
    names is a real component and every API it references really exists.

    Checks:
      (1) COMPONENT-REF resolves — every service's `component-ref` names a real component.
      (2) PROVIDES-API resolves — every `providesApis` entry names a declared `kind: API` entity.
    """
    findings: list[str] = []
    api_names = {a.name for a in model.apis}

    for svc in model.services:
        # (1) the cross-view link back to the logical/development view
        if svc.component_ref and svc.component_ref not in known_components:
            findings.append(
                f"{svc.name}: component-ref '{svc.component_ref}' resolves to no known component"
            )
        # (2) provided APIs must be real entities
        for api in svc.provides_apis:
            if api not in api_names:
                findings.append(f"{svc.name}: providesApis '{api}' names no declared API entity")

    return findings


if __name__ == "__main__":
    # TODO: point these at your service-flow YAML directory + your component-zone model's names.
    _services_dir = Path(__file__).resolve().parent / "services"
    _known_components: frozenset[str] = frozenset()  # TODO: from component-zone model's catalogue
    _model = load_service_flow_model(_services_dir)
    _findings = _check_drift(_model, _known_components)
    for _f in _findings:
        print(f"DRIFT: {_f}")
    raise SystemExit(1 if _findings else 0)
