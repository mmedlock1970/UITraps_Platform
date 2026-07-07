# UI Tenets & Traps — Analyzer Knowledge Base — v1.1 (card-deck-content lineage; card content + v2.1 process structure)

## PROVENANCE (maintainer notes — never loaded into analysis passes)

**Purpose.** This KB is experiment cell D: the v2.1 two-pass process structure applied to v1 card-deck knowledge only. Its per-trap content is generated MECHANICALLY from the card deck (Tenets_and_Traps_Card_MASTER_print.pdf) — verbatim definitions, one example each — with no enrichment from the book manuscript, the v2 KBs, or the KB authors. Thinness of chunks is a property of the source, preserved deliberately: the content difference between this file and trap_kb_v2.1.md is the variable the experiment measures.

**v1 canon, preserved exactly:** 9 Tenets (Understandable, Comfortable, Responsive, Efficient, Forgiving, Discreet, Protective, Habituating, Beautiful); 26 Traps; card names verbatim including "Unnecessary Step" (singular) and "Unattractive Appearance"; Bad Prediction under Efficient; the card vocabulary "cue (label, icon, affordance, or prompt)"; card definitions verbatim even where they differ from v2 canon (e.g., Accidental Activation as misinterpretation of physical actions; Gratuitous Redundancy scoped to actions only). No Incorrect Information Trap exists in this source.

