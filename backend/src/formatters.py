"""
Response formatting and parsing for UI Traps Analyzer

Copyright © 2009-present UI Traps LLC. All Rights Reserved.
PROPRIETARY & CONFIDENTIAL - UI Tenets & Traps Framework
"""
import json
import re
from typing import Dict, Any, Optional
from datetime import datetime


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
        md.append(f"**Users:** {user_context.get('users', 'N/A')}")
        md.append("")

        # Format tasks as bulleted list
        tasks = user_context.get('tasks', 'N/A')
        md.append("**Key Tasks:**")
        if tasks and tasks != 'N/A':
            # Split on common delimiters and create bullets
            task_list = [t.strip() for t in tasks.replace(', ', ',').split(',') if t.strip()]
            if len(task_list) > 1:
                for task in task_list:
                    md.append(f"- {task}")
            else:
                # If no commas, just show as single item
                md.append(f"- {tasks}")
        else:
            md.append("- N/A")
        md.append("")

        md.append(f"**Materials Tested:** {user_context.get('format', 'N/A')}")
        md.append("")
        md.append("---")
        md.append("")

    # Summary
    md.append("## Summary")
    md.append("")
    for bullet in report['summary']:
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
            md.append(f"**Trap Detected:** **{issue['trap_name']}**")
            md.append("")
            md.append(f"**Tenet Violated:** {issue['tenet']}")
            md.append("")
            md.append(f"**Where:** {issue['location']}")
            md.append("")
            md.append(f"**Problem:** {issue['problem']}")
            md.append("")
            md.append(f"**Recommendation:** {issue['recommendation']}")
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
            md.append(f"**Trap Detected:** **{issue['trap_name']}**")
            md.append("")
            md.append(f"**Tenet Violated:** {issue['tenet']}")
            md.append("")
            md.append(f"**Where:** {issue['location']}")
            md.append("")
            md.append(f"**Problem:** {issue['problem']}")
            md.append("")
            md.append(f"**Recommendation:** {issue['recommendation']}")
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
        md.append("## 🟢 Minor Issues")
        md.append("")
        for issue in report['minor_issues']:
            render_frame_info(issue)
            md.append(f"**Trap Detected:** **{issue['trap_name']}**")
            md.append("")
            md.append(f"**Tenet Violated:** {issue['tenet']}")
            md.append("")
            md.append(f"**Where:** {issue['location']}")
            md.append("")
            md.append(f"**Problem:** {issue['problem']}")
            md.append("")
            md.append(f"**Recommendation:** {issue['recommendation']}")
            md.append("")
            if 'confidence' in issue:
                md.append(f"*Confidence: {issue['confidence']}*")
                md.append("")
    else:
        md.append("## 🟢 Minor Issues")
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
            md.append(f"**Trap Detected:** **{issue.get('trap_name', 'UNKNOWN')}** (Potential)")
            md.append("")
            md.append(f"**Tenet:** {issue.get('tenet', 'N/A')}")
            md.append("")
            md.append(f"**Where:** {issue.get('location', 'N/A')}")
            md.append("")
            md.append(f"**Observation:** {issue.get('observation', issue.get('problem', 'N/A'))}")
            md.append("")
            md.append(f"**Why Uncertain:** {issue.get('why_uncertain', 'Requires human review')}")
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

    # Traps Checked but Not Found
    md.append("## Traps Checked But Not Found")
    md.append("")
    if report['traps_checked_not_found']:
        # Format in columns
        traps = report['traps_checked_not_found']
        for trap in traps:
            md.append(f"- {trap}")
        md.append("")
    else:
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
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .ui-traps-report {
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }
        h2 {
            color: #2c3e50;
            margin-top: 30px;
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 8px;
        }
        h3 {
            color: #34495e;
            margin-top: 20px;
        }
        .timestamp {
            color: #7f8c8d;
            font-style: italic;
        }
        .context-section {
            background: #ecf0f1;
            padding: 20px;
            border-radius: 5px;
            margin: 20px 0;
        }
        .summary-section ul {
            background: #e8f4f8;
            padding: 20px 40px;
            border-left: 4px solid #3498db;
            border-radius: 4px;
        }
        .issue-card {
            background: #fff;
            border: 1px solid #ddd;
            border-left: 4px solid #95a5a6;
            padding: 20px;
            margin: 15px 0;
            border-radius: 4px;
        }
        .issue-card.critical {
            border-left-color: #e74c3c;
            background: #fef5f5;
        }
        .issue-card.moderate {
            border-left-color: #f39c12;
            background: #fef9f5;
        }
        .issue-card.minor {
            border-left-color: #3498db;
            background: #f5f9fe;
        }
        .issue-card h3 {
            margin-top: 0;
            color: #2c3e50;
        }
        .issue-card .tenet {
            color: #7f8c8d;
            font-size: 0.9em;
        }
        .issue-card .confidence {
            color: #95a5a6;
            font-size: 0.85em;
            margin-top: 10px;
        }
        .issue-card .frame-info {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 8px 12px;
            border-radius: 4px;
            margin: 0 0 15px 0;
            font-size: 0.9em;
            display: inline-block;
        }
        .issue-card .frame-info strong {
            color: white;
        }
        .frame-thumbnail-link:hover {
            transform: scale(1.05);
            box-shadow: 0 4px 8px rgba(0,0,0,0.3) !important;
        }
        .issue-frames {
            background: #f8f9fa;
            padding: 12px;
            border-radius: 6px;
            border: 1px solid #e9ecef;
        }
        .none-found {
            color: #27ae60;
            font-style: italic;
        }
        .positive-section {
            background: #eafaf1;
            padding: 20px;
            border-radius: 5px;
            border-left: 4px solid #27ae60;
        }
        .potential-issues-section {
            background: #fff9e6;
            padding: 20px;
            border-radius: 5px;
            border-left: 4px solid #f39c12;
            margin: 20px 0;
        }
        .potential-issues-section .issue-card.potential {
            border-left-color: #f39c12;
            background: #fffbf0;
        }
        .traps-not-found {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 5px;
        }
        .trap-list {
            column-count: 2;
            column-gap: 20px;
        }
        .trap-list li {
            break-inside: avoid;
        }
        .footer {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #ecf0f1;
        }
        .confidentiality-notice {
            background: #fff3cd;
            border: 1px solid #ffc107;
            padding: 20px;
            border-radius: 5px;
            margin-top: 20px;
        }
        .confidentiality-notice h3 {
            color: #856404;
            margin-top: 0;
        }
        .confidentiality-notice ul {
            margin: 10px 0;
        }
        .confidentiality-notice li {
            margin: 5px 0;
        }
        hr {
            border: none;
            border-top: 1px solid #ecf0f1;
            margin: 20px 0;
        }
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
        html.append(f"<p><strong>Users:</strong> {user_context.get('users', 'N/A')}</p>")

        # Format tasks as bulleted list
        tasks = user_context.get('tasks', 'N/A')
        html.append("<p><strong>Key Tasks:</strong></p>")
        if tasks and tasks != 'N/A':
            task_list = [t.strip() for t in tasks.replace(', ', ',').split(',') if t.strip()]
            if len(task_list) > 1:
                html.append("<ul>")
                for task in task_list:
                    html.append(f"<li>{task}</li>")
                html.append("</ul>")
            else:
                html.append(f"<ul><li>{tasks}</li></ul>")
        else:
            html.append("<p>N/A</p>")

        html.append(f"<p><strong>Materials Tested:</strong> {user_context.get('format', 'N/A')}</p>")
        html.append("</div>")

    # Summary
    html.append("<div class='summary-section'>")
    html.append("<h2>Summary</h2>")
    html.append("<ul>")
    for bullet in report['summary']:
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

                html.append(f"<p><strong>Trap Detected:</strong> <strong>{issue['trap_name']}</strong></p>")
                html.append(f"<p class='tenet'><strong>Tenet Violated:</strong> {issue['tenet']}</p>")
                html.append(f"<p><strong>Where:</strong> {issue['location']}</p>")
                html.append(f"<p><strong>Problem:</strong> {issue['problem']}</p>")
                html.append(f"<p><strong>Recommendation:</strong> {issue['recommendation']}</p>")
                if 'confidence' in issue:
                    html.append(f"<p class='confidence'><em>Confidence: {issue['confidence']}</em></p>")
                html.append("</div>")
        else:
            html.append(f"<p class='none-found'>None found ✓</p>")

    # Critical Issues
    html.append("<div class='issues-section critical'>")
    html.append("<h2>🔴 Critical Issues</h2>")
    render_issues(report['critical_issues'], "🔴", "critical")
    html.append("</div>")

    # Moderate Issues
    html.append("<div class='issues-section moderate'>")
    html.append("<h2>🟡 Moderate Issues</h2>")
    render_issues(report['moderate_issues'], "🟡", "moderate")
    html.append("</div>")

    # Minor Issues
    html.append("<div class='issues-section minor'>")
    html.append("<h2>🟢 Minor Issues</h2>")
    render_issues(report['minor_issues'], "🟢", "minor")
    html.append("</div>")

    # Positive Observations
    html.append("<div class='positive-section'>")
    html.append("<h2>✅ Positive Observations</h2>")
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
        html.append("<div class='bugs-section' style='background: #fce4ec; padding: 20px; border-radius: 5px; border-left: 4px solid #e91e63; margin: 20px 0;'>")
        html.append("<h2>🐛 Technical Bugs Detected</h2>")
        html.append("<p><em>These are technical issues or broken states, not UI Traps. They represent system failures that should be fixed regardless of usability.</em></p>")
        for bug in report['bugs_detected']:
            html.append("<div class='issue-card' style='border-left-color: #e91e63; background: #fff5f7;'>")

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

            html.append(f"<p><strong>Trap Detected:</strong> <strong>{issue.get('trap_name', 'UNKNOWN')}</strong> (Potential)</p>")
            html.append(f"<p class='tenet'><strong>Tenet:</strong> {issue.get('tenet', 'N/A')}</p>")
            html.append(f"<p><strong>Where:</strong> {issue.get('location', 'N/A')}</p>")
            html.append(f"<p><strong>Observation:</strong> {issue.get('observation', issue.get('problem', 'N/A'))}</p>")
            html.append(f"<p><strong>Why Uncertain:</strong> {issue.get('why_uncertain', 'Requires human review')}</p>")
            html.append(f"<p class='confidence'><em>Confidence: {issue.get('confidence', 'low')} - Requires human review</em></p>")
            html.append("</div>")
        html.append("</div>")

    # Cross-Frame Issues (for video/multi-frame analysis)
    if report.get('cross_frame_issues') and len(report['cross_frame_issues']) > 0:
        html.append("<div class='cross-frame-section' style='background: #e8f5e9; padding: 20px; border-radius: 5px; border-left: 4px solid #4caf50; margin: 20px 0;'>")
        html.append("<h2>🔄 Cross-Frame Issues</h2>")
        html.append("<p><em>These issues were detected by comparing element positions across multiple frames:</em></p>")
        for issue in report['cross_frame_issues']:
            severity_color = '#f39c12' if issue.get('severity') == 'moderate' else '#e74c3c' if issue.get('severity') == 'critical' else '#3498db'
            html.append(f"<div class='issue-card' style='border-left-color: {severity_color}; background: #f5fff5;'>")
            html.append(f"<h3 style='margin-top: 0; color: #2c3e50;'>{issue.get('trap_name', 'WANDERING ELEMENT')}</h3>")
            html.append(f"<p class='tenet'><strong>Tenet:</strong> {issue.get('tenet', 'HABITUATING')}</p>")
            html.append(f"<p><strong>Element:</strong> {issue.get('element_description', 'UI element')}</p>")

            # Show locations as tags
            locations = issue.get('locations_found', [])
            if locations:
                html.append("<p><strong>Locations Found:</strong></p>")
                html.append("<div style='display: flex; flex-wrap: wrap; gap: 8px; margin: 8px 0;'>")
                for loc in locations:
                    html.append(f"<span style='background: #667eea; color: white; padding: 4px 12px; border-radius: 16px; font-size: 0.85em;'>{loc}</span>")
                html.append("</div>")

            html.append(f"<p><strong>Problem:</strong> {issue.get('problem', 'N/A')}</p>")

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
        html.append("<div class='frame-quality-section' style='background: #e3f2fd; padding: 20px; border-radius: 5px; border-left: 4px solid #2196f3; margin: 20px 0;'>")
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

    # Traps Not Found
    html.append("<div class='traps-not-found'>")
    html.append("<h2>Traps Checked But Not Found</h2>")
    if report['traps_checked_not_found']:
        html.append("<ul class='trap-list'>")
        for trap in report['traps_checked_not_found']:
            html.append(f"<li>{trap}</li>")
        html.append("</ul>")
    else:
        html.append("<p>All traps were either found or not fully evaluated</p>")
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


def get_report_statistics(report: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract statistics from report for tracking/analytics.

    Args:
        report: Parsed report dictionary

    Returns:
        Dictionary with report statistics
    """
    return {
        'total_issues': len(report['critical_issues']) + len(report['moderate_issues']) + len(report['minor_issues']),
        'critical_count': len(report['critical_issues']),
        'moderate_count': len(report['moderate_issues']),
        'minor_count': len(report['minor_issues']),
        'positive_count': len(report['positive_observations']),
        'traps_not_found_count': len(report['traps_checked_not_found']),
        'summary_length': len(report['summary'])
    }
