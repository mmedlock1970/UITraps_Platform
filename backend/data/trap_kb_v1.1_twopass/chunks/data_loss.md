<!-- GENERATED from trap_kb_v1.1.md — do not edit; regenerate on any master edit -->
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
