from fastapi import APIRouter, HTTPException
from app.models import ChatRequest, ChatMessage
from app.services.ai_service import ai_service
from typing import List

router = APIRouter()

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

@router.get("/recommendations/{student_id}")
async def get_learning_recommendations(student_id: str):
    try:
        recommendations = await ai_service.get_learning_recommendations(student_id)
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/profile/{student_id}")
async def get_student_profile(student_id: str):
    try:
        profile = ai_service.get_student_profile(student_id)
        return profile
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/voice")
async def process_voice(audio_data: bytes, student_id: str):
    # Enhanced voice processing placeholder
    return {"text": "Voice processing will be implemented with speech recognition", "status": "placeholder"}
