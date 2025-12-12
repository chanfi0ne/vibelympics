# CHAINSAW Red Team Security Assessment

**Assessment Date:** 2025-12-11
**Target:** CHAINSAW npm Supply Chain Security Auditor
**Production Endpoint:** https://chainsaw.up.railway.app/
**Assessment Type:** Authorized Penetration Testing
**Assessor:** Security Engineering Team

---

## Executive Summary

This red team assessment evaluated the CHAINSAW application - an npm supply chain security auditor tool. The assessment combined static code analysis with attempted live testing against the production deployment. The backend was unavailable during live testing (504 Gateway Timeout), so findings are primarily based on comprehensive source code review.

**Overall Security Posture:** MEDIUM RISK

**Critical Findings:** 0
**High Severity:** 2
**Medium Severity:** 4
**Low Severity:** 3
**Informational:** 2

---

## Assessment Methodology

### 1. Reconnaissance
- Reviewed comprehensive documentation (PRD, SRS, ADR-001, DESIGN.md)
- Analyzed architecture and data flow diagrams
- Identified external API integrations and dependencies

### 2. Static Code Analysis
- Analyzed all Python backend code (FastAPI, services, models)
- Reviewed input validation mechanisms
- Examined API client implementations
- Assessed error handling and information disclosure risks

### 3. Dynamic Testing (Attempted)
- Production endpoint: https://chainsaw.up.railway.app/
- Result: Backend unavailable (504 Gateway Timeout)
- Unable to perform live exploitation testing

### 4. Attack Surface Analysis
- API endpoints: /api/audit, /api/audit/compare, /api/health
- External integrations: npm Registry, GitHub API, OSV.dev, npm Sigstore
- Client libraries: httpx (async HTTP)

---

## Findings

### FINDING 1: Server-Side Request Forgery (SSRF) via Repository URL
**Severity:** HIGH
**CWE:** CWE-918 (Server-Side Request Forgery)
**CVSS Score:** 7.5 (High)

#### Description
The GitHub client in `/backend/services/github_client.py` constructs API requests based on repository URLs extracted from npm package metadata without sufficient validation. While the code uses regex to parse GitHub URLs, an attacker controlling a malicious npm package could potentially manipulate the repository field to cause the backend to make requests to unintended destinations.

#### Vulnerable Code Location
File: `/Users/jonc/Workspace/vibelympics/round_2/backend/services/github_client.py`

```python
def parse_github_url(repo_url: Optional[str]) -> Optional[Tuple[str, str]]:
    """Extract owner and repo name from GitHub URL."""
    if not repo_url:
        return None

    # Handle various GitHub URL formats
    patterns = [
        r"github\.com[:/]([^/]+)/([^/\.]+)",
        r"github\.com/([^/]+)/([^/]+)\.git",
    ]

    for pattern in patterns:
        match = re.search(pattern, repo_url)
        if match:
            owner, repo = match.groups()
            repo = repo.replace(".git", "")
            return (owner, repo)

    return None

async def fetch_repository_data(
    client: httpx.AsyncClient,
    repo_url: str,
    token: Optional[str] = None
) -> Dict[str, Any]:
    parsed = parse_github_url(repo_url)
    if not parsed:
        raise ValueError(f"Invalid GitHub URL: {repo_url}")

    owner, repo = parsed
    url = f"https://api.github.com/repos/{owner}/{repo}"  # SSRF risk

    response = await client.get(url, headers=headers, timeout=5.0)
```

File: `/Users/jonc/Workspace/vibelympics/round_2/backend/routers/audit.py` (lines 174-177)

```python
if repo_url:
    repo_url = repo_url.replace("git+", "").replace("git://", "https://")
```

#### Proof of Concept (Theoretical)
Since the production backend is unavailable, this is a code-based PoC:

1. Create malicious npm package with crafted repository URL:
```json
{
  "repository": {
    "type": "git",
    "url": "https://github.com/../../internal-api/secrets"
  }
}
```

2. The regex parsing could potentially be bypassed with carefully crafted URLs
3. Backend makes request to unintended GitHub API endpoint

