"""
Report Generator for Site-Wide Analysis

Generates cohesive, rolled-up reports from multi-page site analysis.
Page-centric format: shows all issues organized by page with full details.

Copyright © 2009-present UI Traps LLC. All Rights Reserved.
"""

from typing import Dict, List, Any
from datetime import datetime
from urllib.parse import urlparse


def generate_site_report(analysis_result: Dict[str, Any], url: str, format: str = "html") -> str:
    """
    Generate a site analysis report in the specified format.

    Args:
        analysis_result: Complete result from SiteAnalyzer.analyze_site()
        url: Starting URL or identifier of the site
        format: Output format ("html" or "markdown")

    Returns:
        Complete report as string
    """
    if format == "markdown":
        return generate_site_report_markdown(analysis_result, url)
    return generate_site_report_html(analysis_result, url)


def generate_site_report_markdown(analysis_result: Dict[str, Any], url: str) -> str:
    """
    Generate a cohesive markdown report for entire site analysis.
    Page-centric format with all issues shown per page.

    Args:
        analysis_result: Complete result from SiteAnalyzer.analyze_site()
        url: Starting URL of the site

    Returns:
        Complete markdown report as string
    """
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
    # Page-by-page with ALL issues
    for page_result in page_analyses:
        page = page_result.get("page", {})
        role = page_result.get("page_role", "unknown")
        page_url = page.get('url', 'Unknown')
        title = page.get('title', 'Unknown')

        report += f"### {title}\n\n"
        report += f"**Role:** {role.upper()}\n"
        report += f"**URL:** [{page_url}]({page_url})\n\n"

        if not page_result.get("success"):
            report += f"*Error analyzing this page: {page_result.get('error', 'Unknown error')}*\n\n"
            report += "---\n\n"
            continue

        analysis = page_result.get("analysis") or {}
        page_stats = analysis.get("statistics") or {}
        page_report = analysis.get("report") or {}

        critical_count = page_stats.get('critical_count', 0)
        moderate_count = page_stats.get('moderate_count', 0)
        minor_count = page_stats.get('minor_count', 0)

        report += f"**Issues Found:** {critical_count} critical, {moderate_count} moderate, {minor_count} minor\n\n"

        # Critical issues
        for issue in page_report.get("critical_issues", []):
            report += f"#### 🔴 CRITICAL: {issue.get('trap_name', 'Unknown')}\n\n"
            report += f"**Tenet Violated:** {issue.get('tenet', 'Unknown')}\n"
            report += f"**Location:** {issue.get('location', 'Unknown')}\n\n"
            report += f"**Problem:** {issue.get('problem', 'No description')}\n\n"
            report += f"**Recommendation:** {issue.get('recommendation', 'No recommendation')}\n\n"

        # Moderate issues
        for issue in page_report.get("moderate_issues", []):
            report += f"#### 🟡 MODERATE: {issue.get('trap_name', 'Unknown')}\n\n"
            report += f"**Tenet Violated:** {issue.get('tenet', 'Unknown')}\n"
            report += f"**Location:** {issue.get('location', 'Unknown')}\n\n"
            report += f"**Problem:** {issue.get('problem', 'No description')}\n\n"
            report += f"**Recommendation:** {issue.get('recommendation', 'No recommendation')}\n\n"

        # Minor issues
        for issue in page_report.get("minor_issues", []):
            report += f"#### 🟢 MINOR: {issue.get('trap_name', 'Unknown')}\n\n"
            report += f"**Tenet Violated:** {issue.get('tenet', 'Unknown')}\n"
            report += f"**Location:** {issue.get('location', 'Unknown')}\n\n"
            report += f"**Problem:** {issue.get('problem', 'No description')}\n\n"
            report += f"**Recommendation:** {issue.get('recommendation', 'No recommendation')}\n\n"

        # Positive observations
        positives = page_report.get("positive_observations", [])
        if positives:
            report += "#### ✅ Positive Observations\n\n"
            for pos in positives:
                report += f"- {pos}\n"
            report += "\n"

        # No issues found
        if critical_count == 0 and moderate_count == 0 and minor_count == 0:
            report += "*No UI Traps detected on this page.*\n\n"

        report += "---\n\n"

    # Footer
    report += """
## Methodology

This analysis used the **UI Tenets & Traps** heuristic framework, which evaluates interfaces against 27 common usability pitfalls organized under 9 core tenets.

Each page was analyzed considering its **role** in the site (homepage, product page, contact, etc.) and evaluated only for tasks **appropriate to that page type**.

---

*Analysis powered by UI Traps Analyzer*
*Copyright © 2009-present UI Traps LLC. All Rights Reserved.*

## ⚠️ CONFIDENTIALITY NOTICE

**PROPRIETARY & CONFIDENTIAL:** This analysis report is provided exclusively to authorized subscribers.
Reproduction, distribution, or sharing without written permission is prohibited.
"""

    return report


