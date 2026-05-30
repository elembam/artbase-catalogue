#!/usr/bin/env python3
"""
artist_profile_generator.py

Generate HTML artist profile pages for all artists that have a Wikidata QID.
Writes to passports/artists/{artbase_id}.html

Usage:
    python3 scripts/artist_profile_generator.py             # all artists with QID
    python3 scripts/artist_profile_generator.py --all       # all artists regardless
    python3 scripts/artist_profile_generator.py ART-AIDE-1913  # single artist
"""

import argparse
import glob
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

REPO_ROOT   = Path(__file__).resolve().parent.parent
ARTISTS_DIR = REPO_ROOT / "artbase_export" / "data" / "artists"
ARTWORKS_DIR= REPO_ROOT / "artbase_export" / "data" / "artworks"
OUT_DIR     = REPO_ROOT / "artists"
TMPL_DIR    = REPO_ROOT / "templates"


def load_all_artists() -> list[dict]:
    artists = []
    for f in sorted(ARTISTS_DIR.glob("*.json")):
        try:
            artists.append(json.loads(f.read_text()))
        except Exception:
            pass
    return artists


def load_artworks_by_maker() -> dict[str, list[dict]]:
    """Return dict mapping artbase_id → list of artwork dicts."""
    mapping: dict[str, list[dict]] = {}
    for f in sorted(ARTWORKS_DIR.glob("*.json")):
        try:
            aw = json.loads(f.read_text())
        except Exception:
            continue
        maker_id = (aw.get("object_id") or {}).get("maker_id")
        if not maker_id:
            maker_id = (aw.get("object_id") or {}).get("maker_display_name")
        if maker_id:
            mapping.setdefault(maker_id, []).append(aw)
    return mapping


def artist_has_qid(artist: dict) -> bool:
    al = artist.get("authority_links") or {}
    return bool((al.get("wikidata") or {}).get("id"))


def render_artist(artist: dict, artworks: list[dict], env: Environment) -> str:
    al = artist.get("authority_links") or {}
    wikidata_qid = (al.get("wikidata") or {}).get("id")
    wikidata_status = (al.get("wikidata") or {}).get("status", "")

    aw_list = []
    for aw in artworks:
        oid = aw.get("object_id") or {}
        aw_list.append({
            "passport_id": aw.get("passport_id", ""),
            "title": oid.get("title", "Untitled"),
            "date": oid.get("creation_date", {}).get("display", "") if isinstance(oid.get("creation_date"), dict) else oid.get("creation_date", ""),
        })

    # Source ledger — build display-ready data
    ledger = artist.get("source_ledger", {})
    source_origin    = ledger.get("origin", [])
    source_authority = ledger.get("authority", [])
    verification     = ledger.get("verification", {})
    verification_status = verification.get("status", "unverified")
    fp = ledger.get("field_provenance", {})
    gallery_only_fields = [
        f for f, d in fp.items() if not d.get("has_citable_source")
    ]

    # Instruction 10 — four-grade validation block
    val_block = ledger.get("validation", {})
    conformance_badge  = val_block.get("conformance_badge", "none")
    validation_level1  = val_block.get("level1", {}).get("level", "PENDING")
    validation_level2  = val_block.get("level2", {}).get("level", "PENDING")
    validation_authority_l1 = val_block.get("level1", {}).get("authority", [])
    validated_by_l1    = val_block.get("level1", {}).get("validated_by", "automated")

    tmpl = env.get_template("artist_profile.html.j2")
    return tmpl.render(
        artist=artist,
        wikidata_qid=wikidata_qid,
        wikidata_status=wikidata_status,
        artworks=aw_list,
        exported_date=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        source_origin=source_origin,
        source_authority=source_authority,
        verification_status=verification_status,
        gallery_only_fields=gallery_only_fields,
        conformance_badge=conformance_badge,
        validation_level1=validation_level1,
        validation_level2=validation_level2,
        validation_authority_l1=validation_authority_l1,
        validated_by_l1=validated_by_l1,
    )


def main():
    parser = argparse.ArgumentParser(description="Generate artist profile HTML pages")
    parser.add_argument("artist_id", nargs="?", help="Single artist ID to generate")
    parser.add_argument("--all", action="store_true", help="Generate for ALL artists (not just those with QID)")
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    env = Environment(
        loader=FileSystemLoader(str(TMPL_DIR)),
        autoescape=True,
    )
    # Make dict.get available in Jinja2
    env.globals["dict"] = dict

    artworks_by_maker = load_artworks_by_maker()
    all_artists = load_all_artists()

    if args.artist_id:
        candidates = [a for a in all_artists if a.get("artbase_id") == args.artist_id]
        if not candidates:
            print(f"Artist not found: {args.artist_id}", file=sys.stderr)
            sys.exit(1)
    elif args.all:
        candidates = all_artists
    else:
        candidates = [a for a in all_artists if artist_has_qid(a)]

    generated = 0
    for artist in candidates:
        aid = artist.get("artbase_id", "UNKNOWN")
        artworks = artworks_by_maker.get(aid, [])
        try:
            html = render_artist(artist, artworks, env)
            out_path = OUT_DIR / f"{aid}.html"
            out_path.write_text(html, encoding="utf-8")
            generated += 1
        except Exception as e:
            print(f"  ERROR {aid}: {e}", file=sys.stderr)

    print(f"✓ Generated {generated} artist profile pages → {OUT_DIR}/")


if __name__ == "__main__":
    main()
