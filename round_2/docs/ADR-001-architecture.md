# ADR-001: Core Architecture and Technology Stack

**Status:** Accepted
**Date:** 2025-12-10
**Decision Makers:** Technical Lead
**Context:** Repojacker npm supply chain security auditor initial architecture

---

## Context and Problem Statement

Repojacker needs to audit npm packages for supply chain security risks by analyzing data from multiple external APIs (npm Registry, GitHub, advisory databases) and presenting results through an intuitive web interface. The system must:

- Complete audits in under 5 seconds
- Handle concurrent API calls efficiently
- Gracefully degrade when external APIs fail
- Be deployable with a single command
- Support future extensibility (PyPI, Maven, etc.)

Key constraints:
- GitHub API rate limit: 60 requests/hour (unauthenticated)
- Must use containerized deployment
- Public APIs only (no API keys required for basic function)
- Competition timeline: ~4 hours total development time

---

## Decision Drivers

1. **Performance** - Concurrent API calls, fast response times
2. **Developer Velocity** - Rapid development within competition timeline
3. **Type Safety** - Reduce runtime errors, especially at API boundaries
4. **Deployability** - Single-command startup for judges
5. **Maintainability** - Clear separation of concerns, testable code
6. **Extensibility** - Easy to add new security signals or ecosystems

---

## Decision 1: FastAPI (Python 3.12) for Backend

### Options Considered

**Option A: FastAPI (Python)**
- Pros: Native async support, excellent performance, automatic OpenAPI docs, Pydantic validation, rapid development
- Cons: Dynamic typing (mitigated by Pydantic), less mature than Flask

**Option B: Express.js (Node.js)**
- Pros: JavaScript everywhere, large ecosystem, familiar to npm developers
- Cons: Callback hell without careful async/await usage, weaker type safety even with TypeScript

**Option C: Go + Gin**
- Pros: Excellent performance, strong typing, compiled binary
- Cons: More verbose, slower development, less familiar for rapid prototyping

### Decision: **FastAPI (Python 3.12)**

**Rationale:**
1. **Async First-Class** - Native async/await for concurrent API calls without complexity
2. **Pydantic Models** - Request/response validation catches errors at API boundary
3. **Speed of Development** - Clear, readable code enables rapid iteration in competition timeline
4. **Built-in OpenAPI** - Automatic API documentation for judges to explore endpoints
5. **Rich Ecosystem** - httpx for async HTTP, extensive security libraries

**Implementation Details:**
```python
# Clear service separation
services/
├── npm_client.py      # Isolated npm API logic
├── github_client.py   # GitHub API with rate limit handling
├── analyzer.py        # Pure analysis logic (no I/O)
└── scoring.py         # Scoring algorithm (unit testable)
```

**Trade-offs Accepted:**
- Python's dynamic nature (mitigated by comprehensive type hints + Pydantic)
- Slightly larger Docker image than Go (acceptable for single-service deployment)

---

## Decision 2: httpx for Async HTTP Client

### Options Considered

**Option A: httpx**
- Pros: Modern async/await API, timeout handling, connection pooling, drop-in replacement for requests
- Cons: Less mature than requests, smaller community

**Option B: aiohttp**
- Pros: Mature async library, widely used
- Cons: More complex API, manual session management, verbose error handling

**Option C: requests + asyncio.to_thread**
- Pros: Familiar requests API
- Cons: Not truly async, thread overhead, poor performance under load

### Decision: **httpx**

**Rationale:**
1. **Clean Async API** - `async with httpx.AsyncClient()` is intuitive and safe
2. **Automatic Timeouts** - Built-in timeout handling prevents hanging requests
3. **Connection Pooling** - Efficient reuse of connections to npm/GitHub
4. **Requests-like API** - Familiar interface reduces learning curve

**Implementation Pattern:**
```python
async def fetch_package(client: httpx.AsyncClient, package_name: str):
    response = await client.get(
        f"https://registry.npmjs.org/{package_name}",
        timeout=5.0
    )
    return response.json()

# Concurrent API calls
async with httpx.AsyncClient() as client:
    npm_data, github_data, advisory_data = await asyncio.gather(
        fetch_package(client, package_name),
        fetch_github(client, repo_url),
        fetch_advisories(client, package_name),
        return_exceptions=True  # Graceful degradation
    )
```

---

## Decision 3: React 18 + Vite for Frontend

### Options Considered

**Option A: React 18 + Vite**
- Pros: Component reusability, fast HMR, excellent dev experience, large ecosystem
- Cons: Client-side only, bundle size

**Option B: Next.js**
- Pros: SSR/SSG, built-in routing, API routes
- Cons: Overkill for single-page app, slower dev server, more complexity

