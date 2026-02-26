"""Chat API routes."""

from fastapi import APIRouter
from app.models.schemas import ChatRequest, ChatResponse
from app.services.ai_engine import process_message

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process a chat message and return AI response."""
    result = await process_message(
        message=request.message,
        user_id=request.user_id,
        language=request.language.value,
        region=request.region,
        pincode=request.pincode,
    )

    return ChatResponse(
        reply=result["reply"],
        intent=result["intent"],
        language=request.language,
        suggestions=result["suggestions"],
    )
