# Wikidata Contributions Log
*ArsAccordia account on Wikidata · Last updated: 2026-06-23*

This file is the single source of truth for all Wikidata work done under the ArsAccordia account.
It tracks what has been submitted, what is ready to submit, and what is planned — and explains
why each contribution matters to the Ars Accordia website and business strategy.

---

## Status summary

| Status | Count | Items |
|---|---|---|
| ✅ VERIFIED | 0 | — |
| 📤 SUBMITTED | 0 | — |
| 🟢 READY | 4 batches | test_batch_first5, test_rozentals_batch, lnmm_batch_02_artwork_items, hansabanka_batch_01 |
| ✅ SUPERSEDED | 1 batch | books_batch1 — both book QIDs already exist (Q139986317, Q139986481) |
| 📝 DRAFT | 1 batch | qs_tier2_rozentals (artwork CREATEs — superseded by lnmm_batch_02 for 006) |
| 🟢 READY | 1 batch | lnmm_phase1_p973_20260614 — P973 backlinks for 5 LNMM artists |
| 🔵 PLANNED | 2 | Phase 3 artist records, Phase 4 artwork items |
| ⚠️ DUPLICATE | 1 | queue_20260528 (superseded by test_batch_first5 + test_rozentals_batch) |

**Nothing has been submitted to Wikidata yet.**

---

## Priority queue — what to submit next

Do these in order. Each step builds trust before the next.

| # | Batch | Statements | Why now |
|---|---|---|---|
| 1 | `test_batch_first5_20260602` | 5 VIAF IDs | First-ever submission; smallest possible safe test |
| 2 | `test_rozentals_batch_20260602` | 5 VIAF IDs | Second test — wait 48h after step 1 for community reaction |
| 3 | `lnmm_phase1_p973_20260614` | 5 P973 links | Highest strategic value — links Wikidata items to Ars Accordia pages |
| 4 | `lnmm_batch_02_artwork_items_20260620` | 1 enrich + 4 CREATE | 5 LNMM artwork items; confirm QLNMM_INSTITUTION before submitting |
| 5 | `hansabanka_batch_01_20260623` | 6 CREATE | Hansabanka works — resolve 5 artist QIDs first |
| 6 | Phase 3 artist records | 8 ArtBase records | Create canonical records before issuing passports |
| 7 | Phase 4 artwork items (follow-on) | 5–8 CREATE | Additional LNMM works after batch 02 QIDs are returned |

---

## Contribution type A — External identifiers (VIAF / ULAN / LNDB)

**Strategic purpose:** Establishes ArsAccordia as a credible Wikidata contributor. Identifier additions are
low-controversy, independently verifiable, and build the account reputation needed for higher-impact edits later.
No direct Ars Accordia site link — this is foundation work.

---

### BATCH: test_batch_first5_20260602 · 🟢 READY

**File:** `test_batch_first5_20260602.qs`  
**Review doc:** `test_batch_first5_20260602.review.md`  
**Generated:** 2026-06-02  
**Property:** P214 (VIAF ID) × 5  
**Purpose:** First-ever QuickStatements submission — proof of process

| Artist | QID | VIAF | Notes |
|---|---|---|---|
| Ojārs Ābols | Q3744638 | 45473840 | ArtBase record exists |
| Bruno Aide | Q16353281 | 305086869 | ArtBase record exists |
| Jānis Aižens | Q55286044 | 305095725 | ArtBase record exists |
| Arturs Akopjans | Q85678805 | 5587160546926410240004 | ArtBase record exists |
| Andrejs Ameļkovičs | Q139097584 | 30725574 | ArtBase record exists |

**Submission status:**
- Batch ID: _______________
- Submitted at: _______________
- Result: ___ / 5 success

---

### BATCH: test_rozentals_batch_20260602 · 🟢 READY

**File:** `test_rozentals_batch_20260602.qs`  
**Review doc:** `test_rozentals_batch_20260602.review.md`  
**Generated:** 2026-06-02  
**Property:** P214 (VIAF ID) × 5  
**Note:** Despite the filename, this batch covers Apsītis, Annuss, Andersons, Anmanis, Apinis — not Rozentāls.

| Artist | QID | VIAF | Notes |
|---|---|---|---|
| Aleksandrs Apsītis | Q130623 | 70659503 | LNMM artist; National Artist of Latvia |
| Augusts Annuss | Q11300069 | 25737434 | LNMM artist |
| Edvīns Andersons | Q134417560 | 305088425 | LNMM artist |
| Jānis Anmanis | Q99483053 | 203230880 | LNMM artist |
| Jēkabs Apinis | Q97930178 | 305098120 | LNMM artist |

