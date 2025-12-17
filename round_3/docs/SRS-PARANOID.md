# Software Requirements Specification: PARANOID v2
## SBOM Roast Generator for Chainguard Vibe Coding Tournament

**Document Version**: 1.0
**Date**: 2025-12-16
**Project**: Vibelympics Round 3 - PARANOID
**Associated ADR**: TBD (Architecture decisions to be documented during implementation)

---

## 1. Project Overview

### 1.1 Objectives
Build a supply chain roast generator that:
- Analyzes dependency files (package.json, requirements.txt, go.mod, SBOMs)
- Generates security memes using pre-built templates with curated captions
- Maintains escalating paranoia about its own integrity
- Produces sarcastic SBOM outputs that mock compliance theater
- Delivers reliable demo performance with zero external runtime dependencies

### 1.2 Success Criteria
**Must Have (Demo Works)**:
- Dependency file analysis completes in under 3 seconds
- Meme generation never fails (fallback to random captions)
- Paranoia system responds visibly to triggers
- SBOM output includes sarcastic commentary
- Health endpoint returns neurotic status messages

**Should Have (Demo Shines)**:
- CVE detection with specific package-level roasts
- Cursed package easter eggs (left-pad, event-stream, etc.)
- SBOM-of-SBOM recursive compliance joke
- Digital signatures on outputs

**Nice to Have (Bonus Points)**:
- Shareable meme URLs with persistence
- Roast history within user session
- Side-by-side comparison of two dependency files

### 1.3 Scope Boundaries

**In Scope**:
- Template-based meme generation (no AI image generation)
- Pre-cached CVE database (build-time refresh)
- Session-based paranoia state management
- Static frontend with minimal JavaScript
- Containerization using Chainguard images

**Out of Scope**:
- Real-time CVE database queries
- AI-generated images (stability risk)
- User authentication or persistence
- Multi-user session management
- Actual security remediation advice

---

## 2. Requirements Tracking Table

### 2.1 Backend Core Infrastructure

| REQ-ID | Description | Acceptance Criteria | Effort | Status | Priority |
|--------|-------------|---------------------|--------|--------|----------|
| REQ-001 | FastAPI application setup | FastAPI app runs on port 8000, returns 200 on GET /, has CORS configured | S | Pending | Must Have |
| REQ-002 | Health endpoint with paranoia levels | GET /healthz returns JSON with status, message, paranoia_level, roasts_completed | S | Pending | Must Have |
| REQ-003 | Paranoia state endpoint | GET /paranoia returns current level (0-2), level_name, message, triggers_this_session | S | Pending | Must Have |
| REQ-004 | Template list endpoint | GET /templates returns list of available meme templates with metadata | S | Pending | Should Have |
| REQ-005 | Error responses as roasts | 400/401/413/429/500 errors return sarcastic messages matching spec format | S | Pending | Should Have |

### 2.2 Dependency Analysis Engine

| REQ-ID | Description | Acceptance Criteria | Effort | Status | Priority |
|--------|-------------|---------------------|--------|--------|----------|
| REQ-006 | Parse package.json format | Extract dependencies + devDependencies, count total, identify package@version pairs | M | Pending | Must Have |
| REQ-007 | Parse requirements.txt format | Extract package specifications, handle == != >= <= ~= operators, count total | M | Pending | Must Have |
| REQ-008 | Parse go.mod format | Extract require blocks, identify module@version pairs, count total | M | Pending | Must Have |
| REQ-009 | Parse SBOM formats | Accept CycloneDX and SPDX JSON, extract components list, count total | M | Pending | Should Have |
| REQ-010 | Single package quick roast | Accept "package@version" or "package" input, analyze single dependency | S | Pending | Must Have |
| REQ-011 | Dependency count analysis | Calculate total deps, classify as 0-10/11-50/51-100/101-500/500+ buckets | S | Pending | Must Have |
| REQ-012 | Supply chain chaos score | Calculate score based on: dep_count * 0.3 + cve_count * 10 + cursed_count * 20 + outdated_count * 2 | M | Pending | Should Have |

### 2.3 CVE Detection System

