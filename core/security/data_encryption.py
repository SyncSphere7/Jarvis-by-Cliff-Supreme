"""
Data encryption and decryption for Jarvis AI Assistant
"""

import os
import json
import logging
import hashlib
from typing import Dict, Any, Optional, Union, List
from datetime import datetime
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64
import secrets

logger = logging.getLogger(__name__)

class DataEncryption:
    """Handles encryption and decryption of sensitive data"""
    
    def __init__(self, master_key: Optional[str] = None):
        self.backend = default_backend()
        self.master_key = master_key
        self.encryption_keys = {}
        
        # Initialize master key if not provided
        if not self.master_key:
            self.master_key = self._generate_master_key()
        
        # Create encryption key from master key
        self.fernet = self._create_fernet_key(self.master_key)
        
        logger.info("Data encryption system initialized")
    
    def _generate_master_key(self) -> str:
        """Generate a secure master key"""
        return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()
    
    def _create_fernet_key(self, password: str, salt: Optional[bytes] = None) -> Fernet:
        """Create a Fernet encryption key from password"""
        if salt is None:
            salt = b'jarvis_ai_salt_2024'  # Static salt for consistency
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=self.backend
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return Fernet(key)
    
    def encrypt_data(self, data: Union[str, Dict, List], data_type: str = "general") -> Dict[str, Any]:
        """
        Encrypt data with metadata
        
        Args:
            data: Data to encrypt (string, dict, or list)
            data_type: Type of data for categorization
            
        Returns:
            Dict containing encrypted data and metadata
        """
        try:
            # Convert data to JSON string if not already string
            if isinstance(data, (dict, list)):
                data_str = json.dumps(data, default=str)
            else:
                data_str = str(data)
            
            # Encrypt the data
            encrypted_data = self.fernet.encrypt(data_str.encode())
            
            # Create metadata
            metadata = {
                'encrypted_data': base64.b64encode(encrypted_data).decode(),
                'data_type': data_type,
                'encryption_method': 'fernet',
                'encrypted_at': datetime.now().isoformat(),
                'data_hash': hashlib.sha256(data_str.encode()).hexdigest()[:16]  # First 16 chars for verification
            }
            
            logger.debug(f"Encrypted {data_type} data successfully")
            return metadata
            
        except Exception as e:
            logger.error(f"Error encrypting data: {e}")
            raise
    
    def decrypt_data(self, encrypted_metadata: Dict[str, Any]) -> Any:
        """
        Decrypt data from metadata
        
        Args:
            encrypted_metadata: Metadata containing encrypted data
            
        Returns:
            Decrypted data in original format
        """
        try:
            # Extract encrypted data
            encrypted_data = base64.b64decode(encrypted_metadata['encrypted_data'])
            
            # Decrypt the data
            decrypted_bytes = self.fernet.decrypt(encrypted_data)
            decrypted_str = decrypted_bytes.decode()
            
            # Verify data integrity
            data_hash = hashlib.sha256(decrypted_str.encode()).hexdigest()[:16]
            if data_hash != encrypted_metadata.get('data_hash'):
                logger.warning("Data integrity check failed")
            
            # Try to parse as JSON, fallback to string
            try:
                decrypted_data = json.loads(decrypted_str)
            except json.JSONDecodeError:
                decrypted_data = decrypted_str
            
            logger.debug(f"Decrypted {encrypted_metadata.get('data_type', 'unknown')} data successfully")
            return decrypted_data
            
        except Exception as e:
            logger.error(f"Error decrypting data: {e}")
            raise
    
    def encrypt_file(self, file_path: str, output_path: Optional[str] = None) -> str:
        """
        Encrypt a file
        
        Args:
            file_path: Path to file to encrypt
            output_path: Path for encrypted file (optional)
            
        Returns:
            Path to encrypted file
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Read file content
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            # Encrypt file data
            encrypted_data = self.fernet.encrypt(file_data)
            
            # Determine output path
            if not output_path:
                output_path = file_path + '.encrypted'
            
            # Write encrypted file
            with open(output_path, 'wb') as f:
                f.write(encrypted_data)
            
            logger.info(f"File encrypted: {file_path} -> {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error encrypting file: {e}")
            raise
    
    def decrypt_file(self, encrypted_file_path: str, output_path: Optional[str] = None) -> str:
        """
        Decrypt a file
        
        Args:
            encrypted_file_path: Path to encrypted file
            output_path: Path for decrypted file (optional)
            
        Returns:
            Path to decrypted file
        """
        try:
            if not os.path.exists(encrypted_file_path):
                raise FileNotFoundError(f"Encrypted file not found: {encrypted_file_path}")
            
            # Read encrypted file
            with open(encrypted_file_path, 'rb') as f:
                encrypted_data = f.read()
            
            # Decrypt file data
            decrypted_data = self.fernet.decrypt(encrypted_data)
            
            # Determine output path
            if not output_path:
                if encrypted_file_path.endswith('.encrypted'):
                    output_path = encrypted_file_path[:-10]  # Remove .encrypted
                else:
                    output_path = encrypted_file_path + '.decrypted'
            
            # Write decrypted file
            with open(output_path, 'wb') as f:
                f.write(decrypted_data)
            
            logger.info(f"File decrypted: {encrypted_file_path} -> {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error decrypting file: {e}")
            raise
    
    def hash_data(self, data: str, algorithm: str = 'sha256') -> str:
        """
        Create a hash of data for verification
        
        Args:
            data: Data to hash
            algorithm: Hash algorithm to use
            
        Returns:
            Hex digest of hash
        """
        try:
            if algorithm == 'sha256':
                hash_obj = hashlib.sha256()
            elif algorithm == 'sha1':
                hash_obj = hashlib.sha1()
            elif algorithm == 'md5':
                hash_obj = hashlib.md5()
            else:
                raise ValueError(f"Unsupported hash algorithm: {algorithm}")
            
            hash_obj.update(data.encode())
            return hash_obj.hexdigest()
            
        except Exception as e:
            logger.error(f"Error hashing data: {e}")
            raise
    
    def generate_secure_token(self, length: int = 32) -> str:
        """Generate a secure random token"""
        return secrets.token_urlsafe(length)
    
    def verify_data_integrity(self, data: str, expected_hash: str, algorithm: str = 'sha256') -> bool:
        """
        Verify data integrity using hash comparison
        
        Args:
            data: Data to verify
            expected_hash: Expected hash value
            algorithm: Hash algorithm used
            
        Returns:
            True if data is intact, False otherwise
        """
        try:
            actual_hash = self.hash_data(data, algorithm)
            return actual_hash == expected_hash
        except Exception as e:
            logger.error(f"Error verifying data integrity: {e}")
            return False
    
    def get_encryption_info(self) -> Dict[str, Any]:
        """Get information about encryption setup"""
        return {
            'encryption_method': 'Fernet (AES 128)',
            'key_derivation': 'PBKDF2-HMAC-SHA256',
            'iterations': 100000,
            'backend': 'cryptography',
            'master_key_set': bool(self.master_key)
        }