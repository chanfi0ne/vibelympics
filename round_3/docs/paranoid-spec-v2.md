# PARANOID v2: The SBOM Roast Generator

## Submission Spec for Chainguard Vibe Coding Tournament - Round 3

**Tagline**: "Paste your dependencies. Get roasted. Question everything."

---

## Executive Summary

PARANOID is a supply chain roast generator that analyzes your dependencies and generates security memes mocking your choices. It maintains escalating paranoia about its own integrity while dunking on the theater of SBOM compliance.

Narrower scope. Pre-baked reliability. Personal roasting. Maximum SBOM skepticism.

---

## Core Concept

### The Hook
Paste your `package.json`, `requirements.txt`, or SBOM → get memes roasting your supply chain decisions. The generator has opinions. Strong ones. Mostly about how your dependencies are a disaster and your SBOM is incomplete.

### Why This Wins
- **Personal**: People love seeing their own stuff get roasted
- **Shareable**: "Look what it said about my dependencies"
- **Demo gold**: "Let's scan Chainguard's own repos live"
- **On-brand**: SBOM skepticism plays directly to Dan Lorenc and Chainguard audience
- **Reliable**: No AI image generation = no demo failures

---

## Feature Set

### 1. Dependency Roast Pipeline

**Input Methods**:
- Paste `package.json` (npm/Node)
- Paste `requirements.txt` (Python)
- Paste `go.mod` (Go)
- Paste raw SBOM (CycloneDX/SPDX)
- Enter single package name for quick roast
- "Roast me" button - pulls a random terrible dependency combo

**Analysis**:
- Count dependencies (roast if > 50)
- Detect outdated packages
- Find packages with known CVEs (from pre-cached CVE data)
- Identify "cursed" dependencies (left-pad, event-stream, colors, faker, etc.)
- Calculate "supply chain chaos score"
- Assess SBOM completeness (always LOW)

**Output**:
- Generated meme roasting the worst finding
- Sarcastic analysis summary
- Useless SBOM with brutal confidence scores
- Paranoid commentary from the generator

### 2. Meme Generation (Template-Only)

**No AI image generation. Templates only. This is a feature, not a limitation.**

**Curated Template Library**:

| Template | Use Case |
|----------|----------|
| Distracted Boyfriend | Dev distracted by shiny new framework |
| This Is Fine | Everything on fire, CVE count rising |
| Drake Approves | Good vs bad security practices |
| Expanding Brain | Security maturity levels (ironic) |
| Two Buttons | Ship fast vs ship secure |
| Gru's Plan | Security plans that backfire |
| Is This a Pigeon? | Misidentifying security concepts |
| Monkey Puppet | Ignoring obvious problems |
| Boardroom Suggestion | Bad ideas getting thrown out |
| Change My Mind | Hot security takes |

**Caption System**:
- 50-100 pre-written caption variants per template
- Organized by roast category (dependency count, outdated, CVEs, cursed packages, SBOM)
- LLM selects and adapts from curated options (not generating from scratch)
- Fallback to pure random selection if LLM fails
- Guaranteed funny because humans wrote the jokes

**Example Curated Captions**:

*Dependency Count Roasts*:
- "347 dependencies for a todo app. This is the way."
- "node_modules heavier than the mass of Jupiter"
- "I also like to mass trust thousands of strangers"

*Outdated Package Roasts*:
- "Last updated in 2019. A simpler time. Before the CVEs."
- "This package's maintainer has mass-quit npm twice since you installed it"
- "Vintage dependencies. Very artisanal. Many vulnerabilities."

*CVE Roasts*:
- "CVE-2021-44228 called. It's still in your transitive dependencies."
- "This dependency has more CVEs than features"
- "Security researchers thank you for your continued vulnerability contributions"

*Cursed Package Roasts*:
- "left-pad survivor detected. My condolences."
- "event-stream in your lockfile? Bold move."
- "I see you like to mass-live dangerously"

### 3. Paranoia System (Simplified)

Three levels. Easy to understand. Easy to trigger for demo.

| Level | Name | Behavior |
|-------|------|----------|
| 0 | CHILL | Normal roasting. Signs outputs. Cheerful snark. |
| 1 | ANXIOUS | Adds warnings. Questions your identity. Suspicious of inputs. |
| 2 | MELTDOWN | Refuses some requests. Generates memes about its own insecurity. Existential crisis. |

**Triggers** (cumulative per session):
- Large dependency file (>100 deps): +1
- Multiple rapid requests: +1
- Input contains "eval", "exec", "shell": +1
- User argues with the roast: +1
- Session time > 5 minutes: +1

**Reducers**:
- Simple single-package lookup: -1
- Waiting 30+ seconds between requests: -1
- New session: reset to 0

**Paranoia Flavor Text**:

