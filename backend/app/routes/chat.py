from fastapi import APIRouter, HTTPException
from app.models import ChatRequest, ChatMessage
from app.services.ai_service import AIService
from typing import List

router = APIRouter()
ai_service = AIService()

@router.post("/message", response_model=ChatMessage)
async def send_message(request: ChatRequest):
    try:
        response = await ai_service.generate_response(
            request.message, 
            request.student_id,
            request.difficulty_level
        )
        return ChatMessage(role="assistant", content=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/voice")
async def process_voice(audio_data: bytes, student_id: str):
    # Placeholder for voice processing
    return {"text": "Voice processing not implemented yet"}
