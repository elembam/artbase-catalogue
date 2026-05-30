#!/usr/bin/env python3
"""
migrate_validation.py — One-time migration: old confirmed/candidate → four-grade validation level.

Mapping (Part G of spec-10):
  confirmed + citable authority        → FULLY_CORROBORATED or PARTIALLY_CORROBORATED
      (computed by the real ledger logic, not hardcoded)
  candidate + citable authority        → PARTIALLY_CORROBORATED
  candidate + origin-only              → ENTITY_SUPPLIED_ONLY
  unverified / confirmed_no_basis      → ENTITY_SUPPLIED_ONLY
  missing status                       → PENDING

The script reads the current source_ledger.verification block and derives the correct
new level, then writes it into source_ledger.validation and sets legacy_status from
the old value.

Usage:
    python3 scripts/migrate_validation.py           # dry-run by default
    python3 scripts/migrate_validation.py --apply   # write changes
    python3 scripts/migrate_validation.py --report  # full mapping table on stdout
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT   = Path(__file__).resolve().parent.parent
ARTISTS_DIR = REPO_ROOT / "artbase_export" / "data" / "artists"

sys.path.insert(0, str(Path(__file__).parent))
import importlib
_bsl = importlib.import_module("build_source_ledger")
compute_ledger       = _bsl.build_ledger
load_source_registry = _bsl.load_source_registry


def _old_to_new(old_status: str, ledger: dict) -> tuple[str, str]:
    """
    Return (new_level, note) based on old verification status and new ledger data.
    We trust the computed ledger level as ground truth; old_status provides context
    for ambiguous cases.
    """
    new_level = ledger["validation"]["level1"]["level"]
    badge     = ledger["validation"]["conformance_badge"]

    if old_status == "confirmed" and new_level == "FULLY_CORROBORATED":
        note = "clean migration"
    elif old_status == "confirmed" and new_level == "PARTIALLY_CORROBORATED":
        note = "was confirmed but not all L1 fields corroborated"
    elif old_status == "confirmed" and new_level == "ENTITY_SUPPLIED_ONLY":
        note = "AMBIGUOUS — was confirmed but no citable authority found; investigate"
    elif old_status == "confirmed_no_basis":
        note = "was flagged confirmed_no_basis in spec-09; correctly demoted"
    elif old_status == "candidate":
        note = "candidate → computed level"
    else:
        note = f"old={old_status or 'missing'}"

    return new_level, note


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply",  action="store_true",
                    help="Write the migration to disk (default: dry-run only)")
    ap.add_argument("--report", action="store_true",
                    help="Print full mapping table (one row per artist)")
    args = ap.parse_args()

    source_registry = load_source_registry()
    ids = sorted(p.stem for p in ARTISTS_DIR.glob("ART-*.json"))

    rows = []
    ambiguous = []

    for aid in ids:
        path = ARTISTS_DIR / f"{aid}.json"
        artist = json.loads(path.read_text())

        old_ledger   = artist.get("source_ledger", {})
        old_verif    = old_ledger.get("verification", {})
        old_status   = old_verif.get("status", "")

        # Compute the fresh ledger (including new validation block)
        new_ledger = compute_ledger(artist, source_registry)
        new_level, note = _old_to_new(old_status, new_ledger)

        badge = new_ledger["validation"]["conformance_badge"]

        if "AMBIGUOUS" in note:
            ambiguous.append(aid)

        rows.append({
            "id":         aid,
            "old_status": old_status or "(none)",
            "new_level":  new_level,
            "badge":      badge,
            "note":       note,
        })

        if args.apply:
            # Preserve legacy_status, then apply new ledger
            artist["source_ledger"] = new_ledger
            artist["source_ledger"]["legacy_status"] = old_status or ""
            path.write_text(json.dumps(artist, indent=2, ensure_ascii=False) + "\n")

    # ── Report ────────────────────────────────────────────────────────────────
    if args.report:
        print(f"{'ID':<35} {'OLD':<22} {'NEW LEVEL':<30} {'BADGE':<8} NOTE")
        print("-" * 115)
        for r in rows:
            flag = " ⚠" if "AMBIGUOUS" in r["note"] else ""
            print(f"{r['id']:<35} {r['old_status']:<22} {r['new_level']:<30} {r['badge']:<8} {r['note']}{flag}")

    # ── Summary ───────────────────────────────────────────────────────────────
    from collections import Counter
    lvl_counts = Counter(r["new_level"] for r in rows)
    badge_counts = Counter(r["badge"] for r in rows)

    action = "Applied" if args.apply else "Would apply (dry-run, use --apply to write)"
    print(f"\n{action} migration for {len(rows)} records.")
    print("\nNew Level 1 distribution:")
    for k, v in sorted(lvl_counts.items()):
        print(f"  {k:<30} {v:>4}")
    print("\nConformance badge distribution:")
    for k, v in sorted(badge_counts.items()):
        print(f"  {k:<10} {v:>4}")

    if ambiguous:
        print(f"\n⚠  {len(ambiguous)} AMBIGUOUS cases (were 'confirmed' but no citable authority):")
        for aid in ambiguous:
            print(f"  {aid}")
        print("  → Investigate these records. They were confirmed_no_basis in spec-09 already.")


if __name__ == "__main__":
    main()
