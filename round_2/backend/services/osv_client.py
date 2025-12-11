# PURPOSE: OSV.dev API client for fetching real vulnerability data
import httpx
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta


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


async def fetch_vulnerabilities(
    client: httpx.AsyncClient,
    package_name: str
) -> List[Dict[str, Any]]:
    """
    Fetch vulnerabilities from OSV.dev API.

    Args:
        client: HTTP client instance
        package_name: npm package name

    Returns:
        List of vulnerability dictionaries with severity, summary, cve_id
    """
    cache_key = f"osv:{package_name}"
    cached = _osv_cache.get(cache_key)
    if cached is not None:
        return cached

    url = "https://api.osv.dev/v1/query"
    payload = {
        "package": {
            "name": package_name,
            "ecosystem": "npm"
        }
    }

    try:
        response = await client.post(url, json=payload, timeout=5.0)
        response.raise_for_status()
        data = response.json()

        vulns = data.get("vulns", [])
        results = []

        for vuln in vulns:
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
