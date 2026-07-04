<!-- GENERATED from trap_kb_v2.1.md — do not edit; regenerate on any master edit -->
### TRAP: POOR GROUPING *(draft-grade)*
*Sub-tenet: Comprehensible*

**Definition.** An important relationship between two or more interface elements is unclear. Covers visual/spatial relationships (unclear hierarchy, insufficient white space, ambiguous label-to-control mapping) AND conceptual organization within information architectures — menu hierarchies, navigation structures, content categorization (per the framework author's ruling in the manuscript's PG1).

**Boundary.** IS: a *relationship* failure between elements, where the relationship is critical to the user's goal. IS NOT about individual elements' meaning (Uncomprehended Element) or noticeability. IS NOT present when apparent groupings are functionally correct, when the relationship isn't goal-critical, or when a stronger cue (explicit labels, connecting lines, consistent treatment) overrides ambiguous proximity. When grouping ambiguity causes a specific wrong control to be chosen confidently, evaluate Inviting Dead End as co-occurring — this Trap is the root cause when fixing the spatial relationship dissolves the false invitation (fix-based rule).

**Detection procedure (pass one — flag, do not filter).** *Unit: per-screen; conceptual/IA form is cross-screen.*
1. From C2 goals, identify the element relationships the user must read correctly to proceed: label↔control mappings, option↔description pairings, group memberships, menu categorizations.
2. For each, evaluate against the Gestalt principles by name: proximity (related elements closer to each other than to competitors — the most commonly violated); similarity (same-function elements share visual properties; different-function elements don't mimic each other); common region (elements sharing a container read as related — flag unrelated elements in one container and related elements split across containers); continuity (alignment implies reading order); figure-ground (interactive elements read as figure). Common fate requires motion artifacts — declare on statics. **[JUDGMENT: equidistance or nearer-to-unrelated = strongest flag, per the manuscript's Tier-1 criterion.]**
3. Flag: controls equidistant between two plausible referents; labels nearer an unrelated element than their referent; conflicting Gestalt cues (proximity says one grouping, similarity another); IA form — menu items whose category membership a user could reasonably assign elsewhere.
4. Name the elements, the ambiguous relationship, AND the specific Gestalt principle violated per flag (G6) — a Poor Grouping flag that cannot cite a principle is not a flag; expected vs. actual grouping must both be stated.

**Disconfirmation (pass two).** NOT present when: (a) apparent groupings are functionally correct; (b) the relationship is not critical to the goal; (c) a stronger cue resolves the ambiguity; (d) conceptual groupings are obviously categorical.

**Severity.** Scales directly with the stakes of the action the grouping supports — from hesitation (Low) to confident wrong action at scale (the butterfly ballot altered a presidential election: Critical). Key property: users who misread a grouping act with confidence, not uncertainty. Escalators: C3 (time pressure and density worsen misreads).

**Assessability & Confidence.** Confirmed ceiling for measurable violations: a control measurably equidistant between competing options with no secondary disambiguation. Otherwise Probable — whether users read the ambiguity wrongly is population/goal-relative; promotion path: task-based observation with grouping-dependent tasks. Context axis: C1 softens (learned conventions can disambiguate); C2 determines criticality.

**Attribution.** Inviting Dead End: confirm a specific wrong choice results, not mere unclarity. Information Overload: confirm excess density contributes — clutter is both cause and symptom; if removing excess resolves the grouping read, Information Overload is root cause (fix-based). Uncomprehended Element: individually clear elements confusing in combination attribute here.

**Report fragments.** Finding: "The spatial or conceptual relationship between [elements] is ambiguous — users are likely to misread which [control/label/option] corresponds to which [referent]." Why it matters: "Users who misread this relationship take the wrong action with confidence, not uncertainty."

**Remediation.** Apply Gestalt principles deliberately: related elements closer to each other than to any competitor; white space as an active grouping tool; explicit separators (lines, containers, color) where proximity alone is insufficient. For IA: categorize by users' mental models, verified by card-sort-style checks. Test with users unfamiliar with the system on grouping-dependent tasks.
