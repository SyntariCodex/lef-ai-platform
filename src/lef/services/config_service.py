"""
Configuration management service for AI Bridge System
"""

import asyncio
import logging
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from pathlib import Path

from ..services.alert_service import AlertService, AlertSeverity
from ..services.monitoring_service import MonitoringService

logger = logging.getLogger(__name__)

class ConfigValue(BaseModel):
    """Configuration value with metadata"""
    value: Any
    type: str
    description: Optional[str] = None
    default: Optional[Any] = None
    required: bool = False
    validation_rules: Dict[str, Any] = Field(default_factory=dict)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    updated_by: Optional[str] = None

class ServiceConfig(BaseModel):
    """Service-specific configuration"""
    service_id: str
    config: Dict[str, ConfigValue]
    version: str
    environment: str
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    updated_by: Optional[str] = None

class ConfigService:
    """Service for managing system and service configurations"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.system_config: Dict[str, ConfigValue] = {}
        self.service_configs: Dict[str, ServiceConfig] = {}
        self.alert_service = AlertService()
        self.monitoring_service = MonitoringService()
        self._config_watcher: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
        
    async def start(self):
        """Start the configuration service"""
        try:
            logger.info("Starting configuration service")
            
            # Create config directory if it doesn't exist
            self.config_dir.mkdir(parents=True, exist_ok=True)
            
            # Load initial configurations
            await self._load_system_config()
            await self._load_service_configs()
            
            # Start config watcher
            self._config_watcher = asyncio.create_task(self._watch_config_changes())
            
            logger.info("Configuration service started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start configuration service: {e}")
            await self.alert_service.create_alert(
                title="Configuration Service Start Failed",
                message=f"Failed to start configuration service: {e}",
                severity=AlertSeverity.ERROR
            )
            raise
            
    async def _load_system_config(self):
        """Load system configuration from file"""
        try:
            config_file = self.config_dir / "system_config.json"
            if config_file.exists():
                with open(config_file) as f:
                    config_data = json.load(f)
                    self.system_config = {
                        key: ConfigValue(**value)
                        for key, value in config_data.items()
                    }
            else:
                # Initialize with default system config
                self.system_config = {
                    "log_level": ConfigValue(
                        value="INFO",
                        type="string",
                        description="System-wide logging level"
                    ),
                    "max_connections": ConfigValue(
                        value=100,
                        type="integer",
                        description="Maximum number of concurrent connections"
                    ),
                    "heartbeat_interval": ConfigValue(
                        value=30,
                        type="integer",
                        description="Heartbeat interval in seconds"
                    )
                }
                await self._save_system_config()
                
        except Exception as e:
            logger.error(f"Failed to load system config: {e}")
            await self.alert_service.create_alert(
                title="System Config Load Failed",
                message=f"Failed to load system configuration: {e}",
                severity=AlertSeverity.ERROR
            )
            raise
            
    async def _load_service_configs(self):
        """Load service configurations from files"""
        try:
            service_config_dir = self.config_dir / "services"
            service_config_dir.mkdir(exist_ok=True)
            
            for config_file in service_config_dir.glob("*.json"):
                try:
                    with open(config_file) as f:
                        config_data = json.load(f)
                        service_config = ServiceConfig(**config_data)
                        self.service_configs[service_config.service_id] = service_config
                except Exception as e:
                    logger.error(f"Failed to load service config {config_file}: {e}")
                    
        except Exception as e:
            logger.error(f"Failed to load service configs: {e}")
            await self.alert_service.create_alert(
                title="Service Configs Load Failed",
                message=f"Failed to load service configurations: {e}",
                severity=AlertSeverity.ERROR
            )
            raise
            
    async def _save_system_config(self):
        """Save system configuration to file"""
        try:
            config_file = self.config_dir / "system_config.json"
            config_data = {
                key: value.dict()
                for key, value in self.system_config.items()
            }
            
            with open(config_file, "w") as f:
                json.dump(config_data, f, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"Failed to save system config: {e}")
            await self.alert_service.create_alert(
                title="System Config Save Failed",
                message=f"Failed to save system configuration: {e}",
                severity=AlertSeverity.ERROR
            )
            raise
            
    async def _save_service_config(self, service_id: str):
        """Save service configuration to file"""
        try:
            if service_id not in self.service_configs:
                raise ValueError(f"Service config {service_id} not found")
                
            service_config_dir = self.config_dir / "services"
            config_file = service_config_dir / f"{service_id}.json"
            
            with open(config_file, "w") as f:
                json.dump(self.service_configs[service_id].dict(), f, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"Failed to save service config {service_id}: {e}")
            await self.alert_service.create_alert(
                title="Service Config Save Failed",
                message=f"Failed to save service configuration for {service_id}: {e}",
                severity=AlertSeverity.ERROR
            )
            raise
            
    async def _watch_config_changes(self):
        """Watch for configuration file changes"""
        while not self._shutdown_event.is_set():
            try:
                # Check for system config changes
                config_file = self.config_dir / "system_config.json"
                if config_file.exists():
                    mtime = config_file.stat().st_mtime
                    if mtime > self.system_config.get("_last_mtime", 0):
                        await self._load_system_config()
                        self.system_config["_last_mtime"] = mtime
                        
                # Check for service config changes
                service_config_dir = self.config_dir / "services"
                for config_file in service_config_dir.glob("*.json"):
                    service_id = config_file.stem
                    mtime = config_file.stat().st_mtime
                    if service_id in self.service_configs:
                        if mtime > self.service_configs[service_id]._last_mtime:
                            await self._load_service_configs()
                            self.service_configs[service_id]._last_mtime = mtime
                            
                await asyncio.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                logger.error(f"Error watching config changes: {e}")
                await asyncio.sleep(5)
                
    async def get_system_config(self, key: Optional[str] = None) -> Dict[str, ConfigValue]:
        """Get system configuration, optionally filtered by key"""
        if key:
            return {key: self.system_config[key]} if key in self.system_config else {}
        return self.system_config
        
    async def update_system_config(self, key: str, value: Any, updated_by: str):
        """Update system configuration value"""
        try:
            if key not in self.system_config:
                raise ValueError(f"Config key {key} not found")
                
            config_value = self.system_config[key]
            config_value.value = value
            config_value.last_updated = datetime.utcnow()
            config_value.updated_by = updated_by
            
            await self._save_system_config()
            
            # Record metric
            await self.monitoring_service._record_metric(
                "config_updates",
                1,
                {"type": "system", "key": key}
            )
            
        except Exception as e:
            logger.error(f"Failed to update system config: {e}")
            await self.alert_service.create_alert(
                title="System Config Update Failed",
                message=f"Failed to update system configuration {key}: {e}",
                severity=AlertSeverity.ERROR
            )
            raise
            
    async def get_service_config(self, service_id: str) -> Optional[ServiceConfig]:
        """Get service configuration"""
        return self.service_configs.get(service_id)
        
    async def update_service_config(
        self,
        service_id: str,
        config: Dict[str, Any],
        version: str,
        environment: str,
        updated_by: str
    ):
        """Update service configuration"""
        try:
            service_config = ServiceConfig(
                service_id=service_id,
                config={
                    key: ConfigValue(
                        value=value,
                        type=type(value).__name__,
                        last_updated=datetime.utcnow(),
                        updated_by=updated_by
                    )
                    for key, value in config.items()
                },
                version=version,
                environment=environment
            )
            
            self.service_configs[service_id] = service_config
            await self._save_service_config(service_id)
            
            # Record metric
            await self.monitoring_service._record_metric(
                "config_updates",
                1,
                {"type": "service", "service_id": service_id}
            )
            
        except Exception as e:
            logger.error(f"Failed to update service config: {e}")
            await self.alert_service.create_alert(
                title="Service Config Update Failed",
                message=f"Failed to update service configuration for {service_id}: {e}",
                severity=AlertSeverity.ERROR
            )
            raise
            
    async def delete_service_config(self, service_id: str):
        """Delete service configuration"""
        try:
            if service_id not in self.service_configs:
                raise ValueError(f"Service config {service_id} not found")
                
            service_config_dir = self.config_dir / "services"
            config_file = service_config_dir / f"{service_id}.json"
            
            if config_file.exists():
                config_file.unlink()
                
            del self.service_configs[service_id]
            
            # Record metric
            await self.monitoring_service._record_metric(
                "config_deletions",
                1,
                {"type": "service", "service_id": service_id}
            )
            
        except Exception as e:
            logger.error(f"Failed to delete service config: {e}")
            await self.alert_service.create_alert(
                title="Service Config Delete Failed",
                message=f"Failed to delete service configuration for {service_id}: {e}",
                severity=AlertSeverity.ERROR
            )
            raise
            
    async def shutdown(self):
        """Shutdown the configuration service"""
        try:
            logger.info("Shutting down configuration service")
            
            # Stop config watcher
            if self._config_watcher:
                self._shutdown_event.set()
                await self._config_watcher
                self._config_watcher = None
                
            logger.info("Configuration service shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during configuration service shutdown: {e}")
            await self.alert_service.create_alert(
                title="Configuration Service Shutdown Failed",
                message=f"Error during shutdown: {e}",
                severity=AlertSeverity.ERROR
            )
            raise 