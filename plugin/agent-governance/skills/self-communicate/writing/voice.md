# voice.md — the house author's voice

This is an **agent-facing** style doc — a resource of the `self-communicate` skill, not a catalogue entry.
It is not rendered to HTML or served. It exists to give the writer a concrete
target when matching prose to the house author's actual voice — Prof. James Davis
(davisjam), whose own published writing supplies the exemplars below.

Read this alongside [`rhetoric.md`](rhetoric.md) (the device toolkit) and the
house-rules writing-style discipline. The rhetoric file says *what tools exist*;
this file says *how the author actually swings them*.

## Three registers — and when to reach for each

The catalogue draws on three registers. Two are the house author's own voice; the third is the target
register for engineer-facing documentation, drawn from best-in-class third-party docs. The exemplars
below are grouped by register.

- **Engineering / documentation** (best-in-class third-party docs — Apache projects). Orient before
  detail, lead with a one-sentence "what it is", plain present-tense active-voice system description,
  imperative how-to steps, precise term definitions, explicit "when NOT to use this" cautions. **This is
  the register to aim for in almost all repo prose** — mechanism entries, design docs, CLAUDE rules, code
  comments, runbooks. It is a *third-party* register, NOT the author's own voice; the exemplars are labeled
  as such.
- **Discursive / argumentative** (his Medium essays). First person, direct address, extended analogy, a
  claim developed by scaffolding. Reach for it *only* where you are genuinely *persuading* — a
  **Motivation** paragraph, a design-rationale aside — walking the reader from a shared start to a
  conclusion. It is the essay register; don't let it leak into reference or how-to prose.
- **Technical / academic** (his co-authored papers). Terse, third-person or "we", claim-scope-evidence in
  tight sequence, limitations stated flat. Reach for it in an **Intent** line, a metadata summary, a "Why
  it's not just X" contrast, or a **Known uses** — anywhere a claim needs a bounded, quantified statement.

**Default to the engineering/documentation register.** Most catalogue entries want it for the spine
(Intent, card, mechanism, Known uses), the technical register for a scoped claim or contrast, and a touch
of the discursive one only where a Motivation earns persuasion. The essay and academic registers are for
their own contexts — an essay, a paper — not for a runbook or a reference entry. The technical and
engineering exemplars teach a *register*, not personal idiom (the papers are multi-author; the docs are
third-party) — how a claim is framed and scoped, how a system is described, how a caution is stated.

## The voice in six characteristics

- **Scaffolded argument, not a flat list of claims.** He states a simplified model first, then complicates
  it with named distinctions. He builds a taxonomy and defends it — essential vs. accidental, engineering
  vs. conceptual novelty — rather than asserting a conclusion and stopping. The reader is walked up the
  structure, not handed the top.
- **Plain diction carrying technical weight.** Everyday words ("pickle", "elbow scratch", "silver bullet",
  "just-so story") sit next to precise technical terms (BMC, loop unwinding, StructTreeRoot) with no
  register clash and no condescension. He reaches for the common word when it will carry the idea, and
  the exact word when it won't.
- **Concrete anchor before abstract claim.** A specific number, a named event, a worked example arrives
  *before* the generalization it supports — 72 minutes, 20 lines of code, the CrowdStrike outage, the
  Ship of Theseus. The abstraction is earned by the instance, never floated on its own.
- **Direct address and rhetorical questions guide the reader's reasoning.** "Repeat after me." "What to
  do, what to do?" "Does it really matter which transcription service you use?" He asks the question the
  reader is forming and answers it, rather than lecturing past it.
- **Confidence paired with an explicit caveat — never hedging, never absolutism.** "YES, with an
  important caveat." "But Unit Proofs are not a silver bullet." He acknowledges the counterexample and the
  limit in the same breath as the claim, then moves on. He does not perform uncertainty, and he does not
  over-claim.
- **Claim → scope → evidence, in tight sequence (technical register).** The papers reveal a move the
  essays soften: a contribution is stated, immediately bounded, then backed with a number, all in a
  sentence or two. "reduces false positive rates (from 80% to 28%), at the cost of an additional 14s
  average latency." The gap being filled is named flatly first ("gaps remain: high false-positive rates…";
  "However, we lack…"), and limitations are stated without apology or hedge. This is the register for an
  Intent line and a "Why it's not just X" contrast.