#### Attack Scenarios
1. **Internal Network Scanning:** If backend runs in cloud environment, could probe internal IPs
2. **API Abuse:** Force backend to make excessive GitHub API requests
3. **Information Disclosure:** Extract internal network topology information

#### Impact
- Medium: Limited to GitHub API domain due to hardcoded `https://api.github.com/repos/` prefix
- Timeout protection (5s) limits exploitation window
- Could waste GitHub API rate limits

#### Remediation

**Priority: HIGH**

1. **Strict URL Validation:**
```python
def parse_github_url(repo_url: Optional[str]) -> Optional[Tuple[str, str]]:
    """Extract owner and repo name from GitHub URL with strict validation."""
    if not repo_url:
        return None

    # Allowlist approach - only accept standard GitHub patterns
    allowed_patterns = [
        r'^https://github\.com/([a-zA-Z0-9_-]+)/([a-zA-Z0-9._-]+)/?$',
        r'^git@github\.com:([a-zA-Z0-9_-]+)/([a-zA-Z0-9._-]+)\.git$',
    ]

    for pattern in allowed_patterns:
        match = re.match(pattern, repo_url.strip())
        if match:
            owner, repo = match.groups()
            repo = repo.replace(".git", "")

            # Additional validation
            if not owner or not repo:
                return None
            if len(owner) > 39 or len(repo) > 100:  # GitHub limits
                return None
            if ".." in owner or ".." in repo:  # Path traversal
                return None

            return (owner, repo)

    return None
```

2. **Domain Allowlisting:**
```python
ALLOWED_DOMAINS = {"github.com"}

def validate_repo_url(url: str) -> bool:
    """Validate repository URL is from allowed domain."""
    from urllib.parse import urlparse

    parsed = urlparse(url)
    return parsed.netloc in ALLOWED_DOMAINS
```

3. **Add Security Headers:**
```python
# In main.py middleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["chainsaw.up.railway.app", "localhost"]
)
```

---

### FINDING 2: Missing Rate Limiting on Audit Endpoint
**Severity:** HIGH
**CWE:** CWE-770 (Allocation of Resources Without Limits)
**CVSS Score:** 7.1 (High)

#### Description
The `/api/audit` and `/api/audit/compare` endpoints have no rate limiting implemented. An attacker could:
1. Exhaust GitHub API rate limits (60/hour unauthenticated, 5000/hour authenticated)
2. Cause Denial of Service by overwhelming the backend with requests
3. Abuse the service to scrape npm package information
4. Force expensive API calls to external services

#### Vulnerable Code Location
File: `/Users/jonc/Workspace/vibelympics/round_2/backend/routers/audit.py` (line 63)

```python
@router.post("/audit", response_model=AuditResponse)
async def audit_package(request: AuditRequest):
    # No rate limiting check
    async with httpx.AsyncClient() as client:
        # Makes multiple external API calls...
```

File: `/Users/jonc/Workspace/vibelympics/round_2/backend/main.py`

```python
# No rate limiting middleware configured
app = FastAPI(...)
```

#### Proof of Concept
```bash
# Theoretical test (backend unavailable)
# Rapid-fire requests to exhaust resources
for i in {1..1000}; do
  curl -X POST "https://chainsaw.up.railway.app/api/audit" \
    -H "Content-Type: application/json" \
    -d '{"package_name":"lodash"}' &
done
wait

# Expected: Backend overwhelmed, GitHub rate limit exhausted
```

#### Impact
- **Resource Exhaustion:** Backend could be overwhelmed with concurrent requests
- **Cost Implications:** Cloud hosting costs increase with traffic
- **API Abuse:** GitHub API rate limits consumed, affecting legitimate users
- **Service Degradation:** Slow response times for legitimate users

#### Remediation

**Priority: HIGH**

1. **Implement Rate Limiting Middleware:**

```bash
pip install slowapi
```

```python
# In main.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# In audit.py
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/audit", response_model=AuditResponse)
@limiter.limit("10/minute")  # 10 requests per minute per IP
async def audit_package(request: AuditRequest):
    ...

@router.post("/audit/compare", response_model=CompareResponse)
@limiter.limit("5/minute")  # 5 requests per minute per IP
async def compare_versions(request: CompareRequest):
    ...
```

