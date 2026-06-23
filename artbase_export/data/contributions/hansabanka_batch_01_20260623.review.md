# Hansabanka Batch 01 — Pre-flight Review
## 2026-06-23

**Phase:** 1 (6 CREATE items)
**Source:** Q139986317 — Hansabanka Contemporary Art Collection catalogue, 2007
**Pages:** 222, 226, 228, 229
**Properties:** P31, P170, P571, P186, P2048, P2049
**References:** S248 Q139986317 + S304 (actual page number from catalogue)

---

## Pre-flight checklist (human must complete before submitting)

### Artist QIDs — resolve all before submitting

- [x] **Ilmārs Blumbergs → Q13611050** — confirmed 2026-06-23
- [x] **Džemma Skulme → Q4422700** — confirmed 2026-06-23
- [x] **Indulis Zariņš → Q13561029** — confirmed 2026-06-23
- [x] **Rūdolfs Pinnis → Q55984280** — confirmed 2026-06-23
- [x] **Vija Maldupe → Q113216930** — confirmed 2026-06-23

---

### Duplicate check — search Wikidata before submitting each CREATE

- [ ] **Work 1** — "Verities of Suffering" / "Ciešanu atziņas" (Blumbergs, 1999): search by title + creator
- [ ] **Work 2** — "The Silver Age" / "Sudraba laikmets" (Blumbergs, 1998): search by title + creator
- [ ] **Work 3** — "Caryatid (Scare-Crow)" / "Kariatīde" (Skulme, 2004): search by title + creator
- [ ] **Work 4** — "In Memory of Chagall" / "Šagāla piemiņai" (Zariņš, 1996): search by title + creator
- [ ] **Work 5 — PRIORITY CHECK** — "The Belly of Paris" (Shemyakin, 1976): Shemyakin is internationally documented. Search Wikidata thoroughly. **If an item already exists, convert Work 5 from CREATE to ENRICH** (add P2048, P2049, P195 if the Hansabanka collection has a QID).
- [ ] **Work 6** — "Carnival" / "Karnevāls" (Maldupe, 1977): search by title + creator

---

### Material QIDs — verify if uncertain

| Code used | QID | Meaning | Confidence |
|---|---|---|---|
| Q11472 | paper | Material support for prints | High |
| Q296955 | oil paint | Oil medium | High |
| Q4259259 | canvas | Textile support | High |
| Q614700 | cardboard | Cardboard support (Skulme work) | Medium — verify |
| Q11060274 | print | Instance of: print (screen-print works) | High |
| Q185511 | lithograph | Instance of: lithograph (Šemjakins work) | High |
| Q3305213 | painting | Instance of: painting (oil works) | High |

---

## Per-work data summary

### Work 1 — Ilmārs Blumbergs, "Verities of Suffering", 1999
- Latvian: *Ciešanu atziņas*
- Medium: screen-print, pencil on paper
- Dimensions: 61 (h) × 90.5 (w) cm
- Catalogue no. 32 · page 222
- P31: Q11060274 (print)
- P186: Q11472 (paper)
- Risk: LOW

### Work 2 — Ilmārs Blumbergs, "The Silver Age", 1998
- Latvian: *Sudraba laikmets*
- Medium: screen-print on paper
- Dimensions: 59 (h) × 89 (w) cm
- Catalogue no. 33 · page 222
- P31: Q11060274 (print)
- P186: Q11472 (paper)
- Risk: LOW

### Work 3 — Džemma Skulme, "Caryatid (Scare-Crow)", 2004
- Latvian: *Kariatīde. (Putnu biedēklis)*
- Medium: oil, collage on cardboard
- Dimensions: 150 (h) × 120 (w) cm
- Catalogue no. 171 · page 228
- Date note: catalogue gives "2004/2006" — 2004 used as inception year
- P31: Q3305213 (painting)
- P186: Q296955 (oil paint) + Q614700 (cardboard)
- Risk: LOW

### Work 4 — Indulis Zariņš, "In Memory of Chagall", 1996
- Latvian: *Šagāla piemiņai*
- Medium: oil on canvas
- Dimensions: 112 (h) × 96 (w) cm
- Catalogue no. 209 · page 229
- P31: Q3305213 (painting)
- P186: Q296955 + Q4259259
- Risk: LOW

### Work 5 — Rūdolfs Pinnis, "Folk-Style Totem", 1989
- Latvian: *Tautisks totēms*
- Medium: oil and gold on canvas
- Dimensions: 150 (h) × 180 (w) cm
- Catalogue no. 150 · page 227
- Artist QID: Q55984280 (confirmed 2026-06-23)
- P31: Q3305213 (painting)
- P186: Q296955 (oil paint) + Q4259259 (canvas) + Q31020 (gold)
- Risk: LOW

### Work 6 — Vija Maldupe, "Carnival", 1977
- Latvian: *Karnevāls*
- Medium: oil on canvas
- Dimensions: 79 (h) × 94 (w) cm
- Catalogue no. 121 · page 226
- Note: 1977 = Soviet period. Maldupe Wikidata QID status unknown.
- P31: Q3305213 (painting)
- P186: Q296955 + Q4259259
- Risk: LOW (if artist QID exists); BLOCKED if artist has no Wikidata item yet

---

## Open question: Hansabanka collection QID

The works are held by the Hansabanka / Swedbank art collection. No confirmed QID for this
collection as an institution has been identified. P195 (held by) has been omitted from this batch.

To add P195 in a follow-up batch:
1. Search Wikidata for the Hansabanka or Swedbank Latvia art collection.
2. If no item exists, consider creating one (corporate art collection item).
3. Then add `LAST  P195  <QID>  S248  Q139986317  S304  "<page>"` to each work.

---

## After submission

1. Record QIDs returned for the 6 CREATE items in `CONTRIBUTIONS_LOG.md`.
2. Create ArtBase passport JSONs for each work (AA/LV/HANS/001–006).
3. Run `python3 scripts/build_passport_score.py --all`.
4. Build scored collection page for the Hansabanka slice.

---

## Submission status

| Work | QID | Submitted |
|---|---|---|
| Work 1 — Ciešanu atziņas (Blumbergs 1999) | _TBD_ | ___ |
| Work 2 — Sudraba laikmets (Blumbergs 1998) | _TBD_ | ___ |
| Work 3 — Kariatīde (Skulme 2004) | _TBD_ | ___ |
| Work 4 — Šagāla piemiņai (Zariņš 1996) | _TBD_ | ___ |
| Work 5 — Parīzes vēders (Šemjakins 1976) | _TBD_ | ___ |
| Work 6 — Karnevāls (Maldupe 1977) | _TBD_ | ___ |
