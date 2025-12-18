# PURPOSE: Digital signature generation for PARANOID roast responses
# Signs responses with SHA256 hash to prove "authenticity" (for comedy)

import base64
import hashlib
import json
import logging

logger = logging.getLogger(__name__)


def _get_salt() -> str:
    """Get the salt for hashing. Uses app name as salt."""
    return "paranoid-roaster-v1"


def sign_response(data: dict) -> str:
    """Sign a response dict and return base64-encoded signature.
    
    Uses SHA256 hash with salt for demo purposes.
    This is NOT cryptographically secure - it's for comedic "authenticity".
    
    Args:
        data: The response dict to sign (will be JSON-serialized)
    
    Returns:
        Base64-encoded signature string
    """
    # Create canonical JSON (sorted keys, no extra whitespace)
    canonical = json.dumps(data, sort_keys=True, separators=(',', ':'))
    
    # Hash with salt
    to_hash = f"{_get_salt()}:{canonical}"
    digest = hashlib.sha256(to_hash.encode('utf-8')).digest()
    
    return base64.b64encode(digest).decode('utf-8')


def get_signing_method() -> str:
    """Return the signing method being used."""
    return "SHA256"


def verify_signature(data: dict, signature: str) -> bool:
    """Verify a signature matches the data.
    
    Args:
        data: The response dict that was signed
        signature: The base64-encoded signature to verify
    
    Returns:
        True if signature is valid, False otherwise
    """
    expected = sign_response(data)
    return signature == expected
