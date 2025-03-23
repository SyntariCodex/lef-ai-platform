"""
API endpoints for project template service
"""

import logging
from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from ..services.project_template_service import ProjectTemplateService, ProjectTemplate
from ..services.logging_service import LoggingService
from ..services.security_service import SecurityService

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize services
project_template_service = ProjectTemplateService()
logging_service = LoggingService()
security_service = SecurityService()

class TemplateCreate(BaseModel):
    """Template creation request"""
    name: str
    description: str
    version: str
    structure: Dict
    validation_rules: Dict
    dependencies: List[str] = []
    tags: List[str] = []
    is_public: bool = False
    access_control: Dict[str, List[str]] = {}

class TemplateUpdate(BaseModel):
    """Template update request"""
    name: Optional[str] = None
    description: Optional[str] = None
    structure: Optional[Dict] = None
    validation_rules: Optional[Dict] = None
    dependencies: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    is_public: Optional[bool] = None
    access_control: Optional[Dict[str, List[str]]] = None
    status: Optional[str] = None

class TemplateShare(BaseModel):
    """Template sharing request"""
    target_user: str
    permissions: List[str]

@router.post("/templates", response_model=Dict)
async def create_template(
    template: TemplateCreate,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Create a new project template"""
    try:
        # Check permissions
        if not await security_service.check_permission(current_user["id"], "create_templates"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to create templates"
            )
            
        # Create template
        project_template = ProjectTemplate(
            id=f"template_{len(project_template_service.templates) + 1}",
            created_by=current_user["id"],
            **template.dict()
        )
        success = await project_template_service.create_template(project_template)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create template"
            )
            
        return {
            "message": "Template created successfully",
            "template_id": project_template.id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create template: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to create template: {e}",
            details={"template_name": template.name}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.put("/templates/{template_id}", response_model=Dict)
async def update_template(
    template_id: str,
    updates: TemplateUpdate,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Update an existing project template"""
    try:
        # Check permissions
        if not await security_service.check_permission(current_user["id"], "update_templates"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update templates"
            )
            
        # Add user to updates
        updates_dict = updates.dict(exclude_unset=True)
        updates_dict["updated_by"] = current_user["id"]
        
        success = await project_template_service.update_template(template_id, updates_dict)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update template"
            )
            
        return {
            "message": "Template updated successfully",
            "template_id": template_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update template: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to update template: {e}",
            details={"template_id": template_id}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/templates/{template_id}", response_model=Dict)
async def get_template(
    template_id: str,
    version: Optional[str] = None,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Get a project template by ID"""
    try:
        # Check permissions
        if not await security_service.check_permission(current_user["id"], "view_templates"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view templates"
            )
            
        template = await project_template_service.get_template(template_id, version)
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
            
        return template.dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get template: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to get template: {e}",
            details={"template_id": template_id}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/templates", response_model=List[Dict])
async def list_templates(
    include_public: bool = True,
    tags: Optional[List[str]] = None,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """List available project templates"""
    try:
        # Check permissions
        if not await security_service.check_permission(current_user["id"], "view_templates"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view templates"
            )
            
        templates = await project_template_service.list_templates(
            current_user["id"],
            include_public,
            tags
        )
        
        return templates
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list templates: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to list templates: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.delete("/templates/{template_id}", response_model=Dict)
async def delete_template(
    template_id: str,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Delete a project template"""
    try:
        # Check permissions
        if not await security_service.check_permission(current_user["id"], "delete_templates"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete templates"
            )
            
        success = await project_template_service.delete_template(template_id, current_user["id"])
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to delete template"
            )
            
        return {
            "message": "Template deleted successfully",
            "template_id": template_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete template: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to delete template: {e}",
            details={"template_id": template_id}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/templates/{template_id}/share", response_model=Dict)
async def share_template(
    template_id: str,
    share_request: TemplateShare,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Share a project template with another user"""
    try:
        # Check permissions
        if not await security_service.check_permission(current_user["id"], "share_templates"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to share templates"
            )
            
        success = await project_template_service.share_template(
            template_id,
            current_user["id"],
            share_request.target_user,
            share_request.permissions
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to share template"
            )
            
        return {
            "message": "Template shared successfully",
            "template_id": template_id,
            "shared_with": share_request.target_user
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to share template: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to share template: {e}",
            details={
                "template_id": template_id,
                "target_user": share_request.target_user
            }
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) 