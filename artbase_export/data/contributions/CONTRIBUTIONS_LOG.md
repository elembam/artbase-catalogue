# Wikidata Contributions Log
*ArsAccordia account on Wikidata · Last updated: 2026-06-23*

This file is the single source of truth for all Wikidata work done under the ArsAccordia account.
It tracks what has been submitted, what is ready to submit, and what is planned.

---

## Status summary

| Status | Count | Items |
|---|---|---|
| ✅ SUBMITTED | 4 batches | test_batch_first5, test_rozentals_batch, lnmm_phase1_p973, phase2_p973 |
| ✅ SUBMITTED | 1 batch | phase3_p973 — 8 Phase 3 artist P973 links |
| ✅ SUBMITTED | partial | hansabanka_batch_01 Works 2–6 ✓ / Work 1 still pending |
| ✅ SUBMITTED | partial | hansabanka_batch_02 Works 2–6 ✓ / Work 1 still pending |
| 🟢 READY | 1 batch | lnmm_batch_02_artwork_items — QLNMM_INSTITUTION resolved; PAGE_TO_CONFIRM is sole blocker |
| 🟢 READY | 2 items | hansabanka_batch_01 Work 1 + hansabanka_batch_02 Work 1 (single CREATE blocks each) |
| 📝 DRAFT | 1 batch | qs_tier2_rozentals — blocked until Rozentāls exemplary passport issued |
| ✅ SUPERSEDED | 2 batches | books_batch1 (both items pre-existed); queue_20260528 (superseded by test batches) |
| ⚠️ INVALID | 1 file | Bruno_Aide.qs.txt — invalid P20 format; do not submit |

**Account created:** 28 May 2026 · **Total edits as of 23 June 2026:** 162

---

## Confirmed QIDs for recurring references

| Entity | QID | Notes |
|---|---|---|
| Latvian National Museum of Art (LNMA) | **Q1370465** | Confirmed from P123 on Q139986481 |
| Hansabanka Contemporary Art Collection catalogue (2007) | **Q139986317** | Created 30 May 2026 |
| Artist. Portrait. Self-portrait / Lamberga 2009 | **Q139986481** | Created 30 May 2026 |
| Latvia, wow! : contemporary artists from Latvia (2014) | **Q139986920** | Created 30 May 2026 |
| Archive of visions and actions : contemporary art from Sweden (2015) | **Q139987283** | Created 30 May 2026 |

---

## Priority queue — what to submit next

| # | Task | File | Notes |
|---|---|---|---|
| 1 | Hansabanka Batch 01 Work 1 | hansabanka_batch_01_20260623.qs | "Verities of Suffering" (Blumbergs 1999) — QID pending confirmation |
| 2 | Hansabanka Batch 02 Work 1 | hansabanka_batch_02_20260623.qs | "The Rustling of the Sea" (Āriņš 1960) — QID pending confirmation |
| 3 | P973 batch 08 — 6 newly confirmed artists | hans_p973_batch_08_20260624.qs | Vilumainis, Poikāns, Lapiņa, Putrāms, Lielā, Subačs |
| 4 | Hansabanka Batch 03 — 6 artwork CREATEs | hansabanka_batch_03_20260624.qs | Naumovs, Liberts, Heinrihsons, Krollis, Putrāms diptych |
| 5 | lnmm_batch_02_artwork_items — strip citations or confirm pages | lnmm_batch_02_artwork_items_20260620.qs | 1 enrich + 4 CREATE |
| 6 | Latvian labels for 10 Hansabanka items | paste block ready | Batches 01+02 Works 2–6 |
| 7 | hans_p973_batch_01-07 — CONFIRM submission status | hans_p973_batch_0{1-7}_2026-06-16.qs | ⚠️ Not in log — were these submitted? |

---

## Contribution type A — External identifiers (VIAF / ULAN / LNDB)

---

### BATCH: test_rozentals_batch_20260602 · ✅ SUBMITTED 2 June 2026

**File:** `test_rozentals_batch_20260602.qs`
**Batch ID:** #1780400621763
**Property:** P214 (VIAF ID) × 5
**Note:** Despite the filename this batch covers Apsītis, Annuss, Andersons, Anmanis, Apinis.

| Artist | QID | VIAF | Result |
|---|---|---|---|
| Aleksandrs Apsītis | Q130623 | 70659503 | ✅ |
| Augusts Annuss | Q11300069 | 25737434 | ✅ |
| Edvīns Andersons | Q134417560 | 305088425 | ✅ |
| Jānis Anmanis | Q99483053 | 203230880 | ✅ |
| Jēkabs Apinis | Q97930178 | 305098120 | ✅ |

---

