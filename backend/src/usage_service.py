"""
Usage tracking service - replaces in-memory dict.

All database operations for usage tracking, API key management, and audit logging.
"""

import json
from datetime import datetime
from typing import Optional

from sqlmodel import Session, select

from src.database import APIKey, UsageRecord, AnalysisAudit


def get_current_month() -> str:
    """Get current month in YYYY-MM format."""
    return datetime.now().strftime("%Y-%m")


# --- API Key Operations ---

def get_or_create_api_key(session: Session, api_key: str, default_limit: int = 20) -> APIKey:
    """
    Get existing API key or create a new one.

    For backward compatibility with VALID_API_KEYS env var,
    auto-creates keys in the database when first seen.
    """
    statement = select(APIKey).where(APIKey.key == api_key)
    db_key = session.exec(statement).first()

    if not db_key:
        db_key = APIKey(key=api_key, monthly_limit=default_limit)
        session.add(db_key)
        session.commit()
        session.refresh(db_key)

    return db_key


def verify_api_key_db(session: Session, api_key: str, valid_keys: set) -> bool:
    """
    Verify API key is valid.

    Checks both database (is_active) and environment variable (VALID_API_KEYS).
    """
    # Development mode: no keys configured, allow all
    if not valid_keys:
        return True

    # Check env var first
    if api_key not in valid_keys:
        return False

    # Check if key exists and is active in DB
    db_key = session.exec(
        select(APIKey).where(APIKey.key == api_key)
    ).first()

    # If not in DB yet, it's valid (will be created on first use)
    if not db_key:
        return True

    return db_key.is_active


def get_monthly_limit(session: Session, api_key: str, default_limit: int) -> int:
    """Get monthly limit for an API key (supports tiered limits)."""
    db_key = session.exec(
        select(APIKey).where(APIKey.key == api_key)
    ).first()

    if db_key:
        return db_key.monthly_limit

    return default_limit


# --- Usage Operations ---

def get_usage(session: Session, api_key: str) -> int:
    """Get usage count for current month."""
    current_month = get_current_month()

    db_key = session.exec(
        select(APIKey).where(APIKey.key == api_key)
    ).first()

    if not db_key:
        return 0

    usage = session.exec(
        select(UsageRecord).where(
            UsageRecord.api_key_id == db_key.id,
            UsageRecord.month == current_month
        )
    ).first()

    return usage.count if usage else 0


def increment_usage(session: Session, api_key: str, amount: int = 1, default_limit: int = 20) -> int:
    """
    Increment usage count for current month.

    Returns the new count after incrementing.
    Auto-creates API key and usage record if needed.
    """
    current_month = get_current_month()

    # Get or create API key
    db_key = get_or_create_api_key(session, api_key, default_limit)

    # Get or create usage record
    usage = session.exec(
        select(UsageRecord).where(
            UsageRecord.api_key_id == db_key.id,
            UsageRecord.month == current_month
        )
    ).first()

    if usage:
        usage.count += amount
        usage.updated_at = datetime.utcnow()
    else:
        usage = UsageRecord(
            api_key_id=db_key.id,
            month=current_month,
            count=amount
        )
        session.add(usage)

    session.commit()
    session.refresh(usage)

    return usage.count


# --- Audit Operations ---

def log_analysis(
    session: Session,
    api_key: str,
    endpoint: str,
    analysis_type: str,
    credits_used: int,
    status: str = "success",
    metadata: Optional[dict] = None
):
    """Log an analysis request to the audit trail."""
    db_key = session.exec(
        select(APIKey).where(APIKey.key == api_key)
    ).first()

    if not db_key:
        # Should not happen in normal flow, but handle gracefully
        db_key = get_or_create_api_key(session, api_key)

    audit = AnalysisAudit(
        api_key_id=db_key.id,
        endpoint=endpoint,
        analysis_type=analysis_type,
        credits_used=credits_used,
        status=status,
        request_metadata=json.dumps(metadata) if metadata else None
    )
    session.add(audit)
    session.commit()
