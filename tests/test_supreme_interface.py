"""
Tests for Supreme Interface
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock

from core.supreme.supreme_interface import (
    SupremeInterface,
    CommandParser,
    VoiceProcessor,
    GestureProcessor,
    StatusMonitor,
    InteractionMode,
    InterfaceTheme,
    CommandComplexity,
    UserPreferences,
    InteractionSession,
    InterfaceCommand,
    InterfaceResponse
)

from core.supreme.supreme_control_interface import SupremeControlInterface, SupremeCommandResult
from core.supreme.supreme_decision_engine import SupremeDecisionEngine


class MockControlInterface:
    """Mock control interface for testing"""
    
    def __init__(self):
        self.is_initialized = True
    
    async def initialize(self):
        return True
    
    async def shutdown(self):
        return True
    
    async def execute_command(self, command):
        return SupremeCommandResult(
            command_id=command.command_id,
            status="completed",
            result={"message": "Mock command executed successfully"},
            execution_time=0.1,
            engines_used=["mock_engine"]
        )
    
    def get_interface_status(self):
        return {
            "is_initialized": True,
            "orchestrator_status": {"is_running": True},
            "engine_status": {"mock_engine": {"status": "active"}}
        }
    
    def get_performance_metrics(self):
        return {
            "total_commands": 10,
            "success_rate": 95.0,
            "average_execution_time": 0.5
        }
    
    def get_command_history(self, limit=10):
        return [
            {"operation": "analyze", "timestamp": datetime.now().isoformat()},
            {"operation": "optimize", "timestamp": datetime.now().isoformat()}
        ]


class MockDecisionEngine:
    """Mock decision engine for testing"""
    
    def __init__(self):
        self.is_running = True
    
    async def initialize(self):
        return True
    
    async def shutdown(self):
        return True


class TestCommandParser:
    """Test CommandParser functionality"""
    
    @pytest.fixture
    def parser(self):
        return CommandParser()
    
    @pytest.mark.asyncio
    async def test_parse_analyze_command(self, parser):
        """Test parsing analyze command"""
        result = await parser.parse_command(
            "analyze system performance", 
            InteractionMode.TEXT, 
            {}
        )
        
        assert result["command_type"] == "analyze"
        assert result["confidence"] > 0
        assert "system" in result["entities"]
        assert "performance" in result["entities"]
    
    @pytest.mark.asyncio
    async def test_parse_optimize_command(self, parser):
        """Test parsing optimize command"""
        result = await parser.parse_command(
            "optimize database queries for better performance", 
            InteractionMode.TEXT, 
            {}
        )
        
        assert result["command_type"] == "optimize"
        assert result["confidence"] > 0
        assert "performance" in result["entities"]
    
    @pytest.mark.asyncio
    async def test_parse_information_request(self, parser):
        """Test parsing information request"""
        result = await parser.parse_command(
            "what is the current system status", 
            InteractionMode.TEXT, 
            {}
        )
        
        assert result["intent"] == "information_request"
        assert "system" in result["entities"]
    
    @pytest.mark.asyncio
    async def test_parse_unclear_command(self, parser):
        """Test parsing unclear command"""
        result = await parser.parse_command(
            "do something", 
            InteractionMode.TEXT, 
            {}
        )
        
        assert result["confidence"] < 0.6
        assert len(result["suggestions"]) > 0
    
    @pytest.mark.asyncio
    async def test_extract_parameters(self, parser):
        """Test parameter extraction"""
        result = await parser.parse_command(
            'analyze "user data" for the last 30 days', 
            InteractionMode.TEXT, 
            {}
        )
        
        assert "quoted_text" in result["parameters"]
        assert "user data" in result["parameters"]["quoted_text"]
        assert "numbers" in result["parameters"]
        assert 30.0 in result["parameters"]["numbers"]


class TestVoiceProcessor:
    """Test VoiceProcessor functionality"""
    
    @pytest.fixture
    def voice_processor(self):
        return VoiceProcessor()
    
    @pytest.mark.asyncio
    async def test_process_voice_input_disabled(self, voice_processor):
        """Test voice input processing when disabled"""
        result = await voice_processor.process_voice_input(b"audio_data")
        assert "not available" in result.lower()
    
    @pytest.mark.asyncio
    async def test_process_voice_input_enabled(self, voice_processor):
        """Test voice input processing when enabled"""
        voice_processor.enable_speech_recognition()
        result = await voice_processor.process_voice_input(b"audio_data")
        assert isinstance(result, str)
        assert len(result) > 0
    
    @pytest.mark.asyncio
    async def test_synthesize_speech_disabled(self, voice_processor):
        """Test speech synthesis when disabled"""
        result = await voice_processor.synthesize_speech("Hello world")
        assert result == b""
    
    @pytest.mark.asyncio
    async def test_synthesize_speech_enabled(self, voice_processor):
        """Test speech synthesis when enabled"""
        voice_processor.enable_text_to_speech()
        result = await voice_processor.synthesize_speech("Hello world")
        assert isinstance(result, bytes)
    
    def test_configure_voice_settings(self, voice_processor):
        """Test voice settings configuration"""
        settings = {"language": "es-ES", "speed": 1.2}
        voice_processor.configure_voice_settings(settings)
        
        assert voice_processor.voice_settings["language"] == "es-ES"
        assert voice_processor.voice_settings["speed"] == 1.2
    
    def test_enable_disable_features(self, voice_processor):
        """Test enabling and disabling voice features"""
        # Test speech recognition
        voice_processor.enable_speech_recognition()
        assert voice_processor.speech_recognition_active
        
        voice_processor.disable_speech_recognition()
        assert not voice_processor.speech_recognition_active
        
        # Test text-to-speech
        voice_processor.enable_text_to_speech()
        assert voice_processor.text_to_speech_active
        
        voice_processor.disable_text_to_speech()
        assert not voice_processor.text_to_speech_active


class TestGestureProcessor:
    """Test GestureProcessor functionality"""
    
    @pytest.fixture
    def gesture_processor(self):
        return GestureProcessor()
    
    @pytest.mark.asyncio
    async def test_process_gesture_disabled(self, gesture_processor):
        """Test gesture processing when disabled"""
        result = await gesture_processor.process_gesture_input({"type": "swipe_left"})
        assert "not available" in result.lower()
    
    @pytest.mark.asyncio
    async def test_process_gesture_enabled(self, gesture_processor):
        """Test gesture processing when enabled"""
        gesture_processor.enable_gesture_recognition()
        result = await gesture_processor.process_gesture_input({"type": "swipe_left"})
        assert result == "gesture_previous"
    
    @pytest.mark.asyncio
    async def test_process_unknown_gesture(self, gesture_processor):
        """Test processing unknown gesture"""
        gesture_processor.enable_gesture_recognition()
        result = await gesture_processor.process_gesture_input({"type": "unknown_gesture"})
        assert "unknown_gesture" in result
    
    def test_add_remove_gesture_pattern(self, gesture_processor):
        """Test adding and removing gesture patterns"""
        # Add custom pattern
        gesture_processor.add_gesture_pattern("custom_gesture", "custom_command")
        assert "custom_gesture" in gesture_processor.gesture_patterns
        
        # Remove pattern
        gesture_processor.remove_gesture_pattern("custom_gesture")
        assert "custom_gesture" not in gesture_processor.gesture_patterns


class TestStatusMonitor:
    """Test StatusMonitor functionality"""
    
    @pytest.fixture
    def control_interface(self):
        return MockControlInterface()
    
    @pytest.fixture
    def status_monitor(self, control_interface):
        return StatusMonitor(control_interface)
    
    @pytest.mark.asyncio
    async def test_get_system_status(self, status_monitor):
        """Test getting system status"""
        status = await status_monitor.get_system_status()
        
        assert isinstance(status, dict)
        assert "timestamp" in status
        assert "overall_health" in status
        assert "engines" in status
        assert "performance" in status
        assert "resources" in status
        assert "security" in status
    
    @pytest.mark.asyncio
    async def test_status_caching(self, status_monitor):
        """Test status caching functionality"""
        # First call
        status1 = await status_monitor.get_system_status()
        
        # Second call (should use cache)
        status2 = await status_monitor.get_system_status()
        
        assert status1["timestamp"] == status2["timestamp"]
    
    def test_cache_management(self, status_monitor):
        """Test cache management"""
        # Add to cache
        status_monitor.status_cache["test"] = {"data": "test"}
        status_monitor.cache_expiry["test"] = datetime.now() + timedelta(seconds=30)
        
        # Check cache validity
        assert status_monitor._is_cache_valid("test")
        
        # Clear cache
        status_monitor.clear_cache()
        assert len(status_monitor.status_cache) == 0
        assert len(status_monitor.cache_expiry) == 0
    
    def test_enable_disable_monitoring(self, status_monitor):
        """Test enabling and disabling monitoring"""
        status_monitor.enable_monitoring()
        assert status_monitor.monitoring_active
        
        status_monitor.disable_monitoring()
        assert not status_monitor.monitoring_active


class TestSupremeInterface:
    """Test SupremeInterface functionality"""
    
    @pytest.fixture
    def control_interface(self):
        return MockControlInterface()
    
    @pytest.fixture
    def decision_engine(self):
        return MockDecisionEngine()
    
    @pytest.fixture
    def supreme_interface(self, control_interface, decision_engine):
        return SupremeInterface(control_interface, decision_engine)
    
    def test_interface_initialization(self, supreme_interface):
        """Test SupremeInterface initialization"""
        assert isinstance(supreme_interface.command_parser, CommandParser)
        assert isinstance(supreme_interface.voice_processor, VoiceProcessor)
        assert isinstance(supreme_interface.gesture_processor, GestureProcessor)
        assert isinstance(supreme_interface.status_monitor, StatusMonitor)
        assert isinstance(supreme_interface.active_sessions, dict)
        assert isinstance(supreme_interface.user_preferences, dict)
        assert not supreme_interface.is_initialized
    
    @pytest.mark.asyncio
    async def test_initialize_shutdown(self, supreme_interface):
        """Test interface initialization and shutdown"""
        # Initialize
        result = await supreme_interface.initialize()
        assert result is True
        assert supreme_interface.is_initialized is True
        
        # Shutdown
        result = await supreme_interface.shutdown()
        assert result is True
        assert supreme_interface.is_initialized is False
    
    @pytest.mark.asyncio
    async def test_session_management(self, supreme_interface):
        """Test session creation and management"""
        await supreme_interface.initialize()
        
        # Create session
        session_id = await supreme_interface.create_session("test_user", InteractionMode.TEXT)
        assert session_id
        assert session_id in supreme_interface.active_sessions
        
        # Get session info
        session_info = supreme_interface.get_session_info(session_id)
        assert session_info is not None
        assert session_info["user_id"] == "test_user"
        assert session_info["interaction_mode"] == "text"
        
        # End session
        result = await supreme_interface.end_session(session_id)
        assert result is True
        assert session_id not in supreme_interface.active_sessions
        
        await supreme_interface.shutdown()
    
    @pytest.mark.asyncio
    async def test_process_text_interaction(self, supreme_interface):
        """Test processing text interaction"""
        await supreme_interface.initialize()
        
        # Create session
        session_id = await supreme_interface.create_session("test_user")
        
        # Process interaction
        response = await supreme_interface.process_interaction(
            session_id, "analyze system performance", InteractionMode.TEXT
        )
        
        assert isinstance(response, InterfaceResponse)
        assert response.success
        assert response.execution_time > 0
        assert len(response.suggestions) >= 0
        
        await supreme_interface.shutdown()
    
    @pytest.mark.asyncio
    async def test_process_help_request(self, supreme_interface):
        """Test processing help request"""
        await supreme_interface.initialize()
        
        session_id = await supreme_interface.create_session("test_user")
        response = await supreme_interface.process_interaction(
            session_id, "help", InteractionMode.TEXT
        )
        
        assert response.success
        assert isinstance(response.content, dict)
        assert "help_topics" in response.content
        assert "examples" in response.content
        
        await supreme_interface.shutdown()
    
    @pytest.mark.asyncio
    async def test_process_status_request(self, supreme_interface):
        """Test processing status request"""
        await supreme_interface.initialize()
        
        session_id = await supreme_interface.create_session("test_user")
        response = await supreme_interface.process_interaction(
            session_id, "show system status", InteractionMode.TEXT
        )
        
        assert response.success
        assert isinstance(response.content, dict)
        assert "timestamp" in response.content
        
        await supreme_interface.shutdown()
    
    def test_user_preferences_management(self, supreme_interface):
        """Test user preferences management"""
        user_id = "test_user"
        
        # Get initial preferences (should create default)
        prefs = supreme_interface.get_user_preferences(user_id)
        assert prefs is None  # Not created yet
        
        # Update preferences
        result = supreme_interface.update_user_preferences(user_id, {
            "interaction_mode": "voice",
            "interface_theme": "dark",
            "command_complexity": "advanced"
        })
        assert result is True
        
        # Get updated preferences
        prefs = supreme_interface.get_user_preferences(user_id)
        assert prefs is not None
        assert prefs.interaction_mode == InteractionMode.VOICE
        assert prefs.interface_theme == InterfaceTheme.DARK
        assert prefs.command_complexity == CommandComplexity.ADVANCED
    
    def test_get_interface_status(self, supreme_interface):
        """Test getting interface status"""
        status = supreme_interface.get_interface_status()
        
        assert isinstance(status, dict)
        assert "is_initialized" in status
        assert "active_sessions" in status
        assert "supported_modes" in status
        assert "metrics" in status
        assert "components" in status
        
        # Check components status
        components = status["components"]
        assert "voice_processor" in components
        assert "gesture_processor" in components
        assert "status_monitor" in components
    
    def test_event_handler_management(self, supreme_interface):
        """Test event handler management"""
        # Mock event handler
        def mock_handler(event_data):
            pass
        
        # Add event handler
        supreme_interface.add_event_handler("test_event", mock_handler)
        assert "test_event" in supreme_interface.event_handlers
        assert mock_handler in supreme_interface.event_handlers["test_event"]
        
        # Remove event handler
        supreme_interface.remove_event_handler("test_event", mock_handler)
        assert mock_handler not in supreme_interface.event_handlers.get("test_event", [])
    
    @pytest.mark.asyncio
    async def test_error_handling(self, supreme_interface):
        """Test error handling in interface"""
        # Test interaction without initialization
        response = await supreme_interface.process_interaction(
            "invalid_session", "test command", InteractionMode.TEXT
        )
        assert not response.success
        assert "not initialized" in response.content.lower()
        
        # Test invalid session
        await supreme_interface.initialize()
        response = await supreme_interface.process_interaction(
            "invalid_session", "test command", InteractionMode.TEXT
        )
        assert not response.success
        assert "invalid session" in response.content.lower()
        
        await supreme_interface.shutdown()


if __name__ == "__main__":
    pytest.main([__file__])