"""
API endpoints for security operations
"""

import logging
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel
from ..services.security_service import SecurityService, SecurityConfig, SecurityEvent
from ..services.logging_service import LoggingService
from ..services.alert_service import AlertSeverity
from .auth_api import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()
security_service = SecurityService()
logging_service = LoggingService()

class SecurityConfigUpdate(BaseModel):
    """Request model for updating security configuration"""
    config: SecurityConfig

class SecurityEventFilter(BaseModel):
    """Request model for filtering security events"""
    event_type: Optional[str] = None
    severity: Optional[AlertSeverity] = None
    user_id: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

@router.get("/config")
async def get_security_config(
    current_user = Depends(get_current_user)
):
    """Get security configuration"""
    try:
        return security_service.config
    except Exception as e:
        logger.error(f"Failed to get security config: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to get security config: {e}",
            user_id=current_user.id
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get security configuration"
        )

@router.put("/config")
async def update_security_config(
    request: SecurityConfigUpdate,
    current_user = Depends(get_current_user)
):
    """Update security configuration"""
    try:
        await security_service.update_security_config(request.config)
        await logging_service.log_message(
            "info",
            "Security configuration updated",
            user_id=current_user.id
        )
        return {"message": "Security configuration updated successfully"}
    except Exception as e:
        logger.error(f"Failed to update security config: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to update security config: {e}",
            user_id=current_user.id
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update security configuration"
        )

@router.post("/validate-password")
async def validate_password(
    password: str,
    current_user = Depends(get_current_user)
):
    """Validate password strength"""
    try:
        is_valid = security_service.validate_password(password)
        await logging_service.log_message(
            "info",
            "Password validation completed",
            user_id=current_user.id,
            details={"is_valid": is_valid}
        )
        return {"is_valid": is_valid}
    except Exception as e:
        logger.error(f"Failed to validate password: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to validate password: {e}",
            user_id=current_user.id
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to validate password"
        )

@router.get("/events")
async def get_security_events(
    filter: SecurityEventFilter,
    current_user = Depends(get_current_user)
):
    """Get security events with filters"""
    try:
        events = await security_service.get_security_events(
            event_type=filter.event_type,
            severity=filter.severity,
            user_id=filter.user_id,
            start_time=filter.start_time,
            end_time=filter.end_time
        )
        await logging_service.log_message(
            "info",
            "Security events retrieved",
            user_id=current_user.id
        )
        return events
    except Exception as e:
        logger.error(f"Failed to get security events: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to get security events: {e}",
            user_id=current_user.id
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get security events"
        )

@router.post("/validate-ip")
async def validate_ip(
    request: Request,
    current_user = Depends(get_current_user)
):
    """Validate IP address"""
    try:
        client_host = request.client.host
        is_valid = await security_service.validate_ip(client_host)
        await logging_service.log_message(
            "info",
            "IP validation completed",
            user_id=current_user.id,
            details={"ip": client_host, "is_valid": is_valid}
        )
        return {"is_valid": is_valid}
    except Exception as e:
        logger.error(f"Failed to validate IP: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to validate IP: {e}",
            user_id=current_user.id
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to validate IP"
        )

@router.post("/session")
async def create_session(
    current_user = Depends(get_current_user)
):
    """Create a new session"""
    try:
        session_id = await security_service.create_session(current_user.id)
        await logging_service.log_message(
            "info",
            "Session created",
            user_id=current_user.id,
            details={"session_id": session_id}
        )
        return {"session_id": session_id}
    except Exception as e:
        logger.error(f"Failed to create session: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to create session: {e}",
            user_id=current_user.id
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create session"
        )

@router.delete("/session/{session_id}")
async def end_session(
    session_id: str,
    current_user = Depends(get_current_user)
):
    """End a session"""
    try:
        await security_service.end_session(session_id)
        await logging_service.log_message(
            "info",
            "Session ended",
            user_id=current_user.id,
            details={"session_id": session_id}
        )
        return {"message": "Session ended successfully"}
    except Exception as e:
        logger.error(f"Failed to end session: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to end session: {e}",
            user_id=current_user.id
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to end session"
        ) 