| REQ-ID | Description | Acceptance Criteria | Effort | Status | Priority |
|--------|-------------|---------------------|--------|--------|----------|
| REQ-013 | CVE data cache structure | JSON file with package_name: [cve_ids], severity, description mapping | S | Pending | Must Have |
| REQ-014 | Pre-cache famous CVEs | Include Log4Shell, Heartbleed, Shellshock, left-pad, event-stream, colors, faker | M | Pending | Must Have |
| REQ-015 | CVE matching logic | Match package@version against cached CVE database, return all matches | M | Pending | Must Have |
| REQ-016 | CVE severity classification | Classify as LOW/MEDIUM/HIGH/CRITICAL, assign roast intensity accordingly | S | Pending | Should Have |
| REQ-017 | Build-time CVE refresh script | Script to fetch recent CRITICAL/HIGH CVEs from NVD, update cache JSON | L | Pending | Nice to Have |

### 2.4 Cursed Package Detection

| REQ-ID | Description | Acceptance Criteria | Effort | Status | Priority |
|--------|-------------|---------------------|--------|--------|----------|
| REQ-018 | Cursed package database | JSON with package names, incident descriptions, easter egg messages | S | Pending | Should Have |
| REQ-019 | Detect left-pad | Match "left-pad" package, return legendary severity, special roast message | S | Pending | Should Have |
| REQ-020 | Detect event-stream | Match "event-stream" package, return cryptocurrency miner easter egg | S | Pending | Should Have |
| REQ-021 | Detect colors/faker | Match "colors" or "faker", return maintainer quit incident message | S | Pending | Should Have |
| REQ-022 | Detect ua-parser-js | Match "ua-parser-js", return 2021 supply chain attack reference | S | Pending | Should Have |

### 2.5 Meme Generation System

| REQ-ID | Description | Acceptance Criteria | Effort | Status | Priority |
|--------|-------------|---------------------|--------|--------|----------|
| REQ-023 | Meme template storage | 10 PNG templates stored in /templates directory, indexed by template_id | M | Pending | Must Have |
| REQ-024 | Caption library JSON | captions.json with 500+ pre-written captions organized by category and template | L | Pending | Must Have |
| REQ-025 | Text overlay rendering | Use Pillow to overlay text on template, support top/bottom text or multi-panel | M | Pending | Must Have |
| REQ-026 | Font rendering with fallback | Use Impact font, fallback to Arial, handle text wrapping and scaling | M | Pending | Must Have |
| REQ-027 | Meme file output | Save rendered meme to /static/memes/{meme_id}.png, return URL path | S | Pending | Must Have |
| REQ-028 | Template-to-finding mapping | Map finding types to appropriate templates per spec table (line 442-448) | M | Pending | Must Have |

### 2.6 Caption Selection System

| REQ-ID | Description | Acceptance Criteria | Effort | Status | Priority |
|--------|-------------|---------------------|--------|--------|----------|
| REQ-029 | Caption category organization | Organize captions by: dependency_count, outdated, cve, cursed, sbom, paranoia | S | Pending | Must Have |
| REQ-030 | LLM caption adaptation | Use Claude API to select and adapt caption from curated list based on findings | M | Pending | Should Have |
| REQ-031 | Fallback random selection | If LLM fails, randomly select caption from appropriate category | S | Pending | Must Have |
| REQ-032 | Caption variable substitution | Replace {dep_count}, {package_name}, {cve_id} in caption templates | M | Pending | Should Have |
| REQ-033 | Caption uniqueness tracking | Track used captions per session, prefer unused captions for variety | M | Pending | Nice to Have |

### 2.7 Paranoia State Management

| REQ-ID | Description | Acceptance Criteria | Effort | Status | Priority |
|--------|-------------|---------------------|--------|--------|----------|
| REQ-034 | Session-based paranoia state | Store paranoia level (0-2) per session, persist across requests | M | Pending | Must Have |
| REQ-035 | Paranoia level triggers | Implement 5 triggers: large_deps, rapid_requests, dangerous_strings, user_argues, session_time | M | Pending | Must Have |
| REQ-036 | Paranoia level reducers | Implement 2 reducers: simple_lookup, waiting_period | M | Pending | Should Have |
| REQ-037 | CHILL level behavior | Level 0: Normal roasting, signs outputs, cheerful snark flavor text | S | Pending | Must Have |
| REQ-038 | ANXIOUS level behavior | Level 1: Add warnings, question user identity, suspicious commentary | S | Pending | Must Have |
| REQ-039 | MELTDOWN level behavior | Level 2: Refuse some requests, generate self-doubt memes, existential crisis | M | Pending | Must Have |
| REQ-040 | Session reset mechanism | New session or explicit reset returns paranoia to level 0 | S | Pending | Must Have |