### BATCH: test_batch_first5_20260602 · ✅ SUBMITTED 15 June 2026

**File:** `test_batch_first5_20260602.qs`
**Batch ID:** #1781545243369
**Property:** P214 (VIAF ID) × 5

| Artist | QID | VIAF | Result |
|---|---|---|---|
| Ojārs Ābols | Q3744638 | 45473840 | ✅ |
| Bruno Aide | Q16353281 | 305086869 | ✅ |
| Jānis Aižens | Q55286044 | 305095725 | ✅ |
| Arturs Akopjans | Q85678805 | 5587160546926410240004 | ✅ |
| Andrejs Ameļkovičs | Q139097584 | 30725574 | ✅ |

---

### BATCH: queue_20260528_105208 · ✅ SUPERSEDED — DO NOT SUBMIT

Covers the same 10 artists as test_batch_first5 + test_rozentals_batch combined. Both batches already submitted — this file would cause duplicates.

---

## Contribution type B — Source document items (books / catalogues)

All four catalogue items now exist on Wikidata. Created manually via UI on 30 May 2026.

| QID | Title | Year | Notes |
|---|---|---|---|
| Q139986317 | Hansabanka Contemporary Art Collection | 2007 | Primary source for all Hansabanka batch items |
| Q139986481 | Artist. Portrait. Self-portrait (Lamberga) | 2009 | Primary source for LNMM batch items |
| Q139986920 | Latvia, wow! : contemporary artists from Latvia | 2014 | Fabrica / Benetton publication |
| Q139987283 | Archive of visions and actions : contemporary art from Sweden | 2015 | Fabrica publication |

### books_batch1_20260530 · ✅ SUPERSEDED — DO NOT SUBMIT

The two CREATEs in this file (Q139986317, Q139986481) were made manually before the batch was submitted. File archived at `contributed/books_batch1_20260530.qs`.

---

## Contribution type C — P973 (described at URL) backlinks to Ars Accordia

P973 creates a machine-readable claim on each artist's Wikidata item pointing to their Ars Accordia artist page. This feeds Google Knowledge Panels and Europeana aggregation.

---

### BATCH: lnmm_phase1_p973_20260614 · ✅ SUBMITTED 14 June 2026

**File:** `lnmm_phase1_p973_20260614.qs`
**Batch ID:** #1781464585539
**Property:** P973 × 5

| Artist | QID | Ars Accordia page | Result |
|---|---|---|---|
| Janis Rozentāls | Q975168 | /artists/ART-ROZENTALS-1866.html | ✅ |
| Kārlis Padegs | Q4342040 | /artists/ART-PADEGS-1911.html | ✅ |
| Jāzeps Grosvalds | Q4150307 | /artists/ART-GROSVALDS-1891.html | ✅ |
| Vilhelms Purvītis | Q2663470 | /artists/ART-PURVITIS-1872.html | ✅ |
| Romans Suta | Q6711504 | /artists/ART-SUTA-1896.html | ✅ |

---

### BATCH: phase2_p973_20260615 · ✅ SUBMITTED 15 June 2026

**Batch ID:** #1781544633567
**Property:** P973 × 3 (Phase 2 QIDs confirmed and P973 added in same session)

| Artist | QID | Ars Accordia page | Result |
|---|---|---|---|
| Kārlis Hūns | Q4152126 | /artists/ART-HUNS-1831.html | ✅ |
| Jūlijs Feders | Q1977258 | /artists/ART-FEDERS-1838.html | ✅ |
| Jānis Tīdemanis | Q4457149 | /artists/ART-TIDEMANIS-1897.html | ✅ |

---

### BATCH: phase3_p973_20260616 · ✅ SUBMITTED 16 June 2026

**Batch ID:** #1781584071910
**Property:** P973 × 8 (Phase 3 QIDs confirmed and P973 added in same session)

| Artist | QID | Ars Accordia page | Result |
|---|---|---|---|
| Johann Walter-Kurau (Jānis Valters) | Q4102980 | /artists/ART-VALTERS-1869.html | ✅ |
| Jēkabs Kazaks | Q5763621 | /artists/ART-KAZAKS-1895.html | ✅ |
| Rūdolfs Pērle | Q14110160 | /artists/ART-PERLE-1875.html | ✅ |
| Pēteris Krastiņš | Q58456712 | /artists/ART-KRASTINS-1882.html | ✅ |
| Ādams Alksnis | Q4062525 | /artists/ART-ALKSNIS-1864.html | ✅ |
| Rihards Zariņš | Q2371375 | /artists/ART-ZARINS-1869.html | ✅ |
| Gustavs Klucis | Q1341721 | /artists/ART-KLUCIS-1895.html | ✅ |
| Teodors Ūders | Q20565577 | /artists/ART-UDERS-1868.html | ✅ |

