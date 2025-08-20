"""
Privacy management system for Jarvis AI Assistant
"""

import json
import logging
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict
import os

from core.security.data_encryption import DataEncryption

logger = logging.getLogger(__name__)

class DataCategory(Enum):
    """Categories of data for privacy management"""
    PERSONAL_INFO = "personal_info"
    VOICE_DATA = "voice_data"
    CONVERSATION_HISTORY = "conversation_history"
    DEVICE_DATA = "device_data"
    LOCATION_DATA = "location_data"
    HEALTH_DATA = "health_data"
    FINANCIAL_DATA = "financial_data"
    BIOMETRIC_DATA = "biometric_data"
    USAGE_ANALYTICS = "usage_analytics"
    PREFERENCES = "preferences"

class ConsentLevel(Enum):
    """Levels of user consent"""
    DENIED = "denied"
    BASIC = "basic"
    ENHANCED = "enhanced"
    FULL = "full"

class RetentionPeriod(Enum):
    """Data retention periods"""
    SESSION_ONLY = "session_only"
    ONE_DAY = "one_day"
    ONE_WEEK = "one_week"
    ONE_MONTH = "one_month"
    THREE_MONTHS = "three_months"
    ONE_YEAR = "one_year"
    INDEFINITE = "indefinite"

@dataclass
class DataConsent:
    """Represents user consent for a data category"""
    category: DataCategory
    consent_level: ConsentLevel
    granted_at: datetime
    expires_at: Optional[datetime]
    retention_period: RetentionPeriod
    purpose: str
    can_share: bool = False
    can_analyze: bool = False

@dataclass
class PrivacySettings:
    """User privacy settings"""
    user_id: str
    consents: Dict[DataCategory, DataConsent]
    created_at: datetime
    updated_at: datetime
    data_minimization: bool = True
    anonymization_enabled: bool = True
    audit_logging: bool = True

