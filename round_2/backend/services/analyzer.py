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

        factors.append(RiskFactor(
            name=f"Known Vulnerability{' (' + cve_id + ')' if cve_id else ''}",
            severity=severity,
            description=summary,
            details=advisory.get("description", ""),
            category=Category.SECURITY
        ))

    return factors
