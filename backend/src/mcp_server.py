"""
UITraps MCP Server

Exposes the UITraps analysis engine as MCP tools for use with Claude Desktop,
Claude Code, Cursor, and any other MCP-compatible AI client.

Authentication: API key via Authorization: Bearer <key> header.
  The key is validated by the middleware in app.py before any tool is called.

Usage tracking: Each tool call charges credits against the API key's monthly quota.
  - analyze_screenshots: 1 credit per image
  - analyze_figma: 1 credit per Figma frame
  - analyze_pdf: 1 credit per PDF page
  - analyze_video: 1 credit per extracted frame
  - ask_about_traps: free (no credits charged)

Copyright © 2009-present UI Traps LLC. All Rights Reserved.
"""

import os
import re
import base64
import tempfile
import logging
from pathlib import Path
from typing import Annotated, Optional

from fastmcp import FastMCP
from pydantic import Field

from .mcp_context import mcp_api_key

logger = logging.getLogger(__name__)

# ── Sync checklist ────────────────────────────────────────────────────────────
# Each MCP tool maps to one analysis endpoint in app.py.
# When app.py gets a new /analyze-* endpoint, add a tool here to match.
#
#   MCP tool               →  app.py endpoint
#   analyze_screenshots    →  /analyze-multi
#   analyze_figma          →  /analyze-figma
#   analyze_pdf            →  /analyze-pdf
#   analyze_video          →  /analyze-video
#   ask_about_traps        →  /api/chat          (free, no credits)
#   get_trap_detection_rules →  (none — parses trap_kb_v2.md directly; no Claude, no credits)
#
# What stays in sync automatically (no action needed):
#   - Bug fixes and prompt changes in the analyzer service classes
#   - New trap definitions in UI_Tenets_Traps.txt
#   - Report format changes in report_generator.py
#   - Quota and usage logic in usage_service.py
# ─────────────────────────────────────────────────────────────────────────────

mcp = FastMCP(
    "UITraps Analyzer",
    instructions=(
        "Analyze UI designs for usability issues using the proprietary UI Tenets & Traps "
        "framework. Always provide 'users' (who uses the interface) and 'tasks' (what "
        "they are trying to accomplish) for the most accurate analysis. All analysis "
        "runs on UITraps servers — no design files are stored. Each analysis type "
        "deducts credits from your monthly quota."
    ),
)


# ── Lazy service factories ────────────────────────────────────────────────────

def _get_multi_analyzer():
    from .analyzer import UITrapsAnalyzer
    from .multi_analyzer import MultiAnalyzer
    return MultiAnalyzer(UITrapsAnalyzer())


def _get_chat_service():
    from .chat.ai_service import ChatAIService
    from .chat.chat_service import ChatService
    ai = ChatAIService(
        anthropic_api_key=os.environ["ANTHROPIC_API_KEY"],
        model=os.environ.get("CHAT_AI_MODEL", "claude-opus-4-8"),
        max_tokens=int(os.environ.get("CHAT_MAX_TOKENS", "1024")),
        temperature=float(os.environ.get("CHAT_TEMPERATURE", "0.7")),
    )
    return ChatService(ai)


# ── Quota helpers ─────────────────────────────────────────────────────────────

def _charge(credits: int) -> tuple[bool, str]:
    """
    Check quota and increment usage for the authenticated API key.
    Returns (ok, error_message). Call before running any analysis.
    """
    from sqlmodel import Session
    from .database import engine
    from .usage_service import get_usage, get_monthly_limit, increment_usage, log_analysis

    api_key = mcp_api_key.get()
    if not api_key:
        return False, "No authenticated API key in context."

    monthly_limit = int(os.environ.get("MONTHLY_LIMIT", "20"))
    with Session(engine) as session:
        limit = get_monthly_limit(session, api_key, monthly_limit)
        current = get_usage(session, api_key)
        if current + credits > limit:
            return False, (
                f"Monthly quota exceeded. You have {limit - current} credit(s) remaining "
                f"but this analysis requires {credits}. Upgrade your plan or wait until "
                "next month."
            )
        increment_usage(session, api_key, credits, limit)
        log_analysis(session, api_key, "/mcp", "mcp_tool", credits, "success")
    return True, ""


# ── Base64 / temp-file helpers ────────────────────────────────────────────────

