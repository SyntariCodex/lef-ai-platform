"""
System API endpoints.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, List, Optional

from ..database import get_system_state
from ..models.system_state import SystemState, SystemStatus, ComponentStatus

router = APIRouter(
    prefix="/api/system",
    tags=["system"]
)

@router.get("/status")
async def get_status() -> Dict:
    """Get system status."""
    try:
        state = get_system_state()
        return {
            "status": state.status,
            "version": state.version,
            "uptime": state.uptime,
            "last_updated": state.last_updated,
            "components": state.components,
            "errors": state.errors,
            "warnings": state.warnings
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics")
async def get_metrics() -> Dict:
    """Get system metrics."""
    try:
        state = get_system_state()
        return {
            "metrics": state.metrics,
            "resource_usage": state.resource_usage,
            "performance_metrics": state.performance_metrics,
            "security_status": state.security_status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def get_health() -> Dict:
    """Get system health status."""
    try:
        state = get_system_state()
        return {
            "status": state.status,
            "components": state.components,
            "errors": state.errors,
            "warnings": state.warnings,
            "metrics": {
                "cpu_usage": state.metrics.get("cpu_usage", 0.0),
                "memory_usage": state.metrics.get("memory_usage", 0.0),
                "disk_usage": state.metrics.get("disk_usage", 0.0)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/components")
async def get_components() -> Dict[str, ComponentStatus]:
    """Get component statuses."""
    try:
        state = get_system_state()
        return state.components
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/errors")
async def get_errors() -> List[str]:
    """Get system errors."""
    try:
        state = get_system_state()
        return state.errors
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/warnings")
async def get_warnings() -> List[str]:
    """Get system warnings."""
    try:
        state = get_system_state()
        return state.warnings
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 