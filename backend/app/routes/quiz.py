from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.models import QuizQuestion, QuizAnswer
from app.services.ai_service import ai_service
from app.services.gamification import gamification
from app.database import get_db
from app.services.database_service import DatabaseService
from typing import List
import time

router = APIRouter()

@router.get("/generate/{topic}", response_model=List[QuizQuestion])
async def generate_quiz(topic: str, difficulty: int = 1, count: int = 10, 
                       student_id: str = None, db: Session = Depends(get_db)):
    try:
        # Ensure minimum 10 questions
        count = max(10, count)
        
        # Create learning session
        if student_id:
            db_service = DatabaseService(db)
            session = db_service.create_learning_session(
                user_id=student_id,
                session_type="quiz",
                topic=topic,
                difficulty=difficulty
            )
        
        questions = await ai_service.generate_quiz(topic, difficulty, count, student_id)
        return questions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/submit")
async def submit_answer(answer: QuizAnswer, db: Session = Depends(get_db)):
    try:
        # Check if answer is correct
        is_correct = await ai_service.check_answer(answer.question_id, answer.answer, answer.student_id)
        
        # Get enhanced feedback using personalized learning
        if not is_correct:
            # Get question details (this would normally come from stored question data)
            question_topic = "general"  # This should be retrieved from question storage
            difficulty = 1  # This should be retrieved from question storage
            
            # Get personalized help for wrong answer
            from app.services.personalized_learning import personalized_learning
            help_content = personalized_learning.handle_wrong_answer(
                topic=question_topic,
                difficulty=difficulty,
                question="",  # Would include actual question text
                user_answer=str(answer.answer),
                correct_answer="",  # Would include correct answer
                user_level="basic"  # Would be determined from user profile
            )
        else:
            help_content = None
        
        # Award points using enhanced gamification
        from app.services.gamification import gamification
        performance_data = {
            "difficulty": difficulty if 'difficulty' in locals() else 1,
            "time_taken": getattr(answer, 'time_taken', 30),
            "topic": question_topic if 'question_topic' in locals() else "general"
        }
        
        activity = "correct_answer" if is_correct else "incorrect_answer"
        gamification_result = gamification.award_points(answer.student_id, activity, performance_data)
        
        response = {
            "correct": is_correct,
            "points_earned": gamification_result["points_earned"],
            "total_points": gamification_result["total_points"],
            "new_badges": gamification_result["new_badges"],
            "level_up": gamification_result["level_up"],
            "current_streak": gamification_result["current_streak"]
        }
        
        # Add detailed help for wrong answers
        if help_content:
            response.update({
                "help": help_content,
                "show_explanation": True
            })
        else:
            response.update({
                "encouragement": "Great job! Keep up the excellent work! 🌟",
                "show_explanation": False
            })
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/complete")
async def complete_quiz(quiz_data: dict, db: Session = Depends(get_db)):
    """Complete a quiz and save results"""
    try:
        db_service = DatabaseService(db)
        
        # Save quiz result
        quiz_result = db_service.save_quiz_result(
            user_id=quiz_data["student_id"],
            quiz_data={
                "topic": quiz_data["topic"],
                "difficulty": quiz_data["difficulty"],
                "total_questions": quiz_data["total_questions"],
                "correct_answers": quiz_data["correct_answers"],
                "score_percentage": quiz_data["score_percentage"],
                "time_taken_seconds": quiz_data.get("time_taken_seconds"),
                "weak_areas": quiz_data.get("weak_areas", []),
                "strong_areas": quiz_data.get("strong_areas", []),
                "quiz_data": quiz_data.get("quiz_data", {})
            }
        )
        
        # Update user progress
        performance = quiz_data["score_percentage"] / 100.0
        db_service.update_user_progress(
            user_id=quiz_data["student_id"],
            topic=quiz_data["topic"],
            performance=performance,
            difficulty=quiz_data["difficulty"]
        )
        
        # Award points for quiz completion
        from app.services.gamification import gamification
        performance_data = {
            "score": performance,
            "difficulty": quiz_data["difficulty"],
            "time_taken": quiz_data.get("time_taken_seconds", 300)
        }
        gamification_result = gamification.award_points(
            quiz_data["student_id"], 
            "quiz_completion", 
            performance_data
        )
        
        return {
            "success": True,
            "quiz_id": quiz_result.id,
            "message": "Quiz completed successfully",
            "score": quiz_data["score_percentage"],
            "gamification": gamification_result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/{student_id}")
async def get_student_analytics(student_id: str, db: Session = Depends(get_db)):
    """Get comprehensive student analytics"""
    try:
        from app.services.gamification import gamification
        analytics = gamification.get_student_analytics(student_id)
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/leaderboard")
async def get_quiz_leaderboard(metric: str = "total_points", limit: int = 10, db: Session = Depends(get_db)):
    """Get quiz leaderboard"""
    try:
        from app.services.gamification import gamification
        leaderboard = gamification.get_leaderboard(metric, limit)
        return {"leaderboard": leaderboard, "metric": metric}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/insights/{student_id}")
async def get_progress_insights(student_id: str, db: Session = Depends(get_db)):
    """Get personalized progress insights"""
    try:
        from app.services.gamification import gamification
        insights = gamification.get_progress_insights(student_id)
        return insights
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/study-plan/{student_id}")
async def get_study_plan(student_id: str, db: Session = Depends(get_db)):
    """Get personalized study plan"""
    try:
        from app.services.gamification import gamification
        study_plan = gamification.get_study_plan(student_id)
        return study_plan
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
