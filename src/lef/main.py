from lef.core.lef import LEF
import time
import signal
import sys
import threading
import logging
import os
from fastapi import FastAPI, HTTPException
import uvicorn
from typing import Dict, Any

# Get environment variables with defaults
LOG_LEVEL = os.getenv('LEF_LOG_LEVEL', 'INFO')
LOG_PATH = os.getenv('LEF_LOG_PATH', '/opt/lef/logs')
METRICS_INTERVAL = int(os.getenv('LEF_METRICS_INTERVAL', '60'))
HEALTH_CHECK_INTERVAL = int(os.getenv('LEF_HEALTH_CHECK_INTERVAL', '30'))
PORT = int(os.getenv('LEF_PORT', '8000'))

# Configure logging
os.makedirs(LOG_PATH, exist_ok=True)
log_file = os.path.join(LOG_PATH, 'lef.log')

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_file)
    ]
)
logger = logging.getLogger('LEF')

# Create FastAPI app
app = FastAPI(title="LEF API", version="1.0.0")

# Global LEF instance
lef_instance = None

def signal_handler(signum, frame):
    """Handle shutdown signals."""
    logger.info("Received shutdown signal. Stopping LEF system...")
    global lef_instance
    if lef_instance:
        lef_instance.stop()
    sys.exit(0)

@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint."""
    global lef_instance
    if not lef_instance or not lef_instance.running:
        raise HTTPException(status_code=503, detail="LEF system is not running")
    
    try:
        state = lef_instance.express_state()
        metrics = lef_instance.get_metrics()
        
        return {
            "status": "healthy",
            "system_state": state.get("status", "unknown"),
            "uptime": metrics.get("uptime", 0),
            "system_health": metrics.get("system_health", 0)
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/metrics")
async def get_metrics() -> Dict[str, Any]:
    """Get system metrics."""
    global lef_instance
    if not lef_instance or not lef_instance.running:
        raise HTTPException(status_code=503, detail="LEF system is not running")
    
    try:
        state = lef_instance.express_state()
        metrics = lef_instance.get_metrics()
        
        return {
            "state": state,
            "metrics": metrics
        }
    except Exception as e:
        logger.error(f"Failed to get metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

def display_state(lef_system):
    """Display the current state of the LEF system with proper formatting"""
    try:
        # Get system state
        state = lef_system.express_state()
        metrics = lef_system.get_metrics()
        
        # Clear screen for better visibility
        print("\033[H\033[J")
        
        # Display active goals with progress
        print("\nActive Goals:")
        active_goals = [g for g in lef_system.goals if g.get('status') == 'in_progress']
        if active_goals:
            for goal in active_goals:
                progress = goal.get('progress', 0.0)
                progress_bar = "=" * int(progress * 20)
                progress_bar = progress_bar.ljust(20, "-")
                print(f"[{progress_bar}] {goal.get('description', 'Unknown Goal')} ({progress:.1%})")
        else:
            print("No active goals")
        
        # Display system status with emojis
        print("\n🚀 LEF System Status:")
        print(f"State: {state.get('status', 'Unknown').title()}")
        print(f"Uptime: {metrics.get('uptime', 0):.1f} seconds")
        print(f"System Health: {metrics.get('system_health', 0):.2f}")
        
        # Display core metrics
        print("\n📊 Core Metrics:")
        print(f"Awareness Level: {metrics.get('awareness_level', 0):.2f}")
        print(f"Learning Performance: {metrics.get('learning_performance', 0):.2f}")
        print(f"Business Efficiency: {metrics.get('business_efficiency', 0):.2f}")
        
        # Display project metrics
        print("\n📈 Project Metrics:")
        print(f"Success Rate: {state.get('project_success_rate', 0):.2f}")
        print(f"Proposal Quality: {state.get('proposal_quality', 0):.2f}")
        print(f"Error Rate: {state.get('error_rate', 0):.2f}")
        
        # Display project counts
        projects = state.get('projects', {})
        print("\n📋 Projects:")
        print(f"Proposed: {projects.get('proposed', 0)}")
        print(f"Active: {projects.get('active', 0)}")
        print(f"Completed: {projects.get('completed', 0)}")
        
    except Exception as e:
        logger.error(f"Error displaying state: {str(e)}")

def run_api_server():
    """Run the FastAPI server."""
    try:
        uvicorn.run(app, host="0.0.0.0", port=PORT)
    except Exception as e:
        logger.error(f"Failed to start API server: {str(e)}")
        sys.exit(1)

def main():
    """Main entry point for the LEF system."""
    try:
        # Register signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        logger.info("Initializing LEF system...")
        global lef_instance
        lef_instance = LEF()
        
        logger.info("Starting LEF system...")
        if not lef_instance.start():
            logger.error("Failed to start LEF system")
            sys.exit(1)
            
        logger.info("LEF system started successfully")
        
        # Start API server in a separate thread
        api_thread = threading.Thread(target=run_api_server)
        api_thread.daemon = True
        api_thread.start()
        
        # Main loop
        last_metrics_update = time.time()
        while True:
            try:
                current_time = time.time()
                
                # Update display if enough time has passed
                if current_time - last_metrics_update >= METRICS_INTERVAL:
                    display_state(lef_instance)
                    last_metrics_update = current_time
                
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error in main loop: {str(e)}")
                time.sleep(1)
                
    except Exception as e:
        logger.error(f"Critical error: {str(e)}")
        if lef_instance:
            lef_instance.stop()
        sys.exit(1)

if __name__ == "__main__":
    main() 