# Hansabanka Batch 02 — Pre-flight Review
## 2026-06-23

**Phase:** 1 (6 CREATE items)
**Source:** Q139986317 — Hansabanka Contemporary Art Collection catalogue, 2007
**Pages:** 222, 223, 226, 227, 228
**Properties:** P31, P170, P571, P186, P2048, P2049
**References:** S248 Q139986317 + S304 (actual page number from catalogue)

**Artist selection notes:**
- Āriņš, Sietiņš, Rozenbergs, Ģelzis: confirmed in previous session
- Mitrēvics + Siliņš: added as replacement pair for Ojārs Pētersons diptych (no Wikidata item)
- Aleksejs Naumovs (Q55420369): held over → Batch 03

---

## Pre-flight checklist

### Artist QIDs — ALL CONFIRMED 2026-06-23

- [x] **Leonīds Āriņš → Q16362314** — confirmed 2026-06-23
- [x] **Jānis Mitrēvics → Q99479594** — confirmed 2026-06-23
- [x] **Herberts Siliņš → Q23054868** — confirmed 2026-06-23
- [x] **Guntars Sietiņš → Q59511477** — confirmed 2026-06-23
- [x] **Egils Rozenbergs → Q56084737** — confirmed 2026-06-23
- [x] **Kristaps Ģelzis → Q94405078** — confirmed 2026-06-23

---

### Duplicate check — search Wikidata before submitting each CREATE

- [ ] **Work 1** — "The Rustling of the Sea" / "Jūras šalkas" (Āriņš, 1960)
- [ ] **Work 2** — "Slackening" / "Atslābums" (Mitrēvics, 1990)
- [ ] **Work 3** — "Autumn" / "Rudens" (Siliņš, 1974)
- [ ] **Work 4** — "Levitation. I" / "Levitācija. I" (Sietiņš, 1995)
- [ ] **Work 5** — "The Sea" / "Jūra" (Rozenbergs, 2004)
- [ ] **Work 6** — "A Picket of Flowers" / "Ziedu pikets" (Ģelzis, 2007)

---

### Material / type QIDs used in this batch

| QID | Label | Confidence | Used for |
|---|---|---|---|
| Q3305213 | painting | High | Works 1, 2, 3, 6 (P31) |
| Q11060274 | print | High | Work 4 (P31 — mezzotint) |
| Q838948 | work of art | High (broad) | Work 5 (P31 — textile+metal) |
| Q296955 | oil paint | High | Works 1, 2, 3 (P186) |
| Q4259259 | canvas | High | Works 1, 2, 3 (P186) |
| Q11472 | paper | High | Works 4, 6 (P186) |
| Q42720 | wool | Medium — verify | Work 5 (P186) |
| Q11426 | metal | Medium — verify | Work 5 (P186) |

**Note on Work 5 (Rozenbergs):** P31 = Q838948 (work of art) is intentionally broad. The medium
"wool and metal" at large dimensions (220×250 cm) suggests a textile wall work. If a better
classification exists (e.g., tapestry = Q838461, textile art = Q12180), it can be added as a
follow-up statement on the created item. Submitting as Q838948 will not be wrong.

---

## Per-work data summary

### Work 1 — Leonīds Āriņš, "The Rustling of the Sea", 1960
- Latvian: *Jūras šalkas*
- Medium: oil on canvas
- Dimensions: 70 (h) × 90 (w) cm
- Catalogue no. 27 · page 222
- P31: Q3305213 (painting)
- P186: Q296955 (oil paint) + Q4259259 (canvas)
- Risk: LOW

### Work 2 — Jānis Mitrēvics, "Slackening", 1990
- Latvian: *Atslābums*
- Medium: oil on canvas
- Dimensions: 200 (h) × 190 (w) cm — large format
- Catalogue no. 126 · page 226
- Date note: 1990 = late Soviet / transition period
- P31: Q3305213 (painting)
- P186: Q296955 + Q4259259
- Risk: LOW

