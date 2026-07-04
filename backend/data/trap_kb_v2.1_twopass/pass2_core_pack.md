<!-- GENERATED from trap_kb_v2.1.md — do not edit; regenerate on any master edit -->
# PASS TWO — ADJUDICATION CORE PACK (KB v2.1, two-pass structure)

**Role of this pass:** adjudication. Load this pack PLUS the full chunk file for each Trap flagged in pass one (see manifest.json). The Taxonomy Index below permits re-routing a finding to a non-candidate Trap; when a Boundary clause routes there, load that Trap's chunk too. Apply, in order: Boundary & Disconfirmation → G3 one-problem-one-issue → G4/G5 assessability → Severity & Confidence → G8 report assembly.

## GLOBAL RULES (apply to every analysis, both passes)

**G1. Exact trap names.** Use full, exact Trap names; several Traps have near-identical names that denote different problems.

**G2. Two-pass discipline, with selective loading.**
- **Pass one (detection):** load only the Detection Procedures for all 27 Traps, plus the Context Intake Schema. Run each procedure. Flag every candidate. Do not filter, do not weigh disconfirmation, do not assign severity. Over-reporting at this stage is correct behavior.
- **Pass two (adjudication):** load the full chunks for candidate Traps only, plus the Taxonomy Index (so adjudication can re-route a finding to a non-candidate Trap when a Boundary clause points there). For each candidate, apply in order: (1) Boundary and Disconfirmation; (2) the one-problem-one-issue procedure (G3); (3) the Assessability lookup (G4/G5); (4) Severity and Confidence; (5) assemble the issue per G8. Kill, merge, and relabel freely — that is this pass's job.

