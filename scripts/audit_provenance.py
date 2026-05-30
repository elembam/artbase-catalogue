#!/usr/bin/env python3
"""
Data Provenance Auditor — classify every field by its source.

Walks canonical JSONs and attributes each field to a known source (Wikidata,
ULAN, AAT, manual entry, etc.). Flags unattributed fields as potential demo
residue or orphaned legacy data.

READ-ONLY. Writes reports, never modifies data.

Usage:
  python3 scripts/audit_provenance.py                  # scan all
  python3 scripts/audit_provenance.py --record ID      # single record
  python3 scripts/audit_provenance.py --strict         # exit 1 if unattributed found
  python3 scripts/audit_provenance.py --by-source ulan # filter by source
  python3 scripts/audit_provenance.py --since 2026-05-01
"""

import argparse
import csv
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from collections import defaultdict

# Paths
REPO_ROOT = Path(__file__).parent.parent
DATA_DIR = REPO_ROOT / "artbase_export" / "data"
ARTISTS_DIR = DATA_DIR / "artists"
ARTWORKS_DIR = DATA_DIR / "artworks"
REPORTS_DIR = REPO_ROOT / "reports"

# Source classification constants
CORE_IDENTITY_FIELDS = {
    "artbase_id", "airtable_id", "artbase_canonical_id", "version",
    "created", "exported", "visibility", "_schema",
    # Artist identity fields
    "identity.preferred_name", "identity.full_name", "identity.sort_name",
    "identity.preferred_name_language", "identity.name_variants",
    # Artwork Object ID core fields
    "object_id.title", "object_id.maker_id", "object_id.maker_display_name",
    "object_id.date_display", "object_id.date_earliest", "object_id.date_latest",
    "object_id.object_type", "object_id.materials", "object_id.dimensions_display",
    "object_id.height_cm", "object_id.width_cm", "object_id.depth_cm",
    "object_id.inscriptions", "object_id.distinguishing", "object_id.subject",
    "object_id.has_photograph",
    # Location
    "location.collection", "location.collection_qid", "location.inventory_number",
    "location.location_notes",
    # Cataloguing metadata
    "cataloguing.review_status", "cataloguing.catalogued_by", "cataloguing.notes",
    "cataloguing.tasks", "cataloguing.engagement_ids",
}

WIKIDATA_TIER1_FIELDS = {
    "life.birth_date", "life.death_date", "life.birth_place", "life.death_place",
    "description_en", "description_lv", "image",
    "authority_links.lndb",
}

WIKIDATA_TIER2_FIELDS = {
    "education", "movement", "genre",
}


