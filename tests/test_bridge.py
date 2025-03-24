"""
Tests for the bridge system
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime
import asyncio

from src.lef.bridge_layer import RecursiveBridge
from src.lef.models.message import Message, MessageType, MessagePriority
from src.lef.models.bridge_status import BridgeState, ServiceConnection

@pytest.mark.asyncio
async def test_bridge_initialization(bridge):
    """Test bridge initialization"""
    assert bridge.bridge_id is not None
    assert bridge.status == "initialized"
    assert len(bridge.connections) == 0
    assert bridge.message_queue is not None

@pytest.mark.asyncio
async def test_message_processing(bridge):
    """Test message processing"""
    # Create a test message
    message = Message(
        type=MessageType.COMMAND,
        priority=MessagePriority.MEDIUM,
        content={"command": "test"},
        timestamp=datetime.utcnow()
    )
    
    # Add message to queue
    await bridge.message_queue.put(message)
    
    # Process message
    processed_message = await bridge.message_queue.get()
    
    # Verify message processing
    assert processed_message.type == MessageType.COMMAND
    assert processed_message.priority == MessagePriority.MEDIUM
    assert processed_message.content["command"] == "test"

@pytest.mark.asyncio
async def test_service_connection(bridge):
    """Test service connection management"""
    # Connect a test service
    service_id = "test_service"
    connection = ServiceConnection(
        service_id=service_id,
        status="connected",
        connected_at=datetime.utcnow(),
        last_heartbeat=datetime.utcnow()
    )
    
    bridge.connections[service_id] = connection
    
    # Verify connection
    assert service_id in bridge.connections
    assert bridge.connections[service_id].status == "connected"
    
    # Disconnect service
    await bridge._disconnect_service(service_id)
    
    # Verify disconnection
    assert service_id not in bridge.connections

@pytest.mark.asyncio
async def test_bridge_state_management(bridge):
    """Test bridge state management"""
    # Update bridge state
    new_state = BridgeState(
        bridge_id=bridge.bridge_id,
        status="active",
        services={
            "test_service": ServiceConnection(
                service_id="test_service",
                status="connected",
                connected_at=datetime.utcnow(),
                last_heartbeat=datetime.utcnow()
            )
        }
    )
    
    await bridge.update_state(new_state)
    
    # Verify state update
    assert bridge.status == "active"
    assert "test_service" in bridge.connections
    assert bridge.connections["test_service"].status == "connected"

@pytest.mark.asyncio
async def test_error_handling(bridge):
    """Test error handling"""
    # Simulate an error
    error_message = "Test error"
    bridge.error = error_message
    
    # Get error status
    status = bridge.get_status()
    
    # Verify error handling
    assert status["error"] == error_message
    assert status["status"] == "error"
    
    # Test error recovery
    await bridge.recover_from_error()
    
    # Verify recovery
    assert bridge.error is None
    assert bridge.status == "initialized"

@pytest.mark.asyncio
async def test_rate_limiting(bridge):
    """Test rate limiting"""
    service_id = "test_service"
    
    # Set up rate limit
    await bridge.rate_limiter.set_rate_limit(service_id, 10, 60)  # 10 requests per minute
    
    # Make requests
    for _ in range(15):
        if not await bridge.rate_limiter.check_rate_limit(service_id):
            break
    
    # Verify rate limiting
    assert not await bridge.rate_limiter.check_rate_limit(service_id)
    
    # Wait for rate limit reset
    await asyncio.sleep(61)
    
    # Verify rate limit reset
    assert await bridge.rate_limiter.check_rate_limit(service_id) 