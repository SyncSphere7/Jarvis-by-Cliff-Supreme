"""
Tests for Supreme Communication Engine
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, patch

from core.supreme.engines.communication_engine import (
    SupremeCommunicationEngine,
    SupremeCommunicator,
    UniversalTranslator,
    ContentCreator,
    CommunicationType,
    ContentStyle,
    CommunicationRequest
)
from core.supreme.base_supreme_engine import SupremeRequest

class TestUniversalTranslator:
    """Test cases for UniversalTranslator"""
    
    @pytest.fixture
    def translator(self):
        config = {"translation": {}}
        return UniversalTranslator(config)
    
    @pytest.mark.asyncio
    async def test_translate_text(self, translator):
        """Test text translation"""
        result = await translator.translate("Hello", "es")
        
        assert result["original_text"] == "Hello"
        assert result["target_language"] == "es"
        assert result["translated_text"] == "[ES] Hello"
        assert result["confidence_score"] == 0.85
    
    @pytest.mark.asyncio
    async def test_translate_with_cache(self, translator):
        """Test translation caching"""
        # First translation
        result1 = await translator.translate("Hello", "es")
        
        # Second translation (should use cache)
        result2 = await translator.translate("Hello", "es")
        
        assert result1 == result2
        assert len(translator.translation_cache) == 1
    
    @pytest.mark.asyncio
    async def test_detect_language(self, translator):
        """Test language detection"""
        result = await translator.detect_language("Hello world")
        
        assert result["language_code"] == "en"
        assert result["language_name"] == "English"
        assert result["confidence"] == 0.85

class TestContentCreator:
    """Test cases for ContentCreator"""
    
    @pytest.fixture
    def content_creator(self):
        config = {"content": {}}
        return ContentCreator(config)
    
    @pytest.mark.asyncio
    async def test_enhance_content_formal(self, content_creator):
        """Test formal content enhancement"""
        content = "I can't believe this won't work"
        enhanced = await content_creator.enhance_content(
            content,
            CommunicationType.EMAIL,
            ContentStyle.FORMAL,
            {}
        )
        
        assert "cannot" in enhanced
        assert "will not" in enhanced
        assert enhanced.startswith("Dear Recipient,")
        assert enhanced.endswith("Best regards,")
    
    @pytest.mark.asyncio
    async def test_enhance_content_casual(self, content_creator):
        """Test casual content enhancement"""
        content = "I cannot believe this will not work"
        enhanced = await content_creator.enhance_content(
            content,
            CommunicationType.CHAT,
            ContentStyle.CASUAL,
            {}
        )
        
        assert "can't" in enhanced
        assert "won't" in enhanced
    
    @pytest.mark.asyncio
    async def test_enhance_content_sms(self, content_creator):
        """Test SMS content enhancement"""
        long_content = "This is a very long message that exceeds the SMS character limit of 160 characters and should be truncated to fit within the limit. This additional text makes it longer than 160 characters."
        enhanced = await content_creator.enhance_content(
            long_content,
            CommunicationType.SMS,
            ContentStyle.CASUAL,
            {}
        )
        
        assert len(enhanced) <= 160
        if len(long_content) > 160:
            assert enhanced.endswith("...")
    
    @pytest.mark.asyncio
    async def test_enhance_content_with_context(self, content_creator):
        """Test content enhancement with context"""
        content = "Hello {name}, your order {order_id} is ready"
        context = {"name": "John", "order_id": "12345"}
        
        enhanced = await content_creator.enhance_content(
            content,
            CommunicationType.EMAIL,
            ContentStyle.PROFESSIONAL,
            context
        )
        
        assert "John" in enhanced
        assert "12345" in enhanced
        assert "{name}" not in enhanced
        assert "{order_id}" not in enhanced
    
    @pytest.mark.asyncio
    async def test_generate_content(self, content_creator):
        """Test content generation"""
        prompt = "Write a welcome message"
        context = {"recipient": "John", "sender": "Jane"}
        
        generated = await content_creator.generate_content(
            prompt,
            CommunicationType.EMAIL,
            ContentStyle.PROFESSIONAL,
            context
        )
        
        assert len(generated) > 0
        assert "John" in generated or "Jane" in generated

class TestSupremeCommunicator:
    """Test cases for SupremeCommunicator"""
    
    @pytest.fixture
    def communicator(self):
        config = {
            "translation": {},
            "content": {}
        }
        return SupremeCommunicator(config)
    
    @pytest.mark.asyncio
    async def test_process_communication_basic(self, communicator):
        """Test basic communication processing"""
        request = CommunicationRequest(
            request_id="test_001",
            communication_type=CommunicationType.EMAIL,
            content="Hello world",
            style=ContentStyle.PROFESSIONAL
        )
        
        result = await communicator.process_communication(request)
        
        assert result["request_id"] == "test_001"
        assert result["communication_type"] == "email"
        assert result["original_content"] == "Hello world"
        assert "enhanced_content" in result
        assert "processing_time" in result
    
    @pytest.mark.asyncio
    async def test_process_communication_with_translation(self, communicator):
        """Test communication processing with translation"""
        request = CommunicationRequest(
            request_id="test_002",
            communication_type=CommunicationType.EMAIL,
            content="Hello world",
            target_language="es",
            style=ContentStyle.PROFESSIONAL
        )
        
        result = await communicator.process_communication(request)
        
        assert "translation" in result
        assert result["translation"]["target_language"] == "es"
        assert "[ES]" in result["processed_content"]
    
    @pytest.mark.asyncio
    async def test_metrics_update(self, communicator):
        """Test metrics updating"""
        initial_count = communicator.metrics["total_communications"]
        
        request = CommunicationRequest(
            request_id="test_003",
            communication_type=CommunicationType.CHAT,
            content="Test message"
        )
        
        await communicator.process_communication(request)
        
        assert communicator.metrics["total_communications"] == initial_count + 1
        assert communicator.metrics["content_generations"] == 1

class TestSupremeCommunicationEngine:
    """Test cases for SupremeCommunicationEngine"""
    
    @pytest.fixture
    def engine(self):
        config = Mock()
        config.communication_config = {
            "translation": {},
            "content": {}
        }
        return SupremeCommunicationEngine("test_comm_engine", config)
    
    @pytest.mark.asyncio
    async def test_engine_initialization(self, engine):
        """Test engine initialization"""
        result = await engine._initialize_engine()
        assert result is True
    
    @pytest.mark.asyncio
    async def test_translate_text_operation(self, engine):
        """Test translate text operation"""
        await engine._initialize_engine()
        
        request = SupremeRequest(
            request_id="test_001",
            operation="translate_text",
            parameters={
                "text": "Hello world",
                "target_language": "es"
            }
        )
        
        result = await engine._execute_operation(request)
        
        assert result["operation"] == "translate_text"
        assert result["success"] is True
        assert "translation" in result
    
    @pytest.mark.asyncio
    async def test_detect_language_operation(self, engine):
        """Test detect language operation"""
        await engine._initialize_engine()
        
        request = SupremeRequest(
            request_id="test_002",
            operation="detect_language",
            parameters={"text": "Hello world"}
        )
        
        result = await engine._execute_operation(request)
        
        assert result["operation"] == "detect_language"
        assert result["success"] is True
        assert "detection" in result
    
    @pytest.mark.asyncio
    async def test_enhance_content_operation(self, engine):
        """Test enhance content operation"""
        await engine._initialize_engine()
        
        request = SupremeRequest(
            request_id="test_003",
            operation="enhance_content",
            parameters={
                "content": "Hello world",
                "communication_type": "email",
                "style": "formal"
            }
        )
        
        result = await engine._execute_operation(request)
        
        assert result["operation"] == "enhance_content"
        assert result["success"] is True
        assert result["original_content"] == "Hello world"
        assert "enhanced_content" in result
    
    @pytest.mark.asyncio
    async def test_generate_content_operation(self, engine):
        """Test generate content operation"""
        await engine._initialize_engine()
        
        request = SupremeRequest(
            request_id="test_004",
            operation="generate_content",
            parameters={
                "prompt": "Write a welcome message",
                "communication_type": "email",
                "style": "professional"
            }
        )
        
        result = await engine._execute_operation(request)
        
        assert result["operation"] == "generate_content"
        assert result["success"] is True
        assert result["prompt"] == "Write a welcome message"
        assert "generated_content" in result
    
    @pytest.mark.asyncio
    async def test_process_communication_operation(self, engine):
        """Test process communication operation"""
        await engine._initialize_engine()
        
        request = SupremeRequest(
            request_id="test_005",
            operation="process_communication",
            parameters={
                "content": "Hello world",
                "communication_type": "email",
                "style": "professional",
                "target_language": "es"
            }
        )
        
        result = await engine._execute_operation(request)
        
        assert result["operation"] == "process_communication"
        assert "request_id" in result
        assert result["communication_type"] == "email"
        assert "translation" in result
    
    @pytest.mark.asyncio
    async def test_communication_status_operation(self, engine):
        """Test communication status operation"""
        await engine._initialize_engine()
        
        request = SupremeRequest(
            request_id="test_006",
            operation="communication_status",
            parameters={}
        )
        
        result = await engine._execute_operation(request)
        
        assert result["operation"] == "communication_status"
        assert result["status"] == "active"
        assert "capabilities" in result
        assert "metrics" in result
    
    @pytest.mark.asyncio
    async def test_supported_operations(self, engine):
        """Test getting supported operations"""
        operations = await engine.get_supported_operations()
        
        expected_operations = [
            "translate_text", "detect_language", "enhance_content", 
            "generate_content", "process_communication", "communication_status"
        ]
        
        for op in expected_operations:
            assert op in operations
    
    @pytest.mark.asyncio
    async def test_error_handling_missing_parameters(self, engine):
        """Test error handling for missing parameters"""
        await engine._initialize_engine()
        
        # Test translate without required parameters
        request = SupremeRequest(
            request_id="test_007",
            operation="translate_text",
            parameters={"text": "Hello"}  # Missing target_language
        )
        
        result = await engine._execute_operation(request)
        
        assert "error" in result
        assert "target_language" in result["error"]
    
    @pytest.mark.asyncio
    async def test_error_handling_invalid_enum_values(self, engine):
        """Test error handling for invalid enum values"""
        await engine._initialize_engine()
        
        request = SupremeRequest(
            request_id="test_008",
            operation="enhance_content",
            parameters={
                "content": "Hello world",
                "communication_type": "invalid_type",
                "style": "professional"
            }
        )
        
        result = await engine._execute_operation(request)
        
        assert "error" in result

if __name__ == "__main__":
    pytest.main([__file__])