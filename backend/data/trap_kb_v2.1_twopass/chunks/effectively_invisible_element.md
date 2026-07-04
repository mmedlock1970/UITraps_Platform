<!-- GENERATED from trap_kb_v2.1.md — do not edit; regenerate on any master edit -->
### TRAP: EFFECTIVELY INVISIBLE ELEMENT *(pilot-grade)*
*Sub-tenet: Noticeable*

**Definition.** An element that is present and perceivable, but that users fail to notice — because it sits outside their attentional focus for the task, **or because it is presented in an unexpected way, regardless of its location**. Applies to visual, auditory, and tactile elements.

**Boundary.**
- IS: a perceivable element likely to go unregistered given where the user's attention falls during the task, or given what they are looking for. **Central placement and high salience do not disconfirm this Trap; expectation mismatch renders elements unnoticed independent of position (goal-driven filtering — the brain passes signals matching the user's search template and suppresses the rest).**
- IS NOT **Invisible Element**: there, no perceivable element exists at all. Tie-breaker: an element exists but is likely missed → here; no element exists → there.
- IS NOT **Distraction**: that Trap is attention wrongly captured; this one is attention never captured (mirror images).
- IS NOT **Wandering Element**: if the element would be noticed at a stable location and the noticing failure stems from its moving between screens or states, Wandering Element is the root cause (fix-based rule) — flag it there and reference the delayed noticing in the explanation.
- IS NOT **Inconsistent Appearance**: if the noticing/recognition failure stems from the same element being restyled across contexts, attribute there.
- IS NOT mere small size or subtle styling in the abstract: the test is misalignment with task-driven attention or expectation, not aesthetics.

**Detection procedure (pass one — flag, do not filter).** *Unit: per-screen, plus cross-screen steps for multi-screen artifacts.*
1. From the stated or assumed user goal, identify the elements on each screen in scope critical to completing it.
2. For each critical element, record: (a) location relative to the likely attentional focus for this task (focus = where the task's primary content or interaction lives, not screen center); (b) whether it differs from surroundings on any pre-attentive feature (color, size, orientation, motion); (c) whether its interaction style matches the flow's dominant interaction pattern (computed per G7); (d) the number of elements competing for attention in its vicinity; (e) **whether the element's appearance matches the visual category users would be searching for, given the goal it serves and their prior experience (C1) — does the thing that does X look like the kind of thing this population expects X to look like?**
3. Flag as candidate any critical element that: is peripheral to the task focus AND lacks pre-attentive distinction; OR deviates from the dominant interaction pattern; OR sits in a high-competition zone; **OR mismatches the user's likely search template for its function — flag regardless of location or visual prominence.**
4. Name the specific condition(s) per flag (G6).
5. Cross-screen (multi-screen artifacts only): flag state or mode indicators that must be noticed on a different screen from where the state was set; flag content that changes between screens in ways the user would not expect (unexpected changes are unlooked-for, hence filtered). Location changes route to Wandering Element; appearance changes route to Inconsistent Appearance (see Boundary).

**Disconfirmation (pass two).** NOT present when: (a) the element is in a location users are habituated to attending from prior product experience (C1) — even if not geometrically central; (b) the element differs from surroundings on a pre-attentive feature causing automatic pop-out AND matches the expected category for its function; (c) the element is consistent with the dominant interaction pattern, so users naturally encounter it in normal task flow.

**Severity.** High when the element is critical-path and fully unnoticed (functionally identical to absence). Delayed noticing is still this Trap; its severity equals the consequence of the delay in the specific task context (a missed mute indicator mid-meeting: High; a slowly-found settings link: Low). Escalators: C3 (divided attention, noise, motion sharply raise miss likelihood); C4 (recurring tasks compound the cost).

**Assessability & Confidence.** Static screenshot: Confirmed ceiling only when the element is measurably far from the primary task area AND critical to task completion; otherwise Probable — promotion path: confirm attentional focus with user observation (usability testing is the gold standard; design review alone cannot reliably confirm or rule this out — curse of knowledge). Context axis: C2 (task goal) softens under its default; C1 gates disconfirmation (a) only — absent C1, candidates cannot be cleared on habituation grounds and stay flagged; C3 modifies likelihood globally (its default makes findings a lower bound).

**Attribution.**
- Variable Outcome: an effectively invisible mode indicator is evidence toward Variable Outcome, but outcome variation must be independently confirmed; when confirmed, this Trap is typically root cause (fixing the indicator's noticeability resolves the outcome surprise).
- Information Overload: if the noticing failure dissolves by removing surrounding excess, Information Overload is the root cause (fix-based rule) — the manuscript states reducing it is often the remedy.
- Distraction: if motion was added to remedy this Trap, independently confirm the motion now captures attention away from the current goal before also flagging Distraction.
- Gratuitous Redundancy: if the element was *duplicated* to remedy this Trap, evaluate the duplicates under Gratuitous Redundancy — duplication is not an endorsed remedy (see Remediation).
- Two-gate interaction with Uncomprehended Element: an unfamiliar goal-critical element can fail pre-attentively (filtered — this Trap) or post-attentively (noticed but undecodable — Uncomprehended Element). Same root property; when the fix converges (a familiar, recognizable element), report one issue using the manifests-as pattern (G3). Live user observation distinguishes the gates (a fixation that never lands vs. a puzzled hover) — needed only if the team wants to size the noticing problem independently.

**Report fragments.** Finding: "An element critical to [goal] is present but likely to go unnoticed: [element], because [named condition — peripheral to task focus / pattern deviation / attention competition / expectation mismatch]." Why it matters: "Users who miss this element cannot proceed — functionally identical to the element being absent."

**Remediation.**
- Place the element within or adjacent to the user's primary attentional focus during the task in which it matters, and render it in the visual category users expect for its function.
- Or make one instance globally perceivable: whole-screen state changes (tint shift, screen-edge pulse) or attention-following placement — techniques that reach the user wherever their focal spotlight sits.
- Exploit pre-attentive features (color, size, orientation, motion) for pop-out. Caution: motion applied to elements not relevant to the current goal becomes a Distraction Trap.
- **Do not remedy by duplicating the element.** The focal area of human vision is tiny and constantly moving; duplicating indicators to "cover" attention produces indicator proliferation and a Gratuitous Redundancy Trap. One element, made unmissable, beats many competing for notice.
