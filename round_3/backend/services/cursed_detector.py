# PURPOSE: Cursed package detection for PARANOID
# Detects infamous packages and typosquats

import json
import random
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

# Load cursed packages database
CURSED_DB_PATH = Path(__file__).parent.parent / "data" / "cursed.json"
CURSED_DB: dict = {}


def load_cursed_db():
    """Load cursed packages database from JSON file."""
    global CURSED_DB
    try:
        with open(CURSED_DB_PATH) as f:
            CURSED_DB = json.load(f)
    except Exception as e:
        print(f"Warning: Could not load cursed packages database: {e}")
        CURSED_DB = {"packages": {}, "typosquats": {}}


load_cursed_db()


@dataclass
class CursedMatch:
    """Represents a cursed package detection."""
    package: str
    severity: str
    incident_type: str
    description: str
    roast: str
    is_typosquat: bool = False
    intended_package: Optional[str] = None


def detect_cursed(package_name: str) -> Optional[CursedMatch]:
    """Detect if a package is cursed (infamous incident or typosquat).
    
    Args:
        package_name: Name of the package
    
    Returns:
        CursedMatch if package is cursed, None otherwise
    """
    pkg_name = package_name.lower().strip()
    packages = CURSED_DB.get("packages", {})
    typosquats = CURSED_DB.get("typosquats", {})
    
    # Check for direct cursed package match
    if pkg_name in packages:
        pkg_data = packages[pkg_name]
        roasts = pkg_data.get("roasts", ["This package has a troubled history."])
        return CursedMatch(
            package=package_name,
            severity=pkg_data.get("severity", "high"),
            incident_type=pkg_data.get("incident_type", "unknown"),
            description=pkg_data.get("description", ""),
            roast=random.choice(roasts),
            is_typosquat=False
        )
    
    # Check for typosquat
    if pkg_name in typosquats:
        intended = typosquats[pkg_name]
        return CursedMatch(
            package=package_name,
            severity="critical",
            incident_type="typosquatting",
            description=f"Potential typosquat of '{intended}'",
            roast=f"'{package_name}' looks suspiciously like '{intended}'. Typosquatting detected. Check your spelling.",
            is_typosquat=True,
            intended_package=intended
        )
    
    return None


def detect_cursed_batch(package_names: list[str]) -> list[CursedMatch]:
    """Detect cursed packages in a list.
    
    Args:
        package_names: List of package names
    
    Returns:
        List of CursedMatch objects for any cursed packages found
    """
    matches = []
    for pkg_name in package_names:
        match = detect_cursed(pkg_name)
        if match:
            matches.append(match)
    return matches


def get_cursed_severity_order(severity: str) -> int:
    """Get numeric order for cursed severity (higher = worse)."""
    order = {
        "medium": 1,
        "high": 2,
        "critical": 3,
        "legendary": 4  # Reserved for left-pad
    }
    return order.get(severity.lower(), 0)


def get_worst_cursed(matches: list[CursedMatch]) -> Optional[CursedMatch]:
    """Get the worst cursed package from a list."""
    if not matches:
        return None
    return max(matches, key=lambda m: get_cursed_severity_order(m.severity))
