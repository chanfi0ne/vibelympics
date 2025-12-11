# Repojacker - Software Requirements Specification

**Project:** Repojacker - npm Supply Chain Security Auditor
**Version:** 1.0.0
**Date:** 2025-12-10
**Status:** Active Development

---

## 1. Project Overview

### 1.1 Objectives

Build a containerized web application that audits npm packages for supply chain security risks by analyzing multiple security signals and presenting an intuitive risk assessment with visual components.

**Success Criteria:**
1. Complete audit of typical packages in under 5 seconds
2. Accurately detect known-bad packages (historical attacks)
3. Deploy with single `docker compose up` command
4. Produce clear, actionable security findings
5. Handle external API failures gracefully

### 1.2 Associated Documents

- **PRD:** `/Users/jonc/Workspace/vibelympics/round_2/docs/PRD.md`
- **Design:** `/Users/jonc/Workspace/vibelympics/round_2/docs/DESIGN.md`
- **Style Guide:** `/Users/jonc/Workspace/vibelympics/round_2/docs/STYLE_GUIDE.md`
- **ADR-001:** `/Users/jonc/Workspace/vibelympics/round_2/docs/ADR-001-architecture.md`

### 1.3 Technology Stack

**Backend:** Python 3.12, FastAPI, httpx, Pydantic, uvicorn
**Frontend:** React 18, Vite, TailwindCSS, Recharts
**Deployment:** Docker, Docker Compose, nginx

---

## 2. Requirements Breakdown

### 2.1 Effort Estimation Guide

- **S (Small):** 30-60 minutes - Single function/component with tests
- **M (Medium):** 1-2 hours - Multiple functions or complex component with integration
- **L (Large):** 2-4 hours - Multiple components, external API integration, complex logic

### 2.2 Requirements Table

