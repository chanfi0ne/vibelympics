# PURPOSE: API route handlers for package audit endpoints
from fastapi import APIRouter, HTTPException
from datetime import datetime
import httpx
import asyncio
from typing import Optional

from models.request import AuditRequest
from models.response import (
    AuditResponse,
    PackageMetadata,
    RepositoryVerification,
    HealthResponse,
)
from services.npm_client import (
    fetch_package_metadata,
    fetch_download_stats,
    PackageNotFoundError,
    RegistryError,
)
from services.github_client import (
    fetch_repository_data,
    RateLimitError,
    RepositoryNotFoundError,
)
from services.osv_client import fetch_vulnerabilities
from services.provenance_client import fetch_provenance_attestations, analyze_provenance
from services.analyzer import (
    analyze_typosquatting,
    analyze_install_scripts,
    analyze_package_age,
    analyze_maintainers,
    analyze_repository,
    analyze_downloads,
    analyze_vulnerabilities,
    analyze_dependencies,
    analyze_license,
    analyze_provenance as analyze_provenance_factors,
)
from services.scoring import (
    calculate_risk_score,
    get_risk_level,
    calculate_radar_scores,
)

router = APIRouter(prefix="/api", tags=["audit"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.utcnow().isoformat() + "Z"
    )


@router.post("/audit", response_model=AuditResponse)
async def audit_package(request: AuditRequest):
    """
    Perform comprehensive security audit on an npm package.

    This endpoint:
    1. Fetches package data from npm registry
    2. Fetches repository data from GitHub (if available)
    3. Analyzes multiple security signals
    4. Calculates risk score and category scores
    5. Returns comprehensive audit report

    Graceful degradation: If external APIs fail, returns partial results.
    """
    start_time = datetime.now()
    package_name = request.package_name

    async with httpx.AsyncClient() as client:
        # Parallel API calls with exception handling
        results = await asyncio.gather(
            fetch_package_metadata(client, package_name),
            fetch_download_stats(client, package_name),
            return_exceptions=True
        )

        npm_data, download_stats = results

        # Handle npm registry errors
        if isinstance(npm_data, PackageNotFoundError):
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "package_not_found",
                    "message": str(npm_data),
                    "status_code": 404
                }
            )
        elif isinstance(npm_data, Exception):
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "internal_error",
                    "message": f"Failed to fetch package data: {str(npm_data)}",
                    "status_code": 500
                }
            )

        # Extract basic package info
        latest_version = npm_data.get("dist-tags", {}).get("latest", "unknown")
        versions = npm_data.get("versions", {})
        latest_version_data = versions.get(latest_version, {})

        # Extract repository URL
        repo_info = latest_version_data.get("repository") or npm_data.get("repository")
        repo_url = None
        if isinstance(repo_info, dict):
            repo_url = repo_info.get("url")
        elif isinstance(repo_info, str):
            repo_url = repo_info

        # Clean up repo URL (remove git+ prefix, .git suffix)
        if repo_url:
            repo_url = repo_url.replace("git+", "").replace("git://", "https://")

        # Fetch GitHub data, vulnerabilities, and provenance in parallel
        github_data = None
        advisories = []
        provenance_data = {}

        # Always fetch vulnerabilities from OSV and provenance (don't require GitHub)
        # Pass version to OSV so we only get vulns affecting the current version
        vuln_task = fetch_vulnerabilities(client, package_name, version=latest_version)
        provenance_task = fetch_provenance_attestations(client, package_name, latest_version)

        if repo_url and "github.com" in repo_url:
            github_results = await asyncio.gather(
                fetch_repository_data(client, repo_url),
                vuln_task,
                provenance_task,
                return_exceptions=True
            )

            github_data_result, advisories_result, provenance_result = github_results

            if not isinstance(github_data_result, Exception):
                github_data = github_data_result

            if not isinstance(advisories_result, Exception):
                advisories = advisories_result

            if not isinstance(provenance_result, Exception) and provenance_result:
                provenance_data = analyze_provenance(provenance_result, package_name)
        else:
            # No GitHub repo, but still fetch vulnerabilities and provenance
            other_results = await asyncio.gather(
                vuln_task,
                provenance_task,
                return_exceptions=True
            )
            advisories_result, provenance_result = other_results

            if not isinstance(advisories_result, Exception):
                advisories = advisories_result

            if not isinstance(provenance_result, Exception) and provenance_result:
                provenance_data = analyze_provenance(provenance_result, package_name)

        # Build metadata
        time_data = npm_data.get("time", {})
        created = time_data.get("created")
        modified = time_data.get("modified")

        maintainers_list = latest_version_data.get("maintainers") or npm_data.get("maintainers") or []
        maintainer_names = [m.get("name", "unknown") for m in maintainers_list if isinstance(m, dict)]

        author_info = latest_version_data.get("author") or npm_data.get("author")
        author_name = None
        if isinstance(author_info, dict):
            author_name = author_info.get("name")
        elif isinstance(author_info, str):
            author_name = author_info

        weekly_downloads = None
        if isinstance(download_stats, dict):
            weekly_downloads = download_stats.get("downloads", 0)

        metadata = PackageMetadata(
            description=latest_version_data.get("description") or npm_data.get("description"),
            author=author_name,
            license=latest_version_data.get("license") or npm_data.get("license"),
            repository=repo_url,
            created=created,
            modified=modified,
            maintainers=maintainer_names,
            downloads_weekly=weekly_downloads,
            versions_count=len(versions)
        )

        # Calculate package age
        age_days = 0
        if created:
            try:
                from dateutil import parser as date_parser
                created_dt = date_parser.parse(created)
                now = datetime.now(created_dt.tzinfo) if created_dt.tzinfo else datetime.now()
                age_days = (now - created_dt).days
            except Exception:
                pass

        # Run all analyzers
        factors = []

        # Typosquatting check
        factors.extend(analyze_typosquatting(package_name))

        # Install scripts check
        factors.extend(analyze_install_scripts(latest_version_data))

        # Package age check
        factors.extend(analyze_package_age(created))

        # Maintainer analysis
        factors.extend(analyze_maintainers(maintainers_list, age_days))

        # Repository verification
        factors.extend(analyze_repository(repo_url, github_data))

        # Download patterns
        factors.extend(analyze_downloads(weekly_downloads, age_days))

        # Dependency analysis
        factors.extend(analyze_dependencies(latest_version_data))

        # License analysis
        license_info = latest_version_data.get("license") or npm_data.get("license")
        factors.extend(analyze_license(license_info))

        # Sigstore provenance analysis
        factors.extend(analyze_provenance_factors(provenance_data))

        # Known vulnerabilities (from OSV.dev)
        factors.extend(analyze_vulnerabilities(advisories))

        # Calculate scores
        risk_score, has_critical_high_risk = calculate_risk_score(factors)
        risk_level = get_risk_level(risk_score, has_critical_high_risk)
        radar_scores = calculate_radar_scores(factors)

        # Build repository verification
        repo_verification = None
        if github_data:
            repo_verification = RepositoryVerification(
                exists=True,
                verified=True,
                stars=github_data.get("stars"),
                forks=github_data.get("forks"),
                archived=github_data.get("archived"),
                last_updated=github_data.get("updated_at")
            )
        elif repo_url:
            # Repo URL exists but couldn't fetch data
            repo_verification = RepositoryVerification(
                exists=False,
                verified=False
            )

        # Calculate duration
        end_time = datetime.now()
        duration_ms = int((end_time - start_time).total_seconds() * 1000)

        # Build response
        return AuditResponse(
            package_name=package_name,
            version=latest_version,
            risk_score=risk_score,
            risk_level=risk_level,
            factors=factors,
            metadata=metadata,
            radar_scores=radar_scores,
            repository_verification=repo_verification,
            timestamp=datetime.utcnow().isoformat() + "Z",
            audit_duration_ms=duration_ms
        )