**Option C: Svelte + SvelteKit**
- Pros: Smaller bundle, less boilerplate
- Cons: Smaller ecosystem, less familiar for most developers

### Decision: **React 18 + Vite**

**Rationale:**
1. **Vite Performance** - Sub-second HMR enables rapid UI iteration
2. **Component Model** - Natural mapping to design (RiskScore, RiskRadar, FindingsList)
3. **Recharts Integration** - Excellent radar chart library for React
4. **Developer Familiarity** - Widely known, easy for others to contribute
5. **Tailwind Compatibility** - Utility-first CSS matches "terminal" aesthetic

**Build Strategy:**
- Vite optimizes for production with tree-shaking and code splitting
- nginx serves static assets in production
- API proxy in development, direct calls in production

---

## Decision 4: State Management - React Hooks (No Redux)

### Options Considered

**Option A: React Hooks only (useState, useEffect)**
- Pros: Zero dependencies, simple for single-page app, fast to implement
- Cons: Prop drilling if deeply nested (not an issue here)

**Option B: Redux Toolkit**
- Pros: Centralized state, devtools, time-travel debugging
- Cons: Massive overkill for audit results that don't persist

**Option C: Zustand**
- Pros: Minimal boilerplate, TypeScript-friendly
- Cons: Unnecessary abstraction for simple state

### Decision: **React Hooks Only**

**Rationale:**
1. **Simple State Model** - Only need: `loading`, `auditResult`, `error`
2. **Single Data Flow** - User submits package → API call → Display results
3. **No Persistence** - Results don't need to persist across page reloads
4. **Zero Dependencies** - Fewer things to break

**Implementation:**
```javascript
// Custom hook encapsulates all audit logic
function useAudit() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const auditPackage = async (packageName) => {
    setLoading(true);
    try {
      const response = await fetch('/api/audit', {
        method: 'POST',
        body: JSON.stringify({ package_name: packageName })
      });
      setResult(await response.json());
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return { loading, result, error, auditPackage };
}
```

---

## Decision 5: Caching Strategy - In-Memory LRU Cache

### Options Considered

**Option A: In-Memory LRU Cache (Python functools.lru_cache)**
- Pros: Zero dependencies, fast, automatic eviction
- Cons: Lost on restart, no sharing across instances

**Option B: Redis**
- Pros: Persistent, shared cache, TTL support
- Cons: Extra infrastructure, deployment complexity, overkill for competition

**Option C: No Caching**
- Pros: Simplest
- Cons: Wastes API rate limits, slow for repeated queries

### Decision: **In-Memory LRU Cache**

**Rationale:**
1. **GitHub Rate Limit Management** - 60/hour is tight; caching prevents waste
2. **Zero Infrastructure** - No additional containers or configuration
3. **Good Enough** - For competition/demo, in-memory is sufficient
4. **Easy Upgrade Path** - Can swap for Redis later without API changes

**Implementation:**
```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=100)
async def fetch_github_repo(repo_url: str) -> dict:
    """Cached for 1 hour (cache cleared manually if needed)"""
    async with httpx.AsyncClient() as client:
        response = await client.get(api_url, timeout=5.0)
        return response.json()

# Manual cache with TTL for more control
from datetime import datetime, timedelta

class TTLCache:
    def __init__(self, ttl_seconds: int):
        self._cache = {}
        self._ttl = timedelta(seconds=ttl_seconds)

    def get(self, key: str):
        if key in self._cache:
            value, timestamp = self._cache[key]
            if datetime.now() - timestamp < self._ttl:
                return value
        return None

    def set(self, key: str, value):
        self._cache[key] = (value, datetime.now())

# GitHub calls cached for 1 hour, npm registry for 5 minutes
github_cache = TTLCache(ttl_seconds=3600)
npm_cache = TTLCache(ttl_seconds=300)
```

---

## Decision 6: Error Handling Pattern - Graceful Degradation

### Options Considered

**Option A: Fail Fast (raise exception if any API fails)**
- Pros: Clear failures
- Cons: User gets no results if GitHub is down

**Option B: Graceful Degradation (continue with partial data)**
- Pros: Better UX, some results better than none
- Cons: More complex error handling

**Option C: Retry with Exponential Backoff**
- Pros: Resilient to transient failures
- Cons: Slows down responses, wastes rate limits

### Decision: **Graceful Degradation**

**Rationale:**
1. **User Experience** - Show what we CAN determine even if one API fails
2. **Rate Limit Preservation** - Don't waste retries on known-down services
3. **Clear Communication** - Report which checks failed and why

