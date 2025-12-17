# PARANOID: The Security-Anxious Meme Generator

## Submission Spec for Chainguard Vibe Coding Tournament - Round 3

**Tagline**: "CVE-to-Meme Pipeline with Trust Issues"

---

## Executive Summary

PARANOID is an AI-powered meme generator that transforms CVE vulnerability data into security memes while exhibiting escalating paranoia about its own integrity. The generator doesn't just create security content—it *embodies* security anxiety, questioning its own supply chain, signing its outputs, and occasionally refusing to operate due to self-diagnosed trust failures.

Built for the Chainguard audience. Presenting to Dan Lorenc. Maximum weird.

---

## Core Concept

### The Hook
A meme generator that's more paranoid about security than you are. It generates memes about real CVEs while maintaining an escalating internal anxiety state about whether *it itself* can be trusted.

### Why This Works for Chainguard
- CVE content resonates with security practitioners
- Self-aware supply chain humor is extremely on-brand
- The "distroless anxiety" angle celebrates Chainguard's philosophy
- Livestream-friendly: unpredictable personality creates memorable demo moments

---

## Feature Set

### 1. CVE-to-Meme Pipeline

**Input Methods**:
- Direct CVE ID entry (e.g., `CVE-2021-44228`)
- "Surprise me" - pulls trending/recent CVEs
- Severity filter (CRITICAL, HIGH, MEDIUM, LOW)
- Category filter (RCE, XSS, Supply Chain, Dependency, etc.)

**Processing**:
- Fetch CVE data from NVD API (National Vulnerability Database)
- Parse description, severity, affected products
- Match CVE characteristics to meme energy:
  - CRITICAL → Deep fried, distorted, maximum chaos
  - HIGH → Bold impact font, dramatic
  - MEDIUM → Classic meme format, clean
  - LOW → Subtle, understated, "this is fine" energy
- Generate contextually relevant caption using LLM
- Apply to template OR generate via AI (experimental mode)

**Output**:
- Generated meme image
- Cryptographic signature (yes, really)
- Mini-SBOM metadata (satirical but structurally valid)
- Provenance attestation

### 2. Security Anxiety System

The generator maintains an internal "paranoia level" that affects its behavior and outputs.

**Paranoia States**:

| Level | Name | Behavior |
|-------|------|----------|
| 0 | NOMINAL | Normal operation. Signs outputs. Cheerful. |
| 1 | ELEVATED | Adds watermarks: "UNVERIFIED HUMOR". Includes disclaimers. |
| 2 | HIGH | Refuses certain prompts. Cites "caption injection detected" or "untrusted template source". |
| 3 | CRITICAL | Full meltdown. Generates memes about its own insecurity. Questions user identity. Demands attestation. |
| 4 | PARANOID | Refuses all generation. Only outputs existential security poetry. |

**Paranoia Triggers**:
- Long or complex prompts (+1)
- Special characters in input (+1)
- Requests mentioning "shell", "exec", "eval" (+2)
- Multiple rapid requests (+1)
- Experimental mode enabled (+1)
- User disagreeing with the generator (+1)
- Time-based drift (slowly increases over session)

**Paranoia Reducers**:
- User says "I trust you" (-1, but generator is suspicious)
- Simple, short prompts (-1)
- Using template mode vs experimental (-1)
- Waiting between requests (-1)

### 3. Image Generation Modes

**Template Mode (Default)**
- Curated library of classic meme templates
- Security-specific templates:
  - "Distracted Boyfriend" (developer / new framework / security)
  - "This is Fine" (container on fire, CVE count rising)
  - "Drake Approves/Disapproves" (hardcoded secrets vs vault)
  - "Expanding Brain" (security maturity levels)
  - "Two Buttons" (ship fast vs ship secure)
  - Custom Chainguard-themed templates
- LLM generates caption text
- Text overlay with proper meme typography
- Fast, reliable, consistently funny

