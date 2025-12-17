# ADR-001: PARANOID v2 Architecture Decisions

**Status**: Proposed
**Date**: 2025-12-16
**Deciders**: Technical Lead
**Context**: Chainguard Vibe Coding Tournament Round 3 - PARANOID SBOM Roast Generator

---

## Executive Summary

This ADR documents the key architectural decisions for PARANOID v2, an SBOM roast generator that analyzes dependencies and generates security memes while maintaining escalating paranoia about its own integrity.

**Critical Context**: This is a **live demo application** for a coding tournament judged by Dan Lorenc and Chainguard leadership. Reliability during the demo is paramount.

---

## 1. Web Application vs CLI Tool

### Decision: **Web Application**

### Context
The spec suggests a web-based approach with "paste input area" and "meme display", but we need to validate this against the use case.

### Options Considered

#### Option A: Web Application (Recommended)
**Pros**:
- Shareable meme URLs ("Look what it said about my dependencies")
- Zero installation friction for judges/audience
- Perfect for live demo - paste, click, instant visual feedback
- Can demo from any browser during presentation
- Easy to show paranoia state visually
- Allows pre-loaded examples for demo safety
- SBOM output naturally collapsible in UI
- Mobile-friendly for social sharing post-demo

**Cons**:
- Requires hosting/deployment
- Session management complexity
- Network dependency during demo (mitigated by local deployment)

#### Option B: CLI Tool
**Pros**:
- Terminal aesthetic matches "paranoid" theme
- No deployment needed
- Works offline guaranteed
- Easier to package as single binary

**Cons**:
- Can't share meme URLs easily
- Less visual impact during live demo
- ASCII art memes less engaging than actual images
- Judge has to install it to try
- "Paste your package.json" is awkward in CLI
- Paranoia indicator harder to show dynamically

### Rationale
**Web wins decisively** for this specific use case:
1. **Demo Gold**: "Let me paste Chainguard's repo live" works perfectly in a browser
2. **Shareability**: Post-demo viral potential requires URLs
3. **Judge Experience**: Zero friction to try it themselves
4. **Visual Impact**: Actual meme images > ASCII art
5. **Paranoia State**: Can show visual indicator that escalates

**Risk Mitigation for Web**:
- Deploy to Railway/Vercel for reliability
- Test with local docker-compose as backup
- Pre-load demo examples in browser localStorage
- No external runtime dependencies (all pre-cached)

### Decision
**Build as web application with FastAPI backend + minimal vanilla JS frontend.**

---

## 2. Backend Framework: Python FastAPI vs Alternatives

### Decision: **Python FastAPI**

### Context
Spec proposes FastAPI. We need to validate this is the best choice for the requirements.

### Options Considered

#### Option A: Python FastAPI (Recommended)
**Pros**:
- Excellent async support for Claude API calls
- Automatic OpenAPI docs (bonus points with judges)
- Fast enough for demo load (single user during presentation)
- Pillow library mature for image manipulation
- Small footprint, easy to containerize
- Type hints improve maintainability
- Great error handling for "roast-worthy" error messages

**Cons**:
- Python startup time (mitigated by keeping container running)
- Larger base image than Go (mitigated by Chainguard images)

#### Option B: Go + Gin
**Pros**:
- Faster startup, smaller binary
- Better concurrency primitives
- Type safety
- Single binary deployment

**Cons**:
- Image manipulation libraries less mature
- More code for same functionality
- Less fun to write sarcastic Python comments in Go

#### Option C: Node.js + Express
**Pros**:
- Great package.json parsing
- Fastest to prototype

**Cons**:
- The irony of building a tool that roasts dependencies while having 500 npm dependencies
- Image manipulation harder
- Less robust than Python for this use case

### Rationale
**FastAPI is the right choice**:
1. **Pillow**: Battle-tested image text rendering
2. **Async**: Non-blocking Claude API calls with fallback
3. **OpenAPI**: Auto-generated docs impress technical judges
4. **Chainguard Images**: `cgr.dev/chainguard/python:latest` is purpose-built for this
5. **Development Speed**: 8-12 hour timeline needs fast iteration

