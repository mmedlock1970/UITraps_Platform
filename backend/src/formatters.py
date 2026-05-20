"""
Response formatting and parsing for UI Traps Analyzer

Copyright © 2009-present UI Traps LLC. All Rights Reserved.
PROPRIETARY & CONFIDENTIAL - UI Tenets & Traps Framework
"""
import json
import re
from typing import Dict, Any, Optional
from datetime import datetime

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
    ("BEAUTIFUL", ["POOR AESTHETIC"]),
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
    name = name.upper()
    name = re.sub(r'\(S\)', 'S', name)           # STEP(S) -> STEPS
    name = re.sub(r'\s*\([^)]*\)\s*', ' ', name) # strip other parentheticals
    return re.sub(r'\s+', ' ', name).strip()


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
    required_fields = ['summary', 'critical_issues', 'moderate_issues', 'minor_issues',
                      'positive_observations', 'traps_checked_not_found']

    for field in required_fields:
        if field not in report:
            raise ValueError(f"Missing required field in response: {field}")

    return report


def format_report_as_markdown(report: Dict[str, Any], user_context: Dict[str, str] = None) -> str:
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
        md.append(f"**Users:** {user_context.get('users', 'N/A')}")
        md.append("")

        # Format tasks as bulleted list
        raw_tasks = user_context.get('tasks', 'N/A')
        task_list = parse_tasks(raw_tasks)
        md.append("**Key Tasks:**")
        for task in task_list:
            md.append(f"- {task}")
        md.append("")

        md.append(f"**Materials Tested:** {user_context.get('format', 'N/A')}")
        md.append("")
        md.append("---")
        md.append("")

    # Summary
    md.append("## Summary")
    md.append("")
    n_issues = len(report.get('user_issues', []))
    n_high = len(report.get('critical_issues', []))
    n_moderate = len(report.get('moderate_issues', []))
    n_low = len(report.get('minor_issues', []))
    n_traps = n_high + n_moderate + n_low
    trap_breakdown = ", ".join(filter(None, [
        f"{n_high} high severity" if n_high else "",
        f"{n_moderate} moderate" if n_moderate else "",
        f"{n_low} low severity" if n_low else "",
    ]))
    trap_summary = f"{n_traps} trap{'s' if n_traps != 1 else ''}"
    if trap_breakdown:
        trap_summary += f" ({trap_breakdown})"
    md.append(f"**Found:** {n_issues} general issue{'s' if n_issues != 1 else ''} • {trap_summary}")
    md.append("")

    # Programmatic count bullet
    import re as _re
    _count_pattern = _re.compile(r'^\d+\s+(trap|issue)s?\s+identified', _re.IGNORECASE)
    count_bullet = f"{n_traps} trap{'s' if n_traps != 1 else ''} identified"
    if trap_breakdown:
        count_bullet += f": {trap_breakdown}."
    else:
        count_bullet += "."
    if n_issues:
        count_bullet += f" {n_issues} general issue{'s' if n_issues != 1 else ''} identified."
    md.append(f"- {count_bullet}")
    for bullet in report['summary']:
        if _count_pattern.match(bullet.strip()):
            continue  # skip AI-generated count bullet
        md.append(f"- {bullet}")
    md.append("")

    # Helper to render frame info for an issue
    def render_frame_info(issue):
        if 'appears_in' in issue and len(issue.get('appears_in', [])) > 1:
            frame_indices = issue.get('frame_indices', [])
            if frame_indices:
                frames_display = ', '.join([f"Frame {idx}" for idx in frame_indices[:5]])
                if len(frame_indices) > 5:
                    frames_display += f" (+{len(frame_indices) - 5} more)"
            else:
                frames_display = ', '.join(issue['appears_in'][:5])
                if len(issue['appears_in']) > 5:
                    frames_display += f" (+{len(issue['appears_in']) - 5} more)"
            md.append(f"**📍 See:** {frames_display}")
            md.append("")
        elif 'frame_index' in issue:
            frame_idx = issue['frame_index']
            frame_label = issue.get('frame', f"Frame {frame_idx}")
            md.append(f"**📍 See Frame {frame_idx}** ({frame_label})")
            md.append("")
        elif 'frame' in issue:
            md.append(f"**📍 Found in:** {issue['frame']}")
            md.append("")

    # Critical Issues
    if report['critical_issues']:
        md.append("## 🔴 Critical Issues")
        md.append("")
        for issue in report['critical_issues']:
            render_frame_info(issue)
            md.append(f"**Trap Detected:** **{issue.get('trap_name', 'UNKNOWN').upper()}**")
            md.append("")
            md.append(f"**Tenet Violated:** {issue.get('tenet', '').upper()}")
            md.append("")
            md.append(f"**Where:** {_cap_terms(issue.get('location', ''))}")
            md.append("")
            md.append(f"**Problem:** {_cap_terms(issue.get('problem', ''))}")
            md.append("")
            if issue.get('recommendation'):
                md.append(f"**Recommendation:** {_cap_terms(issue['recommendation'])}")
            md.append("")
            if 'confidence' in issue:
                md.append(f"*Confidence: {issue['confidence']}*")
                md.append("")
    else:
        md.append("## 🔴 Critical Issues")
        md.append("")
        md.append("*None found* ✓")
        md.append("")

    # Moderate Issues
    if report['moderate_issues']:
        md.append("## 🟡 Moderate Issues")
        md.append("")
        for issue in report['moderate_issues']:
            render_frame_info(issue)
            md.append(f"**Trap Detected:** **{issue.get('trap_name', 'UNKNOWN').upper()}**")
            md.append("")
            md.append(f"**Tenet Violated:** {issue.get('tenet', '').upper()}")
            md.append("")
            md.append(f"**Where:** {_cap_terms(issue.get('location', ''))}")
            md.append("")
            md.append(f"**Problem:** {_cap_terms(issue.get('problem', ''))}")
            md.append("")
            if issue.get('recommendation'):
                md.append(f"**Recommendation:** {_cap_terms(issue['recommendation'])}")
            md.append("")
            if 'confidence' in issue:
                md.append(f"*Confidence: {issue['confidence']}*")
                md.append("")
    else:
        md.append("## 🟡 Moderate Issues")
        md.append("")
        md.append("*None found* ✓")
        md.append("")

    # Minor Issues
    if report['minor_issues']:
        md.append("## 🔵 Minor Issues")
        md.append("")
        for issue in report['minor_issues']:
            render_frame_info(issue)
            md.append(f"**Trap Detected:** **{issue.get('trap_name', 'UNKNOWN').upper()}**")
            md.append("")
            md.append(f"**Tenet Violated:** {issue.get('tenet', '').upper()}")
            md.append("")
            md.append(f"**Where:** {_cap_terms(issue.get('location', ''))}")
            md.append("")
            md.append(f"**Problem:** {_cap_terms(issue.get('problem', ''))}")
            md.append("")
            if issue.get('recommendation'):
                md.append(f"**Recommendation:** {_cap_terms(issue['recommendation'])}")
            md.append("")
            if 'confidence' in issue:
                md.append(f"*Confidence: {issue['confidence']}*")
                md.append("")
    else:
        md.append("## 🔵 Minor Issues")
        md.append("")
        md.append("*None found* ✓")
        md.append("")

    # Positive Observations
    md.append("## ✅ Positive Observations")
    md.append("")
    if report['positive_observations']:
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
            render_frame_info(bug)
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
            render_frame_info(issue)
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

    # General Issues (synthesis layer)
    user_issues = report.get('user_issues', [])
    if user_issues:
        impact_order = {"high": 0, "medium": 1, "low": 2}
        md.append("## General Issues")
        md.append("")
        md.append("*General issues are broad problems experienced by users. Each may stem from one or more specific traps listed below.*")
        md.append("")

        def _render_md_issue(issue):
            impact = issue.get('impact_level', 'low').upper()
            md.append(f"### {issue.get('issue_title', 'Untitled Issue')} [{impact} IMPACT]")
            md.append("")
            md.append(issue.get('issue_description', ''))
            md.append("")
            traps = issue.get('contributing_traps', [])
            if traps:
                trap_names = ", ".join(t.get('trap_name', '') for t in traps if t.get('trap_name'))
                md.append(f"**Underlying traps:** {trap_names}")
                md.append("")
            recs = issue.get('recommendations', [])
            if recs:
                md.append("**How to fix:**")
                for rec in recs:
                    md.append(f"- {rec}")
                md.append("")

        raw_tasks = user_context.get('tasks', 'N/A') if user_context else 'N/A'
        task_list = parse_tasks(raw_tasks)
        multi_task = len(task_list) > 1 and task_list != ['N/A']

        if multi_task:
            # Group issues by task_context; bucket unmatched as general
            def _best_task_match(tc, tasks):
                if not tc:
                    return None
                tc_lower = tc.lower()
                for t in tasks:
                    if tc_lower == t.lower() or tc_lower in t.lower() or t.lower() in tc_lower:
                        return t
                return tc  # keep original label if no match found

            task_buckets = {t: [] for t in task_list}
            general_bucket = []
            other_buckets = {}
            for issue in user_issues:
                tc = issue.get('task_context', '').strip()
                matched = _best_task_match(tc, task_list)
                if matched is None:
                    general_bucket.append(issue)
                elif matched in task_buckets:
                    task_buckets[matched].append(issue)
                else:
                    other_buckets.setdefault(matched, []).append(issue)

            for task in task_list:
                bucket = task_buckets[task]
                if bucket:
                    bucket = sorted(bucket, key=lambda x: impact_order.get(x.get('impact_level', 'low'), 3))
                    md.append(f"**Task: {task}**")
                    md.append("")
                    for issue in bucket:
                        _render_md_issue(issue)

            for label, bucket in other_buckets.items():
                bucket = sorted(bucket, key=lambda x: impact_order.get(x.get('impact_level', 'low'), 3))
                md.append(f"**Task: {label}**")
                md.append("")
                for issue in bucket:
                    _render_md_issue(issue)

            if general_bucket:
                general_bucket = sorted(general_bucket, key=lambda x: impact_order.get(x.get('impact_level', 'low'), 3))
                md.append("**General (applies to all tasks)**")
                md.append("")
                for issue in general_bucket:
                    _render_md_issue(issue)
        else:
            user_issues = sorted(user_issues, key=lambda x: impact_order.get(x.get('impact_level', 'low'), 3))
            for issue in user_issues:
                _render_md_issue(issue)

    # Traps Checked but Not Found — split into tested-clean vs could-not-test
    md.append("## Traps Checked But Not Found")
    md.append("")
    raw_items = report.get('traps_checked_not_found', [])
    md_tested_ok = []
    md_untestable = []
    for item in raw_items:
        if isinstance(item, str):
            md_tested_ok.append(item)
        elif item.get('testable', True):
            md_tested_ok.append(item['trap_name'].upper())
        else:
            md_untestable.append(item)

    if md_tested_ok:
        md.append("### ✓ Evaluated — Not Present")
        md.append("")
        for trap in md_tested_ok:
            md.append(f"- {trap}")
        md.append("")

    if md_untestable:
        md.append("### ⚠ Could Not Evaluate — Insufficient Information")
        md.append("")
        for item in md_untestable:
            reason = _untestable_reason(item.get('trap_name', ''), item.get('reason'))
            md.append(f"- **{item['trap_name'].upper()}** — {reason}")
        md.append("")

    if not md_tested_ok and not md_untestable:
        md.append("*All traps were either found or not fully evaluated*")
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


