"""
Permission API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, List, Optional
from datetime import datetime
from ..services.auth_service import AuthService
from ..models.database.permission import Permission
from ..models.user import User
from pydantic import BaseModel

router = APIRouter(prefix="/api/permissions", tags=["permissions"])

# Request/Response models
class PermissionCreate(BaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    requires_approval: bool = False
    approval_level: int = 1
    parent_id: Optional[str] = None
    metadata: Optional[Dict] = None

class PermissionUpdate(BaseModel):
    description: Optional[str] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None
    requires_approval: Optional[bool] = None
    approval_level: Optional[int] = None
    metadata: Optional[Dict] = None

class PermissionResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    category: Optional[str]
    created_at: datetime
    updated_at: datetime
    is_active: bool
    requires_approval: bool
    approval_level: int
    parent_id: Optional[str]
    metadata: Dict
    children: List['PermissionResponse']

# Dependencies
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service)
) -> User:
    is_valid, user = auth_service.validate_token(token)
    if not is_valid or not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

async def check_admin_permission(current_user: User = Depends(get_current_user)):
    """Check if user has admin permission"""
    if not auth_service.check_permission(current_user.username, "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin permission required"
        )

# Endpoints
@router.post("", response_model=PermissionResponse)
async def create_permission(
    permission_data: PermissionCreate,
    current_user: User = Depends(check_admin_permission),
    db: Session = Depends(get_db)
):
    """Create a new permission"""
    try:
        permission = Permission(
            name=permission_data.name,
            description=permission_data.description,
            category=permission_data.category,
            requires_approval=permission_data.requires_approval,
            approval_level=permission_data.approval_level,
            parent_id=uuid.UUID(permission_data.parent_id) if permission_data.parent_id else None,
            metadata=permission_data.metadata or {}
        )
        db.add(permission)
        db.commit()
        db.refresh(permission)
        return permission
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("", response_model=List[PermissionResponse])
async def list_permissions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all permissions"""
    permissions = db.query(Permission).filter(Permission.is_active == True).all()
    return permissions

@router.get("/{permission_id}", response_model=PermissionResponse)
async def get_permission(
    permission_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific permission"""
    permission = db.query(Permission).filter(
        Permission.id == uuid.UUID(permission_id),
        Permission.is_active == True
    ).first()
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found"
        )
    return permission

@router.put("/{permission_id}", response_model=PermissionResponse)
async def update_permission(
    permission_id: str,
    permission_data: PermissionUpdate,
    current_user: User = Depends(check_admin_permission),
    db: Session = Depends(get_db)
):
    """Update a permission"""
    permission = db.query(Permission).filter(
        Permission.id == uuid.UUID(permission_id),
        Permission.is_active == True
    ).first()
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found"
        )

    try:
        for field, value in permission_data.dict(exclude_unset=True).items():
            setattr(permission, field, value)
        db.commit()
        db.refresh(permission)
        return permission
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/{permission_id}")
async def delete_permission(
    permission_id: str,
    current_user: User = Depends(check_admin_permission),
    db: Session = Depends(get_db)
):
    """Delete a permission"""
    permission = db.query(Permission).filter(
        Permission.id == uuid.UUID(permission_id),
        Permission.is_active == True
    ).first()
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found"
        )

    try:
        permission.is_active = False
        db.commit()
        return {"message": "Permission deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/{permission_id}/children/{child_id}")
async def add_child_permission(
    permission_id: str,
    child_id: str,
    current_user: User = Depends(check_admin_permission),
    db: Session = Depends(get_db)
):
    """Add a child permission"""
    parent = db.query(Permission).filter(
        Permission.id == uuid.UUID(permission_id),
        Permission.is_active == True
    ).first()
    if not parent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent permission not found"
        )

    child = db.query(Permission).filter(
        Permission.id == uuid.UUID(child_id),
        Permission.is_active == True
    ).first()
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Child permission not found"
        )

    try:
        if parent.add_child(child):
            db.commit()
            return {"message": "Child permission added successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Child permission already exists"
            )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/{permission_id}/children/{child_id}")
async def remove_child_permission(
    permission_id: str,
    child_id: str,
    current_user: User = Depends(check_admin_permission),
    db: Session = Depends(get_db)
):
    """Remove a child permission"""
    parent = db.query(Permission).filter(
        Permission.id == uuid.UUID(permission_id),
        Permission.is_active == True
    ).first()
    if not parent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent permission not found"
        )

    try:
        if parent.remove_child(child_id):
            db.commit()
            return {"message": "Child permission removed successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Child permission not found"
            )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{permission_id}/children")
async def list_child_permissions(
    permission_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List child permissions"""
    permission = db.query(Permission).filter(
        Permission.id == uuid.UUID(permission_id),
        Permission.is_active == True
    ).first()
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found"
        )
    return permission.children

@router.get("/{permission_id}/parents")
async def list_parent_permissions(
    permission_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List parent permissions"""
    permission = db.query(Permission).filter(
        Permission.id == uuid.UUID(permission_id),
        Permission.is_active == True
    ).first()
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found"
        )
    return permission.get_all_parents()

@router.get("/{permission_id}/users")
async def list_users_with_permission(
    permission_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List users with the permission"""
    permission = db.query(Permission).filter(
        Permission.id == uuid.UUID(permission_id),
        Permission.is_active == True
    ).first()
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found"
        )
    return permission.users 