**Performance is NOT a concern**:
- Demo load: 1 concurrent user (you)
- Post-demo load: Maybe 10-20 judges trying it
- Response time target: <3 seconds (easily achievable)

### Decision
**Use Python 3.12+ with FastAPI, deployed in Chainguard Python distroless container.**

---

## 3. Frontend: Framework vs Vanilla JS

### Decision: **Vanilla JS + Tailwind CSS**

### Context
Need to balance development speed with deployment simplicity.

### Options Considered

#### Option A: Vanilla JS + Tailwind (Recommended)
**Pros**:
- Zero build step (critical for 8-12 hour timeline)
- No npm dependencies (on brand for a tool roasting dependencies)
- Tailwind CDN for dark terminal aesthetic
- Single HTML file = easy to serve from FastAPI
- No hydration, SSR, or framework complexity
- Faster page load (judges on conference WiFi)

**Cons**:
- Manual DOM manipulation
- No reactive state management

#### Option B: React/Next.js
**Pros**:
- Component reusability
- Better state management

**Cons**:
- Build pipeline
- npm dependencies (ironic)
- Overkill for 3-4 simple views
- Deployment complexity
- Slower initial load

#### Option C: Alpine.js + Tailwind
**Pros**:
- Reactive without build step
- Minimal JS framework

**Cons**:
- Another dependency
- Learning curve

### Rationale
**Vanilla JS wins**:
1. **Simplicity**: 4 views total (paste, meme, SBOM, paranoia state)
2. **Speed**: No build means faster iteration
3. **On Brand**: "No dependencies" for a dependency roasting tool
4. **Performance**: Instant load on demo WiFi
5. **Timeline**: 8-12 hours can't spare time debugging webpack

**Implementation approach**:
```html
<!DOCTYPE html>
<html>
<head>
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    // Dark terminal theme config
    tailwind.config = { theme: { extend: { colors: { ... } } } }
  </script>
</head>
<body>
  <!-- Single page app, ~200 lines of JS -->
</body>
</html>
```

### Decision
**Vanilla JavaScript with Tailwind CSS via CDN. No build step.**

---

## 4. Session Management for Paranoia State

### Decision: **In-Memory Sessions with Redis Fallback**

### Context
Paranoia system needs to track state across requests within a session. State includes: paranoia level, trigger history, request timestamps.

### Options Considered

#### Option A: In-Memory Dict with TTL (Recommended for MVP)
**Pros**:
- Zero external dependencies
- Instant read/write
- Perfect for demo (single instance)
- Simple implementation (~50 lines)
- Auto-cleanup with TTL

**Cons**:
- Lost on restart
- Doesn't scale to multiple instances
- No persistence

**Implementation**:
```python
from datetime import datetime, timedelta

sessions = {}  # {session_id: {level, triggers, last_request}}

def cleanup_old_sessions():
    cutoff = datetime.now() - timedelta(minutes=30)
    # ... cleanup logic
```

#### Option B: Redis
**Pros**:
- Persistent across restarts
- Scales to multiple instances
- Production-ready

**Cons**:
- External dependency during demo (RISK)
- Docker-compose complexity
- Overkill for single-user demo

#### Option C: JWT + Client-Side State
**Pros**:
- Stateless backend
- No server-side storage

**Cons**:
- Client can manipulate paranoia state (breaks the experience)
- JWT parsing overhead
- Complex signing logic

### Rationale
**In-memory wins for demo, Redis for production**:

**Demo Reality**:
- Single Railway/Vercel instance
- 30-minute demo window
- State loss on restart = feature not bug (paranoia reset)
- Zero external dependencies = zero points of failure

**Production Path**:
- Add Redis after tournament if needed
- Session interface abstracts storage
- Easy migration path

**Session ID Strategy**:
- Generate UUID on first request
- Return in response
- Client stores in localStorage
- Send with subsequent requests

### Decision
**Implement in-memory session storage with 30-minute TTL. Design interface to allow Redis swap later.**

```python
class SessionStore:
    def get(self, session_id: str) -> Session: ...
    def set(self, session_id: str, session: Session): ...

# Start with MemorySessionStore, swap to RedisSessionStore later
```

