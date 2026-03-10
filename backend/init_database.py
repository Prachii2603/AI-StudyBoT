#!/usr/bin/env python3
"""
Database initialization script for AI StudyBot
Creates tables and adds demo data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import init_db, SessionLocal
from app.services.database_service import DatabaseService
from datetime import datetime

def create_demo_user():
    """Create a demo user for testing"""
    db = SessionLocal()
    db_service = DatabaseService(db)
    
    try:
        # Check if demo user already exists
        existing_user = db_service.get_user_by_email("demo@example.com")
        if existing_user:
            print("Demo user already exists!")
            return
        
        # Create demo user
        demo_user_data = {
            "name": "Demo User",
            "email": "demo@example.com",
            "password": "password123",
            "age": 25,
            "grade": "college",
            "interests": ["Programming", "Machine Learning", "Mathematics", "Data Science"]
        }
        
        user = db_service.create_user(demo_user_data)
        print(f"Demo user created successfully!")
        print(f"Email: {user.email}")
        print(f"Password: password123")
        print(f"User ID: {user.id}")
        
        # Add some sample data
        # Create a learning session
        session = db_service.create_learning_session(
            user_id=user.id,
            session_type="quiz",
            topic="Python Programming",
            difficulty=2
        )
        
        # Add a quiz result
        quiz_data = {
            "session_id": session.id,
            "topic": "Python Programming",
            "difficulty": 2,
            "total_questions": 10,
            "correct_answers": 8,
            "score_percentage": 80.0,
            "time_taken_seconds": 300,
            "weak_areas": ["List Comprehensions"],
            "strong_areas": ["Functions", "Variables", "Loops"],
            "quiz_data": {"questions": [], "answers": []}
        }
        
        db_service.save_quiz_result(user.id, quiz_data)
        
        # Add game score
        db_service.save_game_score(
            user_id=user.id,
            game_type="word_match",
            score=150,
            topic="Python Programming",
            level=1,
            time_taken=120
        )
        
        # Update user progress
        db_service.update_user_progress(
            user_id=user.id,
            topic="Python Programming",
            performance=0.8,
            difficulty=2
        )
        
        print("Sample data added successfully!")
        
    except Exception as e:
        print(f"Error creating demo user: {e}")
    finally:
        db.close()

def main():
    """Main initialization function"""
    print("Initializing AI StudyBot Database...")
    
    # Create tables
    init_db()
    print("Database tables created successfully!")
    
    # Create demo user
    create_demo_user()
    
    print("\nDatabase initialization complete!")
    print("\nYou can now:")
    print("1. Start the backend server: python -m uvicorn app.main:app --reload")
    print("2. Login with demo@example.com / password123")
    print("3. Or register a new account")

if __name__ == "__main__":
    main()