class PrivacyManager:
    """Manages user privacy settings and data consent"""
    
    def __init__(self, encryption: DataEncryption, storage_path: str = "data/privacy"):
        self.encryption = encryption
        self.storage_path = storage_path
        self.privacy_settings: Dict[str, PrivacySettings] = {}
        
        # Ensure storage directory exists
        os.makedirs(storage_path, exist_ok=True)
        
        # Load existing privacy settings
        self._load_privacy_settings()
        
        logger.info("Privacy Manager initialized")
    
    def _load_privacy_settings(self):
        """Load privacy settings from storage"""
        try:
            settings_file = os.path.join(self.storage_path, "privacy_settings.json")
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    encrypted_data = json.load(f)
                
                # Decrypt and load settings
                decrypted_data = self.encryption.decrypt_data(encrypted_data)
                
                for user_id, settings_data in decrypted_data.items():
                    # Convert back to dataclass objects
                    consents = {}
                    for cat_str, consent_data in settings_data['consents'].items():
                        category = DataCategory(cat_str)
                        consent = DataConsent(
                            category=category,
                            consent_level=ConsentLevel(consent_data['consent_level']),
                            granted_at=datetime.fromisoformat(consent_data['granted_at']),
                            expires_at=datetime.fromisoformat(consent_data['expires_at']) if consent_data['expires_at'] else None,
                            retention_period=RetentionPeriod(consent_data['retention_period']),
                            purpose=consent_data['purpose'],
                            can_share=consent_data['can_share'],
                            can_analyze=consent_data['can_analyze']
                        )
                        consents[category] = consent
                    
                    settings = PrivacySettings(
                        user_id=user_id,
                        consents=consents,
                        data_minimization=settings_data['data_minimization'],
                        anonymization_enabled=settings_data['anonymization_enabled'],
                        audit_logging=settings_data['audit_logging'],
                        created_at=datetime.fromisoformat(settings_data['created_at']),
                        updated_at=datetime.fromisoformat(settings_data['updated_at'])
                    )
                    
                    self.privacy_settings[user_id] = settings
                
                logger.info(f"Loaded privacy settings for {len(self.privacy_settings)} users")
                
        except Exception as e:
            logger.error(f"Error loading privacy settings: {e}")
    
    def _save_privacy_settings(self):
        """Save privacy settings to storage"""
        try:
            # Convert to serializable format
            settings_data = {}
            for user_id, settings in self.privacy_settings.items():
                consents_data = {}
                for category, consent in settings.consents.items():
                    consents_data[category.value] = {
                        'consent_level': consent.consent_level.value,
                        'granted_at': consent.granted_at.isoformat(),
                        'expires_at': consent.expires_at.isoformat() if consent.expires_at else None,
                        'retention_period': consent.retention_period.value,
                        'purpose': consent.purpose,
                        'can_share': consent.can_share,
                        'can_analyze': consent.can_analyze
                    }
                
                settings_data[user_id] = {
                    'consents': consents_data,
                    'data_minimization': settings.data_minimization,
                    'anonymization_enabled': settings.anonymization_enabled,
                    'audit_logging': settings.audit_logging,
                    'created_at': settings.created_at.isoformat(),
                    'updated_at': settings.updated_at.isoformat()
                }
            
            # Encrypt and save
            encrypted_data = self.encryption.encrypt_data(settings_data, "privacy_settings")
            
            settings_file = os.path.join(self.storage_path, "privacy_settings.json")
            with open(settings_file, 'w') as f:
                json.dump(encrypted_data, f, indent=2)
            
            logger.debug("Privacy settings saved successfully")
            
        except Exception as e:
            logger.error(f"Error saving privacy settings: {e}")
    
    def create_user_privacy_settings(self, user_id: str) -> PrivacySettings:
        """Create default privacy settings for a new user"""
        try:
            # Create default consents with minimal permissions
            default_consents = {}
            
            # Essential consents for basic functionality
            essential_categories = [
                (DataCategory.CONVERSATION_HISTORY, "Enable voice interaction"),
                (DataCategory.PREFERENCES, "Remember user preferences"),
                (DataCategory.USAGE_ANALYTICS, "Improve system performance")
            ]
            
            for category, purpose in essential_categories:
                default_consents[category] = DataConsent(
                    category=category,
                    consent_level=ConsentLevel.BASIC,
                    granted_at=datetime.now(),
                    expires_at=None,
                    retention_period=RetentionPeriod.ONE_MONTH,
                    purpose=purpose,
                    can_share=False,
                    can_analyze=True
                )
            
            # Create privacy settings
            settings = PrivacySettings(
                user_id=user_id,
                consents=default_consents,
                data_minimization=True,
                anonymization_enabled=True,
                audit_logging=True,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            self.privacy_settings[user_id] = settings
            self._save_privacy_settings()
            
            logger.info(f"Created privacy settings for user: {user_id}")
            return settings
            
        except Exception as e:
            logger.error(f"Error creating privacy settings: {e}")
            raise
    
    def update_consent(self, 
                      user_id: str, 
                      category: DataCategory, 
                      consent_level: ConsentLevel,
                      retention_period: RetentionPeriod = RetentionPeriod.ONE_MONTH,
                      purpose: str = "",
                      can_share: bool = False,
                      can_analyze: bool = False) -> bool:
        """Update user consent for a data category"""
        try:
            if user_id not in self.privacy_settings:
                self.create_user_privacy_settings(user_id)
            
            settings = self.privacy_settings[user_id]
            
            # Calculate expiration based on retention period
            expires_at = None
            if retention_period != RetentionPeriod.INDEFINITE:
                days_map = {
                    RetentionPeriod.SESSION_ONLY: 0,
                    RetentionPeriod.ONE_DAY: 1,
                    RetentionPeriod.ONE_WEEK: 7,
                    RetentionPeriod.ONE_MONTH: 30,
                    RetentionPeriod.THREE_MONTHS: 90,
                    RetentionPeriod.ONE_YEAR: 365
                }
                days = days_map.get(retention_period, 30)
                if days > 0:
                    expires_at = datetime.now() + timedelta(days=days)
            
            # Create or update consent
            consent = DataConsent(
                category=category,
                consent_level=consent_level,
                granted_at=datetime.now(),
                expires_at=expires_at,
                retention_period=retention_period,
                purpose=purpose,
                can_share=can_share,
                can_analyze=can_analyze
            )
            
            settings.consents[category] = consent
            settings.updated_at = datetime.now()
            
            self._save_privacy_settings()
            
            logger.info(f"Updated consent for user {user_id}, category {category.value}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating consent: {e}")
            return False
    
    def check_data_access_permission(self, 
                                   user_id: str, 
                                   category: DataCategory, 
                                   purpose: str = "") -> bool:
        """Check if data access is permitted for a user and category"""
        try:
            if user_id not in self.privacy_settings:
                return False
            
            settings = self.privacy_settings[user_id]
            
            if category not in settings.consents:
                return False
            
            consent = settings.consents[category]
            
            # Check if consent is denied
            if consent.consent_level == ConsentLevel.DENIED:
                return False
            
            # Check if consent has expired
            if consent.expires_at and datetime.now() > consent.expires_at:
                logger.warning(f"Consent expired for user {user_id}, category {category.value}")
                return False
            
            # Check purpose if specified (allow if purpose is contained in consent purpose)
            if purpose and purpose.lower() not in consent.purpose.lower():
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking data access permission: {e}")
            return False
    
    def get_user_privacy_settings(self, user_id: str) -> Optional[PrivacySettings]:
        """Get privacy settings for a user"""
        return self.privacy_settings.get(user_id)
    
    def delete_user_data(self, user_id: str, categories: Optional[List[DataCategory]] = None) -> bool:
        """Delete user data for specified categories or all data"""
        try:
            if user_id not in self.privacy_settings:
                return True  # No data to delete
            
            settings = self.privacy_settings[user_id]
            
            if categories is None:
                # Delete all user data
                del self.privacy_settings[user_id]
                logger.info(f"Deleted all data for user: {user_id}")
            else:
                # Delete specific categories
                for category in categories:
                    if category in settings.consents:
                        del settings.consents[category]
                        logger.info(f"Deleted {category.value} data for user: {user_id}")
                
                settings.updated_at = datetime.now()
            
            self._save_privacy_settings()
            return True
            
        except Exception as e:
            logger.error(f"Error deleting user data: {e}")
            return False
    
    def cleanup_expired_data(self) -> int:
        """Clean up expired data based on retention periods"""
        try:
            cleanup_count = 0
            current_time = datetime.now()
            
            for user_id, settings in list(self.privacy_settings.items()):
                expired_categories = []
                
                for category, consent in settings.consents.items():
                    if consent.expires_at and current_time > consent.expires_at:
                        expired_categories.append(category)
                
                # Remove expired consents
                for category in expired_categories:
                    del settings.consents[category]
                    cleanup_count += 1
                    logger.info(f"Cleaned up expired {category.value} data for user {user_id}")
                
                # Remove user if no consents remain
                if not settings.consents:
                    del self.privacy_settings[user_id]
                    logger.info(f"Removed user {user_id} - no active consents")
                else:
                    settings.updated_at = current_time
            
            if cleanup_count > 0:
                self._save_privacy_settings()
            
            logger.info(f"Privacy cleanup completed: {cleanup_count} items removed")
            return cleanup_count
            
        except Exception as e:
            logger.error(f"Error during privacy cleanup: {e}")
            return 0
    
    def generate_privacy_report(self, user_id: str) -> Dict[str, Any]:
        """Generate a privacy report for a user"""
        try:
            if user_id not in self.privacy_settings:
                return {"error": "User not found"}
            
            settings = self.privacy_settings[user_id]
            
            report = {
                "user_id": user_id,
                "privacy_settings": {
                    "data_minimization": settings.data_minimization,
                    "anonymization_enabled": settings.anonymization_enabled,
                    "audit_logging": settings.audit_logging
                },
                "consents": [],
                "data_categories_count": len(settings.consents),
                "created_at": settings.created_at.isoformat(),
                "updated_at": settings.updated_at.isoformat()
            }
            
            for category, consent in settings.consents.items():
                consent_info = {
                    "category": category.value,
                    "consent_level": consent.consent_level.value,
                    "granted_at": consent.granted_at.isoformat(),
                    "expires_at": consent.expires_at.isoformat() if consent.expires_at else None,
                    "retention_period": consent.retention_period.value,
                    "purpose": consent.purpose,
                    "can_share": consent.can_share,
                    "can_analyze": consent.can_analyze,
                    "is_expired": consent.expires_at and datetime.now() > consent.expires_at if consent.expires_at else False
                }
                report["consents"].append(consent_info)
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating privacy report: {e}")
            return {"error": str(e)}
    
    def get_system_privacy_stats(self) -> Dict[str, Any]:
        """Get system-wide privacy statistics"""
        try:
            total_users = len(self.privacy_settings)
            total_consents = sum(len(settings.consents) for settings in self.privacy_settings.values())
            
            # Count by consent level
            consent_levels = {}
            for settings in self.privacy_settings.values():
                for consent in settings.consents.values():
                    level = consent.consent_level.value
                    consent_levels[level] = consent_levels.get(level, 0) + 1
            
            # Count by category
            categories = {}
            for settings in self.privacy_settings.values():
                for category in settings.consents.keys():
                    cat_name = category.value
                    categories[cat_name] = categories.get(cat_name, 0) + 1
            
            return {
                "total_users": total_users,
                "total_consents": total_consents,
                "consent_levels": consent_levels,
                "categories": categories,
                "encryption_enabled": True
            }
            
        except Exception as e:
            logger.error(f"Error getting privacy stats: {e}")
            return {"error": str(e)}