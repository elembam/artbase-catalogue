# Ars Accordia — Swedbank / Hansabanka Reconciliation Workflow
**Dataset:** Swedbank / Hansabanka Contemporary Art Collection · 386 artworks · 110 artists  
**Source:** Structured OCR export from catalogue pages 222–229 (`swedbank.html`)  
**Goal:** Link every artwork and artist to Wikidata, assign Ars Accordia passport IDs, and produce a fully reconciled, multi-authority catalogue layer.

---

## Conceptual framework

Reconciliation in Ars Accordia means bringing three authority layers into agreement for each record:

| Layer | Source | Identifier type |
|---|---|---|
| Corporate collection authority | Hansabanka / Swedbank | Catalogue number (e.g. `21`, `22`, …) |
| Open linked data | Wikidata | Q-number |
| Ars Accordia | This project | AA/LV/SWB/xxx |

The workflow moves the Swedbank xlsx from **layer 1 only** to all three layers linked.

> **Note on catalogue numbers:** Many records in `swedbank.html` have an empty `catalogue_no` field — numbers appear for only ~180 of 386 rows. The `id` field (1–386, sequential in source order) serves as the stable internal row key until Ars Accordia IDs are assigned.

---

## Phase 0 — Prepare the dataset

### 0.1 Extract and clean the records
The source is `swedbank.html`, structured OCR from two CSV files:
- `swedbank_collection_page_222_ocr_structured(1).csv` (page 222, 48 records)
- `swedbank_collection_pages_223_229_ocr_structured(1).csv` (pages 223–229, 338 records)

Key cleaning steps:
- **Titles:** `title_lv` and `title_en` are both present; preserve both. Where `title_en` is blank (e.g. row 48: `Čivirs-2`), keep the Latvian title as the canonical label for now.
- **Medium:** `medium_raw` contains bilingual strings in the form `latvian / english`. Extract the English portion after ` / ` as `medium_en`. Note: pages 223–229 use comma-only separators (e.g. `audekls, eļļa`) rather than the ` / ` pattern on page 222 — handle both.
- **Dimensions:** Format is `H x W` in cm (e.g. `86 x 43.5`). Some multi-part works use compound formats (`4 x (30 x 30)`, `5 x (20 x 30)`, or a semicolon-separated list for item 141). Parse defensively; flag compound dimensions in a `notes` column.
- **Year:** Most values are four-digit years. Some are ranges (`2006/2007`, `1988/1989`, `1986/1987`), one is a decade string (`20. gs. 30. gadi` = "1930s"). Normalise to `year_from` / `year_to` columns; use `circa` flag for decade-only dates.
- **No lifespan data:** Unlike the LNMA dataset, artist birth/death years are **not** in the source. They must be retrieved from Wikidata or looked up separately during Phase 1.

### 0.2 Extract the unique artist list
From 386 rows, deduplicate to the **110 unique artists** listed in the catalogue summary. Build an artist authority register:

| Column | Source | Notes |
|---|---|---|
| `artist` | `artist` field | As OCR'd |
| `work_count` | Count of rows per artist | Matches summary: e.g. Heinrihsone 19, Krollis 12 |
| `birth_year` | *(to be filled — Phase 1)* | Not in source |
| `death_year` | *(to be filled — Phase 1)* | Not in source |
| `wikidata_q` | *(to be filled — Phase 1)* | |
| `aa_artist_id` | *(to be assigned)* | AA/LV/ARTIST/xxx |

> **Name variants to watch:** The collection contains artist family groups (Heinrihsone/Heinrihsons, the three ZariņšZariņa surnames, SiliņšSiliņa). Confirm these are distinct people before creating separate Wikidata items.

### 0.3 Assign provisional Ars Accordia passport IDs
Before Wikidata work begins, assign stable internal IDs to all 386 rows:

```
Format:  AA/LV/SWB/{zero-padded sequential}
Example: AA/LV/SWB/001  →  Ūdenskritums (Andris Ablēvs, 2003)
         AA/LV/SWB/002  →  Klintis (Andris Ablēvs, 2004)
         ...
         AA/LV/SWB/386  →  Bez nosaukuma (Andris Žegners, 2004)
```

Sequence follows the source `id` column in `swedbank.html` (1–386). These IDs are stable from this point forward.

