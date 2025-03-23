"""
Rate limiting middleware for applying rate limiting to all API endpoints
"""

import logging
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from ..services.rate_limit_service import RateLimitService
from ..services.logging_service import LoggingService

logger = logging.getLogger(__name__)

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for applying rate limiting to all API endpoints"""
    
    def __init__(self, app):
        super().__init__(app)
        self.rate_limit_service = RateLimitService()
        self.logging_service = LoggingService()
        
    async def dispatch(self, request: Request, call_next):
        """Process the request and apply rate limiting"""
        try:
            # Skip rate limiting for certain paths
            if request.url.path in ["/docs", "/redoc", "/openapi.json"]:
                return await call_next(request)
                
            # Get client IP
            client_host = request.client.host
            
            # Check rate limit
            allowed, info = await self.rate_limit_service.check_rate_limit(client_host)
            
            if not allowed:
                await self.logging_service.log_message(
                    "warning",
                    "Rate limit exceeded",
                    details={
                        "ip": client_host,
                        "path": request.url.path,
                        "method": request.method,
                        "info": info.dict()
                    }
                )
                
                return Response(
                    content="Rate limit exceeded",
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    headers={
                        "X-RateLimit-Remaining": str(info.remaining_requests),
                        "X-RateLimit-Reset": info.reset_time.isoformat(),
                        "X-RateLimit-Burst-Remaining": str(info.burst_remaining)
                    }
                )
                
            # Add rate limit headers to response
            response = await call_next(request)
            response.headers["X-RateLimit-Remaining"] = str(info.remaining_requests)
            response.headers["X-RateLimit-Reset"] = info.reset_time.isoformat()
            response.headers["X-RateLimit-Burst-Remaining"] = str(info.burst_remaining)
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to apply rate limiting: {e}")
            await self.logging_service.log_message(
                "error",
                f"Failed to apply rate limiting: {e}",
                details={
                    "ip": request.client.host,
                    "path": request.url.path,
                    "method": request.method
                }
            )
            return await call_next(request) 