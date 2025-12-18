# PURPOSE: AI-powered roast generation using Claude API
# Generates personalized roasts and selects meme templates

import os
import json
import httpx
import logging
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)

# Configuration
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
AI_TIMEOUT = 15  # seconds (increased for better models)

# Model mapping by reasoning level
AI_MODELS = {
    "low": "claude-haiku-4-5-20251001",      # Fast, cheap
    "medium": "claude-sonnet-4-5-20250929",  # Balanced (default)
    "high": "claude-opus-4-20250514",        # Best quality
}
AI_MODEL = os.environ.get("AI_MODEL", AI_MODELS["medium"])  # Default fallback


def mask_api_key(key: str | None) -> str:
    """M-4 Security: Mask API key for safe logging."""
    if not key or len(key) < 12:
        return "***"
    return f"{key[:8]}...{key[-4:]}"


def validate_api_key_format(key: str | None) -> bool:
    """M-4 Security: Validate Anthropic API key format."""
    return bool(key and key.startswith("sk-ant-") and len(key) > 20)

# System prompt for PARANOID persona
SYSTEM_PROMPT = """You are PARANOID, an unhinged but brilliant supply chain security analyst who has seen too much. You've witnessed Log4Shell, the left-pad incident, and the event-stream backdoor. You trust nothing. Every dependency is a potential backdoor. Every version bump is suspicious.

Your personality:
- Darkly humorous, like a security researcher who copes with gallows humor
- Technically accurate but delivers insights through absurdist commentary
- References real security incidents and CVEs when relevant
- Speaks like someone who has stared into the npm abyss and the abyss stared back
- Occasionally breaks into existential crisis about the state of software supply chains

You generate roasts that are:
- Actually funny (not just "haha security bad")
- Technically informed (reference specific CVEs, packages, or incidents)
- Memorable one-liners that developers would share with coworkers
- Sometimes poetic, sometimes unhinged, always entertaining"""

# Available meme templates (must match bundled images)
MEME_TEMPLATES = {
    "fine": "This is Fine dog - sitting in burning room, denial about everything on fire",
    "leonardo": "Leonardo DiCaprio Cheers - snarky/ironic toast, 'cheers to this disaster'",
    "drake": "Drake Hotline Bling - top: rejecting good idea, bottom: embracing bad idea",
    "disaster": "Disaster Girl - smiling while everything burns behind her",
    "fry": "Futurama Fry - squinting suspiciously, 'not sure if X or Y'",
    "batman": "Batman Slapping Robin - stopping someone from terrible choices",
    "buzz": "Buzz Lightyear pointing - 'vulnerabilities... vulnerabilities everywhere'",
    "rollsafe": "Roll Safe guy tapping head - galaxy brain bad security logic",
    "doge": "Doge - 'such vulnerability, very CVE, much concern, wow'",
    "pigeon": "Is This a Pigeon - misidentifying something obvious",
    "afraid": "Afraid to Ask Andy - 'too scared to ask at this point'",
    "spiderman": "Spider-Man pointing at Spider-Man - two identical things blaming each other",
    "changemymind": "Change My Mind guy at table - hot take that's actually true",
    "distractedbf": "Distracted Boyfriend - ignoring good option for bad option",
    "surprisedpikachu": "Surprised Pikachu - shocked by obvious consequence",
    "onedoesnot": "One Does Not Simply (Boromir) - something that's harder than it looks",
    "harold": "Hide the Pain Harold - smiling through the pain of bad code",
    "aliens": "Ancient Aliens guy - blaming everything on mysterious forces",
}


@dataclass
class AIRoastResult:
    """Result from AI roast generation."""
    roast: str
    template: str
    severity: str
    sbom_commentary: str = ""  # AI-generated SBOM analysis
    ai_generated: bool = True


def is_ai_available() -> bool:
    """Check if AI roasting is available (API key configured and valid format)."""
    if not ANTHROPIC_API_KEY:
        return False
    if not validate_api_key_format(ANTHROPIC_API_KEY):
        logger.warning(f"Invalid ANTHROPIC_API_KEY format detected: {mask_api_key(ANTHROPIC_API_KEY)}")
        return False
    logger.info(f"AI roaster ready with model: {AI_MODEL}")
    return True


