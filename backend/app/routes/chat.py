from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.models import ChatRequest, ChatMessage
from app.services.ai_service import ai_service
from app.database import get_db
from app.services.database_service import DatabaseService
from typing import List

router = APIRouter()

@router.post("/message")
async def send_message(request: ChatRequest, db: Session = Depends(get_db)):
    try:
        db_service = DatabaseService(db)
        
        # Save user message to database
        db_service.save_chat_message(
            user_id=request.student_id,
            message_type="user",
            content=request.message,
            difficulty=request.difficulty_level
        )
        
        # Generate AI response
        response = await ai_service.generate_response(
            request.message, 
            request.student_id,
            request.difficulty_level
        )
        
        # Handle both old and new response formats
        if isinstance(response, dict):
            # Save AI response to database
            db_service.save_chat_message(
                user_id=request.student_id,
                message_type="assistant",
                content=response.get("content", ""),
                topic=response.get("adaptive_info", {}).get("topic"),
                difficulty=response.get("adaptive_info", {}).get("adapted_difficulty"),
                adaptive_info=response.get("adaptive_info", {}),
                images=response.get("images", []),
                learning_resources=response.get("learning_resources", [])
            )
            
            return {
                "role": "assistant",
                "content": response.get("content", ""),
                "images": response.get("images", []),
                "learning_resources": response.get("learning_resources", []),
                "timestamp": response.get("timestamp"),
                "adaptive_info": response.get("adaptive_info", {}),
                "pace_adapted": response.get("adaptive_info", {}).get("adapted_difficulty") != request.difficulty_level
            }
        else:
            # Fallback for old string format
            db_service.save_chat_message(
                user_id=request.student_id,
                message_type="assistant",
                content=response,
                difficulty=request.difficulty_level
            )
            return ChatMessage(role="assistant", content=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{user_id}")
async def get_chat_history(user_id: str, limit: int = 50, db: Session = Depends(get_db)):
    """Get user's chat history"""
    try:
        db_service = DatabaseService(db)
        history = db_service.get_chat_history(user_id, limit)
        
        return {
            "history": [
                {
                    "id": msg.id,
                    "role": msg.message_type,
                    "content": msg.content,
                    "topic": msg.topic,
                    "difficulty": msg.difficulty,
                    "adaptive_info": msg.adaptive_info,
                    "images": msg.images,
                    "learning_resources": msg.learning_resources,
                    "timestamp": msg.created_at.isoformat()
                }
                for msg in history
            ],
            "total": len(history)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/quiz-analysis")
async def analyze_quiz_performance(quiz_results: List[dict], student_id: str):
    try:
        analysis = await ai_service.analyze_quiz_performance(student_id, quiz_results)
        return analysis
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
