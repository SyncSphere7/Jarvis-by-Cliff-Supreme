"""
Tests for Supreme Maintenance System
"""

import pytest
import asyncio
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch

from core.supreme.supreme_maintenance import (
    SupremeMaintenanceManager,
    SystemBackupManager,
    UpdateManager,
    BackupType,
    UpdateType,
    SystemUpdate,
    BackupInfo
)


class TestSystemBackupManager:
    """Test SystemBackupManager functionality"""
    
    @pytest.fixture
    def backup_manager(self, tmp_path):
        return SystemBackupManager(str(tmp_path / "test_backups"))
    
    def test_backup_manager_initialization(self, backup_manager):
        """Test SystemBackupManager initialization"""
        assert isinstance(backup_manager.backup_registry, dict)
        assert backup_manager.backup_path.exists()
        assert backup_manager.max_backups == 10
        assert len(backup_manager.backup_registry) == 0
    
    @pytest.mark.asyncio
    async def test_create_backup_full(self, backup_manager):
        """Test creating a full backup"""
        backup_info = await backup_manager.create_backup(
            BackupType.FULL, 
            "Test full backup"
        )
        
        assert isinstance(backup_info, BackupInfo)
        assert backup_info.backup_type == BackupType.FULL
        assert backup_info.description == "Test full backup"
        assert backup_info.size_mb > 0
        assert backup_info.checksum
        assert Path(backup_info.file_path).exists()
        
        # Check that backup is registered
        assert backup_info.backup_id in backup_manager.backup_registry
    
    @pytest.mark.asyncio
    async def test_create_backup_incremental(self, backup_manager):
        """Test creating an incremental backup"""
        backup_info = await backup_manager.create_backup(
            BackupType.INCREMENTAL, 
            "Test incremental backup"
        )
        
        assert backup_info.backup_type == BackupType.INCREMENTAL
        assert backup_info.description == "Test incremental backup"
        assert Path(backup_info.file_path).exists()
    
    @pytest.mark.asyncio
    async def test_restore_backup_success(self, backup_manager):
        """Test successful backup restoration"""
        # Create a backup first
        backup_info = await backup_manager.create_backup(BackupType.CONFIGURATION)
        
        # Restore the backup
        success = await backup_manager.restore_backup(backup_info.backup_id)
        
        assert success is True
    
    @pytest.mark.asyncio
    async def test_restore_backup_not_found(self, backup_manager):
        """Test restoring non-existent backup"""
        success = await backup_manager.restore_backup("non_existent_backup")
        
        assert success is False
    
    @pytest.mark.asyncio
    async def test_cleanup_old_backups(self, backup_manager):
        """Test cleanup of old backups when limit exceeded"""
        # Set a low limit for testing
        backup_manager.max_backups = 2
        
        # Create more backups than the limit
        backup_ids = []
        for i in range(3):
            backup_info = await backup_manager.create_backup(
                BackupType.INCREMENTAL, 
                f"Test backup {i}"
            )
            backup_ids.append(backup_info.backup_id)
        
        # Should only have max_backups in registry
        assert len(backup_manager.backup_registry) == backup_manager.max_backups
        
        # The oldest backup should be removed
        assert backup_ids[0] not in backup_manager.backup_registry
        assert backup_ids[1] in backup_manager.backup_registry
        assert backup_ids[2] in backup_manager.backup_registry
    
    def test_list_backups(self, backup_manager):
        """Test listing backups"""
        # Initially empty
        backups = backup_manager.list_backups()
        assert len(backups) == 0
        
        # Add a mock backup to registry
        mock_backup = BackupInfo(
            backup_id="test_backup",
            backup_type=BackupType.FULL,
            size_mb=100.0,
            file_path="/test/path",
            checksum="test_checksum",
            created_at=datetime.now()
        )
        backup_manager.backup_registry["test_backup"] = mock_backup
        
        # Should return the backup
        backups = backup_manager.list_backups()
        assert len(backups) == 1
        assert backups[0] == mock_backup


class TestUpdateManager:
    """Test UpdateManager functionality"""
    
    @pytest.fixture
    def update_manager(self):
        return UpdateManager()
    
    def test_update_manager_initialization(self, update_manager):
        """Test UpdateManager initialization"""
        assert isinstance(update_manager.available_updates, dict)
        assert isinstance(update_manager.installed_updates, dict)
        assert isinstance(update_manager.update_history, list)
        assert len(update_manager.available_updates) == 0
        assert len(update_manager.installed_updates) == 0
    
    def test_check_for_updates(self, update_manager):
        """Test checking for available updates"""
        updates = update_manager.check_for_updates()
        
        assert isinstance(updates, list)
        assert len(updates) > 0
        
        # Check that updates were added to available_updates
        assert len(update_manager.available_updates) == len(updates)
        
        # Verify update structure
        for update in updates:
            assert isinstance(update, SystemUpdate)
            assert update.update_id
            assert update.version
            assert isinstance(update.update_type, UpdateType)
            assert update.description
            assert isinstance(update.changelog, list)
            assert update.size_mb > 0
    
    @pytest.mark.asyncio
    async def test_install_update_success(self, update_manager):
        """Test successful update installation"""
        # First check for updates
        updates = update_manager.check_for_updates()
        assert len(updates) > 0
        
        # Install the first update
        update_id = updates[0].update_id
        success = await update_manager.install_update(update_id)
        
        assert success is True
        
        # Check that update moved from available to installed
        assert update_id not in update_manager.available_updates
        assert update_id in update_manager.installed_updates
        
        # Check that installation was recorded in history
        assert len(update_manager.update_history) > 0
        last_history = update_manager.update_history[-1]
        assert last_history["update_id"] == update_id
        assert last_history["action"] == "install"
        assert last_history["success"] is True
    
    @pytest.mark.asyncio
    async def test_install_update_not_found(self, update_manager):
        """Test installing non-existent update"""
        success = await update_manager.install_update("non_existent_update")
        
        assert success is False
        
        # Check that failure was recorded in history
        assert len(update_manager.update_history) > 0
        last_history = update_manager.update_history[-1]
        assert last_history["update_id"] == "non_existent_update"
        assert last_history["action"] == "install"
        assert last_history["success"] is False
    
    def test_get_installed_updates(self, update_manager):
        """Test getting list of installed updates"""
        # Initially empty
        installed = update_manager.get_installed_updates()
        assert len(installed) == 0
        
        # Add a mock installed update
        mock_update = SystemUpdate(
            update_id="test_update",
            version="1.0.1",
            update_type=UpdateType.SECURITY,
            description="Test update",
            changelog=["Test change"],
            size_mb=10.0,
            requires_restart=False,
            installed_at=datetime.now()
        )
        update_manager.installed_updates["test_update"] = mock_update
        
        # Should return the installed update
        installed = update_manager.get_installed_updates()
        assert len(installed) == 1
        assert installed[0] == mock_update


