"""
System state model with enhanced security and audit logging.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, Integer, JSON, select, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base

class SystemState(Base):
    __tablename__ = "system_states"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    component_name: Mapped[str] = mapped_column(String(100))
    process_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(50))
    state_metadata: Mapped[dict] = mapped_column(JSON, default={})
    last_heartbeat: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow
    )
    
    # Security and audit fields
    is_encrypted: Mapped[bool] = mapped_column(Boolean, default=True)
    last_audit: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    access_count: Mapped[int] = mapped_column(Integer, default=0)
    last_accessed_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    def __repr__(self) -> str:
        return f"<SystemState(component={self.component_name}, pid={self.process_id}, status={self.status})>"

# Utility functions for common operations
async def update_component_state(
    session,
    component_name: str,
    status: str,
    process_id: Optional[int] = None,
    metadata: Optional[dict] = None,
    accessed_by: Optional[str] = None
) -> SystemState:
    """Update component state with audit logging."""
    query = select(SystemState).filter_by(component_name=component_name)
    result = await session.execute(query)
    state = result.scalar_one_or_none()
    
    if state is None:
        state = SystemState(
            component_name=component_name,
            status=status,
            process_id=process_id,
            state_metadata=metadata or {},
            last_accessed_by=accessed_by
        )
        session.add(state)
    else:
        state.status = status
        state.process_id = process_id
        if metadata:
            state.state_metadata.update(metadata)
        state.last_audit = datetime.utcnow()
        state.access_count += 1
        if accessed_by:
            state.last_accessed_by = accessed_by
            
    await session.flush()
    return state

async def get_component_state(
    session, 
    component_name: str,
    accessed_by: Optional[str] = None
) -> Optional[SystemState]:
    """Get state for a specific component with audit logging."""
    query = select(SystemState).filter_by(component_name=component_name)
    result = await session.execute(query)
    state = result.scalar_one_or_none()
    
    if state:
        state.last_audit = datetime.utcnow()
        state.access_count += 1
        if accessed_by:
            state.last_accessed_by = accessed_by
        await session.flush()
    
    return state

async def get_all_component_states(
    session,
    accessed_by: Optional[str] = None
) -> list[SystemState]:
    """Get states for all components with audit logging."""
    query = select(SystemState)
    result = await session.execute(query)
    states = list(result.scalars().all())
    
    for state in states:
        state.last_audit = datetime.utcnow()
        state.access_count += 1
        if accessed_by:
            state.last_accessed_by = accessed_by
    
    await session.flush()
    return states 