from fastapi import APIRouter, HTTPException
from app.models import QuizQuestion, QuizAnswer
from app.services.ai_service import ai_service
from app.services.gamification import gamification
from typing import List

router = APIRouter()

@router.get("/generate/{topic}", response_model=List[QuizQuestion])
async def generate_quiz(topic: str, difficulty: int = 1, count: int = 10, student_id: str = None):
    try:
        # Ensure minimum 10 questions
        count = max(10, count)
        questions = await ai_service.generate_quiz(topic, difficulty, count, student_id)
        return questions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/submit")
async def submit_answer(answer: QuizAnswer):
    try:
        result = await ai_service.check_answer(answer.question_id, answer.answer, answer.student_id)
        
        # Update gamification based on result
        points = gamification.award_points(answer.student_id, result["correct"])
        
        return {
            "correct": result["correct"],
            "explanation": result.get("explanation", ""),
            "points": points,
            "performance_update": result.get("performance_update")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
