"""
Tests for Capability Expansion and Load Balancing

This module contains comprehensive tests for capability expansion, load balancing,
and infinite scaling algorithms.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock

from core.supreme.engines.capability_expansion import (
    CapabilityExpander,
    LoadBalancer,
    InfiniteScalingManager,
    CapabilityType,
    LoadBalancingStrategy,
    ExpansionTrigger,
    CapabilityNode,
    LoadBalancingRule,
    ExpansionPlan,
    LoadDistribution
)


class TestCapabilityExpander:
    """Test CapabilityExpander functionality"""
    
    @pytest.fixture
    def capability_expander(self):
        return CapabilityExpander()
    
    @pytest.fixture
    def sample_capability_metrics(self):
        return {
            CapabilityType.PROCESSING: {
                "load_percentage": 85.0,
                "response_time": 250.0,
                "error_rate": 0.5,
                "queue_length": 50,
                "total_capacity": 100.0,
                "node_count": 2
            },
            CapabilityType.STORAGE: {
                "load_percentage": 90.0,
                "response_time": 150.0,
                "error_rate": 0.2,
                "queue_length": 20,
                "total_capacity": 200.0,
                "node_count": 3
            }
        }
    
    def test_capability_expander_initialization(self, capability_expander):
        """Test CapabilityExpander initialization"""
        assert isinstance(capability_expander.capability_nodes, dict)
        assert isinstance(capability_expander.expansion_history, list)
        assert isinstance(capability_expander.expansion_policies, dict)
        
        # Check that policies are initialized
        assert CapabilityType.PROCESSING in capability_expander.expansion_policies
        assert CapabilityType.STORAGE in capability_expander.expansion_policies
        assert CapabilityType.AI_INFERENCE in capability_expander.expansion_policies
        
        # Check policy structure
        processing_policy = capability_expander.expansion_policies[CapabilityType.PROCESSING]
        assert "load_threshold" in processing_policy
        assert "expansion_factor" in processing_policy
        assert "min_nodes" in processing_policy
        assert "max_nodes" in processing_policy
    
    @pytest.mark.asyncio
    async def test_analyze_expansion_needs(self, capability_expander, sample_capability_metrics):
        """Test expansion needs analysis"""
        plans = await capability_expander.analyze_expansion_needs(sample_capability_metrics)
        
        assert isinstance(plans, list)
        assert len(plans) > 0
        
        # Check that plans are properly structured
        for plan in plans:
            assert isinstance(plan, ExpansionPlan)
            assert plan.plan_id
            assert isinstance(plan.capability_type, CapabilityType)
            assert isinstance(plan.trigger, ExpansionTrigger)
            assert plan.target_capacity > plan.current_capacity
            assert plan.expansion_nodes > 0
            assert plan.estimated_cost > 0
            assert isinstance(plan.success_criteria, list)
            assert isinstance(plan.rollback_plan, list)
        
        # Should identify processing expansion need (85% > 80% threshold)
        processing_plans = [p for p in plans if p.capability_type == CapabilityType.PROCESSING]
        assert len(processing_plans) > 0
        
        # Should identify storage expansion need (90% > 85% threshold)
        storage_plans = [p for p in plans if p.capability_type == CapabilityType.STORAGE]
        assert len(storage_plans) > 0
    
    @pytest.mark.asyncio
    async def test_execute_expansion_plan(self, capability_expander):
        """Test expansion plan execution"""
        plan = ExpansionPlan(
            plan_id="test_expansion",
            capability_type=CapabilityType.PROCESSING,
            trigger=ExpansionTrigger.LOAD_THRESHOLD,
            current_capacity=100.0,
            target_capacity=150.0,
            expansion_nodes=2,
            estimated_cost=200.0,
            implementation_time=timedelta(minutes=5),
            success_criteria=["Load reduced below 80%"],
            rollback_plan=["Remove new nodes if needed"]
        )
        
        result = await capability_expander.execute_expansion_plan(plan)
        
        assert isinstance(result, dict)
        assert result["plan_id"] == "test_expansion"
        assert result["status"] == "completed"
        assert result["capability_type"] == "processing"
        assert result["nodes_created"] == 2
        assert result["new_capacity"] == 150.0
        assert "execution_time" in result
        
        # Check that nodes were added to registry
        assert CapabilityType.PROCESSING in capability_expander.capability_nodes
        assert len(capability_expander.capability_nodes[CapabilityType.PROCESSING]) == 2
        
        # Check that execution was added to history
        assert len(capability_expander.expansion_history) == 1
    
    @pytest.mark.asyncio
    async def test_create_capability_node(self, capability_expander):
        """Test capability node creation"""
        node = await capability_expander._create_capability_node(CapabilityType.AI_INFERENCE, 0)
        
        assert isinstance(node, CapabilityNode)
        assert node.node_id
        assert node.capability_type == CapabilityType.AI_INFERENCE
        assert node.capacity > 0
        assert node.current_load == 0.0
        assert node.health_score == 1.0
        assert node.location
        assert "created_at" in node.metadata
        assert node.metadata["auto_created"] is True
    
    @pytest.mark.asyncio
    async def test_get_expansion_analytics(self, capability_expander):
        """Test expansion analytics generation"""
        # Add some test data
        capability_expander.expansion_history = [
            {"status": "completed", "cost": 100.0, "nodes_created": 2, "execution_time": 5.0},
            {"status": "completed", "cost": 150.0, "nodes_created": 3, "execution_time": 7.0},
            {"status": "failed", "cost": 0.0, "nodes_created": 0, "execution_time": 0.0}
        ]
        
        analytics = await capability_expander.get_expansion_analytics()
        
        assert isinstance(analytics, dict)
        assert "total_expansions" in analytics
        assert "successful_expansions" in analytics
        assert "success_rate" in analytics
        assert "total_cost" in analytics
        assert "total_nodes_created" in analytics
        assert "average_execution_time" in analytics
        
        assert analytics["total_expansions"] == 3
        assert analytics["successful_expansions"] == 2
        assert analytics["success_rate"] > 0
        assert analytics["total_cost"] == 250.0
        assert analytics["total_nodes_created"] == 5
        assert analytics["average_execution_time"] == 6.0


class TestLoadBalancer:
    """Test LoadBalancer functionality"""
    
    @pytest.fixture
    def load_balancer(self):
        return LoadBalancer()
    
    @pytest.fixture
    def sample_nodes(self):
        return [
            CapabilityNode(
                node_id="node_1",
                capability_type=CapabilityType.PROCESSING,
                capacity=100.0,
                current_load=30.0,
                response_time=80.0,
                error_rate=0.1,
                health_score=0.9,
                location="zone_a"
            ),
            CapabilityNode(
                node_id="node_2",
                capability_type=CapabilityType.PROCESSING,
                capacity=100.0,
                current_load=60.0,
                response_time=120.0,
                error_rate=0.2,
                health_score=0.8,
                location="zone_b"
            ),
            CapabilityNode(
                node_id="node_3",
                capability_type=CapabilityType.PROCESSING,
                capacity=100.0,
                current_load=20.0,
                response_time=60.0,
                error_rate=0.05,
                health_score=0.95,
                location="zone_c"
            )
        ]
    
    def test_load_balancer_initialization(self, load_balancer):
        """Test LoadBalancer initialization"""
        assert isinstance(load_balancer.load_balancing_rules, dict)
        assert isinstance(load_balancer.node_registry, dict)
        assert isinstance(load_balancer.distribution_history, list)
        
        # Check that rules are initialized
        assert CapabilityType.PROCESSING in load_balancer.load_balancing_rules
        assert CapabilityType.AI_INFERENCE in load_balancer.load_balancing_rules
        assert CapabilityType.STORAGE in load_balancer.load_balancing_rules
        
        # Check rule structure
        processing_rule = load_balancer.load_balancing_rules[CapabilityType.PROCESSING]
        assert isinstance(processing_rule, LoadBalancingRule)
        assert processing_rule.strategy == LoadBalancingStrategy.LEAST_RESPONSE_TIME
        assert isinstance(processing_rule.weight_factors, dict)
        assert isinstance(processing_rule.constraints, list)
    
    @pytest.mark.asyncio
    async def test_distribute_load_round_robin(self, load_balancer, sample_nodes):
        """Test round-robin load distribution"""
        # Override rule to use round-robin
        load_balancer.load_balancing_rules[CapabilityType.PROCESSING] = LoadBalancingRule(
            rule_id="test_rule",
            capability_type=CapabilityType.PROCESSING,
            strategy=LoadBalancingStrategy.ROUND_ROBIN,
            weight_factors={},
            constraints=[],
            priority=5
        )
        
        distribution = await load_balancer.distribute_load(
            CapabilityType.PROCESSING, 300.0, sample_nodes
        )
        
        assert isinstance(distribution, LoadDistribution)
        assert distribution.capability_type == CapabilityType.PROCESSING
        assert distribution.strategy_used == LoadBalancingStrategy.ROUND_ROBIN
        assert len(distribution.node_assignments) == 3
        
        # Should distribute equally (100 per node)
        for node_id, load in distribution.node_assignments.items():
            assert abs(load - 100.0) < 1.0  # Allow small floating point differences
    
    @pytest.mark.asyncio
    async def test_distribute_load_least_connections(self, load_balancer, sample_nodes):
        """Test least connections load distribution"""
        # Override rule to use least connections
        load_balancer.load_balancing_rules[CapabilityType.PROCESSING] = LoadBalancingRule(
            rule_id="test_rule",
            capability_type=CapabilityType.PROCESSING,
            strategy=LoadBalancingStrategy.LEAST_CONNECTIONS,
            weight_factors={},
            constraints=[],
            priority=5
        )
        
        distribution = await load_balancer.distribute_load(
            CapabilityType.PROCESSING, 300.0, sample_nodes
        )
        
        assert distribution.strategy_used == LoadBalancingStrategy.LEAST_CONNECTIONS
        assert len(distribution.node_assignments) == 3
        
        # Node with lowest current load (node_3: 20%) should get more load
        node_3_load = distribution.node_assignments.get("node_3", 0)
        node_2_load = distribution.node_assignments.get("node_2", 0)
        assert node_3_load > node_2_load  # Node 3 has more available capacity
    
    @pytest.mark.asyncio
    async def test_distribute_load_with_constraints(self, load_balancer, sample_nodes):
        """Test load distribution with node constraints"""
        # Add constraint that filters out nodes with health < 0.85
        load_balancer.load_balancing_rules[CapabilityType.PROCESSING] = LoadBalancingRule(
            rule_id="test_rule",
            capability_type=CapabilityType.PROCESSING,
            strategy=LoadBalancingStrategy.ROUND_ROBIN,
            weight_factors={},
            constraints=["health_score > 0.85"],
            priority=5
        )
        
        distribution = await load_balancer.distribute_load(
            CapabilityType.PROCESSING, 200.0, sample_nodes
        )
        
        # Should only use nodes with health > 0.85 (node_1: 0.9, node_3: 0.95)
        # node_2 has health 0.8, so should be excluded
        assert len(distribution.node_assignments) == 2
        assert "node_1" in distribution.node_assignments
        assert "node_3" in distribution.node_assignments
        assert "node_2" not in distribution.node_assignments
    
    def test_filter_nodes_by_constraints(self, load_balancer, sample_nodes):
        """Test node filtering by constraints"""
        constraints = ["health_score > 0.85", "error_rate < 0.15"]
        
        filtered_nodes = load_balancer._filter_nodes_by_constraints(sample_nodes, constraints)
        
        # Should filter out node_2 (health: 0.8, error_rate: 0.2)
        assert len(filtered_nodes) == 2
        node_ids = [node.node_id for node in filtered_nodes]
        assert "node_1" in node_ids
        assert "node_3" in node_ids
        assert "node_2" not in node_ids
    
    def test_evaluate_constraint(self, load_balancer, sample_nodes):
        """Test constraint evaluation"""
        node = sample_nodes[0]  # node_1 with health_score 0.9
        
        # Test health score constraint
        assert load_balancer._evaluate_constraint(node, "health_score > 0.8")
        assert not load_balancer._evaluate_constraint(node, "health_score > 0.95")
        
        # Test error rate constraint
        assert load_balancer._evaluate_constraint(node, "error_rate < 0.2")
        assert not load_balancer._evaluate_constraint(node, "error_rate < 0.05")
        
        # Test current load constraint
        assert load_balancer._evaluate_constraint(node, "current_load < 50.0")
        assert not load_balancer._evaluate_constraint(node, "current_load < 20.0")
    
    @pytest.mark.asyncio
    async def test_get_load_balancing_analytics(self, load_balancer):
        """Test load balancing analytics generation"""
        # Add some test data
        load_balancer.distribution_history = [
            LoadDistribution(
                distribution_id="dist_1",
                capability_type=CapabilityType.PROCESSING,
                strategy_used=LoadBalancingStrategy.ROUND_ROBIN,
                node_assignments={"node_1": 50.0, "node_2": 50.0},
                expected_performance={"response_time": 100.0},
                confidence_score=0.8
            ),
            LoadDistribution(
                distribution_id="dist_2",
                capability_type=CapabilityType.AI_INFERENCE,
                strategy_used=LoadBalancingStrategy.RESOURCE_BASED,
                node_assignments={"node_1": 75.0, "node_2": 25.0},
                expected_performance={"response_time": 120.0},
                confidence_score=0.9
            )
        ]
        
        analytics = await load_balancer.get_load_balancing_analytics()
        
        assert isinstance(analytics, dict)
        assert "total_distributions" in analytics
        assert "average_confidence" in analytics
        assert "strategy_usage" in analytics
        
        assert analytics["total_distributions"] == 2
        assert analytics["average_confidence"] == 0.85
        assert "round_robin" in analytics["strategy_usage"]
        assert "resource_based" in analytics["strategy_usage"]


class TestInfiniteScalingManager:
    """Test InfiniteScalingManager functionality"""
    
    @pytest.fixture
    def scaling_manager(self):
        return InfiniteScalingManager()
    
    @pytest.fixture
    def sample_capability_metrics(self):
        return {
            CapabilityType.PROCESSING: {
                "load_percentage": 85.0,
                "response_time": 200.0,
                "total_capacity": 100.0,
                "total_workload": 150.0,
                "load_trend": 8.0
            },
            CapabilityType.AI_INFERENCE: {
                "load_percentage": 75.0,
                "response_time": 300.0,
                "total_capacity": 200.0,
                "total_workload": 180.0,
                "load_trend": 12.0
            }
        }
    
    @pytest.fixture
    def sample_workload_forecast(self):
        return {
            CapabilityType.PROCESSING: 200.0,
            CapabilityType.AI_INFERENCE: 250.0
        }
    
    def test_infinite_scaling_manager_initialization(self, scaling_manager):
        """Test InfiniteScalingManager initialization"""
        assert isinstance(scaling_manager.capability_expander, CapabilityExpander)
        assert isinstance(scaling_manager.load_balancer, LoadBalancer)
        assert isinstance(scaling_manager.scaling_algorithms, dict)
        assert isinstance(scaling_manager.resource_pools, dict)
        assert isinstance(scaling_manager.scaling_history, list)
        
        # Check that algorithms are initialized
        assert "exponential_scaling" in scaling_manager.scaling_algorithms
        assert "predictive_scaling" in scaling_manager.scaling_algorithms
        assert "elastic_scaling" in scaling_manager.scaling_algorithms
        assert "burst_scaling" in scaling_manager.scaling_algorithms
        
        # Check algorithm structure
        exp_algorithm = scaling_manager.scaling_algorithms["exponential_scaling"]
        assert "description" in exp_algorithm
        assert "parameters" in exp_algorithm
        assert "suitable_for" in exp_algorithm
    
    @pytest.mark.asyncio
    async def test_orchestrate_infinite_scaling(self, scaling_manager, sample_capability_metrics, sample_workload_forecast):
        """Test infinite scaling orchestration"""
        result = await scaling_manager.orchestrate_infinite_scaling(
            sample_capability_metrics, sample_workload_forecast
        )
        
        assert isinstance(result, dict)
        assert "orchestration_id" in result
        assert "expansion_plans_created" in result
        assert "expansion_plans_executed" in result
        assert "load_balancing_updates" in result
        assert "scaling_optimizations" in result
        assert "total_execution_time" in result
        assert "timestamp" in result
        
        assert result["expansion_plans_created"] > 0
        assert result["scaling_optimizations"] > 0
        assert result["total_execution_time"] > 0
        
        # Should be added to scaling history
        assert len(scaling_manager.scaling_history) == 1
    
    def test_select_scaling_algorithm(self, scaling_manager):
        """Test scaling algorithm selection"""
        # Test burst scaling selection (high load + high trend)
        high_load_metrics = {"load_percentage": 95.0, "load_trend": 15.0}
        algorithm = scaling_manager._select_scaling_algorithm(CapabilityType.PROCESSING, high_load_metrics)
        assert algorithm == "burst_scaling"
        
        # Test predictive scaling selection (increasing trend)
        trending_metrics = {"load_percentage": 60.0, "load_trend": 8.0}
        algorithm = scaling_manager._select_scaling_algorithm(CapabilityType.PROCESSING, trending_metrics)
        assert algorithm == "predictive_scaling"
        
        # Test exponential scaling selection (high load)
        high_load_metrics = {"load_percentage": 80.0, "load_trend": 2.0}
        algorithm = scaling_manager._select_scaling_algorithm(CapabilityType.PROCESSING, high_load_metrics)
        assert algorithm == "exponential_scaling"
        
        # Test elastic scaling selection (normal conditions)
        normal_metrics = {"load_percentage": 50.0, "load_trend": 1.0}
        algorithm = scaling_manager._select_scaling_algorithm(CapabilityType.PROCESSING, normal_metrics)
        assert algorithm == "elastic_scaling"
    
    @pytest.mark.asyncio
    async def test_execute_scaling_algorithm(self, scaling_manager):
        """Test scaling algorithm execution"""
        metrics = {
            "total_capacity": 100.0,
            "load_percentage": 85.0,
            "load_trend": 10.0
        }
        
        result = await scaling_manager._execute_scaling_algorithm(
            "exponential_scaling", CapabilityType.PROCESSING, metrics
        )
        
        assert isinstance(result, dict)
        assert "algorithm" in result
        assert "capability_type" in result
        assert "current_capacity" in result
        assert "target_capacity" in result
        assert "scaling_needed" in result
        assert "scale_factor" in result
        assert "confidence" in result
        
        assert result["algorithm"] == "exponential_scaling"
        assert result["capability_type"] == "processing"
        assert result["target_capacity"] > result["current_capacity"]
        assert result["scaling_needed"] is True
    
    @pytest.mark.asyncio
    async def test_get_infinite_scaling_analytics(self, scaling_manager):
        """Test infinite scaling analytics generation"""
        # Add some test data
        scaling_manager.scaling_history = [
            {
                "expansion_plans_created": 2,
                "expansion_plans_executed": 2,
                "total_execution_time": 10.5,
                "scaling_optimizations": [
                    {"algorithm": "exponential_scaling"},
                    {"algorithm": "predictive_scaling"}
                ]
            },
            {
                "expansion_plans_created": 1,
                "expansion_plans_executed": 1,
                "total_execution_time": 8.2,
                "scaling_optimizations": [
                    {"algorithm": "elastic_scaling"}
                ]
            }
        ]
        
        analytics = await scaling_manager.get_infinite_scaling_analytics()
        
        assert isinstance(analytics, dict)
        assert "infinite_scaling_analytics" in analytics
        assert "expansion_analytics" in analytics
        assert "load_balancing_analytics" in analytics
        
        infinite_analytics = analytics["infinite_scaling_analytics"]
        assert "total_orchestrations" in infinite_analytics
        assert "success_rate" in infinite_analytics
        assert "algorithm_usage" in infinite_analytics
        assert "available_algorithms" in infinite_analytics
        
        assert infinite_analytics["total_orchestrations"] == 2
        assert infinite_analytics["available_algorithms"] == 4
        assert "exponential_scaling" in infinite_analytics["algorithm_usage"]


if __name__ == "__main__":
    pytest.main([__file__])