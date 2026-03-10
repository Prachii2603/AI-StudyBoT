# 🗄️ AI StudyBot Database System

## Overview
The AI StudyBot now uses a robust SQLite database system to store all user data, learning progress, chat history, quiz results, and analytics. This replaces the previous in-memory storage with persistent data storage.

## 📊 Database Schema

### Core Tables

#### 1. **Users Table**
Stores user account information and learning profiles.
```sql
- id (Primary Key)
- name
- email (Unique)
- password_hash
- age
- grade
- interests (JSON array)
- created_at, updated_at
- is_active
- total_sessions
- total_questions_answered
- average_score
- preferred_difficulty
- learning_style
```

#### 2. **Learning Sessions Table**
Tracks individual learning sessions (chat, quiz, games).
```sql
- id (Primary Key)
- user_id (Foreign Key)
- session_type (chat/quiz/game)
- topic
- difficulty
- score
- duration_minutes
- questions_answered
- correct_answers
- session_data (JSON)
- created_at
```

#### 3. **Quiz Results Table**
Stores detailed quiz performance data.
```sql
- id (Primary Key)
- user_id (Foreign Key)
- session_id
- topic
- difficulty
- total_questions
- correct_answers
- score_percentage
- time_taken_seconds
- weak_areas (JSON array)
- strong_areas (JSON array)
- quiz_data (JSON)
- created_at
```

#### 4. **Chat History Table**
Preserves all chat conversations with the AI tutor.
```sql
- id (Primary Key)
- user_id (Foreign Key)
- session_id
- message_type (user/assistant)
- content (Text)
- topic
- difficulty
- adaptive_info (JSON)
- images (JSON array)
- learning_resources (JSON array)
- created_at
```

#### 5. **Game Scores Table**
Records game performance and achievements.
```sql
- id (Primary Key)
- user_id (Foreign Key)
- game_type
- topic
- score
- level
- time_taken_seconds
- game_data (JSON)
- created_at
```

#### 6. **User Progress Table**
Tracks learning progress by topic using advanced algorithms.
```sql
- id (Primary Key)
- user_id (Foreign Key)
- topic
- mastery_level (0-100)
- learning_velocity
- last_interaction
- total_interactions
- average_performance
- difficulty_progression (JSON array)
- created_at, updated_at
```

## 🚀 Features

### ✅ **Implemented Features**

1. **User Authentication**
   - Secure user registration and login
   - JWT token-based authentication
   - Password hashing (SHA256)
   - User profile management

2. **Data Persistence**
   - All user data stored in SQLite database
   - Automatic database initialization
   - Migration-ready schema design

3. **Learning Analytics**
   - Comprehensive user analytics
   - Progress tracking by topic
   - Performance metrics and trends
   - Leaderboard system

4. **Chat History**
   - Complete conversation history
   - Adaptive learning information stored
   - Images and resources preserved

5. **Quiz System Integration**
   - Detailed quiz results storage
   - Performance analysis
   - Weak/strong area identification

6. **Game Progress Tracking**
   - High scores and achievements
   - Game-specific statistics
   - Progress over time

## 🛠️ Database Operations

### **DatabaseService Class**
The `DatabaseService` class provides all database operations:

```python
# User Management
create_user(user_data)
get_user_by_email(email)
get_user_by_id(user_id)
update_user_profile(user_id, updates)

# Learning Sessions
create_learning_session(user_id, session_type, topic, difficulty)
update_session_stats(session_id, score, duration, questions, correct)

# Quiz Results
save_quiz_result(user_id, quiz_data)

# Chat History
save_chat_message(user_id, message_type, content, ...)
get_chat_history(user_id, limit)

# Game Scores
save_game_score(user_id, game_type, score, ...)
get_user_best_scores(user_id, game_type)

# Progress Tracking
update_user_progress(user_id, topic, performance, difficulty)
get_user_progress(user_id)

# Analytics
get_user_analytics(user_id)
get_leaderboard(metric, limit)
```

## 📱 Frontend Integration

### **Database Viewer Component**
- View all registered users
- Personal learning analytics
- Leaderboard display
- Real-time database statistics

### **User Profile Enhancement**
- Persistent user data
- Learning progress visualization
- Historical performance tracking

## 🔧 Setup and Initialization

### **Automatic Database Setup**
The database is automatically initialized when the backend starts:

```python
# In auth.py
init_db()  # Creates all tables
```

### **Manual Database Initialization**
You can also run the initialization script:

```bash
cd backend
python init_database.py
```

This creates:
- All database tables
- Demo user account
- Sample learning data

## 📈 Analytics and Insights

### **User Analytics Include:**
- Profile summary (sessions, average score, difficulty preference)
- Quiz performance (total quizzes, questions answered, best scores)
- Game statistics (favorite games, best scores)
- Learning progress by topic (mastery levels, interactions)
- Activity summary (session types, last activity)

### **Leaderboard Metrics:**
- Average quiz scores
- Total questions answered
- Learning consistency
- Topic mastery

## 🔒 Security Features

1. **Password Security**
   - SHA256 password hashing
   - No plain text password storage

2. **JWT Authentication**
   - Secure token-based authentication
   - 30-day token expiration
   - Automatic token validation

3. **Data Privacy**
   - User data isolation
   - Secure API endpoints
   - Input validation and sanitization

## 🎯 Demo Account

**Login Credentials:**
- Email: `demo@example.com`
- Password: `password123`

The demo account includes sample data for testing all features.

## 📊 Database File Location

The SQLite database file is created at:
```
backend/ai_studybot.db
```

## 🔄 Migration and Backup

### **Database Backup**
```bash
# Copy the database file
cp backend/ai_studybot.db backup/ai_studybot_backup_$(date +%Y%m%d).db
```

### **Database Reset**
```bash
# Delete the database file to reset
rm backend/ai_studybot.db
# Restart the server to recreate tables
```

## 🚀 Production Considerations

For production deployment:

1. **Use PostgreSQL or MySQL** instead of SQLite
2. **Implement proper password hashing** (bcrypt)
3. **Add database connection pooling**
4. **Set up automated backups**
5. **Implement database migrations**
6. **Add data validation and constraints**
7. **Set up monitoring and logging**

## 📝 API Endpoints

### **Authentication**
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user
- `GET /api/auth/users` - List all users (admin)
- `GET /api/auth/analytics/{user_id}` - User analytics
- `GET /api/auth/leaderboard` - Get leaderboard

### **Enhanced Endpoints**
- `GET /api/chat/history/{user_id}` - Chat history
- `POST /api/quiz/complete` - Complete quiz with results
- All existing endpoints now store data persistently

## 🎉 Benefits

1. **Data Persistence** - No data loss on server restart
2. **User Profiles** - Personalized learning experiences
3. **Progress Tracking** - Detailed learning analytics
4. **Performance Insights** - Identify strengths and weaknesses
5. **Scalability** - Ready for production deployment
6. **Security** - Proper authentication and data protection

The database system transforms AI StudyBot from a stateless chatbot into a comprehensive learning management system with persistent user profiles and detailed analytics.