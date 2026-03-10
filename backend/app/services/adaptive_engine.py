from typing import Dict, List, Optional, Tuple
import numpy as np
from datetime import datetime, timedelta
import random
from app.models.student import (
    StudentKnowledgeProfile, AdaptiveRecommendation, 
    DifficultyLevel, LearningStyle
)
from app.services.knowledge_tracing import knowledge_tracer, spaced_repetition

class ItemResponseTheory:
    """
    Item Response Theory (IRT) implementation for optimal question selection
    """
    
    def __init__(self):
        # Question parameters (would be learned from data in production)
        self.question_bank = {}  # question_id -> {'difficulty': float, 'discrimination': float}
        
    def estimate_ability(self, responses: List[Tuple[str, bool, float]]) -> float:
        """
        Estimate student ability (theta) based on responses
        
        Args:
            responses: List of (question_id, is_correct, difficulty) tuples
            
        Returns:
            Estimated ability level (-3 to +3, where 0 is average)
        """
        if not responses:
            return 0.0
        
        # Simple ability estimation based on weighted accuracy
        total_weight = 0
        weighted_score = 0
        
        for question_id, is_correct, difficulty in responses:
            weight = 1.0 + difficulty  # Harder questions weighted more
            total_weight += weight
            if is_correct:
                weighted_score += weight
        
        if total_weight == 0:
            return 0.0
        
        # Convert to theta scale (-3 to +3)
        accuracy = weighted_score / total_weight
        theta = (accuracy - 0.5) * 6  # Scale to -3 to +3
        return max(-3, min(3, theta))
    
    def select_optimal_question(self, student_ability: float, 
                              available_questions: List[Dict]) -> Optional[Dict]:
        """
        Select the most informative question for the student
        
        Args:
            student_ability: Current estimated ability (theta)
            available_questions: List of question dictionaries
            
        Returns:
            Optimal question or None if no questions available
        """
        if not available_questions:
            return None
        
        best_question = None
        max_information = 0
        
        for question in available_questions:
            difficulty = question.get('difficulty', 0.5)
            discrimination = question.get('discrimination', 1.0)
            
            # Calculate Fisher Information
            information = self._calculate_information(student_ability, difficulty, discrimination)
            
            if information > max_information:
                max_information = information
                best_question = question
        
        return best_question
    
    def _calculate_information(self, theta: float, difficulty: float, discrimination: float) -> float:
        """Calculate Fisher Information for a question"""
        # Convert difficulty to IRT scale
        b = (difficulty - 0.5) * 4  # Scale to -2 to +2
        a = discrimination
        
        # Probability of correct response
        p = 1 / (1 + np.exp(-a * (theta - b)))
        
        # Fisher Information
        information = a**2 * p * (1 - p)
        
        return information

