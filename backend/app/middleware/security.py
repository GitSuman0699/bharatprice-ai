"""
API Key authentication middleware.

Every request to /api/* must include a valid X-API-Key header.
Public endpoints (health, root, docs) are excluded.
"""

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.config import get_settings


# Paths that do NOT require an API key
_PUBLIC_PATHS = frozenset({
    "/",
    "/health",
    "/docs",
    "/redoc",
    "/openapi.json",
})


class APIKeyMiddleware(BaseHTTPMiddleware):
    """Reject requests to /api/* that lack a valid X-API-Key header."""

    async def dispatch(self, request: Request, call_next):
        settings = get_settings()

        # Skip validation when no key is configured (local dev convenience)
        if not settings.api_secret_key:
            return await call_next(request)

        # Allow public paths or CORS preflight requests through without a key
        if request.url.path in _PUBLIC_PATHS or request.method == "OPTIONS":
            return await call_next(request)

        # Validate the key for all other routes
        # Starlette headers are case-insensitive
        client_key = request.headers.get("x-api-key") or request.headers.get("X-API-Key") or ""
        if client_key != settings.api_secret_key:
            return JSONResponse(
                status_code=403,
                content={"detail": "Invalid or missing API key"},
            )

        return await call_next(request)
