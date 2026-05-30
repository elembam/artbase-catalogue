#!/usr/bin/env python3
"""
gdpr.py — GDPR data-subject request handler for ArtBase.

Handles erasure (Art. 17) and access requests from data subjects.

Design principles (not legal advice — consult a qualified data-protection
professional before deploying):

  1. The OBJECT RECORD and its permanent ID persist.
     An artwork is not personal data; the ID can survive as a tombstone.

  2. PERSONAL FIELDS are redactable without destroying the object record.
     Separation: personal fields (erasable) vs. object/identity fields (permanent).

  3. Data published to Wikidata cannot be unilaterally retracted.
     This script only redacts from ArtBase canonical JSON / source registry.

  4. Every redaction is logged to data/gdpr_requests.json with the action taken.

  5. GDPR coverage:
     - Contributor personal data (private_collector): contact_email, display_name
     - Living artist biographical data: birth_date/place, death_date/place if living
     - Owner identity in provenance records: owner_identity field

Redactable personal fields per entity type:
  Artist (living_person=true):
    identity.preferred_name, identity.full_name, identity.sort_name,
    identity.name_variants, life.birth_date, life.death_date,
    life.birth_place, life.death_place, description_en, description_lv, image

  Contributor (private_collector/gdpr_sensitive):
    name (→ "[Redacted]"), _meta.contact_email (→ null)

  Provenance entry (named living owner):
    owner field within provenance[] entry

CLI:
    python3 scripts/gdpr.py --list-requests
    python3 scripts/gdpr.py --redact ART-0001 --request REQ-001
    python3 scripts/gdpr.py --redact CON-USER-00001 --request REQ-002
    python3 scripts/gdpr.py --redact ART-0001 --request REQ-001 --dry-run
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT   = Path(__file__).resolve().parent.parent
DATA_DIR    = REPO_ROOT / "artbase_export" / "data"
ARTISTS_DIR = DATA_DIR / "artists"
ARTWORKS_DIR = DATA_DIR / "artworks"
SOURCES_DIR = DATA_DIR / "sources"
REQUESTS_LOG = DATA_DIR / "gdpr_requests.json"

# Fields to redact for living-person artist records
ARTIST_PERSONAL_FIELDS = [
    "identity.preferred_name",
    "identity.full_name",
    "identity.sort_name",
    "identity.name_variants",
    "life.birth_date",
    "life.death_date",
    "life.birth_place",
    "life.death_place",
    "description_en",
    "description_lv",
    "image",
]

REDACTED_SENTINEL = "[Redacted under GDPR Art.17]"


# ── Request log ─────────────────────────────────────────────────────────────────

def load_requests() -> list[dict]:
    if REQUESTS_LOG.exists():
        return json.loads(REQUESTS_LOG.read_text(encoding="utf-8"))
    return []


def save_requests(requests: list[dict]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    REQUESTS_LOG.write_text(
        json.dumps(requests, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def log_request(request_id: str, entity_id: str, fields_redacted: list[str],
                dry_run: bool) -> None:
    """Append a redaction record to gdpr_requests.json."""
    if dry_run:
        return
    requests = load_requests()
    requests.append({
        "request_id":      request_id,
        "entity_id":       entity_id,
        "action":          "redact",
        "fields_redacted": fields_redacted,
        "timestamp":       datetime.now(timezone.utc).isoformat(),
        "note":            "Personal fields nulled. Object record and permanent ID preserved.",
    })
    save_requests(requests)


# ── Deep setter for nested paths ────────────────────────────────────────────────

def _nested_set(d: dict, dotpath: str, value) -> bool:
    """
    Set d[key1][key2]... to value. Returns True if the key existed and was non-null.
    """
    parts = dotpath.split(".")
    cur = d
    for part in parts[:-1]:
        if part not in cur or not isinstance(cur[part], dict):
            return False
        cur = cur[part]
    leaf = parts[-1]
    if leaf in cur and cur[leaf] is not None and cur[leaf] != "" and cur[leaf] != []:
        cur[leaf] = value
        return True
    return False


# ── Artist redaction ─────────────────────────────────────────────────────────────

def redact_artist(entity_id: str, request_id: str, dry_run: bool) -> None:
    artist_file = ARTISTS_DIR / f"{entity_id}.json"
    if not artist_file.exists():
        print(f"✗ Artist file not found: {entity_id}.json")
        sys.exit(1)

    record = json.loads(artist_file.read_text(encoding="utf-8"))

    # Only redact living persons
    if not record.get("living_person"):
        print(f"⚠ {entity_id}: living_person is not set. Only living person records are redactable.")
        print("  Set living_person=true in the JSON first if this request is valid.")
        sys.exit(1)

    redacted_fields = []
    for dotpath in ARTIST_PERSONAL_FIELDS:
        if _nested_set(record, dotpath, REDACTED_SENTINEL):
            redacted_fields.append(dotpath)
            if dry_run:
                print(f"  ~ Would redact: {dotpath}")
            else:
                print(f"  ✓ Redacted: {dotpath}")

    # Add gdpr redaction tombstone
    if not dry_run:
        record.setdefault("_meta", {})["gdpr_redacted"] = {
            "request_id": request_id,
            "redacted_at": datetime.now(timezone.utc).isoformat(),
            "fields": redacted_fields,
        }
        artist_file.write_text(
            json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        log_request(request_id, entity_id, redacted_fields, dry_run=False)
        print(f"\n✓ {entity_id}: {len(redacted_fields)} personal field(s) redacted.")
        print(f"  Object record and permanent ID preserved.")
    else:
        print(f"\n~ {entity_id}: would redact {len(redacted_fields)} field(s) (dry run)")


# ── Contributor redaction ────────────────────────────────────────────────────────

def redact_contributor(cid: str, request_id: str, dry_run: bool) -> None:
    registry_file = None
    src = None
    for p in SOURCES_DIR.glob("*.json"):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
            if d.get("contributor_id") == cid:
                registry_file = p
                src = d
                break
        except (KeyError, json.JSONDecodeError):
            pass

    if not src:
        print(f"✗ Contributor {cid} not found in source registry.")
        sys.exit(1)

    if not src.get("gdpr_sensitive"):
        print(f"⚠ {cid}: gdpr_sensitive is not set. Redaction applies only to GDPR-sensitive contributors.")
        sys.exit(1)

    redacted_fields = []

    # Redact display name
    if src.get("name") and src["name"] != REDACTED_SENTINEL:
        if dry_run:
            print(f"  ~ Would redact: name ({src['name']!r})")
        else:
            src["name"] = REDACTED_SENTINEL
        redacted_fields.append("name")

    # Redact contact email
    meta = src.get("_meta", {})
    if meta.get("contact_email"):
        if dry_run:
            print(f"  ~ Would redact: _meta.contact_email")
        else:
            meta["contact_email"] = None
        redacted_fields.append("_meta.contact_email")

    if not dry_run:
        src.setdefault("_meta", {})["gdpr_redacted"] = {
            "request_id": request_id,
            "redacted_at": datetime.now(timezone.utc).isoformat(),
            "fields": redacted_fields,
        }
        registry_file.write_text(
            json.dumps(src, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        log_request(request_id, cid, redacted_fields, dry_run=False)
        print(f"✓ {cid}: {len(redacted_fields)} field(s) redacted.")
        print(f"  Contributor ID and source registry entry preserved as tombstone.")
    else:
        print(f"~ {cid}: would redact {len(redacted_fields)} field(s) (dry run)")


# ── Dispatch ─────────────────────────────────────────────────────────────────────

def redact(entity_id: str, request_id: str, dry_run: bool) -> None:
    if entity_id.startswith("ART-"):
        redact_artist(entity_id, request_id, dry_run)
    elif entity_id.startswith("CON-"):
        redact_contributor(entity_id, request_id, dry_run)
    elif entity_id.startswith("AP-"):
        print(f"✗ Artwork records: redact owner identity via --redact <AP-ID> (not yet implemented).")
        print("  Redact the artwork's provenance owner field manually for now.")
        sys.exit(1)
    else:
        print(f"✗ Unknown entity type for ID: {entity_id}")
        sys.exit(1)


def list_requests() -> None:
    requests = load_requests()
    if not requests:
        print("No GDPR requests logged.")
        return

    print(f"{'Request ID':<15} {'Entity':<25} {'Fields Redacted':>15}  Timestamp")
    print("-" * 80)
    for r in requests:
        n = len(r.get("fields_redacted", []))
        print(f"{r['request_id']:<15} {r['entity_id']:<25} {n:>15}  {r['timestamp'][:19]}")


def main() -> None:
    parser = argparse.ArgumentParser(description="GDPR data-subject request handler")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--redact", metavar="ENTITY-ID",
                       help="Redact personal fields for a living person (ART-*, CON-*)")
    group.add_argument("--list-requests", action="store_true",
                       help="List all GDPR requests logged")

    parser.add_argument("--request", metavar="REQ-ID",
                        help="Request ID (required with --redact)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be redacted without writing")

    args = parser.parse_args()

    if args.list_requests:
        list_requests()

    elif args.redact:
        if not args.request:
            print("✗ --redact requires --request REQ-ID")
            sys.exit(1)
        redact(args.redact, args.request, args.dry_run)


if __name__ == "__main__":
    main()
