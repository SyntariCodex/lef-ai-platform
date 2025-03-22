"""
Tests for tasks API endpoints
"""

import pytest
from fastapi.testclient import TestClient

from src.lef.models import TaskStatus, TaskPriority

@pytest.mark.asyncio
async def test_task_lifecycle(client: TestClient, async_session):
    """Test creating, updating, and getting tasks."""
    # Create a task
    task_data = {
        "phase": "Core Infrastructure",
        "name": "Test Task",
        "description": "A test task",
        "priority": TaskPriority.HIGH.value,
        "metadata": {"type": "test"}
    }
    response = client.post("/tasks", json=task_data)
    assert response.status_code == 200
    data = response.json()
    task_id = data["id"]
    assert data["name"] == "Test Task"
    assert data["status"] == TaskStatus.NOT_STARTED.value
    assert data["progress"] == 0.0
    
    # Get specific task
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Task"
    
    # Update task status
    update_data = {
        "status": TaskStatus.IN_PROGRESS.value,
        "progress": 50.0,
        "notes": "Making progress"
    }
    response = client.put(f"/tasks/{task_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == TaskStatus.IN_PROGRESS.value
    assert data["progress"] == 50.0
    assert data["notes"] == "Making progress"
    
    # Complete task
    complete_data = {
        "status": TaskStatus.COMPLETED.value,
        "progress": 100.0,
        "notes": "Task completed"
    }
    response = client.put(f"/tasks/{task_id}", json=complete_data)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == TaskStatus.COMPLETED.value
    assert data["progress"] == 100.0
    assert data["completed_at"] is not None

@pytest.mark.asyncio
async def test_task_not_found(client: TestClient):
    """Test getting a non-existent task returns 404."""
    response = client.get("/tasks/99999")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_phase_progress(client: TestClient, async_session):
    """Test phase progress calculation."""
    # Create multiple tasks in the same phase
    phase = "Test Phase"
    tasks = [
        {"name": "Task 1", "status": TaskStatus.COMPLETED.value, "progress": 100.0},
        {"name": "Task 2", "status": TaskStatus.IN_PROGRESS.value, "progress": 50.0},
        {"name": "Task 3", "status": TaskStatus.NOT_STARTED.value, "progress": 0.0}
    ]
    
    for task in tasks:
        task_data = {
            "phase": phase,
            "name": task["name"],
            "priority": TaskPriority.MEDIUM.value
        }
        response = client.post("/tasks", json=task_data)
        assert response.status_code == 200
        task_id = response.json()["id"]
        
        if task["status"] != TaskStatus.NOT_STARTED.value:
            update_data = {
                "status": task["status"],
                "progress": task["progress"]
            }
            response = client.put(f"/tasks/{task_id}", json=update_data)
            assert response.status_code == 200
    
    # Check phase progress
    response = client.get(f"/tasks/phase/{phase}")
    assert response.status_code == 200
    data = response.json()
    assert data["phase"] == phase
    assert data["total_tasks"] == 3
    assert data["completed_tasks"] == 1
    assert data["progress_percentage"] == 50.0  # (100 + 50 + 0) / 3

@pytest.mark.asyncio
async def test_blocked_tasks(client: TestClient, async_session):
    """Test getting blocked tasks."""
    # Create some tasks, including blocked ones
    tasks = [
        {"name": "Task 1", "status": TaskStatus.BLOCKED.value},
        {"name": "Task 2", "status": TaskStatus.IN_PROGRESS.value},
        {"name": "Task 3", "status": TaskStatus.BLOCKED.value}
    ]
    
    for task in tasks:
        task_data = {
            "phase": "Test Phase",
            "name": task["name"],
            "priority": TaskPriority.MEDIUM.value
        }
        response = client.post("/tasks", json=task_data)
        assert response.status_code == 200
        task_id = response.json()["id"]
        
        if task["status"] != TaskStatus.NOT_STARTED.value:
            update_data = {"status": task["status"]}
            response = client.put(f"/tasks/{task_id}", json=update_data)
            assert response.status_code == 200
    
    # Get blocked tasks
    response = client.get("/tasks/blocked")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(task["status"] == TaskStatus.BLOCKED.value for task in data)

@pytest.mark.asyncio
async def test_task_filtering(client: TestClient, async_session):
    """Test task filtering by phase and status."""
    # Create tasks in different phases with different statuses
    tasks = [
        {"phase": "Phase 1", "status": TaskStatus.COMPLETED.value},
        {"phase": "Phase 1", "status": TaskStatus.IN_PROGRESS.value},
        {"phase": "Phase 2", "status": TaskStatus.IN_PROGRESS.value}
    ]
    
    for task in tasks:
        task_data = {
            "phase": task["phase"],
            "name": f"Task in {task['phase']}",
            "priority": TaskPriority.MEDIUM.value
        }
        response = client.post("/tasks", json=task_data)
        assert response.status_code == 200
        task_id = response.json()["id"]
        
        update_data = {"status": task["status"]}
        response = client.put(f"/tasks/{task_id}", json=update_data)
        assert response.status_code == 200
    
    # Filter by phase
    response = client.get("/tasks", params={"phase": "Phase 1"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(task["phase"] == "Phase 1" for task in data)
    
    # Filter by status
    response = client.get("/tasks", params={"status": TaskStatus.IN_PROGRESS.value})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(task["status"] == TaskStatus.IN_PROGRESS.value for task in data)
    
    # Filter by both
    response = client.get("/tasks", params={
        "phase": "Phase 1",
        "status": TaskStatus.COMPLETED.value
    })
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["phase"] == "Phase 1"
    assert data[0]["status"] == TaskStatus.COMPLETED.value 