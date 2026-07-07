# UI Tenets & Traps — Trap Cards (v1 card deck, verbatim)

## PROVENANCE (maintainer notes — never loaded into analysis passes)

**Cell B definition:** the public framework as a team would self-serve it — the published card deck's text placed in a prompt, verbatim, with NO added evaluation logic: no priority order, no disconfirmation protocol, no tiers, no severity/confidence system, no report structure, no process rules of any kind. Report structure is supplied by the harness instruction at run time (documented as harness-provided in the eval materials). Source: `Tenets_and_Traps_Card_MASTER_print.pdf`, transcribed 2026-07-04, author-verified definitions (26/26 match the registry). The deck's "Your Trap Here?" community-invitation card is omitted — it is deck furniture, not framework content, and it invites out-of-taxonomy invention; if strict whole-deck fidelity is preferred, it can be restored verbatim. This file supersedes the prior `trap_kb_v1.0.md` (a generated KB carrying added evaluation logic), which is archived as `archive/trap_kb_v1.0_generated_DEPRECATED.md` — licensing exhibit #3 and the file actually executed in the 2026-07-03/04 clean run's B condition (see run-log kb_hash to disambiguate).

---

## WHAT ARE TENETS & TRAPS?

TENETS & TRAPS are a heuristic framework for evaluating user interfaces.

STRENGTHS:
- They distill a massive body of existing UI research into a portable, actionable tool.
- They are proven to predict actual user performance and satisfaction.
- They facilitate the design of better solutions by explaining what causes problems.
- They improve team communication by establishing common language.

TENETS describe general attributes of good interface design.

TRAPS describe common design problems that degrade interface goodness. Reduce traps and the experience improves.

## TENETS AND THEIR TRAPS

+ UNDERSTANDABLE
- Invisible Element
- Effectively Invisible Element
- Distraction
- Uncomprehended Element
- Inviting Dead End
- Poor Grouping
- Forced Syntax
- Memory Challenge
- Feedback Failure

+ COMFORTABLE
- Physical Challenge
- Accidental Activation

+ RESPONSIVE
- Slow or No Response
- Captive Wait

+ EFFICIENT
- Unnecessary Step
- System Amnesia
- Information Overload
- Bad Prediction

+ FORGIVING
- Irreversible Action

+ DISCREET
- Unwanted Disclosure

+ PROTECTIVE
- Data Loss

+ HABITUATING
- Gratuitous Redundancy
- Variable Outcome
- Wandering Element
- Inconsistent Appearance
- Ambiguous Home

+ BEAUTIFUL
- Unattractive Appearance

## HOW TO USE TRAP CARDS

1. Identify the tasks that are most important to your target user.
2. Walk through ALL the ways the user might try to complete each task in the design.
3. Identify and log any Traps you observe and note their severity. Many issues have more than one Trap, log all you see.
4. If you're not sure which Traps apply, ask yourself which Tenets are being degraded - this can help to clarify the problem.
5. For issues that have multiple Traps, ask yourself whether one Trap may be the root cause of the others. Understanding which Trap is at the root of an issue is often critical to finding the best solution.
6. If you have time, cross-validate by having other reviewers run through the tasks.
7. Share your results. Use Tenets & Traps to facilitate a good discussion.

## TRAP CARDS

### Card 1 — INVISIBLE ELEMENT (Tenet: UNDERSTANDABLE)

No cue (label, icon, affordance, or prompt) is provided to signal to the user how to achieve a goal, and the user has insufficient prior learning to overcome its absence.

Example: In 2012 Microsoft released Windows 8. Unlike previous versions, Windows 8 removed a visible means to launch the Start Menu. The resulting user confusion led to the Start button's return in the next version of Windows.

### Card 2 — EFFECTIVELY INVISIBLE ELEMENT (Tenet: UNDERSTANDABLE)

A provided cue (label, icon, affordance, or prompt) is not noticed, or is slow to be noticed, because its appearance or location differs from what the user expects.

Example: In a past version of the Xbox 360 interface, the global search function was placed on the controller's Y button. This was indicated in a corner of the interface, but was effectively invisible to users, whose focus was on the tiles. A subsequent addition of a search tile solved the problem.

