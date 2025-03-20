from typing import Dict, Optional
import time
from lef.core.business import BusinessCore

class FinancialHandler:
    def __init__(self, business_core: BusinessCore):
        self.business_core = business_core
        self.last_update = time.time()
        self.update_interval = 60  # Update every minute
        
    def update(self):
        current_time = time.time()
        if current_time - self.last_update >= self.update_interval:
            self._update_financial_metrics()
            self._check_budget_constraints()
            self._optimize_resource_allocation()
            self.last_update = current_time
            
    def _update_financial_metrics(self):
        """Update financial metrics based on current business state."""
        # Calculate revenue from active projects
        for project_id, project_data in self.business_core.projects.items():
            if project_data['status'] == 'active':
                revenue = self._calculate_project_revenue(project_data)
                self.business_core.update_financial('revenue', revenue)
                
        # Calculate expenses from resources
        for resource_id, resource_data in self.business_core.resources.items():
            if resource_data['status'] == 'active':
                expense = self._calculate_resource_cost(resource_data)
                self.business_core.update_financial('expenses', expense)
                
    def _check_budget_constraints(self):
        """Check if current spending is within budget constraints."""
        total_expenses = sum(self.business_core.financials.get('expenses', {}).values())
        budget_limit = self.business_core.financials.get('budget_limit', float('inf'))
        
        if total_expenses > budget_limit:
            self._implement_cost_reduction()
            
    def _optimize_resource_allocation(self):
        """Optimize resource allocation based on financial performance."""
        profit_margin = self.business_core.financials.get('profit', 0) / max(
            sum(self.business_core.financials.get('revenue', {}).values()), 1
        )
        
        if profit_margin < 0.2:  # If profit margin is below 20%
            self._reallocate_resources()
            
    def _calculate_project_revenue(self, project_data: Dict) -> float:
        """Calculate revenue for a specific project."""
        base_rate = project_data.get('hourly_rate', 0)
        hours_worked = project_data.get('hours_worked', 0)
        return base_rate * hours_worked
        
    def _calculate_resource_cost(self, resource_data: Dict) -> float:
        """Calculate cost for a specific resource."""
        cost_rate = resource_data.get('cost_rate', 0)
        usage_hours = resource_data.get('usage_hours', 0)
        return cost_rate * usage_hours
        
    def _implement_cost_reduction(self):
        """Implement cost reduction strategies."""
        # Identify and optimize expensive resources
        for resource_id, resource_data in self.business_core.resources.items():
            if resource_data['cost_rate'] > self._calculate_average_resource_cost():
                self.business_core.update_resource(resource_id, {'status': 'review'})
                
    def _reallocate_resources(self):
        """Reallocate resources to optimize financial performance."""
        # Move resources from low-performing to high-performing projects
        project_performance = self._calculate_project_performance()
        for resource_id, resource_data in self.business_core.resources.items():
            if resource_data['project_id'] in project_performance['low_performing']:
                new_project = project_performance['high_performing'][0]
                self.business_core.update_resource(resource_id, {'project_id': new_project})
                
    def _calculate_average_resource_cost(self) -> float:
        """Calculate average resource cost across all resources."""
        costs = [r.get('cost_rate', 0) for r in self.business_core.resources.values()]
        return sum(costs) / max(len(costs), 1)
        
    def _calculate_project_performance(self) -> Dict:
        """Calculate and categorize project performance."""
        performances = {}
        for project_id, project_data in self.business_core.projects.items():
            revenue = self._calculate_project_revenue(project_data)
            cost = sum(self._calculate_resource_cost(r) for r in self.business_core.resources.values()
                      if r.get('project_id') == project_id)
            performances[project_id] = revenue - cost
            
        sorted_projects = sorted(performances.items(), key=lambda x: x[1])
        return {
            'low_performing': [p[0] for p in sorted_projects[:len(sorted_projects)//2]],
            'high_performing': [p[0] for p in sorted_projects[len(sorted_projects)//2:]]
        } 