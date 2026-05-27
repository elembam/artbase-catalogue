# Data Provenance Audit Summary

**Run Date:** 2026-05-27T20:46:36.964951  
**Records Scanned:** 291

## Overall Statistics

- **Total Fields:** 13,524
- **Attributed Fields:** 13,523
- **Unattributed Fields:** 1
- **Records with Unattributed Data:** 1
- **Attribution Coverage:** 100.0%

## Attribution by Source

| Source | Field Count |
|--------|-------------|
| empty | 5,112 |
| core_identity | 3,779 |
| authority_id_without_pipeline_proof | 1,568 |
| authority_id | 1,035 |
| wikidata_enrichment | 972 |
| tier1_field_without_enrichment_run | 696 |
| metadata | 263 |
| ulan_enrichment | 66 |
| aat_field_without_linking_run | 20 |
| iconclass_enriched_no_timestamp | 12 |
| unattributed | 1 |

## Top 10 Records with Unattributed Fields

| Rank | Record ID | Unattributed Fields | File |
|------|-----------|---------------------|------|
| 1 | AP-2026-000001 | 1 | `artbase_export/data/artworks/AP-2026-000001.json` |

## Next Steps

1. Review `provenance_audit_20260527_204636.csv` for the full list of unattributed fields
2. For each field, decide:
   - **(a) Delete** if it's demo residue or invalid data
   - **(b) Backfill** `_meta` attribution if legitimate
   - **(c) Move** to `_unverified` suffix until proper enrichment
3. Run `--strict` mode after cleanup to verify 100% coverage
