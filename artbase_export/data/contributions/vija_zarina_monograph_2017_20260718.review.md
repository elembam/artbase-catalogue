# Vija Zariņa monograph (2017, Neputns) — new book item
## 2026-07-18

**Phase:** book-item CREATE (source record, same pattern as `dace_liela_catalogue_2007_20260718`)
**Operations:** 1 CREATE
**Statements proposed:** 11
**Properties used:** P31, P1476, P407 (×2), P577, P212, P123, P921, P50
**References:** none on this batch — self-sourced from the colophon transcription supplied 2026-07-18

---

## Reconciliation — done, before this file was written

- [x] **Searched for an existing item** — by ISBN-13 (`978-9934-565-23-6`), by the ISBN-10 equivalent (`9934565234`), and by full-text search on title+publisher+year. Zero hits, all three methods. No duplicate risk.
- [x] **P31 corrected from the draft's implicit assumption.** The draft note called this a "monograph," not an exhibition catalogue — right call, the colophon has no exhibition venue, dates, or curator anywhere, unlike the Dace Lielā catalogue. Used **Q193495** ("monograph"), not Q780605 ("exhibition catalogue") or the generic Q571 ("book").
- [x] **Publisher QID verified** — **Q30212561** (Neputns). Confirmed two ways: top Wikidata search match, and this exact QID is already in use in this repo at `artbase_export/data/sources/SRC-LNMM-PORTRAITS-2009.json` as Neputns's publisher QID.
- [x] **Subject QID verified** — **Q50359512** ("Vija Zariņa — Latvian painter, born 1961"). Confirmed two ways: matches the Wikidata search, and `artbase_export/data/artists/ART-ZARINA-1961.json` already carries this exact QID as `authority_links.wikidata`, `status: "confirmed"`, `verified_date: 2026-06-16`.
- [x] **Compiler/text-author QID verified** — **Q18218430** (Ieva Rupenheite, "Latvian writer," occupation writer, citizenship Latvia). She holds two roles per the colophon (Sastādītāja/Compiler *and* one of two Tekstu autori/Authors of texts) — used as P50 (author) for the text-author role; the compiler role has no clean Wikidata property and isn't separately modelled (see exclusions below).
- [x] **Second text author checked and excluded** — Anda Treija's only Wikidata search match (Q133649915) is a bare item: no description, no occupation, no citizenship, nothing to confirm it's the same Anda Treija who co-wrote this book's text rather than a namesake. Not included. If you know her correct QID independently, it can be added later — not guessed here.
- [x] **Every property ID reused from the Dace Lielā batch** (P31, P1476, P407, P577, P212, P123, P921, P50) — already verified against Wikidata labels in that batch; same properties, not re-checked individually here since nothing about their meaning changes between batches.

## Pre-flight checklist (human must still complete before submitting)

- [ ] **Re-verify no duplicate appeared since 2026-07-18** — re-run the ISBN/title search immediately before submitting.
- [ ] **Anda Treija** — if you have or can find her correct QID, add a second P50 line; don't let this batch stand in as "done" on text authorship if you want her credited on Wikidata too.
- [ ] **Confirm the description text** (Den/Dlv) — drafted from the colophon facts on hand (title, publisher, year, subject), not a copy of any existing back-cover description.

---

## Per-operation review

### CREATE — Vija Zariņa (monograph)
- **P31** Q193495 — monograph (not exhibition catalogue — no exhibition evidenced in the colophon)
- **P1476** title, Latvian monolingual text
- **P407** ×2 — Latvian (Q9078) + English (Q1860); colophon shows parallel LV/EN text throughout (editor, translator, and proof-reader of English all separately credited)
- **P577** publication date 2017 (year precision)
- **P212** ISBN-13 `978-9934-565-23-6`
- **P123** publisher — Neputns (Q30212561)
- **P921** main subject — Vija Zariņa (Q50359512)
- **P50** author (of text) — Ieva Rupenheite (Q18218430)
- **Risk:** LOW — no existing item found by three independent search methods; publisher and subject QIDs each cross-confirmed against this repo's own existing data, not just a fresh search

### Deliberately excluded — production credits
Per the colophon: language editor (Cilda Redliha), English translator (Filips Birzulis), English proof-reader (Iveta Boiko), designer (Anna Aizsilniece), image processor (Jānis Veiss), seven photographers, the publisher's director and chief editor, and the printer (Jelgavas tipogrāfija) — none included, same reasoning as the Dace Lielā batch: Wikidata has no clean property for most of these roles, and stacking every production credit onto a book item reads as over-granular. These belong in ArtBase's own `sources[]`/`SRC-*` record for this monograph, which has all the colophon detail this .qs file deliberately doesn't.

### Not created here — the cover artwork
The colophon documents a fully identified cover work — *Garām ejot (Pašportrets)* / *Passing by (Self-Portrait)*, 2015, oil on canvas, 45 × 30 cm, artist's property, photo credit Normunds Brasliņš. That's a real, catalogueable ArtBase passport candidate (title in two languages, date, medium, dimensions, holder), but it's a private-collection work (holder = "artist's property," not a public anchor) and creating a passport is a separate, larger step than this book-item batch. Flagging it here rather than acting on it — say the word if you want that done as its own task.

---

## After submission

1. **Record the new QID** in `CONTRIBUTIONS_LOG.md`.
2. **Create a `SRC-*` registry record** in `artbase_export/data/sources/` (matching the `SRC-HANSABANKA-2007` pattern) with the confirmed QID, and the full colophon detail (compiler, both text authors, editor, translator, proof-reader, designer, photographers, printer) that this Wikidata item deliberately omits.
3. **Do not** treat this CREATE as sourcing any specific ArtBase artwork's provenance on its own — same rule as the Dace Lielā batch.

---

## Submission status

- Batch file: `vija_zarina_monograph_2017_20260718.qs`
- Submitted at: _______________
- Batch ID: _______________
- New QID: _______________
