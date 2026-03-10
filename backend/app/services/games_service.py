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
            "python": [
                {"term": "Variable", "definition": "A named storage location that holds data"},
                {"term": "Function", "definition": "A reusable block of code that performs a specific task"},
                {"term": "List", "definition": "An ordered collection of items that can be modified"},
                {"term": "Dictionary", "definition": "A collection of key-value pairs"},
                {"term": "Loop", "definition": "A programming construct that repeats code"},
                {"term": "String", "definition": "A sequence of characters enclosed in quotes"},
                {"term": "Integer", "definition": "A whole number without decimal points"},
                {"term": "Boolean", "definition": "A data type that can be True or False"}
            ],
            "machine learning": [
                {"term": "Algorithm", "definition": "A set of rules or instructions for solving a problem"},
                {"term": "Training Data", "definition": "Data used to teach a machine learning model"},
                {"term": "Overfitting", "definition": "When a model learns training data too well and performs poorly on new data"},
                {"term": "Feature", "definition": "An individual measurable property of observed phenomena"},
                {"term": "Supervised Learning", "definition": "Learning with labeled training examples"},
                {"term": "Neural Network", "definition": "Computing system inspired by biological neural networks"},
                {"term": "Classification", "definition": "Predicting categories or classes"},
                {"term": "Regression", "definition": "Predicting continuous numerical values"}
            ],
            "javascript": [
                {"term": "Variable", "definition": "Container for storing data values"},
                {"term": "Function", "definition": "Block of code designed to perform a particular task"},
                {"term": "Array", "definition": "Ordered list of values stored in a single variable"},
                {"term": "Object", "definition": "Collection of properties and methods"},
                {"term": "Event", "definition": "Action that can be detected by JavaScript"},
                {"term": "DOM", "definition": "Document Object Model - structure of HTML elements"},
                {"term": "Callback", "definition": "Function passed as argument to another function"},
                {"term": "Promise", "definition": "Object representing eventual completion of async operation"}
            ],
            "neural networks": [
                {"term": "Neuron", "definition": "Basic processing unit that receives and sends signals"},
                {"term": "Weight", "definition": "Parameter that determines connection strength between neurons"},
                {"term": "Bias", "definition": "Additional parameter that shifts the activation function"},
                {"term": "Activation Function", "definition": "Function that determines neuron output based on input"},
                {"term": "Backpropagation", "definition": "Algorithm for training networks by updating weights"},
                {"term": "Layer", "definition": "Collection of neurons that process data together"},
                {"term": "Deep Learning", "definition": "Neural networks with multiple hidden layers"},
                {"term": "Gradient", "definition": "Measure of how much to change weights during training"}
            ],
            "data science": [
                {"term": "Dataset", "definition": "Collection of data organized in rows and columns"},
                {"term": "Visualization", "definition": "Graphical representation of data"},
                {"term": "Correlation", "definition": "Statistical measure of relationship between variables"},
                {"term": "Outlier", "definition": "Data point significantly different from others"},
                {"term": "Hypothesis", "definition": "Testable prediction about data"},
                {"term": "Statistics", "definition": "Science of collecting and analyzing numerical data"},
                {"term": "Pandas", "definition": "Python library for data manipulation and analysis"},
                {"term": "Regression", "definition": "Statistical method for modeling relationships"}
            ],
            "programming": [
                {"term": "Variable", "definition": "A storage location with an associated name that contains data"},
                {"term": "Function", "definition": "A reusable block of code that performs a specific task"},
                {"term": "Loop", "definition": "A sequence of instructions that repeats until a condition is met"},
                {"term": "Array", "definition": "A collection of elements stored at contiguous memory locations"},
                {"term": "Debugging", "definition": "The process of finding and fixing errors in code"},
                {"term": "API", "definition": "Application Programming Interface for software communication"},
                {"term": "Algorithm", "definition": "Step-by-step procedure for solving a problem"},
                {"term": "Syntax", "definition": "Rules that define valid constructs in a programming language"}
            ]
        }
        
        # Find matching topic or use generic fallback
        topic_lower = topic.lower()
        for key in topic_pairs:
            if key in topic_lower or topic_lower in key:
                return topic_pairs[key]
        
        # Generic fallback
        return [
            {"term": f"{topic} Concept", "definition": f"Fundamental idea in {topic}"},
            {"term": f"{topic} Method", "definition": f"Common approach used in {topic}"},
            {"term": f"{topic} Tool", "definition": f"Instrument or technique for {topic}"},
            {"term": f"{topic} Process", "definition": f"Series of steps in {topic}"},
            {"term": f"{topic} Theory", "definition": f"Explanation of principles in {topic}"},
            {"term": f"{topic} Application", "definition": f"Practical use of {topic}"}
        ]
    
    def _generate_lightning_questions(self, topic: str) -> List[Dict[str, Any]]:
        """Generate quick questions for lightning quiz"""
        topic_questions = {
            "python": [
                {"question": "What keyword is used to define a function in Python?", "options": ["func", "def", "function", "define"], "correct_answer": 1},
                {"question": "Which data type is mutable in Python?", "options": ["tuple", "string", "list", "int"], "correct_answer": 2},
                {"question": "What symbol is used for comments in Python?", "options": ["//", "#", "/*", "<!--"], "correct_answer": 1},
                {"question": "Which method adds an element to the end of a list?", "options": ["add()", "append()", "insert()", "push()"], "correct_answer": 1},
                {"question": "What is the output of len([1,2,3])?", "options": ["1", "2", "3", "4"], "correct_answer": 2}
            ],
            "machine learning": [
                {"question": "What type of learning uses labeled data?", "options": ["Unsupervised", "Supervised", "Reinforcement", "Deep"], "correct_answer": 1},
                {"question": "What is overfitting?", "options": ["Too simple model", "Perfect model", "Model too complex for data", "Fast training"], "correct_answer": 2},
                {"question": "Which algorithm is used for classification?", "options": ["Linear Regression", "Decision Tree", "K-means", "PCA"], "correct_answer": 1},
                {"question": "What does AI stand for?", "options": ["Automated Intelligence", "Artificial Intelligence", "Advanced Intelligence", "Applied Intelligence"], "correct_answer": 1},
                {"question": "What is cross-validation used for?", "options": ["Data cleaning", "Model evaluation", "Feature selection", "Data collection"], "correct_answer": 1}
            ],
            "javascript": [
                {"question": "Which keyword declares a variable?", "options": ["variable", "var", "declare", "let"], "correct_answer": 1},
                {"question": "What does '===' check?", "options": ["Value only", "Type only", "Type and value", "Reference"], "correct_answer": 2},
                {"question": "Which method adds to end of array?", "options": ["add()", "append()", "push()", "insert()"], "correct_answer": 2},
                {"question": "What is a closure?", "options": ["Loop structure", "Function with outer scope access", "Error handling", "File operation"], "correct_answer": 1},
                {"question": "Which is NOT a JS data type?", "options": ["undefined", "boolean", "float", "symbol"], "correct_answer": 2}
            ],
            "neural networks": [
                {"question": "What is the basic unit of a neural network?", "options": ["Layer", "Neuron", "Weight", "Bias"], "correct_answer": 1},
                {"question": "What do activation functions add?", "options": ["Linearity", "Non-linearity", "Speed", "Memory"], "correct_answer": 1},
                {"question": "What is backpropagation for?", "options": ["Forward pass", "Training weights", "Data preprocessing", "Model evaluation"], "correct_answer": 1},
                {"question": "Which activation is common in hidden layers?", "options": ["Sigmoid", "ReLU", "Linear", "Step"], "correct_answer": 1},
                {"question": "What is a perceptron?", "options": ["Activation function", "Simplest neural network", "Learning algorithm", "Data structure"], "correct_answer": 1}
            ],
            "data science": [
                {"question": "What is the first step in data science?", "options": ["Model building", "Data collection", "Visualization", "Interpretation"], "correct_answer": 1},
                {"question": "Which library is used for data manipulation?", "options": ["NumPy", "Pandas", "Matplotlib", "Scikit-learn"], "correct_answer": 1},
                {"question": "What does EDA stand for?", "options": ["Efficient Data Analysis", "Exploratory Data Analysis", "Extended Data Application", "Experimental Data Approach"], "correct_answer": 1},
                {"question": "Best visualization for distribution?", "options": ["Scatter plot", "Line chart", "Histogram", "Pie chart"], "correct_answer": 2},
                {"question": "What is imputation?", "options": ["Removing missing data", "Filling missing values", "Ignoring missing data", "Creating new data"], "correct_answer": 1}
            ]
        }
        
        # Find matching topic or use generic questions
        topic_lower = topic.lower()
        for key in topic_questions:
            if key in topic_lower or topic_lower in key:
                return topic_questions[key]
        
        # Generic fallback questions
        questions = [
            {
                "question": f"What is a key concept in {topic}?",
                "options": [f"Main concept", f"Secondary idea", f"Unrelated topic", f"Complex theory"],
                "correct_answer": 0
            },
            {
                "question": f"Which statement about {topic} is true?",
                "options": [f"True statement", f"False statement", f"Misleading info", f"Incorrect fact"],
                "correct_answer": 0
            },
            {
                "question": f"In {topic}, what does this term mean?",
                "options": [f"Correct meaning", f"Wrong definition", f"Unrelated term", f"Confusing explanation"],
                "correct_answer": 0
            },
            {
                "question": f"What is the primary use of {topic}?",
                "options": [f"Main application", f"Secondary use", f"Irrelevant purpose", f"Wrong application"],
                "correct_answer": 0
            },
            {
                "question": f"Which approach is common in {topic}?",
                "options": [f"Standard approach", f"Uncommon method", f"Wrong technique", f"Outdated practice"],
                "correct_answer": 0
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