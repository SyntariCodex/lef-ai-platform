"""
Authentication Service for user management and security
"""

import logging
import jwt
import bcrypt
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from ..models.user import User, UserRole, UserStatus
from ..models.alert import Alert, AlertSeverity, AlertStatus
import os
from jose import JWTError
from passlib.context import CryptContext
from pydantic import BaseModel, Field
from fastapi import HTTPException, status

from ..services.logging_service import LoggingService
from ..services.alert_service import AlertService
from ..services.monitoring_service import MonitoringService

logger = logging.getLogger(__name__)

class Token(BaseModel):
    """JWT token model"""
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime
    refresh_token: Optional[str] = None

class TokenData(BaseModel):
    """Token data model"""
    username: Optional[str] = None
    roles: list[str] = Field(default_factory=list)
    permissions: list[str] = Field(default_factory=list)
    exp: Optional[datetime] = None

class AuthService:
    def __init__(self):
        self.logging_service = LoggingService()
        self.alert_service = AlertService()
        self.monitoring_service = MonitoringService()
        
        # Security configuration
        self.secret_key = os.getenv("JWT_SECRET_KEY")
        self.algorithm = "HS256"
        self.access_token_expire_minutes = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
        self.refresh_token_expire_days = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7"))
        
        # Password hashing
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        # Rate limiting
        self.failed_attempts: Dict[str, int] = {}
        self.lockout_minutes = 15
        self.max_failed_attempts = 5
        
        self.users: Dict[str, User] = {}
        self.session_tokens: Dict[str, str] = {}  # token -> username
        self._load_default_admin()

    def _load_default_admin(self):
        """Load default admin user"""
        admin_password = "admin123"  # Should be changed on first login
        hashed = bcrypt.hashpw(admin_password.encode(), bcrypt.gensalt())
        self.users["admin"] = User(
            username="admin",
            email="admin@lef.ai",
            hashed_password=hashed.decode(),
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE,
            permissions=["*"]  # All permissions
        )

    def create_user(self, username: str, email: str, password: str, role: UserRole = UserRole.VIEWER) -> Optional[User]:
        """Create a new user"""
        try:
            if username in self.users:
                self.logger.warning(f"Username {username} already exists")
                return None

            hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
            user = User(
                username=username,
                email=email,
                hashed_password=hashed.decode(),
                role=role,
                status=UserStatus.ACTIVE
            )
            self.users[username] = user
            self.logger.info(f"Created new user: {username}")
            return user
        except Exception as e:
            self.logger.error(f"Error creating user: {e}")
            return None

    async def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        try:
            return self.pwd_context.verify(plain_password, hashed_password)
        except Exception as e:
            await self.logging_service.log(
                level="ERROR",
                message=f"Password verification failed: {e}",
                service="auth_service"
            )
            return False
            
    def get_password_hash(self, password: str) -> str:
        """Generate password hash"""
        return self.pwd_context.hash(password)
        
    def create_access_token(self, data: Dict[str, Any]) -> Token:
        """Create a new access token"""
        try:
            to_encode = data.copy()
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
            to_encode.update({"exp": expire})
            
            encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            
            # Create refresh token
            refresh_expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
            refresh_data = data.copy()
            refresh_data.update({"exp": refresh_expire})
            refresh_token = jwt.encode(refresh_data, self.secret_key, algorithm=self.algorithm)
            
            return Token(
                access_token=encoded_jwt,
                expires_at=expire,
                refresh_token=refresh_token
            )
            
        except Exception as e:
            await self.logging_service.log(
                level="ERROR",
                message=f"Token creation failed: {e}",
                service="auth_service"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create token"
            )
            
    async def verify_token(self, token: str) -> TokenData:
        """Verify and decode a token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return TokenData(**payload)
        except JWTError as e:
            await self.logging_service.log(
                level="ERROR",
                message=f"Token verification failed: {e}",
                service="auth_service"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
            
    async def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate a user"""
        try:
            # Check for account lockout
            if username in self.failed_attempts:
                if self.failed_attempts[username] >= self.max_failed_attempts:
                    await self.logging_service.log(
                        level="WARNING",
                        message=f"Account locked for user: {username}",
                        service="auth_service"
                    )
                    await self.alert_service.create_alert(
                        title="Account Locked",
                        message=f"Account locked for user: {username}",
                        severity=AlertSeverity.WARNING
                    )
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Account is locked"
                    )
                    
            # TODO: Get user from database
            # For now, using mock data
            user = {
                "username": username,
                "hashed_password": self.get_password_hash("password"),  # Mock password
                "roles": ["user"],
                "permissions": ["read"]
            }
            
            if not await self.verify_password(password, user["hashed_password"]):
                # Record failed attempt
                self.failed_attempts[username] = self.failed_attempts.get(username, 0) + 1
                
                await self.logging_service.log(
                    level="WARNING",
                    message=f"Failed login attempt for user: {username}",
                    service="auth_service"
                )
                
                if self.failed_attempts[username] >= self.max_failed_attempts:
                    await self.alert_service.create_alert(
                        title="Multiple Failed Login Attempts",
                        message=f"Multiple failed login attempts detected for user: {username}",
                        severity=AlertSeverity.WARNING
                    )
                    
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials"
                )
                
            # Reset failed attempts on successful login
            self.failed_attempts.pop(username, None)
            
            # Record successful login
            await self.monitoring_service._record_metric(
                "login_attempts",
                1,
                {"status": "success", "username": username}
            )
            
            return user
            
        except Exception as e:
            await self.logging_service.log(
                level="ERROR",
                message=f"Authentication failed: {e}",
                service="auth_service"
            )
            raise
            
    async def refresh_token(self, refresh_token: str) -> Token:
        """Refresh an access token using a refresh token"""
        try:
            # Verify refresh token
            token_data = await self.verify_token(refresh_token)
            
            # Create new access token
            return self.create_access_token({
                "username": token_data.username,
                "roles": token_data.roles,
                "permissions": token_data.permissions
            })
            
        except Exception as e:
            await self.logging_service.log(
                level="ERROR",
                message=f"Token refresh failed: {e}",
                service="auth_service"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
            
    async def revoke_token(self, token: str) -> bool:
        """Revoke a token"""
        try:
            # TODO: Implement token revocation logic
            # This could involve adding the token to a blacklist in Redis
            return True
        except Exception as e:
            await self.logging_service.log(
                level="ERROR",
                message=f"Token revocation failed: {e}",
                service="auth_service"
            )
            return False

    def validate_token(self, token: str) -> Tuple[bool, Optional[User]]:
        """Validate a JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            username = payload.get("sub")
            if not username or token not in self.session_tokens:
                return False, None

            user = self.users.get(username)
            if not user or user.status != UserStatus.ACTIVE:
                return False, None

            return True, user

        except jwt.ExpiredSignatureError:
            self.logger.warning(f"Expired token for user {username}")
            return False, None
        except jwt.InvalidTokenError:
            self.logger.warning("Invalid token")
            return False, None

    def revoke_all_tokens(self, username: str) -> bool:
        """Revoke all session tokens for a user"""
        try:
            user = self.users.get(username)
            if not user:
                return False

            # Remove tokens from session_tokens dict
            for token in user.session_tokens:
                self.session_tokens.pop(token, None)

            # Clear user's session tokens
            user.session_tokens.clear()
            return True
        except Exception as e:
            self.logger.error(f"Error revoking all tokens: {e}")
            return False

    def change_password(self, username: str, old_password: str, new_password: str) -> bool:
        """Change user password"""
        try:
            user = self.users.get(username)
            if not user:
                return False

            if not bcrypt.checkpw(old_password.encode(), user.hashed_password.encode()):
                return False

            hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())
            user.hashed_password = hashed.decode()
            user.last_password_change = datetime.utcnow()
            return True
        except Exception as e:
            self.logger.error(f"Error changing password: {e}")
            return False

    def reset_password(self, username: str) -> Optional[str]:
        """Generate password reset token"""
        try:
            user = self.users.get(username)
            if not user:
                return None

            token = secrets.token_urlsafe(32)
            user.password_reset_token = token
            user.password_reset_expires = datetime.utcnow() + timedelta(hours=1)
            return token
        except Exception as e:
            self.logger.error(f"Error generating reset token: {e}")
            return None

    def verify_reset_token(self, token: str, new_password: str) -> bool:
        """Verify and apply password reset token"""
        try:
            for user in self.users.values():
                if (user.password_reset_token == token and 
                    user.password_reset_expires and 
                    datetime.utcnow() < user.password_reset_expires):
                    
                    hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())
                    user.hashed_password = hashed.decode()
                    user.last_password_change = datetime.utcnow()
                    user.password_reset_token = None
                    user.password_reset_expires = None
                    return True
            return False
        except Exception as e:
            self.logger.error(f"Error verifying reset token: {e}")
            return False

    def enable_2fa(self, username: str) -> Optional[str]:
        """Enable 2FA for a user"""
        try:
            user = self.users.get(username)
            if not user:
                return None

            secret = secrets.token_urlsafe(32)
            user.two_factor_secret = secret
            user.two_factor_enabled = True
            return secret
        except Exception as e:
            self.logger.error(f"Error enabling 2FA: {e}")
            return None

    def verify_2fa(self, username: str, code: str) -> bool:
        """Verify 2FA code"""
        try:
            user = self.users.get(username)
            if not user or not user.two_factor_enabled or not user.two_factor_secret:
                return False

            # TODO: Implement actual 2FA verification
            # This is a placeholder implementation
            return code == "123456"  # Replace with actual 2FA verification
        except Exception as e:
            self.logger.error(f"Error verifying 2FA: {e}")
            return False

    def disable_2fa(self, username: str) -> bool:
        """Disable 2FA for a user"""
        try:
            user = self.users.get(username)
            if not user:
                return False

            user.two_factor_enabled = False
            user.two_factor_secret = None
            return True
        except Exception as e:
            self.logger.error(f"Error disabling 2FA: {e}")
            return False

    def create_api_key(self, username: str, name: str) -> Optional[str]:
        """Create a new API key for a user"""
        try:
            user = self.users.get(username)
            if not user:
                return None

            key = secrets.token_urlsafe(32)
            user.api_keys.append(key)
            return key
        except Exception as e:
            self.logger.error(f"Error creating API key: {e}")
            return None

    def revoke_api_key(self, username: str, key: str) -> bool:
        """Revoke an API key"""
        try:
            user = self.users.get(username)
            if not user or key not in user.api_keys:
                return False

            user.api_keys.remove(key)
            return True
        except Exception as e:
            self.logger.error(f"Error revoking API key: {e}")
            return False

    def check_permission(self, username: str, permission: str) -> bool:
        """Check if user has a specific permission"""
        try:
            user = self.users.get(username)
            if not user:
                return False

            if "*" in user.permissions:  # Wildcard permission
                return True

            return permission in user.permissions
        except Exception as e:
            self.logger.error(f"Error checking permission: {e}")
            return False

    def add_permission(self, username: str, permission: str) -> bool:
        """Add a permission to a user"""
        try:
            user = self.users.get(username)
            if not user:
                return False

            if permission not in user.permissions:
                user.permissions.append(permission)
            return True
        except Exception as e:
            self.logger.error(f"Error adding permission: {e}")
            return False

    def remove_permission(self, username: str, permission: str) -> bool:
        """Remove a permission from a user"""
        try:
            user = self.users.get(username)
            if not user:
                return False

            if permission in user.permissions:
                user.permissions.remove(permission)
            return True
        except Exception as e:
            self.logger.error(f"Error removing permission: {e}")
            return False

    def log_activity(self, username: str, action: str, details: Dict) -> bool:
        """Log user activity"""
        try:
            user = self.users.get(username)
            if not user:
                return False

            log_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "action": action,
                "details": details
            }
            user.audit_log.append(log_entry)
            user.last_activity = datetime.utcnow()
            return True
        except Exception as e:
            self.logger.error(f"Error logging activity: {e}")
            return False 