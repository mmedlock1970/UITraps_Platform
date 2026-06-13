"""
UITraps Unified Platform - Web API

Combines UI Traps analysis (image/video) and RAG chat into a single API.
Existing endpoints (/analyze, /analyze-multi, /analyze-video) unchanged.
New endpoints (/api/chat, /api/ask) use JWT auth for the unified experience.

Copyright © 2009-present UI Traps LLC. All Rights Reserved.
"""

import os
import json
import asyncio
import concurrent.futures
import logging
import tempfile
import time
import traceback
from datetime import datetime
from typing import Optional, List
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()  # Load .env file before other imports

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Import the existing analyzer
from src.analyzer import UITrapsAnalyzer
from src.multi_analyzer import MultiAnalyzer
from src.estimator import (
    estimate_single_image,
    estimate_multi_image,
    estimate_video,
    detect_input_type,
    EstimationConstants
)
from src.video_processor import is_ffmpeg_available, VideoProcessor

# Figma, Web Crawler, Site Analyzer, and PDF Analyzer
from src.figma_analyzer import FigmaAnalyzer
from src.formatters import format_report_as_html, get_report_statistics
from src.web_crawler import WebCrawler
from src.site_analyzer import SiteAnalyzer
from src.pdf_analyzer import PdfAnalyzer, is_pymupdf_available

# Database persistence for usage tracking
from sqlmodel import Session, select
from src.database import init_db, engine
from src.usage_service import (
    get_usage,
    increment_usage,
    get_monthly_limit,
    verify_api_key_db,
    log_analysis,
    get_current_month
)

# Report saver for automatic report persistence
from src.report_saver import save_analysis_report, get_report_saver
from src.database import AnalysisReport

# Subscription and token management
from src.subscription_service import (
    activate_subscription,
    renew_subscription,
    cancel_subscription,
    expire_subscription,
    add_bonus_tokens,
    check_and_consume_token,
    get_usage_summary,
)

# NEW: JWT auth for unified platform
from src.auth import get_current_user

# NEW: Full-context chat pipeline (no RAG - knowledge base injected directly)
from src.chat.ai_service import ChatAIService
from src.chat.chat_service import ChatService

# NEW: Intent router for unified endpoint
from src.router import detect_intent, IntentMode

# MCP server — exposes analysis tools for Claude Desktop, Claude Code, Cursor, etc.
from src.mcp_server import mcp
from src.mcp_context import mcp_api_key

logger = logging.getLogger(__name__)

# File-based error log so we can capture crashes regardless of terminal
_LOG_FILE = os.path.join(os.path.dirname(__file__), 'uitraps_error.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(_LOG_FILE, encoding='utf-8'),
    ]
)

# --- Configuration ---

# Explicit origins for CORS (localhost for dev; uitraps.com domains covered by regex below)
ALLOWED_ORIGINS = os.environ.get(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:5173,http://127.0.0.1:5173"
).split(",")

# Allows uitraps.com and any subdomain (e.g. adrian.uitraps.com, shed.uitraps.com)
ALLOWED_ORIGIN_REGEX = r"https://([\w-]+\.)?uitraps\.com"

# Monthly analysis limit per API key
MONTHLY_LIMIT = int(os.environ.get("MONTHLY_LIMIT", "20"))

# Shared secret for WooCommerce webhook calls (set same value in WordPress and Railway env vars)
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "")

# Simple in-memory cache for Figma file data (avoids hitting API twice for estimate + analyze)
# Key: file_key, Value: {"data": file_data, "timestamp": time.time()}
_figma_cache = {}
FIGMA_CACHE_TTL = 300  # 5 minutes

def get_cached_figma_data(file_key: str):
    """Get Figma file data from cache if still valid."""
    if file_key in _figma_cache:
        cached = _figma_cache[file_key]
        if time.time() - cached["timestamp"] < FIGMA_CACHE_TTL:
            return cached["data"]
        else:
            del _figma_cache[file_key]
    return None

def set_cached_figma_data(file_key: str, data: dict):
    """Cache Figma file data."""
    _figma_cache[file_key] = {"data": data, "timestamp": time.time()}
    # Cleanup old entries (keep max 20)
    if len(_figma_cache) > 20:
        oldest_key = min(_figma_cache.keys(), key=lambda k: _figma_cache[k]["timestamp"])
        del _figma_cache[oldest_key]

def _friendly_api_error(e: Exception) -> HTTPException:
    """Convert raw Anthropic/network errors to user-friendly HTTP exceptions."""
    err = str(e).lower()
    if "credit" in err or "balance" in err or "billing" in err:
        return HTTPException(status_code=402, detail="The AI service is temporarily unavailable due to insufficient API credits. Please contact the administrator.")
    if "rate_limit" in err or "429" in err:
        return HTTPException(status_code=429, detail="Too many requests. Please wait a moment and try again.")
    if "overloaded" in err or "529" in err:
        return HTTPException(status_code=503, detail="The AI service is temporarily overloaded. Please try again in a moment.")
    if "timeout" in err or "timed out" in err:
        return HTTPException(status_code=504, detail="The request timed out. Please try again.")
    return HTTPException(status_code=500, detail="Analysis failed. Please try again.")


# --- Initialize Database ---
try:
    init_db()  # Create tables if they don't exist
except Exception as _db_init_err:
    import logging as _logging
    _logging.getLogger(__name__).warning(
        f"Database unavailable at startup — analysis will still work, "
        f"but report persistence and usage tracking are disabled. Error: {_db_init_err}"
    )


def _save_report_db(user_id: str, result: dict, analysis_type: str,
                    design_name: str = "", file_name: str = ""):
    """Save an analysis report to the database (JWT-authenticated endpoints only)."""
    if not user_id:
        return
    try:
        stats = result.get("statistics")
        report = AnalysisReport(
            user_id=user_id,
            analysis_type=analysis_type,
            design_name=design_name or None,
            file_name=file_name or None,
            html=result.get("html", ""),
            markdown=result.get("markdown"),
            statistics=json.dumps(stats) if stats else None,
        )
        with Session(engine) as session:
            session.add(report)
            session.commit()
    except Exception as e:
        logger.warning(f"[report_db] failed to save report: {e}")

# --- Simple API Key Validation ---
# In production, validate against WooCommerce, Stripe, or database

# For MVP: comma-separated list of valid API keys in environment variable
VALID_API_KEYS = set(
    key.strip()
    for key in os.environ.get("VALID_API_KEYS", "").split(",")
    if key.strip()
)

def verify_api_key(api_key: str, session: Session = None) -> bool:
    """
    Verify API key is valid.

    Checks both environment variable (VALID_API_KEYS) and database (is_active).
    If session is provided, uses database validation.
    """
    if session:
        return verify_api_key_db(session, api_key, VALID_API_KEYS)
    # Fallback to simple env var check
    if not VALID_API_KEYS:
        return True
    return api_key in VALID_API_KEYS

# --- FastAPI App ---

app = FastAPI(
    title="UI Traps Analyzer API",
    description="Analyze UI designs for usability issues using the UI Tenets & Traps framework",
    version="1.0.0"
)

# CORS middleware - allows uitraps.com, all subdomains, and localhost for dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_origin_regex=ALLOWED_ORIGIN_REGEX,
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

# --- MCP auth middleware ---
# Validates API keys for all /mcp/* requests before the MCP sub-app sees them.
# The authenticated key is stored in a contextvar so tools can track usage.

@app.middleware("http")
async def mcp_auth_middleware(request: Request, call_next):
    if not request.url.path.startswith("/mcp"):
        return await call_next(request)

    # Let OPTIONS pass through so CORS preflight works without auth
    if request.method == "OPTIONS":
        return await call_next(request)

    # Accept key from Authorization: Bearer header or ?api_key= query param
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        api_key = auth_header[7:].strip()
    else:
        api_key = request.query_params.get("api_key", "").strip()

    if not api_key:
        return JSONResponse(
            status_code=401,
            content={"error": "Authentication required. Set Authorization: Bearer <api_key> header."},
        )

    with Session(engine) as session:
        if not verify_api_key(api_key, session):
            return JSONResponse(
                status_code=403,
                content={"error": "Invalid or expired API key. Check your UITraps subscription."},
            )

    # Make the key available to MCP tool functions via contextvar
    token = mcp_api_key.set(api_key)
    try:
        return await call_next(request)
    finally:
        mcp_api_key.reset(token)

# --- Mount MCP server ---
# Streamable HTTP endpoint: /mcp  (configure this URL in your MCP client)
try:
    _mcp_asgi = mcp.http_app(path="/")
    app.mount("/mcp", _mcp_asgi)
    logger.info("MCP server mounted at /mcp")
except Exception as e:
    logger.warning("MCP server could not be mounted: %s", e)

# Initialize analyzer (reuse instance for efficiency)
analyzer = None

def get_analyzer() -> UITrapsAnalyzer:
    """Get or create analyzer instance."""
    global analyzer
    if analyzer is None:
        analyzer = UITrapsAnalyzer()
    return analyzer

# --- Response Models ---

class AnalysisResponse(BaseModel):
    success: bool
    report_html: Optional[str] = None
    report_markdown: Optional[str] = None
    statistics: Optional[dict] = None
    usage: Optional[dict] = None
    error: Optional[str] = None

class UsageResponse(BaseModel):
    used_this_month: int
    limit: int
    remaining: int

class HealthResponse(BaseModel):
    status: str
    timestamp: str


class EstimateResponse(BaseModel):
    success: bool
    input_type: str
    file_count: int
    total_size_mb: float
    estimated_frames: Optional[int] = None
    video_duration_seconds: Optional[float] = None
    time_estimate: dict
    cost_estimate: dict
    ffmpeg_available: bool = True


class MultiAnalysisResponse(BaseModel):
    success: bool
    report_html: Optional[str] = None
    report_markdown: Optional[str] = None
    statistics: Optional[dict] = None
    usage: Optional[dict] = None
    analysis_type: str = "multi_image"
    frame_count: int = 0
    error: Optional[str] = None


class FigmaEstimateResponse(BaseModel):
    success: bool
    file_name: str
    frame_count: int
    has_prototype_flows: bool
    time_estimate: dict
    cost_estimate: dict
    figma_available: bool = True


class UrlEstimateResponse(BaseModel):
    success: bool
    url: str
    estimated_pages: int
    time_estimate: dict
    cost_estimate: dict
    playwright_available: bool = True