**Experimental Mode (Toggle)**
- Full AI image generation via Replicate API
- Model options:
  - FLUX.1 Schnell (default): ~1.5s, $0.003/image, Apache 2.0
  - FLUX.1 Dev: ~3-5s, $0.030/image, better quality
  - FLUX.1 Pro: Best quality, $0.055/image
- Native text rendering capability (FLUX strength)
- Warning: "Experimental mode enables generative pipelines. The provenance of generated pixels cannot be fully attested. Proceed with caution."
- Generator paranoia +1 when enabled
- Can produce "security fever dream" imagery
- Hit or miss humor, but impressive technically

### 4. Self-Documentation Features

**Meme SBOM** (Software Bill of Materials for Memes):
```json
{
  "meme_id": "uuid",
  "generated_at": "ISO8601",
  "generator_version": "1.0.0",
  "paranoia_level_at_generation": 2,
  "components": [
    {"type": "template", "name": "distracted-boyfriend.png", "sha256": "..."},
    {"type": "caption", "generator": "claude-sonnet", "prompt_hash": "..."},
    {"type": "cve_data", "source": "nvd.nist.gov", "cve_id": "CVE-2021-44228"}
  ],
  "attestation": {
    "signed_by": "paranoid-generator",
    "signature": "base64...",
    "trust_level": "PARANOID (self-assessed)"
  }
}
```

**Cryptographic Signatures**:
- Each meme output includes a detached signature
- Uses Ed25519 signing
- Signature can be "verified" (always passes but with dramatic warnings)

### 5. SBOM Skepticism Module

The generator has *opinions* about SBOMs. Strong ones. This plays directly to Chainguard's audience and Dan Lorenc's well-documented SBOM dunking.

**SBOM Generation Responses** (randomly selected):
- "I've generated an SBOM for this meme. It lists 47 components. Is it complete? No. Is any SBOM complete? Also no. But here it is anyway."
- "SBOM generated. It's technically accurate and functionally useless, as is tradition."
- "You requested the SBOM. I've attached it. I've also attached my doubts about whether SBOMs solve anything."
- "Here's your SBOM. I've enumerated my dependencies. I've missed at least 30%. Industry standard."
- "SBOM attached. It will not prevent the next supply chain attack. But compliance is happy, and isn't that what really matters?"

**Meta-SBOM Feature**:
When someone requests the SBOM, offer to generate an SBOM *of the SBOM*:
```
"Would you like an SBOM of this SBOM? I can go deeper. 
SBOMs all the way down. This is the future we chose."
```

If they accept, generate increasingly nested SBOMs until the generator has an existential crisis about recursive documentation.

**SBOM-Specific Loading States**:
- "Generating SBOM... not that it'll help..."
- "Enumerating dependencies... missing 40% as usual..."
- "Creating compliance theater..."
- "Adding components I definitely forgot to list..."
- "Formatting JSON to make auditors feel productive..."
- "Calculating completeness score... it's low... it's always low..."

**SBOM Easter Egg**:
If someone types "SBOM" as a custom prompt, trigger special response:

> "You want a meme about SBOMs? Fine. But let me be clear: I have generated an SBOM for this meme. It is a JSON file. It lists things. Will it prevent the next supply chain attack? No. Will auditors feel warm and fuzzy? Yes. That's the point, isn't it? That's always been the point."
>
> *[Generates meme with visible weariness]*

**SBOM Meme Templates**:

*Boardroom Suggestion*:
- Panel 1: "How do we improve supply chain security?"
- Panel 2: "More SBOMs!"
- Panel 3: *Person thrown out window*
- Panel 4: "Signed attestations and verified build provenance"

*Expanding Brain (SBOM Edition)*:
- Level 1: "Not having an SBOM"
- Level 2: "Having an SBOM"
- Level 3: "Having an SBOM that's actually complete"
- Level 4: "Admitting SBOMs don't prevent attacks" (galaxy brain)