def _b64_to_temp(b64: str, suffix: str) -> str:
    """Decode base64 string (with or without data-URI prefix) to a temp file."""
    if "," in b64 and b64.startswith("data:"):
        b64 = b64.split(",", 1)[1]
    data = base64.b64decode(b64)
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as f:
        f.write(data)
        return f.name


def _image_suffix(b64: str) -> tuple[str, str]:
    """Return (cleaned_b64, file_suffix) for an image base64 string."""
    if b64.startswith("data:image/png"):
        return b64.split(",", 1)[1], ".png"
    if b64.startswith("data:image/jpeg") or b64.startswith("data:image/jpg"):
        return b64.split(",", 1)[1], ".jpg"
    return b64, ".png"


# ── Tools ─────────────────────────────────────────────────────────────────────

@mcp.tool()
def analyze_screenshots(
    images_base64: list[str],
    users: str,
    tasks: str,
    format: str = "UI screenshot",
    content_type: str = "website",
) -> dict:
    """
    Analyze UI screenshots for usability traps (1–10 images).

    Each image costs 1 credit. Provide base64-encoded PNG or JPEG screenshots.
    Data-URI format ("data:image/png;base64,...") is also accepted.

    Args:
        images_base64: List of base64-encoded screenshots. 1–10 images.
        users: Who uses this interface — be specific.
               Example: "elderly patients reviewing lab results for the first time"
        tasks: What they are trying to accomplish.
               Example: "find their most recent blood-panel results and book a follow-up"
        format: What kind of UI this is.
               Example: "Mobile iOS checkout flow", "Admin dashboard", "Onboarding wizard"
        content_type: One of: website | mobile_app | desktop_app | game | other

    Returns:
        report_markdown, report_html, statistics, frame_count, credits_used
    """
    count = len(images_base64)
    if not 1 <= count <= 10:
        return {"error": "Provide between 1 and 10 images."}

    ok, err = _charge(count)
    if not ok:
        return {"error": err}

    tmp_paths = []
    try:
        for b64 in images_base64:
            cleaned, suffix = _image_suffix(b64)
            tmp_paths.append(_b64_to_temp(cleaned, suffix))

        user_context = {
            "users": users,
            "tasks": tasks,
            "format": format,
            "content_type": content_type,
        }
        result = _get_multi_analyzer().analyze_images(tmp_paths, user_context)

        return {
            "report_markdown": result.get("markdown", ""),
            "report_html": result.get("html", ""),
            "statistics": result.get("statistics", {}),
            "frame_count": result.get("frame_count", count),
            "credits_used": count,
        }

    except Exception as e:
        logger.error("analyze_screenshots error: %s", e)
        return {"error": f"Analysis failed: {e}"}

    finally:
        for p in tmp_paths:
            try:
                os.unlink(p)
            except Exception:
                pass


@mcp.tool()
def analyze_figma(
    figma_url: str,
    users: str,
    tasks: str,
    format: str = "Figma design",
    content_type: str = "website",
    max_frames: int = 10,
) -> dict:
    """
    Analyze a Figma file for UI usability traps.

    Exports frames from Figma and analyzes each screen. Each frame costs 1 credit.
    Prototype flows are analyzed for multi-screen trap detection.
    Requires FIGMA_TOKEN to be configured on the UITraps server.

    Args:
        figma_url: Full Figma file URL.
                   Example: https://www.figma.com/file/abc123/My-App?node-id=0%3A1
        users: Who uses this interface (e.g. "mobile-first shoppers aged 18–35").
        tasks: What they are trying to accomplish.
        format: Format description (default "Figma design").
        content_type: website | mobile_app | desktop_app | game | other
        max_frames: Maximum frames to export and analyze. Range 1–20 (default 10).

    Returns:
        report_html, statistics, site_summary, pages_analyzed, file_name, credits_used
    """
    if not os.environ.get("FIGMA_TOKEN"):
        return {"error": "Figma analysis unavailable — FIGMA_TOKEN not configured on server."}

    max_frames = max(1, min(20, max_frames))

    try:
        from .figma_analyzer import FigmaAnalyzer
        from .site_analyzer import SiteAnalyzer
        from .report_generator import generate_site_report

        with tempfile.TemporaryDirectory() as tmp_dir:
            figma = FigmaAnalyzer()
            figma_result = figma.analyze_figma_file(
                figma_url, tmp_dir, cached_file_data=None, max_frames=max_frames
            )

            frames = figma_result["frames"]
            file_name = figma_result["file_info"]["name"]
            frame_count = len(frames)

            if frame_count == 0:
                return {"error": "No frames could be exported from the Figma file."}

            ok, err = _charge(frame_count)
            if not ok:
                return {"error": err}

            pages = [
                {
                    "url": f"figma://{figma_result['file_info']['key']}/{f['id']}",
                    "title": f["name"],
                    "screenshot_path": f["image_path"],
                }
                for f in frames
                if f.get("image_path")
            ]

            user_context = {
                "users": users,
                "tasks": tasks,
                "format": format,
                "content_type": content_type,
            }
            result = SiteAnalyzer().analyze_site(pages, user_context)
            html = generate_site_report(result, file_name)

            return {
                "report_html": html,
                "statistics": result.get("statistics", {}),
                "site_summary": result.get("site_summary", {}),
                "pages_analyzed": len(pages),
                "file_name": file_name,
                "credits_used": frame_count,
            }

    except Exception as e:
        logger.error("analyze_figma error: %s", e)
        return {"error": f"Figma analysis failed: {e}"}