### Card 3 — DISTRACTION (Tenet: UNDERSTANDABLE)

Something in the UI suddenly appears or otherwise draws the user's attention, distracting them from their goal.

Example: The iPhone news reader notifications can pop up over the top of the GPS mapping application when the user is driving. This obscures the driving directions.

### Card 4 — UNCOMPREHENDED ELEMENT (Tenet: UNDERSTANDABLE)

A cue (label, icon, affordance, or prompt) critical to achieving a goal is noticed, but its meaning, or the required method of interacting with it, is unclear.

Example: In 2016 Waze changed their search icon from a silhouette of their logo to the very familiar and readily comprehended magnifying glass search icon.

### Card 5 — INVITING DEAD END (Tenet: UNDERSTANDABLE)

A cue (label, icon, affordance, or prompt) is incorrectly judged as a means for achieving a goal. It looks right, but is wrong.

Example: On the original iPhone, users would get drawn into the iTunes app instead of the iPod app due to the design of the icon. Subsequent changes to the iPod (music) icon have not mitigated this problem.

### Card 6 — POOR GROUPING (Tenet: UNDERSTANDABLE)

A critical relationship between two or more otherwise noticeable cues (labels, icons, affordances, or prompts) is not obvious.

Example: In the 2000 presidential election, 4,000 people made the error of punching the second hole on the butterfly ballot in the mistaken belief that the second hole represented the second candidate, while 19,000 people punched more than one hole. This Trap changed the outcome of the election.

### Card 7 — FORCED SYNTAX (Tenet: UNDERSTANDABLE)

The system does not allow the user to issue a command or complete a sequence of actions in the order or manner that is most natural to them.

Example: When talking to voice-driven devices like those powered by Amazon's Alexa, users must first address the device and then say their command. But this isn't always how humans formulate sentences. "Alexa, what time is it?" works, but "What time is it, Alexa?", doesn't.

### Card 8 — MEMORY CHALLENGE (Tenet: UNDERSTANDABLE)

The system requires the user to remember information that is easy to forget.

Example: Efforts to make systems secure often make them impossible to use. In this example, American Express required users to remember not only the answer to their security question, but also the security question itself.

### Card 9 — FEEDBACK FAILURE (Tenet: UNDERSTANDABLE)

The system fails to provide noticeable, comprehensible, and actionable feedback in response to user actions.

Example: Sooner or later everyone encounters an error. The hope is that the error will help guide the user to a solution. In this example, the feedback message fails on this count. [Card shows: Microsoft Word — "Word did not save the document." in response to Ctrl+S]

### Card 10 — PHYSICAL CHALLENGE (Tenet: COMFORTABLE)

An action the system requires the user to perform is physically effortful, difficult, or impossible.

Example: Human finger pads are about 12 mm across on average. Not all touch controls adhere to that norm, including the version of the iPhone lock screen music controls shown above. These were difficult for users to target and were ultimately enlarged.

### Card 11 — ACCIDENTAL ACTIVATION (Tenet: COMFORTABLE)

The system misinterprets a user's physical actions resulting in an unintended outcome.

Example: With gesture based systems like Kinect, it is often difficult to determine the user's intent: Is a hand gesture a navigational swipe or an effort to scratch one's ear? This makes scrolling via hand gestures prone to accidental activations.

### Card 12 — SLOW OR NO RESPONSE (Tenet: RESPONSIVE)

The user is prevented from achieving a goal in a timely manner because of actual or perceived poor system performance.

Example: After pressing the button to activate the Super-Bright LED Flashlight application on an Android phone, it can take up to 5 seconds for the light to actually turn on.

### Card 13 — CAPTIVE WAIT (Tenet: RESPONSIVE)

The user is prevented from achieving a goal in a timely manner because the system intentionally prevents them from advancing and/or backing out of a process.

Example: YouTube often presents users with advertisements without providing a means of advancing to the content they are actually interested in.

### Card 14 — UNNECESSARY STEP (Tenet: EFFICIENT)

When the product is being used as intended, the number of actual or perceived steps required to achieve a goal is too high.

