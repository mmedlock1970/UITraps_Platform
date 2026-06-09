# UI TENETS & TRAPS — MCP KNOWLEDGE ENGINE v2
## Source: Book Manuscript v3 (updated, with enhanced MCP content)
## Built exclusively from manuscript content. No v1 card deck content used.

---
## ARCHITECTURE NOTES FOR AI TOOL

**Priority order for all assessments:**
1. Minimize false alarms (highest priority)
2. Maximize correct rejections
3. Maximize hits on high-severity Traps
4. Minimize misses on high-severity Traps

**Severity rule (universal):** High severity when consequence is task failure or worse, regardless of likelihood.

**Confidence tiers (universal):**
- Tier 1: Detectable from interface artifact alone — report as confirmed finding
- Tier 2: Candidate requiring user context confirmation — report as flagged for review
- Tier 3: Requires hardware testing or external verification — report as risk noted only

**False alarm prevention protocol:** Apply disconfirmation criteria FIRST, before any positive detection logic. If any disconfirmation condition is met, do not flag the Trap — even if detection criteria are also met.

**Root cause discipline:** When confirming related Traps, require independent evidence for each. Never infer Trap B from confirmed Trap A without separate evidence.

---

# CHUNK: FRAMEWORK OVERVIEW

**chunk_id:** framework_overview_v2

## What is UI Tenets & Traps?

UI Tenets & Traps is a heuristic framework for evaluating user interfaces. It distills nearly 100 years of research on human perception, cognition, memory, and ergonomics into an accessible and actionable form. The system comprises 8 Tenets and 27 Traps.

**Tenets** describe general attributes of good interface design.
**Traps** describe common, detectable design problems that degrade this goodness.
**Core idea:** Reduce Traps, improve the experience.

## Framework Structure

| Tenet | User Benefit | Traps |
|---|---|---|
| Understandable | Makes clear what I can do | Invisible Element, Effectively Invisible Element, Distraction, Uncomprehended Element, Inviting Dead End, Poor Grouping, Forced Syntax, Memory Challenge, Feedback Failure |
| Comfortable | Physically effortless to use | Physical Challenge, Accidental Activation |
| Responsive | Never makes me wait | Slow or No Response, Captive Wait |
| Efficient | Minimizes how much I must do | Unnecessary Step(s), Information Overload, System Amnesia |
| Accurate | Factual and relevant | Incorrect Information, Bad Prediction |
| Protective | Gives me control over my actions and data | Irreversible Action, Unwanted Disclosure, Data Loss |
| Habituating | Becomes automatic to use over time | Gratuitous Redundancy, Variable Outcome, Wandering Element, Inconsistent Appearance, Ambiguous Home |
| Beautiful | Aesthetically pleasing | Poor Aesthetic |

## Role in AI-Driven Analysis

AI scales interface output, not quality. AI-generated interfaces reproduce common design failures as readily as common successes. This framework provides the quality filter the generation process cannot. Human cognitive capabilities and limitations — the foundation of this framework — have not changed regardless of how interfaces are generated.

## Context Sensitivity

Context can shape if and how Traps apply. Games may intentionally introduce Physical Challenge or Memory Challenge to create appropriate difficulty. Shopping interfaces may use redundant navigation productively. The bottom line: knowing when different Traps apply requires careful consideration of factors outside the interface.

---

# CHUNK: TENET — UNDERSTANDABLE

**chunk_id:** tenet_understandable_v2

## Definition
An interface is Understandable when users can see what it offers, grasp how to use it, and know whether their actions worked.

## Core Insight
"Intuitive" means previously learned. Recognition, familiarity, and prior learning determine whether an interface is Understandable. The design question is not "how do we make this intuitive?" but "what have our users already learned, and what familiar concepts can we build on?"

## Three Sub-Tenets and Nine Traps

**Noticeable** — Critical elements must reach the user's attention.
→ Traps: Invisible Element, Effectively Invisible Element, Distraction

**Comprehensible** — The meaning of noticed elements must be clear.
→ Traps: Uncomprehended Element, Inviting Dead End, Poor Grouping, Forced Syntax, Memory Challenge

**Confirmatory** — Actions must produce feedback sufficient to confirm success or guide recovery.
→ Trap: Feedback Failure

## Foundational Requirement
For no Tenet is "know thy user" more relevant. Understandable interfaces require intimate knowledge of users' prior experiences, contexts of encounter, and moment-to-moment goals.

---

# CHUNK: TENET — COMFORTABLE

**chunk_id:** tenet_comfortable_v2

## Definition
An interface is Comfortable when it is physically effortless to use — covering comfort of hold, read, reach, manipulate, hear, wear, and navigate.

## Two Traps
**Physical Challenge** and **Accidental Activation** are opposite failure modes. Physical Challenge makes intended actions too difficult; Accidental Activation makes unintended actions too easy. Design changes that reduce one frequently worsen the other. Both must be considered together.

## Scope Note
Ergonomics, accessibility, and human factors have extensive literatures covering this Tenet. The Trap sections key in on targeting accuracy and text legibility as broadly applicable topics.

---

# CHUNK: TENET — RESPONSIVE

**chunk_id:** tenet_responsive_v2

## Definition
An interface is Responsive when it keeps pace with the user, allowing them to maintain a sustained sense of control.

## Universality
Responsive may have the strongest claim to universality of all Tenets. In most contexts, no user prefers to wait. Exceptions exist (gaming, anticipation-building) but the default assumption that users want to accomplish goals without unnecessary delay holds across the overwhelming majority of contexts.

## Two Traps
**Slow or No Response** and **Captive Wait** both rob the user of control — but for different reasons requiring different remedies.

---

# CHUNK: TENET — EFFICIENT

**chunk_id:** tenet_efficient_v2

## Definition
An interface is Efficient when it minimizes the number of steps a user must take and the amount of information they must parse. It achieves this by streamlining task flows, reducing what is presented at any moment, leveraging prior work, and anticipating actions.

## Three Traps
**Unnecessary Step(s)**, **Information Overload**, and **System Amnesia** each capture a distinct way interfaces make users do more work than necessary.

## Note on Bad Prediction
Bad Prediction is covered under the Accurate Tenet in this manuscript, where the consequences of inaccurate prediction are framed as an accuracy failure.

---

# CHUNK: TENET — ACCURATE

**chunk_id:** tenet_accurate_v2

## Definition
An interface is Accurate when it is true in word and deed: the information it presents is correct, and the actions it takes on the user's behalf are welcomed.

## AI Context
Large language and other AI models generate responses that are statistically plausible rather than verified as true. This makes the Accuracy of information simultaneously more important and more challenging to uphold.

## Two Traps
**Incorrect Information** and **Bad Prediction** undermine accuracy. Incorrect Information addresses factually wrong content. Bad Prediction addresses proactive actions or suggestions that are unwelcome — the system acts on the user's behalf and guesses wrong.

---

# CHUNK: TENET — PROTECTIVE

**chunk_id:** tenet_protective_v2

## Definition
An interface is Protective when it allows users to explore freely, secure in the knowledge that they can reverse course if needed, that nothing will be shared without their knowledge or consent, and that their data will never be lost.

## Three Traps
**Irreversible Action**, **Unwanted Disclosure**, and **Data Loss** undermine protection. All three undermine the same thing: the user's ability to act freely with confidence.

## Growing Importance
The data dimension of this Tenet has grown considerably more important as devices follow users everywhere, recording and sharing in ways users never intended.

---

# CHUNK: TENET — HABITUATING

**chunk_id:** tenet_habituating_v2

## Definition
An interface is Habituating when, with practice, users stop thinking about how to use it and focus entirely on their goals.

## Core Mechanism
The Power Law of Practice: performance improves as a predictable function of repetition. When a product behaves predictably, users cannot help but habituate to it. When it behaves unpredictably, improvement is slow and interactions remain effortful.

## Three Sub-Tenets and Five Traps

**Non-Redundant** — One Trap: Gratuitous Redundancy.
**Consistent with Expectations** — Three Traps: Variable Outcome, Wandering Element, Inconsistent Appearance.
**Oriented** — One Trap: Ambiguous Home.

## Key Principle: Know Thy Code
These Traps are less dependent on user knowledge and more amenable to direct inspection. Gratuitous Redundancy shows up as multiple links pointing to the same destination. Variable Outcome shows up as state-handlers routing the same user action to different outcomes.

---

# CHUNK: TENET — BEAUTIFUL

**chunk_id:** tenet_beautiful_v2

## Definition
An interface is Beautiful when users find its design appropriate and attractive.

## Two Dimensions
**Attractiveness** — the design is visually pleasing.
**Appropriateness** — the design is matched to its context, audience, and moment. Appropriateness is time-sensitive: what feels current today can feel dated in three years.

## Key Principles
- A product cannot be Beautiful if it fails on other Tenets. Functional excellence is the necessary foundation.
- You cannot reliably test for beauty before shipping. Pre-launch feedback often reflects resistance to the unfamiliar rather than a reliable signal about lasting response.
- Evaluating the product against the other eight Tenets is a powerful filter against aesthetic failure.

## One Trap
**Poor Aesthetic** undermines Beautiful.
---

# TRAP CHUNKS — UNDERSTANDABLE TENET

---

# CHUNK: INVISIBLE ELEMENT

**chunk_id:** trap_invisible_element_v2
**tenet:** Understandable | **sub-tenet:** Noticeable
**severity_combination_rule:** High when consequence is task failure or worse, regardless of likelihood.

## Definition (verbatim)
No label, icon, or other interface element is provided to let the user know how to achieve a goal, and the user lacks the prior learning needed to overcome its absence.

Applies equally to absent tactile or auditory cues. Common manifestations: hidden swipe actions, press-and-hold actions, hover-only labels, mode-dependent actions with no visible mode indicator.

## DISCONFIRMATION — Apply First
NOT present when:
(a) Users already have sufficient prior learning from products they regularly use — the interaction must exist on multiple established platforms OR it must be demonstrated that the targeted user population has learned it. A single platform example does not meet the threshold.
(b) An alternative visible means of completing the same action is provided — even if an invisible shortcut also exists.
(c) Effective instruction meeting all six conditions has been demonstrably delivered: (1) presented when user is ready and motivated, (2) required action is physically easy, (3) feedback is immediate and clear, (4) total invisible interactions kept very low, (5) each action clearly distinguishable from others, (6) training reintroduced if retention lapses.

## Severity
**Part A — Consequence:** Task failure is the standard outcome. In safety-critical contexts (emergency exits, vehicle controls), consequence rises to significant harm.
**Part B — Likelihood:** High when: invisible interaction is the sole path to a goal; user population has not been exposed to this interaction on similar products; no instruction provided. Decreases when user population is highly tech-savvy and interaction is common on major platforms.
**Combination rule:** High severity when consequence is task failure or worse, regardless of likelihood.

## Confidence Tiers
- **Tier 1:** Sole-path invisible interactions with no visible alternative — absence detectable in interface artifact combined with task analysis.
- **Tier 2:** Most instances — requires knowledge of prior user learning and available system interactions.

## Root Cause Confirmation (U4)
**Variable Outcome** is listed as often caused by Invisible Element. To confirm independently: verify the same action produces different results at different times due to a state change with no visible indication. Do not infer Variable Outcome from the missing indicator alone. Missing indicator confirms Invisible Element; unexpected outcomes must be separately observed.

## Examples → Rules
- **[Example 1.1] Humane Pin (2024):** Video capture required two-finger double tap and hold; no visible indicator existed; voice and palm display were unavailable in sun/noise. → *Rule: When primary input modes are context-dependent and fallbacks exist, every fallback must be visibly communicated or the fallback is an Invisible Element for the context in which it is the only option.*
- **[Example 1.2] Windows 8 Start Menu:** Removed visible Start button; cursor-to-corner trigger was invisible to users. → *Rule: Removing a visible element that users rely on to reach a core function creates Invisible Element even for experienced users — their prior learning pointed to the element, not the underlying interaction.*
- **[Example 1.3] Hulu mobile scroll:** No scroll indicator; users missed content below fold. → *Rule: Scroll affordances cannot be assumed. When content extends beyond view, a visible continuation cue is necessary unless users have strong established prior learning for scrolling in that specific context.*
- **[Example 1.4] BMW M-car DCT:** No visible Park control; foot-on-brake shutdown was invisible. → *Rule: In safety-critical interactions, the absence of a visible control is unacceptable regardless of the elegance of the invisible alternative.*
- **[Example 1.5] Tesla door release:** Unlabeled emergency door releases caused people to be trapped after accidents. → *Rule: Emergency and fallback interactions — needed precisely when users are most stressed — must be the most visibly communicated interactions, not the least.*

## Rules (consolidated)
- [definition] Both conditions must be true for the Trap to be present: no cue exists AND user lacks prior learning. Prior learning can compensate for absence, but only when it reliably exists in the user population.
- [examples] Removing a visible element that triggers a core function creates this Trap even for experienced users.
- [examples] Safety-critical interactions require visible communication regardless of design elegance.
- [why it occurs] Curse of knowledge: team members internalize invisible interactions and overestimate discoverability. Discoverability assessments made by the design team are unreliable.
- [how to avoid] Two-question test before any invisible interaction: (1) Are users demonstrably familiar with this from other products? (2) Is an alternative visible means provided? If both no: make visible or provide effective instruction.
- [AI detectability] Sole-path invisible interactions with no visible alternative are Tier 1. Others are Tier 2 — requires knowledge of user population prior learning and full inventory of system's hidden interactions.

## Related Traps
- **Memory Challenge** (often co-occurs): If a user was trained on the invisible interaction and later cannot recall it, Memory Challenge is also present. Confirm independently that recall, not comprehension, is the failure.
- **Variable Outcome** (often caused by): If no visible mode indicator exists and outcomes vary, confirm separately that outcomes actually differ at different times.

## Report Language (U6)
**Finding:** No visible cue is provided to signal how to achieve [goal], and users cannot reasonably be expected to discover it.
**Why it matters:** Users who do not discover this interaction cannot complete the goal.
**Confidence:** [Tier 1: Confirmed / Tier 2: Flagged — confirm whether users have relevant prior learning]

## Remediation (U7)
Make the action visible — almost always the easier and more reliable path. If retained invisible, deliver effective instruction meeting all six conditions when the user is ready and motivated.

## AI Detection Rules
**Tier 2 — Output to `potential_issues`, confidence "medium":** When a core task identified in the user context has no visible means of completion anywhere in the artifact AND no alternative visible path exists. Flag: "No visible cue signals how to achieve [goal]. If users lack prior learning for an alternative interaction, this is a candidate Invisible Element."
**`testable: false`:** All other instances — evaluating whether users have relevant prior learning requires user population knowledge not available from the artifact alone.

---

# CHUNK: EFFECTIVELY INVISIBLE ELEMENT

**chunk_id:** trap_effectively_invisible_element_v2
**tenet:** Understandable | **sub-tenet:** Noticeable
**severity_combination_rule:** High when consequence is task failure or worse, regardless of likelihood.

## Definition (verbatim)
A label, icon, or other interface element goes unnoticed because it is unexpected or misaligned with the user's focus of attention.

The element physically exists but is functionally invisible. Applies equally to tactile and auditory cues that go unregistered.

## DISCONFIRMATION — Apply First
NOT present when:
(a) The element is in a location users are already habituated to attending to from prior experience — even if not geometrically central.
(b) The element differs from surroundings on a pre-attentive feature (color, orientation, motion, size) causing automatic pop-out.
(c) The element is consistent with the dominant interaction pattern of the interface, so users naturally encounter it.

## Severity
**Part A — Consequence:** Task failure when the element is in the critical path. Slower noticing (vs. complete non-noticing) reduces severity to friction and delay rather than task failure.
**Part B — Likelihood:** High when: element placed outside user's primary attentional zone for their current goal; interface has established a dominant pattern the element deviates from. Low when: element uses strong pre-attentive features or is adjacent to user's primary focus.
**Combination rule:** High severity when consequence is task failure or worse, regardless of likelihood.

**Note on delayed noticing:** Severity of delayed noticing (vs. complete non-noticing) is determined by the consequence of the delay in the specific task context. Delayed noticing that causes task failure is high severity; delay that causes minor friction is not.

## Confidence Tiers
- **Tier 2:** Most instances — requires knowledge of users' attentional focus during specific tasks.
- **Tier 1 (approaching):** When the element is measurably far from the primary task area AND critical to task completion.

## Root Cause Confirmation (U4)
- **Variable Outcome** (often caused by this): Confirm independently that the same action produces different results. The effectively invisible mode indicator is evidence of this Trap, but outcome variation must be separately confirmed.
- **Distraction** (often co-occurs): If motion was added to remedy this Trap, confirm independently that it draws attention away from the user's current goal.

## Examples → Rules
- **[Example 2.1] Zoom mute indicator:** Placed away from where participants attend (other faces); went unnoticed, causing "You're on mute!" experiences. → *Rule: Critical status indicators must be placed within or adjacent to the user's primary attentional focus during the task in which the status matters — not where geometrically convenient.*
- **[Example 2.2] Xbox 360 Y-button search:** Indicated in corner; users expected search to be on a tile since tiles provided primary navigation. → *Rule: When an interface establishes a dominant interaction pattern, elements requiring a different interaction type are at elevated risk of going unnoticed even when physically visible.*
- **[Example 2.3] Academy Awards envelope:** Presenters saw movie title (expected) and missed award category (unexpected). → *Rule: When users approach with strong prior expectations, information that contradicts those expectations is at high risk of going unregistered even when directly visible.*
- **[Example 2.4] Meta Quest setup code:** Appeared on far side of screen; many users missed it; moving to center resolved the issue. → *Rule: In sequential task flows, users' attention anchors to the location of primary instructional content. Supporting information outside that anchor zone is at high risk of going unnoticed.*

## Rules (consolidated)
- [definition] Placing an element where a user can physically see it does not guarantee they will notice it. Attention, not visibility, determines what registers.
- [examples] Elements must be placed within or adjacent to the user's primary attentional focus during the task in which they matter.
- [examples] Dominant interaction patterns create attentional expectations. Elements deviating from the dominant pattern are at elevated risk.
- [why it occurs] Familiarity destroys the ability to see a design as a first-time user does. Once familiar, designers cannot unsee the gorilla.
- [how to avoid] For each critical element: where will the user's attention be during the task in which this element matters? Place it there. Exploit pre-attentive features for pop-out. Use motion only as last resort — motion applied indiscriminately becomes Distraction.
- [AI detectability] Tier 2: requires knowledge of users' attentional focus, prior learning (shapes expectations), and moment-to-moment goals. Cannot confirm from design file alone.

## Related Traps
- **Variable Outcome** (often caused by this): When a mode indicator is located away from where users attend, it becomes effectively invisible. Fix placement to resolve both simultaneously.
- **Distraction** (tension): Motion used to remedy Effectively Invisible Element becomes Distraction when applied to elements irrelevant to the user's current goal.

## Report Language (U6)
**Finding:** A cue critical to [goal] is present in the interface but is likely to go unnoticed because its location or appearance is misaligned with where users attend during this task.
**Why it matters:** Users who miss this element cannot proceed — the outcome is functionally identical to the element being absent.
**Confidence:** [Tier 2: Flagged — confirm attentional focus for this task with user observation]

## Remediation (U7)
Place the element within or adjacent to the user's primary attentional focus during the task — not where convenient. Exploit pre-attentive features (color, size, motion) for pop-out. Caution: motion used to increase visibility becomes Distraction when applied to elements not relevant to the user's current goal.

## AI Detection Rules
**Human Review — Output to `flagged_for_human_review`:** When an element critical to task completion is present but measurably peripheral, low-contrast, or misaligned with the dominant interaction pattern of the interface. Question for reviewer: "Would your users notice [element] in its current location and styling during this task?"
**`testable: false`:** For general cases where attentional focus during the specific task cannot be assessed from the artifact.

---

# CHUNK: DISTRACTION

**chunk_id:** trap_distraction_v2
**tenet:** Understandable | **sub-tenet:** Noticeable
**severity_combination_rule:** High when consequence is task failure or worse, regardless of likelihood.

## Definition (verbatim)
Something in the interface draws the user's attention away from their current goal.

Examples: pop-up notifications, auto-playing audio or video, animated ads, elements that suddenly appear or change state without user initiation.

## DISCONFIRMATION — Apply First
NOT present when:
(a) The attention-drawing element is directly relevant to the user's current goal — a status update during an active process is not Distraction.
(b) The element appears in a passive or exploratory context where no focused goal exists to be disrupted.
(c) The user initiated the element — only unsolicited attention capture qualifies.
(d) The user would agree the disruption was justified — e.g., an important notification from a loved one during an emergency.

**Important:** This Trap also does not require sudden change. The mere presence of certain information types (notification badges, unread counts, alert indicators) can deplete attentional resources even without motion.

## Severity
**Part A — Consequence:** Ranges from minor friction (briefly diverted attention) to task failure (critical information missed or obscured) to safety risk (driving navigation obscured). Boeing 737 MAX: competing warnings made life-saving response impossible — extreme end of spectrum.
**Part B — Likelihood:** High when: element appears without user initiation during focused task execution; element involves motion, sound, or sudden appearance; element appears in visual periphery during high-attention task. Low when: user is in exploratory or passive browsing mode.
**Combination rule:** High severity when consequence is task failure or worse, regardless of likelihood.

**Note on bad-faith design:** Intentional exploitation of this Trap for reasons that run counter to user interests should be flagged as a potential dark pattern in addition to this Trap.

**Note on voice as distraction:** Voice interfaces draw on the same cognitive resources as internal speech. Issuing a voice command while engaged in verbal thought creates Distraction even without visual interruption. Physical interactions draw on different cognitive resources and do not carry this cost.

