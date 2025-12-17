# PURPOSE: Tests for dependency analyzer - confirms parsing works correctly
import pytest
import sys
sys.path.insert(0, '/Users/jonc/Workspace/vibelympics-review/round_3/backend')

from services.analyzer import (
    analyze,
    parse_package_json,
    parse_requirements_txt,
    parse_single_package,
)


class TestPackageJsonParser:
    """Tests for package.json parsing."""

    def test_basic_dependencies(self):
        content = '{"dependencies": {"lodash": "^4.17.21", "express": "~4.18.0"}}'
        result = parse_package_json(content)
        
        assert result.dep_count == 2
        assert len(result.errors) == 0
        names = [d.name for d in result.dependencies]
        assert "lodash" in names
        assert "express" in names

    def test_all_dep_types(self):
        content = '''{
            "dependencies": {"react": "^18.0.0"},
            "devDependencies": {"jest": "^29.0.0"},
            "peerDependencies": {"react-dom": "^18.0.0"},
            "optionalDependencies": {"fsevents": "^2.0.0"}
        }'''
        result = parse_package_json(content)
        
        assert result.dep_count == 4
        sources = [d.source for d in result.dependencies]
        assert "dependencies" in sources
        assert "devDependencies" in sources
        assert "peerDependencies" in sources
        assert "optionalDependencies" in sources

    def test_invalid_json(self):
        content = '{"dependencies": {broken'
        result = parse_package_json(content)
        
        assert result.dep_count == 0
        assert len(result.errors) > 0
        assert "Invalid JSON" in result.errors[0]

    def test_empty_dependencies(self):
        content = '{"name": "test-package", "version": "1.0.0"}'
        result = parse_package_json(content)
        
        assert result.dep_count == 0
        assert len(result.errors) == 0


class TestRequirementsTxtParser:
    """Tests for requirements.txt parsing."""

    def test_basic_requirements(self):
        content = """flask==2.0.0
requests>=2.25.0
numpy"""
        result = parse_requirements_txt(content)
        
        assert result.dep_count == 3
        names = [d.name for d in result.dependencies]
        assert "flask" in names
        assert "requests" in names
        assert "numpy" in names

    def test_comments_skipped(self):
        content = """# This is a comment
flask==2.0.0
# Another comment
requests>=2.25.0"""
        result = parse_requirements_txt(content)
        
        assert result.dep_count == 2

    def test_directives_skipped(self):
        content = """-r base.txt
-e git+https://github.com/user/repo.git
--index-url https://pypi.org/simple
flask==2.0.0"""
        result = parse_requirements_txt(content)
        
        assert result.dep_count == 1
        assert result.dependencies[0].name == "flask"

    def test_dotted_package_names(self):
        """Bug fix test: packages with dots must be parsed correctly."""
        content = """zope.interface==5.0.0
ruamel.yaml>=0.17.0
python-dateutil==2.8.2"""
        result = parse_requirements_txt(content)
        
        assert result.dep_count == 3
        names = [d.name for d in result.dependencies]
        assert "zope.interface" in names
        assert "ruamel.yaml" in names
        assert "python-dateutil" in names

    def test_version_specifiers(self):
        content = """pkg1==1.0.0
pkg2>=2.0.0
pkg3<=3.0.0
pkg4!=4.0.0
pkg5~=5.0.0
pkg6>6.0.0
pkg7<7.0.0"""
        result = parse_requirements_txt(content)
        
        assert result.dep_count == 7
        
    def test_extras_stripped(self):
        content = "requests[security]==2.25.0"
        result = parse_requirements_txt(content)
        
        assert result.dep_count == 1
        assert result.dependencies[0].name == "requests"


class TestSinglePackageParser:
    """Tests for single package parsing."""

    def test_package_with_at_version(self):
        result = parse_single_package("lodash@4.17.21")
        
        assert result.dep_count == 1
        assert result.dependencies[0].name == "lodash"
        assert result.dependencies[0].version == "4.17.21"

    def test_package_with_equals_version(self):
        result = parse_single_package("flask==2.0.0")
        
        assert result.dep_count == 1
        assert result.dependencies[0].name == "flask"
        assert result.dependencies[0].version == "2.0.0"

    def test_package_without_version(self):
        result = parse_single_package("express")
        
        assert result.dep_count == 1
        assert result.dependencies[0].name == "express"
        assert result.dependencies[0].version is None


class TestAnalyzeRouter:
    """Tests for the main analyze() entry point."""

    def test_routes_to_package_json(self):
        result = analyze("package_json", '{"dependencies": {"x": "1.0.0"}}')
        assert result.input_type == "package_json"
        assert result.dep_count == 1

    def test_routes_to_requirements_txt(self):
        result = analyze("requirements_txt", "flask==2.0.0")
        assert result.input_type == "requirements_txt"
        assert result.dep_count == 1

    def test_routes_to_single_package(self):
        result = analyze("single_package", "lodash@4.17.21")
        assert result.input_type == "single_package"
        assert result.dep_count == 1

    def test_unsupported_type(self):
        result = analyze("unknown_format", "some content")
        assert len(result.errors) > 0
        assert "Unsupported" in result.errors[0]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
