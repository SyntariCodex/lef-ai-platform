"""
API endpoints for monitoring system metrics and health
"""

import logging
from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..services.monitoring_service import MonitoringService, Metric, HealthCheck

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/monitoring", tags=["monitoring"])

# Initialize monitoring service
monitoring_service = MonitoringService()

class MetricResponse(BaseModel):
    """Response model for metrics"""
    name: str
    description: str
    type: str
    points: List[Dict[str, any]]
    labels: Dict[str, str]

class HealthCheckResponse(BaseModel):
    """Response model for health checks"""
    name: str
    description: str
    check_type: str
    status: str
    last_check: Optional[str]
    error: Optional[str]
    details: Dict[str, any]

@router.get("/metrics")
async def get_metrics(name: Optional[str] = None):
    """Get system metrics, optionally filtered by name"""
    try:
        metrics = await monitoring_service.get_metrics(name)
        return {
            metric_name: MetricResponse(
                name=metric.name,
                description=metric.description,
                type=metric.type,
                points=[point.dict() for point in metric.points],
                labels=metric.labels
            )
            for metric_name, metric in metrics.items()
        }
    except Exception as e:
        logger.error(f"Failed to get metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics/{metric_name}")
async def get_metric(metric_name: str):
    """Get a specific metric by name"""
    try:
        metrics = await monitoring_service.get_metrics(metric_name)
        if not metrics:
            raise HTTPException(status_code=404, detail=f"Metric {metric_name} not found")
        metric = metrics[metric_name]
        return MetricResponse(
            name=metric.name,
            description=metric.description,
            type=metric.type,
            points=[point.dict() for point in metric.points],
            labels=metric.labels
        )
    except Exception as e:
        logger.error(f"Failed to get metric {metric_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def get_health(name: Optional[str] = None):
    """Get system health checks, optionally filtered by name"""
    try:
        checks = await monitoring_service.get_health_checks(name)
        return {
            check_name: HealthCheckResponse(
                name=check.name,
                description=check.description,
                check_type=check.check_type,
                status=check.status,
                last_check=check.last_check.isoformat() if check.last_check else None,
                error=check.error,
                details=check.details
            )
            for check_name, check in checks.items()
        }
    except Exception as e:
        logger.error(f"Failed to get health checks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health/{check_name}")
async def get_health_check(check_name: str):
    """Get a specific health check by name"""
    try:
        checks = await monitoring_service.get_health_checks(check_name)
        if not checks:
            raise HTTPException(status_code=404, detail=f"Health check {check_name} not found")
        check = checks[check_name]
        return HealthCheckResponse(
            name=check.name,
            description=check.description,
            check_type=check.check_type,
            status=check.status,
            last_check=check.last_check.isoformat() if check.last_check else None,
            error=check.error,
            details=check.details
        )
    except Exception as e:
        logger.error(f"Failed to get health check {check_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_system_status():
    """Get overall system status"""
    try:
        # Get all health checks
        checks = await monitoring_service.get_health_checks()
        
        # Determine overall status
        status = "healthy"
        for check in checks.values():
            if check.status == "unhealthy":
                status = "unhealthy"
                break
            elif check.status == "degraded" and status == "healthy":
                status = "degraded"
                
        return {
            "status": status,
            "health_checks": {
                check_name: HealthCheckResponse(
                    name=check.name,
                    description=check.description,
                    check_type=check.check_type,
                    status=check.status,
                    last_check=check.last_check.isoformat() if check.last_check else None,
                    error=check.error,
                    details=check.details
                )
                for check_name, check in checks.items()
            }
        }
    except Exception as e:
        logger.error(f"Failed to get system status: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 