"""
Tests for Supreme Workflow Automator
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta

from core.supreme.engines.workflow_automator import (
    SupremeWorkflowAutomator, WorkflowDefinition, WorkflowExecution, WorkflowTrigger, WorkflowAction,
    AutomationOpportunity, WorkflowTriggerType, WorkflowActionType, WorkflowStatus
)
from core.supreme.base_supreme_engine import SupremeRequest


class TestSupremeWorkflowAutomator:
    
    @pytest.fixture
    def mock_config(self):
        return Mock(
            auto_scaling=True,
            max_concurrent_operations=10,
            operation_timeout=30.0
        )
    
    @pytest.fixture
    def workflow_automator(self, mock_config):
        return SupremeWorkflowAutomator("test_workflow_automator", mock_config)
    
    @pytest.fixture
    def sample_workflow_definition(self):
        triggers = [
            WorkflowTrigger(
                trigger_id="trigger1",
                trigger_type=WorkflowTriggerType.MANUAL,
                trigger_config={}
            )
        ]
        
        actions = [
            WorkflowAction(
                action_id="action1",
                action_type=WorkflowActionType.API_CALL,
                action_config={
                    "method": "GET",
                    "url": "https://api.example.com/data"
                }
            ),
            WorkflowAction(
                action_id="action2",
                action_type=WorkflowActionType.EMAIL_SEND,
                action_config={
                    "to": "user@example.com",
                    "subject": "Workflow Complete"
                },
                depends_on=["action1"]
            )
        ]
        
        return WorkflowDefinition(
            workflow_id="test_workflow",
            name="Test Workflow",
            description="A test workflow",
            version="1.0.0",
            triggers=triggers,
            actions=actions
        )
    
    @pytest.mark.asyncio
    async def test_initialization(self, workflow_automator):
        """Test workflow automator initialization"""
        with patch.object(workflow_automator, '_load_workflow_data', new_callable=AsyncMock), \
             patch.object(workflow_automator, '_run_workflow_scheduler', new_callable=AsyncMock), \
             patch.object(workflow_automator, '_continuous_opportunity_discovery', new_callable=AsyncMock):
            
            result = await workflow_automator._initialize_engine()
            assert result is True
            assert len(workflow_automator.workflow_templates) > 0
            assert "api_monitoring" in workflow_automator.workflow_templates
    
    @pytest.mark.asyncio
    async def test_create_workflow_success(self, workflow_automator):
        """Test successful workflow creation"""
        with patch.object(workflow_automator, '_validate_workflow', new_callable=AsyncMock) as mock_validate:
            mock_validate.return_value = {"valid": True}
            
            with patch.object(workflow_automator, '_setup_workflow_triggers', new_callable=AsyncMock), \
                 patch.object(workflow_automator, '_save_workflow_data', new_callable=AsyncMock):
                
                parameters = {
                    "name": "Test Workflow",
                    "description": "A test workflow",
                    "triggers": [
                        {
                            "trigger_id": "trigger1",
                            "type": "manual",
                            "config": {}
                        }
                    ],
                    "actions": [
                        {
                            "action_id": "action1",
                            "type": "api_call",
                            "config": {
                                "method": "GET",
                                "url": "https://api.example.com"
                            }
                        }
                    ]
                }
                
                result = await workflow_automator._create_workflow(parameters)
                
                assert result["operation"] == "create_workflow"
                assert result["workflow_name"] == "Test Workflow"
                assert result["triggers"] == 1
                assert result["actions"] == 1
                assert len(workflow_automator.workflow_definitions) == 1
    
    @pytest.mark.asyncio
    async def test_create_workflow_validation_failure(self, workflow_automator):
        """Test workflow creation with validation failure"""
        with patch.object(workflow_automator, '_validate_workflow', new_callable=AsyncMock) as mock_validate:
            mock_validate.return_value = {"valid": False, "error": "Invalid workflow configuration"}
            
            parameters = {
                "name": "Invalid Workflow",
                "actions": []  # Empty actions should cause validation failure
            }
            
            result = await workflow_automator._create_workflow(parameters)
            
            assert result["operation"] == "create_workflow"
            assert "error" in result
            assert "validation failed" in result["error"]
    
    @pytest.mark.asyncio
    async def test_execute_workflow_success(self, workflow_automator, sample_workflow_definition):
        """Test successful workflow execution"""
        # Add workflow to automator
        workflow_automator.workflow_definitions["test_workflow"] = sample_workflow_definition
        
        # Mock workflow execution
        with patch.object(workflow_automator, '_execute_workflow_actions', new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = {
                "success": True,
                "actions_executed": 2,
                "actions_failed": 0,
                "execution_time": 1.5,
                "results": {"action1": {"success": True}, "action2": {"success": True}}
            }
            
            parameters = {"workflow_id": "test_workflow"}
            result = await workflow_automator._execute_workflow(parameters)
            
            assert result["operation"] == "execute_workflow"
            assert result["success"] is True
            assert result["actions_executed"] == 2
            assert result["actions_failed"] == 0
    
    @pytest.mark.asyncio
    async def test_execute_workflow_not_found(self, workflow_automator):
        """Test workflow execution when workflow not found"""
        parameters = {"workflow_id": "nonexistent_workflow"}
        result = await workflow_automator._execute_workflow(parameters)
        
        assert result["operation"] == "execute_workflow"
        assert "error" in result
        assert "not found" in result["error"]
    
    @pytest.mark.asyncio
    async def test_schedule_workflow_success(self, workflow_automator, sample_workflow_definition):
        """Test successful workflow scheduling"""
        # Add workflow to automator
        workflow_automator.workflow_definitions["test_workflow"] = sample_workflow_definition
        
        with patch.object(workflow_automator, '_validate_schedule_config') as mock_validate:
            mock_validate.return_value = {"valid": True}
            
            with patch.object(workflow_automator, '_save_workflow_data', new_callable=AsyncMock):
                parameters = {
                    "workflow_id": "test_workflow",
                    "schedule_type": "interval",
                    "schedule_config": {"interval": 3600}
                }
                
                result = await workflow_automator._schedule_workflow(parameters)
                
                assert result["operation"] == "schedule_workflow"
                assert result["workflow_id"] == "test_workflow"
                assert result["schedule_type"] == "interval"
                assert len(workflow_automator.scheduled_workflows) == 1
    
    @pytest.mark.asyncio
    async def test_monitor_workflows(self, workflow_automator):
        """Test workflow monitoring"""
        # Add some mock execution history
        execution = WorkflowExecution(
            execution_id="exec1",
            workflow_id="test_workflow",
            status=WorkflowStatus.COMPLETED,
            started_at=datetime.now() - timedelta(hours=1),
            completed_at=datetime.now() - timedelta(minutes=30),
            records_processed=100,
            records_synced=95,
            records_failed=5
        )
        workflow_automator.execution_history.append(execution)
        
        parameters = {"time_range": "24h"}
        result = await workflow_automator._monitor_workflows(parameters)
        
        assert result["operation"] == "monitor_workflows"
        assert result["summary"]["total_executions"] == 1
        assert result["summary"]["successful_executions"] == 1
        assert result["summary"]["failed_executions"] == 0
    
    @pytest.mark.asyncio
    async def test_discover_automation_opportunities(self, workflow_automator):
        """Test automation opportunity discovery"""
        with patch.object(workflow_automator, '_analyze_workflow_patterns', new_callable=AsyncMock) as mock_analyze:
            mock_opportunities = [
                AutomationOpportunity(
                    opportunity_id="opp1",
                    title="API Monitoring Automation",
                    description="Automate API health monitoring",
                    confidence_score=0.85,
                    potential_savings={"time_saved_hours": 10, "cost_saved_dollars": 500}
                )
            ]
            mock_analyze.return_value = mock_opportunities
            
            parameters = {
                "data_sources": ["workflow_patterns"],
                "analysis_period": "30d",
                "min_confidence": 0.7
            }
            
            result = await workflow_automator._discover_automation_opportunities(parameters)
            
            assert result["operation"] == "discover_opportunities"
            assert result["qualified_opportunities"] == 1
            assert len(result["opportunities"]) == 1
            assert result["opportunities"][0]["title"] == "API Monitoring Automation"
    
    @pytest.mark.asyncio
    async def test_generate_workflow_from_template(self, workflow_automator):
        """Test workflow generation from template"""
        with patch.object(workflow_automator, '_generate_from_template', new_callable=AsyncMock) as mock_generate:
            mock_workflow = WorkflowDefinition(
                workflow_id="generated_workflow",
                name="Generated Workflow",
                description="Generated from template",
                version="1.0.0",
                triggers=[],
                actions=[]
            )
            mock_generate.return_value = mock_workflow
            
            with patch.object(workflow_automator, '_validate_workflow', new_callable=AsyncMock) as mock_validate:
                mock_validate.return_value = {"valid": True}
                
                with patch.object(workflow_automator, '_save_workflow_data', new_callable=AsyncMock):
                    parameters = {
                        "pattern_type": "template",
                        "pattern_source": "api_monitoring",
                        "name": "Generated Workflow"
                    }
                    
                    result = await workflow_automator._generate_workflow_from_pattern(parameters)
                    
                    assert result["operation"] == "generate_workflow"
                    assert result["workflow_name"] == "Generated Workflow"
                    assert result["pattern_type"] == "template"
    
    @pytest.mark.asyncio
    async def test_manage_workflow_triggers_list(self, workflow_automator, sample_workflow_definition):
        """Test listing workflow triggers"""
        # Add workflow to automator
        workflow_automator.workflow_definitions["test_workflow"] = sample_workflow_definition
        
        parameters = {
            "action": "list",
            "workflow_id": "test_workflow"
        }
        
        result = await workflow_automator._manage_workflow_triggers(parameters)
        
        assert result["operation"] == "manage_triggers"
        assert result["action"] == "list"
        assert result["workflow_id"] == "test_workflow"
        assert len(result["triggers"]) == 1
        assert result["triggers"][0]["trigger_id"] == "trigger1"
    
    @pytest.mark.asyncio
    async def test_manage_workflow_triggers_add(self, workflow_automator, sample_workflow_definition):
        """Test adding workflow trigger"""
        # Add workflow to automator
        workflow_automator.workflow_definitions["test_workflow"] = sample_workflow_definition
        
        with patch.object(workflow_automator, '_setup_trigger', new_callable=AsyncMock), \
             patch.object(workflow_automator, '_save_workflow_data', new_callable=AsyncMock):
            
            parameters = {
                "action": "add",
                "workflow_id": "test_workflow",
                "trigger_config": {
                    "trigger_id": "trigger2",
                    "type": "scheduled",
                    "config": {"interval": 3600}
                }
            }
            
            result = await workflow_automator._manage_workflow_triggers(parameters)
            
            assert result["operation"] == "manage_triggers"
            assert result["action"] == "add"
            assert result["success"] is True
            assert len(sample_workflow_definition.triggers) == 2
    
    @pytest.mark.asyncio
    async def test_get_workflow_status_specific(self, workflow_automator, sample_workflow_definition):
        """Test getting status for specific workflow"""
        # Add workflow to automator
        workflow_automator.workflow_definitions["test_workflow"] = sample_workflow_definition
        
        # Add some execution history
        execution = WorkflowExecution(
            execution_id="exec1",
            workflow_id="test_workflow",
            status=WorkflowStatus.COMPLETED,
            started_at=datetime.now(),
            records_processed=100
        )
        workflow_automator.execution_history.append(execution)
        
        parameters = {"workflow_id": "test_workflow"}
        result = await workflow_automator._get_workflow_status(parameters)
        
        assert result["operation"] == "workflow_status"
        assert result["workflow_id"] == "test_workflow"
        assert result["workflow_name"] == "Test Workflow"
        assert result["triggers"] == 1
        assert result["actions"] == 2
        assert result["execution_stats"]["total_executions"] == 1
    
    @pytest.mark.asyncio
    async def test_get_workflow_status_overall(self, workflow_automator, sample_workflow_definition):
        """Test getting overall workflow status"""
        # Add workflow to automator
        workflow_automator.workflow_definitions["test_workflow"] = sample_workflow_definition
        
        parameters = {}
        result = await workflow_automator._get_workflow_status(parameters)
        
        assert result["operation"] == "workflow_status"
        assert result["total_workflows"] == 1
        assert result["scheduled_workflows"] == 0
        assert "workflows" in result
        assert "test_workflow" in result["workflows"]
    
    def test_workflow_validation_success(self, workflow_automator, sample_workflow_definition):
        """Test successful workflow validation"""
        result = asyncio.run(workflow_automator._validate_workflow(sample_workflow_definition))
        
        assert result["valid"] is True
        assert len(result["errors"]) == 0
    
    def test_workflow_validation_circular_dependency(self, workflow_automator):
        """Test workflow validation with circular dependencies"""
        actions = [
            WorkflowAction("action1", WorkflowActionType.API_CALL, {}, depends_on=["action2"]),
            WorkflowAction("action2", WorkflowActionType.API_CALL, {}, depends_on=["action1"])
        ]
        
        has_cycle = workflow_automator._has_circular_dependencies(actions)
        assert has_cycle is True
    
    def test_workflow_validation_no_circular_dependency(self, workflow_automator):
        """Test workflow validation without circular dependencies"""
        actions = [
            WorkflowAction("action1", WorkflowActionType.API_CALL, {}),
            WorkflowAction("action2", WorkflowActionType.API_CALL, {}, depends_on=["action1"]),
            WorkflowAction("action3", WorkflowActionType.API_CALL, {}, depends_on=["action2"])
        ]
        
        has_cycle = workflow_automator._has_circular_dependencies(actions)
        assert has_cycle is False
    
    def test_schedule_validation_interval(self, workflow_automator):
        """Test schedule validation for interval type"""
        result = workflow_automator._validate_schedule_config("interval", {"interval": 3600})
        assert result["valid"] is True
        
        result = workflow_automator._validate_schedule_config("interval", {})
        assert result["valid"] is False
        assert "missing 'interval' parameter" in result["error"]
    
    def test_schedule_validation_cron(self, workflow_automator):
        """Test schedule validation for cron type"""
        result = workflow_automator._validate_schedule_config("cron", {"cron": "0 0 * * *"})
        assert result["valid"] is True
        
        result = workflow_automator._validate_schedule_config("cron", {"cron": "invalid"})
        assert result["valid"] is False
        assert "must have 5 parts" in result["error"]
    
    @pytest.mark.asyncio
    async def test_supported_operations(self, workflow_automator):
        """Test getting supported operations"""
        operations = await workflow_automator.get_supported_operations()
        
        expected_operations = [
            "create_workflow", "execute_workflow", "schedule_workflow", "monitor_workflows",
            "optimize_workflow", "discover_opportunities", "generate_workflow", "manage_triggers",
            "workflow_status", "list_workflows", "cancel_workflow"
        ]
        
        for operation in expected_operations:
            assert operation in operations
    
    @pytest.mark.asyncio
    async def test_execute_operation_routing(self, workflow_automator):
        """Test operation routing in execute_operation"""
        # Test create workflow operation
        with patch.object(workflow_automator, '_create_workflow', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = {"workflow_id": "test"}
            
            request = SupremeRequest(
                request_id="test_req",
                operation="create_workflow",
                parameters={"name": "test"}
            )
            
            result = await workflow_automator._execute_operation(request)
            assert result["workflow_id"] == "test"
            mock_create.assert_called_once()
        
        # Test execute workflow operation
        with patch.object(workflow_automator, '_execute_workflow', new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = {"success": True}
            
            request = SupremeRequest(
                request_id="test_req",
                operation="execute_workflow",
                parameters={"workflow_id": "test"}
            )
            
            result = await workflow_automator._execute_operation(request)
            assert result["success"] is True
            mock_execute.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])