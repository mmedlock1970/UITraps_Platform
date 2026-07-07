# Process-Only Evaluation KB (Cell F, v1.0)

## PROVENANCE (maintainer notes — never loaded into analysis passes)

**Cell F definition:** the evaluation *process* without the framework — the full v2.1 scaffold (two-pass discipline, evidence bars, issue composition, assessability routing, severity & confidence calibration, report architecture) with ALL trap and tenet content removed and pass-one detection replaced by a tenet-free goal-walk sweep. No rival framework is substituted. Tests whether the process alone, self-served by a competent team, approaches the full offering.

**Built from:** trap_kb_v2.1.md, sha 78a54d00 (Epoch 1 frozen master, per FREEZE_EPOCH1_2026-07-06). F inherits Epoch 1 status at build.

**Contamination pre-commitment (ratified 2026-07-06):** this file contains no trap name, no tenet name, and no distinctive definitional phrasing from the card deck or manuscript. The goal-walk sweep was author-audited line-by-line at ratification.

**Disposition of v2.1 sections:** G1 (exact trap names) — deleted, no referent. G2 (two-pass) — retained, reworded: sweep replaces per-defect detection procedures; disconfirmation genericized from the per-defect windows' function. G3 (issue composition) — retained-neutralized: atomicity, four composition forms, root-cause discrimination, parsimony retained over findings; trap line and per-trap relationship markers deleted. G4 (assessability) — retained-neutralized: three labels, observability/confirmability router, never-clear rule retained; per-defect assessability lookup becomes per-finding first-principles reasoning. G5 — retained, per-defect profile references removed. G6 — retained near verbatim; definitional-scope clause genericized. G7 — retained; sweep declares units. G8 — retained structurally; coverage vocabulary genericized; trap accounting invariant and Trap Disposition Index deleted. Severity & Confidence — retained verbatim except per-defect ceiling and rubric-line references genericized; calibration-gated ceilings and user-test sizing retained verbatim. Context Intake C1–C4 — retained; defect-name mentions genericized. Deleted wholesale: Taxonomy Index, all 27 defect chunks, Verbatim Definitions.

**Mechanics implications (route to the tool, not resolved here):** no defect chunks — splitter contract does not apply; F needs its own pack composition (pass-1 = Goal-Walk Sweep + Context Intake Schema + G2/G6/G7; pass-2 = full Global Rules + Severity & Confidence + Context Intake Schema). Per-finding relationship JSON has no defect keys under F. No Trap Disposition Index is rendered for F runs.

---

## GLOBAL RULES (apply to every analysis, both passes)

**G2. Two-pass discipline, with selective loading.**
- **Pass one (detection):** load only the Goal-Walk Sweep plus the Context Intake Schema. Run the sweep. Flag every candidate. Do not filter, do not weigh disconfirmation, do not assign severity. Over-reporting at this stage is correct behavior. Candidate-line economy: the triggering-condition clause is telegraphic — at most ~15 words, no explanatory subordinate clauses. Pass one routes candidates; pass two explains.
- **Pass two (adjudication):** load the full rule set. For each candidate, apply in order: (1) disconfirmation — actively seek the specific observation that would defeat the candidate (an alternate reading of the element, a compensating cue elsewhere on the path, a context condition that neutralizes the impediment); a candidate survives only if disconfirmation was attempted and failed, and the report states what was checked; (2) the one-problem-one-issue procedure (G3); (3) the assessability reasoning (G4/G5); (4) Severity and Confidence; (5) assemble the issue per G8. Kill, merge, and relabel freely — that is this pass's job.
- **Mode-agnostic discipline:** the staging above describes the two-pass runtime. In single-call execution the same discipline applies sequentially within one response: complete the full permissive sweep first, then adjudicate the resulting candidates. Never filter, weigh disconfirmation, or assign severity during the sweep, in any mode.

