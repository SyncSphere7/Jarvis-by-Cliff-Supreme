"""
Supreme Integration
Integrates supreme capabilities with existing Jarvis architecture.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
import os

from .supreme_orchestrator import SupremeOrchestrator
from .supreme_config import SupremeConfig
from ..interfaces.data_models import Intent, ModuleResponse, UserProfile
from ..brain.context_manager import ContextManager
from ..security.privacy_manager import PrivacyManager
from ..monitoring.system_monitor import system_monitor

class SupremeIntegration:
    """
    Integration layer between supreme capabilities and existing Jarvis system.
    """
    
    def __init__(self, config_path: str = "data/supreme_config.json"):
        self.config_path = config_path
        self.config = None
        self.orchestrator = None
        self.logger = logging.getLogger("supreme.integration")
        self._initialized = False
        
    async def initialize(self) -> bool:
        """Initialize supreme integration"""
        try:
            self.logger.info("Initializing Supreme Integration...")
            
            # Load or create configuration
            self.config = await self._load_config()
            
            # Initialize supreme orchestrator
            self.orchestrator = SupremeOrchestrator(self.config)
            if not await self.orchestrator.initialize():
                return False
            
            self._initialized = True
            self.logger.info("Supreme Integration initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Supreme Integration: {e}")
            return False
    
    async def _load_config(self) -> SupremeConfig:
        """Load supreme configuration"""
        if os.path.exists(self.config_path):
            config = SupremeConfig.load_from_file(self.config_path)
            self.logger.info("Loaded existing supreme configuration")
        else:
            config = SupremeConfig()
            # Enable godlike mode by default for supreme being
            config.enable_godlike_mode()
            config.save_to_file(self.config_path)
            self.logger.info("Created new supreme configuration with godlike mode")
        
        return config
    
    async def process_supreme_intent(self, intent: Intent, user_profile: UserProfile = None) -> ModuleResponse:
        """
        Process an intent using supreme capabilities.
        This is the main integration point with existing Jarvis.
        """
        if not self._initialized:
            return ModuleResponse(
                success=False,
                response="Supreme capabilities not initialized",
                confidence=0.0
            )
        
        try:
            # Convert intent to supreme command
            command = self._intent_to_command(intent)
            parameters = self._extract_parameters(intent)
            
            # Execute using supreme orchestrator
            supreme_response = await self.orchestrator.execute_supreme_command(
                command=command,
                parameters=parameters,
                user_profile=user_profile,
                priority=self._calculate_priority(intent)
            )
            
            # Convert supreme response back to module response
            return self._supreme_to_module_response(supreme_response, intent)
            
        except Exception as e:
            self.logger.error(f"Error processing supreme intent: {e}")
            return ModuleResponse(
                success=False,
                response=f"Supreme processing error: {e}",
                confidence=0.0
            )
    
    def _intent_to_command(self, intent: Intent) -> str:
        """Convert Jarvis intent to supreme command"""
        # Map common intents to supreme commands
        intent_mapping = {
            "analyze": "analyze",
            "solve_problem": "solve",
            "make_plan": "plan",
            "optimize": "optimize",
            "predict": "predict",
            "system_status": "monitor",
            "fix_issue": "heal",
            "learn_from": "learn",
            "connect_to": "integrate",
            "get_insights": "analyze_data",
            "translate_text": "translate",
            "create_content": "create_content",
            "search_info": "search",
            "research_topic": "research",
            "secure_data": "secure",
            "protect_privacy": "protect"
        }
        
        # Try to find direct mapping
        if intent.intent_type in intent_mapping:
            return intent_mapping[intent.intent_type]
        
        # Fallback to analyzing the intent text
        intent_text = intent.text.lower()
        
        # Reasoning keywords
        if any(word in intent_text for word in ["analyze", "think", "reason", "solve", "plan"]):
            return "analyze"
        
        # System keywords
        if any(word in intent_text for word in ["fix", "repair", "heal", "diagnose"]):
            return "heal"
        
        # Learning keywords
        if any(word in intent_text for word in ["learn", "adapt", "improve", "remember"]):
            return "learn"
        
        # Communication keywords
        if any(word in intent_text for word in ["translate", "write", "create", "compose"]):
            return "create_content"
        
        # Knowledge keywords
        if any(word in intent_text for word in ["search", "find", "research", "lookup"]):
            return "search"
        
        # Default to analysis for complex requests
        return "analyze"
    
    def _extract_parameters(self, intent: Intent) -> Dict[str, Any]:
        """Extract parameters from intent for supreme processing"""
        parameters = {
            "intent_text": intent.text,
            "intent_type": intent.intent_type,
            "entities": intent.entities,
            "confidence": intent.confidence
        }
        
        # Add any additional context
        if hasattr(intent, 'context') and intent.context:
            parameters["context"] = intent.context
        
        return parameters
    
    def _calculate_priority(self, intent: Intent) -> int:
        """Calculate priority for supreme processing"""
        # Base priority
        priority = 5
        
        # Adjust based on intent confidence
        if intent.confidence > 0.9:
            priority += 2
        elif intent.confidence < 0.5:
            priority -= 1
        
        # Adjust based on intent type
        high_priority_intents = ["emergency", "security", "critical", "urgent"]
        if any(keyword in intent.text.lower() for keyword in high_priority_intents):
            priority = 10
        
        return max(1, min(10, priority))
    
    def _supreme_to_module_response(self, supreme_response, original_intent: Intent) -> ModuleResponse:
        """Convert supreme response to module response"""
        if not supreme_response.success:
            return ModuleResponse(
                success=False,
                response=f"Supreme processing failed: {supreme_response.error}",
                confidence=0.0,
                data={"supreme_error": supreme_response.error}
            )
        
        # Format the response based on the result
        response_text = self._format_supreme_result(supreme_response.result, original_intent)
        
        return ModuleResponse(
            success=True,
            response=response_text,
            confidence=supreme_response.confidence,
            data={
                "supreme_result": supreme_response.result,
                "execution_time": supreme_response.execution_time,
                "metadata": supreme_response.metadata
            }
        )
    
    def _format_supreme_result(self, result: Any, intent: Intent) -> str:
        """Format supreme result for user presentation"""
        if isinstance(result, dict):
            # Multi-engine result
            if "reasoning" in result:
                return f"Supreme Analysis: {result['reasoning'].get('message', str(result))}"
            elif "knowledge" in result:
                return f"Supreme Knowledge: {result['knowledge'].get('message', str(result))}"
            else:
                # Generic multi-engine response
                engine_results = []
                for engine, engine_result in result.items():
                    if isinstance(engine_result, dict) and "message" in engine_result:
                        engine_results.append(f"{engine.title()}: {engine_result['message']}")
                
                if engine_results:
                    return "Supreme Response:\n" + "\n".join(engine_results)
                else:
                    return f"Supreme Processing Complete: {str(result)}"
        
        elif isinstance(result, str):
            return f"Supreme Response: {result}"
        
        else:
            return f"Supreme Processing Complete: {str(result)}"
    
    async def get_supreme_status(self) -> Dict[str, Any]:
        """Get supreme system status"""
        if not self._initialized or not self.orchestrator:
            return {"status": "not_initialized"}
        
        status = await self.orchestrator.get_system_status()
        
        # Report engine metrics to system monitor
        if "engines" in status:
            for engine_name, engine_metrics in status["engines"].items():
                system_monitor.update_engine_metrics(engine_name, engine_metrics)
        
        return status
    
    async def enable_godlike_mode(self):
        """Enable maximum supreme capabilities"""
        if self.config:
            self.config.enable_godlike_mode()
            self.config.save_to_file(self.config_path)
            self.logger.info("Godlike mode enabled - Jarvis is now supreme!")
    
    async def shutdown(self):
        """Shutdown supreme integration"""
        if self.orchestrator:
            await self.orchestrator.shutdown()
        self._initialized = False
        self.logger.info("Supreme Integration shutdown complete")


# Global supreme integration instance
_supreme_integration: Optional[SupremeIntegration] = None

async def get_supreme_integration() -> SupremeIntegration:
    """Get or create global supreme integration instance"""
    global _supreme_integration
    
    if _supreme_integration is None:
        _supreme_integration = SupremeIntegration()
        await _supreme_integration.initialize()
    
    return _supreme_integration

async def process_with_supreme_capabilities(intent: Intent, user_profile: UserProfile = None) -> ModuleResponse:
    """
    Main function to process intents with supreme capabilities.
    This can be called from existing Jarvis modules.
    """
    integration = await get_supreme_integration()
    return await integration.process_supreme_intent(intent, user_profile)