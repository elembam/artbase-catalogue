#!/usr/bin/env python3
"""
hansabanka_batch_process.py — Process all 108 Hansabanka artists through
Wikidata reconciliation, ArtBase record creation, and QuickStatements generation.

Phases (run in order):
  reconcile  — Search Wikidata for each unrecorded artist; save report JSON
  create     — Create ArtBase JSON skeletons from the reconciliation report
  batches    — Generate QuickStatements P973 batches (10 artists each)
  patch28    — Add 'collections' field to the 28 artists already in ArtBase
  all        — Run reconcile → create → batches → patch28

Usage:
    python3 scripts/hansabanka_batch_process.py reconcile
    python3 scripts/hansabanka_batch_process.py create
    python3 scripts/hansabanka_batch_process.py batches
    python3 scripts/hansabanka_batch_process.py patch28
    python3 scripts/hansabanka_batch_process.py all

Dependencies:
    pip install requests

Output files:
    artbase_export/data/hansabanka_reconciliation.json   — Wikidata matches
    artbase_export/data/artists/ART-*.json               — New artist records
    artbase_export/data/contributions/hans_p973_batch_*.qs — QuickStatements
"""

import argparse
import json
import re
import sys
import time
from pathlib import Path
from datetime import date

try:
    import requests
except ImportError:
    print("Install dependencies: pip install requests")
    sys.exit(1)

# ── Paths ──────────────────────────────────────────────────────────────────────

REPO_ROOT    = Path(__file__).resolve().parent.parent
ARTISTS_DIR  = REPO_ROOT / "artbase_export" / "data" / "artists"
DATA_DIR     = REPO_ROOT / "artbase_export" / "data"
CONTRIB_DIR  = DATA_DIR / "contributions"
REPORT_FILE  = DATA_DIR / "hansabanka_reconciliation.json"
ARTISTS_HTML = REPO_ROOT / "artists"

CONTRIB_DIR.mkdir(parents=True, exist_ok=True)

# ── Constants ──────────────────────────────────────────────────────────────────

WIKIDATA_API    = "https://www.wikidata.org/w/api.php"
USER_AGENT      = "ArsAccordiaCataloguer/0.2 (arsaccordia.com; contact@arsaccordia.com)"
TODAY           = date.today().isoformat()
TODAY_QS        = f"+{TODAY}T00:00:00Z/11"
ARS_BASE_URL    = "https://arsaccordia.com/artists"
HANSABANKA_URL  = "https://arsaccordia.com/collections/hansabanka/"

HANSABANKA_COLLECTION = {
    "id": "hansabanka",
    "name": "Hansabanka Contemporary Art Collection",
    "short_name": "Hansabanka",
    "url": HANSABANKA_URL,
}

HANSABANKA_SOURCE_REF = {
    "source_id": "SRC-HANSABANKA-2007",
    "role": "collection catalogue",
    "accessed": None,
}

ARTIST_KEYWORDS = {
    "painter", "artist", "sculptor", "photographer", "draughtsman",
    "printmaker", "ceramicist", "designer", "illustrator", "graphic",
    "mākslienieks", "gleznotājs", "tēlnieks",  # Latvian
}

# ── Full Hansabanka artist roster (108 artists, from catalogue pages 222–229) ──
# Format: (name_as_in_catalogue, work_count)