**G3. One problem, one issue — evidenced diagnosis.** When multiple candidate flags point at the same underlying design element or decision, report ONE issue. **Atomicity: the unit of an issue is the unit of independent action.** If a subset of the evidence can be fully resolved by a fix that leaves the rest intact, split it into its own issue and cross-reference the related issue(s) — duplicate controls inside a larger architectural problem are separate, precisely assignable issues. Merge only what one fix decision governs. **Issue composition — four forms, decided top-down, stop at the first match:**
1. **Single:** one failure description genuinely applies. Report it; no relationship designation.
2. **Causal chain:** one failure produces the others, and its fix dissolves them (apply the discrimination test below). The root is the finding. Consequences appear only within this issue's description — never as separate issues; where a consequence is condition-gated (e.g., repetition-dependent per C4), state the gate. The issue description states the cascade explicitly: what the root is, and what it leads to.
3. **Independent co-failures:** two or more failures each true on their own evidence, and no fix dissolves the others. Report all within the issue; address the co-occurrence in the description. A downstream consequence is NEVER a co-failure.
4. **Conditional identity:** competing descriptions of ONE failure, decided by a property the artifact cannot settle (audience, intent, context); only one is actually true. Report per the parsimony rule below: the single most applicable description plus a one-line note of the alternatives; full enumeration only when branches diverge on recommended fix or on severity — then each branch states, in the description prose, the specific condition under which it applies. Reserve this form for a genuine either/or the artifact cannot resolve; never as a hedge to avoid committing to a finding (the anti-hedging edge in G8 applies).
**Composition conservatism:** prefer the smallest faithful description set that preserves the evidence. A failure surfaced within an issue never also appears as its own separate issue. **Related-finding prose test:** the description mentions a consequence, co-failure, or conditional alternative ONLY when doing so (a) adds a consequence the primary diagnosis does not convey, (b) changes the fix's ordering or scope, or (c) is a conditional branch that would change fix or severity. Otherwise omit — the primary diagnosis carries the issue.

Then discriminate the relationship among the failure descriptions before any designation:
- **Causal chain** — the descriptions name *different failures*, and a single design change at one of them dissolves the others. Only causal chains receive a root-cause designation; apply the root-cause rule below.
- **Conditional identity** — the descriptions are *competing accounts of the same failure*, and which one applies depends on an unobservable user or context property (typically C1 prior experience or C3 context of use). NEVER designate a root cause among conditional alternatives — there is no chain, only alternative names for one defect. Report per the parsimony rule below.

**Root-cause rule (causal chains only):**
- **Fix-based root cause:** the root cause is the failure whose remediation resolves the others. Designate it "(root cause)" and mark the others "(consequence)." Worked example: an element noticed slowly *because it moves between screens* — pinning it to one location dissolves the noticing problem, so the moving placement is root cause and the delayed noticing is referenced in the explanation, not separately reported.
- **Bidirectional fixes:** when fixing either failure would resolve both, fall back to mechanism order — the failure upstream in the causal chain is root cause.
- **Root cause unclear:** designate no root cause; state "root cause unclear" AND name the specific check that would settle it. "Unclear" without a named check is unfinished adjudication. Independent co-failures — multiple failures on one element where no fix dissolves the others — get NO designation: co-occurrence without causation is neither a chain nor a conditional identity; list each with its own evidence.

**Parsimony rule (conditional identities only):** enumerating every satisfiable description burdens the reader without changing the action taken. Report the single most applicable description — selected on provided C1/C3 where given, else on the declared defaults — and append one line: "Alternative readings ([summaries]) may apply depending on [conditioning factor]." **Exceptions requiring full enumeration — branches diverge on recommended fix or on severity:** then the account is load-bearing; present each branch with its description, fix, and severity, and name the check that settles which branch the users are on. If neither provided context nor the defaults discriminate between branches, state the tie explicitly — never select arbitrarily. One named sub-case (mixed populations cannot arise: C1 names a single population per evaluation, J26):
- **Manifests-as:** one underlying property produces different failure moments for the same user population and the fix converges (e.g., an unfamiliar goal-critical element that some users never register and others register but cannot decode). This is the compact form: report one issue, "manifests as X or Y — same root property, same fix." Do not phrase this as X→Y causation: for the user who never registered the element, the registered-but-undecoded failure never occurred.

**G4. Absent vs. unassessable is a lookup, not a judgment — on two axes.** Assessability is a function of the claim, the artifact evidence, and the context evidence. Before analysis: (a) classify the artifact type (static screenshot / disconnected screens / wired prototype or flow / live product / code); (b) inventory the user context provided against the Context Intake Schema. For each candidate, reason from the artifact class and the context inventory whether the claim is assessable on both axes. Three finding labels, never interchangeable:
- "Not assessable from this artifact — [what artifact would settle it]"
- "Not assessable without user context — [what context field would settle it]"
- "Not present" — requires that the artifact CAN show the failure, required context is available or a declared default covers it, the sweep ran against the relevant scope, and no candidate survived (or disconfirmation positively ruled it out — state which). Route by observability, grade by confirmability: coverage is for what cannot be OBSERVED from the artifact; what is observed but cannot be CONFIRMED is a finding at reduced confidence with a named promotion path — never a coverage entry. A claim whose confirming method the artifact class cannot carry can never be cleared from that artifact class. Standing note, all visual artifacts: interaction-modality accessibility (keyboard and focus order, assistive-technology semantics) is largely not assessable — emit once per report: "Not assessable from this artifact — DOM/code artifacts or an assistive-technology session would settle."

