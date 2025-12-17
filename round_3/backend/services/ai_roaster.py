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
# Model options: claude-sonnet-4-5-20250929, claude-haiku-4-5-20251001, claude-opus-4-5-20251101
AI_MODEL = os.environ.get("AI_MODEL", "claude-sonnet-4-5-20250929")  # Claude Sonnet 4.5


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
}


@dataclass
class AIRoastResult:
    """Result from AI roast generation."""
    roast: str
    template: str
    severity: str
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

Generate a roast that will:
1. Make security engineers snort-laugh at their desks
2. Reference specific findings when juicy (CVE IDs, package names, incidents)
3. Be quotable - something they'd paste in Slack
4. Match the severity - gentle ribbing for clean deps, existential horror for left-pad

IMPORTANT: The roast will be split across TOP and BOTTOM of a meme image.
- Write TWO short parts separated by a period: "Setup line. Punchline."
- Each part should be under 50 characters
- Example: "Log4Shell in your deps. At least you're consistent."

## MEME TEMPLATES (pick the perfect one)
{template_list}

## OUTPUT FORMAT
Return ONLY valid JSON:
{{"roast": "Your devastating roast here", "template": "template_id", "severity": "low|medium|high|critical"}}"""

    return prompt


async def generate_ai_roast(
    dep_count: int,
    package_names: list[str],
    cve_list: list[dict],
    cursed_list: list[dict]
) -> Optional[AIRoastResult]:
    """Generate a roast using Claude API.
    
    Args:
        dep_count: Number of dependencies
        package_names: List of package names
        cve_list: List of CVE dicts with package, version, cve_id, severity, description
        cursed_list: List of cursed package dicts with package, description
    
    Returns:
        AIRoastResult if successful, None if failed
    """
    if not is_ai_available():
        return None
    
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
                    "model": AI_MODEL,
                    "max_tokens": 512,
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
            
            # Validate template
            template = result.get("template", "fine")
            if template not in MEME_TEMPLATES:
                template = "fine"
            
            return AIRoastResult(
                roast=result.get("roast", "Your dependencies are concerning."),
                template=template,
                severity=result.get("severity", "medium"),
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
