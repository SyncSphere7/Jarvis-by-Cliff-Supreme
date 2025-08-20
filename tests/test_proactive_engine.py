"""
Tests for Proactive Intelligence Engine

This module contains comprehensive tests for the proactive intelligence capabilities
including need prediction, opportunity scanning, and proactive orchestration.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock

from core.supreme.engines.proactive_engine import (
    ProactiveIntelligenceEngine,
    ProactiveOrchestrator,
    NeedPredictor,
    OpportunityScanner,
    UserContext,
    PredictedNeed,
    Opportunity,
    ProactiveAction,
    NeedCategory,
    OpportunityType,
    PredictionConfidence
)


class TestUserContext:
    """Test UserContext data model"""
    
    def test_user_context_creation(self):
        """Test UserContext creation with default values"""
        context = UserContext(
            user_id="test_user",
            current_activity="work"
        )
        
        assert context.user_id == "test_user"
        assert context.current_activity == "work"
        assert context.location is None
        assert isinstance(context.time_of_day, datetime)
        assert context.recent_interactions == []
        assert context.goals == []
        assert context.preferences == {}
        assert context.behavioral_patterns == {}
        assert context.calendar_events == []
        assert context.stress_level == 0.0
        assert context.productivity_score == 0.0
    
    def test_user_context_with_data(self):
        """Test UserContext with comprehensive data"""
        context = UserContext(
            user_id="test_user",
            current_activity="meeting",
            location="office",
            recent_interactions=[{"task": "email", "timestamp": "2024-01-01T10:00:00"}],
            goals=["learn python", "improve productivity"],
            preferences={"notification_style": "minimal"},
            behavioral_patterns={"coffee_time": "2024-01-01T09:00:00"},
            calendar_events=[{
                "id": "meeting_1",
                "title": "Team Meeting",
                "start_time": (datetime.now() + timedelta(minutes=20)).isoformat()
            }],
            stress_level=0.6,
            productivity_score=0.8
        )
        
        assert len(context.recent_interactions) == 1
        assert len(context.goals) == 2
        assert "coffee_time" in context.behavioral_patterns
        assert len(context.calendar_events) == 1
        assert context.stress_level == 0.6
        assert context.productivity_score == 0.8


class TestNeedPredictor:
    """Test NeedPredictor functionality"""
    
    @pytest.fixture
    def need_predictor(self):
        return NeedPredictor()
    
    @pytest.fixture
    def sample_context(self):
        return UserContext(
            user_id="test_user",
            current_activity="work",
            behavioral_patterns={"coffee_time": datetime.now().isoformat()},
            calendar_events=[{
                "id": "meeting_1",
                "title": "Important Meeting",
                "start_time": (datetime.now() + timedelta(minutes=25)).isoformat()
            }],
            productivity_score=0.3,
            stress_level=0.8
        )
    
    @pytest.mark.asyncio
    async def test_predict_needs_basic(self, need_predictor, sample_context):
        """Test basic need prediction functionality"""
        needs = await need_predictor.predict_needs(sample_context)
        
        assert isinstance(needs, list)
        assert len(needs) > 0
        
        # Check that needs are properly structured
        for need in needs:
            assert isinstance(need, PredictedNeed)
            assert need.need_id
            assert isinstance(need.category, NeedCategory)
            assert isinstance(need.confidence, PredictionConfidence)
            assert isinstance(need.predicted_time, datetime)
            assert 0 <= need.urgency_score <= 1
    
    @pytest.mark.asyncio
    async def test_behavioral_pattern_prediction(self, need_predictor):
        """Test prediction based on behavioral patterns"""
        context = UserContext(
            user_id="test_user",
            current_activity="work",
            behavioral_patterns={"coffee_time": datetime.now().isoformat()}
        )
        
        needs = await need_predictor.predict_needs(context)
        
        # Should predict coffee need
        coffee_needs = [n for n in needs if "coffee" in n.description.lower()]
        assert len(coffee_needs) > 0
        assert coffee_needs[0].category == NeedCategory.IMMEDIATE
    
    @pytest.mark.asyncio
    async def test_productivity_pattern_prediction(self, need_predictor):
        """Test prediction based on productivity patterns"""
        context = UserContext(
            user_id="test_user",
            current_activity="work",
            productivity_score=0.2  # Very low productivity
        )
        
        needs = await need_predictor.predict_needs(context)
        
        # Should predict productivity optimization need
        productivity_needs = [n for n in needs if "productivity" in n.description.lower()]
        assert len(productivity_needs) > 0
        assert productivity_needs[0].urgency_score > 0.4
    
    @pytest.mark.asyncio
    async def test_stress_pattern_prediction(self, need_predictor):
        """Test prediction based on stress patterns"""
        context = UserContext(
            user_id="test_user",
            current_activity="work",
            stress_level=0.9  # Very high stress
        )
        
        needs = await need_predictor.predict_needs(context)
        
        # Should predict stress relief need
        stress_needs = [n for n in needs if "stress" in n.description.lower()]
        assert len(stress_needs) > 0
        assert stress_needs[0].category == NeedCategory.IMMEDIATE
        assert stress_needs[0].urgency_score > 0.8
    
    @pytest.mark.asyncio
    async def test_schedule_pattern_prediction(self, need_predictor):
        """Test prediction based on schedule patterns"""
        context = UserContext(
            user_id="test_user",
            current_activity="work",
            calendar_events=[{
                "id": "meeting_1",
                "title": "Important Meeting",
                "start_time": (datetime.now() + timedelta(minutes=20)).isoformat()
            }]
        )
        
        needs = await need_predictor.predict_needs(context)
        
        # Should predict preparation need
        prep_needs = [n for n in needs if "preparation" in n.description.lower()]
        assert len(prep_needs) > 0
        assert prep_needs[0].category == NeedCategory.SHORT_TERM


class TestOpportunityScanner:
    """Test OpportunityScanner functionality"""
    
    @pytest.fixture
    def opportunity_scanner(self):
        return OpportunityScanner()
    
    @pytest.fixture
    def sample_context(self):
        return UserContext(
            user_id="test_user",
            current_activity="work",
            goals=["learn python", "improve career", "automate tasks"],
            recent_interactions=[
                {"task": "email_check", "timestamp": "2024-01-01T10:00:00"},
                {"task": "email_check", "timestamp": "2024-01-01T11:00:00"},
                {"task": "email_check", "timestamp": "2024-01-01T12:00:00"},
                {"task": "report_generation", "timestamp": "2024-01-01T13:00:00"},
                {"task": "report_generation", "timestamp": "2024-01-01T14:00:00"}
            ],
            productivity_score=0.6
        )
    
    @pytest.mark.asyncio
    async def test_scan_opportunities_basic(self, opportunity_scanner, sample_context):
        """Test basic opportunity scanning functionality"""
        opportunities = await opportunity_scanner.scan_opportunities(sample_context)
        
        assert isinstance(opportunities, list)
        assert len(opportunities) > 0
        
        # Check that opportunities are properly structured
        for opp in opportunities:
            assert isinstance(opp, Opportunity)
            assert opp.opportunity_id
            assert isinstance(opp.type, OpportunityType)
            assert isinstance(opp.confidence, PredictionConfidence)
            assert opp.potential_value > 0
            assert opp.effort_required > 0
    
    @pytest.mark.asyncio
    async def test_productivity_opportunity_scanning(self, opportunity_scanner):
        """Test scanning for productivity opportunities"""
        context = UserContext(
            user_id="test_user",
            current_activity="work",
            recent_interactions=[
                {"task": "data_entry", "timestamp": "2024-01-01T10:00:00"},
                {"task": "data_entry", "timestamp": "2024-01-01T11:00:00"},
                {"task": "data_entry", "timestamp": "2024-01-01T12:00:00"},
                {"task": "data_entry", "timestamp": "2024-01-01T13:00:00"}
            ]
        )
        
        opportunities = await opportunity_scanner.scan_opportunities(context)
        
        # Should find automation opportunity
        automation_opps = [o for o in opportunities if o.type == OpportunityType.PRODUCTIVITY]
        assert len(automation_opps) > 0
        assert "automation" in automation_opps[0].title.lower()
    
    @pytest.mark.asyncio
    async def test_learning_opportunity_scanning(self, opportunity_scanner):
        """Test scanning for learning opportunities"""
        context = UserContext(
            user_id="test_user",
            current_activity="work",
            goals=["learn machine learning", "improve data science skills"]
        )
        
        opportunities = await opportunity_scanner.scan_opportunities(context)
        
        # Should find learning opportunities
        learning_opps = [o for o in opportunities if o.type == OpportunityType.LEARNING]
        assert len(learning_opps) > 0
        assert any("learn" in opp.title.lower() for opp in learning_opps)
    
    @pytest.mark.asyncio
    async def test_optimization_opportunity_scanning(self, opportunity_scanner):
        """Test scanning for optimization opportunities"""
        context = UserContext(
            user_id="test_user",
            current_activity="work",
            productivity_score=0.4  # Low productivity
        )
        
        opportunities = await opportunity_scanner.scan_opportunities(context)
        
        # Should find optimization opportunity
        optimization_opps = [o for o in opportunities if o.type == OpportunityType.OPTIMIZATION]
        assert len(optimization_opps) > 0
        assert "optimization" in optimization_opps[0].title.lower()
    
    @pytest.mark.asyncio
    async def test_social_opportunity_scanning(self, opportunity_scanner):
        """Test scanning for social/networking opportunities"""
        context = UserContext(
            user_id="test_user",
            current_activity="work",
            goals=["advance career", "expand professional network"]
        )
        
        opportunities = await opportunity_scanner.scan_opportunities(context)
        
        # Should find networking opportunity
        social_opps = [o for o in opportunities if o.type == OpportunityType.SOCIAL]
        assert len(social_opps) > 0
        assert "networking" in social_opps[0].title.lower()


class TestProactiveOrchestrator:
    """Test ProactiveOrchestrator functionality"""
    
    @pytest.fixture
    def orchestrator(self):
        return ProactiveOrchestrator()
    
    @pytest.fixture
    def sample_context(self):
        return UserContext(
            user_id="test_user",
            current_activity="work",
            goals=["learn python", "improve productivity"],
            productivity_score=0.3,
            stress_level=0.8,
            recent_interactions=[
                {"task": "email", "timestamp": "2024-01-01T10:00:00"},
                {"task": "email", "timestamp": "2024-01-01T11:00:00"},
                {"task": "email", "timestamp": "2024-01-01T12:00:00"}
            ]
        )
    
    @pytest.mark.asyncio
    async def test_orchestrate_proactive_intelligence(self, orchestrator, sample_context):
        """Test main orchestration functionality"""
        result = await orchestrator.orchestrate_proactive_intelligence(sample_context)
        
        assert isinstance(result, dict)
        assert "predicted_needs" in result
        assert "opportunities" in result
        assert "planned_actions" in result
        assert "execution_results" in result
        assert "timestamp" in result
        assert "user_id" in result
        
        assert result["user_id"] == "test_user"
        assert isinstance(result["predicted_needs"], list)
        assert isinstance(result["opportunities"], list)
        assert isinstance(result["planned_actions"], list)
        assert isinstance(result["execution_results"], list)
    
    @pytest.mark.asyncio
    async def test_plan_proactive_actions(self, orchestrator):
        """Test proactive action planning"""
        # Create sample needs and opportunities
        needs = [
            PredictedNeed(
                need_id="need_1",
                category=NeedCategory.IMMEDIATE,
                description="High stress detected",
                confidence=PredictionConfidence.HIGH,
                predicted_time=datetime.now(),
                urgency_score=0.9,
                context={},
                suggested_actions=["Take a break"]
            )
        ]
        
        opportunities = [
            Opportunity(
                opportunity_id="opp_1",
                type=OpportunityType.PRODUCTIVITY,
                title="Automation Opportunity",
                description="Automate repetitive tasks",
                confidence=PredictionConfidence.HIGH,
                potential_value=8.0,
                effort_required=2.0,
                time_window=(datetime.now(), datetime.now() + timedelta(days=7)),
                prerequisites=[],
                suggested_actions=["Analyze tasks"],
                context={}
            )
        ]
        
        actions = await orchestrator.plan_proactive_actions(needs, opportunities)
        
        assert isinstance(actions, list)
        assert len(actions) == 2  # One for need, one for opportunity
        
        for action in actions:
            assert isinstance(action, ProactiveAction)
            assert action.action_id
            assert action.title
            assert action.priority > 0
    
    @pytest.mark.asyncio
    async def test_execute_automated_actions(self, orchestrator):
        """Test automated action execution"""
        actions = [
            ProactiveAction(
                action_id="action_1",
                title="Test Action",
                description="Test automated action",
                priority=8,
                estimated_duration=timedelta(minutes=5),
                prerequisites=[],
                expected_outcome="Test outcome",
                risk_level=0.1,
                automation_possible=True,
                user_approval_required=False
            ),
            ProactiveAction(
                action_id="action_2",
                title="Manual Action",
                description="Test manual action",
                priority=7,
                estimated_duration=timedelta(minutes=10),
                prerequisites=[],
                expected_outcome="Manual outcome",
                risk_level=0.3,
                automation_possible=False,
                user_approval_required=True
            )
        ]
        
        results = await orchestrator._execute_automated_actions(actions)
        
        assert isinstance(results, list)
        assert len(results) == 1  # Only automated action should be executed
        assert results[0]["action_id"] == "action_1"
        assert results[0]["status"] == "executed"
    
    @pytest.mark.asyncio
    async def test_get_proactive_analytics(self, orchestrator):
        """Test proactive analytics retrieval"""
        analytics = await orchestrator.get_proactive_analytics()
        
        assert isinstance(analytics, dict)
        assert "active_actions" in analytics
        assert "execution_history" in analytics
        assert "success_rate" in analytics
        assert "average_response_time" in analytics
        assert "user_satisfaction" in analytics
        assert "automation_rate" in analytics
        assert "timestamp" in analytics
        
        assert isinstance(analytics["active_actions"], int)
        assert isinstance(analytics["success_rate"], float)
        assert 0 <= analytics["success_rate"] <= 1


class TestProactiveIntelligenceEngine:
    """Test main ProactiveIntelligenceEngine"""
    
    @pytest.fixture
    def engine(self):
        return ProactiveIntelligenceEngine()
    
    @pytest.fixture
    def sample_context(self):
        return UserContext(
            user_id="test_user",
            current_activity="work",
            goals=["improve productivity"],
            productivity_score=0.5
        )
    
    @pytest.mark.asyncio
    async def test_predict_needs(self, engine, sample_context):
        """Test need prediction through main engine"""
        needs = await engine.predict_needs(sample_context)
        
        assert isinstance(needs, list)
        for need in needs:
            assert isinstance(need, PredictedNeed)
    
    @pytest.mark.asyncio
    async def test_scan_opportunities(self, engine, sample_context):
        """Test opportunity scanning through main engine"""
        opportunities = await engine.scan_opportunities(sample_context)
        
        assert isinstance(opportunities, list)
        for opp in opportunities:
            assert isinstance(opp, Opportunity)
    
    @pytest.mark.asyncio
    async def test_plan_proactive_actions(self, engine):
        """Test action planning through main engine"""
        needs = [
            PredictedNeed(
                need_id="test_need",
                category=NeedCategory.IMMEDIATE,
                description="Test need",
                confidence=PredictionConfidence.HIGH,
                predicted_time=datetime.now(),
                urgency_score=0.8,
                context={},
                suggested_actions=[]
            )
        ]
        
        opportunities = [
            Opportunity(
                opportunity_id="test_opp",
                type=OpportunityType.PRODUCTIVITY,
                title="Test Opportunity",
                description="Test opportunity",
                confidence=PredictionConfidence.MEDIUM,
                potential_value=7.0,
                effort_required=3.0,
                time_window=(datetime.now(), datetime.now() + timedelta(days=1)),
                prerequisites=[],
                suggested_actions=[],
                context={}
            )
        ]
        
        actions = await engine.plan_proactive_actions(needs, opportunities)
        
        assert isinstance(actions, list)
        for action in actions:
            assert isinstance(action, ProactiveAction)
    
    @pytest.mark.asyncio
    async def test_proactive_monitoring_lifecycle(self, engine, sample_context):
        """Test proactive monitoring start/stop lifecycle"""
        assert not engine.is_active
        
        # Start monitoring in background
        monitoring_task = asyncio.create_task(
            engine.start_proactive_monitoring(sample_context)
        )
        
        # Wait a bit to ensure monitoring starts
        await asyncio.sleep(0.1)
        assert engine.is_active
        
        # Stop monitoring
        engine.stop_proactive_monitoring()
        
        # Wait for task to complete
        await asyncio.sleep(0.1)
        assert not engine.is_active
        
        # Cancel the task to clean up
        monitoring_task.cancel()
        try:
            await monitoring_task
        except asyncio.CancelledError:
            pass
    
    @pytest.mark.asyncio
    async def test_get_analytics(self, engine):
        """Test analytics retrieval through main engine"""
        analytics = await engine.get_analytics()
        
        assert isinstance(analytics, dict)
        assert "active_actions" in analytics
        assert "success_rate" in analytics
        assert "timestamp" in analytics


class TestIntegrationScenarios:
    """Test integration scenarios for proactive intelligence"""
    
    @pytest.fixture
    def engine(self):
        return ProactiveIntelligenceEngine()
    
    @pytest.mark.asyncio
    async def test_high_stress_scenario(self, engine):
        """Test proactive response to high stress scenario"""
        context = UserContext(
            user_id="stressed_user",
            current_activity="work",
            stress_level=0.95,
            productivity_score=0.2,
            calendar_events=[{
                "id": "deadline_meeting",
                "title": "Project Deadline Review",
                "start_time": (datetime.now() + timedelta(minutes=30)).isoformat()
            }]
        )
        
        result = await engine.orchestrator.orchestrate_proactive_intelligence(context)
        
        # Should predict stress relief needs
        stress_needs = [n for n in result["predicted_needs"] 
                       if "stress" in n.description.lower()]
        assert len(stress_needs) > 0
        
        # Should plan high-priority actions
        high_priority_actions = [a for a in result["planned_actions"] 
                               if a.priority >= 8]
        assert len(high_priority_actions) > 0
    
    @pytest.mark.asyncio
    async def test_productivity_optimization_scenario(self, engine):
        """Test proactive productivity optimization scenario"""
        context = UserContext(
            user_id="productivity_user",
            current_activity="work",
            productivity_score=0.3,
            recent_interactions=[
                {"task": "email_sorting", "timestamp": "2024-01-01T09:00:00"},
                {"task": "email_sorting", "timestamp": "2024-01-01T10:00:00"},
                {"task": "email_sorting", "timestamp": "2024-01-01T11:00:00"},
                {"task": "report_formatting", "timestamp": "2024-01-01T12:00:00"},
                {"task": "report_formatting", "timestamp": "2024-01-01T13:00:00"}
            ],
            goals=["improve efficiency", "automate workflows"]
        )
        
        result = await engine.orchestrator.orchestrate_proactive_intelligence(context)
        
        # Should identify automation opportunities
        automation_opps = [o for o in result["opportunities"] 
                          if "automation" in o.title.lower()]
        assert len(automation_opps) > 0
        
        # Should predict productivity needs
        productivity_needs = [n for n in result["predicted_needs"] 
                            if "productivity" in n.description.lower()]
        assert len(productivity_needs) > 0
    
    @pytest.mark.asyncio
    async def test_learning_opportunity_scenario(self, engine):
        """Test proactive learning opportunity identification"""
        context = UserContext(
            user_id="learner_user",
            current_activity="research",
            goals=[
                "learn artificial intelligence",
                "improve programming skills",
                "advance career in tech"
            ],
            productivity_score=0.8
        )
        
        result = await engine.orchestrator.orchestrate_proactive_intelligence(context)
        
        # Should identify learning opportunities
        learning_opps = [o for o in result["opportunities"] 
                        if o.type == OpportunityType.LEARNING]
        assert len(learning_opps) > 0
        
        # Should identify networking opportunities for career goals
        social_opps = [o for o in result["opportunities"] 
                      if o.type == OpportunityType.SOCIAL]
        assert len(social_opps) > 0


if __name__ == "__main__":
    pytest.main([__file__])