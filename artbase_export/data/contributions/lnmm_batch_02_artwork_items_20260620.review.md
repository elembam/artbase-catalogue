# LNMM Batch 02 — Artwork items (1 enrichment + 4 CREATEs)
## 2026-06-20

**Phase:** 2 (artwork items — collection, inventory, dimensions, creator)
**Operations:** 1 enrichment (Q22043968) + 4 CREATE
**Statements proposed:** 4 + (4 × 11) = 48 total
**Properties used:** P31, P170, P571, P186, P195, P217, P2048, P2049
**References:** S248 (stated in: LNMM portraits book) + S304 (page) — PLACEHOLDERS until book is in hand
**Excludes:** 012 (Folk Festival at Kokmuiža) — attribution not yet individually verified against museum record

---

## Pre-flight checklist (human must complete before submitting)

- [x] **QLNMM_INSTITUTION resolved** → **Q1370465** (Latvian National Museum of Art). Confirmed 2026-06-20; substituted in batch file.
- [x] **QLNMM_PORTRAITS_2009 resolved** → **Q139986481** ("Artist. Portrait. Self-portrait"). Already on Wikidata; replaced in batch file 2026-06-20. `books_batch1_20260530.qs` no longer needed for this batch.
- [ ] **Confirm page numbers for S304** — check Lamberga 2009 for each work. If a page cannot be confirmed, remove the S248/S304 pair from that statement rather than inventing a number.
- [ ] **Check each target item** for existing statements — especially Q22043968 (Princess with a Monkey): does it already have P195, P217, P2048, P2049? Do not duplicate.
- [ ] **Verify no duplicates** on Wikidata for the four CREATE works — search by title + creator before submitting.
- [ ] **Add Latvian labels** (Llv) for each CREATE item — the .qs file leaves these blank; add them if known.

---

## Per-operation review

### Q22043968 — Princess with a Monkey (ENRICH)
**Wikidata item:** https://www.wikidata.org/wiki/Q22043968
- **Artist:** Janis Rozentāls (Q975168) — confirmed
- **Date:** 1913
- **Materials:** Oil on canvas (not included — already present on item, skip)
- **Adding:**
  - P195 QLNMM_INSTITUTION — "held by"
  - P217 "VMM GL-5668" — inventory number
  - P2048 147.5 cm — height
  - P2049 71.0 cm — width
- **Reference on each:** S248 QLNMM_PORTRAITS_2009 + S304 PAGE_TO_CONFIRM
- **Risk:** LOW — item exists, well-documented; adding collection/inventory/dimensions

---

### 004 — Carousel (CREATE)
**Artist:** Jānis Tīdemanis (Q4457149, confirmed 2026-06-15)
**Date:** 1932 · **Medium:** Oil on canvas · **Dimensions:** 65 × 95 cm · **Inv:** VMM GL-2822
- P31: Q3305213 (painting)
- P170: Q4457149 (Jānis Tīdemanis)
- P571: 1932 (year precision)
- P186: Q296955 (oil paint) + Q4259259 (canvas)
- P2048/2049: 65 × 95 cm
- P195: QLNMM_INSTITUTION
- P217: VMM GL-2822
- **English label:** "Carousel" · **Description:** "1932 painting by Jānis Tīdemanis"
- **Latvian label:** ADD — likely "Karuselis" — **verify before submitting**
- **Risk:** LOW — 20th-century non-living artist; work not yet on Wikidata (verify with search)

---

### 006 — From Church (After the Service) (CREATE)
**Artist:** Janis Rozentāls (Q975168, confirmed)
**Date:** 1894 · **Medium:** Oil on canvas · **Dimensions:** 175 × 103 cm · **Inv:** VMM GL-55
- P31: Q3305213
- P170: Q975168
- P571: 1894
- P186: Q296955 + Q4259259
- P2048/2049: 175 × 103 cm
- P195: QLNMM_INSTITUTION
- P217: VMM GL-55
- **English label:** "From Church (After the Service)"
- **Latvian label:** ADD — likely "No baznīcas (pēc dievkalpojuma)" — **verify**
- **Note:** This work was listed in earlier draft batch `qs_tier2_rozentals.txt` as a priority CREATE. Now formalised here with complete data.
- **Risk:** LOW — major Latvian work by well-documented artist; pre-draft confirmed no existing item

