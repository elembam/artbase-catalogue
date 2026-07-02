#!/usr/bin/env python3
"""
passport_generator.py — Generate a standalone HTML passport for an artwork.

Reads canonical JSON from data/artworks/<ID>.json and data/artists/<artist_id>.json,
renders the Jinja2 template at templates/passport.html.j2, and writes to
passports/<ID>.html.

Usage:
    python3 scripts/passport_generator.py AP-2026-000001
    python3 scripts/passport_generator.py AP-2026-000001 --data-dir /path/to/data
    python3 scripts/passport_generator.py AP-2026-000001 --open

Dependencies:
    pip install jinja2
"""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import re
import sys
import webbrowser
from datetime import date, datetime
from pathlib import Path
from typing import Any, Optional

try:
    from jinja2 import Environment, FileSystemLoader, StrictUndefined, Undefined
except ImportError:
    print("Install Jinja2 first:  pip install jinja2")
    sys.exit(1)


# ── Paths ──────────────────────────────────────────────────────────────────────

SCRIPT_DIR  = Path(__file__).parent
REPO_ROOT   = SCRIPT_DIR.parent
TEMPLATE    = REPO_ROOT / "templates" / "passport.html.j2"
DEFAULT_DATA = REPO_ROOT / "artbase_export" / "data"
PASSPORTS_DIR = REPO_ROOT  # passports live at repo root → arsaccordia.com/AP-*.html


# ── Roman numerals helper (for the seal year) ──────────────────────────────────

def to_roman(n: int) -> str:
    vals = [(1000,"M"),(900,"CM"),(500,"D"),(400,"CD"),(100,"C"),(90,"XC"),
            (50,"L"),(40,"XL"),(10,"X"),(9,"IX"),(5,"V"),(4,"IV"),(1,"I")]
    result = ""
    for v, s in vals:
        while n >= v:
            result += s
            n -= v
    return result


# ── Data loading ───────────────────────────────────────────────────────────────

