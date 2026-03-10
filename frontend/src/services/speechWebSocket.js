/**
 * WebSocket client for real-time speech-to-text
 * Usage example for the faster-whisper WebSocket endpoint
 */

class SpeechWebSocketClient {
  constructor(userId = null) {
    this.userId = userId || `user_${Date.now()}`;
    this.websocket = null;
    this.isConnected = false;
    this.isRecording = false;
    this.mediaRecorder = null;
    this.audioChunks = [];
    this.onTranscription = null;
    this.onError = null;
    this.onStatusChange = null;
  }

  /**
   * Connect to the WebSocket endpoint
   */
  async connect() {
    try {
      const wsUrl = `ws://localhost:8000/ws/speech-to-text/${this.userId}`;
      this.websocket = new WebSocket(wsUrl);

      this.websocket.onopen = () => {
        this.isConnected = true;
        console.log('WebSocket connected for speech-to-text');
        if (this.onStatusChange) {
          this.onStatusChange('connected');
        }
      };

      this.websocket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.handleMessage(data);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      this.websocket.onclose = () => {
        this.isConnected = false;
        console.log('WebSocket disconnected');
        if (this.onStatusChange) {
          this.onStatusChange('disconnected');
        }
      };

      this.websocket.onerror = (error) => {
        console.error('WebSocket error:', error);
        if (this.onError) {
          this.onError(error);
        }
      };

    } catch (error) {
      console.error('Failed to connect WebSocket:', error);
      if (this.onError) {
        this.onError(error);
      }
    }
  }

  /**
   * Handle incoming WebSocket messages
   */
  handleMessage(data) {
    switch (data.type) {
      case 'connection_status':
        console.log('Connection status:', data.message);
        break;
      
      case 'transcription':
        if (this.onTranscription) {
          this.onTranscription({
            text: data.text,
            isPartial: data.is_partial,
            confidence: data.confidence,
            language: data.language,
            timestamp: data.timestamp,
            processingTime: data.processing_time
          });
        }
        break;
      
      case 'error':
        console.error('WebSocket error:', data.message);
        if (this.onError) {
          this.onError(new Error(data.message));
        }
        break;
      
      case 'pong':
        console.log('Received pong');
        break;
      
      default:
        console.log('Unknown message type:', data.type);
    }
  }

  /**
   * Start recording audio
   */
  async startRecording() {
    if (!this.isConnected) {
      throw new Error('WebSocket not connected');
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          sampleRate: 16000,
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true
        } 
      });

      this.mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      });

      this.audioChunks = [];

      this.mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          this.audioChunks.push(event.data);
          this.sendAudioChunk(event.data, false);
        }
      };

      this.mediaRecorder.onstop = () => {
        // Send final chunk
        if (this.audioChunks.length > 0) {
          const finalBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
          this.sendAudioChunk(finalBlob, true);
        }
        
        // Stop all tracks
        stream.getTracks().forEach(track => track.stop());
      };

      this.mediaRecorder.start(1000); // Collect data every 1 second
      this.isRecording = true;
      
      if (this.onStatusChange) {
        this.onStatusChange('recording');
      }

    } catch (error) {
      console.error('Failed to start recording:', error);
      if (this.onError) {
        this.onError(error);
      }
    }
  }

  /**
   * Stop recording audio
   */
  stopRecording() {
    if (this.mediaRecorder && this.isRecording) {
      this.mediaRecorder.stop();
      this.isRecording = false;
      
      if (this.onStatusChange) {
        this.onStatusChange('stopped');
      }
    }
  }

  /**
   * Send audio chunk to WebSocket
   */
  async sendAudioChunk(audioBlob, isFinal = false) {
    if (!this.isConnected || !this.websocket) {
      return;
    }

    try {
      // Convert blob to base64
      const arrayBuffer = await audioBlob.arrayBuffer();
      const base64Audio = btoa(String.fromCharCode(...new Uint8Array(arrayBuffer)));

      const message = {
        type: 'audio_chunk',
        data: base64Audio,
        format: 'webm',
        sample_rate: 16000,
        is_final: isFinal
      };

      this.websocket.send(JSON.stringify(message));
    } catch (error) {
      console.error('Failed to send audio chunk:', error);
      if (this.onError) {
        this.onError(error);
      }
    }
  }

  /**
   * Send ping to keep connection alive
   */
  ping() {
    if (this.isConnected && this.websocket) {
      this.websocket.send(JSON.stringify({
        type: 'ping',
        timestamp: new Date().toISOString()
      }));
    }
  }

  /**
   * Configure whisper settings
   */
  configure(config) {
    if (this.isConnected && this.websocket) {
      this.websocket.send(JSON.stringify({
        type: 'configure',
        config: config
      }));
    }
  }

  /**
   * Disconnect WebSocket
   */
  disconnect() {
    if (this.isRecording) {
      this.stopRecording();
    }
    
    if (this.websocket) {
      this.websocket.close();
      this.websocket = null;
    }
    
    this.isConnected = false;
  }

  /**
   * Set event handlers
   */
  setEventHandlers({ onTranscription, onError, onStatusChange }) {
    this.onTranscription = onTranscription;
    this.onError = onError;
    this.onStatusChange = onStatusChange;
  }
}

export default SpeechWebSocketClient;

/**
 * Usage Example:
 * 
 * const speechClient = new SpeechWebSocketClient('user123');
 * 
 * speechClient.setEventHandlers({
 *   onTranscription: (result) => {
 *     console.log('Transcription:', result.text);
 *     console.log('Confidence:', result.confidence);
 *   },
 *   onError: (error) => {
 *     console.error('Speech error:', error);
 *   },
 *   onStatusChange: (status) => {
 *     console.log('Status:', status);
 *   }
 * });
 * 
 * await speechClient.connect();
 * await speechClient.startRecording();
 * 
 * // Later...
 * speechClient.stopRecording();
 * speechClient.disconnect();
 */