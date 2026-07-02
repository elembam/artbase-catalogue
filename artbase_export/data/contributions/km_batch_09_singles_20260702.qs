#title Klasiskais modernisms — Batch 09: Single-work artists (4 new works)
#summary Purvītis (Q2663470), Matvejs (Q16356282), Siliņš (Q16697625), Plase (Q109894439): 1 work each.
#         Zeltiņš and Silzemnieks EXCLUDED — not yet on Wikidata; see notes below.
#         S248 = Q109893311  S304 = physical page number.
#prepared_by ArsAccordia
#prepared_at 2026-07-02T00:00:00Z

# ══════════════════════════════════════════════════════════════════════
# EXCLUDED ARTISTS — not on Wikidata; create artist items before adding artwork items
#
#   VOLDEMĀRS ZELTIŅŠ
#   Work: "Jumti. Studija" (Rooftops. Study) · p.14 · Kartons, eļļa · 30×24.5 · LNMM
#   Date: "20. gs. sākums" (early 20th century) — imprecise; cannot express in P571
#   Action: create Wikidata artist item, then add artwork pointing to new QID
#
#   ALBERTS SILZEMNIEKS (also known as Krūmiņš)
#   Work: "Klusā daba ar avīzi" (Still Life with a Newspaper) · p.205
#         Ap 1923. Audekls, eļļa. 64×95. LNMM
#   Biographical data available: born 1894-10-14, executed Moscow 1941
#   Action: create Wikidata artist item (see latvian_art_biographies_ocr.html for data),
#            then add artwork pointing to new QID
# ══════════════════════════════════════════════════════════════════════

# QIDs: Purvītis Q2663470 · Matvejs Q16356282 · Siliņš Q16697625 · Plase Q109894439
# LNMM Q1370465 · oil Q296955 · canvas Q4259259 · cardboard Q18668582
# watercolour Q3374389 · paper Q11472 · P1480 circa Q5727902 · unit cm U174728


# ── 1: Vilhelms Purvītis — "Bērzi" (Birches), c.1900 · p.14 · LNMM
# Canvas on cardboard, oil · 54.2 × 36 cm
# Note: Purvītis has 4 existing Wikidata items (all c.1910); this c.1900 work is new.
CREATE
LAST	Len	"Birches"
LAST	Llv	"Bērzi"
LAST	Den	"c.1900 painting by Vilhelms Purvītis"
LAST	P31	Q3305213
LAST	P170	Q2663470	S248	Q109893311	S304	"14"
LAST	P571	+1900-00-00T00:00:00Z/9	P1480	Q5727902	S248	Q109893311	S304	"14"
LAST	P186	Q296955
LAST	P186	Q4259259
LAST	P186	Q18668582
LAST	P2048	54.2U174728	S248	Q109893311	S304	"14"
LAST	P2049	36U174728	S248	Q109893311	S304	"14"
LAST	P195	Q1370465


# ── 2: Voldemārs Matvejs — "Ceļā uz rožaino pasaku pili" (On the Way to the Pink Fairy-Tale Castle), c.1911–1912 · p.15
# Location unknown · no medium/dimensions given in source
# Reproduced in: Voldemārs Matvejs: Raksti. Darbu katalogs. Sarakste. Sast. I. Bužinska. Rīga: VMM, 2002, 11. lpp.
CREATE
LAST	Len	"On the Way to the Pink Fairy-Tale Castle"
LAST	Llv	"Ceļā uz rožaino pasaku pili"
LAST	Den	"c.1911 painting by Voldemārs Matvejs"
LAST	P31	Q3305213
LAST	P170	Q16356282	S248	Q109893311	S304	"15"
LAST	P571	+1911-00-00T00:00:00Z/9	P1480	Q5727902	S248	Q109893311	S304	"15"


# ── 3: Jānis Siliņš — "Sieviete" (Woman), 1921 · p.144 · private collection
# Canvas, oil · 71 × 46 cm
CREATE
LAST	Len	"Woman"
LAST	Llv	"Sieviete"
LAST	Den	"1921 painting by Jānis Siliņš"
LAST	P31	Q3305213
LAST	P170	Q16697625	S248	Q109893311	S304	"144"
LAST	P571	+1921-00-00T00:00:00Z/9	S248	Q109893311	S304	"144"
LAST	P186	Q296955
LAST	P186	Q4259259
LAST	P2048	71U174728	S248	Q109893311	S304	"144"
LAST	P2049	46U174728	S248	Q109893311	S304	"144"


# ── 4: Jānis Plase — "Tējnīcā" (In a Teahouse), c.1929 · p.215 · LNMM
# Canvas, oil · 118 × 100 cm
# Note: Plase item Q109894439 has no birth/death dates yet; these are documented in
#       latvian_art_biographies_ocr.html (born 1892-01-04, died 1929-08-23).
CREATE
LAST	Len	"In a Teahouse"
LAST	Llv	"Tējnīcā"
LAST	Den	"c.1929 painting by Jānis Plase"
LAST	P31	Q3305213
LAST	P170	Q109894439	S248	Q109893311	S304	"215"
LAST	P571	+1929-00-00T00:00:00Z/9	P1480	Q5727902	S248	Q109893311	S304	"215"
LAST	P186	Q296955
LAST	P186	Q4259259
LAST	P2048	118U174728	S248	Q109893311	S304	"215"
LAST	P2049	100U174728	S248	Q109893311	S304	"215"
LAST	P195	Q1370465
