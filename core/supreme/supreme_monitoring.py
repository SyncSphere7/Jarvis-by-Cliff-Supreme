"""
Supreme Monitoring and Improvement System
Continuous monitoring, analytics, and optimization for all supreme capabilities
"""

import logging
import asyncio
import time
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import statistics
from collections import deque

from .supreme_control_interface import SupremeControlInterface, CommandType, SupremeCommand
from .supreme_orchestrator import EngineType

logger = logging.getLogger(__name__)


class MetricType(Enum):
    PERFORMANCE = "performance"
    AVAILABILITY = "availability"
    RELIABILITY = "reliability"
    SECURITY = "security"
    EFFICIENCY = "efficiency"
    USER_SATISFACTION = "user_satisfaction"
    RESOURCE_UTILIZATION = "resource_utilization"
    ERROR_RATE = "error_rate"


class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class MonitoringStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PAUSED = "paused"
    ERROR = "error"


@dataclass
class Metric:
    metric_id: str
    metric_type: MetricType
    name: str
    value: float
    unit: str
    timestamp: datetime
    source: str
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Alert:
    alert_id: str
    level: AlertLevel
    title: str
    description: str
    source: str
    metric_id: Optional[str]
    threshold_value: Optional[float]
    actual_value: Optional[float]
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None


@dataclass
class HealthCheck:
    check_id: str
    name: str
    status: str
    response_time: float
    timestamp: datetime
    details: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None


