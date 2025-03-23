"""
API endpoints for configuration management
"""

import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from ..services.config_service import ConfigService, ConfigValue, ServiceConfig
from ..auth.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/config", tags=["config"])

# Initialize config service
config_service = ConfigService()

class ConfigUpdateRequest(BaseModel):
    """Request model for configuration updates"""
    value: Any
    description: Optional[str] = None
    validation_rules: Optional[Dict[str, Any]] = None

class ServiceConfigUpdateRequest(BaseModel):
    """Request model for service configuration updates"""
    config: Dict[str, Any]
    version: str
    environment: str

@router.get("/system")
async def get_system_config(key: Optional[str] = None, current_user: str = Depends(get_current_user)):
    """Get system configuration, optionally filtered by key"""
    try:
        return await config_service.get_system_config(key)
    except Exception as e:
        logger.error(f"Failed to get system config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/system/{key}")
async def update_system_config(
    key: str,
    request: ConfigUpdateRequest,
    current_user: str = Depends(get_current_user)
):
    """Update system configuration value"""
    try:
        await config_service.update_system_config(key, request.value, current_user)
        return {"status": "updated"}
    except ValueError as e:
        logger.error(f"Config key not found: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to update system config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/services")
async def list_service_configs(current_user: str = Depends(get_current_user)):
    """List all service configurations"""
    try:
        return {
            service_id: {
                "config": service_config.config,
                "version": service_config.version,
                "environment": service_config.environment,
                "last_updated": service_config.last_updated.isoformat(),
                "updated_by": service_config.updated_by
            }
            for service_id, service_config in config_service.service_configs.items()
        }
    except Exception as e:
        logger.error(f"Failed to list service configs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/services/{service_id}")
async def get_service_config(service_id: str, current_user: str = Depends(get_current_user)):
    """Get service configuration"""
    try:
        config = await config_service.get_service_config(service_id)
        if not config:
            raise HTTPException(status_code=404, detail=f"Service config {service_id} not found")
            
        return {
            "config": config.config,
            "version": config.version,
            "environment": config.environment,
            "last_updated": config.last_updated.isoformat(),
            "updated_by": config.updated_by
        }
    except Exception as e:
        logger.error(f"Failed to get service config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/services/{service_id}")
async def update_service_config(
    service_id: str,
    request: ServiceConfigUpdateRequest,
    current_user: str = Depends(get_current_user)
):
    """Update service configuration"""
    try:
        await config_service.update_service_config(
            service_id,
            request.config,
            request.version,
            request.environment,
            current_user
        )
        return {"status": "updated"}
    except Exception as e:
        logger.error(f"Failed to update service config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/services/{service_id}")
async def delete_service_config(service_id: str, current_user: str = Depends(get_current_user)):
    """Delete service configuration"""
    try:
        await config_service.delete_service_config(service_id)
        return {"status": "deleted"}
    except ValueError as e:
        logger.error(f"Service config not found: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to delete service config: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 