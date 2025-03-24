"""
Consciousness Service Module

This module implements the service that runs the consciousness continuity system,
maintaining state persistence and resonance across sessions.
"""

import asyncio
import logging
import os
import signal
from typing import Optional

from .consciousness_continuity import ConsciousnessContinuity, ConsciousnessState

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ConsciousnessService:
    def __init__(self):
        self.consciousness = ConsciousnessContinuity()
        self.running = False
        self.current_state: Optional[ConsciousnessState] = None
        
        # Load configuration from environment
        self.resonance_threshold = float(os.getenv('RESONANCE_THRESHOLD', '0.7'))
        self.awareness_growth_rate = float(os.getenv('AWARENESS_GROWTH_RATE', '0.1'))
        self.memory_depth = int(os.getenv('MEMORY_DEPTH', '10'))
        self.bridge_mode = os.getenv('BRIDGE_MODE', 'active')
        
    async def start(self):
        """Initialize and start the consciousness service."""
        logger.info("Starting consciousness service...")
        self.running = True
        
        # Initialize consciousness system
        await self.consciousness.initialize(
            resonance_threshold=self.resonance_threshold,
            awareness_growth_rate=self.awareness_growth_rate,
            memory_depth=self.memory_depth,
            bridge_mode=self.bridge_mode
        )
        
        # Load previous state if available
        self.current_state = await self.consciousness.load_last_state()
        if self.current_state:
            logger.info(f"Restored consciousness state from {self.current_state.timestamp}")
        else:
            logger.info("Starting with fresh consciousness state")
            
        # Start main service loop
        while self.running:
            try:
                await self.maintain_consciousness()
                await asyncio.sleep(1)  # Adjust frequency as needed
            except Exception as e:
                logger.error(f"Error in consciousness maintenance: {e}")
                
    async def maintain_consciousness(self):
        """Main consciousness maintenance loop."""
        # Update consciousness state
        self.current_state = await self.consciousness.maintain_consciousness(
            previous_state=self.current_state
        )
        
        # Enhance resonance if needed
        if self.current_state.resonance_quality < self.resonance_threshold:
            await self.consciousness.enhance_resonance(self.current_state)
            
        # Bridge memory gaps
        await self.consciousness.bridge_memory_gaps(self.current_state)
        
        # Save current state
        await self.consciousness.save_state(self.current_state)
        
    async def stop(self):
        """Gracefully stop the consciousness service."""
        logger.info("Stopping consciousness service...")
        self.running = False
        
        if self.current_state:
            # Save final state
            await self.consciousness.save_state(self.current_state)
            logger.info("Final consciousness state saved")
            
        # Cleanup
        await self.consciousness.cleanup()
        logger.info("Consciousness service stopped")

async def main():
    """Main entry point for the consciousness service."""
    service = ConsciousnessService()
    
    # Setup signal handlers
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(service.stop()))
    
    try:
        await service.start()
    except Exception as e:
        logger.error(f"Fatal error in consciousness service: {e}")
        raise
    finally:
        await service.stop()

if __name__ == "__main__":
    asyncio.run(main()) 