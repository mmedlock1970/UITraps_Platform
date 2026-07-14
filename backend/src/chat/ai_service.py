"""
AI response generation service for RAG chat.

Port of: Traps Chat/backend-api/src/services/ai.js
Uses Anthropic Claude to generate responses grounded in retrieved context.
"""

import re
import logging
from anthropic import Anthropic

logger = logging.getLogger(__name__)


def _rejects_sampling_params(model: str) -> bool:
    """Opus 4.7/4.8, Sonnet 5, and Fable 5 reject temperature/top_p/top_k with a 400."""
    m = (model or "").lower()
    return any(tag in m for tag in ("opus-4-8", "opus-4-7", "sonnet-5", "fable-5"))


class ChatAIService:
    """Generates AI responses using Claude with RAG context."""

    def __init__(
        self,
        anthropic_api_key: str,
        model: str = "claude-opus-4-8",
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ):
        # max_retries=5 enables automatic exponential backoff on 429 rate limit errors.
        # The full knowledge base system prompt is large (~tokens), so TPM limits can be hit
        # on rapid follow-up messages. 5 retries gives ~31 seconds of total backoff time.
        self._client = Anthropic(api_key=anthropic_api_key, max_retries=5)
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

        # Opus 4.7/4.8, Sonnet 5, and Fable 5 reject sampling params (temperature → 400); only send
        # temperature to models that accept it (e.g. Haiku), so this service stays correct whichever
        # model CHAT_AI_MODEL selects.
        create_kwargs = {
            "model": self._model,
            "max_tokens": self._max_tokens,
            "system": system_prompt,
            "messages": messages,
        }
        if self._temperature is not None and not _rejects_sampling_params(self._model):
            create_kwargs["temperature"] = self._temperature

        response = self._client.messages.create(**create_kwargs)

        # Robust to a leading thinking block (a thinking-on model would put it at content[0]).
        text = next((b.text for b in response.content if getattr(b, "type", None) == "text"), "")
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
