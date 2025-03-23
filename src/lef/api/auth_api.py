"""
Authentication API endpoints
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

from ..services.auth_service import AuthService, Token
from ..services.logging_service import LoggingService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["auth"])

# Initialize services
auth_service = AuthService()
logging_service = LoggingService()

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

class LoginResponse(BaseModel):
    """Login response model"""
    access_token: str
    token_type: str
    expires_at: str
    refresh_token: str

class TokenRefreshRequest(BaseModel):
    """Token refresh request model"""
    refresh_token: str

@router.post("/login", response_model=LoginResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login endpoint"""
    try:
        # Authenticate user
        user = await auth_service.authenticate_user(form_data.username, form_data.password)
        
        # Create access token
        token = auth_service.create_access_token({
            "username": user["username"],
            "roles": user["roles"],
            "permissions": user["permissions"]
        })
        
        await logging_service.log(
            level="INFO",
            message=f"User {form_data.username} logged in successfully",
            service="auth_api"
        )
        
        return LoginResponse(
            access_token=token.access_token,
            token_type=token.token_type,
            expires_at=token.expires_at.isoformat(),
            refresh_token=token.refresh_token
        )
        
    except HTTPException as e:
        await logging_service.log(
            level="WARNING",
            message=f"Login failed for user {form_data.username}: {e.detail}",
            service="auth_api"
        )
        raise
    except Exception as e:
        await logging_service.log(
            level="ERROR",
            message=f"Login error: {e}",
            service="auth_api"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/refresh", response_model=LoginResponse)
async def refresh_token(request: TokenRefreshRequest):
    """Refresh token endpoint"""
    try:
        # Refresh token
        token = await auth_service.refresh_token(request.refresh_token)
        
        await logging_service.log(
            level="INFO",
            message="Token refreshed successfully",
            service="auth_api"
        )
        
        return LoginResponse(
            access_token=token.access_token,
            token_type=token.token_type,
            expires_at=token.expires_at.isoformat(),
            refresh_token=token.refresh_token
        )
        
    except HTTPException as e:
        await logging_service.log(
            level="WARNING",
            message=f"Token refresh failed: {e.detail}",
            service="auth_api"
        )
        raise
    except Exception as e:
        await logging_service.log(
            level="ERROR",
            message=f"Token refresh error: {e}",
            service="auth_api"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/revoke")
async def revoke_token(token: str = Depends(oauth2_scheme)):
    """Revoke token endpoint"""
    try:
        # Revoke token
        success = await auth_service.revoke_token(token)
        
        if success:
            await logging_service.log(
                level="INFO",
                message="Token revoked successfully",
                service="auth_api"
            )
            return {"message": "Token revoked successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to revoke token"
            )
            
    except HTTPException as e:
        await logging_service.log(
            level="WARNING",
            message=f"Token revocation failed: {e.detail}",
            service="auth_api"
        )
        raise
    except Exception as e:
        await logging_service.log(
            level="ERROR",
            message=f"Token revocation error: {e}",
            service="auth_api"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) 