---

## Phase 1 — Artist reconciliation

### 1.1 Build the SPARQL lookup
For each of the 110 unique artists, query Wikidata by name. Because birth/death years are absent from the source, the initial query relies on name matching alone; lifespan is used for confirmation once a candidate is found.

**SPARQL template (run at query.wikidata.org):**
```sparql
SELECT ?item ?itemLabel ?birthYear ?deathYear ?itemDescription WHERE {
  ?item wdt:P31 wd:Q5 .
  OPTIONAL { ?item wdt:P569 ?birth . BIND(YEAR(?birth) AS ?birthYear) }
  OPTIONAL { ?item wdt:P570 ?death . BIND(YEAR(?death) AS ?deathYear) }
  SERVICE wikibase:label {
    bd:serviceParam wikibase:language "en,lv,de,sv" .
  }
  FILTER(CONTAINS(LCASE(?itemLabel), "heinrihsone"))  -- replace per artist
}
LIMIT 10
```

> **Latvian name forms:** Many artists in this collection are known primarily in Latvian. Try the Latvian form first, then transliterated forms. For artists with surname endings like `-s`/`-a` (gender-marked), search for the stem (e.g. `krollis` and `krolle`).

### 1.2 Priority artists (highest work counts)
Run SPARQL lookups in descending work-count order to tackle the highest-impact artists first:

| Artist | Works | Notes |
|---|---|---|
| Helēna Heinrihsone | 19 | Check for Wikidata item; major Latvian artist |
| Gunārs Krollis | 12 | Illustrator + printmaker; likely has item |
| Tatjana Krivenkova | 11 | Check |
| Kristaps Zarūšs | 10 | Distinguish from Kaspars Zarūšs (5) and Indulis Zarūšs (1) |
| Māris Subačs | 10 | Printmaker; check |
| Andrejs Kalniņš | 9 | Common name — verify with lifespan |
| Irēna Lūse | 9 | Check |
| Ivars Heinrihsons | 9 | Husband of Helēna Heinrihsone — verify separately |
| Inta Celmiņa | 6 | Check |
| Lilija Dinere | 6 | Printmaker; check |
| Kristaps Ģelzis | 6 | Installation/mixed media artist; likely has item |
| Ģirts Muižnieks | 6 | Check |
| Juris Putrāms | 6 | Check |
| Olga Šilova | 6 | Sculptor; check |

### 1.3 Classify each artist

| Result | Action |
|---|---|
| Exact name match + lifespan confirms | Record Q-number |
| Name match, lifespan differs | Manual review — disambiguation or data error |
| No match | Flag for Phase 3 (new artist item) |

### 1.4 Record Q-numbers in the artist register
Add `wikidata_q` and `wikidata_status` columns. This becomes the foreign key for all artwork-level work.

---

## Phase 2 — Artwork reconciliation

### 2.1 SPARQL cross-check by artist
For each artist whose Q-number is confirmed, check whether their artworks already exist on Wikidata:

```sparql
SELECT ?item ?itemLabel ?inventoryNumber ?inception WHERE {
  ?item wdt:P170 wd:Q{artist_Q} .
  OPTIONAL { ?item wdt:P217 ?inventoryNumber }
  OPTIONAL { ?item wdt:P571 ?inception }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en,lv" }
}
```

Match candidates to source rows using title + year + medium. The Swedbank catalogue number (`catalogue_no` in `swedbank.html`) is **not** a museum inventory number — do not use it as a Wikidata P217 value.

### 2.2 OpenRefine reconciliation (recommended for bulk rows)
For the bulk of 386 rows:

1. Load the cleaned CSV into **OpenRefine**
2. Reconcile the `artist` column against `Wikidata: human (Q5)` to confirm Q-numbers
3. Reconcile `title_en` against `Wikidata: work of art` — constrain by `creator = [Q-number]`
4. Review scores: below 80 needs manual review

### 2.3 Tier classification
After reconciliation, classify every row:

| Tier | Condition | Estimated count | Action |
|---|---|---|---|
| **Tier 1** | Artist Q exists AND artwork Q exists | ~30–60 | Enrich existing items |
| **Tier 2** | Artist Q exists, artwork Q does not | ~100–180 | Create artwork item only |
| **Tier 3** | Neither artist Q nor artwork Q exists | ~150–250 | Create both |