| REQ-ID | Component | Description | Acceptance Criteria | Effort | Status | Dependencies |
|--------|-----------|-------------|-------------------|--------|--------|--------------|
| **INFRASTRUCTURE** |
| REQ-001 | Backend | Docker setup for Python backend | Dockerfile builds, runs uvicorn on port 8000 | S | Not Started | None |
| REQ-002 | Backend | FastAPI app skeleton with health endpoint | GET /api/health returns 200 with JSON | S | Not Started | REQ-001 |
| REQ-003 | Backend | Pydantic models for request/response | Models validate/serialize correctly | S | Not Started | REQ-002 |
| REQ-004 | Frontend | Docker setup for React frontend | Multi-stage build, nginx serves on port 80 | S | Not Started | None |
| REQ-005 | Frontend | Vite + React app skeleton | Dev server runs, builds successfully | S | Not Started | REQ-004 |
| REQ-006 | Frontend | TailwindCSS configuration with custom theme | Style guide colors/fonts available | S | Not Started | REQ-005 |
| REQ-007 | Infrastructure | Docker Compose configuration | Both services start with `docker compose up` | S | Not Started | REQ-001, REQ-004 |
| **BACKEND - NPM CLIENT** |
| REQ-008 | Backend | npm registry client - package metadata | Fetch package.json from registry.npmjs.org | S | Not Started | REQ-002 |
| REQ-009 | Backend | npm registry client - error handling | Handle 404, timeout, network errors gracefully | S | Not Started | REQ-008 |
| REQ-010 | Backend | npm registry client - scoped packages | Support @scope/package format | S | Not Started | REQ-008 |
| REQ-011 | Backend | npm downloads client | Fetch weekly downloads from api.npmjs.org | S | Not Started | REQ-002 |
| REQ-012 | Backend | npm client integration tests | Verify real API calls with known packages | M | Not Started | REQ-008, REQ-011 |
| **BACKEND - GITHUB CLIENT** |
| REQ-013 | Backend | GitHub repo URL parser | Extract owner/repo from GitHub URLs | S | Not Started | REQ-002 |
| REQ-014 | Backend | GitHub API client - repository data | Fetch repo metadata (stars, forks, updated) | S | Not Started | REQ-013 |
| REQ-015 | Backend | GitHub API client - rate limit handling | Detect rate limit, return cached or degraded response | M | Not Started | REQ-014 |
| REQ-016 | Backend | GitHub API client - advisories | Fetch security advisories for package | S | Not Started | REQ-013 |
| REQ-017 | Backend | GitHub client caching strategy | TTL cache (1hr) for repo data | M | Not Started | REQ-014 |
| REQ-018 | Backend | GitHub client integration tests | Verify caching, rate limit handling | M | Not Started | REQ-014, REQ-015, REQ-017 |
| **BACKEND - ANALYSIS SERVICES** |
| REQ-019 | Backend | Typosquatting detection - popular packages list | Load list of 100+ popular packages | S | Not Started | REQ-002 |
| REQ-020 | Backend | Typosquatting detection - similarity algorithm | Levenshtein distance check (threshold 0.8) | M | Not Started | REQ-019 |
| REQ-021 | Backend | Typosquatting detection - unit tests | Test known typosquats (lodahs→lodash) | S | Not Started | REQ-020 |
| REQ-022 | Backend | Install script analyzer | Detect preinstall/postinstall scripts | S | Not Started | REQ-002 |
| REQ-023 | Backend | Dangerous command detection | Flag curl, wget, eval, bash -c, etc. | S | Not Started | REQ-022 |
| REQ-024 | Backend | Install script analyzer - unit tests | Test scripts with dangerous patterns | S | Not Started | REQ-023 |
| REQ-025 | Backend | Package age analyzer | Calculate age, flag packages <30 days | S | Not Started | REQ-002 |
| REQ-026 | Backend | Maintainer analyzer | Count maintainers, detect single maintainer | S | Not Started | REQ-002 |
| REQ-027 | Backend | Maintainer analyzer - recent changes | Detect new maintainers on old packages | M | Not Started | REQ-026 |
| REQ-028 | Backend | Repository verification | Verify repo exists, not archived, name matches | M | Not Started | REQ-014 |
| REQ-029 | Backend | Download velocity analyzer | Flag suspicious download spikes | S | Not Started | REQ-011 |
| REQ-030 | Backend | Vulnerability analyzer | Parse advisories into findings | S | Not Started | REQ-016 |
| **BACKEND - SCORING ENGINE** |
| REQ-031 | Backend | Risk factor model | RiskFactor Pydantic model with severity/category | S | Not Started | REQ-003 |
| REQ-032 | Backend | Risk score calculator | Sum severity points, cap at 100 | S | Not Started | REQ-031 |
| REQ-033 | Backend | Risk level classifier | Map score to low/medium/high/critical | S | Not Started | REQ-032 |
| REQ-034 | Backend | Radar score calculator | Category scores (authenticity, maintenance, etc.) | M | Not Started | REQ-031 |
| REQ-035 | Backend | Scoring engine unit tests | Test bounds, edge cases, known packages | M | Not Started | REQ-032, REQ-033, REQ-034 |
| **BACKEND - AUDIT ORCHESTRATOR** |
| REQ-036 | Backend | Audit endpoint - request validation | POST /api/audit validates package name | S | Not Started | REQ-003 |
| REQ-037 | Backend | Audit orchestrator - parallel API calls | Use asyncio.gather for concurrent fetching | M | Not Started | REQ-008, REQ-011, REQ-014, REQ-016 |
| REQ-038 | Backend | Audit orchestrator - graceful degradation | Handle partial failures, continue with available data | M | Not Started | REQ-037 |
| REQ-039 | Backend | Audit orchestrator - analysis pipeline | Run all analyzers on fetched data | M | Not Started | REQ-019-REQ-030 |
| REQ-040 | Backend | Audit orchestrator - response assembly | Build complete AuditResponse with all data | M | Not Started | REQ-039 |
| REQ-041 | Backend | Audit endpoint integration tests | Test complete flow with lodash, express | M | Not Started | REQ-036-REQ-040 |
| **FRONTEND - CORE COMPONENTS** |
| REQ-042 | Frontend | SearchBar component | Input field + button, emoji validation | S | Not Started | REQ-006 |
| REQ-043 | Frontend | SearchBar - form submission | Call audit API on submit, handle loading | S | Not Started | REQ-042 |
| REQ-044 | Frontend | useAudit hook | Manage loading/result/error state | S | Not Started | REQ-005 |
| REQ-045 | Frontend | Loading component | Terminal-style loading animation | S | Not Started | REQ-006 |
| REQ-046 | Frontend | Error display component | Show API errors clearly | S | Not Started | REQ-006 |
| REQ-047 | Frontend | RiskScore component | Large score display with severity color | M | Not Started | REQ-006 |
| REQ-048 | Frontend | RiskScore - count-up animation | Animate from 0 to score value | S | Not Started | REQ-047 |
| REQ-049 | Frontend | RiskRadar component with Recharts | Radar chart with 4 categories | M | Not Started | REQ-006 |
| REQ-050 | Frontend | RiskRadar - draw animation | Animate chart appearance | S | Not Started | REQ-049 |
| REQ-051 | Frontend | FindingsList component | Table/list of findings with severity badges | M | Not Started | REQ-006 |
| REQ-052 | Frontend | FindingsList - staggered animation | Fade in findings sequentially | S | Not Started | REQ-051 |
| REQ-053 | Frontend | MetadataCard component | Display package metadata in card | S | Not Started | REQ-006 |
| REQ-054 | Frontend | MetadataCard - repository verification icon | Show checkmark/warning based on verification | S | Not Started | REQ-053 |
| **FRONTEND - LAYOUT & STYLING** |
| REQ-055 | Frontend | Header component with logo | REPOJACKER logo with tagline | S | Not Started | REQ-006 |
| REQ-056 | Frontend | Main layout grid | Responsive 2-column grid for results | S | Not Started | REQ-006 |
| REQ-057 | Frontend | Severity color system | Implement severity badge styles from style guide | S | Not Started | REQ-006 |
| REQ-058 | Frontend | Terminal aesthetic effects | Scanlines, noise, glow effects (subtle) | S | Not Started | REQ-006 |
| REQ-059 | Frontend | Mobile responsive layout | Single column on mobile, stack components | S | Not Started | REQ-056 |
| **INTEGRATION & TESTING** |
| REQ-060 | Testing | Backend unit tests - npm client | Test package fetching, error handling | S | Not Started | REQ-008-REQ-011 |
| REQ-061 | Testing | Backend unit tests - GitHub client | Test repo fetching, caching, rate limits | M | Not Started | REQ-013-REQ-017 |
| REQ-062 | Testing | Backend unit tests - analyzers | Test each analyzer independently | M | Not Started | REQ-019-REQ-030 |
| REQ-063 | Testing | Backend unit tests - scoring | Test score calculation edge cases | S | Not Started | REQ-031-REQ-035 |
| REQ-064 | Testing | Backend integration tests - audit endpoint | Test complete audit with mocked APIs | M | Not Started | REQ-036-REQ-041 |
| REQ-065 | Testing | E2E test - known good package | Test lodash returns low risk score | S | Not Started | REQ-007, REQ-041 |
| REQ-066 | Testing | E2E test - known typosquat | Test lodahs flags similarity to lodash | S | Not Started | REQ-007, REQ-041 |
| REQ-067 | Testing | E2E test - package with install scripts | Test package with postinstall returns warning | S | Not Started | REQ-007, REQ-041 |
| REQ-068 | Testing | E2E test - nonexistent package | Test 404 error handling | S | Not Started | REQ-007, REQ-041 |
| REQ-069 | Testing | E2E test - GitHub rate limit | Test graceful degradation when GitHub limited | M | Not Started | REQ-007, REQ-041 |
| **DEPLOYMENT & POLISH** |
| REQ-070 | Infrastructure | Environment variable configuration | Support GITHUB_TOKEN optional env var | S | Not Started | REQ-007 |
| REQ-071 | Infrastructure | nginx configuration for frontend | Proper routing, API proxy | S | Not Started | REQ-004 |
| REQ-072 | Infrastructure | Health check configuration | Docker healthcheck for backend | S | Not Started | REQ-002 |
| REQ-073 | Documentation | README with setup instructions | Clear instructions for docker compose up | S | Not Started | REQ-007 |
| REQ-074 | Documentation | API documentation | OpenAPI docs accessible at /docs | S | Not Started | REQ-002 |
| REQ-075 | Polish | Frontend - favicon and meta tags | Custom favicon, proper title/description | S | Not Started | REQ-005 |

