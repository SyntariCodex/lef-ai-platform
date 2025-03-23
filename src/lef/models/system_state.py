"""
System state model for the LEF system.
"""

from datetime import datetime
from typing import Optional, Dict
from pydantic import BaseModel, Field

class SystemState(BaseModel):
    """System state model."""
    id: Optional[int] = None
    status: str = Field(..., description="Current system status")
    version: str = Field(..., description="System version")
    uptime: float = Field(..., description="System uptime in seconds")
    last_backup: Optional[datetime] = Field(None, description="Last backup timestamp")
    last_error: Optional[str] = Field(None, description="Last error message")
    error_count: int = Field(0, description="Number of errors since startup")
    memory_usage: float = Field(..., description="Current memory usage in MB")
    cpu_usage: float = Field(..., description="Current CPU usage percentage")
    active_tasks: int = Field(0, description="Number of active tasks")
    completed_tasks: int = Field(0, description="Number of completed tasks")
    failed_tasks: int = Field(0, description="Number of failed tasks")
    system_metrics: Dict = Field(default_factory=dict, description="Additional system metrics")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "status": "running",
                "version": "1.0.0",
                "uptime": 3600.0,
                "memory_usage": 256.5,
                "cpu_usage": 25.0,
                "active_tasks": 5
            }
        }
