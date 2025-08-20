"""
Tests for Supreme Knowledge Engine
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock

from core.supreme.engines.knowledge_engine import (
    SupremeKnowledgeEngine,
    KnowledgeOracle,
    UniversalSearcher,
    KnowledgeSynthesizer,
    KnowledgeSource,
    InformationType,
    ConfidenceLevel,
    KnowledgeItem,
    SynthesisResult
)
from core.supreme.base_supreme_engine import SupremeRequest

class TestUniversalSearcher:
    """Test cases for UniversalSearcher"""
    
    @pytest.fixture
    def searcher(self):
        config = {"searcher": {}}
        return UniversalSearcher(config)
    
    @pytest.mark.asyncio
    async def test_search_all_sources(self, searcher):
        """Test searching across all sources"""
        results = await searcher.search("artificial intelligence", max_results=10)
        
        assert len(results) > 0
        assert len(results) <= 10
        
        # Check that we have results from multiple sources
        sources_found = set(item.source for item in results)
        assert len(sources_found) > 1
    
    @pytest.mark.asyncio
    async def test_search_specific_sources(self, searcher):
        """Test searching specific sources"""
        sources = [KnowledgeSource.WIKIPEDIA, KnowledgeSource.ACADEMIC]
        results = await searcher.search("machine learning", sources=sources, max_results=5)
        
        assert len(results) <= 5
        
        # All results should be from specified sources
        for result in results:
            assert result.source in sources
    
    @pytest.mark.asyncio
    async def test_search_caching(self, searcher):
        """Test search result caching"""
        query = "test query"
        sources = [KnowledgeSource.WEB_SEARCH]
        
        # First search
        results1 = await searcher.search(query, sources=sources)
        initial_cache_hits = searcher.metrics["cache_hits"]
        
        # Second search (should use cache)
        results2 = await searcher.search(query, sources=sources)
        
        assert searcher.metrics["cache_hits"] == initial_cache_hits + 1
        assert len(results1) == len(results2)
    
    @pytest.mark.asyncio
    async def test_search_web(self, searcher):
        """Test web search functionality"""
        results = await searcher._search_web("python programming", 3)
        
        assert len(results) <= 3
        for result in results:
            assert result.source == KnowledgeSource.WEB_SEARCH
            assert result.information_type == InformationType.FACTUAL
            assert result.confidence_level == ConfidenceLevel.MEDIUM
            assert "python programming" in result.content.lower()
    
    @pytest.mark.asyncio
    async def test_search_wikipedia(self, searcher):
        """Test Wikipedia search functionality"""
        results = await searcher._search_wikipedia("quantum computing", 2)
        
        assert len(results) <= 2
        for result in results:
            assert result.source == KnowledgeSource.WIKIPEDIA
            assert result.confidence_level == ConfidenceLevel.HIGH
            assert "wikipedia" in result.source_url.lower()
    
    @pytest.mark.asyncio
    async def test_search_news(self, searcher):
        """Test news search functionality"""
        results = await searcher._search_news("climate change", 3)
        
        assert len(results) <= 3
        for result in results:
            assert result.source == KnowledgeSource.NEWS
            assert result.information_type == InformationType.CURRENT_EVENTS
            assert result.publication_date is not None
    
    @pytest.mark.asyncio
    async def test_search_academic(self, searcher):
        """Test academic search functionality"""
        results = await searcher._search_academic("neural networks", 2)
        
        assert len(results) <= 2
        for result in results:
            assert result.source == KnowledgeSource.ACADEMIC
            assert result.information_type == InformationType.TECHNICAL
            assert result.confidence_level == ConfidenceLevel.VERY_HIGH
            assert result.author is not None
    
    @pytest.mark.asyncio
    async def test_result_ranking(self, searcher):
        """Test result ranking functionality"""
        # Create test items with different relevance and confidence
        items = [
            KnowledgeItem("1", "content1", KnowledgeSource.WEB_SEARCH, InformationType.FACTUAL, 
                         ConfidenceLevel.LOW, 0.9),
            KnowledgeItem("2", "content2", KnowledgeSource.ACADEMIC, InformationType.TECHNICAL, 
                         ConfidenceLevel.VERY_HIGH, 0.8),
            KnowledgeItem("3", "content3", KnowledgeSource.WIKIPEDIA, InformationType.FACTUAL, 
                         ConfidenceLevel.HIGH, 0.7)
        ]
        
        ranked = await searcher._rank_results(items, "test query")
        
        # Academic source with very high confidence should rank highest despite lower relevance
        assert ranked[0].source == KnowledgeSource.ACADEMIC
        assert len(ranked) == 3
    
    def test_cache_key_generation(self, searcher):
        """Test cache key generation"""
        sources = [KnowledgeSource.WEB_SEARCH, KnowledgeSource.WIKIPEDIA]
        key1 = searcher._generate_cache_key("test query", sources)
        key2 = searcher._generate_cache_key("test query", sources)
        key3 = searcher._generate_cache_key("different query", sources)
        
        assert key1 == key2  # Same query and sources should generate same key
        assert key1 != key3  # Different query should generate different key
        assert len(key1) == 32  # MD5 hash length

class TestKnowledgeSynthesizer:
    """Test cases for KnowledgeSynthesizer"""
    
    @pytest.fixture
    def synthesizer(self):
        config = {"synthesizer": {}}
        return KnowledgeSynthesizer(config)
    
    @pytest.fixture
    def sample_knowledge_items(self):
        """Create sample knowledge items for testing"""
        return [
            KnowledgeItem(
                "item1", "AI is a branch of computer science", KnowledgeSource.WIKIPEDIA,
                InformationType.FACTUAL, ConfidenceLevel.HIGH, 0.9
            ),
            KnowledgeItem(
                "item2", "Machine learning is a subset of AI", KnowledgeSource.ACADEMIC,
                InformationType.TECHNICAL, ConfidenceLevel.VERY_HIGH, 0.85
            ),
            KnowledgeItem(
                "item3", "AI has many applications in industry", KnowledgeSource.NEWS,
                InformationType.CURRENT_EVENTS, ConfidenceLevel.MEDIUM, 0.8
            )
        ]
    
    @pytest.mark.asyncio
    async def test_synthesize_by_summarization(self, synthesizer, sample_knowledge_items):
        """Test knowledge synthesis by summarization"""
        result = await synthesizer.synthesize_knowledge(
            "What is AI?", sample_knowledge_items, "summarization"
        )
        
        assert isinstance(result, SynthesisResult)
        assert result.query == "What is AI?"
        assert result.synthesis_method == "summarization"
        assert len(result.source_items) > 0
        assert result.confidence_score > 0
        assert len(result.key_insights) > 0
        assert "AI" in result.synthesized_content or "ai" in result.synthesized_content.lower()
    
    @pytest.mark.asyncio
    async def test_synthesize_by_comparison(self, synthesizer, sample_knowledge_items):
        """Test knowledge synthesis by comparison"""
        result = await synthesizer.synthesize_knowledge(
            "Compare AI perspectives", sample_knowledge_items, "comparison"
        )
        
        assert result.synthesis_method == "comparison"
        assert "Comparative analysis" in result.synthesized_content
        assert result.confidence_score == 0.75  # Fixed confidence for comparison method
        assert len(result.key_insights) > 0
    
    @pytest.mark.asyncio
    async def test_synthesize_invalid_method(self, synthesizer, sample_knowledge_items):
        """Test synthesis with invalid method falls back to summarization"""
        result = await synthesizer.synthesize_knowledge(
            "Test query", sample_knowledge_items, "invalid_method"
        )
        
        assert result.synthesis_method == "summarization"  # Should fall back
        assert result.confidence_score > 0
    
    @pytest.mark.asyncio
    async def test_synthesize_empty_items(self, synthesizer):
        """Test synthesis with empty knowledge items"""
        result = await synthesizer.synthesize_knowledge("Test query", [], "summarization")
        
        assert result.synthesis_method == "summarization"
        assert len(result.source_items) == 0
        assert result.confidence_score >= 0  # Should handle empty gracefully
    
    def test_synthesis_history(self, synthesizer, sample_knowledge_items):
        """Test that synthesis results are stored in history"""
        initial_count = len(synthesizer.synthesis_history)
        
        # Run synthesis (async, so we need to use asyncio.run in test)
        async def run_synthesis():
            await synthesizer.synthesize_knowledge("Test", sample_knowledge_items)
        
        asyncio.run(run_synthesis())
        
        assert len(synthesizer.synthesis_history) == initial_count + 1

class TestKnowledgeOracle:
    """Test cases for KnowledgeOracle"""
    
    @pytest.fixture
    def oracle(self):
        config = {
            "searcher": {},
            "synthesizer": {}
        }
        return KnowledgeOracle(config)
    
    @pytest.mark.asyncio
    async def test_answer_question(self, oracle):
        """Test question answering functionality"""
        answer = await oracle.answer_question("What is machine learning?")
        
        assert "question" in answer
        assert answer["question"] == "What is machine learning?"
        assert "answer" in answer
        assert "confidence_score" in answer
        assert "sources_consulted" in answer
        assert "source_breakdown" in answer
        assert "key_insights" in answer
        assert "processing_time" in answer
        assert answer["sources_consulted"] > 0
    
    @pytest.mark.asyncio
    async def test_answer_question_specific_sources(self, oracle):
        """Test question answering with specific sources"""
        sources = [KnowledgeSource.WIKIPEDIA, KnowledgeSource.ACADEMIC]
        answer = await oracle.answer_question(
            "Explain neural networks", sources=sources, synthesis_method="comparison"
        )
        
        assert answer["synthesis_method"] == "comparison"
        assert answer["sources_consulted"] > 0
        
        # Check that only specified sources were used
        source_breakdown = answer["source_breakdown"]
        for source_name in source_breakdown.keys():
            assert source_name in [s.value for s in sources]
    
    @pytest.mark.asyncio
    async def test_knowledge_base_storage(self, oracle):
        """Test that knowledge items are stored in knowledge base"""
        initial_count = len(oracle.knowledge_base)
        
        await oracle.answer_question("Test question for storage")
        
        assert len(oracle.knowledge_base) > initial_count
    
    @pytest.mark.asyncio
    async def test_query_history(self, oracle):
        """Test that queries are stored in history"""
        initial_count = len(oracle.query_history)
        
        await oracle.answer_question("Test question for history")
        
        assert len(oracle.query_history) == initial_count + 1
        
        latest_query = oracle.query_history[-1]
        assert latest_query["question"] == "Test question for history"
        assert "timestamp" in latest_query
        assert "confidence_score" in latest_query
    
    @pytest.mark.asyncio
    async def test_get_knowledge_analytics(self, oracle):
        """Test knowledge analytics functionality"""
        # First, generate some data
        await oracle.answer_question("Test question for analytics")
        
        analytics = await oracle.get_knowledge_analytics()
        
        assert "performance_metrics" in analytics
        assert "searcher_metrics" in analytics
        assert "knowledge_base_stats" in analytics
        assert "recent_queries" in analytics
        assert "synthesis_history" in analytics
        
        # Check knowledge base stats structure
        kb_stats = analytics["knowledge_base_stats"]
        assert "total_items" in kb_stats
        assert "by_source" in kb_stats
        assert "by_type" in kb_stats
        assert "by_confidence" in kb_stats
    
    def test_source_breakdown_analysis(self, oracle):
        """Test source breakdown analysis"""
        items = [
            KnowledgeItem("1", "content1", KnowledgeSource.WIKIPEDIA, InformationType.FACTUAL, ConfidenceLevel.HIGH, 0.9),
            KnowledgeItem("2", "content2", KnowledgeSource.WIKIPEDIA, InformationType.FACTUAL, ConfidenceLevel.HIGH, 0.8),
            KnowledgeItem("3", "content3", KnowledgeSource.ACADEMIC, InformationType.TECHNICAL, ConfidenceLevel.VERY_HIGH, 0.9)
        ]
        
        breakdown = oracle._analyze_source_breakdown(items)
        
        assert breakdown["wikipedia"] == 2
        assert breakdown["academic"] == 1
        assert len(breakdown) == 2

class TestSupremeKnowledgeEngine:
    """Test cases for SupremeKnowledgeEngine"""
    
    @pytest.fixture
    def engine(self):
        config = Mock()
        config.knowledge_config = {
            "searcher": {},
            "synthesizer": {}
        }
        return SupremeKnowledgeEngine("test_knowledge_engine", config)
    
    @pytest.mark.asyncio
    async def test_engine_initialization(self, engine):
        """Test engine initialization"""
        result = await engine._initialize_engine()
        assert result is True
    
    @pytest.mark.asyncio
    async def test_answer_question_operation(self, engine):
        """Test answer question operation"""
        await engine._initialize_engine()
        
        request = SupremeRequest(
            request_id="test_001",
            operation="answer_question",
            parameters={
                "question": "What is artificial intelligence?",
                "synthesis_method": "summarization"
            }
        )
        
        result = await engine._execute_operation(request)
        
        assert result["operation"] == "answer_question"
        assert result["success"] is True
        assert "result" in result
        assert result["result"]["question"] == "What is artificial intelligence?"
    
    @pytest.mark.asyncio
    async def test_answer_question_with_sources(self, engine):
        """Test answer question with specific sources"""
        await engine._initialize_engine()
        
        request = SupremeRequest(
            request_id="test_002",
            operation="answer_question",
            parameters={
                "question": "Explain quantum computing",
                "sources": ["wikipedia", "academic"],
                "synthesis_method": "comparison"
            }
        )
        
        result = await engine._execute_operation(request)
        
        assert result["success"] is True
        assert result["result"]["synthesis_method"] == "comparison"
    
    @pytest.mark.asyncio
    async def test_search_knowledge_operation(self, engine):
        """Test search knowledge operation"""
        await engine._initialize_engine()
        
        request = SupremeRequest(
            request_id="test_003",
            operation="search_knowledge",
            parameters={
                "query": "machine learning algorithms",
                "sources": ["academic", "web_search"],
                "max_results": 5
            }
        )
        
        result = await engine._execute_operation(request)
        
        assert result["operation"] == "search_knowledge"
        assert result["success"] is True
        assert result["query"] == "machine learning algorithms"
        assert "knowledge_items" in result
        assert result["results_found"] <= 5
    
    @pytest.mark.asyncio
    async def test_synthesize_knowledge_operation(self, engine):
        """Test synthesize knowledge operation"""
        await engine._initialize_engine()
        
        request = SupremeRequest(
            request_id="test_004",
            operation="synthesize_knowledge",
            parameters={
                "query": "deep learning applications",
                "method": "summarization"
            }
        )
        
        result = await engine._execute_operation(request)
        
        assert result["operation"] == "synthesize_knowledge"
        assert result["success"] is True
        assert "synthesis_result" in result
        assert result["synthesis_result"]["synthesis_method"] == "summarization"
    
    @pytest.mark.asyncio
    async def test_get_knowledge_analytics_operation(self, engine):
        """Test get knowledge analytics operation"""
        await engine._initialize_engine()
        
        request = SupremeRequest(
            request_id="test_005",
            operation="get_knowledge_analytics",
            parameters={}
        )
        
        result = await engine._execute_operation(request)
        
        assert result["operation"] == "get_knowledge_analytics"
        assert result["success"] is True
        assert "analytics" in result
    
    @pytest.mark.asyncio
    async def test_knowledge_status_operation(self, engine):
        """Test knowledge status operation"""
        await engine._initialize_engine()
        
        request = SupremeRequest(
            request_id="test_006",
            operation="knowledge_status",
            parameters={}
        )
        
        result = await engine._execute_operation(request)
        
        assert result["operation"] == "knowledge_status"
        assert result["status"] == "active"
        assert "capabilities" in result
        assert result["capabilities"]["universal_search"] is True
        assert result["capabilities"]["knowledge_synthesis"] is True
        assert "supported_sources" in result
    
    @pytest.mark.asyncio
    async def test_supported_operations(self, engine):
        """Test getting supported operations"""
        operations = await engine.get_supported_operations()
        
        expected_operations = [
            "answer_question", "search_knowledge", "synthesize_knowledge",
            "get_knowledge_analytics", "knowledge_status"
        ]
        
        for op in expected_operations:
            assert op in operations
    
    @pytest.mark.asyncio
    async def test_error_handling_missing_question(self, engine):
        """Test error handling for missing question parameter"""
        await engine._initialize_engine()
        
        request = SupremeRequest(
            request_id="test_007",
            operation="answer_question",
            parameters={}  # Missing question
        )
        
        result = await engine._execute_operation(request)
        
        assert "error" in result
        assert "question is required" in result["error"]
    
    @pytest.mark.asyncio
    async def test_error_handling_invalid_sources(self, engine):
        """Test error handling for invalid sources"""
        await engine._initialize_engine()
        
        request = SupremeRequest(
            request_id="test_008",
            operation="answer_question",
            parameters={
                "question": "Test question",
                "sources": ["invalid_source"]
            }
        )
        
        result = await engine._execute_operation(request)
        
        assert "error" in result
        assert "Invalid source" in result["error"]
    
    @pytest.mark.asyncio
    async def test_error_handling_missing_query(self, engine):
        """Test error handling for missing search query"""
        await engine._initialize_engine()
        
        request = SupremeRequest(
            request_id="test_009",
            operation="search_knowledge",
            parameters={}  # Missing query
        )
        
        result = await engine._execute_operation(request)
        
        assert "error" in result
        assert "query is required" in result["error"]

if __name__ == "__main__":
    pytest.main([__file__])