**Submission status:**
- Batch ID: _______________
- Submitted at: _______________
- Result: ___ / 5 success

**Submit this only after test_batch_first5 succeeds with no reverts (wait 48 hours).**

---

### BATCH: queue_20260528_105208 · ⚠️ SUPERSEDED

**File:** `queue_20260528_105208.qs`  
**Do NOT submit this batch.** It covers the same 10 artists as `test_batch_first5` + `test_rozentals_batch` combined.
Submitting it after the test batches would duplicate all statements and cause errors.

---

## Contribution type B — Source document items (books / catalogues)

**Strategic purpose:** Creates Wikidata items for the printed catalogues that Ars Accordia uses as
provenance references (Hansabanka 2007 catalogue, LNMM Portraits 2009). Once these items exist,
artist statements in Wikidata can use them as `stated in` (P248) references — upgrading the quality
of those citations. Also directly links two of our key collections to Wikidata.

---

### BATCH: books_batch1_20260530 · ✅ SUPERSEDED — DO NOT SUBMIT

**File:** `books_batch1_20260530.qs`  
**Review doc:** `books_batch1_20260530.review.md`  
**Generated:** 2026-05-30  
**Operation:** CREATE two new Wikidata items

| Source ID | Title | ISBN | Notes |
|---|---|---|---|
| SRC-HANSABANKA-2007 | Hansabankas mūsdienu mākslas kolekcija | 978-9984-39-381-0 | Hansabanka contemporary art collection catalogue |
| SRC-LNMM-PORTRAITS-2009 | Mākslinieks. Portrets. Pašportrets | 978-9984-807-52-2 | LNMM portraits catalogue — key source for LNMM artist records |

**Status: ✅ SUPERSEDED — both items already exist on Wikidata.**

- SRC-HANSABANKA-2007 → **Q139986317** ("Hansabanka Contemporary Art Collection")
- SRC-LNMM-PORTRAITS-2009 → **Q139986481** ("Artist. Portrait. Self-portrait")

Confirmed 2026-06-20. `books_batch1_20260530.qs` should **not** be submitted — the CREATE operations
would attempt to create items that already exist. Use these QIDs directly as `S248` references.

---

## Contribution type C — P973 (described at URL) backlinks to Ars Accordia

**Strategic purpose:** This is the highest-value contribution for the business.
P973 creates a machine-readable statement on each artist's Wikidata item that says:
*"This person is described at arsaccordia.com/artists/..."*

This is what enables Wikidata to surface Ars Accordia in Google Knowledge Panels and Europeana
aggregation. Every P973 link is a direct SEO and authority signal pointing to the site.
Priority: do this for the 5 confirmed LNMM artists immediately.

**Reference:** `docs/WIKIDATA_LNMM_PLAN.md` Phase 1

---

### BATCH: lnmm_phase1_p973_20260614 · 🟢 READY

**File:** `lnmm_phase1_p973_20260614.qs`  
**Review doc:** `lnmm_phase1_p973_20260614.review.md`  
**Generated:** 2026-06-14  
**Property:** P973 (described at URL) × 5  
**References:** S854 (reference URL) + S813 (retrieved date: 2026-06-14)

| Works | Artist | QID | Ars Accordia page |
|---|---|---|---|
| 39 | Janis Rozentāls | Q975168 | arsaccordia.com/artists/ART-ROZENTALS-1866.html |
| 25 | Kārlis Padegs | Q4342040 | arsaccordia.com/artists/ART-PADEGS-1911.html |
| 19 | Jāzeps Grosvalds | Q4150307 | arsaccordia.com/artists/ART-GROSVALDS-1891.html |
| 18 | Vilhelms Purvītis | Q2663470 | arsaccordia.com/artists/ART-PURVITIS-1872.html |
| 18 | Romans Suta | Q6711504 | arsaccordia.com/artists/ART-SUTA-1896.html |

**Submission status:**
- Batch ID: _______________
- Submitted at: _______________
- Result: ___ / 5 success

---

### BATCH: lnmm_batch_02_artwork_items_20260620 · 🟢 READY

**File:** `lnmm_batch_02_artwork_items_20260620.qs`
**Review doc:** `lnmm_batch_02_artwork_items_20260620.review.md`
**Generated:** 2026-06-20
**Operations:** 1 enrichment (Q22043968) + 4 CREATE
**Statements proposed:** 48 (4 enrichment + 11 × 4 CREATE)
**Properties:** P31, P170, P571, P186, P195, P217, P2048, P2049 · References: S248/S304

