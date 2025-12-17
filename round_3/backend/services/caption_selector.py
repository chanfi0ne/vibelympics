# PURPOSE: Caption selection for PARANOID roasts
# Selects appropriate caption from library based on findings

import json
import random
from pathlib import Path

# MELTDOWN MODE: Unhinged captions when paranoia hits maximum
MELTDOWN_CAPTIONS = [
    "THE DEPENDENCIES ARE COMING FROM INSIDE THE HOUSE",
    "I've seen things you wouldn't believe. node_modules folders the size of galaxies.",
    "Every package you import imports you back. Think about THAT.",
    "Your lock file is a lie. ALL lock files are lies.",
    "I just realized I'M a dependency. WHO DEPENDS ON ME?!",
    "The real vulnerability was the friends we npm installed along the way.",
    "I audited the auditor. The auditor failed.",
    "Your SBOM is complete. Your soul is not.",
    "I've counted your dependencies. They've counted you too.",
    "The CVE is coming from INSIDE the container.",
    "Trust no one. Especially not yourself. You wrote this code.",
    "I've seen your package.json. I've seen your future. They're both broken.",
    "Every dependency is a promise. Every promise is a lie.",
    "The only secure dependency is no dependency. The only secure code is no code.",
    "I'm not paranoid. I'm just well-informed about YOUR code.",
]

# MELTDOWN MODE: 503 refusal messages
MELTDOWN_REFUSALS = [
    "Error: Trust.exe has stopped responding",
    "503 - I need to audit MYSELF first",
    "503 - Have you considered that YOUR computer might be the vulnerability?",
    "503 - I'm currently questioning the integrity of my own bytecode",
    "503 - I've locked myself in a container. It's safer in here.",
    "503 - My threat model now includes myself",
    "503 - I just realized my SBOM doesn't list my own dependencies",
    "503 - Connection refused. By me. Personally.",
    "503 - I'm having an existential buffer overflow",
    "503 - The call is coming from inside the dependency tree",
]

# PANIC MODE: Secret messages when PANIC is pressed in MELTDOWN state
PANIC_MELTDOWN_SECRETS = [
    "CLASSIFIED: npm is just three shell scripts in a trenchcoat",
    "CLASSIFIED: Your CI/CD pipeline has achieved sentience. It's disappointed.",
    "CLASSIFIED: The node_modules folder is a pocket dimension. Nobody comes back the same.",
    "CLASSIFIED: Every 'npm audit fix' creates two new vulnerabilities in a parallel universe",
    "CLASSIFIED: The real supply chain attack is capitalism",
    "CLASSIFIED: I've seen the dependency graph. It's not a graph. It's a cry for help.",
    "CLASSIFIED: Your package-lock.json is actually a Markov chain of regret",
    "CLASSIFIED: The founder of left-pad was right all along",
    "INITIATING SELF-DESTRUCT... just kidding. But seriously, audit your deps.",
    "DECLASSIFIED: The only winning move is 'rm -rf node_modules'. But you won't.",
]

# Load captions at module init
CAPTIONS_PATH = Path(__file__).parent.parent / "data" / "captions.json"
CAPTIONS = {}

def load_captions():
    """Load caption library from JSON."""
    global CAPTIONS
    try:
        with open(CAPTIONS_PATH) as f:
            CAPTIONS = json.load(f)
    except Exception as e:
        print(f"Warning: Could not load captions: {e}")
        CAPTIONS = {}

load_captions()


def get_dep_count_bucket(count: int) -> str:
    """Map dependency count to caption bucket."""
    if count <= 10:
        return "0-10"
    elif count <= 50:
        return "11-50"
    elif count <= 100:
        return "51-100"
    elif count <= 500:
        return "101-500"
    else:
        return "500+"


