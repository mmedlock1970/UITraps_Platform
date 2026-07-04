"""
Structured knowledge base for UI Tenets & Traps Pass 2 enrichment.

Loads the appropriate KB file once and provides fast lookup by trap name
for use in the enrichment prompt.
"""
import re
from pathlib import Path
from typing import Optional

_DATA_DIR = Path(__file__).parent.parent / "data"

_KB_PATHS = {
    "v1":   _DATA_DIR / "trap_kb_v1.0.md",
    "v1.1": _DATA_DIR / "trap_kb_v1.1.md",
    "v2":   _DATA_DIR / "trap_kb_v2.0.md",
    "v2.1": _DATA_DIR / "trap_kb_v2.1.md",
}

# Maps normalized uppercase analyzer names → names used in KB chunk headers.
# Version-specific overrides: outer key is version, inner is the mapping.
_CANONICAL_OVERRIDES: dict[str, dict[str, str]] = {
    "v2": {
        "INCORRECT INFO": "INCORRECT INFORMATION",
        "UNNECESSARY STEP": "UNNECESSARY STEP(S)",
        "UNNECESSARY STEPS": "UNNECESSARY STEP(S)",
    },
    "v2.1": {
        "INCORRECT INFO": "INCORRECT INFORMATION",
        "UNNECESSARY STEP": "UNNECESSARY STEP(S)",
        "UNNECESSARY STEPS": "UNNECESSARY STEP(S)",
    },
    "v1": {
        "UNNECESSARY STEP": "UNNECESSARY STEP",  # v1 uses plain name without (S)
        "UNNECESSARY STEPS": "UNNECESSARY STEP",
        "POOR AESTHETIC": "UNATTRACTIVE APPEARANCE",  # v2 name → v1 name
    },
}

_caches: dict[str, Optional[dict[str, str]]] = {"v1": None, "v1.1": None, "v2": None, "v2.1": None}


def _load_chunks(version: str) -> dict[str, str]:
    """Parse the KB file for the given version into a {UPPERCASE_NAME: chunk_text} dict."""
    if _caches[version] is not None:
        return _caches[version]

    kb_path = _KB_PATHS[version]
    text = kb_path.read_text(encoding="utf-8")

    raw_chunks = re.split(r"\n---\n", text)

    result: dict[str, str] = {}
    for chunk in raw_chunks:
        chunk = chunk.strip()
        if not chunk:
            continue

        match = re.search(r"^#\s+CHUNK:\s+(.+)", chunk, re.MULTILINE)
        if not match:
            continue

        name_raw = match.group(1).strip()
        key = name_raw.upper()
        result[key] = chunk

    _caches[version] = result
    return result


def _normalize(name: str, version: str) -> str:
    """Convert an analyzer trap name to the uppercase key used in the KB."""
    upper = name.upper().strip()
    overrides = _CANONICAL_OVERRIDES.get(version, {})
    return overrides.get(upper, upper)


def get_chunks_for_traps(trap_names: list[str], version: str = "v2") -> str:
    """
    Return the knowledge base chunks for the given trap names as a single string.

    Args:
        trap_names: List of trap names as used in the analyzer (ALL CAPS OK).
        version: Knowledge base version — "v1" or "v2" (default "v2").

    Returns:
        Concatenated chunk texts separated by horizontal rules, or an empty
        string if none of the requested traps are found.
    """
    if version not in _KB_PATHS:
        version = "v2"

    chunks = _load_chunks(version)
    parts: list[str] = []

    for name in trap_names:
        key = _normalize(name, version)
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
