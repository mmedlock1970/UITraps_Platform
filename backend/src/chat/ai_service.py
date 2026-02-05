"""
AI response generation service for RAG chat.

Port of: Traps Chat/backend-api/src/services/ai.js
Uses Anthropic Claude to generate responses grounded in retrieved context.
"""

import re
import logging
from anthropic import Anthropic

logger = logging.getLogger(__name__)


class ChatAIService:
    """Generates AI responses using Claude with RAG context."""

    def __init__(
        self,
        anthropic_api_key: str,
        model: str = "claude-sonnet-4-5-20250929",
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ):
        self._client = Anthropic(api_key=anthropic_api_key)
        self._model = model
        self._max_tokens = max_tokens
        self._temperature = temperature

    def generate_response(
        self,
        user_message: str,
        system_prompt: str,
        conversation_history: list[dict] | None = None,
    ) -> dict:
        """
        Generate a Claude response with RAG system prompt and conversation history.

        Port of: ai.js generateAnthropicResponse() (lines 36-69)

        Args:
            user_message: The user's current question.
            system_prompt: System prompt with RAG context injected.
            conversation_history: Previous messages [{role, content}, ...].

        Returns:
            Dict with: text, sources (list of URLs), usage (dict with input/output tokens)
        """
        messages = []
        if conversation_history:
            messages.extend(
                {"role": msg["role"], "content": msg["content"]}
                for msg in conversation_history
            )
        messages.append({"role": "user", "content": user_message})

        response = self._client.messages.create(
            model=self._model,
            max_tokens=self._max_tokens,
            temperature=self._temperature,
            system=system_prompt,
            messages=messages,
        )

        text = response.content[0].text
        return {
            "text": text,
            "sources": self._extract_sources(text),
            "usage": {
                "inputTokens": response.usage.input_tokens,
                "outputTokens": response.usage.output_tokens,
            },
        }

    @staticmethod
    def _extract_sources(text: str) -> list[str]:
        """
        Extract source URLs mentioned in the AI response.

        Port of: ai.js extractSourcesFromResponse() (lines 108-112)
        """
        urls = re.findall(r"https?://[^\s)]+", text)
        return list(set(urls))
