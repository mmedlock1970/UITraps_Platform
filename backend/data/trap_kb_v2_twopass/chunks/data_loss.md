<!-- GENERATED from trap_kb_v2.md — do not edit; regenerate on any master edit -->
### TRAP: DATA LOSS *(ratified 2026-07-04)*

**Definition.** The system fails to retain information or content the user expects to be preserved: work lost to shutdowns without auto-save, forms discarding partial entries, co-authoring overwrites, ephemeral logs users assumed durable. Explicit-save is an engineering legacy, not a user requirement.

**Boundary.** IS: unintentional or inaction-triggered loss of user work/content. IS NOT **System Amnesia** (failing to *use* what it has vs. failing to *keep* what users expect kept — different causes, different fixes). NOT present when: continuous auto-save actually preserves it; the content is explicitly ephemeral and users are told before creating it; the user knowingly chose to discard. Co-occurs with **Irreversible Action** when a deliberate action destroys data with no undo (reversibility fixes both); accidental navigation-away losing an unsaved form is this Trap alone (system design, no deliberate act).

**Detection procedure (pass one — flag, do not filter).** *Unit: cross-screen + failure-mode analysis.*
1. Identify every point where the user creates or modifies data; for each run the failure-mode battery: session timeout? crash/shutdown? navigation away? network drop? concurrent edit?
2. Flag every point where any answer is "it could be lost": absent auto-save, unpreserved partial entries, last-write-wins co-authoring, dismiss-to-void inputs (comment boxes that vanish on outside-click), transient content users would expect durable (meeting chat logs).
3. Live artifacts: simulate the failure modes where safe; design files: flag structurally and mark simulation-needed.

**Disconfirmation (pass two).** Per Boundary (a)–(c).

**Severity.** Scales with the value of the lost work and recreation effort: Low for trivially re-entered inputs; High for substantial creative work or unrecreatable data; High when permanent and of high personal/professional value — data loss reads as fundamental system failure and destroys trust disproportionately. Anchor: unsaved work destroyed by a forced shutdown (card example): High — substantial work, no recovery; High when the work is unrecreatable and of high personal or professional value. Escalators: C3 (interruption-prone contexts multiply the triggering events).

**Assessability & Confidence.** Medium confidence from design files (auto-save absence is structural; actual loss behavior needs simulation) — promotion path: deliberate failure-mode testing. High confidence from live testing or code (retention logic inspectable). Static single screens: retention behavior is not assessable — declare; visible auto-save indicators and state cues remain flaggable. Context axis: C2 sharpens (what work is at stake); largely population-independent.

**Attribution.** Irreversible Action pairing (deliberate-destruction case; fix-based on reversibility). System Amnesia distinction (above). Unnecessary Step(s): explicit-save requirements are also an eliminable step — auto-save removes both.

**Report fragments.** Finding: "User content in [flow] is permanently lost if [failure mode] occurs before explicit saving; no auto-save or recovery exists." Why it matters: "Data loss is experienced as fundamental system failure — it destroys trust and forces users to repeat work already done."

**Remediation.** Continuous auto-save wherever feasible. Design for failure from the outset — timeouts, drops, and crashes are certainties, not edge cases. Conflict resolution that protects all contributors, not last-write-wins. Where deletion is the goal, complicate the confirmation (typed word) so habituated clicking can't destroy data. Hazard note: auto-save without version history creates its own loss mode — silently overwriting a prior state the user wanted kept; pair continuous save with recoverable history. Governing question: what happens to the user's work if the session ends right now?
