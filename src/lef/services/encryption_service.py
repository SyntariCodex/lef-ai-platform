"""
Encryption service for handling encryption at rest
"""

import logging
import os
from typing import Optional, Union
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64

from ..services.logging_service import LoggingService
from ..services.alert_service import AlertService, AlertSeverity

logger = logging.getLogger(__name__)

class EncryptionService:
    """Service for handling encryption at rest"""
    
    def __init__(self):
        self.logging_service = LoggingService()
        self.alert_service = AlertService()
        
        # Get encryption key from environment
        self.key = os.getenv("ENCRYPTION_KEY")
        if not self.key:
            # Generate a new key if not provided
            self.key = Fernet.generate_key()
            logger.warning("No encryption key provided. Generated new key.")
            
        self.fernet = Fernet(self.key)
        
        # Initialize salt
        self.salt = os.getenv("ENCRYPTION_SALT", os.urandom(16))
        
    async def initialize(self):
        """Initialize the service"""
        if not self.key:
            await self.alert_service.create_alert(
                title="Encryption Key Generated",
                message="No encryption key provided. Generated new key.",
                severity=AlertSeverity.WARNING
            )
        
    def _derive_key(self, password: str) -> bytes:
        """Derive a key from a password using PBKDF2"""
        try:
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=self.salt,
                iterations=100000,
                backend=default_backend()
            )
            return base64.urlsafe_b64encode(kdf.derive(password.encode()))
        except Exception as e:
            logger.error(f"Failed to derive key: {e}")
            raise
            
    async def encrypt_data(self, data: Union[str, bytes], password: Optional[str] = None) -> bytes:
        """Encrypt data"""
        try:
            if isinstance(data, str):
                data = data.encode()
                
            if password:
                # Use password-based encryption
                key = self._derive_key(password)
                f = Fernet(key)
                return f.encrypt(data)
            else:
                # Use system key
                return self.fernet.encrypt(data)
                
        except Exception as e:
            logger.error(f"Failed to encrypt data: {e}")
            await self.alert_service.create_alert(
                title="Encryption Failed",
                message=f"Failed to encrypt data: {e}",
                severity=AlertSeverity.ERROR
            )
            raise
            
    async def decrypt_data(self, encrypted_data: bytes, password: Optional[str] = None) -> bytes:
        """Decrypt data"""
        try:
            if password:
                # Use password-based decryption
                key = self._derive_key(password)
                f = Fernet(key)
                return f.decrypt(encrypted_data)
            else:
                # Use system key
                return self.fernet.decrypt(encrypted_data)
                
        except Exception as e:
            logger.error(f"Failed to decrypt data: {e}")
            await self.alert_service.create_alert(
                title="Decryption Failed",
                message=f"Failed to decrypt data: {e}",
                severity=AlertSeverity.ERROR
            )
            raise
            
    async def encrypt_file(self, file_path: str, password: Optional[str] = None) -> str:
        """Encrypt a file"""
        try:
            # Read file content
            with open(file_path, 'rb') as f:
                data = f.read()
                
            # Encrypt data
            encrypted_data = await self.encrypt_data(data, password)
            
            # Write encrypted data to new file
            encrypted_file_path = f"{file_path}.encrypted"
            with open(encrypted_file_path, 'wb') as f:
                f.write(encrypted_data)
                
            return encrypted_file_path
            
        except Exception as e:
            logger.error(f"Failed to encrypt file: {e}")
            await self.alert_service.create_alert(
                title="File Encryption Failed",
                message=f"Failed to encrypt file {file_path}: {e}",
                severity=AlertSeverity.ERROR
            )
            raise
            
    async def decrypt_file(self, encrypted_file_path: str, password: Optional[str] = None) -> str:
        """Decrypt a file"""
        try:
            # Read encrypted data
            with open(encrypted_file_path, 'rb') as f:
                encrypted_data = f.read()
                
            # Decrypt data
            decrypted_data = await self.decrypt_data(encrypted_data, password)
            
            # Write decrypted data to new file
            decrypted_file_path = encrypted_file_path.replace('.encrypted', '.decrypted')
            with open(decrypted_file_path, 'wb') as f:
                f.write(decrypted_data)
                
            return decrypted_file_path
            
        except Exception as e:
            logger.error(f"Failed to decrypt file: {e}")
            await self.alert_service.create_alert(
                title="File Decryption Failed",
                message=f"Failed to decrypt file {encrypted_file_path}: {e}",
                severity=AlertSeverity.ERROR
            )
            raise
            
    async def encrypt_sensitive_data(self, data: Union[str, bytes]) -> bytes:
        """Encrypt sensitive data using AES-256-GCM"""
        try:
            if isinstance(data, str):
                data = data.encode()
                
            # Generate a random IV
            iv = os.urandom(12)
            
            # Create cipher
            cipher = Cipher(
                algorithms.AES(self.key),
                modes.GCM(iv),
                backend=default_backend()
            )
            encryptor = cipher.encryptor()
            
            # Encrypt data
            ciphertext = encryptor.update(data) + encryptor.finalize()
            
            # Combine IV, ciphertext, and tag
            return iv + ciphertext + encryptor.tag
            
        except Exception as e:
            logger.error(f"Failed to encrypt sensitive data: {e}")
            await self.alert_service.create_alert(
                title="Sensitive Data Encryption Failed",
                message=f"Failed to encrypt sensitive data: {e}",
                severity=AlertSeverity.ERROR
            )
            raise
            
    async def decrypt_sensitive_data(self, encrypted_data: bytes) -> bytes:
        """Decrypt sensitive data using AES-256-GCM"""
        try:
            # Extract IV, ciphertext, and tag
            iv = encrypted_data[:12]
            tag = encrypted_data[-16:]
            ciphertext = encrypted_data[12:-16]
            
            # Create cipher
            cipher = Cipher(
                algorithms.AES(self.key),
                modes.GCM(iv, tag),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()
            
            # Decrypt data
            return decryptor.update(ciphertext) + decryptor.finalize()
            
        except Exception as e:
            logger.error(f"Failed to decrypt sensitive data: {e}")
            await self.alert_service.create_alert(
                title="Sensitive Data Decryption Failed",
                message=f"Failed to decrypt sensitive data: {e}",
                severity=AlertSeverity.ERROR
            )
            raise 