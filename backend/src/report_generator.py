"""
Report Generator for Site-Wide Analysis

Generates cohesive, rolled-up reports from multi-page site analysis.
Page-centric format: shows all issues organized by page with full details.

Copyright © 2009-present UI Traps LLC. All Rights Reserved.
"""

from typing import Dict, List, Any
from datetime import datetime
from urllib.parse import urlparse

try:
    from .formatters import get_report_base_css, _tenet_pill_html
except ImportError:
    from formatters import get_report_base_css, _tenet_pill_html


def generate_site_report(analysis_result: Dict[str, Any], url: str, format: str = "html") -> str:
    if format == "markdown":
        return generate_site_report_markdown(analysis_result, url)
    return generate_site_report_html(analysis_result, url)


def generate_site_report_markdown(analysis_result: Dict[str, Any], url: str) -> str:
    domain = urlparse(url).netloc
    summary = analysis_result.get("site_summary", {})
    page_analyses = analysis_result.get("page_analyses", [])
    metadata = analysis_result.get("metadata", {})

    report = f"""# UI Traps Site Analysis: {domain}

**Analysis Date:** {metadata.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M'))}
**Pages Analyzed:** {metadata.get('pages_analyzed', 0)}

---

## Executive Summary

**Overall Assessment:** {summary.get('overall_assessment', 'No assessment available')}

| Metric | Count |
|--------|-------|
| Critical Issues | {summary.get('critical_count', 0)} |
| Moderate Issues | {summary.get('moderate_count', 0)} |
| Minor Issues | {summary.get('minor_count', 0)} |
| **Total Issues** | **{summary.get('total_issues', 0)}** |

---

## Page-by-Page Analysis

"""
    for page_result in page_analyses:
        page = page_result.get("page", {})
        role = page_result.get("page_role", "unknown")
        page_url = page.get('url', 'Unknown')
        title = page.get('title', 'Unknown')

        report += f"### {title}\n\n"
        report += f"**Role:** {role.upper()}\n"
        report += f"**URL:** [{page_url}]({page_url})\n\n"

        if not page_result.get("success"):
            report += f"*Error analyzing this page: {page_result.get('error', 'Unknown error')}*\n\n---\n\n"
            continue

        analysis = page_result.get("analysis") or {}
        page_stats = analysis.get("statistics") or {}
        page_report = analysis.get("report") or {}

        critical_count = page_stats.get('critical_count', 0)
        moderate_count = page_stats.get('moderate_count', 0)
        minor_count = page_stats.get('minor_count', 0)

        report += f"**Issues Found:** {critical_count} critical, {moderate_count} moderate, {minor_count} minor\n\n"

        for issue in page_report.get("critical_issues", []):
            report += f"#### 🔴 CRITICAL: {issue.get('trap_name', 'Unknown')}\n\n"
            report += f"**Tenet Violated:** {issue.get('tenet', 'Unknown')}\n"
            report += f"**Location:** {issue.get('location', 'Unknown')}\n\n"
            report += f"**Problem:** {issue.get('problem', 'No description')}\n\n"
            report += f"**Recommendation:** {issue.get('recommendation', 'No recommendation')}\n\n"

        for issue in page_report.get("moderate_issues", []):
            report += f"#### 🟡 MODERATE: {issue.get('trap_name', 'Unknown')}\n\n"
            report += f"**Tenet Violated:** {issue.get('tenet', 'Unknown')}\n"
            report += f"**Location:** {issue.get('location', 'Unknown')}\n\n"
            report += f"**Problem:** {issue.get('problem', 'No description')}\n\n"
            report += f"**Recommendation:** {issue.get('recommendation', 'No recommendation')}\n\n"

        for issue in page_report.get("minor_issues", []):
            report += f"#### 🔵 MINOR: {issue.get('trap_name', 'Unknown')}\n\n"
            report += f"**Tenet Violated:** {issue.get('tenet', 'Unknown')}\n"
            report += f"**Location:** {issue.get('location', 'Unknown')}\n\n"
            report += f"**Problem:** {issue.get('problem', 'No description')}\n\n"
            report += f"**Recommendation:** {issue.get('recommendation', 'No recommendation')}\n\n"

        positives = page_report.get("positive_observations", [])
        if positives:
            report += "#### ✅ Positive Observations\n\n"
            for pos in positives:
                report += f"- {pos}\n"
            report += "\n"

        if critical_count == 0 and moderate_count == 0 and minor_count == 0:
            report += "*No UI Traps detected on this page.*\n\n"

        report += "---\n\n"

    report += """
## Methodology

This analysis used the **UI Tenets & Traps** heuristic framework, which evaluates interfaces against 27 common usability pitfalls organized under 9 core tenets.

---

*Analysis powered by UI Traps Analyzer*
*Copyright © 2009-present UI Traps LLC. All Rights Reserved.*
"""
    return report


def _render_issue_card(issue: Dict[str, Any], severity: str, idx: int) -> str:
    trap_name = issue.get('trap_name', 'Unknown')
    tenet = issue.get('tenet', '')
    location = issue.get('location', '')
    problem = issue.get('problem', '')
    recommendation = issue.get('recommendation', '')

    sev_class = {'critical': 'sev-critical', 'moderate': 'sev-moderate', 'minor': 'sev-minor'}.get(severity, '')
    sev_label = severity.upper()
    pill_html = _tenet_pill_html(trap_name, tenet) if tenet else f"<span>{trap_name}</span>"

    return f"""
<div class="issue-card">
  <div class="issue-card-body">
    <p class="finding-num">{sev_label} &nbsp;#{idx}</p>
    <div class="issue-meta">
      <span class="sev-dot {sev_class}"></span>
      {pill_html}
      {"<span class='meta-sep'>|</span><span class='meta-tenet'>" + tenet + "</span>" if tenet else ""}
      {"<span class='meta-sep'>|</span><span class='meta-label'>" + location + "</span>" if location else ""}
    </div>
    <div class="issue-section">
      <p class="issue-section-label">Problem</p>
      <p class="issue-section-body">{problem}</p>
    </div>
    <div class="issue-section">
      <p class="issue-section-label">Recommendation</p>
      <p class="issue-section-body">{recommendation}</p>
    </div>
  </div>
</div>
"""


