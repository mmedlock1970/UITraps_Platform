<!-- GENERATED from trap_kb_v2.1.md — do not edit; regenerate on any master edit -->
### TRAP: INFORMATION OVERLOAD *(draft-grade)*

**Definition.** Information presented is understandable but exceeds what is needed: verbose instructions, wordy AI responses, cluttered displays, option-dense menus. Hick's Law prices it: decision time grows with choice count. The test is not "could there be less?" but "does the user need all of this right now?"

**Boundary.** IS: excess relative to the user's goal in this context. IS NOT present when the density is the task (data dashboards for comprehensive sensemaking), when everything shown is needed now, or when progressive disclosure is functioning. IS NOT **Distraction** (specific capture vs. diffuse excess — shared fix, separate evidence). Caused by **Gratuitous Redundancy** when duplicates inflate the count — confirm duplication independently; density alone can come from feature breadth or poor editing.

**Detection procedure (pass one — flag, do not filter).** *Unit: per-screen; menus/IA cross-screen.*
1. From the C2 goal, partition each screen's content: serves the likely goal now / secondary / serves no evident user goal.
2. Flag screens where the primary task requires processing only a small subset of what's displayed; count elements, options per decision point, and word counts of instructions/labels/errors against a plain-necessity read.
3. Flag verbosity per text element: could it shed half its words without losing clarity (the Krug test)?
4. Strongest static trigger — task burial: the primary action or call-to-action is buried within or beneath large text masses, or is not reachable without scrolling past content that does not serve the goal. Task burial is this Trap's clearest screenshot-grade evidence.
5. Homepages, dashboards, and navigation earn the closest read — accretion concentrates there.

**Disconfirmation (pass two).** NOT present when: (a) all of it is needed for the goal right now; (b) density is appropriate to comprehensive-sensemaking tasks; (c) progressive disclosure already gates the secondary tier.

**Severity.** Medium baseline (processing tax, Hick's-slowed decisions); High when the information cost exceeds motivation and users abandon. Escalators: C4 (a cluttered daily screen taxes forever); C3 (divided attention shrinks processing budget). Expert populations (C1) can legitimately need more — soften accordingly.

**Assessability & Confidence.** Probable ceiling — counts and densities measure Confirmed-grade, but necessity is goal-relative (C2 gates); promotion path: user task analysis or engagement data. Context axis: C2 gates; C1 softens for expert tools.

**Attribution.** Gratuitous Redundancy root cause when duplication inflates (confirm). Distraction co-occurring when specific elements also capture attention (separate evidence). Poor Grouping compounding: clutter obscures relationships — if decluttering restores the grouping read, this Trap is root cause (fix-based).

**Report fragments.** Finding: "[Screen] presents substantially more information than [goal] requires — [N elements / options / words] where [fewer] would serve." Why it matters: "Every element beyond what the goal requires taxes attention and decision speed on every use."

**Remediation.** Build outward from the likeliest goal; every element must earn its place. Progressive disclosure for the secondary tier. Cut text aggressively — get a professional writer. Fewer options per decision point. Audit regularly; interfaces accrete.