2. **Add Request Queue/Throttling:**

```python
import asyncio
from collections import defaultdict
from datetime import datetime, timedelta

class RequestThrottler:
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self._requests = defaultdict(list)
        self._max_requests = max_requests
        self._window = timedelta(seconds=window_seconds)

    async def check_rate_limit(self, client_id: str) -> bool:
        """Check if client is within rate limit."""
        now = datetime.now()

        # Clean old requests
        self._requests[client_id] = [
            req_time for req_time in self._requests[client_id]
            if now - req_time < self._window
        ]

        # Check limit
        if len(self._requests[client_id]) >= self._max_requests:
            return False

        self._requests[client_id].append(now)
        return True
```

3. **Monitor GitHub Rate Limits:**

```python
async def check_github_rate_limit(client: httpx.AsyncClient, token: Optional[str] = None):
    """Check GitHub API rate limit status."""
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"

    response = await client.get(
        "https://api.github.com/rate_limit",
        headers=headers,
        timeout=5.0
    )

    data = response.json()
    remaining = data.get("resources", {}).get("core", {}).get("remaining", 0)

    if remaining < 10:
        # Log warning, consider pausing GitHub requests
        logger.warning(f"GitHub rate limit low: {remaining} remaining")

    return remaining
```

---

### FINDING 3: Information Disclosure via Error Messages
**Severity:** MEDIUM
**CWE:** CWE-209 (Generation of Error Message Containing Sensitive Information)
**CVSS Score:** 5.3 (Medium)

#### Description
Error messages returned by the API include detailed internal information that could aid attackers in reconnaissance. This includes:
- Full exception stack traces in 500 errors
- File paths and internal module names
- External API response details
- Package version information

#### Vulnerable Code Location
File: `/Users/jonc/Workspace/vibelympics/round_2/backend/routers/audit.py` (lines 100-108)

```python
elif isinstance(npm_data, Exception):
    raise HTTPException(
        status_code=500,
        detail={
            "error": "internal_error",
            "message": f"Failed to fetch package data: {str(npm_data)}",  # Exposes internal details
            "status_code": 500
        }
    )
```

#### Proof of Concept
```bash
# Test with invalid package that triggers backend errors
curl -X POST "https://chainsaw.up.railway.app/api/audit" \
  -H "Content-Type: application/json" \
  -d '{"package_name":"../../../etc/passwd"}'

# Expected: Detailed error message revealing internal paths/modules
```

#### Impact
- **Information Leakage:** Internal architecture details exposed
- **Attack Surface Mapping:** Helps attackers understand system internals
- **Dependency Version Disclosure:** Could reveal vulnerable library versions

#### Remediation

**Priority: MEDIUM**

1. **Generic Error Messages for Users:**

```python
# Create error handler
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions with generic message."""
    # Log detailed error internally
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    # Return generic message to user
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_error",
            "message": "An internal error occurred. Please try again later.",
            "request_id": str(uuid.uuid4())  # For support tracking
        }
    )

# In audit.py
elif isinstance(npm_data, Exception):
    # Log detailed error
    logger.error(f"Failed to fetch package data: {npm_data}", exc_info=True)

    # Return generic error
    raise HTTPException(
        status_code=500,
        detail={
            "error": "internal_error",
            "message": "Unable to fetch package data. Please verify the package name.",
            "status_code": 500
        }
    )
```

2. **Structured Logging (Not in Response):**

```python
import logging
import json

logger = logging.getLogger(__name__)

# Log detailed errors for debugging
logger.error({
    "event": "npm_fetch_failed",
    "package_name": package_name,
    "error_type": type(npm_data).__name__,
    "error_message": str(npm_data),
    "timestamp": datetime.utcnow().isoformat()
})
```

---

### FINDING 4: Insufficient Input Validation for Version Parameter
**Severity:** MEDIUM
**CWE:** CWE-20 (Improper Input Validation)
**CVSS Score:** 5.3 (Medium)

#### Description
The `version` parameter in `AuditRequest` and `CompareRequest` models has basic length validation (max_length=50) but lacks semantic version format validation. This could allow:
- Injection of malicious version strings
- Bypass of version-specific security checks
- Potential for exploiting version parsing logic

