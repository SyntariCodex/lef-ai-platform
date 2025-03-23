"""
API endpoints for resource allocation service
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from ..services.resource_allocation_service import (
    ResourceAllocationService,
    Resource,
    ResourceAllocation,
    ResourceType,
    ResourceStatus,
    AllocationPriority,
    ResourceCapacity,
    ResourceCost
)
from ..services.logging_service import LoggingService
from ..services.security_service import SecurityService

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize services
resource_allocation_service = ResourceAllocationService()
logging_service = LoggingService()
security_service = SecurityService()

class ResourceCreate(BaseModel):
    """Resource creation request"""
    name: str
    type: ResourceType
    capacity: ResourceCapacity
    cost: ResourceCost
    skills: Optional[List[str]] = None
    specifications: Optional[Dict] = None
    availability_schedule: Dict[str, List[Dict[str, datetime]]]
    dependencies: List[str] = []
    metadata: Optional[Dict] = None

class ResourceUpdate(BaseModel):
    """Resource update request"""
    name: Optional[str] = None
    status: Optional[ResourceStatus] = None
    capacity: Optional[ResourceCapacity] = None
    cost: Optional[ResourceCost] = None
    skills: Optional[List[str]] = None
    specifications: Optional[Dict] = None
    availability_schedule: Optional[Dict[str, List[Dict[str, datetime]]]] = None
    dependencies: Optional[List[str]] = None
    metadata: Optional[Dict] = None

class AllocationCreate(BaseModel):
    """Resource allocation request"""
    resource_id: str
    project_id: Optional[str] = None
    simulation_id: Optional[str] = None
    quantity: float
    start_time: datetime
    end_time: datetime
    priority: AllocationPriority
    cost_estimate: float
    notes: Optional[str] = None
    metadata: Optional[Dict] = None

class AllocationUpdate(BaseModel):
    """Resource allocation update request"""
    quantity: Optional[float] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    priority: Optional[AllocationPriority] = None
    status: Optional[str] = None
    actual_cost: Optional[float] = None
    utilization: Optional[float] = None
    notes: Optional[str] = None
    metadata: Optional[Dict] = None

@router.post("/resources", response_model=Dict)
async def create_resource(
    resource: ResourceCreate,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Create a new resource"""
    try:
        # Check permissions
        if not await security_service.check_permission(current_user["id"], "create_resources"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to create resources"
            )
            
        # Create resource object
        new_resource = Resource(
            id=f"resource_{datetime.utcnow().timestamp()}",
            status=ResourceStatus.AVAILABLE,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            created_by=current_user["id"],
            updated_by=current_user["id"],
            **resource.dict()
        )
        
        success, resource_id = await resource_allocation_service.create_resource(new_resource)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create resource"
            )
            
        return {
            "message": "Resource created successfully",
            "resource_id": resource_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create resource: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to create resource: {e}",
            details={"resource_name": resource.name}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.put("/resources/{resource_id}", response_model=Dict)
async def update_resource(
    resource_id: str,
    updates: ResourceUpdate,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Update an existing resource"""
    try:
        # Check permissions
        if not await security_service.check_permission(current_user["id"], "update_resources"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update resources"
            )
            
        # Add user to updates
        updates_dict = updates.dict(exclude_unset=True)
        updates_dict["updated_by"] = current_user["id"]
        updates_dict["updated_at"] = datetime.utcnow()
        
        success = await resource_allocation_service.update_resource(resource_id, updates_dict)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update resource"
            )
            
        return {
            "message": "Resource updated successfully",
            "resource_id": resource_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update resource: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to update resource: {e}",
            details={"resource_id": resource_id}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.delete("/resources/{resource_id}", response_model=Dict)
async def delete_resource(
    resource_id: str,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Delete a resource"""
    try:
        # Check permissions
        if not await security_service.check_permission(current_user["id"], "delete_resources"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete resources"
            )
            
        success = await resource_allocation_service.delete_resource(resource_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to delete resource"
            )
            
        return {
            "message": "Resource deleted successfully",
            "resource_id": resource_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete resource: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to delete resource: {e}",
            details={"resource_id": resource_id}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/resources/{resource_id}", response_model=Dict)
async def get_resource(
    resource_id: str,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Get a resource by ID"""
    try:
        # Check permissions
        if not await security_service.check_permission(current_user["id"], "view_resources"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view resources"
            )
            
        resource = await resource_allocation_service.get_resource(resource_id)
        
        if not resource:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resource not found"
            )
            
        return resource.dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get resource: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to get resource: {e}",
            details={"resource_id": resource_id}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/resources", response_model=List[Dict])
async def list_resources(
    resource_type: Optional[ResourceType] = None,
    status: Optional[ResourceStatus] = None,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """List resources with optional filters"""
    try:
        # Check permissions
        if not await security_service.check_permission(current_user["id"], "view_resources"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view resources"
            )
            
        resources = await resource_allocation_service.list_resources(
            resource_type,
            status
        )
        
        return [resource.dict() for resource in resources]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list resources: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to list resources: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/allocations", response_model=Dict)
async def create_allocation(
    allocation: AllocationCreate,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Create a new resource allocation"""
    try:
        # Check permissions
        if not await security_service.check_permission(current_user["id"], "create_allocations"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to create allocations"
            )
            
        # Create allocation object
        new_allocation = ResourceAllocation(
            id=f"allocation_{datetime.utcnow().timestamp()}",
            status="active",
            utilization=0.0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            created_by=current_user["id"],
            updated_by=current_user["id"],
            **allocation.dict()
        )
        
        success, allocation_id = await resource_allocation_service.allocate_resource(new_allocation)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create allocation"
            )
            
        return {
            "message": "Resource allocated successfully",
            "allocation_id": allocation_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create allocation: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to create allocation: {e}",
            details={"resource_id": allocation.resource_id}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.put("/allocations/{allocation_id}", response_model=Dict)
async def update_allocation(
    allocation_id: str,
    updates: AllocationUpdate,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Update an existing allocation"""
    try:
        # Check permissions
        if not await security_service.check_permission(current_user["id"], "update_allocations"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update allocations"
            )
            
        # Get current allocation
        allocation = await resource_allocation_service.get_allocation(allocation_id)
        if not allocation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Allocation not found"
            )
            
        # Add user to updates
        updates_dict = updates.dict(exclude_unset=True)
        updates_dict["updated_by"] = current_user["id"]
        updates_dict["updated_at"] = datetime.utcnow()
        
        # Update allocation
        success = await resource_allocation_service.update_allocation(allocation_id, updates_dict)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update allocation"
            )
            
        return {
            "message": "Allocation updated successfully",
            "allocation_id": allocation_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update allocation: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to update allocation: {e}",
            details={"allocation_id": allocation_id}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/allocations/{allocation_id}/release", response_model=Dict)
async def release_allocation(
    allocation_id: str,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Release a resource allocation"""
    try:
        # Check permissions
        if not await security_service.check_permission(current_user["id"], "release_allocations"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to release allocations"
            )
            
        success = await resource_allocation_service.deallocate_resource(allocation_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to release allocation"
            )
            
        return {
            "message": "Resource allocation released successfully",
            "allocation_id": allocation_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to release allocation: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to release allocation: {e}",
            details={"allocation_id": allocation_id}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/allocations/{allocation_id}", response_model=Dict)
async def get_allocation(
    allocation_id: str,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Get an allocation by ID"""
    try:
        # Check permissions
        if not await security_service.check_permission(current_user["id"], "view_allocations"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view allocations"
            )
            
        allocation = await resource_allocation_service.get_allocation(allocation_id)
        
        if not allocation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Allocation not found"
            )
            
        return allocation.dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get allocation: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to get allocation: {e}",
            details={"allocation_id": allocation_id}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/allocations", response_model=List[Dict])
async def list_allocations(
    resource_id: Optional[str] = None,
    project_id: Optional[str] = None,
    simulation_id: Optional[str] = None,
    status: Optional[str] = None,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """List allocations with optional filters"""
    try:
        # Check permissions
        if not await security_service.check_permission(current_user["id"], "view_allocations"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view allocations"
            )
            
        allocations = await resource_allocation_service.list_allocations(
            resource_id,
            project_id,
            simulation_id,
            status
        )
        
        return [allocation.dict() for allocation in allocations]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list allocations: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to list allocations: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/resources/{resource_id}/utilization", response_model=Dict)
async def get_resource_utilization(
    resource_id: str,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Get resource utilization metrics"""
    try:
        # Check permissions
        if not await security_service.check_permission(current_user["id"], "view_resource_utilization"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view resource utilization"
            )
            
        utilization = await resource_allocation_service.get_resource_utilization(
            resource_id,
            start_time,
            end_time
        )
        
        if not utilization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resource not found or no utilization data available"
            )
            
        return utilization
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get resource utilization: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to get resource utilization: {e}",
            details={"resource_id": resource_id}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/optimize", response_model=Dict)
async def optimize_allocations(
    project_id: Optional[str] = None,
    simulation_id: Optional[str] = None,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Optimize resource allocations"""
    try:
        # Check permissions
        if not await security_service.check_permission(current_user["id"], "optimize_resources"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to optimize resources"
            )
            
        optimization_results = await resource_allocation_service.optimize_allocations(
            project_id,
            simulation_id
        )
        
        if not optimization_results:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to optimize allocations"
            )
            
        return optimization_results
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to optimize allocations: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to optimize allocations: {e}",
            details={
                "project_id": project_id,
                "simulation_id": simulation_id
            }
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) 