# PURPOSE: Unit tests for typosquatting detection
import pytest
from utils.typosquat import check_typosquatting, normalize_package_name


class TestNormalizePackageName:
    def test_lowercase(self):
        assert normalize_package_name("LoDaSh") == "lodash"

    def test_scoped_package(self):
        assert normalize_package_name("@babel/core") == "core"

    def test_underscore_to_hyphen(self):
        assert normalize_package_name("my_package") == "my-package"

    def test_strip_whitespace(self):
        assert normalize_package_name("  lodash  ") == "lodash"


class TestTyposquatDetection:
    def test_exact_match_not_flagged(self):
        """Exact matches to popular packages should not be flagged."""
        result = check_typosquatting("lodash")
        assert result == []

    def test_typosquat_detected(self):
        """Typosquats should be detected with similarity scores."""
        result = check_typosquatting("lodahs")
        assert len(result) > 0
        assert result[0][0] == "lodash"
        assert result[0][1] >= 0.80

    def test_similar_to_express(self):
        """Similar names to express should be detected."""
        result = check_typosquatting("expresss")
        assert len(result) > 0
        assert "express" in [r[0] for r in result]

    def test_unrelated_package_not_flagged(self):
        """Unrelated package names should not trigger false positives."""
        result = check_typosquatting("my-unique-totally-different-package")
        assert result == []

    def test_threshold_respected(self):
        """Lower threshold should catch more matches."""
        strict_result = check_typosquatting("react", threshold=0.95)
        loose_result = check_typosquatting("recat", threshold=0.70)
        assert strict_result == []  # Exact match
        assert len(loose_result) > 0  # Typo caught


class TestPopularPackages:
    def test_popular_packages_not_typosquats(self):
        """All popular packages should not flag themselves."""
        popular = ["react", "express", "lodash", "axios", "typescript", "webpack"]
        for pkg in popular:
            result = check_typosquatting(pkg)
            assert result == [], f"{pkg} flagged itself as typosquat"
