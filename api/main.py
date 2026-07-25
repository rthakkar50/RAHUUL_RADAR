from fastapi import FastAPI, APIRouter, Request, status, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from utils.logger import get_logger
import time
import sys
import json
from application.swing_scanner_service import SwingScannerService

logger = get_logger(__name__)

# Initialize FastAPI App
app = FastAPI(
    title="RAHUUL_RADAR Mobile API",
    description="API for the RAHUUL_RADAR Flutter Mobile Application",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development, allow all. Update for production.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal Server Error", "error_message": str(exc)},
    )

# API Router Setup (Versioning)
v1_router = APIRouter(prefix="/api/v1")

# Root Endpoint
@app.get("/", tags=["General"])
async def root():
    return {"message": "Welcome to RAHUUL_RADAR Mobile API", "version": "1.0.0"}

# Health Endpoint
@v1_router.get("/health", tags=["Health"])
async def health_check():
    logger.info("Health check endpoint called")
    return {
        "status": "online",
        "timestamp": time.time(),
        "python_version": sys.version
    }

# Swing Scanner Endpoint
@v1_router.get("/scanner/swing", tags=["Scanner"])
async def run_swing_scanner():
    logger.info("Swing scanner endpoint called")
    try:
        service = SwingScannerService()
        results = service.execute_swing_scan()
        
        # Serialize results to ensure any custom objects, datetimes, decimals are JSON safe
        json_compatible_results = json.loads(json.dumps(results, default=str))
        return json_compatible_results
    except Exception as e:
        logger.error(f"Error executing swing scan: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# Include routers
app.include_router(v1_router)

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting RAHUUL_RADAR Mobile API on port 8000")
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