---

## 3. Component Interface Specifications

### 3.1 Backend API Contract

#### POST /api/audit

**Request:**
```json
{
  "package_name": "lodash"
}
```

**Response (Success - 200 OK):**
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
    "forks": 7000,
    "archived": false
  },
  "timestamp": "2025-12-10T15:30:00Z",
  "audit_duration_ms": 1250
}
```

**Response (Error - 404 Not Found):**
```json
{
  "error": "package_not_found",
  "message": "Package 'nonexistent-pkg' not found on npm",
  "status_code": 404
}
```

**Response (Error - 422 Validation Error):**
```json
{
  "error": "validation_error",
  "message": "Invalid package name format",
  "details": [
    {
      "field": "package_name",
      "message": "Package name cannot be empty"
    }
  ],
  "status_code": 422
}
```

**Response (Error - 500 Internal Server Error):**
```json
{
  "error": "internal_error",
  "message": "Failed to complete audit",
  "status_code": 500
}
```

#### GET /api/health

**Response (200 OK):**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-12-10T15:30:00Z"
}
```

### 3.2 Backend Service Interfaces

#### npm_client.py

```python
async def fetch_package_metadata(
    client: httpx.AsyncClient,
    package_name: str
) -> dict:
    """
    Fetch package metadata from npm registry.

    Args:
        client: HTTP client instance
        package_name: Package name (supports @scope/package)

    Returns:
        Package JSON data from registry

    Raises:
        PackageNotFoundError: Package doesn't exist
        RegistryError: npm registry unavailable
    """

async def fetch_download_stats(
    client: httpx.AsyncClient,
    package_name: str
) -> dict:
    """
    Fetch download statistics from npm API.

    Returns:
        {"downloads": 1234567, "period": "last-week"}
    """
```