**Implementation:**
```python
# Use asyncio.gather with return_exceptions=True
async def audit_package(package_name: str) -> AuditResponse:
    async with httpx.AsyncClient() as client:
        # All API calls in parallel
        results = await asyncio.gather(
            fetch_npm_registry(client, package_name),
            fetch_npm_downloads(client, package_name),
            fetch_github_repo(client, package_name),
            fetch_github_advisories(client, package_name),
            return_exceptions=True  # Don't fail if one raises
        )

        npm_data, downloads, github_data, advisories = results

        # Build findings from successful results
        findings = []

        if isinstance(npm_data, Exception):
            findings.append(RiskFactor(
                name="Registry Check Failed",
                severity="info",
                description=f"Could not fetch npm data: {npm_data}",
                category="maintenance"
            ))
        else:
            findings.extend(analyze_npm_data(npm_data))

        # Continue with available data
        return build_response(findings, partial_data=True)
```

---

## Decision 7: TailwindCSS for Styling

### Options Considered

**Option A: TailwindCSS**
- Pros: Utility-first matches "terminal" aesthetic, fast iteration, consistent spacing
- Cons: Verbose JSX, learning curve

**Option B: CSS Modules**
- Pros: Scoped styles, familiar CSS
- Cons: More files, harder to maintain design system

**Option C: Styled Components**
- Pros: CSS-in-JS, dynamic styling
- Cons: Runtime overhead, verbose, harder to match design system

### Decision: **TailwindCSS**

**Rationale:**
1. **Design System Enforcement** - Custom theme maps directly to style guide colors/spacing
2. **Rapid Iteration** - No context switching between CSS files
3. **Perfect for "Terminal" Aesthetic** - Utility classes match precise spacing requirements
4. **PurgeCSS Integration** - Vite automatically removes unused styles

**Configuration:**
```javascript
// tailwind.config.js - Implements style guide exactly
module.exports = {
  theme: {
    extend: {
      colors: {
        bg: {
          void: '#050508',
          primary: '#0a0a0f',
          secondary: '#0f0f18',
          card: '#14141f',
        },
        accent: {
          primary: '#00fff2',
          glow: '#00fff240',
        },
        severity: {
          critical: '#ff0040',
          high: '#ff6b00',
          medium: '#ffd000',
          low: '#00ff88',
          info: '#00b4ff',
        },
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
        display: ['Orbitron', 'sans-serif'],
      },
    },
  },
};
```

---

## Consequences

### Positive

1. **Fast Development** - Tech stack chosen for rapid iteration in competition timeline
2. **Clear Architecture** - Service separation enables parallel development and testing
3. **Type Safety** - Pydantic models catch errors at API boundaries
4. **Testability** - Pure functions (analyzer, scoring) are easily unit tested
5. **Performance** - Async architecture supports concurrent API calls
6. **Graceful Degradation** - Users get results even when external APIs fail
7. **Single Command Deploy** - Docker Compose encapsulates everything

### Negative

1. **Python Runtime** - Larger Docker image than compiled languages
2. **Rate Limit Challenges** - GitHub's 60/hour requires careful caching strategy
3. **Client-Side Only** - No SSR means slower initial render (acceptable for tool)
4. **In-Memory Cache** - Lost on restart, no cross-instance sharing (acceptable for v1)

### Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| GitHub rate limit exhaustion | High | TTL cache (1hr), graceful degradation, clear error messages |
| npm Registry downtime | Medium | Timeout quickly, show cached results if available |
| Slow API responses | Medium | 5s timeout per request, 10s total timeout, loading states |
| Docker build failures | High | Multi-stage builds, lock file dependencies, test locally |

---

## Validation

This architecture will be validated by:

1. **Integration Tests** - Test complete audit flow with known packages
2. **Rate Limit Tests** - Verify caching prevents redundant GitHub calls
3. **Failure Tests** - Confirm graceful degradation when APIs are mocked to fail
4. **Performance Tests** - Ensure audits complete under 5s for typical packages
5. **Docker Tests** - Verify `docker compose up` starts cleanly on fresh system

---

## Related Decisions

- ADR-002: Risk Scoring Algorithm (future)
- ADR-003: Typosquatting Detection Strategy (future)
- ADR-004: GitHub Rate Limit Management (future)

---

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [httpx Async Client](https://www.python-httpx.org/async/)
- [React 18 Features](https://react.dev/blog/2022/03/29/react-v18)
- [Vite Guide](https://vitejs.dev/guide/)
- [TailwindCSS Docs](https://tailwindcss.com/docs)
- [npm Registry API](https://github.com/npm/registry/blob/master/docs/REGISTRY-API.md)
- [GitHub REST API](https://docs.github.com/en/rest)
