"""
Base interfaces for Jarvis modules
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class IntentType(Enum):
    """Types of user intents"""
    TASK_MANAGEMENT = "task_management"
    SMART_HOME = "smart_home"
    INFORMATION = "information"
    ENTERTAINMENT = "entertainment"
    HEALTH = "health"
    LEARNING = "learning"
    COMMUNICATION = "communication"
    SYSTEM = "system"

@dataclass
class Intent:
    """Represents a user intent with context"""
    action: str
    intent_type: IntentType
    entities: Dict[str, Any]
    confidence: float
    context: Dict[str, Any]
    timestamp: datetime
    user_id: str = "default"

@dataclass
class ModuleResponse:
    """Standard response format from modules"""
    success: bool
    message: str
    data: Dict[str, Any]
    follow_up_required: bool = False
    context_updates: Dict[str, Any] = None

    def __post_init__(self):
        if self.context_updates is None:
            self.context_updates = {}

@dataclass
class UserProfile:
    """User profile and preferences"""
    user_id: str
    preferences: Dict[str, Any]
    learning_history: List[Dict]
    privacy_settings: Dict[str, bool]
    context_updates: Dict[str, Any]

class BaseModule(ABC):
    """Base class for all Jarvis modules"""
    
    def __init__(self, name: str):
        self.name = name
        self.capabilities = []
        self.is_enabled = True
    
    @abstractmethod
    def can_handle(self, intent: Intent) -> bool:
        """Check if this module can handle the given intent"""
        pass
    
    @abstractmethod
    def execute(self, intent: Intent, context: Dict[str, Any]) -> ModuleResponse:
        """Execute the intent and return response"""
        pass
    
    def get_capabilities(self) -> List[str]:
        """Return list of capabilities this module provides"""
        return self.capabilities
    
    def validate_ethical_compliance(self, intent: Intent) -> bool:
        """Validate that the intent is ethically compliant"""
        # Base implementation - can be overridden by modules
        return True
    
    def initialize(self) -> bool:
        """Initialize the module - called at startup"""
        return True
    
    def shutdown(self) -> bool:
        """Cleanup when shutting down"""
        return True