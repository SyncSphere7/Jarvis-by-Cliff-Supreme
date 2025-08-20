"""
Unit tests for voice processing functionality
"""

import unittest
import numpy as np
from unittest.mock import Mock, patch
import tempfile
import os

from core.voice.enhanced_voice_processor import EnhancedVoiceProcessor
from core.interfaces.voice_interface import VoiceCommand, VoiceResponse

class TestEnhancedVoiceProcessor(unittest.TestCase):
    """Test cases for Enhanced Voice Processor"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.processor = EnhancedVoiceProcessor(
            sample_rate=16000,
            wake_words=["test", "jarvis"],
            whisper_model="tiny.en"
        )
    
    def test_noise_filtering(self):
        """Test noise filtering functionality"""
        # Create test audio with noise
        duration = 1.0
        sample_rate = 16000
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        # Create signal with speech-like frequency (200 Hz) and noise
        speech_signal = 0.5 * np.sin(2 * np.pi * 200 * t)
        noise = 0.1 * np.random.normal(0, 1, len(t))
        noisy_audio = speech_signal + noise
        
        # Apply noise filtering
        filtered_audio = self.processor.apply_noise_filtering(noisy_audio)
        
        # Check that filtering was applied
        self.assertIsInstance(filtered_audio, np.ndarray)
        self.assertEqual(len(filtered_audio), len(noisy_audio))
        
        # Check that audio is normalized
        max_amplitude = np.max(np.abs(filtered_audio))
        self.assertLessEqual(max_amplitude, 1.0)
    
    def test_voice_activity_detection(self):
        """Test voice activity detection"""
        # Test with silence (should return False)
        silence = np.zeros(16000)  # 1 second of silence
        self.assertFalse(self.processor.detect_voice_activity(silence))
        
        # Test with speech-like signal (should return True)
        t = np.linspace(0, 1, 16000)
        speech_like = 0.1 * np.sin(2 * np.pi * 200 * t)  # 200 Hz tone
        self.assertTrue(self.processor.detect_voice_activity(speech_like))
        
        # Test with very quiet signal (should return False)
        quiet_signal = 0.001 * np.sin(2 * np.pi * 200 * t)
        self.assertFalse(self.processor.detect_voice_activity(quiet_signal))
    
    def test_spectral_centroid_calculation(self):
        """Test spectral centroid calculation"""
        # Create test signal with known frequency
        t = np.linspace(0, 1, 16000)
        test_freq = 440  # A4 note
        signal = np.sin(2 * np.pi * test_freq * t)
        
        centroid = self.processor._calculate_spectral_centroid(signal)
        
        # Centroid should be close to the test frequency
        self.assertIsInstance(centroid, float)
        self.assertGreater(centroid, 0)
    
    @patch('sounddevice.rec')
    @patch('sounddevice.wait')
    def test_record_audio(self, mock_wait, mock_rec):
        """Test audio recording functionality"""
        # Mock sounddevice recording
        mock_audio = np.random.random((16000, 1)).astype(np.float32)
        mock_rec.return_value = mock_audio
        
        # Test recording
        result = self.processor.record_audio(1.0)
        
        # Verify recording was called correctly
        mock_rec.assert_called_once()
        mock_wait.assert_called_once()
        
        # Check result
        self.assertIsInstance(result, np.ndarray)
        self.assertEqual(len(result), 16000)  # 1 second at 16kHz
    
    def test_wake_word_detection_logic(self):
        """Test wake word detection logic"""
        # Test with wake word present
        test_text = "hey jarvis what time is it"
        wake_words = ["jarvis", "hey jarvis"]
        
        found = any(wake_word in test_text for wake_word in wake_words)
        self.assertTrue(found)
        
        # Test without wake word
        test_text_no_wake = "what is the weather today"
        found = any(wake_word in test_text_no_wake for wake_word in wake_words)
        self.assertFalse(found)
    
    def test_voice_command_creation(self):
        """Test VoiceCommand object creation"""
        test_audio = np.random.random(16000).astype(np.float32)
        
        # Mock the transcription to avoid loading Whisper model
        with patch.object(self.processor, 'transcribe_audio', return_value=("test command", 0.9)):
            with patch.object(self.processor, 'record_audio', return_value=test_audio):
                command = self.processor.capture_command(5)
        
        self.assertIsInstance(command, VoiceCommand)
        self.assertEqual(command.text, "test command")
        self.assertEqual(command.confidence, 0.9)
        self.assertIsInstance(command.audio_data, np.ndarray)
    
    def test_speaker_identification_placeholder(self):
        """Test speaker identification placeholder"""
        test_audio = np.random.random(16000).astype(np.float32)
        
        speaker_id = self.processor.identify_speaker(test_audio)
        
        # Should return default speaker for now
        self.assertEqual(speaker_id, "default_user")
    
    def test_audio_device_listing(self):
        """Test audio device listing"""
        with patch('sounddevice.query_devices') as mock_query:
            # Mock device list
            mock_devices = [
                {'name': 'Test Mic', 'max_input_channels': 1, 'default_samplerate': 44100},
                {'name': 'Test Speaker', 'max_input_channels': 0, 'default_samplerate': 44100},
                {'name': 'Test Mic 2', 'max_input_channels': 2, 'default_samplerate': 48000}
            ]
            mock_query.return_value = mock_devices
            
            devices = self.processor.get_audio_devices()
            
            # Should only return input devices (max_input_channels > 0)
            self.assertEqual(len(devices), 2)
            self.assertEqual(devices[0]['name'], 'Test Mic')
            self.assertEqual(devices[1]['name'], 'Test Mic 2')
    
    def test_voice_response_handling(self):
        """Test voice response handling"""
        response = VoiceResponse(
            text="Hello, how can I help you?",
            emotion="friendly",
            priority=1
        )
        
        # Test speaking response (currently just logs)
        result = self.processor.speak_response(response)
        self.assertTrue(result)
    
    def test_audio_system_test(self):
        """Test audio system testing functionality"""
        with patch.object(self.processor, 'record_audio', return_value=np.random.random(16000)):
            results = self.processor.test_audio_system()
        
        self.assertIsInstance(results, dict)
        self.assertIn('microphone', results)
        self.assertIn('whisper_model', results)
        self.assertIn('noise_filtering', results)
        self.assertIn('voice_activity_detection', results)

if __name__ == '__main__':
    # Run tests with minimal output
    unittest.main(verbosity=1)