HANSABANKA_ROSTER = [
    ("Aija Jurjāne", 2),
    ("Aija Ozoliņa", 7),
    ("Aija Zariņa", 3),
    ("Aleksandrs Dembo", 2),
    ("Aleksejs Naumovs", 6),
    ("Andrejs Kalnācs", 9),
    ("Andris Abļevs", 5),
    ("Andris Eglītis", 1),
    ("Andris Vītoliņš", 5),
    ("Andris Žegners", 4),
    ("Anita Meldere", 7),
    ("Anna Heinrihsone", 1),
    ("Arnis Pelšs", 1),
    ("Barbara Gaile", 3),
    ("Biruta Delle", 1),
    ("Dace Lapiņa", 1),
    ("Dace Lielā", 1),
    ("Daina Dagnija", 2),
    ("Džemma Skulme", 1),
    ("Edgars Valdmanis", 1),
    ("Edgars Vērpe", 3),
    ("Eduards Kalniņš", 1),
    ("Edvards Grūbe", 4),
    ("Edīte Gronova", 1),
    ("Egils Rozenbergs", 1),
    ("Elita Patmalniece", 2),
    ("Frančeska Kirke", 1),
    ("Genādijs Suhanovs", 3),
    ("Gita Okonova-Treice", 5),
    ("Gunta Liepiņa-Grīva", 4),
    ("Guntars Sietiņš", 3),
    ("Gunārs Krollis", 12),
    ("Gļebs Panteļejevs", 1),
    ("Harijs Brants", 2),
    ("Helēna Heinrihsone", 19),
    ("Herberts Siliņš", 4),
    ("Ieva Iltnerē", 4),
    ("Ieva Maurīte", 1),
    ("Ilmārs Blumbergs", 5),
    ("Ilze Avotiņa", 5),
    ("Ilze Diāne", 1),
    ("Ilze Libiete", 3),
    ("Ilze Neilande", 7),
    ("Imants Vecozols", 1),
    ("Indra Sproģe", 5),
    ("Indriķis Stūrmanis", 4),
    ("Indulis Zariņš", 1),
    ("Inese Lieckalniņa", 2),
    ("Inga Brūvere", 4),
    ("Inta Celmiņa", 6),
    ("Ināra Petruševiča", 5),
    ("Irēna Lūse", 9),
    ("Ivars Heinrihsons", 9),
    ("Ivars Poikāns", 3),
    ("Ivs Zenne", 4),
    ("Juris Jurjāns", 2),
    ("Juris Putrāms", 6),
    ("Jānis Kupčs", 1),
    ("Jānis Mitrēvics", 2),
    ("Jānis Spalviņš", 2),
    ("Jānis Tīdemanis", 2),
    ("Jāzeps Pīgoznis", 1),
    ("Jēkabs Spriņģis", 2),
    ("Jūlijs Vilumainis", 1),
    ("Kaspars Brambergs", 2),
    ("Kaspars Zariņš", 5),
    ("Kate Seržāne", 4),
    ("Kristaps Gulbis", 1),
    ("Kristaps Zariņš", 10),
    ("Kristaps Ģelzis", 6),
    ("Kristiana Dimitere", 5),
    ("Kristīne Drengere", 1),
    ("Kristīne Keire", 2),
    ("Kristīne Luīze Avotiņa", 2),
    ("Kārlis Siliņš", 3),
    ("Laima Bikše", 3),
    ("Laima Puntule", 2),
    ("Laris Strunke", 5),
    ("Leonīds Āriņš", 1),
    ("Lilija Dinere", 6),
    ("Linda Daņiļevska", 3),
    ("Ludolfs Liberts", 1),
    ("Līga Purmale", 3),
    ("Madara Gulbis", 1),
    ("Mihails Šemjakins", 3),
    ("Māra Vaičunas", 1),
    ("Māris Subačs", 10),
    ("Mārtiņš Krūklis", 7),
    ("Ojārs Pētersons", 3),
    ("Olga Šilova", 6),
    ("Oskars Mikāns", 1),
    ("Oskars Muižnieks", 3),
    ("Oļģerts Jaunarājs", 3),
    ("Ritums Ivanovs", 3),
    ("Rūdolfs Pinnis", 2),
    ("Sandra Krastiņa", 4),
    ("Tatjana Krivenkova", 11),
    ("Tomass Fēnikss", 2),
    ("Uno Daņiļevskis", 5),
    ("Valdis Bušs", 1),
    ("Vija Maldupe", 1),
    ("Vija Zariņa", 4),
    ("Vilis Ozols", 1),
    ("Vilnis Zābers", 4),
    ("Vineta Kaulača", 3),
    ("Vita Lēnerte-Grasa", 5),
    ("Vladislavs Grišins", 4),
    ("Ģirts Muižnieks", 6),
]


