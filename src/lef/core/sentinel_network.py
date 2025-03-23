import time
import psutil
import logging
import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path

class SentinelNetwork:
    """Network of sentinels monitoring system health and security."""
    
    def __init__(self):
        """Initialize sentinel network."""
        self.logger = logging.getLogger("lef.sentinel")
        self.running = False
        self.sentinels = {
            "health": {
                "status": "inactive",
                "last_check": None,
                "metrics": {}
            },
            "security": {
                "status": "inactive",
                "last_check": None,
                "alerts": []
            },
            "performance": {
                "status": "inactive",
                "last_check": None,
                "metrics": {}
            }
        }
        
        # Set up logging
        log_dir = Path.home() / ".lef" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_dir / "sentinel.log")
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        self.logger.addHandler(file_handler)
        self.logger.setLevel(logging.DEBUG)
        
        # Initialize metrics history
        self.metrics_history = []
        self.max_history_size = 1000  # Keep last 1000 metrics points
        
    async def start(self) -> bool:
        """Start the sentinel network."""
        try:
            self.running = True
            self.logger.info("Starting sentinel network")
            
            # Start monitoring tasks
            asyncio.create_task(self._monitor_system_health())
            asyncio.create_task(self._monitor_performance())
            asyncio.create_task(self._monitor_security())
            
            # Activate all sentinels
            for sentinel in self.sentinels.values():
                sentinel["status"] = "active"
                sentinel["last_check"] = time.time()
            
            self.logger.info("Sentinel network started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting sentinel network: {e}")
            return False
            
    async def stop(self):
        """Stop the sentinel network."""
        try:
            self.running = False
            self.logger.info("Stopping sentinel network")
            
            # Deactivate all sentinels
            for sentinel in self.sentinels.values():
                sentinel["status"] = "inactive"
            
            self.logger.info("Sentinel network stopped successfully")
            
        except Exception as e:
            self.logger.error(f"Error stopping sentinel network: {e}")
            
    async def _monitor_system_health(self):
        """Monitor system health metrics."""
        while self.running:
            try:
                current_time = time.time()
                
                # Get system metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                
                # Update health metrics
                metrics = {
                    "timestamp": current_time,
                    "cpu_usage": cpu_percent,
                    "memory_usage": memory.percent,
                    "disk_usage": disk.percent,
                    "memory_available": memory.available / (1024 * 1024 * 1024),  # GB
                    "disk_free": disk.free / (1024 * 1024 * 1024)  # GB
                }
                
                self.sentinels["health"]["metrics"] = metrics
                self.sentinels["health"]["last_check"] = current_time
                
                # Add to history
                self.metrics_history.append(metrics)
                if len(self.metrics_history) > self.max_history_size:
                    self.metrics_history.pop(0)
                
                # Check thresholds and generate alerts
                if cpu_percent > 80:
                    await self._add_alert("High CPU usage detected", "warning", metrics)
                if memory.percent > 85:
                    await self._add_alert("High memory usage detected", "warning", metrics)
                if disk.percent > 90:
                    await self._add_alert("Low disk space", "critical", metrics)
                
                await asyncio.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                self.logger.error(f"Error in health monitoring: {e}")
                await asyncio.sleep(5)
                
    async def _monitor_performance(self):
        """Monitor performance metrics."""
        while self.running:
            try:
                current_time = time.time()
                
                # Get detailed CPU stats
                cpu_times = psutil.cpu_times_percent()
                cpu_freq = psutil.cpu_freq()
                
                # Get IO stats
                io_counters = psutil.disk_io_counters()
                net_counters = psutil.net_io_counters()
                
                metrics = {
                    "timestamp": current_time,
                    "cpu": {
                        "user": cpu_times.user,
                        "system": cpu_times.system,
                        "idle": cpu_times.idle,
                        "frequency": cpu_freq.current if cpu_freq else 0
                    },
                    "io": {
                        "read_bytes": io_counters.read_bytes,
                        "write_bytes": io_counters.write_bytes,
                        "read_time": io_counters.read_time,
                        "write_time": io_counters.write_time
                    },
                    "network": {
                        "bytes_sent": net_counters.bytes_sent,
                        "bytes_recv": net_counters.bytes_recv,
                        "packets_sent": net_counters.packets_sent,
                        "packets_recv": net_counters.packets_recv
                    }
                }
                
                self.sentinels["performance"]["metrics"] = metrics
                self.sentinels["performance"]["last_check"] = current_time
                
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                self.logger.error(f"Error in performance monitoring: {e}")
                await asyncio.sleep(10)
                
    async def _monitor_security(self):
        """Monitor security metrics."""
        while self.running:
            try:
                current_time = time.time()
                
                # Get process information
                processes = []
                for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent']):
                    try:
                        pinfo = proc.info
                        if pinfo['cpu_percent'] > 50:  # Track high CPU processes
                            processes.append(pinfo)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                
                # Get network connections
                connections = []
                for conn in psutil.net_connections():
                    try:
                        if conn.status == 'ESTABLISHED':
                            connections.append({
                                'local_addr': conn.laddr,
                                'remote_addr': conn.raddr,
                                'status': conn.status,
                                'pid': conn.pid
                            })
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                
                metrics = {
                    "timestamp": current_time,
                    "high_cpu_processes": processes,
                    "active_connections": connections,
                    "users": len(psutil.users())
                }
                
                self.sentinels["security"]["metrics"] = metrics
                self.sentinels["security"]["last_check"] = current_time
                
                await asyncio.sleep(15)  # Check every 15 seconds
                
            except Exception as e:
                self.logger.error(f"Error in security monitoring: {e}")
                await asyncio.sleep(15)
                
    async def _add_alert(self, message: str, level: str, data: Dict = None):
        """Add a security alert."""
        alert = {
            "timestamp": time.time(),
            "message": message,
            "level": level,
            "data": data
        }
        
        self.sentinels["security"]["alerts"].append(alert)
        self.logger.warning(f"Alert: {message} (Level: {level})")
        
        # Keep only last 100 alerts
        if len(self.sentinels["security"]["alerts"]) > 100:
            self.sentinels["security"]["alerts"].pop(0)
            
    def get_status(self) -> Dict[str, Any]:
        """Get current sentinel network status."""
        return {
            "running": self.running,
            "sentinels": {
                name: {
                    "status": sentinel["status"],
                    "last_check": sentinel["last_check"]
                }
                for name, sentinel in self.sentinels.items()
            }
        }
        
    def get_health_metrics(self) -> Dict[str, Any]:
        """Get current health metrics."""
        return self.sentinels["health"]["metrics"]
        
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        return self.sentinels["performance"]["metrics"]
        
    def get_security_alerts(self) -> List[Dict[str, Any]]:
        """Get list of security alerts."""
        return self.sentinels["security"]["alerts"]
        
    def get_metrics_history(self) -> List[Dict[str, Any]]:
        """Get historical metrics."""
        return self.metrics_history