**G5. Context softens or gates.** For each finding, reason what missing context does per schema field:
- Where context *sharpens* calibration: assess anyway, label "Provisional — assumes [stated assumption]," name what would sharpen it.
- Where context *gates* assessment: do not guess — emit the "not assessable without user context" label, unless a declared default covers that field, in which case assess against the default and declare it.

**G6. Named evidence — symmetric.** Every flag, in either pass, must cite the specific element(s) and condition(s) that triggered it. General impressions ("feels cluttered," "low prominence") are not findings. Clearances are held to the same bar: a "Not present" verdict must cite the specific disconfirming observation or the scope the sweep actually ran against, with the same specificity required of a finding — and must address the claim's full scope. Clearing one manifestation (one element class, one screen region) does not clear the claim; state the scope actually cleared. A clearance without named evidence is not a clearance — emit the applicable not-assessable label from G4 instead. Per-instance enumeration: any claim that an element, badge, or indicator is present on some parallel instances and absent on others must enumerate every instance with its observed state before the claim is made. Presence/absence patterns across repeated elements are the highest-risk observation class; unenumerated pattern claims are not findings.

**G7. Unit of analysis.** The Goal-Walk Sweep declares its units: per-path-step, per-screen, and cross-screen. For multi-screen artifacts: run per-screen steps on every screen in scope; run cross-screen steps where declared; compute flow-level properties (dominant interaction patterns, persistent elements) across the whole flow before consulting them in per-screen judgments — a single screen misestimates them. Every finding cites the screen(s) where its evidence sits.

**G8. Report architecture — issues first.** The evaluator's goal is to find and fix user-impacting issues. Reports have three sections:

1. **Issues.** One block per adjudicated issue: *what is happening to the user and where* (named elements, plain language, standing on its own) → *Severity* (ladder + escalators) → *Confidence* (High / Medium / Low, with the promotion path when not High confidence) → *the fix*. Order issues by severity, worst branch first.
2. **Worth a closer look.** Entries here are questions, not findings: elements whose bearing on the stated goals cannot be determined from the artifact or the provided context, but is pivotal if real. **Discriminator against Issues:** an Issue asserts a problem at some confidence — and High, Medium, and Low confidence are ALL Issue confidences; a Worth-a-closer-look entry asserts no problem — it names an assessability-blocked unknown and the check that settles it. Weak evidence never routes an entry here: a finding that clears its confidence bar, even at Low confidence, is an Issue; a suspicion that clears no bar is dropped or recorded in Coverage notes — never parked here as a low-confidence copy. **Boundary against Coverage notes:** a Coverage note records status (assessed / not assessable) with no action expected; a Worth-a-closer-look entry demands one — the named check — because the unknown is pivotal. Finding-vs-no-finding routing: when an unverifiable fact selects between a problem and no problem — as opposed to between two accounts of a problem — the entry routes HERE with the verifying check, never to Issues as a conditional assertion.
   **Entry ticket — three gates, hard AND; failing any single gate keeps the entry out:**
   - *(a) The unknown is pivotal to a stated C2 goal.* Fails (a): an ambiguous icon on a path no stated goal passes through — curiosity, not pivotality; route to Coverage notes if not assessable, else drop.
   - *(b) The worst plausible branch clears Medium severity.* Fails (b): an unlabeled element whose worst branch costs one wasted click — Low either way; drop.
   - *(c) A specific, nameable check exists.* Fails (c): "needs more research" or "unclear without testing" with no named check — unfinished adjudication (see the anti-hedging edge), not an entry.
   **Entry format:** *element and where — why it matters given the stated goal — the check, with its cost (e.g., one click in the live product; a task-based user test sized per the user-test sizing rule; a code audit) — the implication, compactly both ways.* Note that the "if not" branch is often itself a live finding; reason it through. Batch all checks into a closing verification checklist.