# ── Transliteration ────────────────────────────────────────────────────────────
# Latvian diacritics → ASCII uppercase.  Source and target must be same length.
# ā č ē ģ ī ķ ļ ņ š ū ž  (11 lowercase)  + uppercase equivalents (11)
_LV_TABLE = str.maketrans(
    "āčēģīķļņšūžĀČĒĢĪĶĻŅŠŪŽ",
    "ACEGIKLNSUZACEGIKLNSUZ",
)


def transliterate(s: str) -> str:
    """Remove Latvian diacritics → ASCII uppercase."""
    return s.translate(_LV_TABLE)


def name_to_id_slug(full_name: str, birth_year: str | None) -> str:
    """
    Convert 'Kristaps Zariņš' + '1961' → 'ART-ZARINS-1961'.
    Uses first part of hyphenated surnames.
    Unknown birth year → 'FL2007' (fl. = flourished, from catalogue date).
    """
    parts = full_name.strip().split()
    surname = parts[-1] if len(parts) > 1 else parts[0]
    # Use first component of hyphenated compound surnames
    surname = surname.split("-")[0]
    slug = transliterate(surname).upper()
    slug = re.sub(r"[^A-Z0-9]", "", slug)
    year = birth_year if birth_year else "FL2007"
    return f"ART-{slug}-{year}"


def ascii_name(name: str) -> str:
    """'Kristaps Zariņš' → 'Kristaps Zarins' (title-case, for search and name_variants)."""
    # Apply char-by-char: uppercase only if original char was uppercase
    result = []
    for ch in name:
        t = ch.translate(_LV_TABLE)
        if ch.islower():
            result.append(t.lower())
        else:
            result.append(t)
    return "".join(result)


# ── Wikidata helpers ───────────────────────────────────────────────────────────

def _wd_get(params: dict) -> dict:
    r = requests.get(WIKIDATA_API, params=params,
                     headers={"User-Agent": USER_AGENT}, timeout=15)
    r.raise_for_status()
    return r.json()


def search_wikidata(name: str) -> list[dict]:
    """
    Search Wikidata for an artist by name.  Returns list of candidate dicts
    with keys: qid, label, description, score (0-3).
    """
    results = []

    for search_name, lang in [(name, "en"), (name, "lv"), (ascii_name(name), "en")]:
        data = _wd_get({
            "action":   "wbsearchentities",
            "search":   search_name,
            "language": lang,
            "type":     "item",
            "format":   "json",
            "limit":    8,
        })
        for item in data.get("search", []):
            qid  = item["id"]
            if any(r["qid"] == qid for r in results):
                continue
            desc = (item.get("description") or "").lower()
            label = item.get("label") or ""
            score = 0
            if any(k in desc for k in ARTIST_KEYWORDS):
                score += 1
            if "latvian" in desc or "latvija" in desc or "latvijas" in desc:
                score += 1
            if name.lower().split()[-1] in label.lower():
                score += 1  # surname match
            results.append({
                "qid": qid,
                "label": label,
                "description": item.get("description") or "",
                "score": score,
            })

    return sorted(results, key=lambda x: -x["score"])


