"""
Report Generator for Site-Wide Analysis

Generates cohesive, rolled-up reports from multi-page site analysis.

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

    Args:
        analysis_result: Complete result from SiteAnalyzer.analyze_site()
        url: Starting URL of the site

    Returns:
        Complete markdown report as string
    """
    domain = urlparse(url).netloc
    summary = analysis_result.get("site_summary", {})
    stats = analysis_result.get("statistics", {})
    flow_analyses = analysis_result.get("flow_analyses", [])
    recommendations = analysis_result.get("recommendations", [])
    page_analyses = analysis_result.get("page_analyses", [])
    metadata = analysis_result.get("metadata", {})

    report = f"""# UI Traps Site Analysis: {domain}

**Analysis Date:** {metadata.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M'))}
**Pages Analyzed:** {metadata.get('pages_analyzed', 0)}
**Analysis Duration:** {metadata.get('duration_seconds', 0)} seconds

---

## Executive Summary

**Overall Assessment:** {summary.get('overall_assessment', 'No assessment available')}

| Metric | Count |
|--------|-------|
| Critical Issues | {summary.get('critical_count', 0)} |
| Moderate Issues | {summary.get('moderate_count', 0)} |
| Minor Issues | {summary.get('minor_count', 0)} |
| Positive Observations | {summary.get('positive_count', 0)} |
| **Total Issues** | **{summary.get('total_issues', 0)}** |

### Page Roles Identified

"""
    # List page roles
    for page_result in page_analyses:
        if page_result.get("success"):
            page = page_result.get("page", {})
            role = page_result.get("page_role", "unknown")
            report += f"- **{page.get('title', 'Unknown')}**: {role.upper()}\n"

    report += """
---

## Task Flow Analysis

This section evaluates whether users can complete their goals across the site.

"""
    # Task flows
    tasks = summary.get("tasks_evaluated", [])
    for flow in flow_analyses:
        task = flow.get("task", "Unknown task")
        complete = flow.get("complete", False)
        status = "✅ Complete" if complete else "⚠️ Incomplete"

        report += f"### {task}\n\n"
        report += f"**Status:** {status}\n\n"

        if not complete:
            missing = flow.get("missing_page_types", [])
            report += f"**Missing page types:** {', '.join(missing)}\n\n"
            report += f"**Assessment:** {flow.get('assessment', '')}\n\n"
        else:
            report += "Users have a clear path to complete this task.\n\n"

    # Site-wide issues
    sitewide = summary.get("sitewide_issues", [])
    if sitewide:
        report += """---

## Site-Wide Patterns

These issues appear across multiple pages and should be prioritized for fixing:

"""
        for issue in sitewide:
            report += f"- **{issue['trap']}**: Found on {issue['count']} pages\n"
        report += "\n"

    # Critical issues
    critical_recs = [r for r in recommendations if r.get("severity") == "critical"]
    if critical_recs:
        report += """---

## 🔴 Critical Issues

These issues block core user tasks and require immediate attention:

"""
        for rec in critical_recs:
            report += f"""### {rec.get('trap_name', 'Unknown')}

**Page:** {rec.get('page', 'Unknown')}
**Location:** {rec.get('location', 'Unknown')}

**Problem:** {rec.get('problem', 'No description')}

**Recommendation:** {rec.get('recommendation', 'No recommendation')}

"""

    # Moderate issues
    moderate_recs = [r for r in recommendations if r.get("severity") == "moderate"]
    if moderate_recs:
        report += """---

## 🟡 Moderate Issues

These issues slow users down or cause frustration:

"""
        for rec in moderate_recs[:10]:  # Limit to top 10
            report += f"""### {rec.get('trap_name', 'Unknown')}

**Page:** {rec.get('page', 'Unknown')}
**Location:** {rec.get('location', 'Unknown')}

**Problem:** {rec.get('problem', 'No description')}

**Recommendation:** {rec.get('recommendation', 'No recommendation')}

"""
        if len(moderate_recs) > 10:
            report += f"*...and {len(moderate_recs) - 10} more moderate issues. See page details below.*\n\n"

    # Top recommendations summary
    report += """---

## Top Recommendations

Prioritized list of improvements:

"""
    for i, rec in enumerate(recommendations[:10], 1):
        severity_icon = {"critical": "🔴", "moderate": "🟡", "minor": "🟢"}.get(rec.get("severity"), "⚪")
        report += f"{i}. {severity_icon} **{rec.get('trap_name')}** ({rec.get('page')}): {rec.get('recommendation', '')}\n\n"

    # Page-by-page summary
    report += """---

## Page-by-Page Summary

"""
    for page_result in page_analyses:
        page = page_result.get("page", {})
        role = page_result.get("page_role", "unknown")

        report += f"### {page.get('title', 'Unknown')} ({role.upper()})\n\n"
        report += f"**URL:** {page.get('url', 'Unknown')}\n\n"

        if not page_result.get("success"):
            report += f"*Error analyzing this page: {page_result.get('error', 'Unknown error')}*\n\n"
            continue

        analysis = page_result.get("analysis") or {}
        page_stats = analysis.get("statistics") or {}

        report += f"**Issues:** {page_stats.get('critical_count', 0)} critical, "
        report += f"{page_stats.get('moderate_count', 0)} moderate, "
        report += f"{page_stats.get('minor_count', 0)} minor\n\n"

        # List issues for this page
        page_report = analysis.get("report") or {}
        for issue in page_report.get("critical_issues", []):
            report += f"- 🔴 **{issue.get('trap_name')}**: {issue.get('problem', '')[:100]}...\n"
        for issue in page_report.get("moderate_issues", []):
            report += f"- 🟡 **{issue.get('trap_name')}**: {issue.get('problem', '')[:100]}...\n"

        if page_report.get("critical_issues") or page_report.get("moderate_issues"):
            report += "\n"

    # Footer
    report += """---

## Methodology

This analysis used the **UI Tenets & Traps** heuristic framework, which evaluates interfaces against 27 common usability pitfalls organized by four core tenets:

- **UNDERSTANDABLE**: Users can comprehend what they see
- **EFFICIENT**: Users can accomplish tasks without unnecessary effort
- **TRUSTWORTHY**: Users can rely on the system to behave predictably
- **BEAUTIFUL**: The interface is aesthetically pleasing and professional

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

    Args:
        analysis_result: Complete result from SiteAnalyzer.analyze_site()
        url: Starting URL of the site

    Returns:
        Complete HTML report as string
    """
    domain = urlparse(url).netloc
    summary = analysis_result.get("site_summary", {})
    stats = analysis_result.get("statistics", {})
    flow_analyses = analysis_result.get("flow_analyses", [])
    recommendations = analysis_result.get("recommendations", [])
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
            font-size: 1.2em;
            margin: 20px 0 10px 0;
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
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
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
        .stat-card p {{ opacity: 0.9; margin-top: 5px; }}
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
        .flow-item {{
            background: #f8fafc;
            border-radius: 8px;
            padding: 15px 20px;
            margin: 15px 0;
            border-left: 4px solid #6366f1;
        }}
        .flow-item.incomplete {{
            border-left-color: #f59e0b;
            background: #fffbeb;
        }}
        .flow-item h4 {{ margin-bottom: 8px; }}
        .flow-status {{
            display: inline-block;
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: 600;
        }}
        .flow-status.complete {{ background: #dcfce7; color: #166534; }}
        .flow-status.incomplete {{ background: #fef3c7; color: #92400e; }}
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
        .issue-card h4 {{
            margin-bottom: 10px;
        }}
        .issue-card .location {{
            font-size: 0.9em;
            color: #64748b;
            margin-bottom: 10px;
        }}
        .recommendation {{
            background: #eff6ff;
            padding: 10px 15px;
            border-radius: 6px;
            margin-top: 10px;
            font-size: 0.95em;
        }}
        .page-summary {{
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 20px;
            margin: 15px 0;
        }}
        .page-summary h4 {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .role-badge {{
            background: #6366f1;
            color: white;
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 0.75em;
            font-weight: 600;
            text-transform: uppercase;
        }}
        .issue-badges {{
            display: flex;
            gap: 10px;
            margin: 10px 0;
        }}
        .badge {{
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: 600;
        }}
        .badge.critical {{ background: #fef2f2; color: #dc2626; }}
        .badge.moderate {{ background: #fffbeb; color: #d97706; }}
        .badge.minor {{ background: #f0fdf4; color: #16a34a; }}
        .recommendations-list {{
            background: #f8fafc;
            border-radius: 8px;
            padding: 20px;
        }}
        .recommendations-list ol {{
            margin-left: 20px;
        }}
        .recommendations-list li {{
            margin: 12px 0;
            line-height: 1.5;
        }}
        .severity-icon {{
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }}
        .severity-icon.critical {{ background: #ef4444; }}
        .severity-icon.moderate {{ background: #f59e0b; }}
        .severity-icon.minor {{ background: #22c55e; }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #e5e7eb;
            text-align: center;
            color: #64748b;
            font-size: 0.9em;
        }}
        .toc {{
            background: #f8fafc;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }}
        .toc h3 {{ margin-bottom: 15px; }}
        .toc ul {{ list-style: none; }}
        .toc li {{ margin: 8px 0; }}
        .toc a {{ color: #6366f1; text-decoration: none; }}
        .toc a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>UI Traps Site Analysis: {domain}</h1>

        <div class="meta">
            <p><strong>Analysis Date:</strong> {metadata.get('timestamp', '')}</p>
            <p><strong>Pages Analyzed:</strong> {metadata.get('pages_analyzed', 0)}</p>
            <p><strong>Starting URL:</strong> {url}</p>
        </div>

        <div class="toc">
            <h3>Contents</h3>
            <ul>
                <li><a href="#summary">Executive Summary</a></li>
                <li><a href="#flows">Task Flow Analysis</a></li>
                <li><a href="#critical">Critical Issues</a></li>
                <li><a href="#recommendations">Top Recommendations</a></li>
                <li><a href="#pages">Page-by-Page Details</a></li>
            </ul>
        </div>

        <h2 id="summary">Executive Summary</h2>

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
                <p>Total Issues</p>
            </div>
        </div>

        <h2 id="flows">Task Flow Analysis</h2>
        <p>Can users complete their goals across the site?</p>
"""

    # Task flows
    for flow in flow_analyses:
        complete = flow.get("complete", False)
        status_class = "complete" if complete else "incomplete"
        status_text = "Complete" if complete else "Incomplete"

        html += f"""
        <div class="flow-item {status_class}">
            <h4>{flow.get('task', '')}</h4>
            <span class="flow-status {status_class}">{status_text}</span>
"""
        if not complete:
            missing = flow.get("missing_page_types", [])
            html += f"""
            <p style="margin-top: 10px;"><strong>Missing:</strong> {', '.join(missing)}</p>
            <p><em>{flow.get('assessment', '')}</em></p>
"""
        html += "        </div>\n"

    # Critical issues
    critical_recs = [r for r in recommendations if r.get("severity") == "critical"]
    html += f"""
        <h2 id="critical">Critical Issues ({len(critical_recs)})</h2>
"""
    if critical_recs:
        for rec in critical_recs:
            html += f"""
        <div class="issue-card critical">
            <h4>🔴 {rec.get('trap_name', '')}</h4>
            <p class="location"><strong>Page:</strong> {rec.get('page', '')} | <strong>Location:</strong> {rec.get('location', '')}</p>
            <p>{rec.get('problem', '')}</p>
            <div class="recommendation">
                <strong>Recommendation:</strong> {rec.get('recommendation', '')}
            </div>
        </div>
"""
    else:
        html += "        <p><em>No critical issues found!</em></p>\n"

    # Top recommendations
    html += """
        <h2 id="recommendations">Top Recommendations</h2>
        <div class="recommendations-list">
            <ol>
"""
    for rec in recommendations[:10]:
        severity = rec.get("severity", "minor")
        html += f"""                <li>
                    <span class="severity-icon {severity}"></span>
                    <strong>{rec.get('trap_name', '')}</strong> ({rec.get('page', '')}): {rec.get('recommendation', '')}
                </li>
"""
    html += """            </ol>
        </div>

        <h2 id="pages">Page-by-Page Details</h2>
"""

    # Page summaries
    for page_result in page_analyses:
        page = page_result.get("page", {})
        role = page_result.get("page_role", "unknown")
        title = page.get("title", "Unknown")

        html += f"""
        <div class="page-summary">
            <h4>{title} <span class="role-badge">{role}</span></h4>
            <p><a href="{page.get('url', '#')}" target="_blank">{page.get('url', '')}</a></p>
"""
        if page_result.get("success"):
            analysis = page_result.get("analysis") or {}
            page_stats = analysis.get("statistics") or {}

            html += f"""
            <div class="issue-badges">
                <span class="badge critical">{page_stats.get('critical_count', 0)} critical</span>
                <span class="badge moderate">{page_stats.get('moderate_count', 0)} moderate</span>
                <span class="badge minor">{page_stats.get('minor_count', 0)} minor</span>
            </div>
"""
            # List key issues
            page_report = analysis.get("report") or {}
            issues = page_report.get("critical_issues", []) + page_report.get("moderate_issues", [])[:2]
            if issues:
                html += "            <ul style='margin-top: 10px;'>\n"
                for issue in issues:
                    html += f"                <li><strong>{issue.get('trap_name', '')}</strong>: {issue.get('problem', '')[:80]}...</li>\n"
                html += "            </ul>\n"
        else:
            html += f"            <p><em>Error: {page_result.get('error', 'Unknown')}</em></p>\n"

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
