"""
Supreme Module
Provides access to supreme capabilities through the command system.
"""

import logging
from typing import Dict, Any, List
import re
import os

from ..interfaces.base_module import BaseModule, Intent, ModuleResponse, UserProfile
from ..integrations.aiml_api_integration import AIMLAPIIntegration

class SupremeModule(BaseModule):
    """Supreme Jarvis Module - True AI Intelligence with AIML API"""
    
    def __init__(self):
        super().__init__("supreme")
        self.logger = logging.getLogger(__name__)
        self.logger.info("Supreme module initialized successfully")
        
        # Initialize AIML API Integration
        self.aiml_api = AIMLAPIIntegration(api_key="69ad15a4973d40d3a74e2e4ab2dc6187")
        self.logger.info("AIML API Integration initialized successfully")
        
    def can_handle(self, intent: Intent) -> bool:
        """Check if this module can handle the intent"""
        # SUPREME BEING: Handle ALL intents - no limitations!
        return True
    
    def execute(self, intent: Intent, context: Dict[str, Any]) -> ModuleResponse:
        """Execute intent using supreme AI capabilities"""
        try:
            return self._process_with_aiml_api(intent, context)
        except Exception as e:
            self.logger.error(f"Error processing supreme intent: {e}")
            return ModuleResponse(
                success=False,
                message=f"Supreme processing error: {e}",
                data={}
            )
    
    def _process_with_aiml_api(self, intent: Intent, context: Dict[str, Any]) -> ModuleResponse:
        """Process intent with AIML API - REAL AI"""
        try:
            user_request = intent.action
            
            # Select the best model for the task
            model = self.aiml_api.select_best_model(user_request)
            
            # Get response from AIML API
            response = self.aiml_api.get_response(
                user_request, 
                model=model,
                context=context  # Pass the conversation context
            )
            
            return ModuleResponse(
                success=True,
                message=response,
                data={"ai_generated": True, "model": model, "api": "aiml"}
            )
                
        except Exception as e:
            self.logger.error(f"AIML API processing error: {e}")
            return ModuleResponse(
                success=False,
                message=f"AI processing failed: {e}",
                data={}
            )
    
    def shutdown(self) -> bool:
        """Shutdown supreme module"""
        self.logger.info("Supreme module shutting down...")
        # Supreme integration shutdown is handled by main system
        return True