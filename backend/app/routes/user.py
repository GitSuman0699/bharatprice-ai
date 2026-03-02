"""User profile API routes."""

from fastapi import APIRouter, HTTPException, Request
from app.models.schemas import UserProfile, UserProfileCreate
from app.services.database import create_user, get_user, update_user
from app.middleware.rate_limiter import limiter, USER_LIMIT
import uuid

router = APIRouter(prefix="/api/user", tags=["user"])


@router.post("/register", response_model=UserProfile)
@limiter.limit(USER_LIMIT)
async def register_user(request: Request, profile: UserProfileCreate):
    """Register a new user profile."""
    user_id = f"user_{uuid.uuid4().hex[:8]}"
    return create_user(user_id, profile.model_dump())


@router.get("/{user_id}", response_model=UserProfile)
@limiter.limit(USER_LIMIT)
async def get_user_profile(request: Request, user_id: str):
    """Get user profile by ID."""
    user = get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserProfile)
@limiter.limit(USER_LIMIT)
async def update_user_profile(request: Request, user_id: str, updates: dict):
    """Update user profile."""
    user = update_user(user_id, updates)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