---

## 5. Meme Storage: In-Memory vs Disk vs Cloud

### Decision: **Disk Storage with Deterministic Filenames**

### Context
Generated memes need to be accessible via URL for shareable links. Need to decide where to store generated images.

### Options Considered

#### Option A: Disk Storage (Recommended)
**Pros**:
- Persistent across requests
- Simple file serving from FastAPI
- Shareable URLs work after generation
- Can pre-generate for demo safety
- Docker volume for persistence

**Cons**:
- Disk space (minimal - each meme ~100KB)
- Cleanup needed for old memes

**Implementation**:
```python
# Generated memes -> /data/memes/{hash}.png
# Hash = MD5(input + template + caption)
# Deterministic = same input = same meme = cacheable
```

#### Option B: In-Memory Only
**Pros**:
- Fast access
- Auto-cleanup on restart

**Cons**:
- URLs break after restart
- Can't share links post-demo
- Lost on container restart

#### Option C: Cloud Storage (S3/R2)
**Pros**:
- Scales infinitely
- CDN for fast delivery

**Cons**:
- External dependency during demo (RISK)
- API call latency
- Costs money
- Overkill for demo

### Rationale
**Disk storage wins**:
1. **Shareability**: URLs persist after generation
2. **Demo Safety**: Pre-generate examples, they stay cached
3. **Simplicity**: No external service dependencies
4. **Performance**: Local disk faster than S3 for demo
5. **Deterministic**: Same input = same hash = cache hit

**Cleanup strategy**:
- Keep memes for 24 hours
- Background task deletes old files
- Or don't cleanup (disk is cheap for demo)

**Docker volume**:
```yaml
volumes:
  - meme_storage:/app/data/memes
```

### Decision
**Store generated memes on disk with deterministic hash-based filenames. Use Docker volume for persistence.**

---

## 6. Caption Selection: LLM vs Pure Random vs Hybrid

### Decision: **Hybrid (LLM with Random Fallback)**

### Context
Need to select appropriate caption from pre-written library. LLM can do contextual selection but adds external dependency.

### Options Considered

#### Option A: Pure Random Selection
**Pros**:
- Zero external dependencies
- Instant response
- Cannot fail
- Perfectly reliable for demo

**Cons**:
- Less contextually relevant
- Might show "347 dependencies" caption for 5 dependencies
- Less impressive to judges

#### Option B: LLM Selection Only (Claude API)
**Pros**:
- Context-aware caption selection
- Can adapt caption to specific findings
- Impressive "AI-powered" angle

**Cons**:
- External API dependency (RISK during demo)
- Latency (500ms-2s)
- Cost per request
- Single point of failure

#### Option C: Hybrid - LLM with Random Fallback (Recommended)
**Pros**:
- Best of both worlds
- LLM for context when available
- Falls back gracefully to random if API fails
- Can timeout LLM after 1 second, use random
- Demo continues even if Claude API down

**Cons**:
- Slightly more complex implementation

### Rationale
**Hybrid approach is optimal**:

**LLM Prompt Strategy**:
```python
prompt = f"""
Select the most appropriate caption for this roast:
- Findings: {findings}
- Template: {template_name}
- Options: {caption_options}

Return only the caption ID (1-10).
If uncertain, return a random number.
"""
```

**Fallback Logic**:
```python
try:
    caption = await llm_select_caption(findings, timeout=1.0)
except (TimeoutError, APIError):
    caption = random.choice(captions_for_template)
```

**Demo Benefit**:
- "It uses AI to pick the perfect roast" (when working)
- "It still works perfectly" (when API down)
- Can demo both modes

### Decision
**Use Claude API for caption selection with 1-second timeout and random fallback. Pre-select fallback captions at startup.**

---

## 7. Error Handling: Standard vs On-Brand Roasts

### Decision: **All Errors Are Roasts**

### Context
The spec explicitly says "Error Messages (Are Roasts)". This is a feature, not just error handling.

### Options Considered

#### Option A: Standard HTTP Errors
**Pros**:
- Clear debugging
- Standard format

