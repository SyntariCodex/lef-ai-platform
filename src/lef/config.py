"""
Configuration loader for the LEF system
"""

import os
from pathlib import Path
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings"""
    
    # Database Configuration
    DB_HOST: str = Field("localhost", env="DB_HOST")
    DB_PORT: int = Field(5432, env="DB_PORT")
    DB_NAME: str = Field("lef_db", env="DB_NAME")
    DB_USER: str = Field("lef_user", env="DB_USER")
    DB_PASSWORD: str = Field(..., env="DB_PASSWORD")
    
    @property
    def DATABASE_URL(self) -> str:
        """Get the database URL"""
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    # Redis Configuration
    REDIS_HOST: str = Field("localhost", env="REDIS_HOST")
    REDIS_PORT: int = Field(6379, env="REDIS_PORT")
    REDIS_DB: int = Field(0, env="REDIS_DB")
    REDIS_PASSWORD: str = Field(..., env="REDIS_PASSWORD")
    
    @property
    def REDIS_URL(self) -> str:
        """Get the Redis URL"""
        return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    # JWT Configuration
    JWT_SECRET_KEY: str = Field(..., env="JWT_SECRET_KEY")
    JWT_ALGORITHM: str = Field("HS256", env="JWT_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # Security Configuration
    CORS_ORIGINS: List[str] = Field(
        default_factory=lambda: ["http://localhost:3000"],
        env="CORS_ORIGINS"
    )
    ALLOWED_HOSTS: List[str] = Field(
        default_factory=lambda: ["localhost", "127.0.0.1"],
        env="ALLOWED_HOSTS"
    )
    
    # Logging Configuration
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field("json", env="LOG_FORMAT")
    
    # Service Configuration
    SERVICE_NAME: str = Field("LEF AI Bridge System", env="SERVICE_NAME")
    SERVICE_VERSION: str = Field("1.0.0", env="SERVICE_VERSION")
    
    # OpenTelemetry Configuration
    OTEL_EXPORTER_JAEGER_ENDPOINT: str = Field(
        "http://localhost:14268/api/traces",
        env="OTEL_EXPORTER_JAEGER_ENDPOINT"
    )
    OTEL_SERVICE_NAME: str = Field("lef-ai-bridge", env="OTEL_SERVICE_NAME")
    
    # Feature Flags
    ENABLE_CRITICAL_PATH_ANALYSIS: bool = Field(True, env="ENABLE_CRITICAL_PATH_ANALYSIS")
    ENABLE_RESOURCE_OPTIMIZATION: bool = Field(True, env="ENABLE_RESOURCE_OPTIMIZATION")
    ENABLE_COST_PREDICTION: bool = Field(True, env="ENABLE_COST_PREDICTION")
    ENABLE_RISK_ANALYSIS: bool = Field(True, env="ENABLE_RISK_ANALYSIS")
    
    class Config:
        """Pydantic configuration"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        
        @classmethod
        def parse_env_var(cls, field_name: str, raw_val: str) -> any:
            """Parse environment variables"""
            if field_name in ["CORS_ORIGINS", "ALLOWED_HOSTS"]:
                return json.loads(raw_val)
            return cls.json_loads(raw_val)

# Create global settings instance
settings = Settings() 