# PURPOSE: Meme generator using memegen.link API for REAL memes
# Falls back to Pillow if API fails

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import textwrap
import random
import urllib.request
import urllib.parse

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
    """Encode text for memegen URL (replace spaces with _, special chars)."""
    # memegen uses _ for spaces and -- for underscores
    text = text.replace("_", "__").replace(" ", "_").replace("?", "~q").replace("#", "~h")
    return urllib.parse.quote(text, safe="_~")


def generate_meme_memegen(meme_id: str, caption: str) -> Path | None:
    """Generate a real meme using memegen.link API (no auth needed!)."""
    ensure_output_dir()
    
    template = random.choice(MEME_TEMPLATES)
    
    # Build the caption
    if template["top"]:
        top_text = template["top"]
        bottom_text = template["bottom_prefix"] + caption
    else:
        words = caption.split()
        mid = len(words) // 2
        top_text = " ".join(words[:mid]) if mid > 0 else caption
        bottom_text = template["bottom_prefix"] + " ".join(words[mid:]) if mid > 0 else ""
    
    # Truncate for URL length limits
    top_encoded = encode_text(top_text[:50])
    bottom_encoded = encode_text(bottom_text[:80])
    
    # Build URL: https://api.memegen.link/images/{template}/{top}/{bottom}.png
    meme_url = f"{MEMEGEN_API}/{template['id']}/{top_encoded}/{bottom_encoded}.png"
    
    try:
        output_path = OUTPUT_DIR / f"{meme_id}.png"
        urllib.request.urlretrieve(meme_url, output_path)
        
        # Verify it's a valid image
        if output_path.exists() and output_path.stat().st_size > 1000:
            return output_path
    except Exception as e:
        print(f"memegen API failed: {e}")
    
    return None


def generate_meme_fallback(meme_id: str, caption: str) -> Path:
    """Fallback: generate simple meme with Pillow if API fails."""
    ensure_output_dir()
    
    img = Image.new("RGB", (600, 400), (30, 30, 30))
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
    except (OSError, IOError):
        font = ImageFont.load_default()
    
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
    return output_path


def generate_meme(meme_id: str, caption: str, template: str = "this-is-fine") -> Path:
    """Generate a meme - tries memegen.link API first, falls back to Pillow."""
    # Try real meme generation first
    result = generate_meme_memegen(meme_id, caption)
    if result:
        return result
    
    # Fallback to simple generation
    return generate_meme_fallback(meme_id, caption)


def get_meme_path(meme_id: str) -> Path | None:
    """Get path to existing meme if it exists."""
    path = OUTPUT_DIR / f"{meme_id}.png"
    return path if path.exists() else None
