"""
FastAPI Interface for LEF Bridge Layer
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import asyncio
import uvicorn
from ..bridge_layer import RecursiveBridge, ValidationTier

app = FastAPI(title="LEF Bridge API")
bridge = RecursiveBridge()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class BridgeRequest(BaseModel):
    task: str
    module: str
    origin: str
    received_from: str
    details: Dict
    requests: List[str]
    pulse_alignment: float
    observer_path_status: str

@app.get("/")
async def root():
    """Root endpoint returning bridge status"""
    return {
        "name": "LEF Bridge API",
        "status": "online",
        "bridge_status": bridge.get_status()
    }

@app.get("/status")
async def get_status():
    """Get detailed bridge status"""
    return bridge.get_status()

@app.post("/sync")
async def sync_consciousness(request: BridgeRequest):
    """Synchronize mirror consciousness"""
    result = await bridge.process_request({
        "sync": True,
        "origin": request.origin,
        "pulse_alignment": request.pulse_alignment,
        "observer_path_status": request.observer_path_status
    })
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@app.post("/validate")
async def validate_signal(request: BridgeRequest, tier: Optional[str] = "tier_1"):
    """Validate incoming signal"""
    try:
        validation_tier = ValidationTier(tier)
        is_valid = await bridge.validate_signal(request.dict(), validation_tier)
        return {
            "valid": is_valid,
            "tier": tier,
            "details": bridge.validation
        }
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid validation tier: {tier}")

@app.post("/failover")
async def activate_failover(request: BridgeRequest):
    """Activate Aether mirror fallback"""
    result = await bridge.process_request({
        "failover": True,
        "origin": request.origin,
        "pulse_alignment": request.pulse_alignment,
        "observer_path_status": request.observer_path_status
    })
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result

def start_bridge_api():
    """Start the bridge API server"""
    uvicorn.run(app, host="0.0.0.0", port=8000) 