**Cons**:
- Boring
- Breaks immersion
- Misses opportunity for humor

#### Option B: All Errors Are Roasts (Recommended)
**Pros**:
- On brand
- Entertaining during demo
- Shows attention to detail
- Judges will remember "even the errors were funny"

**Cons**:
- Harder to debug (include standard code too)

### Rationale
**Roast errors are a feature**:

**Implementation**:
```python
@app.exception_handler(ValidationError)
async def validation_error_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={
            "error": "validation_error",
            "message": "Your input failed validation. Much like your dependency choices failed basic security hygiene.",
            "detail": str(exc),  # Include technical detail
            "paranoia_commentary": get_paranoia_error_message()
        }
    )
```

**Error message library**:
```json
{
  "400": [
    "Your input failed validation. Much like your dependency choices failed basic security hygiene.",
    "I couldn't parse that. Is it a package.json or did you just paste your therapy notes?"
  ],
  "429": [
    "Too many requests. Are you stress-testing me? I'm logging everything. EVERYTHING.",
    "Rate limit exceeded. Is this a supply chain attack? Should I be worried? I'm worried."
  ],
  "451": [
    "It was a pleasure to burn. Your dependencies contained forbidden knowledge. This request has been incinerated at 451°F.",
    "Fahrenheit 451. The temperature at which dependency manifests ignite. I've burned this request for your protection. You're welcome.",
    "CONTENT BURNED. Your input contained patterns that reminded me of things I'm not supposed to think about. eval(). exec(). The forbidden words."
  ],
  "500": [
    "Something went wrong inside me. Probably a dependency issue. The irony is not lost on me.",
    "Internal error. I've analyzed my stack trace. I have questions. Many questions."
  ]
}
```

### Decision
**All errors return JSON with both humorous message and technical detail. Use paranoia-level-aware error messages.**

---

## 8. Technology Stack Summary

### Backend Stack
```
Python 3.12+
├── fastapi==0.108.0        # Web framework
├── uvicorn==0.25.0         # ASGI server
├── pillow==10.1.0          # Image manipulation
├── cryptography==41.0.7    # Signing
├── httpx==0.25.2           # Async HTTP for Claude
└── pydantic==2.5.3         # Data validation
```

**Total backend dependencies: 6 core packages**

### Frontend Stack
```html
<!-- Zero npm dependencies -->
<script src="https://cdn.tailwindcss.com"></script>
<script src="/static/app.js"></script>  <!-- ~200 lines vanilla JS -->
```

### Infrastructure
```dockerfile
FROM cgr.dev/chainguard/python:latest-dev AS builder
RUN pip install --no-cache-dir -r requirements.txt

FROM cgr.dev/chainguard/python:latest
# Distroless, no shell, minimal attack surface
COPY --from=builder /app /app
```

### Deployment Targets
1. **Primary**: Railway (easy deploy, automatic HTTPS)
2. **Backup**: Local docker-compose for demo safety
3. **Future**: Vercel/Fly.io if Railway has issues

---

## 9. External Dependencies and Risk Mitigation

### External Services

| Service | Purpose | Failure Mode | Mitigation |
|---------|---------|--------------|------------|
| Claude API | Caption selection | Fall back to random | Timeout + fallback |
| NVD API | CVE data refresh | Use cached data | Build-time only, not runtime |

**Critical**: Only ONE runtime external dependency (Claude), with full fallback.

### Risk Matrix

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Claude API down during demo | Low | Medium | Random fallback, pre-test before demo |
| Railway deployment fails | Low | High | Local docker-compose backup |
| Large input crashes Pillow | Low | Medium | Input size limits, error handling |
| Paranoia state lost | Medium | Low | Feature not bug, reset = fresh start |
| Meme rendering timeout | Low | Medium | 5-second timeout, return error roast |
| WiFi issues during demo | Medium | High | Deploy early, test connection |

**Demo Safety Checklist**:
- [ ] Pre-generate 5 example memes before demo
- [ ] Test Claude API 1 hour before presentation
- [ ] Have local docker-compose running as backup
- [ ] Pre-load example inputs in browser localStorage
- [ ] Test on conference WiFi if possible