def generate_site_report_html(analysis_result: Dict[str, Any], url: str) -> str:
    domain = urlparse(url).netloc
    summary = analysis_result.get("site_summary", {})
    page_analyses = analysis_result.get("page_analyses", [])

    critical_count = summary.get('critical_count', 0)
    moderate_count = summary.get('moderate_count', 0)
    minor_count = summary.get('minor_count', 0)
    total_issues = summary.get('total_issues', 0)
    overall = summary.get('overall_assessment', '')

    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    pages_analyzed = len(page_analyses)

    assessment_cls = "good" if critical_count == 0 else ""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>UI Traps Site Analysis: {domain}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
{get_report_base_css()}
</style>
</head>
<body>
<div class="ui-traps-report">

  <h1>UI Traps<br>Site Analysis: {domain}</h1>
  <p class="timestamp">
    Generated: {now}<br>
    URL: <a href="{url}" target="_blank" style="color:#8a8680">{url}</a><br>
    Pages analyzed: {pages_analyzed}
  </p>

  <h2>Executive Summary</h2>
"""

    if overall:
        html += f'  <div class="assessment-box {assessment_cls}">{overall}</div>\n'

    html += f"""
  <div class="site-stat-row">
    <div class="site-stat">
      <div class="site-stat-num critical">{critical_count}</div>
      <div class="site-stat-label">Critical</div>
    </div>
    <div class="site-stat">
      <div class="site-stat-num moderate">{moderate_count}</div>
      <div class="site-stat-label">Moderate</div>
    </div>
    <div class="site-stat">
      <div class="site-stat-num minor">{minor_count}</div>
      <div class="site-stat-label">Minor</div>
    </div>
    <div class="site-stat">
      <div class="site-stat-num total">{total_issues}</div>
      <div class="site-stat-label">Total</div>
    </div>
  </div>

  <h2>Page-by-Page Analysis</h2>
"""

    for i, page_result in enumerate(page_analyses):
        page = page_result.get("page", {})
        role = page_result.get("page_role", "unknown")
        page_url = page.get('url', '#')
        title = page.get('title', 'Unknown')

        html += f"""
  <div class="page-card" id="page-{i}">
    <div class="page-card-header">
      <div>
        <p class="page-card-title">{title}</p>
        <p class="page-card-url"><a href="{page_url}" target="_blank">{page_url}</a></p>
      </div>
      <span class="page-role-badge">{role}</span>
    </div>
    <div class="page-card-body">
"""

        screenshot_base64 = page.get('screenshot_base64')
        if screenshot_base64:
            html += f"""
      <details class="screenshot-section">
        <summary class="screenshot-toggle">View Screenshot</summary>
        <img src="data:image/jpeg;base64,{screenshot_base64}" alt="Screenshot of {title}" loading="lazy" class="screenshot-img">
      </details>
"""

        if not page_result.get("success"):
            html += f'      <p style="color:#c0392b;font-size:0.93em"><em>Error analyzing this page: {page_result.get("error", "Unknown error")}</em></p>\n'
            html += '    </div>\n  </div>\n'
            continue

        analysis = page_result.get("analysis") or {}
        page_stats = analysis.get("statistics") or {}
        page_report = analysis.get("report") or {}

        page_critical = page_stats.get('critical_count', 0)
        page_moderate = page_stats.get('moderate_count', 0)
        page_minor = page_stats.get('minor_count', 0)

        html += f"""
      <div class="page-stat-row">
        <span class="page-stat-badge critical">{page_critical} critical</span>
        <span class="page-stat-badge moderate">{page_moderate} moderate</span>
        <span class="page-stat-badge minor">{page_minor} minor</span>
      </div>
"""

        if page_critical == 0 and page_moderate == 0 and page_minor == 0:
            html += '      <div class="no-issues-banner">✓ No UI Traps detected on this page</div>\n'
        else:
            idx = 1
            for issue in page_report.get("critical_issues", []):
                html += _render_issue_card(issue, "critical", idx)
                idx += 1
            for issue in page_report.get("moderate_issues", []):
                html += _render_issue_card(issue, "moderate", idx)
                idx += 1
            for issue in page_report.get("minor_issues", []):
                html += _render_issue_card(issue, "minor", idx)
                idx += 1

        positives = page_report.get("positive_observations", [])
        if positives:
            items = "".join(f"<li class='positive-item'>{p}</li>" for p in positives)
            html += f"""
      <div class="positives-section">
        <div class="positive-card">
          <h3 style="margin:0 0 10px;font-size:0.93em;color:#166534;">Positive Observations</h3>
          <ul>{items}</ul>
        </div>
      </div>
"""

        html += '    </div>\n  </div>\n'

    html += """
  <div class="footer confidentiality-notice">
    <p style="color:#8a8680;font-size:0.85em"><em>Analysis powered by UI Traps Analyzer &mdash; UI Tenets &amp; Traps proprietary framework</em></p>
    <hr>
    <div class="confidentiality-notice">
      <h3>⚠️ CONFIDENTIALITY NOTICE</h3>
      <p>This report is proprietary and confidential. Reproduction or distribution without written permission is prohibited.</p>
    </div>
  </div>

</div>
</body>
</html>
"""
    return html