---

### 017 — Young Gipsy Woman (CREATE)
**Artist:** Kārlis Hūns (Q4152126, confirmed 2026-06-15)
**Date:** 1870 · **Medium:** Oil on canvas · **Dimensions:** 125 × 90 cm · **Inv:** VMM GL-1509
- P31: Q3305213
- P170: Q4152126
- P571: 1870
- P186: Q296955 + Q4259259
- P2048/2049: 125 × 90 cm
- P195: QLNMM_INSTITUTION
- P217: VMM GL-1509
- **English label:** "Young Gipsy Woman" · **Description:** "1870 painting by Kārlis Hūns"
- **Latvian label:** ADD — likely "Jauna čigāniete" — **verify**
- **Risk:** LOW — 19th-century Baltic German painter; figure painting well within scope

---

### 019 — Country Landscape (CREATE)
**Artist:** Jūlijs Feders (Q1977258, confirmed 2026-06-15)
**Date:** 1880 · **Medium:** Oil on canvas · **Dimensions:** 80 × 120 cm · **Inv:** VMM GL-1501
- P31: Q3305213
- P170: Q1977258
- P571: 1880
- P186: Q296955 + Q4259259
- P2048/2049: 80 × 120 cm
- P195: QLNMM_INSTITUTION
- P217: VMM GL-1501
- **English label:** "Country Landscape" · **Description:** "1880 painting by Jūlijs Feders"
- **Latvian label:** ADD — likely "Lauku ainava" — **verify**
- **Note:** Provenance citation to Lamberga 2009 removed from ArtBase record (landscape ≠ portraits catalogue). If page number cannot be confirmed, remove S248/S304 from all 019 statements.
- **Risk:** LOW — 19th-century Latvian landscape painter, confirmed QID

---

## 012 — Folk Festival at Kokmuiža (EXCLUDED from this batch)

**Excluded because:** attribution to Kārlis Hūns (Q4152126) is not yet individually verified against the LNMM museum record. The ArtBase record carries a gap flag on provenance and a note that the book citation has been removed.

**To unblock:** Confirm attribution via LNMM museum catalogue or direct museum contact. Once confirmed, add a third CREATE block to this batch (or a follow-up batch) with the same structure as 017 above, using VMM Z-4128 (Watercolour on paper, 21.7 × 27.3 cm, 1855).

---

## After submission

1. **Record QIDs** returned for the 4 CREATE items in `CONTRIBUTIONS_LOG.md` and in each passport's `authority_links.wikidata` block.
2. **Update passports** 004, 006, 017, 019: set `authority_links.wikidata.id = <new QID>`, `status = "confirmed"`, `verified_date = <date>`.
3. **Recompute scores:** `python3 scripts/build_passport_score.py --all` — each work gains a work-level authority link (fill rises from 0.5 to 1.0 for 1-authority works, scores rise from 63/88 to 75/100).
4. **Recompute collection:** `python3 scripts/build_collection_score.py COL-LNMM --check` — confirm Σ = new headline.
5. **Update LNMM collection page** with new scores and Wikidata item links per work.
6. **Register in Mix'n'match #8050** — see `lnmm_batch_02_mixnmatch_20260620.md`.

---

## Submission status

- Batch file: `lnmm_batch_02_artwork_items_20260620.qs`
- Submitted at: _______________
- Batch ID: _______________
- Q22043968 (enrich) result: _______________
- 004 new QID: _______________
- 006 new QID: _______________
- 017 new QID: _______________
- 019 new QID: _______________
