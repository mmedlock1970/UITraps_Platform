"""
The subscription gate (get_current_user) must authorize against the live, webhook-synced DB, not
only the JWT's point-in-time `hasActiveSubscription` claim.

Regression: a user who expired then RE-ACTIVATED still carries a stale "inactive" claim in a token
minted while expired. The DB (updated by the subscription webhook) says active, so the gate must
allow them — otherwise form submission and /api/user/usage 403 with "Active subscription required"
while /usage (which reads the DB directly) correctly shows the active subscription.
"""
import asyncio

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

import src.auth.dependencies as deps


def _call(token="tok"):
    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
    return asyncio.run(deps.get_current_user(credentials=creds))


def _stub_jwt(monkeypatch, *, has_active: bool, user_id="106"):
    monkeypatch.setattr(deps, "_get_jwt_secret", lambda: "x" * 32)
    monkeypatch.setattr(
        deps, "decode_wordpress_jwt",
        lambda t, s: {"userId": user_id, "hasActiveSubscription": has_active},
    )


def test_stale_inactive_claim_allowed_when_db_active(monkeypatch):
    _stub_jwt(monkeypatch, has_active=False)
    monkeypatch.setattr(deps, "_live_subscription_active", lambda uid: True)
    user = _call()
    assert user["id"] == "106" and user["hasActiveSubscription"] is True


def test_inactive_claim_and_inactive_db_still_rejected(monkeypatch):
    _stub_jwt(monkeypatch, has_active=False)
    monkeypatch.setattr(deps, "_live_subscription_active", lambda uid: False)
    with pytest.raises(HTTPException) as ei:
        _call()
    assert ei.value.status_code == 403
    assert ei.value.detail == "Active subscription required"


def test_active_claim_short_circuits_without_db(monkeypatch):
    # Happy path: an active claim must NOT trigger a DB lookup (no extra query per request).
    _stub_jwt(monkeypatch, has_active=True)

    def _boom(uid):
        raise AssertionError("DB must not be consulted when the JWT claim is already active")

    monkeypatch.setattr(deps, "_live_subscription_active", _boom)
    user = _call()
    assert user["id"] == "106"