---

## Contribution type D — Artwork items

---

### BATCH: lnmm_batch_02_artwork_items_20260620 · 🟢 READY (one placeholder remaining)

**File:** `lnmm_batch_02_artwork_items_20260620.qs`
**Review doc:** `lnmm_batch_02_artwork_items_20260620.review.md`
**Operations:** 1 enrichment (Q22043968) + 4 CREATE

**Resolved placeholders:**
- `QLNMM_INSTITUTION` → **Q1370465** ✅ (Latvian National Museum of Art — confirmed)
- `QLNMM_PORTRAITS_2009` → **Q139986481** ✅ (already in file)

**Remaining blocker:**
- `PAGE_TO_CONFIRM` — page numbers from Lamberga 2009 (physical book). Options: (a) obtain page numbers; (b) strip all S248/S304 pairs and submit unsourced — citations can be added later.

| Work | ID | Operation | Artist | QID | Inv | Notes |
|---|---|---|---|---|---|---|
| Princess with a Monkey | AA/LV/LNMA/001 | ENRICH Q22043968 | Rozentāls | Q975168 | VMM GL-5668 | Add P195/P217/dimensions |
| Carousel | AA/LV/LNMA/004 | CREATE | Tīdemanis | Q4457149 | VMM GL-2822 | 1932 |
| From Church (After the Service) | AA/LV/LNMA/006 | CREATE | Rozentāls | Q975168 | VMM GL-55 | 1894 |
| Young Gipsy Woman | AA/LV/LNMA/017 | CREATE | Hūns | Q4152126 | VMM GL-1509 | 1870 |
| Country Landscape | AA/LV/LNMA/019 | CREATE | Feders | Q1977258 | VMM GL-1501 | 1880 — no citation |
| Folk Festival at Kokmuiža | AA/LV/LNMA/012 | **EXCLUDED** | Hūns (unverified) | Q4152126 | VMM Z-4128 | Attribution not confirmed |

**Submission status:**
- Submitted at: _______________
- Q22043968 (enrich) result: _______________
- 004 new QID: _______________
- 006 new QID: _______________
- 017 new QID: _______________
- 019 new QID: _______________

---

### BATCH: qs_tier2_rozentals.txt · ✅ SUBMITTED 23 June 2026

**File:** `ArsAccordiaClaude/qs_tier2_rozentals.txt`

| Title | Inv | QID | P973 status |
|---|---|---|---|
| From Church (After the Service) | VMM GL-55 | **Q140324167** | ✅ Passport exists at /passports/AA/LV/LNMA/006/ — add P973 now |
| Under the Rowan Tree | VMM GL-73 | **Q140324168** | ⏳ No passport yet — needs ArtBase JSON + HTML |
| In the Artist's Studio | VMM GL-36 | **Q140324170** | ⏳ No passport yet |
| Beauty (Ave Sol). Fresco Sketch | VMM Z-4309 | **Q140324171** | ⏳ No passport yet |
| Temptation | VMM Z-4250 | **Q140324172** | ⏳ No passport yet |

**Note:** Check each item on Wikidata — the batch file had P195 as both a main claim and a qualifier on P217. Confirm P195 does not appear twice as a main statement.

---

### BATCH: hansabanka_batch_01_20260623 · ✅ SUBMITTED (Works 2–6) / ⚠️ Work 1 pending

**File:** `hansabanka_batch_01_20260623.qs`
**Source:** Q139986317

| # | Work (LV / EN) | Artist | Year | Page | QID returned |
|---|---|---|---|---|---|
| 1 | Ciešanu atziņas / Verities of Suffering | Blumbergs | 1999 | 222 | **⚠️ NOT SUBMITTED** |
| 2 | Sudraba laikmets / The Silver Age | Blumbergs | 1998 | 222 | **Q140323417** ✅ |
| 3 | Kariatīde / Caryatid (Scare-Crow) | Skulme | 2004 | 228 | **Q140323442** ✅ |
| 4 | Šagāla piemiņai / In Memory of Chagall | Zariņš | 1996 | 229 | **Q140323447** ✅ |
| 5 | Tautisks totēms / Folk-Style Totem | Pinnis | 1989 | 227 | **Q140323450** ✅ |
| 6 | Karnevāls / Carnival | Maldupe | 1977 | 226 | **Q140323452** ✅ |

**To complete:** Paste Work 1 CREATE block from the .qs file (lines 37–46).

---

### BATCH: hansabanka_batch_02_20260623 · ✅ SUBMITTED (Works 2–6) / ⚠️ Work 1 pending

**File:** `hansabanka_batch_02_20260623.qs`
**Source:** Q139986317

