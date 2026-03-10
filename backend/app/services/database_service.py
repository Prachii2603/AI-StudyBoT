from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from app.database import User, LearningSession, QuizResult, ChatHistory, GameScore, UserProgress
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime, timedelta
import hashlib

class DatabaseService:
    def __init__(self, db: Session):
        self.db = db
    
    # User Management
    def create_user(self, user_data: Dict[str, Any]) -> User:
        """Create a new user"""
        user_id = str(uuid.uuid4())
        hashed_password = hashlib.sha256(user_data["password"].encode()).hexdigest()
        
        db_user = User(
            id=user_id,
            name=user_data["name"],
            email=user_data["email"],
            password_hash=hashed_password,
            age=user_data.get("age"),
            grade=user_data.get("grade"),
            interests=user_data.get("interests", []),
            preferred_difficulty=1 if user_data.get("grade") in ["elementary", "middle"] else 2
        )
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify password"""
        return hashlib.sha256(password.encode()).hexdigest() == hashed_password
    
    def update_user_profile(self, user_id: str, updates: Dict[str, Any]) -> Optional[User]:
        """Update user profile"""
        user = self.get_user_by_id(user_id)
        if user:
            for key, value in updates.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            user.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(user)
        return user
    
    # Learning Sessions
    def create_learning_session(self, user_id: str, session_type: str, 
                              topic: str = None, difficulty: int = 1) -> LearningSession:
        """Create a new learning session"""
        session_id = str(uuid.uuid4())
        session = LearningSession(
            id=session_id,
            user_id=user_id,
            session_type=session_type,
            topic=topic,
            difficulty=difficulty
        )
        
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session
    
    def update_session_stats(self, session_id: str, score: float = None, 
                           duration: int = None, questions: int = None, 
                           correct: int = None, data: Dict = None):
        """Update session statistics"""
        session = self.db.query(LearningSession).filter(LearningSession.id == session_id).first()
        if session:
            if score is not None:
                session.score = score
            if duration is not None:
                session.duration_minutes = duration
            if questions is not None:
                session.questions_answered = questions
            if correct is not None:
                session.correct_answers = correct
            if data is not None:
                session.session_data = data
            
            self.db.commit()
    
    # Quiz Results
    def save_quiz_result(self, user_id: str, quiz_data: Dict[str, Any]) -> QuizResult:
        """Save quiz result"""
        result_id = str(uuid.uuid4())
        quiz_result = QuizResult(
            id=result_id,
            user_id=user_id,
            session_id=quiz_data.get("session_id"),
            topic=quiz_data["topic"],
            difficulty=quiz_data["difficulty"],
            total_questions=quiz_data["total_questions"],
            correct_answers=quiz_data["correct_answers"],
            score_percentage=quiz_data["score_percentage"],
            time_taken_seconds=quiz_data.get("time_taken_seconds"),
            weak_areas=quiz_data.get("weak_areas", []),
            strong_areas=quiz_data.get("strong_areas", []),
            quiz_data=quiz_data.get("quiz_data", {})
        )
        
        self.db.add(quiz_result)
        self.db.commit()
        self.db.refresh(quiz_result)
        
        # Update user stats
        self._update_user_quiz_stats(user_id, quiz_data)
        
        return quiz_result
    
    def _update_user_quiz_stats(self, user_id: str, quiz_data: Dict[str, Any]):
        """Update user's overall quiz statistics"""
        user = self.get_user_by_id(user_id)
        if user:
            # Update total questions answered
            user.total_questions_answered += quiz_data["total_questions"]
            
            # Update average score
            total_score = user.average_score * user.total_sessions
            total_score += quiz_data["score_percentage"] / 100
            user.total_sessions += 1
            user.average_score = total_score / user.total_sessions
            
            # Adjust preferred difficulty based on performance
            if quiz_data["score_percentage"] > 80 and user.preferred_difficulty < 3:
                user.preferred_difficulty = min(3, user.preferred_difficulty + 1)
            elif quiz_data["score_percentage"] < 40 and user.preferred_difficulty > 1:
                user.preferred_difficulty = max(1, user.preferred_difficulty - 1)
            
            self.db.commit()
    
    # Chat History
    def save_chat_message(self, user_id: str, message_type: str, content: str,
                         topic: str = None, difficulty: int = None,
                         adaptive_info: Dict = None, images: List = None,
                         learning_resources: List = None, session_id: str = None) -> ChatHistory:
        """Save chat message"""
        message_id = str(uuid.uuid4())
        chat_message = ChatHistory(
            id=message_id,
            user_id=user_id,
            session_id=session_id,
            message_type=message_type,
            content=content,
            topic=topic,
            difficulty=difficulty,
            adaptive_info=adaptive_info or {},
            images=images or [],
            learning_resources=learning_resources or []
        )
        
        self.db.add(chat_message)
        self.db.commit()
        self.db.refresh(chat_message)
        return chat_message
    
    def get_chat_history(self, user_id: str, limit: int = 50) -> List[ChatHistory]:
        """Get user's chat history"""
        return self.db.query(ChatHistory)\
                     .filter(ChatHistory.user_id == user_id)\
                     .order_by(desc(ChatHistory.created_at))\
                     .limit(limit)\
                     .all()
    
    # Game Scores
    def save_game_score(self, user_id: str, game_type: str, score: int,
                       topic: str = None, level: int = 1, time_taken: int = None,
                       game_data: Dict = None) -> GameScore:
        """Save game score"""
        score_id = str(uuid.uuid4())
        game_score = GameScore(
            id=score_id,
            user_id=user_id,
            game_type=game_type,
            topic=topic,
            score=score,
            level=level,
            time_taken_seconds=time_taken,
            game_data=game_data or {}
        )
        
        self.db.add(game_score)
        self.db.commit()
        self.db.refresh(game_score)
        return game_score
    
    def get_user_best_scores(self, user_id: str, game_type: str = None) -> List[GameScore]:
        """Get user's best game scores"""
        query = self.db.query(GameScore).filter(GameScore.user_id == user_id)
        if game_type:
            query = query.filter(GameScore.game_type == game_type)
        
        return query.order_by(desc(GameScore.score)).limit(10).all()
    
    # User Progress Tracking
    def update_user_progress(self, user_id: str, topic: str, performance: float,
                           difficulty: int) -> UserProgress:
        """Update user progress for a topic"""
        progress = self.db.query(UserProgress)\
                          .filter(UserProgress.user_id == user_id)\
                          .filter(UserProgress.topic == topic)\
                          .first()
        
        if not progress:
            progress = UserProgress(
                id=str(uuid.uuid4()),
                user_id=user_id,
                topic=topic,
                mastery_level=performance * 10,  # Convert to 0-100 scale
                total_interactions=1,
                average_performance=performance,
                difficulty_progression=[difficulty]
            )
            self.db.add(progress)
        else:
            # Update existing progress
            progress.total_interactions += 1
            progress.average_performance = (
                (progress.average_performance * (progress.total_interactions - 1) + performance) /
                progress.total_interactions
            )
            progress.mastery_level = min(100, progress.mastery_level + (performance - 0.5) * 5)
            progress.difficulty_progression.append(difficulty)
            progress.last_interaction = datetime.utcnow()
            progress.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(progress)
        return progress
    
    def get_user_progress(self, user_id: str) -> List[UserProgress]:
        """Get all user progress records"""
        return self.db.query(UserProgress)\
                     .filter(UserProgress.user_id == user_id)\
                     .order_by(desc(UserProgress.mastery_level))\
                     .all()
    
    # Analytics and Statistics
    def get_user_analytics(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive user analytics"""
        user = self.get_user_by_id(user_id)
        if not user:
            return {}
        
        # Quiz statistics
        quiz_results = self.db.query(QuizResult)\
                             .filter(QuizResult.user_id == user_id)\
                             .all()
        
        # Game statistics
        game_scores = self.db.query(GameScore)\
                            .filter(GameScore.user_id == user_id)\
                            .all()
        
        # Learning sessions
        sessions = self.db.query(LearningSession)\
                         .filter(LearningSession.user_id == user_id)\
                         .all()
        
        # Progress by topic
        progress_records = self.get_user_progress(user_id)
        
        return {
            "user_info": {
                "name": user.name,
                "email": user.email,
                "grade": user.grade,
                "interests": user.interests,
                "member_since": user.created_at.isoformat(),
                "total_sessions": user.total_sessions,
                "average_score": user.average_score,
                "preferred_difficulty": user.preferred_difficulty
            },
            "quiz_stats": {
                "total_quizzes": len(quiz_results),
                "total_questions": sum(q.total_questions for q in quiz_results),
                "average_score": sum(q.score_percentage for q in quiz_results) / len(quiz_results) if quiz_results else 0,
                "best_score": max(q.score_percentage for q in quiz_results) if quiz_results else 0,
                "topics_covered": list(set(q.topic for q in quiz_results))
            },
            "game_stats": {
                "total_games": len(game_scores),
                "best_scores": {
                    game_type: max(s.score for s in game_scores if s.game_type == game_type)
                    for game_type in set(s.game_type for s in game_scores)
                },
                "favorite_game": max(set(s.game_type for s in game_scores), 
                                   key=lambda x: len([s for s in game_scores if s.game_type == x])) if game_scores else None
            },
            "learning_progress": {
                topic_progress.topic: {
                    "mastery_level": topic_progress.mastery_level,
                    "interactions": topic_progress.total_interactions,
                    "average_performance": topic_progress.average_performance,
                    "last_interaction": topic_progress.last_interaction.isoformat()
                }
                for topic_progress in progress_records
            },
            "activity_summary": {
                "total_sessions": len(sessions),
                "chat_sessions": len([s for s in sessions if s.session_type == "chat"]),
                "quiz_sessions": len([s for s in sessions if s.session_type == "quiz"]),
                "game_sessions": len([s for s in sessions if s.session_type == "game"]),
                "last_activity": max(s.created_at for s in sessions).isoformat() if sessions else None
            }
        }
    
    def get_leaderboard(self, metric: str = "average_score", limit: int = 10) -> List[Dict]:
        """Get leaderboard data"""
        if metric == "average_score":
            users = self.db.query(User)\
                          .filter(User.total_sessions > 0)\
                          .order_by(desc(User.average_score))\
                          .limit(limit)\
                          .all()
            return [{"name": u.name, "score": u.average_score, "sessions": u.total_sessions} for u in users]
        
        elif metric == "total_questions":
            users = self.db.query(User)\
                          .order_by(desc(User.total_questions_answered))\
                          .limit(limit)\
                          .all()
            return [{"name": u.name, "questions": u.total_questions_answered, "sessions": u.total_sessions} for u in users]
        
        return []