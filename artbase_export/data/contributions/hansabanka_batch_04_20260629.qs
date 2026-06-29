#title Hansabanka Batch 04 — 14 CREATE items, confirmed artist QIDs
#summary 14 works using artist QIDs already confirmed in previous batches: Blumbergs, Ģelzis, Heinrihsons (Ivars), Krollis, Mitrēvics, Naumovs, Pinnis, Putrāms, Sietiņš. All sourced to Q139986317 with S304 = catalogue_no from swedbank.html OCR.
#prepared_by Arsaccordia
#prepared_at 2026-06-29T00:00:00Z
#source Q139986317 (Hansabanka Contemporary Art Collection catalogue, 2007)
#source_data swedbank.html (OCR of catalogue pages 222–229)

# ══════════════════════════════════════════════════════════════════════
# ARTIST QIDs — ALL CONFIRMED FROM PREVIOUS BATCHES:
#   Ilmārs Blumbergs   → Q13611050
#   Kristaps Ģelzis    → Q94405078
#   Ivars Heinrihsons  → Q99478595
#   Gunārs Krollis     → Q16667368
#   Jānis Mitrēvics    → Q99479594
#   Aleksejs Naumovs   → Q55420369
#   Rūdolfs Pinnis     → Q55984280
#   Juris Putrāms      → Q99481514
#   Guntars Sietiņš    → Q59511477
#
# S304 = catalogue_no from OCR (= the physical page number in the book).
# The "page" column in the OCR (222–229) is the PDF page, NOT the S304 value.
#
# P31 QIDs USED:
#   Q3305213   = painting
#   Q11060274  = print (used for screen-prints, mezzotints)
#   Q18218093  = etching
#   Q838948    = work of art (broad — used for digital print on canvas)
#
# P186 QIDs USED:
#   Q296955  = oil paint
#   Q4259259 = canvas
#   Q11472   = paper
# ══════════════════════════════════════════════════════════════════════


# ── WORK 1: Ilmārs Blumbergs — "Untitled" (Bez nosaukuma), 1993 ──
# Screen-print, pencil on paper · 100 × 70 cm · catalogue no. 31
# OCR row 18: page 222, cat 31

CREATE
LAST	Len	"Untitled"
LAST	Llv	"Bez nosaukuma"
LAST	Den	"1993 print by Ilmārs Blumbergs"
LAST	P31	Q11060274
LAST	P170	Q13611050	S248	Q139986317	S304	"31"
LAST	P571	+1993-00-00T00:00:00Z/9	S248	Q139986317	S304	"31"
LAST	P186	Q11472
LAST	P2048	100U174728	S248	Q139986317	S304	"31"
LAST	P2049	70U174728	S248	Q139986317	S304	"31"


# ── WORK 2: Kristaps Ģelzis — "Mulder" (Malders), 2000 ──
# Digital print on canvas · 118 × 167 cm · catalogue no. 70
# OCR row 84: page 223, cat 70

CREATE
LAST	Len	"Mulder"
LAST	Llv	"Malders"
LAST	Den	"2000 digital print by Kristaps Ģelzis"
LAST	P31	Q838948
LAST	P170	Q94405078	S248	Q139986317	S304	"70"
LAST	P571	+2000-00-00T00:00:00Z/9	S248	Q139986317	S304	"70"
LAST	P186	Q4259259
LAST	P2048	118U174728	S248	Q139986317	S304	"70"
LAST	P2049	167U174728	S248	Q139986317	S304	"70"


# ── WORK 3: Kristaps Ģelzis — "Over. 2" (Pāri. II), 1987 ──
# Screen-print on paper · 150 × 220 cm · catalogue no. 71
# OCR row 81: page 223, cat 71
# Note: "Pāri. I" at same page has no catalogue_no — not submitted.

CREATE
LAST	Len	"Over. 2"
LAST	Llv	"Pāri. II"
LAST	Den	"1987 screen-print by Kristaps Ģelzis"
LAST	P31	Q11060274
LAST	P170	Q94405078	S248	Q139986317	S304	"71"
LAST	P571	+1987-00-00T00:00:00Z/9	S248	Q139986317	S304	"71"
LAST	P186	Q11472
LAST	P2048	150U174728	S248	Q139986317	S304	"71"
LAST	P2049	220U174728	S248	Q139986317	S304	"71"


# ── WORK 4: Ivars Heinrihsons — "Day" (Diena), 2004 ──
# Oil on canvas · 55 × 46 cm · catalogue no. 80
# OCR row 107: page 224, cat 80
# NOTE: "Nakts" (Night) shares cat 80 — both submitted (Works 4 and 5).

