"""
Database models and connection management for usage tracking.

Uses SQLModel (Pydantic + SQLAlchemy) for type-safe database operations.
"""

import os
from datetime import datetime
from typing import Optional
from pathlib import Path

from sqlmodel import Field, SQLModel, Session, create_engine
from sqlalchemy import UniqueConstraint


# --- Models ---

class APIKey(SQLModel, table=True):
    """API key with tier-based limits."""
    __tablename__ = "api_keys"

    id: Optional[int] = Field(default=None, primary_key=True)
    key: str = Field(unique=True, index=True)
    tier: str = Field(default="basic")
    monthly_limit: int = Field(default=20)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class UsageRecord(SQLModel, table=True):
    """Monthly usage count per API key."""
    __tablename__ = "usage_records"
    __table_args__ = (
        UniqueConstraint("api_key_id", "month", name="unique_key_month"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    api_key_id: int = Field(foreign_key="api_keys.id", index=True)
    month: str = Field(index=True)  # Format: YYYY-MM
    count: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class AnalysisAudit(SQLModel, table=True):
    """Audit trail for all analysis requests."""
    __tablename__ = "analysis_audit"

    id: Optional[int] = Field(default=None, primary_key=True)
    api_key_id: int = Field(foreign_key="api_keys.id", index=True)
    endpoint: str
    analysis_type: Optional[str] = None
    credits_used: int = Field(default=1)
    status: str = Field(default="success")
    request_metadata: Optional[str] = None  # JSON string
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)


# --- Chat Models (for unified platform) ---

class ConversationSession(SQLModel, table=True):
    """Track conversation sessions for follow-up context."""
    __tablename__ = "conversation_sessions"

    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: str = Field(unique=True, index=True)
    user_id: int = Field(index=True)  # From JWT payload
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_analysis_summary: Optional[str] = None  # JSON string of last analysis


class ChatMessageRecord(SQLModel, table=True):
    """Individual messages within a conversation."""
    __tablename__ = "chat_messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: str = Field(index=True)
    role: str  # "user" | "assistant"
    content: str
    mode: Optional[str] = None  # "analysis" | "chat" | "hybrid"
    sources: Optional[str] = None  # JSON array of source URLs
    created_at: datetime = Field(default_factory=datetime.utcnow)


# --- Database Connection ---

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    f"sqlite:///{Path(__file__).parent.parent / 'usage.db'}"
)

# SQLite-specific settings for concurrency
engine = create_engine(
    DATABASE_URL,
    echo=os.environ.get("DEBUG_SQL", "").lower() == "true",
    connect_args={"check_same_thread": False}  # Required for SQLite + FastAPI
)


def init_db():
    """Create all tables. Safe to call multiple times."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Get a database session. Use as dependency or context manager."""
    with Session(engine) as session:
        yield session
