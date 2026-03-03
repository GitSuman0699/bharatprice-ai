"""Chat API routes."""

from fastapi import APIRouter, Request
from app.models.schemas import ChatRequest, ChatResponse
from app.services.ai_engine import process_message
from app.middleware.rate_limiter import limiter, CHAT_LIMIT

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
@limiter.limit(CHAT_LIMIT)
async def chat(request: Request, body: ChatRequest):
    """Process a chat message and return AI response."""
    result = await process_message(
        message=body.message,
        user_id=body.user_id,
        language=body.language.value,
        region=body.region,
        pincode=body.pincode,
        state=body.state,
        district=body.district,
        chat_history=body.chat_history,
    )

    return ChatResponse(
        reply=result["reply"],
        intent=result["intent"],
        language=body.language,
        suggestions=result["suggestions"],
    )