class AdaptiveEngine:
    """
    Main adaptive engine that orchestrates personalized learning
    """
    
    def __init__(self):
        self.irt = ItemResponseTheory()
        self.difficulty_adjustment_rate = 0.1
        
    def generate_personalized_lesson_plan(self, skp: StudentKnowledgeProfile, 
                                        target_topics: List[str]) -> List[AdaptiveRecommendation]:
        """Generate personalized learning sequence"""
        recommendations = []
        
        for topic in target_topics:
            mastery_status = knowledge_tracer.get_mastery_status(skp, topic)
            
            # Determine content type based on mastery and learning velocity
            content_type = self._select_content_type(mastery_status)
            
            # Determine difficulty level
            difficulty = self._select_difficulty_level(skp, topic)
            
            # Generate recommendation
            recommendation = AdaptiveRecommendation(
                student_id=skp.student_id,
                recommended_topic=topic,
                difficulty_level=difficulty,
                content_type=content_type,
                reasoning=self._generate_reasoning(mastery_status, content_type),
                confidence_score=mastery_status['mastery_probability']
            )
            
            recommendations.append(recommendation)
        
        # Sort by priority (lowest mastery first, but consider prerequisites)
        recommendations.sort(key=lambda x: x.confidence_score)
        
        return recommendations
    
    def adapt_difficulty_real_time(self, skp: StudentKnowledgeProfile, 
                                 topic: str, recent_performance: List[bool]) -> float:
        """
        Adapt difficulty in real-time based on recent performance
        
        Args:
            skp: Student knowledge profile
            topic: Current topic
            recent_performance: List of recent correct/incorrect responses
            
        Returns:
            Adjusted difficulty level (0.0 to 1.0)
        """
        current_mastery = skp.knowledge_areas.get(topic, 50) / 100
        
        if not recent_performance:
            return current_mastery
        
        # Calculate recent accuracy
        recent_accuracy = sum(recent_performance) / len(recent_performance)
        
        # Adjust difficulty based on performance
        if recent_accuracy > 0.8:
            # Too easy - increase difficulty
            new_difficulty = min(1.0, current_mastery + self.difficulty_adjustment_rate)
        elif recent_accuracy < 0.4:
            # Too hard - decrease difficulty
            new_difficulty = max(0.1, current_mastery - self.difficulty_adjustment_rate)
        else:
            # Just right - maintain current level
            new_difficulty = current_mastery
        
        return new_difficulty
    
    def select_next_question(self, skp: StudentKnowledgeProfile, topic: str, 
                           question_pool: List[Dict]) -> Optional[Dict]:
        """Select the most appropriate next question using IRT"""
        
        # Estimate student ability for this topic
        mastery_level = skp.knowledge_areas.get(topic, 50) / 100
        student_ability = (mastery_level - 0.5) * 4  # Convert to theta scale
        
        # Filter questions by topic and difficulty appropriateness
        appropriate_questions = []
        target_difficulty = mastery_level
        
        for question in question_pool:
            if question.get('topic') == topic:
                q_difficulty = question.get('difficulty', 0.5)
                # Select questions within reasonable difficulty range
                if abs(q_difficulty - target_difficulty) <= 0.3:
                    appropriate_questions.append(question)
        
        if not appropriate_questions:
            return None
        
        # Use IRT to select optimal question
        return self.irt.select_optimal_question(student_ability, appropriate_questions)
    
    def generate_spaced_repetition_schedule(self, skp: StudentKnowledgeProfile) -> Dict[str, datetime]:
        """Generate spaced repetition schedule for weak concepts"""
        schedule = {}
        
        for concept in skp.weak_concepts:
            # Calculate review interval based on mastery level
            mastery = skp.knowledge_areas.get(concept, 10) / 100
            
            if mastery < 0.3:
                # Very weak - review tomorrow
                next_review = datetime.now() + timedelta(days=1)
            elif mastery < 0.5:
                # Weak - review in 3 days
                next_review = datetime.now() + timedelta(days=3)
            elif mastery < 0.7:
                # Moderate - review in a week
                next_review = datetime.now() + timedelta(days=7)
            else:
                # Getting stronger - review in 2 weeks
                next_review = datetime.now() + timedelta(days=14)
            
            schedule[concept] = next_review
        
        return schedule
    
    def predict_learning_outcome(self, skp: StudentKnowledgeProfile, 
                               topic: str, intervention_type: str) -> Dict[str, float]:
        """Predict learning outcome for different interventions"""
        current_mastery = skp.knowledge_areas.get(topic, 10) / 100
        learning_velocity = skp.learning_velocity.get(topic, 0.0)
        
        predictions = {}
        
        # Base prediction without intervention
        base_improvement = learning_velocity * 0.1
        predictions['no_intervention'] = min(1.0, current_mastery + base_improvement)
        
        # Intervention-specific predictions
        intervention_effects = {
            'additional_practice': 0.15,
            'different_explanation': 0.20,
            'visual_aids': 0.18,
            'interactive_game': 0.12,
            'peer_collaboration': 0.16,
            'one_on_one_tutoring': 0.25
        }
        
        effect = intervention_effects.get(intervention_type, 0.10)
        predictions[intervention_type] = min(1.0, current_mastery + base_improvement + effect)
        
        return predictions
    
    def _select_content_type(self, mastery_status: Dict) -> str:
        """Select appropriate content type based on mastery status"""
        mastery_prob = mastery_status['mastery_probability']
        recommended_action = mastery_status['recommended_action']
        
        if recommended_action == "advance_to_next_topic":
            return "assessment"
        elif recommended_action == "reteach_with_different_approach":
            return "lesson"
        elif recommended_action == "continue_practice":
            return "practice"
        elif mastery_prob < 0.3:
            return "lesson"
        elif mastery_prob < 0.6:
            return "practice"
        else:
            return "quiz"
    
    def _select_difficulty_level(self, skp: StudentKnowledgeProfile, topic: str) -> DifficultyLevel:
        """Select appropriate difficulty level"""
        mastery = skp.knowledge_areas.get(topic, 10) / 100
        
        if mastery < 0.4:
            return DifficultyLevel.BEGINNER
        elif mastery < 0.7:
            return DifficultyLevel.INTERMEDIATE
        else:
            return DifficultyLevel.ADVANCED
    
    def _generate_reasoning(self, mastery_status: Dict, content_type: str) -> str:
        """Generate human-readable reasoning for recommendation"""
        mastery_prob = mastery_status['mastery_probability']
        confidence = mastery_status['confidence_level']
        
        if content_type == "lesson":
            return f"Mastery level is {confidence.lower()} ({mastery_prob:.1%}). New lesson recommended to build foundation."
        elif content_type == "practice":
            return f"Mastery level is {confidence.lower()} ({mastery_prob:.1%}). Practice exercises recommended to reinforce learning."
        elif content_type == "quiz":
            return f"Mastery level is {confidence.lower()} ({mastery_prob:.1%}). Assessment recommended to evaluate understanding."
        else:
            return f"Based on current mastery level ({mastery_prob:.1%}), {content_type} is recommended."

# Global instance
adaptive_engine = AdaptiveEngine()