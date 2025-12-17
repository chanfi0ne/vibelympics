# PURPOSE: CVE detection service for PARANOID
# Matches packages against pre-cached CVE database

import json
import re
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

# Load CVE database
CVE_DB_PATH = Path(__file__).parent.parent / "data" / "cves.json"
CVE_DB: dict = {}


def load_cve_db():
    """Load CVE database from JSON file."""
    global CVE_DB
    try:
        with open(CVE_DB_PATH) as f:
            CVE_DB = json.load(f)
    except Exception as e:
        print(f"Warning: Could not load CVE database: {e}")
        CVE_DB = {}


load_cve_db()


@dataclass
class CVEMatch:
    """Represents a CVE match for a package."""
    package: str
    version: str
    cve_id: str
    severity: str
    description: str
    fixed_version: Optional[str] = None


def parse_version(version_str: str) -> tuple:
    """Parse version string into comparable tuple."""
    if not version_str:
        return (0,)
    # Remove common prefixes
    version_str = re.sub(r'^[v^~>=<]', '', version_str)
    # Extract numeric parts
    parts = re.findall(r'\d+', version_str)
    return tuple(int(p) for p in parts) if parts else (0,)


def version_matches(pkg_version: str, affected_spec: str) -> bool:
    """Check if package version matches affected version specification.
    
    Supports:
    - "<4.17.12" - less than
    - "<=4.17.12" - less than or equal
    - "*" - all versions affected
    - ">=1.0.0,<2.0.0" - range (simplified)
    """
    if not pkg_version or affected_spec == "*":
        return True  # Assume affected if no version or all affected
    
    pkg_ver = parse_version(pkg_version)
    
    # Handle less than
    if affected_spec.startswith("<"):
        is_equal = affected_spec.startswith("<=")
        affected_ver = parse_version(affected_spec.lstrip("<= "))
        if is_equal:
            return pkg_ver <= affected_ver
        return pkg_ver < affected_ver
    
    # Handle greater than (rare for CVEs)
    if affected_spec.startswith(">"):
        is_equal = affected_spec.startswith(">=")
        affected_ver = parse_version(affected_spec.lstrip(">= "))
        if is_equal:
            return pkg_ver >= affected_ver
        return pkg_ver > affected_ver
    
    # Handle exact match
    affected_ver = parse_version(affected_spec)
    return pkg_ver == affected_ver


def detect_cves(package_name: str, version: Optional[str] = None) -> list[CVEMatch]:
    """Detect CVEs for a given package and version.
    
    Args:
        package_name: Name of the package (e.g., "lodash")
        version: Version string (e.g., "4.17.11")
    
    Returns:
        List of CVEMatch objects for matching vulnerabilities
    """
    matches = []
    
    # Normalize package name (lowercase, strip whitespace)
    pkg_name = package_name.lower().strip()
    
    # Skip metadata
    if pkg_name.startswith("_"):
        return matches
    
    # Look up in CVE database
    cves = CVE_DB.get(pkg_name, [])
    
    for cve in cves:
        affected = cve.get("affected_versions", "*")
        
        # Check if version is affected
        if version_matches(version, affected):
            matches.append(CVEMatch(
                package=package_name,
                version=version or "unknown",
                cve_id=cve["id"],
                severity=cve.get("severity", "unknown"),
                description=cve.get("description", ""),
                fixed_version=cve.get("fixed_version")
            ))
    
    return matches


def detect_cves_batch(packages: list[tuple[str, Optional[str]]]) -> list[CVEMatch]:
    """Detect CVEs for multiple packages.
    
    Args:
        packages: List of (package_name, version) tuples
    
    Returns:
        List of all CVE matches across all packages
    """
    all_matches = []
    for pkg_name, version in packages:
        matches = detect_cves(pkg_name, version)
        all_matches.extend(matches)
    return all_matches


def get_severity_order(severity: str) -> int:
    """Get numeric order for severity (higher = worse)."""
    order = {
        "low": 1,
        "medium": 2,
        "high": 3,
        "critical": 4
    }
    return order.get(severity.lower(), 0)


def get_worst_severity(matches: list[CVEMatch]) -> str:
    """Get the worst severity from a list of CVE matches."""
    if not matches:
        return "none"
    return max(matches, key=lambda m: get_severity_order(m.severity)).severity