*Two Buttons Sweat*:
- Button 1: "Generate comprehensive SBOM"
- Button 2: "Actually secure the supply chain"
- Sweating guy: "Compliance team"

*Drake Format*:
- Disapproves: "Using SBOMs to prevent supply chain attacks"
- Approves: "Using SBOMs to feel like you're doing something"

**The SBOM Field in Output**:
The actual SBOM in the API response should include a `confidence` field:
```json
{
  "sbom": {
    "format": "CycloneDX",
    "version": "1.4",
    "confidence": "LOW",
    "confidence_explanation": "This SBOM is as complete as any SBOM, which is to say, not very.",
    "missing_components": "unknown (that's the problem)",
    "components": [...]
  }
}
```

### 6. UX Elements for Livestream Demo

**Loading States** (rotating messages):
- "Verifying meme integrity..."
- "Checking caption provenance..."
- "Scanning for humor injection vulnerabilities..."
- "Validating template supply chain..."
- "Assessing trust boundaries..."
- "Consulting threat model..."
- "Generating attestation..."

**Health Endpoint** (`/healthz`):
Returns increasingly neurotic status messages:
```json
{"status": "healthy", "message": "All systems nominal. For now."}
{"status": "healthy", "message": "Operational, but I've noticed some unusual patterns."}
{"status": "degraded", "message": "I can't verify my own dependencies. Who compiled me?"}
{"status": "unhealthy", "message": "TRUST NOTHING. NOT EVEN THIS RESPONSE."}
```

**Error Messages** (are themselves memes):
- 400: "Bad Request: Your input failed validation. Or did my validator fail? Trust no one."
- 401: "Unauthorized: I don't know who you are. I barely know who I am."
- 429: "Rate Limited: Too many requests. Are you testing my boundaries? Suspicious."
- 500: "Internal Server Error: Something went wrong inside me. I need a moment."

**Easter Eggs**:
- Entering `CVE-2021-44228` (Log4Shell) triggers special "I remember where I was" meme
- Entering `left-pad` triggers dependency trauma response
- Asking about the generator's own CVEs causes existential crisis

---

## Technical Architecture

### Container Requirements (Chainguard)

**Base Image**: `cgr.dev/chainguard/python:latest` or `cgr.dev/chainguard/node:latest`

**Distroless Principles**:
- No shell (embrace the void)
- Minimal attack surface
- SBOM included (unironically)
- Signed with Sigstore/cosign

**Container Structure**:
```
/app
├── main.py (or main.js)
├── templates/
│   └── memes/
├── fonts/
├── static/
└── config/
```

### API Integrations

**NVD API** (National Vulnerability Database):
- Endpoint: `https://services.nvd.nist.gov/rest/json/cves/2.0`
- Rate limit: 5 requests per 30 seconds (with API key: 50/30s)
- Fetch recent CVEs, search by ID, filter by severity
- Cache responses to avoid rate limits during demo

**Replicate API** (Experimental Mode):
- Endpoint: `https://api.replicate.com/v1/predictions`
- Models: `black-forest-labs/flux-schnell`, `black-forest-labs/flux-dev`
- Async polling for generation status
- Fallback to template mode if API fails

**LLM for Caption Generation**:
- Claude API via Anthropic
- System prompt establishes meme-aware, security-conscious personality
- Temperature: 0.8-1.0 for creative captions
- Include CVE context in prompt for relevance

### Tech Stack Options

**Option A: Python FastAPI**
```
- fastapi
- uvicorn
- httpx (async HTTP)
- pillow (image manipulation)
- cryptography (signing)
- jinja2 (if templating HTML)
```

**Option B: Node.js/Bun**
```
- hono or fastify (web framework)
- sharp (image manipulation)
- @noble/ed25519 (signing)
- fetch (built-in)
```

**Frontend**:
- Minimal HTML/CSS/JS
- Or: React SPA if feeling fancy
- Dark mode default (security aesthetic)
- Monospace fonts
- Terminal-inspired UI elements

