"""
Tests for Supreme Social Engine
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock

from core.supreme.engines.social_engine import (
    SupremeSocialEngine,
    SocialManager,
    NetworkingAgent,
    SocialPlatform,
    PostType,
    SocialPost,
    NetworkingContact
)
from core.supreme.base_supreme_engine import SupremeRequest

class TestSocialManager:
    """Test cases for SocialManager"""
    
    @pytest.fixture
    def social_manager(self):
        config = {"social_manager": {}}
        return SocialManager(config)
    
    @pytest.mark.asyncio
    async def test_create_post(self, social_manager):
        """Test creating a social media post"""
        post = await social_manager.create_post(
            SocialPlatform.TWITTER,
            "This is a test post #testing #ai",
            PostType.TEXT
        )
        
        assert post.platform == SocialPlatform.TWITTER
        assert post.post_type == PostType.TEXT
        assert "#testing" in post.hashtags
        assert "#ai" in post.hashtags
        assert post.post_id.startswith("post_")
        assert post.published_time is not None
    
    @pytest.mark.asyncio
    async def test_create_scheduled_post(self, social_manager):
        """Test creating a scheduled post"""
        future_time = datetime.now() + timedelta(hours=1)
        
        post = await social_manager.create_post(
            SocialPlatform.LINKEDIN,
            "Scheduled post content",
            PostType.TEXT,
            scheduled_time=future_time
        )
        
        assert post.scheduled_time == future_time
        assert post.published_time is None  # Should not be published yet
    
    @pytest.mark.asyncio
    async def test_optimize_content_twitter(self, social_manager):
        """Test content optimization for Twitter"""
        long_content = "This is a very long tweet that exceeds the 280 character limit for Twitter posts and should be truncated to fit within the platform's constraints while maintaining readability and meaning for the audience who will be reading this content on their timeline. This additional text makes it much longer than 280 characters and should definitely be truncated."
        
        optimization = await social_manager.optimize_content(long_content, SocialPlatform.TWITTER)
        
        assert len(optimization["optimized_content"]) <= 280
        if len(long_content) > 280:
            assert optimization["optimized_content"].endswith("...")
        assert optimization["platform"] == "twitter"
    
    @pytest.mark.asyncio
    async def test_optimize_content_linkedin(self, social_manager):
        """Test content optimization for LinkedIn"""
        content = "Professional post without proper punctuation"
        
        optimization = await social_manager.optimize_content(content, SocialPlatform.LINKEDIN)
        
        assert optimization["optimized_content"].endswith(".")
        assert optimization["platform"] == "linkedin"
    
    @pytest.mark.asyncio
    async def test_optimize_content_instagram(self, social_manager):
        """Test content optimization for Instagram"""
        content = "Instagram post without emojis"
        
        optimization = await social_manager.optimize_content(content, SocialPlatform.INSTAGRAM)
        
        assert "✨" in optimization["optimized_content"]
        assert optimization["platform"] == "instagram"
    
    @pytest.mark.asyncio
    async def test_analyze_engagement(self, social_manager):
        """Test engagement analysis"""
        # Create a post first
        post = await social_manager.create_post(
            SocialPlatform.TWITTER,
            "Test post for engagement #testing",
            PostType.TEXT
        )
        
        # Analyze engagement
        analysis = await social_manager.analyze_engagement(post.post_id)
        
        assert analysis["post_id"] == post.post_id
        assert analysis["platform"] == "twitter"
        assert "engagement_metrics" in analysis
        assert "hashtag_performance" in analysis
        assert "sentiment_analysis" in analysis
    
    @pytest.mark.asyncio
    async def test_analyze_engagement_nonexistent_post(self, social_manager):
        """Test engagement analysis for non-existent post"""
        analysis = await social_manager.analyze_engagement("nonexistent_post")
        
        assert "error" in analysis
        assert analysis["error"] == "Post not found"
    
    @pytest.mark.asyncio
    async def test_hashtag_extraction(self, social_manager):
        """Test hashtag extraction from content"""
        content = "This is a post with #hashtag1 and #hashtag2 and #hashtag3"
        hashtags = social_manager._extract_hashtags(content)
        
        assert "#hashtag1" in hashtags
        assert "#hashtag2" in hashtags
        assert "#hashtag3" in hashtags
        assert len(hashtags) == 3
    
    @pytest.mark.asyncio
    async def test_sentiment_analysis_positive(self, social_manager):
        """Test positive sentiment analysis"""
        content = "This is an amazing and excellent post that I love"
        sentiment = await social_manager._analyze_post_sentiment(content)
        
        assert sentiment["sentiment"] == "positive"
        assert sentiment["score"] > 0.5
    
    @pytest.mark.asyncio
    async def test_sentiment_analysis_negative(self, social_manager):
        """Test negative sentiment analysis"""
        content = "This is a terrible and awful post that I hate"
        sentiment = await social_manager._analyze_post_sentiment(content)
        
        assert sentiment["sentiment"] == "negative"
        assert sentiment["score"] < 0.5
    
    @pytest.mark.asyncio
    async def test_sentiment_analysis_neutral(self, social_manager):
        """Test neutral sentiment analysis"""
        content = "This is a regular post about technology"
        sentiment = await social_manager._analyze_post_sentiment(content)
        
        assert sentiment["sentiment"] == "neutral"
        assert sentiment["score"] == 0.5
    
    @pytest.mark.asyncio
    async def test_hashtag_suggestions(self, social_manager):
        """Test hashtag suggestions"""
        content = "This post is about AI and technology in business"
        hashtags = await social_manager._suggest_optimal_hashtags(content, SocialPlatform.TWITTER)
        
        assert any("#AI" in tag for tag in hashtags)
        assert any("#Technology" in tag for tag in hashtags)
        assert any("Business" in tag for tag in hashtags)
    
    def test_metrics_update(self, social_manager):
        """Test metrics updating"""
        initial_posts = social_manager.metrics["total_posts"]
        initial_successful = social_manager.metrics["successful_posts"]
        
        # Simulate successful post
        social_manager.metrics["total_posts"] += 1
        social_manager.metrics["successful_posts"] += 1
        
        assert social_manager.metrics["total_posts"] == initial_posts + 1
        assert social_manager.metrics["successful_posts"] == initial_successful + 1

class TestNetworkingAgent:
    """Test cases for NetworkingAgent"""
    
    @pytest.fixture
    def networking_agent(self):
        config = {"networking": {}}
        return NetworkingAgent(config)
    
    @pytest.mark.asyncio
    async def test_add_contact(self, networking_agent):
        """Test adding a networking contact"""
        contact = await networking_agent.add_contact(
            "John Doe",
            SocialPlatform.LINKEDIN,
            "https://linkedin.com/in/johndoe",
            industry="Technology",
            company="Tech Corp"
        )
        
        assert contact.name == "John Doe"
        assert contact.platform == SocialPlatform.LINKEDIN
        assert contact.profile_url == "https://linkedin.com/in/johndoe"
        assert contact.industry == "Technology"
        assert contact.company == "Tech Corp"
        assert contact.contact_id.startswith("contact_")
    
    @pytest.mark.asyncio
    async def test_send_connection_request(self, networking_agent):
        """Test sending a connection request"""
        # Add a contact first
        contact = await networking_agent.add_contact(
            "Jane Smith",
            SocialPlatform.LINKEDIN,
            "https://linkedin.com/in/janesmith",
            industry="Marketing"
        )
        
        # Send connection request
        result = await networking_agent.send_connection_request(
            contact.contact_id,
            "Hi Jane, I'd like to connect!"
        )
        
        assert result["contact_id"] == contact.contact_id
        assert result["contact_name"] == "Jane Smith"
        assert result["platform"] == "linkedin"
        assert result["message"] == "Hi Jane, I'd like to connect!"
        assert result["status"] == "sent"
    
    @pytest.mark.asyncio
    async def test_send_connection_request_auto_message(self, networking_agent):
        """Test sending connection request with auto-generated message"""
        # Add a contact first
        contact = await networking_agent.add_contact(
            "Bob Johnson",
            SocialPlatform.LINKEDIN,
            "https://linkedin.com/in/bobjohnson",
            industry="Finance"
        )
        
        # Send connection request without custom message
        result = await networking_agent.send_connection_request(contact.contact_id)
        
        assert result["contact_id"] == contact.contact_id
        assert "Finance" in result["message"]  # Should mention industry
        assert "Bob Johnson" in result["message"]  # Should mention name
    
    @pytest.mark.asyncio
    async def test_send_connection_request_nonexistent_contact(self, networking_agent):
        """Test sending connection request to non-existent contact"""
        result = await networking_agent.send_connection_request("nonexistent_contact")
        
        assert "error" in result
        assert result["error"] == "Contact not found"
    
    @pytest.mark.asyncio
    async def test_analyze_networking_performance(self, networking_agent):
        """Test networking performance analysis"""
        # Add some contacts
        await networking_agent.add_contact(
            "Contact 1", SocialPlatform.LINKEDIN, "https://example.com/1", industry="Tech"
        )
        await networking_agent.add_contact(
            "Contact 2", SocialPlatform.TWITTER, "https://example.com/2", industry="Marketing"
        )
        
        # Analyze performance
        performance = await networking_agent.analyze_networking_performance("7d")
        
        assert performance["time_range"] == "7d"
        assert performance["new_contacts"] >= 1  # At least one contact should be recent
        assert "top_industries" in performance
        assert "platform_distribution" in performance
        assert performance["top_industries"]["Tech"] == 1
        assert performance["top_industries"]["Marketing"] == 1
    
    @pytest.mark.asyncio
    async def test_generate_connection_message_with_industry(self, networking_agent):
        """Test connection message generation with industry"""
        contact = NetworkingContact(
            contact_id="test_id",
            name="Test User",
            platform=SocialPlatform.LINKEDIN,
            profile_url="https://example.com",
            industry="Technology"
        )
        
        message = await networking_agent._generate_connection_message(contact)
        
        assert "Test User" in message
        assert "Technology" in message
    
    @pytest.mark.asyncio
    async def test_generate_connection_message_without_industry(self, networking_agent):
        """Test connection message generation without industry"""
        contact = NetworkingContact(
            contact_id="test_id",
            name="Test User",
            platform=SocialPlatform.LINKEDIN,
            profile_url="https://example.com"
        )
        
        message = await networking_agent._generate_connection_message(contact)
        
        assert "Test User" in message
        assert "connect" in message.lower()
    
    def test_industry_distribution_analysis(self, networking_agent):
        """Test industry distribution analysis"""
        contacts = [
            NetworkingContact("1", "User 1", SocialPlatform.LINKEDIN, "url1", industry="Tech"),
            NetworkingContact("2", "User 2", SocialPlatform.LINKEDIN, "url2", industry="Tech"),
            NetworkingContact("3", "User 3", SocialPlatform.LINKEDIN, "url3", industry="Marketing"),
        ]
        
        distribution = networking_agent._analyze_industry_distribution(contacts)
        
        assert distribution["Tech"] == 2
        assert distribution["Marketing"] == 1
    
    def test_platform_distribution_analysis(self, networking_agent):
        """Test platform distribution analysis"""
        contacts = [
            NetworkingContact("1", "User 1", SocialPlatform.LINKEDIN, "url1"),
            NetworkingContact("2", "User 2", SocialPlatform.LINKEDIN, "url2"),
            NetworkingContact("3", "User 3", SocialPlatform.TWITTER, "url3"),
        ]
        
        distribution = networking_agent._analyze_platform_distribution(contacts)
        
        assert distribution["linkedin"] == 2
        assert distribution["twitter"] == 1

class TestSupremeSocialEngine:
    """Test cases for SupremeSocialEngine"""
    
    @pytest.fixture
    def engine(self):
        config = Mock()
        config.social_config = {
            "social_manager": {},
            "networking": {}
        }
        return SupremeSocialEngine("test_social_engine", config)
    
    @pytest.mark.asyncio
    async def test_engine_initialization(self, engine):
        """Test engine initialization"""
        result = await engine._initialize_engine()
        assert result is True
    
    @pytest.mark.asyncio
    async def test_create_post_operation(self, engine):
        """Test create post operation"""
        await engine._initialize_engine()
        
        request = SupremeRequest(
            request_id="test_001",
            operation="create_post",
            parameters={
                "platform": "twitter",
                "content": "Test post content #testing",
                "post_type": "text"
            }
        )
        
        result = await engine._execute_operation(request)
        
        assert result["operation"] == "create_post"
        assert result["success"] is True
        assert "post" in result
        assert result["post"]["platform"] == "twitter"
        assert result["post"]["content"] == "Test post content #testing"
    
    @pytest.mark.asyncio
    async def test_analyze_engagement_operation(self, engine):
        """Test analyze engagement operation"""
        await engine._initialize_engine()
        
        # Create a post first
        create_request = SupremeRequest(
            request_id="test_002a",
            operation="create_post",
            parameters={
                "platform": "twitter",
                "content": "Test post for analysis #testing",
                "post_type": "text"
            }
        )
        
        create_result = await engine._execute_operation(create_request)
        post_id = create_result["post"]["post_id"]
        
        # Analyze engagement
        analyze_request = SupremeRequest(
            request_id="test_002b",
            operation="analyze_engagement",
            parameters={"post_id": post_id}
        )
        
        result = await engine._execute_operation(analyze_request)
        
        assert result["operation"] == "analyze_engagement"
        assert result["success"] is True
        assert "analysis" in result
        assert result["analysis"]["post_id"] == post_id
    
    @pytest.mark.asyncio
    async def test_optimize_content_operation(self, engine):
        """Test optimize content operation"""
        await engine._initialize_engine()
        
        request = SupremeRequest(
            request_id="test_003",
            operation="optimize_content",
            parameters={
                "content": "This is content to optimize for social media",
                "platform": "linkedin"
            }
        )
        
        result = await engine._execute_operation(request)
        
        assert result["operation"] == "optimize_content"
        assert result["success"] is True
        assert "optimization" in result
        assert result["optimization"]["platform"] == "linkedin"
    
    @pytest.mark.asyncio
    async def test_add_contact_operation(self, engine):
        """Test add contact operation"""
        await engine._initialize_engine()
        
        request = SupremeRequest(
            request_id="test_004",
            operation="add_contact",
            parameters={
                "name": "John Doe",
                "platform": "linkedin",
                "profile_url": "https://linkedin.com/in/johndoe",
                "industry": "Technology"
            }
        )
        
        result = await engine._execute_operation(request)
        
        assert result["operation"] == "add_contact"
        assert result["success"] is True
        assert "contact" in result
        assert result["contact"]["name"] == "John Doe"
        assert result["contact"]["platform"] == "linkedin"
    
    @pytest.mark.asyncio
    async def test_send_connection_request_operation(self, engine):
        """Test send connection request operation"""
        await engine._initialize_engine()
        
        # Add a contact first
        add_request = SupremeRequest(
            request_id="test_005a",
            operation="add_contact",
            parameters={
                "name": "Jane Smith",
                "platform": "linkedin",
                "profile_url": "https://linkedin.com/in/janesmith"
            }
        )
        
        add_result = await engine._execute_operation(add_request)
        contact_id = add_result["contact"]["contact_id"]
        
        # Send connection request
        connect_request = SupremeRequest(
            request_id="test_005b",
            operation="send_connection_request",
            parameters={
                "contact_id": contact_id,
                "message": "Hi Jane, let's connect!"
            }
        )
        
        result = await engine._execute_operation(connect_request)
        
        assert result["operation"] == "send_connection_request"
        assert result["success"] is True
        assert "request_result" in result
        assert result["request_result"]["contact_id"] == contact_id
    
    @pytest.mark.asyncio
    async def test_analyze_networking_performance_operation(self, engine):
        """Test analyze networking performance operation"""
        await engine._initialize_engine()
        
        request = SupremeRequest(
            request_id="test_006",
            operation="analyze_networking_performance",
            parameters={"time_range": "7d"}
        )
        
        result = await engine._execute_operation(request)
        
        assert result["operation"] == "analyze_networking_performance"
        assert result["success"] is True
        assert "performance" in result
        assert result["performance"]["time_range"] == "7d"
    
    @pytest.mark.asyncio
    async def test_social_status_operation(self, engine):
        """Test social status operation"""
        await engine._initialize_engine()
        
        request = SupremeRequest(
            request_id="test_007",
            operation="social_status",
            parameters={}
        )
        
        result = await engine._execute_operation(request)
        
        assert result["operation"] == "social_status"
        assert result["status"] == "active"
        assert "capabilities" in result
        assert result["capabilities"]["social_media_management"] is True
        assert result["capabilities"]["networking_automation"] is True
    
    @pytest.mark.asyncio
    async def test_supported_operations(self, engine):
        """Test getting supported operations"""
        operations = await engine.get_supported_operations()
        
        expected_operations = [
            "create_post", "analyze_engagement", "optimize_content",
            "add_contact", "send_connection_request", "analyze_networking_performance",
            "social_status"
        ]
        
        for op in expected_operations:
            assert op in operations
    
    @pytest.mark.asyncio
    async def test_error_handling_missing_parameters(self, engine):
        """Test error handling for missing parameters"""
        await engine._initialize_engine()
        
        # Test create post without required parameters
        request = SupremeRequest(
            request_id="test_008",
            operation="create_post",
            parameters={"content": "Test content"}  # Missing platform
        )
        
        result = await engine._execute_operation(request)
        
        assert "error" in result
        assert "platform" in result["error"]
    
    @pytest.mark.asyncio
    async def test_error_handling_invalid_enum_values(self, engine):
        """Test error handling for invalid enum values"""
        await engine._initialize_engine()
        
        request = SupremeRequest(
            request_id="test_009",
            operation="create_post",
            parameters={
                "platform": "invalid_platform",
                "content": "Test content",
                "post_type": "text"
            }
        )
        
        result = await engine._execute_operation(request)
        
        assert "error" in result

if __name__ == "__main__":
    pytest.main([__file__])