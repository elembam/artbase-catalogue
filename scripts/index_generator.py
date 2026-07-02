#!/usr/bin/env python3
"""
index_generator.py — Build passports/index.html from canonical JSON.

Reads every artist and artwork JSON in artbase_export/data/ and renders
a Kress-style catalogue index page using templates/index.html.j2.

Usage:
    python3 scripts/index_generator.py
    python3 scripts/index_generator.py --data-dir /path/to/data --out passports/index.html
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

try:
    from jinja2 import Environment, FileSystemLoader, select_autoescape
except ImportError:
    sys.exit("Jinja2 is required: pip install jinja2")


REPO_ROOT    = Path(__file__).resolve().parent.parent
DATA_DIR     = REPO_ROOT / "artbase_export" / "data"
PASSPORTS_DIR = REPO_ROOT  # passports live at repo root → arsaccordia.com/AP-*.html
TEMPLATES_DIR = REPO_ROOT / "templates"


# ── Helpers ────────────────────────────────────────────────────────────────────

def load_json(path: Path) -> Optional[dict]:
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"  Warning: could not load {path}: {e}", file=sys.stderr)
        return None


def artwork_image_src(artwork: dict, passports_dir: Path) -> Optional[str]:
    """Return a relative image path or None."""
    photos = artwork.get("photography_media") or []
    for photo in photos:
        file_url = photo.get("file_url") or photo.get("url")
        if file_url and Path(file_url).exists():
            # Try to make it relative to passports/
            try:
                return str(Path(file_url).relative_to(passports_dir))
            except ValueError:
                return file_url
    # Check for a pre-embedded image in the passport HTML
    # (not needed here — just return None; the template shows placeholder)
    return None


def build_artwork_entry(artwork: dict, passports_dir: Path, artist: dict = None) -> dict:
    oid = artwork.get("object_id", {})
    passport_id = artwork.get("artbase_id", "")
    passport_file = passports_dir / f"{passport_id}.html"
    artist_name = None
    artist_anchor = None
    if artist:
        artist_name = artist.get("identity", {}).get("preferred_name")
        artist_anchor = artist.get("artbase_id")
    return {
        "passport_id":   passport_id,
        "title":         oid.get("title") or "Untitled",
        "date_display":  oid.get("date_display"),
        "medium":        oid.get("materials"),
        "dimensions":    oid.get("dimensions_display"),
        "image_src":     artwork_image_src(artwork, passports_dir),
        "passport_url":  f"/{passport_id}.html" if passport_file.exists() else None,
        "has_passport":  passport_file.exists(),
        "visibility":    artwork.get("visibility", "private"),
        "artist_name":   artist_name,
        "artist_anchor": artist_anchor,
    }


def build_context(data_dir: Path, passports_dir: Path) -> dict:
    artists_dir  = data_dir / "artists"
    artworks_dir = data_dir / "artworks"

    # Load all artworks, indexed by maker_id
    artworks_by_maker: dict[str, list[dict]] = {}
    total_artworks = 0

    for aw_file in sorted(artworks_dir.glob("*.json")):
        artwork = load_json(aw_file)
        if not artwork:
            continue
        oid      = artwork.get("object_id", {})
        maker_id = oid.get("maker_id")
        if not maker_id:
            # Try display name matching (handled later via artist scan)
            maker_id = oid.get("maker_display_name") or "__unknown__"
        artworks_by_maker.setdefault(maker_id, []).append(artwork)
        total_artworks += 1

    # Load artists, skipping UNKNOWN
    artist_entries = []
    for artist_file in sorted(artists_dir.glob("*.json")):
        artist = load_json(artist_file)
        if not artist or artist.get("artbase_id") == "UNKNOWN":
            continue

        artbase_id   = artist.get("artbase_id", "")
        preferred    = artist.get("identity", {}).get("preferred_name", "")

        # Collect artworks for this artist (by artbase_id or display name)
        aw_list = artworks_by_maker.get(artbase_id, [])
        if not aw_list and preferred:
            aw_list = artworks_by_maker.get(preferred, [])

        # Sort artworks by earliest date
        aw_list_sorted = sorted(
            aw_list,
            key=lambda a: a.get("object_id", {}).get("date_earliest") or 9999
        )

        artist_entries.append({
            "artist":   artist,
            "artworks": [build_artwork_entry(a, passports_dir, artist) for a in aw_list_sorted],
        })

    # Sort artists by sort_name
    artist_entries.sort(
        key=lambda e: e["artist"].get("identity", {}).get("sort_name", "ZZZZ").lower()
    )

    total_passports = sum(
        1 for entry in artist_entries
        for aw in entry["artworks"]
        if aw["has_passport"]
    )

    return {
        "artists":        artist_entries,
        "total_artworks": total_artworks,
        "total_passports": total_passports,
        "generated_at":   datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
    }


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Generate ArtBase index page")
    parser.add_argument("--data-dir",    default=str(DATA_DIR),
                        help="Path to artbase_export/data/")
    parser.add_argument("--passports-dir", default=str(PASSPORTS_DIR),
                        help="Output directory for passports/")
    parser.add_argument("--out",         default=str(REPO_ROOT / "catalogue" / "index.html"),
                        help="Output HTML path (default: catalogue/index.html)")
    parser.add_argument("--templates-dir", default=str(TEMPLATES_DIR))
    args = parser.parse_args()

    data_dir      = Path(args.data_dir)
    passports_dir = Path(args.passports_dir)
    out_path      = Path(args.out)
    templates_dir = Path(args.templates_dir)

    if not data_dir.exists():
        sys.exit(f"Data directory not found: {data_dir}")
    passports_dir.mkdir(parents=True, exist_ok=True)

    env = Environment(
        loader=FileSystemLoader(str(templates_dir)),
        autoescape=select_autoescape(["html"]),
    )
    template = env.get_template("index.html.j2")

    context = build_context(data_dir, passports_dir)

    print(f"Artists:   {len(context['artists'])}")
    print(f"Artworks:  {context['total_artworks']}")
    print(f"Passports: {context['total_passports']}")

    html = template.render(**context)
    out_path.write_text(html, encoding="utf-8")
    size_kb = len(html.encode()) // 1024
    print(f"\n✓ Index written: {out_path}  ({size_kb} KB)")


if __name__ == "__main__":
    main()
