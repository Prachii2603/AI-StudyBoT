from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from typing import Optional, List
import jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from app.database import get_db, User, init_db
from app.services.database_service import DatabaseService

load_dotenv()

router = APIRouter()
security = HTTPBearer()

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60  # 30 days

# Initialize database on startup
init_db()

# Pydantic Models
class UserRegistration(BaseModel):
    name: str
    email: EmailStr
    password: str
    age: Optional[int] = None
    grade: Optional[str] = None
    interests: List[str] = []

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    age: Optional[int]
    grade: Optional[str]
    interests: List[str]
    created_at: str
    learning_profile: dict

class AuthResponse(BaseModel):
    success: bool
    message: str
    user: Optional[UserResponse] = None
    token: Optional[str] = None

# Helper Functions
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), 
                    db: Session = Depends(get_db)):
    """Get current user from JWT token"""
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        
        db_service = DatabaseService(db)
        user = db_service.get_user_by_email(email)
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        
        return user
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

def user_to_response(user: User) -> UserResponse:
    """Convert User model to UserResponse"""
    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        age=user.age,
        grade=user.grade,
        interests=user.interests or [],
        created_at=user.created_at.isoformat(),
        learning_profile={
            "total_sessions": user.total_sessions,
            "total_questions_answered": user.total_questions_answered,
            "average_score": user.average_score,
            "preferred_difficulty": user.preferred_difficulty,
            "learning_style": user.learning_style
        }
    )

# Routes
@router.post("/register", response_model=AuthResponse)
async def register_user(user_data: UserRegistration, db: Session = Depends(get_db)):
    """Register a new user"""
    try:
        db_service = DatabaseService(db)
        
        # Check if user already exists
        existing_user = db_service.get_user_by_email(user_data.email)
        if existing_user:
            return AuthResponse(
                success=False,
                message="User with this email already exists"
            )
        
        # Validate password
        if len(user_data.password) < 6:
            return AuthResponse(
                success=False,
                message="Password must be at least 6 characters long"
            )
        
        # Create new user
        new_user = db_service.create_user({
            "name": user_data.name,
            "email": user_data.email,
            "password": user_data.password,
            "age": user_data.age,
            "grade": user_data.grade,
            "interests": user_data.interests
        })
        
        # Create access token
        access_token = create_access_token(data={"sub": user_data.email})
        
        return AuthResponse(
            success=True,
            message="User registered successfully",
            user=user_to_response(new_user),
            token=access_token
        )
        
    except Exception as e:
        return AuthResponse(
            success=False,
            message=f"Registration failed: {str(e)}"
        )

@router.post("/login", response_model=AuthResponse)
async def login_user(login_data: UserLogin, db: Session = Depends(get_db)):
    """Login user"""
    try:
        db_service = DatabaseService(db)
        
        # Check if user exists
        user = db_service.get_user_by_email(login_data.email)
        if not user:
            return AuthResponse(
                success=False,
                message="Invalid email or password"
            )
        
        # Verify password
        if not db_service.verify_password(login_data.password, user.password_hash):
            return AuthResponse(
                success=False,
                message="Invalid email or password"
            )
        
        # Create access token
        access_token = create_access_token(data={"sub": login_data.email})
        
        return AuthResponse(
            success=True,
            message="Login successful",
            user=user_to_response(user),
            token=access_token
        )
        
    except Exception as e:
        return AuthResponse(
            success=False,
            message=f"Login failed: {str(e)}"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile"""
    return user_to_response(current_user)

@router.post("/logout")
async def logout_user():
    """Logout user (client-side token removal)"""
    return {"success": True, "message": "Logged out successfully"}

@router.get("/users")
async def get_all_users(db: Session = Depends(get_db)):
    """Get all users (for development/admin purposes)"""
    users = db.query(User).all()
    return {
        "users": [
            {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "grade": user.grade,
                "interests": user.interests,
                "created_at": user.created_at.isoformat(),
                "total_sessions": user.total_sessions
            }
            for user in users
        ],
        "total": len(users)
    }

@router.get("/analytics/{user_id}")
async def get_user_analytics(user_id: str, db: Session = Depends(get_db)):
    """Get comprehensive user analytics"""
    db_service = DatabaseService(db)
    analytics = db_service.get_user_analytics(user_id)
    return analytics

@router.get("/leaderboard")
async def get_leaderboard(metric: str = "average_score", limit: int = 10, db: Session = Depends(get_db)):
    """Get leaderboard"""
    db_service = DatabaseService(db)
    leaderboard = db_service.get_leaderboard(metric, limit)
    return {"leaderboard": leaderboard, "metric": metric}