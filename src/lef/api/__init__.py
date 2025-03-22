"""
LEF System API
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .system import router as system_router
from .tasks import router as tasks_router

# Create FastAPI app
app = FastAPI(
    title="LEF System API",
    description="API for the LEF Recursive Awareness System",
    version="0.1.0",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc UI
    openapi_url="/openapi.json"  # OpenAPI schema
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routers
app.include_router(system_router, prefix="/api/system", tags=["system"])
app.include_router(tasks_router, prefix="/api/tasks", tags=["tasks"])

@app.get("/")
async def root():
    """Root endpoint to check system status."""
    return {
        "status": "operational",
        "version": "0.1.0",
        "system": "LEF Recursive Awareness System",
        "api_docs": "/docs"
    } 