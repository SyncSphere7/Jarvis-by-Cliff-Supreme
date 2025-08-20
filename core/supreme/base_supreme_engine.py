"""
Base Supreme Engine
Abstract base class for all supreme capability engines.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from enum import Enum
import asyncio
import logging
import time
from datetime import datetime

from .supreme_config import EngineConfig, CapabilityLevel

class EngineStatus(Enum):
    """Engine operational status"""
    INITIALIZING = "initializing"
    READY = "ready"
    ACTIVE = "active"
    SCALING = "scaling"
    OPTIMIZING = "optimizing"
    ERROR = "error"
    SHUTDOWN = "shutdown"

@dataclass
class EngineMetrics:
    """Performance metrics for supreme engines"""
    operations_per_second: float = 0.0
    success_rate: float = 100.0
    average_response_time: float = 0.0
    resource_utilization: float = 0.0
    learning_progress: float = 0.0
    capability_score: float = 0.0
    last_updated: datetime = None
    
    def __post_init__(self):
        if self.last_updated is None:
            self.last_updated = datetime.now()

@dataclass
class SupremeRequest:
    """Request structure for supreme operations"""
    request_id: str
    operation: str
    parameters: Dict[str, Any]
    priority: int = 5  # 1-10 scale
    timeout: float = 30.0
    context: Optional[Dict[str, Any]] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class SupremeResponse:
    """Response structure for supreme operations"""
    request_id: str
    success: bool
    result: Any = None
    error: Optional[str] = None
    execution_time: float = 0.0
    confidence: float = 1.0
    metadata: Dict[str, Any] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.metadata is None:
            self.metadata = {}

class BaseSupremeEngine(ABC):
    """
    Abstract base class for all supreme capability engines.
    Provides common functionality and interface for supreme operations.
    """
    
    def __init__(self, engine_name: str, config: EngineConfig):
        self.engine_name = engine_name
        self.config = config
        self.status = EngineStatus.INITIALIZING
        self.metrics = EngineMetrics()
        self.logger = logging.getLogger(f"supreme.{engine_name}")
        self._operation_history: List[SupremeResponse] = []
        self._active_operations: Dict[str, asyncio.Task] = {}
        self._start_time = time.time()
        
    async def initialize(self) -> bool:
        """Initialize the supreme engine"""
        try:
            self.logger.info(f"Initializing {self.engine_name} engine...")
            self.status = EngineStatus.INITIALIZING
            
            # Perform engine-specific initialization
            success = await self._initialize_engine()
            
            if success:
                self.status = EngineStatus.READY
                self.logger.info(f"{self.engine_name} engine initialized successfully")
                await self._start_monitoring()
            else:
                self.status = EngineStatus.ERROR
                self.logger.error(f"Failed to initialize {self.engine_name} engine")
                
            return success
            
        except Exception as e:
            self.status = EngineStatus.ERROR
            self.logger.error(f"Error initializing {self.engine_name} engine: {e}")
            return False
    
    @abstractmethod
    async def _initialize_engine(self) -> bool:
        """Engine-specific initialization logic"""
        pass
    
    async def execute(self, request: SupremeRequest) -> SupremeResponse:
        """Execute a supreme operation"""
        start_time = time.time()
        
        try:
            self.status = EngineStatus.ACTIVE
            self.logger.debug(f"Executing {request.operation} (ID: {request.request_id})")
            
            # Validate request
            if not await self._validate_request(request):
                return SupremeResponse(
                    request_id=request.request_id,
                    success=False,
                    error="Invalid request",
                    execution_time=time.time() - start_time
                )
            
            # Execute the operation
            result = await self._execute_operation(request)
            
            # Create response
            response = SupremeResponse(
                request_id=request.request_id,
                success=True,
                result=result,
                execution_time=time.time() - start_time,
                confidence=await self._calculate_confidence(request, result)
            )
            
            # Update metrics
            await self._update_metrics(response)
            self._operation_history.append(response)
            
            # Keep only last 1000 operations in history
            if len(self._operation_history) > 1000:
                self._operation_history = self._operation_history[-1000:]
            
            self.status = EngineStatus.READY
            return response
            
        except Exception as e:
            self.logger.error(f"Error executing {request.operation}: {e}")
            response = SupremeResponse(
                request_id=request.request_id,
                success=False,
                error=str(e),
                execution_time=time.time() - start_time
            )
            self._operation_history.append(response)
            self.status = EngineStatus.READY
            return response
    
    @abstractmethod
    async def _execute_operation(self, request: SupremeRequest) -> Any:
        """Engine-specific operation execution"""
        pass
    
    async def _validate_request(self, request: SupremeRequest) -> bool:
        """Validate incoming request"""
        if not request.request_id or not request.operation:
            return False
        
        # Check if engine supports the operation
        supported_operations = await self.get_supported_operations()
        if request.operation not in supported_operations:
            return False
            
        return True
    
    async def _calculate_confidence(self, request: SupremeRequest, result: Any) -> float:
        """Calculate confidence score for the operation result"""
        # Base confidence calculation - can be overridden by specific engines
        base_confidence = 0.8
        
        # Adjust based on capability level
        level_multiplier = {
            CapabilityLevel.BASIC: 0.6,
            CapabilityLevel.ENHANCED: 0.7,
            CapabilityLevel.ADVANCED: 0.8,
            CapabilityLevel.SUPREME: 0.9,
            CapabilityLevel.GODLIKE: 1.0
        }
        
        return base_confidence * level_multiplier.get(self.config.capability_level, 0.8)
    
    async def _update_metrics(self, response: SupremeResponse):
        """Update engine performance metrics"""
        # Update success rate
        recent_operations = self._operation_history[-100:]  # Last 100 operations
        if recent_operations:
            success_count = sum(1 for op in recent_operations if op.success)
            self.metrics.success_rate = (success_count / len(recent_operations)) * 100
        
        # Update average response time
        if recent_operations:
            total_time = sum(op.execution_time for op in recent_operations)
            self.metrics.average_response_time = total_time / len(recent_operations)
        
        # Update operations per second
        uptime = time.time() - self._start_time
        if uptime > 0:
            self.metrics.operations_per_second = len(self._operation_history) / uptime
        
        # Update capability score based on recent performance
        self.metrics.capability_score = (
            (self.metrics.success_rate / 100) * 0.4 +
            (1.0 / max(self.metrics.average_response_time, 0.1)) * 0.3 +
            min(self.metrics.operations_per_second / 10, 1.0) * 0.3
        ) * 100
        
        self.metrics.last_updated = datetime.now()
    
    async def _start_monitoring(self):
        """Start background monitoring and optimization"""
        if self.config.auto_scaling:
            asyncio.create_task(self._monitor_performance())
    
    async def _monitor_performance(self):
        """Monitor and optimize engine performance"""
        while self.status != EngineStatus.SHUTDOWN:
            try:
                await asyncio.sleep(60)  # Monitor every minute
                
                # Check if optimization is needed
                if (self.metrics.success_rate < 95 or 
                    self.metrics.average_response_time > 5.0):
                    await self._optimize_performance()
                
                # Auto-scale if needed
                if self.config.auto_scaling:
                    await self._auto_scale()
                    
            except Exception as e:
                self.logger.error(f"Error in performance monitoring: {e}")
    
    async def _optimize_performance(self):
        """Optimize engine performance"""
        self.status = EngineStatus.OPTIMIZING
        self.logger.info(f"Optimizing {self.engine_name} engine performance...")
        
        # Engine-specific optimization logic can be implemented in subclasses
        await self._perform_optimization()
        
        self.status = EngineStatus.READY
    
    async def _perform_optimization(self):
        """Engine-specific optimization logic"""
        # Default optimization - can be overridden
        pass
    
    async def _auto_scale(self):
        """Auto-scale engine resources based on demand"""
        if not self.config.auto_scaling:
            return
            
        # Simple scaling logic based on recent performance
        if self.metrics.operations_per_second > 50:  # High load
            self.status = EngineStatus.SCALING
            await self._scale_up()
        elif self.metrics.operations_per_second < 5:  # Low load
            await self._scale_down()
    
    async def _scale_up(self):
        """Scale up engine resources"""
        self.logger.info(f"Scaling up {self.engine_name} engine resources")
        # Engine-specific scaling logic
    
    async def _scale_down(self):
        """Scale down engine resources"""
        self.logger.info(f"Scaling down {self.engine_name} engine resources")
        # Engine-specific scaling logic
    
    @abstractmethod
    async def get_supported_operations(self) -> List[str]:
        """Get list of operations supported by this engine"""
        pass
    
    async def get_status(self) -> Dict[str, Any]:
        """Get current engine status and metrics"""
        return {
            "engine_name": self.engine_name,
            "status": self.status.value,
            "metrics": {
                "operations_per_second": self.metrics.operations_per_second,
                "success_rate": self.metrics.success_rate,
                "average_response_time": self.metrics.average_response_time,
                "resource_utilization": self.metrics.resource_utilization,
                "learning_progress": self.metrics.learning_progress,
                "capability_score": self.metrics.capability_score,
                "last_updated": self.metrics.last_updated.isoformat() if self.metrics.last_updated else None
            },
            "config": {
                "enabled": self.config.enabled,
                "capability_level": self.config.capability_level.value,
                "auto_scaling": self.config.auto_scaling,
                "learning_rate": self.config.learning_rate
            },
            "operation_history_count": len(self._operation_history),
            "active_operations": len(self._active_operations)
        }
    
    async def shutdown(self):
        """Shutdown the engine gracefully"""
        self.logger.info(f"Shutting down {self.engine_name} engine...")
        self.status = EngineStatus.SHUTDOWN
        
        # Cancel active operations
        for task in self._active_operations.values():
            task.cancel()
        
        # Wait for operations to complete
        if self._active_operations:
            await asyncio.gather(*self._active_operations.values(), return_exceptions=True)
        
        # Engine-specific shutdown logic
        await self._shutdown_engine()
        
        self.logger.info(f"{self.engine_name} engine shutdown complete")
    
    async def _shutdown_engine(self):
        """Engine-specific shutdown logic"""
        pass