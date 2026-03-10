from typing import Dict, List, Optional
import uuid
from datetime import datetime
from app.models.student import (
    StudentProfile, StudentKnowledgeProfile, DiagnosticQuizResult,
    LearningStyle, DifficultyLevel
)
from app.services.knowledge_tracing import knowledge_tracer
from app.services.adaptive_engine import adaptive_engine
from app.services.ai_service import ai_service

class OnboardingService:
    """
    Handles student onboarding process including diagnostic assessment
    and initial profile creation
    """
    
    def __init__(self):
        self.student_profiles = {}  # In production, this would be a database
        self.diagnostic_questions = self._initialize_diagnostic_questions()
        
    def create_student_profile(self, name: str, email: Optional[str] = None,
                             age_group: Optional[str] = None,
                             learning_goals: List[str] = None,
                             preferred_subjects: List[str] = None) -> StudentProfile:
        """Create initial student profile"""
        
        student_id = f"student_{uuid.uuid4().hex[:8]}"
        
        profile = StudentProfile(
            student_id=student_id,
            name=name,
            email=email,
            age_group=age_group or "adult",
            learning_goals=learning_goals or [],
            preferred_subjects=preferred_subjects or []
        )
        
        self.student_profiles[student_id] = profile
        return profile
    
    def detect_learning_style(self, responses: Dict[str, str]) -> LearningStyle:
        """
        Detect learning style based on questionnaire responses
        
        Args:
            responses: Dictionary of question_id -> answer
            
        Returns:
            Detected learning style
        """
        visual_score = 0
        auditory_score = 0
        kinesthetic_score = 0
        
        # Learning style questionnaire scoring
        style_mapping = {
            'prefer_diagrams': {'visual': 2, 'auditory': 0, 'kinesthetic': 0},
            'prefer_lectures': {'visual': 0, 'auditory': 2, 'kinesthetic': 0},
            'prefer_hands_on': {'visual': 0, 'auditory': 0, 'kinesthetic': 2},
            'remember_faces': {'visual': 2, 'auditory': 1, 'kinesthetic': 0},
            'remember_names': {'visual': 0, 'auditory': 2, 'kinesthetic': 0},
            'remember_actions': {'visual': 0, 'auditory': 0, 'kinesthetic': 2},
            'learn_by_reading': {'visual': 2, 'auditory': 0, 'kinesthetic': 0},
            'learn_by_listening': {'visual': 0, 'auditory': 2, 'kinesthetic': 0},
            'learn_by_doing': {'visual': 0, 'auditory': 0, 'kinesthetic': 2}
        }
        
        for question_id, answer in responses.items():
            if question_id in style_mapping and answer.lower() == 'yes':
                scores = style_mapping[question_id]
                visual_score += scores['visual']
                auditory_score += scores['auditory']
                kinesthetic_score += scores['kinesthetic']
        
        # Determine dominant style
        max_score = max(visual_score, auditory_score, kinesthetic_score)
        
        if max_score == 0:
            return LearningStyle.MIXED
        elif visual_score == max_score:
            return LearningStyle.VISUAL
        elif auditory_score == max_score:
            return LearningStyle.AUDITORY
        else:
            return LearningStyle.KINESTHETIC
    
    def generate_diagnostic_quiz(self, topics: List[str], 
                               questions_per_topic: int = 3) -> List[Dict]:
        """Generate diagnostic quiz for baseline assessment"""
        
        diagnostic_quiz = []
        
        for topic in topics:
            topic_questions = self.diagnostic_questions.get(topic, [])
            
            # Select questions of varying difficulty
            selected_questions = []
            
            # Easy questions
            easy_questions = [q for q in topic_questions if q.get('difficulty', 0.5) < 0.4]
            if easy_questions:
                selected_questions.extend(easy_questions[:1])
            
            # Medium questions
            medium_questions = [q for q in topic_questions if 0.4 <= q.get('difficulty', 0.5) < 0.7]
            if medium_questions:
                selected_questions.extend(medium_questions[:1])
            
            # Hard questions
            hard_questions = [q for q in topic_questions if q.get('difficulty', 0.5) >= 0.7]
            if hard_questions:
                selected_questions.extend(hard_questions[:1])
            
            # Fill remaining slots
            remaining_slots = questions_per_topic - len(selected_questions)
            if remaining_slots > 0:
                remaining_questions = [q for q in topic_questions if q not in selected_questions]
                selected_questions.extend(remaining_questions[:remaining_slots])
            
            diagnostic_quiz.extend(selected_questions)
        
        return diagnostic_quiz
    
    def process_diagnostic_results(self, student_id: str, 
                                 quiz_responses: List[Dict]) -> DiagnosticQuizResult:
        """Process diagnostic quiz results and update student profile"""
        
        # Analyze responses
        total_questions = len(quiz_responses)
        correct_answers = sum(1 for response in quiz_responses if response.get('is_correct', False))
        accuracy = correct_answers / total_questions if total_questions > 0 else 0
        
        # Calculate concept-specific scores
        concept_scores = {}
        topic_performance = {}
        
        for response in quiz_responses:
            topic = response.get('topic', 'general')
            concept = response.get('concept', topic)
            is_correct = response.get('is_correct', False)
            
            if concept not in concept_scores:
                concept_scores[concept] = {'correct': 0, 'total': 0}
            
            concept_scores[concept]['total'] += 1
            if is_correct:
                concept_scores[concept]['correct'] += 1
            
            if topic not in topic_performance:
                topic_performance[topic] = {'correct': 0, 'total': 0}
            
            topic_performance[topic]['total'] += 1
            if is_correct:
                topic_performance[topic]['correct'] += 1
        
        # Convert to accuracy scores
        concept_accuracy = {
            concept: data['correct'] / data['total'] 
            for concept, data in concept_scores.items()
        }
        
        # Create diagnostic result
        diagnostic_result = DiagnosticQuizResult(
            student_id=student_id,
            topic="diagnostic_assessment",
            questions_answered=total_questions,
            correct_answers=correct_answers,
            accuracy=accuracy,
            response_times=[response.get('response_time', 30.0) for response in quiz_responses],
            difficulty_levels=[response.get('difficulty', 0.5) for response in quiz_responses],
            concept_scores=concept_accuracy
        )
        
        # Initialize or update student knowledge profile
        topics = list(topic_performance.keys())
        skp = knowledge_tracer.initialize_student_knowledge(student_id, topics)
        skp = knowledge_tracer.update_knowledge_from_diagnostic(skp, diagnostic_result)
        
        # Update baseline knowledge in student profile
        if student_id in self.student_profiles:
            profile = self.student_profiles[student_id]
            profile.baseline_knowledge = {
                topic: data['correct'] / data['total'] 
                for topic, data in topic_performance.items()
            }
        
        return diagnostic_result
    
    def generate_initial_learning_path(self, student_id: str) -> List[Dict]:
        """Generate initial personalized learning path"""
        
        if student_id not in self.student_profiles:
            return []
        
        profile = self.student_profiles[student_id]
        
        # Get student knowledge profile
        topics = list(profile.baseline_knowledge.keys()) or profile.preferred_subjects
        if not topics:
            topics = ['python', 'machine learning', 'data science']  # Default topics
        
        skp = knowledge_tracer.initialize_student_knowledge(student_id, topics)
        
        # Generate recommendations
        recommendations = adaptive_engine.generate_personalized_lesson_plan(skp, topics)
        
        # Convert to learning path format
        learning_path = []
        for i, rec in enumerate(recommendations):
            step = {
                'step': i + 1,
                'topic': rec.recommended_topic,
                'difficulty': rec.difficulty_level.value,
                'content_type': rec.content_type,
                'reasoning': rec.reasoning,
                'estimated_time': self._estimate_completion_time(rec.content_type),
                'prerequisites': self._get_prerequisites(rec.recommended_topic)
            }
            learning_path.append(step)
        
        return learning_path
    
    def _initialize_diagnostic_questions(self) -> Dict[str, List[Dict]]:
        """Initialize diagnostic question bank"""
        return {
            'python': [
                {
                    'id': 'py_basic_1',
                    'question': 'What keyword is used to define a function in Python?',
                    'options': ['func', 'def', 'function', 'define'],
                    'correct_answer': 1,
                    'difficulty': 0.2,
                    'concept': 'functions',
                    'topic': 'python'
                },
                {
                    'id': 'py_basic_2',
                    'question': 'Which data type is mutable in Python?',
                    'options': ['tuple', 'string', 'list', 'int'],
                    'correct_answer': 2,
                    'difficulty': 0.3,
                    'concept': 'data_types',
                    'topic': 'python'
                },
                {
                    'id': 'py_inter_1',
                    'question': 'What is a closure in Python?',
                    'options': ['A loop structure', 'A function with access to outer scope', 'An error handling mechanism', 'A data structure'],
                    'correct_answer': 1,
                    'difficulty': 0.6,
                    'concept': 'advanced_functions',
                    'topic': 'python'
                },
                {
                    'id': 'py_adv_1',
                    'question': 'What is the purpose of the __init__ method in Python classes?',
                    'options': ['To initialize class variables', 'To create class instances', 'To define class methods', 'To inherit from parent classes'],
                    'correct_answer': 0,
                    'difficulty': 0.8,
                    'concept': 'object_oriented_programming',
                    'topic': 'python'
                }
            ],
            'machine learning': [
                {
                    'id': 'ml_basic_1',
                    'question': 'What is supervised learning?',
                    'options': ['Learning without labels', 'Learning with labeled data', 'Learning through rewards', 'Learning by trial and error'],
                    'correct_answer': 1,
                    'difficulty': 0.2,
                    'concept': 'learning_types',
                    'topic': 'machine learning'
                },
                {
                    'id': 'ml_inter_1',
                    'question': 'What is overfitting in machine learning?',
                    'options': ['Model is too simple', 'Model performs well on training but poorly on test data', 'Model trains too slowly', 'Model uses too much memory'],
                    'correct_answer': 1,
                    'difficulty': 0.5,
                    'concept': 'model_evaluation',
                    'topic': 'machine learning'
                },
                {
                    'id': 'ml_adv_1',
                    'question': 'What is the purpose of regularization in machine learning?',
                    'options': ['To speed up training', 'To prevent overfitting', 'To increase model complexity', 'To reduce data size'],
                    'correct_answer': 1,
                    'difficulty': 0.7,
                    'concept': 'regularization',
                    'topic': 'machine learning'
                }
            ]
        }
    
    def _estimate_completion_time(self, content_type: str) -> str:
        """Estimate completion time for different content types"""
        time_estimates = {
            'lesson': '15-20 minutes',
            'practice': '10-15 minutes',
            'quiz': '5-10 minutes',
            'assessment': '20-30 minutes',
            'game': '5-10 minutes'
        }
        return time_estimates.get(content_type, '10-15 minutes')
    
    def _get_prerequisites(self, topic: str) -> List[str]:
        """Get prerequisites for a topic"""
        prerequisites_map = {
            'machine learning': ['python', 'statistics'],
            'deep learning': ['machine learning', 'neural networks'],
            'data science': ['python', 'statistics'],
            'neural networks': ['machine learning', 'linear algebra'],
            'advanced python': ['python']
        }
        return prerequisites_map.get(topic, [])

# Global instance
onboarding_service = OnboardingService()