def fetch_birth_death(qid: str) -> tuple[str | None, str | None]:
    """Return (birth_year, death_year) from Wikidata P569/P570, or (None, None)."""
    data = _wd_get({
        "action":    "wbgetentities",
        "ids":       qid,
        "props":     "claims|labels|descriptions|sitelinks",
        "languages": "en|lv",
        "format":    "json",
    })
    entity = data.get("entities", {}).get(qid, {})
    claims = entity.get("claims", {})

    def extract_year(pid: str) -> str | None:
        stmts = claims.get(pid, [])
        if not stmts:
            return None
        val = stmts[0].get("mainsnak", {}).get("datavalue", {}).get("value", {})
        if isinstance(val, dict):
            t = val.get("time", "")
            m = re.match(r"\+(\d{4})", t)
            if m:
                return m.group(1)
        return None

    # Also collect sitelinks for later use
    sitelinks = entity.get("sitelinks", {})
    lv_label = (entity.get("labels", {}).get("lv") or {}).get("value")
    en_label = (entity.get("labels", {}).get("en") or {}).get("value")

    return (
        extract_year("P569"),
        extract_year("P570"),
        lv_label or en_label,
        "lvwiki" in sitelinks or "enwiki" in sitelinks,
    )


# ── Phase 1: Reconcile ─────────────────────────────────────────────────────────

def phase_reconcile():
    print("=" * 70)
    print("PHASE 1 — Wikidata Reconciliation")
    print("=" * 70)
    print(f"Total Hansabanka roster: {len(HANSABANKA_ROSTER)} artists")

    # Find which artists already have ArtBase records (match by preferred_name)
    existing: dict[str, str] = {}  # name → artbase_id
    for path in sorted(ARTISTS_DIR.glob("*.json")):
        try:
            artist = json.loads(path.read_text())
            pname = (artist.get("identity") or {}).get("preferred_name") or ""
            if pname:
                existing[pname] = artist["artbase_id"]
            # Also index name_variants
            for v in ((artist.get("identity") or {}).get("name_variants") or []):
                existing[v] = artist["artbase_id"]
        except Exception:
            continue

    need_records: list[tuple[str, int]] = []
    already_in: list[tuple[str, int, str]] = []

    for name, count in HANSABANKA_ROSTER:
        if name in existing:
            already_in.append((name, count, existing[name]))
        else:
            need_records.append((name, count))

    print(f"Already in ArtBase     : {len(already_in)}")
    print(f"Need new records       : {len(need_records)}")
    print()

    # Wikidata search for the ones needing records
    report: list[dict] = []

    for i, (name, count) in enumerate(need_records, 1):
        print(f"[{i:3}/{len(need_records)}] {name} ({count} works) ... ", end="", flush=True)
        time.sleep(0.5)  # polite rate limiting

        candidates = search_wikidata(name)
        high = [c for c in candidates if c["score"] >= 2]
        mid  = [c for c in candidates if c["score"] == 1]

        if len(high) == 1:
            status = "auto_match"
        elif len(high) > 1:
            status = "candidate_verify"
        elif mid:
            status = "candidate_verify"
        else:
            status = "no_match"

        top = candidates[:3] if candidates else []
        print(f"{status}  {top[0]['qid'] if top else ''} {top[0]['description'][:50] if top else ''}")

        report.append({
            "name":          name,
            "work_count":    count,
            "status":        status,
            "candidates":    top,
            "chosen_qid":    top[0]["qid"] if status == "auto_match" else None,
            "birth_year":    None,
            "death_year":    None,
            "wikidata_label": None,
            "has_wikipedia": False,
            "artbase_id":    None,
        })

    # Fetch birth/death years for matched artists
    print()
    print("Fetching birth/death data for matches...")
    for entry in report:
        qid = entry.get("chosen_qid") or (
            entry["candidates"][0]["qid"] if entry["candidates"] and entry["status"] == "auto_match" else None
        )
        if not qid:
            continue
        time.sleep(0.3)
        try:
            by, dy, label, has_wp = fetch_birth_death(qid)
            entry["birth_year"] = by
            entry["death_year"] = dy
            entry["wikidata_label"] = label
            entry["has_wikipedia"] = has_wp
        except Exception as e:
            print(f"  Warning: could not fetch {qid}: {e}")

    # Assign ArtBase IDs
    used_ids: set[str] = set(existing.values())
    for entry in report:
        if entry["status"] == "auto_match":
            slug = name_to_id_slug(entry["name"], entry["birth_year"])
            # Ensure uniqueness
            candidate_id = slug
            suffix = 0
            while candidate_id in used_ids:
                suffix += 1
                candidate_id = f"{slug}B{suffix}"
            entry["artbase_id"] = candidate_id
            used_ids.add(candidate_id)

    # Write report
    full_report = {
        "generated": TODAY,
        "total_roster": len(HANSABANKA_ROSTER),
        "already_in_artbase": [
            {"name": n, "work_count": c, "artbase_id": aid}
            for n, c, aid in already_in
        ],
        "new_artists": report,
    }
    REPORT_FILE.write_text(json.dumps(full_report, indent=2, ensure_ascii=False))

    # Summary
    auto  = sum(1 for e in report if e["status"] == "auto_match")
    cand  = sum(1 for e in report if e["status"] == "candidate_verify")
    none_ = sum(1 for e in report if e["status"] == "no_match")
    print()
    print(f"{'─'*50}")
    print(f"auto_match        : {auto}  (JSON records will be created)")
    print(f"candidate_verify  : {cand}  (review candidates manually)")
    print(f"no_match          : {none_}  (need manual Wikidata search)")
    print(f"{'─'*50}")
    print(f"Report saved → {REPORT_FILE.relative_to(REPO_ROOT)}")
    print()
    print("Candidate verify — pick the right QID and set status to 'auto_match':")
    for e in report:
        if e["status"] == "candidate_verify":
            print(f"  {e['name']:35} | ", end="")
            for c in e["candidates"][:2]:
                print(f"{c['qid']} ({c['description'][:40]})  ", end="")
            print()
    print()
    print("No match — need manual Wikidata search or new item creation:")
    for e in report:
        if e["status"] == "no_match":
            print(f"  {e['name']:35}  ({e['work_count']} works)")


