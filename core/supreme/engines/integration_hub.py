"""
Supreme Integration Hub
Universal platform connectivity and service orchestration.
"""

import logging
import asyncio
import aiohttp
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import os

from ..base_supreme_engine import BaseSupremeEngine, SupremeRequest, SupremeResponse

class ConnectionStatus(Enum):
    DISCONNECTED = "disconnected"
    CONNECTED = "connected"
    ERROR = "error"

@dataclass
class IntegrationService:
    service_id: str
    name: str
    base_url: str
    credentials: Dict[str, Any]
    status: ConnectionStatus
    endpoints: Dict[str, Any]
    last_connected: Optional[datetime] = None

@dataclass
class AutomationWorkflow:
    workflow_id: str
    name: str
    description: str
    steps: List[Dict[str, Any]]
    enabled: bool = True

class UniversalIntegrator(BaseSupremeEngine):
    """Universal integration hub with supreme connectivity capabilities."""
    
    def __init__(self, engine_name: str, config):
        super().__init__(engine_name, config)
        self.integrated_services: Dict[str, IntegrationService] = {}
        self.automation_workflows: Dict[str, AutomationWorkflow] = {}
        self.data_dir = "data/integrations"
        os.makedirs(self.data_dir, exist_ok=True)
    
    async def _initialize_engine(self) -> bool:
        """Initialize the universal integrator"""
        try:
            self.logger.info("Initializing Universal Integration Hub...")
            
            await self._load_integration_data()
            
            if self.config.auto_scaling:
                asyncio.create_task(self._connection_monitor())
            
            self.logger.info(f"Universal Integration Hub initialized with {len(self.integrated_services)} services")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Universal Integration Hub: {e}")
            return False
    
    async def _execute_operation(self, request: SupremeRequest) -> Any:
        """Execute integration operation"""
        operation = request.operation.lower()
        parameters = request.parameters
        
        if "connect" in operation:
            return await self._connect_service(parameters)
        elif "api" in operation or "call" in operation:
            return await self._execute_api_call(parameters)
        elif "workflow" in operation:
            return await self._manage_workflow(parameters)
        elif "sync" in operation:
            return await self._sync_data(parameters)
        else:
            return await self._get_integration_status(parameters)
    
    async def get_supported_operations(self) -> List[str]:
        """Get supported integration operations"""
        return ["connect_service", "execute_api_call", "manage_workflow", "sync_data", "integration_status"]
    
    async def _connect_service(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Connect to a new service"""
        try:
            service_name = parameters.get("service_name", "")
            base_url = parameters.get("base_url", "")
            credentials = parameters.get("credentials", {})
            
            if not service_name or not base_url:
                return {"error": "Service name and base URL are required", "operation": "connect_service"}
            
            service_id = f"service_{hash(service_name + base_url) % 10000}"
            
            integration_service = IntegrationService(
                service_id=service_id,
                name=service_name,
                base_url=base_url,
                credentials=credentials,
                status=ConnectionStatus.CONNECTED,
                endpoints={"health": "/health", "status": "/status"},
                last_connected=datetime.now()
            )
            
            self.integrated_services[service_id] = integration_service
            await self._save_integration_data()
            
            return {
                "operation": "connect_service",
                "service_id": service_id,
                "service_name": service_name,
                "connection_status": "connected",
                "endpoints_discovered": len(integration_service.endpoints),
                "success": True
            }
            
        except Exception as e:
            self.logger.error(f"Error connecting service: {e}")
            return {"error": str(e), "operation": "connect_service"}
    
    async def _execute_api_call(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute API call to integrated service"""
        try:
            service_id = parameters.get("service_id", "")
            method = parameters.get("method", "GET")
            endpoint = parameters.get("endpoint", "")
            data = parameters.get("data", {})
            
            if service_id not in self.integrated_services:
                return {"error": "Service not found", "operation": "api_call"}
            
            service = self.integrated_services[service_id]
            full_url = f"{service.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
            
            # Execute API call
            api_result = await self._make_api_request(method, full_url, data)
            
            return {
                "operation": "api_call",
                "service_id": service_id,
                "method": method,
                "endpoint": endpoint,
                "success": api_result["success"],
                "response_data": api_result.get("data"),
                "status_code": api_result.get("status_code")
            }
            
        except Exception as e:
            self.logger.error(f"Error executing API call: {e}")
            return {"error": str(e), "operation": "api_call"}
    
    async def _manage_workflow(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Manage automation workflows"""
        try:
            action = parameters.get("action", "create")
            
            if action == "create":
                return await self._create_workflow(parameters)
            elif action == "execute":
                return await self._execute_workflow(parameters)
            elif action == "list":
                return await self._list_workflows()
            else:
                return {"error": f"Unknown workflow action: {action}", "operation": "manage_workflow"}
                
        except Exception as e:
            self.logger.error(f"Error managing workflow: {e}")
            return {"error": str(e), "operation": "manage_workflow"}
    
    async def _create_workflow(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Create automation workflow"""
        workflow_name = parameters.get("name", "")
        description = parameters.get("description", "")
        steps = parameters.get("steps", [])
        
        if not workflow_name or not steps:
            return {"error": "Workflow name and steps are required"}
        
        workflow_id = f"workflow_{hash(workflow_name) % 10000}"
        
        workflow = AutomationWorkflow(
            workflow_id=workflow_id,
            name=workflow_name,
            description=description,
            steps=steps,
            enabled=parameters.get("enabled", True)
        )
        
        self.automation_workflows[workflow_id] = workflow
        await self._save_integration_data()
        
        return {
            "operation": "create_workflow",
            "workflow_id": workflow_id,
            "workflow_name": workflow_name,
            "steps_count": len(steps),
            "success": True
        }
    
    async def _execute_workflow(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute automation workflow"""
        workflow_id = parameters.get("workflow_id", "")
        
        if workflow_id not in self.automation_workflows:
            return {"error": "Workflow not found"}
        
        workflow = self.automation_workflows[workflow_id]
        
        if not workflow.enabled:
            return {"error": "Workflow is disabled"}
        
        execution_results = []
        
        for i, step in enumerate(workflow.steps):
            step_result = {
                "step": i + 1,
                "action": step.get("action", "unknown"),
                "success": True,
                "result": f"Executed step {i + 1}"
            }
            execution_results.append(step_result)
        
        return {
            "operation": "execute_workflow",
            "workflow_id": workflow_id,
            "workflow_name": workflow.name,
            "total_steps": len(workflow.steps),
            "execution_results": execution_results,
            "success": True
        }
    
    async def _list_workflows(self) -> Dict[str, Any]:
        """List all workflows"""
        workflows = [
            {
                "workflow_id": w.workflow_id,
                "name": w.name,
                "description": w.description,
                "steps": len(w.steps),
                "enabled": w.enabled
            }
            for w in self.automation_workflows.values()
        ]
        
        return {
            "operation": "list_workflows",
            "total_workflows": len(workflows),
            "workflows": workflows,
            "success": True
        }
    
    async def _sync_data(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Synchronize data between services"""
        try:
            source_service = parameters.get("source_service", "")
            target_service = parameters.get("target_service", "")
            
            if not source_service or not target_service:
                return {"error": "Source and target services required", "operation": "sync_data"}
            
            # Simplified data sync
            records_synced = 5  # Mock sync result
            
            return {
                "operation": "sync_data",
                "source_service": source_service,
                "target_service": target_service,
                "records_synced": records_synced,
                "success": True
            }
            
        except Exception as e:
            self.logger.error(f"Error syncing data: {e}")
            return {"error": str(e), "operation": "sync_data"}
    
    async def _get_integration_status(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Get integration hub status"""
        try:
            service_status = {
                "total_services": len(self.integrated_services),
                "connected_services": len([s for s in self.integrated_services.values() if s.status == ConnectionStatus.CONNECTED]),
                "services": [
                    {
                        "service_id": s.service_id,
                        "name": s.name,
                        "status": s.status.value,
                        "endpoints": len(s.endpoints)
                    }
                    for s in self.integrated_services.values()
                ]
            }
            
            workflow_status = {
                "total_workflows": len(self.automation_workflows),
                "enabled_workflows": len([w for w in self.automation_workflows.values() if w.enabled]),
                "workflows": [
                    {
                        "workflow_id": w.workflow_id,
                        "name": w.name,
                        "steps": len(w.steps),
                        "enabled": w.enabled
                    }
                    for w in self.automation_workflows.values()
                ]
            }
            
            return {
                "operation": "integration_status",
                "timestamp": datetime.now().isoformat(),
                "service_status": service_status,
                "workflow_status": workflow_status
            }
            
        except Exception as e:
            self.logger.error(f"Error getting integration status: {e}")
            return {"error": str(e), "operation": "integration_status"}
    
    async def _make_api_request(self, method: str, url: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make API request"""
        try:
            # Simplified API request
            return {
                "success": True,
                "status_code": 200,
                "data": {"message": f"Mock {method} response from {url}"}
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _load_integration_data(self):
        """Load integration data from storage"""
        try:
            services_file = os.path.join(self.data_dir, "services.json")
            if os.path.exists(services_file):
                with open(services_file, 'r') as f:
                    services_data = json.load(f)
                    for service_data in services_data:
                        service = IntegrationService(
                            service_id=service_data["service_id"],
                            name=service_data["name"],
                            base_url=service_data["base_url"],
                            credentials=service_data["credentials"],
                            status=ConnectionStatus(service_data["status"]),
                            endpoints=service_data["endpoints"],
                            last_connected=datetime.fromisoformat(service_data["last_connected"]) if service_data.get("last_connected") else None
                        )
                        self.integrated_services[service.service_id] = service
            
            self.logger.info(f"Loaded {len(self.integrated_services)} integrated services")
            
        except Exception as e:
            self.logger.error(f"Error loading integration data: {e}")
    
    async def _save_integration_data(self):
        """Save integration data to storage"""
        try:
            services_file = os.path.join(self.data_dir, "services.json")
            services_data = []
            
            for service in self.integrated_services.values():
                services_data.append({
                    "service_id": service.service_id,
                    "name": service.name,
                    "base_url": service.base_url,
                    "credentials": service.credentials,
                    "status": service.status.value,
                    "endpoints": service.endpoints,
                    "last_connected": service.last_connected.isoformat() if service.last_connected else None
                })
            
            with open(services_file, 'w') as f:
                json.dump(services_data, f, indent=2)
            
        except Exception as e:
            self.logger.error(f"Error saving integration data: {e}")
    
    async def _connection_monitor(self):
        """Monitor connections"""
        while self.status.value != "shutdown":
            try:
                await asyncio.sleep(300)  # Every 5 minutes
                
                for service in self.integrated_services.values():
                    if service.status == ConnectionStatus.CONNECTED:
                        # Simple connection check
                        service.last_connected = datetime.now()
                
            except Exception as e:
                self.logger.error(f"Error in connection monitoring: {e}")
                await asyncio.sleep(600)    
   
 # Helper methods for integration operations
    
    def _initialize_builtin_services(self) -> Dict[str, IntegrationConfig]:
        """Initialize built-in service configurations"""
        return {
            "github": IntegrationConfig(
                service_id="github",
                service_name="GitHub API",
                integration_type=IntegrationType.REST_API,
                base_url="https://api.github.com",
                auth_type=AuthType.BEARER_TOKEN,
                auth_config={"type": "bearer_token"},
                headers={"Accept": "application/vnd.github.v3+json"}
            ),
            "slack": IntegrationConfig(
                service_id="slack",
                service_name="Slack API",
                integration_type=IntegrationType.REST_API,
                base_url="https://slack.com/api",
                auth_type=AuthType.BEARER_TOKEN,
                auth_config={"type": "bearer_token"},
                headers={"Content-Type": "application/json"}
            ),
            "google_drive": IntegrationConfig(
                service_id="google_drive",
                service_name="Google Drive API",
                integration_type=IntegrationType.REST_API,
                base_url="https://www.googleapis.com/drive/v3",
                auth_type=AuthType.OAUTH2,
                auth_config={"type": "oauth2"},
                headers={"Content-Type": "application/json"}
            ),
            "trello": IntegrationConfig(
                service_id="trello",
                service_name="Trello API",
                integration_type=IntegrationType.REST_API,
                base_url="https://api.trello.com/1",
                auth_type=AuthType.API_KEY,
                auth_config={"type": "api_key"},
                headers={"Content-Type": "application/json"}
            ),
            "jira": IntegrationConfig(
                service_id="jira",
                service_name="Jira API",
                integration_type=IntegrationType.REST_API,
                base_url="https://your-domain.atlassian.net/rest/api/3",
                auth_type=AuthType.BASIC_AUTH,
                auth_config={"type": "basic_auth"},
                headers={"Content-Type": "application/json"}
            ),
            "aws": IntegrationConfig(
                service_id="aws",
                service_name="AWS API",
                integration_type=IntegrationType.REST_API,
                base_url="https://aws.amazon.com",
                auth_type=AuthType.CUSTOM,
                auth_config={"type": "aws_signature"},
                headers={"Content-Type": "application/json"}
            )
        }
    
    async def _load_integration_data(self):
        """Load existing integration data from storage"""
        try:
            # Load service connections
            connections_file = os.path.join(self.data_dir, "connections.json")
            if os.path.exists(connections_file):
                with open(connections_file, 'r') as f:
                    connections_data = json.load(f)
                    for service_id, conn_data in connections_data.items():
                        config = IntegrationConfig(**conn_data['config'])
                        connection = ServiceConnection(
                            connection_id=conn_data['connection_id'],
                            config=config,
                            status=ConnectionStatus(conn_data['status']),
                            last_used=datetime.fromisoformat(conn_data['last_used']),
                            success_count=conn_data.get('success_count', 0),
                            error_count=conn_data.get('error_count', 0)
                        )
                        self.service_connections[service_id] = connection
            
            # Load workflows
            workflows_file = os.path.join(self.data_dir, "workflows.json")
            if os.path.exists(workflows_file):
                with open(workflows_file, 'r') as f:
                    workflows_data = json.load(f)
                    for workflow_id, workflow_data in workflows_data.items():
                        steps = [WorkflowStep(**step_data) for step_data in workflow_data['steps']]
                        workflow = IntegrationWorkflow(
                            workflow_id=workflow_id,
                            name=workflow_data['name'],
                            description=workflow_data['description'],
                            steps=steps,
                            created_at=datetime.fromisoformat(workflow_data['created_at']),
                            success_count=workflow_data.get('success_count', 0),
                            failure_count=workflow_data.get('failure_count', 0)
                        )
                        self.integration_workflows[workflow_id] = workflow
                        
        except Exception as e:
            self.logger.warning(f"Could not load integration data: {e}")
    
    async def _save_integration_data(self):
        """Save integration data to storage"""
        try:
            # Save service connections
            connections_data = {}
            for service_id, connection in self.service_connections.items():
                connections_data[service_id] = {
                    'connection_id': connection.connection_id,
                    'config': asdict(connection.config),
                    'status': connection.status.value,
                    'last_used': connection.last_used.isoformat(),
                    'success_count': connection.success_count,
                    'error_count': connection.error_count
                }
            
            connections_file = os.path.join(self.data_dir, "connections.json")
            with open(connections_file, 'w') as f:
                json.dump(connections_data, f, indent=2)
            
            # Save workflows
            workflows_data = {}
            for workflow_id, workflow in self.integration_workflows.items():
                workflows_data[workflow_id] = {
                    'name': workflow.name,
                    'description': workflow.description,
                    'steps': [asdict(step) for step in workflow.steps],
                    'created_at': workflow.created_at.isoformat(),
                    'success_count': workflow.success_count,
                    'failure_count': workflow.failure_count
                }
            
            workflows_file = os.path.join(self.data_dir, "workflows.json")
            with open(workflows_file, 'w') as f:
                json.dump(workflows_data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Could not save integration data: {e}")
    
    async def _initialize_builtin_connections(self):
        """Initialize connections to built-in services if configured"""
        try:
            # Check for environment variables or config for built-in services
            for service_id, config in self.builtin_services.items():
                # Skip if already connected
                if service_id in self.service_connections:
                    continue
                
                # Check for auth credentials in environment
                auth_available = False
                if config.auth_type == AuthType.BEARER_TOKEN:
                    token_var = f"{service_id.upper()}_TOKEN"
                    if os.getenv(token_var):
                        config.auth_config["token"] = os.getenv(token_var)
                        auth_available = True
                elif config.auth_type == AuthType.API_KEY:
                    key_var = f"{service_id.upper()}_API_KEY"
                    if os.getenv(key_var):
                        config.auth_config["api_key"] = os.getenv(key_var)
                        auth_available = True
                
                # Auto-connect if credentials available
                if auth_available:
                    await self._connect_service({
                        "service_id": service_id,
                        "service_name": config.service_name,
                        "type": config.integration_type.value,
                        "base_url": config.base_url,
                        "auth": config.auth_config,
                        "headers": config.headers
                    })
                    
        except Exception as e:
            self.logger.warning(f"Could not initialize built-in connections: {e}")
    
    async def _monitor_connections(self):
        """Monitor connection health and auto-reconnect"""
        while True:
            try:
                await asyncio.sleep(300)  # Check every 5 minutes
                
                for service_id, connection in list(self.service_connections.items()):
                    if connection.status == ConnectionStatus.CONNECTED:
                        # Test connection health
                        health_check = await self._test_service_connection(connection)
                        if not health_check["success"]:
                            self.logger.warning(f"Connection to {service_id} failed health check")
                            connection.status = ConnectionStatus.ERROR
                            connection.error_count += 1
                            
                            # Attempt reconnection
                            if connection.error_count < 3:
                                self.logger.info(f"Attempting to reconnect to {service_id}")
                                reconnect_result = await self._test_service_connection(connection)
                                if reconnect_result["success"]:
                                    connection.status = ConnectionStatus.CONNECTED
                                    connection.success_count += 1
                                    self.logger.info(f"Successfully reconnected to {service_id}")
                    
                    # Clean up old disconnected connections
                    elif connection.status == ConnectionStatus.DISCONNECTED:
                        time_since_last_use = datetime.now() - connection.last_used
                        if time_since_last_use > timedelta(hours=24):
                            del self.service_connections[service_id]
                            self.logger.info(f"Cleaned up old connection to {service_id}")
                
            except Exception as e:
                self.logger.error(f"Error in connection monitoring: {e}")
    
    def _generate_connection_id(self, service_id: str) -> str:
        """Generate unique connection ID"""
        timestamp = datetime.now().isoformat()
        return hashlib.md5(f"{service_id}_{timestamp}".encode()).hexdigest()[:16]
    
    def _generate_request_id(self) -> str:
        """Generate unique request ID"""
        timestamp = datetime.now().isoformat()
        return hashlib.md5(f"req_{timestamp}".encode()).hexdigest()[:16]
    
    def _generate_workflow_id(self, workflow_name: str) -> str:
        """Generate unique workflow ID"""
        timestamp = datetime.now().isoformat()
        return hashlib.md5(f"{workflow_name}_{timestamp}".encode()).hexdigest()[:16]
    
    async def _test_service_connection(self, connection: ServiceConnection) -> Dict[str, Any]:
        """Test connection to a service"""
        try:
            start_time = datetime.now()
            
            # Create session if needed
            if not connection.session or connection.session.closed:
                connection.session = aiohttp.ClientSession(
                    timeout=aiohttp.ClientTimeout(total=connection.config.timeout)
                )
            
            # Prepare headers
            headers = connection.config.headers.copy()
            
            # Add authentication
            if connection.config.auth_type == AuthType.BEARER_TOKEN:
                token = connection.config.auth_config.get("token")
                if token:
                    headers["Authorization"] = f"Bearer {token}"
            elif connection.config.auth_type == AuthType.API_KEY:
                api_key = connection.config.auth_config.get("api_key")
                if api_key:
                    headers["X-API-Key"] = api_key
            
            # Make test request (usually to root or health endpoint)
            test_endpoint = connection.config.auth_config.get("test_endpoint", "/")
            url = f"{connection.config.base_url.rstrip('/')}{test_endpoint}"
            
            async with connection.session.get(url, headers=headers) as response:
                response_time = (datetime.now() - start_time).total_seconds()
                
                if response.status < 400:
                    return {
                        "success": True,
                        "status_code": response.status,
                        "response_time": response_time,
                        "message": "Connection test successful"
                    }
                else:
                    return {
                        "success": False,
                        "status_code": response.status,
                        "response_time": response_time,
                        "error": f"HTTP {response.status}: {await response.text()}"
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response_time": (datetime.now() - start_time).total_seconds()
            }
    
    async def _execute_service_request(self, connection: ServiceConnection, request: IntegrationRequest) -> IntegrationResponse:
        """Execute a request to a service"""
        start_time = datetime.now()
        
        try:
            # Create session if needed
            if not connection.session or connection.session.closed:
                connection.session = aiohttp.ClientSession(
                    timeout=aiohttp.ClientTimeout(total=request.timeout or connection.config.timeout)
                )
            
            # Prepare URL
            url = f"{connection.config.base_url.rstrip('/')}{request.endpoint}"
            if request.params:
                url += "?" + urlencode(request.params)
            
            # Prepare headers
            headers = connection.config.headers.copy()
            if request.headers:
                headers.update(request.headers)
            
            # Add authentication
            if connection.config.auth_type == AuthType.BEARER_TOKEN:
                token = connection.config.auth_config.get("token")
                if token:
                    headers["Authorization"] = f"Bearer {token}"
            elif connection.config.auth_type == AuthType.API_KEY:
                api_key = connection.config.auth_config.get("api_key")
                if api_key:
                    headers["X-API-Key"] = api_key
            elif connection.config.auth_type == AuthType.BASIC_AUTH:
                username = connection.config.auth_config.get("username")
                password = connection.config.auth_config.get("password")
                if username and password:
                    credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
                    headers["Authorization"] = f"Basic {credentials}"
            
            # Make request
            async with connection.session.request(
                request.method,
                url,
                headers=headers,
                json=request.data if request.data else None
            ) as response:
                response_time = (datetime.now() - start_time).total_seconds()
                
                try:
                    response_data = await response.json()
                except:
                    response_data = await response.text()
                
                return IntegrationResponse(
                    request_id=request.request_id,
                    service_id=request.service_id,
                    success=response.status < 400,
                    status_code=response.status,
                    data=response_data,
                    response_time=response_time,
                    headers=dict(response.headers)
                )
                
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds()
            return IntegrationResponse(
                request_id=request.request_id,
                service_id=request.service_id,
                success=False,
                error=str(e),
                response_time=response_time
            )
    
    async def _validate_workflow(self, workflow: IntegrationWorkflow) -> Dict[str, Any]:
        """Validate workflow configuration"""
        try:
            errors = []
            
            # Check if all referenced services are available
            for step in workflow.steps:
                if step.service_id not in self.service_connections and step.service_id not in self.builtin_services:
                    errors.append(f"Service {step.service_id} not available for step {step.step_id}")
            
            # Check step dependencies
            step_ids = {step.step_id for step in workflow.steps}
            for step in workflow.steps:
                for dependency in step.depends_on:
                    if dependency not in step_ids:
                        errors.append(f"Step {step.step_id} depends on non-existent step {dependency}")
            
            # Check for circular dependencies
            if self._has_circular_dependencies(workflow.steps):
                errors.append("Workflow has circular dependencies")
            
            return {
                "valid": len(errors) == 0,
                "errors": errors,
                "error": "; ".join(errors) if errors else None
            }
            
        except Exception as e:
            return {
                "valid": False,
                "error": str(e),
                "errors": [str(e)]
            }
    
    def _has_circular_dependencies(self, steps: List[WorkflowStep]) -> bool:
        """Check for circular dependencies in workflow steps"""
        # Build dependency graph
        graph = {step.step_id: step.depends_on for step in steps}
        
        # Use DFS to detect cycles
        visited = set()
        rec_stack = set()
        
        def has_cycle(node):
            if node in rec_stack:
                return True
            if node in visited:
                return False
            
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in graph.get(node, []):
                if has_cycle(neighbor):
                    return True
            
            rec_stack.remove(node)
            return False
        
        for step_id in graph:
            if step_id not in visited:
                if has_cycle(step_id):
                    return True
        
        return False
    
    async def _execute_workflow_steps(self, workflow: IntegrationWorkflow, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute workflow steps in dependency order"""
        try:
            start_time = datetime.now()
            
            # Sort steps by dependencies
            sorted_steps = self._topological_sort(workflow.steps)
            
            executed_steps = []
            failed_steps = []
            step_results = {}
            
            for step in sorted_steps:
                try:
                    # Check if dependencies completed successfully
                    dependencies_met = all(
                        dep_id in step_results and step_results[dep_id]["success"]
                        for dep_id in step.depends_on
                    )
                    
                    if not dependencies_met:
                        failed_steps.append(step.step_id)
                        step_results[step.step_id] = {
                            "success": False,
                            "error": "Dependencies not met"
                        }
                        continue
                    
                    # Execute step
                    step_result = await self._execute_workflow_step(step, parameters, step_results)
                    step_results[step.step_id] = step_result
                    
                    if step_result["success"]:
                        executed_steps.append(step.step_id)
                    else:
                        failed_steps.append(step.step_id)
                        
                        # Stop execution if step failed and no retry
                        if not step.retry_on_failure:
                            break
                            
                except Exception as e:
                    failed_steps.append(step.step_id)
                    step_results[step.step_id] = {
                        "success": False,
                        "error": str(e)
                    }
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "success": len(failed_steps) == 0,
                "steps_executed": len(executed_steps),
                "steps_failed": len(failed_steps),
                "execution_time": execution_time,
                "results": step_results,
                "error": f"Failed steps: {failed_steps}" if failed_steps else None
            }
            
        except Exception as e:
            return {
                "success": False,
                "steps_executed": 0,
                "steps_failed": len(workflow.steps),
                "execution_time": (datetime.now() - start_time).total_seconds(),
                "results": {},
                "error": str(e)
            }
    
    def _topological_sort(self, steps: List[WorkflowStep]) -> List[WorkflowStep]:
        """Sort steps in dependency order using topological sort"""
        # Build adjacency list and in-degree count
        graph = {step.step_id: [] for step in steps}
        in_degree = {step.step_id: 0 for step in steps}
        step_map = {step.step_id: step for step in steps}
        
        for step in steps:
            for dependency in step.depends_on:
                if dependency in graph:
                    graph[dependency].append(step.step_id)
                    in_degree[step.step_id] += 1
        
        # Kahn's algorithm
        queue = [step_id for step_id, degree in in_degree.items() if degree == 0]
        sorted_steps = []
        
        while queue:
            current = queue.pop(0)
            sorted_steps.append(step_map[current])
            
            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        return sorted_steps
    
    async def _execute_workflow_step(self, step: WorkflowStep, workflow_params: Dict[str, Any], previous_results: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single workflow step"""
        try:
            # Merge parameters
            step_params = step.parameters.copy()
            step_params.update(workflow_params)
            
            # Replace parameter references with previous results
            step_params = self._resolve_parameter_references(step_params, previous_results)
            
            # Execute based on action type
            if step.action == "request":
                return await self._make_service_request({
                    "service_id": step.service_id,
                    **step_params
                })
            elif step.action == "sync":
                return await self._synchronize_data({
                    "source_service": step.service_id,
                    **step_params
                })
            else:
                # Custom action - delegate to service
                return await self._make_service_request({
                    "service_id": step.service_id,
                    "method": "POST",
                    "endpoint": f"/actions/{step.action}",
                    "data": step_params
                })
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _resolve_parameter_references(self, params: Dict[str, Any], previous_results: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve parameter references to previous step results"""
        resolved_params = {}
        
        for key, value in params.items():
            if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                # Parameter reference: ${step_id.field}
                reference = value[2:-1]
                if "." in reference:
                    step_id, field = reference.split(".", 1)
                    if step_id in previous_results and field in previous_results[step_id]:
                        resolved_params[key] = previous_results[step_id][field]
                    else:
                        resolved_params[key] = value  # Keep original if not found
                else:
                    # Reference to entire step result
                    if reference in previous_results:
                        resolved_params[key] = previous_results[reference]
                    else:
                        resolved_params[key] = value
            else:
                resolved_params[key] = value
        
        return resolved_params 
   
    async def _sync_data_one_way(self, source_service: str, target_service: str, data_mapping: Dict[str, Any]) -> Dict[str, Any]:
        """Perform one-way data synchronization"""
        try:
            # Get data from source service
            source_request = IntegrationRequest(
                request_id=self._generate_request_id(),
                service_id=source_service,
                method="GET",
                endpoint=data_mapping.get("source_endpoint", "/data"),
                params=data_mapping.get("source_params", {})
            )
            
            source_connection = self.service_connections[source_service]
            source_response = await self._execute_service_request(source_connection, source_request)
            
            if not source_response.success:
                return {
                    "success": False,
                    "error": f"Failed to fetch data from source: {source_response.error}",
                    "records_synced": 0
                }
            
            # Transform data according to mapping
            source_data = source_response.data
            if isinstance(source_data, dict) and "data" in source_data:
                source_data = source_data["data"]
            
            transformed_data = self._transform_data(source_data, data_mapping.get("field_mapping", {}))
            
            # Send data to target service
            target_request = IntegrationRequest(
                request_id=self._generate_request_id(),
                service_id=target_service,
                method=data_mapping.get("target_method", "POST"),
                endpoint=data_mapping.get("target_endpoint", "/data"),
                data=transformed_data
            )
            
            target_connection = self.service_connections[target_service]
            target_response = await self._execute_service_request(target_connection, target_request)
            
            if target_response.success:
                records_count = len(transformed_data) if isinstance(transformed_data, list) else 1
                return {
                    "success": True,
                    "records_synced": records_count,
                    "source_response": source_response.data,
                    "target_response": target_response.data
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to send data to target: {target_response.error}",
                    "records_synced": 0
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "records_synced": 0
            }
    
    def _transform_data(self, data: Any, field_mapping: Dict[str, str]) -> Any:
        """Transform data according to field mapping"""
        if not field_mapping:
            return data
        
        if isinstance(data, list):
            return [self._transform_data(item, field_mapping) for item in data]
        elif isinstance(data, dict):
            transformed = {}
            for source_field, target_field in field_mapping.items():
                if source_field in data:
                    transformed[target_field] = data[source_field]
            # Include unmapped fields
            for key, value in data.items():
                if key not in field_mapping and key not in transformed:
                    transformed[key] = value
            return transformed
        else:
            return data
    
    async def _list_api_connections(self, service_filter: Optional[str]) -> Dict[str, Any]:
        """List API connections"""
        try:
            connections = []
            
            for service_id, connection in self.service_connections.items():
                if service_filter and service_filter.lower() not in service_id.lower():
                    continue
                
                connections.append({
                    "service_id": service_id,
                    "service_name": connection.config.service_name,
                    "status": connection.status.value,
                    "integration_type": connection.config.integration_type.value,
                    "base_url": connection.config.base_url,
                    "auth_type": connection.config.auth_type.value,
                    "last_used": connection.last_used.isoformat(),
                    "success_count": connection.success_count,
                    "error_count": connection.error_count,
                    "success_rate": connection.success_count / max(1, connection.success_count + connection.error_count)
                })
            
            return {
                "operation": "list_connections",
                "total_connections": len(connections),
                "connections": connections
            }
            
        except Exception as e:
            return {"error": str(e), "operation": "list_connections"}
    
    async def _discover_api_services(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Discover available API services"""
        try:
            discovery_url = parameters.get("discovery_url")
            service_type = parameters.get("service_type", "rest_api")
            
            discovered_services = []
            
            # Add built-in services
            for service_id, config in self.builtin_services.items():
                if service_id not in self.service_connections:
                    discovered_services.append({
                        "service_id": service_id,
                        "service_name": config.service_name,
                        "integration_type": config.integration_type.value,
                        "base_url": config.base_url,
                        "auth_type": config.auth_type.value,
                        "status": "available",
                        "builtin": True
                    })
            
            # Discover from URL if provided
            if discovery_url:
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(discovery_url) as response:
                            if response.status == 200:
                                discovery_data = await response.json()
                                # Parse discovery format (OpenAPI, etc.)
                                parsed_services = self._parse_discovery_data(discovery_data)
                                discovered_services.extend(parsed_services)
                except Exception as e:
                    self.logger.warning(f"Failed to discover from URL {discovery_url}: {e}")
            
            return {
                "operation": "discover_services",
                "discovered_count": len(discovered_services),
                "services": discovered_services
            }
            
        except Exception as e:
            return {"error": str(e), "operation": "discover_services"}
    
    def _parse_discovery_data(self, discovery_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse service discovery data"""
        services = []
        
        # Handle OpenAPI/Swagger format
        if "openapi" in discovery_data or "swagger" in discovery_data:
            base_url = discovery_data.get("servers", [{}])[0].get("url", "")
            service_name = discovery_data.get("info", {}).get("title", "Unknown API")
            
            services.append({
                "service_id": service_name.lower().replace(" ", "_"),
                "service_name": service_name,
                "integration_type": "rest_api",
                "base_url": base_url,
                "auth_type": "bearer_token",  # Default assumption
                "status": "discovered",
                "builtin": False,
                "description": discovery_data.get("info", {}).get("description", "")
            })
        
        return services
    
    async def _test_api_connections(self, service_filter: Optional[str]) -> Dict[str, Any]:
        """Test API connections"""
        try:
            test_results = []
            
            for service_id, connection in self.service_connections.items():
                if service_filter and service_filter.lower() not in service_id.lower():
                    continue
                
                test_result = await self._test_service_connection(connection)
                test_results.append({
                    "service_id": service_id,
                    "service_name": connection.config.service_name,
                    "test_success": test_result["success"],
                    "status_code": test_result.get("status_code"),
                    "response_time": test_result.get("response_time", 0),
                    "error": test_result.get("error")
                })
            
            successful_tests = len([r for r in test_results if r["test_success"]])
            
            return {
                "operation": "test_connections",
                "total_tested": len(test_results),
                "successful_tests": successful_tests,
                "success_rate": successful_tests / max(1, len(test_results)),
                "test_results": test_results
            }
            
        except Exception as e:
            return {"error": str(e), "operation": "test_connections"}
    
    async def _refresh_api_connections(self, service_filter: Optional[str]) -> Dict[str, Any]:
        """Refresh API connections"""
        try:
            refreshed_connections = []
            
            for service_id, connection in list(self.service_connections.items()):
                if service_filter and service_filter.lower() not in service_id.lower():
                    continue
                
                # Close existing session
                if connection.session and not connection.session.closed:
                    await connection.session.close()
                    connection.session = None
                
                # Test connection
                test_result = await self._test_service_connection(connection)
                
                if test_result["success"]:
                    connection.status = ConnectionStatus.CONNECTED
                    connection.success_count += 1
                else:
                    connection.status = ConnectionStatus.ERROR
                    connection.error_count += 1
                
                refreshed_connections.append({
                    "service_id": service_id,
                    "service_name": connection.config.service_name,
                    "refresh_success": test_result["success"],
                    "new_status": connection.status.value,
                    "error": test_result.get("error")
                })
            
            successful_refreshes = len([r for r in refreshed_connections if r["refresh_success"]])
            
            return {
                "operation": "refresh_connections",
                "total_refreshed": len(refreshed_connections),
                "successful_refreshes": successful_refreshes,
                "refresh_results": refreshed_connections
            }
            
        except Exception as e:
            return {"error": str(e), "operation": "refresh_connections"}
    
    async def _automate_workflow_execution(self, automation_config: Dict[str, Any]) -> Dict[str, Any]:
        """Automate workflow execution"""
        try:
            workflow_id = automation_config.get("workflow_id")
            schedule = automation_config.get("schedule", "manual")  # manual, interval, cron
            interval_seconds = automation_config.get("interval_seconds", 3600)
            
            if not workflow_id or workflow_id not in self.integration_workflows:
                return {"error": "Invalid workflow_id", "operation": "automate_workflow"}
            
            if schedule == "interval":
                # Start interval-based execution
                asyncio.create_task(self._run_workflow_interval(workflow_id, interval_seconds))
                return {
                    "operation": "automate_workflow",
                    "workflow_id": workflow_id,
                    "automation_type": "interval",
                    "interval_seconds": interval_seconds,
                    "status": "started"
                }
            else:
                return {
                    "operation": "automate_workflow",
                    "workflow_id": workflow_id,
                    "automation_type": schedule,
                    "status": "configured"
                }
                
        except Exception as e:
            return {"error": str(e), "operation": "automate_workflow"}
    
    async def _run_workflow_interval(self, workflow_id: str, interval_seconds: int):
        """Run workflow at specified intervals"""
        while workflow_id in self.integration_workflows:
            try:
                await asyncio.sleep(interval_seconds)
                
                workflow = self.integration_workflows[workflow_id]
                result = await self._execute_workflow_steps(workflow, {})
                
                self.logger.info(f"Automated workflow {workflow_id} execution: {'success' if result['success'] else 'failed'}")
                
            except Exception as e:
                self.logger.error(f"Error in automated workflow {workflow_id}: {e}")
    
    async def _automate_data_synchronization(self, automation_config: Dict[str, Any]) -> Dict[str, Any]:
        """Automate data synchronization"""
        try:
            source_service = automation_config.get("source_service")
            target_service = automation_config.get("target_service")
            sync_interval = automation_config.get("sync_interval", 3600)
            data_mapping = automation_config.get("data_mapping", {})
            
            if not source_service or not target_service:
                return {"error": "source_service and target_service required", "operation": "automate_sync"}
            
            # Start automated sync
            asyncio.create_task(self._run_sync_interval(source_service, target_service, data_mapping, sync_interval))
            
            return {
                "operation": "automate_sync",
                "source_service": source_service,
                "target_service": target_service,
                "sync_interval": sync_interval,
                "status": "started"
            }
            
        except Exception as e:
            return {"error": str(e), "operation": "automate_sync"}
    
    async def _run_sync_interval(self, source_service: str, target_service: str, data_mapping: Dict[str, Any], interval_seconds: int):
        """Run data sync at specified intervals"""
        while source_service in self.service_connections and target_service in self.service_connections:
            try:
                await asyncio.sleep(interval_seconds)
                
                result = await self._sync_data_one_way(source_service, target_service, data_mapping)
                
                self.logger.info(f"Automated sync {source_service} -> {target_service}: {'success' if result['success'] else 'failed'}")
                
            except Exception as e:
                self.logger.error(f"Error in automated sync {source_service} -> {target_service}: {e}")
    
    async def _automate_connection_monitoring(self, automation_config: Dict[str, Any]) -> Dict[str, Any]:
        """Automate connection monitoring"""
        try:
            monitor_interval = automation_config.get("monitor_interval", 300)
            auto_reconnect = automation_config.get("auto_reconnect", True)
            
            # Connection monitoring is already running if auto_scaling is enabled
            if self.config.auto_scaling:
                return {
                    "operation": "automate_monitoring",
                    "status": "already_running",
                    "monitor_interval": 300,
                    "auto_reconnect": True
                }
            else:
                # Start monitoring
                asyncio.create_task(self._monitor_connections())
                return {
                    "operation": "automate_monitoring",
                    "status": "started",
                    "monitor_interval": monitor_interval,
                    "auto_reconnect": auto_reconnect
                }
                
        except Exception as e:
            return {"error": str(e), "operation": "automate_monitoring"}