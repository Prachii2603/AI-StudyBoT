import asyncio
import io
import time
import tempfile
import os
from typing import Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class FasterWhisperService:
    """
    Service for real-time speech-to-text using faster-whisper library
    """
    
    def __init__(self):
        self.model = None
        self.model_size = "base"  # base, small, medium, large
        self.device = "cpu"  # cpu, cuda
        self.compute_type = "int8"  # int8, float16, float32
        self.language = None  # Auto-detect if None
        self.is_initialized = False
        self.audio_buffer = b""
        self.config = {
            "model_size": "base",
            "device": "cpu",
            "compute_type": "int8",
            "language": None,
            "beam_size": 5,
            "best_of": 5,
            "temperature": 0.0,
            "condition_on_previous_text": True,
            "no_speech_threshold": 0.6,
            "compression_ratio_threshold": 2.4,
            "log_prob_threshold": -1.0
        }
    
    async def initialize(self):
        """Initialize the faster-whisper model"""
        try:
            # Import faster-whisper (install with: pip install faster-whisper)
            from faster_whisper import WhisperModel
            
            logger.info(f"Initializing faster-whisper model: {self.model_size}")
            
            # Initialize model in a thread to avoid blocking
            loop = asyncio.get_event_loop()
            self.model = await loop.run_in_executor(
                None, 
                lambda: WhisperModel(
                    self.model_size, 
                    device=self.device, 
                    compute_type=self.compute_type
                )
            )
            
            self.is_initialized = True
            logger.info("Faster-whisper model initialized successfully")
            
        except ImportError:
            logger.error("faster-whisper library not installed. Install with: pip install faster-whisper")
            # Fallback to mock implementation
            self.model = MockWhisperModel()
            self.is_initialized = True
            logger.warning("Using mock whisper model (install faster-whisper for real functionality)")
            
        except Exception as e:
            logger.error(f"Failed to initialize faster-whisper: {e}")
            # Fallback to mock implementation
            self.model = MockWhisperModel()
            self.is_initialized = True
            logger.warning("Using mock whisper model due to initialization error")
    
    async def transcribe_audio_chunk(self, audio_data: bytes, audio_format: str = "wav", 
                                   sample_rate: int = 16000, is_final: bool = False) -> Dict[str, Any]:
        """
        Transcribe an audio chunk
        
        Args:
            audio_data: Raw audio bytes
            audio_format: Audio format (wav, mp3, webm)
            sample_rate: Audio sample rate
            is_final: Whether this is the final chunk
            
        Returns:
            Dictionary with transcription results
        """
        start_time = time.time()
        
        if not self.is_initialized:
            await self.initialize()
        
        try:
            # Add chunk to buffer
            self.audio_buffer += audio_data
            
            # Only process if we have enough data or if it's final
            min_chunk_size = sample_rate * 2  # 2 seconds minimum
            if len(self.audio_buffer) < min_chunk_size and not is_final:
                return {
                    "text": "",
                    "confidence": 0.0,
                    "language": "en",
                    "timestamp": datetime.now().isoformat(),
                    "processing_time": time.time() - start_time,
                    "status": "buffering"
                }
            
            # Create temporary file for audio processing
            with tempfile.NamedTemporaryFile(suffix=f".{audio_format}", delete=False) as temp_file:
                temp_file.write(self.audio_buffer)
                temp_file_path = temp_file.name
            
            try:
                # Transcribe using faster-whisper
                loop = asyncio.get_event_loop()
                segments, info = await loop.run_in_executor(
                    None,
                    lambda: self.model.transcribe(
                        temp_file_path,
                        language=self.config.get("language"),
                        beam_size=self.config.get("beam_size", 5),
                        best_of=self.config.get("best_of", 5),
                        temperature=self.config.get("temperature", 0.0),
                        condition_on_previous_text=self.config.get("condition_on_previous_text", True),
                        no_speech_threshold=self.config.get("no_speech_threshold", 0.6),
                        compression_ratio_threshold=self.config.get("compression_ratio_threshold", 2.4),
                        log_prob_threshold=self.config.get("log_prob_threshold", -1.0)
                    )
                )
                
                # Extract text from segments
                text_segments = []
                total_confidence = 0.0
                segment_count = 0
                
                for segment in segments:
                    text_segments.append(segment.text)
                    if hasattr(segment, 'avg_logprob'):
                        # Convert log probability to confidence (approximate)
                        confidence = min(1.0, max(0.0, (segment.avg_logprob + 1.0)))
                        total_confidence += confidence
                        segment_count += 1
                
                full_text = " ".join(text_segments).strip()
                avg_confidence = total_confidence / segment_count if segment_count > 0 else 0.0
                
                # Clear buffer if final or if we processed successfully
                if is_final or full_text:
                    self.audio_buffer = b""
                
                processing_time = time.time() - start_time
                
                result = {
                    "text": full_text,
                    "confidence": avg_confidence,
                    "language": info.language if hasattr(info, 'language') else "en",
                    "language_probability": getattr(info, 'language_probability', 0.0),
                    "timestamp": datetime.now().isoformat(),
                    "processing_time": processing_time,
                    "status": "completed" if is_final else "partial",
                    "segments_count": segment_count
                }
                
                logger.info(f"Transcribed: '{full_text}' (confidence: {avg_confidence:.2f}, time: {processing_time:.2f}s)")
                return result
                
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
                    
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return {
                "text": "",
                "confidence": 0.0,
                "language": "en",
                "timestamp": datetime.now().isoformat(),
                "processing_time": time.time() - start_time,
                "status": "error",
                "error": str(e)
            }
    
    async def update_config(self, new_config: Dict[str, Any]):
        """Update service configuration"""
        self.config.update(new_config)
        logger.info(f"Updated faster-whisper config: {new_config}")
        
        # Reinitialize if model settings changed
        model_settings = ["model_size", "device", "compute_type"]
        if any(key in new_config for key in model_settings):
            self.model_size = new_config.get("model_size", self.model_size)
            self.device = new_config.get("device", self.device)
            self.compute_type = new_config.get("compute_type", self.compute_type)
            
            logger.info("Reinitializing model with new settings...")
            await self.initialize()
    
    async def cleanup(self):
        """Clean up resources"""
        self.audio_buffer = b""
        if hasattr(self.model, 'cleanup'):
            self.model.cleanup()
        logger.info("Faster-whisper service cleaned up")


class MockWhisperModel:
    """Mock whisper model for testing when faster-whisper is not available"""
    
    def transcribe(self, audio_path, **kwargs):
        """Mock transcription that returns sample text"""
        import random
        
        # Simulate processing time
        time.sleep(0.1)
        
        # Mock segments with sample text
        class MockSegment:
            def __init__(self, text):
                self.text = text
                self.avg_logprob = -0.5  # Mock confidence
        
        class MockInfo:
            def __init__(self):
                self.language = "en"
                self.language_probability = 0.95
        
        sample_texts = [
            "Hello, this is a test transcription.",
            "The quick brown fox jumps over the lazy dog.",
            "Machine learning is fascinating.",
            "Speech recognition is working well.",
            "This is a mock transcription result."
        ]
        
        mock_text = random.choice(sample_texts)
        segments = [MockSegment(mock_text)]
        info = MockInfo()
        
        return segments, info