# PARANOID - SBOM Roast Generator

Paste your dependencies. Get roasted. Question everything.

PARANOID analyzes your software dependencies and roasts your questionable life choices with AI-generated memes. It detects CVEs, identifies cursed packages, and generates personalized security roasts.

## Features

- **CVE Detection** - Scans for 55+ famous vulnerabilities (Log4Shell, Heartbleed, etc.)
- **Cursed Package Detection** - Identifies 11 infamous packages (left-pad, event-stream, colors, etc.)
- **AI-Powered Roasts** - Claude Haiku generates personalized security burns
- **Meme Generation** - Creates custom memes via memegen.link API
- **Paranoia System** - Escalating distrust based on your dependency choices
- **Multi-Format Support** - package.json, requirements.txt, go.mod, SBOM (CycloneDX/SPDX)

## Security

- **0 CVEs** - Built on Chainguard Wolfi base image
- **Non-root execution** - Runs as UID 65532
- **Security headers** - CSP, X-Frame-Options, X-Content-Type-Options
- **SSRF protection** - URL whitelist, content-type validation, size limits
- **Rate limiting** - 10 requests/minute per IP
- **Input validation** - 100KB max, 500 dependencies max

## Quick Start

```bash
# Build
docker build -t paranoid .

# Run (with AI roasts)
docker run -p 8000:8000 -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY paranoid

# Run (without AI - uses pre-written captions)
docker run -p 8000:8000 paranoid
```

Then visit http://localhost:8000

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Frontend UI |
| `/healthz` | GET | Health check with neurotic messages |
| `/roast` | POST | Analyze dependencies and get roasted |

### POST /roast

```bash
curl -X POST http://localhost:8000/roast \
  -H "Content-Type: application/json" \
  -d '{
    "input_type": "requirements_txt",
    "content": "flask==2.0.0\nrequests==2.25.0",
    "include_sbom": true,
    "use_ai": true
  }'
```

**Input Types:** `package_json`, `requirements_txt`, `go_mod`, `sbom`, `single_package`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | - | Claude API key for AI roasts |
| `ALLOWED_ORIGINS` | `localhost` | CORS allowed origins |
| `MAX_INPUT_SIZE` | `102400` | Max input size (bytes) |
| `MAX_DEPENDENCIES` | `500` | Max dependencies per request |
| `RATE_LIMIT_PER_MINUTE` | `10` | Rate limit per IP |

## Tech Stack

- **Backend:** Python 3.12, FastAPI, Pydantic
- **AI:** Claude 3 Haiku via Anthropic API
- **Memes:** memegen.link API + Pillow
- **Container:** Chainguard Wolfi (zero CVEs)

## Container

```
ghcr.io/chanfi0ne/vibelympics/paranoid:latest
```

## Live Demo

https://chainsaw.up.railway.app

---

*Trust no dependency. Question every import. PARANOID is watching.*