> **Higher Tier 3 estimate than LNMA:** The Swedbank collection is primarily contemporary (1977–2007) and includes many artists who are notable in Latvia but have limited or no Wikidata presence. Expect Tier 3 to be the dominant tier.

---

## Phase 3 — Wikidata enrichment (Tier 1)

For each Tier 1 artwork, prepare QuickStatements to add any missing statements to the existing Wikidata item.

### 3.1 Property mapping

| Swedbank field | Wikidata property | Value format | Notes |
|---|---|---|---|
| `title_en` | P1476 (title) | `"Waterfall"@en` | Also add `title_lv` with `@lv` qualifier |
| `artist` | P170 (creator) | Q-number | From artist register |
| `year` / `year_from` | P571 (inception) | `+2003-00-00T00:00:00Z/9` | Precision 9 = year |
| `dimensions_cm` (h) | P2048 (height) | numeric, unit: cm (Q174728) | Parse `H x W` |
| `dimensions_cm` (w) | P2049 (width) | numeric, unit: cm | |
| Collection | P195 (collection) | Q-number for Swedbank/Hansabanka collection | Verify Q — see note below |
| Catalogue number | P217 (inventory number) | `"21"` | With P195 qualifier; only where `catalogue_no` is populated |
| Medium | P186 (material used) | Q-numbers | See medium mapping table |
| Type | P31 (instance of) | Q-numbers | See type mapping table |
| Ars Accordia ID | *(future property)* | `"AA/LV/SWB/001"` | Add once property is approved |

> **Collection Q-number:** Verify the Wikidata Q-number for the Hansabanka / Swedbank art collection before running any QuickStatements. The bank itself is Hansabanka (Q-number TBD — search wikidata.org for `Hansabanka`); the art collection may or may not have a separate item. If no collection item exists, create one in Phase 5 before artwork creation.

**Medium mapping — Swedbank collection (expanded set):**

| Source medium (English portion) | Wikidata P186 values |
|---|---|
| oil on canvas | Q296955 (oil paint) + Q4259259 (canvas) |
| oil on cardboard / oil on wood | Q296955 + Q389782 / Q287 |
| acrylic on canvas | Q28028 (acrylic paint) + Q4259259 |
| acrylic on cardboard | Q28028 + Q389782 |
| watercolour on paper | Q22915256 + Q11472 |
| gouache on paper | Q204330 + Q11472 |
| pastel on paper / pastel on canvas | Q189085 + Q11472 / Q4259259 |
| lithograph on paper | Q15123870 (lithography) + Q11472 |
| etching on paper | Q18218093 (etching) + Q11472 |
| aquatint on paper | Q1279568 (aquatint) + Q11472 |
| screen-print on paper | Q1228600 (screen printing) + Q11472 |
| mezzotint on paper | Q914494 (mezzotint) + Q11472 |
| drypoint on paper | Q1124696 (drypoint) + Q11472 |
| charcoal on paper | Q27976603 (charcoal) + Q11472 |
| Indian ink on paper | Q177239 (India ink) + Q11472 |
| colour pencils on paper/canvas | Q14674 (colored pencil) + Q11472 / Q4259259 |
| tempera on paper | Q175166 (tempera) + Q11472 |
| mixed media on paper/canvas/wood | Q1902763 (mixed media) + substrate Q |
| photo / digital photo | Q125191 (photography) or Q389754 (digital photography) |
| bronze | Q34095 (bronze) |
| aluminium | Q663 (aluminium) |
| author's technique on paper | flag for manual mapping — non-standard medium |
| hand-cast paper | Q11472 (paper) — flag; no standard WD Q for hand-casting |
| light-box | flag for manual mapping |
| embroidery on canvas | Q189105 (embroidery) + Q4259259 |

**Type mapping (expanded for this collection):**

