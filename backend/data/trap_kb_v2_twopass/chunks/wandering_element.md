<!-- GENERATED from trap_kb_v2.md — do not edit; regenerate on any master edit -->
### TRAP: WANDERING ELEMENT *(ratified 2026-07-04)*
*Sub-tenet: Consistent with Expectations*

**Definition.** The same interface element is presented in a different location at different times — controls, status indicators, or content that move across screens, contexts, or app versions. Spatial memory is among the most powerful automaticities available to designers, and it costs nothing but the discipline of keeping things where they are; wandering squanders it — every displaced encounter pulls the user back into conscious search.

**Boundary.** IS: inconsistent *placement* of the same element across contexts. IS NOT **Inconsistent Appearance** — the manuscript's line: a control can wander without changing appearance and can change appearance without wandering; audit placement and visual form independently, evidence each separately. Downstream of it: **Effectively Invisible Element** — but confirm independently that the new position falls outside where users would look; do not infer invisibility from movement alone (fix-based: pinning the element resolves derivative noticing failures — Wandering Element is root cause). NOT present when: placement variation is context-appropriate and meaningful (a Share button positioned differently in reading vs. list view because the content relationship differs); the element is low-frequency (no spatial memory would form); the change is explicitly communicated through a design transition users will attend to.

**Detection procedure (pass one — flag, do not filter).** *Unit: cross-screen by nature — this Trap does not exist in a single screenshot; declare on single-screen artifacts.*
1. Identify recurring elements across the screens in scope; prioritize high-frequency controls — search, navigation, editing, confirmation — where spatial memory pays most.
2. Map each recurring element's position per context (coordinates/regions in design files make this directly auditable).
3. Flag every placement inconsistency, recording the contexts and displacement; note ecosystem-level wandering (the same platform control placed differently across an app family).

**Disconfirmation (pass two).** Simultaneously visible duplicates are never this Trap (author-ruled 2026-07-05) — it requires the SAME element appearing in DIFFERENT locations at different times; two elements present at once on one screen route to Gratuitous Redundancy (same function) or its lookalike fork (different functions). Per Boundary conditions.

**Severity.** Medium baseline — slowed habituation, conscious search on every encounter. Anchor: the Edit control appearing in different positions across sibling apps (card example): Medium — conscious search on every encounter. Escalates on C4 (high-frequency, time-sensitive controls: navigation, edit, search) and C3 (searching for a moved control while driving or under pressure). High when displacement of a critical control under time pressure costs the task (C3 conversion).

**Assessability & Confidence.** High confidence from multi-screen design files — cross-context placement comparison is directly auditable, one of the most automatable Traps, and precisely the audit human task-based reviews skip (an AI-native strength). Context axis: C4 gates severity weighting (frequency); largely population-independent for presence. Scoped coverage (always emitted, J27): "Wandering Element — a single screen cannot show an element occupying different locations at different times, so nothing is assessable within this artifact; not from this artifact: placement consistency across screens/states — multiple screens or a flow artifact would settle." A single-screen artifact therefore routes this Trap to "Couldn't evaluate" (not-assessable coverage), never to "Not present" / "Did not find" / silent absence.

**Attribution.** Inconsistent Appearance: independent co-audit (both may be present; separate evidence). Effectively Invisible Element downstream (fix-based, above). This Trap is invisible to task-based evaluation — flag the methodology gap in reports where relevant.

**Report fragments.** Finding: "[Control] appears in different positions across [contexts] — users who learned its location in one context must search in others." Why it matters: "Inconsistent placement prevents spatial memory from forming — every encounter demands conscious search that consistency would have made automatic."

**Remediation.** Establish placement conventions for high-frequency controls early and treat them as constraints. Map recurring elements' placement across every context; inconsistencies are the finding. Platform-level controls hold consistent positions across an ecosystem.
