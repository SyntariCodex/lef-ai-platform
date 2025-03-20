"""
LEF Business Operations System - Lambda Function Handlers

This package contains AWS Lambda function handlers for managing various aspects of the LEF business operations system:
- Project Management
- Financial Management
- Stakeholder Management
- Resource Management
"""

from typing import Dict, Any, Optional

# Common response type for all handlers
HandlerResponse = Dict[str, Any]

def create_response(status_code: int, body: Dict[str, Any]) -> HandlerResponse:
    """Create a standardized response format for all handlers."""
    return {
        'statusCode': status_code,
        'body': body,
        'headers': {
            'Content-Type': 'application/json'
        }
    }

def create_error_response(error_message: str, error_code: Optional[str] = None) -> HandlerResponse:
    """Create a standardized error response."""
    return create_response(400, {
        'error': True,
        'message': error_message,
        'code': error_code or 'UNKNOWN_ERROR'
    }) 