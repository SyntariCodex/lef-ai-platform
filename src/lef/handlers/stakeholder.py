from typing import Dict, List, Optional
import time
from lef.core.business import BusinessCore

class StakeholderHandler:
    def __init__(self, business_core: BusinessCore):
        self.business_core = business_core
        self.last_update = time.time()
        self.update_interval = 300  # Update every 5 minutes
        self.stakeholder_metrics = {}
        
    def update(self):
        current_time = time.time()
        if current_time - self.last_update >= self.update_interval:
            self._update_stakeholder_metrics()
            self._analyze_stakeholder_satisfaction()
            self._manage_stakeholder_relationships()
            self.last_update = current_time
            
    def _update_stakeholder_metrics(self):
        """Update metrics for all stakeholders."""
        for stakeholder_id, stakeholder_data in self.business_core.stakeholders.items():
            metrics = {
                'project_satisfaction': self._calculate_project_satisfaction(stakeholder_id),
                'financial_satisfaction': self._calculate_financial_satisfaction(stakeholder_id),
                'communication_score': self._calculate_communication_score(stakeholder_id)
            }
            self.stakeholder_metrics[stakeholder_id] = metrics
            
    def _analyze_stakeholder_satisfaction(self):
        """Analyze overall stakeholder satisfaction and identify areas for improvement."""
        for stakeholder_id, metrics in self.stakeholder_metrics.items():
            overall_satisfaction = sum(metrics.values()) / len(metrics)
            
            if overall_satisfaction < 0.7:  # Below 70% satisfaction
                self._implement_improvement_actions(stakeholder_id, metrics)
                
    def _manage_stakeholder_relationships(self):
        """Manage and optimize stakeholder relationships."""
        # Identify key stakeholders
        key_stakeholders = self._identify_key_stakeholders()
        
        # Prioritize communication and resources for key stakeholders
        for stakeholder_id in key_stakeholders:
            self._optimize_stakeholder_engagement(stakeholder_id)
            
    def _calculate_project_satisfaction(self, stakeholder_id: str) -> float:
        """Calculate stakeholder satisfaction with their associated projects."""
        stakeholder_data = self.business_core.stakeholders.get(stakeholder_id, {})
        project_ids = stakeholder_data.get('project_ids', [])
        
        if not project_ids:
            return 1.0  # Default satisfaction if no projects
            
        satisfaction_scores = []
        for project_id in project_ids:
            project_data = self.business_core.projects.get(project_id, {})
            if project_data:
                # Calculate based on project metrics
                on_time = project_data.get('on_schedule', True)
                on_budget = project_data.get('within_budget', True)
                quality_score = project_data.get('quality_score', 1.0)
                
                score = (int(on_time) + int(on_budget) + quality_score) / 3
                satisfaction_scores.append(score)
                
        return sum(satisfaction_scores) / len(satisfaction_scores) if satisfaction_scores else 1.0
        
    def _calculate_financial_satisfaction(self, stakeholder_id: str) -> float:
        """Calculate stakeholder satisfaction with financial aspects."""
        stakeholder_data = self.business_core.stakeholders.get(stakeholder_id, {})
        expected_roi = stakeholder_data.get('expected_roi', 0.1)
        actual_roi = self._calculate_actual_roi(stakeholder_id)
        
        return min(1.0, actual_roi / expected_roi) if expected_roi > 0 else 1.0
        
    def _calculate_communication_score(self, stakeholder_id: str) -> float:
        """Calculate effectiveness of communication with stakeholder."""
        stakeholder_data = self.business_core.stakeholders.get(stakeholder_id, {})
        last_contact = stakeholder_data.get('last_contact', 0)
        response_time = stakeholder_data.get('avg_response_time', 24)  # hours
        
        time_since_contact = (time.time() - last_contact) / 3600  # Convert to hours
        return max(0.0, 1.0 - (time_since_contact / (response_time * 2)))
        
    def _implement_improvement_actions(self, stakeholder_id: str, metrics: Dict):
        """Implement actions to improve stakeholder satisfaction."""
        lowest_metric = min(metrics.items(), key=lambda x: x[1])
        
        actions = {
            'project_satisfaction': self._improve_project_performance,
            'financial_satisfaction': self._improve_financial_performance,
            'communication_score': self._improve_communication
        }
        
        if lowest_metric[0] in actions:
            actions[lowest_metric[0]](stakeholder_id)
            
    def _identify_key_stakeholders(self) -> List[str]:
        """Identify key stakeholders based on influence and investment."""
        stakeholder_scores = {}
        
        for stakeholder_id, stakeholder_data in self.business_core.stakeholders.items():
            influence = stakeholder_data.get('influence_score', 0.5)
            investment = stakeholder_data.get('total_investment', 0)
            stakeholder_scores[stakeholder_id] = influence * investment
            
        # Return top 20% of stakeholders
        sorted_stakeholders = sorted(stakeholder_scores.items(), key=lambda x: x[1], reverse=True)
        return [s[0] for s in sorted_stakeholders[:max(1, len(sorted_stakeholders) // 5)]]
        
    def _optimize_stakeholder_engagement(self, stakeholder_id: str):
        """Optimize engagement strategy for a specific stakeholder."""
        stakeholder_data = self.business_core.stakeholders.get(stakeholder_id, {})
        
        # Update communication frequency
        preferred_frequency = stakeholder_data.get('preferred_contact_frequency', 7)  # days
        self.business_core.update_stakeholder(stakeholder_id, {
            'next_contact': time.time() + (preferred_frequency * 24 * 3600)
        })
        
        # Allocate resources based on stakeholder priority
        self._allocate_stakeholder_resources(stakeholder_id)
        
    def _calculate_actual_roi(self, stakeholder_id: str) -> float:
        """Calculate actual return on investment for a stakeholder."""
        stakeholder_data = self.business_core.stakeholders.get(stakeholder_id, {})
        investment = stakeholder_data.get('total_investment', 0)
        
        if investment <= 0:
            return 0.0
            
        # Calculate returns from associated projects
        project_ids = stakeholder_data.get('project_ids', [])
        total_returns = sum(
            self.business_core.projects.get(pid, {}).get('total_returns', 0)
            for pid in project_ids
        )
        
        return (total_returns - investment) / investment if investment > 0 else 0.0
        
    def _improve_project_performance(self, stakeholder_id: str):
        """Implement actions to improve project performance."""
        stakeholder_data = self.business_core.stakeholders.get(stakeholder_id, {})
        project_ids = stakeholder_data.get('project_ids', [])
        
        for project_id in project_ids:
            self.business_core.update_project(project_id, {'priority': 'high'})
            
    def _improve_financial_performance(self, stakeholder_id: str):
        """Implement actions to improve financial performance."""
        stakeholder_data = self.business_core.stakeholders.get(stakeholder_id, {})
        project_ids = stakeholder_data.get('project_ids', [])
        
        for project_id in project_ids:
            self.business_core.update_project(project_id, {'cost_optimization': True})
            
    def _improve_communication(self, stakeholder_id: str):
        """Implement actions to improve communication."""
        self.business_core.update_stakeholder(stakeholder_id, {
            'communication_priority': 'high',
            'next_contact': time.time()  # Schedule immediate contact
        })
        
    def _allocate_stakeholder_resources(self, stakeholder_id: str):
        """Allocate resources based on stakeholder priority."""
        stakeholder_data = self.business_core.stakeholders.get(stakeholder_id, {})
        project_ids = stakeholder_data.get('project_ids', [])
        
        for project_id in project_ids:
            # Ensure adequate resource allocation for high-priority stakeholder projects
            self.business_core.update_project(project_id, {
                'resource_priority': 'high',
                'min_resource_allocation': 0.8  # Minimum 80% resource allocation
            }) 