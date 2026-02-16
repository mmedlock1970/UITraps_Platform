"""
Report Saver - Automatic Persistence for Analysis Reports

Saves all analysis reports to disk for easy troubleshooting and reference.
Reports are saved as JSON files in backend/reports/ directory.

Copyright © 2009-present UI Traps LLC. All Rights Reserved.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional


class ReportSaver:
    """
    Automatically saves analysis reports to disk.

    Reports are saved to backend/reports/ with timestamp-based filenames.
    Each report includes full analysis results, user context, and metadata.
    """

    def __init__(self, reports_dir: Optional[str] = None):
        """
        Initialize report saver.

        Args:
            reports_dir: Directory to save reports (defaults to backend/reports)
        """
        if reports_dir:
            self.reports_dir = Path(reports_dir)
        else:
            # Default to backend/reports relative to this file
            backend_dir = Path(__file__).parent.parent
            self.reports_dir = backend_dir / "reports"

        # Create directory if it doesn't exist
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def save_report(
        self,
        analysis_result: Dict[str, Any],
        analysis_type: str,
        user_context: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Save an analysis report to disk.

        Args:
            analysis_result: Full analysis result from analyzer
            analysis_type: Type of analysis (single_image, multi_image, figma, url, pdf, video)
            user_context: User context (users, tasks, format, content_type)
            metadata: Additional metadata (file names, URLs, page counts, etc.)

        Returns:
            Path to saved report file
        """
        # Generate filename with timestamp
        timestamp = datetime.now()
        timestamp_str = timestamp.strftime("%Y-%m-%d_%H-%M-%S")

        # Create a short, descriptive filename
        filename = f"report_{timestamp_str}_{analysis_type}.json"
        filepath = self.reports_dir / filename

        # Build report data
        report_data = {
            "timestamp": timestamp.isoformat(),
            "timestamp_readable": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "analysis_type": analysis_type,
            "user_context": user_context or {},
            "metadata": metadata or {},
            "analysis_result": analysis_result,
            "report_file": str(filepath)
        }

        # Save to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

        return str(filepath)

    def list_reports(self, limit: int = 20) -> list[Dict[str, Any]]:
        """
        List recent reports.

        Args:
            limit: Maximum number of reports to return

        Returns:
            List of report summaries (most recent first)
        """
        report_files = sorted(
            self.reports_dir.glob("report_*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )

        summaries = []
        for filepath in report_files[:limit]:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Extract summary info
                summary = {
                    "filename": filepath.name,
                    "filepath": str(filepath),
                    "timestamp": data.get("timestamp_readable", "Unknown"),
                    "analysis_type": data.get("analysis_type", "unknown"),
                    "file_size_kb": filepath.stat().st_size / 1024,
                }

                # Add type-specific info
                metadata = data.get("metadata", {})
                if "file_name" in metadata:
                    summary["file_name"] = metadata["file_name"]
                if "url" in metadata:
                    summary["url"] = metadata["url"]
                if "pages_analyzed" in metadata:
                    summary["pages_analyzed"] = metadata["pages_analyzed"]

                summaries.append(summary)
            except Exception:
                # Skip corrupted files
                continue

        return summaries

    def get_report(self, filename: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific report by filename.

        Args:
            filename: Report filename

        Returns:
            Full report data or None if not found
        """
        filepath = self.reports_dir / filename
        if not filepath.exists():
            return None

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None

    def cleanup_old_reports(self, keep_count: int = 50):
        """
        Delete old reports, keeping only the most recent ones.

        Args:
            keep_count: Number of reports to keep
        """
        report_files = sorted(
            self.reports_dir.glob("report_*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )

        # Delete old reports beyond keep_count
        for filepath in report_files[keep_count:]:
            try:
                filepath.unlink()
            except Exception:
                pass


# Global instance for convenience
_default_saver = None


def get_report_saver() -> ReportSaver:
    """Get or create the default report saver instance."""
    global _default_saver
    if _default_saver is None:
        _default_saver = ReportSaver()
    return _default_saver


def save_analysis_report(
    analysis_result: Dict[str, Any],
    analysis_type: str,
    user_context: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """
    Convenience function to save a report using the default saver.

    Args:
        analysis_result: Full analysis result from analyzer
        analysis_type: Type of analysis
        user_context: User context
        metadata: Additional metadata

    Returns:
        Path to saved report file
    """
    saver = get_report_saver()
    return saver.save_report(analysis_result, analysis_type, user_context, metadata)
