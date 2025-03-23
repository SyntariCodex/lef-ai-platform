"""
Test cases for the AI Bridge System
"""

import pytest
import asyncio
from datetime import datetime
from pathlib import Path
from src.lef.ai_bridge import AIBridge, Message, BridgeState

@pytest.fixture
async def ai_bridge():
    """Create an AI Bridge instance for testing"""
    bridge = AIBridge()
    await bridge.initialize()
    yield bridge
    await bridge.shutdown()

@pytest.mark.asyncio
async def test_initialization(ai_bridge):
    """Test AI Bridge initialization"""
    assert ai_bridge.state == BridgeState.ACTIVE
    assert len(ai_bridge.connections) > 0
    assert ai_bridge.redis is not None

@pytest.mark.asyncio
async def test_message_sending(ai_bridge):
    """Test sending messages through the bridge"""
    message = Message(
        id="test-1",
        source="test",
        target="claude",
        content={"text": "Hello, Claude!"},
        priority=1,
        timestamp=datetime.now().isoformat()
    )
    
    success = await ai_bridge.send_message(message)
    assert success is True

@pytest.mark.asyncio
async def test_message_receiving(ai_bridge):
    """Test receiving messages from the bridge"""
    message = await ai_bridge.receive_message("claude")
    assert message is not None
    assert isinstance(message, Message)

@pytest.mark.asyncio
async def test_encryption(ai_bridge):
    """Test message encryption and decryption"""
    test_content = {"sensitive": "data"}
    
    # Test encryption
    encrypted = ai_bridge._encrypt_message(test_content)
    assert "encrypted" in encrypted
    assert isinstance(encrypted["encrypted"], str)
    
    # Test decryption
    decrypted = ai_bridge._decrypt_message(encrypted)
    assert decrypted == test_content

@pytest.mark.asyncio
async def test_signature_verification(ai_bridge):
    """Test message signing and verification"""
    message = Message(
        id="test-2",
        source="test",
        target="grok",
        content={"text": "Hello, Grok!"},
        priority=1,
        timestamp=datetime.now().isoformat()
    )
    
    # Test signing
    signature = ai_bridge._sign_message(message)
    assert signature is not None
    assert isinstance(signature, str)
    
    # Test verification
    message_data = message.__dict__
    message_data["signature"] = signature
    assert ai_bridge._verify_signature(message_data) is True

@pytest.mark.asyncio
async def test_shutdown(ai_bridge):
    """Test AI Bridge shutdown"""
    await ai_bridge.shutdown()
    assert ai_bridge.state == BridgeState.SHUTDOWN
    assert len(ai_bridge.connections) == 0
    assert ai_bridge.redis is None 