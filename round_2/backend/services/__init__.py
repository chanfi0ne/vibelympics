# PURPOSE: Package initialization for service modules
from .npm_client import fetch_package_metadata, fetch_download_stats
from .github_client import fetch_repository_data, fetch_security_advisories, parse_github_url
from .analyzer import (
    analyze_typosquatting,
    analyze_install_scripts,
    analyze_package_age,
    analyze_maintainers,
    analyze_repository,
    analyze_downloads,
    analyze_vulnerabilities,
)
from .scoring import calculate_risk_score, get_risk_level, calculate_radar_scores

__all__ = [
    "fetch_package_metadata",
    "fetch_download_stats",
    "fetch_repository_data",
    "fetch_security_advisories",
    "parse_github_url",
    "analyze_typosquatting",
    "analyze_install_scripts",
    "analyze_package_age",
    "analyze_maintainers",
    "analyze_repository",
    "analyze_downloads",
    "analyze_vulnerabilities",
    "calculate_risk_score",
    "get_risk_level",
    "calculate_radar_scores",
]
