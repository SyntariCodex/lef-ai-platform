"""
Base model for the LEF system.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class BaseModel(BaseModel):
    """Base model with common fields."""
    id: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        """Pydantic model configuration."""
        from_attributes = True 