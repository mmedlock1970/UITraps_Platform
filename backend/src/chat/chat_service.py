"""
Chat service orchestrator for the RAG pipeline.

Combines Pinecone retrieval, system prompt building, and AI response generation
into a single handle_chat() method. Falls back to direct Claude conversation
when RAG retrieval fails (e.g., OpenAI quota exceeded).

Port of: Traps Chat/backend-api/src/routes/chat.js (handleChatRequest logic)
"""

import logging

from .pinecone_service import PineconeService
from .ai_service import ChatAIService
from .system_prompt import build_chat_system_prompt

logger = logging.getLogger(__name__)

FALLBACK_SYSTEM_PROMPT = (
    "You are the UITraps AI assistant, an expert in UI/UX design, dark patterns, "
    "deceptive design, and ethical interface practices. You help users understand "
    "UI traps — manipulative design patterns that trick users into unintended actions.\n\n"
    "You are knowledgeable about the 27 UI Traps framework and the 9 Tenets of "
    "user-respecting design. Answer questions clearly and helpfully.\n\n"
    "Note: The content knowledge base is currently unavailable, so you are answering "
    "from your general knowledge. Your responses may not include specific UITraps "
    "articles or sources."
)


class ChatService:
    """Orchestrates the full RAG chat pipeline: embed → retrieve → generate."""

    def __init__(self, pinecone_service: PineconeService, ai_service: ChatAIService):
        self._pinecone = pinecone_service
        self._ai = ai_service

    def handle_chat(
        self,
        message: str,
        conversation_history: list[dict] | None = None,
    ) -> dict:
        """
        Full RAG pipeline for a single chat message.

        Port of: chat.js handleChatRequest() (lines 36-58)

        Args:
            message: The user's question (already validated by caller).
            conversation_history: Previous messages for context.

        Returns:
            Dict with: response, sources, usage, mode
        """
        # Step 1: Try to get relevant content from vector database
        relevant_content = []
        try:
            relevant_content = self._pinecone.get_relevant_content(message)
        except Exception as e:
            logger.warning(f"RAG retrieval failed, falling back to direct chat: {e}")

        # Step 2: Build system prompt (with or without RAG context)
        if relevant_content:
            system_prompt = build_chat_system_prompt(relevant_content)
        else:
            system_prompt = FALLBACK_SYSTEM_PROMPT

        # Step 3: Generate AI response
        result = self._ai.generate_response(
            message, system_prompt, conversation_history
        )

        return {
            "response": result["text"],
            "sources": result["sources"],
            "usage": result["usage"],
            "mode": "chat",
        }
