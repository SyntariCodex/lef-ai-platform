"""
Project Template Service for managing project templates and their lifecycle
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field
from ..services.logging_service import LoggingService
from ..services.encryption_service import EncryptionService

logger = logging.getLogger(__name__)

class ProjectTemplate(BaseModel):
    """Project template configuration"""
    id: str
    name: str
    description: str
    version: str
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "draft"
    metadata: Dict[str, Any] = Field(default_factory=dict)
    structure: Dict[str, Any] = Field(default_factory=dict)
    validation_rules: Dict[str, Any] = Field(default_factory=dict)
    dependencies: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    is_public: bool = False
    access_control: Dict[str, List[str]] = Field(default_factory=dict)

class ProjectTemplateService:
    """Service for managing project templates"""
    
    def __init__(self):
        self.logging_service = LoggingService()
        self.encryption_service = EncryptionService()
        self.templates: Dict[str, ProjectTemplate] = {}
        self.template_versions: Dict[str, List[ProjectTemplate]] = {}
        
    async def initialize(self):
        """Initialize the project template service"""
        try:
            await self.logging_service.initialize()
            await self.encryption_service.initialize()
            logger.info("Project Template Service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Project Template Service: {e}")
            await self.logging_service.log_message(
                "error",
                f"Failed to initialize Project Template Service: {e}"
            )
            raise
            
    async def create_template(self, template: ProjectTemplate) -> bool:
        """Create a new project template"""
        try:
            if template.id in self.templates:
                raise ValueError(f"Template {template.id} already exists")
                
            # Validate template structure
            if not await self._validate_template_structure(template):
                raise ValueError("Invalid template structure")
                
            # Store template
            self.templates[template.id] = template
            self.template_versions[template.id] = [template]
            
            await self.logging_service.log_message(
                "info",
                f"Created new project template: {template.id}",
                details={
                    "name": template.name,
                    "version": template.version,
                    "created_by": template.created_by
                }
            )
            return True
            
        except Exception as e:
            logger.error(f"Failed to create template {template.id}: {e}")
            await self.logging_service.log_message(
                "error",
                f"Failed to create template {template.id}: {e}"
            )
            return False
            
    async def update_template(self, template_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing project template"""
        try:
            if template_id not in self.templates:
                raise ValueError(f"Template {template_id} not found")
                
            template = self.templates[template_id]
            
            # Create new version
            new_version = template.copy()
            new_version.dict().update(updates)
            new_version.updated_at = datetime.utcnow()
            new_version.version = f"{template.version}.{len(self.template_versions[template_id]) + 1}"
            
            # Validate updated template
            if not await self._validate_template_structure(new_version):
                raise ValueError("Invalid template structure")
                
            # Store new version
            self.templates[template_id] = new_version
            self.template_versions[template_id].append(new_version)
            
            await self.logging_service.log_message(
                "info",
                f"Updated project template: {template_id}",
                details={
                    "version": new_version.version,
                    "updated_by": updates.get("updated_by", "system")
                }
            )
            return True
            
        except Exception as e:
            logger.error(f"Failed to update template {template_id}: {e}")
            await self.logging_service.log_message(
                "error",
                f"Failed to update template {template_id}: {e}"
            )
            return False
            
    async def get_template(self, template_id: str, version: Optional[str] = None) -> Optional[ProjectTemplate]:
        """Get a project template by ID and optional version"""
        try:
            if template_id not in self.templates:
                raise ValueError(f"Template {template_id} not found")
                
            if version:
                # Find specific version
                for template in self.template_versions[template_id]:
                    if template.version == version:
                        return template
                raise ValueError(f"Version {version} not found for template {template_id}")
                
            return self.templates[template_id]
            
        except Exception as e:
            logger.error(f"Failed to get template {template_id}: {e}")
            await self.logging_service.log_message(
                "error",
                f"Failed to get template {template_id}: {e}"
            )
            return None
            
    async def list_templates(
        self,
        user_id: str,
        include_public: bool = True,
        tags: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """List available project templates"""
        try:
            templates = []
            for template in self.templates.values():
                # Check access
                if not template.is_public and user_id not in template.access_control.get("view", []):
                    continue
                    
                # Filter by tags if specified
                if tags and not all(tag in template.tags for tag in tags):
                    continue
                    
                templates.append({
                    "id": template.id,
                    "name": template.name,
                    "description": template.description,
                    "version": template.version,
                    "status": template.status,
                    "tags": template.tags,
                    "is_public": template.is_public
                })
                
            return templates
            
        except Exception as e:
            logger.error(f"Failed to list templates: {e}")
            await self.logging_service.log_message(
                "error",
                f"Failed to list templates: {e}"
            )
            return []
            
    async def delete_template(self, template_id: str, user_id: str) -> bool:
        """Delete a project template"""
        try:
            if template_id not in self.templates:
                raise ValueError(f"Template {template_id} not found")
                
            template = self.templates[template_id]
            
            # Check permissions
            if user_id not in template.access_control.get("delete", []):
                raise ValueError("Not authorized to delete template")
                
            # Remove template and versions
            del self.templates[template_id]
            del self.template_versions[template_id]
            
            await self.logging_service.log_message(
                "info",
                f"Deleted project template: {template_id}",
                details={"deleted_by": user_id}
            )
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete template {template_id}: {e}")
            await self.logging_service.log_message(
                "error",
                f"Failed to delete template {template_id}: {e}"
            )
            return False
            
    async def share_template(self, template_id: str, user_id: str, target_user: str, permissions: List[str]) -> bool:
        """Share a project template with another user"""
        try:
            if template_id not in self.templates:
                raise ValueError(f"Template {template_id} not found")
                
            template = self.templates[template_id]
            
            # Check permissions
            if user_id not in template.access_control.get("share", []):
                raise ValueError("Not authorized to share template")
                
            # Update access control
            for permission in permissions:
                if permission not in template.access_control:
                    template.access_control[permission] = []
                if target_user not in template.access_control[permission]:
                    template.access_control[permission].append(target_user)
                    
            await self.logging_service.log_message(
                "info",
                f"Shared project template: {template_id}",
                details={
                    "shared_by": user_id,
                    "shared_with": target_user,
                    "permissions": permissions
                }
            )
            return True
            
        except Exception as e:
            logger.error(f"Failed to share template {template_id}: {e}")
            await self.logging_service.log_message(
                "error",
                f"Failed to share template {template_id}: {e}"
            )
            return False
            
    async def _validate_template_structure(self, template: ProjectTemplate) -> bool:
        """Validate template structure"""
        try:
            # Check required fields
            required_fields = ["name", "description", "version", "created_by"]
            if not all(field in template.dict() for field in required_fields):
                return False
                
            # Validate structure format
            if not isinstance(template.structure, dict):
                return False
                
            # Validate validation rules
            if not isinstance(template.validation_rules, dict):
                return False
                
            # Validate dependencies
            if not isinstance(template.dependencies, list):
                return False
                
            # Validate tags
            if not isinstance(template.tags, list):
                return False
                
            # Validate access control
            if not isinstance(template.access_control, dict):
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Template validation failed: {e}")
            await self.logging_service.log_message(
                "error",
                f"Template validation failed: {e}"
            )
            return False 