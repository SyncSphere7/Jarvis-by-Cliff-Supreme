"""
Enhanced Natural Language Processing Engine for Jarvis
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from core.interfaces.base_module import Intent, IntentType
from core.interfaces.voice_interface import NaturalLanguageProcessor

logger = logging.getLogger(__name__)

class EntityType(Enum):
    """Types of entities that can be extracted"""
    TIME = "time"
    DATE = "date"
    NUMBER = "number"
    DEVICE = "device"
    ROOM = "room"
    PERSON = "person"
    LOCATION = "location"
    DURATION = "duration"
    TEMPERATURE = "temperature"
    PERCENTAGE = "percentage"

@dataclass
class ExtractedEntity:
    """Represents an extracted entity with metadata"""
    text: str
    entity_type: EntityType
    value: Any
    confidence: float
    start_pos: int
    end_pos: int

class EnhancedNLPProcessor(NaturalLanguageProcessor):
    """Enhanced NLP processor with context awareness and entity extraction"""
    
    def __init__(self):
        self.conversation_context = {}
        self.entity_patterns = self._initialize_entity_patterns()
        self.intent_patterns = self._initialize_intent_patterns()
        self.context_keywords = self._initialize_context_keywords()
        
        # Conversation state tracking
        self.last_intent = None
        self.pending_clarifications = []
        self.multi_turn_context = {}
        
        logger.info("Enhanced NLP Processor initialized")    

    def _initialize_entity_patterns(self) -> Dict[EntityType, List[Dict]]:
        """Initialize regex patterns for entity extraction"""
        return {
            EntityType.TIME: [
                {
                    'pattern': r'\b(\d{1,2}):(\d{2})\s*(am|pm)?\b',
                    'processor': self._process_time_12hour
                },
                {
                    'pattern': r'\b(\d{1,2})\s*(am|pm)\b',
                    'processor': self._process_time_simple
                },
                {
                    'pattern': r'\b(morning|afternoon|evening|night|noon|midnight)\b',
                    'processor': self._process_time_relative
                }
            ],
            EntityType.DATE: [
                {
                    'pattern': r'\b(today|tomorrow|yesterday)\b',
                    'processor': self._process_date_relative
                },
                {
                    'pattern': r'\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b',
                    'processor': self._process_date_weekday
                }
            ],
            EntityType.NUMBER: [
                {
                    'pattern': r'\b(\d+(?:\.\d+)?)\b',
                    'processor': self._process_number
                }
            ],
            EntityType.DEVICE: [
                {
                    'pattern': r'\b(light|lights|lamp|thermostat|door|lock|camera|tv|speaker)\b',
                    'processor': self._process_device
                }
            ],
            EntityType.ROOM: [
                {
                    'pattern': r'\b(living room|bedroom|kitchen|bathroom|office|garage)\b',
                    'processor': self._process_room
                }
            ]
        }
    
    def _initialize_intent_patterns(self) -> Dict[IntentType, List[Dict]]:
        """Initialize patterns for intent classification with context awareness"""
        return {
            IntentType.TASK_MANAGEMENT: [
                {
                    'pattern': r'\b(add|create|make|new)\s+.*(task|todo|reminder)\b',
                    'confidence': 0.9,
                    'context_boost': ['productivity', 'calendar']
                },
                {
                    'pattern': r'\b(list|show|display)\s+.*(task|todo|reminder)\b',
                    'confidence': 0.9,
                    'context_boost': ['productivity']
                },
                {
                    'pattern': r'\b(list|show)\s+(task|todo)\b',
                    'confidence': 0.9,
                    'context_boost': ['productivity']
                },
                {
                    'pattern': r'\b(complete|finish|done)\s+.*(task|todo)\b',
                    'confidence': 0.9,
                    'context_boost': ['productivity']
                },
                {
                    'pattern': r'\b(task|todo)\s+(statistic|stat|summary)\b',
                    'confidence': 0.9,
                    'context_boost': ['productivity']
                }
            ],
            IntentType.SMART_HOME: [
                {
                    'pattern': r'\b(turn|switch)\s+(on|off)\b',
                    'confidence': 0.8,
                    'context_boost': ['device', 'room']
                },
                {
                    'pattern': r'\b(set|adjust|change)\s+.*(temperature|thermostat)\b',
                    'confidence': 0.9,
                    'context_boost': ['temperature', 'climate']
                }
            ],
            IntentType.INFORMATION: [
                {
                    'pattern': r'\b(what|who|when|where|how|why)\s+(is|are|was|were)\b',
                    'confidence': 0.7,
                    'context_boost': ['question', 'search']
                },
                {
                    'pattern': r'\b(weather|forecast)\b',
                    'confidence': 0.95,
                    'context_boost': ['weather']
                }
            ],
            IntentType.ENTERTAINMENT: [
                {
                    'pattern': r'\b(play|start)\s+.*(music|song|playlist)\b',
                    'confidence': 0.9,
                    'context_boost': ['music', 'audio']
                }
            ]
        }
    
    def _initialize_context_keywords(self) -> Dict[str, List[str]]:
        """Initialize context keywords for better understanding"""
        return {
            'productivity': ['work', 'office', 'meeting', 'deadline', 'project', 'task'],
            'home': ['house', 'room', 'upstairs', 'downstairs', 'inside', 'outside'],
            'time': ['now', 'later', 'soon', 'urgent', 'schedule', 'calendar'],
            'weather': ['outside', 'rain', 'sunny', 'cloudy', 'hot', 'cold', 'warm'],
            'entertainment': ['fun', 'relax', 'enjoy', 'watch', 'listen', 'read']
        }    

    def process_natural_language(self, text: str) -> Dict[str, Any]:
        """Main entry point for processing natural language"""
        try:
            # Normalize text
            normalized_text = self._normalize_text(text)
            
            # Extract entities
            entities = self.extract_entities(normalized_text, {})
            
            # Classify intent with context
            intent_result = self.classify_intent(normalized_text, {})
            
            # Build comprehensive result
            result = {
                'original_text': text,
                'normalized_text': normalized_text,
                'intent': intent_result,
                'entities': [entity.__dict__ for entity in entities],
                'confidence': intent_result.get('confidence', 0.0),
                'conversation_context': self.conversation_context.copy()
            }
            
            # Update conversation context
            self._update_conversation_context(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing natural language: {e}")
            return {
                'original_text': text,
                'error': str(e),
                'confidence': 0.0
            }
    
    def classify_intent(self, text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Classify intent with context awareness"""
        text_lower = text.lower()
        best_intent = IntentType.SYSTEM
        best_confidence = 0.0
        matched_patterns = []
        
        # Check each intent type
        for intent_type, patterns in self.intent_patterns.items():
            for pattern_info in patterns:
                pattern = pattern_info['pattern']
                base_confidence = pattern_info['confidence']
                
                match = re.search(pattern, text_lower)
                if match:
                    confidence = base_confidence
                    
                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_intent = intent_type
                        matched_patterns.append({
                            'pattern': pattern,
                            'match': match.group(),
                            'confidence': confidence
                        })
        
        return {
            'intent_type': best_intent,
            'confidence': best_confidence,
            'matched_patterns': matched_patterns,
            'action': self._extract_action(text_lower, best_intent)
        }
    
    def extract_entities(self, text: str, context: Dict[str, Any]) -> List[ExtractedEntity]:
        """Extract entities from text with context awareness"""
        entities = []
        text_lower = text.lower()
        
        for entity_type, patterns in self.entity_patterns.items():
            for pattern_info in patterns:
                pattern = pattern_info['pattern']
                processor = pattern_info['processor']
                
                for match in re.finditer(pattern, text_lower):
                    try:
                        entity_value = processor(match, text_lower)
                        if entity_value is not None:
                            entity = ExtractedEntity(
                                text=match.group(),
                                entity_type=entity_type,
                                value=entity_value,
                                confidence=0.8,
                                start_pos=match.start(),
                                end_pos=match.end()
                            )
                            entities.append(entity)
                    except Exception as e:
                        logger.error(f"Error processing entity {entity_type}: {e}")
        
        return entities 
   
    def _normalize_text(self, text: str) -> str:
        """Normalize text for processing"""
        # Convert to lowercase
        normalized = text.lower().strip()
        
        # Remove extra whitespace
        normalized = re.sub(r'\s+', ' ', normalized)
        
        # Handle contractions
        contractions = {
            "won't": "will not",
            "can't": "cannot",
            "it's": "it is",
            "n't": " not",
            "'re": " are",
            "'ve": " have",
            "'ll": " will",
            "'d": " would",
            "'m": " am"
        }
        
        for contraction, expansion in contractions.items():
            normalized = normalized.replace(contraction, expansion)
        
        return normalized
    
    def _extract_action(self, text: str, intent_type: IntentType) -> str:
        """Extract the specific action from text based on intent"""
        action_patterns = {
            IntentType.TASK_MANAGEMENT: {
                'create': r'\b(add|create|make|new)\b',
                'list': r'\b(show|list|display|what)\b',
                'complete': r'\b(complete|finish|done)\b'
            },
            IntentType.SMART_HOME: {
                'turn_on': r'\bturn\s+on\b',
                'turn_off': r'\bturn\s+off\b',
                'set': r'\b(set|adjust|change)\b'
            },
            IntentType.INFORMATION: {
                'search': r'\b(search|find|look up)\b',
                'weather': r'\bweather\b',
                'define': r'\b(define|what is|what are)\b'
            }
        }
        
        patterns = action_patterns.get(intent_type, {})
        for action, pattern in patterns.items():
            if re.search(pattern, text):
                return action
        
        return 'unknown'
    
    def _update_conversation_context(self, result: Dict[str, Any]):
        """Update conversation context with new information"""
        self.conversation_context.update({
            'last_intent': result['intent']['intent_type'],
            'last_entities': result['entities'],
            'last_text': result['normalized_text'],
            'timestamp': datetime.now().isoformat()
        })
    
    # Entity processors
    def _process_time_12hour(self, match, text: str) -> Dict[str, Any]:
        """Process 12-hour time format"""
        hour = int(match.group(1))
        minute = int(match.group(2))
        period = match.group(3) or 'am'
        
        if period.lower() == 'pm' and hour != 12:
            hour += 12
        elif period.lower() == 'am' and hour == 12:
            hour = 0
        
        return {'hour': hour, 'minute': minute, 'format': '12hour'}
    
    def _process_time_simple(self, match, text: str) -> Dict[str, Any]:
        """Process simple time format (e.g., '3 pm')"""
        hour = int(match.group(1))
        period = match.group(2)
        
        if period.lower() == 'pm' and hour != 12:
            hour += 12
        elif period.lower() == 'am' and hour == 12:
            hour = 0
        
        return {'hour': hour, 'minute': 0, 'format': 'simple'}
    
    def _process_time_relative(self, match, text: str) -> Dict[str, Any]:
        """Process relative time (morning, afternoon, etc.)"""
        time_word = match.group(1)
        time_mapping = {
            'morning': {'hour': 9, 'minute': 0},
            'afternoon': {'hour': 14, 'minute': 0},
            'evening': {'hour': 18, 'minute': 0},
            'night': {'hour': 21, 'minute': 0},
            'noon': {'hour': 12, 'minute': 0},
            'midnight': {'hour': 0, 'minute': 0}
        }
        
        return time_mapping.get(time_word, {'hour': 12, 'minute': 0})
    
    def _process_date_relative(self, match, text: str) -> Dict[str, Any]:
        """Process relative dates"""
        date_word = match.group(1)
        today = datetime.now().date()
        
        if date_word == 'today':
            target_date = today
        elif date_word == 'tomorrow':
            target_date = today + timedelta(days=1)
        elif date_word == 'yesterday':
            target_date = today - timedelta(days=1)
        else:
            target_date = today
        
        return {
            'year': target_date.year,
            'month': target_date.month,
            'day': target_date.day,
            'type': 'relative'
        }
    
    def _process_date_weekday(self, match, text: str) -> Dict[str, Any]:
        """Process weekday dates"""
        weekday = match.group(1)
        weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        
        return {
            'weekday': weekday,
            'weekday_index': weekdays.index(weekday),
            'type': 'weekday'
        }
    
    def _process_number(self, match, text: str) -> float:
        """Process numeric numbers"""
        return float(match.group(1))
    
    def _process_device(self, match, text: str) -> Dict[str, str]:
        """Process device entities"""
        device = match.group(1)
        device_mapping = {
            'light': 'lighting', 'lights': 'lighting', 'lamp': 'lighting',
            'thermostat': 'climate', 'door': 'security', 'lock': 'security',
            'camera': 'security', 'tv': 'entertainment', 'speaker': 'entertainment'
        }
        
        return {
            'device': device,
            'category': device_mapping.get(device, 'unknown')
        }
    
    def _process_room(self, match, text: str) -> str:
        """Process room entities"""
        return match.group(1)