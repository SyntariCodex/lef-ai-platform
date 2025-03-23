"""
Alert model for system notifications
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Dict, Optional, List
from enum import Enum

class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AlertStatus(Enum):
    NEW = "new"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    IGNORED = "ignored"

class Alert(BaseModel):
    """Alert model for system notifications"""
    id: int = Field(default=1, description="Unique identifier for alert")
    title: str = Field(..., description="Alert title")
    message: str = Field(..., description="Alert message")
    severity: AlertSeverity = Field(..., description="Alert severity level")
    status: AlertStatus = Field(default=AlertStatus.NEW, description="Current alert status")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Alert creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    source: str = Field(..., description="Source of the alert")
    category: str = Field(..., description="Alert category")
    metadata: Dict = Field(default_factory=dict, description="Additional alert metadata")
    affected_components: List[str] = Field(default_factory=list, description="List of affected system components")
    resolution_notes: Optional[str] = None
    assigned_to: Optional[str] = None
    tags: List[str] = Field(default_factory=list, description="Alert tags for categorization")
    related_alerts: List[int] = Field(default_factory=list, description="IDs of related alerts")
    escalation_level: int = Field(default=1, description="Current escalation level")
    max_escalation_level: int = Field(default=3, description="Maximum escalation level")
    notification_sent: bool = Field(default=False, description="Whether notification has been sent")
    last_notification: Optional[datetime] = None
    notification_channels: List[str] = Field(default_factory=list, description="Channels to send notifications to")
    suppression_until: Optional[datetime] = None
    suppression_reason: Optional[str] = None
    custom_fields: Dict = Field(default_factory=dict, description="Custom fields for specific alert types") 