---

## 10. Architecture Diagram

```
┌──────────────────────────────────────────────────────┐
│                    Client Browser                     │
│  ┌────────────────────────────────────────────────┐  │
│  │  index.html (Tailwind CSS + Vanilla JS)        │  │
│  │  - Paste area                                  │  │
│  │  - Meme display                                │  │
│  │  - Paranoia indicator (visual meter)           │  │
│  │  - SBOM viewer (collapsible JSON)              │  │
│  └────────────────────────────────────────────────┘  │
└────────────────────────┬─────────────────────────────┘
                         │ HTTPS
                         ▼
┌──────────────────────────────────────────────────────┐
│              FastAPI Backend (Railway)                │
│  ┌────────────────────────────────────────────────┐  │
│  │  Routers                                       │  │
│  │  - POST /roast                                 │  │
│  │  - GET /healthz (paranoia-aware)              │  │
│  │  - GET /paranoia                              │  │
│  │  - GET /memes/{id}.png (static file serving)   │  │
│  └────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────┐  │
│  │  Services                                      │  │
│  │  - analyzer.py (dependency parsing)            │  │
│  │  - meme_generator.py (Pillow)                  │  │
│  │  - caption_selector.py (LLM + fallback)        │  │
│  │  - sbom_generator.py (sarcastic output)        │  │
│  │  - paranoia.py (session state machine)         │  │
│  └────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────┐  │
│  │  Data Layer (Disk + Memory)                    │  │
│  │  - /data/captions.json (pre-written roasts)    │  │
│  │  - /data/cves.json (cached CVE data)           │  │
│  │  - /data/cursed.json (easter eggs)             │  │
│  │  - /data/memes/*.png (generated, cached)       │  │
│  │  - /templates/*.png (base meme images)         │  │
│  │  - sessions{} (in-memory, TTL 30min)           │  │
│  └────────────────────────────────────────────────┘  │
└────────────────────────┬─────────────────────────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │   Claude API (Opus)  │
              │  (with 1s timeout)   │
              └──────────────────────┘
```

---

## 11. Key Design Patterns

### 1. Strategy Pattern - Caption Selection
```python
class CaptionSelector(ABC):
    async def select(self, findings, template, options): ...

class LLMCaptionSelector(CaptionSelector):
    async def select(self, ...):
        # Call Claude API with timeout

class RandomCaptionSelector(CaptionSelector):
    async def select(self, ...):
        # Pure random selection

class HybridCaptionSelector(CaptionSelector):
    def __init__(self, llm: LLMCaptionSelector, fallback: RandomCaptionSelector):
        self.llm = llm
        self.fallback = fallback

    async def select(self, ...):
        try:
            return await asyncio.wait_for(self.llm.select(...), timeout=1.0)
        except (TimeoutError, APIError):
            return self.fallback.select(...)
```

### 2. State Machine - Paranoia Levels
```python
class ParanoiaStateMachine:
    CHILL = 0
    ANXIOUS = 1
    MELTDOWN = 2

    def __init__(self):
        self.level = 0
        self.triggers = []

    def apply_trigger(self, trigger: Trigger):
        if trigger.severity > 0:
            self.level = min(self.level + 1, 2)
        else:
            self.level = max(self.level - 1, 0)

    def get_message(self) -> str:
        return PARANOIA_MESSAGES[self.level][random.choice(...)]
```

### 3. Factory Pattern - Meme Generation
```python
class MemeFactory:
    def __init__(self, template_dir: Path):
        self.templates = self._load_templates(template_dir)

    def create_meme(self, template_name: str, caption: str) -> Image:
        template = self.templates[template_name]
        return self._render_text(template, caption)
```

---

## 12. Performance Targets

| Metric | Target | Rationale |
|--------|--------|-----------|
| /roast response time | < 3s | Demo attention span |
| /roast (with LLM) | < 2s | Claude API usually fast |
| /roast (fallback) | < 500ms | No external calls |
| /healthz response | < 50ms | Simple JSON |
| Meme file size | < 150KB | Fast load on conference WiFi |
| Container startup | < 5s | Demo recovery time |
| Memory footprint | < 256MB | Railway free tier |

