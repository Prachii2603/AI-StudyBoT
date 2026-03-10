from app.models import StudentProgress
from app.services.personalized_learning import PersonalizedLearningService
from typing import Dict, List, Any
from datetime import datetime, timedelta

class EnhancedGamificationService:
    def __init__(self):
        self.students: Dict[str, StudentProgress] = {}
        self.student_streaks = {}
        self.student_stats = {}
        self.student_badges = {}  # Track earned badges per student
        self.daily_activities = {}  # Track daily activities for streaks
        self.personalized_learning = PersonalizedLearningService()  # Create instance
    
    def get_student_progress(self, student_id: str) -> StudentProgress:
        if student_id not in self.students:
            self.students[student_id] = StudentProgress(student_id=student_id)
            self.student_streaks[student_id] = {"current": 0, "best": 0, "last_activity": None}
            self.student_stats[student_id] = {
                "questions_answered": 0,
                "correct_answers": 0,
                "quizzes_completed": 0,
                "perfect_quizzes": 0,
                "topics_studied": set(),
                "daily_activity": {},
                "total_points": 0,
                "fast_answers": 0,
                "questions_asked": 0,
                "game_scores": {},
                "has_top_score": False,
                "earned_badges": [],
                "study_streak": 0,
                "active_days": 0
            }
            self.student_badges[student_id] = []
            self.daily_activities[student_id] = {}
        return self.students[student_id]
    
    def award_points(self, student_id: str, activity: str, performance_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Enhanced point awarding system with personalized learning integration"""
        progress = self.get_student_progress(student_id)
        stats = self.student_stats[student_id]
        
        if performance_data is None:
            performance_data = {}
        
        # Calculate points using personalized learning service
        points_earned = self.personalized_learning.calculate_points(activity, performance_data)
        
        # Update student stats
        stats["total_points"] += points_earned
        progress.total_points = stats["total_points"]
        
        # Update activity-specific stats
        if activity == "correct_answer":
            stats["correct_answers"] += 1
            stats["questions_answered"] += 1
            
            # Check for fast answer bonus
            time_taken = performance_data.get("time_taken", 60)
            if time_taken < 30:
                stats["fast_answers"] += 1
            
            # Update streak
            self._update_streak(student_id, True)
            
        elif activity == "quiz_completion":
            stats["quizzes_completed"] += 1
            score = performance_data.get("score", 0)
            if score >= 1.0:  # Perfect score
                stats["perfect_quizzes"] += 1
                
        elif activity == "chat_interaction":
            stats["questions_asked"] += 1
            
        elif activity in ["game_completion", "game_high_score"]:
            game_type = performance_data.get("game_type", "unknown")
            score = performance_data.get("score", 0)
            if game_type not in stats["game_scores"] or score > stats["game_scores"][game_type]:
                stats["game_scores"][game_type] = score
                if activity == "game_high_score":
                    stats["has_top_score"] = True
        
        # Update daily activity and streaks
        self._update_daily_activity(student_id)
        
        # Check for new badges
        new_badges = self._check_new_badges(student_id)
        
        # Update level based on points
        new_level = self._calculate_level(stats["total_points"])
        old_level = progress.level
        progress.level = new_level
        
        return {
            "points_earned": points_earned,
            "total_points": stats["total_points"],
            "new_badges": new_badges,
            "level_up": new_level > old_level,
            "new_level": new_level,
            "current_streak": self.student_streaks[student_id]["current"],
            "study_streak": stats["study_streak"]
        }
    
    def _update_streak(self, student_id: str, is_correct: bool):
        """Update answer streak"""
        streak = self.student_streaks[student_id]
        
        if is_correct:
            streak["current"] += 1
            if streak["current"] > streak["best"]:
                streak["best"] = streak["current"]
        else:
            streak["current"] = 0
    
    def _update_daily_activity(self, student_id: str):
        """Update daily activity and study streaks"""
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        
        stats = self.student_stats[student_id]
        daily_activities = self.daily_activities[student_id]
        
        # Mark today as active
        daily_activities[today.isoformat()] = True
        
        # Calculate study streak
        current_date = today
        streak = 0
        
        while current_date.isoformat() in daily_activities:
            streak += 1
            current_date -= timedelta(days=1)
        
        stats["study_streak"] = streak
        stats["active_days"] = len(daily_activities)
    
    def _check_new_badges(self, student_id: str) -> List[Dict[str, Any]]:
        """Check for newly earned badges"""
        stats = self.student_stats[student_id]
        
        # Use personalized learning service to check badge eligibility
        new_badges = self.personalized_learning.check_badge_eligibility(stats)
        
        # Add new badges to student's collection
        for badge in new_badges:
            if badge["id"] not in stats["earned_badges"]:
                stats["earned_badges"].append(badge["id"])
                self.student_badges[student_id].append(badge)
                # Award badge points
                stats["total_points"] += badge["points"]
        
        return new_badges
    
    def _calculate_level(self, total_points: int) -> int:
        """Calculate level based on total points"""
        # Level progression: 100 points per level initially, then increasing
        if total_points < 100:
            return 1
        elif total_points < 300:
            return 2
        elif total_points < 600:
            return 3
        elif total_points < 1000:
            return 4
        elif total_points < 1500:
            return 5
        else:
            # Higher levels require more points
            return min(50, 5 + (total_points - 1500) // 500)
    
    def get_student_analytics(self, student_id: str) -> Dict[str, Any]:
        """Get comprehensive student analytics"""
        progress = self.get_student_progress(student_id)
        stats = self.student_stats[student_id]
        streak = self.student_streaks[student_id]
        
        # Calculate accuracy
        accuracy = (stats["correct_answers"] / max(1, stats["questions_answered"])) * 100
        
        return {
            "level": progress.level,
            "total_points": stats["total_points"],
            "accuracy": round(accuracy, 1),
            "questions_answered": stats["questions_answered"],
            "correct_answers": stats["correct_answers"],
            "quizzes_completed": stats["quizzes_completed"],
            "perfect_quizzes": stats["perfect_quizzes"],
            "current_streak": streak["current"],
            "best_streak": streak["best"],
            "study_streak": stats["study_streak"],
            "active_days": stats["active_days"],
            "topics_studied": len(stats["topics_studied"]),
            "badges_earned": len(stats["earned_badges"]),
            "badges": self.student_badges.get(student_id, []),
            "fast_answers": stats["fast_answers"],
            "questions_asked": stats["questions_asked"],
            "game_scores": stats["game_scores"]
        }
    
    def get_leaderboard(self, metric: str = "total_points", limit: int = 10) -> List[Dict[str, Any]]:
        """Get leaderboard based on specified metric"""
        leaderboard = []
        
        for student_id, stats in self.student_stats.items():
            progress = self.students[student_id]
            
            if metric == "total_points":
                score = stats["total_points"]
            elif metric == "accuracy":
                score = (stats["correct_answers"] / max(1, stats["questions_answered"])) * 100
            elif metric == "study_streak":
                score = stats["study_streak"]
            elif metric == "level":
                score = progress.level
            else:
                score = stats.get(metric, 0)
            
            leaderboard.append({
                "student_id": student_id,
                "score": score,
                "level": progress.level,
                "total_points": stats["total_points"],
                "badges": len(stats["earned_badges"])
            })
        
        # Sort by score (descending)
        leaderboard.sort(key=lambda x: x["score"], reverse=True)
        
        return leaderboard[:limit]
    
    def get_progress_insights(self, student_id: str) -> Dict[str, Any]:
        """Get personalized progress insights"""
        stats = self.student_stats[student_id]
        progress = self.get_student_progress(student_id)
        
        # Prepare data for personalized learning service
        user_progress = {
            "average_score": stats["correct_answers"] / max(1, stats["questions_answered"]),
            "total_points": stats["total_points"],
            "study_streak": stats["study_streak"],
            "topics": {},  # This would be populated from actual topic progress
            "weak_topics": [],  # This would be determined from quiz results
            "strong_topics": [],  # This would be determined from quiz results
            "preferred_difficulty": 2  # This would come from user profile
        }
        
        return self.personalized_learning.generate_progress_insights(user_progress)
    
    def get_study_plan(self, student_id: str) -> Dict[str, Any]:
        """Get personalized study plan"""
        stats = self.student_stats[student_id]
        
        user_data = {
            "average_score": stats["correct_answers"] / max(1, stats["questions_answered"]),
            "weak_topics": [],  # Would be populated from actual data
            "strong_topics": [],  # Would be populated from actual data
            "preferred_difficulty": 2  # Would come from user profile
        }
        
        return self.personalized_learning.get_personalized_study_plan(user_data)
    def get_student_achievements(self, student_id: str) -> Dict[str, Any]:
        """Get detailed achievements for a student"""
        progress = self.get_student_progress(student_id)
        stats = self.student_stats[student_id]
        streak = self.student_streaks[student_id]

        # Calculate accuracy
        accuracy = (stats["correct_answers"] / max(1, stats["questions_answered"])) * 100

        return {
            "level": progress.level,
            "total_points": stats["total_points"],
            "accuracy": round(accuracy, 1),
            "badges": [
                {
                    "id": badge["id"],
                    "name": badge["name"],
                    "description": badge["description"],
                    "icon": badge.get("icon", "🏅"),
                    "points": badge["points"]
                }
                for badge in self.student_badges.get(student_id, [])
            ],
            "stats": {
                "questions_answered": stats["questions_answered"],
                "correct_answers": stats["correct_answers"],
                "quizzes_completed": stats["quizzes_completed"],
                "topics_studied": len(stats["topics_studied"]),
                "current_streak": streak["current"],
                "best_streak": streak["best"],
                "study_streak": stats["study_streak"],
                "active_days": stats["active_days"],
                "fast_answers": stats["fast_answers"],
                "questions_asked": stats["questions_asked"]
            },
            "next_level_points": self._points_to_next_level(stats["total_points"]),
            "available_badges": self._get_available_badges(student_id)
        }

    def _points_to_next_level(self, current_points: int) -> int:
        """Calculate points needed to reach next level"""
        current_level = self._calculate_level(current_points)
        level_thresholds = [0, 100, 300, 600, 1000, 1500]

        if current_level < len(level_thresholds):
            return level_thresholds[current_level] - current_points
        else:
            next_threshold = 1500 + (current_level - 4) * 500
            return next_threshold - current_points

    def _get_available_badges(self, student_id: str) -> List[Dict[str, Any]]:
        """Get badges that student can still earn"""
        earned_badge_ids = [badge["id"] for badge in self.student_badges.get(student_id, [])]
        available = []

        # Get available badges from personalized learning service
        all_badges = [
            {"id": "first_answer", "name": "First Step", "description": "Answer your first question", "points": 10, "icon": "🎯"},
            {"id": "streak_5", "name": "On Fire", "description": "Get 5 answers correct in a row", "points": 25, "icon": "🔥"},
            {"id": "streak_10", "name": "Unstoppable", "description": "Get 10 answers correct in a row", "points": 50, "icon": "⚡"},
            {"id": "quiz_master", "name": "Quiz Master", "description": "Complete 10 quizzes", "points": 100, "icon": "🎓"},
            {"id": "curious_mind", "name": "Curious Mind", "description": "Answer 50 questions", "points": 75, "icon": "🧠"},
            {"id": "daily_learner", "name": "Daily Learner", "description": "Study for 5 days in a row", "points": 50, "icon": "📚"},
            {"id": "perfect_score", "name": "Perfect Score", "description": "Get 100% on a quiz", "points": 30, "icon": "💯"},
            {"id": "level_10", "name": "Expert", "description": "Reach level 10", "points": 200, "icon": "👑"}
        ]

        for badge in all_badges:
            if badge["id"] not in earned_badge_ids:
                available.append(badge)

        return available
    def complete_quiz(self, student_id: str, score: float, total_questions: int):
        """Called when a student completes a quiz"""
        stats = self.student_stats[student_id]
        progress = self.get_student_progress(student_id)

        stats["quizzes_completed"] += 1

        # Award points for quiz completion
        performance_data = {
            "score": score,
            "total_questions": total_questions,
            "perfect_score": score >= 1.0
        }

        self.award_points(student_id, "quiz_completion", performance_data)

        # Check for perfect score badge
        if score >= 1.0:
            # Award perfect score badge if not already earned
            earned_badge_ids = [badge["id"] for badge in self.student_badges.get(student_id, [])]
            if "perfect_score" not in earned_badge_ids:
                perfect_badge = {
                    "id": "perfect_score",
                    "name": "Perfect Score",
                    "description": "Got 100% on a quiz",
                    "points": 30,
                    "icon": "💯"
                }
                self.student_badges[student_id].append(perfect_badge)
                stats["total_points"] += perfect_badge["points"]

# Global instance
gamification = EnhancedGamificationService()
