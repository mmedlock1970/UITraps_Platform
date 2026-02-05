"""
Intent router for the unified /api/ask endpoint.

Detects whether user input should be routed to:
- ANALYSIS: Trap analysis pipeline (files + context)
- CHAT: RAG chat pipeline (text only)
- HYBRID: Analysis + contextual chat (files + question)
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional


class IntentMode(str, Enum):
    ANALYSIS = "analysis"
    CHAT = "chat"
    HYBRID = "hybrid"


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
) -> IntentResult:
    """
    Route user input to the appropriate pipeline.

    Rules:
    1. Files + context fields filled (users/tasks/format >= 10 chars each) → ANALYSIS
    2. Files + question text only (no context fields)                      → HYBRID
    3. Text only, no files                                                 → CHAT
    4. Files only, no text, no context                                     → ANALYSIS (basic)

    Args:
        message: User's text input.
        files: List of uploaded files.
        users: "Who are the users?" context field.
        tasks: "What are they trying to do?" context field.
        format_desc: "What format is this?" context field.

    Returns:
        IntentResult with mode, message, and detection flags.
    """
    if files is None:
        files = []

    has_files = len(files) > 0
    has_message = bool(message and message.strip())
    has_context = all([
        users and len(users.strip()) >= 10,
        tasks and len(tasks.strip()) >= 10,
        format_desc and len(format_desc.strip()) >= 10,
    ])

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
