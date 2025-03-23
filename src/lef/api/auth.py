"""
Authentication API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Dict, List, Optional
from datetime import datetime
from ..services.auth_service import AuthService
from ..models.user import User, UserRole, UserStatus
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/api/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

# Request/Response models
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: Optional[UserRole] = UserRole.VIEWER

class UserResponse(BaseModel):
    username: str
    email: EmailStr
    role: UserRole
    status: UserStatus
    created_at: datetime
    last_login: Optional[datetime]
    last_activity: Optional[datetime]
    two_factor_enabled: bool
    api_keys: List[str]

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class PasswordChange(BaseModel):
    old_password: str
    new_password: str

class PasswordReset(BaseModel):
    email: EmailStr

class TwoFactorVerify(BaseModel):
    code: str

class ApiKeyCreate(BaseModel):
    name: str

# Dependencies
def get_auth_service() -> AuthService:
    # TODO: Get secret key from configuration
    return AuthService(secret_key="your-secret-key")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service)
) -> User:
    is_valid, user = auth_service.validate_token(token)
    if not is_valid or not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

# Endpoints
@router.post("/register", response_model=UserResponse)
async def register_user(
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Register a new user"""
    user = auth_service.create_user(
        username=user_data.username,
        email=user_data.email,
        password=user_data.password,
        role=user_data.role
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    return user

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    request: Request = None,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Login user and return access token"""
    is_valid, token, user = auth_service.authenticate(
        username=form_data.username,
        password=form_data.password,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=token  # token contains error message in this case
        )
    return {"access_token": token, "token_type": "bearer"}

@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Logout user and revoke all tokens"""
    auth_service.revoke_all_tokens(current_user.username)
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Change user password"""
    success = auth_service.change_password(
        username=current_user.username,
        old_password=password_data.old_password,
        new_password=password_data.new_password
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid old password"
        )
    return {"message": "Password changed successfully"}

@router.post("/reset-password")
async def request_password_reset(
    reset_data: PasswordReset,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Request password reset"""
    token = auth_service.reset_password(reset_data.email)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    # TODO: Send reset email with token
    return {"message": "Password reset email sent"}

@router.post("/reset-password/{token}")
async def reset_password(
    token: str,
    new_password: str,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Reset password using token"""
    success = auth_service.verify_reset_token(token, new_password)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    return {"message": "Password reset successfully"}

@router.post("/2fa/enable")
async def enable_2fa(
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Enable 2FA for user"""
    secret = auth_service.enable_2fa(current_user.username)
    if not secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to enable 2FA"
        )
    # TODO: Return QR code or secret for 2FA setup
    return {"secret": secret}

@router.post("/2fa/verify")
async def verify_2fa(
    code_data: TwoFactorVerify,
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Verify 2FA code"""
    success = auth_service.verify_2fa(current_user.username, code_data.code)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid 2FA code"
        )
    return {"message": "2FA verified successfully"}

@router.post("/2fa/disable")
async def disable_2fa(
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Disable 2FA for user"""
    success = auth_service.disable_2fa(current_user.username)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to disable 2FA"
        )
    return {"message": "2FA disabled successfully"}

@router.post("/api-keys", response_model=Dict[str, str])
async def create_api_key(
    key_data: ApiKeyCreate,
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Create a new API key"""
    key = auth_service.create_api_key(current_user.username, key_data.name)
    if not key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create API key"
        )
    return {"api_key": key}

@router.delete("/api-keys/{key}")
async def revoke_api_key(
    key: str,
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Revoke an API key"""
    success = auth_service.revoke_api_key(current_user.username, key)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    return {"message": "API key revoked successfully"}

@router.get("/permissions")
async def get_user_permissions(current_user: User = Depends(get_current_user)):
    """Get user permissions"""
    return {"permissions": current_user.permissions}

@router.post("/permissions/{permission}")
async def add_permission(
    permission: str,
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Add a permission to user"""
    success = auth_service.add_permission(current_user.username, permission)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to add permission"
        )
    return {"message": "Permission added successfully"}

@router.delete("/permissions/{permission}")
async def remove_permission(
    permission: str,
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Remove a permission from user"""
    success = auth_service.remove_permission(current_user.username, permission)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to remove permission"
        )
    return {"message": "Permission removed successfully"} 