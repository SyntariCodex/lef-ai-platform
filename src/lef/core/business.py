from typing import Dict, Optional, Any
import time
import uuid

class BusinessCore:
    """Core business operations component of the LEF system."""
    
    def __init__(self):
        self.running = False
        self.current_state = {
            'efficiency': 0.7,
            'productivity': 0.7,
            'resource_utilization': 0.7
        }
        self.metrics = {
            'start_time': None,
            'uptime': 0,
            'total_operations': 0,
            'success_rate': 0.95
        }
        self.projects = {}
        self.resources = {}
        self.stakeholders = {}
        self.financials = {
            'revenue': {},
            'expenses': {},
            'profit': 0
        }
        self.last_update = time.time()
        self.update_interval = 60  # Update every minute
        
    def start(self):
        """Start the business core operations."""
        self.running = True
        print("Business Core started")
        
    def stop(self):
        """Stop the business core operations."""
        self.running = False
        print("Business Core stopped")
        
    def update(self):
        """Update the business core state if running."""
        if not self.running:
            return
            
        current_time = time.time()
        if current_time - self.last_update >= self.update_interval:
            self._update_financials()
            self._update_projects()
            self._update_resources()
            self._update_stakeholders()
            self.last_update = current_time
            
    def add_project(self, project_data: Dict) -> str:
        """Add a new project with generated ID."""
        project_id = str(uuid.uuid4())
        project_data['status'] = 'active'
        project_data['creation_time'] = time.time()
        self.projects[project_id] = project_data
        return project_id
        
    def update_project(self, project_id: str, update_data: Dict):
        """Update an existing project if it exists."""
        if project_id in self.projects:
            self.projects[project_id].update(update_data)
            self.projects[project_id]['last_updated'] = time.time()
            
    def add_resource(self, resource_data: Dict) -> str:
        """Add a new resource with generated ID."""
        resource_id = str(uuid.uuid4())
        resource_data['status'] = 'available'
        resource_data['creation_time'] = time.time()
        self.resources[resource_id] = resource_data
        return resource_id
        
    def update_resource(self, resource_id: str, update_data: Dict):
        """Update an existing resource if it exists."""
        if resource_id in self.resources:
            self.resources[resource_id].update(update_data)
            self.resources[resource_id]['last_updated'] = time.time()
            
    def add_stakeholder(self, stakeholder_data: Dict) -> str:
        """Add a new stakeholder with generated ID."""
        stakeholder_id = str(uuid.uuid4())
        stakeholder_data['status'] = 'active'
        stakeholder_data['creation_time'] = time.time()
        self.stakeholders[stakeholder_id] = stakeholder_data
        return stakeholder_id
        
    def update_stakeholder(self, stakeholder_id: str, update_data: Dict):
        """Update an existing stakeholder if it exists."""
        if stakeholder_id in self.stakeholders:
            self.stakeholders[stakeholder_id].update(update_data)
            self.stakeholders[stakeholder_id]['last_updated'] = time.time()
            
    def update_financial(self, category: str, amount: float):
        """Update financial metrics for a specific category."""
        timestamp = str(int(time.time()))
        
        if category == 'revenue':
            self.financials['revenue'][timestamp] = amount
        elif category == 'expenses':
            self.financials['expenses'][timestamp] = amount
            
        self._recalculate_profit()
        
    def _update_financials(self):
        """Update financial metrics."""
        # Clean up old financial entries (older than 30 days)
        cutoff_time = str(int(time.time() - 30 * 24 * 3600))
        
        self.financials['revenue'] = {
            k: v for k, v in self.financials['revenue'].items()
            if k > cutoff_time
        }
        
        self.financials['expenses'] = {
            k: v for k, v in self.financials['expenses'].items()
            if k > cutoff_time
        }
        
        self._recalculate_profit()
        
    def _update_projects(self):
        """Update project states."""
        current_time = time.time()
        
        for project_id, project_data in self.projects.items():
            if project_data['status'] == 'active':
                # Check project deadlines
                if 'deadline' in project_data and current_time > project_data['deadline']:
                    self.update_project(project_id, {'status': 'overdue'})
                    
                # Update project progress
                if 'progress' in project_data:
                    progress = project_data['progress']
                    if progress >= 100:
                        self.update_project(project_id, {'status': 'completed'})
                        
    def _update_resources(self):
        """Update resource states."""
        current_time = time.time()
        
        for resource_id, resource_data in self.resources.items():
            # Update resource availability
            if resource_data['status'] == 'allocated':
                allocation_time = resource_data.get('allocation_time', 0)
                allocation_duration = resource_data.get('allocation_duration', float('inf'))
                
                if current_time - allocation_time > allocation_duration:
                    self.update_resource(resource_id, {'status': 'available'})
                    
    def _update_stakeholders(self):
        """Update stakeholder states."""
        current_time = time.time()
        
        for stakeholder_id, stakeholder_data in self.stakeholders.items():
            # Check stakeholder engagement
            last_contact = stakeholder_data.get('last_contact', 0)
            contact_threshold = stakeholder_data.get('contact_threshold', 30 * 24 * 3600)  # 30 days
            
            if current_time - last_contact > contact_threshold:
                self.update_stakeholder(stakeholder_id, {'engagement_status': 'needs_attention'})
                
    def _recalculate_profit(self):
        """Recalculate total profit based on revenue and expenses."""
        total_revenue = sum(self.financials['revenue'].values())
        total_expenses = sum(self.financials['expenses'].values())
        self.financials['profit'] = total_revenue - total_expenses 

    def reset(self):
        """Reset the business core to a stable state."""
        try:
            # Reset to stable values
            self.current_state = {
                'efficiency': 0.7,
                'productivity': 0.7,
                'resource_utilization': 0.7
            }
            
            # Reset metrics
            self.metrics = {
                'start_time': time.time(),
                'uptime': 0,
                'total_operations': 0,
                'success_rate': 0.95
            }
            
            return True
        except Exception as e:
            print(f"Error resetting business core: {str(e)}")
            return False 

    def get_metrics(self) -> Dict[str, Any]:
        """Get current business metrics."""
        return {
            'efficiency': self.current_state['efficiency'],
            'productivity': self.current_state['productivity'],
            'resource_utilization': self.current_state['resource_utilization'],
            'uptime': self.metrics['uptime'],
            'total_operations': self.metrics['total_operations'],
            'success_rate': self.metrics['success_rate']
        } 