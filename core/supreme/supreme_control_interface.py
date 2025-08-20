"""
Supreme Control Interface
Unified interface for accessing all supreme capabilities
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

from .supreme_orchestrator import (
    SupremeOrchestrator, EngineType, OrchestrationRequest, 
    OrchestrationStrategy, OrchestrationResult
)
from .base_supreme_engine import SupremeRequest, SupremeResponse

logger = logging.getLogger(__name__)


class CommandType(Enum):
    ANALYZE = "analyze"
    EXECUTE = "execute"
    OPTIMIZE = "optimize"
    LEARN = "learn"
    PREDICT = "predict"
    SECURE = "secure"
    SCALE = "scale"
    COMMUNICATE = "communicate"
    INTEGRATE = "integrate"
    MONITOR = "monitor"


class ResponseFormat(Enum):
    JSON = "json"
    TEXT = "text"
    STRUCTURED = "structured"
    SUMMARY = "summary"


@dataclass
class SupremeCommand:
    command_id: str
    command_type: CommandType
    operation: str
    parameters: Dict[str, Any]
    response_format: ResponseFormat = ResponseFormat.STRUCTURED
    priority: int = 5
    timeout: Optional[timedelta] = None
    context: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.context is None:
            self.context = {}
        if self.timeout is None:
            self.timeout = timedelta(minutes=5)


@dataclass
class SupremeCommandResult:
    command_id: str
    status: str
    result: Any
    execution_time: float
    engines_used: List[str]
    errors: List[str] = None
    warnings: List[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []
        if self.metadata is None:
            self.metadata = {}


class CommandProcessor:
    """Processes supreme commands and routes them to appropriate engines"""
    
    def __init__(self):
        self.command_mappings = {
            CommandType.ANALYZE: [EngineType.ANALYTICS, EngineType.REASONING],
            CommandType.EXECUTE: [EngineType.SYSTEM_CONTROL, EngineType.INTEGRATION],
            CommandType.OPTIMIZE: [EngineType.SCALABILITY, EngineType.REASONING],
            CommandType.LEARN: [EngineType.LEARNING, EngineType.ANALYTICS],
            CommandType.PREDICT: [EngineType.ANALYTICS, EngineType.REASONING],
            CommandType.SECURE: [EngineType.SECURITY, EngineType.SYSTEM_CONTROL],
            CommandType.SCALE: [EngineType.SCALABILITY, EngineType.SYSTEM_CONTROL],
            CommandType.COMMUNICATE: [EngineType.COMMUNICATION, EngineType.KNOWLEDGE],
            CommandType.INTEGRATE: [EngineType.INTEGRATION, EngineType.SYSTEM_CONTROL],
            CommandType.MONITOR: [EngineType.SYSTEM_CONTROL, EngineType.ANALYTICS]
        }
        
        self.strategy_mappings = {
            CommandType.ANALYZE: OrchestrationStrategy.PARALLEL,
            CommandType.EXECUTE: OrchestrationStrategy.SEQUENTIAL,
            CommandType.OPTIMIZE: OrchestrationStrategy.ADAPTIVE,
            CommandType.LEARN: OrchestrationStrategy.SEQUENTIAL,
            CommandType.PREDICT: OrchestrationStrategy.PARALLEL,
            CommandType.SECURE: OrchestrationStrategy.PRIORITY_BASED,
            CommandType.SCALE: OrchestrationStrategy.ADAPTIVE,
            CommandType.COMMUNICATE: OrchestrationStrategy.SEQUENTIAL,
            CommandType.INTEGRATE: OrchestrationStrategy.CONDITIONAL,
            CommandType.MONITOR: OrchestrationStrategy.PARALLEL
        }
    
    def process_command(self, command: SupremeCommand) -> OrchestrationRequest:
        """Process a supreme command into an orchestration request"""
        try:
            # Get required engines for this command type
            required_engines = self.command_mappings.get(command.command_type, [])
            
            # Get orchestration strategy
            strategy = self.strategy_mappings.get(command.command_type, OrchestrationStrategy.SEQUENTIAL)
            
            # Create orchestration request
            orchestration_request = OrchestrationRequest(
                request_id=command.command_id,
                operation=command.operation,
                parameters=command.parameters,
                required_engines=required_engines,
                strategy=strategy,
                priority=command.priority,
                timeout=command.timeout
            )
            
            return orchestration_request
            
        except Exception as e:
            logger.error(f"Error processing command {command.command_id}: {e}")
            raise
    
    def format_result(self, orchestration_result: OrchestrationResult, 
                     response_format: ResponseFormat) -> Any:
        """Format orchestration result according to requested format"""
        try:
            if response_format == ResponseFormat.JSON:
                return {
                    "status": orchestration_result.overall_status,
                    "results": orchestration_result.engine_results,
                    "execution_time": orchestration_result.execution_time,
                    "errors": orchestration_result.errors,
                    "warnings": orchestration_result.warnings
                }
            
            elif response_format == ResponseFormat.TEXT:
                text_result = f"Status: {orchestration_result.overall_status}\n"
                text_result += f"Execution Time: {orchestration_result.execution_time:.2f}s\n"
                
                if orchestration_result.engine_results:
                    text_result += "Results:\n"
                    for engine, result in orchestration_result.engine_results.items():
                        text_result += f"  {engine}: {result}\n"
                
                if orchestration_result.errors:
                    text_result += "Errors:\n"
                    for error in orchestration_result.errors:
                        text_result += f"  - {error}\n"
                
                return text_result
            
            elif response_format == ResponseFormat.SUMMARY:
                return {
                    "status": orchestration_result.overall_status,
                    "engines_executed": len(orchestration_result.engine_results),
                    "execution_time": orchestration_result.execution_time,
                    "success_rate": self._calculate_success_rate(orchestration_result),
                    "primary_result": self._extract_primary_result(orchestration_result)
                }
            
            else:  # STRUCTURED
                return orchestration_result
                
        except Exception as e:
            logger.error(f"Error formatting result: {e}")
            return {"error": str(e)}
    
    def _calculate_success_rate(self, result: OrchestrationResult) -> float:
        """Calculate success rate of orchestration"""
        if not result.engine_results:
            return 0.0
        
        successful = sum(1 for r in result.engine_results.values() 
                        if not (isinstance(r, dict) and "error" in r))
        
        return (successful / len(result.engine_results)) * 100
    
    def _extract_primary_result(self, result: OrchestrationResult) -> Any:
        """Extract the primary result from orchestration"""
        if not result.engine_results:
            return None
        
        # Return the first successful result
        for engine_result in result.engine_results.values():
            if not (isinstance(engine_result, dict) and "error" in engine_result):
                return engine_result
        
        return None


class SupremeControlInterface:
    """Unified supreme control interface"""
    
    def __init__(self):
        self.orchestrator = SupremeOrchestrator()
        self.command_processor = CommandProcessor()
        self.command_history: List[SupremeCommand] = []
        self.result_history: List[SupremeCommandResult] = []
        self.is_initialized = False
    
    async def initialize(self) -> bool:
        """Initialize the supreme control interface"""
        try:
            logger.info("Initializing Supreme Control Interface...")
            
            # Initialize orchestrator
            if not await self.orchestrator.initialize():
                return False
            
            self.is_initialized = True
            logger.info("Supreme Control Interface initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing Supreme Control Interface: {e}")
            return False
    
    async def shutdown(self) -> bool:
        """Shutdown the supreme control interface"""
        try:
            logger.info("Shutting down Supreme Control Interface...")
            
            await self.orchestrator.shutdown()
            self.is_initialized = False
            
            logger.info("Supreme Control Interface shutdown complete")
            return True
            
        except Exception as e:
            logger.error(f"Error shutting down Supreme Control Interface: {e}")
            return False
    
    def register_engine(self, engine_type: EngineType, engine, 
                       capabilities: List[str], priority: int = 5) -> bool:
        """Register an engine with the interface"""
        if not self.is_initialized:
            logger.error("Interface not initialized")
            return False
        
        return self.orchestrator.register_engine(engine_type, engine, capabilities, priority)
    
    async def execute_command(self, command: SupremeCommand) -> SupremeCommandResult:
        """Execute a supreme command"""
        start_time = datetime.now()
        
        try:
            if not self.is_initialized:
                return SupremeCommandResult(
                    command_id=command.command_id,
                    status="failed",
                    result=None,
                    execution_time=0.0,
                    engines_used=[],
                    errors=["Interface not initialized"]
                )
            
            # Add to command history
            self.command_history.append(command)
            
            # Process command into orchestration request
            orchestration_request = self.command_processor.process_command(command)
            
            # Submit for orchestration
            request_id = await self.orchestrator.orchestrate_request(orchestration_request)
            
            if not request_id:
                return SupremeCommandResult(
                    command_id=command.command_id,
                    status="failed",
                    result=None,
                    execution_time=0.0,
                    engines_used=[],
                    errors=["Failed to submit orchestration request"]
                )
            
            # Wait for result
            timeout_seconds = command.timeout.total_seconds() if command.timeout else 300.0
            orchestration_result = await self.orchestrator.get_orchestration_result(
                request_id, timeout_seconds
            )
            
            if not orchestration_result:
                return SupremeCommandResult(
                    command_id=command.command_id,
                    status="timeout",
                    result=None,
                    execution_time=(datetime.now() - start_time).total_seconds(),
                    engines_used=[],
                    errors=["Request timed out"]
                )
            
            # Format result
            formatted_result = self.command_processor.format_result(
                orchestration_result, command.response_format
            )
            
            # Create command result
            command_result = SupremeCommandResult(
                command_id=command.command_id,
                status=orchestration_result.overall_status,
                result=formatted_result,
                execution_time=orchestration_result.execution_time,
                engines_used=list(orchestration_result.engine_results.keys()),
                errors=orchestration_result.errors,
                warnings=orchestration_result.warnings,
                metadata={
                    "orchestration_strategy": orchestration_request.strategy.value,
                    "required_engines": [e.value for e in orchestration_request.required_engines]
                }
            )
            
            # Add to result history
            self.result_history.append(command_result)
            
            return command_result
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Error executing command {command.command_id}: {e}")
            
            return SupremeCommandResult(
                command_id=command.command_id,
                status="failed",
                result=None,
                execution_time=execution_time,
                engines_used=[],
                errors=[str(e)]
            )
    
    async def analyze(self, data: Any, analysis_type: str = "comprehensive", 
                     **kwargs) -> SupremeCommandResult:
        """Perform analysis using supreme capabilities"""
        command = SupremeCommand(
            command_id=f"analyze_{datetime.now().isoformat()}",
            command_type=CommandType.ANALYZE,
            operation="analyze_data",
            parameters={
                "data": data,
                "analysis_type": analysis_type,
                **kwargs
            }
        )
        
        return await self.execute_command(command)
    
    async def optimize(self, target: str, parameters: Dict[str, Any], 
                      **kwargs) -> SupremeCommandResult:
        """Optimize a target using supreme capabilities"""
        command = SupremeCommand(
            command_id=f"optimize_{datetime.now().isoformat()}",
            command_type=CommandType.OPTIMIZE,
            operation="optimize_target",
            parameters={
                "target": target,
                "parameters": parameters,
                **kwargs
            }
        )
        
        return await self.execute_command(command)
    
    async def predict(self, data: Any, prediction_type: str = "forecast", 
                     **kwargs) -> SupremeCommandResult:
        """Make predictions using supreme capabilities"""
        command = SupremeCommand(
            command_id=f"predict_{datetime.now().isoformat()}",
            command_type=CommandType.PREDICT,
            operation="make_prediction",
            parameters={
                "data": data,
                "prediction_type": prediction_type,
                **kwargs
            }
        )
        
        return await self.execute_command(command)
    
    async def secure(self, resource: str, security_level: str = "high", 
                    **kwargs) -> SupremeCommandResult:
        """Secure a resource using supreme capabilities"""
        command = SupremeCommand(
            command_id=f"secure_{datetime.now().isoformat()}",
            command_type=CommandType.SECURE,
            operation="secure_resource",
            parameters={
                "resource": resource,
                "security_level": security_level,
                **kwargs
            }
        )
        
        return await self.execute_command(command)
    
    async def scale(self, target: str, scale_direction: str = "up", 
                   **kwargs) -> SupremeCommandResult:
        """Scale a target using supreme capabilities"""
        command = SupremeCommand(
            command_id=f"scale_{datetime.now().isoformat()}",
            command_type=CommandType.SCALE,
            operation="scale_target",
            parameters={
                "target": target,
                "scale_direction": scale_direction,
                **kwargs
            }
        )
        
        return await self.execute_command(command)
    
    def get_interface_status(self) -> Dict[str, Any]:
        """Get current interface status"""
        return {
            "is_initialized": self.is_initialized,
            "orchestrator_status": self.orchestrator.get_orchestration_status() if self.is_initialized else {},
            "command_history_count": len(self.command_history),
            "result_history_count": len(self.result_history),
            "engine_status": self.orchestrator.get_engine_status_summary() if self.is_initialized else {}
        }
    
    def get_command_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent command history"""
        recent_commands = self.command_history[-limit:] if limit > 0 else self.command_history
        
        return [
            {
                "command_id": cmd.command_id,
                "command_type": cmd.command_type.value,
                "operation": cmd.operation,
                "priority": cmd.priority,
                "timestamp": cmd.context.get("timestamp", "unknown")
            }
            for cmd in recent_commands
        ]
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        if not self.result_history:
            return {"message": "No execution history available"}
        
        total_commands = len(self.result_history)
        successful_commands = len([r for r in self.result_history if r.status == "completed"])
        
        execution_times = [r.execution_time for r in self.result_history]
        avg_execution_time = sum(execution_times) / len(execution_times) if execution_times else 0
        
        return {
            "total_commands": total_commands,
            "successful_commands": successful_commands,
            "success_rate": (successful_commands / total_commands) * 100 if total_commands > 0 else 0,
            "average_execution_time": avg_execution_time,
            "min_execution_time": min(execution_times) if execution_times else 0,
            "max_execution_time": max(execution_times) if execution_times else 0
        }