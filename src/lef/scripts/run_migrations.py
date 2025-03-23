"""
Run database migrations
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from alembic.config import Config
from alembic import command

def run_migrations():
    """Run database migrations"""
    try:
        # Create Alembic configuration
        alembic_cfg = Config()
        alembic_cfg.set_main_option("script_location", "src/lef/migrations")
        alembic_cfg.set_main_option("sqlalchemy.url", "postgresql://user:password@localhost:5432/lef_db")

        # Run migrations
        command.upgrade(alembic_cfg, "head")
        print("Migrations completed successfully")
    except Exception as e:
        print(f"Error running migrations: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_migrations() 