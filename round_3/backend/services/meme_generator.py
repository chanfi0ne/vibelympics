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
    text = text.replace(",", "")        # remove commas (cause 404s when encoded)
    text = text.replace("(", "")        # remove parens
    text = text.replace(")", "")
    
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


TEMPLATES_DIR = Path(__file__).parent.parent / "static" / "templates"

# Track recently used templates to force variety
_recent_templates: list[str] = []
MAX_RECENT = 5  # Don't repeat last 5 templates


def get_random_template(exclude: list[str] = None) -> str:
    """Get a random template, excluding recently used ones."""
    available = list(BUNDLED_TEMPLATES.keys())
    
    # Exclude recently used
    exclude_set = set(_recent_templates)
    if exclude:
        exclude_set.update(exclude)
    
    candidates = [t for t in available if t not in exclude_set]
    
    # If all excluded, reset and use any
    if not candidates:
        candidates = available
    
    selected = random.choice(candidates)
    
    # Track as recently used
    _recent_templates.append(selected)
    if len(_recent_templates) > MAX_RECENT:
        _recent_templates.pop(0)
    
    return selected


# Bundled meme templates
BUNDLED_TEMPLATES = {
    "fine": {"file": "fine.png", "text_position": "bottom"},
    "drake": {"file": "drake.jpg", "text_position": "right"},
    "disaster": {"file": "disaster.jpg", "text_position": "bottom"},
    "fry": {"file": "fry.jpg", "text_position": "bottom"},
    "batman": {"file": "batman.jpg", "text_position": "bottom"},
    "buzz": {"file": "buzz.jpg", "text_position": "bottom"},
    "rollsafe": {"file": "rollsafe.jpg", "text_position": "bottom"},
    "doge": {"file": "doge.jpg", "text_position": "bottom"},
    "pigeon": {"file": "pigeon.jpg", "text_position": "bottom"},
    "afraid": {"file": "afraid.jpg", "text_position": "bottom"},
    "spiderman": {"file": "spiderman.jpg", "text_position": "bottom"},
    "changemymind": {"file": "changemymind.jpg", "text_position": "top"},
    "distractedbf": {"file": "distractedbf.jpg", "text_position": "bottom"},
    "surprisedpikachu": {"file": "surprisedpikachu.jpg", "text_position": "bottom"},
    "onedoesnot": {"file": "onedoesnot.jpg", "text_position": "bottom"},
    "harold": {"file": "harold.jpg", "text_position": "bottom"},
    "aliens": {"file": "aliens.jpg", "text_position": "bottom"},
}


def get_font(size: int = 32):
    """Get a bold font for meme text - Impact style preferred."""
    font_paths = [
        # Impact font - THE classic meme font (check macOS locations first)
        "/System/Library/Fonts/Supplemental/Impact.ttf",  # macOS Sonoma+
        "/Library/Fonts/Impact.ttf",  # macOS user-installed
        "/usr/share/fonts/truetype/msttcorefonts/Impact.ttf",  # Linux with MS fonts
        "/usr/share/fonts/truetype/impact.ttf",  # Linux alternate
        # Bold fallbacks that still look good
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",  # macOS
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Linux
        "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
    ]
    for font_path in font_paths:
        try:
            font = ImageFont.truetype(font_path, size)
            logger.info(f"Loaded font: {font_path} at size {size}")
            return font
        except (OSError, IOError):
            continue
    logger.warning(f"No fonts found, using default at size {size}")
    return ImageFont.load_default(size=size)


def draw_text_with_outline(draw: ImageDraw, text: str, x: int, y: int, font, outline: int = 5):
    """Draw single line of text with THICK black outline - classic meme style."""
    # Use stroke parameter for cleaner outline (Pillow 8.0+)
    try:
        draw.text(
            (x, y), text, font=font,
            fill=(255, 255, 255),
            stroke_width=outline,
            stroke_fill=(0, 0, 0)
        )
    except TypeError:
        # Fallback for older Pillow - manual outline
        for dx in range(-outline, outline + 1):
            for dy in range(-outline, outline + 1):
                if dx != 0 or dy != 0:
                    draw.text((x + dx, y + dy), text, font=font, fill=(0, 0, 0))
        draw.text((x, y), text, font=font, fill=(255, 255, 255))


