from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, Integer, JSON, select, Enum
from sqlalchemy.orm import Mapped, mapped_column
from enum import Enum as PyEnum
from .database import Base

class EventType(PyEnum):
    PROCESS_START = "process_start"
    PROCESS_STOP = "process_stop"
    SYSTEM_ERROR = "system_error"
    COMPONENT_STATE_CHANGE = "component_state_change"
    SUPERVISOR_ACTION = "supervisor_action"

class SystemEvent(Base):
    __tablename__ = "system_events"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow
    )
    event_type: Mapped[EventType] = mapped_column(Enum(EventType))
    component_name: Mapped[str] = mapped_column(String(100))
    process_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    message: Mapped[str] = mapped_column(String(500))
    event_metadata: Mapped[dict] = mapped_column(JSON, default={})
    
    def __repr__(self) -> str:
        return f"<SystemEvent({self.event_type}, component={self.component_name}, pid={self.process_id})>"

async def log_event(
    session,
    event_type: EventType,
    component_name: str,
    message: str,
    process_id: Optional[int] = None,
    metadata: Optional[dict] = None
) -> SystemEvent:
    """Log a system event."""
    event = SystemEvent(
        event_type=event_type,
        component_name=component_name,
        process_id=process_id,
        message=message,
        event_metadata=metadata or {}
    )
    session.add(event)
    return event

async def get_recent_events(
    session,
    limit: int = 50,
    event_type: Optional[EventType] = None,
    component_name: Optional[str] = None
) -> list[SystemEvent]:
    """Get recent system events with optional filtering."""
    query = select(SystemEvent).order_by(SystemEvent.timestamp.desc())
    
    if event_type:
        query = query.filter(SystemEvent.event_type == event_type)
    if component_name:
        query = query.filter(SystemEvent.component_name == component_name)
    
    query = query.limit(limit)
    result = await session.execute(query)
    return result.scalars().all()

async def get_component_history(
    session,
    component_name: str,
    limit: int = 20
) -> list[SystemEvent]:
    """Get recent history for a specific component."""
    return await get_recent_events(
        session,
        limit=limit,
        component_name=component_name
    ) 