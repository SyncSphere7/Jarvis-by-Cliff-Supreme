"""
Cognitive Module for Jarvis 2.0
This module provides access to the Hybrid Intelligence System.
"""

from core.interfaces.base_module import BaseModule, Intent, ModuleResponse
from core.cognitive.hybrid_intelligence import HybridIntelligenceSystem

class CognitiveModule(BaseModule):
    def __init__(self):
        super().__init__(name="cognitive")
        self.hybrid_intelligence_system = HybridIntelligenceSystem()

    def execute(self, intent: Intent, context: dict) -> ModuleResponse:
        """
        Executes the given intent using the Hybrid Intelligence System.
        """
        input_data = intent.text
        response = self.hybrid_intelligence_system.reason(input_data)
        return ModuleResponse(success=True, message=response)