| Object type (inferred from medium) | Wikidata P31 Q |
|---|---|
| Painting (oil/acrylic/tempera on canvas/cardboard) | Q3305213 |
| Drawing (charcoal, pencil, ink on paper) | Q93184 |
| Watercolour | Q18761202 |
| Pastel work | Q12043905 |
| Print — lithograph | Q11060274 |
| Print — etching / aquatint / drypoint | Q18218093 |
| Print — screen-print | Q15123870 (use instance of: print) |
| Print — mezzotint | Q11060274 |
| Print — linocut | Q17524919 |
| Sculpture (bronze, aluminium, ceramic) | Q860861 |
| Photograph / digital photograph | Q125191 |
| Installation / mixed-media object | Q20437094 |
| Video / audio work | Q27119817 |

### 3.2 QuickStatements format (Tier 1 enrichment)
```
Q{artwork_Q}	P1476	"Waterfall"@en
Q{artwork_Q}	P1476	"Ūdenskritums"@lv
Q{artwork_Q}	P217	"21"	P195	Q{collection_Q}
Q{artwork_Q}	P2048	86U174728
Q{artwork_Q}	P2049	43.5U174728
```

Run in batches of 50; review after each batch.

---

## Phase 4 — Artwork creation (Tier 2)

For each Tier 2 artwork, create a new Wikidata item. The artist Q-number is confirmed.

### 4.1 Minimum viable item (required statements)

Every new artwork item needs at minimum:
- **Label** English (`Len`): `title_en` (or transliterated Latvian if English absent)
- **Label** Latvian (`Llv`): `title_lv`
- **P31** (instance of): from type mapping table
- **P170** (creator): artist Q-number
- **P571** (inception): year of creation
- **P195** (collection): Swedbank/Hansabanka collection Q-number

### 4.2 Optional additions (where data available)
- **P217** (inventory number): catalogue_no, with P195 qualifier — only where non-blank
- **P2048 / P2049**: height and width — parse from `dimensions_cm`
- **P186**: material(s) — from medium mapping table
- **P1476** (title): add both `@en` and `@lv` language-tagged strings

### 4.3 QuickStatements batch format for new items
```
CREATE
LAST	Len	"Waterfall"
LAST	Llv	"Ūdenskritums"
LAST	P31	Q11060274
LAST	P170	Q{artist_Q}
LAST	P571	+2003-00-00T00:00:00Z/9
LAST	P195	Q{collection_Q}
LAST	P217	"21"	P195	Q{collection_Q}
LAST	P186	Q15123870
LAST	P186	Q11472
LAST	P2048	86U174728
LAST	P2049	43.5U174728
```

After creation, retrieve the new Q-numbers and record them in the working spreadsheet.

---

## Phase 5 — Full creation (Tier 3)

For each Tier 3 artist, create the artist item first, then the artwork items.

### 5.1 Pre-check: Hansabanka collection item
Before any artwork creation, confirm whether a Wikidata item for the Hansabanka / Swedbank Contemporary Art Collection exists. If not, create it:

```
CREATE
LAST	Len	"Hansabanka Contemporary Art Collection"
LAST	Llv	"Hansabankas mākslas kolekcija"
LAST	P31	Q1020767    # art collection
LAST	P127	Q{Hansabanka_Q}    # owned by: Hansabanka/Swedbank
LAST	P17	Q211    # country: Latvia
```

Record this Q-number — it is the `collection_Q` used in all P195 and P217 statements.

### 5.2 Artist item (minimum viable)
```
CREATE
LAST	Len	"{artist name in English/transliterated}"
LAST	Llv	"{artist name in Latvian}"
LAST	P31	Q5
LAST	P27	Q211    # citizenship: Latvia
LAST	P106	Q1028181    # occupation: painter — adjust per artist (printmaker: Q16947657, sculptor: Q1281618, photographer: Q33231)
LAST	P569	+{birth_year}-00-00T00:00:00Z/9    # if known
LAST	P570	+{death_year}-00-00T00:00:00Z/9    # if known; omit if living
```

> Before creating a new artist item, search Wikidata exhaustively — try Latvian, transliterated, and variant spellings. For living artists (most of this collection), P570 is omitted. Do not guess birth years.

### 5.3 Then follow Phase 4 for artwork items
Use the newly created artist Q-number in all P170 statements.

---

## Phase 6 — Passport ID finalisation and catalogue update

### 6.1 Update the working spreadsheet
After all Wikidata work is complete, the spreadsheet should carry:

