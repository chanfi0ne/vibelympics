# PURPOSE: Risk analysis logic for npm packages
from typing import List, Dict, Any, Optional
from datetime import datetime
from dateutil import parser as date_parser

from models.response import RiskFactor, Severity, Category
from utils.typosquat import check_typosquatting
from utils.patterns import check_dangerous_patterns, DANGEROUS_SCRIPTS


def analyze_typosquatting(package_name: str) -> List[RiskFactor]:
    """
    Check if package name is similar to popular packages.

    Returns:
        List of risk factors (empty if no match)
    """
    matches = check_typosquatting(package_name, threshold=0.80)

    if not matches:
        return []

    factors = []

    # Take top 3 matches
    for popular_pkg, similarity in matches[:3]:
        similarity_pct = int(similarity * 100)

        factors.append(RiskFactor(
            name="Typosquatting Detected",
            severity=Severity.CRITICAL,
            description=f"Package name is {similarity_pct}% similar to popular package '{popular_pkg}'",
            details=f"This may be a typosquatting attempt. Verify this is the correct package.",
            category=Category.AUTHENTICITY
        ))

    return factors


def analyze_install_scripts(package_data: Dict[str, Any]) -> List[RiskFactor]:
    """
    Analyze package.json scripts for dangerous patterns.

    Checks:
        - preinstall/postinstall hooks exist
        - Dangerous commands (curl, wget, eval, bash)
    """
    factors = []

    scripts = package_data.get("scripts", {})
    if not scripts:
        return factors

    # Check for dangerous lifecycle scripts
    dangerous_hooks = []
    for script_name in DANGEROUS_SCRIPTS:
        if script_name in scripts:
            dangerous_hooks.append(script_name)

    if dangerous_hooks:
        factors.append(RiskFactor(
            name="Install Scripts Present",
            severity=Severity.MEDIUM,
            description=f"Package has lifecycle scripts: {', '.join(dangerous_hooks)}",
            details="Install scripts execute code during installation and may pose security risks.",
            category=Category.SECURITY
        ))

        # Check each script for dangerous commands
        for hook in dangerous_hooks:
            script_content = scripts[hook]
            dangerous_patterns = check_dangerous_patterns(script_content)

            if dangerous_patterns:
                for pattern, context in dangerous_patterns[:3]:  # Limit to 3 per script
                    factors.append(RiskFactor(
                        name="Dangerous Command in Script",
                        severity=Severity.CRITICAL,
                        description=f"Script '{hook}' contains dangerous command: {pattern}",
                        details=f"Context: {context}",
                        category=Category.SECURITY
                    ))

    return factors


def analyze_package_age(created_date: Optional[str]) -> List[RiskFactor]:
    """
    Analyze package age and flag very new packages.

    <7 days: Critical
    <30 days: High
    <90 days: Medium
    """
    if not created_date:
        return []

    try:
        created = date_parser.parse(created_date)
        now = datetime.now(created.tzinfo) if created.tzinfo else datetime.now()
        age_days = (now - created).days

        if age_days < 0:
            age_days = 0

        if age_days < 7:
            return [RiskFactor(
                name="Very New Package",
                severity=Severity.CRITICAL,
                description=f"Package is only {age_days} days old",
                details="Very new packages may not have been vetted by the community yet.",
                category=Category.REPUTATION
            )]
        elif age_days < 30:
            return [RiskFactor(
                name="New Package",
                severity=Severity.HIGH,
                description=f"Package is {age_days} days old",
                details="New packages may not have established trust in the community.",
                category=Category.REPUTATION
            )]
        elif age_days < 90:
            return [RiskFactor(
                name="Recent Package",
                severity=Severity.MEDIUM,
                description=f"Package is {age_days} days old",
                details="Package is relatively recent with limited history.",
                category=Category.REPUTATION
            )]

    except Exception:
        pass

    return []


def analyze_maintainers(
    maintainers: List[Dict[str, Any]],
    package_age_days: int
) -> List[RiskFactor]:
    """
    Analyze maintainer count and patterns.

    Checks:
        - No maintainers: Critical
        - Single maintainer: Low
    """
    factors = []

    if not maintainers or len(maintainers) == 0:
        factors.append(RiskFactor(
            name="No Maintainers",
            severity=Severity.CRITICAL,
            description="Package has no listed maintainers",
            details="Packages without maintainers may be abandoned or suspicious.",
            category=Category.MAINTENANCE
        ))
    elif len(maintainers) == 1:
        maintainer_name = maintainers[0].get("name", "unknown")
        factors.append(RiskFactor(
            name="Single Maintainer",
            severity=Severity.LOW,
            description="Package has only one maintainer",
            details=f"Single point of failure: {maintainer_name}",
            category=Category.MAINTENANCE
        ))

    return factors