### 2.8 SBOM Generation System

| REQ-ID | Description | Acceptance Criteria | Effort | Status | Priority |
|--------|-------------|---------------------|--------|--------|----------|
| REQ-041 | SBOM output structure | Generate CycloneDX 1.4 format JSON with confidence, completeness_score, components | M | Pending | Must Have |
| REQ-042 | Sarcastic confidence scoring | Always set confidence: LOW, completeness_score: 15-35% (random), will_prevent_next_attack: false | S | Pending | Must Have |
| REQ-043 | SBOM commentary rotation | Randomly select from 5+ commentary options per spec (line 161-166) | S | Pending | Must Have |
| REQ-044 | Components list population | Populate components array with analyzed dependencies, include version, purl | M | Pending | Should Have |
| REQ-045 | SBOM-specific roast | If input is SBOM, add special roast about incompleteness per spec (line 170-171) | S | Pending | Should Have |
| REQ-046 | Meta-SBOM recursion | Endpoint or feature to generate "SBOM of the SBOM" with recursive joke | M | Pending | Nice to Have |

### 2.9 Main Roast Endpoint

| REQ-ID | Description | Acceptance Criteria | Effort | Status | Priority |
|--------|-------------|---------------------|--------|--------|----------|
| REQ-047 | POST /roast endpoint | Accept input_type, content, include_sbom; return complete response per spec (line 318-338) | M | Pending | Must Have |
| REQ-048 | Input type validation | Validate input_type is one of: package_json, requirements_txt, go_mod, sbom, single_package | S | Pending | Must Have |
| REQ-049 | Analysis orchestration | Parse input → analyze deps → detect CVEs → detect cursed → calculate score | M | Pending | Must Have |
| REQ-050 | Findings aggregation | Collect all findings with type, severity, detail; prioritize worst finding for meme | M | Pending | Must Have |
| REQ-051 | Roast summary generation | Generate 1-2 sentence sarcastic summary of all findings | M | Pending | Should Have |
| REQ-052 | Response time optimization | Complete full roast cycle in under 3 seconds for typical input | M | Pending | Must Have |
| REQ-053 | Digital signature generation | Sign response with private key, include base64 signature in response | M | Pending | Should Have |

### 2.10 Frontend Interface

| REQ-ID | Description | Acceptance Criteria | Effort | Status | Priority |
|--------|-------------|---------------------|--------|--------|----------|
| REQ-054 | Input paste area | Large textarea accepting multi-line dependency file content | S | Pending | Must Have |
| REQ-055 | Input type selector | Radio buttons or dropdown for package_json, requirements_txt, go_mod, sbom, single_package | S | Pending | Must Have |
| REQ-056 | Submit roast button | POST to /roast, show loading state, display results | M | Pending | Must Have |
| REQ-057 | Meme display area | Show generated meme image, caption, template name | S | Pending | Must Have |
| REQ-058 | Roast summary display | Display roast_summary prominently with findings list below | S | Pending | Must Have |
| REQ-059 | Paranoia indicator | Visual indicator showing current paranoia level (0-2) with level name | M | Pending | Must Have |
| REQ-060 | SBOM collapsible viewer | Collapsible JSON viewer for SBOM output, initially collapsed | M | Pending | Should Have |
| REQ-061 | Dark terminal aesthetic | Apply dark theme with terminal-style fonts, green/amber accent colors | M | Pending | Should Have |
| REQ-062 | "Roast Me" random button | Button to trigger roast with random terrible dependency combo | M | Pending | Nice to Have |
| REQ-063 | Error message display | Show error responses as sarcastic roasts matching backend format | S | Pending | Should Have |

### 2.11 Pre-written Content Library