def flatten_dict(d: Dict, parent_key: str = "", sep: str = ".") -> Dict[str, Any]:
    """Flatten nested dict to dot-notation paths."""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict) and not _is_leaf_object(new_key, v):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list) and v and isinstance(v[0], dict):
            # List of dicts - flatten each
            for i, item in enumerate(v):
                if isinstance(item, dict):
                    items.extend(flatten_dict(item, f"{new_key}[{i}]", sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def _is_leaf_object(path: str, obj: dict) -> bool:
    """
    Determine if a dict should be treated as a leaf value.
    E.g., {label: "...", wikidata_id: "..."} is a leaf, not a container.
    """
    # AAT/authority structures with label+uri/id are leaves
    if set(obj.keys()) <= {"label", "aat_uri", "aat_id", "uri", "id", "status", 
                            "verified_date", "notes", "role", "wikidata_id", 
                            "wikidata_qid", "tgn_uri", "display", "source_ids",
                            "value", "precision", "source"}:
        return True
    return False


def classify_field(path: str, value: Any, record: Dict, meta: Dict) -> Tuple[str, str]:
    """
    Classify a field's data source.
    Returns (source_category, reason).
    """
    # Skip empty/null values
    if value is None or value == "" or value == []:
        return ("empty", "empty value")
    
    # 10. METADATA - _meta tree is self-documenting
    if path.startswith("_meta"):
        return ("metadata", "_meta subtree is source-tracking")
    
    # 1. CORE_IDENTITY
    if path in CORE_IDENTITY_FIELDS:
        return ("core_identity", "base field from Airtable export")
    
    # Check for partial matches (e.g., identity.*, object_id.*)
    for core_field in CORE_IDENTITY_FIELDS:
        if path.startswith(core_field.split("[")[0]):
            return ("core_identity", "base field from Airtable export")
    
    # 7. MANUAL_OVERRIDE
    manual_overrides = meta.get("manual_overrides", [])
    if path in manual_overrides:
        return ("manual_override", "field in _meta.manual_overrides")
    
    # 6. CANDIDATE_VERIFICATION
    if path.startswith("_meta.candidate_evidence"):
        return ("candidate_verification", "candidate verification evidence")
    
    # 2. AUTHORITY_ID
    if path.startswith("authority_links."):
        if meta.get("wikidata_last_enriched") or meta.get("ulan_last_enriched"):
            return ("authority_id", "authority ID with enrichment proof")
        else:
            return ("authority_id_without_pipeline_proof", 
                    "authority ID present but no _meta enrichment timestamp")
    
    # 3. WIKIDATA_ENRICHMENT - Tier 1
    for tier1_field in WIKIDATA_TIER1_FIELDS:
        if path.startswith(tier1_field):
            if meta.get("wikidata_last_enriched"):
                return ("wikidata_enrichment", "Tier 1 field from wikidata_enrich.py")
            else:
                return ("tier1_field_without_enrichment_run",
                        "Tier 1 field populated but no wikidata_last_enriched timestamp")
    
    # WIKIDATA_ENRICHMENT - Tier 2 (in enrichment namespace)
    for tier2_field in WIKIDATA_TIER2_FIELDS:
        if tier2_field in path:
            if meta.get("wikidata_last_enriched"):
                return ("wikidata_enrichment", "Tier 2 field from wikidata_enrich.py")
            else:
                return ("tier2_field_without_enrichment_run",
                        "Tier 2 field populated but no wikidata_last_enriched timestamp")
    
    # 4. ULAN_ENRICHMENT
    if path.startswith("enrichment.ulan"):
        if meta.get("ulan_last_enriched"):
            return ("ulan_enrichment", "ULAN enrichment field")
        else:
            return ("ulan_field_without_enrichment_run",
                    "ULAN field populated but no ulan_last_enriched timestamp")
    
    # 5. AAT_LINKING
    if path.startswith("aat_terms"):
        if meta.get("aat_linked_at"):
            return ("aat_linking", "AAT vocabulary linking")
        else:
            return ("aat_field_without_linking_run",
                    "AAT field populated but no aat_linked_at timestamp")
    
    # ICONCLASS labels
    if path.startswith("iconography.iconclass_labels"):
        if meta.get("iconclass_enriched_at"):
            return ("iconclass_enrichment", "ICONCLASS label enrichment")
        else:
            return ("iconclass_enriched_no_timestamp",
                    "ICONCLASS labels present but no timestamp")
    
    # 8. DISCOVERY_FIELDS
    if path in ["discovery_source", "discovered_at"] and "discovery_source" in record:
        return ("discovery_fields", "artwork discovery metadata")
    
    # 9. PROVENANCE_BLOCK - check if provenance entries have source
    if path.startswith("provenance"):
        # For now, accept all provenance fields
        return ("provenance_block", "provenance documentation")
    
    # Accept descriptors fields from Airtable
    if path.startswith("descriptors."):
        return ("core_identity", "descriptor from Airtable export")

    # Accept source_ledger (derived view — not a primary field)
    if path.startswith("source_ledger"):
        return ("metadata", "derived source ledger — regenerated from attestations")

    # GALLERY_ORIGIN — attestations from commercial_gallery / data_origin role.
    # Classified as 'gallery_origin': attributed but NOT authoritative.
    # This is distinct from unattributed AND from authority-backed fields.
    if path.startswith("attestations"):
        # Check if this attestation is from a non-citable origin source
        attestations = record.get("attestations", [])
        for att in attestations:
            if att.get("role") == "data_origin" and att.get("authoritative") is False:
                return ("gallery_origin",
                        "data_origin attestation — attributed but non-authoritative (commercial gallery)")
        return ("attestation", "attestation from citable source")

    # Accept sources and conflicts tracking
    if path.startswith("sources") or path.startswith("source_refs") or path.startswith("conflicts"):
        return ("core_identity", "cataloguing metadata")

    # 11. UNATTRIBUTED
    return ("unattributed", "field not attributed to any known source")


def audit_record(filepath: Path) -> Dict:
    """Audit a single record and return classification results."""
    with open(filepath) as f:
        record = json.load(f)
    
    record_id = record.get("artbase_id", filepath.stem)
    meta = record.get("_meta", {})
    
    # Flatten to get all leaf fields
    flat = flatten_dict(record)
    
    # Classify each field
    field_classifications = []
    source_counts = defaultdict(int)
    
    for path, value in sorted(flat.items()):
        source, reason = classify_field(path, value, record, meta)
        source_counts[source] += 1
        
        field_classifications.append({
            "path": path,
            "value": value,
            "source": source,
            "reason": reason
        })
    
    # Extract unattributed fields
    unattributed = [f for f in field_classifications if f["source"] == "unattributed"]
    
    return {
        "id": record_id,
        "file": str(filepath.relative_to(REPO_ROOT)),
        "fields_total": len(field_classifications),
        "fields_attributed": len(field_classifications) - len(unattributed),
        "fields_unattributed": len(unattributed),
        "source_counts": dict(source_counts),
        "unattributed_fields": unattributed,
        "all_fields": field_classifications
    }


def generate_reports(results: List[Dict], run_time: str, args):
    """Generate JSON, CSV, and Markdown reports."""
    REPORTS_DIR.mkdir(exist_ok=True)
    
    # Aggregate stats
    total_fields = sum(r["fields_total"] for r in results)
    total_unattributed = sum(r["fields_unattributed"] for r in results)
    total_attributed = total_fields - total_unattributed
    records_with_unattributed = sum(1 for r in results if r["fields_unattributed"] > 0)
    
    source_totals = defaultdict(int)
    for r in results:
        for source, count in r["source_counts"].items():
            source_totals[source] += count
    
    coverage_pct = (total_attributed / total_fields * 100) if total_fields > 0 else 0
    
    stats = {
        "run_completed": run_time,
        "stats": {
            "records_scanned": len(results),
            "fields_total": total_fields,
            "fields_attributed": total_attributed,
            "fields_unattributed": total_unattributed,
            "records_with_unattributed_fields": records_with_unattributed,
            "attribution_coverage_pct": round(coverage_pct, 1)
        },
        "by_source": dict(source_totals)
    }
    
    # A) JSON report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_file = REPORTS_DIR / f"provenance_audit_{timestamp}.json"
    
    json_report = {
        **stats,
        "records": [
            {
                "id": r["id"],
                "file": r["file"],
                "fields_unattributed": [
                    {
                        "path": f["path"],
                        "value": _preview_value(f["value"]),
                        "reason": f["reason"],
                        "recommendation": _recommend_action(f["path"], f["value"])
                    }
                    for f in r["unattributed_fields"]
                ]
            }
            for r in results if r["fields_unattributed"] > 0
        ]
    }
    
    with open(json_file, "w") as f:
        json.dump(json_report, f, indent=2, ensure_ascii=False)
        f.write("\n")
    
    # B) CSV report
    csv_file = REPORTS_DIR / f"provenance_audit_{timestamp}.csv"
    
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["record_id", "file", "field_path", "field_value_preview", "reason", "recommendation"])
        
        for r in results:
            for field in r["unattributed_fields"]:
                writer.writerow([
                    r["id"],
                    r["file"],
                    field["path"],
                    _preview_value(field["value"]),
                    field["reason"],
                    _recommend_action(field["path"], field["value"])
                ])
    
    # C) Markdown summary
    md_file = REPORTS_DIR / f"provenance_audit_summary.md"
    
    # Top 10 worst offenders
    top_offenders = sorted(
        [r for r in results if r["fields_unattributed"] > 0],
        key=lambda x: x["fields_unattributed"],
        reverse=True
    )[:10]
    
    md_content = f"""# Data Provenance Audit Summary

**Run Date:** {run_time}  
**Records Scanned:** {stats['stats']['records_scanned']}

## Overall Statistics

- **Total Fields:** {total_fields:,}
- **Attributed Fields:** {total_attributed:,}
- **Unattributed Fields:** {total_unattributed:,}
- **Records with Unattributed Data:** {records_with_unattributed}
- **Attribution Coverage:** {coverage_pct:.1f}%

## Attribution by Source

| Source | Field Count |
|--------|-------------|
"""
    
    for source, count in sorted(source_totals.items(), key=lambda x: x[1], reverse=True):
        md_content += f"| {source} | {count:,} |\n"
    
    if top_offenders:
        md_content += f"\n## Top 10 Records with Unattributed Fields\n\n"
        md_content += "| Rank | Record ID | Unattributed Fields | File |\n"
        md_content += "|------|-----------|---------------------|------|\n"
        
        for i, r in enumerate(top_offenders, 1):
            md_content += f"| {i} | {r['id']} | {r['fields_unattributed']} | `{r['file']}` |\n"
    
    if total_unattributed == 0:
        md_content += "\n## ✅ Clean Audit\n\nAll fields are properly attributed to known sources. No action needed.\n"
    else:
        md_content += f"\n## Next Steps\n\n"
        md_content += f"1. Review `{csv_file.name}` for the full list of unattributed fields\n"
        md_content += f"2. For each field, decide:\n"
        md_content += f"   - **(a) Delete** if it's demo residue or invalid data\n"
        md_content += f"   - **(b) Backfill** `_meta` attribution if legitimate\n"
        md_content += f"   - **(c) Move** to `_unverified` suffix until proper enrichment\n"
        md_content += f"3. Run `--strict` mode after cleanup to verify 100% coverage\n"
    
    with open(md_file, "w") as f:
        f.write(md_content)
    
    return json_file, csv_file, md_file


def _preview_value(value: Any, max_len: int = 60) -> str:
    """Generate a preview string for a value."""
    if isinstance(value, (list, dict)):
        s = json.dumps(value, ensure_ascii=False)
    else:
        s = str(value)
    
    if len(s) > max_len:
        return s[:max_len] + "..."
    return s


def _recommend_action(path: str, value: Any) -> str:
    """Generate a recommendation for handling an unattributed field."""
    if "iconography" in path:
        return "verify source; if demo data, delete OR move to iconography_unverified"
    elif "subject" in path and isinstance(value, list):
        return "map to AAT genre terms OR delete if demo keywords"
    elif "notes" in path or "description" in path:
        return "add source attribution OR delete if placeholder text"
    elif "provenance" in path:
        return "add source field to provenance entry"
    else:
        return "review origin; add _meta attribution OR delete if invalid"


def main():
    parser = argparse.ArgumentParser(description="Audit data provenance in canonical records")
    parser.add_argument("--record", help="Audit single record by ID")
    parser.add_argument("--strict", action="store_true", 
                       help="Exit 1 if any unattributed fields found")
    parser.add_argument("--by-source", help="Filter report to show only one source")
    parser.add_argument("--since", help="Only audit records modified after date (YYYY-MM-DD)")
    
    args = parser.parse_args()
    
    # Find records to audit
    if args.record:
        # Try both artists and artworks
        files = []
        artist_file = ARTISTS_DIR / f"{args.record}.json"
        artwork_file = ARTWORKS_DIR / f"{args.record}.json"
        
        if artist_file.exists():
            files = [artist_file]
        elif artwork_file.exists():
            files = [artwork_file]
        else:
            print(f"✗ Record not found: {args.record}")
            sys.exit(1)
    else:
        files = sorted(list(ARTISTS_DIR.glob("ART-*.json")) + 
                      list(ARTWORKS_DIR.glob("AP-*.json")))
    
    print(f"Auditing {len(files)} record(s)...")
    
    # Audit all records
    results = []
    for filepath in files:
        try:
            result = audit_record(filepath)
            results.append(result)
            
            if result["fields_unattributed"] > 0:
                print(f"  ⚠ {result['id']}: {result['fields_unattributed']} unattributed field(s)")
        except Exception as e:
            print(f"  ✗ {filepath.name}: {e}")
    
    # Generate reports
    run_time = datetime.now().isoformat()
    json_file, csv_file, md_file = generate_reports(results, run_time, args)
    
    total_unattributed = sum(r["fields_unattributed"] for r in results)
    total_fields = sum(r["fields_total"] for r in results)
    coverage = ((total_fields - total_unattributed) / total_fields * 100) if total_fields > 0 else 0
    
    print(f"\n✓ Audit complete")
    print(f"  Coverage: {coverage:.1f}% ({total_fields - total_unattributed}/{total_fields} fields attributed)")
    print(f"  Unattributed: {total_unattributed} fields in {sum(1 for r in results if r['fields_unattributed'] > 0)} records")
    print(f"\nReports written:")
    print(f"  JSON: {json_file.relative_to(REPO_ROOT)}")
    print(f"  CSV:  {csv_file.relative_to(REPO_ROOT)}")
    print(f"  MD:   {md_file.relative_to(REPO_ROOT)}")
    
    # Strict mode check
    if args.strict and total_unattributed > 0:
        print(f"\n✗ STRICT MODE: {total_unattributed} unattributed fields found")
        sys.exit(1)
    
    sys.exit(0)


if __name__ == "__main__":
    main()
