import os
import io
import base64
from typing import Optional, Dict, Any
import openai
from openai import OpenAI
import requests
from pydantic import BaseModel

class VoiceProcessingService:
    """
    Voice processing service for speech-to-text and text-to-speech
    """
    
    def __init__(self):
        self.openai_client = None
        self.elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
        
        # Initialize OpenAI client if API key is available
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            self.openai_client = OpenAI(api_key=openai_key)
    
    async def speech_to_text(self, audio_data: bytes, 
                           audio_format: str = "wav") -> Dict[str, Any]:
        """
        Convert speech to text using OpenAI Whisper
        
        Args:
            audio_data: Raw audio bytes
            audio_format: Audio format (wav, mp3, etc.)
            
        Returns:
            Dictionary with transcription and metadata
        """
        try:
            if not self.openai_client:
                return {
                    "success": False,
                    "error": "OpenAI API key not configured",
                    "text": ""
                }
            
            # Create audio file-like object
            audio_file = io.BytesIO(audio_data)
            audio_file.name = f"audio.{audio_format}"
            
            # Use Whisper for transcription
            transcript = self.openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="verbose_json"
            )
            
            return {
                "success": True,
                "text": transcript.text,
                "language": getattr(transcript, 'language', 'unknown'),
                "duration": getattr(transcript, 'duration', 0),
                "confidence": self._estimate_confidence(transcript.text)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "text": ""
            }
    
    async def text_to_speech(self, text: str, 
                           voice: str = "alloy",
                           speed: float = 1.0) -> Dict[str, Any]:
        """
        Convert text to speech using OpenAI TTS
        
        Args:
            text: Text to convert to speech
            voice: Voice to use (alloy, echo, fable, onyx, nova, shimmer)
            speed: Speech speed (0.25 to 4.0)
            
        Returns:
            Dictionary with audio data and metadata
        """
        try:
            if not self.openai_client:
                return {
                    "success": False,
                    "error": "OpenAI API key not configured",
                    "audio_data": None
                }
            
            # Generate speech
            response = self.openai_client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=text,
                speed=speed
            )
            
            # Get audio data
            audio_data = response.content
            
            return {
                "success": True,
                "audio_data": base64.b64encode(audio_data).decode('utf-8'),
                "audio_format": "mp3",
                "text_length": len(text),
                "estimated_duration": len(text) / 150 * 60  # Rough estimate
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "audio_data": None
            }
    
    async def text_to_speech_elevenlabs(self, text: str,
                                      voice_id: str = "21m00Tcm4TlvDq8ikWAM") -> Dict[str, Any]:
        """
        Convert text to speech using ElevenLabs API (higher quality)
        
        Args:
            text: Text to convert
            voice_id: ElevenLabs voice ID
            
        Returns:
            Dictionary with audio data and metadata
        """
        try:
            if not self.elevenlabs_api_key:
                return await self.text_to_speech(text)  # Fallback to OpenAI
            
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.elevenlabs_api_key
            }
            
            data = {
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.5
                }
            }
            
            response = requests.post(url, json=data, headers=headers)
            
            if response.status_code == 200:
                audio_data = response.content
                return {
                    "success": True,
                    "audio_data": base64.b64encode(audio_data).decode('utf-8'),
                    "audio_format": "mp3",
                    "text_length": len(text),
                    "provider": "elevenlabs"
                }
            else:
                # Fallback to OpenAI
                return await self.text_to_speech(text)
                
        except Exception as e:
            # Fallback to OpenAI TTS
            return await self.text_to_speech(text)
    
    def detect_language(self, text: str) -> str:
        """
        Detect language of text (simple implementation)
        """
        # Simple language detection based on common words
        # In production, use a proper language detection library
        
        english_indicators = ['the', 'and', 'is', 'in', 'to', 'of', 'a', 'that']
        spanish_indicators = ['el', 'la', 'y', 'es', 'en', 'de', 'un', 'que']
        french_indicators = ['le', 'de', 'et', 'à', 'un', 'il', 'être', 'et']
        
        text_lower = text.lower()
        
        english_count = sum(1 for word in english_indicators if word in text_lower)
        spanish_count = sum(1 for word in spanish_indicators if word in text_lower)
        french_count = sum(1 for word in french_indicators if word in text_lower)
        
        if english_count >= spanish_count and english_count >= french_count:
            return "en"
        elif spanish_count >= french_count:
            return "es"
        elif french_count > 0:
            return "fr"
        else:
            return "en"  # Default to English
    
    def _estimate_confidence(self, text: str) -> float:
        """
        Estimate transcription confidence based on text characteristics
        """
        if not text:
            return 0.0
        
        # Simple heuristics for confidence estimation
        confidence = 0.8  # Base confidence
        
        # Penalize very short transcriptions
        if len(text) < 10:
            confidence -= 0.2
        
        # Penalize transcriptions with many special characters
        special_char_ratio = sum(1 for c in text if not c.isalnum() and c != ' ') / len(text)
        if special_char_ratio > 0.3:
            confidence -= 0.3
        
        # Boost confidence for longer, coherent text
        if len(text) > 50 and text.count(' ') > 5:
            confidence += 0.1
        
        return max(0.0, min(1.0, confidence))

# Global instance
voice_service = VoiceProcessingService()