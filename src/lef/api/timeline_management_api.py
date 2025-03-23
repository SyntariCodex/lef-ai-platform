"""
API endpoints for timeline management service
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from ..services.timeline_management_service import (
    TimelineManagementService,
    Timeline,
    Milestone,
    Dependency,
    TimelineStatus,
    MilestoneType,
    DependencyType
)
from ..services.security_service import SecurityService
from ..services.logging_service import LoggingService

logger = logging.getLogger(__name__)

# Initialize services
timeline_service = TimelineManagementService()
security_service = SecurityService()
logging_service = LoggingService()

router = APIRouter()

class TimelineCreate(BaseModel):
    """Request model for timeline creation"""
    project_id: str
    name: str
    description: str
    start_date: datetime
    end_date: datetime
    metadata: Dict = {}

class TimelineUpdate(BaseModel):
    """Request model for timeline updates"""
    name: Optional[str]
    description: Optional[str]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    status: Optional[TimelineStatus]
    metadata: Optional[Dict]

class MilestoneCreate(BaseModel):
    """Request model for milestone creation"""
    name: str
    description: str
    type: MilestoneType
    planned_date: datetime
    metadata: Dict = {}

class MilestoneUpdate(BaseModel):
    """Request model for milestone updates"""
    name: Optional[str]
    description: Optional[str]
    type: Optional[MilestoneType]
    planned_date: Optional[datetime]
    actual_date: Optional[datetime]
    status: Optional[TimelineStatus]
    progress: Optional[float]
    metadata: Optional[Dict]

class DependencyCreate(BaseModel):
    """Request model for dependency creation"""
    source_id: str
    target_id: str
    type: DependencyType
    lag: timedelta = timedelta(0)
    metadata: Dict = {}

class DependencyUpdate(BaseModel):
    """Request model for dependency updates"""
    type: Optional[DependencyType]
    lag: Optional[timedelta]
    metadata: Optional[Dict]

@router.post("/timelines", response_model=Timeline)
async def create_timeline(
    request: TimelineCreate,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Create a new timeline"""
    try:
        if not security_service.check_permission(current_user, "timeline:write"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to create timelines"
            )
            
        timeline = await timeline_service.create_timeline(
            project_id=request.project_id,
            name=request.name,
            description=request.description,
            start_date=request.start_date,
            end_date=request.end_date,
            metadata=request.metadata
        )
        
        await logging_service.log_action(
            current_user["id"],
            "timeline",
            "create",
            {"timeline_id": timeline.id}
        )
            
        return timeline
    except Exception as e:
        logger.error(f"Failed to create timeline: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/timelines/{timeline_id}", response_model=Timeline)
