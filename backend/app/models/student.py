from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

class LearningStyle(str, Enum):
    VISUAL = "visual"
    AUDITORY = "auditory"
    KINESTHETIC = "kinesthetic"
    MIXED = "mixed"

class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class StudentProfile(BaseModel):
    student_id: str
    name: str
    email: Optional[str] = None
    age_group: Optional[str] = None  # "child", "teen", "adult"
    learning_style: LearningStyle = LearningStyle.MIXED
    preferred_subjects: List[str] = []
    learning_goals: List[str] = []
    baseline_knowledge: Dict[str, float] = {}  # topic -> competency score (0-1)
    created_at: datetime = datetime.now()
    last_active: datetime = datetime.now()

class StudentKnowledgeProfile(BaseModel):
    """Student Knowledge Profile (SKP) - Core competency tracking"""
    student_id: str
    knowledge_areas: Dict[str, float] = {}  # topic -> mastery level (0-100)
    learning_velocity: Dict[str, float] = {}  # topic -> learning speed
    difficulty_preferences: Dict[str, DifficultyLevel] = {}
    weak_concepts: List[str] = []
    strong_concepts: List[str] = []
    last_updated: datetime = datetime.now()
    
    # Bayesian Knowledge Tracing parameters
    prior_knowledge: Dict[str, float] = {}  # P(L0) - initial knowledge
    learning_rate: Dict[str, float] = {}    # P(T) - probability of learning
    guess_rate: Dict[str, float] = {}       # P(G) - probability of guessing
    slip_rate: Dict[str, float] = {}        # P(S) - probability of slipping

class DiagnosticQuizResult(BaseModel):
    student_id: str
    topic: str
    questions_answered: int
    correct_answers: int
    accuracy: float
    response_times: List[float]  # seconds per question
    difficulty_levels: List[int]  # difficulty of each question
    concept_scores: Dict[str, float]  # concept -> accuracy
    completed_at: datetime = datetime.now()

class LearningSession(BaseModel):
    session_id: str
    student_id: str
    topic: str
    start_time: datetime
    end_time: Optional[datetime] = None
    activities: List[str] = []  # ["chat", "quiz", "game"]
    engagement_score: float = 0.0  # 0-1 based on interaction quality
    learning_progress: Dict[str, float] = {}  # concept -> progress made
    
class AdaptiveRecommendation(BaseModel):
    student_id: str
    recommended_topic: str
    difficulty_level: DifficultyLevel
    content_type: str  # "lesson", "quiz", "game", "review"
    reasoning: str
    confidence_score: float  # 0-1
    generated_at: datetime = datetime.now()