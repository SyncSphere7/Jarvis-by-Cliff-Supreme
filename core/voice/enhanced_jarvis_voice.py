"""
Enhanced Jarvis Voice System integrating all voice components
"""

import logging
import time
from typing import Optional, Dict, Any

from core.voice.enhanced_voice_processor import EnhancedVoiceProcessor
from core.voice.voice_response_generator import VoiceResponseGenerator, PersonalityTrait
from core.brain.enhanced_nlp_processor import EnhancedNLPProcessor
from core.interfaces.voice_interface import VoiceCommand, VoiceResponse

logger = logging.getLogger(__name__)

class EnhancedJarvisVoice:
    """Enhanced Jarvis voice system with improved processing and responses"""
    
    def __init__(self, 
                 command_manager,
                 personality: PersonalityTrait = PersonalityTrait.EMPATHETIC,
                 wake_words: list = None):
        
        self.command_manager = command_manager
        
        # Initialize voice components
        self.voice_processor = EnhancedVoiceProcessor(
            wake_words=wake_words or ["jarvis", "hey jarvis", "hello jarvis"]
        )
        
        self.response_generator = VoiceResponseGenerator(
            personality=personality
        )
        
        self.nlp_processor = EnhancedNLPProcessor()
        
        # System state
        self.is_active = False
        self.conversation_active = False
        
        logger.info("Enhanced Jarvis Voice System initialized")
    
    def start(self):
        """Start the enhanced voice system"""
        logger.info("Enhanced Jarvis Voice System starting...")
        
        # Test audio system
        audio_test = self.voice_processor.test_audio_system()
        if not audio_test['microphone']:
            logger.error("Microphone test failed - voice input may not work")
        
        # Generate startup greeting
        greeting_response = self.response_generator.generate_response('greeting')
        self.response_generator.speak_response(greeting_response)
        
        self.is_active = True
        
        try:
            self._main_loop()
        except KeyboardInterrupt:
            logger.info("Voice system stopped by user")
        finally:
            self.shutdown()
    
    def _main_loop(self):
        """Main voice processing loop"""
        while self.is_active:
            try:
                # Listen for wake word
                if self.voice_processor.listen_for_wake_word():
                    logger.info("Wake word detected!")
                    
                    # Generate acknowledgment
                    ack_response = self.response_generator.generate_response('acknowledgment')
                    self.response_generator.speak_response(ack_response)
                    
                    # Process command
                    self._process_voice_command()
                    
                    time.sleep(1)  # Brief pause before listening again
                else:
                    time.sleep(0.5)  # Short pause between wake word attempts
                    
            except Exception as e:
                logger.error(f"Error in main voice loop: {e}")
                time.sleep(1)
    
    def _process_voice_command(self):
        """Process a voice command after wake word detection"""
        try:
            # Capture the command
            voice_command = self.voice_processor.capture_command(timeout=10)
            
            if not voice_command:
                # No command captured
                response = self.response_generator.generate_response(
                    'error',
                    context={'error': True},
                    custom_text="I didn't hear anything. Could you please try again?"
                )
                self.response_generator.speak_response(response)
                return
            
            logger.info(f"Processing command: '{voice_command.text}'")
            
            # Process with enhanced NLP
            nlp_result = self.nlp_processor.process_natural_language(voice_command.text)
            
            # Check if clarification is needed
            if nlp_result.get('requires_clarification'):
                response = self.response_generator.generate_response(
                    'clarification',
                    custom_text="I need a bit more information. Could you be more specific?"
                )
                self.response_generator.speak_response(response)
                return
            
            # Execute command through command manager
            command_result = self.command_manager.execute_command(voice_command.text)
            
            # Generate appropriate response
            if command_result:
                if "error" in command_result.lower() or "sorry" in command_result.lower():
                    response = self.response_generator.generate_response(
                        'error',
                        context={'error': True},
                        custom_text=command_result
                    )
                else:
                    response = self.response_generator.generate_response(
                        'success',
                        context={'success': True},
                        custom_text=command_result
                    )
            else:
                response = self.response_generator.generate_response(
                    'success',
                    context={'success': True}
                )
            
            self.response_generator.speak_response(response)
            
        except Exception as e:
            logger.error(f"Error processing voice command: {e}")
            error_response = self.response_generator.generate_response(
                'error',
                context={'error': True},
                custom_text="I encountered an error while processing your request."
            )
            self.response_generator.speak_response(error_response)
    
    def process_text_command(self, text: str) -> str:
        """Process a text command (for testing or text interface)"""
        try:
            # Process with NLP
            nlp_result = self.nlp_processor.process_natural_language(text)
            
            # Execute command
            command_result = self.command_manager.execute_command(text)
            
            # Generate response
            if command_result:
                response = self.response_generator.generate_response(
                    'success' if 'error' not in command_result.lower() else 'error',
                    custom_text=command_result
                )
            else:
                response = self.response_generator.generate_response('success')
            
            return response.text
            
        except Exception as e:
            logger.error(f"Error processing text command: {e}")
            return "I encountered an error while processing your request."
    
    def set_personality(self, personality: PersonalityTrait):
        """Change the AI's personality"""
        self.response_generator.set_personality(personality)
        
        # Announce personality change
        response = self.response_generator.generate_response(
            'acknowledgment',
            custom_text=f"I've switched to {personality.value} mode. How can I help you?"
        )
        self.response_generator.speak_response(response)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        audio_status = self.voice_processor.test_audio_system()
        personality_info = self.response_generator.get_personality_info()
        
        return {
            'is_active': self.is_active,
            'conversation_active': self.conversation_active,
            'audio_system': audio_status,
            'personality': personality_info,
            'available_devices': self.voice_processor.get_audio_devices()
        }
    
    def shutdown(self):
        """Shutdown the voice system gracefully"""
        logger.info("Shutting down Enhanced Jarvis Voice System...")
        
        self.is_active = False
        
        # Generate goodbye
        if hasattr(self, 'response_generator'):
            goodbye_response = self.response_generator.generate_response('goodbye')
            self.response_generator.speak_response(goodbye_response)
        
        logger.info("Enhanced Jarvis Voice System shutdown complete")
    
    def test_voice_system(self) -> Dict[str, bool]:
        """Test all voice system components"""
        results = {
            'voice_processor': False,
            'response_generator': False,
            'nlp_processor': False,
            'integration': False
        }
        
        try:
            # Test voice processor
            audio_test = self.voice_processor.test_audio_system()
            results['voice_processor'] = audio_test['microphone'] and audio_test['whisper_model']
            
            # Test response generator
            test_response = self.response_generator.generate_response('greeting')
            results['response_generator'] = isinstance(test_response, VoiceResponse)
            
            # Test NLP processor
            nlp_test = self.nlp_processor.process_natural_language("hello jarvis")
            results['nlp_processor'] = 'intent' in nlp_test
            
            # Test integration
            integration_result = self.process_text_command("hello")
            results['integration'] = isinstance(integration_result, str) and len(integration_result) > 0
            
        except Exception as e:
            logger.error(f"Error in voice system test: {e}")
        
        return results