| New column | Content |
|---|---|
| `aa_passport_id` | AA/LV/SWB/001 – AA/LV/SWB/386 |
| `wikidata_artwork_q` | Q-number (existing or newly created) |
| `wikidata_artist_q` | Q-number from artist register |
| `tier` | 1 / 2 / 3 |
| `wikidata_status` | `enriched` / `created` / `pending` |
| `aa_artist_id` | AA/LV/ARTIST/xxx |

### 6.2 Ars Accordia catalogue record
Each row in this final spreadsheet is a complete **Ars Accordia art passport** for the Hansabanka/Swedbank collection:

```
AA/LV/SWB/001
├── Collection record:  catalogue no. 21  (Hansabanka / Swedbank)
├── Wikidata:           Q{artwork_Q}
├── Artist:             Andris Ablēvs  →  Q{artist_Q}
├── Title (LV):         Ūdenskritums
├── Title (EN):         Waterfall
├── Year:               2003
├── Medium:             lithograph on paper
├── Dimensions:         86 × 43.5 cm
└── Passport issued:    Ars Accordia  [date]
```

### 6.3 Wikidata project page entry
Log the batch contribution at `Wikidata:Ars Accordia` with:
- Number of items enriched (Tier 1)
- Number of items created (Tier 2 + 3)
- Source: Hansabanka / Swedbank catalogue, pages 222–229
- Date of contribution

---

## Phase 7 — Quality assurance

### 7.1 Spot checks (do after every batch)
- Pick 5 random newly created/enriched items and view them on wikidata.org
- Verify: title correct in both languages, creator links to right person, dimensions reasonable
- Check: no duplicate items created (search by artist Q + title)

### 7.2 Common errors to watch for

| Error | Detection | Fix |
|---|---|---|
| Medium parsed incorrectly (page 223+ uses comma not ` / `) | Wrong medium_en extracted | Check pages 223–229 separately; split on last comma-slash pattern |
| Compound dimensions (e.g. `4 x (30 x 30)`) parsed as single h/w | Anomalous values | Flag in notes; add P2048/P2049 only for single-piece works |
| Decade-only year (`20. gs. 30. gadi`) mapped to a specific year | Overly precise P571 | Use precision 8 (decade) and P1480 = Q5727902 (circa) |
| Date range (`2006/2007`) → wrong inception | Both years present | Use `year_from` as P571 value; add `year_to` in qualifier P582 |
| Family name duplicates (Zarūšs × 3, SiliņšSiliņa × 2, Heinrihsone/Heinrihsons) | Wrong Q-number applied | Verify via birth year; check Wikidata description carefully |
| Living artist receives P570 (date of death) | Collection is mostly post-1970 contemporaries | Omit P570 for living artists |
| Duplicate Wikidata item created | No catalogue_no to dedup on | Before creating, search by P170 + P1476 combination |

### 7.3 Catalogue number as a partial deduplication key
Where `catalogue_no` is present, use it as a secondary check. Before creating a new item, run:
```sparql
SELECT ?item WHERE { ?item wdt:P217 "21" ; wdt:P195 wd:Q{collection_Q} }
```
A result means the item exists — enrich rather than create. Note: ~50% of records have no catalogue number; rely on artist + title + year for those.

---

## Execution sequence summary

```
Phase 0:  Clean dataset · extract artist list (110) · assign AA/LV/SWB/ IDs (386)
Phase 1:  Artist SPARQL lookups → artist register with Q-numbers
Phase 2:  OpenRefine / SPARQL artwork reconciliation → tier classification
Phase 3:  QuickStatements enrichment of Tier 1 items (batches of 50)
Phase 4:  QuickStatements creation of Tier 2 artwork items
Phase 5:  Hansabanka collection item check · artist + artwork creation for Tier 3
Phase 6:  Final spreadsheet update · passport records complete
Phase 7:  Spot checks · project page log entry
```

**Estimated scope:** 386 records across 110 artists. Phases 0–2 are analytical (several hours given no lifespan data in source). Phases 3–5 are execution — Tier 3 is likely dominant, so expect 6–10 QuickStatements sessions of ~50 items each. Phase 6–7 are documentation (2–3 hours).

---

*Ars Accordia — Hansabanka / Swedbank reconciliation workflow · drafted May 2026*
