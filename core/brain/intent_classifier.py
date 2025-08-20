"""
Intent classification system for natural language understanding
"""

import re
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from core.interfaces.base_module import Intent, IntentType

logger = logging.getLogger(__name__)

class IntentClassifier:
    """Classifies user intents from natural language"""
    
    def __init__(self):
        self.intent_patterns = {
            IntentType.TASK_MANAGEMENT: [
                r'\b(add|create|make|new)\s+(task|todo|reminder)\b',
                r'\b(remind|schedule|plan)\s+me\b',
                r'\b(what|show|list)\s+(tasks|todos|reminders)\b',
                r'\b(complete|finish|done)\s+(task|todo)\b'
            ],
            IntentType.SMART_HOME: [
                r'\b(turn|switch)\s+(on|off)\s+(light|lights|lamp)\b',
                r'\b(set|adjust|change)\s+(temperature|thermostat)\b',
                r'\b(lock|unlock)\s+(door|doors)\b',
                r'\b(dim|brighten)\s+(light|lights)\b'
            ],
            IntentType.INFORMATION: [
                r'\b(what|who|when|where|how|why)\s+is\b',
                r'\b(search|find|look up|tell me about)\b',
                r'\b(weather|forecast)\b',
                r'\b(news|headlines|current events)\b'
            ],
            IntentType.ENTERTAINMENT: [
                r'\b(play|start|put on)\s+(music|song|playlist)\b',
                r'\b(recommend|suggest)\s+(movie|show|music)\b',
                r'\b(tell|give)\s+me\s+(joke|story)\b',
                r'\b(volume|pause|stop|skip|next)\b'
            ],
            IntentType.HEALTH: [
                r'\b(track|log|record)\s+(steps|exercise|workout)\b',
                r'\b(how many|show)\s+(steps|calories)\b',
                r'\b(remind|time for)\s+(medication|pills)\b',
                r'\b(health|fitness|wellness)\s+(tip|advice)\b'
            ],
            IntentType.LEARNING: [
                r'\b(teach|learn|study|practice)\b',
                r'\b(quiz|test)\s+me\b',
                r'\b(translate|pronunciation)\b',
                r'\b(explain|define|what does)\b'
            ],
            IntentType.COMMUNICATION: [
                r'\b(send|write|compose)\s+(message|email|text)\b',
                r'\b(read|check)\s+(messages|emails|texts)\b',
                r'\b(call|phone|dial)\b',
                r'\b(schedule|set up)\s+(meeting|appointment)\b'
            ],
            IntentType.SYSTEM: [
                r'\b(help|what can you do)\b',
                r'\b(settings|preferences|configure)\b',
                r'\b(status|how are you)\b',
                r'\b(stop|quit|exit|goodbye|bye)\b',
                r'\b(hello|hi|hey|greetings)\b'
            ]
        }
        
        self.entity_patterns = {
            'time': r'\b(\d{1,2}:\d{2}|\d{1,2}\s*(am|pm)|morning|afternoon|evening|tonight|tomorrow|today|yesterday)\b',
            'date': r'\b(\d{1,2}/\d{1,2}/\d{4}|\d{1,2}-\d{1,2}-\d{4}|monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b',
            'number': r'\b\d+\b',
            'device': r'\b(light|lights|lamp|thermostat|door|lock|camera|tv|speaker)\b',
            'room': r'\b(living room|bedroom|kitchen|bathroom|office|garage|basement)\b'
        }
    
    def classify_intent(self, text: str, context: Dict[str, Any] = None) -> Intent:
        """Classify the intent from user text"""
        if context is None:
            context = {}
        
        text_lower = text.lower()
        best_intent_type = IntentType.SYSTEM  # default
        best_confidence = 0.0
        matched_action = text  # Use actual text instead of "unknown"
        
        # Find the best matching intent type
        for intent_type, patterns in self.intent_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text_lower)
                if match:
                    # Simple confidence scoring based on match length
                    confidence = len(match.group()) / len(text_lower)
                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_intent_type = intent_type
                        matched_action = text  # Keep original text for supreme processing
        
        # Extract entities
        entities = self.extract_entities(text_lower)
        
        # Create intent object
        intent = Intent(
            action=matched_action,
            intent_type=best_intent_type,
            entities=entities,
            confidence=min(best_confidence * 2, 1.0),  # Scale confidence
            context=context,
            timestamp=datetime.now()
        )
        
        logger.info(f"Classified intent: {intent.intent_type.value} with confidence {intent.confidence:.2f}")
        return intent
    
    def extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract entities from text"""
        entities = {}
        
        for entity_type, pattern in self.entity_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                entities[entity_type] = matches
        
        return entities
    
    def get_action_from_text(self, text: str, intent_type: IntentType) -> str:
        """Extract the specific action from text based on intent type"""
        text_lower = text.lower()
        
        action_keywords = {
            IntentType.TASK_MANAGEMENT: ['add', 'create', 'list', 'complete', 'delete'],
            IntentType.SMART_HOME: ['turn_on', 'turn_off', 'set', 'adjust', 'lock', 'unlock'],
            IntentType.INFORMATION: ['search', 'weather', 'news', 'define'],
            IntentType.ENTERTAINMENT: ['play', 'pause', 'stop', 'recommend', 'joke'],
            IntentType.HEALTH: ['track', 'log', 'remind', 'advice'],
            IntentType.LEARNING: ['teach', 'quiz', 'translate', 'explain'],
            IntentType.COMMUNICATION: ['send', 'read', 'call', 'schedule'],
            IntentType.SYSTEM: ['help', 'status', 'settings', 'stop']
        }
        
        keywords = action_keywords.get(intent_type, [])
        for keyword in keywords:
            if keyword.replace('_', ' ') in text_lower:
                return keyword
        
        return 'unknown'