def analyze_repository(
    package_repo: Optional[str],
    github_data: Optional[Dict[str, Any]]
) -> List[RiskFactor]:
    """
    Verify repository exists, is active, not archived.
    """
    factors = []

    if not package_repo:
        factors.append(RiskFactor(
            name="No Repository Link",
            severity=Severity.MEDIUM,
            description="Package does not specify a repository URL",
            details="Lack of repository makes it harder to verify package legitimacy.",
            category=Category.AUTHENTICITY
        ))
        return factors

    if not github_data:
        factors.append(RiskFactor(
            name="Repository Not Verified",
            severity=Severity.LOW,
            description="Could not verify repository information",
            details="GitHub API may be rate-limited or repository is inaccessible.",
            category=Category.AUTHENTICITY
        ))
        return factors

    # Check if archived
    if github_data.get("archived"):
        factors.append(RiskFactor(
            name="Repository Archived",
            severity=Severity.HIGH,
            description="GitHub repository is archived",
            details="Archived repositories are read-only and no longer maintained.",
            category=Category.MAINTENANCE
        ))

    # Check if very low stars (potential fake repo)
    stars = github_data.get("stars", 0)
    if stars < 5:
        factors.append(RiskFactor(
            name="Low Repository Stars",
            severity=Severity.INFO,
            description=f"Repository has only {stars} stars",
            details="Low star count may indicate limited community adoption.",
            category=Category.REPUTATION
        ))

    return factors


def analyze_downloads(
    weekly_downloads: Optional[int],
    age_days: int
) -> List[RiskFactor]:
    """
    Check for suspicious download patterns.

    New package with high downloads: High risk
    Old package with very low downloads: Info
    """
    factors = []

    if weekly_downloads is None:
        return factors

    # Suspicious spike: new package with very high downloads
    if age_days < 30 and weekly_downloads > 100000:
        factors.append(RiskFactor(
            name="Suspicious Download Spike",
            severity=Severity.HIGH,
            description=f"New package ({age_days} days) has unusually high downloads ({weekly_downloads:,}/week)",
            details="This may indicate artificial inflation or automated downloads.",
            category=Category.REPUTATION
        ))

    # Very low adoption for old package
    elif age_days > 365 and weekly_downloads < 100:
        factors.append(RiskFactor(
            name="Low Adoption",
            severity=Severity.INFO,
            description=f"Package has minimal usage ({weekly_downloads}/week)",
            details="Low download count may indicate limited community trust or usefulness.",
            category=Category.REPUTATION
        ))

    return factors


def analyze_vulnerabilities(advisories: List[Dict[str, Any]]) -> List[RiskFactor]:
    """
    Parse known vulnerabilities into findings.

    Critical CVE: Critical
    High CVE: High
    etc.
    """
    factors = []

    for advisory in advisories:
        severity_str = advisory.get("severity", "medium").lower()

        # Map advisory severity to our severity enum
        severity_map = {
            "critical": Severity.CRITICAL,
            "high": Severity.HIGH,
            "medium": Severity.MEDIUM,
            "low": Severity.LOW,
        }
        severity = severity_map.get(severity_str, Severity.MEDIUM)

        summary = advisory.get("summary", "Known vulnerability")
        cve_id = advisory.get("cve_id", "")
        vuln_id = advisory.get("id", "")

        # Build details with affected versions if available
        details = advisory.get("description", "")
        if advisory.get("affected"):
            details = f"Affected versions: {advisory['affected']}. {details}"

        # Use CVE ID if available, otherwise use OSV ID
        id_suffix = f" ({cve_id})" if cve_id else (f" ({vuln_id})" if vuln_id else "")

        factors.append(RiskFactor(
            name=f"Known Vulnerability{id_suffix}",
            severity=severity,
            description=summary,
            details=details,
            category=Category.SECURITY
        ))

    return factors


def analyze_dependencies(package_data: Dict[str, Any]) -> List[RiskFactor]:
    """
    Analyze dependency count and flag excessive dependencies.

    >100 deps: High risk (large attack surface)
    >50 deps: Medium risk
    0 deps on non-trivial package: Info (might be bundled)
    """
    factors = []

    dependencies = package_data.get("dependencies", {})
    dep_count = len(dependencies) if isinstance(dependencies, dict) else 0

    if dep_count > 100:
        factors.append(RiskFactor(
            name="Excessive Dependencies",
            severity=Severity.HIGH,
            description=f"Package has {dep_count} runtime dependencies",
            details="Large dependency count increases supply chain attack surface.",
            category=Category.SECURITY
        ))
    elif dep_count > 50:
        factors.append(RiskFactor(
            name="High Dependency Count",
            severity=Severity.MEDIUM,
            description=f"Package has {dep_count} runtime dependencies",
            details="Consider auditing transitive dependencies for security risks.",
            category=Category.SECURITY
        ))

    return factors


