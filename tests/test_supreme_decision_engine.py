"""
Tests for Supreme Decision Engine
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock

from core.supreme.supreme_decision_engine import (
    DecisionMaker,
    SupremeExecutor,
    DecisionContext,
    DecisionType,
    DecisionComplexity,
    DecisionUrgency,
    DecisionOption,
    SupremeDecision
)

from core.supreme.supreme_control_interface import SupremeControlInterface
from core.supreme.supreme_orchestrator import EngineType


class TestDecisionMaker:
    """Test DecisionMaker functionality"""
    
    @pytest.fixture
    def mock_interface(self):
        interface = Mock(spec=SupremeControlInterface)
        interface.execute_command = AsyncMock()
        interface.execute_command.return_value = Mock(result={"status": "success"})
        return interface
    
    @pytest.fixture
    def decision_maker(self, mock_interface):
        return DecisionMaker(mock_interface)
    
    @pytest.fixture
    def sample_context(self):
        return DecisionContext(
            context_id="test_context",
            situation="Need to optimize system performance",
            objectives=["Improve response time", "Reduce resource usage"],
            constraints=["Budget under $1000", "Complete within 1 week"],
            available_resources={"budget": 800, "team_size": 3},
            time_constraints=timedelta(days=7),
            stakeholders=["development_team", "operations_team"],
            risk_tolerance=0.5,
            success_criteria=["Response time under 100ms", "Resource usage reduced by 20%"]
        )
    
    def test_decision_maker_initialization(self, decision_maker, mock_interface):
        """Test DecisionMaker initialization"""
        assert decision_maker.control_interface == mock_interface
        assert isinstance(decision_maker.decision_history, list)
        assert isinstance(decision_maker.execution_history, list)
        assert decision_maker.confidence_threshold == 0.7
        assert decision_maker.risk_threshold == 0.8
    
    @pytest.mark.asyncio
    async def test_generate_decision_options(self, decision_maker, sample_context):
        """Test decision option generation"""
        options = await decision_maker._generate_decision_options(sample_context)
        
        assert isinstance(options, list)
        assert len(options) >= 3  # Should generate at least conservative, aggressive, balanced
        
        for option in options:
            assert isinstance(option, DecisionOption)
            assert option.option_id
            assert option.description
            assert isinstance(option.required_actions, list)
            assert isinstance(option.required_engines, list)
            assert option.estimated_cost > 0
            assert isinstance(option.estimated_time, timedelta)
            assert 0 <= option.success_probability <= 1
            assert 0 <= option.risk_level <= 1
    
    @pytest.mark.asyncio
    async def test_evaluate_options(self, decision_maker, sample_context):
        """Test option evaluation"""
        options = await decision_maker._generate_decision_options(sample_context)
        evaluation_results = await decision_maker._evaluate_options(options, sample_context)
        
        assert isinstance(evaluation_results, dict)
        
        for option in options:
            assert option.option_id in evaluation_results
            option_eval = evaluation_results[option.option_id]
            assert isinstance(option_eval, dict)
    
    def test_select_best_option(self, decision_maker, sample_context):
        """Test option selection"""
        # Create mock options
        options = [
            DecisionOption(
                option_id="option1",
                description="Conservative approach",
                required_actions=["analyze", "implement"],
                required_engines=[EngineType.ANALYTICS],
                estimated_cost=100.0,
                estimated_time=timedelta(hours=4),
                success_probability=0.8,
                risk_level=0.2,
                expected_benefits={"stability": 200.0},
                side_effects=[]
            ),
            DecisionOption(
                option_id="option2",
                description="Aggressive approach",
                required_actions=["rapid_deploy"],
                required_engines=[EngineType.SYSTEM_CONTROL],
                estimated_cost=500.0,
                estimated_time=timedelta(hours=2),
                success_probability=0.6,
                risk_level=0.7,
                expected_benefits={"speed": 400.0},
                side_effects=["risk"]
            )
        ]
        
        evaluation_results = {
            "option1": {"analytics": {"score": 0.8}},
            "option2": {"analytics": {"score": 0.6}}
        }
        
        selected = decision_maker._select_best_option(options, evaluation_results, sample_context)
        
        assert selected in options
        assert isinstance(selected, DecisionOption)
    
    def test_calculate_option_score(self, decision_maker, sample_context):
        """Test option scoring"""
        option = DecisionOption(
            option_id="test_option",
            description="Test option",
            required_actions=["test"],
            required_engines=[EngineType.ANALYTICS],
            estimated_cost=100.0,
            estimated_time=timedelta(hours=2),
            success_probability=0.8,
            risk_level=0.3,
            expected_benefits={"value": 200.0},
            side_effects=[]
        )
        
        evaluation = {"analytics": {"score": 0.7}}
        
        score = decision_maker._calculate_option_score(option, evaluation, sample_context)
        
        assert isinstance(score, float)
        assert 0 <= score <= 1
    
    def test_generate_reasoning(self, decision_maker, sample_context):
        """Test reasoning generation"""
        option = DecisionOption(
            option_id="test_option",
            description="Test option",
            required_actions=["test"],
            required_engines=[EngineType.ANALYTICS],
            estimated_cost=100.0,
            estimated_time=timedelta(hours=2),
            success_probability=0.8,
            risk_level=0.3,
            expected_benefits={"value": 200.0},
            side_effects=[]
        )
        
        evaluation_results = {"test_option": {"analytics": {"score": 0.7}}}
        
        reasoning = decision_maker._generate_reasoning(option, evaluation_results, sample_context)
        
        assert isinstance(reasoning, list)
        assert len(reasoning) > 0
        assert all(isinstance(reason, str) for reason in reasoning)
    
    def test_calculate_confidence(self, decision_maker):
        """Test confidence calculation"""
        option = DecisionOption(
            option_id="test_option",
            description="Test option",
            required_actions=["test"],
            required_engines=[EngineType.ANALYTICS],
            estimated_cost=100.0,
            estimated_time=timedelta(hours=2),
            success_probability=0.8,
            risk_level=0.3,
            expected_benefits={"value": 200.0},
            side_effects=[]
        )
        
        evaluation_results = {"test_option": {"analytics": {"confidence": 0.7}}}
        
        confidence = decision_maker._calculate_confidence(option, evaluation_results)
        
        assert isinstance(confidence, float)
        assert 0 <= confidence <= 1


class TestSupremeExecutor:
    """Test SupremeExecutor functionality"""
    
    @pytest.fixture
    def mock_interface(self):
        interface = Mock(spec=SupremeControlInterface)
        interface.execute_command = AsyncMock()
        interface.execute_command.return_value = Mock(
            result={"status": "success"},
            status="completed",
            engines_used=["analytics"],
            execution_time=1.0
        )
        return interface
    
    @pytest.fixture
    def executor(self, mock_interface):
        return SupremeExecutor(mock_interface)
    
    @pytest.fixture
    def sample_decision(self):
        context = DecisionContext(
            context_id="test_context",
            situation="Test situation",
            objectives=["Test objective"],
            constraints=[],
            available_resources={},
            time_constraints=None,
            stakeholders=["user"],
            risk_tolerance=0.5,
            success_criteria=["Success"]
        )
        
        option = DecisionOption(
            option_id="test_option",
            description="Test option",
            required_actions=["test_action"],
            required_engines=[EngineType.ANALYTICS],
            estimated_cost=100.0,
            estimated_time=timedelta(hours=2),
            success_probability=0.8,
            risk_level=0.3,
            expected_benefits={"value": 200.0},
            side_effects=[]
        )
        
        return SupremeDecision(
            decision_id="test_decision",
            context=context,
            selected_option=option,
            reasoning=["Test reasoning"],
            confidence_score=0.8,
            risk_assessment={"overall_risk": 0.3},
            execution_plan=["Step 1: Initialize", "Step 2: Execute", "Step 3: Validate"],
            monitoring_plan=["Monitor progress"],
            rollback_plan=["Rollback if needed"],
            success_metrics=["Success metric"]
        )
    
    def test_executor_initialization(self, executor, mock_interface):
        """Test SupremeExecutor initialization"""
        assert executor.control_interface == mock_interface
        assert isinstance(executor.active_executions, dict)
        assert isinstance(executor.execution_history, list)
    
    @pytest.mark.asyncio
    async def test_execute_supreme_decision(self, executor, sample_decision):
        """Test supreme decision execution"""
        result = await executor.execute_supreme_decision(sample_decision)
        
        assert isinstance(result, dict)
        assert "execution_id" in result
        assert "decision_id" in result
        assert result["decision_id"] == sample_decision.decision_id
        assert "status" in result
        assert "execution_time" in result
        assert "completed_actions" in result
        assert "failed_actions" in result
    
    def test_determine_step_engines(self, executor):
        """Test step engine determination"""
        available_engines = [EngineType.ANALYTICS, EngineType.SYSTEM_CONTROL, EngineType.SECURITY]
        
        # Test analytics step
        analytics_engines = executor._determine_step_engines("analyze the data", available_engines)
        assert EngineType.ANALYTICS in analytics_engines
        
        # Test system control step
        system_engines = executor._determine_step_engines("execute the deployment", available_engines)
        assert EngineType.SYSTEM_CONTROL in system_engines
        
        # Test security step
        security_engines = executor._determine_step_engines("secure the system", available_engines)
        assert EngineType.SECURITY in security_engines
    
    def test_determine_command_type(self, executor):
        """Test command type determination"""
        from core.supreme.supreme_control_interface import CommandType
        
        # Test analyze command
        assert executor._determine_command_type("analyze the situation") == CommandType.ANALYZE
        
        # Test execute command
        assert executor._determine_command_type("execute the plan") == CommandType.EXECUTE
        
        # Test optimize command
        assert executor._determine_command_type("optimize performance") == CommandType.OPTIMIZE
        
        # Test secure command
        assert executor._determine_command_type("secure the data") == CommandType.SECURE
    
    def test_get_execution_status(self, executor):
        """Test execution status retrieval"""
        # Test with non-existent execution
        status = executor.get_execution_status("non_existent")
        assert status is None
        
        # Test with active execution
        executor.active_executions["test_id"] = {"status": "in_progress"}
        status = executor.get_execution_status("test_id")
        assert status == {"status": "in_progress"}
    
    def test_get_execution_history(self, executor):
        """Test execution history retrieval"""
        # Add some mock history
        executor.execution_history = [
            {"execution_id": "exec1", "status": "completed"},
            {"execution_id": "exec2", "status": "failed"},
            {"execution_id": "exec3", "status": "completed"}
        ]
        
        # Test with limit
        history = executor.get_execution_history(limit=2)
        assert len(history) == 2
        assert history == executor.execution_history[-2:]
        
        # Test without limit
        history = executor.get_execution_history(limit=0)
        assert len(history) == 3
        assert history == executor.execution_history


if __name__ == "__main__":
    pytest.main([__file__])