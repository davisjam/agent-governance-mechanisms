"""3b group-apply helper (throwaway; not a catalogue entry). Loads the classification
artifact, applies one group's L2 patterns + dispositions, recomputes coverage, saves.
Idempotent per key (overwrites PENDING/prior). Run: python3 book-models/_3b_apply.py <group>."""
import json, sys, pathlib

PATH = pathlib.Path("book-models/catalogue-classification.json")

def load():
    return json.loads(PATH.read_text())

def save(d):
    # recompute coverage
    disp = d["dispositions"]
    pending = [k for k, v in disp.items() if v == "PENDING"]
    d["_coverage"] = {
        "total": len(disp),
        "pending": len(pending),
        "resolved": len(disp) - len(pending),
        "pending_keys": pending,
    }
    PATH.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
    print("saved. resolved=%d pending=%d L2=%d" % (len(disp) - len(pending), len(pending), len(d["L2_patterns"])))

def add_l2(d, key, spec):
    d["L2_patterns"][key] = spec

def dispose(d, entry, disposition, reason):
    assert entry in d["dispositions"], "unknown key: " + entry
    d["dispositions"][entry] = {"disposition": disposition, "reason": reason}

GROUPS = {}

def group(name):
    def deco(fn):
        GROUPS[name] = fn
        return fn
    return deco


