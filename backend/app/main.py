from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import chat, quiz, progress, games, onboarding, websocket, auth

app = FastAPI(title="AI Learning Chatbot API - Enhanced")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(quiz.router, prefix="/api/quiz", tags=["quiz"])
app.include_router(progress.router, prefix="/api/progress", tags=["progress"])
app.include_router(games.router, prefix="/api/games", tags=["games"])
app.include_router(onboarding.router, prefix="/api/onboarding", tags=["onboarding"])
app.include_router(websocket.router, prefix="/ws", tags=["websocket"])

@app.get("/")
def root():
    return {"message": "AI Learning Platform API - Enhanced with Advanced Features", "status": "online"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "version": "2.0.0"}

@app.get("/api/health")
def api_health_check():
    return {"status": "healthy", "timestamp": "2026-03-10T14:00:00Z"}
