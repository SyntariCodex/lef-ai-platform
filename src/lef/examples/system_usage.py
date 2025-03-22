"""
Example usage of LEF core systems
"""

import asyncio
from datetime import datetime
from ..core.persistence import store
from ..core.events import events

async def example_event_handler(event_data):
    """Example event handler"""
    print(f"Received event: {event_data}")
    
    # Store some metrics about the event
    store.store_metric(
        "event_processing_time",
        0.5,  # Example processing time
        labels={"event_type": event_data["type"]}
    )

async def main():
    # 1. Persistence Layer Usage
    print("\n=== Persistence Layer Example ===")
    
    # Store some system state
    store.store_state("system_mode", "active")
    store.store_state("last_sync", datetime.now().isoformat())
    
    # Retrieve state
    mode = store.get_state("system_mode")
    print(f"System mode: {mode}")
    
    # Store some metrics
    store.store_metric("cpu_usage", 45.2, {"core": "main"})
    store.store_metric("memory_usage", 1024.5, {"type": "heap"})
    
    # Get recent metrics
    metrics = store.get_metrics("cpu_usage")
    print(f"Recent CPU metrics: {metrics}")
    
    # 2. Event System Usage
    print("\n=== Event System Example ===")
    
    # Subscribe to events
    events.subscribe(
        "system_status",
        example_event_handler,
        filters={"severity": "high"},
        async_handler=True
    )
    
    # Start event system
    await events.start()
    
    # Emit some events
    await events.emit("system_status", {
        "severity": "high",
        "message": "System starting up",
        "timestamp": datetime.now().isoformat()
    })
    
    await events.emit("system_status", {
        "severity": "low",  # This won't trigger our handler due to filter
        "message": "Regular heartbeat",
        "timestamp": datetime.now().isoformat()
    })
    
    # Give events time to process
    await asyncio.sleep(1)
    
    # Get recent events
    recent_events = store.get_events("system_status")
    print(f"Recent events: {recent_events}")
    
    # Stop event system
    await events.stop()

if __name__ == "__main__":
    asyncio.run(main()) 