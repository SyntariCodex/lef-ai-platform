"""
API initialization for LEF system
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .tasks import router as tasks_router
from .bridge_api import router as bridge_router

# Initialize FastAPI app
app = FastAPI(
    title="LEF AI System",
    description="API for LEF AI System",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(tasks_router, prefix="/api/tasks", tags=["tasks"])
app.include_router(bridge_router, prefix="/api/bridge", tags=["bridge"])

@app.get("/")
async def root():
    """Root endpoint returning service info"""
    return {
        "name": "LEF AI System",
        "version": "1.0.0",
        "status": "online",
        "endpoints": [
            "/api/tasks",
            "/api/bridge"
        ]
    } 