# Wikidata Contributions Queue

This directory contains QuickStatements batches for contributing ArtBase data to Wikidata.

## Files

- `queue_YYYYMMDD_HHMMSS.qs` — QuickStatements V1 format batch file
- `queue_YYYYMMDD_HHMMSS.review.md` — Human review document for that batch

## Status

All batches in this directory are PROPOSALS only. None are auto-submitted.

Submission requires:
1. Manual review of both .qs and .review.md files
2. Human login to https://quickstatements.toolforge.org/
3. Manual paste and "Run" action

## Audit trail

Every batch is committed to git alongside its review document. The review document is updated post-submission with:
- Batch ID
- Success/failure counts
- Verification notes

This creates a permanent audit record of all Wikidata contributions.

## Phase tracking

Current phase: **1** (external identifiers only)

Phase 1 properties:
- P7400: LNDB ID
- P245: Getty ULAN ID
- P214: VIAF ID
- P373: Commons category

See `docs/quickstatements_runbook.md` for operational procedures.
