# PURPOSE: Pydantic models for API response serialization
from enum import Enum
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class Severity(str, Enum):
    """Risk severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class Category(str, Enum):
    """Risk factor categories for radar chart."""
    AUTHENTICITY = "authenticity"
    MAINTENANCE = "maintenance"
    SECURITY = "security"
    REPUTATION = "reputation"


class RiskFactor(BaseModel):
    """Individual security finding."""
    name: str = Field(..., description="Brief finding name")
    severity: Severity = Field(..., description="Risk severity level")
    description: str = Field(..., description="Human-readable explanation")
    details: Optional[str] = Field(None, description="Specific evidence or details")
    category: Category = Field(..., description="Risk category for radar chart")


class PackageMetadata(BaseModel):
    """Package metadata from npm registry."""
    description: Optional[str] = Field(None, description="Package description")
    author: Optional[str] = Field(None, description="Package author")
    license: Optional[str] = Field(None, description="Package license")
    repository: Optional[str] = Field(None, description="Repository URL")
    created: Optional[str] = Field(None, description="Package creation date")
    modified: Optional[str] = Field(None, description="Last modification date")
    maintainers: List[str] = Field(default_factory=list, description="List of maintainer usernames")
    downloads_weekly: Optional[int] = Field(None, description="Weekly download count")
    versions_count: Optional[int] = Field(None, description="Total number of versions")


class RepositoryVerification(BaseModel):
    """GitHub repository verification results."""
    exists: bool = Field(..., description="Repository exists on GitHub")
    verified: bool = Field(..., description="Repository verified and accessible")
    stars: Optional[int] = Field(None, description="GitHub stars count")
    forks: Optional[int] = Field(None, description="GitHub forks count")
    archived: Optional[bool] = Field(None, description="Repository archived status")
    last_updated: Optional[str] = Field(None, description="Last update timestamp")


class RadarScores(BaseModel):
    """Category scores for radar chart visualization."""
    authenticity: int = Field(..., ge=0, le=100, description="Authenticity score (0-100)")
    maintenance: int = Field(..., ge=0, le=100, description="Maintenance score (0-100)")
    security: int = Field(..., ge=0, le=100, description="Security score (0-100)")
    reputation: int = Field(..., ge=0, le=100, description="Reputation score (0-100)")


class AuditResponse(BaseModel):
    """Complete audit response."""
    package_name: str = Field(..., description="Audited package name")
    version: Optional[str] = Field(None, description="Latest package version")
    risk_score: int = Field(..., ge=0, le=100, description="Overall risk score (0-100)")
    risk_level: str = Field(..., description="Risk level: low/medium/high/critical")
    factors: List[RiskFactor] = Field(default_factory=list, description="Security findings")
    metadata: PackageMetadata = Field(..., description="Package metadata")
    radar_scores: RadarScores = Field(..., description="Category scores for radar chart")
    repository_verification: Optional[RepositoryVerification] = Field(
        None, description="Repository verification results"
    )
    timestamp: str = Field(..., description="Audit timestamp")
    audit_duration_ms: int = Field(..., description="Audit duration in milliseconds")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    timestamp: str = Field(..., description="Current timestamp")


class VulnerabilityInfo(BaseModel):
    """Vulnerability information for comparison."""
    id: str = Field(..., description="Vulnerability ID (GHSA or CVE)")
    cve_id: Optional[str] = Field(None, description="CVE identifier if available")
    severity: str = Field(..., description="Severity level")
    summary: str = Field(..., description="Brief description")
    fixed_in: Optional[str] = Field(None, description="Version where fixed")


class VersionAnalysis(BaseModel):
    """Analysis results for a specific version."""
    version: str = Field(..., description="Package version")
    vulnerabilities: List[VulnerabilityInfo] = Field(default_factory=list, description="CVEs affecting this version")
    vuln_count: int = Field(..., description="Total vulnerability count")
    critical_count: int = Field(0, description="Critical severity count")
    high_count: int = Field(0, description="High severity count")
    medium_count: int = Field(0, description="Medium severity count")
    low_count: int = Field(0, description="Low severity count")


class CompareResponse(BaseModel):
    """Version comparison response."""
    package_name: str = Field(..., description="Package name")
    old_version: VersionAnalysis = Field(..., description="Old version analysis")
    new_version: VersionAnalysis = Field(..., description="New version analysis")
    vulnerabilities_fixed: List[VulnerabilityInfo] = Field(default_factory=list, description="CVEs fixed in new version")
    vulnerabilities_new: List[VulnerabilityInfo] = Field(default_factory=list, description="New CVEs in new version")
    risk_reduction: int = Field(..., description="Risk score reduction (positive = improvement)")
    recommendation: str = Field(..., description="Upgrade recommendation")
    timestamp: str = Field(..., description="Comparison timestamp")
    duration_ms: int = Field(..., description="Comparison duration in milliseconds")