| Work | ID | Operation | Artist | Inv | Notes |
|---|---|---|---|---|---|
| Princess with a Monkey | AA/LV/LNMA/001 | ENRICH Q22043968 | Rozentāls Q975168 | VMM GL-5668 | Add P195/P217/dimensions |
| Carousel | AA/LV/LNMA/004 | CREATE | Tīdemanis Q4457149 | VMM GL-2822 | 1932 |
| From Church (After the Service) | AA/LV/LNMA/006 | CREATE | Rozentāls Q975168 | VMM GL-55 | 1894 |
| Young Gipsy Woman | AA/LV/LNMA/017 | CREATE | Hūns Q4152126 | VMM GL-1509 | 1870 |
| Country Landscape | AA/LV/LNMA/019 | CREATE | Feders Q1977258 | VMM GL-1501 | 1880 |
| Folk Festival at Kokmuiža | AA/LV/LNMA/012 | **EXCLUDED** | Hūns (unverified) | VMM Z-4128 | Attribution not yet confirmed |

**⚠️ GATING PLACEHOLDERS in batch file — replace before submitting:**
- `QLNMM_INSTITUTION` — Q681819 or Q1370465? Open both on Wikidata and confirm which is LNMM
- `QLNMM_PORTRAITS_2009` — submit `books_batch1_20260530.qs` first; use the QID it creates
- `PAGE_TO_CONFIRM` — verify page numbers from Lamberga 2009; if unconfirmable, remove S248/S304

**Submission status:**
- Submitted at: _______________
- Batch ID: _______________
- Q22043968 (enrich) result: _______________
- 004 new QID: _______________
- 006 new QID: _______________
- 017 new QID: _______________
- 019 new QID: _______________

---

## Contribution type D — Artwork items (new Wikidata items for LNMM works)

**Strategic purpose:** Creates Wikidata items for specific artworks, linking them to the issued Ars Accordia
passport via P973. This is the endgame: a Wikidata item for a painting → cites Ars Accordia passport →
passport appears in search results as the authoritative catalogue record.

**Constraint:** P973 can only be added to an artwork item *after* the Ars Accordia passport has been issued
(we need the AP-2026-XXXXXX ID). The exemplary passports must come first.

**Reference:** `docs/WIKIDATA_LNMM_PLAN.md` Phase 4

---

### BATCH: qs_tier2_rozentals.txt · 📝 DRAFT (needs review before use)

**File:** `ArsAccordiaClaude/qs_tier2_rozentals.txt` (move to contributions/ when ready)  
**Operation:** CREATE 5 painting/artwork items for Rozentāls works

| Title | Cat. No. | P31 type | Notes |
|---|---|---|---|
| From Church (After the Service) | VMM GL-55 | Q3305213 (painting) | Priority for first exemplary passport |
| Under the Rowan Tree | VMM GL-73 | Q3305213 (painting) | |
| In the Artist's Studio | VMM GL-36 | Q3305213 (painting) | |
| Beauty (Ave Sol). Fresco Sketch | VMM Z-4309 | Q12043905 (sketch) | |
| Temptation | VMM Z-4250 | Q18761202 (drawing) | |

**⚠️ Issues to resolve before submitting:**
- [ ] Confirm Q681819 is the correct QID for LNMA (currently used as P195/collection)
- [ ] Add P973 pointing to the issued passport — requires passport to be issued first (AP-2026-XXXXXX)
- [ ] Add Google Arts & Culture URL as P856 reference on each item
- [ ] Verify P2048/P2049 (height/width) unit: U174728 = cm (confirm this is correct)
- [ ] Add Latvian labels (Lnl) for each item

**Do not submit until the Rozentāls exemplary passport is issued.**

---

### BATCH: hansabanka_batch_01_20260623 · 🟢 READY (pending artist QID verification)

**File:** `hansabanka_batch_01_20260623.qs`
**Review doc:** `hansabanka_batch_01_20260623.review.md`
**Generated:** 2026-06-23
**Operations:** 6 CREATE
**Source:** Q139986317 (Hansabanka Contemporary Art Collection catalogue, 2007)
**Pages used:** 222, 226, 228, 229

