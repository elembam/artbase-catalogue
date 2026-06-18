# Phase 2 — P973 Additions: Hūns, Feders, Tīdemanis
## 2026-06-15

**Phase:** 1 (described at URL — Ars Accordia artist pages)  
**Statements proposed:** 3  
**Distinct artists:** 3  
**Properties:** P973 (described at URL) × 3  
**Purpose:** Complete P973 coverage for 3 artists whose Wikidata QIDs were previously unresolved. QIDs confirmed 2026-06-15, JSON records updated, artist pages regenerated.  
**References on every statement:** S854 (reference URL: arsaccordia.com), S813 (retrieved: 2026-06-15)

---

## Per-statement review

### Q4152126 Kārlis Hūns
- **ArtBase ID:** ART-HUNS-1831
- **Lifespan:** 1831–1877
- **Wikidata label (lv):** Kārlis Hūns
- **Wikidata label (de):** Karl Jacob Wilhelm Huhn (Baltic German name)
- **Adding** P973 = "https://arsaccordia.com/artists/ART-HUNS-1831.html"
- **Page exists:** ✅ `artists/ART-HUNS-1831.html`
- **Wikidata item verified:** https://www.wikidata.org/wiki/Q4152126
- **Birth confirmed:** 1831-11-13 (matches ArtBase)
- **Death confirmed:** 1877-01-16 (matches ArtBase)
- **Risk:** LOW — 19th-century Baltic German painter, unambiguous match on dates

### Q1977258 Jūlijs Feders
- **ArtBase ID:** ART-FEDERS-1838
- **Lifespan:** 1838–1909
- **Wikidata label (lv):** Jūlijs Feders
- **Wikidata label (en):** Julius Fedders
- **Adding** P973 = "https://arsaccordia.com/artists/ART-FEDERS-1838.html"
- **Page exists:** ✅ `artists/ART-FEDERS-1838.html`
- **Wikidata item verified:** https://www.wikidata.org/wiki/Q1977258
- **Birth confirmed:** 1838-06-19 (matches ArtBase)
- **Death confirmed:** 1909-01-19 (matches ArtBase)
- **Risk:** LOW — Latvian landscape painter and photographer, confirmed by dates

### Q4457149 Jānis Tīdemanis
- **ArtBase ID:** ART-TIDEMANIS-1897
- **Lifespan:** 1897–1964
- **Wikidata label (lv):** Jānis Tīdemanis
- **Wikidata full name:** Jānis Ferdinands Tīdemanis
- **Adding** P973 = "https://arsaccordia.com/artists/ART-TIDEMANIS-1897.html"
- **Page exists:** ✅ `artists/ART-TIDEMANIS-1897.html`
- **Wikidata item verified:** https://www.wikidata.org/wiki/Q4457149
- **Birth confirmed:** 1897-10-01 (matches ArtBase)
- **Death confirmed:** 1964-04-12 (matches ArtBase)
- **Risk:** LOW — 20th-century Latvian painter, unambiguous match

---

## Pre-submission verification

- [ ] Q4152126 opened on Wikidata — confirmed Baltic German painter 1831–1877
- [ ] Q1977258 opened on Wikidata — confirmed Latvian painter 1838–1909
- [ ] Q4457149 opened on Wikidata — confirmed Latvian painter 1897–1964
- [ ] All 3 artist HTML pages confirmed live at arsaccordia.com
- [ ] P973 not already present on any of the 3 items (check before submitting)
- [ ] Statement format follows QuickStatements V1 syntax (tab-separated)
- [ ] Logged into QuickStatements as **Arsaccordia**

**Important:** Before submitting, open each Wikidata item and confirm P973 is not already present. If it exists with a different URL, do not overwrite — investigate first.

---

## Submission checklist

- [ ] Logged into QuickStatements as Arsaccordia ← CRITICAL
- [ ] Opened https://quickstatements.toolforge.org/
- [ ] Clicked "New batch" → "Import V1 commands"
- [ ] Opened `phase2_p973_huns_feders_tidemanis_20260615.qs` in text editor
- [ ] Selected all (Cmd+A) and copied
- [ ] Pasted into QuickStatements text area
- [ ] Clicked "Import" — confirmed batch appears
- [ ] Status shows "prepared" (NOT running yet)
- [ ] Previewed all 3 statements — QID, P973, URL, references visible
- [ ] Verified all 3 statements look correct
- [ ] Clicked "Run" or "Start"
- [ ] Stayed on page — watched all 3 complete
- [ ] Noted batch ID: _____________
- [ ] All 3 statements: ✅ green (success)

---

## Post-submission audit

**Batch ID:** _______________  
**Submitted at:** _______________  
**Success count:** ___ / 3  
**Failure count:** ___ / 3  
**Verified by:** _______________  

**Manual spot-checks (required):**
- [ ] Opened Q4152126 (Hūns) — P973 present with S854 and S813 references
- [ ] Opened Q1977258 (Feders) — P973 present
- [ ] Opened Q4457149 (Tīdemanis) — P973 present

**48-hour monitoring:**
- [ ] Day 1: Check https://www.wikidata.org/wiki/User_talk:Arsaccordia for messages
- [ ] Day 1: Check watchlist for reverts
- [ ] Day 2: Final check before marking complete

---

## Context

This batch resolves the "Phase 2" action item listed in `lnmm_phase1_p973_20260614.review.md`:
> Resolve QIDs for Kārlis Hūns, Jūlijs Feders, Jānis Tīdemanis — search Wikidata, update JSON, add P973

QIDs confirmed via Wikidata API 2026-06-15. JSON records updated, artist pages regenerated with QID badges.