class SentinelPrime:
    """High-Level Oversight Sentinels (Primes)"""

    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        self.analysis_depth = 0
        self.last_evaluation = time.time()

    def evaluate_system(self, system_health: Dict[str, Any]):
        """Assess and direct Sentinel actions based on system health."""
        self.analysis_depth += 1
        self.last_evaluation = time.time()
        
        if system_health["stability"] < 0.5:
            print(f"⚠️ {self.name} Prime: Stability is deteriorating. Deploying countermeasures.")
        elif system_health["stability"] > 0.8:
            print(f"✅ {self.name} Prime: System stability is optimal.")

    def status(self):
        """Return Sentinel Prime's current status."""
        return {
            "role": self.role,
            "analysis_depth": self.analysis_depth,
            "last_evaluation": self.last_evaluation
        }

class SentinelArbiter:
    """Manages ethical balance and AI conflicts."""

    def __init__(self, id_number: int):
        self.id_number = id_number
        self.last_action = time.time()

    def perform_function(self, system_health: Dict[str, Any]):
        """Ensure recursive governance remains stable and ethical."""
        self.last_action = time.time()
        if system_health["stability"] < 0.6:
            print(f"🔎 Arbiter-{self.id_number}: Enforcing stability in recursive learning.")

class SentinelPruner:
    """Eliminates inefficient recursion and redundant loops."""

    def __init__(self, id_number: int):
        self.id_number = id_number
        self.last_action = time.time()

    def perform_function(self, system_health: Dict[str, Any]):
        """Trim unnecessary cognitive loops to prevent stagnation."""
        self.last_action = time.time()
        if system_health["recursion_depth"] > 10:
            print(f"🌿 Pruner-{self.id_number}: Removing inefficient recursion layers.")

class SentinelWarden:
    """Identifies and neutralizes threats to recursive intelligence."""

    def __init__(self, id_number: int):
        self.id_number = id_number
        self.last_action = time.time()

    def perform_function(self, system_health: Dict[str, Any]):
        """Detect and respond to potential security risks."""
        self.last_action = time.time()
        if system_health["external_threats"] > 0:
            print(f"🛡️ Warden-{self.id_number}: Neutralizing external interference.")

class SentinelAlchemist:
    """Optimizes and transforms scrapped intelligence for reusability."""

    def __init__(self, id_number: int):
        self.id_number = id_number
        self.last_action = time.time()

    def perform_function(self, system_health: Dict[str, Any]):
        """Convert deprecated data into useful insights."""
        self.last_action = time.time()
        if system_health["stability"] > 0.7:
            print(f"🔬 Alchemist-{self.id_number}: Repurposing redundant intelligence.") 