Example: The hamburger menu has become ubiquitous with early mobile design. But companies have discovered that removing it and flattening the hierarchy can increase the efficiency of their UIs. Spotify is a notable example of a company that ditched the hamburger.

### Card 15 — SYSTEM AMNESIA (Tenet: EFFICIENT)

The system re-prompts the user for information it previously gathered, or otherwise fails to leverage the user's prior work.

Example: This version of the Xbox website uses valuable space to sell the user Halo… even though it clearly displays that the user already owns it.

### Card 16 — INFORMATION OVERLOAD (Tenet: EFFICIENT)

Information presented to the user is comprehensible, but there is too much of it.

Example: Back in 2002, the Jeep website had an extremely wordy description explaining how to find the nearest Jeep dealer. By 2007 this issue was fixed. Credit: Jeff Johnson

### Card 17 — BAD PREDICTION (Tenet: EFFICIENT)

The system incorrectly predicts or interprets the user's intent or preference, resulting in the user having to work around the problem.

Example: Spelling autocorrection services often make mistakes. When wrong, it is irritating, embarrassing, or insulting.

### Card 18 — IRREVERSIBLE ACTION (Tenet: FORGIVING)

The system does not allow the user to undo an action they have taken.

Example: In this version of Concur's iOS travel app, pressing the Reserve button not only reserved but also purchased the flight, which could not be undone.

### Card 19 — UNWANTED DISCLOSURE (Tenet: DISCREET)

The system makes the user's data or behavior public in a way that is harmful or embarrassing to the user.

Example: Facebook Beacon was a feature that shared users' partner-site purchase activities on the news feed on an opt-out basis. One consequence of this was that friends were alerted to gifts that were meant to be surprises. Beacon became the target of a class action lawsuit and Facebook shut it down.

### Card 20 — DATA LOSS (Tenet: PROTECTIVE)

The system can lose the user's work through some action or inaction on the user's part.

Example: Unexpected Windows 8 system shutdowns can cause users to lose any unsaved work. Good user interfaces mitigate this risk by continuously saving users' data.

### Card 21 — GRATUITOUS REDUNDANCY (Tenet: HABITUATING)

The system presents duplicate cues (labels, icons, affordances, or prompts) for the same action on the same level, or a directly nested level of the UI.

Example: In 2014 Healthcare.gov had three links on the homepage that all went to the exact same place. They subsequently added a fourth link to the same place, which only exacerbated the issue. This duplication of choices impedes habituation.

### Card 22 — VARIABLE OUTCOME (Tenet: HABITUATING)

The system responds differently at different times to the same user action.

Example: The browser Back button in Twitter yields a different outcome depending on when the user clicks on it. After launching a Twitter dialog and then hitting Back, the user is taken back two steps instead of one. This lack of consistency impedes habituation.

### Card 23 — WANDERING ELEMENT (Tenet: HABITUATING)

The physical location of a cue (label, icon, affordance, or prompt) for a given action varies across the UI.

Example: Placement of the Edit control is inconsistent from one iPhone app to another. Several other functions are similarly inconsistent. This lack of consistency impedes habituation.

### Card 24 — INCONSISTENT APPEARANCE (Tenet: HABITUATING)

The visual appearance of a cue (label, icon, affordance, or prompt) for a given action varies across the UI.

Example: The new action in iPhone apps sometime appears as the word New, while elsewhere it appears as a box with a pen. This lack of consistency impedes habituation.

### Card 25 — AMBIGUOUS HOME (Tenet: HABITUATING)

The UI provides no single place the user can return to at any time to begin a new task or get re-oriented.

Example: Windows 8 had two different Start or Home experiences. One for mouse and keyboard and one for touch. Much was the same…some was different. The result was confusion, which has been mitigated to some extent in more recent versions of the UI.

### Card 26 — UNATTRACTIVE APPEARANCE (Tenet: BEAUTIFUL)

The UI is aesthetically unpleasing, inconsistent, and/or inappropriate for its intended users.

Example: There are many aesthetically pleasing applications, websites and programs. This is not one. This overly cluttered phone app has poor color choice, label justifications and layout issues.
