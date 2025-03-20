from typing import Dict, List, Optional
import time
from lef.core.business import BusinessCore

class ProjectHandler:
    """Handles project management operations."""
    
    def __init__(self, business_core: BusinessCore):
        self.business_core = business_core
        self.active_projects: Dict[str, dict] = {}
        self.completed_projects: Dict[str, dict] = {}
        
    def update(self):
        """Update project states."""
        self._check_project_statuses()
        self._update_project_metrics()
        self._optimize_resource_allocation()
        
    def _check_project_statuses(self):
        """Check and update project statuses."""
        for project_id, project in self.active_projects.items():
            if self._is_project_completed(project):
                self._complete_project(project_id)
                
    def _update_project_metrics(self):
        """Update project performance metrics."""
        for project in self.active_projects.values():
            self._calculate_project_progress(project)
            self._update_project_timeline(project)
            
    def _optimize_resource_allocation(self):
        """Optimize resource allocation across projects."""
        # Placeholder for resource optimization logic
        pass
        
    def _is_project_completed(self, project: dict) -> bool:
        """Check if a project is completed."""
        return project.get('progress', 0) >= 100
        
    def _complete_project(self, project_id: str):
        """Mark a project as completed."""
        if project_id in self.active_projects:
            project = self.active_projects.pop(project_id)
            project['completed_at'] = time.time()
            self.completed_projects[project_id] = project
            
    def _calculate_project_progress(self, project: dict):
        """Calculate project progress."""
        # Placeholder for progress calculation logic
        project['progress'] = min(100, project.get('progress', 0) + 1)
        
    def _update_project_timeline(self, project: dict):
        """Update project timeline."""
        # Placeholder for timeline update logic
        pass
        
    def create_project(self, project_data: dict) -> str:
        """Create a new project."""
        project_id = f"proj_{len(self.active_projects) + 1}"
        project = {
            'data': project_data,
            'progress': 0,
            'created_at': time.time(),
            'status': 'active'
        }
        self.active_projects[project_id] = project
        self.business_core.add_project(project_id, project_data)
        return project_id
        
    def get_project_status(self, project_id: str) -> Optional[dict]:
        """Get the status of a project."""
        if project_id in self.active_projects:
            return self.active_projects[project_id]
        elif project_id in self.completed_projects:
            return self.completed_projects[project_id]
        return None 