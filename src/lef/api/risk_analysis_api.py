"""
API endpoints for risk analysis service
"""

import logging
from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from ..services.risk_analysis_service import (
    RiskAnalysisService,
    Risk,
    RiskAssessment,
    RiskCategory,
    RiskLevel,
    RiskImpact,
    RiskProbability
)
from ..services.logging_service import LoggingService
from ..services.security_service import SecurityService

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize services
risk_analysis_service = RiskAnalysisService()
logging_service = LoggingService()
security_service = SecurityService()

class RiskCreate(BaseModel):
    """Risk creation request"""
    name: str
    description: str
    category: RiskCategory
    level: RiskLevel
    impact: RiskImpact
    probability: RiskProbability
    mitigation_strategy: Optional[str] = None
    mitigation_status: Optional[str] = None
    mitigation_effort: Optional[str] = None
    mitigation_cost: Optional[float] = None
    residual_risk: Optional[RiskLevel] = None
    dependencies: List[str] = []
    affected_components: List[str] = []
    tags: List[str] = []
    metadata: Optional[Dict] = None

class RiskUpdate(BaseModel):
    """Risk update request"""
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[RiskCategory] = None
    level: Optional[RiskLevel] = None
    impact: Optional[RiskImpact] = None
    probability: Optional[RiskProbability] = None
    mitigation_strategy: Optional[str] = None
    mitigation_status: Optional[str] = None
    mitigation_effort: Optional[str] = None
    mitigation_cost: Optional[float] = None
    residual_risk: Optional[RiskLevel] = None
    dependencies: Optional[List[str]] = None
    affected_components: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict] = None

class RiskAssessmentCreate(BaseModel):
    """Risk assessment creation request"""
    simulation_id: str
    risks: List[Risk]
    metadata: Optional[Dict] = None

@router.post("/risks", response_model=Dict)
async def create_risk(
    risk: RiskCreate,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Create a new risk"""
    try:
        # Check permissions
        if not await security_service.check_permission(current_user["id"], "create_risks"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to create risks"
            )
            
        # Create risk
        new_risk = Risk(
            id=f"risk_{len(risk_analysis_service.risks) + 1}",
            created_by=current_user["id"],
            **risk.dict()
        )
        success = await risk_analysis_service.create_risk(new_risk)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create risk"
            )
            
        return {
            "message": "Risk created successfully",
            "risk_id": new_risk.id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create risk: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to create risk: {e}",
            details={"risk_name": risk.name}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.put("/risks/{risk_id}", response_model=Dict)
async def update_risk(
    risk_id: str,
    updates: RiskUpdate,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Update an existing risk"""
    try:
        # Check permissions
        if not await security_service.check_permission(current_user["id"], "update_risks"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update risks"
            )
            
        # Add user to updates
        updates_dict = updates.dict(exclude_unset=True)
        updates_dict["updated_by"] = current_user["id"]
        
        success = await risk_analysis_service.update_risk(risk_id, updates_dict)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update risk"
            )
            
        return {
            "message": "Risk updated successfully",
            "risk_id": risk_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update risk: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to update risk: {e}",
            details={"risk_id": risk_id}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/risks/{risk_id}", response_model=Dict)
async def get_risk(
    risk_id: str,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Get a risk by ID"""
    try:
        # Check permissions
        if not await security_service.check_permission(current_user["id"], "view_risks"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view risks"
            )
            
        risk = await risk_analysis_service.get_risk(risk_id)
        
        if not risk:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Risk not found"
            )
            
        return risk.dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get risk: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to get risk: {e}",
            details={"risk_id": risk_id}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/risks", response_model=List[Dict])
async def list_risks(
    category: Optional[RiskCategory] = None,
    level: Optional[RiskLevel] = None,
    impact: Optional[RiskImpact] = None,
    probability: Optional[RiskProbability] = None,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """List risks with optional filters"""
    try:
        # Check permissions
        if not await security_service.check_permission(current_user["id"], "view_risks"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view risks"
            )
            
        risks = await risk_analysis_service.list_risks(
            category,
            level,
            impact,
            probability
        )
        
        return risks
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list risks: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to list risks: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/assessments", response_model=Dict)
async def create_risk_assessment(
    assessment: RiskAssessmentCreate,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Create a new risk assessment"""
    try:
        # Check permissions
        if not await security_service.check_permission(current_user["id"], "create_assessments"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to create risk assessments"
            )
            
        # Create assessment
        assessment_id = await risk_analysis_service.create_risk_assessment(
            assessment.simulation_id,
            assessment.risks,
            current_user["id"],
            assessment.metadata
        )
        
        if not assessment_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create risk assessment"
            )
            
        return {
            "message": "Risk assessment created successfully",
            "assessment_id": assessment_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create risk assessment: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to create risk assessment: {e}",
            details={"simulation_id": assessment.simulation_id}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/assessments/{assessment_id}", response_model=Dict)
async def get_risk_assessment(
    assessment_id: str,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Get a risk assessment by ID"""
    try:
        # Check permissions
        if not await security_service.check_permission(current_user["id"], "view_assessments"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view risk assessments"
            )
            
        assessment = await risk_analysis_service.get_risk_assessment(assessment_id)
        
        if not assessment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Risk assessment not found"
            )
            
        return assessment.dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get risk assessment: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to get risk assessment: {e}",
            details={"assessment_id": assessment_id}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/simulations/{simulation_id}/assessments", response_model=List[Dict])
async def list_risk_assessments(
    simulation_id: str,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """List risk assessments for a simulation"""
    try:
        # Check permissions
        if not await security_service.check_permission(current_user["id"], "view_assessments"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view risk assessments"
            )
            
        assessments = await risk_analysis_service.list_risk_assessments(
            simulation_id,
            current_user["id"]
        )
        
        return assessments
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list risk assessments: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to list risk assessments: {e}",
            details={"simulation_id": simulation_id}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) 