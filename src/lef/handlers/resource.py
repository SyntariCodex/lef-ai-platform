from typing import Dict, List, Optional
import time
from lef.core.business import BusinessCore

class ResourceHandler:
    def __init__(self, business_core: BusinessCore):
        self.business_core = business_core
        self.last_update = time.time()
        self.update_interval = 60  # Update every minute
        self.resource_metrics = {}
        
    def update(self):
        current_time = time.time()
        if current_time - self.last_update >= self.update_interval:
            self._update_resource_metrics()
            self._optimize_resource_allocation()
            self._manage_resource_scaling()
            self.last_update = current_time
            
    def _update_resource_metrics(self):
        """Update metrics for all resources."""
        for resource_id, resource_data in self.business_core.resources.items():
            metrics = {
                'utilization': self._calculate_utilization(resource_id),
                'efficiency': self._calculate_efficiency(resource_id),
                'cost_effectiveness': self._calculate_cost_effectiveness(resource_id)
            }
            self.resource_metrics[resource_id] = metrics
            
    def _optimize_resource_allocation(self):
        """Optimize allocation of resources across projects."""
        # Get all active projects and their resource requirements
        project_requirements = self._get_project_requirements()
        
        # Sort projects by priority
        sorted_projects = sorted(
            project_requirements.items(),
            key=lambda x: x[1].get('priority', 0),
            reverse=True
        )
        
        # Allocate resources based on priority
        for project_id, requirements in sorted_projects:
            self._allocate_resources_to_project(project_id, requirements)
            
    def _manage_resource_scaling(self):
        """Manage scaling of resources based on demand and performance."""
        total_utilization = self._calculate_total_utilization()
        
        if total_utilization > 0.8:  # Over 80% utilization
            self._scale_up_resources()
        elif total_utilization < 0.4:  # Under 40% utilization
            self._scale_down_resources()
            
    def _calculate_utilization(self, resource_id: str) -> float:
        """Calculate utilization rate for a specific resource."""
        resource_data = self.business_core.resources.get(resource_id, {})
        allocated_time = resource_data.get('allocated_time', 0)
        available_time = resource_data.get('available_time', 40)  # Default 40 hours/week
        
        return min(1.0, allocated_time / available_time) if available_time > 0 else 0.0
        
    def _calculate_efficiency(self, resource_id: str) -> float:
        """Calculate efficiency score for a specific resource."""
        resource_data = self.business_core.resources.get(resource_id, {})
        completed_tasks = resource_data.get('completed_tasks', 0)
        total_tasks = resource_data.get('total_tasks', 1)
        quality_score = resource_data.get('quality_score', 1.0)
        
        completion_rate = completed_tasks / total_tasks if total_tasks > 0 else 1.0
        return completion_rate * quality_score
        
    def _calculate_cost_effectiveness(self, resource_id: str) -> float:
        """Calculate cost effectiveness for a specific resource."""
        resource_data = self.business_core.resources.get(resource_id, {})
        value_generated = resource_data.get('value_generated', 0)
        cost = resource_data.get('cost', 1)
        
        return value_generated / cost if cost > 0 else 0.0
        
    def _get_project_requirements(self) -> Dict:
        """Get resource requirements for all active projects."""
        requirements = {}
        
        for project_id, project_data in self.business_core.projects.items():
            if project_data.get('status') == 'active':
                requirements[project_id] = {
                    'priority': project_data.get('priority', 0),
                    'resource_types': project_data.get('required_resources', []),
                    'min_resources': project_data.get('min_resources', 1),
                    'max_resources': project_data.get('max_resources', float('inf'))
                }
                
        return requirements
        
    def _allocate_resources_to_project(self, project_id: str, requirements: Dict):
        """Allocate resources to a specific project based on requirements."""
        current_allocation = self._get_current_allocation(project_id)
        
        if len(current_allocation) < requirements['min_resources']:
            # Need to allocate more resources
            available_resources = self._find_available_resources(
                requirements['resource_types'],
                requirements['max_resources'] - len(current_allocation)
            )
            
            for resource_id in available_resources:
                self.business_core.update_resource(resource_id, {
                    'project_id': project_id,
                    'status': 'allocated'
                })
                
    def _get_current_allocation(self, project_id: str) -> List[str]:
        """Get list of resources currently allocated to a project."""
        return [
            resource_id for resource_id, resource_data
            in self.business_core.resources.items()
            if resource_data.get('project_id') == project_id
        ]
        
    def _find_available_resources(self, required_types: List[str], max_count: int) -> List[str]:
        """Find available resources matching required types."""
        available_resources = []
        
        for resource_id, resource_data in self.business_core.resources.items():
            if (len(available_resources) >= max_count or
                resource_data.get('status') != 'available' or
                resource_data.get('type') not in required_types):
                continue
                
            available_resources.append(resource_id)
            
        return available_resources
        
    def _calculate_total_utilization(self) -> float:
        """Calculate total utilization across all resources."""
        if not self.resource_metrics:
            return 0.0
            
        total_utilization = sum(
            metrics['utilization']
            for metrics in self.resource_metrics.values()
        )
        return total_utilization / len(self.resource_metrics)
        
    def _scale_up_resources(self):
        """Scale up resources based on demand."""
        # Identify resource types needed
        required_types = self._identify_resource_needs()
        
        for resource_type in required_types:
            # Create new resource request
            self.business_core.add_resource({
                'type': resource_type,
                'status': 'pending',
                'cost': self._estimate_resource_cost(resource_type)
            })
            
    def _scale_down_resources(self):
        """Scale down underutilized resources."""
        for resource_id, metrics in self.resource_metrics.items():
            if (metrics['utilization'] < 0.3 and  # Less than 30% utilization
                metrics['cost_effectiveness'] < 0.5):  # Poor cost effectiveness
                self.business_core.update_resource(resource_id, {'status': 'decommission'})
                
    def _identify_resource_needs(self) -> List[str]:
        """Identify types of resources needed based on demand."""
        resource_demand = {}
        
        for project_id, project_data in self.business_core.projects.items():
            if project_data.get('status') == 'active':
                for resource_type in project_data.get('required_resources', []):
                    resource_demand[resource_type] = resource_demand.get(resource_type, 0) + 1
                    
        # Return types where demand exceeds current capacity
        return [
            resource_type for resource_type, demand in resource_demand.items()
            if demand > self._get_resource_capacity(resource_type)
        ]
        
    def _get_resource_capacity(self, resource_type: str) -> int:
        """Get current capacity for a specific resource type."""
        return sum(
            1 for resource_data in self.business_core.resources.values()
            if resource_data.get('type') == resource_type
        )
        
    def _estimate_resource_cost(self, resource_type: str) -> float:
        """Estimate cost for a new resource based on type."""
        similar_resources = [
            resource_data.get('cost', 0)
            for resource_data in self.business_core.resources.values()
            if resource_data.get('type') == resource_type
        ]
        
        return sum(similar_resources) / len(similar_resources) if similar_resources else 0.0 