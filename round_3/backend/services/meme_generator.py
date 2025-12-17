# PURPOSE: Meme generator using memegen.link API for REAL memes
# Falls back to Pillow if API fails

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import textwrap
import random
import urllib.parse
import httpx
import logging

logger = logging.getLogger(__name__)

# H-2 Security: Constants for safe meme fetching
MEMEGEN_ALLOWED_HOSTS = ["api.memegen.link", "memegen.link"]  # Allow CDN redirects
MAX_MEME_SIZE = 5 * 1024 * 1024  # 5MB max
MEME_FETCH_TIMEOUT = 5.0  # seconds
MAX_REDIRECTS = 3  # Limit redirect chain length

# Output directory
OUTPUT_DIR = Path(__file__).parent.parent / "static" / "memes"

# memegen.link API - no auth required!
MEMEGEN_API = "https://api.memegen.link/images"

# Meme templates with security-themed top text
MEME_TEMPLATES = [
    {"id": "fine", "top": "This is fine", "bottom_prefix": ""},
    {"id": "doge", "top": "Such dependencies", "bottom_prefix": "Very "},
    {"id": "drake", "top": "Reading the CVE list", "bottom_prefix": ""},
    {"id": "buzz", "top": "Vulnerabilities", "bottom_prefix": ""},
    {"id": "batman", "top": "Let me just npm install--", "bottom_prefix": ""},
    {"id": "afraid", "top": "I'm afraid", "bottom_prefix": ""},
    {"id": "aliens", "top": "", "bottom_prefix": "Dependencies"},
    {"id": "rollsafe", "top": "Can't have vulnerabilities", "bottom_prefix": "If you "},
    {"id": "success", "top": "Zero CVEs in production", "bottom_prefix": ""},
    {"id": "boat", "top": "", "bottom_prefix": "I should audit my "},
    {"id": "fry", "top": "", "bottom_prefix": "Not sure if secure or "},
    {"id": "pigeon", "top": "Is this", "bottom_prefix": ""},
]


