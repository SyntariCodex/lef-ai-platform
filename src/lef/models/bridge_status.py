"""
Bridge status models for AI Bridge System
"""

from enum import Enum
from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class BridgeStatus(str, Enum):
    """Status of the AI Bridge"""
    INITIALIZING = "initializing"
    ACTIVE = "active"
    DEGRADED = "degraded"
    ERROR = "error"
    SHUTDOWN = "shutdown"

class ServiceStatus(str, Enum):
    """Status of individual services"""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    DEGRADED = "degraded"

class ServiceMetrics(BaseModel):
    """Metrics for a service connection"""
    messages_sent: int = Field(default=0, description="Number of messages sent")
    messages_received: int = Field(default=0, description="Number of messages received")
    errors: int = Field(default=0, description="Number of errors")
    last_message: Optional[datetime] = Field(None, description="Timestamp of last message")
    latency: float = Field(default=0.0, description="Average message latency")
    uptime: float = Field(default=0.0, description="Service uptime percentage")

class ServiceConnection(BaseModel):
    """Information about a service connection"""
    service_id: str = Field(..., description="Unique service identifier")
    status: ServiceStatus = Field(ServiceStatus.DISCONNECTED, description="Current connection status")
    connected_at: Optional[datetime] = Field(None, description="When the connection was established")
    last_heartbeat: Optional[datetime] = Field(None, description="Last received heartbeat")
    metrics: ServiceMetrics = Field(default_factory=ServiceMetrics, description="Connection metrics")
    error: Optional[str] = Field(None, description="Last error message")
    config: Dict[str, Any] = Field(default_factory=dict, description="Service configuration")

class BridgeState(BaseModel):
    """Complete state of the AI Bridge"""
    bridge_id: str = Field(..., description="Unique bridge identifier")
    status: BridgeStatus = Field(BridgeStatus.INITIALIZING, description="Current bridge status")
    started_at: datetime = Field(default_factory=datetime.utcnow, description="When the bridge started")
    last_heartbeat: Optional[datetime] = Field(None, description="Last bridge heartbeat")
    services: Dict[str, ServiceConnection] = Field(default_factory=dict, description="Connected services")
    metrics: Dict[str, Any] = Field(default_factory=dict, description="Bridge-wide metrics")
    error: Optional[str] = Field(None, description="Last bridge error")
    config: Dict[str, Any] = Field(default_factory=dict, description="Bridge configuration") 