@mcp.tool()
def analyze_pdf(
    pdf_base64: str,
    users: str,
    tasks: str,
    file_name: str = "document.pdf",
    content_type: str = "pdf_document",
    max_pages: int = 20,
) -> dict:
    """
    Analyze a PDF document for usability traps.

    Converts each PDF page to an image and analyzes it. Each page costs 1 credit.
    Works well for forms, reports, presentations, and document-based interfaces.

    Args:
        pdf_base64: Base64-encoded PDF file content.
                    Data-URI format ("data:application/pdf;base64,...") also accepted.
        users: Who reads or fills out this document (e.g. "job applicants").
        tasks: What they are trying to accomplish (e.g. "complete and submit the form").
        file_name: Original filename for report context (e.g. "intake-form-v3.pdf").
        content_type: Content type (default "pdf_document").
        max_pages: Maximum pages to analyze (1–20, default 20).

    Returns:
        report_html, report_markdown, statistics, pages_analyzed, credits_used
    """
    from .pdf_analyzer import PdfAnalyzer, is_pymupdf_available
    from .report_generator import generate_site_report

    if not is_pymupdf_available():
        return {"error": "PDF analysis unavailable — PyMuPDF not installed on server."}

    max_pages = max(1, min(20, max_pages))
    tmp_path = None
    try:
        tmp_path = _b64_to_temp(pdf_base64, ".pdf")

        pdf_analyzer = PdfAnalyzer()
        pdf_info = pdf_analyzer.get_pdf_info(tmp_path)
        pages_to_analyze = min(pdf_info["page_count"], max_pages)

        ok, err = _charge(pages_to_analyze)
        if not ok:
            return {"error": err}

        user_context = {
            "users": users,
            "tasks": tasks,
            "format": f"PDF document: {file_name}",
            "content_type": content_type,
        }
        result = pdf_analyzer.analyze(tmp_path, user_context, max_pages=max_pages)
        html = generate_site_report(result, file_name)
        actual_pages = result.get("pages_analyzed", pages_to_analyze)

        return {
            "report_html": html,
            "report_markdown": result.get("markdown", ""),
            "statistics": result.get("statistics", {}),
            "pages_analyzed": actual_pages,
            "credits_used": actual_pages,
        }

    except Exception as e:
        logger.error("analyze_pdf error: %s", e)
        return {"error": f"PDF analysis failed: {e}"}

    finally:
        if tmp_path:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass


