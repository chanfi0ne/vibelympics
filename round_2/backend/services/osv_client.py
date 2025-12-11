# PURPOSE: OSV.dev API client for fetching real vulnerability data
import httpx
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import re


class TTLCache:
    """Simple TTL cache for OSV responses."""

    def __init__(self, ttl_seconds: int = 3600):
        self._cache: Dict[str, tuple] = {}
        self._ttl = timedelta(seconds=ttl_seconds)

    def get(self, key: str) -> Optional[Any]:
        if key in self._cache:
            value, timestamp = self._cache[key]
            if datetime.now() - timestamp < self._ttl:
                return value
            del self._cache[key]
        return None

    def set(self, key: str, value: Any) -> None:
        self._cache[key] = (value, datetime.now())


_osv_cache = TTLCache(ttl_seconds=3600)


def parse_semver(version: str) -> tuple:
    """Parse semver string to tuple for comparison. Returns (major, minor, patch)."""
    # Handle version strings like "4.17.21", "0.1.0", etc.
    match = re.match(r'^(\d+)\.(\d+)\.(\d+)', version.strip())
    if match:
        return (int(match.group(1)), int(match.group(2)), int(match.group(3)))
    # Fallback for non-semver versions
    return (0, 0, 0)


def version_in_range(
    version: str,
    introduced: str,
    fixed: Optional[str] = None,
    last_affected: Optional[str] = None
) -> bool:
    """
    Check if a version falls within an affected range.

    Args:
        version: The version to check
        introduced: Version where vulnerability was introduced (inclusive)
        fixed: Version where vulnerability was fixed (exclusive), or None if not fixed
        last_affected: Last version affected (inclusive), alternative to fixed

    Returns:
        True if version is affected
    """
    v = parse_semver(version)
    intro = parse_semver(introduced) if introduced and introduced != "0" else (0, 0, 0)

    # Version must be >= introduced
    if v < intro:
        return False

    # If last_affected specified, version must be <= last_affected
    if last_affected:
        last = parse_semver(last_affected)
        return v <= last

    # If fixed specified, version must be < fixed (fixed version is safe)
    if fixed:
        fix = parse_semver(fixed)
        return v < fix

    # No fix or last_affected means all versions >= introduced are affected
    return True


def is_version_affected(version: str, vuln: Dict[str, Any]) -> bool:
    """
    Check if a specific version is affected by a vulnerability.

    Parses OSV affected ranges and checks if the version falls within any affected range.
    """
    if not version:
        return True  # If no version specified, assume affected

    for affected in vuln.get("affected", []):
        # Check if this affects npm ecosystem
        pkg = affected.get("package", {})
        if pkg.get("ecosystem") != "npm":
            continue

        for range_info in affected.get("ranges", []):
            if range_info.get("type") != "SEMVER":
                continue

            events = range_info.get("events", [])
            introduced = None
            fixed = None
            last_affected = None

            for event in events:
                if "introduced" in event:
                    introduced = event["introduced"]
                if "fixed" in event:
                    fixed = event["fixed"]
                if "last_affected" in event:
                    last_affected = event["last_affected"]

            # Check if version is in this range
            if introduced is not None:
                if version_in_range(version, introduced, fixed, last_affected):
                    return True

    return False


async def fetch_vulnerabilities(
    client: httpx.AsyncClient,
    package_name: str,
    version: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Fetch vulnerabilities from OSV.dev API.

    Args:
        client: HTTP client instance
        package_name: npm package name
        version: Optional specific version to check (only returns vulns affecting this version)

    Returns:
        List of vulnerability dictionaries with severity, summary, cve_id
    """
    cache_key = f"osv:{package_name}:{version or 'all'}"
    cached = _osv_cache.get(cache_key)
    if cached is not None:
        return cached

    url = "https://api.osv.dev/v1/query"
    package_info = {
        "name": package_name,
        "ecosystem": "npm"
    }
    # If version specified, OSV will only return vulns affecting that version
    if version:
        package_info["version"] = version

    payload = {"package": package_info}

    try:
        response = await client.post(url, json=payload, timeout=5.0)
        response.raise_for_status()
        data = response.json()

        vulns = data.get("vulns", [])
        results = []

        for vuln in vulns:
            # Filter by version if specified (OSV API filtering is unreliable)
            if version and not is_version_affected(version, vuln):
                continue

            # Extract severity from database_specific or severity array
            severity = "medium"
            if vuln.get("severity"):
                for sev in vuln["severity"]:
                    if sev.get("type") == "CVSS_V3":
                        score = sev.get("score", "")
                        # Parse CVSS score to severity
                        if "CRITICAL" in score.upper():
                            severity = "critical"
                        elif "HIGH" in score.upper():
                            severity = "high"
                        elif "MEDIUM" in score.upper():
                            severity = "medium"
                        elif "LOW" in score.upper():
                            severity = "low"
                        break

            # Also check database_specific for severity
            db_specific = vuln.get("database_specific", {})
            if db_specific.get("severity"):
                severity = db_specific["severity"].lower()

            # Extract CVE ID from aliases
            cve_id = ""
            for alias in vuln.get("aliases", []):
                if alias.startswith("CVE-"):
                    cve_id = alias
                    break

            # Get affected versions info
            affected_info = []
            for affected in vuln.get("affected", []):
                for range_info in affected.get("ranges", []):
                    events = range_info.get("events", [])
                    for event in events:
                        if "introduced" in event:
                            affected_info.append(f"introduced: {event['introduced']}")
                        if "fixed" in event:
                            affected_info.append(f"fixed: {event['fixed']}")

            results.append({
                "id": vuln.get("id", ""),
                "cve_id": cve_id,
                "severity": severity,
                "summary": vuln.get("summary", "Security vulnerability detected"),
                "description": vuln.get("details", "")[:500] if vuln.get("details") else "",
                "affected": ", ".join(affected_info[:3]) if affected_info else "",
                "published": vuln.get("published", ""),
                "modified": vuln.get("modified", ""),
            })

        _osv_cache.set(cache_key, results)
        return results

    except httpx.TimeoutException:
        _osv_cache.set(cache_key, [])
        return []
    except Exception:
        _osv_cache.set(cache_key, [])
        return []