# ── Phase 2: Create ArtBase JSON records ───────────────────────────────────────

def _authority_links_block(qid: str | None, status: str = "confirmed") -> dict:
    base = {k: {"id": None, "uri": None, "status": "search_needed",
                 "verified_date": None, "notes": None}
            for k in ["wikidata", "viaf", "ulan", "isni", "rkd",
                       "lc_naco", "gnd", "bnf", "libris"]}
    base["artbase_id"] = None
    if qid:
        base["wikidata"] = {
            "id": qid,
            "uri": f"https://www.wikidata.org/wiki/{qid}",
            "status": status,
            "verified_date": TODAY if status == "confirmed" else None,
            "notes": None,
        }
    return base


def phase_create():
    if not REPORT_FILE.exists():
        print("Run 'reconcile' phase first.")
        sys.exit(1)

    report = json.loads(REPORT_FILE.read_text())
    new_artists = report["new_artists"]
    to_create = [e for e in new_artists if e["status"] == "auto_match" and e.get("artbase_id")]

    print("=" * 70)
    print(f"PHASE 2 — Creating {len(to_create)} ArtBase JSON records")
    print("=" * 70)

    created = 0
    skipped = 0

    for entry in sorted(to_create, key=lambda x: -x["work_count"]):
        aid     = entry["artbase_id"]
        name    = entry["name"]
        qid     = entry["chosen_qid"]
        by      = entry.get("birth_year")
        dy      = entry.get("death_year")
        count   = entry["work_count"]
        out_path = ARTISTS_DIR / f"{aid}.json"

        if out_path.exists():
            print(f"  skip  {aid}  (file exists)")
            skipped += 1
            continue

        sort_parts = name.rsplit(" ", 1)
        sort_name  = f"{sort_parts[-1]}, {sort_parts[0]}" if len(sort_parts) == 2 else name

        record = {
            "artbase_id": aid,
            "airtable_id": None,
            "artbase_canonical_id": None,
            "version": 1,
            "created": TODAY,
            "exported": f"{TODAY}T00:00:00Z",
            "visibility": "public",
            "identity": {
                "preferred_name": name,
                "preferred_name_language": "lv",
                "full_name": name,
                "name_variants": [ascii_name(name)],
                "sort_name": sort_name,
            },
            "life": {
                "birth_date": {
                    "value": by,
                    "precision": "year",
                    "status": "working" if by else "unknown",
                    "source_ids": ["SRC-HANSABANKA-2007"],
                    "notes": None,
                },
                "death_date": {
                    "value": dy,
                    "precision": "year" if dy else None,
                    "status": "working" if dy else "unknown",
                    "source_ids": [],
                    "notes": None,
                },
                "birth_place": {"display": None, "tgn_uri": None, "wikidata_qid": None, "source_ids": []},
                "death_place": {"display": None, "tgn_uri": None, "wikidata_qid": None, "source_ids": []},
            },
            "descriptors": {
                "nationality": "Latvian",
                "citizenship": [],
                "occupations": ["artist"],
                "occupations_aat": [],
                "media": [],
                "subjects": [],
                "movement_notes": None,
                "biography_summary": None,
            },
            "authority_links": _authority_links_block(qid),
            "sources": [],
            "source_refs": [HANSABANKA_SOURCE_REF],
            "conflicts": [],
            "cataloguing": {
                "review_status": "draft",
                "catalogued_by": None,
                "notes": f"Added from Hansabanka 2007 catalogue. {count} works in collection.",
                "tasks": [
                    "Verify occupation (painter/sculptor/etc.)",
                    "Search VIAF",
                    "Search Getty ULAN",
                    f"Add P973 to Wikidata {qid}",
                ],
                "engagement_ids": [],
            },
            "_schema": "artbase:artist:v1",
            "collections": [
                {**HANSABANKA_COLLECTION, "work_count": count, "display_name": name}
            ],
        }

        out_path.write_text(json.dumps(record, indent=2, ensure_ascii=False))
        print(f"  ✓ {aid:35}  {name}  ({count} works)  QID={qid}")
        created += 1

    print(f"\n{created} records created, {skipped} skipped.")
    if skipped or any(e["status"] == "candidate_verify" for e in new_artists):
        cand = [e for e in new_artists if e["status"] == "candidate_verify"]
        none_ = [e for e in new_artists if e["status"] == "no_match"]
        print(f"\nStill pending:")
        print(f"  {len(cand)} candidate_verify — edit report, set status='auto_match' + chosen_qid, re-run create")
        print(f"  {len(none_)} no_match — need manual Wikidata search")


