from fastapi import APIRouter, HTTPException
from typing import List, Dict, Optional
from pydantic import BaseModel
from app.services.onboarding_service import onboarding_service
from app.models.student import LearningStyle

router = APIRouter()

class StudentRegistration(BaseModel):
    name: str
    email: Optional[str] = None
    age_group: Optional[str] = None  # "child", "teen", "adult"
    learning_goals: List[str] = []
    preferred_subjects: List[str] = []

class LearningStyleAssessment(BaseModel):
    student_id: str
    responses: Dict[str, str]  # question_id -> answer

class DiagnosticQuizRequest(BaseModel):
    student_id: str
    topics: List[str]
    questions_per_topic: int = 3

class DiagnosticResponse(BaseModel):
    student_id: str
    responses: List[Dict]  # List of question responses

@router.post("/register")
async def register_student(registration: StudentRegistration):
    """Register a new student and create initial profile"""
    try:
        profile = onboarding_service.create_student_profile(
            name=registration.name,
            email=registration.email,
            age_group=registration.age_group,
            learning_goals=registration.learning_goals,
            preferred_subjects=registration.preferred_subjects
        )
        
        return {
            "student_id": profile.student_id,
            "message": "Student registered successfully",
            "profile": profile.dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/learning-style-questionnaire")
async def get_learning_style_questionnaire():
    """Get learning style assessment questionnaire"""
    questionnaire = [
        {
            "id": "prefer_diagrams",
            "question": "Do you prefer learning through diagrams and visual aids?",
            "type": "yes_no"
        },
        {
            "id": "prefer_lectures",
            "question": "Do you learn best by listening to lectures or audio content?",
            "type": "yes_no"
        },
        {
            "id": "prefer_hands_on",
            "question": "Do you prefer hands-on activities and practical exercises?",
            "type": "yes_no"
        },
        {
            "id": "remember_faces",
            "question": "Do you easily remember faces but forget names?",
            "type": "yes_no"
        },
        {
            "id": "remember_names",
            "question": "Do you easily remember names and spoken information?",
            "type": "yes_no"
        },
        {
            "id": "remember_actions",
            "question": "Do you best remember things you've physically done?",
            "type": "yes_no"
        },
        {
            "id": "learn_by_reading",
            "question": "Do you prefer to learn by reading text and written materials?",
            "type": "yes_no"
        },
        {
            "id": "learn_by_listening",
            "question": "Do you prefer to learn by listening to explanations?",
            "type": "yes_no"
        },
        {
            "id": "learn_by_doing",
            "question": "Do you prefer to learn by doing and practicing?",
            "type": "yes_no"
        }
    ]
    
    return {
        "questionnaire": questionnaire,
        "instructions": "Answer 'yes' or 'no' to each question based on your learning preferences."
    }

@router.post("/assess-learning-style")
async def assess_learning_style(assessment: LearningStyleAssessment):
    """Assess student's learning style based on questionnaire responses"""
    try:
        learning_style = onboarding_service.detect_learning_style(assessment.responses)
        
        # Update student profile with learning style
        if assessment.student_id in onboarding_service.student_profiles:
            profile = onboarding_service.student_profiles[assessment.student_id]
            profile.learning_style = learning_style
        
        style_descriptions = {
            LearningStyle.VISUAL: "You learn best through visual aids like diagrams, charts, and images. Visual representations help you understand and remember information.",
            LearningStyle.AUDITORY: "You learn best through listening to explanations, discussions, and audio content. You prefer verbal instructions and benefit from talking through problems.",
            LearningStyle.KINESTHETIC: "You learn best through hands-on activities and physical practice. You prefer to learn by doing and benefit from interactive exercises.",
            LearningStyle.MIXED: "You have a balanced learning style and can benefit from various teaching methods including visual, auditory, and hands-on approaches."
        }
        
        return {
            "student_id": assessment.student_id,
            "learning_style": learning_style.value,
            "description": style_descriptions[learning_style],
            "recommendations": get_learning_style_recommendations(learning_style)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-diagnostic-quiz")
async def generate_diagnostic_quiz(request: DiagnosticQuizRequest):
    """Generate diagnostic quiz for baseline assessment"""
    try:
        quiz = onboarding_service.generate_diagnostic_quiz(
            topics=request.topics,
            questions_per_topic=request.questions_per_topic
        )
        
        return {
            "student_id": request.student_id,
            "quiz": quiz,
            "instructions": "This diagnostic quiz will help us understand your current knowledge level. Answer all questions to the best of your ability.",
            "estimated_time": f"{len(quiz) * 2} minutes"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/submit-diagnostic-results")
async def submit_diagnostic_results(response: DiagnosticResponse):
    """Process diagnostic quiz results and generate initial learning path"""
    try:
        # Process diagnostic results
        diagnostic_result = onboarding_service.process_diagnostic_results(
            student_id=response.student_id,
            quiz_responses=response.responses
        )
        
        # Generate initial learning path
        learning_path = onboarding_service.generate_initial_learning_path(response.student_id)
        
        # Generate performance summary
        performance_summary = {
            "overall_accuracy": diagnostic_result.accuracy,
            "questions_answered": diagnostic_result.questions_answered,
            "correct_answers": diagnostic_result.correct_answers,
            "performance_level": get_performance_level(diagnostic_result.accuracy),
            "concept_scores": diagnostic_result.concept_scores,
            "strong_areas": [concept for concept, score in diagnostic_result.concept_scores.items() if score >= 0.7],
            "areas_for_improvement": [concept for concept, score in diagnostic_result.concept_scores.items() if score < 0.5]
        }
        
        return {
            "student_id": response.student_id,
            "diagnostic_complete": True,
            "performance_summary": performance_summary,
            "learning_path": learning_path,
            "next_steps": generate_next_steps(performance_summary, learning_path)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/student-profile/{student_id}")
async def get_student_profile(student_id: str):
    """Get complete student profile including onboarding status"""
    try:
        if student_id not in onboarding_service.student_profiles:
            raise HTTPException(status_code=404, detail="Student not found")
        
        profile = onboarding_service.student_profiles[student_id]
        
        # Check onboarding completion status
        onboarding_status = {
            "registration_complete": True,
            "learning_style_assessed": profile.learning_style != LearningStyle.MIXED,
            "diagnostic_complete": bool(profile.baseline_knowledge),
            "ready_for_learning": bool(profile.baseline_knowledge)
        }
        
        return {
            "profile": profile.dict(),
            "onboarding_status": onboarding_status,
            "completion_percentage": calculate_onboarding_completion(onboarding_status)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def get_learning_style_recommendations(learning_style: LearningStyle) -> List[str]:
    """Get personalized recommendations based on learning style"""
    recommendations = {
        LearningStyle.VISUAL: [
            "Use diagrams and flowcharts to understand concepts",
            "Take advantage of visual aids and infographics",
            "Create mind maps to organize information",
            "Use color coding for different topics",
            "Watch educational videos and animations"
        ],
        LearningStyle.AUDITORY: [
            "Listen to educational podcasts and audio content",
            "Participate in discussions and study groups",
            "Read aloud when studying",
            "Use text-to-speech features",
            "Explain concepts out loud to reinforce learning"
        ],
        LearningStyle.KINESTHETIC: [
            "Engage with interactive simulations and games",
            "Take frequent breaks during study sessions",
            "Use hands-on practice and coding exercises",
            "Walk around while reviewing material",
            "Use physical objects to represent abstract concepts"
        ],
        LearningStyle.MIXED: [
            "Combine visual, auditory, and hands-on learning methods",
            "Experiment with different study techniques",
            "Use multimedia resources that engage multiple senses",
            "Adapt your approach based on the subject matter",
            "Take advantage of all available learning tools"
        ]
    }
    return recommendations.get(learning_style, [])

def get_performance_level(accuracy: float) -> str:
    """Convert accuracy to performance level"""
    if accuracy >= 0.9:
        return "Excellent"
    elif accuracy >= 0.8:
        return "Very Good"
    elif accuracy >= 0.7:
        return "Good"
    elif accuracy >= 0.6:
        return "Average"
    elif accuracy >= 0.5:
        return "Below Average"
    else:
        return "Needs Significant Improvement"

def generate_next_steps(performance_summary: Dict, learning_path: List[Dict]) -> List[str]:
    """Generate personalized next steps based on diagnostic results"""
    next_steps = []
    
    accuracy = performance_summary["overall_accuracy"]
    
    if accuracy < 0.5:
        next_steps.append("Start with foundational concepts to build a strong base")
        next_steps.append("Focus on understanding basic principles before moving to advanced topics")
    elif accuracy < 0.7:
        next_steps.append("Review areas for improvement while building on your strengths")
        next_steps.append("Practice with interactive exercises to reinforce learning")
    else:
        next_steps.append("You're ready for more challenging material")
        next_steps.append("Consider exploring advanced topics in your strong areas")
    
    if learning_path:
        first_topic = learning_path[0]["topic"]
        next_steps.append(f"Begin your personalized learning journey with {first_topic}")
    
    next_steps.append("Take regular quizzes to track your progress")
    next_steps.append("Use the dashboard to monitor your learning achievements")
    
    return next_steps

def calculate_onboarding_completion(status: Dict[str, bool]) -> int:
    """Calculate onboarding completion percentage"""
    total_steps = len(status)
    completed_steps = sum(1 for completed in status.values() if completed)
    return int((completed_steps / total_steps) * 100)