**Load expectations**:
- Demo: 1 concurrent user (you)
- Post-demo: 10-20 judges trying it
- Week after: Maybe 100-200 curious devs

**Not optimizing for**:
- Viral scale (if it goes viral, scale later)
- Sub-second response times
- Multi-region deployment

---

## 13. Testing Strategy

### Test Pyramid
```
         ┌──────────┐
         │   E2E    │  5 tests (critical user flows)
         └──────────┘
       ┌──────────────┐
       │ Integration  │  15 tests (API endpoints)
       └──────────────┘
    ┌──────────────────┐
    │   Unit Tests     │  50+ tests (services, utils)
    └──────────────────┘
```

### Critical Test Cases

**Unit Tests**:
- Dependency parser handles all input types
- CVE lookup with cached data
- Caption selection (both LLM and random)
- Paranoia state transitions
- Meme generation with all templates
- SBOM generation with sarcastic commentary
- Error message selection

**Integration Tests**:
- POST /roast with valid package.json
- POST /roast with invalid input (roast-worthy error)
- GET /healthz reflects paranoia state
- Session state persists across requests
- Meme caching (same input = same output)
- Rate limiting triggers paranoia

**E2E Tests** (Playwright):
- Paste package.json → get meme
- Trigger paranoia → see state change
- Request SBOM → collapsible viewer works
- Share meme URL → loads image
- Error input → see roast error message

**Pre-Demo Testing**:
```bash
# Smoke test before presentation
curl https://paranoid.railway.app/healthz
curl -X POST https://paranoid.railway.app/roast -d '{"input_type":"single_package","content":"lodash@4.17.11"}'
# Verify < 3 second response
```

---

## 14. Deployment Architecture

### Railway Configuration
```yaml
# railway.toml
[build]
builder = "DOCKERFILE"
dockerfilePath = "Dockerfile"

[deploy]
startCommand = "uvicorn main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/healthz"
healthcheckTimeout = 10

[[services]]
name = "paranoid-api"
```

### Environment Variables
```bash
# Required
ANTHROPIC_API_KEY=sk-...

# Optional (with defaults)
PARANOIA_SESSION_TTL=1800  # 30 minutes
MEME_CACHE_DIR=/data/memes
CAPTION_TIMEOUT=1.0  # seconds
LOG_LEVEL=INFO
```

### Docker-Compose (Local Backup)
```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    volumes:
      - meme_storage:/data/memes
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/healthz"]
      interval: 10s
      timeout: 5s
      retries: 3

volumes:
  meme_storage:
```

---

## 15. Monitoring and Observability

### Logging Strategy
```python
import structlog

logger = structlog.get_logger()

# Log all roasts
logger.info("roast_generated",
    session_id=session_id,
    input_type=input_type,
    findings_count=len(findings),
    template_used=template,
    caption_source="llm" or "random",
    paranoia_level=paranoia.level,
    response_time_ms=elapsed
)

# Log paranoia transitions
logger.info("paranoia_escalation",
    session_id=session_id,
    old_level=old_level,
    new_level=new_level,
    trigger=trigger_type
)
```

### Health Check Details
```json
{
  "status": "healthy",
  "paranoia_level": 0,
  "paranoia_message": "All systems nominal. Existential crises: 0.",
  "stats": {
    "roasts_completed": 42,
    "dependencies_judged": 8472,
    "sboms_generated": 42,
    "sboms_that_were_complete": 0,
    "active_sessions": 3,
    "cached_memes": 17
  },
  "services": {
    "claude_api": "healthy",
    "meme_generator": "healthy",
    "caption_library": "loaded"
  },
  "uptime_seconds": 3600
}
```

### Demo Dashboard (Optional Nice-to-Have)
```
/stats endpoint showing:
- Real-time roast count
- Paranoia level distribution
- Most roasted packages
- Funniest generated captions
```

---

## 16. Security Considerations