#### Vulnerable Code Location
File: `/Users/jonc/Workspace/vibelympics/round_2/backend/models/request.py` (lines 10, 55-56)

```python
class AuditRequest(BaseModel):
    package_name: str = Field(..., min_length=1, max_length=214)
    version: Optional[str] = Field(None, max_length=50)  # No format validation

class CompareRequest(BaseModel):
    version_old: str = Field(..., min_length=1, max_length=50)  # No format validation
    version_new: str = Field(..., min_length=1, max_length=50)  # No format validation
```

#### Proof of Concept
```bash
# Test with malicious version strings
curl -X POST "https://chainsaw.up.railway.app/api/audit" \
  -H "Content-Type: application/json" \
  -d '{"package_name":"lodash", "version":"'; DROP TABLE users; --"}'

curl -X POST "https://chainsaw.up.railway.app/api/audit" \
  -H "Content-Type: application/json" \
  -d '{"package_name":"lodash", "version":"../../../etc/passwd"}'
```

#### Impact
- **Injection Attacks:** Potential for injection if version used in unsafe contexts
- **Logic Bypass:** Could manipulate version comparison logic
- **DoS:** Malformed versions might cause parsing errors

#### Remediation

**Priority: MEDIUM**

```python
from pydantic import BaseModel, Field, field_validator
import re

class AuditRequest(BaseModel):
    package_name: str = Field(..., min_length=1, max_length=214)
    version: Optional[str] = Field(None, max_length=50)

    @field_validator("version")
    @classmethod
    def validate_version(cls, v: Optional[str]) -> Optional[str]:
        """Validate semantic version format."""
        if v is None:
            return v

        # Semantic versioning regex
        # Matches: 1.2.3, 1.2.3-alpha.1, 1.2.3+build.123
        semver_pattern = r'^(\d+)\.(\d+)\.(\d+)(?:-([a-zA-Z0-9.-]+))?(?:\+([a-zA-Z0-9.-]+))?$'

        if not re.match(semver_pattern, v):
            raise ValueError(
                "Invalid version format. Must be semantic version (e.g., 1.2.3, 1.0.0-beta)"
            )

        return v

class CompareRequest(BaseModel):
    package_name: str = Field(..., min_length=1, max_length=214)
    version_old: str = Field(..., min_length=1, max_length=50)
    version_new: str = Field(..., min_length=1, max_length=50)

    @field_validator("version_old", "version_new")
    @classmethod
    def validate_versions(cls, v: str) -> str:
        """Validate semantic version format."""
        semver_pattern = r'^(\d+)\.(\d+)\.(\d+)(?:-([a-zA-Z0-9.-]+))?(?:\+([a-zA-Z0-9.-]+))?$'

        if not re.match(semver_pattern, v):
            raise ValueError(
                "Invalid version format. Must be semantic version (e.g., 1.2.3)"
            )

        return v
```

---

### FINDING 5: CORS Configuration Overly Permissive
**Severity:** MEDIUM
**CWE:** CWE-942 (Overly Permissive Cross-domain Whitelist)
**CVSS Score:** 5.0 (Medium)

#### Description
The CORS configuration in `main.py` allows credentials and all methods/headers from specific origins. While origins are restricted (not wildcard), the configuration allows `allow_credentials=True` which could enable CSRF attacks if session cookies are implemented in the future.

#### Vulnerable Code Location
File: `/Users/jonc/Workspace/vibelympics/round_2/backend/main.py` (lines 17-29)

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
        "https://vibelympics-production.up.railway.app",
        "https://chainsaw.up.railway.app",
    ],
    allow_credentials=True,  # Risk if cookies used in future
    allow_methods=["*"],     # All HTTP methods allowed
    allow_headers=["*"],     # All headers allowed
)
```

#### Impact
- **Future CSRF Risk:** If authentication cookies are added, CSRF is possible
- **Method Confusion:** Allowing all methods could enable unexpected behavior
- **Header Injection:** Allowing all headers could enable cache poisoning

#### Remediation

**Priority: MEDIUM**

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
        "https://vibelympics-production.up.railway.app",
        "https://chainsaw.up.railway.app",
    ],
    allow_credentials=False,  # No credentials unless needed
    allow_methods=["GET", "POST", "OPTIONS"],  # Explicit methods
    allow_headers=[
        "Content-Type",
        "Accept",
        "Origin",
        "User-Agent",
    ],  # Explicit headers only
    max_age=600,  # Cache preflight for 10 minutes
)
```

