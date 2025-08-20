"""
Unit tests for NLP processing functionality
"""

import unittest
from datetime import datetime, timedelta

from core.brain.enhanced_nlp_processor import EnhancedNLPProcessor, EntityType, ExtractedEntity
from core.interfaces.base_module import IntentType

class TestEnhancedNLPProcessor(unittest.TestCase):
    """Test cases for Enhanced NLP Processor"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.nlp = EnhancedNLPProcessor()
    
    def test_text_normalization(self):
        """Test text normalization"""
        test_cases = [
            ("Hello   World", "hello world"),
            ("I can't do that", "i cannot do that"),
            ("We're going home", "we are going home"),
            ("It's 3:30 PM", "it is 3:30 pm")
        ]
        
        for input_text, expected in test_cases:
            result = self.nlp._normalize_text(input_text)
            self.assertEqual(result, expected)
    
    def test_time_entity_extraction(self):
        """Test time entity extraction"""
        test_cases = [
            ("Set alarm for 3:30 PM", "3:30 pm"),
            ("Wake me up at 7 AM", "7 am"),
            ("Meeting this morning", "morning"),
            ("Call me at noon", "noon")
        ]
        
        for text, expected_time in test_cases:
            entities = self.nlp.extract_entities(text.lower(), {})
            time_entities = [e for e in entities if e.entity_type == EntityType.TIME]
            
            self.assertGreater(len(time_entities), 0, f"No time entity found in: {text}")
            self.assertEqual(time_entities[0].text, expected_time)
    
    def test_device_entity_extraction(self):
        """Test device entity extraction"""
        test_cases = [
            ("Turn on the lights", "lights"),
            ("Adjust the thermostat", "thermostat"),
            ("Lock the door", "lock"),
            ("Turn off the TV", "tv")
        ]
        
        for text, expected_device in test_cases:
            entities = self.nlp.extract_entities(text.lower(), {})
            device_entities = [e for e in entities if e.entity_type == EntityType.DEVICE]
            
            self.assertGreater(len(device_entities), 0, f"No device entity found in: {text}")
            self.assertEqual(device_entities[0].text, expected_device)
    
    def test_intent_classification(self):
        """Test intent classification"""
        test_cases = [
            ("Turn on the lights", IntentType.SMART_HOME),
            ("What's the weather like", IntentType.INFORMATION),
            ("Add a task to my list", IntentType.TASK_MANAGEMENT),
            ("Play some music", IntentType.ENTERTAINMENT),
            ("Hello Jarvis", IntentType.SYSTEM)
        ]
        
        for text, expected_intent in test_cases:
            result = self.nlp.classify_intent(text, {})
            self.assertEqual(result['intent_type'], expected_intent, 
                           f"Wrong intent for: {text}")
    
    def test_action_extraction(self):
        """Test action extraction from text"""
        test_cases = [
            ("Turn on the lights", IntentType.SMART_HOME, "turn_on"),
            ("Turn off the TV", IntentType.SMART_HOME, "turn_off"),
            ("Set the temperature", IntentType.SMART_HOME, "set"),
            ("Add a new task", IntentType.TASK_MANAGEMENT, "create"),
            ("Show my tasks", IntentType.TASK_MANAGEMENT, "list")
        ]
        
        for text, intent_type, expected_action in test_cases:
            action = self.nlp._extract_action(text.lower(), intent_type)
            self.assertEqual(action, expected_action, 
                           f"Wrong action for: {text}")
    
    def test_date_entity_processing(self):
        """Test date entity processing"""
        test_cases = [
            ("Schedule meeting for tomorrow", "tomorrow"),
            ("Remind me today", "today"),
            ("Meeting on Monday", "monday")
        ]
        
        for text, expected_date in test_cases:
            entities = self.nlp.extract_entities(text.lower(), {})
            date_entities = [e for e in entities if e.entity_type == EntityType.DATE]
            
            self.assertGreater(len(date_entities), 0, f"No date entity found in: {text}")
            self.assertEqual(date_entities[0].text, expected_date)
    
    def test_number_entity_extraction(self):
        """Test number entity extraction"""
        test_cases = [
            ("Set temperature to 72 degrees", "72"),
            ("Remind me in 5 minutes", "5"),
            ("Turn volume to 50", "50")
        ]
        
        for text, expected_number in test_cases:
            entities = self.nlp.extract_entities(text.lower(), {})
            number_entities = [e for e in entities if e.entity_type == EntityType.NUMBER]
            
            self.assertGreater(len(number_entities), 0, f"No number entity found in: {text}")
            self.assertEqual(number_entities[0].text, expected_number)
    
    def test_room_entity_extraction(self):
        """Test room entity extraction"""
        test_cases = [
            ("Turn on lights in the living room", "living room"),
            ("Set bedroom temperature", "bedroom"),
            ("Kitchen lights off", "kitchen")
        ]
        
        for text, expected_room in test_cases:
            entities = self.nlp.extract_entities(text.lower(), {})
            room_entities = [e for e in entities if e.entity_type == EntityType.ROOM]
            
            self.assertGreater(len(room_entities), 0, f"No room entity found in: {text}")
            self.assertEqual(room_entities[0].text, expected_room)
    
    def test_comprehensive_processing(self):
        """Test comprehensive natural language processing"""
        test_text = "Turn on the living room lights at 7 PM"
        
        result = self.nlp.process_natural_language(test_text)
        
        # Check basic structure
        self.assertIn('original_text', result)
        self.assertIn('normalized_text', result)
        self.assertIn('intent', result)
        self.assertIn('entities', result)
        self.assertIn('confidence', result)
        
        # Check intent classification
        self.assertEqual(result['intent']['intent_type'], IntentType.SMART_HOME)
        
        # Check entities were extracted
        self.assertGreater(len(result['entities']), 0)
        
        # Check confidence is reasonable
        self.assertGreater(result['confidence'], 0.0)
    
    def test_conversation_context_update(self):
        """Test conversation context updating"""
        # Process first command
        result1 = self.nlp.process_natural_language("Turn on the lights")
        
        # Check context was updated
        self.assertIn('last_intent', self.nlp.conversation_context)
        self.assertEqual(self.nlp.conversation_context['last_intent'], IntentType.SMART_HOME)
        
        # Process second command
        result2 = self.nlp.process_natural_language("What's the weather")
        
        # Check context was updated again
        self.assertEqual(self.nlp.conversation_context['last_intent'], IntentType.INFORMATION)
    
    def test_time_processing_functions(self):
        """Test time processing helper functions"""
        import re
        
        # Test 12-hour time processing
        match = re.search(r'(\d{1,2}):(\d{2})\s*(am|pm)?', "3:30 pm")
        result = self.nlp._process_time_12hour(match, "3:30 pm")
        self.assertEqual(result['hour'], 15)  # 3 PM = 15:00
        self.assertEqual(result['minute'], 30)
        
        # Test simple time processing
        match = re.search(r'(\d{1,2})\s*(am|pm)', "7 am")
        result = self.nlp._process_time_simple(match, "7 am")
        self.assertEqual(result['hour'], 7)
        self.assertEqual(result['minute'], 0)
        
        # Test relative time processing
        match = re.search(r'(morning|afternoon|evening|night|noon|midnight)', "morning")
        result = self.nlp._process_time_relative(match, "morning")
        self.assertEqual(result['hour'], 9)
    
    def test_date_processing_functions(self):
        """Test date processing helper functions"""
        import re
        
        # Test relative date processing
        match = re.search(r'(today|tomorrow|yesterday)', "tomorrow")
        result = self.nlp._process_date_relative(match, "tomorrow")
        
        tomorrow = datetime.now().date() + timedelta(days=1)
        self.assertEqual(result['year'], tomorrow.year)
        self.assertEqual(result['month'], tomorrow.month)
        self.assertEqual(result['day'], tomorrow.day)
        
        # Test weekday processing
        match = re.search(r'(monday|tuesday|wednesday|thursday|friday|saturday|sunday)', "monday")
        result = self.nlp._process_date_weekday(match, "monday")
        self.assertEqual(result['weekday'], "monday")
        self.assertEqual(result['weekday_index'], 0)
    
    def test_device_categorization(self):
        """Test device categorization"""
        import re
        
        test_cases = [
            ("lights", "lighting"),
            ("thermostat", "climate"),
            ("door", "security"),
            ("tv", "entertainment")
        ]
        
        for device, expected_category in test_cases:
            match = re.search(rf'\b({device})\b', device)
            result = self.nlp._process_device(match, device)
            self.assertEqual(result['category'], expected_category)

if __name__ == '__main__':
    unittest.main(verbosity=1)