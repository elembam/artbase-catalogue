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
PASSPORTS_DIR = REPO_ROOT / "passports"

CATALOGUE_BASE_URL = "https://arsaccordia.com"


# ── XML syntax highlighter ─────────────────────────────────────────────────────

import html as _html
import re as _re

def highlight_xml(xml_str: str) -> str:
    """
    Produce HTML with span-based syntax colouring for XML.
    Returns a string safe to embed inside a <pre> block (no wrapping <pre>).
    """
    result = []
    i = 0
    src = xml_str

    def esc(s: str) -> str:
        return _html.escape(s)

    while i < len(src):
        if src[i:i+4] == "<!--":
            end = src.find("-->", i)
            if end == -1:
                result.append(f'<span class="xml-comment">{esc(src[i:])}</span>')
                break
            result.append(f'<span class="xml-comment">{esc(src[i:end+3])}</span>')
            i = end + 3
        elif src[i:i+2] == "<?":
            end = src.find("?>", i)
            end = (end + 2) if end != -1 else len(src)
            result.append(f'<span class="xml-comment">{esc(src[i:end])}</span>')
            i = end
        elif src[i] == "<":
            # Find close of tag
            end = src.find(">", i)
            if end == -1:
                result.append(esc(src[i:]))
                break
            tag_str = src[i:end+1]
            # Colour tag name
            tag_str_hl = _re.sub(
                r'(</?)([\w:]+)',
                lambda m: f'<span class="xml-tag">{esc(m.group(1))}{esc(m.group(2))}</span>',
                tag_str, count=1
            )
            # Colour attribute names
            tag_str_hl = _re.sub(
                r'([\w:]+)(=)',
                lambda m: f'<span class="xml-attr">{esc(m.group(1))}</span>{esc(m.group(2))}',
                tag_str_hl
            )
            # Colour attribute values
            tag_str_hl = _re.sub(
                r'("(?:[^"\\]|\\.)*")',
                lambda m: f'<span class="xml-value">{m.group(1)}</span>',
                tag_str_hl
            )
            result.append(tag_str_hl)
            i = end + 1
        else:
            # Text content
            next_tag = src.find("<", i)
            if next_tag == -1:
                result.append(f'<span class="xml-text">{esc(src[i:])}</span>')
                break
            text = src[i:next_tag]
            if text.strip():
                result.append(f'<span class="xml-text">{esc(text)}</span>')
            else:
                result.append(esc(text))
            i = next_tag

    return "".join(result)


def highlight_json(obj) -> str:
    """Pretty-print a dict/list as syntax-coloured HTML for embedding in <pre>."""
    import html as _html
    raw = json.dumps(obj, indent=2, ensure_ascii=False)
    lines = []
    for line in raw.splitlines():
        # Key
        line = _re.sub(
            r'^(\s*)"(.*?)"(\s*:)',
            lambda m: f'{m.group(1)}<span class="json-key">"{_html.escape(m.group(2))}"</span>{m.group(3)}',
            line
        )
        # URL string value
        line = _re.sub(
            r'(:\s*)"(https?://[^"]+)"',
            lambda m: f'{m.group(1)}<span class="json-url">"{_html.escape(m.group(2))}"</span>',
            line
        )
        # Other string value
        line = _re.sub(
            r'(:\s*)"([^"]*)"',
            lambda m: f'{m.group(1)}<span class="json-str">"{_html.escape(m.group(2))}"</span>',
            line
        )
        lines.append(line)
    return "\n".join(lines)


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

    maker_id = artwork.get("object_id", {}).get("maker_id")
    artist_profile_url = f"artists/{maker_id}.html" if maker_id else None

    # Load machine-readable XML if already generated
    artbase_id = artwork.get("artbase_id", "")
    api_dir = REPO_ROOT / "api" / artbase_id
    lido_xml  = (api_dir / "lido.xml").read_text(encoding="utf-8")  if (api_dir / "lido.xml").exists()  else None
    eodem_xml = (api_dir / "eodem.xml").read_text(encoding="utf-8") if (api_dir / "eodem.xml").exists() else None

    jsonld_data = build_jsonld(artwork, artist)
    jsonld_pretty_html = highlight_json(jsonld_data)
    lido_html  = highlight_xml(lido_xml)  if lido_xml  else None
    eodem_html = highlight_xml(eodem_xml) if eodem_xml else None

    return {
        "artwork":            artwork,
        "artist":             artist,
        "artist_profile_url": artist_profile_url,
        "image_src":          image_src,
        "issued_date":        issued_date,
        "issued_year_roman":  issued_year_roman,
        "jsonld":             jsonld_data,
        "lido_xml":           lido_xml,
        "eodem_xml":          eodem_xml,
        "lido_html":          lido_html,
        "eodem_html":         eodem_html,
        "jsonld_html":        jsonld_pretty_html,
    }