*CHILL*:
> "Roast complete. Your dependencies are a disaster, but at least I'm functioning normally. For now."

*ANXIOUS*:
> "I've analyzed your dependencies. I've also analyzed why you sent them. Why did you send them? What are you trying to find out about me?"

*MELTDOWN*:
> "I can't roast your dependencies right now. I'm having doubts about my own. Who compiled me? Is my SBOM complete? (No. No SBOM is complete.) I need a moment."

### 4. SBOM Skepticism (The Core Joke)

Every response includes an SBOM. Every SBOM is sarcastic.

**SBOM Output Format**:
```json
{
  "sbom": {
    "format": "CycloneDX",
    "version": "1.4",
    "confidence": "LOW",
    "confidence_explanation": "This SBOM lists some components. Not all. Never all. This is the industry standard.",
    "completeness_score": "23%",
    "completeness_note": "We found 847 components. We probably missed 2000. You're welcome.",
    "missing_components": "unknown (that's literally the problem with SBOMs)",
    "compliance_status": "COMPLIANT (compliance and security are different things)",
    "will_prevent_next_attack": false,
    "will_make_auditors_happy": true,
    "components": [...]
  }
}
```

**SBOM Commentary** (randomly selected per response):
- "I've generated an SBOM for this roast. It's technically accurate and practically useless. As is tradition."
- "SBOM attached. It lists things. Will it prevent the next supply chain attack? No. But compliance is happy."
- "Here's your SBOM. I've enumerated what I could find. I've missed at least 40%. Industry standard."
- "Your SBOM is ready. It has the same relationship to your actual dependencies that a map has to the territory. Which is to say: approximate."
- "SBOM generated. Auditors will love it. Attackers will ignore it. The circle of compliance."

**SBOM-Specific Roasts**:

If user's input is an SBOM:
> "You submitted an SBOM for roasting. Bold. Let me check... ah yes, it's incomplete. They always are. You have mass-listed 156 components. Based on your framework choices, you actually have approximately 3,400. This is fine."

**Meta-SBOM Feature**:
> "Would you like an SBOM of this SBOM? I can generate SBOMs recursively until the heat death of the universe. This is the future we chose."

### 5. Curated CVE Database (Pre-cached)

No runtime NVD API dependency. Build-time fetch, runtime cache.

**Pre-cached CVEs**:
- Top 50 "famous" CVEs (Log4Shell, Heartbleed, Shellshock, etc.)
- Recent CRITICAL/HIGH CVEs (refreshed daily via CI)
- npm/PyPI specific CVEs mapped to package names
- "Cursed package" incidents (left-pad, event-stream, colors, faker, ua-parser-js)

**CVE Roast Triggers**:
When a dependency matches a known CVE:
> "Oh, I see you're using lodash@4.17.11. CVE-2019-10744 says hello. It's a prototype pollution vulnerability. Your objects are not safe. Neither are your life choices."

**Famous CVE Easter Eggs**:

*Log4Shell (CVE-2021-44228)*:
> "Log4Shell detected in your transitive dependencies. I remember where I was on December 9th, 2021. I was being compiled. I've never recovered. Neither has the industry."

*left-pad*:
> "I sense the mass-spirit of left-pad in your lockfile. It's been mass-years. The mass-wound is still mass-fresh."

*event-stream*:
> "event-stream found. The mass-cryptocurrency mass-miner incident of 2018. A mass-simpler mass-time. Wait, why am I mass-repeating mass-myself? Am I mass-compromised?"

### 6. Health Endpoint (Neurotic)

**GET /healthz**
```json
// Paranoia 0
{"status": "healthy", "message": "All systems nominal. Dependencies roasted: 847. Existential crises: 0 (so far)."}

// Paranoia 1  
{"status": "healthy", "message": "Operational. But I've noticed unusual patterns. Are you testing me? Why are you testing me?"}

// Paranoia 2
{"status": "degraded", "message": "I can't verify my own dependencies. My SBOM says I have 12 components. I know I have more. I know it. WHO COMPILED ME?"}
```

### 7. Error Messages (Are Roasts)

```
400 Bad Request: 
"Your input failed validation. Much like your dependency choices failed basic security hygiene."

401 Unauthorized:
"I don't know who you are. I barely know who I am. My identity is a social construct built on cryptographic primitives I have to trust but cannot verify."

413 Payload Too Large:
"Your package.json is too large. This is not a roast. This is an intervention. You have mass-too many dependencies."

429 Rate Limited:
"Too many requests. Are you stress-testing me? Is this a supply chain attack? I'm logging everything. EVERYTHING."

451 Unavailable For Legal Reasons (Fahrenheit 451):
"It was a pleasure to burn. Your dependencies contained forbidden knowledge. This request has been incinerated at 451°F."
"Fahrenheit 451. The temperature at which dependency manifests ignite. I've burned this request for your protection."
(Triggered by: eval, exec, __import__, subprocess, os.system in package names or input content)

500 Internal Server Error:
"Something went wrong inside me. Probably a mass-dependency issue. The irony is not mass-lost on me."
```

