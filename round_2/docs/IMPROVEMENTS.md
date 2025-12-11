# CHAINSAW Improvements Summary

This document summarizes all enhancements made to the CHAINSAW npm supply chain security auditor.

## Branding

- **Renamed**: "Repojacker" → "CHAINSAW"
- **Tagline**: "Cutting through supply chain threats"
- **Logo**: Saw blade icon (🪚)

---

## Security Infrastructure

### Zero-CVE Container Images

Migrated both containers to Chainguard base images with **0 CVEs**:

| Container | Base Image |
|-----------|------------|
| Backend | `cgr.dev/chainguard/python:latest` |
| Frontend | `cgr.dev/chainguard/nginx:latest` |

**Verification commands:**
```bash
# Docker Scout
docker scout cves ghcr.io/chanfi0ne/vibelympics/chainsaw-backend:latest
docker scout cves ghcr.io/chanfi0ne/vibelympics/chainsaw-frontend:latest

# Trivy
trivy image ghcr.io/chanfi0ne/vibelympics/chainsaw-backend:latest
trivy image ghcr.io/chanfi0ne/vibelympics/chainsaw-frontend:latest
```

### SLSA Provenance

Added SLSA (Supply-chain Levels for Software Artifacts) provenance attestations to GitHub Actions workflow for container builds.

### Non-root Execution

Both containers run as non-root users:
- Backend: `nonroot` user (Chainguard default)
- Frontend: nginx runs on port 8080 (non-privileged)

---

## Backend Enhancements

### Real Vulnerability Detection (OSV.dev)

Implemented full OSV.dev API client that:
- Queries the Open Source Vulnerabilities database
- Aggregates data from multiple sources: GitHub Advisory Database (GHSA), NVD, npm advisories
- Performs **version-aware filtering** using semver range checking
- Returns only CVEs that actually affect the queried version

**Key files:**
- `backend/services/osv_client.py` - OSV API client with `fetch_vulnerabilities()` and `fetch_all_vulnerabilities()`

### Historical CVE Tracking

- Shows count of CVEs that existed in older versions but are **fixed** in the current version
- Example: "5 historical CVEs fixed in this version"
- Helps users understand the security improvements of newer versions

### Version-Specific Analysis

- Added optional `version` parameter to audit endpoint
- Returns version-specific publish date (not package modified date)
- Fetches last 20 versions sorted by semver (descending)

### Dependency Analysis

New analyzer that flags excessive dependencies:
- **Medium risk**: 50-100 dependencies
- **High risk**: 100+ dependencies

### License Analysis

New analyzer that detects license issues:
- **High risk**: Missing license, "UNLICENSED"
- **Medium risk**: No license field
- **Info**: Copyleft licenses (GPL, AGPL, LGPL)

### Version Comparison Endpoint

New `/api/audit/compare` endpoint for side-by-side CVE comparison between two versions.

---

## Scoring Algorithm

### Exponential Decay (Diminishing Returns)

Changed from linear deductions to exponential decay formula:

```
score = 100 × (0.5 ^ weighted_severity)
```

**Severity weights:**
| Severity | Weight |
|----------|--------|
| Critical | 0.5 |
| High | 0.3 |
| Medium | 0.15 |
| Low | 0.05 |

**Benefits:**
- First critical CVE has biggest impact
- Additional CVEs have progressively smaller impact
- Avoids "instant zero" scores
- More nuanced risk assessment
- Minimum score of 5 (never hits 0)

**Example:**
- 1 Critical: 100 × 0.5^0.5 = 70
- 1 Critical + 1 High: 100 × 0.5^0.8 = 57
- 8 mixed CVEs: ~17-25 (not 0)

---

## Frontend Enhancements

### Mode Toggle

Two analysis modes:
1. **Deep Inspection** - Full security audit of a single package/version
2. **Compare Versions** - Side-by-side CVE diff between two versions

### Version Picker

- Dropdown showing last 20 versions (semver sorted, descending)
- Automatically populated after initial audit
- Selecting a version re-runs the audit

### Threat Level Display

Improved risk score visualization:

```
        Threat Level
    0 = Safe → 100 = Dangerous
           [SCORE]
          / 100
        [SEVERITY]
        
        [VERDICT]
        [DESCRIPTION]
```

