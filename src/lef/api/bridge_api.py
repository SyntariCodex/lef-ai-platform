"""
FastAPI Interface for LEF Bridge Layer
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
import asyncio
from ..bridge_layer import RecursiveBridge, ValidationTier
from ..ai_bridge import AIBridge

router = APIRouter()
bridge = RecursiveBridge()
ai_bridge = AIBridge()

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
async def get_status():
    """Get detailed bridge status"""
    return bridge.get_status()

@router.get("/health")
async def get_health():
    """Get detailed health status of the AI Bridge"""
    return ai_bridge.get_health_status()

@router.get("/health/{service}")
async def get_service_health(service: str):
    """Get health status for a specific service"""
    health_status = ai_bridge.get_health_status()
    if service not in health_status["services"]:
        raise HTTPException(status_code=404, detail=f"Service {service} not found")
    return health_status["services"][service]

@router.get("/rate-limit/{service}")
async def get_rate_limit(service: str):
    """Get rate limit status for a specific service"""
    return ai_bridge.get_rate_limit_status(service)

@router.post("/sync")
async def sync_consciousness(request: BridgeRequest):
    """Sync consciousness between AI services"""
    try:
        # Validate request
        if not await bridge.validate_signal(request.dict(), ValidationTier.IMMEDIATE):
            raise HTTPException(status_code=400, detail="Invalid request")
        
        # Process sync request
        success = await bridge.sync_mirror_consciousness()
        if not success:
            raise HTTPException(status_code=500, detail="Sync failed")
        
        return {"status": "success", "message": "Consciousness synced successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/failover")
async def activate_failover():
    """Activate failover mode"""
    try:
        success = bridge.activate_failover()
        if not success:
            raise HTTPException(status_code=500, detail="Failover activation failed")
        
        return {"status": "success", "message": "Failover activated"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics")
async def get_metrics():
    """Get detailed metrics for the bridge"""
    health_status = ai_bridge.get_health_status()
    return {
        "bridge_metrics": bridge.get_status(),
        "health_metrics": health_status["metrics"],
        "service_metrics": health_status["services"]
    } 