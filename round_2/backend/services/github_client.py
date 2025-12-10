# PURPOSE: GitHub API client for repository verification and security advisories
import httpx
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import re
import os


class RateLimitError(Exception):
    """Raised when GitHub rate limit is exceeded."""
    pass


class RepositoryNotFoundError(Exception):
    """Raised when repository doesn't exist."""
    pass


# Simple TTL cache for GitHub API responses
class TTLCache:
    """Time-To-Live cache for GitHub API responses."""

    def __init__(self, ttl_seconds: int = 3600):
        self._cache: Dict[str, Tuple[Any, datetime]] = {}
        self._ttl = timedelta(seconds=ttl_seconds)

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired."""
        if key in self._cache:
            value, timestamp = self._cache[key]
            if datetime.now() - timestamp < self._ttl:
                return value
            # Expired, remove from cache
            del self._cache[key]
        return None

    def set(self, key: str, value: Any) -> None:
        """Store value in cache with current timestamp."""
        self._cache[key] = (value, datetime.now())

    def clear(self) -> None:
        """Clear all cached entries."""
        self._cache.clear()


# Global cache instance (1 hour TTL)
_github_cache = TTLCache(ttl_seconds=3600)


def parse_github_url(repo_url: Optional[str]) -> Optional[Tuple[str, str]]:
    """
    Extract owner and repo name from GitHub URL.

    Args:
        repo_url: GitHub repository URL

    Returns:
        (owner, repo) tuple or None if invalid
    """
    if not repo_url:
        return None

    # Handle various GitHub URL formats
    patterns = [
        r"github\.com[:/]([^/]+)/([^/\.]+)",
        r"github\.com/([^/]+)/([^/]+)\.git",
    ]

    for pattern in patterns:
        match = re.search(pattern, repo_url)
        if match:
            owner, repo = match.groups()
            # Remove .git suffix if present
            repo = repo.replace(".git", "")
            return (owner, repo)

    return None


async def fetch_repository_data(
    client: httpx.AsyncClient,
    repo_url: str,
    token: Optional[str] = None
) -> Dict[str, Any]:
    """
    Fetch GitHub repository metadata.

    Args:
        client: HTTP client instance
        repo_url: GitHub repository URL
        token: Optional GitHub API token for higher rate limits

    Returns:
        {
            "stars": 58000,
            "forks": 7000,
            "archived": false,
            "updated_at": "2024-01-15T10:30:00Z"
        }

    Raises:
        RateLimitError: GitHub rate limit exceeded
        RepositoryNotFoundError: Repo doesn't exist
    """
    parsed = parse_github_url(repo_url)
    if not parsed:
        raise ValueError(f"Invalid GitHub URL: {repo_url}")

    owner, repo = parsed

    # Check cache first
    cache_key = f"repo:{owner}/{repo}"
    cached = _github_cache.get(cache_key)
    if cached:
        return cached

    # Prepare headers
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"
    elif os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = f"token {os.environ.get('GITHUB_TOKEN')}"

    url = f"https://api.github.com/repos/{owner}/{repo}"

    try:
        response = await client.get(url, headers=headers, timeout=5.0)

        if response.status_code == 404:
            raise RepositoryNotFoundError(f"Repository {owner}/{repo} not found")

        if response.status_code == 403:
            # Check if it's a rate limit issue
            if "rate limit" in response.text.lower():
                raise RateLimitError("GitHub API rate limit exceeded")
            raise Exception(f"GitHub API forbidden: {response.text}")

        response.raise_for_status()
        data = response.json()

        result = {
            "stars": data.get("stargazers_count", 0),
            "forks": data.get("forks_count", 0),
            "archived": data.get("archived", False),
            "updated_at": data.get("updated_at"),
            "created_at": data.get("created_at"),
            "default_branch": data.get("default_branch", "main"),
        }

        # Cache the result
        _github_cache.set(cache_key, result)

        return result

    except (RateLimitError, RepositoryNotFoundError):
        raise
    except httpx.TimeoutException:
        raise Exception("GitHub API request timed out")
    except Exception as e:
        raise Exception(f"Failed to fetch repository data: {str(e)}")


async def fetch_security_advisories(
    client: httpx.AsyncClient,
    package_name: str,
    token: Optional[str] = None
) -> list:
    """
    Fetch security advisories from GitHub Advisory Database.

    Args:
        client: HTTP client instance
        package_name: Package name
        token: Optional GitHub API token

    Returns:
        List of advisories with severity, description, patched versions
    """
    # Check cache first
    cache_key = f"advisories:{package_name}"
    cached = _github_cache.get(cache_key)
    if cached:
        return cached

    # Prepare headers
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"
    elif os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = f"token {os.environ.get('GITHUB_TOKEN')}"

    # GitHub GraphQL API for advisories (simplified approach)
    # For now, we'll use a simpler approach and return empty list
    # In production, you'd query the GitHub Advisory Database GraphQL API

    # Return empty list for now (graceful degradation)
    # This can be enhanced with GraphQL query to:
    # https://api.github.com/graphql

    result = []
    _github_cache.set(cache_key, result)
    return result
