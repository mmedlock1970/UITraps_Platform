"""
Subscription and token management service.

Handles WooCommerce webhook events for subscription lifecycle and token top-ups.
Users are identified by their WordPress user ID (from JWT payload).
"""

import calendar
from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Session, select

from src.database import UserSubscription


def _parse_iso_utc(value: Optional[str]) -> Optional[datetime]:
    """Parse a WooCommerce ISO 8601 timestamp into a timezone-aware UTC datetime.

    The user_subscriptions datetime columns are timestamptz, so stored values must be
    tz-aware. Handles a trailing 'Z' (e.g. "2026-10-02T18:19:21Z") on every Python version,
    and treats a naive string as UTC. Returns None for an empty value.
    """
    if not value:
        return None
    s = value.strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    dt = datetime.fromisoformat(s)
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def _month_period_start(now: datetime, anchor_day: int) -> datetime:
    """UTC-midnight start of the current monthly allowance period for a given anchor day-of-month.
    Clamps the anchor to the last day of short months (e.g. day 31 -> Feb 28/29)."""
    def at(year: int, month: int) -> datetime:
        day = min(anchor_day, calendar.monthrange(year, month)[1])
        return datetime(year, month, day, tzinfo=timezone.utc)
    this_month = at(now.year, now.month)
    if now >= this_month:
        return this_month
    py, pm = (now.year - 1, 12) if now.month == 1 else (now.year, now.month - 1)
    return at(py, pm)


def _apply_monthly_reset(session: Session, sub: UserSubscription) -> None:
    """Reset monthly_used at the start of each monthly allowance period, for ALL plans — annual
    included, whose renewal webhook fires only yearly. Lazy (no scheduler): called on every
    read/consume. Purchased bonus_tokens are left untouched (they roll over)."""
    anchor = sub.subscription_start or sub.created_at
    if anchor is None:
        return
    if anchor.tzinfo is None:
        anchor = anchor.replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    period_start = _month_period_start(now, anchor.day)
    last_reset = sub.monthly_reset_at
    if last_reset is not None and last_reset.tzinfo is None:
        last_reset = last_reset.replace(tzinfo=timezone.utc)
    if last_reset is None:
        # First encounter (e.g. right after the column is added): anchor to the current period
        # WITHOUT zeroing usage, so no spurious free reset is handed out on deploy.
        sub.monthly_reset_at = period_start
    elif last_reset < period_start:
        sub.monthly_used = 0
        sub.monthly_reset_at = period_start
    else:
        return
    sub.updated_at = now
    session.add(sub)
    session.commit()
    session.refresh(sub)


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
    sub.monthly_reset_at = datetime.now(timezone.utc)
    sub.updated_at = sub.monthly_reset_at

    if subscription_start:
        sub.subscription_start = _parse_iso_utc(subscription_start)
    if subscription_end:
        sub.subscription_end = _parse_iso_utc(subscription_end)
    if next_renewal:
        sub.next_renewal = _parse_iso_utc(next_renewal)

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
    sub.monthly_reset_at = datetime.now(timezone.utc)
    sub.updated_at = sub.monthly_reset_at

    if monthly_limit is not None:
        sub.monthly_limit = monthly_limit
    if next_renewal:
        sub.next_renewal = _parse_iso_utc(next_renewal)
    if subscription_end:
        sub.subscription_end = _parse_iso_utc(subscription_end)

    session.add(sub)
    session.commit()
    session.refresh(sub)
    return sub


def cancel_subscription(session: Session, user_id: str) -> UserSubscription:
    """Cancel subscription — user loses access at period end."""
    sub = get_or_create_subscription(session, user_id)
    sub.subscription_status = "cancelled"
    sub.updated_at = datetime.now(timezone.utc)
    session.add(sub)
    session.commit()
    session.refresh(sub)
    return sub


def expire_subscription(session: Session, user_id: str) -> UserSubscription:
    """Expire subscription — access fully revoked."""
    sub = get_or_create_subscription(session, user_id)
    sub.subscription_status = "expired"
    sub.updated_at = datetime.now(timezone.utc)
    session.add(sub)
    session.commit()
    session.refresh(sub)
    return sub


def add_bonus_tokens(session: Session, user_id: str, tokens: int) -> UserSubscription:
    """Add purchased bonus tokens to user's balance."""
    sub = get_or_create_subscription(session, user_id)
    sub.bonus_tokens += tokens
    sub.updated_at = datetime.now(timezone.utc)
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

    _apply_monthly_reset(session, sub)

    if sub.subscription_status not in ("active", "cancelled"):
        return False, "Your subscription is not active. Please renew to continue."

    # Monthly allowance available
    if sub.monthly_used < sub.monthly_limit:
        sub.monthly_used += 1
        sub.updated_at = datetime.now(timezone.utc)
        session.add(sub)
        session.commit()
        return True, "ok"

    # Fall back to bonus tokens
    if sub.bonus_tokens > 0:
        sub.bonus_tokens -= 1
        sub.updated_at = datetime.now(timezone.utc)
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

    _apply_monthly_reset(session, sub)

    return {
        "subscription_status": sub.subscription_status,
        "monthly_limit": sub.monthly_limit,
        "monthly_used": sub.monthly_used,
        "monthly_remaining": max(0, sub.monthly_limit - sub.monthly_used),
        "bonus_tokens": sub.bonus_tokens,
        "next_renewal": sub.next_renewal.isoformat() if sub.next_renewal else None,
        "subscription_end": sub.subscription_end.isoformat() if sub.subscription_end else None,
    }
