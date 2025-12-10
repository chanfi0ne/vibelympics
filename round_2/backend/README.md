# Repojacker Backend

FastAPI-based backend service for npm supply chain security auditing.

## Structure

```
backend/
├── main.py                 # FastAPI app entry point
├── requirements.txt        # Python dependencies
├── Dockerfile             # Container image definition
├── .dockerignore          # Docker build exclusions
├── routers/
│   ├── __init__.py
│   └── audit.py           # API route handlers
├── services/
│   ├── __init__.py
│   ├── npm_client.py      # npm Registry API client
│   ├── github_client.py   # GitHub API client with caching
│   ├── analyzer.py        # Risk analysis logic
│   └── scoring.py         # Risk score calculation
├── models/
│   ├── __init__.py
│   ├── request.py         # Request validation models
│   └── response.py        # Response serialization models
└── utils/
    ├── __init__.py
    ├── typosquat.py       # Typosquatting detection (100+ popular packages)
    └── patterns.py        # Dangerous command pattern matching
```

## API Endpoints

### GET /api/health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-12-10T15:30:00Z"
}
```

### POST /api/audit
Audit npm package for security risks.

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
  "factors": [...],
  "metadata": {...},
  "radar_scores": {...},
  "repository_verification": {...},
  "timestamp": "2025-12-10T15:30:00Z",
  "audit_duration_ms": 1250
}
```

## Features

### Analysis Capabilities
- **Typosquatting Detection**: Compare against 100+ popular packages using Levenshtein distance
- **Install Script Analysis**: Detect dangerous commands (curl, wget, eval, bash) in lifecycle hooks
- **Package Age Analysis**: Flag packages < 30 days old
- **Maintainer Analysis**: Flag single maintainer or no maintainers
- **Repository Verification**: Check GitHub repo exists, not archived, has activity
- **Download Velocity**: Flag suspicious download spikes
- **Vulnerability Lookup**: GitHub Advisory Database integration

### Scoring Algorithm
- **Critical**: 25 points
- **High**: 15 points
- **Medium**: 8 points
- **Low**: 3 points
- **Info**: 0 points
- **Total**: Capped at 100

### Risk Levels
- **0-25**: low
- **26-50**: medium
- **51-75**: high
- **76-100**: critical

### Radar Scores
Calculate for 4 categories (0-100 each):
- **Authenticity**: Typosquatting, repository verification
- **Maintenance**: Age, maintainer count, repository activity
- **Security**: Vulnerabilities, install scripts, dangerous commands
- **Reputation**: Downloads, stars, community adoption

## Running Locally

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run Development Server
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Run with Docker
```bash
docker build -t repojacker-backend .
docker run -p 8000:8000 repojacker-backend
```

### Environment Variables
- `GITHUB_TOKEN` (optional): GitHub personal access token for higher rate limits

## API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Architecture

### Async Design
All external API calls use `httpx.AsyncClient` with `asyncio.gather` for parallel execution:
- npm Registry metadata
- npm Download stats
- GitHub repository data
- GitHub security advisories

### Graceful Degradation
If external APIs fail (rate limits, timeouts), the service continues with partial data and reports what it couldn't verify.

### Caching Strategy
- **GitHub API**: 1 hour TTL cache (in-memory)
- **npm Registry**: No caching (fast enough)
- Prevents rate limit exhaustion on repeated queries

### Error Handling
- Package not found: HTTP 404
- Validation errors: HTTP 422
- Internal errors: HTTP 500 with details
- All errors include structured JSON responses

## Testing

### Unit Tests
```bash
pytest tests/ -v
```

### Integration Tests
```bash
pytest tests/integration/ -v
```

### Test with curl
```bash
# Health check
curl http://localhost:8000/api/health

# Audit lodash
curl -X POST http://localhost:8000/api/audit \
  -H "Content-Type: application/json" \
  -d '{"package_name": "lodash"}'

# Audit typosquat
curl -X POST http://localhost:8000/api/audit \
  -H "Content-Type: application/json" \
  -d '{"package_name": "lodahs"}'
```

## Dependencies

- **fastapi**: Web framework with async support
- **uvicorn**: ASGI server
- **httpx**: Async HTTP client
- **pydantic**: Data validation and serialization
- **python-dateutil**: Date parsing and manipulation

## Security Considerations

- Input validation on all package names
- Timeouts on all external API calls (5s per request)
- No secrets logged or exposed in error messages
- CORS configured for known frontend origins only
- URL encoding for package names (prevents injection)

## Performance

- Typical audit: < 3 seconds
- Parallel API calls reduce latency
- Caching prevents redundant GitHub API calls
- Connection pooling via httpx
