"""
API endpoints for encryption operations
"""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from ..services.encryption_service import EncryptionService
from ..services.logging_service import LoggingService
from .auth_api import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()
encryption_service = EncryptionService()
logging_service = LoggingService()

class EncryptionRequest(BaseModel):
    """Request model for encryption operations"""
    data: str
    password: Optional[str] = None

class FileEncryptionRequest(BaseModel):
    """Request model for file encryption operations"""
    file_path: str
    password: Optional[str] = None

@router.post("/encrypt")
async def encrypt_data(
    request: EncryptionRequest,
    current_user = Depends(get_current_user)
):
    """Encrypt data"""
    try:
        encrypted_data = await encryption_service.encrypt_data(
            request.data.encode(),
            request.password
        )
        await logging_service.log_message(
            "info",
            "Data encrypted successfully",
            user_id=current_user.id
        )
        return {"encrypted_data": encrypted_data.decode()}
    except Exception as e:
        logger.error(f"Failed to encrypt data: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to encrypt data: {e}",
            user_id=current_user.id
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to encrypt data"
        )

@router.post("/decrypt")
async def decrypt_data(
    request: EncryptionRequest,
    current_user = Depends(get_current_user)
):
    """Decrypt data"""
    try:
        decrypted_data = await encryption_service.decrypt_data(
            request.data.encode(),
            request.password
        )
        await logging_service.log_message(
            "info",
            "Data decrypted successfully",
            user_id=current_user.id
        )
        return {"decrypted_data": decrypted_data.decode()}
    except Exception as e:
        logger.error(f"Failed to decrypt data: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to decrypt data: {e}",
            user_id=current_user.id
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to decrypt data"
        )

@router.post("/encrypt/file")
async def encrypt_file(
    request: FileEncryptionRequest,
    current_user = Depends(get_current_user)
):
    """Encrypt a file"""
    try:
        encrypted_file_path = await encryption_service.encrypt_file(
            request.file_path,
            request.password
        )
        await logging_service.log_message(
            "info",
            f"File encrypted successfully: {encrypted_file_path}",
            user_id=current_user.id
        )
        return {"encrypted_file_path": encrypted_file_path}
    except Exception as e:
        logger.error(f"Failed to encrypt file: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to encrypt file: {e}",
            user_id=current_user.id
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to encrypt file"
        )

@router.post("/decrypt/file")
async def decrypt_file(
    request: FileEncryptionRequest,
    current_user = Depends(get_current_user)
):
    """Decrypt a file"""
    try:
        decrypted_file_path = await encryption_service.decrypt_file(
            request.file_path,
            request.password
        )
        await logging_service.log_message(
            "info",
            f"File decrypted successfully: {decrypted_file_path}",
            user_id=current_user.id
        )
        return {"decrypted_file_path": decrypted_file_path}
    except Exception as e:
        logger.error(f"Failed to decrypt file: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to decrypt file: {e}",
            user_id=current_user.id
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to decrypt file"
        )

@router.post("/encrypt/sensitive")
async def encrypt_sensitive_data(
    request: EncryptionRequest,
    current_user = Depends(get_current_user)
):
    """Encrypt sensitive data"""
    try:
        encrypted_data = await encryption_service.encrypt_sensitive_data(
            request.data.encode()
        )
        await logging_service.log_message(
            "info",
            "Sensitive data encrypted successfully",
            user_id=current_user.id
        )
        return {"encrypted_data": encrypted_data.decode()}
    except Exception as e:
        logger.error(f"Failed to encrypt sensitive data: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to encrypt sensitive data: {e}",
            user_id=current_user.id
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to encrypt sensitive data"
        )

@router.post("/decrypt/sensitive")
async def decrypt_sensitive_data(
    request: EncryptionRequest,
    current_user = Depends(get_current_user)
):
    """Decrypt sensitive data"""
    try:
        decrypted_data = await encryption_service.decrypt_sensitive_data(
            request.data.encode()
        )
        await logging_service.log_message(
            "info",
            "Sensitive data decrypted successfully",
            user_id=current_user.id
        )
        return {"decrypted_data": decrypted_data.decode()}
    except Exception as e:
        logger.error(f"Failed to decrypt sensitive data: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to decrypt sensitive data: {e}",
            user_id=current_user.id
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to decrypt sensitive data"
        ) 