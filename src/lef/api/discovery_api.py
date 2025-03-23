"""
API endpoints for service discovery and registration
"""

import logging
from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..services.discovery_service import DiscoveryService, ServiceRegistration, ServiceInfo

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/discovery", tags=["discovery"])

# Initialize discovery service
discovery_service = DiscoveryService()

class ServiceResponse(BaseModel):
    """Response model for service information"""
    service_id: str
    name: str
    type: str
    version: str
    host: str
    port: int
    status: str
    capabilities: List[str]
    metadata: Dict[str, str]
    last_heartbeat: str
    registration_time: str
    health_status: Dict[str, any]

@router.post("/register")
async def register_service(registration: ServiceRegistration):
    """Register a new service"""
    try:
        service_id = await discovery_service.register_service(registration)
        return {"service_id": service_id, "status": "registered"}
    except Exception as e:
        logger.error(f"Failed to register service: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/services/{service_id}")
async def deregister_service(service_id: str):
    """Deregister a service"""
    try:
        await discovery_service.deregister_service(service_id)
        return {"status": "deregistered"}
    except ValueError as e:
        logger.error(f"Service not found: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to deregister service: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/services/{service_id}/heartbeat")
async def update_heartbeat(service_id: str):
    """Update service heartbeat"""
    try:
        await discovery_service.update_service_heartbeat(service_id)
        return {"status": "heartbeat_updated"}
    except ValueError as e:
        logger.error(f"Service not found: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to update heartbeat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/services")
async def list_services(service_type: Optional[str] = None):
    """List all registered services, optionally filtered by type"""
    try:
        if service_type:
            services = await discovery_service.get_services_by_type(service_type)
        else:
            services = await discovery_service.get_all_services()
            
        return {
            service.service_id: ServiceResponse(
                service_id=service.service_id,
                name=service.name,
                type=service.type,
                version=service.version,
                host=service.host,
                port=service.port,
                status=service.status,
                capabilities=service.capabilities,
                metadata=service.metadata,
                last_heartbeat=service.last_heartbeat.isoformat(),
                registration_time=service.registration_time.isoformat(),
                health_status=service.health_status
            )
            for service in services
        }
    except Exception as e:
        logger.error(f"Failed to list services: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/services/{service_id}")
async def get_service(service_id: str):
    """Get information about a specific service"""
    try:
        service = await discovery_service.get_service(service_id)
        if not service:
            raise HTTPException(status_code=404, detail=f"Service {service_id} not found")
            
        return ServiceResponse(
            service_id=service.service_id,
            name=service.name,
            type=service.type,
            version=service.version,
            host=service.host,
            port=service.port,
            status=service.status,
            capabilities=service.capabilities,
            metadata=service.metadata,
            last_heartbeat=service.last_heartbeat.isoformat(),
            registration_time=service.registration_time.isoformat(),
            health_status=service.health_status
        )
    except Exception as e:
        logger.error(f"Failed to get service {service_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/types")
async def list_service_types():
    """List all registered service types"""
    try:
        services = await discovery_service.get_all_services()
        service_types = {service.type for service in services}
        return {"service_types": list(service_types)}
    except Exception as e:
        logger.error(f"Failed to list service types: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 