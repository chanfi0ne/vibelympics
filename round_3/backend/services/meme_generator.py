# PURPOSE: Simple meme generator using Pillow
# Creates "this is fine" style memes with captions - kept minimal per navigator guidance

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import textwrap

# Meme dimensions
MEME_WIDTH = 600
MEME_HEIGHT = 400

# Colors
BG_COLOR = (30, 30, 30)  # Dark background
TEXT_COLOR = (255, 255, 255)  # White text
ACCENT_COLOR = (249, 115, 22)  # Orange accent (fire theme)

# Output directory
OUTPUT_DIR = Path(__file__).parent.parent / "static" / "memes"


def ensure_output_dir():
    """Create output directory if it doesn't exist."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def wrap_text(text: str, max_chars: int = 40) -> list[str]:
    """Wrap text to fit within meme width."""
    return textwrap.wrap(text, width=max_chars)


def generate_meme(meme_id: str, caption: str, template: str = "this-is-fine") -> Path:
    """
    Generate a meme image with the given caption.
    Returns path to the generated image.
    """
    ensure_output_dir()

    # Create base image
    img = Image.new("RGB", (MEME_WIDTH, MEME_HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # Try to use a nice font, fall back to default
    try:
        # Try common system fonts
        font_large = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 28)
        font_small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 18)
    except (OSError, IOError):
        try:
            font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
        except (OSError, IOError):
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()

    # Draw "THIS IS FINE" header
    header = "THIS IS FINE"
    header_bbox = draw.textbbox((0, 0), header, font=font_large)
    header_width = header_bbox[2] - header_bbox[0]
    header_x = (MEME_WIDTH - header_width) // 2
    draw.text((header_x, 30), header, font=font_large, fill=ACCENT_COLOR)

    # Draw flame decorations (simple rectangles for fire effect)
    for i in range(5):
        x = 50 + i * 110
        flame_height = 60 + (i % 3) * 20
        draw.polygon([
            (x, MEME_HEIGHT - 80),
            (x + 30, MEME_HEIGHT - 80 - flame_height),
            (x + 60, MEME_HEIGHT - 80)
        ], fill=ACCENT_COLOR)

    # Draw caption text (wrapped)
    lines = wrap_text(caption, max_chars=45)
    y_offset = 100
    line_height = 35

    for line in lines:
        line_bbox = draw.textbbox((0, 0), line, font=font_small)
        line_width = line_bbox[2] - line_bbox[0]
        line_x = (MEME_WIDTH - line_width) // 2
        draw.text((line_x, y_offset), line, font=font_small, fill=TEXT_COLOR)
        y_offset += line_height

    # Draw border
    draw.rectangle(
        [(5, 5), (MEME_WIDTH - 5, MEME_HEIGHT - 5)],
        outline=ACCENT_COLOR,
        width=3
    )

    # Add paranoid watermark
    watermark = "PARANOID // SBOM ROAST"
    wm_bbox = draw.textbbox((0, 0), watermark, font=font_small)
    wm_width = wm_bbox[2] - wm_bbox[0]
    draw.text(
        ((MEME_WIDTH - wm_width) // 2, MEME_HEIGHT - 50),
        watermark,
        font=font_small,
        fill=(100, 100, 100)
    )

    # Save image
    output_path = OUTPUT_DIR / f"{meme_id}.png"
    img.save(output_path, "PNG")

    return output_path


def get_meme_path(meme_id: str) -> Path | None:
    """Get path to existing meme if it exists."""
    path = OUTPUT_DIR / f"{meme_id}.png"
    return path if path.exists() else None