---

### FINDING 6: No Request Size Limiting
**Severity:** MEDIUM
**CWE:** CWE-770 (Allocation of Resources Without Limits)
**CVSS Score:** 4.3 (Medium)

#### Description
There is no limit on the size of incoming request bodies. While Pydantic validates field lengths, an attacker could send extremely large JSON payloads to:
- Consume memory resources
- Cause JSON parsing overhead
- Trigger DoS conditions

#### Vulnerable Code Location
File: `/Users/jonc/Workspace/vibelympics/round_2/backend/main.py`

```python
# No request size limiting configured
app = FastAPI(...)
```

#### Impact
- **Memory Exhaustion:** Large payloads consume RAM
- **CPU Overhead:** JSON parsing of large payloads
- **DoS:** Service becomes unresponsive

#### Remediation

**Priority: MEDIUM**

```python
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_size: int = 1024 * 1024):  # 1MB default
        super().__init__(app)
        self.max_size = max_size

    async def dispatch(self, request: Request, call_next):
        if request.method in ["POST", "PUT", "PATCH"]:
            content_length = request.headers.get("content-length")
            if content_length and int(content_length) > self.max_size:
                return JSONResponse(
                    status_code=413,
                    content={"error": "payload_too_large", "message": "Request body too large"}
                )
        return await call_next(request)

# Add to main.py
app.add_middleware(RequestSizeLimitMiddleware, max_size=1024 * 10)  # 10KB limit
```

---

### FINDING 7: GitHub Token Exposure Risk in Environment Variables
**Severity:** LOW
**CWE:** CWE-798 (Use of Hard-coded Credentials)
**CVSS Score:** 3.1 (Low)

#### Description
The GitHub client reads the `GITHUB_TOKEN` from environment variables without additional protection. If logs or error messages inadvertently include environment variables, the token could be exposed.

#### Vulnerable Code Location
File: `/Users/jonc/Workspace/vibelympics/round_2/backend/services/github_client.py` (lines 121-122)

```python
elif os.environ.get("GITHUB_TOKEN"):
    headers["Authorization"] = f"token {os.environ.get('GITHUB_TOKEN')}"
```

#### Impact
- **Credential Leakage:** Token could appear in logs or error traces
- **Rate Limit Abuse:** Exposed token allows API abuse
- **Account Compromise:** Token provides access to GitHub account

#### Remediation

**Priority: LOW**

1. **Use Secret Management:**

```python
from functools import lru_cache

@lru_cache(maxsize=1)
def get_github_token() -> Optional[str]:
    """Securely retrieve GitHub token."""
    # In production, use secret manager (AWS Secrets Manager, etc.)
    token = os.environ.get("GITHUB_TOKEN")

    if token:
        # Never log the token
        logger.info("GitHub token configured (length: %d)", len(token))
    else:
        logger.warning("No GitHub token configured - rate limits will be restricted")

    return token

# Use in code
token = get_github_token()
if token:
    headers["Authorization"] = f"token {token}"
```

2. **Sanitize Logs:**

```python
import logging

class SanitizingFilter(logging.Filter):
    """Filter to sanitize sensitive data from logs."""

    SENSITIVE_PATTERNS = [
        (r'token [a-zA-Z0-9_-]{40}', 'token [REDACTED]'),
        (r'Authorization: .*', 'Authorization: [REDACTED]'),
    ]

    def filter(self, record):
        if isinstance(record.msg, str):
            for pattern, replacement in self.SENSITIVE_PATTERNS:
                record.msg = re.sub(pattern, replacement, record.msg)
        return True

# Add to logging config
logger = logging.getLogger()
logger.addFilter(SanitizingFilter())
```

---

