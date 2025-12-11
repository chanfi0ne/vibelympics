# REPOJACKER

**Detect supply chain threats before they detect you**

Repojacker is a supply chain security analysis tool that audits npm packages for legitimacy, security risks, and potential threats. Given a package name, it generates a comprehensive security-focused audit report with actionable risk scoring.

## Quick Start

```bash
docker compose up --build
```

Then open http://localhost:3000

## Features

### Risk Scoring (0-100)
- **Low (0-25):** Generally safe, minor concerns
- **Medium (26-50):** Caution advised, review findings
- **High (51-75):** Significant risks identified
- **Critical (76-100):** Do not use without thorough review

### Security Signals Analyzed

| Signal | Description |
|--------|-------------|
| **Typosquatting Detection** | Similarity to popular packages (lodahs → lodash) |
| **Package Age** | Flags packages less than 30 days old |
| **Maintainer Analysis** | Single maintainer, no maintainers, recent changes |
| **Install Scripts** | preinstall/postinstall hooks detected |
| **Dangerous Commands** | curl, wget, eval, bash in scripts |
| **Repository Verification** | GitHub repo exists and matches |
| **Download Velocity** | Suspicious download spikes |
| **Dependency Analysis** | Flags excessive dependencies (>50 or >100) |
| **License Analysis** | Missing, restrictive, or copyleft licenses |
| **Known Vulnerabilities** | CVEs from OSV.dev vulnerability database |
| **Sigstore Provenance** | SLSA build attestations via npm Sigstore |

### Visual Risk Radar
Spider chart showing normalized scores across categories:
- **Authenticity** - Is this the real package?
- **Maintenance** - Is it well-maintained?
- **Security** - Are there vulnerabilities?
- **Reputation** - Is it widely trusted?

## Architecture

```
┌──────────────────┐         ┌──────────────────────────────────┐
│  React Frontend  │◄───────►│  FastAPI Backend                 │
│  (nginx:3000)    │  REST   │  (uvicorn:8000)                  │
└──────────────────┘         └──────────────┬───────────────────┘
                                            │
         ┌──────────────┬───────────────────┼───────────────┬──────────────┐
         │              │                   │               │              │
         ▼              ▼                   ▼               ▼              ▼
  ┌─────────────┐ ┌───────────┐    ┌─────────────┐  ┌───────────┐  ┌────────────┐
  │npm Registry │ │ OSV.dev   │    │ GitHub API  │  │npm Sigstore│  │   Rekor    │
  │    API      │ │ (CVEs)    │    │             │  │Attestations│  │Transparency│
  └─────────────┘ └───────────┘    └─────────────┘  └───────────┘  └────────────┘
```

## API

### POST /api/audit
```bash
curl -X POST http://localhost:8000/api/audit \
  -H "Content-Type: application/json" \
  -d '{"package_name": "lodash"}'
```

### GET /api/health
```bash
curl http://localhost:8000/api/health
```

## Test Packages

Try these packages to see different risk levels:

| Package | Expected Risk | Why |
|---------|---------------|-----|
| `lodash` | Low | Established, well-maintained |
| `express` | Low | Popular, multiple maintainers |
| `lodahs` | High | Typosquat of lodash |
| `@babel/core` | Low | Official scoped package |

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GITHUB_TOKEN` | Optional GitHub token for higher rate limits | None |

## Development

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Tech Stack

- **Backend:** Python 3.12, FastAPI, httpx, Pydantic
- **Frontend:** React 18, Vite, TailwindCSS, Recharts
- **Deployment:** Docker, Docker Compose, nginx

## Container Security

Repojacker practices what it preaches. Our containers are built with supply chain security in mind.

### Zero-CVE Base Images

Both containers use [Chainguard](https://chainguard.dev) base images:

| Container | Base Image | CVEs |
|-----------|------------|------|
| Backend | `cgr.dev/chainguard/python` | **0** |
| Frontend | `cgr.dev/chainguard/nginx` | **0** |

### SLSA Provenance

All container builds include SLSA provenance attestations. Verify the supply chain integrity:

```bash
# Verify backend image provenance
gh attestation verify oci://ghcr.io/chanfi0ne/vibelympics/repojacker-backend:latest \
  --owner chanfi0ne

# Verify frontend image provenance
gh attestation verify oci://ghcr.io/chanfi0ne/vibelympics/repojacker-frontend:latest \
  --owner chanfi0ne
```

### Pre-built Images

Pull from GitHub Container Registry:

```bash
docker pull ghcr.io/chanfi0ne/vibelympics/repojacker-backend:latest
docker pull ghcr.io/chanfi0ne/vibelympics/repojacker-frontend:latest
```

## License

MIT
