"""
UITraps Unified Platform - Web API

Combines UI Traps analysis (image/video) and RAG chat into a single API.
Existing endpoints (/analyze, /analyze-multi, /analyze-video) unchanged.
New endpoints (/api/chat, /api/ask) use JWT auth for the unified experience.

Copyright © 2009-present UI Traps LLC. All Rights Reserved.
"""

import os
import json
import logging
import tempfile
import time
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

# Database persistence for usage tracking
from sqlmodel import Session
from src.database import init_db, engine
from src.usage_service import (
    get_usage,
    increment_usage,
    get_monthly_limit,
    verify_api_key_db,
    log_analysis,
    get_current_month
)

# NEW: JWT auth for unified platform
from src.auth import get_current_user

# NEW: RAG chat pipeline
from src.chat.pinecone_service import PineconeService
from src.chat.ai_service import ChatAIService
from src.chat.chat_service import ChatService

# NEW: Intent router for unified endpoint
from src.router import detect_intent, IntentMode

logger = logging.getLogger(__name__)

# --- Configuration ---

# Allowed origins for CORS (update with your domain)
ALLOWED_ORIGINS = os.environ.get(
    "ALLOWED_ORIGINS",
    "https://uitraps.com,https://www.uitraps.com,http://localhost:3000,http://localhost:5173,http://127.0.0.1:5173"
).split(",")

# Monthly analysis limit per API key
MONTHLY_LIMIT = int(os.environ.get("MONTHLY_LIMIT", "20"))

# --- Initialize Database ---
init_db()  # Create tables if they don't exist

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

# CORS middleware - allows your website to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

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
    """Get or create chat service instance. Returns None if not configured."""
    global _chat_service
    if _chat_service is None:
        pinecone_key = os.environ.get("PINECONE_API_KEY", "")
        openai_key = os.environ.get("OPENAI_API_KEY", "")
        anthropic_key = os.environ.get("ANTHROPIC_API_KEY", "")
        index_name = os.environ.get("PINECONE_INDEX_NAME", "")

        if not all([pinecone_key, openai_key, anthropic_key, index_name]):
            return None  # Chat not configured yet

        pinecone_svc = PineconeService(
            pinecone_api_key=pinecone_key,
            index_name=index_name,
            openai_api_key=openai_key,
            top_k=int(os.environ.get("PINECONE_TOP_K", "5")),
        )
        ai_svc = ChatAIService(
            anthropic_api_key=anthropic_key,
            model=os.environ.get("CHAT_AI_MODEL", "claude-sonnet-4-5-20250929"),
            max_tokens=int(os.environ.get("CHAT_MAX_TOKENS", "1024")),
            temperature=float(os.environ.get("CHAT_TEMPERATURE", "0.7")),
        )
        _chat_service = ChatService(pinecone_svc, ai_svc)
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
    # Analysis fields
    report_html: Optional[str] = None
    report_markdown: Optional[str] = None
    statistics: Optional[dict] = None
    usage: Optional[dict] = None
    error: Optional[str] = None


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
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(contents)
                tmp_path = tmp.name

            # 6. Build user context
            user_context = {
                "users": users,
                "tasks": tasks,
                "format": format,
                "content_type": content_type
            }

            # 7. Run analysis
            analyzer_instance = get_analyzer()
            result = analyzer_instance.analyze_design(
                design_file=tmp_path,
                user_context=user_context
            )

            # 8. Increment usage after successful analysis
            new_usage = increment_usage(session, api_key, 1, MONTHLY_LIMIT)
            log_analysis(session, api_key, "/analyze", "single_image", 1, "success")

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
            # Unexpected errors
            raise HTTPException(
                status_code=500,
                detail=f"Analysis failed: {str(e)}"
            )

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
        "max_images": EstimationConstants.MAX_IMAGES,
        "max_video_frames": EstimationConstants.MAX_VIDEO_FRAMES,
        "max_image_size_mb": 10,
        "max_video_size_mb": 100,
        "supported_image_types": ["image/png", "image/jpeg"],
        "supported_video_types": ["video/mp4", "video/quicktime", "video/webm"]
    }


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
            detail="Chat service not configured. Missing PINECONE_API_KEY, OPENAI_API_KEY, or PINECONE_INDEX_NAME.",
        )

    try:
        result = chat_svc.handle_chat(
            request.message, request.conversationHistory
        )
        return result
    except Exception as e:
        error_msg = str(e)
        if "rate limit" in error_msg.lower():
            raise HTTPException(
                status_code=429,
                detail="AI service rate limit reached. Please try again in a moment.",
            )
        if "pinecone" in error_msg.lower():
            raise HTTPException(
                status_code=503,
                detail="Content search temporarily unavailable. Please try again.",
            )
        logger.error("Chat error: %s", error_msg)
        raise HTTPException(
            status_code=500, detail="Failed to generate response. Please try again."
        )


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
):
    """
    Unified endpoint: auto-routes to analysis, chat, or hybrid based on input.

    - Text only → RAG chat
    - Files + context → Trap analysis
    - Files + question (no context) → Hybrid
    """
    intent = detect_intent(message, files, users, tasks, format)

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

        result = chat_svc.handle_chat(message, history)
        return {
            "success": True,
            "mode": "chat",
            "response": result["response"],
            "sources": result["sources"],
            "usage": result.get("usage"),
        }

    elif intent.mode == IntentMode.ANALYSIS:
        # --- Trap analysis ---
        if not files:
            raise HTTPException(status_code=400, detail="No files provided for analysis")

        if not intent.has_context:
            raise HTTPException(
                status_code=400,
                detail="Analysis requires context. Please provide users, tasks, and format descriptions (at least 10 characters each).",
            )

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
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                    tmp.write(contents)
                    tmp_path = tmp.name

                user_context = {"users": users, "tasks": tasks, "format": format, "content_type": content_type}
                result = get_analyzer().analyze_design(design_file=tmp_path, user_context=user_context)

                return {
                    "success": True,
                    "mode": "analysis",
                    "report_html": result.get("html"),
                    "report_markdown": result.get("markdown"),
                    "statistics": result.get("statistics"),
                }
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

                user_context = {"users": users, "tasks": tasks, "format": format, "content_type": content_type}
                result = get_multi_analyzer().analyze_images(tmp_paths, user_context)

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
