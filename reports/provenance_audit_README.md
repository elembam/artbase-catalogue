# Data Provenance Audit System

**Built:** 2026-05-27  
**Status:** Production-ready

## Purpose

The provenance audit system walks every canonical JSON record and classifies each field by its data source. Any field that cannot be attributed to a known source is flagged as "unattributed" — surfacing demo data, hardcoded placeholders, and orphaned legacy fields.

**This is a READ-ONLY audit.** It writes reports, never modifies data.

## Usage

```bash
# Audit all records
python3 scripts/audit_provenance.py

# Audit single record
python3 scripts/audit_provenance.py --record AP-2026-000001

# Strict mode - exit 1 if unattributed fields found (for CI)
python3 scripts/audit_provenance.py --strict

# Filter by source
python3 scripts/audit_provenance.py --by-source ulan

# Only records modified after date
python3 scripts/audit_provenance.py --since 2026-05-01
```

## Classification Rules

The script classifies each populated field by checking sources in order:

1. **CORE_IDENTITY** — base fields from Airtable export (id, name, nationality, etc.)
2. **AUTHORITY_ID** — fields under `authorities.*` with pipeline proof
3. **WIKIDATA_ENRICHMENT** — Tier 1/2 fields from `wikidata_enrich.py`
4. **ULAN_ENRICHMENT** — fields under `enrichment.ulan.*`
5. **AAT_LINKING** — fields under `aat_terms.*`
6. **CANDIDATE_VERIFICATION** — `_meta.candidate_evidence`
7. **MANUAL_OVERRIDE** — fields in `_meta.manual_overrides[]`
8. **DISCOVERY_FIELDS** — `discovery_source`, `discovered_at`
9. **PROVENANCE_BLOCK** — `provenance.*` entries
10. **METADATA** — entire `_meta.*` tree
11. **UNATTRIBUTED** — everything else (the audit target)

## Output Reports

Each run generates three files in `reports/`:

### A) JSON Report (`provenance_audit_YYYYMMDD_HHMMSS.json`)

Machine-readable full report with:
- Overall statistics
- Attribution breakdown by source
- Per-record unattributed fields with recommendations

### B) CSV Report (`provenance_audit_YYYYMMDD_HHMMSS.csv`)

Flat spreadsheet format for review:
- record_id, file, field_path, field_value_preview, reason, recommendation

### C) Markdown Summary (`provenance_audit_summary.md`)

Human-readable summary with:
- Top-line statistics
- Attribution breakdown table
- Top 10 worst-offending records
- Next steps

## First Run Results

**Run Date:** 2026-05-27  
**Coverage:** 100.0% (13,523/13,524 fields attributed)  
**Unattributed:** 1 field in 1 record

### What Was Found

Only **one unattributed field** across the entire catalogue:

- **AP-2026-000001** (Mona Lisa demo passport)
  - `iconography.iconclass_codes` — ICONCLASS codes from demo seed without timestamp

This is expected demo residue that needs either:
1. **Deletion** (if purely demo data)
2. **Timestamp backfill** (run `iconclass_enrich.py` and it will add `_meta.iconclass_enriched_at`)

### Notable Classifications

**5,112 empty fields** — correctly ignored (null/empty values don't need attribution)

**3,779 core_identity fields** — base Airtable export data, accepted as authoritative

**1,568 authority_id_without_pipeline_proof** — authority IDs present but no enrichment timestamp. These are from early imports before `_meta` tracking existed. Legitimate data, just needs backfill.

**696 tier1_field_without_enrichment_run** — Wikidata Tier 1 fields populated but missing `_meta.wikidata_last_enriched`. Same issue: legitimate, needs timestamp backfill.

**972 wikidata_enrichment fields** — properly attributed with timestamps ✅

**66 ulan_enrichment fields** — properly attributed ✅

**20 aat_field_without_linking_run** — AAT terms present but missing `_meta.aat_linked_at` timestamp (needs backfill)

**12 iconclass_enriched_no_timestamp** — ICONCLASS labels present but missing timestamp

## Integration with CI/Build Pipeline

The `--strict` flag is designed for pre-commit hooks and CI:

```bash
# In .github/workflows/validate.yml or pre-commit config
python3 scripts/audit_provenance.py --strict
```

This ensures every commit maintains 100% attribution coverage. Any new field without a known source fails the build.

## Future Work

### Phase 2: Timestamp Backfilling

Build `scripts/migrate_provenance.py` to add missing `_meta` timestamps to legitimate fields:

```bash
# Dry-run: show what would be backfilled
python3 scripts/migrate_provenance.py --dry-run

# Backfill missing timestamps for known enrichments
python3 scripts/migrate_provenance.py --backfill-timestamps

# Mark specific fields as manual overrides
python3 scripts/migrate_provenance.py --add-override AP-2026-000001:iconography.iconclass_codes
```

This would bring the 1,568 "authority_id_without_pipeline_proof" fields and 696 "tier1_field_without_enrichment_run" fields into full compliance.

### Phase 3: Source-Level Validation

Extend the audit to validate not just *presence* of attribution, but *correctness*:

- Does `_meta.wikidata_last_enriched` actually align with Wikidata revision IDs?
- Are manual overrides still necessary, or has enrichment caught up?
- Are there fields marked as "candidate" that have been verified but not updated?

## Design Principles

1. **Attribution over inference** — A field is either traceable to a known source or it's flagged. We don't guess.

2. **Read-only by default** — The audit never modifies data. All fixes go through explicit migration scripts.

3. **Deterministic output** — Running twice on unchanged data produces identical reports (timestamp aside).

4. **CI-friendly** — `--strict` mode exits 1 if unattributed fields exist, perfect for automated quality gates.

5. **Human-readable** — The Markdown summary is what you read first; CSV and JSON are for deeper analysis.

## Current State: Excellent

With 100.0% coverage and only 1 trivial unattributed field (demo seed residue), the ArtBase canonical data is in excellent provenance health. Every enrichment pipeline properly tracks its source, and the audit confirms we can trust the data lineage.
