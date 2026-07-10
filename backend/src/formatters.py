"""
Response formatting and parsing for UI Traps Analyzer

Copyright © 2009-present UI Traps LLC. All Rights Reserved.
PROPRIETARY & CONFIDENTIAL - UI Tenets & Traps Framework
"""
import base64
import html
import json
import re
from collections import Counter, OrderedDict
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Keys whose values are base64/data-URI or internal telemetry — never HTML-escaped
# (base64's alphabet contains no HTML-special chars, so escaping is a wasteful no-op;
# telemetry is tool-generated and non-text).
_ESC_SKIP_KEYS = frozenset({
    "region_image_b64", "image_b64", "base64", "data", "_design_file",
    "_usage_last", "_twopass_meta", "usage",
})


def _escape_html_deep(obj, _key=None):
    """
    Recursively deep-copy a report/context structure, HTML-escaping every string value
    so model- and user-supplied text is safe to interpolate into the HTML report.

    Escaping is applied at the formatter boundary (see format_*_as_html) so no individual
    interpolation site can be missed. It is a no-op on control values (trap names, severity
    labels, coverage statuses — none contain HTML-special chars), so downstream branching
    logic is unaffected. Base64/telemetry keys are passed through untouched.
    """
    if isinstance(obj, str):
        if _key in _ESC_SKIP_KEYS:
            return obj
        return html.escape(obj, quote=True)
    if isinstance(obj, dict):
        return {k: _escape_html_deep(v, k) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_escape_html_deep(v, _key) for v in obj]
    return obj

try:
    from .schema import is_new_kb, normalize_relationship
except ImportError:
    from schema import is_new_kb, normalize_relationship

TENET_COLORS = {
    "UNDERSTANDABLE": "#2B4C6F",
    "COMFORTABLE":    "#D1492E",
    "RESPONSIVE":     "#E0AE22",
    "EFFICIENT":      "#AF1C66",
    "ACCURATE":       "#45A24C",
    "PROTECTIVE":     "#642FA1",
    "HABITUATING":    "#1F7DA8",
    "BEAUTIFUL":      "#E37209",
    # v1-only Tenets (the v1 deck splits what v2 folded into PROTECTIVE). Colors are tool
    # DISPLAY (the card deck defines no hex); kept in the PROTECTIVE purple family, distinct.
    "FORGIVING":      "#7A3FB0",
    "DISCREET":       "#4A3A8C",
}

# Canonical tenet → trap ordering for the coverage matrix
TENETS_AND_TRAPS = [
    ("UNDERSTANDABLE", [
        "INVISIBLE ELEMENT", "EFFECTIVELY INVISIBLE ELEMENT", "DISTRACTION",
        "UNCOMPREHENDED ELEMENT", "INVITING DEAD END", "POOR GROUPING",
        "FORCED SYNTAX", "MEMORY CHALLENGE", "FEEDBACK FAILURE",
    ]),
    ("COMFORTABLE", ["PHYSICAL CHALLENGE", "ACCIDENTAL ACTIVATION"]),
    ("RESPONSIVE", ["SLOW OR NO RESPONSE", "CAPTIVE WAIT"]),
    ("EFFICIENT", ["UNNECESSARY STEP(S)", "UNNECESSARY STEP", "UNNECESSARY STEPS", "INFORMATION OVERLOAD", "SYSTEM AMNESIA"]),
    ("ACCURATE", ["BAD PREDICTION", "INCORRECT INFORMATION"]),
    ("PROTECTIVE", ["IRREVERSIBLE ACTION", "UNWANTED DISCLOSURE", "DATA LOSS"]),
    ("HABITUATING", [
        "GRATUITOUS REDUNDANCY", "VARIABLE OUTCOME", "WANDERING ELEMENT",
        "INCONSISTENT APPEARANCE", "AMBIGUOUS HOME",
    ]),
    ("BEAUTIFUL", ["POOR AESTHETIC", "UNATTRACTIVE APPEARANCE"]),
]


# Default explanations for traps that cannot be assessed from static screenshots.
# Used as a fallback when the AI omits the `reason` field on a testable:false item.
_UNTESTABLE_REASON_DEFAULTS: Dict[str, str] = {
    "INVISIBLE ELEMENT": "Requires a complete inventory of every system interaction, including those not visible in a single screenshot — static analysis is explicitly insufficient for this Trap.",
    "EFFECTIVELY INVISIBLE ELEMENT": "Requires knowledge of each user's prior learning history and moment-to-moment attentional goals, which cannot be inferred from a static image.",
    "DISTRACTION": "Requires knowing users' goals both inside and outside the product at the time of use — this is context-dependent and cannot be determined from a screenshot.",
    "UNCOMPREHENDED ELEMENT": "Comprehensibility is user-dependent, not interface-inherent. Requires knowing what conventions and labels the target users have and have not previously encountered.",
    "INVITING DEAD END": "What constitutes a plausible wrong path depends entirely on user mental models. Requires user research or usability testing to identify which paths look attractive but lead nowhere.",
    "MEMORY CHALLENGE": "Requires knowing what information users must retain across sessions and whether the system supports recall. Cannot be assessed from a single screen in isolation.",
    "PHYSICAL CHALLENGE": "Not detectable from static design files. Requires testing on real hardware, in real-world environments, with representative users — particularly important for mobile and wearable surfaces.",
    "ACCIDENTAL ACTIVATION": "Not detectable from static design files. Requires hands-on testing in realistic use conditions to identify which controls are triggered unintentionally during normal interaction.",
    "FEEDBACK FAILURE": "Requires performing actions and observing system responses over time. A static before-state screenshot cannot reveal whether the system confirms, acknowledges, or fails to respond to user actions.",
    "SLOW OR NO RESPONSE": "Actual response times require live performance measurement under realistic network and device conditions. Perceived slowness also requires user observation, not structural analysis.",
    "CAPTIVE WAIT": "Requires attempting to skip or advance through the wait to determine whether users are truly captive. Not observable from a static screenshot of the waiting state.",
    "IRREVERSIBLE ACTION": "Requires observing the consequences of actions after they are taken. A before-state screenshot cannot reveal whether a committed action can be undone.",
    "DATA LOSS": "Requires testing failure modes — unexpected shutdowns, session timeouts, network interruptions — none of which are visible in a normal-state screenshot.",
    "SYSTEM AMNESIA": "Requires knowledge of the underlying data model and what contextual information the system retains or discards between sessions and interactions.",
    "VARIABLE OUTCOME": "Requires testing the same interaction across different device states, user roles, or environmental contexts to confirm whether results are inconsistent.",
    "WANDERING ELEMENT": "Requires comparing the same UI element across multiple pages or screens to determine whether its position or behaviour is consistent.",
    "INCONSISTENT APPEARANCE": "Requires comparing the same component across multiple screens or interaction states. A single screenshot cannot confirm cross-screen visual consistency.",
    "AMBIGUOUS HOME": "Requires seeing the full information architecture across multiple sections to determine whether the structural 'home' is clear to users.",
    "UNWANTED DISCLOSURE": "Requires understanding the social and physical contexts in which the product is used — who might be able to see the screen, and what information would be inappropriate in those contexts.",
    "POOR AESTHETIC": "Aesthetic quality involves cultural, demographic, and contextual judgement that cannot be reliably assessed through structural analysis of a static design file alone.",
    "UNATTRACTIVE APPEARANCE": "Aesthetic quality involves cultural, demographic, and contextual judgement that cannot be reliably assessed through structural analysis of a static design file alone.",
}


def _untestable_reason(trap_name: str, claude_reason: str | None) -> str:
    """Return the best available explanation for a testable:false trap item."""
    if claude_reason and claude_reason.strip() and claude_reason.strip() != 'Requires additional context to evaluate.':
        return claude_reason.strip()
    normalized = _normalize_trap_name(trap_name)
    return _UNTESTABLE_REASON_DEFAULTS.get(normalized, 'Requires additional screenshots, interaction data, or live testing to evaluate.')


def _normalize_trap_name(name: str) -> str:
    name = (name or "").upper()   # tolerate None/'' (a present-but-null trap_name must not crash)
    name = re.sub(r'\(S\)', 'S', name)           # STEP(S) -> STEPS
    name = re.sub(r'\s*\([^)]*\)\s*', ' ', name) # strip other parentheticals
    return re.sub(r'\s+', ' ', name).strip()


# Reverse lookup: normalized trap name → Tenet (upper), v2 lineage. v1 / v1.1 do NOT use this —
# they read the FROZEN v1.0 map from the KB at runtime (see _tenet_for → load_v1_trap_tenet_map),
# so there is no hand-maintained v1 copy to drift.
_TRAP_TO_TENET: Dict[str, str] = {
    _normalize_trap_name(trap): tenet
    for tenet, traps in TENETS_AND_TRAPS
    for trap in traps
}


def _tenet_for(trap_name: str, fallback_tenet: str = '', version: str | None = None) -> str:
    """Return the Tenet name (upper) for a trap name (fallback if not found).

    version selects the lineage: v1 / v1.1 read the FROZEN v1.0 card-deck map FROM THE KB
    (knowledge_extractor.load_v1_trap_tenet_map — ONE source of truth, parsed once + cached, no
    tool copy); everything else reads the v2 table. Passing the wrong version to a v1 render is
    the taxonomy leak this guards against."""
    if fallback_tenet:
        return fallback_tenet.upper()
    nm = _normalize_trap_name(trap_name)
    if version in ("v1", "v1.1"):
        try:
            from .knowledge_extractor import load_v1_trap_tenet_map
        except ImportError:
            from knowledge_extractor import load_v1_trap_tenet_map
        return load_v1_trap_tenet_map().get(nm, '')
    return _TRAP_TO_TENET.get(nm, '')


def _tenet_pill_html(trap_name: str, tenet: str) -> str:
    """Render a trap name as a tenet-colored pill span."""
    color = TENET_COLORS.get(tenet.upper(), '#4a4744')
    return (
        f"<span class='tenet-pill' style='background:{color};'>"
        f"{trap_name.upper()}</span>"
    )


# ── Trap card images ──────────────────────────────────────────────────────────
_TRAP_CARDS_DIR = Path(__file__).parent.parent / 'data' / 'trap_cards'

_TRAP_CARD_FILENAMES: Dict[str, str] = {
    "INVISIBLE ELEMENT":             "Final_op1_understandable_01_front.png",
    "EFFECTIVELY INVISIBLE ELEMENT": "Final_op1_understandable_02_front.png",
    "DISTRACTION":                   "Final_op1_understandable_03_front.png",
    "UNCOMPREHENDED ELEMENT":        "Final_op1_understandable_04_front.png",
    "INVITING DEAD END":             "Final_op1_understandable_05_front.png",
    "POOR GROUPING":                 "Final_op1_understandable_06_front.png",
    "FORCED SYNTAX":                 "Final_op1_understandable_07_front.png",
    "MEMORY CHALLENGE":              "Final_op1_understandable_08_front.png",
    "FEEDBACK FAILURE":              "Final_op1_understandable_09_front.png",
    "PHYSICAL CHALLENGE":            "Final_op1_comfortable_01_front.png",
    "ACCIDENTAL ACTIVATION":         "Final_op1_comfortable_02_front.png",
    "SLOW OR NO RESPONSE":           "Final_op1_responsive_01_front.png",
    "CAPTIVE WAIT":                  "Final_op1_responsive_02_front.png",
    "UNNECESSARY STEPS":             "Final_op1_efficient_01_front.png",
    "INFORMATION OVERLOAD":          "Final_op1_efficient_02_front.png",
    "SYSTEM AMNESIA":                "Final_op1_efficient_03_front.png",
    "BAD PREDICTION":                "Final_op1_accurate_02_front.png",
    "INCORRECT INFORMATION":         "Final_op1_accurate_01_front.png",
    "IRREVERSIBLE ACTION":           "Final_op1_protective_01_front.png",
    "UNWANTED DISCLOSURE":           "Final_op1_protective_02_front.png",
    "DATA LOSS":                     "Final_op1_protective_03_front.png",
    "GRATUITOUS REDUNDANCY":         "Final_op1_habituating_01_front.png",
    "VARIABLE OUTCOME":              "Final_op1_habituating_02_front.png",
    "WANDERING ELEMENT":             "Final_op1_habituating_03_front.png",
    "INCONSISTENT APPEARANCE":       "Final_op1_habituating_04_front.png",
    "AMBIGUOUS HOME":                "Final_op1_habituating_05_front.png",
    "POOR AESTHETIC":                "Final_op1_beautiful_01_front.png",
    # v1-lineage names share their v2 counterpart's card art (so v1.0 By-Trap gets full coverage).
    "UNNECESSARY STEP":              "Final_op1_efficient_01_front.png",
    "UNATTRACTIVE APPEARANCE":       "Final_op1_beautiful_01_front.png",
}


def _load_trap_card_images() -> Dict[str, str]:
    """Load all trap card PNGs as base64 data URIs at module import time."""
    result: Dict[str, str] = {}
    for raw_name, filename in _TRAP_CARD_FILENAMES.items():
        norm = _normalize_trap_name(raw_name)
        path = _TRAP_CARDS_DIR / filename
        try:
            data = base64.b64encode(path.read_bytes()).decode('ascii')
            result[norm] = f"data:image/png;base64,{data}"
        except OSError:
            pass
    return result


_TRAP_CARD_B64: Dict[str, str] = _load_trap_card_images()


def _get_card_img(trap_name: str) -> Optional[str]:
    """Return the base64 data URI for a trap card image, or None if not found."""
    return _TRAP_CARD_B64.get(_normalize_trap_name(trap_name))


def _cap_terms(text: str) -> str:
    """Capitalize 'trap(s)' and 'tenet(s)' as words wherever they appear in body text."""
    if not text:
        return text
    text = re.sub(r'\btraps?\b', lambda m: m.group(0).capitalize(), text, flags=re.IGNORECASE)
    text = re.sub(r'\btenets?\b', lambda m: m.group(0).capitalize(), text, flags=re.IGNORECASE)
    return text


def _build_trap_matrix_html(report: Dict[str, Any]) -> str:
    """Build an HTML table showing confirmed issue counts by trap and severity."""
    counts: Dict[str, Dict[str, int]] = {'critical': {}, 'moderate': {}, 'minor': {}}
    for sev, field in [('critical', 'critical_issues'), ('moderate', 'moderate_issues'), ('minor', 'minor_issues')]:
        for issue in report.get(field, []):
            norm = _normalize_trap_name(issue.get('trap_name', ''))
            if norm:
                counts[sev][norm] = counts[sev].get(norm, 0) + 1

    rows = []
    for tenet, traps in TENETS_AND_TRAPS:
        for i, trap in enumerate(traps):
            norm = _normalize_trap_name(trap)
            c = counts['critical'].get(norm, 0)
            m = counts['moderate'].get(norm, 0)
            mi = counts['minor'].get(norm, 0)
            total = c + m + mi
            row_class = ' class="has-issues"' if total > 0 else ''
            cells = (
                f"<td class='trap-name'>{trap}</td>"
                f"<td class='count critical'>{c or ''}</td>"
                f"<td class='count moderate'>{m or ''}</td>"
                f"<td class='count minor'>{mi or ''}</td>"
                f"<td class='count total'>{total or ''}</td>"
            )
            if i == 0:
                tenet_cell = f"<td class='tenet-cell' rowspan='{len(traps)}'>{tenet}</td>"
                rows.append(f"<tr{row_class}>{tenet_cell}{cells}</tr>")
            else:
                rows.append(f"<tr{row_class}>{cells}</tr>")

    return (
        "<div class='trap-matrix'>"
        "<h2>Trap Coverage Matrix</h2>"
        "<table class='trap-matrix-table'>"
        "<thead><tr>"
        "<th>Tenet</th><th>Trap</th>"
        "<th class='count-col'>&#128308; Critical</th>"
        "<th class='count-col'>&#128993; Moderate</th>"
        "<th class='count-col'>&#128309; Minor</th>"
        "<th class='count-col'>Total</th>"
        "</tr></thead>"
        "<tbody>" + "\n".join(rows) + "</tbody>"
        "</table></div>"
    )


def parse_tasks(tasks_str: str) -> list:
    """Extract individual tasks from a free-form tasks string.

    Handles numbered lists (1) X  2) Y), preamble text ("there are two tasks:"),
    semicolons, and bare "and"-joined items. Returns a list of clean task strings.
    """
    if not tasks_str or tasks_str.strip() in ('', 'N/A'):
        return [tasks_str or 'N/A']

    s = tasks_str.strip()

    # Strip common preamble patterns before the actual task list
    preamble = re.match(
        r'^.*?\btasks?\b.*?(?:assess|include|are|consider)[:\s]+',
        s, re.IGNORECASE
    )
    if preamble:
        s = s[preamble.end():].strip()

    # Find numbered markers: "1)", "2)", "1.", "2." — but NOT inside "(e.g."
    markers = list(re.finditer(r'(?<!\()(?<!\w)(\d+)[.)]\s+', s))
    if len(markers) >= 1:
        tasks = []
        # Content before the first numbered marker (may be an implicit "task 1")
        if markers[0].start() > 0:
            pre = s[:markers[0].start()].strip()
            pre = re.sub(r'[\s,;]+(?:and|or)?\s*$', '', pre, flags=re.IGNORECASE).strip()
            if pre:
                tasks.append(pre)
        for i, marker in enumerate(markers):
            start = marker.end()
            end = markers[i + 1].start() if i + 1 < len(markers) else len(s)
            task_text = s[start:end].strip()
            task_text = re.sub(r'[\s,;]+(?:and|or)?\s*$', '', task_text, flags=re.IGNORECASE).strip()
            if task_text:
                tasks.append(task_text)
        if len(tasks) >= 2:
            return tasks

    # Semicolon-separated
    if ';' in s:
        parts = [t.strip() for t in s.split(';') if t.strip()]
        if len(parts) >= 2:
            return parts

    return [tasks_str.strip()]


_USERS_LABELS = [
    'Experience with product:',
    'Tech savviness:',
    'Frequency of use:',
    'Experience with similar interfaces:',
]


def _parse_users_string(users_raw: str):
    """Parse a joined users string into (description, [(label, value), ...]).

    The string is assembled as "Free text desc. Label: value. Label: value."
    Returns the unlabeled description first, then each structured field.
    """
    if not users_raw or users_raw == 'N/A':
        return users_raw, []

    first_pos = len(users_raw)
    for label in _USERS_LABELS:
        pos = users_raw.find(label)
        if pos != -1 and pos < first_pos:
            first_pos = pos

    desc = users_raw[:first_pos].strip().rstrip('.')
    parts = []
    remainder = users_raw[first_pos:]
    for label in _USERS_LABELS:
        pos = remainder.find(label)
        if pos == -1:
            continue
        end_pos = len(remainder)
        for other in _USERS_LABELS:
            other_pos = remainder.find(other, pos + len(label))
            if other_pos != -1 and other_pos < end_pos:
                end_pos = other_pos
        value = remainder[pos + len(label):end_pos].strip().rstrip('. ')
        if value:
            parts.append((label.rstrip(':'), value))
    return desc, parts


