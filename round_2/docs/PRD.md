# Package Security Auditor - Product Requirements Document

## Executive Summary

**Product Name:** Repojacker  
**Tagline:** "Detect supply chain threats before they detect you"  
**Target Ecosystem:** npm (Node.js/JavaScript)  
**Competition:** Vibelympics Round 2 - Security Tooling Challenge

Repojacker is a supply chain security analysis tool that audits npm packages for legitimacy, security risks, and potential threats. Given a package name, it generates a comprehensive security-focused audit report with actionable risk scoring.

---

## Problem Statement

Software supply chain attacks have exploded in recent years:
- **event-stream (2018):** Malicious code injected via maintainer social engineering
- **ua-parser-js (2021):** Hijacked package delivered crypto miners
- **colors/faker (2022):** Maintainer sabotage wiped enterprise systems
- **node-ipc (2022):** Protestware deleted files based on geolocation

Developers blindly `npm install` packages with no visibility into:
- Is this package legitimate or a typosquat?
- Who maintains it? Have maintainers changed recently?
- Does it have install scripts that execute code?
- Is the linked GitHub repo real and active?
- Are there known vulnerabilities?
- What's the overall risk profile?

---

## Solution

ChainGuard provides instant, comprehensive security analysis of any npm package through:

1. **Risk Scoring** - 0-100 score with clear severity levels
2. **Multi-Signal Analysis** - 12+ security indicators
3. **Visual Risk Radar** - At-a-glance threat visualization
4. **Actionable Findings** - Clear explanations and remediation guidance
5. **Easy Deployment** - Single `docker compose up` to run

---

## Target Users

1. **Security Engineers** - Vetting packages before approval
2. **DevOps/Platform Teams** - Automating dependency checks in CI/CD
3. **Developers** - Quick sanity check before installing
4. **Security Researchers** - Investigating suspicious packages

---

## Core Features

### F1: Package Lookup
- Input: npm package name (e.g., `lodash`, `@babel/core`)
- Support for scoped packages (`@org/package`)
- Validation and sanitization of input

### F2: Risk Score Calculation
- **0-100 numeric score** based on weighted factors
- **Severity Levels:**
  - 🟢 **Low (0-25):** Generally safe, minor concerns
  - 🟡 **Medium (26-50):** Caution advised, review findings
  - 🟠 **High (51-75):** Significant risks identified
  - 🔴 **Critical (76-100):** Do not use without thorough review

### F3: Security Signal Analysis

| Signal | Description | Severity Weight |
|--------|-------------|-----------------|
| **Typosquatting Detection** | Similarity to popular packages | Critical |
| **Package Age** | Days since creation | High |
| **Maintainer Analysis** | Count, recent changes | High |
| **Install Scripts** | preinstall/postinstall hooks | Critical |
| **Dangerous Commands** | curl, wget, eval in scripts | Critical |
| **Repository Verification** | GitHub exists and matches | Medium |
| **Download Velocity** | Weekly downloads vs age | Medium |
| **Dependency Count** | Runtime dependency depth | Low |
| **Known Vulnerabilities** | CVEs from advisory databases | Critical |
| **License Analysis** | Missing or unusual license | Low |
| **Version Entropy** | Suspicious version patterns | Medium |
| **Provenance/Attestation** | npm sigstore verification | Info |

### F4: Detailed Findings Report
Each finding includes:
- **Name:** Brief identifier
- **Severity:** Critical/High/Medium/Low/Info
- **Description:** What was found
- **Details:** Specific evidence
- **Recommendation:** What to do about it

### F5: Visual Risk Radar
Spider/radar chart showing normalized scores across categories:
- Authenticity (typosquatting, provenance)
- Maintenance (age, updates, maintainers)
- Security (vulns, scripts, commands)
- Reputation (downloads, stars, community)

### F6: Package Metadata Display
- Name, version, description
- Author and maintainers
- Repository links
- License
- Creation/modification dates
- Download statistics

---

## Non-Functional Requirements

### Performance
- Audit completes in < 5 seconds for typical packages
- Concurrent API calls to npm, GitHub, advisory DBs

### Reliability
- Graceful degradation if external APIs fail
- Clear error messages for invalid packages

### Usability
- Single-page web interface
- No authentication required
- Mobile-responsive design

### Deployment
- Docker Compose for one-command startup
- Environment variables for configuration
- Health check endpoint

---

## Technical Constraints

### Must Use
- Containerized deployment (Docker)
- Web interface accessible on configurable port
- Public APIs only (no API keys required for basic function)

### APIs to Integrate
1. **npm Registry API** - `registry.npmjs.org`
2. **npm Downloads API** - `api.npmjs.org`
3. **GitHub API** - Repository verification (rate-limited)
4. **GitHub Advisory Database** - Known vulnerabilities

### Rate Limiting Considerations
- GitHub API: 60 requests/hour unauthenticated
- npm Registry: Generally permissive
- Implement caching for repeated lookups

---

## Success Criteria

1. ✅ Accurately identifies known-bad packages (test against historical attacks)
2. ✅ Produces actionable, understandable reports
3. ✅ Runs with single `docker compose up` command
4. ✅ Completes audit in reasonable time (<10s)
5. ✅ Visually distinctive and memorable UI
6. ✅ Code is clean and well-documented

---

## Out of Scope (v1)

- Multi-ecosystem support (PyPI, Maven, etc.)
- Historical trend analysis
- Continuous monitoring/alerting
- API authentication for higher rate limits
- Dependency tree deep scanning
- SBOM generation
- Integration with CI/CD systems

---

## Test Cases

### Known-Bad Packages (Historical)
| Package | Attack Type | Expected Detection |
|---------|-------------|-------------------|
| `event-stream` | Maintainer hijack | Medium (historical) |
| `ua-parser-js` | Account compromise | Should show vulns |
| `colors` | Sabotage | Unmaintained warning |
| `node-ipc` | Protestware | Install script warning |

### Typosquatting Examples
| Input | Should Flag Similarity To |
|-------|---------------------------|
| `lodahs` | `lodash` |
| `expresss` | `express` |
| `recat` | `react` |

### Legitimate Packages (Low Risk Expected)
- `lodash` - Established, well-maintained
- `express` - Popular, multiple maintainers
- `@types/node` - Official TypeScript definitions

---

## Timeline

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| Design | 30 min | PRD, Tech Design |
| Backend | 60 min | FastAPI service |
| Frontend | 60 min | React dashboard |
| Integration | 30 min | Docker compose |
| Testing | 30 min | Verification |
| Polish | 30 min | UI/UX refinement |

---

## Appendix: Inspiration

- **Socket.dev** - Commercial supply chain security
- **Snyk** - Vulnerability scanning
- **npm audit** - Built-in but limited
- **Bundlephobia** - Size analysis (UI inspiration)
- **deps.dev** - Google's dependency insights
