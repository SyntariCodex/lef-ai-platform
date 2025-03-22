"""
System API endpoints for LEF system state and monitoring
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from ..models import (
    get_db,
    SystemState,
    SystemEvent,
    EventType,
    log_event,
    update_component_state
)
from sqlalchemy import select, desc

router = APIRouter(prefix="/system", tags=["system"])

# Pydantic models for API
class ComponentStateUpdate(BaseModel):
    status: str
    process_id: Optional[int] = None
    metadata: Optional[dict] = None

class ComponentStateResponse(BaseModel):
    component_name: str
    status: str
    process_id: Optional[int]
    metadata: dict
    last_heartbeat: datetime
    
    class Config:
        from_attributes = True

class SystemEventResponse(BaseModel):
    timestamp: datetime
    event_type: str
    component_name: str
    process_id: Optional[int]
    message: str
    metadata: dict
    
    class Config:
        from_attributes = True

@router.get("/components", response_model=List[ComponentStateResponse])
async def get_all_components(session: AsyncSession = Depends(get_db)):
    """Get status of all system components"""
    result = await session.execute(select(SystemState))
    return result.scalars().all()

@router.get("/components/{component_name}", response_model=ComponentStateResponse)
async def get_component_state(component_name: str, session: AsyncSession = Depends(get_db)):
    """Get status of a specific component"""
    result = await session.execute(
        select(SystemState).filter(SystemState.component_name == component_name)
    )
    component = result.scalar_one_or_none()
    if not component:
        raise HTTPException(status_code=404, detail="Component not found")
    return component

@router.put("/components/{component_name}", response_model=ComponentStateResponse)
async def update_component(
    component_name: str,
    state: ComponentStateUpdate,
    session: AsyncSession = Depends(get_db)
):
    """Update a component's state"""
    component = await update_component_state(
        session,
        component_name,
        state.status,
        state.process_id,
        state.metadata
    )
    
    # Log the state change
    await log_event(
        session,
        EventType.COMPONENT_STATE_CHANGE,
        component_name,
        f"Component state updated to {state.status}",
        state.process_id,
        state.metadata
    )
    
    await session.commit()
    return component

@router.get("/events", response_model=List[SystemEventResponse])
async def get_system_events(
    limit: int = 50,
    component_name: Optional[str] = None,
    event_type: Optional[str] = None,
    session: AsyncSession = Depends(get_db)
):
    """Get system events with optional filtering"""
    query = select(SystemEvent).order_by(desc(SystemEvent.timestamp))
    
    if component_name:
        query = query.filter(SystemEvent.component_name == component_name)
    if event_type:
        query = query.filter(SystemEvent.event_type == event_type)
    
    query = query.limit(limit)
    result = await session.execute(query)
    return result.scalars().all()

@router.post("/events", response_model=SystemEventResponse)
async def create_system_event(
    event_type: EventType,
    component_name: str,
    message: str,
    process_id: Optional[int] = None,
    metadata: Optional[dict] = None,
    session: AsyncSession = Depends(get_db)
):
    """Create a new system event"""
    event = await log_event(
        session,
        event_type,
        component_name,
        message,
        process_id,
        metadata
    )
    await session.commit()
    return event 