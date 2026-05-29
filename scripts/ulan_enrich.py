#!/usr/bin/env python3
"""
ulan_enrich.py — Getty ULAN enrichment for Ars Accordia artist records.

For each artist with a confirmed ULAN ID:
  - Query Getty's SPARQL endpoint for biographical data
  - Store in enrichment.ulan namespace (separate from Wikidata Tier 1 fields)
  - Track idempotency via _meta.ulan_last_enriched
  - Respect manual_overrides
  - Produce diff reports in reports/

Fields pulled:
  - biography_note
  - roles (more granular than Wikidata)
  - nationalities
  - birth_place_ulan, death_place_ulan
  - alternate_names
  - related_people

CLI:
    python3 scripts/ulan_enrich.py --artist ART-ANNUSS-1893
    python3 scripts/ulan_enrich.py --all
    python3 scripts/ulan_enrich.py --all --dry-run
    python3 scripts/ulan_enrich.py --all --force
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

from ulan_lib.sparql import fetch_ulan_person, parse_sparql_results

# ── Config ─────────────────────────────────────────────────────────────────────
REPO_ROOT   = Path(__file__).resolve().parent.parent
DATA_DIR    = REPO_ROOT / "artbase_export" / "data" / "artists"
REPORTS_DIR = REPO_ROOT / "reports"


# ── Skip rules ─────────────────────────────────────────────────────────────────

def should_skip(artist_data: dict) -> Optional[str]:
    """Return skip reason string, or None to proceed."""
    if artist_data.get("_meta", {}).get("do_not_enrich"):
        return "do_not_enrich flag"
    
    # Skip candidate matches
    wd = artist_data.get("authority_links", {}).get("wikidata", {})
    if wd.get("status") == "candidate_verify":
        return "candidate (needs verification)"
    
    # Check for ULAN ID
    ulan = (
        artist_data.get("authority_links", {}).get("ulan", {}).get("id")
        or artist_data.get("authorities", {}).get("ulan")
    )
    if not ulan:
        return "no ULAN ID"
    
    return None


def get_ulan_id(artist_data: dict) -> Optional[str]:
    ulan_link = artist_data.get("authority_links", {}).get("ulan", {})
    if isinstance(ulan_link, dict):
        return ulan_link.get("id")
    ulan_auth = artist_data.get("authorities", {}).get("ulan")
    return ulan_auth if isinstance(ulan_auth, str) else None


# ── Diff & apply ──────────────────────────────────────────────────────────────

def compute_diff(current: dict, new_values: dict, manual_overrides: list[str], force: bool) -> list[dict]:
    changes = []
    for field, new_val in new_values.items():
        if new_val is None or new_val == [] or new_val == {}:
            continue
        if field in manual_overrides and not force:
            continue
        old_val = current.get(field)
        if old_val != new_val:
            changes.append({"field": field, "old": old_val, "new": new_val})
    return changes


def apply_enrichment_to_json(
    artist_data: dict,
    enriched: dict,
    manual_overrides: list[str],
    force: bool,
    now_iso: str,
) -> tuple[list[dict], dict]:
    """Apply ULAN enrichment to artist_data. Returns (changes_list, updated_data)."""
    updated = copy.deepcopy(artist_data)
    
    # All ULAN data goes under enrichment.ulan
    if "enrichment" not in updated:
        updated["enrichment"] = {}
    if "ulan" not in updated["enrichment"]:
        updated["enrichment"]["ulan"] = {}
    
    current_ulan = updated["enrichment"]["ulan"]
    changes = compute_diff(current_ulan, enriched, manual_overrides, force)
    
    if not changes:
        return [], updated
    
    # Apply changes
    for change in changes:
        field = change["field"]
        val   = change["new"]
        updated["enrichment"]["ulan"][field] = val
    
    # Update _meta
    meta = updated.setdefault("_meta", {})
    meta["ulan_last_enriched"] = now_iso
    meta.setdefault("manual_overrides", manual_overrides)
    
    return changes, updated


# ── File I/O ──────────────────────────────────────────────────────────────────

def load_artist(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def save_artist(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def get_artist_paths() -> list[Path]:
    return sorted(DATA_DIR.glob("ART-*.json"))


# ── Main enrichment logic ──────────────────────────────────────────────────────

def enrich_artist(
    path: Path,
    dry_run: bool,
    force: bool,
    now_iso: str,
    stats: dict,
) -> Optional[dict]:
    """Enrich a single artist with ULAN data. Returns per-artist report dict or None."""
    artist_data = load_artist(path)
    artbase_id  = artist_data.get("id") or path.stem
    
    skip_reason = should_skip(artist_data)
    if skip_reason:
        if "candidate" in skip_reason:
            stats["artists_skipped_candidate"] += 1
        elif "no ULAN" in skip_reason:
            stats["artists_skipped_no_ulan"] += 1
        return None
    
    ulan_id = get_ulan_id(artist_data)
    if not ulan_id:
        return None
    
    # Fetch ULAN data
    sparql_result = fetch_ulan_person(ulan_id)
    if not sparql_result:
        stats["errors"] += 1
        print(f"  ⚠ {artbase_id}: SPARQL query failed for ULAN {ulan_id}", file=sys.stderr)
        return {"id": artbase_id, "warning": f"SPARQL query failed", "changes": []}
    
    enriched = parse_sparql_results(sparql_result)
    if not enriched:
        stats["artists_skipped_no_data"] = stats.get("artists_skipped_no_data", 0) + 1
        return None
    
    manual_overrides = artist_data.get("_meta", {}).get("manual_overrides", [])
    changes, updated_data = apply_enrichment_to_json(
        artist_data, enriched, manual_overrides, force, now_iso
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
    
    # Write JSON
    save_artist(path, updated_data)
    return {"id": artbase_id, "changes": changes}


# ── Report writer ──────────────────────────────────────────────────────────────

def write_report(report: dict) -> Path:
    REPORTS_DIR.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path  = REPORTS_DIR / f"ulan_enrich_{stamp}.json"
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


# ── CLI ────────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Getty ULAN enrichment for Ars Accordia artists")
    group  = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--artist", metavar="ID",    help="Enrich a single artist by Ars Accordia ID")
    group.add_argument("--all",    action="store_true", help="Enrich all artists with ULAN IDs")
    parser.add_argument("--dry-run", action="store_true", help="Show diffs, write nothing")
    parser.add_argument("--force",   action="store_true", help="Overwrite manual_overrides fields")
    args = parser.parse_args()
    
    now_iso   = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    run_start = time.time()
    
    stats = {
        "artists_scanned":              0,
        "artists_skipped_candidate":    0,
        "artists_skipped_no_ulan":      0,
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
        paths = get_artist_paths()
    
    stats["artists_scanned"] = len(paths)
    print(f"Scanning {len(paths)} artist(s){'  [DRY RUN]' if args.dry_run else ''}...")
    
    for path in paths:
        artbase_id = path.stem
        try:
            result = enrich_artist(path, args.dry_run, args.force, now_iso, stats)
            if result and result.get("changes"):
                marker = "~" if args.dry_run else "✓"
                print(f"  {marker} {artbase_id}: {len(result['changes'])} change(s)")
                for c in result["changes"]:
                    old_preview = str(c['old'])[:60] if c['old'] else None
                    new_preview = str(c['new'])[:60] if c['new'] else None
                    print(f"      {c['field']}: {old_preview!r} → {new_preview!r}")
                per_artist.append(result)
            elif result and result.get("warning"):
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
