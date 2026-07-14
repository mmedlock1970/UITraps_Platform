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
import base64
import tempfile
import logging
from typing import Optional

from fastmcp import FastMCP

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
