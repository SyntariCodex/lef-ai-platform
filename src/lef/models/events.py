"""
Events model for the LEF system.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict
from pydantic import BaseModel, Field

class EventType(str, Enum):
    """Event type enum."""
    SYSTEM = "system"
    TASK = "task"
    USER = "user"
    ERROR = "error"
    SECURITY = "security"
    BACKUP = "backup"

class EventSeverity(str, Enum):
    """Event severity enum."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class Event(BaseModel):
    """Event model."""
    id: Optional[int] = None
    type: EventType
    severity: EventSeverity = EventSeverity.INFO
    source: str = Field(..., description="Event source (component/module)")
    message: str = Field(..., description="Event message")
    details: Optional[Dict] = Field(None, description="Additional event details")
    task_id: Optional[int] = Field(None, description="Related task ID")
    user_id: Optional[str] = Field(None, description="Related user ID")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "type": "TASK",
                "severity": "INFO",
                "source": "task_manager",
                "message": "Task completed successfully",
                "details": {"task_name": "data_processing", "duration": 120},
                "task_id": 1
            }
        } 