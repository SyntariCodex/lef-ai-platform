"""
API endpoints for success criteria evaluation service
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from ..services.success_criteria_service import (
    SuccessCriteriaService,
    CriteriaType,
    CriteriaStatus,
    EvaluationMethod,
    SuccessCriteria,
    EvaluationResult
)
from ..services.logging_service import LoggingService
from ..services.security_service import SecurityService

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize services
success_criteria_service = SuccessCriteriaService()
logging_service = LoggingService()
security_service = SecurityService()

class SuccessCriteriaCreate(BaseModel):
    """Success criteria creation request"""
    name: str
    description: str
    project_id: Optional[str]
    simulation_id: Optional[str]
    type: CriteriaType
    evaluation_method: EvaluationMethod
    weight: float = Field(ge=0.0, le=1.0)
    target_value: Optional[float]
    threshold: Optional[Dict]
    dependencies: List[str] = []
    metrics: List[str] = []
    evaluation_frequency: str
    metadata: Optional[Dict] = None

class SuccessCriteriaUpdate(BaseModel):
    """Success criteria update request"""
    name: Optional[str] = None
    description: Optional[str] = None
    type: Optional[CriteriaType] = None
    status: Optional[CriteriaStatus] = None
    evaluation_method: Optional[EvaluationMethod] = None
    weight: Optional[float] = Field(None, ge=0.0, le=1.0)
    target_value: Optional[float] = None
    threshold: Optional[Dict] = None
    dependencies: Optional[List[str]] = None
    metrics: Optional[List[str]] = None
    evaluation_frequency: Optional[str] = None
    metadata: Optional[Dict] = None

class EvaluationResultCreate(BaseModel):
    """Evaluation result creation request"""
    criteria_id: str
    status: CriteriaStatus
    score: float = Field(ge=0.0, le=1.0)
    measured_value: Optional[float]
    qualitative_assessment: Optional[str]
    supporting_data: Dict = {}
    recommendations: List[str] = []
    evaluation_method: EvaluationMethod
    metadata: Optional[Dict] = None

@router.post("/criteria", response_model=Dict)
async def create_criteria(
    criteria: SuccessCriteriaCreate,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Create new success criteria"""
    try:
        # Check permissions
        if not await security_service.check_permission(current_user["id"], "create_success_criteria"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to create success criteria"
            )
            
        # Create criteria object
        new_criteria = SuccessCriteria(
            id=f"criteria_{datetime.utcnow().timestamp()}",
            status=CriteriaStatus.PENDING,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            created_by=current_user["id"],
            updated_by=current_user["id"],
            **criteria.dict()
        )
        
        success, criteria_id = await success_criteria_service.create_criteria(new_criteria)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create success criteria"
            )
            
        return {
            "message": "Success criteria created successfully",
            "criteria_id": criteria_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create success criteria: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to create success criteria: {e}",
            details={"criteria_name": criteria.name}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.put("/criteria/{criteria_id}", response_model=Dict)
async def update_criteria(
    criteria_id: str,
    updates: SuccessCriteriaUpdate,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Update existing success criteria"""
    try:
        # Check permissions
        if not await security_service.check_permission(current_user["id"], "update_success_criteria"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update success criteria"
            )
            
        # Add user to updates
        updates_dict = updates.dict(exclude_unset=True)
        updates_dict["updated_by"] = current_user["id"]
        updates_dict["updated_at"] = datetime.utcnow()
        
        success = await success_criteria_service.update_criteria(criteria_id, updates_dict)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update success criteria"
            )
            
        return {
            "message": "Success criteria updated successfully",
            "criteria_id": criteria_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update success criteria: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to update success criteria: {e}",
            details={"criteria_id": criteria_id}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/criteria/{criteria_id}", response_model=Dict)
async def get_criteria(
    criteria_id: str,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Get success criteria by ID"""
    try:
        # Check permissions
        if not await security_service.check_permission(current_user["id"], "view_success_criteria"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view success criteria"
            )
            
        criteria = await success_criteria_service.get_criteria(criteria_id)
        
        if not criteria:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Success criteria not found"
            )
            
        return criteria.dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get success criteria: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to get success criteria: {e}",
            details={"criteria_id": criteria_id}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/criteria", response_model=List[Dict])
async def list_criteria(
    project_id: Optional[str] = None,
    simulation_id: Optional[str] = None,
    criteria_type: Optional[CriteriaType] = None,
    status: Optional[CriteriaStatus] = None,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """List success criteria with optional filters"""
    try:
        # Check permissions
        if not await security_service.check_permission(current_user["id"], "view_success_criteria"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view success criteria"
            )
            
        criteria = await success_criteria_service.list_criteria(
            project_id,
            simulation_id,
            criteria_type,
            status
        )
        
        return [c.dict() for c in criteria]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list success criteria: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to list success criteria: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/evaluations", response_model=Dict)
async def record_evaluation(
    evaluation: EvaluationResultCreate,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Record evaluation result"""
    try:
        # Check permissions
        if not await security_service.check_permission(current_user["id"], "record_evaluations"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to record evaluations"
            )
            
        # Create evaluation result object
        new_evaluation = EvaluationResult(
            id=f"eval_{datetime.utcnow().timestamp()}",
            evaluator_id=current_user["id"],
            evaluated_at=datetime.utcnow(),
            **evaluation.dict()
        )
        
        success, evaluation_id = await success_criteria_service.record_evaluation(new_evaluation)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to record evaluation"
            )
            
        return {
            "message": "Evaluation recorded successfully",
            "evaluation_id": evaluation_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to record evaluation: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to record evaluation: {e}",
            details={"criteria_id": evaluation.criteria_id}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/criteria/{criteria_id}/history", response_model=List[Dict])
async def get_evaluation_history(
    criteria_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Get evaluation history for criteria"""
    try:
        # Check permissions
        if not await security_service.check_permission(current_user["id"], "view_evaluation_history"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view evaluation history"
            )
            
        evaluations = await success_criteria_service.get_evaluation_history(
            criteria_id,
            start_date,
            end_date
        )
        
        return [e.dict() for e in evaluations]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get evaluation history: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to get evaluation history: {e}",
            details={"criteria_id": criteria_id}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/projects/{project_id}/success-score", response_model=Dict)
async def get_project_success_score(
    project_id: str,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Get project success score"""
    try:
        # Check permissions
        if not await security_service.check_permission(current_user["id"], "view_success_scores"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view success scores"
            )
            
        score = await success_criteria_service.calculate_success_score(project_id=project_id)
        
        if not score:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found or no success criteria available"
            )
            
        return score
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get project success score: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to get project success score: {e}",
            details={"project_id": project_id}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/simulations/{simulation_id}/success-score", response_model=Dict)
async def get_simulation_success_score(
    simulation_id: str,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Get simulation success score"""
    try:
        # Check permissions
        if not await security_service.check_permission(current_user["id"], "view_success_scores"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view success scores"
            )
            
        score = await success_criteria_service.calculate_success_score(simulation_id=simulation_id)
        
        if not score:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Simulation not found or no success criteria available"
            )
            
        return score
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get simulation success score: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to get simulation success score: {e}",
            details={"simulation_id": simulation_id}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/trends", response_model=Dict)
async def analyze_success_trends(
    project_id: Optional[str] = None,
    simulation_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Analyze success criteria trends"""
    try:
        # Check permissions
        if not await security_service.check_permission(current_user["id"], "view_success_trends"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view success trends"
            )
            
        trends = await success_criteria_service.analyze_success_trends(
            project_id,
            simulation_id,
            start_date,
            end_date
        )
        
        if not trends:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No success trend data available"
            )
            
        return trends
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to analyze success trends: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to analyze success trends: {e}",
            details={
                "project_id": project_id,
                "simulation_id": simulation_id
            }
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) 