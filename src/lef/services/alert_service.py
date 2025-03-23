"""
Alert service for AI Bridge System
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from pydantic import BaseModel, Field
from enum import Enum
import uuid

logger = logging.getLogger(__name__)

class AlertSeverity(str, Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AlertStatus(str, Enum):
    """Alert status"""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"

class Alert(BaseModel):
    """Alert model"""
    id: str = Field(..., description="Unique alert ID")
    title: str = Field(..., description="Alert title")
    message: str = Field(..., description="Alert message")
    severity: AlertSeverity = Field(..., description="Alert severity")
    status: AlertStatus = Field(AlertStatus.ACTIVE, description="Alert status")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="When the alert was created")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="When the alert was last updated")
    acknowledged_at: Optional[datetime] = Field(None, description="When the alert was acknowledged")
    resolved_at: Optional[datetime] = Field(None, description="When the alert was resolved")
    source: Optional[str] = Field(None, description="Source of the alert")
    category: Optional[str] = Field(None, description="Alert category")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional alert metadata")
    affected_components: List[str] = Field(default_factory=list, description="Components affected by the alert")
    resolution_notes: Optional[str] = Field(None, description="Notes about alert resolution")
    assigned_to: Optional[str] = Field(None, description="Person/team assigned to handle the alert")
    tags: List[str] = Field(default_factory=list, description="Alert tags")
    related_alerts: List[str] = Field(default_factory=list, description="IDs of related alerts")
    escalation_level: int = Field(default=0, description="Current escalation level")
    max_escalation_level: int = Field(default=3, description="Maximum escalation level")
    notification_sent: bool = Field(default=False, description="Whether notification was sent")
    last_notification: Optional[datetime] = Field(None, description="When notification was last sent")
    notification_channels: List[str] = Field(default_factory=list, description="Channels to send notifications to")
    suppression_until: Optional[datetime] = Field(None, description="When to suppress the alert until")
    suppression_reason: Optional[str] = Field(None, description="Reason for suppressing the alert")
    custom_fields: Dict[str, Any] = Field(default_factory=dict, description="Custom alert fields")

class AlertService:
    """Service for managing system alerts"""
    
    def __init__(self):
        self._alerts: Dict[str, Alert] = {}
        self._notification_handlers = {}
        
    async def create_alert(
        self,
        title: str,
        message: str,
        severity: AlertSeverity,
        source: Optional[str] = None,
        category: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        affected_components: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        notification_channels: Optional[List[str]] = None,
        custom_fields: Optional[Dict[str, Any]] = None
    ) -> Alert:
        """Create a new alert"""
        alert = Alert(
            id=str(uuid.uuid4()),
            title=title,
            message=message,
            severity=severity,
            source=source,
            category=category,
            metadata=metadata or {},
            affected_components=affected_components or [],
            tags=tags or [],
            notification_channels=notification_channels or [],
            custom_fields=custom_fields or {}
        )
        
        self._alerts[alert.id] = alert
        logger.info(f"Created alert {alert.id}: {alert.title}")
        
        # Send notification if channels configured
        if alert.notification_channels:
            await self._send_notification(alert)
            
        return alert
        
    async def acknowledge_alert(self, alert_id: str, user: str) -> Optional[Alert]:
        """Acknowledge an alert"""
        alert = self._alerts.get(alert_id)
        if not alert:
            return None
            
        alert.status = AlertStatus.ACKNOWLEDGED
        alert.acknowledged_at = datetime.utcnow()
        alert.updated_at = datetime.utcnow()
        alert.assigned_to = user
        
        logger.info(f"Alert {alert_id} acknowledged by {user}")
        return alert
        
    async def resolve_alert(
        self,
        alert_id: str,
        resolution_notes: Optional[str] = None,
        user: Optional[str] = None
    ) -> Optional[Alert]:
        """Resolve an alert"""
        alert = self._alerts.get(alert_id)
        if not alert:
            return None
            
        alert.status = AlertStatus.RESOLVED
        alert.resolved_at = datetime.utcnow()
        alert.updated_at = datetime.utcnow()
        alert.resolution_notes = resolution_notes
        
        if user:
            alert.assigned_to = user
            
        logger.info(f"Alert {alert_id} resolved by {user or 'system'}")
        return alert
        
    async def suppress_alert(
        self,
        alert_id: str,
        duration: int,
        reason: str,
        user: str
    ) -> Optional[Alert]:
        """Suppress an alert for a specified duration"""
        alert = self._alerts.get(alert_id)
        if not alert:
            return None
            
        alert.status = AlertStatus.SUPPRESSED
        alert.suppression_until = datetime.utcnow() + timedelta(seconds=duration)
        alert.suppression_reason = reason
        alert.updated_at = datetime.utcnow()
        alert.assigned_to = user
        
        logger.info(f"Alert {alert_id} suppressed by {user} until {alert.suppression_until}")
        return alert
        
    async def escalate_alert(self, alert_id: str) -> Optional[Alert]:
        """Escalate an alert to the next level"""
        alert = self._alerts.get(alert_id)
        if not alert:
            return None
            
        if alert.escalation_level >= alert.max_escalation_level:
            logger.warning(f"Alert {alert_id} already at maximum escalation level")
            return alert
            
        alert.escalation_level += 1
        alert.updated_at = datetime.utcnow()
        
        # Send notification for escalation
        if alert.notification_channels:
            await self._send_notification(alert)
            
        logger.info(f"Alert {alert_id} escalated to level {alert.escalation_level}")
        return alert
        
    async def get_active_alerts(
        self,
        severity: Optional[AlertSeverity] = None,
        category: Optional[str] = None,
        source: Optional[str] = None
    ) -> List[Alert]:
        """Get active alerts with optional filtering"""
        alerts = [
            alert for alert in self._alerts.values()
            if alert.status == AlertStatus.ACTIVE
        ]
        
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        if category:
            alerts = [a for a in alerts if a.category == category]
        if source:
            alerts = [a for a in alerts if a.source == source]
            
        return alerts
        
    async def get_alert(self, alert_id: str) -> Optional[Alert]:
        """Get a specific alert by ID"""
        return self._alerts.get(alert_id)
        
    async def _send_notification(self, alert: Alert):
        """Send notification for an alert"""
        try:
            for channel in alert.notification_channels:
                if channel in self._notification_handlers:
                    await self._notification_handlers[channel](alert)
                    
            alert.notification_sent = True
            alert.last_notification = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Failed to send notification for alert {alert.id}: {e}")
            
    def register_notification_handler(self, channel: str, handler: Callable):
        """Register a notification handler for a channel"""
        self._notification_handlers[channel] = handler 