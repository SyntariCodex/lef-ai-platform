"""
Tasks model for the LEF system.
"""

from datetime import datetime
from typing import List, Optional, Dict
from pydantic import BaseModel

from .task import TaskStatus, TaskPriority, TaskResponse

class TaskList(BaseModel):
    """Schema for list of tasks."""
    tasks: List[TaskResponse]
    total: int
    page: int
    per_page: int
    
    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "tasks": [
                    {
                        "id": 1,
                        "name": "Implement user authentication",
                        "phase": "development",
                        "status": "IN_PROGRESS",
                        "progress": 50.0
                    }
                ],
                "total": 1,
                "page": 1,
                "per_page": 10
            }
        } 