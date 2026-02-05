"""
Site Analyzer - Multi-Page Analysis Orchestration

Coordinates analysis across multiple pages with context awareness,
page role classification, and task flow evaluation.

Copyright © 2009-present UI Traps LLC. All Rights Reserved.
"""

import os
import time
from typing import Dict, List, Any, Optional
from pathlib import Path

try:
    from .analyzer import UITrapsAnalyzer
    from .page_classifier import (
        classify_page,
        classify_all_pages,
        get_relevant_tasks,
        generate_flow_analysis
    )
except ImportError:
    # Fallback for direct script execution
    from analyzer import UITrapsAnalyzer
    from page_classifier import (
        classify_page,
        classify_all_pages,
        get_relevant_tasks,
        generate_flow_analysis
    )


class SiteAnalyzer:
    """
    Orchestrates UI Traps analysis across multiple pages of a website.

    Provides context-aware analysis by:
    1. Classifying each page's role (homepage, product, contact, etc.)
    2. Mapping tasks to appropriate page types
    3. Analyzing task flows across pages
    4. Generating cohesive site-wide reports
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the site analyzer.

        Args:
            api_key: Anthropic API key (or uses ANTHROPIC_API_KEY env var)
        """
        self.analyzer = UITrapsAnalyzer(api_key=api_key)
        self.page_classifications = {}
        self.page_analyses = []
        self.flow_analyses = []

    def analyze_site(
        self,
        pages: List[Dict],
        user_context: Dict[str, Any],
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Analyze an entire website with context awareness.

        Args:
            pages: List of page dicts from crawler, each with:
                - url: Page URL
                - title: Page title
                - screenshot_path: Path to screenshot image
            user_context: Dict with:
                - users: Description of target users
                - tasks: List of user tasks (as list or newline-separated string)
                - format: Design format description
            progress_callback: Optional function(current, total, message) for progress updates

        Returns:
            Complete site analysis dict with:
                - site_summary: Overall site assessment
                - page_classifications: Role classification for each page
                - flow_analyses: Task flow evaluation
                - page_analyses: Individual page analysis results
                - statistics: Aggregate statistics
                - recommendations: Prioritized recommendations
        """
        start_time = time.time()

        # Parse tasks into list if string
        tasks = self._parse_tasks(user_context.get("tasks", []))

        # Step 1: Classify all pages
        if progress_callback:
            progress_callback(0, len(pages) + 2, "Classifying page roles...")

        self.page_classifications = classify_all_pages(pages)

        # Step 2: Analyze task flows
        if progress_callback:
            progress_callback(1, len(pages) + 2, "Analyzing task flows...")

        self.flow_analyses = generate_flow_analysis(tasks, self.page_classifications)

        # Step 3: Analyze each page with context
        self.page_analyses = []
        site_page_titles = [p.get("title", "Unknown") for p in pages]

        for i, page in enumerate(pages):
            if progress_callback:
                progress_callback(i + 2, len(pages) + 2, f"Analyzing: {page.get('title', 'Unknown')}")

            page_result = self._analyze_page_with_context(
                page=page,
                user_context=user_context,
                tasks=tasks,
                site_page_titles=site_page_titles
            )
            self.page_analyses.append(page_result)

        # Step 4: Generate aggregate statistics
        statistics = self._calculate_statistics()

        # Step 5: Generate prioritized recommendations
        recommendations = self._generate_recommendations()

        # Step 6: Generate site summary
        site_summary = self._generate_site_summary(tasks)

        duration = time.time() - start_time

        return {
            "site_summary": site_summary,
            "page_classifications": self.page_classifications,
            "flow_analyses": self.flow_analyses,
            "page_analyses": self.page_analyses,
            "statistics": statistics,
            "recommendations": recommendations,
            "metadata": {
                "pages_analyzed": len(pages),
                "tasks_evaluated": len(tasks),
                "duration_seconds": round(duration, 2),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        }

    def _parse_tasks(self, tasks: Any) -> List[str]:
        """Parse tasks into a list of strings."""
        if isinstance(tasks, list):
            return tasks
        if isinstance(tasks, str):
            # Split by newlines or common separators
            lines = tasks.replace(";", "\n").replace(",", "\n").split("\n")
            return [t.strip() for t in lines if t.strip()]
        return []

    def _analyze_page_with_context(
        self,
        page: Dict,
        user_context: Dict,
        tasks: List[str],
        site_page_titles: List[str]
    ) -> Dict[str, Any]:
        """
        Analyze a single page with full context awareness.

        Args:
            page: Page dict with url, title, screenshot_path
            user_context: Original user context
            tasks: Parsed list of tasks
            site_page_titles: Titles of all pages on site

        Returns:
            Analysis result dict
        """
        url = page.get("url", "")
        title = page.get("title", "Unknown")
        screenshot_path = page.get("screenshot_path", "")

        # Get page classification
        page_role = classify_page(url, title)
        role_info = self.page_classifications.get(url, {})

        # Get relevant tasks for this page type
        relevant_tasks = get_relevant_tasks(page_role, tasks)

        # Build task description for this page
        task_description = self._build_task_description(relevant_tasks, page_role)

        # Build page context for the analyzer
        page_context = {
            "page_role": page_role,
            "page_title": title,
            "page_url": url,
            "site_pages": site_page_titles,
            "relevant_tasks": relevant_tasks.get("full", []) + relevant_tasks.get("partial", [])
        }

        # Build modified user context
        modified_context = {
            "users": user_context.get("users", ""),
            "tasks": task_description,
            "format": user_context.get("format", "PNG screenshot")
        }

        try:
            # Run analysis with page context
            result = self.analyzer.analyze_design(
                design_file=screenshot_path,
                user_context=modified_context,
                page_context=page_context
            )

            return {
                "page": page,
                "page_role": page_role,
                "relevant_tasks": relevant_tasks,
                "analysis": result,
                "success": True
            }

        except Exception as e:
            return {
                "page": page,
                "page_role": page_role,
                "relevant_tasks": relevant_tasks,
                "error": str(e),
                "success": False
            }

    def _build_task_description(self, relevant_tasks: Dict[str, List[str]], page_role: str) -> str:
        """Build a task description that respects page role."""
        lines = []

        if relevant_tasks.get("full"):
            lines.append("PRIMARY tasks for this page type:")
            for task in relevant_tasks["full"]:
                lines.append(f"  - {task}")

        if relevant_tasks.get("partial"):
            lines.append("\nSECONDARY tasks (evaluate pathway, not full completion):")
            for task in relevant_tasks["partial"]:
                lines.append(f"  - {task}")

        if relevant_tasks.get("navigation_only"):
            lines.append("\nNAVIGATION-ONLY (just check if link/path exists):")
            for task in relevant_tasks["navigation_only"]:
                lines.append(f"  - {task}")

        if not lines:
            lines.append(f"General evaluation of {page_role} page usability")

        return "\n".join(lines)

    def _calculate_statistics(self) -> Dict[str, Any]:
        """Calculate aggregate statistics across all pages."""
        total_critical = 0
        total_moderate = 0
        total_minor = 0
        total_positive = 0
        trap_frequency = {}

        for page_result in self.page_analyses:
            if not page_result.get("success"):
                continue

            analysis = page_result.get("analysis", {})
            stats = analysis.get("statistics", {})
            report = analysis.get("report", {})

            total_critical += stats.get("critical_count", 0)
            total_moderate += stats.get("moderate_count", 0)
            total_minor += stats.get("minor_count", 0)
            total_positive += stats.get("positive_count", 0)

            # Count trap frequency
            for issue_list in ["critical_issues", "moderate_issues", "minor_issues"]:
                for issue in report.get(issue_list, []):
                    trap_name = issue.get("trap_name", "Unknown")
                    trap_frequency[trap_name] = trap_frequency.get(trap_name, 0) + 1

        # Sort traps by frequency
        sorted_traps = sorted(trap_frequency.items(), key=lambda x: x[1], reverse=True)

        return {
            "total_issues": total_critical + total_moderate + total_minor,
            "critical_count": total_critical,
            "moderate_count": total_moderate,
            "minor_count": total_minor,
            "positive_count": total_positive,
            "pages_analyzed": len(self.page_analyses),
            "pages_successful": sum(1 for p in self.page_analyses if p.get("success")),
            "trap_frequency": dict(sorted_traps),
            "most_common_traps": sorted_traps[:5]
        }

    def _generate_recommendations(self) -> List[Dict[str, Any]]:
        """Generate prioritized recommendations from all analyses."""
        recommendations = []
        seen = set()

        # Collect all issues with context
        for page_result in self.page_analyses:
            if not page_result.get("success"):
                continue

            page_title = page_result.get("page", {}).get("title", "Unknown")
            report = page_result.get("analysis", {}).get("report", {})

            for severity, issue_list in [
                ("critical", "critical_issues"),
                ("moderate", "moderate_issues"),
                ("minor", "minor_issues")
            ]:
                for issue in report.get(issue_list, []):
                    # Create unique key to avoid duplicates
                    key = f"{issue.get('trap_name')}:{issue.get('recommendation', '')[:50]}"
                    if key in seen:
                        continue
                    seen.add(key)

                    recommendations.append({
                        "severity": severity,
                        "trap_name": issue.get("trap_name"),
                        "recommendation": issue.get("recommendation"),
                        "page": page_title,
                        "location": issue.get("location"),
                        "problem": issue.get("problem")
                    })

        # Sort by severity (critical first, then moderate, then minor)
        severity_order = {"critical": 0, "moderate": 1, "minor": 2}
        recommendations.sort(key=lambda x: severity_order.get(x["severity"], 3))

        return recommendations

    def _generate_site_summary(self, tasks: List[str]) -> Dict[str, Any]:
        """Generate overall site summary."""
        # Check flow completeness
        incomplete_flows = [f for f in self.flow_analyses if not f.get("complete")]

        # Get page role coverage
        roles_found = set(info["role"] for info in self.page_classifications.values())

        # Identify site-wide issues (appear on multiple pages)
        stats = self._calculate_statistics()
        sitewide_issues = [
            {"trap": trap, "count": count}
            for trap, count in stats.get("most_common_traps", [])
            if count > 1
        ]

        # Generate assessment
        if stats["critical_count"] > 0:
            overall_assessment = "Significant usability issues require attention"
        elif stats["moderate_count"] > 3:
            overall_assessment = "Several moderate issues may impact user experience"
        elif incomplete_flows:
            overall_assessment = "Task flows have gaps that may frustrate users"
        else:
            overall_assessment = "Generally good usability with minor improvements possible"

        return {
            "overall_assessment": overall_assessment,
            "total_issues": stats["total_issues"],
            "critical_count": stats["critical_count"],
            "moderate_count": stats["moderate_count"],
            "minor_count": stats["minor_count"],
            "positive_count": stats["positive_count"],
            "page_roles_found": list(roles_found),
            "incomplete_task_flows": [
                {
                    "task": f["task"],
                    "missing": f["missing_page_types"],
                    "assessment": f["assessment"]
                }
                for f in incomplete_flows
            ],
            "sitewide_issues": sitewide_issues,
            "tasks_evaluated": tasks
        }
