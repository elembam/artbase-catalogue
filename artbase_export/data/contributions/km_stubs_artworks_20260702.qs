#title KM artwork stubs — Zeltiņš + Silzemnieks (TEMPLATE — edit QIDs before running)
#
#  ┌─────────────────────────────────────────────────────────────────────┐
#  │  BEFORE RUNNING: replace the two placeholders with real Wikidata QIDs │
#  │                                                                     │
#  │  Q140400463     → the new QID assigned to Voldemārs Zeltiņš    │
#  │  Q140400464 → the new QID assigned to Alberts Silzemnieks  │
#  │                                                                     │
#  │  Get these by running km_stubs_artists_zeltins_silzemnieks.qs first │
#  └─────────────────────────────────────────────────────────────────────┘
#
#summary Zeltiņš (1 work) + Silzemnieks (1 work). S248 = Q109893311.
#prepared_by ArsAccordia
#prepared_at 2026-07-02T00:00:00Z

# QIDs: LNMM Q1370465 · oil Q296955 · canvas Q4259259 · cardboard Q18668582
# P1480 circa Q5727902 · unit cm U174728


# ── Zeltiņš: "Jumti. Studija" (Rooftops. Study), early 20th century · p.14 · LNMM
# Oil on cardboard · 30 × 24.5 cm
# Date: "20. gs. sākums" — encoded as decade precision (1900s) with circa qualifier.
CREATE
LAST	Len	"Rooftops. Study"
LAST	Llv	"Jumti. Studija"
LAST	Den	"early 20th century painting by Voldemārs Zeltiņš"
LAST	P31	Q3305213
LAST	P170	Q140400463	S248	Q109893311	S304	"14"
LAST	P571	+1905-00-00T00:00:00Z/8	P1480	Q5727902	S248	Q109893311	S304	"14"
LAST	P186	Q296955
LAST	P186	Q18668582
LAST	P2048	30U174728	S248	Q109893311	S304	"14"
LAST	P2049	24.5U174728	S248	Q109893311	S304	"14"
LAST	P195	Q1370465


# ── Silzemnieks: "Klusā daba ar avīzi" (Still Life with a Newspaper), c.1923 · p.205 · LNMM
# Oil on canvas · 64 × 95 cm
CREATE
LAST	Len	"Still Life with a Newspaper"
LAST	Llv	"Klusā daba ar avīzi"
LAST	Den	"c.1923 painting by Alberts Silzemnieks"
LAST	P31	Q3305213
LAST	P170	Q140400464	S248	Q109893311	S304	"205"
LAST	P571	+1923-00-00T00:00:00Z/9	P1480	Q5727902	S248	Q109893311	S304	"205"
LAST	P186	Q296955
LAST	P186	Q4259259
LAST	P2048	64U174728	S248	Q109893311	S304	"205"
LAST	P2049	95U174728	S248	Q109893311	S304	"205"
LAST	P195	Q1370465
