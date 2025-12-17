# PURPOSE: Dependency file parsing and analysis for PARANOID
# Parses package.json, requirements.txt, extracts dependencies

import json
import re
from dataclasses import dataclass


@dataclass
class Dependency:
    name: str
    version: str | None = None
    source: str = "unknown"  # dependencies, devDependencies, etc.


@dataclass
class AnalysisResult:
    dependencies: list[Dependency]
    dep_count: int
    input_type: str
    raw_content: str
    errors: list[str]


def parse_package_json(content: str) -> AnalysisResult:
    """Parse npm package.json and extract dependencies."""
    deps = []
    errors = []

    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        return AnalysisResult(
            dependencies=[],
            dep_count=0,
            input_type="package_json",
            raw_content=content,
            errors=[f"Invalid JSON: {str(e)}"]
        )

    # Extract dependencies
    for dep_type in ["dependencies", "devDependencies", "peerDependencies", "optionalDependencies"]:
        if dep_type in data and isinstance(data[dep_type], dict):
            for name, version in data[dep_type].items():
                deps.append(Dependency(
                    name=name,
                    version=str(version) if version else None,
                    source=dep_type
                ))

    return AnalysisResult(
        dependencies=deps,
        dep_count=len(deps),
        input_type="package_json",
        raw_content=content,
        errors=errors
    )


def parse_requirements_txt(content: str) -> AnalysisResult:
    """Parse Python requirements.txt and extract dependencies."""
    deps = []
    errors = []

    # Regex for requirement lines: package==version, package>=version, etc.
    # Also handles bare package names
    req_pattern = re.compile(r'^([a-zA-Z0-9_-]+)([<>=!~]+.*)?$')

    for line in content.split('\n'):
        line = line.strip()

        # Skip empty lines and comments
        if not line or line.startswith('#'):
            continue

        # Skip -r, -e, --index-url, etc.
        if line.startswith('-'):
            continue

        # Try to parse the requirement
        match = req_pattern.match(line.split('[')[0].strip())  # Remove extras like [dev]
        if match:
            name = match.group(1)
            version = match.group(2)
            deps.append(Dependency(
                name=name,
                version=version.strip() if version else None,
                source="requirements"
            ))

    return AnalysisResult(
        dependencies=deps,
        dep_count=len(deps),
        input_type="requirements_txt",
        raw_content=content,
        errors=errors
    )


def parse_single_package(content: str) -> AnalysisResult:
    """Parse a single package name, optionally with version."""
    content = content.strip()

    # Handle package@version or package==version
    if '@' in content:
        parts = content.split('@', 1)
        name, version = parts[0], parts[1]
    elif '==' in content:
        parts = content.split('==', 1)
        name, version = parts[0], parts[1]
    else:
        name = content
        version = None

    dep = Dependency(name=name, version=version, source="single")

    return AnalysisResult(
        dependencies=[dep],
        dep_count=1,
        input_type="single_package",
        raw_content=content,
        errors=[]
    )


def analyze(input_type: str, content: str) -> AnalysisResult:
    """Main entry point - routes to appropriate parser."""
    parsers = {
        "package_json": parse_package_json,
        "requirements_txt": parse_requirements_txt,
        "single_package": parse_single_package,
    }

    parser = parsers.get(input_type)
    if not parser:
        return AnalysisResult(
            dependencies=[],
            dep_count=0,
            input_type=input_type,
            raw_content=content,
            errors=[f"Unsupported input type: {input_type}. Try package_json, requirements_txt, or single_package."]
        )

    return parser(content)