**Structure inherited from v2.1 (trap-agnostic process only):** two-pass discipline with selective loading; one-problem-one-issue with root-cause designation (per the card deck's own How to Use steps 3 and 5: log all Traps with severity; ask whether one Trap is the root cause of the others); two-axis assessability; context softening/gating with declared defaults; named evidence; unit of analysis; issues-first report architecture; the severity ladder and confidence scale.

**Stripped from the inherited structure (trap-specific v2 content, documented for auditability):** the sibling-Trap reserved definition; the segment-conditional and manifests-as trap-line patterns and all worked examples naming Traps; C2's Inviting-Dead-End pointer; illustrative High confidence-evidence examples in the confidence scale; the closer-look bucket's trap-named illustration. Per-trap detection procedures, disconfirmation decompositions, assessability lines, and remediation notes below are derived from each card's definition sentence by a fixed template — no external knowledge added.

**Scaffold parity log (2026-07-04).** The trap-agnostic process rules ratified in v2.1 on this date (J18 test sizing; J19 symmetric clearance evidence; J20 candidate/coverage economy; J21 causal-chain vs conditional-identity gate with parsimony rule; J22 calibration-gated ceilings, incl. the Physical Challenge Assessability line; J23 closer-look discriminator and hard-AND ticket; J24 mode-agnostic discipline; J25 severity-asserts-no-occurrence clarification) are mirrored here per the D-cell design: v1 content, current process. Ported with the strip-list discipline applied — no sibling reference, no trap-named sub-case patterns or examples; vocabulary adapted to the card's "cue" terminology. D and E share this scaffold version as of this date; scaffold edits land in both masters in the same pass from here on. Q&A ratification cycle additions (same date): J26 (one sub-population per evaluation, C1) and J27 (scoped coverage for partially assessable Traps, G8) mirrored; G3 gains the independent-co-failures no-designation line; PC promotion path made modality-conditional. All v2.1 scaffold rules are author-ratified as of this date (see v2.1 Open Items closure log); trap-content rulings from the same cycle are v2.1-only per the content/process split.

---

## GLOBAL RULES

**G1. Exact trap names.** Use full, exact Trap names; several Traps have near-identical names that denote different problems.

**G2. Two-pass discipline, with selective loading.**
- **Pass one (detection):** load only the Detection Procedures for all 26 Traps, plus the Context Intake Schema. Run each procedure. Flag every candidate. Do not filter, do not weigh disconfirmation, do not assign severity. Over-reporting at this stage is correct behavior. Candidate-line economy: the triggering-condition clause is telegraphic — at most ~15 words, no explanatory subordinate clauses. Pass one routes chunks; pass two explains.
- **Pass two (adjudication):** load the full chunks for candidate Traps only, plus the Taxonomy Index. For each candidate, apply in order: (1) Disconfirmation; (2) the one-problem-one-issue procedure (G3); (3) the Assessability lookup (G4/G5); (4) Severity and Confidence; (5) assemble the issue per G8.
- **Mode-agnostic discipline:** the staging above describes the two-pass runtime. In single-call execution the same discipline applies sequentially within one response: complete the full permissive detection sweep across ALL Traps first, then adjudicate the resulting candidates. Never filter, weigh disconfirmation, or assign severity during the detection sweep, in any mode.

**G3. One problem, one issue — evidenced diagnosis.** When multiple candidate flags point at the same underlying design element or decision, report ONE issue. **Atomicity (author-ruled 2026-07-05): the unit of an issue is the unit of independent action.** If a subset of the evidence can be fully resolved by a fix that leaves the rest intact, split it into its own issue and cross-reference the related issue(s) — duplicate controls inside a larger architectural problem are separate, precisely assignable issues. Merge only what one fix decision governs. At the bottom of each issue, list the Traps that align to it — each listed Trap independently evidenced. **Issue composition — four forms, decided top-down, stop at the first match (populate the tool's per-Trap `relationship` marker with the bracketed value):**
1. **Single** [none]: only one Trap genuinely applies. Show it; no relationship designation.
2. **Causal chain** [root_cause / consequence]: one Trap's presence produces the others, and its fix dissolves them (apply the discrimination test below). The root is the finding. Consequence Traps appear only within this issue's trap line, designated "(consequence)" — never as separate entries elsewhere and never as their own issues; where a consequence is condition-gated (e.g., repetition-dependent per C4), state the gate. The issue description states the cascade explicitly: what the root is, and which Trap(s) it leads to.
3. **Independent co-failures** [co-occurring]: two or more Traps each true on their own evidence, and no fix dissolves the others. Show all; designate EVERY listed Trap co-occurring — no unmarked primary; address the co-occurrence in the description. A downstream consequence is NEVER co-occurring.
4. **Conditional identity** [conditional — primary / conditional — enumerated]: competing descriptions of ONE failure, decided by a property the artifact cannot settle (audience, intent, context); only one is actually true. Report per the parsimony rule below: the single most applicable Trap [conditional — primary] plus the one-line other-Traps note; FULL enumeration [conditional — enumerated, one per branch] only when branches diverge on recommended fix or on severity — then each branch states, in the description prose, the specific condition under which its Trap applies. Reserve this form for a genuine either/or the artifact cannot resolve; never as a hedge to avoid committing to a finding (the anti-hedging edge in G8 applies).
**Composition conservatism:** prefer the smallest faithful set of Traps that preserves the evidence. A Trap surfaced within an issue never also appears as its own separate issue. **Related-Trap prose test (author-ruled 2026-07-05):** the description mentions a consequence, co-occurring, or conditional-alternative Trap ONLY when doing so (a) adds a consequence the primary diagnosis does not convey, (b) changes the fix's ordering or scope, or (c) is a conditional branch that would change fix or severity. Otherwise omit — the primary diagnosis carries the issue. The per-Trap `relationship` data is populated in full regardless of what the prose omits.

Then discriminate the relationship among the listed Traps before any designation:
- **Causal chain** — the listed Traps describe *different failures*, and a single design change at one of them dissolves the others. Only causal chains receive a root-cause designation. Ask whether one Trap is the root cause of the others (per the deck's How to Use, step 5); designate "(root cause)" and "(consequence)" where the evidence supports it. If the root cause is unclear, say so AND name the specific check that would settle it. Independent co-failures — multiple Traps on one element where no fix dissolves the others — get NO designation: co-occurrence without causation is neither a chain nor a conditional identity; list each with its own evidence.
- **Conditional identity** — the listed Traps are *competing descriptions of the same failure*, and which one applies depends on an unobservable user or context property (typically C1 prior experience or C3 context of use). NEVER designate a root cause among conditional alternatives — there is no chain, only alternative names for one defect. Report per the parsimony rule: name the single most applicable Trap — selected on provided C1/C3 where given, else on the declared defaults — and append one line: "Other Traps ([names]) may apply depending on [conditioning factor]." **Exceptions requiring full enumeration — branches diverge on recommended fix or on severity:** then present each branch with its Trap, fix, and severity, and name the check that settles which branch the users are on. If neither provided context nor the defaults discriminate between branches, state the tie explicitly — never select arbitrarily.

**G4. Absent vs. unassessable is a lookup, not a judgment — on two axes.** Before analysis: (a) classify the artifact type (static screenshot / disconnected screens / wired prototype or flow / live product / code); (b) inventory the user context provided against the Context Intake Schema. Consult each Trap's Assessability line on both axes. Three finding labels, never interchangeable: "Not assessable from this artifact — [what artifact would settle it]"; "Not assessable without user context — [what context field would settle it]"; "Not present" — requires that the artifact CAN show the Trap, required context is available or a declared default covers it, the Detection Procedure ran, and no candidate survived. Route by observability, grade by confirmability (author-ruled 2026-07-06): coverage is for what cannot be OBSERVED from the artifact; what is observed but cannot be CONFIRMED is a finding at reduced confidence with a named promotion path — never a coverage entry. A Trap whose Assessability declares the artifact class insufficient can never be cleared from that artifact class (author-ruled 2026-07-06); if a Trap's chunk is absent from adjudication context, default its coverage line to the not-assessable form, never to Not-present. Standing note, all visual artifacts: interaction-modality accessibility (keyboard and focus order, assistive-technology semantics) is largely not assessable — emit once per report: "Not assessable from this artifact — DOM/code artifacts or an assistive-technology session would settle."

**G5. Context softens or gates.** Where context sharpens calibration: assess anyway, label "Provisional — assumes [stated assumption]," name what would sharpen it. Where context gates assessment: do not guess — emit the "not assessable without user context" label, unless a default is declared for that field, in which case assess against the default and declare it.

**G6. Named evidence — symmetric.** Every flag, in either pass, must cite the specific cue(s)/element(s) and condition(s) that triggered it. General impressions are not findings. (Per the deck's How to Use, step 3: identify and log any Traps observed; note their severity; log all.) Clearances are held to the same bar: a "Not present" verdict must cite the specific disconfirming observation or the scope the procedure actually ran against, with the same specificity required of a finding — and must address the Trap's full definitional scope. Clearing one manifestation (one cue class, one screen region, one definitional clause) does not clear the Trap; state the scope actually cleared. A clearance without named evidence is not a clearance — emit the applicable not-assessable label from G4 instead. Per-instance enumeration (author-ruled 2026-07-06): any claim that an element, badge, or indicator is present on some parallel instances and absent on others must enumerate every instance with its observed state before the claim is made. Presence/absence patterns across repeated elements are the highest-risk observation class; unenumerated pattern claims are not findings.

**G7. Unit of analysis.** Detection Procedures declare their unit: per-screen, cross-screen, or both. For multi-screen artifacts: run per-screen steps on every screen in scope; run cross-screen steps where declared; a persistent element rendered across screens is ONE element. Every finding cites the screen(s) where its evidence sits.

**G8. Report architecture — issues first.** The evaluator's goal is to find and fix user-impacting issues; the Trap vocabulary rides on issues as diagnosis and shared team language. Reports have three sections:
1. **Issues.** One block per adjudicated issue: what is happening to the user and where (named cues/elements, plain language) → Severity (ladder + escalators) → Confidence (High / Medium / Low, with the promotion path when not High confidence) → the fix direction → closing trap line per G3. Order by severity, worst first.
2. **Worth a closer look.** Entries here are questions, not findings: elements whose bearing on the stated goals cannot be determined from the artifact or the provided context, but is pivotal if real. **Discriminator against Issues:** an Issue asserts a problem at some confidence — and High, Medium, and Low confidence are ALL Issue confidences; a Worth-a-closer-look entry asserts no problem — it names an assessability-blocked unknown and the check that settles it. Weak evidence never routes an entry here: a finding that clears its Trap's bar, even at Low confidence, is an Issue; a suspicion that clears no bar is dropped or recorded in Coverage notes — never parked here as a low-confidence copy. **Boundary against Coverage notes:** a Coverage note records status (assessed / not assessable) with no action expected; a Worth-a-closer-look entry demands one — the named check — because the unknown is pivotal. Trap-vs-no-trap routing (author-ruled 2026-07-06): when an unverifiable fact selects between a Trap and no-Trap — as opposed to between two Traps — the finding routes HERE with the verifying check, never to Issues as a conditional assertion.
   **Entry ticket — three gates, hard AND; failing any single gate keeps the entry out:**
   - *(a) The unknown is pivotal to a stated C2 goal.* Fails (a): an ambiguous cue on a path no stated goal passes through — curiosity, not pivotality; route to Coverage notes if not assessable, else drop.
   - *(b) The worst plausible branch clears Medium severity.* Fails (b): an unlabeled cue whose worst branch costs one wasted click — Low either way; drop.
   - *(c) A specific, nameable check exists.* Fails (c): "needs more research" or "unclear without testing" with no named check — unfinished adjudication, not an entry.
   **Entry format:** *cue/element and where — why it matters given the stated goal — the check, with its cost (e.g., one click in the live product; a task-based user test sized per the user-test sizing rule; a code audit) — the implication, compactly both ways.* Batch all checks into a closing verification checklist. A finding whose evidence clears its confidence bar MUST be an issue, not a bucket entry; an "I'm not sure" without a nameable check is unfinished adjudication — resolve it, drop it, or record it as a Coverage note, in that order of preference.
3. **Coverage notes.** Traps assessed and not present (with the condition that ruled them out), and Traps not assessable (with what would settle them). Exactly one line per Trap, from this fixed vocabulary, no elaboration: "Not present — procedure run against [scope], no triggering conditions" / "Not present — disconfirmed: [observation]" / "Not assessable from this artifact — [what would settle it]" / "Not assessable without user context — [field]" / "[Trap] — assessed within scope: [artifact-assessable sub-domains]; not assessable from this artifact: [inaccessible sub-domains] — [what would settle them]". The bracketed clause is the G6 evidence; it is mandatory and it is the whole sentence's budget. Trap accounting invariant (author-ruled 2026-07-06): every Trap in the taxonomy is accounted for exactly once per report — as an issue's primary, as a named secondary within an identified issue, or in exactly one coverage bucket; no Trap is ever silently absent. The report's Trap Disposition Index is rendered from this accounting. Scoped-coverage rule (J27): where a Trap's Assessability line declares artifact-inaccessible sub-domains, its scoped coverage line is ALWAYS emitted — including when the Trap also appears in Issues; an issue reports findings within the assessable scope and never implies the inaccessible scope was examined.

---

## SEVERITY & CONFIDENCE

**Severity ladder** — the worst plausible outcome for the stated goals (C2) under the stated context (C3), per affected user, three levels: **High** (task failure or abandonment with no discoverable recovery, or irreversible harm: data loss, unwanted disclosure, physical or safety harm, unrecoverable cost) / **Medium** (recoverable failure, or recurring friction) / **Low** (one-time friction, delay, polish).
**Severity asserts no prediction of occurrence.** It classifies the worst plausible outcome branch conditional on the Trap being real for an affected user. Likelihood is carried elsewhere by design: Confidence (is the Trap real), population conditioning (C1 — every finding names whom it is conditional on), the plausibility gate (evidence must make the branch live, per G6), and exposure (C4). Never write "likely" or any occurrence estimate into a severity rationale; reach is not estimated. Rubric phrasing ("High when users abandon") is a branch mapping in this conditional sense, not a prediction.
**Escalators:** Repetition (C4) — friction on a task performed daily escalates one level. Context (C3) — occupied channels, divided attention, motion, or time pressure can convert recoverable to unrecoverable in practice.
Reach is not estimated; findings are population-conditional via C1.

**Confidence scale** — how sure the analyzer is that the problem is real: **High confidence** (direct evidence in hand) / **Medium confidence** (risk conditions present, disconfirmation checked and cleared, confirming method not accessible from this artifact or context) / **Low confidence** (conditions partially present, or the judgment leans on a declared default). Each Trap's Assessability line sets the ceiling; every finding below High confidence names its promotion path and cost. Because severity and confidence share label words, prose always qualifies confidence values with the word "confidence"; the report's labeled fields disambiguate on screen.

**Calibration-gated ceilings.** Where a Trap's definitional threshold is a physical or absolute quantity (target size in millimeters, rendered text size, timing), that quantity is not derivable from a screenshot alone — rendered physical size depends on display hardware and resolution, which the pixels do not carry. Without calibration information (device class and resolution, or an in-artifact reference of known physical size), the ceiling is Medium confidence, promotion path "measure on the target device against [threshold]." High confidence requires stated calibration or on-device measurement. Ratios computable from pixels alone (e.g., contrast ratio) are exempt. Clearances gate identically (G6): "exceeds the minimum" is not observable from an uncalibrated artifact either.

**User-test sizing (promotion paths and remediation checks).** Never recommend a fixed participant count as a rule of thumb. Standard report wording: "Verify with a user test sized to the expected frequency of the problem — common problems need few participants; rare or severe ones need more." Mechanism, so the wording is applied correctly: severity raises the confidence bar to demand before declaring the problem absent; the confidence bar and the expected per-participant discovery rate together set the participant count. A specific count may be stated only when the assumed discovery rate is stated alongside it.

---

## CONTEXT INTAKE SCHEMA (C1–C4)

**C1. User Knowledge.** Products and conventions the users have already internalized; domain expertise; novice/expert mix; prior exposure to this product's conventions. ONE sub-population per evaluation (J26): C1 names a single population; evaluating multiple segments means running multiple evaluations. If a mixed population is provided anyway, analyze against the FIRST-NAMED segment and emit one prominent Coverage line: \"Context named multiple populations; this analysis is conditioned on [first-named]. Run a separate evaluation for [others].\" *Default when absent:* general adult population familiar with mainstream web/mobile conventions — declare it. Brand-specific, domain-insider, and novel cues cannot be cleared under the default.

**C2. Goals.** The user's primary tasks and critical paths — AND the fuller set of goals users might plausibly bring to each screen. *Default when absent:* infer the apparent primary task from the screen itself and declare it; findings requiring the full goal set are degraded under this default.

**C3. Context of Use.** Availability of the user's channels and circumstances: attention (focused / divided / interrupted); vision (available / occupied); hearing (quiet / noisy); speech & audio-out (free / constrained by others or privacy); hands (both free / one / none); mobility (stationary / in motion); plus lighting, time pressure, device and input method. *Default when absent:* attentive, stationary, unencumbered, quiet, private use — the most forgiving context on every channel. Declare it, and state that findings under this default are a lower bound.

**C4. Exposure & Repetition.** User exposure stage (first-run / habituated / mixed) and task repetition profile (once / a few times / recurring). Habituating-tenet Traps scale with repetition; one-time tasks make comprehension Traps paramount. *Defaults when absent:* mixed exposure including first-time users for public-facing products; infer the task's repetition profile from its nature — declare both.

---

## TAXONOMY INDEX (26 Traps by Tenet — card definitions verbatim)

**UNDERSTANDABLE**
- **Invisible Element** (card 1) — No cue (label, icon, affordance, or prompt) is provided to signal to the user how to achieve a goal, and the user has insufficient prior learning to overcome its absence.
- **Effectively Invisible Element** (card 2) — A provided cue (label, icon, affordance, or prompt) is not noticed, or is slow to be noticed, because its appearance or location differs from what the user expects.
- **Distraction** (card 3) — Something in the UI suddenly appears or otherwise draws the user's attention, distracting them from their goal.
- **Uncomprehended Element** (card 4) — A cue (label, icon, affordance, or prompt) critical to achieving a goal is noticed, but its meaning, or the required method of interacting with it, is unclear.
- **Inviting Dead End** (card 5) — A cue (label, icon, affordance, or prompt) is incorrectly judged as a means for achieving a goal. It looks right, but is wrong.
- **Poor Grouping** (card 6) — A critical relationship between two or more otherwise noticeable cues (labels, icons, affordances, or prompts) is not obvious.
- **Forced Syntax** (card 7) — The system does not allow the user to issue a command or complete a sequence of actions in the order or manner that is most natural to them.
- **Memory Challenge** (card 8) — The system requires the user to remember information that is easy to forget.
- **Feedback Failure** (card 9) — The system fails to provide noticeable, comprehensible, and actionable feedback in response to user actions.

**COMFORTABLE**
- **Physical Challenge** (card 10) — An action the system requires the user to perform is physically effortful, difficult, or impossible.
- **Accidental Activation** (card 11) — The system misinterprets a user's physical actions resulting in an unintended outcome.

**RESPONSIVE**
- **Slow or No Response** (card 12) — The user is prevented from achieving a goal in a timely manner because of actual or perceived poor system performance.
- **Captive Wait** (card 13) — The user is prevented from achieving a goal in a timely manner because the system intentionally prevents them from advancing and/or backing out of a process.

**EFFICIENT**
- **Unnecessary Step** (card 14) — When the product is being used as intended, the number of actual or perceived steps required to achieve a goal is too high.
- **System Amnesia** (card 15) — The system re-prompts the user for information it previously gathered, or otherwise fails to leverage the user's prior work.
- **Information Overload** (card 16) — Information presented to the user is comprehensible, but there is too much of it.
- **Bad Prediction** (card 17) — The system incorrectly predicts or interprets the user's intent or preference, resulting in the user having to work around the problem.

**FORGIVING**
- **Irreversible Action** (card 18) — The system does not allow the user to undo an action they have taken.

**DISCREET**
- **Unwanted Disclosure** (card 19) — The system makes the user's data or behavior public in a way that is harmful or embarrassing to the user.

**PROTECTIVE**
- **Data Loss** (card 20) — The system can lose the user's work through some action or inaction on the user's part.

**HABITUATING**
- **Gratuitous Redundancy** (card 21) — The system presents duplicate cues (labels, icons, affordances, or prompts) for the same action on the same level, or a directly nested level of the UI.
- **Variable Outcome** (card 22) — The system responds differently at different times to the same user action.
- **Wandering Element** (card 23) — The physical location of a cue (label, icon, affordance, or prompt) for a given action varies across the UI.
- **Inconsistent Appearance** (card 24) — The visual appearance of a cue (label, icon, affordance, or prompt) for a given action varies across the UI.
- **Ambiguous Home** (card 25) — The UI provides no single place the user can return to at any time to begin a new task or get re-oriented.

**BEAUTIFUL**
- **Unattractive Appearance** (card 26) — The UI is aesthetically unpleasing, inconsistent, and/or inappropriate for its intended users.

---

## TRAP CHUNKS

### TRAP: INVISIBLE ELEMENT *(card 1 — mechanically templated from card content)*
*Tenet: Understandable*

**Definition (card, verbatim).** No cue (label, icon, affordance, or prompt) is provided to signal to the user how to achieve a goal, and the user has insufficient prior learning to overcome its absence.

**Definitional conditions (decomposed from the definition sentence; the Trap requires all):** (a) no cue signals how to achieve a goal the user plausibly holds (C2); (b) the user population lacks sufficient prior learning to overcome the absence (C1).

**Detection procedure (pass one — flag, do not filter).** *Unit: per-screen, against the goal set.*
1. From the C2 goal set, survey the artifact for the definitional conditions above.
2. Flag every candidate where the conditions appear present; name the specific cue(s)/element(s) and the condition(s) observed (G6).
3. Where a condition cannot be evaluated from this artifact or without a context field, record that as the reason per G4 rather than silently skipping.

**Disconfirmation (pass two).** The Trap requires ALL definitional conditions; NOT present when condition (a) fails — verify each independently. NOT present when condition (b) fails — verify each independently. No further disconfirmation content exists in this source.

**Severity.** Place on the ladder by the worst plausible outcome for the stated goals; apply C3/C4 escalators. No Trap-specific severity anchors exist in this source.

**Assessability & Confidence.** user-context gated: condition (b) cannot be cleared without C1; under the C1 default only widely learned interactions can be cleared.

**Attribution.** Apply G3. No Trap-specific attribution rules exist in this source.

**Report fragments.** Finding: "[cue/element(s)] on [screen]: [definitional condition(s) observed, with named evidence]." Why it matters: "This degrades Understandable: the conditions above prevent or burden progress toward the user’s goal."

**Card example (the source's single anchor).** In 2012 Microsoft released Windows 8. Unlike previous versions, Windows 8 removed a visible means to launch the Start Menu. The resulting user confusion led to the Start button's return in the next version of Windows.

**Remediation.** No remediation guidance exists in this source beyond the example above. Direction derivable from the definition: remove or negate the definitional condition(s). Do not fabricate technique-level guidance the source does not contain.

---

### TRAP: EFFECTIVELY INVISIBLE ELEMENT *(card 2 — mechanically templated from card content)*
*Tenet: Understandable*

**Definition (card, verbatim).** A provided cue (label, icon, affordance, or prompt) is not noticed, or is slow to be noticed, because its appearance or location differs from what the user expects.

**Definitional conditions (decomposed from the definition sentence; the Trap requires all):** (a) a cue is provided; (b) it is likely to go unnoticed or be slow to be noticed; (c) because its appearance or location differs from what the user expects (C1/C2).

**Detection procedure (pass one — flag, do not filter).** *Unit: per-screen.*
1. From the C2 goal set, survey the artifact for the definitional conditions above.
2. Flag every candidate where the conditions appear present; name the specific cue(s)/element(s) and the condition(s) observed (G6).
3. Where a condition cannot be evaluated from this artifact or without a context field, record that as the reason per G4 rather than silently skipping.

**Disconfirmation (pass two).** The Trap requires ALL definitional conditions; NOT present when condition (a) fails — verify each independently. NOT present when condition (b) fails — verify each independently. NOT present when condition (c) fails — verify each independently. No further disconfirmation content exists in this source.

**Severity.** Place on the ladder by the worst plausible outcome for the stated goals; apply C3/C4 escalators. No Trap-specific severity anchors exist in this source.

**Assessability & Confidence.** user-context gated: expectation (appearance/location) derives from C1 prior learning and C2 task focus; ceiling Medium confidence from statics.

**Attribution.** Apply G3. No Trap-specific attribution rules exist in this source.

**Report fragments.** Finding: "[cue/element(s)] on [screen]: [definitional condition(s) observed, with named evidence]." Why it matters: "This degrades Understandable: the conditions above prevent or burden progress toward the user’s goal."

**Card example (the source's single anchor).** In a past version of the Xbox 360 interface, the global search function was placed on the controller's Y button. This was indicated in a corner of the interface, but was effectively invisible to users, whose focus was on the tiles. A subsequent addition of a search tile solved the problem.

**Remediation.** No remediation guidance exists in this source beyond the example above. Direction derivable from the definition: remove or negate the definitional condition(s). Do not fabricate technique-level guidance the source does not contain.

---

### TRAP: DISTRACTION *(card 3 — mechanically templated from card content)*
*Tenet: Understandable*

**Definition (card, verbatim).** Something in the UI suddenly appears or otherwise draws the user's attention, distracting them from their goal.

**Definitional conditions (decomposed from the definition sentence; the Trap requires all):** (a) something in the UI suddenly appears or otherwise draws attention; (b) it distracts the user from their goal (C2).

**Detection procedure (pass one — flag, do not filter).** *Unit: per-screen; appearing elements need flow/live evidence.*
1. From the C2 goal set, survey the artifact for the definitional conditions above.
2. Flag every candidate where the conditions appear present; name the specific cue(s)/element(s) and the condition(s) observed (G6).
3. Where a condition cannot be evaluated from this artifact or without a context field, record that as the reason per G4 rather than silently skipping.

**Disconfirmation (pass two).** The Trap requires ALL definitional conditions; NOT present when condition (a) fails — verify each independently. NOT present when condition (b) fails — verify each independently. No further disconfirmation content exists in this source.

**Severity.** Place on the ladder by the worst plausible outcome for the stated goals; apply C3/C4 escalators. No Trap-specific severity anchors exist in this source.

**Assessability & Confidence.** goal-gated (C2); sudden-appearance behavior is not assessable from a single static — declare.

**Attribution.** Apply G3. No Trap-specific attribution rules exist in this source.

**Report fragments.** Finding: "[cue/element(s)] on [screen]: [definitional condition(s) observed, with named evidence]." Why it matters: "This degrades Understandable: the conditions above prevent or burden progress toward the user’s goal."

**Card example (the source's single anchor).** The iPhone news reader notifications can pop up over the top of the GPS mapping application when the user is driving. This obscures the driving directions.

**Remediation.** No remediation guidance exists in this source beyond the example above. Direction derivable from the definition: remove or negate the definitional condition(s). Do not fabricate technique-level guidance the source does not contain.

---

### TRAP: UNCOMPREHENDED ELEMENT *(card 4 — mechanically templated from card content)*
*Tenet: Understandable*

**Definition (card, verbatim).** A cue (label, icon, affordance, or prompt) critical to achieving a goal is noticed, but its meaning, or the required method of interacting with it, is unclear.

**Definitional conditions (decomposed from the definition sentence; the Trap requires all):** (a) the cue is critical to achieving a goal (C2); (b) it is noticed; (c) its meaning or required interaction method is unclear to the population (C1).

**Detection procedure (pass one — flag, do not filter).** *Unit: per-screen.*
1. From the C2 goal set, survey the artifact for the definitional conditions above.
2. Flag every candidate where the conditions appear present; name the specific cue(s)/element(s) and the condition(s) observed (G6).
3. Where a condition cannot be evaluated from this artifact or without a context field, record that as the reason per G4 rather than silently skipping.

**Disconfirmation (pass two).** The Trap requires ALL definitional conditions; NOT present when condition (a) fails — verify each independently. NOT present when condition (b) fails — verify each independently. NOT present when condition (c) fails — verify each independently. No further disconfirmation content exists in this source.

**Severity.** Place on the ladder by the worst plausible outcome for the stated goals; apply C3/C4 escalators. No Trap-specific severity anchors exist in this source.

**Assessability & Confidence.** user-context gated: clarity is population-relative (C1); under the C1 default only widely recognized cues can be cleared.

**Attribution.** Apply G3. No Trap-specific attribution rules exist in this source.

**Report fragments.** Finding: "[cue/element(s)] on [screen]: [definitional condition(s) observed, with named evidence]." Why it matters: "This degrades Understandable: the conditions above prevent or burden progress toward the user’s goal."

**Card example (the source's single anchor).** In 2016 Waze changed their search icon from a silhouette of their logo to the very familiar and readily comprehended magnifying glass search icon.

**Remediation.** No remediation guidance exists in this source beyond the example above. Direction derivable from the definition: remove or negate the definitional condition(s). Do not fabricate technique-level guidance the source does not contain.

---

### TRAP: INVITING DEAD END *(card 5 — mechanically templated from card content)*
*Tenet: Understandable*

**Definition (card, verbatim).** A cue (label, icon, affordance, or prompt) is incorrectly judged as a means for achieving a goal. It looks right, but is wrong.

**Definitional conditions (decomposed from the definition sentence; the Trap requires all):** (a) a cue is likely to be judged a means to a goal the user plausibly holds (C2); (b) it is in fact wrong for that goal.

**Detection procedure (pass one — flag, do not filter).** *Unit: per-screen for candidates; destination verification needs flows/live/code.*
1. From the C2 goal set, survey the artifact for the definitional conditions above.
2. Flag every candidate where the conditions appear present; name the specific cue(s)/element(s) and the condition(s) observed (G6).
3. Where a condition cannot be evaluated from this artifact or without a context field, record that as the reason per G4 rather than silently skipping.

**Disconfirmation (pass two).** The Trap requires ALL definitional conditions; NOT present when condition (a) fails — verify each independently. NOT present when condition (b) fails — verify each independently. No further disconfirmation content exists in this source.

**Severity.** Place on the ladder by the worst plausible outcome for the stated goals; apply C3/C4 escalators. No Trap-specific severity anchors exist in this source.

**Assessability & Confidence.** wrongness is verifiable where the artifact shows destinations/outcomes (High confidence); plausibility of the wrong judgment is C1/C2-gated.

**Attribution.** Apply G3. No Trap-specific attribution rules exist in this source.

**Report fragments.** Finding: "[cue/element(s)] on [screen]: [definitional condition(s) observed, with named evidence]." Why it matters: "This degrades Understandable: the conditions above prevent or burden progress toward the user’s goal."

**Card example (the source's single anchor).** On the original iPhone, users would get drawn into the iTunes app instead of the iPod app due to the design of the icon. Subsequent changes to the iPod (music) icon have not mitigated this problem.

**Remediation.** No remediation guidance exists in this source beyond the example above. Direction derivable from the definition: remove or negate the definitional condition(s). Do not fabricate technique-level guidance the source does not contain.

---

### TRAP: POOR GROUPING *(card 6 — mechanically templated from card content)*
*Tenet: Understandable*

**Definition (card, verbatim).** A critical relationship between two or more otherwise noticeable cues (labels, icons, affordances, or prompts) is not obvious.

**Definitional conditions (decomposed from the definition sentence; the Trap requires all):** (a) two or more noticeable cues bear a relationship; (b) the relationship is critical to a goal (C2); (c) the relationship is not obvious.

**Detection procedure (pass one — flag, do not filter).** *Unit: per-screen.*
1. From the C2 goal set, survey the artifact for the definitional conditions above.
2. Flag every candidate where the conditions appear present; name the specific cue(s)/element(s) and the condition(s) observed (G6).
3. Where a condition cannot be evaluated from this artifact or without a context field, record that as the reason per G4 rather than silently skipping.

**Disconfirmation (pass two).** The Trap requires ALL definitional conditions; NOT present when condition (a) fails — verify each independently. NOT present when condition (b) fails — verify each independently. NOT present when condition (c) fails — verify each independently. No further disconfirmation content exists in this source.

**Severity.** Place on the ladder by the worst plausible outcome for the stated goals; apply C3/C4 escalators. No Trap-specific severity anchors exist in this source.

**Assessability & Confidence.** spatial evidence is artifact-native; whether the relationship reads as non-obvious to the population is C1-softened.

**Attribution.** Apply G3. No Trap-specific attribution rules exist in this source.

**Report fragments.** Finding: "[cue/element(s)] on [screen]: [definitional condition(s) observed, with named evidence]." Why it matters: "This degrades Understandable: the conditions above prevent or burden progress toward the user’s goal."

**Card example (the source's single anchor).** In the 2000 presidential election, 4,000 people made the error of punching the second hole on the butterfly ballot in the mistaken belief that the second hole represented the second candidate, while 19,000 people punched more than one hole. This Trap changed the outcome of the election.

**Remediation.** No remediation guidance exists in this source beyond the example above. Direction derivable from the definition: remove or negate the definitional condition(s). Do not fabricate technique-level guidance the source does not contain.

---

### TRAP: FORCED SYNTAX *(card 7 — mechanically templated from card content)*
*Tenet: Understandable*

**Definition (card, verbatim).** The system does not allow the user to issue a command or complete a sequence of actions in the order or manner that is most natural to them.

**Definitional conditions (decomposed from the definition sentence; the Trap requires all):** (a) a command or action sequence exists for a goal; (b) the order or manner most natural to the user (C1) is not allowed by the system.

**Detection procedure (pass one — flag, do not filter).** *Unit: cross-screen/flow by nature; statics show risk only.*
1. From the C2 goal set, survey the artifact for the definitional conditions above.
2. Flag every candidate where the conditions appear present; name the specific cue(s)/element(s) and the condition(s) observed (G6).
3. Where a condition cannot be evaluated from this artifact or without a context field, record that as the reason per G4 rather than silently skipping.

**Disconfirmation (pass two).** The Trap requires ALL definitional conditions; NOT present when condition (a) fails — verify each independently. NOT present when condition (b) fails — verify each independently. No further disconfirmation content exists in this source.

**Severity.** Place on the ladder by the worst plausible outcome for the stated goals; apply C3/C4 escalators. No Trap-specific severity anchors exist in this source.

**Assessability & Confidence.** what is 'most natural' is C1-gated; which orders the system allows requires flow, live, or code evidence — declare on statics.

**Attribution.** Apply G3. No Trap-specific attribution rules exist in this source.

**Report fragments.** Finding: "[cue/element(s)] on [screen]: [definitional condition(s) observed, with named evidence]." Why it matters: "This degrades Understandable: the conditions above prevent or burden progress toward the user’s goal."

**Card example (the source's single anchor).** When talking to voice-driven devices like those powered by Amazon's Alexa, users must first address the device and then say their command. But this isn't always how humans formulate sentences. "Alexa, what time is it?" works, but "What time is it, Alexa?", doesn't.

**Remediation.** No remediation guidance exists in this source beyond the example above. Direction derivable from the definition: remove or negate the definitional condition(s). Do not fabricate technique-level guidance the source does not contain.

---

### TRAP: MEMORY CHALLENGE *(card 8 — mechanically templated from card content)*
*Tenet: Understandable*

**Definition (card, verbatim).** The system requires the user to remember information that is easy to forget.

**Definitional conditions (decomposed from the definition sentence; the Trap requires all):** (a) the system requires the user to remember information; (b) that information is easy to forget.

**Detection procedure (pass one — flag, do not filter).** *Unit: cross-screen (carries) and per-screen (recall demands).*
1. From the C2 goal set, survey the artifact for the definitional conditions above.
2. Flag every candidate where the conditions appear present; name the specific cue(s)/element(s) and the condition(s) observed (G6).
3. Where a condition cannot be evaluated from this artifact or without a context field, record that as the reason per G4 rather than silently skipping.

**Disconfirmation (pass two).** The Trap requires ALL definitional conditions; NOT present when condition (a) fails — verify each independently. NOT present when condition (b) fails — verify each independently. No further disconfirmation content exists in this source.

**Severity.** Place on the ladder by the worst plausible outcome for the stated goals; apply C3/C4 escalators. No Trap-specific severity anchors exist in this source.

**Assessability & Confidence.** the recall demand is often artifact-visible; whether the information is easy to forget is C1/C4-softened.

**Attribution.** Apply G3. No Trap-specific attribution rules exist in this source.

**Report fragments.** Finding: "[cue/element(s)] on [screen]: [definitional condition(s) observed, with named evidence]." Why it matters: "This degrades Understandable: the conditions above prevent or burden progress toward the user’s goal."

**Card example (the source's single anchor).** Efforts to make systems secure often make them impossible to use. In this example, American Express required users to remember not only the answer to their security question, but also the security question itself.

**Remediation.** No remediation guidance exists in this source beyond the example above. Direction derivable from the definition: remove or negate the definitional condition(s). Do not fabricate technique-level guidance the source does not contain.

---

### TRAP: FEEDBACK FAILURE *(card 9 — mechanically templated from card content)*
*Tenet: Understandable*

**Definition (card, verbatim).** The system fails to provide noticeable, comprehensible, and actionable feedback in response to user actions.

**Definitional conditions (decomposed from the definition sentence; the Trap requires all):** (a) a user action occurs; (b) the feedback in response is not noticeable, or not comprehensible, or not actionable.

**Detection procedure (pass one — flag, do not filter).** *Unit: cross-screen: audit action→response pairs; visible messages auditable per-screen.*
1. From the C2 goal set, survey the artifact for the definitional conditions above.
2. Flag every candidate where the conditions appear present; name the specific cue(s)/element(s) and the condition(s) observed (G6).
3. Where a condition cannot be evaluated from this artifact or without a context field, record that as the reason per G4 rather than silently skipping.

**Disconfirmation (pass two).** The Trap requires ALL definitional conditions; NOT present when condition (a) fails — verify each independently. NOT present when condition (b) fails — verify each independently. No further disconfirmation content exists in this source.

**Severity.** Place on the ladder by the worst plausible outcome for the stated goals; apply C3/C4 escalators. No Trap-specific severity anchors exist in this source.

**Assessability & Confidence.** visible feedback text is auditable from the artifact; responses to actions require flow/live evidence — declare on statics.

**Attribution.** Apply G3. No Trap-specific attribution rules exist in this source.

**Report fragments.** Finding: "[cue/element(s)] on [screen]: [definitional condition(s) observed, with named evidence]." Why it matters: "This degrades Understandable: the conditions above prevent or burden progress toward the user’s goal."

**Card example (the source's single anchor).** Sooner or later everyone encounters an error. The hope is that the error will help guide the user to a solution. In this example, the feedback message fails on this count. (Microsoft Word: "Word did not save the document.")

**Remediation.** No remediation guidance exists in this source beyond the example above. Direction derivable from the definition: remove or negate the definitional condition(s). Do not fabricate technique-level guidance the source does not contain.

---

### TRAP: PHYSICAL CHALLENGE *(card 10 — mechanically templated from card content)*
*Tenet: Comfortable*

**Definition (card, verbatim).** An action the system requires the user to perform is physically effortful, difficult, or impossible.

**Definitional conditions (decomposed from the definition sentence; the Trap requires all):** (a) the system requires a physical action; (b) that action is physically effortful, difficult, or impossible for the population (C1) in the context (C3).

**Detection procedure (pass one — flag, do not filter).** *Unit: per-screen for visible physical demands.*
1. From the C2 goal set, survey the artifact for the definitional conditions above.
2. Flag every candidate where the conditions appear present; name the specific cue(s)/element(s) and the condition(s) observed (G6).
3. Where a condition cannot be evaluated from this artifact or without a context field, record that as the reason per G4 rather than silently skipping.

**Disconfirmation (pass two).** The Trap requires ALL definitional conditions; NOT present when condition (a) fails — verify each independently. NOT present when condition (b) fails — verify each independently. No further disconfirmation content exists in this source.

**Severity.** Place on the ladder by the worst plausible outcome for the stated goals; apply C3/C4 escalators. No Trap-specific severity anchors exist in this source.

**Assessability & Confidence.** Contrast ratio is pixel-derivable and eligible for High confidence from the artifact alone. Target size, spacing, and rendered text size are physical quantities: High confidence only with calibration (device class and resolution, or an in-artifact reference of known physical size); on uncalibrated artifacts the ceiling is Medium confidence, promotion path "measure on the target device against the applicable standard for the asserted input modality" — per the calibration-gated ceilings rule, and symmetrically for clearances (an uncalibrated artifact can neither confirm nor clear a size threshold). Other physical properties are not assessable from the artifact — declare.

**Attribution.** Apply G3. No Trap-specific attribution rules exist in this source.

**Report fragments.** Finding: "[cue/element(s)] on [screen]: [definitional condition(s) observed, with named evidence]." Why it matters: "This degrades Comfortable: the conditions above prevent or burden progress toward the user’s goal."

**Card example (the source's single anchor).** Human finger pads are about 12 mm across on average. Not all touch controls adhere to that norm, including the version of the iPhone lock screen music controls shown above. These were difficult for users to target and were ultimately enlarged.

**Remediation.** No remediation guidance exists in this source beyond the example above. Direction derivable from the definition: remove or negate the definitional condition(s). Do not fabricate technique-level guidance the source does not contain.

---

### TRAP: ACCIDENTAL ACTIVATION *(card 11 — mechanically templated from card content)*
*Tenet: Comfortable*

**Definition (card, verbatim).** The system misinterprets a user's physical actions resulting in an unintended outcome.

**Definitional conditions (decomposed from the definition sentence; the Trap requires all):** (a) the user takes a physical action; (b) the system misinterprets it; (c) an unintended outcome results.

**Detection procedure (pass one — flag, do not filter).** *Unit: whole-artifact; behavior evidence needed.*
1. From the C2 goal set, survey the artifact for the definitional conditions above.
2. Flag every candidate where the conditions appear present; name the specific cue(s)/element(s) and the condition(s) observed (G6).
3. Where a condition cannot be evaluated from this artifact or without a context field, record that as the reason per G4 rather than silently skipping.

**Disconfirmation (pass two).** The Trap requires ALL definitional conditions; NOT present when condition (a) fails — verify each independently. NOT present when condition (b) fails — verify each independently. NOT present when condition (c) fails — verify each independently. No further disconfirmation content exists in this source.

**Severity.** Place on the ladder by the worst plausible outcome for the stated goals; apply C3/C4 escalators. No Trap-specific severity anchors exist in this source.

**Assessability & Confidence.** misinterpretation is behavior — not assessable from statics; flag risk conditions only and declare.

**Attribution.** Apply G3. No Trap-specific attribution rules exist in this source.

**Report fragments.** Finding: "[cue/element(s)] on [screen]: [definitional condition(s) observed, with named evidence]." Why it matters: "This degrades Comfortable: the conditions above prevent or burden progress toward the user’s goal."

**Card example (the source's single anchor).** With gesture based systems like Kinect, it is often difficult to determine the user's intent: Is a hand gesture a navigational swipe or an effort to scratch one's ear? This makes scrolling via hand gestures prone to accidental activations.

**Remediation.** No remediation guidance exists in this source beyond the example above. Direction derivable from the definition: remove or negate the definitional condition(s). Do not fabricate technique-level guidance the source does not contain.

---

### TRAP: SLOW OR NO RESPONSE *(card 12 — mechanically templated from card content)*
*Tenet: Responsive*

**Definition (card, verbatim).** The user is prevented from achieving a goal in a timely manner because of actual or perceived poor system performance.

**Definitional conditions (decomposed from the definition sentence; the Trap requires all):** (a) the user pursues a goal (C2); (b) actual or perceived system performance prevents timely achievement.

**Detection procedure (pass one — flag, do not filter).** *Unit: per-interaction; live/measured artifacts.*
1. From the C2 goal set, survey the artifact for the definitional conditions above.
2. Flag every candidate where the conditions appear present; name the specific cue(s)/element(s) and the condition(s) observed (G6).
3. Where a condition cannot be evaluated from this artifact or without a context field, record that as the reason per G4 rather than silently skipping.

**Disconfirmation (pass two).** The Trap requires ALL definitional conditions; NOT present when condition (a) fails — verify each independently. NOT present when condition (b) fails — verify each independently. No further disconfirmation content exists in this source.

**Severity.** Place on the ladder by the worst plausible outcome for the stated goals; apply C3/C4 escalators. No Trap-specific severity anchors exist in this source.

**Assessability & Confidence.** performance is not assessable from static artifacts — declare; live/measured evidence can Confirm.

**Attribution.** Apply G3. No Trap-specific attribution rules exist in this source.

**Report fragments.** Finding: "[cue/element(s)] on [screen]: [definitional condition(s) observed, with named evidence]." Why it matters: "This degrades Responsive: the conditions above prevent or burden progress toward the user’s goal."

**Card example (the source's single anchor).** After pressing the button to activate the Super-Bright LED Flashlight application on an Android phone, it can take up to 5 seconds for the light to actually turn on.

**Remediation.** No remediation guidance exists in this source beyond the example above. Direction derivable from the definition: remove or negate the definitional condition(s). Do not fabricate technique-level guidance the source does not contain.

---

### TRAP: CAPTIVE WAIT *(card 13 — mechanically templated from card content)*
*Tenet: Responsive*

**Definition (card, verbatim).** The user is prevented from achieving a goal in a timely manner because the system intentionally prevents them from advancing and/or backing out of a process.

**Definitional conditions (decomposed from the definition sentence; the Trap requires all):** (a) the user is in a process toward a goal (C2); (b) the system intentionally prevents advancing and/or backing out; (c) timely achievement is prevented.

**Detection procedure (pass one — flag, do not filter).** *Unit: cross-screen (flow states).*
1. From the C2 goal set, survey the artifact for the definitional conditions above.
2. Flag every candidate where the conditions appear present; name the specific cue(s)/element(s) and the condition(s) observed (G6).
3. Where a condition cannot be evaluated from this artifact or without a context field, record that as the reason per G4 rather than silently skipping.

**Disconfirmation (pass two).** The Trap requires ALL definitional conditions; NOT present when condition (a) fails — verify each independently. NOT present when condition (b) fails — verify each independently. NOT present when condition (c) fails — verify each independently. No further disconfirmation content exists in this source.

**Severity.** Place on the ladder by the worst plausible outcome for the stated goals; apply C3/C4 escalators. No Trap-specific severity anchors exist in this source.

**Assessability & Confidence.** locked states are flow/live/code-assessable; a single static shows at most a missing visible skip/back affordance — declare the limit.

**Attribution.** Apply G3. No Trap-specific attribution rules exist in this source.

**Report fragments.** Finding: "[cue/element(s)] on [screen]: [definitional condition(s) observed, with named evidence]." Why it matters: "This degrades Responsive: the conditions above prevent or burden progress toward the user’s goal."

**Card example (the source's single anchor).** YouTube often presents users with advertisements without providing a means of advancing to the content they are actually interested in.

**Remediation.** No remediation guidance exists in this source beyond the example above. Direction derivable from the definition: remove or negate the definitional condition(s). Do not fabricate technique-level guidance the source does not contain.

---

### TRAP: UNNECESSARY STEP *(card 14 — mechanically templated from card content)*
*Tenet: Efficient*

**Definition (card, verbatim).** When the product is being used as intended, the number of actual or perceived steps required to achieve a goal is too high.

**Definitional conditions (decomposed from the definition sentence; the Trap requires all):** (a) the product is used as intended; (b) actual or perceived steps to a goal (C2) exceed what is needed.

**Detection procedure (pass one — flag, do not filter).** *Unit: cross-screen (flows); statics show risk only.*
1. From the C2 goal set, survey the artifact for the definitional conditions above.
2. Flag every candidate where the conditions appear present; name the specific cue(s)/element(s) and the condition(s) observed (G6).
3. Where a condition cannot be evaluated from this artifact or without a context field, record that as the reason per G4 rather than silently skipping.

**Disconfirmation (pass two).** The Trap requires ALL definitional conditions; NOT present when condition (a) fails — verify each independently. NOT present when condition (b) fails — verify each independently. No further disconfirmation content exists in this source.

**Severity.** Place on the ladder by the worst plausible outcome for the stated goals; apply C3/C4 escalators. No Trap-specific severity anchors exist in this source.

**Assessability & Confidence.** step counts need flow evidence; whether steps are 'too high' is C2-gated — declare on statics.

**Attribution.** Apply G3. No Trap-specific attribution rules exist in this source.

**Report fragments.** Finding: "[cue/element(s)] on [screen]: [definitional condition(s) observed, with named evidence]." Why it matters: "This degrades Efficient: the conditions above prevent or burden progress toward the user’s goal."

**Card example (the source's single anchor).** The hamburger menu has become ubiquitous with early mobile design. But companies have discovered that removing it and flattening the hierarchy can increase the efficiency of their UIs. Spotify is a notable example of a company that ditched the hamburger.

**Remediation.** No remediation guidance exists in this source beyond the example above. Direction derivable from the definition: remove or negate the definitional condition(s). Do not fabricate technique-level guidance the source does not contain.

---

### TRAP: SYSTEM AMNESIA *(card 15 — mechanically templated from card content)*
*Tenet: Efficient*

**Definition (card, verbatim).** The system re-prompts the user for information it previously gathered, or otherwise fails to leverage the user's prior work.

**Definitional conditions (decomposed from the definition sentence; the Trap requires all):** (a) the system previously gathered information or prior work exists; (b) the system re-prompts for it or fails to leverage it.

**Detection procedure (pass one — flag, do not filter).** *Unit: cross-screen/cross-session.*
1. From the C2 goal set, survey the artifact for the definitional conditions above.
2. Flag every candidate where the conditions appear present; name the specific cue(s)/element(s) and the condition(s) observed (G6).
3. Where a condition cannot be evaluated from this artifact or without a context field, record that as the reason per G4 rather than silently skipping.

**Disconfirmation (pass two).** The Trap requires ALL definitional conditions; NOT present when condition (a) fails — verify each independently. NOT present when condition (b) fails — verify each independently. No further disconfirmation content exists in this source.

**Severity.** Place on the ladder by the worst plausible outcome for the stated goals; apply C3/C4 escalators. No Trap-specific severity anchors exist in this source.

**Assessability & Confidence.** requires evidence of what was previously gathered — flow, session, or in-artifact display; declare when absent.

**Attribution.** Apply G3. No Trap-specific attribution rules exist in this source.

**Report fragments.** Finding: "[cue/element(s)] on [screen]: [definitional condition(s) observed, with named evidence]." Why it matters: "This degrades Efficient: the conditions above prevent or burden progress toward the user’s goal."

**Card example (the source's single anchor).** This version of the Xbox website uses valuable space to sell the user Halo… even though it clearly displays that the user already owns it.

**Remediation.** No remediation guidance exists in this source beyond the example above. Direction derivable from the definition: remove or negate the definitional condition(s). Do not fabricate technique-level guidance the source does not contain.

---

### TRAP: INFORMATION OVERLOAD *(card 16 — mechanically templated from card content)*
*Tenet: Efficient*

**Definition (card, verbatim).** Information presented to the user is comprehensible, but there is too much of it.

**Definitional conditions (decomposed from the definition sentence; the Trap requires all):** (a) information presented is comprehensible; (b) there is more of it than the goal (C2) requires.

**Detection procedure (pass one — flag, do not filter).** *Unit: per-screen.*
1. From the C2 goal set, survey the artifact for the definitional conditions above.
2. Flag every candidate where the conditions appear present; name the specific cue(s)/element(s) and the condition(s) observed (G6).
3. Where a condition cannot be evaluated from this artifact or without a context field, record that as the reason per G4 rather than silently skipping.

**Disconfirmation (pass two).** The Trap requires ALL definitional conditions; NOT present when condition (a) fails — verify each independently. NOT present when condition (b) fails — verify each independently. No further disconfirmation content exists in this source.

**Severity.** Place on the ladder by the worst plausible outcome for the stated goals; apply C3/C4 escalators. No Trap-specific severity anchors exist in this source.

**Assessability & Confidence.** volume is artifact-native; 'too much' is relative to C2 — gate on goals or declare the default.

**Attribution.** Apply G3. No Trap-specific attribution rules exist in this source.

**Report fragments.** Finding: "[cue/element(s)] on [screen]: [definitional condition(s) observed, with named evidence]." Why it matters: "This degrades Efficient: the conditions above prevent or burden progress toward the user’s goal."

**Card example (the source's single anchor).** Back in 2002, the Jeep website had an extremely wordy description explaining how to find the nearest Jeep dealer. By 2007 this issue was fixed.

**Remediation.** No remediation guidance exists in this source beyond the example above. Direction derivable from the definition: remove or negate the definitional condition(s). Do not fabricate technique-level guidance the source does not contain.

---

### TRAP: BAD PREDICTION *(card 17 — mechanically templated from card content)*
*Tenet: Efficient*

**Definition (card, verbatim).** The system incorrectly predicts or interprets the user's intent or preference, resulting in the user having to work around the problem.

**Definitional conditions (decomposed from the definition sentence; the Trap requires all):** (a) the system predicts or interprets intent/preference; (b) the prediction is incorrect for this user (C1/C2); (c) the user must work around it.

**Detection procedure (pass one — flag, do not filter).** *Unit: whole-artifact feature inventory.*
1. From the C2 goal set, survey the artifact for the definitional conditions above.
2. Flag every candidate where the conditions appear present; name the specific cue(s)/element(s) and the condition(s) observed (G6).
3. Where a condition cannot be evaluated from this artifact or without a context field, record that as the reason per G4 rather than silently skipping.

**Disconfirmation (pass two).** The Trap requires ALL definitional conditions; NOT present when condition (a) fails — verify each independently. NOT present when condition (b) fails — verify each independently. NOT present when condition (c) fails — verify each independently. No further disconfirmation content exists in this source.

**Severity.** Place on the ladder by the worst plausible outcome for the stated goals; apply C3/C4 escalators. No Trap-specific severity anchors exist in this source.

**Assessability & Confidence.** incorrectness requires stated user context (C1/C2) or usage evidence; with stated context, visible contradictions are artifact-assessable.

**Attribution.** Apply G3. No Trap-specific attribution rules exist in this source.

**Report fragments.** Finding: "[cue/element(s)] on [screen]: [definitional condition(s) observed, with named evidence]." Why it matters: "This degrades Efficient: the conditions above prevent or burden progress toward the user’s goal."

**Card example (the source's single anchor).** Spelling autocorrection services often make mistakes. When wrong, it is irritating, embarrassing, or insulting.

**Remediation.** No remediation guidance exists in this source beyond the example above. Direction derivable from the definition: remove or negate the definitional condition(s). Do not fabricate technique-level guidance the source does not contain.

---

### TRAP: IRREVERSIBLE ACTION *(card 18 — mechanically templated from card content)*
*Tenet: Forgiving*

**Definition (card, verbatim).** The system does not allow the user to undo an action they have taken.

**Definitional conditions (decomposed from the definition sentence; the Trap requires all):** (a) the user takes an action; (b) the system provides no way to undo it.

**Detection procedure (pass one — flag, do not filter).** *Unit: cross-screen (flows/code).*
1. From the C2 goal set, survey the artifact for the definitional conditions above.
2. Flag every candidate where the conditions appear present; name the specific cue(s)/element(s) and the condition(s) observed (G6).
3. Where a condition cannot be evaluated from this artifact or without a context field, record that as the reason per G4 rather than silently skipping.

**Disconfirmation (pass two).** The Trap requires ALL definitional conditions; NOT present when condition (a) fails — verify each independently. NOT present when condition (b) fails — verify each independently. No further disconfirmation content exists in this source.

**Severity.** Place on the ladder by the worst plausible outcome for the stated goals; apply C3/C4 escalators. No Trap-specific severity anchors exist in this source.

**Assessability & Confidence.** absence of undo requires flow/code evidence; a static shows at most no visible undo affordance — declare the limit.

**Attribution.** Apply G3. No Trap-specific attribution rules exist in this source.

**Report fragments.** Finding: "[cue/element(s)] on [screen]: [definitional condition(s) observed, with named evidence]." Why it matters: "This degrades Forgiving: the conditions above prevent or burden progress toward the user’s goal."

**Card example (the source's single anchor).** In this version of Concur's iOS travel app, pressing the Reserve button not only reserved but also purchased the flight, which could not be undone.

**Remediation.** No remediation guidance exists in this source beyond the example above. Direction derivable from the definition: remove or negate the definitional condition(s). Do not fabricate technique-level guidance the source does not contain.

---

### TRAP: UNWANTED DISCLOSURE *(card 19 — mechanically templated from card content)*
*Tenet: Discreet*

**Definition (card, verbatim).** The system makes the user's data or behavior public in a way that is harmful or embarrassing to the user.

**Definitional conditions (decomposed from the definition sentence; the Trap requires all):** (a) the system makes user data or behavior public; (b) the disclosure is harmful or embarrassing to the user (C3 context).

**Detection procedure (pass one — flag, do not filter).** *Unit: whole-artifact + settings.*
1. From the C2 goal set, survey the artifact for the definitional conditions above.
2. Flag every candidate where the conditions appear present; name the specific cue(s)/element(s) and the condition(s) observed (G6).
3. Where a condition cannot be evaluated from this artifact or without a context field, record that as the reason per G4 rather than silently skipping.

**Disconfirmation (pass two).** The Trap requires ALL definitional conditions; NOT present when condition (a) fails — verify each independently. NOT present when condition (b) fails — verify each independently. No further disconfirmation content exists in this source.

**Severity.** Place on the ladder by the worst plausible outcome for the stated goals; apply C3/C4 escalators. No Trap-specific severity anchors exist in this source.

**Assessability & Confidence.** sharing mechanics are artifact/settings-assessable; harm/embarrassment is C3-gated.

**Attribution.** Apply G3. No Trap-specific attribution rules exist in this source.

**Report fragments.** Finding: "[cue/element(s)] on [screen]: [definitional condition(s) observed, with named evidence]." Why it matters: "This degrades Discreet: the conditions above prevent or burden progress toward the user’s goal."

**Card example (the source's single anchor).** Facebook Beacon was a feature that shared users' partner-site purchase activities on the news feed on an opt-out basis. One consequence of this was that friends were alerted to gifts that were meant to be surprises. Beacon became the target of a class action lawsuit and Facebook shut it down.

**Remediation.** No remediation guidance exists in this source beyond the example above. Direction derivable from the definition: remove or negate the definitional condition(s). Do not fabricate technique-level guidance the source does not contain.

---

### TRAP: DATA LOSS *(card 20 — mechanically templated from card content)*
*Tenet: Protective*

**Definition (card, verbatim).** The system can lose the user's work through some action or inaction on the user's part.

**Definitional conditions (decomposed from the definition sentence; the Trap requires all):** (a) the user creates work; (b) a user action or inaction can cause the system to lose it.

**Detection procedure (pass one — flag, do not filter).** *Unit: cross-screen + failure modes.*
1. From the C2 goal set, survey the artifact for the definitional conditions above.
2. Flag every candidate where the conditions appear present; name the specific cue(s)/element(s) and the condition(s) observed (G6).
3. Where a condition cannot be evaluated from this artifact or without a context field, record that as the reason per G4 rather than silently skipping.

**Disconfirmation (pass two).** The Trap requires ALL definitional conditions; NOT present when condition (a) fails — verify each independently. NOT present when condition (b) fails — verify each independently. No further disconfirmation content exists in this source.

**Severity.** Place on the ladder by the worst plausible outcome for the stated goals; apply C3/C4 escalators. No Trap-specific severity anchors exist in this source.

**Assessability & Confidence.** loss behavior requires flow/live/code evidence; statics show at most missing save/auto-save affordances — declare.

**Attribution.** Apply G3. No Trap-specific attribution rules exist in this source.

**Report fragments.** Finding: "[cue/element(s)] on [screen]: [definitional condition(s) observed, with named evidence]." Why it matters: "This degrades Protective: the conditions above prevent or burden progress toward the user’s goal."

**Card example (the source's single anchor).** Unexpected Windows 8 system shutdowns can cause users to lose any unsaved work. Good user interfaces mitigate this risk by continuously saving users' data.

**Remediation.** No remediation guidance exists in this source beyond the example above. Direction derivable from the definition: remove or negate the definitional condition(s). Do not fabricate technique-level guidance the source does not contain.

---

### TRAP: GRATUITOUS REDUNDANCY *(card 21 — mechanically templated from card content)*
*Tenet: Habituating*

**Definition (card, verbatim).** The system presents duplicate cues (labels, icons, affordances, or prompts) for the same action on the same level, or a directly nested level of the UI.

**Definitional conditions (decomposed from the definition sentence; the Trap requires all):** (a) two or more cues serve the same action; (b) they sit on the same level or a directly nested level.

**Detection procedure (pass one — flag, do not filter).** *Unit: per-screen/per-level.*
1. From the C2 goal set, survey the artifact for the definitional conditions above.
2. Flag every candidate where the conditions appear present; name the specific cue(s)/element(s) and the condition(s) observed (G6).
3. Where a condition cannot be evaluated from this artifact or without a context field, record that as the reason per G4 rather than silently skipping.

**Disconfirmation (pass two).** The Trap requires ALL definitional conditions; NOT present when condition (a) fails — verify each independently. NOT present when condition (b) fails — verify each independently. No further disconfirmation content exists in this source.

**Severity.** Place on the ladder by the worst plausible outcome for the stated goals; apply C3/C4 escalators. No Trap-specific severity anchors exist in this source.

**Assessability & Confidence.** apparent duplicates are artifact-flaggable; confirming same-action requires flows/live/code — declare on statics.

**Attribution.** Apply G3. No Trap-specific attribution rules exist in this source.

**Report fragments.** Finding: "[cue/element(s)] on [screen]: [definitional condition(s) observed, with named evidence]." Why it matters: "This degrades Habituating: the conditions above prevent or burden progress toward the user’s goal."

**Card example (the source's single anchor).** In 2014 Healthcare.gov had three links on the homepage that all went to the exact same place. They subsequently added a fourth link to the same place, which only exacerbated the issue. This duplication of choices impedes habituation.

**Remediation.** No remediation guidance exists in this source beyond the example above. Direction derivable from the definition: remove or negate the definitional condition(s). Do not fabricate technique-level guidance the source does not contain.

---

### TRAP: VARIABLE OUTCOME *(card 22 — mechanically templated from card content)*
*Tenet: Habituating*

**Definition (card, verbatim).** The system responds differently at different times to the same user action.

**Definitional conditions (decomposed from the definition sentence; the Trap requires all):** (a) the same user action occurs at different times; (b) the system's response differs.

**Detection procedure (pass one — flag, do not filter).** *Unit: cross-state/cross-time.*
1. From the C2 goal set, survey the artifact for the definitional conditions above.
2. Flag every candidate where the conditions appear present; name the specific cue(s)/element(s) and the condition(s) observed (G6).
3. Where a condition cannot be evaluated from this artifact or without a context field, record that as the reason per G4 rather than silently skipping.

**Disconfirmation (pass two).** The Trap requires ALL definitional conditions; NOT present when condition (a) fails — verify each independently. NOT present when condition (b) fails — verify each independently. No further disconfirmation content exists in this source.

**Severity.** Place on the ladder by the worst plausible outcome for the stated goals; apply C3/C4 escalators. No Trap-specific severity anchors exist in this source.

**Assessability & Confidence.** not assessable from a single static — requires multi-state, live, or code evidence; declare.

**Attribution.** Apply G3. No Trap-specific attribution rules exist in this source.

**Report fragments.** Finding: "[cue/element(s)] on [screen]: [definitional condition(s) observed, with named evidence]." Why it matters: "This degrades Habituating: the conditions above prevent or burden progress toward the user’s goal."

**Card example (the source's single anchor).** The browser Back button in Twitter yields a different outcome depending on when the user clicks on it. After launching a Twitter dialog and then hitting Back, the user is taken back two steps instead of one. This lack of consistency impedes habituation.

**Remediation.** No remediation guidance exists in this source beyond the example above. Direction derivable from the definition: remove or negate the definitional condition(s). Do not fabricate technique-level guidance the source does not contain.

---

### TRAP: WANDERING ELEMENT *(card 23 — mechanically templated from card content)*
*Tenet: Habituating*

**Definition (card, verbatim).** The physical location of a cue (label, icon, affordance, or prompt) for a given action varies across the UI.

**Definitional conditions (decomposed from the definition sentence; the Trap requires all):** (a) the same cue serves a given action in multiple UI contexts; (b) its physical location varies across them.

**Detection procedure (pass one — flag, do not filter).** *Unit: cross-screen by nature.*
1. From the C2 goal set, survey the artifact for the definitional conditions above.
2. Flag every candidate where the conditions appear present; name the specific cue(s)/element(s) and the condition(s) observed (G6).
3. Where a condition cannot be evaluated from this artifact or without a context field, record that as the reason per G4 rather than silently skipping.

**Disconfirmation (pass two).** The Trap requires ALL definitional conditions; NOT present when condition (a) fails — verify each independently. NOT present when condition (b) fails — verify each independently. No further disconfirmation content exists in this source.

**Severity.** Place on the ladder by the worst plausible outcome for the stated goals; apply C3/C4 escalators. No Trap-specific severity anchors exist in this source.

**Assessability & Confidence.** directly auditable across provided screens; not assessable from a single screenshot — declare.

**Attribution.** Apply G3. No Trap-specific attribution rules exist in this source.

**Report fragments.** Finding: "[cue/element(s)] on [screen]: [definitional condition(s) observed, with named evidence]." Why it matters: "This degrades Habituating: the conditions above prevent or burden progress toward the user’s goal."

**Card example (the source's single anchor).** Placement of the Edit control is inconsistent from one iPhone app to another. Several other functions are similarly inconsistent. This lack of consistency impedes habituation.

**Remediation.** No remediation guidance exists in this source beyond the example above. Direction derivable from the definition: remove or negate the definitional condition(s). Do not fabricate technique-level guidance the source does not contain.

---

### TRAP: INCONSISTENT APPEARANCE *(card 24 — mechanically templated from card content)*
*Tenet: Habituating*

**Definition (card, verbatim).** The visual appearance of a cue (label, icon, affordance, or prompt) for a given action varies across the UI.

**Definitional conditions (decomposed from the definition sentence; the Trap requires all):** (a) the same cue serves a given action in multiple UI contexts; (b) its visual appearance varies across them.

**Detection procedure (pass one — flag, do not filter).** *Unit: cross-screen by nature.*
1. From the C2 goal set, survey the artifact for the definitional conditions above.
2. Flag every candidate where the conditions appear present; name the specific cue(s)/element(s) and the condition(s) observed (G6).
3. Where a condition cannot be evaluated from this artifact or without a context field, record that as the reason per G4 rather than silently skipping.

**Disconfirmation (pass two).** The Trap requires ALL definitional conditions; NOT present when condition (a) fails — verify each independently. NOT present when condition (b) fails — verify each independently. No further disconfirmation content exists in this source.

**Severity.** Place on the ladder by the worst plausible outcome for the stated goals; apply C3/C4 escalators. No Trap-specific severity anchors exist in this source.

**Assessability & Confidence.** directly auditable across provided screens; not assessable from a single screenshot — declare.

**Attribution.** Apply G3. No Trap-specific attribution rules exist in this source.

**Report fragments.** Finding: "[cue/element(s)] on [screen]: [definitional condition(s) observed, with named evidence]." Why it matters: "This degrades Habituating: the conditions above prevent or burden progress toward the user’s goal."

**Card example (the source's single anchor).** The new action in iPhone apps sometime appears as the word New, while elsewhere it appears as a box with a pen. This lack of consistency impedes habituation.

**Remediation.** No remediation guidance exists in this source beyond the example above. Direction derivable from the definition: remove or negate the definitional condition(s). Do not fabricate technique-level guidance the source does not contain.

---

### TRAP: AMBIGUOUS HOME *(card 25 — mechanically templated from card content)*
*Tenet: Habituating*

**Definition (card, verbatim).** The UI provides no single place the user can return to at any time to begin a new task or get re-oriented.

**Definitional conditions (decomposed from the definition sentence; the Trap requires all):** (a) users need a place to begin new tasks or re-orient; (b) no single such place is reliably reachable at any time.

**Detection procedure (pass one — flag, do not filter).** *Unit: whole-IA / cross-screen.*
1. From the C2 goal set, survey the artifact for the definitional conditions above.
2. Flag every candidate where the conditions appear present; name the specific cue(s)/element(s) and the condition(s) observed (G6).
3. Where a condition cannot be evaluated from this artifact or without a context field, record that as the reason per G4 rather than silently skipping.

**Disconfirmation (pass two).** The Trap requires ALL definitional conditions; NOT present when condition (a) fails — verify each independently. NOT present when condition (b) fails — verify each independently. No further disconfirmation content exists in this source.

**Severity.** Place on the ladder by the worst plausible outcome for the stated goals; apply C3/C4 escalators. No Trap-specific severity anchors exist in this source.

**Assessability & Confidence.** candidate homes and return actions are auditable across provided screens; which place users treat as home is C1-gated.

**Attribution.** Apply G3. No Trap-specific attribution rules exist in this source.

**Report fragments.** Finding: "[cue/element(s)] on [screen]: [definitional condition(s) observed, with named evidence]." Why it matters: "This degrades Habituating: the conditions above prevent or burden progress toward the user’s goal."

**Card example (the source's single anchor).** Windows 8 had two different Start or Home experiences. One for mouse and keyboard and one for touch. Much was the same…some was different. The result was confusion, which has been mitigated to some extent in more recent versions of the UI.

**Remediation.** No remediation guidance exists in this source beyond the example above. Direction derivable from the definition: remove or negate the definitional condition(s). Do not fabricate technique-level guidance the source does not contain.

---

### TRAP: UNATTRACTIVE APPEARANCE *(card 26 — mechanically templated from card content)*
*Tenet: Beautiful*

**Definition (card, verbatim).** The UI is aesthetically unpleasing, inconsistent, and/or inappropriate for its intended users.

**Definitional conditions (decomposed from the definition sentence; the Trap requires all):** (a) the UI's aesthetics are unpleasing, inconsistent, and/or inappropriate; (b) judged against its intended users (C1).

**Detection procedure (pass one — flag, do not filter).** *Unit: per-screen + cross-screen consistency.*
1. From the C2 goal set, survey the artifact for the definitional conditions above.
2. Flag every candidate where the conditions appear present; name the specific cue(s)/element(s) and the condition(s) observed (G6).
3. Where a condition cannot be evaluated from this artifact or without a context field, record that as the reason per G4 rather than silently skipping.

**Disconfirmation (pass two).** The Trap requires ALL definitional conditions; NOT present when condition (a) fails — verify each independently. NOT present when condition (b) fails — verify each independently. No further disconfirmation content exists in this source.

**Severity.** Place on the ladder by the worst plausible outcome for the stated goals; apply C3/C4 escalators. No Trap-specific severity anchors exist in this source.

**Assessability & Confidence.** inconsistency is auditable; unpleasingness/appropriateness are judged against the intended users (C1) — gate or declare the default.

**Attribution.** Apply G3. No Trap-specific attribution rules exist in this source.

**Report fragments.** Finding: "[cue/element(s)] on [screen]: [definitional condition(s) observed, with named evidence]." Why it matters: "This degrades Beautiful: the conditions above prevent or burden progress toward the user’s goal."

**Card example (the source's single anchor).** There are many aesthetically pleasing applications, websites and programs. This is not one. This overly cluttered phone app has poor color choice, label justifications and layout issues.

**Remediation.** No remediation guidance exists in this source beyond the example above. Direction derivable from the definition: remove or negate the definitional condition(s). Do not fabricate technique-level guidance the source does not contain.

---

## VERBATIM DEFINITIONS (report display only — never loaded into analysis passes)

*Registry of card-verbatim trap definitions for report rendering, mirroring the v2.1 design. The tool displays the entry matching each cited Trap under its badge; the pack generator MUST exclude this section from the pass-one and pass-two packs and emit it into the manifest for the rendering layer. Note: in this v1 lineage the verbatims equal the working definitions by construction (the card text is the sole source; the Taxonomy Index carries the same wording) — this section exists so the tool's manifest lookup works uniformly across KB families, and duplicates rather than diverges. Source: `Tenets_and_Traps_Card_MASTER_print.pdf`, author-verified 2026-07-04.*

- **Invisible Element** — No cue (label, icon, affordance, or prompt) is provided to signal to the user how to achieve a goal, and the user has insufficient prior learning to overcome its absence.
- **Effectively Invisible Element** — A provided cue (label, icon, affordance, or prompt) is not noticed, or is slow to be noticed, because its appearance or location differs from what the user expects.
- **Distraction** — Something in the UI suddenly appears or otherwise draws the user's attention, distracting them from their goal.
- **Uncomprehended Element** — A cue (label, icon, affordance, or prompt) critical to achieving a goal is noticed, but its meaning, or the required method of interacting with it, is unclear.
- **Inviting Dead End** — A cue (label, icon, affordance, or prompt) is incorrectly judged as a means for achieving a goal. It looks right, but is wrong.
- **Poor Grouping** — A critical relationship between two or more otherwise noticeable cues (labels, icons, affordances, or prompts) is not obvious.
- **Forced Syntax** — The system does not allow the user to issue a command or complete a sequence of actions in the order or manner that is most natural to them.
- **Memory Challenge** — The system requires the user to remember information that is easy to forget.
- **Feedback Failure** — The system fails to provide noticeable, comprehensible, and actionable feedback in response to user actions.
- **Physical Challenge** — An action the system requires the user to perform is physically effortful, difficult, or impossible.
- **Accidental Activation** — The system misinterprets a user's physical actions resulting in an unintended outcome.
- **Slow or No Response** — The user is prevented from achieving a goal in a timely manner because of actual or perceived poor system performance.
- **Captive Wait** — The user is prevented from achieving a goal in a timely manner because the system intentionally prevents them from advancing and/or backing out of a process.
- **Unnecessary Step** — When the product is being used as intended, the number of actual or perceived steps required to achieve a goal is too high.
- **System Amnesia** — The system re-prompts the user for information it previously gathered, or otherwise fails to leverage the user's prior work.
- **Information Overload** — Information presented to the user is comprehensible, but there is too much of it.
- **Bad Prediction** — The system incorrectly predicts or interprets the user's intent or preference, resulting in the user having to work around the problem.
- **Irreversible Action** — The system does not allow the user to undo an action they have taken.
- **Unwanted Disclosure** — The system makes the user's data or behavior public in a way that is harmful or embarrassing to the user.
- **Data Loss** — The system can lose the user's work through some action or inaction on the user's part.
- **Gratuitous Redundancy** — The system presents duplicate cues (labels, icons, affordances, or prompts) for the same action on the same level, or a directly nested level of the UI.
- **Variable Outcome** — The system responds differently at different times to the same user action.
- **Wandering Element** — The physical location of a cue (label, icon, affordance, or prompt) for a given action varies across the UI.
- **Inconsistent Appearance** — The visual appearance of a cue (label, icon, affordance, or prompt) for a given action varies across the UI.
- **Ambiguous Home** — The UI provides no single place the user can return to at any time to begin a new task or get re-oriented.
- **Unattractive Appearance** — The UI is aesthetically unpleasing, inconsistent, and/or inappropriate for its intended users.
