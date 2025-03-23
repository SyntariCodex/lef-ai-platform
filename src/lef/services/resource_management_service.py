"""
Resource Management Service for handling resource allocation, tracking, and optimization
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class ResourceType(Enum):
    """Types of resources that can be managed"""
    HUMAN = "human"
    COMPUTE = "compute"
    STORAGE = "storage"
    NETWORK = "network"
    FINANCIAL = "financial"
    EQUIPMENT = "equipment"
    LICENSE = "license"
    OTHER = "other"

class ResourceStatus(Enum):
    """Status of a resource"""
    AVAILABLE = "available"
    ALLOCATED = "allocated"
    MAINTENANCE = "maintenance"
    RESERVED = "reserved"
    UNAVAILABLE = "unavailable"

class ResourcePriority(Enum):
    """Priority levels for resource allocation"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Resource(BaseModel):
    """Resource model"""
    id: str
    name: str
    description: str
    type: ResourceType
    status: ResourceStatus
    capacity: float
    used_capacity: float
    unit: str
    cost_per_unit: float
    priority: ResourcePriority
    tags: List[str]
    metadata: Optional[Dict] = None
    created_at: datetime
    updated_at: datetime
    created_by: str
    updated_by: Optional[str] = None

class ResourceAllocation(BaseModel):
    """Resource allocation model"""
    id: str
    resource_id: str
    project_id: Optional[str]
    simulation_id: Optional[str]
    allocated_capacity: float
    start_time: datetime
    end_time: Optional[datetime]
    status: str
    priority: ResourcePriority
    allocated_by: str
    allocated_at: datetime
    released_at: Optional[datetime] = None
    metadata: Optional[Dict] = None

class ResourceConstraint(BaseModel):
    """Resource constraint model"""
    resource_id: str
    min_capacity: float
    max_capacity: float
    blackout_periods: List[Dict[str, datetime]]
    dependencies: List[str]
    metadata: Optional[Dict] = None

