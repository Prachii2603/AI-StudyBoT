from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: Optional[datetime] = None

class ChatRequest(BaseModel):
    message: str
    student_id: str
    difficulty_level: int = 1

class QuizQuestion(BaseModel):
    id: str
    question: str
    options: List[str]
    correct_answer: int
    difficulty: int

class QuizAnswer(BaseModel):
    question_id: str
    student_id: str
    answer: int

class StudentProgress(BaseModel):
    student_id: str
    points: int = 0
    level: int = 1
    badges: List[str] = []
    topics_mastered: List[str] = []
