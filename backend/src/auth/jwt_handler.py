"""
JWT token handler for WordPress-issued tokens.

Port of: Traps Chat/backend-api/src/middleware/auth.js
Token format: HS256, payload contains userId and hasActiveSubscription.
"""

import jwt


def decode_wordpress_jwt(token: str, secret: str) -> dict:
    """
    Decode and validate a WordPress-issued JWT.

    Args:
        token: The JWT string (without 'Bearer ' prefix)
        secret: The shared secret (must match WordPress wp-config.php JWT_SECRET)

    Returns:
        Decoded payload dict with userId, hasActiveSubscription, iat, exp

    Raises:
        jwt.ExpiredSignatureError: Token has expired
        jwt.InvalidTokenError: Token is malformed or signature invalid
    """
    payload = jwt.decode(token, secret, algorithms=["HS256"])
    return payload
