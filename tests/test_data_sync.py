"""
Tests for Supreme Data Synchronizer
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from core.supreme.engines.data_synchronizer import (
    SupremeDataSynchronizer, SyncConfiguration, DataSource, SyncRule, FieldMapping,
    SyncDirection, SyncStrategy, ConflictResolution
)
from core.supreme.base_supreme_engine import SupremeRequest


class TestSupremeDataSynchronizer:
    
    @pytest.fixture
    def mock_config(self):
        return Mock(auto_scaling=True, max_concurrent_operations=10)
    
    @pytest.fixture
    def data_synchronizer(self, mock_config):
        return SupremeDataSynchronizer("test_sync", mock_config)
    
    @pytest.mark.asyncio
    async def test_initialization(self, data_synchronizer):
        """Test data synchronizer initialization"""
        with patch.object(data_synchronizer, '_load_sync_data', new_callable=AsyncMock), \
             patch.object(data_synchronizer, '_run_sync_scheduler', new_callable=AsyncMock), \
             patch.object(data_synchronizer, '_monitor_data_conflicts', new_callable=AsyncMock):
            
            result = await data_synchronizer._initialize_engine()
            assert result is True
            assert len(data_synchronizer.transformation_functions) > 0
    
    @pytest.mark.asyncio
    async def test_create_sync_success(self, data_synchronizer):
        """Test successful sync configuration creation"""
        with patch.object(data_synchronizer, '_validate_sync_configuration', new_callable=AsyncMock) as mock_validate:
            mock_validate.return_value = {"valid": True}
            
            with patch.object(data_synchronizer, '_save_sync_data', new_callable=AsyncMock):
                parameters = {
                    "name": "Test Sync",
                    "sources": [
                        {"source_id": "s1", "name": "DB", "type": "database", "connection": {}},
                        {"source_id": "s2", "name": "API", "type": "api", "connection": {}}
                    ],
                    "direction": "one_way",
                    "strategy": "overwrite",
                    "rules": [{"rule_id": "r1", "name": "Rule", "field_mappings": []}]
                }
                
                result = await data_synchronizer._create_sync_configuration(parameters)
                
                assert result["operation"] == "create_sync"
                assert result["sync_name"] == "Test Sync"
                assert len(data_synchronizer.sync_configurations) == 1
    
    @pytest.mark.asyncio
    async def test_supported_operations(self, data_synchronizer):
        """Test getting supported operations"""
        operations = await data_synchronizer.get_supported_operations()
        
        expected = ["create_sync", "execute_sync", "schedule_sync", "monitor_sync"]
        for operation in expected:
            assert operation in operations
    
    def test_transformation_functions(self, data_synchronizer):
        """Test built-in transformation functions"""
        uppercase_func = data_synchronizer.transformation_functions["uppercase"]
        assert uppercase_func("hello") == "HELLO"
        
        trim_func = data_synchronizer.transformation_functions["trim"]
        assert trim_func("  hello  ") == "hello"
    
    def test_phone_formatting(self, data_synchronizer):
        """Test phone number formatting"""
        result = data_synchronizer._format_phone("1234567890")
        assert result == "(123) 456-7890"


if __name__ == "__main__":
    pytest.main([__file__])