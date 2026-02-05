"""
Chat service orchestrator for the RAG pipeline.

Combines Pinecone retrieval, system prompt building, and AI response generation
into a single handle_chat() method.

Port of: Traps Chat/backend-api/src/routes/chat.js (handleChatRequest logic)
"""

import logging

from .pinecone_service import PineconeService
from .ai_service import ChatAIService
from .system_prompt import build_chat_system_prompt

logger = logging.getLogger(__name__)

NO_RESULTS_MESSAGE = (
    "I couldn't find any relevant information in the UITraps content library "
    "to answer your question. Could you rephrase or ask about a different topic?"
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
        # Step 1: Get relevant content from vector database
        relevant_content = self._pinecone.get_relevant_content(message)

        if not relevant_content:
            return {
                "response": NO_RESULTS_MESSAGE,
                "sources": [],
                "usage": None,
                "mode": "chat",
            }

        # Step 2: Build system prompt with retrieved context
        system_prompt = build_chat_system_prompt(relevant_content)

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