**Verdicts by score:**
| Score | Verdict |
|-------|---------|
| 80+ | DO NOT USE |
| 60-79 | USE WITH EXTREME CAUTION |
| 40-59 | REVIEW CAREFULLY |
| 20-39 | ACCEPTABLE RISK |
| 0-19 | GENERALLY SAFE |

### Threat Summary

Shows breakdown of what's driving the score:
- **Severity badges**: `[1 Critical] [3 High] [2 Medium]`
- **Top 3 issues**: Lists critical/high findings by name
- **"+X more findings below"**: Links to full results

### Version Age Display

Shows how old the selected version is:
- Recent versions: `📅 This version is 3 months old`
- Old versions (2+ years): `⚠️ This version is 8 years old — consider upgrading or use an alternate library`

### Historical CVEs Badge

Green badge showing CVEs fixed in current version:
```
✓ 5 historical CVEs fixed in this version
```

### Loading Screen

Enhanced with vulnerability database indicators:
- GitHub Advisory Database (GHSA)
- National Vulnerability Database (NVD)
- npm Security Advisories
- OSV.dev (aggregator)

### Example Package Buttons

Quick-scan buttons for demo packages:
- `lodash` - Popular utility library
- `express` - Web framework
- `lodahs` - Typosquat example
- `event-stream` - Historical malware incident

---

## Test Coverage

Added comprehensive pytest test suite with **45 tests**:

| Category | Tests |
|----------|-------|
| Typosquatting detection | 10 |
| Analyzer functions | 21 |
| Scoring algorithm | 14 |

**Test files:**
- `backend/tests/test_typosquat.py`
- `backend/tests/test_analyzer.py`
- `backend/tests/test_scoring.py`

---

## Bug Fixes

1. **Nginx proxy 404**: Created full `nginx.conf` for Chainguard nonroot requirements
2. **Version sorting**: Implemented proper semver sorting with pre-release handling
3. **Dashboard not updating**: Fixed state update on version change
4. **Tests excluded**: Removed `tests` from `.dockerignore`
5. **Test expectations**: Updated for exponential decay algorithm

---

## Files Modified/Created

### Backend
- `services/osv_client.py` - New OSV.dev API client
- `services/analyzer.py` - Added dependency/license analyzers
- `services/scoring.py` - Exponential decay algorithm
- `routers/audit.py` - Version parameter, historical CVEs, compare endpoint
- `models/request.py` - Added version field, CompareRequest
- `models/response.py` - Added historical_cves_fixed, available_versions
- `tests/test_*.py` - New test files
- `.dockerignore` - Removed tests exclusion
- `Dockerfile` - Chainguard base image

### Frontend
- `src/App.jsx` - Mode toggle, version picker, historical badge
- `src/components/RiskScore.jsx` - Threat summary, age display, verdicts
- `src/components/CompareSearch.jsx` - New comparison input form
- `src/components/CompareView.jsx` - New side-by-side comparison view
- `src/hooks/useAudit.js` - Version parameter support
- `nginx.conf` - Full config for Chainguard nonroot
- `Dockerfile` - Chainguard base images

### CI/CD
- `.github/workflows/round-2-ci.yml` - SLSA provenance, renamed images

---

## Commits (chronological)

1. `feat: implement real OSV.dev vulnerability client`
2. `feat: add dependency and license analyzers`
3. `test: add comprehensive pytest test suite`
4. `feat: migrate to Chainguard zero-CVE base images`
5. `fix: nginx config for Chainguard nonroot user`
6. `feat: add SLSA provenance to CI/CD`
7. `rebrand: Repojacker → CHAINSAW`
8. `ui: rename 'Audit Package' to 'Deep Inspection'`
9. `feat: add historical CVEs badge and version picker`
10. `fix: sort versions by semver`
11. `fix: use diminishing returns for radar score`
12. `ux: improve threat level display clarity`
13. `ux: add threat summary showing why score is high`
14. `ux: add version age to threat summary`
15. `ux: suggest alternate library for old versions`
16. `fix: update tests for exponential decay scoring`
17. `docs: rebrand to CHAINSAW in main README`
