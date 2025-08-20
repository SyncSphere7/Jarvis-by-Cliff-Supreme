"""
System Monitor for Supreme Jarvis
Tracks system performance, resource usage, and health metrics.
"""

import psutil
import time
import asyncio
from datetime import datetime
from typing import Dict, Any, List
from dataclasses import dataclass, asdict
from collections import deque
import json
import os

from core.utils.log import logger


@dataclass
class SystemMetrics:
    """System performance metrics"""
    timestamp: float
    cpu_percent: float
    memory_percent: float
    disk_usage_percent: float
    network_bytes_sent: int
    network_bytes_recv: int
    uptime_seconds: float
    load_average: List[float]  # 1, 5, 15 minute load averages


@dataclass
class EngineMetrics:
    """Engine-specific metrics"""
    engine_name: str
    operations_per_second: float
    success_rate: float
    average_response_time: float
    resource_utilization: float
    learning_progress: float
    capability_score: float
    last_updated: str


class SystemMonitor:
    """Monitors system health and performance metrics"""
    
    def __init__(self, metrics_history_size: int = 1000):
        self.metrics_history = deque(maxlen=metrics_history_size)
        self.engine_metrics = {}
        self.start_time = time.time()
        self.last_network_stats = None
        self.is_monitoring = False
        self.monitoring_task = None
        
        # Create metrics directory
        self.metrics_dir = "data/metrics"
        os.makedirs(self.metrics_dir, exist_ok=True)
        
        logger.info("System Monitor initialized")
    
    async def start_monitoring(self, interval: int = 60):
        """Start continuous system monitoring"""
        if self.is_monitoring:
            logger.warning("System monitoring already running")
            return
            
        self.is_monitoring = True
        self.monitoring_task = asyncio.create_task(self._monitor_loop(interval))
        logger.info(f"System monitoring started with {interval}s interval")
    
    async def stop_monitoring(self):
        """Stop continuous system monitoring"""
        if not self.is_monitoring:
            logger.warning("System monitoring not running")
            return
            
        self.is_monitoring = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        logger.info("System monitoring stopped")
    
    async def _monitor_loop(self, interval: int):
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                metrics = self._collect_system_metrics()
                self.metrics_history.append(metrics)
                
                # Log metrics periodically
                if len(self.metrics_history) % 10 == 0:
                    self._log_system_health(metrics)
                
                # Save metrics to file periodically
                if len(self.metrics_history) % 60 == 0:
                    self._save_metrics_to_file()
                
                await asyncio.sleep(interval)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(interval)
    
    def _collect_system_metrics(self) -> SystemMetrics:
        """Collect current system metrics"""
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memory usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        # Disk usage
        disk = psutil.disk_usage('/')
        disk_usage_percent = (disk.used / disk.total) * 100
        
        # Network stats
        network = psutil.net_io_counters()
        if self.last_network_stats is None:
            self.last_network_stats = network
        
        # Load average (Unix only)
        try:
            load_average = os.getloadavg()
        except AttributeError:
            # Windows doesn't have load average
            load_average = [0.0, 0.0, 0.0]
        
        metrics = SystemMetrics(
            timestamp=time.time(),
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            disk_usage_percent=disk_usage_percent,
            network_bytes_sent=network.bytes_sent,
            network_bytes_recv=network.bytes_recv,
            uptime_seconds=time.time() - self.start_time,
            load_average=list(load_average)
        )
        
        self.last_network_stats = network
        return metrics
    
    def _log_system_health(self, metrics: SystemMetrics):
        """Log system health metrics"""
        logger.info("System Health Metrics", **asdict(metrics))
        
        # Check for critical thresholds
        if metrics.cpu_percent > 90:
            logger.warning(f"High CPU usage: {metrics.cpu_percent:.1f}%")
        
        if metrics.memory_percent > 90:
            logger.warning(f"High memory usage: {metrics.memory_percent:.1f}%")
        
        if metrics.disk_usage_percent > 95:
            logger.warning(f"High disk usage: {metrics.disk_usage_percent:.1f}%")
    
    def _save_metrics_to_file(self):
        """Save metrics to file for analysis"""
        try:
            filename = f"system_metrics_{datetime.now().strftime('%Y%m%d')}.json"
            filepath = os.path.join(self.metrics_dir, filename)
            
            # Convert metrics to serializable format
            metrics_list = []
            for metrics in self.metrics_history:
                metrics_dict = asdict(metrics)
                metrics_dict['timestamp'] = datetime.fromtimestamp(metrics_dict['timestamp']).isoformat()
                metrics_list.append(metrics_dict)
            
            with open(filepath, 'w') as f:
                json.dump(metrics_list, f, indent=2)
                
            logger.info(f"Saved {len(metrics_list)} metrics to {filepath}")
        except Exception as e:
            logger.error(f"Error saving metrics to file: {e}")
    
    def update_engine_metrics(self, engine_name: str, metrics: Dict[str, Any]):
        """Update metrics for a specific engine"""
        self.engine_metrics[engine_name] = EngineMetrics(
            engine_name=engine_name,
            operations_per_second=metrics.get('operations_per_second', 0.0),
            success_rate=metrics.get('success_rate', 100.0),
            average_response_time=metrics.get('average_response_time', 0.0),
            resource_utilization=metrics.get('resource_utilization', 0.0),
            learning_progress=metrics.get('learning_progress', 0.0),
            capability_score=metrics.get('capability_score', 0.0),
            last_updated=datetime.now().isoformat()
        )
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status"""
        if not self.metrics_history:
            return {"status": "unknown", "message": "No metrics collected yet"}
        
        latest_metrics = self.metrics_history[-1]
        
        # Determine overall health
        health_status = "healthy"
        if (latest_metrics.cpu_percent > 90 or 
            latest_metrics.memory_percent > 90 or 
            latest_metrics.disk_usage_percent > 95):
            health_status = "degraded"
        elif (latest_metrics.cpu_percent > 75 or 
              latest_metrics.memory_percent > 75 or 
              latest_metrics.disk_usage_percent > 85):
            health_status = "warning"
        
        return {
            "status": health_status,
            "timestamp": datetime.fromtimestamp(latest_metrics.timestamp).isoformat(),
            "system_metrics": asdict(latest_metrics),
            "engine_metrics": {name: asdict(metrics) for name, metrics in self.engine_metrics.items()},
            "uptime": str(datetime.now() - datetime.fromtimestamp(self.start_time))
        }
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate a performance report"""
        if not self.metrics_history:
            return {"message": "No metrics available"}
        
        # Calculate averages
        cpu_avg = sum(m.cpu_percent for m in self.metrics_history) / len(self.metrics_history)
        memory_avg = sum(m.memory_percent for m in self.metrics_history) / len(self.metrics_history)
        disk_avg = sum(m.disk_usage_percent for m in self.metrics_history) / len(self.metrics_history)
        
        # Get latest metrics
        latest = self.metrics_history[-1]
        
        return {
            "report_generated": datetime.now().isoformat(),
            "period_seconds": time.time() - self.metrics_history[0].timestamp,
            "metrics_count": len(self.metrics_history),
            "averages": {
                "cpu_percent": round(cpu_avg, 2),
                "memory_percent": round(memory_avg, 2),
                "disk_usage_percent": round(disk_avg, 2)
            },
            "latest": {
                "cpu_percent": latest.cpu_percent,
                "memory_percent": latest.memory_percent,
                "disk_usage_percent": latest.disk_usage_percent,
                "load_average": latest.load_average
            },
            "engine_performance": {name: asdict(metrics) for name, metrics in self.engine_metrics.items()}
        }


# Global system monitor instance
system_monitor = SystemMonitor()


def get_system_monitor() -> SystemMonitor:
    """Get the global system monitor instance"""
    return system_monitor