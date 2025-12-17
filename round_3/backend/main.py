# PURPOSE: FastAPI application entry point for PARANOID SBOM Roast Generator
# Provides /healthz and /roast endpoints with paranoia-aware responses

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Literal, Optional
import random
import uuid


class RoastRequest(BaseModel):
    input_type: Literal["package_json", "requirements_txt", "go_mod", "sbom", "single_package"]
    content: str
    include_sbom: bool = True


class Finding(BaseModel):
    type: str
    severity: str
    detail: str


class RoastResponse(BaseModel):
    meme_url: str
    meme_id: str
    roast_summary: str
    findings: list[Finding]
    caption: str
    template_used: str
    sbom: Optional[dict] = None
    paranoia: dict
    signature: Optional[str] = None

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


# Stub roast captions - will be replaced with caption library
STUB_CAPTIONS = [
    "Your dependencies are a disaster. This is fine.",
    "{count} dependencies for a todo app. Bold move.",
    "I've seen better supply chains in a haunted house.",
    "Your SBOM is technically accurate and practically useless. As is tradition.",
    "node_modules heavier than my existential dread.",
]


@app.post("/roast", response_model=RoastResponse)
async def roast(request: RoastRequest):
    """Main roast endpoint - analyzes dependencies and generates meme."""

    # Stub: count "dependencies" (lines or entries)
    content = request.content.strip()
    if not content:
        raise HTTPException(
            status_code=400,
            detail="Your input is empty. Much like your security strategy."
        )

    # Very basic "analysis" - just count lines for now
    lines = [l for l in content.split('\n') if l.strip()]
    dep_count = len(lines)

    # Update stats
    stats["roasts_completed"] += 1
    stats["dependencies_judged"] += dep_count
    stats["sboms_generated"] += 1 if request.include_sbom else 0

    # Generate stub response
    meme_id = str(uuid.uuid4())[:8]
    caption = random.choice(STUB_CAPTIONS).format(count=dep_count)

    # Stub findings
    findings = [
        Finding(
            type="dependency_count",
            severity="high" if dep_count > 50 else "medium" if dep_count > 10 else "low",
            detail=f"{dep_count} dependencies detected"
        )
    ]

    # Stub SBOM (sarcastic)
    sbom = None
    if request.include_sbom:
        sbom = {
            "format": "CycloneDX",
            "version": "1.4",
            "confidence": "LOW",
            "confidence_explanation": "This SBOM lists some components. Not all. Never all.",
            "completeness_score": f"{random.randint(15, 35)}%",
            "completeness_note": f"We found {dep_count} components. We probably missed {dep_count * 3}.",
            "will_prevent_next_attack": False,
            "will_make_auditors_happy": True,
            "components": []  # Stub - will populate later
        }

    return RoastResponse(
        meme_url=f"/memes/{meme_id}.png",  # Stub URL - meme gen comes later
        meme_id=meme_id,
        roast_summary=f"You have {dep_count} dependencies. Your SBOM completeness is estimated at {random.randint(15,35)}%. This is fine.",
        findings=findings,
        caption=caption,
        template_used="this-is-fine",  # Stub
        sbom=sbom,
        paranoia={
            "level": 0,
            "level_name": "CHILL",
            "message": "Roast complete. Your dependencies are a disaster, but at least I'm functioning normally. For now."
        }
    )
