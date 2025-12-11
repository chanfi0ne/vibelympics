# PURPOSE: API route handlers for package audit endpoints
from fastapi import APIRouter, HTTPException
from datetime import datetime
import httpx
import asyncio
from typing import Optional

from models.request import AuditRequest, CompareRequest
from models.response import (
    AuditResponse,
    PackageMetadata,
    RepositoryVerification,
    HealthResponse,
    CompareResponse,
    VersionAnalysis,
    VulnerabilityInfo,
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
from services.osv_client import fetch_vulnerabilities, fetch_all_vulnerabilities, is_version_affected
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
        
        # Use requested version or default to latest
        target_version = request.version if request.version else latest_version
        if request.version and request.version not in versions:
            raise HTTPException(
                status_code=400,
                detail={"error": "invalid_version", "message": f"Version '{request.version}' not found"}
            )
        
        latest_version_data = versions.get(target_version, {})
        
        # Get recent versions for version picker (last 10)
        version_list = list(versions.keys())
        available_versions = version_list[-15:] if len(version_list) > 15 else version_list
        available_versions.reverse()  # Most recent first

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
        vuln_task = fetch_vulnerabilities(client, package_name, version=target_version)
        all_vulns_task = fetch_all_vulnerabilities(client, package_name)  # For historical count
        provenance_task = fetch_provenance_attestations(client, package_name, target_version)

        all_vulns = []  # All historical vulnerabilities
        
        if repo_url and "github.com" in repo_url:
            github_results = await asyncio.gather(
                fetch_repository_data(client, repo_url),
                vuln_task,
                all_vulns_task,
                provenance_task,
                return_exceptions=True
            )

            github_data_result, advisories_result, all_vulns_result, provenance_result = github_results

            if not isinstance(github_data_result, Exception):
                github_data = github_data_result

            if not isinstance(advisories_result, Exception):
                advisories = advisories_result

            if not isinstance(all_vulns_result, Exception):
                all_vulns = all_vulns_result

            if not isinstance(provenance_result, Exception) and provenance_result:
                provenance_data = analyze_provenance(provenance_result, package_name)
        else:
            # No GitHub repo, but still fetch vulnerabilities and provenance
            other_results = await asyncio.gather(
                vuln_task,
                all_vulns_task,
                provenance_task,
                return_exceptions=True
            )
            advisories_result, all_vulns_result, provenance_result = other_results

            if not isinstance(advisories_result, Exception):
                advisories = advisories_result

            if not isinstance(all_vulns_result, Exception):
                all_vulns = all_vulns_result

            if not isinstance(provenance_result, Exception) and provenance_result:
                provenance_data = analyze_provenance(provenance_result, package_name)
        
        # Calculate historical CVEs fixed (all CVEs that don't affect current version)
        historical_cves_fixed = 0
        for vuln in all_vulns:
            if not is_version_affected(target_version, vuln):
                historical_cves_fixed += 1

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
            version=target_version,
            risk_score=risk_score,
            risk_level=risk_level,
            factors=factors,
            metadata=metadata,
            radar_scores=radar_scores,
            repository_verification=repo_verification,
            historical_cves_fixed=historical_cves_fixed,
            available_versions=available_versions,
            timestamp=datetime.utcnow().isoformat() + "Z",
            audit_duration_ms=duration_ms
        )


