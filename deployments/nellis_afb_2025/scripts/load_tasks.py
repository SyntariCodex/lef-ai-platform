"""
Script to load NAFB Phase 1 tasks into the LEF system.
"""

import asyncio
import yaml
from pathlib import Path
from typing import Dict, Any

from src.lef.database import async_session
from src.lef.models.task import Task, TaskStatus, TaskPriority

async def load_tasks(config_path: str):
    """Load tasks from deployment configuration."""
    # Read configuration
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    async with async_session() as session:
        # Create tasks
        tasks: Dict[str, Task] = {}
        
        for task_config in config["tasks"]:
            task = Task(
                name=task_config["name"],
                phase=config["phase"],
                priority=TaskPriority(task_config["priority"]),
                status=TaskStatus.PENDING,
                task_metadata={
                    "initiated_by": config["initiated_by"],
                    "objectives": config["objectives"]
                },
                resource_baseline=task_config.get("resource_baseline", {}),
                alert_threshold=task_config.get("alert_threshold", 7.5),
                pulse_checkpoint_interval=task_config.get("pulse_checkpoint_interval", 3),
                observer_confirmation_required=task_config.get("observer_confirmation_required", False),
                requires_sync=task_config.get("requires_sync", [])
            )
            
            session.add(task)
            tasks[task_config["name"]] = task
        
        await session.commit()
        
        # Set up dependencies
        for task_config in config["tasks"]:
            task = tasks[task_config["name"]]
            for dep_name in task_config.get("dependencies", []):
                if dep_name in tasks:
                    task.dependencies.append(tasks[dep_name])
        
        await session.commit()
        print(f"Loaded {len(tasks)} tasks for {config['phase']}")

if __name__ == "__main__":
    config_path = Path(__file__).parent.parent / "config" / "deployment.yaml"
    asyncio.run(load_tasks(str(config_path))) 