class SiteAnalysisResponse(BaseModel):
    success: bool
    report_html: Optional[str] = None
    report_markdown: Optional[str] = None
    statistics: Optional[dict] = None
    site_summary: Optional[dict] = None
    pages_analyzed: int = 0
    analysis_type: str = "site"
    error: Optional[str] = None


# --- Capability Checks ---

def is_figma_available() -> bool:
    """Check if Figma API is configured."""
    return bool(os.environ.get("FIGMA_TOKEN"))


def is_playwright_available() -> bool:
    """Check if Playwright is installed."""
    try:
        from playwright.sync_api import sync_playwright
        return True
    except ImportError:
        return False


# --- Multi-analyzer instance ---
multi_analyzer = None


def get_multi_analyzer() -> MultiAnalyzer:
    """Get or create multi-analyzer instance."""
    global multi_analyzer
    if multi_analyzer is None:
        multi_analyzer = MultiAnalyzer(get_analyzer())
    return multi_analyzer


# --- Chat Service (lazy init) ---
_chat_service = None


def get_chat_service() -> ChatService:
    """
    Get or create chat service instance.

    Uses full context injection - the complete UI Tenets & Traps knowledge base
    is loaded into the system prompt. No external vector database required.

    Returns None if ANTHROPIC_API_KEY is not configured.
    """
    global _chat_service
    if _chat_service is None:
        anthropic_key = os.environ.get("ANTHROPIC_API_KEY", "")

        if not anthropic_key:
            return None  # Chat not configured yet

        ai_svc = ChatAIService(
            anthropic_api_key=anthropic_key,
            model=os.environ.get("CHAT_AI_MODEL", "claude-sonnet-4-5-20250929"),
            max_tokens=int(os.environ.get("CHAT_MAX_TOKENS", "1024")),
            temperature=float(os.environ.get("CHAT_TEMPERATURE", "0.7")),
        )
        _chat_service = ChatService(ai_svc)
    return _chat_service


# --- Chat Response Models ---

class ChatRequest(BaseModel):
    message: str
    conversationHistory: list[dict] = []


class ChatResponse(BaseModel):
    response: str
    sources: list[str] = []
    usage: Optional[dict] = None
    mode: str = "chat"


class UnifiedAskResponse(BaseModel):
    success: bool
    mode: str
    # Chat fields
    response: Optional[str] = None
    sources: Optional[list[str]] = None
    # Analysis fields (single version)
    report_html: Optional[str] = None
    report_markdown: Optional[str] = None
    statistics: Optional[dict] = None
    usage: Optional[dict] = None
    error: Optional[str] = None
    # Dual analysis fields (kb_version="both")
    report_html_v1: Optional[str] = None
    report_html_v2: Optional[str] = None
    statistics_v1: Optional[dict] = None
    statistics_v2: Optional[dict] = None
    kb_version: Optional[str] = None


# --- Endpoints ---

@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check for monitoring."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

class AccessCodeRequest(BaseModel):
    code: str = ""

@app.post("/auth/access-code")
async def verify_access_code(body: AccessCodeRequest):
    """Verify a direct-access code for non-WordPress users."""
    code = body.code.strip()
    configured = os.environ.get("DIRECT_ACCESS_CODE", "").strip()
    if not configured:
        return {"success": False, "error": "Access code not configured on server"}
    if code and code == configured:
        return {"success": True}
    return {"success": False, "error": "Invalid access code"}

# ===========================================================
# Analysis Endpoints
#
# SYNC RULE: When adding a new /analyze-* endpoint below,
# also add a corresponding @mcp.tool() in src/mcp_server.py.
# The MCP tools are thin wrappers — all logic stays here in
# the service classes. See src/mcp_server.py for the checklist.
# ===========================================================

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze(
    image: UploadFile = File(..., description="PNG or JPEG image to analyze"),
    users: str = Form(..., description="Who are the users? (e.g., 'First-time visitors, ages 25-45')"),
    tasks: str = Form(..., description="What are they trying to do? (e.g., 'Sign up for an account')"),
    format: str = Form(..., description="What format is this? (e.g., 'Mobile app screenshot')"),
    content_type: str = Form("website", description="Content type: website, mobile_app, desktop_app, game, or other"),
    api_key: str = Form(..., description="Your API key from subscription")
):
    """
    Analyze a UI screenshot for usability issues.

    Upload a PNG or JPEG image along with context about the users and their tasks.
    Returns a detailed HTML report identifying UI Traps and usability issues.

    **Rate Limit**: 20 analyses per month per API key (configurable).
    """
    with Session(engine) as session:
        # 1. Verify API key
        if not verify_api_key(api_key, session):
            log_analysis(session, api_key, "/analyze", "single_image", 0, "failed_auth")
            raise HTTPException(
                status_code=403,
                detail="Invalid or expired API key. Please check your subscription."
            )

        # 2. Get tier-specific limit and check usage quota
        limit = get_monthly_limit(session, api_key, MONTHLY_LIMIT)
        current_usage = get_usage(session, api_key)
        if current_usage >= limit:
            log_analysis(session, api_key, "/analyze", "single_image", 0, "quota_exceeded")
            raise HTTPException(
                status_code=402,
                detail=f"Monthly quota exceeded. You've used {current_usage}/{limit} analyses this month. "
                       f"Please upgrade your plan or wait until next month."
            )

        # 3. Validate file type
        if image.content_type not in ["image/png", "image/jpeg", "image/jpg"]:
            raise HTTPException(
                status_code=400,
                detail=f"Only PNG and JPEG images are supported. Received: {image.content_type}"
            )

        # 4. Validate file size (max 10MB)
        contents = await image.read()
        if len(contents) > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail="Image too large. Maximum size is 10MB."
            )

        # 5. Save to temp file (analyzer expects file path)
        suffix = ".png" if image.content_type == "image/png" else ".jpg"

        try:
            logger.info(f"[/analyze] start — file={image.filename} size={len(contents)} content_type={image.content_type}")
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(contents)
                tmp_path = tmp.name
            logger.info(f"[/analyze] temp file written: {tmp_path}")

            # 6. Build user context
            user_context = {
                "users": users,
                "tasks": tasks,
                "format": format,
                "content_type": content_type
            }

            # 7. Run analysis
            logger.info("[/analyze] starting analyze_design")
            analyzer_instance = get_analyzer()
            result = analyzer_instance.analyze_design(
                design_file=tmp_path,
                user_context=user_context
            )
            logger.info("[/analyze] analyze_design complete")

            # 8. Increment usage after successful analysis
            logger.info("[/analyze] incrementing usage")
            new_usage = increment_usage(session, api_key, 1, MONTHLY_LIMIT)
            log_analysis(session, api_key, "/analyze", "single_image", 1, "success")
            logger.info(f"[/analyze] usage incremented to {new_usage}")

            # 8.5. Save report to disk
            report_path = save_analysis_report(
                analysis_result=result,
                analysis_type="single_image",
                user_context=user_context,
                metadata={"file_name": image.filename, "api_key": api_key[:8] + "..."}
            )
            logger.info(f"Report saved to: {report_path}")

            # 9. Return response
            return {
                "success": True,
                "report_html": result.get("html"),
                "report_markdown": result.get("markdown"),
                "statistics": result.get("statistics"),
                "usage": {
                    "used_this_month": new_usage,
                    "limit": limit,
                    "remaining": limit - new_usage
                }
            }

        except ValueError as e:
            # Validation errors from analyzer
            raise HTTPException(status_code=400, detail=str(e))

        except Exception as e:
            logger.error(f"Analysis error: {e}\n{traceback.format_exc()}")
            raise _friendly_api_error(e)

        finally:
            # Clean up temp file
            try:
                if 'tmp_path' in locals():
                    os.unlink(tmp_path)
            except:
                pass

@app.get("/usage", response_model=UsageResponse)
async def get_usage_info(api_key: str):
    """
    Get current usage information for an API key.

    Returns how many analyses have been used this month and the limit.
    """
    with Session(engine) as session:
        if not verify_api_key(api_key, session):
            raise HTTPException(status_code=403, detail="Invalid API key")

        current_usage = get_usage(session, api_key)
        limit = get_monthly_limit(session, api_key, MONTHLY_LIMIT)
        return {
            "used_this_month": current_usage,
            "limit": limit,
            "remaining": limit - current_usage
        }


