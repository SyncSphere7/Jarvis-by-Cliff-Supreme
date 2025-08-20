"""
Test Advanced Reasoning Engine
Comprehensive tests for supreme reasoning capabilities.
"""

import pytest
import asyncio
from unittest.mock import Mock

from core.supreme.engines.reasoning_engine import SupremeReasoningEngine
from core.supreme.engines.logical_processor import LogicalProcessor
from core.supreme.engines.problem_solver import ProblemSolver
from core.supreme.engines.strategic_planner import StrategicPlanner
from core.supreme.engines.optimization_engine import OptimizationEngine
from core.supreme.base_supreme_engine import SupremeRequest
from core.supreme.supreme_config import EngineConfig, CapabilityLevel

class TestLogicalProcessor:
    """Test logical processing capabilities"""
    
    def test_logical_structure_analysis(self):
        """Test logical structure analysis"""
        processor = LogicalProcessor()
        
        text = "If it rains, then the ground gets wet. It is raining. Therefore, the ground is wet."
        structure = processor.analyze_logical_structure(text)
        
        assert "premises" in structure
        assert "conclusions" in structure
        assert "logical_connectors" in structure
        assert "if" in structure["logical_connectors"]
        assert "then" in structure["logical_connectors"]
    
    def test_deductive_reasoning(self):
        """Test deductive reasoning"""
        processor = LogicalProcessor()
        
        premises = [
            "All humans are mortal",
            "Socrates is human"
        ]
        
        chain = processor.perform_deductive_reasoning(premises)
        
        assert chain.problem == "Deductive reasoning from premises"
        assert len(chain.steps) >= 0
        assert chain.final_conclusion is not None
        assert 0 <= chain.overall_confidence <= 1
    
    def test_inductive_reasoning(self):
        """Test inductive reasoning"""
        processor = LogicalProcessor()
        
        observations = [
            "The sun rose in the east today",
            "The sun rose in the east yesterday", 
            "The sun rose in the east last week"
        ]
        
        chain = processor.perform_inductive_reasoning(observations)
        
        assert chain.problem == "Inductive reasoning from observations"
        assert chain.final_conclusion is not None
        assert 0 <= chain.overall_confidence <= 1

class TestProblemSolver:
    """Test problem solving capabilities"""
    
    def test_complex_problem_solving(self):
        """Test complex problem solving"""
        solver = ProblemSolver()
        
        problem = "Our company needs to increase revenue by 30% while reducing costs by 15%"
        solution = solver.solve_complex_problem(problem)
        
        assert solution.problem == problem
        assert solution.problem_type is not None
        assert len(solution.components) > 0
        assert len(solution.solutions) > 0
        assert len(solution.implementation_plan) > 0
        assert 0 <= solution.overall_confidence <= 1
    
    def test_problem_classification(self):
        """Test problem type classification"""
        solver = ProblemSolver()
        
        # Test optimization problem
        opt_problem = "How can we optimize our supply chain efficiency?"
        opt_solution = solver.solve_complex_problem(opt_problem)
        assert opt_solution.problem_type.value == "optimization"
        
        # Test strategic problem
        strategic_problem = "What strategy should we use for market expansion?"
        strategic_solution = solver.solve_complex_problem(strategic_problem)
        assert strategic_solution.problem_type.value == "strategic"
        
        # Test troubleshooting problem
        trouble_problem = "Our system is experiencing frequent crashes"
        trouble_solution = solver.solve_complex_problem(trouble_problem)
        assert trouble_solution.problem_type.value == "troubleshooting"

class TestStrategicPlanner:
    """Test strategic planning capabilities"""
    
    def test_strategic_plan_creation(self):
        """Test strategic plan creation"""
        planner = StrategicPlanner()
        
        objective = "Expand into new international markets"
        plan = planner.create_strategic_plan(objective)
        
        assert plan.title is not None
        assert objective in plan.title
        assert plan.strategy_type is not None
        assert len(plan.goals) > 0
        assert len(plan.action_items) > 0
        assert len(plan.success_metrics) > 0
        assert 0 <= plan.overall_confidence <= 1
    
    def test_strategy_type_classification(self):
        """Test strategy type classification"""
        planner = StrategicPlanner()
        
        # Test business strategy
        business_obj = "Increase market share and profitability"
        business_plan = planner.create_strategic_plan(business_obj)
        assert business_plan.strategy_type.value == "business"
        
        # Test technology strategy
        tech_obj = "Implement digital transformation initiative"
        tech_plan = planner.create_strategic_plan(tech_obj)
        assert tech_plan.strategy_type.value == "technology"
        
        # Test growth strategy
        growth_obj = "Scale operations to new regions"
        growth_plan = planner.create_strategic_plan(growth_obj)
        assert growth_plan.strategy_type.value == "growth"

