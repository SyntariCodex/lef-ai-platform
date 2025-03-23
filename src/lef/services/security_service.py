"""
Security service for handling security-related operations
"""

import logging
import os
import re
from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from ..services.logging_service import LoggingService
from ..services.alert_service import AlertService, AlertSeverity
from ..services.encryption_service import EncryptionService

logger = logging.getLogger(__name__)

class SecurityConfig(BaseModel):
    """Security configuration model"""
    password_min_length: int = Field(default=12, ge=8)
    password_require_uppercase: bool = Field(default=True)
    password_require_lowercase: bool = Field(default=True)
    password_require_numbers: bool = Field(default=True)
    password_require_special: bool = Field(default=True)
    max_login_attempts: int = Field(default=5, ge=1)
    lockout_duration_minutes: int = Field(default=30, ge=1)
    session_timeout_minutes: int = Field(default=60, ge=1)
    require_2fa: bool = Field(default=True)
    allowed_ips: List[str] = Field(default_factory=list)
    blocked_ips: List[str] = Field(default_factory=list)
    rate_limit_requests: int = Field(default=100, ge=1)
    rate_limit_window_minutes: int = Field(default=1, ge=1)

class SecurityEvent(BaseModel):
    """Security event model"""
    event_type: str
    severity: AlertSeverity
    timestamp: datetime
    user_id: Optional[str] = None
    ip_address: Optional[str] = None
    details: Dict[str, any] = Field(default_factory=dict)

class SecurityService:
    """Service for handling security-related operations"""
    
    def __init__(self):
        self.logging_service = LoggingService()
        self.alert_service = AlertService()
        self.encryption_service = EncryptionService()
        
        # Load security configuration
        self.config = SecurityConfig()
        
        # Initialize security state
        self.login_attempts: Dict[str, int] = {}
        self.locked_accounts: Dict[str, datetime] = {}
        self.active_sessions: Dict[str, datetime] = {}
        self.security_events: List[SecurityEvent] = []
        
    async def initialize(self):
        """Initialize the service"""
        await self.encryption_service.initialize()
        
    def validate_password(self, password: str) -> bool:
        """Validate password strength"""
        try:
            if len(password) < self.config.password_min_length:
                return False
                
            if self.config.password_require_uppercase and not re.search(r"[A-Z]", password):
                return False
                
            if self.config.password_require_lowercase and not re.search(r"[a-z]", password):
                return False
                
            if self.config.password_require_numbers and not re.search(r"\d", password):
                return False
                
            if self.config.password_require_special and not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to validate password: {e}")
            return False
            
    async def check_login_attempts(self, user_id: str) -> bool:
        """Check if user has exceeded login attempts"""
        try:
            if user_id in self.locked_accounts:
                lockout_end = self.locked_accounts[user_id]
                if datetime.now() < lockout_end:
                    return False
                else:
                    # Reset lockout
                    del self.locked_accounts[user_id]
                    self.login_attempts[user_id] = 0
                    
            if user_id in self.login_attempts:
                if self.login_attempts[user_id] >= self.config.max_login_attempts:
                    # Lock account
                    self.locked_accounts[user_id] = datetime.now() + timedelta(
                        minutes=self.config.lockout_duration_minutes
                    )
                    await self.log_security_event(
                        "account_locked",
                        AlertSeverity.WARNING,
                        user_id=user_id,
                        details={"reason": "max_login_attempts_exceeded"}
                    )
                    return False
                    
            return True
            
        except Exception as e:
            logger.error(f"Failed to check login attempts: {e}")
            return False
            
    async def record_login_attempt(self, user_id: str, success: bool):
        """Record a login attempt"""
        try:
            if success:
                if user_id in self.login_attempts:
                    del self.login_attempts[user_id]
                if user_id in self.locked_accounts:
                    del self.locked_accounts[user_id]
            else:
                if user_id not in self.login_attempts:
                    self.login_attempts[user_id] = 0
                self.login_attempts[user_id] += 1
                
        except Exception as e:
            logger.error(f"Failed to record login attempt: {e}")
            
    async def validate_ip(self, ip_address: str) -> bool:
        """Validate IP address"""
        try:
            if ip_address in self.config.blocked_ips:
                return False
                
            if self.config.allowed_ips and ip_address not in self.config.allowed_ips:
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to validate IP: {e}")
            return False
            
    async def create_session(self, user_id: str) -> str:
        """Create a new session"""
        try:
            session_id = os.urandom(32).hex()
            self.active_sessions[session_id] = datetime.now()
            await self.log_security_event(
                "session_created",
                AlertSeverity.INFO,
                user_id=user_id,
                details={"session_id": session_id}
            )
            return session_id
            
        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            raise
            
    async def validate_session(self, session_id: str) -> bool:
        """Validate a session"""
        try:
            if session_id not in self.active_sessions:
                return False
                
            session_time = self.active_sessions[session_id]
            if datetime.now() - session_time > timedelta(minutes=self.config.session_timeout_minutes):
                del self.active_sessions[session_id]
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to validate session: {e}")
            return False
            
    async def end_session(self, session_id: str):
        """End a session"""
        try:
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
                
        except Exception as e:
            logger.error(f"Failed to end session: {e}")
            
    async def log_security_event(
        self,
        event_type: str,
        severity: AlertSeverity,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        details: Optional[Dict[str, any]] = None
    ):
        """Log a security event"""
        try:
            event = SecurityEvent(
                event_type=event_type,
                severity=severity,
                timestamp=datetime.now(),
                user_id=user_id,
                ip_address=ip_address,
                details=details or {}
            )
            
            self.security_events.append(event)
            
            # Log to logging service
            await self.logging_service.log_message(
                "security",
                f"Security event: {event_type}",
                user_id=user_id,
                details=event.dict()
            )
            
            # Create alert for high severity events
            if severity in [AlertSeverity.ERROR, AlertSeverity.CRITICAL]:
                await self.alert_service.create_alert(
                    title=f"Security Alert: {event_type}",
                    message=f"Security event detected: {event_type}",
                    severity=severity,
                    details=event.dict()
                )
                
        except Exception as e:
            logger.error(f"Failed to log security event: {e}")
            
    async def get_security_events(
        self,
        event_type: Optional[str] = None,
        severity: Optional[AlertSeverity] = None,
        user_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[SecurityEvent]:
        """Get security events with filters"""
        try:
            events = self.security_events
            
            if event_type:
                events = [e for e in events if e.event_type == event_type]
                
            if severity:
                events = [e for e in events if e.severity == severity]
                
            if user_id:
                events = [e for e in events if e.user_id == user_id]
                
            if start_time:
                events = [e for e in events if e.timestamp >= start_time]
                
            if end_time:
                events = [e for e in events if e.timestamp <= end_time]
                
            return events
            
        except Exception as e:
            logger.error(f"Failed to get security events: {e}")
            return []
            
    async def update_security_config(self, config: SecurityConfig):
        """Update security configuration"""
        try:
            self.config = config
            await self.log_security_event(
                "config_updated",
                AlertSeverity.INFO,
                details={"config": config.dict()}
            )
            
        except Exception as e:
            logger.error(f"Failed to update security config: {e}")
            raise 