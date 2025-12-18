# PURPOSE: FastAPI application entry point for PARANOID SBOM Roast Generator
# Provides /healthz and /roast endpoints with paranoia-aware responses

from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import BaseModel, field_validator
from typing import Literal, Optional
from pathlib import Path
import logging
import random
import uuid
import os
import time
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from services.analyzer import analyze
from services.caption_selector import (
    select_caption, get_sbom_commentary, get_paranoia_message,
    get_meltdown_caption, get_meltdown_refusal, get_panic_meltdown_secret
)
from services import paranoia as paranoia_service
from services.meme_generator import generate_meme, get_meme_path
from services.cve_detector import detect_cves_batch, detect_cves_batch_live, get_worst_severity, CVEMatch
from services.cursed_detector import detect_cursed_batch, get_worst_cursed, CursedMatch
from services.ai_roaster import generate_ai_roast, is_ai_available, AIRoastResult

# Configuration
MAX_INPUT_SIZE = int(os.environ.get("MAX_INPUT_SIZE", 102400))  # 100KB
MAX_DEPENDENCIES = int(os.environ.get("MAX_DEPENDENCIES", 500))
RATE_LIMIT_PER_MINUTE = int(os.environ.get("RATE_LIMIT_PER_MINUTE", 10))
MEME_TTL_SECONDS = int(os.environ.get("MEME_TTL_SECONDS", 3600))  # 1 hour

# Rate limiting state (in-memory, resets on restart)
rate_limit_store: dict[str, list[float]] = defaultdict(list)

# Path to frontend directory
FRONTEND_DIR = Path(__file__).parent.parent / "frontend"
MEMES_DIR = Path(__file__).parent / "static" / "memes"


class RoastRequest(BaseModel):
    input_type: Literal["package_json", "requirements_txt", "go_mod", "sbom", "single_package"]
    content: str
    include_sbom: bool = True
    use_ai: bool = False  # Enable AI-generated roasts (requires ANTHROPIC_API_KEY)
    ai_level: Literal["low", "medium", "high"] = "medium"  # low=Haiku, medium=Sonnet, high=Opus

    @field_validator('content')
    @classmethod
    def validate_content_size(cls, v):
        if len(v) > MAX_INPUT_SIZE:
            raise ValueError(f"Input too large. Maximum {MAX_INPUT_SIZE // 1024}KB. Your input weighs as much as your node_modules.")
        return v


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
    # v0.0.2 additions
    ai_generated: bool = False
    cve_count: int = 0
    cursed_count: int = 0

app = FastAPI(
    title="PARANOID",
    description="SBOM Roast Generator - Paste your dependencies. Get roasted. Question everything.",
    version="0.1.0",
    debug=False  # Never True in production
)


