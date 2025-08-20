"""
Tests for Supreme Testing Framework
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, AsyncMock

from core.supreme.supreme_testing_framework import (
    SupremeTestingFramework,
    PerformanceBenchmark,
    SecurityTester,
    TestType,
    TestStatus,
    TestPriority,
    TestResult,
    TestCase
)

from core.supreme.supreme_control_interface import SupremeControlInterface, CommandType
from core.supreme.supreme_orchestrator import EngineType


class TestPerformanceBenchmark:
    """Test PerformanceBenchmark functionality"""
    
    @pytest.fixture
    def performance_benchmark(self):
        return PerformanceBenchmark()
    
    @pytest.fixture
    def mock_interface(self):
        interface = Mock(spec=SupremeControlInterface)
        interface.execute_command = AsyncMock()
        
        # Mock successful command execution
        mock_result = Mock()
        mock_result.status = "completed"
        mock_result.result = {"test": "success"}
        mock_result.execution_time = 0.5
        
        interface.execute_command.return_value = mock_result
        return interface
    
    def test_performance_benchmark_initialization(self, performance_benchmark):
        """Test PerformanceBenchmark initialization"""
        assert isinstance(performance_benchmark.benchmarks, dict)
        assert isinstance(performance_benchmark.baseline_metrics, dict)
        assert isinstance(performance_benchmark.performance_history, list)
        assert len(performance_benchmark.benchmarks) == 0
    
    @pytest.mark.asyncio
    async def test_run_performance_benchmark(self, performance_benchmark, mock_interface):
        """Test performance benchmark execution"""
        test_scenarios = [
            {"name": "Test Scenario 1", "operation": "test_op", "parameters": {"test": "data"}},
            {"name": "Test Scenario 2", "operation": "test_op2", "parameters": {"test": "data2"}}
        ]
        
        result = await performance_benchmark.run_performance_benchmark(
            EngineType.REASONING, mock_interface, test_scenarios
        )
        
        assert isinstance(result, dict)
        assert "benchmark_id" in result
        assert "engine_type" in result
        assert result["engine_type"] == "reasoning"
        assert "scenario_results" in result
        assert "summary_metrics" in result
        assert len(result["scenario_results"]) == 2
        
        # Check summary metrics
        summary = result["summary_metrics"]
        assert "total_execution_time" in summary
        assert "average_response_time" in summary
        assert "throughput" in summary
        assert "success_rate" in summary
        
        # Should be stored in benchmarks
        assert len(performance_benchmark.benchmarks) == 1
        assert len(performance_benchmark.performance_history) == 1
    
    def test_set_baseline_metrics(self, performance_benchmark):
        """Test setting baseline metrics"""
        baseline_metrics = {
            "average_response_time": 0.5,
            "throughput": 10.0,
            "success_rate": 0.95
        }
        
        performance_benchmark.set_baseline_metrics(EngineType.REASONING, baseline_metrics)
        
        assert "reasoning" in performance_benchmark.baseline_metrics
        assert performance_benchmark.baseline_metrics["reasoning"] == baseline_metrics
    
    def test_compare_with_baseline(self, performance_benchmark):
        """Test baseline comparison"""
        # Set baseline
        baseline_metrics = {
            "average_response_time": 0.5,
            "throughput": 10.0,
            "success_rate": 0.95
        }
        performance_benchmark.set_baseline_metrics(EngineType.REASONING, baseline_metrics)
        
        # Create benchmark results
        benchmark_results = {
            "engine_type": "reasoning",
            "summary_metrics": {
                "average_response_time": 0.4,  # Improved
                "throughput": 12.0,  # Improved
                "success_rate": 0.90  # Degraded
            }
        }
        
        comparison = performance_benchmark.compare_with_baseline(benchmark_results)
        
        assert isinstance(comparison, dict)
        assert "comparison" in comparison
        assert "overall_status" in comparison
        
        comp_data = comparison["comparison"]
        assert "average_response_time" in comp_data
        assert "throughput" in comp_data
        assert "success_rate" in comp_data
        
        # Check that improvements and degradations are detected
        assert comp_data["throughput"]["status"] == "improved"


class TestSecurityTester:
    """Test SecurityTester functionality"""
    
    @pytest.fixture
    def security_tester(self):
        return SecurityTester()
    
    @pytest.fixture
    def mock_interface(self):
        interface = Mock(spec=SupremeControlInterface)
        interface.execute_command = AsyncMock()
        
        # Mock successful security test
        mock_result = Mock()
        mock_result.status = "completed"
        mock_result.result = {"security_test": "passed"}
        
        interface.execute_command.return_value = mock_result
        return interface
    
    def test_security_tester_initialization(self, security_tester):
        """Test SecurityTester initialization"""
        assert isinstance(security_tester.security_tests, list)
        assert isinstance(security_tester.vulnerability_reports, list)
        assert isinstance(security_tester.security_baselines, dict)
        assert len(security_tester.vulnerability_reports) == 0
    
    @pytest.mark.asyncio
    async def test_run_security_assessment(self, security_tester, mock_interface):
        """Test security assessment execution"""
        result = await security_tester.run_security_assessment(mock_interface)
        
        assert isinstance(result, dict)
        assert "assessment_id" in result
        assert "test_results" in result
        assert "vulnerabilities" in result
        assert "security_score" in result
        assert "recommendations" in result
        
        # Check that tests were run
        assert len(result["test_results"]) > 0
        
        # Check security score
        assert isinstance(result["security_score"], (int, float))
        assert 0 <= result["security_score"] <= 100
        
        # Should be stored in vulnerability reports
        assert len(security_tester.vulnerability_reports) == 1


class TestSupremeTestingFramework:
    """Test SupremeTestingFramework functionality"""
    
    @pytest.fixture
    def mock_interface(self):
        interface = Mock(spec=SupremeControlInterface)
        interface.execute_command = AsyncMock()
        
        # Mock successful command execution
        mock_result = Mock()
        mock_result.status = "completed"
        mock_result.result = {"test": "success"}
        mock_result.execution_time = 0.5
        mock_result.engines_used = ["reasoning", "analytics"]
        
        interface.execute_command.return_value = mock_result
        return interface
    
    @pytest.fixture
    def testing_framework(self, mock_interface):
        return SupremeTestingFramework(mock_interface)
    
    def test_testing_framework_initialization(self, testing_framework, mock_interface):
        """Test SupremeTestingFramework initialization"""
        assert testing_framework.control_interface == mock_interface
        assert isinstance(testing_framework.performance_benchmark, PerformanceBenchmark)
        assert isinstance(testing_framework.security_tester, SecurityTester)
        assert isinstance(testing_framework.test_suites, dict)
        assert isinstance(testing_framework.test_results, dict)
        assert isinstance(testing_framework.test_history, list)
    
    @pytest.mark.asyncio
    async def test_test_engine(self, testing_framework):
        """Test individual engine testing"""
        result = await testing_framework._test_engine(EngineType.REASONING)
        
        assert isinstance(result, dict)
        assert "engine_type" in result
        assert result["engine_type"] == "reasoning"
        assert "test_scenarios" in result
        assert "passed" in result
        assert "failed" in result
        assert "errors" in result
        assert "success_rate" in result
        assert "test_details" in result
        
        # Check that tests were executed
        assert result["test_scenarios"] > 0
        assert isinstance(result["success_rate"], (int, float))
    
    def test_get_engine_test_scenarios(self, testing_framework):
        """Test engine test scenario generation"""
        scenarios = testing_framework._get_engine_test_scenarios(EngineType.REASONING)
        
        assert isinstance(scenarios, list)
        assert len(scenarios) > 0
        
        # Check scenario structure
        for scenario in scenarios:
            assert "name" in scenario
            assert "operation" in scenario
            assert "parameters" in scenario
    
    @pytest.mark.asyncio
    async def test_run_performance_tests(self, testing_framework):
        """Test performance testing execution"""
        result = await testing_framework._run_performance_tests()
        
        assert isinstance(result, dict)
        assert len(result) > 0  # Should test at least one engine
        
        # Check that each engine result has the expected structure
        for engine_result in result.values():
            if isinstance(engine_result, dict) and "summary_metrics" in engine_result:
                assert "total_execution_time" in engine_result["summary_metrics"]
                assert "success_rate" in engine_result["summary_metrics"]
    
    @pytest.mark.asyncio
    async def test_run_integration_tests(self, testing_framework):
        """Test integration testing execution"""
        result = await testing_framework._run_integration_tests()
        
        assert isinstance(result, dict)
        assert "multi_engine_coordination" in result
        assert "data_flow_integration" in result
        assert "orchestration_integration" in result
        
        # Check that each integration test has status
        for test_result in result.values():
            assert isinstance(test_result, dict)
            assert "status" in test_result
    
    def test_calculate_overall_status(self, testing_framework):
        """Test overall status calculation"""
        # Mock test results
        mock_results = {
            "engine_tests": {
                "reasoning": {"passed": 8, "failed": 1, "errors": 1},
                "analytics": {"passed": 9, "failed": 1, "errors": 0}
            },
            "security_assessment": {"security_score": 85},
            "integration_tests": {
                "test1": {"status": "passed"},
                "test2": {"status": "passed"},
                "test3": {"status": "failed"}
            }
        }
        
        status = testing_framework._calculate_overall_status(mock_results)
        
        assert isinstance(status, str)
        assert status in ["excellent", "good", "acceptable", "needs_improvement", "unknown"]
    
    def test_get_test_summary_no_history(self, testing_framework):
        """Test getting test summary with no history"""
        summary = testing_framework.get_test_summary()
        
        assert isinstance(summary, dict)
        assert "message" in summary
        assert summary["message"] == "No test history available"
    
    def test_get_test_summary_with_history(self, testing_framework):
        """Test getting test summary with history"""
        # Add mock test history
        mock_test_result = {
            "test_run_id": "test_123",
            "overall_status": "good",
            "end_time": "2023-01-01T12:00:00",
            "engine_tests": {"reasoning": {"passed": 5, "failed": 0, "errors": 0}},
            "security_assessment": {"security_score": 80},
            "performance_benchmarks": {
                "reasoning": {
                    "summary_metrics": {
                        "average_response_time": 0.5,
                        "throughput": 10.0,
                        "success_rate": 0.95
                    }
                }
            }
        }
        
        testing_framework.test_history.append(mock_test_result)
        
        summary = testing_framework.get_test_summary()
        
        assert isinstance(summary, dict)
        assert "latest_test_run" in summary
        assert "overall_status" in summary
        assert "total_test_runs" in summary
        assert "engines_tested" in summary
        assert "security_score" in summary
        assert "performance_summary" in summary
        
        assert summary["latest_test_run"] == "test_123"
        assert summary["overall_status"] == "good"
        assert summary["total_test_runs"] == 1
        assert summary["security_score"] == 80


if __name__ == "__main__":
    pytest.main([__file__])