| REQ-ID | Description | Acceptance Criteria | Effort | Status | Priority |
|--------|-------------|---------------------|--------|--------|----------|
| REQ-064 | Dependency count roasts | Write 50+ roast variations for 5 dependency count buckets | L | Pending | Must Have |
| REQ-065 | Outdated package roasts | Write 30+ roasts for packages 1yr, 2yr, 5yr+ old | M | Pending | Should Have |
| REQ-066 | CVE severity roasts | Write 40+ roasts for LOW/MEDIUM/HIGH/CRITICAL CVEs | M | Pending | Should Have |
| REQ-067 | Cursed package roasts | Write specific roasts for left-pad, event-stream, colors, faker, ua-parser-js | M | Pending | Should Have |
| REQ-068 | SBOM commentary collection | Write 10+ variations of SBOM skepticism commentary | S | Pending | Must Have |
| REQ-069 | Paranoia flavor text | Write 5+ messages each for CHILL, ANXIOUS, MELTDOWN levels | M | Pending | Must Have |
| REQ-070 | Error message roasts | Write sarcastic messages for 400, 401, 413, 429, 451, 500 errors | S | Pending | Should Have |
| REQ-070a | Fahrenheit 451 easter egg | Return HTTP 451 when paranoia detects "dangerous knowledge" (eval, exec, __import__) with message about burning forbidden dependencies | S | Pending | Should Have |
| REQ-071 | Health endpoint messages | Write neurotic health check messages for each paranoia level | S | Pending | Must Have |

### 2.12 Containerization and Deployment

| REQ-ID | Description | Acceptance Criteria | Effort | Status | Priority |
|--------|-------------|---------------------|--------|--------|----------|
| REQ-072 | Multi-stage Dockerfile | Use cgr.dev/chainguard/python:latest-dev for build, :latest for runtime | M | Pending | Must Have |
| REQ-073 | Distroless runtime image | Final image has no shell, minimal attack surface, only Python + app | M | Pending | Should Have |
| REQ-074 | Docker Compose configuration | docker-compose.yml runs backend + frontend, maps ports, mounts volumes | S | Pending | Must Have |
| REQ-075 | Environment variable config | Support PORT, CLAUDE_API_KEY, DEBUG via environment variables | S | Pending | Must Have |
| REQ-076 | Static file serving | Serve frontend HTML/CSS/JS and generated memes via FastAPI static files | S | Pending | Must Have |
| REQ-077 | Build-time CVE refresh | CI job to refresh CVE cache before container build | L | Pending | Nice to Have |

### 2.13 Testing and Quality

| REQ-ID | Description | Acceptance Criteria | Effort | Status | Priority |
|--------|-------------|---------------------|--------|--------|----------|
| REQ-078 | Parser unit tests | Test all 4 input parsers with valid/invalid inputs, edge cases | M | Pending | Must Have |
| REQ-079 | CVE matching unit tests | Test CVE detection with known packages, version ranges, false positives | M | Pending | Must Have |
| REQ-080 | Paranoia state unit tests | Test all triggers and reducers, level transitions, session isolation | M | Pending | Must Have |
| REQ-081 | Meme rendering tests | Test all 10 templates render successfully with various caption lengths | M | Pending | Must Have |
| REQ-082 | Integration test: full roast | Test POST /roast end-to-end for each input type, verify response structure | M | Pending | Must Have |
| REQ-083 | Performance test | Verify roast completes in < 3s for 100-dependency input, < 5s for 500-dependency | M | Pending | Must Have |
| REQ-084 | Fallback behavior tests | Test LLM failure fallback, missing template fallback, empty input handling | M | Pending | Must Have |

### 2.14 Demo Preparation

| REQ-ID | Description | Acceptance Criteria | Effort | Status | Priority |
|--------|-------------|---------------------|--------|--------|----------|
| REQ-085 | Demo script document | Written demo script matching spec flow (line 369-408), timing verified | S | Pending | Must Have |
| REQ-086 | Sample dependency files | Prepare 5+ test files: minimal, bloated, CVE-laden, cursed, SBOM | M | Pending | Must Have |
| REQ-087 | Paranoia escalation demo path | Document exact sequence to trigger level 0→1→2 reliably in demo | S | Pending | Must Have |
| REQ-088 | SBOM-of-SBOM demo | Prepare and test recursive SBOM generation for big laugh moment | M | Pending | Should Have |
| REQ-089 | Container showcase | Prepare `docker inspect` or similar to show Chainguard image usage | S | Pending | Should Have |

