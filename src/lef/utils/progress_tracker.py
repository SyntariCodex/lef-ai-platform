"""
Dynamic Progress Tracking System for LEF Development
"""

import json
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, asdict
import logging

@dataclass
class TaskStatus:
    completed: bool
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    dependencies: List[str]
    blockers: List[str]
    notes: List[str]
    priority: int
    risk_level: str
    assigned_to: Optional[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert TaskStatus to dictionary for JSON serialization"""
        data = asdict(self)
        # Convert datetime objects to ISO format strings
        if data['started_at']:
            data['started_at'] = data['started_at'].isoformat()
        if data['completed_at']:
            data['completed_at'] = data['completed_at'].isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaskStatus':
        """Create TaskStatus from dictionary"""
        # Convert ISO format strings back to datetime objects
        if data.get('started_at'):
            data['started_at'] = datetime.fromisoformat(data['started_at'])
        if data.get('completed_at'):
            data['completed_at'] = datetime.fromisoformat(data['completed_at'])
        return cls(**data)

class ProgressTracker:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.progress_file = Path.home() / ".lef/state/progress.json"
        self.status_data: Dict[str, Dict[str, TaskStatus]] = {}
        self.load_progress()

    def load_progress(self):
        """Load progress data from file"""
        try:
            if self.progress_file.exists():
                with open(self.progress_file, 'r') as f:
                    data = json.load(f)
                    self.status_data = {
                        phase: {
                            task: TaskStatus.from_dict(status) 
                            for task, status in tasks.items()
                        }
                        for phase, tasks in data.items()
                    }
            else:
                self._initialize_from_roadmap()
        except Exception as e:
            self.logger.error(f"Error loading progress: {str(e)}")
            self._initialize_from_roadmap()

    def _initialize_from_roadmap(self):
        """Initialize progress data from roadmap"""
        try:
            roadmap_file = Path('roadmap.yaml')
            if not roadmap_file.exists():
                self.logger.error("Roadmap file not found")
                return
            
            with open(roadmap_file) as f:
                roadmap = yaml.safe_load(f)
            
            self.status_data = {}
            for phase, phase_data in roadmap.items():
                self.status_data[phase] = {}
                for task in phase_data.get('tasks', []):
                    self.status_data[phase][task] = TaskStatus(
                        completed=False,
                        started_at=None,
                        completed_at=None,
                        dependencies=[],
                        blockers=[],
                        notes=[],
                        priority=1,
                        risk_level="LOW",
                        assigned_to=None
                    )
            
            self.save_progress()
        except Exception as e:
            self.logger.error(f"Error initializing from roadmap: {str(e)}")

    def save_progress(self):
        """Save progress data to file"""
        try:
            self.progress_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.progress_file, 'w') as f:
                json.dump(self.status_data, f, indent=2, default=lambda x: x.to_dict())
        except Exception as e:
            self.logger.error(f"Error saving progress: {str(e)}")

    def update_task_status(
        self,
        phase: str,
        task: str,
        status: bool,
        notes: Optional[str] = None,
        blockers: Optional[List[str]] = None
    ):
        """Update task status and related information"""
        if phase in self.status_data and task in self.status_data[phase]:
            task_status = self.status_data[phase][task]
            task_status.completed = status
            
            if status:
                task_status.completed_at = datetime.now()
            else:
                task_status.started_at = datetime.now()
            
            if notes:
                task_status.notes.append(f"{datetime.now()}: {notes}")
            
            if blockers:
                task_status.blockers = blockers
            
            self.save_progress()
        else:
            self.logger.error(f"Task {task} not found in phase {phase}")

    def get_current_phase(self) -> Optional[str]:
        """Get the current active phase"""
        for phase, tasks in self.status_data.items():
            incomplete_tasks = [
                task for task, status in tasks.items() 
                if not status.completed
            ]
            if incomplete_tasks:
                return phase
        return None

    def get_next_tasks(self, limit: int = 3) -> List[Dict[str, str]]:
        """Get the next tasks to be completed"""
        current_phase = self.get_current_phase()
        if not current_phase:
            return []

        next_tasks = []
        for task, status in self.status_data[current_phase].items():
            if not status.completed and not status.blockers:
                next_tasks.append({
                    "phase": current_phase,
                    "task": task,
                    "priority": status.priority,
                    "risk_level": status.risk_level
                })
                if len(next_tasks) >= limit:
                    break
        
        return sorted(next_tasks, key=lambda x: x["priority"], reverse=True)

    def get_blockers(self) -> List[Dict[str, List[str]]]:
        """Get all blocked tasks and their blockers"""
        blocked_tasks = []
        for phase, tasks in self.status_data.items():
            for task, status in tasks.items():
                if status.blockers:
                    blocked_tasks.append({
                        "phase": phase,
                        "task": task,
                        "blockers": status.blockers
                    })
        return blocked_tasks

    def generate_report(self) -> Dict[str, Any]:
        """Generate a progress report"""
        total_tasks = 0
        completed_tasks = 0
        blocked_tasks = 0
        
        for tasks in self.status_data.values():
            for status in tasks.values():
                total_tasks += 1
                if status.completed:
                    completed_tasks += 1
                if status.blockers:
                    blocked_tasks += 1

        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "completion_percentage": (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0,
            "blocked_tasks": blocked_tasks,
            "current_phase": self.get_current_phase(),
            "next_tasks": self.get_next_tasks(),
            "blockers": self.get_blockers(),
            "last_updated": datetime.now().isoformat()
        }

    def predict_completion(self, phase: str) -> Optional[datetime]:
        """Predict completion date for a phase based on current progress"""
        if phase not in self.status_data:
            return None
            
        tasks = self.status_data[phase]
        completed_tasks = sum(1 for status in tasks.values() if status.completed)
        total_tasks = len(tasks)
        
        if completed_tasks == 0:
            return None
            
        first_completion = min(
            (status.completed_at 
             for status in tasks.values() 
             if status.completed_at is not None),
            default=None
        )
        
        if not first_completion:
            return None
            
        last_completion = max(
            (status.completed_at 
             for status in tasks.values() 
             if status.completed_at is not None),
            default=None
        )
        
        if not last_completion or first_completion == last_completion:
            return None
            
        time_per_task = (last_completion - first_completion) / completed_tasks
        remaining_tasks = total_tasks - completed_tasks
        
        return datetime.now() + (time_per_task * remaining_tasks) 