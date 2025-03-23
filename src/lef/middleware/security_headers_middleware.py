"""
Security headers middleware for adding security headers to all responses
"""

import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from ..services.logging_service import LoggingService

logger = logging.getLogger(__name__)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware for adding security headers to all responses"""
    
    def __init__(self, app):
        super().__init__(app)
        self.logging_service = LoggingService()
        
    async def dispatch(self, request: Request, call_next):
        """Process the request and add security headers"""
        try:
            response = await call_next(request)
            
            # Add security headers
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';"
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
            response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to add security headers: {e}")
            await self.logging_service.log_message(
                "error",
                f"Failed to add security headers: {e}",
                details={
                    "ip": request.client.host,
                    "path": request.url.path,
                    "method": request.method
                }
            )
            return await call_next(request) 