def _build_user_issues_html(report: Dict[str, Any], user_context: Dict[str, str] = None) -> str:
    """Build the General Issues section HTML."""
    issues = report.get('user_issues', [])
    if not issues:
        return ""

    impact_order = {"high": 0, "medium": 1, "low": 2}

    def _render_issue_card(issue, html):
        impact = issue.get('impact_level', 'low')
        html.append(f"<div class='user-issue-card impact-{impact}'>")
        html.append("<div class='user-issue-header'>")
        html.append(f"<span class='impact-badge {impact}'>{impact.upper()} IMPACT</span>")
        html.append(f"<h3 class='user-issue-title'>{issue.get('issue_title', '')}</h3>")
        html.append("</div>")
        html.append(f"<p>{issue.get('issue_description', '')}</p>")
        traps = issue.get('contributing_traps', [])
        if traps:
            html.append("<div class='contributing-traps'>")
            html.append("<span class='traps-label'>Underlying traps:</span>")
            for t in traps:
                sev = t.get('severity', 'minor')
                name = t.get('trap_name', '')
                contrib = t.get('contribution', '')
                html.append(f"<span class='trap-pill {sev}' title='{contrib}'>{name}</span>")
            html.append("</div>")
        recs = issue.get('recommendations', [])
        if recs:
            html.append("<div class='user-issue-recs'>")
            html.append("<strong>How to fix:</strong>")
            html.append("<ul>")
            for rec in recs:
                html.append(f"<li>{rec}</li>")
            html.append("</ul>")
            html.append("</div>")
        html.append("</div>")

    raw_tasks = user_context.get('tasks', 'N/A') if user_context else 'N/A'
    task_list = parse_tasks(raw_tasks)
    multi_task = len(task_list) > 1 and task_list != ['N/A']

    html = ["<div class='user-issues-section'>"]
    html.append("<h2>General Issues</h2>")
    html.append("<p class='user-issues-intro'>General issues are broad problems experienced by users. Each issue may stem from one or more specific traps. The traps listed under each issue identify the root causes.</p>")

    if multi_task:
        def _best_task_match(tc, tasks):
            if not tc:
                return None
            tc_lower = tc.lower()
            for t in tasks:
                if tc_lower == t.lower() or tc_lower in t.lower() or t.lower() in tc_lower:
                    return t
            return tc

        task_buckets = {t: [] for t in task_list}
        general_bucket = []
        other_buckets = {}
        for issue in issues:
            tc = issue.get('task_context', '').strip()
            matched = _best_task_match(tc, task_list)
            if matched is None:
                general_bucket.append(issue)
            elif matched in task_buckets:
                task_buckets[matched].append(issue)
            else:
                other_buckets.setdefault(matched, []).append(issue)

        for task in task_list:
            bucket = task_buckets[task]
            if bucket:
                bucket = sorted(bucket, key=lambda x: impact_order.get(x.get('impact_level', 'low'), 3))
                html.append(f"<h3 class='task-group-header'>Task: {task}</h3>")
                for issue in bucket:
                    _render_issue_card(issue, html)

        for label, bucket in other_buckets.items():
            bucket = sorted(bucket, key=lambda x: impact_order.get(x.get('impact_level', 'low'), 3))
            html.append(f"<h3 class='task-group-header'>Task: {label}</h3>")
            for issue in bucket:
                _render_issue_card(issue, html)

        if general_bucket:
            general_bucket = sorted(general_bucket, key=lambda x: impact_order.get(x.get('impact_level', 'low'), 3))
            html.append("<h3 class='task-group-header'>General (applies to all tasks)</h3>")
            for issue in general_bucket:
                _render_issue_card(issue, html)
    else:
        issues = sorted(issues, key=lambda x: impact_order.get(x.get('impact_level', 'low'), 3))
        for issue in issues:
            _render_issue_card(issue, html)

    html.append("</div>")
    return "\n".join(html)


