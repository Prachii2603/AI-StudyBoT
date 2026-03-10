from fastapi import APIRouter
from app.models import StudentProgress
from app.services.gamification import GamificationService

router = APIRouter()
gamification = GamificationService()

@router.get("/{student_id}", response_model=StudentProgress)
async def get_progress(student_id: str):
    return gamification.get_student_progress(student_id)

@router.get("/leaderboard")
async def get_leaderboard(limit: int = 10):
    return gamification.get_leaderboard(limit)
