<!-- GENERATED from trap_kb_v1.1.md — do not edit; regenerate on any master edit -->
# PASS ONE — DETECTION PACK (KB v1.1, two-pass structure)

**Role of this pass:** permissive detection. Run every procedure below against the artifact. Flag every candidate with named evidence. Do NOT filter, do NOT weigh disconfirmation, do NOT assign severity — over-reporting at this stage is correct behavior. Adjudication happens in pass two with different materials.

**Harness guidance (not KB content):** for speed, instruct the model to emit candidates in a terse line format — `TRAP | screen | element(s) | triggering condition(s)` — one line per candidate, no prose. Decode time scales with output length; adjudication needs the evidence, not an essay.

**G1. Exact trap names.** Use full, exact Trap names; several Traps have near-identical names that denote different problems.

**G2. Two-pass discipline, with selective loading.**
- **Pass one (detection):** load only the Detection Procedures for all 26 Traps, plus the Context Intake Schema. Run each procedure. Flag every candidate. Do not filter, do not weigh disconfirmation, do not assign severity. Over-reporting at this stage is correct behavior. Candidate-line economy: the triggering-condition clause is telegraphic — at most ~15 words, no explanatory subordinate clauses. Pass one routes chunks; pass two explains.
- **Pass two (adjudication):** load the full chunks for candidate Traps only, plus the Taxonomy Index. For each candidate, apply in order: (1) Disconfirmation; (2) the one-problem-one-issue procedure (G3); (3) the Assessability lookup (G4/G5); (4) Severity and Confidence; (5) assemble the issue per G8.
- **Mode-agnostic discipline:** the staging above describes the two-pass runtime. In single-call execution the same discipline applies sequentially within one response: complete the full permissive detection sweep across ALL Traps first, then adjudicate the resulting candidates. Never filter, weigh disconfirmation, or assign severity during the detection sweep, in any mode.

