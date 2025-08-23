"""
Enhanced Voice Response Generator with personality and emotion
"""

import logging
import random
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass
import threading
import queue
import time
from gtts import gTTS
import pygame
import tempfile

from core.interfaces.voice_interface import VoiceResponse

logger = logging.getLogger(__name__)

class EmotionType(Enum):
    """Types of emotions for voice responses"""
    NEUTRAL = "neutral"
    FRIENDLY = "friendly"
    EXCITED = "excited"
    CONCERNED = "concerned"
    APOLOGETIC = "apologetic"
    CONFIDENT = "confident"
    HELPFUL = "helpful"
    HUMOROUS = "humorous"

class PersonalityTrait(Enum):
    """Personality traits that influence responses"""
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    WITTY = "witty"
    EMPATHETIC = "empathetic"

@dataclass
class ResponseTemplate:
    """Template for generating contextual responses"""
    base_text: str
    emotion: EmotionType
    personality_variants: Dict[PersonalityTrait, str]
    context_conditions: List[str] = None

class VoiceResponseGenerator:
    """Enhanced voice response generator with personality and emotion"""
    
    def __init__(self, 
                 personality: PersonalityTrait = PersonalityTrait.EMPATHETIC,
                 voice_rate: int = 200,
                 voice_volume: float = 0.9):
        
        self.personality = personality
        self.voice_rate = voice_rate
        self.voice_volume = voice_volume
        
        # Initialize TTS engine (placeholder for now)
        self.tts_engine = None
        self.tts_queue = queue.Queue()
        self.is_speaking = False
        
        # Response templates
        self.response_templates = self._initialize_response_templates()
        
        # Context tracking for personality consistency
        self.conversation_mood = EmotionType.NEUTRAL
        self.recent_interactions = []
        
        logger.info(f"Voice Response Generator initialized with {personality.value} personality")
    
    def _initialize_response_templates(self) -> Dict[str, List[ResponseTemplate]]:
        """Initialize response templates for different scenarios"""
        return {
            'greeting': [
                ResponseTemplate(
                    base_text="Hello! How can I help you today?",
                    emotion=EmotionType.FRIENDLY,
                    personality_variants={
                        PersonalityTrait.PROFESSIONAL: "Good day. How may I assist you?",
                        PersonalityTrait.CASUAL: "Hey there! What's up?",
                        PersonalityTrait.WITTY: "Well hello there! Ready for some AI magic?",
                        PersonalityTrait.EMPATHETIC: "Hello! I'm here and ready to help with whatever you need."
                    }
                )
            ],
            'acknowledgment': [
                ResponseTemplate(
                    base_text="Got it!",
                    emotion=EmotionType.CONFIDENT,
                    personality_variants={
                        PersonalityTrait.PROFESSIONAL: "Understood.",
                        PersonalityTrait.CASUAL: "Yep, got it!",
                        PersonalityTrait.WITTY: "Roger that, captain!",
                        PersonalityTrait.EMPATHETIC: "I understand completely."
                    }
                )
            ],
            'error': [
                ResponseTemplate(
                    base_text="I'm sorry, I encountered an error.",
                    emotion=EmotionType.APOLOGETIC,
                    personality_variants={
                        PersonalityTrait.PROFESSIONAL: "I apologize, but an error has occurred.",
                        PersonalityTrait.CASUAL: "Oops, something went wrong.",
                        PersonalityTrait.WITTY: "Well, that's embarrassing. I seem to have hit a snag.",
                        PersonalityTrait.EMPATHETIC: "I'm really sorry, but I ran into a problem."
                    }
                )
            ],
            'success': [
                ResponseTemplate(
                    base_text="Done!",
                    emotion=EmotionType.CONFIDENT,
                    personality_variants={
                        PersonalityTrait.PROFESSIONAL: "Task completed successfully.",
                        PersonalityTrait.CASUAL: "All done!",
                        PersonalityTrait.WITTY: "Boom! Nailed it!",
                        PersonalityTrait.EMPATHETIC: "There you go! I hope that helps."
                    }
                )
            ]
        } 
   
    def generate_response(self, 
                         message_type: str, 
                         context: Dict[str, Any] = None,
                         custom_text: str = None) -> VoiceResponse:
        """Generate a contextual voice response"""
        
        if custom_text:
            # Use custom text with appropriate emotion
            emotion = self._determine_emotion_from_context(context or {})
            return VoiceResponse(
                text=custom_text,
                emotion=emotion.value,
                priority=context.get('priority', 1) if context else 1
            )
        
        # Get appropriate template
        templates = self.response_templates.get(message_type, [])
        if not templates:
            # Fallback for unknown message types
            return VoiceResponse(
                text="I understand.",
                emotion=EmotionType.NEUTRAL.value,
                priority=1
            )
        
        # Select template based on context
        selected_template = self._select_template(templates, context or {})
        
        # Generate personalized text
        response_text = self._personalize_response(selected_template)
        
        # Determine priority
        priority = self._determine_priority(selected_template.emotion, context or {})
        
        return VoiceResponse(
            text=response_text,
            emotion=selected_template.emotion.value,
            priority=priority,
            should_interrupt=priority >= 4
        )
    
    def speak_response(self, response: VoiceResponse) -> bool:
        """Queue a response for speaking"""
        try:
            tts = gTTS(text=response.text, lang='en')
            with tempfile.NamedTemporaryFile(delete=True) as fp:
                tts.save(f"{fp.name}.mp3")
                pygame.mixer.init()
                pygame.mixer.music.load(f"{fp.name}.mp3")
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
            
            # Track interaction for personality consistency
            self._track_interaction(response)
            
            return True
            
        except Exception as e:
            logger.error(f"Error in speech response: {e}")
            return False
    
    def _select_template(self, templates: List[ResponseTemplate], context: Dict[str, Any]) -> ResponseTemplate:
        """Select the most appropriate template based on context"""
        # For now, just select the first template
        # In a full implementation, this would consider context conditions
        return templates[0]
    
    def _personalize_response(self, template: ResponseTemplate) -> str:
        """Personalize response based on personality trait"""
        if self.personality in template.personality_variants:
            return template.personality_variants[self.personality]
        return template.base_text
    
    def _determine_emotion_from_context(self, context: Dict[str, Any]) -> EmotionType:
        """Determine appropriate emotion from context"""
        if context.get('error'):
            return EmotionType.APOLOGETIC
        elif context.get('success'):
            return EmotionType.CONFIDENT
        elif context.get('urgent'):
            return EmotionType.CONCERNED
        elif context.get('humor'):
            return EmotionType.HUMOROUS
        else:
            return EmotionType.FRIENDLY
    
    def _determine_priority(self, emotion: EmotionType, context: Dict[str, Any]) -> int:
        """Determine response priority"""
        if context.get('urgent'):
            return 5
        elif emotion in [EmotionType.CONCERNED, EmotionType.APOLOGETIC]:
            return 3
        elif emotion == EmotionType.EXCITED:
            return 2
        else:
            return 1
    
    def _track_interaction(self, response: VoiceResponse):
        """Track interaction for personality consistency"""
        self.recent_interactions.append({
            'emotion': response.emotion,
            'text_length': len(response.text),
            'timestamp': time.time()
        })
        
        # Keep only recent interactions (last 10)
        if len(self.recent_interactions) > 10:
            self.recent_interactions = self.recent_interactions[-10:]
    
    def set_personality(self, personality: PersonalityTrait):
        """Change the AI's personality"""
        self.personality = personality
        logger.info(f"Personality changed to: {personality.value}")
    
    def get_personality_info(self) -> Dict[str, Any]:
        """Get current personality information"""
        return {
            'current_personality': self.personality.value,
            'conversation_mood': self.conversation_mood.value,
            'recent_interactions': len(self.recent_interactions)
        }
