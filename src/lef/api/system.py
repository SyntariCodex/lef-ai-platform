"""
System API endpoints for the LEF system.
"""

import psutil
from datetime import datetime
from fastapi import APIRouter, HTTPException
from typing import List, Optional

from ..models.system_state import SystemState
from ..models.events import Event, EventType, EventSeverity

router = APIRouter(prefix="/api/system", tags=["system"])

@router.get("/status", response_model=SystemState)
async def get_system_status():
    """Get current system status."""
    try:
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return SystemState(
            status="running",
            version="1.0.0",
            uptime=process.create_time(),
            memory_usage=memory_info.rss / 1024 / 1024,  # Convert to MB
            cpu_usage=process.cpu_percent(),
            active_tasks=0,  # TODO: Implement task counting
            completed_tasks=0,
            failed_tasks=0,
            system_metrics={
                "threads": process.num_threads(),
                "open_files": len(process.open_files()),
                "connections": len(process.connections())
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/events", response_model=List[Event])
async def get_system_events(
    event_type: Optional[EventType] = None,
    severity: Optional[EventSeverity] = None,
    limit: int = 50
):
    """Get system events with optional filtering."""
    # TODO: Implement event storage and retrieval
    return []

@router.post("/events", response_model=Event)
async def create_system_event(event: Event):
    """Create a new system event."""
    # TODO: Implement event storage
    event.created_at = datetime.utcnow()
    return event 