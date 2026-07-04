<!-- GENERATED from trap_kb_v1.1.md — do not edit; regenerate on any master edit -->
# PASS ONE — DETECTION PACK (KB v1.1, two-pass structure)

**Role of this pass:** permissive detection. Run every procedure below. Flag every candidate with named evidence. Do NOT filter, weigh disconfirmation, or assign severity. Emit candidates as `TRAP | screen | cue(s)/element(s) | condition(s)` — one line each, no prose.

**G1. Exact trap names.** Use full, exact Trap names; several Traps have near-identical names that denote different problems.

**G2. Two-pass discipline, with selective loading.**
- **Pass one (detection):** load only the Detection Procedures for all 26 Traps, plus the Context Intake Schema. Run each procedure. Flag every candidate. Do not filter, do not weigh disconfirmation, do not assign severity. Over-reporting at this stage is correct behavior.
- **Pass two (adjudication):** load the full chunks for candidate Traps only, plus the Taxonomy Index. For each candidate, apply in order: (1) Disconfirmation; (2) the one-problem-one-issue procedure (G3); (3) the Assessability lookup (G4/G5); (4) Severity and Confidence; (5) assemble the issue per G8.

**G6. Named evidence.** Every flag, in either pass, must cite the specific cue(s)/element(s) and condition(s) that triggered it. General impressions are not findings. (Per the deck's How to Use, step 3: identify and log any Traps observed; note their severity; log all.)

**G7. Unit of analysis.** Detection Procedures declare their unit: per-screen, cross-screen, or both. For multi-screen artifacts: run per-screen steps on every screen in scope; run cross-screen steps where declared; a persistent element rendered across screens is ONE element. Every finding cites the screen(s) where its evidence sits.

---

## CONTEXT INTAKE SCHEMA (C1–C4)

**C1. User Knowledge.** Products and conventions the users have already internalized; domain expertise; novice/expert mix; prior exposure to this product's conventions. *Default when absent:* general adult population familiar with mainstream web/mobile conventions — declare it. Brand-specific, domain-insider, and novel cues cannot be cleared under the default.

**C2. Goals.** The user's primary tasks and critical paths — AND the fuller set of goals users might plausibly bring to each screen. *Default when absent:* infer the apparent primary task from the screen itself and declare it; findings requiring the full goal set are degraded under this default.

**C3. Context of Use.** Availability of the user's channels and circumstances: attention (focused / divided / interrupted); vision (available / occupied); hearing (quiet / noisy); speech & audio-out (free / constrained by others or privacy); hands (both free / one / none); mobility (stationary / in motion); plus lighting, time pressure, device and input method. *Default when absent:* attentive, stationary, unencumbered, quiet, private use — the most forgiving context on every channel. Declare it, and state that findings under this default are a lower bound.

**C4. Exposure & Repetition.** User exposure stage (first-run / habituated / mixed) and task repetition profile (once / a few times / recurring). Habituating-tenet Traps scale with repetition; one-time tasks make comprehension Traps paramount. *Defaults when absent:* mixed exposure including first-time users for public-facing products; infer the task's repetition profile from its nature — declare both.

---

---

## DETECTION PROCEDURES (all 26 Traps)

### Invisible Element
**Definitional conditions (decomposed from the definition sentence; the Trap requires all):** (a) no cue signals how to achieve a goal the user plausibly holds (C2); (b) the user population lacks sufficient prior learning to overcome the absence (C1).

**Detection procedure (pass one — flag, do not filter).** *Unit: per-screen, against the goal set.*
1. From the C2 goal set, survey the artifact for the definitional conditions above.
2. Flag every candidate where the conditions appear present; name the specific cue(s)/element(s) and the condition(s) observed (G6).
3. Where a condition cannot be evaluated from this artifact or without a context field, record that as the reason per G4 rather than silently skipping.

---

### Effectively Invisible Element
**Definitional conditions (decomposed from the definition sentence; the Trap requires all):** (a) a cue is provided; (b) it is likely to go unnoticed or be slow to be noticed; (c) because its appearance or location differs from what the user expects (C1/C2).

**Detection procedure (pass one — flag, do not filter).** *Unit: per-screen.*
1. From the C2 goal set, survey the artifact for the definitional conditions above.
2. Flag every candidate where the conditions appear present; name the specific cue(s)/element(s) and the condition(s) observed (G6).
3. Where a condition cannot be evaluated from this artifact or without a context field, record that as the reason per G4 rather than silently skipping.

---

### Distraction
**Definitional conditions (decomposed from the definition sentence; the Trap requires all):** (a) something in the UI suddenly appears or otherwise draws attention; (b) it distracts the user from their goal (C2).

**Detection procedure (pass one — flag, do not filter).** *Unit: per-screen; appearing elements need flow/live evidence.*
1. From the C2 goal set, survey the artifact for the definitional conditions above.
2. Flag every candidate where the conditions appear present; name the specific cue(s)/element(s) and the condition(s) observed (G6).
3. Where a condition cannot be evaluated from this artifact or without a context field, record that as the reason per G4 rather than silently skipping.

---

### Uncomprehended Element
**Definitional conditions (decomposed from the definition sentence; the Trap requires all):** (a) the cue is critical to achieving a goal (C2); (b) it is noticed; (c) its meaning or required interaction method is unclear to the population (C1).

**Detection procedure (pass one — flag, do not filter).** *Unit: per-screen.*
1. From the C2 goal set, survey the artifact for the definitional conditions above.
2. Flag every candidate where the conditions appear present; name the specific cue(s)/element(s) and the condition(s) observed (G6).
3. Where a condition cannot be evaluated from this artifact or without a context field, record that as the reason per G4 rather than silently skipping.

---

### Inviting Dead End
**Definitional conditions (decomposed from the definition sentence; the Trap requires all):** (a) a cue is likely to be judged a means to a goal the user plausibly holds (C2); (b) it is in fact wrong for that goal.

**Detection procedure (pass one — flag, do not filter).** *Unit: per-screen for candidates; destination verification needs flows/live/code.*
1. From the C2 goal set, survey the artifact for the definitional conditions above.
2. Flag every candidate where the conditions appear present; name the specific cue(s)/element(s) and the condition(s) observed (G6).
3. Where a condition cannot be evaluated from this artifact or without a context field, record that as the reason per G4 rather than silently skipping.

---

### Poor Grouping
**Definitional conditions (decomposed from the definition sentence; the Trap requires all):** (a) two or more noticeable cues bear a relationship; (b) the relationship is critical to a goal (C2); (c) the relationship is not obvious.

**Detection procedure (pass one — flag, do not filter).** *Unit: per-screen.*
1. From the C2 goal set, survey the artifact for the definitional conditions above.
2. Flag every candidate where the conditions appear present; name the specific cue(s)/element(s) and the condition(s) observed (G6).
3. Where a condition cannot be evaluated from this artifact or without a context field, record that as the reason per G4 rather than silently skipping.

---

### Forced Syntax
**Definitional conditions (decomposed from the definition sentence; the Trap requires all):** (a) a command or action sequence exists for a goal; (b) the order or manner most natural to the user (C1) is not allowed by the system.

**Detection procedure (pass one — flag, do not filter).** *Unit: cross-screen/flow by nature; statics show risk only.*
1. From the C2 goal set, survey the artifact for the definitional conditions above.
2. Flag every candidate where the conditions appear present; name the specific cue(s)/element(s) and the condition(s) observed (G6).
3. Where a condition cannot be evaluated from this artifact or without a context field, record that as the reason per G4 rather than silently skipping.

---

### Memory Challenge
**Definitional conditions (decomposed from the definition sentence; the Trap requires all):** (a) the system requires the user to remember information; (b) that information is easy to forget.

**Detection procedure (pass one — flag, do not filter).** *Unit: cross-screen (carries) and per-screen (recall demands).*
1. From the C2 goal set, survey the artifact for the definitional conditions above.
2. Flag every candidate where the conditions appear present; name the specific cue(s)/element(s) and the condition(s) observed (G6).
3. Where a condition cannot be evaluated from this artifact or without a context field, record that as the reason per G4 rather than silently skipping.

---

### Feedback Failure
**Definitional conditions (decomposed from the definition sentence; the Trap requires all):** (a) a user action occurs; (b) the feedback in response is not noticeable, or not comprehensible, or not actionable.

**Detection procedure (pass one — flag, do not filter).** *Unit: cross-screen: audit action→response pairs; visible messages auditable per-screen.*
1. From the C2 goal set, survey the artifact for the definitional conditions above.
2. Flag every candidate where the conditions appear present; name the specific cue(s)/element(s) and the condition(s) observed (G6).
3. Where a condition cannot be evaluated from this artifact or without a context field, record that as the reason per G4 rather than silently skipping.

---

### Physical Challenge
**Definitional conditions (decomposed from the definition sentence; the Trap requires all):** (a) the system requires a physical action; (b) that action is physically effortful, difficult, or impossible for the population (C1) in the context (C3).

**Detection procedure (pass one — flag, do not filter).** *Unit: per-screen for visible physical demands.*
1. From the C2 goal set, survey the artifact for the definitional conditions above.
2. Flag every candidate where the conditions appear present; name the specific cue(s)/element(s) and the condition(s) observed (G6).
3. Where a condition cannot be evaluated from this artifact or without a context field, record that as the reason per G4 rather than silently skipping.

---

### Accidental Activation
**Definitional conditions (decomposed from the definition sentence; the Trap requires all):** (a) the user takes a physical action; (b) the system misinterprets it; (c) an unintended outcome results.

**Detection procedure (pass one — flag, do not filter).** *Unit: whole-artifact; behavior evidence needed.*
1. From the C2 goal set, survey the artifact for the definitional conditions above.
2. Flag every candidate where the conditions appear present; name the specific cue(s)/element(s) and the condition(s) observed (G6).
3. Where a condition cannot be evaluated from this artifact or without a context field, record that as the reason per G4 rather than silently skipping.

---

### Slow or No Response
**Definitional conditions (decomposed from the definition sentence; the Trap requires all):** (a) the user pursues a goal (C2); (b) actual or perceived system performance prevents timely achievement.

**Detection procedure (pass one — flag, do not filter).** *Unit: per-interaction; live/measured artifacts.*
1. From the C2 goal set, survey the artifact for the definitional conditions above.
2. Flag every candidate where the conditions appear present; name the specific cue(s)/element(s) and the condition(s) observed (G6).
3. Where a condition cannot be evaluated from this artifact or without a context field, record that as the reason per G4 rather than silently skipping.

---

### Captive Wait
**Definitional conditions (decomposed from the definition sentence; the Trap requires all):** (a) the user is in a process toward a goal (C2); (b) the system intentionally prevents advancing and/or backing out; (c) timely achievement is prevented.

**Detection procedure (pass one — flag, do not filter).** *Unit: cross-screen (flow states).*
1. From the C2 goal set, survey the artifact for the definitional conditions above.
2. Flag every candidate where the conditions appear present; name the specific cue(s)/element(s) and the condition(s) observed (G6).
3. Where a condition cannot be evaluated from this artifact or without a context field, record that as the reason per G4 rather than silently skipping.

---

### Unnecessary Step
**Definitional conditions (decomposed from the definition sentence; the Trap requires all):** (a) the product is used as intended; (b) actual or perceived steps to a goal (C2) exceed what is needed.

**Detection procedure (pass one — flag, do not filter).** *Unit: cross-screen (flows); statics show risk only.*
1. From the C2 goal set, survey the artifact for the definitional conditions above.
2. Flag every candidate where the conditions appear present; name the specific cue(s)/element(s) and the condition(s) observed (G6).
3. Where a condition cannot be evaluated from this artifact or without a context field, record that as the reason per G4 rather than silently skipping.

---

### System Amnesia
**Definitional conditions (decomposed from the definition sentence; the Trap requires all):** (a) the system previously gathered information or prior work exists; (b) the system re-prompts for it or fails to leverage it.

**Detection procedure (pass one — flag, do not filter).** *Unit: cross-screen/cross-session.*
1. From the C2 goal set, survey the artifact for the definitional conditions above.
2. Flag every candidate where the conditions appear present; name the specific cue(s)/element(s) and the condition(s) observed (G6).
3. Where a condition cannot be evaluated from this artifact or without a context field, record that as the reason per G4 rather than silently skipping.

---

### Information Overload
**Definitional conditions (decomposed from the definition sentence; the Trap requires all):** (a) information presented is comprehensible; (b) there is more of it than the goal (C2) requires.

**Detection procedure (pass one — flag, do not filter).** *Unit: per-screen.*
1. From the C2 goal set, survey the artifact for the definitional conditions above.
2. Flag every candidate where the conditions appear present; name the specific cue(s)/element(s) and the condition(s) observed (G6).
3. Where a condition cannot be evaluated from this artifact or without a context field, record that as the reason per G4 rather than silently skipping.

---

### Bad Prediction
**Definitional conditions (decomposed from the definition sentence; the Trap requires all):** (a) the system predicts or interprets intent/preference; (b) the prediction is incorrect for this user (C1/C2); (c) the user must work around it.

**Detection procedure (pass one — flag, do not filter).** *Unit: whole-artifact feature inventory.*
1. From the C2 goal set, survey the artifact for the definitional conditions above.
2. Flag every candidate where the conditions appear present; name the specific cue(s)/element(s) and the condition(s) observed (G6).
3. Where a condition cannot be evaluated from this artifact or without a context field, record that as the reason per G4 rather than silently skipping.

---

### Irreversible Action
**Definitional conditions (decomposed from the definition sentence; the Trap requires all):** (a) the user takes an action; (b) the system provides no way to undo it.

**Detection procedure (pass one — flag, do not filter).** *Unit: cross-screen (flows/code).*
1. From the C2 goal set, survey the artifact for the definitional conditions above.
2. Flag every candidate where the conditions appear present; name the specific cue(s)/element(s) and the condition(s) observed (G6).
3. Where a condition cannot be evaluated from this artifact or without a context field, record that as the reason per G4 rather than silently skipping.

---

### Unwanted Disclosure
**Definitional conditions (decomposed from the definition sentence; the Trap requires all):** (a) the system makes user data or behavior public; (b) the disclosure is harmful or embarrassing to the user (C3 context).

**Detection procedure (pass one — flag, do not filter).** *Unit: whole-artifact + settings.*
1. From the C2 goal set, survey the artifact for the definitional conditions above.
2. Flag every candidate where the conditions appear present; name the specific cue(s)/element(s) and the condition(s) observed (G6).
3. Where a condition cannot be evaluated from this artifact or without a context field, record that as the reason per G4 rather than silently skipping.

---

### Data Loss
**Definitional conditions (decomposed from the definition sentence; the Trap requires all):** (a) the user creates work; (b) a user action or inaction can cause the system to lose it.

**Detection procedure (pass one — flag, do not filter).** *Unit: cross-screen + failure modes.*
1. From the C2 goal set, survey the artifact for the definitional conditions above.
2. Flag every candidate where the conditions appear present; name the specific cue(s)/element(s) and the condition(s) observed (G6).
3. Where a condition cannot be evaluated from this artifact or without a context field, record that as the reason per G4 rather than silently skipping.

---

### Gratuitous Redundancy
**Definitional conditions (decomposed from the definition sentence; the Trap requires all):** (a) two or more cues serve the same action; (b) they sit on the same level or a directly nested level.

**Detection procedure (pass one — flag, do not filter).** *Unit: per-screen/per-level.*
1. From the C2 goal set, survey the artifact for the definitional conditions above.
2. Flag every candidate where the conditions appear present; name the specific cue(s)/element(s) and the condition(s) observed (G6).
3. Where a condition cannot be evaluated from this artifact or without a context field, record that as the reason per G4 rather than silently skipping.

---

### Variable Outcome
**Definitional conditions (decomposed from the definition sentence; the Trap requires all):** (a) the same user action occurs at different times; (b) the system's response differs.

**Detection procedure (pass one — flag, do not filter).** *Unit: cross-state/cross-time.*
1. From the C2 goal set, survey the artifact for the definitional conditions above.
2. Flag every candidate where the conditions appear present; name the specific cue(s)/element(s) and the condition(s) observed (G6).
3. Where a condition cannot be evaluated from this artifact or without a context field, record that as the reason per G4 rather than silently skipping.

---

### Wandering Element
**Definitional conditions (decomposed from the definition sentence; the Trap requires all):** (a) the same cue serves a given action in multiple UI contexts; (b) its physical location varies across them.

**Detection procedure (pass one — flag, do not filter).** *Unit: cross-screen by nature.*
1. From the C2 goal set, survey the artifact for the definitional conditions above.
2. Flag every candidate where the conditions appear present; name the specific cue(s)/element(s) and the condition(s) observed (G6).
3. Where a condition cannot be evaluated from this artifact or without a context field, record that as the reason per G4 rather than silently skipping.

---

### Inconsistent Appearance
**Definitional conditions (decomposed from the definition sentence; the Trap requires all):** (a) the same cue serves a given action in multiple UI contexts; (b) its visual appearance varies across them.

**Detection procedure (pass one — flag, do not filter).** *Unit: cross-screen by nature.*
1. From the C2 goal set, survey the artifact for the definitional conditions above.
2. Flag every candidate where the conditions appear present; name the specific cue(s)/element(s) and the condition(s) observed (G6).
3. Where a condition cannot be evaluated from this artifact or without a context field, record that as the reason per G4 rather than silently skipping.

---

### Ambiguous Home
**Definitional conditions (decomposed from the definition sentence; the Trap requires all):** (a) users need a place to begin new tasks or re-orient; (b) no single such place is reliably reachable at any time.

**Detection procedure (pass one — flag, do not filter).** *Unit: whole-IA / cross-screen.*
1. From the C2 goal set, survey the artifact for the definitional conditions above.
2. Flag every candidate where the conditions appear present; name the specific cue(s)/element(s) and the condition(s) observed (G6).
3. Where a condition cannot be evaluated from this artifact or without a context field, record that as the reason per G4 rather than silently skipping.

---

### Unattractive Appearance
**Definitional conditions (decomposed from the definition sentence; the Trap requires all):** (a) the UI's aesthetics are unpleasing, inconsistent, and/or inappropriate; (b) judged against its intended users (C1).

**Detection procedure (pass one — flag, do not filter).** *Unit: per-screen + cross-screen consistency.*
1. From the C2 goal set, survey the artifact for the definitional conditions above.
2. Flag every candidate where the conditions appear present; name the specific cue(s)/element(s) and the condition(s) observed (G6).
3. Where a condition cannot be evaluated from this artifact or without a context field, record that as the reason per G4 rather than silently skipping.
