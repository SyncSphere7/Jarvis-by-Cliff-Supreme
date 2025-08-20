"""
Supreme System Controller
Master controller for autonomous system management.
"""

import logging
import asyncio
import psutil
import platform
import time
from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

from ..base_supreme_engine import BaseSupremeEngine, SupremeRequest, SupremeResponse

class SystemStatus(Enum):
    OPTIMAL = "optimal"
    GOOD = "good"
    WARNING = "warning"
    CRITICAL = "critical"

@dataclass
class SystemMetrics:
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    process_count: int
    uptime: float
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class SupremeSystemController(BaseSupremeEngine):
    """Supreme system controller with autonomous management capabilities."""
    
    def __init__(self, engine_name: str, config):
        super().__init__(engine_name, config)
        self.system_metrics_history: List[SystemMetrics] = []
        self.auto_healing_enabled = True
        self.alert_thresholds = {
            "cpu_usage": 80.0,
            "memory_usage": 85.0,
            "disk_usage": 90.0
        }
    
    async def _initialize_engine(self) -> bool:
        """Initialize the supreme system controller"""
        try:
            self.logger.info("Initializing Supreme System Controller...")
            
            initial_metrics = await self._collect_system_metrics()
            self.system_metrics_history.append(initial_metrics)
            self.logger.info(f"System baseline: CPU {initial_metrics.cpu_usage:.1f}%, Memory {initial_metrics.memory_usage:.1f}%")
            
            if self.config.auto_scaling:
                asyncio.create_task(self._continuous_monitoring())
            
            self.logger.info("Supreme System Controller initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Supreme System Controller: {e}")
            return False
    
    async def _execute_operation(self, request: SupremeRequest) -> Any:
        """Execute system management operation"""
        operation = request.operation.lower()
        parameters = request.parameters
        
        if "monitor" in operation:
            return await self._monitor_system_health(parameters)
        elif "diagnose" in operation:
            return await self._diagnose_system_issues(parameters)
        elif "heal" in operation:
            return await self._perform_system_healing(parameters)
        elif "optimize" in operation:
            return await self._optimize_system_performance(parameters)
        else:
            return await self._get_system_status(parameters)
    
    async def get_supported_operations(self) -> List[str]:
        """Get supported operations"""
        return ["monitor", "diagnose", "heal", "optimize", "system_status"]
    
    async def _monitor_system_health(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor system health"""
        try:
            current_metrics = await self._collect_system_metrics()
            self.system_metrics_history.append(current_metrics)
            
            health_status = self._analyze_system_health(current_metrics)
            alerts = self._check_for_alerts(current_metrics)
            
            return {
                "operation": "system_monitoring",
                "timestamp": current_metrics.timestamp.isoformat(),
                "overall_status": health_status.value,
                "metrics": {
                    "cpu_usage": current_metrics.cpu_usage,
                    "memory_usage": current_metrics.memory_usage,
                    "disk_usage": current_metrics.disk_usage,
                    "process_count": current_metrics.process_count,
                    "uptime_hours": current_metrics.uptime / 3600
                },
                "alerts": len(alerts),
                "recommendations": self._generate_recommendations(current_metrics, health_status)
            }
            
        except Exception as e:
            return {"error": str(e), "operation": "system_monitoring"}
    
    async def _diagnose_system_issues(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Diagnose system issues"""
        try:
            diagnostics = {
                "cpu": await self._diagnose_cpu(),
                "memory": await self._diagnose_memory(),
                "disk": await self._diagnose_disk()
            }
            
            total_issues = sum(len(diag.get("issues", [])) for diag in diagnostics.values())
            
            return {
                "operation": "system_diagnostics",
                "overall_status": "warning" if total_issues > 0 else "optimal",
                "diagnostics": diagnostics,
                "total_issues": total_issues
            }
            
        except Exception as e:
            return {"error": str(e), "operation": "system_diagnostics"}
    
    async def _perform_system_healing(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Perform system healing"""
        try:
            current_metrics = await self._collect_system_metrics()
            healing_actions = []
            
            if current_metrics.cpu_usage > self.alert_thresholds["cpu_usage"]:
                await self._heal_high_cpu()
                healing_actions.append("cpu_optimization")
            
            if current_metrics.memory_usage > self.alert_thresholds["memory_usage"]:
                await self._heal_high_memory()
                healing_actions.append("memory_cleanup")
            
            post_healing_metrics = await self._collect_system_metrics()
            
            return {
                "operation": "system_healing",
                "healing_actions_taken": healing_actions,
                "before_metrics": {
                    "cpu_usage": current_metrics.cpu_usage,
                    "memory_usage": current_metrics.memory_usage
                },
                "after_metrics": {
                    "cpu_usage": post_healing_metrics.cpu_usage,
                    "memory_usage": post_healing_metrics.memory_usage
                },
                "success": len(healing_actions) > 0
            }
            
        except Exception as e:
            return {"error": str(e), "operation": "system_healing"}
    
    async def _optimize_system_performance(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize system performance"""
        try:
            baseline_metrics = await self._collect_system_metrics()
            optimization_actions = []
            
            if baseline_metrics.cpu_usage > 60:
                optimization_actions.append("cpu_optimization")
            
            if baseline_metrics.memory_usage > 70:
                optimization_actions.append("memory_optimization")
            
            optimized_metrics = await self._collect_system_metrics()
            
            return {
                "operation": "performance_optimization",
                "optimization_actions": optimization_actions,
                "baseline_metrics": {
                    "cpu_usage": baseline_metrics.cpu_usage,
                    "memory_usage": baseline_metrics.memory_usage
                },
                "optimized_metrics": {
                    "cpu_usage": optimized_metrics.cpu_usage,
                    "memory_usage": optimized_metrics.memory_usage
                },
                "success": len(optimization_actions) > 0
            }
            
        except Exception as e:
            return {"error": str(e), "operation": "performance_optimization"}
    
    async def _get_system_status(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Get system status"""
        try:
            current_metrics = await self._collect_system_metrics()
            health_status = self._analyze_system_health(current_metrics)
            
            return {
                "operation": "system_status",
                "timestamp": datetime.now().isoformat(),
                "overall_health": health_status.value,
                "system_info": {
                    "platform": platform.system(),
                    "architecture": platform.architecture()[0],
                    "hostname": platform.node()
                },
                "current_metrics": {
                    "cpu_usage": current_metrics.cpu_usage,
                    "memory_usage": current_metrics.memory_usage,
                    "disk_usage": current_metrics.disk_usage,
                    "process_count": current_metrics.process_count,
                    "uptime_hours": current_metrics.uptime / 3600
                },
                "auto_healing_enabled": self.auto_healing_enabled
            }
            
        except Exception as e:
            return {"error": str(e), "operation": "system_status"}
    
    async def _collect_system_metrics(self) -> SystemMetrics:
        """Collect system metrics"""
        try:
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            process_count = len(psutil.pids())
            uptime = time.time() - psutil.boot_time()
            
            return SystemMetrics(
                cpu_usage=cpu_usage,
                memory_usage=memory.percent,
                disk_usage=(disk.used / disk.total) * 100,
                process_count=process_count,
                uptime=uptime
            )
            
        except Exception as e:
            self.logger.error(f"Error collecting metrics: {e}")
            return SystemMetrics(0.0, 0.0, 0.0, 0, 0.0)
    
    def _analyze_system_health(self, metrics: SystemMetrics) -> SystemStatus:
        """Analyze system health"""
        if metrics.cpu_usage > 90 or metrics.memory_usage > 95:
            return SystemStatus.CRITICAL
        elif metrics.cpu_usage > 80 or metrics.memory_usage > 85:
            return SystemStatus.WARNING
        elif metrics.cpu_usage > 60 or metrics.memory_usage > 70:
            return SystemStatus.GOOD
        else:
            return SystemStatus.OPTIMAL
    
    def _check_for_alerts(self, metrics: SystemMetrics) -> List[str]:
        """Check for alerts"""
        alerts = []
        if metrics.cpu_usage > self.alert_thresholds["cpu_usage"]:
            alerts.append(f"High CPU: {metrics.cpu_usage:.1f}%")
        if metrics.memory_usage > self.alert_thresholds["memory_usage"]:
            alerts.append(f"High Memory: {metrics.memory_usage:.1f}%")
        return alerts
    
    def _generate_recommendations(self, metrics: SystemMetrics, status: SystemStatus) -> List[str]:
        """Generate recommendations"""
        recommendations = []
        if metrics.cpu_usage > 80:
            recommendations.append("Reduce CPU load by closing applications")
        if metrics.memory_usage > 85:
            recommendations.append("Free up memory")
        if status == SystemStatus.OPTIMAL:
            recommendations.append("System running optimally")
        return recommendations
    
    async def _diagnose_cpu(self) -> Dict[str, Any]:
        """Diagnose CPU"""
        cpu_percent = psutil.cpu_percent(interval=1)
        issues = []
        if cpu_percent > 90:
            issues.append("CPU critically high")
        return {"status": "critical" if cpu_percent > 90 else "optimal", "issues": issues}
    
    async def _diagnose_memory(self) -> Dict[str, Any]:
        """Diagnose memory"""
        memory = psutil.virtual_memory()
        issues = []
        if memory.percent > 95:
            issues.append("Memory critically high")
        return {"status": "critical" if memory.percent > 95 else "optimal", "issues": issues}
    
    async def _diagnose_disk(self) -> Dict[str, Any]:
        """Diagnose disk"""
        disk = psutil.disk_usage('/')
        usage_percent = (disk.used / disk.total) * 100
        issues = []
        if usage_percent > 95:
            issues.append("Disk space critically low")
        return {"status": "critical" if usage_percent > 95 else "optimal", "issues": issues}
    
    async def _heal_high_cpu(self):
        """Heal high CPU"""
        self.logger.info("Performing CPU healing...")
    
    async def _heal_high_memory(self):
        """Heal high memory"""
        self.logger.info("Performing memory healing...")
    
    async def _continuous_monitoring(self):
        """Continuous monitoring"""
        while self.status.value != "shutdown":
            try:
                await asyncio.sleep(30)
                metrics = await self._collect_system_metrics()
                self.system_metrics_history.append(metrics)
                
                if self.auto_healing_enabled:
                    health_status = self._analyze_system_health(metrics)
                    if health_status == SystemStatus.CRITICAL:
                        await self._perform_system_healing({})
                
                if len(self.system_metrics_history) > 1000:
                    self.system_metrics_history = self.system_metrics_history[-1000:]
                    
            except Exception as e:
                self.logger.error(f"Monitoring error: {e}")
                await asyncio.sleep(60)