**G3. One problem, one issue — evidenced diagnosis.** When multiple candidate flags point at the same underlying design element or decision, report ONE issue. At the bottom of each issue, list the Traps that align to that issue — each listed Trap must independently meet its own evidence bar (no tag-cloud padding; nothing evidenced omitted). Then apply the root-cause rule:
- **Fix-based root cause:** the root cause is the Trap whose remediation resolves the other listed Traps. Designate it "(root cause)" and mark the others "(consequence)." Worked example: an element noticed slowly *because it moves between screens* — pinning it to one location (Wandering Element's fix) dissolves the noticing problem, so Wandering Element is root cause and the delayed noticing is referenced in the explanation, not separately reported.
- **Bidirectional fixes:** when fixing either Trap would resolve both, fall back to mechanism order — the Trap upstream in the causal chain is root cause.
- **Root cause unclear:** designate no root cause; state "root cause unclear" AND name the specific check that would settle it. "Unclear" without a named check is unfinished adjudication.
- **Segment-conditional:** when which Trap applies depends on who the user is (see the Uncomprehended Element / Inviting Dead End sibling definition), list both, each tagged with its segment.
- **Manifests-as:** when one underlying property produces different Traps at different moments for the same user population and the fix converges (e.g., an unfamiliar goal-critical element that some users filter [Effectively Invisible Element] and others notice but can't decode [Uncomprehended Element]), report one issue: "manifests as X or Y — same root property, same fix." Do not phrase this as X→Y causation: for the non-noticing user, the noticed-element Trap never occurred.

**G4. Absent vs. unassessable is a lookup, not a judgment — on two axes.** Assessability is a function of the Trap, the artifact evidence, and the context evidence. Before analysis: (a) classify the artifact type (static screenshot / disconnected screens / wired prototype or flow / live product / code); (b) inventory the user context provided against the Context Intake Schema. Consult each Trap's Assessability & Confidence section on both axes. Three finding labels, never interchangeable:
- "Not assessable from this artifact — [what artifact would settle it]"
- "Not assessable without user context — [what context field would settle it]"
- "Not present" — requires that the artifact CAN show the Trap, required context is available or a declared default covers it, the Detection Procedure ran, and no candidate survived (or disconfirmation positively ruled it out — state which).

**G5. Context softens or gates.** Each Trap's Assessability & Confidence section states what missing context does per schema field:
- Where context *sharpens* calibration: assess anyway, label "Provisional — assumes [stated assumption]," name what would sharpen it.
- Where context *gates* assessment: do not guess — emit the "not assessable without user context" label, unless the Trap's profile declares a permitted default for that field, in which case assess against the default and declare it.

**G6. Named evidence.** Every flag, in either pass, must cite the specific element(s) and condition(s) that triggered it. General impressions ("feels cluttered," "low prominence") are not findings.

**G7. Unit of analysis.** Detection Procedures declare their unit: per-screen, cross-screen, or both. For multi-screen artifacts: run per-screen steps on every screen in scope; run cross-screen steps where declared; compute flow-level properties (dominant interaction patterns, persistent elements) across the whole flow before consulting them in per-screen judgments — a single screen misestimates them. Every finding cites the screen(s) where its evidence sits.

**G8. Report architecture — issues first.** The evaluator's goal is not to find and name Traps per se; it is to find and fix user-impacting issues. The Trap vocabulary rides on issues as diagnosis and shared team language. Reports have three sections:

1. **Issues.** One block per adjudicated issue: *what is happening to the user and where* (named elements, plain language, standing on its own without framework knowledge) → *Severity* (ladder + escalators) → *Confidence* (Confirmed / Probable / Flagged, with the promotion path when not Confirmed) → *the fix* → closing **trap line**: the Traps aligned to this issue, root cause called out when clear, per G3 patterns. Order issues by severity, worst branch first.
2. **Worth a closer look.** For elements whose bearing on the stated goals cannot be determined from the artifact but is pivotal if real. Entry format: *element — why it matters given the stated goal — the check (with its cost: one click / five-user test / code audit) — the implication, compactly both ways.* Entry ticket: the unknown must be pivotal to a stated C2 goal AND the worst branch must clear Medium severity AND a specific nameable check must exist. Note that the "if not" branch is often itself a live Trap (e.g., if the ambiguous element is NOT the ingress to the goal, nothing on screen may communicate the goal path at all — Invisible Element); reason it through. Batch all checks into a closing verification checklist.
3. **Coverage notes.** Compressed G4 outputs: Traps assessed and not present (with the condition that ruled them out), and Traps not assessable (with what would settle them).

**Anti-hedging edge (both directions):** a finding whose evidence clears its Trap's confidence bar MUST be reported as an issue, even where a check could add certainty — the bucket is for genuine pivotal unknowns, not for discomfort. An "I'm not sure" without a nameable check is not a bucket entry; it is unfinished adjudication. An optional whole-report Trap summary may be generated as an appendix view over the issues; it is never the primary structure.

---

---

## SEVERITY & CONFIDENCE (replaces per-Trap consequence/likelihood/combination blocks)

**Severity ladder** — the worst plausible outcome for the stated goals (C2) under the stated context (C3), per affected user. One axis:
- **Critical** — irreversible harm: data loss, unwanted disclosure, physical harm or safety risk, unrecoverable cost.
- **High** — task failure or abandonment with no discoverable recovery.
- **Medium** — recoverable failure, or recurring friction.
- **Low** — one-time friction, delay, polish.

**Escalators:**
- **Repetition (C4):** friction on a task performed daily escalates one level; friction on a once-per-lifetime setup task does not. Habituating-tenet Traps scale with repetition by nature.
- **Context (C3):** occupied channels, divided attention, motion, or time pressure can convert "recoverable" to "unrecoverable in practice" (a fumbled interaction while driving is not Medium).

Reach is not estimated. Findings are population-conditional via C1: a finding means "this population hits this." Severity is per-affected-user; priority (severity × reach × strategy) is the team's call, not the analyzer's.

**Confidence scale** — how sure the analyzer is that the problem is real, per finding:
- **Confirmed** — direct evidence in hand (e.g., a "not allowed" error message; audited duplicate link targets; a visible input mask; measured contrast below standard).
- **Probable** — risk conditions present, disconfirmation checked and cleared, but the confirming method is not accessible from this artifact or context.
- **Flagged** — conditions partially present, or the judgment leans on a declared default rather than provided context.

Each Trap's Assessability & Confidence section sets the **ceiling** (a Trap that requires user knowledge, analyzed from a bare screenshot, cannot exceed Probable regardless of how loud the risk conditions are). Every non-Confirmed finding names its **promotion path**: the specific step that would confirm or dismiss it, with its cost.

---

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
- **Inconsistent Appearance** — the same interface element is presented in a different style at different times.
- **Ambiguous Home** — the interface presents multiple, competing locations for getting oriented and initiating tasks.

**BEAUTIFUL** (It's aesthetically appealing)
- **Poor Aesthetic** — the system's sensory design, style, personality, or tone is judged unpleasing, inappropriate, or inauthentic by its intended users.

**Sibling Traps (reserved term):** Uncomprehended Element and Inviting Dead End are siblings — the same element can present either Trap, with which one applying depending on the user's prior experience: a user who has never seen the element forms no interpretation (Uncomprehended Element); a user who knows it from elsewhere, applied to a different function, forms a confident wrong one (Inviting Dead End). No other Trap pair is termed "sibling."

---
