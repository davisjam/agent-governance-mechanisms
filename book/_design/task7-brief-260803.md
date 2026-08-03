# READY-TO-DISPATCH BRIEF — TASK 7: harness/Agent-OS references → bib + weave (Opus)

Post-deploy. Model **opus**. run_in_background. Live tree, branch main, NO worktree, single writer. commit-early. Deploy at end. Record to results-log. All 7 refs are VERIFIED REAL (see table) — cite with the CORRECTED metadata below; handle the benchmark claims with the guardrails.

## Brief text (paste into Agent prompt)

You are adding a verified set of external references to the MAGE book and weaving them into the harness material (LIVE checkout `/Users/davisjam/Projects/ada-tool/talks-and-notes/governance-catalog`, branch main — NO worktree, you are the only writer). Work slow+correct, commit early. NOT the parent ada-tool product — book workflow = edit → `catalog.py validate` → `book/build_book_html.py` → `catalog.py deploy github`.

**WHY:** ch `1.4-why-mage-follows-from-the-machine` (Task 6) argues MAGE follows from the foundation-model + harness substrate. A real 2026 "harness engineering" literature has emerged that CONVERGES with that thesis — citing it grounds the book's argument in the field rather than presenting it as invented in a vacuum. Add these references and weave the load-bearing ones into 1.4 + §2.1.

**READ FIRST:**
- `book/_design/harness-references-capture-260802.md` — the original capture: the full Gill LinkedIn article text + the key concepts (model–harness–environment triad, the harness-as-OS framing, Anthropic's "subtraction principle," "thin harness, fat skills"). Context for the weave.
- `book/_design/bibliography-subsystem-260801.md` + `book-models/` — the bib SSOT + the `[cite: key]` markup (numeric superscript). Learn how to add a bib entry + cite it. Follow the existing idiom exactly.
- `book/part1/1.4-why-mage-follows-from-the-machine.md` and `book/part2/2.1-the-agent-stack.md` — the weave targets.

**THE 7 VERIFIED REFERENCES (use this CORRECTED metadata — exact titles/authors/dates/URLs):**
1. **Zhong & Zhu 2026** — "AI Harness Engineering: A Runtime Substrate for Foundation-Model Software Agents," Hailin Zhong & Shengxin Zhu, arXiv:2605.13357, 13 May 2026. https://arxiv.org/abs/2605.13357  (likely the source of the "autonomous SE capability is an emergent property of a model–harness–environment system, not the model alone" framing.)
2. **Lee et al. 2026 (Meta-Harness)** — "Meta-Harness: End-to-End Optimization of Model Harnesses," Yoonho Lee, Roshen Nair, Qizheng Zhang, Kangwook Lee, Omar Khattab, Chelsea Finn (Stanford/MIT), arXiv:2603.28052, 30 Mar 2026. https://arxiv.org/abs/2603.28052
3. **Han Lee 2026** — "Hidden Technical Debt of AI Systems: Agent Harness" (NOTE corrected title), Han Lee, blog, 8 May 2026. https://leehanchung.github.io/blogs/2026/05/08/hidden-technical-debt-agent-harness/
4. **Reganti 2026** — "The AI Agent Stack in 2026," Aishwarya Naresh Reganti, Substack, 29 Apr 2026. https://thenuancedperspective.substack.com/p/the-ai-agent-stack-in-2026
5. **Young / Anthropic 2025** — "Effective harnesses for long-running agents," Justin Young (Anthropic), 26 Nov 2025. https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents  (the "subtraction principle" source.)
6. **Zaharia et al. / Databricks 2026** — "Introducing Omnigent: A Meta-Harness to Combine, Control and Share Your Agents," Matei Zaharia, Kasey Uhlenhuth, Corey Zumar, Databricks blog, 13 Jun 2026 (Apache-2.0). https://www.databricks.com/blog/introducing-omnigent-meta-harness-combine-control-and-share-your-agents
7. **Tan 2026** — "Thin Harness, Fat Skills," Garry Tan, gbrain repo ethos docs, 9–11 Apr 2026. https://github.com/garrytan/gbrain/blob/master/docs/ethos/THIN_HARNESS_FAT_SKILLS.md
- **Surfacing pointer (cite as the source that surfaced these):** Gurbinder Gill, "The Rise of the Agent OS: Comparing Harnesses, Runtimes, and Orchestration Layers for LLM Agents," LinkedIn, 15 Jul 2026 (NOTE: page shows Jul 15, not Jul 14). https://www.linkedin.com/pulse/rise-agent-os-comparing-harnesses-runtimes-layers-llm-gurbinder-gill-72c9c/

**⚠️ BENCHMARK-CLAIM GUARDRAILS (do NOT repeat these as unqualified facts):**
- The "LangGraph jumped to Top-5 on TerminalBench 2.0 by changing only the harness" claim is really **LangChain's `deepagents-cli` (52.8%→66.5%, same model)** — cite it precisely if used (source: LangChain blog "Improving Deep Agents with harness engineering"), NOT as "LangGraph."
- The "76.4% on TerminalBench-2, 4× fewer tokens" line **CONFLATES two different Meta-Harness experiments** (the 76.4% used Opus 4.6 on TBench-2; the 4×-fewer-tokens is a *different* benchmark, online text classification). Do NOT combine them — either cite one precisely or omit the numbers.
- **"Haiku outranked Opus with a better harness" has NO pinned primary source — do NOT state it as fact.**
- GENERALIZE the durable IDEA, not the volatile 2026 numbers: the load-bearing, durable claims to weave are **the model–harness–environment triad** (capability is a property of the system, not the model alone), **the harness-as-runtime/OS** framing, **the subtraction principle** (harness components encode assumptions about what the model can't yet do, and expire as models improve — pairs with our durability thread), and **"thin harness, fat skills"** (durable substrate vs. deletable scaffolding). Prefer these principles over any benchmark figure. (This anticipates Task-4 durability: the principle survives even as the 2026 numbers age.)

**THE WEAVE (light, high-value — do NOT bloat the chapters):**
- In **1.4**, add a short grounding note (a few sentences + citations) that the model–harness–environment framing MAGE derives is now an emerging research + industry consensus — cite Zhong&Zhu (triad), Young/Anthropic (subtraction principle), Lee et al. (harness-as-variable), Tan (thin-harness-fat-skills). Keep MAGE's distinct contribution clear (MAGE = the *engineering method* implied by the substrate + governance; these are the substrate/harness literature it stands on).
- In **§2.1**, where the foundation-model + harness stack is described, add the taxonomy grounding (framework vs harness vs agent-OS — Gill/Reganti) + the harness-as-OS analogy (Han Lee) as citations, briefly.
- Add ALL 7 to the bibliography (+ the Gill pointer) even if not every one is cited inline — the references section can carry the fuller reading list.

**DISCIPLINE:** house style; `[cite:]` idiom exactly as the bib subsystem defines; C7 watch-phrase discipline; book coverage ⊇ site framings; no fabricated numbers.

**GATES:** `catalog.py validate` 0 · `book/build_book_html.py` green · `catalog.py deploy github`; foreground-poll Deploy Pages CI to success; curl 1.4 + 2.1 + the bibliography page for 200 + spot-check a citation renders.

**RECORD (do not relay):** append a `## TASK 7 — harness references` block to `book/_design/editorial-run-results-260802.md`: which refs added to the bib, where each is cited, the benchmark-claim decisions (what you cited vs omitted/caveated), gates, live SHA.

Thorough over fast. On ambiguity, make the defensible call, DOCUMENT it, continue.
