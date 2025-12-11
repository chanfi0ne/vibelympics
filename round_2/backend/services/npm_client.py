# PURPOSE: npm Registry API client for fetching package data
import httpx
from typing import Dict, Any, Optional
import urllib.parse


class PackageNotFoundError(Exception):
    """Raised when package is not found in npm registry."""
    pass


class RegistryError(Exception):
    """Raised when npm registry is unavailable."""
    pass


async def fetch_package_metadata(
    client: httpx.AsyncClient,
    package_name: str
) -> Dict[str, Any]:
    """
    Fetch package metadata from npm registry.

    Args:
        client: HTTP client instance
        package_name: Package name (supports @scope/package)

    Returns:
        Package JSON data from registry

    Raises:
        PackageNotFoundError: Package doesn't exist
        RegistryError: npm registry unavailable or timeout
    """
    # URL encode package name (handles scoped packages like @babel/core)
    encoded_name = urllib.parse.quote(package_name, safe="@/")
    url = f"https://registry.npmjs.org/{encoded_name}"

    try:
        response = await client.get(url, timeout=5.0)

        if response.status_code == 404:
            raise PackageNotFoundError(f"Package '{package_name}' not found on npm")

        response.raise_for_status()
        return response.json()

    except httpx.TimeoutException:
        raise RegistryError("npm registry request timed out")
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise PackageNotFoundError(f"Package '{package_name}' not found on npm")
        raise RegistryError(f"npm registry error: HTTP {e.response.status_code}")
    except Exception as e:
        raise RegistryError(f"Failed to fetch package metadata: {str(e)}")


async def fetch_download_stats(
    client: httpx.AsyncClient,
    package_name: str
) -> Dict[str, Any]:
    """
    Fetch download statistics from npm API.

    Args:
        client: HTTP client instance
        package_name: Package name

    Returns:
        {"downloads": 1234567, "period": "last-week"}
    """
    # URL encode package name
    encoded_name = urllib.parse.quote(package_name, safe="@/")
    url = f"https://api.npmjs.org/downloads/point/last-week/{encoded_name}"

    try:
        response = await client.get(url, timeout=5.0)

        # Downloads API returns 404 for packages with no downloads
        if response.status_code == 404:
            return {"downloads": 0, "period": "last-week"}

        response.raise_for_status()
        data = response.json()

        return {
            "downloads": data.get("downloads", 0),
            "period": "last-week"
        }

    except Exception:
        # Return zero downloads on any error
        return {"downloads": 0, "period": "last-week"}
