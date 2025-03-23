"""
Rate limiting service for handling API rate limiting
"""

import logging
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from ..services.logging_service import LoggingService
from ..services.alert_service import AlertService, AlertSeverity

logger = logging.getLogger(__name__)

class RateLimitConfig(BaseModel):
    """Rate limit configuration model"""
    requests_per_minute: int = Field(default=100, ge=1)
    burst_size: int = Field(default=10, ge=1)
    block_duration_minutes: int = Field(default=5, ge=1)
    enabled: bool = Field(default=True)

class RateLimitInfo(BaseModel):
    """Rate limit information model"""
    remaining_requests: int
    reset_time: datetime
    burst_remaining: int
    is_blocked: bool
    block_end_time: Optional[datetime] = None

class RateLimitService:
    """Service for handling API rate limiting"""
    
    def __init__(self):
        self.logging_service = LoggingService()
        self.alert_service = AlertService()
        
        # Load rate limit configuration
        self.config = RateLimitConfig()
        
        # Initialize rate limit state
        self.request_counts: Dict[str, List[float]] = {}
        self.burst_counts: Dict[str, int] = {}
        self.blocked_ips: Dict[str, datetime] = {}
        
    async def initialize(self):
        """Initialize the service"""
        pass
        
    async def check_rate_limit(self, ip_address: str) -> Tuple[bool, RateLimitInfo]:
        """Check if request should be rate limited"""
        try:
            if not self.config.enabled:
                return True, RateLimitInfo(
                    remaining_requests=self.config.requests_per_minute,
                    reset_time=datetime.now() + timedelta(minutes=1),
                    burst_remaining=self.config.burst_size,
                    is_blocked=False
                )
                
            # Check if IP is blocked
            if ip_address in self.blocked_ips:
                block_end = self.blocked_ips[ip_address]
                if datetime.now() < block_end:
                    return False, RateLimitInfo(
                        remaining_requests=0,
                        reset_time=block_end,
                        burst_remaining=0,
                        is_blocked=True,
                        block_end_time=block_end
                    )
                else:
                    # Reset block
                    del self.blocked_ips[ip_address]
                    
            # Get current time
            current_time = time.time()
            
            # Initialize request counts for IP if not exists
            if ip_address not in self.request_counts:
                self.request_counts[ip_address] = []
                self.burst_counts[ip_address] = self.config.burst_size
                
            # Clean old requests
            self.request_counts[ip_address] = [
                t for t in self.request_counts[ip_address]
                if current_time - t < 60
            ]
            
            # Check if rate limit exceeded
            if len(self.request_counts[ip_address]) >= self.config.requests_per_minute:
                # Check burst allowance
                if self.burst_counts[ip_address] > 0:
                    self.burst_counts[ip_address] -= 1
                    self.request_counts[ip_address].append(current_time)
                    return True, RateLimitInfo(
                        remaining_requests=0,
                        reset_time=datetime.fromtimestamp(
                            self.request_counts[ip_address][0] + 60
                        ),
                        burst_remaining=self.burst_counts[ip_address],
                        is_blocked=False
                    )
                else:
                    # Block IP
                    block_end = datetime.now() + timedelta(
                        minutes=self.config.block_duration_minutes
                    )
                    self.blocked_ips[ip_address] = block_end
                    
                    await self.log_security_event(
                        "rate_limit_exceeded",
                        AlertSeverity.WARNING,
                        ip_address=ip_address,
                        details={
                            "requests": len(self.request_counts[ip_address]),
                            "block_duration": self.config.block_duration_minutes
                        }
                    )
                    
                    return False, RateLimitInfo(
                        remaining_requests=0,
                        reset_time=block_end,
                        burst_remaining=0,
                        is_blocked=True,
                        block_end_time=block_end
                    )
                    
            # Add request
            self.request_counts[ip_address].append(current_time)
            
            # Reset burst count if needed
            if len(self.request_counts[ip_address]) == 1:
                self.burst_counts[ip_address] = self.config.burst_size
                
            return True, RateLimitInfo(
                remaining_requests=self.config.requests_per_minute - len(self.request_counts[ip_address]),
                reset_time=datetime.fromtimestamp(
                    self.request_counts[ip_address][0] + 60
                ),
                burst_remaining=self.burst_counts[ip_address],
                is_blocked=False
            )
            
        except Exception as e:
            logger.error(f"Failed to check rate limit: {e}")
            return True, RateLimitInfo(
                remaining_requests=self.config.requests_per_minute,
                reset_time=datetime.now() + timedelta(minutes=1),
                burst_remaining=self.config.burst_size,
                is_blocked=False
            )
            
    async def get_rate_limit_info(self, ip_address: str) -> RateLimitInfo:
        """Get rate limit information for IP"""
        try:
            if ip_address not in self.request_counts:
                return RateLimitInfo(
                    remaining_requests=self.config.requests_per_minute,
                    reset_time=datetime.now() + timedelta(minutes=1),
                    burst_remaining=self.config.burst_size,
                    is_blocked=False
                )
                
            # Check if IP is blocked
            if ip_address in self.blocked_ips:
                block_end = self.blocked_ips[ip_address]
                if datetime.now() < block_end:
                    return RateLimitInfo(
                        remaining_requests=0,
                        reset_time=block_end,
                        burst_remaining=0,
                        is_blocked=True,
                        block_end_time=block_end
                    )
                    
            # Get current time
            current_time = time.time()
            
            # Clean old requests
            self.request_counts[ip_address] = [
                t for t in self.request_counts[ip_address]
                if current_time - t < 60
            ]
            
            return RateLimitInfo(
                remaining_requests=self.config.requests_per_minute - len(self.request_counts[ip_address]),
                reset_time=datetime.fromtimestamp(
                    self.request_counts[ip_address][0] + 60
                ) if self.request_counts[ip_address] else datetime.now() + timedelta(minutes=1),
                burst_remaining=self.burst_counts[ip_address],
                is_blocked=False
            )
            
        except Exception as e:
            logger.error(f"Failed to get rate limit info: {e}")
            return RateLimitInfo(
                remaining_requests=self.config.requests_per_minute,
                reset_time=datetime.now() + timedelta(minutes=1),
                burst_remaining=self.config.burst_size,
                is_blocked=False
            )
            
    async def update_rate_limit_config(self, config: RateLimitConfig):
        """Update rate limit configuration"""
        try:
            self.config = config
            await self.log_security_event(
                "rate_limit_config_updated",
                AlertSeverity.INFO,
                details={"config": config.dict()}
            )
            
        except Exception as e:
            logger.error(f"Failed to update rate limit config: {e}")
            raise
            
    async def log_security_event(
        self,
        event_type: str,
        severity: AlertSeverity,
        ip_address: Optional[str] = None,
        details: Optional[Dict[str, any]] = None
    ):
        """Log a security event"""
        try:
            # Log to logging service
            await self.logging_service.log_message(
                "security",
                f"Rate limit event: {event_type}",
                details=details or {}
            )
            
            # Create alert for high severity events
            if severity in [AlertSeverity.ERROR, AlertSeverity.CRITICAL]:
                await self.alert_service.create_alert(
                    title=f"Rate Limit Alert: {event_type}",
                    message=f"Rate limit event detected: {event_type}",
                    severity=severity,
                    details=details or {}
                )
                
        except Exception as e:
            logger.error(f"Failed to log security event: {e}")
            
    async def cleanup(self):
        """Clean up old rate limit data"""
        try:
            current_time = time.time()
            
            # Clean up request counts
            for ip in list(self.request_counts.keys()):
                self.request_counts[ip] = [
                    t for t in self.request_counts[ip]
                    if current_time - t < 60
                ]
                if not self.request_counts[ip]:
                    del self.request_counts[ip]
                    
            # Clean up blocked IPs
            for ip in list(self.blocked_ips.keys()):
                if datetime.now() >= self.blocked_ips[ip]:
                    del self.blocked_ips[ip]
                    
        except Exception as e:
            logger.error(f"Failed to cleanup rate limit data: {e}") 