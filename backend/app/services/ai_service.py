import os
from typing import List, Dict, Any, Optional
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
from pyunsplash import PyUnsplash
from app.services.knowledge_tracing import knowledge_tracer
from app.services.adaptive_engine import adaptive_engine
from app.services.personalized_learning import personalized_learning
from app.models.student import StudentKnowledgeProfile, LearningSession

# Load environment variables
load_dotenv()

class EnhancedAIService:
    def __init__(self):
        self.ai_provider = os.getenv("AI_PROVIDER", "groq").lower()
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.groq_api_key = os.getenv("GROQ_API_KEY", "")
        self.unsplash_access_key = os.getenv("UNSPLASH_ACCESS_KEY", "")
        self.conversation_history = {}
        self.student_profiles = {}
        self.quiz_answers = {}
        self.quiz_explanations = {}
        
        # Initialize Wikipedia API
        self.wiki = wikipediaapi.Wikipedia(
            language='en',
            extract_format=wikipediaapi.ExtractFormat.WIKI,
            user_agent='AI-Learning-Chatbot/1.0'
        )
        
        # Initialize Unsplash for images
        if self.unsplash_access_key:
            self.unsplash = PyUnsplash(api_key=self.unsplash_access_key)
        
        # Initialize AI clients
        if self.ai_provider == "openai" and self.openai_api_key:
            self.openai_client = openai.OpenAI(api_key=self.openai_api_key)
        elif self.ai_provider == "groq" and self.groq_api_key:
            self.groq_client = Groq(api_key=self.groq_api_key)
    
    async def get_educational_images(self, topic: str, count: int = 3) -> List[Dict[str, str]]:
        """Get educational images related to the topic"""
        images = []
        try:
            if hasattr(self, 'unsplash'):
                # Search for educational images
                search = self.unsplash.search(type_='photos', query=f"{topic} education learning", per_page=count)
                for photo in search.entries:
                    images.append({
                        'url': photo.urls.regular,
                        'description': photo.description or f"Educational image about {topic}",
                        'alt_text': photo.alt_description or topic,
                        'credit': f"Photo by {photo.user.name} on Unsplash"
                    })
            else:
                # Fallback to placeholder images
                for i in range(count):
                    images.append({
                        'url': f"https://via.placeholder.com/400x300/4F46E5/FFFFFF?text={topic.replace(' ', '+')}+{i+1}",
                        'description': f"Educational illustration about {topic}",
                        'alt_text': f"{topic} educational content",
                        'credit': "Placeholder image"
                    })
        except Exception as e:
            print(f"Error fetching images: {e}")
            # Fallback images
            images = [{
                'url': f"https://via.placeholder.com/400x300/4F46E5/FFFFFF?text={topic.replace(' ', '+')}",
                'description': f"Educational content about {topic}",
                'alt_text': topic,
                'credit': "Educational placeholder"
            }]
        
        return images
    
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
        # Get or initialize student knowledge profile
        try:
            # Try to get existing knowledge profile from knowledge tracer
            skp = knowledge_tracer.get_student_progress(student_id)
        except:
            # Initialize if doesn't exist
            topics = self._extract_topics_from_message(message)
            skp = knowledge_tracer.initialize_student_knowledge(student_id, topics)
        
        # Get basic student profile for conversation history
        profile = self.get_student_profile(student_id)
        
        if student_id not in self.conversation_history:
            self.conversation_history[student_id] = []
        
        self.conversation_history[student_id].append({"role": "user", "content": message})
        
        # Extract topic from message for adaptive learning
        topic = self._extract_main_topic(message)
        
        # Adapt difficulty based on student's learning pace and mastery
        adapted_difficulty = self._adapt_difficulty_for_pace(skp, topic, difficulty)
        
        # Get learning pace recommendations
        pace_recommendations = self._get_pace_recommendations(skp, topic)
        
        # Analyze if the question needs current information
        needs_search = self._needs_web_search(message)
        needs_images = self._needs_visual_content(message)
        
        # Gather relevant information
        context_info = ""
        images = []
        
        if needs_search:
            # Search for current information
            search_results = await self.search_web_content(message)
            if search_results:
                context_info += "\n\nCurrent information from web sources:\n"
                for result in search_results:
                    context_info += f"- {result['title']}: {result['snippet'][:200]}...\n"
        
        # Get Wikipedia information for educational topics
        wiki_content = await self.get_wikipedia_content(message)
        if wiki_content:
            context_info += f"\n\nEducational background:\n{wiki_content}\n"
        
        # Get educational images if needed
        if needs_images:
            topic_keywords = self._extract_topic_keywords(message)
            if topic_keywords:
                images = await self.get_educational_images(topic_keywords, 2)
        
        # Create adaptive system prompt with pace information
        system_prompt = self._create_pace_adaptive_prompt(
            profile, skp, adapted_difficulty, context_info, pace_recommendations
        )
        
        try:
            if self.ai_provider == "openai" and hasattr(self, 'openai_client'):
                response = await self._get_openai_response(system_prompt, self.conversation_history[student_id])
            elif self.ai_provider == "groq" and hasattr(self, 'groq_client'):
                response = await self._get_groq_response(system_prompt, self.conversation_history[student_id])
            else:
                response = f"I understand you're asking about: {message}. Let me help you learn this concept at your optimal pace. (Note: AI provider not configured)"
        except Exception as e:
            response = f"I'm here to help you learn! However, I'm having trouble connecting to my AI service right now. Could you try rephrasing your question? (Error: {str(e)})"
        
        self.conversation_history[student_id].append({"role": "assistant", "content": response})
        
        # Track this interaction for learning pace analysis
        self._track_learning_interaction(student_id, topic, message, response, adapted_difficulty)
        
        # Update student interaction history
        profile['interaction_history'].append({
            'timestamp': datetime.now().isoformat(),
            'question': message,
            'response': response,
            'original_difficulty': difficulty,
            'adapted_difficulty': adapted_difficulty,
            'topic': topic,
            'images_provided': len(images) > 0,
            'pace_adapted': adapted_difficulty != difficulty
        })
        
        # Return response with adaptive learning information
        learning_resources = await self._get_learning_resources(message)
        
        return {
            "content": response,
            "images": images,
            "learning_resources": learning_resources,
            "timestamp": datetime.now().isoformat(),
            "adaptive_info": {
                "original_difficulty": difficulty,
                "adapted_difficulty": adapted_difficulty,
                "learning_pace": pace_recommendations["pace_level"],
                "mastery_level": skp.knowledge_areas.get(topic, 10),
                "pace_explanation": pace_recommendations["explanation"]
            }
        }
    
    def _needs_visual_content(self, message: str) -> bool:
        """Determine if a question would benefit from visual content"""
        visual_keywords = [
            'diagram', 'chart', 'graph', 'image', 'picture', 'visual', 'show me',
            'structure', 'architecture', 'anatomy', 'process', 'workflow',
            'neural network', 'algorithm', 'data structure', 'molecule', 'cell',
            'system', 'model', 'design', 'layout', 'interface'
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in visual_keywords)
    
    def _extract_topic_keywords(self, message: str) -> str:
        """Extract main topic keywords for image search"""
        # Simple keyword extraction - in production, use NLP libraries
        common_words = {'what', 'is', 'are', 'how', 'does', 'do', 'can', 'will', 'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        words = message.lower().split()
        keywords = [word for word in words if word not in common_words and len(word) > 2]
        return ' '.join(keywords[:3])  # Take first 3 meaningful words
    
    async def _get_learning_resources(self, topic: str) -> List[Dict[str, str]]:
        """Get learning resource recommendations with links"""
        resources = []
        
        # Extract main topic
        topic_clean = self._extract_topic_keywords(topic)
        
        # Predefined quality learning resources
        resource_templates = [
            {
                "title": f"Khan Academy - {topic_clean.title()}",
                "url": f"https://www.khanacademy.org/search?search_again=1&page_search_query={topic_clean.replace(' ', '%20')}",
                "description": "Free, world-class education with interactive exercises and videos",
                "type": "Interactive Learning"
            },
            {
                "title": f"Coursera Courses - {topic_clean.title()}",
                "url": f"https://www.coursera.org/search?query={topic_clean.replace(' ', '%20')}",
                "description": "University-level courses from top institutions",
                "type": "Online Courses"
            },
            {
                "title": f"YouTube Educational Videos - {topic_clean.title()}",
                "url": f"https://www.youtube.com/results?search_query={topic_clean.replace(' ', '+')}+tutorial+education",
                "description": "Visual learning through educational videos",
                "type": "Video Learning"
            },
            {
                "title": f"Wikipedia - {topic_clean.title()}",
                "url": f"https://en.wikipedia.org/wiki/{topic_clean.replace(' ', '_')}",
                "description": "Comprehensive encyclopedia articles with references",
                "type": "Reference"
            }
        ]
        
        return resource_templates[:3]  # Return top 3 resources
    
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
            model="llama-3.1-8b-instant",
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
    
    async def generate_quiz(self, topic: str, difficulty: int, count: int = 10, student_id: str = None) -> List[QuizQuestion]:
        """Generate comprehensive quiz with minimum 10 questions"""
        try:
            # Ensure minimum 10 questions
            count = max(10, count)
            
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
                return self._generate_comprehensive_mock_quiz(topic, difficulty, count)
            
            questions = self._parse_quiz_response(quiz_data, difficulty)
            
            # Ensure we have at least 10 questions
            if len(questions) < 10:
                additional_questions = self._generate_comprehensive_mock_quiz(topic, difficulty, 10 - len(questions))
                questions.extend(additional_questions)
            
            # Store the correct answers and explanations for verification
            self.store_quiz_answers(questions)
            
            return questions[:count]  # Return exactly the requested number
        except Exception as e:
            print(f"Error generating quiz: {e}")
            return self._generate_comprehensive_mock_quiz(topic, difficulty, count)
    
    def _generate_comprehensive_mock_quiz(self, topic: str, difficulty: int, count: int) -> List[QuizQuestion]:
        """Generate comprehensive fallback quiz with detailed questions"""
        questions = []
        difficulty_labels = {1: "Basic", 2: "Intermediate", 3: "Advanced"}
        
        # Comprehensive topic-specific question banks
        question_banks = {
            "python": [
                {
                    "question": "Which of the following is the correct way to define a function in Python?",
                    "options": ["function myFunc():", "def myFunc():", "define myFunc():", "func myFunc():"],
                    "correct": 1,
                    "explanation": "In Python, functions are defined using the 'def' keyword followed by the function name and parentheses."
                },
                {
                    "question": "What is the output of: print(type([1, 2, 3]))?",
                    "options": ["<class 'tuple'>", "<class 'list'>", "<class 'array'>", "<class 'dict'>"],
                    "correct": 1,
                    "explanation": "The type() function returns the class type of an object. [1, 2, 3] is a list, so it returns <class 'list'>."
                },
                {
                    "question": "Which method is used to add an element to the end of a list in Python?",
                    "options": ["add()", "append()", "insert()", "push()"],
                    "correct": 1,
                    "explanation": "The append() method adds a single element to the end of a list."
                },
                {
                    "question": "What is the correct way to create a dictionary in Python?",
                    "options": ["{key: value}", "[key: value]", "(key: value)", "<key: value>"],
                    "correct": 0,
                    "explanation": "Dictionaries in Python are created using curly braces {} with key-value pairs separated by colons."
                },
                {
                    "question": "Which of the following is used for single-line comments in Python?",
                    "options": ["//", "/* */", "#", "<!-- -->"],
                    "correct": 2,
                    "explanation": "In Python, single-line comments start with the # symbol."
                },
                {
                    "question": "What does the 'len()' function return?",
                    "options": ["The last element", "The first element", "The number of elements", "The type of object"],
                    "correct": 2,
                    "explanation": "The len() function returns the number of items (length) in an object like a string, list, or dictionary."
                },
                {
                    "question": "Which operator is used for exponentiation in Python?",
                    "options": ["^", "**", "exp()", "pow()"],
                    "correct": 1,
                    "explanation": "The ** operator is used for exponentiation in Python. For example, 2**3 equals 8."
                },
                {
                    "question": "What is the correct way to import the 'math' module in Python?",
                    "options": ["include math", "import math", "using math", "require math"],
                    "correct": 1,
                    "explanation": "The 'import' keyword is used to import modules in Python."
                },
                {
                    "question": "Which of the following is a mutable data type in Python?",
                    "options": ["tuple", "string", "list", "integer"],
                    "correct": 2,
                    "explanation": "Lists are mutable in Python, meaning their contents can be changed after creation."
                },
                {
                    "question": "What is the output of: print('Hello' + 'World')?",
                    "options": ["Hello World", "HelloWorld", "Hello+World", "Error"],
                    "correct": 1,
                    "explanation": "String concatenation with + joins strings together without spaces, resulting in 'HelloWorld'."
                }
            ],
            "machine learning": [
                {
                    "question": "What is the primary goal of machine learning?",
                    "options": ["To replace human intelligence", "To enable computers to learn from data", "To create robots", "To process text only"],
                    "correct": 1,
                    "explanation": "Machine learning enables computers to learn patterns from data and make predictions or decisions without being explicitly programmed for each task."
                },
                {
                    "question": "Which type of machine learning uses labeled training data?",
                    "options": ["Unsupervised learning", "Supervised learning", "Reinforcement learning", "Deep learning"],
                    "correct": 1,
                    "explanation": "Supervised learning uses labeled training data where the correct answers are provided to train the model."
                },
                {
                    "question": "What is overfitting in machine learning?",
                    "options": ["Model performs well on training data but poorly on new data", "Model is too simple", "Model trains too slowly", "Model uses too little data"],
                    "correct": 0,
                    "explanation": "Overfitting occurs when a model learns the training data too well, including noise, making it perform poorly on new, unseen data."
                },
                {
                    "question": "Which algorithm is commonly used for classification problems?",
                    "options": ["Linear Regression", "Decision Tree", "K-means", "PCA"],
                    "correct": 1,
                    "explanation": "Decision Trees are commonly used for classification problems as they can categorize data into different classes."
                },
                {
                    "question": "What is the purpose of cross-validation?",
                    "options": ["To increase training speed", "To evaluate model performance", "To reduce data size", "To clean data"],
                    "correct": 1,
                    "explanation": "Cross-validation is used to evaluate how well a model will perform on unseen data by testing it on different subsets of the training data."
                },
                {
                    "question": "Which metric is commonly used to evaluate classification models?",
                    "options": ["Mean Squared Error", "Accuracy", "R-squared", "Mean Absolute Error"],
                    "correct": 1,
                    "explanation": "Accuracy measures the percentage of correct predictions and is a common metric for classification models."
                },
                {
                    "question": "What is feature engineering?",
                    "options": ["Building hardware", "Creating new features from existing data", "Removing data", "Training models"],
                    "correct": 1,
                    "explanation": "Feature engineering involves creating new features or modifying existing ones to improve model performance."
                },
                {
                    "question": "Which type of learning doesn't use labeled data?",
                    "options": ["Supervised learning", "Unsupervised learning", "Semi-supervised learning", "Reinforcement learning"],
                    "correct": 1,
                    "explanation": "Unsupervised learning finds patterns in data without using labeled examples or target variables."
                },
                {
                    "question": "What is a neural network inspired by?",
                    "options": ["Computer circuits", "The human brain", "Mathematical equations", "Database structures"],
                    "correct": 1,
                    "explanation": "Neural networks are inspired by the structure and function of biological neural networks in the human brain."
                },
                {
                    "question": "What is the purpose of training data in machine learning?",
                    "options": ["To test the final model", "To teach the model patterns", "To validate results", "To store information"],
                    "correct": 1,
                    "explanation": "Training data is used to teach the machine learning model to recognize patterns and make predictions."
                }
            ],
            "neural networks": [
                {
                    "question": "What is the basic building block of a neural network?",
                    "options": ["Neuron/Node", "Layer", "Weight", "Bias"],
                    "correct": 0,
                    "explanation": "A neuron (or node) is the basic computational unit of a neural network that receives inputs, processes them, and produces an output."
                },
                {
                    "question": "What is the purpose of activation functions in neural networks?",
                    "options": ["To add complexity and non-linearity", "To reduce computation", "To store data", "To connect layers"],
                    "correct": 0,
                    "explanation": "Activation functions introduce non-linearity into the network, allowing it to learn complex patterns and relationships in data."
                },
                {
                    "question": "What is backpropagation used for?",
                    "options": ["Forward pass calculation", "Training the network by updating weights", "Data preprocessing", "Model evaluation"],
                    "correct": 1,
                    "explanation": "Backpropagation is the algorithm used to train neural networks by calculating gradients and updating weights to minimize error."
                },
                {
                    "question": "Which activation function is commonly used in hidden layers?",
                    "options": ["Sigmoid", "ReLU", "Linear", "Step function"],
                    "correct": 1,
                    "explanation": "ReLU (Rectified Linear Unit) is commonly used in hidden layers because it helps with the vanishing gradient problem and is computationally efficient."
                },
                {
                    "question": "What is a perceptron?",
                    "options": ["A type of activation function", "The simplest form of neural network", "A learning algorithm", "A data structure"],
                    "correct": 1,
                    "explanation": "A perceptron is the simplest form of neural network, consisting of a single neuron that can learn linear decision boundaries."
                },
                {
                    "question": "What is the purpose of bias in neural networks?",
                    "options": ["To add flexibility to the model", "To reduce overfitting", "To speed up training", "To store weights"],
                    "correct": 0,
                    "explanation": "Bias allows the activation function to shift, providing more flexibility for the model to fit the data better."
                },
                {
                    "question": "What is a deep neural network?",
                    "options": ["A network with one hidden layer", "A network with multiple hidden layers", "A network with many neurons", "A network with complex data"],
                    "correct": 1,
                    "explanation": "A deep neural network has multiple hidden layers (typically more than 2-3), allowing it to learn complex hierarchical patterns."
                },
                {
                    "question": "What is the vanishing gradient problem?",
                    "options": ["Gradients become too large", "Gradients become very small in deep networks", "Gradients disappear completely", "Gradients become negative"],
                    "correct": 1,
                    "explanation": "The vanishing gradient problem occurs when gradients become very small as they propagate back through deep networks, making learning difficult."
                },
                {
                    "question": "Which layer type is typically used for image recognition?",
                    "options": ["Dense layer", "Convolutional layer", "Recurrent layer", "Dropout layer"],
                    "correct": 1,
                    "explanation": "Convolutional layers are specifically designed for image recognition as they can detect local features and patterns in images."
                },
                {
                    "question": "What is dropout in neural networks?",
                    "options": ["A type of layer", "A regularization technique", "An activation function", "A loss function"],
                    "correct": 1,
                    "explanation": "Dropout is a regularization technique that randomly sets some neurons to zero during training to prevent overfitting."
                }
            ],
            "javascript": [
                {
                    "question": "Which of the following is the correct way to declare a variable in JavaScript?",
                    "options": ["variable x = 5;", "var x = 5;", "declare x = 5;", "x := 5;"],
                    "correct": 1,
                    "explanation": "In JavaScript, variables are declared using 'var', 'let', or 'const' keywords."
                },
                {
                    "question": "What is the difference between '==' and '===' in JavaScript?",
                    "options": ["No difference", "'==' checks type, '===' doesn't", "'===' checks type and value, '==' only value", "'==' is faster"],
                    "correct": 2,
                    "explanation": "'===' (strict equality) checks both type and value, while '==' (loose equality) only checks value after type coercion."
                },
                {
                    "question": "Which method is used to add an element to the end of an array?",
                    "options": ["add()", "append()", "push()", "insert()"],
                    "correct": 2,
                    "explanation": "The push() method adds one or more elements to the end of an array and returns the new length."
                },
                {
                    "question": "What is a closure in JavaScript?",
                    "options": ["A way to close files", "A function with access to outer scope", "A loop structure", "An error handling mechanism"],
                    "correct": 1,
                    "explanation": "A closure is a function that has access to variables in its outer (enclosing) scope even after the outer function has returned."
                },
                {
                    "question": "Which of the following is NOT a JavaScript data type?",
                    "options": ["undefined", "boolean", "float", "symbol"],
                    "correct": 2,
                    "explanation": "JavaScript doesn't have a 'float' data type. Numbers in JavaScript are all of type 'number'."
                },
                {
                    "question": "What does 'this' refer to in JavaScript?",
                    "options": ["The current function", "The global object", "The object that owns the method", "The previous element"],
                    "correct": 2,
                    "explanation": "'this' refers to the object that is executing the current function or method."
                },
                {
                    "question": "Which method is used to remove the last element from an array?",
                    "options": ["pop()", "remove()", "delete()", "splice()"],
                    "correct": 0,
                    "explanation": "The pop() method removes and returns the last element from an array."
                },
                {
                    "question": "What is the correct way to create a function in JavaScript?",
                    "options": ["function = myFunc() {}", "function myFunc() {}", "create function myFunc() {}", "def myFunc() {}"],
                    "correct": 1,
                    "explanation": "Functions in JavaScript are declared using the 'function' keyword followed by the function name and parentheses."
                },
                {
                    "question": "Which operator is used for strict inequality in JavaScript?",
                    "options": ["!=", "!==", "<>", "=/="],
                    "correct": 1,
                    "explanation": "The '!==' operator checks for strict inequality (different type or value)."
                },
                {
                    "question": "What is the purpose of JSON.parse()?",
                    "options": ["To create JSON", "To convert JSON string to object", "To validate JSON", "To format JSON"],
                    "correct": 1,
                    "explanation": "JSON.parse() converts a JSON string into a JavaScript object."
                }
            ],
            "data science": [
                {
                    "question": "What is the first step in the data science process?",
                    "options": ["Model building", "Data collection", "Data visualization", "Result interpretation"],
                    "correct": 1,
                    "explanation": "Data collection is typically the first step, as you need data before you can analyze or model it."
                },
                {
                    "question": "Which Python library is most commonly used for data manipulation?",
                    "options": ["NumPy", "Pandas", "Matplotlib", "Scikit-learn"],
                    "correct": 1,
                    "explanation": "Pandas is the most popular library for data manipulation and analysis in Python."
                },
                {
                    "question": "What does EDA stand for in data science?",
                    "options": ["Efficient Data Analysis", "Exploratory Data Analysis", "Extended Data Application", "Experimental Data Approach"],
                    "correct": 1,
                    "explanation": "EDA stands for Exploratory Data Analysis, which involves examining data to understand its characteristics."
                },
                {
                    "question": "Which visualization is best for showing the distribution of a single variable?",
                    "options": ["Scatter plot", "Line chart", "Histogram", "Pie chart"],
                    "correct": 2,
                    "explanation": "Histograms are ideal for showing the distribution of a single continuous variable."
                },
                {
                    "question": "What is missing data imputation?",
                    "options": ["Removing missing data", "Filling in missing values", "Ignoring missing data", "Creating new data"],
                    "correct": 1,
                    "explanation": "Imputation is the process of filling in missing values with estimated values based on other available data."
                },
                {
                    "question": "Which correlation coefficient ranges from -1 to 1?",
                    "options": ["Spearman", "Pearson", "Kendall", "All of the above"],
                    "correct": 3,
                    "explanation": "All major correlation coefficients (Pearson, Spearman, Kendall) range from -1 to 1."
                },
                {
                    "question": "What is feature scaling?",
                    "options": ["Adding new features", "Removing features", "Normalizing feature values", "Selecting important features"],
                    "correct": 2,
                    "explanation": "Feature scaling involves normalizing or standardizing feature values to ensure they're on similar scales."
                },
                {
                    "question": "Which type of chart is best for showing relationships between two variables?",
                    "options": ["Bar chart", "Scatter plot", "Pie chart", "Histogram"],
                    "correct": 1,
                    "explanation": "Scatter plots are ideal for visualizing relationships between two continuous variables."
                },
                {
                    "question": "What is the purpose of data cleaning?",
                    "options": ["To reduce data size", "To improve data quality", "To speed up analysis", "To create backups"],
                    "correct": 1,
                    "explanation": "Data cleaning aims to improve data quality by handling missing values, outliers, and inconsistencies."
                },
                {
                    "question": "Which statistical measure is most affected by outliers?",
                    "options": ["Median", "Mode", "Mean", "Range"],
                    "correct": 2,
                    "explanation": "The mean is most affected by outliers because it considers all values in its calculation."
                }
            ]
        }
        
        # Get topic-specific questions or use general ones
        topic_lower = topic.lower()
        base_questions = []
        
        for key in question_banks:
            if key in topic_lower or topic_lower in key:
                base_questions = question_banks[key]
                break
        
        # If no specific topic found, create general questions
        if not base_questions:
            base_questions = [
                {
                    "question": f"What is a fundamental concept in {topic}?",
                    "options": [f"Basic principle of {topic}", f"Advanced technique in {topic}", f"Unrelated concept", f"Complex theory"],
                    "correct": 0,
                    "explanation": f"This question tests your understanding of fundamental concepts in {topic}."
                },
                {
                    "question": f"Which approach is commonly used in {topic}?",
                    "options": [f"Standard {topic} method", f"Uncommon approach", f"Irrelevant technique", f"Outdated method"],
                    "correct": 0,
                    "explanation": f"This tests knowledge of common approaches and methods used in {topic}."
                },
                {
                    "question": f"What is the primary goal of {topic}?",
                    "options": [f"To achieve {topic} objectives", f"To complicate processes", f"To avoid learning", f"To create confusion"],
                    "correct": 0,
                    "explanation": f"Understanding the primary goals and objectives is crucial in {topic}."
                }
            ]
        
        # Generate questions ensuring we have at least the requested count
        for i in range(count):
            if i < len(base_questions):
                q = base_questions[i]
                question_id = str(uuid.uuid4())
                questions.append(QuizQuestion(
                    id=question_id,
                    question=q["question"],
                    options=q["options"],
                    correct_answer=q["correct"],
                    difficulty=difficulty
                ))
                # Store explanation
                self.quiz_explanations[question_id] = q["explanation"]
            else:
                # Cycle through questions if we need more
                q = base_questions[i % len(base_questions)]
                question_id = str(uuid.uuid4())
                modified_question = f"{q['question']} (Question {i+1})"
                questions.append(QuizQuestion(
                    id=question_id,
                    question=modified_question,
                    options=q["options"],
                    correct_answer=q["correct"],
                    difficulty=difficulty
                ))
                self.quiz_explanations[question_id] = q["explanation"]
        
        return questions
    
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
    
    async def analyze_quiz_performance(self, student_id: str, quiz_results: List[Dict]) -> Dict[str, Any]:
        """Analyze quiz performance and identify weak concepts"""
        total_questions = len(quiz_results)
        correct_answers = sum(1 for result in quiz_results if result['correct'])
        score_percentage = (correct_answers / total_questions) * 100
        
        # Categorize questions by topic/concept
        concept_performance = {}
        weak_concepts = []
        strong_concepts = []
        
        for result in quiz_results:
            question_id = result['question_id']
            is_correct = result['correct']
            
            # Extract concept from question (simplified - in production use NLP)
            concept = self._extract_concept_from_question(result.get('question', ''))
            
            if concept not in concept_performance:
                concept_performance[concept] = {'correct': 0, 'total': 0, 'questions': []}
            
            concept_performance[concept]['total'] += 1
            concept_performance[concept]['questions'].append(result)
            
            if is_correct:
                concept_performance[concept]['correct'] += 1
        
        # Identify weak and strong concepts
        for concept, performance in concept_performance.items():
            accuracy = performance['correct'] / performance['total']
            if accuracy < 0.6:  # Less than 60% accuracy
                weak_concepts.append({
                    'concept': concept,
                    'accuracy': accuracy,
                    'questions_missed': performance['total'] - performance['correct'],
                    'total_questions': performance['total']
                })
            elif accuracy >= 0.8:  # 80% or higher accuracy
                strong_concepts.append({
                    'concept': concept,
                    'accuracy': accuracy,
                    'questions_correct': performance['correct'],
                    'total_questions': performance['total']
                })
        
        # Generate performance insights
        performance_level = self._get_performance_level(score_percentage)
        recommendations = await self._generate_study_recommendations(weak_concepts, strong_concepts)
        
        # Update student profile
        profile = self.get_student_profile(student_id)
        for concept_data in weak_concepts:
            concept = concept_data['concept']
            if concept in profile['knowledge_areas']:
                profile['knowledge_areas'][concept] = max(0, profile['knowledge_areas'][concept] - 10)
            else:
                profile['knowledge_areas'][concept] = 30  # Below average
        
        for concept_data in strong_concepts:
            concept = concept_data['concept']
            if concept in profile['knowledge_areas']:
                profile['knowledge_areas'][concept] = min(100, profile['knowledge_areas'][concept] + 15)
            else:
                profile['knowledge_areas'][concept] = 80  # Above average
        
        return {
            'score': {
                'correct': correct_answers,
                'total': total_questions,
                'percentage': round(score_percentage, 1)
            },
            'performance_level': performance_level,
            'weak_concepts': weak_concepts,
            'strong_concepts': strong_concepts,
            'concept_breakdown': concept_performance,
            'recommendations': recommendations,
            'next_steps': self._get_next_steps(weak_concepts, performance_level)
        }
    
    def _extract_concept_from_question(self, question: str) -> str:
        """Extract main concept from question text"""
        # Simplified concept extraction - in production use NLP
        question_lower = question.lower()
        
        concept_keywords = {
            'machine learning': ['machine learning', 'ml', 'algorithm', 'model', 'training', 'prediction'],
            'neural networks': ['neural', 'network', 'neuron', 'layer', 'activation', 'backpropagation'],
            'data structures': ['array', 'list', 'tree', 'graph', 'stack', 'queue', 'hash'],
            'programming': ['function', 'variable', 'loop', 'condition', 'syntax', 'code'],
            'mathematics': ['equation', 'formula', 'calculation', 'number', 'algebra', 'geometry'],
            'science': ['experiment', 'hypothesis', 'theory', 'observation', 'analysis']
        }
        
        for concept, keywords in concept_keywords.items():
            if any(keyword in question_lower for keyword in keywords):
                return concept
        
        return 'general knowledge'
    
    def _get_performance_level(self, score_percentage: float) -> Dict[str, str]:
        """Determine performance level based on score"""
        if score_percentage >= 90:
            return {
                'level': 'Excellent',
                'description': 'Outstanding performance! You have mastered this topic.',
                'color': 'green'
            }
        elif score_percentage >= 80:
            return {
                'level': 'Good',
                'description': 'Good job! You have a solid understanding with room for improvement.',
                'color': 'blue'
            }
        elif score_percentage >= 70:
            return {
                'level': 'Average',
                'description': 'You have a basic understanding. Focus on weak areas for improvement.',
                'color': 'yellow'
            }
        elif score_percentage >= 60:
            return {
                'level': 'Below Average',
                'description': 'You need more practice. Review the concepts and try again.',
                'color': 'orange'
            }
        else:
            return {
                'level': 'Needs Improvement',
                'description': 'Significant improvement needed. Consider reviewing fundamentals.',
                'color': 'red'
            }
    
    async def _generate_study_recommendations(self, weak_concepts: List[Dict], strong_concepts: List[Dict]) -> List[Dict[str, str]]:
        """Generate personalized study recommendations"""
        recommendations = []
        
        if weak_concepts:
            for concept_data in weak_concepts[:3]:  # Top 3 weak concepts
                concept = concept_data['concept']
                recommendations.append({
                    'type': 'improvement',
                    'title': f"Focus on {concept.title()}",
                    'description': f"You got {concept_data['questions_missed']} out of {concept_data['total_questions']} questions wrong in this area.",
                    'action': f"Review {concept} fundamentals and practice more questions",
                    'resources': await self._get_learning_resources(concept)
                })
        
        if strong_concepts:
            for concept_data in strong_concepts[:2]:  # Top 2 strong concepts
                concept = concept_data['concept']
                recommendations.append({
                    'type': 'strength',
                    'title': f"Excellent work on {concept.title()}",
                    'description': f"You answered {concept_data['questions_correct']} out of {concept_data['total_questions']} questions correctly!",
                    'action': f"Consider exploring advanced topics in {concept}",
                    'resources': await self._get_learning_resources(f"advanced {concept}")
                })
        
        return recommendations
    
    def _get_next_steps(self, weak_concepts: List[Dict], performance_level: Dict) -> List[str]:
        """Get specific next steps based on performance"""
        steps = []
        
        if performance_level['level'] in ['Excellent', 'Good']:
            steps.append("🎉 Great job! Consider taking a more challenging quiz or exploring advanced topics.")
            steps.append("📚 Try teaching these concepts to someone else to reinforce your knowledge.")
        
        if weak_concepts:
            steps.append(f"📖 Review the following concepts: {', '.join([c['concept'] for c in weak_concepts[:3]])}")
            steps.append("🔄 Retake the quiz after studying to track your improvement.")
            steps.append("💡 Use the provided learning resources for targeted practice.")
        
        if performance_level['level'] in ['Below Average', 'Needs Improvement']:
            steps.append("🎯 Focus on understanding fundamentals before moving to advanced topics.")
            steps.append("👥 Consider finding a study partner or joining a study group.")
            steps.append("⏰ Set aside regular study time each day for consistent improvement.")
        
        return steps
    
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

    async def check_answer(self, question_id: str, answer: int, student_id: str = None) -> Dict[str, Any]:
        """Enhanced answer checking with detailed explanations"""
        is_correct = self.quiz_answers.get(question_id, 0) == answer
        explanation = self.quiz_explanations.get(question_id, "Keep learning and practicing!")
        
        result = {
            "correct": is_correct,
            "explanation": explanation,
            "performance_update": None
        }
        
        # Update student performance if student_id provided
        if student_id:
            result["performance_update"] = {
                "points_earned": 10 if is_correct else 2,
                "streak_updated": True
            }
        
        return result

    def store_quiz_answers(self, questions: List[QuizQuestion]):
        """Store correct answers and explanations for later verification"""
        for question in questions:
            self.quiz_answers[question.id] = question.correct_answer
            # Store explanation if not already stored
            if question.id not in self.quiz_explanations:
                self.quiz_explanations[question.id] = f"The correct answer relates to fundamental concepts in this topic area."
    
    def _extract_topics_from_message(self, message: str) -> List[str]:
        """Extract potential topics from a message for knowledge tracking"""
        # Common educational topics
        topic_keywords = {
            'python': ['python', 'programming', 'code', 'function', 'variable', 'list', 'dictionary'],
            'machine learning': ['machine learning', 'ml', 'algorithm', 'model', 'training', 'prediction'],
            'neural networks': ['neural network', 'deep learning', 'neuron', 'backpropagation', 'activation'],
            'javascript': ['javascript', 'js', 'web development', 'dom', 'event', 'callback'],
            'data science': ['data science', 'statistics', 'analysis', 'visualization', 'pandas', 'numpy'],
            'mathematics': ['math', 'algebra', 'calculus', 'geometry', 'equation', 'formula'],
            'physics': ['physics', 'force', 'energy', 'motion', 'wave', 'particle'],
            'chemistry': ['chemistry', 'molecule', 'atom', 'reaction', 'compound', 'element']
        }
        
        message_lower = message.lower()
        detected_topics = []
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                detected_topics.append(topic)
        
        return detected_topics if detected_topics else ['general']
    
    def _extract_main_topic(self, message: str) -> str:
        """Extract the main topic from a message"""
        topics = self._extract_topics_from_message(message)
        return topics[0] if topics else 'general'
    
    def _adapt_difficulty_for_pace(self, skp: StudentKnowledgeProfile, topic: str, base_difficulty: int) -> int:
        """Adapt difficulty based on student's learning pace and mastery level"""
        # Get current mastery level for the topic
        mastery_level = skp.knowledge_areas.get(topic, 10) / 100  # Convert to 0-1 scale
        learning_velocity = skp.learning_velocity.get(topic, 0.0)
        
        # Adapt based on mastery level
        if mastery_level < 0.3:
            adapted_difficulty = max(1, base_difficulty - 1)
        elif mastery_level > 0.8:
            adapted_difficulty = min(3, base_difficulty + 1)
        else:
            if learning_velocity > 0.1:
                adapted_difficulty = min(3, base_difficulty + 1)
            elif learning_velocity < -0.1:
                adapted_difficulty = max(1, base_difficulty - 1)
            else:
                adapted_difficulty = base_difficulty
        
        return adapted_difficulty
    
    def _get_pace_recommendations(self, skp: StudentKnowledgeProfile, topic: str) -> Dict[str, Any]:
        """Get learning pace recommendations for the student"""
        mastery_level = skp.knowledge_areas.get(topic, 10) / 100
        learning_velocity = skp.learning_velocity.get(topic, 0.0)
        
        if mastery_level < 0.3:
            pace_level = "foundational"
            explanation = "Building strong foundations with step-by-step explanations"
        elif mastery_level < 0.6:
            pace_level = "developing"
            explanation = "Reinforcing understanding with guided practice"
        elif mastery_level < 0.8:
            pace_level = "proficient"
            explanation = "Advancing knowledge with deeper exploration"
        else:
            pace_level = "advanced"
            explanation = "Challenging with expert-level insights"
        
        return {
            "pace_level": pace_level,
            "explanation": explanation,
            "mastery_level": mastery_level,
            "learning_velocity": learning_velocity
        }
    
    def _create_pace_adaptive_prompt(self, profile: Dict[str, Any], skp: StudentKnowledgeProfile, 
                                   difficulty: int, context_info: str, pace_recommendations: Dict) -> str:
        """Create an adaptive system prompt based on learning pace"""
        
        base_prompt = f"""You are an AI tutor that adapts to each student's learning pace and style. 

STUDENT LEARNING PROFILE:
- Learning Pace: {pace_recommendations['pace_level']}
- Mastery Level: {pace_recommendations['mastery_level']:.1%}
- Learning Velocity: {pace_recommendations['learning_velocity']:.2f}
- Pace Strategy: {pace_recommendations['explanation']}

DIFFICULTY LEVEL: {difficulty} (adapted based on student's pace)

TEACHING GUIDELINES:
1. Match your explanation complexity to the student's current mastery level
2. Adjust pacing based on their learning velocity
3. Use appropriate examples for their skill level
4. Provide the right amount of detail - not too much, not too little
5. Encourage progress while maintaining appropriate challenge level

{context_info}

Remember: Your goal is to help the student learn effectively at their optimal pace."""

        return base_prompt
    
    def _track_learning_interaction(self, student_id: str, topic: str, question: str, 
                                  response: str, difficulty: int):
        """Track learning interaction for pace analysis"""
        try:
            if not hasattr(self, 'learning_sessions'):
                self.learning_sessions = {}
            
            if student_id not in self.learning_sessions:
                self.learning_sessions[student_id] = []
            
            # Simple tracking for now
            interaction = {
                'timestamp': datetime.now().isoformat(),
                'topic': topic,
                'question': question,
                'difficulty': difficulty
            }
            self.learning_sessions[student_id].append(interaction)
            
        except Exception as e:
            print(f"Error tracking learning interaction: {e}")

# Create a global instance
ai_service = EnhancedAIService()