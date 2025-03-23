"""
API endpoints for resource management service
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from ..services.resource_management_service import (
    ResourceManagementService,
    Resource,
    ResourceType,
    ResourceStatus,
    ResourcePriority,
    ResourceConstraint
)
from ..services.logging_service import LoggingService
from ..services.security_service import SecurityService

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize services
resource_management_service = ResourceManagementService()
logging_service = LoggingService()
security_service = SecurityService()

class ResourceCreate(BaseModel):
    """Resource creation request"""
    name: str
    description: str
    type: ResourceType
    capacity: float
    unit: str
    cost_per_unit: float
    priority: ResourcePriority
    tags: List[str]
    metadata: Optional[Dict] = None

class ResourceUpdate(BaseModel):
    """Resource update request"""
    name: Optional[str] = None
    description: Optional[str] = None
    type: Optional[ResourceType] = None
    capacity: Optional[float] = None
    unit: Optional[str] = None
    cost_per_unit: Optional[float] = None
    priority: Optional[ResourcePriority] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict] = None

class ResourceAllocationRequest(BaseModel):
    """Resource allocation request"""
    capacity: float
    project_id: Optional[str] = None
    simulation_id: Optional[str] = None
    priority: ResourcePriority = ResourcePriority.MEDIUM
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

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
            used_capacity=0.0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            created_by=current_user["id"],
            **resource.dict()
        )
        
        success = await resource_management_service.create_resource(new_resource)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create resource"
            )
            
        return {
            "message": "Resource created successfully",
            "resource_id": new_resource.id
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
        
        success = await resource_management_service.update_resource(resource_id, updates_dict)
        
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
            
        resource = await resource_management_service.get_resource(resource_id)
        
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
    tags: Optional[List[str]] = None,
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
            
        resources = await resource_management_service.list_resources(
            resource_type,
            status,
            tags
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

@router.post("/resources/{resource_id}/allocate", response_model=Dict)
async def allocate_resource(
    resource_id: str,
    allocation: ResourceAllocationRequest,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Allocate a resource"""
    try:
        # Check permissions
        if not await security_service.check_permission(current_user["id"], "allocate_resources"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to allocate resources"
            )
            
        # Check resource availability
        is_available = await resource_management_service.check_resource_availability(
            resource_id,
            allocation.capacity,
            allocation.start_time or datetime.utcnow(),
            allocation.end_time
        )
        
        if not is_available:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Resource not available for allocation"
            )
            
        allocation_id = await resource_management_service.allocate_resource(
            resource_id,
            allocation.capacity,
            allocation.project_id,
            allocation.simulation_id,
            allocation.priority,
            allocation.start_time,
            allocation.end_time,
            current_user["id"]
        )
        
        if not allocation_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to allocate resource"
            )
            
        return {
            "message": "Resource allocated successfully",
            "allocation_id": allocation_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to allocate resource: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to allocate resource: {e}",
            details={"resource_id": resource_id}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/resources/allocations/{allocation_id}/release", response_model=Dict)
async def release_resource(
    allocation_id: str,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Release an allocated resource"""
    try:
        # Check permissions
        if not await security_service.check_permission(current_user["id"], "release_resources"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to release resources"
            )
            
        success = await resource_management_service.release_resource(allocation_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to release resource"
            )
            
        return {
            "message": "Resource released successfully",
            "allocation_id": allocation_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to release resource: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to release resource: {e}",
            details={"allocation_id": allocation_id}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/resources/{resource_id}/utilization", response_model=Dict)
async def get_resource_utilization(
    resource_id: str,
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
            
        utilization = await resource_management_service.get_resource_utilization(resource_id)
        
        if not utilization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resource not found"
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

@router.post("/resources/{resource_id}/constraints", response_model=Dict)
async def set_resource_constraints(
    resource_id: str,
    constraint: ResourceConstraint,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Set constraints for a resource"""
    try:
        # Check permissions
        if not await security_service.check_permission(current_user["id"], "manage_resource_constraints"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to manage resource constraints"
            )
            
        success = await resource_management_service.set_resource_constraints(
            resource_id,
            constraint
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to set resource constraints"
            )
            
        return {
            "message": "Resource constraints set successfully",
            "resource_id": resource_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to set resource constraints: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to set resource constraints: {e}",
            details={"resource_id": resource_id}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/resources/optimize", response_model=Dict)
async def optimize_resource_allocation(
    project_id: Optional[str] = None,
    simulation_id: Optional[str] = None,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Optimize resource allocation"""
    try:
        # Check permissions
        if not await security_service.check_permission(current_user["id"], "optimize_resources"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to optimize resources"
            )
            
        optimization_results = await resource_management_service.optimize_resource_allocation(
            project_id,
            simulation_id
        )
        
        return optimization_results
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to optimize resource allocation: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to optimize resource allocation: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) 