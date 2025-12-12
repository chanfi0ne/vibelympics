# PURPOSE: FastAPI application entry point for Chainsaw backend
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from routers import audit_router

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Create FastAPI app
app = FastAPI(
    title="Chainsaw API",
    description="Cutting through supply chain threats",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
        "https://vibelympics-production.up.railway.app",
        "https://chainsaw.up.railway.app",
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
        "service": "Chainsaw API",
        "version": "1.0.0",
        "description": "Cutting through supply chain threats",
        "docs": "/docs",
        "health": "/api/health",
    }
