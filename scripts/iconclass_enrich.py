#!/usr/bin/env python3
"""
ICONCLASS Label Enrichment — add human-readable labels to ICONCLASS codes.

Reads artwork JSONs and maps ICONCLASS codes to labels using the curated
mapping in data/_vocab/iconclass_mapping.json.

Usage:
  python3 scripts/iconclass_enrich.py --all              # enrich all artworks
  python3 scripts/iconclass_enrich.py --artwork AP-...   # single artwork
  python3 scripts/iconclass_enrich.py --all --dry-run    # preview changes
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

# Paths
REPO_ROOT = Path(__file__).parent.parent
DATA_DIR = REPO_ROOT / "artbase_export" / "data"
ARTWORKS_DIR = DATA_DIR / "artworks"
VOCAB_DIR = DATA_DIR / "_vocab"
MAPPING_FILE = VOCAB_DIR / "iconclass_mapping.json"
REPORTS_DIR = REPO_ROOT / "reports"
UNMATCHED_FILE = REPORTS_DIR / "iconclass_unmatched.json"


def load_mapping() -> dict:
    """Load the curated ICONCLASS mapping."""
    if not MAPPING_FILE.exists():
        print(f"✗ Mapping file not found: {MAPPING_FILE}")
        sys.exit(1)
    
    with open(MAPPING_FILE) as f:
        return json.load(f)


def enrich_artwork(artwork: dict, mapping: dict, unmatched: set) -> dict:
    """
    Add iconclass_labels to an artwork based on the mapping.
    Returns dict with changes info.
    """
    changes = {}
    codes = artwork.get("iconography", {}).get("iconclass_codes", [])
    
    if not codes:
        return changes
    
    labels = []
    for code in codes:
        if code in mapping:
            labels.append({
                "code": code,
                "label": mapping[code],
                "uri": f"https://iconclass.org/{code}"
            })
        else:
            unmatched.add(code)
    
    if labels:
        if "iconography" not in artwork:
            artwork["iconography"] = {}
        
        old_labels = artwork["iconography"].get("iconclass_labels", [])
        artwork["iconography"]["iconclass_labels"] = labels
        
        if old_labels != labels:
            changes["iconclass_labels"] = f"{len(labels)} label(s) added"
    
    return changes


def process_artworks(artwork_id: Optional[str], dry_run: bool):
    """Process one or all artworks."""
    mapping = load_mapping()
    unmatched = set()
    stats = {
        "scanned": 0,
        "enriched": 0,
        "unchanged": 0,
        "errors": 0
    }
    
    # Find artworks to process
    if artwork_id:
        files = [ARTWORKS_DIR / f"{artwork_id}.json"]
        if not files[0].exists():
            print(f"✗ Artwork not found: {artwork_id}")
            return
    else:
        files = sorted(ARTWORKS_DIR.glob("AP-*.json"))
    
    print(f"Scanning {len(files)} artwork(s){'  [DRY RUN]' if dry_run else ''}...")
    
    for filepath in files:
        stats["scanned"] += 1
        
        try:
            with open(filepath) as f:
                artwork = json.load(f)
            
            changes = enrich_artwork(artwork, mapping, unmatched)
            
            if changes:
                stats["enriched"] += 1
                codes = artwork.get("iconography", {}).get("iconclass_codes", [])
                labels_count = len(artwork.get("iconography", {}).get("iconclass_labels", []))
                print(f"  {'~' if dry_run else '✓'} {artwork['artbase_id']}: {labels_count}/{len(codes)} labels")
                
                if not dry_run:
                    with open(filepath, "w") as f:
                        json.dump(artwork, f, indent=2, ensure_ascii=False)
                        f.write("\n")
            else:
                stats["unchanged"] += 1
        
        except Exception as e:
            stats["errors"] += 1
            print(f"  ✗ {filepath.name}: {e}")
    
    # Write unmatched report
    if unmatched:
        REPORTS_DIR.mkdir(exist_ok=True)
        
        existing = []
        if UNMATCHED_FILE.exists():
            with open(UNMATCHED_FILE) as f:
                existing = json.load(f)
        
        for code in unmatched:
            if code not in existing:
                existing.append(code)
        
        with open(UNMATCHED_FILE, "w") as f:
            json.dump(sorted(existing), f, indent=2)
            f.write("\n")
        
        print(f"\n⚠ {len(unmatched)} unmatched code(s) appended to {UNMATCHED_FILE.relative_to(REPO_ROOT)}")
    
    # Summary
    print(f"\nEnriched {stats['enriched']} artworks, "
          f"{stats['unchanged']} unchanged, "
          f"{stats['errors']} errors{'  [DRY RUN]' if dry_run else ''}")


def main():
    parser = argparse.ArgumentParser(description="Enrich artwork records with ICONCLASS labels")
    parser.add_argument("--artwork", help="Single artwork ID (e.g., AP-2026-000001)")
    parser.add_argument("--all", action="store_true", help="Process all artworks")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    
    args = parser.parse_args()
    
    if not args.artwork and not args.all:
        parser.error("Must specify --artwork ID or --all")
    
    if args.artwork and args.all:
        parser.error("Cannot specify both --artwork and --all")
    
    process_artworks(args.artwork, args.dry_run)


if __name__ == "__main__":
    main()