## Confidence Tiers
- **Tier 1:** Elements that auto-play audio or video during documented task flows — detectable and almost universally distracting during focused tasks.
- **Tier 2:** Motion, sudden appearance, and other attention-capturing elements — detectable in interface artifacts, but whether they constitute Distraction depends on task context.

## Root Cause Confirmation (U4)
- **Information Overload** (often co-occurs): Confirm independently that the volume of information exceeds what is needed for the user's current goal. Do not infer overload from the presence of a distracting element alone.
- **Effectively Invisible Element** (tension): If motion was added to remedy an EIE, confirm independently that the original element had an attention problem before attributing the motion to this relationship.

## Examples → Rules
- **[Example 3.1] iPhone GPS + news notifications:** News notifications overlaid driving directions. → *Rule: Notification timing must account for the user's state within and outside the product. An interruption tolerable during passive browsing is a safety issue during active navigation.*
- **[Example 3.2] Boeing 737 MAX warnings (2019):** Six+ concurrent warnings including overlapping voice alerts made prioritization impossible. → *Rule: Concurrent alerts do not compound attention — they compete for it. Multiple simultaneous warnings provide less actionable information than a single prioritized alert.*
- **[Example 3.3] Netflix autoplay:** Unexpected sound and motion during browsing disrupted information-scanning. → *Rule: Autoplay audio and video are among the highest-impact Distraction mechanisms — they combine motion, sound, and unexpectedness simultaneously.*
- **[Example 3.4] Oculus VR casting indicator:** Red dot in center of immersive interface during gameplay generated sustained frustration. → *Rule: Status indicators that persist in the center of an immersive or high-focus interface are categorically distracting regardless of their size.*

## Rules (consolidated)
- [definition] Peripheral vision is optimized for motion detection. Humans evolved to automatically redirect attention toward movement — this response is involuntary.
- [definition] Distraction does not require sudden change; notification badges and unread counts deplete attention even when static.
- [examples] Context of use determines whether the same element constitutes a Trap. An element tolerable during browsing can be a safety issue during navigation.
- [why it occurs] Designers evaluate elements in isolation rather than in the context of the broader experience and what users will be doing when the element appears.
- [governing question] Not "will this be noticed?" but "what will the user be doing when this appears, and what will noticing it cost them?"
- [AI detectability] Tier 1 for auto-play audio/video. Tier 2 for other elements — requires knowledge of users' goals within and outside the product.

## Related Traps
- **Information Overload** (often co-occurs): Line between them is blurry; solving for either often resolves both — remove what isn't relevant to user's goal.
- **Effectively Invisible Element** (tension): Motion used as EIE remedy becomes Distraction when applied to elements irrelevant to the user's current goal.

## Report Language (U6)
**Finding:** [Element] draws user attention away from [primary goal] without being initiated by the user or directly relevant to their current task, and without being something the user would judge worthy of shifting attention to.
**Why it matters:** Involuntary attention cannot be suppressed — when this element appears, users will unavoidably notice it regardless of their efforts to focus.
**Confidence:** [Tier 1: Confirmed for auto-play audio/video / Tier 2: Flagged — confirm task context]

## Remediation (U7)
The governing question is not "will this be noticed?" but "what will the user be doing when this appears, and what will noticing it cost them?" Remove or defer any element that appears without user initiation during focused task execution unless confidence is high that the disruption will be welcomed. For notification systems, evaluate whether the interruption serves the user or the product's engagement metrics — these are not always the same. Caution: eliminating a distracting element that was compensating for an Effectively Invisible Element may require adding a non-distracting visible solution.

## AI Detection Rules
**Tier 1 — Confirmed finding:** Auto-playing audio or video elements. Flag directly as a confirmed finding.
**Human Review — Output to `flagged_for_human_review`:** Motion, notification badges, unread counts, or unsolicited elements during documented task flows. Question: "Does [element] pull user attention away from [primary task]?"
**`testable: false`:** General attention-capture requiring knowledge of user goals outside the product.
**Severity calibration (apply every time):**
- **Minor**: Static or slow-updating element (counter, badge, timer) in entertainment, browsing, or casual context — brief involuntary glance, negligible task cost.
- **Moderate**: Motion, animation, or audio in focused transactional context (checkout, form completion, search).
- **High/Critical**: Any distracting element during safety-critical, time-sensitive, or irreversible tasks; or any element that physically obscures critical interface content.
⚠️ Do NOT default to Moderate for all Distraction findings — calibrate to what the distraction actually costs the user given what they are doing.

---

# CHUNK: UNCOMPREHENDED ELEMENT

**chunk_id:** trap_uncomprehended_element_v2
**tenet:** Understandable | **sub-tenet:** Comprehensible
**severity_combination_rule:** High when consequence is task failure or worse, regardless of likelihood.

## Definition (verbatim)
A label, icon, or other interface element is noticed, but its meaning or required method of interaction is unclear.

## DISCONFIRMATION — Apply First
NOT present when:
(a) The element uses a widely adopted convention users are demonstrably familiar with — magnifying glass for search, house for home, gear for settings.
(b) A text label is provided that compensates for an unclear icon — noting that a label reduces but may not fully eliminate this Trap when the icon actively contradicts the label.
(c) Effective instruction is provided at the moment of first encounter.

## Severity
**Part A — Consequence:** Task failure when the element is in the critical path to the user's primary goal. Friction and delay when alternative paths exist.
**Part B — Likelihood:** High when: element represents a core function using a brand-specific or non-standard symbol; no text label is provided; user population is general rather than specialist. Low when: user population has deep prior exposure to this specific product's conventions.
**Combination rule:** High severity when consequence is task failure or worse, regardless of likelihood.

## Confidence Tiers
- **Tier 1:** Brand symbols used as functional icons with no conventional signifier equivalent and no text label — risk high enough to flag without user confirmation.
- **Tier 2:** Most icons, labels, or other signifiers — requires knowledge of user familiarity with specific conventions.

## Root Cause Confirmation (U4)
- **Inviting Dead End** (often co-occurs): Confirm independently that a specific incorrect element is likely to be chosen. Not merely that the correct element is unclear — a compelling wrong element can attract users even when the correct element is somewhat clear.
- **Memory Challenge** (sometimes co-occurs): If users once knew the element's meaning but cannot recall it, confirm independently that this is a recall failure rather than a comprehension failure — the intervention differs.

## Examples → Rules
- **[Example 4.1] Waze search icon:** Original Waze-logo silhouette was unrecognized as Search; magnifying glass replacement was instantly recognized. → *Rule: When a core function uses a brand-specific symbol instead of a universally recognized signifier, comprehension depends on brand familiarity. For core navigation functions, universal conventions take precedence over brand expression.*
- **[Example 4.2] Amazon Fire TV mic → Alexa symbol:** Replacing microphone with Alexa symbol for brand reinforcement caused confusion; reverted to mic icon. → *Rule: Replacing an established, comprehensible signifier with a brand symbol constitutes this Trap even when the brand is well-known.*
- **[Example 4.3] Oculus "O" Home icon:** Users ignored the O-logo icon even when labeled "Home" because the icon's visual form undermined the label. → *Rule: A label partially compensates for an unclear icon. But when an icon actively contradicts its label, the label alone does not resolve the Trap.*
- **[Example 4.4] Hulu icon-only controls (2019):** Icon-only navigation replaced with text labels, improving comprehension. → *Rule: Icon-only navigation scales poorly with interface complexity. As function count grows, the demand to learn a proprietary icon vocabulary exceeds users' willingness to invest.*
- **[Example 4.5] Spotify heart → check:** Replacing heart (liked) with check (ambiguous: liked or added to playlist) made meaning genuinely unclear even for experienced users. → *Rule: Comprehension is not static — it can be removed by design changes. A symbol change introducing meaning overlap creates this Trap even for users who understood the original.*

## Rules (consolidated)
- [definition] Two conditions required: element is noticed AND meaning or required interaction method is unclear. If not noticed, it is Effectively Invisible Element.
- [examples] Universal conventions for core functions take precedence over brand expression.
- [examples] Icon-only navigation for complex interfaces imposes a proprietary vocabulary learning burden users typically reject.
- [why it occurs] Teams skew toward troubleshooters who will figure things out; they underestimate how much general users dislike friction. The question to ask is not "will users figure it out?" but "have we made sure they already know?"
- [how to avoid] When in doubt, provide labels. Test by showing the element to a small number of potential users and asking what it means. This is a trivially simple test requiring almost no resources.
- [AI detectability] Tier 1 for brand symbols as functional icons without labels. Tier 2 for most signifiers — requires knowledge of user familiarity with conventions.

## Related Traps
- **Inviting Dead End** (often co-occurs): Uncomprehended Element leaves the user uncertain; Inviting Dead End leads them confidently in the wrong direction. The combination is particularly damaging.
- **Memory Challenge** (sometimes co-occurs): Distinguish comprehension failure from recall failure — interventions differ.

## Report Language (U6)
**Finding:** [Element] is unlikely to be correctly interpreted by users unfamiliar with [product/brand convention], and no standard signifier or text label is provided to clarify its meaning.
**Why it matters:** Users who cannot interpret this element cannot determine how to proceed toward their goal.
**Confidence:** [Tier 1: Confirmed for brand symbols as functional icons without labels / Tier 2: Flagged — confirm with user familiarity assessment]

## Remediation (U7)
Use universally recognized signifiers for core functions. When in doubt, provide a text label — a labeled unclear icon is always better than an unlabeled one. For genuinely novel concepts with no existing convention, plan instruction delivered when the user is ready to receive it. Replacing a well-learned brand symbol with a conventional signifier is almost always the right call for functional elements, even at the cost of brand expression.

## AI Detection Rules
**Tier 1 — Confirmed finding, moderate severity:** A brand-specific or non-standard symbol used as a functional icon for a core function with no text label and no conventional signifier equivalent. Flag directly.
**Human Review — All other cases:** Output to `flagged_for_human_review`. Question: "Would your target users understand what [term/icon] means?"
**What IS this trap:** Unfamiliar icons, unfamiliar terminology, ambiguous labels, icons without text labels users might not recognize, any element where the information present is insufficient for the user to understand it or act confidently.
**What is NOT this trap (critical disambiguation):**
- Filter/dropdown state not visible → **FEEDBACK FAILURE** instead (the issue is visibility of state, not meaning of label)
- Selected values not displayed → **FEEDBACK FAILURE** or **INVISIBLE ELEMENT**
- Standard UI patterns (chevrons, hamburger menus, magnifying glass for search) → universally understood
- Clear labels like "Price", "Rating", "Sort", "Filter" → not this trap
- Any issue about VISIBILITY of current state rather than MEANING of labels → not this trap
**vs. INFORMATION OVERLOAD (critical disambiguation):** Mutually exclusive. Information Overload = volume makes it hard to find or act. Uncomprehended Element = content present is insufficient to understand the element or act confidently. If your problem description is the reverse of the trap's definition, you have chosen the wrong trap.

---

# CHUNK: INVITING DEAD END

**chunk_id:** trap_inviting_dead_end_v2
**tenet:** Understandable | **sub-tenet:** Comprehensible
**severity_combination_rule:** High when consequence is task failure or worse, regardless of likelihood.

## Definition (verbatim)
A label, icon, or other interface element is incorrectly judged to be a means of achieving a goal; it looks right but is wrong.

Where Uncomprehended Element leaves the user uncertain, Inviting Dead End leads them confidently in the wrong direction.

## DISCONFIRMATION — Apply First
NOT present when:
(a) No other element in the interface could plausibly be mistaken for the correct path to the user's current goal.
(b) The correct element is visually distinctive enough from all other elements that confusion is implausible given the user's task context.

**Critical detection signal:** Interfaces that display error messages amounting to "the action you just took is not allowed" confirm this Trap without user testing. The message is evidence that the wrong path looked correct. The fix is to remove the wrong path, not improve the error message.

## Severity
**Part A — Consequence:** Task failure when element is in the critical path. Friction and delay when alternative paths exist. Significantly worse when combined with Irreversible Action.
**Part B — Likelihood:** High when: element represents a core function using non-standard or brand-specific symbol; no text label; user population is general. Low when: user population has deep prior exposure to this product's conventions.
**Combination rule:** High severity when consequence is task failure or worse, regardless of likelihood.

## Confidence Tiers
- **Tier 1:** Interfaces displaying error messages documenting the wrong path (code or UI showing "not allowed" responses to specific actions) — confirmable without user testing.
- **Tier 2:** Visual similarity detectable but whether users will judge a specific element as a plausible wrong path requires user knowledge.

## Root Cause Confirmation (U4)
- **Uncomprehended Element** (often co-occurs): Confirm independently that the correct element's meaning is genuinely unclear — not merely that users are choosing the wrong one. A compelling wrong element can attract users even when the correct element is clear.
- **Poor Grouping** (sometimes causes): Confirm independently that a spatial ambiguity is creating the false association rather than visual similarity alone.

## Examples → Rules
- **[Example 5.1] Apple Music / iTunes icons:** Similar icon designs drew users into iTunes instead of iPod/Music. → *Rule: When two elements are visually similar and users are attempting one, the other becomes this Trap. Icon differentiation must account for the full set of plausible visual comparisons, not just the icon in isolation.*
- **[Example 5.2] Elevator current floor button:** Interface allows selecting the floor you're already on; error message results. → *Rule: Any error message amounting to "the action you just took is not allowed" confirms this Trap. Fix: remove the wrong path, not the error message.*
- **[Example 5.3] Westin Hotel bathroom:** Ambiguous enough that labels had to be added to distinguish urinals from sinks. → *Rule: When a design requires explanatory labels to prevent wrong action, the label is evidence of the Trap — not a solution. Redesign the affordance.*
- **[Example 5.4] Google app icon redesign:** Same four colors across app icons caused users to consistently select wrong apps. → *Rule: Brand consistency achieved at the cost of functional differentiability creates this Trap across an entire suite. When icons must be distinguished quickly, visual differentiation takes precedence over brand unity.*
- **[Example 5.5] Amazon Prime Video paywalled content:** Content appeared available but required extra fee, revealed only after selection. → *Rule: In browsing interfaces, content requiring additional action or payment must be visually distinguished before selection — not disclosed after. Post-selection disclosure is this Trap.*
- **[Example 5.6] Oculus home icon → Library:** House icon led to software Library, not Home. → *Rule: Using a universally recognized symbol (house = home) for a non-standard destination creates a particularly strong instance because users rely on the symbol's conventional meaning and will not read the label.*

## Rules (consolidated)
- [definition] The user is not confused — they are confident but wrong. This is what makes the Trap damaging: it does not create hesitation, it creates misdirection.
- [examples] Error messages documenting wrong paths are Tier 1 confirmation of this Trap.
- [examples] Visual similarity between elements plus user task creates wrong-path pull — evaluate elements in task context, not isolation.
- [why it occurs] Design attention concentrates on the intended path. Designers who know the system know which elements to ignore — misleading elements on wrong paths rarely get scrutinized.
- [how to avoid] Walk every plausible path, not just the intended one. At each decision point: is there anything a user unfamiliar with the system might reasonably try instead?
- [AI detectability] Tier 1 for error messages documenting wrong paths. Tier 2 for visual similarity — requires user knowledge.

## Related Traps
- **Uncomprehended Element** (often co-occurs): The combination is maximally damaging — no correct path clear AND an incorrect path looks compelling.
- **Incorrect Information** (sometimes causes): Incorrect information that suggests a wrong path is an Inviting Dead End, but Incorrect Information is the root cause. If a signifier is merely confused as being correct but is not factually wrong, it's only this Trap.
- **Poor Grouping** (sometimes causes): Ambiguous spatial relationships can make the wrong control appear associated with the right action.

## Report Language (U6)
**Finding:** [Element] is likely to be judged as the correct path to [goal] by users unfamiliar with the system, but leads to [wrong destination/outcome] instead.
**Why it matters:** Users who follow this path will expend effort, lose confidence, and may not find their way to the correct path without assistance.
**Confidence:** [Tier 1: Confirmed when error messages document the wrong path / Tier 2: Flagged — confirm with user task observation]

## Remediation (U7)
Systematically walk every plausible path through the interface, not just the intended one. At each decision point, ask whether any element could reasonably be mistaken for the correct next step. Where a wrong path exists, either increase visual differentiation between correct and incorrect elements, or remove the incorrect path entirely. An error message that says "don't do what you just did" is evidence of this Trap — the fix is to remove the wrong path, not improve the error message. There are no cases where such a message is acceptable and the element that triggered it should not be redesigned.

## AI Detection Rules
**Tier 1 — Confirmed finding, moderate severity:** An error message in the artifact amounting to "you should not have done what you just did" or "this action is not allowed" — this confirms users followed a plausible wrong path. Also: when you have verified the destination (multi-page analysis) and it objectively mismatches the CTA text; or when CTA text makes a specific promise that is objectively not kept (e.g., "Free Download" leads to payment).
**Human Review — All other visual similarity cases:** Output to `flagged_for_human_review`. Question: "Do your users expect [element] to lead to [destination type]?"

---

# CHUNK: POOR GROUPING

**chunk_id:** trap_poor_grouping_v2
**tenet:** Understandable | **sub-tenet:** Comprehensible
**severity_combination_rule:** High when consequence is task failure or worse, regardless of likelihood.

## Definition (verbatim)
An important relationship between two or more interface elements is unclear.

Focused on relationships between elements rather than individual elements. Applies to both visual/spatial relationships between interface elements AND to conceptual relationships within information architectures, including menu hierarchies, navigation structures, and content organization.

## DISCONFIRMATION — Apply First
NOT present when:
(a) Elements that appear spatially close (or bounded/similar in design) are actually functionally related — correct grouping is not a problem.
(b) The relationship is not critical to the user's goal — Poor Grouping specifically applies to critical relationships.
(c) Spatial ambiguity is resolved by a stronger cue: explicit labels, connecting lines, or consistent visual treatment that overrides proximity.
(d) Conceptual elements (menu items) are grouped into obviously similar categories — when the conceptual grouping is clear, spatial proximity issues alone may not constitute this Trap.

## Severity
**Part A — Consequence:** Ranges from minor friction (user hesitates) to highly consequential (butterfly ballot — wrong choice made confidently at scale). Severity scales directly with the stakes of the action the grouping supports.
**Part B — Likelihood:** High when: a control is equidistant between two competing targets or further from a related than an unrelated element; high information density makes spatial or conceptual relationships hard to read; users are under time pressure. Low when: strong secondary cues (labels, color, lines) or conceptual connections disambiguate the relationship.
**Combination rule:** High severity when consequence is task failure or worse, regardless of likelihood.

## Confidence Tiers
- **Tier 1:** Butterfly-ballot-level violations where a control is measurably equidistant between two competing options and no secondary disambiguation cues exist; or instances where unrelated items are measurably closer than related items.
- **Tier 2:** Most instances — proximity measurements available in design files but whether ambiguity constitutes a Trap requires user knowledge.

## Root Cause Confirmation (U4)
- **Inviting Dead End** (often co-occurs): Confirm independently that grouping ambiguity causes a specific wrong control to be chosen — not merely that the relationship is unclear. Ambiguous grouping alone does not confirm that users will take the wrong action.
- **Information Overload** (sometimes contributes): Confirm independently that excess information is making spatial/conceptual relationships hard to read. Reduce information density and reassess before attributing to Poor Grouping.

## Examples → Rules
- **[Example 6.1] Butterfly Ballot (2000 election):** Layout created false spatial association between candidate names and wrong punch holes; 4,000+ wrong votes, 19,000+ double-punches. → *Rule: Spatial proximity is the dominant grouping cue. When a label and a control are equidistant between two options, users distribute associations according to expectations — not designer intent. In selection interfaces, the control must be unambiguously closer to its corresponding option than to any competing option.*
- **[Example 6.2] SXSW conference registration:** Buttons evenly spaced between track descriptions; unclear which button matched which block. → *Rule: In list interfaces where controls alternate with content, even spacing creates ambiguous grouping. Explicit separation (white space, dividers, indentation) is required to make control-to-content associations unambiguous.*
- **[Example 6.3] Amazon Prime Video nav bars:** Participants failed to recognize relationship between primary and secondary nav bars; subsequent redesign grouped all nav in close proximity. → *Rule: Navigation elements belonging to the same system should be grouped together. When primary and secondary navigation are separated by content, users may not perceive them as part of the same navigational structure.*
- **[Example 6.4] Elevator direction buttons:** Buttons and arrows in ambiguous spatial relationship — unclear which button maps to which direction. → *Rule: When controls and indicators share a visual field, their spatial grouping must be unambiguous. Equidistance between a control and two competing indicators creates grouping failure regardless of indicator clarity.*
- **[Example 6.5] Navigation IA menus:** Items grouped under wrong categories prevent users from finding them. → *Rule: Poor Grouping applies to conceptual organization within information architectures — menu hierarchies and navigation structures — not only to visual/spatial relationships.*

## Rules (consolidated)
- [definition] Users do not consciously analyze spatial relationships — they perceive them automatically through Gestalt mechanisms. Designing against these mechanisms produces misread relationships.
- [definition] This Trap applies to both visual/spatial relationships AND to conceptual organization in information architecture.
- [examples] Proximity is the most powerful grouping principle and the most commonly violated. A label equidistant between two controls will be perceived as ambiguously related to both.
- [examples] When 19,000+ people make the same error in the same direction, the cause is the design, not the users.
- [how to avoid] Proximity: elements belonging together should be measurably closer to each other than to any competing element. White space is one of the most effective grouping tools — separation between unrelated groups, proximity within related ones.
- [AI detectability] Tier 1 for measurable spatial violations (equidistance, closer-to-unrelated-than-related). Tier 2 for most instances — whether ambiguity constitutes a Trap requires user knowledge.