---

## 3. Non-Functional Requirements

### 3.1 Performance

| NFR-ID | Requirement | Acceptance Criteria | Priority |
|--------|-------------|---------------------|----------|
| NFR-001 | Response Time | POST /roast completes in < 3 seconds for typical input (< 100 deps) | Must Have |
| NFR-002 | Large Input Handling | POST /roast completes in < 5 seconds for large input (500+ deps) | Should Have |
| NFR-003 | Concurrent Requests | Support 10 concurrent requests without degradation | Should Have |
| NFR-004 | Startup Time | Container starts and serves requests within 10 seconds | Should Have |

### 3.2 Reliability

| NFR-ID | Requirement | Acceptance Criteria | Priority |
|--------|-------------|---------------------|----------|
| NFR-005 | Zero External Failures | No runtime dependency on external APIs for core functionality | Must Have |
| NFR-006 | LLM Fallback | System functions fully if Claude API is unavailable | Must Have |
| NFR-007 | Graceful Degradation | Invalid inputs return 400 with helpful error, don't crash server | Must Have |
| NFR-008 | Template Robustness | All templates tested in CI, meme generation never fails | Must Have |

### 3.3 Usability

| NFR-ID | Requirement | Acceptance Criteria | Priority |
|--------|-------------|---------------------|----------|
| NFR-009 | Input Flexibility | Accept multiple formats without requiring manual format specification | Should Have |
| NFR-010 | Error Clarity | Error messages explain what went wrong while maintaining roast tone | Should Have |
| NFR-011 | Mobile Responsive | Frontend usable on tablet/mobile devices (not primary use case) | Nice to Have |

### 3.4 Security

| NFR-ID | Requirement | Acceptance Criteria | Priority |
|--------|-------------|---------------------|----------|
| NFR-012 | Input Sanitization | All user inputs sanitized before processing, no code injection possible | Must Have |
| NFR-013 | Rate Limiting | Implement 429 rate limiting at 10 requests/minute per IP | Should Have |
| NFR-014 | Minimal Attack Surface | Runtime container has no shell, only Python interpreter + app code | Should Have |
| NFR-015 | CORS Configuration | CORS restricted to specific origins, not wildcard | Should Have |

### 3.5 Maintainability

| NFR-ID | Requirement | Acceptance Criteria | Priority |
|--------|-------------|---------------------|----------|
| NFR-016 | Code Documentation | All modules have PURPOSE comments, functions have docstrings | Must Have |
| NFR-017 | Configuration Externalization | All environment-specific values in env vars, not hardcoded | Must Have |
| NFR-018 | Content Updates | Caption library updatable without code changes (JSON file) | Should Have |
| NFR-019 | CVE Cache Updates | CVE database refreshable via script or CI job | Should Have |

---

## 4. Technical Architecture Summary

### 4.1 Technology Stack

**Backend**:
- FastAPI (async web framework)
- Uvicorn (ASGI server)
- Pillow (image manipulation)
- httpx (async HTTP for Claude API)
- cryptography (digital signatures)

**Frontend**:
- HTML5 + Tailwind CSS
- Vanilla JavaScript (no framework)
- Fetch API for backend communication

**Infrastructure**:
- Docker with Chainguard Python images
- Docker Compose for local development
- Static file serving via FastAPI

### 4.2 Data Storage

**Files**:
- `/backend/data/captions.json` - Pre-written roast library (500+ entries)
- `/backend/data/cves.json` - Cached CVE database (refreshed at build time)
- `/backend/data/cursed.json` - Cursed package incidents database
- `/backend/templates/*.png` - Meme template images (10 files)
- `/backend/fonts/*.ttf` - Font files for text rendering

**Runtime State**:
- Session-based paranoia state (in-memory, session cookies)
- No persistent database required

### 4.3 External Dependencies

