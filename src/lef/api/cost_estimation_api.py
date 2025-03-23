"""
API endpoints for cost estimation service
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from ..services.cost_estimation_service import (
    CostEstimationService,
    CostType,
    CostCategory,
    CostStatus,
    CostBreakdown,
    CostEstimate,
    CostActual
)
from ..services.logging_service import LoggingService
from ..services.security_service import SecurityService

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize services
cost_estimation_service = CostEstimationService()
logging_service = LoggingService()
security_service = SecurityService()

class CostEstimateCreate(BaseModel):
    """Cost estimate creation request"""
    name: str
    description: str
    project_id: Optional[str]
    simulation_id: Optional[str]
    cost_type: CostType
    category: CostCategory
    breakdown: CostBreakdown
    start_date: datetime
    end_date: datetime
    confidence_level: float
    assumptions: List[str]
    risks: List[Dict]
    dependencies: List[str]
    metadata: Optional[Dict] = None

class CostEstimateUpdate(BaseModel):
    """Cost estimate update request"""
    name: Optional[str] = None
    description: Optional[str] = None
    cost_type: Optional[CostType] = None
    category: Optional[CostCategory] = None
    status: Optional[CostStatus] = None
    breakdown: Optional[CostBreakdown] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    confidence_level: Optional[float] = None
    assumptions: Optional[List[str]] = None
    risks: Optional[List[Dict]] = None
    dependencies: Optional[List[str]] = None
    metadata: Optional[Dict] = None

class CostActualCreate(BaseModel):
    """Actual cost creation request"""
    estimate_id: str
    breakdown: CostBreakdown
    explanation: Optional[str] = None
    metadata: Optional[Dict] = None

@router.post("/estimates", response_model=Dict)
async def create_estimate(
    estimate: CostEstimateCreate,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Create a new cost estimate"""
    try:
        # Check permissions
        if not await security_service.check_permission(current_user["id"], "create_cost_estimates"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to create cost estimates"
            )
            
        # Create estimate object
        new_estimate = CostEstimate(
            id=f"estimate_{datetime.utcnow().timestamp()}",
            status=CostStatus.DRAFT,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            created_by=current_user["id"],
            updated_by=current_user["id"],
            **estimate.dict()
        )
        
        success, estimate_id = await cost_estimation_service.create_estimate(new_estimate)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create cost estimate"
            )
            
        return {
            "message": "Cost estimate created successfully",
            "estimate_id": estimate_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create cost estimate: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to create cost estimate: {e}",
            details={"estimate_name": estimate.name}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.put("/estimates/{estimate_id}", response_model=Dict)
async def update_estimate(
    estimate_id: str,
    updates: CostEstimateUpdate,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Update an existing cost estimate"""
    try:
        # Check permissions
        if not await security_service.check_permission(current_user["id"], "update_cost_estimates"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update cost estimates"
            )
            
        # Add user to updates
        updates_dict = updates.dict(exclude_unset=True)
        updates_dict["updated_by"] = current_user["id"]
        updates_dict["updated_at"] = datetime.utcnow()
        
        success = await cost_estimation_service.update_estimate(estimate_id, updates_dict)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update cost estimate"
            )
            
        return {
            "message": "Cost estimate updated successfully",
            "estimate_id": estimate_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update cost estimate: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to update cost estimate: {e}",
            details={"estimate_id": estimate_id}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/estimates/{estimate_id}", response_model=Dict)
async def get_estimate(
    estimate_id: str,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Get a cost estimate by ID"""
    try:
        # Check permissions
        if not await security_service.check_permission(current_user["id"], "view_cost_estimates"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view cost estimates"
            )
            
        estimate = await cost_estimation_service.get_estimate(estimate_id)
        
        if not estimate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cost estimate not found"
            )
            
        return estimate.dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get cost estimate: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to get cost estimate: {e}",
            details={"estimate_id": estimate_id}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/estimates", response_model=List[Dict])
async def list_estimates(
    project_id: Optional[str] = None,
    simulation_id: Optional[str] = None,
    cost_type: Optional[CostType] = None,
    category: Optional[CostCategory] = None,
    status: Optional[CostStatus] = None,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """List cost estimates with optional filters"""
    try:
        # Check permissions
        if not await security_service.check_permission(current_user["id"], "view_cost_estimates"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view cost estimates"
            )
            
        estimates = await cost_estimation_service.list_estimates(
            project_id,
            simulation_id,
            cost_type,
            category,
            status
        )
        
        return [estimate.dict() for estimate in estimates]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list cost estimates: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to list cost estimates: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/actuals", response_model=Dict)
async def record_actual_cost(
    actual: CostActualCreate,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Record actual cost"""
    try:
        # Check permissions
        if not await security_service.check_permission(current_user["id"], "record_actual_costs"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to record actual costs"
            )
            
        # Get estimate for variance calculation
        estimate = await cost_estimation_service.get_estimate(actual.estimate_id)
        if not estimate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Referenced estimate not found"
            )
            
        # Calculate variance
        variance = actual.breakdown.total_amount - estimate.breakdown.total_amount
        variance_percentage = (variance / estimate.breakdown.total_amount * 100) if estimate.breakdown.total_amount > 0 else 0
        
        # Create actual cost object
        new_actual = CostActual(
            id=f"actual_{datetime.utcnow().timestamp()}",
            estimate_id=actual.estimate_id,
            breakdown=actual.breakdown,
            variance=variance,
            variance_percentage=variance_percentage,
            explanation=actual.explanation,
            metadata=actual.metadata or {},
            recorded_at=datetime.utcnow(),
            recorded_by=current_user["id"]
        )
        
        success, actual_id = await cost_estimation_service.record_actual_cost(new_actual)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to record actual cost"
            )
            
        return {
            "message": "Actual cost recorded successfully",
            "actual_id": actual_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to record actual cost: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to record actual cost: {e}",
            details={"estimate_id": actual.estimate_id}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/actuals/{actual_id}", response_model=Dict)
async def get_actual_cost(
    actual_id: str,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Get actual cost by ID"""
    try:
        # Check permissions
        if not await security_service.check_permission(current_user["id"], "view_actual_costs"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view actual costs"
            )
            
        actual = await cost_estimation_service.get_actual_cost(actual_id)
        
        if not actual:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Actual cost not found"
            )
            
        return actual.dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get actual cost: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to get actual cost: {e}",
            details={"actual_id": actual_id}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/actuals", response_model=List[Dict])
async def list_actual_costs(
    estimate_id: Optional[str] = None,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """List actual costs with optional filters"""
    try:
        # Check permissions
        if not await security_service.check_permission(current_user["id"], "view_actual_costs"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view actual costs"
            )
            
        actuals = await cost_estimation_service.list_actual_costs(estimate_id)
        return [actual.dict() for actual in actuals]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list actual costs: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to list actual costs: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/projects/{project_id}/costs", response_model=Dict)
async def get_project_costs(
    project_id: str,
    include_estimates: bool = True,
    include_actuals: bool = True,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Get total project costs"""
    try:
        # Check permissions
        if not await security_service.check_permission(current_user["id"], "view_project_costs"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view project costs"
            )
            
        costs = await cost_estimation_service.calculate_project_costs(
            project_id,
            include_estimates,
            include_actuals
        )
        
        if not costs:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found or no cost data available"
            )
            
        return costs
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get project costs: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to get project costs: {e}",
            details={"project_id": project_id}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/simulations/{simulation_id}/costs", response_model=Dict)
async def get_simulation_costs(
    simulation_id: str,
    include_estimates: bool = True,
    include_actuals: bool = True,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Get total simulation costs"""
    try:
        # Check permissions
        if not await security_service.check_permission(current_user["id"], "view_simulation_costs"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view simulation costs"
            )
            
        costs = await cost_estimation_service.calculate_simulation_costs(
            simulation_id,
            include_estimates,
            include_actuals
        )
        
        if not costs:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Simulation not found or no cost data available"
            )
            
        return costs
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get simulation costs: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to get simulation costs: {e}",
            details={"simulation_id": simulation_id}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/trends", response_model=Dict)
async def analyze_cost_trends(
    project_id: Optional[str] = None,
    simulation_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Analyze cost trends"""
    try:
        # Check permissions
        if not await security_service.check_permission(current_user["id"], "view_cost_trends"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view cost trends"
            )
            
        trends = await cost_estimation_service.analyze_cost_trends(
            project_id,
            simulation_id,
            start_date,
            end_date
        )
        
        if not trends:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No cost trend data available"
            )
            
        return trends
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to analyze cost trends: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to analyze cost trends: {e}",
            details={
                "project_id": project_id,
                "simulation_id": simulation_id
            }
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) 