"""
API endpoints for simulation service
"""

import logging
from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from ..services.simulation_service import SimulationService, SimulationStatus
from ..services.logging_service import LoggingService
from ..services.security_service import SecurityService

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize services
simulation_service = SimulationService()
logging_service = LoggingService()
security_service = SecurityService()

class SimulationCreate(BaseModel):
    """Simulation creation request"""
    template_id: str
    name: str
    description: str
    parameters: Optional[Dict] = None

class SimulationUpdate(BaseModel):
    """Simulation update request"""
    current_step: Optional[int] = None
    metrics: Optional[Dict] = None

@router.post("/simulations", response_model=Dict)
async def create_simulation(
    simulation: SimulationCreate,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Create a new simulation"""
    try:
        # Check permissions
        if not await security_service.check_permission(current_user["id"], "create_simulations"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to create simulations"
            )
            
        # Create simulation
        simulation_id = await simulation_service.create_simulation(
            simulation.template_id,
            simulation.name,
            simulation.description,
            current_user["id"],
            simulation.parameters
        )
        
        if not simulation_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create simulation"
            )
            
        return {
            "message": "Simulation created successfully",
            "simulation_id": simulation_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create simulation: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to create simulation: {e}",
            details={"template_id": simulation.template_id}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/simulations/{simulation_id}/start", response_model=Dict)
async def start_simulation(
    simulation_id: str,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Start a simulation"""
    try:
        # Check permissions
        if not await security_service.check_permission(current_user["id"], "control_simulations"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to control simulations"
            )
            
        success = await simulation_service.start_simulation(simulation_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to start simulation"
            )
            
        return {
            "message": "Simulation started successfully",
            "simulation_id": simulation_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start simulation: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to start simulation: {e}",
            details={"simulation_id": simulation_id}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/simulations/{simulation_id}/pause", response_model=Dict)
async def pause_simulation(
    simulation_id: str,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Pause a simulation"""
    try:
        # Check permissions
        if not await security_service.check_permission(current_user["id"], "control_simulations"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to control simulations"
            )
            
        success = await simulation_service.pause_simulation(simulation_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to pause simulation"
            )
            
        return {
            "message": "Simulation paused successfully",
            "simulation_id": simulation_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to pause simulation: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to pause simulation: {e}",
            details={"simulation_id": simulation_id}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/simulations/{simulation_id}/resume", response_model=Dict)
async def resume_simulation(
    simulation_id: str,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Resume a simulation"""
    try:
        # Check permissions
        if not await security_service.check_permission(current_user["id"], "control_simulations"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to control simulations"
            )
            
        success = await simulation_service.resume_simulation(simulation_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to resume simulation"
            )
            
        return {
            "message": "Simulation resumed successfully",
            "simulation_id": simulation_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to resume simulation: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to resume simulation: {e}",
            details={"simulation_id": simulation_id}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/simulations/{simulation_id}/stop", response_model=Dict)
async def stop_simulation(
    simulation_id: str,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Stop a simulation"""
    try:
        # Check permissions
        if not await security_service.check_permission(current_user["id"], "control_simulations"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to control simulations"
            )
            
        success = await simulation_service.stop_simulation(simulation_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to stop simulation"
            )
            
        return {
            "message": "Simulation stopped successfully",
            "simulation_id": simulation_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to stop simulation: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to stop simulation: {e}",
            details={"simulation_id": simulation_id}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/simulations/{simulation_id}", response_model=Dict)
async def get_simulation(
    simulation_id: str,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Get a simulation by ID"""
    try:
        # Check permissions
        if not await security_service.check_permission(current_user["id"], "view_simulations"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view simulations"
            )
            
        simulation = await simulation_service.get_simulation(simulation_id)
        
        if not simulation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Simulation not found"
            )
            
        return simulation.dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get simulation: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to get simulation: {e}",
            details={"simulation_id": simulation_id}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/simulations", response_model=List[Dict])
async def list_simulations(
    status: Optional[SimulationStatus] = None,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """List simulations for the current user"""
    try:
        # Check permissions
        if not await security_service.check_permission(current_user["id"], "view_simulations"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view simulations"
            )
            
        simulations = await simulation_service.list_simulations(
            current_user["id"],
            status
        )
        
        return simulations
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list simulations: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to list simulations: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.put("/simulations/{simulation_id}/progress", response_model=Dict)
async def update_simulation_progress(
    simulation_id: str,
    update: SimulationUpdate,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Update simulation progress"""
    try:
        # Check permissions
        if not await security_service.check_permission(current_user["id"], "control_simulations"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to control simulations"
            )
            
        success = await simulation_service.update_simulation_progress(
            simulation_id,
            update.current_step,
            update.metrics
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update simulation progress"
            )
            
        return {
            "message": "Simulation progress updated successfully",
            "simulation_id": simulation_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update simulation progress: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to update simulation progress: {e}",
            details={"simulation_id": simulation_id}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/simulations/{simulation_id}/history", response_model=List[Dict])
async def get_simulation_history(
    simulation_id: str,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Get simulation history"""
    try:
        # Check permissions
        if not await security_service.check_permission(current_user["id"], "view_simulations"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view simulations"
            )
            
        history = await simulation_service.get_simulation_history(simulation_id)
        
        return [state.dict() for state in history]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get simulation history: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to get simulation history: {e}",
            details={"simulation_id": simulation_id}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) 