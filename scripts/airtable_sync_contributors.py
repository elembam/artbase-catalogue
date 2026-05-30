#!/usr/bin/env python3
"""
airtable_sync_contributors.py — Sync the Contributors source-trust registry to Airtable.

Every entity that contributes data to ArtBase (galleries, private collectors,
institutions, platform staff) is a Contributor row in Airtable. This script
reads data/sources/*.json and syncs them to the Contributors table.

It also creates the corresponding Source_Documents row for index-type sources
(e.g. paintings.lv artist list) and links the relevant Artists_Makers rows.

Trust model enforced by this script:
  contributor_type       wikidata_citable  can_confirm  gdpr_sensitive
  ─────────────────────  ────────────────  ───────────  ──────────────
  authority_file         true              true         false
  institutional          true (if auth)    true         false
  platform_staff         false             true         false
  commercial_gallery     false             false        false
  private_collector      false             false        true   ← GDPR
  data_partner           false             false        false

CLI:
    python3 scripts/airtable_sync_contributors.py --dry-run
    python3 scripts/airtable_sync_contributors.py
    python3 scripts/airtable_sync_contributors.py --contributor CON-GALERIJA-JEKABS
    python3 scripts/airtable_sync_contributors.py --new-user \\
        --name "Jane Doe" --email "jane@example.com"   # register a private collector

IMPORTANT: This script writes to Airtable. Run --dry-run first.
The pipeline is otherwise read-only; this is the controlled exception.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path

# ── Path setup ─────────────────────────────────────────────────────────────────
REPO_ROOT    = Path(__file__).resolve().parent.parent
ARTBASE_PKG  = REPO_ROOT / "artbase_export" / "src"
sys.path.insert(0, str(ARTBASE_PKG))

from artbase_export.config import Config
from artbase_export.airtable.schema import (
    Tables, ContributorFields as CF, SourceFields as SF, ArtistFields as AF
)

# ── Config ─────────────────────────────────────────────────────────────────────
DATA_DIR     = REPO_ROOT / "artbase_export" / "data"
ARTISTS_DIR  = DATA_DIR / "artists"
SOURCES_DIR  = DATA_DIR / "sources"

CONTRIBUTOR_TYPE_LABELS = {
    "authority_file":     "Authority File",
    "institutional":      "Institutional",
    "platform_staff":     "Platform Staff",
    "commercial_gallery": "Commercial Gallery",
    "private_collector":  "Private Collector",
    "data_partner":       "Data Partner",
}


# ── Airtable helpers ───────────────────────────────────────────────────────────

def get_api(config: Config):
    try:
        from pyairtable import Api
        return Api(config.airtable.token)
    except ImportError:
        print("✗ pyairtable not installed: pip install pyairtable")
        sys.exit(1)


def get_table(api, base_id: str, table_name: str):
    return api.table(base_id, table_name)


def find_existing(table, field: str, value: str) -> dict | None:
    """Return the first Airtable record matching field=value, or None."""
    try:
        rows = table.all(formula=f'{{{field}}} = "{value}"')
        return rows[0] if rows else None
    except Exception as e:
        print(f"  ⚠ Search error ({field}={value}): {e}")
        return None


# ── Contributor sync ───────────────────────────────────────────────────────────

def build_contributor_fields(src: dict) -> dict:
    """Map a source registry dict to Airtable ContributorFields."""
    ctype = src.get("contributor_type") or src.get("source_type", "")
    return {
        CF.ID:              src["contributor_id"],
        CF.DISPLAY_NAME:    src["name"],
        CF.CONTRIBUTOR_TYPE: CONTRIBUTOR_TYPE_LABELS.get(ctype, ctype),
        CF.WEBSITE:         src.get("website", ""),
        CF.WIKIDATA_CITABLE: src.get("wikidata_citable", False),
        CF.CAN_CONFIRM:     src.get("can_confirm", False),
        CF.GDPR_SENSITIVE:  src.get("gdpr_sensitive", False),
        CF.WIKIDATA_QID:    src.get("wikidata_qid") or "",
        CF.TERMS_NOTE:      (src.get("_meta") or {}).get("terms_note", ""),
        CF.NOTES:           src.get("role_in_catalogue", ""),
    }


def sync_contributor(src: dict, contributors_table, dry_run: bool) -> dict:
    """Create or update a contributor row. Returns {action, airtable_id}."""
    cid = src["contributor_id"]
    fields = build_contributor_fields(src)
    existing = find_existing(contributors_table, CF.ID, cid)

    if existing:
        if not dry_run:
            contributors_table.update(existing["id"], fields)
        return {"action": "updated", "airtable_id": existing["id"]}
    else:
        if not dry_run:
            row = contributors_table.create(fields)
            return {"action": "created", "airtable_id": row["id"]}
        return {"action": "would_create", "airtable_id": None}


# ── Source document sync ───────────────────────────────────────────────────────

def sync_source_document(src: dict, contributor_airtable_id: str | None,
                          sources_table, dry_run: bool) -> dict | None:
    """
    For sources with an artist_index_url, create a Source_Documents row
    representing the artist index page as a citable document reference.
    """
    index_url = src.get("artist_index_url")
    if not index_url:
        return None

    doc_id = f"SD-{src['contributor_id']}-INDEX"
    fields = {
        SF.ID:            doc_id,
        SF.DOCUMENT_TYPE: "Gallery Artist Index",
        SF.CITATION:      f"{src['name']} — Artist Index. {index_url}. Retrieved {date.today().isoformat()}.",
        SF.URL:           index_url,
        SF.RELIABILITY:   "Medium",
        SF.PUBLIC:        "Yes",
        SF.GDPR_SENSITIVE: "No" if not src.get("gdpr_sensitive") else "Yes",
        SF.NOTES:         src.get("role_in_catalogue", ""),
    }
    if contributor_airtable_id:
        fields[SF.CONTRIBUTOR] = [contributor_airtable_id]

    existing = find_existing(sources_table, SF.ID, doc_id)
    if existing:
        if not dry_run:
            sources_table.update(existing["id"], fields)
        return {"action": "updated", "airtable_id": existing["id"]}
    else:
        if not dry_run:
            row = sources_table.create(fields)
            return {"action": "created", "airtable_id": row["id"]}
        return {"action": "would_create", "airtable_id": None}


# ── Artist link sync ───────────────────────────────────────────────────────────

def sync_artist_links(src: dict, source_doc_airtable_id: str | None,
                       artists_table, dry_run: bool) -> int:
    """
    For each artist JSON that has an attestation from this source, link the
    Airtable Artists_Makers row to the Source_Documents row (not Contributor).
    Returns count of artists linked.
    """
    if not source_doc_airtable_id:
        return 0

    source_id = src["source_id"]
    linked = 0

    for path in sorted(ARTISTS_DIR.glob("ART-*.json")):
        artist = json.loads(path.read_text(encoding="utf-8"))
        has_att = any(
            a.get("source_id") == source_id
            for a in artist.get("attestations", [])
        )
        if not has_att:
            continue

        artbase_id = artist.get("artbase_id", path.stem)
        existing = find_existing(artists_table, AF.ARTBASE_ID, artbase_id)
        if not existing:
            continue

        # Append source doc to the linked Source Documents field
        current_sources = [
            r["id"] for r in
            (existing["fields"].get(AF.SOURCES) or [])
            if isinstance(r, dict)
        ]
        if source_doc_airtable_id not in current_sources:
            if not dry_run:
                artists_table.update(existing["id"], {
                    AF.SOURCES: current_sources + [source_doc_airtable_id]
                })
            linked += 1

    return linked


# ── Private user registration ──────────────────────────────────────────────────

def register_private_user(name: str, email: str, config: Config,
                           dry_run: bool) -> None:
    """
    Register a new private collector as a Contributor.

    This creates:
    1. A source registry JSON in data/sources/
    2. A Contributors row in Airtable

    Trust defaults for private collectors:
      wikidata_citable: false  — their claims need independent confirmation
      can_confirm: false       — they are origin only
      gdpr_sensitive: true     — personal data, contact email stays internal

    The contributor_id is auto-incremented from existing CON-USER-* entries.
    """
    # Find next user ID
    existing_ids = [
        p.stem for p in SOURCES_DIR.glob("SRC-USER-*.json")
    ]
    next_n = len(existing_ids) + 1
    cid = f"CON-USER-{next_n:05d}"
    sid = f"SRC-USER-{next_n:05d}"
    today = date.today().isoformat()

    src = {
        "source_id":        sid,
        "contributor_id":   cid,
        "name":             name,
        "source_type":      "private_collector",
        "contributor_type": "private_collector",
        "wikidata_citable": False,
        "can_confirm":      False,
        "gdpr_sensitive":   True,
        "role_in_catalogue": "Private collector — data origin only. Facts require independent authority confirmation before publication.",
        "_meta": {
            "registered_at": today,
            "contact_email": email,   # stored in registry, NEVER exported to HTML/JSON
            "terms_note": "Data submitted by collector. Personal data handled under GDPR Art.6(1)(b). Do not publish contact details.",
        }
    }

    registry_path = SOURCES_DIR / f"{sid}.json"
    if not dry_run:
        registry_path.write_text(json.dumps(src, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  ✓ Created source registry: {registry_path}")
    else:
        print(f"  ~ Would create: {registry_path}")

    # Sync to Airtable
    api = get_api(config)
    contributors_table = get_table(api, config.airtable.base_id, Tables.CONTRIBUTORS)
    result = sync_contributor(src, contributors_table, dry_run)
    tag = "(DRY RUN)" if dry_run else ""
    print(f"  {result['action']} contributor {cid} in Airtable {tag}")
    print(f"\n  Contributor ID: {cid}")
    print(f"  Source ID:      {sid}")
    print(f"  ⚠  Contact email stored only in source registry — never exported.")


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Sync Contributors registry to Airtable"
    )
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would change without writing")
    parser.add_argument("--contributor", metavar="CON-ID",
                        help="Sync a single contributor only")
    # New-user registration sub-command flags
    parser.add_argument("--new-user", action="store_true",
                        help="Register a new private collector")
    parser.add_argument("--name", help="Display name (required with --new-user)")
    parser.add_argument("--email", help="Contact email (required with --new-user, internal only)")
    args = parser.parse_args()

    config = Config(REPO_ROOT / "artbase_export" / "config.yaml")

    # ── Private user registration ──────────────────────────────────────────────
    if args.new_user:
        if not args.name or not args.email:
            print("✗ --new-user requires --name and --email")
            sys.exit(1)
        register_private_user(args.name, args.email, config, args.dry_run)
        return

    # ── Bulk / single contributor sync ────────────────────────────────────────
    sources = []
    for path in SOURCES_DIR.glob("*.json"):
        try:
            s = json.loads(path.read_text(encoding="utf-8"))
            if "contributor_id" not in s:
                continue  # skip old-format entries without contributor_id
            if args.contributor and s["contributor_id"] != args.contributor:
                continue
            sources.append(s)
        except (KeyError, json.JSONDecodeError) as e:
            print(f"  ⚠ Skipping {path.name}: {e}")

    if not sources:
        print("No contributor sources found.")
        return

    api = get_api(config)
    base = config.airtable.base_id
    contributors_table = get_table(api, base, Tables.CONTRIBUTORS)
    sources_table      = get_table(api, base, Tables.SOURCES)
    artists_table      = get_table(api, base, Tables.ARTISTS)

    dry_tag = " (DRY RUN)" if args.dry_run else ""

    for src in sources:
        cid = src["contributor_id"]
        print(f"\n{cid} — {src['name']}")

        # 1. Sync contributor row
        result = sync_contributor(src, contributors_table, args.dry_run)
        print(f"  Contributor: {result['action']}{dry_tag}")
        contributor_airtable_id = result.get("airtable_id")

        # 2. Sync source document (index page etc.)
        doc_result = sync_source_document(src, contributor_airtable_id, sources_table, args.dry_run)
        if doc_result:
            print(f"  Source doc:  {doc_result['action']}{dry_tag}")

        # 3. Link matched artists to the source document row
        source_doc_id = doc_result.get("airtable_id") if doc_result else None
        linked = sync_artist_links(src, source_doc_id, artists_table, args.dry_run)
        if linked:
            print(f"  Artist links: {linked} artist(s) linked{dry_tag}")
        else:
            print(f"  Artist links: none to add")

    print(f"\n✓ Sync complete{dry_tag}")


if __name__ == "__main__":
    main()
