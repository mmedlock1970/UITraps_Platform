"""
FastAPI authentication dependencies.

Provides get_current_user() as a Depends() injectable that verifies
JWT tokens from the Authorization header.

Port of: Traps Chat/backend-api/src/middleware/auth.js (verifyToken)
"""

import os
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .jwt_handler import decode_wordpress_jwt

security = HTTPBearer(auto_error=False)

_jwt_secret = None


def _get_jwt_secret() -> str:
    global _jwt_secret
    if _jwt_secret is None:
        _jwt_secret = os.environ.get("JWT_SECRET", "")
        if len(_jwt_secret) < 32:
            raise RuntimeError(
                "JWT_SECRET must be at least 32 characters. "
                "Set it in your .env file to match WordPress wp-config.php."
            )
    return _jwt_secret


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    FastAPI dependency: extracts and validates JWT from Authorization header.

    Returns:
        dict with "id" (WordPress user ID) and "hasActiveSubscription" (bool)

    Raises:
        HTTPException 401: Missing, expired, or invalid token
        HTTPException 403: User does not have active subscription
    """
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid authorization header",
        )

    token = credentials.credentials

    # Dev mode: skip JWT validation for local testing
    if token == "dev-mode":
        dev_mode = os.environ.get("DEV_MODE", "false").lower() in ("true", "1", "yes")
        if dev_mode:
            return {"id": "dev-user", "hasActiveSubscription": True}
        raise HTTPException(
            status_code=401,
            detail="Dev mode not enabled on server. Set DEV_MODE=true in .env",
        )

    secret = _get_jwt_secret()

    try:
        payload = decode_wordpress_jwt(token, secret)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token expired",
            headers={"X-Error-Code": "TOKEN_EXPIRED"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
            headers={"X-Error-Code": "INVALID_TOKEN"},
        )

    # The JWT's hasActiveSubscription is a point-in-time snapshot minted by WordPress; it goes stale
    # when the subscription changes AFTER the token was issued (e.g. expire → re-activate). Before
    # rejecting, fall back to the live, webhook-synced DB status — the subscription webhook is our
    # source of truth — so a stale "inactive" claim can't lock out an actually-active user. The DB is
    # only ever written by the authenticated webhook, so trusting a DB "active" over the claim is safe.
    active = bool(payload.get("hasActiveSubscription")) or _live_subscription_active(payload.get("userId"))
    if not active:
        raise HTTPException(
            status_code=403,
            detail="Active subscription required",
        )

    return {
        "id": payload.get("userId"),
        "hasActiveSubscription": True,
    }


def _live_subscription_active(user_id) -> bool:
    """True if the webhook-synced DB shows an active (or cancelled-but-in-period) subscription.

    Read-only. On any DB error returns False so auth degrades to the JWT claim rather than crashing.
    """
    if not user_id:
        return False
    try:
        from sqlmodel import Session
        from ..database import engine
        from ..subscription_service import get_subscription_status
        with Session(engine) as session:
            return get_subscription_status(session, str(user_id)) in ("active", "cancelled")
    except Exception:
        return False
