import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import math
from app.models.student import StudentKnowledgeProfile, DiagnosticQuizResult, LearningSession

class BayesianKnowledgeTracing:
    """
    Bayesian Knowledge Tracing (BKT) implementation for adaptive learning
    Tracks student knowledge state and predicts mastery probability
    """
    
    def __init__(self):
        # Default BKT parameters
        self.default_params = {
            'prior_knowledge': 0.1,    # P(L0) - initial knowledge probability
            'learning_rate': 0.3,      # P(T) - probability of learning from instruction
            'guess_rate': 0.2,         # P(G) - probability of guessing correctly
            'slip_rate': 0.1           # P(S) - probability of slipping (knowing but answering wrong)
        }
        
        # Mastery threshold
        self.mastery_threshold = 0.8
        
    def initialize_student_knowledge(self, student_id: str, topics: List[str]) -> StudentKnowledgeProfile:
        """Initialize knowledge profile for new student"""
        skp = StudentKnowledgeProfile(student_id=student_id)
        
        for topic in topics:
            skp.prior_knowledge[topic] = self.default_params['prior_knowledge']
            skp.learning_rate[topic] = self.default_params['learning_rate']
            skp.guess_rate[topic] = self.default_params['guess_rate']
            skp.slip_rate[topic] = self.default_params['slip_rate']
            skp.knowledge_areas[topic] = self.default_params['prior_knowledge'] * 100
            
        return skp
    
    def update_knowledge_from_diagnostic(self, skp: StudentKnowledgeProfile, 
                                       diagnostic_result: DiagnosticQuizResult) -> StudentKnowledgeProfile:
        """Update knowledge profile based on diagnostic quiz results"""
        topic = diagnostic_result.topic
        accuracy = diagnostic_result.accuracy
        
        # Update based on overall performance
        if accuracy > 0.8:
            # High performance - increase prior knowledge
            skp.prior_knowledge[topic] = min(0.9, skp.prior_knowledge.get(topic, 0.1) + 0.2)
            skp.knowledge_areas[topic] = min(95, skp.knowledge_areas.get(topic, 10) + 20)
        elif accuracy > 0.6:
            # Medium performance
            skp.prior_knowledge[topic] = min(0.7, skp.prior_knowledge.get(topic, 0.1) + 0.1)
            skp.knowledge_areas[topic] = min(80, skp.knowledge_areas.get(topic, 10) + 15)
        else:
            # Low performance - keep low prior knowledge
            skp.prior_knowledge[topic] = max(0.05, skp.prior_knowledge.get(topic, 0.1))
            skp.knowledge_areas[topic] = max(5, skp.knowledge_areas.get(topic, 10))
        
        # Update concept-specific scores
        for concept, score in diagnostic_result.concept_scores.items():
            if score > 0.7:
                if concept not in skp.strong_concepts:
                    skp.strong_concepts.append(concept)
                if concept in skp.weak_concepts:
                    skp.weak_concepts.remove(concept)
            elif score < 0.4:
                if concept not in skp.weak_concepts:
                    skp.weak_concepts.append(concept)
                if concept in skp.strong_concepts:
                    skp.strong_concepts.remove(concept)
        
        skp.last_updated = datetime.now()
        return skp
    
    def update_knowledge_from_interaction(self, skp: StudentKnowledgeProfile, 
                                        topic: str, is_correct: bool, 
                                        difficulty: float = 0.5) -> Tuple[StudentKnowledgeProfile, float]:
        """
        Update knowledge state based on single interaction using BKT
        Returns updated profile and new mastery probability
        """
        # Get current parameters
        P_L_prev = skp.knowledge_areas.get(topic, 10) / 100  # Previous mastery probability
        P_T = skp.learning_rate.get(topic, self.default_params['learning_rate'])
        P_G = skp.guess_rate.get(topic, self.default_params['guess_rate'])
        P_S = skp.slip_rate.get(topic, self.default_params['slip_rate'])
        
        # Adjust parameters based on difficulty
        P_G = max(0.05, P_G - (difficulty - 0.5) * 0.2)  # Harder questions = less guessing
        P_S = min(0.3, P_S + (difficulty - 0.5) * 0.1)   # Harder questions = more slipping
        
        # Calculate probability of correct response given knowledge state
        if is_correct:
            # P(correct | learned) = 1 - P_S, P(correct | not learned) = P_G
            P_correct_given_learned = 1 - P_S
            P_correct_given_not_learned = P_G
            
            # Bayes' theorem to update knowledge probability
            numerator = P_L_prev * P_correct_given_learned
            denominator = P_L_prev * P_correct_given_learned + (1 - P_L_prev) * P_correct_given_not_learned
        else:
            # P(incorrect | learned) = P_S, P(incorrect | not learned) = 1 - P_G
            P_incorrect_given_learned = P_S
            P_incorrect_given_not_learned = 1 - P_G
            
            numerator = P_L_prev * P_incorrect_given_learned
            denominator = P_L_prev * P_incorrect_given_learned + (1 - P_L_prev) * P_incorrect_given_not_learned
        
        # Update mastery probability
        if denominator > 0:
            P_L_current = numerator / denominator
        else:
            P_L_current = P_L_prev
        
        # Apply learning opportunity (student had chance to learn)
        P_L_after_learning = P_L_current + (1 - P_L_current) * P_T
        
        # Update knowledge profile
        skp.knowledge_areas[topic] = min(99, max(1, P_L_after_learning * 100))
        
        # Update learning velocity (how quickly student is improving)
        if topic not in skp.learning_velocity:
            skp.learning_velocity[topic] = 0.0
        
        velocity_change = (P_L_after_learning - P_L_prev) * 10  # Scale for visibility
        skp.learning_velocity[topic] = 0.7 * skp.learning_velocity[topic] + 0.3 * velocity_change
        
        skp.last_updated = datetime.now()
        
        return skp, P_L_after_learning
    
    def predict_performance(self, skp: StudentKnowledgeProfile, topic: str, difficulty: float) -> float:
        """Predict probability of correct response for given topic and difficulty"""
        P_L = skp.knowledge_areas.get(topic, 10) / 100
        P_G = max(0.05, skp.guess_rate.get(topic, self.default_params['guess_rate']) - (difficulty - 0.5) * 0.2)
        P_S = min(0.3, skp.slip_rate.get(topic, self.default_params['slip_rate']) + (difficulty - 0.5) * 0.1)
        
        # P(correct) = P(learned) * P(correct|learned) + P(not learned) * P(correct|not learned)
        P_correct = P_L * (1 - P_S) + (1 - P_L) * P_G
        
        return P_correct
    
    def get_mastery_status(self, skp: StudentKnowledgeProfile, topic: str) -> Dict[str, any]:
        """Get detailed mastery status for a topic"""
        mastery_prob = skp.knowledge_areas.get(topic, 10) / 100
        
        status = {
            'topic': topic,
            'mastery_probability': mastery_prob,
            'is_mastered': mastery_prob >= self.mastery_threshold,
            'confidence_level': self._get_confidence_level(mastery_prob),
            'learning_velocity': skp.learning_velocity.get(topic, 0.0),
            'recommended_action': self._get_recommended_action(mastery_prob, skp.learning_velocity.get(topic, 0.0))
        }
        
        return status
    
    def _get_confidence_level(self, mastery_prob: float) -> str:
        """Convert mastery probability to confidence level"""
        if mastery_prob >= 0.9:
            return "Very High"
        elif mastery_prob >= 0.8:
            return "High"
        elif mastery_prob >= 0.6:
            return "Medium"
        elif mastery_prob >= 0.4:
            return "Low"
        else:
            return "Very Low"
    
    def _get_recommended_action(self, mastery_prob: float, learning_velocity: float) -> str:
        """Recommend next action based on mastery and learning velocity"""
        if mastery_prob >= self.mastery_threshold:
            return "advance_to_next_topic"
        elif mastery_prob >= 0.6 and learning_velocity > 0.1:
            return "continue_practice"
        elif mastery_prob < 0.4:
            return "reteach_with_different_approach"
        elif learning_velocity < 0.05:
            return "provide_additional_support"
        else:
            return "continue_current_approach"