### Work 3 — Herberts Siliņš, "Autumn", 1974
- Latvian: *Rudens*
- Medium: oil on canvas
- Dimensions: 92 (h) × 93 (w) cm — near-square
- Catalogue no. 169 · page 228
- Date note: 1974 = Soviet period; classic landscape subject
- P31: Q3305213 (painting)
- P186: Q296955 + Q4259259
- Risk: LOW

### Work 4 — Guntars Sietiņš, "Levitation. I", 1995
- Latvian: *Levitācija. I*
- Medium: mezzotint on paper
- Dimensions: 34 (h) × 52 (w) cm
- Catalogue no. 167 · page 228
- Note: "I" in the title implies a series; Part II may be elsewhere
- P31: Q11060274 (print)
- P186: Q11472 (paper)
- Risk: LOW

### Work 5 — Egils Rozenbergs, "The Sea", 2004
- Latvian: *Jūra*
- Medium: wool and metal
- Dimensions: 220 (h) × 250 (w) cm — very large format
- Catalogue no. 165 · page 227
- Note: Title "Jūra" may duplicate other works; be careful with the title-check search
- P31: Q838948 (work of art — broad; can be refined)
- P186: Q42720 (wool) + Q11426 (metal)
- Risk: LOW to MEDIUM (type choice is conservative, not wrong)

### Work 6 — Kristaps Ģelzis, "A Picket of Flowers", 2007
- Latvian: *Ziedu pikets*
- Medium: watercolour on paper
- Dimensions: 150 (h) × 280 (w) cm — very wide format
- Catalogue no. 72 · page 223
- Note: Ģelzis is an active contemporary artist (born 1962); check for existing Wikidata items
- P31: Q3305213 (painting)
- P186: Q11472 (paper)
- Risk: LOW

---

## Open question: Hansabanka collection QID

Same as Batch 01 — P195 (held by) is omitted pending confirmation of the collection's QID.

---

## How to submit

Submit one CREATE block at a time:
1. Go to quickstatements.toolforge.org → V1 (tab-separated)
2. Paste only the CLEAN lines for one work (starting with `CREATE`, ending before the next `CREATE`)
3. Do NOT include comment lines (lines starting with `#`)
4. Click Run — verify 100% before moving to the next work

Example paste for Work 1 (clean version, no comments):
```
CREATE
LAST	Len	"The Rustling of the Sea"
LAST	Llv	"Jūras šalkas"
LAST	Den	"1960 painting by Leonīds Āriņš"
LAST	P31	Q3305213
LAST	P170	Q16362314	S248	Q139986317	S304	"222"
LAST	P571	+1960-00-00T00:00:00Z/9	S248	Q139986317	S304	"222"
LAST	P186	Q296955
LAST	P186	Q4259259
LAST	P2048	70U174728	S248	Q139986317	S304	"222"
LAST	P2049	90U174728	S248	Q139986317	S304	"222"
```

---

## After submission

1. Record returned QIDs in the table below and in `CONTRIBUTIONS_LOG.md`
2. Create ArtBase passport JSONs: `artbase_export/data/artworks/AA/LV/HANS/007–012.json`
3. Add P195 (held by Hansabanka collection) once collection QID is resolved

---

## Submission status

| Work | QID | Submitted |
|---|---|---|
| Work 1 — Jūras šalkas (Āriņš 1960) | _TBD_ | ___ |
| Work 2 — Atslābums (Mitrēvics 1990) | _TBD_ | ___ |
| Work 3 — Rudens (Siliņš 1974) | _TBD_ | ___ |
| Work 4 — Levitācija. I (Sietiņš 1995) | _TBD_ | ___ |
| Work 5 — Jūra (Rozenbergs 2004) | _TBD_ | ___ |
| Work 6 — Ziedu pikets (Ģelzis 2007) | _TBD_ | ___ |