async def get_timeline(
    timeline_id: str,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Get timeline by ID"""
    try:
        if not security_service.check_permission(current_user, "timeline:read"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view timelines"
            )
            
        timeline = await timeline_service.get_timeline(timeline_id)
        if not timeline:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Timeline not found"
            )
            
        return timeline
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get timeline: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put("/timelines/{timeline_id}", response_model=Timeline)
async def update_timeline(
    timeline_id: str,
    request: TimelineUpdate,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Update timeline"""
    try:
        if not security_service.check_permission(current_user, "timeline:write"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update timelines"
            )
            
        updates = request.dict(exclude_unset=True)
        timeline = await timeline_service.update_timeline(timeline_id, updates)
        
        if not timeline:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Timeline not found"
            )
            
        await logging_service.log_action(
            current_user["id"],
            "timeline",
            "update",
            {"timeline_id": timeline_id, "updates": updates}
        )
            
        return timeline
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update timeline: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/timelines/{timeline_id}")
async def delete_timeline(
    timeline_id: str,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Delete timeline"""
    try:
        if not security_service.check_permission(current_user, "timeline:write"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete timelines"
            )
            
        success = await timeline_service.delete_timeline(timeline_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Timeline not found"
            )
            
        await logging_service.log_action(
            current_user["id"],
            "timeline",
            "delete",
            {"timeline_id": timeline_id}
        )
            
        return {"status": "success"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete timeline: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/timelines/{timeline_id}/milestones", response_model=Milestone)
async def create_milestone(
    timeline_id: str,
    request: MilestoneCreate,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Create a new milestone"""
    try:
        if not security_service.check_permission(current_user, "timeline:write"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to create milestones"
            )
            
        milestone = await timeline_service.create_milestone(
            timeline_id=timeline_id,
            name=request.name,
            description=request.description,
            milestone_type=request.type,
            planned_date=request.planned_date,
            metadata=request.metadata
        )
        
        if not milestone:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Timeline not found"
            )
            
        await logging_service.log_action(
            current_user["id"],
            "milestone",
            "create",
            {"milestone_id": milestone.id, "timeline_id": timeline_id}
        )
            
        return milestone
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create milestone: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put("/milestones/{milestone_id}", response_model=Milestone)
async def update_milestone(
    milestone_id: str,
    request: MilestoneUpdate,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Update milestone"""
    try:
        if not security_service.check_permission(current_user, "timeline:write"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update milestones"
            )
            
        updates = request.dict(exclude_unset=True)
        milestone = await timeline_service.update_milestone(milestone_id, updates)
        
        if not milestone:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Milestone not found"
            )
            
        await logging_service.log_action(
            current_user["id"],
            "milestone",
            "update",
            {"milestone_id": milestone_id, "updates": updates}
        )
            
        return milestone
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update milestone: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/milestones/{milestone_id}")
async def delete_milestone(
    milestone_id: str,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Delete milestone"""
    try:
        if not security_service.check_permission(current_user, "timeline:write"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete milestones"
            )
            
        success = await timeline_service.delete_milestone(milestone_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Milestone not found"
            )
            
        await logging_service.log_action(
            current_user["id"],
            "milestone",
            "delete",
            {"milestone_id": milestone_id}
        )
            
        return {"status": "success"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete milestone: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/timelines/{timeline_id}/dependencies", response_model=Dependency)
async def create_dependency(
    timeline_id: str,
    request: DependencyCreate,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Create a new dependency"""
    try:
        if not security_service.check_permission(current_user, "timeline:write"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to create dependencies"
            )
            
        dependency = await timeline_service.create_dependency(
            timeline_id=timeline_id,
            source_id=request.source_id,
            target_id=request.target_id,
            dependency_type=request.type,
            lag=request.lag,
            metadata=request.metadata
        )
        
        if not dependency:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Timeline or milestones not found"
            )
            
        await logging_service.log_action(
            current_user["id"],
            "dependency",
            "create",
            {
                "dependency_id": dependency.id,
                "timeline_id": timeline_id,
                "source_id": request.source_id,
                "target_id": request.target_id
            }
        )
            
        return dependency
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create dependency: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put("/dependencies/{dependency_id}", response_model=Dependency)
async def update_dependency(
    dependency_id: str,
    request: DependencyUpdate,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Update dependency"""
    try:
        if not security_service.check_permission(current_user, "timeline:write"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update dependencies"
            )
            
        updates = request.dict(exclude_unset=True)
        dependency = await timeline_service.update_dependency(dependency_id, updates)
        
        if not dependency:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dependency not found"
            )
            
        await logging_service.log_action(
            current_user["id"],
            "dependency",
            "update",
            {"dependency_id": dependency_id, "updates": updates}
        )
            
        return dependency
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update dependency: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/dependencies/{dependency_id}")
async def delete_dependency(
    dependency_id: str,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Delete dependency"""
    try:
        if not security_service.check_permission(current_user, "timeline:write"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete dependencies"
            )
            
        success = await timeline_service.delete_dependency(dependency_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dependency not found"
            )
            
        await logging_service.log_action(
            current_user["id"],
            "dependency",
            "delete",
            {"dependency_id": dependency_id}
        )
            
        return {"status": "success"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete dependency: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/timelines/{timeline_id}/critical-path", response_model=List[str])
async def get_critical_path(
    timeline_id: str,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Get critical path for timeline"""
    try:
        if not security_service.check_permission(current_user, "timeline:read"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view critical path"
            )
            
        critical_path = await timeline_service.calculate_critical_path(timeline_id)
        return critical_path
    except Exception as e:
        logger.error(f"Failed to get critical path: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/timelines/{timeline_id}/progress")
async def update_timeline_progress(
    timeline_id: str,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Update timeline progress"""
    try:
        if not security_service.check_permission(current_user, "timeline:write"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update timeline progress"
            )
            
        success = await timeline_service.update_progress(timeline_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Timeline not found"
            )
            
        await logging_service.log_action(
            current_user["id"],
            "timeline",
            "update_progress",
            {"timeline_id": timeline_id}
        )
            
        return {"status": "success"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update timeline progress: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/health")
async def check_health(
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Check service health"""
    try:
        if not security_service.check_permission(current_user, "timeline:read"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to check service health"
            )
            
        health_status = await timeline_service.check_health()
        return health_status
    except Exception as e:
        logger.error(f"Failed to check service health: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) 