class TestOptimizationEngine:
    """Test optimization capabilities"""
    
    def test_basic_optimization(self):
        """Test basic optimization"""
        from core.supreme.engines.optimization_engine import OptimizationVariable, OptimizationType, OptimizationMethod
        
        engine = OptimizationEngine()
        
        variables = [
            OptimizationVariable("x", 0, 10, 5),
            OptimizationVariable("y", 0, 10, 5)
        ]
        
        result = engine.optimize(
            objective_function="maximize x + y",
            variables=variables,
            optimization_type=OptimizationType.MAXIMIZE,
            method=OptimizationMethod.GREEDY,
            max_iterations=50
        )
        
        assert result.success == True
        assert "x" in result.optimal_values
        assert "y" in result.optimal_values
        assert result.iterations > 0
        assert result.execution_time >= 0
    
    def test_resource_allocation_optimization(self):
        """Test resource allocation optimization"""
        engine = OptimizationEngine()
        
        resources = {"budget": 1000, "time": 100, "personnel": 10}
        demands = {"project_a": 400, "project_b": 300, "project_c": 500}
        priorities = {"project_a": 0.5, "project_b": 0.3, "project_c": 0.2}
        
        result = engine.optimize_resource_allocation(resources, demands, priorities)
        
        assert "allocation" in result
        assert "utilization" in result
        assert "satisfaction" in result
        assert "efficiency" in result
        assert 0 <= result["utilization"] <= 1
        assert 0 <= result["satisfaction"] <= 1

class TestSupremeReasoningEngine:
    """Test supreme reasoning engine integration"""
    
    @pytest.fixture
    async def reasoning_engine(self):
        """Create test reasoning engine"""
        config = EngineConfig()
        config.capability_level = CapabilityLevel.SUPREME
        
        engine = SupremeReasoningEngine("reasoning", config)
        await engine.initialize()
        yield engine
        await engine.shutdown()
    
    @pytest.mark.asyncio
    async def test_reasoning_engine_initialization(self, reasoning_engine):
        """Test reasoning engine initialization"""
        assert reasoning_engine.engine_name == "reasoning"
        assert reasoning_engine.logical_processor is not None
        assert reasoning_engine.problem_solver is not None
        assert reasoning_engine.strategic_planner is not None
        assert reasoning_engine.optimization_engine is not None
    
    @pytest.mark.asyncio
    async def test_logical_analysis_operation(self, reasoning_engine):
        """Test logical analysis operation"""
        request = SupremeRequest(
            request_id="test-logical",
            operation="logical_analysis",
            parameters={
                "text": "If A then B. A is true. Therefore B is true."
            }
        )
        
        response = await reasoning_engine.execute(request)
        
        assert response.success == True
        assert response.result is not None
        assert response.result["analysis_type"] == "logical_analysis"
        assert "logical_structure" in response.result
    
    @pytest.mark.asyncio
    async def test_problem_solving_operation(self, reasoning_engine):
        """Test problem solving operation"""
        request = SupremeRequest(
            request_id="test-problem",
            operation="problem_solving",
            parameters={
                "problem": "How to improve customer satisfaction while reducing costs?"
            }
        )
        
        response = await reasoning_engine.execute(request)
        
        assert response.success == True
        assert response.result is not None
        assert response.result["analysis_type"] == "problem_solving"
        assert "solution_summary" in response.result
        assert response.result["reasoning_quality"] == "supreme"
    
    @pytest.mark.asyncio
    async def test_strategic_planning_operation(self, reasoning_engine):
        """Test strategic planning operation"""
        request = SupremeRequest(
            request_id="test-strategy",
            operation="strategic_planning",
            parameters={
                "objective": "Launch new product line successfully"
            }
        )
        
        response = await reasoning_engine.execute(request)
        
        assert response.success == True
        assert response.result is not None
        assert response.result["analysis_type"] == "strategic_planning"
        assert "primary_goal" in response.result
        assert response.result["reasoning_quality"] == "supreme"
    
    @pytest.mark.asyncio
    async def test_optimization_operation(self, reasoning_engine):
        """Test optimization operation"""
        request = SupremeRequest(
            request_id="test-optimization",
            operation="optimization",
            parameters={
                "objective": "maximize efficiency",
                "variables": {
                    "x": {"min": 0, "max": 100, "current": 50},
                    "y": {"min": 0, "max": 100, "current": 50}
                }
            }
        )
        
        response = await reasoning_engine.execute(request)
        
        assert response.success == True
        assert response.result is not None
        assert response.result["analysis_type"] == "optimization"
        assert "optimal_values" in response.result
        assert response.result["reasoning_quality"] == "supreme"
    
    @pytest.mark.asyncio
    async def test_comprehensive_analysis_operation(self, reasoning_engine):
        """Test comprehensive analysis operation"""
        request = SupremeRequest(
            request_id="test-comprehensive",
            operation="analyze",
            parameters={
                "intent_text": "We need to solve the problem of declining sales by developing a strategic plan to optimize our marketing approach"
            }
        )
        
        response = await reasoning_engine.execute(request)
        
        assert response.success == True
        assert response.result is not None
        assert response.result["analysis_type"] == "comprehensive_analysis"
        assert "analyses_performed" in response.result
        assert "key_insights" in response.result
        assert response.result["reasoning_quality"] == "supreme"
        assert response.result["total_analyses"] > 0
    
    @pytest.mark.asyncio
    async def test_supported_operations(self, reasoning_engine):
        """Test supported operations"""
        operations = await reasoning_engine.get_supported_operations()
        
        assert len(operations) > 10
        assert "analyze" in operations
        assert "logical_analysis" in operations
        assert "problem_solving" in operations
        assert "strategic_planning" in operations
        assert "optimization" in operations

