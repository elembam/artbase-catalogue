#!/usr/bin/env python3
"""
AAT Linker — add Getty AAT vocabulary URIs to artwork records.

Reads artwork JSONs from data/artworks/, maps free-text materials/techniques/
genres to AAT URIs using the curated mapping in data/_vocab/aat_mapping.json,
and writes enriched artwork.aat_terms blocks back to the JSON files.

Usage:
  python3 scripts/aat_link.py --all              # link all artworks
  python3 scripts/aat_link.py --artwork AP-...   # link single artwork
  python3 scripts/aat_link.py --all --dry-run    # preview changes
"""

import argparse
import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

# Paths
REPO_ROOT = Path(__file__).parent.parent
DATA_DIR = REPO_ROOT / "artbase_export" / "data"
ARTWORKS_DIR = DATA_DIR / "artworks"
VOCAB_DIR = DATA_DIR / "_vocab"
MAPPING_FILE = VOCAB_DIR / "aat_mapping.json"
REPORTS_DIR = REPO_ROOT / "reports"
UNMATCHED_FILE = REPORTS_DIR / "aat_unmatched.json"

AAT_BASE_URI = "http://vocab.getty.edu/aat/"


def load_mapping() -> dict:
    """Load the curated AAT mapping."""
    if not MAPPING_FILE.exists():
        print(f"✗ Mapping file not found: {MAPPING_FILE}")
        sys.exit(1)
    
    with open(MAPPING_FILE) as f:
        return json.load(f)


def normalize_key(text: Optional[str]) -> str:
    """Normalize text for mapping lookup (lowercase, trimmed)."""
    if not text:
        return ""
    return text.strip().lower()


def link_artwork(artwork: dict, mapping: dict, unmatched: dict) -> dict:
    """
    Add aat_terms to an artwork based on the mapping.
    Returns dict with field changes.
    """
    changes = {}
    aat_terms = {}
    
    # Link object type
    obj_type = artwork.get("object_id", {}).get("object_type")
    if obj_type:
        key = normalize_key(obj_type)
        if key in mapping["object_types"]:
            entry = mapping["object_types"][key]
            aat_terms["type"] = {
                "label": entry["label"],
                "aat_uri": f"{AAT_BASE_URI}{entry['aat_id']}"
            }
            changes["type"] = f"linked to {entry['label']}"
        else:
            unmatched.setdefault("object_types", set()).add(obj_type)
    
    # Link materials/techniques
    materials = artwork.get("object_id", {}).get("materials")
    if materials:
        key = normalize_key(materials)
        if key in mapping["materials_techniques"]:
            entry = mapping["materials_techniques"][key]
            materials_list = []
            
            for role in ["technique", "medium", "support"]:
                if role in entry:
                    materials_list.append({
                        "role": role,
                        "label": entry[role]["label"],
                        "aat_uri": f"{AAT_BASE_URI}{entry[role]['aat_id']}"
                    })
            
            if materials_list:
                aat_terms["materials"] = materials_list
                changes["materials"] = f"{len(materials_list)} component(s)"
        else:
            unmatched.setdefault("materials_techniques", set()).add(materials)
    
    # Link genre/subject (check both subject and a hypothetical genre field)
    subject = artwork.get("object_id", {}).get("subject") or artwork.get("genre")
    if subject:
        key = normalize_key(subject)
        if key in mapping["genres"]:
            entry = mapping["genres"][key]
            aat_terms["genre"] = {
                "label": entry["label"],
                "aat_uri": f"{AAT_BASE_URI}{entry['aat_id']}"
            }
            changes["genre"] = f"linked to {entry['label']}"
        # Subject is usually descriptive text, not a genre keyword, so don't
        # add to unmatched unless it looks like a genre term (single word/phrase)
        elif len(subject.split()) <= 3:
            unmatched.setdefault("genres", set()).add(subject)
    
    # Write aat_terms if we have any
    if aat_terms:
        artwork["aat_terms"] = aat_terms
    
    return changes


def process_artworks(artwork_id: Optional[str], dry_run: bool):
    """Process one or all artworks."""
    mapping = load_mapping()
    unmatched = {}
    stats = {
        "scanned": 0,
        "linked": 0,
        "unchanged": 0,
        "errors": 0
    }
    changes_log = []
    
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
            
            original_aat = artwork.get("aat_terms", {})
            changes = link_artwork(artwork, mapping, unmatched)
            
            if changes:
                stats["linked"] += 1
                change_summary = ", ".join(f"{k}: {v}" for k, v in changes.items())
                print(f"  {'~' if dry_run else '✓'} {artwork['artbase_id']}: {change_summary}")
                
                changes_log.append({
                    "id": artwork["artbase_id"],
                    "changes": changes
                })
                
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
        
        # Load existing unmatched if present
        existing = {}
        if UNMATCHED_FILE.exists():
            with open(UNMATCHED_FILE) as f:
                existing = json.load(f)
        
        # Merge with existing (sets → lists for JSON)
        for category, items in unmatched.items():
            existing.setdefault(category, [])
            for item in items:
                if item not in existing[category]:
                    existing[category].append(item)
        
        with open(UNMATCHED_FILE, "w") as f:
            json.dump(existing, f, indent=2, ensure_ascii=False)
            f.write("\n")
        
        total_unmatched = sum(len(v) for v in unmatched.values())
        print(f"\n⚠ {total_unmatched} unmatched term(s) appended to {UNMATCHED_FILE.relative_to(REPO_ROOT)}")
    
    # Summary
    print(f"\nLinked {stats['linked']} artworks, "
          f"{stats['unchanged']} unchanged, "
          f"{stats['errors']} errors{'  [DRY RUN]' if dry_run else ''}")


def main():
    parser = argparse.ArgumentParser(description="Link artwork records to Getty AAT vocabulary")
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
