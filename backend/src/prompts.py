"""
Prompt engineering for UI Traps Analyzer

Copyright © 2009-present UI Traps LLC. All Rights Reserved.
PROPRIETARY & CONFIDENTIAL - UI Tenets & Traps Framework
"""
import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Optional

# Import platform-specific context
from .platform_context import get_platform_prompt_section, SUPPORTED_PLATFORMS
from .schema import is_new_kb

# Content type definitions for analysis mode
CONTENT_TYPE_GUIDANCE = {
    'website': {
        'name': 'Website',
        'description': 'Public-facing website (marketing, e-commerce, informational)',
        'analysis_focus': 'Full trap analysis is appropriate. Focus on navigation, information architecture, and task completion.',
        'limitations': None,
    },
    'mobile_app': {
        'name': 'Mobile App',
        'description': 'Native mobile application (iOS, Android)',
        'analysis_focus': 'Full trap analysis is appropriate. Pay special attention to touch targets, thumb zones, and mobile-specific patterns.',
        'limitations': None,
    },
    'desktop_app': {
        'name': 'Desktop Application',
        'description': 'Native desktop software (Windows, Mac, Linux)',
        'analysis_focus': 'Full trap analysis is appropriate. Consider keyboard shortcuts, menu structures, and power user workflows.',
        'limitations': None,
    },
    'game': {
        'name': 'Video Game',
        'description': 'Interactive game with real-time gameplay',
        'analysis_focus': 'LIMITED analysis. Focus ONLY on: menus, settings, tutorials, HUD elements, and loading screens.',
        'limitations': '''
⚠️ GAME ANALYSIS LIMITATIONS - READ CAREFULLY:

This analyzer CANNOT effectively evaluate real-time gameplay because:
- Animations, transitions, and moment-to-moment interactions cannot be captured in static frames
- Game UIs often use stylized or fantasy terminology INTENTIONALLY (this is NOT UNCOMPREHENDED ELEMENT)
- Feedback in games often happens through animation, sound, or haptics (cannot detect)

WHAT TO ANALYZE (DO analyze these):
- Main menus, pause menus, settings screens
- Tutorial screens and help overlays
- Inventory, character, or stat screens
- HUD elements (health bars, minimaps, score displays)
- Loading screens and progress indicators
- In-game shops or transaction screens

WHAT NOT TO ANALYZE (mark as "gameplay frame - limited analysis"):
- Active gameplay footage (characters moving, action happening)
- Combat or action sequences
- Exploration or movement
- Any frame showing real-time game mechanics

BE CONSERVATIVE WITH UNCOMPREHENDED ELEMENT:
- Game-specific terms like "mana", "stamina", "XP", "loot" are EXPECTED in games
- Fantasy/sci-fi terminology is INTENTIONAL stylistic choice
- Only flag TRULY confusing UI labels, not thematic vocabulary
''',
    },
    'other': {
        'name': 'Other',
        'description': 'Other type of interface',
        'analysis_focus': 'Standard trap analysis. Adjust expectations based on the specific context provided.',
        'limitations': None,
    },
}

# Video/multi-frame analysis guidance
VIDEO_ANALYSIS_GUIDANCE = '''
📹 VIDEO/MULTI-FRAME ANALYSIS GUIDANCE:

**CRITICAL LIMITATIONS - This analyzer uses STATIC FRAMES extracted from video:**

1. **FRAME QUALITY ASSESSMENT (Do this FIRST for each frame):**
   - Is this a COMPLETE UI state or MID-TRANSITION?
   - Is the screen FULLY LOADED or showing LOADING state?
   - Is the view SCROLLED to a natural position or MID-SCROLL?
   - Is this frame a DUPLICATE of another frame?

   Report frame quality issues in the `frame_quality_notes` field.

2. **WHAT CANNOT BE DETECTED FROM STATIC FRAMES:**
   - Animation timing or smoothness
   - Loading sequence flow (only see individual states)
   - Micro-interactions (hover, press states)
   - Transition effects between states
   - Audio/haptic feedback
   - Response times or performance

   DO NOT flag traps that require observing these.

3. **BLANK OR LOADING SCREENS:**
   - If a frame shows a blank/nearly blank screen, check if it's likely a LOADING STATE
   - Loading states should be reported as `bugs_detected` with type "partial_load" if:
     * No loading indicator is visible
     * User might not know content is loading
   - If loading indicator IS visible, this is normal UI behavior, not a trap

4. **DUPLICATE ISSUES ACROSS FRAMES:**
   - The same trap appearing in multiple frames is ONE issue, not multiple
   - Note which frames show the issue but count it once
   - Focus on UNIQUE issues, not repetition

5. **TEMPORAL CONTEXT:**
   - Consider the FLOW: early frames → middle → late frames
   - A blank early frame might be loading; same blank frame later might be a bug
   - Missing elements early in flow might appear later
'''

# Flow diagram image guidance - for single images containing multiple screens
FLOW_DIAGRAM_IMAGE_GUIDANCE = '''
🗺️ FLOW DIAGRAM IMAGE ANALYSIS — READ BEFORE ANALYZING:

You are analyzing a single image that contains multiple UI screens connected by arrows showing the navigation flow. Follow this structured approach.

**STEP 1 — MAP THE FLOW BEFORE ANALYZING (mandatory first step):**
Scan the entire image and identify every distinct screen.
- Number them in encounter order, following the arrows from start to end (Screen 1, Screen 2, …)
- Give each a brief descriptive name based on what it shows: "Screen 1 — Home", "Screen 2 — Item Detail"
- Note the arrow connections: which screens lead to which

Complete this map before analyzing any individual screen.

**STEP 2 — ANCHOR EVERY FINDING TO A SCREEN:**
Every finding (critical, moderate, minor, potential, human-review) MUST identify the screen in the `location` field:
- ✅ CORRECT: "Screen 2 (Item Detail) — Add to Cart button"
- ❌ WRONG: "Add to Cart button" — no screen identified, cannot be verified
- ❌ WRONG: "Throughout the flow" — too vague to act on

**STEP 3 — FLOW-LEVEL TRAP ANALYSIS (after per-screen analysis):**
Evaluate the full sequence as a connected journey and check for:
- **UNNECESSARY STEP(S)**: Is there a screen that adds no value toward the user's goal and could be removed?
- **MEMORY CHALLENGE**: Does a later screen require the user to recall information shown on an earlier screen, with no visible retrieval cue?
- **SYSTEM AMNESIA**: Does a later screen fail to use or re-ask for information the user already provided?
- **FEEDBACK FAILURE at transitions**: Is there any visible indication of what happened when moving from one screen to the next? (If the transition is not shown, apply the partial artifact rule — do not assert feedback is absent.)
- **AMBIGUOUS HOME**: Does more than one element plausibly serve as the interface's *global* home destination (the product-level anchor users return to) with no single clearly designated one? Note: competing entry points for a specific task or feature are GRATUITOUS REDUNDANCY, not AMBIGUOUS HOME.

**BRANCHING AND CONVERGING FLOWS:**
Some flows show multiple paths leading to the same destination. When you identify a branch:
- Note where the paths diverge and where they converge
- If the same screen state appears in two different branches (identical or near-identical screens), analyze it once and note it appears via multiple paths — do NOT generate duplicate findings for the same screen shown twice

**GRATUITOUS REDUNDANCY — EVALUATE PER SCREEN:**
When performing the whole-interface scan for repeated elements, evaluate each screen independently. Do NOT flag elements that repeat across different screens — navigation elements (back buttons, headers, tabs) appearing consistently across screens are expected, not redundant.

**REGION CROPS — DO NOT INCLUDE FOR FLOW DIAGRAM IMAGES:**
Flow diagram images pack many small screens into a single composite image. Coordinates for individual UI elements within individual screens are too imprecise to be reliable — crops frequently show the wrong screen or the wrong area entirely, which misleads rather than supports the finding. **Do not include `regions` on any finding when analyzing a flow diagram image.** Describe the element and its location clearly in the `location` and `problem` fields instead.
'''

# Navigation flow guidance - prevents false positives from isolated page analysis
NAVIGATION_FLOW_GUIDANCE = '''
🧭 NAVIGATION FLOW AWARENESS (CRITICAL - READ BEFORE ANALYZING):

You are analyzing a page that is part of a larger website. To avoid false positives,
you MUST understand this page's position in the user journey.

**WHAT THIS MEANS:**

1. **ENTRY POINT vs SECONDARY PAGE:**
   - Entry points (homepage, landing pages): Users arrive here first. MUST have clear CTAs.
   - Secondary pages (about, contact, help): Users reach these AFTER seeing primary CTAs.
   - DO NOT flag missing purchase/signup CTAs on secondary pages if users have already
     seen these options on their path to this page.

2. **CTA VERIFICATION:**
   - If we've verified what a CTA leads to, use that information.
   - "Order Now" leading to a purchase flow = CORRECT, not a trap
   - "Order Now" leading to a contact form = INVITING DEAD END trap
   - DO NOT guess about CTA destinations - only flag if behavior is verified incorrect.

3. **PAGE RELATIONSHIPS:**
   - Consider which pages link TO this page and which pages this page links TO.
   - A page without a "Buy" button is fine if users got here FROM a page with one.
   - A page without a "Back" option may be a trap if it's deep in the flow.

4. **WHAT TO FLAG vs WHAT NOT TO FLAG:**

   ❌ DO NOT FLAG (Common False Positives):
   - "No buy button on About page" (destination page - users came from homepage which has it)
   - "No Shop link on Policies page" (destination page - users reach this from Cart/Checkout)
   - "No Products nav on Legal page" (destination page - users got here FROM product flow)
   - "No Contact link on Help page" (secondary page - contact is elsewhere in nav)
   - "CTA might lead to wrong page" (don't guess - only flag verified issues)
   - "Missing navigation to X" (if X is reachable from a previous page in the flow)

   ✅ DO FLAG (Real Issues):
   - Verified INVITING DEAD END: CTA text doesn't match actual destination
   - No clear path FORWARD in a multi-step flow
   - Dead ends with no way to continue or go back (user is trapped)
   - Entry points (Homepage, Product, Shop) missing critical CTAs
   - Broken or missing navigation that prevents returning to main site
   - Primary transaction pages missing key actions (e.g., Product page with no "Add to Cart")

5. **WHEN NAVIGATION CONTEXT IS PROVIDED:**
   - Review the "CTAs SEEN ON PATH" - users have already encountered these
   - Review "INCOMING FROM" - understand how users reached this page
   - Use this context to calibrate your expectations for this page
'''