class ResourceManagementService:
    """Service for managing resources and their allocations"""
    
    def __init__(self):
        """Initialize the service"""
        self.resources: Dict[str, Resource] = {}
        self.allocations: Dict[str, ResourceAllocation] = {}
        self.constraints: Dict[str, ResourceConstraint] = {}
        self.logging_service = None
        self.project_service = None
        self.simulation_service = None

    async def initialize(self):
        """Initialize the service and its dependencies"""
        try:
            from .logging_service import LoggingService
            from .project_service import ProjectService
            from .simulation_service import SimulationService
            
            self.logging_service = LoggingService()
            self.project_service = ProjectService()
            self.simulation_service = SimulationService()
            
            await self.logging_service.log_message(
                "info",
                "Resource Management Service initialized"
            )
        except Exception as e:
            logger.error(f"Failed to initialize Resource Management Service: {e}")
            raise

    async def create_resource(self, resource: Resource) -> bool:
        """Create a new resource"""
        try:
            if resource.id in self.resources:
                await self.logging_service.log_message(
                    "error",
                    f"Resource {resource.id} already exists"
                )
                return False
            
            self.resources[resource.id] = resource
            await self.logging_service.log_message(
                "info",
                f"Resource {resource.id} created",
                details={"resource_name": resource.name}
            )
            return True
        except Exception as e:
            logger.error(f"Failed to create resource: {e}")
            await self.logging_service.log_message(
                "error",
                f"Failed to create resource: {e}",
                details={"resource_name": resource.name}
            )
            return False

    async def update_resource(self, resource_id: str, updates: Dict) -> bool:
        """Update an existing resource"""
        try:
            if resource_id not in self.resources:
                await self.logging_service.log_message(
                    "error",
                    f"Resource {resource_id} not found"
                )
                return False
            
            resource = self.resources[resource_id]
            for key, value in updates.items():
                setattr(resource, key, value)
            resource.updated_at = datetime.utcnow()
            
            await self.logging_service.log_message(
                "info",
                f"Resource {resource_id} updated",
                details={"updates": updates}
            )
            return True
        except Exception as e:
            logger.error(f"Failed to update resource: {e}")
            await self.logging_service.log_message(
                "error",
                f"Failed to update resource: {e}",
                details={"resource_id": resource_id}
            )
            return False

    async def get_resource(self, resource_id: str) -> Optional[Resource]:
        """Get a resource by ID"""
        try:
            return self.resources.get(resource_id)
        except Exception as e:
            logger.error(f"Failed to get resource: {e}")
            await self.logging_service.log_message(
                "error",
                f"Failed to get resource: {e}",
                details={"resource_id": resource_id}
            )
            return None

    async def list_resources(
        self,
        resource_type: Optional[ResourceType] = None,
        status: Optional[ResourceStatus] = None,
        tags: Optional[List[str]] = None
    ) -> List[Resource]:
        """List resources with optional filters"""
        try:
            resources = list(self.resources.values())
            
            if resource_type:
                resources = [r for r in resources if r.type == resource_type]
            if status:
                resources = [r for r in resources if r.status == status]
            if tags:
                resources = [r for r in resources if any(tag in r.tags for tag in tags)]
                
            return resources
        except Exception as e:
            logger.error(f"Failed to list resources: {e}")
            await self.logging_service.log_message(
                "error",
                f"Failed to list resources: {e}"
            )
            return []

    async def allocate_resource(
        self,
        resource_id: str,
        capacity: float,
        project_id: Optional[str] = None,
        simulation_id: Optional[str] = None,
        priority: ResourcePriority = ResourcePriority.MEDIUM,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        allocated_by: str = None
    ) -> Optional[str]:
        """Allocate a resource"""
        try:
            resource = await self.get_resource(resource_id)
            if not resource:
                await self.logging_service.log_message(
                    "error",
                    f"Resource {resource_id} not found"
                )
                return None
                
            if resource.used_capacity + capacity > resource.capacity:
                await self.logging_service.log_message(
                    "error",
                    f"Insufficient capacity for resource {resource_id}"
                )
                return None
                
            allocation_id = f"alloc_{len(self.allocations) + 1}"
            allocation = ResourceAllocation(
                id=allocation_id,
                resource_id=resource_id,
                project_id=project_id,
                simulation_id=simulation_id,
                allocated_capacity=capacity,
                start_time=start_time or datetime.utcnow(),
                end_time=end_time,
                status="active",
                priority=priority,
                allocated_by=allocated_by,
                allocated_at=datetime.utcnow()
            )
            
            self.allocations[allocation_id] = allocation
            resource.used_capacity += capacity
            
            await self.logging_service.log_message(
                "info",
                f"Resource {resource_id} allocated",
                details={
                    "allocation_id": allocation_id,
                    "capacity": capacity,
                    "project_id": project_id,
                    "simulation_id": simulation_id
                }
            )
            return allocation_id
        except Exception as e:
            logger.error(f"Failed to allocate resource: {e}")
            await self.logging_service.log_message(
                "error",
                f"Failed to allocate resource: {e}",
                details={"resource_id": resource_id}
            )
            return None

    async def release_resource(self, allocation_id: str) -> bool:
        """Release an allocated resource"""
        try:
            allocation = self.allocations.get(allocation_id)
            if not allocation:
                await self.logging_service.log_message(
                    "error",
                    f"Allocation {allocation_id} not found"
                )
                return False
                
            resource = await self.get_resource(allocation.resource_id)
            if not resource:
                await self.logging_service.log_message(
                    "error",
                    f"Resource {allocation.resource_id} not found"
                )
                return False
                
            resource.used_capacity -= allocation.allocated_capacity
            allocation.status = "released"
            allocation.released_at = datetime.utcnow()
            
            await self.logging_service.log_message(
                "info",
                f"Resource {allocation.resource_id} released",
                details={"allocation_id": allocation_id}
            )
            return True
        except Exception as e:
            logger.error(f"Failed to release resource: {e}")
            await self.logging_service.log_message(
                "error",
                f"Failed to release resource: {e}",
                details={"allocation_id": allocation_id}
            )
            return False

    async def get_resource_utilization(self, resource_id: str) -> Dict:
        """Get resource utilization metrics"""
        try:
            resource = await self.get_resource(resource_id)
            if not resource:
                return {}
                
            active_allocations = [
                a for a in self.allocations.values()
                if a.resource_id == resource_id and a.status == "active"
            ]
            
            return {
                "total_capacity": resource.capacity,
                "used_capacity": resource.used_capacity,
                "available_capacity": resource.capacity - resource.used_capacity,
                "utilization_percentage": (resource.used_capacity / resource.capacity) * 100,
                "active_allocations": len(active_allocations)
            }
        except Exception as e:
            logger.error(f"Failed to get resource utilization: {e}")
            await self.logging_service.log_message(
                "error",
                f"Failed to get resource utilization: {e}",
                details={"resource_id": resource_id}
            )
            return {}

    async def set_resource_constraints(
        self,
        resource_id: str,
        constraint: ResourceConstraint
    ) -> bool:
        """Set constraints for a resource"""
        try:
            if resource_id not in self.resources:
                await self.logging_service.log_message(
                    "error",
                    f"Resource {resource_id} not found"
                )
                return False
                
            self.constraints[resource_id] = constraint
            await self.logging_service.log_message(
                "info",
                f"Constraints set for resource {resource_id}"
            )
            return True
        except Exception as e:
            logger.error(f"Failed to set resource constraints: {e}")
            await self.logging_service.log_message(
                "error",
                f"Failed to set resource constraints: {e}",
                details={"resource_id": resource_id}
            )
            return False

    async def check_resource_availability(
        self,
        resource_id: str,
        required_capacity: float,
        start_time: datetime,
        end_time: Optional[datetime] = None
    ) -> bool:
        """Check if a resource is available for allocation"""
        try:
            resource = await self.get_resource(resource_id)
            if not resource:
                return False
                
            # Check capacity constraints
            if resource.used_capacity + required_capacity > resource.capacity:
                return False
                
            # Check time constraints
            constraint = self.constraints.get(resource_id)
            if constraint:
                if required_capacity < constraint.min_capacity or required_capacity > constraint.max_capacity:
                    return False
                    
                # Check blackout periods
                for blackout in constraint.blackout_periods:
                    if (start_time >= blackout["start"] and
                        (not end_time or end_time <= blackout["end"])):
                        return False
                        
            return True
        except Exception as e:
            logger.error(f"Failed to check resource availability: {e}")
            await self.logging_service.log_message(
                "error",
                f"Failed to check resource availability: {e}",
                details={"resource_id": resource_id}
            )
            return False

    async def optimize_resource_allocation(
        self,
        project_id: Optional[str] = None,
        simulation_id: Optional[str] = None
    ) -> Dict:
        """Optimize resource allocation based on usage patterns and constraints"""
        try:
            allocations = [
                a for a in self.allocations.values()
                if (a.status == "active" and
                    (not project_id or a.project_id == project_id) and
                    (not simulation_id or a.simulation_id == simulation_id))
            ]
            
            optimization_results = {
                "total_allocations": len(allocations),
                "optimization_suggestions": [],
                "potential_savings": 0.0
            }
            
            for allocation in allocations:
                resource = await self.get_resource(allocation.resource_id)
                if not resource:
                    continue
                    
                # Check for underutilization
                if allocation.allocated_capacity > (resource.capacity * 0.8):
                    optimization_results["optimization_suggestions"].append({
                        "allocation_id": allocation.id,
                        "resource_id": resource.id,
                        "suggestion": "Consider reducing allocated capacity",
                        "current_capacity": allocation.allocated_capacity,
                        "suggested_capacity": resource.capacity * 0.7
                    })
                    
                # Calculate potential cost savings
                potential_saving = (
                    allocation.allocated_capacity -
                    (resource.capacity * 0.7)
                ) * resource.cost_per_unit
                optimization_results["potential_savings"] += potential_saving
                
            await self.logging_service.log_message(
                "info",
                "Resource allocation optimization completed",
                details=optimization_results
            )
            return optimization_results
        except Exception as e:
            logger.error(f"Failed to optimize resource allocation: {e}")
            await self.logging_service.log_message(
                "error",
                f"Failed to optimize resource allocation: {e}"
            )
            return {} 