@mcp.tool()
def analyze_video(
    video_base64: str,
    users: str,
    tasks: str,
    format: str = "Screen recording",
    content_type: str = "website",
    file_extension: str = ".mp4",
    max_frames: int = 15,
) -> dict:
    """
    Analyze a screen recording for UI usability traps.

    Extracts key frames from the video where the UI changes and analyzes each.
    Each extracted frame costs 1 credit. Requires FFmpeg on the server.

    Args:
        video_base64: Base64-encoded video file (MP4, MOV, or WebM).
                      Data-URI format also accepted.
        users: Who uses this interface.
        tasks: What they are trying to accomplish.
        format: Format description (default "Screen recording").
        content_type: website | mobile_app | desktop_app | game | other
        file_extension: Video format — .mp4, .mov, or .webm (include the dot).
        max_frames: Maximum frames to extract and analyze. Range 5–20 (default 15).

    Returns:
        report_markdown, report_html, statistics, frame_count, credits_used
    """
    from .video_processor import is_ffmpeg_available, VideoProcessor

    if not is_ffmpeg_available():
        return {"error": "Video analysis unavailable — FFmpeg not installed on server."}

    max_frames = max(5, min(20, max_frames))
    suffix = file_extension if file_extension.startswith(".") else f".{file_extension}"
    tmp_path = None
    try:
        tmp_path = _b64_to_temp(video_base64, suffix)

        # Estimate frames for quota check before running the full analysis
        estimated = VideoProcessor().estimate_frames(tmp_path)
        frames_to_use = min(estimated, max_frames)

        ok, err = _charge(frames_to_use)
        if not ok:
            return {"error": err}

        user_context = {
            "users": users,
            "tasks": tasks,
            "format": format,
            "content_type": content_type,
        }
        result = _get_multi_analyzer().analyze_video(tmp_path, user_context, max_frames=max_frames)
        actual_frames = result.get("frame_count", frames_to_use)

        return {
            "report_markdown": result.get("markdown", ""),
            "report_html": result.get("html", ""),
            "statistics": result.get("statistics", {}),
            "frame_count": actual_frames,
            "credits_used": actual_frames,
        }

    except Exception as e:
        logger.error("analyze_video error: %s", e)
        return {"error": f"Video analysis failed: {e}"}

    finally:
        if tmp_path:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass


@mcp.tool()
def ask_about_traps(
    question: str,
    conversation_history: Optional[list[dict]] = None,
) -> dict:
    """
    Ask questions about the UI Tenets & Traps framework. Free — no credits charged.

    Use this to:
    - Understand what a specific trap means and how to recognize it
    - Learn which traps to watch for in a given design context
    - Ask follow-up questions after running an analysis
    - Get guidance on how to fix a specific trap in your design

    Args:
        question: Your question about UI traps or usability.
        conversation_history: Optional prior messages for multi-turn conversations.
                              Format: [{"role": "user", "content": "..."}, ...]

    Returns:
        response — a detailed answer grounded in the UI Tenets & Traps knowledge base
    """
    try:
        result = _get_chat_service().handle_chat(question, conversation_history or [])
        return {"response": result["response"]}
    except Exception as e:
        logger.error("ask_about_traps error: %s", e)
        return {"error": f"Chat failed: {e}"}


# ── Trap detection rules (KB-derived; no Claude, no credits) ───────────────────
# get_trap_detection_rules serves the v2 knowledge base as structured data: per-
# Trap definition (one sentence), detection rules, disambiguation, severity,
# confidence, and fix — all drawn straight from the KB, nothing invented — plus a
# general section (severity scale, confidence, the two-pass detect→enrich
# procedure, and the required per-finding output format). It never calls Claude
# and never charges credits.
#
# The no-argument response is PAGINATED (offset / next_offset). Every Trap is
# returned at full verbatim fidelity across pages, each page kept well under any
# single-call size limit — so as the KB grows, all of it stays reachable and
# nothing is ever summarized away or truncated. Pass a trap_name for one Trap.

_KB_CACHE = None
_KB_SOURCE_LABEL = "UI Tenets & Traps Knowledge Base v2.1 (trap_kb_v2.md)"
# Public framework site for per-Trap citations. uitraps.com has no per-Trap pages
# yet, so _kb_trap_link points at the framework site; when per-Trap pages exist,
# switch it to f"{_TRAP_SITE}/traps/{_kb_trap_slug(name)}" (one-line change).
_TRAP_SITE = "https://uitraps.com"
# Cap on the per-page traps payload (chars). Keeps each call comfortably small
# regardless of how large the KB grows; the caller pages via next_offset.
_PAGE_CHAR_BUDGET = 38000

_KB_TENET_RE = re.compile(r'^##\s+TRAP CHUNKS\s+[—–-]\s+(.+?)\s*$')
_KB_TRAP_RE = re.compile(r'^###\s+TRAP:\s+(.+?)\s*$')
_KB_FIELD_RE = re.compile(r'^\*\*([A-Z][^*]+?)\.\*\*\s*(.*)$')