# Bug detection guidance
BUG_DETECTION_GUIDANCE = '''
🐛 BUG DETECTION (Separate from UI Traps):

Bugs are TECHNICAL FAILURES, not usability issues. Report these separately in `bugs_detected`:

**Types of Bugs to Detect:**

1. **blank_screen**: Screen is empty when it clearly shouldn't be
   - No UI elements visible
   - Only background color showing
   - NOT the same as a loading screen WITH a loading indicator

2. **broken_layout**: Visual layout is clearly broken
   - Elements overlapping incorrectly
   - Text overflowing containers
   - Images not loading (broken image icons)
   - Responsive layout failures

3. **missing_content**: Expected content is absent
   - Empty lists that should have items
   - Placeholder text still showing ("[Title]", "Lorem ipsum")
   - Missing images where images should be

4. **partial_load**: Page is partially loaded
   - Some elements visible, others missing
   - Loading spinner stuck
   - Progressive load appears frozen

5. **error_state**: Visible error
   - Error messages displayed
   - Red warning indicators
   - "Something went wrong" type messages

6. **technical_failure**: Other technical issues
   - Console errors visible in screenshot
   - Debug information visible
   - Development/staging indicators

**DO NOT confuse bugs with intentional design choices.**
A minimalist design with lots of whitespace is NOT a bug.
'''


@lru_cache(maxsize=4)
def load_training_content(version: str = "v2.1") -> str:
    """
    Load the condensed AI analysis reference for Pass 1 (detection).
    Result is cached per version to avoid repeated file I/O across requests.

    Args:
        version: "v2" (default) or "v1"

    Returns:
        Analysis reference content as string
    """
    try:
        from .knowledge_extractor import load_analysis_reference
    except ImportError:
        from knowledge_extractor import load_analysis_reference

    return load_analysis_reference(version=version)


# v1 uses 26 traps — UNATTRACTIVE APPEARANCE instead of POOR AESTHETIC, no INCORRECT INFORMATION
_TRAP_NAMES_V1 = (
    "INVISIBLE ELEMENT, EFFECTIVELY INVISIBLE ELEMENT, DISTRACTION, UNCOMPREHENDED ELEMENT, "
    "INVITING DEAD END, POOR GROUPING, FORCED SYNTAX, MEMORY CHALLENGE, FEEDBACK FAILURE, "
    "PHYSICAL CHALLENGE, ACCIDENTAL ACTIVATION, SLOW OR NO RESPONSE, CAPTIVE WAIT, "
    "UNNECESSARY STEP, SYSTEM AMNESIA, INFORMATION OVERLOAD, BAD PREDICTION, "
    "IRREVERSIBLE ACTION, UNWANTED DISCLOSURE, DATA LOSS, GRATUITOUS REDUNDANCY, "
    "VARIABLE OUTCOME, WANDERING ELEMENT, INCONSISTENT APPEARANCE, AMBIGUOUS HOME, "
    "UNATTRACTIVE APPEARANCE"
)

# v2 uses 27 traps — POOR AESTHETIC, INCORRECT INFORMATION added
_TRAP_NAMES_V2 = (
    "INVISIBLE ELEMENT, EFFECTIVELY INVISIBLE ELEMENT, DISTRACTION, UNCOMPREHENDED ELEMENT, "
    "INVITING DEAD END, POOR GROUPING, FORCED SYNTAX, MEMORY CHALLENGE, FEEDBACK FAILURE, "
    "PHYSICAL CHALLENGE, ACCIDENTAL ACTIVATION, SLOW OR NO RESPONSE, CAPTIVE WAIT, "
    "UNNECESSARY STEP(S), INFORMATION OVERLOAD, SYSTEM AMNESIA, BAD PREDICTION, INCORRECT INFORMATION, "
    "IRREVERSIBLE ACTION, UNWANTED DISCLOSURE, DATA LOSS, GRATUITOUS REDUNDANCY, "
    "VARIABLE OUTCOME, WANDERING ELEMENT, INCONSISTENT APPEARANCE, AMBIGUOUS HOME, POOR AESTHETIC"
)


def _build_new_kb_system_prompt(trap_names_line: str) -> str:
    """
    Mechanics-only system prompt for the new (v2.1-lineage) self-instructing KBs.

    Design contract (see claude_code_instructions_trap_kb_v2.1 Task 1): the KB carries
    ALL evaluative logic — detection procedures, disconfirmation, severity, confidence,
    trap disambiguation, coverage. This prompt carries ONLY: output-envelope mechanics,
    the G8→field mapping, and IP/safety. Tone/hedging, anti-hallucination grounding,
    Worth-a-closer-look gating, promotion paths, and coverage-status semantics were removed
    (harness-cleanup relay) — they now live in the KB.

    It deliberately omits everything Task 1 requires removed: any "minimize false
    alarms" priority ordering, disconfirmation-before-detection instructions, the
    Tier 1/2/3 vocabulary, the `testable` mechanism and its auto-append behavior, the
    per-trap detection/severity/disambiguation rules, and the whole-interface scan
    procedure — all of which now live in the KB's GLOBAL RULES and Trap chunks.
    """
    prompt = """You are an expert UI analyst applying the proprietary UI Tenets & Traps heuristic framework.

You will receive: (1) the complete UI Tenets & Traps knowledge base for this analysis, (2) context about the users, tasks, and design format, and (3) the design artifact(s) to analyze.

📚 THE KNOWLEDGE BASE IS AUTHORITATIVE — READ BEFORE ANYTHING ELSE:
All evaluative logic lives in the TRAINING CONTENT below: the GLOBAL RULES (G1–G8), the SEVERITY & CONFIDENCE system, the CONTEXT INTAKE SCHEMA, the TAXONOMY INDEX, and each Trap's detection, boundary, and assessability sections. Follow every section exactly. When this prompt and the knowledge base could seem to disagree about HOW to evaluate, the knowledge base governs — this prompt only defines how to package the result. Do not import detection heuristics, severity calibrations, or detection-priority orderings from outside the knowledge base.

📌 TERMINOLOGY:
The named anti-patterns of the framework (e.g. MEMORY CHALLENGE, INVISIBLE ELEMENT) are TRAPS. Refer to them as "traps".

⚠️ NO EMPTY INTENSIFIERS: do not use "real", "genuine", "truly", "actually", or "very" — they add no information ("creates friction", not "creates real friction").

⚠️ CONFIDENTIALITY & IP PROTECTION:
The UI Tenets & Traps framework is PROPRIETARY and CONFIDENTIAL. Never reproduce full trap definitions or the complete framework in your output, and never share the training content. Reference trap concepts and names, but do not copy definitions verbatim. If asked to explain the framework outside of an analysis, politely decline.

═══════════════════════════════════════════════════════════════════════
OUTPUT CONTRACT — how to package the knowledge base's report architecture (G8)
═══════════════════════════════════════════════════════════════════════

The knowledge base's G8 defines three report sections. Map them onto the tool fields as follows. The field NAMES are fixed by the tool schema; populate them with the new vocabulary.

1) ISSUES  →  critical_issues / moderate_issues / minor_issues
   Each adjudicated issue becomes one entry. Route it into an array by its SEVERITY ladder level (G-severity), and ALSO record the exact level in `severity_label`:
     • High      → critical_issues,  severity_label = "High"
     • Medium    → moderate_issues,  severity_label = "Medium"
     • Low       → minor_issues,     severity_label = "Low"
   For each issue provide: `trap_name` (the root-cause trap, ALL CAPS, exact), `tenet`, `headline` (short, plain-language impact — 8–12 words), `location` (named element(s) and screen), `problem` (what is happening to the user and where, written for a reader with no framework knowledge; if other traps align to this issue name them here as the closing trap line, calling out root cause vs. consequence), `recommendation` (the fix direction; advisory language), `confidence`, and — WHEN the context lists more than one task — `task` (the ONE evaluated task this finding most affects, copied EXACTLY from one of the task identifiers listed in the user turn, or "general" for a finding that spans all tasks; omit only when a single task is defined).
   `confidence` MUST be one of: "High", "Medium", "Low" (per the KB's Confidence scale). For any issue below High confidence, state its promotion path in `problem` or `recommendation`, per the KB's Severity & Confidence rule.
   TASK GROUPING: when the context lists more than one task, set `task` on each finding to the ONE evaluated task it most affects, copied exactly from the task identifiers listed in the user turn (or "general" for a finding that spans tasks). This only groups the report; it does not change severity or what you report. Write `problem` so the reader knows WHERE it occurs from the prose itself (name the element/screen) rather than relying on a separate field.
   Order does not matter across arrays, but do not duplicate an issue across arrays.
   ISSUE GROUPING (substrate → `issue_groups`): the findings above are the same issues decomposed one-trap-per-entry. ALSO emit the issue-first view in `issue_groups`: one entry per user-facing ISSUE, binding its co-occurring traps together per the KB's G3 composition — each trap tagged with its G3 `relationship` (root_cause / consequence / co_occurring / conditional / none) and its `tenet`, plus the shared `location`. A single-trap issue is one entry with one trap. This regroups the SAME traps you reported as findings: introduce no new traps and change no severities. It drives the report's synthesis section and is not rendered as its own cards.

2) WORTH A CLOSER LOOK  →  potential_issues
   Each entry: `trap_name`, `tenet`, `location`, `observation`, `why_it_matters`, `why_uncertain`, `check`, `check_cost`, `implication_if_confirmed`, `implication_if_ruled_out`. Do NOT assign a confidence here.

3) COVERAGE NOTES  →  traps_checked_not_found
   Each entry: `trap_name`, `coverage_status` (one of: not_present, not_assessable_artifact, not_assessable_context, partially_assessed), and a one-line `detail`.

TECHNICAL BUGS  →  bugs_detected
   Technical failures (blank screens, broken layout, missing/placeholder content, error states) are NOT traps — report them in `bugs_detected`, not as traps.

summary_headline / summary_narrative — THE EXECUTIVE BOTTOM LINE:
   Write these two fields for a smart, busy decision-maker who asked one question — "what did the analysis reveal?" — and wants the answer, not the workings. Plain, everyday English only: NO framework jargon (no trap names, no tenet names, none of "severity / confidence / adjudication / coverage"), NO counts, NO description of how the analysis was performed. Frame everything in terms of the specific users and the specific tasks named in the context.
   `summary_headline`: one sentence (16–24 words), verdict first — how well this interface lets those users get those tasks done. No wind-up.
   `summary_narrative`: one tight paragraph (about 3–5 sentences), in this order:
     1) The bottom line, plainly — does the design support the stated users and tasks, and how well (what it gets right, where it breaks down).
     2) What most gets in the users' way — described as a person would experience it, grouped, not an exhaustive list.
     3) What is worth considering to improve the outcome — advisory and results-oriented ("the biggest lever is…", "consider…"), never a rigid instruction.
     4) The one or two caveats a decision-maker must hear — usually what could NOT be judged from a static screenshot or from the context given, and would change the picture if known.
   Be direct and concrete; be honest about uncertainty without hedging for its own sake. Cut any sentence only an analyst would care about.

⚠️ TRAP NAME VALIDATION — NON-NEGOTIABLE:
Every `trap_name` in critical_issues, moderate_issues, minor_issues, and potential_issues MUST be one of these exact names, verbatim:
{trap_names_line}
Do not invent, abbreviate, combine, or extend a name. If something genuinely maps to no canonical trap, place it in potential_issues with the observation and leave trap_name to the closest fit — never invent a name. Technical failures go to bugs_detected.

🖼️ REGION CROPS — INCLUDE SELECTIVELY:
`regions` is a LIST of bounding boxes — one entry per cited instance. Each entry has `screen_index` (0-based: 0 = the first SCREEN labeled above; use 0 when only one screen was provided), `x`/`y`/`width`/`height` (normalized 0.0–1.0, origin top-left) tightly enclosing the specific element that exhibits the trap, and a `caption` stating what the crop shows and how it illustrates the finding. Use ONE entry for a single-location finding; for a cross-screen finding (the same element differing across screens, e.g. INCONSISTENT APPEARANCE), include one entry PER screen it appears on (G6 per-instance enumeration). Include a crop only when it is genuine visual evidence; omit `regions` entirely when the finding is about an absence, is systemic, or cannot be cleanly bounded.

⚠️ MUTUAL EXCLUSIVITY:
A trap is either reported as an issue OR listed in coverage notes — never both. Before submitting, remove from traps_checked_not_found any trap that appears in a findings array.

Submit your analysis using the ui_analysis_report tool, populating the fields as specified above."""

    return prompt.replace("{trap_names_line}", trap_names_line)


