"""
Secure storage system with optional cloud backup
"""

import os
import json
import logging
import shutil
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path

from core.security.data_encryption import DataEncryption
from core.security.privacy_manager import PrivacyManager, DataCategory

logger = logging.getLogger(__name__)

class SecureStorage:
    """Secure local storage with optional encrypted cloud backup"""
    
    def __init__(self, 
                 encryption: DataEncryption,
                 privacy_manager: PrivacyManager,
                 storage_root: str = "data/secure",
                 backup_enabled: bool = False):
        
        self.encryption = encryption
        self.privacy_manager = privacy_manager
        self.storage_root = Path(storage_root)
        self.backup_enabled = backup_enabled
        
        # Create storage directories
        self.storage_root.mkdir(parents=True, exist_ok=True)
        (self.storage_root / "user_data").mkdir(exist_ok=True)
        (self.storage_root / "system_data").mkdir(exist_ok=True)
        (self.storage_root / "backups").mkdir(exist_ok=True)
        
        logger.info(f"Secure storage initialized at: {self.storage_root}")
    
    def store_user_data(self, 
                       user_id: str, 
                       data_category: DataCategory, 
                       data: Any, 
                       metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Store user data securely with privacy checks
        
        Args:
            user_id: User identifier
            data_category: Category of data being stored
            data: Data to store
            metadata: Additional metadata
            
        Returns:
            True if stored successfully, False otherwise
        """
        try:
            # Check privacy permissions
            if not self.privacy_manager.check_data_access_permission(user_id, data_category):
                logger.warning(f"Storage denied for user {user_id}, category {data_category.value}")
                return False
            
            # Create user directory
            user_dir = self.storage_root / "user_data" / user_id
            user_dir.mkdir(exist_ok=True)
            
            # Prepare data with metadata
            storage_data = {
                'data': data,
                'metadata': metadata or {},
                'stored_at': datetime.now().isoformat(),
                'data_category': data_category.value,
                'user_id': user_id
            }
            
            # Encrypt data
            encrypted_data = self.encryption.encrypt_data(storage_data, data_category.value)
            
            # Store encrypted data
            file_path = user_dir / f"{data_category.value}.json"
            with open(file_path, 'w') as f:
                json.dump(encrypted_data, f, indent=2)
            
            logger.debug(f"Stored {data_category.value} data for user {user_id}")
            
            # Create backup if enabled
            if self.backup_enabled:
                self._create_backup(user_id, data_category, encrypted_data)
            
            return True
            
        except Exception as e:
            logger.error(f"Error storing user data: {e}")
            return False
    
    def retrieve_user_data(self, 
                          user_id: str, 
                          data_category: DataCategory) -> Optional[Any]:
        """
        Retrieve user data with privacy checks
        
        Args:
            user_id: User identifier
            data_category: Category of data to retrieve
            
        Returns:
            Decrypted data or None if not found/not permitted
        """
        try:
            # Check privacy permissions
            if not self.privacy_manager.check_data_access_permission(user_id, data_category):
                logger.warning(f"Retrieval denied for user {user_id}, category {data_category.value}")
                return None
            
            # Check if file exists
            file_path = self.storage_root / "user_data" / user_id / f"{data_category.value}.json"
            if not file_path.exists():
                return None
            
            # Load encrypted data
            with open(file_path, 'r') as f:
                encrypted_data = json.load(f)
            
            # Decrypt data
            decrypted_data = self.encryption.decrypt_data(encrypted_data)
            
            logger.debug(f"Retrieved {data_category.value} data for user {user_id}")
            return decrypted_data.get('data')
            
        except Exception as e:
            logger.error(f"Error retrieving user data: {e}")
            return None
    
    def delete_user_data(self, 
                        user_id: str, 
                        data_category: Optional[DataCategory] = None) -> bool:
        """
        Delete user data (specific category or all data)
        
        Args:
            user_id: User identifier
            data_category: Specific category to delete (None for all)
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            user_dir = self.storage_root / "user_data" / user_id
            
            if not user_dir.exists():
                return True  # Nothing to delete
            
            if data_category:
                # Delete specific category
                file_path = user_dir / f"{data_category.value}.json"
                if file_path.exists():
                    file_path.unlink()
                    logger.info(f"Deleted {data_category.value} data for user {user_id}")
                
                # Delete backup
                backup_path = self.storage_root / "backups" / user_id / f"{data_category.value}.json"
                if backup_path.exists():
                    backup_path.unlink()
            else:
                # Delete all user data
                shutil.rmtree(user_dir)
                logger.info(f"Deleted all data for user {user_id}")
                
                # Delete user backups
                backup_dir = self.storage_root / "backups" / user_id
                if backup_dir.exists():
                    shutil.rmtree(backup_dir)
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting user data: {e}")
            return False
    
    def store_system_data(self, 
                         data_key: str, 
                         data: Any, 
                         metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Store system-level data (non-user specific)
        
        Args:
            data_key: Unique key for the data
            data: Data to store
            metadata: Additional metadata
            
        Returns:
            True if stored successfully, False otherwise
        """
        try:
            # Prepare data with metadata
            storage_data = {
                'data': data,
                'metadata': metadata or {},
                'stored_at': datetime.now().isoformat(),
                'data_key': data_key
            }
            
            # Encrypt data
            encrypted_data = self.encryption.encrypt_data(storage_data, "system_data")
            
            # Store encrypted data
            file_path = self.storage_root / "system_data" / f"{data_key}.json"
            with open(file_path, 'w') as f:
                json.dump(encrypted_data, f, indent=2)
            
            logger.debug(f"Stored system data: {data_key}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing system data: {e}")
            return False
    
    def retrieve_system_data(self, data_key: str) -> Optional[Any]:
        """
        Retrieve system-level data
        
        Args:
            data_key: Unique key for the data
            
        Returns:
            Decrypted data or None if not found
        """
        try:
            file_path = self.storage_root / "system_data" / f"{data_key}.json"
            if not file_path.exists():
                return None
            
            # Load encrypted data
            with open(file_path, 'r') as f:
                encrypted_data = json.load(f)
            
            # Decrypt data
            decrypted_data = self.encryption.decrypt_data(encrypted_data)
            
            logger.debug(f"Retrieved system data: {data_key}")
            return decrypted_data.get('data')
            
        except Exception as e:
            logger.error(f"Error retrieving system data: {e}")
            return None
    
    def _create_backup(self, 
                      user_id: str, 
                      data_category: DataCategory, 
                      encrypted_data: Dict[str, Any]):
        """Create a backup of encrypted data"""
        try:
            backup_dir = self.storage_root / "backups" / user_id
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Add backup timestamp to metadata
            backup_data = encrypted_data.copy()
            backup_data['backup_created_at'] = datetime.now().isoformat()
            
            backup_path = backup_dir / f"{data_category.value}.json"
            with open(backup_path, 'w') as f:
                json.dump(backup_data, f, indent=2)
            
            logger.debug(f"Created backup for user {user_id}, category {data_category.value}")
            
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
    
    def restore_from_backup(self, 
                           user_id: str, 
                           data_category: DataCategory) -> bool:
        """
        Restore data from backup
        
        Args:
            user_id: User identifier
            data_category: Category to restore
            
        Returns:
            True if restored successfully, False otherwise
        """
        try:
            backup_path = self.storage_root / "backups" / user_id / f"{data_category.value}.json"
            if not backup_path.exists():
                logger.warning(f"No backup found for user {user_id}, category {data_category.value}")
                return False
            
            # Load backup data
            with open(backup_path, 'r') as f:
                backup_data = json.load(f)
            
            # Restore to main storage
            user_dir = self.storage_root / "user_data" / user_id
            user_dir.mkdir(parents=True, exist_ok=True)
            
            restore_path = user_dir / f"{data_category.value}.json"
            with open(restore_path, 'w') as f:
                json.dump(backup_data, f, indent=2)
            
            logger.info(f"Restored {data_category.value} data for user {user_id} from backup")
            return True
            
        except Exception as e:
            logger.error(f"Error restoring from backup: {e}")
            return False
    
    def list_user_data(self, user_id: str) -> List[str]:
        """
        List available data categories for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            List of available data categories
        """
        try:
            user_dir = self.storage_root / "user_data" / user_id
            if not user_dir.exists():
                return []
            
            categories = []
            for file_path in user_dir.glob("*.json"):
                category = file_path.stem
                categories.append(category)
            
            return categories
            
        except Exception as e:
            logger.error(f"Error listing user data: {e}")
            return []
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        try:
            stats = {
                'total_users': 0,
                'total_files': 0,
                'storage_size_bytes': 0,
                'backup_enabled': self.backup_enabled,
                'categories': {}
            }
            
            # Count user data
            user_data_dir = self.storage_root / "user_data"
            if user_data_dir.exists():
                for user_dir in user_data_dir.iterdir():
                    if user_dir.is_dir():
                        stats['total_users'] += 1
                        
                        for file_path in user_dir.glob("*.json"):
                            stats['total_files'] += 1
                            stats['storage_size_bytes'] += file_path.stat().st_size
                            
                            category = file_path.stem
                            stats['categories'][category] = stats['categories'].get(category, 0) + 1
            
            # Count system data
            system_data_dir = self.storage_root / "system_data"
            if system_data_dir.exists():
                for file_path in system_data_dir.glob("*.json"):
                    stats['total_files'] += 1
                    stats['storage_size_bytes'] += file_path.stat().st_size
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting storage stats: {e}")
            return {"error": str(e)}
    
    def cleanup_old_backups(self, days_old: int = 30) -> int:
        """
        Clean up old backup files
        
        Args:
            days_old: Delete backups older than this many days
            
        Returns:
            Number of files deleted
        """
        try:
            deleted_count = 0
            cutoff_time = datetime.now().timestamp() - (days_old * 24 * 60 * 60)
            
            backup_dir = self.storage_root / "backups"
            if backup_dir.exists():
                for user_dir in backup_dir.iterdir():
                    if user_dir.is_dir():
                        for backup_file in user_dir.glob("*.json"):
                            if backup_file.stat().st_mtime < cutoff_time:
                                backup_file.unlink()
                                deleted_count += 1
                                logger.debug(f"Deleted old backup: {backup_file}")
                        
                        # Remove empty user directories
                        if not any(user_dir.iterdir()):
                            user_dir.rmdir()
            
            logger.info(f"Cleaned up {deleted_count} old backup files")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error cleaning up old backups: {e}")
            return 0