class MetricsCollector:
    """Collects and manages metrics from all supreme engines"""
    
    def __init__(self):
        self.metrics: Dict[str, deque] = {}  # Metric ID -> deque of recent values
        self.metric_definitions: Dict[str, Dict[str, Any]] = {}
        self.collection_intervals: Dict[str, float] = {}
        self.max_metric_history = 1000  # Keep last 1000 values per metric
    
    def register_metric(self, metric_id: str, metric_type: MetricType, 
                       name: str, unit: str, collection_interval: float = 60.0):
        """Register a new metric for collection"""
        self.metric_definitions[metric_id] = {
            "type": metric_type,
            "name": name,
            "unit": unit,
            "registered_at": datetime.now()
        }
        self.collection_intervals[metric_id] = collection_interval
        self.metrics[metric_id] = deque(maxlen=self.max_metric_history)
        
        logger.info(f"Registered metric: {name} ({metric_id})")
    
    def record_metric(self, metric: Metric):
        """Record a metric value"""
        if metric.metric_id not in self.metrics:
            # Auto-register if not exists
            self.register_metric(
                metric.metric_id, 
                metric.metric_type, 
                metric.name, 
                metric.unit
            )
        
        self.metrics[metric.metric_id].append(metric)
    
    def get_metric_history(self, metric_id: str, 
                          time_range: Optional[timedelta] = None) -> List[Metric]:
        """Get metric history for a specific metric"""
        if metric_id not in self.metrics:
            return []
        
        metrics = list(self.metrics[metric_id])
        
        if time_range:
            cutoff_time = datetime.now() - time_range
            metrics = [m for m in metrics if m.timestamp >= cutoff_time]
        
        return metrics
    
    def get_metric_statistics(self, metric_id: str, 
                            time_range: Optional[timedelta] = None) -> Dict[str, float]:
        """Get statistical summary of a metric"""
        history = self.get_metric_history(metric_id, time_range)
        
        if not history:
            return {}
        
        values = [m.value for m in history]
        
        return {
            "count": len(values),
            "mean": statistics.mean(values),
            "median": statistics.median(values),
            "min": min(values),
            "max": max(values),
            "std_dev": statistics.stdev(values) if len(values) > 1 else 0.0,
            "latest": values[-1] if values else 0.0
        }
    
    def get_all_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of all registered metrics"""
        summary = {}
        
        for metric_id, definition in self.metric_definitions.items():
            stats = self.get_metric_statistics(metric_id, timedelta(hours=1))
            summary[metric_id] = {
                "definition": definition,
                "recent_stats": stats,
                "data_points": len(self.metrics.get(metric_id, []))
            }
        
        return summary


class AlertManager:
    """Manages alerts and notifications for system issues"""
    
    def __init__(self):
        self.alerts: List[Alert] = []
        self.alert_rules: Dict[str, Dict[str, Any]] = {}
        self.notification_handlers: List[Callable] = []
    
    def add_alert_rule(self, rule_id: str, metric_id: str, 
                      condition: str, threshold: float, 
                      alert_level: AlertLevel, message: str):
        """Add an alert rule for a metric"""
        self.alert_rules[rule_id] = {
            "metric_id": metric_id,
            "condition": condition,  # "greater_than", "less_than", "equals"
            "threshold": threshold,
            "alert_level": alert_level,
            "message": message,
            "created_at": datetime.now(),
            "triggered_count": 0,
            "last_triggered": None
        }
        
        logger.info(f"Added alert rule: {rule_id} for metric {metric_id}")
    
    def check_alert_rules(self, metric: Metric):
        """Check if any alert rules are triggered by a metric"""
        for rule_id, rule in self.alert_rules.items():
            if rule["metric_id"] == metric.metric_id:
                if self._evaluate_condition(metric.value, rule["condition"], rule["threshold"]):
                    self._trigger_alert(rule_id, rule, metric)
    
    def _evaluate_condition(self, value: float, condition: str, threshold: float) -> bool:
        """Evaluate alert condition"""
        if condition == "greater_than":
            return value > threshold
        elif condition == "less_than":
            return value < threshold
        elif condition == "equals":
            return abs(value - threshold) < 0.001  # Float comparison
        elif condition == "not_equals":
            return abs(value - threshold) >= 0.001
        else:
            return False
    
    def _trigger_alert(self, rule_id: str, rule: Dict[str, Any], metric: Metric):
        """Trigger an alert"""
        alert = Alert(
            alert_id=f"alert_{rule_id}_{datetime.now().isoformat()}",
            level=rule["alert_level"],
            title=f"Alert: {rule['message']}",
            description=f"Metric {metric.name} value {metric.value} {rule['condition']} {rule['threshold']}",
            source=metric.source,
            metric_id=metric.metric_id,
            threshold_value=rule["threshold"],
            actual_value=metric.value,
            timestamp=datetime.now()
        )
        
        self.alerts.append(alert)
        rule["triggered_count"] += 1
        rule["last_triggered"] = datetime.now()
        
        # Notify handlers
        for handler in self.notification_handlers:
            try:
                handler(alert)
            except Exception as e:
                logger.error(f"Error in notification handler: {e}")
        
        logger.warning(f"Alert triggered: {alert.title}")
    
    def resolve_alert(self, alert_id: str):
        """Mark an alert as resolved"""
        for alert in self.alerts:
            if alert.alert_id == alert_id and not alert.resolved:
                alert.resolved = True
                alert.resolved_at = datetime.now()
                logger.info(f"Alert resolved: {alert_id}")
                break
    
    def get_active_alerts(self) -> List[Alert]:
        """Get all active (unresolved) alerts"""
        return [alert for alert in self.alerts if not alert.resolved]
    
    def get_alert_summary(self) -> Dict[str, Any]:
        """Get summary of alert status"""
        active_alerts = self.get_active_alerts()
        
        return {
            "total_alerts": len(self.alerts),
            "active_alerts": len(active_alerts),
            "critical_alerts": len([a for a in active_alerts if a.level == AlertLevel.CRITICAL]),
            "error_alerts": len([a for a in active_alerts if a.level == AlertLevel.ERROR]),
            "warning_alerts": len([a for a in active_alerts if a.level == AlertLevel.WARNING]),
            "alert_rules": len(self.alert_rules)
        }


class HealthMonitor:
    """Monitors health of all supreme engines and components"""
    
    def __init__(self, control_interface: SupremeControlInterface):
        self.control_interface = control_interface
        self.health_checks: Dict[str, HealthCheck] = {}
        self.check_intervals: Dict[str, float] = {}
        self.monitoring_tasks: Dict[str, asyncio.Task] = {}
        self.is_monitoring = False
    
    def register_health_check(self, check_id: str, name: str, 
                            check_function: Callable, interval: float = 300.0):
        """Register a health check"""
        self.check_intervals[check_id] = interval
        
        # Store check function reference (simplified for demo)
        logger.info(f"Registered health check: {name} ({check_id})")
    
    async def start_monitoring(self):
        """Start health monitoring"""
        self.is_monitoring = True
        
        # Start monitoring tasks for each engine
        engines_to_monitor = [
            EngineType.REASONING,
            EngineType.ANALYTICS,
            EngineType.COMMUNICATION,
            EngineType.SECURITY,
            EngineType.SCALABILITY,
            EngineType.LEARNING,
            EngineType.PROACTIVE,
            EngineType.KNOWLEDGE,
            EngineType.SYSTEM_CONTROL,
            EngineType.INTEGRATION
        ]
        
        for engine in engines_to_monitor:
            task = asyncio.create_task(self._monitor_engine_health(engine))
            self.monitoring_tasks[engine.value] = task
        
        logger.info("Health monitoring started")
    
    async def stop_monitoring(self):
        """Stop health monitoring"""
        self.is_monitoring = False
        
        # Cancel all monitoring tasks
        for task in self.monitoring_tasks.values():
            task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(*self.monitoring_tasks.values(), return_exceptions=True)
        self.monitoring_tasks.clear()
        
        logger.info("Health monitoring stopped")
    
    async def _monitor_engine_health(self, engine_type: EngineType):
        """Monitor health of a specific engine"""
        check_id = f"health_{engine_type.value}"
        
        while self.is_monitoring:
            try:
                start_time = time.time()
                
                # Perform health check
                command = SupremeCommand(
                    command_id=f"health_check_{engine_type.value}",
                    command_type=CommandType.MONITOR,
                    operation="health_check",
                    parameters={"engine": engine_type.value}
                )
                
                result = await self.control_interface.execute_command(command)
                response_time = time.time() - start_time
                
                # Create health check result
                if result and result.status == "completed":
                    status = "healthy"
                    error_message = None
                else:
                    status = "unhealthy"
                    error_message = f"Health check failed: {result.errors if result else 'No response'}"
                
                health_check = HealthCheck(
                    check_id=check_id,
                    name=f"{engine_type.value} Health Check",
                    status=status,
                    response_time=response_time,
                    timestamp=datetime.now(),
                    details={"engine_type": engine_type.value},
                    error_message=error_message
                )
                
                self.health_checks[check_id] = health_check
                
                # Wait for next check
                await asyncio.sleep(self.check_intervals.get(check_id, 300.0))
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health monitoring for {engine_type.value}: {e}")
                await asyncio.sleep(60.0)  # Wait before retrying
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get overall health status"""
        if not self.health_checks:
            return {"status": "unknown", "message": "No health checks available"}
        
        healthy_checks = len([hc for hc in self.health_checks.values() if hc.status == "healthy"])
        total_checks = len(self.health_checks)
        
        health_percentage = (healthy_checks / total_checks) * 100 if total_checks > 0 else 0
        
        if health_percentage >= 90:
            overall_status = "excellent"
        elif health_percentage >= 80:
            overall_status = "good"
        elif health_percentage >= 70:
            overall_status = "fair"
        else:
            overall_status = "poor"
        
        return {
            "status": overall_status,
            "health_percentage": health_percentage,
            "healthy_components": healthy_checks,
            "total_components": total_checks,
            "last_check": max([hc.timestamp for hc in self.health_checks.values()]).isoformat() if self.health_checks else None
        }
    
    def get_component_health(self, component_id: str) -> Optional[HealthCheck]:
        """Get health status of a specific component"""
        return self.health_checks.get(component_id)


