"""
Risk Analysis Service for managing project risk analysis and assessment
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from ..services.logging_service import LoggingService
from ..services.simulation_service import SimulationService

logger = logging.getLogger(__name__)

class RiskLevel(str, Enum):
    """Risk level"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class RiskCategory(str, Enum):
    """Risk category"""
    TECHNICAL = "technical"
    BUSINESS = "business"
    OPERATIONAL = "operational"
    FINANCIAL = "financial"
    LEGAL = "legal"
    ENVIRONMENTAL = "environmental"
    SECURITY = "security"
    COMPLIANCE = "compliance"

class RiskImpact(str, Enum):
    """Risk impact"""
    NEGLIGIBLE = "negligible"
    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"
    CATASTROPHIC = "catastrophic"

class RiskProbability(str, Enum):
    """Risk probability"""
    RARE = "rare"
    UNLIKELY = "unlikely"
    POSSIBLE = "possible"
    LIKELY = "likely"
    ALMOST_CERTAIN = "almost_certain"

class Risk(BaseModel):
    """Risk definition"""
    id: str
    name: str
    description: str
    category: RiskCategory
    level: RiskLevel
    impact: RiskImpact
    probability: RiskProbability
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    mitigation_strategy: Optional[str] = None
    mitigation_status: Optional[str] = None
    mitigation_effort: Optional[str] = None
    mitigation_cost: Optional[float] = None
    residual_risk: Optional[RiskLevel] = None
    dependencies: List[str] = Field(default_factory=list)
    affected_components: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class RiskAssessment(BaseModel):
    """Risk assessment"""
    id: str
    simulation_id: str
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    risks: List[Risk] = Field(default_factory=list)
    overall_risk_level: RiskLevel
    risk_score: float
    risk_trend: str
    recommendations: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class RiskAnalysisService:
    """Service for managing risk analysis"""
    
    def __init__(self):
        self.logging_service = LoggingService()
        self.simulation_service = SimulationService()
        self.risks: Dict[str, Risk] = {}
        self.risk_assessments: Dict[str, RiskAssessment] = {}
        self.risk_history: Dict[str, List[RiskAssessment]] = {}
        
    async def initialize(self):
        """Initialize the risk analysis service"""
        try:
            await self.logging_service.initialize()
            await self.simulation_service.initialize()
            logger.info("Risk Analysis Service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Risk Analysis Service: {e}")
            await self.logging_service.log_message(
                "error",
                f"Failed to initialize Risk Analysis Service: {e}"
            )
            raise
            
    async def create_risk(self, risk: Risk) -> bool:
        """Create a new risk"""
        try:
            if risk.id in self.risks:
                raise ValueError(f"Risk {risk.id} already exists")
                
            # Store risk
            self.risks[risk.id] = risk
            
            await self.logging_service.log_message(
                "info",
                f"Created new risk: {risk.id}",
                details={
                    "name": risk.name,
                    "category": risk.category,
                    "level": risk.level,
                    "created_by": risk.created_by
                }
            )
            return True
            
        except Exception as e:
            logger.error(f"Failed to create risk {risk.id}: {e}")
            await self.logging_service.log_message(
                "error",
                f"Failed to create risk {risk.id}: {e}"
            )
            return False
            
    async def update_risk(self, risk_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing risk"""
        try:
            if risk_id not in self.risks:
                raise ValueError(f"Risk {risk_id} not found")
                
            risk = self.risks[risk_id]
            
            # Update risk
            for key, value in updates.items():
                if hasattr(risk, key):
                    setattr(risk, key, value)
                    
            risk.updated_at = datetime.utcnow()
            
            await self.logging_service.log_message(
                "info",
                f"Updated risk: {risk_id}",
                details={"updated_by": updates.get("updated_by", "system")}
            )
            return True
            
        except Exception as e:
            logger.error(f"Failed to update risk {risk_id}: {e}")
            await self.logging_service.log_message(
                "error",
                f"Failed to update risk {risk_id}: {e}"
            )
            return False
            
    async def get_risk(self, risk_id: str) -> Optional[Risk]:
        """Get a risk by ID"""
        try:
            if risk_id not in self.risks:
                raise ValueError(f"Risk {risk_id} not found")
                
            return self.risks[risk_id]
            
        except Exception as e:
            logger.error(f"Failed to get risk {risk_id}: {e}")
            await self.logging_service.log_message(
                "error",
                f"Failed to get risk {risk_id}: {e}"
            )
            return None
            
    async def list_risks(
        self,
        category: Optional[RiskCategory] = None,
        level: Optional[RiskLevel] = None,
        impact: Optional[RiskImpact] = None,
        probability: Optional[RiskProbability] = None
    ) -> List[Dict[str, Any]]:
        """List risks with optional filters"""
        try:
            risks = []
            for risk in self.risks.values():
                # Apply filters
                if category and risk.category != category:
                    continue
                if level and risk.level != level:
                    continue
                if impact and risk.impact != impact:
                    continue
                if probability and risk.probability != probability:
                    continue
                    
                risks.append({
                    "id": risk.id,
                    "name": risk.name,
                    "description": risk.description,
                    "category": risk.category,
                    "level": risk.level,
                    "impact": risk.impact,
                    "probability": risk.probability,
                    "mitigation_status": risk.mitigation_status,
                    "residual_risk": risk.residual_risk
                })
                
            return risks
            
        except Exception as e:
            logger.error(f"Failed to list risks: {e}")
            await self.logging_service.log_message(
                "error",
                f"Failed to list risks: {e}"
            )
            return []
            
    async def create_risk_assessment(
        self,
        simulation_id: str,
        risks: List[Risk],
        user_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """Create a new risk assessment"""
        try:
            # Get simulation
            simulation = await self.simulation_service.get_simulation(simulation_id)
            if not simulation:
                raise ValueError(f"Simulation {simulation_id} not found")
                
            # Calculate overall risk level and score
            overall_risk_level = self._calculate_overall_risk_level(risks)
            risk_score = self._calculate_risk_score(risks)
            risk_trend = self._calculate_risk_trend(simulation_id)
            
            # Create assessment
            assessment = RiskAssessment(
                id=f"assessment_{len(self.risk_assessments) + 1}",
                simulation_id=simulation_id,
                created_by=user_id,
                risks=risks,
                overall_risk_level=overall_risk_level,
                risk_score=risk_score,
                risk_trend=risk_trend,
                recommendations=self._generate_recommendations(risks),
                metadata=metadata or {}
            )
            
            # Store assessment
            self.risk_assessments[assessment.id] = assessment
            if simulation_id not in self.risk_history:
                self.risk_history[simulation_id] = []
            self.risk_history[simulation_id].append(assessment)
            
            await self.logging_service.log_message(
                "info",
                f"Created new risk assessment: {assessment.id}",
                details={
                    "simulation_id": simulation_id,
                    "overall_risk_level": overall_risk_level,
                    "risk_score": risk_score,
                    "created_by": user_id
                }
            )
            return assessment.id
            
        except Exception as e:
            logger.error(f"Failed to create risk assessment: {e}")
            await self.logging_service.log_message(
                "error",
                f"Failed to create risk assessment: {e}"
            )
            return None
            
    async def get_risk_assessment(self, assessment_id: str) -> Optional[RiskAssessment]:
        """Get a risk assessment by ID"""
        try:
            if assessment_id not in self.risk_assessments:
                raise ValueError(f"Risk assessment {assessment_id} not found")
                
            return self.risk_assessments[assessment_id]
            
        except Exception as e:
            logger.error(f"Failed to get risk assessment {assessment_id}: {e}")
            await self.logging_service.log_message(
                "error",
                f"Failed to get risk assessment {assessment_id}: {e}"
            )
            return None
            
    async def list_risk_assessments(
        self,
        simulation_id: str,
        user_id: str
    ) -> List[Dict[str, Any]]:
        """List risk assessments for a simulation"""
        try:
            if simulation_id not in self.risk_history:
                return []
                
            assessments = []
            for assessment in self.risk_history[simulation_id]:
                assessments.append({
                    "id": assessment.id,
                    "created_at": assessment.created_at,
                    "updated_at": assessment.updated_at,
                    "overall_risk_level": assessment.overall_risk_level,
                    "risk_score": assessment.risk_score,
                    "risk_trend": assessment.risk_trend,
                    "number_of_risks": len(assessment.risks)
                })
                
            return assessments
            
        except Exception as e:
            logger.error(f"Failed to list risk assessments: {e}")
            await self.logging_service.log_message(
                "error",
                f"Failed to list risk assessments: {e}"
            )
            return []
            
    def _calculate_overall_risk_level(self, risks: List[Risk]) -> RiskLevel:
        """Calculate overall risk level from list of risks"""
        if not risks:
            return RiskLevel.LOW
            
        # Calculate weighted average of risk levels
        risk_levels = {
            RiskLevel.LOW: 1,
            RiskLevel.MEDIUM: 2,
            RiskLevel.HIGH: 3,
            RiskLevel.CRITICAL: 4
        }
        
        total_weight = 0
        weighted_sum = 0
        
        for risk in risks:
            weight = risk_levels[risk.level]
            total_weight += weight
            weighted_sum += weight
            
        average = weighted_sum / total_weight
        
        # Map average to risk level
        if average <= 1.5:
            return RiskLevel.LOW
        elif average <= 2.5:
            return RiskLevel.MEDIUM
        elif average <= 3.5:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL
            
    def _calculate_risk_score(self, risks: List[Risk]) -> float:
        """Calculate risk score from list of risks"""
        if not risks:
            return 0.0
            
        # Calculate weighted average of impact and probability
        impact_weights = {
            RiskImpact.NEGLIGIBLE: 1,
            RiskImpact.MINOR: 2,
            RiskImpact.MODERATE: 3,
            RiskImpact.MAJOR: 4,
            RiskImpact.CATASTROPHIC: 5
        }
        
        probability_weights = {
            RiskProbability.RARE: 1,
            RiskProbability.UNLIKELY: 2,
            RiskProbability.POSSIBLE: 3,
            RiskProbability.LIKELY: 4,
            RiskProbability.ALMOST_CERTAIN: 5
        }
        
        total_score = 0
        for risk in risks:
            impact_score = impact_weights[risk.impact]
            probability_score = probability_weights[risk.probability]
            total_score += (impact_score * probability_score) / 25  # Normalize to 0-1
            
        return total_score / len(risks)
        
    def _calculate_risk_trend(self, simulation_id: str) -> str:
        """Calculate risk trend for a simulation"""
        if simulation_id not in self.risk_history:
            return "stable"
            
        assessments = self.risk_history[simulation_id]
        if len(assessments) < 2:
            return "stable"
            
        # Compare last two assessments
        last_two = assessments[-2:]
        if last_two[1].risk_score > last_two[0].risk_score:
            return "increasing"
        elif last_two[1].risk_score < last_two[0].risk_score:
            return "decreasing"
        else:
            return "stable"
            
    def _generate_recommendations(self, risks: List[Risk]) -> List[str]:
        """Generate risk mitigation recommendations"""
        recommendations = []
        
        # Sort risks by level and impact
        sorted_risks = sorted(
            risks,
            key=lambda x: (x.level, x.impact),
            reverse=True
        )
        
        # Generate recommendations for high and critical risks
        for risk in sorted_risks:
            if risk.level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                recommendations.append(
                    f"Develop and implement mitigation strategy for {risk.name} "
                    f"({risk.category.value} risk)"
                )
                
        return recommendations 