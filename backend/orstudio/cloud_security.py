from __future__ import annotations

import hashlib
import hmac
import os
import secrets
from datetime import datetime, timezone
from typing import Any

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError
from fastapi import Depends, HTTPException, Request

from . import cloud_store

COOKIE_NAME = "ors_session"
SESSION_TTL_HOURS = 24 * 14
GUEST_TTL_HOURS = 24
_password_hasher = PasswordHasher(time_cost=3, memory_cost=65536, parallelism=2)


def hash_password(password: str) -> str:
    return _password_hasher.hash(password)


def verify_password(password_hash: str, password: str) -> bool:
    try:
        return _password_hasher.verify(password_hash, password)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False


def new_session(principal_id: str, guest: bool = False) -> str:
    token = secrets.token_urlsafe(48)
    cloud_store.create_session(token_hash(token), principal_id, GUEST_TTL_HOURS if guest else SESSION_TTL_HOURS)
    return token


def token_hash(token: str) -> str:
    pepper = os.getenv("ORS_SESSION_SECRET", "development-only-session-pepper").encode("utf-8")
    return hmac.new(pepper, token.encode("utf-8"), hashlib.sha256).hexdigest()


def current_principal_optional(request: Request) -> dict[str, Any] | None:
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return None
    principal = cloud_store.get_principal_by_session(token_hash(token))
    if principal and principal.get("kind") == "GUEST":
        expiry = principal.get("expires_at")
        if expiry and expiry.tzinfo is None:
            expiry = expiry.replace(tzinfo=timezone.utc)
        if expiry and expiry < datetime.now(timezone.utc):
            cloud_store.delete_session(token_hash(token))
            return None
    if principal:
        principal.pop("password_hash", None)
    return principal


def require_principal(principal=Depends(current_principal_optional)) -> dict[str, Any]:
    if not principal:
        raise HTTPException(status_code=401, detail="Session expired. Continue as guest or sign in again.")
    return principal


def set_session_cookie(response, token: str, secure: bool, guest: bool = False) -> None:
    ttl_hours = GUEST_TTL_HOURS if guest else SESSION_TTL_HOURS
    response.set_cookie(
        COOKIE_NAME, token, max_age=ttl_hours * 3600,
        httponly=True, secure=secure, samesite="lax", path="/",
    )


def clear_session_cookie(response, secure: bool) -> None:
    response.delete_cookie(COOKIE_NAME, path="/", secure=secure, httponly=True, samesite="lax")
