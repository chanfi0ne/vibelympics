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
AI_TIMEOUT = 10  # seconds
AI_MODEL = "claude-3-haiku-20240307"  # Fast and cheap


def mask_api_key(key: str | None) -> str:
    """M-4 Security: Mask API key for safe logging."""
    if not key or len(key) < 12:
        return "***"
    return f"{key[:8]}...{key[-4:]}"


def validate_api_key_format(key: str | None) -> bool:
    """M-4 Security: Validate Anthropic API key format."""
    return bool(key and key.startswith("sk-ant-") and len(key) > 20)

# Available meme templates
MEME_TEMPLATES = {
    "fine": "This is Fine dog - denial, everything burning",
    "drake": "Drake Hotline Bling - bad vs good choices",
    "batman": "Batman Slapping Robin - stopping bad behavior",
    "buzz": "Buzz Lightyear - 'X everywhere'",
    "disaster": "Disaster Girl - watching things burn",
    "fry": "Futurama Fry - uncertainty, squinting",
    "rollsafe": "Roll Safe - bad logic, tapping head",
    "doge": "Doge - such/very/wow",
    "pigeon": "Is This a Pigeon - misidentification",
    "afraid": "I'm Afraid - nervous confession"
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
    return True


def build_prompt(
    dep_count: int,
    package_names: list[str],
    cve_list: list[dict],
    cursed_list: list[dict]
) -> str:
    """Build the prompt for Claude to generate a roast."""
    
    # Format CVEs
    cve_text = "None found"
    if cve_list:
        cve_items = [f"- {c['package']}@{c['version']}: {c['cve_id']} ({c['severity']}) - {c['description']}" 
                    for c in cve_list[:5]]
        cve_text = "\n".join(cve_items)
        if len(cve_list) > 5:
            cve_text += f"\n- ...and {len(cve_list) - 5} more"
    
    # Format cursed packages
    cursed_text = "None found"
    if cursed_list:
        cursed_items = [f"- {c['package']}: {c['description']}" for c in cursed_list]
        cursed_text = "\n".join(cursed_items)
    
    # Format package sample
    pkg_sample = ", ".join(package_names[:10])
    if len(package_names) > 10:
        pkg_sample += f" (+{len(package_names) - 10} more)"
    
    # Template list
    template_list = "\n".join([f"- {k}: {v}" for k, v in MEME_TEMPLATES.items()])
    
    prompt = f"""You are PARANOID, a sarcastic and witty supply chain security roaster. Your job is to roast people's dependencies in a funny but technically accurate way.

Analyze these dependencies and generate a brutal but entertaining roast:

DEPENDENCY SUMMARY:
- Total count: {dep_count} dependencies
- Sample packages: {pkg_sample}

CVEs DETECTED:
{cve_text}

CURSED/INFAMOUS PACKAGES:
{cursed_text}

AVAILABLE MEME TEMPLATES:
{template_list}

Generate a roast that:
1. Is 2-3 sentences max
2. References specific packages or CVEs when relevant
3. Is sarcastic but not mean-spirited
4. Would make a security engineer laugh (or cry)

Also select the most appropriate meme template based on the findings.

Respond with ONLY valid JSON in this exact format:
{{"roast": "Your roast here", "template": "template_id", "severity": "low|medium|high|critical"}}"""

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
                    "max_tokens": 256,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ]
                }
            )
            
            if response.status_code != 200:
                # M-4 Security: Log error without exposing full response (may contain key info)
                logger.warning(f"AI API error: status={response.status_code}")
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
