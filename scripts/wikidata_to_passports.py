#!/usr/bin/env python3
"""
wikidata_to_passports.py

Pull artworks from Wikidata → canonical JSON → HTML passports.
Replaces Airtable as the data source for public-collection artworks.

The pipeline:
  1. SPARQL: find all artworks P170-linked to a target artist list
  2. wbgetentities: fetch full item data
  3. Transform: Wikidata entity → canonical artwork JSON
  4. Write:     data/artworks/AP-2026-XXXXXX.json
  5. Generate:  passports/AP-2026-XXXXXX.html via passport_generator.py
  6. Index:     passports/index.html via index_generator.py

Usage:
    # All KM artists (default):
    python3 scripts/wikidata_to_passports.py

    # Specific artists:
    python3 scripts/wikidata_to_passports.py --artists Q4150307,Q5763621

    # Specific artwork QIDs (skip SPARQL):
    python3 scripts/wikidata_to_passports.py --qids Q135001234,Q135001235

    # Dry-run (transform only, no files written):
    python3 scripts/wikidata_to_passports.py --dry-run

    # Skip passport HTML generation (only write canonical JSON):
    python3 scripts/wikidata_to_passports.py --no-passports
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

SCRIPT_DIR   = Path(__file__).resolve().parent
REPO_ROOT    = SCRIPT_DIR.parent
DATA_DIR     = REPO_ROOT / "artbase_export" / "data"
ARTWORKS_DIR = DATA_DIR / "artworks"
ARTISTS_DIR  = DATA_DIR / "artists"
PASSPORTS_DIR = REPO_ROOT  # passports live at repo root → arsaccordia.com/AP-*.html

sys.path.insert(0, str(SCRIPT_DIR))
from wikidata_lib import fetch as wdfetch
from wikidata_lib import parse as wdparse
from wikidata_lib import labels as wdlabels


# ── KM artist QIDs ────────────────────────────────────────────────────────────
# All artists whose works appear in "Klasiskais modernisms" (Q109893311).
# Zeltiņš and Silzemnieks not yet listed — add their QIDs once stubs are uploaded.

KM_ARTIST_QIDS: list[str] = [
    "Q4150307",   # Jāzeps Grosvalds
    "Q5763621",   # Jēkabs Kazaks
    "Q6711504",   # Romans Suta
    "Q13560149",  # Ādolfs Tone
    "Q6429766",   # Konrāds Ubāns
    "Q4422702",   # Oto Skulme
    "Q7877565",   # Uga Skulme
    "Q18193873",  # Niklāvs Strunke
    "Q2093617",   # Aleksandra Beļcova
    "Q5733973",   # Jānis Liepiņš
    "Q8479028",   # Ludolfs Liberts
    "Q1341721",   # Gustavs Klucis
    "Q2632125",   # Aleksandrs Drēviņš
    "Q1387109",   # Kārlis Johansons
    "Q4102980",   # Johans Valters
    "Q11238108",  # Ģederts Eliass
    "Q4410059",   # Leo Svemps
    "Q2037175",   # Otomārs Nemme
    "Q2663470",   # Vilhelms Purvītis
    "Q16356282",  # Voldemārs Matvejs
    "Q16697625",  # Jānis Siliņš
    "Q109894439", # Jānis Plase
]

# ── Controlled-vocabulary mappings ────────────────────────────────────────────

OBJECT_TYPE_MAP: dict[str, str] = {
    "Q3305213":  "painting",
    "Q18761202": "watercolour painting",
    "Q22060043": "linocut print",
    "Q18219090": "woodcut print",
    "Q93184":    "drawing",
    "Q860861":   "sculpture",
    "Q179700":   "statue",
    "Q4502142":  "visual art",
}

# Media (binders / coloured substances) vs supports (surfaces)
MEDIA_QIDS: set[str] = {
    "Q296955",   # oil paint
    "Q3374389",  # watercolour paint
    "Q175166",   # tempera
    "Q204330",   # gouache
    "Q127418",   # ink
    "Q429659",   # shellac / zīmoglaka
    "Q1783255",  # coloured pencil
    "Q34095",    # bronze
}

SUPPORT_QIDS: set[str] = {
    "Q4259259",  # canvas
    "Q11472",    # paper
    "Q18668582", # cardboard
    "Q1348059",  # wood panel / panel
    "Q11469",    # glass
    "Q22657",    # concrete
}

MATERIAL_DISPLAY: dict[str, str] = {
    "Q296955":   "oil",
    "Q3374389":  "watercolour",
    "Q175166":   "tempera",
    "Q204330":   "gouache",
    "Q127418":   "ink",
    "Q429659":   "shellac",
    "Q1783255":  "coloured pencil",
    "Q34095":    "bronze",
    "Q4259259":  "canvas",
    "Q11472":    "paper",
    "Q18668582": "cardboard",
    "Q1348059":  "panel",
    "Q11469":    "glass",
    "Q22657":    "concrete",
}

COLLECTION_MAP: dict[str, str] = {
    "Q1370465":  "Latvian National Museum of Art",
    "Q183334":   "State Tretyakov Gallery",
    "Q247518":   "MOMus — Museum of Modern Art — Costakis Collection",
    "Q4465070":  "Tukuma muzejs",
    "Q10717657": "Värmlands Museum",
}

CIRCA_QID = "Q5727902"

SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"
USER_AGENT      = "Ars Accordia/1.0 (https://github.com/elembam/artbase-catalogue)"


# ── SPARQL ────────────────────────────────────────────────────────────────────

def sparql_artworks_by_artists(artist_qids: list[str]) -> list[str]:
    """Return QIDs of all artworks P170-linked to any of the given artists."""
    values = " ".join(f"wd:{q}" for q in artist_qids)
    query = f"""
