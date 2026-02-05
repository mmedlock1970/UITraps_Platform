"""
Pinecone vector search service for RAG pipeline.

Port of: Traps Chat/backend-api/src/services/pinecone.js
Embeds user queries via OpenAI and queries Pinecone for relevant content chunks.
"""

import logging
from openai import OpenAI
from pinecone import Pinecone

logger = logging.getLogger(__name__)


class PineconeService:
    """Handles embedding generation and Pinecone vector search."""

    def __init__(
        self,
        pinecone_api_key: str,
        index_name: str,
        openai_api_key: str,
        embedding_model: str = "text-embedding-3-small",
        top_k: int = 10,
        similarity_threshold: float = 0.4,
    ):
        self._pc = Pinecone(api_key=pinecone_api_key)
        self._index = self._pc.Index(index_name)
        self._openai = OpenAI(api_key=openai_api_key)
        self._embedding_model = embedding_model
        self._top_k = top_k
        self._similarity_threshold = similarity_threshold

    def generate_embedding(self, text: str) -> list[float]:
        """
        Generate embedding vector for a text query.

        Port of: pinecone.js generateEmbedding() (lines 30-41)
        Uses OpenAI text-embedding-3-small (1536 dimensions).
        """
        response = self._openai.embeddings.create(
            model=self._embedding_model,
            input=text,
        )
        return response.data[0].embedding

    def get_relevant_content(self, query: str) -> list[dict]:
        """
        Search Pinecone for content chunks relevant to the user query.

        Port of: pinecone.js getRelevantContent() (lines 50-81)
        - Generates embedding for the query
        - Queries Pinecone with topK and includeMetadata
        - Filters results by similarity threshold (0.7)

        Returns:
            List of dicts with: content, title, url, score, postId
        """
        # Step 1: Generate embedding for the query
        query_embedding = self.generate_embedding(query)

        # Step 2: Query Pinecone
        query_response = self._index.query(
            vector=query_embedding,
            top_k=self._top_k,
            include_metadata=True,
        )

        # Step 3: Filter by similarity threshold and format results
        results = [
            {
                "content": match.metadata.get("text", ""),
                "title": match.metadata.get("title", ""),
                "url": match.metadata.get("url", ""),
                "score": match.score,
                "postId": match.metadata.get("postId"),
            }
            for match in query_response.matches
            if match.score > self._similarity_threshold
        ]

        logger.info(
            "Found %d relevant chunks for query: \"%s...\"",
            len(results),
            query[:50],
        )

        return results
