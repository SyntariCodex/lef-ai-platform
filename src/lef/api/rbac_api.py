"""
RBAC API endpoints
"""

import logging
from typing import List, Set
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from ..services.rbac_service import RBACService, Role, Permission
from ..services.logging_service import LoggingService
from ..auth.auth import get_current_user, check_permission

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/rbac", tags=["rbac"])

# Initialize services
rbac_service = RBACService()
logging_service = LoggingService()

class RoleCreate(BaseModel):
    """Role creation model"""
    name: str
    description: str
    permissions: Set[str] = set()
    parent_roles: Set[str] = set()

class RoleUpdate(BaseModel):
    """Role update model"""
    description: str
    permissions: Set[str]
    parent_roles: Set[str]

class PermissionCreate(BaseModel):
    """Permission creation model"""
    name: str
    description: str
    resource: str
    action: str

@router.post("/roles", response_model=Role)
async def create_role(
    role: RoleCreate,
    current_user: str = Depends(get_current_user)
):
    """Create a new role"""
    try:
        # Check permission
        if not await check_permission(current_user, "write:roles"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
            
        new_role = Role(
            name=role.name,
            description=role.description,
            permissions=role.permissions,
            parent_roles=role.parent_roles
        )
        
        return await rbac_service.create_role(new_role)
        
    except HTTPException as e:
        await logging_service.log(
            level="WARNING",
            message=f"Failed to create role: {e.detail}",
            service="rbac_api"
        )
        raise
    except Exception as e:
        await logging_service.log(
            level="ERROR",
            message=f"Error creating role: {e}",
            service="rbac_api"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.put("/roles/{role_name}", response_model=Role)
async def update_role(
    role_name: str,
    role: RoleUpdate,
    current_user: str = Depends(get_current_user)
):
    """Update an existing role"""
    try:
        # Check permission
        if not await check_permission(current_user, "write:roles"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
            
        updated_role = Role(
            name=role_name,
            description=role.description,
            permissions=role.permissions,
            parent_roles=role.parent_roles
        )
        
        return await rbac_service.update_role(role_name, updated_role)
        
    except HTTPException as e:
        await logging_service.log(
            level="WARNING",
            message=f"Failed to update role: {e.detail}",
            service="rbac_api"
        )
        raise
    except Exception as e:
        await logging_service.log(
            level="ERROR",
            message=f"Error updating role: {e}",
            service="rbac_api"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.delete("/roles/{role_name}")
async def delete_role(
    role_name: str,
    current_user: str = Depends(get_current_user)
):
    """Delete a role"""
    try:
        # Check permission
        if not await check_permission(current_user, "delete:roles"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
            
        success = await rbac_service.delete_role(role_name)
        if success:
            return {"message": f"Role {role_name} deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to delete role"
            )
            
    except HTTPException as e:
        await logging_service.log(
            level="WARNING",
            message=f"Failed to delete role: {e.detail}",
            service="rbac_api"
        )
        raise
    except Exception as e:
        await logging_service.log(
            level="ERROR",
            message=f"Error deleting role: {e}",
            service="rbac_api"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/roles", response_model=List[Role])
async def get_roles(
    current_user: str = Depends(get_current_user)
):
    """Get all roles"""
    try:
        # Check permission
        if not await check_permission(current_user, "read:roles"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
            
        return await rbac_service.get_all_roles()
        
    except HTTPException as e:
        await logging_service.log(
            level="WARNING",
            message=f"Failed to get roles: {e.detail}",
            service="rbac_api"
        )
        raise
    except Exception as e:
        await logging_service.log(
            level="ERROR",
            message=f"Error getting roles: {e}",
            service="rbac_api"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/roles/{role_name}", response_model=Role)
async def get_role(
    role_name: str,
    current_user: str = Depends(get_current_user)
):
    """Get a specific role"""
    try:
        # Check permission
        if not await check_permission(current_user, "read:roles"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
            
        role = await rbac_service.get_role(role_name)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role {role_name} not found"
            )
        return role
        
    except HTTPException as e:
        await logging_service.log(
            level="WARNING",
            message=f"Failed to get role: {e.detail}",
            service="rbac_api"
        )
        raise
    except Exception as e:
        await logging_service.log(
            level="ERROR",
            message=f"Error getting role: {e}",
            service="rbac_api"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/roles/{role_name}/permissions", response_model=Set[str])
async def get_role_permissions(
    role_name: str,
    current_user: str = Depends(get_current_user)
):
    """Get all permissions for a role"""
    try:
        # Check permission
        if not await check_permission(current_user, "read:roles"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
            
        return await rbac_service.get_role_permissions(role_name)
        
    except HTTPException as e:
        await logging_service.log(
            level="WARNING",
            message=f"Failed to get role permissions: {e.detail}",
            service="rbac_api"
        )
        raise
    except Exception as e:
        await logging_service.log(
            level="ERROR",
            message=f"Error getting role permissions: {e}",
            service="rbac_api"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/permissions", response_model=Permission)
async def create_permission(
    permission: PermissionCreate,
    current_user: str = Depends(get_current_user)
):
    """Create a new permission"""
    try:
        # Check permission
        if not await check_permission(current_user, "write:permissions"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
            
        new_permission = Permission(
            name=permission.name,
            description=permission.description,
            resource=permission.resource,
            action=permission.action
        )
        
        return await rbac_service.create_permission(new_permission)
        
    except HTTPException as e:
        await logging_service.log(
            level="WARNING",
            message=f"Failed to create permission: {e.detail}",
            service="rbac_api"
        )
        raise
    except Exception as e:
        await logging_service.log(
            level="ERROR",
            message=f"Error creating permission: {e}",
            service="rbac_api"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/permissions", response_model=List[Permission])
async def get_permissions(
    current_user: str = Depends(get_current_user)
):
    """Get all permissions"""
    try:
        # Check permission
        if not await check_permission(current_user, "read:permissions"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
            
        return await rbac_service.get_all_permissions()
        
    except HTTPException as e:
        await logging_service.log(
            level="WARNING",
            message=f"Failed to get permissions: {e.detail}",
            service="rbac_api"
        )
        raise
    except Exception as e:
        await logging_service.log(
            level="ERROR",
            message=f"Error getting permissions: {e}",
            service="rbac_api"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) 