# PURPOSE: FastAPI application entry point for Chainsaw backend
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import audit_router

# Create FastAPI app
app = FastAPI(
    title="Chainsaw API",
    description="Cutting through supply chain threats",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS - allow all origins for public API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,  # Must be False when using "*"
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(audit_router)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": "Chainsaw API",
        "version": "1.0.0",
        "description": "Cutting through supply chain threats",
        "docs": "/docs",
        "health": "/api/health",
    }
