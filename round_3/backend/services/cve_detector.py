# PURPOSE: CVE detection service for PARANOID
# Matches packages against pre-cached CVE database + live OSV.dev API

import json
import re
import logging
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
import httpx

logger = logging.getLogger(__name__)

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

# Package name aliases - map variants to canonical names in CVE DB
PACKAGE_ALIASES = {
    "lodash-es": "lodash",
    "lodash.merge": "lodash",
    "lodash.template": "lodash",
    "lodash.set": "lodash",
    "lodash.get": "lodash",
    "lodash.clonedeep": "lodash",
    "underscore.js": "underscore",
    "jquery-slim": "jquery",
    "jquery.min": "jquery",
    "axios-http": "axios",
    "node-fetch": "node-fetch",
    "isomorphic-fetch": "node-fetch",
    "whatwg-fetch": "node-fetch",
}


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
    
    # Check for package aliases (e.g., lodash-es -> lodash)
    canonical_name = PACKAGE_ALIASES.get(pkg_name, pkg_name)
    
    # Look up in CVE database
    cves = CVE_DB.get(canonical_name, [])
    
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


# --- OSV.dev Live API Integration ---

OSV_API_URL = "https://api.osv.dev/v1/query"
OSV_TIMEOUT = 3.0  # Fast timeout to not slow down roasts


async def query_osv(package_name: str, version: str, ecosystem: str = "npm") -> list[CVEMatch]:
    """Query OSV.dev API for real vulnerabilities.
    
    Args:
        package_name: Package name
        version: Version string
        ecosystem: Package ecosystem (npm, PyPI, etc.)
    
    Returns:
        List of CVEMatch objects from OSV.dev
    """
    matches = []
    
    payload = {
        "package": {
            "name": package_name,
            "ecosystem": ecosystem
        }
    }
    
    # Add version if available for more accurate results
    if version:
        payload["version"] = version
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(OSV_API_URL, json=payload, timeout=OSV_TIMEOUT)
            
            if response.status_code != 200:
                return matches
            
            data = response.json()
            vulns = data.get("vulns", [])
            
            for vuln in vulns:
                # Extract CVE ID from aliases
                cve_id = vuln.get("id", "")
                for alias in vuln.get("aliases", []):
                    if alias.startswith("CVE-"):
                        cve_id = alias
                        break
                
                # Extract severity
                severity = "medium"
                for sev in vuln.get("severity", []):
                    if sev.get("type") == "CVSS_V3":
                        score_str = sev.get("score", "")
                        # Parse CVSS vector for severity
                        if "/S:" in score_str:
                            # Extract severity from CVSS vector
                            pass
                        # Try to get base score
                        try:
                            base_score = float(score_str.split("/")[0].replace("CVSS:3.1/AV:", "").split(":")[0])
                            if base_score >= 9.0:
                                severity = "critical"
                            elif base_score >= 7.0:
                                severity = "high"
                            elif base_score >= 4.0:
                                severity = "medium"
                            else:
                                severity = "low"
                        except:
                            pass
                
                # Check database_specific for severity
                db_specific = vuln.get("database_specific", {})
                if db_specific.get("severity"):
                    severity = db_specific["severity"].lower()
                
                matches.append(CVEMatch(
                    package=package_name,
                    version=version or "unknown",
                    cve_id=cve_id,
                    severity=severity,
                    description=vuln.get("summary", "Security vulnerability")[:200],
                    fixed_version=None  # Would need to parse from affected ranges
                ))
            
            logger.info(f"OSV.dev: {package_name}@{version} -> {len(matches)} vulns")
            
    except httpx.TimeoutException:
        logger.debug(f"OSV.dev timeout for {package_name}")
    except Exception as e:
        logger.debug(f"OSV.dev error for {package_name}: {e}")
    
    return matches


async def detect_cves_live(package_name: str, version: Optional[str] = None, ecosystem: str = "npm") -> list[CVEMatch]:
    """Detect CVEs using both cached database AND live OSV.dev API.
    
    Args:
        package_name: Package name
        version: Version string
        ecosystem: Package ecosystem
    
    Returns:
        Combined list of CVE matches (deduplicated by CVE ID)
    """
    # First check cached database (fast)
    cached_matches = detect_cves(package_name, version)
    
    # Then query OSV.dev for live data
    live_matches = await query_osv(package_name, version, ecosystem)
    
    # Combine and deduplicate by CVE ID
    seen_cves = {m.cve_id for m in cached_matches}
    combined = list(cached_matches)
    
    for match in live_matches:
        if match.cve_id not in seen_cves:
            combined.append(match)
            seen_cves.add(match.cve_id)
    
    return combined


async def detect_cves_batch_live(
    packages: list[tuple[str, Optional[str]]], 
    ecosystem: str = "npm",
    max_osv_queries: int = 20  # Limit API calls
) -> list[CVEMatch]:
    """Detect CVEs for multiple packages using cached + live OSV.dev.
    
    Args:
        packages: List of (package_name, version) tuples
        ecosystem: Package ecosystem
        max_osv_queries: Max number of OSV.dev API calls (to avoid rate limiting)
    
    Returns:
        Combined list of all CVE matches
    """
    all_matches = []
    osv_queries = 0
    
    for pkg_name, version in packages:
        # Always check cached database
        cached = detect_cves(pkg_name, version)
        all_matches.extend(cached)
        
        # Query OSV.dev for packages without cached CVEs (up to limit)
        if osv_queries < max_osv_queries:
            try:
                live = await query_osv(pkg_name, version, ecosystem)
                # Add only new CVEs not in cached
                cached_ids = {m.cve_id for m in cached}
                for match in live:
                    if match.cve_id not in cached_ids:
                        all_matches.append(match)
                osv_queries += 1
            except:
                pass
    
    logger.info(f"CVE detection: {len(packages)} packages, {osv_queries} OSV queries, {len(all_matches)} total CVEs")
    return all_matches
