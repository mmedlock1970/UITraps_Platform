<!-- GENERATED from trap_kb_v2.1.md — do not edit; regenerate on any master edit -->
### TRAP: PHYSICAL CHALLENGE *(pilot-grade)*
*Sub-tenet: —*

**Definition.** Some aspect of the system causes physical discomfort or makes it physically difficult or impossible to complete actions: touch targets too small to hit reliably, text too faint to read without strain, controls beyond comfortable reach, device forms too heavy or sharp to hold, audio too quiet for the environment, surfaces too hot, VR video jittery enough to induce queasiness. The user understands what to do; doing it costs strain, discomfort, or harm.

**Boundary.** IS: a physical demand exceeding the population's capabilities in the real context of use (C1 physical range + C3 channels). IS NOT **Accidental Activation** — its mirror image: this Trap makes intended actions too hard; that one makes unintended actions too easy; the fixes pull in opposite directions and each requires separate evidence. IS NOT present when the demand falls within established guidelines for the expected population and context, when difficulty is the point (dexterity games), or when it exists only under unrealistic test conditions. Systems that respond *too fast* for users to track or act on are also housed here (per the manuscript's FAQ — there is no separate "too fast" Trap).

**Detection procedure (pass one — flag, do not filter).** *Unit: per-screen for measurables; whole-artifact for form-factor properties.*
1. Measure every interactive target against the ~12 mm finger-pad standard (platform minimums); flag undersized targets, tight spacing, and targets in hard-reach zones for the device size and expected grip (thumb-zone maps).
2. Measure text contrast against WCAG ratios and size against platform minimums at expected viewing distance; flag failures.
3. Enumerate channel demands and check each against C3: audio-dependent elements (flag if hearing may be unavailable), speech-required interactions (flag against speech/privacy constraints), two-handed or precision gestures (flag against hands/mobility), sustained-attention visuals (flag against motion).
4. Note form-factor properties not assessable from the artifact (weight, thermals, VR comfort) for the coverage notes rather than guessing.

**Disconfirmation (pass two).** NOT present when: (a) within established guidelines for the expected population and context; (b) difficulty is intentional and appropriate to the use case; (c) the difficulty exists only in test conditions that don't reflect real use.

**Severity.** Medium for targeting errors and legibility strain; High for exclusion — users who cannot complete actions at all (accessibility populations first); Critical for illness or injury (VR motion sickness, thermal harm). Note the fluency effect: hard-to-read text doesn't just strain — users judge the *product* as harder and disengage (legibility is an engagement variable, not just an accessibility one). Escalators: C3 (a marginal target in motion or one-handed becomes a failure); C4 (strain on a core loop compounds).

**Assessability & Confidence.** Confirmed for measurable properties from artifacts: target size, spacing, contrast ratio, font size — checkable against published standards. Not assessable from design files for weight, thermal, vestibular, and true one-handed reach — hardware testing required; declare, never guess. Context axis: C3 is this Trap's primary input — its default (unencumbered, quiet, stationary) makes findings a lower bound and can gate presence outright (a hands-occupied context creates Traps a hands-free one lacks); C1 physical-capability range gates population-specific judgments (the general default assumes typical adult ranges — declare).

**Attribution.** Accidental Activation: opposite failure modes; evaluate together (enlarging targets to fix this Trap can create that one) but evidence separately. Feedback Failure: absent tactile/visual confirmation is that Trap's route (4) — confirm the perception difficulty independently.

**Report fragments.** Finding: "[Element/interaction] imposes a physical demand exceeding [guideline / comfortable reach / legibility threshold] for [population / context]." Why it matters: "Physical barriers cause errors and exclusion — and reduce users' perception of overall product quality independent of the specific difficulty."

**Remediation.** Follow established standards: minimum target sizes, WCAG contrast, platform reach-zone guidance. Prototype on real hardware in realistic conditions — design-file analysis flags candidates but cannot confirm most instances. Improving contrast removes a barrier AND measurably increases engagement. Caution: calibrate against Accidental Activation when enlarging or sensitizing anything.