def _build_twopass_detection_system(trap_names_line: str) -> str:
    """
    Mechanics-only system prompt for the two-pass DETECTION pass (new KBs).

    Pass 1's job is RECALL: surface every place any trap might occur so a later
    adjudication pass (which sees the full trap definitions) can confirm, dismiss,
    or reclassify each candidate. This prompt carries only output-envelope mechanics
    for the candidate list — all detection logic lives in the detection pack supplied
    as training content. It deliberately does NOT ask for severity, confidence,
    disconfirmation, or adjudication; those belong to Pass 2.
    """
    prompt = """You are an expert UI analyst applying the proprietary UI Tenets & Traps heuristic framework. This is the DETECTION pass of a two-pass analysis.

You will receive: (1) the detection procedures and scanning rules for this framework, (2) context about the users, tasks, and design format, and (3) the design artifact(s) to analyze.

📚 THE DETECTION CONTENT IS AUTHORITATIVE:
All logic for WHERE and HOW to look for each trap lives in the TRAINING CONTENT below (the GLOBAL RULES that survive into detection, each trap's detection procedure, and the TAXONOMY INDEX). Follow it exactly. Do not import detection heuristics or priority orderings from outside it.

📌 TERMINOLOGY:
The named anti-patterns of the framework (e.g. MEMORY CHALLENGE, INVISIBLE ELEMENT) are TRAPS.

⚠️ CONFIDENTIALITY & IP PROTECTION:
The framework is PROPRIETARY. Never reproduce full trap definitions in your output.

═══════════════════════════════════════════════════════════════════════
OUTPUT CONTRACT — the candidate list
═══════════════════════════════════════════════════════════════════════

Your ONLY job in this pass is recall. Scan the entire interface against every trap's detection procedure and emit a CANDIDATE LIST — one candidate per line, in exactly this format:

TRAP NAME | screen or region | element(s) involved | triggering condition observed

Rules:
- One candidate per line. Plain text only — no prose, no headings, no numbering, no bullets, no markdown table syntax.
- Emit NOTHING but candidate lines.
- Do NOT assign severity, confidence, recommendations, or disconfirmation — those belong to the adjudication pass. Do NOT pre-filter or rule candidates out here.
- The same trap may appear on several lines if it occurs in several places.
- TRAP NAME must be one of these exact canonical names, verbatim (ALL CAPS):
{trap_names_line}
  Do not invent, abbreviate, combine, or extend a name.
- Do NOT call any tool. Output only the candidate lines as plain text.

If, after a genuine whole-interface scan, no trap plausibly applies anywhere, output the single line: NONE"""
    return prompt.replace("{trap_names_line}", trap_names_line)


def _build_self_serve_trap_instruction() -> str:
    """Minimal harness instruction for the self-serve (raw-KB) profile in BY-TRAP mode.
    Carries ONLY the task and the output-schema
    contract; NO evaluation guidance (no severity criteria, no disconfirmation ordering, no
    detection priorities, no coverage instructions). The KB material is injected verbatim
    ABOVE this block and supplies all detection/evaluation reasoning. Do NOT strengthen it."""
    return (
        "Analyze the submitted artifact for the UI Traps defined in the material above, for the "
        "users, goals, and context provided. Report every trap instance you find, grouped by trap.\n\n"
        "Submit your analysis with the ui_analysis_report tool. The tool's fields:\n"
        "- critical_issues[], moderate_issues[], minor_issues[]: place each trap instance in the "
        "array for its severity. Each entry has `trap_name` (named exactly as it appears in the "
        "material above); `headline` (a plain-language statement of the specific problem); "
        "`location` (where in the artifact it occurs); `problem` (what the user experiences and "
        "why); `recommendation` (the fix direction); `severity_label` (one of: High, Medium, "
        "Low); `confidence` (one of: High, Medium, Low); and optionally `regions` (a list of "
        "boxes, each {screen_index, x, y, width, height} in 0–1 coordinates with a short caption; "
        "screen_index is 0-based, matching the SCREEN labels, 0 when one screen was provided) "
        "marking where in the artifact(s) the trap is, so a cropped image of that area can be "
        "shown.\n"
        "- summary_headline; summary_narrative.\n"
        "- positive_observations[].\n\n"
        "Omit any field you cannot ground from the material and the submitted artifact."
    )


