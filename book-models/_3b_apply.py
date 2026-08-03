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
    dispose(d, "agent/governance-doc-controls/doc-hygiene-lints", "demote-to-L3-under Drift / Parity Gate",
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


@group("product-all")
def product_all(d):
    add_l2(d, "One Door Enforced", {
        "abstract_name": "One Door Enforced (sole sanctioned mutation surface)",
        "intent": "Route all mutation of a hazardous resource through one typed surface that encodes its invariants, with the raw alternative structurally banned — the bug made unrepresentable, not reviewed for. (Our instance: PdfModel, held by a raw-iText ban-lint.)",
        "capability": "CAP-CONSTRAIN",
        "relation": "every mutation → the sanctioned typed seam (construction, held by a counted detection sensor)",
        "score": {"novelty": 2, "agentic": 2, "durability": 2, "generality": 2, "thesis": 2, "arch_depth": 2, "evidence": 2, "tradeoffs": 2, "composition": 2, "wow": 1, "total": 19},
        "override": "Foundational — the Alignment-thesis mutation-constraint flagship.",
        "canonical_card": "product/canonical-models-and-seams/pdf-model",
        "vivid_failure": "a raw library call bypassed the format's invariants and shipped a corrupt tag tree (the v172 corruption)",
        "concrete_impl": "PdfModel is the sole PDF mutation surface; a ban-lint keeps every call site off raw iText",
        "merged_cards": ["product/canonical-models-and-seams/pdf-model"],
        "variants_note": "Same one-door RELATION over different resources, folded as known-uses (distinct resource, distinct guarantee-boundary preserved): office-models (defect-class consolidation on a 2nd object model), raw-redis-seam (shared-state + schema seam), service-client (typed cross-service seam — the signature is the enforcement), canonical-walkers (the traversal component: one walker per tree)."
    })
    add_l2(d, "Closed Action Vocabulary", {
        "abstract_name": "Closed Action Vocabulary",
        "intent": "Make the actor's move-space a closed, named, typed set — bounding the action space is what makes attribution, validation, and policy tractable at all; an absent action forces a deliberate vocabulary addition.",
        "capability": "CAP-CONSTRAIN",
        "relation": "every mutation ∈ the closed verb vocabulary (the bounded action space over the artifact)",
        "score": {"novelty": 1, "agentic": 2, "durability": 2, "generality": 2, "thesis": 2, "arch_depth": 1, "evidence": 1, "tradeoffs": 2, "composition": 2, "wow": 1, "total": 16},
        "override": "Foundational — bounding a probabilistic actor's move-space is what makes every downstream governance question finite.",
        "canonical_card": "product/repair-vocabulary/remediation-verbs",
        "vivid_failure": "an open-ended repair space made attribution and validation questions unanswerable — anything could have happened",
        "concrete_impl": "a closed, typed remediation-verb set; every mutation is one named verb",
        "merged_cards": ["product/repair-vocabulary/remediation-verbs"],
        "variants_note": "typed-categories (closed typed enum with exhaustiveness as the checkable property — category variant), role-typed-dispatch (the same closed-vocabulary move applied to AUTHORITY: bundles of capability as a typed role, enforced at every gated op), codemod-first (an execution-MODE vocabulary — soft threshold rule bounding how bulk change executes)."
    })
    add_l2(d, "Machine-Enforced Semantic Policy", {
        "abstract_name": "Machine-Enforced Semantic Policy",
        "intent": "Encode every mechanically-detectable domain invariant as a blocking check with scoped, reason-bearing escapes — audits become lints; policy moves from reviewer memory into durable machinery. (The distinctively agentic force: agents produce violations too fast for human review.)",
        "capability": "CAP-CONSTRAIN",
        "relation": "implementation ⊨ semantic policy — per-source domain invariants over the tool's own code (a DISTINCT relation from parity, provenance-coverage, and seam-mediation, even though all use lint technology)",
        "score": {"novelty": 1, "agentic": 2, "durability": 2, "generality": 2, "thesis": 2, "arch_depth": 1, "evidence": 2, "tradeoffs": 2, "composition": 1, "wow": 1, "total": 16},
        "override": "Foundational — the operational form of P5 (convert recurring failures into enforced controls).",
        "canonical_card": "product/validation-and-conformance/semantic-lints",
        "vivid_failure": "a policy that lived in reviewer memory was silently violated once the reviewer was a fleet; worse, a checker became the hazard (a ReDoS regex — the fix was deleting the regex surface, not linting the bug)",
        "concrete_impl": "the blocking-semantic-lint fleet with scoped reason-bearing suppressions",
        "merged_cards": ["product/validation-and-conformance/semantic-lints"],
        "false_merger_note": "NOT merged with Drift/Parity Gate, Caused-By Provenance's wiring lint, or the mediator ban-lints — all are 'lints' but enforce different relations."
    })
    add_l2(d, "Preservation Invariant", {
        "abstract_name": "Preservation Invariant",
        "intent": "Make semantic preservation a deterministic post-condition checked on every produced artifact — the input's content must survive as a subset of the output — with a per-stage variant that names the stage that lost it.",
        "capability": "CAP-PRESERVE",
        "relation": "input content ⊆ output content — the preservation invariant over the artifact",
        "score": {"novelty": 2, "agentic": 1, "durability": 2, "generality": 2, "thesis": 1, "arch_depth": 1, "evidence": 2, "tradeoffs": 2, "composition": 2, "wow": 1, "total": 16},
        "override": "Coverage/Case — the semantic-preservation class; indispensable to DocAble's correctness posture.",
        "canonical_card": "product/validation-and-conformance/content-validator",
        "vivid_failure": "a remediation pass silently dropped document content — 'ran successfully but produced garbage'",
        "concrete_impl": "ContentValidator checks input ⊆ output on every artifact; a staging variant localizes the offending pass",
        "merged_cards": ["product/validation-and-conformance/content-validator"],
        "composition": "the payoff of the sanctioned seam + provenance stack — damage through the one door is caught here"
    })
    add_l2(d, "Conformance-to-External-Spec Engine", {
        "abstract_name": "Conformance-to-External-Spec Engine",
        "intent": "Make conformance a deterministic predicate in which every finding names the external-standard clause it closes, and keep the coverage claim honest (covered / gap / aspirational) by a same-commit discipline.",
        "capability": "CAP-PRESERVE",
        "relation": "finding → external-standard clause — the artifact ⊨ an external conformance specification, clause-grounded",
        "score": {"novelty": 1, "agentic": 1, "durability": 2, "generality": 1, "thesis": 1, "arch_depth": 1, "evidence": 2, "tradeoffs": 1, "composition": 1, "wow": 1, "total": 12},
        "override": "Case/Coverage — indispensable to understanding DocAble (the product IS a conformance tool) + represents the external-spec-conformance class.",
        "canonical_card": "product/validation-and-conformance/standards-rule-engine",
        "vivid_failure": "an opaque conformance score could not be defended clause by clause when a claim was challenged",
        "concrete_impl": "the WCAG/standards rule engine; each finding cites its clause, coverage tracked covered/gap/aspirational",
        "merged_cards": ["product/validation-and-conformance/standards-rule-engine"]
    })
    add_l2(d, "Caused-By Provenance", {
        "abstract_name": "Caused-By Provenance (Complete Mutation Provenance)",
        "intent": "Attach durable attribution at the point of every mutation and check that the wiring is COMPLETE over a closed verb set, so the artifact's mutation history — who changed what, and why — is reconstructable on demand. (Our instance: per-mutator stamps + a wiring lint + a derived changelog.)",
        "capability": "CAP-PROVENANCE",
        "relation": "every mutation site → embedded provenance; every mutation verb → wired emission (coverage-completeness); every change → its typed cause",
        "score": {"novelty": 2, "agentic": 2, "durability": 2, "generality": 2, "thesis": 2, "arch_depth": 2, "evidence": 2, "tradeoffs": 2, "composition": 2, "wow": 2, "total": 20},
        "override": "Foundational + Awesome — reconstruct a document's mutation history from embedded provenance; the strong composition (seam → stamps → wiring-lint → changelog) is the showcase.",
        "canonical_card": "product/provenance-and-attribution/mutator-stamps",
        "vivid_failure": "an input-vs-output diff could say WHAT changed but never WHO or WHY, so a remediation could not be explained or reversed",
        "concrete_impl": "per-mutator stamps embedded at the mutation site, one sanctioned writer per format",
        "merged_cards": ["product/provenance-and-attribution/mutator-stamps"],
        "components_note": "A COMPOSED STACK, presented as one canonical pattern with named components (not merged-identical): a11y_-prefix (MARK the insertion + auto-register for validation), mutator-stamps (EMIT at the site), f10-wiring-lint (COVER: every verb wired, completeness legible + cheap), derive-changelog (READ: reconstruct the attributed history), caused-by-provenance (the AGENT-SIDE arm: every commit → typed cause from a closed taxonomy)."
    })
    add_l2(d, "Generative Validation", {
        "abstract_name": "Generative Validation",
        "intent": "Falsify a specification with machine-generated inputs at two poles — invariant-shaped properties over tame inputs (round-trip, idempotence, laws) and wild adversarial inputs fixed to the stable spec point — with the structured model as the declared oracle in the deepest form.",
        "capability": "CAP-COMPLETE",
        "relation": "generated input → declared specification (invariant / stable spec point); the model-as-oracle collapses the rich-oracle-vs-wild-input tradeoff",
        "score": {"novelty": 1, "agentic": 1, "durability": 2, "generality": 2, "thesis": 1, "arch_depth": 1, "evidence": 2, "tradeoffs": 2, "composition": 1, "wow": 1, "total": 14},
        "override": "Awesome (facet) — the model-as-oracle synthesis is the distinctive contribution; property/fuzz alone are standard practice (exclusion crit 2/9).",
        "canonical_card": "product/regression-tests/fuzz-campaigns",
        "vivid_failure": "a fix aimed at a failing fuzz SEED passed that seed and still broke every other spec-allowed input",
        "concrete_impl": "fuzz campaigns with RCA to the stable spec point + coverage measurement; FsCheck property tests at the tame-input pole",
        "merged_cards": ["product/regression-tests/fuzz-campaigns", "product/regression-tests/property-tests"],
        "merge_rationale": "The two entries self-frame as 'two sides of one coin' — same obligation (falsify the spec over generated inputs), same guarantee shape (confidence by sampling, not proof), differing only in the oracle/input pole. Merged; property-tests is the tame-oracle pole, fuzz the wild-input pole."
    })

    # One Door variants/known-uses
    dispose(d, "product/canonical-models-and-seams/pdf-model", "keep-as-L2 One Door Enforced", "Canonical sole-mutation-surface mechanism.")
    dispose(d, "product/canonical-models-and-seams/office-models", "demote-to-L3-under One Door Enforced",
            "Defect-class-consolidation known-use: the same construction+ban pattern on a 2nd object model (per-format), so a fix benefits every format at once. The entries themselves frame it as consolidation.")
    dispose(d, "product/canonical-models-and-seams/raw-redis-seam", "demote-to-L3-under One Door Enforced",
            "Shared-state-seam variant: the sole raw-Redis seam owns atomicity + the declared schema — 'no other place to write the bug'.")
    dispose(d, "product/canonical-models-and-seams/service-client", "demote-to-L3-under One Door Enforced",
            "Typed distributed variant: the ONE cross-service seam whose signature (bytes, not path) makes the type-confusion class unrepresentable.")
    dispose(d, "product/canonical-models-and-seams/canonical-walkers", "demote-to-L3-under One Door Enforced",
            "Traversal COMPONENT: one walker per tree centralizes traversal invariants. Entry self-declares low novelty — a component of the sanctioned-surface pattern, not a peer.")

    # Closed Action Vocabulary variants
    dispose(d, "product/repair-vocabulary/remediation-verbs", "keep-as-L2 Closed Action Vocabulary", "Canonical closed-action-vocabulary mechanism.")
    dispose(d, "product/repair-vocabulary/typed-categories", "demote-to-L3-under Closed Action Vocabulary",
            "Category variant: closed typed enum (ViolationCategory/FailureCategory) with exhaustiveness as the checkable property; external strings mapped in at a controlled boundary.")
    dispose(d, "product/repair-vocabulary/codemod-first", "demote-to-L3-under Closed Action Vocabulary",
            "Execution-mode variant: a soft threshold rule (N≳50 → one deterministic AST transform) bounding HOW bulk change executes. A process discipline, folded as the execution-mode face of a bounded action space.")

    # Semantic policy / preservation / conformance
    dispose(d, "product/validation-and-conformance/semantic-lints", "keep-as-L2 Machine-Enforced Semantic Policy", "Canonical implementation⊨policy mechanism.")
    dispose(d, "product/validation-and-conformance/content-validator", "keep-as-L2 Preservation Invariant", "Canonical input⊆output preservation mechanism.")
    dispose(d, "product/validation-and-conformance/standards-rule-engine", "keep-as-L2 Conformance-to-External-Spec Engine", "Canonical external-spec-conformance mechanism.")
    dispose(d, "product/validation-and-conformance/coherence-lints", "demote-to-L3-under Drift / Parity Gate",
            "Cross-source coherence: a declared relational invariant (subset/equality/one-to-one) between independent product sources — kin of model↔reality parity applied across sources. Distinct relation preserved.")

    # Caused-By Provenance components
    dispose(d, "product/provenance-and-attribution/mutator-stamps", "keep-as-L2 Caused-By Provenance", "Canonical: emit durable attribution at the mutation site.")
    dispose(d, "product/provenance-and-attribution/a11y-prefix", "demote-to-L3-under Caused-By Provenance",
            "MARK component: tool-inserted content made distinguishable by a checkable rule, every inserter auto-covered by validation via registration.")
    dispose(d, "product/provenance-and-attribution/f10-wiring-lint", "demote-to-L3-under Caused-By Provenance",
            "COVER component: completeness of provenance over the closed verb set, pitched at 'was the call made on the way out' — the level where completeness is legible AND cheap. Distinct coverage relation (not parity, not semantic policy) though the tech is a lint.")
    dispose(d, "product/provenance-and-attribution/derive-changelog", "demote-to-L3-under Caused-By Provenance",
            "READ component: provenance must have a consumer — reconstruct the attributed history from the artifact on demand (who + why, which a raw diff cannot answer).")
    dispose(d, "agent/lifecycle-and-observability/caused-by-provenance", "demote-to-L3-under Caused-By Provenance",
            "AGENT-SIDE arm: every repository change carries a typed cause from a closed taxonomy, minted at the cause and asserted at admission — a continuously-emitted traceability matrix, one row per commit. Same provenance capability, agent-side subject.")

    # Generative Validation poles
    dispose(d, "product/regression-tests/fuzz-campaigns", "keep-as-L2 Generative Validation", "Canonical (wild-input pole + model-as-oracle, the distinctive content).")
    dispose(d, "product/regression-tests/property-tests", "merge-into Generative Validation",
            "The tame-oracle / rich-invariant pole of the same generative-validation pattern; the entries self-frame as two sides of one coin.")

    # Regression demotions to other L2s
    dispose(d, "product/regression-tests/ddt-pin-trailers", "demote-to-L3-under Drift / Parity Gate",
            "Test ⟷ cited-source freshness parity: editing a cited source obliges regenerating the pin's trailer in the same change. Parity applied to the tests-derived-from-docs join.")
    dispose(d, "product/regression-tests/test-onion-tiers", "demote-to-L3-under Staged Admission Gates",
            "Cost-stratified regression body: verification cost matched to the gated decision, with escalation rules. Standard practice (exclusion crit 2); the agentic delta is escalation + the 1-second discipline under fleet velocity. Sidebar/breadth — feeds the admission staircase.")


@group("agent-remainder")
def agent_remainder(d):
    # New L2 under CAP-SYNC (3a-flagged strong standalone candidate)
    add_l2(d, "Derived Traceability", {
        "abstract_name": "Derived Traceability",
        "intent": "Make every cross-layer join a typed, DERIVED edge re-proven against live reality at read time — derived edges defend, snapshotted ones drift; liveness is a property of the representation (resolution IS the read), not a sync process running beside a stored graph.",
        "capability": "CAP-SYNC",
        "relation": "model element ⟷ its enforcing/verifying/governed artifacts — the join web between abstraction levels, held by derivation rather than storage",
        "score": {"novelty": 2, "agentic": 1, "durability": 2, "generality": 2, "thesis": 2, "arch_depth": 2, "evidence": 2, "tradeoffs": 2, "composition": 2, "wow": 2, "total": 19},
        "override": "Awesome — unusually strong evidence discipline (designed from observed drift, validated on an independent drift set); the rung above a parity gate (derive the edge so it cannot drift).",
        "canonical_card": "models-bridge/system-models/symbol-anchored-traceability-graph",
        "vivid_failure": "a stored traceability edge went stale silently — the map claimed a join that reality had severed",
        "concrete_impl": "symbol-anchored edges re-provable against live reality; a broken join reddens at scan time, a resolving anchor means the claim is currently true",
        "merged_cards": ["models-bridge/system-models/symbol-anchored-traceability-graph"],
        "composition": "the highest rung over Drift/Parity Gate — where parity CHECKS a stored model against reality, Derived Traceability removes the store so drift is unrepresentable"
    })
    # append to CAP-SYNC capability
    for cap in d["gee_capabilities"]:
        if cap["id"] == "CAP-SYNC" and "Derived Traceability" not in cap["canonical_mechanisms"]:
            cap["canonical_mechanisms"].append("Derived Traceability")

    add_l2(d, "Validated Dispatch", {
        "abstract_name": "Validated Dispatch",
        "intent": "Structurally validate the instruction packet that confers autonomy BEFORE granting it — a work order that launches an autonomous actor is deterministically checked at the point of no return, not by probabilistic review. (Pre-authorization of autonomous work.)",
        "capability": "CAP-ADMIT",
        "relation": "dispatch artifact ⊨ launch contract — the brief's declared marker/snippet set conforms to the schema of what makes a launch safe; governs the work order, not the work",
        "score": {"novelty": 2, "agentic": 2, "durability": 2, "generality": 2, "thesis": 2, "arch_depth": 1, "evidence": 1, "tradeoffs": 2, "composition": 2, "wow": 1, "total": 17},
        "override": "Foundational — distinctively agentic: admission on the WORK ORDER itself, pre-authorizing autonomy.",
        "canonical_card": "agent/context-and-dispatch/brief-linting",
        "vivid_failure": "a brief missing its worktree-isolation marker launched an agent that edited main directly — the failure surfaced downstream, not at authoring",
        "concrete_impl": "a deterministic pre-dispatch lint over the brief (marker battery + genre-gated checks) wired into the sole launch path; exit 1 refuses the launch",
        "merged_cards": ["agent/context-and-dispatch/brief-linting"],
        "components_note": "mandatory-snippet-table (the enumerable registry the lint reads — the check SOURCE), epic-and-design-templates (the same schema-on-the-artifact move applied to PLANNING artifacts — a kin variant, distinct obligation: analytic-section completeness vs launch safety)."
    })
    add_l2(d, "Staged Admission Gates", {
        "abstract_name": "Staged Admission Gates",
        "intent": "Order verification cheap-to-expensive along the path to production, each rung independently re-checkable, so no user is exposed to an unverified build and a predictably doomed run is never started.",
        "capability": "CAP-ADMIT",
        "relation": "release candidate ⊨ ordered admission contract — verification precedes exposure, staged by cost; each rung's pass is a checkable fact, not a trusted one",
        "score": {"novelty": 1, "agentic": 2, "durability": 2, "generality": 2, "thesis": 1, "arch_depth": 1, "evidence": 1, "tradeoffs": 1, "composition": 2, "wow": 1, "total": 14},
        "override": "Foundational (for the staircase) — standard practice lifted by agentic deploy velocity; two rungs carry distinctive sub-ideas (evidence-bound tree-sha commit gate; independence-proved-before-integration).",
        "canonical_card": "agent/gates-and-merge-train/staged-deploy-gates",
        "vivid_failure": "an unverified build reached users because the expensive check ran only after promotion",
        "concrete_impl": "canary → smoke → promote on traffic-free surfaces; a doomed deploy refused before it starts",
        "merged_cards": ["agent/gates-and-merge-train/staged-deploy-gates"],
        "variants_note": "The staircase's rungs, each a known-use: pre-commit-hook (evidence-bound commit gate — tree-sha markers make 'checks ran green on THIS tree' replay-proof; the strong sub-idea), sentinel-first-commit (t≈0 fail-fast substrate assertion), merge-train-mis-batching (integration rung — conflict-freedom proved BY CONSTRUCTION before landing; MIS is one implementation of 'independence before integration', the durable idea), cron-alerts-gate (health-conditioned admission — promote an observability signal into a blocking barrier), test-onion-tiers (the cost stratification the rungs consume)."
    })
    add_l2(d, "Authoritative Lifecycle State", {
        "abstract_name": "Authoritative Lifecycle State",
        "intent": "Make destructive lifecycle decisions consult an authoritative recorded fact of liveness and disposition — never an inference from side effects; the record precedes the reclaim.",
        "capability": "CAP-MANAGE",
        "relation": "destructive operation ⊨ recorded lifecycle state — authority over 'what is alive / accounted for' moves from inferred filesystem signals to an authoritative append-only record",
        "score": {"novelty": 2, "agentic": 2, "durability": 2, "generality": 2, "thesis": 1, "arch_depth": 1, "evidence": 2, "tradeoffs": 2, "composition": 1, "wow": 1, "total": 16},
        "override": "Foundational — the record-before-destructive-action principle, carried by a vivid scar.",
        "canonical_card": "agent/lifecycle-and-observability/agent-registry",
        "vivid_failure": "a cleanup heuristic inferred an agent was dead from filesystem signals and destroyed a LIVE worktree mid-run",
        "concrete_impl": "an append-only agent-registry consulted before any reclaim; tools refuse to operate on an agent whose live marker exists",
        "merged_cards": ["agent/lifecycle-and-observability/agent-registry"],
        "variants_note": "tombstone-commits is the CLOSE-RECORD variant: an irreversible reclaim justified by a durable, machine-checkable close record carrying an explicit disposition — cleanup proves safety from the record instead of guessing intent off a branch. Same obligation, at the close moment."
    })
    add_l2(d, "Mediated Resource Admission", {
        "abstract_name": "Mediated Resource Admission (fixed-capacity)",
        "intent": "Mediate shared-resource use through a single admission point at a chosen cardinality (destructive ⇒ exclusive N=1; parallel-safe-heavy ⇒ bounded M), with the raw unmediated path structurally impossible rather than conventionally discouraged, and the permitted seams declared in a model so a coverage lint detects every bypass.",
        "capability": "CAP-MANAGE",
        "relation": "every invocation → the authorized mediated seam at a bounded cardinality (mediation on the COUNT of admitted work)",
        "score": {"novelty": 1, "agentic": 2, "durability": 1, "generality": 2, "thesis": 1, "arch_depth": 1, "evidence": 2, "tradeoffs": 2, "composition": 2, "wow": 1, "total": 15},
        "override": "Foundational — the directive's own exemplar of a good pattern (inclusion crit 1: mediator + single-writer contract declared in a model + coverage lint > 'use a wrapper'). Variants are local infra (exclusion crit 4).",
        "canonical_card": "agent/mediators-and-resource-locks/test-serializer",
        "vivid_failure": "concurrent agents ran the destructive test runner simultaneously and corrupted each other's shared build state",
        "concrete_impl": "an N=1 host flock on the test runner, the raw path banned; coverage checked against the declared concurrency-contracts model",
        "merged_cards": ["agent/mediators-and-resource-locks/test-serializer"],
        "variants_note": "Cardinality variants of ONE relation: build-serializer (bounded M=8 for parallel-safe-heavy compute), aggregate-compute-protection (whole-sweep singleton — mediation at the granularity of the aggregate job). Its MODEL side is concurrency-contracts (declared coverage over the mediation regime)."
    })
    add_l2(d, "Adaptive Resource-Pressure Admission", {
        "abstract_name": "Adaptive Resource-Pressure Admission",
        "intent": "Admit AND continue heavy work only under bearable live conditions — one shared pressure signal consulted both when work is admitted and while it runs, so a RED host neither starts new heavy work nor is left running it (admit-before, shed-during).",
        "capability": "CAP-MANAGE",
        "relation": "work admission/continuation ⊨ live resource condition — gating on the STATE of the environment (vs the cardinality mediators' gating on the COUNT)",
        "score": {"novelty": 1, "agentic": 1, "durability": 1, "generality": 2, "thesis": 0, "arch_depth": 1, "evidence": 1, "tradeoffs": 2, "composition": 1, "wow": 1, "total": 11},
        "override": "Coverage — represents the ADAPTIVE pole the directive mandates splitting out of the mediator family (split by forces + guarantees, not 'both control compute').",
        "canonical_card": "agent/mediators-and-resource-locks/resource-pressure-gating",
        "vivid_failure": "fixed concurrency slots still let heavy work pile onto a host already thrashing, because the count was fine but the machine was not",
        "concrete_impl": "one shared pressure signal read at admit + during execution; shed on RED (as-built: the load-pressure ADMISSION gate is a flagged extension; shed + disk-floor wired)",
        "merged_cards": ["agent/mediators-and-resource-locks/resource-pressure-gating"],
        "split_rationale": "SPLIT from Mediated Resource Admission per the directive: the obligation (gate on live condition + shed-during) and guarantee (bearable conditions, not a fixed count) differ, even though both 'control compute'."
    })
    add_l2(d, "Fleet Observability Surface", {
        "abstract_name": "Fleet Observability Surface",
        "intent": "Make operational health a queryable, self-documenting, typo-proof signal surface and bind every signal to a prescribed response — emission alone is not observability; the loop is emit → interpret → react.",
        "capability": "CAP-MANAGE",
        "relation": "substrate event → typed topic → prescribed response — each signal carries its own interpretation and reaction (vs free-form logs that carry neither)",
        "score": {"novelty": 1, "agentic": 2, "durability": 2, "generality": 2, "thesis": 1, "arch_depth": 1, "evidence": 1, "tradeoffs": 1, "composition": 2, "wow": 1, "total": 14},
        "override": "Coverage — the observability class; the agentic delta is typed topics + a bound response (the reactor loop), not raw logging.",
        "canonical_card": "agent/lifecycle-and-observability/typed-event-bus",
        "vivid_failure": "operational failures scrolled past in free-form logs that carried neither their meaning nor a prescribed response",
        "concrete_impl": "an orchestrator-as-reactor over a typed event bus; topics enumerable, each bound to a playbook response",
        "merged_cards": ["agent/lifecycle-and-observability/typed-event-bus"],
        "variants_note": "deploy-heartbeats is the progress-liveness variant: a long operation emits periodic progress so 'no heartbeat for N windows' reads deterministically as stale (liveness ≠ correctness). cron-alerts-gate is the promote-signal-into-a-gate composition (see Staged Admission Gates)."
    })
    add_l2(d, "Point-of-Action Policy Delivery", {
        "abstract_name": "Point-of-Action Policy Delivery",
        "intent": "Deliver the constraint that governs an action to the actor at the point and moment of action — a runtime lifecycle event fires the check deterministically, converting policy from available (pull, optional) to binding (pushed into the mandatory task spec).",
        "capability": "CAP-MANAGE",
        "relation": "runtime lifecycle event / change-target → guaranteed delivery of the governing constraint at the decision point ('hard delivery of soft guidance')",
        "score": {"novelty": 1, "agentic": 2, "durability": 1, "generality": 1, "thesis": 1, "arch_depth": 1, "evidence": 1, "tradeoffs": 2, "composition": 1, "wow": 1, "total": 11},
        "override": "Historical/Case (partial) — the durable core is interposition (guaranteed firing at a runtime moment); two variants compensate for current-runtime limits (exclusion crit 3) and belong more online than in print.",
        "canonical_card": "agent/lifecycle-and-observability/lifecycle-hooks",
        "vivid_failure": "a step owed at a runtime moment depended on the actor remembering it, and was silently skipped",
        "concrete_impl": "lifecycle hooks (turn-stop / compaction / session-start / pre-action) split into guaranteed firing + a payload that blocks (hard) or aims (soft)",
        "merged_cards": ["agent/lifecycle-and-observability/lifecycle-hooks"],
        "variants_note": "dynamic-context-injection is the flagship FEED-FORWARD variant (slice the meta-substrate to just the rules governing THESE files, push them into the task spec — durable idea: 'every meta-substrate becomes a JIT constraint registry once you add a slicing operator'; but its context-reinjection face is model-progress-vulnerable). reflection-facet-substrate is the FEED-BACK variant (soft nudges under one shared attention budget — transient)."
    })
    add_l2(d, "Governed Knowledge Base", {
        "abstract_name": "Governed Knowledge Base",
        "intent": "Govern the document that carries the governance: the boot-context map of the rules must itself be bounded, canonical (one home per rule), admission-gated, and mechanically enforced — the delivery vehicle for every converted failure is itself under mechanism.",
        "capability": "CAP-GOVERN",
        "relation": "governance corpus → bounded binding index (rule → exactly-one canonical home; fleet-context ⊇ index) — the record of the mechanisms is itself under mechanism",
        "score": {"novelty": 1, "agentic": 2, "durability": 2, "generality": 2, "thesis": 1, "arch_depth": 1, "evidence": 1, "tradeoffs": 1, "composition": 1, "wow": 1, "total": 13},
        "override": "Foundational — the rule index IS the fleet's shared boot context; without governing it, the whole failure→mechanism move rots at its root.",
        "canonical_card": "agent/governance-doc-controls/claude-md-rule-index",
        "vivid_failure": "the governance index grew unbounded and citations rotted, so agents booted from a map that no longer matched the rules",
        "concrete_impl": "a size-capped, admission-gated rule index with stable citable numbering + cross-reference integrity lints",
        "merged_cards": ["agent/governance-doc-controls/claude-md-rule-index", "agent/context-and-dispatch/docs-hierarchy"],
        "merge_rationale": "claude-md-rule-index and docs-hierarchy are deliberately two LENSES on ONE artifact (the bounded canonical rule index — the enforcement lens + the boot-context lens); merged per 3a."
    })
    add_l2(d, "Encoded Operational Judgment", {
        "abstract_name": "Encoded Operational Judgment",
        "intent": "Pre-reason each recurring operational situation once, when nothing is burning — encode trigger, ordered steps, and reflexes-to-avoid — lead with the positive model of how the substrate works healthy, generate the runbook from a typed source of truth, and keep it honest by reference validation.",
        "capability": "CAP-GOVERN",
        "relation": "operational situation → prescribed response, over a substrate ⟷ positive-operational-model relation; encoded judgment keyed by the situation, not by the doc",
        "score": {"novelty": 1, "agentic": 1, "durability": 2, "generality": 2, "thesis": 1, "arch_depth": 1, "evidence": 1, "tradeoffs": 1, "composition": 1, "wow": 1, "total": 12},
        "override": "Coverage — the operations-knowledge class; the agentic delta over ordinary runbooks is generated-from-model + ref-lint-kept + positive-model-first.",
        "canonical_card": "agent/governance-doc-controls/operational-playbooks",
        "vivid_failure": "an operator improvised a recovery under fire and took a reflex the situation specifically punishes, because the judgment lived in no one's reach at the moment of need",
        "concrete_impl": "situation-keyed playbooks; an operator runbook skill generated from the lifecycle model, every pointer ref-checked against disk",
        "merged_cards": ["agent/governance-doc-controls/operational-playbooks"],
        "variants_note": "operator-runbook-skill is the GENERATED + symptom-indexed + positive-model-first variant (leads with how the substrate works healthy, falls back to symptom routing; kept honest by a ref-check since a non-executable index earns trust from ref-validation, not tests). Its source model is lifecycle-model (under Executable Source of Truth)."
    })

    # -------- dispositions --------
    dispose(d, "models-bridge/system-models/symbol-anchored-traceability-graph", "keep-as-L2 Derived Traceability", "Canonical CAP-SYNC derived-edge mechanism (3a-flagged standalone candidate).")
    dispose(d, "models-bridge/system-models/lifecycle-model", "demote-to-L3-under Executable Source of Truth",
            "Subject model: operational subsystem → healthy-state predicate + symptom keying, prose as a projection of the model. A declared system model; its runbook projection is the composition with Encoded Operational Judgment.")

    # Validated Dispatch
    dispose(d, "agent/context-and-dispatch/brief-linting", "keep-as-L2 Validated Dispatch", "Canonical work-order admission mechanism.")
    dispose(d, "agent/governance-doc-controls/mandatory-snippet-table", "demote-to-L3-under Validated Dispatch",
            "The enumerable registry of universal safety boilerplate that the dispatch lint reads — the check SOURCE (a checklist with no reader catches nothing). Component of Validated Dispatch.")
    dispose(d, "agent/governance-doc-controls/epic-and-design-templates", "demote-to-L3-under Validated Dispatch",
            "The same schema-on-the-artifact move applied to PLANNING artifacts (planning artifact ⊨ required-section schema). Kin variant, distinct obligation (analytic-section completeness vs launch safety); note the hollow-section limit — presence, not the thought in it.")

    # Staged Admission Gates
    dispose(d, "agent/gates-and-merge-train/staged-deploy-gates", "keep-as-L2 Staged Admission Gates", "Canonical path-to-production staircase.")
    dispose(d, "agent/gates-and-merge-train/pre-commit-hook", "demote-to-L3-under Staged Admission Gates",
            "The first, cheapest rung: an evidence-bound commit gate whose tree-sha markers make 'checks ran green on THIS tree' a replay-proof fact a later stage can CHECK not TRUST. Strong sub-idea; composes with Re-Derived Definition of Done.")
    dispose(d, "agent/gates-and-merge-train/sentinel-first-commit", "demote-to-L3-under Staged Admission Gates",
            "The t≈0 rung: assert environmental health at the earliest observable moment on the real dispatch path, so a doomed run aborts at minute one instead of minute sixty (bound the waste of unlandable work).")
    dispose(d, "agent/gates-and-merge-train/merge-train-mis-batching", "demote-to-L3-under Staged Admission Gates",
            "The integration rung: conflict-freedom established BY CONSTRUCTION before landing (no two members touch the same file). The directive's own exemplar of 'clever but distracts' — the durable idea is 'independence proved before integration'; MIS is one implementation, folded as a variant not a peer.")
    dispose(d, "agent/lifecycle-and-observability/cron-alerts-gate", "demote-to-L3-under Staged Admission Gates",
            "Health-conditioned admission: a surfaced critical alert becomes a blocking barrier on admitting NEW work (availability → binding, applied to alerts). The promote-a-sensor-into-a-gate move; composes with Fleet Observability Surface.")

    # Authoritative Lifecycle State
    dispose(d, "agent/lifecycle-and-observability/agent-registry", "keep-as-L2 Authoritative Lifecycle State", "Canonical record-before-destructive-action mechanism.")
    dispose(d, "agent/lifecycle-and-observability/tombstone-commits", "demote-to-L3-under Authoritative Lifecycle State",
            "Close-record variant: an irreversible reclaim justified by a durable close record with an explicit disposition — cleanup proves safety from the record instead of guessing intent off a branch.")

    # Mediated Resource Admission (fixed) + adaptive
    dispose(d, "agent/mediators-and-resource-locks/test-serializer", "keep-as-L2 Mediated Resource Admission", "Canonical single-writer (N=1) mediation with structural ban.")
    dispose(d, "agent/mediators-and-resource-locks/build-serializer", "demote-to-L3-under Mediated Resource Admission",
            "Bounded-M cardinality variant: parallel-safe-heavy compute rationed at M=8; cardinality chosen from the contention profile. Same mediation relation, different cardinality.")
    dispose(d, "agent/mediators-and-resource-locks/aggregate-compute-protection", "demote-to-L3-under Mediated Resource Admission",
            "Whole-sweep singleton variant: mediation at the granularity of the aggregate job (one whole-sweep in flight per host). Same mediation relation, coarser unit.")
    dispose(d, "agent/mediators-and-resource-locks/resource-pressure-gating", "keep-as-L2 Adaptive Resource-Pressure Admission", "Canonical adaptive pole (split from the fixed-capacity mediator family per the directive).")

    # Fleet Observability
    dispose(d, "agent/lifecycle-and-observability/typed-event-bus", "keep-as-L2 Fleet Observability Surface", "Canonical emit→interpret→react mechanism.")
    dispose(d, "agent/lifecycle-and-observability/deploy-heartbeats", "demote-to-L3-under Fleet Observability Surface",
            "Progress-liveness variant: periodic progress evidence so staleness is decidable from signal absence (liveness ≠ correctness). Distinct signal, same observability surface.")

    # Point-of-Action Policy Delivery
    dispose(d, "agent/lifecycle-and-observability/lifecycle-hooks", "keep-as-L2 Point-of-Action Policy Delivery", "Canonical interposition mechanism (guaranteed firing at a runtime moment).")
    dispose(d, "agent/context-and-dispatch/dynamic-context-injection", "demote-to-L3-under Point-of-Action Policy Delivery",
            "Feed-forward variant (flagship): slice the meta-substrate to just the rules governing the change-target and push them into the mandatory task spec. Durable idea (JIT constraint registry via a slicing operator); its context-reinjection face is model-progress-vulnerable (exclusion crit 3).")
    dispose(d, "agent/lifecycle-and-observability/reflection-facet-substrate", "demote-to-L3-under Point-of-Action Policy Delivery",
            "Feed-back variant: soft policy nudges aggregated under one shared attention budget (cap the family's aggregate emission, not each member). Historically-contingent (transient runtime-limit compensation).")

    # Governed Knowledge Base (merge two lenses) + Encoded Operational Judgment
    dispose(d, "agent/governance-doc-controls/claude-md-rule-index", "keep-as-L2 Governed Knowledge Base", "Canonical (the enforcement lens of the bounded rule index).")
    dispose(d, "agent/context-and-dispatch/docs-hierarchy", "merge-into Governed Knowledge Base",
            "The boot-context lens of the SAME artifact (one bounded canonical rule map shared by every actor). Merged with claude-md-rule-index per 3a — two views, one mechanism.")
    dispose(d, "agent/governance-doc-controls/operational-playbooks", "keep-as-L2 Encoded Operational Judgment", "Canonical situation-keyed operational-judgment mechanism.")
    dispose(d, "agent/governance-doc-controls/operator-runbook-skill", "demote-to-L3-under Encoded Operational Judgment",
            "Generated + symptom-indexed + positive-model-first variant, kept honest by reference validation. Same encode-operational-judgment relation, richer construction.")

    # L1 lift
    dispose(d, "agent/governance-doc-controls/semantic-level-enforcement", "lift-to-L1 P8 (Enforce at the right semantic level)",
            "Not a peer pattern: a design-time PLACEMENT judgment (match a control's enforcement scope to the property's legibility scope) that EXPLAINS where every other mechanism sits. Lifted out of the pattern set to L1 per 3a.")


def main():
    g = sys.argv[1]
    d = load()
    GROUPS[g](d)
    save(d)

if __name__ == "__main__":
    main()