| Dependency | Usage | Fallback Strategy | Required? |
|------------|-------|-------------------|-----------|
| Claude API | Caption selection/adaptation | Random selection from library | Optional |
| NVD API | Build-time CVE refresh | Use existing cache | Build-time only |

### 4.4 API Endpoints Summary

| Method | Endpoint | Purpose | Priority |
|--------|----------|---------|----------|
| POST | /roast | Main roast generation | Must Have |
| GET | /healthz | Neurotic health check | Must Have |
| GET | /paranoia | Paranoia state query | Must Have |
| GET | /templates | List available templates | Should Have |
| GET | /static/memes/{id}.png | Serve generated memes | Must Have |

---

## 5. Identified Gaps and Ambiguities

### 5.1 Specification Gaps

1. **Session Management Details**
   - **Gap**: How are sessions identified? Cookies? Session IDs?
   - **Recommendation**: Use FastAPI session middleware with secure HTTP-only cookies
   - **Impact**: Medium - affects paranoia state persistence

2. **Outdated Package Detection**
   - **Gap**: How to determine package age without real-time registry queries?
   - **Recommendation**: Pre-cache popular package publish dates, or rely on version heuristics
   - **Impact**: Medium - affects "outdated" roast category

3. **"Random Terrible Dependency Combo"**
   - **Gap**: What constitutes a "terrible" combo? Pre-defined or generated?
   - **Recommendation**: Create 10-20 pre-defined terrible examples for "Roast Me" button
   - **Impact**: Low - nice-to-have feature

4. **Shareable Meme URLs**
   - **Gap**: URL persistence strategy unclear (filesystem? S3? TTL?)
   - **Recommendation**: Filesystem with 24-hour TTL, cleanup job
   - **Impact**: Low - nice-to-have feature

5. **SBOM Format Details**
   - **Gap**: Exact CycloneDX component structure not specified
   - **Recommendation**: Use minimal valid CycloneDX schema, prioritize comedy over completeness
   - **Impact**: Low - SBOM is intentionally incomplete for comedic effect

### 5.2 Technical Ambiguities

1. **Version Range Matching for CVEs**
   - **Ambiguity**: How to match version ranges (e.g., CVE affects "< 4.17.21")?
   - **Recommendation**: Use simple string matching initially, add semver library if needed
   - **Impact**: Medium - affects CVE detection accuracy

2. **Text Wrapping Algorithm**
   - **Ambiguity**: How to handle very long captions on meme templates?
   - **Recommendation**: Implement text scaling + wrapping algorithm with max 3 lines
   - **Impact**: Medium - affects meme visual quality

3. **Paranoia Trigger "User Argues"**
   - **Ambiguity**: How to detect user arguing with roast? Re-submitting same input?
   - **Recommendation**: Detect identical input hash submitted twice in 60 seconds
   - **Impact**: Low - fun but non-critical trigger

4. **Rate Limiting Scope**
   - **Ambiguity**: Per-IP? Per-session? Both?
   - **Recommendation**: 10 requests/minute per IP, show sarcastic 429 message
   - **Impact**: Medium - demo reliability consideration

### 5.3 Demo Considerations

1. **Live Chainguard Repo Scan**
   - **Risk**: Demo spec mentions "scan Chainguard's own repos live"
   - **Recommendation**: Pre-fetch a Chainguard repo's package.json as backup if live fetch fails
   - **Impact**: High - demo reliability

2. **SBOM-of-SBOM Implementation**
   - **Ambiguity**: Does this generate a new SBOM for the previous SBOM, or just add metadata?
   - **Recommendation**: Generate actual second-level SBOM listing the first SBOM as component
   - **Impact**: Medium - key demo moment

3. **Meltdown Refusal Behavior**
   - **Ambiguity**: What percentage of requests at level 2 are refused?
   - **Recommendation**: 50% chance of refusal with self-doubt meme, ensures demo can proceed
   - **Impact**: High - demo flow reliability

---

## 6. Implementation Priorities

### 6.1 Phase 1: Minimum Viable Demo (Must Have)

**Goal**: Working demo in 4-6 hours

