"""
Task model for the LEF system.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict
from pydantic import BaseModel, Field

class TaskStatus(str, Enum):
    """Task status enum."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    FAILED = "failed"

class TaskPriority(str, Enum):
    """Task priority enum."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class TaskCreate(BaseModel):
    """Schema for creating a new task."""
    name: str = Field(..., description="Task name")
    phase: str = Field(..., description="Development phase this task belongs to")
    priority: TaskPriority = Field(..., description="Task priority level")
    description: Optional[str] = Field(None, description="Detailed task description")
    estimated_hours: Optional[float] = Field(None, description="Estimated hours to complete")
    task_metadata: Optional[dict] = Field(None, description="Additional task metadata")
    resource_baseline: Optional[dict] = Field(None, description="Baseline resource values")
    alert_threshold: Optional[float] = Field(7.5, description="Alert threshold percentage")
    pulse_checkpoint_interval: Optional[int] = Field(3, description="Cycles between pulse checkpoints")
    observer_confirmation_required: Optional[bool] = Field(False, description="Requires observer confirmation")
    requires_sync: Optional[List[str]] = Field(None, description="Systems that need to sync")

    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "name": "Implement user authentication",
                "phase": "development",
                "priority": "HIGH",
                "description": "Add JWT-based user authentication",
                "estimated_hours": 8.0
            }
        }

class TaskUpdate(BaseModel):
    """Schema for updating a task."""
    status: Optional[TaskStatus] = None
    progress: Optional[float] = Field(None, ge=0, le=100)
    description: Optional[str] = None
    priority: Optional[TaskPriority] = None
    error_log: Optional[str] = None
    resource_current: Optional[dict] = None
    observer_confirmed: Optional[bool] = None
    last_pulse_check: Optional[datetime] = None

    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "status": "IN_PROGRESS",
                "progress": 50.0,
                "error_log": "Rate limit exceeded"
            }
        }

class TaskResponse(BaseModel):
    """Schema for task response."""
    id: int
    name: str
    phase: str
    description: Optional[str]
    priority: TaskPriority
    status: TaskStatus
    progress: float
    estimated_hours: Optional[float]
    error_log: Optional[str]
    task_metadata: Optional[dict]
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    resource_baseline: Optional[dict]
    resource_current: Optional[dict]
    alert_threshold: float
    pulse_checkpoint_interval: int
    last_pulse_check: Optional[datetime]
    observer_confirmation_required: bool
    observer_confirmed: bool
    requires_sync: List[str]

    class Config:
        """Pydantic model configuration."""
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Implement user authentication",
                "phase": "development",
                "status": "IN_PROGRESS",
                "progress": 50.0
            }
        } 