# ── Schema.org JSON-LD builder ────────────────────────────────────────────────

def build_jsonld(artwork: dict, artist: Optional[dict]) -> dict:
    """
    Build a Schema.org VisualArtwork JSON-LD dict for embedding in <head>.

    Uses only data already present in the canonical JSON — no external calls.
    All sameAs links point to external authority records, never back to ourselves.
    """
    oid = artwork.get("object_id", {})
    auth = artwork.get("authority_links", {})
    artbase_id = artwork.get("artbase_id", "")

    jsonld: dict[str, Any] = {
        "@context": "https://schema.org",
        "@type": "VisualArtwork",
        "@id": f"{CATALOGUE_BASE_URL}/{artbase_id}",
        "name": oid.get("title") or artbase_id,
        "url": f"{CATALOGUE_BASE_URL}/{artbase_id}.html",
        "identifier": artbase_id,
        "description": oid.get("subject") or "",
    }

    # Date created
    date_earliest = oid.get("date_earliest")
    date_latest = oid.get("date_latest")
    if date_earliest:
        jsonld["dateCreated"] = (
            f"{date_earliest}/{date_latest}" if date_latest and date_latest != date_earliest
            else str(date_earliest)
        )

    # Medium / material
    if oid.get("materials"):
        jsonld["artMedium"] = oid["materials"]

    # Dimensions
    if oid.get("dimensions_display"):
        jsonld["size"] = oid["dimensions_display"]

    # Object type → artform
    if oid.get("object_type"):
        jsonld["artform"] = oid["object_type"].capitalize()

    # Artwork sameAs — Wikidata QID only (external authority)
    artwork_wikidata = auth.get("wikidata", {})
    if isinstance(artwork_wikidata, dict) and artwork_wikidata.get("uri"):
        jsonld["sameAs"] = artwork_wikidata["uri"]

    # Creator
    if artist:
        a_identity = artist.get("identity", {})
        a_life = artist.get("life", {})
        a_auth = artist.get("authority_links", {})

        creator: dict[str, Any] = {
            "@type": "Person",
            "name": a_identity.get("preferred_name", ""),
        }

        # sameAs: collect all confirmed/candidate external authority URIs
        same_as = []

        wikidata = a_auth.get("wikidata", {})
        if isinstance(wikidata, dict) and wikidata.get("id") and wikidata.get("status") in ("confirmed", "candidate_verify"):
            same_as.append(f"https://www.wikidata.org/wiki/{wikidata['id']}")

        viaf = a_auth.get("viaf", {})
        if isinstance(viaf, dict) and viaf.get("id") and viaf.get("status") in ("confirmed", "candidate_verify"):
            same_as.append(f"https://viaf.org/viaf/{viaf['id']}")

        ulan = a_auth.get("ulan", {})
        if isinstance(ulan, dict) and ulan.get("id") and ulan.get("status") in ("confirmed", "candidate_verify"):
            same_as.append(f"https://www.getty.edu/vow/ULANFullDisplay?find=&role=&nation=&subjectid={ulan['id']}")

        isni = a_auth.get("isni", {})
        if isinstance(isni, dict) and isni.get("id") and isni.get("status") in ("confirmed", "candidate_verify"):
            same_as.append(f"https://isni.org/isni/{isni['id']}")

        gnd = a_auth.get("gnd", {})
        if isinstance(gnd, dict) and gnd.get("id") and gnd.get("status") in ("confirmed", "candidate_verify"):
            same_as.append(f"https://d-nb.info/gnd/{gnd['id']}")

        bnf = a_auth.get("bnf", {})
        if isinstance(bnf, dict) and bnf.get("id") and bnf.get("status") in ("confirmed", "candidate_verify"):
            same_as.append(f"https://data.bnf.fr/ark:/12148/cb{bnf['id']}")

        lc = a_auth.get("lc_naco", {})
        if isinstance(lc, dict) and lc.get("id") and lc.get("status") in ("confirmed", "candidate_verify"):
            same_as.append(f"https://id.loc.gov/authorities/names/{lc['id']}.html")

        if same_as:
            creator["sameAs"] = same_as

        # Birth/death dates
        birth = a_life.get("birth_date", {})
        if isinstance(birth, dict) and birth.get("value"):
            creator["birthDate"] = birth["value"]
        death = a_life.get("death_date", {})
        if isinstance(death, dict) and death.get("value"):
            creator["deathDate"] = death["value"]

        # Nationality
        descriptors = artist.get("descriptors", {})
        if descriptors.get("nationality"):
            creator["nationality"] = descriptors["nationality"]

        jsonld["creator"] = creator

    # Location / collection
    location = artwork.get("location", {})
    if location.get("collection"):
        holder: dict[str, Any] = {"@type": "Organization", "name": location["collection"]}
        if location.get("collection_qid"):
            holder["sameAs"] = f"https://www.wikidata.org/wiki/{location['collection_qid']}"
        jsonld["locationCreated"] = holder  # repurposed as current holder context

    # Iconographic subjects → about
    iconography = artwork.get("iconography", {})
    iconclass_labels = iconography.get("iconclass_labels", [])
    if iconclass_labels:
        jsonld["about"] = [
            {"@type": "Thing", "name": item["label"], "url": item["uri"]}
            for item in iconclass_labels
            if isinstance(item, dict) and item.get("label") and item.get("uri")
        ]

    return jsonld


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate an HTML artwork passport from canonical JSON."
    )
    parser.add_argument("passport_id", help="Artwork passport ID, e.g. AP-2026-000001")
    parser.add_argument(
        "--data-dir", default=None,
        help=f"Path to data/ directory (default: {DEFAULT_DATA})"
    )
    parser.add_argument(
        "--out-dir", default=None,
        help=f"Output directory (default: {PASSPORTS_DIR})"
    )
    parser.add_argument(
        "--open", action="store_true",
        help="Open the generated passport in the default browser"
    )
    args = parser.parse_args()

    data_dir    = Path(args.data_dir) if args.data_dir else DEFAULT_DATA
    out_dir     = Path(args.out_dir)  if args.out_dir  else PASSPORTS_DIR
    artwork_path = data_dir / "artworks" / f"{args.passport_id}.json"

    if not artwork_path.exists():
        print(f"✗ Artwork JSON not found: {artwork_path}", file=sys.stderr)
        return 1

    if not TEMPLATE.exists():
        print(f"✗ Template not found: {TEMPLATE}", file=sys.stderr)
        return 1

    # Load data
    artwork = load_json(artwork_path)
    artist  = find_artist_json(artwork, data_dir)
    image_src = resolve_image(artwork, data_dir)

    if artist:
        print(f"  Artist: {artist.get('artbase_id')} — {artist.get('identity', {}).get('preferred_name', '?')}")
    else:
        print(f"  Artist: (not found)")
    if image_src:
        print(f"  Image:  embedded ({len(image_src)//1024} KB)")
    else:
        print(f"  Image:  not available")

    # Set up Jinja2
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATE.parent)),
        autoescape=True,
        undefined=Undefined,   # silently skip missing vars
    )
    env.filters["title_visibility"] = filter_title_visibility
    env.filters["aat_id"]           = filter_aat_id
    env.filters["title"]            = filter_title

    template = env.get_template(TEMPLATE.name)
    context  = build_context(artwork, artist, image_src)
    html     = template.render(**context)

    # Write output
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{args.passport_id}.html"
    out_path.write_text(html, encoding="utf-8")

    print(f"\n✓ Passport written: {out_path}")
    print(f"  Size: {len(html)//1024} KB")

    if args.open:
        webbrowser.open(out_path.as_uri())

    return 0


if __name__ == "__main__":
    sys.exit(main())