@app.post("/estimate")
async def estimate_analysis(
    files: List[UploadFile] = File(..., description="Files to analyze (images or video)")
):
    """
    Get time and cost estimates before running analysis.

    Upload your files to see how long analysis will take and how many credits it will cost.
    Does NOT run the actual analysis - just provides estimates.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    if len(files) > EstimationConstants.MAX_IMAGES:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum {EstimationConstants.MAX_IMAGES} files allowed"
        )

    # Get file info
    filenames = [f.filename for f in files]
    file_sizes = []

    for f in files:
        content = await f.read()
        file_sizes.append(len(content))
        await f.seek(0)  # Reset for potential later use

    try:
        input_type = detect_input_type(filenames)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    ffmpeg_ok = True

    if input_type == 'video':
        # Need FFmpeg for video
        ffmpeg_ok = is_ffmpeg_available()

        if ffmpeg_ok:
            # Save temp file to get video info
            video_file = files[0]
            content = await video_file.read()
            suffix = Path(video_file.filename).suffix

            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(content)
                tmp_path = tmp.name

            try:
                processor = VideoProcessor()
                video_info = processor.get_video_info(tmp_path)
                estimated_frames = processor.estimate_frames(tmp_path)

                estimate = estimate_video(
                    file_sizes[0],
                    video_info['duration'],
                    estimated_frames
                )
            finally:
                os.unlink(tmp_path)
        else:
            # Can't process video without FFmpeg
            estimate = estimate_video(file_sizes[0], 30, 8)  # Rough estimate

    elif input_type == 'multi_image':
        estimate = estimate_multi_image(file_sizes)

    else:  # single_image
        estimate = estimate_single_image(file_sizes[0])

    result = estimate.to_dict()
    result['success'] = True
    result['ffmpeg_available'] = ffmpeg_ok

    return result


@app.post("/analyze-multi", response_model=MultiAnalysisResponse)
async def analyze_multi(
    images: List[UploadFile] = File(..., description="Multiple PNG or JPEG images"),
    users: str = Form(..., description="Who are the users?"),
    tasks: str = Form(..., description="What are they trying to do?"),
    format: str = Form(..., description="What format is this?"),
    content_type: str = Form("website", description="Content type: website, mobile_app, desktop_app, game, or other"),
    api_key: str = Form(..., description="Your API key")
):
    """
    Analyze multiple screenshots at once.

    Upload 2-10 screenshots of a user flow for comprehensive analysis.
    Results are aggregated across all images.
    """
    with Session(engine) as session:
        # 1. Verify API key
        if not verify_api_key(api_key, session):
            log_analysis(session, api_key, "/analyze-multi", "multi_image", 0, "failed_auth")
            raise HTTPException(status_code=403, detail="Invalid API key")

        # 2. Validate file count
        if len(images) < 1:
            raise HTTPException(status_code=400, detail="At least 1 image required")

        if len(images) > EstimationConstants.MAX_IMAGES:
            raise HTTPException(
                status_code=400,
                detail=f"Maximum {EstimationConstants.MAX_IMAGES} images allowed"
            )

        # 3. Check quota (each image costs 1 credit)
        limit = get_monthly_limit(session, api_key, MONTHLY_LIMIT)
        current_usage = get_usage(session, api_key)
        credits_needed = len(images)

        if current_usage + credits_needed > limit:
            log_analysis(session, api_key, "/analyze-multi", "multi_image", 0, "quota_exceeded")
            raise HTTPException(
                status_code=402,
                detail=f"Not enough credits. You have {limit - current_usage} remaining, "
                       f"but this analysis requires {credits_needed} credits."
            )

        # 4. Save all images to temp files
        tmp_paths = []
        try:
            for img in images:
                if img.content_type not in ["image/png", "image/jpeg", "image/jpg"]:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Only PNG and JPEG images supported. Got: {img.content_type}"
                    )

                content = await img.read()
                if len(content) > 10 * 1024 * 1024:
                    raise HTTPException(status_code=400, detail="Image too large (max 10MB)")

                suffix = ".png" if img.content_type == "image/png" else ".jpg"
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                    tmp.write(content)
                    tmp_paths.append(tmp.name)

            # 5. Build context
            user_context = {"users": users, "tasks": tasks, "format": format, "content_type": content_type}

            # 6. Run multi-analysis
            multi = get_multi_analyzer()
            result = multi.analyze_images(tmp_paths, user_context)

            # 7. Increment usage
            new_usage = increment_usage(session, api_key, credits_needed, MONTHLY_LIMIT)
            log_analysis(session, api_key, "/analyze-multi", "multi_image", credits_needed, "success",
                        {"image_count": len(images)})

            # 7.5. Save report to disk
            report_path = save_analysis_report(
                analysis_result=result,
                analysis_type="multi_image",
                user_context=user_context,
                metadata={
                    "image_count": len(images),
                    "file_names": [img.filename for img in images],
                    "api_key": api_key[:8] + "..."
                }
            )
            logger.info(f"Report saved to: {report_path}")

            return {
                "success": True,
                "report_html": result.get("html"),
                "report_markdown": result.get("markdown"),
                "statistics": result.get("statistics"),
                "analysis_type": "multi_image",
                "frame_count": result.get("frame_count", len(images)),
                "usage": {
                    "used_this_month": new_usage,
                    "limit": limit,
                    "remaining": limit - new_usage
                }
            }

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

        finally:
            # Clean up temp files
            for path in tmp_paths:
                try:
                    os.unlink(path)
                except:
                    pass


@app.post("/analyze-video", response_model=MultiAnalysisResponse)
async def analyze_video(
    video: UploadFile = File(..., description="Video file (MP4, MOV, WebM)"),
    users: str = Form(..., description="Who are the users?"),
    tasks: str = Form(..., description="What are they trying to do?"),
    format: str = Form(..., description="What format is this?"),
    content_type: str = Form("website", description="Content type: website, mobile_app, desktop_app, game, or other"),
    api_key: str = Form(..., description="Your API key"),
    max_frames: int = Form(15, description="Maximum frames to analyze (5-20)")
):
    """
    Analyze a video by extracting and analyzing key frames.

    Upload a screen recording and we'll extract frames where the UI changes,
    then analyze each frame for UI Traps.

    **Requires FFmpeg on server.**
    """
    # 1. Check FFmpeg availability
    if not is_ffmpeg_available():
        raise HTTPException(
            status_code=503,
            detail="Video analysis is not available. FFmpeg is not installed on the server."
        )

    with Session(engine) as session:
        # 2. Verify API key
        if not verify_api_key(api_key, session):
            log_analysis(session, api_key, "/analyze-video", "video", 0, "failed_auth")
            raise HTTPException(status_code=403, detail="Invalid API key")

        # 3. Validate max_frames
        max_frames = max(5, min(20, max_frames))

        # 4. Validate file type
        video_types = ["video/mp4", "video/quicktime", "video/webm", "video/x-msvideo"]
        if video.content_type not in video_types:
            raise HTTPException(
                status_code=400,
                detail=f"Only MP4, MOV, WebM videos supported. Got: {video.content_type}"
            )

        # 5. Save video to temp file
        content = await video.read()
        if len(content) > 100 * 1024 * 1024:  # 100MB limit for video
            raise HTTPException(status_code=400, detail="Video too large (max 100MB)")

        suffix = Path(video.filename).suffix or ".mp4"
        tmp_path = None

        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(content)
                tmp_path = tmp.name

            # 6. Estimate frames and check quota
            processor = VideoProcessor()
            estimated_frames = processor.estimate_frames(tmp_path)
            frames_to_use = min(estimated_frames, max_frames)

            limit = get_monthly_limit(session, api_key, MONTHLY_LIMIT)
            current_usage = get_usage(session, api_key)
            if current_usage + frames_to_use > limit:
                log_analysis(session, api_key, "/analyze-video", "video", 0, "quota_exceeded")
                raise HTTPException(
                    status_code=402,
                    detail=f"Not enough credits. You have {limit - current_usage} remaining, "
                           f"but this video may need up to {frames_to_use} credits."
                )

            # 7. Build context
            user_context = {"users": users, "tasks": tasks, "format": format, "content_type": content_type}

            # 8. Run video analysis
            multi = get_multi_analyzer()
            result = multi.analyze_video(tmp_path, user_context, max_frames=max_frames)

            # 9. Increment usage based on actual frames analyzed
            actual_frames = result.get("successful_count", frames_to_use)
            new_usage = increment_usage(session, api_key, actual_frames, MONTHLY_LIMIT)
            log_analysis(session, api_key, "/analyze-video", "video", actual_frames, "success",
                        {"frame_count": actual_frames})

            # 9.5. Save report to disk
            report_path = save_analysis_report(
                analysis_result=result,
                analysis_type="video",
                user_context=user_context,
                metadata={
                    "file_name": video.filename,
                    "frame_count": actual_frames,
                    "api_key": api_key[:8] + "..."
                }
            )
            logger.info(f"Report saved to: {report_path}")

            return {
                "success": True,
                "report_html": result.get("html"),
                "report_markdown": result.get("markdown"),
                "statistics": result.get("statistics"),
                "analysis_type": "video",
                "frame_count": result.get("frame_count", 0),
                "usage": {
                    "used_this_month": new_usage,
                    "limit": limit,
                    "remaining": limit - new_usage
                }
            }

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Video analysis failed: {str(e)}")

        finally:
            if tmp_path:
                try:
                    os.unlink(tmp_path)
                except:
                    pass


@app.get("/capabilities")
async def get_capabilities():
    """
    Get server capabilities (video support, limits, etc.)

    Use this to know what features are available before uploading.
    """
    return {
        "video_analysis": is_ffmpeg_available(),
        "figma_analysis": is_figma_available(),
        "url_analysis": is_playwright_available(),
        "pdf_analysis": is_pymupdf_available(),
        "max_images": EstimationConstants.MAX_IMAGES,
        "max_video_frames": EstimationConstants.MAX_VIDEO_FRAMES,
        "max_pdf_pages": 20,
        "max_crawl_pages": 10,
        "max_image_size_mb": 10,
        "max_video_size_mb": 100,
        "max_pdf_size_mb": 50,
        "supported_image_types": ["image/png", "image/jpeg"],
        "supported_video_types": ["video/mp4", "video/quicktime", "video/webm"],
        "supported_document_types": ["application/pdf"]
    }


@app.get("/reports")
async def list_saved_reports(
    limit: int = 20,
    user: dict = Depends(get_current_user)
):
    """List saved analysis reports for the authenticated user (DB-backed)."""
    user_id = str(user.get("id") or user.get("userId", ""))
    try:
        with Session(engine) as session:
            rows = session.exec(
                select(AnalysisReport)
                .where(AnalysisReport.user_id == user_id)
                .order_by(AnalysisReport.timestamp.desc())
                .limit(limit)
            ).all()
            reports = [
                {
                    "id": r.id,
                    "timestamp": r.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    "analysis_type": r.analysis_type,
                    "design_name": r.design_name,
                    "file_name": r.file_name,
                    "statistics": json.loads(r.statistics) if r.statistics else None,
                }
                for r in rows
            ]
        return {"success": True, "reports": reports, "count": len(reports)}
    except Exception as _db_err:
        logger.warning("Database unavailable for /reports: %s", _db_err)
        return {"success": True, "reports": [], "count": 0, "db_unavailable": True}


@app.get("/reports/{report_id}")
async def get_saved_report(
    report_id: int,
    user: dict = Depends(get_current_user)
):
    """Retrieve a specific saved report by ID (DB-backed)."""
    user_id = str(user.get("id") or user.get("userId", ""))
    try:
        with Session(engine) as session:
            report = session.get(AnalysisReport, report_id)
            if report is None:
                raise HTTPException(status_code=404, detail="Report not found")
            if report.user_id != user_id:
                raise HTTPException(status_code=403, detail="Access denied")
            result = {
                "success": True,
                "report": {
                    "id": report.id,
                    "timestamp": report.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    "analysis_type": report.analysis_type,
                    "design_name": report.design_name,
                    "file_name": report.file_name,
                    "html": report.html,
                    "markdown": report.markdown,
                    "statistics": json.loads(report.statistics) if report.statistics else None,
                }
            }
        return result
    except HTTPException:
        raise
    except Exception as _db_err:
        logger.warning("Database unavailable for /reports/%s: %s", report_id, _db_err)
        raise HTTPException(status_code=503, detail="Report storage is temporarily unavailable.")


# ===========================================================
# URL-Based Analysis Endpoints (Figma and Website Crawl)
# ===========================================================

@app.post("/estimate-figma")
async def estimate_figma(
    figma_url: str = Form(..., description="Figma file URL")
):
    """
    Get estimate for Figma file analysis.

    Fetches file metadata without exporting images to provide time/cost estimate.
    """
    if not is_figma_available():
        raise HTTPException(
            status_code=503,
            detail="Figma analysis not available. FIGMA_TOKEN not configured."
        )

    try:
        figma = FigmaAnalyzer()
        file_key, _ = figma.parse_figma_url(figma_url)

        # Check cache first to avoid hitting Figma API twice
        file_data = get_cached_figma_data(file_key)
        if not file_data:
            file_data = figma.get_file_data(file_key)
            set_cached_figma_data(file_key, file_data)

        # Get frame count
        frames = figma.get_all_frames(file_data)
        frame_count = len(frames)

        # Get prototype flows
        flows = figma.get_prototype_flows(file_data)

        # Estimate time: ~30 seconds per frame for export + analysis
        time_min = frame_count * 25
        time_max = frame_count * 45

        return {
            "success": True,
            "file_name": file_data.get("name", "Untitled"),
            "frame_count": frame_count,
            "has_prototype_flows": len(flows) > 0,
            "flow_count": len(flows),
            "time_estimate": {
                "min_seconds": time_min,
                "max_seconds": time_max,
                "description": f"{time_min // 60}-{time_max // 60} minutes"
            },
            "cost_estimate": {
                "credits": frame_count,
                "description": f"{frame_count} credits (1 per frame)"
            },
            "figma_available": True
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch Figma file: {str(e)}")


@app.post("/estimate-url")
async def estimate_url(
    url: str = Form(..., description="Website URL to analyze"),
    max_pages: int = Form(10, description="Maximum pages to crawl (1-10)"),
    device_type: Optional[str] = Form(None, description="Device type: mobile, tablet, or desktop")
):
    """
    Get estimate for website crawl and analysis.

    Returns estimated time and cost based on max pages setting.
    """
    if not is_playwright_available():
        raise HTTPException(
            status_code=503,
            detail="URL analysis not available. Playwright not installed."
        )

    # Validate max_pages
    max_pages = max(1, min(10, max_pages))

    # Determine viewport from device type
    viewport_presets = {
        "mobile": (390, 844, "iPhone 13"),
        "tablet": (768, 1024, "iPad"),
        "desktop": (1920, 1080, "Desktop")
    }
    viewport_width, viewport_height, device_name = viewport_presets.get(
        device_type,
        (1920, 1080, "Desktop")
    )

    # Estimate: ~20 seconds per page for crawl, ~30 seconds per page for analysis
    time_per_page = 50  # seconds
    time_min = max_pages * 40
    time_max = max_pages * 60

    return {
        "success": True,
        "url": url,
        "estimated_pages": max_pages,
        "device_type": device_type or "desktop",
        "viewport": {
            "width": viewport_width,
            "height": viewport_height,
            "description": f"{device_name} ({viewport_width}×{viewport_height})"
        },
        "time_estimate": {
            "min_seconds": time_min,
            "max_seconds": time_max,
            "description": f"{time_min // 60}-{time_max // 60} minutes (up to {max_pages} pages)"
        },
        "cost_estimate": {
            "credits": max_pages,
            "description": f"Up to {max_pages} credits (1 per page)"
        },
        "playwright_available": True
    }


@app.post("/analyze-figma", response_model=SiteAnalysisResponse)
async def analyze_figma(
    figma_url: str = Form(..., description="Figma file URL"),
    users: str = Form(..., description="Who are the users?"),
    tasks: str = Form(..., description="What are they trying to do?"),
    format: str = Form("Figma design", description="Format description"),
    content_type: str = Form("website", description="Content type"),
    api_key: str = Form(..., description="Your API key"),
    max_frames: int = Form(10, description="Maximum frames to analyze (1-20)")
):
    """
    Analyze a Figma file for UI Traps.

    Exports frames from Figma and analyzes each for usability issues.
    Includes prototype flow analysis for multi-screen traps.
    """
    if not is_figma_available():
        raise HTTPException(
            status_code=503,
            detail="Figma analysis not available. FIGMA_TOKEN not configured."
        )

    with Session(engine) as session:
        # Verify API key
        if not verify_api_key(api_key, session):
            log_analysis(session, api_key, "/analyze-figma", "figma", 0, "failed_auth")
            raise HTTPException(status_code=403, detail="Invalid API key")

        # Validate max_frames
        max_frames = max(1, min(20, max_frames))

        try:
            # Create temp directory for exports
            with tempfile.TemporaryDirectory() as tmp_dir:
                # Export frames from Figma (use cached file data if available)
                # Pass max_frames to limit exports and speed up analysis
                figma = FigmaAnalyzer()
                file_key, _ = figma.parse_figma_url(figma_url)
                cached_data = get_cached_figma_data(file_key)
                figma_result = figma.analyze_figma_file(
                    figma_url, tmp_dir,
                    cached_file_data=cached_data,
                    max_frames=max_frames
                )

                frames = figma_result["frames"]
                frame_count = len(frames)

                # Check quota
                limit = get_monthly_limit(session, api_key, MONTHLY_LIMIT)
                current_usage = get_usage(session, api_key)
                if current_usage + frame_count > limit:
                    log_analysis(session, api_key, "/analyze-figma", "figma", 0, "quota_exceeded")
                    raise HTTPException(
                        status_code=402,
                        detail=f"Not enough credits. You have {limit - current_usage} remaining, "
                               f"but this analysis requires {frame_count} credits."
                    )

                # Prepare pages for SiteAnalyzer
                pages = []
                for frame in frames:
                    if frame.get("image_path"):
                        pages.append({
                            "url": f"figma://{figma_result['file_info']['key']}/{frame['id']}",
                            "title": frame["name"],
                            "screenshot_path": frame["image_path"]
                        })

                if not pages:
                    raise HTTPException(status_code=400, detail="No frames could be exported from Figma file")

                # Run site analysis
                site_analyzer = SiteAnalyzer()
                user_context = {
                    "users": users,
                    "tasks": tasks,
                    "format": format,
                    "content_type": content_type
                }

                result = site_analyzer.analyze_site(pages, user_context)

                # Generate HTML report from results
                from src.report_generator import generate_site_report
                html_report = generate_site_report(result, figma_result["file_info"]["name"])

                # Increment usage
                new_usage = increment_usage(session, api_key, frame_count, MONTHLY_LIMIT)
                log_analysis(session, api_key, "/analyze-figma", "figma", frame_count, "success",
                            {"frame_count": frame_count, "file_name": figma_result["file_info"]["name"]})

                # Save report to disk
                report_path = save_analysis_report(
                    analysis_result={
                        "html": html_report,
                        "statistics": result.get("statistics"),
                        "site_summary": result.get("site_summary"),
                        "page_analyses": result.get("page_analyses"),
                        "flow_analyses": result.get("flow_analyses"),
                        "recommendations": result.get("recommendations")
                    },
                    analysis_type="figma",
                    user_context=user_context,
                    metadata={
                        "figma_url": figma_url,
                        "file_name": figma_result["file_info"]["name"],
                        "frame_count": frame_count,
                        "api_key": api_key[:8] + "..."
                    }
                )
                logger.info(f"Report saved to: {report_path}")

                return {
                    "success": True,
                    "report_html": html_report,
                    "statistics": result.get("statistics"),
                    "site_summary": result.get("site_summary"),
                    "pages_analyzed": frame_count,
                    "analysis_type": "figma"
                }

        except HTTPException:
            raise
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Figma analysis error: {e}")
            raise HTTPException(status_code=500, detail=f"Figma analysis failed: {str(e)}")


@app.post("/analyze-url", response_model=SiteAnalysisResponse)
async def analyze_url(
    url: str = Form(..., description="Website URL to analyze"),
    users: str = Form(..., description="Who are the users?"),
    tasks: str = Form(..., description="What are they trying to do?"),
    format: str = Form("Website", description="Format description"),
    content_type: str = Form("website", description="Content type"),
    api_key: str = Form(..., description="Your API key"),
    max_pages: int = Form(10, description="Maximum pages to crawl (1-10)"),
    capture_interactions: bool = Form(False, description="Enable interaction capture (hover, click, form states)"),
    cookies: Optional[str] = Form(None, description="Cookies as JSON string (array or dict format)"),
    device_type: Optional[str] = Form(None, description="Device type: mobile, tablet, or desktop"),
    viewport_width: Optional[int] = Form(None, description="Viewport width override"),
    viewport_height: Optional[int] = Form(None, description="Viewport height override")
):
    """
    Crawl and analyze a website for UI Traps.

    Crawls the website starting from the given URL, captures screenshots,
    and analyzes each page for usability issues.

    With capture_interactions=True, also captures and analyzes:
    - Hover states on interactive elements
    - Click feedback on buttons and links
    - Form validation states
    - Responsive behavior at different viewport sizes

    With cookies parameter, can access authenticated/logged-in pages:
    - Format: '[{"name":"session","value":"abc123","domain":".site.com"}]'
    - Helps avoid false positives from missing authenticated content
    """
    if not is_playwright_available():
        raise HTTPException(
            status_code=503,
            detail="URL analysis not available. Playwright not installed. "
                   "Install with: pip install playwright && playwright install chromium"
        )

    with Session(engine) as session:
        # Verify API key
        if not verify_api_key(api_key, session):
            log_analysis(session, api_key, "/analyze-url", "url", 0, "failed_auth")
            raise HTTPException(status_code=403, detail="Invalid API key")

        # Validate max_pages
        max_pages = max(1, min(10, max_pages))

        # Check quota upfront (estimate)
        limit = get_monthly_limit(session, api_key, MONTHLY_LIMIT)
        current_usage = get_usage(session, api_key)
        if current_usage + max_pages > limit:
            log_analysis(session, api_key, "/analyze-url", "url", 0, "quota_exceeded")
            raise HTTPException(
                status_code=402,
                detail=f"Not enough credits. You have {limit - current_usage} remaining, "
                       f"but this analysis may require up to {max_pages} credits."
            )

        try:
            # Apply viewport presets based on device type
            viewport_presets = {
                "mobile": (390, 844),   # iPhone 13
                "tablet": (768, 1024),  # iPad
                "desktop": (1920, 1080)  # Standard desktop
            }

            # Use explicit viewport if provided, otherwise use device preset
            if viewport_width and viewport_height:
                final_viewport_width = viewport_width
                final_viewport_height = viewport_height
            else:
                final_viewport_width, final_viewport_height = viewport_presets.get(
                    device_type,
                    (1920, 1080)  # Default to desktop
                )

            logger.info(f"Using viewport: {final_viewport_width}x{final_viewport_height} (device_type: {device_type})")

            # Create temp directory for screenshots
            with tempfile.TemporaryDirectory() as tmp_dir:
                # Crawl website (with optional interaction capture)
                # Run in thread pool to avoid Playwright sync API conflict with asyncio
                import asyncio
                import concurrent.futures

                def run_crawl():
                    crawler = WebCrawler(
                        max_pages=max_pages,
                        max_depth=2,
                        viewport_width=final_viewport_width,
                        viewport_height=final_viewport_height,
                        cookies=cookies,  # ADD: Cookie support for authenticated crawling
                        enable_interaction_capture=capture_interactions,
                        enable_navigation_graph=True,  # Explicitly enable navigation graph
                        verify_ctas=True  # Verify CTA destinations
                    )
                    crawl_result = crawler.crawl(url, tmp_dir)
                    # Return both crawl result AND the navigation graph
                    return crawl_result, crawler.get_navigation_graph()

                loop = asyncio.get_running_loop()
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    crawl_result, navigation_graph = await loop.run_in_executor(executor, run_crawl)

                pages = crawl_result.get("pages", [])
                if not pages:
                    error_detail = (
                        f"No pages could be crawled from {url}. "
                        "This typically happens when:\n"
                        "1. The site is blocking automated access (bot detection)\n"
                        "2. The site requires authentication or cookies\n"
                        "3. The site is not accessible or has network issues\n"
                        "4. The site uses heavy JavaScript that didn't load in time\n\n"
                        "Try:\n"
                        "- Verifying the URL is accessible in a browser\n"
                        "- Using authentication if the site requires login\n"
                        "- Trying a different URL that may be less protected\n"
                        "- Waiting a few minutes before retrying (rate limiting)"
                    )
                    logger.warning(f"Crawl failed for {url}: No pages captured")
                    raise HTTPException(status_code=400, detail=error_detail)

                # Prepare pages for SiteAnalyzer
                site_pages = []
                for page in pages:
                    if page.get("screenshot_path") and os.path.exists(page["screenshot_path"]):
                        page_data = {
                            "url": page["url"],
                            "title": page["title"],
                            "screenshot_path": page["screenshot_path"],
                            "screenshot_base64": page.get("screenshot_base64")  # ADD: Include base64 for embedding
                        }
                        # Include interactions if captured
                        if page.get("interactions"):
                            page_data["interactions"] = page["interactions"]
                        site_pages.append(page_data)

                if not site_pages:
                    raise HTTPException(status_code=400, detail="No screenshots captured during crawl")

                # Run site analysis
                site_analyzer = SiteAnalyzer()

                # CRITICAL: Set navigation graph for flow-aware analysis
                if navigation_graph:
                    site_analyzer.set_navigation_graph(navigation_graph)
                    logger.info(f"Navigation graph set with {len(navigation_graph.pages)} pages")

                user_context = {
                    "users": users,
                    "tasks": tasks,
                    "format": format,
                    "content_type": content_type,
                    "device_type": device_type or "desktop",
                    "viewport": f"{final_viewport_width}×{final_viewport_height}"
                }

                # Use interaction-aware analysis if interactions were captured
                if capture_interactions:
                    result = site_analyzer.analyze_site_with_interactions(
                        site_pages,
                        user_context,
                        analyze_interactions=True
                    )
                else:
                    result = site_analyzer.analyze_site(site_pages, user_context)

                # Generate HTML report
                from src.report_generator import generate_site_report
                html_report = generate_site_report(result, url)

                # Increment usage based on actual pages analyzed
                pages_analyzed = len(site_pages)
                new_usage = increment_usage(session, api_key, pages_analyzed, MONTHLY_LIMIT)
                log_analysis(session, api_key, "/analyze-url", "url", pages_analyzed, "success",
                            {"pages_analyzed": pages_analyzed, "url": url})

                # Save report to disk
                report_path = save_analysis_report(
                    analysis_result={
                        "html": html_report,
                        "statistics": result.get("statistics"),
                        "site_summary": result.get("site_summary"),
                        "page_analyses": result.get("page_analyses"),
                        "flow_analyses": result.get("flow_analyses"),
                        "recommendations": result.get("recommendations"),
                        "interaction_analysis": result.get("interaction_analysis")
                    },
                    analysis_type="url",
                    user_context=user_context,
                    metadata={
                        "url": url,
                        "pages_analyzed": pages_analyzed,
                        "capture_interactions": capture_interactions,
                        "api_key": api_key[:8] + "..."
                    }
                )
                logger.info(f"Report saved to: {report_path}")

                response_data = {
                    "success": True,
                    "report_html": html_report,
                    "statistics": result.get("statistics"),
                    "site_summary": result.get("site_summary"),
                    "pages_analyzed": pages_analyzed,
                    "analysis_type": "url"
                }

                # Include interaction analysis if available
                if capture_interactions and result.get("interaction_analysis"):
                    response_data["interaction_analysis"] = result["interaction_analysis"]

                return response_data

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"URL analysis error: {e}")
            raise HTTPException(status_code=500, detail=f"URL analysis failed: {str(e)}")


# ===========================================================
# PDF Analysis Endpoints
# ===========================================================

@app.post("/estimate-pdf")
async def estimate_pdf(
    file: UploadFile = File(..., description="PDF file to analyze")
):
    """
    Get estimate for PDF document analysis.

    Returns page count and estimated time/cost.
    """
    if not is_pymupdf_available():
        raise HTTPException(
            status_code=503,
            detail="PDF analysis not available. PyMuPDF not installed. "
                   "Install with: pip install pymupdf"
        )

    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")

    # Save to temp file to read metadata
    content = await file.read()
    if len(content) > 50 * 1024 * 1024:  # 50MB limit
        raise HTTPException(status_code=400, detail="PDF too large (max 50MB)")

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        pdf_analyzer = PdfAnalyzer()
        pdf_info = pdf_analyzer.get_pdf_info(tmp_path)
        page_count = pdf_info['page_count']

        # Cap at max pages
        pages_to_analyze = min(page_count, pdf_analyzer.MAX_PAGES)

        # Estimate: ~20 seconds per page for conversion + analysis
        time_min = pages_to_analyze * 15
        time_max = pages_to_analyze * 30

        return {
            "success": True,
            "file_name": file.filename,
            "page_count": page_count,
            "pages_to_analyze": pages_to_analyze,
            "pdf_info": {
                "title": pdf_info.get('title', ''),
                "author": pdf_info.get('author', ''),
            },
            "time_estimate": {
                "min_seconds": time_min,
                "max_seconds": time_max,
                "description": f"{time_min // 60}-{time_max // 60} minutes"
            },
            "cost_estimate": {
                "credits": pages_to_analyze,
                "description": f"{pages_to_analyze} credits (1 per page)"
            },
            "pymupdf_available": True
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read PDF: {str(e)}")
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass


@app.post("/analyze-pdf")
async def analyze_pdf(
    file: UploadFile = File(..., description="PDF file to analyze"),
    users: str = Form(..., description="Who are the users?"),
    tasks: str = Form(..., description="What are they trying to do?"),
    format: str = Form("PDF document", description="Format description"),
    content_type: str = Form("pdf_document", description="Content type"),
    api_key: str = Form(..., description="Your API key"),
    max_pages: int = Form(20, description="Maximum pages to analyze (1-20)")
):
    """
    Analyze a PDF document for UI/document usability issues.

    Converts PDF pages to images and analyzes each for usability problems.
    Works well for forms, reports, presentations, and document-based interfaces.
    """
    if not is_pymupdf_available():
        raise HTTPException(
            status_code=503,
            detail="PDF analysis not available. PyMuPDF not installed. "
                   "Install with: pip install pymupdf"
        )

    with Session(engine) as session:
        # Verify API key
        if not verify_api_key(api_key, session):
            log_analysis(session, api_key, "/analyze-pdf", "pdf", 0, "failed_auth")
            raise HTTPException(status_code=403, detail="Invalid API key")

        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="File must be a PDF")

        # Validate max_pages
        max_pages = max(1, min(20, max_pages))

        # Save to temp file
        content = await file.read()
        if len(content) > 50 * 1024 * 1024:  # 50MB limit
            raise HTTPException(status_code=400, detail="PDF too large (max 50MB)")

        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                tmp.write(content)
                tmp_path = tmp.name

            # Get page count for quota check
            pdf_analyzer = PdfAnalyzer()
            pdf_info = pdf_analyzer.get_pdf_info(tmp_path)
            pages_to_analyze = min(pdf_info['page_count'], max_pages)

            # Check quota
            limit = get_monthly_limit(session, api_key, MONTHLY_LIMIT)
            current_usage = get_usage(session, api_key)
            if current_usage + pages_to_analyze > limit:
                log_analysis(session, api_key, "/analyze-pdf", "pdf", 0, "quota_exceeded")
                raise HTTPException(
                    status_code=402,
                    detail=f"Not enough credits. You have {limit - current_usage} remaining, "
                           f"but this analysis requires {pages_to_analyze} credits."
                )

            # Build user context
            user_context = {
                "users": users,
                "tasks": tasks,
                "format": format,
                "content_type": content_type
            }

            # Run PDF analysis
            result = pdf_analyzer.analyze(tmp_path, user_context, max_pages=max_pages)

            # Generate HTML report
            from src.report_generator import generate_site_report
            html_report = generate_site_report(result, file.filename)

            # Increment usage
            actual_pages = result.get('pages_analyzed', pages_to_analyze)
            new_usage = increment_usage(session, api_key, actual_pages, MONTHLY_LIMIT)
            log_analysis(session, api_key, "/analyze-pdf", "pdf", actual_pages, "success",
                        {"pages_analyzed": actual_pages, "file_name": file.filename})

            # Save report to disk
            report_path = save_analysis_report(
                analysis_result=result,
                analysis_type="pdf",
                user_context=user_context,
                metadata={
                    "file_name": file.filename,
                    "pages_analyzed": actual_pages,
                    "pdf_info": result.get("pdf_info"),
                    "api_key": api_key[:8] + "..."
                }
            )
            logger.info(f"Report saved to: {report_path}")

            return {
                "success": True,
                "report_html": html_report,
                "report_markdown": result.get("markdown"),
                "statistics": result.get("statistics"),
                "pdf_info": result.get("pdf_info"),
                "pages_analyzed": actual_pages,
                "analysis_type": "pdf",
                "usage": {
                    "used_this_month": new_usage,
                    "limit": limit,
                    "remaining": limit - new_usage
                }
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"PDF analysis error: {e}")
            raise HTTPException(status_code=500, detail=f"PDF analysis failed: {str(e)}")
        finally:
            if tmp_path:
                try:
                    os.unlink(tmp_path)
                except Exception:
                    pass


# ===========================================================
# Subscription & Token Webhook Endpoints (called by WordPress/WooCommerce)
# ===========================================================

def _verify_webhook_secret(request: Request) -> bool:
    """Check the X-Webhook-Secret header matches our shared secret."""
    if not WEBHOOK_SECRET:
        logger.warning("WEBHOOK_SECRET not set — accepting all webhook calls (dev mode)")
        return True
    return request.headers.get("X-Webhook-Secret", "") == WEBHOOK_SECRET


class SubscriptionWebhookRequest(BaseModel):
    user_id: str
    event: str  # activated | renewed | cancelled | expired
    monthly_limit: Optional[int] = None
    subscription_start: Optional[str] = None
    subscription_end: Optional[str] = None
    next_renewal: Optional[str] = None


class TokensWebhookRequest(BaseModel):
    user_id: str
    tokens: int


@app.post("/api/webhook/subscription")
async def webhook_subscription(payload: SubscriptionWebhookRequest, request: Request):
    """
    WooCommerce subscription lifecycle webhook.

    Called by WordPress when a subscription is activated, renewed, cancelled, or expired.
    Secure with X-Webhook-Secret header — set WEBHOOK_SECRET env var on both sides.

    Events:
      activated — new subscription started, resets monthly usage
      renewed   — subscription renewed, resets monthly usage and updates dates
      cancelled — subscription cancelled (access continues until period end)
      expired   — subscription fully expired, access revoked
    """
    if not _verify_webhook_secret(request):
        raise HTTPException(status_code=401, detail="Invalid webhook secret.")

    event = payload.event.lower()
    try:
        with Session(engine) as session:
            if event == "activated":
                result = activate_subscription(
                    session, payload.user_id,
                    monthly_limit=payload.monthly_limit or MONTHLY_LIMIT,
                    subscription_start=payload.subscription_start,
                    subscription_end=payload.subscription_end,
                    next_renewal=payload.next_renewal,
                )
            elif event == "renewed":
                result = renew_subscription(
                    session, payload.user_id,
                    monthly_limit=payload.monthly_limit,
                    next_renewal=payload.next_renewal,
                    subscription_end=payload.subscription_end,
                )
            elif event == "cancelled":
                result = cancel_subscription(session, payload.user_id)
            elif event == "expired":
                result = expire_subscription(session, payload.user_id)
            else:
                raise HTTPException(status_code=400, detail=f"Unknown event: {payload.event}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[webhook/subscription] DB error for user={payload.user_id} event={event}: {e}")
        raise HTTPException(status_code=503, detail="Database unavailable — subscription webhook could not be processed. Retry when DB is restored.")

    logger.info(f"[webhook/subscription] user={payload.user_id} event={event} status={result.subscription_status}")
    return {"success": True, "user_id": payload.user_id, "status": result.subscription_status}


@app.post("/api/webhook/tokens")
async def webhook_tokens(payload: TokensWebhookRequest, request: Request):
    """
    WooCommerce token top-up webhook.

    Called by WordPress when a user purchases additional tokens.
    Secure with X-Webhook-Secret header.
    """
    if not _verify_webhook_secret(request):
        raise HTTPException(status_code=401, detail="Invalid webhook secret.")

    if payload.tokens <= 0:
        raise HTTPException(status_code=400, detail="Tokens must be a positive number.")

    with Session(engine) as session:
        result = add_bonus_tokens(session, payload.user_id, payload.tokens)

    logger.info(f"[webhook/tokens] user={payload.user_id} added={payload.tokens} total_bonus={result.bonus_tokens}")
    return {"success": True, "user_id": payload.user_id, "bonus_tokens": result.bonus_tokens}


@app.get("/api/user/usage")
async def get_user_usage(user: dict = Depends(get_current_user)):
    """
    Get current usage and subscription status for the authenticated user.

    Returns monthly allowance, usage, bonus tokens, and subscription dates.
    """
    user_id = str(user.get("id") or user.get("userId", ""))
    with Session(engine) as session:
        summary = get_usage_summary(session, user_id)
    return {"success": True, **summary}


# ===========================================================
# NEW: Unified Platform Endpoints (JWT auth)
# ===========================================================

@app.get("/api/health")
async def api_health():
    """Health check for the unified API."""
    chat_available = get_chat_service() is not None
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "chat_available": chat_available,
    }


@app.post("/api/chat", response_model=ChatResponse)
async def api_chat(
    request: ChatRequest,
    user: dict = Depends(get_current_user),
):
    """
    RAG chat endpoint. Requires JWT authentication.

    Matches the contract from the Node.js backend exactly:
    - Input: {message, conversationHistory}
    - Output: {response, sources, usage}
    """
    # Validate message (matching Node chat.js lines 19-33)
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    if len(request.message) > 2000:
        raise HTTPException(
            status_code=400, detail="Message too long (max 2000 characters)"
        )

    chat_svc = get_chat_service()
    if chat_svc is None:
        raise HTTPException(
            status_code=503,
            detail="Chat service not configured. Missing ANTHROPIC_API_KEY.",
        )

    try:
        result = chat_svc.handle_chat(
            request.message, request.conversationHistory
        )
        return result
    except Exception as e:
        logger.error("Chat error: %s", e)
        raise _friendly_api_error(e)


@app.post("/api/ask", response_model=UnifiedAskResponse)
async def unified_ask(
    user: dict = Depends(get_current_user),
    message: Optional[str] = Form(None),
    files: List[UploadFile] = File(default=[]),
    users: Optional[str] = Form(None),
    tasks: Optional[str] = Form(None),
    format: Optional[str] = Form(None),
    content_type: str = Form("website"),
    conversation_history: Optional[str] = Form(None),
    chat_context: Optional[str] = Form(None),
    extra_context: Optional[str] = Form(None),
    product_context: Optional[str] = Form(None),
    physical_env: Optional[str] = Form(None),
    lighting: Optional[str] = Form(None),
    grip_position: Optional[str] = Form(None),
    attentional_state: Optional[str] = Form(None),
    tenet_filter: Optional[str] = Form(None),
    design_name: Optional[str] = Form(None),
    kb_version: str = Form("v2"),
    verbosity: str = Form("standard"),
    pass1_model: Optional[str] = Form(None),
    thorough_mode: Optional[str] = Form(None),
    task_list: Optional[str] = Form(None),
    input_type: Optional[str] = Form(None),
    flow_mode: Optional[str] = Form(None),
    figma_url: Optional[str] = Form(None),
):
    """
    Unified endpoint: auto-routes to analysis, chat, or hybrid based on input.

    - Text only → RAG chat
    - Files + context → Trap analysis
    - Files + question (no context) → Hybrid
    """
    intent = detect_intent(message, files, users, tasks, format, figma_url=figma_url, input_type=input_type)

    # For analysis requests, check subscription and consume a token
    # Skip in dev mode (DEV_MODE=true in .env) or for smoke-test user IDs (SMOKE_TEST_USER_IDS env var)
    _dev_mode = os.environ.get("DEV_MODE", "false").lower() in ("true", "1", "yes")
    _smoke_users = {u.strip() for u in os.environ.get("SMOKE_TEST_USER_IDS", "").split(",") if u.strip()}
    if intent.mode in (IntentMode.ANALYSIS, IntentMode.HYBRID, IntentMode.URL_ANALYSIS) and not _dev_mode:
        user_id = str(user.get("id") or user.get("userId", ""))
        if user_id not in _smoke_users:
            with Session(engine) as session:
                allowed, reason = check_and_consume_token(session, user_id)
            if not allowed:
                raise HTTPException(status_code=402, detail=reason)

    if intent.mode == IntentMode.CHAT:
        # --- Pure chat ---
        chat_svc = get_chat_service()
        if chat_svc is None:
            raise HTTPException(
                status_code=503,
                detail="Chat service not configured.",
            )

        if not message or not message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        if len(message) > 2000:
            raise HTTPException(status_code=400, detail="Message too long (max 2000 characters)")

        # Parse conversation history from JSON string
        history = []
        if conversation_history:
            try:
                history = json.loads(conversation_history)
            except json.JSONDecodeError:
                pass

        try:
            result = chat_svc.handle_chat(message, history)
        except Exception as e:
            logger.error("Chat error in /api/ask: %s", e)
            raise _friendly_api_error(e)
        return {
            "success": True,
            "mode": "chat",
            "response": result["response"],
            "sources": result["sources"],
            "usage": result.get("usage"),
        }

    elif intent.mode == IntentMode.ANALYSIS:
        # --- Trap analysis ---
        _has_figma_flow = bool(figma_url and figma_url.strip() and (input_type or '') == 'flow_diagram')
        if not files and not _has_figma_flow:
            raise HTTPException(status_code=400, detail="No files provided for analysis")

        if not intent.has_context:
            raise HTTPException(
                status_code=400,
                detail="Analysis requires context. Please provide users, tasks, and format descriptions.",
            )

        _task_list_parsed = []
        if task_list:
            try:
                _task_list_parsed = json.loads(task_list)
                if not isinstance(_task_list_parsed, list):
                    _task_list_parsed = []
            except (json.JSONDecodeError, TypeError):
                _task_list_parsed = []

        _input_type = input_type or 'screenshot'
        _is_flow_diagram = _input_type == 'flow_diagram'

        # ── Figma URL flow path ──────────────────────────────────────────────
        if _is_flow_diagram and figma_url and figma_url.strip():
            if not is_figma_available():
                raise HTTPException(
                    status_code=503,
                    detail="Figma analysis not available. FIGMA_TOKEN not configured."
                )
            try:
                with tempfile.TemporaryDirectory() as _tmp_dir:
                    _figma = FigmaAnalyzer()
                    _file_key, _ = _figma.parse_figma_url(figma_url.strip())
                    _cached = get_cached_figma_data(_file_key)
                    _figma_result = _figma.analyze_figma_file(
                        figma_url.strip(), _tmp_dir,
                        cached_file_data=_cached,
                        max_frames=10
                    )
                    _frames = _figma_result['frames']
                    _flows = _figma_result['flows']

                    from src.figma_analyzer import build_flow_map
                    _flow_map = build_flow_map(_frames, _flows)

                    _fctx = {
                        "users": users,
                        "tasks": tasks,
                        "format": format,
                        "content_type": content_type,
                        "extra_context": extra_context or "",
                        "product_context": product_context or "",
                        "physical_env": physical_env or "",
                        "lighting": lighting or "",
                        "grip_position": grip_position or "",
                        "attentional_state": attentional_state or "",
                        "tenet_filter": tenet_filter or "",
                        "design_name": design_name or "",
                        "task_list": _task_list_parsed,
                    }
                    _flow_analyzer = UITrapsAnalyzer()
                    _t0 = time.time()
                    _report_dict = _flow_analyzer.analyze_flow_diagram(
                        frames=_frames,
                        flow_map=_flow_map,
                        user_context=_fctx,
                        kb_version=kb_version,
                        verbosity=verbosity,
                        pass1_model=pass1_model,
                    )
                    _elapsed = time.time() - _t0
                    for _opt in ['critical_issues', 'moderate_issues', 'minor_issues',
                                 'positive_observations', 'potential_issues',
                                 'traps_checked_not_found', 'flagged_for_human_review',
                                 'incomplete_flow_findings']:
                        if not isinstance(_report_dict.get(_opt), list):
                            _report_dict[_opt] = []

                    _analysis_settings = {
                        'verbosity': verbosity,
                        'pass1_model': pass1_model,
                        'kb_version': kb_version,
                        'elapsed_seconds': _elapsed,
                        'thorough_mode': False,
                    }
                    _html = format_report_as_html(_report_dict, _fctx, analysis_settings=_analysis_settings)
                    _stats = get_report_statistics(_report_dict)

                    return {
                        "success": True,
                        "mode": "analysis",
                        "report_html": _html,
                        "statistics": _stats,
                        "kb_version": kb_version,
                    }
            except HTTPException:
                raise
            except Exception as _e:
                logger.error(f"Flow Figma analysis error: {_e}")
                _err_str = str(_e)
                if '401' in _err_str or 'Unauthorized' in _err_str:
                    raise HTTPException(
                        status_code=401,
                        detail="Figma access token has expired or is invalid. Please contact support."
                    )
                if '403' in _err_str or 'Forbidden' in _err_str.lower():
                    raise HTTPException(
                        status_code=403,
                        detail="This Figma file is private. In Figma, go to Share → set to 'Anyone with the link can view', then try again."
                    )
                if '404' in _err_str or 'Not Found' in _err_str:
                    raise HTTPException(
                        status_code=404,
                        detail="Figma file not found. Check that the link is correct and the file still exists."
                    )
                raise HTTPException(status_code=500, detail=f"Flow analysis failed: {_err_str}")

        # ── PDF path: convert pages to images, then route through normal pipeline ──
        _pdf_file = next(
            (f for f in files
             if f.content_type == 'application/pdf' or (f.filename or '').lower().endswith('.pdf')),
            None
        )
        if _pdf_file is not None:
            if not is_pymupdf_available():
                raise HTTPException(
                    status_code=503,
                    detail="PDF analysis is not available on this server. Please export your PDF pages as PNG or JPEG images and upload those instead."
                )
            _pdf_contents = await _pdf_file.read()
            if len(_pdf_contents) > 50 * 1024 * 1024:
                raise HTTPException(status_code=400, detail="PDF too large (max 50MB)")
            _pdf_tmp_path = None
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as _pdf_tmp:
                    _pdf_tmp.write(_pdf_contents)
                    _pdf_tmp_path = _pdf_tmp.name
                _pdf_analyzer_inst = PdfAnalyzer()
                with tempfile.TemporaryDirectory() as _pdf_img_dir:
                    _page_tuples = _pdf_analyzer_inst.convert_pages_to_images(
                        _pdf_tmp_path, output_dir=_pdf_img_dir, max_pages=20
                    )
                    _pdf_img_paths = [p for p, _ in _page_tuples]
                    if not _pdf_img_paths:
                        raise HTTPException(status_code=400, detail="No pages could be extracted from the PDF.")

                    user_context = {
                        "users": users, "tasks": tasks, "format": format,
                        "content_type": content_type,
                        "extra_context": extra_context or "",
                        "product_context": product_context or "",
                        "physical_env": physical_env or "",
                        "lighting": lighting or "",
                        "grip_position": grip_position or "",
                        "attentional_state": attentional_state or "",
                        "tenet_filter": tenet_filter or "",
                        "design_name": design_name or "",
                        "task_list": _task_list_parsed,
                        "input_type": _input_type,
                    }
                    user_id = str(user.get("id") or user.get("userId", ""))
                    logger.info(f"[/api/ask pdf] {len(_pdf_img_paths)} page(s) extracted from {_pdf_file.filename}")

                    if len(_pdf_img_paths) == 1:
                        result = get_analyzer().analyze_design(
                            design_file=_pdf_img_paths[0],
                            user_context=user_context,
                            chat_context=chat_context,
                            kb_version=kb_version,
                            verbosity=verbosity,
                            pass1_model=pass1_model,
                            thorough_mode=(thorough_mode == 'true'),
                        )
                        save_analysis_report(
                            analysis_result=result,
                            analysis_type="single_image",
                            user_context=user_context,
                            metadata={"file_name": _pdf_file.filename, "source": "pdf"},
                            user_id=user_id,
                        )
                        return {
                            "success": True,
                            "mode": "analysis",
                            "kb_version": kb_version,
                            "report_html": result.get("html"),
                            "report_markdown": result.get("markdown"),
                            "statistics": result.get("statistics"),
                        }
                    else:
                        result = get_multi_analyzer().analyze_images(
                            _pdf_img_paths, user_context, chat_context=chat_context
                        )
                        save_analysis_report(
                            analysis_result=result,
                            analysis_type="multi_image",
                            user_context=user_context,
                            metadata={"file_name": _pdf_file.filename, "source": "pdf", "page_count": len(_pdf_img_paths)},
                            user_id=user_id,
                        )
                        return {
                            "success": True,
                            "mode": "analysis",
                            "report_html": result.get("html"),
                            "report_markdown": result.get("markdown"),
                            "statistics": result.get("statistics"),
                        }
            except HTTPException:
                raise
            except Exception as _pdf_err:
                logger.error(f"[/api/ask pdf] error: {_pdf_err}\n{traceback.format_exc()}")
                raise _friendly_api_error(_pdf_err)
            finally:
                if _pdf_tmp_path:
                    try:
                        os.unlink(_pdf_tmp_path)
                    except Exception:
                        pass

        # Determine single vs multi image
        if len(files) == 1:
            image = files[0]
            if image.content_type not in ["image/png", "image/jpeg", "image/jpg"]:
                raise HTTPException(status_code=400, detail=f"Only PNG and JPEG supported. Got: {image.content_type}")

            contents = await image.read()
            if len(contents) > 10 * 1024 * 1024:
                raise HTTPException(status_code=400, detail="Image too large (max 10MB)")

            suffix = ".png" if image.content_type == "image/png" else ".jpg"
            try:
                logger.info(f"[/api/ask analysis] start — file={image.filename} size={len(contents)} kb_version={kb_version}")
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                    tmp.write(contents)
                    tmp_path = tmp.name
                logger.info(f"[/api/ask analysis] temp file written: {tmp_path}")

                user_context = {"users": users, "tasks": tasks, "format": format, "content_type": content_type, "extra_context": extra_context or "", "product_context": product_context or "", "physical_env": physical_env or "", "lighting": lighting or "", "grip_position": grip_position or "", "attentional_state": attentional_state or "", "tenet_filter": tenet_filter or "", "design_name": design_name or "", "task_list": _task_list_parsed, "input_type": _input_type}
                user_id = str(user.get("id") or user.get("userId", ""))

                if kb_version == "both":
                    loop = asyncio.get_running_loop()
                    analyzer_v2 = UITrapsAnalyzer()
                    analyzer_v1 = UITrapsAnalyzer()

                    logger.info("[/api/ask analysis] running dual analysis in parallel")
                    _thorough = thorough_mode == 'true'
                    result_v2, result_v1 = await asyncio.gather(
                        loop.run_in_executor(
                            None,
                            lambda: analyzer_v2.analyze_design(
                                design_file=tmp_path, user_context=user_context,
                                chat_context=chat_context, kb_version="v2",
                                verbosity=verbosity, pass1_model=pass1_model,
                                thorough_mode=_thorough,
                            )
                        ),
                        loop.run_in_executor(
                            None,
                            lambda: analyzer_v1.analyze_design(
                                design_file=tmp_path, user_context=user_context,
                                chat_context=chat_context, kb_version="v1",
                                verbosity=verbosity, pass1_model=pass1_model,
                                thorough_mode=_thorough,
                            )
                        ),
                    )
                    logger.info("[/api/ask analysis] dual analysis complete")

                    save_analysis_report(
                        analysis_result=result_v2,
                        analysis_type="single_image",
                        user_context=user_context,
                        metadata={"file_name": image.filename, "kb_version": "both"},
                        user_id=user_id
                    )
                    _save_report_db(user_id, result_v2, "single_image",
                                    design_name=design_name or "", file_name=image.filename)

                    return {
                        "success": True,
                        "mode": "analysis",
                        "kb_version": "both",
                        "report_html_v1": result_v1.get("html"),
                        "report_html_v2": result_v2.get("html"),
                        "report_markdown": result_v2.get("markdown"),
                        "statistics_v1": result_v1.get("statistics"),
                        "statistics_v2": result_v2.get("statistics"),
                    }
                else:
                    logger.info(f"[/api/ask analysis] calling analyze_design (kb_version={kb_version} verbosity={verbosity} pass1_model={pass1_model} thorough={thorough_mode})")
                    result = get_analyzer().analyze_design(
                        design_file=tmp_path, user_context=user_context,
                        chat_context=chat_context, kb_version=kb_version,
                        verbosity=verbosity, pass1_model=pass1_model,
                        thorough_mode=(thorough_mode == 'true'),
                    )
                    logger.info("[/api/ask analysis] analyze_design complete")

                    save_analysis_report(
                        analysis_result=result,
                        analysis_type="single_image",
                        user_context=user_context,
                        metadata={"file_name": image.filename},
                        user_id=user_id
                    )
                    _save_report_db(user_id, result, "single_image",
                                    design_name=design_name or "", file_name=image.filename)

                    return {
                        "success": True,
                        "mode": "analysis",
                        "kb_version": kb_version,
                        "report_html": result.get("html"),
                        "report_markdown": result.get("markdown"),
                        "statistics": result.get("statistics"),
                    }
            except Exception as e:
                logger.error(f"[/api/ask analysis] error: {e}\n{traceback.format_exc()}")
                raise _friendly_api_error(e)
            finally:
                try:
                    os.unlink(tmp_path)
                except Exception:
                    pass
        else:
            # Multi-image
            tmp_paths = []
            try:
                for img in files:
                    if img.content_type not in ["image/png", "image/jpeg", "image/jpg"]:
                        raise HTTPException(status_code=400, detail=f"Only PNG and JPEG supported. Got: {img.content_type}")
                    content = await img.read()
                    if len(content) > 10 * 1024 * 1024:
                        raise HTTPException(status_code=400, detail="Image too large (max 10MB)")
                    suffix = ".png" if img.content_type == "image/png" else ".jpg"
                    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                        tmp.write(content)
                        tmp_paths.append(tmp.name)

                user_context = {"users": users, "tasks": tasks, "format": format, "content_type": content_type, "extra_context": extra_context or "", "product_context": product_context or "", "physical_env": physical_env or "", "lighting": lighting or "", "grip_position": grip_position or "", "attentional_state": attentional_state or "", "tenet_filter": tenet_filter or "", "design_name": design_name or "", "task_list": _task_list_parsed, "input_type": _input_type}
                result = get_multi_analyzer().analyze_images(tmp_paths, user_context, chat_context=chat_context)

                user_id = str(user.get("id") or user.get("userId", ""))
                save_analysis_report(
                    analysis_result=result,
                    analysis_type="multi_image",
                    user_context=user_context,
                    metadata={"file_names": [f.filename for f in files]},
                    user_id=user_id
                )
                _save_report_db(user_id, result, "multi_image",
                                design_name=design_name or "",
                                file_name=", ".join(f.filename for f in files))

                return {
                    "success": True,
                    "mode": "analysis",
                    "report_html": result.get("html"),
                    "report_markdown": result.get("markdown"),
                    "statistics": result.get("statistics"),
                }
            finally:
                for path in tmp_paths:
                    try:
                        os.unlink(path)
                    except Exception:
                        pass

    elif intent.mode == IntentMode.HYBRID:
        # --- Hybrid: run analysis, then use result as context for chat ---
        if not files:
            raise HTTPException(status_code=400, detail="No files provided")

        # For hybrid, we do a basic analysis then answer the question using both
        # analysis results and RAG context
        image = files[0]
        if image.content_type not in ["image/png", "image/jpeg", "image/jpg"]:
            raise HTTPException(status_code=400, detail=f"Only PNG and JPEG supported. Got: {image.content_type}")

        contents = await image.read()
        if len(contents) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Image too large (max 10MB)")

        suffix = ".png" if image.content_type == "image/png" else ".jpg"
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(contents)
                tmp_path = tmp.name

            # Use generic context for hybrid mode
            user_context = {
                "users": users or "General users",
                "tasks": tasks or "General tasks",
                "format": format or "Website or application",
                "content_type": content_type,
            }
            result = get_analyzer().analyze_design(design_file=tmp_path, user_context=user_context)

            # If chat is available, also answer the question with RAG + analysis context
            chat_response = None
            sources = []
            chat_svc = get_chat_service()
            if chat_svc and message:
                try:
                    chat_result = chat_svc.handle_chat(message)
                    chat_response = chat_result["response"]
                    sources = chat_result["sources"]
                except Exception:
                    pass  # Chat failure shouldn't block the analysis result

            return {
                "success": True,
                "mode": "hybrid",
                "report_html": result.get("html"),
                "report_markdown": result.get("markdown"),
                "statistics": result.get("statistics"),
                "response": chat_response,
                "sources": sources,
            }
        finally:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass

    elif intent.mode == IntentMode.URL_ANALYSIS:
        # --- URL / website crawl analysis ---
        url = intent.message
        if not url:
            raise HTTPException(status_code=400, detail="No URL provided")

        if not is_playwright_available():
            raise HTTPException(
                status_code=503,
                detail="URL analysis not available. Playwright not installed. "
                       "Install with: pip install playwright && playwright install chromium"
            )

        max_pages = 5  # reasonable default for JWT-authenticated requests

        try:
            with tempfile.TemporaryDirectory() as tmp_dir:
                def run_crawl():
                    crawler = WebCrawler(
                        max_pages=max_pages,
                        max_depth=2,
                        viewport_width=1920,
                        viewport_height=1080,
                    )
                    crawl_result = crawler.crawl(url, tmp_dir)
                    return crawl_result, crawler.get_navigation_graph()

                loop = asyncio.get_running_loop()
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    crawl_result, navigation_graph = await loop.run_in_executor(executor, run_crawl)

                pages = crawl_result.get("pages", [])
                if not pages:
                    raise HTTPException(
                        status_code=400,
                        detail=(
                            f"No pages could be crawled from {url}. The site may be blocking "
                            "automated access, require authentication, or be unavailable."
                        )
                    )

                site_pages = []
                for page in pages:
                    if page.get("screenshot_path") and os.path.exists(page["screenshot_path"]):
                        site_pages.append({
                            "url": page["url"],
                            "title": page["title"],
                            "screenshot_path": page["screenshot_path"],
                            "screenshot_base64": page.get("screenshot_base64"),
                        })

                if not site_pages:
                    raise HTTPException(status_code=400, detail="No screenshots captured during crawl")

                user_context = {
                    "users": users or "General users",
                    "tasks": tasks or "General tasks",
                    "format": format or "Website",
                    "content_type": content_type,
                }

                site_analyzer = SiteAnalyzer()
                if navigation_graph:
                    site_analyzer.set_navigation_graph(navigation_graph)

                def run_analysis():
                    return site_analyzer.analyze_site(site_pages, user_context)

                with concurrent.futures.ThreadPoolExecutor() as executor:
                    result = await loop.run_in_executor(executor, run_analysis)

                from src.report_generator import generate_site_report
                html_report = generate_site_report(result, url)

                user_id = str(user.get("id") or user.get("userId", ""))
                save_analysis_report(
                    analysis_result={
                        "html": html_report,
                        "statistics": result.get("statistics"),
                        "site_summary": result.get("site_summary"),
                    },
                    analysis_type="url",
                    user_context=user_context,
                    metadata={"url": url, "pages_analyzed": len(site_pages)},
                    user_id=user_id
                )

                return {
                    "success": True,
                    "mode": "analysis",
                    "report_html": html_report,
                    "statistics": result.get("statistics"),
                }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"[/api/ask url_analysis] error: {e}\n{traceback.format_exc()}")
            raise _friendly_api_error(e)


# ===========================================================
# Report Chat Endpoint
# ===========================================================

class ReportChatRequest(BaseModel):
    message: str
    report_markdown: str
    conversation: list[dict] = []
    api_key: str


@app.post("/analyze/chat")
async def report_chat(request: ReportChatRequest):
    """
    Conversational Q&A about a completed analysis report.

    Accepts the report markdown + prior conversation + a new user message.
    Returns a grounded response without re-running analysis.
    Does not consume usage credits.
    """
    _dev_mode = os.environ.get("DEV_MODE", "false").lower() in ("true", "1", "yes")
    if not _dev_mode and request.api_key != "dev-mode":
        with Session(engine) as session:
            if not verify_api_key(request.api_key, session):
                raise HTTPException(status_code=403, detail="Invalid API key")

    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    if len(request.message) > 2000:
        raise HTTPException(status_code=400, detail="Message too long (max 2000 characters)")

    anthropic_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not anthropic_key:
        raise HTTPException(status_code=503, detail="AI service not configured")

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=anthropic_key)

        system_prompt = (
            "You are a UI/UX expert assistant helping a designer or researcher discuss their "
            "UI analysis report. The report was generated using the UI Tenets & Traps framework, "
            "which identifies specific usability patterns called 'traps'.\n\n"
            "Here is the analysis report:\n\n"
            "---\n"
            f"{request.report_markdown}\n"
            "---\n\n"
            "IMPORTANT — Re-run Analysis:\n"
            "There is a 'Re-run Analysis' button at the top of this chat panel. When the user "
            "clicks it, the ENTIRE conversation — including everything they have told you — is "
            "automatically passed to the analyzer as context. You do NOT need to tell the user "
            "to update any fields or re-enter anything manually.\n\n"
            "CRITICAL — NEVER attempt an inline re-analysis. You cannot see the original images "
            "and you cannot produce a structured report. If the user asks you to 're-run', "
            "'rerun', 'run it again', 'redo', 're-analyze', or uses any similar phrasing, "
            "do NOT generate a new analysis, do NOT describe what the findings would be, "
            "do NOT say 'Here is how the findings changed'. Instead, respond with exactly one "
            "short sentence: 'Click **Re-run Analysis** above and I'll apply this automatically.'\n\n"
            "When the user provides clarifying context that would change the analysis (e.g. "
            "'those users are adults', 'that modal is intentional', 'this is for kids'), "
            "acknowledge the clarification briefly, then say: "
            "'Click **Re-run Analysis** and I'll take this into account.' "
            "Do NOT tell them to update user context fields, re-enter descriptions, or go back "
            "to the main screen. Just point them to the button — everything else is automatic.\n\n"
            "Guidelines:\n"
            "- Answer questions about specific findings in the report\n"
            "- Explain what a trap means and why it was flagged\n"
            "- If the user provides context that changes the interpretation of a finding, "
            "acknowledge it and say: 'Click Re-run Analysis and I'll apply this new context.'\n"
            "- Be concise. One to three short paragraphs is usually enough.\n"
            "- Do not invent findings that are not in the report\n"
            "- Stay focused on the report and UI/UX topics"
        )

        messages = []
        for msg in request.conversation:
            role = msg.get("role", "")
            content = msg.get("content", "")
            if role in ("user", "assistant") and content:
                messages.append({"role": role, "content": content})
        messages.append({"role": "user", "content": request.message})

        model = os.environ.get("CHAT_AI_MODEL", "claude-haiku-4-5-20251001")
        response = client.messages.create(
            model=model,
            max_tokens=1024,
            system=system_prompt,
            messages=messages,
        )

        return {"success": True, "response": response.content[0].text}

    except Exception as e:
        logger.error(f"Report chat error: {e}")
        raise _friendly_api_error(e)


# --- Error Handlers ---

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail
        }
    )

# --- Run with Uvicorn ---

if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))

    print(f"Starting UITraps Unified Platform on port {port}")
    print(f"Allowed origins: {ALLOWED_ORIGINS}")
    print(f"Monthly limit: {MONTHLY_LIMIT} analyses per API key")
    print(f"Chat available: {get_chat_service() is not None}")

    if not VALID_API_KEYS:
        print("WARNING: No API keys configured. Running in development mode (all keys accepted).")

    uvicorn.run(app, host="0.0.0.0", port=port)
