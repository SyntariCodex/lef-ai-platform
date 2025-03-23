"""
User model for authentication and authorization
"""

from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum

class UserRole(Enum):
    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"
    SYSTEM = "system"

class UserStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    DELETED = "deleted"

class User(BaseModel):
    """User model for authentication and authorization"""
    id: int = Field(default=1, description="Unique identifier for user")
    username: str = Field(..., description="Username")
    email: EmailStr = Field(..., description="User email")
    hashed_password: str = Field(..., description="Hashed password")
    role: UserRole = Field(default=UserRole.VIEWER, description="User role")
    status: UserStatus = Field(default=UserStatus.ACTIVE, description="User status")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="User creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    last_login: Optional[datetime] = None
    last_password_change: Optional[datetime] = None
    failed_login_attempts: int = Field(default=0, description="Number of failed login attempts")
    locked_until: Optional[datetime] = None
    password_reset_token: Optional[str] = None
    password_reset_expires: Optional[datetime] = None
    two_factor_enabled: bool = Field(default=False, description="Whether 2FA is enabled")
    two_factor_secret: Optional[str] = None
    api_keys: List[str] = Field(default_factory=list, description="List of API keys")
    permissions: List[str] = Field(default_factory=list, description="List of specific permissions")
    metadata: Dict = Field(default_factory=dict, description="Additional user metadata")
    last_activity: Optional[datetime] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_tokens: List[str] = Field(default_factory=list, description="Active session tokens")
    audit_log: List[Dict] = Field(default_factory=list, description="User activity audit log")
    notes: Optional[str] = None
    tags: List[str] = Field(default_factory=list, description="User tags for categorization")
    custom_fields: Dict = Field(default_factory=dict, description="Custom fields for specific user types") 