from core.utils.log import logger
from core.ethics.validator import EthicsValidator
from core.ethics.content_filter import ContentFilter
from core.brain.module_registry import ModuleRegistry
from core.brain.intent_classifier import IntentClassifier
from core.brain.context_manager import ContextManager
from core.interfaces.base_module import ModuleResponse

class CommandManager:
    """Enhanced command manager with modular architecture"""
    
    def __init__(self):
        # Legacy command support
        self.commands = {}
        
        # New modular architecture
        self.module_registry = ModuleRegistry()
        self.intent_classifier = IntentClassifier()
        self.context_manager = ContextManager()
        
        # Ethics and safety
        self.ethics_validator = EthicsValidator()
        self.content_filter = ContentFilter()
        
        logger.info("Enhanced CommandManager initialized")

    def register_command(self, keywords, function):
        """Legacy command registration - kept for backward compatibility"""
        for keyword in keywords:
            self.commands[keyword] = function
            logger.info(f"Registered legacy command for keyword: {keyword}")

    def register_module(self, module):
        """Register a new module with the system"""
        return self.module_registry.register_module(module)

    def initialize_system(self):
        """Initialize all modules and systems"""
        logger.info("Initializing Jarvis system...")
        success = self.module_registry.initialize_all_modules()
        if success:
            logger.info("All modules initialized successfully")
        else:
            logger.warning("Some modules failed to initialize")
        return success

    def process_command(self, text: str) -> str:
        """Process a command using the new modular architecture"""
        try:
            # First validate the command for ethical compliance
            validation_result = self.ethics_validator.validate_command(text)
            
            if not validation_result["is_valid"]:
                logger.warning(f"Command blocked due to ethics violation: {text}")
                return validation_result["message"]
            
            # Filter content for safety
            filter_result = self.content_filter.filter_content(text)
            if not filter_result["is_safe"]:
                logger.info(f"Content filtered: {text}")
                text = filter_result["filtered_content"]
            
            # Classify the intent
            intent = self.intent_classifier.classify_intent(
                text, 
                self.context_manager.get_context()
            )
            
            # Get current context with conversation history
            current_context = self.context_manager.get_context()
            current_context['conversation_history'] = self.context_manager.get_recent_context(5)
            
            # Execute using module registry
            response = self.module_registry.execute_intent(
                intent, 
                current_context
            )
            
            # Update context with response
            if response.context_updates:
                self.context_manager.update_context(response.context_updates)
            
            # Add to conversation history
            self.context_manager.add_conversation_turn(
                text, 
                intent.intent_type.value, 
                response.message
            )
            
            # Log ethical decision
            self.ethics_validator.log_ethical_decision(
                text, "approved", "Command processed successfully"
            )
            
            return response.message
            
        except Exception as e:
            logger.error(f"Error processing command: {e}")
            return "I encountered an error while processing that command."

    def execute_command(self, text: str) -> str:
        """Main entry point - tries new architecture first, falls back to legacy"""
        # Try new modular architecture first
        if self.module_registry.modules:
            return self.process_command(text)
        
        # Fall back to legacy command processing
        return self._execute_legacy_command(text)

    def _execute_legacy_command(self, text: str) -> str:
        """Legacy command execution for backward compatibility"""
        # First validate the command for ethical compliance
        validation_result = self.ethics_validator.validate_command(text)
        
        if not validation_result["is_valid"]:
            logger.warning(f"Command blocked due to ethics violation: {text}")
            return validation_result["message"]
        
        # Filter content for safety
        filter_result = self.content_filter.filter_content(text)
        if not filter_result["is_safe"]:
            logger.info(f"Content filtered: {text}")
            text = filter_result["filtered_content"]
        
        # Execute the command if it passes validation
        for keyword, function in self.commands.items():
            if keyword in text.lower():
                try:
                    result = function()
                    self.ethics_validator.log_ethical_decision(
                        text, "approved", "Legacy command passed validation"
                    )
                    return result if result else "Command executed successfully."
                except Exception as e:
                    logger.error(f"Error executing legacy command: {e}")
                    return "I encountered an error while processing that command."
        
        logger.info("Unknown command.")
        return "I didn't understand that command. Could you please rephrase?"

    def get_system_status(self) -> dict:
        """Get status of the entire system"""
        return {
            "modules": self.module_registry.get_module_status(),
            "context": self.context_manager.get_conversation_summary(),
            "legacy_commands": len(self.commands)
        }

    def shutdown(self):
        """Shutdown all systems gracefully"""
        logger.info("Shutting down CommandManager...")
        self.module_registry.shutdown_all_modules()
        logger.info("CommandManager shutdown complete")