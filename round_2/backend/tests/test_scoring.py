# PURPOSE: Unit tests for risk scoring
import pytest
from services.scoring import (
    calculate_risk_score,
    get_risk_level,
    calculate_radar_scores,
)
from models.response import RiskFactor, Severity, Category


def make_factor(severity: Severity, category: Category) -> RiskFactor:
    """Helper to create test risk factors."""
    return RiskFactor(
        name="Test Factor",
        severity=severity,
        description="Test description",
        details="Test details",
        category=category
    )


class TestCalculateRiskScore:
    def test_no_factors_zero_score(self):
        """No risk factors should result in score of 0."""
        score, has_critical = calculate_risk_score([])
        assert score == 0
        assert has_critical is False

    def test_single_critical_high_score(self):
        """Single critical factor should give significant score."""
        factors = [make_factor(Severity.CRITICAL, Category.SECURITY)]
        score, has_critical = calculate_risk_score(factors)
        assert score >= 25
        assert has_critical is True

    def test_category_multipliers(self):
        """Security/Authenticity factors should score higher."""
        security_factor = [make_factor(Severity.HIGH, Category.SECURITY)]
        reputation_factor = [make_factor(Severity.HIGH, Category.REPUTATION)]
        
        security_score, _ = calculate_risk_score(security_factor)
        reputation_score, _ = calculate_risk_score(reputation_factor)
        
        assert security_score > reputation_score

    def test_score_capped_at_100(self):
        """Score should never exceed 100."""
        factors = [make_factor(Severity.CRITICAL, Category.SECURITY) for _ in range(10)]
        score, _ = calculate_risk_score(factors)
        assert score == 100

    def test_info_severity_no_points(self):
        """INFO severity should add 0 points."""
        factors = [make_factor(Severity.INFO, Category.REPUTATION)]
        score, _ = calculate_risk_score(factors)
        assert score == 0


class TestGetRiskLevel:
    def test_low_risk(self):
        assert get_risk_level(0) == "low"
        assert get_risk_level(25) == "low"

    def test_medium_risk(self):
        assert get_risk_level(26) == "medium"
        assert get_risk_level(50) == "medium"

    def test_high_risk(self):
        assert get_risk_level(51) == "high"
        assert get_risk_level(75) == "high"

    def test_critical_risk(self):
        assert get_risk_level(76) == "critical"
        assert get_risk_level(100) == "critical"

    def test_critical_in_high_risk_category_elevates(self):
        """Critical finding in high-risk category should elevate to at least high."""
        # Low score but has critical in security
        assert get_risk_level(20, has_critical_high_risk=True) == "high"


class TestCalculateRadarScores:
    def test_no_factors_all_100(self):
        """No factors should result in all categories at 100."""
        scores = calculate_radar_scores([])
        assert scores.authenticity == 100
        assert scores.maintenance == 100
        assert scores.security == 100
        assert scores.reputation == 100

    def test_critical_factor_reduces_category(self):
        """Critical factor should reduce its category significantly."""
        factors = [make_factor(Severity.CRITICAL, Category.SECURITY)]
        scores = calculate_radar_scores(factors)
        assert scores.security == 60  # 100 - 40
        assert scores.authenticity == 100
        assert scores.maintenance == 100
        assert scores.reputation == 100

    def test_multiple_factors_same_category(self):
        """Multiple factors in same category should stack deductions."""
        factors = [
            make_factor(Severity.HIGH, Category.MAINTENANCE),
            make_factor(Severity.MEDIUM, Category.MAINTENANCE),
        ]
        scores = calculate_radar_scores(factors)
        assert scores.maintenance == 60  # 100 - 25 - 15

    def test_score_floors_at_zero(self):
        """Category scores should not go below 0."""
        factors = [make_factor(Severity.CRITICAL, Category.AUTHENTICITY) for _ in range(5)]
        scores = calculate_radar_scores(factors)
        assert scores.authenticity == 0
