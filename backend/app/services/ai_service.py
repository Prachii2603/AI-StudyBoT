import os
from typing import List, Dict, Any
from app.models import QuizQuestion
import uuid
from dotenv import load_dotenv
import openai
from groq import Groq
import json
import requests
from bs4 import BeautifulSoup
import wikipediaapi
from duckduckgo_search import DDGS
import re
from datetime import datetime

# Load environment variables
load_dotenv()

class EnhancedAIService:
    def __init__(self):
        self.ai_provider = os.getenv("AI_PROVIDER", "groq").lower()
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.groq_api_key = os.getenv("GROQ_API_KEY", "")
        self.conversation_history = {}
        self.student_profiles = {}
        self.quiz_answers = {}
        
        # Initialize Wikipedia API
        self.wiki = wikipediaapi.Wikipedia(
            language='en',
            extract_format=wikipediaapi.ExtractFormat.WIKI,
            user_agent='AI-Learning-Chatbot/1.0'
        )
        
        # Initialize AI clients
        if self.ai_provider == "openai" and self.openai_api_key:
            self.openai_client = openai.OpenAI(api_key=self.openai_api_key)
        elif self.ai_provider == "groq" and self.groq_api_key:
            self.groq_client = Groq(api_key=self.groq_api_key)
    
    def get_student_profile(self, student_id: str) -> Dict[str, Any]:
        """Get or create student learning profile"""
        if student_id not in self.student_profiles:
            self.student_profiles[student_id] = {
                'learning_style': 'visual',  # visual, auditory, kinesthetic
                'knowledge_areas': {},  # topic -> proficiency_level (0-100)
                'difficulty_preferences': {},  # topic -> preferred_difficulty (1-3)
                'interaction_history': [],
                'strengths': [],
                'areas_for_improvement': [],
                'last_assessment': None
            }
        return self.student_profiles[student_id]
    
    def update_student_progress(self, student_id: str, topic: str, performance: float, difficulty: int):
        """Update student's learning progress based on performance"""
        profile = self.get_student_profile(student_id)
        
        # Update knowledge area proficiency
        if topic not in profile['knowledge_areas']:
            profile['knowledge_areas'][topic] = 50  # Start at medium proficiency
        
        # Adjust proficiency based on performance
        current_proficiency = profile['knowledge_areas'][topic]
        if performance > 0.8:  # Excellent performance
            profile['knowledge_areas'][topic] = min(100, current_proficiency + 10)
        elif performance > 0.6:  # Good performance
            profile['knowledge_areas'][topic] = min(100, current_proficiency + 5)
        elif performance < 0.4:  # Poor performance
            profile['knowledge_areas'][topic] = max(0, current_proficiency - 5)
        
        # Update difficulty preferences
        if performance > 0.8 and difficulty < 3:
            profile['difficulty_preferences'][topic] = difficulty + 1
        elif performance < 0.4 and difficulty > 1:
            profile['difficulty_preferences'][topic] = difficulty - 1
        else:
            profile['difficulty_preferences'][topic] = difficulty
    
    async def search_web_content(self, query: str, max_results: int = 3) -> List[Dict[str, str]]:
        """Search for current information using DuckDuckGo"""
        try:
            with DDGS() as ddgs:
                results = []
                for result in ddgs.text(query, max_results=max_results):
                    results.append({
                        'title': result.get('title', ''),
                        'snippet': result.get('body', ''),
                        'url': result.get('href', '')
                    })
                return results
        except Exception as e:
            print(f"Web search error: {e}")
            return []
    
    async def get_wikipedia_content(self, topic: str) -> str:
        """Get Wikipedia content for a topic"""
        try:
            page = self.wiki.page(topic)
            if page.exists():
                # Get first few paragraphs
                summary = page.summary[:1000] if len(page.summary) > 1000 else page.summary
                return summary
            return ""
        except Exception as e:
            print(f"Wikipedia error: {e}")
            return ""
    
    async def generate_response(self, message: str, student_id: str, difficulty: int):
        profile = self.get_student_profile(student_id)
        
        if student_id not in self.conversation_history:
            self.conversation_history[student_id] = []
        
        self.conversation_history[student_id].append({"role": "user", "content": message})
        
        # Analyze if the question needs current information
        needs_search = self._needs_web_search(message)
        
        # Gather relevant information
        context_info = ""
        if needs_search:
            # Search for current information
            search_results = await self.search_web_content(message)
            if search_results:
                context_info += "\\n\\nCurrent information from web sources:\\n"
                for result in search_results:
                    context_info += f"- {result['title']}: {result['snippet'][:200]}...\\n"
        
        # Get Wikipedia information for educational topics
        wiki_content = await self.get_wikipedia_content(message)
        if wiki_content:
            context_info += f"\\n\\nEducational background:\\n{wiki_content}\\n"
        
        # Create enhanced system prompt
        system_prompt = self._create_adaptive_prompt(profile, difficulty, context_info)
        
        try:
            if self.ai_provider == "openai" and hasattr(self, 'openai_client'):
                response = await self._get_openai_response(system_prompt, self.conversation_history[student_id])
            elif self.ai_provider == "groq" and hasattr(self, 'groq_client'):
                response = await self._get_groq_response(system_prompt, self.conversation_history[student_id])
            else:
                response = f"I understand you're asking about: {message}. Let me help you learn this concept at difficulty level {difficulty}. (Note: AI provider not configured)"
        except Exception as e:
            response = f"I'm here to help you learn! However, I'm having trouble connecting to my AI service right now. Could you try rephrasing your question? (Error: {str(e)})"
        
        self.conversation_history[student_id].append({"role": "assistant", "content": response})
        
        # Update student interaction history
        profile['interaction_history'].append({
            'timestamp': datetime.now().isoformat(),
            'question': message,
            'response': response,
            'difficulty': difficulty
        })
        
        return response
    
    def _needs_web_search(self, message: str) -> bool:
        """Determine if a question needs current web information"""
        current_keywords = ['latest', 'recent', 'current', 'today', 'now', 'new', '2024', '2025', '2026']
        news_keywords = ['news', 'update', 'development', 'breakthrough', 'discovery']
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in current_keywords + news_keywords)
    
    def _create_adaptive_prompt(self, profile: Dict[str, Any], difficulty: int, context_info: str) -> str:
        """Create an adaptive system prompt based on student profile"""
        
        difficulty_prompts = {
            1: "You are a patient, encouraging AI tutor for beginners. Use simple language, provide step-by-step explanations, and include lots of examples. Always be supportive and positive.",
            2: "You are an AI tutor for intermediate learners. Provide detailed explanations with practical examples, introduce some technical terms, and encourage critical thinking.",
            3: "You are an AI tutor for advanced learners. Give comprehensive explanations with complex examples, technical details, challenging questions, and encourage deep analysis."
        }
        
        base_prompt = difficulty_prompts.get(difficulty, difficulty_prompts[1])
        
        # Add learning style adaptation
        learning_style = profile.get('learning_style', 'visual')
        if learning_style == 'visual':
            base_prompt += " Use visual descriptions, analogies, and suggest diagrams or charts when helpful."
        elif learning_style == 'auditory':
            base_prompt += " Use verbal explanations, suggest listening to related content, and use sound-based analogies."
        elif learning_style == 'kinesthetic':
            base_prompt += " Suggest hands-on activities, practical exercises, and real-world applications."
        
        # Add knowledge areas context
        knowledge_areas = profile.get('knowledge_areas', {})
        if knowledge_areas:
            strong_areas = [topic for topic, level in knowledge_areas.items() if level > 70]
            weak_areas = [topic for topic, level in knowledge_areas.items() if level < 40]
            
            if strong_areas:
                base_prompt += f" The student is strong in: {', '.join(strong_areas)}. You can reference these areas when explaining new concepts."
            if weak_areas:
                base_prompt += f" The student needs more support in: {', '.join(weak_areas)}. Provide extra explanations for these topics."
        
        # Add context information
        if context_info:
            base_prompt += f"\\n\\nUse this current information to enhance your response: {context_info}"
        
        base_prompt += "\\n\\nAlways end your response with a follow-up question to encourage continued learning and engagement."
        
        return base_prompt
    
    async def _get_openai_response(self, system_prompt: str, conversation: List[dict]):
        messages = [{"role": "system", "content": system_prompt}] + conversation[-10:]  # Keep last 10 messages
        
        response = self.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=500,
            temperature=0.7
        )
        return response.choices[0].message.content
    
    async def _get_groq_response(self, system_prompt: str, conversation: List[dict]):
        messages = [{"role": "system", "content": system_prompt}] + conversation[-10:]  # Keep last 10 messages
        
        response = self.groq_client.chat.completions.create(
            model="llama3-8b-8192",  # You can change this to other Groq models
            messages=messages,
            max_tokens=500,
            temperature=0.7
        )
        return response.choices[0].message.content
    
    async def generate_quiz(self, topic: str, difficulty: int, count: int) -> List[QuizQuestion]:
        try:
            if self.ai_provider == "openai" and hasattr(self, 'openai_client'):
                quiz_data = await self._generate_quiz_openai(topic, difficulty, count)
            elif self.ai_provider == "groq" and hasattr(self, 'groq_client'):
                quiz_data = await self._generate_quiz_groq(topic, difficulty, count)
            else:
                return self._generate_mock_quiz(topic, difficulty, count)
            
            return self._parse_quiz_response(quiz_data, difficulty)
        except Exception as e:
            print(f"Error generating quiz: {e}")
            return self._generate_mock_quiz(topic, difficulty, count)
    
    async def _generate_quiz_openai(self, topic: str, difficulty: int, count: int):
        difficulty_levels = {1: "beginner", 2: "intermediate", 3: "advanced"}
        prompt = f"""Generate {count} multiple choice questions about {topic} for {difficulty_levels[difficulty]} level students.

Format your response as a JSON array with this exact structure:
[
  {{
    "question": "Question text here?",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct_answer": 0
  }}
]

Make sure questions are educational and appropriate for the difficulty level."""

        response = self.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
            temperature=0.7
        )
        return response.choices[0].message.content
    
    async def _generate_quiz_groq(self, topic: str, difficulty: int, count: int):
        difficulty_levels = {1: "beginner", 2: "intermediate", 3: "advanced"}
        prompt = f"""Generate {count} multiple choice questions about {topic} for {difficulty_levels[difficulty]} level students.

Format your response as a JSON array with this exact structure:
[
  {{
    "question": "Question text here?",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct_answer": 0
  }}
]

Make sure questions are educational and appropriate for the difficulty level."""

        response = self.groq_client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
            temperature=0.7
        )
        return response.choices[0].message.content
    
    def _parse_quiz_response(self, response_text: str, difficulty: int) -> List[QuizQuestion]:
        try:
            # Extract JSON from response if it's wrapped in markdown
            if "```json" in response_text:
                start = response_text.find("```json") + 7
                end = response_text.find("```", start)
                response_text = response_text[start:end].strip()
            elif "```" in response_text:
                start = response_text.find("```") + 3
                end = response_text.find("```", start)
                response_text = response_text[start:end].strip()
            
            quiz_data = json.loads(response_text)
            questions = []
            
            for item in quiz_data:
                questions.append(QuizQuestion(
                    id=str(uuid.uuid4()),
                    question=item["question"],
                    options=item["options"],
                    correct_answer=item["correct_answer"],
                    difficulty=difficulty
                ))
            
            return questions
        except Exception as e:
            print(f"Error parsing quiz response: {e}")
            return self._generate_mock_quiz("General Knowledge", difficulty, len(quiz_data) if 'quiz_data' in locals() else 3)
    
    def _generate_mock_quiz(self, topic: str, difficulty: int, count: int) -> List[QuizQuestion]:
        # Fallback mock quiz generation
        questions = []
        for i in range(count):
            questions.append(QuizQuestion(
                id=str(uuid.uuid4()),
                question=f"Question {i+1} about {topic} (Difficulty {difficulty})?",
                options=["Option A", "Option B", "Option C", "Option D"],
                correct_answer=0,
                difficulty=difficulty
            ))
        return questions
    
    async def check_answer(self, question_id: str, answer: int) -> bool:
        # In a real implementation, you'd store questions and their correct answers
        # For now, we'll use a simple storage mechanism
        if not hasattr(self, 'quiz_answers'):
            self.quiz_answers = {}
        
        # This is a simplified version - in production, you'd store this in a database
        return self.quiz_answers.get(question_id, 0) == answer
    
    def store_quiz_answers(self, questions: List[QuizQuestion]):
        """Store correct answers for later verification"""
        if not hasattr(self, 'quiz_answers'):
            self.quiz_answers = {}
        
        for question in questions:
            self.quiz_answers[question.id] = question.correct_answer
    async def _get_openai_response(self, system_prompt: str, conversation: List[dict]):
        messages = [{"role": "system", "content": system_prompt}] + conversation[-10:]  # Keep last 10 messages
        
        response = self.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=800,
            temperature=0.7
        )
        return response.choices[0].message.content
    
    async def _get_groq_response(self, system_prompt: str, conversation: List[dict]):
        messages = [{"role": "system", "content": system_prompt}] + conversation[-10:]  # Keep last 10 messages
        
        response = self.groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",  # Updated to current Groq model
            messages=messages,
            max_tokens=800,
            temperature=0.7
        )
        return response.choices[0].message.content
    
    async def generate_quiz(self, topic: str, difficulty: int, count: int, student_id: str = None) -> List[QuizQuestion]:
        """Generate adaptive quiz based on student profile"""
        try:
            # Get student profile for adaptive quiz generation
            profile = self.get_student_profile(student_id) if student_id else {}
            
            # Get current information about the topic
            context_info = ""
            search_results = await self.search_web_content(f"{topic} facts information")
            if search_results:
                context_info = "Current information: " + " ".join([r['snippet'][:100] for r in search_results[:2]])
            
            wiki_content = await self.get_wikipedia_content(topic)
            if wiki_content:
                context_info += f" Educational background: {wiki_content[:300]}"
            
            if self.ai_provider == "openai" and hasattr(self, 'openai_client'):
                quiz_data = await self._generate_quiz_openai(topic, difficulty, count, context_info, profile)
            elif self.ai_provider == "groq" and hasattr(self, 'groq_client'):
                quiz_data = await self._generate_quiz_groq(topic, difficulty, count, context_info, profile)
            else:
                return self._generate_mock_quiz(topic, difficulty, count)
            
            questions = self._parse_quiz_response(quiz_data, difficulty)
            
            # Store answers for verification
            self.store_quiz_answers(questions)
            
            return questions
        except Exception as e:
            print(f"Error generating quiz: {e}")
            return self._generate_mock_quiz(topic, difficulty, count)
    
    async def _generate_quiz_openai(self, topic: str, difficulty: int, count: int, context_info: str, profile: Dict):
        difficulty_levels = {1: "beginner", 2: "intermediate", 3: "advanced"}
        
        # Adaptive prompt based on student profile
        adaptive_note = ""
        if profile.get('knowledge_areas'):
            strong_areas = [area for area, level in profile['knowledge_areas'].items() if level > 70]
            if strong_areas:
                adaptive_note = f" The student is strong in {', '.join(strong_areas)}, so you can include some cross-references to these areas."
        
        prompt = f"""Generate {count} multiple choice questions about {topic} for {difficulty_levels[difficulty]} level students.{adaptive_note}

Use this information to create accurate, current questions: {context_info}

Requirements:
1. Questions should be educational and test understanding, not just memorization
2. Include a mix of factual, conceptual, and application questions
3. Make incorrect options plausible but clearly wrong
4. Ensure questions are current and accurate

Format your response as a JSON array with this exact structure:
[
  {{
    "question": "Question text here?",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct_answer": 0,
    "explanation": "Brief explanation of why this answer is correct"
  }}
]"""

        response = self.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500,
            temperature=0.7
        )
        return response.choices[0].message.content
    
    async def _generate_quiz_groq(self, topic: str, difficulty: int, count: int, context_info: str, profile: Dict):
        difficulty_levels = {1: "beginner", 2: "intermediate", 3: "advanced"}
        
        # Adaptive prompt based on student profile
        adaptive_note = ""
        if profile.get('knowledge_areas'):
            strong_areas = [area for area, level in profile['knowledge_areas'].items() if level > 70]
            if strong_areas:
                adaptive_note = f" The student is strong in {', '.join(strong_areas)}, so you can include some cross-references to these areas."
        
        prompt = f"""Generate {count} multiple choice questions about {topic} for {difficulty_levels[difficulty]} level students.{adaptive_note}

Use this information to create accurate, current questions: {context_info}

Requirements:
1. Questions should be educational and test understanding, not just memorization
2. Include a mix of factual, conceptual, and application questions
3. Make incorrect options plausible but clearly wrong
4. Ensure questions are current and accurate

Format your response as a JSON array with this exact structure:
[
  {{
    "question": "Question text here?",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct_answer": 0,
    "explanation": "Brief explanation of why this answer is correct"
  }}
]"""

        response = self.groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500,
            temperature=0.7
        )
        return response.choices[0].message.content
    
    def _parse_quiz_response(self, response_text: str, difficulty: int) -> List[QuizQuestion]:
        try:
            # Extract JSON from response if it's wrapped in markdown
            if "```json" in response_text:
                start = response_text.find("```json") + 7
                end = response_text.find("```", start)
                response_text = response_text[start:end].strip()
            elif "```" in response_text:
                start = response_text.find("```") + 3
                end = response_text.find("```", start)
                response_text = response_text[start:end].strip()
            
            quiz_data = json.loads(response_text)
            questions = []
            
            for item in quiz_data:
                questions.append(QuizQuestion(
                    id=str(uuid.uuid4()),
                    question=item["question"],
                    options=item["options"],
                    correct_answer=item["correct_answer"],
                    difficulty=difficulty
                ))
            
            return questions
        except Exception as e:
            print(f"Error parsing quiz response: {e}")
            return self._generate_mock_quiz("General Knowledge", difficulty, 3)
    
    def _generate_mock_quiz(self, topic: str, difficulty: int, count: int) -> List[QuizQuestion]:
        """Enhanced fallback quiz generation"""
        questions = []
        difficulty_labels = {1: "Basic", 2: "Intermediate", 3: "Advanced"}
        
        sample_questions = {
            "neural networks": [
                {
                    "question": f"What is the basic building block of a neural network?",
                    "options": ["Neuron/Node", "Layer", "Weight", "Bias"],
                    "correct": 0
                },
                {
                    "question": f"What is backpropagation used for in neural networks?",
                    "options": ["Data preprocessing", "Training the network", "Making predictions", "Visualizing results"],
                    "correct": 1
                }
            ],
            "default": [
                {
                    "question": f"{difficulty_labels[difficulty]} question about {topic}: What is a key concept?",
                    "options": ["Concept A", "Concept B", "Concept C", "Concept D"],
                    "correct": 0
                }
            ]
        }
        
        topic_questions = sample_questions.get(topic.lower(), sample_questions["default"])
        
        for i in range(min(count, len(topic_questions))):
            q = topic_questions[i] if i < len(topic_questions) else topic_questions[0]
            questions.append(QuizQuestion(
                id=str(uuid.uuid4()),
                question=q["question"],
                options=q["options"],
                correct_answer=q["correct"],
                difficulty=difficulty
            ))
        
        return questions
    
    async def check_answer(self, question_id: str, answer: int, student_id: str = None) -> Dict[str, Any]:
        """Enhanced answer checking with performance tracking"""
        is_correct = self.quiz_answers.get(question_id, 0) == answer
        
        result = {
            "correct": is_correct,
            "explanation": "Good job!" if is_correct else "Not quite right. Keep learning!",
            "performance_update": None
        }
        
        # Update student performance if student_id provided
        if student_id:
            # This would typically involve more sophisticated tracking
            # For now, we'll do basic performance updates
            result["performance_update"] = {
                "points_earned": 10 if is_correct else 2,
                "streak_updated": True
            }
        
        return result
    
    def store_quiz_answers(self, questions: List[QuizQuestion]):
        """Store correct answers for later verification"""
        for question in questions:
            self.quiz_answers[question.id] = question.correct_answer
    
    async def get_learning_recommendations(self, student_id: str) -> Dict[str, Any]:
        """Generate personalized learning recommendations"""
        profile = self.get_student_profile(student_id)
        
        recommendations = {
            "next_topics": [],
            "difficulty_adjustments": {},
            "study_methods": [],
            "strengths": [],
            "areas_for_improvement": []
        }
        
        # Analyze knowledge areas
        knowledge_areas = profile.get('knowledge_areas', {})
        if knowledge_areas:
            # Find strong and weak areas
            strong_areas = [(topic, level) for topic, level in knowledge_areas.items() if level > 70]
            weak_areas = [(topic, level) for topic, level in knowledge_areas.items() if level < 40]
            
            recommendations["strengths"] = [topic for topic, _ in strong_areas]
            recommendations["areas_for_improvement"] = [topic for topic, _ in weak_areas]
            
            # Suggest next topics based on strong areas
            if strong_areas:
                recommendations["next_topics"] = [f"Advanced {topic}" for topic, _ in strong_areas[:3]]
        
        # Learning style recommendations
        learning_style = profile.get('learning_style', 'visual')
        style_methods = {
            'visual': ['Use diagrams and charts', 'Watch educational videos', 'Create mind maps'],
            'auditory': ['Listen to podcasts', 'Discuss topics with others', 'Use text-to-speech'],
            'kinesthetic': ['Try hands-on experiments', 'Build projects', 'Use interactive simulations']
        }
        recommendations["study_methods"] = style_methods.get(learning_style, style_methods['visual'])
        
        return recommendations

# Create a global instance
ai_service = EnhancedAIService()