# ── Phase 3: Generate QuickStatements P973 batches ────────────────────────────

def phase_batches():
    print("=" * 70)
    print("PHASE 3 — QuickStatements P973 batches")
    print("=" * 70)

    # Collect all artists with QID + live HTML page (or at least a JSON record)
    eligible: list[dict] = []

    for path in sorted(ARTISTS_DIR.glob("*.json")):
        try:
            artist = json.loads(path.read_text())
        except Exception:
            continue

        # Only Hansabanka artists (check collections)
        cols = artist.get("collections") or []
        if not any(c.get("id") == "hansabanka" for c in cols):
            continue

        aid  = artist.get("artbase_id", "")
        wd   = (artist.get("authority_links") or {}).get("wikidata") or {}
        qid  = wd.get("id")
        status = wd.get("status", "")

        if not qid or status not in ("confirmed", "working"):
            continue

        # Check if page will exist (has JSON = will have HTML after generation)
        page_url = f"{ARS_BASE_URL}/{aid}.html"
        work_count = next(
            (c["work_count"] for c in cols if c["id"] == "hansabanka"), 0
        )
        name = (artist.get("identity") or {}).get("preferred_name", aid)

        eligible.append({
            "artbase_id": aid,
            "qid": qid,
            "name": name,
            "url": page_url,
            "work_count": work_count,
        })

    # Sort by work count descending (highest priority first)
    eligible.sort(key=lambda x: -x["work_count"])

    BATCH_SIZE = 10
    batches = [eligible[i:i+BATCH_SIZE] for i in range(0, len(eligible), BATCH_SIZE)]

    print(f"Eligible artists (QID confirmed + Hansabanka collection): {len(eligible)}")
    print(f"Batches of {BATCH_SIZE}: {len(batches)}")
    print()

    for batch_num, batch in enumerate(batches, 1):
        # Name by work-count range for clarity
        counts = [a["work_count"] for a in batch]
        batch_name = f"hans_p973_batch_{batch_num:02d}_{TODAY}"
        out_file = CONTRIB_DIR / f"{batch_name}.qs"

        lines = []
        for a in batch:
            url  = a["url"]
            qid  = a["qid"]
            # P973: described at URL; S854: reference URL; S813: retrieved date
            line = f'{qid}\tP973\t"{url}"\tS854\t"{url}"\tS813\t{TODAY_QS}'
            lines.append(line)

        out_file.write_text("\n".join(lines) + "\n", encoding="utf-8")

        print(f"  Batch {batch_num:2}: {len(batch)} artists (works: {max(counts)}–{min(counts)})")
        for a in batch:
            print(f"           {a['qid']:12} {a['name']:35} {a['work_count']} works")
        print(f"    → {out_file.relative_to(REPO_ROOT)}")
        print()

    if not eligible:
        print("No eligible artists yet — run 'reconcile' and 'create' phases first.")

    print("Upload plan:")
    for i, batch in enumerate(batches, 1):
        counts = [a["work_count"] for a in batch]
        name = f"hans_p973_batch_{i:02d}_{TODAY}"
        print(f"  Batch {i:2}: {name}.qs  ({len(batch)} artists, {max(counts)}–{min(counts)} works)")
    print()
    print("Submit at: https://quickstatements.toolforge.org/")
    print("Format: Tab-separated V1 (paste content of .qs file)")
    print("Note: No S248 — Ars Accordia Wikidata item does not exist yet.")