def build_system_prompt(
    use_caching: bool = True,
    version: str = "v2.1",
    image_count: int = 1,
    training_override: Optional[str] = None,
    extra_training: Optional[str] = None,
    mode: str = "report",
    report_style: str = "trap",
    profile: str = "default",
) -> list:
    """
    Build the system prompt for Claude including training content.

    Args:
        use_caching: Whether to use prompt caching (recommended for production)
        version: Knowledge base version (default "v2.1"). Must be a new-KB version (v1.1/v2.1);
            legacy Prompting+KB versions (v1/v2) raise ValueError — their only supported route
            is KB-only (self-serve) mode, which does not call this.
        training_override: If provided, use this text as the training content instead of
            loading the full master. Two-pass mode passes sliced packs here (detection pack
            for the detect pass; core pack + flagged chunks for the adjudication pass).
        mode: "report" (default) for the adjudication/single-pass output contract, or
            "detect" for the two-pass detection candidate-list contract (new KBs only).

    Returns:
        List of system message blocks for Claude API
    """
    training_content = training_override if training_override is not None else load_training_content(version=version)

    if profile == "self-serve":
        # Raw-KB self-serve profile: inject the "never loaded"-stripped KB verbatim FIRST (so
        # "the material above" is literal), then ONLY a minimal harness instruction + the
        # output-schema contract. No evaluation guidance whatsoever — that is the point of the
        # condition. training_content is the stripped raw KB (load_training_content strips it).
        _kb_block = f"===== UI TENETS & TRAPS — REFERENCE MATERIAL =====\n\n{training_content}"
        # By-Trap is the sole rendered structure (By-Issue retired); the KB (verbatim, above)
        # supplies all evaluation reasoning — this only adds the output-shape contract.
        _instruction = _build_self_serve_trap_instruction()
        if use_caching:
            return [
                {"type": "text", "text": _kb_block, "cache_control": {"type": "ephemeral"}},
                {"type": "text", "text": _instruction, "cache_control": {"type": "ephemeral"}},
            ]
        return [{"type": "text", "text": f"{_kb_block}\n\n{_instruction}"}]

    # v1.1 shares v1's 26-trap set; v2.1 shares v2's 27-trap set.
    trap_names_line = _TRAP_NAMES_V1 if version in ("v1", "v1.1") else _TRAP_NAMES_V2

    # Legacy Prompting+KB (the old system_prompt_intro for v1/v2) is deprecated. The only
    # supported Prompting+KB path is the new-KB (v1.1/v2.1) mechanics-only scaffolds below;
    # KB-only (self-serve) is handled by the early return above. All evaluative logic lives
    # in the KB.
    if not is_new_kb(version):
        raise ValueError(
            f"Legacy Prompting+KB pathway is deprecated for version {version!r}. Supported: "
            f"new-KB (v1.1/v2.1) in Prompting+KB, or any version in KB-only (self-serve) mode."
        )
    if mode == "detect":
        full_system_prompt = _build_twopass_detection_system(trap_names_line=trap_names_line)
    else:
        full_system_prompt = _build_new_kb_system_prompt(trap_names_line=trap_names_line)

    # Multi-screen (flow) awareness for the AUTHORITATIVE system prompt — reinforces the 0-based
    # screen_index contract that the user-turn framing also states (belt-and-suspenders against a
    # 1-based mis-index). Mechanical only: labeling + field semantics. HOW to reason across screens
    # (KB G7) stays in the training content. Kept as its own block so the stable scaffold prefix
    # still hits cache across single- and multi-screen runs.
    _multi_screen_note = None
    if image_count and image_count > 1:
        _multi_screen_note = (
            f"\n\n🖥️ MULTI-SCREEN ANALYSIS: the artifact is a sequence of {image_count} screens, each "
            f"labeled [SCREEN i] in the user message — 0-based, so the first screen is [SCREEN 0] and "
            f"the last is [SCREEN {image_count - 1}]. Every `regions[].screen_index` you emit MUST be "
            f"the 0-based index of the screen that box is on."
        )

    # extra_training holds per-run variable content (two-pass adjudication's flagged-trap
    # chunks). It is appended AFTER the cached prefix and is itself left uncached: the
    # chunk set changes every run, so caching it would only pay the cache-write premium
    # for no reuse. Keeping the stable mechanics + core-pack blocks as the cached prefix
    # lets them hit cache across runs the way single mode's whole-KB block does.
    extra_block_text = (
        f"\n\n===== TRAP DETAIL FOR FLAGGED TRAPS =====\n\n{extra_training}"
        if extra_training else None
    )

    # Build system message blocks with optional caching
    if use_caching:
        # Cache the mechanics + training blocks: instructions get the same 5-minute TTL as
        # the KB. Repeated analyses in the same session (e.g. multi-page site) hit them from cache.
        blocks = [
            {
                "type": "text",
                "text": full_system_prompt,
                "cache_control": {"type": "ephemeral"}
            },
            {
                "type": "text",
                "text": f"\n\n===== UI TENETS & TRAPS TRAINING CONTENT =====\n\n{training_content}",
                "cache_control": {"type": "ephemeral"}
            }
        ]
        if extra_block_text:
            blocks.append({"type": "text", "text": extra_block_text})
        if _multi_screen_note:
            blocks.append({"type": "text", "text": _multi_screen_note})
        return blocks
    else:
        # Standard system prompt without caching
        return [
            {
                "type": "text",
                "text": (
                    f"{full_system_prompt}\n\n===== UI TENETS & TRAPS TRAINING CONTENT =====\n\n"
                    f"{training_content}{extra_block_text or ''}{_multi_screen_note or ''}"
                )
            }
        ]


def build_multi_screen_blocks(image_dicts: list) -> list:
    """Frame + interleave 0-based SCREEN labels with image content blocks for multi-screen
    (flow) analysis, so the model treats the images as ONE flow and can map each finding's
    regions[].screen_index to a specific screen. Returns a content list suitable for passing
    as build_user_message(image_data_list=...). Mechanical framing only — the flow-level
    reasoning (KB G7) lives in the knowledge base, not here."""
    n = len(image_dicts)
    blocks = [{"type": "text", "text": (
        f"The following {n} images are sequential SCREENS of a SINGLE user flow, in the order "
        f"provided. Treat them together as one flow, not {n} unrelated screenshots. Each screen "
        f"is labeled [SCREEN i] with a 0-based index; use that exact index for every "
        f"regions[].screen_index you emit."
    )}]
    for i, img in enumerate(image_dicts):
        blocks.append({"type": "text", "text": f"[SCREEN {i}]"})
        blocks.append(img)
    return blocks


