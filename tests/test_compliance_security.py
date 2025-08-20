"""
Tests for Compliance and Security Evolution

This module contains comprehensive tests for compliance management,
security evolution, and quantum-resistant security capabilities.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock

from core.supreme.engines.compliance_security import (
    ComplianceEnforcer,
    SecurityEvolution,
    QuantumSecurity,
    ComplianceStandard,
    SecurityLevel,
    ComplianceStatus,
    ThreatLevel,
    ComplianceRule,
    ComplianceAssessment,
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
            "consent_management_enabled": True,
            "data_subject_rights_implemented": True,
            "encryption_at_rest": True,
            "encryption_in_transit": True,
            "cardholder_data_encrypted": True,
            "access_controls_enabled": True
        }
    
    def test_compliance_enforcer_initialization(self, compliance_enforcer):
        """Test ComplianceEnforcer initialization"""
        assert isinstance(compliance_enforcer.compliance_rules, dict)
        assert isinstance(compliance_enforcer.assessment_history, list)
        assert isinstance(compliance_enforcer.active_standards, set)
        
        # Check that rules are initialized
        assert ComplianceStandard.GDPR in compliance_enforcer.compliance_rules
        assert ComplianceStandard.HIPAA in compliance_enforcer.compliance_rules
        assert ComplianceStandard.PCI_DSS in compliance_enforcer.compliance_rules
        
        # Check GDPR rules
        gdpr_rules = compliance_enforcer.compliance_rules[ComplianceStandard.GDPR]
        assert len(gdpr_rules) >= 2
        assert any(rule.rule_id == "GDPR_001" for rule in gdpr_rules)
        assert any(rule.rule_id == "GDPR_002" for rule in gdpr_rules)
    
    @pytest.mark.asyncio
    async def test_assess_compliance_gdpr_compliant(self, compliance_enforcer, sample_system_data):
        """Test GDPR compliance assessment - compliant scenario"""
        assessment = await compliance_enforcer.assess_compliance(
            ComplianceStandard.GDPR, sample_system_data
        )
        
        assert isinstance(assessment, ComplianceAssessment)
        assert assessment.standard == ComplianceStandard.GDPR
        assert assessment.status == ComplianceStatus.COMPLIANT
        assert assessment.compliance_score == 100.0
        assert len(assessment.violations) == 0
        assert isinstance(assessment.assessment_time, datetime)
        assert isinstance(assessment.next_review_date, datetime)
    
    @pytest.mark.asyncio
    async def test_assess_compliance_gdpr_non_compliant(self, compliance_enforcer):
        """Test GDPR compliance assessment - non-compliant scenario"""
        non_compliant_data = {
            "consent_management_enabled": False,
            "data_subject_rights_implemented": False
        }
        
        assessment = await compliance_enforcer.assess_compliance(
            ComplianceStandard.GDPR, non_compliant_data
        )
        
        assert assessment.standard == ComplianceStandard.GDPR
        assert assessment.status == ComplianceStatus.NON_COMPLIANT
        assert assessment.compliance_score == 0.0
        assert len(assessment.violations) == 2
        assert len(assessment.recommendations) > 0
        assert len(assessment.remediation_plan) > 0
    
    @pytest.mark.asyncio
    async def test_assess_compliance_hipaa(self, compliance_enforcer, sample_system_data):
        """Test HIPAA compliance assessment"""
        assessment = await compliance_enforcer.assess_compliance(
            ComplianceStandard.HIPAA, sample_system_data
        )
        
        assert assessment.standard == ComplianceStandard.HIPAA
        assert assessment.status == ComplianceStatus.COMPLIANT
        assert assessment.compliance_score == 100.0
        assert len(assessment.violations) == 0
    
    @pytest.mark.asyncio
    async def test_assess_compliance_pci_dss(self, compliance_enforcer, sample_system_data):
        """Test PCI DSS compliance assessment"""
        assessment = await compliance_enforcer.assess_compliance(
            ComplianceStandard.PCI_DSS, sample_system_data
        )
        
        assert assessment.standard == ComplianceStandard.PCI_DSS
        assert assessment.status == ComplianceStatus.COMPLIANT
        assert assessment.compliance_score == 100.0
        assert len(assessment.violations) == 0
    
    @pytest.mark.asyncio
    async def test_assess_compliance_unknown_standard(self, compliance_enforcer):
        """Test compliance assessment for unknown standard"""
        # Create a mock standard not in the rules
        mock_standard = Mock()
        mock_standard.value = "unknown_standard"
        
        assessment = await compliance_enforcer.assess_compliance(mock_standard)
        
        assert assessment.status == ComplianceStatus.UNDER_REVIEW
        assert assessment.compliance_score == 0.0
        assert "Define compliance rules" in assessment.recommendations[0]
    
    @pytest.mark.asyncio
    async def test_enforce_compliance(self, compliance_enforcer):
        """Test compliance enforcement"""
        # Create a non-compliant assessment
        non_compliant_data = {"consent_management_enabled": False}
        assessment = await compliance_enforcer.assess_compliance(
            ComplianceStandard.GDPR, non_compliant_data
        )
        
        # Enforce compliance
        enforcement_result = await compliance_enforcer.enforce_compliance(assessment)
        
        assert isinstance(enforcement_result, dict)
        assert "assessment_id" in enforcement_result
        assert "standard" in enforcement_result
        assert "enforcement_results" in enforcement_result
        assert "total_violations" in enforcement_result
        assert "remediated_violations" in enforcement_result
        assert enforcement_result["total_violations"] > 0
    
    @pytest.mark.asyncio
    async def test_get_compliance_dashboard(self, compliance_enforcer, sample_system_data):
        """Test compliance dashboard generation"""
        # Perform some assessments first
        await compliance_enforcer.assess_compliance(ComplianceStandard.GDPR, sample_system_data)
        await compliance_enforcer.assess_compliance(ComplianceStandard.HIPAA, sample_system_data)
        
        dashboard = await compliance_enforcer.get_compliance_dashboard()
        
        assert isinstance(dashboard, dict)
        assert "overall_compliance_score" in dashboard
        assert "standards_status" in dashboard
        assert "total_assessments" in dashboard
        assert "last_updated" in dashboard
        
        assert dashboard["overall_compliance_score"] > 0
        assert dashboard["total_assessments"] == 2
        assert "gdpr" in dashboard["standards_status"]
        assert "hipaa" in dashboard["standards_status"]


class TestSecurityEvolution:
    """Test SecurityEvolution functionality"""
    
    @pytest.fixture
    def security_evolution(self):
        return SecurityEvolution()
    
    @pytest.fixture
    def sample_threat_data(self):
        return {
            "malware_detections": 200,
            "phishing_attempts": 80,
            "brute_force_attacks": 30,
            "zero_day_exploits": 2,
            "insider_threats": 4,
            "ddos_attempts": 12,
            "data_breach_attempts": 6,
            "social_engineering": 25
        }
    
    def test_security_evolution_initialization(self, security_evolution):
        """Test SecurityEvolution initialization"""
        assert security_evolution.current_security_level == SecurityLevel.BASIC
        assert isinstance(security_evolution.threat_intelligence, dict)
        assert isinstance(security_evolution.evolution_history, list)
        assert isinstance(security_evolution.security_metrics, dict)
    
    @pytest.mark.asyncio
    async def test_analyze_threat_landscape(self, security_evolution, sample_threat_data):
        """Test threat landscape analysis"""
        analysis = await security_evolution.analyze_threat_landscape(sample_threat_data)
        
        assert isinstance(analysis, dict)
        assert "threat_level" in analysis
        assert "emerging_threats" in analysis
        assert "attack_vectors" in analysis
        assert "vulnerability_trends" in analysis
        assert "recommended_security_level" in analysis
        
        assert isinstance(analysis["threat_level"], ThreatLevel)
        assert isinstance(analysis["emerging_threats"], list)
        assert isinstance(analysis["attack_vectors"], list)
        assert isinstance(analysis["vulnerability_trends"], list)
        assert isinstance(analysis["recommended_security_level"], SecurityLevel)
    
    def test_calculate_threat_level(self, security_evolution):
        """Test threat level calculation"""
        # Test different threat levels
        minimal_threats = {"malware_detections": 5}
        low_threats = {"malware_detections": 15}
        moderate_threats = {"malware_detections": 60}
        high_threats = {"malware_detections": 150}
        critical_threats = {"malware_detections": 250}
        extreme_threats = {"malware_detections": 350}
        
        assert security_evolution._calculate_threat_level(minimal_threats) == ThreatLevel.MINIMAL
        assert security_evolution._calculate_threat_level(low_threats) == ThreatLevel.LOW
        assert security_evolution._calculate_threat_level(moderate_threats) == ThreatLevel.MODERATE
        assert security_evolution._calculate_threat_level(high_threats) == ThreatLevel.HIGH
        assert security_evolution._calculate_threat_level(critical_threats) == ThreatLevel.CRITICAL
        assert security_evolution._calculate_threat_level(extreme_threats) == ThreatLevel.EXTREME
    
    def test_identify_emerging_threats(self, security_evolution):
        """Test emerging threat identification"""
        threat_data = {
            "zero_day_exploits": 1,
            "phishing_attempts": 60,
            "insider_threats": 5,
            "ddos_attempts": 8
        }
        
        emerging_threats = security_evolution._identify_emerging_threats(threat_data)
        
        assert isinstance(emerging_threats, list)
        assert any("zero-day" in threat.lower() for threat in emerging_threats)
        assert any("phishing" in threat.lower() for threat in emerging_threats)
        assert any("insider" in threat.lower() for threat in emerging_threats)
        assert any("ddos" in threat.lower() for threat in emerging_threats)
    
    def test_recommend_security_level(self, security_evolution):
        """Test security level recommendation"""
        # Test different threat scenarios
        minimal_data = {"malware_detections": 5}
        extreme_data = {"malware_detections": 350}
        
        minimal_level = security_evolution._recommend_security_level(minimal_data)
        extreme_level = security_evolution._recommend_security_level(extreme_data)
        
        assert minimal_level == SecurityLevel.BASIC
        assert extreme_level == SecurityLevel.QUANTUM
    
    @pytest.mark.asyncio
    async def test_create_evolution_plan(self, security_evolution):
        """Test security evolution plan creation"""
        plan = await security_evolution.create_evolution_plan(SecurityLevel.ADVANCED)
        
        assert isinstance(plan, SecurityEvolutionPlan)
        assert plan.current_level == SecurityLevel.BASIC
        assert plan.target_level == SecurityLevel.ADVANCED
        assert isinstance(plan.enhancement_actions, list)
        assert len(plan.enhancement_actions) > 0
        assert isinstance(plan.implementation_timeline, dict)
        assert isinstance(plan.resource_requirements, dict)
        assert isinstance(plan.success_metrics, list)
        assert isinstance(plan.rollback_strategy, list)
    
    def test_generate_enhancement_actions(self, security_evolution):
        """Test enhancement action generation"""
        actions = security_evolution._generate_enhancement_actions(
            SecurityLevel.BASIC, SecurityLevel.QUANTUM
        )
        
        assert isinstance(actions, list)
        assert len(actions) > 0
        
        # Check for expected actions at different levels
        assert any("multi-factor authentication" in action.lower() for action in actions)
        assert any("quantum" in action.lower() for action in actions)
    
    @pytest.mark.asyncio
    async def test_execute_evolution_plan(self, security_evolution):
        """Test evolution plan execution"""
        plan = await security_evolution.create_evolution_plan(SecurityLevel.ENHANCED)
        result = await security_evolution.execute_evolution_plan(plan)
        
        assert isinstance(result, dict)
        assert "plan_id" in result
        assert "execution_results" in result
        assert "total_actions" in result
        assert "successful_actions" in result
        assert "current_security_level" in result
        assert "timestamp" in result
        
        assert result["total_actions"] == len(plan.enhancement_actions)


class TestQuantumSecurity:
    """Test QuantumSecurity functionality"""
    
    @pytest.fixture
    def quantum_security(self):
        return QuantumSecurity()
    
    def test_quantum_security_initialization(self, quantum_security):
        """Test QuantumSecurity initialization"""
        assert isinstance(quantum_security.quantum_algorithms, dict)
        assert "CRYSTALS-Kyber" in quantum_security.quantum_algorithms
        assert "CRYSTALS-Dilithium" in quantum_security.quantum_algorithms
        assert "FALCON" in quantum_security.quantum_algorithms
        assert "SPHINCS+" in quantum_security.quantum_algorithms
        
        assert quantum_security.active_config is None
        assert isinstance(quantum_security.key_rotation_schedule, dict)
    
    @pytest.mark.asyncio
    async def test_initialize_quantum_security(self, quantum_security):
        """Test quantum security initialization"""
        config = await quantum_security.initialize_quantum_security()
        
        assert isinstance(config, QuantumSecurityConfig)
        assert config.encryption_algorithm == "CRYSTALS-Kyber"
        assert config.key_size > 0
        assert config.quantum_resistance_level in ["low", "medium", "high", "very_high"]
        assert config.authentication_method == "quantum_digital_signature"
        assert isinstance(config.key_rotation_interval, timedelta)
        assert isinstance(config.backup_algorithms, list)
        assert 0 <= config.performance_impact <= 1
        
        assert quantum_security.active_config == config
    
    @pytest.mark.asyncio
    async def test_initialize_quantum_security_custom_algorithm(self, quantum_security):
        """Test quantum security initialization with custom algorithm"""
        config = await quantum_security.initialize_quantum_security("CRYSTALS-Dilithium")
        
        assert config.encryption_algorithm == "CRYSTALS-Dilithium"
        assert config.key_size == 2420
    
    @pytest.mark.asyncio
    async def test_initialize_quantum_security_invalid_algorithm(self, quantum_security):
        """Test quantum security initialization with invalid algorithm"""
        config = await quantum_security.initialize_quantum_security("InvalidAlgorithm")
        
        # Should fallback to default
        assert config.encryption_algorithm == "CRYSTALS-Kyber"
    
    @pytest.mark.asyncio
    async def test_generate_quantum_keys(self, quantum_security):
        """Test quantum key generation"""
        keys = await quantum_security.generate_quantum_keys()
        
        assert isinstance(keys, dict)
        assert "private_key" in keys
        assert "public_key" in keys
        assert "algorithm" in keys
        assert "key_size" in keys
        assert "generated_at" in keys
        
        assert keys["private_key"]
        assert keys["public_key"]
        assert keys["algorithm"] == "CRYSTALS-Kyber"
        assert keys["key_size"] > 0
    
    @pytest.mark.asyncio
    async def test_quantum_encrypt_decrypt(self, quantum_security):
        """Test quantum encryption and decryption"""
        # Generate keys
        keys = await quantum_security.generate_quantum_keys()
        
        # Test data
        original_data = "This is a test message for quantum encryption"
        
        # Encrypt
        encrypted_data = await quantum_security.quantum_encrypt(
            original_data, keys["public_key"]
        )
        
        assert encrypted_data
        assert encrypted_data != original_data
        
        # Decrypt
        decrypted_data = await quantum_security.quantum_decrypt(
            encrypted_data, keys["private_key"]
        )
        
        assert decrypted_data == original_data
    
    @pytest.mark.asyncio
    async def test_quantum_authenticate_verify(self, quantum_security):
        """Test quantum authentication and verification"""
        # Generate keys
        keys = await quantum_security.generate_quantum_keys()
        
        # Test message
        message = "This is a test message for quantum authentication"
        
        # Create signature
        signature = await quantum_security.quantum_authenticate(
            message, keys["private_key"]
        )
        
        assert signature
        
        # Verify signature
        is_valid = await quantum_security.verify_quantum_signature(
            message, signature, keys["public_key"]
        )
        
        assert is_valid
        
        # Test with tampered message
        tampered_message = "This is a tampered message"
        is_valid_tampered = await quantum_security.verify_quantum_signature(
            tampered_message, signature, keys["public_key"]
        )
        
        assert not is_valid_tampered
    
    @pytest.mark.asyncio
    async def test_rotate_quantum_keys(self, quantum_security):
        """Test quantum key rotation"""
        # Initialize quantum security
        await quantum_security.initialize_quantum_security()
        
        # Test rotation when not due
        result = await quantum_security.rotate_quantum_keys()
        assert result["status"] == "rotation_not_due"
        
        # Manually set rotation time to past
        quantum_security.key_rotation_schedule["next_rotation"] = datetime.now() - timedelta(hours=1)
        
        # Test rotation when due
        result = await quantum_security.rotate_quantum_keys()
        assert result["status"] == "keys_rotated"
        assert "new_keys" in result
        assert "next_rotation" in result
    
    @pytest.mark.asyncio
    async def test_get_quantum_security_status(self, quantum_security):
        """Test quantum security status retrieval"""
        # Test before initialization
        status = await quantum_security.get_quantum_security_status()
        assert status["status"] == "not_initialized"
        
        # Initialize and test again
        await quantum_security.initialize_quantum_security()
        status = await quantum_security.get_quantum_security_status()
        
        assert status["status"] == "active"
        assert "algorithm" in status
        assert "key_size" in status
        assert "quantum_resistance_level" in status
        assert "performance_impact" in status
        assert "key_rotation_interval" in status
        assert "backup_algorithms" in status
        assert "timestamp" in status


class TestIntegrationScenarios:
    """Test integration scenarios for compliance and security evolution"""
    
    @pytest.fixture
    def compliance_enforcer(self):
        return ComplianceEnforcer()
    
    @pytest.fixture
    def security_evolution(self):
        return SecurityEvolution()
    
    @pytest.fixture
    def quantum_security(self):
        return QuantumSecurity()
    
    @pytest.mark.asyncio
    async def test_comprehensive_security_assessment(self, compliance_enforcer, security_evolution):
        """Test comprehensive security assessment scenario"""
        # Assess compliance
        system_data = {
            "consent_management_enabled": True,
            "data_subject_rights_implemented": True,
            "encryption_at_rest": True,
            "encryption_in_transit": True
        }
        
        gdpr_assessment = await compliance_enforcer.assess_compliance(
            ComplianceStandard.GDPR, system_data
        )
        
        # Analyze threat landscape
        threat_data = {
            "malware_detections": 180,
            "phishing_attempts": 65,
            "zero_day_exploits": 1
        }
        
        threat_analysis = await security_evolution.analyze_threat_landscape(threat_data)
        
        # Create evolution plan
        evolution_plan = await security_evolution.create_evolution_plan()
        
        # Verify results
        assert gdpr_assessment.status == ComplianceStatus.COMPLIANT
        assert threat_analysis["threat_level"] in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]
        assert evolution_plan.target_level in [SecurityLevel.SUPREME, SecurityLevel.ADVANCED, SecurityLevel.QUANTUM]
    
    @pytest.mark.asyncio
    async def test_quantum_security_integration(self, quantum_security, security_evolution):
        """Test quantum security integration scenario"""
        # Initialize quantum security
        config = await quantum_security.initialize_quantum_security()
        
        # Create evolution plan targeting quantum level
        evolution_plan = await security_evolution.create_evolution_plan(SecurityLevel.QUANTUM)
        
        # Generate quantum keys
        keys = await quantum_security.generate_quantum_keys()
        
        # Test quantum operations
        test_data = "Sensitive data requiring quantum protection"
        encrypted_data = await quantum_security.quantum_encrypt(test_data, keys["public_key"])
        decrypted_data = await quantum_security.quantum_decrypt(encrypted_data, keys["private_key"])
        
        # Verify integration
        assert config.encryption_algorithm in quantum_security.quantum_algorithms
        assert evolution_plan.target_level == SecurityLevel.QUANTUM
        assert any("quantum" in action.lower() for action in evolution_plan.enhancement_actions)
        assert decrypted_data == test_data
    
    @pytest.mark.asyncio
    async def test_compliance_driven_security_evolution(self, compliance_enforcer, security_evolution):
        """Test compliance-driven security evolution scenario"""
        # Assess compliance with gaps
        non_compliant_data = {
            "consent_management_enabled": False,
            "encryption_at_rest": False
        }
        
        assessment = await compliance_enforcer.assess_compliance(
            ComplianceStandard.GDPR, non_compliant_data
        )
        
        # Create evolution plan to address compliance gaps
        evolution_plan = await security_evolution.create_evolution_plan(SecurityLevel.ENHANCED)
        
        # Enforce compliance
        enforcement_result = await compliance_enforcer.enforce_compliance(assessment)
        
        # Verify compliance-driven evolution
        assert assessment.status == ComplianceStatus.NON_COMPLIANT
        assert len(assessment.violations) > 0
        assert len(evolution_plan.enhancement_actions) > 0
        assert enforcement_result["total_violations"] > 0
        
        # Check that security enhancements address compliance requirements
        security_actions = [action.lower() for action in evolution_plan.enhancement_actions]
        assert any("authentication" in action for action in security_actions)


if __name__ == "__main__":
    pytest.main([__file__])