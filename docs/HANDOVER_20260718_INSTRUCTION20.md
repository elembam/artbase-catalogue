# ArtBase Session Handover — Instruction 20 (Imago Mundi Latvia)

**Date:** 2026-07-18  
**Spec:** `ArsAccordiaClaude/copilot-spec-20-imago-mundi-catalogue.md`  
**Latest commit:** `c896967` (pushed to `main`)

---

## What was completed against Spec 20

### 1) Source and extraction assets
- Added source record: `artbase_export/data/sources/SRC-IMAGOMUNDI-LV-2014.json`
- Added extraction/reference files under `ArsAccordiaClaude/References/`:
  - `catalogues-pdf_catalogue-latvia.pdf`
  - `imago-mundi-latvia-2014.json`
  - `imago-mundi-latvia-2014-corrected.json`

### 2) Spot-check before writes
- Completed spot-check of 5 matched artists against raw PDF text (as requested before writes).

### 3) Matched-artist enrichment
- Enriched **31 matched artists** with:
  - EN + LV biography block
  - citation linkage to `SRC-IMAGOMUNDI-LV-2014`
  - source references in artist JSONs
- Regenerated corresponding **31 artist pages**.

### 4) Artwork creation
- Created **31 artwork JSON records** (`AP-2026-000337` … `AP-2026-000367`) with:
  - Imago Mundi holder/collection note
  - rights-restricted handling
  - no image ingestion
- Generated **31 new passport HTML pages** for those works.

### 5) Site regeneration
- Regenerated sitemap (`sitemap.xml`).
- Current dry-run count: **731 URLs** (366 passports, 354 artist pages).

### 6) Reporting deliverables
- Added report:  
  `artbase_export/data/contributions/instruction20_imago_reconciliation_reports_20260718.md`
- Report includes:
  - **130-unmatched contemporary-gap map** (no records created)
  - **23 review-queue conflicts** for human resolution (untouched)
  - explicit note that **HTML-without-JSON gap is deferred to Instruction 21** (untouched)

---

## Important implementation notes for next Copilot

1. **Artist biography placement mismatch exists**
   - Canonical Pydantic model (`artbase_export/src/artbase_export/canonical/models.py`) formally defines artist summary at:
     - `descriptors.biography_summary`
   - Imago batch currently stores richer bilingual text in top-level:
     - `biography.en`, `biography.lv`, with source/page metadata
   - This is currently in committed data and rendered pages; treat as current working reality unless/until schema migration is explicitly commissioned.

2. **Validation baseline is not clean for this dataset**
   - `pytest` passes.
   - Full `artbase_export validate` reports schema/status mismatches on existing/new records (not all caused by this single step).
   - Do not assume a fully strict-model-clean baseline yet.

3. **Living-artist safeguards were preserved**
   - No bulk creation of unmatched living-artist records.
   - No Wikidata writes performed as part of this instruction.
   - Image ingestion remained disabled for rights reasons.

---

## Files most relevant to continue Instruction 20

- Spec: `ArsAccordiaClaude/copilot-spec-20-imago-mundi-catalogue.md`
- Source document record: `artbase_export/data/sources/SRC-IMAGOMUNDI-LV-2014.json`
- Extracted dataset: `ArsAccordiaClaude/References/imago-mundi-latvia-2014-corrected.json`
- Reconciliation/gap report:  
  `artbase_export/data/contributions/instruction20_imago_reconciliation_reports_20260718.md`
- Changed artist canonical JSONs: `artbase_export/data/artists/ART-*.json` (31 Imago-enriched records)
- New artwork canonical JSONs: `artbase_export/data/artworks/AP-2026-000337.json` … `AP-2026-000367.json`
- Generated artist pages: `artists/ART-*.html` (31 regenerated)
- Generated passports: `AP-2026-000337.html` … `AP-2026-000367.html`
- Sitemap: `sitemap.xml`

---

## Recommended next actions (if Instruction 20 follow-up is requested)

1. Resolve the **23 review-queue conflicts** one-by-one with human decisions.
2. Decide whether to normalize bilingual biography storage into schema-managed structure (migration task, separate instruction).
3. Execute deferred **Instruction 21** work for HTML-without-JSON consistency gap.
4. If needed, produce a Phase-2 readiness subset for Wikidata (`wikidata_batch_eligible`) with strict page-backed sourcing only.

