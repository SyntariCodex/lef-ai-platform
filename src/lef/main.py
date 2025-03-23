"""
Main FastAPI application
"""

import logging
from fastapi import FastAPI, Request, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .api import (
    auth_api,
    rbac_api,
    security_api,
    encryption_api,
    rate_limit_api,
    ai_bridge_api,
    project_template_api,
    project_api,
    simulation_api,
    risk_analysis_api,
    performance_metrics_api,
    timeline_management_api,
    resource_allocation_api,
    cost_estimation_api,
    success_criteria_api,
    resource_management_api,
    meta_learning_api
)
from .middleware.rate_limit_middleware import RateLimitMiddleware
from .middleware.security_headers_middleware import SecurityHeadersMiddleware
from .middleware.request_validation_middleware import RequestValidationMiddleware
from .services.security_service import SecurityService
from .services.encryption_service import EncryptionService
from .services.rate_limit_service import RateLimitService
from .services.logging_service import LoggingService
from .services.ai_bridge_service import AIBridgeService
from .services.project_template_service import ProjectTemplateService
from .services import (
    ProjectService,
    SimulationService,
    RiskAnalysisService,
    PerformanceMetricsService,
    TimelineManagementService,
    ResourceAllocationService,
    CostEstimationService,
    SuccessCriteriaService,
    ResourceManagementService,
    MetaLearningService
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="LEF AI Bridge System",
    description="AI Bridge System for Learning and Enhancement Framework",
    version="1.0.0"
)

# Initialize services
security_service = SecurityService()
encryption_service = EncryptionService()
rate_limit_service = RateLimitService()
logging_service = LoggingService()
ai_bridge_service = AIBridgeService()
project_template_service = ProjectTemplateService()
project_service = ProjectService()
simulation_service = SimulationService()
risk_analysis_service = RiskAnalysisService()
performance_metrics_service = PerformanceMetricsService()
timeline_management_service = TimelineManagementService()
resource_allocation_service = ResourceAllocationService()
cost_estimation_service = CostEstimationService()
success_criteria_service = SuccessCriteriaService()
resource_management_service = ResourceManagementService()
meta_learning_service = MetaLearningService()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add security middlewares
app.add_middleware(RequestValidationMiddleware)  # First, validate requests
app.add_middleware(SecurityHeadersMiddleware)    # Then, add security headers
app.add_middleware(RateLimitMiddleware)          # Finally, apply rate limiting

# Include routers
app.include_router(auth_api.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(rbac_api.router, prefix="/api/rbac", tags=["RBAC"])
app.include_router(security_api.router, prefix="/api/security", tags=["Security"])
app.include_router(encryption_api.router, prefix="/api/encryption", tags=["Encryption"])
app.include_router(rate_limit_api.router, prefix="/api/rate-limit", tags=["Rate Limiting"])
app.include_router(ai_bridge_api.router, prefix="/api/ai-bridge", tags=["AI Bridge"])
app.include_router(project_template_api.router, prefix="/api/project-templates", tags=["Project Templates"])
app.include_router(
    project_api.router,
    prefix="/api/projects",
    tags=["Projects"]
)
app.include_router(
    simulation_api.router,
    prefix="/api/simulations",
    tags=["Simulations"]
)
app.include_router(
    risk_analysis_api.router,
    prefix="/api/risks",
    tags=["Risk Analysis"]
)
app.include_router(
    performance_metrics_api.router,
    prefix="/api/metrics",
    tags=["Performance Metrics"]
)
app.include_router(
    timeline_management_api.router,
    prefix="/api/timeline",
    tags=["Timeline Management"]
)
app.include_router(
    resource_allocation_api.router,
    prefix="/api/resources",
    tags=["Resource Allocation"]
)
app.include_router(
    cost_estimation_api.router,
    prefix="/api/costs",
    tags=["Cost Estimation"]
)
app.include_router(
    success_criteria_api.router,
    prefix="/api/success-criteria",
    tags=["Success Criteria"]
)
app.include_router(
    resource_management_api.router,
    prefix="/api/resources",
    tags=["Resource Management"]
)
app.include_router(
    meta_learning_api.router,
    prefix="/api/meta-learning",
    tags=["Meta Learning"]
)

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    try:
        await security_service.initialize()
        await encryption_service.initialize()
        await rate_limit_service.initialize()
        await logging_service.initialize()
        await ai_bridge_service.initialize()
        await project_template_service.initialize()
        await project_service.initialize()
        await simulation_service.initialize()
        await risk_analysis_service.initialize()
        await performance_metrics_service.initialize()
        await timeline_management_service.initialize()
        await resource_allocation_service.initialize()
        await cost_estimation_service.initialize()
        await success_criteria_service.initialize()
        await resource_management_service.initialize()
        await meta_learning_service.initialize()
        logger.info("All services initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up services on shutdown"""
    try:
        await rate_limit_service.cleanup()
        await project_service.cleanup()
        await simulation_service.cleanup()
        await risk_analysis_service.cleanup()
        await performance_metrics_service.cleanup()
        await timeline_management_service.cleanup()
        await resource_allocation_service.cleanup()
        await cost_estimation_service.cleanup()
        await success_criteria_service.cleanup()
        await resource_management_service.cleanup()
        await meta_learning_service.cleanup()
        logger.info("Services cleaned up successfully")
    except Exception as e:
        logger.error(f"Failed to clean up services: {e}")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to LEF AI Bridge System",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check services health
        project_health = await project_service.check_health()
        simulation_health = await simulation_service.check_health()
        risk_analysis_health = await risk_analysis_service.check_health()
        performance_metrics_health = await performance_metrics_service.check_health()
        timeline_health = await timeline_management_service.check_health()
        resource_allocation_health = await resource_allocation_service.check_health()
        cost_estimation_health = await cost_estimation_service.check_health()
        success_criteria_health = await success_criteria_service.check_health()
        resource_management_health = await resource_management_service.check_health()
        meta_learning_health = await meta_learning_service.check_health()
        
        return {
            "status": "healthy",
            "services": {
                "project": project_health,
                "simulation": simulation_health,
                "risk_analysis": risk_analysis_health,
                "performance_metrics": performance_metrics_health,
                "timeline_management": timeline_health,
                "resource_allocation": resource_allocation_health,
                "cost_estimation": cost_estimation_health,
                "success_criteria": success_criteria_health,
                "resource_management": resource_management_health,
                "meta_learning": meta_learning_health
            }
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        ) 