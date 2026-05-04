"""
Knowledge Base Extractor for Two-Pass Analysis

Copyright © 2009-present UI Traps LLC. All Rights Reserved.
PROPRIETARY & CONFIDENTIAL - UI Tenets & Traps Framework

Manages loading and extraction from two knowledge sources:
- UI_Traps_Analysis_Reference.md  →  Pass 1 (detection, condensed, AI-optimized)
- UI_Tenets_Traps.txt             →  Pass 2 (enrichment, full book content)
"""
import re
from pathlib import Path
from typing import Dict, List

# Paths relative to this file
_DATA_DIR = Path(__file__).parent.parent / "data"
ANALYSIS_REFERENCE_PATH = _DATA_DIR / "UI_Traps_Analysis_Reference.md"
FULL_BOOK_PATH = _DATA_DIR / "UI_Tenets_Traps.txt"

# Max characters to extract per trap section (avoids token bloat for verbose traps)
MAX_SECTION_CHARS = 6000

# All 27 valid trap names — used to find section boundaries in the book
TRAP_NAMES = [
    "INVISIBLE ELEMENT",
    "EFFECTIVELY INVISIBLE ELEMENT",
    "DISTRACTION",
    "UNCOMPREHENDED ELEMENT",
    "INVITING DEAD END",
    "POOR GROUPING",
    "FORCED SYNTAX",
    "MEMORY CHALLENGE",
    "FEEDBACK FAILURE",
    "PHYSICAL CHALLENGE",
    "ACCIDENTAL ACTIVATION",
    "SLOW OR NO RESPONSE",
    "CAPTIVE WAIT",
    "UNNECESSARY STEP",
    "INFORMATION OVERLOAD",
    "SYSTEM AMNESIA",
    "BAD PREDICTION",
    "INCORRECT INFO",
    "IRREVERSIBLE ACTION",
    "UNWANTED DISCLOSURE",
    "DATA LOSS",
    "GRATUITOUS REDUNDANCY",
    "VARIABLE OUTCOME",
    "WANDERING ELEMENT",
    "INCONSISTENT APPEARANCE",
    "AMBIGUOUS HOME",
    "POOR AESTHETIC",
]

# Module-level caches — loaded once per process
_analysis_reference_cache: str | None = None
_full_book_cache: str | None = None


def load_analysis_reference() -> str:
    """
    Load the condensed AI analysis reference (Pass 1 knowledge base).
    Cached after first load.
    """
    global _analysis_reference_cache
    if _analysis_reference_cache is None:
        if not ANALYSIS_REFERENCE_PATH.exists():
            raise FileNotFoundError(
                f"Analysis reference not found at {ANALYSIS_REFERENCE_PATH}. "
                f"Ensure UI_Traps_Analysis_Reference.md is in the data/ directory."
            )
        _analysis_reference_cache = ANALYSIS_REFERENCE_PATH.read_text(encoding="utf-8")
    return _analysis_reference_cache


def load_full_book() -> str:
    """
    Load the full book manuscript (Pass 2 knowledge base).
    Cached after first load.
    """
    global _full_book_cache
    if _full_book_cache is None:
        if not FULL_BOOK_PATH.exists():
            raise FileNotFoundError(
                f"Full book not found at {FULL_BOOK_PATH}. "
                f"Ensure UI_Tenets_Traps.txt is in the data/ directory."
            )
        _full_book_cache = FULL_BOOK_PATH.read_text(encoding="utf-8")
    return _full_book_cache


def extract_trap_sections(trap_names: List[str]) -> Dict[str, str]:
    """
    Extract the book sections for a list of trap names.

    For each trap name, finds its section in the full book and returns
    the text from that section header until the next trap section begins.

    Args:
        trap_names: List of trap names to extract (e.g. ["INVISIBLE ELEMENT", "POOR GROUPING"])

    Returns:
        Dict mapping trap_name -> extracted book section text.
        Traps not found in the book are omitted from the result.
    """
    book_text = load_full_book()
    sections = {}

    for trap_name in trap_names:
        section = _extract_single_section(trap_name, book_text)
        if section:
            sections[trap_name] = section

    return sections


def _extract_single_section(trap_name: str, book_text: str) -> str:
    """
    Extract a single trap's section from the book text.

    The book structure uses:
        TRAPS
        TRAP_NAME
        <content...>

    Trap names appear multiple times (table of contents, inline references,
    and the actual chapter). We identify the chapter occurrence by finding the
    trap name preceded by "TRAPS" within ~60 characters, then capture content
    until the next chapter-level trap name appears.
    """
    escaped = re.escape(trap_name)
    standalone = re.compile(rf'(?im)^[ \t]*{escaped}[ \t]*$')
    all_matches = list(standalone.finditer(book_text))

    if not all_matches:
        return ""

    # Find the chapter occurrence: preceded by "TRAPS" within ~60 chars
    chapter_match = None
    for m in all_matches:
        preceding = book_text[max(0, m.start() - 60):m.start()]
        if re.search(r'TRAPS\s*$', preceding, re.IGNORECASE):
            chapter_match = m
            break

    # Fall back to the last occurrence if the chapter pattern isn't found
    if chapter_match is None:
        chapter_match = all_matches[-1]

    section_start = chapter_match.start()
    search_from = chapter_match.end()
    earliest_end = len(book_text)

    # Find the end: next chapter-level trap name (preceded by TRAPS, or 500+ chars away)
    for other_trap in TRAP_NAMES:
        if other_trap == trap_name:
            continue
        other_escaped = re.escape(other_trap)
        other_standalone = re.compile(rf'(?im)^[ \t]*{other_escaped}[ \t]*$')
        for om in other_standalone.finditer(book_text, search_from):
            preceding = book_text[max(0, om.start() - 60):om.start()]
            if re.search(r'TRAPS\s*$', preceding, re.IGNORECASE) or \
               (om.start() - section_start) > 500:
                if om.start() < earliest_end:
                    earliest_end = om.start()
                break

    section_text = book_text[section_start:earliest_end].strip()

    # Truncate if the section is very long to keep tokens manageable
    if len(section_text) > MAX_SECTION_CHARS:
        section_text = section_text[:MAX_SECTION_CHARS] + "\n[...section truncated for brevity...]"

    return section_text


def collect_found_trap_names(report: dict) -> List[str]:
    """
    Extract all unique trap names from a Pass 1 report.

    Collects from critical_issues, moderate_issues, minor_issues, and potential_issues.

    Args:
        report: Pass 1 structured report dict

    Returns:
        Deduplicated list of trap names found in the report
    """
    found = set()
    for severity in ("critical_issues", "moderate_issues", "minor_issues", "potential_issues"):
        for issue in report.get(severity, []):
            trap_name = issue.get("trap_name")
            if trap_name:
                found.add(trap_name)
    return list(found)
