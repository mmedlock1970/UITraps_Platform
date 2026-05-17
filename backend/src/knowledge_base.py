"""
Structured knowledge base for UI Tenets & Traps Pass 2 enrichment.

Loads trap_knowledge_base.md (MCP-formatted chunks) once and provides
fast lookup by trap name for use in the enrichment prompt.
"""
import re
from pathlib import Path
from typing import Optional

_DATA_DIR = Path(__file__).parent.parent / "data"
_KB_PATH = _DATA_DIR / "trap_knowledge_base.md"

# Maps normalized uppercase names from the analyzer to the names used in the
# knowledge base chunk headers/metadata. Only entries that differ are listed.
_CANONICAL_OVERRIDES: dict[str, str] = {
    "INCORRECT INFO": "INCORRECT INFORMATION",
    "UNNECESSARY STEP": "UNNECESSARY STEP(S)",
    "UNNECESSARY STEPS": "UNNECESSARY STEP(S)",
}

_chunks: Optional[dict[str, str]] = None


def _load_chunks() -> dict[str, str]:
    """Parse the knowledge base file into a {UPPERCASE_NAME: chunk_text} dict."""
    global _chunks
    if _chunks is not None:
        return _chunks

    text = _KB_PATH.read_text(encoding="utf-8")

    # Split on the horizontal rule that separates chunks.
    # Each chunk starts with "# CHUNK: TRAP — NAME".
    raw_chunks = re.split(r"\n---\n", text)

    result: dict[str, str] = {}
    for chunk in raw_chunks:
        chunk = chunk.strip()
        if not chunk:
            continue

        # Extract name from "# CHUNK: NAME" header
        match = re.search(r"^#\s+CHUNK:\s+(.+)", chunk, re.MULTILINE)
        if not match:
            continue

        name_raw = match.group(1).strip()
        key = name_raw.upper()
        result[key] = chunk

    _chunks = result
    return _chunks


def _normalize(name: str) -> str:
    """Convert an analyzer trap name to the uppercase key used in the KB."""
    upper = name.upper().strip()
    return _CANONICAL_OVERRIDES.get(upper, upper)


def get_chunks_for_traps(trap_names: list[str]) -> str:
    """
    Return the knowledge base chunks for the given trap names as a single string.

    Args:
        trap_names: List of trap names as used in the analyzer (ALL CAPS OK,
                    e.g. "INVISIBLE ELEMENT", "INCORRECT INFO").

    Returns:
        Concatenated chunk texts separated by horizontal rules, or an empty
        string if none of the requested traps are found.
    """
    chunks = _load_chunks()
    parts: list[str] = []

    for name in trap_names:
        key = _normalize(name)
        chunk = chunks.get(key)
        if chunk:
            parts.append(chunk)
        else:
            # Fallback: try stripping trailing "(S)" variant
            alt = key.rstrip("S").rstrip("(") if key.endswith("(S)") else None
            if alt:
                chunk = chunks.get(alt)
                if chunk:
                    parts.append(chunk)

    if not parts:
        return ""

    return "\n\n---\n\n".join(parts)
