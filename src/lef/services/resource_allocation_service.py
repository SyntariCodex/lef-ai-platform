"""
Resource allocation service for managing and optimizing resource distribution
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from enum import Enum
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class ResourceType(Enum):
    """Types of resources that can be allocated"""
    HUMAN = "human"
    COMPUTE = "compute"
    FINANCIAL = "financial"
    EQUIPMENT = "equipment"
    LICENSE = "license"
    FACILITY = "facility"
    CUSTOM = "custom"

class ResourceStatus(Enum):
    """Status of a resource"""
    AVAILABLE = "available"
    ALLOCATED = "allocated"
    MAINTENANCE = "maintenance"
    RESERVED = "reserved"
    UNAVAILABLE = "unavailable"

class AllocationPriority(Enum):
    """Priority levels for resource allocation"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class ResourceCapacity(BaseModel):
    """Resource capacity model"""
    total: float
    allocated: float
    reserved: float
    available: float
    unit: str

class ResourceCost(BaseModel):
    """Resource cost model"""
    base_rate: float
    overtime_rate: Optional[float]
    currency: str
    billing_cycle: str  # hourly, daily, monthly, etc.

class Resource(BaseModel):
    """Resource model"""
    id: str
    name: str
    type: ResourceType
    status: ResourceStatus
    capacity: ResourceCapacity
    cost: ResourceCost
    skills: Optional[List[str]] = None  # For human resources
    specifications: Optional[Dict] = None  # Technical specs
    availability_schedule: Dict[str, List[Dict[str, datetime]]]
    dependencies: List[str] = []
    metadata: Dict = {}
    created_at: datetime
    updated_at: datetime
    created_by: str
    updated_by: str

class ResourceAllocation(BaseModel):
    """Resource allocation model"""
    id: str
    resource_id: str
    project_id: Optional[str]
    simulation_id: Optional[str]
    quantity: float
    start_time: datetime
    end_time: datetime
    priority: AllocationPriority
    status: str
    cost_estimate: float
    actual_cost: Optional[float]
    utilization: float
    notes: Optional[str]
    metadata: Dict = {}
    created_at: datetime
    updated_at: datetime
    created_by: str
    updated_by: str

