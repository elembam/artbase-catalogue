#!/usr/bin/env python3
"""
record_book_qid.py — update a source registry JSON with a newly created Wikidata QID.

Usage:
  python3 scripts/record_book_qid.py SRC-HANSABANKA-2007 Q123456
  python3 scripts/record_book_qid.py SRC-LNMM-PORTRAITS-2009 Q789012 --lndb-id "LV-0045678"

The script:
  1. Finds artbase_export/data/sources/<SOURCE_ID>.json
  2. Sets wikidata_qid and wikidata_status = "created"
  3. Optionally sets lndb_id
  4. Writes the file back in-place
"""

import argparse
import json
import re
import sys
from pathlib import Path

SOURCES_DIR = Path(__file__).parent.parent / "artbase_export" / "data" / "sources"


def _validate_qid(qid: str) -> str:
    if not re.fullmatch(r"Q\d+", qid):
        raise SystemExit(f"ERROR: '{qid}' is not a valid Wikidata QID (expected Q followed by digits)")
    return qid


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Record a Wikidata QID into a source registry JSON file"
    )
    parser.add_argument("source_id", metavar="SOURCE-ID",
                        help="Source file basename without .json, e.g. SRC-HANSABANKA-2007")
    parser.add_argument("qid", metavar="QID",
                        help="Wikidata QID to record, e.g. Q12345678")
    parser.add_argument("--lndb-id", metavar="LNB-ID",
                        help="Optional: Latvian National Library catalogue ID (lndb_id)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print what would be changed without writing")
    args = parser.parse_args()

    qid = _validate_qid(args.qid)
    path = SOURCES_DIR / f"{args.source_id}.json"

    if not path.exists():
        raise SystemExit(f"ERROR: source file not found: {path}")

    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)

    if data.get("wikidata_qid"):
        print(f"WARNING: {args.source_id} already has wikidata_qid = {data['wikidata_qid']}")
        if not args.dry_run:
            confirm = input("Overwrite? (yes/no): ").strip().lower()
            if confirm != "yes":
                raise SystemExit("Aborted.")

    data["wikidata_qid"] = qid
    data["wikidata_status"] = "created"

    if args.lndb_id:
        data["lndb_id"] = args.lndb_id

    if args.dry_run:
        print("DRY RUN — would write:")
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    with path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    print(f"✓ {args.source_id} → {qid}")
    if args.lndb_id:
        print(f"  lndb_id  → {args.lndb_id}")
    print(f"  File: {path}")


if __name__ == "__main__":
    main()
