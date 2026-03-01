"""
BharatPrice AI — Backend API Server
AI-powered hyperlocal pricing intelligence for India's kirana stores.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from app.config import get_settings
from app.routes import chat, data, user

settings = get_settings()

app = FastAPI(
    title="BharatPrice AI",
    description="AI-powered hyperlocal pricing intelligence for India's kirana stores",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
