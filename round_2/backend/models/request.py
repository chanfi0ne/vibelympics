# PURPOSE: Pydantic models for API request validation
from pydantic import BaseModel, Field, field_validator


class AuditRequest(BaseModel):
    """Request model for package audit endpoint."""

    package_name: str = Field(..., min_length=1, max_length=214, description="npm package name")

    @field_validator("package_name")
    @classmethod
    def validate_package_name(cls, v: str) -> str:
        """Validate npm package name format."""
        v = v.strip()
        if not v:
            raise ValueError("Package name cannot be empty")

        # Basic npm package name validation
        # Allow: lowercase, numbers, hyphens, underscores, dots, and scoped packages (@scope/name)
        if v.startswith(".") or v.startswith("_"):
            raise ValueError("Package name cannot start with . or _")

        # Check for invalid characters (basic check)
        # Allow @ and / for scoped packages like @babel/core
        invalid_chars = set(" !#$%^&*()+=[]{}|\\;:'\"<>,?~`")
        if any(char in invalid_chars for char in v):
            raise ValueError("Package name contains invalid characters")

        # Validate scoped package format
        if v.startswith("@"):
            if "/" not in v:
                raise ValueError("Scoped package must have format @scope/name")
            parts = v.split("/")
            if len(parts) != 2 or not parts[0][1:] or not parts[1]:
                raise ValueError("Invalid scoped package format")

        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"package_name": "lodash"},
                {"package_name": "@babel/core"},
            ]
        }
    }


class CompareRequest(BaseModel):
    """Request model for version comparison endpoint."""

    package_name: str = Field(..., min_length=1, max_length=214, description="npm package name")
    version_old: str = Field(..., min_length=1, max_length=50, description="Old version to compare")
    version_new: str = Field(..., min_length=1, max_length=50, description="New version to compare")

    @field_validator("package_name")
    @classmethod
    def validate_package_name(cls, v: str) -> str:
        """Validate npm package name format."""
        v = v.strip()
        if not v:
            raise ValueError("Package name cannot be empty")
        if v.startswith(".") or v.startswith("_"):
            raise ValueError("Package name cannot start with . or _")
        invalid_chars = set(" !#$%^&*()+=[]{}|\\;:'\"<>,?~`")
        if any(char in invalid_chars for char in v):
            raise ValueError("Package name contains invalid characters")
        if v.startswith("@"):
            if "/" not in v:
                raise ValueError("Scoped package must have format @scope/name")
            parts = v.split("/")
            if len(parts) != 2 or not parts[0][1:] or not parts[1]:
                raise ValueError("Invalid scoped package format")
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"package_name": "lodash", "version_old": "4.17.11", "version_new": "4.17.21"},
            ]
        }
    }
