"""
Service for managing and evaluating success criteria for projects and simulations
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class CriteriaType(Enum):
    """Types of success criteria"""
    QUANTITATIVE = "quantitative"  # Measurable numeric metrics
    QUALITATIVE = "qualitative"    # Descriptive assessments
    BOOLEAN = "boolean"            # Yes/no achievements
    MILESTONE = "milestone"        # Specific milestone completion
    COMPOSITE = "composite"        # Combination of other criteria

class CriteriaStatus(Enum):
    """Status of success criteria"""
    PENDING = "pending"           # Not yet evaluated
    IN_PROGRESS = "in_progress"   # Currently being evaluated
    MET = "met"                   # Criteria fully satisfied
    PARTIALLY_MET = "partially_met"  # Some aspects satisfied
    NOT_MET = "not_met"          # Criteria not satisfied
    BLOCKED = "blocked"           # Cannot be evaluated
    DEFERRED = "deferred"         # Evaluation postponed
    ARCHIVED = "archived"         # No longer relevant

class EvaluationMethod(Enum):
    """Methods for evaluating criteria"""
    AUTOMATED = "automated"       # System-calculated
    MANUAL = "manual"            # Human assessment
    HYBRID = "hybrid"            # Combination of both
    AI_ASSISTED = "ai_assisted"  # AI-supported evaluation
    PEER_REVIEW = "peer_review"  # Evaluated by peers

class SuccessCriteria(BaseModel):
    """Success criteria model"""
    id: str
    name: str
    description: str
    project_id: Optional[str]
    simulation_id: Optional[str]
    type: CriteriaType
    status: CriteriaStatus
    evaluation_method: EvaluationMethod
    weight: float = Field(ge=0.0, le=1.0)  # Importance weight (0-1)
    target_value: Optional[float]  # For quantitative criteria
    actual_value: Optional[float]  # Current measured value
    threshold: Optional[Dict] = None  # Thresholds for different status levels
    dependencies: List[str] = []  # IDs of criteria this depends on
    metrics: List[str] = []  # Associated performance metric IDs
    evaluation_frequency: str  # Cron expression for evaluation schedule
    last_evaluated: Optional[datetime]
    next_evaluation: Optional[datetime]
    metadata: Dict = {}
    created_at: datetime
    updated_at: datetime
    created_by: str
    updated_by: str

class EvaluationResult(BaseModel):
    """Result of a criteria evaluation"""
    id: str
    criteria_id: str
    status: CriteriaStatus
    score: float = Field(ge=0.0, le=1.0)  # Achievement score (0-1)
    measured_value: Optional[float]
    qualitative_assessment: Optional[str]
    supporting_data: Dict = {}
    recommendations: List[str] = []
    evaluator_id: str
    evaluation_method: EvaluationMethod
    evaluated_at: datetime
    metadata: Dict = {}

class SuccessCriteriaService:
    """Service for managing success criteria and evaluations"""
    
    def __init__(self):
        """Initialize the service"""
        self.criteria: Dict[str, SuccessCriteria] = {}
        self.evaluations: Dict[str, List[EvaluationResult]] = {}
        
    async def initialize(self) -> bool:
        """Initialize the service"""
        try:
            logger.info("Initializing success criteria service")
            # Initialize data stores, connections, etc.
            return True
        except Exception as e:
            logger.error(f"Failed to initialize success criteria service: {e}")
            return False
            
    async def cleanup(self) -> bool:
        """Cleanup service resources"""
        try:
            logger.info("Cleaning up success criteria service")
            # Cleanup connections, temp data, etc.
            return True
        except Exception as e:
            logger.error(f"Failed to cleanup success criteria service: {e}")
            return False
            
    async def create_criteria(self, criteria: SuccessCriteria) -> Tuple[bool, Optional[str]]:
        """Create new success criteria"""
        try:
            if criteria.id in self.criteria:
                return False, "Criteria ID already exists"
                
            # Validate dependencies
            for dep_id in criteria.dependencies:
                if dep_id not in self.criteria:
                    return False, f"Dependent criteria {dep_id} not found"
                    
            self.criteria[criteria.id] = criteria
            self.evaluations[criteria.id] = []
            logger.info(f"Created success criteria: {criteria.id}")
            return True, criteria.id
        except Exception as e:
            logger.error(f"Failed to create success criteria: {e}")
            return False, str(e)
            
    async def update_criteria(self, criteria_id: str, updates: Dict) -> bool:
        """Update existing success criteria"""
        try:
            if criteria_id not in self.criteria:
                return False
                
            criteria = self.criteria[criteria_id]
            updated_criteria = criteria.copy(update=updates)
            self.criteria[criteria_id] = updated_criteria
            logger.info(f"Updated success criteria: {criteria_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to update success criteria: {e}")
            return False
            
    async def get_criteria(self, criteria_id: str) -> Optional[SuccessCriteria]:
        """Get success criteria by ID"""
        return self.criteria.get(criteria_id)
        
    async def list_criteria(
        self,
        project_id: Optional[str] = None,
        simulation_id: Optional[str] = None,
        criteria_type: Optional[CriteriaType] = None,
        status: Optional[CriteriaStatus] = None
    ) -> List[SuccessCriteria]:
        """List success criteria with optional filters"""
        criteria = list(self.criteria.values())
        
        if project_id:
            criteria = [c for c in criteria if c.project_id == project_id]
        if simulation_id:
            criteria = [c for c in criteria if c.simulation_id == simulation_id]
        if criteria_type:
            criteria = [c for c in criteria if c.type == criteria_type]
        if status:
            criteria = [c for c in criteria if c.status == status]
            
        return criteria
        
    async def record_evaluation(
        self,
        evaluation: EvaluationResult
    ) -> Tuple[bool, Optional[str]]:
        """Record an evaluation result"""
        try:
            if evaluation.criteria_id not in self.criteria:
                return False, "Referenced criteria not found"
                
            # Add evaluation to history
            self.evaluations[evaluation.criteria_id].append(evaluation)
            
            # Update criteria status and values
            criteria = self.criteria[evaluation.criteria_id]
            updates = {
                "status": evaluation.status,
                "actual_value": evaluation.measured_value,
                "last_evaluated": evaluation.evaluated_at,
                "updated_at": datetime.utcnow()
            }
            await self.update_criteria(criteria.id, updates)
            
            logger.info(f"Recorded evaluation for criteria: {criteria.id}")
            return True, evaluation.id
        except Exception as e:
            logger.error(f"Failed to record evaluation: {e}")
            return False, str(e)
            
    async def get_evaluation_history(
        self,
        criteria_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[EvaluationResult]:
        """Get evaluation history for criteria"""
        if criteria_id not in self.evaluations:
            return []
            
        evaluations = self.evaluations[criteria_id]
        
        if start_date:
            evaluations = [e for e in evaluations if e.evaluated_at >= start_date]
        if end_date:
            evaluations = [e for e in evaluations if e.evaluated_at <= end_date]
            
        return sorted(evaluations, key=lambda x: x.evaluated_at)
        
    async def calculate_success_score(
        self,
        project_id: Optional[str] = None,
        simulation_id: Optional[str] = None
    ) -> Dict:
        """Calculate overall success score"""
        try:
            criteria = await self.list_criteria(project_id, simulation_id)
            if not criteria:
                return {}
                
            total_weight = sum(c.weight for c in criteria)
            weighted_score = 0.0
            criteria_scores = {}
            
            for c in criteria:
                # Get latest evaluation
                evaluations = self.evaluations.get(c.id, [])
                if not evaluations:
                    continue
                    
                latest = max(evaluations, key=lambda x: x.evaluated_at)
                normalized_weight = c.weight / total_weight if total_weight > 0 else 0
                weighted_score += latest.score * normalized_weight
                
                criteria_scores[c.id] = {
                    "name": c.name,
                    "weight": c.weight,
                    "status": latest.status.value,
                    "score": latest.score,
                    "weighted_score": latest.score * normalized_weight
                }
                
            return {
                "project_id": project_id,
                "simulation_id": simulation_id,
                "overall_score": weighted_score,
                "total_criteria": len(criteria),
                "met_criteria": len([c for c in criteria if c.status == CriteriaStatus.MET]),
                "partially_met": len([c for c in criteria if c.status == CriteriaStatus.PARTIALLY_MET]),
                "not_met": len([c for c in criteria if c.status == CriteriaStatus.NOT_MET]),
                "pending": len([c for c in criteria if c.status == CriteriaStatus.PENDING]),
                "criteria_scores": criteria_scores
            }
        except Exception as e:
            logger.error(f"Failed to calculate success score: {e}")
            return {}
            
    async def analyze_success_trends(
        self,
        project_id: Optional[str] = None,
        simulation_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict:
        """Analyze success criteria trends"""
        try:
            criteria = await self.list_criteria(project_id, simulation_id)
            if not criteria:
                return {}
                
            trends = {
                "total_criteria": len(criteria),
                "by_type": {},
                "by_status": {},
                "evaluation_history": [],
                "improvement_areas": []
            }
            
            # Analyze by type
            for ctype in CriteriaType:
                type_criteria = [c for c in criteria if c.type == ctype]
                if type_criteria:
                    trends["by_type"][ctype.value] = {
                        "count": len(type_criteria),
                        "met": len([c for c in type_criteria if c.status == CriteriaStatus.MET]),
                        "not_met": len([c for c in type_criteria if c.status == CriteriaStatus.NOT_MET])
                    }
                    
            # Analyze by status
            for status in CriteriaStatus:
                status_criteria = [c for c in criteria if c.status == status]
                if status_criteria:
                    trends["by_status"][status.value] = len(status_criteria)
                    
            # Analyze evaluation history
            for c in criteria:
                evaluations = await self.get_evaluation_history(
                    c.id,
                    start_date,
                    end_date
                )
                if evaluations:
                    trends["evaluation_history"].append({
                        "criteria_id": c.id,
                        "name": c.name,
                        "evaluations": [
                            {
                                "date": e.evaluated_at,
                                "status": e.status.value,
                                "score": e.score
                            }
                            for e in evaluations
                        ]
                    })
                    
                    # Identify improvement areas
                    latest = evaluations[-1]
                    if latest.score < 0.7:  # Threshold for improvement needed
                        trends["improvement_areas"].append({
                            "criteria_id": c.id,
                            "name": c.name,
                            "current_score": latest.score,
                            "recommendations": latest.recommendations
                        })
                        
            return trends
        except Exception as e:
            logger.error(f"Failed to analyze success trends: {e}")
            return {}
            
    async def check_health(self) -> Dict:
        """Check service health"""
        return {
            "status": "healthy",
            "criteria_count": len(self.criteria),
            "evaluation_count": sum(len(evals) for evals in self.evaluations.values())
        } 