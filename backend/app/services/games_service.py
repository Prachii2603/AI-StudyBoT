from typing import List, Dict, Any
import random
import uuid
from datetime import datetime

class GamesService:
    def __init__(self):
        self.active_games = {}
        self.game_scores = {}
        
    def get_available_games(self) -> List[Dict[str, Any]]:
        """Get list of available educational games"""
        return [
            {
                "id": "word-match",
                "name": "Word Match Challenge",
                "description": "Match terms with their definitions",
                "difficulty": "Beginner",
                "category": "Vocabulary",
                "estimated_time": "5-10 minutes",
                "icon": "🎯"
            },
            {
                "id": "quick-quiz",
                "name": "Lightning Quiz",
                "description": "Answer questions as fast as you can",
                "difficulty": "Beginner",
                "category": "General Knowledge",
                "estimated_time": "3-5 minutes",
                "icon": "⚡"
            },
            {
                "id": "concept-builder",
                "name": "Concept Builder",
                "description": "Build understanding step by step",
                "difficulty": "Beginner",
                "category": "Learning",
                "estimated_time": "10-15 minutes",
                "icon": "🏗️"
            },
            {
                "id": "memory-cards",
                "name": "Memory Cards",
                "description": "Flip cards to match pairs",
                "difficulty": "Beginner",
                "category": "Memory",
                "estimated_time": "5-8 minutes",
                "icon": "🃏"
            },
            {
                "id": "drag-drop",
                "name": "Drag & Drop Sorting",
                "description": "Sort items into correct categories",
                "difficulty": "Beginner",
                "category": "Classification",
                "estimated_time": "5-10 minutes",
                "icon": "📦"
            }
        ]
    
    def start_word_match_game(self, topic: str, student_id: str) -> Dict[str, Any]:
        """Start a word matching game"""
        game_id = str(uuid.uuid4())
        
        # Generate word pairs based on topic
        word_pairs = self._generate_word_pairs(topic)
        
        # Shuffle options
        terms = [pair["term"] for pair in word_pairs]
        definitions = [pair["definition"] for pair in word_pairs]
        random.shuffle(definitions)
        
        game_data = {
            "game_id": game_id,
            "type": "word-match",
            "topic": topic,
            "student_id": student_id,
            "pairs": word_pairs,
            "terms": terms,
            "definitions": definitions,
            "matches_made": [],
            "score": 0,
            "start_time": datetime.now().isoformat(),
            "status": "active"
        }
        
        self.active_games[game_id] = game_data
        
        return {
            "game_id": game_id,
            "terms": terms,
            "definitions": definitions,
            "instructions": "Match each term with its correct definition. Click on a term, then click on its matching definition!",
            "total_pairs": len(word_pairs)
        }
    
    def start_lightning_quiz(self, topic: str, student_id: str) -> Dict[str, Any]:
        """Start a lightning quiz game"""
        game_id = str(uuid.uuid4())
        
        # Generate quick questions
        questions = self._generate_lightning_questions(topic)
        
        game_data = {
            "game_id": game_id,
            "type": "lightning-quiz",
            "topic": topic,
            "student_id": student_id,
            "questions": questions,
            "current_question": 0,
            "score": 0,
            "correct_answers": 0,
            "start_time": datetime.now().isoformat(),
            "time_limit": 30,  # 30 seconds per question
            "status": "active"
        }
        
        self.active_games[game_id] = game_data
        
        return {
            "game_id": game_id,
            "question": questions[0],
            "question_number": 1,
            "total_questions": len(questions),
            "time_limit": 30,
            "instructions": "Answer as many questions correctly as you can! You have 30 seconds per question."
        }
    
    def start_memory_cards_game(self, topic: str, student_id: str) -> Dict[str, Any]:
        """Start a memory cards game"""
        game_id = str(uuid.uuid4())
        
        # Generate card pairs
        card_pairs = self._generate_memory_cards(topic)
        
        # Create shuffled deck
        cards = []
        for i, pair in enumerate(card_pairs):
            cards.extend([
                {"id": f"{i}a", "content": pair["term"], "type": "term", "pair_id": i},
                {"id": f"{i}b", "content": pair["definition"], "type": "definition", "pair_id": i}
            ])
        
        random.shuffle(cards)
        
        game_data = {
            "game_id": game_id,
            "type": "memory-cards",
            "topic": topic,
            "student_id": student_id,
            "cards": cards,
            "flipped_cards": [],
            "matched_pairs": [],
            "moves": 0,
            "score": 0,
            "start_time": datetime.now().isoformat(),
            "status": "active"
        }
        
        self.active_games[game_id] = game_data
        
        return {
            "game_id": game_id,
            "cards": [{"id": card["id"], "flipped": False} for card in cards],
            "total_pairs": len(card_pairs),
            "instructions": "Flip two cards at a time to find matching pairs. Try to remember where each card is!"
        }
    
    def make_word_match(self, game_id: str, term: str, definition: str) -> Dict[str, Any]:
        """Process a word match attempt"""
        if game_id not in self.active_games:
            return {"error": "Game not found"}
        
        game = self.active_games[game_id]
        
        # Check if match is correct
        correct_pair = None
        for pair in game["pairs"]:
            if pair["term"] == term and pair["definition"] == definition:
                correct_pair = pair
                break
        
        if correct_pair:
            game["matches_made"].append(correct_pair)
            game["score"] += 10
            
            # Check if game is complete
            if len(game["matches_made"]) == len(game["pairs"]):
                game["status"] = "completed"
                game["end_time"] = datetime.now().isoformat()
                return {
                    "correct": True,
                    "game_completed": True,
                    "final_score": game["score"],
                    "message": "Congratulations! You've matched all pairs!"
                }
            
            return {
                "correct": True,
                "score": game["score"],
                "matches_remaining": len(game["pairs"]) - len(game["matches_made"]),
                "message": "Great match!"
            }
        else:
            return {
                "correct": False,
                "score": game["score"],
                "message": "Not quite right. Try again!"
            }
    
    def answer_lightning_question(self, game_id: str, answer: int) -> Dict[str, Any]:
        """Process lightning quiz answer"""
        if game_id not in self.active_games:
            return {"error": "Game not found"}
        
        game = self.active_games[game_id]
        current_q = game["questions"][game["current_question"]]
        
        is_correct = current_q["correct_answer"] == answer
        if is_correct:
            game["correct_answers"] += 1
            game["score"] += 10
        
        game["current_question"] += 1
        
        # Check if game is complete
        if game["current_question"] >= len(game["questions"]):
            game["status"] = "completed"
            game["end_time"] = datetime.now().isoformat()
            
            accuracy = (game["correct_answers"] / len(game["questions"])) * 100
            
            return {
                "correct": is_correct,
                "game_completed": True,
                "final_score": game["score"],
                "accuracy": round(accuracy, 1),
                "correct_answers": game["correct_answers"],
                "total_questions": len(game["questions"]),
                "message": f"Game complete! You got {game['correct_answers']} out of {len(game['questions'])} correct!"
            }
        
        # Next question
        next_question = game["questions"][game["current_question"]]
        return {
            "correct": is_correct,
            "score": game["score"],
            "question": next_question,
            "question_number": game["current_question"] + 1,
            "total_questions": len(game["questions"])
        }
    
    def flip_memory_card(self, game_id: str, card_id: str) -> Dict[str, Any]:
        """Process memory card flip"""
        if game_id not in self.active_games:
            return {"error": "Game not found"}
        
        game = self.active_games[game_id]
        
        # Find the card
        card = None
        for c in game["cards"]:
            if c["id"] == card_id:
                card = c
                break
        
        if not card:
            return {"error": "Card not found"}
        
        # Add to flipped cards
        game["flipped_cards"].append(card)
        
        # Check if we have two flipped cards
        if len(game["flipped_cards"]) == 2:
            game["moves"] += 1
            card1, card2 = game["flipped_cards"]
            
            # Check if they match
            if card1["pair_id"] == card2["pair_id"]:
                # Match found
                game["matched_pairs"].extend([card1["id"], card2["id"]])
                game["score"] += 20
                game["flipped_cards"] = []
                
                # Check if game is complete
                if len(game["matched_pairs"]) == len(game["cards"]):
                    game["status"] = "completed"
                    game["end_time"] = datetime.now().isoformat()
                    
                    return {
                        "match": True,
                        "game_completed": True,
                        "final_score": game["score"],
                        "moves": game["moves"],
                        "message": "Congratulations! You've found all pairs!"
                    }
                
                return {
                    "match": True,
                    "score": game["score"],
                    "moves": game["moves"],
                    "pairs_remaining": (len(game["cards"]) - len(game["matched_pairs"])) // 2
                }
            else:
                # No match - cards will flip back
                game["flipped_cards"] = []
                return {
                    "match": False,
                    "score": game["score"],
                    "moves": game["moves"],
                    "message": "No match. Try to remember where these cards are!"
                }
        
        return {
            "card_flipped": True,
            "card_content": card["content"],
            "waiting_for_second_card": len(game["flipped_cards"]) == 1
        }
    
    def _generate_word_pairs(self, topic: str) -> List[Dict[str, str]]:
        """Generate word-definition pairs for the topic"""
        topic_pairs = {
            "machine learning": [
                {"term": "Algorithm", "definition": "A set of rules or instructions for solving a problem"},
                {"term": "Training Data", "definition": "Data used to teach a machine learning model"},
                {"term": "Overfitting", "definition": "When a model learns training data too well and performs poorly on new data"},
                {"term": "Feature", "definition": "An individual measurable property of observed phenomena"},
                {"term": "Supervised Learning", "definition": "Learning with labeled training examples"},
                {"term": "Neural Network", "definition": "Computing system inspired by biological neural networks"}
            ],
            "programming": [
                {"term": "Variable", "definition": "A storage location with an associated name that contains data"},
                {"term": "Function", "definition": "A reusable block of code that performs a specific task"},
                {"term": "Loop", "definition": "A sequence of instructions that repeats until a condition is met"},
                {"term": "Array", "definition": "A collection of elements stored at contiguous memory locations"},
                {"term": "Debugging", "definition": "The process of finding and fixing errors in code"},
                {"term": "API", "definition": "Application Programming Interface for software communication"}
            ]
        }
        
        return topic_pairs.get(topic.lower(), [
            {"term": "Concept A", "definition": f"Definition related to {topic}"},
            {"term": "Concept B", "definition": f"Another definition about {topic}"},
            {"term": "Concept C", "definition": f"Third concept in {topic}"},
            {"term": "Concept D", "definition": f"Fourth concept about {topic}"}
        ])
    
    def _generate_lightning_questions(self, topic: str) -> List[Dict[str, Any]]:
        """Generate quick questions for lightning quiz"""
        questions = [
            {
                "question": f"What is a key concept in {topic}?",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "correct_answer": 0
            },
            {
                "question": f"Which statement about {topic} is true?",
                "options": ["Statement 1", "Statement 2", "Statement 3", "Statement 4"],
                "correct_answer": 1
            },
            {
                "question": f"In {topic}, what does this term mean?",
                "options": ["Meaning A", "Meaning B", "Meaning C", "Meaning D"],
                "correct_answer": 2
            },
            {
                "question": f"What is the primary use of {topic}?",
                "options": ["Use A", "Use B", "Use C", "Use D"],
                "correct_answer": 0
            },
            {
                "question": f"Which approach is common in {topic}?",
                "options": ["Approach A", "Approach B", "Approach C", "Approach D"],
                "correct_answer": 1
            }
        ]
        
        return questions
    
    def _generate_memory_cards(self, topic: str) -> List[Dict[str, str]]:
        """Generate memory card pairs"""
        return self._generate_word_pairs(topic)[:6]  # 6 pairs = 12 cards
    
    def get_game_leaderboard(self, game_type: str) -> List[Dict[str, Any]]:
        """Get leaderboard for a specific game type"""
        # Mock leaderboard data
        return [
            {"rank": 1, "player": "Student A", "score": 180, "time": "2:45"},
            {"rank": 2, "player": "Student B", "score": 160, "time": "3:12"},
            {"rank": 3, "player": "Student C", "score": 140, "time": "3:45"},
            {"rank": 4, "player": "You", "score": 120, "time": "4:20"},
            {"rank": 5, "player": "Student D", "score": 100, "time": "5:10"}
        ]

# Create global instance
games_service = GamesService()