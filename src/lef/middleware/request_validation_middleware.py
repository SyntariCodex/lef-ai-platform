"""
Request validation middleware for validating and sanitizing incoming requests
"""

import logging
import re
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from ..services.logging_service import LoggingService

logger = logging.getLogger(__name__)

class RequestValidationMiddleware(BaseHTTPMiddleware):
    """Middleware for validating and sanitizing incoming requests"""
    
    def __init__(self, app):
        super().__init__(app)
        self.logging_service = LoggingService()
        
        # Define patterns for validation
        self.safe_patterns = {
            "username": re.compile(r"^[a-zA-Z0-9_-]{3,32}$"),
            "email": re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"),
            "path": re.compile(r"^[a-zA-Z0-9/_-]+$"),
            "id": re.compile(r"^[a-zA-Z0-9_-]+$")
        }
        
    async def dispatch(self, request: Request, call_next):
        """Process the request and validate/sanitize input"""
        try:
            # Validate path parameters
            for param_name, param_value in request.path_params.items():
                if param_name in self.safe_patterns:
                    if not self.safe_patterns[param_name].match(str(param_value)):
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Invalid {param_name} format"
                        )
            
            # Validate query parameters
            for param_name, param_value in request.query_params.items():
                if param_name in self.safe_patterns:
                    if not self.safe_patterns[param_name].match(str(param_value)):
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Invalid {param_name} format"
                        )
            
            # Validate headers
            for header_name, header_value in request.headers.items():
                if header_name.lower() in ["x-forwarded-for", "x-real-ip"]:
                    if not self._is_valid_ip(header_value):
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid IP address in header"
                        )
            
            # Check content type
            if request.method in ["POST", "PUT", "PATCH"]:
                content_type = request.headers.get("content-type", "")
                if not content_type.startswith("application/json"):
                    raise HTTPException(
                        status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                        detail="Content-Type must be application/json"
                    )
            
            # Check request size
            content_length = request.headers.get("content-length")
            if content_length and int(content_length) > 10 * 1024 * 1024:  # 10MB limit
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail="Request too large"
                )
            
            return await call_next(request)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Request validation failed: {e}")
            await self.logging_service.log_message(
                "error",
                f"Request validation failed: {e}",
                details={
                    "ip": request.client.host,
                    "path": request.url.path,
                    "method": request.method
                }
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid request"
            )
            
    def _is_valid_ip(self, ip: str) -> bool:
        """Validate IP address format"""
        try:
            parts = ip.split(".")
            return len(parts) == 4 and all(0 <= int(part) <= 255 for part in parts)
        except (AttributeError, TypeError, ValueError):
            return False 