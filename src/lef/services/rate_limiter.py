"""
Rate limiter service for AI Bridge System
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict

logger = logging.getLogger(__name__)

class RateLimitConfig:
    """Configuration for rate limiting"""
    def __init__(
        self,
        max_requests: int = 100,
        window_seconds: int = 60,
        burst_size: int = 10
    ):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.burst_size = burst_size

class RateLimiter:
    """Rate limiter for controlling message flow"""
    
    def __init__(self):
        self._requests: Dict[str, List[datetime]] = defaultdict(list)
        self._configs: Dict[str, RateLimitConfig] = {}
        self._lock = asyncio.Lock()
        
    def configure_service(self, service_id: str, config: RateLimitConfig):
        """Configure rate limiting for a service"""
        self._configs[service_id] = config
        
    async def check_rate_limit(self, service_id: str) -> bool:
        """Check if a service has exceeded its rate limit"""
        async with self._lock:
            now = datetime.utcnow()
            config = self._configs.get(service_id, RateLimitConfig())
            
            # Clean old requests
            window_start = now - timedelta(seconds=config.window_seconds)
            self._requests[service_id] = [
                req_time for req_time in self._requests[service_id]
                if req_time > window_start
            ]
            
            # Check if limit exceeded
            if len(self._requests[service_id]) >= config.max_requests:
                logger.warning(
                    f"Rate limit exceeded for service {service_id}: "
                    f"{len(self._requests[service_id])}/{config.max_requests} requests"
                )
                return False
                
            return True
            
    async def record_message(self, service_id: str):
        """Record a message for rate limiting"""
        async with self._lock:
            now = datetime.utcnow()
            self._requests[service_id].append(now)
            
            # Keep only recent requests
            config = self._configs.get(service_id, RateLimitConfig())
            window_start = now - timedelta(seconds=config.window_seconds)
            self._requests[service_id] = [
                req_time for req_time in self._requests[service_id]
                if req_time > window_start
            ]
            
    async def get_rate_limit_status(self, service_id: str) -> Dict:
        """Get current rate limit status for a service"""
        async with self._lock:
            config = self._configs.get(service_id, RateLimitConfig())
            now = datetime.utcnow()
            window_start = now - timedelta(seconds=config.window_seconds)
            
            # Clean old requests
            self._requests[service_id] = [
                req_time for req_time in self._requests[service_id]
                if req_time > window_start
            ]
            
            return {
                "service_id": service_id,
                "current_requests": len(self._requests[service_id]),
                "max_requests": config.max_requests,
                "window_seconds": config.window_seconds,
                "burst_size": config.burst_size,
                "remaining_requests": max(0, config.max_requests - len(self._requests[service_id])),
                "reset_time": window_start + timedelta(seconds=config.window_seconds)
            }
            
    async def reset_rate_limit(self, service_id: str):
        """Reset rate limit for a service"""
        async with self._lock:
            self._requests[service_id] = []
            
    async def get_all_rate_limits(self) -> Dict[str, Dict]:
        """Get rate limit status for all services"""
        return {
            service_id: await self.get_rate_limit_status(service_id)
            for service_id in self._configs
        } 