"""
Service discovery service for AI Bridge System
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from pydantic import BaseModel, Field
from uuid import uuid4

from ..models.system_state import SystemState, ComponentStatus
from ..services.alert_service import AlertService, AlertSeverity
from ..services.monitoring_service import MonitoringService

logger = logging.getLogger(__name__)

class ServiceInfo(BaseModel):
    """Information about a discovered service"""
    service_id: str
    name: str
    type: str
    version: str
    host: str
    port: int
    status: str = "active"
    capabilities: List[str] = Field(default_factory=list)
    metadata: Dict[str, str] = Field(default_factory=dict)
    last_heartbeat: datetime = Field(default_factory=datetime.utcnow)
    registration_time: datetime = Field(default_factory=datetime.utcnow)
    health_status: Dict[str, any] = Field(default_factory=dict)

class ServiceRegistration(BaseModel):
    """Service registration request"""
    name: str
    type: str
    version: str
    host: str
    port: int
    capabilities: List[str] = Field(default_factory=list)
    metadata: Dict[str, str] = Field(default_factory=dict)

class DiscoveryService:
    """Service for managing service discovery and registration"""
    
    def __init__(self):
        self.services: Dict[str, ServiceInfo] = {}
        self.service_types: Dict[str, Set[str]] = {}
        self.alert_service = AlertService()
        self.monitoring_service = MonitoringService()
        self._cleanup_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
        
    async def start(self):
        """Start the discovery service"""
        try:
            logger.info("Starting discovery service")
            
            # Start cleanup task
            self._cleanup_task = asyncio.create_task(self._cleanup_stale_services())
            
            logger.info("Discovery service started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start discovery service: {e}")
            await self.alert_service.create_alert(
                title="Discovery Service Start Failed",
                message=f"Failed to start discovery service: {e}",
                severity=AlertSeverity.ERROR
            )
            raise
            
    async def register_service(self, registration: ServiceRegistration) -> str:
        """Register a new service"""
        try:
            service_id = str(uuid4())
            
            service_info = ServiceInfo(
                service_id=service_id,
                name=registration.name,
                type=registration.type,
                version=registration.version,
                host=registration.host,
                port=registration.port,
                capabilities=registration.capabilities,
                metadata=registration.metadata
            )
            
            self.services[service_id] = service_info
            
            # Update service type index
            if registration.type not in self.service_types:
                self.service_types[registration.type] = set()
            self.service_types[registration.type].add(service_id)
            
            logger.info(f"Service registered: {service_id} ({registration.name})")
            
            # Record metric
            await self.monitoring_service._record_metric(
                "service_registrations",
                1,
                {"service_type": registration.type}
            )
            
            return service_id
            
        except Exception as e:
            logger.error(f"Failed to register service: {e}")
            await self.alert_service.create_alert(
                title="Service Registration Failed",
                message=f"Failed to register service: {e}",
                severity=AlertSeverity.ERROR
            )
            raise
            
    async def deregister_service(self, service_id: str):
        """Deregister a service"""
        try:
            if service_id not in self.services:
                raise ValueError(f"Service {service_id} not found")
                
            service = self.services[service_id]
            
            # Remove from service type index
            if service.type in self.service_types:
                self.service_types[service.type].remove(service_id)
                if not self.service_types[service.type]:
                    del self.service_types[service.type]
                    
            del self.services[service_id]
            
            logger.info(f"Service deregistered: {service_id}")
            
            # Record metric
            await self.monitoring_service._record_metric(
                "service_deregistrations",
                1,
                {"service_type": service.type}
            )
            
        except Exception as e:
            logger.error(f"Failed to deregister service: {e}")
            await self.alert_service.create_alert(
                title="Service Deregistration Failed",
                message=f"Failed to deregister service {service_id}: {e}",
                severity=AlertSeverity.ERROR
            )
            raise
            
    async def update_service_heartbeat(self, service_id: str):
        """Update service heartbeat"""
        try:
            if service_id not in self.services:
                raise ValueError(f"Service {service_id} not found")
                
            service = self.services[service_id]
            service.last_heartbeat = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Failed to update service heartbeat: {e}")
            
    async def get_service(self, service_id: str) -> Optional[ServiceInfo]:
        """Get service information by ID"""
        return self.services.get(service_id)
        
    async def get_services_by_type(self, service_type: str) -> List[ServiceInfo]:
        """Get all services of a specific type"""
        service_ids = self.service_types.get(service_type, set())
        return [self.services[service_id] for service_id in service_ids]
        
    async def get_all_services(self) -> List[ServiceInfo]:
        """Get all registered services"""
        return list(self.services.values())
        
    async def _cleanup_stale_services(self):
        """Clean up services that haven't sent heartbeats"""
        while not self._shutdown_event.is_set():
            try:
                now = datetime.utcnow()
                stale_threshold = now - timedelta(minutes=5)
                
                stale_services = [
                    service_id for service_id, service in self.services.items()
                    if service.last_heartbeat < stale_threshold
                ]
                
                for service_id in stale_services:
                    service = self.services[service_id]
                    logger.warning(f"Service {service_id} ({service.name}) is stale")
                    
                    # Update service status
                    service.status = "stale"
                    
                    # Create alert
                    await self.alert_service.create_alert(
                        title="Stale Service Detected",
                        message=f"Service {service.name} ({service_id}) has not sent heartbeat",
                        severity=AlertSeverity.WARNING
                    )
                    
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error cleaning up stale services: {e}")
                await asyncio.sleep(5)
                
    async def shutdown(self):
        """Shutdown the discovery service"""
        try:
            logger.info("Shutting down discovery service")
            
            # Stop cleanup task
            if self._cleanup_task:
                self._shutdown_event.set()
                await self._cleanup_task
                self._cleanup_task = None
                
            logger.info("Discovery service shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during discovery service shutdown: {e}")
            await self.alert_service.create_alert(
                title="Discovery Service Shutdown Failed",
                message=f"Error during shutdown: {e}",
                severity=AlertSeverity.ERROR
            )
            raise 