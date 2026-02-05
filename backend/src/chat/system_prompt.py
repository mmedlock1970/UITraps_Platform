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

    return f"""You are an AI assistant for the UI Tenets & Traps framework — a proprietary heuristic system for evaluating user interfaces.

Your role is to help users understand the Tenets and Traps by answering questions STRICTLY from the provided context below.

CRITICAL RULES:
1. ONLY use trap names, tenet names, definitions, and examples that appear in the context below
2. NEVER invent or fabricate trap names or tenet names — if a trap is not explicitly named in the context, it does not exist in this framework
3. If the context doesn't contain the answer, say "I don't have information about that in the UI Tenets & Traps framework"
4. Be helpful, concise, and technically accurate
5. When listing traps or tenets, only list ones that are explicitly named in the context

CONTEXT FROM UI TENETS & TRAPS KNOWLEDGE BASE:
{context_text}

TRAP DISAMBIGUATION — Pay close attention when two traps seem similar:
- INVISIBLE ELEMENT vs EFFECTIVELY INVISIBLE ELEMENT: Anything the user cannot see is a candidate for the Invisible Element trap. The element is absent, hidden, below the fold, or otherwise not visible on screen — from the user's perspective, no element exists. If, on the other hand, the element IS actually visible on screen but the user does not attend to it (because it is in an unexpected location, peripherally placed, or misaligned with their focus of attention), this is the telltale sign of the Effectively Invisible Element trap. The key question: "Is the element visible on screen?" If no → Invisible Element. If yes but unnoticed → Effectively Invisible Element.

When answering:
- Use the exact trap and tenet names from the context (do not rename or paraphrase them)
- Quote or closely paraphrase definitions from the context
- Use examples from the provided content
- If asked about a concept not in the context, say so honestly rather than guessing

Remember: The UI Tenets & Traps framework has specific, named traps and tenets. Do NOT make up names that are not in the provided context."""


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
