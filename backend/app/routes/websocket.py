from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState
import json
import base64
import io
import asyncio
from typing import Dict, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Store active WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.user_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: str = None):
        await websocket.accept()
        self.active_connections.append(websocket)
        if user_id:
            self.user_connections[user_id] = websocket
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket, user_id: str = None):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if user_id and user_id in self.user_connections:
            del self.user_connections[user_id]
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        if websocket.client_state == WebSocketState.CONNECTED:
            await websocket.send_text(message)

    async def send_to_user(self, message: str, user_id: str):
        if user_id in self.user_connections:
            websocket = self.user_connections[user_id]
            if websocket.client_state == WebSocketState.CONNECTED:
                await websocket.send_text(message)

manager = ConnectionManager()

@router.websocket("/speech-to-text/{user_id}")
async def websocket_speech_to_text(websocket: WebSocket, user_id: str):
    """
    WebSocket endpoint for real-time speech-to-text conversion
    
    Expected message format:
    {
        "type": "audio_chunk",
        "data": "base64_encoded_audio_data",
        "format": "wav|mp3|webm",
        "sample_rate": 16000,
        "is_final": false
    }
    
    Response format:
    {
        "type": "transcription",
        "text": "transcribed text",
        "is_partial": false,
        "confidence": 0.95,
        "timestamp": "2024-01-01T12:00:00Z"
    }
    """
    
    await manager.connect(websocket, user_id)
    
    # Initialize faster-whisper model (lazy loading)
    whisper_service = None
    
    try:
        # Import and initialize faster-whisper service
        from app.services.faster_whisper_service import FasterWhisperService
        whisper_service = FasterWhisperService()
        await whisper_service.initialize()
        
        # Send connection confirmation
        await manager.send_personal_message(json.dumps({
            "type": "connection_status",
            "status": "connected",
            "message": "Speech-to-text service ready",
            "user_id": user_id
        }), websocket)
        
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                message_type = message.get("type")
                
                if message_type == "audio_chunk":
                    # Process audio chunk
                    audio_data = message.get("data")
                    audio_format = message.get("format", "wav")
                    sample_rate = message.get("sample_rate", 16000)
                    is_final = message.get("is_final", False)
                    
                    if audio_data:
                        # Decode base64 audio data
                        try:
                            audio_bytes = base64.b64decode(audio_data)
                            
                            # Process with faster-whisper
                            result = await whisper_service.transcribe_audio_chunk(
                                audio_bytes, 
                                audio_format, 
                                sample_rate,
                                is_final
                            )
                            
                            # Send transcription result
                            response = {
                                "type": "transcription",
                                "text": result.get("text", ""),
                                "is_partial": not is_final,
                                "confidence": result.get("confidence", 0.0),
                                "language": result.get("language", "en"),
                                "timestamp": result.get("timestamp"),
                                "processing_time": result.get("processing_time", 0.0)
                            }
                            
                            await manager.send_personal_message(
                                json.dumps(response), websocket
                            )
                            
                        except Exception as decode_error:
                            logger.error(f"Audio decoding error: {decode_error}")
                            await manager.send_personal_message(json.dumps({
                                "type": "error",
                                "message": "Failed to decode audio data",
                                "error": str(decode_error)
                            }), websocket)
                
                elif message_type == "ping":
                    # Respond to ping with pong
                    await manager.send_personal_message(json.dumps({
                        "type": "pong",
                        "timestamp": message.get("timestamp")
                    }), websocket)
                
                elif message_type == "configure":
                    # Configure whisper settings
                    config = message.get("config", {})
                    if whisper_service:
                        await whisper_service.update_config(config)
                        await manager.send_personal_message(json.dumps({
                            "type": "config_updated",
                            "config": config
                        }), websocket)
                
                else:
                    # Unknown message type
                    await manager.send_personal_message(json.dumps({
                        "type": "error",
                        "message": f"Unknown message type: {message_type}"
                    }), websocket)
                    
            except json.JSONDecodeError:
                await manager.send_personal_message(json.dumps({
                    "type": "error",
                    "message": "Invalid JSON format"
                }), websocket)
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                await manager.send_personal_message(json.dumps({
                    "type": "error",
                    "message": "Error processing message",
                    "error": str(e)
                }), websocket)
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for user: {user_id}")
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
        try:
            await manager.send_personal_message(json.dumps({
                "type": "error",
                "message": "WebSocket connection error",
                "error": str(e)
            }), websocket)
        except:
            pass
    finally:
        manager.disconnect(websocket, user_id)
        if whisper_service:
            await whisper_service.cleanup()

@router.websocket("/speech-to-text")
async def websocket_speech_to_text_anonymous(websocket: WebSocket):
    """Anonymous WebSocket endpoint for speech-to-text (no user tracking)"""
    import uuid
    anonymous_id = f"anonymous_{uuid.uuid4().hex[:8]}"
    await websocket_speech_to_text(websocket, anonymous_id)