class TestSupremeMaintenanceManager:
    """Test SupremeMaintenanceManager functionality"""
    
    @pytest.fixture
    def maintenance_manager(self, tmp_path):
        # Use temporary path for backups
        manager = SupremeMaintenanceManager()
        manager.backup_manager = SystemBackupManager(str(tmp_path / "test_backups"))
        return manager
    
    def test_maintenance_manager_initialization(self, maintenance_manager):
        """Test SupremeMaintenanceManager initialization"""
        assert isinstance(maintenance_manager.backup_manager, SystemBackupManager)
        assert isinstance(maintenance_manager.update_manager, UpdateManager)
        assert isinstance(maintenance_manager.system_health, dict)
        assert maintenance_manager.last_health_check is None
    
    @pytest.mark.asyncio
    async def test_perform_health_check(self, maintenance_manager):
        """Test system health check"""
        health_status = await maintenance_manager._perform_health_check()
        
        assert isinstance(health_status, dict)
        assert "overall_health" in health_status
        assert "engine_health" in health_status
        assert "resource_usage" in health_status
        assert "timestamp" in health_status
        
        # Check engine health structure
        engine_health = health_status["engine_health"]
        assert len(engine_health) == 10  # All 10 engines
        
        for engine_name, engine_status in engine_health.items():
            assert "status" in engine_status
            assert "response_time" in engine_status
            assert "memory_usage" in engine_status
        
        # Check that health was stored
        assert maintenance_manager.system_health == health_status
        assert maintenance_manager.last_health_check is not None
    
    @pytest.mark.asyncio
    async def test_cleanup_system(self, maintenance_manager):
        """Test system cleanup"""
        # Should not raise an exception
        await maintenance_manager._cleanup_system()
    
    @pytest.mark.asyncio
    async def test_perform_routine_maintenance(self, maintenance_manager):
        """Test routine maintenance execution"""
        result = await maintenance_manager.perform_routine_maintenance()
        
        assert isinstance(result, dict)
        assert "maintenance_id" in result
        assert "start_time" in result
        assert "end_time" in result
        assert "duration" in result
        assert "tasks_completed" in result
        assert "errors" in result
        
        # Check that tasks were completed
        tasks_completed = result["tasks_completed"]
        assert "health_check" in tasks_completed
        assert "backup_creation" in tasks_completed
        assert "update_check" in tasks_completed
        assert "system_cleanup" in tasks_completed
        
        # Check that duration is reasonable
        assert result["duration"] > 0
        assert result["duration"] < 30  # Should complete within 30 seconds
    
    @pytest.mark.asyncio
    async def test_emergency_recovery_without_backup(self, maintenance_manager):
        """Test emergency recovery without specifying backup"""
        result = await maintenance_manager.emergency_recovery()
        
        assert isinstance(result, dict)
        assert "recovery_id" in result
        assert "start_time" in result
        assert "end_time" in result
        assert "steps_completed" in result
        assert "status" in result
        
        # Should complete successfully
        assert result["status"] == "completed"
        
        # Should have completed basic recovery steps
        steps_completed = result["steps_completed"]
        assert "emergency_backup_created" in steps_completed
        assert "health_validation" in steps_completed
    
    @pytest.mark.asyncio
    async def test_emergency_recovery_with_backup(self, maintenance_manager):
        """Test emergency recovery with backup restoration"""
        # Create a backup first
        backup_info = await maintenance_manager.backup_manager.create_backup(BackupType.FULL)
        
        # Perform emergency recovery with the backup
        result = await maintenance_manager.emergency_recovery(backup_info.backup_id)
        
        assert result["status"] == "completed"
        
        # Should have restored the backup
        steps_completed = result["steps_completed"]
        assert "backup_restored" in steps_completed
        assert result["restored_backup_id"] == backup_info.backup_id
    
    def test_get_system_status(self, maintenance_manager):
        """Test getting system status"""
        # Set some mock data
        maintenance_manager.system_health = {"overall_health": "excellent"}
        maintenance_manager.last_health_check = datetime.now()
        
        status = maintenance_manager.get_system_status()
        
        assert isinstance(status, dict)
        assert "system_health" in status
        assert "last_health_check" in status
        assert "available_backups" in status
        assert "available_updates" in status
        assert "installed_updates" in status
        assert "timestamp" in status
        
        # Check values
        assert status["system_health"] == {"overall_health": "excellent"}
        assert status["available_backups"] == 0  # Initially no backups
        assert status["available_updates"] == 0   # Initially no updates
        assert status["installed_updates"] == 0   # Initially no installed updates


if __name__ == "__main__":
    pytest.main([__file__])