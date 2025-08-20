"""
Voice interface definitions
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from dataclasses import dataclass
import numpy as np

@dataclass
class VoiceCommand:
    """Represents a voice command with metadata"""
    text: str
    confidence: float
    audio_data: Optional[np.ndarray] = None
    speaker_id: Optional[str] = None
    language: str = "en"
    timestamp: float = 0.0

@dataclass
class VoiceResponse:
    """Represents a voice response to be spoken"""
    text: str
    emotion: str = "neutral"
    priority: int = 1  # 1=low, 5=urgent
    should_interrupt: bool = False

class VoiceProcessor(ABC):
    """Abstract base class for voice processing"""
    
    @abstractmethod
    def listen_for_wake_word(self) -> bool:
        """Listen for wake word activation"""
        pass
    
    @abstractmethod
    def capture_command(self, timeout: int = 10) -> Optional[VoiceCommand]:
        """Capture and transcribe voice command"""
        pass
    
    @abstractmethod
    def speak_response(self, response: VoiceResponse) -> bool:
        """Convert text to speech and play"""
        pass
    
    @abstractmethod
    def identify_speaker(self, audio_data: np.ndarray) -> Optional[str]:
        """Identify the speaker from audio data"""
        pass

class NaturalLanguageProcessor(ABC):
    """Abstract base class for NLP processing"""
    
    @abstractmethod
    def process_natural_language(self, text: str) -> Dict[str, Any]:
        """Process natural language and extract intent/entities"""
        pass
    
    @abstractmethod
    def classify_intent(self, text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Classify user intent from text"""
        pass
    
    @abstractmethod
    def extract_entities(self, text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract entities from text"""
        pass