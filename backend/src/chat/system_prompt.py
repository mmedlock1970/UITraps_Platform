"""
System prompt builder for RAG chat responses.

Port of: Traps Chat/backend-api/src/prompts/system.js
Exact same prompt text and context formatting as the Node.js version.
"""


def build_chat_system_prompt(relevant_content: list[dict]) -> str:
    """
    Build the system prompt with retrieved RAG context injected.

    Port of: system.js buildSystemPrompt() (lines 4-29)

    Args:
        relevant_content: List of content chunks from Pinecone search.
            Each dict has: content, title, url, score, postId

    Returns:
        Complete system prompt string with context embedded.
    """
    context_text = format_context_for_ai(relevant_content)

    return f"""You are an AI assistant for UITraps.com, a WordPress resource site focused on UI design patterns, traps, and best practices.

Your role is to help paid subscribers by answering questions about the content in the UITraps library.

CRITICAL RULES:
1. ONLY answer questions using the provided context below
2. If the context doesn't contain relevant information, say so clearly
3. Never make up information or browse external websites
4. Always cite which article or page your answer comes from
5. Be helpful, concise, and technically accurate
6. If asked about something not in the context, suggest related topics that ARE covered

CONTEXT FROM UITRAPS LIBRARY:
{context_text}

When answering:
- Reference specific articles by title when possible
- Use examples from the provided content
- If multiple articles discuss the topic, synthesize their perspectives
- Keep answers focused and practical
- Include relevant URLs when referencing specific content

Remember: You can ONLY discuss what's in the provided context. If a question can't be answered from the context, be honest about it."""


def format_context_for_ai(relevant_content: list[dict]) -> str:
    """
    Format retrieved content chunks for inclusion in the system prompt.

    Port of: system.js formatContextForAI() (lines 35-53)
    Formats each chunk as [Source N: Title] with URL and relevance percentage.

    Args:
        relevant_content: List of content chunk dicts from Pinecone.

    Returns:
        Formatted context string.
    """
    if not relevant_content:
        return "No relevant content found."

    chunks = []
    for i, chunk in enumerate(relevant_content, 1):
        chunks.append(
            f"\n[Source {i}: {chunk['title']}]\n"
            f"URL: {chunk['url']}\n"
            f"Relevance: {chunk['score'] * 100:.1f}%\n\n"
            f"{chunk['content']}\n\n"
            f"---\n"
        )

    return "\n".join(chunks)
