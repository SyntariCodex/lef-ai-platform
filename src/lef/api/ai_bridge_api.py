"""
API endpoints for AI Bridge service
"""

import logging
from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from ..services.ai_bridge_service import AIBridgeService, AIModel, LearningTask
from ..services.logging_service import LoggingService
from ..services.security_service import SecurityService

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize services
ai_bridge_service = AIBridgeService()
logging_service = LoggingService()
security_service = SecurityService()

class ModelCreate(BaseModel):
    """Model creation request"""
    name: str
    type: str
    version: str
    capabilities: List[str]
    endpoint: str
    api_key: Optional[str] = None
    parameters: Optional[Dict] = None

class TaskCreate(BaseModel):
    """Task creation request"""
    name: str
    description: str
    model_name: str
    input_data: Dict
    expected_output: Optional[Dict] = None

@router.post("/models", response_model=Dict)
async def register_model(
    model: ModelCreate,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Register a new AI model"""
    try:
        # Check permissions
        if not await security_service.check_permission(current_user["id"], "manage_ai_models"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to manage AI models"
            )
            
        # Create model
        ai_model = AIModel(**model.dict())
        success = await ai_bridge_service.register_model(ai_model)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to register model"
            )
            
        return {"message": "Model registered successfully", "model_name": model.name}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to register model: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to register model: {e}",
            details={"model_name": model.name}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.delete("/models/{model_name}", response_model=Dict)
async def unregister_model(
    model_name: str,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Unregister an AI model"""
    try:
        # Check permissions
        if not await security_service.check_permission(current_user["id"], "manage_ai_models"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to manage AI models"
            )
            
        success = await ai_bridge_service.unregister_model(model_name)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to unregister model"
            )
            
        return {"message": "Model unregistered successfully", "model_name": model_name}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to unregister model: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to unregister model: {e}",
            details={"model_name": model_name}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/models/{model_name}/status", response_model=Dict)
async def get_model_status(
    model_name: str,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Get the status of an AI model"""
    try:
        # Check permissions
        if not await security_service.check_permission(current_user["id"], "view_ai_models"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view AI models"
            )
            
        status = await ai_bridge_service.get_model_status(model_name)
        
        if not status:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Model not found"
            )
            
        return status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get model status: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to get model status: {e}",
            details={"model_name": model_name}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/tasks", response_model=Dict)
async def create_learning_task(
    task: TaskCreate,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Create a new learning task"""
    try:
        # Check permissions
        if not await security_service.check_permission(current_user["id"], "create_learning_tasks"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to create learning tasks"
            )
            
        # Generate task ID
        task_id = f"task_{len(ai_bridge_service.tasks) + 1}"
        
        # Create task
        learning_task = LearningTask(
            id=task_id,
            **task.dict()
        )
        success = await ai_bridge_service.create_learning_task(learning_task)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create learning task"
            )
            
        return {
            "message": "Learning task created successfully",
            "task_id": task_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create learning task: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to create learning task: {e}",
            details={"task_name": task.name}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/tasks/{task_id}/execute", response_model=Dict)
async def execute_learning_task(
    task_id: str,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Execute a learning task"""
    try:
        # Check permissions
        if not await security_service.check_permission(current_user["id"], "execute_learning_tasks"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to execute learning tasks"
            )
            
        results = await ai_bridge_service.execute_learning_task(task_id)
        
        if not results:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to execute learning task"
            )
            
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to execute learning task: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to execute learning task: {e}",
            details={"task_id": task_id}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/tasks/{task_id}/status", response_model=Dict)
async def get_task_status(
    task_id: str,
    current_user: Dict = Depends(security_service.get_current_user)
):
    """Get the status of a learning task"""
    try:
        # Check permissions
        if not await security_service.check_permission(current_user["id"], "view_learning_tasks"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view learning tasks"
            )
            
        status = await ai_bridge_service.get_task_status(task_id)
        
        if not status:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
            
        return status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get task status: {e}")
        await logging_service.log_message(
            "error",
            f"Failed to get task status: {e}",
            details={"task_id": task_id}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) 