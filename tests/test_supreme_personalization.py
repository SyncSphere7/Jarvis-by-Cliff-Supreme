"""
Tests for Supreme Personalization Engine
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, AsyncMock

from core.supreme.supreme_personalization import (
    SupremePersonalizationEngine,
    PersonalityEngine,
    PreferenceManager,
    PersonalityTrait,
    CommunicationStyle,
    LearningPreference,
    InteractionMode,
    UserPreferences
)

from core.supreme.supreme_control_interface import SupremeControlInterface


class TestPersonalityEngine:
    """Test PersonalityEngine functionality"""
    
    @pytest.fixture
    def personality_engine(self):
        return PersonalityEngine()
    
    @pytest.fixture
    def sample_preferences(self):
        return UserPreferences(
            user_id="test_user",
            personality_traits={
                PersonalityTrait.ANALYTICAL: 0.8,
                PersonalityTrait.CREATIVE: 0.6,
                PersonalityTrait.EMPATHETIC: 0.7
            },
            communication_style=CommunicationStyle.CONVERSATIONAL,
            learning_preferences=[LearningPreference.VISUAL],
            interaction_mode=InteractionMode.BALANCED,
            preferred_engines=["reasoning", "analytics"],
            response_complexity="detailed",
            risk_tolerance=0.5,
            privacy_level="medium",
            notification_preferences={},
            customization_level="basic"
        )
    
    def test_personality_engine_initialization(self, personality_engine):
        """Test PersonalityEngine initialization"""
        assert isinstance(personality_engine.personality_profiles, dict)
        assert isinstance(personality_engine.adaptation_history, list)
        assert len(personality_engine.personality_profiles) == 0
    
    def test_get_personality_profile(self, personality_engine, sample_preferences):
        """Test personality profile creation and retrieval"""
        user_id = "test_user"
        
        # First call should create profile
        profile = personality_engine.get_personality_profile(user_id, sample_preferences)
        
        assert isinstance(profile, dict)
        assert len(profile) == len(PersonalityTrait)
        assert profile[PersonalityTrait.ANALYTICAL] == 0.8
        assert profile[PersonalityTrait.CREATIVE] == 0.6
        assert profile[PersonalityTrait.EMPATHETIC] == 0.7
        
        # Missing traits should have default values
        assert profile[PersonalityTrait.PRACTICAL] == 0.5
        
        # Second call should return same profile
        profile2 = personality_engine.get_personality_profile(user_id, sample_preferences)
        assert profile == profile2
    
    def test_adapt_personality(self, personality_engine, sample_preferences):
        """Test personality adaptation"""
        user_id = "test_user"
        
        # Create initial profile
        initial_profile = personality_engine.get_personality_profile(user_id, sample_preferences)
        initial_analytical = initial_profile[PersonalityTrait.ANALYTICAL]
        
        # Provide positive feedback
        feedback = {"satisfaction": 0.8, "response_type": "analytical"}
        adapted_profile = personality_engine.adapt_personality(user_id, feedback)
        
        # Profile should be slightly adjusted
        assert isinstance(adapted_profile, dict)
        assert adapted_profile[PersonalityTrait.ANALYTICAL] >= initial_analytical


class TestPreferenceManager:
    """Test PreferenceManager functionality"""
    
    @pytest.fixture
    def preference_manager(self):
        return PreferenceManager()
    
    def test_preference_manager_initialization(self, preference_manager):
        """Test PreferenceManager initialization"""
        assert isinstance(preference_manager.user_preferences, dict)
        assert len(preference_manager.user_preferences) == 0
    
    def test_get_user_preferences_new_user(self, preference_manager):
        """Test getting preferences for new user"""
        user_id = "new_user"
        
        preferences = preference_manager.get_user_preferences(user_id)
        
        assert isinstance(preferences, UserPreferences)
        assert preferences.user_id == user_id
        assert preferences.communication_style == CommunicationStyle.CONVERSATIONAL
        assert preferences.response_complexity == "detailed"
        assert preferences.risk_tolerance == 0.5
        assert preferences.privacy_level == "medium"
        
        # Should be stored for future retrieval
        assert user_id in preference_manager.user_preferences
    
    def test_get_user_preferences_existing_user(self, preference_manager):
        """Test getting preferences for existing user"""
        user_id = "existing_user"
        
        # First call creates preferences
        preferences1 = preference_manager.get_user_preferences(user_id)
        
        # Second call should return same preferences
        preferences2 = preference_manager.get_user_preferences(user_id)
        
        assert preferences1 == preferences2
        assert preferences1 is preferences2


class TestSupremePersonalizationEngine:
    """Test SupremePersonalizationEngine functionality"""
    
    @pytest.fixture
    def mock_interface(self):
        interface = Mock(spec=SupremeControlInterface)
        interface.execute_command = AsyncMock()
        interface.execute_command.return_value = Mock(result={"status": "success"})
        return interface
    
    @pytest.fixture
    def personalization_engine(self, mock_interface):
        return SupremePersonalizationEngine(mock_interface)
    
    def test_personalization_engine_initialization(self, personalization_engine, mock_interface):
        """Test SupremePersonalizationEngine initialization"""
        assert personalization_engine.control_interface == mock_interface
        assert isinstance(personalization_engine.personality_engine, PersonalityEngine)
        assert isinstance(personalization_engine.preference_manager, PreferenceManager)
        assert isinstance(personalization_engine.personalization_history, list)
    
    @pytest.mark.asyncio
    async def test_personalize_interaction(self, personalization_engine):
        """Test interaction personalization"""
        user_id = "test_user"
        request = {"query": "How can I improve my productivity?"}
        
        result = await personalization_engine.personalize_interaction(user_id, request)
        
        assert isinstance(result, dict)
        assert "personalized_request" in result
        assert "personalization_applied" in result
        assert result["personalization_applied"] is True
        
        personalized_request = result["personalized_request"]
        assert "response_format" in personalized_request
        assert "complexity" in personalized_request
        assert "preferred_engines" in personalized_request
        
        # Original request should be preserved
        assert personalized_request["query"] == request["query"]
    
    def test_get_response_format(self, personalization_engine):
        """Test response format mapping"""
        # Test different communication styles
        assert personalization_engine._get_response_format(CommunicationStyle.FORMAL) == "structured"
        assert personalization_engine._get_response_format(CommunicationStyle.CASUAL) == "conversational"
        assert personalization_engine._get_response_format(CommunicationStyle.TECHNICAL) == "detailed"
        assert personalization_engine._get_response_format(CommunicationStyle.CONCISE) == "summary"
    
    @pytest.mark.asyncio
    async def test_learn_from_feedback(self, personalization_engine):
        """Test learning from user feedback"""
        user_id = "test_user"
        interaction_data = {
            "satisfaction": 0.8,
            "response_type": "analytical",
            "preferred_detail_level": "high"
        }
        
        result = await personalization_engine.learn_from_feedback(user_id, interaction_data)
        
        assert isinstance(result, dict)
        assert "learning_applied" in result
        assert result["learning_applied"] is True
        assert "timestamp" in result
        
        # Should be added to history
        assert len(personalization_engine.personalization_history) == 1
        assert personalization_engine.personalization_history[0]["user_id"] == user_id
    
    def test_get_personalization_summary(self, personalization_engine):
        """Test getting personalization summary"""
        user_id = "test_user"
        
        summary = personalization_engine.get_personalization_summary(user_id)
        
        assert isinstance(summary, dict)
        assert "user_id" in summary
        assert summary["user_id"] == user_id
        assert "communication_style" in summary
        assert "learning_preferences" in summary
        assert "interaction_mode" in summary
        assert "response_complexity" in summary
        assert "risk_tolerance" in summary
        assert "privacy_level" in summary
        assert "personality_traits" in summary
        assert "last_updated" in summary


if __name__ == "__main__":
    pytest.main([__file__])