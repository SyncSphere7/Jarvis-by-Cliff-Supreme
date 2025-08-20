"""
Supreme Integration Hub Examples
Demonstrates universal connectivity and service integration capabilities.
"""

import asyncio
import json
from datetime import datetime

from core.supreme.engines.integration_hub import SupremeIntegrationHub
from core.supreme.base_supreme_engine import SupremeRequest


class IntegrationHubExamples:
    """Examples demonstrating Integration Hub capabilities"""
    
    def __init__(self):
        self.config = type('Config', (), {
            'auto_scaling': True,
            'max_concurrent_operations': 10,
            'operation_timeout': 30.0
        })()
        
        self.integration_hub = SupremeIntegrationHub("integration_hub", self.config)
    
    async def initialize(self):
        """Initialize the integration hub"""
        await self.integration_hub._initialize_engine()
        print("🔗 Supreme Integration Hub initialized")
    
    async def example_connect_to_services(self):
        """Example: Connect to multiple services"""
        print("\n=== Connecting to Services ===")
        
        # Connect to GitHub API
        github_request = SupremeRequest(
            request_id="connect_github",
            operation="connect_service",
            parameters={
                "service_id": "github",
                "service_name": "GitHub API",
                "base_url": "https://api.github.com",
                "auth": {
                    "type": "bearer_token",
                    "token": "your_github_token_here"
                },
                "headers": {
                    "Accept": "application/vnd.github.v3+json"
                }
            }
        )
        
        github_result = await self.integration_hub.execute_request(github_request)
        print(f"GitHub connection: {github_result.data.get('status', 'failed')}")
        
        # Connect to Slack API
        slack_request = SupremeRequest(
            request_id="connect_slack",
            operation="connect_service",
            parameters={
                "service_id": "slack",
                "service_name": "Slack API",
                "base_url": "https://slack.com/api",
                "auth": {
                    "type": "bearer_token",
                    "token": "your_slack_token_here"
                }
            }
        )
        
        slack_result = await self.integration_hub.execute_request(slack_request)
        print(f"Slack connection: {slack_result.data.get('status', 'failed')}")
        
        # Connect to custom REST API
        custom_request = SupremeRequest(
            request_id="connect_custom",
            operation="connect_service",
            parameters={
                "service_id": "custom_api",
                "service_name": "Custom REST API",
                "base_url": "https://api.example.com",
                "auth": {
                    "type": "api_key",
                    "api_key": "your_api_key_here"
                },
                "rate_limit": 100,
                "timeout": 15.0
            }
        )
        
        custom_result = await self.integration_hub.execute_request(custom_request)
        print(f"Custom API connection: {custom_result.data.get('status', 'failed')}")
    
    async def example_make_service_requests(self):
        """Example: Make requests to connected services"""
        print("\n=== Making Service Requests ===")
        
        # GitHub API request - Get user repositories
        github_repos_request = SupremeRequest(
            request_id="github_repos",
            operation="make_request",
            parameters={
                "service_id": "github",
                "method": "GET",
                "endpoint": "/user/repos",
                "params": {
                    "type": "owner",
                    "sort": "updated",
                    "per_page": 10
                }
            }
        )
        
        repos_result = await self.integration_hub.execute_request(github_repos_request)
        if repos_result.success:
            repos = repos_result.data.get('data', [])
            print(f"Found {len(repos)} repositories")
            for repo in repos[:3]:  # Show first 3
                print(f"  - {repo.get('name', 'Unknown')}: {repo.get('description', 'No description')}")
        
        # Slack API request - Post message
        slack_message_request = SupremeRequest(
            request_id="slack_message",
            operation="make_request",
            parameters={
                "service_id": "slack",
                "method": "POST",
                "endpoint": "/chat.postMessage",
                "data": {
                    "channel": "#general",
                    "text": "Hello from Jarvis Integration Hub! 🤖",
                    "username": "Jarvis"
                }
            }
        )
        
        message_result = await self.integration_hub.execute_request(slack_message_request)
        if message_result.success:
            print("Message sent to Slack successfully")
        else:
            print(f"Failed to send Slack message: {message_result.data.get('error', 'Unknown error')}")
    
    async def example_create_integration_workflow(self):
        """Example: Create a multi-service integration workflow"""
        print("\n=== Creating Integration Workflow ===")
        
        workflow_request = SupremeRequest(
            request_id="create_workflow",
            operation="create_workflow",
            parameters={
                "name": "GitHub to Slack Notification",
                "description": "Monitor GitHub repositories and notify Slack of new issues",
                "steps": [
                    {
                        "step_id": "fetch_issues",
                        "service_id": "github",
                        "action": "request",
                        "parameters": {
                            "method": "GET",
                            "endpoint": "/repos/owner/repo/issues",
                            "params": {
                                "state": "open",
                                "since": "${workflow.last_run}"
                            }
                        }
                    },
                    {
                        "step_id": "filter_new_issues",
                        "service_id": "github",
                        "action": "request",
                        "parameters": {
                            "method": "GET",
                            "endpoint": "/repos/owner/repo/issues/${fetch_issues.issue_id}"
                        },
                        "depends_on": ["fetch_issues"],
                        "condition": "${fetch_issues.data.length} > 0"
                    },
                    {
                        "step_id": "notify_slack",
                        "service_id": "slack",
                        "action": "request",
                        "parameters": {
                            "method": "POST",
                            "endpoint": "/chat.postMessage",
                            "data": {
                                "channel": "#dev-notifications",
                                "text": "New GitHub issue: ${filter_new_issues.title}\\n${filter_new_issues.html_url}",
                                "username": "GitHub Bot"
                            }
                        },
                        "depends_on": ["filter_new_issues"]
                    }
                ]
            }
        )
        
        workflow_result = await self.integration_hub.execute_request(workflow_request)
        if workflow_result.success:
            workflow_id = workflow_result.data.get('workflow_id')
            print(f"Created workflow: {workflow_id}")
            return workflow_id
        else:
            print(f"Failed to create workflow: {workflow_result.data.get('error', 'Unknown error')}")
            return None
    
    async def example_execute_workflow(self, workflow_id: str):
        """Example: Execute an integration workflow"""
        print("\n=== Executing Integration Workflow ===")
        
        if not workflow_id:
            print("No workflow ID provided")
            return
        
        execute_request = SupremeRequest(
            request_id="execute_workflow",
            operation="execute_workflow",
            parameters={
                "workflow_id": workflow_id,
                "parameters": {
                    "last_run": (datetime.now().isoformat())
                }
            }
        )
        
        execution_result = await self.integration_hub.execute_request(execute_request)
        if execution_result.success:
            result_data = execution_result.data
            print(f"Workflow executed successfully:")
            print(f"  - Steps executed: {result_data.get('steps_executed', 0)}")
            print(f"  - Steps failed: {result_data.get('steps_failed', 0)}")
            print(f"  - Execution time: {result_data.get('execution_time', 0):.2f}s")
        else:
            print(f"Workflow execution failed: {execution_result.data.get('error', 'Unknown error')}")
    
    async def example_data_synchronization(self):
        """Example: Synchronize data between services"""
        print("\n=== Data Synchronization ===")
        
        # Sync GitHub issues to custom tracking system
        sync_request = SupremeRequest(
            request_id="sync_data",
            operation="sync_data",
            parameters={
                "source_service": "github",
                "target_service": "custom_api",
                "data_mapping": {
                    "source_endpoint": "/repos/owner/repo/issues",
                    "target_endpoint": "/issues",
                    "target_method": "POST",
                    "field_mapping": {
                        "id": "github_id",
                        "title": "issue_title",
                        "body": "description",
                        "state": "status",
                        "created_at": "created_date",
                        "user.login": "reporter"
                    }
                },
                "mode": "one_way"
            }
        )
        
        sync_result = await self.integration_hub.execute_request(sync_request)
        if sync_result.success:
            result_data = sync_result.data
            print(f"Data synchronization completed:")
            print(f"  - Records synced: {result_data.get('total_records_synced', 0)}")
            print(f"  - Success: {result_data.get('success', False)}")
        else:
            print(f"Data synchronization failed: {sync_result.data.get('error', 'Unknown error')}")
    
    async def example_api_management(self):
        """Example: Manage API connections"""
        print("\n=== API Connection Management ===")
        
        # List all connections
        list_request = SupremeRequest(
            request_id="list_apis",
            operation="manage_apis",
            parameters={
                "action": "list"
            }
        )
        
        list_result = await self.integration_hub.execute_request(list_request)
        if list_result.success:
            connections = list_result.data.get('connections', [])
            print(f"Active connections: {len(connections)}")
            for conn in connections:
                print(f"  - {conn['service_name']}: {conn['status']} (Success rate: {conn['success_rate']:.2%})")
        
        # Test all connections
        test_request = SupremeRequest(
            request_id="test_apis",
            operation="manage_apis",
            parameters={
                "action": "test"
            }
        )
        
        test_result = await self.integration_hub.execute_request(test_request)
        if test_result.success:
            test_data = test_result.data
            print(f"Connection tests completed:")
            print(f"  - Total tested: {test_data.get('total_tested', 0)}")
            print(f"  - Successful: {test_data.get('successful_tests', 0)}")
            print(f"  - Success rate: {test_data.get('success_rate', 0):.2%}")
    
    async def example_automation_setup(self):
        """Example: Set up automation for integration processes"""
        print("\n=== Setting Up Automation ===")
        
        # Automate workflow execution
        workflow_automation_request = SupremeRequest(
            request_id="automate_workflow",
            operation="automate_process",
            parameters={
                "type": "workflow",
                "config": {
                    "workflow_id": "github_slack_workflow",
                    "schedule": "interval",
                    "interval_seconds": 3600  # Run every hour
                }
            }
        )
        
        workflow_automation_result = await self.integration_hub.execute_request(workflow_automation_request)
        if workflow_automation_result.success:
            print("Workflow automation configured - will run every hour")
        
        # Automate data synchronization
        sync_automation_request = SupremeRequest(
            request_id="automate_sync",
            operation="automate_process",
            parameters={
                "type": "sync",
                "config": {
                    "source_service": "github",
                    "target_service": "custom_api",
                    "sync_interval": 1800,  # Sync every 30 minutes
                    "data_mapping": {
                        "source_endpoint": "/repos/owner/repo/issues",
                        "target_endpoint": "/issues",
                        "field_mapping": {"id": "github_id", "title": "issue_title"}
                    }
                }
            }
        )
        
        sync_automation_result = await self.integration_hub.execute_request(sync_automation_request)
        if sync_automation_result.success:
            print("Data synchronization automation configured - will sync every 30 minutes")
        
        # Automate connection monitoring
        monitoring_request = SupremeRequest(
            request_id="automate_monitoring",
            operation="automate_process",
            parameters={
                "type": "monitoring",
                "config": {
                    "monitor_interval": 300,  # Check every 5 minutes
                    "auto_reconnect": True
                }
            }
        )
        
        monitoring_result = await self.integration_hub.execute_request(monitoring_request)
        if monitoring_result.success:
            print("Connection monitoring automation configured")
    
    async def example_integration_status(self):
        """Example: Get comprehensive integration status"""
        print("\n=== Integration Status ===")
        
        status_request = SupremeRequest(
            request_id="integration_status",
            operation="integration_status",
            parameters={}
        )
        
        status_result = await self.integration_hub.execute_request(status_request)
        if status_result.success:
            status_data = status_result.data
            print(f"Integration Hub Status:")
            print(f"  - Total services: {status_data.get('total_services', 0)}")
            print(f"  - Connected services: {status_data.get('connected_services', 0)}")
            print(f"  - Connection rate: {status_data.get('connection_rate', 0):.2%}")
            print(f"  - Total workflows: {status_data.get('total_workflows', 0)}")
            print(f"  - Total requests: {status_data.get('total_requests', 0)}")
            print(f"  - Request success rate: {status_data.get('request_success_rate', 0):.2%}")
            
            services = status_data.get('services', {})
            if services:
                print("  Service Details:")
                for service_id, service_info in services.items():
                    print(f"    - {service_info['name']}: {service_info['status']} "
                          f"(Success rate: {service_info['success_rate']:.2%})")
    
    async def run_all_examples(self):
        """Run all integration hub examples"""
        print("🚀 Starting Supreme Integration Hub Examples")
        
        await self.initialize()
        
        # Connect to services
        await self.example_connect_to_services()
        
        # Make service requests
        await self.example_make_service_requests()
        
        # Create and execute workflow
        workflow_id = await self.example_create_integration_workflow()
        if workflow_id:
            await self.example_execute_workflow(workflow_id)
        
        # Data synchronization
        await self.example_data_synchronization()
        
        # API management
        await self.example_api_management()
        
        # Automation setup
        await self.example_automation_setup()
        
        # Integration status
        await self.example_integration_status()
        
        print("\n✅ All Integration Hub examples completed!")


async def main():
    """Run the integration hub examples"""
    examples = IntegrationHubExamples()
    await examples.run_all_examples()


if __name__ == "__main__":
    asyncio.run(main())