"""
Tests for Supreme Monitoring System
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock

from core.supreme.supreme_monitoring import (
    SupremeMonitoringSystem,
    MetricsCollector,
    AlertManager,
    HealthMonitor,
    PerformanceAnalyzer,
    ContinuousImprovement,
    Metric,
    Alert,
    HealthCheck,
    MetricType,
    AlertLevel,
    MonitoringStatus
)

from core.supreme.supreme_control_interface import SupremeControlInterface


class TestMetricsCollector:
    """Test MetricsCollector functionality"""
    
    @pytest.fixture
    def metrics_collector(self):
        return MetricsCollector()
    
    def test_metrics_collector_initialization(self, metrics_collector):
        """Test MetricsCollector initialization"""
        assert isinstance(metrics_collector.metrics, dict)
        assert isinstance(metrics_collector.metric_definitions, dict)
        assert isinstance(metrics_collector.collection_intervals, dict)
        assert metrics_collector.max_metric_history == 1000
    
    def test_register_metric(self, metrics_collector):
        """Test metric registration"""
        metrics_collector.register_metric(
            "test_metric", MetricType.PERFORMANCE, 
            "Test Metric", "units", 60.0
        )
        
        assert "test_metric" in metrics_collector.metric_definitions
        assert "test_metric" in metrics_collector.collection_intervals
        assert "test_metric" in metrics_collector.metrics
        
        definition = metrics_collector.metric_definitions["test_metric"]
        assert definition["type"] == MetricType.PERFORMANCE
        assert definition["name"] == "Test Metric"
        assert definition["unit"] == "units"
    
    def test_record_metric(self, metrics_collector):
        """Test metric recording"""
        # Register metric first
        metrics_collector.register_metric(
            "test_metric", MetricType.PERFORMANCE, 
            "Test Metric", "units"
        )
        
        # Create and record metric
        metric = Metric(
            metric_id="test_metric",
            metric_type=MetricType.PERFORMANCE,
            name="Test Metric",
            value=42.0,
            unit="units",
            timestamp=datetime.now(),
            source="test"
        )
        
        metrics_collector.record_metric(metric)
        
        # Check that metric was recorded
        assert len(metrics_collector.metrics["test_metric"]) == 1
        recorded_metric = metrics_collector.metrics["test_metric"][0]
        assert recorded_metric.value == 42.0
    
    def test_get_metric_statistics(self, metrics_collector):
        """Test metric statistics calculation"""
        # Register and record multiple metrics
        metrics_collector.register_metric(
            "test_metric", MetricType.PERFORMANCE, 
            "Test Metric", "units"
        )
        
        values = [10.0, 20.0, 30.0, 40.0, 50.0]
        for value in values:
            metric = Metric(
                metric_id="test_metric",
                metric_type=MetricType.PERFORMANCE,
                name="Test Metric",
                value=value,
                unit="units",
                timestamp=datetime.now(),
                source="test"
            )
            metrics_collector.record_metric(metric)
        
        stats = metrics_collector.get_metric_statistics("test_metric")
        
        assert stats["count"] == 5
        assert stats["mean"] == 30.0
        assert stats["median"] == 30.0
        assert stats["min"] == 10.0
        assert stats["max"] == 50.0
        assert stats["latest"] == 50.0
    
    def test_get_all_metrics_summary(self, metrics_collector):
        """Test getting summary of all metrics"""
        # Register a metric and record some data
        metrics_collector.register_metric(
            "test_metric", MetricType.PERFORMANCE, 
            "Test Metric", "units"
        )
        
        metric = Metric(
            metric_id="test_metric",
            metric_type=MetricType.PERFORMANCE,
            name="Test Metric",
            value=42.0,
            unit="units",
            timestamp=datetime.now(),
            source="test"
        )
        metrics_collector.record_metric(metric)
        
        summary = metrics_collector.get_all_metrics_summary()
        
        assert "test_metric" in summary
        assert "definition" in summary["test_metric"]
        assert "recent_stats" in summary["test_metric"]
        assert "data_points" in summary["test_metric"]


class TestAlertManager:
    """Test AlertManager functionality"""
    
    @pytest.fixture
    def alert_manager(self):
        return AlertManager()
    
    def test_alert_manager_initialization(self, alert_manager):
        """Test AlertManager initialization"""
        assert isinstance(alert_manager.alerts, list)
        assert isinstance(alert_manager.alert_rules, dict)
        assert isinstance(alert_manager.notification_handlers, list)
        assert len(alert_manager.alerts) == 0
    
    def test_add_alert_rule(self, alert_manager):
        """Test adding alert rules"""
        alert_manager.add_alert_rule(
            "test_rule", "test_metric", "greater_than", 
            100.0, AlertLevel.WARNING, "Test alert"
        )
        
        assert "test_rule" in alert_manager.alert_rules
        rule = alert_manager.alert_rules["test_rule"]
        assert rule["metric_id"] == "test_metric"
        assert rule["condition"] == "greater_than"
        assert rule["threshold"] == 100.0
        assert rule["alert_level"] == AlertLevel.WARNING
    
    def test_check_alert_rules(self, alert_manager):
        """Test alert rule checking"""
        # Add alert rule
        alert_manager.add_alert_rule(
            "test_rule", "test_metric", "greater_than", 
            100.0, AlertLevel.WARNING, "Test alert"
        )
        
        # Create metric that should trigger alert
        metric = Metric(
            metric_id="test_metric",
            metric_type=MetricType.PERFORMANCE,
            name="Test Metric",
            value=150.0,  # Above threshold
            unit="units",
            timestamp=datetime.now(),
            source="test"
        )
        
        # Check alert rules
        alert_manager.check_alert_rules(metric)
        
        # Should have triggered an alert
        assert len(alert_manager.alerts) == 1
        alert = alert_manager.alerts[0]
        assert alert.level == AlertLevel.WARNING
        assert alert.metric_id == "test_metric"
        assert alert.actual_value == 150.0
    
    def test_resolve_alert(self, alert_manager):
        """Test alert resolution"""
        # Add and trigger an alert
        alert_manager.add_alert_rule(
            "test_rule", "test_metric", "greater_than", 
            100.0, AlertLevel.WARNING, "Test alert"
        )
        
        metric = Metric(
            metric_id="test_metric",
            metric_type=MetricType.PERFORMANCE,
            name="Test Metric",
            value=150.0,
            unit="units",
            timestamp=datetime.now(),
            source="test"
        )
        
        alert_manager.check_alert_rules(metric)
        
        # Get the alert ID and resolve it
        alert_id = alert_manager.alerts[0].alert_id
        alert_manager.resolve_alert(alert_id)
        
        # Check that alert is resolved
        assert alert_manager.alerts[0].resolved is True
        assert alert_manager.alerts[0].resolved_at is not None
    
    def test_get_active_alerts(self, alert_manager):
        """Test getting active alerts"""
        # Add and trigger alerts
        alert_manager.add_alert_rule(
            "test_rule1", "test_metric", "greater_than", 
            100.0, AlertLevel.WARNING, "Test alert 1"
        )
        alert_manager.add_alert_rule(
            "test_rule2", "test_metric", "greater_than", 
            200.0, AlertLevel.ERROR, "Test alert 2"
        )
        
        metric = Metric(
            metric_id="test_metric",
            metric_type=MetricType.PERFORMANCE,
            name="Test Metric",
            value=250.0,  # Triggers both alerts
            unit="units",
            timestamp=datetime.now(),
            source="test"
        )
        
        alert_manager.check_alert_rules(metric)
        
        # Should have 2 active alerts
        active_alerts = alert_manager.get_active_alerts()
        assert len(active_alerts) == 2
        
        # Resolve one alert
        alert_manager.resolve_alert(active_alerts[0].alert_id)
        
        # Should have 1 active alert
        active_alerts = alert_manager.get_active_alerts()
        assert len(active_alerts) == 1


class TestHealthMonitor:
    """Test HealthMonitor functionality"""
    
    @pytest.fixture
    def mock_interface(self):
        interface = Mock(spec=SupremeControlInterface)
        interface.execute_command = AsyncMock()
        
        # Mock successful health check
        mock_result = Mock()
        mock_result.status = "completed"
        mock_result.result = {"health": "ok"}
        
        interface.execute_command.return_value = mock_result
        return interface
    
    @pytest.fixture
    def health_monitor(self, mock_interface):
        return HealthMonitor(mock_interface)
    
    def test_health_monitor_initialization(self, health_monitor, mock_interface):
        """Test HealthMonitor initialization"""
        assert health_monitor.control_interface == mock_interface
        assert isinstance(health_monitor.health_checks, dict)
        assert isinstance(health_monitor.check_intervals, dict)
        assert isinstance(health_monitor.monitoring_tasks, dict)
        assert not health_monitor.is_monitoring
    
    def test_register_health_check(self, health_monitor):
        """Test health check registration"""
        def dummy_check():
            return True
        
        health_monitor.register_health_check(
            "test_check", "Test Health Check", dummy_check, 60.0
        )
        
        assert "test_check" in health_monitor.check_intervals
        assert health_monitor.check_intervals["test_check"] == 60.0
    
    def test_get_health_status_no_checks(self, health_monitor):
        """Test getting health status with no checks"""
        status = health_monitor.get_health_status()
        
        assert status["status"] == "unknown"
        assert "message" in status
    
    def test_get_health_status_with_checks(self, health_monitor):
        """Test getting health status with checks"""
        # Add some mock health checks
        health_monitor.health_checks["check1"] = HealthCheck(
            check_id="check1",
            name="Check 1",
            status="healthy",
            response_time=0.1,
            timestamp=datetime.now()
        )
        health_monitor.health_checks["check2"] = HealthCheck(
            check_id="check2",
            name="Check 2",
            status="unhealthy",
            response_time=0.2,
            timestamp=datetime.now()
        )
        
        status = health_monitor.get_health_status()
        
        assert status["status"] in ["excellent", "good", "fair", "poor"]
        assert status["health_percentage"] == 50.0  # 1 out of 2 healthy
        assert status["healthy_components"] == 1
        assert status["total_components"] == 2


class TestSupremeMonitoringSystem:
    """Test SupremeMonitoringSystem functionality"""
    
    @pytest.fixture
    def mock_interface(self):
        interface = Mock(spec=SupremeControlInterface)
        interface.execute_command = AsyncMock()
        
        # Mock successful command execution
        mock_result = Mock()
        mock_result.status = "completed"
        mock_result.result = {"response_time": 0.5, "throughput": 100.0}
        
        interface.execute_command.return_value = mock_result
        return interface
    
    @pytest.fixture
    def monitoring_system(self, mock_interface):
        return SupremeMonitoringSystem(mock_interface)
    
    def test_monitoring_system_initialization(self, monitoring_system, mock_interface):
        """Test SupremeMonitoringSystem initialization"""
        assert monitoring_system.control_interface == mock_interface
        assert isinstance(monitoring_system.metrics_collector, MetricsCollector)
        assert isinstance(monitoring_system.alert_manager, AlertManager)
        assert isinstance(monitoring_system.health_monitor, HealthMonitor)
        assert isinstance(monitoring_system.performance_analyzer, PerformanceAnalyzer)
        assert isinstance(monitoring_system.continuous_improvement, ContinuousImprovement)
        assert monitoring_system.monitoring_status == MonitoringStatus.INACTIVE
    
    def test_setup_default_metrics(self, monitoring_system):
        """Test default metrics setup"""
        # Check that default metrics are registered
        metrics = monitoring_system.metrics_collector.metric_definitions
        
        assert "response_time_avg" in metrics
        assert "throughput" in metrics
        assert "error_rate" in metrics
        assert "availability" in metrics
        assert "cpu_utilization" in metrics
        assert "memory_utilization" in metrics
        assert "user_satisfaction" in metrics
    
    def test_setup_default_alerts(self, monitoring_system):
        """Test default alert rules setup"""
        # Check that default alert rules are set up
        rules = monitoring_system.alert_manager.alert_rules
        
        assert "high_response_time" in rules
        assert "high_error_rate" in rules
        assert "low_availability" in rules
        assert "high_cpu" in rules
        assert "high_memory" in rules
    
    def test_get_system_status(self, monitoring_system):
        """Test getting system status"""
        status = monitoring_system.get_system_status()
        
        assert isinstance(status, dict)
        assert "overall_status" in status
        assert "health_percentage" in status
        assert "monitoring_active" in status
        assert "active_alerts" in status
        assert "timestamp" in status
        
        # Should be healthy initially
        assert status["overall_status"] in ["healthy", "warning", "degraded", "critical", "unknown"]
    
    def test_get_monitoring_dashboard(self, monitoring_system):
        """Test getting monitoring dashboard"""
        dashboard = monitoring_system.get_monitoring_dashboard()
        
        assert isinstance(dashboard, dict)
        assert "monitoring_status" in dashboard
        assert "system_health" in dashboard
        assert "active_alerts" in dashboard
        assert "alert_summary" in dashboard
        assert "metrics_summary" in dashboard
        assert "improvement_summary" in dashboard
        assert "last_updated" in dashboard


if __name__ == "__main__":
    pytest.main([__file__])