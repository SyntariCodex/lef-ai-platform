"""
Database configuration for the LEF system.
"""

import os
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Get database URL from environment or use default
DATABASE_URL = os.getenv(
    "LEF_DATABASE_URL",
    f"sqlite+aiosqlite:///{Path.home()}/.lef/lef.db"
)

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Set to False in production
    future=True
)

# Create async session factory
async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db():
    """Get database session."""
    async with async_session() as session:
        yield session

async def init_db():
    """Initialize database."""
    from .models.base import Base
    from .models.task import Task
    from .models.events import SystemEvent
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all) 