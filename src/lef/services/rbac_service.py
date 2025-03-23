"""
Role-based access control service
"""

import logging
from typing import Dict, List, Optional, Set
from pydantic import BaseModel, Field
from fastapi import HTTPException, status

from ..services.logging_service import LoggingService
from ..services.alert_service import AlertService, AlertSeverity

logger = logging.getLogger(__name__)

class Permission(BaseModel):
    """Permission model"""
    name: str
    description: str
    resource: str
    action: str

class Role(BaseModel):
    """Role model"""
    name: str
    description: str
    permissions: Set[str] = Field(default_factory=set)
    parent_roles: Set[str] = Field(default_factory=set)

class RBACService:
    """Service for managing roles and permissions"""
    
    def __init__(self):
        self.logging_service = LoggingService()
        self.alert_service = AlertService()
        
        # Initialize default roles and permissions
        self.permissions: Dict[str, Permission] = {}
        self.roles: Dict[str, Role] = {}
        self._initialize_default_permissions()
        self._initialize_default_roles()
        
    def _initialize_default_permissions(self):
        """Initialize default system permissions"""
        default_permissions = [
            Permission(
                name="read:users",
                description="Read user information",
                resource="users",
                action="read"
            ),
            Permission(
                name="write:users",
                description="Modify user information",
                resource="users",
                action="write"
            ),
            Permission(
                name="delete:users",
                description="Delete users",
                resource="users",
                action="delete"
            ),
            Permission(
                name="read:roles",
                description="Read role information",
                resource="roles",
                action="read"
            ),
            Permission(
                name="write:roles",
                description="Modify role information",
                resource="roles",
                action="write"
            ),
            Permission(
                name="delete:roles",
                description="Delete roles",
                resource="roles",
                action="delete"
            ),
            Permission(
                name="read:permissions",
                description="Read permission information",
                resource="permissions",
                action="read"
            ),
            Permission(
                name="write:permissions",
                description="Modify permission information",
                resource="permissions",
                action="write"
            ),
            Permission(
                name="delete:permissions",
                description="Delete permissions",
                resource="permissions",
                action="delete"
            ),
            Permission(
                name="admin:all",
                description="Full system access",
                resource="*",
                action="*"
            )
        ]
        
        for permission in default_permissions:
            self.permissions[permission.name] = permission
            
    def _initialize_default_roles(self):
        """Initialize default system roles"""
        default_roles = [
            Role(
                name="admin",
                description="System administrator with full access",
                permissions={"admin:all"}
            ),
            Role(
                name="user_manager",
                description="User management role",
                permissions={
                    "read:users",
                    "write:users",
                    "delete:users",
                    "read:roles",
                    "read:permissions"
                }
            ),
            Role(
                name="role_manager",
                description="Role management role",
                permissions={
                    "read:roles",
                    "write:roles",
                    "delete:roles",
                    "read:permissions"
                }
            ),
            Role(
                name="user",
                description="Standard user role",
                permissions={
                    "read:users"
                }
            )
        ]
        
        for role in default_roles:
            self.roles[role.name] = role
            
    async def create_permission(self, permission: Permission) -> Permission:
        """Create a new permission"""
        try:
            if permission.name in self.permissions:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Permission {permission.name} already exists"
                )
                
            self.permissions[permission.name] = permission
            
            await self.logging_service.log(
                level="INFO",
                message=f"Created new permission: {permission.name}",
                service="rbac_service"
            )
            
            return permission
            
        except Exception as e:
            await self.logging_service.log(
                level="ERROR",
                message=f"Failed to create permission: {e}",
                service="rbac_service"
            )
            raise
            
    async def create_role(self, role: Role) -> Role:
        """Create a new role"""
        try:
            if role.name in self.roles:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Role {role.name} already exists"
                )
                
            # Validate permissions
            for permission in role.permissions:
                if permission not in self.permissions:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Permission {permission} does not exist"
                    )
                    
            # Validate parent roles
            for parent_role in role.parent_roles:
                if parent_role not in self.roles:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Parent role {parent_role} does not exist"
                    )
                    
            self.roles[role.name] = role
            
            await self.logging_service.log(
                level="INFO",
                message=f"Created new role: {role.name}",
                service="rbac_service"
            )
            
            return role
            
        except Exception as e:
            await self.logging_service.log(
                level="ERROR",
                message=f"Failed to create role: {e}",
                service="rbac_service"
            )
            raise
            
    async def update_role(self, role_name: str, role: Role) -> Role:
        """Update an existing role"""
        try:
            if role_name not in self.roles:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Role {role_name} does not exist"
                )
                
            # Validate permissions
            for permission in role.permissions:
                if permission not in self.permissions:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Permission {permission} does not exist"
                    )
                    
            # Validate parent roles
            for parent_role in role.parent_roles:
                if parent_role not in self.roles:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Parent role {parent_role} does not exist"
                    )
                    
            self.roles[role_name] = role
            
            await self.logging_service.log(
                level="INFO",
                message=f"Updated role: {role_name}",
                service="rbac_service"
            )
            
            return role
            
        except Exception as e:
            await self.logging_service.log(
                level="ERROR",
                message=f"Failed to update role: {e}",
                service="rbac_service"
            )
            raise
            
    async def delete_role(self, role_name: str) -> bool:
        """Delete a role"""
        try:
            if role_name not in self.roles:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Role {role_name} does not exist"
                )
                
            # Check if role is a parent of other roles
            for role in self.roles.values():
                if role_name in role.parent_roles:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Cannot delete role {role_name} as it is a parent of other roles"
                    )
                    
            del self.roles[role_name]
            
            await self.logging_service.log(
                level="INFO",
                message=f"Deleted role: {role_name}",
                service="rbac_service"
            )
            
            return True
            
        except Exception as e:
            await self.logging_service.log(
                level="ERROR",
                message=f"Failed to delete role: {e}",
                service="rbac_service"
            )
            raise
            
    async def get_role_permissions(self, role_name: str) -> Set[str]:
        """Get all permissions for a role, including inherited permissions"""
        try:
            if role_name not in self.roles:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Role {role_name} does not exist"
                )
                
            role = self.roles[role_name]
            permissions = role.permissions.copy()
            
            # Add permissions from parent roles
            for parent_role_name in role.parent_roles:
                parent_permissions = await self.get_role_permissions(parent_role_name)
                permissions.update(parent_permissions)
                
            return permissions
            
        except Exception as e:
            await self.logging_service.log(
                level="ERROR",
                message=f"Failed to get role permissions: {e}",
                service="rbac_service"
            )
            raise
            
    async def check_permission(self, role_name: str, permission: str) -> bool:
        """Check if a role has a specific permission"""
        try:
            permissions = await self.get_role_permissions(role_name)
            return permission in permissions
        except Exception as e:
            await self.logging_service.log(
                level="ERROR",
                message=f"Failed to check permission: {e}",
                service="rbac_service"
            )
            return False
            
    async def get_all_roles(self) -> List[Role]:
        """Get all roles"""
        return list(self.roles.values())
        
    async def get_all_permissions(self) -> List[Permission]:
        """Get all permissions"""
        return list(self.permissions.values())
        
    async def get_role(self, role_name: str) -> Optional[Role]:
        """Get a specific role"""
        return self.roles.get(role_name)
        
    async def get_permission(self, permission_name: str) -> Optional[Permission]:
        """Get a specific permission"""
        return self.permissions.get(permission_name) 