# Instruction 20 — Integrate the Imago Mundi "Latvia, WOW!" Catalogue

*Hand to Copilot as a single ingestion component. Source: `catalogues-pdf_catalogue-latvia.pdf` — Imago Mundi, *Latvia, WOW! Contemporary Artists from Latvia* (Fondazione Benetton / Luciano Benetton, 2014), 227 pp., trilingual EN/LV/IT, InDesign-produced with a clean embedded text layer. Structure: one artist per spread (trilingual biography + one catalogued work with title×3, medium, dimensions, year), then a back index mapping artist → page → work. This is a **new source document** that (a) enriches existing artist records and (b) supplies ~200 catalogued works. The artists are **living contemporary artists** — Instruction 9 privacy and the living-artist Wikidata caution govern the whole job. Reconcile before creating; verify before publishing. Where this conflicts with Copilot's instinct, the spec wins — ask before deviating.*

---

## Purpose

Turn the catalogue into: one `Source_Documents` record; structured biography + a bibliographic citation added to matched artist records; ~200 artwork records (each the artist's Imago Mundi work); site surfacing on the relevant artist pages; and a **held-for-review** basis for later Wikidata give-back — without duplicating artists, inventing data, or exposing personal data of living people.

---

## Part A — Extract (against this PDF's real structure)

1. **Text layer is clean** (`pdftotext -layout`); do **not** OCR. Rasterize a page only to resolve a specific ambiguity.
2. **Parse the index first** (the pages listing `page → Name (EN) / Name (LV) / Work title ×3`). The index is the spine: it enumerates every artist, their spread page, and their work title, so use it to drive extraction and as a cross-check that no artist is missed.
3. **Per-artist spread** yields:
   - **Names**: English form and **Latvian form** (diacritics) — the Latvian form is the match key.
   - **Birth year** (printed top-right of each spread).
   - **Biography**: studies, solo exhibitions, group exhibitions — capture the **English and Latvian** text (skip Italian for storage; note it exists).
   - **The work**: title (EN/LV/IT), medium, dimensions, year (nearly all are `10 x 12 cm`, 2013–2014 — but read each; do not assume).
4. **Emit an extraction report**: N artists parsed, index-count vs spread-count reconciliation, and any spread that failed to parse — flag, never silently drop.

## Part B — The source-document record

Create one record `SRC-IMAGOMUNDI-LV-2014` (pattern of `SRC-HANSABANKA-2007`):
- title *Latvia, WOW! Contemporary Artists from Latvia*; series **Imago Mundi**; publisher **Fondazione Benetton Iniziative Culturali** (verify exact imprint); year **2014**; languages EN/LV/IT; **find the ISBN** (on the cover/colophon pages — inspect them; do not fabricate one).
- This single record is the citation target for every biography and work drawn from the catalogue.

## Part C — Reconcile artists to the store (living-artist caution)

1. Match each catalogue artist to existing artist JSONs by **Latvian name + birth year** (same matcher discipline as Instruction 19: ≥95% auto, everything ambiguous → review list). Expect substantial overlap with the existing Hansabanka/Latvian set (e.g. Heinrihsone, Ivanovs, Krastiņa, Kirke).
2. **Matched** artists: append the biography (as structured fields, EN+LV) and a citation to `SRC-IMAGOMUNDI-LV-2014` (page number from the index). Do **not** overwrite existing biographical facts — add, and flag any **conflict** (e.g. a differing birth year) for human resolution rather than choosing.
3. **Unmatched** artists (in catalogue, not in store): list them in a report. Do **not** auto-create artist records — creating living-person records is a decision for Jakob, made deliberately, not a bulk side effect.
4. **Privacy (Instruction 9):** biographies here are public professional facts (exhibitions, studies) and fine to record. Do **not** ingest or infer anything personal beyond what the catalogue prints. No home locations, no personal data.

## Part D — The works

For each artist's catalogue work, create an artwork record:
- title (EN + LV + IT-as-alt), maker → the matched artist, medium, dimensions, year — all from the page.
- **Provenance / holder**: the Imago Mundi / Fondazione Benetton collection (a recorded fact — the works were made for that collection). This is a **private-collection holder**, not a public object anchor; record it, don't overclaim it as an institutional anchor.
- source → `SRC-IMAGOMUNDI-LV-2014`, with page.
- **No image ingestion** unless the catalogue's rights permit it — the book's images are © the artists/photographers; treat as **rights-restricted** (link/describe, do not redistribute), per the Instruction 16 rights discipline. Never assume reusable.
- Only create the work record for an artist who **matched** (Part C) or whom Jakob has approved for creation; don't mint orphan works for unmatched artists.

## Part E — Surface on the site

- On each **matched artist page**: the new biography content and an Imago Mundi entry in the Sources section; the catalogue work listed among their works (with its holder noted).
- Regenerate artist pages and the sitemap afterward.
- **Depth, not breadth**: this adds real content to *existing* artist pages (good — it thickens exactly the thin pages GSC is deferring). Do **not** spin up ~200 new thin artist/work stubs for unmatched artists as indexable pages; unmatched artists stay in the report until Jakob decides.

## Part F — Wikidata eligibility (prepare, hold — no edits here)

- Mark biography facts and works with `wikidata_batch_eligible` per the Instruction 19 two-tier rule: a fact is eligible only if it's precise and sourced to the catalogue with a page.
- **Living-artist caution**: for a living person, prefer sourced, uncontroversial statements; do **not** batch anything sensitive. This is Phase-2 material, a separate instruction, human-reviewed QuickStatements only — **generate nothing to Wikidata in this instruction.**
- The catalogue *is* a citable source (`P1343`/`S248` once it has a Wikidata book item) — creating that book item (reconcile-first by ISBN) is a clean later contribution, not part of this job.

## What this component does NOT do

- Does **not** OCR (clean text layer exists).
- Does **not** auto-create artist records for unmatched living people, or overwrite existing biographical facts.
- Does **not** ingest or redistribute the catalogue's images (rights-restricted).
- Does **not** treat the Imago Mundi/Benetton holder as a public object anchor.
- Does **not** publish ~200 new thin stubs, or make any Wikidata edit.
- Does **not** invent an ISBN, a page, or a birth year — absent data stays a flagged gap.

## Done criteria

1. Extraction report: artists parsed, index-vs-spread reconciliation, parse failures flagged.
2. `SRC-IMAGOMUNDI-LV-2014` created (with real ISBN, or ISBN flagged as not-found).
3. Match report: matched (≥95%), review-needed, unmatched — with any birth-year conflicts flagged.
4. Matched artist records enriched (biography + citation, additive) and their catalogue works created with holder + source; artist pages and sitemap regenerated.
5. `wikidata_batch_eligible` counts reported as the Phase-2 input; no Wikidata edits made.
