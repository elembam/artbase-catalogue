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


def safe_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def prose_person_name(value: str) -> str:
    text = safe_text(value)
    if "," not in text:
        return text
    parts = [p.strip() for p in text.split(",", 1)]
    if len(parts) == 2 and parts[0] and parts[1]:
        return f"{parts[1]} {parts[0]}"
    return text


def authority_id(authority_links: dict, key: str) -> Optional[str]:
    entry = authority_links.get(key) or {}
    value = safe_text(entry.get("id"))
    return value or None


def collection_page_url(artwork: dict) -> Optional[str]:
    collection = safe_text((artwork.get("location") or {}).get("collection"))
    if not collection:
        return "/collections/"
    if "Latvian National Museum of Art" in collection or "Latvijas Nacionālais mākslas muzejs" in collection:
        return "/collections/lnmm/"
    if "Hansabanka Contemporary Art Collection" in collection or "Swedbank Latvia" in collection:
        return "/collections/hansabanka/"
    return "/collections/"


def artist_role_label(artist: Optional[dict]) -> str:
    if not artist:
        return ""
    desc = artist.get("descriptors") or {}
    occupations = desc.get("occupations") or []
    if occupations:
        return str(occupations[0])
    occupation = desc.get("occupation")
    if occupation:
        return str(occupation)
    return ""


def artist_page_title(artist: Optional[dict]) -> str:
    if not artist:
        return "Artwork Passport | Ars Accordia"
    identity = artist.get("identity") or {}
    preferred = safe_text(identity.get("preferred_name"))
    if not preferred:
        return "Artist profile | Ars Accordia"
    life = artist.get("life") or {}
    birth = safe_text((life.get("birth_date") or {}).get("value"))
    death = safe_text((life.get("death_date") or {}).get("value"))
    role = artist_role_label(artist)
    if birth and death:
        name_segment = f"{preferred} ({birth}–{death})"
    elif birth:
        name_segment = f"{preferred} ({birth})"
    elif death:
        name_segment = f"{preferred} (–{death})"
    else:
        name_segment = preferred
    if role:
        return f"{name_segment} — Latvian {role} | Ars Accordia"
    return f"{name_segment} | Ars Accordia"


def artist_page_description(artist: Optional[dict], artwork_count: int) -> str:
    if not artist:
        return "ArtBase catalogue record and authority links for this artist."
    identity = artist.get("identity") or {}
    preferred = safe_text(identity.get("preferred_name"))
    life = artist.get("life") or {}
    birth = safe_text((life.get("birth_date") or {}).get("value"))
    death = safe_text((life.get("death_date") or {}).get("value"))
    role = artist_role_label(artist)

    name_segment = preferred
    if birth and death:
        name_segment = f"{preferred} ({birth}–{death})"
    elif birth:
        name_segment = f"{preferred} ({birth})"
    elif death:
        name_segment = f"{preferred} (–{death})"

    sentence = f"{name_segment}"
    if role:
        sentence += f", Latvian {role}."
    else:
        sentence += "."
    if artwork_count > 0:
        sentence += f" {artwork_count} works documented by Ars Accordia,"
    sentence += " cross-referenced to Wikidata, Getty ULAN and public authority records."
    return sentence


def normalize_dimension(value: str) -> str:
    text = safe_text(value)
    if not text:
        return ""
    text = text.replace("×", "x")
    text = re.sub(r"(\d+)\.0(?=\s*(?:x|cm|mm|m|in|cm\b))", r"\1", text)
    text = text.replace(" x ", " × ")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def short_title_text(title: str, year: str, artist_name: str) -> str:
    suffix = " | Ars Accordia"

    def escaped_len(value: str) -> int:
        return len(
            value.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#39;")
        )

    title_text = title.strip()
    if not title_text:
        title_text = "Untitled"
    base = title_text
    if year:
        base = f"{title_text} ({year})"
    if artist_name:
        base = f"{base}, {artist_name}"
    if escaped_len(base + suffix) <= 60:
        return base

    if year:
        no_artist = f"{title_text} ({year})"
        if escaped_len(no_artist + suffix) <= 60:
            return no_artist

    if escaped_len(title_text + suffix) <= 60:
        return title_text

    clipped = title_text
    while escaped_len(clipped + "..." + suffix) > 60 and len(clipped) > 1:
        clipped = clipped[:-1]
    return clipped.rstrip() + "..."