## Related Traps
- **Inviting Dead End** (often co-occurs): Ambiguous grouping can make wrong control appear associated with right action.
- **Uncomprehended Element** (often co-occurs): Poor Grouping can make individually comprehensible elements confusing in combination by obscuring their relationships.
- **Information Overload** (often co-occurs): Visual clutter is both a cause and symptom of Poor Grouping.

## Report Language (U6)
**Finding:** The spatial or conceptual relationship between [elements] is ambiguous — users are likely to misread which [control/label/menu option] corresponds to which [option/action/category].
**Why it matters:** Users who misread this relationship will take the wrong action with confidence, not uncertainty.
**Confidence:** [Tier 1: Confirmed for measurable spatial or conceptual violations / Tier 2: Flagged — confirm with user task observation]

## Remediation (U7)
Apply Gestalt principles deliberately — elements that belong together should be spatially or conceptually closer to each other than to any competing element. Use white space as an active grouping tool. Where proximity alone is insufficient, add explicit visual separators (lines, containers, color). Test with users unfamiliar with the system by asking them to complete tasks that depend on correct grouping recognition.

## AI Detection Rules
**Tier 1 — Confirmed finding:** Measurable spatial violations: a control is measurably equidistant between two competing options with no secondary disambiguation cues; OR related items are measurably closer to unrelated items than to each other.
**Tier 2 — Output to `potential_issues`, confidence "medium":** Most other cases — ambiguity is detectable but whether it constitutes a Trap requires user knowledge.
**Required evaluation framework — Gestalt Principles:** POOR GROUPING is ONLY present when a specific Gestalt perceptual principle is violated. Evaluate against these principles:
1. **PROXIMITY** (most common): Related elements must be spatially closer to each other than to unrelated elements.
2. **SIMILARITY**: Same-function elements share visual properties. Violation: same-function elements look different, OR different-function elements look identical.
3. **COMMON REGION**: Elements in the same visual boundary are perceived as related. Violation: unrelated elements share a container, or related elements split across containers.
4. **CONTINUITY**: Eye follows smooth aligned paths. Violation: misalignment breaks expected reading order.
5. **FIGURE-GROUND**: Foreground elements must be distinguishable from background. Use POOR GROUPING only when the issue is grouping confusion, not contrast alone.
6. **CLOSURE**: Incomplete shapes resolve into recognizable forms. Rarely applicable to most UI analysis.
7. **COMMON FATE**: Elements that move together are perceived as related. Requires video — cannot assess from static screenshots.
8. **SYMMETRY/ORDER**: Near-symmetry creating unintentional imbalance. Example: two columns of equal importance with very unequal item counts.
**What is NOT POOR GROUPING:** Mixed content serving the same navigational purpose; standard layouts following conventions; aesthetic preferences that don't violate the above. Multiple navigation options → may be GRATUITOUS REDUNDANCY instead.
**Output requirement when flagging:** Cite (1) which Gestalt principle is violated, (2) measurable/observable evidence, (3) expected vs. actual grouping. If you cannot cite a specific principle violation, it is NOT POOR GROUPING.

---

# CHUNK: FORCED SYNTAX

**chunk_id:** trap_forced_syntax_v2
**tenet:** Understandable | **sub-tenet:** Comprehensible
**severity_combination_rule:** High when consequence is task failure or worse, regardless of likelihood.

## Definition (verbatim)
A sequence of actions cannot be completed in the order or manner the user expects or prefers.

Examples: systems requiring object before action ("bedroom light > turn on") but not the reverse ("turn on > bedroom light"); systems requiring "Alexa, what's the time?" but not "What's the time, Alexa?"

## DISCONFIRMATION — Apply First
NOT present when:
(a) The sequence has a dominant natural order that virtually all users expect and prefer for this task type.
(b) The interface provides a flexible alternative for the most common alternative construction. Note: supporting every possible sequence is not required — only reasonably likely alternatives.

**Key distinction from Gratuitous Redundancy:** Forced Syntax and Gratuitous Redundancy are mutually exclusive for a given task flow. Forced Syntax provides only one grammatical construction; Gratuitous Redundancy provides duplicate paths via the same construction. Confirm which is present before flagging either.

## Severity
**Part A — Consequence:** Task failure if users assume the function is not supported or fail to find the supported sequence. Significant friction and extra steps when users must reorganize their approach before proceeding.
**Part B — Likelihood:** High when: interface imposes single fixed order for a task with multiple natural starting points; user population includes both novice and expert users who conceptualize tasks differently; interface is voice-driven (grammatical flexibility is highest in natural speech). Low when: task has a dominant natural sequence and user population is homogeneous.
**Combination rule:** High severity when consequence is task failure or worse, regardless of likelihood.

## Confidence Tiers
- **Tier 2:** Fixed sequences identifiable in design files and task flows, but whether the sequence is unnatural for real users requires user knowledge.

## Root Cause Confirmation (U4)
- **Unnecessary Steps** (sometimes caused by): If users must restart a flow because of Forced Syntax, confirm independently that extra steps are caused by the syntax constraint and not a separate flow design issue.
- **Gratuitous Redundancy** (distinction): Mutually exclusive per task flow — confirm which is present before flagging either.

## Examples → Rules
- **[Example 7.1] Alexa voice commands:** "Alexa, what time is it?" works; "What time is it, Alexa?" does not. → *Rule: Voice interfaces that require a fixed grammatical construction impose this Trap on any user whose natural formulation differs. Where possible, accept commands in multiple constructions.*
- **[Example 7.2] Parking garage toll machine:** Required ticket first, then credit card; more flexible systems accept either order. → *Rule: When a multi-step physical interaction has no technical requirement for a specific order, requiring that order places burden on the user for system convenience, not user benefit.*

## Rules (consolidated)
- [definition] Different users, or the same user at different times, construct the same goal differently. This is not a weakness — it reflects how human cognition naturally varies.
- [examples] Voice interfaces are particularly prone because natural language construction varies significantly between users and contexts.
- [how to avoid] Understand all the different ways users conceptualize the tasks your product supports. Systematically plan which tasks should support object→action AND action→object constructions.
- [how to find] Observe real users attempting tasks without guidance. Where they try to start somewhere different from where the interface requires, a Forced Syntax problem exists.
- [AI detectability] Tier 2: fixed sequences identifiable in design files but whether unnatural for real users requires user knowledge.

## Related Traps
- **Gratuitous Redundancy** (mutually exclusive): Flexible syntax accommodates different mental models; Gratuitous Redundancy duplicates paths via the same construction. See FAQ in manuscript.
- **Unnecessary Steps** (sometimes caused by): When users must restart due to Forced Syntax, extra steps result.

## Report Language (U6)
**Finding:** [Task/Flow] can only be initiated in one order — users who naturally approach this task from a different starting point will find the interface unresponsive to their intent.
**Why it matters:** Users who think differently from the assumed sequence must reorganize their approach before proceeding — adding friction and reducing efficiency.
**Confidence:** [Tier 2: Flagged — confirm alternative starting points with user observation]

## Remediation (U7)
Identify all reasonable starting points users might use for this task and ensure the interface accepts them. Plan explicitly which tasks should support object→action AND action→object constructions — providing both allows users to approach tasks in the way that feels natural.

## AI Detection Rules
**Tier 2 — Output to `potential_issues`, confidence "medium":** Fixed sequences identifiable in design files and task flows — flag when the sequence appears unnatural for the user population described. Caveat: "Syntax requirements may extend beyond visible screenshots."
**`testable: false`:** Whether a specific sequence is genuinely unnatural for real users requires user population knowledge.
**vs. GRATUITOUS REDUNDANCY:** Mutually exclusive per task flow. Forced Syntax provides only one grammatical construction; Gratuitous Redundancy duplicates paths via the same construction. Confirm which is present before flagging.

---

# CHUNK: MEMORY CHALLENGE

**chunk_id:** trap_memory_challenge_v2
**tenet:** Understandable | **sub-tenet:** Comprehensible
**severity_combination_rule:** High when consequence is task failure or worse, regardless of likelihood.

## Definition (verbatim)
The user is required to remember information that is easy to forget.

Examples: requiring users to hold information in mind from one screen to the next; recall passwords or commands from long-term memory without retrieval cues; execute multi-step processes by memory alone.

## DISCONFIRMATION — Apply First
NOT present when:
(a) The information is genuinely easy to remember in context — a user's own name, a PIN used daily.
(b) The interface presents information for selection rather than requiring recall — recognition task, not recall task.
(c) The information is available for reference during the task and the user is not required to hold it in memory.

**Key distinction from System Amnesia:** Memory Challenge = system requires the user to remember something easy to forget. System Amnesia = system previously collected the information from the user but fails to use it. When both are present (system has the data AND user must recall it anyway), cite System Amnesia as root cause.

## Severity
**Part A — Consequence:** Task failure when user cannot recall required information and no recovery path exists. Significant friction when recall fails and recovery is available but effortful.
**Part B — Likelihood:** High when: information must be carried across a context boundary (screen, session, application); information is context-free (no retrieval cue); interaction is infrequent. Low when: information is used daily, is spatially represented, chunked or otherwise structured to facilitate recall, or provided as a recognizable list to choose from.
**Combination rule:** High severity when consequence is task failure or worse, regardless of likelihood.

## Confidence Tiers
- **Tier 2:** Flows requiring recall without retrieval cues are identifiable in design files. Whether the specific information is genuinely easy to forget requires user population knowledge.

## Root Cause Confirmation (U4)
- **System Amnesia** (distinction): If the system had the opportunity to collect the data but did not, or collected it but did not use it, cite System Amnesia as root cause. If the user is required to remember information the system never had, that is Memory Challenge.
- **Invisible Element** (sometimes co-occurs): An invisible interaction the user was taught but forgot is both — confirm which is the primary issue.

## Examples → Rules
- **[Example 8.1] American Express security question:** Required users to remember both the security question AND their answer. → *Rule: Security mechanisms requiring recall of context-free strings (passwords, security questions) without retrieval cues create this Trap. Show the security question rather than requiring users to remember which one they chose.*
- **[Example 8.2] Smart elevator systems:** Brief display of elevator letter/number easy to forget in distracting lobby; spatial maps (showing elevator position) are more robust. → *Rule: When users must hold information while taking an action, spatial representation is significantly more robust than alphanumeric information. Externalize spatial relationships the brain would otherwise hold in memory.*
- **[Example 8.3] Workday address re-entry:** Users required to re-enter address in subsequent modules despite having entered it in earlier ones. → *Rule: Any time a user is asked to re-enter information they have already provided to the system, both Memory Challenge and System Amnesia are present. Cite System Amnesia as root cause since the system had the data.*
- **[Example 8.4] Xbox voice command list:** Extensive lists of voice commands impossible to internalize. → *Rule: Voice interfaces requiring recall of commands from memory without in-context cues impose this Trap proportional to command count. "See it, say it" pattern — displaying available commands in context — converts recall to recognition.*

## Rules (consolidated)
- [definition] Recognition (matching against something visible) is fast, reliable, and deeply evolved. Recall (searching memory without external template) is slow, effortful, error-prone. Design for recognition over recall wherever possible.
- [definition] Spatial memory is remarkably robust. Nearly half the cortex processes spatial information. Use spatial representations over text where possible.
- [examples] Short-term memory is extraordinarily volatile — even carrying a small piece of information from one screen to the next may be asking too much.
- [governing question] Am I asking the user to remember this, or am I giving them a way to recognize it?
- [AI detectability] Tier 2: flows requiring recall without retrieval cues identifiable in design files. Whether information is genuinely easy to forget requires user population knowledge.

## Related Traps
- **System Amnesia** (distinguish): Memory Challenge is a design demand on the user; System Amnesia is a data architecture failure. Both may co-occur — cite System Amnesia as root cause when the system had the data.
- **Uncomprehended Element** (distinguish): Uncomprehended Element = never learned; Memory Challenge = learned but difficult to retrieve. Interventions differ.
- **Invisible Element** (sometimes co-occurs): An invisible interaction the user was trained on but later forgot is both.

## Report Language (U6)
**Finding:** [Task/Step] requires users to recall [information] without a retrieval cue, in a context where this information is likely to be forgotten.
**Why it matters:** When users cannot recall this information, they cannot complete the task — and may not know how to recover.
**Confidence:** [Tier 2: Flagged — confirm interaction frequency and information memorability with user data]

## Remediation (U7)
Design for recognition over recall — let users see and choose rather than remember and enter. Present information spatially and chunk it whenever possible to facilitate recall. When users must produce information from memory, provide retrieval cues. The governing question: am I asking the user to remember this, or am I giving them a way to recognize it?

## AI Detection Rules
**Tier 1 — Confirmed finding:** When multiple screens show both the source information AND the recall demand — confirmable without user testing.
**Tier 2 — Output to `potential_issues`, confidence "medium":** When the artifact explicitly reveals users must recall prior-session information with no retrieval cue (e.g., instructions to recall a security question, blank credential fields with no hint). Flag: "This screen requires users to recall [information] from a prior session with no retrieval cue visible." Caveat: "Earlier screens may have provided this information."
**`testable: false`:** When memory demand can only be inferred from knowing what earlier screens contained.
**vs. SYSTEM AMNESIA:** Memory Challenge = system requires the user to remember something easy to forget. System Amnesia = system previously collected the information but fails to use it. When both apply, cite System Amnesia as root cause.

---

# CHUNK: FEEDBACK FAILURE

**chunk_id:** trap_feedback_failure_v2
**tenet:** Understandable | **sub-tenet:** Confirmatory
**severity_combination_rule:** High when consequence is task failure or worse, regardless of likelihood.

## Definition (verbatim)
The system fails to communicate to the user the consequence of their actions, or how to resolve a failed action.

**Important:** Feedback Failure is not defined by a single mechanism but by a moment in time — what happens after the user acts. It is always caused by another Trap. Its purpose is to ensure evaluators pay special attention to whether a system closes the loop on users' actions.

## DISCONFIRMATION — Apply First
NOT present when:
(a) The action's consequence is self-evident from the resulting interface state — no additional feedback needed.
(b) The absence of feedback is itself the meaningful signal — silence confirming no error.
(c) Feedback exists but is not reaching the user due to another Trap — in that case, Feedback Failure is the symptom and the root cause Trap requires fixing.

## Severity
**Part A — Consequence:** Ranges from confusion and repeated attempts (minor) to inability to recover from error (task failure) to compounding an irreversible action with no recovery guidance (significant harm) to potential injury due to absence of safety-critical feedback (severe harm).
**Part B — Likelihood:** High when: action has ambiguous or non-obvious outcome; interface includes error states with no recovery guidance; physical controls replaced with touch surfaces providing no tactile confirmation. Low when: resulting state change is visually obvious and self-explanatory.
**Combination rule:** High severity when consequence is task failure or worse, regardless of likelihood.

## Confidence Tiers
- **Tier 1:** Error messages — auditable from design files: do they answer "what happened?" AND "what should I do?" Both questions must be answered.
- **Tier 1:** Actions that produce no noticeable system response — detectable by auditing action→response pairs.
- **Tier 2:** Noticeability and comprehensibility — whether feedback is seen and understood requires user knowledge.

## Root Cause Confirmation (U4)
**Critical — identify root cause before flagging:**
(1) No feedback element exists → **Invisible Element** (root cause)
(2) Feedback present but away from attentional focus → **Effectively Invisible Element** (root cause)
(3) Feedback present and noticed but unclear → **Uncomprehended Element** (root cause)
(4) Feedback present but physically hard to perceive → **Physical Challenge** (root cause)
(5) Feedback delayed → **Slow or No Response** (root cause)
(6) Feedback factually wrong → **Incorrect Information** (root cause)

The root cause determines the fix. Do not flag Feedback Failure without identifying which of these is causing it.

**Irreversible Action (see also):** Recovery feedback is only useful when recovery is possible. When an action cannot be undone, even clear feedback cannot compensate for the absence of a path back. Flag both Traps when an irreversible action produces inadequate feedback.

## Examples → Rules
- **[Example 9.1] Generic error messages (e.g., "Word did not save the document"):** Tells users something went wrong without telling them what to do. → *Rule: Every error message must answer two questions: what went wrong, and what should the user do now? Messages answering only the first are this Trap. Auditing error messages requires no user testing.*
- **[Example 9.2] VW capacitive steering wheel buttons (2020, reverted 2024):** Replacing physical buttons with capacitive surfaces removed tactile feedback for location and activation; users complained. → *Rule: Physical controls provide immediate tactile feedback communicating both location and activation. Replacing them with touch surfaces removes this feedback channel. Substitute feedback must be designed explicitly.*
- **[Example 9.3] YouTube dislike count removal (2021):** Users confused about purpose of a dislike button showing no count; tooltip feedback added temporarily. → *Rule: When an action's consequence is not visible to the user who took it, the feedback loop is broken. Removing the visible consequence without replacing it creates this Trap.*
- **[Example 9.4] Reddit real-time email validation:** Past: error revealed only on submit. Now: real-time validation during input. → *Rule: When input validity can be assessed before submission, real-time feedback is superior to post-submission error messages.*
- **[Example 9.5] Meta Quest VR play space (improved):** Manual boundary drawing could miss hazards; improved with automatic safe zones and obstacle warnings. → *Rule: Feedback is not limited to confirming intended actions — it includes surfacing consequences the user's senses cannot reach.*

## Rules (consolidated)
- [definition] Feedback Failure is always caused by another Trap. Identifying which is the key to knowing how to fix it.
- [definition] Continuous, real-time feedback is more natural, more informative, and more forgiving than discrete post-submission feedback.
- [examples] Error messages that tell users what went wrong without telling them what to do are this Trap. Auditing error messages is one of the fastest, cheapest ways to detect it.
- [how to avoid] Every action in the interface should produce a response that is immediate, clear, and sufficient.
- [AI detectability] Tier 1 for error message audit (action→response pairs) and absence of response. Tier 2 for noticeability/comprehensibility of existing feedback. Not reliable for physical interfaces where physical feedback is critical.

## Related Traps
- **Invisible Element, Effectively Invisible Element, Uncomprehended Element, Physical Challenge, Slow or No Response, Incorrect Information:** All are root causes of Feedback Failure. See Root Cause Confirmation above.
- **Irreversible Action (see also):** When irreversible action produces inadequate feedback, flag both.

## Report Language (U6)
**Finding:** When users take [action], the system fails to communicate [what happened / what to do next] in a way that is [noticeable / comprehensible / actionable].
**Why it matters:** Without clear feedback, users cannot confirm their action succeeded, recover from errors, or learn how the system responds to their input.
**Confidence:** [Tier 1: Confirmed for absent or non-actionable error messages / Tier 2: Flagged — confirm feedback visibility with user observation]

## Remediation (U7)
Every action should produce a response that is immediate, clear, and sufficient. Error messages must answer two questions: what went wrong, and what should the user do now? Continuous real-time feedback is superior to post-submission feedback. The fix depends entirely on the root cause — identify which Trap is causing the failure before designing a solution.

## AI Detection Rules
**Tier 1 — Confirmed finding:**
(a) Error messages visible in the artifact that fail to answer BOTH "what happened?" AND "what should I do?" — answering only one question is this Trap.
(b) Interactive elements where no in-screen response state is visible (no loading indicator, button state change, or inline confirmation on the same screen).
**Critical distinction — in-screen vs. post-action feedback:**
- Feedback that should appear on the same screen immediately → confirmed absent if not visible on that screen, Tier 1 finding.
- Feedback on a subsequent screen (toast, confirmation page after transition) → DO NOT assert absent. Apply the partial artifact rule; use conditional language: "If no confirmation screen or toast exists elsewhere in this flow, users would have no indication the action completed."
**`testable: false`:** Assessing whether feedback is noticeable or comprehensible to real users.

---

# TRAP CHUNKS — COMFORTABLE TENET

---

# CHUNK: PHYSICAL CHALLENGE

**chunk_id:** trap_physical_challenge_v2
**tenet:** Comfortable
**severity_combination_rule:** High when consequence is task failure or worse, regardless of likelihood.

## Definition (verbatim)
Some aspect of the system causes physical discomfort or makes it physically difficult or impossible for the user to complete actions.

Manifestations: touch targets too small to hit reliably, text too faint to read without strain, controls out of comfortable reach, device too heavy or sharp-edged for extended use, audio prompts too quiet, surfaces too hot to touch, VR video too jittery causing queasiness. The user understands what to do but doing it means strain, discomfort, or worse.

## DISCONFIRMATION — Apply First
NOT present when:
(a) The physical demand falls within established guidelines for the expected user population and context — minimum touch target size, contrast ratios, font sizes, audio levels.
(b) Physical difficulty is intentional and appropriate to the use case — games that test dexterity are not this Trap.
(c) Difficulty exists only in test conditions that don't reflect real-world use — must be assessed under realistic conditions.

## Severity
**Part A — Consequence:** Ranges from minor targeting errors (friction) to inability to use the interface at all, especially for users with physical limitations (exclusion), to illness or injury in extreme cases (VR motion sickness, thermal burns).
**Part B — Likelihood:** High when: touch targets measurably below 12mm; text contrast falls below WCAG standards; controls outside one-handed reach zone for device size. These are objective and measurable. For other manifestations (weight, temperature, VR comfort), likelihood requires hardware testing.
**Combination rule:** High severity when consequence is task failure or worse, regardless of likelihood.

## Confidence Tiers
- **Tier 1:** Measurable properties — touch target size vs. 12mm standard, text contrast vs. WCAG standards. Checkable against guidelines in design files.
- **Tier 3:** Real-world conditions — weight, thermal comfort, VR sickness, one-handed reach on real hardware. Cannot be assessed from design files.