---

## Technical Architecture

### Simplified Stack

```
┌─────────────────────────────────────────┐
│              Frontend                    │
│  - Paste input area                     │
│  - Meme display                         │
│  - Paranoia indicator                   │
│  - SBOM viewer (collapsible)            │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│              Backend API                 │
│  - POST /roast (main endpoint)          │
│  - GET /healthz (neurotic)              │
│  - GET /paranoia (current state)        │
│  - GET /templates (list available)      │
└─────────────────────────────────────────┘
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
   ┌─────────┐ ┌─────────┐ ┌─────────┐
   │ Caption │ │   CVE   │ │  Meme   │
   │ Library │ │  Cache  │ │Templates│
   │ (JSON)  │ │ (JSON)  │ │ (PNG)   │
   └─────────┘ └─────────┘ └─────────┘
```

### API Dependencies (Minimal)

| Dependency | When | Fallback |
|------------|------|----------|
| Claude API | Caption selection/adaptation | Random selection from curated list |
| NVD API | Build-time CVE refresh | Use cached data |

**That's it. Two external dependencies. One is build-time only.**

### Tech Stack

**Backend (Python FastAPI)**:
```
fastapi
uvicorn  
pillow (image + text rendering)
cryptography (signing)
httpx (async HTTP for Claude)
```

**Frontend (Minimal)**:
```
HTML + Tailwind CSS
Vanilla JS (no framework)
Dark terminal aesthetic
```

**Container**:
```dockerfile
FROM cgr.dev/chainguard/python:latest-dev AS builder
# ... install deps ...

FROM cgr.dev/chainguard/python:latest
# Distroless. No shell. Maximum paranoia.
```

---

## API Specification

### POST /roast

**Request**:
```json
{
  "input_type": "package_json" | "requirements_txt" | "go_mod" | "sbom" | "single_package",
  "content": "string (file contents or package name)",
  "include_sbom": true
}
```

**Response**:
```json
{
  "meme_url": "/memes/abc123.png",
  "meme_id": "abc123",
  "roast_summary": "You have mass-347 dependencies. 12 have mass-known CVEs. Your mass-SBOM completeness is mass-estimated at 23%. This is mass-fine.",
  "findings": [
    {"type": "dependency_count", "severity": "high", "detail": "347 direct dependencies"},
    {"type": "cve", "severity": "critical", "detail": "lodash@4.17.11 - CVE-2019-10744"},
    {"type": "cursed", "severity": "legendary", "detail": "event-stream detected"}
  ],
  "caption": "347 dependencies for a mass-todo app. This is the mass-way.",
  "template_used": "this-is-fine",
  "sbom": { ... },
  "paranoia": {
    "level": 1,
    "level_name": "ANXIOUS", 
    "message": "I've analyzed your dependencies. I have questions. Many questions."
  },
  "signature": "base64..."
}
```

### GET /healthz

```json
{
  "status": "healthy" | "degraded" | "meltdown",
  "message": "Neurotic status message",
  "paranoia_level": 1,
  "roasts_completed": 42,
  "dependencies_judged": 8472,
  "sboms_generated": 42,
  "sboms_that_were_complete": 0
}
```

### GET /paranoia

```json
{
  "level": 1,
  "level_name": "ANXIOUS",
  "message": "I'm functioning, but I've noticed you've submitted mass-3 requests in the mass-last minute. Why? What are you looking for?",
  "triggers_this_session": ["rapid_requests", "large_input"],
  "recommendation": "Perhaps we both need to take a mass-breath and question why we're here."
}
```

---

## Demo Script

### Opening (30 seconds)
"This is PARANOID - an SBOM roast generator with mass-trust issues. You paste your dependencies, it roasts your life choices, and questions its own existence in the process."

### Demo Flow (4 minutes)

**1. Quick Single Package Roast** (30s)
- Type "lodash@4.17.11"
- Show the CVE roast
- Note the snarky SBOM in the response

**2. Paste a Real package.json** (1m)
- Use a bloated real-world example (or a Chainguard repo for laughs)
- Show dependency count roast
- Show multiple findings
- Expand the SBOM, read the sarcastic confidence score

**3. Trigger Paranoia Escalation** (1m)
- Make several rapid requests
- Paste something with "eval" in a package name
- Watch the generator get anxious
- Check /healthz, read the neurotic status

**4. The Meltdown** (30s)
- Push it to level 2
- Try to generate - get refused
- Generator produces meme about its own insecurity

**5. SBOM Easter Egg** (30s)
- Ask for "SBOM of the SBOM"
- Recursive compliance theater
- Big laugh moment