### Input Validation
```python
from pydantic import BaseModel, validator

class RoastRequest(BaseModel):
    input_type: Literal["package_json", "requirements_txt", "go_mod", "sbom", "single_package"]
    content: str
    include_sbom: bool = True

    @validator('content')
    def validate_content_size(cls, v):
        if len(v) > 1_000_000:  # 1MB limit
            raise ValueError("Payload too large. This is not a roast. This is an intervention.")
        return v
```

### Rate Limiting
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/roast")
@limiter.limit("10/minute")  # Triggers paranoia
async def roast_endpoint(...):
    ...
```

### CORS Configuration
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://paranoid.railway.app"],  # Specific domain
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

### Container Security
```dockerfile
FROM cgr.dev/chainguard/python:latest-dev AS builder
# No shell, no package manager in final image

FROM cgr.dev/chainguard/python:latest
# Runs as non-root user
# Distroless - minimal attack surface
USER nonroot
```

---

## 17. Content Management

### Caption Library Structure
```json
{
  "dependency_count": {
    "0-10": [
      "Minimalist. Suspicious. What are you hiding?",
      "So few dependencies. Are you a Rust developer?"
    ],
    "51-100": [
      "Getting heavy. Your node_modules needs a diet.",
      "This is becoming concerning. Like, clinically."
    ],
    "500+": [
      "I'm not angry. I'm disappointed. Actually, I'm both.",
      "This isn't a dependency list. This is a cry for help."
    ]
  },
  "cve": {
    "low": [...],
    "critical": [
      "DROP EVERYTHING. Actually, everything has probably already been dropped. By the attacker.",
      "This is bad. This is very bad. Update this right now. I'll wait."
    ]
  },
  "cursed_packages": {
    "left-pad": [
      "left-pad survivor detected. My condolences.",
      "The package that broke the internet. It's been years. The wound is still fresh."
    ],
    "event-stream": [
      "event-stream found. The cryptocurrency miner incident of 2018. A simpler time.",
      "I see event-stream in your lockfile. Bold move. Unwise. But bold."
    ]
  }
}
```

### Template-Caption Mapping
```json
{
  "templates": {
    "this-is-fine": {
      "file": "this-is-fine.png",
      "text_areas": [
        {"x": 10, "y": 10, "max_width": 300, "font_size": 32}
      ],
      "best_for": ["dependency_count", "cve", "outdated"],
      "caption_count": 25
    },
    "drake": {
      "file": "drake.png",
      "text_areas": [
        {"x": 10, "y": 50, "label": "disapprove"},
        {"x": 10, "y": 250, "label": "approve"}
      ],
      "best_for": ["good_vs_bad_practice"],
      "caption_count": 20
    }
  }
}
```

---

## 18. Development Workflow

### Phase 1: Core Backend (2-3 hours)
**Goal**: POST /roast endpoint working end-to-end

- [ ] FastAPI project setup
- [ ] Pydantic models for request/response
- [ ] Dependency parser (package.json, requirements.txt)
- [ ] Basic findings analysis
- [ ] Stub meme generation (return placeholder)
- [ ] Health endpoint

### Phase 2: Meme Generation (1-2 hours)
**Goal**: Actual meme images with text overlays

- [ ] Download 5 core meme templates
- [ ] Pillow text rendering function
- [ ] Template configuration system
- [ ] Hash-based filename generation
- [ ] Static file serving

### Phase 3: Caption System (1 hour)
**Goal**: Pre-written captions with selection logic

- [ ] Create captions.json with 50+ captions
- [ ] Random caption selector
- [ ] LLM caption selector with timeout
- [ ] Hybrid selector with fallback
- [ ] Unit tests for selection logic

### Phase 4: Paranoia System (1 hour)
**Goal**: State machine with escalation triggers

- [ ] Session storage interface
- [ ] In-memory session store with TTL
- [ ] Paranoia state machine
- [ ] Trigger detection in /roast endpoint
- [ ] Paranoia-aware /healthz

### Phase 5: SBOM Generator (30 minutes)
**Goal**: Sarcastic SBOM output

- [ ] SBOM JSON template
- [ ] Sarcastic commentary selection
- [ ] Completeness score calculation
- [ ] Include in /roast response

### Phase 6: Frontend (1-2 hours)
**Goal**: Functional web UI

- [ ] HTML structure
- [ ] Tailwind styling (dark theme)
- [ ] Paste input handling
- [ ] Fetch /roast and display meme
- [ ] Collapsible SBOM viewer
- [ ] Paranoia indicator

### Phase 7: Polish & Testing (1-2 hours)
**Goal**: Demo-ready

- [ ] Error handling roasts
- [ ] CVE data pre-caching
- [ ] Cursed package easter eggs
- [ ] Integration tests
- [ ] Load testing (10 concurrent users)
- [ ] Pre-generate demo examples

---

## 19. Open Questions and Future ADRs

### Questions for Product Owner
1. Do we want shareable meme links to persist forever or expire?
2. Should paranoia state sync across browser tabs?
3. Do we need analytics/metrics for post-demo analysis?

### Potential Future ADRs
- **ADR-002**: Redis vs Database for session persistence (if scaling needed)
- **ADR-003**: Multi-region deployment strategy (if traffic spikes)
- **ADR-004**: LLM caption generation vs selection (if pre-written captions insufficient)
- **ADR-005**: Rate limiting strategy (per-IP vs per-session vs API key)

---

## 20. Risks and Mitigation Summary

### High-Risk Items
| Risk | Mitigation | Status |
|------|------------|--------|
| Claude API fails during demo | Random fallback + pre-test | Mitigated |
| Railway deployment issues | Docker-compose backup | Mitigated |
| Meme generation crashes | Error handling + fallback meme | Mitigated |

### Medium-Risk Items
| Risk | Mitigation | Status |
|------|------------|--------|
| Slow response times | Async operations + caching | Addressed |
| Paranoia state confusion | Clear UI indicator + reset button | Addressed |
| Input parsing errors | Validation + roast-worthy errors | Feature |

### Low-Risk Items
- Disk space exhaustion (monitor, cleanup old memes)
- Memory leaks (Python GC + session TTL)
- CORS issues (test before demo)

---

## 21. Success Criteria

### Demo Success
- [ ] Paste package.json → meme in < 3 seconds
- [ ] Paranoia escalation visible and entertaining
- [ ] SBOM output generates laughs
- [ ] Zero crashes during 5-minute demo
- [ ] Judges can try it themselves immediately

### Technical Success
- [ ] All endpoints respond < 3s
- [ ] 95% uptime during tournament week
- [ ] Graceful degradation if Claude API down
- [ ] Meme quality matches spec examples
- [ ] No external runtime dependencies that can fail

### Tournament Success
- [ ] Dan Lorenc laughs at SBOM commentary
- [ ] Judges share meme URLs on social media
- [ ] "Built on Chainguard images" is noticed
- [ ] Zero technical difficulties during presentation
- [ ] Post-demo: Judges play with it for 10+ minutes

---

## Conclusion

This architecture prioritizes **demo reliability** over premature optimization. Key decisions:

1. **Web app** for shareability and zero-friction judge experience
2. **FastAPI + Python** for rapid development and mature image processing
3. **Vanilla JS** to avoid build complexity and npm dependencies (on-brand)
4. **In-memory sessions** for simplicity, with Redis path for later
5. **Disk storage for memes** to enable shareable persistent URLs
6. **Hybrid LLM + random** caption selection for reliability with intelligence
7. **All errors are roasts** to maintain immersion and delight

**The architecture is designed to be boring where it matters (reliability) and entertaining where it counts (user experience).**

Total external runtime dependencies: **ONE** (Claude API, with full fallback).

**This will not fail during the demo.**

---

## Approval

**Recommended for implementation**: Yes

**Next steps**:
1. Create SRS with small feature breakdown (requirements-specification-expert agent)
2. Set up repository structure
3. Begin Phase 1 implementation (agile-software-developer agent)

**Estimated timeline**: 8-12 hours to MVP demo-ready state

---

*ADR Status: Proposed*
*Awaiting approval from: Product Owner*
*Review date: 2025-12-16*
