from app.models import StudentProgress
from typing import Dict, List
from datetime import datetime, timedelta

class EnhancedGamificationService:
    def __init__(self):
        self.students: Dict[str, StudentProgress] = {}
        self.badges = {
            "first_answer": {"name": "First Steps", "description": "Answered your first question", "points": 5},
            "streak_5": {"name": "On Fire", "description": "5 correct answers in a row", "points": 25},
            "streak_10": {"name": "Unstoppable", "description": "10 correct answers in a row", "points": 50},
            "daily_learner": {"name": "Daily Learner", "description": "Learned something new today", "points": 10},
            "topic_master": {"name": "Topic Master", "description": "Mastered a topic", "points": 100},
            "quiz_champion": {"name": "Quiz Champion", "description": "Completed 10 quizzes", "points": 75},
            "perfect_score": {"name": "Perfect Score", "description": "Got 100% on a quiz", "points": 30},
            "curious_mind": {"name": "Curious Mind", "description": "Asked 50 questions", "points": 40},
            "level_10": {"name": "Expert Learner", "description": "Reached level 10", "points": 200}
        }
        self.student_streaks = {}
        self.student_stats = {}
    
    def get_student_progress(self, student_id: str) -> StudentProgress:
        if student_id not in self.students:
            self.students[student_id] = StudentProgress(student_id=student_id)
            self.student_streaks[student_id] = {"current": 0, "best": 0}
            self.student_stats[student_id] = {
                "questions_answered": 0,
                "quizzes_completed": 0,
                "topics_studied": set(),
                "daily_activity": {},
                "last_activity": None
            }
        return self.students[student_id]
    
    def award_points(self, student_id: str, is_correct: bool, topic: str = None) -> int:
        progress = self.get_student_progress(student_id)
        stats = self.student_stats[student_id]
        streak = self.student_streaks[student_id]
        
        # Base points
        points = 10 if is_correct else 2
        
        # Update stats
        stats["questions_answered"] += 1
        if topic:
            stats["topics_studied"].add(topic)
        
        # Update daily activity
        today = datetime.now().date().isoformat()
        if today not in stats["daily_activity"]:
            stats["daily_activity"][today] = 0
        stats["daily_activity"][today] += 1
        stats["last_activity"] = datetime.now().isoformat()
        
        # Handle streaks
        if is_correct:
            streak["current"] += 1
            streak["best"] = max(streak["best"], streak["current"])
            
            # Bonus points for streaks
            if streak["current"] >= 5:
                points += 5  # Streak bonus
        else:
            streak["current"] = 0
        
        # Award points
        progress.points += points
        
        # Check for level up
        old_level = progress.level
        progress.level = self._calculate_level(progress.points)
        
        # Check for new badges
        new_badges = self._check_badges(student_id, is_correct, topic)
        for badge in new_badges:
            if badge not in progress.badges:
                progress.badges.append(badge)
                points += self.badges[badge]["points"]
                progress.points += self.badges[badge]["points"]
        
        # Level up bonus
        if progress.level > old_level:
            level_bonus = progress.level * 10
            progress.points += level_bonus
            points += level_bonus
        
        return points
    
    def _calculate_level(self, points: int) -> int:
        # Progressive leveling system
        if points < 100:
            return 1
        elif points < 300:
            return 2
        elif points < 600:
            return 3
        elif points < 1000:
            return 4
        elif points < 1500:
            return 5
        else:
            return min(50, 5 + (points - 1500) // 500)
    
    def _check_badges(self, student_id: str, is_correct: bool, topic: str = None) -> List[str]:
        stats = self.student_stats[student_id]
        streak = self.student_streaks[student_id]
        progress = self.students[student_id]
        new_badges = []
        
        # First answer badge
        if stats["questions_answered"] == 1 and "first_answer" not in progress.badges:
            new_badges.append("first_answer")
        
        # Streak badges
        if streak["current"] == 5 and "streak_5" not in progress.badges:
            new_badges.append("streak_5")
        elif streak["current"] == 10 and "streak_10" not in progress.badges:
            new_badges.append("streak_10")
        
        # Daily learner badge
        today = datetime.now().date().isoformat()
        if (today in stats["daily_activity"] and 
            stats["daily_activity"][today] >= 5 and 
            "daily_learner" not in progress.badges):
            new_badges.append("daily_learner")
        
        # Quiz completion badges
        if stats["quizzes_completed"] >= 10 and "quiz_champion" not in progress.badges:
            new_badges.append("quiz_champion")
        
        # Curious mind badge
        if stats["questions_answered"] >= 50 and "curious_mind" not in progress.badges:
            new_badges.append("curious_mind")
        
        # Level badges
        if progress.level >= 10 and "level_10" not in progress.badges:
            new_badges.append("level_10")
        
        return new_badges
    
    def complete_quiz(self, student_id: str, score: float, total_questions: int):
        """Called when a student completes a quiz"""
        stats = self.student_stats[student_id]
        progress = self.get_student_progress(student_id)
        
        stats["quizzes_completed"] += 1
        
        # Perfect score badge
        if score == 1.0 and "perfect_score" not in progress.badges:
            progress.badges.append("perfect_score")
            progress.points += self.badges["perfect_score"]["points"]
    
    def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        # Add some mock data if no real students exist
        if not self.students:
            mock_students = [
                {"rank": 1, "student_id": "demo_student_1", "points": 150, "level": 3, "badges": 2, "streak": 5, "questions_answered": 25},
                {"rank": 2, "student_id": "demo_student_2", "points": 120, "level": 2, "badges": 1, "streak": 3, "questions_answered": 18},
                {"rank": 3, "student_id": "demo_student_3", "points": 90, "level": 2, "badges": 1, "streak": 0, "questions_answered": 12},
            ]
            return mock_students
        
        sorted_students = sorted(
            self.students.values(),
            key=lambda x: (x.points, x.level),
            reverse=True
        )[:limit]
        
        leaderboard = []
        for i, student in enumerate(sorted_students):
            stats = self.student_stats.get(student.student_id, {})
            leaderboard.append({
                "rank": i + 1,
                "student_id": student.student_id,
                "points": student.points,
                "level": student.level,
                "badges": len(student.badges),
                "streak": self.student_streaks.get(student.student_id, {}).get("current", 0),
                "questions_answered": stats.get("questions_answered", 0)
            })
        
        return leaderboard
    
    def get_student_achievements(self, student_id: str) -> Dict:
        """Get detailed achievements for a student"""
        progress = self.get_student_progress(student_id)
        stats = self.student_stats[student_id]
        streak = self.student_streaks[student_id]
        
        return {
            "level": progress.level,
            "points": progress.points,
            "badges": [
                {
                    "id": badge,
                    "name": self.badges[badge]["name"],
                    "description": self.badges[badge]["description"]
                }
                for badge in progress.badges
            ],
            "stats": {
                "questions_answered": stats["questions_answered"],
                "quizzes_completed": stats["quizzes_completed"],
                "topics_studied": len(stats["topics_studied"]),
                "current_streak": streak["current"],
                "best_streak": streak["best"],
                "days_active": len(stats["daily_activity"])
            },
            "next_level_points": self._points_to_next_level(progress.points),
            "available_badges": self._get_available_badges(student_id)
        }
    
    def _points_to_next_level(self, current_points: int) -> int:
        current_level = self._calculate_level(current_points)
        level_thresholds = [0, 100, 300, 600, 1000, 1500]
        
        if current_level < len(level_thresholds):
            return level_thresholds[current_level] - current_points
        else:
            next_threshold = 1500 + (current_level - 4) * 500
            return next_threshold - current_points
    
    def _get_available_badges(self, student_id: str) -> List[Dict]:
        """Get badges that student can still earn"""
        progress = self.students[student_id]
        available = []
        
        for badge_id, badge_info in self.badges.items():
            if badge_id not in progress.badges:
                available.append({
                    "id": badge_id,
                    "name": badge_info["name"],
                    "description": badge_info["description"],
                    "points": badge_info["points"]
                })
        
        return available

# Create global instance
gamification = EnhancedGamificationService()
