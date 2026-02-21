"""
Chat service orchestrator.

Uses full context injection by default (recommended for small knowledge bases).
RAG mode via Pinecone is available as an optional fallback but not recommended.

Port of: Traps Chat/backend-api/src/routes/chat.js (handleChatRequest logic)
"""

import logging

from .ai_service import ChatAIService
from .system_prompt import build_full_context_system_prompt

logger = logging.getLogger(__name__)


class ChatService:
    """
    Orchestrates chat responses using full context injection.

    The complete UI Tenets & Traps knowledge base is injected into the system
    prompt, giving Claude complete context without retrieval gaps.
    """

    def __init__(self, ai_service: ChatAIService):
        """
        Initialize the chat service.

        Args:
            ai_service: The AI service for generating responses.
        """
        self._ai = ai_service
        # Pre-build the system prompt (cached after first call)
        self._system_prompt = build_full_context_system_prompt()
        logger.info("ChatService initialized with full context injection")

    def handle_chat(
        self,
        message: str,
        conversation_history: list[dict] | None = None,
    ) -> dict:
        """
        Handle a chat message using full context injection.

        Args:
            message: The user's question (already validated by caller).
            conversation_history: Previous messages for context.

        Returns:
            Dict with: response, sources, usage, mode
        """
        # Generate AI response with full knowledge base context
        result = self._ai.generate_response(
            message, self._system_prompt, conversation_history
        )

        return {
            "response": result["text"],
            "sources": result["sources"],
            "usage": result["usage"],
            "mode": "chat",
        }
