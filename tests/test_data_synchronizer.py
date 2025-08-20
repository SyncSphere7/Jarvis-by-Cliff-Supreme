"""
Tests for Supreme Data Synchronizer
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta

from core.supreme.engines.data_synchronizer import (
    SupremeDataSynchronizer, SyncConfiguration, SyncExecution, DataSource, SyncRule, FieldMapping,
    DataConflict, SyncDirection, SyncStrategy, SyncStatus, ConflictResolution
)
from core.supreme.base_supreme_engine import SupremeRequest


class TestSupremeDataSynchronizer:
    
    @pytest.fixture
    def mock_config(self):
        return Mock(
            auto_scaling=True,
            max_concurrent_operations=10,
            operation_timeout=30.0
        )
    
    @pytest.fixture
    def data_synchronizer(self, mock_config):
        return SupremeDataSynchronizer("test_data_synchronizer", mock_config)
    
    @pytest.fixture
    def sample_data_sources(self):
        return [
            DataSource(
                source_id="source1",
                source_name="Database A",
                source_type="database",
                connection_config={"host": "db1.example.com", "port": 5432}
            ),
            DataSource(
                source_id="source2",
                source_name="API B",
                source_type="api",
                connection_config={"base_url": "https://api.example.com"}
            )
        ]
    
    @pytest.fixture
    def sample_sync_configuration(self, sample_data_sources):
        field_mappings = [
            FieldMapping(
                source_field="user_id",
                target_field="id",
                required=True
            ),
            FieldMapping(
                source_field="user_name",
                target_field="name",
                transformation="trim"
            )
        ]
        
        sync_rules = [
            SyncRule(
                rule_id="rule1",
                name="User Sync Rule",
                description="Synchronize user data",
                field_mappings=field_mappings
            )
        ]
        
        return SyncConfiguration(
            sync_id="test_sync",
            name="Test Sync",
            description="A test synchronization",
            sources=sample_data_sources,
            sync_direction=SyncDirection.ONE_WAY,
            sync_strategy=SyncStrategy.OVERWRITE,
            sync_rules=sync_rules
        )
    
    @pytest.mark.asyncio
    async def test_initialization(self, data_synchronizer):
        """Test data synchronizer initialization"""
        with patch.object(data_synchronizer, '_load_sync_data', new_callable=AsyncMock), \
             patch.object(data_synchronizer, '_run_sync_scheduler', new_callable=AsyncMock), \
             patch.object(data_synchronizer, '_monitor_data_conflicts', new_callable=AsyncMock):
            
            result = await data_synchronizer._initialize_engine()
            assert result is True
            assert len(data_synchronizer.transformation_functions) > 0
            assert "uppercase" in data_synchronizer.transformation_functions
    
    @pytest.mark.asyncio
    async def test_create_sync_configuration_success(self, data_synchronizer):
        """Test successful sync configuration creation"""
        with patch.object(data_synchronizer, '_validate_sync_configuration', new_callable=AsyncMock) as mock_validate:
            mock_validate.return_value = {"valid": True}
            
            with patch.object(data_synchronizer, '_save_sync_data', new_callable=AsyncMock):
                parameters = {
                    "name": "Test Sync",
                    "description": "A test synchronization",
                    "sources": [
                        {
                            "source_id": "source1",
                            "name": "Database A",
                            "type": "database",
                            "connection": {"host": "db1.example.com"}
                        },
                        {
                            "source_id": "source2",
                            "name": "API B",
                            "type": "api",
                            "connection": {"base_url": "https://api.example.com"}
                        }
                    ],
                    "direction": "one_way",
                    "strategy": "overwrite",
                    "rules": [
                        {
                            "rule_id": "rule1",
                            "name": "User Sync Rule",
                            "field_mappings": [
                                {
                                    "source_field": "user_id",
                                    "target_field": "id",
                                    "required": True
                                }
                            ]
                        }
                    ]
                }
                
                result = await data_synchronizer._create_sync_configuration(parameters)
                
                assert result["operation"] == "create_sync"
                assert result["sync_name"] == "Test Sync"
                assert result["sources"] == 2
                assert result["rules"] == 1
                assert len(data_synchronizer.sync_configurations) == 1
    
    @pytest.mark.asyncio
    async def test_create_sync_configuration_validation_failure(self, data_synchronizer):
        """Test sync configuration creation with validation failure"""
        with patch.object(data_synchronizer, '_validate_sync_configuration', new_callable=AsyncMock) as mock_validate:
            mock_validate.return_value = {"valid": False, "error": "Invalid sync configuration"}
            
            parameters = {
                "name": "Invalid Sync",
                "sources": [{"source_id": "source1"}]  # Only one source should fail validation
            }
            
            result = await data_synchronizer._create_sync_configuration(parameters)
            
            assert result["operation"] == "create_sync"
            assert "error" in result
            assert "validation failed" in result["error"]
    
    @pytest.mark.asyncio
    async def test_execute_synchronization_success(self, data_synchronizer, sample_sync_configuration):
        """Test successful synchronization execution"""
        # Add sync configuration to synchronizer
        data_synchronizer.sync_configurations["test_sync"] = sample_sync_configuration
        
        # Mock synchronization execution
        with patch.object(data_synchronizer, '_perform_synchronization', new_callable=AsyncMock) as mock_perform:
            mock_perform.return_value = {
                "success": True,
                "records_processed": 100,
                "records_synced": 95,
                "records_failed": 5,
                "conflicts_detected": 2,
                "execution_time": 2.5,
                "details": {"source_source2": {"records_processed": 100}}
            }
            
            parameters = {"sync_id": "test_sync"}
            result = await data_synchronizer._execute_synchronization(parameters)
            
            assert result["operation"] == "execute_sync"
            assert result["success"] is True
            assert result["records_processed"] == 100
            assert result["records_synced"] == 95
            assert result["conflicts_detected"] == 2
    
    @pytest.mark.asyncio
    async def test_execute_synchronization_not_found(self, data_synchronizer):
        """Test synchronization execution when sync not found"""
        parameters = {"sync_id": "nonexistent_sync"}
        result = await data_synchronizer._execute_synchronization(parameters)
        
        assert result["operation"] == "execute_sync"
        assert "error" in result
        assert "not found" in result["error"]
    
    @pytest.mark.asyncio
    async def test_schedule_synchronization_success(self, data_synchronizer, sample_sync_configuration):
        """Test successful synchronization scheduling"""
        # Add sync configuration to synchronizer
        data_synchronizer.sync_configurations["test_sync"] = sample_sync_configuration
        
        with patch.object(data_synchronizer, '_validate_schedule_config') as mock_validate:
            mock_validate.return_value = {"valid": True}
            
            with patch.object(data_synchronizer, '_save_sync_data', new_callable=AsyncMock):
                parameters = {
                    "sync_id": "test_sync",
                    "schedule_type": "interval",
                    "schedule_config": {"interval": 3600}
                }
                
                result = await data_synchronizer._schedule_synchronization(parameters)
                
                assert result["operation"] == "schedule_sync"
                assert result["sync_id"] == "test_sync"
                assert result["schedule_type"] == "interval"
                assert len(data_synchronizer.scheduled_syncs) == 1
    
    @pytest.mark.asyncio
    async def test_monitor_synchronization(self, data_synchronizer):
        """Test synchronization monitoring"""
        # Add some mock execution history
        execution = SyncExecution(
            execution_id="exec1",
            sync_id="test_sync",
            status=SyncStatus.COMPLETED,
            started_at=datetime.now() - timedelta(hours=1),
            completed_at=datetime.now() - timedelta(minutes=30),
            records_processed=100,
            records_synced=95,
            records_failed=5,
            conflicts_detected=2
        )
        data_synchronizer.execution_history.append(execution)
        
        parameters = {"time_range": "24h"}
        result = await data_synchronizer._monitor_synchronization(parameters)
        
        assert result["operation"] == "monitor_sync"
        assert result["summary"]["total_executions"] == 1
        assert result["summary"]["successful_executions"] == 1
        assert result["summary"]["total_records_processed"] == 100
        assert result["summary"]["total_conflicts"] == 2
    
    @pytest.mark.asyncio
    async def test_resolve_data_conflicts_specific(self, data_synchronizer):
        """Test resolving specific data conflict"""
        # Add a mock conflict
        conflict = DataConflict(
            conflict_id="conflict1",
            sync_id="test_sync",
            execution_id="exec1",
            source_record={"id": 1, "name": "John"},
            target_record={"id": 1, "name": "Jane"},
            conflicting_fields=["name"],
            resolution_strategy=ConflictResolution.SOURCE_WINS
        )
        data_synchronizer.data_conflicts["conflict1"] = conflict
        
        with patch.object(data_synchronizer, '_apply_conflict_resolution', new_callable=AsyncMock) as mock_apply:
            mock_apply.return_value = {
                "success": True,
                "resolution_data": {"id": 1, "name": "John"}
            }
            
            with patch.object(data_synchronizer, '_save_sync_data', new_callable=AsyncMock):
                parameters = {
                    "conflict_id": "conflict1",
                    "resolution_strategy": "source_wins"
                }
                
                result = await data_synchronizer._resolve_data_conflicts(parameters)
                
                assert result["operation"] == "resolve_conflicts"
                assert result["success"] is True
                assert conflict.resolved is True
    
    @pytest.mark.asyncio
    async def test_resolve_data_conflicts_auto_resolve(self, data_synchronizer):
        """Test auto-resolving all conflicts"""
        # Add mock conflicts
        conflict1 = DataConflict(
            conflict_id="conflict1",
            sync_id="test_sync",
            execution_id="exec1",
            source_record={"id": 1, "name": "John"},
            target_record={"id": 1, "name": "Jane"},
            conflicting_fields=["name"],
            resolution_strategy=ConflictResolution.SOURCE_WINS
        )
        conflict2 = DataConflict(
            conflict_id="conflict2",
            sync_id="test_sync",
            execution_id="exec1",
            source_record={"id": 2, "email": "john@example.com"},
            target_record={"id": 2, "email": "john@test.com"},
            conflicting_fields=["email"],
            resolution_strategy=ConflictResolution.TARGET_WINS
        )
        data_synchronizer.data_conflicts["conflict1"] = conflict1
        data_synchronizer.data_conflicts["conflict2"] = conflict2
        
        with patch.object(data_synchronizer, '_auto_resolve_conflict', new_callable=AsyncMock) as mock_auto:
            mock_auto.return_value = {"success": True, "resolution_data": {}}
            
            parameters = {"auto_resolve": True}
            result = await data_synchronizer._resolve_data_conflicts(parameters)
            
            assert result["operation"] == "resolve_conflicts"
            assert result["auto_resolve"] is True
            assert result["resolved_conflicts"] == 2
    
    @pytest.mark.asyncio
    async def test_validate_data_consistency(self, data_synchronizer, sample_sync_configuration):
        """Test data consistency validation"""
        # Add sync configuration to synchronizer
        data_synchronizer.sync_configurations["test_sync"] = sample_sync_configuration
        
        with patch.object(data_synchronizer, '_perform_data_validation', new_callable=AsyncMock) as mock_validate:
            mock_validate.return_value = {
                "passed": False,
                "total_records": 1000,
                "inconsistencies": [
                    {"record_id": "record1", "field": "email", "severity": "medium"}
                ],
                "consistency_score": 0.95,
                "details": {"validation_time": 2.0}
            }
            
            parameters = {"sync_id": "test_sync"}
            result = await data_synchronizer._validate_data_consistency(parameters)
            
            assert result["operation"] == "validate_data"
            assert result["validation_passed"] is False
            assert result["total_records_checked"] == 1000
            assert result["inconsistencies_found"] == 1
            assert result["consistency_score"] == 0.95
    
    @pytest.mark.asyncio
    async def test_optimize_synchronization(self, data_synchronizer, sample_sync_configuration):
        """Test synchronization optimization"""
        # Add sync configuration to synchronizer
        data_synchronizer.sync_configurations["test_sync"] = sample_sync_configuration
        
        with patch.object(data_synchronizer, '_analyze_sync_performance', new_callable=AsyncMock) as mock_analyze:
            mock_analyze.return_value = {
                "avg_execution_time": 5.0,
                "success_rate": 0.95,
                "bottlenecks": ["Network latency"]
            }
            
            with patch.object(data_synchronizer, '_generate_sync_optimizations', new_callable=AsyncMock) as mock_optimize:
                mock_optimize.return_value = {
                    "recommendations": [
                        {"type": "incremental_sync", "impact": "high"}
                    ]
                }
                
                parameters = {
                    "sync_id": "test_sync",
                    "type": "performance"
                }
                
                result = await data_synchronizer._optimize_synchronization(parameters)
                
                assert result["operation"] == "optimize_sync"
                assert result["optimization_type"] == "performance"
                assert "analysis" in result
                assert "optimizations" in result
    
    @pytest.mark.asyncio
    async def test_manage_data_sources_list(self, data_synchronizer, sample_sync_configuration):
        """Test listing data sources"""
        # Add sync configuration to synchronizer
        data_synchronizer.sync_configurations["test_sync"] = sample_sync_configuration
        
        parameters = {
            "action": "list",
            "sync_id": "test_sync"
        }
        
        result = await data_synchronizer._manage_data_sources(parameters)
        
        assert result["operation"] == "manage_sources"
        assert result["action"] == "list"
        assert result["sync_id"] == "test_sync"
        assert len(result["sources"]) == 2
        assert result["sources"][0]["source_id"] == "source1"
    
    @pytest.mark.asyncio
    async def test_manage_data_sources_test(self, data_synchronizer, sample_sync_configuration):
        """Test testing data source connection"""
        # Add sync configuration to synchronizer
        data_synchronizer.sync_configurations["test_sync"] = sample_sync_configuration
        
        with patch.object(data_synchronizer, '_test_data_source', new_callable=AsyncMock) as mock_test:
            mock_test.return_value = {
                "success": True,
                "response_time": 0.1,
                "status": "connected"
            }
            
            parameters = {
                "action": "test",
                "sync_id": "test_sync",
                "source_id": "source1"
            }
            
            result = await data_synchronizer._manage_data_sources(parameters)
            
            assert result["operation"] == "manage_sources"
            assert result["action"] == "test"
            assert result["test_result"]["success"] is True
    
    @pytest.mark.asyncio
    async def test_get_sync_status_specific(self, data_synchronizer, sample_sync_configuration):
        """Test getting status for specific sync"""
        # Add sync configuration to synchronizer
        data_synchronizer.sync_configurations["test_sync"] = sample_sync_configuration
        
        # Add some execution history
        execution = SyncExecution(
            execution_id="exec1",
            sync_id="test_sync",
            status=SyncStatus.COMPLETED,
            started_at=datetime.now(),
            records_processed=100
        )
        data_synchronizer.execution_history.append(execution)
        
        parameters = {"sync_id": "test_sync"}
        result = await data_synchronizer._get_sync_status(parameters)
        
        assert result["operation"] == "sync_status"
        assert result["sync_id"] == "test_sync"
        assert result["sync_name"] == "Test Sync"
        assert result["sources"] == 2
        assert result["rules"] == 1
        assert result["execution_stats"]["total_executions"] == 1
    
    @pytest.mark.asyncio
    async def test_get_sync_status_overall(self, data_synchronizer, sample_sync_configuration):
        """Test getting overall sync status"""
        # Add sync configuration to synchronizer
        data_synchronizer.sync_configurations["test_sync"] = sample_sync_configuration
        
        parameters = {}
        result = await data_synchronizer._get_sync_status(parameters)
        
        assert result["operation"] == "sync_status"
        assert result["total_syncs"] == 1
        assert result["scheduled_syncs"] == 0
        assert "syncs" in result
        assert "test_sync" in result["syncs"]
    
    def test_transformation_functions(self, data_synchronizer):
        """Test built-in transformation functions"""
        # Test uppercase transformation
        uppercase_func = data_synchronizer.transformation_functions["uppercase"]
        assert uppercase_func("hello") == "HELLO"
        assert uppercase_func(None) is None
        
        # Test lowercase transformation
        lowercase_func = data_synchronizer.transformation_functions["lowercase"]
        assert lowercase_func("HELLO") == "hello"
        
        # Test trim transformation
        trim_func = data_synchronizer.transformation_functions["trim"]
        assert trim_func("  hello  ") == "hello"
        
        # Test to_int transformation
        to_int_func = data_synchronizer.transformation_functions["to_int"]
        assert to_int_func("123") == 123
        assert to_int_func("abc") is None
        
        # Test format_email transformation
        format_email_func = data_synchronizer.transformation_functions["format_email"]
        assert format_email_func("USER@EXAMPLE.COM") == "user@example.com"
        assert format_email_func("invalid") is None
    
    def test_format_phone(self, data_synchronizer):
        """Test phone number formatting"""
        # Test 10-digit phone number
        result = data_synchronizer._format_phone("1234567890")
        assert result == "(123) 456-7890"
        
        # Test 11-digit phone number with country code
        result = data_synchronizer._format_phone("11234567890")
        assert result == "+1 (123) 456-7890"
        
        # Test invalid phone number
        result = data_synchronizer._format_phone("123")
        assert result == "123"
    
    def test_sync_configuration_validation_success(self, data_synchronizer, sample_sync_configuration):
        """Test successful sync configuration validation"""
        result = asyncio.run(data_synchronizer._validate_sync_configuration(sample_sync_configuration))
        
        assert result["valid"] is True
        assert len(result["errors"]) == 0
    
    def test_sync_configuration_validation_insufficient_sources(self, data_synchronizer):
        """Test sync configuration validation with insufficient sources"""
        sync_config = SyncConfiguration(
            sync_id="test_sync",
            name="Test Sync",
            description="Test",
            sources=[DataSource("source1", "Source 1", "api", {})],  # Only one source
            sync_direction=SyncDirection.ONE_WAY,
            sync_strategy=SyncStrategy.OVERWRITE,
            sync_rules=[]
        )
        
        result = asyncio.run(data_synchronizer._validate_sync_configuration(sync_config))
        
        assert result["valid"] is False
        assert "At least 2 sources are required" in result["error"]
    
    def test_schedule_validation_interval(self, data_synchronizer):
        """Test schedule validation for interval type"""
        result = data_synchronizer._validate_schedule_config("interval", {"interval": 3600})
        assert result["valid"] is True
        
        result = data_synchronizer._validate_schedule_config("interval", {})
        assert result["valid"] is False
        assert "missing 'interval' parameter" in result["error"]
    
    def test_schedule_validation_cron(self, data_synchronizer):
        """Test schedule validation for cron type"""
        result = data_synchronizer._validate_schedule_config("cron", {"cron": "0 0 * * *"})
        assert result["valid"] is True
        
        result = data_synchronizer._validate_schedule_config("cron", {"cron": "invalid"})
        assert result["valid"] is False
        assert "must have 5 parts" in result["error"]
    
    @pytest.mark.asyncio
    async def test_auto_resolve_conflict_source_wins(self, data_synchronizer):
        """Test auto-resolving conflict with source wins strategy"""
        conflict = DataConflict(
            conflict_id="conflict1",
            sync_id="test_sync",
            execution_id="exec1",
            source_record={"id": 1, "name": "John"},
            target_record={"id": 1, "name": "Jane"},
            conflicting_fields=["name"],
            resolution_strategy=ConflictResolution.SOURCE_WINS
        )
        
        result = await data_synchronizer._auto_resolve_conflict(conflict)
        
        assert result["success"] is True
        assert result["resolution_data"]["name"] == "John"
    
    @pytest.mark.asyncio
    async def test_auto_resolve_conflict_target_wins(self, data_synchronizer):
        """Test auto-resolving conflict with target wins strategy"""
        conflict = DataConflict(
            conflict_id="conflict1",
            sync_id="test_sync",
            execution_id="exec1",
            source_record={"id": 1, "name": "John"},
            target_record={"id": 1, "name": "Jane"},
            conflicting_fields=["name"],
            resolution_strategy=ConflictResolution.TARGET_WINS
        )
        
        result = await data_synchronizer._auto_resolve_conflict(conflict)
        
        assert result["success"] is True
        assert result["resolution_data"]["name"] == "Jane"
    
    @pytest.mark.asyncio
    async def test_supported_operations(self, data_synchronizer):
        """Test getting supported operations"""
        operations = await data_synchronizer.get_supported_operations()
        
        expected_operations = [
            "create_sync", "execute_sync", "schedule_sync", "monitor_sync",
            "resolve_conflicts", "validate_data", "optimize_sync", "manage_sources",
            "sync_status", "list_syncs", "cancel_sync"
        ]
        
        for operation in expected_operations:
            assert operation in operations
    
    @pytest.mark.asyncio
    async def test_execute_operation_routing(self, data_synchronizer):
        """Test operation routing in execute_operation"""
        # Test create sync operation
        with patch.object(data_synchronizer, '_create_sync_configuration', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = {"sync_id": "test"}
            
            request = SupremeRequest(
                request_id="test_req",
                operation="create_sync",
                parameters={"name": "test"}
            )
            
           )file__]main([__pytest.:
    ain__" == "__m __name__ce()


ifrt_called_onssexecute.a  mock_e       ue
   is Tress"] cct["susul reert   ass)
         uestration(reqopeer._execute_roniz data_synch = await result           
        
        )
         "test"}d":c_i{"synrameters=        pa       ,
 nc"te_sytion="execupera      o
          est_req","tuest_id=     req        
   Request(upreme = S     request     
          
    ue}uccess": Trlue = {"svaeturn__execute.r      mock   xecute:
   k_e mocyncMock) asable=As new_call',hronizationxecute_syncnizer, '_e_synchrodatat(patch.objec     with tion
   operaxecute sync  # Test e
             
  lled_once()_cae.assert  mock_creat
          t"tes= "c_id"] =synt["rt resul        asse)
    questeration(rete_opnizer._execudata_synchrowait = a result 