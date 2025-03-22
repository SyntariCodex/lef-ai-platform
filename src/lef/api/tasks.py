"""
Task Management API
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict
from datetime import datetime

from ..database import get_db
from ..models.task import Task, TaskCreate, TaskUpdate, TaskResponse

router = APIRouter()

@router.get("/", response_model=List[TaskResponse])
async def get_tasks(
    phase: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get all tasks with optional filtering."""
    query = Task.select()
    if phase:
        query = query.where(Task.phase == phase)
    if status:
        query = query.where(Task.status == status)
    result = await db.execute(query)
    return [TaskResponse.from_orm(task) for task in result.scalars()]

@router.post("/", response_model=TaskResponse)
async def create_task(
    task: TaskCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new task."""
    db_task = Task(**task.dict())
    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)
    return TaskResponse.from_orm(db_task)

@router.get("/blocked", response_model=List[TaskResponse])
async def get_blocked_tasks(db: AsyncSession = Depends(get_db)):
    """Get all blocked tasks."""
    query = Task.select().where(Task.status == "blocked")
    result = await db.execute(query)
    return [TaskResponse.from_orm(task) for task in result.scalars()]

@router.get("/phase/{phase}", response_model=dict)
async def get_phase_progress(phase: str, db: AsyncSession = Depends(get_db)):
    """Get progress for a specific phase."""
    query = Task.select().where(Task.phase == phase)
    result = await db.execute(query)
    tasks = list(result.scalars())
    
    total_tasks = len(tasks)
    completed_tasks = sum(1 for task in tasks if task.status == "completed")
    total_progress = sum(task.progress for task in tasks)
    
    return {
        "phase": phase,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "total_progress": total_progress / total_tasks if total_tasks > 0 else 0
    }

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific task by ID."""
    result = await db.execute(Task.select().where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskResponse.from_orm(task)

@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a task's status and progress."""
    result = await db.execute(Task.select().where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    for field, value in task_update.dict(exclude_unset=True).items():
        setattr(task, field, value)
    
    await db.commit()
    await db.refresh(task)
    return TaskResponse.from_orm(task)

@router.put("/{task_id}/resources", response_model=TaskResponse)
async def update_task_resources(
    task_id: int,
    resources: Dict[str, float],
    db: AsyncSession = Depends(get_db)
):
    """Update a task's current resource values."""
    result = await db.execute(Task.select().where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task.resource_current = resources
    
    # Check if resources exceed alert threshold
    for resource, value in resources.items():
        if resource in task.resource_baseline:
            baseline = task.resource_baseline[resource]
            deviation = abs((value - baseline) / baseline * 100)
            if deviation > task.alert_threshold:
                task.status = "blocked"
                task.error_log = f"Resource {resource} exceeds alert threshold: {deviation:.1f}%"
    
    await db.commit()
    await db.refresh(task)
    return TaskResponse.from_orm(task)

@router.post("/{task_id}/pulse-check", response_model=TaskResponse)
async def record_pulse_check(
    task_id: int,
    observer_confirmed: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """Record a pulse cycle checkpoint for a task."""
    result = await db.execute(Task.select().where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task.last_pulse_check = datetime.utcnow()
    
    if task.observer_confirmation_required:
        task.observer_confirmed = observer_confirmed
        if not observer_confirmed:
            task.status = "blocked"
            task.error_log = "Waiting for observer confirmation"
    
    await db.commit()
    await db.refresh(task)
    return TaskResponse.from_orm(task)

@router.get("/{task_id}/dependencies", response_model=List[TaskResponse])
async def get_task_dependencies(
    task_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get all dependencies for a task."""
    result = await db.execute(Task.select().where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return [TaskResponse.from_orm(dep) for dep in task.dependencies]

@router.get("/phase/{phase}/resources", response_model=Dict[str, Dict[str, float]])
async def get_phase_resources(
    phase: str,
    db: AsyncSession = Depends(get_db)
):
    """Get resource usage summary for a phase."""
    query = Task.select().where(Task.phase == phase)
    result = await db.execute(query)
    tasks = list(result.scalars())
    
    resources = {}
    for task in tasks:
        if task.resource_current:
            for resource, value in task.resource_current.items():
                if resource not in resources:
                    resources[resource] = {
                        "total": 0.0,
                        "baseline": 0.0,
                        "deviation": 0.0
                    }
                resources[resource]["total"] += value
                if resource in task.resource_baseline:
                    resources[resource]["baseline"] += task.resource_baseline[resource]
    
    # Calculate deviations
    for resource in resources:
        baseline = resources[resource]["baseline"]
        if baseline > 0:
            resources[resource]["deviation"] = (
                (resources[resource]["total"] - baseline) / baseline * 100
            )
    
    return resources 