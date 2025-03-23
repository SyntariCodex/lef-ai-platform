from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import json
import logging
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Setup templates and static files
templates = Jinja2Templates(directory=str(Path(__file__).parent / "static" / "templates"))
router.mount("/static", StaticFiles(directory=str(Path(__file__).parent / "static")), name="static")

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: Dict[str, Any]):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting message: {e}")
                self.disconnect(connection)

manager = ConnectionManager()

@router.get("/", response_class=HTMLResponse)
async def get_ui(request: Request):
    """Serve the main UI page."""
    return templates.TemplateResponse("index.html", {"request": request})

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Handle WebSocket connections for real-time updates."""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                await handle_websocket_message(message)
            except json.JSONDecodeError:
                logger.error("Invalid JSON received")
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid message format"
                })
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

async def handle_websocket_message(message: Dict[str, Any]):
    """Handle incoming WebSocket messages."""
    action = message.get("action")
    if not action:
        return

    try:
        if action == "get_status":
            # TODO: Implement status retrieval from supervisor
            await manager.broadcast({
                "type": "status",
                "data": {
                    "status": "running",
                    "components": {
                        "Supervisor": "running",
                        "API Server": "running",
                        "Database": "running"
                    },
                    "resources": {
                        "CPU": "45%",
                        "Memory": "60%",
                        "Disk": "30%"
                    }
                }
            })
        elif action == "get_tasks":
            # TODO: Implement task retrieval from database
            await manager.broadcast({
                "type": "tasks",
                "data": [
                    {
                        "id": 1,
                        "name": "Implement Task Management",
                        "status": "in_progress",
                        "progress": 75
                    }
                ]
            })
        elif action == "update_task":
            task_id = message.get("task_id")
            updates = message.get("updates")
            if not task_id or not updates:
                raise ValueError("Missing task_id or updates")
            
            # TODO: Implement task update in database
            await manager.broadcast({
                "type": "success",
                "message": f"Task {task_id} updated successfully"
            })
        elif action == "create_task":
            task = message.get("task")
            if not task:
                raise ValueError("Missing task data")
            
            # TODO: Implement task creation in database
            await manager.broadcast({
                "type": "success",
                "message": "Task created successfully"
            })
        else:
            await manager.broadcast({
                "type": "error",
                "message": f"Unknown action: {action}"
            })
    except Exception as e:
        logger.error(f"Error handling message: {e}")
        await manager.broadcast({
            "type": "error",
            "message": str(e)
        }) 