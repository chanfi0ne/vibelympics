# CHAINSAW Security Quick Fixes

Quick reference guide for developers to implement critical security remediations.

---

## URGENT: Fix These First (HIGH Priority)

### 1. Add Rate Limiting (2-4 hours)

**Install dependency:**
```bash
cd backend
pip install slowapi
echo "slowapi==0.1.9" >> requirements.txt
```

**Update `main.py`:**
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
```

**Update `routers/audit.py`:**
```python
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request

limiter = Limiter(key_func=get_remote_address)

@router.post("/audit", response_model=AuditResponse)
@limiter.limit("10/minute")
async def audit_package(request: Request, audit_request: AuditRequest):
    # Rename 'request' parameter to avoid conflict
    package_name = audit_request.package_name
    # ... rest of function
```

**Test:**
```bash
# Should get 429 after 10 requests in 1 minute
for i in {1..15}; do
    curl -X POST http://localhost:8000/api/audit \
        -H "Content-Type: application/json" \
        -d '{"package_name":"lodash"}'
done
```

---

### 2. Fix SSRF in GitHub URL Parsing (2 hours)

**Update `services/github_client.py`:**

```python
import re
from typing import Optional, Tuple
from urllib.parse import urlparse

# Allowlist of trusted domains
ALLOWED_GITHUB_DOMAINS = {"github.com", "api.github.com"}

def parse_github_url(repo_url: Optional[str]) -> Optional[Tuple[str, str]]:
    """
    Extract owner and repo name from GitHub URL with strict validation.

    Args:
        repo_url: GitHub repository URL

    Returns:
        (owner, repo) tuple or None if invalid
    """
    if not repo_url:
        return None

    # Remove whitespace
    repo_url = repo_url.strip()

    # Validate URL format
    try:
        parsed = urlparse(repo_url)

        # Must be from allowed domain
        if parsed.netloc not in ALLOWED_GITHUB_DOMAINS:
            # Try without protocol
            if not any(domain in repo_url for domain in ALLOWED_GITHUB_DOMAINS):
                return None
    except Exception:
        return None

    # Strict pattern matching - only accept standard GitHub URLs
    patterns = [
        r'^https?://github\.com/([a-zA-Z0-9_-]+)/([a-zA-Z0-9._-]+?)(?:\.git)?/?$',
        r'^git@github\.com:([a-zA-Z0-9_-]+)/([a-zA-Z0-9._-]+?)\.git$',
        r'^github\.com/([a-zA-Z0-9_-]+)/([a-zA-Z0-9._-]+?)(?:\.git)?/?$',
    ]

    for pattern in patterns:
        match = re.match(pattern, repo_url)
        if match:
            owner, repo = match.groups()

            # Additional validation
            if not owner or not repo:
                return None

            # GitHub username/org limits (max 39 chars)
            if len(owner) > 39:
                return None

            # GitHub repo name limits (max 100 chars)
            if len(repo) > 100:
                return None

            # Prevent path traversal
            if ".." in owner or ".." in repo:
                return None

            # Prevent special chars that could be exploited
            if any(char in owner for char in ['/', '\\', '<', '>', '|']):
                return None

            return (owner, repo)

    return None
```

**Add tests in `tests/test_github_client.py`:**
```python
import pytest
from services.github_client import parse_github_url

def test_parse_valid_github_urls():
    """Test valid GitHub URL formats."""
    assert parse_github_url("https://github.com/lodash/lodash") == ("lodash", "lodash")
    assert parse_github_url("https://github.com/user/repo.git") == ("user", "repo")
    assert parse_github_url("git@github.com:user/repo.git") == ("user", "repo")

def test_reject_ssrf_attempts():
    """Test that SSRF attempts are rejected."""
    # Path traversal
    assert parse_github_url("https://github.com/../../etc/passwd") is None
    assert parse_github_url("https://github.com/../internal-api/secret") is None

    # Wrong domain
    assert parse_github_url("https://evil.com/user/repo") is None
    assert parse_github_url("http://169.254.169.254/latest/meta-data") is None

    # Special characters
    assert parse_github_url("https://github.com/user;rm -rf/repo") is None
    assert parse_github_url("https://github.com/user|whoami/repo") is None

def test_reject_invalid_formats():
    """Test that invalid formats are rejected."""
    assert parse_github_url("not-a-url") is None
    assert parse_github_url("") is None
    assert parse_github_url(None) is None
    assert parse_github_url("https://github.com/toolongusername" + "a"*100 + "/repo") is None
