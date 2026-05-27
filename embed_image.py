#!/usr/bin/env python3
"""
embed_image.py — Embed an artwork image directly into the passport HTML files
                 as a base64 data URI, so the files are self-contained and
                 don't require network access to render.

Run this on your local machine where you have network access to the image
source (Wikimedia or wherever else).

Usage:
    python3 embed_image.py

What it does:
    1. Downloads the Mona Lisa image from Wikimedia at 600px wide.
    2. Base64-encodes it as a data URI.
    3. Patches both HTML files in the current folder to use the data URI
       instead of the Wikimedia URL.

The same HTML files will then display the image when opened directly via
file:// in any browser.

Requirements: Python 3.7+, the `requests` library (or change to use urllib).
    pip install requests
"""

import base64
import re
import sys
from pathlib import Path

try:
    import requests
except ImportError:
    print("This script needs the 'requests' library. Install with:")
    print("    pip install requests")
    sys.exit(1)


# ---------- Configuration ----------

# The image we want to embed. You can change this URL to any other public-domain
# artwork image you'd like to use for testing.
IMAGE_URL = (
    "https://upload.wikimedia.org/wikipedia/commons/thumb/"
    "e/ec/Mona_Lisa%2C_by_Leonardo_da_Vinci%2C_from_C2RMF_retouched.jpg/"
    "600px-Mona_Lisa%2C_by_Leonardo_da_Vinci%2C_from_C2RMF_retouched.jpg"
)

# HTML files we want to patch. They should be in the same directory as this script.
HTML_FILES = [
    "artwork_passport_mona_lisa.html",
    "artwork_passport_mona_lisa.eodem.html",
]

# Wikimedia requires a proper User-Agent for hotlinking-style requests.
HEADERS = {
    "User-Agent": (
        "ArtBaseCatalogueTool/0.1 "
        "(https://example.com; contact@example.com) "
        "python-requests"
    )
}


# ---------- Implementation ----------

def download_image(url: str) -> tuple[bytes, str]:
    """Download an image and return (raw bytes, mime type)."""
    print(f"→ Downloading {url[:80]}…")
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()

    content_type = response.headers.get("Content-Type", "image/jpeg")
    print(f"  ✓ Got {len(response.content):,} bytes, type {content_type}")
    return response.content, content_type


def to_data_uri(image_bytes: bytes, mime_type: str) -> str:
    """Encode bytes as a base64 data URI."""
    encoded = base64.b64encode(image_bytes).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def patch_html_file(path: Path, data_uri: str) -> int:
    """Replace SVG placeholder data URIs (and any leftover Wikimedia URLs) in img src
    attributes with the real image data URI. Returns count of replacements."""
    if not path.exists():
        print(f"  ⚠ Skipping {path.name} — not found")
        return 0

    content = path.read_text(encoding="utf-8")

    # Match img src attributes that contain either:
    #   1) An SVG data URI (the placeholder we ship)
    #   2) A Wikimedia URL pointing at Mona Lisa (in case someone reverted)
    # The crucial thing is we only touch `src=...`, NEVER `href=...` — clicking
    # the source link should still navigate to Wikimedia, even if the image
    # itself is embedded as base64.

    patterns = [
        # SVG placeholder data URI inside src=
        re.compile(r'src="data:image/svg\+xml;base64,[^"]+"'),
        # Wikimedia URL inside src=
        re.compile(r'src="https://upload\.wikimedia\.org/wikipedia/commons/[^"]*Mona_Lisa[^"]*"'),
    ]

    total = 0
    for pattern in patterns:
        content, count = pattern.subn(f'src="{data_uri}"', content)
        total += count

    if total > 0:
        path.write_text(content, encoding="utf-8")
        print(f"  ✓ {path.name}: replaced {total} src attribute(s) with real image")
    else:
        print(f"  • {path.name}: no placeholder src found (already patched?)")

    return total


def main() -> int:
    print("ArtBase — Image embedding tool")
    print("=" * 50)

    try:
        image_bytes, mime_type = download_image(IMAGE_URL)
    except Exception as e:
        print(f"\n✗ Download failed: {e}")
        print("\nThings to try:")
        print("  - Check your network connection")
        print("  - Verify the URL is still valid")
        print("  - Some networks block Wikimedia; try a different connection")
        return 1

    data_uri = to_data_uri(image_bytes, mime_type)
    approx_kb = len(data_uri) // 1024
    print(f"\n→ Data URI ready ({approx_kb} KB encoded)")

    print("\n→ Patching HTML files…")
    total_replaced = 0
    for filename in HTML_FILES:
        total_replaced += patch_html_file(Path(filename), data_uri)

    print("\n" + "=" * 50)
    if total_replaced > 0:
        print(f"✓ Done. {total_replaced} image reference(s) embedded.")
        print("\nOpen the HTML files in any browser — the image now loads")
        print("without requiring network access.")
    else:
        print("• No replacements made. The files may already be patched,")
        print("  or they're not in the current directory.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