SELECT DISTINCT ?item WHERE {{
  VALUES ?artist {{ {values} }}
  ?item wdt:P170 ?artist .
}}
"""
    params = urllib.parse.urlencode({"query": query, "format": "json"})
    url    = f"{SPARQL_ENDPOINT}?{params}"
    req    = urllib.request.Request(url, headers={
        "User-Agent": USER_AGENT,
        "Accept": "application/sparql-results+json",
    })
    for attempt in range(4):
        if attempt > 0:
            wait = 15 * (2 ** (attempt - 1))  # 15s, 30s, 60s
            print(f"  WDQS rate-limited — retrying in {wait}s…")
            time.sleep(wait)
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                data = json.loads(r.read())
            return [
                b["item"]["value"].split("/")[-1]
                for b in data.get("results", {}).get("bindings", [])
            ]
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504):
                continue   # transient — retry
            print(f"  ✗ SPARQL HTTP {e.code}: {e}", file=sys.stderr)
            return []
        except Exception as e:
            print(f"  ✗ SPARQL failed: {e}", file=sys.stderr)
            return []
    print("  ✗ SPARQL: gave up after 4 attempts (WDQS overloaded). Try --qids instead.", file=sys.stderr)
    return []


# ── Quantity parsing (dimensions) ─────────────────────────────────────────────

def get_quantity_cm(entity: dict, pid: str) -> Optional[float]:
    """Return the numeric value of a quantity claim (e.g. P2048 height in cm)."""
    claims = entity.get("claims", {}).get(pid, [])
    for claim in claims:
        if claim.get("rank") == "deprecated":
            continue
        snak = claim.get("mainsnak", {})
        if snak.get("snaktype") == "value":
            dv = snak.get("datavalue", {})
            if dv.get("type") == "quantity":
                try:
                    return float(dv["value"]["amount"])
                except (KeyError, ValueError):
                    pass
    return None


# ── Date parsing ──────────────────────────────────────────────────────────────

def parse_date_display(entity: dict) -> tuple[str | None, int | None, int | None]:
    """
    Return (display_string, earliest_year, latest_year) from P571.
    Handles year, decade, century precision and P1480 (circa) qualifier.
    """
    claims = entity.get("claims", {}).get("P571", [])
    for claim in claims:
        if claim.get("rank") == "deprecated":
            continue
        snak = claim.get("mainsnak", {})
        if snak.get("snaktype") != "value":
            continue
        dv = snak.get("datavalue", {})
        if dv.get("type") != "time":
            continue
        tv       = dv["value"]
        precision = tv.get("precision", 0)
        raw      = tv.get("time", "").lstrip("+-").split("T")[0]
        segments = raw.split("-")
        year     = int(segments[0]) if segments and segments[0].isdigit() else None
        if year is None:
            continue

        # Check for circa qualifier
        is_circa = any(
            ref_snak.get("datavalue", {}).get("value", {}).get("id") == CIRCA_QID
            for qualifier in claim.get("qualifiers", {}).get("P1480", [])
            for ref_snak in [qualifier.get("datavalue", {})]
        )
        # Simpler circa check via raw qualifier structure
        is_circa = bool(claim.get("qualifiers", {}).get("P1480"))

        if precision >= 9:   # year
            display = f"c. {year}" if is_circa else str(year)
            return display, year, year
        elif precision == 8: # decade
            decade = (year // 10) * 10
            display = f"c. {decade}s" if is_circa else f"{decade}s"
            return display, decade, decade + 9
        elif precision == 7: # century
            c = (year // 100) + 1
            display = f"c. {c}th century" if is_circa else f"{c}th century"
            return display, (c - 1) * 100, c * 100 - 1
    return None, None, None


# ── Material display string ───────────────────────────────────────────────────

def build_materials_display(material_qids: list[str]) -> str:
    """
    Convert a list of material QIDs to a conventional display string.
    e.g. [Q296955, Q4259259] → "Oil on canvas"
    Falls back to labels for any unknown QIDs.
    """
    if not material_qids:
        return ""

    media    = [q for q in material_qids if q in MEDIA_QIDS]
    supports = [q for q in material_qids if q in SUPPORT_QIDS]
    other    = [q for q in material_qids if q not in MEDIA_QIDS and q not in SUPPORT_QIDS]

    def disp(q: str) -> str:
        return MATERIAL_DISPLAY.get(q) or wdlabels.label_for(q)

    parts = []
    if media:
        parts.append(", ".join(disp(q) for q in media).capitalize())
    if supports:
        parts.append(" ".join(disp(q) for q in supports))
    if other:
        parts.append(", ".join(disp(q) for q in other))

    if media and supports:
        return f"{parts[0]} on {parts[1]}" + (f", {parts[2]}" if other else "")
    return ", ".join(parts) if parts else ""


# ── Artist index ──────────────────────────────────────────────────────────────

def build_artist_index(artists_dir: Path) -> dict[str, dict]:
    """Return {wikidata_qid: artist_json} for all artists with confirmed Wikidata QIDs."""
    index: dict[str, dict] = {}
    for f in artists_dir.glob("*.json"):
        try:
            data = json.loads(f.read_text("utf-8"))
            qid  = (
                data.get("authority_links", {}).get("wikidata", {}).get("id")
                or data.get("authorities", {}).get("wikidata", {}).get("id")
            )
            if qid:
                index[qid] = data
        except Exception:
            continue
    return index


# ── ArtBase ID assignment ─────────────────────────────────────────────────────

def build_wikidata_id_map(artworks_dir: Path) -> dict[str, str]:
    """Return {wikidata_qid: artbase_id} for artworks already in canonical store."""
    mapping: dict[str, str] = {}
    for f in artworks_dir.glob("*.json"):
        try:
            data = json.loads(f.read_text("utf-8"))
            qid  = data.get("authority_links", {}).get("wikidata", {}).get("id")
            aid  = data.get("artbase_id")
            if qid and aid:
                mapping[qid] = aid
        except Exception:
            continue
    return mapping


def next_artbase_id(artworks_dir: Path) -> str:
    """Return the next AP-2026-XXXXXX ID, sequentially after the highest in use."""
    existing = []
    for f in artworks_dir.glob("AP-2026-*.json"):
        m = re.search(r"AP-2026-(\d+)", f.stem)
        if m:
            existing.append(int(m.group(1)))
    nxt = (max(existing) + 1) if existing else 1
    return f"AP-2026-{nxt:06d}"


# ── Transform ─────────────────────────────────────────────────────────────────

def transform(
    qid:            str,
    entity:         dict,
    artbase_id:     str,
    artist_index:   dict[str, dict],
) -> dict:
    """Transform a Wikidata entity dict to canonical artwork JSON."""

    labels_en = entity.get("labels", {}).get("en", {}).get("value") or ""
    labels_lv = entity.get("labels", {}).get("lv", {}).get("value") or ""
    title     = labels_lv or labels_en  # prefer Latvian for Latvian artworks

    # Type of object
    type_qids  = wdparse.get_all_entity_ids(entity, "P31")
    obj_type   = next((OBJECT_TYPE_MAP[q] for q in type_qids if q in OBJECT_TYPE_MAP), "painting")

    # Maker
    creator_qids = wdparse.get_all_entity_ids(entity, "P170")
    artist_data  = next((artist_index[q] for q in creator_qids if q in artist_index), None)
    maker_id     = artist_data.get("artbase_id") if artist_data else None
    maker_name   = (
        artist_data.get("identity", {}).get("preferred_name") if artist_data
        else wdlabels.label_for(creator_qids[0]) if creator_qids
        else None
    )

    # Date
    date_display, date_earliest, date_latest = parse_date_display(entity)

    # Materials
    material_qids    = wdparse.get_all_entity_ids(entity, "P186")
    materials_display = build_materials_display(material_qids)

    # Dimensions
    height = get_quantity_cm(entity, "P2048")
    width  = get_quantity_cm(entity, "P2049")
    dims_display = f"{height} × {width} cm" if height and width else None

    # Collection
    coll_qid  = wdparse.get_entity_id(entity, "P195")
    coll_name = COLLECTION_MAP.get(coll_qid) or (wdlabels.label_for(coll_qid) if coll_qid else None)

    # Inventory number
    inv_no = wdparse.get_string_value(entity, "P217")

    now = datetime.now(timezone.utc).isoformat() + "Z"

    return {
        "_schema":    "artbase:artwork:v1",
        "artbase_id": artbase_id,
        "version":    1,
        "exported":   now,
        "visibility": "public",
        "object_id": {
            "title":              title or None,
            "title_en":           labels_en or None,
            "title_lv":           labels_lv or None,
            "object_type":        obj_type,
            "materials":          materials_display or None,
            "dimensions_display": dims_display,
            "height_cm":          height,
            "width_cm":           width,
            "date_display":       date_display,
            "date_earliest":      date_earliest,
            "date_latest":        date_latest,
            "maker_id":           maker_id,
            "maker_display_name": maker_name,
            "has_photograph":     False,
        },
        "iconography": {
            "iconclass_codes":  [],
            "iconclass_labels": [],
            "depicts":          [],
        },
        "location": {
            "collection":       coll_name,
            "collection_qid":   coll_qid,
            "inventory_number": inv_no,
            "location_notes":   None,
        },
        "provenance": [],
        "authority_links": {
            "wikidata": {
                "scope":         "artwork_object",
                "system":        "Wikidata",
                "id":            qid,
                "uri":           f"https://www.wikidata.org/wiki/{qid}",
                "status":        "confirmed",
                "verified_date": now[:10],
                "notes":         None,
            },
            "artbase_id": None,
            "work_level":  [],
        },
        "rights": {
            "public_domain":    True,
            "copyright_status": "public_domain",
            "license":          "https://creativecommons.org/publicdomain/zero/1.0/",
            "attribution":      None,
            "source":           "Artist born before 1874 or work created before 1929 (Latvia)",
        },
        "media": [],
        "sources": [],
        "source_refs": [],
        "conflicts": [],
        "cataloguing": {
            "review_status":  "draft",
            "catalogued_by":  "wikidata_to_passports.py",
            "notes":          f"Auto-generated from Wikidata {qid}",
            "tasks":          [],
            "engagement_ids": [],
        },
    }


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Pull Wikidata artworks → canonical JSON → passports (replaces Airtable for public works)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--artists",
        help="Comma-separated artist QIDs (default: all KM artists)",
    )
    parser.add_argument(
        "--qids",
        help="Comma-separated artwork QIDs — skip SPARQL, fetch these directly",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Transform and print, but write nothing",
    )
    parser.add_argument(
        "--no-passports", action="store_true",
        help="Write canonical JSON only; skip passport and index HTML generation",
    )
    parser.add_argument(
        "--no-index", action="store_true",
        help="Skip regenerating passports/index.html",
    )
    parser.add_argument(
        "--update", action="store_true",
        help="Re-fetch and update existing canonical JSON (default: skip already-imported QIDs)",
    )
    args = parser.parse_args()

    ARTWORKS_DIR.mkdir(parents=True, exist_ok=True)

    # ── Step 1: determine artwork QIDs ───────────────────────────────────────
    if args.qids:
        artwork_qids = [q.strip() for q in args.qids.split(",") if q.strip()]
        print(f"Targeting {len(artwork_qids)} artwork QID(s) (direct)")
    else:
        artist_qids = (
            [q.strip() for q in args.artists.split(",") if q.strip()]
            if args.artists else KM_ARTIST_QIDS
        )
        print(f"Querying Wikidata for artworks by {len(artist_qids)} artist(s)…")
        artwork_qids = sparql_artworks_by_artists(artist_qids)
        print(f"  Found {len(artwork_qids)} artwork(s)")

    if not artwork_qids:
        print("Nothing to do.", file=sys.stderr)
        return 0

    # ── Step 2: filter out already-imported QIDs (unless --update) ───────────
    existing_map    = build_wikidata_id_map(ARTWORKS_DIR)   # {qid → artbase_id}
    artist_index    = build_artist_index(ARTISTS_DIR)

    new_qids     = [q for q in artwork_qids if q not in existing_map]
    update_qids  = [q for q in artwork_qids if q in existing_map] if args.update else []

    to_fetch = new_qids + update_qids
    print(f"  New: {len(new_qids)} · Update: {len(update_qids)} · Skip: {len(artwork_qids) - len(to_fetch)}")

    if not to_fetch:
        print("All QIDs already imported. Use --update to refresh.", file=sys.stderr)
        return 0

    # ── Step 3: fetch entity data ─────────────────────────────────────────────
    print(f"Fetching {len(to_fetch)} entities from Wikidata…")
    entities = wdfetch.fetch_entities(to_fetch)
    print(f"  Received {len(entities)} entities")

    # ── Step 4: transform and write ───────────────────────────────────────────
    written:   list[Path] = []
    skipped:   int        = 0

    for qid, entity in entities.items():
        # Assign or reuse artbase_id
        if qid in existing_map and args.update:
            artbase_id = existing_map[qid]
        else:
            artbase_id = next_artbase_id(ARTWORKS_DIR)

        try:
            canonical = transform(qid, entity, artbase_id, artist_index)
        except Exception as e:
            print(f"  ✗ {qid}: transform error — {e}", file=sys.stderr)
            skipped += 1
            continue

        title  = canonical["object_id"].get("title") or qid
        artist = canonical["object_id"].get("maker_display_name") or "?"
        score  = sum(1 for v in [
            canonical["object_id"].get("object_type"),
            canonical["object_id"].get("materials"),
            canonical["object_id"].get("dimensions_display"),
            canonical["object_id"].get("title"),
            canonical["object_id"].get("date_display"),
            canonical["object_id"].get("maker_id"),
        ] if v)
        print(f"  {'(dry)' if args.dry_run else '✓'} {artbase_id}  [{artist}]  {title!r}  ObjID:{score}/6")

        if args.dry_run:
            continue

        out_path = ARTWORKS_DIR / f"{artbase_id}.json"
        out_path.write_text(json.dumps(canonical, ensure_ascii=False, indent=2), encoding="utf-8")
        written.append(out_path)

    if args.dry_run or not written:
        print(f"\nDone. {len(written)} written, {skipped} skipped.")
        return 0

    print(f"\n{len(written)} canonical JSON file(s) written.")

    # ── Step 5: generate passport HTML (batch, not per-file) ─────────────────
    if not args.no_passports:
        print(f"\nGenerating passport HTML for all artworks…")
        gen    = SCRIPT_DIR / "passport_generator.py"
        result = subprocess.run(
            [sys.executable, str(gen), "--all"],
            capture_output=False, text=True,
        )
        if result.returncode != 0:
            print("  ✗ Passport generator reported errors (see above)", file=sys.stderr)

    # ── Step 6: regenerate index ──────────────────────────────────────────────
    if not args.no_index and not args.no_passports:
        print(f"\nRegenerating index…")
        idx = SCRIPT_DIR / "index_generator.py"
        result = subprocess.run([sys.executable, str(idx)], capture_output=True, text=True)
        if result.returncode == 0:
            print("  ✓ passports/index.html updated")
        else:
            print(f"  ✗ Index failed: {result.stderr.strip()}", file=sys.stderr)

    print(f"\nAll done. Push passports/ to GitHub to publish on arsaccordia.com.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