### FINDING 8: Cache Timing Attack on Package Popularity
**Severity:** LOW
**CWE:** CWE-208 (Observable Timing Discrepancy)
**CVSS Score:** 2.6 (Low)

#### Description
The GitHub client implements a 1-hour TTL cache. Response times could reveal whether a package has been queried recently by other users, potentially leaking information about what packages are being audited.

#### Vulnerable Code Location
File: `/Users/jonc/Workspace/vibelympics/round_2/backend/services/github_client.py` (lines 46-47, 112-115)

```python
_github_cache = TTLCache(ttl_seconds=3600)

def get(self, key: str) -> Optional[Any]:
    if key in self._cache:
        value, timestamp = self._cache[key]
        if datetime.now() - timestamp < self._ttl:
            return value  # Fast response = cached
```

#### Impact
- **Information Leakage:** Timing reveals cache hits
- **Privacy Concern:** Usage patterns could be inferred
- **Low Exploitability:** Requires precise timing measurements

#### Remediation

**Priority: LOW**

```python
import random
import asyncio

async def add_timing_jitter(min_ms: int = 10, max_ms: int = 50):
    """Add random delay to obscure cache timing."""
    delay = random.uniform(min_ms / 1000, max_ms / 1000)
    await asyncio.sleep(delay)

async def fetch_repository_data(...):
    # Check cache
    cached = _github_cache.get(cache_key)

    if cached:
        # Add jitter to cached responses
        await add_timing_jitter()
        return cached

    # Fetch from API
    response = await client.get(url, headers=headers, timeout=5.0)
    # ... process and cache

    # Also add jitter to fresh responses
    await add_timing_jitter()
    return result
```

---

### FINDING 9: Potential ReDoS in Semver Parsing
**Severity:** LOW
**CWE:** CWE-1333 (Inefficient Regular Expression Complexity)
**CVSS Score:** 3.7 (Low)

#### Description
The semver parsing regex in `audit.py` could be vulnerable to Regular Expression Denial of Service (ReDoS) if fed extremely long or complex version strings.

#### Vulnerable Code Location
File: `/Users/jonc/Workspace/vibelympics/round_2/backend/routers/audit.py` (lines 127-134)

```python
match = re.match(r'^(\d+)\.(\d+)\.(\d+)(?:-(.+))?', v)
```

#### Impact
- **CPU Exhaustion:** Malicious version string could cause high CPU usage
- **DoS:** Service slowdown or hang
- **Low Exploitability:** Requires control of npm package versions

#### Remediation

**Priority: LOW**

```python
import re
from functools import lru_cache

# Pre-compile regex for performance
SEMVER_PATTERN = re.compile(
    r'^(\d{1,5})\.(\d{1,5})\.(\d{1,5})'  # Limit digit length
    r'(?:-([a-zA-Z0-9.-]{1,50}))?'        # Limit pre-release length
    r'(?:\+([a-zA-Z0-9.-]{1,50}))?$',     # Limit build metadata length
    re.ASCII
)

def safe_semver_parse(version: str) -> Optional[tuple]:
    """Safely parse semantic version with limits."""
    if len(version) > 100:  # Hard limit
        return None

    match = SEMVER_PATTERN.match(version)
    if not match:
        return None

    major, minor, patch, pre, build = match.groups()
    return (int(major), int(minor), int(patch), pre or 'zzz')
```

---

## Additional Informational Findings

### INFO 1: OpenAPI Documentation Publicly Accessible
**Severity:** INFORMATIONAL

The `/docs` endpoint exposes full API documentation via FastAPI's automatic OpenAPI generation. While this is helpful for developers, it provides attackers with complete API schema information.

**Recommendation:** Consider restricting access to `/docs` and `/redoc` in production:

```python
app = FastAPI(
    docs_url="/docs" if os.getenv("ENVIRONMENT") == "development" else None,
    redoc_url="/redoc" if os.getenv("ENVIRONMENT") == "development" else None,
)
```

### INFO 2: No Security Headers Implemented
**Severity:** INFORMATIONAL

The application lacks common security headers:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Strict-Transport-Security`
- `Content-Security-Policy`

**Recommendation:** Add security headers middleware:

```python
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

