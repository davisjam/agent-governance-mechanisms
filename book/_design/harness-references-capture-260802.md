# Capture — harness / Agent-OS references (POST-DEPLOY; VERIFY-FIRST)

**Status:** CAPTURED 260802, do-not-act-yet. Post-deploy activity (after the editorial run's final deploy). Author directive verbatim: _"I trust the author, but check the claims and pull the real references."_

**Why this matters to MAGE:** directly feeds **Task 6 "MAGE follows from the machine"** (the harness/substrate-derivation thread) and the **foundation-model + harness §2.1** material. The harness-as-OS framing, the model–harness–environment triad, the "subtraction principle" (harness components encode assumptions about what the model can't do, and expire as models improve), and **"thin harness, fat skills"** are all load-bearing for our governance-of-the-environment thesis. Feeds the **bibliography subsystem** (`book-models/` bib SSOT + `[cite:]` markup).

## The task
1. **VERIFY each reference before citing** — the source is a LinkedIn post; several citations may be hallucinated or mis-numbered. For each: confirm it exists, pull the *real* arXiv ID / DOI / canonical URL, authors, venue, date. Flag any that cannot be confirmed (do NOT cite an unverifiable claim — record it as UNVERIFIED in the results-log).
   - Suspicious to double-check: `arXiv 2605.13357` and `arXiv 2603.28052` are plausible-format (YYMM.NNNNN → May-2026 / Mar-2026) but must be confirmed to exist and to match the attributed title/authors.
   - Anthropic "Effective Harnesses for Long-Running Agents" (Nov 2025) and Databricks "Introducing Omnigent" (Jun 2026) should have canonical first-party URLs — prefer those.
2. **Check the article's factual claims** we might repeat (e.g. "LangGraph jumped from outside top-30 to rank 5 on TerminalBench 2.0 by changing only harness infra"; "auto-optimized harness 76.4% on TerminalBench 2, 4× fewer tokens"; "Haiku outranked Opus with a better harness"). Only repeat a claim if we can source it to the underlying paper, not the LinkedIn summary.
3. **Add verified entries to the bibliography** (bib SSOT) and cite the LinkedIn article itself as the pointer that surfaced them.
4. **Weave** the confirmed ones where they earn their place (Task-6 §, §2.1 foundation-model/harness, governance-of-the-environment). Generalize the idea, cite the evidence — don't over-index on 2026-specific benchmark numbers (ties to Task 4 durability: benchmark specifics are 2026-volatile; the model–harness–environment principle is durable).

## Reference list to verify (as given by the author)
- **AI Harness Engineering** — Zhong & Zhu, arXiv **2605.13357**
- **Meta-Harness** — Lee et al. (Omar Khattab co-author), arXiv **2603.28052** (Stanford; DSPy lineage)
- **Hidden Technical Debt: Agent Harness** — Han Lee, May 2026
- **AI Agent Stack in 2026** — Reganti, April 2026
- **Effective Harnesses for Long-Running Agents** — Anthropic, November 2025
- **Introducing Omnigent** — Zaharia et al., Databricks, June 2026 (Apache-2.0, open-sourced)
- **Thin Harness, Fat Skills** — Garry Tan / gbrain, April 2026

## Surfacing article to CITE (provenance pointer)
**The Rise of the Agent OS: Comparing Harnesses, Runtimes, and Orchestration Layers for LLM Agents** — Gurbinder Gill (Co-Founder & CPO, Corvic AI), LinkedIn, **July 14, 2026**.
URL: https://www.linkedin.com/pulse/rise-agent-os-comparing-harnesses-runtimes-layers-llm-gurbinder-gill-72c9c/

### Key quotes / claims worth mining (verify against primaries before repeating)
- Stanford/Tsinghua (May 2026): _"Autonomous software-engineering capability is an emergent property of a model–harness–environment system, not of the model alone."_ ← this is the money quote for the model–harness–environment triad; find the primary (likely the AI-Harness-Engineering paper).
- Taxonomy: **agent framework** (LangGraph/CrewAI/AutoGen) vs **agent harness** (full runtime: context, tools, memory, permissions, failure recovery, verification) vs **agent OS** (general scheduling/resource mgmt across the stack).
- Han Lee analogy: _"The harness is the operating system. It provides interrupts and interfaces to the outside world, manages different processes and threads, and manages memory."_
- Anthropic **subtraction principle**: _"every harness component encodes an assumption about what the model cannot do alone, and those assumptions expire as models improve. The craft is as much removal as construction."_ ← pairs with our durability/Task-4 thesis.
- DSPy Meta-Harness: the harness designs itself — a frontier model reads raw failure traces and rewrites the orchestration layer; smaller-model-on-better-harness beats larger-model-on-worse.
- Closing rule: **"Thin harness, fat skills."** Durable substrate (data, governance, domain knowledge in reusable skills) survives model releases; control-flow scaffolding is built to be deleted.

### Full article text (archived — LinkedIn rots)
> The Rise of the Agent OS: Comparing Harnesses, Runtimes, and Orchestration Layers for LLM Agents — Gurbinder Gill, July 14, 2026
>
> A May 2026 paper from Stanford and Tsinghua put it plainly: "Autonomous software-engineering capability is an emergent property of a model–harness–environment system, not of the model alone." The evidence is hard to ignore. A benchmark deep-dive this year showed LangGraph jump from outside the top 30 to rank 5 on TerminalBench 2.0 by changing only harness infrastructure, same model, better scaffolding. The 2026 Meta-Harness paper (Lee et al., Stanford) showed an auto-optimized harness score 76.4% on TerminalBench 2, beating every hand-engineered entry while using 4x fewer tokens. Haiku outranked Opus when the harness around it was better optimized. The model is not the product anymore. The harness is.
>
> What Is a Harness? The Stanford/Tsinghua paper offers a useful starting taxonomy: Agent framework — infrastructure for composing agents and tools (LangGraph, CrewAI, AutoGen); Agent harness — the full runtime surrounding an agent: context, tools, memory, permissions, failure recovery, verification (Databricks's Omnigent, Corvic AI); Agent OS — a broader term for platforms attempting general scheduling and resource management across the full stack (VAST AI OS, Corvic). Han Lee's Hidden Technical Debt of AI Systems (May 2026): "The harness is the operating system. It provides interrupts and interfaces to the outside world, manages different processes and threads, and manages memory." A prompt shapes one call. A harness governs an entire episode.
>
> Agent Frameworks — The Orchestration Layer. LangGraph compiles agent logic into a stateful directed graph: serializable state, checkpointing, deterministic replay, parallel node execution. Production standard for complex, auditable workflows — LinkedIn, Uber, Replit. CrewAI: role-based team metaphor; ships fast, hits a ceiling at conditional branching/cycles. Microsoft Agent Framework (merged AutoGen + Semantic Kernel, October 2025). OpenAI Agents SDK — lightweight, tool-centric. Corvic Workflows and Playbooks — outcome-in-plain-language, DSL-free.
>
> Harnesses — Full Runtime Environments. Databricks Omnigent (open-sourced June 2026, Apache 2.0, Matei Zaharia's team) is the meta-harness: sits above frameworks, orchestrates across them (Claude Code, Codex, custom agents). Three primitives: Composition, Control (cost budgets, permission gates, human-approval checkpoints via Unity AI Gateway), Collaboration. Traced in MLflow. Claude Code and Codex are full-product coding harnesses — the loop, surface, tooling ship together. Anthropic's subtraction principle: every harness component encodes an assumption about what the model cannot do alone, and those assumptions expire as models improve. DSPy's Meta-Harness: the harness designs itself (Lee et al., Omar Khattab co-author) — a frontier model reads raw failure traces and rewrites the orchestration layer. Corvic AI as a runtime harness: multimodal context via MoS™, zero-hallucination retrieval, persistent memory via Data Rooms, RBAC/SOC 2, reasoning-step explainability; exposes agents via MCP.
>
> Platform-Level OS Bets. VAST Data's AI OS (May 2025): full kernel, agent runtime, event processing, messaging, distributed file/database storage — for trillions of agents across global GPU grids. Corvic AI: "the AI operating system for enterprise data" — intelligence/knowledge layer; shows up at framework + harness + data-substrate layers.
>
> The Data Substrate — The Layer Everyone Forgets. Databricks Unity Catalog + AI Search; Vector DBs (Chroma, Qdrant, Weaviate, Pinecone); MLflow 3; Corvic MoS™.
>
> The One Principle Worth Remembering. The harness engineering literature — the gbrain ethos doc, Anthropic's engineering posts, the Meta-Harness paper — converges on a single rule: Thin harness, fat skills. Build the durable substrate to last. Build the orchestration scaffolding to be deleted. Every component that compensates for something a model cannot yet do is temporary. The data, the governance, the domain knowledge in reusable skills — those survive the next model release. The control flow logic mostly does not.
