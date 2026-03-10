from fastapi import APIRouter, HTTPException
from app.services.games_service import games_service
from typing import List, Dict, Any
from pydantic import BaseModel

router = APIRouter()

class GameStartRequest(BaseModel):
    topic: str
    student_id: str

class WordMatchRequest(BaseModel):
    game_id: str
    term: str
    definition: str

class QuizAnswerRequest(BaseModel):
    game_id: str
    answer: int

class CardFlipRequest(BaseModel):
    game_id: str
    card_id: str

@router.get("/available")
async def get_available_games():
    """Get list of available educational games"""
    try:
        return games_service.get_available_games()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/word-match/start")
async def start_word_match(request: GameStartRequest):
    """Start a word matching game"""
    try:
        return games_service.start_word_match_game(request.topic, request.student_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/word-match/match")
async def make_word_match(request: WordMatchRequest):
    """Make a word match attempt"""
    try:
        return games_service.make_word_match(request.game_id, request.term, request.definition)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/lightning-quiz/start")
async def start_lightning_quiz(request: GameStartRequest):
    """Start a lightning quiz game"""
    try:
        return games_service.start_lightning_quiz(request.topic, request.student_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/lightning-quiz/answer")
async def answer_lightning_question(request: QuizAnswerRequest):
    """Answer a lightning quiz question"""
    try:
        return games_service.answer_lightning_question(request.game_id, request.answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/memory-cards/start")
async def start_memory_cards(request: GameStartRequest):
    """Start a memory cards game"""
    try:
        return games_service.start_memory_cards_game(request.topic, request.student_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/memory-cards/flip")
async def flip_memory_card(request: CardFlipRequest):
    """Flip a memory card"""
    try:
        return games_service.flip_memory_card(request.game_id, request.card_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/leaderboard/{game_type}")
async def get_game_leaderboard(game_type: str):
    """Get leaderboard for a specific game type"""
    try:
        return games_service.get_game_leaderboard(game_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))