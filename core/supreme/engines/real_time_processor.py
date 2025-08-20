"""
Supreme Real-Time Processor
Advanced real-time data processing and streaming analytics.
"""

import logging
import asyncio
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
import os
import hashlib
from collections import defaultdict, deque
import statistics
import math

from ..base_supreme_engine import BaseSupremeEngine, SupremeRequest, SupremeResponse

class StreamingMode(Enum):
    CONTINUOUS = "continuous"
    BATCH = "batch"
    WINDOWED = "windowed"
    EVENT_DRIVEN = "event_driven"

class AggregationType(Enum):
    SUM = "sum"
    AVERAGE = "average"
    COUNT = "count"
    MIN = "min"
    MAX = "max"
    MEDIAN = "median"
    PERCENTILE = "percentile"
    STANDARD_DEVIATION = "std_dev"

@dataclass
class StreamConfig:
    """Configuration for a data stream"""
    stream_id: str
    stream_name: str
    source_type: str
    processing_mode: StreamingMode
    window_size: Optional[int] = None
    aggregations: List[AggregationType] = None
    alert_thresholds: Dict[str, float] = None
    
    def __post_init__(self):
        if self.aggregations is None:
            self.aggregations = [AggregationType.AVERAGE]
        if self.alert_thresholds is None:
            self.alert_thresholds = {}

@dataclass
class StreamingWindow:
    """Represents a time window for streaming data"""
    window_id: str
    stream_id: str
    start_time: datetime
    end_time: datetime
    data_points: List[Dict[str, Any]]
    aggregated_results: Dict[str, float] = None
    
    def __post_init__(self):
        if self.aggregated_results is None:
            self.aggregated_results = {}

@dataclass
class StreamAlert:
    """Represents an alert from streaming data"""
    alert_id: str
    stream_id: str
    alert_type: str
    message: str
    severity: str
    value: float
    threshold: float
    timestamp: datetime
    resolved: bool = False

