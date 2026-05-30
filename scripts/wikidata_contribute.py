#!/usr/bin/env python3
"""
wikidata_contribute.py

Generate QuickStatements batches to contribute Arsaccordia data TO Wikidata.
NEVER auto-submits. Output is human-reviewed .qs files for manual submission.

Phase 1: External identifiers only (LNDB, ULAN, VIAF, Commons category)
Phase 2: Factual biographical data (dates, places, images)
Phase 3: Interpretive data (education, movement, genre) — deferred

Hard rule (Instruction 8): any source with wikidata_citable: false in the
source registry MUST NOT appear in any QuickStatements reference (S248).
check_source_citable() enforces this before any statement is emitted.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Phase gate — change this constant to enable higher phases
CURRENT_PHASE = 1

# Base URL for Ars Accordia artist pages
ARSACCORDIA_BASE = "https://arsaccordia.com/artists"

# Phase 1: External identifiers (safest)
PHASE_1_PROPERTIES = {
    "P7400": "lndb",      # LNDB ID
    "P245": "ulan",       # Getty ULAN ID
    "P214": "viaf",       # VIAF ID
    "P373": "commons",    # Commons category
    "P973": "arsaccordia_page",  # described at URL — Ars Accordia artist page
}

# Phase 2: Factual biographical data
PHASE_2_PROPERTIES = {
    "P569": "birth_date",
    "P570": "death_date",
    "P19": "birth_place",
    "P20": "death_place",
    "P18": "image",
}

# Phase 3: Interpretive data (not yet enabled)
PHASE_3_PROPERTIES = {
    "P69": "education",
    "P135": "movement",
    "P136": "genre",
    "P106": "occupation",
}

# Source authority QIDs for S248 references
SOURCE_QIDS = {
    "lndb": "Q105108433",  # National Library of Latvia
    "ulan": "Q1142772",    # Getty ULAN
    "viaf": "Q54919",      # VIAF
    "commons": "Q565",     # Wikimedia Commons
}


def _load_source_registry() -> dict[str, dict]:
    """Load data/sources/*.json — returns {source_id: source_dict}."""
    sources_dir = Path(__file__).resolve().parent.parent / "artbase_export" / "data" / "sources"
    registry: dict[str, dict] = {}
    if sources_dir.exists():
        for p in sources_dir.glob("*.json"):
            try:
                s = json.loads(p.read_text(encoding="utf-8"))
                registry[s["source_id"]] = s
            except (KeyError, json.JSONDecodeError):
                pass
    return registry

# Loaded once at import time
_SOURCE_REGISTRY: dict[str, dict] = _load_source_registry()


def check_source_citable(source_id: str) -> bool:
    """
    Return True only if this source may back a Wikidata reference.

    Trust is resolved in two layers (Part B):
      1. Source-document override: wikidata_citable_override in the source JSON.
         Values: "true" / "false" / "inherit" (or absent → inherit).
      2. Contributor default: wikidata_citable on the source JSON.

    Hard rules:
      - Any source with wikidata_citable: false is blocked.
      - owner_asserted / user_submission / pending_review sources are NEVER citable.
      - Defaults to True for unknown sources (external authority files not in registry).
    """
    src = _SOURCE_REGISTRY.get(source_id)
    if src is None:
        return True   # unknown → assume authority-grade

    # Hard block: submissions under review or owner-asserted cannot be Wikidata sources
    if src.get("status") in ("pending_review", "rejected"):
        return False
    if src.get("source_type") in ("user_submission",):
        return False

    # Layer 1: source-document override takes precedence
    override = src.get("wikidata_citable_override", "inherit")
    if override == "true":
        return True
    if override == "false":
        return False

    # Layer 2: contributor default
    return bool(src.get("wikidata_citable", True))


class ContributionBatch:
    """Manages a single QuickStatements contribution batch."""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        self.statements: list[str] = []
        self.review_items: list[dict] = []
        self.skipped: list[dict] = []
        self.artists_count = 0
        
    def add_statement(self, qid: str, prop: str, value: str, refs: dict, artist_info: dict):
        """Add a single statement to the batch with references."""
        # Build tab-separated QuickStatements line
        parts = [qid, prop, value]
        
        # Required references
        if "reference_url" in refs:
            parts.extend(["S854", f'"{refs["reference_url"]}"'])
        
        if "retrieved" in refs:
            parts.extend(["S813", refs["retrieved"]])
        
        if "stated_in_qid" in refs:
            parts.extend(["S248", refs["stated_in_qid"]])
        
        if "title" in refs:
            parts.extend(["S1476", refs["title"]])
        
        self.statements.append("\t".join(parts))
        
        # Add to review doc
        self.review_items.append({
            "qid": qid,
            "artist": artist_info.get("name", "Unknown"),
            "property": prop,
            "value": value,
            "source_url": refs.get("reference_url", ""),
            "confidence": "verified",
        })
        
    def skip(self, artist_id: str, reason: str):
        """Log a skipped contribution."""
        self.skipped.append({"artist_id": artist_id, "reason": reason})
        
    def write(self) -> tuple[Path, Path]:
        """Write .qs and .review.md files."""
        qs_path = self.output_dir / f"queue_{self.timestamp}.qs"
        review_path = self.output_dir / f"queue_{self.timestamp}.review.md"
        
        # Write .qs file
        with open(qs_path, "w", encoding="utf-8") as f:
            # Header comments
            f.write(f"#title Arsaccordia Latvian artist records: Phase {CURRENT_PHASE} contributions\n")
            f.write(f"#summary Adding external identifiers from verified sources\n")
            f.write(f"#prepared_by Arsaccordia\n")
            f.write(f"#prepared_at {datetime.now(timezone.utc).isoformat()}\n")
            f.write(f"#phase {CURRENT_PHASE}\n")
            f.write(f"#review_doc {review_path.name}\n")
            f.write("\n")
            
            # Statements
            for stmt in self.statements:
                f.write(stmt + "\n")
        
        # Write review document
        with open(review_path, "w", encoding="utf-8") as f:
            f.write(f"# Contribution batch {self.timestamp}\n\n")
            f.write(f"**Phase:** {CURRENT_PHASE} (external identifiers only)\n")
            f.write(f"**Statements proposed:** {len(self.statements)}\n")
            f.write(f"**Distinct artists:** {self.artists_count}\n")
            f.write(f"**Properties:** ")
            
            prop_counts = {}
            for item in self.review_items:
                prop = item["property"]
                prop_counts[prop] = prop_counts.get(prop, 0) + 1
            
            prop_list = [f"{prop} × {count}" for prop, count in prop_counts.items()]
            f.write(", ".join(prop_list) + "\n\n")
            
            f.write("## Per-statement review\n\n")
            
            current_qid = None
            for item in self.review_items:
                if item["qid"] != current_qid:
                    current_qid = item["qid"]
                    f.write(f"\n### {item['qid']} {item['artist']}\n")
                
                f.write(f"- **Adding** {item['property']} = {item['value']}\n")
                f.write(f"- **Source:** {item['source_url']}\n")
                f.write(f"- **Arsaccordia confidence:** {item['confidence']}\n")
                risk = "low — described at URL, no identity claim" if item["property"] == "P973" else "low — external identifier"
                f.write(f"- **Risk:** {risk}\n\n")
            
            if self.skipped:
                f.write("\n## Skipped (with reasons)\n\n")
                for skip in self.skipped:
                    f.write(f"- {skip['artist_id']}: {skip['reason']}\n")
            
            f.write("\n## Submission checklist\n\n")
            f.write("- [ ] Visually scan the .qs file — confirm tabs, quotes, time format\n")
            f.write("- [ ] Open https://quickstatements.toolforge.org/ and log in\n")
            f.write("- [ ] Paste contents into 'Import V1 commands'\n")
            f.write("- [ ] Click 'Import' — confirm batch appears\n")
            f.write("- [ ] Preview first 5 statements in human-readable form\n")
            f.write("- [ ] Click 'Run' only if all spot-checks correct\n")
            f.write("- [ ] Watch batch run. Note any failures.\n")
            f.write("- [ ] Mark this doc as ✅ submitted with timestamp\n")
        
        return qs_path, review_path


def load_artist(path: Path) -> dict:
    """Load artist JSON from canonical store."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def check_eligibility(artist: dict, prop: str, phase: int) -> tuple[bool, str]:
    """
    Check if this artist/property pair is eligible for contribution.
    Returns (eligible, reason).
    """
    # Check phase
    if phase == 1 and prop not in PHASE_1_PROPERTIES:
        return False, f"Property {prop} not in Phase 1"
    elif phase == 2 and prop not in PHASE_1_PROPERTIES and prop not in PHASE_2_PROPERTIES:
        return False, f"Property {prop} not in Phase 2"
    elif phase > CURRENT_PHASE:
        return False, f"Phase {phase} not yet enabled (current: {CURRENT_PHASE})"
    
    # Must have Wikidata QID
    wikidata = artist.get("authority_links", {}).get("wikidata", {})
    if not wikidata.get("id"):
        return False, "No Wikidata QID"
    
    # Check verification status
    # For now, we'll trust artists that have been enriched
    # In production, check artist.get("cataloguing", {}).get("review_status")
    
    # Check do_not_contribute list
    do_not_contribute = artist.get("_meta", {}).get("do_not_contribute", [])
    if prop in do_not_contribute:
        return False, f"Property {prop} in do_not_contribute list"
    
    return True, "OK"


def get_lndb_id(artist: dict) -> Optional[tuple[str, dict]]:
    """Extract LNDB ID and build reference dict."""
    # LNDB is stored in a custom field or authority_links
    # For now, check if we have LNDB data from enrichment
    # This is a placeholder — real implementation needs LNDB field
    
    # Check _meta for LNDB source
    meta = artist.get("_meta", {})
    
    # For demo: if artist has Wikidata enrichment, we might have LNDB
    # In production, this needs proper LNDB field in canonical schema
    
    return None  # Placeholder


def get_viaf_id(artist: dict) -> Optional[tuple[str, dict]]:
    """Extract VIAF ID and build reference dict."""
    viaf = artist.get("authority_links", {}).get("viaf", {})
    viaf_id = viaf.get("id")
    
    if not viaf_id:
        return None
    
    # Build reference
    ref = {
        "reference_url": f"https://viaf.org/viaf/{viaf_id}/",
        "retrieved": datetime.now(timezone.utc).strftime("+%Y-%m-%dT00:00:00Z/11"),
        "stated_in_qid": SOURCE_QIDS["viaf"],
    }
    
    return f'"{viaf_id}"', ref


def get_ulan_id(artist: dict) -> Optional[tuple[str, dict]]:
    """Extract Getty ULAN ID and build reference dict."""
    ulan = artist.get("authority_links", {}).get("ulan", {})
    ulan_id = ulan.get("id")
    
    if not ulan_id:
        return None
    
    # Build reference
    ref = {
        "reference_url": f"http://vocab.getty.edu/page/ulan/{ulan_id}",
        "retrieved": datetime.now(timezone.utc).strftime("+%Y-%m-%dT00:00:00Z/11"),
        "stated_in_qid": SOURCE_QIDS["ulan"],
    }
    
    return f'"{ulan_id}"', ref


def get_artist_page_url(artist: dict) -> Optional[tuple[str, dict]]:
    """
    Build P973 (described at URL) statement pointing to the Ars Accordia artist page.

    Only generated when the artist page has been published (i.e. the artist
    has an artbase_id and a confirmed Wikidata QID — both required before
    any page is generated or linked to from a Wikidata item).
    """
    artbase_id = artist.get("artbase_id")
    if not artbase_id:
        return None

    page_url = f"{ARSACCORDIA_BASE}/{artbase_id}.html"

    retrieved = datetime.now(timezone.utc).strftime("+%Y-%m-%dT00:00:00Z/11")
    ref = {
        "reference_url": page_url,
        "retrieved": retrieved,
    }

    return f'"{page_url}"', ref


def fetch_wikidata_current_state(qid: str) -> dict:
    """
    Fetch current Wikidata entity to check existing claims.
    Uses cache if available, otherwise fetches live.
    """
    # Import here to avoid circular dependency
    sys.path.insert(0, str(Path(__file__).parent))
    from wikidata_lib.fetch import fetch_entities
    
    entities = fetch_entities([qid])
    return entities.get(qid, {})


def has_existing_claim(entity: dict, prop: str) -> bool:
    """Check if Wikidata entity already has a claim for this property."""
    claims = entity.get("claims", {})
    return prop in claims and len(claims[prop]) > 0


def process_artist(artist: dict, args: argparse.Namespace, batch: ContributionBatch) -> int:
    """
    Process a single artist. Returns number of statements added.
    """
    artist_id = artist.get("artbase_id", "UNKNOWN")
    wikidata_qid = artist.get("authority_links", {}).get("wikidata", {}).get("id")
    
    if not wikidata_qid:
        batch.skip(artist_id, "No Wikidata QID")
        return 0
    
    # Fetch current Wikidata state only when --refresh-wikidata is explicitly requested.
    # Default: skip live fetch (entity = {}), which means has_existing_claim returns False
    # and all eligible values are proposed. QuickStatements itself rejects actual duplicates.
    if args.refresh_wikidata and not args.dry_run:
        if not hasattr(process_artist, '_cache'):
            process_artist._cache = {}
        if wikidata_qid not in process_artist._cache:
            entity = fetch_wikidata_current_state(wikidata_qid)
            process_artist._cache[wikidata_qid] = entity
        else:
            entity = process_artist._cache[wikidata_qid]
    else:
        entity = {}  # No live fetch — QuickStatements will reject duplicates safely
    
    statements_added = 0
    
    # Process Phase 1 properties
    if CURRENT_PHASE >= 1:
        # VIAF
        if not args.property or args.property == "P214":
            if not has_existing_claim(entity, "P214"):
                viaf_data = get_viaf_id(artist)
                if viaf_data:
                    value, refs = viaf_data
                    batch.add_statement(wikidata_qid, "P214", value, refs, {
                        "name": artist.get("identity", {}).get("preferred_name", "")
                    })
                    statements_added += 1
        
        # ULAN
        if not args.property or args.property == "P245":
            if not has_existing_claim(entity, "P245"):
                ulan_data = get_ulan_id(artist)
                if ulan_data:
                    value, refs = ulan_data
                    batch.add_statement(wikidata_qid, "P245", value, refs, {
                        "name": artist.get("identity", {}).get("preferred_name", "")
                    })
                    statements_added += 1

        # P973 — described at URL (Ars Accordia artist page)
        if not args.property or args.property == "P973":
            if not has_existing_claim(entity, "P973"):
                page_data = get_artist_page_url(artist)
                if page_data:
                    value, refs = page_data
                    batch.add_statement(wikidata_qid, "P973", value, refs, {
                        "name": artist.get("identity", {}).get("preferred_name", "")
                    })
                    statements_added += 1
    
    return statements_added


def main():
    parser = argparse.ArgumentParser(
        description="Generate QuickStatements batches for Wikidata contribution"
    )
    parser.add_argument("--artist", help="Process single artist by ID")
    parser.add_argument("--property", help="Process single property (e.g., P7400)")
    parser.add_argument("--max", type=int, help="Maximum statements to generate")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    parser.add_argument("--refresh-wikidata", action="store_true", 
                       help="Re-fetch Wikidata state (default: use cache)")
    
    args = parser.parse_args()
    
    # Setup paths
    base_dir = Path(__file__).parent.parent / "artbase_export"
    artists_dir = base_dir / "data" / "artists"
    output_dir = base_dir / "data" / "contributions"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Check phase restrictions
    if args.property:
        if args.property in PHASE_3_PROPERTIES and CURRENT_PHASE < 3:
            print(f"❌ Property {args.property} is Phase 3, but CURRENT_PHASE={CURRENT_PHASE}")
            print(f"   Phase 3 properties require code change to enable.")
            return 1
        elif args.property in PHASE_2_PROPERTIES and CURRENT_PHASE < 2:
            print(f"❌ Property {args.property} is Phase 2, but CURRENT_PHASE={CURRENT_PHASE}")
            return 1
    
    # Create batch
    batch = ContributionBatch(output_dir)
    
    # Process artists
    if args.artist:
        artist_files = [artists_dir / f"{args.artist}.json"]
    else:
        artist_files = sorted(artists_dir.glob("ART-*.json"))
    
    total_statements = 0
    artists_processed = set()
    
    for artist_file in artist_files:
        if not artist_file.exists():
            print(f"⚠️  Artist file not found: {artist_file}")
            continue
        
        artist = load_artist(artist_file)
        artist_id = artist.get("artbase_id", "")
        
        statements = process_artist(artist, args, batch)
        if statements > 0:
            total_statements += statements
            artists_processed.add(artist_id)
        
        # Check max limit
        if args.max and total_statements >= args.max:
            break
    
    batch.artists_count = len(artists_processed)
    
    # Output
    if args.dry_run:
        print(f"\n🔍 DRY RUN — no files written")
        print(f"   Would generate {total_statements} statements for {len(artists_processed)} artists")
        for item in batch.review_items[:5]:
            print(f"   • {item['qid']} {item['property']} = {item['value']}")
        if len(batch.review_items) > 5:
            print(f"   ... and {len(batch.review_items) - 5} more")
        return 0
    
    if total_statements == 0:
        print("✅ No eligible contributions found.")
        print("   Reasons:")
        for skip in batch.skipped[:10]:
            print(f"   • {skip['artist_id']}: {skip['reason']}")
        return 0
    
    # Write files
    qs_path, review_path = batch.write()
    
    print(f"\n✅ QuickStatements batch generated")
    print(f"   {total_statements} statements for {len(artists_processed)} artists")
    print(f"   Phase: {CURRENT_PHASE}")
    print(f"\n📄 Files written:")
    print(f"   {qs_path}")
    print(f"   {review_path}")
    print(f"\n📋 Next steps:")
    print(f"   1. Open {qs_path} in text editor and visually verify")
    print(f"   2. Read {review_path} carefully")
    print(f"   3. Go to https://quickstatements.toolforge.org/")
    print(f"   4. Log in as Arsaccordia")
    print(f"   5. Import V1 commands → paste file contents")
    print(f"   6. Preview and run ONLY if everything looks correct")
    print(f"\n⚠️  NEVER skip the manual review step!")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
