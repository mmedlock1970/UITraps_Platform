<!-- GENERATED from trap_kb_v1.1.md — do not edit; regenerate on any master edit -->
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