## Root Cause Confirmation (U4)
- **Accidental Activation** (opposite failure mode): Physical Challenge makes intended actions too difficult; Accidental Activation makes unintended actions too easy. They pull in opposite directions — confirm both independently. A design that makes intended actions hard does not automatically make unintended actions easy.
- **Feedback Failure** (sometimes co-occurs): Confirm independently that tactile or visual confirmation of physical interaction is absent — not merely that the physical action is difficult.

## Examples → Rules
- **[Example 10.1] iPhone lock screen music controls:** Touch targets substantially smaller than 12mm average finger pad; targeting errors resulted; ultimately enlarged. → *Rule: Touch targets substantially smaller than the 12mm average finger pad will produce targeting errors regardless of user skill or motivation. When a design change that addresses a physical constraint resolves user difficulty, the original design had this Trap.*
- **[Example 10.2] Mobile phone reach zones (Hurff's Touch Zones):** As screens grew larger, top-of-screen controls exceeded comfortable one-handed reach; reachability features introduced as engineering workarounds. → *Rule: Fitts' Law assumes unconstrained reach. Ergonomic constraints (grip position, hand size) reduce effective target size below what the formula predicts. Controls must be within comfortable reach for the intended grip.*
- **[Example 10.3] Zillow high-contrast text (2017):** Increasing text contrast produced measurable engagement jump. → *Rule: Text legibility is not only an accessibility issue — it directly drives engagement. Poor contrast makes the product feel more complex overall, reducing likelihood of use.*
- **[Example 10.4] Apple Vision Pro headset (2023):** Discomfort from size/weight after extended use; Apple updated headband. → *Rule: For wearable devices, comfort is time-dependent. Adequate comfort for brief use may become this Trap for extended use. Testing under realistic duration is required.*
- **[Example 10.5] Apple Liquid Glass (2025):** Readability issues followed by opacity adjustment option. → *Rule: Visual design decisions that reduce contrast or legibility require validation against WCAG standards. Design aesthetics do not override legibility requirements.*
- **[Example 10.6] VW capacitive steering wheel buttons (2020, reverted 2024):** Removing tactile buttons eliminated location and activation feedback; VW reverted to physical controls. → *Rule: Physical feedback from controls (key travel, click resistance, tactile bumps) is a form of Comfortable design. Removing it creates both Physical Challenge (location/targeting) and Feedback Failure simultaneously.*

## Rules (consolidated)
- [definition] Three severity levels: effortful, difficult, impossible. Impossible is most severe; effortful is the minimum threshold.
- [examples] 12mm is the established minimum touch target for the average finger pad.
- [examples] Improving contrast not only removes Physical Challenge but demonstrably increases engagement.
- [examples] Physical Challenge is not always visible in design files — many instances only emerge through testing on real hardware in real environments.
- [why it occurs] Designers working on high-resolution monitors, in even lighting, with both hands free, under non-realistic conditions fail to identify issues.
- [how to avoid] Follow guidelines. Prototype and test on real hardware in realistic conditions. Iterative physical prototyping is critical.
- [AI detectability] Tier 1 for touch target size and contrast ratio violations. Tier 3 for real-world conditions — requires hardware testing.

## Related Traps
- **Accidental Activation** (opposite failure mode): Enlarging targets to resolve Physical Challenge increases Accidental Activation risk — evaluate both together.
- **Feedback Failure** (sometimes co-occurs): Absence of tactile/visual confirmation of physical interaction; confirm independently.

## Report Language (U6)
**Finding:** [Element/interaction] imposes a physical demand that exceeds [established guideline / comfortable reach / legibility threshold] for [the expected user population / the expected use context].
**Why it matters:** Physical barriers cause errors and exclusion — and reduce users' perception of overall product quality independent of the specific difficulty.
**Confidence:** [Tier 1: Confirmed for measurable guideline violations / Tier 3: Risk noted — confirm with hardware testing for non-measurable properties]

## Remediation (U7)
Follow established guidelines: minimum 12mm touch targets, WCAG contrast ratios, platform-specific reach zone guidance. Prototype and test on real hardware in realistic conditions. Improving contrast not only removes this Trap but demonstrably increases engagement. Caution: enlarging targets to resolve Physical Challenge may increase Accidental Activation risk — evaluate both together.

## AI Detection Rules
**Tier 1 — Confirmed finding:** Measurable violations: touch targets visibly below 12mm, text contrast below WCAG minimums, text size below legibility thresholds. Checkable against guidelines in design files.
**Tier 3 — Risk noted, output to `potential_issues`, confidence "low":** Non-measurable properties (weight, thermal comfort, VR motion sickness, one-handed reach) — note explicitly that hardware testing is required.

---

# CHUNK: ACCIDENTAL ACTIVATION

**chunk_id:** trap_accidental_activation_v2
**tenet:** Comfortable
**severity_combination_rule:** High when consequence is task failure or worse, regardless of likelihood.

## Definition (verbatim)
It's easy for the user to unintentionally trigger an action during normal use.

The mirror image of Physical Challenge. Where Physical Challenge makes intended actions too difficult, Accidental Activation makes unintended actions too easy. The Trap occurs when physical properties of a control — size, sensitivity, placement, or activation gesture — make it vulnerable to unintended triggering.

## DISCONFIRMATION — Apply First
NOT present when:
(a) Activation requires a deliberate, non-incidental physical action unlikely to occur during normal device handling.
(b) The accidental activation is immediately reversible with minimal consequence — this reduces severity but does not eliminate the Trap.
(c) The input vocabulary does not overlap with natural behaviors in the context of use.

**Key distinction from Bad Prediction:** Accidental Activation involves insufficient physical barriers where no intent inference is involved (a button pressed accidentally is simply a button pressed — the system responds to the physical input). Bad Prediction involves a system probabilistically misinterpreting intent. When the system makes an intent inference and gets it wrong, cite Bad Prediction as the root cause.

## Severity
**Part A — Consequence:** Scales with reversibility and consequence of triggered action. Accidental screenshot: minor nuisance. Accidental purchase: significant. Accidental emergency call or recording: severe. The acceptable false-positive rate approaches zero for actions with privacy or safety implications.
**Part B — Likelihood:** High when: controls at natural grip points; gesture vocabulary overlaps with natural behavior in context of use; passive sensor-based activation used. Low when: controls require deliberate, non-incidental actions to trigger.
**Combination rule:** High severity when consequence is task failure or worse, regardless of likelihood.

## Confidence Tiers
- **Tier 2:** Control placement relative to known grip points visible in design file — flag as candidate.
- **Tier 3:** Actual activation behavior requires hardware testing under realistic use conditions.

## Root Cause Confirmation (U4)
- **Bad Prediction** (sometimes the root cause): Confirm independently that the system interpreted the physical action as intentional probabilistically (Bad Prediction) rather than responding to a simple binary signal. Bad Prediction involves wrong intent inference; Accidental Activation proper involves insufficient physical barriers with no intent guessing.
- **Physical Challenge** (opposite failure mode): Confirm both independently — they pull in opposite directions and each requires its own evidence.
- **Variable Outcome** (sometimes causes): Interfaces where the same physical action produces different outcomes depending on system state are particularly prone. Inconsistency is the root cause.

## Examples → Rules
- **[Example 11.1] iPhone screenshot (side button + volume up):** Side button inadvertently created screenshot gesture at natural grip points; Apple mitigations left underlying cause untouched; iPhone 16 Camera Control added analogous problem in same zone. → *Rule: Controls placed at natural grip points will be accidentally activated regardless of design intent. Grip zone analysis must precede control placement decisions.*
- **[Example 11.2] Kinect gesture interface:** Navigational swipe and natural behaviors (scratching ear) could not be distinguished by recognition system. → *Rule: When a gesture or voice vocabulary overlaps with natural human behaviors in the context of use, accidental activations will occur regardless of recognition system sophistication.*
- **[Example 11.3] Gemalto Smart USB token:** Many users experienced accidental activation simply from how the token was held or carried. → *Rule: Controls on portable devices must account for all physical interactions during transport and storage, not only during intentional use.*
- **[Example 11.4] Wayfair Megamenu:** The Wayfair shopping site includes a “mega menu” that can be accidently activated if users unintentionally hover their mouse pointer over the tabs at the top. → *Rule: Controls that automatically engage on hover must account for what happens when user did not intend to take advantage of the automatically deployed interface element.*

## Rules (consolidated)
- [definition] The relationship with Physical Challenge is a source of tension: larger targets reduce Physical Challenge but increase Accidental Activation risk. No universal resolution — the right balance depends on context, stakes, and reversibility.
- [examples] Grip zone analysis must precede control placement decisions for physical devices.
- [examples] Gesture and voice vocabularies that overlap with natural behavior will produce accidental activations regardless of recognition sophistication.
- [why it occurs] Optimizing ease of access to a control without considering full range of physical interactions during normal device use.
- [how to avoid] Add friction: recess or shield controls, require sequential actions, add physical resistance. Use confirmation as last resort — only for actions that are both consequential AND irreversible, after physical design options exhausted.
- [AI detectability] Tier 2 for control placement relative to grip points from design files. Tier 3 for actual activation behavior — requires hardware testing.

## Related Traps
- **Physical Challenge** (opposite failure mode): Adding friction to reduce Accidental Activation may increase Physical Challenge. Evaluate both together.
- **Bad Prediction** (sometimes root cause): When system misreads intent probabilistically, Bad Prediction is the root cause of what appears as Accidental Activation.
- **Inviting Dead End** (distinguish): Inviting Dead End lures the user in deliberately; Accidental Activation occurs without the user noticing. One misleads; the other fails to prevent.

## Report Language (U6)
**Finding:** [Control/gesture/activation mechanism] is positioned or configured in a way that makes unintentional triggering likely during normal device use.
**Why it matters:** Accidental activations are difficult to prevent even when users give attention and care. The severity scales directly with the reversibility and consequence of the triggered action: from minor nuisance (accidental screenshot) to severe harm (accidental emergency call or recording).
**Confidence:** [Tier 3: Risk noted — confirm with hardware testing under realistic use conditions]

## Remediation (U7)
Add friction to the activation path: recess or shield controls, require sequential actions before critical functions execute, add physical resistance, or increase gesture distinctiveness. Reserve confirmation dialogs as a last resort — they add Unnecessary Steps for the majority of intentional users. Use confirmation only for actions that are both consequential AND irreversible, after physical design options are exhausted. Caution: friction that reduces Accidental Activation may increase Physical Challenge — calibrate to context and stakes.

## AI Detection Rules
**Tier 3 — Risk noted, output to `potential_issues`, confidence "low":** When controls are visibly positioned at natural grip points for the device type shown (e.g., controls at the edges or back of a phone, gesture-activated surfaces covering the full device). Note explicitly that hardware testing is required to confirm.
**`testable: false`:** For all other instances.

---

# TRAP CHUNKS — RESPONSIVE TENET

---

# CHUNK: SLOW OR NO RESPONSE

**chunk_id:** trap_slow_or_no_response_v2
**tenet:** Responsive
**severity_combination_rule:** High when consequence is task failure or worse, regardless of likelihood.

## Definition (verbatim)
The actual or perceived time it takes the system to respond exceeds what the user wants or expects.

Arises from both objectively measurable delays and design decisions that impact the subjective experience of waiting.

## DISCONFIRMATION — Apply First
NOT present when:
(a) Response time is within established thresholds for the interaction type AND well-designed progress feedback is provided for longer operations.
(b) Deliberate pacing serves a legitimate purpose — an animation that aids state change comprehension is not this Trap.
(c) The system responds too quickly and a small delay is a corrective measure to ensure the user can track the change. (A system can respond too quickly — this Trap only applies in the too-slow direction.)

## Severity
**Part A — Consequence:** Ranges from frustration and repeated inputs (minor) to task abandonment at the 10-second threshold (significant).
**Part B — Likelihood (established thresholds — objectively measurable):**
- VR/AR tracking: sub-10ms required
- Digital ink response: sub-10ms required
- Button/tap feedback: sub-100ms (feels instantaneous); beyond this, delay becomes perceptible
- Conversational exchanges: sub-1 second (gap in human conversation averages ~250ms)
- Before task abandonment risk: sub-10 seconds
Also applies to captive waits where duration is undisclosed.
**Combination rule:** High severity when consequence is task failure or worse, regardless of likelihood.

## Confidence Tiers
- **Tier 1:** Measurable response times against established thresholds.
- **Tier 2:** Perceived slowness — a system within objective bounds may still feel slow due to absent or poorly designed progress feedback.
- **Tier 2:** Captive wait variant — design intent visible in files but adequacy of duration and skip options requires context assessment.

## Root Cause Confirmation (U4)
- **Feedback Failure** (often co-occurs): Confirm independently that no progress indication is provided during the delay. A slow system with well-designed progress feedback has this Trap but not Feedback Failure. Both require separate evidence.

## Examples → Rules
- **[Example 12.1] SuperBright LED Flashlight (Android):** 5-second delay for a tool whose primary use is immediate illumination in urgent situations. → *Rule: Severity scales with how critical timely response is to the use case. When the primary use context demands immediate response, even a 5-second delay defeats the tool's core purpose.*
- **[Example 12.2] Conversational AI interfaces:** Responses delayed beyond 1 second cause users to attribute rudeness or incompetence to the system. → *Rule: For conversational interfaces, the comparison set is human-to-human conversation (~250ms gaps). Delays beyond 1 second break conversational expectations and cause users to make negative personality attributions.*

## Rules (consolidated)
- [definition] Perceived slowness is a legitimate form of this Trap even when actual performance is acceptable. A system that performs adequately but feels slow has a problem requiring design intervention.
- [examples] Severity scales with how critical timely response is to the use case and context.
- [related concepts] Occupied time feels shorter than unoccupied time (1.4–1.8× longer perceived for unoccupied waits). Skeleton screens, progressive loading, and background activity reduce perceived wait without changing actual duration.
- [related concepts] Peak-End Rule: a slow process that ends quickly and cleanly is remembered more favorably than one that starts quickly and bogs down at the end. Optimize the end of long processes.
- [related concepts] Weber-Fechner Law: to make a response feel faster, it must improve by at least 20%. Sub-20% improvements are imperceptible.
- [AI detectability] Tier 1 for measurable response times. Tier 2 for perceived slowness and progress feedback quality.

## Related Traps
- **Feedback Failure** (often co-occurs): No progress indication during delay; confirm independently.
- **Physical Challenge** (see also): Interfaces responding too quickly can outpace users' ability to respond accurately. Note the system can respond too quickly as well.

## Report Language (U6)
**Finding:** [Interaction/process] takes [observed/estimated duration] to respond — [exceeding the established threshold for this interaction type / with no or poorly designed progress indication during the wait].
**Why it matters:** Delays beyond perception thresholds cause users to repeat actions, abandon tasks, or lose confidence that the system received their input.
**Confidence:** [Tier 1: Confirmed against measurable thresholds / Tier 2: Flagged — confirm perceived response quality with user observation]

## Remediation (U7)
For interactions below the 100ms threshold: provide immediate confirmation that the action was received before the full response is ready. For processes over 1 second: provide continuous progress feedback. Never leave users facing a static screen with no indication the system is working. Apply occupied-time principles — skeleton screens, progressive loading, and background activity reduce perceived wait without changing actual duration. For captive waits: make them skippable or communicate exact duration upfront.

## AI Detection Rules
**`testable: false`:** Actual response times require live performance measurement; perceived slowness requires user observation. Always omit this trap from `traps_checked_not_found` — it is added automatically to the output.

---

# CHUNK: CAPTIVE WAIT

**chunk_id:** trap_captive_wait_v2
**tenet:** Responsive
**severity_combination_rule:** High when consequence is task failure or worse, regardless of likelihood.

## Definition (verbatim)
The system does not allow the user to advance or back out of a process at a time of their choosing.

Coined by Steve Seow. Captive Wait describes any process that holds the user hostage. May be driven by technical constraints but often is a business or design-driven choice. Examples: un-skippable pre-roll ads, un-skippable cutscenes, install/update procedures that take over a device.

## DISCONFIRMATION — Apply First
NOT present when:
(a) The wait is skippable — even a brief mandatory period followed by a skip option significantly reduces the Trap.
(b) The wait duration is clearly communicated upfront and is short enough that users judge it reasonable for the purpose.
(c) The captive period is technically unavoidable AND users were informed in advance with an accurate duration estimate AND the user finds the technical limitation reasonable.

## Severity
**Part A — Consequence:** Frustration disproportionate to actual time cost — perceived control significantly affects experience independent of objective duration. Task abandonment for longer captive waits. Competitive vulnerability when competing products offer same content without mandatory viewing.
**Part B — Likelihood:** High when: users are in active goal pursuit rather than passive browsing; captive content is unrelated to user's goal; no duration information is provided. Low when: captive content serves user's goal (required legal disclosure, essential setup step).
**Combination rule:** High severity when consequence is task failure or worse, regardless of likelihood.

## Confidence Tiers
- **Tier 2:** Mandatory flows and unskippable sequences are identifiable in design files. Whether duration and lack of skip option constitute a meaningful Trap depends on context and duration.

## Root Cause Confirmation (U4)
- **Feedback Failure** (often co-occurs): Confirm independently that the captive wait provides no information about its duration or purpose. A captive wait with clear duration and purpose disclosure has this Trap but not Feedback Failure.

## Examples → Rules
- **[Example 13.1] YouTube pre-roll ads (unskippable):** Users cannot advance to content during mandatory ad viewing. → *Rule: Any process that prevents users from advancing to their goal for organizational or business reasons — not technical necessity — is this Trap. The business justification does not resolve the user experience failure.*
- **[Example 13.2] Self-cleaning oven locked during cycle (Seow example):** System unavailable during cleaning; no indication of when it will end. → *Rule: When a system must be unavailable, communicating duration upfront and notifying when complete does not eliminate the Trap but meaningfully reduces its severity. No information about duration compounds frustration disproportionately.*
- **[Example 13.3] Ragnorök video game:** Players of the acclaimed God of War Ragnarök are prevented from skipping these sequences. This is especially frustrating when a player wants to re-attempt a challenging battle that follows the cutscene – to do so, they must watch the entire scene again→ *Rule: Designs should allow users to advance through cutscenes especially if the user has already been exposed to the content before.*


## Rules (consolidated)
- [definition] Two distinct causes: (1) organizational — business models depending on forced exposure; (2) design — mandatory flows imposed to ensure information delivery without considering user autonomy.
- [related concepts] Perceived control over an experience significantly affects how it is rated, independent of objective properties. Users who can skip an ad rate the experience better than those who cannot, even when ad duration is identical.
- [how to avoid] Question every point where the user cannot advance, back out, or skip. In most cases, the best alternative is progressive disclosure: surface critical information at the moment needed, not forced in advance.
- [AI detectability] Tier 2: identifiable from design documentation or code showing if/when the interface puts the user in a timed state they cannot exit.

## Related Traps
- **Feedback Failure** (often co-occurs): Captive wait without duration/purpose information compounds the experience. Confirm independently.

## Report Language (U6)
**Finding:** [Flow/Screen] prevents users from advancing or backing out for [duration/unknown duration], without [disclosing the duration / offering a skip option / serving the user's current goal].
**Why it matters:** Perceived control significantly affects experience independent of actual duration. Captive waits generate frustration disproportionate to their time cost precisely because they remove user autonomy.
**Confidence:** [Tier 2: Flagged — confirm duration, skip availability, and relevance to user goal]

## Remediation (U7)
Question every point where users cannot advance, back out, or skip. For unavoidable captive periods: communicate duration upfront, make content skippable as quickly as possible, ensure content serves the user's goal. For system processes (updates, installations): give advance notice, allow parallel tasks where possible, notify when complete.

## AI Detection Rules
**Tier 2 — Output to `potential_issues`, confidence "medium":** When the artifact shows a mandatory sequence, interstitial, or process with no visible skip option, no visible duration indicator, and no visible means of backing out. Flag: "This sequence appears to prevent users from advancing or exiting — confirm whether a skip option or duration disclosure exists."
**`testable: false`:** Assessing whether the duration and purpose justify the captive period.

---

# TRAP CHUNKS — EFFICIENT TENET

---

# CHUNK: UNNECESSARY STEP(S)

**chunk_id:** trap_unnecessary_steps_v2
**tenet:** Efficient
**severity_combination_rule:** High when consequence is task failure or worse, regardless of likelihood.

## Definition (verbatim)
The number of steps a user must take to achieve a goal is greater than it needs to be.

Examples: multi-step workflows for simple tasks, nested architectures in lieu of flat ones, confirmation requests in lieu of reversible actions. Both actual steps (measurable interactions) and perceived steps (interactions that feel like more work) qualify.

## DISCONFIRMATION — Apply First
NOT present when:
(a) A step that appears unnecessary serves a legitimate purpose — a confirmation step for a consequential irreversible action.
(b) The step reduces cognitive load by breaking a complex decision into manageable parts — the goal is the right number of steps, not the minimum number.
(c) The step is required for security, legal, or safety reasons that have been deliberately documented.

## Severity
**Part A — Consequence:** Friction and reduced efficiency in most cases. Task abandonment for high-frequency tasks where cumulative step cost erodes motivation. Competitive vulnerability when a competing product offers the same function in fewer steps.
**Part B — Likelihood:** High when: task is high-frequency and extra steps apply to every instance; steps were added by different teams at different times without end-to-end audit; confirmation dialogs substitute for reversibility. Low when: steps are infrequent, low-effort, or serve a purpose users understand.
**Combination rule:** High severity when consequence is task failure or worse, regardless of likelihood.

## Confidence Tiers
- **Tier 1:** Confirmation dialogs on reversible actions — detectable and by definition unnecessary when reversal is available.
- **Tier 2:** Step counts visible in task flow documentation but whether steps are genuinely unnecessary requires knowledge of user goals and legitimate purpose.

## Root Cause Confirmation (U4)
- **Gratuitous Redundancy** (sometimes root cause): Confirm independently that duplicate paths exist and are displacing content off screen — do not infer from step count alone.
- **Irreversible Action** (related): Confirm independently that the action is genuinely irreversible before judging a confirmation dialog as Unnecessary Step — if irreversible and consequential, the confirmation may be justified.

## Examples → Rules
- **[Example 14.1] Spotify hamburger menu elimination:** Moved high-frequency functions from hamburger to always-present nav bar; reported significant engagement gains. → *Rule: Every level of navigation a user must descend to reach a high-frequency goal is a step that may be eliminable by flattening the structure. Engagement gains from flattening confirm the original hierarchy contained Unnecessary Steps.*
- **[Example 14.2] Amazon one-click purchase:** Eliminated all cart steps for known purchase. → *Rule: When the system has sufficient information to complete an action on the user's behalf without confirmation, requiring steps for that action is this Trap.*
- **[Example 14.3] Workday field-by-field confirmation:** Required OK/Cancel after every individual field entry in profile setup. → *Rule: When steps are applied uniformly to all fields regardless of their consequence, the confirmation mechanism is not calibrated to risk — it is a Trap for low-consequence fields.*
- **[Example 14.4] iPhone 2019 message deletion:** Functions (delete, flag, move) nested under reply function — one additional step away. → *Rule: When frequently used functions are nested under infrequently used functions for organizational convenience, users bear the inefficiency cost on every use.*
- **[Example 14.5] Android Auto one-touch apps:** Added physical shortcuts to replace voice+wake+speak sequence. → *Rule: Reducing step count can simultaneously address Invisible Element (hidden capability becomes visible) and Memory Challenge (commands no longer need to be recalled). Step reduction often resolves multiple Traps at once.*
- **[Example 14.5] Figma Auto Layout:** This feature reduced many of the steps needed to layout components. → *Rule: Step reduction is a powerful means of streamlining manual processes.*

## Rules (consolidated)
- [definition] The goal is the right number of steps, not the minimum. Steps serving legitimate purposes (security, safety, legal, cognitive load management) are not this Trap.
- [examples] Confirmation dialogs added as substitute for reversibility create Unnecessary Steps. Making actions reversible removes both the risk and the step.
- [why it occurs] Three sources: (1) caution — adding confirmation steps to prevent errors rather than allowing recovery; (2) organizational — steps added by different teams without auditing cumulative effect; (3) technical — backend constraints imposing steps for engineering reasons.
- [AI detectability] Tier 1 for confirmation dialogs on reversible actions. Tier 2 for other step counts — requires knowledge of user goals and legitimate purpose.

## Related Traps
- **Gratuitous Redundancy** (sometimes root cause): Redundant paths push content off screen, requiring scrolling and introducing steps.
- **Irreversible Action** (see also): Confirmation dialogs often added for irreversible actions. Making actions reversible eliminates both the risk and the step.

## Report Language (U6)
**Finding:** [Task/Flow] requires [N] steps to complete, [N-X] of which appear unnecessary — they could be eliminated, automated, or combined without loss to the quality of the experience.
**Why it matters:** Every unnecessary step is a cost paid on every use — compounding across frequency and user base into significant lost efficiency.
**Confidence:** [Tier 1: Confirmed for confirmation dialogs on reversible actions / Tier 2: Flagged — confirm step necessity with task analysis]

## Remediation (U7)
For navigation hierarchy: surface high-frequency functions to persistent navigation rather than nesting them. For confirmation dialogs: make the action reversible instead of confirming before taking it. Walk every task flow end to end and ask of each step: does this need to exist? Particular attention to flows built incrementally by different teams where cumulative step count has never been audited.

## AI Detection Rules
**Tier 2 — Requires complete task flows:** Steps can happen between the screenshots provided — a step visible in the artifact may be justified by context not shown. Flag when a step appears to add no value, but include the caveat: "Based on provided screenshots. Additional steps in the flow may provide context that justifies this step."
Output to `potential_issues`, confidence "medium".
**`testable: false`:** Whether the step is genuinely unnecessary requires seeing the full flow.

---

# CHUNK: INFORMATION OVERLOAD

**chunk_id:** trap_information_overload_v2
**tenet:** Efficient
**severity_combination_rule:** High when consequence is task failure or worse, regardless of likelihood.

## Definition (verbatim)
Information presented to the user is understandable but there's more of it than there needs to be.

Examples: verbose on-screen instructions, wordy responses from AI assistants, visually cluttered displays.

## DISCONFIRMATION — Apply First
NOT present when:
(a) All presented information is necessary for the user's goal in the current context — the test is not "could there be less?" but "does the user need all of this right now?"
(b) Information density is appropriate to the task of making sense of comprehensive related information — data dashboards for expert users who need comprehensive information qualify.
(c) Progressive disclosure is functioning correctly and secondary information appears only when needed.

## Severity
**Part A — Consequence:** Slowed progress and increased cognitive load in most cases. Longer decision-making time (Hick's Law) when option count is excessive. Task abandonment when information cost exceeds user motivation.
**Part B — Likelihood:** High when: primary task requires processing only a subset of what is displayed; interface has accumulated content over time without audit; multiple stakeholders have advocated for visibility of different features. Low when: user population is expert and genuinely needs comprehensive information to perform their role.
**Combination rule:** High severity when consequence is task failure or worse, regardless of likelihood.

## Confidence Tiers
- **Tier 2:** Element count, word count, and option density are measurable against guidelines but whether specific information is necessary requires knowledge of user goals and context.

## Root Cause Confirmation (U4)
- **Gratuitous Redundancy** (sometimes root cause): Confirm independently that duplicate paths or options exist — high density can arise from feature breadth, poor editing, or organizational pressure. Do not infer Gratuitous Redundancy from high density alone.
- **Distraction** (sometimes co-occurs): Confirm independently that specific elements actively draw attention away from user's goal — excess information alone constitutes Information Overload; attention-capturing elements constitute Distraction.

## Examples → Rules
- **[Example 15.1] Jeep dealer search (2002 → 2007):** Lengthy paragraph describing how to enter zip code replaced with just the input field. → *Rule: When a task requires only simple input, extensive explanatory text around it is Information Overload. The redesign demonstrates the extent to which information can be reduced without loss of usability — far more than teams typically assume is possible.*
- **[Example 15.2] Amazon Accounts & Lists reduction over time:** Substantially reduced options presented under this tab. → *Rule: Hick's Law: each doubling of choices adds a roughly constant increment of decision time. Reducing option count has disproportionately positive impact on decision speed. Audit interfaces that have grown over time.*
- **[Example 15.3] Amazon Alexa Voice Assistant:** Users complained voice responses were too wordy. A ‘brief mode’ setting was added to address this problem. → *Rule: Information overload extends to voice interfaces and allowing users to control a system's verbosity is critical.*


## Rules (consolidated)
- [definition] Specifically about comprehensible information in excess. Unclear information is Uncomprehended Element — a different Trap.
- [examples] Aggressive cutting is not only possible but invariably yields better, clearer communication.
- [related concepts] Hick's Law (1952): time to make a decision increases logarithmically with number of choices. The quantitative foundation for why less is more.
- [why it occurs] Adding detail feels safe; organizational stakeholders each advocate for visibility; interfaces accumulate content over time without audit.
- [governing question] Not "could there be less?" but "does the user need all of this right now?"
- [AI detectability] Tier 2: element count, word count, and option density measurable but whether specific information is necessary requires user goal knowledge.

## Related Traps
- **Gratuitous Redundancy** (sometimes root cause): Duplicate options contribute to Information Overload.
- **Distraction** (sometimes co-occurs): Excess information that captures attention is both — confirm which mechanism is primary.

## Report Language (U6)
**Finding:** [Screen/Section] presents substantially more information than users need to accomplish [primary goal] — [N elements / word count / option count] where [fewer] would suffice.
**Why it matters:** Every additional element the user must process beyond what their goal requires is a tax on attention and decision speed that compounds across every use.
**Confidence:** [Tier 2: Flagged — confirm information necessity against user task analysis]

## Remediation (U7)
Start from the user's most likely goal and include only what directly serves it. Apply progressive disclosure: surface secondary information only when needed. Write all text to the minimum length that preserves clarity — aggressive cutting almost always yields better communication. For navigation and option structures, minimize choices to increase decision speed. Audit regularly — interfaces accumulate content over time, and what was reasonable at launch may be overwhelming as the product grows.

## AI Detection Rules
**`testable: true` — Always evaluable from a static screenshot.** ⚠️ DO NOT UNDER-FLAG.
**Flag as CRITICAL when:**
- Page is predominantly text (>70% of visible content is dense text paragraphs)
- The primary user task/action is buried within or below large blocks of text
- User must read substantial content to find how to accomplish their task
- Call-to-action or key functionality is not visible without scrolling past text walls
**Flag as MODERATE when:**
- Page has substantial text but key actions are somewhat visible
- Important information requires parsing through multiple paragraphs
- Visual hierarchy exists but doesn't adequately prioritize task completion
**Output to `potential_issues` ONLY when:**
- Content density MIGHT be legally required (terms, disclaimers, compliance)
- The audience is known to need detailed information (e.g., technical documentation)
**DO NOT use `potential_issues`** if the task is clearly obscured by excessive text — that is a confirmed finding.
**vs. UNCOMPREHENDED ELEMENT:** Opposite conditions. Information Overload = volume makes it hard to find or act. Uncomprehended Element = content present is insufficient to understand or act confidently. Never apply one while acknowledging the other describes the situation better.

---

# CHUNK: SYSTEM AMNESIA

**chunk_id:** trap_system_amnesia_v2
**tenet:** Efficient
**severity_combination_rule:** High when consequence is task failure or worse, regardless of likelihood.

## Definition (verbatim)
The system fails to take advantage of the user's prior work, preferences, or context.

Arises when a system forgets what the user has done in the past and either makes the user do the same work twice, or presents content/information/suggestions in ways that show it has not been paying attention. The system was previously exposed to the information it needed — either failed to collect it or collected it but did not use it.

## DISCONFIRMATION — Apply First
NOT present when:
(a) Re-prompting serves a legitimate security or verification purpose deliberately designed — though even in these cases, confirmation of prior entries with option to update is superior to requiring re-entry of everything.
(b) The system genuinely does not have access to prior information due to architectural constraints — though teams should examine whether this is actual or assumed.
(c) Prior information may have changed since provided, making re-prompting appropriate — though again, confirmation of prior entries with option to update is superior.

## Severity
**Part A — Consequence:** Friction and frustration in most cases. Significant when re-prompting forces users to recreate substantial prior work. The cumulative effect of a system that never remembers is a product that feels progressively less intelligent over time — users may regard it as forgetful or not paying attention.
**Part B — Likelihood:** High when: system demonstrably has the information (showing it on screen while asking about it — Xbox Halo example); interface asks something about an action a user just took in a way showing it has no memory; re-prompt occurs in same session as original provision; information is high-effort to re-supply. Low when: re-prompting is for legitimate verification with disclosed rationale.
**Combination rule:** High severity when consequence is task failure or worse, regardless of likelihood.

## Confidence Tiers
- **Tier 1:** System displays information it possesses while simultaneously requesting it, or makes statements showing it neglected to note prior user behavior — visible in a single screen.
- **Tier 2:** Re-prompting for previously provided information identifiable in design flows, but confirming the system has the data requires knowledge of data architecture.

## Root Cause Confirmation (U4)
- **Bad Prediction** (downstream effect): Confirm independently that predictions are poor AND that prior context data is available but unused. Do not infer System Amnesia from bad predictions alone.
- **Memory Challenge** (distinction): System Amnesia = system had the opportunity to collect or note user data but did not, or collected it but did not use it. Memory Challenge = user is required to remember information that is easy to forget. Both can co-occur.

## Examples → Rules
- **[Example 16.1] Xbox website recommending owned game:** "Sell" page prominently featured Halo to a user whose profile clearly showed they already owned it. → *Rule: When a system displays information it possesses while simultaneously presenting content that ignores that information, this is Tier 1 confirmation — no user testing needed.*
- **[Example 16.2] Alexa Mobile App re-asking criteria:** Made users re-state criteria they had already provided in the same session. → *Rule: Information provided earlier in the same session must be available throughout the session. Re-prompting within a single session is one of the strongest signals of this Trap.*
- **[Example 16.3] Vending machine credit card question:** Asked users if they knew it accepted credit cards while processing a purchase just made with a credit card. → *Rule: When a system's current action demonstrates it already has information, prompting for that information is a Tier 1 instance. The evidence of the Trap is present on the same screen.*
- **[Example 16.4] Workday address re-entry:** Required re-entering address in subsequent modules despite having been entered in earlier ones. → *Rule: User data provided in one module of a product should be available across all modules of the same product. Siloed data architecture is not a user's problem — it is a design failure.*
- **[Example 16.5] Medical form re-entry of info:** Patients are often asked to enter the same information into both paper and digital medical forms prior to every healthcare visit, even when this information was previously captured. → *Rule: While it is important to ensure certain kinds of information, like medical history, is up-to-date, more efficient solutions only require users to edit or confirm previously entered data, rather than re-enter it.*


## Rules (consolidated)
- [definition] Two forms: (1) actively re-prompting for information already provided; (2) passively failing to use prior work, preferences, or context.
- [definition] "Prior work" includes information user directly provided AND information system gathered from user behavior (purchases, preferences, activity).
- [examples] The cumulative effect of a system that never remembers is a product that feels progressively less intelligent over time.
- [why it occurs] Siloed data architecture; deliberate choices to re-prompt for verification applied more broadly than necessary; context loss between conversational AI sessions accepted as given when user-facing cost is not fully accounted for.
- [AI detectability] Tier 1 when system displays possessed information while simultaneously requesting it. Tier 2 otherwise — requires knowledge of underlying data architecture.

## Related Traps
- **Memory Challenge** (distinguish): System Amnesia = system design failure; Memory Challenge = design demand on user. Both may co-occur — cite System Amnesia as root cause when system had the data.
- **Bad Prediction** (downstream): System Amnesia is a common root cause of persistent Bad Prediction. Confirm independently.
- **Unwanted Disclosure** (see also): Avoiding System Amnesia means retaining user data. Every effort must be made to keep that data secure — failure exposes user to Unwanted Disclosure.

## Report Language (U6)
**Finding:** [Screen/Flow] requests [information] that the system already has — either from earlier in this session or from prior user interactions — or displays information showing it has not kept track of the user's prior behavior or stated preferences.
**Why it matters:** Being asked to provide information the system already has, or encountering a system that ignores prior behavior, creates friction and signals that the system does not know the user — directly undermining the value of any personalization or context-awareness the system claims to offer.
**Confidence:** [Tier 1: Confirmed when system displays possessed information while simultaneously requesting it / Tier 2: Flagged — confirm data availability with architecture review]

## Remediation (U7)
Design for retention by default: when a user provides information at any point in a flow, it should be available at all subsequent points in the same session. Ensure user data is shared across product contexts rather than siloed. For recommendation systems, build logic that excludes content the user already owns or has engaged with. The governing question: could the system reasonably be expected to retain this? If yes, it should.

## AI Detection Rules
**Tier 1 — Confirmed finding, moderate severity:** When the artifact shows the system displaying information it demonstrably possesses while simultaneously requesting it or acting contrary to it — visible on a single screen. Examples: recommending a product the user's profile shows they already own; asking for information already shown elsewhere on the same screen; prompting for a preference the interface shows has already been set.
**`testable: false`:** Re-prompting across screens requiring knowledge of prior-session data.

---

# TRAP CHUNKS — ACCURATE TENET

---

# CHUNK: INCORRECT INFORMATION

**chunk_id:** trap_incorrect_information_v2
**tenet:** Accurate
**severity_combination_rule:** High when consequence is task failure or worse, regardless of likelihood.

## Definition (verbatim)
Information presented to the user is factually wrong, distorted, incomplete, out-of-date, or contains errors.

**⚠️ SCOPE — read before classifying anything as this trap:**
This trap applies exclusively to static factual claims — content that is factually wrong independent of who the user is. The test is: **would this content be wrong for any user?** If yes, it may be Incorrect Information. If it is only wrong for this specific user (because the system chose to show the wrong thing), it is **BAD PREDICTION**, not Incorrect Information.

Personalization failures, recommendation errors, and surfaced content that is inappropriate for a specific user are BAD PREDICTION — the error is in the system's choice of what to show, not in the factual accuracy of the content itself.

Examples of Incorrect Information (static factual errors): a button labelled "Save" that actually deletes the item; a product description stating incorrect dimensions; a chatbot response citing a legal case that does not exist; a "Romantic Comedies" category that contains horror films.

Examples of BAD PREDICTION (wrong for this user, not wrong in fact): a homepage recommendation row showing thriller films to a user who stated they want children's content; a search default set to a category the user has never shown interest in; an auto-complete suggestion irrelevant to this user's task. The thriller films are correctly described — the error is that the system chose to show them to this user.

**Key characteristic:** Unlike most Traps, this one produces no friction. The user receives information, acts on it, and does not immediately realize it is wrong. This makes it particularly consequential — errors go undetected until consequences arrive. Note: bad recommendations DO produce friction (the user must scroll past irrelevant content); if friction is present, this is a signal you may be looking at Bad Prediction rather than Incorrect Information.

## DISCONFIRMATION — Apply First
NOT present when:
(a) Information is clearly attributed to a source and presented with appropriate uncertainty indicators — the Trap applies to information presented as fact.
(b) Information was accurate at the time and the interface provides a mechanism for keeping it current.
(c) The "incorrect" judgment reflects user preference disagreement rather than factual inaccuracy.
(d) The element is a recommendation, surfaced content row, suggestion, prediction, or system-generated default that is wrong for this specific user — that is BAD PREDICTION, not Incorrect Information. The fact that a recommendation engine made an error — even one you would describe as a "prediction error" — does not make it Incorrect Information. Wrong for this user ≠ factually incorrect.

**Key distinction from Bad Prediction — single disambiguation test:**

Ask: "Would this content be wrong for a user with completely different goals?"
- If **yes** (only wrong for this specific user) → **BAD PREDICTION**. The system chose to show the wrong thing to this user. The factual accuracy of the content does not matter.
- If **no** (factually wrong for any user, regardless of their goals) → **INCORRECT INFORMATION**. The error is in the content itself, not in who it was shown to.

## Severity
**Part A — Consequence:** Scales with stakes of the domain. Minor for low-stakes recommendations. Significant for financial, health, navigational, or legal information acted upon in good faith. Severe when incorrect information causes irreversible harm (hallucinated legal cases; sycophancy leading to confirmation bias).
**Part B — Likelihood:** High when: AI-generated factual assertions presented without attribution or uncertainty indicators; information is time-sensitive with no refresh mechanism; AI-authored content presented as authoritative fact without disclosure that it was generated.
**Combination rule:** High severity when consequence is task failure or worse, regardless of likelihood.

## Confidence Tiers
- **Tier 2:** Structural indicators — absence of attribution, AI-generated content without disclosure, staleness indicators, assertions contradicted within the interface (instructions directing users to a page that does not exist).
- **Tier 3:** Factual accuracy of specific claims — requires external verification; cannot be automated for general content.

## Root Cause Confirmation (U4)
- **Bad Prediction** (distinction): Apply the single disambiguation test above. If the content would be fine for a user with different goals, it is Bad Prediction (wrong for this user). If the content would be wrong for any user, it is Incorrect Information (wrong in fact).
- **Inviting Dead End** (downstream consequence): Incorrect information suggesting a wrong path forward is actually correct (mislabeled button, outdated instructions) functions as Inviting Dead End, but Incorrect Information is root cause. If a signifier is merely visually confusing but not factually wrong, it's only Inviting Dead End.

## Examples → Rules
- **[Example 17.1] ChatGPT hallucinated legal cases (2023):** Lawyer filed brief citing cases that did not exist; lawyer and firm sanctioned by FTC. → *Rule: AI-generated content presented as authoritative fact creates this Trap structurally, regardless of the specific content. The structural indicator — AI generation without disclosure — is sufficient to flag at Tier 2.*
- **[Example 17.2] Canada Airlines chatbot (AI):** Chatbot gave incorrect refund policy information; airline held liable. → *Rule: When AI-generated information about policies, procedures, or entitlements is incorrect and users act on it in good faith, both user harm and organizational liability result. Disclosure and human verification paths are required for high-stakes domains.*

## Rules (consolidated)
- [definition] Unlike most Traps, this one produces no user friction at the moment of encounter — making it especially dangerous in high-stakes domains.
- [examples] AI-generated content without attribution or uncertainty indicators is a structural Tier 2 indicator, regardless of whether the specific content is actually wrong.
- [why it occurs] Outdated data, AI probabilistic generation of factual claims, human error, intentional deception. Note: an algorithm surfacing content inappropriate for a specific user is Bad Prediction, not Incorrect Information — that is a relevance failure, not a factual accuracy failure.
- [how to avoid] For any information presented as fact: document the source, the verification process, and the mechanism for keeping it current. AI-generated content must be labeled and accompanied by source citations where possible.
- [governing principle] Design interfaces to surface uncertainty rather than hide it — confident presentation of uncertain information is a design failure, not a feature.
- [AI detectability] Tier 2 for structural indicators (no attribution, AI disclosure absent, internal contradictions). Tier 3 for factual accuracy of specific claims.

## Related Traps
- **Bad Prediction** (distinguish): Apply the single disambiguation test. Content wrong only for this specific user = Bad Prediction. Content factually wrong for any user = Incorrect Information. These are mutually exclusive — do not apply both to the same element.
- **Inviting Dead End** (downstream): Incorrect information pointing to wrong path makes Incorrect Information the root cause.

## Report Language (U6)
**Finding:** [Screen/Feature] presents [type of information] as fact that is verifiably incorrect or lacking [source attribution / uncertainty indicators / freshness mechanism] — in a domain where acting on incorrect information could cause [consequence].
**Why it matters:** Users have no reliable way to calibrate trust in an interface's outputs without external verification. The design obligation to be accurate is not merely a quality issue — in high-stakes domains it is an ethical and legal one.
**Confidence:** [Tier 2: Flagged for structural indicators / Tier 3: Factual accuracy requires external verification]

## Remediation (U7)
For any information presented as fact: document the source, the verification process, and the mechanism for keeping it current. AI-generated content should be explicitly labeled and accompanied by source citations where possible. High-stakes domains (health, finance, safety, legal) require the highest verification standard and the clearest disclosure of limitations. Design interfaces to surface uncertainty rather than hide it.

## AI Detection Rules
**The single disambiguation test (apply BEFORE classifying):** Ask — "Would this content be wrong for a user with completely different goals?"
- If YES (only wrong for THIS specific user) → **BAD PREDICTION**. Do not classify as Incorrect Information.
- If NO (factually wrong for any user regardless of goals) → **INCORRECT INFORMATION**.
**Tier 1 — Confirmed finding:** ONLY for static factual claims that are wrong independent of who the user is: UI labels or descriptions that contradict what the element actually does; ratings, metadata, or descriptions visibly inconsistent with the actual content shown; content filed under a category or label that factually does not describe it.
**Do NOT flag as INCORRECT INFORMATION:** Recommendation rows, surfaced content, personalisation results, or system-generated suggestions — those are always **BAD PREDICTION** when wrong for a specific user.

---

# CHUNK: BAD PREDICTION

**chunk_id:** trap_bad_prediction_v2
**tenet:** Accurate
**severity_combination_rule:** High when consequence is task failure or worse, regardless of likelihood.

## Definition (verbatim)
The system fails in its attempt to anticipate the user's intent, preference, or context; it guesses wrong.

Examples: auto-correct/auto-complete errors, proactive automation errors, irrelevant content recommendations, ill-timed voice assistant suggestions. The user understands what the system is suggesting or doing on their behalf but doesn't find it valuable.

**Key nuance:** A 10% error rate in autocomplete may be a net positive; the same rate in automated message sending is not. The question is whether the benefit of acting on imperfect prediction outweighs the cost of getting it wrong in this specific context.

## DISCONFIRMATION — Apply First
NOT present when:
(a) The prediction is correct — a feature that occasionally misfires but is a net positive is not this Trap unless the error cost exceeds the benefit.
(b) The predicted action is easily dismissed or goes away without disrupting the user AND without meaningful additional effort.

## Severity
**Part A — Consequence:** Minor inconvenience for dismissible suggestions or suggestions taking up space that could serve more relevant content. Embarrassment or social harm for wrong autocorrect in messages. Significant for automated irreversible actions (sent messages, completed purchases). Severe for safety-critical false activations (accidental 911 calls, recording without consent).
**Part B — Likelihood:** High when: predicted action is irreversible; system acts on ambiguous signals (passive sensor-based activation).
**Combination rule:** High severity when consequence is task failure or worse, regardless of likelihood.

## Confidence Tiers
- **Tier 1 (confirmed finding from static screenshot):** When user context is provided and the interface visibly surfaces content, sections, or defaults that are clearly wrong for the stated user — the prediction failure is directly observable from the artifact. Do not require usage data; flag as confirmed finding. Also applies to high-consequence irreversible predictive features (accidental send, privacy exposure) regardless of accuracy rate.
- **Tier 2:** Predictive features identifiable in design files where the specific predictions cannot be evaluated without usage data (no user context provided, or the mismatch is not visible in the artifact).

## Root Cause Confirmation (U4)
- **System Amnesia** (sometimes root cause): Confirm independently that user previously engaged in behavior or provided information that is unused. Do not infer System Amnesia from poor predictions alone.
- **Accidental Activation** (downstream effect): Confirm that the system probabilistically interpreted the user's action as intentional (Bad Prediction) rather than that the activation was purely physical — both require independent evidence.
- **Distraction** (downstream effect): Confirm that irrelevant proactive recommendation actually functions as Distraction. Do not infer from poor predictions alone.
- **Unwanted Disclosure** (downstream effect): Confirm that prediction error actually results in information being exposed undesirably. Do not infer from poor predictions alone.
- **Unnecessary Steps** (downstream effect): Confirm that wrong prediction actually results in user having to take additional steps. Do not infer from poor predictions alone.

## Examples → Rules
- **[Example 18.1] Smartphone autocorrect:** Incorrect substitutions range from irritating to embarrassing to insulting. → *Rule: The severity of individual wrong predictions varies enormously by the nature of the substitution — not just frequency. An error rate produces very different user experiences depending on what is being substituted. Evaluate error type, not just error rate.*
- **[Example 18.2] Apple iPhone proximity-sensor voice recorder (2016):** Feature automatically started voice recorder when proximity sensor detected phone near ear; prone to accidental activation when phone simply held at different angles; problem persisted as of 2026. → *Rule: When passive sensor-based activation triggers a recording function, the acceptable false-positive rate is near zero — any activation without clear intent is a severe instance due to privacy implications.*
- **[Example 18.3] Amazon humidifier recommendation spam:** Correctly predicting a purchase led to repeated, irrelevant humidifier recommendations — the model treated the purchase as indicating a collecting interest rather than a one-time need. → *Rule: Prediction models trained on behavioral patterns can get the inference logic wrong even when the underlying data is accurate. The symptom is recommendations that feel insulting or tone-deaf to the user.*
- **[Example 18.4] Hover cover in UI (Office, TV guides):** Hover-triggered content occludes the content the user was trying to read. → *Rule: Proactively surfaced content that covers the content users are actively attending to is a Bad Prediction — the system inferred the user wanted the surfaced content when they wanted to continue reading.*
- **[Example 18.5] Amazon Alexa "By the way" promotions:** Amazon’s Alexa voice assistant
began adding unsolicited "By the way..." messages after replies to promote other features. Users judged these messages to be irrelevant or ill-timed leading Amazon to reduce these prompts. → *Rule: Proactively surfaced content must not only be relevant but timely - and only presented to users when you can be certain they are open to suggestion.*

- **[Example 18.6] Content recommendation wrong for stated user (classification guidance):** An interface homepage prominently features content sections that contradict the stated user's goal or demographic. The content items are correctly labelled — the error is not in the accuracy of any item's description but in the system's decision to surface this content to this user. → *Rule: This is BAD PREDICTION, not INCORRECT INFORMATION. The system guessed wrong about what to show; the content itself is accurately described. The diagnostic question: would this content row be wrong for a user with different goals? If yes — it is only wrong for this specific user → BAD PREDICTION. If the content would be wrong for any user (factually inaccurate regardless of who views it) → INCORRECT INFORMATION. These two traps are mutually exclusive; do not apply both.*

## Rules (consolidated)
- [definition] The question is not whether prediction is perfect, but whether the benefit of acting on imperfect prediction outweighs the cost of getting it wrong in this context.
- [definition] Acting requires a higher accuracy threshold than suggesting. Where wrong-prediction consequence is significant and reversal is difficult, suggest rather than act.
- [definition] Safe rule: predict when certain, or only predict when negative consequences of a bad prediction are well understood and trivial.
- [examples] Passive sensor-based activations with privacy implications require near-zero false-positive rate.
- [why it occurs] Optimization pressures: systems trained to maximize engagement make predictions that produce clicks, not what serves user needs. Accurate prediction is genuinely hard — contextual factors determining user receptivity are myriad and constantly shifting.
- [AI detectability] Tier 1 for high-consequence irreversible predictive features. Tier 2 for others — whether specific predictions are wrong requires usage data.

## Related Traps
- **System Amnesia** (sometimes root cause): System failing to retain prior context will make progressively worse predictions.
- **Accidental Activation** (downstream): In voice and gesture interfaces, Bad Prediction is often the mechanism. Distinguish from physical Accidental Activation.
- **Distraction, Unwanted Disclosure, Unnecessary Steps** (downstream): All possible downstream effects — confirm each independently.
- **Incorrect Information** (distinguish): Apply the single disambiguation test. If the content would be fine for a user with different goals, it is Bad Prediction. If it would be factually wrong for any user, it is Incorrect Information. These are mutually exclusive — do not apply both to the same element.

## Report Language (U6)
**Finding:** [Predictive feature] is generated by the system but unwelcomed by the user — requiring users to work around the incorrect result rather than benefiting from the intended assistance.
**Why it matters:** A prediction that creates more effort to correct than it saves is a net negative — and wrong predictions in [irreversible/privacy-sensitive] contexts cause harm that cannot be undone.
**Confidence:** [Tier 1: Confirmed for high-consequence irreversible predictions / Tier 2: Flagged — confirm accuracy rate with usage data]

## Remediation (U7)
The governing question: is the benefit of acting on this imperfect prediction greater than the cost of getting it wrong? Where wrong-prediction consequence is significant and reversal is difficult, suggest rather than act — and make dismissal easy. Where prediction accuracy cannot be verified, default to inaction. Acting requires a higher accuracy threshold than suggesting. In other words: predict when certain.

## AI Detection Rules
**Actively check when user context is provided.**
**Tier 1 — Confirmed finding, moderate severity:** When the screenshot shows the interface surfacing content, recommendations, or defaults that are visibly wrong for the stated user — the system's proactive decision does not serve this user. Examples: curated/personalised sections surfacing items contradicting the described user's demographics, goals, or tasks; default settings visibly mismatching the stated user's context; a screen dominated by content clearly wrong for the stated user population.
**`testable: false`:** When content relevance cannot be assessed without off-screen personalisation state.
**BAD PREDICTION is directly detectable from a static screenshot** when the interface visibly surfaces wrong content for the stated user. Do not treat as generally undetectable.
**Disambiguation with INCORRECT INFORMATION:** See INCORRECT INFORMATION chunk. Recommendation rows and personalisation results are always BAD PREDICTION when wrong — never INCORRECT INFORMATION.

---

# TRAP CHUNKS — PROTECTIVE TENET

---

# CHUNK: IRREVERSIBLE ACTION

**chunk_id:** trap_irreversible_action_v2
**tenet:** Protective
**severity_combination_rule:** High when consequence is task failure or worse, regardless of likelihood.

## Definition (verbatim)
The system does not allow the user to undo or reverse an action they have taken.

Consequences range from frustrating to catastrophic: a purchase that cannot be cancelled, a message that cannot be recalled, a file that cannot be restored. This Trap applies when recovery is possible but not supported — not only when recovery is technically impossible.

## DISCONFIRMATION — Apply First
NOT present when:
(a) Irreversibility is genuine AND a non-habituating confirmation mechanism has been provided — e.g., typing a specific phrase rather than clicking a button, appropriate to the stakes. Standard confirmation dialogs alone do NOT resolve this Trap.
(b) The action's consequence is the intended, understood, and desired outcome — permanent deletion of a sensitive file where irreversibility is the point.
(c) A time-limited recovery window has been provided — Instagram's 30-day recovery window resolves this Trap.

**Critical note:** Confirmation dialogs are frequently dismissed without being read. They are not a reliable substitute for reversibility. Jef Raskin: complicating the confirmation (requiring a non-habituating response such as typing a specific word) is required for cases where irreversibility is genuine.

## Severity
**Part A — Consequence:** Scales directly with stakes: minor inconvenience for low-value irreversible action; significant for consequential purchase or data deletion; severe for actions with irreversible real-world consequences (flight purchase, legal submission, safety action).
**Part B — Likelihood:** High when: action reachable in fewer steps than expected; a misleading label understates commitment level (Reserve = Purchase); user is under time pressure. Low when: path to the irreversible action is clearly marked and deliberate.
**Combination rule:** High severity when consequence is task failure or worse, regardless of likelihood.

## Confidence Tiers
- **Tier 2:** Actions lacking visible undo mechanisms are identifiable in design files but whether a specific action could technically be made reversible requires architecture knowledge.

## Root Cause Confirmation (U4)
- **Inviting Dead End** (sometimes contributing cause): Confirm independently that a misleading element led the user to the irreversible action. An irreversible action reached via the correct path is this Trap only; one reached via a misleading element is both, with Inviting Dead End as root cause.
- **Data Loss** (often co-occurs): Confirm independently that the irreversible action causes data to be permanently lost — both Traps may be present simultaneously.

## Examples → Rules
- **[Example 19.1] Concur iOS Reserve = Purchase:** "Reserve" button executed purchase with no ability to undo; label-consequence mismatch combined with irreversibility. → *Rule: When a label communicates a lower-commitment action than what the system actually executes, and that action cannot be undone, two Traps are simultaneously present: Inviting Dead End (the label misled) and Irreversible Action (the result cannot be undone). The combination is maximally damaging.*
- **[Example 19.2] Instagram post deletion (then 30-day recovery):** No undo for deleted posts; later introduced 30-day recovery window. → *Rule: The recovery path had always been technically feasible — it simply had not been designed. "Cannot be undone" is almost always a design choice, not a technical necessity.*
- **[Example 19.3] Alexa shopping list no-delete:** Users could not delete the last item added when Alexa misheard. → *Rule: In voice interfaces where commands can be misinterpreted, the ability to undo the most recent action is critical. Voice Accidental Activation and Irreversible Action are particularly damaging in combination.*
- **[Example 19.4] Systems asking "did you want to include an attachment?":** Proactive error prevention targeting the irreversible action of sending an email. → *Rule: Proactive error prevention (surfacing probable errors before the irreversible action executes) is preferable to irreversible action plus remediation. But it must be accurate — false positives create Bad Prediction.*

## Rules (consolidated)
- [definition] This Trap applies when recovery is possible but not supported — not only when technically impossible.
- [definition] Confirmation dialogs as substitute for reversibility are unreliable — users habituate and dismiss without reading.
- [examples] "Cannot be undone" is almost always a design choice, not a technical necessity.
- [examples] The label-consequence mismatch (Reserve = Purchase) combined with irreversibility is the most damaging combination of this Trap with Inviting Dead End.
- [how to avoid] Design forwards AND backwards. For every action, ask: what does the user do if they change their mind?
- [AI detectability] Tier 2: actions lacking visible undo mechanisms identifiable in design files. Whether technically reversible requires architecture knowledge.

## Related Traps
- **Data Loss** (often co-occurs): When irreversible action causes permanent data loss, both Traps are present.
- **Unnecessary Steps** (downstream): Confirmation dialogs added as substitute for reversibility create Unnecessary Steps.
- **Inviting Dead End** (sometimes co-occurs as root cause): When misleading label draws user to irreversible action, Inviting Dead End is root cause.

## Report Language (U6)
**Finding:** [Action] cannot be undone, and no recovery mechanism (undo, time-limited reversal, or non-habituating confirmation) is provided.
**Why it matters:** Users who take this action unintentionally or under misapprehension have no path to recovery — the cost of the error is permanent.
**Confidence:** [Tier 2: Flagged — confirm reversibility feasibility with technical review]

## Remediation (U7)
Design forwards and backwards: for every consequential action, ask what the user does if they change their mind. Making an action reversible is almost always better than asking for confirmation — it removes both the risk and the step. Where true irreversibility exists, provide a time-limited recovery window if technically feasible. Where neither is possible, use a non-habituating confirmation (type a specific phrase) rather than a standard dialog. Confirmation dialogs are frequently dismissed without being read — they are not a reliable substitute for reversibility.

## AI Detection Rules
**Tier 2 — Output to `potential_issues`, confidence "medium":** When a consequential action (delete, send, purchase, submit, publish) is visible with no visible undo mechanism, cancel option, time-limited recovery window, or non-habituating confirmation. Flag: "This action appears to have no recovery path — confirm whether reversal is technically feasible."
**Important:** Standard OK/Cancel dialogs alone do NOT resolve this Trap — flag even when present if the action is consequential.
**`testable: false`:** Assessing whether an action could technically be made reversible.

---

# CHUNK: UNWANTED DISCLOSURE

**chunk_id:** trap_unwanted_disclosure_v2
**tenet:** Protective
**severity_combination_rule:** High when consequence is task failure or worse, regardless of likelihood.

## Definition (verbatim)
The system exposes personal data or behavior in a way that is harmful, embarrassing, or unexpected.

Broader than it first appears: includes digital data shared without consent AND physical disclosure — devices reading notifications aloud in crowded rooms, voice assistants responding audibly in quiet offices, screens displaying sensitive information in public places.

## DISCONFIRMATION — Apply First
NOT present when:
(a) The user explicitly consented with full understanding of what would be shared, when, and with whom.
(b) The disclosure is to the user themselves in a private context — confirming a purchase to the buyer on their personal device is not this Trap.
(c) Data is aggregated and anonymized such that no individual's behavior is identifiable.

## Severity
**Part A — Consequence:** Ranges from minor embarrassment (revealed gift surprise) to significant social harm (disclosed sensitive behavior) to legal liability (class action, regulatory action — Facebook Beacon). Privacy violations involving sensitive categories (health, location, financial behavior) are inherently high-consequence.
**Part B — Likelihood:** High when: sharing is opt-out rather than opt-in; interface is used on shared or ambient devices; notifications surface sensitive content in social contexts. Low when: explicit opt-in consent was obtained and sharing context is private and expected.
**Combination rule:** High severity when consequence is task failure or worse, regardless of likelihood.

## Confidence Tiers
- **Tier 1:** Opt-out sharing of sensitive behavioral data — default setting is detectable and risk is high enough to flag without further confirmation.
- **Tier 2:** Data sharing features and default settings identifiable in design files. Whether specific disclosure would be unwanted requires knowledge of social and physical contexts of use.

## Root Cause Confirmation (U4)
- **Feedback Failure** (often co-occurs): Confirm independently that the system fails to notify users that sharing is occurring. A disclosed but unwanted sharing has this Trap without Feedback Failure; an undisclosed sharing has both.
- **Bad Prediction** (sometimes co-occurs): Confirm independently that a misjudgment of context caused the unwanted disclosure. Not all unwanted disclosures involve a prediction error.

## Examples → Rules
- **[Example 20.1] Facebook Beacon:** Shared users' partner-site purchase activities on news feed on opt-out basis; revealed gift surprises; class action lawsuit; shut down. → *Rule: Opt-out sharing defaults create this Trap for all users who do not notice or understand the opt-out. Default settings should reflect what users would choose if fully informed — not what maximizes data sharing. Retrospective confirmation: shutdown in response to user backlash and legal action confirms Trap at scale.*
- **[Example 20.2] Amazon Echo Show purchase/shipping notifications:** Visible to household visitors; customers reported purchasing elsewhere to avoid revealed gift surprises. → *Rule: Data collected in one context (private purchase history) that surfaces in a different context (ambient display in shared home) creates this Trap. The disclosure context determines whether sharing is unwanted, not whether the data itself is "private."*
- **[Example 20.3] Mobile apps with high-precision location tracking:** Many current apps collect data allowing precision location tracking without user awareness. → *Rule: Data collection that enables tracking without explicit user awareness constitutes this Trap structurally — the Trap exists before any specific disclosure occurs.*
- **[Example 20.4] Venmo public-by default sharing of transactions:** Venmo removed its global feed that made users' payments visible to strangers worldwide. However, transactions remain public by default, with anyone able to view them by visiting a user's profile. → *Rule: Data collection that enables tracking without explicit user awareness constitutes this Trap structurally — the Trap exists before any specific disclosure occurs.*
- **[Example 20.5] Zoom saves private chats when it saves meetings:** As of 2026, when a user saves Zoom meeting chats locally, it saves chats sent to everyone in the meeting, as well as the users' private messages. Users who copy-paste the entire chat log into emails or shared documents may inadvertently expose private conversations to everyone with access. → *Rule: Data collection that enables exposure of communications assumed to be constitutes this Trap structurally.*


## Rules (consolidated)
- [definition] "Public" includes any audience the user did not intend — not only the general public. Sharing with friends, household members, or third-party advertisers without user intent all qualify.
- [definition] Physical dimension: devices that surface private information through sound or screen in social contexts are included.
- [examples] Contextual integrity (Nissenbaum): the question is not "is this data private?" but "does this flow match what the user would expect given the context in which they shared it?"
- [examples] Privacy by Design (Cavoukian): privacy should be the default, not an opt-in. Default settings should reflect user interests, not system interests.
- [why it occurs] Two sources: (1) oversight — designers don't fully consider cross-context surfacing; (2) intention — systems designed to serve business goals over user interests.
- [AI detectability] Tier 1 for opt-out sharing of sensitive behavioral data. Tier 2 for contextual evaluation. Tier 3 for physical dimension — requires knowledge of real-world use contexts.

## Related Traps
- **Feedback Failure** (often co-occurs): Undisclosed sharing — system acts without notifying user.
- **Bad Prediction** (sometimes co-occurs): Context misjudgment causing disclosure.
- **System Amnesia** (see also): Avoiding System Amnesia requires retaining user data; failing to secure that data creates Unwanted Disclosure risk.

## Report Language (U6)
**Finding:** [Feature/setting] shares [data type] with [audience] on an opt-out basis — or in a context where users are unlikely to expect or intend the disclosure.
**Why it matters:** Users have no way to prevent disclosures they are not aware of — and consequences range from personal embarrassment to legal liability.
**Confidence:** [Tier 1: Confirmed for opt-out sharing of sensitive behavioral data / Tier 2: Flagged — confirm disclosure context and user expectations]

## Remediation (U7)
Default settings should reflect what users would choose if fully informed — not what maximizes data collection. For any data sharing feature, ask: where could this data surface, and would the user expect and accept that? Require explicit opt-in for sensitive behavioral data. For ambient and shared devices, provide granular control over what content is displayed and when.

## AI Detection Rules
**Tier 1 — Confirmed finding, high severity:** When the artifact shows opt-out sharing of sensitive behavioral data as the default setting.
**Tier 2 — Output to `potential_issues`, confidence "medium":** When the artifact shows data sharing features, notification defaults, or ambient display settings where social or physical context could make disclosure unwanted.
**`testable: false`:** Contextual evaluation of whether specific disclosures would be unwanted for this specific user.

---

# CHUNK: DATA LOSS

**chunk_id:** trap_data_loss_v2
**tenet:** Protective
**severity_combination_rule:** High when consequence is task failure or worse, regardless of likelihood.

## Definition (verbatim)
The system fails to retain information or content the user expects to be preserved.

Occurs when a user unintentionally loses work through action or inaction. Causes: unexpected system/app shutdowns without auto-saving, forms that don't preserve partial entries, data entry conflicts during co-authoring.

The convention of requiring explicit saving is a historical artifact — not a user requirement.

## DISCONFIRMATION — Apply First
NOT present when:
(a) Continuous auto-save is functioning and data is preserved automatically without user action.
(b) Data is explicitly ephemeral and users are clearly informed before creating it.
(c) The user explicitly and knowingly chose to discard the data — this Trap covers unintentional or inaction-triggered loss only.

**Key distinction from System Amnesia:** Data Loss = system fails to retain data the user expected to be preserved. System Amnesia = system fails to use data the user previously provided regardless of whether the system still has access to it. Different causes, different fixes.

## Severity
**Part A — Consequence:** Scales with value of lost data and effort to recreate. Minor for easily re-created inputs. Significant for substantial creative work, complex form completions, or data that cannot be recreated. Severe when data loss is permanent and data has high personal or professional value.
**Part B — Likelihood:** High when: explicit saving is required and failure modes (crashes, timeouts, navigation away) are foreseeable. Low when: auto-save is active and recovery mechanisms exist.
**Combination rule:** High severity when consequence is task failure or worse, regardless of likelihood.

## Confidence Tiers
- **Tier 2:** Absence of auto-save is detectable in design documentation. Testing for actual data loss under failure conditions requires active simulation.

## Root Cause Confirmation (U4)
- **Irreversible Action** (often co-occurs): Confirm independently that the data-losing action cannot be undone. Accidental navigation away from an unsaved form is Data Loss from system design; deliberate deletion without undo is both. Making the action reversible typically resolves both.
- **System Amnesia** (distinguish): Data Loss = system fails to retain expected data. System Amnesia = system fails to use data it still has. Different causes, different fixes.

## Examples → Rules
- **[Example 21.1] Pre-cloud document editing (Windows unexpected shutdown):** Unsaved work lost on unexpected shutdown. → *Rule: When explicit saving is required and unexpected events can prevent saving, Data Loss is an inherent property of the design. The question is not "how do we warn users to save?" but "how do we eliminate the need to save at all?"*
- **[Example 21.2] Google Docs co-authoring overwrites:** Concurrent users can overwrite each other's data. → *Rule: Collaborative editing systems must implement conflict resolution that protects all users' contributions rather than defaulting to last-write-wins.*
- **[Example 21.3] Figma comments (click twice outside and gone):** Comment input lost on accidental click outside. → *Rule: Partial state — including partially written user input — must be preserved against accidental dismissal. Any action that discards partial input without confirmation is a candidate for this Trap.*
- **[Example 21.4] Zoom meeting chat logs:** Chat logs not preserved after meeting ends without deliberate export. → *Rule: When users create content in an ephemeral context, the system must either preserve it automatically or clearly communicate its ephemeral nature before users invest effort.*

## Rules (consolidated)
- [definition] This Trap applies regardless of frequency — the Trap exists whenever the risk of data loss exists, even if rarely triggered.
- [definition] The convention of explicit saving is an engineering legacy, not a user requirement. Continuous auto-save is the standard mitigation.
- [examples] Session timeouts, network interruptions, and crashes are certainties, not edge cases. Design for failure from the outset.
- [how to avoid] Auto-save wherever technically feasible. Design for failure from the outset: simulate unexpected shutdowns, timeouts, network interruptions.
- [how to avoid] When deliberate permanent deletion is the goal, complicate the confirmation (Raskin) — require typing a specific word to avoid habituated dismissal.
- [AI detectability] Tier 2: absence of auto-save detectable in design documentation. Actual failure-mode testing requires active simulation.

## Related Traps
- **Irreversible Action** (often co-occurs): When data-losing action cannot be undone, both Traps are present. Making action reversible typically resolves both.
- **System Amnesia** (distinguish): Different causes — confirm which is present.
- **Unnecessary Steps** (see also): Requiring users to explicitly save their work adds a step that continuous automatic saving can eliminate.

## Report Language (U6)
**Finding:** User-generated content in [screen/flow] can be permanently lost if [failure mode — session timeout / crash / unintentional navigation / collaborative authoring conflict] occurs before explicit saving, and no auto-save or recovery mechanism is in place.
**Why it matters:** Data loss is experienced as a fundamental system failure — it destroys trust and requires users to repeat work they have already done.
**Confidence:** [Tier 2: Flagged — confirm auto-save status and failure mode coverage with technical review]

## Remediation (U7)
Implement continuous auto-save wherever technically feasible — the requirement for explicit saving is an engineering legacy, not a user requirement. Design for failure from the outset: session timeouts, network interruptions, and crashes are certainties, not edge cases. For collaborative tools, implement conflict resolution that protects all users' contributions. The governing question: what happens to the user's work if the session ends unexpectedly right now?

## AI Detection Rules
**Tier 2 — Output to `potential_issues`, confidence "medium":** When the artifact shows user-generated content (form fields, text input, creative work, multi-step data entry) with no visible auto-save indicator AND no explicit save mechanism AND context where failure modes are foreseeable (session timeout, navigation away, crash). Flag: "User-generated content in this flow may be lost if [failure mode] occurs — confirm whether auto-save is implemented."
**`testable: false`:** Confirming actual data loss — requires live testing.

---

# TRAP CHUNKS — HABITUATING TENET

---

# CHUNK: GRATUITOUS REDUNDANCY

**chunk_id:** trap_gratuitous_redundancy_v2
**tenet:** Habituating | **sub-tenet:** Non-Redundant
**severity_combination_rule:** High when consequence is task failure or worse, regardless of likelihood.

## Definition (verbatim)
Multiple instances of the same interface element are presented to the user at the same time.

The test is: same destination or same function. Visual form is irrelevant — a search field and a search icon that both invoke search are redundant even though they look different. Whether a duplicate "adds value," "serves a structural purpose," or "feels justified" is irrelevant to detection. If two elements on the same screen reach the same destination or invoke the same function, this Trap is present.

## DISCONFIRMATION — Apply First
NOT present only when ONE of these clearly applies:
(a) **Flexible syntax:** The two paths approach the same goal from structurally opposite starting points — one starting from an object (select a file, then choose "Delete"), the other from an action (choose "Delete," then select a file). This is the object→action / action→object distinction that serves genuinely different user mental models. This exception does NOT apply when two elements simply invoke the same function from the same direction in different visual forms. A search field and a standalone search icon are both approached action-first (go to search) — they are redundant, not flexible syntax.
(b) **Different hierarchy levels:** The two paths exist at genuinely different depth levels of the product — e.g., the same destination linked from the site home page and again from deep within a section three levels down. This does NOT apply to elements on the same screen. A global nav bar and a contextual sub-nav bar are both visible on the same screen; elements in both are redundant if they serve the same function or reach the same destination.
(c) **Different destinations:** What appears to be the same function actually reaches genuinely different destinations.

**Element identification:** Before comparing destinations, determine whether two items are one element or two. A form field and its directly adjacent submit control (a search box with a Search button immediately beside it) are one element — users interact with them as a unit. Elements at separate locations on the screen — even if they invoke similar functions — are separate elements. Two controls in different interface regions that each independently trigger search are two separate elements.

**Forced Syntax distinction:** These are mutually exclusive. Forced Syntax: only one path exists to complete the task. Gratuitous Redundancy: two or more paths to the same destination co-exist.

## Severity
**Part A — Consequence:** Slowed habituation is the primary cost. Also generates downstream Traps (Invisible Elements displaced off screen, Unnecessary Steps from scrolling, Information Overload from option proliferation). Compounding effects make cumulative severity higher than any individual instance suggests.
**Part B — Likelihood:** High when: different teams designed different sections independently; discoverability concerns addressed by adding paths rather than improving visibility of existing ones; interface has grown over time without redundancy audit.
**Combination rule:** High severity when consequence is task failure or worse, regardless of likelihood.

## Confidence Tiers
- **Tier 1:** Multiple elements visually appearing to reach the same destination or invoke the same function — detectable from the screen. Note: from a screenshot alone, destination identity is inferred, not confirmed. Flag as Tier 1 suspected when visual evidence is strong; note that destination confirmation requires code inspection or live testing.

## Root Cause Confirmation (U4)
- **Downstream Traps** (Invisible Element, Unnecessary Steps, Information Overload): Confirm each independently before attributing to Gratuitous Redundancy. Content displaced off screen, scrolling required, and excess option count each require their own evidence. Gratuitous Redundancy is more often a contributor to these Traps than sole cause.

## Examples → Rules
- **[Example 22.1] Healthcare.gov three (then four) duplicate links (2014):** Three links on homepage all went to same destination; added a fourth, exacerbating the issue. → *Rule: Adding more duplicates to address discoverability problems worsens the Trap. The correct response to poor discoverability is to improve the visibility of the existing element, not add copies.*
- **[Example 22.2] Swedish medical site 30+ duplicated links:** As of 2020, "find a location" link appeared 6 times on home screen; 30+ duplicate links total. → *Rule: In large organizational products built incrementally by different teams, Gratuitous Redundancy accumulates over time without anyone intending it. Periodic systematic audit is required.*
## Rules (consolidated)
- [definition] Gratuitous Redundancy is different from flexible syntax. The distinction is purpose: paths serving genuinely different mental models or interaction approaches are useful; paths that reach the same destination serving the same mental model are this Trap — regardless of visual form.
- [definition] Same destination is the test, not same appearance. Elements that look different but invoke the same function or navigate to the same place are still this Trap.
- [definition] Power Law of Practice: when users can reach a destination by multiple routes, practice is divided across routes rather than concentrated. Curve toward automaticity flattens. Mastery takes longer.
- [related concepts] Hick's Law: more choices adds decision time at every encounter. Gratuitous Redundancy increases choices without adding destinations.
- [related concepts] Raskin's "monotony": one way to do things. Not dogmatic but directionally correct — resist the instinct toward variety at the cost of habit formation.
- [detection] Audit the code for duplicate destination links — the most reliable detection method. This Trap rarely surfaces in standard usability testing (which walks intended paths).
- [AI detectability] Tier 1: structural analysis — multiple links to same destination, same control in multiple locations. Determining whether redundant paths serve different mental models requires user understanding.

## Related Traps
- **Invisible Element, Unnecessary Steps, Information Overload** (downstream): Often caused by Gratuitous Redundancy displacing other content. Confirm each independently.
- **Forced Syntax** (distinguish): Mutually exclusive — see Disconfirmation above.

## Report Language (U6)
**Finding:** [N] separate elements on [screen/level] appear to reach the same destination — [destination]. The duplicates add decision overhead without adding functionality.
**Why it matters:** Duplicate paths multiply the choices users must evaluate without multiplying destinations, slowing both decision-making and the development of automatic navigation habits.
**Confidence:** [Tier 1: Suspected — visual evidence of duplicate destinations is strong; confirm destination identity via code inspection or live testing]

## Remediation (U7)
Consolidate to one path per destination for a given grammatical construction. Audit the code for duplicate destination links — the most reliable detection method. When the motivation for adding a duplicate was poor discoverability of the original, fix the visibility of the original element rather than adding a copy. Caution: do not confuse Gratuitous Redundancy with useful flexible syntax — supporting both object→action and action→object constructions is valuable and should be preserved.

## AI Detection Rules
**⚠️ DO NOT UNDER-FLAG. Directly detectable from a static screenshot — check on every analysis.**
**Mandatory whole-interface scan (before trap-by-trap analysis):** Scan the entire interface and catalog every text string, label, icon, and interactive control that appears more than once anywhere on the same screen — regardless of which navigation bar, panel, or component each instance appears in. Do NOT filter based on visual proximity or component hierarchy.
**Tier 1 — Confirmed finding, moderate severity:** Same text label, icon, control, or navigation destination appearing in 2+ locations simultaneously on the same screen with no independent informational distinction. Raise severity to high if redundancy displaces other content or creates measurable Unnecessary Steps or Information Overload.
**Tier 2 — Output to `potential_issues`, confidence "medium":** Two visually different elements that could plausibly invoke the same function from the same direction and are independently operable.
**Directed inspection (output to `potential_issues`, confidence "low"):** Identical elements observed but functions unverifiable. State: "Cannot confirm from this artifact whether [element A] and [element B] trigger the same function — analyst must test each. If same function → Gratuitous Redundancy. If different functions → Variable Outcome."
**DO NOT DISMISS as "standard patterns" — these are Tier 1 confirmed:**
- Site logo navigating to homepage AND a separate "Home" nav link
- Same navigation destination in two or more separate nav regions on the same screen
- A search input field AND a standalone search icon/button both visible on the same screen
- Multiple "Sign In" or "Get Started" buttons for the same action
**The flexible-syntax exception is NARROW:** Only disconfirmed when one path is strictly object→action AND the other is strictly action→object. Visual difference, size difference, or placement in different components does NOT create an exception.
**vs. AMBIGUOUS HOME:** AMBIGUOUS HOME is about the product's global home destination; multiple competing entry points to a specific feature or task → GRATUITOUS REDUNDANCY.
**vs. FORCED SYNTAX:** Mutually exclusive per task flow — confirm which is present before flagging.

---

# CHUNK: VARIABLE OUTCOME

**chunk_id:** trap_variable_outcome_v2
**tenet:** Habituating | **sub-tenet:** Consistent with Expectations
**severity_combination_rule:** High when consequence is task failure or worse, regardless of likelihood.

## Definition (verbatim)
The system responds differently and unexpectedly to the same user action at different times.

Most often the result of a mode error. A mode is a system state causing the same user action to produce a different result depending on context. Also occurs without a formal mode when the same action produces different results that cannot be predicted from any clearly communicated rule.

## DISCONFIRMATION — Apply First
NOT present when:
(a) Different outcomes from the same action are clearly communicated by a mode indicator located within the user's attentional focus — a well-placed indicator makes different outcomes expected rather than surprising.
(b) The user sustains the mode by continuously acting on another control (quasi-mode: held Shift key, held sustain pedal) — Raskin's criterion for an acceptable mode, because the user cannot forget it.
(c) Variation is in degree rather than kind — a scroll that moves faster when flicked harder is not this Trap.
(d) The context shift producing the different outcome is itself an explicit, user-initiated action the user would be attending to.

## Severity
**Part A — Consequence:** Ranges from minor confusion (unexpected Back button behavior) to catastrophic (Chrysler Monostable Gear Shifter — deaths, injuries, 1.1M vehicle recall). Severity scales directly with stakes of the unexpected outcome.
**Part B — Likelihood:** High when: mode indicator exists but placed away from user's attentional focus during mode-dependent action; mode is changed by system events rather than explicit user actions; same physical control has multiple functions across contexts.
**Combination rule:** High severity when consequence is task failure or worse, regardless of likelihood.

## Confidence Tiers
- **Tier 1 for detection:** State-handlers in code — where same user action routes to different outcomes — are directly detectable.
- **Tier 2 for confirmation as Trap:** Whether users will be unaware of the relevant system state requires user knowledge.

## Root Cause Confirmation (U4)
- **Invisible Element** (sometimes root cause): Confirm independently that no mode indicator exists. Do not infer Invisible Element from Variable Outcome alone — the absent indicator must be separately confirmed.
- **Effectively Invisible Element** (sometimes root cause): Confirm independently that a mode indicator exists AND is positioned outside the user's likely attentional focus during the mode-dependent action. Do not infer EIE from Variable Outcome alone — indicator must separately be confirmed to exist, be present in design, and be in a location users will not attend to.

## Examples → Rules
- **[Example 23.1] Twitter Back button:** Back button takes user back 2 steps instead of 1 after launching a dialog — unexpected because the dialog launch was a system-mediated state change. → *Rule: Navigation controls (Back, Home, Close) must produce consistent outcomes across all system states. These controls are invoked precisely for recovery and orientation — users depend on them being predictable exactly when they are uncertain.*
- **[Example 23.2] iPhone shake-to-undo (works in some apps, not others):** Same physical gesture produces different results depending on app context. → *Rule: Platform-level gestures and controls must behave consistently across all contexts in the platform ecosystem, not only within individual apps.*
- **[Example 23.3] Chrysler Monostable Gear Shifter (2016):** Same action (pushing up/down) leads to different gears depending on current state when user is attending to road rather than shifter; deaths, injuries, 1.1M vehicle recall. → *Rule: In safety-critical interfaces, the acceptable risk of mode error is zero. Redesign to eliminate mode dependency — not merely improve the indicator.*
- **[Example 23.4] CapsLock errors (universal):** Classic benign example. → *Rule: CapsLock works because the visual feedback (uppercase display on screen) is immediate and continuous — the mode indicator IS within user attention during the effect. Mode indicators must be visible at the moment of the mode-dependent action.*

## Rules (consolidated)
- [definition] The key question is not whether the same action produces different results, but whether the user is attending to the signal that explains the difference.
- [definition] Modes are acceptable when it is impossible for the user to forget which mode they are in (Raskin's criterion). Quasi-modes (sustained physical action) achieve this; true modes often do not.
- [detection] Most reliable technique: scrub the code for state-handlers. Any place where the same user action routes to different outcomes is a candidate.
- [examples] For safety-critical interfaces: acceptable risk of mode error is zero.
- [how to avoid] Prefer: eliminate the mode entirely. Second preference: quasi-mode. Third preference: mode indicator in user's attentional focus. Least preferred: mode indicator placed elsewhere.
- [AI detectability] Tier 1 for code-based state-handler detection. Tier 2 for confirming whether users will notice the mode indicator.

## Related Traps
- **Invisible Element** (sometimes root cause): Absent mode indicator.
- **Effectively Invisible Element** (sometimes root cause): Mode indicator present but misplaced.
- **Ambiguous Home** (see also): If home action doesn't reliably return user to home, Variable Outcome is also present.

## Report Language (U6)
**Finding:** [Action] produces different outcomes depending on [system state], but no indicator of that state is reliably within the user's attentional focus when the action is taken.
**Why it matters:** When the same action produces unexpected results, users cannot develop reliable habits — and in safety-critical contexts, the consequences of unexpected outcomes can be severe.
**Confidence:** [Tier 1: State-handler detected in code / Tier 2: Flagged — confirm whether mode indicator is within user's attentional focus]

## Remediation (U7)
Where possible, eliminate the mode entirely — consistent behavior is always better than a clearly indicated mode. When modes are unavoidable, place the mode indicator where the user is attending when they take the mode-dependent action — not where geometrically convenient. Evaluate mode clarity not by whether the indicator is provided, but by whether a user focused on their task will be attending to it. Alternatively, require continuous action to sustain the mode (quasi-mode), bringing it into user awareness. For safety-critical interfaces: the acceptable risk of mode error is zero — redesign to eliminate the mode dependency, not merely improve the indicator.

## AI Detection Rules
**Standard form:** Requires testing the same interaction across different modes/states/contexts — generally testable only with live testing or multi-screen flows showing evidence of variable behavior.
**Spatial case — `testable: true` when whole-interface scan finds identical-looking elements:** Flag for directed inspection. Instruct analyst to test each element. If functions differ → Variable Outcome. If functions are the same → Gratuitous Redundancy.
**Tier 2 — Multiple screens:** When evidence of variable behavior exists across provided screens, output to `potential_issues`, confidence "medium". Caveat: "Requires multiple task flows to confirm inconsistency."
**`testable: false`:** For temporal inconsistency without multi-state evidence.

---

# CHUNK: WANDERING ELEMENT

**chunk_id:** trap_wandering_element_v2
**tenet:** Habituating | **sub-tenet:** Consistent with Expectations
**severity_combination_rule:** High when consequence is task failure or worse, regardless of likelihood.

## Definition (verbatim)
The same interface element is presented in a different location at different times.

Inconsistent placement of controls, status indicators, content, etc. When the same control appears in different locations across an interface, users cannot repeat exactly the same action to reach it. Each encounter requires a small act of search and reorientation rather than automatic reach.

## DISCONFIRMATION — Apply First
NOT present when:
(a) Placement variation is appropriate to context — a Share button positioned differently in a reading view vs. a list view because the content relationship differs.
(b) The element is low-frequency and users would not be expected to develop spatial memory for it.
(c) The placement change is explicitly communicated through a design language transition users will attend to.

**Distinction from Inconsistent Appearance:** Wandering Element = inconsistent placement, same visual form. Inconsistent Appearance = inconsistent visual form, same or different placement. A control can wander without changing appearance and vice versa. Audit both independently.

## Severity
**Part A — Consequence:** Slowed habituation for the affected control — forces conscious search on every encounter rather than automatic reach. More severe for high-frequency, time-sensitive controls (navigation, edit, search) than for low-frequency ones.
**Part B — Likelihood:** High when: same control appears across multiple screens or contexts where users would reach for it automatically; product built by multiple teams designing independently. Low when: control is low-frequency or context-specific placement variation is meaningful.
**Combination rule:** High severity when consequence is task failure or worse, regardless of likelihood.

## Confidence Tiers
- **Tier 1:** Cross-context placement consistency directly auditable by comparing control coordinates across screens in design file. One of the more automatable Traps.

## Root Cause Confirmation (U4)
- **Effectively Invisible Element** (downstream effect): Confirm independently that the element's new position is outside the location users are likely to look for it. Do not infer invisibility from placement change alone — new position may be equally or more discoverable.
- **Inconsistent Appearance** (distinct, sometimes co-occurs): Audit both placement and visual form independently.

## Examples → Rules
- **[Example 24.1] iPhone Edit control inconsistency across apps:** Edit placed differently across native iOS apps; same for other functions. → *Rule: Platform-level controls must appear in consistent positions across all apps in the platform ecosystem. Inconsistency in native apps undermines platform-wide spatial habits.*
- **[Example 24.2] iOS 26.2 native apps (Messages, Mail, Calendar):** Search, filter, and new controls placed in different spots across these apps. → *Rule: When the same control category (search, filter, new) appears in different positions across related app contexts, users must consciously relocate it every time they switch contexts.*
- **[Example 24.3] Kindle re-flow:** Content re-flows in response to some interactions, potentially displacing elements users were reaching for. → *Rule: Content re-flow that displaces controls users were targeting creates this Trap dynamically within a single interaction sequence.*

## Rules (consolidated)
- [definition] Humans form spatial memories for frequently used objects automatically and without conscious effort. WANDERING ELEMENT defeats this capacity: every encounter requires conscious search.
- [related concepts] Spatial memory research (Scarr, Cockburn, Gutwin): when controls are reliably located, users stop consciously registering position and simply reach. This is one of the most powerful forms of automaticity available to designers — requiring nothing except consistency.
- [why it occurs] Different teams designing different parts independently; iterative redesign moving elements to optimize one context without considering other contexts; task-by-task evaluation that doesn't surface cross-context inconsistency.
- [detection] Cross-context placement audit: identify most frequent controls, map placement systematically across every context. Standard reviews and usability tests don't reveal this — they follow task flows.
- [AI detectability] Tier 1: systematic comparison of element placement across screens. Detectable from complete design files.

## Related Traps
- **Inconsistent Appearance** (distinguish and sometimes co-occurs): Audit placement and visual form independently.
- **Effectively Invisible Element** (downstream): If wandered element is now outside expected location, it may become effectively invisible in new position.

## Report Language (U6)
**Finding:** [Control] appears in different positions across [contexts] — users who have learned its location in one context will need to search for it in others.
**Why it matters:** When controls appear in different locations across contexts, users cannot develop automatic spatial memory for them — every encounter requires conscious search, undoing the efficiency that habituation is supposed to provide.
**Confidence:** [Tier 1: Confirmed — placement inconsistency is directly measurable across screens]

## Remediation (U7)
Identify controls appearing most frequently across the interface and map their placement systematically across every context. Inconsistencies are Wandering Elements. Pay particular attention to high-frequency controls — search, edit, navigation, confirmation — where spatial memory provides the greatest efficiency gain. Platform-level controls must appear in consistent positions across all apps in an ecosystem.

## AI Detection Rules
**Tier 1 — Confirmed finding, multiple screens only:** Cross-context placement consistency is directly auditable by comparing control positions across provided screens.
**`testable: false`:** For single screenshot analyses — omit from `traps_checked_not_found` for single-screenshot submissions; this is added automatically.

---

# CHUNK: INCONSISTENT APPEARANCE

**chunk_id:** trap_inconsistent_appearance_v2
**tenet:** Habituating | **sub-tenet:** Consistent with Expectations
**severity_combination_rule:** High when consequence is task failure or worse, regardless of likelihood.

## Definition (verbatim)
The same interface element is presented in a different style at different times.

Differing visual or auditory representation of the same icons, labels, controls, sounds, etc. Wandering Element describes controls that move; Inconsistent Appearance describes controls that change how they look or sound while staying in the same place.

## DISCONFIRMATION — Apply First
NOT present when:
(a) Visual variation across contexts is intentional and communicates meaningful distinction — a "save" action visually different in edit mode vs. view mode to signal the mode.
(b) The variation is between a legacy component and current components in a context where users recognize the legacy context as distinct.
(c) The element is low-frequency and users would not be expected to develop automatic visual recognition of it.

**Distinction from Wandering Element:** Inconsistent Appearance = same control, different visual form, same or different position. Wandering Element = same control, same visual form, different position. A control can be visually inconsistent while staying in the same position (this Trap only), or can move while maintaining consistent appearance (Wandering Element only). Audit both independently.

## Severity
**Part A — Consequence:** Slowed recognition and habituation — similar to Wandering Element. May temporarily produce an Uncomprehended Element when users encounter a familiar function in an unfamiliar visual form and must determine whether it is the same thing.
**Part B — Likelihood:** High when: same function represented by different icons in different contexts, or a word in some contexts and an icon in others; legacy components coexist with current design language; different teams applied a design system inconsistently. Low when: element is low-frequency or variation is intentionally meaningful.
**Combination rule:** High severity when consequence is task failure or worse, regardless of likelihood.

## Confidence Tiers
- **Tier 1:** Cross-context visual consistency directly auditable by comparing visual representation of recurring controls across screens. One of the more automatable Traps.

## Root Cause Confirmation (U4)
- **Wandering Element** (distinct, sometimes co-occurs): Audit placement and visual form independently. Both Traps may be present and both require separate evidence.
- **Uncomprehended Element** (downstream effect): Confirm independently that the visual change has made the element genuinely unclear — not merely different from what was previously seen.

## Examples → Rules
- **[Example 25.1] Windows Fluent Design + legacy Control Panel (ongoing):** Users encounter mixture of modern Fluent Design menus and 1990s-era 3D buttons and icons. Controls not incomprehensible in isolation, but inconsistency means no single automatic response to "navigate settings." → *Rule: When two design languages coexist in the same product, users cannot form a single automatic response to the same type of task. The inconsistency does not just slow habituation — it can break it entirely at each boundary crossing.*
- **[Example 25.2] iPhone "New" action (word vs. compose icon):** "New" appears as text in some apps, as box-with-pen icon in others. → *Rule: When the same function is represented by a word in some contexts and an icon in others, users must process each form independently rather than developing a single automatic recognition response. Mixing representations for the same function is this Trap.*

## Rules (consolidated)
- [definition] The inconsistency does not just slow habituation — it can temporarily break it, requiring the user to stop and consciously identify whether this is the same function they've encountered elsewhere.
- [related concepts] Gestalt Principle of Similarity: elements that look alike are perceived as belonging to the same category. Inconsistent Appearance presents the same element in forms the visual system treats as different things — forcing conscious identification where automatic recognition should suffice.
- [related concepts] Design systems: a well-maintained design system makes consistency the path of least resistance. The failure mode is a design system that exists on paper but is not enforced in practice, or updated without auditing legacy components that no longer conform.
- [why it occurs] Large products developed over long periods where design languages evolve but legacy components are not updated; different teams applying shared design systems inconsistently; components adapted for different contexts without maintaining coherence.
- [detection] Cross-system visual audit: identify most frequent elements, compare visual and auditory presentation across every context. Like Wandering Element, this is invisible to task-based evaluation.
- [AI detectability] Tier 1: systematic visual comparison of recurring elements across screens.

## Related Traps
- **Wandering Element** (distinguish and sometimes co-occurs): Audit both independently — placement and visual form are distinct dimensions.
- **Uncomprehended Element** (downstream): Visual change making element genuinely unclear; confirm independently.

## Report Language (U6)
**Finding:** [Function] is represented as [form A] in [context 1] and [form B] in [context 2] — users who have learned to recognize one form will not automatically recognize the other as the same function.
**Why it matters:** Each visual form users must learn for the same function is an additional cognitive investment that consistent design would eliminate.
**Confidence:** [Tier 1: Confirmed — visual inconsistency is directly auditable across screens]

## Remediation (U7)
Identify functions appearing most frequently across the product and systematically compare their visual representation across contexts. A design system specifying appearance for every recurring component is the most reliable prevention. For legacy components: either update to the current design language or clearly separate them into a context where the design language transition is explicitly communicated. Core actions — New, Delete, Edit, Share — must be represented consistently across the entire product.

## AI Detection Rules
**Tier 1 — Confirmed finding, multiple screens only:** Cross-context visual consistency is directly auditable by comparing visual representation of recurring controls across provided screens.
**`testable: false`:** For single screenshot analyses — omit from `traps_checked_not_found` for single-screenshot submissions; this is added automatically.

---

# CHUNK: AMBIGUOUS HOME

**chunk_id:** trap_ambiguous_home_v2
**tenet:** Habituating | **sub-tenet:** Oriented
**severity_combination_rule:** High when consequence is task failure or worse, regardless of likelihood.

## Definition (verbatim)
The interface presents the user with multiple, competing locations for getting oriented and initiating tasks.

A well-oriented interface has one place users conceptualize as home: a single, reliable starting point reachable from anywhere with one consistent action. It provides the spatial and navigational anchor from which all habituation in a hierarchically structured interface flows.

Ambiguous Home is a special case of both Non-Redundant and Consistent with Expectations sub-tenets: multiple homes is a redundancy problem; an inconsistent action for returning home is a consistency problem.

## DISCONFIRMATION — Apply First
NOT present when:
(a) A single clearly defined home exists and is reachable from every context via a consistent action — confirmed when users consistently agree on where home is and how to reach it.
(b) The product is deliberately designed without a persistent home because all tasks are self-contained.
(c) What appears to be multiple homes are entry points to clearly distinct, non-overlapping sections that users understand as separate.

## Severity
**Part A — Consequence:** Disorientation and loss of navigational confidence. Task abandonment when users cannot recover from getting lost. More severe in complex products with deep hierarchies where home is the primary recovery mechanism. Automaticity will not be achieved — users must always commit some attention to starting activities.
**Part B — Likelihood:** High when: two or more elements could plausibly serve as home and navigating to either produces a different starting context; product spans multiple input modes with different home experiences; home was designed by different teams at different times.
**Combination rule:** High severity when consequence is task failure or worse, regardless of likelihood.

## Confidence Tiers
- **Tier 2:** Multiple home candidates identifiable in design files. Whether the ambiguity is disorienting for real users requires knowledge of user mental models and navigation expectations.

## Root Cause Confirmation (U4)
- **Variable Outcome** (sometimes co-occurs): Confirm independently that the home action produces different results at different times — not merely that multiple home candidates exist. Multiple home candidates = Ambiguous Home. A home action that sometimes works and sometimes doesn't = Variable Outcome. Both may be present but require separate evidence.
- **Gratuitous Redundancy** (sometimes co-occurs): Confirm that the same actions can be invoked from the different home destinations — if so, both Traps apply.
- **Memory Challenge** (downstream effect): Confirm independently that users must consciously track their location because no reliable home exists.

## Examples → Rules
- **[Example 26.1] Windows 8 dual home experiences:** Mouse/keyboard and touch had different Start/Home experiences; much was same, some was different; confusion resulted; mitigated in later versions. → *Rule: When a product has two distinct Home experiences for different input modes that partially overlap, users cannot determine whether behavior expected in one mode will apply in the other. Partial overlap is more confusing than two fully distinct experiences. A single, consistent home across all input modes is required.*
- **[Example 26.2] Oculus Rift 2017 (3 separate homes):** Library, Explore (with house icon!), and Home — users couldn't get oriented. → *Rule: Using a universally recognized home symbol (house icon) for a destination that is not the primary home creates an Inviting Dead End that directly compounds Ambiguous Home. Home iconography must be reserved exclusively for the primary home.*

## Rules (consolidated)
- [definition] A clear single home makes returning to it one of the most deeply automatic actions a user can perform. Without it, users must reason their way back — the opposite of what a Habituating interface should require.
- [definition] The consequences extend beyond navigation: when users lack a clear home, they also lack a reliable recovery point.
- [detection] Ask users, without prompting, where they would go to start a new task or recover from being lost. Inconsistent answers confirm the Trap.
- [how to avoid] Establish a single home early in the design process and treat it as a constraint. Every section, regardless of which team designs it, should have one consistent action for returning to that home.
- [AI detectability] Tier 2: multiple home candidates identifiable from design files. Whether ambiguity is disorienting requires user observation.

## Related Traps
- **Variable Outcome** (sometimes co-occurs): Home action producing inconsistent results.
- **Gratuitous Redundancy** (sometimes co-occurs): Duplicate paths to initiate tasks from different homes.
- **Memory Challenge** (downstream): Without clear home, users must consciously track location.
- **Poor Grouping** (sometimes co-occurs): Multiple locations with partially overlapping capabilities slow development of a clear mental model for where to start.

## Report Language (U6)
**Finding:** The interface offers [N] locations or actions that could plausibly serve as home — [describe them] — producing different starting contexts and preventing users from developing a single reliable orientation habit.
**Why it matters:** Without a single reliable home, users who get disoriented must reason their way back rather than reaching automatically — and may not be able to recover at all. Automaticity will not be achieved — users will always commit some attention to starting activities.
**Confidence:** [Tier 2: Flagged — confirm user mental models around home with navigation observation]

## Remediation (U7)
Consolidate to one home — not better labeling of multiple homes. Ask users without prompting where they would go to start a new task or recover from being lost. Inconsistent answers confirm the Trap. The fix is always consolidation: one destination, one action, consistent across all contexts and input modes. Home iconography (house symbol) must be reserved exclusively for the primary home destination — using it elsewhere creates an Inviting Dead End that directly compounds this Trap.

## AI Detection Rules
**Tier 2 — Output to `potential_issues`, confidence "medium":** When the artifact shows two or more elements that could plausibly serve as the interface's global home destination (the single top-level anchor of the entire product). Flag: "Multiple elements could plausibly serve as the global home — confirm whether users agree on a single starting point."
**`testable: false`:** For single-screen artifacts where home ambiguity requires cross-section navigation knowledge.
**Critical disambiguation with GRATUITOUS REDUNDANCY:**
- AMBIGUOUS HOME is EXCLUSIVELY about the interface's **global home destination** — the product-level "home" that anchors the entire navigation system.
- Multiple competing entry points for a **specific feature, task, or action** → **GRATUITOUS REDUNDANCY**, NOT AMBIGUOUS HOME.
- Test: "Is the ambiguity about where to start in the *whole app*, or about which element to use for a *specific task*?" If the latter → GRATUITOUS REDUNDANCY.

---

# TRAP CHUNKS — BEAUTIFUL TENET

---

# CHUNK: POOR AESTHETIC

**chunk_id:** trap_poor_aesthetic_v2
**tenet:** Beautiful
**severity_combination_rule:** High when consequence is task failure or worse, regardless of likelihood.

## Definition (verbatim)
The system's sensory design, style, personality, or tone is judged as unpleasing, inappropriate, or inauthentic by its intended users.

The most difficult Trap in the framework to diagnose. Every other Trap can be identified through structural analysis, measurement, or observation of user behavior. Poor Aesthetic cannot. There is no measurement that tells you a design is unattractive, no code to inspect. There is only the response of the people experiencing it, interpreted in the context of who they are, where they are, and when.

## Two Dimensions
**Attractiveness:** The design is visually unpleasant.
**Appropriateness:** The design is mismatched to its context, audience, or purpose.

These should be assessed and reported as distinct findings when they can be independently evaluated. Attractiveness failures based on measurable properties (contrast, density, alignment) can be reported as Tier 1 findings. Appropriateness failures require audience and cultural knowledge and should be reported as Tier 3 — risk noted, not confirmed.

**Temporal appropriateness:** What feels current can feel dated in three years. This dimension cannot be reliably assessed from design file analysis alone — it requires ongoing cultural knowledge and should be flagged as outside the scope of automated assessment.

## DISCONFIRMATION — Apply First
NOT present when:
(a) Negative pre-launch aesthetic feedback reflects resistance to difference rather than lasting aesthetic failure — Motorola Razr and Aeron chair were both met with negative pre-launch responses and became aesthetic standards. Pre-launch feedback reliably reflects novelty resistance, not lasting aesthetic quality. Do not flag based on pre-launch feedback.
(b) The aesthetic is appropriate to its audience and context even if it would be inappropriate elsewhere — evaluation is audience-relative.
(c) Apparent aesthetic problems will be naturally resolved by fixing co-occurring functional Traps — assess aesthetic quality after functional remediation.

## Severity
**Part A — Consequence:** Reduced trust, reduced engagement, reduced willingness to recommend. Research shows poor aesthetics cause users to judge the entire product as more complex and less capable, independent of actual performance. For consumer products, aesthetic failure can be commercially fatal.
**Part B — Likelihood:** Measurable aesthetic failures (low contrast, misalignment, cluttered layout) are objectively present or absent. Overall aesthetic appropriateness requires audience and cultural knowledge.
**Combination rule:** High severity when consequence is task failure or worse, regardless of likelihood.

## Confidence Tiers
- **Tier 1:** Specific measurable co-occurring failures (contrast below WCAG, element misalignment, information density above thresholds) — serve as aesthetic risk indicators even when overall aesthetic cannot be assessed.
- **Tier 3:** Overall aesthetic judgment — cannot be assessed from design files alone. Requires cultural knowledge, aesthetic sensibility, and understanding of the social context in which the product will be experienced.

## Root Cause Confirmation (U4)
- **Poor Grouping, Information Overload, Inconsistent Appearance** (contributing causes): Each confirmed through their own independent evidence. When three or more functional Traps co-occur on the same screen, flag Poor Aesthetic as a likely co-occurring finding even when aesthetic judgment itself cannot be confirmed from the design file.

## Examples → Rules
- **[Example 27.1] Cluttered phone app with poor color, label justifications, layout issues:** Multiple simultaneous aesthetic failures signal lack of design investment overall. → *Rule: Aesthetic problems are cumulative — three simultaneous failures are not three times worse than one; the combined effect signals overall design investment failure. Flag co-occurring measurable failures as aesthetic risk indicators.*
- **[Example 27.2] ChatGPT-4o sycophancy (2025):** Aesthetic of personality/tone was notably mismatched to users — many described it as sycophantic; OpenAI rolled back within a week. → *Rule: Aesthetics apply to any sensory aspect of an experience, including personality and tone. An AI system's communicative style has aesthetic quality — sycophantic tone is this Trap for voice and conversational interfaces.*
- **[Example 27.3] Motorola Razr (negative pre-launch, massive success post-launch):** Pre-launch: "it'll break, doesn't look like a phone." Post-launch: became the new aesthetic standard. → *Rule: Pre-launch aesthetic feedback reliably reflects resistance to the unfamiliar rather than a signal about lasting quality. Acting on pre-launch aesthetic user feedback would have killed the Razr. Trust designers over pre-launch aesthetic feedback.*
- **[Example 27.4] Aeron chair (same pattern):** Negative pre-launch aesthetic response; became an enduring design icon. → *Rule: Same pattern as Razr. Novelty resistance is systematic and predictable. Pre-launch aesthetic feedback is not a reliable quality signal.*

## Rules (consolidated)
- [definition] A product cannot be Beautiful if it fails on other Tenets. Functional excellence is the necessary foundation for aesthetic quality.
- [definition] You cannot reliably test for beauty before shipping. You can test for what will prevent it from being realized — evaluate the product against the other eight Tenets.
- [examples] Aesthetics apply to any sensory dimension: visual, auditory, tone, personality. Sycophantic AI tone is a Poor Aesthetic finding.
- [related concepts] Aesthetic-Usability Effect (Tractinsky et al., 2000): users perceive attractive interfaces as easier to use. The relationship runs both directions: usable interfaces are perceived as more beautiful. Failures on either Tenet produce perceptions of failure on both.
- [related concepts] Processing Fluency: ease of visual processing produces positive aesthetic responses. Physical Challenge (poor legibility) creates negative aesthetic perception independent of actual design quality — legibility and aesthetic quality are entangled.
- [why it occurs] Insufficient investment (cut under schedule/budget pressure); insufficient expertise (aesthetic decisions by committee or relying on pre-launch user feedback).
- [AI detectability] Tier 3 for overall aesthetic judgment. Tier 1 for specific measurable violations (contrast, misalignment, density) that serve as risk indicators.

## Related Traps
- **Poor Grouping, Information Overload, Inconsistent Appearance** (contributing causes): Often produce visual clutter that is both functionally and aesthetically problematic. Addressing functional Traps often improves aesthetics simultaneously.

## Report Language (U6)
**Attractiveness dimension (Tier 1 only):**
**Finding:** The interface exhibits [specific measurable failures — low contrast / misalignment / visual clutter] that are likely to reduce perceived quality and user engagement, independent of functional performance.
**Why it matters:** Poor aesthetics cause users to judge the entire product as more complex and less trustworthy — a known predictor of disengagement affecting all users, not only those who notice specific failures.
**Confidence:** [Tier 1: Confirmed for measurable failures]

**Appropriateness dimension:**
**Confidence:** [Tier 3: Overall aesthetic judgment requires cultural and audience knowledge beyond design file analysis / Temporal appropriateness is outside scope of automated assessment]

## Remediation (U7)
Ensure functional excellence on the other eight Tenets first — aesthetic quality cannot rescue a functionally broken product, and fixing functional Traps often improves aesthetics naturally. Give design expertise genuine authority from the earliest stages. Do not act on pre-launch aesthetic user feedback — it reliably reflects resistance to difference, not lasting aesthetic failure. Trust designers, not pre-launch user aesthetic responses.

## AI Detection Rules
**`testable: false`:** Not reliably detectable through structural analysis — requires cultural and aesthetic judgment. Always omit this trap from `traps_checked_not_found` — it is added automatically to the output.
**Human Review only:** When you observe potential visual inconsistencies or quality concerns, output to `flagged_for_human_review`. Question: "Does the visual design of [element] meet your brand/quality standards?"

