# PURPOSE: FastAPI application entry point for Repojacker backend
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import audit_router

# Create FastAPI app
app = FastAPI(
    title="Repojacker API",
    description="npm supply chain security auditor",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",  # Vite dev server
        "http://frontend",
        "http://frontend:80",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(audit_router)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": "Repojacker API",
        "version": "1.0.0",
        "description": "npm supply chain security auditor",
        "docs": "/docs",
        "health": "/api/health",
    }
