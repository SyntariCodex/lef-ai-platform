"""
Tests for system API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime

from src.lef.models import EventType

def test_root_endpoint(client: TestClient):
    """Test the root endpoint returns correct status."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "operational"

@pytest.mark.asyncio
async def test_component_lifecycle(client: TestClient, async_session):
    """Test creating, updating, and getting component state."""
    # Create/update component state
    component_data = {
        "status": "running",
        "process_id": 12345,
        "metadata": {"version": "1.0.0"}
    }
    response = client.put("/system/components/test_component", json=component_data)
    assert response.status_code == 200
    data = response.json()
    assert data["component_name"] == "test_component"
    assert data["status"] == "running"
    assert data["process_id"] == 12345
    
    # Get specific component
    response = client.get("/system/components/test_component")
    assert response.status_code == 200
    data = response.json()
    assert data["component_name"] == "test_component"
    assert data["status"] == "running"
    
    # Get all components
    response = client.get("/system/components")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["component_name"] == "test_component"
    
    # Update component state
    update_data = {
        "status": "stopped",
        "process_id": None,
        "metadata": {"shutdown_time": datetime.utcnow().isoformat()}
    }
    response = client.put("/system/components/test_component", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "stopped"
    assert data["process_id"] is None

@pytest.mark.asyncio
async def test_component_not_found(client: TestClient):
    """Test getting a non-existent component returns 404."""
    response = client.get("/system/components/nonexistent")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_system_events(client: TestClient, async_session):
    """Test creating and retrieving system events."""
    # Create an event
    event_data = {
        "event_type": EventType.PROCESS_START.value,
        "component_name": "test_component",
        "message": "Component started",
        "process_id": 12345,
        "metadata": {"version": "1.0.0"}
    }
    response = client.post("/system/events", json=event_data)
    assert response.status_code == 200
    data = response.json()
    assert data["event_type"] == EventType.PROCESS_START.value
    assert data["component_name"] == "test_component"
    
    # Get all events
    response = client.get("/system/events")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1  # Might have more due to component state changes
    
    # Get filtered events
    response = client.get(
        "/system/events",
        params={
            "component_name": "test_component",
            "event_type": EventType.PROCESS_START.value
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert all(e["component_name"] == "test_component" for e in data)
    assert all(e["event_type"] == EventType.PROCESS_START.value for e in data)

@pytest.mark.asyncio
async def test_event_limit(client: TestClient, async_session):
    """Test event listing respects the limit parameter."""
    # Create multiple events
    for i in range(10):
        event_data = {
            "event_type": EventType.SYSTEM_ERROR.value,
            "component_name": f"component_{i}",
            "message": f"Error {i}",
            "process_id": i,
            "metadata": {}
        }
        client.post("/system/events", json=event_data)
    
    # Get limited events
    response = client.get("/system/events", params={"limit": 5})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5 