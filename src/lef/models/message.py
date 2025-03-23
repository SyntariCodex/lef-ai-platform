"""
Message models for AI Bridge System
"""

from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class MessageType(str, Enum):
    """Types of messages that can be sent through the bridge"""
    STATE_UPDATE = "state_update"
    ANALYSIS_REQUEST = "analysis_request"
    ANALYSIS_RESPONSE = "analysis_response"
    ERROR = "error"
    HEARTBEAT = "heartbeat"
    CONFIG_UPDATE = "config_update"
    HEALTH_CHECK = "health_check"

class MessagePriority(str, Enum):
    """Priority levels for messages"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Message(BaseModel):
    """Message model for AI Bridge communication"""
    id: str = Field(..., description="Unique message ID")
    type: MessageType = Field(..., description="Type of message")
    priority: MessagePriority = Field(MessagePriority.MEDIUM, description="Message priority")
    content: Dict[str, Any] = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")
    source: Optional[str] = Field(None, description="Source service ID")
    target: Optional[str] = Field(None, description="Target service ID")
    correlation_id: Optional[str] = Field(None, description="ID for correlating related messages")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional message metadata")
    retry_count: int = Field(default=0, description="Number of retry attempts")
    max_retries: int = Field(default=3, description="Maximum number of retry attempts")
    error: Optional[str] = Field(None, description="Error message if applicable")
    processed: bool = Field(default=False, description="Whether the message has been processed")
    processed_at: Optional[datetime] = Field(None, description="When the message was processed") 