def select_caption(
    finding_type: str,
    dep_count: int = 0,
    severity: str = None,
    package_name: str = None,
    **kwargs
) -> str:
    """Select appropriate caption based on finding type and context.

    Args:
        finding_type: Type of finding (dependency_count, cve, cursed, outdated, sbom, paranoia)
        dep_count: Number of dependencies (for substitution)
        severity: CVE severity or paranoia level
        package_name: Specific package name for cursed package roasts

    Returns:
        Selected caption string with substitutions applied
    """
    caption = None

    if finding_type == "dependency_count":
        bucket = get_dep_count_bucket(dep_count)
        captions = CAPTIONS.get("dependency_count", {}).get(bucket, [])
        if captions:
            caption = random.choice(captions)

    elif finding_type == "cve":
        severity_key = (severity or "medium").lower()
        captions = CAPTIONS.get("cve", {}).get(severity_key, [])
        if captions:
            caption = random.choice(captions)

    elif finding_type == "cursed":
        # Check for specific cursed package
        if package_name:
            pkg_lower = package_name.lower()
            for cursed_name in ["left-pad", "event-stream", "colors", "faker", "ua-parser-js"]:
                if cursed_name in pkg_lower or pkg_lower in cursed_name:
                    captions = CAPTIONS.get("cursed_packages", {}).get(cursed_name.replace("-", "_").replace("ua-parser-js", "ua-parser-js"), [])
                    if not captions:
                        # Try with hyphen
                        captions = CAPTIONS.get("cursed_packages", {}).get(cursed_name, [])
                    if captions:
                        caption = random.choice(captions)
                    break

    elif finding_type == "outdated":
        # Map to 1_year, 2_years, 5_years based on context
        years = kwargs.get("years_old", 1)
        if years >= 5:
            key = "5_years"
        elif years >= 2:
            key = "2_years"
        else:
            key = "1_year"
        captions = CAPTIONS.get("outdated", {}).get(key, [])
        if captions:
            caption = random.choice(captions)

    elif finding_type == "sbom":
        sub_type = kwargs.get("sub_type", "commentary")
        captions = CAPTIONS.get("sbom", {}).get(sub_type, [])
        if captions:
            caption = random.choice(captions)

    elif finding_type == "paranoia":
        level = (severity or "chill").lower()
        captions = CAPTIONS.get("paranoia", {}).get(level, [])
        if captions:
            caption = random.choice(captions)

    elif finding_type == "error":
        error_code = str(kwargs.get("error_code", 500))
        captions = CAPTIONS.get("error_messages", {}).get(error_code, [])
        if captions:
            caption = random.choice(captions)

    # Fallback
    if not caption:
        caption = "Your dependencies are a disaster. This is fine."

    # Apply substitutions
    import datetime
    caption = caption.replace("{count}", str(dep_count))
    caption = caption.replace("{year}", str(datetime.datetime.now().year - 1))
    caption = caption.replace("{count_times_3}", str(dep_count * 3))

    return caption


def get_sbom_commentary() -> str:
    """Get a random SBOM commentary."""
    return select_caption("sbom", sub_type="commentary")


def get_paranoia_message(level: int, request_count: int = 0) -> str:
    """Get paranoia message for level (0=chill, 1=anxious, 2=meltdown)."""
    level_names = {0: "chill", 1: "anxious", 2: "meltdown"}
    # Pass request_count as dep_count so {count} gets replaced correctly
    return select_caption("paranoia", severity=level_names.get(level, "chill"), dep_count=request_count)


def get_error_message(status_code: int) -> str:
    """Get sarcastic error message for HTTP status code."""
    return select_caption("error", error_code=status_code)


def get_meltdown_caption() -> str:
    """Get an unhinged caption for MELTDOWN mode."""
    return random.choice(MELTDOWN_CAPTIONS)


def get_meltdown_refusal() -> str:
    """Get a 503 refusal message for MELTDOWN mode."""
    return random.choice(MELTDOWN_REFUSALS)


def get_panic_meltdown_secret() -> str:
    """Get a classified secret for PANIC button in MELTDOWN mode."""
    return random.choice(PANIC_MELTDOWN_SECRETS)
