"""
Tests for Supreme Integration Hub
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta

from core.supreme.engines.integration_hub import (
    SupremeIntegrationHub, IntegrationConfig, ServiceConnection, 
    IntegrationRequest, IntegrationResponse, WorkflowStep, IntegrationWorkflow,
    IntegrationType, AuthType, ConnectionStatus
)
from core.supreme.base_supreme_engine import SupremeRequest


class TestSupremeIntegrationHub:
    
    @pytest.fixture
    def mock_config(self):
        return Mock(
            auto_scaling=True,
            max_concurrent_operations=10,
            operation_timeout=30.0
        )
    
    @pytest.fixture
    def integration_hub(self, mock_config):
        return SupremeIntegrationHub("test_integration_hub", mock_config)
    
    @pytest.fixture
    def sample_integration_config(self):
        return IntegrationConfig(
            service_id="test_service",
            service_name="Test Service",
            integration_type=IntegrationType.REST_API,
            base_url="https://api.test.com",
            auth_type=AuthType.BEARER_TOKEN,
            auth_config={"type": "bearer_token", "token": "test_token"}
        )
    
    @pytest.fixture
    def sample_service_connection(self, sample_integration_config):
        return ServiceConnection(
            connection_id="test_conn_123",
            config=sample_integration_config,
            status=ConnectionStatus.CONNECTED,
            last_used=datetime.now()
        )
    
    @pytest.mark.asyncio
    async def test_initialization(self, integration_hub):
        """Test integration hub initialization"""
        # Mock the initialization methods
        with patch.object(integration_hub, '_load_integration_data', new_callable=AsyncMock), \
             patch.object(integration_hub, '_initialize_builtin_connections', new_callable=AsyncMock):
            
            result = await integration_hub._initialize_engine()
            assert result is True
            assert len(integration_hub.builtin_services) > 0
            assert "github" in integration_hub.builtin_services
            assert "slack" in integration_hub.builtin_services
    
    @pytest.mark.asyncio
    async def test_connect_service_success(self, integration_hub):
        """Test successful service connection"""
        # Mock the test connection method
        with patch.object(integration_hub, '_test_service_connection', new_callable=AsyncMock) as mock_test:
            mock_test.return_value = {"success": True, "status_code": 200}
            
            with patch.object(integration_hub, '_save_integration_data', new_callable=AsyncMock):
                parameters = {
                    "service_id": "test_service",
                    "service_name": "Test Service",
                    "base_url": "https://api.test.com",
                    "auth": {"type": "bearer_token", "token": "test_token"}
                }
                
                result = await integration_hub._connect_service(parameters)
                
                assert result["operation"] == "connect_service"
                assert result["status"] == "connected"
                assert result["service_id"] == "test_service"
                assert "test_service" in integration_hub.service_connections
    
    @pytest.mark.asyncio
    async def test_connect_service_failure(self, integration_hub):
        """Test failed service connection"""
        # Mock the test connection method to fail
        with patch.object(integration_hub, '_test_service_connection', new_callable=AsyncMock) as mock_test:
            mock_test.return_value = {"success": False, "error": "Connection timeout"}
            
            parameters = {
                "service_id": "test_service",
                "base_url": "https://api.test.com",
                "auth": {"type": "bearer_token", "token": "invalid_token"}
            }
            
            result = await integration_hub._connect_service(parameters)
            
            assert result["operation"] == "connect_service"
            assert result["status"] == "connection_failed"
            assert "error" in result
    
    @pytest.mark.asyncio
    async def test_disconnect_service(self, integration_hub, sample_service_connection):
        """Test service disconnection"""
        # Add a connected service
        integration_hub.service_connections["test_service"] = sample_service_connection
        
        parameters = {"service_id": "test_service"}
        result = await integration_hub._disconnect_service(parameters)
        
        assert result["operation"] == "disconnect_service"
        assert result["status"] == "disconnected"
        assert "test_service" not in integration_hub.service_connections
    
    @pytest.mark.asyncio
    async def test_make_service_request_success(self, integration_hub, sample_service_connection):
        """Test successful service request"""
        # Add a connected service
        integration_hub.service_connections["test_service"] = sample_service_connection
        
        # Mock the request execution
        mock_response = IntegrationResponse(
            request_id="req_123",
            service_id="test_service",
            success=True,
            status_code=200,
            data={"message": "success"},
            response_time=0.5
        )
        
        with patch.object(integration_hub, '_execute_service_request', new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = mock_response
            
            parameters = {
                "service_id": "test_service",
                "method": "GET",
                "endpoint": "/users",
                "params": {"limit": 10}
            }
            
            result = await integration_hub._make_service_request(parameters)
            
            assert result["operation"] == "service_request"
            assert result["success"] is True
            assert result["status_code"] == 200
            assert result["data"]["message"] == "success"
    
    @pytest.mark.asyncio
    async def test_make_service_request_not_connected(self, integration_hub):
        """Test service request when service not connected"""
        parameters = {
            "service_id": "nonexistent_service",
            "method": "GET",
            "endpoint": "/users"
        }
        
        result = await integration_hub._make_service_request(parameters)
        
        assert result["operation"] == "service_request"
        assert "error" in result
        assert "not connected" in result["error"]
    
    @pytest.mark.asyncio
    async def test_create_workflow_success(self, integration_hub):
        """Test successful workflow creation"""
        with patch.object(integration_hub, '_validate_workflow', new_callable=AsyncMock) as mock_validate:
            mock_validate.return_value = {"valid": True}
            
            with patch.object(integration_hub, '_save_integration_data', new_callable=AsyncMock):
                parameters = {
                    "name": "Test Workflow",
                    "description": "A test workflow",
                    "steps": [
                        {
                            "step_id": "step1",
                            "service_id": "test_service",
                            "action": "request",
                            "parameters": {"method": "GET", "endpoint": "/data"}
                        },
                        {
                            "step_id": "step2",
                            "service_id": "test_service",
                            "action": "request",
                            "parameters": {"method": "POST", "endpoint": "/process"},
                            "depends_on": ["step1"]
                        }
                    ]
                }
                
                result = await integration_hub._create_integration_workflow(parameters)
                
                assert result["operation"] == "create_workflow"
                assert result["workflow_name"] == "Test Workflow"
                assert result["steps"] == 2
                assert len(integration_hub.integration_workflows) == 1
    
    @pytest.mark.asyncio
    async def test_create_workflow_validation_failure(self, integration_hub):
        """Test workflow creation with validation failure"""
        with patch.object(integration_hub, '_validate_workflow', new_callable=AsyncMock) as mock_validate:
            mock_validate.return_value = {"valid": False, "error": "Circular dependency detected"}
            
            parameters = {
                "name": "Invalid Workflow",
                "steps": [
                    {
                        "step_id": "step1",
                        "service_id": "test_service",
                        "action": "request",
                        "depends_on": ["step2"]
                    },
                    {
                        "step_id": "step2",
                        "service_id": "test_service",
                        "action": "request",
                        "depends_on": ["step1"]
                    }
                ]
            }
            
            result = await integration_hub._create_integration_workflow(parameters)
            
            assert result["operation"] == "create_workflow"
            assert "error" in result
            assert "validation failed" in result["error"]
    
    @pytest.mark.asyncio
    async def test_execute_workflow_success(self, integration_hub):
        """Test successful workflow execution"""
        # Create a test workflow
        workflow = IntegrationWorkflow(
            workflow_id="test_workflow",
            name="Test Workflow",
            description="Test",
            steps=[
                WorkflowStep(
                    step_id="step1",
                    service_id="test_service",
                    action="request",
                    parameters={"method": "GET", "endpoint": "/data"}
                )
            ],
            created_at=datetime.now()
        )
        integration_hub.integration_workflows["test_workflow"] = workflow
        
        # Mock workflow execution
        with patch.object(integration_hub, '_execute_workflow_steps', new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = {
                "success": True,
                "steps_executed": 1,
                "steps_failed": 0,
                "execution_time": 1.5,
                "results": {"step1": {"success": True, "data": "result"}}
            }
            
            parameters = {"workflow_id": "test_workflow"}
            result = await integration_hub._execute_integration_workflow(parameters)
            
            assert result["operation"] == "execute_workflow"
            assert result["success"] is True
            assert result["steps_executed"] == 1
            assert result["steps_failed"] == 0
    
    @pytest.mark.asyncio
    async def test_synchronize_data_success(self, integration_hub, sample_service_connection):
        """Test successful data synchronization"""
        # Add connected services
        integration_hub.service_connections["source_service"] = sample_service_connection
        integration_hub.service_connections["target_service"] = sample_service_connection
        
        # Mock sync operation
        with patch.object(integration_hub, '_sync_data_one_way', new_callable=AsyncMock) as mock_sync:
            mock_sync.return_value = {
                "success": True,
                "records_synced": 5,
                "source_response": {"data": [1, 2, 3, 4, 5]},
                "target_response": {"status": "created"}
            }
            
            parameters = {
                "source_service": "source_service",
                "target_service": "target_service",
                "data_mapping": {"field_mapping": {"id": "identifier"}},
                "mode": "one_way"
            }
            
            result = await integration_hub._synchronize_data(parameters)
            
            assert result["operation"] == "sync_data"
            assert result["success"] is True
            assert result["total_records_synced"] == 5
    
    @pytest.mark.asyncio
    async def test_get_integration_status_overall(self, integration_hub, sample_service_connection):
        """Test getting overall integration status"""
        # Add some test data
        integration_hub.service_connections["test_service"] = sample_service_connection
        integration_hub.request_history = [
            IntegrationResponse("req1", "test_service", True, 200, {}, response_time=0.5),
            IntegrationResponse("req2", "test_service", False, 500, error="Server error", response_time=1.0)
        ]
        
        parameters = {}
        result = await integration_hub._get_integration_status(parameters)
        
        assert result["operation"] == "integration_status"
        assert result["total_services"] == 1
        assert result["connected_services"] == 1
        assert result["total_requests"] == 2
        assert result["successful_requests"] == 1
        assert result["request_success_rate"] == 0.5
    
    @pytest.mark.asyncio
    async def test_get_integration_status_specific_service(self, integration_hub, sample_service_connection):
        """Test getting status for specific service"""
        integration_hub.service_connections["test_service"] = sample_service_connection
        
        parameters = {"service_id": "test_service"}
        result = await integration_hub._get_integration_status(parameters)
        
        assert result["operation"] == "integration_status"
        assert result["service_id"] == "test_service"
        assert result["status"] == "connected"
        assert "success_rate" in result
    
    def test_workflow_validation_circular_dependency(self, integration_hub):
        """Test workflow validation detects circular dependencies"""
        steps = [
            WorkflowStep("step1", "service1", "action1", {}, depends_on=["step2"]),
            WorkflowStep("step2", "service1", "action2", {}, depends_on=["step1"])
        ]
        
        has_cycle = integration_hub._has_circular_dependencies(steps)
        assert has_cycle is True
    
    def test_workflow_validation_no_circular_dependency(self, integration_hub):
        """Test workflow validation with valid dependencies"""
        steps = [
            WorkflowStep("step1", "service1", "action1", {}),
            WorkflowStep("step2", "service1", "action2", {}, depends_on=["step1"]),
            WorkflowStep("step3", "service1", "action3", {}, depends_on=["step2"])
        ]
        
        has_cycle = integration_hub._has_circular_dependencies(steps)
        assert has_cycle is False
    
    def test_topological_sort(self, integration_hub):
        """Test topological sorting of workflow steps"""
        steps = [
            WorkflowStep("step3", "service1", "action3", {}, depends_on=["step1", "step2"]),
            WorkflowStep("step1", "service1", "action1", {}),
            WorkflowStep("step2", "service1", "action2", {}, depends_on=["step1"])
        ]
        
        sorted_steps = integration_hub._topological_sort(steps)
        step_ids = [step.step_id for step in sorted_steps]
        
        # step1 should come first, step2 should come before step3
        assert step_ids.index("step1") < step_ids.index("step2")
        assert step_ids.index("step2") < step_ids.index("step3")
    
    def test_data_transformation(self, integration_hub):
        """Test data transformation with field mapping"""
        source_data = [
            {"id": 1, "name": "John", "email": "john@example.com"},
            {"id": 2, "name": "Jane", "email": "jane@example.com"}
        ]
        
        field_mapping = {"id": "identifier", "name": "full_name"}
        
        transformed_data = integration_hub._transform_data(source_data, field_mapping)
        
        assert len(transformed_data) == 2
        assert transformed_data[0]["identifier"] == 1
        assert transformed_data[0]["full_name"] == "John"
        assert transformed_data[0]["email"] == "john@example.com"  # Unmapped field preserved
    
    def test_parameter_reference_resolution(self, integration_hub):
        """Test parameter reference resolution"""
        params = {
            "user_id": "${step1.user_id}",
            "static_value": "test",
            "full_result": "${step2}"
        }
        
        previous_results = {
            "step1": {"user_id": 123, "name": "John"},
            "step2": {"status": "completed", "data": [1, 2, 3]}
        }
        
        resolved_params = integration_hub._resolve_parameter_references(params, previous_results)
        
        assert resolved_params["user_id"] == 123
        assert resolved_params["static_value"] == "test"
        assert resolved_params["full_result"] == {"status": "completed", "data": [1, 2, 3]}
    
    @pytest.mark.asyncio
    async def test_supported_operations(self, integration_hub):
        """Test getting supported operations"""
        operations = await integration_hub.get_supported_operations()
        
        expected_operations = [
            "connect_service", "disconnect_service", "make_request", "create_workflow",
            "execute_workflow", "sync_data", "manage_apis", "automate_process",
            "integration_status", "list_services", "test_connection"
        ]
        
        for operation in expected_operations:
            assert operation in operations
    
    @pytest.mark.asyncio
    async def test_execute_operation_routing(self, integration_hub):
        """Test operation routing in execute_operation"""
        # Test connect operation
        with patch.object(integration_hub, '_connect_service', new_callable=AsyncMock) as mock_connect:
            mock_connect.return_value = {"status": "connected"}
            
            request = SupremeRequest(
                request_id="test_req",
                operation="connect_service",
                parameters={"service_id": "test"}
            )
            
            result = await integration_hub._execute_operation(request)
            assert result["status"] == "connected"
            mock_connect.assert_called_once()
        
        # Test request operation
        with patch.object(integration_hub, '_make_service_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"success": True}
            
            request = SupremeRequest(
                request_id="test_req",
                operation="make_request",
                parameters={"service_id": "test"}
            )
            
            result = await integration_hub._execute_operation(request)
            assert result["success"] is True
            mock_request.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])