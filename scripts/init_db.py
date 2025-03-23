"""
Database initialization script
"""

import os
import sys
import logging
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.lef.config import settings
from src.lef.services.timeline_management_service import Base as TimelineBase

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    """Initialize the database"""
    try:
        logger.info(f"Initializing database at {settings.DATABASE_URL}")
        
        # Create database if it doesn't exist
        engine = create_engine(settings.DATABASE_URL)
        if not database_exists(engine.url):
            create_database(engine.url)
            logger.info("Database created successfully")
        
        # Create tables
        TimelineBase.metadata.create_all(engine)
        logger.info("Database tables created successfully")
        
        return True
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        return False

if __name__ == "__main__":
    success = init_db()
    if not success:
        sys.exit(1) 