"""
Initialize database with default data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from lef.scripts.run_migrations import run_migrations
from lef.scripts.init_permissions import init_database

def init_db():
    """Initialize database with migrations and default data"""
    try:
        # Run migrations
        print("Running migrations...")
        run_migrations()

        # Initialize permissions and default data
        print("Initializing permissions and default data...")
        init_database()

        print("Database initialization completed successfully")
    except Exception as e:
        print(f"Error initializing database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    init_db() 