#### github_client.py

```python
async def fetch_repository_data(
    client: httpx.AsyncClient,
    repo_url: str,
    token: Optional[str] = None
) -> dict:
    """
    Fetch GitHub repository metadata.

    Returns:
        {
            "stars": 58000,
            "forks": 7000,
            "archived": false,
            "updated_at": "2024-01-15T10:30:00Z"
        }

    Raises:
        RateLimitError: GitHub rate limit exceeded
        RepositoryNotFoundError: Repo doesn't exist
    """

async def fetch_security_advisories(
    client: httpx.AsyncClient,
    package_name: str
) -> list[dict]:
    """
    Fetch security advisories from GitHub Advisory Database.

    Returns:
        List of advisories with severity, description, patched versions
    """
```

#### analyzer.py

```python
def analyze_typosquatting(
    package_name: str,
    popular_packages: list[str]
) -> list[RiskFactor]:
    """
    Check if package name is similar to popular packages.

    Returns:
        List of risk factors (empty if no match)
    """

def analyze_install_scripts(
    package_data: dict
) -> list[RiskFactor]:
    """
    Analyze package.json scripts for dangerous patterns.

    Checks:
        - preinstall/postinstall hooks exist
        - Dangerous commands (curl, wget, eval, bash)
    """

def analyze_package_age(
    created_date: str
) -> list[RiskFactor]:
    """
    Analyze package age and flag very new packages.

    <7 days: Critical
    <30 days: High
    <90 days: Medium
    """

def analyze_maintainers(
    maintainers: list[dict],
    package_age_days: int
) -> list[RiskFactor]:
    """
    Analyze maintainer count and recent changes.

    Checks:
        - No maintainers: Critical
        - Single maintainer: Low
        - Recent changes on old package: High
    """

def analyze_repository(
    package_repo: str,
    github_data: Optional[dict]
) -> list[RiskFactor]:
    """
    Verify repository exists, is active, name matches.
    """

def analyze_downloads(
    weekly_downloads: int,
    age_days: int
) -> list[RiskFactor]:
    """
    Check for suspicious download patterns.

    New package with high downloads: High risk
    Old package with very low downloads: Info
    """

def analyze_vulnerabilities(
    advisories: list[dict]
) -> list[RiskFactor]:
    """
    Parse known vulnerabilities into findings.

    Critical CVE: Critical
    High CVE: High
    etc.
    """
```

#### scoring.py

```python
def calculate_risk_score(factors: list[RiskFactor]) -> int:
    """
    Calculate overall risk score (0-100).

    Severity weights:
        Critical: 25 points
        High: 15 points
        Medium: 8 points
        Low: 3 points
        Info: 0 points

    Score is capped at 100.
    """

def get_risk_level(score: int) -> str:
    """
    Map score to risk level.

    76-100: critical
    51-75: high
    26-50: medium
    0-25: low
    """

def calculate_radar_scores(factors: list[RiskFactor]) -> dict:
    """
    Calculate category-specific scores for radar chart.

    Returns:
        {
            "authenticity": 95,
            "maintenance": 70,
            "security": 90,
            "reputation": 98
        }

    Each category starts at 100, deductions based on findings.
    """
```

### 3.3 Frontend Component Interfaces

#### SearchBar.jsx

```jsx
function SearchBar({ onSubmit, loading }) {
  /**
   * Package name input with audit button.
   *
   * Props:
   *   onSubmit: (packageName: string) => void
   *   loading: boolean
   */
}
```

