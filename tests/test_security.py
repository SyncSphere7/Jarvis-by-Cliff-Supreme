"""
Unit tests for security components
"""

import unittest
import tempfile
import shutil
import os
from datetime import datetime, timedelta

from core.security.data_encryption import DataEncryption
from core.security.privacy_manager import (
    PrivacyManager, DataCategory, ConsentLevel, RetentionPeriod
)
from core.security.secure_storage import SecureStorage

class TestDataEncryption(unittest.TestCase):
    """Test cases for Data Encryption"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.encryption = DataEncryption()
    
    def test_encryption_initialization(self):
        """Test encryption system initialization"""
        self.assertIsNotNone(self.encryption.master_key)
        self.assertIsNotNone(self.encryption.fernet)
    
    def test_string_encryption_decryption(self):
        """Test encrypting and decrypting strings"""
        test_data = "This is sensitive information"
        
        # Encrypt
        encrypted_metadata = self.encryption.encrypt_data(test_data, "test_string")
        
        self.assertIn('encrypted_data', encrypted_metadata)
        self.assertIn('data_type', encrypted_metadata)
        self.assertEqual(encrypted_metadata['data_type'], "test_string")
        
        # Decrypt
        decrypted_data = self.encryption.decrypt_data(encrypted_metadata)
        self.assertEqual(decrypted_data, test_data)
    
    def test_dict_encryption_decryption(self):
        """Test encrypting and decrypting dictionaries"""
        test_data = {
            "name": "John Doe",
            "age": 30,
            "preferences": ["music", "reading"]
        }
        
        # Encrypt
        encrypted_metadata = self.encryption.encrypt_data(test_data, "test_dict")
        
        # Decrypt
        decrypted_data = self.encryption.decrypt_data(encrypted_metadata)
        self.assertEqual(decrypted_data, test_data)
    
    def test_data_hashing(self):
        """Test data hashing functionality"""
        test_data = "test data for hashing"
        
        # Test SHA256
        hash_sha256 = self.encryption.hash_data(test_data, 'sha256')
        self.assertEqual(len(hash_sha256), 64)  # SHA256 produces 64 char hex
        
        # Test consistency
        hash_sha256_2 = self.encryption.hash_data(test_data, 'sha256')
        self.assertEqual(hash_sha256, hash_sha256_2)
    
    def test_secure_token_generation(self):
        """Test secure token generation"""
        token1 = self.encryption.generate_secure_token()
        token2 = self.encryption.generate_secure_token()
        
        self.assertNotEqual(token1, token2)
        self.assertIsInstance(token1, str)
        self.assertGreater(len(token1), 0)