CREATE
LAST	Len	"Day"
LAST	Llv	"Diena"
LAST	Den	"2004 painting by Ivars Heinrihsons"
LAST	P31	Q3305213
LAST	P170	Q99478595	S248	Q139986317	S304	"80"
LAST	P571	+2004-00-00T00:00:00Z/9	S248	Q139986317	S304	"80"
LAST	P186	Q296955
LAST	P186	Q4259259
LAST	P2048	55U174728	S248	Q139986317	S304	"80"
LAST	P2049	46U174728	S248	Q139986317	S304	"80"


# ── WORK 5: Ivars Heinrihsons — "Night" (Nakts), 2004 ──
# Oil on canvas · 55 × 46 cm · catalogue no. 80
# OCR row 108: page 224, cat 80

CREATE
LAST	Len	"Night"
LAST	Llv	"Nakts"
LAST	Den	"2004 painting by Ivars Heinrihsons"
LAST	P31	Q3305213
LAST	P170	Q99478595	S248	Q139986317	S304	"80"
LAST	P571	+2004-00-00T00:00:00Z/9	S248	Q139986317	S304	"80"
LAST	P186	Q296955
LAST	P186	Q4259259
LAST	P2048	55U174728	S248	Q139986317	S304	"80"
LAST	P2049	46U174728	S248	Q139986317	S304	"80"


# ── WORK 6: Gunārs Krollis — "Fleeing Time. Illustration to J. Rainis 'The Beginning and the End'" (Skrejošais laiks. Ilustrācija J. Raiņa dzejas ciklam 'Gals un sākums'), 1988/1989 ──
# Etching on paper · 30.5 × 38 cm · catalogue no. 109
# OCR row 169: page 225, cat 109. Title confirmed from physical book (OCR reads 'Šķērsais laiks' — physical book says 'Skrejošais laiks').
# Three works share cat 109 (Works 6, 7, 8).

CREATE
LAST	Len	"Fleeing Time. Illustration to J. Rainis 'The Beginning and the End'"
LAST	Llv	"Skrejošais laiks. Ilustrācija J. Raiņa dzejas ciklam 'Gals un sākums'"
LAST	Den	"1988/1989 etching by Gunārs Krollis"
LAST	P31	Q18218093
LAST	P170	Q16667368	S248	Q139986317	S304	"109"
LAST	P571	+1988-00-00T00:00:00Z/9	S248	Q139986317	S304	"109"
LAST	P186	Q11472
LAST	P2048	30.5U174728	S248	Q139986317	S304	"109"
LAST	P2049	38U174728	S248	Q139986317	S304	"109"


# ── WORK 7: Gunārs Krollis — "The Voice of Pain. Illustration to J. Rainis 'The Beginning and the End'" (Smeldzes balss. Ilustrācija J. Raiņa dzejas ciklam 'Gals un sākums'), 1988/1989 ──
# Etching on paper · 30.5 × 38 cm · catalogue no. 109
# OCR row 170: page 225, cat 109

CREATE
LAST	Len	"The Voice of Pain. Illustration to J. Rainis 'The Beginning and the End'"
LAST	Llv	"Smeldzes balss. Ilustrācija J. Raiņa dzejas ciklam 'Gals un sākums'"
LAST	Den	"1988/1989 etching by Gunārs Krollis"
LAST	P31	Q18218093
LAST	P170	Q16667368	S248	Q139986317	S304	"109"
LAST	P571	+1988-00-00T00:00:00Z/9	S248	Q139986317	S304	"109"
LAST	P186	Q11472
LAST	P2048	30.5U174728	S248	Q139986317	S304	"109"
LAST	P2049	38U174728	S248	Q139986317	S304	"109"


# ── WORK 8: Gunārs Krollis — "Spring Dream. Illustration to J. Rainis 'The Beginning and the End'" (Pavasara sapnis. Ilustrācija J. Raiņa dzejas ciklam 'Gals un sākums'), 1988/1989 ──
# Etching on paper · 30.5 × 38 cm · catalogue no. 109
# OCR row 171: page 225, cat 109

CREATE
LAST	Len	"Spring Dream. Illustration to J. Rainis 'The Beginning and the End'"
LAST	Llv	"Pavasara sapnis. Ilustrācija J. Raiņa dzejas ciklam 'Gals un sākums'"
LAST	Den	"1988/1989 etching by Gunārs Krollis"
LAST	P31	Q18218093
LAST	P170	Q16667368	S248	Q139986317	S304	"109"
LAST	P571	+1988-00-00T00:00:00Z/9	S248	Q139986317	S304	"109"
LAST	P186	Q11472
LAST	P2048	30.5U174728	S248	Q139986317	S304	"109"
LAST	P2049	38U174728	S248	Q139986317	S304	"109"


# ── WORK 9: Jānis Mitrēvics — "The Opposite" (Pretstats), 1993 ──
# Oil on canvas · 100 × 80 cm · catalogue no. 127
# OCR row 217: page 226, cat 127

