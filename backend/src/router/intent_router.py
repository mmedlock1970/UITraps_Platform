"""
Intent router for the unified /api/ask endpoint.

Detects whether user input should be routed to:
- ANALYSIS: Trap analysis pipeline (files + context)
- CHAT: RAG chat pipeline (text only)
- HYBRID: Analysis + contextual chat (files + question)
- URL_ANALYSIS: Website crawl + analysis pipeline (URL + context)
"""

import re
from enum import Enum
from dataclasses import dataclass
from typing import Optional


class IntentMode(str, Enum):
    ANALYSIS = "analysis"
    CHAT = "chat"
    HYBRID = "hybrid"
    URL_ANALYSIS = "url_analysis"


_URL_RE = re.compile(r'^https?://', re.IGNORECASE)


@dataclass
class IntentResult:
    mode: IntentMode
    message: Optional[str]
    has_files: bool
    has_context: bool


def detect_intent(
    message: Optional[str] = None,
    files: list | None = None,
    users: Optional[str] = None,
    tasks: Optional[str] = None,
    format_desc: Optional[str] = None,
    figma_url: Optional[str] = None,
    input_type: Optional[str] = None,
) -> IntentResult:
    """
    Route user input to the appropriate pipeline.

    Rules:
    1. Files + context fields filled (users/tasks/format >= 2 chars each) → ANALYSIS
    2. Files + question text only (no context fields)                      → HYBRID
    3. Text only, no files                                                 → CHAT
    4. Files only, no text, no context                                     → ANALYSIS (basic)
    5. Figma URL + input_type=flow_diagram + context                       → ANALYSIS

    Args:
        message: User's text input.
        files: List of uploaded files.
        users: "Who are the users?" context field.
        tasks: "What are they trying to do?" context field.
        format_desc: "What format is this?" context field.
        figma_url: Figma file URL (treated as input when input_type=flow_diagram).
        input_type: Input type hint from the frontend.

    Returns:
        IntentResult with mode, message, and detection flags.
    """
    if files is None:
        files = []

    has_figma_flow = bool(figma_url and figma_url.strip() and input_type == 'flow_diagram')
    has_files = len(files) > 0 or has_figma_flow
    has_message = bool(message and message.strip())
    has_context = all([
        users and len(users.strip()) >= 2,
        tasks and len(tasks.strip()) >= 2,
        format_desc and len(format_desc.strip()) >= 2,
    ])
    is_url = bool(message and _URL_RE.match(message.strip()))

    # URL with no files → website crawl analysis
    if is_url and not has_files:
        return IntentResult(
            mode=IntentMode.URL_ANALYSIS,
            message=message.strip(),
            has_files=False,
            has_context=has_context,
        )

    if has_files and has_context:
        # Standard trap analysis with full context
        return IntentResult(
            mode=IntentMode.ANALYSIS,
            message=message,
            has_files=True,
            has_context=True,
        )

    if has_files and has_message and not has_context:
        # Files + question but no structured context → hybrid
        return IntentResult(
            mode=IntentMode.HYBRID,
            message=message,
            has_files=True,
            has_context=False,
        )

    if has_files and not has_message and not has_context:
        # Files only, no context → basic analysis (will need context prompted)
        return IntentResult(
            mode=IntentMode.ANALYSIS,
            message=None,
            has_files=True,
            has_context=False,
        )

    # Text only → RAG chat
    return IntentResult(
        mode=IntentMode.CHAT,
        message=message,
        has_files=False,
        has_context=False,
    )