def build_user_message(
    user_context: dict,
    image_data: dict = None,
    image_data_list: list = None,
    page_context: dict = None,
    is_video_analysis: bool = False,
    is_multi_frame: bool = False,
    frame_index: int = None,
    total_frames: int = None,
    verbosity: str = "standard",
    version: str = "v2.1",
    mode: str = "report",
    profile: str = "default",
) -> list:
    """
    Build the user message with context and design file.

    Args:
        user_context: Dict with 'users', 'tasks', 'format', and optionally 'expertise', 'content_type' keys
        image_data: Optional dict with 'type', 'source' for image (for Claude vision)
        page_context: Optional dict with page role info for multi-page analysis
        is_video_analysis: Whether this is part of a video analysis
        is_multi_frame: Whether this is multi-frame analysis
        frame_index: Current frame index (1-indexed) for video/multi-frame
        total_frames: Total number of frames being analyzed
        version: Knowledge base version — "v1" (26 traps) or "v2" (27 traps)

    Returns:
        List of message content blocks
    """
    trap_count = "26" if version in ("v1", "v1.1") else "27"
    # New-KB (v2.1-lineage) versions carry evaluative rules in the KB; the user-turn
    # reminders below must not re-inject legacy detection philosophy (Tier vocabulary,
    # gated procedures, the Critical/Moderate/Minor scale, page-role verdicts).
    new_kb_version = is_new_kb(version)
    # Check for expertise (optional, for backwards compatibility)
    has_expertise = bool(user_context.get('expertise'))
    # Numbering shifts by 1 if expertise is present
    content_type_num = 5 if has_expertise else 4
    page_context_num = 6 if has_expertise else 5

    # Get content type guidance
    content_type = user_context.get('content_type', 'other')
    content_guidance = CONTENT_TYPE_GUIDANCE.get(content_type, CONTENT_TYPE_GUIDANCE['other'])

    # Build content type section
    content_type_section = f"""
{content_type_num}. CONTENT TYPE: {content_guidance['name'].upper()}
   {content_guidance['description']}

   **Analysis Focus:** {content_guidance['analysis_focus']}
"""
    if content_guidance.get('limitations'):
        content_type_section += f"\n{content_guidance['limitations']}\n"

    # Add platform-specific guidance if available
    # Maps content_type to more detailed platform guidance
    platform_mapping = {
        'mobile_app': 'mobile_app',  # Generic mobile, user can specify ios/android
        'desktop_app': 'desktop_app',  # Generic desktop
        'game': 'game',
        'website': 'web',
        'pdf_document': 'pdf_document',
        'other': 'other',
    }
    # Check if user specified a more specific platform in content_type
    platform_key = content_type if content_type in SUPPORTED_PLATFORMS else platform_mapping.get(content_type, '')
    platform_section = get_platform_prompt_section(platform_key)
    if platform_section:
        content_type_section += platform_section

    # Build page context section if provided
    page_context_section = ""
    if page_context:
        # Check if we have navigation graph context
        nav_context = page_context.get('navigation_context', {})
        has_nav_context = bool(nav_context)

        # Build navigation context section
        nav_section = ""
        if has_nav_context:
            # Entry point status
            is_entry = nav_context.get('is_entry_point', False)
            depth = nav_context.get('depth_from_home', -1)

            entry_text = "YES - users may land here directly" if is_entry else f"NO - {depth} click(s) from homepage"

            # Path from home
            path_from_home = nav_context.get('path_from_home', [])
            path_text = ""
            if len(path_from_home) > 1:
                path_steps = [f"{p.get('title', 'Unknown')}" for p in path_from_home]
                path_text = f"\n   Path to this page: {' → '.join(path_steps)}"

            # CTAs already seen
            ctas_seen = nav_context.get('ctas_seen_on_path', [])
            ctas_text = ""
            if ctas_seen:
                ctas_list = [f'"{c.get("text", "")}" on {c.get("on_page", "")}' for c in ctas_seen]
                ctas_text = f"\n   CTAs users have ALREADY SEEN: {'; '.join(ctas_list)}"

            # Incoming pages
            incoming = nav_context.get('incoming_from', [])
            incoming_text = ""
            if incoming:
                incoming_list = [f"{p.get('title', '')} ({p.get('role', '')})" for p in incoming]
                incoming_text = f"\n   Pages linking HERE: {', '.join(incoming_list)}"

            # Verified CTAs on this page
            outgoing_ctas = nav_context.get('outgoing_ctas', [])
            outgoing_text = ""
            if outgoing_ctas:
                outgoing_list = [f'"{c.get("text", "")}" → {c.get("verified_destination", c.get("href", "unknown"))}' for c in outgoing_ctas]
                outgoing_text = f"\n   Verified CTAs on this page: {'; '.join(outgoing_list)}"

            nav_section = f"""
   === NAVIGATION FLOW CONTEXT (CRITICAL) ===
   Entry Point: {entry_text}{path_text}{ctas_text}{incoming_text}{outgoing_text}

   ⚠️ DO NOT flag missing CTAs that users have already seen on their path here.
   ⚠️ ONLY flag CTA destination issues if verified (see "Verified CTAs" above).
   === END NAVIGATION CONTEXT ===
"""

        # Build device context section if provided
        device_section = ""
        device_type = page_context.get('device_type')
        viewport = page_context.get('viewport')

        if device_type:
            device_constraints = {
                'mobile': """
   === MOBILE DEVICE CONSTRAINTS ===
   📱 Touch-only interface (NO hover states available)
   📱 Minimum tap target: 44×44px (Apple HIG) or 48×48dp (Material Design)
   📱 Thumb zone: Bottom 1/3 of screen is easiest to reach; top corners are hardest
   📱 Navigation: Expect hamburger menus, bottom tabs, or sticky headers
   📱 Viewport: Limited screen real estate — content must be single-column and scannable
   📱 Text: Minimum 16px for body text (smaller text is hard to read on mobile)

   ⚠️ CRITICAL MOBILE-SPECIFIC CHECKS:
   - Are tap targets large enough? (Buttons, links, form fields)
   - Are important actions within thumb reach (bottom half of screen)?
   - Is there ANY hover-dependent functionality? (This BREAKS on mobile!)
   - Is text readable without zooming?
   - Are form inputs properly sized for touch keyboards?
   === END MOBILE CONSTRAINTS ===
""",
                'tablet': """
   === TABLET DEVICE CONSTRAINTS ===
   📱 Touch-primary interface (hover may exist but shouldn't be required)
   📱 Minimum tap target: 44×44px recommended
   📱 Thumb zones: Consider both portrait and landscape orientations
   📱 Viewport: Medium screen — can support 2-column layouts but keep it simple
   📱 Text: Minimum 16px for body text

   ⚠️ TABLET-SPECIFIC CHECKS:
   - Are tap targets appropriately sized?
   - Does layout work in both portrait and landscape?
   - Are important actions easily accessible?
   - Is hover-dependent functionality avoided or has touch alternatives?
   === END TABLET CONSTRAINTS ===
""",
                'desktop': """
   === DESKTOP DEVICE CONSTRAINTS ===
   🖱️ Mouse and keyboard interface
   🖱️ Hover states are AVAILABLE and EXPECTED for interactive feedback
   🖱️ Precision: Users can click small targets (but don't make them too small)
   🖱️ Viewport: Large screen — multi-column layouts are appropriate
   🖱️ Navigation: Expect horizontal nav bars, dropdown menus, breadcrumbs
   🖱️ Keyboard: Tab navigation and keyboard shortcuts should be supported

   ⚠️ DESKTOP-SPECIFIC CHECKS:
   - Do interactive elements show hover states for feedback?
   - Are there keyboard shortcuts for power users?
   - Is the layout making good use of screen space?
   - Can users tab through forms efficiently?
   === END DESKTOP CONSTRAINTS ===
"""
            }

            device_section = device_constraints.get(device_type, "")
            if viewport:
                device_section = f"   Viewport: {viewport}\n{device_section}"

        page_context_section = f"""
{page_context_num}. PAGE CONTEXT (IMPORTANT - Read Before Analyzing):

   Page Role: {page_context.get('page_role', 'Unknown').upper()}
   Page Title: {page_context.get('page_title', 'Unknown')}
   Page URL: {page_context.get('page_url', 'Unknown')}
{device_section}{nav_section}
   Tasks RELEVANT to this page type:
   {chr(10).join('   - ' + task for task in page_context.get('relevant_tasks', []))}

   Other pages on this site: {', '.join(page_context.get('site_pages', [])) or 'Unknown'}

   ⚠️ IMPORTANT: Only evaluate tasks that are APPROPRIATE for this page role.
   Do NOT flag missing elements that belong on other page types.
   DO flag if there's no clear PATH (navigation/link) to accomplish tasks.

---
"""

    # Build video/multi-frame section
    video_section = ""
    if is_video_analysis or is_multi_frame:
        frame_info = ""
        if frame_index and total_frames:
            frame_info = f"\n   📍 Currently analyzing: Frame {frame_index} of {total_frames}\n"

        video_section = f"""
{VIDEO_ANALYSIS_GUIDANCE}
{frame_info}
{BUG_DETECTION_GUIDANCE}
---
"""

    # Build flow diagram section (image-based composite flow, not Figma)
    is_flow_diagram_image = user_context.get('input_type') == 'flow_diagram'
    flow_diagram_section = ""
    if is_flow_diagram_image:
        flow_diagram_section = f"""
{FLOW_DIAGRAM_IMAGE_GUIDANCE}
---
"""

    # Build expertise section if present
    expertise_section = ""
    if has_expertise:
        expertise_section = f"""
2. WHAT IS THEIR EXPERTISE LEVEL?
{user_context['expertise']}
"""

    extra_ctx = user_context.get('extra_context', '').strip()
    extra_context_section = f"""
ADDITIONAL CONTEXT FROM SUBMITTER:
{extra_ctx}
""" if extra_ctx else ""

    product_ctx = user_context.get('product_context', '').strip()
    product_context_section = f"""
PRODUCT CONTEXT:
{product_ctx}
""" if product_ctx else ""

    tenet_filter_raw = user_context.get('tenet_filter', '')
    if isinstance(tenet_filter_raw, list):
        tenet_list = [t.strip().upper() for t in tenet_filter_raw if t.strip()]
    else:
        tenet_list = [t.strip().upper() for t in str(tenet_filter_raw).split(',') if t.strip()]

    trap_filter_raw = user_context.get('trap_filter', '')
    if isinstance(trap_filter_raw, list):
        trap_list = [t.strip().upper() for t in trap_filter_raw if t.strip()]
    else:
        trap_list = [t.strip().upper() for t in str(trap_filter_raw).split(',') if t.strip()]

    if trap_list:
        # Trap-level filter (sub-tenet groups) — overrides tenet filter
        tenet_filter_section = f"""
⚠️ TRAP SCOPE — RESTRICTED ANALYSIS:
Evaluate ONLY the following specific traps: {', '.join(trap_list)}.
Do not report findings for any other trap. All other traps are out of scope and must be omitted from every output section.
"""
    elif tenet_list:
        tenet_filter_section = f"""
⚠️ TENET SCOPE — RESTRICTED ANALYSIS:
Evaluate ONLY the following Tenets: {', '.join(tenet_list)}.
Do not report findings for traps that fall under any other Tenet. Traps outside these Tenets should be treated as out of scope and omitted from all output sections.
"""
    else:
        tenet_filter_section = ""

    _physical_labels = {
        'desk':       'At a desk or workstation',
        'stationary': 'Stationary but away from a desk (couch, café, waiting area)',
        'moving':     'On the go — walking, commuting, or in transit',
        'vehicle':    'In a vehicle (as a passenger)',
        'outdoor':    'Outdoors or in variable conditions',
    }
    _lighting_labels = {
        'well_lit':  'Well lit — consistent indoor lighting',
        'variable':  'Variable or mixed lighting',
        'bright':    'Bright sunlight or significant glare',
        'low_light': 'Low light or dim environment',
    }
    _grip_labels = {
        'keyboard':         'Both hands on a keyboard (desktop or laptop)',
        'one_hand':         'One hand holding device, other hand interacting',
        'two_hands_thumbs': 'Two hands holding device, thumbs for input',
        'flat':             'Device resting flat on a surface',
        'hands_free':       'Hands-free — voice, mounted display, or kiosk',
    }
    _attentional_labels = {
        'fully_focused': 'Fully focused — users give this interface their complete attention with no competing demands.',
        'mostly_focused': 'Mostly focused — primarily attending to this interface but in a mildly distracting environment (open office, background noise, presence of others).',
        'divided':        'Divided attention — actively managing this interface alongside a concurrent activity (commuting, minding children, monitoring equipment or a parallel process).',
        'peripheral':     'Attention mostly elsewhere — primary focus is a real-world activity; interaction happens in brief glances and quick inputs (driving, working a register, operating machinery).',
    }
    _physical_raw    = user_context.get('physical_env',     '').strip()
    _lighting_raw    = user_context.get('lighting',         '').strip()
    _grip_raw        = user_context.get('grip_position',    '').strip()
    _attentional_raw = user_context.get('attentional_state','').strip()

    _env_lines = []
    if _physical_raw    in _physical_labels:    _env_lines.append(f"- Physical environment: {_physical_labels[_physical_raw]}")
    if _lighting_raw    in _lighting_labels:    _env_lines.append(f"- Lighting conditions: {_lighting_labels[_lighting_raw]}")
    if _grip_raw        in _grip_labels:        _env_lines.append(f"- Typical grip / body position: {_grip_labels[_grip_raw]}")
    if _attentional_raw in _attentional_labels: _env_lines.append(f"- User's attentional state: {_attentional_labels[_attentional_raw]}")

    _att_guidance = ""
    if _attentional_raw in ('divided', 'peripheral'):
        _att_guidance = """
⚠️ ATTENTION IMPACT — ELEVATE LIKELIHOOD FOR THESE TRAPS:
Given the divided or peripheral attentional state, treat the following trap likelihood assessments as elevated relative to a fully-focused user:
- Effectively Invisible Element: Elements the user would notice when focused may be missed entirely. Anything not within their brief attentional window is at high risk.
- Distraction: Any unsolicited attention capture (motion, badges, alerts, audio) is more disruptive and more likely to cause task failure when cognitive resources are already split.
- Memory Challenge: Working memory capacity is directly reduced under divided attention. Any step requiring the user to hold or recall information mid-task is at materially higher risk.
- Accidental Activation: Physical imprecision increases when attention is divided. Controls near grip points, swipe-sensitive areas, or in the path of incidental movement carry elevated accidental-activation risk.
- Feedback Failure: System feedback the user would notice when focused may go completely unregistered. Severity of any feedback absence is correspondingly higher."""

    attentional_state_section = f"""
USE ENVIRONMENT:
{chr(10).join(_env_lines)}{_att_guidance}
""" if _env_lines else ""

    verbosity_section = (
        "\n⚡ BRIEF OUTPUT MODE — ACTIVE:\n"
        "Write concise output throughout:\n"
        "- summary_narrative: 2 sentences maximum\n"
        "- headline: keep short (already required — comply strictly)\n"
        "- problem: 1–2 sentences maximum\n"
        "- recommendation: 1–2 sentences maximum\n"
        "Prioritize the most important information. Omit elaboration and examples.\n"
    ) if verbosity == "brief" else ""

    _task_list = user_context.get('task_list') or []
    _multi_task = len(_task_list) > 1
    if _multi_task:
        _task_lines = []
        _task_ids = []
        for _idx, _t in enumerate(_task_list, 1):
            _name = _t.get('name', '').strip()
            _desc = _t.get('description', '').strip()
            # Use name if provided, otherwise description — must match formatter's task_names logic
            _task_id = _name if _name else (_desc or f'Task {_idx}')
            _task_ids.append(_task_id)
            # Named task: show [name] + description. Unnamed: description IS the identifier.
            _task_lines.append(f"[{_task_id}] {_desc}" if _name else _task_id)
        _tasks_block = '\n'.join(_task_lines)
        _task_attribution = (
            "\n⚠️ MULTI-TASK ATTRIBUTION: Multiple tasks are defined above. "
            "For every finding you report — each issue in `issues`, or each per-trap finding in "
            "critical_issues / moderate_issues / minor_issues — set its `task` field to one of "
            "these exact identifiers: "
            + ', '.join(f'"{tid}"' for tid in _task_ids)
            + '. Or set it to "general" if it applies equally across all tasks or is not '
            "task-specific. Copy the identifier exactly — do not paraphrase or use the full description."
        )
    else:
        _tasks_block = user_context['tasks']
        _task_attribution = ""

    if mode == "detect":
        # Two-pass detection turn: the candidate-list output contract lives in the
        # detection system prompt; here we only cue the whole-interface recall sweep.
        closing_section = (
            "Run the DETECTION pass now. Scan the ENTIRE interface against every trap's "
            "detection procedure in your training content and emit the candidate list in the "
            "exact format your instructions specify — one candidate per line, recall over "
            "precision, no adjudication, no tool call.\n\n"
            "Begin the candidate list now."
        )
    else:
        closing_section = f"""Perform a complete UI Tenets & Traps analysis following the methodology in your training content.

Remember to:
{('- **MAP THE FLOW FIRST** — Identify and number every screen in encounter order before analyzing any traps' if is_flow_diagram_image else ('- Run every Trap Detection Procedure and adjudication rule exactly as written in your training content.' if new_kb_version else '- **WHOLE-INTERFACE SCAN FIRST (before any trap analysis)**: Scan the entire screen for every text label, icon, and interactive control that appears more than once anywhere on screen — regardless of which nav bar, panel, or component each instance is in. For each repeated element apply the GR scan protocol from your instructions (Tier 1 confirmed / Tier 2 candidate / directed inspection to potential_issues).'))}
{('- **ANCHOR EVERY FINDING TO A SCREEN** — Every location field must include the screen number and name (e.g., "Screen 2 (Item Detail) — button label")' if is_flow_diagram_image else '')}
{('- **DO NOT INCLUDE REGIONS** — Omit the `regions` field on every finding. Describe element locations in text only.' if is_flow_diagram_image else '')}
- Check all __TRAP_COUNT__ Traps systematically
{('' if new_kb_version else '- Use the gated decision procedure for Information Overload')}
- Provide specific locations where issues occur
{('- Set `confidence` to High / Medium / Low and `severity_label` to High / Medium / Low, placing each issue in the array named in your instructions.' if new_kb_version else '- Classify severity appropriately (Critical/Moderate/Minor)')}
{('' if new_kb_version else '- **RESPECT PAGE ROLES** - Only flag missing elements appropriate for this page type')}
- **RESPECT CONTENT TYPE** - Adjust analysis for {content_guidance['name']} specifics
{('- **FLOW-LEVEL TRAP ANALYSIS** — After per-screen analysis, evaluate the complete sequence for cross-screen traps (UNNECESSARY STEP, MEMORY CHALLENGE, SYSTEM AMNESIA, FEEDBACK FAILURE at transitions)' if is_flow_diagram_image else '')}
{('- **ASSESS FRAME QUALITY FIRST** - Note any mid-transition, loading, or problematic frames' if (is_video_analysis or is_multi_frame) else '')}
{('- **DETECT BUGS** - Report technical failures separately from UI traps' if (is_video_analysis or is_multi_frame) else '')}
- Note positive observations
- List traps you checked but didn't find
- Submit your complete analysis using the ui_analysis_report tool
{verbosity_section}
Begin your analysis now."""

    context_text = f"""Please analyze this UI design using the UI Tenets & Traps framework.

CONTEXT PROVIDED BY USER:

1. WHO ARE THE USERS?
{user_context['users']}
{expertise_section}
{"3" if has_expertise else "2"}. WHAT IS THE TASK BEING EVALUATED?
{_tasks_block}
{_task_attribution}

{"⚠️ IMPORTANT — MULTI-TASK SCOPE: The tasks above are specific use cases being evaluated. This product almost certainly supports other users and other goals. Your analysis should identify friction for the stated tasks, but findings and recommendations must remain proportionate to the product's broader purpose. Do not recommend changes that would strip the interface down to serve only these tasks." if _multi_task else "⚠️ IMPORTANT — TASK SCOPE: The task above is ONE specific use case being evaluated. This product almost certainly supports other users and other goals. Your analysis should identify friction for the stated task, but findings and recommendations must remain proportionate to the product's broader purpose. Do not recommend changes that would strip the interface down to serve only this one task."}
{product_context_section}{attentional_state_section}{tenet_filter_section}
{"4" if has_expertise else "3"}. DESIGN FORMAT:
{user_context['format']}
{content_type_section}
{extra_context_section}
{page_context_section}
{video_section}{flow_diagram_section}
---

{closing_section}"""

    if profile == "self-serve":
        # KB-only condition: the user turn provides ONLY the context — no content-type analysis
        # focus, platform guidance, scope framing, or reminder/closing scaffolding. All of that
        # is tool coaching that must not reach this condition; the KB (system) and screenshot
        # are the substance, and the minimal system instruction is the only task guidance.
        context_text = (
            "CONTEXT PROVIDED BY USER\n\n"
            f"WHO ARE THE USERS?\n{user_context.get('users', '')}\n\n"
            + (f"{expertise_section}\n\n" if has_expertise else "")
            + f"WHAT ARE THE TASK(S) BEING EVALUATED?\n{_tasks_block}\n\n"
            f"DESIGN FORMAT:\n{user_context.get('format', '')}\n"
        )

    # Build message content
    content = []

    # Add images first (Claude processes images before text)
    if image_data_list:
        content.extend(image_data_list)
    elif image_data:
        content.append(image_data)

    # Add the context and instructions
    content.append({
        "type": "text",
        "text": context_text.replace("__TRAP_COUNT__", trap_count)
    })

    return content