@pytest.mark.asyncio
async def test_end_to_end_reasoning():
    """Test complete end-to-end reasoning workflow"""
    # Create reasoning engine
    config = EngineConfig()
    config.capability_level = CapabilityLevel.GODLIKE
    
    engine = SupremeReasoningEngine("supreme_reasoning", config)
    await engine.initialize()
    
    try:
        # Test complex reasoning scenario
        request = SupremeRequest(
            request_id="end-to-end-test",
            operation="analyze",
            parameters={
                "intent_text": "Our startup needs to decide between three growth strategies: expanding to new markets, developing new products, or optimizing current operations. We have limited resources and need to maximize ROI while minimizing risk."
            }
        )
        
        response = await engine.execute(request)
        
        # Verify comprehensive analysis
        assert response.success == True
        assert response.confidence > 0.5
        assert response.result["analysis_type"] == "comprehensive_analysis"
        assert response.result["reasoning_quality"] == "supreme"
        assert len(response.result["analyses_performed"]) >= 2  # Should perform multiple analyses
        
        # Verify detailed analyses
        detailed = response.result["detailed_analyses"]
        assert len(detailed) > 0
        
        # Should include strategic planning for growth strategies
        if "strategic" in detailed:
            strategic_result = detailed["strategic"]
            assert "primary_goal" in strategic_result
            assert strategic_result["strategy_type"] == "growth"
        
        # Should include problem solving for decision making
        if "problem_solving" in detailed:
            problem_result = detailed["problem_solving"]
            assert "solution_summary" in problem_result
            assert problem_result["problem_type"] in ["decision_making", "strategic"]
        
        print("🎉 End-to-end reasoning test passed!")
        print(f"   Analyses performed: {response.result['analyses_performed']}")
        print(f"   Key insights: {len(response.result['key_insights'])}")
        print(f"   Confidence: {response.confidence:.2%}")
        
    finally:
        await engine.shutdown()

if __name__ == "__main__":
    # Run the end-to-end test
    asyncio.run(test_end_to_end_reasoning())
    print("✅ Advanced Reasoning Engine tests completed!")