# ── Phase 4: Patch existing 28 artists with Hansabanka collections field ───────

def phase_patch28():
    if not REPORT_FILE.exists():
        print("Run 'reconcile' phase first.")
        sys.exit(1)

    report = json.loads(REPORT_FILE.read_text())
    already_in = {e["name"]: (e["artbase_id"], 0) for e in report.get("already_in_artbase", [])}

    # Build work-count lookup from roster
    roster_counts = {name: count for name, count in HANSABANKA_ROSTER}

    print("=" * 70)
    print("PHASE 4 — Patching existing 28 ArtBase records with Hansabanka collection")
    print("=" * 70)

    patched = 0
    skipped = 0

    for name, (aid, _) in sorted(already_in.items()):
        path = ARTISTS_DIR / f"{aid}.json"
        if not path.exists():
            print(f"  warn  {aid}  file not found")
            continue

        artist = json.loads(path.read_text())
        cols = artist.get("collections") or []

        # Check if already patched
        if any(c.get("id") == "hansabanka" for c in cols):
            print(f"  skip  {aid}  already has hansabanka collection")
            skipped += 1
            continue

        count = roster_counts.get(name, 0)
        cols.append({
            **HANSABANKA_COLLECTION,
            "work_count": count,
            "display_name": name,
        })
        artist["collections"] = cols

        path.write_text(json.dumps(artist, indent=2, ensure_ascii=False))
        print(f"  ✓ {aid:35}  {name}  ({count} works)")
        patched += 1

    print(f"\n{patched} patched, {skipped} already done.")


# ── CLI ────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("phase", choices=["reconcile", "create", "batches", "patch28", "all"],
                        help="Which phase to run")
    args = parser.parse_args()

    if args.phase in ("reconcile", "all"):
        phase_reconcile()
    if args.phase in ("create", "all"):
        phase_create()
    if args.phase in ("batches", "all"):
        phase_batches()
    if args.phase in ("patch28", "all"):
        phase_patch28()


if __name__ == "__main__":
    main()