def ensure_output_dir():
    """Create output directory if it doesn't exist."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def encode_text(text: str) -> str:
    """Encode text for memegen URL (replace spaces with _, special chars).

    See: https://memegen.link/docs#special-characters
    """
    # Strip problematic trailing punctuation BEFORE encoding
    text = text.rstrip(".!?,;:")
    
    # memegen special character encoding (order matters!)
    text = text.replace("-", "--")      # hyphen -> --
    text = text.replace("_", "__")      # underscore -> __
    text = text.replace(" ", "_")       # space -> _
    text = text.replace("?", "~q")      # question mark -> ~q
    text = text.replace("#", "~h")      # hash -> ~h
    text = text.replace("/", "~s")      # slash -> ~s
    text = text.replace(".", "~p")      # period -> ~p (mid-text only now)
    text = text.replace("'", "")        # remove apostrophes (cause 404s)
    text = text.replace('"', "")        # remove quotes (cause 404s)
    text = text.replace(":", "~c")      # colon -> ~c
    text = text.replace(";", "~c")      # semicolon -> ~c
    text = text.replace("%", "")        # remove percent signs
    
    # Clean up any triple underscores from removed chars
    while "___" in text:
        text = text.replace("___", "__")
    
    # Remove problematic chars at end
    text = text.rstrip("_~")
    
    return urllib.parse.quote(text, safe="_~-")


def validate_memegen_url(url: str, allow_any_path: bool = False) -> bool:
    """H-2 Security: Validate that URL is from allowed memegen hosts."""
    try:
        parsed = urllib.parse.urlparse(url)
        host_ok = parsed.scheme == "https" and parsed.netloc in MEMEGEN_ALLOWED_HOSTS
        path_ok = allow_any_path or parsed.path.startswith("/images/")
        return host_ok and path_ok
    except Exception:
        return False


def generate_meme_memegen(meme_id: str, caption: str, template_id: str | None = None) -> Path | None:
    """Generate a real meme using memegen.link API (no auth needed!).

    H-2 Security: Uses httpx with timeout, content-type validation, and size limits.

    Args:
        meme_id: Unique ID for the meme file
        caption: The roast text (goes on bottom of meme)
        template_id: Specific template to use (e.g., "fine", "drake"). If None, picks random.
    """
    ensure_output_dir()

    # Use specified template or pick random
    if template_id:
        # AI specified a template - split caption between top and bottom
        selected_template_id = template_id
        # Split at sentence boundary or midpoint
        if ". " in caption:
            parts = caption.split(". ", 1)
            top_text = parts[0] + "."
            bottom_text = parts[1] if len(parts) > 1 else ""
        else:
            # Split at midpoint by words
            words = caption.split()
            mid = len(words) // 2
            top_text = " ".join(words[:mid]) if mid > 0 else ""
            bottom_text = " ".join(words[mid:]) if mid > 0 else caption
    else:
        # Fallback mode - use pre-defined templates with prefixes
        template = random.choice(MEME_TEMPLATES)
        selected_template_id = template["id"]
        if template["top"]:
            top_text = template["top"]
            bottom_text = template["bottom_prefix"] + caption
        else:
            words = caption.split()
            mid = len(words) // 2
            top_text = " ".join(words[:mid]) if mid > 0 else caption
            bottom_text = template["bottom_prefix"] + " ".join(words[mid:]) if mid > 0 else ""

    # Truncate for URL length limits (memegen has ~60 char limit per line)
    top_encoded = encode_text(top_text[:60]) if top_text else "_"
    bottom_encoded = encode_text(bottom_text[:60]) if bottom_text else "_"
    
    # Build URL: https://api.memegen.link/images/{template}/{top}/{bottom}.png
    meme_url = f"{MEMEGEN_API}/{selected_template_id}/{top_encoded}/{bottom_encoded}.png"
    
    # H-2 Security: Validate URL before fetching
    if not validate_memegen_url(meme_url):
        logger.warning(f"Invalid meme URL rejected: {meme_url[:100]}")
        return None
    
    try:
        # H-2 Security: Manually follow redirects with validation
        current_url = meme_url
        with httpx.Client(timeout=MEME_FETCH_TIMEOUT, follow_redirects=False) as client:
            for redirect_count in range(MAX_REDIRECTS + 1):
                response = client.get(current_url)

                # Handle redirects safely
                if response.status_code in (301, 302, 303, 307, 308):
                    redirect_url = response.headers.get("location", "")
                    # Handle relative redirects
                    if redirect_url.startswith("/"):
                        redirect_url = f"https://api.memegen.link{redirect_url}"
                    logger.info(f"Meme redirect to: {redirect_url[:100]}")
                    # Validate redirect destination is still memegen
                    if not validate_memegen_url(redirect_url, allow_any_path=True):
                        logger.warning(f"Blocked redirect to untrusted URL: {redirect_url[:100]}")
                        return None
                    current_url = redirect_url
                    continue

                # Validate final response status
                if response.status_code != 200:
                    logger.warning(f"Meme API returned {response.status_code}")
                    return None

                # H-2 Security: Validate content-type is an image
                content_type = response.headers.get("content-type", "")
                if not content_type.startswith("image/"):
                    logger.warning(f"Invalid content-type from meme API: {content_type}")
                    return None

                # H-2 Security: Validate size limit
                content_length = len(response.content)
                if content_length > MAX_MEME_SIZE:
                    logger.warning(f"Meme too large: {content_length} bytes")
                    return None

                if content_length < 1000:
                    logger.warning(f"Meme too small (likely error): {content_length} bytes")
                    return None

                # Write file
                output_path = OUTPUT_DIR / f"{meme_id}.png"
                output_path.write_bytes(response.content)
                return output_path

            # Too many redirects
            logger.warning(f"Too many redirects ({MAX_REDIRECTS})")
            return None

    except httpx.TimeoutException:
        logger.warning("Meme API timeout")
    except Exception as e:
        logger.warning(f"Meme API failed: {e}")
    
    return None


def generate_meme_fallback(meme_id: str, caption: str) -> Path:
    """Fallback: generate simple meme with Pillow if API fails."""
    logger.info(f"Using Pillow fallback for meme {meme_id}")
    ensure_output_dir()
    
    try:
        img = Image.new("RGB", (600, 400), (30, 30, 30))
        draw = ImageDraw.Draw(img)
        
        # Try to load a font, fall back to default
        font = None
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
        ]
        for font_path in font_paths:
            try:
                font = ImageFont.truetype(font_path, 24)
                break
            except (OSError, IOError):
                continue
        
        if font is None:
            font = ImageFont.load_default()
            logger.info("Using default font (no TTF found)")
        
        # Draw text with wrapping
        lines = textwrap.wrap(caption, width=35)
        y = 150
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            x = (600 - (bbox[2] - bbox[0])) // 2
            # Draw outline
            for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
                draw.text((x + dx, y + dy), line, font=font, fill=(0, 0, 0))
            draw.text((x, y), line, font=font, fill=(255, 255, 255))
            y += 40
        
        # Add watermark
        draw.text((200, 370), "PARANOID // SBOM ROAST", font=font, fill=(100, 100, 100))
        
        output_path = OUTPUT_DIR / f"{meme_id}.png"
        img.save(output_path, "PNG")
        logger.info(f"Pillow fallback saved: {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Pillow fallback failed: {e}")
        raise


def generate_meme(meme_id: str, caption: str, template: str | None = None) -> Path:
    """Generate a meme - tries memegen.link API first, falls back to Pillow.

    Args:
        meme_id: Unique ID for the meme file
        caption: The roast text
        template: Template ID from AI (e.g., "fine", "drake"). None for random.
    """
    # Try real meme generation first
    result = generate_meme_memegen(meme_id, caption, template_id=template)
    if result:
        return result
    
    # Fallback to simple generation
    return generate_meme_fallback(meme_id, caption)


def get_meme_path(meme_id: str) -> Path | None:
    """Get path to existing meme if it exists."""
    path = OUTPUT_DIR / f"{meme_id}.png"
    return path if path.exists() else None
