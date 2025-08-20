"""
Tests for Compliance and Security Evolution

This module contains comprehensive tests for compliance enforcement,
security evolution, and quantum-resistant security capabilities.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock

from core.supreme.engines.compliance_evolution import (
    ComplianceEnforcer,
    ComplianceStandard,
    ComplianceStatus,
    ComplianceRequirement,
    ComplianceAssessment
)

from core.supreme.engines.security_evolution import (
    SecurityEvolution,
    QuantumSecurity,
    SecurityEvolutionLevel,
    QuantumResistanceLevel,
    SecurityEvolutionPlan,
    QuantumSecurityConfig
)


class TestComplianceEnforcer:
    """Test ComplianceEnforcer functionality"""
    
    @pytest.fixture
    def compliance_enforcer(self):
        return ComplianceEnforcer()
    
    @pytest.fixture
    def sample_system_data(self):
        return {
            "encryption": True,
            "data_classification": "confidential",
            "privacy_controls": True,
            "authentication": "multi_factor",
            "authorization": "role_based",
            "access_logs": True,
            "firewall_config": "configured",
            "network_topology": "documented",
            "security_groups": "implemented"
        }
    
    @pytest.mark.asyncio
    async def test_enforce_compliance_gdpr(self, compliance_enforcer, sample_system_data):
        """Test GDPR compliance enforcement"""
        result = await compliance_enforcer.enforce_compliance(
            ComplianceStandard.GDPR, sample_system_data
        )
        
        assert isinstance(result, dict)
        assert result["standard"] == ComplianceStandard.GDPR.value
        assert result["status"] == "enforced"
        assert "assessment" in result
        assert "remediation_plan" in result
        assert "compliance_score" in result
        assert "timestamp" in result
        
        # Check assessment structure
        assessment = result["assessment"]
        assert isinstance(assessment, ComplianceAssessment)
        assert assessment.standard == ComplianceStandard.GDPR
        assert isinstance(assessment.compliance_score, float)
        assert 0 <= assessment.compliance_score <= 1
    
    @pytest.mark.asyncio
    async def test_enforce_compliance_hipaa(self, compliance_enforcer, sample_system_data):
        """Test HIPAA compliance enforcement"""
        result = await compliance_enforcer.enforce_compliance(
            ComplianceStandard.HIPAA, sample_system_data
        )
        
        assert result["standard"] == ComplianceStandard.HIPAA.value
        assert result["status"] == "enforced"
        
        # HIPAA should focus on access control and encryption
        assessment = result["assessment"]
        assert len(assessment.assessed_requirements) > 0
        
        # Check for HIPAA-specific requirements
        requirement_ids = [req["requirement_id"] for req in assessment.assessed_requirements]
        assert any("access_control" in req_id for req_id in requirement_ids)
        assert any("encryption" in req_id for req_id in requirement_ids)
    
    @pytest.mark.asyncio
    async def test_get_compliance_status(self, compliance_enforcer, sample_system_data):
        """Test compliance status retrieval"""
        # First enforce compliance to create history
        await compliance_enforcer.enforce_compliance(
            ComplianceStandard.GDPR, sample_system_data
        )
        
        # Test getting status for specific standard
        status = await compliance_enforcer.get_compliance_status(ComplianceStandard.GDPR)
        
        assert isinstance(status, dict)
        assert "standard" in status
        assert "status" in status
        assert "score" in status
        assert "last_assessment" in status

class TestSecurityEvolution:
    """Test SecurityEvolution functionality"""
    
    @pytest.fixture
    def security_evolution(self):
        return SecurityEvolution()
    
    @pytest.fixture
    def sample_threat_landscape(self):
        return {
            "new_threats": ["ai_powered_attacks", "quantum_threats"],
            "sophistication_trend": 0.3,
            "frequency_change": 0.2,
            "new_vectors": ["supply_chain", "cloud_native"],
            "actor_changes": {"nation_state": "increased"},
            "tech_threats": ["deepfake", "adversarial_ml"]
        }
    
    @pytest.fixture
    def sample_performance_metrics(self):
        return {
            "threat_detection_rate": 0.85,
            "response_time": 4.0,
            "false_positive_rate": 0.08,
            "coverage_score": 0.9,
            "automation_level": 0.75,
            "adaptation_speed": 0.7
        }
    
    @pytest.mark.asyncio
    async def test_evolve_security_basic(self, security_evolution, sample_threat_landscape, sample_performance_metrics):
        """Test basic security evolution functionality"""
        result = await security_evolution.evolve_security(
            sample_threat_landscape, sample_performance_metrics
        )
        
        assert isinstance(result, dict)
        assert result["status"] == "evolved"
        assert "current_level" in result
        assert "evolution_plan" in result
        assert "evolution_results" in result
        assert "threat_adaptation" in result
        assert "timestamp" in result
        
        # Check evolution plan structure
        evolution_plan = result["evolution_plan"]
        assert isinstance(evolution_plan, SecurityEvolutionPlan)
        assert isinstance(evolution_plan.current_level, SecurityEvolutionLevel)
        assert isinstance(evolution_plan.target_level, SecurityEvolutionLevel)
        assert isinstance(evolution_plan.enhancement_actions, list)
    
    @pytest.mark.asyncio
    async def test_security_posture_analysis(self, security_evolution, sample_performance_metrics):
        """Test security posture analysis"""
        posture = await security_evolution._analyze_security_posture(sample_performance_metrics)
        
        assert isinstance(posture, dict)
        assert "threat_detection_rate" in posture
        assert "response_time" in posture
        assert "false_positive_rate" in posture
        assert "maturity_score" in posture
        assert "maturity_level" in posture
        
        assert 0 <= posture["maturity_score"] <= 1
        assert isinstance(posture["maturity_level"], SecurityEvolutionLevel)
    
    @pytest.mark.asyncio
    async def test_get_evolution_status(self, security_evolution):
        """Test evolution status retrieval"""
        status = await security_evolution.get_evolution_status()
        
        assert isinstance(status, dict)
        assert "current_level" in status
        assert "evolution_history_count" in status
        assert "capabilities" in status
        assert "next_evolution_target" in status
        assert "timestamp" in status
        
        assert isinstance(status["capabilities"], list)
        assert len(status["capabilities"]) > 0


class TestQuantumSecurity:
    """Test QuantumSecurity functionality"""
    
    @pytest.fixture
    def quantum_security(self):
        return QuantumSecurity()
    
    @pytest.mark.asyncio
    async def test_implement_quantum_resistance_basic(self, quantum_security):
        """Test basic quantum resistance implementation"""
        result = await quantum_security.implement_quantum_resistance(
            QuantumResistanceLevel.QUANTUM_SAFE
        )
        
        assert isinstance(result, dict)
        assert result["status"] == "implemented"
        assert result["resistance_level"] == QuantumResistanceLevel.QUANTUM_SAFE.value
        assert "configuration" in result
        assert "algorithm_results" in result
        assert "authentication_results" in result
        assert "migration_results" in result
        assert "timestamp" in result
    
    @pytest.mark.asyncio
    async def test_quantum_config_generation(self, quantum_security):
        """Test quantum security configuration generation"""
        config = await quantum_security._generate_quantum_config(
            QuantumResistanceLevel.POST_QUANTUM
        )
        
        assert isinstance(config, QuantumSecurityConfig)
        assert config.resistance_level == QuantumResistanceLevel.POST_QUANTUM
        assert len(config.encryption_algorithms) > 0
        assert len(config.key_exchange_methods) > 0
        assert len(config.signature_schemes) > 0
        assert len(config.hash_functions) > 0
        assert len(config.migration_plan) > 0
        
        # Check for post-quantum algorithms
        all_algorithms = (
            config.encryption_algorithms +
            config.key_exchange_methods +
            config.signature_schemes +
            config.hash_functions
        )
        
        # Should include some post-quantum algorithms
        assert any("Kyber" in alg for alg in all_algorithms)
        assert any("Dilithium" in alg for alg in all_algorithms)
    
    @pytest.mark.asyncio
    async def test_quantum_resistance_levels(self, quantum_security):
        """Test different quantum resistance levels"""
        levels_to_test = [
            QuantumResistanceLevel.CLASSICAL,
            QuantumResistanceLevel.QUANTUM_SAFE,
            QuantumResistanceLevel.POST_QUANTUM,
            QuantumResistanceLevel.QUANTUM_PROOF
        ]
        
        for level in levels_to_test:
            result = await quantum_security.implement_quantum_resistance(level)
            
            assert result["status"] == "implemented"
            assert result["resistance_level"] == level.value
            
            # Higher levels should have more advanced algorithms
            config = result["configuration"]
            if level in [QuantumResistanceLevel.POST_QUANTUM, QuantumResistanceLevel.QUANTUM_PROOF]:
                all_algs = (
                    config.encryption_algorithms +
                    config.key_exchange_methods +
                    config.signature_schemes
                )
                assert any("Kyber" in alg or "Dilithium" in alg or "Falcon" in alg for alg in all_algs)
    
    @pytest.mark.asyncio
    async def test_get_quantum_status(self, quantum_security):
        """Test quantum security status retrieval"""
        status = await quantum_security.get_quantum_status()
        
        assert isinstance(status, dict)
        assert "quantum_resistance_level" in status
        assert "implemented_algorithms" in status
        assert "migration_progress" in status
        assert "authentication_methods" in status
        assert "quantum_readiness_score" in status
        assert "last_update" in status
        
        assert 0 <= status["quantum_readiness_score"] <= 1


if __name__ == "__main__":
    pytest.main([__file__])