def generate_site_report_html(analysis_result: Dict[str, Any], url: str) -> str:
    """
    Generate a cohesive HTML report for entire site analysis.
    Page-centric format with all issues shown per page.

    Args:
        analysis_result: Complete result from SiteAnalyzer.analyze_site()
        url: Starting URL of the site

    Returns:
        Complete HTML report as string
    """
    domain = urlparse(url).netloc
    summary = analysis_result.get("site_summary", {})
    page_analyses = analysis_result.get("page_analyses", [])
    metadata = analysis_result.get("metadata", {})

    # Count by severity
    critical_count = summary.get('critical_count', 0)
    moderate_count = summary.get('moderate_count', 0)
    minor_count = summary.get('minor_count', 0)
    total_issues = summary.get('total_issues', 0)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>UI Traps Analysis: {domain}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
            padding: 20px;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #1a1a1a;
            font-size: 2.2em;
            margin-bottom: 10px;
            border-bottom: 3px solid #6366f1;
            padding-bottom: 15px;
        }}
        h2 {{
            color: #2c3e50;
            font-size: 1.5em;
            margin: 30px 0 15px 0;
            padding-bottom: 8px;
            border-bottom: 2px solid #e5e7eb;
        }}
        h3 {{
            color: #374151;
            font-size: 1.3em;
            margin: 25px 0 10px 0;
        }}
        .meta {{
            background: #f8fafc;
            padding: 15px 20px;
            border-radius: 8px;
            margin-bottom: 25px;
            border-left: 4px solid #6366f1;
        }}
        .meta p {{ margin: 5px 0; color: #64748b; }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        .stat-card {{
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            color: white;
        }}
        .stat-card.critical {{ background: linear-gradient(135deg, #ef4444, #dc2626); }}
        .stat-card.moderate {{ background: linear-gradient(135deg, #f59e0b, #d97706); }}
        .stat-card.minor {{ background: linear-gradient(135deg, #22c55e, #16a34a); }}
        .stat-card.total {{ background: linear-gradient(135deg, #6366f1, #4f46e5); }}
        .stat-card h3 {{ color: white; font-size: 2em; margin: 0; }}
        .stat-card p {{ opacity: 0.9; margin-top: 5px; font-size: 0.9em; }}
        .assessment {{
            background: #fef3c7;
            border: 1px solid #f59e0b;
            padding: 15px 20px;
            border-radius: 8px;
            margin: 20px 0;
        }}
        .assessment.good {{
            background: #dcfce7;
            border-color: #22c55e;
        }}
        .page-section {{
            background: #fafafa;
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: 25px;
            margin: 25px 0;
        }}
        .page-header {{
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 15px;
            flex-wrap: wrap;
        }}
        .page-header h3 {{
            margin: 0;
            flex-grow: 1;
        }}
        .role-badge {{
            background: #6366f1;
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: 600;
            text-transform: uppercase;
        }}
        .page-url {{
            font-size: 0.9em;
            margin-bottom: 15px;
        }}
        .page-url a {{
            color: #6366f1;
            text-decoration: none;
        }}
        .page-url a:hover {{
            text-decoration: underline;
        }}
        .issue-summary {{
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }}
        .issue-count {{
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
        }}
        .issue-count.critical {{ background: #fef2f2; color: #dc2626; }}
        .issue-count.moderate {{ background: #fffbeb; color: #d97706; }}
        .issue-count.minor {{ background: #f0fdf4; color: #16a34a; }}
        .issue-card {{
            border-radius: 8px;
            padding: 20px;
            margin: 15px 0;
            border-left: 4px solid;
        }}
        .issue-card.critical {{
            background: #fef2f2;
            border-left-color: #ef4444;
        }}
        .issue-card.moderate {{
            background: #fffbeb;
            border-left-color: #f59e0b;
        }}
        .issue-card.minor {{
            background: #f0fdf4;
            border-left-color: #22c55e;
        }}
        .issue-card h4 {{
            margin: 0 0 12px 0;
            font-size: 1.1em;
        }}
        .issue-card .severity-label {{
            font-weight: 700;
            text-transform: uppercase;
            font-size: 0.75em;
            letter-spacing: 0.5px;
        }}
        .issue-card .severity-label.critical {{ color: #dc2626; }}
        .issue-card .severity-label.moderate {{ color: #d97706; }}
        .issue-card .severity-label.minor {{ color: #16a34a; }}
        .issue-meta {{
            font-size: 0.9em;
            color: #64748b;
            margin-bottom: 12px;
        }}
        .issue-problem {{
            margin-bottom: 12px;
        }}
        .issue-recommendation {{
            background: rgba(255,255,255,0.7);
            padding: 12px 15px;
            border-radius: 6px;
            font-size: 0.95em;
        }}
        .issue-recommendation strong {{
            color: #4f46e5;
        }}
        .positive-section {{
            background: #f0fdf4;
            border-radius: 8px;
            padding: 15px 20px;
            margin-top: 15px;
        }}
        .positive-section h4 {{
            color: #166534;
            margin: 0 0 10px 0;
            font-size: 1em;
        }}
        .positive-section ul {{
            margin: 0;
            padding-left: 20px;
        }}
        .positive-section li {{
            margin: 5px 0;
            color: #166534;
        }}
        .no-issues {{
            color: #166534;
            background: #dcfce7;
            padding: 15px 20px;
            border-radius: 8px;
            text-align: center;
        }}
        .toc {{
            background: #f8fafc;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }}
        .toc h3 {{ margin-bottom: 15px; font-size: 1.1em; }}
        .toc ul {{ list-style: none; }}
        .toc li {{ margin: 8px 0; }}
        .toc a {{ color: #6366f1; text-decoration: none; }}
        .toc a:hover {{ text-decoration: underline; }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #e5e7eb;
            text-align: center;
            color: #64748b;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>UI Traps Site Analysis: {domain}</h1>

        <div class="meta">
            <p><strong>Analysis Date:</strong> {metadata.get('timestamp', '')}</p>
            <p><strong>Pages Analyzed:</strong> {metadata.get('pages_analyzed', 0)}</p>
            <p><strong>Starting URL:</strong> <a href="{url}" target="_blank">{url}</a></p>
        </div>

        <div class="toc">
            <h3>Pages Analyzed</h3>
            <ul>
"""

    # Build table of contents
    for i, page_result in enumerate(page_analyses):
        page = page_result.get("page", {})
        title = page.get('title', 'Unknown')
        role = page_result.get("page_role", "unknown")
        html += f'                <li><a href="#page-{i}">{title}</a> <span style="color: #64748b; font-size: 0.85em;">({role})</span></li>\n'

    html += f"""            </ul>
        </div>

        <h2>Executive Summary</h2>

        <div class="assessment {"good" if critical_count == 0 else ""}">
            <strong>Overall Assessment:</strong> {summary.get('overall_assessment', '')}
        </div>

        <div class="stats-grid">
            <div class="stat-card critical">
                <h3>{critical_count}</h3>
                <p>Critical</p>
            </div>
            <div class="stat-card moderate">
                <h3>{moderate_count}</h3>
                <p>Moderate</p>
            </div>
            <div class="stat-card minor">
                <h3>{minor_count}</h3>
                <p>Minor</p>
            </div>
            <div class="stat-card total">
                <h3>{total_issues}</h3>
                <p>Total</p>
            </div>
        </div>

        <h2>Page-by-Page Analysis</h2>
"""

    # Page-by-page with ALL issues
    for i, page_result in enumerate(page_analyses):
        page = page_result.get("page", {})
        role = page_result.get("page_role", "unknown")
        page_url = page.get('url', '#')
        title = page.get('title', 'Unknown')

        html += f"""
        <div class="page-section" id="page-{i}">
            <div class="page-header">
                <h3>{title}</h3>
                <span class="role-badge">{role}</span>
            </div>
            <p class="page-url"><a href="{page_url}" target="_blank">{page_url}</a></p>
"""

        if not page_result.get("success"):
            html += f'            <p style="color: #dc2626;"><em>Error analyzing this page: {page_result.get("error", "Unknown error")}</em></p>\n'
            html += "        </div>\n"
            continue

        analysis = page_result.get("analysis") or {}
        page_stats = analysis.get("statistics") or {}
        page_report = analysis.get("report") or {}

        page_critical = page_stats.get('critical_count', 0)
        page_moderate = page_stats.get('moderate_count', 0)
        page_minor = page_stats.get('minor_count', 0)

        html += f"""
            <div class="issue-summary">
                <span class="issue-count critical">{page_critical} critical</span>
                <span class="issue-count moderate">{page_moderate} moderate</span>
                <span class="issue-count minor">{page_minor} minor</span>
            </div>
"""

        # Check if no issues
        if page_critical == 0 and page_moderate == 0 and page_minor == 0:
            html += '            <div class="no-issues">✅ No UI Traps detected on this page</div>\n'
        else:
            # Critical issues
            for issue in page_report.get("critical_issues", []):
                html += f"""
            <div class="issue-card critical">
                <h4><span class="severity-label critical">🔴 CRITICAL</span> — {issue.get('trap_name', 'Unknown')}</h4>
                <p class="issue-meta"><strong>Tenet:</strong> {issue.get('tenet', 'Unknown')} | <strong>Location:</strong> {issue.get('location', 'Unknown')}</p>
                <p class="issue-problem">{issue.get('problem', 'No description')}</p>
                <div class="issue-recommendation">
                    <strong>Recommendation:</strong> {issue.get('recommendation', 'No recommendation')}
                </div>
            </div>
"""

            # Moderate issues
            for issue in page_report.get("moderate_issues", []):
                html += f"""
            <div class="issue-card moderate">
                <h4><span class="severity-label moderate">🟡 MODERATE</span> — {issue.get('trap_name', 'Unknown')}</h4>
                <p class="issue-meta"><strong>Tenet:</strong> {issue.get('tenet', 'Unknown')} | <strong>Location:</strong> {issue.get('location', 'Unknown')}</p>
                <p class="issue-problem">{issue.get('problem', 'No description')}</p>
                <div class="issue-recommendation">
                    <strong>Recommendation:</strong> {issue.get('recommendation', 'No recommendation')}
                </div>
            </div>
"""

            # Minor issues
            for issue in page_report.get("minor_issues", []):
                html += f"""
            <div class="issue-card minor">
                <h4><span class="severity-label minor">🟢 MINOR</span> — {issue.get('trap_name', 'Unknown')}</h4>
                <p class="issue-meta"><strong>Tenet:</strong> {issue.get('tenet', 'Unknown')} | <strong>Location:</strong> {issue.get('location', 'Unknown')}</p>
                <p class="issue-problem">{issue.get('problem', 'No description')}</p>
                <div class="issue-recommendation">
                    <strong>Recommendation:</strong> {issue.get('recommendation', 'No recommendation')}
                </div>
            </div>
"""

        # Positive observations
        positives = page_report.get("positive_observations", [])
        if positives:
            html += """
            <div class="positive-section">
                <h4>✅ Positive Observations</h4>
                <ul>
"""
            for pos in positives:
                html += f"                    <li>{pos}</li>\n"
            html += """                </ul>
            </div>
"""

        html += "        </div>\n"

    # Footer
    html += """
        <div class="footer">
            <p><em>Analysis powered by UI Traps Analyzer</em></p>
            <p><em>Copyright © 2009-present UI Traps LLC. All Rights Reserved.</em></p>
            <p style="margin-top: 15px; font-size: 0.85em;">
                <strong>CONFIDENTIALITY NOTICE:</strong> This report is proprietary and confidential.
                Reproduction or distribution without permission is prohibited.
            </p>
        </div>
    </div>
</body>
</html>
"""

    return html