def _kb_v2_path() -> Path:
    """Canonical path to the v2 knowledge base (reuses knowledge_base._KB_PATHS)."""
    try:
        from .knowledge_base import _KB_PATHS
        p = _KB_PATHS.get("v2")
        if p:
            return p
    except Exception:
        pass
    return Path(__file__).parent.parent / "data" / "trap_kb_v2.md"


def _kb_clean_trap_name(raw: str) -> str:
    # Strip a trailing "*(ratified …)*"-style annotation from the header.
    return re.sub(r'\s*\*\(.*?\)\*\s*$', '', raw).strip()


def _kb_clean_field(text_lines: list) -> str:
    out = []
    for ln in text_lines:
        if ln.strip() == "---":  # end-of-chunk separator
            break
        out.append(ln)
    return "\n".join(out).strip()


def _kb_extract_fields(body_lines: list) -> list:
    """Split a Trap chunk's body into (label, lines) fields keyed by their **Label.** header."""
    fields = []
    label = None
    buf = []
    for line in body_lines:
        m = _KB_FIELD_RE.match(line)
        if m:
            if label is not None:
                fields.append((label, buf))
            label = m.group(1).strip()
            buf = [m.group(2)] if m.group(2) else []
        elif label is not None:
            buf.append(line)
    if label is not None:
        fields.append((label, buf))
    return fields


def _kb_pick(fields: list, prefix: str) -> str:
    for label, buf in fields:
        if label.startswith(prefix):
            return _kb_clean_field(buf)
    return ""


def _kb_normalize(s: str) -> str:
    return re.sub(r'[^a-z0-9]', '', (s or "").lower())


def _kb_trap_slug(name: str) -> str:
    return re.sub(r'[^a-z0-9]+', '-', (name or "").lower()).strip('-')


def _kb_trap_link(name: str) -> str:
    # Per-Trap page link. uitraps.com has no per-Trap pages yet, so cite the framework
    # site; switch to f"{_TRAP_SITE}/traps/{_kb_trap_slug(name)}" once those pages exist.
    return _TRAP_SITE


def _kb_trap_source(name: str, tenet: str) -> str:
    """Per-Trap source label: 'UI Tenets & Traps: <Trap> (<Tenet>) — <link>'."""
    return f"UI Tenets & Traps: {name} ({tenet or ''}) — {_kb_trap_link(name)}"


def _kb_first_sentence(text: str) -> str:
    """First sentence of a field — used to summarize the (long) Definition to one line."""
    text = (text or "").strip()
    if not text:
        return ""
    m = re.search(r'(.+?[.!?])(?:\s+[A-Z(]|\s*$)', text, re.S)
    return (m.group(1) if m else text).strip()


def _kb_tidy(s: str) -> str:
    # Drop a trailing markdown rule ("---") left in a section capture.
    return re.sub(r'\s*-{3,}\s*$', '', (s or "")).strip()


def _parse_tenet_glosses(text: str) -> dict:
    """Parse the KB's TENET-GLOSSES block: one line per Tenet, `- less <Tenet>: "<gloss>"`."""
    glosses = {}
    block = re.search(r'<!-- TENET-GLOSSES:START -->(.*?)<!-- TENET-GLOSSES:END -->', text, re.S)
    if block:
        for mm in re.finditer(r'-\s*less\s+(\w+):\s*"([^"]*)"', block.group(1)):
            glosses[mm.group(1).strip().lower()] = mm.group(2).strip()
    return glosses


def _parse_general_section(text: str) -> dict:
    """Extract the KB's cross-cutting rules verbatim, anchored on stable markers
    (not line numbers) so growth in the KB does not break the extraction."""
    def _grab(pattern):
        m = re.search(pattern, text, re.S | re.M)
        return m.group(1).strip() if m else ""

    # Severity scale + how to assign it, and how to express confidence —
    # the whole "## SEVERITY & CONFIDENCE" section, split at the confidence half.
    sc = _grab(r'^##\s+SEVERITY & CONFIDENCE[^\n]*\n(.*?)(?=^##\s)')
    severity_scale, confidence = sc, ""
    idx = sc.find("**Confidence scale**")
    if idx != -1:
        severity_scale, confidence = sc[:idx].strip(), sc[idx:].strip()

    return {
        "severity_scale": _kb_tidy(severity_scale),
        "confidence": _kb_tidy(confidence),
        # Analysis procedure the web analyzer follows: two-pass detect → enrich (G2).
        "analysis_procedure": _grab(r'(\*\*G2\..*?)(?=\n\*\*G3\.)'),
        # Required output format per finding — the "Issues" block of the four-section body.
        "output_format_per_finding": _grab(
            r'(1\.\s+\*\*Issues\.\*\*.*?)(?=\n2\.\s+\*\*Worth a closer look)'
        ),
        "knowledge_base": _KB_SOURCE_LABEL,
    }


