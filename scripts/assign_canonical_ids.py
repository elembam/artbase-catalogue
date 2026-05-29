#!/usr/bin/env python3
"""
assign_canonical_ids.py — Assign stable AR + Crockford base32 IDs to all artist
and artwork canonical JSON files.

IDs are deterministic: SHA-256(slug)[:5 bytes] → 8 Crockford base32 chars.
Running this script twice produces the same IDs. Safe to re-run.

Usage:
    python3 scripts/assign_canonical_ids.py [--dry-run]
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

# Crockford base32 alphabet (no I, L, O, U)
CROCKFORD = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"

DATA_DIR = Path(__file__).parent.parent / "artbase_export" / "data"
ARTISTS_DIR = DATA_DIR / "artists"
ARTWORKS_DIR = DATA_DIR / "artworks"


def crockford_encode(slug: str, prefix: str) -> str:
    """
    Generate a deterministic Crockford base32 ID from a slug.
    Takes first 5 bytes (40 bits) of SHA-256 → 8 × 5-bit groups.
    E.g. "ART-HERBERTS-SILINS-1926" → "AR3K8VQM2X"
    """
    h = hashlib.sha256(slug.encode("utf-8")).digest()
    num = int.from_bytes(h[:5], "big")
    chars = []
    for _ in range(8):
        chars.append(CROCKFORD[num & 0x1F])
        num >>= 5
    return prefix + "".join(reversed(chars))


def process_file(path: Path, prefix: str, dry_run: bool) -> tuple[str, str]:
    """Load JSON, assign artbase_canonical_id if not already set, save."""
    data = json.loads(path.read_text(encoding="utf-8"))
    slug = data.get("artbase_id", path.stem)

    existing = data.get("artbase_canonical_id")
    new_id = crockford_encode(slug, prefix)

    if existing and existing != new_id:
        print(f"  ⚠️  CONFLICT {path.name}: existing={existing} computed={new_id} — keeping existing")
        return slug, existing

    if existing == new_id:
        return slug, existing  # already correct, nothing to do

    # Assign the new ID
    data["artbase_canonical_id"] = new_id
    if not dry_run:
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    return slug, new_id


def main():
    parser = argparse.ArgumentParser(description="Assign canonical AR/AB IDs to all JSON files")
    parser.add_argument("--dry-run", action="store_true", help="Print IDs without writing files")
    args = parser.parse_args()

    if args.dry_run:
        print("DRY RUN — no files will be written\n")

    # ── Artists ──────────────────────────────────────────────────────────────
    artist_files = sorted(ARTISTS_DIR.glob("*.json"))
    print(f"Artists: {len(artist_files)} files")
    assigned = 0
    for f in artist_files:
        slug, cid = process_file(f, "AR", args.dry_run)
        data = json.loads(f.read_text(encoding="utf-8"))
        was_null = data.get("artbase_canonical_id") is None if not args.dry_run else True
        if was_null or args.dry_run:
            print(f"  {slug:40s}  →  {cid}")
            assigned += 1
    print(f"  Assigned {assigned} artist IDs\n")

    # ── Artworks ─────────────────────────────────────────────────────────────
    artwork_files = sorted(ARTWORKS_DIR.glob("*.json"))
    print(f"Artworks: {len(artwork_files)} files")
    for f in artwork_files:
        slug, cid = process_file(f, "AB", args.dry_run)
        data = json.loads(f.read_text(encoding="utf-8"))
        was_null = data.get("artbase_canonical_id") is None if not args.dry_run else True
        if was_null or args.dry_run:
            print(f"  {slug:40s}  →  {cid}")

    print("\nDone." if not args.dry_run else "\n(dry run — run without --dry-run to write)")


if __name__ == "__main__":
    main()