def format_report_as_html(report: Dict[str, Any], user_context: Dict[str, str] = None) -> str:
    """
    Format the report as HTML for web display.

    Args:
        report: Parsed report dictionary
        user_context: Optional context info

    Returns:
        Formatted HTML string with embedded CSS
    """
    html = []

    # Add HTML document structure and CSS
    html.append("<!DOCTYPE html>")
    html.append("<html lang='en'>")
    html.append("<head>")
    html.append("<meta charset='UTF-8'>")
    html.append("<meta name='viewport' content='width=device-width, initial-scale=1.0'>")
    html.append("<title>UI Tenets & Traps Analysis Report</title>")
    html.append("<style>")
    html.append("""
        /* ── Base ── */
        html, body {
            margin: 0; padding: 0;
            font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            font-size: 15px;
            line-height: 1.65;
            color: #111111;
            background: #f7f6f4;
        }
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            color: #111111;
            letter-spacing: -0.3px;
        }
        .ui-traps-report {
            padding: 32px 28px;
            max-width: 860px;
            margin: 0 auto;
        }
        .timestamp {
            color: #8a8680;
            font-size: 0.85em;
        }
        .context-section {
            padding: 20px 24px;
            border-radius: 12px;
            margin: 20px 0;
            border: 1px solid #e8e6e2;
            background: #ffffff;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
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
        .findings-overview {
            font-size: 0.93em;
            color: #4a4744;
            margin: 0 0 16px 0;
            padding: 12px 16px;
            background: #f7f6f4;
            border-radius: 8px;
            border: 1px solid #e8e6e2;
        }
        /* CSS-only severity dots — explicit color, no emoji rendering */
        .sev-dot {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 8px;
            vertical-align: middle;
            flex-shrink: 0;
        }
        .sev-critical { background: #c0392b; }
        .sev-moderate { background: #e05c1a; }
        .sev-minor    { background: #3498db; }
        .issue-card {
            background: #ffffff;
            border: 1px solid #e8e6e2;
            border-left: 4px solid #d0cdc8;
            padding: 20px 22px;
            margin: 12px 0;
            border-radius: 10px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }
        .issue-card.critical {
            border-left-color: #c0392b;
        }
        .issue-card.moderate {
            border-left-color: #e05c1a;
        }
        .issue-card.minor {
            border-left-color: #3498db;
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
            border: 1px solid #e8e6e2;
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
            border: 1px solid #e8e6e2;
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
        .positive-section {
            padding: 20px 24px;
            border-radius: 12px;
            border: 1px solid #e8e6e2;
            border-left: 4px solid #27ae60;
            background: #ffffff;
            margin: 20px 0;
        }
        .positive-item { color: #1a7a40; }
        h1 { font-size: 1.6em; font-weight: 800; color: #111111; border-bottom: 2px solid #e8e6e2; padding-bottom: 12px; margin-bottom: 20px; }
        h2 { font-size: 1.15em; font-weight: 700; color: #111111; border-bottom: 1px solid #e8e6e2; padding-bottom: 10px; margin: 28px 0 16px; }
        h3 { font-size: 1em; font-weight: 700; color: #111111; margin: 20px 0 10px; }
        h4 { font-size: 0.92em; font-weight: 600; color: #4a4744; margin: 16px 0 8px; }
        .potential-issues-section {
            padding: 20px 24px;
            border-radius: 12px;
            border-left: 4px solid #e05c1a;
            border: 1px solid #e8e6e2;
            background: #ffffff;
            margin: 20px 0;
        }
        .potential-issues-section .issue-card.potential {
            border-left-color: #e05c1a;
        }
        .traps-not-found {
            padding: 20px 24px;
            border-radius: 12px;
            border: 1px solid #e8e6e2;
            background: #ffffff;
        }
        .traps-not-found h3 {
            font-size: 0.92em;
            margin: 16px 0 8px;
            color: #111111;
            font-weight: 600;
        }
        .trap-list {
            column-count: 2;
            column-gap: 20px;
        }
        .trap-list li {
            break-inside: avoid;
        }
        .untestable-list {
            list-style: none;
            padding: 0;
            margin: 0;
        }
        .untestable-list li {
            padding: 7px 0;
            border-bottom: 1px solid #e8e6e2;
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
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e8e6e2;
        }
        .confidentiality-notice {
            border: 1px solid #e8e6e2;
            padding: 20px 24px;
            border-radius: 12px;
            margin-top: 20px;
            background: #ffffff;
        }
        .confidentiality-notice h3 {
            color: #8a6500;
            margin-top: 0;
        }
        .confidentiality-notice ul { margin: 10px 0; }
        .confidentiality-notice li { margin: 5px 0; }
        hr {
            border: none;
            border-top: 1px solid #e8e6e2;
            margin: 24px 0;
        }
        .trap-matrix { margin: 30px 0; }
        .trap-matrix-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.87em;
            border-radius: 10px;
            overflow: hidden;
            border: 1px solid #e8e6e2;
        }
        .trap-matrix-table thead th {
            background: #111111;
            color: #ffffff;
            padding: 10px 14px;
            text-align: left;
            font-weight: 600;
            font-size: 0.85em;
            letter-spacing: 0.02em;
        }
        .trap-matrix-table thead th.count-col { text-align: center; }
        .trap-matrix-table td {
            padding: 7px 14px;
            border-bottom: 1px solid #e8e6e2;
            vertical-align: middle;
        }
        .trap-matrix-table .tenet-cell {
            font-weight: 700;
            font-size: 0.75em;
            letter-spacing: 0.06em;
            background: #f7f6f4;
            color: #4a4744;
            text-align: center;
            border-right: 1px solid #e8e6e2;
            white-space: nowrap;
            text-transform: uppercase;
        }
        .trap-matrix-table .trap-name {
            color: #4a4744;
            font-size: 0.85em;
        }
        .trap-matrix-table .count { text-align: center; font-weight: 600; min-width: 60px; }
        .trap-matrix-table .count.critical { color: #c0392b; }
        .trap-matrix-table .count.moderate { color: #e05c1a; }
        .trap-matrix-table .count.minor { color: #2980b9; }
        .trap-matrix-table .count.total {
            color: #111111;
            border-left: 1px solid #e8e6e2;
        }
        .trap-matrix-table tr.has-issues td.trap-name { font-weight: 600; color: #111111; }

        /* General Issues */
        .user-issues-section {
            margin: 30px 0;
            padding: 24px 28px;
            border-radius: 12px;
            border: 1px solid #e8e6e2;
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
            border: 1px solid #e8e6e2;
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
        .task-group-header { font-size: 0.95em; color: #4a4744; font-weight: 700; margin: 22px 0 8px; padding-bottom: 6px; border-bottom: 1px solid #e8e6e2; letter-spacing: -0.1px; }
    """)
    html.append("</style>")
    html.append("</head>")
    html.append("<body>")
    html.append("<div class='ui-traps-report'>")

    # Header
    html.append(f"<h1>UI Tenets & Traps Analysis Report</h1>")

    # Design name/title
    if user_context and user_context.get('design_name'):
        html.append(f"<h2>{user_context['design_name']}</h2>")

    html.append(f"<p class='timestamp'>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>")

    # Context
    if user_context:
        html.append("<div class='context-section'>")
        html.append("<h2>Context</h2>")
        if user_context.get('chat_context_used'):
            html.append("<p class='chat-context-badge'>&#x21BA; Re-analyzed with chat clarifications</p>")
        html.append(f"<p><strong>Users:</strong> {user_context.get('users', 'N/A')}</p>")

        # Format tasks as bulleted list
        raw_tasks = user_context.get('tasks', 'N/A')
        task_list = parse_tasks(raw_tasks)
        html.append("<p><strong>Key Tasks:</strong></p>")
        html.append("<ul>")
        for task in task_list:
            html.append(f"<li>{task}</li>")
        html.append("</ul>")

        html.append(f"<p><strong>Materials Tested:</strong> {user_context.get('format', 'N/A')}</p>")
        html.append("</div>")

    # Summary
    html.append("<div class='summary-section'>")
    html.append("<h2>Summary</h2>")

    # Findings overview — distinguishes general issues from traps
    n_issues = len(report.get('user_issues', []))
    n_high = len(report.get('critical_issues', []))
    n_moderate = len(report.get('moderate_issues', []))
    n_low = len(report.get('minor_issues', []))
    n_traps = n_high + n_moderate + n_low
    trap_breakdown = ", ".join(filter(None, [
        f"{n_high} high severity" if n_high else "",
        f"{n_moderate} moderate" if n_moderate else "",
        f"{n_low} low severity" if n_low else "",
    ]))
    trap_summary = f"{n_traps} trap{'s' if n_traps != 1 else ''}"
    if trap_breakdown:
        trap_summary += f" ({trap_breakdown})"
    issue_summary = f"{n_issues} general issue{'s' if n_issues != 1 else ''}"

    html.append(f"<p class='findings-overview'><strong>Found:</strong> {issue_summary} &bull; {trap_summary}</p>")

    # Programmatic count bullet — never trust the AI to get the terminology right
    count_bullet = f"{n_traps} trap{'s' if n_traps != 1 else ''} identified"
    if trap_breakdown:
        count_bullet += f": {trap_breakdown}."
    else:
        count_bullet += "."
    if n_issues:
        count_bullet += f" {n_issues} general issue{'s' if n_issues != 1 else ''} identified."

    import re as _re
    _count_pattern = _re.compile(r'^\d+\s+(trap|issue)s?\s+identified', _re.IGNORECASE)

    html.append("<ul>")
    html.append(f"<li>{count_bullet}</li>")
    for bullet in report['summary']:
        if _count_pattern.match(bullet.strip()):
            continue  # skip AI-generated count bullet
        html.append(f"<li>{bullet}</li>")
    html.append("</ul>")
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

    # Helper function for issue sections
    def render_issues(issues, severity_emoji, severity_class):
        if issues:
            for issue in issues:
                html.append(f"<div class='issue-card {severity_class}'>")

                # Always show frame reference for video/multi-image analysis
                has_frame_info = 'frame_index' in issue or 'frame_indices' in issue or 'frame' in issue

                if has_frame_info:
                    html.append("<div class='issue-frames' style='margin-bottom: 12px;'>")
                    html.append("<p style='margin: 0 0 8px 0; font-weight: 600; color: #2c3e50;'>📍 Found in:</p>")

                    # Show thumbnails if we have frame_images data
                    if frame_images and ('frame_index' in issue or 'frame_indices' in issue):
                        html.append("<div style='display: flex; flex-wrap: wrap; gap: 4px; margin-bottom: 8px;'>")

                        if 'frame_indices' in issue and len(issue.get('frame_indices', [])) > 1:
                            # Multiple frames - show thumbnails for each (up to 5)
                            for idx in issue['frame_indices'][:5]:
                                html.append(render_frame_thumbnail(idx, 'small'))
                            if len(issue['frame_indices']) > 5:
                                html.append(f"<span style='align-self: center; color: #7f8c8d; margin-left: 8px;'>+{len(issue['frame_indices']) - 5} more</span>")
                        elif 'frame_index' in issue:
                            # Single frame - show thumbnail
                            html.append(render_frame_thumbnail(issue['frame_index'], 'small'))

                        html.append("</div>")

                    # ALWAYS show text reference with timestamp (in case thumbnails fail)
                    if 'frame_indices' in issue and len(issue.get('frame_indices', [])) > 1:
                        # Multiple frames
                        frame_labels = []
                        for idx in issue['frame_indices'][:5]:
                            if idx in frame_images and frame_images[idx].get('timestamp') is not None:
                                ts = frame_images[idx]['timestamp']
                                frame_labels.append(f"Frame {idx} ({ts:.1f}s)")
                            else:
                                frame_labels.append(f"Frame {idx}")
                        label_text = ", ".join(frame_labels)
                        if len(issue['frame_indices']) > 5:
                            label_text += f" +{len(issue['frame_indices']) - 5} more"
                        html.append(f"<p style='margin: 0; color: #555; font-size: 0.9em;'>{label_text}</p>")
                    elif 'frame_index' in issue:
                        # Single frame
                        idx = issue['frame_index']
                        if idx in frame_images and frame_images[idx].get('timestamp') is not None:
                            ts = frame_images[idx]['timestamp']
                            html.append(f"<p style='margin: 0; color: #555; font-size: 0.9em;'>Frame {idx} ({ts:.1f}s)</p>")
                        else:
                            html.append(f"<p style='margin: 0; color: #555; font-size: 0.9em;'>Frame {idx}</p>")
                    elif 'frame' in issue:
                        # Just frame label, no index
                        html.append(f"<p style='margin: 0; color: #555; font-size: 0.9em;'>{issue['frame']}</p>")

                    html.append("</div>")

                html.append(f"<p><strong>Trap Detected:</strong> <strong>{issue['trap_name'].upper()}</strong></p>")
                html.append(f"<p class='tenet'><strong>Tenet Violated:</strong> {issue['tenet'].upper()}</p>")
                html.append(f"<p><strong>Where:</strong> {_cap_terms(issue['location'])}</p>")
                html.append(f"<p><strong>Problem:</strong> {_cap_terms(issue['problem'])}</p>")
                html.append(f"<p><strong>Recommendation:</strong> {_cap_terms(issue['recommendation'])}</p>")
                if 'confidence' in issue:
                    html.append(f"<p class='confidence'><em>Confidence: {issue['confidence']}</em></p>")
                html.append("</div>")
        else:
            html.append(f"<p class='none-found'>None found ✓</p>")

    # General Issues (synthesis layer)
    html.append(_build_user_issues_html(report, user_context))

    # Critical Issues
    html.append("<div class='issues-section critical'>")
    html.append("<h2><span class='sev-dot sev-critical'></span>High Severity Traps</h2>")
    render_issues(report['critical_issues'], "", "critical")
    html.append("</div>")

    # Moderate Issues
    html.append("<div class='issues-section moderate'>")
    html.append("<h2><span class='sev-dot sev-moderate'></span>Moderate Severity Traps</h2>")
    render_issues(report['moderate_issues'], "", "moderate")
    html.append("</div>")

    # Minor Issues
    html.append("<div class='issues-section minor'>")
    html.append("<h2><span class='sev-dot sev-minor'></span>Low Severity Traps</h2>")
    render_issues(report['minor_issues'], "", "minor")
    html.append("</div>")

    # Positive Observations
    html.append("<div class='positive-section'>")
    html.append("<h2>Positives</h2>")
    if report['positive_observations']:
        html.append("<ul>")
        for obs in report['positive_observations']:
            html.append(f"<li>{obs}</li>")
        html.append("</ul>")
    else:
        html.append("<p>None noted</p>")
    html.append("</div>")

    # Bugs Detected (Technical Issues)
    if report.get('bugs_detected') and len(report['bugs_detected']) > 0:
        html.append("<div class='bugs-section' style='padding: 20px; border-radius: 5px; border-left: 4px solid #e91e63; margin: 20px 0;'>")
        html.append("<h2>🐛 Technical Bugs Detected</h2>")
        html.append("<p><em>These are technical issues or broken states, not UI Traps. They represent system failures that should be fixed regardless of usability.</em></p>")
        for bug in report['bugs_detected']:
            html.append("<div class='issue-card' style='border-left-color: #e91e63;'>")

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
            html.append(f"<p><strong>Bug Type:</strong> <strong>{bug_type_display}</strong></p>")
            html.append(f"<p><strong>Where:</strong> {bug.get('location', 'N/A')}</p>")
            html.append(f"<p><strong>Description:</strong> {bug.get('description', 'N/A')}</p>")
            if bug.get('possible_cause'):
                html.append(f"<p><strong>Possible Cause:</strong> {bug['possible_cause']}</p>")
            html.append(f"<p class='confidence'><em>Confidence: {bug.get('confidence', 'medium')}</em></p>")
            html.append("</div>")
        html.append("</div>")

    # Potential Traps / Items for Review
    if report.get('potential_issues') and len(report['potential_issues']) > 0:
        html.append("<div class='potential-issues-section'>")
        html.append("<h2>⚠️ Potential Traps - Items for Review</h2>")
        html.append("<p><em>These items might be traps but require human judgment to confirm. The AI observed something potentially problematic but lacks context to definitively classify it.</em></p>")
        for issue in report['potential_issues']:
            html.append("<div class='issue-card potential'>")

            # Always show frame reference for video/multi-image analysis
            has_frame_info = 'frame_index' in issue or 'frame_indices' in issue or 'frame' in issue

            if has_frame_info:
                html.append("<div class='issue-frames' style='margin-bottom: 12px;'>")
                html.append("<p style='margin: 0 0 8px 0; font-weight: 600; color: #2c3e50;'>📍 Found in:</p>")

                # Show thumbnails if we have frame_images data
                if frame_images and ('frame_index' in issue or 'frame_indices' in issue):
                    html.append("<div style='display: flex; flex-wrap: wrap; gap: 4px; margin-bottom: 8px;'>")

                    if 'frame_indices' in issue and len(issue.get('frame_indices', [])) > 1:
                        for idx in issue['frame_indices'][:5]:
                            html.append(render_frame_thumbnail(idx, 'small'))
                        if len(issue['frame_indices']) > 5:
                            html.append(f"<span style='align-self: center; color: #7f8c8d; margin-left: 8px;'>+{len(issue['frame_indices']) - 5} more</span>")
                    elif 'frame_index' in issue:
                        html.append(render_frame_thumbnail(issue['frame_index'], 'small'))

                    html.append("</div>")

                # ALWAYS show text reference with timestamp
                if 'frame_indices' in issue and len(issue.get('frame_indices', [])) > 1:
                    frame_labels = []
                    for idx in issue['frame_indices'][:5]:
                        if idx in frame_images and frame_images[idx].get('timestamp') is not None:
                            ts = frame_images[idx]['timestamp']
                            frame_labels.append(f"Frame {idx} ({ts:.1f}s)")
                        else:
                            frame_labels.append(f"Frame {idx}")
                    label_text = ", ".join(frame_labels)
                    if len(issue['frame_indices']) > 5:
                        label_text += f" +{len(issue['frame_indices']) - 5} more"
                    html.append(f"<p style='margin: 0; color: #555; font-size: 0.9em;'>{label_text}</p>")
                elif 'frame_index' in issue:
                    idx = issue['frame_index']
                    if idx in frame_images and frame_images[idx].get('timestamp') is not None:
                        ts = frame_images[idx]['timestamp']
                        html.append(f"<p style='margin: 0; color: #555; font-size: 0.9em;'>Frame {idx} ({ts:.1f}s)</p>")
                    else:
                        html.append(f"<p style='margin: 0; color: #555; font-size: 0.9em;'>Frame {idx}</p>")
                elif 'frame' in issue:
                    html.append(f"<p style='margin: 0; color: #555; font-size: 0.9em;'>{issue['frame']}</p>")

                html.append("</div>")

            html.append(f"<p><strong>Trap Detected:</strong> <strong>{issue.get('trap_name', 'UNKNOWN').upper()}</strong> (Potential)</p>")
            html.append(f"<p class='tenet'><strong>Tenet:</strong> {issue.get('tenet', 'N/A').upper()}</p>")
            html.append(f"<p><strong>Where:</strong> {_cap_terms(issue.get('location', 'N/A'))}</p>")
            html.append(f"<p><strong>Observation:</strong> {_cap_terms(issue.get('observation', issue.get('problem', 'N/A')))}</p>")
            html.append(f"<p><strong>Why Uncertain:</strong> {_cap_terms(issue.get('why_uncertain', 'Requires human review'))}</p>")
            html.append(f"<p class='confidence'><em>Confidence: {issue.get('confidence', 'low')} - Requires human review</em></p>")
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

    # Traps Not Found — split into tested-clean vs could-not-test
    html.append("<div class='traps-not-found'>")
    html.append("<h2>Traps Checked But Not Found</h2>")
    raw_items = report.get('traps_checked_not_found', [])
    tested_ok = []
    untestable = []
    for item in raw_items:
        if isinstance(item, str):
            tested_ok.append(item)           # backward compat with old string format
        elif item.get('testable', True):
            tested_ok.append(item['trap_name'])
        else:
            untestable.append(item)

    if tested_ok:
        html.append("<h3>✓ Evaluated — Not Present</h3>")
        html.append("<ul class='trap-list'>")
        for trap in tested_ok:
            html.append(f"<li>{trap}</li>")
        html.append("</ul>")

    if untestable:
        html.append("<h3>⚠ Could Not Evaluate — Insufficient Information</h3>")
        html.append("<p class='untestable-note'>These Traps require additional screenshots, interaction data, or session context to assess:</p>")
        html.append("<ul class='untestable-list'>")
        for item in untestable:
            reason = _cap_terms(_untestable_reason(item.get('trap_name', ''), item.get('reason')))
            html.append(f"<li><span class='trap-label'>{item['trap_name'].upper()}</span> — {reason}</li>")
        html.append("</ul>")

    if not tested_ok and not untestable:
        html.append("<p>All traps were either found or not fully evaluated</p>")
    html.append("</div>")

    # Trap Coverage Matrix
    html.append(_build_trap_matrix_html(report))

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


def get_report_statistics(report: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract statistics from report for tracking/analytics.

    Args:
        report: Parsed report dictionary

    Returns:
        Dictionary with report statistics
    """
    user_issues = report.get('user_issues', [])
    return {
        'total_issues': len(report['critical_issues']) + len(report['moderate_issues']) + len(report['minor_issues']),
        'critical_count': len(report['critical_issues']),
        'moderate_count': len(report['moderate_issues']),
        'minor_count': len(report['minor_issues']),
        'positive_count': len(report['positive_observations']),
        'traps_not_found_count': len(report.get('traps_checked_not_found', [])),
        'summary_length': len(report['summary']),
        'user_issues_count': len(user_issues),
        'user_issues_high': sum(1 for i in user_issues if i.get('impact_level') == 'high'),
        'user_issues_medium': sum(1 for i in user_issues if i.get('impact_level') == 'medium'),
        'user_issues_low': sum(1 for i in user_issues if i.get('impact_level') == 'low'),
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
