from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import chat, quiz, progress, games

app = FastAPI(title="AI Learning Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(quiz.router, prefix="/api/quiz", tags=["quiz"])
app.include_router(progress.router, prefix="/api/progress", tags=["progress"])
app.include_router(games.router, prefix="/api/games", tags=["games"])

@app.get("/")
def root():
    return {"message": "AI Learning Chatbot API"}
