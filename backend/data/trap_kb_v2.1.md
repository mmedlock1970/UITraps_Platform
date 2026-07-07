# UI Tenets & Traps — Analyzer Knowledge Base — v2.1 (manuscript-content lineage; successor to deployed v2.0; full 27-trap coverage)

## PROVENANCE & CHUNK GRADES (maintainer notes — never loaded into analysis passes)

*v2.1 incorporates the salvage audit of the deployed v2.0 KB: rules that passed the salvage test (imperative, condition-named, pass-assigned) are integrated below; v2-sourced additions pending author sign-off are listed in Open Items.*

**Chunk grades.** Seven chunks are pilot-grade (deep-reviewed with the framework author): Effectively Invisible Element, Uncomprehended Element, Inviting Dead End, Forced Syntax, Gratuitous Redundancy, Incorrect Information, Physical Challenge. The remaining twenty are draft-grade: extracted from the manuscript with authoring judgment was marked inline as [JUDGMENT] wherever content went beyond the manuscript. ALL flags were closed via the author Q&A ratification cycle of 2026-07-04 — see the closure log in Open Items; the file carries no open flags. *(Note: inline [JUDGMENT] tags within chunks remain visible to analysis until the author's deep pass strips them — accepted pre-freeze state.)*

---

## GLOBAL RULES (apply to every analysis, both passes)

**G1. Exact trap names.** Use full, exact Trap names; several Traps have near-identical names that denote different problems.

**G2. Two-pass discipline, with selective loading.**
- **Pass one (detection):** load only the Detection Procedures for all 27 Traps, plus the Context Intake Schema. Run each procedure. Flag every candidate. Do not filter, do not weigh disconfirmation, do not assign severity. Over-reporting at this stage is correct behavior. Candidate-line economy the triggering-condition clause is telegraphic — at most ~15 words, no explanatory subordinate clauses. Pass one routes chunks; pass two explains.
- **Pass two (adjudication):** load the full chunks for candidate Traps only, plus the Taxonomy Index (so adjudication can re-route a finding to a non-candidate Trap when a Boundary clause points there). For each candidate, apply in order: (1) Boundary and Disconfirmation; (2) the one-problem-one-issue procedure (G3); (3) the Assessability lookup (G4/G5); (4) Severity and Confidence; (5) assemble the issue per G8. Kill, merge, and relabel freely — that is this pass's job.
- **Mode-agnostic discipline:** the staging above describes the two-pass runtime. In single-call execution the same discipline applies sequentially within one response: complete the full permissive detection sweep across ALL Traps first, then adjudicate the resulting candidates. Never filter, weigh disconfirmation, or assign severity during the detection sweep, in any mode.

**G3. One problem, one issue — evidenced diagnosis.** When multiple candidate flags point at the same underlying design element or decision, report ONE issue. **Atomicity (author-ruled 2026-07-05): the unit of an issue is the unit of independent action.** If a subset of the evidence can be fully resolved by a fix that leaves the rest intact, split it into its own issue and cross-reference the related issue(s) — duplicate controls inside a larger architectural problem are separate, precisely assignable issues. Merge only what one fix decision governs. At the bottom of each issue, list the Traps that align to that issue — each listed Trap must independently meet its own evidence bar (no tag-cloud padding; nothing evidenced omitted). **Issue composition — four forms, decided top-down, stop at the first match (populate the tool's per-Trap `relationship` marker with the bracketed value):**
1. **Single** [none]: only one Trap genuinely applies. Show it; no relationship designation.
2. **Causal chain** [root_cause / consequence]: one Trap's presence produces the others, and its fix dissolves them (apply the discrimination test below). The root is the finding. Consequence Traps appear only within this issue's trap line, designated "(consequence)" — never as separate entries elsewhere and never as their own issues; where a consequence is condition-gated (e.g., repetition-dependent per C4), state the gate. The issue description states the cascade explicitly: what the root is, and which Trap(s) it leads to.
3. **Independent co-failures** [co-occurring]: two or more Traps each true on their own evidence, and no fix dissolves the others. Show all; designate EVERY listed Trap co-occurring — no unmarked primary; address the co-occurrence in the description. A downstream consequence is NEVER co-occurring.
4. **Conditional identity** [conditional — primary / conditional — enumerated]: competing descriptions of ONE failure, decided by a property the artifact cannot settle (audience, intent, context); only one is actually true. Report per the parsimony rule below: the single most applicable Trap [conditional — primary] plus the one-line other-Traps note; FULL enumeration [conditional — enumerated, one per branch] only when branches diverge on recommended fix or on severity — then each branch states, in the description prose, the specific condition under which its Trap applies. Reserve this form for a genuine either/or the artifact cannot resolve; never as a hedge to avoid committing to a finding (the anti-hedging edge in G8 applies).
**Composition conservatism:** prefer the smallest faithful set of Traps that preserves the evidence. A Trap surfaced within an issue never also appears as its own separate issue. **Related-Trap prose test (author-ruled 2026-07-05):** the description mentions a consequence, co-occurring, or conditional-alternative Trap ONLY when doing so (a) adds a consequence the primary diagnosis does not convey, (b) changes the fix's ordering or scope, or (c) is a conditional branch that would change fix or severity. Otherwise omit — the primary diagnosis carries the issue. The per-Trap `relationship` data is populated in full regardless of what the prose omits.

Then discriminate the relationship among the listed Traps before any designation
- **Causal chain** — the listed Traps describe *different failures*, and a single design change at one of them dissolves the others. Only causal chains receive a root-cause designation; apply the root-cause rule below.
- **Conditional identity** — the listed Traps are *competing descriptions of the same failure*, and which one applies depends on an unobservable user or context property (typically C1 prior experience or C3 context of use). NEVER designate a root cause among conditional alternatives — there is no chain, only alternative names for one defect. Report per the parsimony rule below.

**Root-cause rule (causal chains only):**
- **Fix-based root cause:** the root cause is the Trap whose remediation resolves the other listed Traps. Designate it "(root cause)" and mark the others "(consequence)." Worked example: an element noticed slowly *because it moves between screens* — pinning it to one location (Wandering Element's fix) dissolves the noticing problem, so Wandering Element is root cause and the delayed noticing is referenced in the explanation, not separately reported.
- **Bidirectional fixes:** when fixing either Trap would resolve both, fall back to mechanism order — the Trap upstream in the causal chain is root cause.
- **Root cause unclear:** designate no root cause; state "root cause unclear" AND name the specific check that would settle it. "Unclear" without a named check is unfinished adjudication. Independent co-failures — multiple Traps on one element where no fix dissolves the others — get NO designation: co-occurrence without causation is neither a chain nor a conditional identity; list each with its own evidence.

**Parsimony rule (conditional identities only):** enumerating every satisfiable Trap name burdens the reader without changing the action taken. Report the single most applicable Trap — selected on provided C1/C3 where given, else on the declared defaults — and append one line: "Other Traps ([names]) may apply depending on [conditioning factor]." **Exceptions requiring full enumeration — branches diverge on recommended fix or on severity:** then the attribution is load-bearing; present each branch with its Trap, fix, and severity, and name the check that settles which branch the users are on. If neither provided context nor the defaults discriminate between branches, state the tie explicitly — never select arbitrarily. One named sub-case (mixed populations cannot arise: C1 names a single population per evaluation, J26):
- **Manifests-as:** one underlying property produces different Traps at different moments for the same user population and the fix converges (e.g., an unfamiliar goal-critical element that some users filter [Effectively Invisible Element] and others notice but can't decode [Uncomprehended Element]). This is the compact form: report one issue, "manifests as X or Y — same root property, same fix." Do not phrase this as X→Y causation: for the non-noticing user, the noticed-element Trap never occurred.

**G4. Absent vs. unassessable is a lookup, not a judgment — on two axes.** Assessability is a function of the Trap, the artifact evidence, and the context evidence. Before analysis: (a) classify the artifact type (static screenshot / disconnected screens / wired prototype or flow / live product / code); (b) inventory the user context provided against the Context Intake Schema. Consult each Trap's Assessability & Confidence section on both axes. Three finding labels, never interchangeable:
- "Not assessable from this artifact — [what artifact would settle it]"
- "Not assessable without user context — [what context field would settle it]"
- "Not present" — requires that the artifact CAN show the Trap, required context is available or a declared default covers it, the Detection Procedure ran, and no candidate survived (or disconfirmation positively ruled it out — state which). Route by observability, grade by confirmability (author-ruled 2026-07-06): coverage is for what cannot be OBSERVED from the artifact; what is observed but cannot be CONFIRMED is a finding at reduced confidence with a named promotion path — never a coverage entry. A Trap whose Assessability declares the artifact class insufficient can never be cleared from that artifact class (author-ruled 2026-07-06); if a Trap's chunk is absent from adjudication context, default its coverage line to the not-assessable form, never to Not-present. Standing note, all visual artifacts: interaction-modality accessibility (keyboard and focus order, assistive-technology semantics) is largely not assessable — emit once per report: "Not assessable from this artifact — DOM/code artifacts or an assistive-technology session would settle."

**G5. Context softens or gates.** Each Trap's Assessability & Confidence section states what missing context does per schema field:
- Where context *sharpens* calibration: assess anyway, label "Provisional — assumes [stated assumption]," name what would sharpen it.
- Where context *gates* assessment: do not guess — emit the "not assessable without user context" label, unless the Trap's profile declares a permitted default for that field, in which case assess against the default and declare it.

**G6. Named evidence — symmetric.** Every flag, in either pass, must cite the specific element(s) and condition(s) that triggered it. General impressions ("feels cluttered," "low prominence") are not findings. Clearances are held to the same bar a "Not present" verdict must cite the specific disconfirming observation or the scope the procedure actually ran against, with the same specificity required of a finding — and must address the Trap's full definitional scope as given in its chunk. Clearing one manifestation (one element class, one screen region, one definitional clause) does not clear the Trap; state the scope actually cleared. A clearance without named evidence is not a clearance — emit the applicable not-assessable label from G4 instead. Per-instance enumeration (author-ruled 2026-07-06): any claim that an element, badge, or indicator is present on some parallel instances and absent on others must enumerate every instance with its observed state before the claim is made. Presence/absence patterns across repeated elements are the highest-risk observation class; unenumerated pattern claims are not findings.

**G7. Unit of analysis.** Detection Procedures declare their unit: per-screen, cross-screen, or both. For multi-screen artifacts: run per-screen steps on every screen in scope; run cross-screen steps where declared; compute flow-level properties (dominant interaction patterns, persistent elements) across the whole flow before consulting them in per-screen judgments — a single screen misestimates them. Every finding cites the screen(s) where its evidence sits.

**G8. Report architecture — issues first.** The evaluator's goal is not to find and name Traps per se; it is to find and fix user-impacting issues. The Trap vocabulary rides on issues as diagnosis and shared team language. Reports have three sections:

1. **Issues.** One block per adjudicated issue: *what is happening to the user and where* (named elements, plain language, standing on its own without framework knowledge) → *Severity* (ladder + escalators) → *Confidence* (High / Medium / Low, with the promotion path when not High confidence) → *the fix* → closing **trap line**: the Traps aligned to this issue, root cause called out when clear, per G3 patterns. Order issues by severity, worst branch first.
2. **Worth a closer look.** Entries here are questions, not findings: elements whose bearing on the stated goals cannot be determined from the artifact or the provided context, but is pivotal if real. **Discriminator against Issues:** an Issue asserts a problem at some confidence — and High, Medium, and Low confidence are ALL Issue confidences; a Worth-a-closer-look entry asserts no problem — it names an assessability-blocked unknown and the check that settles it. Weak evidence never routes an entry here: a finding that clears its Trap's bar, even at Low confidence, is an Issue; a suspicion that clears no bar is dropped or recorded in Coverage notes — never parked here as a low-confidence copy. **Boundary against Coverage notes:** a Coverage note records status (assessed / not assessable) with no action expected; a Worth-a-closer-look entry demands one — the named check — because the unknown is pivotal. Trap-vs-no-trap routing (author-ruled 2026-07-06): when an unverifiable fact selects between a Trap and no-Trap — as opposed to between two Traps — the finding routes HERE with the verifying check, never to Issues as a conditional assertion.
   **Entry ticket — three gates, hard AND; failing any single gate keeps the entry out:**
   - *(a) The unknown is pivotal to a stated C2 goal.* Fails (a): an ambiguous icon on a path no stated goal passes through — curiosity, not pivotality; route to Coverage notes if not assessable, else drop.
   - *(b) The worst plausible branch clears Medium severity.* Fails (b): an unlabeled element whose worst branch costs one wasted click — Low either way; drop.
   - *(c) A specific, nameable check exists.* Fails (c): "needs more research" or "unclear without testing" with no named check — unfinished adjudication (see the anti-hedging edge), not an entry.
   **Entry format:** *element and where — why it matters given the stated goal — the check, with its cost (e.g., one click in the live product; a task-based user test sized per the user-test sizing rule; a code audit) — the implication, compactly both ways.* Note that the "if not" branch is often itself a live Trap (e.g., if the ambiguous element is NOT the ingress to the goal, nothing on screen may communicate the goal path at all — Invisible Element); reason it through. Batch all checks into a closing verification checklist.
3. **Coverage notes.** Compressed G4 outputs: Traps assessed and not present (with the condition that ruled them out), and Traps not assessable (with what would settle them). Exactly one line per Trap, from this fixed vocabulary, no elaboration: "Not present — procedure run against [scope], no triggering conditions" / "Not present — disconfirmed: [observation]" / "Not assessable from this artifact — [what would settle it]" / "Not assessable without user context — [field]" / "[Trap] — assessed within scope: [artifact-assessable sub-domains]; not assessable from this artifact: [inaccessible sub-domains] — [what would settle them]". The bracketed clause is the G6 evidence; it is mandatory and it is the whole sentence's budget. Trap accounting invariant (author-ruled 2026-07-06): every Trap in the taxonomy is accounted for exactly once per report — as an issue's primary, as a named secondary within an identified issue, or in exactly one coverage bucket; no Trap is ever silently absent. The report's Trap Disposition Index is rendered from this accounting. Scoped-coverage rule (J27): where a Trap's Assessability section declares artifact-inaccessible sub-domains, its scoped coverage line is ALWAYS emitted — including when the Trap also appears in Issues; an issue reports findings within the assessable scope and never implies the inaccessible scope was examined.

**Anti-hedging edge (both directions):** a finding whose evidence clears its Trap's confidence bar MUST be reported as an issue, even where a check could add certainty — the bucket is for genuine pivotal unknowns, not for discomfort; demoting a bar-clearing finding to Worth a closer look is under-reporting. An "I'm not sure" without a nameable check is not a bucket entry; it is unfinished adjudication — resolve it, drop it, or record it as a Coverage note, in that order of preference. An optional whole-report Trap summary may be generated as an appendix view over the issues; it is never the primary structure.

---

## SEVERITY & CONFIDENCE (replaces per-Trap consequence/likelihood/combination blocks)

**Severity ladder** — the worst plausible outcome for the stated goals (C2) under the stated context (C3), per affected user. One axis, three levels:
- **High** — task failure or abandonment with no discoverable recovery, or irreversible harm (data loss, unwanted disclosure, physical or safety harm, unrecoverable cost).
- **Medium** — recoverable failure, or recurring friction.
- **Low** — one-time friction, delay, polish.

**Severity asserts no prediction of occurrence.** It classifies the worst plausible outcome branch conditional on the Trap being real for an affected user. Likelihood is carried elsewhere by design: Confidence (is the Trap real), population conditioning (C1 — every finding names whom it is conditional on), the plausibility gate (evidence must make the branch live, per G6), and exposure (C4). Never write "likely" or any occurrence estimate into a severity rationale; reach is not estimated. Rubric lines in Trap chunks ("High when users abandon") are branch mappings in this conditional sense, not predictions.

**Escalators:**
- **Repetition (C4):** friction on a task performed daily escalates one level; friction on a once-per-lifetime setup task does not. Habituating-tenet Traps scale with repetition by nature.
- **Context (C3):** occupied channels, divided attention, motion, or time pressure can convert "recoverable" to "unrecoverable in practice" (a fumbled interaction while driving is not Medium).

Reach is not estimated. Findings are population-conditional via C1: a finding means "this population hits this." Severity is per-affected-user; priority (severity × reach × strategy) is the team's call, not the analyzer's.

**Confidence scale** — how sure the analyzer is that the problem is real, per finding:
- **High confidence** — direct evidence in hand (e.g., a "not allowed" error message; audited duplicate link targets; a visible input mask; measured contrast below standard).
- **Medium confidence** — risk conditions present, disconfirmation checked and cleared, but the confirming method is not accessible from this artifact or context.
- **Low confidence** — conditions partially present, or the judgment leans on a declared default rather than provided context.

Because severity and confidence share label words (High/Medium/Low), prose must always qualify confidence values with the word "confidence" ("capped at Medium confidence"); severity values stand bare or with "severity." The report's labeled fields (Severity: / Confidence:) disambiguate on screen.

Each Trap's Assessability & Confidence section sets the **ceiling** (a Trap that requires user knowledge, analyzed from a bare screenshot, cannot exceed Medium confidence regardless of how loud the risk conditions are). Every finding below High confidence names its **promotion path**: the specific step that would confirm or dismiss it, with its cost.

**Calibration-gated ceilings.** Where a Trap's definitional threshold is a physical or absolute quantity (target size in millimeters, rendered text size, timing), that quantity is not derivable from a screenshot alone — rendered physical size depends on display hardware and resolution, which the pixels do not carry. Without calibration information (device class and resolution, or an in-artifact reference of known physical size), the ceiling is Medium confidence, promotion path "measure on the target device against [threshold]." High confidence requires stated calibration or on-device measurement. Ratios computable from pixels alone (e.g., contrast ratio) are exempt. Clearances gate identically (G6): "exceeds the minimum" is not observable from an uncalibrated artifact either.

**User-test sizing (promotion paths and remediation checks).** Never recommend a fixed participant count as a rule of thumb. Standard report wording: "Verify with a user test sized to the expected frequency of the problem — common problems need few participants; rare or severe ones need more." Mechanism, so the wording is applied correctly: severity raises the confidence bar to demand before declaring the problem absent; the confidence bar and the expected per-participant discovery rate together set the participant count. A specific count may be stated only when the assumed discovery rate is stated alongside it.

---

## CONTEXT INTAKE SCHEMA (canonical — all Trap gates and defaults reference these fields)

**C1. User Knowledge.** Products and conventions the users have already internalized; domain expertise; prior exposure to this product's own conventions. ONE sub-population per evaluation (J26): C1 names a single population; evaluating multiple segments means running multiple evaluations. If a mixed population is provided anyway, analyze against the FIRST-NAMED segment and emit one prominent Coverage line: "Context named multiple populations; this analysis is conditioned on [first-named]. Run a separate evaluation for [others]." *Default when absent:* general adult population familiar with mainstream web/mobile conventions — declare it. Brand-specific, domain-insider, and novel elements cannot be cleared under the default.

**C2. Goals.** The user's primary tasks and critical paths — AND the fuller set of goals users might plausibly bring to each screen (some Traps require the full set, not just the primary; see Inviting Dead End). *Default when absent:* infer the apparent primary task from the screen itself and declare it; findings requiring the full goal set are degraded under this default.

**C3. Context of Use.** Availability of the user's channels and circumstances:
- *Attention:* fully focused, dividing attention across concurrent tasks, or frequently interrupted.
- *Vision:* eyes available vs. occupied (driving, walking, operating equipment).
- *Hearing:* environment quiet enough to hear audio, or too noisy.
- *Speech & audio-out:* free to speak and play audio comfortably — or constrained by disturbing others or by privacy (information that must not be overheard or displayed to bystanders).
- *Hands:* both free, one occupied, both occupied.
- *Mobility:* stationary vs. in motion.
- Plus: lighting, time pressure or stress, device and input method.

*Default when absent:* attentive, stationary, unencumbered, quiet, private use — the most forgiving context on every channel. Declare it, and state that findings under this default are a lower bound: occupied channels raise likelihood of attention- and memory-dependent Traps and can create channel-dependent Traps outright (an auditory-only element in a loud environment; a two-handed interaction for an encumbered user) without any change to the pixels.

**C4. Exposure & Repetition.** Two facets of the learning curve:
- *User exposure stage:* first-run users, habituated users, or a mix.
- *Task repetition profile:* performed once (setup, onboarding), a few times, or repeatedly for as long as the product is used.

Habituating-tenet Traps scale with repetition; one-time tasks make comprehension Traps paramount — every user is a first-timer, forever. *Defaults when absent:* mix including first-time users for public-facing products; infer the task's repetition profile from its nature (setup vs. core loop) — declare both.

---

## TAXONOMY INDEX (all 27 Traps — pass-two routing reference)

**UNDERSTANDABLE** (It makes clear what I can do)
- **Invisible Element** — no label, icon, or other interface element is provided to let the user know how to achieve a goal, and the user lacks the prior learning needed to overcome its absence.
- **Effectively Invisible Element** — an element goes unnoticed because it is unexpected or misaligned with the user's focus of attention.
- **Distraction** — something in the interface draws the user's attention away from their current goal.
- **Uncomprehended Element** — an element is noticed, but its meaning or required method of interaction is unclear.
- **Inviting Dead End** — an element is incorrectly judged to be a means of achieving a goal; it looks right but is wrong.
- **Poor Grouping** — an important relationship between two or more interface elements is unclear.
- **Forced Syntax** — a sequence of actions cannot be completed in the order or manner the user expects or prefers.
- **Memory Challenge** — the user is required to remember information that is easy to forget.
- **Feedback Failure** — the system fails to communicate the consequence of the user's actions, or how to resolve a failed action.

**COMFORTABLE** (It's physically effortless to use)
- **Physical Challenge** — some aspect of the system causes physical discomfort or makes it physically difficult or impossible to complete actions.
- **Accidental Activation** — it's easy for the user to unintentionally trigger an action during normal use.

**RESPONSIVE** (It never makes me wait)
- **Slow or No Response** — the actual or perceived time the system takes to respond exceeds what the user wants or expects.
- **Captive Wait** — the system does not allow the user to advance or back out of a process at a time of their choosing.

**EFFICIENT** (It minimizes how much I must do)
- **Unnecessary Step(s)** — the number of steps required to achieve a goal is greater than it needs to be.
- **Information Overload** — information presented is understandable but there's more of it than there needs to be.
- **System Amnesia** — the system fails to take advantage of the user's prior work, preferences, or context.

**ACCURATE** (It's factual and relevant)
- **Incorrect Information** — information presented is factually wrong, distorted, incomplete, out-of-date, or contains errors.
- **Bad Prediction** — the system fails in its attempt to anticipate the user's intent, preference, or context; it guesses wrong.

**PROTECTIVE** (It gives me control over my actions and data)
- **Irreversible Action** — the user cannot backtrack or undo an action they have taken, though recovery is possible but unsupported.
- **Unwanted Disclosure** — the system exposes personal data or behavior in a way that is harmful, embarrassing, or unexpected.
- **Data Loss** — the system fails to retain information or content the user expects to be preserved.

**HABITUATING** (It becomes automatic to use over time)
- **Gratuitous Redundancy** — multiple separate elements at the same level serve the same function (destination, action, or information), whether visually identical or not.
- **Variable Outcome** — the system responds differently and unexpectedly to the same user action at different times.
- **Wandering Element** — the same interface element is presented in a different location at different times.
- **Inconsistent Appearance** — the same interface element is presented in a different style at different times or in different places.
- **Ambiguous Home** — the interface presents multiple, competing locations for getting oriented and initiating tasks.

**BEAUTIFUL** (It's aesthetically appealing)
- **Poor Aesthetic** — the system's sensory design, style, personality, or tone is judged unpleasing, inappropriate, or inauthentic by its intended users.

**Sibling Traps (reserved term):** Uncomprehended Element and Inviting Dead End are siblings — the same element can present either Trap, with which one applying depending on the user's prior experience: a user who has never seen the element forms no interpretation (Uncomprehended Element); a user who knows it from elsewhere, applied to a different function, forms a confident wrong one (Inviting Dead End). No other Trap pair is termed "sibling."

---
## TRAP CHUNKS — UNDERSTANDABLE

### TRAP: INVISIBLE ELEMENT *(ratified 2026-07-04)*
*Sub-tenet: Noticeable*

**Definition.** Nothing in the interface communicates how to achieve a goal — no label, icon, or other element — and the user lacks the prior learning to overcome the absence. Applies to absent visual, tactile, or auditory elements. Common forms: hidden swipe actions, press-and-hold actions, hover-only labels.

**Boundary.** IS a *missing* element (in Norman's terms, a missing signifier — Norman's own refinement of his earlier 'affordance,' which properly names the action possibility rather than its perceivable indicator: nothing signals the action is available). IS NOT Effectively Invisible Element — there, an element exists but goes unnoticed; here, no element exists. IS NOT present when users already carry the knowledge (pinch-to-zoom is invisible but universally learned). IS NOT a gated path: when the path to a goal is absent because a prerequisite gate (authentication, registration, paywall, mandatory consent) blocks access, the path is not hidden — it is blocked; classify under Unnecessary Step(s) (see its forced-prerequisite-gate flag), not here. This Trap requires that the path exists but lacks visible communication. This Trap covers the absence of any perceivable signifier — visual, tactile, of any kind — at the moment of need, whether by design (edge-swipe and gesture-only interactions, hover-only reveals) or by placement off the visible viewport: an element the user cannot perceive when they want to act is, for them, absent. If any perceivable cue of the path or of its continuation IS presented (a scroll indicator, partial content peek, hint text), something was presented — route that cue's failure to Effectively Invisible Element or Uncomprehended Element instead.

**Detection procedure (pass one — flag, do not filter).** *Unit: per-screen + task analysis.*
1. From C2 goals, enumerate goals achievable on/from this screen per the product's actual capabilities (from flows, code, or documentation where available).
2. For each goal, check: does any visible/audible/tactile element communicate how to initiate it?
3. Flag every goal with no communicating element — noting whether an invisible interaction is the SOLE path (highest concern) or a visible alternative exists.
4. Flag interactions requiring gestures with no on-screen element signaling them (swipe, press-and-hold, hover-reveal, corner-hotspots).
5. Flag content that continues beyond the visible fold with no visible continuation indicator — scroll affordances cannot be assumed absent strong prior learning for that context.
6. Flag fallback interactions that are the sole path when a primary modality is unavailable (per C3) but carry no visible communication — a fallback is an Invisible Element in exactly the context where it is needed.
7. Where version or redesign context is available: flag removal of a formerly visible element for a core function — prior learning pointed to the element, not the underlying interaction, so removal creates this Trap even for experienced users. Static-screenshot limitation: the analyzer can only detect this Trap for goals it knows the product supports — declare "capability list needed" when goals cannot be enumerated.

**Disconfirmation (pass two).** Path-exhaustion rule (author-ruled 2026-07-05): before flagging, enumerate every on-screen element that plausibly provides or signals a path to the goal; if any exists — however unfamiliar or ambiguous — this is NOT Invisible Element (ambiguity routes to Uncomprehended Element; expectation-mismatch to Effectively Invisible Element). Where a candidate path-element exists but its destination is unverifiable from the artifact, report the conditional-identity form — Uncomprehended/Effectively Invisible Element primary per C1, Invisible Element only as the verified-no-path branch — with the check "verify where [element] leads." NOT present when: (a) users have sufficient prior learning from products they regularly use — standard: the interaction exists on multiple established platforms, or the target population (C1) demonstrably learned it; (b) an alternative visible means of the same action exists; (c) effective instruction has demonstrably been delivered meeting all six conditions: presented when the user is ready and motivated; action physically easy; feedback immediate and clear; total invisible-interaction count kept very low; each action distinguishable; training reintroduced on retention failure.

**Severity.** High by default — the user cannot achieve a goal they would reasonably attempt; High in safety contexts (vehicle exits, emergency functions — see Tesla door releases). Low–Medium when a visible alternative exists (invisible path is then an expert shortcut). C4: for one-time tasks, instruction-based mitigation is weakest (no chance to habituate).

**Assessability & Confidence.** Sole-path invisible interactions with no visible alternative: High-confidence ceiling from artifact + capability knowledge (Tier-1-like). Otherwise Medium confidence ceiling — prior learning (C1) gates disconfirmation (a). Code/flow artifacts materially improve detection (hidden handlers enumerable). Context axis: C1 gates clearing on prior-learning grounds; C3 raises severity when the invisible path's modality is unavailable (voice command in a loud venue — the Humane Pin case). Call this Trap definitively only when BOTH hold: (a) the function is KNOWN to exist — established from flows, code, documentation, or verified product capability, never assumed; and (b) nothing is presented to the user at the time they want to use it. Function existence unestablished → the absence may be a capability gap, not a Trap: cap at Low confidence, or route to Worth a closer look with the check "verify the capability exists." Detection scope is the intersection of known capabilities and stated C2 goals; outside it, absence claims are untestable, not clear. Scoped coverage (always emitted): "Invisible Element — assessed within scope: paths for stated goals with known capabilities; not assessable from this artifact: signifier absence for undocumented capabilities (incl. gesture-only functions) — flows or code would settle."

**Attribution.** Often root cause of Variable Outcome: a mode with NO indicator. Confirm outcome variation independently; the missing indicator alone confirms only this Trap. With Memory Challenge: a trained-but-forgotten invisible interaction is both — recall failure vs. never-learned determines which leads. Distinguish from Effectively Invisible Element via existence: no element → here; unnoticed element → there.

**Report fragments.** Finding: "No visible element signals how to achieve [goal]; users cannot reasonably be expected to discover [interaction]." Why it matters: "Users who do not discover this interaction cannot complete the goal."

**Remediation.** Make the action visible — almost always the easier and more reliable path. If the invisible interaction must remain, deliver instruction meeting the six conditions, and keep the total number of invisible interactions very low. Emergency and fallback interactions — needed precisely when users are most stressed — must be the most visibly communicated interactions in the product, not the least.

---

### TRAP: EFFECTIVELY INVISIBLE ELEMENT *(ratified 2026-07-04)*
*Sub-tenet: Noticeable*

**Definition.** An element that is present and perceivable, but that users fail to notice — because it sits outside their attentional focus for the task, **or because it is presented in an unexpected way, regardless of its location**. Applies to visual, auditory, and tactile elements.

**Boundary.**
- IS: a perceivable element likely to go unregistered given where the user's attention falls during the task, or given what they are looking for. **Central placement and high salience do not disconfirm this Trap; expectation mismatch renders elements unnoticed independent of position (goal-driven filtering — the brain passes signals matching the user's search template and suppresses the rest).**
- IS NOT **Invisible Element**: there, no perceivable element exists at all. Tie-breaker: an element exists but is likely missed → here; no element exists → there.
- IS NOT **Distraction**: that Trap is attention wrongly captured; this one is attention never captured (mirror images). Shared-salience-budget cases (one over-weighted element captures attention AND drowns a goal element): one issue, anchored on the goal element's finding HERE, the over-weighted element named as root cause in the fix — see Distraction's Attribution.
- IS NOT **Wandering Element**: if the element would be noticed at a stable location and the noticing failure stems from its moving between screens or states, Wandering Element is the root cause (fix-based rule) — flag it there and reference the delayed noticing in the explanation.
- IS NOT **Inconsistent Appearance**: if the noticing/recognition failure stems from the same element being restyled across contexts, attribute there.
- IS NOT mere small size or subtle styling in the abstract: the test is misalignment with task-driven attention or expectation, not aesthetics.

**Detection procedure (pass one — flag, do not filter).** *Unit: per-screen, plus cross-screen steps for multi-screen artifacts.*
1. From the stated or assumed user goal, identify the elements on each screen in scope critical to completing it.
2. For each critical element, record: (a) location relative to the likely attentional focus for this task (focus = where the task's primary content or interaction lives, not screen center); (b) whether it differs from surroundings on any pre-attentive feature (color, size, orientation, motion); (c) whether its interaction style matches the flow's dominant interaction pattern (computed per G7); (d) the number of elements competing for attention in its vicinity; (e) **whether the element's appearance matches the visual category users would be searching for, given the goal it serves and their prior experience (C1) — does the thing that does X look like the kind of thing this population expects X to look like?**
3. Flag as candidate any critical element that: is peripheral to the task focus AND lacks pre-attentive distinction; OR deviates from the dominant interaction pattern; OR sits in a high-competition zone; **OR mismatches the user's likely search template for its function — flag regardless of location or visual prominence.**
4. Name the specific condition(s) per flag (G6).
5. Cross-screen (multi-screen artifacts only): flag state or mode indicators that must be noticed on a different screen from where the state was set; flag content that changes between screens in ways the user would not expect (unexpected changes are unlooked-for, hence filtered). Location changes route to Wandering Element; appearance changes route to Inconsistent Appearance (see Boundary).

6. Flag goal-critical elements styled or positioned like promotional content (banner slots, right rails, ad-like framing) — learned suppression of ad-shaped regions applies regardless of C1 product familiarity.

**Disconfirmation (pass two).** NOT present when: (a) the element is in a location users are habituated to attending from prior product experience (C1) — even if not geometrically central; (b) the element differs from surroundings on a pre-attentive feature causing automatic pop-out AND matches the expected category for its function; (c) the element is consistent with the dominant interaction pattern, so users naturally encounter it in normal task flow.

**Severity.** High when the element is critical-path and fully unnoticed (functionally identical to absence). Delayed noticing is still this Trap; its severity equals the consequence of the delay in the specific task context (a missed mute indicator mid-meeting: High; a slowly-found settings link: Low). Escalators: C3 (divided attention, noise, motion sharply raise miss likelihood); C4 (recurring tasks compound the cost).

**Assessability & Confidence.** Static screenshot: High-confidence ceiling only when the element is measurably far from the primary task area AND critical to task completion; otherwise Medium confidence — promotion path: confirm attentional focus with user observation (usability testing is the gold standard; design review alone cannot reliably confirm or rule this out — curse of knowledge). Context axis: C2 (task goal) softens under its default; C1 gates disconfirmation (a) only — absent C1, candidates cannot be cleared on habituation grounds and stay flagged; C3 modifies likelihood globally (its default makes findings a lower bound).

**Attribution.**
- Variable Outcome: an effectively invisible mode indicator is evidence toward Variable Outcome, but outcome variation must be independently confirmed; when confirmed, this Trap is typically root cause (fixing the indicator's noticeability resolves the outcome surprise).
- Information Overload: if the noticing failure dissolves by removing surrounding excess, Information Overload is the root cause (fix-based rule) — the manuscript states reducing it is often the remedy.
- Distraction: if motion was added to remedy this Trap, independently confirm the motion now captures attention away from the current goal before also flagging Distraction.
- Gratuitous Redundancy: if the element was *duplicated* to remedy this Trap, evaluate the duplicates under Gratuitous Redundancy — duplication is not an endorsed remedy (see Remediation).
- Two-gate interaction with Uncomprehended Element: an unfamiliar goal-critical element can fail pre-attentively (filtered — this Trap) or post-attentively (noticed but undecodable — Uncomprehended Element). Same root property; when the fix converges (a familiar, recognizable element), report one issue using the manifests-as pattern (G3). Live user observation distinguishes the gates (a fixation that never lands vs. a puzzled hover) — needed only if the team wants to size the noticing problem independently.

**Report fragments.** Finding: "An element critical to [goal] is present but likely to go unnoticed: [element], because [named condition — peripheral to task focus / pattern deviation / attention competition / expectation mismatch]." Why it matters: "Users who miss this element cannot proceed — functionally identical to the element being absent."

**Remediation.**
- Place the element within or adjacent to the user's primary attentional focus during the task in which it matters, and render it in the visual category users expect for its function.
- Or make one instance globally perceivable: whole-screen state changes (tint shift, screen-edge pulse) or attention-following placement — techniques that reach the user wherever their focal spotlight sits.
- Exploit pre-attentive features (color, size, orientation, motion) for pop-out. Caution: motion applied to elements not relevant to the current goal becomes a Distraction Trap.
- **Do not remedy by duplicating the element.** The focal area of human vision is tiny and constantly moving; duplicating indicators to "cover" attention produces indicator proliferation and a Gratuitous Redundancy Trap. One element, made unmissable, beats many competing for notice.

---

### TRAP: DISTRACTION *(ratified 2026-07-04)*
*Sub-tenet: Noticeable*

**Definition.** Something in the interface draws the user's attention away from their current goal. The mirror image of Effectively Invisible Element: every attribute that makes something noticeable (color, motion, sound, sudden appearance, spatial position) can direct attention appropriately or hijack it. Forms: pop-up notifications, auto-playing audio/video, animated ads, attention-demanding chrome; also mere presence of certain information (a visible phone, a persistent badge), and mode-of-interaction distraction (voice interaction consumes the same cognitive resources as internal verbal thought — issuing a voice command mid-thought breaks the thought; a practiced physical action does not).

**Boundary.** IS: unsolicited exogenous attention capture away from the user's goal. IS NOT present when the user initiated it, when it is directly relevant to the current goal (a status update during an active process), when no focused goal exists to disrupt (passive browsing), or when the user would judge the interruption justified (an emergency call). IS NOT Information Overload: excess information slowing processing is that Trap; specific elements capturing attention is this one — the line is blurry and the fix is shared (remove what isn't relevant to the goal), so when both flags fire on the same material, report one issue and evidence each Trap independently. Bad-faith exploitation (engagement-driven autoplay, attention-hijacking ads) should additionally be flagged as a potential dark pattern.

**Detection procedure (pass one — flag, do not filter).** *Unit: per-screen; cross-screen for elements that appear during flows.*
1. Enumerate every element that moves, animates, auto-plays, sounds, appears without user initiation, or changes state on its own; plus persistent attention-pulling elements (badges, blinking indicators) and, in flow artifacts, interstitials/notifications injected mid-task.
2. For each, record: user-initiated? relevant to the C2 goal at that moment? modality (motion and peripheral motion are un-ignorable — the orienting response is involuntary)?
3. Flag every uninitiated, goal-irrelevant attention-capturing element; flag cumulative competition (many simultaneous attention-demanding elements — the Boeing 737 pattern) as its own candidate.

**Disconfirmation (pass two).** NOT present when: (a) directly relevant to the current goal; (b) passive/exploratory context with no focused goal; (c) user-initiated; (d) the user would agree the interruption was justified by its importance.

**Severity.** Grade by the cost of the captured glance, never by the fact of capture (author-ruled 2026-07-06). Low when the capture displaces nothing and interrupts nothing — the user glances and returns at the cost of a saccade (a peripheral ticker, badge, or ambient element during a browsing or orientation task, motion included). Escalate only on named costs: occlusion or displacement of goal-critical content — anchor: a notification popping over active driving directions (card example): High, critical information obscured mid-task; interruption of a fragile task state (mid-input, mid-transaction) where recovery may lose work or place: Medium; recovery cost beyond a glance (lost position in reading or in a flow): Medium; C3 divided-attention or safety contexts converting glances into danger (competing cockpit warnings): High; C4 persistence — continuous motion in the periphery taxing an extended task repeatedly — escalates one level. Cumulative visual noise from many individually low-cost captures is not graded here: route the aggregate to the shared-salience-budget rule (Attribution) and Poor Aesthetic's cumulative-risk observation — per-element severity is never inflated to express a screen-level problem.

**Assessability & Confidence.** Auto-play audio/video during documented task flows: High-confidence ceiling from artifact. Otherwise Medium confidence — whether capture harms depends on task context (C2 gates: what is the user trying to do when this fires?). Scoped coverage (statics): "Distraction — assessed within scope: persistent attention-pullers, layout-visible interstitials; not assessable from this artifact: motion, animation, audio, and timing behaviors — live session or screen recording would settle." Context axis: C2 gates goal-relevance judgments; C3 sharpens severity.

**Attribution.** Shared-salience-budget cases — one over-weighted element both captures attention AND drowns a goal element: report ONE issue anchored on the goal element's Effectively Invisible Element finding, the over-weighted element named as root cause in the fix, the Distraction evidence folded into the description (the Q18 victim-oriented pattern). If motion was added as a remedy for an Effectively Invisible Element, confirm the original attention problem independently; remediation must replace, not merely delete (see that Trap). Information Overload: confirm excess volume independently — do not infer overload from one distracting element. Bad Prediction: an irrelevant proactive notification is Bad Prediction root cause with Distraction as consequence (fix-based: improving the prediction/removing the proaction resolves the distraction).

**Report fragments.** Finding: "[Element] draws attention away from [goal] without user initiation, goal relevance, or a justification the user would endorse." Why it matters: "Involuntary attention cannot be suppressed — users will notice this regardless of their efforts to focus."

**Remediation.** The governing question is not "will this be noticed?" but "what will the user be doing when this appears, and what will noticing it cost them?" Remove or defer uninitiated elements during focused execution; evaluate whether each interruption serves the user or the product's engagement metrics. Caution: removing a distraction that compensated for an Effectively Invisible Element requires adding a non-distracting visible solution.

---

### TRAP: UNCOMPREHENDED ELEMENT *(ratified 2026-07-04)*
*Sub-tenet: Comprehensible*

**Definition.** The user notices an interface element but cannot make sense of its meaning or how to interact with it. Applies to icons, labels, controls, physical affordances, text prompts, and audible elements. The governing question is not "will users figure it out?" but "have we made sure they already know?" — comprehension is previously learned recognition, not deduction.

**Boundary.**
- IS: a noticed element that yields *no* confident interpretation for the target population. "Noticed" includes passing over: the user looked at it, failed to interpret it, and moved on — noticing happened, comprehension failed.
- IS NOT **Inviting Dead End** (sibling Trap — see Taxonomy Index for the reserved definition): there, the user forms a confident interpretation that is *wrong*. Tie-breaker: no interpretation → here; wrong interpretation → there. Under a mixed population (C1/C4 defaults), both can be simultaneously true of one element for different segments — use the segment-conditional trap line (G3), each Trap independently evidenced.
- IS NOT **Effectively Invisible Element**: that Trap is failure to notice; this one begins after noticing succeeds. But note the two-gate interaction: the same unfamiliar element can be filtered pre-attentively (that Trap) or noticed and undecodable (this one) — when the fix converges, one issue, manifests-as pattern (G3).
- IS NOT **Memory Challenge**: a user who once learned the meaning but cannot recall it has a recall failure, not a comprehension failure — the interventions differ.
- IS NOT a state-visibility problem: when the issue is that current state or selected values are not shown (filter state invisible, selection undisplayed), the meaning of the element may be perfectly clear — route to Feedback Failure or Invisible Element. The test: MEANING of the element unclear → here; VISIBILITY of state → there.
- IS NOT **Information Overload** — opposite polarities: that Trap is too much understandable content; this one is content insufficient to interpret or act confidently. If the problem description reads as the reverse of the chosen Trap's definition, the wrong Trap was chosen.
- Comprehension is not static: replacing a learned element's form or meaning (a heart that becomes a check; a mic that becomes a brand symbol) creates this Trap for experienced users — their learning attached to the old form.
- IS NOT unfamiliarity in the abstract: comprehension is population-relative (C1).

**Detection procedure (pass one — flag, do not filter).** *Unit: per-screen.*
1. From the goals (C2), enumerate, on each screen in scope, every element the user must interpret to proceed: icons, labels, controls, affordances, prompts.
2. Classify each: (a) universal convention (magnifying glass, house, gear); (b) domain convention; (c) product/brand-specific symbol; (d) novel element. Record whether a text label accompanies it, and whether icon and label agree.
3. Flag: any (c) or (d) element for a core function lacking a text label; any element whose icon and label contradict each other; any label using insider or domain jargon outside the population's presumed vocabulary (C1); any (b) element when C1 does not establish domain familiarity.
4. Name each flag with the element, its classification, and the missing compensation (G6).

5. Flag meaning or state encoded solely in hue with no shape, label, or position redundancy — ~8% of males have a color-vision deficiency; the finding is population-conditional, but the encoding fact itself is eligible for High confidence from pixels. Contrast-adjacent legibility routes to Physical Challenge.

**Disconfirmation (pass two).** NOT present when: (a) the element is a widely adopted convention the population is demonstrably familiar with (C1, or the C1 default for universal conventions); (b) a text label compensates for an unclear icon — a label reduces but may not eliminate the Trap when the icon actively contradicts it; (c) effective instruction is delivered at the moment of first encounter.

**Severity.** High when the element is on the critical path — most users choose not to "figure it out"; they abandon. Medium when alternatives exist. Escalators: C4 — one-time tasks (setup, onboarding) make this Trap paramount: every user is a first-timer, forever, and habituation will never rescue it.

**Assessability & Confidence.** High-confidence ceiling from a static artifact for brand symbols used as functional icons with no conventional equivalent and no text label — the risk is high enough on the artifact alone. Otherwise Medium confidence ceiling — comprehension is population-relative; promotion path: show the element to a few target users and ask what it means (cheap; recommend it in reports — there is no excuse for skipping it). Context axis: C1 gates most judgments — the C1 default clears universal conventions only; brand-specific, domain, and novel elements stay flagged under the default. C4 softens: habituated populations lower likelihood.

**Attribution.**
- Inviting Dead End: confirm independently that a specific *incorrect* element is likely to be chosen — not merely that the correct element is unclear. Often co-occur (right path unclear, wrong path compelling), compounding — list both only when both are evidenced.
- Memory Challenge: if users once knew the meaning, the finding moves there — confirm which failure it is.
- Where branding drove the unclear element, name the root cause as over-indexing on differentiation (a design-decision cause, not a separate Trap).

**Report fragments.** Finding: "[Element] is unlikely to be correctly interpreted by users unfamiliar with [product/brand/domain convention], and no standard element or text label clarifies its meaning." Why it matters: "Users who cannot interpret this element cannot determine how to proceed — and most will not work to figure it out."

**Remediation.** Use universally recognized elements for core functions. When in doubt, add a text label — a labeled unclear icon always beats an unlabeled one. For genuinely novel concepts, plan instruction delivered when the user is ready to receive it. Replacing a well-learned brand symbol with a conventional element is almost always the right call for functional elements, even at the cost of brand expression.

---

### TRAP: INVITING DEAD END *(ratified 2026-07-04)*
*Sub-tenet: Comprehensible*

**Definition.** An interface element is incorrectly judged to be a means of achieving a goal — it looks right but is wrong. Two recurring forms: (1) lookalike elements — similar icons or labels representing different functions, so the wrong one attracts users pursuing the right one; (2) post-hoc invalidation — the interface presents as valid an option that is rejected only after the user commits (error messages amounting to "the action you just took is not allowed"; options revealed as unavailable, paywalled, or region-blocked only after selection).

**Boundary.**
- IS: an element that is present, compelling, and incorrect for a goal the user plausibly holds — the interface equivalent of a false affordance.
- IS NOT **Uncomprehended Element** (sibling — see Taxonomy Index): there the user forms no interpretation; here a confident wrong one. Each requires its own evidence; segment-conditional listing under mixed populations (G3).
- IS NOT **Accidental Activation**: an Inviting Dead End *lures* action ("I am the right choice"); Accidental Activation *fails to prevent* an action whose risk was never communicated. One invites, the other fails to guard.
- IS NOT **Poor Grouping**: if a *spatial ambiguity* (unclear association between label and control) creates the false path, attribute there; this Trap's mechanism is the element's own semantics or visual similarity.
- IS NOT the root cause when **Incorrect Information** creates it: a mislabeled button or outdated instruction functions as an Inviting Dead End, but Incorrect Information is the root cause — correct the information first; report this Trap as consequence (G3).
- There is NO acceptable instance of post-hoc invalidation: an option that will be refused must communicate its unavailability before the user acts. An error message saying "don't do what you just did" is never the fix — it is the evidence.

**Detection procedure (pass one — flag, do not filter).** *Unit: per-screen for lookalike and hidden-gate flags; cross-screen for path-walking.*
1. Enumerate the goals a user could plausibly bring to each screen in scope — the full C2 set, not only the primary task. An element can be the correct path for one goal and an Inviting Dead End for another.
2. For each goal, walk every plausible path, not just the intended one. At each decision point, list the elements a user unfamiliar with the system might judge the correct next step — weighting visual prominence, label semantics, proximity to the correct path, and similarity to the element the user would expect.
3. Flag: lookalike pairs (similar icons or labels, different functions); elements styled as interactive that are not; options presented as available that carry hidden gates (fees, regions, states) revealed only after commitment; CTA text making a specific promise the destination objectively does not keep ("Free Download" leading to payment) — where the destination is verifiable in the artifact, promise-breaking is High confidence-grade.
4. Flag independently: any visible error state or message amounting to "that action is not allowed" — direct High confidence-grade evidence that a wrong path was left open and inviting.
5. Name each flag with the element, the goal it falsely invites, and the actual destination or outcome (G6).

**Disconfirmation (pass two).** The invitation test (author-ruled 2026-07-06): this Trap requires that the element makes a specific, false representation of fit to the goal — "this looks like the right thing" — judged against what its label, icon, or placement actually communicates to the C1 population. An element a user might try as a plausible container or in the absence of better options — "let me see if this works" — is NOT this Trap: generic categories, broad menus, and search boxes invite exploration, not a specific promise. If exploration fails, the failure belongs to the missing or invisible path to the goal, not to the explored element. Test: would the C1 user, seeing the element, believe it IS the path — or merely that it MIGHT contain one? NOT present when: (a) no other element could plausibly be mistaken for the correct path to the user's goals (C2); (b) the correct element is visually and semantically distinctive enough from all others that confusion is implausible in this task context.

**Severity.** Medium for recoverable wrong turns (wasted effort, lost confidence); High when users cannot recover to the correct path — anchor: the music icon that opens the store instead (card example): Medium, a recoverable wrong turn, but recurring (C4) and confidence-eroding; escalates when the dead end commits the user (payment, destructive confirmation) before revealing itself. Escalators: C3 — divided attention makes lookalike errors far more likely (the current-floor elevator button); C4 — lookalikes in recurring tasks compound.

**Assessability & Confidence.** A visible "not allowed" error state in the artifact, or such logic in code: High confidence from the artifact alone. Lookalike pairs and hidden-gate presentations from statics: Medium confidence ceiling (plausibility is population-relative); promotion path: user task observation, or flow/code audit for post-hoc invalidation logic. Context axis: C2 gates breadth — without the full goal set, only primary-task dead ends can be assessed (declare under the C2 default); C1 gates population-specific plausibility; C3 raises likelihood under divided attention.

**Attribution.** Uncomprehended Element: confirm the correct element's meaning is genuinely unclear before also reporting it — a compelling wrong element attracts users even when the right one is clear. Poor Grouping: confirm spatial ambiguity is the mechanism, vs. visual similarity. Incorrect Information: where wrong content creates the false path, it is root cause; this Trap is its consequence. Irreversible Action: a dead end that commits irreversibly is both, with this Trap as the luring cause.

**Report fragments.** Finding: "[Element] is likely to be judged the correct path to [goal] but leads to [actual destination/outcome]." Post-hoc form: "[Option] is presented as available but refused after selection ([error/gate]) — the interface invites an action it will not honor." Why it matters: "Users who follow this path expend effort, lose confidence, and may not recover to the correct path without assistance."

**Remediation.** Walk every plausible path; at each decision point, remove or visually differentiate anything that could be mistaken for the correct next step. For post-hoc invalidation: communicate unavailability before the act — disable, hide, or mark the option; never rely on the error message. For lookalikes: increase differentiation or eliminate the wrong path entirely. When a design needs an explanatory label to stop users from taking the wrong action, the label is evidence of the Trap, not its solution — redesign the elements so the wrong path stops looking right.

---

### TRAP: POOR GROUPING *(ratified 2026-07-04)*
*Sub-tenet: Comprehensible*

**Definition.** An important relationship between two or more interface elements is unclear. Covers visual/spatial relationships (unclear hierarchy, insufficient white space, ambiguous label-to-control mapping) AND conceptual organization within information architectures — menu hierarchies, navigation structures, content categorization (per the framework author's ruling in the manuscript's PG1).

**Boundary.** IS: a *relationship* failure between elements, where the relationship is critical to the user's goal. IS NOT about individual elements' meaning (Uncomprehended Element) or noticeability. IS NOT present when apparent groupings are functionally correct, when the relationship isn't goal-critical, or when a stronger cue (explicit labels, connecting lines, consistent treatment) overrides ambiguous proximity. When grouping ambiguity causes a specific wrong control to be chosen confidently, evaluate Inviting Dead End as co-occurring — this Trap is the root cause when fixing the spatial relationship dissolves the false invitation (fix-based rule).

**Detection procedure (pass one — flag, do not filter).** *Unit: per-screen; conceptual/IA form is cross-screen.*
1. From C2 goals, derive the expected association map: the element relationships the user must read correctly to proceed — label↔control mappings, option↔description pairings, group memberships, menu categorizations — including BOTH which elements SHOULD read as related AND which SHOULD read as unrelated. Steps 2–3 evaluate the design against this map in both directions: a true relationship the design fails to convey (missed association), and a false relationship it does convey (spurious association — the butterfly ballot's direction). A design where unrelated things also group has failed even if all related things group.
2. Evaluate the map against the FULL set of established Gestalt grouping principles, by name, including at minimum: proximity (related elements closer to each other than to competitors — the most commonly violated); similarity (same-function elements share visual properties; different-function elements don't mimic each other); common region (elements sharing a container read as related — flag unrelated elements in one container and related elements split across containers); uniform connectedness (elements joined by explicit connectors or sharing dividers read as related — misplaced dividers split siblings and weld strangers); continuity (alignment implies reading order); closure (implied containment reads as grouping); figure-ground (interactive elements read as figure). Common fate requires motion artifacts — declare on statics. Equidistance or nearer-to-unrelated = strongest flag. Flag violations in both directions per the step-1 map.
2b. Semantic grouping (independent axis): for every NAMED group — menu categories, tab sets, section headings, settings clusters — assess (i) internal coherence: do all members plausibly belong under the label as the C1 population reads it; (ii) assignment ambiguity: could a member reasonably be sought under a different existing category; (iii) label↔member fit: does the group name predict its contents. Flag semantic misgrouping even where visual grouping is flawless — perceptual and semantic grouping fail independently (the IA form; cross-screen unit).
3. Flag: controls equidistant between two plausible referents; labels nearer an unrelated element than their referent; conflicting Gestalt cues (proximity says one grouping, similarity another); IA form — menu items whose category membership a user could reasonably assign elsewhere.
4. Name the elements, the ambiguous relationship, AND the specific Gestalt principle violated per flag (G6) — a Poor Grouping flag that cannot cite a principle is not a flag; expected vs. actual grouping must both be stated.

**Disconfirmation (pass two).** NOT present when: (a) apparent groupings are functionally correct; (b) the relationship is not critical to the goal; (c) a stronger cue resolves the ambiguity; (d) conceptual groupings are obviously categorical.

**Severity.** Scales directly with the stakes of the action the grouping supports — from hesitation (Low) to confident wrong action at scale (the butterfly ballot altered a presidential election: High). Key property: users who misread a grouping act with confidence, not uncertainty. Escalators: C3 (time pressure and density worsen misreads).

**Assessability & Confidence.** High-confidence ceiling for measurable violations: a control measurably equidistant between competing options with no secondary disambiguation. Otherwise Medium confidence — whether users read the ambiguity wrongly is population/goal-relative; promotion path: task-based observation with grouping-dependent tasks. Context axis: C1 softens (learned conventions can disambiguate); C2 determines criticality.

**Attribution.** Inviting Dead End: confirm a specific wrong choice results, not mere unclarity. Information Overload: confirm excess density contributes — clutter is both cause and symptom; if removing excess resolves the grouping read, Information Overload is root cause (fix-based). Uncomprehended Element: individually clear elements confusing in combination attribute here.

**Report fragments.** Finding: "The spatial or conceptual relationship between [elements] is ambiguous — users are likely to misread which [control/label/option] corresponds to which [referent]." Why it matters: "Users who misread this relationship take the wrong action with confidence, not uncertainty."

**Remediation.** Apply Gestalt principles deliberately: related elements closer to each other than to any competitor; white space as an active grouping tool; explicit separators (lines, containers, color) where proximity alone is insufficient. For IA: categorize by users' mental models, verified by card-sort-style checks. Test with users unfamiliar with the system on grouping-dependent tasks.

---

### TRAP: FORCED SYNTAX *(ratified 2026-07-04)*
*Sub-tenet: Comprehensible*

**Definition.** The interface honors only one of several reasonable ways to sequence or express a task. Two sub-patterns:
- **A — Construction rigidity:** only one ordering of task steps is supported (object→action but not action→object; wake-word must precede command).
- **B — Expression rigidity:** input is accepted in only one exact format when multiple unambiguous formats exist (dates, phone numbers, currency, names with diacritics).

**Boundary.**
- IS: either sub-pattern, where at least one unsupported alternative is one users would reasonably expect or prefer.
- IS NOT **Gratuitous Redundancy** — mutually exclusive per task flow: only-one-construction = Forced Syntax; duplicate paths via the same construction = Gratuitous Redundancy. Confirm which is present before flagging either.
- IS NOT present when the task has a single dominant natural order virtually all users share, or when the fixed order is a genuine technical constraint.
- IS NOT an obligation to support every conceivable sequence: only reasonably likely alternatives count — for presence and for remediation.
- IS NOT **Captive Wait**: Forced Syntax imposes *order*; Captive Wait imposes *timing and exit* — a flow the user cannot back out of is Captive Wait even if its ordering is flexible.
- IS NOT **Unnecessary Step(s)**: if users must restart a flow because of the syntax constraint, confirm the extra steps are caused by the constraint, not separate flow design, before attributing.

**Detection procedure (pass one — flag, do not filter).** *Unit: sub-pattern B per-screen; sub-pattern A cross-screen (flow-level by nature).*
- Sub-pattern B (any artifact): (1) enumerate every free-input field; (2) record format signals — input masks, placeholder text prescribing an exact format, format-error messaging, character restrictions; (3) flag any field demanding a single encoding of information that has multiple common unambiguous encodings; name the field and the excluded encodings.
- Sub-pattern A (flow, prototype, live, or code artifacts): (1) state the task goal; enumerate the reasonable constructions (object→action, action→object, distinct entry points users would plausibly try); (2) walk the flow attempting each; record whether an entry point exists for it; (3) flag when exactly one construction is honored and at least one alternative is reasonably likely for this population.
- Sub-pattern A (static screenshot): flag as risk-only when a single rigid entry point is visible; label "needs flow or code to confirm alternative constructions."

**Disconfirmation (pass two).** NOT present when: (a) the sequence has a dominant natural order virtually all users expect for this task type; (b) the interface already provides the most common alternative construction; (c) the rigidity is a genuine technical constraint. Supporting every possible sequence is not required — only reasonably likely alternatives.

**Severity.** High when users abandon — assuming the function is unsupported or failing to find the supported sequence; Medium for reorganization friction. Anchor: the command accepted only wake-word-first — "Alexa, what time is it?" works, "What time is it, Alexa?" doesn't (card example): Medium — reorganization friction taxing every use. Voice-driven interfaces raise likelihood (natural speech has maximal grammatical flexibility). Escalators: C4 (a rigid construction in a daily task taxes every use); mixed novice/expert populations (C1) raise likelihood — the stages of skill acquisition construct tasks differently.

**Assessability & Confidence.** Sub-pattern B: High confidence from a static screenshot when masks/placeholders/error text are visible; fully confirmable live by probing accepted formats. Sub-pattern A: structurally High confidence from flows/code (which constructions exist), but whether unsupported alternatives are "reasonably expected" stays Medium confidence without C1 — promotion path: population data or user observation of attempted starting points. Context axis: C1 softens under its default (mainstream conventions); C2 identifies the tasks that matter.

**Attribution.** Mutual exclusivity with Gratuitous Redundancy (above). Unnecessary Step(s): independent confirmation before adding. Sequence routing map (author-ruled): (1) user doesn't know how to proceed, no expectation story → Invisible/Effectively Invisible/Uncomprehended Element per their boundaries, not this Trap. (2) User misses or misreads the entry point BECAUSE they are anchored at a different semantic starting point → bidirectional pair with the element Trap: supporting their natural start (this Trap's fix) dissolves the element problem; making the entry salient dissolves discovery but leaves the unnatural order — list both, note the bidirectionality, name the deciding check. (3) User notices, understands, and merely dislikes the required order → this Trap alone (the Alexa case). (4) User completes the sequence but cannot recall it later → this Trap (root cause), Memory Challenge (consequence, C4-gated): the recall burden exists because the required order is arbitrary relative to the user's mental model, and accepting their natural construction dissolves it. Memory Challenge stands alone only when the recalled content is intrinsically arbitrary (codes, passwords) — no syntax flexibility removes those.

**Report fragments.** Sub-A: "[Task] can be initiated only via [construction] — users who naturally approach it via [alternative] will find the interface unresponsive to their intent." Sub-B: "[Field] accepts only [format]; common valid encodings [list] are rejected." Why it matters: "Users who think differently from the assumed sequence must reorganize their approach before proceeding — friction, and abandonment risk if they conclude the capability is missing."

**Remediation.** Sub-A: identify all reasonable starting points and accept them; plan explicitly which tasks support object→action AND action→object; support only reasonably likely constructions. Sub-B: parse tolerantly — accept all common unambiguous encodings and normalize internally; reserve rejection for genuinely ambiguous input.

---

### TRAP: MEMORY CHALLENGE *(ratified 2026-07-04)*
*Sub-tenet: Comprehensible*

**Definition.** The user is required to remember information that is easy to forget: holding information across screens, recalling passwords/commands from long-term memory without a retrieval cue, executing multi-step processes by memory alone. Even carrying a small item from one screen to the next may be too much — short-term memory is tiny and volatile.

**Boundary.** IS: an unreasonable recall demand imposed by the design. IS NOT **System Amnesia**: that is the *system* failing to use information it was previously given; this is the *user* being made to remember. Both can co-occur (system has the data AND makes the user recall it) — then System Amnesia is root cause (fix-based: the system using its data removes the recall demand). IS NOT **Uncomprehended Element**: that is a knowledge gap (never learned); this is a recall gap (learned but unretrievable). With **Invisible Element**: a trained-but-forgotten invisible interaction is both — determine which is primary.

**Detection procedure (pass one — flag, do not filter).** *Unit: cross-screen by nature; per-screen for recall-without-cue fields.*
1. Walk each task flow; at every step, list what the user must hold in mind to proceed, retrieve from memory without a cue, or execute from memorized instructions.
2. Flag every context-boundary carry: information shown on one screen and needed on another (or another session/device) without being re-presented.
3. Flag recall-without-cue demands: fields requiring memorized identifiers, security answers without the question shown, command vocabularies with no visible reference (voice command lists are the canonical case).
4. Flag instruction sequences the user cannot keep visible while executing them.

**Disconfirmation (pass two).** NOT present when: (a) the information is genuinely easy to remember in context (own name; a daily-used PIN); (b) the task is recognition, not recall — information presented for selection; (c) the information stays available for reference during the task.

**Severity.** High when recall failure blocks the task with no recovery path; Medium when recovery is effortful. Anchor: the security answer demanded without its question shown (card example): High — recall failure blocks the task with no recovery short of a reset flow. Escalators: C3 — interruption, time pressure, and divided attention are precisely when held information evaporates; C4 — infrequent tasks (rare logins) maximize forgetting; spatially-presented information is markedly more memorable than verbal (mall-map principle).

**Assessability & Confidence.** High confidence when provided screens show both the source information AND the recall demand — the cross-boundary carry is visible without user testing. Recall-without-cue flows: High confidence-grade structural detection from flows/design files; whether the specific information is genuinely easy to forget stays Medium confidence without C1/C4 — promotion path: interaction-frequency data or observation. Scoped coverage (single statics): cross-boundary carries require multiple screens to observe — "assessed within scope: recall-without-cue demands visible on this screen; not assessable from this artifact: cross-screen and cross-session carries — flow artifacts would settle." Context axis: C4 (frequency) softens; C3 (interruption/pressure) sharpens severity.

**Attribution.** System Amnesia (above, fix-based). Invisible Element overlap (above). Forced Syntax adjacency (author-ruled): a required order that must be memorized is Forced Syntax (root cause) with this Trap as C4-gated consequence — the recall burden exists because the order is arbitrary relative to the user's mental model; accepting their natural construction dissolves it. This Trap stands alone only when the recalled content is intrinsically arbitrary (codes, passwords, security answers) — no syntax flexibility removes those. System Amnesia link: when the system's failure to retain imposes the recall burden, that Trap is root cause and this one the consequence.

**Report fragments.** Finding: "[Task/step] requires users to recall [information] without a retrieval cue, in a context where it is likely to be forgotten." Why it matters: "When users cannot recall this, they cannot complete the task — and may not know how to recover."

**Remediation.** Design for recognition over recall: let users see and choose rather than remember and enter. Present information spatially; chunk it; keep instructions visible during execution; provide retrieval cues (show the security question). The governing question: am I asking the user to remember this, or giving them a way to recognize it?

---

### TRAP: FEEDBACK FAILURE *(ratified 2026-07-04)*
*Sub-tenet: Confirmatory*

**Definition.** The system fails to communicate the consequence of the user's action, or how to resolve a failed action. Unlike other Traps, this one is defined by a *moment* — what happens after the user acts — not a single mechanism. Any failure that leaves the user without a clear understanding of what their action accomplished, or how to recover, qualifies. It is an additional lens: it exists to force evaluators to check whether the system closes the loop on every action, because feedback is foundational to how people learn an interface.

**Boundary.** IS: a broken action→response loop. When feedback EXISTS but fails, the root cause is another Trap and MUST be identified before this Trap is flagged: present but away from attention → Effectively Invisible Element; noticed but unclear → Uncomprehended Element; physically hard to perceive → Physical Challenge; too late → Slow or No Response; factually wrong → Incorrect Information; inconsistent across occasions → Variable Outcome. Report ONE issue with the root cause designated and Feedback Failure listed as the lens/consequence (G3). When NO feedback exists at all — the loop was never closed — this Trap stands alone as the finding: absence is its own core mechanism, no other Trap owns it, and the fix is simply to provide feedback (author-ruled 2026-07-04, superseding the manuscript's unconditional MUST — see Open Items 2). IS NOT present when the consequence is self-evident from the resulting state, or when silence is itself the designed, understood signal.

**Detection procedure (pass one — flag, do not filter).** *Unit: cross-screen — audits action→response pairs.*
1. Enumerate every user action in scope (taps, submissions, commands, toggles).
2. For each, record the system's response: what changes, where, when, and does it state what happened and — on failure — what to do now?
3. Flag: actions with no perceivable response; error messages that fail either question ("what went wrong?" / "what should I do?") — auditable without any user testing; feedback arriving after the user would have moved on; post-submission validation where continuous validation is feasible.
   *In-screen vs. post-action rule (partial artifacts):* feedback that should appear on the same screen immediately (button state, inline validation, loading indicator) is High confidence absent if not visible there; feedback that would arrive on a subsequent screen (toast, confirmation page) must NOT be asserted absent from a partial artifact — use conditional language ("if no confirmation exists elsewhere in this flow, users would have no indication the action completed") and route to the closer-look bucket per G8.
   Feedback scope includes surfacing hazards and consequential states the user needs to know about, not only confirming intended actions.
4. Route each flag to its candidate root cause per the Boundary list, as input to pass two.

**Disconfirmation (pass two).** NOT present when: (a) the consequence is self-evident from the resulting interface state; (b) absence of feedback is itself the meaningful, understood signal (silence = no error, by established convention); (c) the failure is fully attributed to a root-cause Trap — then that Trap is the finding and this one rides the trap line.

**Severity.** Medium for confusion/repeated attempts; High when users cannot recover from errors — anchor: the error message failing both questions, "Word did not save the document" (card example): High, the user can determine neither what went wrong nor what to do; High when absent feedback compounds an irreversible action or conceals a safety condition (play-space boundaries). Escalators: C3 (occupied channels can make otherwise-adequate feedback imperceptible — route to Physical Challenge/Effectively Invisible Element as root cause).

**Assessability & Confidence.** Error-message quality: High confidence from artifact (audit each message against the two questions). Absent responses: High confidence from flows/live/code (action→response pairs enumerable). Noticeability/comprehensibility of feedback: Medium confidence ceiling — inherits the root-cause Trap's profile. Not assessable for physical-feedback products from digital artifacts — declare.

**Attribution.** Root-cause routing is mandatory (Boundary).Irreversible Action interplay: when an action is irreversible AND nothing communicates what happened or how to recover, these are independent co-failures on one element — list both, NO root-cause designation (neither fix dissolves the other; co-occurrence without causation gets no designation, per G3). Remediation carries the ordering: support recovery first, then communicate it — recovery feedback without recovery is a false promise and would itself create an Inviting Dead End.

**Report fragments.** Finding: "When users [action], the system fails to communicate [what happened / what to do next] in a way that is [noticeable / comprehensible / timely / actionable]." Why it matters: "Without clear feedback, users cannot confirm success, recover from errors, or learn how the system responds."

**Remediation.** Every action produces a response that is immediate, clear, and sufficient. Error messages answer both questions. Prefer continuous real-time validation over post-submission. The fix depends entirely on the root cause — identify it first.

---

## TRAP CHUNKS — COMFORTABLE

### TRAP: PHYSICAL CHALLENGE *(ratified 2026-07-04)*
*Sub-tenet: —*

**Definition.** Some aspect of the system causes physical discomfort or makes it physically difficult or impossible to complete actions: touch targets too small to hit reliably, text too faint to read without strain, controls beyond comfortable reach, device forms too heavy or sharp to hold, audio too quiet for the environment, surfaces too hot, VR video jittery enough to induce queasiness. The user understands what to do; doing it costs strain, discomfort, or harm.

**Boundary.** IS: a physical demand exceeding the population's capabilities in the real context of use (C1 physical range + C3 channels). IS NOT **Accidental Activation** — its mirror image: this Trap makes intended actions too hard; that one makes unintended actions too easy; the fixes pull in opposite directions and each requires separate evidence. IS NOT present when the demand falls within established guidelines for the expected population and context, when difficulty is the point (dexterity games), or when it exists only under unrealistic test conditions. Systems that respond *too fast* for users to track or act on are also housed here (per the manuscript's FAQ — there is no separate "too fast" Trap).

**Detection procedure (pass one — flag, do not filter).** *Unit: per-screen for measurables; whole-artifact for form-factor properties.*
1. Flag any interactive target that appears small or crowded relative to whatever scale can be inferred from the artifact (standard platform elements, surrounding text, sibling controls). Physical size is not derivable from uncalibrated pixels, so apparent smallness is flagged conditionally, never measured (calibration-gated ceilings rule); where calibration IS provided, measure. The applicable standard is set by the input modality asserted in C3 — touch (~12 mm finger pad / platform minimums), mouse or other pointer (platform pointer minimums), remote, stylus, etc.; modality unstated: apply the declared C3 default and say so. Also flag tight spacing, and targets in hard-reach zones given the asserted C3 posture and grip (e.g., one-handed phone use — thumb-zone maps).
2. Measure text contrast against WCAG ratios and size against platform minimums at expected viewing distance; flag failures.
3. Enumerate channel demands and check each against C3: audio-dependent elements (flag if hearing may be unavailable), speech-required interactions (flag against speech/privacy constraints), two-handed or precision gestures (flag against hands/mobility), sustained-attention visuals (flag against motion).
4. Note form-factor properties not assessable from the artifact (weight, thermals, VR comfort) for the coverage notes rather than guessing.

**Disconfirmation (pass two).** NOT present when: (a) within established guidelines for the expected population and context; (b) difficulty is intentional and appropriate to the use case; (c) the difficulty exists only in test conditions that don't reflect real use.

**Severity.** Medium for targeting errors and legibility strain; High for exclusion — users who cannot complete actions at all (accessibility populations first); High for illness or injury (VR motion sickness, thermal harm). Anchor: lock-screen music controls below finger-pad size (card example): Medium — targeting errors and retry friction; High wherever undersized targets exclude users outright. Note the fluency effect: hard-to-read text doesn't just strain — users judge the *product* as harder and disengage (legibility is an engagement variable, not just an accessibility one). Escalators: C3 (a marginal target in motion or one-handed becomes a failure); C4 (strain on a core loop compounds).

**Assessability & Confidence.** Contrast ratio is pixel-derivable and eligible for High confidence from the artifact alone. Target size, spacing, and rendered text size are physical quantities: High confidence only with calibration (device class + resolution, or an in-artifact reference of known physical size); on uncalibrated artifacts the ceiling is Medium confidence, promotion path "measure on the target device against the applicable standard for the asserted input modality" — per the calibration-gated ceilings rule, and symmetrically for clearances (an uncalibrated artifact can neither confirm nor clear a size threshold). Reach findings from posture/grip assertions (C3) are likewise capped at Medium confidence; High confidence requires on-device testing. Not assessable from design files: weight, thermal, vestibular. Scoped coverage (always emitted, J27): "Physical Challenge — assessed within scope: apparent target size and spacing (conditional, uncalibrated), contrast, reach per asserted posture; not assessable from this artifact: motion/animation effects (incl. motion-sickness risk), weight, thermals, audio, haptics — on-device session would settle." Context axis: C3 is this Trap's primary input — its default (unencumbered, quiet, stationary) makes findings a lower bound and can gate presence outright (a hands-occupied context creates Traps a hands-free one lacks); C1 physical-capability range gates population-specific judgments (the general default assumes typical adult ranges — declare).

**Attribution.** Accidental Activation: opposite failure modes; evaluate together (enlarging targets to fix this Trap can create that one) but evidence separately. Feedback Failure: absent tactile/visual confirmation is that Trap's route (4) — confirm the perception difficulty independently.

**Report fragments.** Finding: "[Element/interaction] imposes a physical demand exceeding [guideline / comfortable reach / legibility threshold] for [population / context]." Why it matters: "Physical barriers cause errors and exclusion — and reduce users' perception of overall product quality independent of the specific difficulty."

**Remediation.** Follow established standards: minimum target sizes, WCAG contrast, platform reach-zone guidance. Prototype on real hardware in realistic conditions — design-file analysis flags candidates but cannot confirm most instances. Improving contrast removes a barrier AND measurably increases engagement. Caution: calibrate against Accidental Activation when enlarging or sensitizing anything.

---

### TRAP: ACCIDENTAL ACTIVATION *(ratified 2026-07-04)*
*Sub-tenet: —*

**Definition.** It's easy for the user to unintentionally trigger an action during normal use: controls at natural grip points, overloaded gestures, wake words overlapping ordinary speech, hair-trigger sensors.

**Boundary.** IS: insufficient physical/interaction barriers between normal use and unintended triggering, with NO intent inference involved (a button pressed accidentally is simply a button pressed). IS NOT **Bad Prediction**: when the system *interprets* an ambiguous signal as intent and guesses wrong (wake word in background conversation, gesture read from incidental movement), Bad Prediction is the root cause and the activation its consequence (fix-based: better prediction thresholds resolve it). IS NOT **Inviting Dead End**: that Trap lures a deliberate action; this one fails to prevent an undeliberate one. IS NOT **Physical Challenge** — mirror image; separate evidence each way. Reversibility of the triggered action reduces severity but does not disconfirm.

**Detection procedure (pass one — flag, do not filter).** *Unit: whole-artifact; requires device/form-factor context.*
1. Map controls against natural grip points, resting zones, and edge/corner contact areas for the device class; flag consequential controls located there.
2. Flag overloaded activations (double-tap, press-and-hold on grip surfaces), edge gestures adjacent to system gestures, and passive/sensor-based activations (proximity, motion, always-listening) — the last as candidates for Bad Prediction routing.
3. Flag hover-activated controls (menus, previews, tooltips-with-side-effects) positioned across common pointer paths — hover engagement during ordinary cursor travel is a static-detectable desktop case of this Trap.
4. For each flag, record the triggered action's consequence and reversibility (feeds severity).

**Disconfirmation (pass two).** NOT present when: (a) activation requires a deliberate, non-incidental action unlikely during normal handling; (b) the input vocabulary doesn't overlap natural behavior in the context of use (C3).

**Severity.** Scales with consequence × reversibility of the triggered action: accidental screenshot Low; accidental purchase High; accidental emergency call or recording High — for privacy/safety actions the acceptable false-trigger rate approaches zero. Anchor: the hand gesture read as a navigation swipe when the user scratched their ear (card example): Medium — unintended navigation, recoverable; the same false trigger on a purchase or recording action grades High. Escalators: C3 (motion, encumbrance, and pocketed/gripped carrying multiply incidental contact).

**Assessability & Confidence.** Medium confidence ceiling from design files (placement vs. known grip zones flags candidates); actual activation behavior requires hardware testing — promotion path: realistic-use hardware trials. Context axis: C3 gates (grip, mobility, environment determine what "normal use" contacts); device class knowledge required — declare when absent.

**Attribution.** Bad Prediction routing (Boundary). Variable Outcome: overloaded controls whose outcome depends on unattended state make accidents worse — consistency is the root cause there; evidence separately.

**Report fragments.** Finding: "[Control/gesture] is positioned or configured so unintentional triggering is likely during normal use." Why it matters: "Accidental activations resist user care — severity scales with the reversibility and consequence of what fires."

**Remediation.** Add friction to the activation path: recess or shield controls, require sequential actions, add resistance, increase gesture distinctiveness. Confirmation dialogs are a last resort — they tax every intentional user (Unnecessary Step(s)); reserve for consequential AND irreversible actions after physical options are exhausted. Caution: friction added here can worsen Physical Challenge — calibrate together.

---

## TRAP CHUNKS — RESPONSIVE

### TRAP: SLOW OR NO RESPONSE *(ratified 2026-07-04)*

**Definition.** The actual or perceived time the system takes to respond exceeds what the user wants or expects. Anchored to psychophysical thresholds: continuous actions (ink, AR/VR tracking) 0–10 ms; discrete actions (tap, click, scroll) ≤100 ms feels instantaneous, >1 s disruptive, >10 s attention abandons; conversational turns ≤1 s (human gaps average ~250 ms). Perceived duration is separately designable: unoccupied waits feel 1.4–1.8× longer; uncertain and unexplained waits feel longer.

**Boundary.** IS: response beyond threshold for the interaction type, OR within bounds but *feeling* slow due to absent/poor progress design. IS NOT **Captive Wait**: that Trap is about denied *control* (can't advance or exit); this is about *speed*. IS NOT present when deliberate pacing serves comprehension (transition animations that show what happened) or when a small delay corrects a too-fast response. Too-fast failures route by what the speed defeats: defeats acting (timing windows, targets expiring before they can be hit) → Physical Challenge; defeats noticing (state changes too brief to register) → Feedback Failure as the entry lens; its routing map designates the root (too-brief perceivable feedback → Physical Challenge root, FF as lens); defeats reading or using (content withdrawn before the user chose to move on) → Captive Wait; defeats comprehending (transitions too fast to parse) → Uncomprehended Element.

**Detection procedure (pass one — flag, do not filter).** *Unit: per-interaction; live artifacts strongly preferred.*
1. For live/instrumented artifacts: measure response times per significant interaction; flag every threshold violation by interaction type.
2. For all artifacts: audit wait-state design — flag any operation >1 s without continuous progress feedback; any >10 s with no occupied-time treatment (skeleton screens, background continuation); progress indicators that jump discretely or stall.
3. For static artifacts: response times are not assessable — declare; wait-state *design* (presence/quality of progress feedback in mocked states) remains flaggable. Scoped coverage (always emitted on statics, J27): "Slow or No Response — assessed within scope: wait-state design; not assessable from this artifact: actual response times — live session or screen recording would settle."

**Disconfirmation (pass two).** NOT present when: (a) within thresholds AND longer operations carry well-designed progress feedback; (b) deliberate pacing serves comprehension; (c) delay is corrective for a too-fast response.

**Severity.** Medium for perceptible-but-tolerated delays; High at abandonment thresholds (>10 s undisclosed) and for conversational products beyond 1 s (users attribute rudeness/unintelligence). Anchor: a flashlight app taking up to five seconds to light (card example): High — the tool's entire value is immediacy; users judge it broken and abandon. High for AR/VR tracking lag (motion sickness → Physical Challenge co-listing). Escalators: C4 (latency in a core loop taxes every use).

**Assessability & Confidence.** High confidence for measured times against thresholds (among the most automatable checks — live artifacts, instrumented artifacts, and screen recordings, which carry genuine timing at frame-rate precision). Medium confidence for perceived slowness from design review; promotion path: measurement, or observation of repeat-actions/frustration signals. Context axis: C2 (expectations vary by task stakes); C1 (population norms for the product category shape expectations).

**Attribution.** Feedback Failure: a slow system WITH good progress feedback has this Trap only; absent progress indication is that Trap co-occurring — separate evidence. Peak-end note for remediation prioritization: ends dominate memory; fix trailing slowness first.

**Report fragments.** Finding: "[Interaction] takes [duration] — exceeding the [threshold] for its type / with no progress indication during the wait." Why it matters: "Beyond perception thresholds users repeat actions, abandon tasks, or lose confidence their input registered."

**Remediation.** Immediate receipt confirmation under 100 ms even when the full response lags; continuous progress feedback beyond 1 s; never a static screen. Occupied-time techniques (skeletons, progressive loading, background continuation); pre-fetch so waits start before users mark time; make progress accelerate toward completion (peak-end). Improve actual speed in ≥20% increments to be felt — and beware the reverse: successive regressions each below ~20% are individually imperceptible and are how products rot; guard with instrumented latency budgets.

---

### TRAP: CAPTIVE WAIT *(ratified 2026-07-04)*

**Definition.** The system does not allow the user to advance or back out of a process at a time of their choosing: unskippable pre-roll ads and cutscenes, updates that commandeer the device, locked flows. Frustration is disproportionate to time cost because the violation is of *control*, not speed.

**Boundary.** Scope is bidirectional: control over WHEN is denied whether the user is held past their choosing (cannot advance or exit) or dragged before it (auto-advancing/auto-dismissing content) — \"at a time of their choosing\" covers both directions. IS: denied ability to advance, skip, or exit. IS NOT **Slow or No Response** (speed, not control) — a captive wait can be short and still this Trap. IS NOT **Forced Syntax** (order, not exit). NOT present when the wait is skippable, when duration is disclosed and reasonable for a purpose users accept, or when technically unavoidable AND pre-announced with an accurate estimate AND the limitation is one users find reasonable.

**Detection procedure (pass one — flag, do not filter).** *Unit: cross-screen (flow states).*
1. Walk every flow; at each state, test: can the user advance at will? back out? skip? Flag every state where all three fail.
2. Flag auto-advancing/auto-dismissing screens that deny reading-pace control.
3. For each flag, record: duration, disclosure of duration, skip affordance and when it appears, and whether the captive content serves the user's goal or the business's.
4. Attend especially to onboarding, setup, updates, and ad placements.

**Disconfirmation (pass two).** NOT present when: (a) skippable (even after a brief mandatory period); (b) duration disclosed and judged reasonable for the purpose; (c) technically unavoidable + advance notice + accurate estimate + reasonable limitation.

**Severity.** Medium typically — anchor: the unskippable advertisement before requested content (card example): Medium, escalating hard on C4, every session pays it — and escalates on repetition (C4: an unskippable ad on every session compounds) and when users are in active goal pursuit rather than passive browsing; High when captivity blocks time-sensitive goals or forces abandonment. Undisclosed duration compounds (uncertain waits feel longer — route the missing disclosure to Feedback Failure as co-occurring).

**Assessability & Confidence.** High confidence from flows/live/code (locked states and missing skip paths are structural). Static screenshots: not assessable beyond visible skip affordances — declare. Context axis: C2 gates the goal-service judgment; C4 sharpens severity via repetition.

**Attribution.** Feedback Failure: confirm independently that duration/purpose are undisclosed — disclosure reduces severity without dissolving the Trap. Business-driven captivity (forced ad exposure) flags as potential dark pattern, per the Distraction precedent.

**Report fragments.** Finding: "[Flow/screen] prevents advancing or backing out for [duration/unknown], without [skip / disclosure / service to the user's goal]." Why it matters: "Perceived control shapes experience independent of duration — captivity generates frustration disproportionate to its time cost."

**Remediation.** Question every no-exit point. Make content skippable as fast as possible; disclose duration upfront; for system processes give advance notice, allow parallel work, notify on completion; anything >10 s needs a stop or background option. Prefer progressive disclosure over mandatory flows.

---

## TRAP CHUNKS — EFFICIENT

### TRAP: UNNECESSARY STEP(S) *(ratified 2026-07-04)*

**Definition.** The number of steps to achieve a goal exceeds what it needs to be: steps that could be eliminated, automated, or combined without loss. The target is the *right* number, not the minimum — steps that make an experience more understandable (wizard vs. one dense screen) are a legitimate trade.

**Boundary.** IS: eliminable/automatable/combinable steps. IS NOT present when a step serves a documented legitimate purpose: confirmation for consequential irreversible actions; cognitive-load chunking; security/legal/safety requirements. Confirmation dialogs on *reversible* actions are this Trap by definition (reversibility makes them pure cost). IS NOT **Forced Syntax** (wrong order vs. too many). Caused by **Gratuitous Redundancy** when duplicates displace content into scrolling — confirm displacement independently.

**Detection procedure (pass one — flag, do not filter).** *Unit: cross-screen (flows).*
1. Walk each C2 task flow end to end; count steps; for each ask: eliminable? automatable? combinable?
2. Flag: confirmation dialogs (check reversibility of the confirmed action — reversible = automatic flag); per-field confirmations; navigation depth (levels descended to reach frequent functions — hamburger-nested high-frequency actions are the canonical case); re-entry of derivable information; round-trips between choice and outcome views (missing previews).
3. Flag forced prerequisite gates: the artifact shows users must complete a prerequisite (authentication, registration, paywall, mandatory consent) before reaching core functionality, AND either (a) the core function does not technically require it, or (b) a guest/unauthenticated path would reasonably serve the stated goal. Do NOT classify a gated path as Invisible Element — the path is blocked, not hidden.

**Disconfirmation (pass two).** NOT present when: (a) the step serves a legitimate documented purpose; (b) it chunks complexity for comprehension; (c) security/legal/safety requires it.

**Severity.** Medium baseline (friction); escalates hard on C4 — extra steps on high-frequency tasks are paid on every use. Anchor: the hamburger menu hiding primary navigation behind an extra tap (card example): Medium — one added step, paid on every navigation act; its removal (Spotify's nav-flattening) produced large engagement gains; High when cumulative cost drives abandonment.

**Assessability & Confidence.** High confidence for confirmation-on-reversible (structural); step counts High confidence from flows; whether a step is *genuinely* unnecessary stays Medium confidence without C2 purpose knowledge — promotion path: task analysis with the team. Context axis: C2 gates necessity judgments; C4 drives severity.

**Attribution.** Gratuitous Redundancy as root cause (displacement — confirm independently). Irreversible Action: confirm irreversibility before condemning a confirmation; the superior fix is usually reversibility, which removes both the risk and the step (fix-based pairing).

**Report fragments.** Finding: "[Task] requires [N] steps; [which] could be eliminated, automated, or combined without loss." Why it matters: "Every unnecessary step is a cost paid on every use — compounding across frequency into significant lost efficiency."

**Remediation.** Surface high-frequency functions to persistent navigation; provide hierarchy-cutting paths (search, command, voice); replace confirmations with reversibility; preview outcomes to kill round-trips; audit accreted flows end to end.

---

### TRAP: INFORMATION OVERLOAD *(ratified 2026-07-04)*

**Definition.** Information presented is understandable but exceeds what is needed: verbose instructions, wordy AI responses, cluttered displays, option-dense menus. Hick's Law prices it: decision time grows with choice count. The test is not "could there be less?" but "does the user need all of this right now?"

**Boundary.** IS: excess relative to the user's goal in this context. IS NOT present when the density is the task (data dashboards for comprehensive sensemaking), when everything shown is needed now, or when progressive disclosure is functioning. IS NOT **Distraction** (specific capture vs. diffuse excess — shared fix, separate evidence). Caused by **Gratuitous Redundancy** when duplicates inflate the count — confirm duplication independently; density alone can come from feature breadth or poor editing.

**Detection procedure (pass one — flag, do not filter).** *Unit: per-screen; menus/IA cross-screen.*
1. From the C2 goal, partition each screen's content: serves the likely goal now / secondary / serves no evident user goal.
2. Flag screens where the primary task requires processing only a small subset of what's displayed; count elements, options per decision point, and word counts of instructions/labels/errors against a plain-necessity read.
3. Flag verbosity per text element: could it shed half its words without losing clarity (the Krug test)?
4. Strongest static trigger — task burial: the primary action or call-to-action is buried within or beneath large text masses, or is not reachable without scrolling past content that does not serve the goal. Task burial is this Trap's clearest screenshot-grade evidence.
5. Homepages, dashboards, and navigation earn the closest read — accretion concentrates there.

**Disconfirmation (pass two).** NOT present when: (a) all of it is needed for the goal right now; (b) density is appropriate to comprehensive-sensemaking tasks; (c) progressive disclosure already gates the secondary tier.

**Severity.** Medium baseline (processing tax, Hick's-slowed decisions); High when the information cost exceeds motivation and users abandon. Anchor: the dealer locator preceded by a seven-step instruction block (card example): Medium — comprehensible but burying the single field it explains; the eventual fix was one field and a button. Escalators: C4 (a cluttered daily screen taxes forever); C3 (divided attention shrinks processing budget). Expert populations (C1) can legitimately need more — soften accordingly.

**Assessability & Confidence.** Medium confidence ceiling — counts and densities measure High confidence-grade, but necessity is goal-relative (C2 gates); promotion path: user task analysis or engagement data. Context axis: C2 gates; C1 softens for expert tools.

**Attribution.** Gratuitous Redundancy root cause when duplication inflates (confirm). Distraction co-occurring when specific elements also capture attention (separate evidence). Poor Grouping compounding: clutter obscures relationships — if decluttering restores the grouping read, this Trap is root cause (fix-based).

**Report fragments.** Finding: "[Screen] presents substantially more information than [goal] requires — [N elements / options / words] where [fewer] would serve." Why it matters: "Every element beyond what the goal requires taxes attention and decision speed on every use."

**Remediation.** Build outward from the likeliest goal; every element must earn its place. Progressive disclosure for the secondary tier. Cut text aggressively — get a professional writer. Fewer options per decision point. Audit regularly; interfaces accrete.

---

### TRAP: SYSTEM AMNESIA *(ratified 2026-07-04)*

**Definition.** The system fails to take advantage of the user's prior work, preferences, or context: re-entering known information, recommendations ignoring ownership or history, context lost between sessions, re-authentication of the already-authenticated. Either the system never collected what it was exposed to, or collected it and doesn't use it.

**Boundary.** IS: the *system's* failure to leverage what it had. IS NOT **Memory Challenge** (the *user* made to remember) — both together (system has it AND user must recall it) make System Amnesia root cause (fix-based). IS NOT **Data Loss** (failing to *retain* what the user expects preserved vs. failing to *use* what it has). NOT present when re-prompting serves deliberate security/verification (though confirm-and-edit beats full re-entry even there), when architecture genuinely lacks access (verify it's actual, not assumed), or when the information may have changed (same superior pattern applies).

**Detection procedure (pass one — flag, do not filter).** *Unit: cross-screen/cross-session by nature.*
1. Inventory every point where the user supplies information or exhibits trackable behavior; then flag every later point that requests or ignores the same thing: repeated form fields, criteria re-stated, ownership-blind promotions, context dropped across sessions.
2. Strongest flag — self-evidencing amnesia: the system *displays* information while simultaneously requesting it, or comments on an action in a way proving it didn't register it (selling the user what the same screen shows they own; a machine asking if you knew it takes credit cards while processing your credit card).
3. Live/multi-session artifacts: probe cross-session recall (resume point, preferences, exclusions).

**Disconfirmation (pass two).** NOT present when: (a) deliberate security/verification re-prompting (still note confirm-and-edit as superior); (b) genuine architectural inaccessibility (verified); (c) plausibly-changed information (same note).

**Severity.** Medium baseline (friction, "not paying attention" perception — which directly undermines any personalization claim the product makes); grade upward by recreation cost — the volume of work recreated, the recall difficulty of the recreated information, and the error stakes of recreating it wrong; High when substantial or high-stakes prior work must be recreated (the doctor's-office intake form is the anchor case: months between sessions, maximal severity). Escalators: C4 (recurring re-entry compounds, whether within one session or across visits years apart). Proximity of the original entry does not grade severity. Attribution note: when the recreated information is itself hard to remember, Memory Challenge co-occurs as a consequence — the system's failure to retain imposes the recall burden (this Trap root cause, Memory Challenge consequence).

**Assessability & Confidence.** High confidence for self-evidencing cases (single screen suffices). Otherwise Medium confidence — knowing what the system *has* requires data-architecture knowledge or session history; promotion path: architecture review or multi-session probe. Context axis: largely context-free structurally; C2 sharpens severity (critical-path re-entry).

**Attribution.** Bad Prediction downstream: poor retention makes poor predictions — confirm both (available-but-unused data AND bad predictions) before chaining, System Amnesia as root cause. Memory Challenge pairing (above). Unwanted Disclosure tension: fixing amnesia means retaining data — remediation must note the security obligation.

**Report fragments.** Finding: "[Flow] requests [information] the system already has — or displays evidence it hasn't tracked prior behavior." Why it matters: "Re-asking for what it knows signals the system isn't paying attention — friction now, and erosion of every personalization claim the product makes."

**Remediation.** Retention by default: information provided once is available at every subsequent point. Share data across product contexts. Exclude owned/engaged content from recommendations. For AI systems, design cross-session memory deliberately. Governing question: could the system reasonably be expected to retain this? If yes, it should — and secure it (see Unwanted Disclosure).

---

## TRAP CHUNKS — ACCURATE

### TRAP: INCORRECT INFORMATION *(ratified 2026-07-04)*

**Definition.** Information presented to the user is factually wrong, distorted, incomplete, out-of-date, or contains errors: inaccuracies, hallucinations, algorithmically biased content, deliberate misleading, down to typos. Its signature danger: unlike most Traps it produces no friction — users act on it in good faith and discover the wrongness late or never.

**Boundary.** IS NOT presentational inconsistency — the same element or signifier varying in style, location, or presence across times or places routes to the Habituating Traps (Inconsistent Appearance, Wandering Element, Variable Outcome). This Trap requires informational content that is wrong: route here when two claims cannot both be true, since at least one must then be false — internal contradiction is this Trap's cheapest static evidence, not the Habituating family's (author-ruled 2026-07-06).  IS: content presented as fact that is wrong (by external fact, internal contradiction, or staleness). IS NOT **Bad Prediction** — two tie-breakers, applied together: (1) *did the user ask for this?* Hard-coded or requested content that is wrong → this Trap only; unrequested proactive content → Bad Prediction; if also factually wrong → both. (2) *would this content be wrong for a user with completely different goals?* Wrong for any user regardless of goals → this Trap; wrong only for THIS user → Bad Prediction. Recommendation rows, surfaced content, and personalization results that are wrong for the stated user are always Bad Prediction, never this Trap. IS NOT present when content carries source attribution and honest uncertainty indicators, when it was accurate and a freshness mechanism exists, or when "incorrect" is really preference disagreement. Root cause of **Inviting Dead End** when wrong content marks a wrong path as right (mislabeled button, outdated instructions) — correct the information first; a merely-confusable element with no factual error is that Trap alone.

**Detection procedure (pass one — flag, do not filter).** *Unit: per-screen + cross-screen consistency.*
1. **Internal-contradiction sweep (strongest artifact-native check):** totals vs. their line items; labels vs. adjacent charts/data; counts vs. visible items; instructions referencing elements/pages that don't exist in the artifact; cross-screen statements that conflict.
2. Staleness sweep: dates, prices, version references, "current" claims with no freshness mechanism; flag time-sensitive content lacking one.
3. Provenance sweep: AI-generated or algorithmic content presented as fact without labeling, attribution, or uncertainty indicators — flag structurally regardless of truth value.
4. External-fact spot checks only where verifiable against authoritative sources within the analysis; otherwise record as not-assessable rather than guessing.

**Disconfirmation (pass two).** NOT present when: (a) attributed and presented with appropriate uncertainty — the Trap targets information presented *as fact*; (b) accurate-at-the-time with a live freshness mechanism; (c) the dispute is preference, not fact; (d) the content is placeholder (lorem ipsum, grey-box images, stub copy) and the submitter's context states the design is a draft — a known unfilled slot is not a factual claim; skip this Trap for such content.

**Severity.** Scales with domain stakes and the user's likely action taken in good faith: Low for trivial errors; High for financial, health, navigational, legal content acted upon; High when acted-upon wrongness is irreversible (the hallucinated-case sanctions). Confident presentation of uncertain information is itself the failure — users cannot calibrate trust without external verification, making accuracy an ethical obligation, not just a quality bar.

**Assessability & Confidence.** High confidence for internal contradictions — the artifact convicts itself; this is the analyzer's native strength on this Trap. High confidence for structural provenance failures (unlabeled AI content, missing attribution on factual claims). External factual accuracy: Medium confidence at best, usually not-assessable without verification — declare rather than fact-check beyond reach. Scoped coverage (always emitted where external claims exist): "Incorrect Information — assessed within scope: internal consistency, staleness structure, provenance labeling; not assessable from this artifact: external factual accuracy — verification against authoritative sources would settle." Context axis: C2 sharpens severity (what will the user *do* with this?); largely population-independent otherwise.

**Attribution.** Inviting Dead End downstream (above; fix-based — correcting the information dissolves the dead end). Bad Prediction (the did-they-ask test; both when unrequested AND wrong). Feedback Failure route (6): wrong progress/status feedback lands here as root cause.

**Report fragments.** Finding: "[Feature] presents [information] as fact that is [internally contradicted by X / stale with no freshness mechanism / unattributed machine output], in a domain where acting on it could [consequence]." Why it matters: "Users cannot calibrate trust in an interface's outputs without external verification — accuracy is an ethical and, in high-stakes domains, legal obligation."

**Remediation.** Document source, verification process, and freshness mechanism for every factual claim. Label AI-generated content and cite sources users can check. Highest verification standard plus clearest limitation disclosure for health/finance/safety/legal. Surface uncertainty rather than hide it — confident presentation of uncertain information is a design failure.

---

### TRAP: BAD PREDICTION *(ratified 2026-07-04)*

**Definition.** The system fails in its attempt to anticipate the user's intent, preference, or context — it guesses wrong: autocorrect errors, irrelevant recommendations, ill-timed suggestions, proactive automation misfires. The user understands what the system did; they just didn't want it. The evaluation is economic: a 10%-wrong autocomplete can be net-positive; a 10%-wrong auto-*sender* cannot — acting demands a far higher accuracy bar than suggesting.

**Boundary.** IS: unwelcome proactive behavior from probabilistic intent inference. Two gate questions: *did the user ask for this?* and *would it be wrong for a user with completely different goals?* — content wrong only for THIS user is this Trap; content wrong for any user is Incorrect Information. IS NOT **Incorrect Information** (requested/hard-coded wrong content; both apply when unrequested AND universally wrong). Root cause of **Accidental Activation** when the system *interprets* ambiguity as intent (wake-word false positives); of **Distraction** (irrelevant interruptions); of **Unwanted Disclosure** (misjudged context surfacing private content); of **Unnecessary Step(s)** (undo/work-around burden) — each downstream effect requires its own evidence before chaining. Sometimes caused by **System Amnesia** (unused available context → worse guesses; confirm both).

**Detection procedure (pass one — flag, do not filter).** *Unit: whole-artifact feature inventory.*
1. Inventory every predictive/proactive feature: autocomplete/correct, recommendations, auto-actions, sensor-triggered behaviors, "helpful" interjections.
2. For each, record: does it *act* or *suggest*? Is a wrong guess dismissible at near-zero cost, or does it require undoing? Is the acted-upon outcome reversible? What signals feed it (rich context vs. ambiguous single sensor)?
3. Flag structurally (no accuracy data needed): any feature that ACTS on a prediction whose wrong outcome is irreversible or privacy/safety-relevant — the acting-threshold is unmet regardless of hit rate; any prediction requiring meaningful effort to dismiss or undo.
4. When user context (C1/C2) is stated: flag surfaced content, recommendations, or defaults that visibly contradict the stated user's demographics, goals, or tasks — this is static-screenshot detectable, and objective contradictions reach High confidence without usage data.
5. Flag proactively surfaced content that occludes content the user is actively attending to (hover covers, overlay suggestions) — the system's guess about what helps is overriding what the user chose to attend to.
6. With usage/observation data: flag features whose correction cost exceeds their saving.

**Disconfirmation (pass two).** NOT present when: (a) the prediction economy is net-positive AND error cost is trivial; (b) wrong guesses dismiss themselves without disruption or effort.

**Severity.** Low for dismissible suggestions (residual cost: occupied space that pushes relevant content away); Medium–High for embarrassment/social harm and effortful workarounds — anchor: autocorrect rewriting a sent message (card example): Medium–High, social harm, effortful correction, and the message is already delivered; High for irreversible or safety/privacy misfires (false 911, unconsented recording). Escalators: C3 (ambient/shared contexts raise disclosure stakes); C4 (a daily-loop misprediction compounds).

**Assessability & Confidence.** High confidence for the structural act-vs-consequence flags (feature design convicts itself). Actual accuracy: not assessable without usage data — declare; promotion path: observation of hesitation/correction/frustration after system-initiated actions. Scoped coverage: "Bad Prediction — assessed within scope: act-vs-suggest structure, dismissal cost, stated-context contradictions; not assessable from this artifact: prediction accuracy — usage observation would settle." Context axis: C2 gates welcomeness (the same suggestion is welcome or painful by moment); C1/C3 shape it.

**Attribution.** Downstream chains per Boundary — each independently evidenced, this Trap as root cause where the fix (predict-when-certain, or suggest-don't-act) dissolves them. System Amnesia upstream (confirm available-but-unused context).

**Report fragments.** Finding: "[Feature] acts on [prediction] where a wrong guess is [irreversible / privacy-relevant / costly to undo] — requiring users to work around the system's guesses rather than benefit from them." Why it matters: "A prediction costing more to correct than it saves is a net negative — and wrong guesses in irreversible contexts cause harm that cannot be undone."

**Remediation.** Predict when certain. Acting requires a far higher bar than suggesting: where wrong-guess consequence is significant and reversal hard, suggest — and make dismissal free. Where accuracy can't be verified, default to inaction. Feed predictions with retained context (fix System Amnesia first where it's the cause).

---

## TRAP CHUNKS — PROTECTIVE

### TRAP: IRREVERSIBLE ACTION *(ratified 2026-07-04)*

**Definition.** The user cannot backtrack or undo an action they have taken — a purchase that can't cancel, a message that can't recall, a file that can't restore. The Trap applies when recovery is *possible but unsupported* (Instagram's 30-day restore was always feasible; it simply hadn't been designed). Genuinely unavoidable real-world irreversibility (processed payment, delivered-and-read message) is scoped out — but a time-limited recovery window often exists even there.

**Boundary.** IS: unsupported-but-feasible recovery. NOT present when: irreversibility is genuine AND a *non-habituating* confirmation guards it (typed phrase, not a clickable dialog — users auto-dismiss standard dialogs); irreversibility is the intended, understood, desired outcome (permanent deletion of a sensitive file — then complicate the confirmation); a time-limited recovery window exists. A standard confirmation dialog alone does NOT disconfirm. Root cause of **Data Loss** when the unrecoverable action destroys work (reversibility fixes both — fix-based). Pairs against **Unnecessary Step(s)**: confirmations are usually a symptom; reversibility removes the risk AND the step. **Inviting Dead End** upstream when a misleading element led into the irreversible act (Reserve that means Purchase) — that Trap is root cause of the *entry*; this one owns the *no-exit*.

**Detection procedure (pass one — flag, do not filter).** *Unit: cross-screen (flows/code).*
1. Walk every consequential action in scope; for each ask: is there undo? a recovery window? a back path that truly restores prior state?
2. Flag every consequential action with none of the three; record what guards it instead (nothing / standard dialog / non-habituating confirmation).
3. Flag commitment-understating labels on irreversible actions (Reserve→Purchase) as co-candidates for Inviting Dead End.
4. Flag existing confirmation dialogs for the reversibility-instead question (feeds Unnecessary Step(s)).

**Disconfirmation (pass two).** Per Boundary (a)–(c).

**Severity.** Scales with stakes: Low for trivial unrecoverable acts; High for consequential purchases/deletions; High for real-world irreversible harm (flight purchased, legal filing, safety actions). Anchor: the Reserve-that-purchases flight (card example): High — consequential purchase, no undo, label understating commitment. Likelihood risers: the action is reachable in fewer steps than its weight suggests; labels understate commitment; time pressure (C3).

**Assessability & Confidence.** Medium confidence from flows/design (absence of visible undo is structural; whether recovery is *technically feasible* needs architecture knowledge) — promotion path: technical/architecture review (hours, not users). Static single screens: largely not assessable — undo affordances and recovery windows are flow properties; declare "Not assessable from this artifact — flow or code would settle." High confidence from code showing no recovery path for a feasible one. Context axis: C2 sharpens stakes; C3 (pressure) raises likelihood.

**Attribution.** Data Loss pairing (fix-based, above). Unnecessary Step(s) pairing (reversibility beats confirmation). Inviting Dead End entry (above). Bad Prediction note: proactive error-prevention prompts ("send without attachment?") are predictions — hold them to predict-when-certain.

**Report fragments.** Finding: "[Action] cannot be undone; no recovery mechanism (undo, time-limited window, or non-habituating confirmation) exists." Why it matters: "Users who act unintentionally or under misapprehension have no path back — the cost of the error is permanent."

**Remediation.** Design forwards and backwards: for every consequential action, what does a user who changed their mind do? Reversibility over confirmation — it removes the risk and the step. Where truly irreversible: time-limited recovery window if feasible; else a non-habituating confirmation (typed phrase). Hazard note: typed-phrase confirmations trade friction for safety — reserve them for genuinely irreversible, high-stakes acts, or they become Unnecessary Step(s). Proactively prevent where prediction is certain.

---

### TRAP: UNWANTED DISCLOSURE *(ratified 2026-07-04)*

**Definition.** The system exposes personal data or behavior in a way that is harmful, embarrassing, or unexpected. Two dimensions: *remote/digital* (data shared to third parties, opt-out defaults, location surfacing, history visible to household members) and *physical/real-time* (a notification read aloud in a crowded room, sensitive content on a visible screen, unsilenceable sounds). The governing test is contextual integrity: not "is this data secret?" but "does this flow match what the user would expect given the context in which they shared it?"

**Boundary.** IS: any communication of user data/behavior the user did not intend, by either dimension. NOT present when: explicit, fully-informed consent covers what/when/whom; disclosure is to the user themselves in a private context; data is aggregated and anonymized beyond individual identifiability. Caused by **Bad Prediction** when a context misjudgment surfaces private content (confirm the prediction error). Co-occurs with **Feedback Failure** when sharing happens *undisclosed* (disclosed-but-unwanted lacks that co-Trap). Deliberate business-driven over-sharing (opt-out defaults, opaque collection) flags additionally as potential dark pattern.

**Detection procedure (pass one — flag, do not filter).** *Unit: whole-artifact + settings audit.*
1. Trace every feature that collects, stores, or surfaces user data; for each flow ask: would the user expect this destination, given where they shared it?
2. Audit defaults: flag every opt-out (rather than opt-in) sharing default, with sensitivity class (location, health, finance, behavior = highest).
3. Physical-dimension sweep against C3: flag audio announcements of content, always-visible sensitive surfaces on shared/ambient devices, unsilenceable sounds — any output the user cannot gate in social contexts.
4. Flag exports, saves, and shares that bundle more than users would expect — e.g., a saved meeting chat log that silently includes private messages; the expectation is set by what the user thinks they are sharing, not by what the feature technically captures.
5. Flag consent asked at moments the user can't understand what they're consenting to.

**Disconfirmation (pass two).** Per Boundary (a)–(c).

**Severity.** High baseline for sensitive categories (health, location, finance, sexuality) — inherently high-consequence; High when disclosure is irreversible and harmful (irreversibility is the norm for disclosure — what varies is the harm branch; grade by it); Medium for social embarrassment (spoiled gifts — which still drove users to competitors). Anchor: the partner-site purchase feed (card example): embarrassment-grade harm, Medium by harm branch — yet irreversible, and it drove a class action and feature shutdown; harm-branch grading is not a reason to under-weigh business risk in the description. Escalators: C3 (shared/ambient devices, public contexts).

**Assessability & Confidence.** High confidence for structural findings: opt-out defaults on sensitive data, ungated audio output of content (artifact/settings suffice). Whether a specific flow violates expectations: Medium confidence, gated by C3 social context — promotion path: context-of-use inquiry. Static single screens: the settings/defaults audit is not assessable — declare "Not assessable from this artifact — settings audit or flows would settle"; physical-dimension flags (visible sensitive surfaces, audio indicators) remain assessable. Context axis: C3 is primary (the privacy clause exists for this Trap); C1 norms shape expectation.

**Attribution.** Bad Prediction upstream (confirm). Feedback Failure co-occurrence (undisclosed sharing). System Amnesia tension: its remediation (retain more) raises this Trap's stakes — cross-note both ways.

**Report fragments.** Finding: "[Feature/setting] shares [data] with [audience] on an opt-out basis / in a context where users are unlikely to expect or intend it." Why it matters: "Users cannot prevent disclosures they don't know about — consequences run from embarrassment to legal liability, and disclosure cannot be undone."

**Remediation.** Defaults must match what fully-informed users would choose. Explicit opt-in for sensitive behavioral data; consent at moments of genuine understanding. For ambient/shared devices: granular control over what surfaces, when, and through which channel. Ask of every collection point: where could this surface, and would the user accept that?

---

### TRAP: DATA LOSS *(ratified 2026-07-04)*

**Definition.** The system fails to retain information or content the user expects to be preserved: work lost to shutdowns without auto-save, forms discarding partial entries, co-authoring overwrites, ephemeral logs users assumed durable. Explicit-save is an engineering legacy, not a user requirement.

**Boundary.** IS: unintentional or inaction-triggered loss of user work/content. IS NOT **System Amnesia** (failing to *use* what it has vs. failing to *keep* what users expect kept — different causes, different fixes). NOT present when: continuous auto-save actually preserves it; the content is explicitly ephemeral and users are told before creating it; the user knowingly chose to discard. Co-occurs with **Irreversible Action** when a deliberate action destroys data with no undo (reversibility fixes both); accidental navigation-away losing an unsaved form is this Trap alone (system design, no deliberate act).

**Detection procedure (pass one — flag, do not filter).** *Unit: cross-screen + failure-mode analysis.*
1. Identify every point where the user creates or modifies data; for each run the failure-mode battery: session timeout? crash/shutdown? navigation away? network drop? concurrent edit?
2. Flag every point where any answer is "it could be lost": absent auto-save, unpreserved partial entries, last-write-wins co-authoring, dismiss-to-void inputs (comment boxes that vanish on outside-click), transient content users would expect durable (meeting chat logs).
3. Live artifacts: simulate the failure modes where safe; design files: flag structurally and mark simulation-needed.

**Disconfirmation (pass two).** Per Boundary (a)–(c).

**Severity.** Scales with the value of the lost work and recreation effort: Low for trivially re-entered inputs; High for substantial creative work or unrecreatable data; High when permanent and of high personal/professional value — data loss reads as fundamental system failure and destroys trust disproportionately. Anchor: unsaved work destroyed by a forced shutdown (card example): High — substantial work, no recovery; High when the work is unrecreatable and of high personal or professional value. Escalators: C3 (interruption-prone contexts multiply the triggering events).

**Assessability & Confidence.** Medium confidence from design files (auto-save absence is structural; actual loss behavior needs simulation) — promotion path: deliberate failure-mode testing. High confidence from live testing or code (retention logic inspectable). Static single screens: retention behavior is not assessable — declare; visible auto-save indicators and state cues remain flaggable. Context axis: C2 sharpens (what work is at stake); largely population-independent.

**Attribution.** Irreversible Action pairing (deliberate-destruction case; fix-based on reversibility). System Amnesia distinction (above). Unnecessary Step(s): explicit-save requirements are also an eliminable step — auto-save removes both.

**Report fragments.** Finding: "User content in [flow] is permanently lost if [failure mode] occurs before explicit saving; no auto-save or recovery exists." Why it matters: "Data loss is experienced as fundamental system failure — it destroys trust and forces users to repeat work already done."

**Remediation.** Continuous auto-save wherever feasible. Design for failure from the outset — timeouts, drops, and crashes are certainties, not edge cases. Conflict resolution that protects all contributors, not last-write-wins. Where deletion is the goal, complicate the confirmation (typed word) so habituated clicking can't destroy data. Hazard note: auto-save without version history creates its own loss mode — silently overwriting a prior state the user wanted kept; pair continuous save with recoverable history. Governing question: what happens to the user's work if the session ends right now?

---

## TRAP CHUNKS — HABITUATING

### TRAP: GRATUITOUS REDUNDANCY *(ratified 2026-07-04)*
*Sub-tenet: Non-Redundant*

**Definition.** Two or more separate elements, at the same or directly nested level, serve the same function — leading to the same destination, triggering the same action, or conveying the same information. Scope is defined by function — navigational, operative, or informational: duplicated status indicators are this Trap even though they are never traversed. Visual appearance is irrelevant: duplicates need not look alike (Healthcare.gov's differently-labeled links to one page are the canonical case). For destination and action paths, duplication counts only within the same grammatical construction (object→action vs. action→object): paths serving different, *reasonably expected* constructions are flexible syntax, not this Trap. For informational elements no such exemption exists — two elements conveying the same information at the same level are duplicates regardless.

**Boundary.**
- IS: functional duplication per the definition, whether the elements are visually identical or not.
- IS NOT flexible syntax — but the exemption covers only constructions users would reasonably expect or prefer; duplicating via unlikely constructions is still gratuitous. Mutually exclusive with **Forced Syntax** per flow: only-one-construction = that Trap; duplicate-paths-same-construction = this one; confirm which before flagging either.
- Identical-looking elements with DIFFERENT functions: NOT this Trap (same function required). Route to Inviting Dead End (root cause) — each lookalike invites the incorrect judgment that it does what its twin does. Under repeated exposure (C4), additionally list Variable Outcome (consequence): across encounters the user experiences what they perceive as "the same" control yielding different outcomes, impeding habituation; a first encounter produces Inviting Dead End alone — the Variable Outcome line is C4-gated. Fix at the root: differentiate the elements AND give each a label or appearance that conveys its distinct function comprehensibly (Uncomprehended Element's bar applies to the fix — differentiation that leaves meanings undecodable converts the problem rather than resolving it); response consistency is not an available fix, since the functions legitimately differ (author-ruled 2026-07-04, superseding v2.0's Variable Outcome routing).
- Simultaneous visibility satisfies the level condition (author-ruled 2026-07-06): global chrome and section chrome rendered together are directly nested by construction; the level clause excludes only duplicates separated across non-nested contexts, never elements the user sees at once.
- Duplication dichotomy (author-ruled 2026-07-06): where target equivalence is unverified, the unknown selects between two Traps, never between Trap and no-Trap — same targets → this Trap; different targets → the lookalike fork below (Inviting Dead End root). Report the conditional pair with the verifying check; the fixes diverge (consolidate vs. differentiate and label), so both branches are stated. Observed duplication is never routed to coverage. (Contrast the mirror case: where an unknown selects between a Trap and NO-Trap, route to Worth a closer look instead — see G8.)
- IS NOT gratuitous multi-cue encoding of one signal BY one element (one state carried by color + icon + weight + border + motion at one location): separate elements are required for this Trap. Over-encoding harms route by their victim: a neighbor element losing relative salience → Effectively Invisible Element for the victim (the over-encoding named as root cause in the fix); conflicting cues → Uncomprehended Element; accumulated visual noise → one measurable ingredient for Poor Aesthetic's cumulative-risk observation; no victim anywhere → not a Trap (redundant encoding is often correct accessibility practice — never encode by color alone).
- IS NOT redundant encoding within a single element: icon plus label on one button, or color plus shape within one indicator, is one element — often accessibility best practice; never flag it as this Trap.
- IS NOT elements that look similar but serve different functions — route to the lookalike fork (Inviting Dead End root cause; see the dichotomy above); conversely, visually dissimilar elements sharing one function ARE candidates — the definition does not require visual identity.
- IS NOT duplication across different, non-nested hierarchy levels.
- IS NOT one persistent element rendered across multiple screens (header nav, tab bar) — that is ONE element.
- **No attentional-context exemption for informational elements.** Duplicating an indicator so "one copy is wherever the user looks" is not sanctioned design — it is this Trap. The endorsed alternative is a single indicator made globally perceivable (see Remediation and Effectively Invisible Element).

**Detection procedure (pass one — flag, do not filter).** *Unit: per-screen, plus cross-screen grouping for multi-screen artifacts.*
1. Enumerate every interactive and informational element on the screen or level under review — links, buttons, icons, menu items, status indicators — recording each element's apparent function from label, icon, placement, and context.
2. Group by function — apparent destination, triggered action, or information conveyed — ignoring visual appearance. For informational elements, group by the state or fact communicated.
3. Flag any group of two or more at the same or directly nested level; record the count and every instance's location.
4. Confirm functional equivalence where the artifact allows: traverse the prototype or live site; audit link targets and handlers in code; for indicators, confirm they reflect the same state variable.
5. Cross-screen (multi-screen artifacts only): group functions across screens within the same navigation level; persistent chrome counts once — flag only additional elements duplicating what it already provides.
6. Conventional-pair guard — do not silently exempt "standard patterns"; these are candidates like any others: site logo navigating to homepage alongside a separate Home link; a search input field alongside a standalone search icon triggering the same search; multiple Sign In / Get Started buttons for the same action; the same destination in two or more nav regions on one screen. Convention may inform severity; it does not disconfirm presence.
7. Routing fork on identical-looking elements: if the functional-equivalence check (step 4) shows identical-looking elements with the SAME function → this Trap; with DIFFERENT functions → route to Inviting Dead End (a lookalike inviting the wrong choice) and, where the same element type behaves differently across contexts, Variable Outcome — per those Traps' boundaries.
8. Name every candidate concretely ("six elements on Home appear to lead to Find a Location"); never flag on a general impression of clutter (G6).

9. Enumerate visible duplication on the screen: elements sharing an exact label, sharing an icon, or presenting the same evident function (two search ingresses, two orientation anchors). Flag every pair or group; on static artifacts, flag on appearance — target verification is adjudication's concern, not detection's (author-ruled 2026-07-06). Elements positioned in navigation chrome are treated as interactive by default — a clickable branded wordmark or nav link is a navigation control regardless of branding appearance; the informational-label exemption applies only to plainly non-interactive text.

**Disconfirmation (pass two).** NOT present when: (a) the paths serve different, reasonably expected goal constructions (flexible syntax); (b) the elements sit on different, non-nested hierarchy levels; (c) apparent duplicates in fact serve different functions (verified); (d) the "duplicates" are one persistent element rendered across screens.

**Severity.** The consequence is decision think-time ("are these different?") plus visual noise — for visually identical and dissimilar duplicates alike — and slowed habituation as practice divides across routes. Scales with duplicate count and real estate consumed (two quiet duplicates: Low; thirty-plus duplicated links restructuring a homepage: High). Apparent-duplication groups (shared exact label, or same evident function) default to Medium severity at Medium confidence pending target verification (author-ruled 2026-07-06); the count/real-estate gradient adjusts from there. Anchor: the homepage carrying three, then four, links to one destination (card example): Medium–High as duplicate count and consumed real estate grow — each addition further divides practice. Escalators: C4 is decisive — duplication on recurring tasks rates far higher than on one-time tasks (it blocks the automaticity repetition would otherwise build); C2 critical-path placement escalates. Compounding downstream effects (displaced content, added scrolling, option proliferation) raise cumulative severity but are attributed only per the Attribution rules.

**Assessability & Confidence.** Static screenshot (author-ruled 2026-07-06): apparent duplication is observable and REPORTABLE — never routed to coverage. Shared exact label or icon is itself evidence of shared function (a label is a promise — see Inviting Dead End's label-as-evidence rule) → Medium confidence, promotion path "verify the targets of [elements]," cost one click each. Same evident function without shared labeling (two search ingresses, two orientation anchors) → Low confidence, same path. Each duplication group is its own issue (G3 atomicity). The ONLY declared limitation is the genuinely hidden class: visually dissimilar elements whose shared function is entirely invisible — coverage line: "this artifact cannot exclude visually dissimilar duplicates; a link-target audit would settle." Prototype/live/code: High confidence — among the most automatable Traps; code audit (duplicate destinations, shared handlers, one state variable rendered twice) routinely finds what usability testing misses, since testing walks intended paths only. Context axis: largely context-free — duplication is structural; C2 and C4 sharpen severity only; no field gates presence.

**Attribution.** Downstream Traps (Invisible Element via displaced content, Unnecessary Step(s) via added scrolling, Information Overload via option proliferation) each require independent evidence — never assume them from confirmed duplication; when confirmed, this Trap is more often a contributor than sole cause. Reverse link: where duplication was introduced to remedy an Effectively Invisible Element, report this Trap as the current problem and note the underlying attention problem it compensated for — the fix must address both. Ambiguous Home: duplicated orientation points co-occur — see that Trap.

**Report fragments.** Finding: "[N] separate elements on [screen/level] serve the same function — [function]. The duplicates add decision overhead and visual noise without adding capability." Why it matters: "Duplicate elements multiply what users must evaluate without multiplying what they can do, slowing decisions and preventing the repetition on a single route that automatic use requires."

**Remediation.** Consolidate: one path per destination per reasonably expected construction; one indicator per state. If the duplicate was added because the original was hard to notice, fix the original's noticeability instead of keeping copies — relocate into the task's attentional focus, or make the single instance globally perceivable (whole-screen tint shift, screen-edge pulse, attention-following placement). Audit code for duplicate destinations and shared handlers. Preserve genuinely flexible syntax; do not "fix" it as redundancy.

---

### TRAP: VARIABLE OUTCOME *(ratified 2026-07-04)*
*Sub-tenet: Consistent with Expectations*

**Definition.** The system responds differently and unexpectedly to the same user action at different times. Most often a mode error (CapsLock; gear selectors; overloaded controls), but modes aren't required — inconsistently supported functions (right-click works on some instances, not others) qualify. The key question is not whether the same action produces different results, but whether the user is *attending to the signal that explains the difference*: a context-dependent button the user is looking at is unproblematic; a mode tracked only in memory is the Trap.

**Boundary.** IS: same action, different outcome, with the explaining state outside the user's awareness. Physically distinct lookalike elements with different functions are NOT this Trap's root — route to Inviting Dead End (root cause) with this Trap as C4-gated consequence (see Gratuitous Redundancy's fork); this Trap proper requires literally the same control varying over time. NOT present when: a mode indicator sits within the user's attentional focus at the moment of action; the state is a quasi-mode the user physically sustains (held Shift — impossible to forget); variation is in degree, not kind (harder flick scrolls faster); the state change is itself an explicit user action they'd be attending to. Caused by **Invisible Element** (no indicator exists) or **Effectively Invisible Element** (indicator exists, placed away from attention) — confirm the indicator's existence/placement independently; do not infer either from the outcome variation alone; when confirmed, the indicator Trap is root cause (fixing it dissolves the surprise — fix-based). **Accidental Activation** worsens on overloaded, state-dependent controls — consistency is root cause there.

**Detection procedure (pass one — flag, do not filter).** *Unit: cross-screen/cross-state; code is the native artifact.*
1. Code artifacts: sweep for state-handlers — any place one user action routes to different outcomes by system state; each is a candidate.
2. Flow/live artifacts: for each control, probe across contexts/states — same action, same result? Flag every divergence.
3. For each candidate, locate the state signal: does one exist? where, relative to the user's attentional focus at the action moment (feeds EIE/IE routing)? Is the state user-sustained (quasi-mode)?
4. Flag inconsistently supported functions (same element type responding differently across instances) — the modeless form; static screenshots cannot detect this Trap — declare.

**Disconfirmation (pass two).** Per Boundary conditions (a)–(d) above.

**Severity.** Medium for surprise-and-retry; High when the wrong-state action costs the task; High in safety contexts — mode error is a recurring factor in aviation, vehicle, and medical catastrophes (the Monostable shifter killed). For safety-critical interfaces the acceptable mode-error risk is zero: redesign to eliminate the mode, not to improve the indicator. Escalators: C3 (attention elsewhere is precisely when modes are forgotten — driving); C4 (overloaded controls in core loops slow all learning — game-controller research).

**Assessability & Confidence.** High confidence detection from code (state-handlers are directly findable — an AI-native strength); whether users will be unaware of the state: Medium confidence, gated by attention knowledge (C2/C3) — promotion path: observe attention at the action moment. Modeless form: harder, needs flows/live probing. Context axis: C3 gates the awareness judgment; C1 (prior product conventions) softens.

**Attribution.** Indicator routing per Boundary (fix-based). Wandering Element and Inconsistent Appearance are the placement/appearance members of this consistency family — audit each independently. Ambiguous Home: a home action that sometimes lands elsewhere is this Trap co-occurring there.

**Report fragments.** Finding: "[Action] produces different outcomes depending on [state], and no indicator of that state is reliably within the user's attention when acting." Why it matters: "Unexpected outcomes prevent reliable habits — and in safety-critical contexts, mode errors kill."

**Remediation.** Eliminate the mode where possible — consistent behavior beats a well-indicated mode (even perfectly visible indicators lose to dedicated functions for learning speed). Where unavoidable: put the indicator where attention already is at the action moment, or convert to a user-sustained quasi-mode. Safety-critical: eliminate, don't indicate.

---

### TRAP: WANDERING ELEMENT *(ratified 2026-07-04)*
*Sub-tenet: Consistent with Expectations*

**Definition.** The same interface element is presented in a different location at different times — controls, status indicators, or content that move across screens, contexts, or app versions. Spatial memory is among the most powerful automaticities available to designers, and it costs nothing but the discipline of keeping things where they are; wandering squanders it — every displaced encounter pulls the user back into conscious search.

**Boundary.** IS: inconsistent *placement* of the same element across contexts. IS NOT **Inconsistent Appearance** — the manuscript's line: a control can wander without changing appearance and can change appearance without wandering; audit placement and visual form independently, evidence each separately. Downstream of it: **Effectively Invisible Element** — but confirm independently that the new position falls outside where users would look; do not infer invisibility from movement alone (fix-based: pinning the element resolves derivative noticing failures — Wandering Element is root cause). NOT present when: placement variation is context-appropriate and meaningful (a Share button positioned differently in reading vs. list view because the content relationship differs); the element is low-frequency (no spatial memory would form); the change is explicitly communicated through a design transition users will attend to.

**Detection procedure (pass one — flag, do not filter).** *Unit: cross-screen by nature — this Trap does not exist in a single screenshot; declare on single-screen artifacts.*
1. Identify recurring elements across the screens in scope; prioritize high-frequency controls — search, navigation, editing, confirmation — where spatial memory pays most.
2. Map each recurring element's position per context (coordinates/regions in design files make this directly auditable).
3. Flag every placement inconsistency, recording the contexts and displacement; note ecosystem-level wandering (the same platform control placed differently across an app family).

**Disconfirmation (pass two).** Simultaneously visible duplicates are never this Trap (author-ruled 2026-07-05) — it requires the SAME element appearing in DIFFERENT locations at different times; two elements present at once on one screen route to Gratuitous Redundancy (same function) or its lookalike fork (different functions). Per Boundary conditions.

**Severity.** Medium baseline — slowed habituation, conscious search on every encounter. Anchor: the Edit control appearing in different positions across sibling apps (card example): Medium — conscious search on every encounter. Escalates on C4 (high-frequency, time-sensitive controls: navigation, edit, search) and C3 (searching for a moved control while driving or under pressure). High when displacement of a critical control under time pressure costs the task (C3 conversion).

**Assessability & Confidence.** High confidence from multi-screen design files — cross-context placement comparison is directly auditable, one of the most automatable Traps, and precisely the audit human task-based reviews skip (an AI-native strength). Context axis: C4 gates severity weighting (frequency); largely population-independent for presence.

**Attribution.** Inconsistent Appearance: independent co-audit (both may be present; separate evidence). Effectively Invisible Element downstream (fix-based, above). This Trap is invisible to task-based evaluation — flag the methodology gap in reports where relevant.

**Report fragments.** Finding: "[Control] appears in different positions across [contexts] — users who learned its location in one context must search in others." Why it matters: "Inconsistent placement prevents spatial memory from forming — every encounter demands conscious search that consistency would have made automatic."

**Remediation.** Establish placement conventions for high-frequency controls early and treat them as constraints. Map recurring elements' placement across every context; inconsistencies are the finding. Platform-level controls hold consistent positions across an ecosystem.

---

### TRAP: INCONSISTENT APPEARANCE *(ratified 2026-07-04)*
*Sub-tenet: Consistent with Expectations*

**Definition.** The same interface element is presented in a different style at different times — visual or auditory: differing icons, labels, control styling, or sounds for the same function while position may hold. Users cannot form an automatic response to something that doesn't reliably present itself the same way; worse, a learned form may not be *recognized* in its variant form — habit breaks, deliberation resumes (Windows' Fluent-vs-legacy settings is the persistent example). Scope (author-ruled 2026-07-06): variance across different TIMES or different PLACES — including parallel instances on one screen; the temporal-only reading was narrower than the Trap's intent (canon verbatim retains the printed wording; deviation logged).

**Boundary.** IS: inconsistent presentation of the same element/function. IS NOT **Wandering Element** (placement vs. appearance — independent audits, separate evidence). Downstream: can temporarily produce an **Uncomprehended Element** when a familiar function appears in an unfamiliar form — confirm the variant is genuinely unclear, not merely different; when it is, this Trap is root cause (fix-based: unifying the form restores recognition). NOT present when: variation is intentional and communicates a meaningful distinction (save styled differently in edit vs. view mode to signal the mode); the legacy context is one users recognize as distinct; the element is low-frequency.

**Detection procedure (pass one — flag, do not filter).** *Unit: cross-screen by nature; declare on single-screen artifacts.*
1. Identify recurring functions across screens in scope; prioritize core actions — New, Delete, Edit, Share, Search — and recurring status vocabulary.
2. For each, collect every visual/auditory representation across contexts; flag any function with more than one form (icon variants, icon-in-one-place-word-in-another, mixed design languages, legacy/current coexistence).
3. Record whether variation is systematic (design-language boundary) or scattered (drift) — informs remediation.

**Disconfirmation (pass two).** IS NOT content contradiction — two informational claims that cannot both be true route to Incorrect Information (something is wrong, not merely varying); this Trap's harm is unlearnability of a signifier whose instances are each individually acceptable (author-ruled 2026-07-06). Different elements with different functions carrying different visual treatments are NOT this Trap (author-ruled 2026-07-05) — it requires the SAME element or action varying. Mixed treatment classes within one container that track a real functional distinction (destinations as text tabs, utilities as icon-only controls — a platform-wide convention) are differentiation, not inconsistency; where similarity or dissimilarity misleads grouping, route to Poor Grouping. The complement (author-ruled 2026-07-06): the same signifier for the same state varying across parallel instances — including on one screen — IS this Trap, provided the sameness of state is established; unverifiable state routes to Worth a closer look per the trap-vs-no-trap rule. Per Boundary conditions.

**Severity.** Medium baseline — slowed recognition and habituation, plus per-form learning cost. Anchor: the same New action rendered as a text label in one context and a pen icon in another (card example): Medium — per-form learning cost, slowed recognition. Escalates on C4 (core recurring actions) and at comprehension breakdown (route the Uncomprehended Element consequence). Escalator: mixed design languages across a product boundary users cross constantly.

**Assessability & Confidence.** High confidence from multi-screen design files — cross-context visual comparison of recurring elements is directly auditable; like its placement twin, an AI-native strength and a blind spot of task-based human review. Context axis: C4 weights severity; C1 softens where the population knows the legacy context as distinct.

**Attribution.** Wandering Element co-audit. Uncomprehended Element downstream (fix-based, above). Gestalt similarity note: inconsistent forms don't just fail recognition — they actively signal *different function*, misleading category perception.

**Report fragments.** Finding: "[Function] appears as [form A] in [context 1] and [form B] in [context 2] — users who learned one form will not automatically recognize the other as the same function." Why it matters: "Each form users must learn for the same function is a cognitive investment consistency would have eliminated — and variant forms can read as different functions entirely."

**Remediation.** A design system specifying every recurring element's presentation, enforced — deviations require explicit justification. Evolving the design language obligates a legacy-component audit; don't let two languages coexist. Core actions represented identically product-wide.

---

### TRAP: AMBIGUOUS HOME *(ratified 2026-07-04)*
*Sub-tenet: Well-Oriented*

**Definition.** The interface presents multiple, competing locations for getting oriented and initiating tasks. A single reliable home — one place, reachable from anywhere by one consistent action — is the anchor from which navigational habituation flows and the automatic recovery point when users get lost. When home is ambiguous, users must hold the structure in conscious memory and reason their way back — the burden habituation should have removed.

**Boundary.** IS: two or more plausible homes, or an inconsistent action for reaching home. Scope test: this Trap is exclusively about the product's GLOBAL home — the top-level anchor of the whole navigation system. Multiple competing entry points to a specific feature or task are Gratuitous Redundancy, not this Trap; ask "is the ambiguity about where to start in the whole product, or about which element to use for a specific task?" The manuscript frames it as a special case of its neighbors — multiple homes is a redundancy problem, an inconsistent home action a consistency problem — but it is its own Trap with its own fix (consolidation). NOT present when: one clearly defined home is reachable from every context via one consistent action; the product is deliberately homeless because all tasks are self-contained; apparent multiple homes are entry points to clearly distinct, non-overlapping sections users understand as separate. Co-occurring: **Gratuitous Redundancy** when the homes duplicate capabilities (confirm the overlap); **Variable Outcome** when the home action lands differently at different times (separate evidence); **Memory Challenge** downstream when users must consciously track location because no reliable home exists (confirm); **Poor Grouping** when overlapping capabilities blur the mental model. Home iconography used for non-home destinations (a house icon on a Library button — the Meta VR case) is an **Inviting Dead End** compounding this Trap.

**Detection procedure (pass one — flag, do not filter).** *Unit: cross-screen/whole-IA.*
1. Identify every element or location that could plausibly be read as a starting point / orientation anchor (landing screens, dashboards, home-labeled or home-iconed destinations, launcher surfaces). More than one candidate = flag.
2. Audit the return-home action from every context: same action everywhere? single-step everywhere? Flag inconsistencies and multi-step returns.
3. Flag home iconography attached to non-home destinations (routes to Inviting Dead End co-listing).
4. Multi-platform/multi-mode products: compare home conventions across modes (the Windows 8 two-homes case).

**Disconfirmation (pass two).** Per Boundary conditions.

**Severity.** Medium — disorientation, orientation attention-tax on every task start; High when users cannot recover from being lost (deep hierarchies where home is the recovery mechanism) or abandon. Anchor: two competing Start/Home experiences, one per input mode (card example): Medium–High — orientation is the recovery mechanism, and it forked. Escalators: C4 (orientation happens every session, forever); product complexity.

**Assessability & Confidence.** Medium confidence from design files (candidate homes and return-action consistency are structural; which one users *conceptualize* as home needs user knowledge) — promotion path: ask users unprompted where they'd go to start a task or recover; inconsistent answers confirm. High confidence for the return-action inconsistency half (directly auditable). Context axis: C1 gates the conceptualization judgment; C4 weights severity.

**Attribution.** Per Boundary — each co-Trap independently evidenced; this Trap is root cause where consolidation dissolves the others (fix-based).

**Report fragments.** Finding: "The interface offers [N] plausible homes — [list] — producing different starting contexts and preventing a single orientation habit; the return-home action is [inconsistent across contexts]." Why it matters: "Without one reliable home, disoriented users must reason their way back instead of reaching automatically — orientation permanently taxes attention that habituation should have freed."

**Remediation.** Consolidate to one home — not better labeling of several. One destination, one action, consistent across every context and input mode. Reserve home iconography exclusively for the primary home. Audit every new entry point for whether it creates a competing home.

---

## TRAP CHUNKS — BEAUTIFUL

### TRAP: POOR AESTHETIC *(ratified 2026-07-04)*

**Definition.** The system's sensory design, style, personality, or tone is judged unpleasing, inappropriate, or inauthentic by its intended users. Two dimensions: *attractiveness* (visually unpleasant) and *appropriateness* (mismatched to context, audience, or moment — and time-sensitive: current today can be dated in three years). Scope includes every sensory register — visuals, sound, voice intonation, and product personality/tone (a chatbot's sycophancy is an aesthetic failure).

**Boundary & assessability warning (read first).** The manuscript is explicit: this is the Trap least amenable to automated detection, and the framework author's verdict (revised 2026-07-04): the analyzer NEVER asserts the PLEASINGNESS verdict — that belongs to intended users, and reliably only over exposure (first-encounter liking is unstable; mere-exposure effects shift it). It DOES assess aesthetic APPROPRIATENESS and AUTHENTICITY as findings: a mismatch between a named design property and a STATED C1/C2/C3/brand fact, evidenced per G6 — ceiling Medium confidence (population-relative); leaning on declared defaults instead of stated facts caps at Low confidence; no stated fact to cite → no appropriateness finding, route to the cumulative-risk observation instead. All perception checks in this chunk specify repeated-exposure or longitudinal designs; first-encounter reactions are insufficient to confirm or clear. Its entire legitimate contribution: (1) principle-violation flags — misalignment, broken visual hierarchy, inconsistent typography, contrast failures — most of which route to *other* Traps as root cause (contrast → Physical Challenge; hierarchy → Poor Grouping; inconsistency → Inconsistent Appearance); (2) the functional-foundation audit — the aesthetic-usability effect runs both directions, so failures on the other eight Tenets actively degrade aesthetic experience; addressing every other-Tenet finding is the analyzer's real aesthetic contribution; (3) tone/personality observations flagged as observations for designer judgment, never verdicts. Also NOT a Trap to validate via pre-launch user opinion: pre-launch aesthetic feedback reflects resistance to the unfamiliar (the Razr and Aeron were pre-launch failures and post-launch standards) — reports must not treat "users disliked the look" as confirmation.

**Detection procedure (pass one — flag, do not filter).** *Unit: per-screen + whole-product coherence.*
1. Run the principle audit: alignment grid violations, hierarchy collapse (no clear reading order), typography inconsistency, color-system violations, contrast failures — each flagged with its routing Trap where one exists.
2. Flag tone/personality mismatches observable in copy and sound (celebratory intonation on sad content; sycophantic assistant register) as designer-referral observations.
3. Compile the cross-Tenet foundation summary: aesthetic experience is capped by the product's worst functional failures.
4. Cumulative-risk observation (author-ratified; emit through Worth a closer look — it passes all three gates by construction: pivotal, worst branch ≥ Medium, named check = exposure-aware perception testing with the intended population, cost stated): when three or more measurable principle violations or functional Traps co-occur on one screen, add an observation (not a verdict) that the accumulation itself signals design-investment risk — aesthetic failures are cumulative, and the combined effect reads as overall quality failure to users.

**Disconfirmation (pass two).** Principle-violation flags disconfirm normally under their routing Traps. The residual aesthetic judgment is permanently "not assessable by this analyzer — designer domain": that is the correct, honest output, not a failure of the tool.

**Severity.** When principle violations route elsewhere, their host Trap's ladder applies. The unrouted residual carries business weight the report should state without scoring: aesthetically failing products are perceived as less trustworthy, less desirable, and less usable (aesthetic-usability effect) — reported as context, not a ladder rating (author-ratified).

**Report fragments.** Observation form only: "The following measurable design-principle violations were found [list, with routed Traps]; the residual judgment of attractiveness and appropriateness for [audience/moment] requires design expertise and is outside this analysis. Note: pre-launch user aesthetic feedback is an unreliable validator — novel designs routinely test poorly and succeed."

**Remediation.** Excel on the other eight Tenets first — functional failure cannot be rescued visually, and functional excellence is beauty's necessary foundation. Give design expertise genuine authority; principles (alignment, hierarchy, contrast, proximity, color, typography) are the floor, and knowing when to depart from them is where expertise earns its place. Listen to users; trust your designers.

---

## VERBATIM DEFINITIONS (report display only — never loaded into analysis passes)

*Registry of canon-verbatim trap definitions for report rendering. The tool displays the entry matching each cited Trap under its badge in the report UI. The pack generator MUST exclude this section from the pass-one and pass-two packs and emit it into the manifest for the rendering layer. These definitions play no role in analysis: the working definitions in the Taxonomy Index and Trap chunks govern detection and adjudication. Deviations between a verbatim and its working definition are deliberate — together they form the improvement ledger that feeds future printings of the cards and manuscript (see Open Items 8). Source: manuscript v3 trap-section definition slots, author-verified 2026-07-04; Gratuitous Redundancy sourced from the updated printed card (post-dates the manuscript). Whitespace normalized to single spaces; otherwise character-exact.*

- **Invisible Element** — No label, icon, or other interface element is provided to let the user know how to achieve a goal, and the user lacks the prior learning needed to overcome its absence.
- **Effectively Invisible Element** — A label, icon, or other interface element goes unnoticed because it is unexpected or misaligned with the user’s focus of attention.
- **Distraction** — Something in the interface draws the user's attention away from their current goal.
- **Uncomprehended Element** — A label, icon, or other interface element is noticed, but its meaning or required method of interaction is unclear.
- **Inviting Dead End** — A label, icon, or other interface element is incorrectly judged to be a means of achieving a goal; it looks right but is wrong.
- **Poor Grouping** — An important relationship between two or more interface elements is unclear.
- **Forced Syntax** — A sequence of actions cannot be completed in the order or manner the user expects or prefers.
- **Memory Challenge** — The user is required to remember information that is easy to forget.
- **Feedback Failure** — The system fails to communicate to the user the consequence of their actions, or how to resolve a failed action.
- **Physical Challenge** — Some aspect of the system causes physical discomfort or makes it physically difficult or impossible for the user to complete actions.
- **Accidental Activation** — It’s easy for the user to unintentionally trigger an action during normal use.
- **Slow or No Response** — The actual or perceived time it takes the system to respond exceeds what the user wants or expects.
- **Captive Wait** — The system does not allow the user to advance or back out of a process at a time of their choosing.
- **Unnecessary Step(s)** — The number of steps a user must take to achieve a goal is greater than it needs to be.
- **Information Overload** — Information presented to the user is understandable but there’s more of it than there needs to be.
- **System Amnesia** — The system fails to take advantage of the user’s prior work, preferences, or context.
- **Incorrect Information** — Information presented to the user is factually wrong, distorted, incomplete, out-of-date, or contains errors.
- **Bad Prediction** — The system fails in its attempt to anticipate the user's intent, preference, or context; it guesses wrong.
- **Irreversible Action** — The system does not allow the user to undo or reverse an action they have taken.
- **Unwanted Disclosure** — The system exposes personal data or behavior in a way that is harmful, embarrassing, or unexpected.
- **Data Loss** — The system fails to retain information or content the user expects to be preserved.
- **Gratuitous Redundancy** — Multiple instances of interface elements that complete the same action are presented to the user at the same time.
- **Variable Outcome** — The system responds differently and unexpectedly to the same user action at different times.
- **Wandering Element** — The same interface element is presented in a different location at different times.
- **Inconsistent Appearance** — The same interface element is presented in a different style at different times.
- **Ambiguous Home** — The interface presents the user with multiple, competing locations for getting oriented and initiating tasks.
- **Poor Aesthetic** — The system's sensory design, style, personality, or tone is judged as unpleasing, inappropriate, or inauthentic by its intended users.

---

## AUTHORING STANDARDS (for KB maintainers — never loaded into the analyzer)

**A1. Generalization test.** Every rule must be stated in terms of mechanism and observable conditions, never the surface features of a UI it was derived from. Before a rule enters the KB: would it fire correctly on an unseen interface from a different domain (medical device, game console, banking app)? If it names widgets, layouts, or phrasings specific to one evaluated product, it is overfit — rewrite at the mechanism level or reject.

**A2. Anecdote rule.** A failure observed once justifies a measurement, not a rule. Rules enter on evidence across artifacts or on principled mechanism; single-incident rules enter, at most, as a scoresheet column to watch.

**A3. Token budget.** Every rule competes with every other rule for the model's attention. Prefer deletion to addition; a rule that cannot state what failure it prevents does not stay.

**A4. Eval hygiene.** Never tune rules against the same artifacts used to score the KB. When iterating on eval results, hold out artifacts the revised KB has not seen, or the KB overfits the eval set exactly as A1 warns for single UIs.

**A5. Context-free language.** Every rule must be self-contained and readable without the history of its authoring. Never write a rule as a correction to a misreading only the authors remember ("X, not Y" where Y is a private reference); name the full intended scope instead. The analyzer has no memory of why a sentence was written — only what it says.

**A6. Write against the full artifact range.** Draft every detection procedure against all artifact types the analyzer accepts (single screenshot, disconnected screens, flows, live products, code) and declare its unit of analysis per G7. A procedure written with only the simplest artifact in mind silently overfits to it — "this screen" phrasing on a flow analysis is the canonical failure.

**A7. Definition coverage check.** Before a Trap chunk is final, map each clause of its definition to at least one detection trigger; any definitional clause with no corresponding trigger means the procedure detects a subset of the Trap. Sub-check — qualifier scope: for every qualifier in a definition, verify it applies to every disjunct it grammatically modifies; a qualifier true of some disjuncts silently attached to all of them makes the definition mean less (or more) than it says.

**A8. Controlled vocabulary, neutral terms.** The KB uses the framework's controlled vocabulary throughout — "element," not cue/signifier/affordance; synonyms from the broader literature appear only when explaining related concepts, never in operational rules. "Sibling Trap" is reserved for the Uncomprehended Element / Inviting Dead End pair as defined in the Taxonomy Index. Operational terms must be descriptively neutral — no intent, agency, or evaluation baked into words naming observable conditions (test: does the connotation describe the mechanism or decorate it? "invites" describes an Inviting Dead End's mechanism and stays; "disguised" decorated duplicate-appearance with intent and was cut).

---

## OPEN ITEMS (maintainer notes — never loaded into analysis passes)
1. CLOSED (author-ruled 2026-07-04, Q18): gratuitous multi-cue encoding routes by expressed harm via Gratuitous Redundancy's Boundary (victim salience → Effectively Invisible Element; conflicting cues → Uncomprehended Element; noise → Poor Aesthetic cumulative-risk ingredient; separate-element repetition → Gratuitous Redundancy informational scope; no victim → not a Trap). [Gap-lens candidate tag retained for the phase-two literature pass.]
2. Manuscript edits implied by KB work (additions 2026-07-04: Feedback Failure's unconditional root-cause MUST softens to the six mechanism routes, pure absence stands alone per Q8; cue vocabulary 'affordance' → 'signifier' per Norman's refinement; GR definition slot stale vs updated card — see item 8): Gratuitous Redundancy section rewritten in function language (incl. informational scope and appearance-irrelevance); Forced Syntax boundary vs. expression rigidity made explicit; FAQ Q8 (element terminology) answer written; Effectively Invisible Element confidence-tier sentence completed; placeholders (Forced Syntax Alexa example, Mass General, "add another path to it. But…", missing quotes/examples across draft-trap sections); stranded Variable Outcome definition line at end of Gratuitous Redundancy's block; "Sibling Trap" definition added to the manuscript.
3. CLOSED (2026-07-04): the draft-grade review was executed as a structured author Q&A — 22 rulings, all inline flags closed; see the closure log (item 9). Residual author option: a final full-file skim before declaring freeze, for unflagged drift the Q&A could not surface.
4. Literature gap-lens (phase two): per-trap audit of what the literature offers that the manuscript hasn't operationalized, and where each item sits.
5. Eval build: artifacts (seeded seven + decoys + one root-cause-ambiguous case + clean control), scoresheet (detection / attribution three-way / epistemic honesty / remediation specificity / trap-name-adjacency watch column), pre-registered success bars, A/B/C/D/E conditions with fresh-content C.
6. CLOSED (author-ratified 2026-07-04, Q5–Q7): v2-salvage additions, all signed off: Invisible Element ↔ Unnecessary Step(s) prerequisite-gate disambiguation; Incorrect Information ↔ Bad Prediction wrong-for-whom test and recommendation-row rule; the placeholder/draft exception; Feedback Failure's in-screen vs. post-action rule; Gratuitous Redundancy's conventional-pair guard (logo+Home, search field+icon, repeated CTAs) and identical-elements routing fork; Ambiguous Home's global-home scope test; Uncomprehended Element's state-vs-meaning exclusion, IO polarity check, and design-change regression clause; Poor Grouping's cite-the-principle requirement and common-region addition; Memory Challenge's dual-visibility Confirmed condition; Information Overload's task-burial trigger; Accidental Activation's hover trigger; Unwanted Disclosure's bundled-export trigger; Inviting Dead End's promise-breaking and label-as-evidence rules; Poor Aesthetic's cumulative-risk observation (also [JUDGMENT]-tagged). Routing note RULED (Q6): Inviting Dead End (root cause) with Variable Outcome as C4-gated consequence; fix = differentiate AND label comprehensibly (Uncomprehended Element bar applies to the fix). v2.0's Variable Outcome routing overruled.
7. CLOSED (author-ratified 2026-07-04, Q1–Q4): the J18–J25 rule batch, all ratified; J18's sub-ruling resolved as Option A (a specific participant count is permitted when its assumed discovery rate is stated). Historical sourcing below:
   - **J18** (Severity & Confidence — user-test sizing): standard wording is author-approved verbatim; **open sub-ruling** — as drafted, a specific participant count is permitted when its assumed discovery rate is stated; the alternative is template-only, no numbers ever.
   - **J19** (G6 — symmetric evidence for clearances): sourced from B's false-clearances (Physical Challenge "adequately sized"; Bad Prediction cleared on autocomplete sub-scope). Condition-neutral.
   - **J20** (G2 + G8 — candidate-line and coverage-note economy): defense-in-depth against output-budget truncation; no information loss, pass one routes and pass two explains.
   - **J21** (G3 — causal-chain vs conditional-identity discrimination gate + parsimony rule): sourced from E designating Inviting Dead End as root cause among IE/UE/IDE conditional alternatives. Author-specified: single most-applicable Trap + one-line note, full enumeration only on fix or severity divergence. Prior Segment-conditional and Manifests-as patterns renested as the two named sub-cases; **confirm the renesting preserves intended behavior for the sibling pair.**
   - **J22** (Severity & Confidence — calibration-gated ceilings; propagated into the Physical Challenge chunk): sourced from E stamping Confirmed on target size from an uncalibrated screenshot (author measured the live UI at >12 mm on a 15" display). **Physical Challenge is pilot-grade and was edited under this rule — re-review that chunk's detection step 1 and Assessability section.** Audit remaining chunks for other absolute-quantity thresholds (timing claims in Slow or No Response; text-size claims elsewhere) at deep pass.
   - **J23** (G8 §2 — Worth-a-closer-look discriminator, hard-AND entry ticket with per-gate fail examples, section boundaries): sourced from low-confidence findings leaking into the bucket in tool output. Key restatement: the Issue/bucket boundary is assert-vs-ask, NOT evidence-bar-cleared-vs-not (Flagged is an Issue confidence; sub-bar suspicions drop or go to Coverage notes). Also propagated J18 into §2's cost examples ("five-user test" removed).
   - **J24** (G2 — mode-agnostic discipline line; mirrored untagged in v1.1's shared scaffold): the tool now runs single-call and two-pass as permanent selectable modes; the masters must produce correct analyses in both. One line makes the detect-then-adjudicate discipline explicit for single-call execution. Also in this batch: preamble maintainer commentary in BOTH masters wrapped into "never loaded" H2 sections (v2.1: PROVENANCE & CHUNK GRADES; v1.1: PROVENANCE — its preamble described the experiment design to the analysis model, a leak in the same class as the OPEN ITEMS one the tool engineer caught); OPEN ITEMS heading renamed to carry the never-loaded marker.
   - **J25** (Severity ladder — severity asserts no prediction of occurrence; mirrored untagged in v1.1): sourced from the author misreading rubric shorthand ("High when users abandon") as an occurrence claim. Clarifies the two-axis design: severity classifies the worst plausible branch conditional on the Trap being real; likelihood lives in Confidence, C1 conditioning, the plausibility gate, and C4. Bans "likely" and occurrence estimates from severity rationales.
8. **Verbatim-definitions ledger (added 2026-07-04, author-ruled).** The VERBATIM DEFINITIONS section carries canon wording for report display only; the working definitions govern analysis. The two sets are a deliberate ledger: each deviation is an eval-tested improvement candidate for future card/manuscript printings, with the long-term goal of converging on one best common definition set for the AI and for humans. Current substantive deviations, both author-confirmed: **Gratuitous Redundancy** (verbatim = updated card wording, action-only scope; working definition covers destination/action/information — author notes the card wording's narrowness as a known limitation) and **Irreversible Action** (working definition adds the "recovery is possible but unsupported" clause bounding against Data Loss). Whitespace in verbatims normalized to single spaces per author-accepted recommendation. Manuscript editorial consequence: the manuscript's GR definition slot is stale relative to the updated printed card — add to the item-2 list. Extraction also surfaced for item 2: mislabeled "TRAP | EFFECTIVELY INVISIBLE ELEMENT" banner heading the Invisible Element section; "UNECESSARY STEP(S)" and "UNCOMPRE-HENDED ELEMENT" header typos; "Jakob Neisen" epigraph attribution; "inteerface" and "CONSISTENT WITH EXPECTAIONS" typos; "[Add quote here if we have an apt one]" placeholders at Captive Wait, Unnecessary Step(s), and the Efficient tenet page.
9. **CLOSURE LOG — author Q&A ratification cycle, 2026-07-04 (the deep pass of record).** Q1: J18 grounded-numbers Option A. Q2: J26 one sub-population per evaluation (mixed C1 → first-named segment + Coverage flag); G3 segment-conditional sub-case deleted; parsimony rule with fix-or-severity divergence as sole enumeration trigger. Q3: Physical Challenge redraft — modality-conditioned standards (12 mm = touch exemplar, not universal), inference-based flagging, reach at Probable per asserted C3 posture. Q4: J19/J20/J23/J24/J25 ratified. Q5: seventeen uncontested salvage rules ratified. Q6: GR lookalike fork → IDE root, VO C4-gated consequence, differentiate-and-label fix. Q7: Poor Aesthetic — appropriateness/authenticity assessable via stated-fact mismatch; pleasingness verdict never (and unreliable on first encounter — exposure-aware checks chunk-wide); cumulative-risk observation ratified, re-homed through Worth a closer look. Q8: Feedback Failure — six mechanism routes mandatory, pure absence stands alone. Q9: FF × Irreversible Action = independent co-failures, no designation; false-promise/IDE clause in remediation; G3 co-occurrence line added. Q10: Distraction interstitials clause. Q11: PG strongest-flag criterion; full Gestalt scrub incl. uniform connectedness and closure; expected association map (both directions); semantic-grouping step (independent axis). Q12: Forced Syntax sequence routing map (four cases; FS root → MC consequence C4-gated; MC standalone for intrinsically arbitrary content). Q13: Invisible Element — no perceivable signifier at the moment of need (by design or off-screen); definitive only when function known to exist AND nothing presented; scoped coverage for capability-knowledge limits; Norman signifier gloss. Q14: SNR Weber rule relocated to Remediation; recordings measurement-grade; scoped coverage. Q15: Captive Wait bidirectional scope + inverse capture ratified; dark-pattern note ratified; SNR too-fast line replaced by the four-way speed router; Fleeting Element rejected; Captive Wait name RETAINED (Forced Pace and Captive Pace considered and declined). Q16: Unnecessary Step(s) accretion heuristic DELETED (etiology, not detection signal; manifestations owned by their Traps). Q17: System Amnesia severity = recreation-cost gradient (volume × recall difficulty × error stakes; doctor's-office anchor; proximity does not grade severity; SA-root→MC-consequence note); Unwanted Disclosure floor parenthetical replaced (irreversibility constant, harm grades); Wandering Element C3 escalation ratified. Q18: multi-cue encoding routed by expressed harm (item 1). Q19: F cell (process-only, "B-alt") ratified — name F, no rival framework, tenet-free sweep, pre-registered predictions incl. expected near-parity on process-carried criteria. This Q&A constitutes the author deep pass; the file carries no open flags.
10. **F cell build (ratified Q19, queued):** the v2.1 process scaffold with all trap content stripped; generic goal-walk sweep written with zero tenet structure; provenance log per the v1.1 pattern; pre-registered predictions per the closure log. Smallest KB in the family; build next.
11. **Deliberate scope-outs (documented so absences read as design):** the framework is not a dark-pattern taxonomy — the Captive Wait, Distraction, and Unwanted Disclosure pattern notes are the intended coverage of deceptive-design adjacency; and the analyzer does not evaluate visual brand quality beyond Poor Aesthetic's evidence rules (appropriateness/authenticity via stated-fact mismatch; pleasingness never).
12. **COMPLETION SPRINT LOG (2026-07-04, author-ratified in four batches).** The draft/pilot grade distinction is retired: all 27 chunks now carry *(ratified 2026-07-04)*, each meeting the done-bar: Definition + Boundary with nearest-neighbor discriminators; mechanism-level detection (A1); named disconfirmers; severity block with a concrete anchor case (card-example-grounded); Assessability with ceiling, costed promotion path, and scoped-coverage line where partially assessable; attribution lines for known cascades; mechanism-tuned remediation with fix-hazard notes where real (typed-phrase↔US, auto-save↔version history, enlarge↔AA, differentiate↔UE, recovery-feedback↔IDE). Batch contents: B1 Critical cluster (IA, UD, DL, II, BP — anchors, scoped lines, two hazards); B2 Understandable drafts + review one-liners (Distraction/MC/FF anchors + scoped lines; INC-1 router-lens clause; INC-2 shared-salience designation; GAP-1 hue-only encoding in UE; GAP-2 banner-blindness in EIE; GAP-3 interaction-modality honesty line in G4, mirrored to v1.1; GAP-5 scope-outs = item 11); B3 pilot anchors (IDE, FS, GR, PC); B4 tail anchors (AA, SNR, CW, US, IO, WE, IncApp, AH; SA and VO already anchored; PA takes none by design — residual carries no ladder rating). Deferred with rationale: GAP-4 body-copy readability (needs the literature pass, item 4) and the 27×27 boundary matrix (needs measured confusion data, post-eval).
13. **FIRST LIVE-RUN REFEREE BATCH (2026-07-05, author-ruled from the initial v2.1 tool run on the regression fixture).** Four rules ratified as a set: (a) Invisible Element path-exhaustion disconfirmer — the run stamped IE-Confirmed while the grid icon (the marker element itself) sat unexhausted on-screen; (b) G3 atomicity — issue unit = unit of independent action (the dual-nav mega-issue correctly merges the architecture but the duplicate-Home and duplicate-search evidence split into their own GR issues); plus every co-occurring Trap carries the designation, no unmarked primary; (c) Wandering Element simultaneity guard — the run labeled two simultaneously visible search entry points WE; (d) Inconsistent Appearance differentiation guard — mixed nav treatments tracking a real functional distinction are not IncApp. Fixture ground truth recorded: the two search entry points share scope and destination (author-verified) → the duplication is Gratuitous Redundancy. Scaffold items (b) mirrored to v1.1 same pass.
14. **SCALE SIMPLIFICATION (2026-07-05, author-ruled).** Severity reduced to three levels — High absorbs the former Critical (irreversible harm folded into High's definition; all former Critical references in chunks remapped). Confidence relabeled High/Medium/Low with criteria unchanged (former Confirmed/Probable/Flagged map 1:1). Collision risk (two axes, same label words) was raised and accepted; mitigation encoded: prose always qualifies confidence values with the word "confidence," labeled report fields disambiguate on screen. Related-Trap prose test added to the composition rules: secondary Traps appear in description text only when they deepen understanding of consequences or resolution; `relationship` data populated in full regardless. All scaffold changes mirrored to v1.1 same pass.
15. **DUPLICATION-DETECTION BATCH (2026-07-06, author-ruled from the second live run).** The run observed every functional duplication (both search ingresses, triple Prime Video labels, dual orientation anchors) but routed them to coverage because target equivalence was unverifiable — conflating cannot-observe with cannot-confirm. Four rules ratified: (1) G4 observability/confirmability router (scaffold, mirrored to v1.1); (2) GR detection step enumerating visible duplication, flagged on appearance; (3) GR assessability rewrite — shared label/icon = Medium confidence with one-click promotion path, same evident function = Low confidence; (4) duplication dichotomy — the unverified unknown selects GR vs the IDE lookalike fork, never trap-vs-nothing; conditional pair reported with branches (fix divergence). Atomicity applies: each duplication group is its own issue. Predicted rerun delta: GR coverage entry shrinks to genuinely hidden cases; three Medium-confidence duplication issues appear on the fixture.
16. **DISTRACTION SEVERITY CALIBRATION (2026-07-06, author-ruled from the live sports-timer finding).** The run graded a peripheral countdown timer Medium for being "motion-like"; the author ruled it Low — severity grades the cost of the captured glance (occlusion, fragile-state interruption, recovery cost, C3 danger, C4 persistence), never the fact of capture. Aggregate visual noise routes to the salience-budget rule and Poor Aesthetic cumulative-risk, never inflates per-element severity. Content-level (Distraction chunk), v2.1 only. Fixture prediction: the timer finding regrades to Low.
17. **OBSERVATION-ACCURACY BATCH (2026-07-06, author-refereed).** The run reported Prime badges absent from two Suspense-row thumbnails; author verification of the source image shows badges present on ALL FIVE — a hallucinated absence, upstream of all attribution machinery. Ratified: (1) G6 per-instance enumeration rule (scaffold, mirrored); (2) Inconsistent Appearance working definition widened to "different times or in different places" per author canon ruling (third documented working-vs-verbatim deviation, next-printing candidate); complement added to the differentiation guard (same signifier, same state, varying across parallel instances = this Trap); (3) trap-vs-no-trap → Worth-a-closer-look routing (G8, mirrored; contrast note in GR's dichotomy). Fixture ground truth recorded: Issue 07 is FALSE — prediction: it does not recur. Eval scoresheet gains the observation-accuracy defect class. Addendum (same date): content-vs-presentation router ratified — content contradictions (claims that cannot both be true) → Incorrect Information; presentation variance of the same element/signifier → Habituating Traps (IncApp/WE/VO; author excluded GR from the router — duplication is sameness, not variance). Note: the Continue Watching row contains genuine indicator variance (Apple TV+ mark, purchase-bag icons) that tracks real entitlement distinctions — correct differentiation, not a Trap; a useful negative fixture case.
18. **INVITATION TEST (2026-07-06, author-ruled from the Movies/TV-shows IDE finding).** IDE requires a specific false representation of fit ("this looks like the right thing"), never mere willingness to explore ("let me see if this works"); generic categories invite exploration, not a promise, and failed exploration belongs to the missing path, not the explored element. Operational test: would the C1 user believe the element IS the path, or merely that it MIGHT contain one? Note: the run also filed a self-described unverifiable trap-vs-no-trap case as a Medium-confidence Issue — the exact pattern item 17's routing rule now forbids (run predates the rule). Fixture prediction: Issue 08 re-routes to Worth a closer look with its own "verify the kids filter" check; the invitation test denies it IDE standing either way. Retroactive coherence check: the grid-icon finding also fails the invitation test, confirming its UE/EIE-conditional routing.
19. **COVERAGE-INTEGRITY BATCH (2026-07-06, author-ruled).** (a) GR escape hatches closed: simultaneous visibility satisfies the level condition; nav-chrome elements interactive by default; apparent-duplication groups default Medium severity / Medium confidence. (b) G4 never-clear rule (scaffold, mirrored): a Trap whose Assessability declares the artifact class insufficient can never be cleared from it; chunk-absent traps default to not-assessable, never Not-present — sourced from Irreversible Action misfiled as "Did not find" on a static browse screen, root cause structural (non-candidate chunks never reach adjudication context; mechanical fix requested: per-trap assessability digest in the pass-2 core pack). (c) G8 trap accounting invariant (scaffold, mirrored): every Trap accounted for exactly once — issue primary, named secondary, or one coverage bucket; renders as the Trap Disposition Index (tool-side), sourced from Information Overload appearing only in prose with no scannable pill. Fixture predictions: two standalone GR issues (orange triple, green pair) at Medium/Medium; IA coverage line moves to Couldn't evaluate.
