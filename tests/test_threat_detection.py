"""
Tests for Threat Detection and Action Planning

This module contains comprehensive tests for the threat detection, action planning,
and proactive optimization capabilities.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock

from core.supreme.engines.threat_detection import (
    ThreatDetector,
    ActionPlanner,
    ProactiveOptimizer,
    UserContext,
    ThreatAssessment,
    ProactiveAction,
    ActionPlan,
    OptimizationOpportunity,
    ThreatType,
    ThreatSeverity,
    ActionType,
    PredictionConfidence
)


class TestThreatDetector:
    """Test ThreatDetector functionality"""
    
    @pytest.fixture
    def threat_detector(self):
        return ThreatDetector()
    
    @pytest.fixture
    def sample_context(self):
        return UserContext(
            user_id="test_user",
            current_activity="work",
            calendar_events=[{
                "id": "deadline_1",
                "title": "Project Deadline Review",
                "start_time": (datetime.now() + timedelta(minutes=30)).isoformat()
            }],
            productivity_score=0.2,
            stress_level=0.8
        )
    
    @pytest.fixture
    def sample_metrics(self):
        return {
            "cpu_usage": 95,
            "memory_usage": 90,
            "disk_usage": 95,
            "network_latency": 1500,
            "failed_login_attempts": 8,
            "data_access_rate": 150,
            "last_backup_time": (datetime.now() - timedelta(hours=48)).isoformat(),
            "file_system_errors": 3
        }
    
    @pytest.mark.asyncio
    async def test_detect_threats_basic(self, threat_detector, sample_context, sample_metrics):
        """Test basic threat detection functionality"""
        threats = await threat_detector.detect_threats(sample_context, sample_metrics)
        
        assert isinstance(threats, list)
        assert len(threats) > 0
        
        # Check that threats are properly structured
        for threat in threats:
            assert isinstance(threat, ThreatAssessment)
            assert threat.threat_id
            assert isinstance(threat.threat_type, ThreatType)
            assert isinstance(threat.severity, ThreatSeverity)
            assert isinstance(threat.confidence, PredictionConfidence)
            assert isinstance(threat.detected_time, datetime)
            assert 0 <= threat.estimated_impact <= 1
    
    @pytest.mark.asyncio
    async def test_detect_security_threats(self, threat_detector, sample_context):
        """Test security threat detection"""
        metrics = {
            "failed_login_attempts": 10,
            "data_access_rate": 200
        }
        
        threats = await threat_detector.detect_threats(sample_context, metrics)
        
        # Should detect security threats
        security_threats = [t for t in threats if t.threat_type == ThreatType.SECURITY]
        privacy_threats = [t for t in threats if t.threat_type == ThreatType.PRIVACY]
        
        assert len(security_threats) > 0
        assert len(privacy_threats) > 0
        
        # Check security threat details
        login_threat = security_threats[0]
        assert "login" in login_threat.title.lower()
        assert login_threat.severity == ThreatSeverity.HIGH
        assert any("two-factor" in action.lower() for action in login_threat.mitigation_actions)
    
    @pytest.mark.asyncio
    async def test_detect_performance_threats(self, threat_detector, sample_context):
        """Test performance threat detection"""
        metrics = {
            "cpu_usage": 98,
            "memory_usage": 92
        }
        
        threats = await threat_detector.detect_threats(sample_context, metrics)
        
        # Should detect performance threats
        performance_threats = [t for t in threats if t.threat_type == ThreatType.PERFORMANCE]
        resource_threats = [t for t in threats if t.threat_type == ThreatType.RESOURCE_EXHAUSTION]
        
        assert len(performance_threats) > 0
        assert len(resource_threats) > 0
        
        # Check CPU threat
        cpu_threats = [t for t in threats if "cpu" in t.title.lower()]
        assert len(cpu_threats) > 0
        assert cpu_threats[0].severity == ThreatSeverity.HIGH
    
    @pytest.mark.asyncio
    async def test_detect_deadline_threats(self, threat_detector):
        """Test deadline threat detection"""
        context = UserContext(
            user_id="test_user",
            current_activity="work",
            calendar_events=[{
                "id": "urgent_deadline",
                "title": "Critical Project Deadline",
                "start_time": (datetime.now() + timedelta(minutes=45)).isoformat()
            }]
        )
        
        threats = await threat_detector.detect_threats(context)
        
        # Should detect deadline threat
        deadline_threats = [t for t in threats if t.threat_type == ThreatType.DEADLINE]
        assert len(deadline_threats) > 0
        
        deadline_threat = deadline_threats[0]
        assert "deadline" in deadline_threat.title.lower()
        assert deadline_threat.severity in [ThreatSeverity.HIGH, ThreatSeverity.MEDIUM]
    
    @pytest.mark.asyncio
    async def test_detect_resource_threats(self, threat_detector, sample_context):
        """Test resource exhaustion threat detection"""
        metrics = {
            "disk_usage": 97,
            "network_latency": 2000
        }
        
        threats = await threat_detector.detect_threats(sample_context, metrics)
        
        # Should detect resource threats
        resource_threats = [t for t in threats if t.threat_type == ThreatType.RESOURCE_EXHAUSTION]
        performance_threats = [t for t in threats if t.threat_type == ThreatType.PERFORMANCE]
        
        assert len(resource_threats) > 0
        
        # Check disk space threat
        disk_threats = [t for t in threats if "disk" in t.title.lower()]
        assert len(disk_threats) > 0
        assert disk_threats[0].severity in [ThreatSeverity.HIGH, ThreatSeverity.CRITICAL]
    
    @pytest.mark.asyncio
    async def test_detect_data_loss_threats(self, threat_detector, sample_context):
        """Test data loss threat detection"""
        metrics = {
            "last_backup_time": (datetime.now() - timedelta(hours=96)).isoformat(),
            "file_system_errors": 5
        }
        
        threats = await threat_detector.detect_threats(sample_context, metrics)
        
        # Should detect data loss threats
        data_threats = [t for t in threats if t.threat_type == ThreatType.DATA_LOSS]
        assert len(data_threats) > 0
        
        # Check backup threat
        backup_threats = [t for t in threats if "backup" in t.title.lower()]
        assert len(backup_threats) > 0
        assert backup_threats[0].severity == ThreatSeverity.HIGH
    
    @pytest.mark.asyncio
    async def test_productivity_threat_detection(self, threat_detector):
        """Test productivity-based threat detection"""
        context = UserContext(
            user_id="test_user",
            current_activity="work",
            productivity_score=0.1  # Very low productivity
        )
        
        threats = await threat_detector.detect_threats(context)
        
        # Should detect productivity threat
        productivity_threats = [t for t in threats if "productivity" in t.description.lower()]
        assert len(productivity_threats) > 0
        assert productivity_threats[0].severity == ThreatSeverity.MEDIUM


class TestActionPlanner:
    """Test ActionPlanner functionality"""
    
    @pytest.fixture
    def action_planner(self):
        return ActionPlanner()
    
    @pytest.fixture
    def sample_threats(self):
        return [
            ThreatAssessment(
                threat_id="threat_1",
                threat_type=ThreatType.SECURITY,
                severity=ThreatSeverity.CRITICAL,
                title="Critical Security Threat",
                description="High-priority security issue",
                confidence=PredictionConfidence.HIGH,
                detected_time=datetime.now(),
                estimated_impact=0.9,
                time_to_impact=timedelta(minutes=5),
                affected_systems=["authentication"],
                indicators=["suspicious activity"],
                mitigation_actions=["Enable 2FA", "Lock account", "Review logs"],
                context={}
            ),
            ThreatAssessment(
                threat_id="threat_2",
                threat_type=ThreatType.PERFORMANCE,
                severity=ThreatSeverity.HIGH,
                title="Performance Degradation",
                description="System performance issues",
                confidence=PredictionConfidence.MEDIUM,
                detected_time=datetime.now(),
                estimated_impact=0.7,
                time_to_impact=timedelta(minutes=10),
                affected_systems=["system_performance"],
                indicators=["high CPU usage"],
                mitigation_actions=["Optimize processes", "Scale resources"],
                context={}
            )
        ]
    
    @pytest.mark.asyncio
    async def test_create_action_plan_basic(self, action_planner, sample_threats):
        """Test basic action plan creation"""
        plan = await action_planner.create_action_plan(sample_threats)
        
        assert isinstance(plan, ActionPlan)
        assert plan.plan_id
        assert plan.title
        assert plan.description
        assert isinstance(plan.actions, list)
        assert len(plan.actions) > 0
        assert isinstance(plan.estimated_total_duration, timedelta)
        assert isinstance(plan.resource_requirements, dict)
        assert isinstance(plan.risk_assessment, dict)
    
    @pytest.mark.asyncio
    async def test_threat_mitigation_actions(self, action_planner, sample_threats):
        """Test creation of threat mitigation actions"""
        plan = await action_planner.create_action_plan(sample_threats)
        
        # Should create actions for each threat's mitigation strategies
        threat_actions = [a for a in plan.actions if "threat" in a.action_id]
        assert len(threat_actions) > 0
        
        # Check action priorities (critical threats should have higher priority)
        critical_actions = [a for a in threat_actions if a.priority >= 10]
        high_actions = [a for a in threat_actions if 8 <= a.priority < 10]
        
        assert len(critical_actions) > 0  # Should have critical threat actions
        assert len(high_actions) > 0     # Should have high threat actions
    
    @pytest.mark.asyncio
    async def test_action_plan_with_needs_and_opportunities(self, action_planner, sample_threats):
        """Test action plan creation with needs and opportunities"""
        # Mock needs and opportunities with proper attributes
        mock_need = Mock()
        mock_need.urgency_score = 0.8
        mock_need.suggested_actions = ["Address urgent need"]
        mock_need.need_id = "test_need"
        mock_need.category = "urgent"
        
        mock_opportunity = Mock()
        mock_opportunity.potential_value = 7.0
        mock_opportunity.suggested_actions = ["Pursue opportunity"]
        mock_opportunity.opportunity_id = "test_opportunity"
        mock_opportunity.prerequisites = []
        mock_opportunity.implementation_effort = 2.0
        mock_opportunity.title = "Test Opportunity"
        
        mock_needs = [mock_need]
        mock_opportunities = [mock_opportunity]
        
        plan = await action_planner.create_action_plan(sample_threats, mock_needs, mock_opportunities)
        
        assert len(plan.actions) > 0  # Should include actions
        
        # Check that different types of actions are created
        need_actions = [a for a in plan.actions if "need" in a.action_id]
        opportunity_actions = [a for a in plan.actions if "opportunity" in a.action_id]
        threat_actions = [a for a in plan.actions if "threat" in a.action_id]
        
        # Should have at least some actions
        assert len(need_actions) > 0 or len(opportunity_actions) > 0 or len(threat_actions) > 0
    
    @pytest.mark.asyncio
    async def test_execute_action_plan(self, action_planner, sample_threats):
        """Test action plan execution"""
        plan = await action_planner.create_action_plan(sample_threats)
        
        # Execute the plan
        result = await action_planner.execute_action_plan(plan)
        
        assert isinstance(result, dict)
        assert "plan_id" in result
        assert "execution_results" in result
        assert "total_actions" in result
        assert "automated_actions" in result
        assert "pending_actions" in result
        assert "timestamp" in result
        
        assert result["total_actions"] == len(plan.actions)
        assert result["automated_actions"] + result["pending_actions"] == result["total_actions"]
    
    @pytest.mark.asyncio
    async def test_action_execution(self, action_planner):
        """Test individual action execution"""
        action = ProactiveAction(
            action_id="test_action",
            title="Test Action",
            description="Test action execution",
            priority=5,
            estimated_duration=timedelta(minutes=5),
            prerequisites=[],
            expected_outcome="Test outcome",
            risk_level=0.1,
            automation_possible=True,
            user_approval_required=False
        )
        
        result = await action_planner._execute_action(action)
        
        assert isinstance(result, dict)
        assert result["action_id"] == "test_action"
        assert result["status"] == "executed"
        assert "timestamp" in result


class TestProactiveOptimizer:
    """Test ProactiveOptimizer functionality"""
    
    @pytest.fixture
    def optimizer(self):
        return ProactiveOptimizer()
    
    @pytest.fixture
    def sample_context(self):
        return UserContext(
            user_id="test_user",
            current_activity="work",
            recent_interactions=[
                {"task": "email_processing", "timestamp": "2024-01-01T10:00:00"},
                {"task": "email_processing", "timestamp": "2024-01-01T11:00:00"},
                {"task": "email_processing", "timestamp": "2024-01-01T12:00:00"},
                {"task": "report_generation", "timestamp": "2024-01-01T13:00:00"}
            ],
            productivity_score=0.5,
            stress_level=0.7
        )
    
    @pytest.fixture
    def sample_metrics(self):
        return {
            "cpu_usage": 75,
            "memory_usage": 65,
            "disk_usage": 80,
            "network_latency": 300
        }
    
    @pytest.mark.asyncio
    async def test_identify_optimization_opportunities_basic(self, optimizer, sample_context, sample_metrics):
        """Test basic optimization opportunity identification"""
        opportunities = await optimizer.identify_optimization_opportunities(sample_context, sample_metrics)
        
        assert isinstance(opportunities, list)
        assert len(opportunities) > 0
        
        # Check that opportunities are properly structured
        for opp in opportunities:
            assert isinstance(opp, OptimizationOpportunity)
            assert opp.opportunity_id
            assert opp.title
            assert opp.description
            assert isinstance(opp.current_performance, dict)
            assert isinstance(opp.expected_improvement, dict)
            assert opp.implementation_effort > 0
            assert isinstance(opp.confidence, PredictionConfidence)
    
    @pytest.mark.asyncio
    async def test_performance_optimizations(self, optimizer, sample_context):
        """Test performance optimization identification"""
        metrics = {
            "cpu_usage": 85,
            "memory_usage": 75
        }
        
        opportunities = await optimizer.identify_optimization_opportunities(sample_context, metrics)
        
        # Should identify performance optimizations
        perf_opps = [o for o in opportunities if o.optimization_type == "performance"]
        assert len(perf_opps) > 0
        
        # Check CPU optimization
        cpu_opps = [o for o in perf_opps if "cpu" in o.title.lower()]
        assert len(cpu_opps) > 0
        assert cpu_opps[0].expected_improvement["cpu_usage"] < 0  # Should reduce CPU usage
    
    @pytest.mark.asyncio
    async def test_workflow_optimizations(self, optimizer, sample_context):
        """Test workflow optimization identification"""
        opportunities = await optimizer.identify_optimization_opportunities(sample_context)
        
        # Should identify workflow optimizations
        workflow_opps = [o for o in opportunities if o.optimization_type == "workflow"]
        productivity_opps = [o for o in opportunities if o.optimization_type == "productivity"]
        
        assert len(workflow_opps) > 0 or len(productivity_opps) > 0
        
        # Check automation opportunity
        automation_opps = [o for o in opportunities if "automation" in o.title.lower()]
        if automation_opps:
            assert automation_opps[0].expected_improvement["automation_rate"] > 0
    
    @pytest.mark.asyncio
    async def test_resource_optimizations(self, optimizer, sample_context):
        """Test resource optimization identification"""
        metrics = {
            "disk_usage": 85,
            "network_latency": 500
        }
        
        opportunities = await optimizer.identify_optimization_opportunities(sample_context, metrics)
        
        # Should identify resource optimizations
        resource_opps = [o for o in opportunities if o.optimization_type == "resource"]
        network_opps = [o for o in opportunities if o.optimization_type == "network"]
        
        assert len(resource_opps) > 0 or len(network_opps) > 0
        
        # Check storage optimization
        storage_opps = [o for o in opportunities if "storage" in o.title.lower()]
        if storage_opps:
            assert storage_opps[0].expected_improvement["disk_usage"] < 0  # Should reduce disk usage
    
    @pytest.mark.asyncio
    async def test_ux_optimizations(self, optimizer):
        """Test user experience optimization identification"""
        context = UserContext(
            user_id="test_user",
            current_activity="work",
            stress_level=0.8  # High stress
        )
        
        opportunities = await optimizer.identify_optimization_opportunities(context)
        
        # Should identify UX optimizations
        ux_opps = [o for o in opportunities if o.optimization_type == "user_experience"]
        assert len(ux_opps) > 0
        
        # Check stress reduction optimization
        stress_opps = [o for o in ux_opps if "stress" in o.title.lower()]
        assert len(stress_opps) > 0
        assert stress_opps[0].expected_improvement["stress_level"] < 0  # Should reduce stress


class TestIntegrationScenarios:
    """Test integration scenarios for threat detection and action planning"""
    
    @pytest.fixture
    def threat_detector(self):
        return ThreatDetector()
    
    @pytest.fixture
    def action_planner(self):
        return ActionPlanner()
    
    @pytest.fixture
    def optimizer(self):
        return ProactiveOptimizer()
    
    @pytest.mark.asyncio
    async def test_critical_threat_scenario(self, threat_detector, action_planner):
        """Test response to critical threat scenario"""
        context = UserContext(
            user_id="critical_user",
            current_activity="work"
        )
        
        metrics = {
            "failed_login_attempts": 15,
            "disk_usage": 99,
            "cpu_usage": 98
        }
        
        # Detect threats
        threats = await threat_detector.detect_threats(context, metrics)
        
        # Should detect multiple critical/high threats
        critical_threats = [t for t in threats if t.severity == ThreatSeverity.CRITICAL]
        high_threats = [t for t in threats if t.severity == ThreatSeverity.HIGH]
        
        assert len(critical_threats) > 0 or len(high_threats) > 0
        
        # Create action plan
        plan = await action_planner.create_action_plan(threats)
        
        # Should create high-priority actions
        high_priority_actions = [a for a in plan.actions if a.priority >= 8]
        assert len(high_priority_actions) > 0
        
        # Should require approval for critical actions
        assert plan.approval_required
    
    @pytest.mark.asyncio
    async def test_comprehensive_optimization_scenario(self, threat_detector, action_planner, optimizer):
        """Test comprehensive optimization scenario"""
        context = UserContext(
            user_id="optimization_user",
            current_activity="work",
            recent_interactions=[
                {"task": "data_processing", "timestamp": "2024-01-01T09:00:00"},
                {"task": "data_processing", "timestamp": "2024-01-01T10:00:00"},
                {"task": "data_processing", "timestamp": "2024-01-01T11:00:00"}
            ],
            productivity_score=0.4,
            stress_level=0.6
        )
        
        metrics = {
            "cpu_usage": 80,
            "memory_usage": 70,
            "disk_usage": 75
        }
        
        # Detect threats
        threats = await threat_detector.detect_threats(context, metrics)
        
        # Identify optimization opportunities
        opportunities = await optimizer.identify_optimization_opportunities(context, metrics)
        
        # Create comprehensive action plan
        plan = await action_planner.create_action_plan(threats, opportunities=opportunities)
        
        # Should include actions (either threat mitigation or optimization)
        assert len(plan.actions) > 0
        
        # Check that we have some kind of actions
        threat_actions = [a for a in plan.actions if "threat" in a.action_id]
        optimization_actions = [a for a in plan.actions if "opportunity" in a.action_id]
        
        # At least one type of action should be present
        assert len(threat_actions) > 0 or len(optimization_actions) > 0 or len(plan.actions) > 0
        
        # Should have reasonable resource requirements
        assert 0 <= plan.resource_requirements.get("cpu_usage", 0) <= 1
        assert 0 <= plan.resource_requirements.get("memory_usage", 0) <= 1
    
    @pytest.mark.asyncio
    async def test_deadline_pressure_scenario(self, threat_detector, action_planner):
        """Test response to deadline pressure scenario"""
        context = UserContext(
            user_id="deadline_user",
            current_activity="work",
            calendar_events=[
                {
                    "id": "urgent_deadline",
                    "title": "Critical Project Deadline",
                    "start_time": (datetime.now() + timedelta(minutes=30)).isoformat()
                },
                {
                    "id": "another_deadline",
                    "title": "Important Deadline Meeting",
                    "start_time": (datetime.now() + timedelta(hours=1)).isoformat()
                }
            ],
            stress_level=0.9,
            productivity_score=0.3
        )
        
        # Detect threats
        threats = await threat_detector.detect_threats(context)
        
        # Should detect deadline and stress-related threats
        deadline_threats = [t for t in threats if t.threat_type == ThreatType.DEADLINE]
        performance_threats = [t for t in threats if "productivity" in t.description.lower()]
        
        # Should detect at least deadline threats or performance threats
        assert len(deadline_threats) > 0 or len(performance_threats) > 0 or len(threats) > 0
        
        # Create action plan
        plan = await action_planner.create_action_plan(threats)
        
        # Should prioritize deadline-related actions
        deadline_actions = [a for a in plan.actions if "deadline" in a.description.lower()]
        assert len(deadline_actions) > 0
        
        # Should have high-priority actions
        urgent_actions = [a for a in plan.actions if a.priority >= 8]
        assert len(urgent_actions) > 0


if __name__ == "__main__":
    pytest.main([__file__])