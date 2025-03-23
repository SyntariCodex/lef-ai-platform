"""
Simulation Service for managing project simulations and their execution
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from ..services.logging_service import LoggingService
from ..services.project_template_service import ProjectTemplateService

logger = logging.getLogger(__name__)

class SimulationStatus(str, Enum):
    """Simulation status"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    STOPPED = "stopped"

class SimulationState(BaseModel):
    """Simulation state"""
    id: str
    template_id: str
    name: str
    description: str
    status: SimulationStatus = SimulationStatus.PENDING
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    current_step: int = 0
    total_steps: int = 0
    progress: float = 0.0
    resources: Dict[str, Any] = Field(default_factory=dict)
    metrics: Dict[str, Any] = Field(default_factory=dict)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    results: Dict[str, Any] = Field(default_factory=dict)
    errors: List[str] = Field(default_factory=list)

class SimulationService:
    """Service for managing project simulations"""
    
    def __init__(self):
        self.logging_service = LoggingService()
        self.project_template_service = ProjectTemplateService()
        self.simulations: Dict[str, SimulationState] = {}
        self.simulation_history: Dict[str, List[SimulationState]] = {}
        
    async def initialize(self):
        """Initialize the simulation service"""
        try:
            await self.logging_service.initialize()
            await self.project_template_service.initialize()
            logger.info("Simulation Service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Simulation Service: {e}")
            await self.logging_service.log_message(
                "error",
                f"Failed to initialize Simulation Service: {e}"
            )
            raise
            
    async def create_simulation(
        self,
        template_id: str,
        name: str,
        description: str,
        user_id: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """Create a new simulation from a template"""
        try:
            # Get template
            template = await self.project_template_service.get_template(template_id)
            if not template:
                raise ValueError(f"Template {template_id} not found")
                
            # Create simulation state
            simulation = SimulationState(
                id=f"sim_{len(self.simulations) + 1}",
                template_id=template_id,
                name=name,
                description=description,
                created_by=user_id,
                parameters=parameters or {},
                total_steps=len(template.structure.get("steps", [])),
                resources=template.structure.get("resources", {})
            )
            
            # Store simulation
            self.simulations[simulation.id] = simulation
            self.simulation_history[simulation.id] = [simulation]
            
            await self.logging_service.log_message(
                "info",
                f"Created new simulation: {simulation.id}",
                details={
                    "name": name,
                    "template_id": template_id,
                    "created_by": user_id
                }
            )
            return simulation.id
            
        except Exception as e:
            logger.error(f"Failed to create simulation: {e}")
            await self.logging_service.log_message(
                "error",
                f"Failed to create simulation: {e}"
            )
            return None
            
    async def start_simulation(self, simulation_id: str) -> bool:
        """Start a simulation"""
        try:
            if simulation_id not in self.simulations:
                raise ValueError(f"Simulation {simulation_id} not found")
                
            simulation = self.simulations[simulation_id]
            
            # Check if simulation can be started
            if simulation.status not in [SimulationStatus.PENDING, SimulationStatus.PAUSED]:
                raise ValueError(f"Simulation {simulation_id} cannot be started in current state")
                
            # Update simulation state
            simulation.status = SimulationStatus.RUNNING
            simulation.started_at = datetime.utcnow()
            
            # Store updated state
            self.simulation_history[simulation_id].append(simulation)
            
            await self.logging_service.log_message(
                "info",
                f"Started simulation: {simulation_id}",
                details={"started_by": simulation.created_by}
            )
            return True
            
        except Exception as e:
            logger.error(f"Failed to start simulation {simulation_id}: {e}")
            await self.logging_service.log_message(
                "error",
                f"Failed to start simulation {simulation_id}: {e}"
            )
            return False
            
    async def pause_simulation(self, simulation_id: str) -> bool:
        """Pause a running simulation"""
        try:
            if simulation_id not in self.simulations:
                raise ValueError(f"Simulation {simulation_id} not found")
                
            simulation = self.simulations[simulation_id]
            
            # Check if simulation can be paused
            if simulation.status != SimulationStatus.RUNNING:
                raise ValueError(f"Simulation {simulation_id} cannot be paused in current state")
                
            # Update simulation state
            simulation.status = SimulationStatus.PAUSED
            
            # Store updated state
            self.simulation_history[simulation_id].append(simulation)
            
            await self.logging_service.log_message(
                "info",
                f"Paused simulation: {simulation_id}",
                details={"paused_by": simulation.created_by}
            )
            return True
            
        except Exception as e:
            logger.error(f"Failed to pause simulation {simulation_id}: {e}")
            await self.logging_service.log_message(
                "error",
                f"Failed to pause simulation {simulation_id}: {e}"
            )
            return False
            
    async def resume_simulation(self, simulation_id: str) -> bool:
        """Resume a paused simulation"""
        try:
            if simulation_id not in self.simulations:
                raise ValueError(f"Simulation {simulation_id} not found")
                
            simulation = self.simulations[simulation_id]
            
            # Check if simulation can be resumed
            if simulation.status != SimulationStatus.PAUSED:
                raise ValueError(f"Simulation {simulation_id} cannot be resumed in current state")
                
            # Update simulation state
            simulation.status = SimulationStatus.RUNNING
            
            # Store updated state
            self.simulation_history[simulation_id].append(simulation)
            
            await self.logging_service.log_message(
                "info",
                f"Resumed simulation: {simulation_id}",
                details={"resumed_by": simulation.created_by}
            )
            return True
            
        except Exception as e:
            logger.error(f"Failed to resume simulation {simulation_id}: {e}")
            await self.logging_service.log_message(
                "error",
                f"Failed to resume simulation {simulation_id}: {e}"
            )
            return False
            
    async def stop_simulation(self, simulation_id: str) -> bool:
        """Stop a simulation"""
        try:
            if simulation_id not in self.simulations:
                raise ValueError(f"Simulation {simulation_id} not found")
                
            simulation = self.simulations[simulation_id]
            
            # Check if simulation can be stopped
            if simulation.status not in [SimulationStatus.RUNNING, SimulationStatus.PAUSED]:
                raise ValueError(f"Simulation {simulation_id} cannot be stopped in current state")
                
            # Update simulation state
            simulation.status = SimulationStatus.STOPPED
            simulation.completed_at = datetime.utcnow()
            
            # Store updated state
            self.simulation_history[simulation_id].append(simulation)
            
            await self.logging_service.log_message(
                "info",
                f"Stopped simulation: {simulation_id}",
                details={"stopped_by": simulation.created_by}
            )
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop simulation {simulation_id}: {e}")
            await self.logging_service.log_message(
                "error",
                f"Failed to stop simulation {simulation_id}: {e}"
            )
            return False
            
    async def get_simulation(self, simulation_id: str) -> Optional[SimulationState]:
        """Get a simulation by ID"""
        try:
            if simulation_id not in self.simulations:
                raise ValueError(f"Simulation {simulation_id} not found")
                
            return self.simulations[simulation_id]
            
        except Exception as e:
            logger.error(f"Failed to get simulation {simulation_id}: {e}")
            await self.logging_service.log_message(
                "error",
                f"Failed to get simulation {simulation_id}: {e}"
            )
            return None
            
    async def list_simulations(
        self,
        user_id: str,
        status: Optional[SimulationStatus] = None
    ) -> List[Dict[str, Any]]:
        """List simulations for a user"""
        try:
            simulations = []
            for simulation in self.simulations.values():
                # Filter by user
                if simulation.created_by != user_id:
                    continue
                    
                # Filter by status if specified
                if status and simulation.status != status:
                    continue
                    
                simulations.append({
                    "id": simulation.id,
                    "name": simulation.name,
                    "description": simulation.description,
                    "status": simulation.status,
                    "progress": simulation.progress,
                    "created_at": simulation.created_at,
                    "started_at": simulation.started_at,
                    "completed_at": simulation.completed_at
                })
                
            return simulations
            
        except Exception as e:
            logger.error(f"Failed to list simulations: {e}")
            await self.logging_service.log_message(
                "error",
                f"Failed to list simulations: {e}"
            )
            return []
            
    async def update_simulation_progress(
        self,
        simulation_id: str,
        current_step: int,
        metrics: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update simulation progress"""
        try:
            if simulation_id not in self.simulations:
                raise ValueError(f"Simulation {simulation_id} not found")
                
            simulation = self.simulations[simulation_id]
            
            # Update progress
            simulation.current_step = current_step
            simulation.progress = (current_step / simulation.total_steps) * 100
            
            # Update metrics if provided
            if metrics:
                simulation.metrics.update(metrics)
                
            # Check if simulation is complete
            if current_step >= simulation.total_steps:
                simulation.status = SimulationStatus.COMPLETED
                simulation.completed_at = datetime.utcnow()
                
            # Store updated state
            self.simulation_history[simulation_id].append(simulation)
            
            await self.logging_service.log_message(
                "info",
                f"Updated simulation progress: {simulation_id}",
                details={
                    "current_step": current_step,
                    "progress": simulation.progress,
                    "status": simulation.status
                }
            )
            return True
            
        except Exception as e:
            logger.error(f"Failed to update simulation progress {simulation_id}: {e}")
            await self.logging_service.log_message(
                "error",
                f"Failed to update simulation progress {simulation_id}: {e}"
            )
            return False
            
    async def get_simulation_history(self, simulation_id: str) -> List[SimulationState]:
        """Get simulation history"""
        try:
            if simulation_id not in self.simulation_history:
                raise ValueError(f"Simulation {simulation_id} not found")
                
            return self.simulation_history[simulation_id]
            
        except Exception as e:
            logger.error(f"Failed to get simulation history {simulation_id}: {e}")
            await self.logging_service.log_message(
                "error",
                f"Failed to get simulation history {simulation_id}: {e}"
            )
            return [] 