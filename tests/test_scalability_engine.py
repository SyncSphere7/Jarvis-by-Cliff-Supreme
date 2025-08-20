"""
Tests for Scalability Engine

This module contains comprehensive tests for the infinite scalability capabilities
including resource scaling, performance optimization, and scalability orchestration.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock

from core.supreme.engines.scalability_engine import (
    ResourceScaler,
    PerformanceOptimizer,
    CapabilityExpander,
    LoadBalancer,
    ResourceType,
    PerformanceMetric,
    ScalingDirection,
    ScalingStrategy,
    CapabilityType,
    ExpansionStrategy,
    LoadBalancingStrategy,
    ResourceMetrics,
    ScalingAction,
    PerformanceTarget,
    ScalabilityPlan,
    CapabilityRequirement,
    WorkloadNode
)

from core.supreme.engines.scalability_orchestrator import ScalabilityOrchestrator


class TestResourceScaler:
    """Test ResourceScaler functionality"""
    
    @pytest.fixture
    def resource_scaler(self):
        return ResourceScaler()
    
    @pytest.fixture
    def sample_metrics(self):
        return {
            ResourceType.CPU: ResourceMetrics(
                resource_type=ResourceType.CPU,
                current_usage=85.0,
                capacity=100.0,
                utilization_percentage=85.0,
                trend=5.0,
                timestamp=datetime.now()
            ),
            ResourceType.MEMORY: ResourceMetrics(
                resource_type=ResourceType.MEMORY,
                current_usage=25.0,
                capacity=100.0,
                utilization_percentage=25.0,
                trend=-2.0,
                timestamp=datetime.now()
            )
        }
    
    def test_resource_scaler_initialization(self, resource_scaler):
        """Test ResourceScaler initialization"""
        assert isinstance(resource_scaler.resource_metrics, dict)
        assert isinstance(resource_scaler.scaling_history, list)
        assert isinstance(resource_scaler.scaling_policies, dict)
        
        # Check that policies are initialized
        assert ResourceType.CPU in resource_scaler.scaling_policies
        assert ResourceType.MEMORY in resource_scaler.scaling_policies
        
        # Check policy structure
        cpu_policy = resource_scaler.scaling_policies[ResourceType.CPU]
        assert "scale_up_threshold" in cpu_policy
        assert "scale_down_threshold" in cpu_policy
        assert "scale_factor" in cpu_policy
    
    @pytest.mark.asyncio
    async def test_analyze_resource_needs_scale_up(self, resource_scaler, sample_metrics):
        """Test resource needs analysis for scale-up scenario"""
        actions = await resource_scaler.analyze_resource_needs(sample_metrics)
        
        assert isinstance(actions, list)
        assert len(actions) > 0
        
        # Should have scale-up action for CPU (85% > 80% threshold)
        cpu_actions = [a for a in actions if a.resource_type == ResourceType.CPU]
        assert len(cpu_actions) > 0
        assert cpu_actions[0].direction == ScalingDirection.UP
        assert cpu_actions[0].magnitude > 0
        assert cpu_actions[0].priority > 0
    
    @pytest.mark.asyncio
    async def test_analyze_resource_needs_scale_down(self, resource_scaler, sample_metrics):
        """Test resource needs analysis for scale-down scenario"""
        actions = await resource_scaler.analyze_resource_needs(sample_metrics)
        
        # Should have scale-down action for MEMORY (25% < 30% threshold)
        memory_actions = [a for a in actions if a.resource_type == ResourceType.MEMORY]
        assert len(memory_actions) > 0
        assert memory_actions[0].direction == ScalingDirection.DOWN
        assert memory_actions[0].magnitude > 0
    
    @pytest.mark.asyncio
    async def test_execute_scaling_action(self, resource_scaler):
        """Test scaling action execution"""
        action = ScalingAction(
            action_id="test_action",
            resource_type=ResourceType.CPU,
            direction=ScalingDirection.UP,
            magnitude=50.0,
            strategy=ScalingStrategy.REACTIVE,
            priority=8,
            estimated_duration=timedelta(minutes=2),
            expected_impact={"performance_improvement": 25.0},
            prerequisites=[],
            rollback_plan=["Scale down by 50.0"],
            cost_estimate=5.0,
            risk_level=0.2
        )
        
        result = await resource_scaler.execute_scaling_action(action)
        
        assert isinstance(result, dict)
        assert result["action_id"] == "test_action"
        assert result["status"] == "completed"
        assert result["resource_type"] == "cpu"
        assert result["direction"] == "up"
        assert result["magnitude"] == 50.0
        assert "timestamp" in result
        
        # Check that action was added to history
        assert len(resource_scaler.scaling_history) == 1
    
    def test_calculate_priority(self, resource_scaler):
        """Test priority calculation"""
        # Test critical priority
        critical_priority = resource_scaler._calculate_priority(150.0, 80.0)
        assert critical_priority == 10
        
        # Test high priority
        high_priority = resource_scaler._calculate_priority(100.0, 80.0)
        assert high_priority == 8
        
        # Test medium priority
        medium_priority = resource_scaler._calculate_priority(85.0, 80.0)
        assert medium_priority == 6
        
        # Test low priority
        low_priority = resource_scaler._calculate_priority(75.0, 80.0)
        assert low_priority == 4


class TestPerformanceOptimizer:
    """Test PerformanceOptimizer functionality"""
    
    @pytest.fixture
    def performance_optimizer(self):
        return PerformanceOptimizer()
    
    @pytest.fixture
    def sample_performance_metrics(self):
        return {
            PerformanceMetric.RESPONSE_TIME: 200.0,  # High (target: 100ms)
            PerformanceMetric.THROUGHPUT: 5000.0,    # Low (target: 10000 req/s)
            PerformanceMetric.CPU_UTILIZATION: 90.0, # High (target: 70%)
            PerformanceMetric.ERROR_RATE: 0.05,      # Good (target: 0.1%)
            PerformanceMetric.AVAILABILITY: 99.95    # Good (target: 99.9%)
        }
    
    def test_performance_optimizer_initialization(self, performance_optimizer):
        """Test PerformanceOptimizer initialization"""
        assert isinstance(performance_optimizer.performance_baselines, dict)
        assert isinstance(performance_optimizer.optimization_history, list)
        assert isinstance(performance_optimizer.performance_targets, dict)
    
    @pytest.mark.asyncio
    async def test_analyze_performance(self, performance_optimizer, sample_performance_metrics):
        """Test performance analysis"""
        targets = await performance_optimizer.analyze_performance(sample_performance_metrics)
        
        assert isinstance(targets, list)
        assert len(targets) > 0
        
        # Check that targets are properly structured
        for target in targets:
            assert isinstance(target, PerformanceTarget)
            assert isinstance(target.metric, PerformanceMetric)
            assert target.target_value > 0
            assert target.current_value > 0
            assert target.priority > 0
            assert isinstance(target.optimization_actions, list)
        
        # Should identify response time as needing optimization
        response_time_targets = [t for t in targets if t.metric == PerformanceMetric.RESPONSE_TIME]
        assert len(response_time_targets) > 0
        assert response_time_targets[0].current_value > response_time_targets[0].target_value
    
    def test_needs_optimization(self, performance_optimizer):
        """Test optimization need detection"""
        # Response time - lower is better
        assert performance_optimizer._needs_optimization(
            PerformanceMetric.RESPONSE_TIME, 200.0, 100.0
        )
        assert not performance_optimizer._needs_optimization(
            PerformanceMetric.RESPONSE_TIME, 80.0, 100.0
        )
        
        # Throughput - higher is better
        assert performance_optimizer._needs_optimization(
            PerformanceMetric.THROUGHPUT, 5000.0, 10000.0
        )
        assert not performance_optimizer._needs_optimization(
            PerformanceMetric.THROUGHPUT, 12000.0, 10000.0
        )
    
    @pytest.mark.asyncio
    async def test_optimize_performance(self, performance_optimizer):
        """Test performance optimization execution"""
        targets = [
            PerformanceTarget(
                metric=PerformanceMetric.RESPONSE_TIME,
                target_value=100.0,
                current_value=200.0,
                tolerance=0.2,
                priority=8,
                optimization_actions=["Optimize database queries", "Implement caching"]
            )
        ]
        
        result = await performance_optimizer.optimize_performance(targets)
        
        assert isinstance(result, dict)
        assert "total_targets" in result
        assert "optimization_results" in result
        assert "successful_optimizations" in result
        assert result["total_targets"] == 1
        assert result["successful_optimizations"] > 0
    
    @pytest.mark.asyncio
    async def test_get_performance_analytics(self, performance_optimizer):
        """Test performance analytics generation"""
        # Add some optimization history
        performance_optimizer.optimization_history = [
            {"status": "completed", "improvement": 15.0},
            {"status": "completed", "improvement": 20.0},
            {"status": "failed", "improvement": 0.0}
        ]
        
        analytics = await performance_optimizer.get_performance_analytics()
        
        assert isinstance(analytics, dict)
        assert "total_optimizations" in analytics
        assert "success_rate" in analytics
        assert "average_improvement" in analytics
        assert analytics["total_optimizations"] == 3
        assert analytics["success_rate"] > 0
        assert analytics["average_improvement"] > 0


class TestScalabilityOrchestrator:
    """Test ScalabilityOrchestrator functionality"""
    
    @pytest.fixture
    def orchestrator(self):
        return ScalabilityOrchestrator()
    
    @pytest.fixture
    def sample_resource_metrics(self):
        return {
            ResourceType.CPU: ResourceMetrics(
                resource_type=ResourceType.CPU,
                current_usage=85.0,
                capacity=100.0,
                utilization_percentage=85.0,
                trend=5.0,
                timestamp=datetime.now()
            )
        }
    
    @pytest.fixture
    def sample_performance_metrics(self):
        return {
            PerformanceMetric.RESPONSE_TIME: 200.0,
            PerformanceMetric.THROUGHPUT: 5000.0
        }
    
    def test_orchestrator_initialization(self, orchestrator):
        """Test ScalabilityOrchestrator initialization"""
        assert isinstance(orchestrator.resource_scaler, ResourceScaler)
        assert isinstance(orchestrator.performance_optimizer, PerformanceOptimizer)
        assert isinstance(orchestrator.scalability_plans, dict)
        assert isinstance(orchestrator.orchestration_history, list)
        assert not orchestrator.monitoring_active
    
    @pytest.mark.asyncio
    async def test_orchestrate_scalability(self, orchestrator, sample_resource_metrics, sample_performance_metrics):
        """Test scalability orchestration"""
        plan = await orchestrator.orchestrate_scalability(
            sample_resource_metrics, sample_performance_metrics
        )
        
        assert isinstance(plan, ScalabilityPlan)
        assert plan.plan_id
        assert isinstance(plan.scaling_actions, list)
        assert isinstance(plan.performance_targets, list)
        assert isinstance(plan.resource_requirements, dict)
        assert isinstance(plan.timeline, dict)
        assert isinstance(plan.success_criteria, list)
        assert isinstance(plan.monitoring_metrics, list)
        assert isinstance(plan.rollback_strategy, list)
        assert isinstance(plan.estimated_cost, float)
        assert isinstance(plan.expected_benefits, dict)
        
        # Plan should be stored
        assert plan.plan_id in orchestrator.scalability_plans
    
    @pytest.mark.asyncio
    async def test_execute_scalability_plan(self, orchestrator, sample_resource_metrics, sample_performance_metrics):
        """Test scalability plan execution"""
        plan = await orchestrator.orchestrate_scalability(
            sample_resource_metrics, sample_performance_metrics
        )
        
        result = await orchestrator.execute_scalability_plan(plan)
        
        assert isinstance(result, dict)
        assert "plan_id" in result
        assert "scaling_results" in result
        assert "optimization_results" in result
        assert "overall_status" in result
        assert "start_time" in result
        assert "end_time" in result
        
        assert result["plan_id"] == plan.plan_id
        assert result["overall_status"] in ["completed", "partial_success", "failed"]
        
        # Execution should be added to history
        assert len(orchestrator.orchestration_history) == 1
    
    @pytest.mark.asyncio
    async def test_get_scalability_analytics(self, orchestrator):
        """Test scalability analytics generation"""
        # Add some test data
        orchestrator.orchestration_history = [
            {"overall_status": "completed"},
            {"overall_status": "completed"},
            {"overall_status": "failed"}
        ]
        
        orchestrator.scalability_plans = {
            "plan1": ScalabilityPlan(
                plan_id="plan1",
                scaling_actions=[],
                performance_targets=[],
                resource_requirements={},
                timeline={},
                success_criteria=[],
                monitoring_metrics=[],
                rollback_strategy=[],
                estimated_cost=100.0,
                expected_benefits={"performance_improvement": 25.0}
            )
        }
        
        analytics = await orchestrator.get_scalability_analytics()
        
        assert isinstance(analytics, dict)
        assert "total_plans" in analytics
        assert "execution_history" in analytics
        assert "success_rate" in analytics
        assert "average_cost" in analytics
        assert "average_benefits" in analytics
        
        assert analytics["total_plans"] == 1
        assert analytics["execution_history"] == 3
        assert analytics["success_rate"] > 0
        assert analytics["average_cost"] == 100.0


class TestCapabilityExpander:
    """Test CapabilityExpander functionality"""
    
    @pytest.fixture
    def capability_expander(self):
        return CapabilityExpander()
    
    @pytest.fixture
    def sample_capability_requirements(self):
        return [
            CapabilityRequirement(
                capability_type=CapabilityType.PROCESSING,
                required_capacity=1000.0,
                current_capacity=500.0,
                expansion_urgency=8,
                dependencies=["storage", "networking"],
                constraints={"max_cost": 1000.0},
                success_metrics=["throughput_increase", "response_time_improvement"]
            ),
            CapabilityRequirement(
                capability_type=CapabilityType.STORAGE,
                required_capacity=2000.0,
                current_capacity=1800.0,
                expansion_urgency=5,
                dependencies=[],
                constraints={},
                success_metrics=["capacity_increase"]
            )
        ]
    
    def test_capability_expander_initialization(self, capability_expander):
        """Test CapabilityExpander initialization"""
        assert isinstance(capability_expander.capability_inventory, dict)
        assert isinstance(capability_expander.expansion_history, list)
        assert isinstance(capability_expander.expansion_policies, dict)
        
        # Check that policies are initialized for different capability types
        assert CapabilityType.PROCESSING in capability_expander.expansion_policies
        assert CapabilityType.STORAGE in capability_expander.expansion_policies
        assert CapabilityType.NETWORKING in capability_expander.expansion_policies
    
    @pytest.mark.asyncio
    async def test_analyze_capability_needs(self, capability_expander, sample_capability_requirements):
        """Test capability needs analysis"""
        expansion_plans = await capability_expander.analyze_capability_needs(sample_capability_requirements)
        
        assert isinstance(expansion_plans, list)
        assert len(expansion_plans) > 0
        
        # Should create expansion plan for processing (high urgency and capacity gap)
        processing_plans = [p for p in expansion_plans if p.capability_type == CapabilityType.PROCESSING]
        assert len(processing_plans) > 0
        
        plan = processing_plans[0]
        assert plan.capacity_increase > 0
        assert isinstance(plan.strategy, ExpansionStrategy)
        assert isinstance(plan.implementation_steps, list)
        assert len(plan.implementation_steps) > 0
        assert plan.cost_estimate > 0
        assert isinstance(plan.risk_assessment, dict)
    
    def test_needs_expansion(self, capability_expander):
        """Test expansion need detection"""
        # High utilization requirement
        high_util_req = CapabilityRequirement(
            capability_type=CapabilityType.PROCESSING,
            required_capacity=900.0,
            current_capacity=1000.0,
            expansion_urgency=5,
            dependencies=[],
            constraints={},
            success_metrics=[]
        )
        assert capability_expander._needs_expansion(high_util_req)
        
        # High urgency requirement
        high_urgency_req = CapabilityRequirement(
            capability_type=CapabilityType.PROCESSING,
            required_capacity=500.0,
            current_capacity=1000.0,
            expansion_urgency=9,
            dependencies=[],
            constraints={},
            success_metrics=[]
        )
        assert capability_expander._needs_expansion(high_urgency_req)
        
        # Low utilization and urgency
        low_req = CapabilityRequirement(
            capability_type=CapabilityType.PROCESSING,
            required_capacity=500.0,
            current_capacity=1000.0,
            expansion_urgency=3,
            dependencies=[],
            constraints={},
            success_metrics=[]
        )
        assert not capability_expander._needs_expansion(low_req)
    
    @pytest.mark.asyncio
    async def test_execute_expansion_plan(self, capability_expander, sample_capability_requirements):
        """Test expansion plan execution"""
        expansion_plans = await capability_expander.analyze_capability_needs(sample_capability_requirements)
        assert len(expansion_plans) > 0
        
        plan = expansion_plans[0]
        result = await capability_expander.execute_expansion_plan(plan)
        
        assert isinstance(result, dict)
        assert "expansion_id" in result
        assert "capability_type" in result
        assert "strategy" in result
        assert "status" in result
        assert "completed_steps" in result
        assert "start_time" in result
        assert "end_time" in result
        
        assert result["expansion_id"] == plan.expansion_id
        assert result["status"] == "completed"
        assert len(result["completed_steps"]) == len(plan.implementation_steps)
        
        # Should be added to history
        assert len(capability_expander.expansion_history) == 1


class TestLoadBalancer:
    """Test LoadBalancer functionality"""
    
    @pytest.fixture
    def load_balancer(self):
        return LoadBalancer()
    
    @pytest.fixture
    def sample_nodes(self):
        return [
            WorkloadNode(
                node_id="node1",
                capacity=1000.0,
                current_load=200.0,
                response_time=50.0,
                health_status="healthy",
                location="us-east-1",
                capabilities=["processing", "storage"]
            ),
            WorkloadNode(
                node_id="node2",
                capacity=800.0,
                current_load=600.0,
                response_time=80.0,
                health_status="healthy",
                location="us-west-1",
                capabilities=["processing"]
            ),
            WorkloadNode(
                node_id="node3",
                capacity=1200.0,
                current_load=100.0,
                response_time=30.0,
                health_status="healthy",
                location="eu-west-1",
                capabilities=["processing", "analytics"]
            )
        ]
    
    def test_load_balancer_initialization(self, load_balancer):
        """Test LoadBalancer initialization"""
        assert isinstance(load_balancer.nodes, dict)
        assert isinstance(load_balancer.distribution_history, list)
        assert isinstance(load_balancer.balancing_policies, dict)
        
        # Check that policies are initialized for different strategies
        assert LoadBalancingStrategy.ROUND_ROBIN in load_balancer.balancing_policies
        assert LoadBalancingStrategy.WEIGHTED in load_balancer.balancing_policies
        assert LoadBalancingStrategy.LEAST_CONNECTIONS in load_balancer.balancing_policies
    
    @pytest.mark.asyncio
    async def test_analyze_workload_distribution_weighted(self, load_balancer, sample_nodes):
        """Test workload distribution analysis with weighted strategy"""
        total_workload = 1000.0
        
        distribution = await load_balancer.analyze_workload_distribution(
            sample_nodes, total_workload, LoadBalancingStrategy.WEIGHTED
        )
        
        assert distribution.distribution_id
        assert distribution.strategy == LoadBalancingStrategy.WEIGHTED
        assert isinstance(distribution.node_assignments, dict)
        assert isinstance(distribution.expected_performance, dict)
        assert isinstance(distribution.load_balancing_rules, list)
        assert isinstance(distribution.monitoring_metrics, list)
        
        # Check that all nodes have assignments
        assert len(distribution.node_assignments) == len(sample_nodes)
        
        # Check that total assigned workload equals requested workload
        total_assigned = sum(distribution.node_assignments.values())
        assert abs(total_assigned - total_workload) < 1.0  # Allow small floating point differences
        
        # Node with best performance (node3) should get more load
        assert distribution.node_assignments["node3"] > distribution.node_assignments["node2"]
    
    @pytest.mark.asyncio
    async def test_analyze_workload_distribution_round_robin(self, load_balancer, sample_nodes):
        """Test workload distribution analysis with round-robin strategy"""
        total_workload = 1200.0
        
        distribution = await load_balancer.analyze_workload_distribution(
            sample_nodes, total_workload, LoadBalancingStrategy.ROUND_ROBIN
        )
        
        assert distribution.strategy == LoadBalancingStrategy.ROUND_ROBIN
        
        # Round-robin should distribute equally
        expected_per_node = total_workload / len(sample_nodes)
        for node_id, assigned_load in distribution.node_assignments.items():
            assert abs(assigned_load - expected_per_node) < 1.0
    
    @pytest.mark.asyncio
    async def test_analyze_workload_distribution_least_connections(self, load_balancer, sample_nodes):
        """Test workload distribution analysis with least connections strategy"""
        total_workload = 800.0
        
        distribution = await load_balancer.analyze_workload_distribution(
            sample_nodes, total_workload, LoadBalancingStrategy.LEAST_CONNECTIONS
        )
        
        assert distribution.strategy == LoadBalancingStrategy.LEAST_CONNECTIONS
        
        # Node with least current load (node3) should get load first
        assert distribution.node_assignments["node3"] > 0
        
        # Node with highest current load (node2) should get less or no additional load
        assert distribution.node_assignments["node2"] <= distribution.node_assignments["node3"]
    
    @pytest.mark.asyncio
    async def test_execute_load_balancing(self, load_balancer, sample_nodes):
        """Test load balancing execution"""
        total_workload = 600.0
        
        distribution = await load_balancer.analyze_workload_distribution(
            sample_nodes, total_workload, LoadBalancingStrategy.WEIGHTED
        )
        
        result = await load_balancer.execute_load_balancing(distribution, sample_nodes)
        
        assert isinstance(result, dict)
        assert "distribution_id" in result
        assert "strategy" in result
        assert "status" in result
        assert "node_results" in result
        assert "start_time" in result
        assert "end_time" in result
        assert "total_nodes_balanced" in result
        
        assert result["distribution_id"] == distribution.distribution_id
        assert result["status"] == "completed"
        assert len(result["node_results"]) == len(sample_nodes)
        
        # Check node results structure
        for node_result in result["node_results"]:
            assert "node_id" in node_result
            assert "assigned_load" in node_result
            assert "previous_load" in node_result
            assert "new_total_load" in node_result
            assert "utilization" in node_result
            assert "status" in node_result
            assert node_result["status"] == "completed"
        
        # Should be added to history
        assert len(load_balancer.distribution_history) == 1
    
    @pytest.mark.asyncio
    async def test_get_load_balancing_analytics(self, load_balancer):
        """Test load balancing analytics generation"""
        # Add some test data
        load_balancer.distribution_history = [
            {"status": "completed", "total_nodes_balanced": 3, "strategy": "weighted"},
            {"status": "completed", "total_nodes_balanced": 2, "strategy": "round_robin"},
            {"status": "failed", "total_nodes_balanced": 0, "strategy": "weighted"}
        ]
        
        analytics = await load_balancer.get_load_balancing_analytics()
        
        assert isinstance(analytics, dict)
        assert "total_distributions" in analytics
        assert "success_rate" in analytics
        assert "average_nodes_per_distribution" in analytics
        assert "most_used_strategy" in analytics
        
        assert analytics["total_distributions"] == 3
        assert analytics["success_rate"] > 0
        assert analytics["average_nodes_per_distribution"] > 0
        assert analytics["most_used_strategy"] == "weighted"


if __name__ == "__main__":
    pytest.main([__file__])