"""
Database models and connection management for usage tracking.

Uses SQLModel (Pydantic + SQLAlchemy) for type-safe database operations.
"""

import os
from datetime import datetime
from typing import Optional
from pathlib import Path

from sqlmodel import Field, SQLModel, Session, create_engine
from sqlalchemy import UniqueConstraint, text


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


# --- Subscription & Token Models ---

class UserSubscription(SQLModel, table=True):
    """Per-user subscription status and token balance, keyed by WordPress user ID."""
    __tablename__ = "user_subscriptions"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(unique=True, index=True)  # WordPress user ID (from JWT)
    subscription_status: str = Field(default="inactive")  # active | cancelled | expired | inactive
    monthly_limit: int = Field(default=0)
    monthly_used: int = Field(default=0)
    bonus_tokens: int = Field(default=0)
    subscription_start: Optional[datetime] = Field(default=None)
    subscription_end: Optional[datetime] = Field(default=None)
    next_renewal: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# --- Analysis Report Storage ---

class AnalysisReport(SQLModel, table=True):
    """Persisted analysis reports, keyed by WordPress user ID."""
    __tablename__ = "analysis_reports"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)
    analysis_type: str = Field(default="single_image")
    design_name: Optional[str] = None
    file_name: Optional[str] = None
    html: str = Field(sa_column_kwargs={"nullable": False})
    markdown: Optional[str] = None
    statistics: Optional[str] = None  # JSON string


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

# Whether DATABASE_URL was explicitly provided. When it wasn't, we fall back to a
# local SQLite file — fine for local dev, but on a deployed host that file is
# throwaway and it silently masks a missing DATABASE_URL (see check at startup).
DATABASE_URL_FROM_ENV = "DATABASE_URL" in os.environ

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    f"sqlite:///{Path(__file__).parent.parent / 'usage.db'}"
)

# Railway provides postgres:// but SQLAlchemy requires postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# SQLite needs check_same_thread=False; PostgreSQL does not accept that arg
_is_sqlite = DATABASE_URL.startswith("sqlite")
engine = create_engine(
    DATABASE_URL,
    echo=os.environ.get("DEBUG_SQL", "").lower() == "true",
    **( {"connect_args": {"check_same_thread": False}} if _is_sqlite else {} )
)


def is_using_fallback_sqlite() -> bool:
    """True when we fell back to the local SQLite file because DATABASE_URL was unset."""
    return _is_sqlite and not DATABASE_URL_FROM_ENV


def check_db_connection() -> tuple[bool, Optional[str]]:
    """Confirm the database is actually reachable with a trivial query.

    Returns (ok, error_message); error_message is None when ok is True.
    Use this instead of assuming the engine is usable — creating the engine
    never opens a connection, so a bad DATABASE_URL looks fine until first use.
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True, None
    except Exception as e:
        return False, str(e)


def init_db():
    """Create all tables. Safe to call multiple times."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Get a database session. Use as dependency or context manager."""
    with Session(engine) as session:
        yield session
