"""
LEF Control Hub UI Application
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
import json
import asyncio
from typing import Dict, List
import logging

from ..api import app as lef_api
from ..models.task import Task, TaskStatus
from ..models.system_state import SystemState

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="LEF Control Hub")

# Mount static files
static_path = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Templates
templates = Jinja2Templates(directory=str(static_path / "templates"))

# WebSocket connections
active_connections: List[WebSocket] = []

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.get("/", response_class=HTMLResponse)
async def root(request):
    """Serve the main UI."""
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates."""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle incoming messages
            await handle_message(data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

async def handle_message(message: str):
    """Handle incoming WebSocket messages."""
    try:
        data = json.loads(message)
        action = data.get("action")
        
        if action == "get_status":
            # Get system status
            status = await get_system_status()
            await manager.broadcast(json.dumps({
                "type": "status",
                "data": status
            }))
        elif action == "get_tasks":
            # Get tasks
            tasks = await get_tasks()
            await manager.broadcast(json.dumps({
                "type": "tasks",
                "data": tasks
            }))
        elif action == "update_task":
            # Update task
            task_id = data.get("task_id")
            updates = data.get("updates")
            await update_task(task_id, updates)
            # Broadcast updated tasks
            tasks = await get_tasks()
            await manager.broadcast(json.dumps({
                "type": "tasks",
                "data": tasks
            }))
    except Exception as e:
        logger.error(f"Error handling message: {e}")
        await manager.broadcast(json.dumps({
            "type": "error",
            "message": str(e)
        }))

async def get_system_status() -> Dict:
    """Get current system status."""
    # This would normally come from the LEF API
    return {
        "status": "operational",
        "components": {
            "supervisor": "running",
            "api": "running",
            "database": "connected"
        },
        "resources": {
            "cpu": "45%",
            "memory": "60%",
            "disk": "30%"
        }
    }

async def get_tasks() -> List[Dict]:
    """Get all tasks."""
    # This would normally come from the LEF API
    return [
        {
            "id": 1,
            "name": "System Initialization",
            "status": "completed",
            "progress": 100
        },
        {
            "id": 2,
            "name": "API Setup",
            "status": "in_progress",
            "progress": 75
        }
    ]

async def update_task(task_id: int, updates: Dict):
    """Update a task."""
    # This would normally go to the LEF API
    logger.info(f"Updating task {task_id} with {updates}") 