"""
System module for handling basic system commands
"""

import logging
from typing import Dict, Any
from core.interfaces.base_module import BaseModule, Intent, IntentType, ModuleResponse

logger = logging.getLogger(__name__)

class SystemModule(BaseModule):
    """Handles basic system commands like help, status, etc."""
    
    def __init__(self):
        super().__init__("system")
        self.capabilities = [
            "help", "status", "capabilities", "settings", "greeting", "goodbye"
        ]
    
    def can_handle(self, intent: Intent) -> bool:
        """Check if this module can handle the intent"""
        return intent.intent_type == IntentType.SYSTEM
    
    def execute(self, intent: Intent, context: Dict[str, Any]) -> ModuleResponse:
        """Execute system commands"""
        action = intent.action.lower()
        
        if "help" in action or "what can you do" in action:
            return self._handle_help(intent, context)
        elif "status" in action or "how are you" in action:
            return self._handle_status(intent, context)
        elif "hello" in action or "hi" in action or "hey" in action:
            return self._handle_greeting(intent, context)
        elif "goodbye" in action or "bye" in action or "stop" in action:
            return self._handle_goodbye(intent, context)
        else:
            return ModuleResponse(
                success=False,
                message="I'm not sure how to help with that system command.",
                data={}
            )
    
    def _handle_help(self, intent: Intent, context: Dict[str, Any]) -> ModuleResponse:
        """Handle help requests"""
        help_message = """I'm Jarvis, your ethical AI assistant! Here's what I can help you with:

🎯 **Task Management**: Create tasks, set reminders, manage your schedule
🏠 **Smart Home**: Control lights, temperature, and other connected devices  
📚 **Information**: Search the web, get weather, news, and definitions
🎵 **Entertainment**: Play music, recommend movies, tell jokes
💪 **Health & Wellness**: Track fitness, set health reminders
📖 **Learning**: Help you study, practice skills, learn new topics
💬 **Communication**: Manage messages, schedule meetings

Just speak naturally - I'll understand what you need!"""
        
        return ModuleResponse(
            success=True,
            message=help_message,
            data={"command_type": "help"}
        )
    
    def _handle_status(self, intent: Intent, context: Dict[str, Any]) -> ModuleResponse:
        """Handle status requests"""
        status_message = "I'm running well and ready to help! All systems are operational."
        
        return ModuleResponse(
            success=True,
            message=status_message,
            data={
                "command_type": "status",
                "system_status": "operational"
            }
        )
    
    def _handle_greeting(self, intent: Intent, context: Dict[str, Any]) -> ModuleResponse:
        """Handle greetings"""
        user_id = context.get('user_id', 'there')
        greeting_message = f"Hello {user_id}! I'm Jarvis, your AI assistant. How can I help you today?"
        
        return ModuleResponse(
            success=True,
            message=greeting_message,
            data={"command_type": "greeting"}
        )
    
    def _handle_goodbye(self, intent: Intent, context: Dict[str, Any]) -> ModuleResponse:
        """Handle goodbye"""
        goodbye_message = "Goodbye! Feel free to ask for help anytime."
        
        return ModuleResponse(
            success=True,
            message=goodbye_message,
            data={
                "command_type": "goodbye",
                "should_shutdown": False  # Don't actually shutdown, just acknowledge
            }
        )
    
    def initialize(self) -> bool:
        """Initialize the system module"""
        logger.info("System module initialized")
        return True
    
    def shutdown(self) -> bool:
        """Shutdown the system module"""
        logger.info("System module shutdown")
        return True