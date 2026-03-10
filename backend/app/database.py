from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ai_studybot.db")

# Create engine
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Database Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    age = Column(Integer, nullable=True)
    grade = Column(String, nullable=True)
    interests = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Learning profile fields
    total_sessions = Column(Integer, default=0)
    total_questions_answered = Column(Integer, default=0)
    average_score = Column(Float, default=0.0)
    preferred_difficulty = Column(Integer, default=1)
    learning_style = Column(String, default="visual")

class LearningSession(Base):
    __tablename__ = "learning_sessions"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    session_type = Column(String, nullable=False)  # chat, quiz, game
    topic = Column(String, nullable=True)
    difficulty = Column(Integer, default=1)
    score = Column(Float, nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    questions_answered = Column(Integer, default=0)
    correct_answers = Column(Integer, default=0)
    session_data = Column(JSON, default=dict)  # Store additional session info
    created_at = Column(DateTime, default=datetime.utcnow)

class QuizResult(Base):
    __tablename__ = "quiz_results"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    session_id = Column(String, nullable=True)
    topic = Column(String, nullable=False)
    difficulty = Column(Integer, default=1)
    total_questions = Column(Integer, nullable=False)
    correct_answers = Column(Integer, nullable=False)
    score_percentage = Column(Float, nullable=False)
    time_taken_seconds = Column(Integer, nullable=True)
    weak_areas = Column(JSON, default=list)
    strong_areas = Column(JSON, default=list)
    quiz_data = Column(JSON, default=dict)  # Store questions and answers
    created_at = Column(DateTime, default=datetime.utcnow)

class ChatHistory(Base):
    __tablename__ = "chat_history"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    session_id = Column(String, nullable=True)
    message_type = Column(String, nullable=False)  # user, assistant
    content = Column(Text, nullable=False)
    topic = Column(String, nullable=True)
    difficulty = Column(Integer, nullable=True)
    adaptive_info = Column(JSON, default=dict)
    images = Column(JSON, default=list)
    learning_resources = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)

class GameScore(Base):
    __tablename__ = "game_scores"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    game_type = Column(String, nullable=False)
    topic = Column(String, nullable=True)
    score = Column(Integer, nullable=False)
    level = Column(Integer, default=1)
    time_taken_seconds = Column(Integer, nullable=True)
    game_data = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

class UserProgress(Base):
    __tablename__ = "user_progress"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    topic = Column(String, nullable=False)
    mastery_level = Column(Float, default=0.0)  # 0-100
    learning_velocity = Column(Float, default=0.0)
    last_interaction = Column(DateTime, default=datetime.utcnow)
    total_interactions = Column(Integer, default=0)
    average_performance = Column(Float, default=0.0)
    difficulty_progression = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create all tables
def create_tables():
    Base.metadata.create_all(bind=engine)

# Initialize database
def init_db():
    create_tables()
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_db()