class PerformanceAnalyzer:
    """Analyzes performance trends and identifies optimization opportunities"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        self.analysis_history: List[Dict[str, Any]] = []
        self.optimization_recommendations: List[Dict[str, Any]] = []
    
    async def analyze_performance_trends(self) -> Dict[str, Any]:
        """Analyze performance trends across all metrics"""
        try:
            analysis_id = f"perf_analysis_{datetime.now().isoformat()}"
            
            analysis_results = {
                "analysis_id": analysis_id,
                "timestamp": datetime.now().isoformat(),
                "metric_trends": {},
                "performance_score": 0.0,
                "recommendations": [],
                "alerts": []
            }
            
            # Analyze each metric
            for metric_id in self.metrics_collector.metric_definitions.keys():
                trend_analysis = self._analyze_metric_trend(metric_id)
                analysis_results["metric_trends"][metric_id] = trend_analysis
            
            # Calculate overall performance score
            analysis_results["performance_score"] = self._calculate_performance_score(
                analysis_results["metric_trends"]
            )
            
            # Generate recommendations
            analysis_results["recommendations"] = self._generate_performance_recommendations(
                analysis_results["metric_trends"]
            )
            
            # Store analysis
            self.analysis_history.append(analysis_results)
            
            return analysis_results
            
        except Exception as e:
            logger.error(f"Error analyzing performance trends: {e}")
            return {"error": str(e)}
    
    def _analyze_metric_trend(self, metric_id: str) -> Dict[str, Any]:
        """Analyze trend for a specific metric"""
        try:
            # Get recent data (last 24 hours)
            recent_data = self.metrics_collector.get_metric_history(
                metric_id, timedelta(hours=24)
            )
            
            if len(recent_data) < 2:
                return {"trend": "insufficient_data", "confidence": 0.0}
            
            # Calculate trend
            values = [m.value for m in recent_data]
            timestamps = [m.timestamp.timestamp() for m in recent_data]
            
            # Simple linear trend calculation
            n = len(values)
            sum_x = sum(timestamps)
            sum_y = sum(values)
            sum_xy = sum(x * y for x, y in zip(timestamps, values))
            sum_x2 = sum(x * x for x in timestamps)
            
            # Calculate slope (trend direction)
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
            
            # Determine trend direction
            if abs(slope) < 0.001:
                trend = "stable"
            elif slope > 0:
                trend = "increasing"
            else:
                trend = "decreasing"
            
            # Calculate confidence based on data consistency
            mean_value = statistics.mean(values)
            std_dev = statistics.stdev(values) if len(values) > 1 else 0
            confidence = max(0.0, min(1.0, 1.0 - (std_dev / mean_value) if mean_value != 0 else 0))
            
            return {
                "trend": trend,
                "slope": slope,
                "confidence": confidence,
                "data_points": len(values),
                "mean": mean_value,
                "std_dev": std_dev,
                "latest_value": values[-1] if values else 0
            }
            
        except Exception as e:
            logger.error(f"Error analyzing trend for metric {metric_id}: {e}")
            return {"trend": "error", "error": str(e)}
    
    def _calculate_performance_score(self, metric_trends: Dict[str, Any]) -> float:
        """Calculate overall performance score"""
        if not metric_trends:
            return 0.0
        
        scores = []
        
        for metric_id, trend_data in metric_trends.items():
            if trend_data.get("trend") == "error":
                continue
            
            # Score based on trend and metric type
            metric_def = self.metrics_collector.metric_definitions.get(metric_id, {})
            metric_type = metric_def.get("type")
            
            base_score = 50.0  # Neutral score
            
            trend = trend_data.get("trend", "stable")
            confidence = trend_data.get("confidence", 0.5)
            
            # Adjust score based on metric type and trend
            if metric_type == MetricType.PERFORMANCE:
                if trend == "increasing":
                    base_score = 80.0  # Good for performance metrics
                elif trend == "decreasing":
                    base_score = 30.0  # Bad for performance metrics
            elif metric_type == MetricType.ERROR_RATE:
                if trend == "decreasing":
                    base_score = 80.0  # Good for error rate
                elif trend == "increasing":
                    base_score = 30.0  # Bad for error rate
            
            # Weight by confidence
            weighted_score = base_score * confidence + 50.0 * (1 - confidence)
            scores.append(weighted_score)
        
        return statistics.mean(scores) if scores else 50.0
    
    def _generate_performance_recommendations(self, metric_trends: Dict[str, Any]) -> List[str]:
        """Generate performance optimization recommendations"""
        recommendations = []
        
        for metric_id, trend_data in metric_trends.items():
            metric_def = self.metrics_collector.metric_definitions.get(metric_id, {})
            metric_name = metric_def.get("name", metric_id)
            trend = trend_data.get("trend", "stable")
            confidence = trend_data.get("confidence", 0.0)
            
            if confidence < 0.5:
                continue  # Skip low-confidence trends
            
            if trend == "decreasing" and metric_def.get("type") == MetricType.PERFORMANCE:
                recommendations.append(f"Performance degradation detected in {metric_name}. Consider optimization.")
            elif trend == "increasing" and metric_def.get("type") == MetricType.ERROR_RATE:
                recommendations.append(f"Error rate increasing for {metric_name}. Investigate root cause.")
            elif trend == "increasing" and metric_def.get("type") == MetricType.RESOURCE_UTILIZATION:
                recommendations.append(f"Resource utilization increasing for {metric_name}. Consider scaling.")
        
        if not recommendations:
            recommendations.append("System performance appears stable. Continue monitoring.")
        
        return recommendations


class ContinuousImprovement:
    """Implements continuous improvement based on monitoring data"""
    
    def __init__(self, control_interface: SupremeControlInterface):
        self.control_interface = control_interface
        self.improvement_actions: List[Dict[str, Any]] = []
        self.optimization_history: List[Dict[str, Any]] = []
        self.improvement_rules: Dict[str, Dict[str, Any]] = {}
    
    def add_improvement_rule(self, rule_id: str, condition: str, 
                           action: str, priority: int = 5):
        """Add an improvement rule"""
        self.improvement_rules[rule_id] = {
            "condition": condition,
            "action": action,
            "priority": priority,
            "created_at": datetime.now(),
            "applied_count": 0,
            "last_applied": None
        }
        
        logger.info(f"Added improvement rule: {rule_id}")
    
    async def apply_improvements(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Apply improvements based on analysis results"""
        try:
            improvement_id = f"improvement_{datetime.now().isoformat()}"
            
            applied_improvements = {
                "improvement_id": improvement_id,
                "timestamp": datetime.now().isoformat(),
                "applied_actions": [],
                "skipped_actions": [],
                "errors": []
            }
            
            # Check performance score and apply improvements if needed
            performance_score = analysis_results.get("performance_score", 50.0)
            
            if performance_score < 70:
                # Apply performance improvements
                perf_improvements = await self._apply_performance_improvements(analysis_results)
                applied_improvements["applied_actions"].extend(perf_improvements)
            
            # Check for specific metric issues
            metric_trends = analysis_results.get("metric_trends", {})
            for metric_id, trend_data in metric_trends.items():
                if trend_data.get("trend") == "decreasing" and trend_data.get("confidence", 0) > 0.7:
                    # Apply metric-specific improvements
                    metric_improvements = await self._apply_metric_improvements(metric_id, trend_data)
                    applied_improvements["applied_actions"].extend(metric_improvements)
            
            # Store improvement history
            self.optimization_history.append(applied_improvements)
            
            return applied_improvements
            
        except Exception as e:
            logger.error(f"Error applying improvements: {e}")
            return {"error": str(e)}
    
    async def _apply_performance_improvements(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Apply general performance improvements"""
        improvements = []
        
        try:
            # Example: Optimize resource allocation
            optimization_command = SupremeCommand(
                command_id="optimize_resources",
                command_type=CommandType.OPTIMIZE,
                operation="optimize_resource_allocation",
                parameters={"analysis_data": analysis_results}
            )
            
            result = await self.control_interface.execute_command(optimization_command)
            
            if result and result.status == "completed":
                improvements.append("Applied resource allocation optimization")
            else:
                improvements.append("Failed to apply resource optimization")
            
        except Exception as e:
            improvements.append(f"Error applying performance improvements: {e}")
        
        return improvements
    
    async def _apply_metric_improvements(self, metric_id: str, trend_data: Dict[str, Any]) -> List[str]:
        """Apply improvements for specific metrics"""
        improvements = []
        
        try:
            # Example: Scale resources if utilization is high
            if "utilization" in metric_id.lower():
                scaling_command = SupremeCommand(
                    command_id=f"scale_for_{metric_id}",
                    command_type=CommandType.SCALE,
                    operation="auto_scale_resources",
                    parameters={"metric_id": metric_id, "trend_data": trend_data}
                )
                
                result = await self.control_interface.execute_command(scaling_command)
                
                if result and result.status == "completed":
                    improvements.append(f"Applied auto-scaling for {metric_id}")
                else:
                    improvements.append(f"Failed to apply scaling for {metric_id}")
            
        except Exception as e:
            improvements.append(f"Error applying metric improvements for {metric_id}: {e}")
        
        return improvements
    
    def get_improvement_summary(self) -> Dict[str, Any]:
        """Get summary of improvement activities"""
        if not self.optimization_history:
            return {"message": "No improvement history available"}
        
        total_improvements = len(self.optimization_history)
        recent_improvements = [h for h in self.optimization_history 
                             if datetime.fromisoformat(h["timestamp"]) > datetime.now() - timedelta(days=7)]
        
        total_actions = sum(len(h.get("applied_actions", [])) for h in self.optimization_history)
        
        return {
            "total_improvement_cycles": total_improvements,
            "recent_improvement_cycles": len(recent_improvements),
            "total_actions_applied": total_actions,
            "improvement_rules": len(self.improvement_rules),
            "last_improvement": self.optimization_history[-1]["timestamp"] if self.optimization_history else None
        }


class SupremeMonitoringSystem:
    """Master monitoring and improvement system for all supreme capabilities"""
    
    def __init__(self, control_interface: SupremeControlInterface):
        self.control_interface = control_interface
        self.metrics_collector = MetricsCollector()
        self.alert_manager = AlertManager()
        self.health_monitor = HealthMonitor(control_interface)
        self.performance_analyzer = PerformanceAnalyzer(self.metrics_collector)
        self.continuous_improvement = ContinuousImprovement(control_interface)
        
        self.monitoring_status = MonitoringStatus.INACTIVE
        self.monitoring_task: Optional[asyncio.Task] = None
        self.monitoring_interval = 300.0  # 5 minutes
        
        self._setup_default_metrics()
        self._setup_default_alerts()
    
    def _setup_default_metrics(self):
        """Setup default metrics for monitoring"""
        # Performance metrics
        self.metrics_collector.register_metric(
            "response_time_avg", MetricType.PERFORMANCE, 
            "Average Response Time", "seconds", 60.0
        )
        self.metrics_collector.register_metric(
            "throughput", MetricType.PERFORMANCE, 
            "System Throughput", "requests/second", 60.0
        )
        
        # Reliability metrics
        self.metrics_collector.register_metric(
            "error_rate", MetricType.ERROR_RATE, 
            "Error Rate", "percentage", 60.0
        )
        self.metrics_collector.register_metric(
            "availability", MetricType.AVAILABILITY, 
            "System Availability", "percentage", 300.0
        )
        
        # Resource metrics
        self.metrics_collector.register_metric(
            "cpu_utilization", MetricType.RESOURCE_UTILIZATION, 
            "CPU Utilization", "percentage", 30.0
        )
        self.metrics_collector.register_metric(
            "memory_utilization", MetricType.RESOURCE_UTILIZATION, 
            "Memory Utilization", "percentage", 30.0
        )
        
        # User satisfaction
        self.metrics_collector.register_metric(
            "user_satisfaction", MetricType.USER_SATISFACTION, 
            "User Satisfaction Score", "score", 3600.0
        )
    
    def _setup_default_alerts(self):
        """Setup default alert rules"""
        # Performance alerts
        self.alert_manager.add_alert_rule(
            "high_response_time", "response_time_avg", 
            "greater_than", 2.0, AlertLevel.WARNING,
            "High response time detected"
        )
        
        # Error rate alerts
        self.alert_manager.add_alert_rule(
            "high_error_rate", "error_rate", 
            "greater_than", 5.0, AlertLevel.ERROR,
            "High error rate detected"
        )
        
        # Availability alerts
        self.alert_manager.add_alert_rule(
            "low_availability", "availability", 
            "less_than", 95.0, AlertLevel.CRITICAL,
            "Low system availability"
        )
        
        # Resource utilization alerts
        self.alert_manager.add_alert_rule(
            "high_cpu", "cpu_utilization", 
            "greater_than", 80.0, AlertLevel.WARNING,
            "High CPU utilization"
        )
        self.alert_manager.add_alert_rule(
            "high_memory", "memory_utilization", 
            "greater_than", 85.0, AlertLevel.WARNING,
            "High memory utilization"
        )
    
    async def start_monitoring(self):
        """Start the monitoring system"""
        try:
            if self.monitoring_status == MonitoringStatus.ACTIVE:
                logger.warning("Monitoring is already active")
                return
            
            self.monitoring_status = MonitoringStatus.ACTIVE
            
            # Start health monitoring
            await self.health_monitor.start_monitoring()
            
            # Start main monitoring loop
            self.monitoring_task = asyncio.create_task(self._monitoring_loop())
            
            logger.info("Supreme monitoring system started")
            
        except Exception as e:
            logger.error(f"Error starting monitoring system: {e}")
            self.monitoring_status = MonitoringStatus.ERROR
    
    async def stop_monitoring(self):
        """Stop the monitoring system"""
        try:
            self.monitoring_status = MonitoringStatus.INACTIVE
            
            # Stop health monitoring
            await self.health_monitor.stop_monitoring()
            
            # Cancel monitoring task
            if self.monitoring_task:
                self.monitoring_task.cancel()
                try:
                    await self.monitoring_task
                except asyncio.CancelledError:
                    pass
            
            logger.info("Supreme monitoring system stopped")
            
        except Exception as e:
            logger.error(f"Error stopping monitoring system: {e}")
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_status == MonitoringStatus.ACTIVE:
            try:
                # Collect metrics
                await self._collect_system_metrics()
                
                # Analyze performance trends
                analysis_results = await self.performance_analyzer.analyze_performance_trends()
                
                # Apply improvements if needed
                if analysis_results.get("performance_score", 100) < 80:
                    await self.continuous_improvement.apply_improvements(analysis_results)
                
                # Wait for next monitoring cycle
                await asyncio.sleep(self.monitoring_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(60.0)  # Wait before retrying
    
    async def _collect_system_metrics(self):
        """Collect metrics from all system components"""
        try:
            timestamp = datetime.now()
            
            # Collect performance metrics
            perf_command = SupremeCommand(
                command_id="collect_performance_metrics",
                command_type=CommandType.MONITOR,
                operation="get_performance_metrics",
                parameters={}
            )
            
            perf_result = await self.control_interface.execute_command(perf_command)
            
            if perf_result and perf_result.status == "completed":
                metrics_data = perf_result.result or {}
                
                # Record individual metrics
                for metric_id, value in metrics_data.items():
                    if isinstance(value, (int, float)):
                        metric = Metric(
                            metric_id=metric_id,
                            metric_type=MetricType.PERFORMANCE,
                            name=metric_id.replace("_", " ").title(),
                            value=float(value),
                            unit="units",
                            timestamp=timestamp,
                            source="system_monitor"
                        )
                        
                        self.metrics_collector.record_metric(metric)
                        self.alert_manager.check_alert_rules(metric)
            
            # Simulate some additional metrics
            import random
            
            # Response time metric
            response_time = random.uniform(0.1, 1.5)
            response_metric = Metric(
                metric_id="response_time_avg",
                metric_type=MetricType.PERFORMANCE,
                name="Average Response Time",
                value=response_time,
                unit="seconds",
                timestamp=timestamp,
                source="system_monitor"
            )
            self.metrics_collector.record_metric(response_metric)
            self.alert_manager.check_alert_rules(response_metric)
            
            # Error rate metric
            error_rate = random.uniform(0.1, 3.0)
            error_metric = Metric(
                metric_id="error_rate",
                metric_type=MetricType.ERROR_RATE,
                name="Error Rate",
                value=error_rate,
                unit="percentage",
                timestamp=timestamp,
                source="system_monitor"
            )
            self.metrics_collector.record_metric(error_metric)
            self.alert_manager.check_alert_rules(error_metric)
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
    
    def get_monitoring_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive monitoring dashboard data"""
        try:
            return {
                "monitoring_status": self.monitoring_status.value,
                "system_health": self.health_monitor.get_health_status(),
                "active_alerts": len(self.alert_manager.get_active_alerts()),
                "alert_summary": self.alert_manager.get_alert_summary(),
                "metrics_summary": self.metrics_collector.get_all_metrics_summary(),
                "improvement_summary": self.continuous_improvement.get_improvement_summary(),
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating monitoring dashboard: {e}")
            return {"error": str(e)}
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get high-level system status"""
        try:
            health_status = self.health_monitor.get_health_status()
            alert_summary = self.alert_manager.get_alert_summary()
            
            # Determine overall status
            health_score = health_status.get("health_percentage", 0)
            critical_alerts = alert_summary.get("critical_alerts", 0)
            error_alerts = alert_summary.get("error_alerts", 0)
            
            if critical_alerts > 0:
                overall_status = "critical"
            elif error_alerts > 0 or health_score < 70:
                overall_status = "degraded"
            elif health_score < 90:
                overall_status = "warning"
            else:
                overall_status = "healthy"
            
            return {
                "overall_status": overall_status,
                "health_percentage": health_score,
                "monitoring_active": self.monitoring_status == MonitoringStatus.ACTIVE,
                "active_alerts": alert_summary.get("active_alerts", 0),
                "critical_issues": critical_alerts,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {"overall_status": "unknown", "error": str(e)}
    
    async def run_manual_analysis(self) -> Dict[str, Any]:
        """Run manual performance analysis"""
        try:
            # Collect fresh metrics
            await self._collect_system_metrics()
            
            # Run analysis
            analysis_results = await self.performance_analyzer.analyze_performance_trends()
            
            # Apply improvements if needed
            improvement_results = await self.continuous_improvement.apply_improvements(analysis_results)
            
            return {
                "analysis": analysis_results,
                "improvements": improvement_results,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error running manual analysis: {e}")
            return {"error": str(e)}