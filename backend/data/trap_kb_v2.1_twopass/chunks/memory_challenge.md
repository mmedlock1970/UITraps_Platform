<!-- GENERATED from trap_kb_v2.1.md — do not edit; regenerate on any master edit -->
### TRAP: MEMORY CHALLENGE *(draft-grade)*
*Sub-tenet: Comprehensible*

**Definition.** The user is required to remember information that is easy to forget: holding information across screens, recalling passwords/commands from long-term memory without a retrieval cue, executing multi-step processes by memory alone. Even carrying a small item from one screen to the next may be too much — short-term memory is tiny and volatile.

**Boundary.** IS: an unreasonable recall demand imposed by the design. IS NOT **System Amnesia**: that is the *system* failing to use information it was previously given; this is the *user* being made to remember. Both can co-occur (system has the data AND makes the user recall it) — then System Amnesia is root cause (fix-based: the system using its data removes the recall demand). IS NOT **Uncomprehended Element**: that is a knowledge gap (never learned); this is a recall gap (learned but unretrievable). With **Invisible Element**: a trained-but-forgotten invisible interaction is both — determine which is primary.

**Detection procedure (pass one — flag, do not filter).** *Unit: cross-screen by nature; per-screen for recall-without-cue fields.*
1. Walk each task flow; at every step, list what the user must hold in mind to proceed, retrieve from memory without a cue, or execute from memorized instructions.
2. Flag every context-boundary carry: information shown on one screen and needed on another (or another session/device) without being re-presented.
3. Flag recall-without-cue demands: fields requiring memorized identifiers, security answers without the question shown, command vocabularies with no visible reference (voice command lists are the canonical case).
4. Flag instruction sequences the user cannot keep visible while executing them.

**Disconfirmation (pass two).** NOT present when: (a) the information is genuinely easy to remember in context (own name; a daily-used PIN); (b) the task is recognition, not recall — information presented for selection; (c) the information stays available for reference during the task.

**Severity.** High when recall failure blocks the task with no recovery path; Medium when recovery is effortful. Escalators: C3 — interruption, time pressure, and divided attention are precisely when held information evaporates; C4 — infrequent tasks (rare logins) maximize forgetting; spatially-presented information is markedly more memorable than verbal (mall-map principle).

**Assessability & Confidence.** Confirmed when provided screens show both the source information AND the recall demand — the cross-boundary carry is visible without user testing. Recall-without-cue flows: Confirmed-grade structural detection from flows/design files; whether the specific information is genuinely easy to forget stays Probable without C1/C4 — promotion path: interaction-frequency data or observation. Context axis: C4 (frequency) softens; C3 (interruption/pressure) sharpens severity.

**Attribution.** System Amnesia (above, fix-based). Invisible Element overlap (above). Forced Syntax adjacency: an unguessable required order that must be memorized — distinguish unaccommodating (there) from unlearnable-without-memorization (here) **[JUDGMENT]**.

**Report fragments.** Finding: "[Task/step] requires users to recall [information] without a retrieval cue, in a context where it is likely to be forgotten." Why it matters: "When users cannot recall this, they cannot complete the task — and may not know how to recover."

**Remediation.** Design for recognition over recall: let users see and choose rather than remember and enter. Present information spatially; chunk it; keep instructions visible during execution; provide retrieval cues (show the security question). The governing question: am I asking the user to remember this, or giving them a way to recognize it?