class SpacedRepetitionScheduler:
    """
    SM-2 Algorithm implementation for spaced repetition
    Schedules review sessions based on forgetting curve
    """
    
    def __init__(self):
        self.default_easiness = 2.5
        self.min_easiness = 1.3
        
    def calculate_next_review(self, quality: int, repetition: int, 
                            easiness: float, interval: int) -> Tuple[int, float, int]:
        """
        Calculate next review interval using SM-2 algorithm
        
        Args:
            quality: Response quality (0-5, where 3+ is correct)
            repetition: Number of repetitions
            easiness: Easiness factor
            interval: Current interval in days
            
        Returns:
            (new_interval, new_easiness, new_repetition)
        """
        if quality >= 3:
            # Correct response
            if repetition == 0:
                new_interval = 1
            elif repetition == 1:
                new_interval = 6
            else:
                new_interval = round(interval * easiness)
            
            new_repetition = repetition + 1
        else:
            # Incorrect response - reset
            new_interval = 1
            new_repetition = 0
        
        # Update easiness factor
        new_easiness = easiness + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        new_easiness = max(self.min_easiness, new_easiness)
        
        return new_interval, new_easiness, new_repetition
    
    def get_due_topics(self, student_reviews: Dict[str, Dict]) -> List[str]:
        """Get list of topics due for review"""
        due_topics = []
        current_date = datetime.now().date()
        
        for topic, review_data in student_reviews.items():
            next_review_date = review_data.get('next_review_date')
            if next_review_date and current_date >= next_review_date:
                due_topics.append(topic)
        
        return due_topics

# Global instances
knowledge_tracer = BayesianKnowledgeTracing()
spaced_repetition = SpacedRepetitionScheduler()