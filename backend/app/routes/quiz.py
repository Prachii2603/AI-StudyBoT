from fastapi import APIRouter, HTTPException
from app.models import QuizQuestion, QuizAnswer
from app.services.ai_service import AIService
from app.services.gamification import GamificationService
from typing import List

router = APIRouter()
ai_service = AIService()
gamification = GamificationService()

@router.get("/generate/{topic}", response_model=List[QuizQuestion])
async def generate_quiz(topic: str, difficulty: int = 1, count: int = 5):
    try:
        questions = await ai_service.generate_quiz(topic, difficulty, count)
        return questions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/submit")
async def submit_answer(answer: QuizAnswer):
    is_correct = await ai_service.check_answer(answer.question_id, answer.answer)
    points = gamification.award_points(answer.student_id, is_correct)
    return {"correct": is_correct, "points": points}
