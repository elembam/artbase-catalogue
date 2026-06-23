/* ARS ACCORDIA — Wikidata book contribution — Batch 1
   Generated: 2026-05-30
   Items: 2 book records (SRC-HANSABANKA-2007, SRC-LNMM-PORTRAITS-2009)
   Contributor account: ArsAccordia
   
   BEFORE RUNNING:
   1. Verify FIND queries return empty (no duplicate) — paste each SPARQL block
      into https://query.wikidata.org/ and confirm 0 results.
   2. Paste the CREATE block for each book into https://quickstatements.toolforge.org/
      one book at a time. Record the returned QID.
   3. Run: python3 scripts/record_book_qid.py SRC-HANSABANKA-2007 <QID>
             python3 scripts/record_book_qid.py SRC-LNMM-PORTRAITS-2009 <QID>
*/

/* ── FIND QUERY 1: check Book 1 not already on Wikidata ───────────────────────
   Paste into https://query.wikidata.org/ — must return 0 rows before proceeding.

SELECT ?book ?bookLabel WHERE {
  VALUES ?isbn { "9789984393810" "978-9984-39-381-0" }
  ?book wdt:P212 ?isbn .
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en,lv". }
}

   Status as of 2026-05-30: 0 results ✓  (safe to create)
   ─────────────────────────────────────────────────────────────────────────── */

/* ── BOOK 1: Hansabankas mūsdienu mākslas kolekcija (2007) ─────────────────── */
CREATE
LAST	Llv	"Hansabankas mūsdienu mākslas kolekcija"
LAST	Len	"Hansabanka Contemporary Art Collection"
LAST	Dlv	"2007. gada Hansabankas mūsdienu mākslas kolekcijas katalogs"
LAST	Den	"2007 catalogue of the Hansabanka contemporary art collection"
LAST	P31	Q3331189
LAST	P1476	lv:"Hansabankas mūsdienu mākslas kolekcija"
LAST	P1476	en:"Hansabanka contemporary art collection"
LAST	P212	"978-9984-39-381-0"
LAST	P123	Q104429642
LAST	P2093	"Ilze Žeivaite"
LAST	P577	+2007-00-00T00:00:00Z/9
LAST	P291	Q1773
LAST	P407	Q9078
LAST	P407	Q1860
LAST	P1104	238

/* Notes on Book 1:
   P31  Q3331189 = instance of: version, edition, or translation (book)
   P212          = ISBN-13 (hyphenated format)
   P123 Q104429642 = Swedbank Latvia (formerly AS Hansabanka until 2008)
   P2093 "Ilze Žeivaite" = author as string (title-page spelling used;
          authority heading may differ — upgrade to P50 if WD item found)
   P577 precision /9 = year only
   P291 Q1773 = Riga (place of publication)
   P407 Q9078 = Latvian; P407 Q1860 = English (bilingual catalogue)
   P1104 = number of pages
*/


/* ── FIND QUERY 2: check Book 2 not already on Wikidata ───────────────────────
   Paste into https://query.wikidata.org/ — must return 0 rows before proceeding.

SELECT ?book ?bookLabel WHERE {
  VALUES ?isbn { "9789984807522" "978-9984-807-52-2" }
  ?book wdt:P212 ?isbn .
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en,lv". }
}

   Status as of 2026-05-30: 0 results ✓  (safe to create)
   ─────────────────────────────────────────────────────────────────────────── */

/* ── BOOK 2: Mākslinieks. Portrets. Pašportrets (LNMM, 2009) ──────────────── */
CREATE
LAST	Llv	"Mākslinieks. Portrets. Pašportrets"
LAST	Len	"Artist. Portrait. Self-portrait"
LAST	Dlv	"2009. gada Latvijas Nacionālā mākslas muzeja izstādes katalogs"
LAST	Den	"2009 exhibition catalogue, Latvian National Museum of Art"
LAST	P31	Q3331189
LAST	P1476	lv:"Mākslinieks. Portrets. Pašportrets"
LAST	P1476	en:"Artist. Portrait. Self-portrait"
LAST	P212	"978-9984-807-52-2"
LAST	P50	Q109864986
LAST	P123	Q1370465
LAST	P123	Q30212561
LAST	P577	+2009-00-00T00:00:00Z/9
LAST	P291	Q1773
LAST	P407	Q9078
LAST	P407	Q1860
LAST	P1104	107

/* Notes on Book 2:
   P50  Q109864986 = Dace Lamberga (compiler; has WD item — use P50 not P2093)
   P123 Q1370465  = Latvijas Nacionālais mākslas muzejs (LNMM)
   P123 Q30212561 = Neputns (publisher)
   All others same as Book 1.
   
   Optional enrichment (separate session):
   - P110 (illustrator) → Juris Petraškevičs (if WD item exists; b. 1953)
   - Model the Arsenāls exhibition itself as a separate WD item
   - P921 (main subject) → Latvian portrait painting
*/