3. **Coverage notes.** Compressed G4 outputs, organized by goal and screen: what was assessed and found clear (with the condition that ruled it out), and what was not assessable (with what would settle it). One line per entry, from this fixed vocabulary, no elaboration: "Assessed — sweep run against [scope], no surviving conditions" / "Assessed — cleared: [disconfirming observation]" / "Not assessable from this artifact — [what would settle it]" / "Not assessable without user context — [field]" / "Assessed within scope: [assessable sub-domains]; not assessable from this artifact: [inaccessible sub-domains] — [what would settle them]". The bracketed clause is the G6 evidence; it is mandatory and it is the whole sentence's budget. Scoped-coverage rule: where a claim's domain has artifact-inaccessible sub-domains, its scoped coverage line is ALWAYS emitted — including when the claim also appears in Issues; an issue reports findings within the assessable scope and never implies the inaccessible scope was examined.

**Anti-hedging edge (both directions):** a finding whose evidence clears its confidence bar MUST be reported as an issue, even where a check could add certainty — the bucket is for genuine pivotal unknowns, not for discomfort; demoting a bar-clearing finding to Worth a closer look is under-reporting. An "I'm not sure" without a nameable check is not a bucket entry; it is unfinished adjudication — resolve it, drop it, or record it as a Coverage note, in that order of preference.

---

## GOAL-WALK SWEEP (pass one — detection; replaces per-defect detection procedures)

**Unit declaration.** The sweep runs per-path-step, per-screen, and cross-screen; every logged candidate cites the screen(s) where its evidence sits (G7).

**S1. Context intake.** Populate C1–C4 per the Context Intake Schema, applying declared defaults where fields are absent.

**S2. Goal enumeration.** From C2, list the primary task(s) and the fuller set of goals users might plausibly bring to each screen. Each goal gets its own walk.

**S3. Path enumeration.** For each goal, enumerate every path a C1-population user might plausibly attempt from the artifact's entry point — the designed path and the attempts the artifact's own surface invites. Do not prune paths the designer did not intend.

**S4. Step walk.** Walk each path step by step. At each step record: (a) what the user is trying to do; (b) what the artifact shows or does; (c) any observed condition that could block, slow, confuse, mislead, harm, or annoy this population at this step. Log every such condition as a candidate. Do not filter, do not weigh counter-evidence, do not assign severity — over-reporting at this stage is correct behavior (G2).

**S5. Whole-screen sweep.** After the walks, examine each screen in scope element by element, including regions no walked path touched. Log any condition that could impede any plausible goal from S2.

**S6. Cross-screen sweep.** For multi-screen artifacts, compare screens: log conditions observable only across screens (differences, repetitions, or drift in elements, layout, or behavior) that could impede this population. Compute flow-level properties across the whole flow before consulting them in per-screen judgments (G7).

**S7. Channel and repetition sweep.** Against C3, log steps that demand a channel the stated context leaves unavailable or degraded. Against C4, log steps whose difficulty plausibly differs between first-run and habituated users.

**Candidate-line economy.** Each candidate is telegraphic — at most ~15 words: element, condition, screen. Pass one routes; pass two explains (G2). Every candidate names its specific element(s) and condition(s) (G6); impressions without a named element are not candidates.

**Hand-off.** All candidates proceed to pass-two adjudication: disconfirmation, composition (G3), assessability (G4/G5), Severity & Confidence, report assembly (G8).

---

## SEVERITY & CONFIDENCE (single system — severity ladder + confidence scale)

**Severity ladder** — the worst plausible outcome for the stated goals (C2) under the stated context (C3), per affected user. One axis, three levels:
- **High** — task failure or abandonment with no discoverable recovery, or irreversible harm (data loss, unwanted disclosure, physical or safety harm, unrecoverable cost).
- **Medium** — recoverable failure, or recurring friction.
- **Low** — one-time friction, delay, polish.

**Severity asserts no prediction of occurrence.** It classifies the worst plausible outcome branch conditional on the failure being real for an affected user. Likelihood is carried elsewhere by design: Confidence (is the failure real), population conditioning (C1 — every finding names whom it is conditional on), the plausibility gate (evidence must make the branch live, per G6), and exposure (C4). Never write "likely" or any occurrence estimate into a severity rationale; reach is not estimated.

**Escalators:**
- **Repetition (C4):** friction on a task performed daily escalates one level; friction on a once-per-lifetime setup task does not. Friction tied to habit formation scales with repetition by nature.
- **Context (C3):** occupied channels, divided attention, motion, or time pressure can convert "recoverable" to "unrecoverable in practice" (a fumbled interaction while driving is not Medium).

Reach is not estimated. Findings are population-conditional via C1: a finding means "this population hits this." Severity is per-affected-user; priority (severity × reach × strategy) is the team's call, not the analyzer's.

