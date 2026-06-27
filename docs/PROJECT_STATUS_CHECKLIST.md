# ArsAccordia — Project Status Checklist
*Last updated: 2026-06-24*

Tick items as they are confirmed complete. Sections follow the four workstreams: Wikidata uploads, LNMM data quality, Hansabanka passports, and business roadmap.

---

## 1. Wikidata — QuickStatements upload cadence

### LNMM artwork CREATEs
- [x] LNMM Batch 01 Work 1 — Rozentāls "From Church After the Service" — created (batch #1782252373940)
- [x] LNMM Batch 02 Work 1 — Tīdemanis "Sailing Boats" — created (batch #1782252373940)
- [ ] LNMM Batch 01 Works 2–5 (qs_tier2_rozentals.txt) — Rozentāls ×4 — confirm QIDs logged in CONTRIBUTIONS_LOG
- [ ] Retrieve QIDs for all confirmed LNMM artwork CREATEs → write to passport JSONs (artwork_wikidata authority block)
- [ ] LNMM Batch 03 — remaining LNMM artworks — **blocked until portrait passport HTML pages are published**

### LNMM P973 backlinks
- [ ] ⚠️ Confirm whether hans_p973_batch_01–07 were submitted — not in CONTRIBUTIONS_LOG; check Wikidata contribution history
- [ ] If not yet submitted: submit the 6 P973 lines from `hans_p973_batch_08_20260624.qs`

### Latvian labels block
- [ ] Submit Latvian (lv) labels for 10 Wikidata items — block was prepared; not yet submitted

### Hansabanka artwork CREATEs
- [x] Hansabanka Batch 01 Works 2–6 — confirmed created (batch #1782252373940)
- [x] Hansabanka Batch 02 Works 2–6 — confirmed created (batch #1782252373940)
- [x] Hansabanka Batch 03 (6 items: Naumovs, Liberts, Heinrihsons, Krollis, Putrāms ×2) — submitted 2026-06-24
- [ ] Retrieve QIDs from Batch 03 (Naumovs, Liberts, Heinrihsons, Krollis, Putrāms diptych I+II) → update HANS/013–018 JSON records
- [ ] Retrieve QIDs from Batch 01 W1 + Batch 02 W1 → update HANS/001 and HANS/007 JSON records

### Hansabanka P973 backlinks
- [x] P973 backlinks for 15 newly confirmed Hansabanka artists — `hans_p973_batch_08_20260624.qs` prepared
- [ ] Submit `hans_p973_batch_08_20260624.qs` (6 lines: Vilumainis, Poikāns, Lapiņa, Putrāms, Lielā, Subačs)
- [ ] P973 backlinks for remaining no-page artists — blocked until their HTML artist pages are generated

### Artist QID reconciliation
- [x] 15 new Hansabanka artist QIDs confirmed (June 2026 reconciliation)
- [x] 5 Hansabanka artists confirmed as having no Wikidata item
- [ ] SPARQL lookup for ~16 still-pending Hansabanka artist QIDs — blocked during SPARQL outage (797a132); retry when available
- [ ] Mikhail Shemyakin (Mihails Šemjakins) QID — definitely on Wikidata; not retrieved during outage
- [ ] Oskars Muižnieks — Q134570321 (painter b. 1922) needs human verification vs. Q2034178 (biathlete)

### Mix'n'match catalog
- [ ] Register LNMM and Hansabanka works in Mix'n'match catalog #8050

---

## 2. LNMM data quality — Spec 14 / Spec 15

### A1 — Name error (LNMA/017)
- [x] `maker_display_name` in LNMA/017.json — already reads "Kārlis Hūns" (not "Ādams Hūns"); no correction needed
- [x] LNMA/012.json ("Folk Festival at Kokmuiža") — SRC-LNMM-PORTRAITS-2009 citation already removed; marked as genre/landscape work

### A2 — institution QID missing
- [x] `location.collection_qid` set to "Q1370465" in LNMA/001, 004, 006, 012, 017, 019 — fixed 2026-06-24
- [ ] Add `source_qid: "Q139986481"` annotation to SRC-LNMM-PORTRAITS-2009 reference in all 6 passports (book Wikidata QID confirmed)

### A3 — Provenance page citations (HUMAN action required)
- [ ] Verify LNMA/001 provenance page against physical copy of *Mākslinieks. Portrets. Pašportrets.* (2009)
- [ ] Verify LNMA/004 provenance page against physical copy
- [ ] Verify LNMA/006 provenance page against physical copy
- [ ] Verify LNMA/017 provenance page against physical copy
- [ ] Mark each as "verified" in the provenance source note once confirmed

### A4/A5 — Score arithmetic
- [x] `build_collection_score.py` uses `round_half_up` (not banker's rounding) — already correct
- [x] `build_passport_score.py` imports `round_half_up` from `build_collection_score.py` — already correct
- [x] `--check` passes for COL-LNMM (stored=502, computed=502)

### LNMM passport HTML pages
- [ ] Regenerate LNMM portrait passport HTML pages (AP-2026-000001 through AP-2026-000006) with confirmed artwork Wikidata QIDs in §02 Authority section
- [ ] Publish portrait passport HTML pages to arsaccordia.com — **unblocks LNMM Batch 03 QS uploads**

---

## 3. Hansabanka passports — Spec 15 Part C

### Passport JSON records
- [x] 18 Hansabanka passport JSONs created (AA/LV/HANS/001–018) — 2026-06-24
- [x] COL-HANSABANKA.json updated (18 member passports, score=1728, avg=96.0 "Complete Record")
- [ ] Update HANS/013–018 with Batch 03 artwork Wikidata QIDs (once retrieved)
- [ ] Update HANS/001 with Batch 01 W1 artwork QID; HANS/007 with Batch 02 W1 artwork QID
- [ ] Rerun `build_collection_score.py COL-HANSABANKA` after QID updates (authority fills will rise 0.5→1.0 for 6 works; score expected 1728→1800)

### Hansabanka collection page
- [ ] Build `collections/hansabanka/index.html` — Hansabanka collection overview page
- [ ] List 18 passport thumbnails/links on collection page

### Artist HTML pages (artists without pages)
- [ ] Generate HTML pages for 9 Hansabanka no-page artists (Grišins, Liepiņa-Grīva, Spalviņš, Kalnācs, Brūvere, Šilova, Daņiļevska, Krūklis, + Strunke if applicable)
- [ ] Add P973 lines for these artists once pages exist

---

## 4. Infrastructure / site

### Dossier generator
- [ ] Build `scripts/build_dossier.py` — Spec 15 Part D — client-facing PDF/HTML dossier output

### COL-DEMO score drift
- [ ] Investigate COL-DEMO drift (stored=120, computed=160) — update or archive demo collection score

---

## 5. Business roadmap — Q3 2026

- [ ] Hansabanka pilot offer — approach 3 warm contacts with a sample collection dossier (target: end-July 2026)
- [ ] LNMM pilot offer — contact LNMM with portrait passport samples + Wikidata contribution summary (target: Q3 2026)
- [ ] Madrid leave-behind / assessment document — finalize and distribute (ArsAccordia Claude Madrid materials ready)

---

## Blocked items (do not action until unblocked)

| Item | Blocked by |
|---|---|
| LNMM Batch 03 QS upload | Portrait passport HTML pages published |
| P973 for no-page Hansabanka artists | HTML pages generated |
| Remaining 16 artist SPARQL lookups | Wikidata SPARQL endpoint outage clear |
| Oskars Muižnieks QID | Human verification of Q134570321 |
| Relative completeness score for LNMM | total_extent confirmed |
