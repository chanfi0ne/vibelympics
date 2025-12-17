# PURPOSE: Caption selection for PARANOID roasts
# Selects appropriate caption from library based on findings

import json
import random
from pathlib import Path

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


def get_paranoia_message(level: int) -> str:
    """Get paranoia message for level (0=chill, 1=anxious, 2=meltdown)."""
    level_names = {0: "chill", 1: "anxious", 2: "meltdown"}
    return select_caption("paranoia", severity=level_names.get(level, "chill"))


def get_error_message(status_code: int) -> str:
    """Get sarcastic error message for HTTP status code."""
    return select_caption("error", error_code=status_code)
