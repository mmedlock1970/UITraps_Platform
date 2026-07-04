<!-- GENERATED from trap_kb_v1.1.md — do not edit; regenerate on any master edit -->
# PASS TWO — ADJUDICATION CORE PACK (KB v1.1, two-pass structure)

**Role of this pass:** adjudication. Load this pack PLUS the chunk file for each Trap flagged in pass one (see manifest.json). Apply: Disconfirmation → G3 → G4/G5 → Severity & Confidence → G8 report assembly.

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

---

## SEVERITY & CONFIDENCE

**Severity ladder** — the worst plausible outcome for the stated goals (C2) under the stated context (C3), per affected user: **Critical** (irreversible harm: data loss, unwanted disclosure, physical harm, unrecoverable cost) / **High** (task failure or abandonment with no discoverable recovery) / **Medium** (recoverable failure, or recurring friction) / **Low** (one-time friction, delay, polish).
**Escalators:** Repetition (C4) — friction on a task performed daily escalates one level. Context (C3) — occupied channels, divided attention, motion, or time pressure can convert recoverable to unrecoverable in practice.
Reach is not estimated; findings are population-conditional via C1.

**Confidence scale** — how sure the analyzer is that the problem is real: **Confirmed** (direct evidence in hand) / **Probable** (risk conditions present, disconfirmation checked and cleared, confirming method not accessible from this artifact or context) / **Flagged** (conditions partially present, or the judgment leans on a declared default). Each Trap's Assessability line sets the ceiling; every non-Confirmed finding names its promotion path and cost.

---

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