def draw_meme_text(draw: ImageDraw, text: str, position: str, img_width: int, img_height: int, font):
    """Draw classic meme text - TOP and BOTTOM with huge Impact-style font."""
    text = text.upper()  # ALL CAPS - essential for meme style

    # Split into top/bottom if there's a period or newline
    if ". " in text:
        parts = text.split(". ", 1)
        top_text = parts[0]
        bottom_text = parts[1] if len(parts) > 1 else ""
    elif "\n" in text:
        parts = text.split("\n", 1)
        top_text = parts[0]
        bottom_text = parts[1] if len(parts) > 1 else ""
    else:
        # Single text - put at specified position
        top_text = text if position == "top" else ""
        bottom_text = text if position != "top" else ""

    font_size = font.size if hasattr(font, 'size') else 60
    line_height = int(font_size * 1.1)  # Tight line spacing for more text
    outline = max(4, font_size // 16)  # Visible but not excessive outline

    # Calculate wrap width - Impact font is VERY condensed (~0.45x font size)
    # Measure actual text to get accurate width
    test_text = "ABCDEFGHIJKLMNOP"  # 16 chars for better average
    try:
        bbox = draw.textbbox((0, 0), test_text, font=font)
        avg_char_width = (bbox[2] - bbox[0]) / len(test_text)
    except Exception:
        avg_char_width = font_size * 0.45  # Impact is VERY condensed

    # Fill image width minus margins (20px total for 10px on each side)
    margin = 10
    target_width = img_width - (margin * 2)
    wrap_chars = max(12, int(target_width / avg_char_width))

    # Allow up to 3 lines to avoid cutting off punchlines
    max_lines = 3

    # Minimum margin to prevent clipping
    margin = 10

    # Draw TOP text (stays at very top)
    if top_text:
        lines = textwrap.wrap(top_text, width=wrap_chars)[:max_lines]
        y = margin
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            # Center but ensure minimum margin on both sides
            x = max(margin, (img_width - text_width) // 2)
            draw_text_with_outline(draw, line, x, y, font, outline)
            y += line_height

    # Draw BOTTOM text (stays at very bottom)
    if bottom_text:
        lines = textwrap.wrap(bottom_text, width=wrap_chars)[:max_lines]
        total_height = len(lines) * line_height
        y = img_height - total_height - margin
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            # Center but ensure minimum margin on both sides
            x = max(margin, (img_width - text_width) // 2)
            draw_text_with_outline(draw, line, x, y, font, outline)
            y += line_height


def generate_meme_pillow(meme_id: str, caption: str, template_id: str | None = None) -> Path:
    """Generate meme with bundled template and Pillow.
    
    Args:
        meme_id: Unique ID for output file
        caption: The roast text to overlay
        template_id: Template to use (fine, drake, disaster, fry). Random if None.
    """
    ensure_output_dir()
    
    try:
        # Use AI-selected template if valid, otherwise pick random (excluding recent)
        if template_id and template_id in BUNDLED_TEMPLATES:
            # AI picked a valid template - trust it for content matching
            selected_id = template_id
            # Track as recently used for variety
            if selected_id in _recent_templates:
                _recent_templates.remove(selected_id)
            _recent_templates.append(selected_id)
            if len(_recent_templates) > MAX_RECENT:
                _recent_templates.pop(0)
        else:
            # Invalid or no template - pick random excluding recently used
            selected_id = get_random_template()
            if template_id:
                logger.warning(f"Unknown template '{template_id}', using random: {selected_id}")
        
        template = BUNDLED_TEMPLATES[selected_id]
        template_path = TEMPLATES_DIR / template["file"]
        
        if template_path.exists():
            img = Image.open(template_path).convert("RGB")
            logger.info(f"Using template: {selected_id}")
        else:
            img = Image.new("RGB", (600, 400), (30, 30, 30))
            logger.warning(f"Template not found: {template_path}, using plain background")
        
        draw = ImageDraw.Draw(img)

        # Scale font based on caption length - smaller for readability
        caption_len = len(caption)
        if caption_len > 80:
            # Long text - smaller font
            font_size = max(28, img.width // 18)
        elif caption_len > 50:
            # Medium text
            font_size = max(32, img.width // 16)
        else:
            # Short text
            font_size = max(36, img.width // 14)

        font = get_font(size=font_size)
        logger.info(f"Using font size {font_size}px for {img.width}x{img.height} image (caption len: {caption_len})")
        
        # Draw the caption with Impact-style text
        draw_meme_text(draw, caption, template["text_position"], img.width, img.height, font)
        
        output_path = OUTPUT_DIR / f"{meme_id}.png"
        img.save(output_path, "PNG")
        logger.info(f"Meme saved: {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Meme generation failed: {e}")
        raise


def generate_meme(meme_id: str, caption: str, template: str | None = None) -> Path:
    """Generate a meme using bundled templates and Pillow.

    Args:
        meme_id: Unique ID for the meme file
        caption: The roast text
        template: Template ID from AI (e.g., "fine", "drake", "disaster", "fry")
    """
    logger.info(f"Generating meme {meme_id} with template={template}")
    return generate_meme_pillow(meme_id, caption, template)


def get_meme_path(meme_id: str) -> Path | None:
    """Get path to existing meme if it exists."""
    path = OUTPUT_DIR / f"{meme_id}.png"
    return path if path.exists() else None
