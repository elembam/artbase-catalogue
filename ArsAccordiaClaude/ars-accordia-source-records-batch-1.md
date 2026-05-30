# Ars Accordia — Source Records: Batch 1

*Two catalogue sources, fully set up for the `sources/` registry and for Wikidata. Both land squarely on the mission: a **corporate collection** (Hansabanka) and a **national-museum exhibition catalogue** (LNMM).*

---

## Status of identifiers

**Verified QIDs (safe to use):**
- Dace Lamberga (compiler/author, Book 2) → **Q109864986**
- Publisher of Book 1 — the Latvian bank formerly named AS Hansabanka → **Q104429642**

**Verify on Wikidata before submitting (3 items):**
1. **Book 1 author spelling** — "Žeivaite" (title page) vs "Žeivate" (authority heading). Confirm against the person's LNB/LNDB record, or omit the author line.
2. **Book 2 — LNMM QID.** The museum certainly has a Wikidata item; look it up directly (search *Latvijas Nacionālais mākslas muzejs* on Wikidata, or follow the "Wikidata item" link from its Wikipedia page). *(Note: I referenced `Q1370465` for the museum earlier in our conversation but did not verify it — confirm the exact QID independently before using it.)*
3. **Book 2 — Neputns QID.** The publisher has a Wikidata item; look it up the same way.

Get those, drop them into the placeholders below, and both books are ready to submit.

---

# Book 1 — Hansabanka Contemporary Art Collection (2007)

**`SRC-HANSABANKA-2007` · ISBN 9789984393810 · corporate collection catalogue**

### Registry record

```json
// data/sources/SRC-HANSABANKA-2007.json
{
  "source_id": "SRC-HANSABANKA-2007",
  "citation": "Žeivaite, Ilze, et al. Hansabankas mūsdienu mākslas kolekcija / Hansabanka Contemporary Art Collection. Rīga: Hansabanka, 2007.",
  "title": "Hansabankas mūsdienu mākslas kolekcija",
  "title_parallel_en": "Hansabanka Contemporary Art Collection",
  "type": "collection catalogue",
  "authors": ["Ilze Žeivaite"],
  "author_note": "Text authors: Ilze Žeivaite + others (u.c.). Authority heading spells surname 'Žeivate' — verify before citing.",
  "publisher": "Hansabanka",
  "publisher_wikidata_qid": "Q104429642",
  "publication_year": 2007,
  "place": "Rīga",
  "language": ["lv", "en"],
  "pages": 238,
  "isbn_13": "9789984393810",
  "isbn_10": null,
  "udc": "7.074(474.3)(083.82)",
  "subject": "Latvian art, 20th–21st century — catalogues",
  "documents_collection": "Hansabanka Contemporary Art Collection (corporate collection)",
  "wikidata_qid": null,
  "wikidata_status": "unresolved",
  "lndb_id": null
}
```

### Step 1 — find query (run first)

```sparql
SELECT ?book ?bookLabel WHERE {
  VALUES ?isbn { "9789984393810" "978-9984-39-381-0" }
  ?book wdt:P212 ?isbn .
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en,lv". }
}
```

### Step 2 — CREATE batch (if find returns nothing)

```
CREATE
LAST	Llv	"Hansabankas mūsdienu mākslas kolekcija"
LAST	Len	"Hansabanka Contemporary Art Collection"
LAST	Dlv	"2007. gada Hansabankas mūsdienu mākslas kolekcijas katalogs"
LAST	Den	"2007 catalogue of the Hansabanka contemporary art collection"
LAST	P31	Q3331189
LAST	P1476	lv:"Hansabankas mūsdienu mākslas kolekcija"
LAST	P1476	en:"Hansabanka contemporary art collection"
LAST	P212	"9789984393810"
LAST	P123	Q104429642
LAST	P2093	"Ilze Žeivaite"
LAST	P577	+2007-00-00T00:00:00Z/9
LAST	P291	Q1773
LAST	P407	Q9078
LAST	P407	Q1860
LAST	P1104	238
```

Notes:
- `P123 = Q104429642` — the publisher (the Latvian bank, named AS Hansabanka until 2008).
- `P2093 = "Ilze Žeivaite"` — **confirm spelling or remove** (see verify item 1). If she has a Wikidata item, use `P50 <QID>` instead.
- `P407` twice (Latvian + English, bilingual catalogue).
- `P212` shown plain; enter as hyphenated on the book for Wikidata's preferred format.

---

# Book 2 — Artist. Portrait. Self-portrait (LNMM, 2009)

**`SRC-LNMM-PORTRAITS-2009` · ISBN 9789984807522 · exhibition catalogue**

