"""
Test configuration for the LEF system.
"""

import os
import pytest
from pathlib import Path
from tempfile import mkdtemp
from shutil import rmtree

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