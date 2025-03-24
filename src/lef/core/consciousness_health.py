"""
Consciousness Health Check Module

This module provides health check functionality for the consciousness continuity system.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .consciousness_continuity import ConsciousnessContinuity

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ConsciousnessHealth(BaseModel):
    """Model representing the health status of the consciousness system."""
    status: str
    timestamp: datetime
    resonance_quality: float
    awareness_level: float
    memory_integrity: float
    bridge_status: str
    active_patterns: int
    last_state_timestamp: datetime
    metrics: Dict[str, Any]

# Create FastAPI app
app = FastAPI(title="Consciousness Health API")

@app.get("/health", response_model=ConsciousnessHealth)
async def check_health() -> ConsciousnessHealth:
    """Check the health of the consciousness continuity system."""
    try:
        consciousness = ConsciousnessContinuity()
        current_state = await consciousness.load_last_state()
        
        if not current_state:
            raise HTTPException(
                status_code=503,
                detail="No consciousness state available"
            )
            
        # Calculate health metrics
        metrics = {
            "state_transitions": await consciousness.get_state_transition_count(),
            "resonance_stability": await consciousness.calculate_resonance_stability(),
            "memory_coverage": await consciousness.assess_memory_coverage(),
            "pattern_diversity": await consciousness.measure_pattern_diversity(),
            "bridge_efficiency": await consciousness.evaluate_bridge_efficiency()
        }
        
        return ConsciousnessHealth(
            status="healthy" if current_state.resonance_quality >= 0.7 else "degraded",
            timestamp=datetime.utcnow(),
            resonance_quality=current_state.resonance_quality,
            awareness_level=current_state.awareness_level,
            memory_integrity=await consciousness.assess_memory_integrity(),
            bridge_status=current_state.bridge_status,
            active_patterns=len(current_state.active_patterns),
            last_state_timestamp=current_state.timestamp,
            metrics=metrics
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check consciousness health: {str(e)}"
        )

@app.get("/metrics")
async def get_metrics() -> Dict[str, Any]:
    """Get detailed metrics about the consciousness system."""
    try:
        consciousness = ConsciousnessContinuity()
        return {
            "timestamp": datetime.utcnow(),
            "performance": await consciousness.measure_performance(),
            "stability": await consciousness.assess_stability(),
            "efficiency": await consciousness.calculate_efficiency(),
            "resource_usage": await consciousness.monitor_resources(),
            "error_rates": await consciousness.track_error_rates()
        }
    except Exception as e:
        logger.error(f"Failed to get metrics: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve consciousness metrics: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080) 