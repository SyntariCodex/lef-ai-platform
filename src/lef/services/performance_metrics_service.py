"""
Performance Metrics Service for tracking and analyzing simulation and project performance
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from ..services.logging_service import LoggingService
from ..services.simulation_service import SimulationService

logger = logging.getLogger(__name__)

class MetricType(str, Enum):
    """Metric type"""
    EFFICIENCY = "efficiency"
    QUALITY = "quality"
    COST = "cost"
    TIME = "time"
    RESOURCE = "resource"
    CUSTOM = "custom"

class MetricCategory(str, Enum):
    """Metric category"""
    SIMULATION = "simulation"
    PROJECT = "project"
    SYSTEM = "system"
    USER = "user"

class Metric(BaseModel):
    """Performance metric definition"""
    id: str
    name: str
    description: str
    type: MetricType
    category: MetricCategory
    value: float
    unit: str
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    target_value: Optional[float] = None
    threshold_min: Optional[float] = None
    threshold_max: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class MetricCollection(BaseModel):
    """Collection of related metrics"""
    id: str
    name: str
    description: str
    simulation_id: Optional[str] = None
    project_id: Optional[str] = None
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metrics: List[Metric] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class PerformanceMetricsService:
    """Service for managing performance metrics"""
    
    def __init__(self):
        self.logging_service = LoggingService()
        self.simulation_service = SimulationService()
        self.metrics: Dict[str, Metric] = {}
        self.metric_collections: Dict[str, MetricCollection] = {}
        self.metric_history: Dict[str, List[Metric]] = {}
        
    async def initialize(self):
        """Initialize the performance metrics service"""
        try:
            await self.logging_service.initialize()
            await self.simulation_service.initialize()
            logger.info("Performance Metrics Service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Performance Metrics Service: {e}")
            await self.logging_service.log_message(
                "error",
                f"Failed to initialize Performance Metrics Service: {e}"
            )
            raise
            
    async def create_metric(self, metric: Metric) -> bool:
        """Create a new metric"""
        try:
            if metric.id in self.metrics:
                raise ValueError(f"Metric {metric.id} already exists")
                
            # Store metric
            self.metrics[metric.id] = metric
            
            # Add to history
            if metric.id not in self.metric_history:
                self.metric_history[metric.id] = []
            self.metric_history[metric.id].append(metric)
            
            await self.logging_service.log_message(
                "info",
                f"Created new metric: {metric.id}",
                details={
                    "name": metric.name,
                    "type": metric.type,
                    "category": metric.category,
                    "created_by": metric.created_by
                }
            )
            return True
            
        except Exception as e:
            logger.error(f"Failed to create metric {metric.id}: {e}")
            await self.logging_service.log_message(
                "error",
                f"Failed to create metric {metric.id}: {e}"
            )
            return False
            
    async def update_metric(self, metric_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing metric"""
        try:
            if metric_id not in self.metrics:
                raise ValueError(f"Metric {metric_id} not found")
                
            metric = self.metrics[metric_id]
            
            # Update metric
            for key, value in updates.items():
                if hasattr(metric, key):
                    setattr(metric, key, value)
                    
            metric.updated_at = datetime.utcnow()
            
            # Add to history
            self.metric_history[metric_id].append(metric)
            
            await self.logging_service.log_message(
                "info",
                f"Updated metric: {metric_id}",
                details={"updated_by": updates.get("updated_by", "system")}
            )
            return True
            
        except Exception as e:
            logger.error(f"Failed to update metric {metric_id}: {e}")
            await self.logging_service.log_message(
                "error",
                f"Failed to update metric {metric_id}: {e}"
            )
            return False
            
    async def get_metric(self, metric_id: str) -> Optional[Metric]:
        """Get a metric by ID"""
        try:
            if metric_id not in self.metrics:
                raise ValueError(f"Metric {metric_id} not found")
                
            return self.metrics[metric_id]
            
        except Exception as e:
            logger.error(f"Failed to get metric {metric_id}: {e}")
            await self.logging_service.log_message(
                "error",
                f"Failed to get metric {metric_id}: {e}"
            )
            return None
            
    async def list_metrics(
        self,
        category: Optional[MetricCategory] = None,
        type: Optional[MetricType] = None,
        simulation_id: Optional[str] = None,
        project_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List metrics with optional filters"""
        try:
            metrics = []
            for metric in self.metrics.values():
                # Apply filters
                if category and metric.category != category:
                    continue
                if type and metric.type != type:
                    continue
                    
                metrics.append({
                    "id": metric.id,
                    "name": metric.name,
                    "description": metric.description,
                    "type": metric.type,
                    "category": metric.category,
                    "value": metric.value,
                    "unit": metric.unit,
                    "target_value": metric.target_value,
                    "threshold_min": metric.threshold_min,
                    "threshold_max": metric.threshold_max
                })
                
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to list metrics: {e}")
            await self.logging_service.log_message(
                "error",
                f"Failed to list metrics: {e}"
            )
            return []
            
    async def create_metric_collection(
        self,
        name: str,
        description: str,
        user_id: str,
        simulation_id: Optional[str] = None,
        project_id: Optional[str] = None,
        metrics: Optional[List[Metric]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """Create a new metric collection"""
        try:
            # Create collection
            collection = MetricCollection(
                id=f"collection_{len(self.metric_collections) + 1}",
                name=name,
                description=description,
                simulation_id=simulation_id,
                project_id=project_id,
                created_by=user_id,
                metrics=metrics or [],
                metadata=metadata or {}
            )
            
            # Store collection
            self.metric_collections[collection.id] = collection
            
            await self.logging_service.log_message(
                "info",
                f"Created new metric collection: {collection.id}",
                details={
                    "name": name,
                    "simulation_id": simulation_id,
                    "project_id": project_id,
                    "created_by": user_id
                }
            )
            return collection.id
            
        except Exception as e:
            logger.error(f"Failed to create metric collection: {e}")
            await self.logging_service.log_message(
                "error",
                f"Failed to create metric collection: {e}"
            )
            return None
            
    async def get_metric_collection(self, collection_id: str) -> Optional[MetricCollection]:
        """Get a metric collection by ID"""
        try:
            if collection_id not in self.metric_collections:
                raise ValueError(f"Metric collection {collection_id} not found")
                
            return self.metric_collections[collection_id]
            
        except Exception as e:
            logger.error(f"Failed to get metric collection {collection_id}: {e}")
            await self.logging_service.log_message(
                "error",
                f"Failed to get metric collection {collection_id}: {e}"
            )
            return None
            
    async def list_metric_collections(
        self,
        simulation_id: Optional[str] = None,
        project_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List metric collections with optional filters"""
        try:
            collections = []
            for collection in self.metric_collections.values():
                # Apply filters
                if simulation_id and collection.simulation_id != simulation_id:
                    continue
                if project_id and collection.project_id != project_id:
                    continue
                if user_id and collection.created_by != user_id:
                    continue
                    
                collections.append({
                    "id": collection.id,
                    "name": collection.name,
                    "description": collection.description,
                    "simulation_id": collection.simulation_id,
                    "project_id": collection.project_id,
                    "created_at": collection.created_at,
                    "updated_at": collection.updated_at,
                    "number_of_metrics": len(collection.metrics)
                })
                
            return collections
            
        except Exception as e:
            logger.error(f"Failed to list metric collections: {e}")
            await self.logging_service.log_message(
                "error",
                f"Failed to list metric collections: {e}"
            )
            return []
            
    async def get_metric_history(
        self,
        metric_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Metric]:
        """Get metric history with optional time range"""
        try:
            if metric_id not in self.metric_history:
                raise ValueError(f"Metric {metric_id} not found")
                
            history = self.metric_history[metric_id]
            
            # Filter by time range if specified
            if start_time:
                history = [m for m in history if m.created_at >= start_time]
            if end_time:
                history = [m for m in history if m.created_at <= end_time]
                
            return history
            
        except Exception as e:
            logger.error(f"Failed to get metric history {metric_id}: {e}")
            await self.logging_service.log_message(
                "error",
                f"Failed to get metric history {metric_id}: {e}"
            )
            return []
            
    async def calculate_simulation_metrics(self, simulation_id: str) -> List[Metric]:
        """Calculate metrics for a simulation"""
        try:
            # Get simulation
            simulation = await self.simulation_service.get_simulation(simulation_id)
            if not simulation:
                raise ValueError(f"Simulation {simulation_id} not found")
                
            metrics = []
            
            # Calculate efficiency metrics
            if simulation.started_at and simulation.completed_at:
                duration = (simulation.completed_at - simulation.started_at).total_seconds()
                metrics.append(Metric(
                    id=f"efficiency_{simulation_id}",
                    name="Simulation Duration",
                    description="Total time taken for simulation",
                    type=MetricType.EFFICIENCY,
                    category=MetricCategory.SIMULATION,
                    value=duration,
                    unit="seconds",
                    created_by="system"
                ))
                
            # Calculate quality metrics
            if simulation.errors:
                metrics.append(Metric(
                    id=f"quality_{simulation_id}",
                    name="Error Count",
                    description="Number of errors encountered",
                    type=MetricType.QUALITY,
                    category=MetricCategory.SIMULATION,
                    value=len(simulation.errors),
                    unit="count",
                    created_by="system"
                ))
                
            # Calculate resource metrics
            if simulation.resources:
                for resource, value in simulation.resources.items():
                    metrics.append(Metric(
                        id=f"resource_{simulation_id}_{resource}",
                        name=f"Resource Usage - {resource}",
                        description=f"Resource usage for {resource}",
                        type=MetricType.RESOURCE,
                        category=MetricCategory.SIMULATION,
                        value=value,
                        unit="count",
                        created_by="system"
                    ))
                    
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to calculate simulation metrics: {e}")
            await self.logging_service.log_message(
                "error",
                f"Failed to calculate simulation metrics: {e}"
            )
            return [] 