### Registry record

```json
// data/sources/SRC-LNMM-PORTRAITS-2009.json
{
  "source_id": "SRC-LNMM-PORTRAITS-2009",
  "citation": "Lamberga, Dace (comp.). Mākslinieks. Portrets. Pašportrets / Artist. Portrait. Self-portrait. Rīga: Latvijas Nacionālais mākslas muzejs; Neputns, 2009.",
  "title": "Mākslinieks. Portrets. Pašportrets",
  "title_parallel_en": "Artist. Portrait. Self-portrait",
  "type": "exhibition catalogue",
  "exhibition": {
    "venue": "Latvijas Nacionālā mākslas muzeja izstāžu zāle \"Arsenāls\"",
    "start": "2009-11-05",
    "end": "2010-01-17"
  },
  "compiler": "Dace Lamberga",
  "compiler_wikidata_qid": "Q109864986",
  "designer": "Juris Petraškevičs",
  "publishers": ["Latvijas Nacionālais mākslas muzejs", "Neputns"],
  "publisher_wikidata_qids": ["[LNMM QID — verify]", "[Neputns QID — verify]"],
  "publication_year": 2009,
  "place": "Rīga",
  "language": ["lv", "en"],
  "pages": 107,
  "isbn_13": "9789984807522",
  "isbn_10": null,
  "udc": "7.041.5(474.3)(083.824)",
  "subject": "Latvian portrait painting; artists — Latvia — portraits; exhibition catalogues",
  "wikidata_qid": null,
  "wikidata_status": "unresolved",
  "lndb_id": null
}
```

### Step 1 — find query (run first)

```sparql
SELECT ?book ?bookLabel WHERE {
  VALUES ?isbn { "9789984807522" "978-9984-807-52-2" }
  ?book wdt:P212 ?isbn .
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en,lv". }
}
```

### Step 2 — CREATE batch (if find returns nothing)

Fill the two `[…_QID]` placeholders first (verify items 2 and 3).

```
CREATE
LAST	Llv	"Mākslinieks. Portrets. Pašportrets"
LAST	Len	"Artist. Portrait. Self-portrait"
LAST	Dlv	"2009. gada Latvijas Nacionālā mākslas muzeja izstādes katalogs"
LAST	Den	"2009 exhibition catalogue, Latvian National Museum of Art"
LAST	P31	Q3331189
LAST	P1476	lv:"Mākslinieks. Portrets. Pašportrets"
LAST	P1476	en:"Artist. Portrait. Self-portrait"
LAST	P212	"9789984807522"
LAST	P50	Q109864986
LAST	P123	[LNMM_QID]
LAST	P123	[NEPUTNS_QID]
LAST	P577	+2009-00-00T00:00:00Z/9
LAST	P291	Q1773
LAST	P407	Q9078
LAST	P407	Q1860
LAST	P1104	107
```

Notes:
- `P50 = Q109864986` — Dace Lamberga, the compiler and text author (verified).
- `P123` twice — the two co-publishers (LNMM + Neputns); fill the QIDs.
- `P407` twice (Latvian + English).
- `P291 = Q1773` (Riga), `P577 = 2009`, `P1104 = 107`.

**Optional enrichment (later):**
- `P110` (illustrator) → Juris Petraškevičs, the designer, if he has a Wikidata item (his record gives b. 1953).
- Model the **exhibition** itself as a separate entity (the show at "Arsenāls", 2009-11-05 to 2010-01-17) and link the catalogue to it — useful once you start cataloguing the portrait works it documents.
- `P921` (main subject) → Latvian portrait painting.

---

## Before you submit — consolidated checklist

```
[ ] Verify item 1 — Book 1 author: "Žeivaite" vs "Žeivate" (confirm or drop P2093)
[ ] Verify item 2 — Book 2: LNMM Wikidata QID (look up directly on Wikidata)
[ ] Verify item 3 — Book 2: Neputns Wikidata QID (look up directly on Wikidata)
[ ] Run BOTH find-queries — do not create a duplicate
[ ] If absent, preview each CREATE batch in QuickStatements, then run (per the runbook)
[ ] Record each returned QID into its sources/ JSON (wikidata_qid, status: created)
[ ] (Optional) add the LNB/LNDB IDs for both books into the registry records
```

Once both books have QIDs, every fact you draw from them is cited with `S248 <book_QID>  S304 "<page>"` — the strongest reference type on Wikidata, per the book-reference procedure.

---

*Companion documents: the Wikidata book-reference procedure (citing these books on statements), the QuickStatements runbook (batch submission), and the catalogue-sources spec (the automated registry + contribution pipeline).*