def parse_claude_response(response_text: str) -> Dict[str, Any]:
    """
    Parse Claude's JSON response into structured report.

    Args:
        response_text: Raw text from Claude API

    Returns:
        Parsed report dictionary

    Raises:
        ValueError: If response is not valid JSON
    """
    # Try to extract JSON from response (in case Claude added extra text)
    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)

    if json_match:
        json_text = json_match.group(0)
    else:
        json_text = response_text

    try:
        report = json.loads(json_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse Claude response as JSON: {e}\n\nResponse: {response_text[:500]}")

    # Validate required fields
    required_fields = ['summary_headline', 'summary_narrative', 'critical_issues', 'moderate_issues',
                       'minor_issues', 'positive_observations', 'traps_checked_not_found']

    for field in required_fields:
        if field not in report:
            raise ValueError(f"Missing required field in response: {field}")

    return report


def format_report_as_markdown(report: Dict[str, Any], user_context: Dict[str, str] = None,
                              kb_version: str = None) -> str:
    """
    Format the report as Markdown for display or export.

    Args:
        report: Parsed report dictionary
        user_context: Optional context info to include in header

    Returns:
        Formatted markdown string
    """
    md = []

    # Header
    md.append("# UI Tenets & Traps Analysis Report")
    md.append("")

    # Design name/title (from context or default)
    if user_context and user_context.get('design_name'):
        md.append(f"## {user_context['design_name']}")
        md.append("")

    md.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
    md.append("")

    # Context (if provided)
    if user_context:
        md.append("## Context")
        md.append("")
        if user_context.get('chat_context_used'):
            md.append("_↺ Re-analyzed with chat clarifications_")
            md.append("")
        if user_context.get('design_name'):
            md.append(f"**Name of analysis:** {user_context['design_name']}")
            md.append("")
        md.append(f"**Users:** {user_context.get('users', 'N/A')}")
        md.append("")

        # Format tasks as bulleted list
        raw_tasks = user_context.get('tasks', 'N/A')
        task_list = parse_tasks(raw_tasks)
        md.append("**User's goal(s):**")
        for task in task_list:
            md.append(f"- {task}")
        md.append("")
        md.append("---")
        md.append("")

    # Summary — scorecard + headline + narrative
    md.append("## Summary")
    md.append("")

    _new_kb_md = is_new_kb(kb_version)
    if _new_kb_md:
        # New-KB severity ladder (High/Medium/Low), counted by severity_label.
        # Any legacy "Critical" label collapses into High.
        _ladder = {'High': 0, 'Medium': 0, 'Low': 0}
        _fb = {'critical_issues': 'High', 'moderate_issues': 'Medium', 'minor_issues': 'Low'}
        _lbl_norm = {'critical': 'High', 'high': 'High', 'medium': 'Medium', 'low': 'Low'}
        for _arr in ('critical_issues', 'moderate_issues', 'minor_issues'):
            for _i in report.get(_arr) or []:
                _raw = (_i.get('severity_label') if isinstance(_i, dict) else None) or _fb[_arr]
                _lbl = _lbl_norm.get(str(_raw).strip().lower(), _fb[_arr])
                _ladder[_lbl] += 1
        md.append("| High | Medium | Low |")
        md.append("|:---:|:---:|:---:|")
        md.append(f"| {_ladder['High'] or '—'} | {_ladder['Medium'] or '—'} | {_ladder['Low'] or '—'} |")
        md.append("")
    else:
        n_high = len(report.get('critical_issues', []))
        n_moderate = len(report.get('moderate_issues', []))
        n_low = len(report.get('minor_issues', []))
        n_potential = len(report.get('potential_issues', []))
        md.append("| | High Severity | Moderate Severity | Low Severity |")
        md.append("|---|:---:|:---:|:---:|")
        md.append(f"| Higher confidence | {n_high or '—'} | {n_moderate or '—'} | {n_low or '—'} |")
        md.append(f"| Lower confidence | — | — | {n_potential or '—'} |")
        md.append("")

    headline = report.get('summary_headline', '')
    narrative = report.get('summary_narrative', '')
    if headline:
        md.append(f"**{headline}**")
        md.append("")
    if narrative:
        md.append(narrative)
        md.append("")

    # Traps Found — sorted by severity, then confidence within severity
    conf_order = {"high": 0, "medium": 1, "low": 2}
    all_confirmed_md = (
        [('critical', 'High', i) for i in report.get('critical_issues', [])] +
        [('moderate', 'Moderate', i) for i in report.get('moderate_issues', [])] +
        [('minor', 'Low', i) for i in report.get('minor_issues', [])]
    )
    sorted_md = []
    for sev_key in ('critical', 'moderate', 'minor'):
        group = [(s, sl, i) for s, sl, i in all_confirmed_md if s == sev_key]
        group.sort(key=lambda x: conf_order.get((x[2].get('confidence') or 'low').lower(), 2))
        sorted_md.extend(group)

    md.append("## Traps Found")
    md.append("")
    if sorted_md:
        for sev_class, sev_label, issue in sorted_md:
            # Frame reference
            if 'frame_index' in issue:
                md.append(f"*Frame {issue['frame_index']}*")
                md.append("")
            elif 'frame' in issue:
                md.append(f"*{issue['frame']}*")
                md.append("")
            # Headline
            if issue.get('headline'):
                md.append(f"### {_cap_terms(issue['headline'])}")
                md.append("")
            # Meta — prefer the new-KB ladder level when present
            conf = issue.get('confidence', '')
            _sl = (issue.get('severity_label') if _new_kb_md else None) or sev_label
            meta = f"{(issue.get('trap_name') or '').upper()} · {(issue.get('tenet') or '').upper()} · {_sl} severity"
            if conf:
                meta += f" · {conf.title()} confidence"
            md.append(f"*{meta}*")
            md.append("")
            # Finding
            if issue.get('problem'):
                md.append("**Finding**")
                md.append("")
                md.append(_cap_terms(issue['problem']))
                md.append("")
            # Recommendation
            if issue.get('recommendation'):
                md.append("**Recommendation**")
                md.append("")
                md.append(_cap_terms(issue['recommendation']))
                md.append("")
            md.append("---")
            md.append("")
    else:
        md.append("*No confirmed traps found ✓*")
        md.append("")

    # Positive Observations
    md.append("## ✅ Positive Observations")
    md.append("")
    if report.get('positive_observations'):
        for obs in report['positive_observations']:
            md.append(f"- {obs}")
        md.append("")
    else:
        md.append("*None noted*")
        md.append("")

    # Bugs Detected (Technical Issues)
    if report.get('bugs_detected') and len(report['bugs_detected']) > 0:
        md.append("## 🐛 Technical Bugs Detected")
        md.append("")
        md.append("*These are technical issues or broken states, not UI Traps. They represent system failures that should be fixed regardless of usability.*")
        md.append("")
        for bug in report['bugs_detected']:
            md.append(f"**Bug Type:** {bug.get('bug_type', 'unknown').replace('_', ' ').title()}")
            md.append("")
            md.append(f"**Where:** {bug.get('location', 'N/A')}")
            md.append("")
            md.append(f"**Description:** {bug.get('description', 'N/A')}")
            md.append("")
            if bug.get('possible_cause'):
                md.append(f"**Possible Cause:** {bug['possible_cause']}")
                md.append("")
            md.append(f"*Confidence: {bug.get('confidence', 'medium')}*")
            md.append("")

    # Potential Traps / Items for Review
    if report.get('potential_issues') and len(report['potential_issues']) > 0:
        md.append("## ⚠️ Potential Traps - Items for Review")
        md.append("")
        md.append("*These items might be traps but require human judgment to confirm. The AI observed something potentially problematic but lacks context to definitively classify it.*")
        md.append("")
        for issue in report['potential_issues']:
            md.append(f"**Trap Detected:** **{issue.get('trap_name', 'UNKNOWN').upper()}** (Potential)")
            md.append("")
            md.append(f"**Tenet:** {issue.get('tenet', 'N/A').upper()}")
            md.append("")
            md.append(f"**Where:** {_cap_terms(issue.get('location', 'N/A'))}")
            md.append("")
            md.append(f"**Observation:** {_cap_terms(issue.get('observation', issue.get('problem', 'N/A')))}")
            md.append("")
            md.append(f"**Why Uncertain:** {_cap_terms(issue.get('why_uncertain', 'Requires human review'))}")
            md.append("")
            md.append(f"*Confidence: {issue.get('confidence', 'low')} - Requires human review*")
            md.append("")

    # Cross-Frame Issues (for video/multi-frame analysis)
    if report.get('cross_frame_issues') and len(report['cross_frame_issues']) > 0:
        md.append("## 🔄 Cross-Frame Issues")
        md.append("")
        md.append("*These issues were detected by comparing element positions across multiple frames:*")
        md.append("")
        for issue in report['cross_frame_issues']:
            md.append(f"**{issue.get('trap_name', 'WANDERING ELEMENT')}**")
            md.append("")
            md.append(f"**Tenet:** {issue.get('tenet', 'HABITUATING')}")
            md.append("")
            md.append(f"**Element:** {issue.get('element_description', 'UI element')}")
            md.append("")
            md.append(f"**Locations Found:** {', '.join(issue.get('locations_found', []))}")
            md.append("")
            md.append(f"**Problem:** {issue.get('problem', 'N/A')}")
            md.append("")
            # Show frame timeline
            if issue.get('frame_occurrences'):
                md.append("**Timeline:**")
                for occ in issue['frame_occurrences']:
                    timestamp_str = f" ({occ['timestamp']:.1f}s)" if occ.get('timestamp') is not None else ""
                    md.append(f"  - Frame {occ['frame_index']}{timestamp_str}: {occ.get('location', 'unknown')}")
                md.append("")
            md.append(f"**Recommendation:** {issue.get('recommendation', 'Maintain consistent element placement.')}")
            md.append("")
            md.append(f"*Confidence: {issue.get('confidence', 'medium')} | Severity: {issue.get('severity', 'moderate')}*")
            md.append("")
            md.append("---")
            md.append("")

    # Frame Quality Notes (for video/multi-frame analysis)
    if report.get('frame_quality_notes') and len(report['frame_quality_notes']) > 0:
        md.append("## 🎬 Frame Quality Notes")
        md.append("")
        md.append("*Some frames were filtered out during analysis due to quality issues:*")
        md.append("")
        for note in report['frame_quality_notes']:
            issue_labels = {
                'mid_transition': 'Mid-transition',
                'partial_scroll': 'Partial scroll',
                'loading_state': 'Loading screen',
                'blank_screen': 'Blank/empty',
                'duplicate': 'Duplicate frame',
                'low_quality': 'Low quality',
                'incomplete_ui': 'Incomplete UI'
            }
            issue_label = issue_labels.get(note.get('issue'), note.get('issue', 'Unknown'))
            timestamp = note.get('timestamp')
            if timestamp is not None:
                md.append(f"- **Frame at {timestamp:.1f}s**: {issue_label} - {note.get('description', 'Skipped')}")
            else:
                md.append(f"- **Frame {note.get('frame_index', '?')}**: {issue_label} - {note.get('description', 'Skipped')}")
        md.append("")

    # Traps Not Found + Needs More Context
    raw_items = report.get('traps_checked_not_found', [])
    md_tested_ok = []
    md_untestable = []
    for item in raw_items:
        if isinstance(item, str):
            md_tested_ok.append(item)
            continue
        _nm = (item.get('trap_name') or '') if isinstance(item, dict) else ''
        if not _nm:
            continue  # skip malformed coverage entries with no trap name
        # New-KB coverage uses the G4 coverage_status label; legacy uses testable bool.
        status = item.get('coverage_status')
        if status is not None:
            if status in ('not_assessable_artifact', 'not_assessable_context'):
                md_untestable.append(item)
            else:
                md_tested_ok.append(_nm.upper())
        elif item.get('testable', True):
            md_tested_ok.append(_nm.upper())
        else:
            md_untestable.append(item)

    if md_tested_ok:
        md.append("## Traps Not Found")
        md.append("")
        md.append("*The following traps were specifically evaluated and do not appear to be present in the submitted design.*")
        md.append("")
        for trap in md_tested_ok:
            md.append(f"- {trap}")
        md.append("")

    if md_untestable:
        md.append("## Needs More Context")
        md.append("")
        md.append("*The following traps could not be fully evaluated from the submitted materials. To investigate further, consider testing the live product with representative users, reviewing additional screens in the task flow, or inspecting the underlying code.*")
        md.append("")
        for item in md_untestable:
            md.append(f"- {(item.get('trap_name') or '').upper()}")
        md.append("")

    # Footer
    md.append("---")
    md.append("")
    md.append("*Generated using UI Tenets & Traps proprietary framework*")
    md.append("")
    md.append("## ⚠️ CONFIDENTIALITY NOTICE")
    md.append("")
    md.append("**PROPRIETARY & CONFIDENTIAL:** This analysis report is provided exclusively to authorized subscribers of the UI Tenets & Traps analysis service.")
    md.append("")
    md.append("- **Copyright © 2009-present UI Traps LLC.** All Rights Reserved.")
    md.append("- The UI Tenets & Traps framework is proprietary intellectual property")
    md.append("- Reproduction, distribution, or sharing without written permission is prohibited")
    md.append("- This report is for your internal use only")
    md.append("- Unauthorized disclosure may result in termination of service and legal action")
    md.append("")
    md.append("For licensing inquiries: service@uitraps.com")

    return "\n".join(md)


def get_report_base_css() -> str:
    """Return the shared CSS used by all report HTML pages."""
    return """
        /* ── Base ── */
        html, body {
            margin: 0; padding: 0;
            font-family: 'Montserrat', 'Inter', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            font-size: 15px;
            line-height: 1.65;
            color: #111111;
            background: #ffffff;
        }
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Montserrat', 'Inter', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            color: #111111;
        }
        .ui-traps-report {
            padding: 40px 32px 60px;
            max-width: 860px;
            margin: 0 auto;
        }
        .timestamp {
            color: #8a8680;
            font-size: 0.85em;
            display: block;
            margin-bottom: 28px;
        }
        .context-section {
            padding: 0;
            border-radius: 14px;
            margin: 0 0 16px;
            border: 1px solid #e4e1dc;
            background: #ffffff;
            box-shadow: 0 1px 4px rgba(0,0,0,0.07), 0 1px 2px rgba(0,0,0,0.04);
            overflow: hidden;
        }
        .context-section > h2 {
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            color: #8a8680;
            padding: 16px 24px;
            margin: 0;
            border-bottom: 1px solid #e4e1dc;
        }
        .context-body {
            padding: 20px 24px;
            font-size: 14px;
        }
        .context-body p { margin: 0 0 8px; }
        .context-body p:last-child { margin-bottom: 0; }
        .context-body ul { margin: 4px 0 8px; padding-left: 20px; }
        .users-detail { margin: 0 0 8px; }
        .users-detail-label { margin: 0 0 8px; }
        .users-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.93em;
            border: 1px solid #e4e1dc;
            border-radius: 6px;
            overflow: hidden;
        }
        .users-table td {
            padding: 7px 12px;
            border: 1px solid #e4e1dc;
            vertical-align: top;
            line-height: 1.5;
        }
        .users-table .ut-label {
            width: 170px;
            text-align: right;
            font-size: 0.78em;
            font-weight: 700;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            color: #8a8680;
            white-space: nowrap;
            background: #faf9f7;
        }
        .users-table .ut-value { color: #2c2c2c; }
        .summary-section {
            padding: 0;
            border-radius: 14px;
            border: 1px solid #e4e1dc;
            background: #ffffff;
            box-shadow: 0 1px 4px rgba(0,0,0,0.07), 0 1px 2px rgba(0,0,0,0.04);
            margin: 0 0 24px;
            overflow: hidden;
        }
        .summary-section > h2 {
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            color: #8a8680;
            padding: 16px 24px;
            margin: 0;
            border-bottom: 1px solid #e4e1dc;
        }
        .summary-inner {
            padding: 20px 24px;
        }
        .summary-section ul {
            padding: 16px 24px 16px 40px;
            border-left: 3px solid #e05c1a;
            border-radius: 4px;
            background: #fdf1ea;
            margin: 12px 0;
        }
        .chat-context-badge {
            display: inline-block;
            font-size: 0.78em;
            color: #e05c1a;
            background: #fdf1ea;
            border: 1px solid rgba(224,92,26,0.25);
            border-radius: 100px;
            padding: 3px 10px;
            margin-bottom: 12px;
            font-weight: 600;
            letter-spacing: 0.03em;
        }
        .chat-override-section { margin-top: 12px; }
        .chat-override-list { margin: 6px 0 0; padding-left: 20px; font-size: 13px; color: #4a4744; }
        .chat-override-list li { margin-bottom: 3px; }
        .scorecard-title {
            font-size: 0.72em;
            font-weight: 700;
            letter-spacing: 0.07em;
            text-transform: uppercase;
            color: #8a8680;
            margin: 0 0 8px;
        }
        .scorecard-table {
            width: 100%;
            border-collapse: collapse;
            border-radius: 10px;
            overflow: hidden;
            border: 1px solid #e4e1dc;
            margin: 0 0 20px 0;
            font-size: 0.9em;
        }
        .scorecard-table thead th {
            background: #f7f6f4;
            color: #8a8680;
            padding: 9px 14px;
            text-align: center;
            font-weight: 600;
            font-size: 0.75em;
            letter-spacing: 0.07em;
            text-transform: uppercase;
            border-bottom: 1px solid #e4e1dc;
        }
        .scorecard-table thead th:first-child { text-align: left; color: #4a4744; }
        .scorecard-th-high     { color: #c0392b !important; }
        .scorecard-th-moderate { color: #9a7000 !important; }
        .scorecard-th-low      { color: #2980b9 !important; }
        .scorecard-th-positive { color: #27ae60 !important; }
        .scorecard-label {
            padding: 10px 14px;
            font-size: 0.85em;
            font-weight: 600;
            color: #4a4744;
            border-bottom: 1px solid #e4e1dc;
            background: #faf9f7;
        }
        .scorecard-col {
            text-align: center;
            padding: 10px 14px;
            border-bottom: 1px solid #e4e1dc;
            font-weight: 700;
            font-size: 1em;
        }
        .scorecard-val-high     { background: rgba(192,57,43,0.08);   color: #c0392b; }
        .scorecard-val-moderate { background: rgba(154,112,0,0.08);   color: #9a7000; }
        .scorecard-val-low      { background: rgba(41,128,185,0.08);  color: #2980b9; }
        .scorecard-val-positive { background: rgba(39,174,96,0.07);  color: #27ae60; }
        .scorecard-val-potential{ background: rgba(127,140,141,0.07);color: #7f8c8d; }
        .scorecard-empty        { color: #d0cdc8; }
        .summary-headline {
            font-size: 1.05em;
            font-weight: 700;
            color: #111111;
            margin: 4px 0 10px;
            line-height: 1.5;
        }
        .summary-narrative {
            font-size: 0.93em;
            color: #4a4744;
            margin: 0 0 4px;
            line-height: 1.65;
        }
        .issue-headline {
            font-size: 1em;
            font-weight: 700;
            color: #111111;
            margin: 0 0 10px;
            line-height: 1.45;
        }
        .tenet-pill {
            display: inline-block;
            font-size: 0.72em;
            font-weight: 700;
            font-family: 'Montserrat', 'Inter', system-ui, sans-serif;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            color: #ffffff;
            border-radius: 4px;
            padding: 3px 10px;
            white-space: nowrap;
            line-height: 1.5;
        }
        .issue-region-figure {
            margin: 16px 0 10px;
            width: 100%;
            max-width: 480px;
            border: 1px solid #e4e1dc;
            border-radius: 8px;
            overflow: hidden;
            background: #f7f5f2;
        }
        .issue-region-img {
            display: block;
            /* Preserve aspect ratio; never upscale small crops or overflow the card.
               Both caps apply together, so the browser scales to fit the box. */
            max-width: 100%;
            max-height: 300px;
            width: auto;
            height: auto;
            margin: 0 auto;
            object-fit: contain;
        }
        .issue-region-caption {
            display: block;
            padding: 6px 10px;
            font-size: 0.78em;
            color: #6b6764;
            font-style: italic;
            border-top: 1px solid #e4e1dc;
            background: #f7f5f2;
        }
        .issue-meta {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 0 4px;
            margin: 0 0 14px;
            font-size: 0.82em;
            color: #4a4744;
        }
        .meta-label   { color: #4a4744; }
        .meta-pipe    { color: #d0cdc8; margin: 0 4px; }
        .meta-sep     { color: #d0cdc8; margin: 0 6px; }
        .meta-tenet   { color: #4a4744; }
        .meta-severity { font-weight: 600; }
        .meta-severity.sev-critical { color: #c0392b; }
        .meta-severity.sev-moderate { color: #9a7000; }
        .meta-severity.sev-minor    { color: #2980b9; }
        .meta-confidence { color: #4a4744; }
        .meta-trap-name { font-weight: 700; font-size: 0.82em; letter-spacing: 0.04em; color: #2c2a28; }
        .issue-section { margin: 10px 0 0; }
        .issue-section-label {
            font-size: 0.78em;
            font-weight: 700;
            letter-spacing: 0.07em;
            text-transform: uppercase;
            color: #8a8680;
            margin: 0 0 4px;
        }
        .issue-section-body {
            font-size: 0.93em;
            color: #2c2c2c;
            margin: 0;
            line-height: 1.6;
        }
        .trap-name-list {
            list-style: none;
            padding: 0;
            margin: 8px 0 0;
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
        }
        .frame-ref-text {
            margin: 0;
            color: #8a8680;
            font-size: 0.85em;
        }
        .sev-dot {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 6px;
            vertical-align: middle;
            flex-shrink: 0;
        }
        .sev-dot.sev-critical { background: #c0392b; }
        .sev-dot.sev-moderate { background: #c49200; }
        .sev-dot.sev-minor    { background: #3498db; }
        .issue-card {
            background: #ffffff;
            border: 1px solid #e4e1dc;
            padding: 22px 24px;
            margin: 12px 0;
            border-radius: 14px;
            box-shadow: 0 1px 4px rgba(0,0,0,0.07), 0 1px 2px rgba(0,0,0,0.04);
            display: flex;
            align-items: flex-start;
            gap: 0;
        }
        .card-img-float {
            width: 130px;
            flex-shrink: 0;
            margin: 0 22px 0 0;
            border-radius: 8px;
            display: block;
            box-shadow: 0 2px 10px rgba(0,0,0,0.18);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            cursor: zoom-in;
            position: relative;
            z-index: 1;
        }
        .card-img-float:hover {
            transform: scale(1.8);
            transform-origin: top left;
            z-index: 100;
            box-shadow: 0 8px 28px rgba(0,0,0,0.28);
        }
        .issue-card-body {
            flex: 1;
            min-width: 0;
        }
        .finding-num {
            font-size: 0.72em;
            font-weight: 700;
            letter-spacing: 0.07em;
            text-transform: uppercase;
            color: #8a8680;
            margin: 0 0 4px;
        }
        .issue-card h3 {
            margin-top: 0;
            color: #111111;
            font-size: 1em;
            font-weight: 700;
        }
        .issue-card .tenet {
            color: #8a8680;
            font-size: 0.88em;
        }
        .issue-card .confidence {
            color: #8a8680;
            font-size: 0.82em;
            margin-top: 10px;
        }
        .issue-card .frame-info {
            background: #f7f6f4;
            color: #4a4744;
            border: 1px solid #e4e1dc;
            padding: 6px 12px;
            border-radius: 6px;
            margin: 0 0 14px 0;
            font-size: 0.88em;
            display: inline-block;
        }
        .issue-card .frame-info strong {
            color: #111111;
        }
        .frame-thumbnail-link:hover {
            transform: scale(1.05);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2) !important;
        }
        .issue-frames {
            background: #f7f6f4;
            padding: 12px;
            border-radius: 8px;
            border: 1px solid #e4e1dc;
        }
        .section-intro {
            color: #8a8680;
            font-size: 0.91em;
            margin: -6px 0 16px;
            line-height: 1.55;
        }
        .none-found {
            color: #8a8680;
            font-style: italic;
        }
        .positive-section { display: none; }
        .positives-section { margin: 24px 0; }
        .positive-card {
            padding: 18px 22px;
            border-radius: 14px;
            border: 1px solid #e4e1dc;
            border-left: 4px solid #27ae60;
            background: #ffffff;
            box-shadow: 0 1px 4px rgba(0,0,0,0.07), 0 1px 2px rgba(0,0,0,0.04);
        }
        .positive-card ul { margin: 0; padding-left: 20px; }
        .positive-card li { margin: 4px 0; font-size: 0.93em; }
        .positive-item { color: #111111; }
        h1 { font-size: 1.85em; font-weight: 800; color: #111111; letter-spacing: -0.7px; line-height: 1.2; border-bottom: none; padding-bottom: 0; margin: 0 0 6px; }
        h2 { font-size: 1.05em; font-weight: 700; color: #111111; letter-spacing: -0.2px; border-bottom: none; padding-bottom: 0; margin: 28px 0 14px; }
        h3 { font-size: 1em; font-weight: 700; color: #111111; margin: 16px 0 8px; letter-spacing: -0.1px; }
        h4 { font-size: 0.92em; font-weight: 600; color: #4a4744; margin: 12px 0 6px; }
        .potential-issues-section {
            padding: 22px 24px;
            border-radius: 14px;
            border-left: 4px solid #e05c1a;
            border: 1px solid #e4e1dc;
            background: #ffffff;
            margin: 20px 0;
            box-shadow: 0 1px 4px rgba(0,0,0,0.07), 0 1px 2px rgba(0,0,0,0.04);
        }
        .potential-issues-section .issue-card.potential {
            border-left-color: #e05c1a;
        }
        .bug-card {
            background: #ffffff;
            border: 1px solid #e4e1dc;
            border-left: 4px solid #e91e63;
            border-radius: 10px;
            padding: 16px 20px;
            margin: 12px 0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        }
        .bug-card-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 12px;
        }
        .bug-type-badge {
            font-size: 0.78em;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            background: #fce4ec;
            color: #c2185b;
            padding: 3px 10px;
            border-radius: 4px;
        }
        .bug-confidence {
            font-size: 0.78em;
            color: #8a8680;
            font-style: italic;
        }
        .bug-field {
            font-size: 0.9em;
            color: #333;
            margin: 7px 0;
            line-height: 1.5;
        }
        .confidence-group-header {
            font-size: 0.78em;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: #8a8680;
            margin: 28px 0 4px;
            padding-bottom: 8px;
            border-bottom: 1px solid #e4e1dc;
        }
        .confidence-group-header:first-of-type { margin-top: 8px; }
        .task-section-header {
            font-size: 1.05em;
            font-weight: 700;
            color: #2c2a27;
            margin: 80px 0 4px;
            padding-top: 24px;
            padding-bottom: 6px;
            border-top: 1px solid #e4e1dc;
            border-bottom: 2px solid #e4e1dc;
        }
        .task-section-desc {
            color: #8a8680;
            font-size: 0.88em;
            margin: 0 0 14px;
        }
        .traps-not-found {
            padding: 22px 24px;
            border-radius: 14px;
            border: 1px solid #e4e1dc;
            background: #ffffff;
            box-shadow: 0 1px 4px rgba(0,0,0,0.07), 0 1px 2px rgba(0,0,0,0.04);
            margin: 0 0 16px;
        }
        .traps-not-found h2 { margin: 0 0 8px; font-size: 1.05em; font-weight: 700; }
        .traps-not-found h3 {
            font-size: 0.92em;
            margin: 16px 0 8px;
            color: #111111;
            font-weight: 600;
        }
        .untestable-list {
            list-style: none;
            padding: 0;
            margin: 0;
        }
        .untestable-list li {
            padding: 7px 0;
            border-bottom: 1px solid #e4e1dc;
            font-size: 0.87em;
            color: #4a4744;
        }
        .untestable-list li:last-child { border-bottom: none; }
        .untestable-list .trap-label {
            font-weight: 600;
            color: #111111;
        }
        .untestable-note {
            font-size: 0.85em;
            color: #8a8680;
            margin: 0 0 8px;
        }
        .footer {
            margin-top: 48px;
            padding-top: 24px;
            border-top: 1px solid #e4e1dc;
        }
        .confidentiality-notice {
            border: 1px solid #e4e1dc;
            padding: 20px 24px;
            border-radius: 14px;
            margin-top: 20px;
            background: #ffffff;
            box-shadow: 0 1px 4px rgba(0,0,0,0.07), 0 1px 2px rgba(0,0,0,0.04);
        }
        .confidentiality-notice h3 {
            color: #8a6500;
            margin-top: 0;
        }
        .confidentiality-notice ul { margin: 10px 0; }
        .confidentiality-notice li { margin: 5px 0; }
        hr {
            border: none;
            border-top: 1px solid #e4e1dc;
            margin: 24px 0;
        }
        .issues-section h2, .traps-not-found h2 { margin: 0 0 4px; }
        .issues-section { margin: 24px 0; }
        .issues-section > h2, .potential-issues-section > h2 {
            margin: 0 0 4px;
        }
        .trap-matrix { margin: 30px 0; }
        .trap-matrix-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.87em;
            border-radius: 14px;
            overflow: hidden;
            border: 1px solid #e4e1dc;
        }
        .trap-matrix-table thead th {
            background: #f7f6f4;
            color: #8a8680;
            padding: 10px 14px;
            text-align: left;
            font-weight: 600;
            font-size: 0.75em;
            letter-spacing: 0.07em;
            text-transform: uppercase;
            border-bottom: 1px solid #e4e1dc;
        }
        .trap-matrix-table thead th.count-col { text-align: center; }
        .trap-matrix-table td {
            padding: 7px 14px;
            border-bottom: 1px solid #e4e1dc;
            vertical-align: middle;
        }
        .trap-matrix-table .tenet-cell {
            font-weight: 700;
            font-size: 0.75em;
            letter-spacing: 0.06em;
            background: #faf9f7;
            color: #4a4744;
            text-align: center;
            border-right: 1px solid #e4e1dc;
            white-space: nowrap;
            text-transform: uppercase;
        }
        .trap-matrix-table .trap-name {
            color: #4a4744;
            font-size: 0.85em;
        }
        .trap-matrix-table .count { text-align: center; font-weight: 600; min-width: 60px; }
        .trap-matrix-table .count.critical { color: #c0392b; }
        .trap-matrix-table .count.moderate { color: #9a7000; }
        .trap-matrix-table .count.minor { color: #2980b9; }
        .trap-matrix-table .count.total {
            color: #111111;
            border-left: 1px solid #e4e1dc;
        }
        .trap-matrix-table tr.has-issues td.trap-name { font-weight: 600; color: #111111; }
        .user-issues-section {
            margin: 30px 0;
            padding: 24px 28px;
            border-radius: 12px;
            border: 1px solid #e4e1dc;
            background: #ffffff;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }
        .user-issues-section h2 { border-bottom-color: #e05c1a; margin-top: 0; }
        .user-issues-intro { color: #8a8680; font-size: 0.91em; margin: -4px 0 18px; }
        .user-issue-card {
            background: #f7f6f4;
            border-radius: 8px;
            padding: 18px 20px;
            margin: 12px 0;
            border-left: 4px solid #d0cdc8;
            border: 1px solid #e4e1dc;
            box-shadow: none;
        }
        .user-issue-card.impact-high   { border-left-color: #c0392b; }
        .user-issue-card.impact-medium { border-left-color: #e05c1a; }
        .user-issue-card.impact-low    { border-left-color: #3498db; }
        .user-issue-header { display: flex; align-items: center; gap: 10px; margin-bottom: 6px; }
        .impact-badge {
            font-size: 0.7em; font-weight: 700; letter-spacing: 0.07em;
            padding: 3px 9px; border-radius: 100px; white-space: nowrap;
            text-transform: uppercase;
        }
        .impact-badge.high   { background: #fdecea; color: #c0392b; }
        .impact-badge.medium { background: #fdf1ea; color: #e05c1a; }
        .impact-badge.low    { background: #eaf4fd; color: #2471a3; }
        .user-issue-title { margin: 0; font-size: 1em; color: #111111; font-weight: 700; }
        .task-context { color: #8a8680; font-size: 0.87em; margin: 2px 0 10px; }
        .contributing-traps { display: flex; flex-wrap: wrap; align-items: center; gap: 6px; margin: 12px 0 8px; }
        .traps-label { font-size: 0.8em; color: #8a8680; font-weight: 600; margin-right: 2px; }
        .trap-pill {
            font-size: 0.72em; font-weight: 700; padding: 2px 9px;
            border-radius: 100px; letter-spacing: 0.04em;
        }
        .trap-pill.critical { background: #fdecea; color: #c0392b; border: 1px solid #f5c6c6; }
        .trap-pill.moderate { background: #fdf1ea; color: #e05c1a; border: 1px solid rgba(224,92,26,0.25); }
        .trap-pill.minor    { background: #eaf4fd; color: #2471a3; border: 1px solid #c6dff5; }
        .user-issue-recs strong { font-size: 0.9em; color: #111111; }
        .user-issue-recs ul { margin: 6px 0 0; padding-left: 20px; }
        .user-issue-recs li { margin: 3px 0; font-size: 0.93em; }
        .task-group-header { font-size: 0.95em; color: #4a4744; font-weight: 700; margin: 22px 0 8px; padding-bottom: 6px; border-bottom: 1px solid #e4e1dc; letter-spacing: -0.1px; }
        /* Site report extras */
        .site-stat-row {
            display: flex;
            gap: 12px;
            margin: 16px 0 24px;
            flex-wrap: wrap;
        }
        .site-stat {
            flex: 1;
            min-width: 80px;
            background: #ffffff;
            border: 1px solid #e4e1dc;
            border-radius: 12px;
            padding: 16px 12px;
            text-align: center;
            box-shadow: 0 1px 4px rgba(0,0,0,0.06);
        }
        .site-stat-num {
            font-size: 2em;
            font-weight: 800;
            line-height: 1;
            margin-bottom: 4px;
        }
        .site-stat-num.critical { color: #c0392b; }
        .site-stat-num.moderate { color: #9a7000; }
        .site-stat-num.minor    { color: #2980b9; }
        .site-stat-num.total    { color: #111111; }
        .site-stat-label {
            font-size: 0.72em;
            font-weight: 700;
            letter-spacing: 0.07em;
            text-transform: uppercase;
            color: #8a8680;
        }
        .page-card {
            background: #ffffff;
            border: 1px solid #e4e1dc;
            border-radius: 14px;
            margin: 0 0 20px;
            overflow: hidden;
            box-shadow: 0 1px 4px rgba(0,0,0,0.07), 0 1px 2px rgba(0,0,0,0.04);
        }
        .page-card-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 16px 24px;
            border-bottom: 1px solid #e4e1dc;
            background: #faf9f7;
            flex-wrap: wrap;
            gap: 8px;
        }
        .page-card-title {
            font-size: 1em;
            font-weight: 700;
            color: #111111;
            margin: 0;
        }
        .page-card-url {
            font-size: 0.82em;
            color: #8a8680;
            margin: 2px 0 0;
        }
        .page-card-url a { color: #6366f1; text-decoration: none; }
        .page-card-url a:hover { text-decoration: underline; }
        .page-role-badge {
            font-size: 0.7em;
            font-weight: 700;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            color: #ffffff;
            background: #6366f1;
            border-radius: 100px;
            padding: 4px 12px;
            white-space: nowrap;
        }
        .page-card-body { padding: 20px 24px; }
        .page-stat-row {
            display: flex;
            gap: 8px;
            margin-bottom: 16px;
            flex-wrap: wrap;
        }
        .page-stat-badge {
            font-size: 0.78em;
            font-weight: 700;
            padding: 4px 12px;
            border-radius: 100px;
        }
        .page-stat-badge.critical { background: #fdecea; color: #c0392b; }
        .page-stat-badge.moderate { background: #fdf3e0; color: #9a7000; }
        .page-stat-badge.minor    { background: #eaf4fd; color: #2471a3; }
        .no-issues-banner {
            background: #f0fdf4;
            border: 1px solid #bbf7d0;
            border-radius: 10px;
            padding: 14px 20px;
            color: #166534;
            font-size: 0.93em;
            font-weight: 600;
            text-align: center;
        }
        .screenshot-section {
            margin: 0 0 16px;
            border: 1px solid #e4e1dc;
            border-radius: 10px;
            overflow: hidden;
        }
        .screenshot-toggle {
            cursor: pointer;
            padding: 12px 16px;
            background: #f7f6f4;
            font-size: 0.85em;
            font-weight: 600;
            color: #4a4744;
            user-select: none;
            list-style: none;
        }
        .screenshot-toggle::-webkit-details-marker { display: none; }
        .screenshot-toggle::before { content: '▶  '; font-size: 0.8em; }
        details[open] .screenshot-toggle::before { content: '▼  '; }
        .screenshot-img {
            display: block;
            width: 100%;
            height: auto;
            border-top: 1px solid #e4e1dc;
        }
        .assessment-box {
            background: #fdf1ea;
            border: 1px solid rgba(224,92,26,0.3);
            border-left: 4px solid #e05c1a;
            border-radius: 10px;
            padding: 14px 20px;
            margin: 0 0 20px;
            font-size: 0.93em;
            color: #4a4744;
        }
        .assessment-box.good {
            background: #f0fdf4;
            border-color: #bbf7d0;
            border-left-color: #27ae60;
            color: #166534;
        }
    """


def format_report_as_html(
    report: Dict[str, Any],
    user_context: Dict[str, str] = None,
    analysis_settings: Dict[str, Any] = None,
) -> str:
    """
    Format the report as HTML for web display.

    Args:
        report: Parsed report dictionary
        user_context: Optional context info
        analysis_settings: Optional dict with verbosity, pass1_model, kb_version, elapsed_seconds

    Returns:
        Formatted HTML string with embedded CSS
    """
    # SECURITY: escape all model/user text once, at the boundary, so no interpolation
    # site downstream can inject markup. No-op on control values and base64. Covers
    # analysis_settings too — verbosity/pass1_model there are unvalidated Form fields.
    report = _escape_html_deep(report)
    if user_context is not None:
        user_context = _escape_html_deep(user_context)
    if analysis_settings is not None:
        analysis_settings = _escape_html_deep(analysis_settings)

    # New-KB (v2-lineage) reports use the new vocabulary: Confidence is High/Medium/Low
    # (High = "higher confidence" for grouping), and coverage is expressed with G4 labels
    # instead of the testable boolean. Legacy 'confirmed' still counts as higher confidence.
    _kb_version = (analysis_settings or {}).get('kb_version', 'v2')
    _new_kb = is_new_kb(_kb_version)

    def _is_higher_confidence(issue):
        conf = (issue.get('confidence') or '').strip().lower()
        return conf in ('high', 'confirmed') if _new_kb else conf == 'high'

    html = []

    # Add HTML document structure and CSS
    html.append("<!DOCTYPE html>")
    html.append("<html lang='en'>")
    html.append("<head>")
    html.append("<meta charset='UTF-8'>")
    html.append("<meta name='viewport' content='width=device-width, initial-scale=1.0'>")
    html.append("<title>UI Tenets & Traps Analysis Report</title>")
    html.append("<link rel='preconnect' href='https://fonts.googleapis.com'>")
    html.append("<link rel='preconnect' href='https://fonts.gstatic.com' crossorigin>")
    html.append("<link href='https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800&display=swap' rel='stylesheet'>")
    html.append("<style>")
    html.append("""
        /* ── Base ── */
        html, body {
            margin: 0; padding: 0;
            font-family: 'Montserrat', 'Inter', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            font-size: 15px;
            line-height: 1.65;
            color: #111111;
            background: #ffffff;
        }
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Montserrat', 'Inter', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            color: #111111;
        }
        .ui-traps-report {
            padding: 40px 32px 60px;
            max-width: 860px;
            margin: 0 auto;
        }
        .timestamp {
            color: #8a8680;
            font-size: 0.85em;
            display: block;
            margin-bottom: 28px;
        }
        .context-section {
            padding: 0;
            border-radius: 14px;
            margin: 0 0 16px;
            border: 1px solid #e4e1dc;
            background: #ffffff;
            box-shadow: 0 1px 4px rgba(0,0,0,0.07), 0 1px 2px rgba(0,0,0,0.04);
            overflow: hidden;
        }
        .context-section > h2 {
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            color: #8a8680;
            padding: 16px 24px;
            margin: 0;
            border-bottom: 1px solid #e4e1dc;
        }
        .context-body {
            padding: 20px 24px;
            font-size: 14px;
        }
        .context-body p { margin: 0 0 8px; }
        .context-body p:last-child { margin-bottom: 0; }
        .context-body ul { margin: 4px 0 8px; padding-left: 20px; }
        .users-detail { margin: 0 0 8px; }
        .users-detail-label { margin: 0 0 8px; }
        .users-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.93em;
            border: 1px solid #e4e1dc;
            border-radius: 6px;
            overflow: hidden;
        }
        .users-table td {
            padding: 7px 12px;
            border: 1px solid #e4e1dc;
            vertical-align: top;
            line-height: 1.5;
        }
        .users-table .ut-label {
            width: 170px;
            text-align: right;
            font-size: 0.78em;
            font-weight: 700;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            color: #8a8680;
            white-space: nowrap;
            background: #faf9f7;
        }
        .users-table .ut-value { color: #2c2c2c; }
        .summary-section {
            padding: 0;
            border-radius: 14px;
            border: 1px solid #e4e1dc;
            background: #ffffff;
            box-shadow: 0 1px 4px rgba(0,0,0,0.07), 0 1px 2px rgba(0,0,0,0.04);
            margin: 0 0 24px;
            overflow: hidden;
        }
        .summary-section > h2 {
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            color: #8a8680;
            padding: 16px 24px;
            margin: 0;
            border-bottom: 1px solid #e4e1dc;
        }
        .summary-inner {
            padding: 20px 24px;
        }
        .summary-section ul {
            padding: 16px 24px 16px 40px;
            border-left: 3px solid #e05c1a;
            border-radius: 4px;
            background: #fdf1ea;
            margin: 12px 0;
        }
        .chat-context-badge {
            display: inline-block;
            font-size: 0.78em;
            color: #e05c1a;
            background: #fdf1ea;
            border: 1px solid rgba(224,92,26,0.25);
            border-radius: 100px;
            padding: 3px 10px;
            margin-bottom: 12px;
            font-weight: 600;
            letter-spacing: 0.03em;
        }
        .chat-override-section { margin-top: 12px; }
        .chat-override-list { margin: 6px 0 0; padding-left: 20px; font-size: 13px; color: #4a4744; }
        .chat-override-list li { margin-bottom: 3px; }
        /* Scorecard table title */
        .scorecard-title {
            font-size: 0.72em;
            font-weight: 700;
            letter-spacing: 0.07em;
            text-transform: uppercase;
            color: #8a8680;
            margin: 0 0 8px;
        }
        /* Scorecard table */
        .scorecard-table {
            width: 100%;
            border-collapse: collapse;
            border-radius: 10px;
            overflow: hidden;
            border: 1px solid #e4e1dc;
            margin: 0 0 20px 0;
            font-size: 0.9em;
        }
        .scorecard-table thead th {
            background: #f7f6f4;
            color: #8a8680;
            padding: 9px 14px;
            text-align: center;
            font-weight: 600;
            font-size: 0.75em;
            letter-spacing: 0.07em;
            text-transform: uppercase;
            border-bottom: 1px solid #e4e1dc;
        }
        .scorecard-table thead th:first-child { text-align: left; color: #4a4744; }
        .scorecard-th-high     { color: #c0392b !important; }
        .scorecard-th-moderate { color: #9a7000 !important; }
        .scorecard-th-low      { color: #2980b9 !important; }
        .scorecard-th-positive { color: #27ae60 !important; }
        .scorecard-label {
            padding: 10px 14px;
            font-size: 0.85em;
            font-weight: 600;
            color: #4a4744;
            border-bottom: 1px solid #e4e1dc;
            background: #faf9f7;
        }
        .scorecard-col {
            text-align: center;
            padding: 10px 14px;
            border-bottom: 1px solid #e4e1dc;
            font-weight: 700;
            font-size: 1em;
        }
        /* Value cell color coding — tinted background + matching text */
        .scorecard-val-high     { background: rgba(192,57,43,0.08);   color: #c0392b; }
        .scorecard-val-moderate { background: rgba(154,112,0,0.08);   color: #9a7000; }
        .scorecard-val-low      { background: rgba(41,128,185,0.08);  color: #2980b9; }
        .scorecard-val-positive { background: rgba(39,174,96,0.07);  color: #27ae60; }
        .scorecard-val-potential{ background: rgba(127,140,141,0.07);color: #7f8c8d; }
        .scorecard-empty        { color: #d0cdc8; }
        /* Summary headline + narrative */
        .summary-headline {
            font-size: 1.05em;
            font-weight: 700;
            color: #111111;
            margin: 4px 0 10px;
            line-height: 1.5;
        }
        .summary-narrative {
            font-size: 0.93em;
            color: #4a4744;
            margin: 0 0 4px;
            line-height: 1.65;
        }
        /* Trap card — new layout */
        .issue-headline {
            font-size: 1em;
            font-weight: 700;
            color: #111111;
            margin: 0 0 10px;
            line-height: 1.45;
        }
        /* Tenet-colored badge — used for trap names in cards and not-found lists */
        .tenet-pill {
            display: inline-block;
            font-size: 0.72em;
            font-weight: 700;
            font-family: 'Montserrat', 'Inter', system-ui, sans-serif;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            color: #ffffff;
            border-radius: 4px;
            padding: 3px 10px;
            white-space: nowrap;
            line-height: 1.5;
        }
        /* Region screenshot figure */
        .issue-region-figure {
            margin: 16px 0 10px;
            width: 100%;
            max-width: 480px;
            border: 1px solid #e4e1dc;
            border-radius: 8px;
            overflow: hidden;
            background: #f7f5f2;
        }
        .issue-region-img {
            display: block;
            /* Preserve aspect ratio; never upscale small crops or overflow the card.
               Both caps apply together, so the browser scales to fit the box. */
            max-width: 100%;
            max-height: 300px;
            width: auto;
            height: auto;
            margin: 0 auto;
            object-fit: contain;
        }
        .issue-region-caption {
            display: block;
            padding: 6px 10px;
            font-size: 0.78em;
            color: #6b6764;
            font-style: italic;
            border-top: 1px solid #e4e1dc;
            background: #f7f5f2;
        }
        .issue-meta {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 0 4px;
            margin: 0 0 14px;
            font-size: 0.82em;
            color: #4a4744;
        }
        .meta-label   { color: #4a4744; }
        .meta-pipe    { color: #d0cdc8; margin: 0 4px; }
        .meta-sep     { color: #d0cdc8; margin: 0 6px; }
        .meta-tenet   { color: #4a4744; }
        .meta-severity { font-weight: 600; }
        .meta-severity.sev-critical { color: #c0392b; }
        .meta-severity.sev-moderate { color: #9a7000; }
        .meta-severity.sev-minor    { color: #2980b9; }
        .meta-confidence { color: #4a4744; }
        .meta-trap-name { font-weight: 700; font-size: 0.82em; letter-spacing: 0.04em; color: #2c2a28; }
        .issue-section { margin: 10px 0 0; }
        .issue-section-label {
            font-size: 0.78em;
            font-weight: 700;
            letter-spacing: 0.07em;
            text-transform: uppercase;
            color: #8a8680;
            margin: 0 0 4px;
        }
        .issue-section-body {
            font-size: 0.93em;
            color: #2c2c2c;
            margin: 0;
            line-height: 1.6;
        }
        /* Not-found list */
        .trap-name-list {
            list-style: none;
            padding: 0;
            margin: 8px 0 0;
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
        }
        /* Frame ref */
        .frame-ref-text {
            margin: 0;
            color: #8a8680;
            font-size: 0.85em;
        }
        /* CSS-only severity dots — background scoped to .sev-dot only */
        .sev-dot {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 6px;
            vertical-align: middle;
            flex-shrink: 0;
        }
        .sev-dot.sev-critical { background: #c0392b; }
        .sev-dot.sev-moderate { background: #c49200; }
        .sev-dot.sev-minor    { background: #3498db; }
        .issue-card {
            background: #ffffff;
            border: 1px solid #e4e1dc;
            padding: 22px 24px;
            margin: 12px 0;
            border-radius: 14px;
            box-shadow: 0 1px 4px rgba(0,0,0,0.07), 0 1px 2px rgba(0,0,0,0.04);
            display: flex;
            align-items: flex-start;
            gap: 0;
        }
        /* Trap card image — fixed-width left column */
        .card-img-float {
            width: 130px;
            flex-shrink: 0;
            margin: 0 22px 0 0;
            border-radius: 8px;
            display: block;
            box-shadow: 0 2px 10px rgba(0,0,0,0.18);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            cursor: zoom-in;
            position: relative;
            z-index: 1;
        }
        .card-img-float:hover {
            transform: scale(1.8);
            transform-origin: top left;
            z-index: 100;
            box-shadow: 0 8px 28px rgba(0,0,0,0.28);
        }
        /* Content column — takes remaining width, never wraps under image */
        .issue-card-body {
            flex: 1;
            min-width: 0;
        }
        /* Finding number above headline */
        .finding-num {
            font-size: 0.72em;
            font-weight: 700;
            letter-spacing: 0.07em;
            text-transform: uppercase;
            color: #8a8680;
            margin: 0 0 4px;
        }
        .issue-card h3 {
            margin-top: 0;
            color: #111111;
            font-size: 1em;
            font-weight: 700;
        }
        .issue-card .tenet {
            color: #8a8680;
            font-size: 0.88em;
        }
        .issue-card .confidence {
            color: #8a8680;
            font-size: 0.82em;
            margin-top: 10px;
        }
        .issue-card .frame-info {
            background: #f7f6f4;
            color: #4a4744;
            border: 1px solid #e4e1dc;
            padding: 6px 12px;
            border-radius: 6px;
            margin: 0 0 14px 0;
            font-size: 0.88em;
            display: inline-block;
        }
        .issue-card .frame-info strong {
            color: #111111;
        }
        .frame-thumbnail-link:hover {
            transform: scale(1.05);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2) !important;
        }
        .issue-frames {
            background: #f7f6f4;
            padding: 12px;
            border-radius: 8px;
            border: 1px solid #e4e1dc;
        }
        .section-intro {
            color: #8a8680;
            font-size: 0.91em;
            margin: -6px 0 16px;
            line-height: 1.55;
        }
        .none-found {
            color: #8a8680;
            font-style: italic;
        }
        .positive-section { display: none; } /* replaced by .positives-section */
        .positives-section { margin: 24px 0; }
        .positive-card {
            padding: 18px 22px;
            border-radius: 14px;
            border: 1px solid #e4e1dc;
            border-left: 4px solid #27ae60;
            background: #ffffff;
            box-shadow: 0 1px 4px rgba(0,0,0,0.07), 0 1px 2px rgba(0,0,0,0.04);
        }
        .positive-card ul { margin: 0; padding-left: 20px; }
        .positive-card li { margin: 4px 0; font-size: 0.93em; }
        .positive-item { color: #111111; }
        h1 { font-size: 1.85em; font-weight: 800; color: #111111; letter-spacing: -0.7px; line-height: 1.2; border-bottom: none; padding-bottom: 0; margin: 0 0 6px; }
        h2 { font-size: 1.05em; font-weight: 700; color: #111111; letter-spacing: -0.2px; border-bottom: none; padding-bottom: 0; margin: 28px 0 14px; }
        h3 { font-size: 1em; font-weight: 700; color: #111111; margin: 16px 0 8px; letter-spacing: -0.1px; }
        h4 { font-size: 0.92em; font-weight: 600; color: #4a4744; margin: 12px 0 6px; }
        .potential-issues-section {
            padding: 22px 24px;
            border-radius: 14px;
            border-left: 4px solid #e05c1a;
            border: 1px solid #e4e1dc;
            background: #ffffff;
            margin: 20px 0;
            box-shadow: 0 1px 4px rgba(0,0,0,0.07), 0 1px 2px rgba(0,0,0,0.04);
        }
        .potential-issues-section .issue-card.potential {
            border-left-color: #e05c1a;
        }
        /* Confidence group headers inside Traps Found */
        .confidence-group-header {
            font-size: 0.78em;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: #8a8680;
            margin: 28px 0 4px;
            padding-bottom: 8px;
            border-bottom: 1px solid #e4e1dc;
        }
        .confidence-group-header:first-of-type { margin-top: 8px; }
        .task-section-header {
            font-size: 1.05em;
            font-weight: 700;
            color: #2c2a27;
            margin: 80px 0 4px;
            padding-top: 24px;
            padding-bottom: 6px;
            border-top: 1px solid #e4e1dc;
            border-bottom: 2px solid #e4e1dc;
        }
        .task-section-desc {
            color: #8a8680;
            font-size: 0.88em;
            margin: 0 0 14px;
        }
        .traps-not-found {
            padding: 22px 24px;
            border-radius: 14px;
            border: 1px solid #e4e1dc;
            background: #ffffff;
            box-shadow: 0 1px 4px rgba(0,0,0,0.07), 0 1px 2px rgba(0,0,0,0.04);
            margin: 0 0 16px;
        }
        .traps-not-found h2 { margin: 0 0 8px; font-size: 1.05em; font-weight: 700; }
        .traps-not-found h3 {
            font-size: 0.92em;
            margin: 16px 0 8px;
            color: #111111;
            font-weight: 600;
        }
        .untestable-list {
            list-style: none;
            padding: 0;
            margin: 0;
        }
        .untestable-list li {
            padding: 7px 0;
            border-bottom: 1px solid #e4e1dc;
            font-size: 0.87em;
            color: #4a4744;
        }
        .untestable-list li:last-child { border-bottom: none; }
        .untestable-list .trap-label {
            font-weight: 600;
            color: #111111;
        }
        .untestable-note {
            font-size: 0.85em;
            color: #8a8680;
            margin: 0 0 8px;
        }
        .footer {
            margin-top: 48px;
            padding-top: 24px;
            border-top: 1px solid #e4e1dc;
        }
        .confidentiality-notice {
            border: 1px solid #e4e1dc;
            padding: 20px 24px;
            border-radius: 14px;
            margin-top: 20px;
            background: #ffffff;
            box-shadow: 0 1px 4px rgba(0,0,0,0.07), 0 1px 2px rgba(0,0,0,0.04);
        }
        .confidentiality-notice h3 {
            color: #8a6500;
            margin-top: 0;
        }
        .confidentiality-notice ul { margin: 10px 0; }
        .confidentiality-notice li { margin: 5px 0; }
        hr {
            border: none;
            border-top: 1px solid #e4e1dc;
            margin: 24px 0;
        }
        .issues-section h2, .traps-not-found h2 { margin: 0 0 4px; }
        .issues-section { margin: 24px 0; }
        .issues-section > h2, .potential-issues-section > h2 {
            margin: 0 0 4px;
        }
        .trap-matrix { margin: 30px 0; }
        .trap-matrix-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.87em;
            border-radius: 14px;
            overflow: hidden;
            border: 1px solid #e4e1dc;
        }
        .trap-matrix-table thead th {
            background: #f7f6f4;
            color: #8a8680;
            padding: 10px 14px;
            text-align: left;
            font-weight: 600;
            font-size: 0.75em;
            letter-spacing: 0.07em;
            text-transform: uppercase;
            border-bottom: 1px solid #e4e1dc;
        }
        .trap-matrix-table thead th.count-col { text-align: center; }
        .trap-matrix-table td {
            padding: 7px 14px;
            border-bottom: 1px solid #e4e1dc;
            vertical-align: middle;
        }
        .trap-matrix-table .tenet-cell {
            font-weight: 700;
            font-size: 0.75em;
            letter-spacing: 0.06em;
            background: #faf9f7;
            color: #4a4744;
            text-align: center;
            border-right: 1px solid #e4e1dc;
            white-space: nowrap;
            text-transform: uppercase;
        }
        .trap-matrix-table .trap-name {
            color: #4a4744;
            font-size: 0.85em;
        }
        .trap-matrix-table .count { text-align: center; font-weight: 600; min-width: 60px; }
        .trap-matrix-table .count.critical { color: #c0392b; }
        .trap-matrix-table .count.moderate { color: #9a7000; }
        .trap-matrix-table .count.minor { color: #2980b9; }
        .trap-matrix-table .count.total {
            color: #111111;
            border-left: 1px solid #e4e1dc;
        }
        .trap-matrix-table tr.has-issues td.trap-name { font-weight: 600; color: #111111; }

        /* General Issues */
        .user-issues-section {
            margin: 30px 0;
            padding: 24px 28px;
            border-radius: 12px;
            border: 1px solid #e4e1dc;
            background: #ffffff;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }
        .user-issues-section h2 { border-bottom-color: #e05c1a; margin-top: 0; }
        .user-issues-intro { color: #8a8680; font-size: 0.91em; margin: -4px 0 18px; }
        .user-issue-card {
            background: #f7f6f4;
            border-radius: 8px;
            padding: 18px 20px;
            margin: 12px 0;
            border-left: 4px solid #d0cdc8;
            border: 1px solid #e4e1dc;
            box-shadow: none;
        }
        .user-issue-card.impact-high   { border-left-color: #c0392b; }
        .user-issue-card.impact-medium { border-left-color: #e05c1a; }
        .user-issue-card.impact-low    { border-left-color: #3498db; }
        .user-issue-header { display: flex; align-items: center; gap: 10px; margin-bottom: 6px; }
        .impact-badge {
            font-size: 0.7em; font-weight: 700; letter-spacing: 0.07em;
            padding: 3px 9px; border-radius: 100px; white-space: nowrap;
            text-transform: uppercase;
        }
        .impact-badge.high   { background: #fdecea; color: #c0392b; }
        .impact-badge.medium { background: #fdf1ea; color: #e05c1a; }
        .impact-badge.low    { background: #eaf4fd; color: #2471a3; }
        .user-issue-title { margin: 0; font-size: 1em; color: #111111; font-weight: 700; }
        .task-context { color: #8a8680; font-size: 0.87em; margin: 2px 0 10px; }
        .contributing-traps { display: flex; flex-wrap: wrap; align-items: center; gap: 6px; margin: 12px 0 8px; }
        .traps-label { font-size: 0.8em; color: #8a8680; font-weight: 600; margin-right: 2px; }
        .trap-pill {
            font-size: 0.72em; font-weight: 700; padding: 2px 9px;
            border-radius: 100px; letter-spacing: 0.04em;
        }
        .trap-pill.critical { background: #fdecea; color: #c0392b; border: 1px solid #f5c6c6; }
        .trap-pill.moderate { background: #fdf1ea; color: #e05c1a; border: 1px solid rgba(224,92,26,0.25); }
        .trap-pill.minor    { background: #eaf4fd; color: #2471a3; border: 1px solid #c6dff5; }
        .user-issue-recs strong { font-size: 0.9em; color: #111111; }
        .user-issue-recs ul { margin: 6px 0 0; padding-left: 20px; }
        .user-issue-recs li { margin: 3px 0; font-size: 0.93em; }
        .task-group-header { font-size: 0.95em; color: #4a4744; font-weight: 700; margin: 22px 0 8px; padding-bottom: 6px; border-bottom: 1px solid #e4e1dc; letter-spacing: -0.1px; }
    """)
    html.append("</style>")
    html.append("</head>")
    html.append("<body>")
    html.append("<div class='ui-traps-report'>")

    # Header
    html.append(f"<h1>UI Tenets &amp; Traps<br>Analysis Report</h1>")

    _ts_lines = [f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}"]
    if analysis_settings:
        _v = analysis_settings.get('verbosity')
        _ts_lines.append(f"Report detail: {'Brief' if _v == 'brief' else 'Standard'}")
        _m = analysis_settings.get('pass1_model')
        _ts_lines.append(f"Analysis model: {'Haiku 4.5' if _m == 'haiku' else 'Sonnet 4.6'}")
        _kb = analysis_settings.get('kb_version')
        if _kb:
            _kb_display = {'v1': 'v1', 'v1.1': 'v1.1', 'v2': 'v2'}.get(_kb, _kb)
            _ts_lines.append(f"Knowledge base: {_kb_display}")
        _style = analysis_settings.get('report_style')
        if _style:
            _ts_lines.append(f"Report style: {'By Issue' if _style == 'issues' else 'By Trap'}")
        _coverage = 'Thorough' if analysis_settings.get('thorough_mode') else 'Standard'
        _ts_lines.append(f"Analysis coverage: {_coverage}")
        if analysis_settings.get('mode') == 'twopass':
            _ts_lines.append("Analysis architecture: Two-pass (detection → adjudication)")
        _elapsed = analysis_settings.get('elapsed_seconds')
        if _elapsed is not None:
            _m2, _s = divmod(int(_elapsed), 60)
            _time_str = f"{_m2}m {_s}s" if _m2 else f"{_s}s"
            _ts_lines.append(f"Time to complete: {_time_str}")
        _usage = analysis_settings.get('usage') or {}
        _cached = (_usage.get('cache_read', 0) or 0) + (_usage.get('cache_creation', 0) or 0)
        _tok_total = (_usage.get('input', 0) or 0) + (_usage.get('output', 0) or 0) + _cached
        if _tok_total:
            _ts_lines.append(
                f"Tokens: {_tok_total:,} ({_usage.get('input', 0):,} input · "
                f"{_usage.get('output', 0):,} output · {_cached:,} cached)"
            )
            _cost = _usage.get('cost')
            if _cost is not None:
                _ts_lines.append(f"Estimated cost: ~${_cost:,.4f}")
    html.append(f"<p class='timestamp'>{'<br>'.join(_ts_lines)}</p>")

    # Truncation banner — the model's output hit the length cap, so the report is incomplete.
    if (analysis_settings or {}).get('truncated'):
        html.append(
            "<div style='margin:14px 0;padding:12px 16px;border-left:4px solid #b4232a;"
            "background:#f7e5e6;border-radius:6px;color:#7a1a1f;font-size:14px;'>"
            "⚠️ <b>Incomplete report:</b> the analysis output was cut off at the length limit, "
            "so some findings or coverage notes may be missing. Re-running usually resolves this."
            "</div>"
        )

    # Evaluation Details
    if user_context:
        html.append("<h2>Evaluation Details</h2>")
        html.append("<div class='context-section'>")
        html.append("<div class='context-body'>")
        if user_context.get('design_name'):
            html.append(f"<p><strong>Interface evaluated:</strong> {user_context['design_name']}</p>")

        # Strip leading "Target users: " prefix (it's now the label) and capitalize first letter
        users_raw = user_context.get('users') or 'N/A'
        if users_raw.startswith('Target users: '):
            users_raw = users_raw[len('Target users: '):]
        if users_raw:
            users_raw = users_raw[0].upper() + users_raw[1:]

        users_desc, users_attrs = _parse_users_string(users_raw)
        # Drop Frequency of use — not needed in the report summary
        users_attrs = [(l, v) for l, v in users_attrs if l != 'Frequency of use']
        html.append("<div class='users-detail'>")
        html.append("<p class='users-detail-label'><strong>Intended users:</strong></p>")
        html.append("<table class='users-table'>")
        if users_desc:
            html.append(f"<tr><td class='ut-label'>Description</td><td class='ut-value'>{users_desc}</td></tr>")
        for label, value in users_attrs:
            html.append(f"<tr><td class='ut-label'>{label}</td><td class='ut-value'>{value}</td></tr>")
        if not users_desc and not users_attrs:
            html.append(f"<tr><td class='ut-label'>Description</td><td class='ut-value'>{users_raw}</td></tr>")
        html.append("</table>")
        html.append("</div>")

        # Format tasks as bulleted list
        _tl = user_context.get('task_list') or []
        if len(_tl) > 1:
            html.append("<p><strong>Task(s) evaluated:</strong></p>")
            html.append("<ul>")
            for _t in _tl:
                _n = _t.get('name', '').strip()
                _d = _t.get('description', '').strip()
                html.append(f"<li><strong>{_n}</strong>: {_d}</li>" if _n else f"<li>{_d}</li>")
            html.append("</ul>")
        else:
            raw_tasks = user_context.get('tasks', 'N/A')
            task_list_display = parse_tasks(raw_tasks)
            html.append("<p><strong>Task(s) evaluated:</strong></p>")
            html.append("<ul>")
            for task in task_list_display:
                html.append(f"<li>{task}</li>")
            html.append("</ul>")

        # When re-analyzed via chat, surface the user's instructions so overrides are visible
        chat_content = user_context.get('chat_context_content', '')
        if chat_content:
            user_lines = []
            for line in chat_content.split('\n'):
                stripped = line.strip()
                if stripped.startswith('User: '):
                    user_lines.append(stripped[6:])
            if user_lines:
                html.append("<div class='chat-override-section'>")
                html.append("<p class='chat-context-badge'>&#x21BA; Re-analyzed with chat instructions &mdash; the following overrides were applied to this analysis:</p>")
                html.append("<ul class='chat-override-list'>")
                for line in user_lines:
                    html.append(f"<li>{line}</li>")
                html.append("</ul>")
                html.append("</div>")

        html.append("</div>")
        html.append("</div>")

    # Summary
    html.append("<h2>Summary of Findings</h2>")
    html.append("<div class='summary-section'>")
    html.append("<div class='summary-inner'>")

    # Scorecard: higher confidence = 'high' (both legacy and new KB; legacy 'Confirmed'
    # also counts as higher); lower = everything else + potentials.
    n_positive = len(report.get('positive_observations', []))

    def _is_high(issue):
        return _is_higher_confidence(issue)

    hc_critical = sum(1 for i in report.get('critical_issues', []) if _is_high(i))
    hc_moderate = sum(1 for i in report.get('moderate_issues', []) if _is_high(i))
    hc_low      = sum(1 for i in report.get('minor_issues',    []) if _is_high(i))
    lc_critical = sum(1 for i in report.get('critical_issues', []) if not _is_high(i))
    lc_moderate = sum(1 for i in report.get('moderate_issues', []) if not _is_high(i))
    lc_low      = (sum(1 for i in report.get('minor_issues',   []) if not _is_high(i))
                   + len(report.get('potential_issues', [])))

    def _sc(val, cls):
        return f"<td class='scorecard-col {cls}'>{val if val else '<span class=\"scorecard-empty\">—</span>'}</td>"

    if _new_kb:
        # Severity-ladder counts (High/Medium/Low) from severity_label — the G8 vocabulary.
        # Any legacy "Critical" label collapses into High.
        _ladder_counts = {'High': 0, 'Medium': 0, 'Low': 0}
        _bucket_fallback = {'critical_issues': 'High', 'moderate_issues': 'Medium', 'minor_issues': 'Low'}
        _sl_norm = {'critical': 'High', 'high': 'High', 'medium': 'Medium', 'low': 'Low'}
        for _arr in ('critical_issues', 'moderate_issues', 'minor_issues'):
            for _i in report.get(_arr) or []:
                _sl = _sl_norm.get((_i.get('severity_label') or '').strip().lower(), _bucket_fallback[_arr])
                _ladder_counts[_sl] += 1
        html.append("<p class='scorecard-title'>Issues by severity</p>")
        html.append("<table class='scorecard-table'>")
        html.append("<thead><tr>")
        for _lvl in ('High', 'Medium', 'Low'):
            html.append(f"<th class='scorecard-col'>{_lvl}</th>")
        html.append("</tr></thead><tbody><tr>")
        for _lvl in ('High', 'Medium', 'Low'):
            html.append(_sc(_ladder_counts[_lvl], 'scorecard-val-high'))
        html.append("</tr></tbody></table>")
    else:
        html.append("<p class='scorecard-title'>Number of Traps Identified</p>")
        html.append("<table class='scorecard-table'>")
        html.append("<thead><tr>")
        html.append("<th></th>")
        html.append("<th class='scorecard-col scorecard-th-high'>High Severity</th>")
        html.append("<th class='scorecard-col scorecard-th-moderate'>Moderate Severity</th>")
        html.append("<th class='scorecard-col scorecard-th-low'>Low Severity</th>")
        html.append("</tr></thead>")
        html.append("<tbody>")
        html.append("<tr>")
        html.append("<td class='scorecard-label'>Higher confidence</td>")
        html.append(_sc(hc_critical, 'scorecard-val-high'))
        html.append(_sc(hc_moderate, 'scorecard-val-moderate'))
        html.append(_sc(hc_low, 'scorecard-val-low'))
        html.append("</tr>")
        html.append("<tr>")
        html.append("<td class='scorecard-label'>Lower confidence</td>")
        html.append(_sc(lc_critical, 'scorecard-val-high'))
        html.append(_sc(lc_moderate, 'scorecard-val-moderate'))
        html.append(_sc(lc_low, 'scorecard-val-low'))
        html.append("</tr>")
        html.append("</tbody>")
        html.append("</table>")

    # Summary headline + narrative
    headline = report.get('summary_headline', '')
    narrative = report.get('summary_narrative', '')
    if headline:
        html.append(f"<p class='summary-headline'>{headline}</p>")
    if narrative:
        html.append(f"<p class='summary-narrative'>{narrative}</p>")

    html.append("</div>")
    html.append("</div>")

    # Get frame images from report if available (for video/multi-image analysis)
    frame_images = report.get('frame_images', {})

    # Helper function to render frame thumbnail
    def render_frame_thumbnail(frame_idx, size='small'):
        """Render a clickable thumbnail for a frame."""
        # Thumbnail size based on context
        thumb_width = "100px" if size == 'small' else "140px"
        thumb_height = "75px" if size == 'small' else "105px"

        # Default label
        label = f"Frame {frame_idx}"
        timestamp = None

        # Get frame data if available
        if frame_idx in frame_images:
            frame_data = frame_images[frame_idx]
            image_data = frame_data.get('image_data') or ''
            timestamp = frame_data.get('timestamp')

            if timestamp is not None:
                label = f"Frame {frame_idx} ({timestamp:.1f}s)"
        else:
            image_data = ''

        # Check if we have valid image data
        has_image = image_data and image_data.startswith('data:image')

        if has_image:
            # Render thumbnail with base64 image directly in src attribute
            # (src attributes can handle large base64 strings safely, unlike onclick handlers)
            return f"""
                <a href='#frame-{frame_idx}' class='frame-thumbnail-link' title='Click to see {label}' style='
                    display: inline-block;
                    margin: 4px;
                    text-decoration: none;
                    border-radius: 6px;
                    overflow: hidden;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                    transition: transform 0.2s, box-shadow 0.2s;
                '>
                    <div style='position: relative;'>
                        <img src='{image_data}' alt='{label}' style='
                            width: {thumb_width};
                            height: {thumb_height};
                            object-fit: cover;
                            display: block;
                        '>
                        <div style='
                            position: absolute;
                            bottom: 0;
                            left: 0;
                            right: 0;
                            background: rgba(0,0,0,0.75);
                            color: white;
                            font-size: 11px;
                            padding: 4px 6px;
                            text-align: center;
                            font-weight: 600;
                        '>{label}</div>
                    </div>
                </a>
            """
        else:
            # Render placeholder with timestamp info (no image available)
            return f"""
                <a href='#frame-{frame_idx}' class='frame-thumbnail-link' title='Go to {label}' style='
                    display: inline-flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    margin: 4px;
                    text-decoration: none;
                    border-radius: 6px;
                    overflow: hidden;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                    width: {thumb_width};
                    height: {thumb_height};
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    transition: transform 0.2s, box-shadow 0.2s;
                '>
                    <div style='font-size: 20px;'>🎬</div>
                    <div style='font-size: 10px; font-weight: 600; margin-top: 4px; text-align: center; padding: 0 4px;'>{label}</div>
                </a>
            """

    # Helper: render frame reference block
    def render_frame_ref(issue):
        has_frame_info = 'frame_index' in issue or 'frame_indices' in issue or 'frame' in issue
        if not has_frame_info:
            return
        html.append("<div class='issue-frames'>")
        if frame_images and ('frame_index' in issue or 'frame_indices' in issue):
            html.append("<div style='display:flex;flex-wrap:wrap;gap:4px;margin-bottom:6px;'>")
            if 'frame_indices' in issue and len(issue.get('frame_indices', [])) > 1:
                for idx in issue['frame_indices'][:5]:
                    html.append(render_frame_thumbnail(idx, 'small'))
                if len(issue['frame_indices']) > 5:
                    html.append(f"<span style='align-self:center;color:#8a8680;margin-left:8px;font-size:0.85em;'>+{len(issue['frame_indices'])-5} more</span>")
            elif 'frame_index' in issue:
                html.append(render_frame_thumbnail(issue['frame_index'], 'small'))
            html.append("</div>")
        if 'frame_indices' in issue and len(issue.get('frame_indices', [])) > 1:
            frame_labels = []
            for idx in issue['frame_indices'][:5]:
                if idx in frame_images and frame_images[idx].get('timestamp') is not None:
                    frame_labels.append(f"Frame {idx} ({frame_images[idx]['timestamp']:.1f}s)")
                else:
                    frame_labels.append(f"Frame {idx}")
            label_text = ", ".join(frame_labels)
            if len(issue['frame_indices']) > 5:
                label_text += f" +{len(issue['frame_indices'])-5} more"
            html.append(f"<p class='frame-ref-text'>{label_text}</p>")
        elif 'frame_index' in issue:
            idx = issue['frame_index']
            ts_str = f" ({frame_images[idx]['timestamp']:.1f}s)" if idx in frame_images and frame_images[idx].get('timestamp') is not None else ""
            html.append(f"<p class='frame-ref-text'>Frame {idx}{ts_str}</p>")
        elif 'frame' in issue:
            html.append(f"<p class='frame-ref-text'>{issue['frame']}</p>")
        html.append("</div>")

    # Helper: render a single trap card
    confidence_order = {"high": 0, "medium": 1, "low": 2}

    def render_trap_card(issue, severity_class, finding_num=None):
        html.append(f"<div class='issue-card {severity_class}'>")
        # Trap card image — fixed-width left column
        card_img = _get_card_img(issue.get('trap_name', ''))
        if card_img:
            html.append(f"<img class='card-img-float' src='{card_img}' alt='{issue.get('trap_name','').upper()} trap card' />")
        # Content column — never wraps under image
        html.append("<div class='issue-card-body'>")
        render_frame_ref(issue)
        # Finding number + headline + meta row
        if finding_num is not None:
            html.append(f"<p class='finding-num'>Finding {finding_num}</p>")
        headline_text = _cap_terms(issue.get('headline', ''))
        if headline_text:
            html.append(f"<p class='issue-headline'>{headline_text}</p>")
        # Meta row: "Trap: NAME | Severity: ● High | Confidence: High" — below headline
        conf = issue.get('confidence', '')
        # New-KB findings carry the exact ladder level (High/Medium/Low); prefer it.
        # The fallback is version-aware: new-KB uses the High/Medium/Low ladder vocab
        # (consistent with its scorecard), legacy keeps its High/Moderate/Low labels.
        _sev_fallback = ({'critical': 'High', 'moderate': 'Medium', 'minor': 'Low'} if _new_kb
                         else {'critical': 'High', 'moderate': 'Moderate', 'minor': 'Low'})
        _sl_raw = issue.get('severity_label') or _sev_fallback.get(severity_class, severity_class.title())
        # Collapse any legacy "Critical" label into High for new-KB display.
        sev_label = 'High' if (_new_kb and str(_sl_raw).strip().lower() == 'critical') else _sl_raw
        html.append("<div class='issue-meta'>")
        trap_name_display = (issue.get('trap_name') or '').upper()
        if trap_name_display:
            html.append(f"<span class='meta-label'>Trap:</span>")
            html.append(f"<span class='meta-trap-name'>{trap_name_display}</span>")
            html.append(f"<span class='meta-pipe'> | </span>")
        html.append(f"<span class='meta-label'>Severity:</span>")
        html.append(f"<span class='sev-dot sev-{severity_class}'></span>")
        html.append(f"<span class='meta-severity sev-{severity_class}'>{sev_label}</span>")
        if conf:
            html.append(f"<span class='meta-pipe'> | </span>")
            html.append(f"<span class='meta-label'>Confidence:</span>")
            html.append(f"<span class='meta-confidence'>{conf.title()}</span>")
        html.append("</div>")
        # Finding body (no label — keep it clean)
        problem_text = _cap_terms(issue.get('problem', ''))
        if problem_text:
            html.append("<div class='issue-section'>")
            html.append(f"<p class='issue-section-body'>{problem_text}</p>")
            html.append("</div>")
        # Region screenshot figure (between problem and recommendation)
        region_b64 = issue.get('region_image_b64')
        if region_b64:
            caption = _cap_terms((issue.get('region') or {}).get('caption') or issue.get('location', ''))
            html.append("<figure class='issue-region-figure'>")
            html.append(f"<img src='data:image/png;base64,{region_b64}' class='issue-region-img' alt='Screenshot detail showing the identified issue' />")
            if caption:
                html.append(f"<figcaption class='issue-region-caption'>{caption}</figcaption>")
            html.append("</figure>")
        # Recommendation (keep label)
        rec_text = _cap_terms(issue.get('recommendation', ''))
        if rec_text:
            html.append("<div class='issue-section'>")
            html.append("<p class='issue-section-label'>Recommendation</p>")
            html.append(f"<p class='issue-section-body'>{rec_text}</p>")
            html.append("</div>")
        # Why uncertain note (only present on folded-in potential issues)
        why = issue.get('why_uncertain', '')
        if why:
            html.append(f"<p class='issue-section-body' style='margin-top:10px;font-style:italic;color:#8a8680;font-size:0.9em;'>{_cap_terms(why)}</p>")
        html.append("</div>")  # close issue-card-body
        html.append("</div>")  # close issue-card

    # ── Traps Found ──
    all_confirmed = (
        [('critical', i) for i in report.get('critical_issues', [])] +
        [('moderate', i) for i in report.get('moderate_issues', [])] +
        [('minor', i) for i in report.get('minor_issues', [])]
    )
    sev_order = {'critical': 0, 'moderate': 1, 'minor': 2}

    # Fold potential_issues into the lower-confidence pool
    potential_pool = []
    for p in report.get('potential_issues', []):
        norm = dict(p)
        if 'problem' not in norm and 'observation' in norm:
            norm['problem'] = norm.pop('observation')
        norm.setdefault('confidence', 'low')
        if not norm.get('headline') and norm.get('trap_name'):
            norm['headline'] = norm['trap_name'].title()
        potential_pool.append(('minor', norm))

    _task_list = (user_context or {}).get('task_list') or []
    _multi_task = len(_task_list) > 1

    html.append("<div class='issues-section'>")
    html.append("<h2>Issues</h2>" if _new_kb else "<h2>Traps Found</h2>")

    if _new_kb:
        # One Issues section ordered by the severity ladder (severity_label) — no confidence
        # grouping, and potential_issues are NOT folded in (they get their own section below).
        # High/Medium/Low only; any legacy 'critical' ties with 'high' (no Critical-above-High).
        _ladder = {'critical': 0, 'high': 0, 'medium': 1, 'low': 2}

        def _sev_rank(entry):
            _sl = (entry[1].get('severity_label') or '').strip().lower()
            return _ladder.get(_sl, {'critical': 0, 'moderate': 1, 'minor': 2}.get(entry[0], 1))

        if not all_confirmed:
            html.append("<p class='none-found'>No issues found ✓</p>")
        else:
            _fn = 0
            for sev_class, issue in sorted(all_confirmed, key=_sev_rank):
                _fn += 1
                render_trap_card(issue, sev_class, _fn)
    elif not all_confirmed and not potential_pool:
        html.append("<p class='none-found'>No confirmed traps found ✓</p>")
    elif _multi_task:
        task_names = [
            (t.get('name') or '').strip() or (t.get('description') or '').strip() or f'Task {i + 1}'
            for i, t in enumerate(_task_list)
        ]

        def _match_task(issue_task_field):
            if not issue_task_field or issue_task_field.strip().lower() == 'general':
                return None
            itf_lower = issue_task_field.strip().lower()
            for tn in task_names:
                if tn.lower() == itf_lower or tn.lower() in itf_lower or itf_lower in tn.lower():
                    return tn
            return None  # unmatched → general

        general_issues = []
        per_task = {tn: [] for tn in task_names}
        for sev_class, issue in all_confirmed + potential_pool:
            matched = _match_task(issue.get('task', ''))
            if matched:
                per_task[matched].append((sev_class, issue))
            else:
                general_issues.append((sev_class, issue))

        finding_num = [0]  # use list so inner function can mutate

        def _render_confidence_group(items):
            hc = sorted(
                [(s, iss) for s, iss in items if _is_higher_confidence(iss)],
                key=lambda x: sev_order.get(x[0], 2)
            )
            lc = sorted(
                [(s, iss) for s, iss in items if not _is_higher_confidence(iss)],
                key=lambda x: sev_order.get(x[0], 2)
            )
            if hc:
                html.append("<h4 class='confidence-group-header'>Higher confidence</h4>")
                for sc, iss in hc:
                    finding_num[0] += 1
                    render_trap_card(iss, sc, finding_num[0])
            if lc:
                html.append("<h4 class='confidence-group-header'>Lower confidence</h4>")
                for sc, iss in lc:
                    finding_num[0] += 1
                    render_trap_card(iss, sc, finding_num[0])

        if general_issues:
            html.append("<h3 class='task-section-header'>General Findings</h3>")
            _tasks_label = ' and '.join(f'<em>{tn}</em>' for tn in task_names)
            html.append(f"<p class='task-section-desc'>These findings apply equally across all tasks ({_tasks_label}) or are not specific to any one task.</p>")
            _render_confidence_group(general_issues)

        for tn in task_names:
            bucket = per_task.get(tn, [])
            if bucket:
                html.append(f"<h3 class='task-section-header'>Task: {tn}</h3>")
                _render_confidence_group(bucket)

    else:
        # Single-task: original flat confidence split
        high_conf = sorted(
            [(s, i) for s, i in all_confirmed if _is_higher_confidence(i)],
            key=lambda x: sev_order.get(x[0], 2)
        )
        low_conf = sorted(
            [(s, i) for s, i in all_confirmed if not _is_higher_confidence(i)],
            key=lambda x: sev_order.get(x[0], 2)
        ) + potential_pool

        finding_num = 0
        if high_conf:
            html.append("<h3 class='confidence-group-header'>Higher confidence</h3>")
            for sev_class, issue in high_conf:
                finding_num += 1
                render_trap_card(issue, sev_class, finding_num)
        if low_conf:
            html.append("<h3 class='confidence-group-header'>Lower confidence</h3>")
            for sev_class, issue in low_conf:
                finding_num += 1
                render_trap_card(issue, sev_class, finding_num)

    html.append("</div>")

    # ── Worth a closer look (G8 §2) — new KB only; pivotal unknowns as their own section ──
    if _new_kb:
        _closer = report.get('potential_issues', []) or []
        if _closer:
            html.append("<div class='issues-section'>")
            html.append("<h2>Worth a closer look</h2>")
            html.append("<p class='section-intro'>Pivotal unknowns that could not be settled from this artifact — each names a check that would resolve it.</p>")
            for _item in _closer:
                _trap = (_item.get('trap_name') or '').upper()
                _hl = _cap_terms(_item.get('why_it_matters') or _item.get('observation') or _trap.title())
                html.append("<div class='issue-card minor'>")
                html.append("<div class='issue-card-body'>")
                if _hl:
                    html.append(f"<p class='issue-headline'>{_hl}</p>")
                html.append("<div class='issue-meta'>")
                if _trap:
                    html.append("<span class='meta-label'>Trap:</span>")
                    html.append(f"<span class='meta-trap-name'>{_trap}</span>")
                _loc = _cap_terms(_item.get('location', ''))
                if _loc:
                    html.append("<span class='meta-pipe'> | </span><span class='meta-label'>Where:</span>")
                    html.append(f"<span class='meta-severity'>{_loc}</span>")
                html.append("</div>")
                _obs = _cap_terms(_item.get('observation', ''))
                if _obs:
                    html.append(f"<div class='issue-section'><p class='issue-section-body'>{_obs}</p></div>")
                _check = _cap_terms(_item.get('check', ''))
                if _check:
                    _cost = _cap_terms(_item.get('check_cost', ''))
                    _cost_str = f" <em>({_cost})</em>" if _cost else ""
                    html.append(f"<div class='issue-section'><p class='issue-section-label'>The check</p><p class='issue-section-body'>{_check}{_cost_str}</p></div>")
                _if_c = _cap_terms(_item.get('implication_if_confirmed', ''))
                _if_r = _cap_terms(_item.get('implication_if_ruled_out', ''))
                if _if_c or _if_r:
                    html.append("<div class='issue-section'><p class='issue-section-label'>Implications</p>")
                    if _if_c:
                        html.append(f"<p class='issue-section-body'><strong>If confirmed:</strong> {_if_c}</p>")
                    if _if_r:
                        html.append(f"<p class='issue-section-body'><strong>If ruled out:</strong> {_if_r}</p>")
                    html.append("</div>")
                html.append("</div>")  # close issue-card-body
                html.append("</div>")  # close issue-card
            html.append("</div>")

    # Positive Observations
    html.append("<div class='positives-section'>")
    html.append("<h2>Positives</h2>")
    html.append("<div class='positive-card'>")
    if report.get('positive_observations'):
        html.append("<ul>")
        for obs in report['positive_observations']:
            html.append(f"<li class='positive-item'>{obs}</li>")
        html.append("</ul>")
    else:
        html.append("<p class='none-found'>None noted</p>")
    html.append("</div>")
    html.append("</div>")

    # Bugs Detected (Technical Issues)
    if report.get('bugs_detected') and len(report['bugs_detected']) > 0:
        html.append("<div class='bugs-section' style='padding: 20px; border-radius: 5px; border-left: 4px solid #e91e63; margin: 20px 0;'>")
        html.append("<h2>🐛 Technical Bugs Detected</h2>")
        html.append("<p><em>These are technical issues or broken states, not UI Traps. They represent system failures that should be fixed regardless of usability.</em></p>")
        for bug in report['bugs_detected']:
            html.append("<div class='bug-card'>")

            # Show frame reference if available
            has_frame_info = 'frame_index' in bug or 'frame_indices' in bug or 'frame' in bug
            if has_frame_info:
                html.append("<div class='issue-frames' style='margin-bottom: 12px;'>")
                html.append("<p style='margin: 0 0 8px 0; font-weight: 600; color: #2c3e50;'>📍 Found in:</p>")
                if frame_images and 'frame_index' in bug:
                    html.append("<div style='display: flex; flex-wrap: wrap; gap: 4px; margin-bottom: 8px;'>")
                    html.append(render_frame_thumbnail(bug['frame_index'], 'small'))
                    html.append("</div>")
                if 'frame_index' in bug:
                    idx = bug['frame_index']
                    if idx in frame_images and frame_images[idx].get('timestamp') is not None:
                        ts = frame_images[idx]['timestamp']
                        html.append(f"<p style='margin: 0; color: #555; font-size: 0.9em;'>Frame {idx} ({ts:.1f}s)</p>")
                    else:
                        html.append(f"<p style='margin: 0; color: #555; font-size: 0.9em;'>Frame {idx}</p>")
                elif 'frame' in bug:
                    html.append(f"<p style='margin: 0; color: #555; font-size: 0.9em;'>{bug['frame']}</p>")
                html.append("</div>")

            bug_type_display = bug.get('bug_type', 'unknown').replace('_', ' ').title()
            confidence = bug.get('confidence', 'medium').capitalize()
            html.append(f"""
                <div class='bug-card-header'>
                    <span class='bug-type-badge'>{bug_type_display}</span>
                    <span class='bug-confidence'>Confidence: {confidence}</span>
                </div>
                <div class='bug-field'><strong>Where:</strong> {bug.get('location', 'N/A')}</div>
                <div class='bug-field'><strong>Description:</strong> {bug.get('description', 'N/A')}</div>
            """)
            if bug.get('possible_cause'):
                html.append(f"<div class='bug-field'><strong>Possible Cause:</strong> {bug['possible_cause']}</div>")
            html.append("</div>")
        html.append("</div>")

    # Cross-Frame Issues (for video/multi-frame analysis)
    if report.get('cross_frame_issues') and len(report['cross_frame_issues']) > 0:
        html.append("<div class='cross-frame-section' style='padding: 20px; border-radius: 5px; border-left: 4px solid #4caf50; margin: 20px 0;'>")
        html.append("<h2>🔄 Cross-Frame Issues</h2>")
        html.append("<p><em>These issues were detected by comparing element positions across multiple frames:</em></p>")
        for issue in report['cross_frame_issues']:
            severity_color = '#f39c12' if issue.get('severity') == 'moderate' else '#e74c3c' if issue.get('severity') == 'critical' else '#3498db'
            html.append(f"<div class='issue-card' style='border-left-color: {severity_color};'>")
            html.append(f"<h3 style='margin-top: 0; color: #2c3e50;'>{issue.get('trap_name', 'WANDERING ELEMENT').upper()}</h3>")
            html.append(f"<p class='tenet'><strong>Tenet:</strong> {issue.get('tenet', 'HABITUATING').upper()}</p>")
            html.append(f"<p><strong>Element:</strong> {issue.get('element_description', 'UI element')}</p>")

            # Show locations as tags
            locations = issue.get('locations_found', [])
            if locations:
                html.append("<p><strong>Locations Found:</strong></p>")
                html.append("<div style='display: flex; flex-wrap: wrap; gap: 8px; margin: 8px 0;'>")
                for loc in locations:
                    html.append(f"<span style='background: #667eea; color: white; padding: 4px 12px; border-radius: 16px; font-size: 0.85em;'>{loc}</span>")
                html.append("</div>")

            html.append(f"<p><strong>Problem:</strong> {_cap_terms(issue.get('problem', 'N/A'))}</p>")

            # Show frame timeline
            if issue.get('frame_occurrences'):
                html.append("<div style='background: #f8f9fa; padding: 12px; border-radius: 6px; margin: 12px 0;'>")
                html.append("<p style='margin: 0 0 8px 0; font-weight: 600;'>📍 Timeline:</p>")
                html.append("<div style='display: flex; flex-wrap: wrap; gap: 8px;'>")
                for occ in issue['frame_occurrences']:
                    timestamp_str = f" ({occ['timestamp']:.1f}s)" if occ.get('timestamp') is not None else ""
                    html.append(f"""
                        <div style='background: white; border: 1px solid #e0e0e0; border-radius: 6px; padding: 8px 12px; text-align: center;'>
                            <div style='font-weight: 600; color: #667eea;'>Frame {occ['frame_index']}{timestamp_str}</div>
                            <div style='font-size: 0.85em; color: #666; margin-top: 4px;'>{occ.get('location', 'unknown')}</div>
                        </div>
                    """)
                html.append("</div>")
                html.append("</div>")

            html.append(f"<p><strong>Recommendation:</strong> {issue.get('recommendation', 'Maintain consistent element placement.')}</p>")
            html.append(f"<p class='confidence'><em>Confidence: {issue.get('confidence', 'medium')} | Severity: {issue.get('severity', 'moderate')}</em></p>")
            html.append("</div>")
        html.append("</div>")

    # Frame Quality Notes (for video/multi-frame analysis)
    if report.get('frame_quality_notes') and len(report['frame_quality_notes']) > 0:
        html.append("<div class='frame-quality-section' style='padding: 20px; border-radius: 5px; border-left: 4px solid #2196f3; margin: 20px 0;'>")
        html.append("<h2>🎬 Frame Quality Notes</h2>")
        html.append("<p><em>Some frames were filtered out during analysis due to quality issues:</em></p>")
        html.append("<ul style='margin: 10px 0;'>")
        for note in report['frame_quality_notes']:
            issue_labels = {
                'mid_transition': 'Mid-transition',
                'partial_scroll': 'Partial scroll',
                'loading_state': 'Loading screen',
                'blank_screen': 'Blank/empty',
                'duplicate': 'Duplicate frame',
                'low_quality': 'Low quality',
                'incomplete_ui': 'Incomplete UI'
            }
            issue_label = issue_labels.get(note.get('issue'), note.get('issue', 'Unknown'))
            timestamp = note.get('timestamp')
            if timestamp is not None:
                html.append(f"<li><strong>Frame at {timestamp:.1f}s:</strong> {issue_label} - {note.get('description', 'Skipped')}</li>")
            else:
                html.append(f"<li><strong>Frame {note.get('frame_index', '?')}:</strong> {issue_label} - {note.get('description', 'Skipped')}</li>")
        html.append("</ul>")
        html.append("</div>")

    # Coverage notes. New-KB reports carry G4 `coverage_status` labels; legacy reports
    # use the testable boolean and render two separate sections.
    raw_items = report.get('traps_checked_not_found', [])
    if _new_kb:
        not_present = []
        not_assessable = []
        for item in raw_items:
            if isinstance(item, str):
                not_present.append({'trap_name': item})
                continue
            status = (item.get('coverage_status') or '').strip()
            if status in ('not_assessable_artifact', 'not_assessable_context'):
                not_assessable.append(item)
            else:
                # not_present or unlabeled → treat as assessed-not-present rather than drop.
                not_present.append(item)

        _cov_labels = {
            'not_assessable_artifact': 'Not assessable from this artifact',
            'not_assessable_context': 'Not assessable without user context',
        }
        if not_present or not_assessable:
            html.append("<div class='traps-not-found'>")
            html.append("<h2>Coverage notes</h2>")
            if not_present:
                html.append("<p class='section-intro'>Traps specifically evaluated that do not appear to be present in the submitted design.</p>")
                html.append("<ul class='trap-name-list'>")
                for item in not_present:
                    name = item.get('trap_name', '')
                    detail = (item.get('detail') or '').strip()
                    detail_html = f" <span class='coverage-detail'>— {detail}</span>" if detail else ""
                    html.append(f"<li>{_tenet_pill_html(name, _tenet_for(name))}{detail_html}</li>")
                html.append("</ul>")
            if not_assessable:
                html.append("<p class='section-intro'>Traps that could not be assessed from the submitted materials — each notes what would settle it.</p>")
                html.append("<ul class='trap-name-list'>")
                for item in not_assessable:
                    name = item.get('trap_name', '')
                    label = _cov_labels.get((item.get('coverage_status') or '').strip(), 'Not assessable')
                    detail = (item.get('detail') or '').strip()
                    tail = f": {detail}" if detail else ""
                    html.append(f"<li>{_tenet_pill_html(name, _tenet_for(name))} <span class='coverage-detail'>— {label}{tail}</span></li>")
                html.append("</ul>")
            html.append("</div>")
    else:
        tested_ok = []
        untestable = []
        for item in raw_items:
            if isinstance(item, str):
                tested_ok.append(item)
            elif not (item.get('trap_name') if isinstance(item, dict) else None):
                continue  # skip malformed coverage entries with no trap name
            elif item.get('testable', True):
                tested_ok.append(item['trap_name'])
            else:
                untestable.append(item)

        if tested_ok:
            html.append("<div class='traps-not-found'>")
            html.append("<h2>Traps Not Found</h2>")
            html.append("<p class='section-intro'>The following traps were specifically evaluated and do not appear to be present in the submitted design.</p>")
            html.append("<ul class='trap-name-list'>")
            for trap in tested_ok:
                tenet = _tenet_for(trap)
                html.append(f"<li>{_tenet_pill_html(trap, tenet)}</li>")
            html.append("</ul>")
            html.append("</div>")

        if untestable:
            html.append("<div class='traps-not-found'>")
            html.append("<h2>Needs More Context</h2>")
            html.append("<p class='section-intro'>The following traps could not be fully evaluated from the submitted materials. To investigate further, consider testing the live product with representative users, reviewing additional screens in the task flow, or inspecting the underlying code.</p>")
            html.append("<ul class='trap-name-list'>")
            for item in untestable:
                tenet = _tenet_for(item['trap_name'])
                html.append(f"<li>{_tenet_pill_html(item['trap_name'], tenet)}</li>")
            html.append("</ul>")
            html.append("</div>")

    # Footer
    html.append("<div class='footer confidentiality-notice'>")
    html.append("<p><em>Generated using UI Tenets & Traps proprietary framework</em></p>")
    html.append("<hr/>")
    html.append("<h3>⚠️ CONFIDENTIALITY NOTICE</h3>")
    html.append("<p><strong>PROPRIETARY & CONFIDENTIAL:</strong> This analysis report is provided exclusively to authorized subscribers of the UI Tenets & Traps analysis service.</p>")
    html.append("<ul>")
    html.append("<li><strong>Copyright © 2009-present UI Traps LLC.</strong> All Rights Reserved.</li>")
    html.append("<li>The UI Tenets & Traps framework is proprietary intellectual property</li>")
    html.append("<li>Reproduction, distribution, or sharing without written permission is prohibited</li>")
    html.append("<li>This report is for your internal use only</li>")
    html.append("<li>Unauthorized disclosure may result in termination of service and legal action</li>")
    html.append("</ul>")
    html.append("<p>For licensing inquiries: <a href='mailto:service@uitraps.com'>service@uitraps.com</a></p>")
    html.append("</div>")

    html.append("</div>")
    html.append("</body>")
    html.append("</html>")

    return "\n".join(html)


# Tenet → solid pill background (white-text-safe on both themes), from the rev6 design.
_TENET_PILL = {
    "UNDERSTANDABLE": "#35597F", "COMFORTABLE": "#C1442B", "RESPONSIVE": "#8F6510",
    "EFFICIENT": "#A11B5E", "ACCURATE": "#34793B", "PROTECTIVE": "#5C2E93",
    "HABITUATING": "#1C6F96", "BEAUTIFUL": "#A85408",
    # v1-only Tenets (v1 deck's split of what v2 folded into PROTECTIVE). Tool DISPLAY colors —
    # the card deck defines no hex — kept in the PROTECTIVE-purple family, distinct from each other.
    "FORGIVING": "#6E39A6", "DISCREET": "#453A82",
}
_SEV_CLASS = {"critical": "high", "high": "high", "medium": "medium", "low": "low"}
# Single source for the rev6 scorecard AND card display-normalization, so the matrix tally can
# never disagree with the per-finding cards (both formatters assign their locals from these).
# Collapses legacy vocab (Critical→High; Confirmed/Probable/Flagged→High/Medium/Low). Fallbacks
# applied at each call site: severity→Medium, confidence→Low.
_SEV_NORM = {"critical": "High", "high": "High", "medium": "Medium", "low": "Low"}
_CONF_NORM = {"confirmed": "High", "probable": "Medium", "flagged": "Low",
              "high": "High", "medium": "Medium", "low": "Low"}
_SCORE_ROWS = ["High", "Medium", "Low"]
_SCORE_COLS = [("High", "task failure / high friction", "high"),
               ("Medium", "significant friction", "med"),
               ("Low", "low friction / polish", "low")]

def _emit_eval_details(h: list, uc: dict) -> None:
    """Append the rev6 'Evaluation details' section (intended users + tasks evaluated) to `h`.
    Shared verbatim by the By-Issue and By-Trap renderers; `uc` is pre-escaped at the boundary."""
    _users_raw = uc.get("users") or ""
    if _users_raw.startswith("Target users: "):
        _users_raw = _users_raw[len("Target users: "):]
    if _users_raw:
        _users_raw = _users_raw[0].upper() + _users_raw[1:]
    _u_desc, _u_attrs = _parse_users_string(_users_raw) if _users_raw else ("", [])
    _u_attrs = [(l, v) for l, v in _u_attrs if l != "Frequency of use"]
    _tl = uc.get("task_list") or []
    if len(_tl) > 1:
        _task_items = [((t.get("name") or "").strip(), (t.get("description") or "").strip())
                       for t in _tl if isinstance(t, dict)]
    elif uc.get("tasks"):
        _task_items = [("", t) for t in parse_tasks(uc.get("tasks", "")) if t]
    else:
        _task_items = []
    _task_items = [(n, d) for n, d in _task_items if n or d]
    _has_users = bool(_u_desc or _u_attrs or _users_raw)
    if _has_users or _task_items:
        h.append("<div class='section'><div class='section-eyebrow'>Evaluation details</div>")
        h.append("<div class='eval-grid'>")
        if _has_users:
            h.append("<div class='eval-block'><div class='field-label'>Intended users</div><dl class='eval-dl'>")
            if _u_desc:
                h.append(f"<div class='eval-row'><dt>Description</dt><dd>{_u_desc}</dd></div>")
            for _lbl, _val in _u_attrs:
                h.append(f"<div class='eval-row'><dt>{_lbl}</dt><dd>{_val}</dd></div>")
            if not _u_desc and not _u_attrs:
                h.append(f"<div class='eval-row'><dt>Description</dt><dd>{_users_raw}</dd></div>")
            h.append("</dl></div>")
        if _task_items:
            h.append("<div class='eval-block'><div class='field-label'>Tasks evaluated</div><ul class='eval-tasks'>")
            for _n, _d in _task_items:
                h.append(f"<li><b>{_n}</b> — {_d}</li>" if _n else f"<li>{_d}</li>")
            h.append("</ul></div>")
        h.append("</div></div>")


_NEW_KB_ISSUES_CSS = """
:root{--ground:#e9ebef;--surface:#fff;--surface-sunk:#f4f5f7;--ink:#1b1e24;--ink-soft:#565d68;--ink-faint:#8b929c;
--hairline:#e2e5ea;--hairline-strong:#d2d7de;--brand:#0f766e;--brand-soft:#ddf0ed;
--sev-critical:#b4232a;--sev-high:#cf5f26;--sev-medium:#b3860c;--sev-low:#3a7ca5;
--sev-critical-tint:#f7e5e6;--sev-high-tint:#f8e9df;--sev-medium-tint:#f6eed9;--sev-low-tint:#e2edf4;
--radius:11px;--rail:216px;--shadow:0 1px 2px rgba(20,25,35,.05),0 8px 24px rgba(20,25,35,.06);
--font-sans:'Montserrat',system-ui,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
--font-mono:ui-monospace,"SF Mono","Cascadia Code","Roboto Mono",Menlo,Consolas,monospace;}
/* Report defaults to LIGHT (matches the rest of the app). Dark is opt-in only, via an
   explicit data-theme="dark" on the root — never auto-switched from the OS preference,
   which would leave the report dark while the app is light. */
:root[data-theme="light"]{--ground:#e9ebef;--surface:#fff;--surface-sunk:#f4f5f7;--ink:#1b1e24;--ink-soft:#565d68;--ink-faint:#8b929c;--hairline:#e2e5ea;--hairline-strong:#d2d7de;--brand:#0f766e;--brand-soft:#ddf0ed;--sev-critical:#b4232a;--sev-high:#cf5f26;--sev-medium:#b3860c;--sev-low:#3a7ca5;--sev-critical-tint:#f7e5e6;--sev-high-tint:#f8e9df;--sev-medium-tint:#f6eed9;--sev-low-tint:#e2edf4;}
:root[data-theme="dark"]{--ground:#14171c;--surface:#1d2127;--surface-sunk:#23282f;--ink:#eef1f5;--ink-soft:#aab2bd;--ink-faint:#7b838f;--hairline:#2c323a;--hairline-strong:#363d47;--brand:#3fbcae;--brand-soft:#10312e;--sev-critical:#e06a6f;--sev-high:#e79256;--sev-medium:#d9b038;--sev-low:#6fb0d4;--sev-critical-tint:#3a2528;--sev-high-tint:#3a2c21;--sev-medium-tint:#35301d;--sev-low-tint:#22323c;}
*{box-sizing:border-box}body{margin:0;background:var(--ground);color:var(--ink);font-family:var(--font-sans);font-size:15px;line-height:1.55;-webkit-font-smoothing:antialiased}
/* Preserve pill fills, scorecard tints, and every other background when exporting to PDF /
   printing — browsers drop backgrounds by default unless a page opts in with print-color-adjust. */
.report,.report *{-webkit-print-color-adjust:exact;print-color-adjust:exact;color-adjust:exact}
@media print{.wrap{padding:0}body{background:#fff}.report{box-shadow:none;border:none}}
.wrap{max-width:920px;margin:0 auto;padding:28px 20px 80px}
.report{background:var(--surface);border:1px solid var(--hairline);border-radius:var(--radius);box-shadow:var(--shadow);overflow:hidden}
.r-header{padding:26px 32px 22px;border-bottom:1px solid var(--hairline)}
.r-eyebrow{font-family:var(--font-sans);font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--ink-faint);font-weight:600}
.r-title{font-size:23px;margin:8px 0 2px;font-weight:680;letter-spacing:-.01em}
.r-meta{margin-top:16px;display:flex;flex-wrap:wrap;gap:6px 22px;font-size:12.5px;color:var(--ink-soft)}
.r-meta .k{font-family:var(--font-sans);font-size:10.5px;letter-spacing:.06em;text-transform:uppercase;color:var(--ink-faint)}
.r-stamp{margin-top:10px;font-family:ui-monospace,'SFMono-Regular',Menlo,Consolas,monospace;font-size:11px;color:var(--ink-faint);letter-spacing:.02em;user-select:all;-webkit-user-select:all}
.r-attest{margin-top:5px;font-size:11px;color:var(--ink-soft);letter-spacing:.01em}
.trunc{margin:14px 0;padding:12px 16px;border-left:4px solid var(--sev-critical);background:var(--sev-critical-tint);border-radius:6px;color:var(--sev-critical);font-size:14px}
.report-inner{padding:28px 32px}
.section+.section{margin-top:30px}
.section-eyebrow{font-family:var(--font-sans);font-size:13px;letter-spacing:.08em;text-transform:uppercase;color:var(--ink);font-weight:700;margin:0 0 16px;padding-bottom:11px;border-bottom:1px solid var(--hairline-strong)}
.sub-block{margin-top:26px}
.sub-label{font-family:var(--font-sans);font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-faint);font-weight:700;margin:0 0 12px}
.eval-grid{display:grid;grid-template-columns:1fr 1fr;gap:26px 44px;align-items:start}
.eval-block .field-label{margin:0 0 14px;padding-bottom:8px;border-bottom:1px solid var(--hairline)}
.eval-dl{margin:0;display:flex;flex-direction:column;gap:13px}
.eval-row{display:block}
.eval-row dt{font-size:9.5px;letter-spacing:.06em;text-transform:uppercase;color:var(--ink-faint);font-weight:700;margin-bottom:2px}
.eval-row dd{margin:0;font-size:13.5px;color:var(--ink);line-height:1.45}
.eval-tasks{margin:0;padding:0;list-style:none;display:flex;flex-direction:column;gap:11px}
.eval-tasks li{font-size:13.5px;color:var(--ink);line-height:1.45;padding-left:16px;position:relative}
.eval-tasks li::before{content:"";position:absolute;left:0;top:8px;width:5px;height:5px;border-radius:50%;background:var(--brand)}
.eval-tasks li b{font-weight:640}
@media(max-width:680px){.eval-grid{grid-template-columns:1fr;gap:22px}}
.headline-lg{font-size:18px;font-weight:640;margin:0 0 10px;letter-spacing:-.01em}
.narrative{color:var(--ink-soft);margin:0;max-width:68ch}
/* Separate stacked summary paragraphs (narrative + Emergent-Patterns lines) so the bold verdict
   and the tenet-concentration prose never run together; no trailing gap before the scorecard. */
.narrative + .narrative{margin-top:10px}
.ep-line a{color:inherit;text-decoration:underline;text-decoration-style:dotted;text-underline-offset:2px}
.scorecard-wrap{overflow-x:auto}
table.scorecard{border-collapse:separate;border-spacing:0;width:100%;min-width:480px;table-layout:fixed;font-variant-numeric:tabular-nums}
.scorecard caption{text-align:left;font-family:var(--font-sans);font-size:10.5px;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-faint);padding-bottom:10px}
.scorecard th,.scorecard td{padding:9px 10px;text-align:center;border-bottom:1px solid rgba(128,132,140,.32)}
.scorecard thead th{font-family:var(--font-sans);font-size:11px;font-weight:700;letter-spacing:.08em;vertical-align:bottom;border-bottom:1px solid rgba(128,132,140,.55)}
.scorecard thead th .cap{display:block;font-weight:400;font-size:10.5px;letter-spacing:0;text-transform:none;color:var(--ink-faint);margin-top:4px;line-height:1.3}
.scorecard .corner{width:206px;background:transparent;border-bottom:1px solid rgba(128,132,140,.55)}
.scorecard tbody tr:last-child td{border-bottom:none}
.sc-high{color:var(--sev-critical)}.sc-med{color:var(--sev-medium)}.sc-low{color:var(--sev-low)}
.scorecard .corner-blank{background:transparent;border:none}
.scorecard .axis-top{font-family:var(--font-sans);font-size:10.5px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--ink-faint);text-align:center;padding:0 10px 7px;border-bottom:1px solid rgba(128,132,140,.32)}
.scorecard .axis-side{font-family:var(--font-sans);font-size:10.5px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-faint);text-align:left;vertical-align:bottom}
.scorecard .rowlab{text-align:left;font-size:13px;color:var(--ink);font-weight:560;white-space:nowrap}
.scorecard .rowlab small{display:block;font-weight:400;color:var(--ink-faint);font-size:11px}
.scorecard td.count{font-size:15.5px;font-weight:680}
.scorecard td.high{color:var(--sev-critical)}.scorecard td.med{color:var(--sev-medium)}.scorecard td.low{color:var(--sev-low)}
.scorecard td.zero{color:var(--ink-faint);font-weight:400}
.scorecard tbody tr td:nth-child(2){background:var(--sev-critical-tint)}
.scorecard tbody tr td:nth-child(3){background:var(--sev-medium-tint)}
.scorecard tbody tr td:nth-child(4){background:var(--sev-low-tint)}
/* Summary scorecard — the matrix leads the section in a subtly recessed panel (its own scan zone),
   set clearly apart from the verdict prose that follows. */
.summary-scorecard{background:var(--surface-sunk);border:1px solid var(--hairline);border-radius:var(--radius);padding:17px 20px 15px;margin:22px 0 26px}
.summary-scorecard .sub-label{margin:0 0 13px}
.summary-scorecard + .headline-lg{margin-top:0}
.card{border:1px solid var(--hairline);border-radius:var(--radius);background:var(--surface);margin-top:16px;padding:22px 24px;display:grid;grid-template-columns:var(--rail) 1fr;column-gap:28px;row-gap:18px;align-items:start;scroll-margin-top:16px}
.card+.card{margin-top:14px}
.card-rail{display:flex;flex-direction:column;gap:16px;min-width:0}
.card-main{min-width:0}
.card-num{display:block;font-family:var(--font-sans);font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:var(--ink-faint);font-weight:700;margin-bottom:8px}
.readouts-inline{display:flex;flex-wrap:wrap;align-items:baseline;gap:6px;margin:0 0 4px}
.ri-k{font-size:13px;color:var(--ink-soft)}
.ri-k::after{content:":";margin-left:1px;color:var(--ink-faint)}
.ri-sep{color:var(--ink-faint);margin:0 3px}
.ro-v{font-size:14px;font-weight:660;color:var(--ink);letter-spacing:-.01em}
.ro-v.s-high{color:var(--sev-critical)}.ro-v.s-medium{color:var(--sev-medium)}.ro-v.s-low{color:var(--sev-low)}
.ro-v.c-medium{color:var(--ink-soft);font-weight:600}.ro-v.c-low{color:var(--ink-faint);font-weight:600}
.card-headline{font-size:19px;line-height:1.3;font-weight:660;margin:0 0 6px;letter-spacing:-.015em}
.field{margin-top:16px}
.field-label{font-family:var(--font-sans);font-size:10.5px;letter-spacing:.1em;text-transform:uppercase;color:var(--ink-faint);font-weight:700;margin-bottom:6px}
.field p{margin:0;color:var(--ink)}.field.muted p{color:var(--ink-soft)}
.trap{display:flex;flex-direction:column;align-items:stretch;gap:6px}
.tenet{font-family:var(--font-sans);font-size:10px;font-weight:700;letter-spacing:.07em;text-transform:uppercase}
.tpill{align-self:flex-start;font-family:var(--font-sans);font-size:11.5px;font-weight:700;letter-spacing:.03em;text-transform:uppercase;color:#fff;padding:5px 11px;border-radius:6px;line-height:1.25;overflow-wrap:break-word}
/* Tenet pill fills are tuned for light grounds; lift them a touch on dark so they read. */
:root[data-theme="dark"] .tpill{filter:brightness(1.14) saturate(1.06)}
.rel{align-self:flex-start;font-family:var(--font-sans);font-size:9.5px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-faint);border:1px solid var(--hairline-strong);border-radius:5px;padding:2px 6px}
.tdef{margin:2px 0 0;padding:9px 12px;background:var(--surface-sunk);border-left:3px solid var(--ink-faint);border-radius:0 7px 7px 0;color:var(--ink-soft);font-size:11.5px;line-height:1.5}
.crop{margin:12px 0 0}.crop img{max-width:100%;max-height:320px;border:1px solid var(--hairline);border-radius:8px}
.crop figcaption{margin-top:6px;font-size:12px;color:var(--ink-faint)}
.cov-group+.cov-group{margin-top:32px}
.cov-grouplabel{font-family:var(--font-sans);font-size:11px;letter-spacing:.09em;text-transform:uppercase;color:var(--ink-soft);font-weight:700;margin:0 0 5px}
.cov-intro{font-size:12px;color:var(--ink-faint);margin:0 0 16px;max-width:66ch;line-height:1.55}
.coverage{display:flex;flex-wrap:wrap;gap:18px 22px}
.cov-item{display:flex;flex-direction:column;align-items:flex-start;gap:7px}
.cov-item.assess{flex:1 1 300px;max-width:420px}
.cov-item .cs{color:var(--ink-soft);font-size:11.5px;line-height:1.5}
.r-footer{border-top:1px solid var(--hairline);padding:16px 32px;font-size:11.5px;color:var(--ink-faint);font-family:var(--font-sans);letter-spacing:.03em}
@media (max-width:720px){.card{grid-template-columns:1fr;row-gap:16px}}
/* By-Trap report: a Trap card's main column lists the instances found of that trap. */
.trap-count{font-family:var(--font-sans);font-size:11px;letter-spacing:.07em;text-transform:uppercase;color:var(--ink-faint);font-weight:700;margin:2px 0 15px}
/* Trap card artwork in the By-Trap rail — one Trap per card, so the physical card fits. */
/* Small by default; the underlying PNG is high-res, so hovering scales it up to full
   resolution for readability. transform-origin keeps the zoom anchored in the rail. */
/* Cards that show a Trap's card artwork in the rail (By-Trap and By-Issue alike): narrow the
   rail to the card width so there's no dead space between the card and the description. */
.card.card-trapart{--rail:136px;column-gap:20px}
.trap-card-img{display:block;width:100%;max-width:134px;border-radius:10px;box-shadow:0 1px 5px rgba(0,0,0,.12);cursor:zoom-in;transition:transform .18s ease,box-shadow .18s ease;transform-origin:top left}
.trap-card-img:hover{transform:scale(2.1);box-shadow:0 12px 34px rgba(0,0,0,.32);position:relative;z-index:30}
@media (prefers-reduced-motion:reduce){.trap-card-img{transition:none}}
/* Task grouping in the By-Trap 'Traps identified' section. */
.task-group+.task-group{margin-top:30px}
.task-group-label{font-family:var(--font-sans);font-size:13.5px;font-weight:700;letter-spacing:.01em;color:var(--ink);margin:0 0 2px;padding-bottom:9px;border-bottom:2px solid var(--hairline-strong)}
.instance+.instance{margin-top:20px;padding-top:18px;border-top:1px solid var(--hairline)}
.inst-num{font-family:var(--font-sans);font-size:10px;letter-spacing:.09em;text-transform:uppercase;color:var(--ink-faint);font-weight:700;display:block;margin-bottom:8px}
/* Trap Disposition Index — one scannable row per taxonomy trap, accounted for exactly once. */
.disp-intro{font-size:12px;color:var(--ink-faint);margin:0 0 16px;max-width:70ch;line-height:1.55}
.disp-wrap{overflow-x:auto}
table.disposition{border-collapse:separate;border-spacing:0;width:100%;min-width:420px}
.disposition td{padding:7px 12px 7px 0;border-bottom:1px solid var(--hairline);vertical-align:middle}
.disposition tr:last-child td{border-bottom:none}
.disposition .dt-trap{width:1%;white-space:nowrap;padding-right:20px}
.disposition .dt-trap .tpill{font-size:10.5px;padding:4px 9px}
.disposition .dt-disp{font-size:13px;color:var(--ink-soft);line-height:1.45}
.disp-link{color:var(--brand);font-weight:640;text-decoration:none;border-bottom:1px solid transparent}
.disp-link:hover{border-bottom-color:currentColor}
.disp-rel{color:var(--ink-faint);font-weight:400}
.disp-cov{color:var(--ink-soft)}
.disp-sep{color:var(--ink-faint);margin:0 7px}
.disp-none{color:var(--sev-critical);font-weight:600}
"""


# Emergent Patterns tenet cash-out glosses are KB-OWNED and read at runtime — the tool holds NO
# copy (KB Ledger 23; superseding the old "tool holds a synced verbatim copy" model). They are
# parsed once from the loaded KB and rendered verbatim; see knowledge_extractor.load_tenet_glosses.
_EP_NUM = {2: "Two", 3: "Three", 4: "Four", 5: "Five", 6: "Six", 7: "Seven", 8: "Eight", 9: "Nine"}


def _ep_join(items: list) -> str:
    """Oxford-comma join of already-cleaned phrases."""
    items = [i for i in items if i]
    if len(items) <= 1:
        return items[0] if items else ""
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return ", ".join(items[:-1]) + ", and " + items[-1]


def _priority_handle(f: dict) -> str:
    """Short 3-5 word handle for the priority statement. Prefers the model-authored `handle` field
    (schema); falls back to a trimmed headline as a crash-guard only (LOSSY)."""
    h = str(f.get("handle") or "").strip()
    if h:
        return h
    return " ".join(str(f.get("headline") or "").strip().split()[:5])


def _compute_card_numbers(findings, task_names, uc):
    """SINGLE SOURCE for trap-card numbering — {id(finding): card number}. Replicates
    _emit_trap_cards' grouping EXACTLY (flat, or General then Task 1..N; first-seen distinct trap PER
    BUCKET keyed by str(trap_name).strip().upper() — the emitter's own key, UNCHANGED, so no
    STEP(S)/STEPS merge; idx continuous across buckets) without emitting HTML, and maps every finding
    to its card's number. Both the priority statement (worst-instance finding) and _emit_trap_cards
    (a card's instances) read this map, so their numbers cannot drift. Keyed by id() — VALID ONLY
    because both consumers receive the same `_findings` objects (the sole copy is the one `{**f, ...}`
    flatten in _format_new_kb_bytrap_html; nothing downstream re-copies or rebuilds them)."""
    findings = [f for f in (findings or []) if isinstance(f, dict) and f.get("trap_name")]

    def _key(f):
        return str(f.get("trap_name") or "").strip().upper()

    buckets = [findings]                                    # flat default (no task grouping)
    if len(task_names) > 1:
        def _match(tc):                                     # identical to _emit_trap_cards' _match_task
            tcl = (tc or "").strip().lower()
            if not tcl:
                return None
            for nm in task_names:
                if tcl == nm.lower():
                    return nm
            best = None
            for nm in task_names:
                nl = nm.lower()
                if (tcl in nl or nl in tcl) and (best is None or len(nm) > len(best)):
                    best = nm
            return best
        general, tb = [], OrderedDict((nm, []) for nm in task_names)
        for f in findings:
            m = _match(f.get("task") or f.get("task_context"))
            (tb[m] if m in tb else general).append(f)
        if any(tb.values()):
            buckets = ([general] if general else []) + [tb[nm] for nm in task_names if tb[nm]]
    numbers, idx = {}, 0
    for bucket in buckets:
        seen = {}
        for f in bucket:
            k = _key(f)
            if k not in seen:
                idx += 1
                seen[k] = idx
            numbers[id(f)] = seen[k]                         # every instance -> its card's number
    return numbers


def _emergent_patterns_html(report: dict, findings: list, version: str = "v2", card_numbers: dict = None) -> list:
    """Render-time DERIVATION (NO model call) of the opening Emergent Patterns synthesis
    (KB G8 / Ledger 22). Failure-side, observation register, descriptive-only — never an
    imperative, never a severity change. Reads the retained issue-level substrate (issue_groups)
    plus the fired findings' Tenets; no fresh cross-Trap/cross-Tenet pass. Two independent axes
    (both may fire). Omitted entirely when there are no findings. Inputs are pre-escaped by the
    public entry, so dynamic values (location, headlines) are appended without re-escaping.

    The tenet cash-out glosses are read VERBATIM from the KB (version-scoped) once per render — the
    tool holds no copy (Ledger 23)."""
    findings = [f for f in (findings or []) if isinstance(f, dict)]
    if not findings:
        return []

    lines = []  # at most one line: the priority statement

    # ── Priority statement (d2bb63cb) — replaces the former axis-(a) region lines and axis-(b)
    # tenet-characterization line (both removed, along with the now-pointless per-render TENET-GLOSSES
    # read; the block stays in the KB, just no longer read). Names the <=3 highest-priority Traps,
    # severity-led (High > Medium > Low), then root-cause Traps before standalone among ties.
    # Descriptor from the model `handle` field (headline-trim crash-fallback only); no render-time Trap
    # numbers. Its own short paragraph, ALWAYS emitted when any Trap fired.
    #
    # Two root-cause sets, deliberately different (KB line 34 forbids a cascade claim for independent
    # co-failures): `_root_cause` (LOOSE - root_cause in ANY group) drives ordering/tiebreak only,
    # which makes no output claim; `_cascade` (STRICT - root_cause in a group that ALSO holds >=1
    # `consequence` trap, i.e. a root cause with real dependents) is the ONLY gate on the "also clears
    # smaller issues" clause. A root-cause-labelled trap with no co-occurring consequence therefore
    # gets impact-only phrasing, never the cascade clause. Forbidden in output: adjudication / root
    # cause / region / locus / concentrate, and Tenet names.
    _SEVR = {"High": 3, "Medium": 2, "Low": 1}
    _root_cause: "set" = set()   # loose: ordering/tiebreak only (no cascade claim)
    _cascade: "set" = set()      # strict: root_cause in a group that also holds a consequence trap
    for _g in (report.get("issue_groups") or []):
        if not isinstance(_g, dict):
            continue
        _gt = [_t for _t in (_g.get("traps") or []) if isinstance(_t, dict)]
        _rels = [normalize_relationship(_t.get("relationship")) for _t in _gt]
        _has_consequence = "consequence" in _rels
        for _t, _rel in zip(_gt, _rels):
            if _rel == "root_cause":
                _rcnm = _normalize_trap_name(_t.get("trap_name", ""))
                if _rcnm:
                    _root_cause.add(_rcnm)
                    if _has_consequence:
                        _cascade.add(_rcnm)
    # One entry per DISTINCT fired Trap: (sev_rank, handle, is_root_cause_loose, cascade_ok). Worst
    # severity kept when a Trap fires more than once.
    _by_trap = OrderedDict()
    for f in findings:
        nm = _normalize_trap_name(f.get("trap_name", ""))
        if not nm:
            continue
        sev = _SEV_NORM.get((f.get("severity_label") or "").strip().lower()) or f.get("_src_sev") or "Medium"
        rank = _SEVR.get(sev, 2)
        prev = _by_trap.get(nm)
        if prev is None or rank > prev[0]:
            _by_trap[nm] = (rank, _priority_handle(f), nm in _root_cause, nm in _cascade, f)  # +worst instance
    _ranked = sorted(_by_trap.values(), key=lambda e: (-e[0], not e[2]))[:3]   # sev desc, root-cause first

    def _lab(handle, wf):
        # Visible "(Trap NN)" that also links to the card (id="trap-NN"). Number from the shared
        # card-numbers map, keyed by the worst-instance finding's id() — exactly the card that
        # instance renders under (same object identity as _emit_trap_cards; guaranteed to match).
        n = card_numbers.get(id(wf)) if card_numbers else None
        return f'{handle} (<a href="#trap-{n:02d}">Trap {n:02d}</a>)' if n else handle

    _descs = [_lab(h, wf) for (_r, h, _rc, _c, wf) in _ranked if h]
    if _descs:
        _lead = "The priority here is " if len(_descs) == 1 else "The priorities here, worst first, are "
        _stmt = _lead + _ep_join(_descs) + "."
        _cascade_h = [_lab(h, wf) for (_r, h, _rc, _c, wf) in _ranked if _c and h]   # STRICT gate; numbered too
        if _cascade_h:
            _stmt += f" Fixing {_ep_join(_cascade_h)} also clears smaller issues."
        lines.append(_stmt)

    # Bare paragraphs — folded into the Summary section above the scorecard, no subtitle.
    return [f"<p class='narrative ep-line'>{ln}</p>" for ln in lines]


# Class-gap remedies (the settling artifact), computed from the floor — the relay's "generic remedy
# from the class gap" where the KB scoped-coverage string isn't surfaced here.
_CLASS_GAP_REMEDY = {"disconnected-screens": "needs a second screen to observe this trap",
                     "flow": "needs the screen-to-screen flow to observe this trap",
                     "live": "needs the live product to observe this trap",
                     "code": "needs the source to observe this trap"}


def _apply_disposition_gate(report: dict, settings: dict) -> None:
    """Disposition gate — G4 three-state rule (Ledger 26/27), applied IN PLACE to traps_checked_not_found.
    Each `not_present` verdict is re-routed by observability class and the Trap's KB-owned floor:

      • below floor (unobservable, incl. unknown Trap) → "Couldn't evaluate" (not_assessable_artifact)
        with a class-gap remedy.
      • PARTIAL Trap AT its floor → scoped clearance (Ledger 27, Option 3): re-routed to
        `partially_assessed` rendering the KB's pulled scoped-coverage string — the Trap cleared only
        its floor-supported sub-scope, NEVER a bare "Not present." The string is KB-owned; the tool
        never synthesizes scope language.
      • otherwise observable (non-partial at/above floor, or a partial ABOVE its floor):
          – with named G6 disconfirming evidence (the coverage `detail`) → stays "Not present" (hard clear).
          – without it → "Couldn't evaluate" (the clear was unjustified).

    v2 COACHED ONLY: self-serve is the raw-KB condition that tests whether the model applies G4 unaided,
    so the tool must not enforce it there; v1 / v1.1 carry no digest.

    Idempotent (only `not_present` entries are ever touched), so it is safe to run once on the source
    report — so the markdown export and the returned object agree with the HTML — AND again on the
    escaped render copy inside the formatter, without double-counting.
    """
    _ver = str(settings.get("kb_version", "v2")).strip().lower()
    if _ver != "v2" or str(settings.get("profile", "")).strip().lower() == "self-serve":
        return
    try:
        from .knowledge_extractor import load_assessability_digest, load_scoped_coverage, ARTIFACT_CLASS_RANK
    except ImportError:
        from knowledge_extractor import load_assessability_digest, load_scoped_coverage, ARTIFACT_CLASS_RANK
    # Re-key the KB digest + scoped strings through the formatter's normalizer so `STEP(S)` etc. match
    # the finding side (the loaders keep the raw KB spelling; both sides must fold identically). Fresh
    # dicts each call — the cached KB values are never mutated.
    _digest = {_normalize_trap_name(k): v for k, v in load_assessability_digest("v2").items()}
    _scoped = {_normalize_trap_name(k): v for k, v in load_scoped_coverage("v2").items()}
    _ac = str(settings.get("artifact_class", "static-screenshot")).strip().lower()
    _ac_rank = ARTIFACT_CLASS_RANK.get(_ac, 0)     # unknown/absent class → most restrictive rung
    for _c in report.get("traps_checked_not_found") or []:
        if not isinstance(_c, dict) or _c.get("coverage_status") != "not_present":
            continue
        _nm = _normalize_trap_name(_c.get("trap_name", ""))
        _floor = _digest.get(_nm)
        # (1) Below floor / unknown Trap → not observable at all → Couldn't evaluate.
        if _floor is None or _ac_rank < _floor[0]:
            _c["coverage_status"] = "not_assessable_artifact"
            if _floor is not None:
                _c["_assess_remedy"] = _CLASS_GAP_REMEDY.get(_floor[1], "needs a richer artifact to observe this trap")
            continue
        # (2) PARTIAL Trap AT its floor → scoped clearance: partially_assessed with the KB scoped string,
        # never a bare "Not present." (Above its floor the fuller scope is observable, so a partial falls
        # through to the hard-clear rule below like a non-partial.)
        if _floor[2] and _ac_rank == _floor[0]:
            _c["coverage_status"] = "partially_assessed"
            _s = _scoped.get(_nm)
            if _s:
                # Drop the leading "Trap Name — " (the coverage pill already shows the name) — a
                # mechanical de-dup of the KB string, not a rewrite of its scope language.
                _lead, _sep, _rest = _s.partition(" — ")
                _c["detail"] = _rest if (_sep and _normalize_trap_name(_lead) == _nm) else _s
            continue
        # (3) Observable (non-partial, or partial above floor): honest "Not present" needs cited G6.
        if bool(str(_c.get("detail") or "").strip()):
            continue                                # a legitimate "Not present" — leave it standing
        _c["coverage_status"] = "not_assessable_artifact"
        _c["_assess_remedy"] = "no disconfirming evidence was cited to rule it out"


# In-report click interceptor for the priority statement's "(Trap NN)" links. The report renders in
# an `<iframe srcDoc>`, whose document (about:srcdoc) resolves a bare `#trap-NN` fragment against the
# PARENT app URL — so an unhandled click navigates the iframe to the app (the form) instead of
# scrolling. This catches clicks on the trap-anchor links only and scrolls within THIS document, which
# owns both the links and the id="trap-NN" targets. Scoped to a[href^="#trap-"]; all other links and
# the numbering/ids/sentence are untouched.
_TRAP_ANCHOR_JS = (
    "<script>document.addEventListener('click',function(e){"
    "var t=e.target,a=t&&t.closest?t.closest('a[href^=\"#trap-\"]'):null;"
    "if(!a)return;e.preventDefault();"
    "var el=document.getElementById(a.getAttribute('href').slice(1));"
    "if(el)el.scrollIntoView({behavior:'smooth',block:'start'});});</script>"
)


def _format_new_kb_bytrap_html(report: dict, user_context: dict, settings: dict) -> str:
    """Render the new-KB BY-TRAP report in the rev6 style — one entry per Trap, each listing
    the instances found (or, for traps with none, grouped compactly under Coverage notes).
    Reuses the By-Issue CSS and chrome so the two reports look identical; only the middle
    body differs (trap-centric vs issue-centric). Input is pre-escaped."""
    uc = user_context or {}
    # Lineage for taxonomy resolution: v1 / v1.1 renders read the FROZEN v1.0 tenet map; everything
    # else reads the v2 table. Threaded into every _tenet_for call below so no v1 render is
    # colored/labelled/grouped by the v2 taxonomy.
    _ver = str(settings.get("kb_version", "v2")).strip().lower()

    def sevc(label):
        return _SEV_CLASS.get((label or "").strip().lower(), "medium")

    # Flatten every finding (instance) from the severity arrays, then group by trap name in
    # first-seen order. Each finding is one observed instance of its trap.
    from collections import OrderedDict
    _SRC_SEV = {"critical_issues": "High", "moderate_issues": "Medium", "minor_issues": "Low"}
    _findings = []
    for _arr in ("critical_issues", "moderate_issues", "minor_issues"):
        for f in report.get(_arr) or []:
            if isinstance(f, dict) and f.get("trap_name"):
                # Tag each finding with the severity implied by the array it arrived in, so a
                # missing/off-enum severity_label falls back to the model's array placement
                # rather than a blanket "Medium" (self-serve by-trap leaves severity_label optional).
                _findings.append({**f, "_src_sev": _SRC_SEV[_arr]})

    # Card numbering — SINGLE SOURCE for both the priority statement and the trap cards, keyed by
    # id() of each finding. Task names are hoisted here (they were computed in the cards section
    # below) so the map is ready before the priority statement (EP) renders. id()-keying is valid
    # ONLY because these same `_findings` objects flow into BOTH _emergent_patterns_html and
    # _emit_trap_cards with no copy/rebuild in between (the sole copy is the `{**f, ...}` flatten
    # above; the task bucketing below appends references).
    _tl = uc.get("task_list") or []
    _task_names = [(_t.get("name") or _t.get("description") or "").strip()
                   for _t in _tl if isinstance(_t, dict) and (_t.get("name") or _t.get("description"))]
    if len(_task_names) <= 1 and uc.get("tasks"):
        _pt = [t for t in parse_tasks(uc.get("tasks", "")) if t]
        if len(_pt) > 1:
            _task_names = _pt
    _card_numbers = _compute_card_numbers(_findings, _task_names, uc)

    # Disposition gate FIRST (G4 three-state rule) — it re-routes unsupportable "not present" verdicts
    # to "Couldn't evaluate". Emergent Patterns' assessability leash counts un-inspectable Traps, so it
    # MUST read post-gate statuses; running the gate here (before EP) keeps the exec-summary tenet
    # concentration from asserting what the gate below then withdraws. Idempotent if already run at the
    # source (analyzer): only `not_present` entries are ever touched.
    _apply_disposition_gate(report, settings)

    # Emergent Patterns computed ONCE here and reused in the Summary body below, so the attestation
    # line can state the ACTUAL render outcome (emitted or not), never an assumption. v1 / v1.1
    # suppress it entirely (Ledger 22 is v2 material).
    _ep_lines = _emergent_patterns_html(report, _findings, version=_ver,
                                        card_numbers=_card_numbers) if _ver not in ("v1", "v1.1") else []

    # ── Runtime provenance (RELAY B) — facts the tool verifies for THIS run, never hardcoded. KB
    # sha is sha256 of the loaded KB file; build sha is env/git; the isolation / full-stack items
    # derive from the ACTUAL config + render path (they attest INPUTS/paths, not output quality). ──
    try:
        from .knowledge_extractor import kb_file_sha256, build_sha
    except ImportError:
        from knowledge_extractor import kb_file_sha256, build_sha
    _kb_sha = kb_file_sha256(settings.get("kb_version", "v2"))
    _build = build_sha()
    _is_v1 = _ver in ("v1", "v1.1")
    _profile = str(settings.get("profile", "")).strip().lower()
    _selfserve = _profile == "self-serve"
    _twopass = settings.get("mode") == "twopass"
    _ep_rendered = bool(_ep_lines)

    # ── header meta (identical to By-Issue) ──
    _meta = []
    _meta.append(("KB", settings.get("kb_version", "v2")))
    _meta.append(("Architecture", "Two-pass" if settings.get("mode") == "twopass" else "Single-pass"))
    _meta.append(("Coverage", "Thorough" if settings.get("thorough_mode") else "Standard"))
    _meta.append(("Report style", "By Trap"))
    if settings.get("verbosity"):
        _meta.append(("Verbosity", str(settings["verbosity"]).title()))
    if settings.get("pass1_model"):
        _meta.append(("Pass-1 model", str(settings["pass1_model"]).title()))
    _el = settings.get("elapsed_seconds")
    if _el is not None:
        _m, _s = divmod(int(_el), 60)
        _meta.append(("Time", f"{_m}m {_s}s" if _m else f"{_s}s"))
    _usage = settings.get("usage") or {}
    _tok = (_usage.get("input", 0) or 0) + (_usage.get("output", 0) or 0) + (_usage.get("cache_read", 0) or 0) + (_usage.get("cache_creation", 0) or 0)
    if _tok:
        _meta.append(("Tokens", f"{_tok:,}"))
    if _usage.get("cost") is not None:
        _meta.append(("Est. cost", f"${_usage['cost']:,.4f}"))

    design_name = uc.get("design_name") or "UI analysis"
    h = ['<!DOCTYPE html>', "<html lang='en'>", "<head><meta charset='UTF-8'>",
         "<meta name='viewport' content='width=device-width, initial-scale=1.0'>",
         "<title>UI Traps — By Trap</title>",
         "<link rel='preconnect' href='https://fonts.googleapis.com'>",
         "<link rel='preconnect' href='https://fonts.gstatic.com' crossorigin>",
         "<link href='https://fonts.googleapis.com/css2?family=Montserrat:wght@400..700&display=swap' rel='stylesheet'>",
         f"<style>{_NEW_KB_ISSUES_CSS}</style>",
         "</head><body data-selftheme='1'>", "<div class='wrap'>", "<div class='report'>"]

    # header
    h.append("<div class='r-header'>")
    h.append("<div class='r-eyebrow'>UI Tenets &amp; Traps · Analysis Report</div>")
    h.append(f"<div class='r-title'>{design_name}</div>")
    h.append("<div class='r-meta'>")
    for k, v in _meta:
        h.append(f"<span><span class='k'>{k}</span> {v}</span>")
    h.append("</div>")
    # Provenance stamp — the true version + shas as facts (no staleness verdict; a-simple). Copyable.
    h.append(f"<div class='r-stamp'>KB {settings.get('kb_version', 'v2')} · {_kb_sha} · build {_build or 'unavailable'}</div>")
    # Isolation / full-stack attestation — each item a runtime fact about what was loaded/applied
    # THIS run. v1: confirmed-clean INPUTS/paths (NOT a leak-free-output guarantee). v2: components
    # PRESENT/APPLIED (NOT a performance/optimality claim). A contradicting fact is stamped as-is.
    if _is_v1:
        _att = [
            f"KB {_kb_sha}",
            "v1 taxonomy",
            ("no Emergent Patterns" if not _ep_rendered else "Emergent Patterns RENDERED (unexpected)"),
            ("self-serve (no v2 scaffolding)" if _selfserve
             else f"profile {_profile or 'unknown'} — NOT self-serve"),
        ]
        h.append("<div class='r-attest'>v1.0 isolated — " + " · ".join(_att) + "</div>")
    else:
        _coached = not _selfserve
        _att = [
            f"KB {_kb_sha}",
            ("system-prompt know-how ✓" if _coached else "system-prompt know-how — (self-serve, KB-only)"),
            ("two-pass ✓" if _twopass else "two-pass — (not applied)"),
            ("Emergent Patterns ✓" if _ep_rendered
             else ("Emergent Patterns — (no findings)" if not _findings
                   else "Emergent Patterns — (no reportable pattern)")),
            ("exec-voice ✓" if _coached else "exec-voice — (self-serve, KB-only)"),
        ]
        h.append("<div class='r-attest'>v2 full stack — " + " · ".join(_att) + "</div>")
    h.append("</div>")

    if settings.get("truncated"):
        h.append("<div class='trunc'>⚠️ <b>Incomplete report:</b> the analysis output was cut off at the length limit, so some traps or coverage notes may be missing. Re-running usually resolves this.</div>")
    if settings.get("frame_notice"):
        # Truncation disclosure (e.g. a large Figma file capped to the first N frames). States
        # analyzed AND skipped counts so an un-analyzed-frame miss reads as truncation, not a KB gap.
        h.append(f"<div class='trunc'>ℹ️ <b>Partial coverage:</b> {settings['frame_notice']}</div>")

    h.append("<div class='report-inner'>")

    # evaluation details (identical to By-Issue)
    _emit_eval_details(h, uc)

    # summary section — the "Number of Traps found" matrix leads, then the verdict prose (headline,
    # narrative, Emergent Patterns). Matrix-first per layout request: the scorecard is the at-a-glance
    # scan, so it sits at the top of the section above the exec-voice paragraph.
    h.append("<div class='section'><div class='section-eyebrow'>Summary of findings</div>")
    _rows, _cols = _SCORE_ROWS, _SCORE_COLS
    _counts = {(r, c[0]): 0 for r in _rows for c in _cols}
    _sev_norm, _conf_norm = _SEV_NORM, _CONF_NORM
    # Count DISTINCT traps (one per trap card below), NOT flattened instances: a trap that fires N
    # times is one Trap, so it lands in exactly one cell — that of its WORST instance (highest
    # severity, then highest confidence). This keeps the "Number of Traps found" total in agreement
    # with the one-card-per-trap enumeration instead of inflating when a trap has multiple instances.
    # Grouping key matches _emit_trap_cards (str.strip().upper()) so the counts track the cards.
    _rank = {"High": 3, "Medium": 2, "Low": 1}
    _worst_cell: dict = {}   # trap name -> ((sev_rank, conf_rank), conf, sev)
    for i in _findings:
        _tn = str(i.get("trap_name") or "").strip().upper()
        if not _tn:
            continue
        sev = _sev_norm.get((i.get("severity_label") or "").strip().lower()) or i.get("_src_sev") or "Medium"
        conf = _conf_norm.get((i.get("confidence") or "").strip().lower(), "Low")
        _rk = (_rank.get(sev, 2), _rank.get(conf, 1))
        if _tn not in _worst_cell or _rk > _worst_cell[_tn][0]:
            _worst_cell[_tn] = (_rk, conf, sev)
    for _rk, conf, sev in _worst_cell.values():
        _counts[(conf, sev)] += 1
    h.append("<div class='sub-block summary-scorecard'><div class='sub-label'>Number of Traps found</div><div class='scorecard-wrap'>")
    h.append("<table class='scorecard'><thead>")
    h.append("<tr><td class='corner-blank'></td><th class='axis-top' colspan='3'>Severity</th></tr>")
    h.append("<tr><th class='axis-side'>Confidence</th>")
    for label, cap, cls in _cols:
        h.append(f"<th class='sc-{cls}'>{label.upper()}<span class='cap'>{cap}</span></th>")
    h.append("</tr></thead><tbody>")
    for rlabel in _rows:
        h.append(f"<tr><td class='rowlab'>{rlabel}</td>")
        for label, cap, cls in _cols:
            n = _counts[(rlabel, label)]
            h.append(f"<td class='count {cls}'>{n}</td>" if n else "<td class='count zero'>—</td>")
        h.append("</tr>")
    h.append("</tbody></table></div></div>")   # close table, scorecard-wrap, sub-block (NOT the section)
    # verdict prose beneath the matrix: headline, narrative, then Emergent Patterns (no subtitle;
    # computed once above as _ep_lines, gated there — v2 material only, suppressed for v1 / v1.1).
    if report.get("summary_headline"):
        h.append(f"<p class='headline-lg'>{report['summary_headline']}</p>")
    if report.get("summary_narrative"):
        h.append(f"<p class='narrative'>{report['summary_narrative']}</p>")
    h.extend(_ep_lines)
    h.append("</div>")   # close the summary section

    # ── Traps identified — one card per trap. For a multi-task analysis, cards are grouped
    # under "General" then "Task N: <name>"; a finding's task_context assigns it (best-match).
    def _emit_trap_cards(findings):
        """Group `findings` by trap name (first-seen order) and emit one card per trap. The card
        NUMBER is read from the shared `_card_numbers` map (keyed by id() of the instance) — the SAME
        map the priority statement read — so the card's "Trap N" and the sentence's "(Trap N)" match
        by construction. The card also carries id="trap-NN" so the sentence's anchor can jump to it."""
        by_trap = OrderedDict()
        for f in findings:
            if isinstance(f, dict) and f.get("trap_name"):
                by_trap.setdefault(str(f["trap_name"]).strip().upper(), []).append(f)
        for tname, instances in by_trap.items():
            first = instances[0]
            number = _card_numbers.get(id(first), 0)   # same map, same objects as the priority statement
            tenet = (first.get("tenet") or "").upper() or (_tenet_for(tname, version=_ver) or "").upper()
            color = _TENET_PILL.get(tenet, "#35597F")
            definition = first.get("definition") or ""
            h.append(f"<div class='card card-trapart' id='trap-{number:02d}'>")
            # rail — the Trap's card artwork (one Trap per card, so it fits). The card carries
            # the tenet, name, and definition; only when there is no card art do we fall back
            # to the rev6 tenet eyebrow + pill + text definition.
            h.append("<div class='card-rail'><div class='trap'>")
            _card_img = _get_card_img(tname)
            if _card_img:
                h.append(f"<img class='trap-card-img' src='{_card_img}' alt='{tname} trap card' loading='lazy'>")
            else:
                if tenet:
                    h.append(f"<span class='tenet' style='color:{color}'>{tenet.title()}</span>")
                h.append(f"<span class='tpill' style='background:{color}'>{tname}</span>")
                if definition:
                    h.append(f"<p class='tdef' style='border-color:{color}'>{definition}</p>")
            h.append("</div></div>")
            # main — the instances found of this trap
            h.append("<div class='card-main'>")
            h.append(f"<span class='card-num'>Trap {number:02d}</span>")
            _n = len(instances)
            # Count line only when there is more than one instance (a single instance is self-evident).
            if _n > 1:
                h.append(f"<div class='trap-count'>{_n} instances found</div>")
            for j, inst in enumerate(instances, 1):
                sl = _sev_norm.get((inst.get("severity_label") or "").strip().lower()) or inst.get("_src_sev") or "Medium"
                _cf_raw = (inst.get("confidence") or "").strip()
                # Same normalization+fallback as the scorecard (blank/off-vocab → "Low") so card
                # and matrix agree.
                cf = _conf_norm.get(_cf_raw.lower(), "Low")
                sc = sevc(sl)
                h.append("<div class='instance'>")
                if _n > 1:
                    h.append(f"<span class='inst-num'>Instance {j}</span>")
                # Headline — the specific problem observed (a concrete instance of the general trap).
                if inst.get("headline"):
                    h.append(f"<p class='card-headline'>{inst['headline']}</p>")
                h.append("<div class='readouts-inline'>")
                h.append(f"<span class='ri-k'>Severity</span><span class='ro-v s-{sc}'>{sl}</span>")
                if cf:
                    h.append(f"<span class='ri-sep'>|</span><span class='ri-k'>Confidence</span><span class='ro-v c-{cf.strip().lower()}'>{cf}</span>")
                h.append("</div>")
                # One "Description" (the location is woven into the prose when it helps), rather
                # than separate Where / What's happening fields — matches the By-Issue card.
                _desc = (inst.get("problem") or "").strip()
                if not _desc and inst.get("location"):
                    _desc = inst["location"]  # fall back to bare location if that's all we have
                if _desc:
                    h.append(f"<div class='field muted'><div class='field-label'>Description</div><p>{_desc}</p></div>")
                # One crop per cited instance (regions[]) — multi-screen findings crop per screen.
                for _rg in (inst.get("regions") or []):
                    if not isinstance(_rg, dict) or not _rg.get("image_b64"):
                        continue
                    _cap = _rg.get("caption") or ""
                    h.append("<figure class='crop'>")
                    h.append(f"<img src='data:image/png;base64,{_rg['image_b64']}' alt='Region crop'>")
                    if _cap:
                        h.append(f"<figcaption>{_cap}</figcaption>")
                    h.append("</figure>")
                if inst.get("recommendation"):
                    h.append(f"<div class='field'><div class='field-label'>Recommendation</div><p>{inst['recommendation']}</p></div>")
                h.append("</div>")  # .instance
            h.append("</div>")  # .card-main
            h.append("</div>")  # .card

    h.append("<div class='section'><div class='section-eyebrow'>Traps identified</div>")
    if not _findings:
        h.append("<p class='narrative'>No traps were found for the stated users and tasks.</p>")
    else:
        # _task_names was computed above (hoisted before the priority statement, which shares the
        # _card_numbers map _emit_trap_cards reads).
        if len(_task_names) > 1:
            def _match_task(tc):
                tcl = (tc or "").strip().lower()
                if not tcl:
                    return None
                # Exact match wins; otherwise the LONGEST task name in a containment relationship,
                # so a short name listed first ("Search") can't steal a finding tagged with a
                # longer one ("Search and filter results").
                for nm in _task_names:
                    if tcl == nm.lower():
                        return nm
                _best = None
                for nm in _task_names:
                    _nl = nm.lower()
                    if (tcl in _nl or _nl in tcl) and (_best is None or len(nm) > len(_best)):
                        _best = nm
                return _best
            _general = []
            _task_buckets = OrderedDict((nm, []) for nm in _task_names)
            for f in _findings:
                # `task` is the field the model fills; `task_context` is a tolerated alias.
                m = _match_task(f.get("task") or f.get("task_context")) if isinstance(f, dict) else None
                (_task_buckets[m] if m in _task_buckets else _general).append(f)
            if not any(_task_buckets.values()):
                # No finding was attributed to a task (e.g. the KB-only bare schema emits no
                # task_context) — a lone "General" heading would be noise, so render flat.
                _emit_trap_cards(_findings)
            else:
                # General first, then each task in order — empty groups are skipped. Numbers come
                # from the shared _card_numbers map, so no running index needs threading here.
                if _general:
                    h.append("<div class='task-group'><div class='task-group-label'>General</div>")
                    _emit_trap_cards(_general)
                    h.append("</div>")
                for _i, nm in enumerate(_task_names, 1):
                    if _task_buckets[nm]:
                        h.append(f"<div class='task-group'><div class='task-group-label'>Task {_i}: {nm}</div>")
                        _emit_trap_cards(_task_buckets[nm])
                        h.append("</div>")
        else:
            _emit_trap_cards(_findings)
    h.append("</div>")  # traps section

    # ── Worth a closer look (G8 §2) — pivotal, assessability-blocked unknowns. PARITY with the
    # By-Issue report: without this, a coached by-trap run silently dropped every potential_issues
    # entry the model produced. Same rev6 card style; ungrouped by task. ──
    _closer = [c for c in report.get("potential_issues") or [] if isinstance(c, dict)]
    if _closer:
        h.append("<div class='section' id='worth-a-closer-look'><div class='section-eyebrow'>Worth a closer look</div>")
        h.append("<p class='narrative'>Pivotal unknowns that couldn't be settled from this artifact — each names a check that would resolve it.</p>")
        for _c in _closer:
            _pname = _c.get("trap_name", "")
            _tn = (_c.get("tenet") or "").upper() or (_tenet_for(_pname, version=_ver) or "").upper()
            _color = _TENET_PILL.get(_tn, "#35597F")
            h.append("<div class='card card-trapart'>")
            h.append("<div class='card-rail'><div class='trap'>")
            _img = _get_card_img(_pname)
            if _img:
                h.append(f"<img class='trap-card-img' src='{_img}' alt='{_pname} trap card' loading='lazy'>")
            else:
                if _tn:
                    h.append(f"<span class='tenet' style='color:{_color}'>{_tn.title()}</span>")
                h.append(f"<span class='tpill' style='background:{_color}'>{_pname}</span>")
            h.append("</div></div>")  # .trap, .card-rail
            h.append("<div class='card-main'>")
            h.append("<span class='card-num'>Worth a closer look</span>")
            _hl = _c.get("why_it_matters") or _c.get("observation") or _pname
            if _hl:
                h.append(f"<p class='card-headline'>{_hl}</p>")
            _loc = _c.get("location") or ""
            if _loc:
                h.append(f"<div class='field muted'><div class='field-label'>Where</div><p>{_loc}</p></div>")
            _obs = _c.get("observation") or ""
            if _obs:
                h.append(f"<div class='field muted'><div class='field-label'>What's visible</div><p>{_obs}</p></div>")
            _chk = _c.get("check") or ""
            if _chk:
                _cost = _c.get("check_cost") or ""
                _cost_str = f" <em>({_cost})</em>" if _cost else ""
                h.append(f"<div class='field'><div class='field-label'>The check</div><p>{_chk}{_cost_str}</p></div>")
            _ifc = _c.get("implication_if_confirmed") or ""
            _ifr = _c.get("implication_if_ruled_out") or ""
            if _ifc or _ifr:
                h.append("<div class='field'><div class='field-label'>Implications</div>")
                if _ifc:
                    h.append(f"<p><strong>If confirmed:</strong> {_ifc}</p>")
                if _ifr:
                    h.append(f"<p><strong>If ruled out:</strong> {_ifr}</p>")
                h.append("</div>")
            h.append("</div>")  # .card-main
            h.append("</div>")  # .card
        h.append("</div>")  # worth-a-closer-look section

    # ── Coverage notes — traps with NO instances (identical buckets to By-Issue) ──
    cov = [c for c in report.get("traps_checked_not_found") or [] if isinstance(c, dict)]
    # Mutual exclusivity: a trap accounted for elsewhere must not ALSO surface as a coverage bucket
    # (partially_assessed may co-exist per J27). "Elsewhere" = a per-trap finding (`_raised`) OR a
    # secondary binding inside an issue_groups issue (`_secondary_names`) — the disposition index gives
    # both precedence over coverage, so a coverage "Not found" for such a trap would contradict the
    # index (e.g. a trap shown "Within an issue (consequence)" there and "Not found" here).
    _raised = {_normalize_trap_name(f.get("trap_name", "")) for f in _findings}
    _raised.discard("")
    _secondary_names = {_normalize_trap_name(_t.get("trap_name", ""))
                        for _g in (report.get("issue_groups") or []) if isinstance(_g, dict)
                        for _t in (_g.get("traps") or []) if isinstance(_t, dict)}
    _accounted = (_raised | _secondary_names)
    _accounted.discard("")
    cov = [c for c in cov if c.get("coverage_status") == "partially_assessed"
           or _normalize_trap_name(c.get("trap_name", "")) not in _accounted]
    # De-dup by normalized trap name (a model can emit the same trap twice in traps_checked_not_found):
    # the disposition index already dedups, so without this the coverage buckets would show twin pills.
    _seen_cov: set = set()
    _deduped_cov = []
    for c in cov:
        _cnm = _normalize_trap_name(c.get("trap_name", ""))
        if _cnm and _cnm in _seen_cov:
            continue
        _seen_cov.add(_cnm)
        _deduped_cov.append(c)
    cov = _deduped_cov
    _did_not_find = [c for c in cov if c.get("coverage_status") == "not_present"]
    _partial = [c for c in cov if c.get("coverage_status") == "partially_assessed"]
    # "Couldn't evaluate" also absorbs any off-enum / missing coverage_status (e.g. from a
    # truncated tool response). Without this catch-all such an entry matches no bucket and vanishes
    # silently; folding it here keeps the trap visible rather than dropped from coverage.
    _couldnt = [c for c in cov if c.get("coverage_status") not in ("not_present", "partially_assessed")]
    if cov:
        h.append("<div class='section'><div class='section-eyebrow'>Coverage notes</div>")
        if _partial:
            h.append("<div class='cov-group'><div class='cov-grouplabel'>Partially evaluated</div>")
            h.append("<p class='cov-intro'>Checked for the parts a static screen can show; the rest depends on timing, motion, or what happens after you act — worth confirming in the live product.</p>")
            h.append("<div class='coverage'>")
            for c in _partial:
                name = c.get('trap_name', '')
                color = _TENET_PILL.get(_tenet_for(name, version=_ver).upper(), "#35597F")
                d = (c.get("detail") or "").replace("assessed within scope:", "Checked:").replace("not assessable from this artifact:", "couldn’t check:").replace("not assessable:", "couldn’t check:")
                h.append("<div class='cov-item assess'>")
                h.append(f"<span class='tpill' style='background:{color}'>{name}</span>")
                if d:
                    h.append(f"<span class='cs'>{d}</span>")
                h.append("</div>")
            h.append("</div></div>")
        if _did_not_find:
            h.append("<div class='cov-group'><div class='cov-grouplabel'>Not found</div>")
            h.append("<p class='cov-intro'>Traps checked and not seen in what was submitted — no instances here.</p>")
            h.append("<div class='coverage'>")
            for c in _did_not_find:
                name = c.get('trap_name', '')
                color = _TENET_PILL.get(_tenet_for(name, version=_ver).upper(), "#35597F")
                h.append(f"<div class='cov-item'><span class='tpill' style='background:{color}'>{name}</span></div>")
            h.append("</div></div>")
        if _couldnt:
            h.append("<div class='cov-group'><div class='cov-grouplabel'>Couldn't evaluate</div>")
            h.append("<p class='cov-intro'>Couldn't be judged from what was submitted — these would need the live product, more screens, or details about your users. Treat them as unanswered, not cleared.</p>")
            h.append("<div class='coverage'>")
            for c in _couldnt:
                name = c.get('trap_name', '')
                color = _TENET_PILL.get(_tenet_for(name, version=_ver).upper(), "#35597F")
                reason = (c.get("_assess_remedy")
                          or ("needs details about your users" if c.get("coverage_status") == "not_assessable_context"
                              else "needs the live product or more screens"))
                h.append("<div class='cov-item assess'>")
                h.append(f"<span class='tpill' style='background:{color}'>{name}</span>")
                h.append(f"<span class='cs'>{reason}</span>")
                h.append("</div>")
            h.append("</div></div>")
        h.append("</div>")
    else:
        # Parity with By-Issue: show the section with 'None reported' rather than omitting it —
        # the absence of coverage notes is itself informative.
        h.append("<div class='section'><div class='section-eyebrow'>Coverage notes</div>"
                 "<p class='narrative cov-none'>None reported.</p></div>")

    # positives
    pos = [p for p in report.get("positive_observations") or [] if p]
    if pos:
        h.append("<div class='section'><div class='section-eyebrow'>What works well</div>")
        h.append("<p class='narrative'>" + " ".join(str(p) for p in pos) + "</p></div>")

    # ── Trap Disposition Index — re-homed from By-Issue (KB accounting invariant). Every taxonomy
    # trap resolves to EXACTLY ONE disposition, derived from data already present on the by-trap
    # report:  a per-trap FINDING (primary) → "Reported above";  a trap bound as a secondary in an
    # issue_groups issue with no finding of its own (consequence / co-occurring) → "Within an
    # issue (<relationship>)";  a Worth-a-closer-look entry → linked;  a coverage bucket → its
    # label;  nowhere structured → "Not accounted for". Precedence finding > secondary >
    # worth-a-closer-look > coverage guarantees the exactly-once invariant.
    try:
        from .schema import _valid_trap_names as _vtn
    except ImportError:
        from schema import _valid_trap_names as _vtn
    _taxonomy = _vtn(settings.get("kb_version", "v2")) or []
    if _taxonomy:
        _found = {_normalize_trap_name(f.get("trap_name", "")) for f in _findings}
        _found.discard("")
        _secondary: dict = {}
        for _g in (report.get("issue_groups") or []):
            if not isinstance(_g, dict):
                continue
            for _t in (_g.get("traps") or []):
                if not isinstance(_t, dict):
                    continue
                _nm2 = _normalize_trap_name(_t.get("trap_name", ""))
                if not _nm2 or _nm2 in _found:
                    continue
                _rel = normalize_relationship(_t.get("relationship"))
                if _nm2 not in _secondary or (_secondary[_nm2] in ("none", "") and _rel not in ("none", "")):
                    _secondary[_nm2] = _rel
        _COV_LABEL = {"not_present": "Did not find",
                      "not_assessable_artifact": "Couldn't evaluate",
                      "not_assessable_context": "Couldn't evaluate",
                      "partially_assessed": "Partially evaluated"}
        _cov_of: dict = {}
        for c in cov:
            _nmc = _normalize_trap_name(c.get("trap_name", ""))
            if _nmc and _nmc not in _cov_of:
                _cov_of[_nmc] = _COV_LABEL.get(c.get("coverage_status"), "Coverage noted")
        _pot_of = {_normalize_trap_name(p.get("trap_name", "")) for p in _closer}
        _pot_of.discard("")
        _REL_DISP = {"co_occurring": "co-occurring", "consequence": "consequence",
                     "conditional_primary": "conditional", "conditional_enumerated": "conditional",
                     "root_cause": "root cause"}
        h.append("<div class='section'><div class='section-eyebrow'>Trap disposition index</div>")
        h.append("<p class='disp-intro'>Every framework trap, accounted for exactly once — reported as a trap above, bound within an issue, flagged as worth a closer look, or noted under coverage. Scan the column to confirm nothing was silently dropped.</p>")
        h.append("<div class='disp-wrap'><table class='disposition'><tbody>")
        for canonical in _taxonomy:
            _nm = _normalize_trap_name(canonical)
            color = _TENET_PILL.get(_tenet_for(canonical, version=_ver).upper(), "#35597F")
            h.append("<tr>")
            h.append(f"<td class='dt-trap'><span class='tpill' style='background:{color}'>{canonical}</span></td>")
            if _nm in _found:
                h.append("<td class='dt-disp'><span class='disp-cov'>Reported above</span></td>")
            elif _nm in _secondary:
                _rl = _REL_DISP.get(_secondary[_nm], "secondary")
                h.append(f"<td class='dt-disp'>Within an issue <span class='disp-rel'>({_rl})</span></td>")
            elif _nm in _pot_of:
                h.append("<td class='dt-disp'><a class='disp-link' href='#worth-a-closer-look'>Worth a closer look</a></td>")
            elif _nm in _cov_of:
                h.append(f"<td class='dt-disp'><span class='disp-cov'>{_cov_of[_nm]}</span></td>")
            else:
                h.append("<td class='dt-disp'><span class='disp-none'>Not accounted for</span></td>")
            h.append("</tr>")
        h.append("</tbody></table></div></div>")

    h.append("</div>")  # report-inner
    h.append("<div class='r-footer'>© UI Traps LLC · Proprietary &amp; Confidential — UI Tenets &amp; Traps Framework</div>")
    h.append("</div></div>")
    h.append(_TRAP_ANCHOR_JS)   # scroll trap-anchor links within the iframe (srcDoc fragment fix)
    h.append("</body></html>")
    return "\n".join(h)


def format_bytrap_report_as_html(
    report: dict[str, Any],
    user_context: dict[str, Any],
    analysis_settings: Optional[dict[str, Any]] = None,
) -> str:
    """Public entry for the rev6 BY-TRAP report — the sole rendered report structure. Escapes
    report, user_context AND settings at the boundary (the renderer's meta row interpolates
    settings values — unvalidated Form fields), then renders via _format_new_kb_bytrap_html."""
    report = _escape_html_deep(report)
    if user_context is not None:
        user_context = _escape_html_deep(user_context)
    if analysis_settings is not None:
        analysis_settings = _escape_html_deep(analysis_settings)
    return _format_new_kb_bytrap_html(report, user_context or {}, analysis_settings or {})


def get_report_statistics(report: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract statistics from report for tracking/analytics.

    Args:
        report: Parsed report dictionary

    Returns:
        Dictionary with report statistics
    """
    return {
        'total_issues': len(report.get('critical_issues', [])) + len(report.get('moderate_issues', [])) + len(report.get('minor_issues', [])),
        'critical_count': len(report.get('critical_issues', [])),
        'moderate_count': len(report.get('moderate_issues', [])),
        'minor_count': len(report.get('minor_issues', [])),
        'positive_count': len(report.get('positive_observations', [])),
        'traps_not_found_count': len(report.get('traps_checked_not_found', [])),
        'potential_count': len(report.get('potential_issues', [])),
    }


# ============================================================================
# Interaction Analysis Formatting
# ============================================================================

def format_interaction_analysis_markdown(
    analysis: Dict[str, Any],
    element_description: str = None,
    page_title: str = None
) -> str:
    """
    Format a single interaction analysis result as markdown.

    Args:
        analysis: Interaction analysis result from Claude
        element_description: Description of the element analyzed
        page_title: Page where interaction was captured

    Returns:
        Formatted markdown string
    """
    md = []

    interaction_type = analysis.get('interaction_type', 'unknown')
    element = element_description or analysis.get('element_analyzed', 'Unknown element')
    overall = analysis.get('overall_assessment', 'unknown')

    # Assessment emoji
    assessment_emoji = {
        'good': '✅',
        'acceptable': '🟡',
        'needs_improvement': '⚠️',
        'poor': '🔴'
    }.get(overall, '❓')

    # Header
    md.append(f"### {interaction_type.title()} Interaction {assessment_emoji}")
    md.append("")
    if page_title:
        md.append(f"**Page:** {page_title}")
    md.append(f"**Element:** {element}")
    md.append(f"**Overall Assessment:** {overall.replace('_', ' ').title()}")
    md.append("")

    # Summary
    if analysis.get('summary'):
        md.append(f"*{analysis['summary']}*")
        md.append("")

    # Feedback Quality
    feedback = analysis.get('feedback_quality', {})
    md.append("**Feedback Quality:**")
    md.append(f"- Visual feedback: {'Yes' if feedback.get('has_visual_feedback') else 'No'}")
    md.append(f"- Timing: {feedback.get('feedback_timing', 'unknown')}")
    md.append(f"- Clarity: {feedback.get('feedback_clarity', 'unknown')}")
    if feedback.get('feedback_description'):
        md.append(f"- Details: {feedback['feedback_description']}")
    md.append("")

    # State Transition
    transition = analysis.get('state_transition', {})
    md.append("**State Transition:**")
    md.append(f"- Predictable: {'Yes' if transition.get('is_predictable') else 'No'}")
    md.append(f"- Reversible: {'Yes' if transition.get('is_reversible') else 'No'}")
    md.append(f"- Maintains context: {'Yes' if transition.get('maintains_context') else 'No'}")
    if transition.get('transition_description'):
        md.append(f"- Details: {transition['transition_description']}")
    md.append("")

    # Traps Detected
    traps = analysis.get('traps_detected', [])
    if traps:
        md.append("**Issues Found:**")
        for trap in traps:
            severity_emoji = {'critical': '🔴', 'moderate': '🟡', 'minor': '🟢'}.get(trap.get('severity'), '⚪')
            md.append(f"- {severity_emoji} **{trap.get('trap_name', 'UNKNOWN')}**")
            md.append(f"  - Observation: {trap.get('observation', 'N/A')}")
            md.append(f"  - Recommendation: {trap.get('recommendation', 'N/A')}")
        md.append("")

    # Accessibility Concerns
    accessibility = analysis.get('accessibility_concerns', [])
    if accessibility:
        md.append("**Accessibility Concerns:**")
        for concern in accessibility:
            md.append(f"- {concern.get('concern', 'N/A')}")
            md.append(f"  - Affected: {concern.get('affected_users', 'N/A')}")
            md.append(f"  - Fix: {concern.get('recommendation', 'N/A')}")
        md.append("")

    # Positive Observations
    positives = analysis.get('positive_observations', [])
    if positives:
        md.append("**What Works Well:**")
        for pos in positives:
            md.append(f"- {pos}")
        md.append("")

    return "\n".join(md)


def format_interaction_summary_markdown(
    interaction_analysis: Dict[str, Any],
    include_individual: bool = False
) -> str:
    """
    Format complete interaction analysis section as markdown.

    Args:
        interaction_analysis: Full interaction analysis dict from SiteAnalyzer
        include_individual: Whether to include individual interaction details

    Returns:
        Formatted markdown string
    """
    md = []

    if not interaction_analysis.get('enabled'):
        return ""

    md.append("# Interaction Analysis")
    md.append("")
    md.append("*Analysis of moment-by-moment UI interactions including hover states, click feedback, form validation, scroll behavior, and responsive layout.*")
    md.append("")

    summary = interaction_analysis.get('summary', {})
    stats = interaction_analysis.get('statistics', {})

    # Overall Quality
    quality = summary.get('overall_quality', 'unknown')
    quality_emoji = {
        'good': '✅',
        'acceptable': '🟡',
        'needs_improvement': '⚠️',
        'poor': '🔴',
        'unknown': '❓'
    }.get(quality, '❓')

    md.append(f"## Overall Interaction Quality: {quality.replace('_', ' ').title()} {quality_emoji}")
    md.append("")

    # Statistics
    md.append("### Statistics")
    md.append("")
    md.append(f"- **Interactions Analyzed:** {stats.get('total_analyzed', 0)}")
    md.append(f"- **Successful:** {stats.get('successful', 0)}")
    md.append(f"- **Failed:** {stats.get('failed', 0)}")
    md.append("")

    # Issues by severity
    issues = stats.get('issues_by_severity', {})
    if any(issues.values()):
        md.append("**Issues Found:**")
        if issues.get('critical', 0) > 0:
            md.append(f"- 🔴 Critical: {issues['critical']}")
        if issues.get('moderate', 0) > 0:
            md.append(f"- 🟡 Moderate: {issues['moderate']}")
        if issues.get('minor', 0) > 0:
            md.append(f"- 🟢 Minor: {issues['minor']}")
        md.append("")

    # By Type
    by_type = stats.get('by_type', {})
    if by_type:
        md.append("### By Interaction Type")
        md.append("")
        md.append("| Type | Analyzed | Issues |")
        md.append("|------|----------|--------|")
        for itype, data in by_type.items():
            md.append(f"| {itype.title()} | {data.get('count', 0)} | {data.get('issues', 0)} |")
        md.append("")

    # Critical Findings
    critical = summary.get('critical_issues', [])
    if critical:
        md.append("### Critical Interaction Issues")
        md.append("")
        for issue in critical:
            md.append(f"**{issue.get('trap_name', 'UNKNOWN')}** on {issue.get('page', 'Unknown page')}")
            md.append(f"- {issue.get('observation', 'N/A')}")
            md.append(f"- Recommendation: {issue.get('recommendation', 'N/A')}")
            md.append("")

    # Common Issues
    common = summary.get('common_interaction_issues', [])
    if common:
        md.append("### Common Issues Across Interactions")
        md.append("")
        for issue in common:
            md.append(f"- **{issue.get('trap_name', 'UNKNOWN')}** (found {issue.get('count', 0)} times)")
            for ex in issue.get('examples', []):
                md.append(f"  - {ex.get('page', 'Unknown')}: {ex.get('observation', '')[:80]}...")
        md.append("")

    # Individual Analyses
    if include_individual:
        individual = interaction_analysis.get('individual_analyses', [])
        if individual:
            md.append("### Individual Interaction Details")
            md.append("")
            for ia in individual:
                if ia.get('success'):
                    md.append(format_interaction_analysis_markdown(
                        ia.get('analysis', {}),
                        ia.get('element'),
                        ia.get('page_title')
                    ))
                    md.append("---")
                    md.append("")

    return "\n".join(md)


def format_interaction_summary_html(
    interaction_analysis: Dict[str, Any],
    include_individual: bool = False
) -> str:
    """
    Format interaction analysis section as HTML.

    Args:
        interaction_analysis: Full interaction analysis dict from SiteAnalyzer
        include_individual: Whether to include individual interaction details

    Returns:
        Formatted HTML string
    """
    if not interaction_analysis.get('enabled'):
        return ""

    html = []
    summary = interaction_analysis.get('summary', {})
    stats = interaction_analysis.get('statistics', {})

    # Container
    html.append("<div class='interaction-analysis-section' style='margin-top: 40px;'>")
    html.append("<h1>Interaction Analysis</h1>")
    html.append("<p style='color: #8a8680; font-size: 0.91em;'>Analysis of moment-by-moment UI interactions including hover states, click feedback, form validation, scroll behavior, and responsive layout.</p>")

    # Overall Quality Card
    quality = summary.get('overall_quality', 'unknown')
    quality_colors = {
        'good': '#27ae60',
        'acceptable': '#f39c12',
        'needs_improvement': '#e67e22',
        'poor': '#e74c3c',
        'unknown': '#95a5a6'
    }
    quality_color = quality_colors.get(quality, '#95a5a6')

    html.append(f"""
        <div style='background: linear-gradient(135deg, {quality_color}22, {quality_color}11);
                    border-left: 4px solid {quality_color};
                    padding: 20px;
                    border-radius: 8px;
                    margin: 20px 0;'>
            <h2 style='margin: 0; color: {quality_color};'>
                Overall Interaction Quality: {quality.replace('_', ' ').title()}
            </h2>
        </div>
    """)

    # Statistics Grid
    html.append("""
        <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin: 20px 0;'>
    """)

    # Stat cards
    stat_items = [
        ('Total Analyzed', stats.get('total_analyzed', 0), '#3498db'),
        ('Successful', stats.get('successful', 0), '#27ae60'),
        ('Failed', stats.get('failed', 0), '#e74c3c'),
    ]

    issues = stats.get('issues_by_severity', {})
    if issues.get('critical', 0) > 0:
        stat_items.append(('Critical Issues', issues['critical'], '#e74c3c'))
    if issues.get('moderate', 0) > 0:
        stat_items.append(('Moderate Issues', issues['moderate'], '#f39c12'))
    if issues.get('minor', 0) > 0:
        stat_items.append(('Minor Issues', issues['minor'], '#3498db'))

    for label, value, color in stat_items:
        html.append(f"""
            <div style='background: white; border: 1px solid #e0e0e0; border-radius: 8px;
                        padding: 15px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05);'>
                <div style='font-size: 24px; font-weight: bold; color: {color};'>{value}</div>
                <div style='font-size: 12px; color: #7f8c8d; margin-top: 5px;'>{label}</div>
            </div>
        """)

    html.append("</div>")

    # By Type Table
    by_type = stats.get('by_type', {})
    if by_type:
        html.append("<h3>By Interaction Type</h3>")
        html.append("""
            <table style='width: 100%; border-collapse: collapse; margin: 15px 0;'>
                <thead>
                    <tr style='background: #f8f9fa;'>
                        <th style='padding: 12px; text-align: left; border-bottom: 2px solid #e0e0e0;'>Type</th>
                        <th style='padding: 12px; text-align: center; border-bottom: 2px solid #e0e0e0;'>Analyzed</th>
                        <th style='padding: 12px; text-align: center; border-bottom: 2px solid #e0e0e0;'>Issues</th>
                    </tr>
                </thead>
                <tbody>
        """)

        type_icons = {
            'hover': '👆',
            'click': '👇',
            'form': '📝',
            'scroll': '📜',
            'responsive': '📱'
        }

        for itype, data in by_type.items():
            icon = type_icons.get(itype, '🔹')
            html.append(f"""
                <tr style='border-bottom: 1px solid #e0e0e0;'>
                    <td style='padding: 12px;'>{icon} {itype.title()}</td>
                    <td style='padding: 12px; text-align: center;'>{data.get('count', 0)}</td>
                    <td style='padding: 12px; text-align: center;'>{data.get('issues', 0)}</td>
                </tr>
            """)

        html.append("</tbody></table>")

    # Critical Findings
    critical = summary.get('critical_issues', [])
    if critical:
        html.append("<h3>🔴 Critical Interaction Issues</h3>")
        for issue in critical:
            html.append(f"""
                <div class='issue-card critical' style='background: #fef5f5; border-left: 4px solid #e74c3c;
                            padding: 15px; margin: 10px 0; border-radius: 4px;'>
                    <strong>{issue.get('trap_name', 'UNKNOWN').upper()}</strong> on {issue.get('page', 'Unknown page')}
                    <p style='margin: 10px 0 5px 0;'>{_cap_terms(issue.get('observation', 'N/A'))}</p>
                    <p style='margin: 0; color: #27ae60;'><strong>Recommendation:</strong> {_cap_terms(issue.get('recommendation', 'N/A'))}</p>
                </div>
            """)

    html.append("</div>")

    return "\n".join(html)
