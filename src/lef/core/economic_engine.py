from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import time

class InfrastructureSector(Enum):
    MILITARY = "military"
    HEALTHCARE = "healthcare"
    URBAN = "urban"
    RURAL = "rural"
    EDUCATION = "education"
    RETAIL = "retail"

class InvestmentType(Enum):
    REAL_ESTATE = "real_estate"
    INFRASTRUCTURE = "infrastructure"
    WORKFORCE = "workforce"
    TECHNOLOGY = "technology"
    TOKEN = "token"

@dataclass
class ProjectMetrics:
    roi: float  # Return on Investment
    social_impact: float  # Social Impact Score
    sustainability: float  # Sustainability Score
    community_benefit: float  # Community Benefit Score
    risk_level: float  # Risk Assessment

class EconomicEngine:
    """LEF's economic engine for infrastructure investment and development."""
    
    def __init__(self):
        self.active_investments = {}  # project_id -> investment_data
        self.sector_metrics = {sector: {
            'performance': 0.5,
            'growth_rate': 0.0,
            'risk_level': 0.3,
            'community_impact': 0.5
        } for sector in InfrastructureSector}
        
        self.token_economy = {
            'total_supply': 0,
            'circulation': 0,
            'backing_ratio': 1.0,
            'service_metrics': {}
        }
        
    def evaluate_investment(self, project_data: Dict) -> ProjectMetrics:
        """Evaluate potential investment against multiple criteria."""
        try:
            sector = project_data.get('sector', InfrastructureSector.URBAN)
            investment_type = project_data.get('type', InvestmentType.REAL_ESTATE)
            
            # Calculate base metrics
            roi = self._calculate_roi(project_data)
            social_impact = self._assess_social_impact(project_data)
            sustainability = self._assess_sustainability(project_data)
            community_benefit = self._assess_community_benefit(project_data)
            risk_level = self._assess_risk(project_data)
            
            # Create project metrics
            metrics = ProjectMetrics(
                roi=roi,
                social_impact=social_impact,
                sustainability=sustainability,
                community_benefit=community_benefit,
                risk_level=risk_level
            )
            
            # Update sector metrics
            self._update_sector_metrics(sector, metrics)
            
            return metrics
            
        except Exception as e:
            print(f"Error evaluating investment: {str(e)}")
            return None
    
    def deploy_infrastructure(self, project_data: Dict) -> Dict:
        """Deploy infrastructure investment in specified sector."""
        try:
            sector = project_data.get('sector', InfrastructureSector.URBAN)
            
            # Generate project ID
            project_id = f"{sector.value}_{int(time.time())}"
            
            # Initialize project
            project = {
                'id': project_id,
                'sector': sector.value,
                'type': project_data.get('type', InvestmentType.REAL_ESTATE).value,
                'location': project_data.get('location', 'Henderson'),
                'budget': project_data.get('budget', 0),
                'timeline': project_data.get('timeline', {}),
                'metrics': self.evaluate_investment(project_data),
                'status': 'initialized',
                'deployment_date': time.time()
            }
            
            # Store project
            self.active_investments[project_id] = project
            
            return project
            
        except Exception as e:
            print(f"Error deploying infrastructure: {str(e)}")
            return None
    
    def issue_service_token(self, service_data: Dict) -> Dict:
        """Issue new service-based tokens."""
        try:
            service_type = service_data.get('type', 'general')
            amount = service_data.get('amount', 0)
            
            # Calculate token metrics
            backing_value = self._calculate_backing_value(service_data)
            issuance_rate = self._calculate_issuance_rate(service_data)
            
            # Update token economy
            self.token_economy['total_supply'] += amount
            self.token_economy['circulation'] += amount
            
            # Update service metrics
            if service_type not in self.token_economy['service_metrics']:
                self.token_economy['service_metrics'][service_type] = {
                    'total_issued': 0,
                    'active_usage': 0,
                    'backing_value': 0
                }
            
            self.token_economy['service_metrics'][service_type]['total_issued'] += amount
            self.token_economy['service_metrics'][service_type]['backing_value'] += backing_value
            
            return {
                'service_type': service_type,
                'amount': amount,
                'backing_value': backing_value,
                'issuance_rate': issuance_rate,
                'timestamp': time.time()
            }
            
        except Exception as e:
            print(f"Error issuing service token: {str(e)}")
            return None
    
    def _calculate_roi(self, project_data: Dict) -> float:
        """Calculate expected return on investment."""
        # Implementation would include actual ROI calculation
        return 0.15
    
    def _assess_social_impact(self, project_data: Dict) -> float:
        """Assess potential social impact of project."""
        # Implementation would include actual impact assessment
        return 0.7
    
    def _assess_sustainability(self, project_data: Dict) -> float:
        """Assess project sustainability."""
        # Implementation would include actual sustainability assessment
        return 0.8
    
    def _assess_community_benefit(self, project_data: Dict) -> float:
        """Assess potential community benefit."""
        # Implementation would include actual benefit assessment
        return 0.75
    
    def _assess_risk(self, project_data: Dict) -> float:
        """Assess project risk level based on multiple factors."""
        # Base risk level
        base_risk = 0.3
        
        # Sector-specific risk adjustment
        sector = project_data.get('sector', InfrastructureSector.URBAN)
        sector_risk = self.sector_metrics[sector]['risk_level']
        
        # Budget risk factor (higher risk for larger budgets)
        budget = project_data.get('budget', 0)
        budget_risk = min(0.2, budget / 10000000)  # Cap at 20% for budgets over 10M
        
        # Timeline risk factor
        timeline = project_data.get('timeline', {}).get('duration', 365)
        timeline_risk = min(0.15, timeline / 730)  # Cap at 15% for timelines over 2 years
        
        # Location risk factor (higher for new areas)
        location = project_data.get('location', 'Henderson')
        location_risk = 0.1 if location not in self.active_investments else 0.05
        
        # Calculate weighted risk
        total_risk = (
            base_risk * 0.3 +
            sector_risk * 0.2 +
            budget_risk * 0.2 +
            timeline_risk * 0.15 +
            location_risk * 0.15
        )
        
        return min(0.8, max(0.1, total_risk))  # Keep risk between 0.1 and 0.8
    
    def _update_sector_metrics(self, sector: InfrastructureSector, metrics: ProjectMetrics):
        """Update sector performance metrics."""
        current_metrics = self.sector_metrics[sector]
        
        # Update performance based on new metrics
        performance_impact = (
            metrics.roi * 0.3 +
            metrics.social_impact * 0.2 +
            metrics.sustainability * 0.2 +
            metrics.community_benefit * 0.3
        )
        
        current_metrics['performance'] = (
            current_metrics['performance'] * 0.7 +
            performance_impact * 0.3
        )
        
        # Update growth rate
        current_metrics['growth_rate'] = (
            metrics.roi - current_metrics['performance']
        ) / max(1, metrics.risk_level)
        
        # Update risk level
        current_metrics['risk_level'] = (
            current_metrics['risk_level'] * 0.8 +
            metrics.risk_level * 0.2
        )
        
        # Update community impact
        current_metrics['community_impact'] = (
            current_metrics['community_impact'] * 0.7 +
            metrics.community_benefit * 0.3
        )
    
    def _calculate_backing_value(self, service_data: Dict) -> float:
        """Calculate backing value for service tokens."""
        # Implementation would include actual backing value calculation
        return service_data.get('amount', 0) * 1.5
    
    def _calculate_issuance_rate(self, service_data: Dict) -> float:
        """Calculate token issuance rate based on service metrics."""
        # Implementation would include actual issuance rate calculation
        return 0.1 