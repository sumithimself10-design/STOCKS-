"""
Minimal write-protection for the simulator, not a full auth system.

If SIMULATOR_API_KEY is unset (local dev default), every request passes —
convenient for development, unacceptable for production. Set the env var
before deploying, and give the value only to yourself/your frontend build
via NEXT_PUBLIC_SIMULATOR_API_KEY. This is a shared-secret gate, not
per-user auth — good enough for a personal or capstone deployment where
you're the only real writer; swap for real session-based auth before
opening this up to other people's simulator data.
"""
from fastapi import Header, HTTPException

from core.config import get_settings

settings = get_settings()


async def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    if not settings.simulator_api_key:
        return  # auth disabled — local dev only, see module docstring
    if x_api_key != settings.simulator_api_key:
        raise HTTPException(status_code=401, detail="Invalid or missing X-API-Key header")
