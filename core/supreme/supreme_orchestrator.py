"""
Supreme Engine Orchestrator
Master coordination and communication system for all supreme engines
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json

from .base_supreme_engine import BaseSupremeEngine, SupremeRequest, SupremeResponse

logger = logging.getLogger(__name__)


class EngineType(Enum):
    REASONING = "reasoning"
    SYSTEM_CONTROL = "system_control"
    LEARNING = "learning"
    INTEGRATION = "integration"
    ANALYTICS = "analytics"
    COMMUNICATION = "communication"
    KNOWLEDGE = "knowledge"
    PROACTIVE = "proactive"
    SECURITY = "security"
    SCALABILITY = "scalability"


class OrchestrationStrategy(Enum):
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"
    PRIORITY_BASED = "priority_based"
    ADAPTIVE = "adaptive"


class EngineStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    BUSY = "busy"
    ERROR = "error"
    MAINTENANCE = "maintenance"


@dataclass
class EngineInfo:
    engine_type: EngineType
    engine_instance: BaseSupremeEngine
    status: EngineStatus
    capabilities: List[str]
    priority: int
    last_activity: datetime
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OrchestrationRequest:
    request_id: str
    operation: str
    parameters: Dict[str, Any]
    required_engines: List[EngineType]
    strategy: OrchestrationStrategy
    priority: int
    timeout: Optional[timedelta] = None
    dependencies: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class OrchestrationResult:
    request_id: str
    overall_status: str
    engine_results: Dict[str, Any]
    execution_time: float
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    completed_at: datetime = field(default_factory=datetime.now)


class EngineCoordinator:
    """Coordinates communication and data sharing between engines"""
    
    def __init__(self):
        self.engines: Dict[EngineType, EngineInfo] = {}
        self.communication_channels: Dict[str, asyncio.Queue] = {}
        self.shared_data_store: Dict[str, Any] = {}
        self.coordination_history: List[Dict[str, Any]] = []
    
    def register_engine(self, engine_type: EngineType, engine: BaseSupremeEngine, 
                       capabilities: List[str], priority: int = 5) -> bool:
        """Register an engine with the coordinator"""
        try:
            engine_info = EngineInfo(
                engine_type=engine_type,
                engine_instance=engine,
                status=EngineStatus.ACTIVE,
                capabilities=capabilities,
                priority=priority,
                last_activity=datetime.now()
            )
            
            self.engines[engine_type] = engine_info
            
            # Create communication channel for this engine
            channel_name = f"{engine_type.value}_channel"
            self.communication_channels[channel_name] = asyncio.Queue()
            
            logger.info(f"Registered engine: {engine_type.value} with {len(capabilities)} capabilities")
            return True
            
        except Exception as e:
            logger.error(f"Error registering engine {engine_type.value}: {e}")
            return False
    
    def unregister_engine(self, engine_type: EngineType) -> bool:
        """Unregister an engine from the coordinator"""
        try:
            if engine_type in self.engines:
                del self.engines[engine_type]
                
                # Remove communication channel
                channel_name = f"{engine_type.value}_channel"
                if channel_name in self.communication_channels:
                    del self.communication_channels[channel_name]
                
                logger.info(f"Unregistered engine: {engine_type.value}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error unregistering engine {engine_type.value}: {e}")
            return False
    
    async def send_message(self, from_engine: EngineType, to_engine: EngineType, 
                          message: Dict[str, Any]) -> bool:
        """Send a message between engines"""
        try:
            channel_name = f"{to_engine.value}_channel"
            if channel_name in self.communication_channels:
                message_envelope = {
                    "from": from_engine.value,
                    "to": to_engine.value,
                    "message": message,
                    "timestamp": datetime.now().isoformat()
                }
                
                await self.communication_channels[channel_name].put(message_envelope)
                
                # Update coordination history
                self.coordination_history.append({
                    "type": "message",
                    "from": from_engine.value,
                    "to": to_engine.value,
                    "timestamp": datetime.now().isoformat()
                })
                
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error sending message from {from_engine.value} to {to_engine.value}: {e}")
            return False
    
    async def receive_message(self, engine_type: EngineType, timeout: float = 1.0) -> Optional[Dict[str, Any]]:
        """Receive a message for an engine"""
        try:
            channel_name = f"{engine_type.value}_channel"
            if channel_name in self.communication_channels:
                try:
                    message = await asyncio.wait_for(
                        self.communication_channels[channel_name].get(),
                        timeout=timeout
                    )
                    return message
                except asyncio.TimeoutError:
                    return None
            return None
            
        except Exception as e:
            logger.error(f"Error receiving message for {engine_type.value}: {e}")
            return None
    
    def share_data(self, key: str, data: Any, source_engine: EngineType) -> bool:
        """Share data between engines"""
        try:
            self.shared_data_store[key] = {
                "data": data,
                "source": source_engine.value,
                "timestamp": datetime.now().isoformat()
            }
            
            # Update coordination history
            self.coordination_history.append({
                "type": "data_share",
                "key": key,
                "source": source_engine.value,
                "timestamp": datetime.now().isoformat()
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Error sharing data from {source_engine.value}: {e}")
            return False
    
    def get_shared_data(self, key: str) -> Optional[Any]:
        """Get shared data"""
        try:
            if key in self.shared_data_store:
                return self.shared_data_store[key]["data"]
            return None
            
        except Exception as e:
            logger.error(f"Error getting shared data for key {key}: {e}")
            return None
    
    def get_engine_status(self, engine_type: EngineType) -> Optional[EngineStatus]:
        """Get the status of an engine"""
        if engine_type in self.engines:
            return self.engines[engine_type].status
        return None
    
    def update_engine_status(self, engine_type: EngineType, status: EngineStatus) -> bool:
        """Update the status of an engine"""
        try:
            if engine_type in self.engines:
                self.engines[engine_type].status = status
                self.engines[engine_type].last_activity = datetime.now()
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error updating engine status for {engine_type.value}: {e}")
            return False
    
    def get_available_engines(self) -> List[EngineType]:
        """Get list of available engines"""
        return [
            engine_type for engine_type, info in self.engines.items()
            if info.status == EngineStatus.ACTIVE
        ]
    
    def get_engine_capabilities(self, engine_type: EngineType) -> List[str]:
        """Get capabilities of an engine"""
        if engine_type in self.engines:
            return self.engines[engine_type].capabilities
        return []


class SupremeOrchestrator:
    """Master orchestrator for all supreme engines"""
    
    def __init__(self, config=None):
        self.config = config
        self.coordinator = EngineCoordinator()
        self.orchestration_queue: asyncio.Queue = asyncio.Queue()
        self.active_requests: Dict[str, OrchestrationRequest] = {}
        self.completed_requests: Dict[str, OrchestrationResult] = {}
        self.orchestration_strategies = {
            OrchestrationStrategy.SEQUENTIAL: self._execute_sequential,
            OrchestrationStrategy.PARALLEL: self._execute_parallel,
            OrchestrationStrategy.CONDITIONAL: self._execute_conditional,
            OrchestrationStrategy.PRIORITY_BASED: self._execute_priority_based,
            OrchestrationStrategy.ADAPTIVE: self._execute_adaptive
        }
        self.is_running = False
        self.orchestration_task: Optional[asyncio.Task] = None
    
    async def initialize(self) -> bool:
        """Initialize the supreme orchestrator"""
        try:
            logger.info("Initializing Supreme Orchestrator...")
            
            # Start orchestration loop
            self.is_running = True
            self.orchestration_task = asyncio.create_task(self._orchestration_loop())
            
            logger.info("Supreme Orchestrator initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing Supreme Orchestrator: {e}")
            return False
    
    async def shutdown(self) -> bool:
        """Shutdown the supreme orchestrator"""
        try:
            logger.info("Shutting down Supreme Orchestrator...")
            
            self.is_running = False
            if self.orchestration_task:
                self.orchestration_task.cancel()
                try:
                    await self.orchestration_task
                except asyncio.CancelledError:
                    pass
            
            logger.info("Supreme Orchestrator shutdown complete")
            return True
            
        except Exception as e:
            logger.error(f"Error shutting down Supreme Orchestrator: {e}")
            return False
    
    def register_engine(self, engine_type: EngineType, engine: BaseSupremeEngine, 
                       capabilities: List[str], priority: int = 5) -> bool:
        """Register an engine with the orchestrator"""
        return self.coordinator.register_engine(engine_type, engine, capabilities, priority)
    
    async def orchestrate_request(self, request: OrchestrationRequest) -> str:
        """Submit a request for orchestration"""
        try:
            # Add to active requests
            self.active_requests[request.request_id] = request
            
            # Add to orchestration queue
            await self.orchestration_queue.put(request)
            
            logger.info(f"Orchestration request submitted: {request.request_id}")
            return request.request_id
            
        except Exception as e:
            logger.error(f"Error submitting orchestration request: {e}")
            return ""
    
    async def get_orchestration_result(self, request_id: str, timeout: float = 30.0) -> Optional[OrchestrationResult]:
        """Get the result of an orchestration request"""
        try:
            start_time = datetime.now()
            
            while (datetime.now() - start_time).total_seconds() < timeout:
                if request_id in self.completed_requests:
                    return self.completed_requests[request_id]
                
                await asyncio.sleep(0.1)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting orchestration result: {e}")
            return None
    
    async def _orchestration_loop(self):
        """Main orchestration loop"""
        while self.is_running:
            try:
                # Get next request from queue
                try:
                    request = await asyncio.wait_for(self.orchestration_queue.get(), timeout=1.0)
                except asyncio.TimeoutError:
                    continue
                
                # Execute the request
                result = await self._execute_orchestration_request(request)
                
                # Store result and clean up
                self.completed_requests[request.request_id] = result
                if request.request_id in self.active_requests:
                    del self.active_requests[request.request_id]
                
            except Exception as e:
                logger.error(f"Error in orchestration loop: {e}")
                await asyncio.sleep(1.0)
    
    async def _execute_orchestration_request(self, request: OrchestrationRequest) -> OrchestrationResult:
        """Execute an orchestration request"""
        start_time = datetime.now()
        
        try:
            # Get orchestration strategy
            strategy_func = self.orchestration_strategies.get(
                request.strategy, 
                self._execute_sequential
            )
            
            # Execute using the selected strategy
            engine_results = await strategy_func(request)
            
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Determine overall status
            overall_status = "completed"
            errors = []
            warnings = []
            
            for engine_type, result in engine_results.items():
                if isinstance(result, dict) and "error" in result:
                    errors.append(f"{engine_type}: {result['error']}")
                    overall_status = "partial_failure"
            
            if len(errors) == len(engine_results):
                overall_status = "failed"
            
            return OrchestrationResult(
                request_id=request.request_id,
                overall_status=overall_status,
                engine_results=engine_results,
                execution_time=execution_time,
                errors=errors,
                warnings=warnings
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Error executing orchestration request {request.request_id}: {e}")
            
            return OrchestrationResult(
                request_id=request.request_id,
                overall_status="failed",
                engine_results={},
                execution_time=execution_time,
                errors=[str(e)]
            )
    
    async def _execute_sequential(self, request: OrchestrationRequest) -> Dict[str, Any]:
        """Execute engines sequentially"""
        results = {}
        
        # Sort engines by priority
        sorted_engines = sorted(
            request.required_engines,
            key=lambda e: self.coordinator.engines.get(e, EngineInfo(e, None, EngineStatus.INACTIVE, [], 0, datetime.now())).priority,
            reverse=True
        )
        
        for engine_type in sorted_engines:
            if engine_type in self.coordinator.engines:
                engine_info = self.coordinator.engines[engine_type]
                
                if engine_info.status == EngineStatus.ACTIVE:
                    try:
                        # Create engine request
                        engine_request = SupremeRequest(
                            request_id=f"{request.request_id}_{engine_type.value}",
                            operation=request.operation,
                            parameters=request.parameters
                        )
                        
                        # Execute on engine
                        result = await engine_info.engine_instance.execute_request(engine_request)
                        results[engine_type.value] = result.result if result else {"error": "No result"}
                        
                    except Exception as e:
                        results[engine_type.value] = {"error": str(e)}
                else:
                    results[engine_type.value] = {"error": f"Engine not active: {engine_info.status.value}"}
            else:
                results[engine_type.value] = {"error": "Engine not registered"}
        
        return results
    
    async def _execute_parallel(self, request: OrchestrationRequest) -> Dict[str, Any]:
        """Execute engines in parallel"""
        tasks = []
        engine_types = []
        
        for engine_type in request.required_engines:
            if engine_type in self.coordinator.engines:
                engine_info = self.coordinator.engines[engine_type]
                
                if engine_info.status == EngineStatus.ACTIVE:
                    # Create engine request
                    engine_request = SupremeRequest(
                        request_id=f"{request.request_id}_{engine_type.value}",
                        operation=request.operation,
                        parameters=request.parameters
                    )
                    
                    # Create task
                    task = asyncio.create_task(
                        engine_info.engine_instance.execute_request(engine_request)
                    )
                    tasks.append(task)
                    engine_types.append(engine_type)
        
        # Wait for all tasks to complete
        if tasks:
            results_list = await asyncio.gather(*tasks, return_exceptions=True)
            
            results = {}
            for i, result in enumerate(results_list):
                engine_type = engine_types[i]
                if isinstance(result, Exception):
                    results[engine_type.value] = {"error": str(result)}
                elif result:
                    results[engine_type.value] = result.result
                else:
                    results[engine_type.value] = {"error": "No result"}
            
            return results
        
        return {}
    
    async def _execute_conditional(self, request: OrchestrationRequest) -> Dict[str, Any]:
        """Execute engines based on conditions"""
        # For now, implement as sequential with condition checking
        # This can be enhanced with more sophisticated condition logic
        return await self._execute_sequential(request)
    
    async def _execute_priority_based(self, request: OrchestrationRequest) -> Dict[str, Any]:
        """Execute engines based on priority"""
        # This is similar to sequential but with strict priority ordering
        return await self._execute_sequential(request)
    
    async def _execute_adaptive(self, request: OrchestrationRequest) -> Dict[str, Any]:
        """Execute engines using adaptive strategy"""
        # Start with parallel execution, fall back to sequential if needed
        try:
            return await self._execute_parallel(request)
        except Exception:
            logger.warning("Parallel execution failed, falling back to sequential")
            return await self._execute_sequential(request)
    
    def get_orchestration_status(self) -> Dict[str, Any]:
        """Get current orchestration status"""
        return {
            "is_running": self.is_running,
            "active_requests": len(self.active_requests),
            "completed_requests": len(self.completed_requests),
            "registered_engines": len(self.coordinator.engines),
            "available_engines": len(self.coordinator.get_available_engines()),
            "queue_size": self.orchestration_queue.qsize()
        }
    
    def get_engine_status_summary(self) -> Dict[str, Any]:
        """Get summary of all engine statuses"""
        summary = {}
        
        for engine_type, engine_info in self.coordinator.engines.items():
            summary[engine_type.value] = {
                "status": engine_info.status.value,
                "capabilities": len(engine_info.capabilities),
                "priority": engine_info.priority,
                "last_activity": engine_info.last_activity.isoformat()
            }
        
        return summary