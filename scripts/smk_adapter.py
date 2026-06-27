#!/usr/bin/env python3
"""
smk_adapter.py — SMK Open API → ArtBase passport CLI

Usage:
    python3 scripts/smk_adapter.py KMS4185 --draft       # fetch & emit draft passport JSON
    python3 scripts/smk_adapter.py KMS4185 --report      # import report: imported / gaps / reconciliation
    python3 scripts/smk_adapter.py --search "Hunæus"     # search SMK by keyword
    python3 scripts/smk_adapter.py KMS4185 --wikidata    # prepare reviewed SMK↔Wikidata task

The --draft flag writes to:
    artbase_export/data/artworks/AA/DK/SMK/<object_number>.json

The --wikidata flag writes a reviewed QuickStatements file to:
    artbase_export/data/contributions/smk_wd_<object_number>_<date>.qs
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# ── Path setup ────────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "artbase_export" / "src"))

from artbase_export.adapters.smk import SMKAdapter

ARTWORKS_DIR      = REPO_ROOT / "artbase_export" / "data" / "artworks"
CONTRIBUTIONS_DIR = REPO_ROOT / "artbase_export" / "data" / "contributions"


# ── CLI ───────────────────────────────────────────────────────────────────────

def cmd_draft(adapter: SMKAdapter, object_number: str, stdout: bool = False):
    print(f"Fetching {object_number} from SMK Open API…", file=sys.stderr)
    raw    = adapter.fetch_object_by_id(object_number)
    record = adapter.normalize_to_object_record(raw)

    out_path = ARTWORKS_DIR / "AA" / "DK" / "SMK" / f"{object_number}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    content = json.dumps(record, indent=2, ensure_ascii=False)
    if stdout:
        print(content)
    else:
        out_path.write_text(content)
        print(f"Draft written: {out_path.relative_to(REPO_ROOT)}")
        print(f"Rights:        {record['rights']['copyright_status']}")
        print(f"Media records: {len(record['media'])}")
        print(f"Provenance steps: {len(record['provenance'])}")
        print(f"\nNext step: review draft, then run --report and --wikidata")


def cmd_report(adapter: SMKAdapter, object_number: str):
    print(f"Fetching {object_number} from SMK Open API…", file=sys.stderr)
    raw    = adapter.fetch_object_by_id(object_number)
    report = adapter.produce_import_report(raw)
    print(report)


def cmd_search(adapter: SMKAdapter, query: str):
    print(f"Searching SMK for '{query}'…", file=sys.stderr)
    results = adapter.search_objects(query)
    if not results:
        print("No results.")
        return
    print(f"{len(results)} result(s):\n")
    for item in results:
        obj_num    = item.get("object_number", "?")
        titles     = item.get("titles") or []
        title      = titles[0]["title"] if titles else "—"
        production = item.get("production") or []
        creator    = production[0].get("creator", "—") if production else "—"
        prod_dates = item.get("production_date") or []
        period     = prod_dates[0].get("period", "—") if prod_dates else "—"
        pd         = "PD" if item.get("public_domain") else "©"
        print(f"  {obj_num:<12} [{pd}]  {creator}  ·  {title}  ·  {period}")


def cmd_wikidata(adapter: SMKAdapter, object_number: str):
    print(f"Fetching {object_number} from SMK Open API…", file=sys.stderr)
    raw = adapter.fetch_object_by_id(object_number)

    print("Searching Wikidata for existing artwork item…", file=sys.stderr)
    artwork_qid = adapter.find_wikidata_item(object_number)
    if artwork_qid:
        print(f"Found Wikidata item: {artwork_qid}", file=sys.stderr)
    else:
        print("No existing Wikidata item found — generating CREATE stub.", file=sys.stderr)

    qs_content = adapter.produce_wikidata_task(raw, artwork_qid=artwork_qid)

    from datetime import date
    today     = date.today().isoformat().replace("-", "")
    qs_fname  = f"smk_wd_{object_number}_{today}.qs"
    qs_path   = CONTRIBUTIONS_DIR / qs_fname

    qs_path.write_text(qs_content)
    print(f"Reviewed QS task written: {qs_path.relative_to(REPO_ROOT)}")
    print("\n--- QuickStatements preview ---")
    print(qs_content)
    print("--- Review carefully before submitting to QuickStatements ---")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="SMK Open API → ArtBase passport adapter",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("object_number", nargs="?",
                        help="SMK inventory number (e.g. KMS4185)")
    parser.add_argument("--draft",    action="store_true",
                        help="Fetch and write a draft passport JSON")
    parser.add_argument("--report",   action="store_true",
                        help="Print import report: imported / gaps / reconciliation")
    parser.add_argument("--search",   metavar="QUERY",
                        help="Search SMK by keyword")
    parser.add_argument("--wikidata", action="store_true",
                        help="Prepare a reviewed SMK↔Wikidata QuickStatements task")
    parser.add_argument("--stdout",   action="store_true",
                        help="Print draft JSON to stdout instead of writing file")
    args = parser.parse_args()

    adapter = SMKAdapter()

    if args.search:
        cmd_search(adapter, args.search)
        return

    if not args.object_number:
        parser.print_help()
        sys.exit(1)

    obj = args.object_number.strip().upper()

    try:
        if args.draft:
            cmd_draft(adapter, obj, stdout=args.stdout)
        elif args.report:
            cmd_report(adapter, obj)
        elif args.wikidata:
            cmd_wikidata(adapter, obj)
        else:
            parser.print_help()
            sys.exit(1)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