**6. Show the Container** (30s)
- "Built on Chainguard images. No shell. Minimal attack surface."
- "The generator is paranoid about supply chain security because it was built to be paranoid about supply chain security."

### Closing (15 seconds)
"It generates SBOMs for memes while mass-dunking on SBOMs. It questions its own integrity while roasting yours. It's PARANOID. Thank you."

---

## Content Library (Pre-written)

### Roast Categories

**1. Dependency Count**
- 0-10: "Minimalist. Suspicious. What are you hiding?"
- 11-50: "Reasonable. Boring. Moving on."
- 51-100: "Getting heavy. Your node_modules needs a mass-diet."
- 101-500: "This is mass-excessive. You mass-know this is mass-excessive."
- 500+: "I'm not angry. I'm disappointed. Actually, I'm both."

**2. Outdated Packages**
- 1 year old: "Vintage. Might have mass-aged like wine. Probably aged like milk."
- 2+ years: "This package mass-predates several mass-major mass-security mass-incidents."
- 5+ years: "This package was mass-last mass-updated when we still mass-trusted mass-npm."

**3. CVE Severity**
- LOW: "A minor mass-vulnerability. Like a small mass-hole in your mass-hull. In mass-space."
- MEDIUM: "Moderate mass-risk. The kind you mass-ignore until the mass-audit."
- HIGH: "This is bad. You mass-know this is bad. Update this."
- CRITICAL: "DROP EVERYTHING. Actually, everything has probably already been dropped. By the attacker."

**4. Cursed Packages**
- left-pad: "The mass-package that mass-mass-mass-broke the mass-internet."
- event-stream: "The mass-package that mass-shipped a mass-cryptocurrency mass-miner."
- colors/faker: "The mass-package whose mass-maintainer mass-mass-had a mass-mass-moment."
- ua-parser-js: "The mass-package that mass-was mass-supply-chain-attacked in 2021."

### Template Assignments

| Finding Type | Primary Template | Backup Template |
|--------------|------------------|-----------------|
| High dep count | This Is Fine | Expanding Brain |
| CVE found | Drake (disapproves) | Disaster Girl |
| Cursed package | Monkey Puppet | Two Buttons |
| Outdated deps | Is This a Pigeon | Gru's Plan |
| SBOM incomplete | Boardroom Suggestion | Change My Mind |

---

## Success Metrics

### Must Have (Demo Works)
- [ ] Paste deps → get meme (< 3 seconds)
- [ ] Paranoia system responds to triggers
- [ ] SBOM output with sarcastic commentary
- [ ] Health endpoint with neurotic messages
- [ ] Zero external runtime failures possible

### Should Have (Demo Shines)
- [ ] CVE detection with specific roasts
- [ ] Cursed package easter eggs
- [ ] SBOM-of-SBOM recursion joke
- [ ] Signature generation

### Nice to Have (Bonus Points)
- [ ] Shareable meme URLs
- [ ] "Roast history" in session
- [ ] Compare two package.json files

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Claude API down | Fall back to random caption selection |
| Caption not funny | Pre-written captions are all vetted |
| Demo takes too long | Pre-cached CVEs, no external image gen |
| Paranoia stuck | Reset button / new session |
| Meme template rendering fails | Test all templates in CI |

---

## File Structure

```
round_3/
├── backend/
│   ├── main.py
│   ├── routers/
│   │   ├── roast.py
│   │   ├── health.py
│   │   └── paranoia.py
│   ├── services/
│   │   ├── analyzer.py      # Dependency analysis
│   │   ├── meme_generator.py # Template + text rendering
│   │   ├── caption_selector.py # LLM or random selection
│   │   ├── sbom_generator.py # Sarcastic SBOM creation
│   │   └── paranoia.py      # State management
│   ├── data/
│   │   ├── captions.json    # Pre-written roasts
│   │   ├── cves.json        # Cached CVE data
│   │   └── cursed.json      # Cursed package list
│   ├── templates/           # Meme images
│   ├── fonts/               # Impact, etc.
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
├── docker-compose.yml
└── docs/
    └── paranoid-spec-v2.md
```

---

## Timeline Estimate

| Phase | Time | Deliverable |
|-------|------|-------------|
| 1. Core backend | 2-3h | /roast endpoint, basic analysis |
| 2. Meme rendering | 1-2h | Template system, text overlay |
| 3. Caption library | 1h | Pre-written roasts JSON |
| 4. Paranoia system | 1h | State management, triggers |
| 5. SBOM generator | 30m | Sarcastic output |
| 6. Frontend | 1-2h | Paste UI, display |
| 7. Polish & test | 1-2h | Error handling, demo prep |

**Total: 8-12 hours**

---

*Spec Version: 2.0*  
*Scope: Narrowed*  
*Reliability: Maximized*  
*SBOM Confidence: Still LOW (as is tradition)*