# Common permissive licenses considered safe
SAFE_LICENSES = {
    "mit", "isc", "bsd-2-clause", "bsd-3-clause", "apache-2.0", "apache 2.0",
    "unlicense", "cc0-1.0", "wtfpl", "0bsd", "artistic-2.0",
    "(mit or apache-2.0)", "mit or apache-2.0", "apache-2.0 or mit",
}

# Copyleft licenses that may have compliance requirements
COPYLEFT_LICENSES = {
    "gpl-2.0", "gpl-3.0", "gpl-2.0-only", "gpl-3.0-only",
    "lgpl-2.0", "lgpl-2.1", "lgpl-3.0", "agpl-3.0", "agpl-3.0-only",
    "mpl-2.0", "eupl-1.2", "osl-3.0", "cc-by-sa-4.0",
}


def analyze_license(license_info: Optional[str]) -> List[RiskFactor]:
    """
    Analyze package license for missing or problematic licenses.

    No license: Medium risk (legal uncertainty)
    Copyleft: Info (compliance requirements)
    UNLICENSED: High risk (cannot legally use)
    """
    factors = []

    if not license_info:
        factors.append(RiskFactor(
            name="No License Specified",
            severity=Severity.MEDIUM,
            description="Package does not specify a license",
            details="Using packages without clear licensing may pose legal risks.",
            category=Category.AUTHENTICITY
        ))
        return factors

    license_lower = license_info.lower().strip()

    # Check for explicitly unlicensed
    if license_lower in ("unlicensed", "none", "proprietary", "see license"):
        factors.append(RiskFactor(
            name="Restrictive License",
            severity=Severity.HIGH,
            description=f"Package has restrictive license: {license_info}",
            details="This package may not be legally usable in your project.",
            category=Category.AUTHENTICITY
        ))
        return factors

    # Check for copyleft licenses
    if license_lower in COPYLEFT_LICENSES:
        factors.append(RiskFactor(
            name="Copyleft License",
            severity=Severity.INFO,
            description=f"Package uses copyleft license: {license_info}",
            details="Copyleft licenses may require you to open-source derivative works.",
            category=Category.AUTHENTICITY
        ))

    return factors


def analyze_provenance(provenance_data: Dict[str, Any]) -> List[RiskFactor]:
    """
    Analyze Sigstore provenance attestations for supply chain integrity.

    Checks:
    - Has provenance attestations (Sigstore)
    - SLSA build level
    - Transparency log entries (Rekor)
    - Verified build source

    Packages with provenance are more trustworthy as they have
    cryptographic proof of their build origin.
    """
    factors = []

    has_provenance = provenance_data.get("has_provenance", False)
    provenance_type = provenance_data.get("provenance_type", "none")
    slsa_level = provenance_data.get("slsa_level")
    is_verified = provenance_data.get("is_verified", False)
    transparency_log = provenance_data.get("transparency_log", False)
    build_source = provenance_data.get("build_source")

    if not has_provenance:
        # No provenance is not necessarily bad, but having it is a positive signal
        factors.append(RiskFactor(
            name="No Sigstore Provenance",
            severity=Severity.LOW,
            description="Package lacks cryptographic provenance attestations",
            details="Packages with Sigstore provenance provide verifiable proof of build origin. "
                    "Consider preferring packages with SLSA provenance for critical dependencies.",
            category=Category.AUTHENTICITY
        ))
        return factors

    # Has provenance - this is good! But check the details

    if transparency_log and is_verified:
        # This is excellent - fully verified with transparency log
        factors.append(RiskFactor(
            name="Sigstore Provenance Verified",
            severity=Severity.INFO,
            description=f"Package has verified Sigstore provenance (SLSA Level {slsa_level or 'N/A'})",
            details=f"Build source: {build_source or 'CI/CD'}. "
                    "Cryptographic attestations recorded in Rekor transparency log.",
            category=Category.AUTHENTICITY
        ))
    elif has_provenance and not is_verified:
        # Has provenance but couldn't fully verify
        factors.append(RiskFactor(
            name="Provenance Present (Unverified)",
            severity=Severity.INFO,
            description="Package has provenance attestations but verification incomplete",
            details="Sigstore attestations are present but could not be fully verified.",
            category=Category.AUTHENTICITY
        ))

    return factors