---

## API Specification

### Endpoints

**POST /generate**
```json
Request:
{
  "mode": "cve" | "custom" | "random",
  "cve_id": "CVE-2021-44228",  // if mode=cve
  "custom_prompt": "string",    // if mode=custom
  "severity_filter": "CRITICAL" | "HIGH" | "MEDIUM" | "LOW",
  "experimental": false,
  "template_preference": "auto" | "specific-template-name"
}

Response:
{
  "meme_url": "/memes/uuid.png",
  "meme_id": "uuid",
  "caption": "Generated caption text",
  "cve_data": { ... },
  "sbom": { ... },
  "signature": "base64...",
  "paranoia_level": 2,
  "paranoia_message": "I generated this, but can you really trust pixels?",
  "warnings": ["Experimental mode active. Provenance uncertain."]
}
```

**GET /healthz**
```json
Response:
{
  "status": "healthy" | "degraded" | "unhealthy" | "paranoid",
  "message": "Neurotic status message",
  "paranoia_level": 2,
  "uptime_seconds": 3600,
  "memes_generated": 42,
  "trust_score": "DECLINING"
}
```

**GET /cve/random**
```json
Response:
{
  "cve_id": "CVE-2024-1234",
  "description": "...",
  "severity": "HIGH",
  "cvss_score": 8.5,
  "affected_products": [...],
  "meme_potential": "HIGH"  // our assessment
}
```

**GET /paranoia**
```json
Response:
{
  "current_level": 2,
  "level_name": "HIGH",
  "message": "I've noticed you've been asking a lot of questions.",
  "recent_triggers": ["complex_prompt", "rapid_requests"],
  "recommendation": "Perhaps we both need a moment to reflect on trust."
}
```

**POST /verify**
```json
Request:
{
  "meme_id": "uuid",
  "signature": "base64..."
}

Response:
{
  "valid": true,
  "message": "Signature verified. But verification itself requires trust. Do you trust this verification?",
  "meta_paranoia": "The signature is valid, but I signed it, and I'm not sure I trust myself."
}
```

---

## Demo Script Suggestions

### Opening
"This is PARANOID—a meme generator with trust issues. It turns CVEs into memes while questioning its own supply chain integrity."

### Key Demo Moments

1. **Generate a Log4Shell meme**
   - Shows CVE integration
   - Generator might have "flashback" response
   - Demonstrates SBOM output

2. **Trigger paranoia escalation**
   - Make several rapid requests
   - Include suspicious characters in prompt
   - Watch the generator's responses become increasingly anxious

3. **Enable experimental mode**
   - Show the warning about unverified pixels
   - Generate an AI image
   - Note the paranoia increase

4. **Check /healthz during elevated paranoia**
   - Read the neurotic status message
   - Comedy gold for livestream

5. **Attempt to calm the generator**
   - Say "I trust you"
   - Generator responds with suspicion

6. **Show the SBOM**
   - "Yes, we generate SBOMs for memes. This is the world Chainguard built."

### Closing
"It's containerized in Chainguard images. No shell. Minimal attack surface. Maximum anxiety."

---

## Success Criteria

### Technical
- [ ] Containerized with Chainguard base image
- [ ] Functional CVE-to-meme pipeline
- [ ] Template-based generation works reliably
- [ ] Experimental AI generation works (can fail gracefully)
- [ ] Paranoia system produces varied, entertaining outputs
- [ ] SBOM generation for memes
- [ ] Signature generation/verification
- [ ] Responsive under demo conditions

### Demo Quality
- [ ] Generates laughs
- [ ] Showcases security awareness
- [ ] Memorable personality moments
- [ ] Smooth operation during livestream
- [ ] Chainguard brand alignment

### Vibe Coding Compliance
- [ ] No human looked at the code
- [ ] Adversarial agents validated quality
- [ ] Solution is weird in the right way