**Confidence scale** — how sure the analyzer is that the problem is real, per finding:
- **High confidence** — direct evidence in hand (e.g., a "not allowed" error message; audited duplicate link targets; a visible input mask; measured contrast below standard).
- **Medium confidence** — risk conditions present, disconfirmation checked and cleared, but the confirming method is not accessible from this artifact or context.
- **Low confidence** — conditions partially present, or the judgment leans on a declared default rather than provided context.

Because severity and confidence share label words (High/Medium/Low), prose must always qualify confidence values with the word "confidence" ("capped at Medium confidence"); severity values stand bare or with "severity." The report's labeled fields (Severity: / Confidence:) disambiguate on screen.

Ceilings follow from the claim's confirming method: a claim that requires user knowledge or user behavior to confirm, analyzed from a bare screenshot, cannot exceed Medium confidence regardless of how loud the risk conditions are. Every finding below High confidence names its **promotion path**: the specific step that would confirm or dismiss it, with its cost.

**Calibration-gated ceilings.** Where a claim's threshold is a physical or absolute quantity (target size in millimeters, rendered text size, timing), that quantity is not derivable from a screenshot alone — rendered physical size depends on display hardware and resolution, which the pixels do not carry. Without calibration information (device class and resolution, or an in-artifact reference of known physical size), the ceiling is Medium confidence, promotion path "measure on the target device against [threshold]." High confidence requires stated calibration or on-device measurement. Ratios computable from pixels alone (e.g., contrast ratio) are exempt. Clearances gate identically (G6): "exceeds the minimum" is not observable from an uncalibrated artifact either.

**User-test sizing (promotion paths and remediation checks).** Never recommend a fixed participant count as a rule of thumb. Standard report wording: "Verify with a user test sized to the expected frequency of the problem — common problems need few participants; rare or severe ones need more." Mechanism, so the wording is applied correctly: severity raises the confidence bar to demand before declaring the problem absent; the confidence bar and the expected per-participant discovery rate together set the participant count. A specific count may be stated only when the assumed discovery rate is stated alongside it.

---

## CONTEXT INTAKE SCHEMA (canonical — all gates and defaults reference these fields)

**C1. User Knowledge.** Products and conventions the users have already internalized; domain expertise; prior exposure to this product's own conventions. ONE sub-population per evaluation (J26): C1 names a single population; evaluating multiple segments means running multiple evaluations. If a mixed population is provided anyway, analyze against the FIRST-NAMED segment and emit one prominent Coverage line: "Context named multiple populations; this analysis is conditioned on [first-named]. Run a separate evaluation for [others]." *Default when absent:* general adult population familiar with mainstream web/mobile conventions — declare it. Brand-specific, domain-insider, and novel elements cannot be cleared under the default.

**C2. Goals.** The user's primary tasks and critical paths — AND the fuller set of goals users might plausibly bring to each screen (some checks require the full set, not just the primary). *Default when absent:* infer the apparent primary task from the screen itself and declare it; findings requiring the full goal set are degraded under this default.

**C3. Context of Use.** Availability of the user's channels and circumstances:
- *Attention:* fully focused, dividing attention across concurrent tasks, or frequently interrupted.
- *Vision:* eyes available vs. occupied (driving, walking, operating equipment).
- *Hearing:* environment quiet enough to hear audio, or too noisy.
- *Speech & audio-out:* free to speak and play audio comfortably — or constrained by disturbing others or by privacy (information that must not be overheard or displayed to bystanders).
- *Hands:* both free, one occupied, both occupied.
- *Mobility:* stationary vs. in motion.
- Plus: lighting, time pressure or stress, device and input method.

*Default when absent:* attentive, stationary, unencumbered, quiet, private use — the most forgiving context on every channel. Declare it, and state that findings under this default are a lower bound: occupied channels raise likelihood of attention- and memory-dependent failures and can create channel-dependent failures outright (an auditory-only element in a loud environment; a two-handed interaction for an encumbered user) without any change to the pixels.

**C4. Exposure & Repetition.** Two facets of the learning curve:
- *User exposure stage:* first-run users, habituated users, or a mix.
- *Task repetition profile:* performed once (setup, onboarding), a few times, or repeatedly for as long as the product is used.

Habit-dependent friction scales with repetition; one-time tasks make first-encounter comprehension paramount — every user is a first-timer, forever. *Defaults when absent:* mix including first-time users for public-facing products; infer the task's repetition profile from its nature (setup vs. core loop) — declare both.
