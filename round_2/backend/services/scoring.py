# PURPOSE: Risk score calculation and categorization
from typing import List, Dict, Tuple
from models.response import RiskFactor, Severity, Category, RadarScores


# Category weights - authenticity and security issues are more severe
CATEGORY_MULTIPLIERS = {
    Category.AUTHENTICITY: 1.5,  # Typosquatting, provenance issues
    Category.SECURITY: 1.5,      # Vulnerabilities, dangerous scripts
    Category.MAINTENANCE: 1.0,   # Maintainer issues, age
    Category.REPUTATION: 0.8,    # Download counts, community trust
}

# High-risk categories where critical findings should escalate overall risk
HIGH_RISK_CATEGORIES = {Category.AUTHENTICITY, Category.SECURITY}


def calculate_risk_score(factors: List[RiskFactor]) -> Tuple[int, bool]:
    """
    Calculate overall risk score (0-100).

    Severity base points:
        Critical: 25 points
        High: 15 points
        Medium: 8 points
        Low: 3 points
        Info: 0 points

    Category multipliers applied:
        Authenticity: 1.5x (typosquatting is serious)
        Security: 1.5x (vulnerabilities are serious)
        Maintenance: 1.0x (standard)
        Reputation: 0.8x (less critical)

    Returns:
        Tuple of (score, has_critical_in_high_risk_category)
    """
    severity_points = {
        Severity.CRITICAL: 25,
        Severity.HIGH: 15,
        Severity.MEDIUM: 8,
        Severity.LOW: 3,
        Severity.INFO: 0,
    }

    total = 0.0
    has_critical_high_risk = False

    for factor in factors:
        base_points = severity_points[factor.severity]
        multiplier = CATEGORY_MULTIPLIERS.get(factor.category, 1.0)
        total += base_points * multiplier

        # Track if there's a critical finding in a high-risk category
        if factor.severity == Severity.CRITICAL and factor.category in HIGH_RISK_CATEGORIES:
            has_critical_high_risk = True

    # Cap at 100
    return min(100, int(total)), has_critical_high_risk


def get_risk_level(score: int, has_critical_high_risk: bool = False) -> str:
    """
    Map score to risk level.

    Base thresholds:
        76-100: critical
        51-75: high
        26-50: medium
        0-25: low

    Special rule: If there's a CRITICAL finding in authenticity or security,
    the minimum risk level is HIGH (regardless of score).
    """
    # Critical finding in high-risk category forces at least HIGH
    if has_critical_high_risk and score < 51:
        return "high"

    if score >= 76:
        return "critical"
    elif score >= 51:
        return "high"
    elif score >= 26:
        return "medium"
    else:
        return "low"


def calculate_radar_scores(factors: List[RiskFactor]) -> RadarScores:
    """
    Calculate category-specific scores for radar chart.

    Returns:
        {
            "authenticity": 95,
            "maintenance": 70,
            "security": 90,
            "reputation": 98
        }

    Each category starts at 100, deductions based on findings.
    """
    # Start all categories at 100
    scores = {
        Category.AUTHENTICITY: 100,
        Category.MAINTENANCE: 100,
        Category.SECURITY: 100,
        Category.REPUTATION: 100,
    }

    # Deduction amounts by severity
    deductions = {
        Severity.CRITICAL: 40,
        Severity.HIGH: 25,
        Severity.MEDIUM: 15,
        Severity.LOW: 5,
        Severity.INFO: 0,
    }

    # Apply deductions for each factor
    for factor in factors:
        category = factor.category
        deduction = deductions[factor.severity]
        scores[category] = max(0, scores[category] - deduction)

    # Convert to RadarScores model
    return RadarScores(
        authenticity=scores[Category.AUTHENTICITY],
        maintenance=scores[Category.MAINTENANCE],
        security=scores[Category.SECURITY],
        reputation=scores[Category.REPUTATION],
    )
