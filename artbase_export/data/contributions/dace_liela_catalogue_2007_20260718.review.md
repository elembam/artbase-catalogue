# Dace Lielā catalogue (2007) — new book/exhibition-catalogue item
## 2026-07-18

**Phase:** book-item CREATE (source record for future S248/S304 references, not an artwork or artist batch)
**Operations:** 1 CREATE
**Statements proposed:** 12
**Properties used:** P31, P1476, P407 (×2), P577, P212, P123, P921, P50
**References:** none on this batch — this item's own statements are self-sourced (colophon/ISBN), not sourced to a third work

---

## Reconciliation — done, before this file was written

- [x] **Searched for an existing item** — by ISBN-13 (`978-9984-19-295-4`), by the ISBN-10 equivalent (`9984192954`), by title prefix, and by full-text search. Zero hits, all four methods. No duplicate risk.
- [x] **P31 QID verified** — the original draft proposed `Q105420117` as "best recall, verify." Checked: that QID is a 2012 taxonomy paper on Himalayan beetles, unrelated. Corrected to **Q780605** ("exhibition catalogue"), confirmed by label+description lookup. **Confirmed with Jakob 2026-07-18 that this is in fact an exhibition catalogue, not a plain book.**
- [x] **Publisher QID verified** — `Q20563094` ("Latvijas mākslinieku savienība", organization). Unambiguous top search match.
- [x] **Subject QID verified** — `Q99477354` ("Dace Liela", Latvian artist, occupation: visual artist). Cross-checked independently against the local store: `artbase_export/data/artists/ART-LIELA-1957.json` already carries this exact QID as `authority_links.wikidata`, `status: "confirmed"`, `verified_date: 2026-07-02`. Two independent paths agree.
- [x] **Author QID verified** — `Q109865282` ("Pēteris Bankovskis"), occupations "author" + "art historian" — fits a catalogue-text author.
- [x] **Bilingual claim confirmed with Jakob** 2026-07-18 — Latvian + English, both P407 lines kept.
- [x] **Every property ID checked** (not just item QIDs) — P31/P1476/P407/P577/P212/P123/P921/P50 all confirmed against their Wikidata labels.

## Pre-flight checklist (human must still complete before submitting)

- [ ] **Re-verify no duplicate appeared since 2026-07-18** — a few weeks' gap before submitting is enough that someone else could have created it; re-run the ISBN/title search immediately before running the batch.
- [ ] **Confirm the description text** (Den/Dlv) reads naturally — drafted from the ISBN/title/publisher facts on hand, not copied from the colophon itself (I don't have the scanned page in this session).

---

## Per-operation review

### CREATE — Dace Lielā. Gleznas. Katalogs
- **P31** Q780605 — exhibition catalogue (verified 2026-07-18, corrected from a wrong placeholder QID)
- **P1476** title, Latvian monolingual text
- **P407** ×2 — Latvian (Q9078) + English (Q1860), confirmed bilingual by Jakob
- **P577** publication date 2007 (year precision)
- **P212** ISBN-13 `978-9984-19-295-4`
- **P123** publisher — Latvijas mākslinieku savienība (Q20563094)
- **P921** main subject — Dace Lielā (Q99477354)
- **P50** author (of text) — Pēteris Bankovskis (Q109865282)
- **Risk:** LOW — no existing item found by four independent search methods; all QIDs independently verified, one cross-confirmed against the local store

### Deliberately excluded — production credits
Illustrator/compiler, photographer, designer, translator, editor were all in the original draft's "needs a QID" list except one (Baranovska, proposed P110 illustrator). Not included here: Wikidata has no clean property for "compiler," and stacking every production credit onto a catalogue item is over-granular for what reviewers expect on a book item. These belong in ArtBase's own `sources[]` record for this catalogue instead, once one exists — see "After submission" below.

---

## After submission

1. **Record the new QID** in `CONTRIBUTIONS_LOG.md`.
2. **Create a `SRC-*` registry record** for this catalogue in `artbase_export/data/sources/` (matching the `SRC-HANSABANKA-2007`/`SRC-LNMM-PORTRAITS-2009` pattern) with the confirmed QID — this session doesn't have the specific ArtBase artwork/passport(s) this catalogue is a source for, so that linking (and any `sources[]` entries citing it, including the production-credit fields excluded above) is a follow-up step for whoever has that context.
3. **Do not** treat this CREATE as satisfying any artwork's provenance citation on its own — it only establishes the book as a citable Wikidata entity; individual S248/S304 references on artwork statements still need their own page numbers confirmed, per the standing rule.

---

## Submission status

- Batch file: `dace_liela_catalogue_2007_20260718.qs`
- Submitted at: _______________
- Batch ID: _______________
- New QID: _______________
