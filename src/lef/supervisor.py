"""
Supervisor module for the LEF system.
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Optional

from .database import init_db
from .api import app
import uvicorn

class Supervisor:
    """Supervisor for managing LEF system components."""
    
    def __init__(self):
        """Initialize the supervisor."""
        self.logger = logging.getLogger(__name__)
        self.api_server: Optional[uvicorn.Server] = None
        
        # Set up logging
        log_dir = Path.home() / ".lef" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_dir / "supervisor.log")
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        self.logger.addHandler(file_handler)
        self.logger.setLevel(logging.INFO)
    
    async def start(self):
        """Start the LEF system."""
        try:
            self.logger.info("Starting LEF system...")
            
            # Initialize database
            self.logger.info("Initializing database...")
            init_db()
            self.logger.info("Database initialized")
            
            # Start API server
            self.logger.info("Starting API server...")
            config = uvicorn.Config(
                app,
                host="0.0.0.0",
                port=8001,
                log_level="info"
            )
            self.api_server = uvicorn.Server(config)
            await self.api_server.serve()
            
        except Exception as e:
            self.logger.error(f"Error starting LEF system: {e}")
            raise
    
    async def stop(self):
        """Stop the LEF system."""
        try:
            self.logger.info("Stopping LEF system...")
            
            if self.api_server:
                self.logger.info("Stopping API server...")
                self.api_server.should_exit = True
                await self.api_server.shutdown()
                self.logger.info("API server stopped")
            
            self.logger.info("LEF system stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping LEF system: {e}")
            raise

async def main():
    """Main entry point."""
    supervisor = Supervisor()
    try:
        await supervisor.start()
    except KeyboardInterrupt:
        await supervisor.stop()
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 