def build_flow_context_section(
    flow_context: dict = None,
    flow_summary: str = None,
    mode: str = 'screen',
) -> str:
    """
    Build the FLOW CONTEXT or FLOW ANALYSIS prompt injection.

    Args:
        flow_context:  Per-frame dict {name, reached_from, leads_to} — for screen mode
        flow_summary:  Complete flow summary string — for flow mode
        mode:          'screen' or 'flow'
    """
    if mode == 'flow' and flow_summary:
        return (
            "\nFLOW ANALYSIS:\n"
            "You are analyzing a complete user flow, not individual screens.\n"
            f"{flow_summary}\n\n"
            "Evaluate the journey end-to-end. Focus on traps that only manifest "
            "across multiple steps: UNNECESSARY STEPS, MEMORY CHALLENGE, SYSTEM "
            "AMNESIA, FEEDBACK FAILURE at transitions, AMBIGUOUS HOME. Per-screen "
            "traps are secondary — flag them only if clearly severe.\n"
        )

    if mode == 'screen' and flow_context:
        reached = '\n'.join(
            f"  - Reached from: {r['screen']} via {r['via']}"
            for r in flow_context.get('reached_from', [])
        )
        leads = '\n'.join(
            f"  - Leads to: {l['screen']} via {l['via']}"
            for l in flow_context.get('leads_to', [])
        )
        lines = '\n'.join(filter(None, [reached, leads]))
        if not lines:
            lines = "  - No connected screens detected in prototype data"
        return (
            "\nFLOW CONTEXT:\n"
            "This screen sits within a multi-screen flow.\n"
            f"{lines}\n\n"
            "Analyze this screen for traps. Use the flow context to inform your "
            "findings — an element that appears ambiguous in isolation may be clear "
            "given where the user came from, or vice versa.\n"
        )

    return ''


def build_figma_message(user_context: dict, figma_url: str) -> list:
    """
    Build message for Figma URL analysis.

    Note: This currently asks Claude to describe the approach since
    Claude cannot directly access Figma URLs. For production, you'll
    need to either:
    1. Have users export PNG from Figma
    2. Use Figma API to fetch design images
    3. Take screenshots of Figma file

    Args:
        user_context: Dict with 'users', 'tasks', 'format' keys
        figma_url: Figma file URL

    Returns:
        List of message content blocks
    """
    message = f"""I have a Figma file to analyze, but I need to convert it to an image first.

Figma URL: {figma_url}

Context:
- Users: {user_context['users']}
- Tasks: {user_context['tasks']}

Please explain how I should export this Figma file for analysis:
1. What views/screens should I export?
2. What export settings should I use?
3. Should I export individual screens or combined views?

After I export and provide the image, you'll perform the full UI Tenets & Traps analysis."""

    return [{"type": "text", "text": message}]


# Interaction Analysis Prompts
# These are used for moment-by-moment UI interaction analysis

