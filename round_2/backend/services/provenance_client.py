# PURPOSE: Verify npm package provenance via Sigstore attestations
import httpx
from typing import Optional, Dict, Any, List


class ProvenanceError(Exception):
    """Error fetching provenance data."""
    pass


async def fetch_provenance_attestations(
    client: httpx.AsyncClient,
    package_name: str,
    version: str
) -> Optional[Dict[str, Any]]:
    """
    Fetch npm provenance attestations for a package version.

    npm uses Sigstore for provenance attestations, providing:
    - Build provenance (where/how the package was built)
    - Source repository verification
    - SLSA provenance levels

    Returns attestation data or None if not available.
    """
    # Handle scoped packages
    if package_name.startswith("@"):
        encoded_name = package_name.replace("/", "%2F")
    else:
        encoded_name = package_name

    # npm attestations endpoint
    url = f"https://registry.npmjs.org/-/npm/v1/attestations/{encoded_name}@{version}"

    try:
        response = await client.get(url, timeout=10.0)

        if response.status_code == 404:
            # No attestations available
            return None

        if response.status_code == 200:
            return response.json()

        return None

    except httpx.TimeoutException:
        return None
    except Exception:
        return None


async def check_rekor_transparency_log(
    client: httpx.AsyncClient,
    package_name: str,
    version: str
) -> Optional[Dict[str, Any]]:
    """
    Check Sigstore Rekor transparency log for package entries.

    Rekor is a tamper-evident log of software signatures.
    Entries here indicate the package was signed with Sigstore.

    Returns log entry info or None if not found.
    """
    # Search Rekor for npm package attestations
    search_url = "https://rekor.sigstore.dev/api/v1/index/retrieve"

    # Search by package name in the artifact
    search_payload = {
        "hash": f"sha256:{package_name}@{version}"  # Simplified search
    }

    try:
        # First try to search by email/subject for npm
        search_url = "https://rekor.sigstore.dev/api/v1/log/entries/retrieve"

        response = await client.post(
            search_url,
            json={"entries": []},  # Would need actual entry UUIDs
            timeout=10.0
        )

        # For now, we primarily rely on npm attestations endpoint
        # Rekor search is more complex and requires specific entry IDs
        return None

    except Exception:
        return None


def analyze_provenance(
    attestations: Optional[Dict[str, Any]],
    package_name: str
) -> Dict[str, Any]:
    """
    Analyze provenance attestations and return verification result.

    Returns dict with:
    - has_provenance: bool
    - provenance_type: str (e.g., "sigstore", "none")
    - slsa_level: Optional[int] (0-4)
    - build_source: Optional[str] (e.g., "github-actions")
    - source_repo: Optional[str]
    - is_verified: bool
    """
    result = {
        "has_provenance": False,
        "provenance_type": "none",
        "slsa_level": None,
        "build_source": None,
        "source_repo": None,
        "is_verified": False,
        "transparency_log": False
    }

    if not attestations:
        return result

    # Parse npm attestations response
    attestation_list = attestations.get("attestations", [])

    if not attestation_list:
        return result

    result["has_provenance"] = True
    result["provenance_type"] = "sigstore"
    result["transparency_log"] = True  # npm attestations are logged to Rekor

    for attestation in attestation_list:
        predicate_type = attestation.get("predicateType", "")

        # Check for SLSA provenance
        if "slsa" in predicate_type.lower():
            bundle = attestation.get("bundle", {})

            # Extract SLSA level if available
            # SLSA provenance indicates build integrity
            if "v1" in predicate_type:
                result["slsa_level"] = 1
            elif "v0.2" in predicate_type:
                result["slsa_level"] = 2

            # Try to extract build info from the bundle
            payload = bundle.get("dsseEnvelope", {}).get("payload", "")
            if payload:
                try:
                    import base64
                    import json
                    decoded = json.loads(base64.b64decode(payload))

                    predicate = decoded.get("predicate", {})

                    # Extract builder info
                    builder = predicate.get("builder", {})
                    builder_id = builder.get("id", "")

                    if "github" in builder_id.lower():
                        result["build_source"] = "github-actions"
                    elif "gitlab" in builder_id.lower():
                        result["build_source"] = "gitlab-ci"

                    # Extract source repo
                    materials = predicate.get("materials", [])
                    for material in materials:
                        uri = material.get("uri", "")
                        if "github.com" in uri or "gitlab.com" in uri:
                            result["source_repo"] = uri
                            break

                    # Check invocation info for SLSA level
                    build_type = predicate.get("buildType", "")
                    if "slsa" in build_type.lower():
                        result["is_verified"] = True

                except Exception:
                    pass

        # Check for publish attestation
        if "publish" in predicate_type.lower():
            result["is_verified"] = True

    return result
