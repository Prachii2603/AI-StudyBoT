from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json

class PersonalizedLearningService:
    """
    Enhanced personalized learning service that provides:
    - Wrong answer explanations and remediation
    - Progress tracking and analytics
    - Gamification elements (points, badges, leaderboards)
    """
    
    def __init__(self):
        self.concept_explanations = self._load_concept_explanations()
        self.badge_definitions = self._load_badge_definitions()
        self.point_system = self._load_point_system()
    
    def _load_concept_explanations(self) -> Dict[str, Dict]:
        """Load concept explanations for different topics"""
        return {
            "machine_learning": {
                "basic": {
                    "explanation": "Machine Learning is like teaching a computer to learn patterns from examples, just like how you learn to recognize faces by seeing many different faces.",
                    "examples": [
                        "Email spam detection: The computer learns from thousands of emails marked as 'spam' or 'not spam'",
                        "Photo recognition: The computer learns to identify cats by looking at thousands of cat photos",
                        "Music recommendations: The computer learns your music taste from songs you like/dislike"
                    ],
                    "resources": [
                        {"title": "Machine Learning Explained Simply", "url": "https://www.youtube.com/watch?v=aircAruvnKk", "type": "video"},
                        {"title": "ML for Beginners - Interactive Course", "url": "https://www.khanacademy.org/computing/intro-to-programming", "type": "interactive"},
                        {"title": "What is Machine Learning?", "url": "https://en.wikipedia.org/wiki/Machine_learning", "type": "article"}
                    ]
                },
                "intermediate": {
                    "explanation": "Machine Learning uses algorithms to find patterns in data and make predictions. There are three main types: supervised (learning from labeled examples), unsupervised (finding hidden patterns), and reinforcement learning (learning through trial and error).",
                    "examples": [
                        "Supervised: Predicting house prices based on size, location, and features",
                        "Unsupervised: Grouping customers by shopping behavior without knowing the groups beforehand",
                        "Reinforcement: Training a game AI that gets better by playing many games"
                    ],
                    "resources": [
                        {"title": "Machine Learning Course", "url": "https://www.coursera.org/learn/machine-learning", "type": "course"},
                        {"title": "Hands-on ML with Python", "url": "https://www.kaggle.com/learn/intro-to-machine-learning", "type": "interactive"},
                        {"title": "ML Algorithms Explained", "url": "https://towardsdatascience.com/machine-learning-algorithms-explained", "type": "article"}
                    ]
                }
            },
            "python": {
                "basic": {
                    "explanation": "Python is a programming language that's easy to read and write. Think of it like giving instructions to a computer in a way that's almost like English.",
                    "examples": [
                        "print('Hello World') - tells the computer to display 'Hello World'",
                        "name = 'Alice' - stores the word 'Alice' in a box called 'name'",
                        "if age > 18: print('Adult') - checks if someone is over 18 and says 'Adult'"
                    ],
                    "resources": [
                        {"title": "Python for Beginners", "url": "https://www.python.org/about/gettingstarted/", "type": "tutorial"},
                        {"title": "Interactive Python Course", "url": "https://www.codecademy.com/learn/learn-python-3", "type": "interactive"},
                        {"title": "Python Basics Video", "url": "https://www.youtube.com/watch?v=rfscVS0vtbw", "type": "video"}
                    ]
                }
            },
            "neural_networks": {
                "basic": {
                    "explanation": "Neural networks are inspired by how our brain works. Just like our brain has neurons that connect and send signals, artificial neural networks have nodes that process information and pass it along.",
                    "examples": [
                        "Image recognition: Each layer of the network looks for different features (edges, shapes, objects)",
                        "Language translation: The network learns patterns between languages",
                        "Game playing: The network learns winning strategies by playing many games"
                    ],
                    "resources": [
                        {"title": "Neural Networks Explained", "url": "https://www.youtube.com/watch?v=aircAruvnKk", "type": "video"},
                        {"title": "Interactive Neural Network", "url": "https://playground.tensorflow.org/", "type": "interactive"},
                        {"title": "Neural Networks Basics", "url": "https://en.wikipedia.org/wiki/Artificial_neural_network", "type": "article"}
                    ]
                }
            }
        }
    
    def _load_badge_definitions(self) -> Dict[str, Dict]:
        """Define available badges and their requirements"""
        return {
            "quiz_master": {
                "name": "Quiz Master",
                "description": "Complete 10 quizzes with 80%+ average score",
                "icon": "🏆",
                "requirements": {"quizzes_completed": 10, "min_average_score": 0.8},
                "points": 500
            },
            "fast_learner": {
                "name": "Fast Learner",
                "description": "Answer 5 questions correctly in under 30 seconds each",
                "icon": "⚡",
                "requirements": {"fast_answers": 5, "max_time_per_question": 30},
                "points": 300
            },
            "study_streak_7": {
                "name": "7-Day Study Streak",
                "description": "Study for 7 consecutive days",
                "icon": "🔥",
                "requirements": {"consecutive_days": 7},
                "points": 700
            },
            "study_streak_30": {
                "name": "30-Day Study Streak",
                "description": "Study for 30 consecutive days",
                "icon": "🌟",
                "requirements": {"consecutive_days": 30},
                "points": 3000
            },
            "topic_expert": {
                "name": "Topic Expert",
                "description": "Achieve 90%+ mastery in any topic",
                "icon": "🎓",
                "requirements": {"topic_mastery": 0.9},
                "points": 1000
            },
            "helpful_learner": {
                "name": "Helpful Learner",
                "description": "Ask 20 thoughtful questions to the AI tutor",
                "icon": "💡",
                "requirements": {"questions_asked": 20},
                "points": 400
            },
            "game_champion": {
                "name": "Game Champion",
                "description": "Achieve top score in any educational game",
                "icon": "🎮",
                "requirements": {"top_game_score": True},
                "points": 600
            },
            "consistent_learner": {
                "name": "Consistent Learner",
                "description": "Complete at least one learning activity for 14 days",
                "icon": "📚",
                "requirements": {"active_days": 14},
                "points": 800
            }
        }
    
    def _load_point_system(self) -> Dict[str, int]:
        """Define point values for different activities"""
        return {
            "correct_answer": 10,
            "quiz_completion": 50,
            "perfect_quiz": 100,  # 100% score
            "daily_login": 5,
            "chat_interaction": 2,
            "game_completion": 25,
            "game_high_score": 50,
            "lesson_completion": 30,
            "streak_bonus": 20,  # per day in streak
            "improvement_bonus": 15,  # when score improves
            "help_seeking": 5  # asking for help/resources
        }
    
    def handle_wrong_answer(self, topic: str, difficulty: int, question: str, 
                          user_answer: str, correct_answer: str, 
                          user_level: str = "basic") -> Dict[str, Any]:
        """
        Provide personalized help when student gives wrong answer
        """
        response = {
            "explanation": "",
            "examples": [],
            "resources": [],
            "encouragement": "",
            "next_steps": []
        }
        
        # Get topic-specific explanation
        topic_key = topic.lower().replace(" ", "_")
        if topic_key in self.concept_explanations:
            concept_data = self.concept_explanations[topic_key].get(user_level, 
                          self.concept_explanations[topic_key].get("basic", {}))
            
            response["explanation"] = concept_data.get("explanation", 
                "Let me explain this concept in a different way...")
            response["examples"] = concept_data.get("examples", [])
            response["resources"] = concept_data.get("resources", [])
        
        # Add encouraging message
        encouragements = [
            "Don't worry! Learning is all about making mistakes and improving. 🌟",
            "Great attempt! Let's break this down step by step. 💪",
            "No problem! Even experts got things wrong when they were learning. 🚀",
            "That's okay! Every mistake is a step closer to understanding. ✨",
            "Good try! Let's explore this concept together. 🎯"
        ]
        
        import random
        response["encouragement"] = random.choice(encouragements)
        
        # Suggest next steps based on difficulty
        if difficulty == 1:  # Beginner
            response["next_steps"] = [
                "Try the interactive examples above",
                "Watch the beginner video tutorial",
                "Practice with similar easier questions",
                "Ask me to explain any part you don't understand"
            ]
        elif difficulty == 2:  # Intermediate
            response["next_steps"] = [
                "Review the fundamental concepts first",
                "Work through the provided examples",
                "Try breaking the problem into smaller parts",
                "Practice with related questions"
            ]
        else:  # Advanced
            response["next_steps"] = [
                "Review the underlying theory",
                "Analyze the examples step by step",
                "Consider alternative approaches",
                "Connect this to related advanced concepts"
            ]
        
        return response
    
    def calculate_points(self, activity: str, performance_data: Dict[str, Any]) -> int:
        """Calculate points earned for an activity"""
        base_points = self.point_system.get(activity, 0)
        bonus_points = 0
        
        if activity == "correct_answer":
            # Bonus for difficulty
            difficulty = performance_data.get("difficulty", 1)
            bonus_points += difficulty * 5
            
            # Bonus for speed (if answered quickly)
            time_taken = performance_data.get("time_taken", 60)
            if time_taken < 10:
                bonus_points += 15  # Very fast
            elif time_taken < 30:
                bonus_points += 5   # Fast
        
        elif activity == "quiz_completion":
            score = performance_data.get("score", 0)
            if score >= 0.9:  # 90%+
                bonus_points += 50
            elif score >= 0.8:  # 80%+
                bonus_points += 25
            elif score >= 0.7:  # 70%+
                bonus_points += 10
        
        elif activity == "streak_bonus":
            streak_days = performance_data.get("streak_days", 1)
            bonus_points = streak_days * self.point_system["streak_bonus"]
        
        return base_points + bonus_points
    
    def check_badge_eligibility(self, user_stats: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check which badges the user has earned"""
        earned_badges = []
        
        for badge_id, badge_info in self.badge_definitions.items():
            requirements = badge_info["requirements"]
            earned = True
            
            # Check each requirement
            for req_key, req_value in requirements.items():
                user_value = user_stats.get(req_key, 0)
                
                if req_key in ["min_average_score", "topic_mastery"]:
                    if user_value < req_value:
                        earned = False
                        break
                elif req_key == "top_game_score":
                    if not user_stats.get("has_top_score", False):
                        earned = False
                        break
                else:
                    if user_value < req_value:
                        earned = False
                        break
            
            if earned and badge_id not in user_stats.get("earned_badges", []):
                earned_badges.append({
                    "id": badge_id,
                    "name": badge_info["name"],
                    "description": badge_info["description"],
                    "icon": badge_info["icon"],
                    "points": badge_info["points"]
                })
        
        return earned_badges
    
    def generate_progress_insights(self, user_progress: Dict[str, Any]) -> Dict[str, Any]:
        """Generate insights about user's learning progress"""
        insights = {
            "strengths": [],
            "areas_for_improvement": [],
            "recommendations": [],
            "next_goals": [],
            "motivation_message": ""
        }
        
        # Analyze strengths (topics with high mastery)
        topic_progress = user_progress.get("topics", {})
        for topic, data in topic_progress.items():
            mastery = data.get("mastery_level", 0)
            if mastery >= 80:
                insights["strengths"].append({
                    "topic": topic,
                    "mastery": mastery,
                    "message": f"Excellent understanding of {topic}!"
                })
            elif mastery < 50:
                insights["areas_for_improvement"].append({
                    "topic": topic,
                    "mastery": mastery,
                    "message": f"Focus more on {topic} fundamentals"
                })
        
        # Generate recommendations
        avg_score = user_progress.get("average_score", 0)
        if avg_score < 0.6:
            insights["recommendations"].extend([
                "Try starting with easier difficulty levels",
                "Spend more time on concept explanations",
                "Use the interactive examples and resources",
                "Don't hesitate to ask questions when confused"
            ])
        elif avg_score < 0.8:
            insights["recommendations"].extend([
                "Challenge yourself with harder questions",
                "Focus on your weaker topics",
                "Try explaining concepts in your own words",
                "Practice regularly to maintain progress"
            ])
        else:
            insights["recommendations"].extend([
                "Explore advanced topics in your strong areas",
                "Help others by explaining concepts",
                "Try real-world applications of your knowledge",
                "Consider teaching or mentoring others"
            ])
        
        # Set next goals
        total_points = user_progress.get("total_points", 0)
        if total_points < 500:
            insights["next_goals"].append("Reach 500 points milestone")
        elif total_points < 1000:
            insights["next_goals"].append("Achieve 1000 points milestone")
        
        streak = user_progress.get("study_streak", 0)
        if streak < 7:
            insights["next_goals"].append("Build a 7-day study streak")
        elif streak < 30:
            insights["next_goals"].append("Reach 30-day study streak")
        
        # Motivation message
        motivation_messages = [
            "You're making great progress! Keep up the excellent work! 🌟",
            "Every step forward is progress. You're doing amazing! 🚀",
            "Your dedication to learning is inspiring! 💪",
            "Knowledge is power, and you're building yours every day! 🎓",
            "The journey of learning never ends, and you're on the right path! ✨"
        ]
        
        import random
        insights["motivation_message"] = random.choice(motivation_messages)
        
        return insights
    
    def get_personalized_study_plan(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a personalized study plan based on user's progress"""
        plan = {
            "daily_goals": [],
            "weekly_focus": "",
            "recommended_activities": [],
            "difficulty_adjustment": "",
            "estimated_time": ""
        }
        
        # Analyze user's current level
        avg_score = user_data.get("average_score", 0)
        weak_topics = user_data.get("weak_topics", [])
        strong_topics = user_data.get("strong_topics", [])
        preferred_difficulty = user_data.get("preferred_difficulty", 1)
        
        # Set daily goals
        plan["daily_goals"] = [
            "Complete at least one quiz or learning session",
            "Spend 15-30 minutes on focused study",
            "Review one concept you found challenging"
        ]
        
        if weak_topics:
            plan["daily_goals"].append(f"Practice {weak_topics[0]} for 10 minutes")
        
        # Weekly focus
        if weak_topics:
            plan["weekly_focus"] = f"Strengthen understanding of {weak_topics[0]}"
        elif strong_topics:
            plan["weekly_focus"] = f"Advance to higher levels in {strong_topics[0]}"
        else:
            plan["weekly_focus"] = "Explore new topics and build foundational knowledge"
        
        # Recommended activities
        if avg_score < 0.6:
            plan["recommended_activities"] = [
                "Start with beginner-level quizzes",
                "Use interactive examples and tutorials",
                "Ask questions when concepts are unclear",
                "Focus on understanding rather than speed"
            ]
            plan["difficulty_adjustment"] = "Stay at beginner level until comfortable"
            plan["estimated_time"] = "20-30 minutes daily"
        
        elif avg_score < 0.8:
            plan["recommended_activities"] = [
                "Mix of beginner and intermediate content",
                "Challenge yourself with harder questions",
                "Review and reinforce weak areas",
                "Try educational games for variety"
            ]
            plan["difficulty_adjustment"] = "Gradually increase to intermediate level"
            plan["estimated_time"] = "30-45 minutes daily"
        
        else:
            plan["recommended_activities"] = [
                "Focus on advanced topics",
                "Explore real-world applications",
                "Help others by explaining concepts",
                "Take on challenging projects"
            ]
            plan["difficulty_adjustment"] = "Challenge yourself with advanced content"
            plan["estimated_time"] = "45-60 minutes daily"
        
        return plan

# Global instance
personalized_learning = PersonalizedLearningService()