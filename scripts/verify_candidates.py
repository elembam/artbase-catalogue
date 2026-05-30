#!/usr/bin/env python3
"""
verify_candidates.py — (Re)compute validation levels for artist canonical records.

Reads each canonical JSON, rebuilds the source ledger validation block, and writes
the result back.  The authoritative `source_ledger` is always derived from
attestations[] and authority_links — this script just makes it explicit.

Usage:
    python3 scripts/verify_candidates.py             # process all
    python3 scripts/verify_candidates.py --record ART-AIDE-1913
    python3 scripts/verify_candidates.py --print ART-AIDE-1913   # show validation block only
    python3 scripts/verify_candidates.py --summary               # print level distribution
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT   = Path(__file__).resolve().parent.parent
ARTISTS_DIR = REPO_ROOT / "artbase_export" / "data" / "artists"

# Import build_source_ledger helpers via sys.path
sys.path.insert(0, str(Path(__file__).parent))
import importlib
_bsl = importlib.import_module("build_source_ledger")
compute_ledger   = _bsl.build_ledger
load_source_registry = _bsl.load_source_registry


def process_one(artist_id: str, source_registry: dict, dry_run: bool = False) -> dict | None:
    path = ARTISTS_DIR / f"{artist_id}.json"
    if not path.exists():
        print(f"  NOT FOUND: {path}", file=sys.stderr)
        return None

    artist = json.loads(path.read_text())
    ledger  = compute_ledger(artist, source_registry)
    validation = ledger["validation"]

    if not dry_run:
        artist["source_ledger"] = ledger
        path.write_text(json.dumps(artist, indent=2, ensure_ascii=False) + "\n")

    return validation


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--record", metavar="ART-ID",
                    help="Process a single artist record")
    ap.add_argument("--print", dest="print_id", metavar="ART-ID",
                    help="Print the validation block for one record and exit")
    ap.add_argument("--summary", action="store_true",
                    help="Print level-distribution summary")
    ap.add_argument("--dry-run", action="store_true",
                    help="Show what would change without writing")
    args = ap.parse_args()

    source_registry = load_source_registry()

    # ── --print mode ─────────────────────────────────────────────────────────
    if args.print_id:
        v = process_one(args.print_id, source_registry, dry_run=True)
        if v:
            print(json.dumps(v, indent=2))
        sys.exit(0)

    # ── Determine which records to process ───────────────────────────────────
    if args.record:
        ids = [args.record]
    else:
        ids = sorted(p.stem for p in ARTISTS_DIR.glob("ART-*.json"))

    level_counts: Counter = Counter()
    changed = 0

    for aid in ids:
        path = ARTISTS_DIR / f"{aid}.json"
        if not path.exists():
            print(f"  SKIP (not found): {aid}")
            continue

        artist = json.loads(path.read_text())
        ledger  = compute_ledger(artist, source_registry)
        new_val = ledger["validation"]
        old_val = artist.get("source_ledger", {}).get("validation", {})

        badge    = new_val.get("conformance_badge", "none")
        l1_level = new_val.get("level1", {}).get("level", "PENDING")
        level_counts[l1_level] += 1

        if new_val != old_val:
            changed += 1
            if args.dry_run:
                old_l1 = old_val.get("level1", {}).get("level", "—")
                print(f"  WOULD UPDATE {aid}: {old_l1} → {l1_level} [{badge}]")
            else:
                artist["source_ledger"] = ledger
                path.write_text(json.dumps(artist, indent=2, ensure_ascii=False) + "\n")

    action = "Would update" if args.dry_run else "Updated"
    print(f"\n{action} {changed}/{len(ids)} records.")

    if args.summary or not args.record:
        print("\nLevel 1 distribution:")
        for level, count in sorted(level_counts.items()):
            print(f"  {level:<30} {count:>4}")


if __name__ == "__main__":
    main()