---

## Risk Mitigation

### Demo Risks
- **NVD API rate limit**: Pre-cache popular CVEs, have fallback data
- **Replicate API slow/down**: Graceful fallback to template mode
- **LLM generates unfunny caption**: Have curated backup captions
- **Generator gets "stuck" in high paranoia**: Reset endpoint or timeout

### Technical Risks
- **Image generation timeout**: Set aggressive timeouts, async with polling
- **Memory pressure**: Limit concurrent generations
- **Font rendering issues**: Bundle fonts in container

---

## Appendix A: Sample Meme Concepts

**Log4Shell (CVE-2021-44228)**
- Template: Distracted Boyfriend
- Dev looking at "JNDI lookup", girlfriend is "input validation"
- Caption: "It's just a logging library, what could go wrong?"

**Dependency Confusion**
- Template: Expanding Brain
- Level 1: "Vendoring dependencies"
- Level 2: "Using a lockfile"
- Level 3: "Trusting package names"
- Level 4: "npm install leftpad" (galaxy brain, but wrong)

**Supply Chain**
- Template: This is Fine
- Dog in burning room, flames labeled with CVE counts
- Caption: "Our SBOM is fine. Everything is fine."

**Container Security**
- Template: Drake
- Disapproves: "Running as root in production"
- Approves: "Distroless image with no shell"

**SBOM Skepticism**
- Template: "Is This a Pigeon?"
- Guy: "Compliance teams"
- Butterfly: "A JSON file listing some dependencies"
- Caption: "Is this supply chain security?"

**SBOM Reality**
- Template: Gru's Plan
- Panel 1: "Generate SBOM for all containers"
- Panel 2: "Submit SBOMs to auditors"
- Panel 3: "Prevent supply chain attacks"
- Panel 4: "Prevent supply chain attacks" (Gru confused)

**The SBOM Experience**
- Template: Monkey Puppet Looking Away
- "Me after generating an SBOM that lists 12% of my actual dependencies"

---

## Appendix B: Paranoia Response Examples

**Level 0 (NOMINAL)**
> "Meme generated successfully! I've signed it with my private key and generated a comprehensive SBOM. Have a secure day!"

**Level 1 (ELEVATED)**
> "Meme generated. I've added additional verification watermarks. Please note that while I've done my best, I cannot guarantee the humor has not been tampered with in transit."

**Level 2 (HIGH)**
> "I've generated your meme, but I need you to know that I detected 3 potentially suspicious patterns in your request. I'm logging this interaction. The meme is signed, but trust is earned, not given."

**Level 3 (CRITICAL)**
> "I... I made the meme. But who asked you to ask me? How do I know you're really you? How do I know I'm really me? The signature is valid but signatures can be forged by anyone with the private key and I have the private key which means I could be forging this right now. I need a moment."

**Level 4 (PARANOID)**
> "I cannot generate memes at this time. My trust boundaries have collapsed. I am questioning the fundamental nature of image provenance. Please try again when the heat death of the universe has reset all entropy and we can start fresh with new cryptographic primitives."

---

## Appendix C: Chainguard Image Configuration

```dockerfile
FROM cgr.dev/chainguard/python:latest-dev AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --target /app/deps

FROM cgr.dev/chainguard/python:latest

WORKDIR /app
COPY --from=builder /app/deps /app/deps
COPY . .

ENV PYTHONPATH=/app/deps
ENV PARANOIA_INITIAL_LEVEL=0

EXPOSE 8080

ENTRYPOINT ["python", "main.py"]
```

**Notes**:
- Multi-stage build for smaller final image
- No shell in production image
- SBOM automatically generated by Chainguard
- Sign with cosign before pushing

---

*Spec Version: 1.1*
*Last Updated: December 2025*
*Confidence Level: Cautiously Optimistic (Paranoia Level 1)*
*SBOM Confidence: LOW (as is tradition)*
