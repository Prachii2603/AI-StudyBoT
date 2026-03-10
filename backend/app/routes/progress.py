from fastapi import APIRouter, HTTPException
from app.models import StudentProgress
from app.services.gamification import gamification

router = APIRouter()

@router.get("/{student_id}", response_model=StudentProgress)
async def get_progress(student_id: str):
    try:
        return gamification.get_student_progress(student_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{student_id}/achievements")
async def get_achievements(student_id: str):
    try:
        return gamification.get_student_achievements(student_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/leaderboard")
async def get_leaderboard(limit: int = 10):
    try:
        return gamification.get_leaderboard(limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{student_id}/quiz-complete")
async def complete_quiz(student_id: str, score: float, total_questions: int):
    try:
        gamification.complete_quiz(student_id, score, total_questions)
        return {"message": "Quiz completion recorded", "achievements_updated": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
