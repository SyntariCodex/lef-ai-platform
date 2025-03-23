"""
Cost estimation service for calculating and tracking project and simulation costs
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from enum import Enum
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class CostType(Enum):
    """Types of costs that can be estimated"""
    LABOR = "labor"
    MATERIAL = "material"
    EQUIPMENT = "equipment"
    SOFTWARE = "software"
    INFRASTRUCTURE = "infrastructure"
    OPERATIONAL = "operational"
    MAINTENANCE = "maintenance"
    OVERHEAD = "overhead"
    CONTINGENCY = "contingency"
    CUSTOM = "custom"

class CostCategory(Enum):
    """Categories for cost classification"""
    DIRECT = "direct"
    INDIRECT = "indirect"
    FIXED = "fixed"
    VARIABLE = "variable"
    RECURRING = "recurring"
    NON_RECURRING = "non_recurring"

class CostStatus(Enum):
    """Status of a cost estimate"""
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class CostBreakdown(BaseModel):
    """Cost breakdown model"""
    base_amount: float
    tax_amount: Optional[float] = 0.0
    discount_amount: Optional[float] = 0.0
    overhead_amount: Optional[float] = 0.0
    contingency_amount: Optional[float] = 0.0
    total_amount: float
    currency: str

class CostEstimate(BaseModel):
    """Cost estimate model"""
    id: str
    name: str
    description: str
    project_id: Optional[str]
    simulation_id: Optional[str]
    cost_type: CostType
    category: CostCategory
    status: CostStatus
    breakdown: CostBreakdown
    start_date: datetime
    end_date: datetime
    confidence_level: float  # 0-1 scale
    assumptions: List[str]
    risks: List[Dict]
    dependencies: List[str]
    metadata: Dict = {}
    created_at: datetime
    updated_at: datetime
    created_by: str
    updated_by: str

class CostActual(BaseModel):
    """Actual cost tracking model"""
    id: str
    estimate_id: str
    breakdown: CostBreakdown
    variance: float  # Difference between estimated and actual
    variance_percentage: float
    explanation: Optional[str]
    metadata: Dict = {}
    recorded_at: datetime
    recorded_by: str

class CostEstimationService:
    """Service for managing cost estimations"""
    
    def __init__(self):
        """Initialize the service"""
        self.estimates: Dict[str, CostEstimate] = {}
        self.actuals: Dict[str, CostActual] = {}
        
    async def initialize(self) -> bool:
        """Initialize the service"""
        try:
            logger.info("Initializing cost estimation service")
            # Initialize data stores, connections, etc.
            return True
        except Exception as e:
            logger.error(f"Failed to initialize cost estimation service: {e}")
            return False
            
    async def cleanup(self) -> bool:
        """Cleanup service resources"""
        try:
            logger.info("Cleaning up cost estimation service")
            # Cleanup connections, temp data, etc.
            return True
        except Exception as e:
            logger.error(f"Failed to cleanup cost estimation service: {e}")
            return False
            
    async def create_estimate(self, estimate: CostEstimate) -> Tuple[bool, Optional[str]]:
        """Create a new cost estimate"""
        try:
            if estimate.id in self.estimates:
                return False, "Estimate ID already exists"
                
            self.estimates[estimate.id] = estimate
            logger.info(f"Created cost estimate: {estimate.id}")
            return True, estimate.id
        except Exception as e:
            logger.error(f"Failed to create cost estimate: {e}")
            return False, str(e)
            
    async def update_estimate(self, estimate_id: str, updates: Dict) -> bool:
        """Update an existing cost estimate"""
        try:
            if estimate_id not in self.estimates:
                return False
                
            estimate = self.estimates[estimate_id]
            updated_estimate = estimate.copy(update=updates)
            self.estimates[estimate_id] = updated_estimate
            logger.info(f"Updated cost estimate: {estimate_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to update cost estimate: {e}")
            return False
            
    async def get_estimate(self, estimate_id: str) -> Optional[CostEstimate]:
        """Get a cost estimate by ID"""
        return self.estimates.get(estimate_id)
        
    async def list_estimates(
        self,
        project_id: Optional[str] = None,
        simulation_id: Optional[str] = None,
        cost_type: Optional[CostType] = None,
        category: Optional[CostCategory] = None,
        status: Optional[CostStatus] = None
    ) -> List[CostEstimate]:
        """List cost estimates with optional filters"""
        estimates = list(self.estimates.values())
        
        if project_id:
            estimates = [e for e in estimates if e.project_id == project_id]
        if simulation_id:
            estimates = [e for e in estimates if e.simulation_id == simulation_id]
        if cost_type:
            estimates = [e for e in estimates if e.cost_type == cost_type]
        if category:
            estimates = [e for e in estimates if e.category == category]
        if status:
            estimates = [e for e in estimates if e.status == status]
            
        return estimates
        
    async def record_actual_cost(self, actual: CostActual) -> Tuple[bool, Optional[str]]:
        """Record actual cost"""
        try:
            if actual.id in self.actuals:
                return False, "Actual cost ID already exists"
                
            # Verify estimate exists
            if actual.estimate_id not in self.estimates:
                return False, "Referenced estimate does not exist"
                
            self.actuals[actual.id] = actual
            logger.info(f"Recorded actual cost: {actual.id}")
            return True, actual.id
        except Exception as e:
            logger.error(f"Failed to record actual cost: {e}")
            return False, str(e)
            
    async def get_actual_cost(self, actual_id: str) -> Optional[CostActual]:
        """Get actual cost by ID"""
        return self.actuals.get(actual_id)
        
    async def list_actual_costs(
        self,
        estimate_id: Optional[str] = None
    ) -> List[CostActual]:
        """List actual costs with optional filters"""
        actuals = list(self.actuals.values())
        
        if estimate_id:
            actuals = [a for a in actuals if a.estimate_id == estimate_id]
            
        return actuals
        
    async def calculate_project_costs(
        self,
        project_id: str,
        include_estimates: bool = True,
        include_actuals: bool = True
    ) -> Dict:
        """Calculate total project costs"""
        try:
            total_estimated = 0.0
            total_actual = 0.0
            cost_breakdown = {}
            
            if include_estimates:
                estimates = await self.list_estimates(project_id=project_id)
                for estimate in estimates:
                    total_estimated += estimate.breakdown.total_amount
                    cost_type = estimate.cost_type.value
                    if cost_type not in cost_breakdown:
                        cost_breakdown[cost_type] = {
                            "estimated": 0.0,
                            "actual": 0.0
                        }
                    cost_breakdown[cost_type]["estimated"] += estimate.breakdown.total_amount
                    
            if include_actuals:
                project_estimates = await self.list_estimates(project_id=project_id)
                estimate_ids = [e.id for e in project_estimates]
                actuals = [
                    a for a in self.actuals.values()
                    if a.estimate_id in estimate_ids
                ]
                for actual in actuals:
                    total_actual += actual.breakdown.total_amount
                    estimate = self.estimates[actual.estimate_id]
                    cost_type = estimate.cost_type.value
                    cost_breakdown[cost_type]["actual"] += actual.breakdown.total_amount
                    
            return {
                "project_id": project_id,
                "total_estimated": total_estimated,
                "total_actual": total_actual,
                "variance": total_actual - total_estimated,
                "variance_percentage": ((total_actual - total_estimated) / total_estimated * 100) if total_estimated > 0 else 0,
                "cost_breakdown": cost_breakdown
            }
        except Exception as e:
            logger.error(f"Failed to calculate project costs: {e}")
            return {}
            
    async def calculate_simulation_costs(
        self,
        simulation_id: str,
        include_estimates: bool = True,
        include_actuals: bool = True
    ) -> Dict:
        """Calculate total simulation costs"""
        try:
            total_estimated = 0.0
            total_actual = 0.0
            cost_breakdown = {}
            
            if include_estimates:
                estimates = await self.list_estimates(simulation_id=simulation_id)
                for estimate in estimates:
                    total_estimated += estimate.breakdown.total_amount
                    cost_type = estimate.cost_type.value
                    if cost_type not in cost_breakdown:
                        cost_breakdown[cost_type] = {
                            "estimated": 0.0,
                            "actual": 0.0
                        }
                    cost_breakdown[cost_type]["estimated"] += estimate.breakdown.total_amount
                    
            if include_actuals:
                simulation_estimates = await self.list_estimates(simulation_id=simulation_id)
                estimate_ids = [e.id for e in simulation_estimates]
                actuals = [
                    a for a in self.actuals.values()
                    if a.estimate_id in estimate_ids
                ]
                for actual in actuals:
                    total_actual += actual.breakdown.total_amount
                    estimate = self.estimates[actual.estimate_id]
                    cost_type = estimate.cost_type.value
                    cost_breakdown[cost_type]["actual"] += actual.breakdown.total_amount
                    
            return {
                "simulation_id": simulation_id,
                "total_estimated": total_estimated,
                "total_actual": total_actual,
                "variance": total_actual - total_estimated,
                "variance_percentage": ((total_actual - total_estimated) / total_estimated * 100) if total_estimated > 0 else 0,
                "cost_breakdown": cost_breakdown
            }
        except Exception as e:
            logger.error(f"Failed to calculate simulation costs: {e}")
            return {}
            
    async def analyze_cost_trends(
        self,
        project_id: Optional[str] = None,
        simulation_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict:
        """Analyze cost trends"""
        try:
            estimates = []
            if project_id:
                estimates = await self.list_estimates(project_id=project_id)
            elif simulation_id:
                estimates = await self.list_estimates(simulation_id=simulation_id)
            else:
                return {}
                
            if start_date:
                estimates = [e for e in estimates if e.end_date >= start_date]
            if end_date:
                estimates = [e for e in estimates if e.start_date <= end_date]
                
            # Calculate trends
            trends = {
                "total_estimates": len(estimates),
                "cost_types": {},
                "categories": {},
                "monthly_totals": {},
                "confidence_levels": {
                    "high": len([e for e in estimates if e.confidence_level >= 0.8]),
                    "medium": len([e for e in estimates if 0.5 <= e.confidence_level < 0.8]),
                    "low": len([e for e in estimates if e.confidence_level < 0.5])
                }
            }
            
            # Analyze by cost type
            for cost_type in CostType:
                type_estimates = [e for e in estimates if e.cost_type == cost_type]
                if type_estimates:
                    trends["cost_types"][cost_type.value] = {
                        "count": len(type_estimates),
                        "total_amount": sum(e.breakdown.total_amount for e in type_estimates),
                        "average_amount": sum(e.breakdown.total_amount for e in type_estimates) / len(type_estimates)
                    }
                    
            # Analyze by category
            for category in CostCategory:
                category_estimates = [e for e in estimates if e.category == category]
                if category_estimates:
                    trends["categories"][category.value] = {
                        "count": len(category_estimates),
                        "total_amount": sum(e.breakdown.total_amount for e in category_estimates),
                        "average_amount": sum(e.breakdown.total_amount for e in category_estimates) / len(category_estimates)
                    }
                    
            return trends
        except Exception as e:
            logger.error(f"Failed to analyze cost trends: {e}")
            return {}
            
    async def check_health(self) -> Dict:
        """Check service health"""
        return {
            "status": "healthy",
            "estimate_count": len(self.estimates),
            "actual_count": len(self.actuals)
        } 