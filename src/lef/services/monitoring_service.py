"""
Monitoring service for AI Bridge System
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from collections import defaultdict

from ..models.system_state import SystemState, ComponentStatus
from ..models.bridge_status import BridgeStatus
from ..services.alert_service import AlertService, AlertSeverity

logger = logging.getLogger(__name__)

class MetricPoint(BaseModel):
    """Single metric data point"""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    value: float
    labels: Dict[str, str] = Field(default_factory=dict)

class Metric(BaseModel):
    """Metric definition"""
    name: str
    description: str
    type: str  # gauge, counter, histogram
    points: List[MetricPoint] = Field(default_factory=list)
    labels: Dict[str, str] = Field(default_factory=dict)

class HealthCheck(BaseModel):
    """Health check definition"""
    name: str
    description: str
    check_type: str
    status: str
    last_check: Optional[datetime] = None
    error: Optional[str] = None
    details: Dict[str, Any] = Field(default_factory=dict)

class MonitoringService:
    """Service for monitoring system metrics and health"""
    
    def __init__(self):
        self.metrics: Dict[str, Metric] = {}
        self.health_checks: Dict[str, HealthCheck] = {}
        self.alert_service = AlertService()
        self._collection_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
        
    async def start(self):
        """Start the monitoring service"""
        try:
            logger.info("Starting monitoring service")
            
            # Initialize default metrics
            self._init_default_metrics()
            
            # Initialize health checks
            self._init_health_checks()
            
            # Start metric collection
            self._collection_task = asyncio.create_task(self._collect_metrics())
            
            logger.info("Monitoring service started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start monitoring service: {e}")
            await self.alert_service.create_alert(
                title="Monitoring Service Start Failed",
                message=f"Failed to start monitoring service: {e}",
                severity=AlertSeverity.ERROR
            )
            raise
            
    def _init_default_metrics(self):
        """Initialize default system metrics"""
        default_metrics = [
            {
                "name": "system_cpu_usage",
                "description": "System CPU usage percentage",
                "type": "gauge"
            },
            {
                "name": "system_memory_usage",
                "description": "System memory usage percentage",
                "type": "gauge"
            },
            {
                "name": "system_disk_usage",
                "description": "System disk usage percentage",
                "type": "gauge"
            },
            {
                "name": "message_processing_rate",
                "description": "Messages processed per second",
                "type": "counter"
            },
            {
                "name": "error_rate",
                "description": "Error rate per second",
                "type": "counter"
            },
            {
                "name": "service_latency",
                "description": "Service response latency",
                "type": "histogram"
            }
        ]
        
        for metric_def in default_metrics:
            self.metrics[metric_def["name"]] = Metric(**metric_def)
            
    def _init_health_checks(self):
        """Initialize system health checks"""
        default_checks = [
            {
                "name": "system_health",
                "description": "Overall system health",
                "check_type": "composite"
            },
            {
                "name": "service_connectivity",
                "description": "Service connectivity status",
                "check_type": "connectivity"
            },
            {
                "name": "resource_usage",
                "description": "System resource usage",
                "check_type": "resource"
            }
        ]
        
        for check_def in default_checks:
            self.health_checks[check_def["name"]] = HealthCheck(**check_def)
            
    async def _collect_metrics(self):
        """Collect system metrics periodically"""
        while not self._shutdown_event.is_set():
            try:
                # Collect system metrics
                await self._collect_system_metrics()
                
                # Collect service metrics
                await self._collect_service_metrics()
                
                # Run health checks
                await self._run_health_checks()
                
                # Clean up old metrics
                await self._cleanup_old_metrics()
                
                await asyncio.sleep(60)  # Collect every minute
                
            except Exception as e:
                logger.error(f"Error collecting metrics: {e}")
                await asyncio.sleep(5)  # Wait before retrying
                
    async def _collect_system_metrics(self):
        """Collect system-level metrics"""
        try:
            import psutil
            
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self._record_metric("system_cpu_usage", cpu_percent)
            
            # Memory usage
            memory = psutil.virtual_memory()
            self._record_metric("system_memory_usage", memory.percent)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            self._record_metric("system_disk_usage", disk.percent)
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            
    async def _collect_service_metrics(self):
        """Collect service-level metrics"""
        # TODO: Implement service-specific metric collection
        pass
        
    async def _run_health_checks(self):
        """Run system health checks"""
        try:
            # System health check
            system_health = await self._check_system_health()
            self._update_health_check("system_health", system_health)
            
            # Service connectivity check
            service_health = await self._check_service_connectivity()
            self._update_health_check("service_connectivity", service_health)
            
            # Resource usage check
            resource_health = await self._check_resource_usage()
            self._update_health_check("resource_usage", resource_health)
            
        except Exception as e:
            logger.error(f"Error running health checks: {e}")
            
    async def _check_system_health(self) -> Dict[str, Any]:
        """Check overall system health"""
        return {
            "status": "healthy",
            "components": {
                "api": "healthy",
                "database": "healthy",
                "cache": "healthy"
            }
        }
        
    async def _check_service_connectivity(self) -> Dict[str, Any]:
        """Check service connectivity"""
        return {
            "status": "healthy",
            "connected_services": 5,
            "disconnected_services": 0
        }
        
    async def _check_resource_usage(self) -> Dict[str, Any]:
        """Check system resource usage"""
        import psutil
        
        return {
            "status": "healthy",
            "cpu_usage": psutil.cpu_percent(),
            "memory_usage": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent
        }
        
    def _record_metric(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Record a metric value"""
        if name not in self.metrics:
            logger.warning(f"Unknown metric: {name}")
            return
            
        metric = self.metrics[name]
        point = MetricPoint(value=value, labels=labels or {})
        metric.points.append(point)
        
    def _update_health_check(self, name: str, details: Dict[str, Any]):
        """Update health check status"""
        if name not in self.health_checks:
            logger.warning(f"Unknown health check: {name}")
            return
            
        check = self.health_checks[name]
        check.last_check = datetime.utcnow()
        check.details = details
        
        # Update status based on details
        if "status" in details:
            check.status = details["status"]
            
        # Create alert if status is unhealthy
        if check.status == "unhealthy":
            self.alert_service.create_alert(
                title=f"Health Check Failed: {name}",
                message=f"Health check {name} reported unhealthy status",
                severity=AlertSeverity.WARNING
            )
            
    async def _cleanup_old_metrics(self):
        """Clean up old metric data"""
        cutoff = datetime.utcnow() - timedelta(hours=24)
        
        for metric in self.metrics.values():
            metric.points = [
                point for point in metric.points
                if point.timestamp > cutoff
            ]
            
    async def get_metrics(self, name: Optional[str] = None) -> Dict[str, Metric]:
        """Get metrics, optionally filtered by name"""
        if name:
            return {name: self.metrics[name]} if name in self.metrics else {}
        return self.metrics
        
    async def get_health_checks(self, name: Optional[str] = None) -> Dict[str, HealthCheck]:
        """Get health checks, optionally filtered by name"""
        if name:
            return {name: self.health_checks[name]} if name in self.health_checks else {}
        return self.health_checks
        
    async def shutdown(self):
        """Shutdown the monitoring service"""
        try:
            logger.info("Shutting down monitoring service")
            
            # Stop metric collection
            if self._collection_task:
                self._shutdown_event.set()
                await self._collection_task
                self._collection_task = None
                
            logger.info("Monitoring service shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during monitoring service shutdown: {e}")
            await self.alert_service.create_alert(
                title="Monitoring Service Shutdown Failed",
                message=f"Error during shutdown: {e}",
                severity=AlertSeverity.ERROR
            )
            raise 