@group("cap-know")
def cap_know(d):
    add_l2(d, "Executable Source of Truth", {
        "abstract_name": "Executable Source of Truth",
        "intent": "Maintain authoritative system knowledge as machine-readable typed data that is continuously consumed and mechanically held true — the interface through which a context-bounded agent operates a context-exceeding system.",
        "capability": "CAP-KNOW",
        "relation": "model ⟷ reality (the model is also the authoritative source that generates parts of the territory)",
        "score": {"novelty": 2, "agentic": 2, "durability": 2, "generality": 2, "thesis": 2, "arch_depth": 2, "evidence": 2, "tradeoffs": 2, "composition": 2, "wow": 2, "total": 20},
        "override": "Foundational — the flagship of the Modeling thesis; the whole model zoo hangs off it.",
        "canonical_card": "models-bridge/system-models/executable-source-of-truth",
        "vivid_failure": "a stale architecture paragraph that no longer matched the code, so agents reasoned from a lie",
        "concrete_impl": "the typed system-models bridge (component/zone, service-flow, deployment, ...) projected data-not-code and held true by build-time gates",
        "merged_cards": ["models-bridge/system-models/executable-source-of-truth"],
        "variants_note": "The subject-specific declared models below are VARIANTS/known-uses: each shares the six-field structure (declare authoritative typed data + build-time parity) and differs only in WHICH RELATION it models and its known-uses. Per BEWARE FALSE MERGERS each variant preserves its distinct relation (recorded in its disposition) — they are folded, not collapsed."
    })
    add_l2(d, "Read the Model, Don't Copy It", {
        "abstract_name": "Read the Model, Don't Copy It",
        "intent": "Consumers derive answers from the live model at use time — a copied-out value is banned, so one authoritative answer holds and a model change updates every consumer at once.",
        "capability": "CAP-KNOW",
        "relation": "consumer value → live model query (the copy relation banned)",
        "score": {"novelty": 2, "agentic": 2, "durability": 2, "generality": 2, "thesis": 2, "arch_depth": 1, "evidence": 1, "tradeoffs": 2, "composition": 2, "wow": 1, "total": 17},
        "override": "Foundational — the consumption discipline that keeps a single source of truth actually single.",
        "canonical_card": "models-bridge/system-models/meta-model-consumption",
        "vivid_failure": "a value snapshotted out of the model drifted from it, silently disabling a check keyed on the stale copy",
        "concrete_impl": "a ban-lint that flags copied-out model values on policed paths; consumers query the model at use time",
        "merged_cards": ["models-bridge/system-models/meta-model-consumption"]
    })
    add_l2(d, "Composed State-Machine Model", {
        "abstract_name": "Composed State-Machine Model",
        "intent": "Author the concurrency composition as one checkable object — which lifecycles exist, how they compose, and the predicates that must hold ACROSS them — each predicate carrying a derived verification obligation.",
        "capability": "CAP-KNOW",
        "relation": "composed lifecycle legality + cross-machine predicates — what may happen over time, across machines (distinct from any single machine's transition graph)",
        "score": {"novelty": 2, "agentic": 1, "durability": 2, "generality": 1, "thesis": 2, "arch_depth": 2, "evidence": 1, "tradeoffs": 1, "composition": 2, "wow": 2, "total": 16},
        "override": "Awesome — composed lifecycle machines with cross-machine property checks (inclusion crit 12).",
        "canonical_card": "models-bridge/system-models/composed-state-machine-model",
        "vivid_failure": "two async lifecycles legal alone deadlocked when composed; no single-machine model could see it",
        "concrete_impl": "typed lifecycle machines + cross-machine invariants, the specification a formal verifier runs against",
        "merged_cards": ["models-bridge/system-models/composed-state-machine-model"],
        "composition": "pairs with formal-invariant-verification (Model-Derived Assurance Coverage) — spec + checker"
    })

    esot = "Executable Source of Truth"
    # subject-variant zoo of Executable Source of Truth
    variants = {
        "models-bridge/system-models/component-zone-model": "structural ownership relation (file → component/zone/boundary); the fix-once registry every tool queries, held by bidirectional parity",
        "models-bridge/system-models/service-flow-model": "structural who-exists-and-how-wired relation of the architecture (service topology + API contracts ⟷ deployed reality); wiring generated from the model",
        "models-bridge/system-models/deployment-topology-model": "physical-topology relation (service → tier/layer/host) plus layering constraints, parity-checked against deploy tables + import graph",
        "models-bridge/system-models/data-flow-model": "governed-flow relation (data category → transitively-reachable sinks); compliance properties evaluated as graph walks — the transitive question no flat list answers",
        "models-bridge/system-models/domain-registries": "fact canonicalization (domain fact → single typed home); coverage/parity-linted, docs generated from it",
        "models-bridge/system-models/rule-metadata-registry": "governance rule → enforcement + scope metadata; policy prose made a queryable model, claims cross-checked against real enforcers (governance-of-governance lean)",
        "models-bridge/system-models/telemetry-collection-provenance": "observability-coverage relation (stream → origin/landing/per-env collection); distinguishes an absent stream from a true zero",
        "models-bridge/system-models/typed-contract-surfaces": "boundary-shape relation (producer ⟷ declared contract ⟷ consumer) plus typed boundary policy (visibility/auth/stability); both sides reconcile at build time",
        "models-bridge/system-models/timeout-budget-ordering-model": "temporal containment ordering (inner budget < containing budget), proven for every declared pair — a latent prod hang converted to a build finding [SHOWPIECE known-use, Awesome]",
        "models-bridge/system-models/synchronization-model": "synchronization-contract relation (lock → guarded resource + acquisition order); undeclared lock / inverted acquisition fail at author time",
        "models-bridge/system-models/process-view": "simultaneity/collision relation (process ∥ process over a shared resource, each race joined to its guard) — deliberately distinct from single-machine transition legality",
        "models-bridge/system-models/user-journey-model": "product goal → implementation surface (behavioral traversal joined down to endpoints); declared deps ⟷ real call sites, unlocks journey-aware differential scale-up",
        "models-bridge/system-models/agent-orchestration-model": "the same MBSE method pointed at the FLEET substrate (developer-journey + operator-loop legality) — the production substrate made as checkable as the product [SHOWPIECE: second subject arm]",
        "models-bridge/system-models/required-config-per-role-manifest": "completeness-as-admission (runtime env ⊇ role's declared required set); an incomplete environment refused at the door with the full gap [admission face; composes with Staged Admission]",
        "models-bridge/system-models/agent-first-mbse-harness": "CONSTRUCTION-METHOD variant — frozen typed records, adopt the best genre's schema, skip its runtime; hand-roll and own the executable layer per view",
        "models-bridge/system-models/model-driven-codegen": "GENERATION face — artifact = f(model); real artifacts derived + provenance-marked so hand-edits and staleness fail the build",
        "models-bridge/system-models/concurrency-contracts": "MODEL side of Mediated Resource Admission — 'who may run this, how many at once' declared as data so COVERAGE (not just seam-enforcement) is checkable; composes with the mediator pattern",
        "models-bridge/system-models/invariant-dag-execution-policy": "the correctness-check DAG as a declared model with a TYPED POLICY LAYER (correctness graph host-invariant; concurrency/budget a profile over it); composes with Mediated Resource Admission",
    }
    for k, rel in variants.items():
        dispose(d, k, "demote-to-L3-under " + esot,
                "Subject/face variant of Executable Source of Truth — same declare-typed-data+parity structure, distinct relation preserved: " + rel)

    # Read-the-Model consumers
    dispose(d, "models-bridge/system-models/query-surface", "demote-to-L3-under Read the Model, Don't Copy It",
            "The canonical self-describing READ API (one documented dialect) that makes 'read the model' ergonomic; soft, not a lint-banned monopoly.")
    dispose(d, "models-bridge/system-models/model-graded-finding-severity", "demote-to-L3-under Read the Model, Don't Copy It",
            "A model-CONSUMING gate: finding × change → severity via model distance, computed once against the live component model. Strong instance of reading-the-model to grade; no independent canonical status.")

    # canonical self
    dispose(d, "models-bridge/system-models/executable-source-of-truth", "keep-as-L2 Executable Source of Truth",
            "Canonical mechanism of CAP-KNOW.")
    dispose(d, "models-bridge/system-models/meta-model-consumption", "keep-as-L2 Read the Model, Don't Copy It",
            "Canonical consumption discipline.")
    dispose(d, "models-bridge/system-models/composed-state-machine-model", "keep-as-L2 Composed State-Machine Model",
            "Canonical behavioral/temporal composition mechanism.")


def main():
    g = sys.argv[1]
    d = load()
    GROUPS[g](d)
    save(d)

if __name__ == "__main__":
    main()