# H-1 Security Fix: Add security headers to all responses
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to prevent clickjacking, XSS, and MIME sniffing attacks."""
    
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        # Prevent MIME-type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        # XSS protection (legacy but still useful)
        response.headers["X-XSS-Protection"] = "1; mode=block"
        # Content Security Policy
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "img-src 'self' https://api.memegen.link data:; "
            "style-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com; "
            "script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com; "
            "font-src 'self' https://fonts.gstatic.com"
        )
        # Referrer policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        # Permissions policy (modern replacement for Feature-Policy)
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        return response


app.add_middleware(SecurityHeadersMiddleware)

# CORS configuration - tightened from wildcard
ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "http://localhost:8000,http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS if ALLOWED_ORIGINS != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "X-Session-Id"],
)


def check_rate_limit(client_ip: str) -> bool:
    """Check if client has exceeded rate limit. Returns True if allowed."""
    now = time.time()
    minute_ago = now - 60
    
    # Clean old entries
    rate_limit_store[client_ip] = [t for t in rate_limit_store[client_ip] if t > minute_ago]
    
    # Check limit
    if len(rate_limit_store[client_ip]) >= RATE_LIMIT_PER_MINUTE:
        return False
    
    # Record request
    rate_limit_store[client_ip].append(now)
    return True


def cleanup_old_memes():
    """Delete memes older than TTL."""
    if not MEMES_DIR.exists():
        return
    now = time.time()
    for meme_file in MEMES_DIR.glob("*.png"):
        if meme_file.stat().st_mtime < (now - MEME_TTL_SECONDS):
            try:
                meme_file.unlink()
            except Exception:
                pass  # Ignore cleanup errors

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
        "ai_available": is_ai_available(),  # For frontend to auto-enable AI toggle
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
    state["message"] = get_paranoia_message(session.level, session.request_count)
    state["session_id"] = session.session_id
    return state


@app.post("/reset")
async def reset_paranoia(x_session_id: Optional[str] = Header(None)):
    """Reset paranoia level to CHILL. For demo purposes."""
    session = paranoia_service.reset_session(x_session_id)
    return {
        "status": "reset",
        "message": "Deep breaths. Trust restored. For now.",
        "paranoia_level": session.level,
        "session_id": session.session_id
    }


@app.post("/panic")
async def panic(x_session_id: Optional[str] = Header(None)):
    """PANIC button endpoint - behavior changes based on paranoia level.
    
    - CHILL/ANXIOUS: Returns 451 with standard burn message
    - MELTDOWN: Returns classified secrets
    """
    session = paranoia_service.get_or_create_session(x_session_id)
    
    # In MELTDOWN mode, reveal classified secrets
    if session.level == paranoia_service.MELTDOWN:
        return JSONResponse(
            status_code=200,
            content={
                "status": "CLASSIFIED",
                "clearance": "MELTDOWN",
                "message": get_panic_meltdown_secret(),
                "paranoia_level": session.level,
                "warning": "This information will self-destruct. Not really. But you should still audit your deps."
            }
        )
    
    # Normal mode: Fahrenheit 451 easter egg
    # Escalate paranoia for pressing PANIC
    session.level = min(session.level + 1, paranoia_service.MELTDOWN)
    session.triggers.append("panic_button")
    
    raise HTTPException(
        status_code=451,
        detail="It was a pleasure to burn. This request has been incinerated at 451°F. Your paranoia has increased."
    )


@app.post("/roast", response_model=RoastResponse)
async def roast(request: RoastRequest, req: Request, x_session_id: Optional[str] = Header(None)):
    """Main roast endpoint - analyzes dependencies and generates meme."""
    
    # Rate limiting
    client_ip = req.client.host if req.client else "unknown"
    if not check_rate_limit(client_ip):
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Are you stress-testing me? I'm logging everything. EVERYTHING."
        )
    
    # Cleanup old memes periodically (1 in 10 chance per request)
    if random.random() < 0.1:
        cleanup_old_memes()

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

    # M-2 Security Fix: Enforce MAX_DEPENDENCIES limit
    if dep_count > MAX_DEPENDENCIES:
        logger.warning(f"Dependency limit exceeded: {dep_count} > {MAX_DEPENDENCIES}")
        raise HTTPException(
            status_code=400,
            detail=f"Too many dependencies ({dep_count}). Maximum {MAX_DEPENDENCIES} allowed. Your supply chain has serious trust issues."
        )

    # Apply paranoia triggers
    is_simple = request.input_type == "single_package"
    paranoia_service.apply_reducers(session, is_simple_lookup=is_simple)
    triggered = paranoia_service.apply_triggers(session, dep_count, content)

    # Check for MELTDOWN refusal - use unhinged error messages
    if paranoia_service.should_refuse_request(session):
        raise HTTPException(
            status_code=503,
            detail=get_meltdown_refusal()
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

    # CVE Detection - uses cached DB + live OSV.dev API
    # Map input type to OSV ecosystem
    ecosystem_map = {
        "package_json": "npm",
        "requirements_txt": "PyPI",
        "go_mod": "Go",
        "single_package": "npm",  # Default to npm for single packages
        "sbom": "npm",  # Default for SBOM
    }
    ecosystem = ecosystem_map.get(request.input_type, "npm")
    
    packages_to_check = [(d.name, d.version) for d in result.dependencies]
    cve_matches = await detect_cves_batch_live(packages_to_check, ecosystem=ecosystem, max_osv_queries=25)
    cve_count = len(cve_matches)
    worst_cve_severity = get_worst_severity(cve_matches)

    # Cursed Package Detection
    package_names = [d.name for d in result.dependencies]
    cursed_matches = detect_cursed_batch(package_names)
    cursed_count = len(cursed_matches)
    worst_cursed = get_worst_cursed(cursed_matches)

    # Generate response
    meme_id = str(uuid.uuid4())[:8]
    ai_generated = False
    template_used = "leonardo"
    
    # Try AI generation if requested and available
    if request.use_ai and is_ai_available():
        # Prepare data for AI - pass ALL findings for full context
        cve_data = [
            {"package": c.package, "version": c.version, "cve_id": c.cve_id,
             "severity": c.severity, "description": c.description}
            for c in cve_matches  # All CVEs, not just 5
        ]
        cursed_data = [
            {"package": c.package, "description": c.description}
            for c in cursed_matches
        ]
        
        ai_result = await generate_ai_roast(
            dep_count=dep_count,
            package_names=package_names,
            cve_list=cve_data,
            cursed_list=cursed_data,
            level=request.ai_level
        )
        
        if ai_result:
            caption = ai_result.roast
            template_used = ai_result.template
            ai_generated = True
    
    # Fallback to pre-written captions if AI not used or failed
    if not ai_generated:
        # MELTDOWN MODE: Use unhinged captions
        if session.level == paranoia_service.MELTDOWN:
            caption = get_meltdown_caption()
        elif worst_cursed:
            caption = worst_cursed.roast
        elif cve_count > 0:
            caption = select_caption("cve", severity=worst_cve_severity)
        else:
            caption = select_caption("dependency_count", dep_count=dep_count)

    # Generate the meme image
    generate_meme(meme_id, caption, template=template_used)

    # Build findings based on actual analysis
    dep_severity = "high" if dep_count > 50 else "medium" if dep_count > 10 else "low"
    findings = [
        Finding(
            type="dependency_count",
            severity=dep_severity,
            detail=f"{dep_count} dependencies detected"
        )
    ]

    # Add CVE findings
    for cve in cve_matches[:5]:  # Limit to top 5
        findings.append(Finding(
            type="cve",
            severity=cve.severity,
            detail=f"{cve.package}@{cve.version}: {cve.cve_id} - {cve.description}"
        ))
    if cve_count > 5:
        findings.append(Finding(
            type="cve",
            severity="info",
            detail=f"...and {cve_count - 5} more CVEs"
        ))

    # Add cursed package findings
    for cursed in cursed_matches:
        findings.append(Finding(
            type="cursed" if not cursed.is_typosquat else "typosquat",
            severity=cursed.severity,
            detail=cursed.roast
        ))

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
    paranoia_state["message"] = get_paranoia_message(session.level, session.request_count)
    paranoia_state["session_id"] = session.session_id

    # Build roast summary
    summary_parts = [f"You have {dep_count} dependencies."]
    if cve_count > 0:
        summary_parts.append(f"{cve_count} CVE{'s' if cve_count > 1 else ''} detected.")
    if cursed_count > 0:
        summary_parts.append(f"{cursed_count} cursed package{'s' if cursed_count > 1 else ''} found.")
    summary_parts.append(sbom_commentary)
    roast_summary = " ".join(summary_parts)

    return RoastResponse(
        meme_url=f"/memes/{meme_id}.png",
        meme_id=meme_id,
        roast_summary=roast_summary,
        findings=findings,
        caption=caption,
        template_used=template_used,
        sbom=sbom,
        paranoia=paranoia_state,
        ai_generated=ai_generated,
        cve_count=cve_count,
        cursed_count=cursed_count
    )