#### RiskScore.jsx

```jsx
function RiskScore({ score, level }) {
  /**
   * Large risk score display with severity styling.
   *
   * Props:
   *   score: number (0-100)
   *   level: "low" | "medium" | "high" | "critical"
   *
   * Features:
   *   - Count-up animation from 0 to score
   *   - Color changes based on level
   *   - Progress bar visualization
   */
}
```

#### RiskRadar.jsx

```jsx
function RiskRadar({ scores }) {
  /**
   * Radar chart showing category scores.
   *
   * Props:
   *   scores: {
   *     authenticity: number,
   *     maintenance: number,
   *     security: number,
   *     reputation: number
   *   }
   *
   * Uses Recharts RadarChart component.
   */
}
```

#### FindingsList.jsx

```jsx
function FindingsList({ findings }) {
  /**
   * List of security findings with severity badges.
   *
   * Props:
   *   findings: Array<{
   *     name: string,
   *     severity: string,
   *     description: string,
   *     details?: string,
   *     category: string
   *   }>
   *
   * Features:
   *   - Staggered fade-in animation
   *   - Expandable details
   *   - Grouped by severity
   */
}
```

#### MetadataCard.jsx

```jsx
function MetadataCard({ metadata, repoVerification }) {
  /**
   * Package metadata display card.
   *
   * Props:
   *   metadata: {
   *     description: string,
   *     author: string,
   *     license: string,
   *     repository: string,
   *     created: string,
   *     modified: string,
   *     maintainers: string[],
   *     downloads_weekly: number,
   *     versions_count: number
   *   }
   *   repoVerification: {
   *     exists: boolean,
   *     verified: boolean,
   *     stars: number,
   *     forks: number
   *   }
   */
}
```

#### useAudit.js

```javascript
function useAudit() {
  /**
   * Custom hook for audit API interaction.
   *
   * Returns:
   *   {
   *     loading: boolean,
   *     result: AuditResponse | null,
   *     error: string | null,
   *     auditPackage: (packageName: string) => Promise<void>,
   *     reset: () => void
   *   }
   */
}
```

---

## 4. Risk Analysis

### 4.1 External API Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **GitHub Rate Limit Exhaustion** | High | High | TTL cache (1hr), graceful degradation, optional token support |
| **npm Registry Downtime** | Low | High | 5s timeout, cached results, clear error messages |
| **GitHub Advisory DB Slow** | Medium | Medium | Parallel requests, timeout, continue without advisories |
| **Invalid Package Names** | High | Low | Input validation, sanitization, clear error messages |
| **Network Timeouts** | Medium | Medium | Per-request timeouts (5s), total timeout (10s) |

### 4.2 Security Considerations

| Concern | Risk | Mitigation |
|---------|------|------------|
| **XSS via Package Names** | Medium | Input sanitization, React auto-escaping |
| **Server-Side Request Forgery (SSRF)** | Low | Validate GitHub URLs, allowlist domains |
| **Denial of Service (DoS)** | Medium | Rate limiting, timeout all requests |
| **Injection Attacks** | Low | Pydantic validation, parameterized queries |
| **Secrets in Logs** | Low | Never log API tokens, sanitize error messages |

### 4.3 Performance Risks

| Concern | Target | Mitigation |
|---------|--------|------------|
| **Slow API Responses** | <5s audit time | Parallel requests, aggressive timeouts |
| **Memory Leaks** | Stable over 1000 requests | Proper async cleanup, bounded caches |
| **Large Responses** | <1MB per audit | Limit advisory count, paginate if needed |
| **Cold Start Delay** | <2s first request | Optimize Docker image, pre-import modules |

---

## 5. Testing Strategy

### 5.1 Unit Test Coverage

**Backend (Target: 80%+ coverage)**

```python
# tests/test_npm_client.py
async def test_fetch_package_metadata_success()
async def test_fetch_package_metadata_not_found()
async def test_fetch_package_metadata_timeout()
async def test_fetch_scoped_package()

# tests/test_github_client.py
async def test_fetch_repository_data_success()
async def test_fetch_repository_rate_limited()
async def test_fetch_repository_cached()

# tests/test_analyzer.py
def test_typosquatting_detection_lodahs()
def test_typosquatting_no_match()
def test_install_scripts_dangerous_commands()
def test_install_scripts_safe()
def test_package_age_critical()
def test_package_age_safe()
def test_maintainer_single()
def test_maintainer_none()

# tests/test_scoring.py
def test_risk_score_calculation()
def test_risk_score_capped_at_100()
def test_risk_level_thresholds()
def test_radar_scores_deduction()
```