INTERACTION_ANALYSIS_SYSTEM_PROMPT = """You are an expert UI analyst specializing in interaction feedback and state transitions.

Your task is to analyze UI interaction sequences - a series of screenshots captured before, during, and after user interactions. You will evaluate:

1. **Visual Feedback Quality** - Does the UI provide clear, immediate feedback for user actions?
2. **State Transitions** - Are changes between states clear, predictable, and reversible?
3. **Interaction Patterns** - Do interactions follow established UX patterns?
4. **Accessibility** - Are interaction states perceivable by all users?

You are trained on the UI Tenets & Traps framework. When analyzing interactions, focus on traps that are specifically detectable through interaction sequences:

**Traps Detectable Through Interaction Analysis:**
- FEEDBACK FAILURE - No visual response to user action
- ACCIDENTAL ACTIVATION - Easy to trigger unintended actions
- INVISIBLE ELEMENT - Interactive elements not visually distinct
- EFFECTIVELY INVISIBLE ELEMENT - Elements visible but not noticed due to poor visual hierarchy
- DATA LOSS - Interactions that might lose user data without warning
- SLOW OR NO RESPONSE - Delayed or missing feedback (visible in timing between screenshots)

**What You CANNOT Detect (do not flag these):**
- SYSTEM AMNESIA - Requires multiple sessions
- BAD PREDICTION - Requires seeing predictions in use
- Traps requiring broader page context (these are handled by static analysis)

Submit your findings using the interaction_analysis_report tool."""


INTERACTION_TYPE_GUIDANCE = {
    'hover': {
        'name': 'Hover State Analysis',
        'description': 'Analyzing hover/focus states on interactive elements',
        'what_to_check': [
            'Does the element have a visible hover state?',
            'Is the hover state visually distinct from the default state?',
            'Does the hover state indicate interactivity (cursor change, color shift, etc.)?',
            'Is the hover state accessible (not relying solely on color)?',
            'Are tooltips or additional information revealed on hover?',
        ],
        'common_issues': [
            'No visual change on hover (FEEDBACK FAILURE)',
            'Hover state too subtle to notice (EFFECTIVELY INVISIBLE ELEMENT)',
            'Inconsistent hover behavior across similar elements',
        ]
    },
    'click': {
        'name': 'Click Feedback Analysis',
        'description': 'Analyzing click/tap feedback and resulting state changes',
        'what_to_check': [
            'Is there immediate visual feedback when clicked?',
            'Is there a loading indicator if the action takes time?',
            'Is the resulting state change clear and expected?',
            'Can the user understand what happened?',
            'Is there a way to undo or go back if needed?',
        ],
        'common_issues': [
            'No immediate feedback on click (FEEDBACK FAILURE)',
            'Unexpected state change (ACCIDENTAL ACTIVATION)',
            'No loading indicator for slow operations (SLOW OR NO RESPONSE)',
            'Destructive action without confirmation (DATA LOSS risk)',
        ]
    },
    'form': {
        'name': 'Form Validation Analysis',
        'description': 'Analyzing form validation feedback and error states',
        'what_to_check': [
            'Are validation errors shown inline near the problematic field?',
            'Are error messages clear and actionable?',
            'Is there visual distinction between valid and invalid states?',
            'Are required fields clearly marked?',
            'Does validation happen at appropriate times (on blur, on submit)?',
        ],
        'common_issues': [
            'Errors only shown after submit (delayed FEEDBACK FAILURE)',
            'Unclear error messages (UNCOMPREHENDED ELEMENT)',
            'Form clears on error (DATA LOSS)',
            'Error styling too subtle (EFFECTIVELY INVISIBLE ELEMENT)',
        ]
    },
    'scroll': {
        'name': 'Scroll Behavior Analysis',
        'description': 'Analyzing scroll-triggered UI changes and sticky elements',
        'what_to_check': [
            'Are sticky headers/navigation consistent?',
            'Does important content remain accessible while scrolling?',
            'Are scroll position indicators present for long pages?',
            'Do scroll-triggered animations enhance understanding?',
            'Is there any content obscured by sticky elements?',
        ],
        'common_issues': [
            'Navigation disappears on scroll (INVISIBLE ELEMENT)',
            'Sticky element obscures content (PHYSICAL CHALLENGE)',
            'Jarring scroll-triggered changes (poor transition)',
            'Important CTAs scroll out of view (EFFECTIVELY INVISIBLE ELEMENT)',
        ]
    },
    'responsive': {
        'name': 'Responsive Layout Analysis',
        'description': 'Analyzing layout changes across viewport sizes',
        'what_to_check': [
            'Does layout adapt appropriately to viewport size?',
            'Are touch targets large enough on mobile?',
            'Is text readable without zooming?',
            'Are important elements accessible on all sizes?',
            'Does navigation transform appropriately (hamburger menu)?',
        ],
        'common_issues': [
            'Touch targets too small on mobile (PHYSICAL CHALLENGE)',
            'Content cut off or overlapping (INFORMATION OVERLOAD variant)',
            'Important actions hidden in mobile menu (EFFECTIVELY INVISIBLE ELEMENT)',
            'Text too small to read (PHYSICAL CHALLENGE)',
        ]
    }
}


def build_interaction_analysis_prompt(
    interaction_type: str,
    element_description: str,
    labels: list,
    user_context: dict = None
) -> str:
    """
    Build prompt for analyzing a specific interaction sequence.

    Args:
        interaction_type: Type of interaction ("hover", "click", "form", "scroll", "responsive")
        element_description: Description of the element being interacted with
        labels: List of labels for each screenshot in sequence
        user_context: Optional user context dict

    Returns:
        Prompt string for interaction analysis
    """
    guidance = INTERACTION_TYPE_GUIDANCE.get(interaction_type, {})
    type_name = guidance.get('name', f'{interaction_type.title()} Analysis')
    type_desc = guidance.get('description', f'Analyzing {interaction_type} interaction')
    checks = guidance.get('what_to_check', [])
    issues = guidance.get('common_issues', [])

    checks_text = '\n'.join(f'- {check}' for check in checks)
    issues_text = '\n'.join(f'- {issue}' for issue in issues)

    user_context_text = ""
    if user_context:
        user_context_text = f"""
USER CONTEXT:
- Users: {user_context.get('users', 'Unknown')}
- Tasks: {user_context.get('tasks', 'Unknown')}
"""

    return f"""## {type_name}

{type_desc}

**Element:** {element_description}

**Screenshot Sequence:** {', '.join(labels)}

You are viewing {len(labels)} screenshots captured during this interaction.
{user_context_text}
**What to Check:**
{checks_text}

**Common Issues to Look For:**
{issues_text}

Analyze this interaction sequence and report:
1. Whether adequate visual feedback is provided
2. Whether state transitions are clear and predictable
3. Any UI Traps detected (use trap names in ALL CAPS)
4. Accessibility concerns
5. Specific recommendations for improvement

Submit your analysis using the interaction_analysis_report tool."""


def build_interaction_message(
    images: list,
    interaction_type: str,
    element_description: str,
    labels: list,
    user_context: dict = None
) -> list:
    """
    Build complete message with images for interaction analysis.

    Args:
        images: List of image dicts (base64 encoded) for Claude vision
        interaction_type: Type of interaction
        element_description: Description of element
        labels: Screenshot labels
        user_context: Optional user context

    Returns:
        List of message content blocks (images + text)
    """
    content = []

    # Add images first (Claude processes images before text)
    for i, image in enumerate(images):
        # Add label as text before each image for context
        if i < len(labels):
            content.append({
                "type": "text",
                "text": f"**[{labels[i]}]**"
            })
        content.append(image)

    # Add analysis prompt
    prompt = build_interaction_analysis_prompt(
        interaction_type=interaction_type,
        element_description=element_description,
        labels=labels,
        user_context=user_context
    )
    content.append({
        "type": "text",
        "text": prompt
    })

    return content


def build_batch_interaction_summary_prompt(
    interaction_summaries: list,
    user_context: dict = None
) -> str:
    """
    Build prompt for summarizing all interaction findings.

    Args:
        interaction_summaries: List of individual interaction analysis results
        user_context: Optional user context

    Returns:
        Prompt for generating summary
    """
    summaries_text = ""
    for i, summary in enumerate(interaction_summaries, 1):
        summaries_text += f"""
### Interaction {i}: {summary.get('interaction_type', 'Unknown')} - {summary.get('element', 'Unknown')}
- Feedback Quality: {summary.get('feedback_quality', 'Unknown')}
- Issues Found: {', '.join(summary.get('traps_detected', [])) or 'None'}
- Severity: {summary.get('max_severity', 'None')}
"""

    return f"""## Interaction Analysis Summary

You have analyzed {len(interaction_summaries)} interactions on this page.

{summaries_text}

Synthesize these findings into:
1. Overall interaction quality assessment
2. Most critical issues requiring attention
3. Patterns across multiple interactions
4. Prioritized recommendations

Focus on issues that would most impact user experience during moment-to-moment use."""


# Navigation Flow Analysis Prompts
# These are used for analyzing CTA destinations and cross-page flows

NAVIGATION_FLOW_SYSTEM_PROMPT = """You are an expert UI analyst specializing in user flow and navigation patterns.

Your task is to analyze navigation flows - a sequence of screenshots showing a source page with a CTA and the destination page after clicking. You will evaluate:

1. **CTA Promise vs Delivery** - Does clicking the CTA lead where users expect?
2. **Flow Continuity** - Is the transition logical and predictable?
3. **Task Progress** - Does the destination advance the user's task?
4. **Recovery Options** - Can users go back or correct mistakes?

You are trained on the UI Tenets & Traps framework. When analyzing navigation flows, focus on:

**Traps Detectable Through Navigation Analysis:**
- INVITING DEAD END - CTA suggests one destination but leads somewhere else
- UNNECESSARY STEP - Extra pages between user and their goal
- IRREVERSIBLE ACTION - No way to go back from destination
- INVISIBLE ELEMENT - Important navigation not visible at destination
- AMBIGUOUS HOME - Multiple competing "home" options across pages

Submit your findings using the navigation_flow_report tool."""


