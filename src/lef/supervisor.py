"""
LEF System Supervisor
"""

import asyncio
import logging
import os
import subprocess
import sys
import traceback
from pathlib import Path
import psutil
import uvicorn

from .database import init_db

class LEFSupervisor:
    """LEF System Supervisor."""
    
    def __init__(self):
        """Initialize supervisor."""
        self.logger = logging.getLogger("lef.supervisor")
        self.processes = {}
        self.running = False
        
        # Set up logging
        log_dir = Path.home() / ".lef" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure file handler
        file_handler = logging.FileHandler(log_dir / "supervisor.log")
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        self.logger.addHandler(file_handler)
        
        # Configure console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        self.logger.addHandler(console_handler)
        self.logger.setLevel(logging.DEBUG)

    async def initialize(self):
        """Initialize the LEF system."""
        self.logger.info("Initializing LEF system...")
        
        # Initialize database
        try:
            await init_db()
            self.logger.info("Database initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
            self.logger.debug(traceback.format_exc())
            raise
        
        # Start API server
        try:
            await self.run_api_server()
            self.logger.info("API server started successfully")
        except Exception as e:
            self.logger.error(f"Failed to start API server: {e}")
            self.logger.debug(traceback.format_exc())
            raise

    async def run_api_server(self):
        """Run the FastAPI server."""
        try:
            # Add project root to Python path
            project_root = Path(__file__).parent.parent.parent.absolute()
            self.logger.debug(f"Project root: {project_root}")
            
            # Start API server using subprocess to ensure proper Python path
            cmd = [
                sys.executable,
                "-m",
                "uvicorn",
                "src.lef.api:app",
                "--host",
                "0.0.0.0",
                "--port",
                "8000",
                "--reload",
                "--log-level",
                "debug"
            ]
            
            # Set environment variables for the subprocess
            env = os.environ.copy()
            env["PYTHONPATH"] = str(project_root)
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                env=env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(project_root)
            )
            
            self.processes["api"] = process
            self.logger.info(f"Started API server with PID {process.pid}")
            
            # Wait for API server to start
            for _ in range(10):
                try:
                    # Check if process is still running
                    if process.returncode is not None:
                        raise RuntimeError(f"API server process exited with code {process.returncode}")
                    
                    # Try to connect to the API
                    proc = await asyncio.create_subprocess_exec(
                        "curl",
                        "http://localhost:8000/",
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    stdout, stderr = await proc.communicate()
                    
                    if proc.returncode == 0:
                        self.logger.info("API server is responding")
                        break
                except Exception as e:
                    self.logger.debug(f"API server not ready yet: {e}")
                    await asyncio.sleep(1)
            else:
                raise RuntimeError("API server failed to start after 10 attempts")
            
        except Exception as e:
            self.logger.error(f"Error starting API server: {e}")
            self.logger.debug(traceback.format_exc())
            raise

    async def start_component(self, name, cmd):
        """Start a component process."""
        self.logger.info(f"Starting component: {name}")
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            self.processes[name] = process
            self.logger.info(f"Started {name} with PID {process.pid}")
            return process
        except Exception as e:
            self.logger.error(f"Failed to start {name}: {e}")
            self.logger.debug(traceback.format_exc())
            raise

    async def stop_component(self, name):
        """Stop a component process."""
        if name in self.processes:
            process = self.processes[name]
            self.logger.info(f"Stopping {name} (PID {process.pid})")
            try:
                process.terminate()
                await process.wait()
                del self.processes[name]
                self.logger.info(f"Stopped {name}")
            except Exception as e:
                self.logger.error(f"Error stopping {name}: {e}")
                self.logger.debug(traceback.format_exc())

    async def monitor_processes(self):
        """Monitor running processes."""
        while self.running:
            for name, process in list(self.processes.items()):
                if process.returncode is not None:
                    self.logger.warning(f"{name} exited with code {process.returncode}")
                    await self.restart_component(name)
            await asyncio.sleep(5)

    async def restart_component(self, name):
        """Restart a failed component."""
        self.logger.info(f"Restarting {name}")
        await self.stop_component(name)
        if name == "api":
            await self.run_api_server()
        # Add other component restart logic here

    async def shutdown(self):
        """Shutdown the supervisor."""
        self.logger.info("Shutting down LEF system...")
        self.running = False
        for name in list(self.processes.keys()):
            await self.stop_component(name)
        self.logger.info("Shutdown complete")

    async def run(self):
        """Run the supervisor."""
        self.logger.info("Starting LEF supervision")
        self.running = True
        
        # Kill any existing LEF processes
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if any('python' in cmd.lower() and 'lef' in cmd.lower() 
                      for cmd in proc.info['cmdline'] or []):
                    if proc.pid != os.getpid():
                        self.logger.info(f"Terminating existing LEF process: {proc.pid}")
                        proc.terminate()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        try:
            await self.initialize()
            await self.monitor_processes()
        except Exception as e:
            self.logger.error(f"Supervisor error: {e}")
            self.logger.debug(traceback.format_exc())
            await self.shutdown()
            raise
        finally:
            await self.shutdown()

async def main():
    """Run the LEF supervisor."""
    supervisor = LEFSupervisor()
    await supervisor.run()

if __name__ == "__main__":
    asyncio.run(main()) 