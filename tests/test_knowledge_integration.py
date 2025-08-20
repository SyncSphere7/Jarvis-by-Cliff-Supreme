"""
Integration tests for Knowledge Engine with Expert System and Fact Verification
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock

from core.supreme.engines.knowledge_engine import SupremeKnowledgeEngine
from core.supreme.engines.expert_system import ExpertDomain, FactStatus
from core.supreme.base_supreme_engine import SupremeRequest

class TestKnowledgeEngineIntegration:
    """Integration test cases for Knowledge Engine with Expert System and Fact Checker"""
    
    @pytest.fixture
    def engine(self):
        config = Mock()
        config.knowledge_config = {
            "searcher": {},
            "synthesizer": {},
            "expert_system": {},
            "fact_checker": {}
        }
        return SupremeKnowledgeEngine("test_knowledge_engine", config)
    
    @pytest.mark.asyncio
    async def test_consult_expert_operation(self, engine):
        """Test expert consultation through knowledge engine"""
        await engine._initialize_engine()
        
        request = SupremeRequest(
            request_id="test_001",
            operation="consult_expert",
            parameters={
                "domain": "technology",
                "query": "How should I implement scalability in my web application?",
                "context": {"application_type": "web_service", "expected_users": 10000}
            }
        )
        
        result = await engine._execute_operation(request)
        
        assert result["operation"] == "consult_expert"
        assert result["success"] is True
        assert "consultation_result" in result
        
        consultation = result["consultation_result"]
        assert consultation["domain"] == "technology"
        assert "scalability" in consultation["query"].lower()
        assert consultation["confidence_score"] > 0
        assert len(consultation["recommendations"]) > 0
        assert consultation["domain_expertise_level"] in ["Basic", "Intermediate", "Advanced", "Expert"]
    
    @pytest.mark.asyncio
    async def test_verify_fact_operation(self, engine):
        """Test fact verification through knowledge engine"""
        await engine._initialize_engine()
        
        request = SupremeRequest(
            request_id="test_002",
            operation="verify_fact",
            parameters={
                "claim": "Python is a programming language developed by Guido van Rossum",
                "context": {"topic": "programming", "year": "1991"}
            }
        )
        
        result = await engine._execute_operation(request)
        
        assert result["operation"] == "verify_fact"
        assert result["success"] is True
        assert "fact_check_result" in result
        
        fact_check = result["fact_check_result"]
        assert fact_check["claim"] == "Python is a programming language developed by Guido van Rossum"
        assert fact_check["status"] in ["verified", "disputed", "unverified", "false", "partially_true"]
        assert fact_check["confidence_score"] >= 0
        assert len(fact_check["evidence"]) > 0
        assert len(fact_check["verification_sources"]) > 0
    
    @pytest.mark.asyncio
    async def test_verify_suspicious_fact_operation(self, engine):
        """Test verification of suspicious claim"""
        await engine._initialize_engine()
        
        request = SupremeRequest(
            request_id="test_003",
            operation="verify_fact",
            parameters={
                "claim": "This miracle cure is 100% guaranteed and doctors hate this secret method",
                "context": {"topic": "health"}
            }
        )
        
        result = await engine._execute_operation(request)
        
        assert result["success"] is True
        fact_check = result["fact_check_result"]
        
        # Should have lower confidence due to suspicious patterns
        assert fact_check["confidence_score"] < 0.8
        assert fact_check["status"] in ["false", "disputed", "unverified"]
    
    @pytest.mark.asyncio
    async def test_expert_consultation_multiple_domains(self, engine):
        """Test consulting experts from multiple domains"""
        await engine._initialize_engine()
        
        domains_and_queries = [
            ("technology", "What are best practices for database design?"),
            ("science", "How should I design a controlled experiment?"),
            ("finance", "What factors should I consider for investment risk assessment?")
        ]
        
        results = []
        for domain, query in domains_and_queries:
            request = SupremeRequest(
                request_id=f"test_{domain}",
                operation="consult_expert",
                parameters={"domain": domain, "query": query}
            )
            
            result = await engine._execute_operation(request)
            results.append(result)
        
        # All consultations should be successful
        assert all(r["success"] for r in results)
        
        # Each should have domain-specific responses
        tech_result = results[0]["consultation_result"]
        science_result = results[1]["consultation_result"]
        finance_result = results[2]["consultation_result"]
        
        assert "database" in tech_result["expert_response"].lower()
        assert "experiment" in science_result["expert_response"].lower()
        assert "risk" in finance_result["expert_response"].lower()
    
    @pytest.mark.asyncio
    async def test_fact_verification_batch_processing(self, engine):
        """Test batch fact verification capabilities"""
        await engine._initialize_engine()
        
        claims = [
            "Water boils at 100 degrees Celsius at sea level",
            "The Earth is flat",
            "Python was created in 1991",
            "This miracle cure works 100% of the time"
        ]
        
        results = []
        for i, claim in enumerate(claims):
            request = SupremeRequest(
                request_id=f"batch_test_{i}",
                operation="verify_fact",
                parameters={"claim": claim}
            )
            
            result = await engine._execute_operation(request)
            results.append(result)
        
        # All verifications should complete successfully
        assert all(r["success"] for r in results)
        
        # Check that different claims get different confidence scores
        confidence_scores = [r["fact_check_result"]["confidence_score"] for r in results]
        assert len(set(confidence_scores)) > 1  # Should have different confidence levels
        
        # The suspicious claim should have lower confidence
        suspicious_result = results[3]["fact_check_result"]  # "miracle cure" claim
        assert suspicious_result["confidence_score"] < 0.7
    
    @pytest.mark.asyncio
    async def test_knowledge_engine_comprehensive_workflow(self, engine):
        """Test comprehensive workflow combining all knowledge capabilities"""
        await engine._initialize_engine()
        
        # Step 1: Answer a question using knowledge synthesis
        question_request = SupremeRequest(
            request_id="workflow_001",
            operation="answer_question",
            parameters={
                "question": "What are the key principles of machine learning?",
                "synthesis_method": "summarization"
            }
        )
        
        question_result = await engine._execute_operation(question_request)
        assert question_result["success"] is True
        
        # Step 2: Consult technology expert for implementation advice
        expert_request = SupremeRequest(
            request_id="workflow_002",
            operation="consult_expert",
            parameters={
                "domain": "technology",
                "query": "How should I implement machine learning in production?",
                "context": {"scale": "enterprise", "data_size": "large"}
            }
        )
        
        expert_result = await engine._execute_operation(expert_request)
        assert expert_result["success"] is True
        
        # Step 3: Verify a related fact
        fact_request = SupremeRequest(
            request_id="workflow_003",
            operation="verify_fact",
            parameters={
                "claim": "Machine learning requires large datasets for training",
                "context": {"domain": "technology"}
            }
        )
        
        fact_result = await engine._execute_operation(fact_request)
        assert fact_result["success"] is True
        
        # Step 4: Get analytics on all operations
        analytics_request = SupremeRequest(
            request_id="workflow_004",
            operation="get_knowledge_analytics",
            parameters={}
        )
        
        analytics_result = await engine._execute_operation(analytics_request)
        assert analytics_result["success"] is True
        
        # Verify the workflow generated comprehensive results
        assert question_result["result"]["sources_consulted"] > 0
        assert expert_result["consultation_result"]["confidence_score"] > 0
        assert fact_result["fact_check_result"]["confidence_score"] >= 0
        assert analytics_result["analytics"]["performance_metrics"]["total_queries"] >= 1
    
    @pytest.mark.asyncio
    async def test_error_handling_invalid_domain(self, engine):
        """Test error handling for invalid expert domain"""
        await engine._initialize_engine()
        
        request = SupremeRequest(
            request_id="error_test_001",
            operation="consult_expert",
            parameters={
                "domain": "invalid_domain",
                "query": "Test query"
            }
        )
        
        result = await engine._execute_operation(request)
        
        assert "error" in result
        assert "Invalid domain" in result["error"]
    
    @pytest.mark.asyncio
    async def test_error_handling_missing_parameters(self, engine):
        """Test error handling for missing parameters"""
        await engine._initialize_engine()
        
        # Test expert consultation without domain
        expert_request = SupremeRequest(
            request_id="error_test_002",
            operation="consult_expert",
            parameters={"query": "Test query"}  # Missing domain
        )
        
        expert_result = await engine._execute_operation(expert_request)
        assert "error" in expert_result
        assert "domain and query are required" in expert_result["error"]
        
        # Test fact verification without claim
        fact_request = SupremeRequest(
            request_id="error_test_003",
            operation="verify_fact",
            parameters={}  # Missing claim
        )
        
        fact_result = await engine._execute_operation(fact_request)
        assert "error" in fact_result
        assert "claim is required" in fact_result["error"]
    
    @pytest.mark.asyncio
    async def test_knowledge_status_with_expert_capabilities(self, engine):
        """Test knowledge status includes expert system capabilities"""
        await engine._initialize_engine()
        
        request = SupremeRequest(
            request_id="status_test",
            operation="knowledge_status",
            parameters={}
        )
        
        result = await engine._execute_operation(request)
        
        assert result["status"] == "active"
        capabilities = result["capabilities"]
        assert capabilities["expert_consultation"] is True
        assert capabilities["fact_verification"] is True
        assert capabilities["universal_search"] is True
        assert capabilities["knowledge_synthesis"] is True

if __name__ == "__main__":
    pytest.main([__file__])