His punctuation leans on the em-dash for a qualifying aside or a mid-sentence pivot, and on quotation
marks to isolate a phrase he is about to interrogate ("just engineering", "no one has published this
before"). The em-dash is a *tool he varies with*, not a reflex — note in the exemplars how often a
period, a colon, or a plain comma does the work instead. He avoids flowery flourish, passive-voice
drift, performative hedging, and abstraction untethered from an example.

## Economy — less is more

The prose leg of the skill's governing stance (SKILL.md, §"The governing stance: less is more"): **Hemingway's
economy.** The word count is not the target; the target is that every word carries the idea. Strip the ones
that don't.

- **No fluffy adjectives.** Cut the decorative modifier that adds heat but no information — *powerful,
  seamless, robust, elegant, comprehensive, cutting-edge, sophisticated*. "A validator that checks output ⊆
  input," not "a powerful, comprehensive validator." Keep an adjective only when it is a claim the reader can
  check (*idempotent*, *at-least-once*, *148-line*) — those carry information; the fluffy ones carry mood.
  This sharpens the same edge as the "cut qualifiers" rule below, one level up: qualifiers weaken a claim,
  fluffy adjectives inflate it, and both are ornament.
- **Reserve flowery language for the contexts that earn it — and use it sparingly even there.** A blog post
  or a keynote is *persuading*, and a well-placed flourish earns its keep; that is the discursive register
  above, and the extended analogy is a tool in it. Repo prose — a reference, a runbook, a design doc — is
  not persuading; it is *informing*, and there the flourish is noise. Match the ornament to the register: a
  touch of it in a Motivation that genuinely persuades, none of it in a reference definition. Even in the
  contexts that earn it, one flourish that lands beats three that decorate.
- **The plain word beats the ornamental one when it carries the idea.** This is the "plain diction carrying
  technical weight" characteristic, stated as a rule: reach for the common word ("pickle", "silver bullet")
  when it will carry the idea, and the exact technical term only when the plain word won't. An inflated word
  doing a plain word's job is the failure this catches.

The [`audit.md`](audit.md) procedure flags a fluffy adjective as a Pass-3 house-style finding.

## Exemplars — verbatim, with the rule each teaches

The exemplars split by register. The **engineering/documentation** set (best-in-class third-party docs)
teaches the target register for repo prose; the **discursive** set (Medium essays) teaches persuasion and
rhythm; the **technical** set (co-authored papers) teaches terse claim-framing and scoping. Draw from
whichever register the section you are writing calls for — and default to the engineering one.

### Engineering / documentation — the target register (third-party exemplars)

**Provenance:** these are best-in-class **third-party** engineer-facing docs (Apache Software Foundation
projects), NOT the house author's voice. They are the register to *aim for* in repo prose — mechanism
entries, design docs, CLAUDE rules, code comments, runbooks. Each is tagged with its
[Diátaxis](https://diataxis.fr/) mode (explanation · reference · how-to · tutorial), which feeds the
engineering-discourse layer.

E1. > "ZooKeeper is a distributed, open-source coordination service for distributed applications. It
    > exposes a simple set of primitives that distributed applications can build upon to implement higher
    > level services for synchronization, configuration maintenance, and groups and naming."
    > — ZooKeeper, [overview](https://zookeeper.apache.org/doc/current/zookeeperOver.html) · *explanation*

    **Rule:** Lead with a one-sentence "what it is" before any detail. The first sentence names the thing
    and its job in plain present-tense active voice; the second says what you build *with* it. A reader who
    stops after sentence one still knows what this is.

E2. > "ZooKeeper is simple. … ZooKeeper is replicated. … ZooKeeper is ordered. … ZooKeeper is fast. It is
    > especially fast in 'read-dominant' workloads."
    > — ZooKeeper, [overview](https://zookeeper.apache.org/doc/current/zookeeperOver.html) · *explanation*

    **Rule:** Describe a system as a set of plain declaratives, each a claimed property followed by its
    consequence. Active voice, present tense, one property per sentence. The parallel "X is P" openers are
    an anaphora used *deliberately* to structure a property list — the register's sanctioned repetition.

E3. > "Maven is based around the central concept of a build lifecycle. … There are three built-in build
    > lifecycles: default, clean and site. The default lifecycle handles your project deployment, the
    > clean lifecycle handles project cleaning, while the site lifecycle handles the creation of your
    > project's web site."
    > — Maven, [build lifecycle](https://maven.apache.org/guides/introduction/introduction-to-the-lifecycle.html) · *explanation*

    **Rule:** Orient before detail: name the organizing concept, state how many parts it has, then define
    each part in one clause. The reader gets the map ("three lifecycles") before the territory, so the
    detail lands in a frame instead of arriving cold.

E4. > "An event is a statement about a change of the state of the domain modelled by the application.
    > Events can be input and/or output of a stream or batch processing application. Events are special
    > types of records."
    > — Flink, [glossary](https://nightlies.apache.org/flink/flink-docs-stable/docs/concepts/glossary/) · *reference*

    **Rule:** A reference definition is one precise sentence: the term, then its genus and differentia
    ("a statement about a change of state"). Follow with how it relates to neighbouring terms ("special
    types of records"). No motivation, no example — reference prose defines, it does not persuade.

E5. > "It is not possible to prevent such attacks entirely, but you can do certain things to mitigate the
    > problems that they create."
    > — httpd, [security tips](https://httpd.apache.org/docs/current/misc/security_tips.html) · *how-to*

    **Rule:** State the honest limit before the remedy. A how-to that overpromises loses trust; naming what
    the reader *can't* do ("prevent entirely") makes the "but you can mitigate" that follows credible. Set
    the expectation, then give the steps.

E6. > "A request for /files/../../etc/passwd could potentially access files outside the intended directory.
    > Use restrictive patterns in your RewriteRule (for example, [a-zA-Z0-9_-]+ instead of .+), and rely on
    > Apache's built-in protections (Options and <Directory> restrictions) as defense in depth."
    > — httpd, [mod_rewrite intro](https://httpd.apache.org/docs/current/rewrite/intro.html) · *how-to*

    **Rule:** Carry the concept on a concrete worked example, then give the imperative fix. The dangerous
    input is shown literally (`/files/../../etc/passwd`), the fix is an imperative with a concrete
    contrast (`[a-zA-Z0-9_-]+` instead of `.+`). Show the failing case, then command the fix.

E7. > "Don't fear the filesystem! … This structure has the advantage that all operations are O(1) and reads
    > do not block writes or each other. This has obvious performance advantages since the performance is
    > completely decoupled from the data size."
    > — Kafka, [design](https://kafka.apache.org/43/design/design) · *explanation*

    **Rule:** Name the reader's likely objection, then dismantle it with a mechanism. The blunt opener
    ("Don't fear the filesystem!") surfaces the doubt; the O(1) / decoupled-from-size reasoning answers it
    on the merits. Explanation earns a claim by walking the *why*, not by asserting the *what*.

E8. > "The TimeOut directive should be lowered on sites that are subject to DoS attacks. Setting this to as
    > low as a few seconds may be appropriate. As TimeOut is currently used for several different
    > operations, setting it to a low value introduces problems with long running CGI scripts."
    > — httpd, [security tips](https://httpd.apache.org/docs/current/misc/security_tips.html) · *how-to*

    **Rule:** Give the directive, the concrete setting, and the tradeoff in one beat. A how-to step is not
    complete until it names what the change *costs* ("introduces problems with long running CGI scripts") —
    the same claim-plus-cost discipline as the technical register, in imperative form.

### Discursive / argumentative register

1. > "The novelty argument is therefore not simply 'no one has published this before,' but rather 'this
   > task was not previously achievable in a practical way.'"
   > — [*Different contributions require different novelty arguments*](https://davisjam.medium.com/different-contributions-require-different-novelty-arguments-42b2dac0eade)

   **Rule:** The "not X, but Y" figure (correctio) works when it *redefines* — it replaces a weak framing
   with a sharper one, and the two halves carry different content. Use it to correct a misconception, not
   as a cadence you fall into every third sentence.

2. > "But Unit Proofs are not a silver bullet. They do not provide complete guarantees on their own. On
   > small programs, they can find these defects almost for 'free'. On large programs, solvers struggle."
   > — [*Unit Proofing*](https://davisjam.medium.com/unit-proofing-unit-tests-for-memory-safety-a60cf73cdae7)

   **Rule:** State the limit plainly, right after the claim. Short declaratives ("They do not provide
   complete guarantees") land harder than a hedged long sentence. The parallel "On small… / On large…"
   antithesis earns its symmetry because the two cases genuinely oppose.

3. > "Here is the key difference from the earlier types that I described. For engineering research, the bar
   > is not 'Is it in the literature?' but rather 'Is it possible through a straightforward application of
   > the state-of-the-art methods?'"
   > — [*Different contributions require different novelty arguments*](https://davisjam.medium.com/different-contributions-require-different-novelty-arguments-42b2dac0eade)

   **Rule:** Signpost the pivot in a short sentence of its own ("Here is the key difference"), then deliver
   the contrast. He frames comparisons as question-versus-question, which forces the reader to feel the
   distinction rather than be told it.

4. > "If you can construct such a solution without inventing anything new, then you have a pickle—you have
   > built a new thing that did not previously exist."
   > — [*Different contributions require different novelty arguments*](https://davisjam.medium.com/different-contributions-require-different-novelty-arguments-42b2dac0eade)

   **Rule:** A plain, slightly informal word ("pickle") in a rigorous argument is a feature, not a lapse —
   it keeps the prose human. Here the em-dash introduces the *definition* of the plain word, which is
   exactly the aside the dash is for.

5. > "This is a 'just-so story' that works well to introduce the research process. But it is a
   > simplification of research reality."
   > — [*Different contributions require different novelty arguments*](https://davisjam.medium.com/different-contributions-require-different-novelty-arguments-42b2dac0eade)

   **Rule:** Concede the useful-but-incomplete model, then complicate it. The two-sentence beat — set up,
   then "But…" — is his default engine for moving an argument forward. No em-dash needed; the period does it.

6. > "Repeat after me: 'Graduate school is not like undergraduate. Graduate school is not like
   > undergraduate.'"
   > — [*Advice on applying to graduate school*](https://davisjam.medium.com/prof-daviss-advice-on-applying-to-graduate-school-in-computing-in-the-usa-160cb539ecab)

   **Rule:** Direct address ("Repeat after me") and deliberate repetition drive one point home when it
   matters. Reserve it for the load-bearing claim — repetition everywhere is noise; repetition once is
   emphasis. The colon sets up the quoted line without a dash.

### Technical / academic register

These are from multi-author papers — they teach the *register*, not the author's personal idiom: how a
claim is framed and scoped, how a contribution and its cost are stated together, how a limitation is
stated flat.

7. > "While prior work has developed defenses against package confusions in some software package
   > registries, notably NPM, PyPI, and RubyGems, gaps remain: high false-positive rates, generalization
   > to more software package ecosystems, and insights from real-world deployment."
   > — [arXiv:2502.20528](https://arxiv.org/abs/2502.20528)

   **Rule:** Name the gap flatly, as a colon-led list, right after crediting what exists. "Gaps remain: A,
   B, and C" is the terse move for a Motivation or a "Why it's not just X" — it scopes the contribution by
   naming exactly what the prior thing lacks, no throat-clearing.

8. > "Our approach significantly reduces false positive rates (from 80% to 28%), at the cost of an
   > additional 14s average latency to filter out benign packages by analyzing the package metadata."
   > — [arXiv:2502.20528](https://arxiv.org/abs/2502.20528)

   **Rule:** State the win and its cost in one breath, both quantified. The parenthetical carries the
   number; the "at the cost of" clause carries the tradeoff. This is the register for an Intent line — a
   claim is not done until its price is on the page.

9. > "Of 89 recreated defects, systematic unit proofs detected 66 (74%) and an additional 8 (9%) with
   > increased BMC bounds, while 10 remained undetected due to memory exhaustion."
   > — [arXiv:2503.13762](https://arxiv.org/abs/2503.13762)

   **Rule:** Report the negative case with the same precision as the positive one. "10 remained undetected
   due to memory exhaustion" — the failures get a count and a cause, not a hand-wave. Being precise about
   what it *doesn't* do is how a technical claim earns trust.

10. > "External Validity: Our study evaluated unit proofing on functions from embedded operating systems.
    > This raises concerns about generalizability. On what kinds of functions do our results hold?"
    > — [arXiv:2503.13762](https://arxiv.org/abs/2503.13762)

    **Rule:** State the limitation as a plain declarative, then pose the exact question it raises and go
    answer it. No apology, no defensiveness — the limitation is named, scoped, and addressed. This is the
    "confidence + explicit caveat" characteristic in its terse form.

11. > "However, we lack in-depth industry perspectives on the practices and challenges of learning from
    > failures. To address this gap, we conducted a case study through 10 in-depth interviews with research
    > software engineers at a national space research center."
    > — [arXiv:2509.06301](https://arxiv.org/abs/2509.06301)

    **Rule:** The two-beat "However, we lack X. To address this, we did Y." is the paper's engine for
    turning a gap into a contribution. Name the missing thing, then say precisely what you did about it —
    the number ("10 in-depth interviews") anchors the method before any claim rests on it.

12. > "Our findings show that (1) constraint-based fuzz driver generation reduces the number of crashes by
    > 2–8% …; (2) context-based crash validation reduces the number of reported crashes by 57.3 – 61.3% …;
    > and (3) generating fuzz drivers with OSS-Fuzz-Gen costs less than a dollar, with tool usage
    > contributing the highest proportion of costs."
    > — [arXiv:2510.02185](https://arxiv.org/abs/2510.02185)

    **Rule:** A findings summary is a numbered list where each item is claim-plus-number, not prose. When
    you have three or more results, enumerate them — the reader scans the list, and each result carries its
    own measured value. (This is the technical twin of the house rule "an enumeration of three is a list,
    not a comma-run.")
