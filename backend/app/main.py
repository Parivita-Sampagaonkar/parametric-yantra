"""
FastAPI main application entry point
Parametric Yantra Generator Backend v0.6
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import logging
import time

from app.config import settings
from app.database import engine, Base
from app.api import generate, validate, export_router, astronomy

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    logger.info("🚀 Starting Parametric Yantra Generator API")
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Database tables created/verified")
    yield
    # Shutdown
    logger.info("👋 Shutting down API")

# Initialize FastAPI app
app = FastAPI(
    title="Parametric Yantra Generator API",
    description="Generate historically accurate astronomical instruments with modern parametric CAD",
    version="0.6.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Process-Time"]
)

# Compression middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Request ID and timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add request ID and processing time headers"""
    request_id = request.headers.get("X-Request-ID", f"req_{int(time.time() * 1000)}")
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(round(process_time * 1000, 2))
    response.headers["X-Request-ID"] = request_id
    
    return response

# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with detailed messages"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": exc.errors(),
            "message": "Validation error in request data"
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Catch-all exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "message": "Internal server error",
            "detail": str(exc) if settings.DEBUG else "An unexpected error occurred"
        }
    )

# Include routers
app.include_router(generate.router, prefix="/api/v1/generate", tags=["Generation"])
app.include_router(validate.router, prefix="/api/v1/validate", tags=["Validation"])
app.include_router(export_router.router, prefix="/api/v1/export", tags=["Export"])
app.include_router(astronomy.router, prefix="/api/v1/astronomy", tags=["Astronomy"])

# Health check endpoints
@app.get("/health", tags=["Health"])
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "version": "0.6.0",
        "timestamp": time.time()
    }

@app.get("/health/ready", tags=["Health"])
async def readiness_check():
    """Readiness check with dependency verification"""
    from app.database import SessionLocal
    from redis import Redis
    
    checks = {
        "database": False,
        "redis": False
    }
    
    # Database check
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        checks["database"] = True
    except Exception as e:
        logger.error(f"Database check failed: {e}")
    
    # Redis check (if configured)
    try:
        if settings.REDIS_URL:
            redis_client = Redis.from_url(settings.REDIS_URL)
            redis_client.ping()
            checks["redis"] = True
    except Exception as e:
        logger.error(f"Redis check failed: {e}")
    
    all_healthy = all(checks.values())
    return {
        "ready": all_healthy,
        "checks": checks,
        "timestamp": time.time()
    }

@app.get("/", tags=["Root"])
async def root():
    """API root - welcome message"""
    return {
        "message": "Parametric Yantra Generator API",
        "version": "0.6.0",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "generate": "/api/v1/generate",
            "validate": "/api/v1/validate",
            "export": "/api/v1/export",
            "astronomy": "/api/v1/astronomy"
        }
    }

# Development/debug endpoints
if settings.DEBUG:
    @app.get("/debug/config", tags=["Debug"])
    async def debug_config():
        """Show current configuration (debug only)"""
        return {
            "environment": settings.ENVIRONMENT,
            "debug": settings.DEBUG,
            "cors_origins": settings.CORS_ORIGINS,
            "database_configured": bool(settings.DATABASE_URL),
            "redis_configured": bool(settings.REDIS_URL),
            "r2_configured": bool(settings.R2_ACCOUNT_ID)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )