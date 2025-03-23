"""
API endpoints for logging and tracing
"""

import logging
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel

from ..services.logging_service import LoggingService, LogEntry, TraceSpan
from ..auth.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/logs", tags=["logs"])

# Initialize logging service
logging_service = LoggingService()

class LogFilter(BaseModel):
    """Filter parameters for log queries"""
    service: Optional[str] = None
    level: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    trace_id: Optional[str] = None

@router.get("/")
async def get_logs(
    service: Optional[str] = None,
    level: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    trace_id: Optional[str] = None,
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0),
    current_user: str = Depends(get_current_user)
) -> List[LogEntry]:
    """Get logs with optional filtering"""
    try:
        return await logging_service.get_logs(
            service=service,
            level=level,
            start_time=start_time,
            end_time=end_time,
            trace_id=trace_id
        )
    except Exception as e:
        logger.error(f"Failed to get logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trace/{trace_id}")
async def get_trace(
    trace_id: str,
    current_user: str = Depends(get_current_user)
) -> List[TraceSpan]:
    """Get trace information"""
    try:
        return await logging_service.get_trace(trace_id)
    except Exception as e:
        logger.error(f"Failed to get trace: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search")
async def search_logs(
    filter: LogFilter,
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0),
    current_user: str = Depends(get_current_user)
) -> List[LogEntry]:
    """Search logs with complex filtering"""
    try:
        return await logging_service.get_logs(
            service=filter.service,
            level=filter.level,
            start_time=filter.start_time,
            end_time=filter.end_time,
            trace_id=filter.trace_id
        )
    except Exception as e:
        logger.error(f"Failed to search logs: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 