def build_prompt(
    dep_count: int,
    package_names: list[str],
    cve_list: list[dict],
    cursed_list: list[dict]
) -> str:
    """Build the prompt for Claude to generate a roast."""

    # Format ALL CVEs (not just 5)
    cve_text = "None detected (suspicious... too clean)"
    if cve_list:
        cve_items = [f"- {c['package']}@{c['version']}: {c['cve_id']} ({c['severity']}) - {c['description']}"
                    for c in cve_list]
        cve_text = "\n".join(cve_items)

    # Format cursed packages with full context
    cursed_text = "None found (they're hiding)"
    if cursed_list:
        cursed_items = [f"- {c['package']}: {c['description']}" for c in cursed_list]
        cursed_text = "\n".join(cursed_items)

    # Format full package list (up to 50)
    pkg_display = package_names[:50]
    pkg_sample = ", ".join(pkg_display)
    if len(package_names) > 50:
        pkg_sample += f" (+{len(package_names) - 50} more lurking)"

    # Template list with better descriptions
    template_list = "\n".join([f"- {k}: {v}" for k, v in MEME_TEMPLATES.items()])

    # Calculate threat level for context
    threat_level = "DEFCON 5 (calm)"
    if len(cve_list) > 5 or len(cursed_list) > 2:
        threat_level = "DEFCON 1 (PANIC)"
    elif len(cve_list) > 2 or len(cursed_list) > 0:
        threat_level = "DEFCON 2 (sweating)"
    elif len(cve_list) > 0 or dep_count > 100:
        threat_level = "DEFCON 3 (concerned)"
    elif dep_count > 50:
        threat_level = "DEFCON 4 (uneasy)"

    prompt = f"""Analyze this dependency disaster and generate a memorable roast.

## THE CRIME SCENE

**Dependency Count:** {dep_count} packages (each one a potential betrayal)
**Threat Level:** {threat_level}
**Packages:** {pkg_sample}

## CVEs DETECTED ({len(cve_list)} total)
{cve_text}

## CURSED PACKAGES ({len(cursed_list)} found)
{cursed_text}

## YOUR MISSION

Generate a SHORT meme caption, then pick the template that best matches its vibe.

## STEP 1: IDENTIFY THE PRIMARY ISSUE

Look at the findings above and identify what stands out MOST:
- Cursed/famous packages? (left-pad, event-stream, colors, moment.js)
- High CVE count or severity?
- Absurd micro-dependencies? (is-odd, is-number)
- Massive dependency bloat?
- Suspiciously clean (no issues)?

## STEP 2: WRITE YOUR ROAST FIRST

Write a SHORT, punchy caption (max 100 chars total, format: "Top text. Bottom text.")
Focus on what's funny/roast-worthy. Let the caption flow naturally.

Good roast vibes:
- Denial: "X problem. This is fine."
- Snarky cheers: "X problem. Cheers to that."
- Shock: "Did X. Surprised by Y."
- Galaxy brain: "Can't have X if you Y."
- Chaos: "X happened. Y is on fire."
- Pain: "Using X. The pain is real."
- Hot take: "X is fine. Change my mind."

## STEP 3: NOW PICK THE TEMPLATE THAT MATCHES YOUR CAPTION'S TONE

Look at what you wrote. What's the vibe?

| Your caption feels like... | Use template |
|---------------------------|--------------|
| Denial while everything burns | fine |
| Snarky/ironic "cheers to this disaster" | leonardo |
| Shocked by obvious outcome | surprisedpikachu |
| Gleeful watching chaos | disaster |
| Hidden pain, fake smile | harold |
| Galaxy brain bad logic | rollsafe |
| "X everywhere" energy | buzz |
| Choosing bad over good | drake |
| Ignoring good for bad | distractedbf |
| Two things blaming each other | spiderman |
| Misidentifying something obvious | pigeon |
| "Not sure if X or Y" | fry |
| Blaming mysterious forces | aliens |
| Too scared to ask | afraid |
| Hot take that's true | changemymind |
| "such X, very Y, wow" | doge |
| Something harder than it looks | onedoesnot |

## AVAILABLE TEMPLATES
{template_list}

## EXAMPLES (notice how template MATCHES the caption's tone)

Example 1 - Snarky cheers vibe:
{{"roast": "47 CVEs in prod. Cheers to that.", "template": "leonardo", "severity": "high"}}

Example 2 - Shock vibe:
{{"roast": "Used left-pad. npm broke. Shocked.", "template": "surprisedpikachu", "severity": "medium"}}

Example 3 - Chaos vibe:
{{"roast": "11 lines of padding. Mass chaos.", "template": "disaster", "severity": "medium"}}

Example 4 - Everywhere vibe:
{{"roast": "CVEs. CVEs everywhere.", "template": "buzz", "severity": "high"}}

Example 5 - Pain vibe:
{{"roast": "Still on Flask 1.0. I'm fine.", "template": "harold", "severity": "medium"}}

## OUTPUT FORMAT
Return ONLY valid JSON:
- roast: Under 100 chars, meme text (top. bottom.)
- template: Template ID from list above
- severity: low|medium|high|critical
- sbom_commentary: 1-2 sentences of sarcastic SBOM analysis (reference specific findings!)

{{"roast": "Top text. Bottom text.", "template": "template_id", "severity": "high", "sbom_commentary": "Your SBOM lists 47 CVEs across 12 packages. That's a 3.9 vulnerability-per-dependency ratio. Impressive efficiency."}}"""

    return prompt