def load_json(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def find_artist_json(artwork: dict, data_dir: Path) -> Optional[dict]:
    # Try canonical maker_id first
    maker_id = artwork.get("object_id", {}).get("maker_id")
    if maker_id:
        artist_path = data_dir / "artists" / f"{maker_id}.json"
        if artist_path.exists():
            return load_json(artist_path)

    # Fall back: scan all artist files and match by preferred_name or artbase_id
    display_name = artwork.get("object_id", {}).get("maker_display_name") or \
                   artwork.get("object_id", {}).get("maker_id") or \
                   artwork.get("artist_display_name")
    artists_dir = data_dir / "artists"
    if artists_dir.exists():
        for artist_file in sorted(artists_dir.glob("*.json")):
            if artist_file.stem == "UNKNOWN":
                continue
            try:
                a = load_json(artist_file)
                preferred = a.get("identity", {}).get("preferred_name", "")
                artbase   = a.get("artbase_id", "")
                if display_name and (
                    preferred.lower() == display_name.lower() or
                    artbase == display_name
                ):
                    return a
            except Exception:
                continue
    return None


# ── Image embedding ────────────────────────────────────────────────────────────

def embed_image(file_path: str) -> Optional[str]:
    """Load an image file and return a data URI, or None if not available."""
    p = Path(file_path)
    if not p.exists():
        return None
    mime, _ = mimetypes.guess_type(str(p))
    if not mime or not mime.startswith("image/"):
        return None
    data = base64.b64encode(p.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{data}"


def resolve_image(artwork: dict, data_dir: Path) -> Optional[str]:
    """
    Try to find an image for the artwork:
    1. Check the canonical JSON for a photography media file path
    2. Look for a conventional file in data/images/<artbase_id>.*
    """
    artbase_id = artwork.get("artbase_id", "")

    # Check conventional image locations
    for ext in (".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff"):
        candidate = data_dir / "images" / f"{artbase_id}{ext}"
        if candidate.exists():
            src = embed_image(str(candidate))
            if src:
                return src

    return None


# ── Jinja2 filters ─────────────────────────────────────────────────────────────

def filter_title_visibility(value: str) -> str:
    mapping = {
        "private":          "Private",
        "unlisted":         "Unlisted",
        "public-unindexed": "Public — Not Indexed",
        "public":           "Public — Indexed",
    }
    return mapping.get(value, value.replace("-", " ").title())


def filter_aat_id(uri: str) -> str:
    """Extract numeric ID from a Getty URI like http://vocab.getty.edu/aat/300033618"""
    m = re.search(r"/(\d+)$", uri)
    return m.group(1) if m else uri


def filter_title(value: str) -> str:
    return value.replace("_", " ").title()


# ── JSON-LD builder ────────────────────────────────────────────────────────────

def _confirmed_id(authority_links: dict, key: str) -> Optional[str]:
    """Return an authority ID only if its status is 'confirmed'."""
    entry = authority_links.get(key) or {}
    if entry.get("status") == "confirmed" and entry.get("id"):
        return entry["id"]
    return None


def build_jsonld(artwork: dict, artist: Optional[dict],
                 image_src: Optional[str]) -> dict:
    artbase_id = artwork.get("artbase_id", "")
    base_url   = "https://arsaccordia.com"
    page_url   = f"{base_url}/{artbase_id}.html"
    entity_url = f"{base_url}/{artbase_id}"

    oid  = artwork.get("object_id") or {}
    loc  = artwork.get("location") or {}
    aw_links = artwork.get("authority_links") or {}

    # Artwork-level sameAs — only confirmed IDs
    artwork_same_as = []
    aw_wikidata = _confirmed_id(aw_links, "wikidata")
    if aw_wikidata:
        artwork_same_as.append(f"https://www.wikidata.org/wiki/{aw_wikidata}")

    # Creator block
    creator: dict = {"@type": "Person"}
    if artist:
        al = artist.get("authority_links") or {}
        creator["name"] = artist.get("identity", {}).get("preferred_name", "")
        artist_id = artist.get("artbase_id", "")
        if artist_id:
            creator["@id"] = f"{base_url}/artists/{artist_id}"
        creator_same_as = []
        wikidata_qid = _confirmed_id(al, "wikidata")
        if wikidata_qid:
            creator_same_as.append(f"https://www.wikidata.org/wiki/{wikidata_qid}")
        viaf_id = _confirmed_id(al, "viaf")
        if viaf_id:
            creator_same_as.append(f"https://viaf.org/viaf/{viaf_id}")
        ulan_id = _confirmed_id(al, "ulan")
        if ulan_id:
            creator_same_as.append(f"https://vocab.getty.edu/page/ulan/{ulan_id}")
        if artist_id:
            creator_same_as.append(f"{base_url}/artists/{artist_id}.html")
        if creator_same_as:
            creator["sameAs"] = creator_same_as
        life = artist.get("life") or {}
        birth = (life.get("birth_date") or {}).get("value")
        death = (life.get("death_date") or {}).get("value")
        if birth:
            creator["birthDate"] = birth
        if death:
            creator["deathDate"] = death
        nationality = (artist.get("descriptors") or {}).get("nationality")
        if nationality:
            creator["nationality"] = nationality
    else:
        display_name = oid.get("maker_display_name") or oid.get("maker_id")
        if display_name:
            creator["name"] = display_name

    # Structured dimensions
    width_cm  = oid.get("width_cm")
    height_cm = oid.get("height_cm")

    # Owner / location
    collection = loc.get("collection") or "Private collection"
    owner = {"@type": "Organization", "name": collection}
    collection_qid = loc.get("collection_qid")
    if collection_qid:
        owner["sameAs"] = f"https://www.wikidata.org/wiki/{collection_qid}"

    # Base LD object
    ld: dict = {
        "@context":  "https://schema.org",
        "@type":     "VisualArtwork",
        "@id":       entity_url,
        "name":      oid.get("title", ""),
        "url":       page_url,
        "identifier": artbase_id,
        "creator":   creator,
        "artform":   oid.get("object_type", "painting").title(),
        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id":   page_url,
            "isPartOf": {"@id": base_url},
        },
    }

    if oid.get("materials"):
        ld["artMedium"] = oid["materials"]
    if oid.get("date_display"):
        ld["dateCreated"] = oid["date_display"]
    if oid.get("subject"):
        ld["description"] = oid["subject"]
    if width_cm is not None:
        ld["width"]  = {"@type": "QuantitativeValue", "value": width_cm,  "unitCode": "CMT"}
    if height_cm is not None:
        ld["height"] = {"@type": "QuantitativeValue", "value": height_cm, "unitCode": "CMT"}
    if oid.get("dimensions_display"):
        ld["size"] = oid["dimensions_display"]

    # Image: only include if it's a real URL (not base64), as base64 is not useful for the graph
    if image_src and not image_src.startswith("data:"):
        ld["image"] = image_src

    ld["owner"] = owner

    if artwork_same_as:
        ld["sameAs"] = artwork_same_as

    return ld


# ── Template context builder ───────────────────────────────────────────────────

def build_context(artwork: dict, artist: Optional[dict],
                  image_src: Optional[str]) -> dict:
    # Issued date from exported field or today
    exported = artwork.get("exported") or datetime.utcnow().isoformat()
    try:
        issued_dt = datetime.fromisoformat(exported.rstrip("Z"))
        issued_date = issued_dt.strftime("%Y-%m-%d")
        issued_year_roman = to_roman(issued_dt.year)
    except (ValueError, AttributeError):
        issued_date = date.today().isoformat()
        issued_year_roman = to_roman(date.today().year)

    artist_id = (artist or {}).get("artbase_id") if artist else None
    return {
        "artwork":            artwork,
        "artist":             artist,
        "artist_profile_url": f"/artists/{artist_id}.html" if artist_id else None,
        "image_src":          image_src,
        "issued_date":        issued_date,
        "issued_year_roman":  issued_year_roman,
        "jsonld":             build_jsonld(artwork, artist, image_src),
    }


# ── Main ───────────────────────────────────────────────────────────────────────

def _generate_one(passport_id: str, data_dir: Path, out_dir: Path,
                   env: "Environment", open_browser: bool = False) -> bool:
    artwork_path = data_dir / "artworks" / f"{passport_id}.json"
    if not artwork_path.exists():
        print(f"✗ Artwork JSON not found: {artwork_path}", file=sys.stderr)
        return False

    artwork   = load_json(artwork_path)
    artist    = find_artist_json(artwork, data_dir)
    image_src = resolve_image(artwork, data_dir)

    template  = env.get_template(TEMPLATE.name)
    context   = build_context(artwork, artist, image_src)
    html      = template.render(**context)

    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{passport_id}.html"
    out_path.write_text(html, encoding="utf-8")

    artist_name = artist.get("identity", {}).get("preferred_name", "?") if artist else "(not found)"
    img_note    = f"{len(image_src)//1024} KB" if image_src else "none"
    print(f"  ✓ {out_path.name}  [{artist_name}]  image:{img_note}  {len(html)//1024} KB")

    if open_browser:
        webbrowser.open(out_path.as_uri())
    return True


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate HTML artwork passports from canonical JSON."
    )
    parser.add_argument(
        "passport_id", nargs="?",
        help="Artwork passport ID, e.g. AP-2026-000001 (omit with --all)",
    )
    parser.add_argument(
        "--all", action="store_true",
        help="Generate passports for every artwork JSON in data/artworks/",
    )
    parser.add_argument(
        "--data-dir", default=None,
        help=f"Path to data/ directory (default: {DEFAULT_DATA})",
    )
    parser.add_argument(
        "--out-dir", default=None,
        help=f"Output directory (default: {PASSPORTS_DIR})",
    )
    parser.add_argument(
        "--open", action="store_true",
        help="Open the generated passport(s) in the default browser",
    )
    args = parser.parse_args()

    if not args.all and not args.passport_id:
        parser.error("Provide a passport ID or use --all")

    data_dir = Path(args.data_dir) if args.data_dir else DEFAULT_DATA
    out_dir  = Path(args.out_dir)  if args.out_dir  else PASSPORTS_DIR

    if not TEMPLATE.exists():
        print(f"✗ Template not found: {TEMPLATE}", file=sys.stderr)
        return 1

    env = Environment(
        loader=FileSystemLoader(str(TEMPLATE.parent)),
        autoescape=True,
        undefined=Undefined,
    )
    env.filters["title_visibility"] = filter_title_visibility
    env.filters["aat_id"]           = filter_aat_id
    env.filters["title"]            = filter_title

    if args.all:
        artworks_dir = data_dir / "artworks"
        files = sorted(artworks_dir.glob("*.json"))
        if not files:
            print(f"No artwork JSON files found in {artworks_dir}", file=sys.stderr)
            return 1
        print(f"Generating {len(files)} passport(s) → {out_dir}/")
        ok = sum(_generate_one(f.stem, data_dir, out_dir, env) for f in files)
        print(f"\n✓ {ok}/{len(files)} passports written")
        return 0 if ok == len(files) else 1

    ok = _generate_one(args.passport_id, data_dir, out_dir, env, open_browser=args.open)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