CREATE
LAST	Len	"The Opposite"
LAST	Llv	"Pretstats"
LAST	Den	"1993 painting by Jānis Mitrēvics"
LAST	P31	Q3305213
LAST	P170	Q99479594	S248	Q139986317	S304	"127"
LAST	P571	+1993-00-00T00:00:00Z/9	S248	Q139986317	S304	"127"
LAST	P186	Q296955
LAST	P186	Q4259259
LAST	P2048	100U174728	S248	Q139986317	S304	"127"
LAST	P2049	80U174728	S248	Q139986317	S304	"127"


# ── WORK 10: Aleksejs Naumovs — "Etruscan Vases under Red Sun" (Etrusku vāzes sarkanā saulē), 1994 ──
# Oil on canvas · 100 × 100 cm · catalogue no. 131
# OCR row 228: page 226, cat 131

CREATE
LAST	Len	"Etruscan Vases under Red Sun"
LAST	Llv	"Etrusku vāzes sarkanā saulē"
LAST	Den	"1994 painting by Aleksejs Naumovs"
LAST	P31	Q3305213
LAST	P170	Q55420369	S248	Q139986317	S304	"131"
LAST	P571	+1994-00-00T00:00:00Z/9	S248	Q139986317	S304	"131"
LAST	P186	Q296955
LAST	P186	Q4259259
LAST	P2048	100U174728	S248	Q139986317	S304	"131"
LAST	P2049	100U174728	S248	Q139986317	S304	"131"


# ── WORK 11: Rūdolfs Pinnis — "A Vase with Fruit" (Vāze ar augļiem), 1973 ──
# Oil on canvas · 93 × 81 cm · catalogue no. 151
# OCR row 266: page 227, cat 151

CREATE
LAST	Len	"A Vase with Fruit"
LAST	Llv	"Vāze ar augļiem"
LAST	Den	"1973 painting by Rūdolfs Pinnis"
LAST	P31	Q3305213
LAST	P170	Q55984280	S248	Q139986317	S304	"151"
LAST	P571	+1973-00-00T00:00:00Z/9	S248	Q139986317	S304	"151"
LAST	P186	Q296955
LAST	P186	Q4259259
LAST	P2048	93U174728	S248	Q139986317	S304	"151"
LAST	P2049	81U174728	S248	Q139986317	S304	"151"


# ── WORK 12: Juris Putrāms — "The Marked One" (Iezīmētais), 1985 ──
# Etching, watercolour on paper · 19 × 13 cm · catalogue no. 160
# OCR row 276: page 227, cat 160

CREATE
LAST	Len	"The Marked One"
LAST	Llv	"Iezīmētais"
LAST	Den	"1985 etching by Juris Putrāms"
LAST	P31	Q18218093
LAST	P170	Q99481514	S248	Q139986317	S304	"160"
LAST	P571	+1985-00-00T00:00:00Z/9	S248	Q139986317	S304	"160"
LAST	P186	Q11472
LAST	P2048	19U174728	S248	Q139986317	S304	"160"
LAST	P2049	13U174728	S248	Q139986317	S304	"160"


# ── WORK 13: Juris Putrāms — "The Tribune" (Tribūns), 1985 ──
# Etching, watercolour on paper · 19 × 13 cm · catalogue no. 162
# OCR row 277: page 227, cat 161 — physically verified: page 162 (OCR error)

CREATE
LAST	Len	"The Tribune"
LAST	Llv	"Tribūns"
LAST	Den	"1985 etching by Juris Putrāms"
LAST	P31	Q18218093
LAST	P170	Q99481514	S248	Q139986317	S304	"162"
LAST	P571	+1985-00-00T00:00:00Z/9	S248	Q139986317	S304	"162"
LAST	P186	Q11472
LAST	P2048	19U174728	S248	Q139986317	S304	"162"
LAST	P2049	13U174728	S248	Q139986317	S304	"162"


# ── WORK 14: Guntars Sietiņš — "Levitation. XIII" (Levitācija. XIII), 1999 ──
# Mezzotint on paper · 22.5 × 44 cm · catalogue no. 166
# OCR row 289: page 228, cat 166

CREATE
LAST	Len	"Levitation. XIII"
LAST	Llv	"Levitācija. XIII"
LAST	Den	"1999 mezzotint by Guntars Sietiņš"
LAST	P31	Q11060274
LAST	P170	Q59511477	S248	Q139986317	S304	"166"
LAST	P571	+1999-00-00T00:00:00Z/9	S248	Q139986317	S304	"166"
LAST	P186	Q11472
LAST	P2048	22.5U174728	S248	Q139986317	S304	"166"
LAST	P2049	44U174728	S248	Q139986317	S304	"166"