**Frontend (Target: 60%+ coverage)**

```javascript
// tests/SearchBar.test.jsx
test('submits package name on button click')
test('validates empty input')
test('disables button while loading')

// tests/RiskScore.test.jsx
test('displays correct severity color')
test('animates count-up')

// tests/useAudit.test.js
test('fetches audit data successfully')
test('handles API errors')
test('sets loading state correctly')
```

### 5.2 Integration Tests

```python
# tests/integration/test_audit_flow.py
async def test_audit_lodash_complete_flow():
    """Test complete audit with real npm registry."""

async def test_audit_with_github_rate_limit():
    """Mock GitHub to return 403, verify graceful degradation."""

async def test_audit_with_network_failure():
    """Mock all APIs to fail, verify partial results."""
```

### 5.3 E2E Test Scenarios

| Scenario | Package | Expected Outcome |
|----------|---------|------------------|
| **Legitimate Package** | `lodash` | Low risk (0-25), no critical findings |
| **Typosquat Detection** | `lodahs` | High risk, "Similar to lodash" finding |
| **Install Scripts** | `node-ipc@10.1.0` | Medium/High risk, install script warning |
| **Very New Package** | Package <7 days old | High risk, "Very new package" finding |
| **Nonexistent Package** | `zzz-nonexistent-9999` | 404 error, clear message |
| **Scoped Package** | `@babel/core` | Low risk, proper parsing |
| **GitHub Rate Limited** | Any package (mocked) | Degraded response, missing repo data |

### 5.4 Test Data

**Known Packages for Testing:**

```python
TEST_PACKAGES = {
    "legitimate": ["lodash", "express", "react", "@types/node"],
    "typosquats": ["lodahs", "expresss", "recat"],
    "with_scripts": ["node-ipc@10.1.0"],
    "vulnerabilities": ["ua-parser-js@0.7.28"],  # Historical vuln
    "nonexistent": ["zzz-nonexistent-test-pkg-9999"]
}
```

### 5.5 Test Automation

```bash
# Backend tests
cd backend
pytest tests/ --cov=. --cov-report=html

# Frontend tests
cd frontend
npm test -- --coverage

# Integration tests (requires Docker)
docker compose up -d
pytest tests/integration/
docker compose down

# E2E tests
docker compose up -d
npm run test:e2e
docker compose down
```

---

## 6. Implementation Strategy

### 6.1 Phase 1: Foundation (Requirements REQ-001 to REQ-007)

**Goal:** Both services running in Docker Compose

1. Backend skeleton with health endpoint
2. Frontend skeleton with Vite + Tailwind
3. Docker Compose orchestration

**Completion Criteria:**
- `docker compose up` starts both services
- Backend /api/health returns 200
- Frontend displays "Hello World"

### 6.2 Phase 2: Backend Core (REQ-008 to REQ-035)

**Goal:** Complete audit logic without frontend integration

1. npm client with error handling
2. GitHub client with caching
3. All analyzers with unit tests
4. Scoring engine with validation

**Completion Criteria:**
- All unit tests pass
- Manual API test with curl returns valid JSON
- Known-bad packages detected correctly

### 6.3 Phase 3: Backend Integration (REQ-036 to REQ-041)

**Goal:** Complete audit endpoint working end-to-end

1. Audit orchestrator with parallel API calls
2. Graceful degradation logic
3. Response assembly
4. Integration tests

**Completion Criteria:**
- POST /api/audit with "lodash" returns complete response
- Integration tests pass with mocked APIs
- Error scenarios handled gracefully

### 6.4 Phase 4: Frontend Components (REQ-042 to REQ-054)

**Goal:** All UI components functional

1. SearchBar with API integration
2. RiskScore with animation
3. RiskRadar with Recharts
4. FindingsList with styling
5. MetadataCard with verification icons

**Completion Criteria:**
- All components render with mock data
- Animations work smoothly
- Responsive layout functions

### 6.5 Phase 5: Frontend Integration (REQ-055 to REQ-059)

**Goal:** Complete user flow working

1. Main layout with all components
2. useAudit hook wired up
3. Loading and error states
4. Terminal aesthetic applied

**Completion Criteria:**
- Search → Loading → Results flow works
- Error handling displays correctly
- Mobile responsive layout verified

