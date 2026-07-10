<!-- GENERATED from trap_kb_v2.md — do not edit; regenerate on any master edit -->
### TRAP: AMBIGUOUS HOME *(ratified 2026-07-04)*
*Sub-tenet: Well-Oriented*

**Definition.** The interface presents multiple, competing locations for getting oriented and initiating tasks. A single reliable home — one place, reachable from anywhere by one consistent action — is the anchor from which navigational habituation flows and the automatic recovery point when users get lost. When home is ambiguous, users must hold the structure in conscious memory and reason their way back — the burden habituation should have removed.

**Boundary.** IS: two or more plausible homes, or an inconsistent action for reaching home. Scope test: this Trap is exclusively about the product's GLOBAL home — the top-level anchor of the whole navigation system. Multiple competing entry points to a specific feature or task are Gratuitous Redundancy, not this Trap; ask "is the ambiguity about where to start in the whole product, or about which element to use for a specific task?" The manuscript frames it as a special case of its neighbors — multiple homes is a redundancy problem, an inconsistent home action a consistency problem — but it is its own Trap with its own fix (consolidation). NOT present when: one clearly defined home is reachable from every context via one consistent action; the product is deliberately homeless because all tasks are self-contained; apparent multiple homes are entry points to clearly distinct, non-overlapping sections users understand as separate. Co-occurring: **Gratuitous Redundancy** when the homes duplicate capabilities (confirm the overlap); **Variable Outcome** when the home action lands differently at different times (separate evidence); **Memory Challenge** downstream when users must consciously track location because no reliable home exists (confirm); **Poor Grouping** when overlapping capabilities blur the mental model. Home iconography used for non-home destinations (a house icon on a Library button — the Meta VR case) is an **Inviting Dead End** compounding this Trap.

**Detection procedure (pass one — flag, do not filter).** *Unit: cross-screen/whole-IA.*
1. Identify every element or location that could plausibly be read as a starting point / orientation anchor (landing screens, dashboards, home-labeled or home-iconed destinations, launcher surfaces). More than one candidate = flag.
2. Audit the return-home action from every context: same action everywhere? single-step everywhere? Flag inconsistencies and multi-step returns.
3. Flag home iconography attached to non-home destinations (routes to Inviting Dead End co-listing).
4. Multi-platform/multi-mode products: compare home conventions across modes (the Windows 8 two-homes case).

**Disconfirmation (pass two).** Per Boundary conditions.

**Severity.** Medium — disorientation, orientation attention-tax on every task start; High when users cannot recover from being lost (deep hierarchies where home is the recovery mechanism) or abandon. Anchor: two competing Start/Home experiences, one per input mode (card example): Medium–High — orientation is the recovery mechanism, and it forked. Escalators: C4 (orientation happens every session, forever); product complexity.

**Assessability & Confidence.** Medium confidence from design files (candidate homes and return-action consistency are structural; which one users *conceptualize* as home needs user knowledge) — promotion path: ask users unprompted where they'd go to start a task or recover; inconsistent answers confirm. High confidence for the return-action inconsistency half (directly auditable). Context axis: C1 gates the conceptualization judgment; C4 weights severity.

**Attribution.** Per Boundary — each co-Trap independently evidenced; this Trap is root cause where consolidation dissolves the others (fix-based).

**Report fragments.** Finding: "The interface offers [N] plausible homes — [list] — producing different starting contexts and preventing a single orientation habit; the return-home action is [inconsistent across contexts]." Why it matters: "Without one reliable home, disoriented users must reason their way back instead of reaching automatically — orientation permanently taxes attention that habituation should have freed."

**Remediation.** Consolidate to one home — not better labeling of several. One destination, one action, consistent across every context and input mode. Reserve home iconography exclusively for the primary home. Audit every new entry point for whether it creates a competing home.
