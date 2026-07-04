<!-- GENERATED from trap_kb_v2.1.md — do not edit; regenerate on any master edit -->
### TRAP: ACCIDENTAL ACTIVATION *(draft-grade)*
*Sub-tenet: —*

**Definition.** It's easy for the user to unintentionally trigger an action during normal use: controls at natural grip points, overloaded gestures, wake words overlapping ordinary speech, hair-trigger sensors.

**Boundary.** IS: insufficient physical/interaction barriers between normal use and unintended triggering, with NO intent inference involved (a button pressed accidentally is simply a button pressed). IS NOT **Bad Prediction**: when the system *interprets* an ambiguous signal as intent and guesses wrong (wake word in background conversation, gesture read from incidental movement), Bad Prediction is the root cause and the activation its consequence (fix-based: better prediction thresholds resolve it). IS NOT **Inviting Dead End**: that Trap lures a deliberate action; this one fails to prevent an undeliberate one. IS NOT **Physical Challenge** — mirror image; separate evidence each way. Reversibility of the triggered action reduces severity but does not disconfirm.

**Detection procedure (pass one — flag, do not filter).** *Unit: whole-artifact; requires device/form-factor context.*
1. Map controls against natural grip points, resting zones, and edge/corner contact areas for the device class; flag consequential controls located there.
2. Flag overloaded activations (double-tap, press-and-hold on grip surfaces), edge gestures adjacent to system gestures, and passive/sensor-based activations (proximity, motion, always-listening) — the last as candidates for Bad Prediction routing.
3. Flag hover-activated controls (menus, previews, tooltips-with-side-effects) positioned across common pointer paths — hover engagement during ordinary cursor travel is a static-detectable desktop case of this Trap.
4. For each flag, record the triggered action's consequence and reversibility (feeds severity).

**Disconfirmation (pass two).** NOT present when: (a) activation requires a deliberate, non-incidental action unlikely during normal handling; (b) the input vocabulary doesn't overlap natural behavior in the context of use (C3).

**Severity.** Scales with consequence × reversibility of the triggered action: accidental screenshot Low; accidental purchase High; accidental emergency call or recording Critical — for privacy/safety actions the acceptable false-trigger rate approaches zero. Escalators: C3 (motion, encumbrance, and pocketed/gripped carrying multiply incidental contact).

**Assessability & Confidence.** Probable ceiling from design files (placement vs. known grip zones flags candidates); actual activation behavior requires hardware testing — promotion path: realistic-use hardware trials. Context axis: C3 gates (grip, mobility, environment determine what "normal use" contacts); device class knowledge required — declare when absent.

**Attribution.** Bad Prediction routing (Boundary). Variable Outcome: overloaded controls whose outcome depends on unattended state make accidents worse — consistency is the root cause there; evidence separately.

**Report fragments.** Finding: "[Control/gesture] is positioned or configured so unintentional triggering is likely during normal use." Why it matters: "Accidental activations resist user care — severity scales with the reversibility and consequence of what fires."

**Remediation.** Add friction to the activation path: recess or shield controls, require sequential actions, add resistance, increase gesture distinctiveness. Confirmation dialogs are a last resort — they tax every intentional user (Unnecessary Step(s)); reserve for consequential AND irreversible actions after physical options are exhausted. Caution: friction added here can worsen Physical Challenge — calibrate together.