@router.post("/audit/compare", response_model=CompareResponse)
async def compare_versions(request: CompareRequest):
    """
    Compare security vulnerabilities between two versions of a package.

    Returns:
    - Vulnerabilities affecting each version
    - CVEs fixed by upgrading
    - New CVEs introduced (if any)
    - Risk reduction score
    - Upgrade recommendation
    """
    start_time = datetime.now()
    package_name = request.package_name
    version_old = request.version_old
    version_new = request.version_new

    async with httpx.AsyncClient() as client:
        # Verify package exists
        try:
            npm_data = await fetch_package_metadata(client, package_name)
        except PackageNotFoundError:
            raise HTTPException(
                status_code=404,
                detail={"error": "package_not_found", "message": f"Package '{package_name}' not found"}
            )

        # Verify versions exist
        versions = npm_data.get("versions", {})
        if version_old not in versions:
            raise HTTPException(
                status_code=400,
                detail={"error": "invalid_version", "message": f"Version '{version_old}' not found"}
            )
        if version_new not in versions:
            raise HTTPException(
                status_code=400,
                detail={"error": "invalid_version", "message": f"Version '{version_new}' not found"}
            )

        # Fetch vulnerabilities for both versions in parallel
        vulns_old, vulns_new = await asyncio.gather(
            fetch_vulnerabilities(client, package_name, version=version_old),
            fetch_vulnerabilities(client, package_name, version=version_new),
            return_exceptions=True
        )

        # Handle errors gracefully
        if isinstance(vulns_old, Exception):
            vulns_old = []
        if isinstance(vulns_new, Exception):
            vulns_new = []

        # Convert to VulnerabilityInfo objects
        def to_vuln_info(vuln: dict) -> VulnerabilityInfo:
            return VulnerabilityInfo(
                id=vuln.get("id", ""),
                cve_id=vuln.get("cve_id"),
                severity=vuln.get("severity", "medium"),
                summary=vuln.get("summary", ""),
                fixed_in=vuln.get("affected", "").split("fixed: ")[-1].split(",")[0] if "fixed:" in vuln.get("affected", "") else None
            )

        vulns_old_info = [to_vuln_info(v) for v in vulns_old]
        vulns_new_info = [to_vuln_info(v) for v in vulns_new]

        # Calculate counts by severity
        def count_by_severity(vulns: list) -> dict:
            counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
            for v in vulns:
                sev = v.severity.lower() if hasattr(v, 'severity') else v.get("severity", "medium").lower()
                if sev in counts:
                    counts[sev] += 1
            return counts

        old_counts = count_by_severity(vulns_old_info)
        new_counts = count_by_severity(vulns_new_info)

        # Build version analyses
        old_analysis = VersionAnalysis(
            version=version_old,
            vulnerabilities=vulns_old_info,
            vuln_count=len(vulns_old_info),
            critical_count=old_counts["critical"],
            high_count=old_counts["high"],
            medium_count=old_counts["medium"],
            low_count=old_counts["low"]
        )

        new_analysis = VersionAnalysis(
            version=version_new,
            vulnerabilities=vulns_new_info,
            vuln_count=len(vulns_new_info),
            critical_count=new_counts["critical"],
            high_count=new_counts["high"],
            medium_count=new_counts["medium"],
            low_count=new_counts["low"]
        )

        # Find fixed and new vulnerabilities
        old_ids = {v.id for v in vulns_old_info}
        new_ids = {v.id for v in vulns_new_info}

        fixed_ids = old_ids - new_ids
        new_vuln_ids = new_ids - old_ids

        vulns_fixed = [v for v in vulns_old_info if v.id in fixed_ids]
        vulns_introduced = [v for v in vulns_new_info if v.id in new_vuln_ids]

        # Calculate risk reduction (weighted by severity)
        severity_weights = {"critical": 25, "high": 15, "medium": 8, "low": 3}
        old_risk = sum(severity_weights.get(v.severity.lower(), 5) for v in vulns_old_info)
        new_risk = sum(severity_weights.get(v.severity.lower(), 5) for v in vulns_new_info)
        risk_reduction = old_risk - new_risk

        # Generate recommendation
        if len(vulns_fixed) > 0 and len(vulns_introduced) == 0:
            if any(v.severity.lower() in ["critical", "high"] for v in vulns_fixed):
                recommendation = f"STRONGLY RECOMMENDED: Upgrade fixes {len(vulns_fixed)} vulnerabilities including critical/high severity issues."
            else:
                recommendation = f"Recommended: Upgrade fixes {len(vulns_fixed)} vulnerabilities."
        elif len(vulns_introduced) > 0:
            recommendation = f"Caution: Upgrade fixes {len(vulns_fixed)} but introduces {len(vulns_introduced)} new vulnerabilities."
        elif len(vulns_old_info) == 0 and len(vulns_new_info) == 0:
            recommendation = "Both versions have no known vulnerabilities."
        else:
            recommendation = "No significant security difference between versions."

        # Calculate duration
        end_time = datetime.now()
        duration_ms = int((end_time - start_time).total_seconds() * 1000)

        return CompareResponse(
            package_name=package_name,
            old_version=old_analysis,
            new_version=new_analysis,
            vulnerabilities_fixed=vulns_fixed,
            vulnerabilities_new=vulns_introduced,
            risk_reduction=risk_reduction,
            recommendation=recommendation,
            timestamp=datetime.utcnow().isoformat() + "Z",
            duration_ms=duration_ms
        )
