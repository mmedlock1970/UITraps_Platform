<!-- GENERATED from trap_kb_v1.1.md — do not edit; regenerate on any master edit -->
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