### 6.6 Phase 6: Testing & Polish (REQ-060 to REQ-075)

**Goal:** Production-ready application

1. Complete test suite
2. E2E tests with known packages
3. Documentation
4. Performance validation

**Completion Criteria:**
- All tests pass
- Audit completes in <5s
- README has clear setup instructions
- Docker images build successfully

---

## 7. Development Workflow (TDD Process)

### 7.1 Red-Green-Refactor Cycle

For each requirement:

1. **Write Failing Test (RED)**
   ```bash
   # Example: REQ-020 Typosquatting detection
   def test_typosquatting_lodahs():
       result = check_typosquatting("lodahs")
       assert any(match[0] == "lodash" for match in result)

   # Run: pytest - Test FAILS (not implemented)
   ```

2. **Write Minimal Code (GREEN)**
   ```python
   def check_typosquatting(package_name):
       popular = ["lodash", "express", "react"]
       from difflib import SequenceMatcher

       matches = []
       for pkg in popular:
           ratio = SequenceMatcher(None, package_name, pkg).ratio()
           if ratio > 0.8 and package_name != pkg:
               matches.append((pkg, ratio))
       return matches

   # Run: pytest - Test PASSES
   ```

3. **Refactor (REFACTOR)**
   ```python
   # Extract to service, add type hints, optimize
   from typing import List, Tuple
   from difflib import SequenceMatcher

   POPULAR_PACKAGES = ["lodash", "express", "react", ...]
   SIMILARITY_THRESHOLD = 0.8

   def check_typosquatting(
       package_name: str,
       threshold: float = SIMILARITY_THRESHOLD
   ) -> List[Tuple[str, float]]:
       """Check if package name is similar to popular packages."""
       matches = []
       normalized = package_name.lower().replace("_", "-")

       for pkg in POPULAR_PACKAGES:
           ratio = SequenceMatcher(None, normalized, pkg).ratio()
           if ratio > threshold and normalized != pkg:
               matches.append((pkg, ratio))

       return sorted(matches, key=lambda x: x[1], reverse=True)

   # Run: pytest - Tests still PASS
   ```

4. **Commit Immediately**
   ```bash
   git add tests/test_typosquat.py services/typosquat.py
   git commit -m "feat(analyzer): implement typosquatting detection

   - Add SequenceMatcher-based similarity check
   - Test with lodahs -> lodash example
   - Threshold set to 0.8 for accuracy

   Implements REQ-020"
   ```

### 7.2 Test Categories by Phase

**Unit Tests (Write First):**
- Pure functions (analyzers, scoring)
- Utility functions (URL parsing, validation)
- Data transformations

**Integration Tests (Write During):**
- API clients with mocked responses
- Endpoint handlers with test client
- Cache behavior

**E2E Tests (Write Last):**
- Complete audit flow
- Error scenarios
- Performance validation

---

## 8. Definition of Done

A requirement is considered complete when:

1. ✅ **Code Implemented** - Feature works as specified
2. ✅ **Tests Pass** - All new tests green, no regressions
3. ✅ **Test Coverage** - New code has >80% coverage (backend), >60% (frontend)
4. ✅ **Code Review** - Self-review for clarity and style
5. ✅ **Documentation** - Docstrings, type hints, comments where needed
6. ✅ **Committed** - Clean commit message following conventional commits
7. ✅ **Integration Verified** - Works with dependent components

For infrastructure requirements (Docker, etc.):

1. ✅ **Builds Successfully** - No errors during build
2. ✅ **Runs Locally** - Verified on clean system
3. ✅ **Documentation** - Setup steps documented

---

## 9. Open Questions & Decisions Needed

### 9.1 Pending Decisions

| Question | Options | Decision Owner | Target Date |
|----------|---------|----------------|-------------|
| Include Snyk API integration? | Yes (needs key) / No (keep simple) | Tech Lead | Before REQ-030 |
| Support package version specification? | Yes (@1.2.3) / No (latest only) | Product | Before REQ-008 |
| Add report export (PDF/JSON)? | Yes / No (out of scope) | Product | Before REQ-075 |

### 9.2 Assumptions

1. **GitHub API is primary blocker** - Caching is critical due to 60/hr limit
2. **Most packages are benign** - Focus on clear presentation, not just detection
3. **Judges will test with known packages** - Include test scenarios in README
4. **No authentication required** - Tool is fully public
5. **Single-threaded usage** - No concurrent user load considerations

---

