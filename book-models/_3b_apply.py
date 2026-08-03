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


@group("cap-sync-assurance-govern-models")
def cap_sync_assurance_govern_models(d):
    add_l2(d, "Drift / Parity Gate", {
        "abstract_name": "Drift / Parity Gate",
        "intent": "Keep the map equal to the territory bidirectionally — a build-blocking parity predicate fails the moment the model or the reality drifts unilaterally.",
        "capability": "CAP-SYNC",
        "relation": "model ⟷ reality — bidirectional parity as a build-blocking invariant",
        "score": {"novelty": 1, "agentic": 2, "durability": 2, "generality": 2, "thesis": 2, "arch_depth": 2, "evidence": 2, "tradeoffs": 2, "composition": 2, "wow": 1, "total": 18},
        "override": "Foundational — the enforcement that makes Executable Source of Truth trustworthy (a model without a parity gate degrades to a snapshot).",
        "canonical_card": "models-bridge/system-models/drift-parity-gates",
        "vivid_failure": "a moved directory silently staled every tool's private inference of the tree",
        "concrete_impl": "bidirectional parity lints wired into the build; divergence in either direction fails it",
        "merged_cards": ["models-bridge/system-models/drift-parity-gates"],
        "variants_note": "coherence-lints (cross-source relational parity), doc-hygiene-lints (corpus↔index parity), ddt-pin-trailers (test↔cited-source freshness) are known-use variants — same model⟷reality relation applied across different source pairs; each preserved distinctly."
    })
    add_l2(d, "Model-Derived Assurance Coverage", {
        "abstract_name": "Model-Derived Assurance Coverage",
        "intent": "Derive the assurance obligation from the model itself — the should-be-tested denominator, the test tier, the assertion strength, the verification method — and lint the gap, so an untested obligation is a named finding whose set regrows with every model change.",
        "capability": "CAP-COMPLETE",
        "relation": "model-declared surface → owed assurance (obligation / placement / strength / method), denominator drawn from the model not the code",
        "score": {"novelty": 2, "agentic": 2, "durability": 2, "generality": 2, "thesis": 2, "arch_depth": 2, "evidence": 1, "tradeoffs": 2, "composition": 2, "wow": 2, "total": 19},
        "override": "Awesome — test evidence ↔ modeled invariants; coverage measured over meanings, not lines.",
        "canonical_card": "models-bridge/system-models/model-derived-test-obligation-census",
        "vivid_failure": "a green coverage percentage hid an entire untested category of model obligations",
        "concrete_impl": "the obligation census derives owed tests from the models and lints the gap; four distinct-obligation variants fold under it",
        "merged_cards": ["models-bridge/system-models/model-derived-test-obligation-census"],
        "variants_note": "Five DISTINCT obligations kept as variants (not merged): obligation-census (completeness denominator), journey-criticality-test-placement (tier), journey-task-closure (assertion strength), coverage-model-mapping (per-node exercise), formal-invariant-verification (verification METHOD by temporal shape — the model-checking pole, composes with Composed State-Machine Model)."
    })
    add_l2(d, "Governance Graph", {
        "abstract_name": "Governance Graph",
        "intent": "Model the control system itself — governance mechanisms as typed conflict edges over a closed shared-resource vocabulary — so a proposed control's collisions are checkable at authoring, not at the tripwire.",
        "capability": "CAP-GOVERN",
        "relation": "control × control → conflict over a shared resource (the interaction dual of the control census; join key is the typed resource, not the call)",
        "score": {"novelty": 2, "agentic": 2, "durability": 2, "generality": 1, "thesis": 1, "arch_depth": 2, "evidence": 1, "tradeoffs": 2, "composition": 2, "wow": 2, "total": 17},
        "override": "Coverage — the governance-of-governance class (once controls proliferate the control estate needs modeling); Awesome facet: detecting control collisions.",
        "canonical_card": "models-bridge/system-models/governance-graph",
        "vivid_failure": "two controls claimed the same slot with no ordering, colliding only when both fired in production",
        "concrete_impl": "a typed interaction model; mechanically-decidable conflict classes (same-slot no-order, lock cycles) caught by construction",
        "merged_cards": ["models-bridge/system-models/governance-graph"],
        "variants_note": "control-coverage-census is the COVERAGE lens of the same governance-of-governance subject (control → governance target, portfolio completeness over a closed target taxonomy) — a distinct relation, folded here as the census variant."
    })
    add_l2(d, "Computed Control Blast Radius", {
        "abstract_name": "Computed Control Blast Radius",
        "intent": "Every control declares the substrate assumption it bakes in as a typed fact, so 'what breaks when I change this substrate' is a computed query before the change, not archaeology after it.",
        "capability": "CAP-GOVERN",
        "relation": "control → substrate assumption (the governance fleet's own dependency edges made typed and queryable)",
        "score": {"novelty": 2, "agentic": 2, "durability": 2, "generality": 1, "thesis": 1, "arch_depth": 2, "evidence": 1, "tradeoffs": 2, "composition": 2, "wow": 2, "total": 17},
        "override": "Awesome — the blast radius of an architectural migration across governance controls, computed not grepped.",
        "canonical_card": "models-bridge/system-models/control-substrate-dependency",
        "vivid_failure": "a substrate migration silently broke controls whose dependency on it lived only in someone's memory",
        "concrete_impl": "each control declares its typed substrate stance; blast radius is a query over the declarations",
        "merged_cards": ["models-bridge/system-models/control-substrate-dependency"]
    })
    add_l2(d, "Re-Derived Definition of Done", {
        "abstract_name": "Re-Derived Definition of Done",
        "intent": "Establish completion by independently re-derived evidence against the current state — never by recorded assertion; trust nothing written down before now.",
        "capability": "CAP-COMPLETE",
        "relation": "completion claim ⊨ re-derived evidence at current state — completion moves from assertion to recomputation",
        "score": {"novelty": 2, "agentic": 2, "durability": 2, "generality": 2, "thesis": 2, "arch_depth": 1, "evidence": 2, "tradeoffs": 2, "composition": 1, "wow": 1, "total": 17},
        "override": "Foundational — the Alignment-thesis completion flagship (replace self-report with recomputed evidence).",
        "canonical_card": "agent/governance-doc-controls/epic-definition-of-done",
        "vivid_failure": "an effort self-marked done while its owned checks had rotted and its commits never actually landed",
        "concrete_impl": "the close tool re-runs every owned check + verifies commit ancestry against the substrate as it stands now",
        "merged_cards": ["agent/governance-doc-controls/epic-definition-of-done"],
        "composition": "pairs with the evidence-bound commit gate (tree-sha markers) — cheap replay-proof evidence at commit, full re-derivation at close"
    })

    # Drift/Parity variants (product coherence-lints handled in product group)
    dispose(d, "models-bridge/system-models/drift-parity-gates", "keep-as-L2 Drift / Parity Gate", "Canonical CAP-SYNC mechanism.")
    dispose(d, "models-bridge/system-models/doc-hygiene-lints", "demote-to-L3-under Drift / Parity Gate",
            "Corpus-structure parity: doc corpus ⟷ its declared structure (index ⊇ docs; emitted file → declared emitter; pointer → resolvable target). Same parity relation applied to the documentation corpus; enforces the Governed Knowledge Base.")

    # Model-Derived Assurance Coverage variants
    dispose(d, "models-bridge/system-models/model-derived-test-obligation-census", "keep-as-L2 Model-Derived Assurance Coverage", "Canonical: derive the owed-test denominator, lint the gap.")
    dispose(d, "models-bridge/system-models/journey-criticality-test-placement", "demote-to-L3-under Model-Derived Assurance Coverage",
            "PLACEMENT obligation: derive the test tier as a pure function of a criticality trait, with a floor guaranteeing local-green ⟹ every major path ran. Distinct obligation from the denominator census.")
    dispose(d, "models-bridge/system-models/journey-task-closure", "demote-to-L3-under Model-Derived Assurance Coverage",
            "STRENGTH obligation: a major journey's terminal assertion provably has the shape of task closure, strength derived from the expression. Distinct obligation.")
    dispose(d, "models-bridge/system-models/coverage-model-mapping", "demote-to-L3-under Model-Derived Assurance Coverage",
            "GRANULARITY obligation: per model node (state/seam/invariant) 'is this tested?' is a queried fact a threshold cannot hide. Distinct obligation (exercise over meanings).")
    dispose(d, "models-bridge/system-models/formal-invariant-verification", "demote-to-L3-under Model-Derived Assurance Coverage",
            "METHOD obligation: route each invariant to the checker its temporal shape (safety/liveness) demands — the model-checking pole (proof across bounded interleavings, or a counterexample). Strongest/showpiece variant; composes with Composed State-Machine Model.")

    # Governance-of-governance
    dispose(d, "models-bridge/system-models/governance-graph", "keep-as-L2 Governance Graph", "Canonical control-interaction mechanism.")
    dispose(d, "models-bridge/system-models/control-substrate-dependency", "keep-as-L2 Computed Control Blast Radius", "Canonical computed-blast-radius mechanism.")
    dispose(d, "models-bridge/system-models/control-coverage-census", "demote-to-L3-under Governance Graph",
            "The COVERAGE lens of governance-of-governance: control → governance target, portfolio completeness over a closed complementary-targets taxonomy, re-derived on every query. Distinct relation from control×control conflict; folded as the census variant of the same subject.")

    # Re-Derived DoD
    dispose(d, "agent/governance-doc-controls/epic-definition-of-done", "keep-as-L2 Re-Derived Definition of Done", "Canonical CAP-COMPLETE completion mechanism.")


def main():
    g = sys.argv[1]
    d = load()
    GROUPS[g](d)
    save(d)

if __name__ == "__main__":
    main()
