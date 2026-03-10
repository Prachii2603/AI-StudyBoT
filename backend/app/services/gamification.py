from app.models import StudentProgress
from typing import Dict, List

class GamificationService:
    def __init__(self):
        self.students: Dict[str, StudentProgress] = {}
        self.badges = {
            "first_answer": "First Steps",
            "streak_5": "On Fire",
            "master_topic": "Topic Master",
            "level_10": "Expert Learner"
        }
    
    def award_points(self, student_id: str, is_correct: bool) -> int:
        if student_id not in self.students:
            self.students[student_id] = StudentProgress(student_id=student_id)
        
        points = 10 if is_correct else 2
        self.students[student_id].points += points
        
        # Level up logic
        if self.students[student_id].points >= self.students[student_id].level * 100:
            self.students[student_id].level += 1
        
        return points
    
    def get_student_progress(self, student_id: str) -> StudentProgress:
        if student_id not in self.students:
            self.students[student_id] = StudentProgress(student_id=student_id)
        return self.students[student_id]
    
    def get_leaderboard(self, limit: int) -> List[Dict]:
        sorted_students = sorted(
            self.students.values(),
            key=lambda x: x.points,
            reverse=True
        )[:limit]
        return [{"student_id": s.student_id, "points": s.points, "level": s.level} for s in sorted_students]