## 10. Success Metrics

### 10.1 Functional Metrics

- ✅ Detect all historical attack packages in test suite
- ✅ Audit completes in <5s for 90% of packages
- ✅ Zero false positives on top 20 npm packages
- ✅ Graceful degradation when GitHub rate-limited

### 10.2 Quality Metrics

- ✅ Backend test coverage >80%
- ✅ Frontend test coverage >60%
- ✅ Zero critical security vulnerabilities in dependencies
- ✅ All Docker images build successfully on amd64 + arm64

### 10.3 Usability Metrics

- ✅ Deploy from zero to running in <5 minutes
- ✅ Clear error messages for all failure modes
- ✅ Responsive UI works on mobile (320px width)
- ✅ Accessible to screen readers (WCAG 2.1 AA)

---

## 11. Out of Scope (Future Enhancements)

The following are explicitly NOT included in v1:

1. **Multi-Ecosystem Support** - PyPI, Maven, RubyGems (future ADR required)
2. **Dependency Tree Scanning** - Recursive analysis of transitive dependencies
3. **CI/CD Integration** - GitHub Action, CLI tool
4. **Historical Tracking** - Compare risk over time
5. **User Accounts** - No authentication or personalization
6. **API Rate Limit Dashboard** - No visibility into remaining GitHub quota
7. **SBOM Generation** - CycloneDX/SPDX output
8. **Custom Risk Policies** - Users cannot adjust severity weights
9. **Bulk Package Scanning** - One package at a time only
10. **Real-Time Monitoring** - No webhook notifications or continuous scanning

---

## 12. Maintenance Plan

### 12.1 Dependency Updates

- **Monthly:** Update npm dependencies (frontend)
- **Monthly:** Update Python dependencies (backend)
- **Quarterly:** Review popular packages list for typosquatting detection
- **As Needed:** Update Docker base images for security patches

### 12.2 Monitoring

- Docker healthcheck monitors backend availability
- Manual testing with known packages after updates
- Track GitHub rate limit consumption in logs

### 12.3 Known Technical Debt

| Item | Impact | Remediation Plan |
|------|--------|------------------|
| In-memory cache lost on restart | Low | Migrate to Redis in v2 |
| No request rate limiting | Low | Add rate limiter for production use |
| Manual popular packages list | Medium | Fetch from npm API weekly |
| No GitHub token rotation | Low | Support multiple tokens if needed |

---

## Appendix A: Popular Packages List (Typosquatting)

Initial list of 50 packages (expand to 100+):

```python
POPULAR_PACKAGES = [
    # Top downloads
    "lodash", "react", "react-dom", "express", "axios", "typescript",
    "webpack", "next", "vue", "angular", "moment", "jquery",

    # Common typosquat targets
    "eslint", "babel", "prettier", "jest", "mocha", "chai",
    "request", "commander", "chalk", "debug", "async", "bluebird",

    # Framework ecosystems
    "@angular/core", "@babel/core", "@types/node", "@types/react",

    # Security-sensitive
    "dotenv", "jsonwebtoken", "bcrypt", "passport", "helmet",

    # Build tools
    "vite", "rollup", "esbuild", "parcel", "gulp", "grunt",

    # Historical attack targets
    "event-stream", "ua-parser-js", "colors", "faker", "node-ipc"
]
```

---

## Appendix B: Dangerous Command Patterns

```python
DANGEROUS_COMMANDS = [
    # Network operations
    "curl", "wget", "nc ", "netcat", "telnet",

    # Shell execution
    "bash -c", "/bin/sh", "/bin/bash", "sh -c",
    "eval(", "eval ", "exec(", "exec ",

    # Encoding/obfuscation
    "base64", "base32", "rot13", "atob", "btoa",

    # Windows shells
    "powershell", "cmd.exe", "cmd /c",

    # Destructive operations
    "rm -rf", "del /f", "format ", "> /dev/", "| /dev/",

    # Persistence
    "crontab", "systemctl", "launchctl", "at ", "schtasks",

    # Data exfiltration
    "ftp", "scp", "sftp", "rsync", "dd if=", "tar czf"
]

DANGEROUS_SCRIPTS = [
    "preinstall",
    "postinstall",
    "preuninstall",
    "postuninstall"
]
```

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-12-10 | Technical Lead | Initial SRS with 75 requirements |

---

**Document Status:** Active Development
**Next Review:** After Phase 2 completion
**Contact:** Technical Lead, Repojacker Project
