"""
Context management for maintaining conversation state
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class ConversationTurn:
    """Represents a single turn in conversation"""
    user_input: str
    intent_type: str
    response: str
    timestamp: datetime
    context_snapshot: Dict[str, Any] = field(default_factory=dict)

class ContextManager:
    """Manages conversation context and state"""
    
    def __init__(self, context_timeout_minutes: int = 30):
        self.current_context: Dict[str, Any] = {}
        self.conversation_history: List[ConversationTurn] = []
        self.context_timeout = timedelta(minutes=context_timeout_minutes)
        self.last_activity = datetime.now()
        
        # Initialize default context
        self.reset_context()
    
    def reset_context(self):
        """Reset context to default state"""
        self.current_context = {
            'user_id': 'default',
            'session_id': f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'active_task': None,
            'last_intent_type': None,
            'pending_confirmations': [],
            'user_preferences': {},
            'conversation_topic': None,
            'multi_step_operation': None
        }
        self.last_activity = datetime.now()
        logger.info("Context reset to default state")
    
    def update_context(self, updates: Dict[str, Any]):
        """Update context with new information"""
        self.current_context.update(updates)
        self.last_activity = datetime.now()
        logger.debug(f"Context updated: {list(updates.keys())}")
    
    def get_context(self) -> Dict[str, Any]:
        """Get current context"""
        # Check if context has expired
        if datetime.now() - self.last_activity > self.context_timeout:
            logger.info("Context expired, resetting")
            self.reset_context()
        
        return self.current_context.copy()
    
    def add_conversation_turn(self, user_input: str, intent_type: str, response: str):
        """Add a conversation turn to history"""
        turn = ConversationTurn(
            user_input=user_input,
            intent_type=intent_type,
            response=response,
            timestamp=datetime.now(),
            context_snapshot=self.current_context.copy()
        )
        
        self.conversation_history.append(turn)
        
        # Keep only last 50 turns to prevent memory issues
        if len(self.conversation_history) > 50:
            self.conversation_history = self.conversation_history[-50:]
        
        self.last_activity = datetime.now()
    
    def get_recent_context(self, turns: int = 3) -> List[ConversationTurn]:
        """Get recent conversation turns for context"""
        return self.conversation_history[-turns:] if self.conversation_history else []
    
    def set_pending_confirmation(self, confirmation_id: str, data: Dict[str, Any]):
        """Set a pending confirmation that requires user response"""
        confirmation = {
            'id': confirmation_id,
            'data': data,
            'timestamp': datetime.now()
        }
        
        self.current_context['pending_confirmations'].append(confirmation)
        logger.info(f"Added pending confirmation: {confirmation_id}")
    
    def get_pending_confirmation(self, confirmation_id: str) -> Optional[Dict[str, Any]]:
        """Get a pending confirmation by ID"""
        confirmations = self.current_context.get('pending_confirmations', [])
        for confirmation in confirmations:
            if confirmation['id'] == confirmation_id:
                return confirmation
        return None
    
    def resolve_confirmation(self, confirmation_id: str) -> bool:
        """Remove a resolved confirmation"""
        confirmations = self.current_context.get('pending_confirmations', [])
        original_count = len(confirmations)
        
        self.current_context['pending_confirmations'] = [
            c for c in confirmations if c['id'] != confirmation_id
        ]
        
        resolved = len(self.current_context['pending_confirmations']) < original_count
        if resolved:
            logger.info(f"Resolved confirmation: {confirmation_id}")
        
        return resolved
    
    def start_multi_step_operation(self, operation_type: str, data: Dict[str, Any]):
        """Start a multi-step operation"""
        self.current_context['multi_step_operation'] = {
            'type': operation_type,
            'data': data,
            'step': 1,
            'started_at': datetime.now()
        }
        logger.info(f"Started multi-step operation: {operation_type}")
    
    def update_multi_step_operation(self, updates: Dict[str, Any]):
        """Update current multi-step operation"""
        if self.current_context.get('multi_step_operation'):
            self.current_context['multi_step_operation'].update(updates)
    
    def complete_multi_step_operation(self):
        """Complete and clear multi-step operation"""
        operation = self.current_context.get('multi_step_operation')
        if operation:
            logger.info(f"Completed multi-step operation: {operation['type']}")
            self.current_context['multi_step_operation'] = None
    
    def is_in_multi_step_operation(self) -> bool:
        """Check if currently in a multi-step operation"""
        return self.current_context.get('multi_step_operation') is not None
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get a summary of the current conversation"""
        recent_turns = self.get_recent_context(5)
        
        return {
            'session_id': self.current_context.get('session_id'),
            'total_turns': len(self.conversation_history),
            'recent_topics': [turn.intent_type for turn in recent_turns],
            'active_task': self.current_context.get('active_task'),
            'pending_confirmations': len(self.current_context.get('pending_confirmations', [])),
            'in_multi_step': self.is_in_multi_step_operation(),
            'last_activity': self.last_activity
        }