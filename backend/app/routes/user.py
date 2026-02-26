"""User profile API routes."""

from fastapi import APIRouter, HTTPException
from app.models.schemas import UserProfile, UserProfileCreate
from app.services.database import create_user, get_user, update_user
import uuid

router = APIRouter(prefix="/api/user", tags=["user"])


@router.post("/register", response_model=UserProfile)
async def register_user(profile: UserProfileCreate):
    """Register a new user profile."""
    user_id = f"user_{uuid.uuid4().hex[:8]}"
    return create_user(user_id, profile.model_dump())


@router.get("/{user_id}", response_model=UserProfile)
async def get_user_profile(user_id: str):
    """Get user profile by ID."""
    user = get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserProfile)
async def update_user_profile(user_id: str, updates: dict):
    """Update user profile."""
    user = update_user(user_id, updates)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
