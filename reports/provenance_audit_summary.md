# Data Provenance Audit Summary

**Run Date:** 2026-05-30T10:38:23.110361  
**Records Scanned:** 1

## Overall Statistics

- **Total Fields:** 98
- **Attributed Fields:** 93
- **Unattributed Fields:** 5
- **Records with Unattributed Data:** 1
- **Attribution Coverage:** 94.9%

## Attribution by Source

| Source | Field Count |
|--------|-------------|
| metadata | 36 |
| empty | 17 |
| core_identity | 15 |
| authority_id | 9 |
| gallery_origin | 8 |
| wikidata_enrichment | 8 |
| unattributed | 5 |

## Top 10 Records with Unattributed Fields

| Rank | Record ID | Unattributed Fields | File |
|------|-----------|---------------------|------|
| 1 | ART-AIDE-1913 | 5 | `artbase_export/data/artists/ART-AIDE-1913.json` |

## Next Steps

1. Review `provenance_audit_20260530_103823.csv` for the full list of unattributed fields
2. For each field, decide:
   - **(a) Delete** if it's demo residue or invalid data
   - **(b) Backfill** `_meta` attribution if legitimate
   - **(c) Move** to `_unverified` suffix until proper enrichment
3. Run `--strict` mode after cleanup to verify 100% coverage
