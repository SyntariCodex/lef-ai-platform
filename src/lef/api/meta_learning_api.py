"""
API endpoints for meta-learning service
"""

import logging
from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from ..services.meta_learning_service import (
    MetaLearningService,
    LearningPattern,
    SystemImprovement
)
from ..services.security_service import SecurityService
from ..services.logging_service import LoggingService

logger = logging.getLogger(__name__)

# Initialize services
meta_learning_service = MetaLearningService()
security_service = SecurityService()
logging_service = LoggingService()

router = APIRouter()

class PerformanceAnalysisResponse(BaseModel):
    """Response model for system performance analysis"""
    timestamp: str
    overall_health: float
    component_performance: Dict
    improvement_opportunities: List[Dict]

class ImprovementRequest(BaseModel):
    """Request model for applying improvements"""
    improvement_ids: List[str]

@router.get("/performance", response_model=PerformanceAnalysisResponse)
async def analyze_system_performance(
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Analyze performance across all system components"""
    try:
        if not security_service.check_permission(current_user, "meta_learning:read"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to analyze system performance"
            )
            
        performance_data = await meta_learning_service.analyze_system_performance()
        if not performance_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to analyze system performance"
            )
            
        await logging_service.log_action(
            current_user["id"],
            "meta_learning",
            "analyze_performance",
            {"result": "success"}
        )
            
        return performance_data
    except Exception as e:
        logger.error(f"Failed to analyze system performance: {e}")
        await logging_service.log_action(
            current_user["id"],
            "meta_learning",
            "analyze_performance",
            {"result": "error", "error": str(e)}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/patterns", response_model=List[LearningPattern])
async def get_learning_patterns(
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Get identified learning patterns"""
    try:
        if not security_service.check_permission(current_user, "meta_learning:read"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view learning patterns"
            )
            
        patterns = await meta_learning_service.identify_learning_patterns()
        
        await logging_service.log_action(
            current_user["id"],
            "meta_learning",
            "get_patterns",
            {"result": "success", "pattern_count": len(patterns)}
        )
            
        return patterns
    except Exception as e:
        logger.error(f"Failed to get learning patterns: {e}")
        await logging_service.log_action(
            current_user["id"],
            "meta_learning",
            "get_patterns",
            {"result": "error", "error": str(e)}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/improvements", response_model=List[SystemImprovement])
async def get_improvements(
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Get generated system improvements"""
    try:
        if not security_service.check_permission(current_user, "meta_learning:read"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view improvements"
            )
            
        improvements = await meta_learning_service.generate_improvements()
        
        await logging_service.log_action(
            current_user["id"],
            "meta_learning",
            "get_improvements",
            {"result": "success", "improvement_count": len(improvements)}
        )
            
        return improvements
    except Exception as e:
        logger.error(f"Failed to get improvements: {e}")
        await logging_service.log_action(
            current_user["id"],
            "meta_learning",
            "get_improvements",
            {"result": "error", "error": str(e)}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/improvements/apply", response_model=Dict)
async def apply_improvements(
    request: ImprovementRequest,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Apply selected system improvements"""
    try:
        if not security_service.check_permission(current_user, "meta_learning:write"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to apply improvements"
            )
            
        # Get improvements by IDs
        improvements = []
        for imp_id in request.improvement_ids:
            if imp_id in meta_learning_service.improvements:
                improvements.append(meta_learning_service.improvements[imp_id])
            
        if not improvements:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No valid improvements found"
            )
            
        results = await meta_learning_service.apply_improvements(improvements)
        
        await logging_service.log_action(
            current_user["id"],
            "meta_learning",
            "apply_improvements",
            {
                "result": "success",
                "improvement_ids": request.improvement_ids,
                "results": results
            }
        )
            
        return results
    except Exception as e:
        logger.error(f"Failed to apply improvements: {e}")
        await logging_service.log_action(
            current_user["id"],
            "meta_learning",
            "apply_improvements",
            {
                "result": "error",
                "improvement_ids": request.improvement_ids,
                "error": str(e)
            }
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/improvements/validate", response_model=Dict)
async def validate_improvements(
    request: ImprovementRequest,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Validate applied improvements"""
    try:
        if not security_service.check_permission(current_user, "meta_learning:write"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to validate improvements"
            )
            
        validation_results = await meta_learning_service.validate_improvements(
            request.improvement_ids
        )
        
        await logging_service.log_action(
            current_user["id"],
            "meta_learning",
            "validate_improvements",
            {
                "result": "success",
                "improvement_ids": request.improvement_ids,
                "validation_results": validation_results
            }
        )
            
        return validation_results
    except Exception as e:
        logger.error(f"Failed to validate improvements: {e}")
        await logging_service.log_action(
            current_user["id"],
            "meta_learning",
            "validate_improvements",
            {
                "result": "error",
                "improvement_ids": request.improvement_ids,
                "error": str(e)
            }
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/health")
async def check_health(
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Check meta-learning service health"""
    try:
        if not security_service.check_permission(current_user, "meta_learning:read"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to check service health"
            )
            
        health_status = await meta_learning_service.check_health()
        return health_status
    except Exception as e:
        logger.error(f"Failed to check service health: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) 