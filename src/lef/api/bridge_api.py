"""
FastAPI Interface for LEF Bridge Layer
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, List, Optional
import asyncio
from ..bridge_layer import RecursiveBridge, ValidationTier, BridgeStatus
from ..ai_bridge import AIBridge, Message
import logging
from ..models.message import MessageType, MessagePriority
from ..models.bridge_status import BridgeState, ServiceConnection
from ..models.system_state import SystemState
from ..services.alert_service import AlertService, AlertSeverity

logger = logging.getLogger(__name__)
router = APIRouter()
bridge = RecursiveBridge()
ai_bridge = AIBridge()
alert_service = AlertService()

# Initialize AI bridge
@router.on_event("startup")
async def startup_event():
    """Initialize AI bridge on startup"""
    await ai_bridge.initialize()

class BridgeRequest(BaseModel):
    task: str
    module: str
    origin: str
    received_from: str
    details: Dict
    requests: List[str]
    pulse_alignment: float
    observer_path_status: str

class AnalysisRequest(BaseModel):
    """Request model for analysis"""
    service_id: str
    data: Dict
    priority: Optional[MessagePriority] = MessagePriority.MEDIUM

class StateSyncRequest(BaseModel):
    """Request model for state synchronization"""
    state: SystemState
    force: bool = False

@router.get("/")
async def root():
    """Root endpoint returning bridge status"""
    return {
        "name": "LEF Bridge API",
        "status": "online",
        "bridge_status": bridge.get_status(),
        "health_status": ai_bridge.get_health_status()
    }

@router.get("/status")
async def get_bridge_status():
    """Get current bridge status"""
    try:
        state = BridgeState(
            bridge_id=bridge.bridge_id,
            status=bridge.status,
            services=bridge.connections
        )
        return state
    except Exception as e:
        logger.error(f"Failed to get bridge status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def get_bridge_health():
    """Get bridge health status"""
    try:
        return {
            "status": bridge.status,
            "active_connections": len(bridge.connections),
            "message_queue_size": bridge.message_queue.qsize(),
            "last_error": bridge.error if hasattr(bridge, 'error') else None
        }
    except Exception as e:
        logger.error(f"Failed to get bridge health: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health/{service}")
async def get_service_health(service: str):
    """Get health status for a specific service"""
    health_status = ai_bridge.get_health_status()
    if service not in health_status["services"]:
        raise HTTPException(status_code=404, detail=f"Service {service} not found")
    return health_status["services"][service]

@router.get("/metrics")
async def get_bridge_metrics():
    """Get bridge metrics"""
    try:
        return {
            "messages_processed": bridge.metrics.get("messages_processed", 0),
            "errors": bridge.metrics.get("errors", 0),
            "latency": bridge.metrics.get("latency", 0.0),
            "active_connections": len(bridge.connections)
        }
    except Exception as e:
        logger.error(f"Failed to get bridge metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sync")
async def sync_state(request: StateSyncRequest, background_tasks: BackgroundTasks):
    """Synchronize system state"""
    try:
        background_tasks.add_task(bridge.broadcast_state, request.state)
        return {"status": "success", "message": "State sync initiated"}
    except Exception as e:
        logger.error(f"Failed to sync state: {e}")
        await alert_service.create_alert(
            title="State Sync Failed",
            message=f"Failed to sync state: {e}",
            severity=AlertSeverity.ERROR
        )
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/recover")
async def recover_from_error(background_tasks: BackgroundTasks):
    """Trigger error recovery"""
    try:
        # Start recovery in background
        background_tasks.add_task(bridge.recover_from_error)
        return {"status": "recovery_started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze")
async def request_analysis(request: AnalysisRequest):
    """Request data analysis from a service"""
    try:
        result = await bridge.request_analysis(request.service_id, request.data)
        if result is None:
            raise HTTPException(status_code=404, detail="Service not found or analysis failed")
        return result
    except Exception as e:
        logger.error(f"Failed to request analysis: {e}")
        await alert_service.create_alert(
            title="Analysis Request Failed",
            message=f"Failed to request analysis: {e}",
            severity=AlertSeverity.ERROR
        )
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/validate")
async def validate_signal(request: BridgeRequest, tier: ValidationTier):
    """Validate a signal with specified tier"""
    try:
        result = await bridge.validate_signal(request.dict(), tier)
        return {
            "status": "success" if result else "error",
            "valid": result,
            "tier": tier.value
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/state")
async def update_state(request: StateSyncRequest):
    """Update bridge state"""
    try:
        # Validate state update
        if not await bridge.validate_signal(request.dict(), ValidationTier.IMMEDIATE):
            raise HTTPException(status_code=400, detail="Invalid state update")
        
        # Update state
        await bridge.sync_state()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/errors")
async def get_errors():
    """Get error history"""
    return {
        "errors": bridge.error_history,
        "count": len(bridge.error_history)
    }

@router.get("/services")
async def list_services():
    """List all connected services"""
    try:
        return {
            service_id: {
                "status": connection.status,
                "connected_at": connection.connected_at,
                "last_heartbeat": connection.last_heartbeat,
                "metrics": connection.metrics
            }
            for service_id, connection in bridge.connections.items()
        }
    except Exception as e:
        logger.error(f"Failed to list services: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/services/{service_id}")
async def get_service_status(service_id: str):
    """Get status of a specific service"""
    try:
        if service_id not in bridge.connections:
            raise HTTPException(status_code=404, detail="Service not found")
        return bridge.connections[service_id]
    except Exception as e:
        logger.error(f"Failed to get service status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/services/{service_id}/reconnect")
async def reconnect_service(service_id: str, background_tasks: BackgroundTasks):
    """Reconnect to a service"""
    try:
        if service_id not in bridge.connections:
            raise HTTPException(status_code=404, detail="Service not found")
            
        background_tasks.add_task(bridge._reconnect_service, service_id)
        return {"status": "success", "message": "Reconnection initiated"}
    except Exception as e:
        logger.error(f"Failed to reconnect service: {e}")
        await alert_service.create_alert(
            title="Service Reconnection Failed",
            message=f"Failed to reconnect to service {service_id}: {e}",
            severity=AlertSeverity.ERROR
        )
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/rate-limits")
async def get_rate_limits():
    """Get rate limit status for all services"""
    try:
        return await bridge.rate_limiter.get_all_rate_limits()
    except Exception as e:
        logger.error(f"Failed to get rate limits: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/rate-limits/{service_id}")
async def get_service_rate_limit(service_id: str):
    """Get rate limit status for a specific service"""
    try:
        return await bridge.rate_limiter.get_rate_limit_status(service_id)
    except Exception as e:
        logger.error(f"Failed to get rate limit for service {service_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/rate-limits/{service_id}/reset")
async def reset_rate_limit(service_id: str):
    """Reset rate limit for a service"""
    try:
        await bridge.rate_limiter.reset_rate_limit(service_id)
        return {"status": "success", "message": "Rate limit reset"}
    except Exception as e:
        logger.error(f"Failed to reset rate limit: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 