def _parse_kb() -> dict:
    text = _kb_v2_path().read_text(encoding="utf-8")
    tenet = None
    traps = []
    cur = None

    def _close():
        nonlocal cur
        if cur is not None:
            traps.append(cur)
            cur = None

    for line in text.split("\n"):
        if line.startswith("## "):
            _close()
            m = _KB_TENET_RE.match(line)
            tenet = m.group(1).strip().title() if m else None
            continue
        tm = _KB_TRAP_RE.match(line)
        if tm:
            _close()
            cur = {"name": _kb_clean_trap_name(tm.group(1)), "tenet": tenet, "body": []}
            continue
        if cur is not None:
            cur["body"].append(line)
    _close()

    rules = []
    for t in traps:
        f = _kb_extract_fields(t["body"])
        rules.append({
            "trap": t["name"],
            "tenet": t["tenet"],
            "source": _kb_trap_source(t["name"], t["tenet"]),
            "definition": _kb_first_sentence(_kb_pick(f, "Definition")),
            "detection_rules": _kb_pick(f, "Detection"),
            "disambiguation": {
                "boundary": _kb_pick(f, "Boundary"),
                "attribution": _kb_pick(f, "Attribution"),
            },
            "severity": _kb_pick(f, "Severity"),
            "confidence": _kb_pick(f, "Assessability"),
            "fix": _kb_pick(f, "Remediation"),
        })
    return {
        "general": _parse_general_section(text),
        "traps": rules,
        "tenet_glosses": _parse_tenet_glosses(text),
    }


def _load_kb() -> dict:
    global _KB_CACHE
    if _KB_CACHE is None:
        _KB_CACHE = _parse_kb()
    return _KB_CACHE


def _kb_trap_size(t: dict) -> int:
    d = t.get("disambiguation", {})
    return sum(len(x) for x in (
        t["trap"], t["tenet"] or "", t.get("source", ""), t["definition"], t["detection_rules"],
        d.get("boundary", ""), d.get("attribution", ""),
        t["severity"], t["confidence"], t["fix"],
    )) + 160  # approx JSON key/structure overhead per Trap


@mcp.tool()
def get_trap_detection_rules(trap_name: Optional[str] = None, offset: int = 0) -> dict:
    """Returns what to look for when checking a screenshot or design for UI Traps, plus the per-Trap source label to cite. Use this, then examine the image yourself and report your findings as a LIST OF TRAPS. For EVERY finding, use exactly this format, in this order, heading first before anything else:
[Trap name] · [Tenet]
Element: …
Rule matched: [quote the detection rule]
Severity: …   Confidence: …
Fix: …
Source: [the per-Trap 'source' label this tool returns for that Trap, including its link]
If a finding involves more than one Trap, lead with the primary Trap in the heading and list the secondary Trap(s) on the Element line. Begin your answer with "Based on UI Tenets & Traps:". Results are paginated: when the response includes a non-null 'next_offset', call again with offset=next_offset until it is null to retrieve every Trap; pass a trap_name to get one Trap's full detail instead."""
    try:
        kb = _load_kb()
    except Exception as e:
        logger.error("get_trap_detection_rules load error: %s", e)
        return {"error": f"Could not load trap knowledge base: {e}"}

    rules = kb["traps"]

    # Single-Trap lookup — full verbatim detail for one Trap.
    if trap_name and trap_name.strip():
        target = _kb_normalize(trap_name)
        exact = [r for r in rules if _kb_normalize(r["trap"]) == target]
        if exact:
            return {"trap": exact[0], "knowledge_base": _KB_SOURCE_LABEL}
        partial = [r for r in rules if target and target in _kb_normalize(r["trap"])]
        if len(partial) == 1:
            return {"trap": partial[0], "knowledge_base": _KB_SOURCE_LABEL}
        if len(partial) > 1:
            return {
                "error": f"'{trap_name}' matches multiple Traps; specify one.",
                "candidates": [r["trap"] for r in partial],
                "knowledge_base": _KB_SOURCE_LABEL,
            }
        return {
            "error": f"No Trap named '{trap_name}'.",
            "available_traps": [r["trap"] for r in rules],
            "knowledge_base": _KB_SOURCE_LABEL,
        }

    # Full dump — paginated so the entire KB is reachable at full fidelity.
    total = len(rules)
    try:
        start = max(0, int(offset))
    except (TypeError, ValueError):
        start = 0

    page = []
    used = 0
    i = start
    while i < total:
        sz = _kb_trap_size(rules[i])
        if page and used + sz > _PAGE_CHAR_BUDGET:
            break
        page.append(rules[i])
        used += sz
        i += 1
    next_offset = i if i < total else None

    resp = {
        "traps": page,
        "total_traps": total,
        "offset": start,
        "returned": len(page),
        "next_offset": next_offset,
        "knowledge_base": _KB_SOURCE_LABEL,
    }
    if next_offset is not None:
        resp["note"] = (
            f"More Traps remain. Call get_trap_detection_rules(offset={next_offset}) and keep "
            "following next_offset until it is null so every Trap is examined."
        )
    # The general section and the full taxonomy ride on the first page only.
    if start == 0:
        resp["general"] = kb["general"]
        resp["taxonomy"] = [{"trap": r["trap"], "tenet": r["tenet"]} for r in rules]
    return resp


