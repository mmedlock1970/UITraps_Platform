"""
UI Traps Analyzer - AI-powered UI evaluation using the UI Tenets & Traps framework

Copyright © 2009-present UI Traps LLC. All Rights Reserved.
PROPRIETARY & CONFIDENTIAL - UI Tenets & Traps Framework

Main exports:
    - UITrapsAnalyzer: Main analyzer class
    - analyze_design: Convenience function for quick analysis
    - SiteAnalyzer: Multi-page site analysis with context awareness
    - classify_page: Page type detection and task mapping
"""

from .analyzer import UITrapsAnalyzer, analyze_design
from .validators import validate_file_format, validate_context
from .formatters import format_report_as_markdown, format_report_as_html, get_report_statistics
from .schema import get_ui_analysis_schema
from .page_classifier import classify_page, get_relevant_tasks, generate_flow_analysis, classify_all_pages
from .site_analyzer import SiteAnalyzer
from .report_generator import generate_site_report_markdown, generate_site_report_html

__version__ = "2.0.0"  # Updated for context-aware site analysis
__all__ = [
    # Core analyzer
    "UITrapsAnalyzer",
    "analyze_design",
    # Validators
    "validate_file_format",
    "validate_context",
    # Page-level formatters
    "format_report_as_markdown",
    "format_report_as_html",
    "get_report_statistics",
    # Schema
    "get_ui_analysis_schema",
    # Site-level analysis (new in v2.0)
    "classify_page",
    "classify_all_pages",
    "get_relevant_tasks",
    "generate_flow_analysis",
    "SiteAnalyzer",
    "generate_site_report_markdown",
    "generate_site_report_html"
]
