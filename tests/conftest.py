"""
Test configuration for the LEF system.
"""

import os
import pytest
from pathlib import Path
from tempfile import mkdtemp
from shutil import rmtree
import asyncio
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock

from src.lef.services.monitoring_service import MonitoringService
from src.lef.services.alert_service import AlertService
from src.lef.bridge_layer import RecursiveBridge
from src.lef.models.system_state import SystemState

@pytest.fixture(scope="session")
def test_dir():
    """Create a temporary directory for test data."""
    temp_dir = mkdtemp()
    yield temp_dir
    rmtree(temp_dir)

@pytest.fixture(scope="session")
def test_db_path(test_dir):
    """Create a test database path."""
    return Path(test_dir) / "test.db"

@pytest.fixture(autouse=True)
def setup_test_env(test_db_path):
    """Set up test environment."""
    # Set environment variables
    os.environ["LEF_ENV"] = "test"
    os.environ["LEF_DB_PATH"] = str(test_db_path)
    
    yield
    
    # Clean up
    if test_db_path.exists():
        test_db_path.unlink()

@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def monitoring_service() -> AsyncGenerator[MonitoringService, None]:
    """Create a monitoring service instance for testing."""
    service = MonitoringService(cloudwatch_config={"enabled": False})
    await service.start()
    yield service
    await service.shutdown()

@pytest.fixture
def alert_service() -> AlertService:
    """Create an alert service instance for testing."""
    return AlertService()

@pytest.fixture
def bridge() -> RecursiveBridge:
    """Create a bridge instance for testing."""
    return RecursiveBridge()

@pytest.fixture
def mock_cloudwatch() -> MagicMock:
    """Create a mock CloudWatch client."""
    mock_client = MagicMock()
    mock_client.put_metric_data = AsyncMock()
    return mock_client

@pytest.fixture
def system_state() -> SystemState:
    """Create a system state instance for testing."""
    return SystemState(
        status="initializing",
        components={
            "bridge": {"status": "healthy"},
            "monitoring": {"status": "healthy"},
            "alert": {"status": "healthy"}
        }
    ) 