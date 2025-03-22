"""
Task model for the LEF system.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey, Table, Boolean
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field

from .base import Base

# Task dependencies association table
task_dependencies = Table(
    "task_dependencies",
    Base.metadata,
    Column("task_id", Integer, ForeignKey("tasks.id"), primary_key=True),
    Column("dependency_id", Integer, ForeignKey("tasks.id"), primary_key=True)
)

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

class Task(Base):
    """Task model."""
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phase = Column(String, nullable=False)
    description = Column(String)
    priority = Column(String, nullable=False)
    status = Column(String, default=TaskStatus.PENDING)
    progress = Column(Float, default=0.0)
    estimated_hours = Column(Float)
    error_log = Column(String)
    task_metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Resource tracking
    resource_baseline = Column(JSON, default=dict)
    resource_current = Column(JSON, default=dict)
    alert_threshold = Column(Float, default=7.5)
    
    # Pulse cycle monitoring
    pulse_checkpoint_interval = Column(Integer, default=3)
    last_pulse_check = Column(DateTime)
    observer_confirmation_required = Column(Boolean, default=False)
    observer_confirmed = Column(Boolean, default=False)
    
    # System sync requirements
    requires_sync = Column(JSON, default=list)

    # Relationships
    dependencies = relationship(
        "Task",
        secondary=task_dependencies,
        primaryjoin="Task.id==task_dependencies.c.task_id",
        secondaryjoin="Task.id==task_dependencies.c.dependency_id",
        backref="dependent_tasks"
    )

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
        from_attributes = True 