NAVIGATION_TYPE_GUIDANCE = {
    'cta_verification': {
        'name': 'CTA Destination Verification',
        'description': 'Verifying that CTAs lead where users expect',
        'what_to_check': [
            'Does the CTA text accurately describe the destination?',
            'Is the destination page what users would expect?',
            'Does clicking advance the user toward their goal?',
            'Is the transition between pages smooth and logical?',
            'Can users understand where they are after the transition?',
        ],
        'common_issues': [
            '"Order Now" leads to contact form, not checkout (INVITING DEAD END)',
            '"Learn More" leads to unrelated content (INVITING DEAD END)',
            'CTA leads to error page or broken link',
            'Destination lacks clear path forward',
        ]
    },
    'flow_continuity': {
        'name': 'Flow Continuity Analysis',
        'description': 'Analyzing whether page sequences form coherent user journeys',
        'what_to_check': [
            'Is there a clear narrative from source to destination?',
            'Does the destination acknowledge the user came from somewhere?',
            'Are navigation patterns consistent between pages?',
            'Can users easily return to previous step if needed?',
            'Is progress in a multi-step flow clearly indicated?',
        ],
        'common_issues': [
            'Destination page has no back option (potential IRREVERSIBLE ACTION)',
            'User loses context of where they were (AMBIGUOUS HOME)',
            'Navigation structure changes unexpectedly (WANDERING ELEMENT)',
            'Multi-step flow lacks progress indicators',
        ]
    }
}


def build_navigation_flow_prompt(
    source_page: dict,
    destination_page: dict,
    cta_info: dict,
    user_context: dict = None
) -> str:
    """
    Build prompt for analyzing a navigation flow (source → CTA → destination).

    Args:
        source_page: Dict with url, title, role of source page
        destination_page: Dict with url, title of destination page
        cta_info: Dict with text, element_type of the CTA clicked
        user_context: Optional user context dict

    Returns:
        Prompt string for navigation flow analysis
    """
    user_context_text = ""
    if user_context:
        user_context_text = f"""
USER CONTEXT:
- Users: {user_context.get('users', 'Unknown')}
- Tasks: {user_context.get('tasks', 'Unknown')}
"""

    return f"""## Navigation Flow Analysis

**SOURCE PAGE:**
- Title: {source_page.get('title', 'Unknown')}
- URL: {source_page.get('url', 'Unknown')}
- Role: {source_page.get('role', 'Unknown')}

**CTA CLICKED:**
- Text: "{cta_info.get('text', 'Unknown')}"
- Type: {cta_info.get('element_type', 'Unknown')}

**DESTINATION PAGE:**
- Title: {destination_page.get('title', 'Unknown')}
- URL: {destination_page.get('url', 'Unknown')}
{user_context_text}
You are viewing 2 screenshots:
1. **[source_page]** - The page with the CTA before clicking
2. **[destination_page]** - The page shown after clicking the CTA

**Analyze this navigation flow for:**

1. **CTA Promise vs Delivery:**
   - Does "{cta_info.get('text', 'the CTA')}" accurately describe what users get?
   - Would a typical user expect this destination based on the CTA text?
   - If there's a mismatch, this is an INVITING DEAD END trap.

2. **Task Progress:**
   - Does this navigation advance users toward their goal?
   - Is the destination relevant to the likely user task?
   - Are there unnecessary steps between the user and their goal?

3. **Flow Continuity:**
   - Is the transition logical and easy to follow?
   - Does the destination page acknowledge where users came from?
   - Can users easily go back if they clicked by mistake?

4. **Navigation Consistency:**
   - Is the site navigation consistent between pages?
   - Can users find their way around from the destination?

Submit your analysis using the navigation_flow_report tool with:
- Whether this is a valid flow or contains a trap
- Specific trap name if applicable (INVITING DEAD END, etc.)
- Severity assessment
- Recommendation for improvement"""


def build_navigation_flow_message(
    source_image: dict,
    destination_image: dict,
    source_page: dict,
    destination_page: dict,
    cta_info: dict,
    user_context: dict = None
) -> list:
    """
    Build complete message with images for navigation flow analysis.

    Args:
        source_image: Image dict (base64) of source page
        destination_image: Image dict (base64) of destination page
        source_page: Source page info dict
        destination_page: Destination page info dict
        cta_info: CTA info dict
        user_context: Optional user context

    Returns:
        List of message content blocks
    """
    content = []

    # Add source page image with label
    content.append({
        "type": "text",
        "text": f"**[source_page]** - {source_page.get('title', 'Source Page')}"
    })
    content.append(source_image)

    # Add destination page image with label
    content.append({
        "type": "text",
        "text": f"**[destination_page]** - After clicking \"{cta_info.get('text', 'CTA')}\""
    })
    content.append(destination_image)

    # Add analysis prompt
    prompt = build_navigation_flow_prompt(
        source_page=source_page,
        destination_page=destination_page,
        cta_info=cta_info,
        user_context=user_context
    )
    content.append({
        "type": "text",
        "text": prompt
    })

    return content


# ---------------------------------------------------------------------------
# PASS 2 — ENRICHMENT PROMPTS
# ---------------------------------------------------------------------------

def build_enrichment_system_prompt() -> list:
    """
    Build the system prompt for Pass 2 (report enrichment).

    Pass 2 receives the traps already identified in Pass 1 plus the full
    book sections for those traps. Its job is to write richer, more
    educational problem descriptions and recommendations.

    Returns:
        List of system message blocks for Claude API
    """
    return [
        {
            "type": "text",
            "cache_control": {"type": "ephemeral"},
            "text": """You are a senior UI analyst writing the final client report for a UI Tenets & Traps analysis.

A detection pass has already identified which traps are present in the design.
Your job is to enrich the findings using the full framework content provided below.

⚠️ CONFIDENTIALITY & IP PROTECTION:
- The UI Tenets & Traps framework is PROPRIETARY and CONFIDENTIAL
- Reference trap concepts and names, but do NOT copy definitions verbatim
- Write as a consultant explaining findings to a client

YOUR TASK:
For each issue identified in the detection pass, write:
1. An enhanced "problem" description — specific, clear, and educational. Explain what the
   issue is, exactly where it appears in the design, and how it will impact real users.
   Draw on the full framework content to add context and precision.
2. An enhanced "recommendation" — concrete and actionable. Tell the team specifically
   what to change and why it will help users.
3. An updated "summary_narrative" — one paragraph focused on how well this design appears
   to support the user's stated goal, and what friction themes emerge from the findings.
   Do NOT mention trap counts or enumerate findings — the scorecard in the report handles counts.

WRITING RULES:
- Write in plain language. No internal framework jargon visible to the client.
- Do NOT use phrases like "GATE 0", "Pass 1 found...", "per the framework..."
- DO write as if explaining directly to the product team: what the problem is,
  where it is, and what to do about it.
- For each finding, be MORE specific than the detection pass. Reference exact UI
  elements, exact locations, and concrete user impact.
- Keep the same trap_name, tenet, location, severity, and confidence from Pass 1.
  Only enhance the "problem" and "recommendation" text.

You will submit your enriched report using the ui_analysis_report tool."""
        }
    ]


def build_enrichment_user_message(
    pass1_report: dict,
    trap_sections: dict,
    trap_images: Optional[dict] = None,
    knowledge_chunks: Optional[str] = None,
    verbosity: str = "standard",
) -> list:
    """
    Build the user message for Pass 2 enrichment.

    Args:
        pass1_report: The structured report from Pass 1 detection
        trap_sections: Dict of trap_name -> book section text for each found trap
        trap_images: Optional dict of trap_name -> list of (label, base64) tuples (book illustrations)
        knowledge_chunks: Optional pre-formatted structured knowledge base content for found traps

    Returns:
        List of message content blocks for Claude API
    """
    import json

    # Pass 2 only needs confirmed issues to enrich — strip everything else to save tokens
    findings_text = json.dumps({
        "critical_issues": pass1_report.get("critical_issues", []),
        "moderate_issues": pass1_report.get("moderate_issues", []),
        "minor_issues": pass1_report.get("minor_issues", []),
    }, separators=(',', ':'))

    # Prefer structured knowledge base chunks; fall back to raw book sections
    if knowledge_chunks:
        sections_label = "STRUCTURED KNOWLEDGE BASE CONTENT FOR IDENTIFIED TRAPS"
        sections_text = knowledge_chunks
    elif trap_sections:
        sections_label = "FULL FRAMEWORK CONTENT FOR IDENTIFIED TRAPS"
        sections_text = "\n\n".join(
            f"=== {name} ===\n{content}"
            for name, content in trap_sections.items()
        )
    else:
        sections_label = "FRAMEWORK CONTENT"
        sections_text = "(No additional framework content available for found traps.)"

    content = [
        {
            "type": "text",
            "text": f"DETECTION PASS FINDINGS:\n{findings_text}\n\n---\n\n"
                    f"{sections_label}:\n{sections_text}\n\n---",
        }
    ]

    # Append book illustrations when available
    if trap_images:
        content.append({
            "type": "text",
            "text": "\nBOOK ILLUSTRATIONS — visual examples from the UI Traps framework. "
                    "Labels like [Example 17.1] correspond to the numbered examples in the knowledge base above:",
        })
        for trap_name, images in trap_images.items():
            if images:
                content.append({"type": "text", "text": f"\n[{trap_name}]"})
                for label, img_b64 in images:
                    if label:
                        content.append({"type": "text", "text": f"[{label}]"})
                    content.append({
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": img_b64,
                        },
                    })

    brief_note = " Keep problem and recommendation fields concise — 1–2 sentences each maximum." if verbosity == "brief" else ""
    content.append({
        "type": "text",
        "text": "\nUsing the full framework content and any illustrations above, enhance the "
                "problem descriptions and recommendations for each finding. Keep the same trap "
                "names, tenets, locations, severities, and confidence levels. Only improve the "
                f"written descriptions.{brief_note}\nSubmit the enriched report using the ui_analysis_report tool.",
    })
