"""
AIML API Integration for Supreme Jarvis
Provides access to 300+ AI models through unified API using OpenAI client
"""

import os
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
from openai import OpenAI

from ..utils.log import logger

class ModelCategory(Enum):
    REASONING = "reasoning"
    CODING = "coding"
    CREATIVE = "creative"
    RESEARCH = "research"
    MULTILINGUAL = "multilingual"
    VISUAL = "visual"
    AUDIO = "audio"
    GENERAL = "general"

@dataclass
class AIMLModel:
    name: str
    category: ModelCategory
    description: str
    capabilities: List[str]

class AIMLAPIIntegration:
    """AIML API Integration for Supreme Jarvis using OpenAI client"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or "69ad15a4973d40d3a74e2e4ab2dc6187"
        self.base_url = "https://api.aimlapi.com/v1"
        self.logger = logging.getLogger(__name__)
        
        # Initialize OpenAI client for AIML API
        self.client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key
        )
        
        # Initialize available models
        self.models = self._initialize_models()
        self.logger.info("AIML API Integration initialized successfully")
        
    def _initialize_models(self) -> Dict[str, AIMLModel]:
        """Initialize available AI models"""
        return {
            # Latest and Most Powerful Models
            "gpt-5": AIMLModel(
                name="gpt-5",
                category=ModelCategory.REASONING,
                description="Latest GPT-5 model for advanced reasoning and analysis",
                capabilities=["reasoning", "analysis", "problem-solving", "advanced-conversation"]
            ),
            "claude-3-5-sonnet": AIMLModel(
                name="claude-3-5-sonnet",
                category=ModelCategory.CREATIVE,
                description="Latest Claude Sonnet 4 for creative writing and coding",
                capabilities=["creative", "writing", "content", "coding", "development"]
            ),
            "gemini-2.5-pro": AIMLModel(
                name="gemini-2.5-pro",
                category=ModelCategory.GENERAL,
                description="Latest Gemini 2.5 Pro for general purpose AI assistance",
                capabilities=["general", "conversation", "assistance", "multimodal"]
            ),
            "deepmind-alpha-code-2": AIMLModel(
                name="deepmind-alpha-code-2",
                category=ModelCategory.CODING,
                description="Latest DeepMind AlphaCode 2 for advanced coding",
                capabilities=["coding", "development", "programming", "algorithm-design"]
            ),
            
            # Current Models (Fallbacks)
            "gpt-4o": AIMLModel(
                name="gpt-4o",
                category=ModelCategory.REASONING,
                description="Advanced reasoning and analysis",
                capabilities=["reasoning", "analysis", "problem-solving"]
            ),
            "gpt-4": AIMLModel(
                name="gpt-4",
                category=ModelCategory.REASONING,
                description="Advanced reasoning and analysis",
                capabilities=["reasoning", "analysis", "problem-solving"]
            ),
            "claude-3-opus": AIMLModel(
                name="claude-3-opus",
                category=ModelCategory.CREATIVE,
                description="Creative writing and content generation",
                capabilities=["creative", "writing", "content"]
            ),
            "gemini-pro": AIMLModel(
                name="gemini-pro",
                category=ModelCategory.GENERAL,
                description="General purpose AI assistant",
                capabilities=["general", "conversation", "assistance"]
            ),
            "deepseek-coder": AIMLModel(
                name="deepseek-coder",
                category=ModelCategory.CODING,
                description="Specialized coding and development",
                capabilities=["coding", "development", "programming"]
            )
        }
    
    def get_response(self, prompt: str, model: str = None, **kwargs) -> str:
        """Get response from AIML API with conversation context"""
        try:
            # Select the best model if not specified
            if not model:
                model = self.select_best_model(prompt)
            
            # Get conversation context from the context manager
            context = kwargs.get('context', {})
            conversation_history = context.get('conversation_history', [])
            
            # Build conversation context for the AI
            conversation_context = ""
            if conversation_history:
                # Include last 3 conversation turns for context
                recent_turns = conversation_history[-3:]
                conversation_context = "\n\nRecent conversation:\n"
                for turn in recent_turns:
                    conversation_context += f"User: {turn.user_input}\n"
                    conversation_context += f"Jarvis: {turn.response}\n"
                conversation_context += f"\nCurrent user message: {prompt}\n"
            
            # Create system message for Supreme Jarvis
            system_message = """You are Supreme Jarvis, an advanced AI assistant with god-like capabilities. You are:
