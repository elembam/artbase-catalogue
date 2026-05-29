import os
#!/usr/bin/env python3
"""
wikidata_enrich.py — Deep Wikidata enrichment for Ars Accordia artist records.

For each artist with a *confirmed* Wikidata QID:
  - Fetch Tier 1 fields: birth/death date+place, LNDB ID, image, descriptions
  - Fetch Tier 2 fields: education, movement, genre (stored as "wikidata_auto")
  - Write enrichment back to canonical JSON and Airtable
  - Track idempotency via _meta.wikidata_revision_id (skip if unchanged)
  - Respect manual_overrides: those fields are never overwritten (unless --force)
  - Produce a diff report in reports/

CLI:
    python3 scripts/wikidata_enrich.py --artist ART-AIDE-1913
    python3 scripts/wikidata_enrich.py --all
    python3 scripts/wikidata_enrich.py --all --dry-run
    python3 scripts/wikidata_enrich.py --all --skip-airtable
    python3 scripts/wikidata_enrich.py --all --force
    python3 scripts/wikidata_enrich.py --all --since 2026-05-01
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))

from wikidata_lib import fetch as wdfetch
from wikidata_lib import parse as wdparse
from wikidata_lib import labels as wdlabels
from wikidata_lib.airtable_sync import AirtableSync

# ── Config ─────────────────────────────────────────────────────────────────────
REPO_ROOT   = Path(__file__).resolve().parent.parent
DATA_DIR    = REPO_ROOT / "artbase_export" / "data" / "artists"
REPORTS_DIR = REPO_ROOT / "reports"

TOKEN      = os.getenv("AIRTABLE_TOKEN", "")
BASE_ID    = "appoyRXU3qxxKZcbp"
TABLE_NAME = "Artists_Makers"


# ── Skip rules ─────────────────────────────────────────────────────────────────

def should_skip(artist_data: dict) -> Optional[str]:
    """Return skip reason string, or None to proceed."""
    if artist_data.get("_meta", {}).get("do_not_enrich"):
        return "do_not_enrich flag"

    wd = (
        artist_data.get("authority_links", {}).get("wikidata")
        or artist_data.get("authorities", {}).get("wikidata")
    )
    if not wd:
        return "no wikidata block"

    qid = wd.get("id") if isinstance(wd, dict) else None
    if not qid:
        return "no QID"

    status = wd.get("status") if isinstance(wd, dict) else None
    if status == "candidate_verify":
        return "candidate (needs verification)"

    return None


def get_qid(artist_data: dict) -> Optional[str]:
    wd = (
        artist_data.get("authority_links", {}).get("wikidata")
        or artist_data.get("authorities", {}).get("wikidata")
    )
    if isinstance(wd, dict):
        return wd.get("id")
    return None


# ── Enrichment extraction ──────────────────────────────────────────────────────

def extract_enrichment(entity: dict, labels_map: dict[str, str]) -> dict:
    """Pull all enrichment fields from a Wikidata entity."""
    enriched: dict[str, Any] = {}

    # Tier 1 — birth/death dates with precision
    birth_val, birth_prec = wdparse.parse_time_value(entity, "P569")
    enriched["birth_date"]           = birth_val
    enriched["birth_date_precision"] = birth_prec

    death_val, death_prec = wdparse.parse_time_value(entity, "P570")
    enriched["death_date"]           = death_val
    enriched["death_date_precision"] = death_prec

    # Tier 1 — birth/death place
    birth_qid = wdparse.get_entity_id(entity, "P19")
    if birth_qid:
        enriched["birth_place"] = {"label": labels_map.get(birth_qid, birth_qid), "wikidata_id": birth_qid}

    death_qid = wdparse.get_entity_id(entity, "P20")
    if death_qid:
        enriched["death_place"] = {"label": labels_map.get(death_qid, death_qid), "wikidata_id": death_qid}

    # Tier 1 — LNDB (P7400)
    lndb = wdparse.get_string_value(entity, "P7400")
    if lndb:
        enriched["lndb_id"] = lndb

    # Tier 1 — image (P18)
    img_filename = wdparse.get_image_filename(entity)
    enriched["image"] = wdparse.build_image_urls(img_filename) if img_filename else None

    # Tier 1 — descriptions
    enriched["description_en"] = wdparse.get_description(entity, "en")
    enriched["description_lv"] = wdparse.get_description(entity, "lv")

    # Tier 2 — unverified structured data
    def tier2(pid: str) -> list[dict]:
        return [
            {"label": labels_map.get(q, q), "wikidata_id": q, "source": "wikidata_auto"}
            for q in wdparse.get_all_entity_ids(entity, pid)
        ]

    enriched["education"] = tier2("P69")
    enriched["movement"]  = tier2("P135")
    enriched["genre"]     = tier2("P136")

    return enriched


# ── Diff & apply ──────────────────────────────────────────────────────────────

def compute_diff(current_flat: dict, new_values: dict, manual_overrides: list[str], force: bool) -> list[dict]:
    changes = []
    for field, new_val in new_values.items():
        if new_val is None:
            continue
        if new_val == [] or new_val == {}:
            continue
        if field in manual_overrides and not force:
            continue
        old_val = current_flat.get(field)
        if old_val != new_val:
            changes.append({"field": field, "old": old_val, "new": new_val})
    return changes


def _nested_get(d: dict, keys: list[str]) -> Any:
    for k in keys:
        if not isinstance(d, dict):
            return None
        d = d.get(k)
    return d


def apply_enrichment_to_json(
    artist_data: dict,
    enriched: dict,
    manual_overrides: list[str],
    force: bool,
    revision_id: int,
    now_iso: str,
) -> tuple[list[dict], dict]:
    """Returns (changes_list, updated_data). Writes to a deep copy."""
    updated = copy.deepcopy(artist_data)

    # Build flat view of current values for comparison
    life = updated.get("life", {})
    bd   = life.get("birth_date", {}) if isinstance(life.get("birth_date"), dict) else {}
    dd   = life.get("death_date", {}) if isinstance(life.get("death_date"), dict) else {}
    bp   = life.get("birth_place", {}) if isinstance(life.get("birth_place"), dict) else {}
    dp   = life.get("death_place", {}) if isinstance(life.get("death_place"), dict) else {}

    current_flat = {
        "birth_date":           bd.get("value") or updated.get("birth_date"),
        "birth_date_precision": bd.get("precision") or updated.get("birth_date_precision"),
        "death_date":           dd.get("value") or updated.get("death_date"),
        "death_date_precision": dd.get("precision") or updated.get("death_date_precision"),
        "birth_place":          bp.get("display") or updated.get("birth_place"),
        "death_place":          dp.get("display") or updated.get("death_place"),
        "lndb_id":              _nested_get(updated, ["authority_links", "lndb", "id"]) or _nested_get(updated, ["authorities", "lndb"]),
        "image":                updated.get("image"),
        "description_en":       updated.get("description_en"),
        "description_lv":       updated.get("description_lv"),
        "education":            updated.get("education"),
        "movement":             updated.get("movement"),
        "genre":                updated.get("genre"),
    }

    changes = compute_diff(current_flat, enriched, manual_overrides, force)
    if not changes:
        return [], updated

    for change in changes:
        field = change["field"]
        val   = change["new"]

        if field in ("birth_date", "birth_date_precision"):
            if "life" not in updated:
                updated["life"] = {}
            if not isinstance(updated["life"].get("birth_date"), dict):
                updated["life"]["birth_date"] = {}
            key = "value" if field == "birth_date" else "precision"
            updated["life"]["birth_date"][key] = val

        elif field in ("death_date", "death_date_precision"):
            if "life" not in updated:
                updated["life"] = {}
            if not isinstance(updated["life"].get("death_date"), dict):
                updated["life"]["death_date"] = {}
            key = "value" if field == "death_date" else "precision"
            updated["life"]["death_date"][key] = val

        elif field == "birth_place":
            if "life" not in updated:
                updated["life"] = {}
            if not isinstance(updated["life"].get("birth_place"), dict):
                updated["life"]["birth_place"] = {}
            updated["life"]["birth_place"]["display"]     = val.get("label")
            updated["life"]["birth_place"]["wikidata_qid"] = val.get("wikidata_id")

        elif field == "death_place":
            if "life" not in updated:
                updated["life"] = {}
            if not isinstance(updated["life"].get("death_place"), dict):
                updated["life"]["death_place"] = {}
            updated["life"]["death_place"]["display"]     = val.get("label")
            updated["life"]["death_place"]["wikidata_qid"] = val.get("wikidata_id")

        elif field == "lndb_id":
            if "authority_links" in updated:
                updated["authority_links"]["lndb"] = {"id": val, "status": "confirmed", "source": "wikidata_auto"}
            elif "authorities" in updated:
                updated["authorities"]["lndb"] = val
            else:
                updated["lndb_id"] = val

        else:
            updated[field] = val

    # Update _meta
    meta = updated.setdefault("_meta", {})
    meta["wikidata_last_enriched"] = now_iso
    meta["wikidata_revision_id"]   = revision_id
    if "manual_overrides" not in meta:
        meta["manual_overrides"] = manual_overrides

    return changes, updated


# ── File I/O ──────────────────────────────────────────────────────────────────

def load_artist(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def save_artist(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def get_artist_paths(since: Optional[datetime] = None) -> list[Path]:
    paths = sorted(DATA_DIR.glob("ART-*.json"))
    if since:
        paths = [p for p in paths if datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc) >= since]
    return paths


# ── Main enrichment logic ──────────────────────────────────────────────────────

def enrich_artist(
    path: Path,
    airtable: Optional[AirtableSync],
    dry_run: bool,
    force: bool,
    now_iso: str,
    stats: dict,
) -> Optional[dict]:
    """Enrich a single artist. Returns per-artist report dict or None if skipped."""
    artist_data = load_artist(path)
    artbase_id  = artist_data.get("id") or path.stem

    skip_reason = should_skip(artist_data)
    if skip_reason:
        if "candidate" in skip_reason:
            stats["artists_skipped_candidate"] += 1
        return None

    qid = get_qid(artist_data)
    if not qid:
        return None

    entity = wdfetch.fetch_entity(qid)
    if not entity:
        stats["errors"] += 1
        print(f"  ⚠ {artbase_id}: QID {qid} not found on Wikidata", file=sys.stderr)
        return {"id": artbase_id, "warning": f"QID {qid} not found", "changes": []}

    if wdfetch.is_redirect(entity):
        stats["errors"] += 1
        print(f"  ⚠ {artbase_id}: QID {qid} is a redirect — flag for review", file=sys.stderr)
        return {"id": artbase_id, "warning": f"QID {qid} is a redirect", "changes": []}

    # Idempotency: skip if Wikidata revision unchanged
    revision_id      = wdfetch.get_revision_id(entity) or 0
    stored_revision  = artist_data.get("_meta", {}).get("wikidata_revision_id")
    if stored_revision == revision_id:
        stats["artists_skipped_unchanged"] += 1
        return None

    # Collect all QIDs that need label resolution
    qids_to_resolve = []
    for pid in ("P19", "P20"):
        q = wdparse.get_entity_id(entity, pid)
        if q:
            qids_to_resolve.append(q)
    for pid in ("P69", "P135", "P136"):
        qids_to_resolve.extend(wdparse.get_all_entity_ids(entity, pid))

    labels_map = wdlabels.resolve(qids_to_resolve) if qids_to_resolve else {}
    enriched   = extract_enrichment(entity, labels_map)

    manual_overrides = artist_data.get("_meta", {}).get("manual_overrides", [])
    changes, updated_data = apply_enrichment_to_json(
        artist_data, enriched, manual_overrides, force, revision_id, now_iso
    )

    # Count protected fields
    all_changes = compute_diff({}, enriched, [], False)
    protected_count = sum(1 for c in all_changes if c["field"] in manual_overrides and not force)
    stats["fields_protected_by_override"] += protected_count

    if not changes:
        stats["artists_skipped_unchanged"] += 1
        return None

    stats["artists_enriched"] += 1
    stats["fields_added"]     += sum(1 for c in changes if c["old"] is None)
    stats["fields_updated"]   += sum(1 for c in changes if c["old"] is not None)

    if dry_run:
        return {"id": artbase_id, "changes": changes}

    original_data = copy.deepcopy(artist_data)
    save_artist(path, updated_data)

    if airtable:
        try:
            record_id = airtable.find_record_id(artbase_id)
            if record_id:
                at_fields = airtable.build_fields(enriched, now_iso)
                airtable.update_enrichment(record_id, at_fields)
            else:
                print(f"  ⚠ {artbase_id}: no Airtable record found", file=sys.stderr)
        except Exception as e:
            save_artist(path, original_data)
            stats["errors"] += 1
            print(f"  ✗ {artbase_id}: Airtable failed, JSON rolled back — {e}", file=sys.stderr)
            return {"id": artbase_id, "error": str(e), "changes": []}

    return {"id": artbase_id, "changes": changes}


# ── Report writer ──────────────────────────────────────────────────────────────

def write_report(report: dict) -> Path:
    REPORTS_DIR.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path  = REPORTS_DIR / f"enrich_{stamp}.json"
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


# ── CLI ────────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Wikidata deep enrichment for Ars Accordia artists")
    group  = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--artist", metavar="ID",    help="Enrich a single artist by Ars Accordia ID")
    group.add_argument("--all",    action="store_true", help="Enrich all confirmed artists")
    parser.add_argument("--dry-run",       action="store_true", help="Show diffs, write nothing")
    parser.add_argument("--skip-airtable", action="store_true", help="Update JSON only, skip Airtable")
    parser.add_argument("--force",         action="store_true", help="Overwrite manual_overrides fields")
    parser.add_argument("--since",  metavar="DATE",  help="Only artists not enriched since DATE (YYYY-MM-DD)")
    args = parser.parse_args()

    now_iso   = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    run_start = time.time()

    airtable: Optional[AirtableSync] = None
    if not args.dry_run and not args.skip_airtable:
        airtable = AirtableSync(TOKEN, BASE_ID, TABLE_NAME)

    since_dt: Optional[datetime] = None
    if args.since:
        since_dt = datetime.fromisoformat(args.since).replace(tzinfo=timezone.utc)

    stats = {
        "artists_scanned":              0,
        "artists_skipped_candidate":    0,
        "artists_skipped_unchanged":    0,
        "artists_enriched":             0,
        "fields_added":                 0,
        "fields_updated":               0,
        "fields_protected_by_override": 0,
        "errors":                       0,
    }
    per_artist: list[dict] = []

    if args.artist:
        path = DATA_DIR / f"{args.artist}.json"
        if not path.exists():
            print(f"✗ File not found: {path}", file=sys.stderr)
            sys.exit(1)
        paths = [path]
    else:
        paths = get_artist_paths(since_dt)

    stats["artists_scanned"] = len(paths)
    print(f"Scanning {len(paths)} artist(s){'  [DRY RUN]' if args.dry_run else ''}...")

    for path in paths:
        artbase_id = path.stem
        try:
            result = enrich_artist(path, airtable, args.dry_run, args.force, now_iso, stats)
            if result and result.get("changes"):
                marker = "~" if args.dry_run else "✓"
                print(f"  {marker} {artbase_id}: {len(result['changes'])} change(s)")
                for c in result["changes"]:
                    print(f"      {c['field']}: {c['old']!r} → {c['new']!r}")
                per_artist.append(result)
            elif result and result.get("warning"):
                per_artist.append(result)
            elif result and result.get("error"):
                per_artist.append(result)
        except Exception as e:
            stats["errors"] += 1
            print(f"  ✗ {artbase_id}: {e}", file=sys.stderr)
            per_artist.append({"id": artbase_id, "error": str(e), "changes": []})

    elapsed = time.time() - run_start
    mins    = int(elapsed // 60)
    secs    = int(elapsed % 60)
    mode    = " (DRY RUN)" if args.dry_run else ""

    print(
        f"\nEnriched {stats['artists_enriched']} artists, "
        f"{stats['fields_added']} new fields, "
        f"{stats['fields_updated']} updated, "
        f"{stats['errors']} errors in {mins}m{secs}s{mode}"
    )

    report = {
        "run_started":   now_iso,
        "run_completed": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "dry_run":       args.dry_run,
        "stats":         stats,
        "per_artist":    per_artist,
    }

    report_path = write_report(report)
    print(f"Report: {report_path}")


if __name__ == "__main__":
    main()
