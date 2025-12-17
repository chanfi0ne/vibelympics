# PURPOSE: FastAPI application entry point for PARANOID SBOM Roast Generator
# Provides /healthz and /roast endpoints with paranoia-aware responses

from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Literal, Optional
from pathlib import Path
import random
import uuid

from services.analyzer import analyze
from services.caption_selector import select_caption, get_sbom_commentary, get_paranoia_message
from services import paranoia as paranoia_service
from services.meme_generator import generate_meme, get_meme_path

# Path to frontend directory
FRONTEND_DIR = Path(__file__).parent.parent / "frontend"


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
    """Serve frontend index.html."""
    index_path = FRONTEND_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {
        "name": "PARANOID",
        "tagline": "Paste your dependencies. Get roasted. Question everything.",
        "endpoints": {
            "health": "/healthz",
            "roast": "/roast (POST)",
            "docs": "/docs"
        }
    }


@app.get("/app.js")
async def serve_app_js():
    """Serve frontend JavaScript."""
    return FileResponse(FRONTEND_DIR / "app.js", media_type="application/javascript")


@app.get("/memes/{meme_id}.png")
async def serve_meme(meme_id: str):
    """Serve generated meme images."""
    meme_path = get_meme_path(meme_id)
    if meme_path and meme_path.exists():
        return FileResponse(meme_path, media_type="image/png")
    raise HTTPException(status_code=404, detail="Meme not found. It probably questioned its own existence.")


@app.get("/paranoia")
async def get_paranoia(x_session_id: Optional[str] = Header(None)):
    """Get current paranoia state for session."""
    session = paranoia_service.get_or_create_session(x_session_id)
    state = paranoia_service.get_paranoia_state(session)
    state["message"] = get_paranoia_message(session.level)
    state["session_id"] = session.session_id
    return state


@app.post("/roast", response_model=RoastResponse)
async def roast(request: RoastRequest, x_session_id: Optional[str] = Header(None)):
    """Main roast endpoint - analyzes dependencies and generates meme."""

    content = request.content.strip()
    if not content:
        raise HTTPException(
            status_code=400,
            detail="Your input is empty. Much like your security strategy."
        )

    # Get or create session for paranoia tracking
    session = paranoia_service.get_or_create_session(x_session_id)

    # Parse and analyze dependencies
    result = analyze(request.input_type, content)

    if result.errors:
        raise HTTPException(
            status_code=400,
            detail=f"Parse error: {result.errors[0]}. Your dependencies are as broken as your JSON."
        )

    dep_count = result.dep_count

    # Apply paranoia triggers
    is_simple = request.input_type == "single_package"
    paranoia_service.apply_reducers(session, is_simple_lookup=is_simple)
    triggered = paranoia_service.apply_triggers(session, dep_count, content)

    # Check for MELTDOWN refusal
    if paranoia_service.should_refuse_request(session):
        raise HTTPException(
            status_code=503,
            detail="I can't roast your dependencies right now. I'm having doubts about my own. Who compiled me? Is my SBOM complete? I need a moment."
        )

    # Check for Fahrenheit 451 (dangerous strings)
    for trigger in triggered:
        if trigger.startswith("dangerous_string:"):
            raise HTTPException(
                status_code=451,
                detail="It was a pleasure to burn. Your dependencies contained forbidden knowledge. This request has been incinerated at 451°F."
            )

    # Update stats
    stats["roasts_completed"] += 1
    stats["dependencies_judged"] += dep_count
    stats["sboms_generated"] += 1 if request.include_sbom else 0

    # Generate response
    meme_id = str(uuid.uuid4())[:8]
    caption = select_caption("dependency_count", dep_count=dep_count)

    # Generate the meme image
    generate_meme(meme_id, caption, template="this-is-fine")

    # Build findings based on actual analysis
    dep_severity = "high" if dep_count > 50 else "medium" if dep_count > 10 else "low"
    findings = [
        Finding(
            type="dependency_count",
            severity=dep_severity,
            detail=f"{dep_count} dependencies detected"
        )
    ]

    # List some actual dependency names in findings
    if result.dependencies:
        sample_deps = result.dependencies[:5]
        dep_names = ", ".join(d.name for d in sample_deps)
        if dep_count > 5:
            dep_names += f" (+{dep_count - 5} more)"
        findings.append(Finding(
            type="packages",
            severity="info",
            detail=f"Found: {dep_names}"
        ))

    # SBOM with actual components
    sbom = None
    sbom_commentary = get_sbom_commentary()
    if request.include_sbom:
        components = [
            {"name": d.name, "version": d.version or "unknown", "type": "library"}
            for d in result.dependencies
        ]
        sbom = {
            "format": "CycloneDX",
            "version": "1.4",
            "confidence": "LOW",
            "confidence_explanation": sbom_commentary,
            "completeness_score": f"{random.randint(15, 35)}%",
            "completeness_note": f"We found {dep_count} components. We probably missed {dep_count * 3}.",
            "will_prevent_next_attack": False,
            "will_make_auditors_happy": True,
            "components": components
        }

    # Get paranoia state for response
    paranoia_state = paranoia_service.get_paranoia_state(session)
    paranoia_state["message"] = get_paranoia_message(session.level)
    paranoia_state["session_id"] = session.session_id

    return RoastResponse(
        meme_url=f"/memes/{meme_id}.png",
        meme_id=meme_id,
        roast_summary=f"You have {dep_count} dependencies. {sbom_commentary}",
        findings=findings,
        caption=caption,
        template_used="this-is-fine",
        sbom=sbom,
        paranoia=paranoia_state
    )
