"""
Database model for the LEF system.
"""

import os
from pathlib import Path

# Get data directory
data_dir = Path.home() / ".lef" / "data"
data_dir.mkdir(parents=True, exist_ok=True)

# Database path
DATABASE_PATH = data_dir / "lef.db"

def get_database_path() -> Path:
    """Get the database path."""
    return DATABASE_PATH 