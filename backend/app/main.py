"""
BharatPrice AI — Backend API Server
AI-powered hyperlocal pricing intelligence for India's kirana stores.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from mangum import Mangum
from app.config import get_settings
from app.routes import chat, data, user
from app.middleware.security import APIKeyMiddleware
from app.middleware.rate_limiter import limiter

settings = get_settings()

# Disable docs in production (when API key is configured)
_docs_url = None if settings.api_secret_key else "/docs"
_redoc_url = None if settings.api_secret_key else "/redoc"

app = FastAPI(
    title="BharatPrice AI",
    description="AI-powered hyperlocal pricing intelligence for India's kirana stores",
    version="1.0.0",
    docs_url=_docs_url,
    redoc_url=_redoc_url,
)

# ── Rate limiter state ──────────────────────────────────────────
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ── Middleware stack (order matters: last added = first executed) ───
# 1. CORS — tight allowed methods & headers
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT"],
    allow_headers=["Content-Type", "X-API-Key"],
)

# 2. API key gate
app.add_middleware(APIKeyMiddleware)

# 3. Trusted host validation
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.allowed_hosts.split(","),
)

# Routes
app.include_router(chat.router)
app.include_router(data.router)
app.include_router(user.router)


@app.get("/")
async def root():
    return {
        "name": "BharatPrice AI",
        "version": "1.0.0",
        "status": "running",
        "description": "AI-powered hyperlocal pricing intelligence for India's kirana stores",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}

# AWS Lambda Handler
handler = Mangum(app)
