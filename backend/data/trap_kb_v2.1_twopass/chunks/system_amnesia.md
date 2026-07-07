<!-- GENERATED from trap_kb_v2.1.md — do not edit; regenerate on any master edit -->
### TRAP: SYSTEM AMNESIA *(ratified 2026-07-04)*

**Definition.** The system fails to take advantage of the user's prior work, preferences, or context: re-entering known information, recommendations ignoring ownership or history, context lost between sessions, re-authentication of the already-authenticated. Either the system never collected what it was exposed to, or collected it and doesn't use it.

**Boundary.** IS: the *system's* failure to leverage what it had. IS NOT **Memory Challenge** (the *user* made to remember) — both together (system has it AND user must recall it) make System Amnesia root cause (fix-based). IS NOT **Data Loss** (failing to *retain* what the user expects preserved vs. failing to *use* what it has). NOT present when re-prompting serves deliberate security/verification (though confirm-and-edit beats full re-entry even there), when architecture genuinely lacks access (verify it's actual, not assumed), or when the information may have changed (same superior pattern applies).

**Detection procedure (pass one — flag, do not filter).** *Unit: cross-screen/cross-session by nature.*
1. Inventory every point where the user supplies information or exhibits trackable behavior; then flag every later point that requests or ignores the same thing: repeated form fields, criteria re-stated, ownership-blind promotions, context dropped across sessions.
2. Strongest flag — self-evidencing amnesia: the system *displays* information while simultaneously requesting it, or comments on an action in a way proving it didn't register it (selling the user what the same screen shows they own; a machine asking if you knew it takes credit cards while processing your credit card).
3. Live/multi-session artifacts: probe cross-session recall (resume point, preferences, exclusions).

**Disconfirmation (pass two).** NOT present when: (a) deliberate security/verification re-prompting (still note confirm-and-edit as superior); (b) genuine architectural inaccessibility (verified); (c) plausibly-changed information (same note).

**Severity.** Medium baseline (friction, "not paying attention" perception — which directly undermines any personalization claim the product makes); grade upward by recreation cost — the volume of work recreated, the recall difficulty of the recreated information, and the error stakes of recreating it wrong; High when substantial or high-stakes prior work must be recreated (the doctor's-office intake form is the anchor case: months between sessions, maximal severity). Escalators: C4 (recurring re-entry compounds, whether within one session or across visits years apart). Proximity of the original entry does not grade severity. Attribution note: when the recreated information is itself hard to remember, Memory Challenge co-occurs as a consequence — the system's failure to retain imposes the recall burden (this Trap root cause, Memory Challenge consequence).

**Assessability & Confidence.** High confidence for self-evidencing cases (single screen suffices). Otherwise Medium confidence — knowing what the system *has* requires data-architecture knowledge or session history; promotion path: architecture review or multi-session probe. Context axis: largely context-free structurally; C2 sharpens severity (critical-path re-entry).

**Attribution.** Bad Prediction downstream: poor retention makes poor predictions — confirm both (available-but-unused data AND bad predictions) before chaining, System Amnesia as root cause. Memory Challenge pairing (above). Unwanted Disclosure tension: fixing amnesia means retaining data — remediation must note the security obligation.

**Report fragments.** Finding: "[Flow] requests [information] the system already has — or displays evidence it hasn't tracked prior behavior." Why it matters: "Re-asking for what it knows signals the system isn't paying attention — friction now, and erosion of every personalization claim the product makes."

**Remediation.** Retention by default: information provided once is available at every subsequent point. Share data across product contexts. Exclude owned/engaged content from recommendations. For AI systems, design cross-session memory deliberately. Governing question: could the system reasonably be expected to retain this? If yes, it should — and secure it (see Unwanted Disclosure).
