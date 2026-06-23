#title LNMM Batch 02 — Artwork items: 1 enrichment + 4 CREATEs
#summary Enrich Q22043968 (Princess with a Monkey); CREATE 4 new artwork items for Carousel, From Church (After the Service), Young Gipsy Woman, Country Landscape. All five works held at LNMM.
#prepared_by Arsaccordia
#prepared_at 2026-06-20T00:00:00Z
#phase 2
#review_doc lnmm_batch_02_artwork_items_20260620.review.md

# ══════════════════════════════════════════════════════════════════════
# RESOLVED:
#   S248 source  → Q139986481 (Artist. Portrait. Self-portrait)
#                  Confirmed 2026-06-20 — item already on Wikidata.
#   P195 collection → Q1370465 (Latvian National Museum of Art)
#                  Confirmed 2026-06-20.
#
# STILL NEEDED:
#   PAGE_TO_CONFIRM = Replace with actual page number from Lamberga 2009
#                     (Q139986481) once book is in hand.
#                     If page cannot be confirmed, remove S248/S304 pair.
# ══════════════════════════════════════════════════════════════════════


# ── 001 ENRICH: Q22043968 "Princess with a Monkey" (already exists) ──
# Janis Rozentāls, 1913, oil on canvas, 147.5 × 71.0 cm, VMM GL-5668
# Only add statements not yet present — check Q22043968 on Wikidata first.

Q22043968	P195	Q1370465	S248	Q139986481	S304	"PAGE_TO_CONFIRM"
Q22043968	P217	"VMM GL-5668"	S248	Q139986481	S304	"PAGE_TO_CONFIRM"
Q22043968	P2048	147.5U174728	S248	Q139986481	S304	"PAGE_TO_CONFIRM"
Q22043968	P2049	71U174728	S248	Q139986481	S304	"PAGE_TO_CONFIRM"


# ── 004 CREATE: "Carousel" — Jānis Tīdemanis, 1932 ───────────────────
# Oil on canvas, 65 × 95 cm, VMM GL-2822

CREATE
LAST	Len	"Carousel"
LAST	Den	"1932 painting by Jānis Tīdemanis"
LAST	P31	Q3305213
LAST	P170	Q4457149	S248	Q139986481	S304	"PAGE_TO_CONFIRM"
LAST	P571	+1932-00-00T00:00:00Z/9	S248	Q139986481	S304	"PAGE_TO_CONFIRM"
LAST	P186	Q296955
LAST	P186	Q4259259
LAST	P2048	65U174728	S248	Q139986481	S304	"PAGE_TO_CONFIRM"
LAST	P2049	95U174728	S248	Q139986481	S304	"PAGE_TO_CONFIRM"
LAST	P195	Q1370465
LAST	P217	"VMM GL-2822"


# ── 006 CREATE: "From Church (After the Service)" — Janis Rozentāls, 1894 ──
# Oil on canvas, 175 × 103 cm, VMM GL-55

CREATE
LAST	Len	"From Church (After the Service)"
LAST	Den	"1894 painting by Janis Rozentāls"
LAST	P31	Q3305213
LAST	P170	Q975168	S248	Q139986481	S304	"PAGE_TO_CONFIRM"
LAST	P571	+1894-00-00T00:00:00Z/9	S248	Q139986481	S304	"PAGE_TO_CONFIRM"
LAST	P186	Q296955
LAST	P186	Q4259259
LAST	P2048	175U174728	S248	Q139986481	S304	"PAGE_TO_CONFIRM"
LAST	P2049	103U174728	S248	Q139986481	S304	"PAGE_TO_CONFIRM"
LAST	P195	Q1370465
LAST	P217	"VMM GL-55"


# ── 017 CREATE: "Young Gipsy Woman" — Kārlis Hūns, 1870 ──────────────
# Oil on canvas, 125 × 90 cm, VMM GL-1509

CREATE
LAST	Len	"Young Gipsy Woman"
LAST	Den	"1870 painting by Kārlis Hūns"
LAST	P31	Q3305213
LAST	P170	Q4152126	S248	Q139986481	S304	"PAGE_TO_CONFIRM"
LAST	P571	+1870-00-00T00:00:00Z/9	S248	Q139986481	S304	"PAGE_TO_CONFIRM"
LAST	P186	Q296955
LAST	P186	Q4259259
LAST	P2048	125U174728	S248	Q139986481	S304	"PAGE_TO_CONFIRM"
LAST	P2049	90U174728	S248	Q139986481	S304	"PAGE_TO_CONFIRM"
LAST	P195	Q1370465
LAST	P217	"VMM GL-1509"


# ── 019 CREATE: "Country Landscape" — Jūlijs Feders, 1880 ────────────
# Oil on canvas, 80 × 120 cm, VMM GL-1501
# NOTE: S248/S304 removed — country landscape cannot appear in a portraits
# catalogue. No verified source citation available; statements are unsourced.

CREATE
LAST	Len	"Country Landscape"
LAST	Den	"1880 painting by Jūlijs Feders"
LAST	P31	Q3305213
LAST	P170	Q1977258
LAST	P571	+1880-00-00T00:00:00Z/9
LAST	P186	Q296955
LAST	P186	Q4259259
LAST	P2048	80U174728
LAST	P2049	120U174728
LAST	P195	Q1370465
LAST	P217	"VMM GL-1501"
