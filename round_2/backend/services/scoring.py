# PURPOSE: Risk score calculation and categorization
from typing import List, Dict
from models.response import RiskFactor, Severity, Category, RadarScores


def calculate_risk_score(factors: List[RiskFactor]) -> int:
    """
    Calculate overall risk score (0-100).

    Severity weights:
        Critical: 25 points
        High: 15 points
        Medium: 8 points
        Low: 3 points
        Info: 0 points

    Score is capped at 100.
    """
    severity_points = {
        Severity.CRITICAL: 25,
        Severity.HIGH: 15,
        Severity.MEDIUM: 8,
        Severity.LOW: 3,
        Severity.INFO: 0,
    }

    total = sum(severity_points[factor.severity] for factor in factors)

    # Cap at 100
    return min(100, total)


def get_risk_level(score: int) -> str:
    """
    Map score to risk level.

    76-100: critical
    51-75: high
    26-50: medium
    0-25: low
    """
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
