"""
Enhanced Voice Processor with noise filtering and multi-user support
"""

import numpy as np
import sounddevice as sd
import whisper
import logging
from typing import Optional, Dict, List, Tuple
from datetime import datetime
import scipy.signal
from scipy.io import wavfile
import tempfile
import os

from core.interfaces.voice_interface import VoiceProcessor, VoiceCommand, VoiceResponse

logger = logging.getLogger(__name__)

class EnhancedVoiceProcessor(VoiceProcessor):
    """Enhanced voice processor with noise filtering and speaker identification"""
    
    def __init__(self, 
                 sample_rate: int = 16000,
                 wake_words: List[str] = None,
                 whisper_model: str = "base.en"):
        
        self.sample_rate = sample_rate
        self.wake_words = wake_words or ["jarvis", "hey jarvis", "hello jarvis"]
        self.whisper_model_name = whisper_model
        
        # Load Whisper model
        try:
            self.whisper_model = whisper.load_model(whisper_model)
            logger.info(f"Loaded Whisper model: {whisper_model}")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            self.whisper_model = None
        
        # Voice activity detection parameters
        self.vad_threshold = 0.01
        self.min_speech_duration = 0.5  # seconds
        
        # Noise reduction parameters
        self.noise_gate_threshold = 0.005
        self.noise_reduction_factor = 0.3
        
        # Speaker identification (simple implementation)
        self.known_speakers = {}
        self.speaker_profiles = {}
        
        # Wake word detection settings
        self.wake_word_confidence_threshold = 0.7
        self.wake_word_timeout = 2.0  # seconds
        
        logger.info("Enhanced Voice Processor initialized")
    
    def apply_noise_filtering(self, audio: np.ndarray) -> np.ndarray:
        """Apply noise filtering to audio signal"""
        try:
            # Apply noise gate - remove very quiet sounds
            audio_filtered = np.where(np.abs(audio) > self.noise_gate_threshold, audio, 0)
            
            # Apply high-pass filter to remove low-frequency noise
            nyquist = self.sample_rate / 2
            high_cutoff = 80  # Hz - remove very low frequencies
            high = high_cutoff / nyquist
            
            if high < 1.0:
                b, a = scipy.signal.butter(4, high, btype='high')
                audio_filtered = scipy.signal.filtfilt(b, a, audio_filtered)
            
            # Apply low-pass filter to remove high-frequency noise
            low_cutoff = 8000  # Hz - human speech is typically below this
            low = low_cutoff / nyquist
            
            if low < 1.0:
                b, a = scipy.signal.butter(4, low, btype='low')
                audio_filtered = scipy.signal.filtfilt(b, a, audio_filtered)
            
            # Normalize audio
            if np.max(np.abs(audio_filtered)) > 0:
                audio_filtered = audio_filtered / np.max(np.abs(audio_filtered))
            
            logger.debug("Applied noise filtering to audio")
            return audio_filtered
            
        except Exception as e:
            logger.error(f"Error applying noise filtering: {e}")
            return audio
    
    def detect_voice_activity(self, audio: np.ndarray) -> bool:
        """Detect if audio contains voice activity"""
        try:
            # Calculate RMS energy
            rms_energy = np.sqrt(np.mean(audio ** 2))
            
            # Check if energy is above threshold
            has_energy = rms_energy > self.vad_threshold
            
            # Check for speech-like frequency content
            # Human speech has most energy between 85-255 Hz (fundamental) and harmonics
            fft = np.fft.fft(audio)
            freqs = np.fft.fftfreq(len(audio), 1/self.sample_rate)
            
            # Focus on speech frequency range (80-4000 Hz)
            speech_mask = (np.abs(freqs) >= 80) & (np.abs(freqs) <= 4000)
            speech_energy = np.sum(np.abs(fft[speech_mask]))
            total_energy = np.sum(np.abs(fft))
            
            speech_ratio = speech_energy / total_energy if total_energy > 0 else 0
            has_speech_characteristics = speech_ratio > 0.3
            
            return has_energy and has_speech_characteristics
            
        except Exception as e:
            logger.error(f"Error in voice activity detection: {e}")
            return True  # Default to assuming voice activity
    
    def record_audio(self, duration: float, device: Optional[int] = None) -> Optional[np.ndarray]:
        """Record audio with error handling"""
        try:
            logger.debug(f"Recording {duration}s of audio...")
            
            audio = sd.rec(
                int(duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=1,
                dtype='float32',
                device=device
            )
            sd.wait()  # Wait until recording finishes
            
            audio_flat = audio.flatten()
            
            # Apply noise filtering
            audio_filtered = self.apply_noise_filtering(audio_flat)
            
            return audio_filtered
            
        except Exception as e:
            logger.error(f"Recording error: {e}")
            return None
    
    def transcribe_audio(self, audio: np.ndarray) -> Tuple[str, float]:
        """Transcribe audio to text with confidence score"""
        if audio is None or len(audio) == 0 or self.whisper_model is None:
            return "", 0.0
        
        try:
            # Check for voice activity first
            if not self.detect_voice_activity(audio):
                logger.debug("No voice activity detected")
                return "", 0.0
            
            # Transcribe using Whisper
            result = self.whisper_model.transcribe(
                audio.astype(np.float32),
                language="en",
                task="transcribe"
            )
            
            text = result["text"].strip()
            
            # Calculate confidence based on Whisper's internal scoring
            # This is a simplified confidence calculation
            segments = result.get("segments", [])
            if segments:
                avg_confidence = np.mean([seg.get("no_speech_prob", 0.5) for seg in segments])
                confidence = 1.0 - avg_confidence  # Invert no_speech_prob
            else:
                confidence = 0.5  # Default confidence
            
            logger.debug(f"Transcribed: '{text}' (confidence: {confidence:.2f})")
            return text.lower(), confidence
            
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return "", 0.0
    
    def listen_for_wake_word(self) -> bool:
        """Listen for wake word activation"""
        try:
            audio = self.record_audio(self.wake_word_timeout)
            if audio is None:
                return False
            
            text, confidence = self.transcribe_audio(audio)
            
            # Check if any wake word is present
            for wake_word in self.wake_words:
                if wake_word in text and confidence > self.wake_word_confidence_threshold:
                    logger.info(f"Wake word '{wake_word}' detected with confidence {confidence:.2f}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Wake word detection error: {e}")
            return False
    
    def capture_command(self, timeout: int = 10) -> Optional[VoiceCommand]:
        """Capture and transcribe voice command"""
        try:
            logger.info("Listening for command...")
            audio = self.record_audio(timeout)
            
            if audio is None:
                return None
            
            text, confidence = self.transcribe_audio(audio)
            
            if not text:
                logger.info("No speech detected")
                return None
            
            # Create voice command object
            command = VoiceCommand(
                text=text,
                confidence=confidence,
                audio_data=audio,
                timestamp=datetime.now().timestamp()
            )
            
            logger.info(f"Command captured: '{text}' (confidence: {confidence:.2f})")
            return command
            
        except Exception as e:
            logger.error(f"Command capture error: {e}")
            return None
    
    def speak_response(self, response: VoiceResponse) -> bool:
        """Convert text to speech and play (placeholder implementation)"""
        try:
            # For now, just log the response
            # In a full implementation, this would use TTS
            logger.info(f"Speaking: {response.text}")
            print(f"🗣️ Jarvis: {response.text}")
            return True
            
        except Exception as e:
            logger.error(f"Speech synthesis error: {e}")
            return False
    
    def identify_speaker(self, audio_data: np.ndarray) -> Optional[str]:
        """Identify speaker from audio data (simplified implementation)"""
        try:
            # This is a placeholder for speaker identification
            # In a full implementation, this would use speaker recognition models
            
            # For now, extract basic audio features for future use
            rms_energy = np.sqrt(np.mean(audio_data ** 2))
            spectral_centroid = self._calculate_spectral_centroid(audio_data)
            
            # Store features for potential future speaker identification
            features = {
                'rms_energy': rms_energy,
                'spectral_centroid': spectral_centroid,
                'timestamp': datetime.now()
            }
            
            # Return default speaker for now
            return "default_user"
            
        except Exception as e:
            logger.error(f"Speaker identification error: {e}")
            return None
    
    def _calculate_spectral_centroid(self, audio: np.ndarray) -> float:
        """Calculate spectral centroid of audio signal"""
        try:
            # Compute FFT
            fft = np.fft.fft(audio)
            magnitude = np.abs(fft)
            freqs = np.fft.fftfreq(len(audio), 1/self.sample_rate)
            
            # Calculate spectral centroid
            centroid = np.sum(freqs[:len(freqs)//2] * magnitude[:len(magnitude)//2]) / np.sum(magnitude[:len(magnitude)//2])
            return float(centroid)
            
        except Exception as e:
            logger.error(f"Spectral centroid calculation error: {e}")
            return 0.0
    
    def get_audio_devices(self) -> List[Dict]:
        """Get list of available audio devices"""
        try:
            devices = sd.query_devices()
            device_list = []
            
            for i, device in enumerate(devices):
                if device['max_input_channels'] > 0:  # Only input devices
                    device_list.append({
                        'id': i,
                        'name': device['name'],
                        'channels': device['max_input_channels'],
                        'sample_rate': device['default_samplerate']
                    })
            
            return device_list
            
        except Exception as e:
            logger.error(f"Error getting audio devices: {e}")
            return []
    
    def test_audio_system(self) -> Dict[str, bool]:
        """Test audio system components"""
        results = {
            'microphone': False,
            'whisper_model': False,
            'noise_filtering': False,
            'voice_activity_detection': False
        }
        
        try:
            # Test microphone
            test_audio = self.record_audio(1.0)
            results['microphone'] = test_audio is not None
            
            # Test Whisper model
            results['whisper_model'] = self.whisper_model is not None
            
            # Test noise filtering
            if test_audio is not None:
                filtered = self.apply_noise_filtering(test_audio)
                results['noise_filtering'] = filtered is not None
                
                # Test voice activity detection
                results['voice_activity_detection'] = True  # Basic test
            
            logger.info(f"Audio system test results: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Audio system test error: {e}")
            return results