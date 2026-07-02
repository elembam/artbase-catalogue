#!/usr/bin/env python3
"""
generate_km_artist_stubs.py

Fetch missing KM artists from Wikidata and write canonical artist JSON stubs.
Also patches artwork JSONs where maker_display_name uses a non-Latvian form.

Usage:
    python3 scripts/generate_km_artist_stubs.py
    python3 scripts/generate_km_artist_stubs.py --dry-run
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT  = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

from wikidata_lib.fetch import fetch_entities  # type: ignore

ARTISTS_DIR  = REPO_ROOT / "artbase_export" / "data" / "artists"
ARTWORKS_DIR = REPO_ROOT / "artbase_export" / "data" / "artworks"

# Artists missing from data/artists/ — {QID: artbase_id}
MISSING_ARTISTS: dict[str, str] = {
    "Q2632125":  "ART-DREVINS-1889",    # Aleksandrs Drēviņš
    "Q1387109":  "ART-JOHANSONS-1880",  # Kārlis Johansons
    "Q16356282": "ART-MATVEJS-1877",    # Voldemārs Matvejs
    "Q16697625": "ART-SILINS-1896",     # Jānis Siliņš
    "Q109894439":"ART-PLASE-1889",      # Jānis Plase
}

# Name aliases: Wikidata may return Russian/other names; map to Latvian preferred form.
# Used to patch maker_display_name in existing artwork JSONs.
NAME_ALIASES: dict[str, str] = {
    "Aleksandr Drevin":     "Aleksandrs Drēviņš",
    "Alexander Drevin":     "Aleksandrs Drēviņš",
    "Drēviņš, Aleksandrs": "Aleksandrs Drēviņš",
}


def _get_claim_value(claims: dict, prop: str) -> str | None:
    """Get first string value from a Wikidata property."""
    for c in claims.get(prop, []):
        sv = c.get("mainsnak", {}).get("datavalue", {}).get("value")
        if isinstance(sv, str):
            return sv
        if isinstance(sv, dict):
            return sv.get("id") or sv.get("text") or sv.get("time")
    return None


def _parse_date(claims: dict, prop: str) -> tuple[str | None, str]:
    """Return (year_str, precision_label) from a time claim."""
    for c in claims.get(prop, []):
        sv = c.get("mainsnak", {}).get("datavalue", {}).get("value", {})
        if not isinstance(sv, dict):
            continue
        time_str = sv.get("time", "")
        prec = sv.get("precision", 9)
        if not time_str:
            continue
        year = time_str[1:5]
        if prec == 11:
            label = "day"
        elif prec == 10:
            label = "month"
        elif prec == 9:
            label = "year"
        elif prec == 8:
            label = "decade"
        else:
            label = "year"
        return year, label
    return None, "year"


def _get_external_id(claims: dict, prop: str) -> str | None:
    """Get first external-id value from a Wikidata property."""
    for c in claims.get(prop, []):
        sv = c.get("mainsnak", {}).get("datavalue", {}).get("value")
        if isinstance(sv, str):
            return sv
    return None


def _authority_entry(id_val: str | None, uri: str | None = None, status: str | None = None) -> dict:
    return {
        "id":            id_val,
        "uri":           uri,
        "status":        status or ("confirmed" if id_val else "search_needed"),
        "verified_date": None,
        "notes":         None,
    }


def build_artist_json(qid: str, entity: dict, artbase_id: str) -> dict:
    labels   = entity.get("labels", {})
    claims   = entity.get("claims", {})

    # Preferred name: Latvian label, fall back to English
    lv_label = labels.get("lv", {}).get("value")
    en_label = labels.get("en", {}).get("value")
    preferred = lv_label or en_label or qid

    # Sort name: "Surname, Given"
    parts = preferred.split()
    sort_name = f"{parts[-1]}, {' '.join(parts[:-1])}" if len(parts) > 1 else preferred

    # Dates
    birth_year, birth_prec = _parse_date(claims, "P569")
    death_year, death_prec = _parse_date(claims, "P570")

    # Authority IDs
    viaf = _get_external_id(claims, "P214")
    ulan = _get_external_id(claims, "P245")
    isni = _get_external_id(claims, "P213")
    gnd  = _get_external_id(claims, "P227")
    bnf  = _get_external_id(claims, "P268")

    now = datetime.now(timezone.utc).isoformat()

    return {
        "artbase_id":           artbase_id,
        "airtable_id":          None,
        "artbase_canonical_id": None,
        "version":              1,
        "created":              now,
        "exported":             now,
        "visibility":           "public",
        "identity": {
            "preferred_name":          preferred,
            "preferred_name_language": "lv" if lv_label else "en",
            "full_name":               preferred,
            "name_variants":           ([en_label] if en_label and en_label != preferred else []),
            "sort_name":               sort_name,
        },
        "life": {
            "birth_date": {
                "value":      birth_year,
                "precision":  birth_prec,
                "status":     "working",
                "source_ids": [],
                "notes":      None,
            },
            "death_date": {
                "value":      death_year,
                "precision":  death_prec,
                "status":     "working",
                "source_ids": [],
                "notes":      None,
            },
            "birth_place": {"display": None, "tgn_uri": None, "wikidata_qid": None, "source_ids": []},
            "death_place": {"display": None, "tgn_uri": None, "wikidata_qid": None, "source_ids": []},
        },
        "descriptors": {
            "nationality":       "Latvian",
            "citizenship":       [],
            "occupations":       ["painter"],
            "occupations_aat":   [],
            "media":             [],
            "subjects":          [],
            "movement_notes":    "Latvian modernism (Klasiskais modernisms)",
            "biography_summary": None,
        },
        "authority_links": {
            "wikidata": _authority_entry(qid, f"https://www.wikidata.org/wiki/{qid}", "confirmed"),
            "viaf":     _authority_entry(viaf),
            "ulan":     _authority_entry(ulan, f"http://vocab.getty.edu/ulan/{ulan}" if ulan else None),
            "isni":     _authority_entry(isni),
            "rkd":      _authority_entry(None),
            "lc_naco":  _authority_entry(None),
            "gnd":      _authority_entry(gnd),
            "bnf":      _authority_entry(bnf),
            "libris":   _authority_entry(None),
            "artbase_id": None,
        },
        "sources": [],
        "source_refs": [],
        "conflicts": [],
        "cataloguing": {
            "review_status": "draft",
            "catalogued_by": "generate_km_artist_stubs.py",
            "notes":         f"Wikidata stub generated from {qid}",
            "tasks":         [],
            "engagement_ids": [],
        },
        "_schema": "artbase:artist:v1",
        "collections": [],
    }


def patch_artwork_names(preferred_by_artbase_id: dict[str, str], dry_run: bool) -> int:
    """
    For each artwork JSON, if maker_display_name is a known alias,
    replace it with the canonical Latvian preferred name and set maker_id.
    Returns count of patched files.
    """
    patched = 0
    # Build reverse lookup: old name → (preferred_name, artbase_id)
    for aw_file in sorted(ARTWORKS_DIR.glob("*.json")):
        aw = json.load(open(aw_file))
        oid = aw.get("object_id", {})
        display = oid.get("maker_display_name", "") or ""
        canonical = NAME_ALIASES.get(display)
        if not canonical:
            continue
        # Find artbase_id for this canonical name
        aid = next((a for a, n in preferred_by_artbase_id.items() if n == canonical), None)
        if not aid:
            continue
        print(f"  Patching {aw_file.name}: '{display}' → '{canonical}' (maker_id={aid})")
        if not dry_run:
            oid["maker_display_name"] = canonical
            oid["maker_id"] = aid
            aw["object_id"] = oid
            aw_file.write_text(json.dumps(aw, ensure_ascii=False, indent=2), encoding="utf-8")
        patched += 1
    return patched


def main(dry_run: bool = False) -> None:
    qids = list(MISSING_ARTISTS.keys())
    print(f"Fetching {len(qids)} artists from Wikidata…")
    entities = fetch_entities(qids)

    preferred_by_artbase_id: dict[str, str] = {}

    for qid, artbase_id in MISSING_ARTISTS.items():
        entity = entities.get(qid)
        if not entity:
            print(f"  ✗ {qid} not found on Wikidata")
            continue

        artist_json = build_artist_json(qid, entity, artbase_id)
        preferred = artist_json["identity"]["preferred_name"]
        preferred_by_artbase_id[artbase_id] = preferred

        out_path = ARTISTS_DIR / f"{artbase_id}.json"
        print(f"  {'(dry) ' if dry_run else ''}✓ {artbase_id}  {preferred}  ({qid})")

        if not dry_run:
            out_path.write_text(
                json.dumps(artist_json, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

    print(f"\nPatching artwork maker_display_name aliases…")
    n = patch_artwork_names(preferred_by_artbase_id, dry_run)
    print(f"  {n} artwork(s) patched")

    if not dry_run:
        print("\nDone. Run index_generator.py to rebuild catalogue/index.html.")


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    main(dry_run=dry)