**Requirements**: REQ-001 through REQ-013, REQ-023 through REQ-027, REQ-029, REQ-031, REQ-034, REQ-035, REQ-037 through REQ-040, REQ-041 through REQ-043, REQ-047 through REQ-049, REQ-054 through REQ-059, REQ-064, REQ-068, REQ-069, REQ-072, REQ-074 through REQ-076, REQ-078, REQ-082, REQ-085, REQ-086

**Deliverables**:
- POST /roast accepts package.json and requirements.txt
- Dependency counting and basic analysis
- Template-based meme generation with random caption selection
- 3-level paranoia system with triggers
- Sarcastic SBOM output
- Basic frontend with paste area and results display
- Containerized application
- Demo script

### 6.2 Phase 2: Demo Polish (Should Have)

**Goal**: Impressive demo in additional 3-4 hours

**Requirements**: REQ-014 through REQ-022, REQ-028, REQ-030, REQ-032, REQ-044, REQ-045, REQ-050 through REQ-053, REQ-060, REQ-061, REQ-063, REQ-065 through REQ-067, REQ-070, REQ-071, REQ-073, REQ-079 through REQ-081, REQ-083, REQ-084, REQ-087 through REQ-089

**Deliverables**:
- CVE detection with famous CVE easter eggs
- Cursed package detection
- LLM caption adaptation with fallback
- Digital signatures
- SBOM-of-SBOM recursion feature
- Dark terminal aesthetic
- Error message roasts
- Full test coverage
- Paranoia escalation demo path

### 6.3 Phase 3: Bonus Features (Nice to Have)

**Goal**: Extra polish if time permits (1-2 hours)

**Requirements**: REQ-008, REQ-017, REQ-033, REQ-046, REQ-062, REQ-077

**Deliverables**:
- Go.mod parsing
- Build-time CVE refresh automation
- "Roast Me" random button
- Caption uniqueness tracking
- SBOM format input support

---

## 7. Testing Strategy

### 7.1 Unit Testing

**Components to Test**:
- Dependency parsers (package.json, requirements.txt, go.mod, SBOM)
- CVE matching logic
- Cursed package detection
- Paranoia state machine
- Caption selection (with and without LLM)
- SBOM generation
- Text overlay rendering

**Test Data**:
- Valid and invalid dependency files
- Edge cases: empty files, malformed JSON, massive files
- Known CVE packages with version variations
- All cursed packages

### 7.2 Integration Testing

**Scenarios**:
1. POST /roast with package.json → verify complete response structure
2. Paranoia escalation through multiple requests → verify level changes
3. Meme generation for all template types → verify image output
4. SBOM generation with varying input sizes → verify performance
5. Error conditions → verify sarcastic error responses

### 7.3 Demo Rehearsal Testing

**Checklist**:
- [ ] Demo script executed start to finish in < 5 minutes
- [ ] All sample files roast successfully
- [ ] Paranoia escalation triggers reliably
- [ ] SBOM-of-SBOM generates expected output
- [ ] Container starts cleanly and quickly
- [ ] No external API failures possible
- [ ] Backup plans tested for each demo step

---

## 8. Risk Assessment

| Risk | Likelihood | Impact | Mitigation | Owner |
|------|------------|--------|------------|-------|
| LLM API fails during demo | Medium | Low | Fallback to random caption selection | Backend |
| Meme rendering takes too long | Low | High | Pre-render common templates, optimize Pillow | Backend |
| Paranoia state doesn't trigger | Low | Medium | Add manual paranoia level override for demo | Backend |
| CVE detection misses obvious packages | Medium | Medium | Extensive pre-cached CVE database | Backend |
| Frontend doesn't handle large SBOM output | Medium | Low | Collapsible JSON viewer with virtual scrolling | Frontend |
| Container fails to build | Low | High | Test Chainguard image compatibility early | DevOps |
| Demo input file has no roastable content | Low | Medium | Prepare backup terrible dependency files | Content |

---

## 9. Definition of Done

### 9.1 Per Requirement

A requirement is considered complete when:
- [ ] Implementation matches acceptance criteria exactly
- [ ] Unit tests pass with > 80% coverage for affected code
- [ ] Integration test demonstrates requirement in context
- [ ] Code reviewed and follows style guidelines
- [ ] PURPOSE comments added to new files
- [ ] No console errors or warnings in normal operation
- [ ] Committed to feature branch with conventional commit message