class SupremeRealTimeProcessor(BaseSupremeEngine):
    """
    Supreme real-time processor for streaming data analysis.
    Provides advanced real-time analytics, windowing, and alerting.
    """
    
    def __init__(self, engine_name: str, config):
        super().__init__(engine_name, config)
        
        # Streaming storage
        self.stream_configs: Dict[str, StreamConfig] = {}
        self.active_windows: Dict[str, List[StreamingWindow]] = defaultdict(list)
        self.stream_buffers: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.stream_alerts: List[StreamAlert] = []
        
        # Processing capabilities
        self.processing_capabilities = {
            "create_stream": self._create_data_stream,
            "process_stream": self._process_streaming_data,
            "aggregate_window": self._aggregate_window_data,
            "detect_anomalies": self._detect_streaming_anomalies,
            "manage_alerts": self._manage_stream_alerts,
            "get_stream_stats": self._get_stream_statistics
        }
        
        # Built-in processors
        self.stream_processors = self._initialize_stream_processors()
        
        # Data persistence
        self.data_dir = "data/streaming"
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Processing control
        self.processor_running = False
    
    async def _initialize_engine(self) -> bool:
        """Initialize the real-time processor"""
        try:
            self.logger.info("Initializing Supreme Real-Time Processor...")
            
            # Load existing stream configurations
            await self._load_stream_data()
            
            # Start stream processor
            if self.config.auto_scaling:
                asyncio.create_task(self._run_stream_processor())
                self.processor_running = True
            
            self.logger.info(f"Real-Time Processor initialized with {len(self.stream_configs)} streams")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Real-Time Processor: {e}")
            return False
    
    async def _execute_operation(self, request: SupremeRequest) -> Any:
        """Execute real-time processing operation"""
        operation = request.operation.lower()
        parameters = request.parameters
        
        # Route to appropriate processing capability
        if "create" in operation and "stream" in operation:
            return await self._create_data_stream(parameters)
        elif "process" in operation:
            return await self._process_streaming_data(parameters)
        elif "aggregate" in operation:
            return await self._aggregate_window_data(parameters)
        elif "anomal" in operation:
            return await self._detect_streaming_anomalies(parameters)
        elif "alert" in operation:
            return await self._manage_stream_alerts(parameters)
        elif "stats" in operation:
            return await self._get_stream_statistics(parameters)
        else:
            return await self._get_processor_status(parameters)
    
    async def get_supported_operations(self) -> List[str]:
        """Get supported real-time processing operations"""
        return [
            "create_stream", "process_stream", "aggregate_window", "detect_anomalies",
            "manage_alerts", "get_stream_stats", "processor_status"
        ]
    
    async def _create_data_stream(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new data stream configuration"""
        try:
            stream_name = parameters.get("stream_name")
            source_type = parameters.get("source_type", "generic")
            processing_mode = parameters.get("processing_mode", "continuous")
            window_size = parameters.get("window_size")
            aggregations = parameters.get("aggregations", ["average"])
            alert_thresholds = parameters.get("alert_thresholds", {})
            
            if not stream_name:
                return {"error": "stream_name is required", "operation": "create_stream"}
            
            # Generate stream ID
            stream_id = self._generate_stream_id(stream_name)
            
            # Create stream configuration
            stream_config = StreamConfig(
                stream_id=stream_id,
                stream_name=stream_name,
                source_type=source_type,
                processing_mode=StreamingMode(processing_mode),
                window_size=window_size,
                aggregations=[AggregationType(agg) for agg in aggregations],
                alert_thresholds=alert_thresholds
            )
            
            # Store configuration
            self.stream_configs[stream_id] = stream_config
            
            # Initialize stream buffer
            self.stream_buffers[stream_id] = deque(maxlen=10000)
            
            result = {
                "operation": "create_stream",
                "stream_id": stream_id,
                "stream_name": stream_name,
                "processing_mode": processing_mode,
                "window_size": window_size,
                "aggregations": aggregations,
                "alert_thresholds": alert_thresholds
            }
            
            # Save stream data
            await self._save_stream_data()
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error creating stream: {e}")
            return {"error": str(e), "operation": "create_stream"}
    
    async def _process_streaming_data(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming streaming data"""
        try:
            stream_id = parameters.get("stream_id")
            data_points = parameters.get("data_points", [])
            
            if not stream_id or not data_points:
                return {"error": "stream_id and data_points are required", "operation": "process_stream"}
            
            if stream_id not in self.stream_configs:
                return {"error": f"Stream {stream_id} not found", "operation": "process_stream"}
            
            stream_config = self.stream_configs[stream_id]
            processed_count = 0
            alerts_generated = []
            
            # Process each data point
            for data_point in data_points:
                # Add timestamp if not present
                if "timestamp" not in data_point:
                    data_point["timestamp"] = datetime.now().isoformat()
                
                # Add to stream buffer
                self.stream_buffers[stream_id].append(data_point)
                processed_count += 1
                
                # Check for alerts
                alert = await self._check_stream_alerts(stream_id, data_point, stream_config)
                if alert:
                    alerts_generated.append(alert)
                
                # Process based on mode
                if stream_config.processing_mode == StreamingMode.WINDOWED:
                    await self._process_windowed_data(stream_id, data_point, stream_config)
                elif stream_config.processing_mode == StreamingMode.BATCH:
                    await self._process_batch_data(stream_id, data_point, stream_config)
            
            # Calculate current statistics
            current_stats = await self._calculate_current_stream_stats(stream_id)
            
            result = {
                "operation": "process_stream",
                "stream_id": stream_id,
                "processed_count": processed_count,
                "alerts_generated": len(alerts_generated),
                "current_stats": current_stats,
                "alerts": alerts_generated,
                "buffer_size": len(self.stream_buffers[stream_id])
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing streaming data: {e}")
            return {"error": str(e), "operation": "process_stream"}
    
    async def _aggregate_window_data(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregate data within time windows"""
        try:
            stream_id = parameters.get("stream_id")
            window_size = parameters.get("window_size", 60)  # seconds
            aggregation_types = parameters.get("aggregations", ["average", "count"])
            
            if not stream_id:
                return {"error": "stream_id is required", "operation": "aggregate_window"}
            
            if stream_id not in self.stream_buffers:
                return {"error": f"Stream {stream_id} not found", "operation": "aggregate_window"}
            
            # Get recent data points
            now = datetime.now()
            window_start = now - timedelta(seconds=window_size)
            
            # Filter data points in window
            window_data = []
            for data_point in self.stream_buffers[stream_id]:
                point_time = datetime.fromisoformat(data_point["timestamp"])
                if point_time >= window_start:
                    window_data.append(data_point)
            
            if not window_data:
                return {
                    "operation": "aggregate_window",
                    "stream_id": stream_id,
                    "window_size": window_size,
                    "data_points": 0,
                    "aggregations": {}
                }
            
            # Perform aggregations
            aggregations = {}
            values = [float(dp.get("value", 0)) for dp in window_data if "value" in dp]
            
            if values:
                for agg_type in aggregation_types:
                    if agg_type == "sum":
                        aggregations[agg_type] = sum(values)
                    elif agg_type == "average":
                        aggregations[agg_type] = statistics.mean(values)
                    elif agg_type == "count":
                        aggregations[agg_type] = len(values)
                    elif agg_type == "min":
                        aggregations[agg_type] = min(values)
                    elif agg_type == "max":
                        aggregations[agg_type] = max(values)
                    elif agg_type == "median":
                        aggregations[agg_type] = statistics.median(values)
                    elif agg_type == "std_dev":
                        aggregations[agg_type] = statistics.stdev(values) if len(values) > 1 else 0
            
            # Create window object
            window = StreamingWindow(
                window_id=self._generate_window_id(stream_id),
                stream_id=stream_id,
                start_time=window_start,
                end_time=now,
                data_points=window_data,
                aggregated_results=aggregations
            )
            
            # Store window
            self.active_windows[stream_id].append(window)
            
            # Limit window history
            if len(self.active_windows[stream_id]) > 100:
                self.active_windows[stream_id] = self.active_windows[stream_id][-100:]
            
            result = {
                "operation": "aggregate_window",
                "stream_id": stream_id,
                "window_id": window.window_id,
                "window_size": window_size,
                "data_points": len(window_data),
                "aggregations": aggregations,
                "window_start": window_start.isoformat(),
                "window_end": now.isoformat()
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error aggregating window data: {e}")
            return {"error": str(e), "operation": "aggregate_window"}
    
    async def _detect_streaming_anomalies(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Detect anomalies in streaming data"""
        try:
            stream_id = parameters.get("stream_id")
            detection_method = parameters.get("method", "statistical")
            sensitivity = parameters.get("sensitivity", 2.0)  # Standard deviations
            window_size = parameters.get("window_size", 100)  # Number of points
            
            if not stream_id:
                return {"error": "stream_id is required", "operation": "detect_anomalies"}
            
            if stream_id not in self.stream_buffers:
                return {"error": f"Stream {stream_id} not found", "operation": "detect_anomalies"}
            
            # Get recent data points
            recent_data = list(self.stream_buffers[stream_id])[-window_size:]
            
            if len(recent_data) < 10:
                return {
                    "operation": "detect_anomalies",
                    "stream_id": stream_id,
                    "anomalies": [],
                    "message": "Insufficient data for anomaly detection"
                }
            
            # Extract values
            values = [float(dp.get("value", 0)) for dp in recent_data if "value" in dp]
            
            if not values:
                return {
                    "operation": "detect_anomalies",
                    "stream_id": stream_id,
                    "anomalies": [],
                    "message": "No numeric values found"
                }
            
            # Detect anomalies based on method
            anomalies = []
            
            if detection_method == "statistical":
                anomalies = await self._detect_statistical_anomalies(values, recent_data, sensitivity)
            elif detection_method == "moving_average":
                anomalies = await self._detect_moving_average_anomalies(values, recent_data, sensitivity)
            elif detection_method == "percentile":
                anomalies = await self._detect_percentile_anomalies(values, recent_data, sensitivity)
            
            result = {
                "operation": "detect_anomalies",
                "stream_id": stream_id,
                "detection_method": detection_method,
                "sensitivity": sensitivity,
                "window_size": len(recent_data),
                "anomalies_detected": len(anomalies),
                "anomalies": anomalies
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error detecting anomalies: {e}")
            return {"error": str(e), "operation": "detect_anomalies"}
    
    async def _manage_stream_alerts(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Manage stream alerts and notifications"""
        try:
            action = parameters.get("action", "list")  # list, create, resolve, delete
            stream_id = parameters.get("stream_id")
            alert_id = parameters.get("alert_id")
            
            if action == "list":
                # List alerts
                filtered_alerts = []
                for alert in self.stream_alerts:
                    if not stream_id or alert.stream_id == stream_id:
                        filtered_alerts.append({
                            "alert_id": alert.alert_id,
                            "stream_id": alert.stream_id,
                            "alert_type": alert.alert_type,
                            "message": alert.message,
                            "severity": alert.severity,
                            "value": alert.value,
                            "threshold": alert.threshold,
                            "timestamp": alert.timestamp.isoformat(),
                            "resolved": alert.resolved
                        })
                
                return {
                    "operation": "manage_alerts",
                    "action": "list",
                    "total_alerts": len(filtered_alerts),
                    "unresolved_alerts": len([a for a in filtered_alerts if not a["resolved"]]),
                    "alerts": filtered_alerts[-50:]  # Last 50 alerts
                }
            
            elif action == "resolve":
                # Resolve alert
                if not alert_id:
                    return {"error": "alert_id is required for resolve action", "operation": "manage_alerts"}
                
                alert = next((a for a in self.stream_alerts if a.alert_id == alert_id), None)
                if not alert:
                    return {"error": f"Alert {alert_id} not found", "operation": "manage_alerts"}
                
                alert.resolved = True
                
                return {
                    "operation": "manage_alerts",
                    "action": "resolve",
                    "alert_id": alert_id,
                    "resolved": True
                }
            
            else:
                return {"error": f"Unknown action: {action}", "operation": "manage_alerts"}
                
        except Exception as e:
            self.logger.error(f"Error managing alerts: {e}")
            return {"error": str(e), "operation": "manage_alerts"}
    
    async def _get_stream_statistics(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Get comprehensive stream statistics"""
        try:
            stream_id = parameters.get("stream_id")
            time_range = parameters.get("time_range", "1h")
            
            if stream_id and stream_id not in self.stream_buffers:
                return {"error": f"Stream {stream_id} not found", "operation": "get_stream_stats"}
            
            # Calculate time range
            now = datetime.now()
            if time_range == "5m":
                start_time = now - timedelta(minutes=5)
            elif time_range == "1h":
                start_time = now - timedelta(hours=1)
            elif time_range == "24h":
                start_time = now - timedelta(days=1)
            else:
                start_time = now - timedelta(hours=1)
            
            if stream_id:
                # Statistics for specific stream
                stream_data = list(self.stream_buffers[stream_id])
                
                # Filter by time range
                filtered_data = []
                for dp in stream_data:
                    point_time = datetime.fromisoformat(dp["timestamp"])
                    if point_time >= start_time:
                        filtered_data.append(dp)
                
                values = [float(dp.get("value", 0)) for dp in filtered_data if "value" in dp]
                
                stats = {
                    "stream_id": stream_id,
                    "data_points": len(filtered_data),
                    "time_range": time_range,
                    "statistics": {}
                }
                
                if values:
                    stats["statistics"] = {
                        "count": len(values),
                        "sum": sum(values),
                        "average": statistics.mean(values),
                        "min": min(values),
                        "max": max(values),
                        "median": statistics.median(values),
                        "std_dev": statistics.stdev(values) if len(values) > 1 else 0
                    }
                
                return {
                    "operation": "get_stream_stats",
                    "stream_statistics": stats
                }
            
            else:
                # Overall statistics
                total_streams = len(self.stream_configs)
                active_streams = len([s for s in self.stream_buffers.keys() if len(self.stream_buffers[s]) > 0])
                total_alerts = len(self.stream_alerts)
                unresolved_alerts = len([a for a in self.stream_alerts if not a.resolved])
                
                return {
                    "operation": "get_stream_stats",
                    "total_streams": total_streams,
                    "active_streams": active_streams,
                    "total_alerts": total_alerts,
                    "unresolved_alerts": unresolved_alerts,
                    "processor_running": self.processor_running,
                    "streams": {
                        sid: {
                            "name": config.stream_name,
                            "mode": config.processing_mode.value,
                            "buffer_size": len(self.stream_buffers[sid]),
                            "window_count": len(self.active_windows[sid])
                        }
                        for sid, config in self.stream_configs.items()
                    }
                }
                
        except Exception as e:
            self.logger.error(f"Error getting stream statistics: {e}")
            return {"error": str(e), "operation": "get_stream_stats"} 
   
    # Helper methods for real-time processing
    
    def _initialize_stream_processors(self) -> Dict[str, Callable]:
        """Initialize built-in stream processors"""
        return {
            "moving_average": self._calculate_moving_average,
            "exponential_smoothing": self._calculate_exponential_smoothing,
            "trend_detection": self._detect_trend,
            "spike_detection": self._detect_spikes,
            "pattern_matching": self._match_patterns
        }
    
    async def _load_stream_data(self):
        """Load existing stream configurations"""
        try:
            streams_file = os.path.join(self.data_dir, "streams.json")
            if os.path.exists(streams_file):
                with open(streams_file, 'r') as f:
                    streams_data = json.load(f)
                    for stream_id, stream_data in streams_data.items():
                        config = StreamConfig(
                            stream_id=stream_id,
                            stream_name=stream_data['stream_name'],
                            source_type=stream_data['source_type'],
                            processing_mode=StreamingMode(stream_data['processing_mode']),
                            window_size=stream_data['window_size'],
                            aggregations=[AggregationType(agg) for agg in stream_data['aggregations']],
                            alert_thresholds=stream_data['alert_thresholds']
                        )
                        self.stream_configs[stream_id] = config
                        
        except Exception as e:
            self.logger.warning(f"Could not load stream data: {e}")
    
    async def _save_stream_data(self):
        """Save stream configurations"""
        try:
            streams_data = {}
            for stream_id, config in self.stream_configs.items():
                streams_data[stream_id] = {
                    'stream_name': config.stream_name,
                    'source_type': config.source_type,
                    'processing_mode': config.processing_mode.value,
                    'window_size': config.window_size,
                    'aggregations': [agg.value for agg in config.aggregations],
                    'alert_thresholds': config.alert_thresholds
                }
            
            streams_file = os.path.join(self.data_dir, "streams.json")
            with open(streams_file, 'w') as f:
                json.dump(streams_data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Could not save stream data: {e}")
    
    def _generate_stream_id(self, stream_name: str) -> str:
        """Generate unique stream ID"""
        timestamp = datetime.now().isoformat()
        return hashlib.md5(f"{stream_name}_{timestamp}".encode()).hexdigest()[:16]
    
    def _generate_window_id(self, stream_id: str) -> str:
        """Generate unique window ID"""
        timestamp = datetime.now().isoformat()
        return hashlib.md5(f"window_{stream_id}_{timestamp}".encode()).hexdigest()[:16]
    
    def _generate_alert_id(self) -> str:
        """Generate unique alert ID"""
        timestamp = datetime.now().isoformat()
        return hashlib.md5(f"alert_{timestamp}".encode()).hexdigest()[:16]
    
    async def _check_stream_alerts(self, stream_id: str, data_point: Dict[str, Any], config: StreamConfig) -> Optional[StreamAlert]:
        """Check if data point triggers any alerts"""
        try:
            if not config.alert_thresholds:
                return None
            
            value = float(data_point.get("value", 0))
            
            for threshold_type, threshold_value in config.alert_thresholds.items():
                alert_triggered = False
                severity = "medium"
                
                if threshold_type == "max" and value > threshold_value:
                    alert_triggered = True
                    severity = "high"
                elif threshold_type == "min" and value < threshold_value:
                    alert_triggered = True
                    severity = "high"
                elif threshold_type == "spike" and self._is_spike(stream_id, value, threshold_value):
                    alert_triggered = True
                    severity = "medium"
                
                if alert_triggered:
                    alert = StreamAlert(
                        alert_id=self._generate_alert_id(),
                        stream_id=stream_id,
                        alert_type=threshold_type,
                        message=f"Stream {stream_id} {threshold_type} threshold exceeded: {value} > {threshold_value}",
                        severity=severity,
                        value=value,
                        threshold=threshold_value,
                        timestamp=datetime.now()
                    )
                    
                    self.stream_alerts.append(alert)
                    
                    # Limit alert history
                    if len(self.stream_alerts) > 1000:
                        self.stream_alerts = self.stream_alerts[-1000:]
                    
                    return alert
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error checking stream alerts: {e}")
            return None
    
    def _is_spike(self, stream_id: str, current_value: float, spike_threshold: float) -> bool:
        """Check if current value is a spike compared to recent values"""
        try:
            recent_data = list(self.stream_buffers[stream_id])[-10:]  # Last 10 points
            if len(recent_data) < 5:
                return False
            
            recent_values = [float(dp.get("value", 0)) for dp in recent_data[:-1]]  # Exclude current
            avg_recent = statistics.mean(recent_values)
            
            # Check if current value deviates significantly from recent average
            deviation = abs(current_value - avg_recent) / max(avg_recent, 1)
            return deviation > spike_threshold
            
        except Exception as e:
            return False
    
    async def _process_windowed_data(self, stream_id: str, data_point: Dict[str, Any], config: StreamConfig):
        """Process data in windowed mode"""
        try:
            if not config.window_size:
                return
            
            # Check if we need to create a new window
            current_time = datetime.now()
            
            # Get the latest window for this stream
            if stream_id in self.active_windows and self.active_windows[stream_id]:
                latest_window = self.active_windows[stream_id][-1]
                window_duration = (current_time - latest_window.start_time).total_seconds()
                
                if window_duration < config.window_size:
                    # Add to existing window
                    latest_window.data_points.append(data_point)
                    latest_window.end_time = current_time
                else:
                    # Create new window
                    await self._create_new_window(stream_id, data_point, config)
            else:
                # Create first window
                await self._create_new_window(stream_id, data_point, config)
                
        except Exception as e:
            self.logger.error(f"Error processing windowed data: {e}")
    
    async def _create_new_window(self, stream_id: str, data_point: Dict[str, Any], config: StreamConfig):
        """Create a new streaming window"""
        try:
            window = StreamingWindow(
                window_id=self._generate_window_id(stream_id),
                stream_id=stream_id,
                start_time=datetime.now(),
                end_time=datetime.now(),
                data_points=[data_point]
            )
            
            self.active_windows[stream_id].append(window)
            
            # Limit window history
            if len(self.active_windows[stream_id]) > 100:
                self.active_windows[stream_id] = self.active_windows[stream_id][-100:]
                
        except Exception as e:
            self.logger.error(f"Error creating new window: {e}")
    
    async def _process_batch_data(self, stream_id: str, data_point: Dict[str, Any], config: StreamConfig):
        """Process data in batch mode"""
        try:
            # In batch mode, we accumulate data and process periodically
            # This is handled by the main processor loop
            pass
            
        except Exception as e:
            self.logger.error(f"Error processing batch data: {e}")
    
    async def _calculate_current_stream_stats(self, stream_id: str) -> Dict[str, Any]:
        """Calculate current statistics for a stream"""
        try:
            if stream_id not in self.stream_buffers:
                return {}
            
            recent_data = list(self.stream_buffers[stream_id])[-100:]  # Last 100 points
            if not recent_data:
                return {}
            
            values = [float(dp.get("value", 0)) for dp in recent_data if "value" in dp]
            
            if not values:
                return {"data_points": len(recent_data)}
            
            return {
                "data_points": len(recent_data),
                "latest_value": values[-1],
                "average": statistics.mean(values),
                "min": min(values),
                "max": max(values),
                "std_dev": statistics.stdev(values) if len(values) > 1 else 0
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating stream stats: {e}")
            return {}
    
    async def _detect_statistical_anomalies(self, values: List[float], data_points: List[Dict], sensitivity: float) -> List[Dict[str, Any]]:
        """Detect anomalies using statistical methods"""
        try:
            if len(values) < 10:
                return []
            
            mean_val = statistics.mean(values)
            std_val = statistics.stdev(values)
            threshold = sensitivity * std_val
            
            anomalies = []
            for i, (value, data_point) in enumerate(zip(values, data_points)):
                if abs(value - mean_val) > threshold:
                    anomalies.append({
                        "index": i,
                        "value": value,
                        "expected": mean_val,
                        "deviation": abs(value - mean_val),
                        "threshold": threshold,
                        "timestamp": data_point.get("timestamp"),
                        "severity": "high" if abs(value - mean_val) > 2 * threshold else "medium"
                    })
            
            return anomalies
            
        except Exception as e:
            self.logger.error(f"Error detecting statistical anomalies: {e}")
            return []
    
    async def _detect_moving_average_anomalies(self, values: List[float], data_points: List[Dict], sensitivity: float) -> List[Dict[str, Any]]:
        """Detect anomalies using moving average"""
        try:
            window_size = min(20, len(values) // 4)
            if window_size < 3:
                return []
            
            anomalies = []
            
            for i in range(window_size, len(values)):
                window_values = values[i-window_size:i]
                moving_avg = statistics.mean(window_values)
                moving_std = statistics.stdev(window_values) if len(window_values) > 1 else 0
                
                current_value = values[i]
                threshold = sensitivity * moving_std
                
                if abs(current_value - moving_avg) > threshold:
                    anomalies.append({
                        "index": i,
                        "value": current_value,
                        "expected": moving_avg,
                        "deviation": abs(current_value - moving_avg),
                        "threshold": threshold,
                        "timestamp": data_points[i].get("timestamp"),
                        "severity": "high" if abs(current_value - moving_avg) > 2 * threshold else "medium"
                    })
            
            return anomalies
            
        except Exception as e:
            self.logger.error(f"Error detecting moving average anomalies: {e}")
            return []
    
    async def _detect_percentile_anomalies(self, values: List[float], data_points: List[Dict], sensitivity: float) -> List[Dict[str, Any]]:
        """Detect anomalies using percentile-based method"""
        try:
            # Calculate percentiles
            p25 = np.percentile(values, 25)
            p75 = np.percentile(values, 75)
            iqr = p75 - p25
            
            # Calculate bounds
            lower_bound = p25 - sensitivity * iqr
            upper_bound = p75 + sensitivity * iqr
            
            anomalies = []
            for i, (value, data_point) in enumerate(zip(values, data_points)):
                if value < lower_bound or value > upper_bound:
                    anomalies.append({
                        "index": i,
                        "value": value,
                        "lower_bound": lower_bound,
                        "upper_bound": upper_bound,
                        "timestamp": data_point.get("timestamp"),
                        "severity": "high" if value < lower_bound - iqr or value > upper_bound + iqr else "medium"
                    })
            
            return anomalies
            
        except Exception as e:
            self.logger.error(f"Error detecting percentile anomalies: {e}")
            return []
    
    async def _run_stream_processor(self):
        """Main stream processing loop"""
        while self.processor_running:
            try:
                await asyncio.sleep(1)  # Process every second
                
                # Process each active stream
                for stream_id, config in self.stream_configs.items():
                    if config.processing_mode == StreamingMode.BATCH:
                        await self._process_batch_stream(stream_id, config)
                    elif config.processing_mode == StreamingMode.WINDOWED:
                        await self._process_windowed_stream(stream_id, config)
                
                # Clean up old data
                await self._cleanup_old_data()
                
            except Exception as e:
                self.logger.error(f"Error in stream processor: {e}")
    
    async def _process_batch_stream(self, stream_id: str, config: StreamConfig):
        """Process stream in batch mode"""
        try:
            # Check if it's time to process batch
            # This would be based on time intervals or data volume
            pass
            
        except Exception as e:
            self.logger.error(f"Error processing batch stream {stream_id}: {e}")
    
    async def _process_windowed_stream(self, stream_id: str, config: StreamConfig):
        """Process stream in windowed mode"""
        try:
            # Check for completed windows and aggregate them
            if stream_id in self.active_windows:
                current_time = datetime.now()
                
                for window in self.active_windows[stream_id]:
                    if not window.aggregated_results:
                        window_duration = (current_time - window.start_time).total_seconds()
                        
                        if window_duration >= config.window_size:
                            # Aggregate the window
                            await self._aggregate_window_data({
                                "stream_id": stream_id,
                                "window_size": config.window_size,
                                "aggregations": [agg.value for agg in config.aggregations]
                            })
            
        except Exception as e:
            self.logger.error(f"Error processing windowed stream {stream_id}: {e}")
    
    async def _cleanup_old_data(self):
        """Clean up old data to prevent memory issues"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=24)
            
            # Clean up old alerts
            self.stream_alerts = [
                alert for alert in self.stream_alerts
                if alert.timestamp > cutoff_time
            ]
            
            # Clean up old windows
            for stream_id in self.active_windows:
                self.active_windows[stream_id] = [
                    window for window in self.active_windows[stream_id]
                    if window.end_time > cutoff_time
                ]
            
        except Exception as e:
            self.logger.error(f"Error cleaning up old data: {e}")
    
    async def _get_processor_status(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Get processor status"""
        try:
            return {
                "operation": "processor_status",
                "processor_running": self.processor_running,
                "total_streams": len(self.stream_configs),
                "active_buffers": len([s for s in self.stream_buffers.keys() if len(self.stream_buffers[s]) > 0]),
                "total_windows": sum(len(windows) for windows in self.active_windows.values()),
                "total_alerts": len(self.stream_alerts),
                "unresolved_alerts": len([a for a in self.stream_alerts if not a.resolved])
            }
            
        except Exception as e:
            self.logger.error(f"Error getting processor status: {e}")
            return {"error": str(e), "operation": "processor_status"}
    
    # Built-in stream processing functions
    
    def _calculate_moving_average(self, values: List[float], window_size: int = 10) -> float:
        """Calculate moving average"""
        if len(values) < window_size:
            return statistics.mean(values) if values else 0
        return statistics.mean(values[-window_size:])
    
    def _calculate_exponential_smoothing(self, values: List[float], alpha: float = 0.3) -> float:
        """Calculate exponentially smoothed value"""
        if not values:
            return 0
        if len(values) == 1:
            return values[0]
        
        smoothed = values[0]
        for value in values[1:]:
            smoothed = alpha * value + (1 - alpha) * smoothed
        
        return smoothed
    
    def _detect_trend(self, values: List[float], min_points: int = 5) -> str:
        """Detect trend in values"""
        if len(values) < min_points:
            return "insufficient_data"
        
        # Simple trend detection using linear regression slope
        x = list(range(len(values)))
        n = len(values)
        
        sum_x = sum(x)
        sum_y = sum(values)
        sum_xy = sum(x[i] * values[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
        
        if slope > 0.1:
            return "increasing"
        elif slope < -0.1:
            return "decreasing"
        else:
            return "stable"
    
    def _detect_spikes(self, values: List[float], threshold: float = 2.0) -> List[int]:
        """Detect spikes in values"""
        if len(values) < 3:
            return []
        
        spikes = []
        mean_val = statistics.mean(values)
        std_val = statistics.stdev(values) if len(values) > 1 else 0
        
        for i, value in enumerate(values):
            if abs(value - mean_val) > threshold * std_val:
                spikes.append(i)
        
        return spikes
    
    def _match_patterns(self, values: List[float], pattern: List[float], tolerance: float = 0.1) -> List[int]:
        """Match patterns in values"""
        if len(values) < len(pattern):
            return []
        
        matches = []
        pattern_len = len(pattern)
        
        for i in range(len(values) - pattern_len + 1):
            window = values[i:i + pattern_len]
            
            # Normalize both sequences
            window_norm = [(v - min(window)) / (max(window) - min(window)) if max(window) != min(window) else 0 for v in window]
            pattern_norm = [(v - min(pattern)) / (max(pattern) - min(pattern)) if max(pattern) != min(pattern) else 0 for v in pattern]
            
            # Calculate similarity
            similarity = 1 - sum(abs(w - p) for w, p in zip(window_norm, pattern_norm)) / pattern_len
            
            if similarity > (1 - tolerance):
                matches.append(i)
        
        return matches