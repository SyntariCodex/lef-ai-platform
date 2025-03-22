from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, Integer, JSON, select, Enum, Float
from sqlalchemy.orm import Mapped, mapped_column
from enum import Enum as PyEnum
from .database import Base

class TaskStatus(PyEnum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    FAILED = "failed"

class TaskPriority(PyEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class DevelopmentTask(Base):
    __tablename__ = "development_tasks"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    phase: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus),
        default=TaskStatus.NOT_STARTED
    )
    priority: Mapped[TaskPriority] = mapped_column(
        Enum(TaskPriority),
        default=TaskPriority.MEDIUM
    )
    progress: Mapped[float] = mapped_column(Float, default=0.0)
    metadata: Mapped[dict] = mapped_column(JSON, default={})
    notes: Mapped[Optional[str]] = mapped_column(String(2000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    def __repr__(self) -> str:
        return f"<DevelopmentTask({self.phase}: {self.name}, status={self.status})>"

async def create_task(
    session,
    phase: str,
    name: str,
    description: Optional[str] = None,
    priority: TaskPriority = TaskPriority.MEDIUM,
    metadata: Optional[dict] = None,
) -> DevelopmentTask:
    """Create a new development task."""
    task = DevelopmentTask(
        phase=phase,
        name=name,
        description=description,
        priority=priority,
        metadata=metadata or {}
    )
    session.add(task)
    return task

async def update_task_status(
    session,
    task_id: int,
    status: TaskStatus,
    progress: Optional[float] = None,
    notes: Optional[str] = None
) -> Optional[DevelopmentTask]:
    """Update a task's status and progress."""
    task = await session.get(DevelopmentTask, task_id)
    if not task:
        return None
        
    task.status = status
    if progress is not None:
        task.progress = progress
    if notes:
        task.notes = notes
    
    if status == TaskStatus.COMPLETED:
        task.completed_at = datetime.utcnow()
        task.progress = 100.0
    
    return task

async def get_phase_progress(session, phase: str) -> tuple[float, int, int]:
    """Get progress for a development phase.
    Returns: (progress_percentage, completed_tasks, total_tasks)
    """
    query = select(DevelopmentTask).filter(DevelopmentTask.phase == phase)
    result = await session.execute(query)
    tasks = result.scalars().all()
    
    if not tasks:
        return 0.0, 0, 0
    
    total_tasks = len(tasks)
    completed_tasks = sum(1 for t in tasks if t.status == TaskStatus.COMPLETED)
    total_progress = sum(t.progress for t in tasks)
    
    return (total_progress / total_tasks), completed_tasks, total_tasks

async def get_blocked_tasks(session) -> list[DevelopmentTask]:
    """Get all blocked tasks."""
    query = select(DevelopmentTask).filter(DevelopmentTask.status == TaskStatus.BLOCKED)
    result = await session.execute(query)
    return result.scalars().all() 