### 9.2 Per Phase

A phase is considered complete when:
- [ ] All phase requirements meet individual DOD
- [ ] Full integration test suite passes
- [ ] Demo script executable with phase features
- [ ] Performance benchmarks met (< 3s roast time)
- [ ] No known blocking bugs
- [ ] Documentation updated (this SRS, ADRs if applicable)

### 9.3 Project Complete

The project is considered complete when:
- [ ] All Must Have requirements implemented and tested
- [ ] Demo rehearsed successfully 3+ times without failures
- [ ] Container builds and runs on clean system
- [ ] All error conditions handled gracefully
- [ ] Content library has minimum 500 caption variations
- [ ] CVE database includes 50+ famous CVEs
- [ ] Health check returns proper status at all paranoia levels
- [ ] SBOM output validates against CycloneDX schema
- [ ] No external runtime dependencies for core demo flow
- [ ] Performance metrics met: < 3s typical roast, < 5s large input
- [ ] Demo video recorded showing full feature set

---

## 10. Assumptions and Dependencies

### 10.1 Assumptions

1. Demo environment has internet access for optional LLM calls
2. Audience is technical and familiar with supply chain security concepts
3. Demo will be judged on creativity, execution, and Chainguard brand alignment
4. Template memes are legally usable (fair use for parody/commentary)
5. Pre-written captions are sufficiently funny across diverse dependency inputs
6. Session duration < 30 minutes (paranoia state doesn't need long-term persistence)

### 10.2 Dependencies

**Development**:
- Python 3.11+ for FastAPI and async support
- Docker and Docker Compose for containerization
- Access to Claude API for optional caption adaptation
- Meme template images (sourced or created)
- Impact font or similar for meme text

**Runtime**:
- Docker runtime environment
- Port 8000 available for backend
- Port 3000 available for frontend (if separate)
- Minimal RAM (< 512MB) and CPU (< 1 core)

**External Services** (optional):
- Claude API (Anthropic) - fallback available
- NVD API (NIST) - build-time only

---

## 11. Open Questions

1. **Q**: Should we support file upload in addition to paste?
   **A**: Defer to Phase 3 - paste is sufficient for demo

2. **Q**: What format should digital signatures use?
   **A**: Ed25519 signature of JSON response, base64-encoded in signature field

3. **Q**: How long should generated memes persist?
   **A**: 24 hours, then cleanup job deletes (nice-to-have feature)

4. **Q**: Should paranoia state sync across browser tabs?
   **A**: No - session-based, new tab = new session

5. **Q**: Can users submit their own captions?
   **A**: Out of scope - pre-written library only maintains quality

6. **Q**: Should we track analytics (roast count, popular findings)?
   **A**: Defer to post-tournament - not required for demo

---

## 12. Success Measurement

### 12.1 Technical Metrics

- **Response Time**: 95th percentile < 3 seconds
- **Uptime**: 100% during demo (no crashes)
- **Test Coverage**: > 80% line coverage
- **Fallback Success**: 100% success rate when LLM unavailable
- **Template Rendering**: 100% success rate across all templates

### 12.2 Demo Metrics

- **Demo Duration**: 4-5 minutes (matches spec timing)
- **Audience Laughs**: Subjective but track reactions
- **Feature Coverage**: All "Must Have" features demonstrated
- **Failure Rate**: 0 errors during demo
- **Recovery Time**: < 5 seconds if something does fail

### 12.3 Content Quality

- **Caption Variety**: < 10% repeat captions in typical 10-roast session
- **Roast Accuracy**: Detected findings match actual dependency issues
- **Comedy Landing Rate**: Subjective feedback from test audiences
- **Brand Alignment**: References to SBOM skepticism, supply chain paranoia

---

## Document Change History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-16 | Requirements Specification Expert | Initial SRS creation based on PARANOID v2 spec |

---

**END OF SOFTWARE REQUIREMENTS SPECIFICATION**

*Total Requirements*: 89 functional + 19 non-functional = **108 requirements**
*Estimated Effort*: 8-12 hours per spec timeline
*Priority Breakdown*: 52 Must Have, 45 Should Have, 11 Nice to Have
