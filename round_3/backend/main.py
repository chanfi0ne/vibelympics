# PURPOSE: FastAPI application entry point for PARANOID SBOM Roast Generator
# Provides /healthz and /roast endpoints with paranoia-aware responses

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import random

app = FastAPI(
    title="PARANOID",
    description="SBOM Roast Generator - Paste your dependencies. Get roasted. Question everything.",
    version="0.1.0"
)

# CORS - permissive for now, tighten later
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory state
stats = {
    "roasts_completed": 0,
    "dependencies_judged": 0,
    "sboms_generated": 0,
    "sboms_that_were_complete": 0  # Always 0. As is tradition.
}

HEALTH_MESSAGES = [
    "All systems nominal. Dependencies roasted: {roasts}. Existential crises: 0 (so far).",
    "Operational. I've analyzed {deps} dependencies today. I have opinions about all of them.",
    "Functioning within acceptable parameters. My SBOM says I'm healthy. I don't trust it.",
]


@app.get("/healthz")
async def healthz():
    """Neurotic health check endpoint."""
    message = random.choice(HEALTH_MESSAGES).format(
        roasts=stats["roasts_completed"],
        deps=stats["dependencies_judged"]
    )
    return {
        "status": "healthy",
        "message": message,
        "paranoia_level": 0,
        "roasts_completed": stats["roasts_completed"],
        "dependencies_judged": stats["dependencies_judged"],
        "sboms_generated": stats["sboms_generated"],
        "sboms_that_were_complete": stats["sboms_that_were_complete"]
    }


@app.get("/")
async def root():
    """Root endpoint - redirect to docs or show welcome."""
    return {
        "name": "PARANOID",
        "tagline": "Paste your dependencies. Get roasted. Question everything.",
        "endpoints": {
            "health": "/healthz",
            "roast": "/roast (POST)",
            "docs": "/docs"
        }
    }
