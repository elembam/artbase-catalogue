#title Hansabanka Batch 01 — 6 CREATE items from the Hansabanka Contemporary Art Collection
#summary 6 works from the Hansabanka/Swedbank collection: 2 Blumbergs prints, 1 Skulme, 1 Zariņš, 1 Šemjakins, 1 Maldupe. All sourced to Q139986317 with page numbers from the catalogue.
#prepared_by Arsaccordia
#prepared_at 2026-06-23T00:00:00Z
#phase 1
#review_doc hansabanka_batch_01_20260623.review.md

# ══════════════════════════════════════════════════════════════════════
# SOURCE:
#   S248 → Q139986317 (Hansabanka Contemporary Art Collection catalogue, 2007)
#          Confirmed on Wikidata; item already exists.
#   S304 → actual page numbers from catalogue (pp. 222–229)
#          Sourced from structured OCR of catalogue pages.
#
# COLLECTION:
#   P195 (held by) → QHANSABANKA_COLLECTION
#   The Hansabanka/Swedbank art collection does not yet have a confirmed
#   Wikidata QID. Omitted from this batch. Add as a follow-up once resolved.
#
# STILL NEEDED (resolve before submitting):
#   QARTIST_BLUMBERGS     = QID for Ilmārs Blumbergs (Latvian artist, 1943–2016)
#   QARTIST_SKULME        = QID for Džemma Skulme (Latvian artist, 1925–2022)
#   QARTIST_ZARINS_INDULIS = QID for Indulis Zariņš (Latvian artist, 1929–1997)
#   QARTIST_SHEMYAKIN     = QID for Mihails Šemjakins (likely Q214867 — verify)
#   QARTIST_MALDUPE       = QID for Vija Maldupe (Latvian painter)
#
# BEFORE SUBMITTING:
#   1. Verify no duplicate Wikidata items exist (especially for Šemjakins —
#      his works are internationally documented and may already be on Wikidata).
#   2. Confirm all artist QIDs by searching Wikidata.
#   3. Replace all QARTIST_* placeholders with real QIDs.
# ══════════════════════════════════════════════════════════════════════


# ── WORK 1: Ilmārs Blumbergs — "Verities of Suffering" (Ciešanu atziņas), 1999 ──
# Screen-print, pencil on paper · 61 × 90.5 cm · catalogue no. 32 · p. 222

CREATE
LAST	Len	"Verities of Suffering"
LAST	Llv	"Ciešanu atziņas"
LAST	Den	"1999 print by Ilmārs Blumbergs"
LAST	P31	Q11060274
LAST	P170	QARTIST_BLUMBERGS	S248	Q139986317	S304	"222"
LAST	P571	+1999-00-00T00:00:00Z/9	S248	Q139986317	S304	"222"
LAST	P186	Q11472
LAST	P2048	61U174728	S248	Q139986317	S304	"222"
LAST	P2049	90.5U174728	S248	Q139986317	S304	"222"


# ── WORK 2: Ilmārs Blumbergs — "The Silver Age" (Sudraba laikmets), 1998 ──
# Screen-print on paper · 59 × 89 cm · catalogue no. 33 · p. 222

CREATE
LAST	Len	"The Silver Age"
LAST	Llv	"Sudraba laikmets"
LAST	Den	"1998 print by Ilmārs Blumbergs"
LAST	P31	Q11060274
LAST	P170	QARTIST_BLUMBERGS	S248	Q139986317	S304	"222"
LAST	P571	+1998-00-00T00:00:00Z/9	S248	Q139986317	S304	"222"
LAST	P186	Q11472
LAST	P2048	59U174728	S248	Q139986317	S304	"222"
LAST	P2049	89U174728	S248	Q139986317	S304	"222"


# ── WORK 3: Džemma Skulme — "Caryatid (Scare-Crow)" (Kariatīde), 2004 ──
# Oil, collage on cardboard · 150 × 120 cm · catalogue no. 171 · p. 228
# NOTE: catalogue dates this as "2004/2006" — 2004 used as inception year.

CREATE
LAST	Len	"Caryatid (Scare-Crow)"
LAST	Llv	"Kariatīde. (Putnu biedēklis)"
LAST	Den	"2004 painting by Džemma Skulme"
LAST	P31	Q3305213
LAST	P170	QARTIST_SKULME	S248	Q139986317	S304	"228"
LAST	P571	+2004-00-00T00:00:00Z/9	S248	Q139986317	S304	"228"
LAST	P186	Q296955
LAST	P186	Q614700
LAST	P2048	150U174728	S248	Q139986317	S304	"228"
LAST	P2049	120U174728	S248	Q139986317	S304	"228"


# ── WORK 4: Indulis Zariņš — "In Memory of Chagall" (Šagāla piemiņai), 1996 ──
# Oil on canvas · 112 × 96 cm · catalogue no. 209 · p. 229

CREATE
LAST	Len	"In Memory of Chagall"
LAST	Llv	"Šagāla piemiņai"
LAST	Den	"1996 painting by Indulis Zariņš"
LAST	P31	Q3305213
LAST	P170	QARTIST_ZARINS_INDULIS	S248	Q139986317	S304	"229"
LAST	P571	+1996-00-00T00:00:00Z/9	S248	Q139986317	S304	"229"
LAST	P186	Q296955
LAST	P186	Q4259259
LAST	P2048	112U174728	S248	Q139986317	S304	"229"
LAST	P2049	96U174728	S248	Q139986317	S304	"229"


# ── WORK 5: Mihails Šemjakins — "The Belly of Paris" (Parīzes vēders), 1976 ──
# Lithograph on paper · 64 × 46 cm · catalogue no. 192 · p. 228
# IMPORTANT: Šemjakins (= Mikhail Shemyakin) is internationally famous.
#   Likely QID: Q214867 — VERIFY before submitting.
#   This work may ALREADY exist on Wikidata — search before CREATEing.
#   If it exists: convert to ENRICH (add P195, P2048, P2049 to the existing item).

CREATE
LAST	Len	"The Belly of Paris"
LAST	Llv	"Parīzes vēders"
LAST	Den	"1976 lithograph by Mikhail Shemyakin"
LAST	P31	Q185511
LAST	P170	QARTIST_SHEMYAKIN	S248	Q139986317	S304	"228"
LAST	P571	+1976-00-00T00:00:00Z/9	S248	Q139986317	S304	"228"
LAST	P186	Q11472
LAST	P2048	64U174728	S248	Q139986317	S304	"228"
LAST	P2049	46U174728	S248	Q139986317	S304	"228"


# ── WORK 6: Vija Maldupe — "Carnival" (Karnevāls), 1977 ──
# Oil on canvas · 79 × 94 cm · catalogue no. 121 · p. 226

CREATE
LAST	Len	"Carnival"
LAST	Llv	"Karnevāls"
LAST	Den	"1977 painting by Vija Maldupe"
LAST	P31	Q3305213
LAST	P170	QARTIST_MALDUPE	S248	Q139986317	S304	"226"
LAST	P571	+1977-00-00T00:00:00Z/9	S248	Q139986317	S304	"226"
LAST	P186	Q296955
LAST	P186	Q4259259
LAST	P2048	79U174728	S248	Q139986317	S304	"226"
LAST	P2049	94U174728	S248	Q139986317	S304	"226"
