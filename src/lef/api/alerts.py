"""
Alert API endpoints
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, List, Optional
from datetime import timedelta
from ..services.alert_service import AlertService
from ..models.alert import Alert, AlertSeverity, AlertStatus

router = APIRouter(
    prefix="/api/alerts",
    tags=["alerts"]
)

alert_service = AlertService()

@router.get("/")
async def get_alerts(
    severity: Optional[AlertSeverity] = None,
    category: Optional[str] = None,
    status: Optional[AlertStatus] = None,
    active_only: bool = False
) -> List[Alert]:
    """Get alerts with optional filtering"""
    try:
        alerts = alert_service.alerts
        
        if active_only:
            alerts = alert_service.get_active_alerts()
        if severity:
            alerts = alert_service.get_alerts_by_severity(severity)
        if category:
            alerts = alert_service.get_alerts_by_category(category)
        if status:
            alerts = [a for a in alerts if a.status == status]
            
        return alerts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{alert_id}")
async def get_alert(alert_id: int) -> Alert:
    """Get a specific alert by ID"""
    try:
        alert = next((a for a in alert_service.alerts if a.id == alert_id), None)
        if not alert:
            raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")
        return alert
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: int, user: str) -> Alert:
    """Acknowledge an alert"""
    try:
        alert = alert_service.acknowledge_alert(alert_id, user)
        if not alert:
            raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")
        return alert
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{alert_id}/resolve")
async def resolve_alert(alert_id: int, notes: Optional[str] = None) -> Alert:
    """Resolve an alert"""
    try:
        alert = alert_service.resolve_alert(alert_id, notes)
        if not alert:
            raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")
        return alert
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{alert_id}/suppress")
async def suppress_alert(
    alert_id: int,
    duration_minutes: int,
    reason: str
) -> Alert:
    """Suppress an alert for a specified duration"""
    try:
        alert = alert_service.suppress_alert(
            alert_id,
            timedelta(minutes=duration_minutes),
            reason
        )
        if not alert:
            raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")
        return alert
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{alert_id}/escalate")
async def escalate_alert(alert_id: int) -> Alert:
    """Escalate an alert to the next level"""
    try:
        alert = alert_service.escalate_alert(alert_id)
        if not alert:
            raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")
        return alert
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_alert_stats() -> Dict:
    """Get alert statistics"""
    try:
        alerts = alert_service.alerts
        return {
            "total_alerts": len(alerts),
            "active_alerts": len(alert_service.get_active_alerts()),
            "by_severity": {
                severity.value: len(alert_service.get_alerts_by_severity(severity))
                for severity in AlertSeverity
            },
            "by_status": {
                status.value: len([a for a in alerts if a.status == status])
                for status in AlertStatus
            },
            "by_category": {
                category: len(alert_service.get_alerts_by_category(category))
                for category in set(a.category for a in alerts)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 