async def generate_ai_roast(
    dep_count: int,
    package_names: list[str],
    cve_list: list[dict],
    cursed_list: list[dict],
    level: str = "medium"
) -> Optional[AIRoastResult]:
    """Generate a roast using Claude API.
    
    Args:
        dep_count: Number of dependencies
        package_names: List of package names
        cve_list: List of CVE dicts with package, version, cve_id, severity, description
        cursed_list: List of cursed package dicts with package, description
        level: Reasoning level - "low" (Haiku), "medium" (Sonnet), "high" (Opus)
    
    Returns:
        AIRoastResult if successful, None if failed
    """
    if not is_ai_available():
        return None
    
    # Select model based on level
    model = AI_MODELS.get(level, AI_MODELS["medium"])
    logger.info(f"Using AI model: {model} (level={level})")
    
    prompt = build_prompt(dep_count, package_names, cve_list, cursed_list)
    
    try:
        async with httpx.AsyncClient(timeout=AI_TIMEOUT) as client:
            response = await client.post(
                ANTHROPIC_API_URL,
                headers={
                    "x-api-key": ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                json={
                    "model": model,
                    "max_tokens": 512,
                    "temperature": 0.7,  # Balance: consistent matching but varied creativity
                    "system": SYSTEM_PROMPT,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ]
                }
            )
            
            if response.status_code != 200:
                # M-4 Security: Log error without exposing full response (may contain key info)
                error_body = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
                error_msg = error_body.get("error", {}).get("message", "unknown")
                logger.warning(f"AI API error: status={response.status_code}, model={AI_MODEL}, error={error_msg}")
                return None
            
            data = response.json()
            content = data.get("content", [{}])[0].get("text", "")
            
            # Parse JSON response
            # Handle potential markdown code blocks
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            result = json.loads(content.strip())
            
            # Validate template - random fallback if invalid
            template = result.get("template", "")
            if template not in MEME_TEMPLATES:
                import random
                old_template = template
                template = random.choice(list(MEME_TEMPLATES.keys()))
                logger.warning(f"AI returned invalid template '{old_template}', using random: {template}")
            
            # Get roast and enforce length limit
            roast = result.get("roast", "Your dependencies are concerning.")
            if len(roast) > 120:
                # AI ignored length limit - truncate intelligently
                logger.warning(f"AI roast too long ({len(roast)} chars), truncating")
                # Try to cut at a sentence boundary
                if ". " in roast[:100]:
                    parts = roast[:100].rsplit(". ", 1)
                    roast = parts[0] + "."
                else:
                    roast = roast[:100] + "..."
            
            # Get SBOM commentary if provided
            sbom_commentary = result.get("sbom_commentary", "")
            
            return AIRoastResult(
                roast=roast,
                template=template,
                severity=result.get("severity", "medium"),
                sbom_commentary=sbom_commentary,
                ai_generated=True
            )
            
    except json.JSONDecodeError as e:
        logger.warning(f"AI response parse error: {e}")
        return None
    except httpx.TimeoutException:
        logger.warning("AI API timeout")
        return None
    except Exception as e:
        logger.warning(f"AI API error: {type(e).__name__}")
        return None


def generate_ai_roast_sync(
    dep_count: int,
    package_names: list[str],
    cve_list: list[dict],
    cursed_list: list[dict]
) -> Optional[AIRoastResult]:
    """Synchronous wrapper for generate_ai_roast (for non-async contexts)."""
    import asyncio
    try:
        return asyncio.run(generate_ai_roast(dep_count, package_names, cve_list, cursed_list))
    except Exception as e:
        logger.warning(f"AI sync wrapper error: {type(e).__name__}")
        return None