**G6. Named evidence — symmetric.** Every flag, in either pass, must cite the specific cue(s)/element(s) and condition(s) that triggered it. General impressions are not findings. (Per the deck's How to Use, step 3: identify and log any Traps observed; note their severity; log all.) Clearances are held to the same bar: a "Not present" verdict must cite the specific disconfirming observation or the scope the procedure actually ran against, with the same specificity required of a finding — and must address the Trap's full definitional scope. Clearing one manifestation (one cue class, one screen region, one definitional clause) does not clear the Trap; state the scope actually cleared. A clearance without named evidence is not a clearance — emit the applicable not-assessable label from G4 instead. Per-instance enumeration (author-ruled 2026-07-06): any claim that an element, badge, or indicator is present on some parallel instances and absent on others must enumerate every instance with its observed state before the claim is made. Presence/absence patterns across repeated elements are the highest-risk observation class; unenumerated pattern claims are not findings.

**G7. Unit of analysis.** Detection Procedures declare their unit: per-screen, cross-screen, or both. For multi-screen artifacts: run per-screen steps on every screen in scope; run cross-screen steps where declared; a persistent element rendered across screens is ONE element. Every finding cites the screen(s) where its evidence sits.

---

## CONTEXT INTAKE SCHEMA (C1–C4)

**C1. User Knowledge.** Products and conventions the users have already internalized; domain expertise; novice/expert mix; prior exposure to this product's conventions. ONE sub-population per evaluation (J26): C1 names a single population; evaluating multiple segments means running multiple evaluations. If a mixed population is provided anyway, analyze against the FIRST-NAMED segment and emit one prominent Coverage line: \"Context named multiple populations; this analysis is conditioned on [first-named]. Run a separate evaluation for [others].\" *Default when absent:* general adult population familiar with mainstream web/mobile conventions — declare it. Brand-specific, domain-insider, and novel cues cannot be cleared under the default.

**C2. Goals.** The user's primary tasks and critical paths — AND the fuller set of goals users might plausibly bring to each screen. *Default when absent:* infer the apparent primary task from the screen itself and declare it; findings requiring the full goal set are degraded under this default.

**C3. Context of Use.** Availability of the user's channels and circumstances: attention (focused / divided / interrupted); vision (available / occupied); hearing (quiet / noisy); speech & audio-out (free / constrained by others or privacy); hands (both free / one / none); mobility (stationary / in motion); plus lighting, time pressure, device and input method. *Default when absent:* attentive, stationary, unencumbered, quiet, private use — the most forgiving context on every channel. Declare it, and state that findings under this default are a lower bound.

**C4. Exposure & Repetition.** User exposure stage (first-run / habituated / mixed) and task repetition profile (once / a few times / recurring). Habituating-tenet Traps scale with repetition; one-time tasks make comprehension Traps paramount. *Defaults when absent:* mixed exposure including first-time users for public-facing products; infer the task's repetition profile from its nature — declare both.

---

---

## DETECTION PROCEDURES (all 26 Traps)

### Invisible Element
*No cue (label, icon, affordance, or prompt) is provided to signal to the user how to achieve a goal, and the user has insufficient prior learning to overcome its absence.*

**Detection procedure (pass one — flag, do not filter).** *Unit: per-screen, against the goal set.*
1. From the C2 goal set, survey the artifact for the definitional conditions above.
2. Flag every candidate where the conditions appear present; name the specific cue(s)/element(s) and the condition(s) observed (G6).
3. Where a condition cannot be evaluated from this artifact or without a context field, record that as the reason per G4 rather than silently skipping.

---

### Effectively Invisible Element
*A provided cue (label, icon, affordance, or prompt) is not noticed, or is slow to be noticed, because its appearance or location differs from what the user expects.*

**Detection procedure (pass one — flag, do not filter).** *Unit: per-screen.*
1. From the C2 goal set, survey the artifact for the definitional conditions above.
2. Flag every candidate where the conditions appear present; name the specific cue(s)/element(s) and the condition(s) observed (G6).
3. Where a condition cannot be evaluated from this artifact or without a context field, record that as the reason per G4 rather than silently skipping.

---

### Distraction
*Something in the UI suddenly appears or otherwise draws the user's attention, distracting them from their goal.*

**Detection procedure (pass one — flag, do not filter).** *Unit: per-screen; appearing elements need flow/live evidence.*
1. From the C2 goal set, survey the artifact for the definitional conditions above.
2. Flag every candidate where the conditions appear present; name the specific cue(s)/element(s) and the condition(s) observed (G6).
3. Where a condition cannot be evaluated from this artifact or without a context field, record that as the reason per G4 rather than silently skipping.

---

### Uncomprehended Element
*A cue (label, icon, affordance, or prompt) critical to achieving a goal is noticed, but its meaning, or the required method of interacting with it, is unclear.*

**Detection procedure (pass one — flag, do not filter).** *Unit: per-screen.*
1. From the C2 goal set, survey the artifact for the definitional conditions above.
2. Flag every candidate where the conditions appear present; name the specific cue(s)/element(s) and the condition(s) observed (G6).
3. Where a condition cannot be evaluated from this artifact or without a context field, record that as the reason per G4 rather than silently skipping.

---

### Inviting Dead End
*A cue (label, icon, affordance, or prompt) is incorrectly judged as a means for achieving a goal. It looks right, but is wrong.*

**Detection procedure (pass one — flag, do not filter).** *Unit: per-screen for candidates; destination verification needs flows/live/code.*
1. From the C2 goal set, survey the artifact for the definitional conditions above.
2. Flag every candidate where the conditions appear present; name the specific cue(s)/element(s) and the condition(s) observed (G6).
3. Where a condition cannot be evaluated from this artifact or without a context field, record that as the reason per G4 rather than silently skipping.

---

### Poor Grouping
*A critical relationship between two or more otherwise noticeable cues (labels, icons, affordances, or prompts) is not obvious.*

**Detection procedure (pass one — flag, do not filter).** *Unit: per-screen.*
1. From the C2 goal set, survey the artifact for the definitional conditions above.
2. Flag every candidate where the conditions appear present; name the specific cue(s)/element(s) and the condition(s) observed (G6).
3. Where a condition cannot be evaluated from this artifact or without a context field, record that as the reason per G4 rather than silently skipping.

---

### Forced Syntax
*The system does not allow the user to issue a command or complete a sequence of actions in the order or manner that is most natural to them.*

**Detection procedure (pass one — flag, do not filter).** *Unit: cross-screen/flow by nature; statics show risk only.*
1. From the C2 goal set, survey the artifact for the definitional conditions above.
2. Flag every candidate where the conditions appear present; name the specific cue(s)/element(s) and the condition(s) observed (G6).
3. Where a condition cannot be evaluated from this artifact or without a context field, record that as the reason per G4 rather than silently skipping.

---

### Memory Challenge
*The system requires the user to remember information that is easy to forget.*

**Detection procedure (pass one — flag, do not filter).** *Unit: cross-screen (carries) and per-screen (recall demands).*
1. From the C2 goal set, survey the artifact for the definitional conditions above.
2. Flag every candidate where the conditions appear present; name the specific cue(s)/element(s) and the condition(s) observed (G6).
3. Where a condition cannot be evaluated from this artifact or without a context field, record that as the reason per G4 rather than silently skipping.

---

### Feedback Failure
*The system fails to provide noticeable, comprehensible, and actionable feedback in response to user actions.*

**Detection procedure (pass one — flag, do not filter).** *Unit: cross-screen: audit action→response pairs; visible messages auditable per-screen.*
1. From the C2 goal set, survey the artifact for the definitional conditions above.
2. Flag every candidate where the conditions appear present; name the specific cue(s)/element(s) and the condition(s) observed (G6).
3. Where a condition cannot be evaluated from this artifact or without a context field, record that as the reason per G4 rather than silently skipping.

---

### Physical Challenge
*An action the system requires the user to perform is physically effortful, difficult, or impossible.*

**Detection procedure (pass one — flag, do not filter).** *Unit: per-screen for visible physical demands.*
1. From the C2 goal set, survey the artifact for the definitional conditions above.
2. Flag every candidate where the conditions appear present; name the specific cue(s)/element(s) and the condition(s) observed (G6).
3. Where a condition cannot be evaluated from this artifact or without a context field, record that as the reason per G4 rather than silently skipping.

---

### Accidental Activation
*The system misinterprets a user's physical actions resulting in an unintended outcome.*

**Detection procedure (pass one — flag, do not filter).** *Unit: whole-artifact; behavior evidence needed.*
1. From the C2 goal set, survey the artifact for the definitional conditions above.
2. Flag every candidate where the conditions appear present; name the specific cue(s)/element(s) and the condition(s) observed (G6).
3. Where a condition cannot be evaluated from this artifact or without a context field, record that as the reason per G4 rather than silently skipping.

---

### Slow or No Response
*The user is prevented from achieving a goal in a timely manner because of actual or perceived poor system performance.*

**Detection procedure (pass one — flag, do not filter).** *Unit: per-interaction; live/measured artifacts.*
1. From the C2 goal set, survey the artifact for the definitional conditions above.
2. Flag every candidate where the conditions appear present; name the specific cue(s)/element(s) and the condition(s) observed (G6).
3. Where a condition cannot be evaluated from this artifact or without a context field, record that as the reason per G4 rather than silently skipping.

---

### Captive Wait
*The user is prevented from achieving a goal in a timely manner because the system intentionally prevents them from advancing and/or backing out of a process.*

**Detection procedure (pass one — flag, do not filter).** *Unit: cross-screen (flow states).*
1. From the C2 goal set, survey the artifact for the definitional conditions above.
2. Flag every candidate where the conditions appear present; name the specific cue(s)/element(s) and the condition(s) observed (G6).
3. Where a condition cannot be evaluated from this artifact or without a context field, record that as the reason per G4 rather than silently skipping.

---

### Unnecessary Step
*When the product is being used as intended, the number of actual or perceived steps required to achieve a goal is too high.*

**Detection procedure (pass one — flag, do not filter).** *Unit: cross-screen (flows); statics show risk only.*
1. From the C2 goal set, survey the artifact for the definitional conditions above.
2. Flag every candidate where the conditions appear present; name the specific cue(s)/element(s) and the condition(s) observed (G6).
3. Where a condition cannot be evaluated from this artifact or without a context field, record that as the reason per G4 rather than silently skipping.

---

### System Amnesia
*The system re-prompts the user for information it previously gathered, or otherwise fails to leverage the user's prior work.*

**Detection procedure (pass one — flag, do not filter).** *Unit: cross-screen/cross-session.*
1. From the C2 goal set, survey the artifact for the definitional conditions above.
2. Flag every candidate where the conditions appear present; name the specific cue(s)/element(s) and the condition(s) observed (G6).
3. Where a condition cannot be evaluated from this artifact or without a context field, record that as the reason per G4 rather than silently skipping.

---

### Information Overload
*Information presented to the user is comprehensible, but there is too much of it.*

**Detection procedure (pass one — flag, do not filter).** *Unit: per-screen.*
1. From the C2 goal set, survey the artifact for the definitional conditions above.
2. Flag every candidate where the conditions appear present; name the specific cue(s)/element(s) and the condition(s) observed (G6).
3. Where a condition cannot be evaluated from this artifact or without a context field, record that as the reason per G4 rather than silently skipping.

---

### Bad Prediction
*The system incorrectly predicts or interprets the user's intent or preference, resulting in the user having to work around the problem.*

**Detection procedure (pass one — flag, do not filter).** *Unit: whole-artifact feature inventory.*
1. From the C2 goal set, survey the artifact for the definitional conditions above.
2. Flag every candidate where the conditions appear present; name the specific cue(s)/element(s) and the condition(s) observed (G6).
3. Where a condition cannot be evaluated from this artifact or without a context field, record that as the reason per G4 rather than silently skipping.

---

### Irreversible Action
*The system does not allow the user to undo an action they have taken.*

**Detection procedure (pass one — flag, do not filter).** *Unit: cross-screen (flows/code).*
1. From the C2 goal set, survey the artifact for the definitional conditions above.
2. Flag every candidate where the conditions appear present; name the specific cue(s)/element(s) and the condition(s) observed (G6).
3. Where a condition cannot be evaluated from this artifact or without a context field, record that as the reason per G4 rather than silently skipping.

---

### Unwanted Disclosure
*The system makes the user's data or behavior public in a way that is harmful or embarrassing to the user.*

**Detection procedure (pass one — flag, do not filter).** *Unit: whole-artifact + settings.*
1. From the C2 goal set, survey the artifact for the definitional conditions above.
2. Flag every candidate where the conditions appear present; name the specific cue(s)/element(s) and the condition(s) observed (G6).
3. Where a condition cannot be evaluated from this artifact or without a context field, record that as the reason per G4 rather than silently skipping.

---

### Data Loss
*The system can lose the user's work through some action or inaction on the user's part.*

**Detection procedure (pass one — flag, do not filter).** *Unit: cross-screen + failure modes.*
1. From the C2 goal set, survey the artifact for the definitional conditions above.
2. Flag every candidate where the conditions appear present; name the specific cue(s)/element(s) and the condition(s) observed (G6).
3. Where a condition cannot be evaluated from this artifact or without a context field, record that as the reason per G4 rather than silently skipping.

---

### Gratuitous Redundancy
*The system presents duplicate cues (labels, icons, affordances, or prompts) for the same action on the same level, or a directly nested level of the UI.*

**Detection procedure (pass one — flag, do not filter).** *Unit: per-screen/per-level.*
1. From the C2 goal set, survey the artifact for the definitional conditions above.
2. Flag every candidate where the conditions appear present; name the specific cue(s)/element(s) and the condition(s) observed (G6).
3. Where a condition cannot be evaluated from this artifact or without a context field, record that as the reason per G4 rather than silently skipping.

---

### Variable Outcome
*The system responds differently at different times to the same user action.*

**Detection procedure (pass one — flag, do not filter).** *Unit: cross-state/cross-time.*
1. From the C2 goal set, survey the artifact for the definitional conditions above.
2. Flag every candidate where the conditions appear present; name the specific cue(s)/element(s) and the condition(s) observed (G6).
3. Where a condition cannot be evaluated from this artifact or without a context field, record that as the reason per G4 rather than silently skipping.

---

### Wandering Element
*The physical location of a cue (label, icon, affordance, or prompt) for a given action varies across the UI.*

**Detection procedure (pass one — flag, do not filter).** *Unit: cross-screen by nature.*
1. From the C2 goal set, survey the artifact for the definitional conditions above.
2. Flag every candidate where the conditions appear present; name the specific cue(s)/element(s) and the condition(s) observed (G6).
3. Where a condition cannot be evaluated from this artifact or without a context field, record that as the reason per G4 rather than silently skipping.

---

### Inconsistent Appearance
*The visual appearance of a cue (label, icon, affordance, or prompt) for a given action varies across the UI.*

**Detection procedure (pass one — flag, do not filter).** *Unit: cross-screen by nature.*
1. From the C2 goal set, survey the artifact for the definitional conditions above.
2. Flag every candidate where the conditions appear present; name the specific cue(s)/element(s) and the condition(s) observed (G6).
3. Where a condition cannot be evaluated from this artifact or without a context field, record that as the reason per G4 rather than silently skipping.

---

### Ambiguous Home
*The UI provides no single place the user can return to at any time to begin a new task or get re-oriented.*

**Detection procedure (pass one — flag, do not filter).** *Unit: whole-IA / cross-screen.*
1. From the C2 goal set, survey the artifact for the definitional conditions above.
2. Flag every candidate where the conditions appear present; name the specific cue(s)/element(s) and the condition(s) observed (G6).
3. Where a condition cannot be evaluated from this artifact or without a context field, record that as the reason per G4 rather than silently skipping.

---

### Unattractive Appearance
*The UI is aesthetically unpleasing, inconsistent, and/or inappropriate for its intended users.*

**Detection procedure (pass one — flag, do not filter).** *Unit: per-screen + cross-screen consistency.*
1. From the C2 goal set, survey the artifact for the definitional conditions above.
2. Flag every candidate where the conditions appear present; name the specific cue(s)/element(s) and the condition(s) observed (G6).
3. Where a condition cannot be evaluated from this artifact or without a context field, record that as the reason per G4 rather than silently skipping.

---