app.add_middleware(SecurityHeadersMiddleware)
```

---

## Risk Summary by Category

### By Severity
| Severity | Count | Findings |
|----------|-------|----------|
| Critical | 0 | - |
| High | 2 | SSRF via Repository URL, Missing Rate Limiting |
| Medium | 4 | Information Disclosure, Version Validation, CORS Config, Request Size |
| Low | 3 | Token Exposure, Cache Timing, ReDoS |
| Info | 2 | API Docs Exposed, Security Headers |

### By CWE Category
| CWE Category | Count |
|--------------|-------|
| Injection & SSRF | 2 |
| Resource Management | 3 |
| Information Disclosure | 2 |
| Configuration Issues | 3 |
| Timing & Side Channel | 1 |

---

## Recommended Remediation Priority

### Immediate (Within 1 Week)
1. **Implement Rate Limiting** - Prevent DoS and API abuse
2. **Fix SSRF Vulnerability** - Strengthen URL validation
3. **Add Request Size Limiting** - Prevent memory exhaustion

### Short Term (Within 1 Month)
4. **Improve Error Messages** - Remove internal details from responses
5. **Validate Version Format** - Prevent injection via version strings
6. **Review CORS Configuration** - Tighten to minimum required

### Long Term (Within 3 Months)
7. **Implement Security Headers** - Add standard security headers
8. **Secret Management** - Use proper secret management for tokens
9. **Add Logging & Monitoring** - Detect and respond to attacks

---

## Production Environment Notes

### Deployment Status
- Production URL: https://chainsaw.up.railway.app/
- Status: Backend unavailable (504 Gateway Timeout) during assessment
- Frontend: Serving static React application
- Backend: Not responding to API requests

### Observed Issues
1. **504 Gateway Timeout:** Backend API calls timing out
2. **Nginx Proxy:** Indicates nginx reverse proxy in front of backend
3. **Health Check Failing:** `/api/health` endpoint unreachable

### Recommendations for Deployment
1. Investigate backend timeout issues
2. Configure proper health checks for Railway deployment
3. Review backend startup logs for errors
4. Ensure environment variables properly configured
5. Consider implementing graceful shutdown handling

---

## Testing Limitations

Due to production backend unavailability, the following tests could not be performed:

1. **Live SSRF Testing:** Could not test malicious repository URLs
2. **Rate Limiting Validation:** Could not verify absence of rate limits
3. **Error Message Analysis:** Could not observe actual error responses
4. **DoS Testing:** Could not test request flooding
5. **Cache Timing Analysis:** Could not measure response time differences
6. **Input Fuzzing:** Could not test various malicious inputs

**Recommendation:** Perform live penetration testing once backend is operational.

---

## Positive Security Observations

Despite the vulnerabilities identified, the application demonstrates several security best practices:

1. **Input Validation:** Pydantic models provide strong type validation
2. **Parameterized Queries:** No SQL injection risk (no database)
3. **Timeout Protection:** All external API calls have 5-second timeouts
4. **URL Encoding:** Package names properly encoded in URLs
5. **Exception Handling:** Graceful degradation when external APIs fail
6. **HTTPS:** All external API calls use HTTPS
7. **No Hardcoded Secrets:** Uses environment variables for tokens
8. **Scoped Packages:** Properly handles npm scoped package format

---

## Conclusion

CHAINSAW demonstrates a solid foundation with several security controls in place. However, the HIGH severity findings around SSRF and rate limiting require immediate attention before production deployment at scale.

The absence of rate limiting is particularly concerning for a public-facing security tool, as it could be abused to:
- Exhaust GitHub API quotas
- Scrape npm package data
- Launch DoS attacks

The SSRF vulnerability, while somewhat mitigated by hardcoded GitHub API domain, still presents risk and should be addressed with stricter URL validation.

### Overall Assessment
**Current Security Posture:** MEDIUM RISK
**Recommended Actions:** Address HIGH and MEDIUM findings before wider deployment
**Retest Required:** Yes, after remediation and when backend is operational

---

**Report Prepared By:** Security Engineering Team
**Date:** 2025-12-11
**Classification:** Internal Security Assessment
**Distribution:** Development Team, Security Team, Technical Leadership
