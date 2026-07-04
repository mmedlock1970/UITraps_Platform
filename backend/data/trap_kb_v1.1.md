# UI Tenets & Traps — Analyzer Knowledge Base — v1.1 (card-deck-content lineage; card content + v2.1 process structure)

**Purpose.** This KB is experiment cell D: the v2.1 two-pass process structure applied to v1 card-deck knowledge only. Its per-trap content is generated MECHANICALLY from the card deck (Tenets_and_Traps_Card_MASTER_print.pdf) — verbatim definitions, one example each — with no enrichment from the book manuscript, the v2 KBs, or the KB authors. Thinness of chunks is a property of the source, preserved deliberately: the content difference between this file and trap_kb_v2.1.md is the variable the experiment measures.

**v1 canon, preserved exactly:** 9 Tenets (Understandable, Comfortable, Responsive, Efficient, Forgiving, Discreet, Protective, Habituating, Beautiful); 26 Traps; card names verbatim including "Unnecessary Step" (singular) and "Unattractive Appearance"; Bad Prediction under Efficient; the card vocabulary "cue (label, icon, affordance, or prompt)"; card definitions verbatim even where they differ from v2 canon (e.g., Accidental Activation as misinterpretation of physical actions; Gratuitous Redundancy scoped to actions only). No Incorrect Information Trap exists in this source.

**Structure inherited from v2.1 (trap-agnostic process only):** two-pass discipline with selective loading; one-problem-one-issue with root-cause designation (per the card deck's own How to Use steps 3 and 5: log all Traps with severity; ask whether one Trap is the root cause of the others); two-axis assessability; context softening/gating with declared defaults; named evidence; unit of analysis; issues-first report architecture; the severity ladder and confidence scale.

**Stripped from the inherited structure (trap-specific v2 content, documented for auditability):** the sibling-Trap reserved definition; the segment-conditional and manifests-as trap-line patterns and all worked examples naming Traps; C2's Inviting-Dead-End pointer; illustrative Confirmed-evidence examples in the confidence scale; the closer-look bucket's trap-named illustration. Per-trap detection procedures, disconfirmation decompositions, assessability lines, and remediation notes below are derived from each card's definition sentence by a fixed template — no external knowledge added.

---

## GLOBAL RULES

**G1. Exact trap names.** Use full, exact Trap names; several Traps have near-identical names that denote different problems.

**G2. Two-pass discipline, with selective loading.**
- **Pass one (detection):** load only the Detection Procedures for all 26 Traps, plus the Context Intake Schema. Run each procedure. Flag every candidate. Do not filter, do not weigh disconfirmation, do not assign severity. Over-reporting at this stage is correct behavior.
- **Pass two (adjudication):** load the full chunks for candidate Traps only, plus the Taxonomy Index. For each candidate, apply in order: (1) Disconfirmation; (2) the one-problem-one-issue procedure (G3); (3) the Assessability lookup (G4/G5); (4) Severity and Confidence; (5) assemble the issue per G8.

**G3. One problem, one issue — evidenced diagnosis.** When multiple candidate flags point at the same underlying design element or decision, report ONE issue. At the bottom of each issue, list the Traps that align to it — each listed Trap independently evidenced. Ask whether one Trap is the root cause of the others (per the deck's How to Use, step 5); designate "(root cause)" and "(consequence)" where the evidence supports it. If the root cause is unclear, say so AND name the specific check that would settle it.

**G4. Absent vs. unassessable is a lookup, not a judgment — on two axes.** Before analysis: (a) classify the artifact type (static screenshot / disconnected screens / wired prototype or flow / live product / code); (b) inventory the user context provided against the Context Intake Schema. Consult each Trap's Assessability line on both axes. Three finding labels, never interchangeable: "Not assessable from this artifact — [what artifact would settle it]"; "Not assessable without user context — [what context field would settle it]"; "Not present" — requires that the artifact CAN show the Trap, required context is available or a declared default covers it, the Detection Procedure ran, and no candidate survived.

**G5. Context softens or gates.** Where context sharpens calibration: assess anyway, label "Provisional — assumes [stated assumption]," name what would sharpen it. Where context gates assessment: do not guess — emit the "not assessable without user context" label, unless a default is declared for that field, in which case assess against the default and declare it.

**G6. Named evidence.** Every flag, in either pass, must cite the specific cue(s)/element(s) and condition(s) that triggered it. General impressions are not findings. (Per the deck's How to Use, step 3: identify and log any Traps observed; note their severity; log all.)

**G7. Unit of analysis.** Detection Procedures declare their unit: per-screen, cross-screen, or both. For multi-screen artifacts: run per-screen steps on every screen in scope; run cross-screen steps where declared; a persistent element rendered across screens is ONE element. Every finding cites the screen(s) where its evidence sits.

**G8. Report architecture — issues first.** The evaluator's goal is to find and fix user-impacting issues; the Trap vocabulary rides on issues as diagnosis and shared team language. Reports have three sections:
1. **Issues.** One block per adjudicated issue: what is happening to the user and where (named cues/elements, plain language) → Severity (ladder + escalators) → Confidence (Confirmed / Probable / Flagged, with the promotion path when not Confirmed) → the fix direction → closing trap line per G3. Order by severity, worst first.
2. **Worth a closer look.** For elements whose bearing on the stated goals cannot be determined from the artifact but is pivotal if real. Entry: element — why it matters given the stated goal — the check (with its cost) — the implication both ways. Entry ticket: pivotal to a stated C2 goal AND worst branch ≥ Medium AND a specific nameable check exists. A finding whose evidence clears its confidence bar MUST be an issue, not a bucket entry; an "I'm not sure" without a nameable check is unfinished adjudication.
3. **Coverage notes.** Traps assessed and not present (with the condition that ruled them out), and Traps not assessable (with what would settle them).

---

## SEVERITY & CONFIDENCE

**Severity ladder** — the worst plausible outcome for the stated goals (C2) under the stated context (C3), per affected user: **Critical** (irreversible harm: data loss, unwanted disclosure, physical harm, unrecoverable cost) / **High** (task failure or abandonment with no discoverable recovery) / **Medium** (recoverable failure, or recurring friction) / **Low** (one-time friction, delay, polish).
**Escalators:** Repetition (C4) — friction on a task performed daily escalates one level. Context (C3) — occupied channels, divided attention, motion, or time pressure can convert recoverable to unrecoverable in practice.
Reach is not estimated; findings are population-conditional via C1.

**Confidence scale** — how sure the analyzer is that the problem is real: **Confirmed** (direct evidence in hand) / **Probable** (risk conditions present, disconfirmation checked and cleared, confirming method not accessible from this artifact or context) / **Flagged** (conditions partially present, or the judgment leans on a declared default). Each Trap's Assessability line sets the ceiling; every non-Confirmed finding names its promotion path and cost.

---

## CONTEXT INTAKE SCHEMA (C1–C4)

**C1. User Knowledge.** Products and conventions the users have already internalized; domain expertise; novice/expert mix; prior exposure to this product's conventions. *Default when absent:* general adult population familiar with mainstream web/mobile conventions — declare it. Brand-specific, domain-insider, and novel cues cannot be cleared under the default.

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

**Assessability & Confidence.** user-context gated: expectation (appearance/location) derives from C1 prior learning and C2 task focus; ceiling Probable from statics.

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

**Assessability & Confidence.** wrongness is verifiable where the artifact shows destinations/outcomes (Confirmed); plausibility of the wrong judgment is C1/C2-gated.

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

**Assessability & Confidence.** visible demands (target size, text size/contrast) are artifact-assessable; other physical properties are not assessable from the artifact — declare.

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