| # | Work (LV / EN) | Artist | Year | Page | QID returned |
|---|---|---|---|---|---|
| 1 | Jūras šalkas / The Rustling of the Sea | Āriņš | 1960 | 222 | **⚠️ NOT SUBMITTED** |
| 2 | Atslābums / Slackening | Mitrēvics | 1990 | 226 | **Q140323550** ✅ |
| 3 | Rudens / Autumn | Siliņš | 1974 | 228 | **Q140323551** ✅ |
| 4 | Levitācija. I / Levitation. I | Sietiņš | 1995 | 228 | **Q140323553** ✅ |
| 5 | Jūra / The Sea | Rozenbergs | 2004 | 227 | **Q140323556** ✅ |
| 6 | Ziedu pikets / A Picket of Flowers | Ģelzis | 2007 | 223 | **Q140323559** ✅ |

**To complete:** Paste Work 1 CREATE block from the .qs file (lines 26–36).

---

### BATCH: hansabanka_batch_03_20260624 · 🟢 READY

**File:** `hansabanka_batch_03_20260624.qs`

| # | Work (LV / EN) | Artist | Year | Page | QID returned |
|---|---|---|---|---|---|
| 1 | Parīze vakara saulē / Paris under the Evening Sun | Naumovs | 1987 | 226 | **⚠️ NOT SUBMITTED** |
| 2 | Venēcija. Dodžu pils / Venice. The Doge's Palace | Liberts | 1930 | 225 | **⚠️ NOT SUBMITTED** |
| 3 | Pelēkās klavieres / The Grey Piano | Heinrihsons | 2004 | 224 | **⚠️ NOT SUBMITTED** |
| 4 | Aizmirstie karaļdārzi. III / Forgotten King's Gardens. III | Krollis | 1994 | 225 | **⚠️ NOT SUBMITTED** |
| 5 | Hameleons. Diptihs I daļa / Chameleon. Diptych. Part I | Putrāms | 1993 | 227 | **⚠️ NOT SUBMITTED** |
| 6 | Hameleona pavadonis. Diptihs II daļa / Chameleon's Companion. Diptych. Part II | Putrāms | 1993 | 227 | **⚠️ NOT SUBMITTED** |

---

### BATCH: hans_p973_batch_08_20260624 · 🟢 READY

**File:** `hans_p973_batch_08_20260624.qs`
**Property:** P973 × 6 — newly confirmed no_match artists with HTML pages

| Artist | QID | ArtBase ID | Result |
|---|---|---|---|
| Jūlijs Vilumainis | Q99480030 | ART-VILUMAINIS-1909 | ⚠️ NOT SUBMITTED |
| Ivars Poikāns | Q99483958 | ART-POIKANS-1952 | ⚠️ NOT SUBMITTED |
| Dace Lapiņa | Q99481295 | ART-LAPINA-1954 | ⚠️ NOT SUBMITTED |
| Juris Putrāms | Q99481514 | ART-PUTRAMS-1956 | ⚠️ NOT SUBMITTED |
| Dace Lielā | Q99477354 | ART-LIELA-1957 | ⚠️ NOT SUBMITTED |
| Māris Subačs | Q99480580 | ART-SUBACS-1963 | ⚠️ NOT SUBMITTED |

---

### ⚠️ STATUS UNKNOWN: hans_p973_batch_01 through 07 (2026-06-16)

**Files:** `hans_p973_batch_01_2026-06-16.qs` through `hans_p973_batch_07_2026-06-16.qs`
These 7 batches (~70 auto_match artists) were generated by the reconciliation script on 16 June 2026 but are **not recorded in this log**. Confirm with ArsAccordia account holder whether these were submitted. If not, submit before batch 08.

---

### Bruno Aide place of death · ⚠️ INVALID — do not submit

**File:** `Bruno_Aide.qs.txt` (root level)

Invalid format — P20 value is a string ("Rīga, Latvija") instead of a QID.
Fix: `Q16353281	P20	Q1773	S854	"https://lv.wikipedia.org/wiki/Bruno_Aide"`

---

## Key references

| Resource | Link |
|---|---|
| QuickStatements | https://quickstatements.toolforge.org/ |
| ArsAccordia Wikidata account | https://www.wikidata.org/wiki/User:Arsaccordia |
| LNMM on Wikidata | https://www.wikidata.org/wiki/Q1370465 |
| Hansabanka catalogue on Wikidata | https://www.wikidata.org/wiki/Q139986317 |
| Lamberga 2009 on Wikidata | https://www.wikidata.org/wiki/Q139986481 |
| LNMM Wikidata plan | `docs/WIKIDATA_LNMM_PLAN.md` |