def passport_page_title(artwork: dict, artist: Optional[dict]) -> str:
    oid = artwork.get("object_id") or {}
    title = safe_text(oid.get("title"))
    if not title:
        title = "Untitled"
    year = safe_text(oid.get("date_display") or oid.get("date_earliest"))
    artist_name = safe_text((artist.get("identity") or {}).get("preferred_name")) if artist else prose_person_name(oid.get("maker_display_name") or oid.get("maker_id"))
    main = short_title_text(title, year, artist_name)
    return f"{main} | Ars Accordia"


def passport_page_description(artwork: dict, artist: Optional[dict]) -> str:
    oid = artwork.get("object_id") or {}
    title = safe_text(oid.get("title"))
    if not title:
        title = "Untitled"
    year = safe_text(oid.get("date_display") or oid.get("date_earliest"))
    artist_name = safe_text((artist.get("identity") or {}).get("preferred_name")) if artist else prose_person_name(oid.get("maker_display_name") or oid.get("maker_id"))
    medium = safe_text(oid.get("materials"))
    dimensions = normalize_dimension(oid.get("dimensions_display"))
    collection = safe_text((artwork.get("location") or {}).get("collection"))
    ap_id = safe_text(artwork.get("artbase_id"))

    base_bits = [title]
    if year:
        base_bits.append(year)
    if artist_name:
        base_bits.append(f"by {artist_name}")
    lead = ", ".join(bit for bit in base_bits if bit)

    details = []
    if medium:
        details.append(medium)
    if dimensions:
        details.append(dimensions)
    if collection:
        details.append(collection)
    detail_text = ". ".join(part for part in details if part)
    if detail_text:
        detail_text = f" {detail_text}."
    if ap_id:
        return f"{lead}.{detail_text} Permanent Artwork Passport {ap_id} with sourced provenance and authority cross-references."
    return f"{lead}.{detail_text} Permanent artwork record with sourced provenance and authority cross-references."


# ── JSON-LD builder ────────────────────────────────────────────────────────────

def build_jsonld(artwork: dict, artist: Optional[dict],
                 image_src: Optional[str]) -> dict:
    artbase_id = safe_text(artwork.get("artbase_id"))
    base_url = "https://arsaccordia.com"
    page_url = f"{base_url}/{artbase_id}.html" if artbase_id else ""
    oid = artwork.get("object_id") or {}
    aw_links = artwork.get("authority_links") or {}

    ld: dict = {
        "@context": "https://schema.org",
        "@type": "VisualArtwork",
    }
    title = safe_text(oid.get("title"))
    if title:
        ld["name"] = title

    creator_name = ""
    if artist:
        creator_name = safe_text((artist.get("identity") or {}).get("preferred_name"))
    if not creator_name:
        creator_name = prose_person_name(oid.get("maker_display_name") or oid.get("maker_id"))
    if creator_name:
        creator: dict = {"@type": "Person", "name": creator_name}
        if artist:
            artist_wikidata = authority_id(artist.get("authority_links") or {}, "wikidata")
            if artist_wikidata:
                creator["sameAs"] = [f"https://www.wikidata.org/wiki/{artist_wikidata}"]
        ld["creator"] = creator

    date_created = safe_text(oid.get("date_display") or oid.get("date_earliest"))
    if date_created:
        ld["dateCreated"] = date_created

    art_medium = safe_text(oid.get("materials"))
    if art_medium:
        ld["artMedium"] = art_medium

    width_cm = oid.get("width_cm")
    if width_cm is not None:
        ld["width"] = {"@type": "QuantitativeValue", "value": width_cm, "unitCode": "CMT"}
    height_cm = oid.get("height_cm")
    if height_cm is not None:
        ld["height"] = {"@type": "QuantitativeValue", "value": height_cm, "unitCode": "CMT"}

    if artbase_id:
        ld["identifier"] = artbase_id
    if page_url:
        ld["url"] = page_url

    work_wikidata = authority_id(aw_links, "wikidata")
    if work_wikidata:
        ld["sameAs"] = [f"https://www.wikidata.org/wiki/{work_wikidata}"]

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
    collection_url = collection_page_url(artwork)
    return {
        "artwork":            artwork,
        "artist":             artist,
        "artist_profile_url": f"/artists/{artist_id}.html" if artist_id else None,
        "collection_page_url": collection_url,
        "image_src":          image_src,
        "issued_date":        issued_date,
        "issued_year_roman":  issued_year_roman,
        "page_title":         passport_page_title(artwork, artist),
        "page_description":   passport_page_description(artwork, artist),
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
