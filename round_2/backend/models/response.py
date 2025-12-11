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
