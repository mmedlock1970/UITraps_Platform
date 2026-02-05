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

    # Check subscription claim (matching Node.js auth.js line 29)
    if not payload.get("hasActiveSubscription"):
        raise HTTPException(
            status_code=403,
            detail="Active subscription required",
        )

    return {
        "id": payload.get("userId"),
        "hasActiveSubscription": True,
    }