# ── Prompt: guided trap analysis ──────────────────────────────────────────────

@mcp.prompt()
def run_trap_analysis(
    users: Annotated[str, Field(description="Who uses the product")],
    goal: Annotated[str, Field(description="What they are trying to do")],
) -> str:
    """Analyze an attached screenshot or design for UI Traps against the UI Tenets & Traps framework."""
    return (
        "You are analyzing a user interface for UI Traps (usability problems) using the "
        "UI Tenets & Traps framework.\n\n"
        f"Users (who uses the product): {users}\n"
        f"Goal (what they are trying to do): {goal}\n\n"
        "Do the following, in order:\n"
        "1. Call the get_trap_detection_rules tool to load what to look for (the detection "
        "rules, severity guidance, fixes, and per-Trap source label for every Trap).\n"
        "2. Examine the attached screenshot or design carefully against those rules, given the "
        "users and goal above.\n"
        "3. Report your findings as a LIST OF TRAPS. For EVERY finding, use exactly this "
        "format, in this order, with the heading first before anything else:\n\n"
        "[Trap name] · [Tenet]\n"
        "Element: <the specific element(s) involved>\n"
        "Rule matched: <quote the detection rule you matched>\n"
        "Severity: <High/Medium/Low>   Confidence: <High/Medium/Low>\n"
        "Fix: <how to fix it>\n"
        "Source: <the per-Trap 'source' label the tool returned for this Trap, including its link>\n\n"
        "If a finding involves more than one Trap, lead with the primary Trap in the heading "
        "and list the secondary Trap(s) on the Element line.\n\n"
        'Begin your answer with exactly: "Based on UI Tenets & Traps:"'
    )


# ── Resource: the 8 Tenets ────────────────────────────────────────────────────

@mcp.resource(
    "uitraps://tenets",
    name="The 8 Tenets",
    description="The eight UI Tenets with their one-line glosses from the knowledge base.",
    mime_type="text/markdown",
)
def tenets_resource() -> str:
    """List the 8 UI Tenets with the KB's one-line gloss for each."""
    kb = _load_kb()
    glosses = kb["tenet_glosses"]
    ordered = []
    for r in kb["traps"]:
        if r["tenet"] and r["tenet"] not in ordered:
            ordered.append(r["tenet"])
    lines = [
        "# The 8 UI Tenets",
        "",
        "One-line glosses from the UI Tenets & Traps knowledge base — each says what the "
        "interface is like when that Tenet is not met:",
        "",
    ]
    for tenet in ordered:
        g = glosses.get(tenet.lower(), "")
        lines.append(f'- **{tenet}** — when it is missing: "{g}"' if g else f"- **{tenet}**")
    lines += ["", f"Source: {_KB_SOURCE_LABEL}"]
    return "\n".join(lines)
