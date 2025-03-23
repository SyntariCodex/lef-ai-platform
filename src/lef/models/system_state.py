"""
System state models for AI Bridge System
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

class SystemStatus(str, Enum):
    """Overall system status"""
    ACTIVE = "active"
    DEGRADED = "degraded"
    ERROR = "error"
    MAINTENANCE = "maintenance"
    SHUTDOWN = "shutdown"

class ComponentStatus(str, Enum):
    """Status of system components"""
    ACTIVE = "active"
    DEGRADED = "degraded"
    ERROR = "error"
    DISABLED = "disabled"
    MAINTENANCE = "maintenance"

class ResourceMetrics(BaseModel):
    """Resource usage metrics"""
    cpu_usage: float = Field(default=0.0, description="CPU usage percentage")
    memory_usage: float = Field(default=0.0, description="Memory usage percentage")
    disk_usage: float = Field(default=0.0, description="Disk usage percentage")
    network_io: Dict[str, float] = Field(
        default_factory=lambda: {"in": 0.0, "out": 0.0},
        description="Network I/O in bytes per second"
    )
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When metrics were collected")

class ComponentMetrics(BaseModel):
    """Component-specific metrics"""
    requests_processed: int = Field(default=0, description="Number of requests processed")
    errors: int = Field(default=0, description="Number of errors")
    latency: float = Field(default=0.0, description="Average request latency")
    queue_size: int = Field(default=0, description="Current queue size")
    active_connections: int = Field(default=0, description="Number of active connections")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When metrics were collected")

class Component(BaseModel):
    """System component information"""
    id: str = Field(..., description="Unique component identifier")
    name: str = Field(..., description="Component name")
    type: str = Field(..., description="Component type")
    status: ComponentStatus = Field(ComponentStatus.ACTIVE, description="Current component status")
    started_at: datetime = Field(default_factory=datetime.utcnow, description="When component started")
    last_heartbeat: Optional[datetime] = Field(None, description="Last received heartbeat")
    metrics: ComponentMetrics = Field(default_factory=ComponentMetrics, description="Component metrics")
    error: Optional[str] = Field(None, description="Last error message")
    config: Dict[str, Any] = Field(default_factory=dict, description="Component configuration")
    dependencies: List[str] = Field(default_factory=list, description="Component dependencies")
    health_checks: List[Dict[str, Any]] = Field(default_factory=list, description="Health check results")

class SystemState(BaseModel):
    """Complete system state"""
    system_id: str = Field(..., description="Unique system identifier")
    status: SystemStatus = Field(SystemStatus.ACTIVE, description="Current system status")
    started_at: datetime = Field(default_factory=datetime.utcnow, description="When system started")
    last_heartbeat: Optional[datetime] = Field(None, description="Last system heartbeat")
    components: Dict[str, Component] = Field(default_factory=dict, description="System components")
    resources: ResourceMetrics = Field(default_factory=ResourceMetrics, description="System resources")
    metrics: Dict[str, Any] = Field(default_factory=dict, description="System-wide metrics")
    error: Optional[str] = Field(None, description="Last system error")
    config: Dict[str, Any] = Field(default_factory=dict, description="System configuration")
    version: str = Field(..., description="System version")
    environment: str = Field(..., description="System environment (dev/staging/prod)")
    maintenance_mode: bool = Field(default=False, description="Whether system is in maintenance mode")
    last_backup: Optional[datetime] = Field(None, description="Last successful backup")
    security_status: Dict[str, Any] = Field(default_factory=dict, description="Security-related status")
    compliance_status: Dict[str, Any] = Field(default_factory=dict, description="Compliance status")
    custom_fields: Dict[str, Any] = Field(default_factory=dict, description="Custom system fields")
