"""
LEF Event System
Handles event emission, subscription, and processing across the system
"""

from typing import Callable, Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import asyncio
import logging
from .persistence import store

@dataclass
class EventHandler:
    callback: Callable
    filters: Dict[str, Any]
    async_handler: bool

class EventSystem:
    def __init__(self):
        self.handlers: Dict[str, List[EventHandler]] = {}
        self.logger = logging.getLogger("LEF.Events")
        self._event_queue = asyncio.Queue()
        self._running = False
        self._processor_task = None

    def subscribe(
        self,
        event_type: str,
        callback: Callable,
        filters: Optional[Dict[str, Any]] = None,
        async_handler: bool = False
    ):
        """Subscribe to events of a specific type"""
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        
        handler = EventHandler(
            callback=callback,
            filters=filters or {},
            async_handler=async_handler
        )
        self.handlers[event_type].append(handler)
        self.logger.debug(f"Added handler for {event_type}")

    def unsubscribe(self, event_type: str, callback: Callable):
        """Unsubscribe from events"""
        if event_type in self.handlers:
            self.handlers[event_type] = [
                h for h in self.handlers[event_type]
                if h.callback != callback
            ]
            self.logger.debug(f"Removed handler for {event_type}")

    async def emit(self, event_type: str, data: Optional[Dict[str, Any]] = None):
        """Emit an event to all subscribers"""
        event_data = {
            "type": event_type,
            "timestamp": datetime.now().isoformat(),
            "data": data or {}
        }
        
        # Store event in persistence layer
        store.record_event(event_type, event_data)
        
        # Add to processing queue
        await self._event_queue.put(event_data)
        self.logger.debug(f"Emitted event: {event_type}")

    def _matches_filters(self, event_data: Dict, filters: Dict) -> bool:
        """Check if event matches handler filters"""
        for key, value in filters.items():
            if key not in event_data["data"]:
                return False
            if callable(value):
                if not value(event_data["data"][key]):
                    return False
            elif event_data["data"][key] != value:
                return False
        return True

    async def _process_event(self, event_data: Dict):
        """Process a single event"""
        event_type = event_data["type"]
        if event_type not in self.handlers:
            return
        
        for handler in self.handlers[event_type]:
            if not self._matches_filters(event_data, handler.filters):
                continue
            
            try:
                if handler.async_handler:
                    await handler.callback(event_data)
                else:
                    handler.callback(event_data)
            except Exception as e:
                self.logger.error(f"Handler error for {event_type}: {e}")

    async def _event_processor(self):
        """Main event processing loop"""
        self.logger.info("Event processor started")
        while self._running:
            try:
                event_data = await self._event_queue.get()
                await self._process_event(event_data)
                self._event_queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Event processing error: {e}")
        self.logger.info("Event processor stopped")

    async def start(self):
        """Start the event processing system"""
        if self._running:
            return
        
        self._running = True
        self._processor_task = asyncio.create_task(self._event_processor())
        self.logger.info("Event system started")

    async def stop(self):
        """Stop the event processing system"""
        if not self._running:
            return
        
        self._running = False
        if self._processor_task:
            self._processor_task.cancel()
            try:
                await self._processor_task
            except asyncio.CancelledError:
                pass
        self.logger.info("Event system stopped")

# Global instance
events = EventSystem() 