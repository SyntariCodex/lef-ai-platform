"""
API endpoints for performance metrics service
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from ..services.performance_metrics_service import (
    PerformanceMetricsService,
    Metric,
    MetricCollection,
    MetricType,
    MetricCategory
)
from ..services.logging_service import LoggingService
from ..services.security_service import SecurityService

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize services
performance_metrics_service = PerformanceMetricsService()
logging_service = LoggingService()
security_service = SecurityService()

class MetricCreate(BaseModel):
    """Metric creation request"""
    name: str
    description: str
    type: MetricType
    category: MetricCategory
    value: float
    unit: str
    target_value: Optional[float] = None
    threshold_min: Optional[float] = None
    threshold_max: Optional[float] = None
    metadata: Optional[Dict] = None

class MetricUpdate(BaseModel):
    """Metric update request"""
    name: Optional[str] = None
    description: Optional[str] = None
    type: Optional[MetricType] = None
    category: Optional[MetricCategory] = None
    value: Optional[float] = None
    unit: Optional[str] = None
    target_value: Optional[float] = None
    threshold_min: Optional[float] = None
    threshold_max: Optional[float] = None
    metadata: Optional[Dict] = None

class MetricCollectionCreate(BaseModel):
    """Metric collection creation request"""
    name: str
    description: str
    simulation_id: Optional[str] = None
    project_id: Optional[str] = None
    metrics: Optional[List[Metric]] = None
    metadata: Optional[Dict] = None

@router.post("/metrics", response_model=Dict)
async def create_metric(
    metric: MetricCreate,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Create a new metric"""
    try:
        # Check permissions
        if not await security_service.check_permission(current_user["id"], "create_metrics"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to create metrics"
            )
            
        # Create metric
        new_metric = Metric(
            id=f"metric_{len(performance_metrics_service.metrics) + 1}",
            created_by=current_user["id"],
            **metric.dict()
        )
        success = await performance_metrics_service.create_metric(new_metric)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create metric"
            )
            
        return {
            "message": "Metric created successfully",
            "metric_id": new_metric.id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create metric: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to create metric: {e}",
            details={"metric_name": metric.name}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.put("/metrics/{metric_id}", response_model=Dict)
async def update_metric(
    metric_id: str,
    updates: MetricUpdate,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Update an existing metric"""
    try:
        # Check permissions
        if not await security_service.check_permission(current_user["id"], "update_metrics"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update metrics"
            )
            
        # Add user to updates
        updates_dict = updates.dict(exclude_unset=True)
        updates_dict["updated_by"] = current_user["id"]
        
        success = await performance_metrics_service.update_metric(metric_id, updates_dict)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update metric"
            )
            
        return {
            "message": "Metric updated successfully",
            "metric_id": metric_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update metric: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to update metric: {e}",
            details={"metric_id": metric_id}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/metrics/{metric_id}", response_model=Dict)
async def get_metric(
    metric_id: str,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Get a metric by ID"""
    try:
        # Check permissions
        if not await security_service.check_permission(current_user["id"], "view_metrics"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view metrics"
            )
            
        metric = await performance_metrics_service.get_metric(metric_id)
        
        if not metric:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Metric not found"
            )
            
        return metric.dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get metric: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to get metric: {e}",
            details={"metric_id": metric_id}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/metrics", response_model=List[Dict])
async def list_metrics(
    category: Optional[MetricCategory] = None,
    type: Optional[MetricType] = None,
    simulation_id: Optional[str] = None,
    project_id: Optional[str] = None,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """List metrics with optional filters"""
    try:
        # Check permissions
        if not await security_service.check_permission(current_user["id"], "view_metrics"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view metrics"
            )
            
        metrics = await performance_metrics_service.list_metrics(
            category,
            type,
            simulation_id,
            project_id
        )
        
        return metrics
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list metrics: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to list metrics: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/collections", response_model=Dict)
async def create_metric_collection(
    collection: MetricCollectionCreate,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Create a new metric collection"""
    try:
        # Check permissions
        if not await security_service.check_permission(current_user["id"], "create_collections"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to create metric collections"
            )
            
        # Create collection
        collection_id = await performance_metrics_service.create_metric_collection(
            collection.name,
            collection.description,
            current_user["id"],
            collection.simulation_id,
            collection.project_id,
            collection.metrics,
            collection.metadata
        )
        
        if not collection_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create metric collection"
            )
            
        return {
            "message": "Metric collection created successfully",
            "collection_id": collection_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create metric collection: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to create metric collection: {e}",
            details={"collection_name": collection.name}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/collections/{collection_id}", response_model=Dict)
async def get_metric_collection(
    collection_id: str,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Get a metric collection by ID"""
    try:
        # Check permissions
        if not await security_service.check_permission(current_user["id"], "view_collections"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view metric collections"
            )
            
        collection = await performance_metrics_service.get_metric_collection(collection_id)
        
        if not collection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Metric collection not found"
            )
            
        return collection.dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get metric collection: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to get metric collection: {e}",
            details={"collection_id": collection_id}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/collections", response_model=List[Dict])
async def list_metric_collections(
    simulation_id: Optional[str] = None,
    project_id: Optional[str] = None,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """List metric collections with optional filters"""
    try:
        # Check permissions
        if not await security_service.check_permission(current_user["id"], "view_collections"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view metric collections"
            )
            
        collections = await performance_metrics_service.list_metric_collections(
            simulation_id,
            project_id,
            current_user["id"]
        )
        
        return collections
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list metric collections: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to list metric collections: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/metrics/{metric_id}/history", response_model=List[Dict])
async def get_metric_history(
    metric_id: str,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Get metric history with optional time range"""
    try:
        # Check permissions
        if not await security_service.check_permission(current_user["id"], "view_metrics"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view metrics"
            )
            
        history = await performance_metrics_service.get_metric_history(
            metric_id,
            start_time,
            end_time
        )
        
        return [metric.dict() for metric in history]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get metric history: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to get metric history: {e}",
            details={"metric_id": metric_id}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/simulations/{simulation_id}/metrics", response_model=List[Dict])
async def get_simulation_metrics(
    simulation_id: str,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Get metrics for a simulation"""
    try:
        # Check permissions
        if not await security_service.check_permission(current_user["id"], "view_metrics"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view metrics"
            )
            
        metrics = await performance_metrics_service.calculate_simulation_metrics(simulation_id)
        
        return [metric.dict() for metric in metrics]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get simulation metrics: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to get simulation metrics: {e}",
            details={"simulation_id": simulation_id}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) 