```

**Run tests:**
```bash
cd backend
pytest tests/test_github_client.py -v
```

---

### 3. Add Request Size Limiting (1 hour)

**Create `middleware/security.py`:**
```python
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to limit request body size."""

    def __init__(self, app, max_size: int = 10 * 1024):  # 10KB default
        super().__init__(app)
        self.max_size = max_size

    async def dispatch(self, request: Request, call_next):
        if request.method in ["POST", "PUT", "PATCH"]:
            content_length = request.headers.get("content-length")

            if content_length:
                try:
                    size = int(content_length)
                    if size > self.max_size:
                        return JSONResponse(
                            status_code=413,
                            content={
                                "error": "payload_too_large",
                                "message": f"Request body exceeds maximum size of {self.max_size} bytes",
                                "max_size": self.max_size,
                                "provided_size": size
                            }
                        )
                except ValueError:
                    pass

        return await call_next(request)
```

**Update `main.py`:**
```python
from middleware.security import RequestSizeLimitMiddleware

# Add after CORS middleware
app.add_middleware(RequestSizeLimitMiddleware, max_size=10 * 1024)  # 10KB
```

**Test:**
```bash
# Should return 413
python3 -c "
import requests
large_payload = {'package_name': 'a' * (11 * 1024)}
r = requests.post('http://localhost:8000/api/audit', json=large_payload)
print(f'Status: {r.status_code}')
print(f'Response: {r.json()}')
"
```

---

## MEDIUM Priority Fixes

### 4. Sanitize Error Messages (3 hours)

**Update `routers/audit.py`:**
```python
import logging
import uuid

logger = logging.getLogger(__name__)

# Replace detailed error messages
elif isinstance(npm_data, Exception):
    # Log detailed error for debugging
    error_id = str(uuid.uuid4())
    logger.error(
        f"[{error_id}] Failed to fetch package data for '{package_name}': {type(npm_data).__name__}: {str(npm_data)}",
        exc_info=True
    )

    # Return generic error to user
    raise HTTPException(
        status_code=500,
        detail={
            "error": "internal_error",
            "message": "Unable to fetch package data. Please verify the package name and try again.",
            "error_id": error_id  # For support correlation
        }
    )
```

---

### 5. Add Version Validation (2 hours)

**Update `models/request.py`:**
```python
import re
from pydantic import field_validator

class AuditRequest(BaseModel):
    package_name: str = Field(...)
    version: Optional[str] = Field(None, max_length=50)

    @field_validator("version")
    @classmethod
    def validate_version(cls, v: Optional[str]) -> Optional[str]:
        """Validate semantic version format."""
        if v is None:
            return v

        # Semantic versioning pattern
        # Matches: 1.2.3, 1.2.3-alpha.1, 1.2.3+build.123
        semver_pattern = r'^(\d{1,5})\.(\d{1,5})\.(\d{1,5})(?:-([a-zA-Z0-9.-]{1,50}))?(?:\+([a-zA-Z0-9.-]{1,50}))?$'

        if not re.match(semver_pattern, v, re.ASCII):
            raise ValueError(
                "Invalid version format. Must be semantic version (e.g., 1.2.3, 1.0.0-beta.1)"
            )

        return v
```

**Test:**
```bash
# Should reject invalid versions
curl -X POST http://localhost:8000/api/audit \
    -H "Content-Type: application/json" \
    -d '{"package_name":"lodash","version":"not-a-version"}' | jq .

# Should accept valid versions
curl -X POST http://localhost:8000/api/audit \
    -H "Content-Type: application/json" \
    -d '{"package_name":"lodash","version":"4.17.21"}' | jq .
```

---

### 6. Tighten CORS (1 hour)

**Update `main.py`:**
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
    allow_credentials=False,  # Disable unless needed
    allow_methods=["GET", "POST", "OPTIONS"],  # Explicit only
    allow_headers=[
        "Content-Type",
        "Accept",
        "Origin",
        "User-Agent",
    ],
    max_age=600,
)
```

---

### 7. Add Security Headers (1 hour)

**Update `middleware/security.py`:**
```python
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Prevent MIME sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        # Enable XSS protection
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Force HTTPS (only in production)
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        # Content Security Policy
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' https://registry.npmjs.org https://api.github.com"
        )

        return response
```

**Update `main.py`:**
```python
from middleware.security import SecurityHeadersMiddleware

app.add_middleware(SecurityHeadersMiddleware)
```

---

## Testing Checklist

After implementing fixes, run these tests:

```bash
# 1. Unit tests
cd backend
pytest tests/ -v --cov=.

# 2. Rate limiting test
./docs/RED_TEAM_POC.sh http://localhost:8000

# 3. Integration test
curl -X POST http://localhost:8000/api/audit \
    -H "Content-Type: application/json" \
    -d '{"package_name":"lodash"}' | jq .

# 4. Security headers check
curl -I http://localhost:8000/api/health | grep -i "x-content-type-options"

# 5. SSRF test
pytest tests/test_github_client.py -v -k ssrf
```

---

## Deployment Checklist

Before deploying to production:

- [ ] All HIGH priority fixes implemented
- [ ] All tests passing
- [ ] Security headers verified
- [ ] Rate limiting tested
- [ ] Error messages sanitized
- [ ] CORS configuration reviewed
- [ ] Environment variables set correctly
- [ ] Logging configured
- [ ] Monitoring enabled
- [ ] Backup plan ready

---

## Quick Commands Reference

```bash
# Install security dependencies
pip install slowapi==0.1.9

# Run security tests
pytest tests/ -v -k security

# Check for vulnerabilities in dependencies
pip install safety
safety check

# Scan for secrets
pip install detect-secrets
detect-secrets scan

# Static analysis
pip install bandit
bandit -r . -f json -o security-report.json

# Run full test suite
pytest tests/ -v --cov=. --cov-report=html

# Start with security features
export ENVIRONMENT=production
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## Emergency Contacts

**Security Issue Found?**
1. Do NOT commit to main branch
2. Create private branch: `git checkout -b security/fix-ISSUE-NAME`
3. Implement fix following this guide
4. Run all tests
5. Create PR with `[SECURITY]` prefix
6. Request immediate review

**Questions?**
- Security Team: security@chainsaw.dev
- Tech Lead: Review ADR-001 for architecture decisions
- Documentation: `/docs/RED_TEAM_ASSESSMENT.md`

---

**Last Updated:** 2025-12-11
**Version:** 1.0
**Maintained By:** Security Engineering Team
