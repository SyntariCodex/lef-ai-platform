"""
API endpoints for rate limiting operations
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel
from ..services.rate_limit_service import RateLimitService, RateLimitConfig
from ..services.logging_service import LoggingService
from .auth_api import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()
rate_limit_service = RateLimitService()
logging_service = LoggingService()

class RateLimitConfigUpdate(BaseModel):
    """Request model for updating rate limit configuration"""
    config: RateLimitConfig

@router.get("/config")
async def get_rate_limit_config(
    current_user = Depends(get_current_user)
):
    """Get rate limit configuration"""
    try:
        return rate_limit_service.config
    except Exception as e:
        logger.error(f"Failed to get rate limit config: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to get rate limit config: {e}",
            user_id=current_user.id
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get rate limit configuration"
        )

@router.put("/config")
async def update_rate_limit_config(
    request: RateLimitConfigUpdate,
    current_user = Depends(get_current_user)
):
    """Update rate limit configuration"""
    try:
        await rate_limit_service.update_rate_limit_config(request.config)
        await logging_service.log_message(
            "info",
            "Rate limit configuration updated",
            user_id=current_user.id
        )
        return {"message": "Rate limit configuration updated successfully"}
    except Exception as e:
        logger.error(f"Failed to update rate limit config: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to update rate limit config: {e}",
            user_id=current_user.id
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update rate limit configuration"
        )

@router.get("/info")
async def get_rate_limit_info(
    request: Request,
    current_user = Depends(get_current_user)
):
    """Get rate limit information for current IP"""
    try:
        client_host = request.client.host
        info = await rate_limit_service.get_rate_limit_info(client_host)
        await logging_service.log_message(
            "info",
            "Rate limit info retrieved",
            user_id=current_user.id,
            details={"ip": client_host, "info": info.dict()}
        )
        return info
    except Exception as e:
        logger.error(f"Failed to get rate limit info: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to get rate limit info: {e}",
            user_id=current_user.id
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get rate limit information"
        )

@router.post("/check")
async def check_rate_limit(
    request: Request,
    current_user = Depends(get_current_user)
):
    """Check if request should be rate limited"""
    try:
        client_host = request.client.host
        allowed, info = await rate_limit_service.check_rate_limit(client_host)
        
        if not allowed:
            await logging_service.log_message(
                "warning",
                "Rate limit exceeded",
                user_id=current_user.id,
                details={"ip": client_host, "info": info.dict()}
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
                headers={
                    "X-RateLimit-Remaining": str(info.remaining_requests),
                    "X-RateLimit-Reset": info.reset_time.isoformat(),
                    "X-RateLimit-Burst-Remaining": str(info.burst_remaining)
                }
            )
            
        await logging_service.log_message(
            "info",
            "Rate limit check passed",
            user_id=current_user.id,
            details={"ip": client_host, "info": info.dict()}
        )
        return info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to check rate limit: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to check rate limit: {e}",
            user_id=current_user.id
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check rate limit"
        ) 