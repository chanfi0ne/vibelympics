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
    # Also handles bare package names and dotted names (zope.interface, ruamel.yaml)
    req_pattern = re.compile(r'^([a-zA-Z0-9_.-]+)([<>=!~]+.*)?$')

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


def parse_go_mod(content: str) -> AnalysisResult:
    """Parse Go go.mod and extract dependencies."""
    deps = []
    errors = []
    
    lines = content.split('\n')
    in_require_block = False
    
    for line in lines:
        line = line.strip()
        
        # Skip empty lines and comments
        if not line or line.startswith('//'):
            continue
        
        # Detect require block start
        if line.startswith('require ('):
            in_require_block = True
            continue
        
        # Detect require block end
        if in_require_block and line == ')':
            in_require_block = False
            continue
        
        # Parse dependencies inside require block
        if in_require_block:
            # Format: github.com/gin-gonic/gin v1.9.1 // indirect
            parts = line.split()
            if len(parts) >= 2:
                name = parts[0]
                version = parts[1].lstrip('v')  # Remove 'v' prefix
                source = "indirect" if "// indirect" in line else "direct"
                deps.append(Dependency(name=name, version=version, source=source))
        
        # Parse single-line require: require github.com/pkg/errors v0.9.1
        elif line.startswith('require ') and '(' not in line:
            parts = line[8:].split()  # Skip "require "
            if len(parts) >= 2:
                name = parts[0]
                version = parts[1].lstrip('v')
                source = "indirect" if "// indirect" in line else "direct"
                deps.append(Dependency(name=name, version=version, source=source))
    
    return AnalysisResult(
        dependencies=deps,
        dep_count=len(deps),
        input_type="go_mod",
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


def detect_input_type(content: str) -> str:
    """Auto-detect input type based on content patterns."""
    content_stripped = content.strip()
    
    # Check for package.json (JSON with dependencies or devDependencies)
    if content_stripped.startswith("{"):
        try:
            data = json.loads(content_stripped)
            if isinstance(data, dict):
                if "dependencies" in data or "devDependencies" in data:
                    return "package_json"
                if "name" in data and "version" in data:
                    return "package_json"  # Likely a package.json
        except json.JSONDecodeError:
            pass
    
    # Check for requirements.txt patterns
    # Lines like: package==1.0.0, package>=1.0, package[extra], etc.
    lines = content_stripped.split('\n')
    requirements_patterns = 0
    for line in lines[:10]:  # Check first 10 lines
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        # requirements.txt patterns: ==, >=, <=, ~=, !=, or just package name
        if any(op in line for op in ['==', '>=', '<=', '~=', '!=', '>']):
            requirements_patterns += 1
        elif re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*(\[.*\])?$', line):
            requirements_patterns += 1
    
    if requirements_patterns >= 2:
        return "requirements_txt"
    
    # Check for go.mod
    if "module " in content_stripped and "go " in content_stripped:
        return "go_mod"
    
    # Check for single package (simple format: name or name@version)
    if '\n' not in content_stripped and len(content_stripped) < 100:
        if re.match(r'^@?[a-zA-Z][a-zA-Z0-9_/-]*(@[\d.]+)?$', content_stripped):
            return "single_package"
    
    # Default fallback
    return "unknown"


def analyze(input_type: str, content: str, auto_detect: bool = True) -> AnalysisResult:
    """Main entry point - routes to appropriate parser.
    
    Args:
        input_type: Specified input type
        content: The content to analyze
        auto_detect: If True, override input_type if content clearly matches another type
    """
    parsers = {
        "package_json": parse_package_json,
        "requirements_txt": parse_requirements_txt,
        "go_mod": parse_go_mod,
        "single_package": parse_single_package,
    }

    # Auto-detect input type if enabled
    if auto_detect:
        detected = detect_input_type(content)
        if detected != "unknown" and detected != input_type:
            # Content clearly matches a different type - use detected type
            input_type = detected

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
