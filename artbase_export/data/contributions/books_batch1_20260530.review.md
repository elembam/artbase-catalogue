# Wikidata Books Batch 1 — Review Checklist

Generated: 2026-05-30  
Contributor account: ArsAccordia  
Batch file: `books_batch1_20260530.qs`

---

## Items to create

| # | Source ID | Title (lv) | ISBN-13 | Status |
|---|-----------|-----------|---------|--------|
| 1 | SRC-HANSABANKA-2007 | Hansabankas mūsdienu mākslas kolekcija | 978-9984-39-381-0 | `to_create` |
| 2 | SRC-LNMM-PORTRAITS-2009 | Mākslinieks. Portrets. Pašportrets | 978-9984-807-52-2 | `to_create` |

---

## Pre-flight checklist (complete before running QuickStatements)

### Both books

- [ ] Run FIND query 1 (Book 1) on https://query.wikidata.org/ — confirm 0 results
- [ ] Run FIND query 2 (Book 2) on https://query.wikidata.org/ — confirm 0 results

### QID cross-checks (already verified 2026-05-30 — re-verify if >30 days old)

| QID | Label | Check |
|-----|-------|-------|
| Q104429642 | Swedbank Latvia (former Hansabanka) | ✅ |
| Q1370465 | Latvijas Nacionālais mākslas muzejs | ✅ |
| Q30212561 | Neputns | ✅ |
| Q109864986 | Dace Lamberga | ✅ |
| Q1773 | Rīga | ✅ |
| Q3331189 | version, edition, or translation | ✅ |
| Q9078 | Latvian language | ✅ |
| Q1860 | English language | ✅ |

---

## Submission steps (one book at a time)

### Book 1 — Hansabanka 2007

1. Go to https://quickstatements.toolforge.org/#/batch
2. Log in as **ArsAccordia**
3. Select **V1 format**
4. Paste *only* the Book 1 CREATE block from `.qs` (lines after the Book 1 separator)
5. Click **Import** → review the statement list
6. Click **Run** — note returned QID (e.g. `Q12345678`)
7. Open the item on Wikidata and verify statements look correct
8. Run: `python3 scripts/record_book_qid.py SRC-HANSABANKA-2007 Q12345678`

### Book 2 — LNMM Portraits 2009

1. Same steps above, paste the Book 2 CREATE block
2. Note returned QID
3. Run: `python3 scripts/record_book_qid.py SRC-LNMM-PORTRAITS-2009 Q12345678`

---

## Post-submission

After both items are created and QIDs recorded:

- [ ] Commit source registry JSONs with updated `wikidata_qid` and `wikidata_status: "created"`
- [ ] Update affected artist JSON files: in `auth_links`, set `ref_type: "bibliography"` entries for any artist whose record cites either catalogue as a source
- [ ] Optional: add `P910` (topic's main category) on Wikidata once a category page exists

---

## Open questions

| Question | Decision |
|----------|----------|
| Book 1 author spelling: "Žeivaite" vs "Žeivate" | Use P2093 string "Ilze Žeivaite" (title-page spelling). LNB OPAC inaccessible for verification. Revisit if LNB record is found. |
| Juris Petraškevičs (designer, Book 2) | Omit for now — no WD item confirmed. |
| P180/P921 subject enrichment | Do in a follow-up session; keep batch minimal for first contribution. |
