#!/usr/bin/env python3
"""
contributors.py — Manage ArtBase contributors.

Replaces the --new-user flag in airtable_sync_contributors.py and adds
--set-verification for updating a contributor's verification level.

Trust model — verification_level is orthogonal to trust flags:
  Raising a contributor's verification_level NEVER changes
  wikidata_citable or can_confirm. It only governs the scrutiny
  level applied during submission review.

CLI:
    python3 scripts/contributors.py --create-user \\
        --name "Jane Doe" --email "jane@example.com"
    python3 scripts/contributors.py --create-user \\
        --name "Jane Doe" --email "jane@example.com" --dry-run

    python3 scripts/contributors.py --set-verification CON-USER-00001 email_verified
    python3 scripts/contributors.py --set-verification CON-USER-00001 identity_verified --dry-run

    python3 scripts/contributors.py --list
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

REPO_ROOT   = Path(__file__).resolve().parent.parent
ARTBASE_PKG = REPO_ROOT / "artbase_export" / "src"
sys.path.insert(0, str(ARTBASE_PKG))

from artbase_export.config import Config
from artbase_export.airtable.schema import (
    Tables, ContributorFields as CF,
    VerificationLevel,
)

DATA_DIR    = REPO_ROOT / "artbase_export" / "data"
SOURCES_DIR = DATA_DIR / "sources"

VERIFICATION_LEVELS = {
    "unverified":         VerificationLevel.UNVERIFIED,
    "email_verified":     VerificationLevel.EMAIL_VERIFIED,
    "identity_verified":  VerificationLevel.IDENTITY_VERIFIED,
    "known_institution":  VerificationLevel.KNOWN_INSTITUTION,
}

# Trust defaults per contributor type — FIXED, never changed by verification_level
TRUST_DEFAULTS = {
    "authority_file":     {"wikidata_citable": True,  "can_confirm": True},
    "institutional":      {"wikidata_citable": True,  "can_confirm": True},
    "platform_staff":     {"wikidata_citable": False, "can_confirm": True},
    "commercial_gallery": {"wikidata_citable": False, "can_confirm": False},
    "private_collector":  {"wikidata_citable": False, "can_confirm": False},
    "data_partner":       {"wikidata_citable": False, "can_confirm": False},
}


def get_api(config: Config):
    try:
        from pyairtable import Api
        return Api(config.airtable.token)
    except ImportError:
        print("✗ pyairtable not installed: pip install pyairtable")
        sys.exit(1)


def next_user_id() -> tuple[str, str]:
    """Return (CON-USER-NNNNN, SRC-USER-NNNNN) for the next private user."""
    existing = [p.stem for p in SOURCES_DIR.glob("SRC-USER-*.json")]
    n = len(existing) + 1
    return f"CON-USER-{n:05d}", f"SRC-USER-{n:05d}"


def create_user(name: str, email: str, config: Config, dry_run: bool) -> None:
    """
    Register a new private collector.

    Creates:
      1. data/sources/SRC-USER-NNNNN.json  (contact email stays here only)
      2. Airtable Contributors row
    """
    cid, sid = next_user_id()
    today = date.today().isoformat()

    src = {
        "source_id":         sid,
        "contributor_id":    cid,
        "name":              name,
        "source_type":       "private_collector",
        "contributor_type":  "private_collector",
        "verification_level": "unverified",
        "wikidata_citable":  False,
        "can_confirm":       False,
        "gdpr_sensitive":    True,
        "role_in_catalogue": (
            "Private collector — data origin only. "
            "Facts require independent authority confirmation before publication."
        ),
        "_meta": {
            "registered_at":  today,
            "contact_email":  email,   # NEVER exported to HTML/JSON/public
            "terms_note": (
                "Data submitted by collector. Personal data handled under "
                "GDPR Art.6(1)(b). Do not publish contact details."
            ),
        },
    }

    registry_path = SOURCES_DIR / f"{sid}.json"
    if not dry_run:
        registry_path.write_text(
            json.dumps(src, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"  ✓ Created source registry: {registry_path.relative_to(REPO_ROOT)}")
    else:
        print(f"  ~ Would create: {registry_path.relative_to(REPO_ROOT)}")

    api = get_api(config)
    table = api.table(config.airtable.base_id, Tables.CONTRIBUTORS)

    fields = {
        CF.ID:                 cid,
        CF.DISPLAY_NAME:       name,
        CF.CONTRIBUTOR_TYPE:   "Private Collector",
        CF.VERIFICATION_LEVEL: "unverified",
        CF.WIKIDATA_CITABLE:   False,
        CF.CAN_CONFIRM:        False,
        CF.GDPR_SENSITIVE:     True,
        CF.LIVING_PERSON:      True,
        CF.GDPR_ROLE:          "data_subject",
        CF.REGISTERED_AT:      today,
        CF.TERMS_NOTE:         src["_meta"]["terms_note"],
    }

    if dry_run:
        print(f"  ~ Would create Airtable row: {cid}")
    else:
        table.create(fields)
        print(f"  ✓ Created Airtable row: {cid}")

    print(f"\n  Contributor ID : {cid}")
    print(f"  Source ID      : {sid}")
    print(f"  ⚠  Contact email stored only in source registry — never exported.")


def set_verification(cid: str, level: str, config: Config, dry_run: bool) -> None:
    """
    Update a contributor's verification_level.

    This NEVER touches wikidata_citable or can_confirm — those are determined
    by contributor_type alone and are immutable through verification.
    """
    if level not in VERIFICATION_LEVELS:
        print(f"✗ Unknown level '{level}'. Valid: {', '.join(VERIFICATION_LEVELS)}")
        sys.exit(1)

    # Update source registry JSON
    matches = list(SOURCES_DIR.glob("*.json"))
    registry_file = None
    src = None
    for p in matches:
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

    old_level = src.get("verification_level", "unverified")
    src["verification_level"] = level

    if dry_run:
        print(f"  ~ Would update {registry_file.name}: {old_level} → {level}")
    else:
        registry_file.write_text(
            json.dumps(src, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"  ✓ Updated {registry_file.name}: {old_level} → {level}")

    # Update Airtable
    api = get_api(config)
    table = api.table(config.airtable.base_id, Tables.CONTRIBUTORS)
    rows = table.all(formula=f'{{{CF.ID}}} = "{cid}"')
    if not rows:
        print(f"  ⚠ {cid} not found in Airtable — run airtable_sync_contributors.py first")
        return

    if dry_run:
        print(f"  ~ Would update Airtable {cid}: Verification Level → {level}")
    else:
        table.update(rows[0]["id"], {CF.VERIFICATION_LEVEL: level})
        print(f"  ✓ Airtable {cid}: Verification Level → {level}")

    # Confirm trust flags unchanged
    trust = TRUST_DEFAULTS.get(src.get("contributor_type", ""), {})
    print(f"  ℹ Trust flags unchanged: wikidata_citable={trust.get('wikidata_citable')}, "
          f"can_confirm={trust.get('can_confirm')}")


def list_contributors() -> None:
    """Print a table of all contributors in the source registry."""
    rows = []
    for p in sorted(SOURCES_DIR.glob("*.json")):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
            if "contributor_id" not in d:
                continue
            rows.append(d)
        except (KeyError, json.JSONDecodeError):
            pass

    if not rows:
        print("No contributors found.")
        return

    print(f"{'ID':<25} {'Type':<20} {'Verification':<20} {'Citable':>8} {'Confirm':>8}")
    print("-" * 85)
    for d in sorted(rows, key=lambda x: x["contributor_id"]):
        print(
            f"{d['contributor_id']:<25} "
            f"{d.get('contributor_type',''):<20} "
            f"{d.get('verification_level','unverified'):<20} "
            f"{'yes' if d.get('wikidata_citable') else 'no':>8} "
            f"{'yes' if d.get('can_confirm') else 'no':>8}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Manage ArtBase contributors")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--create-user", action="store_true",
                       help="Register a new private collector")
    group.add_argument("--set-verification", nargs=2,
                       metavar=("CON-ID", "LEVEL"),
                       help="Set verification_level (does NOT change trust flags)")
    group.add_argument("--list", action="store_true",
                       help="List all contributors in the source registry")

    parser.add_argument("--name",  help="Display name (required with --create-user)")
    parser.add_argument("--email", help="Contact email (required with --create-user, internal only)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would change without writing")

    args = parser.parse_args()

    if args.list:
        list_contributors()
        return

    config = Config(REPO_ROOT / "artbase_export" / "config.yaml")

    if args.create_user:
        if not args.name or not args.email:
            print("✗ --create-user requires --name and --email")
            sys.exit(1)
        create_user(args.name, args.email, config, args.dry_run)

    elif args.set_verification:
        cid, level = args.set_verification
        set_verification(cid, level, config, args.dry_run)


if __name__ == "__main__":
    main()
