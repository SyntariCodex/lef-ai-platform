"""
Tasks API endpoints for the LEF system.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from ..models.task import TaskCreate, TaskResponse, TaskStatus
from ..models.tasks import TaskList
from ..database import create_task, get_task, get_tasks, update_task, delete_task

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

@router.post("/", response_model=TaskResponse)
async def create_new_task(task: TaskCreate):
    """Create a new task."""
    try:
        return create_task(task)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task_by_id(task_id: int):
    """Get a task by ID."""
    task = get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.get("/", response_model=TaskList)
async def list_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    phase: Optional[str] = None,
    status: Optional[TaskStatus] = None
):
    """List tasks with optional filtering."""
    try:
        tasks = get_tasks(skip=skip, limit=limit, phase=phase, status=status)
        total = len(tasks)  # TODO: Implement count query
        return TaskList(
            tasks=tasks,
            total=total,
            page=skip // limit + 1,
            per_page=limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{task_id}", response_model=TaskResponse)
async def update_task_by_id(task_id: int, task_data: dict):
    """Update a task."""
    task = update_task(task_id, task_data)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.delete("/{task_id}")
async def delete_task_by_id(task_id: int):
    """Delete a task."""
    if not delete_task(task_id):
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted successfully"} 