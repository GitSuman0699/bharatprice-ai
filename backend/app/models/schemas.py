"""Pydantic models for API request/response validation."""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class Language(str, Enum):
    ENGLISH = "en"
    HINDI = "hi"
    TAMIL = "ta"
    TELUGU = "te"
    MARATHI = "mr"


class ChatRequest(BaseModel):
    """Incoming chat message from user."""
    message: str = Field(..., description="User's text message")
    user_id: str = Field(default="demo_user", description="User identifier")
    language: Language = Field(default=Language.ENGLISH, description="Preferred language")
    region: str = Field(default="delhi", description="User's region/city for price data")
    pincode: Optional[str] = Field(default=None, description="User's pincode for locality-level pricing")
    state: Optional[str] = Field(default=None, description="Explicit state from frontend GPS")
    district: Optional[str] = Field(default=None, description="Explicit district from frontend GPS")
    session_id: Optional[str] = Field(default=None, description="Conversation session ID")


class PriceInfo(BaseModel):
    """Price data for a single source."""
    source: str
    price: float
    unit: str = "per kg"


class ChatResponse(BaseModel):
    """Bot response to user."""
    reply: str = Field(..., description="Bot's text reply")
    intent: str = Field(default="general", description="Detected intent")
    language: Language = Field(default=Language.ENGLISH)
    prices: Optional[list[PriceInfo]] = Field(default=None, description="Price data if applicable")
    audio_url: Optional[str] = Field(default=None, description="URL to audio response")
    suggestions: list[str] = Field(default_factory=list, description="Quick reply suggestions")


class UserProfile(BaseModel):
    """Kirana store owner profile."""
    user_id: str
    store_name: str = ""
    pin_code: str = ""
    city: str = ""
    language: Language = Language.HINDI
    categories: list[str] = Field(default_factory=lambda: ["grocery"])


class UserProfileCreate(BaseModel):
    """Request to create a user profile."""
    store_name: str = Field(..., description="Name of the store")
    pin_code: str = Field(..., description="Store PIN code")
    city: str = Field(..., description="City name")
    language: Language = Field(default=Language.HINDI)
    categories: list[str] = Field(default_factory=lambda: ["grocery"])


class PriceData(BaseModel):
    """Price record for a product in a region."""
    product_id: str
    product_name: str
    date: str
    region: str
    mandi_price: Optional[float] = None
    bigbasket_price: Optional[float] = None
    jiomart_price: Optional[float] = None
    local_avg: Optional[float] = None
    recommended_retail: Optional[float] = None
    demand_trend: str = "stable"
    unit: str = "per kg"


class MandiRate(BaseModel):
    """Mandi wholesale price."""
    mandi_name: str
    location: str
    price: float
    unit: str = "per quintal"
    date: str


class PriceTrend(BaseModel):
    """Price trend over time."""
    product_name: str
    region: str
    period_days: int = 30
    current_price: float
    price_change_pct: float
    trend: str  # "rising", "falling", "stable"
    data_points: list[dict] = Field(default_factory=list)
    summary: str = ""
