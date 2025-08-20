"""
Unit tests for voice response generation
"""

import unittest
from unittest.mock import Mock, patch

from core.voice.voice_response_generator import (
    VoiceResponseGenerator, 
    EmotionType, 
    PersonalityTrait,
    ResponseTemplate
)
from core.interfaces.voice_interface import VoiceResponse

class TestVoiceResponseGenerator(unittest.TestCase):
    """Test cases for Voice Response Generator"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.generator = VoiceResponseGenerator(
            personality=PersonalityTrait.EMPATHETIC
        )
    
    def test_initialization(self):
        """Test voice response generator initialization"""
        self.assertEqual(self.generator.personality, PersonalityTrait.EMPATHETIC)
        self.assertEqual(self.generator.voice_rate, 200)
        self.assertEqual(self.generator.voice_volume, 0.9)
        self.assertIsNotNone(self.generator.response_templates)
    
    def test_custom_text_response(self):
        """Test generating response with custom text"""
        custom_text = "This is a custom response"
        context = {'success': True}
        
        response = self.generator.generate_response(
            message_type='custom',
            context=context,
            custom_text=custom_text
        )
        
        self.assertIsInstance(response, VoiceResponse)
        self.assertEqual(response.text, custom_text)
        self.assertEqual(response.emotion, EmotionType.CONFIDENT.value)
    
    def test_template_based_response(self):
        """Test generating response from templates"""
        response = self.generator.generate_response('greeting')
        
        self.assertIsInstance(response, VoiceResponse)
        self.assertIn('help', response.text.lower())
        self.assertEqual(response.emotion, EmotionType.FRIENDLY.value)
    
    def test_personality_variants(self):
        """Test different personality variants"""
        personalities = [
            PersonalityTrait.PROFESSIONAL,
            PersonalityTrait.CASUAL,
            PersonalityTrait.WITTY,
            PersonalityTrait.EMPATHETIC
        ]
        
        for personality in personalities:
            generator = VoiceResponseGenerator(personality=personality)
            response = generator.generate_response('greeting')
            
            self.assertIsInstance(response, VoiceResponse)
            self.assertIsInstance(response.text, str)
            self.assertTrue(len(response.text) > 0)
    
    def test_emotion_determination_from_context(self):
        """Test emotion determination from context"""
        test_cases = [
            ({'error': True}, EmotionType.APOLOGETIC),
            ({'success': True}, EmotionType.CONFIDENT),
            ({'urgent': True}, EmotionType.CONCERNED),
            ({'humor': True}, EmotionType.HUMOROUS),
            ({}, EmotionType.FRIENDLY)
        ]
        
        for context, expected_emotion in test_cases:
            emotion = self.generator._determine_emotion_from_context(context)
            self.assertEqual(emotion, expected_emotion)
    
    def test_priority_determination(self):
        """Test priority determination"""
        test_cases = [
            ({'urgent': True}, 5),
            ({}, EmotionType.CONCERNED, 3),
            ({}, EmotionType.APOLOGETIC, 3),
            ({}, EmotionType.EXCITED, 2),
            ({}, EmotionType.NEUTRAL, 1)
        ]
        
        for case in test_cases:
            if len(case) == 2:
                context, expected_priority = case
                emotion = EmotionType.NEUTRAL
            else:
                context, emotion, expected_priority = case
            
            priority = self.generator._determine_priority(emotion, context)
            self.assertEqual(priority, expected_priority)
    
    def test_response_template_structure(self):
        """Test response template structure"""
        templates = self.generator.response_templates
        
        # Check that we have expected template types
        expected_types = ['greeting', 'acknowledgment', 'error', 'success']
        for template_type in expected_types:
            self.assertIn(template_type, templates)
            self.assertIsInstance(templates[template_type], list)
            self.assertGreater(len(templates[template_type]), 0)
        
        # Check template structure
        for template_list in templates.values():
            for template in template_list:
                self.assertIsInstance(template, ResponseTemplate)
                self.assertIsInstance(template.base_text, str)
                self.assertIsInstance(template.emotion, EmotionType)
                self.assertIsInstance(template.personality_variants, dict)
    
    def test_personality_variants_completeness(self):
        """Test that all personality variants are defined"""
        templates = self.generator.response_templates
        
        for template_list in templates.values():
            for template in template_list:
                # Check that all personality traits have variants
                for personality in PersonalityTrait:
                    self.assertIn(personality, template.personality_variants,
                                f"Missing personality variant for {personality}")
    
    def test_speak_response(self):
        """Test speaking a response"""
        response = VoiceResponse(
            text="Test response",
            emotion=EmotionType.FRIENDLY.value,
            priority=1
        )
        
        # Should return True for successful "speaking" (printing)
        result = self.generator.speak_response(response)
        self.assertTrue(result)
    
    def test_interaction_tracking(self):
        """Test interaction tracking"""
        initial_count = len(self.generator.recent_interactions)
        
        response = VoiceResponse(
            text="Test response",
            emotion=EmotionType.FRIENDLY.value,
            priority=1
        )
        
        self.generator._track_interaction(response)
        
        self.assertEqual(len(self.generator.recent_interactions), initial_count + 1)
        
        # Check interaction data
        last_interaction = self.generator.recent_interactions[-1]
        self.assertEqual(last_interaction['emotion'], EmotionType.FRIENDLY.value)
        self.assertEqual(last_interaction['text_length'], len(response.text))
        self.assertIn('timestamp', last_interaction)
    
    def test_personality_change(self):
        """Test changing personality"""
        original_personality = self.generator.personality
        new_personality = PersonalityTrait.WITTY
        
        self.generator.set_personality(new_personality)
        self.assertEqual(self.generator.personality, new_personality)
        self.assertNotEqual(self.generator.personality, original_personality)
    
    def test_personality_info(self):
        """Test getting personality information"""
        info = self.generator.get_personality_info()
        
        self.assertIsInstance(info, dict)
        self.assertIn('current_personality', info)
        self.assertIn('conversation_mood', info)
        self.assertIn('recent_interactions', info)
        
        self.assertEqual(info['current_personality'], self.generator.personality.value)
        self.assertEqual(info['conversation_mood'], self.generator.conversation_mood.value)
    
    def test_fallback_for_unknown_message_type(self):
        """Test fallback response for unknown message types"""
        response = self.generator.generate_response('unknown_type')
        
        self.assertIsInstance(response, VoiceResponse)
        self.assertEqual(response.text, "I understand.")
        self.assertEqual(response.emotion, EmotionType.NEUTRAL.value)
        self.assertEqual(response.priority, 1)
    
    def test_template_selection(self):
        """Test template selection logic"""
        templates = [
            ResponseTemplate(
                base_text="Template 1",
                emotion=EmotionType.FRIENDLY,
                personality_variants={PersonalityTrait.EMPATHETIC: "Empathetic 1"}
            ),
            ResponseTemplate(
                base_text="Template 2", 
                emotion=EmotionType.EXCITED,
                personality_variants={PersonalityTrait.EMPATHETIC: "Empathetic 2"}
            )
        ]
        
        selected = self.generator._select_template(templates, {})
        self.assertIn(selected, templates)
    
    def test_response_personalization(self):
        """Test response personalization"""
        template = ResponseTemplate(
            base_text="Base text",
            emotion=EmotionType.FRIENDLY,
            personality_variants={
                PersonalityTrait.EMPATHETIC: "Empathetic text",
                PersonalityTrait.PROFESSIONAL: "Professional text"
            }
        )
        
        # Test with empathetic personality
        self.generator.set_personality(PersonalityTrait.EMPATHETIC)
        personalized = self.generator._personalize_response(template)
        self.assertEqual(personalized, "Empathetic text")
        
        # Test with professional personality
        self.generator.set_personality(PersonalityTrait.PROFESSIONAL)
        personalized = self.generator._personalize_response(template)
        self.assertEqual(personalized, "Professional text")

if __name__ == '__main__':
    unittest.main(verbosity=1)