| # | Work | Artist | Year | Page | Artist QID status |
|---|---|---|---|---|---|
| 1 | Ciešanu atziņas (Verities of Suffering) | Ilmārs Blumbergs | 1999 | 222 | Q13611050 ✓ |
| 2 | Sudraba laikmets (The Silver Age) | Ilmārs Blumbergs | 1998 | 222 | Q13611050 ✓ |
| 3 | Kariatīde (Caryatid) | Džemma Skulme | 2004 | 228 | Q4422700 ✓ |
| 4 | Šagāla piemiņai (In Memory of Chagall) | Indulis Zariņš | 1996 | 229 | Q13561029 ✓ |
| 5 | Tautisks totēms (Folk-Style Totem) | Rūdolfs Pinnis | 1989 | 227 | Q55984280 ✓ |
| 6 | Karnevāls (Carnival) | Vija Maldupe | 1977 | 226 | Q113216930 ✓ |

**Status: all artist QIDs resolved. Batch is ready to submit.**

**Submission status:**
- All artist QIDs resolved: ___
- Submitted at: _______________
- Work 1 QID: _______________
- Work 2 QID: _______________
- Work 3 QID: _______________
- Work 4 QID: _______________
- Work 5 QID: _______________ *(or "ENRICH — existing item" if already on Wikidata)*
- Work 6 QID: _______________

---

### Bruno Aide place of death · ⚠️ NEEDS REVIEW

**File:** `Bruno_Aide.qs.txt` (root level — move to contributions/ or delete)

Contains: `Q16353281|P20|"Rīga, Latvija"|S854|"https://lv.wikipedia.org/wiki/Bruno_Aide"`

**Issues:**
- P20 (place of death) value should be a QID (Q1773 for Rīga), not a string
- Current format is invalid — will fail in QuickStatements
- Fix: `Q16353281	P20	Q1773	S854	"https://lv.wikipedia.org/wiki/Bruno_Aide"`
- Alternatively: skip and add this in a general identifier batch for Bruno Aide

**Status:** Do not submit in current form.

---

## Phase 3 — Missing artists (create ArtBase records first, Wikidata second)

**Reference:** `docs/WIKIDATA_LNMM_PLAN.md` Phase 3

These 8 high-representation LNMM artists have no ArtBase record yet.
Priority: create ArtBase JSON record → generate artist page → submit P973 to Wikidata.

| Works | Artist | Lifespan | ArtBase record | Wikidata QID |
|---|---|---|---|---|
| 28 | Johann Walter / Jānis Valters | 1869–1932 | ❌ needed | TBD — likely exists |
| 20 | Jēkabs Kazaks | 1895–1920 | ❌ needed | TBD — likely exists |
| 16 | Rūdolfs Pērle | 1875–1917 | ❌ needed | TBD — search "Rudolf Perle" |
| 12 | Pēteris Krastiņš | 1882–1942 | ❌ needed | TBD |
| 11 | Ādams Alksnis | 1864–1897 | ❌ needed | TBD |
| 9 | Rihards Zariņš | 1869–1939 | ❌ needed | TBD — likely exists |
| 7 | Teodors Ūders | 1868–1915 | ❌ needed | TBD |
| 5 | Gustavs Klucis | 1895–1938 | ❌ needed | Almost certainly exists (Constructivist) |

---

## Phase 2 — QID resolution needed (ArtBase records exist, Wikidata unconfirmed)

| Works | Artist | Lifespan | ArtBase record | Action |
|---|---|---|---|---|
| 10 | Kārlis Hūns | 1830–1877 | ✅ exists | Search Wikidata for "Karl Hün" — update ArtBase JSON |
| 9 | Jūlijs Feders | 1838–1909 | ✅ exists | Search Wikidata for "Julius Feders" — update ArtBase JSON |
| 7 | Jānis Tīdemanis | 1897–1964 | ✅ exists | Search Wikidata for "Jānis Tīdemanis" — update ArtBase JSON |

---

## Archive — submitted and verified

*(Nothing here yet — all contributions are pending.)*

---

## Key references

| Resource | Link |
|---|---|
| QuickStatements | https://quickstatements.toolforge.org/ |
| Wikidata P973 property | https://www.wikidata.org/wiki/Property:P973 |
| ArsAccordia Wikidata account | https://www.wikidata.org/wiki/User:Arsaccordia |
| LNMM Wikidata plan | `docs/WIKIDATA_LNMM_PLAN.md` |
| Business roadmap | `docs/BUSINESS_ROADMAP.md` |
| Runbook | `docs/quickstatements_runbook.md` |
| LNMM collection page | https://arsaccordia.com/collections/lnmm/ |