class ResourceAllocationService:
    """Service for managing resource allocation"""
    
    def __init__(self):
        """Initialize the service"""
        self.resources: Dict[str, Resource] = {}
        self.allocations: Dict[str, ResourceAllocation] = {}
        
    async def initialize(self) -> bool:
        """Initialize the service"""
        try:
            logger.info("Initializing resource allocation service")
            # Initialize data stores, connections, etc.
            return True
        except Exception as e:
            logger.error(f"Failed to initialize resource allocation service: {e}")
            return False
            
    async def cleanup(self) -> bool:
        """Cleanup service resources"""
        try:
            logger.info("Cleaning up resource allocation service")
            # Cleanup connections, temp data, etc.
            return True
        except Exception as e:
            logger.error(f"Failed to cleanup resource allocation service: {e}")
            return False
            
    async def create_resource(self, resource: Resource) -> Tuple[bool, Optional[str]]:
        """Create a new resource"""
        try:
            if resource.id in self.resources:
                return False, "Resource ID already exists"
                
            self.resources[resource.id] = resource
            logger.info(f"Created resource: {resource.id}")
            return True, resource.id
        except Exception as e:
            logger.error(f"Failed to create resource: {e}")
            return False, str(e)
            
    async def update_resource(self, resource_id: str, updates: Dict) -> bool:
        """Update an existing resource"""
        try:
            if resource_id not in self.resources:
                return False
                
            resource = self.resources[resource_id]
            updated_resource = resource.copy(update=updates)
            self.resources[resource_id] = updated_resource
            logger.info(f"Updated resource: {resource_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to update resource: {e}")
            return False
            
    async def delete_resource(self, resource_id: str) -> bool:
        """Delete a resource"""
        try:
            if resource_id not in self.resources:
                return False
                
            # Check for active allocations
            active_allocations = [
                a for a in self.allocations.values()
                if a.resource_id == resource_id and a.status == "active"
            ]
            if active_allocations:
                return False
                
            del self.resources[resource_id]
            logger.info(f"Deleted resource: {resource_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete resource: {e}")
            return False
            
    async def get_resource(self, resource_id: str) -> Optional[Resource]:
        """Get a resource by ID"""
        return self.resources.get(resource_id)
        
    async def list_resources(
        self,
        resource_type: Optional[ResourceType] = None,
        status: Optional[ResourceStatus] = None
    ) -> List[Resource]:
        """List resources with optional filters"""
        resources = list(self.resources.values())
        
        if resource_type:
            resources = [r for r in resources if r.type == resource_type]
        if status:
            resources = [r for r in resources if r.status == status]
            
        return resources
        
    async def allocate_resource(
        self,
        allocation: ResourceAllocation
    ) -> Tuple[bool, Optional[str]]:
        """Allocate a resource"""
        try:
            resource = self.resources.get(allocation.resource_id)
            if not resource:
                return False, "Resource not found"
                
            # Check resource availability
            if resource.status != ResourceStatus.AVAILABLE:
                return False, "Resource not available"
                
            # Check capacity
            if allocation.quantity > resource.capacity.available:
                return False, "Insufficient capacity"
                
            # Check scheduling conflicts
            if not await self._check_availability(
                resource,
                allocation.start_time,
                allocation.end_time
            ):
                return False, "Scheduling conflict"
                
            # Create allocation
            self.allocations[allocation.id] = allocation
            
            # Update resource capacity
            resource.capacity.allocated += allocation.quantity
            resource.capacity.available -= allocation.quantity
            
            logger.info(f"Created allocation: {allocation.id}")
            return True, allocation.id
        except Exception as e:
            logger.error(f"Failed to allocate resource: {e}")
            return False, str(e)
            
    async def deallocate_resource(
        self,
        allocation_id: str
    ) -> bool:
        """Deallocate a resource"""
        try:
            allocation = self.allocations.get(allocation_id)
            if not allocation:
                return False
                
            resource = self.resources.get(allocation.resource_id)
            if not resource:
                return False
                
            # Update resource capacity
            resource.capacity.allocated -= allocation.quantity
            resource.capacity.available += allocation.quantity
            
            # Update allocation status
            allocation.status = "completed"
            allocation.updated_at = datetime.utcnow()
            
            logger.info(f"Deallocated resource: {allocation_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to deallocate resource: {e}")
            return False
            
    async def get_allocation(
        self,
        allocation_id: str
    ) -> Optional[ResourceAllocation]:
        """Get an allocation by ID"""
        return self.allocations.get(allocation_id)
        
    async def list_allocations(
        self,
        resource_id: Optional[str] = None,
        project_id: Optional[str] = None,
        simulation_id: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[ResourceAllocation]:
        """List allocations with optional filters"""
        allocations = list(self.allocations.values())
        
        if resource_id:
            allocations = [a for a in allocations if a.resource_id == resource_id]
        if project_id:
            allocations = [a for a in allocations if a.project_id == project_id]
        if simulation_id:
            allocations = [a for a in allocations if a.simulation_id == simulation_id]
        if status:
            allocations = [a for a in allocations if a.status == status]
            
        return allocations
        
    async def get_resource_utilization(
        self,
        resource_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict:
        """Get resource utilization metrics"""
        try:
            resource = self.resources.get(resource_id)
            if not resource:
                return {}
                
            allocations = [
                a for a in self.allocations.values()
                if a.resource_id == resource_id
            ]
            
            if start_time:
                allocations = [
                    a for a in allocations
                    if a.end_time >= start_time
                ]
            if end_time:
                allocations = [
                    a for a in allocations
                    if a.start_time <= end_time
                ]
                
            total_capacity = resource.capacity.total
            total_allocated = sum(a.quantity for a in allocations)
            utilization_rate = (total_allocated / total_capacity) if total_capacity > 0 else 0
            
            return {
                "resource_id": resource_id,
                "total_capacity": total_capacity,
                "total_allocated": total_allocated,
                "utilization_rate": utilization_rate,
                "allocation_count": len(allocations),
                "start_time": start_time,
                "end_time": end_time
            }
        except Exception as e:
            logger.error(f"Failed to get resource utilization: {e}")
            return {}
            
    async def optimize_allocations(
        self,
        project_id: Optional[str] = None,
        simulation_id: Optional[str] = None
    ) -> Dict:
        """Optimize resource allocations"""
        try:
            allocations = self.list_allocations(
                project_id=project_id,
                simulation_id=simulation_id
            )
            
            # Implement optimization logic here
            # This could include:
            # - Load balancing
            # - Cost optimization
            # - Schedule optimization
            # - Resource leveling
            
            optimization_results = {
                "original_cost": sum(a.cost_estimate for a in allocations),
                "optimized_cost": 0,  # Calculate after optimization
                "resource_savings": {},
                "schedule_impact": {},
                "recommendations": []
            }
            
            return optimization_results
        except Exception as e:
            logger.error(f"Failed to optimize allocations: {e}")
            return {}
            
    async def _check_availability(
        self,
        resource: Resource,
        start_time: datetime,
        end_time: datetime
    ) -> bool:
        """Check if a resource is available for the given time period"""
        try:
            # Get existing allocations for the resource
            existing_allocations = [
                a for a in self.allocations.values()
                if a.resource_id == resource.id and a.status == "active"
            ]
            
            # Check for scheduling conflicts
            for allocation in existing_allocations:
                if (
                    (start_time <= allocation.end_time) and
                    (end_time >= allocation.start_time)
                ):
                    return False
                    
            return True
        except Exception as e:
            logger.error(f"Failed to check resource availability: {e}")
            return False
            
    async def check_health(self) -> Dict:
        """Check service health"""
        return {
            "status": "healthy",
            "resource_count": len(self.resources),
            "allocation_count": len(self.allocations)
        } 