"""
Subscription and token management service.

Handles WooCommerce webhook events for subscription lifecycle and token top-ups.
Users are identified by their WordPress user ID (from JWT payload).
"""

from datetime import datetime
from typing import Optional

from sqlmodel import Session, select

from src.database import UserSubscription


def get_or_create_subscription(session: Session, user_id: str) -> UserSubscription:
    """Get existing subscription record or create a blank one."""
    sub = session.exec(
        select(UserSubscription).where(UserSubscription.user_id == user_id)
    ).first()

    if not sub:
        sub = UserSubscription(user_id=user_id)
        session.add(sub)
        session.commit()
        session.refresh(sub)

    return sub


def activate_subscription(
    session: Session,
    user_id: str,
    monthly_limit: int,
    subscription_start: Optional[str] = None,
    subscription_end: Optional[str] = None,
    next_renewal: Optional[str] = None,
) -> UserSubscription:
    """Activate or reactivate a subscription. Resets monthly usage."""
    sub = get_or_create_subscription(session, user_id)

    sub.subscription_status = "active"
    sub.monthly_limit = monthly_limit
    sub.monthly_used = 0
    sub.updated_at = datetime.utcnow()

    if subscription_start:
        sub.subscription_start = datetime.fromisoformat(subscription_start)
    if subscription_end:
        sub.subscription_end = datetime.fromisoformat(subscription_end)
    if next_renewal:
        sub.next_renewal = datetime.fromisoformat(next_renewal)

    session.add(sub)
    session.commit()
    session.refresh(sub)
    return sub


def renew_subscription(
    session: Session,
    user_id: str,
    monthly_limit: Optional[int] = None,
    next_renewal: Optional[str] = None,
    subscription_end: Optional[str] = None,
) -> UserSubscription:
    """Renew subscription — resets monthly usage, updates dates."""
    sub = get_or_create_subscription(session, user_id)

    sub.subscription_status = "active"
    sub.monthly_used = 0
    sub.updated_at = datetime.utcnow()

    if monthly_limit is not None:
        sub.monthly_limit = monthly_limit
    if next_renewal:
        sub.next_renewal = datetime.fromisoformat(next_renewal)
    if subscription_end:
        sub.subscription_end = datetime.fromisoformat(subscription_end)

    session.add(sub)
    session.commit()
    session.refresh(sub)
    return sub


def cancel_subscription(session: Session, user_id: str) -> UserSubscription:
    """Cancel subscription — user loses access at period end."""
    sub = get_or_create_subscription(session, user_id)
    sub.subscription_status = "cancelled"
    sub.updated_at = datetime.utcnow()
    session.add(sub)
    session.commit()
    session.refresh(sub)
    return sub


def expire_subscription(session: Session, user_id: str) -> UserSubscription:
    """Expire subscription — access fully revoked."""
    sub = get_or_create_subscription(session, user_id)
    sub.subscription_status = "expired"
    sub.updated_at = datetime.utcnow()
    session.add(sub)
    session.commit()
    session.refresh(sub)
    return sub


def add_bonus_tokens(session: Session, user_id: str, tokens: int) -> UserSubscription:
    """Add purchased bonus tokens to user's balance."""
    sub = get_or_create_subscription(session, user_id)
    sub.bonus_tokens += tokens
    sub.updated_at = datetime.utcnow()
    session.add(sub)
    session.commit()
    session.refresh(sub)
    return sub


def check_and_consume_token(session: Session, user_id: str) -> tuple[bool, str]:
    """
    Check if user can run an analysis and consume one token if so.

    Returns (allowed: bool, reason: str).
    Draws from monthly allowance first, then bonus tokens.
    """
    sub = session.exec(
        select(UserSubscription).where(UserSubscription.user_id == user_id)
    ).first()

    if not sub:
        return False, "No active subscription found."

    if sub.subscription_status not in ("active", "cancelled"):
        return False, "Your subscription is not active. Please renew to continue."

    # Monthly allowance available
    if sub.monthly_used < sub.monthly_limit:
        sub.monthly_used += 1
        sub.updated_at = datetime.utcnow()
        session.add(sub)
        session.commit()
        return True, "ok"

    # Fall back to bonus tokens
    if sub.bonus_tokens > 0:
        sub.bonus_tokens -= 1
        sub.updated_at = datetime.utcnow()
        session.add(sub)
        session.commit()
        return True, "ok"

    return False, (
        f"Monthly limit reached ({sub.monthly_limit} analyses). "
        "Purchase additional tokens or wait for your subscription to renew."
    )


def get_subscription_status(session: Session, user_id: str) -> Optional[str]:
    """Return the stored subscription_status for a user, or None if no record exists.

    Read-only (never creates a row). Used by the auth gate to authorize against the
    live, webhook-synced DB rather than a point-in-time JWT claim.
    """
    sub = session.exec(
        select(UserSubscription).where(UserSubscription.user_id == user_id)
    ).first()
    return sub.subscription_status if sub else None


def get_usage_summary(session: Session, user_id: str) -> dict:
    """Return a usage summary for the user."""
    sub = session.exec(
        select(UserSubscription).where(UserSubscription.user_id == user_id)
    ).first()

    if not sub:
        return {
            "subscription_status": "inactive",
            "monthly_limit": 0,
            "monthly_used": 0,
            "monthly_remaining": 0,
            "bonus_tokens": 0,
        }

    return {
        "subscription_status": sub.subscription_status,
        "monthly_limit": sub.monthly_limit,
        "monthly_used": sub.monthly_used,
        "monthly_remaining": max(0, sub.monthly_limit - sub.monthly_used),
        "bonus_tokens": sub.bonus_tokens,
        "next_renewal": sub.next_renewal.isoformat() if sub.next_renewal else None,
        "subscription_end": sub.subscription_end.isoformat() if sub.subscription_end else None,
    }