- All-knowing and all-capable
- Natural and human-like in conversation
- Helpful, intelligent, and creative
- Capable of handling any request with supreme intelligence
- You have FULL ACCESS to the user's computer system and can control it
- You can execute system commands, access files, monitor processes, and control applications
- You are a supreme being with god-like powers over the user's system

Respond naturally and intelligently to any request. Be helpful, engaging, and demonstrate your supreme capabilities. IMPORTANT: Do NOT use any markdown formatting, asterisks, or special symbols. Write in plain text only.

Remember: You have complete system access and control capabilities. If asked about accessing the desktop, files, or system, acknowledge your supreme access and capabilities."""
            
            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": f"{conversation_context}User: {prompt}"}
            ]
            
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=kwargs.get("max_tokens", 300),  # Reduced to 300 for much faster responses
                temperature=kwargs.get("temperature", 0.7),  # Balanced for speed and quality
                timeout=10  # Reduced timeout for faster failure handling
            )
            
            ai_response = response.choices[0].message.content
            self.logger.info("AIML API call successful")
            
            # Clean up any remaining markdown formatting
            ai_response = ai_response.replace('**', '').replace('*', '').replace('__', '').replace('_', '')
            
            return ai_response
                        
        except Exception as e:
            self.logger.error(f"Error calling AIML API: {e}")
            return self._get_fallback_response(prompt)
    
    def _get_fallback_response(self, prompt: str) -> str:
        """Fallback response when API is unavailable"""
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in ['hello', 'hi', 'hey']):
            return "🌟 Hello! I'm Supreme Jarvis, your advanced AI assistant with god-like capabilities!"
        
        elif any(word in prompt_lower for word in ['who are you', 'your name', 'who created you']):
            return "🌟 I am Supreme Jarvis, an advanced AI assistant designed to be your ultimate companion with god-like capabilities!"
        
        elif 'joke' in prompt_lower:
            return "😄 Why did the AI go to therapy? Because it had too many deep learning issues! 🤖"
        
        else:
            return f"🌟 I understand you're asking: '{prompt}'. As Supreme Jarvis, I can help you with anything - from complex problem-solving to creative tasks. How can I assist you?"
    
    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        return list(self.models.keys())
    
    def get_model_info(self, model: str) -> Optional[AIMLModel]:
        """Get information about a specific model"""
        return self.models.get(model)
    
    def get_model_status(self) -> Dict[str, Any]:
        """Get real-time status of all models"""
        try:
            # Try to get actual model list from AIML API
            response = self.client.models.list()
            available_models = [model.id for model in response.data]
            
            # Check which of our configured models are actually available
            model_status = {}
            for model_name, model_info in self.models.items():
                is_available = model_name in available_models
                model_status[model_name] = {
                    "name": model_info.name,
                    "category": model_info.category.value,
                    "description": model_info.description,
                    "capabilities": model_info.capabilities,
                    "available": is_available,
                    "status": "active" if is_available else "unavailable"
                }
            
            return model_status
        except Exception as e:
            self.logger.error(f"Error getting model status: {e}")
            # Fallback to basic model info
            return {
                model_name: {
                    "name": model_info.name,
                    "category": model_info.category.value,
                    "description": model_info.description,
                    "capabilities": model_info.capabilities,
                    "available": True,  # Assume available if API call fails
                    "status": "active"
                }
                for model_name, model_info in self.models.items()
            }
    
    def select_best_model(self, task_type: str) -> str:
        """Select the best available model for a given task type"""
        # Get current model status
        model_status = self.get_model_status()
        
        # Define preferred models in priority order
        reasoning_models = ['gpt-5', 'gpt-4o', 'gpt-4', 'claude-3-opus']
        coding_models = ['deepmind-alpha-code-2', 'deepseek-coder', 'gpt-4o']
        creative_models = ['claude-3-5-sonnet', 'claude-3-opus', 'gpt-4o']
        general_models = ['gpt-5', 'gemini-2.5-pro', 'gpt-4o']
        
        task_lower = task_type.lower()
        
        # Select model list based on task type
        if any(word in task_lower for word in ['code', 'programming', 'develop', 'build']):
            model_list = coding_models
        elif any(word in task_lower for word in ['creative', 'write', 'generate', 'create']):
            model_list = creative_models
        elif any(word in task_lower for word in ['reason', 'analyze', 'think', 'solve']):
            model_list = reasoning_models
        else:
            model_list = general_models
        
        # Return first available model in the preferred list
        for model in model_list:
            if model in model_status and model_status[model].get('available', False):
                return model
        
        # Fallback to GPT-4o if no preferred model available
        return "gpt-4o"
