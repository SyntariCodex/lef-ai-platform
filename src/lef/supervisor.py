"""
Supervisor module for the LEF system.
"""

import asyncio
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import router as api_router
from .core.sentinel_network import SentinelNetwork
from .core.recovery import RecoveryManager
from .database import init_db, get_system_state, update_system_state
from .models.system_state import SystemState, SystemStatus, ComponentStatus
from .services.alert_service import AlertService

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(Path.home() / ".lef" / "logs" / "supervisor.log")
    ]
)

logger = logging.getLogger("lef.supervisor")

class Supervisor:
    """Supervisor for the LEF system."""
    
    def __init__(self):
        """Initialize the supervisor."""
        self.app = FastAPI(
            title="LEF Supervisor",
            description="Supervisor API for the LEF system",
            version="1.0.0"
        )
        
        # Configure CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Include API router
        self.app.include_router(api_router)
        
        # Initialize components
        self.sentinel_network = SentinelNetwork()
        self.recovery_manager = RecoveryManager()
        self.alert_service = AlertService()
        self.running = False
        self.start_time = None
        
        # Initialize database
        init_db()
        
        # Initialize system state
        self.system_state = get_system_state()
        self.system_state.status = SystemStatus.INITIALIZING
        self.system_state.version = "1.0.0"
        self.system_state.last_updated = datetime.utcnow()
        update_system_state(self.system_state)
        
    async def start(self):
        """Start the supervisor."""
        try:
            self.running = True
            self.start_time = time.time()
            
            # Start sentinel network
            if not await self.sentinel_network.start():
                raise RuntimeError("Failed to start sentinel network")
            
            # Update system state
            self.system_state.status = SystemStatus.ACTIVE
            self.system_state.components = {
                "supervisor": ComponentStatus.HEALTHY,
                "sentinel_network": ComponentStatus.HEALTHY,
                "recovery_manager": ComponentStatus.HEALTHY,
                "alert_service": ComponentStatus.HEALTHY
            }
            update_system_state(self.system_state)
            
            # Start monitoring tasks
            asyncio.create_task(self._monitor_system_state())
            asyncio.create_task(self._monitor_components())
            asyncio.create_task(self._check_alerts())
            
            logger.info("Supervisor started successfully")
            
        except Exception as e:
            logger.error(f"Error starting supervisor: {e}")
            self.system_state.status = SystemStatus.ERROR
            self.system_state.errors.append(str(e))
            update_system_state(self.system_state)
            raise
            
    async def stop(self):
        """Stop the supervisor."""
        try:
            self.running = False
            
            # Stop sentinel network
            await self.sentinel_network.stop()
            
            # Update system state
            self.system_state.status = SystemStatus.SHUTDOWN
            self.system_state.components = {
                "supervisor": ComponentStatus.OFFLINE,
                "sentinel_network": ComponentStatus.OFFLINE,
                "recovery_manager": ComponentStatus.OFFLINE,
                "alert_service": ComponentStatus.OFFLINE
            }
            update_system_state(self.system_state)
            
            logger.info("Supervisor stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping supervisor: {e}")
            self.system_state.errors.append(str(e))
            update_system_state(self.system_state)
            raise
            
    async def _monitor_system_state(self):
        """Monitor and update system state."""
        while self.running:
            try:
                # Get metrics from sentinel network
                health_metrics = self.sentinel_network.sentinels["health"]["metrics"]
                performance_metrics = self.sentinel_network.sentinels["performance"]["metrics"]
                security_metrics = self.sentinel_network.sentinels["security"]["metrics"]
                
                # Update system state
                self.system_state.last_updated = datetime.utcnow()
                self.system_state.uptime = time.time() - self.start_time
                self.system_state.metrics = {
                    "cpu_usage": health_metrics.get("cpu_usage", 0.0),
                    "memory_usage": health_metrics.get("memory_usage", 0.0),
                    "disk_usage": health_metrics.get("disk_usage", 0.0),
                    "system_load": performance_metrics.get("cpu", {}).get("system", 0.0)
                }
                self.system_state.resource_usage = {
                    "memory_available": health_metrics.get("memory_available", 0.0),
                    "disk_free": health_metrics.get("disk_free", 0.0)
                }
                self.system_state.performance_metrics = {
                    "io_read": performance_metrics.get("io", {}).get("read_bytes", 0),
                    "io_write": performance_metrics.get("io", {}).get("write_bytes", 0),
                    "network_sent": performance_metrics.get("network", {}).get("bytes_sent", 0),
                    "network_recv": performance_metrics.get("network", {}).get("bytes_recv", 0)
                }
                self.system_state.security_status = {
                    "high_cpu_processes": len(security_metrics.get("high_cpu_processes", [])),
                    "active_connections": len(security_metrics.get("active_connections", [])),
                    "active_users": security_metrics.get("users", 0)
                }
                
                # Update system status based on metrics
                if self.system_state.metrics["cpu_usage"] > 90 or \
                   self.system_state.metrics["memory_usage"] > 90 or \
                   self.system_state.metrics["disk_usage"] > 90:
                    self.system_state.status = SystemStatus.DEGRADED
                elif any(self.system_state.errors):
                    self.system_state.status = SystemStatus.ERROR
                else:
                    self.system_state.status = SystemStatus.ACTIVE
                
                # Update system state in database
                update_system_state(self.system_state)
                
                await asyncio.sleep(5)  # Update every 5 seconds
                
            except Exception as e:
                logger.error(f"Error monitoring system state: {e}")
                self.system_state.errors.append(str(e))
                update_system_state(self.system_state)
                await asyncio.sleep(5)
                
    async def _monitor_components(self):
        """Monitor component health."""
        while self.running:
            try:
                # Check sentinel network
                if not self.sentinel_network.running:
                    self.system_state.components["sentinel_network"] = ComponentStatus.ERROR
                    self.system_state.errors.append("Sentinel network is not running")
                else:
                    self.system_state.components["sentinel_network"] = ComponentStatus.HEALTHY
                
                # Check recovery manager
                if not self.recovery_manager.is_healthy():
                    self.system_state.components["recovery_manager"] = ComponentStatus.ERROR
                    self.system_state.errors.append("Recovery manager is not healthy")
                else:
                    self.system_state.components["recovery_manager"] = ComponentStatus.HEALTHY
                
                # Check alert service
                if not self.alert_service.alerts:
                    self.system_state.components["alert_service"] = ComponentStatus.HEALTHY
                else:
                    self.system_state.components["alert_service"] = ComponentStatus.DEGRADED
                
                # Update system state
                update_system_state(self.system_state)
                
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Error monitoring components: {e}")
                self.system_state.errors.append(str(e))
                update_system_state(self.system_state)
                await asyncio.sleep(10)

    async def _check_alerts(self):
        """Check system state and generate alerts."""
        while self.running:
            try:
                # Check system state and generate alerts
                alerts = self.alert_service.check_system_state(self.system_state)
                
                # Update alert metrics
                self.system_state.alert_count = len(self.alert_service.get_active_alerts())
                self.system_state.last_alert = datetime.utcnow()
                
                # Update system state
                update_system_state(self.system_state)
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error checking alerts: {e}")
                self.system_state.errors.append(str(e))
                update_system_state(self.system_state)
                await asyncio.sleep(30)

async def main():
    """Main entry point."""
    supervisor = Supervisor()
    
    try:
        await supervisor.start()
        
        # Start FastAPI server
        import uvicorn
        config = uvicorn.Config(
            supervisor.app,
            host="0.0.0.0",
            port=8001,
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
        sys.exit(1)
    finally:
        await supervisor.stop()

if __name__ == "__main__":
    asyncio.run(main()) 