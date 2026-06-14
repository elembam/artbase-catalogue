# TEST BATCH — LNMM Established Artists
## 2026-06-02

**Phase:** 1 (external identifiers only)  
**Statements proposed:** 5  
**Distinct artists:** 5  
**Properties:** P214 (VIAF) × 5  
**Purpose:** First authorized test upload with established Latvian artists

---

## Per-statement review

### Q130623 Aleksandrs Apsītis
- **Artist:** Latvian painter (1880-1944), National Artist of Latvia
- **Adding** P214 = "70659503"
- **Source:** https://viaf.org/viaf/70659503/
- **Verify:** Major figure - Wikipedia article exists
- **Risk:** LOW — well-established artist, verified VIAF

### Q11300069 Augusts Annuss
- **Artist:** Latvian painter and graphic artist (1893-1982)
- **Adding** P214 = "25737434"
- **Source:** https://viaf.org/viaf/25737434/
- **Verify:** Notable artist in Latvian art history
- **Risk:** LOW — verified external identifier

### Q134417560 Edvīns Andersons
- **Artist:** Latvian artist (1929-)
- **Adding** P214 = "305088425"
- **Source:** https://viaf.org/viaf/305088425/
- **Verify:** Contemporary Latvian artist
- **Risk:** LOW — verified external identifier

### Q99483053 Jānis Anmanis
- **Artist:** Latvian artist (1943-)
- **Adding** P214 = "203230880"
- **Source:** https://viaf.org/viaf/203230880/
- **Verify:** Contemporary Latvian artist
- **Risk:** LOW — verified external identifier

### Q97930178 Jēkabs Apinis
- **Artist:** Latvian painter (1899-1942)
- **Adding** P214 = "305098120"
- **Source:** https://viaf.org/viaf/305098120/
- **Verify:** Mid-20th century Latvian artist
- **Risk:** LOW — verified external identifier

---

## Pre-submission verification

✅ All 5 artists have existing Wikidata items  
✅ All VIAF IDs verified at viaf.org  
✅ Statement format follows QuickStatements V1 syntax  
✅ References include: S854 (reference URL), S813 (retrieved date), S248 (stated in: VIAF Q54919)  
✅ Retrieved date updated to 2026-06-02  
✅ Mix of historical and contemporary artists for balanced test  

---

## Submission checklist (from quickstatements_runbook.md)

- [ ] **Logged into QuickStatements as Arsaccordia** ← CRITICAL
- [ ] Opened https://quickstatements.toolforge.org/
- [ ] Clicked "New batch" → "Import V1 commands"
- [ ] Opened `test_rozentals_batch_20260602.qs` in text editor
- [ ] Selected all (Cmd+A) and copied
- [ ] Pasted into QuickStatements text area
- [ ] Clicked "Import" — confirmed batch appears
- [ ] Status shows "prepared" (NOT running yet)
- [ ] Previewed all 5 statements in human-readable form
- [ ] Read first 3 statements carefully (QID, property, value, references)
- [ ] Read last statement (catches truncation issues)
- [ ] Picked 1 random VIAF URL and opened in new tab to verify
- [ ] Cross-checked artist names match Wikidata labels
- [ ] Clicked "Run" or "Start"
- [ ] **STAYED ON PAGE** — did not navigate away
- [ ] Watched progress counter increment
- [ ] Noted batch ID: _____________
- [ ] All statements: ✅ green (success) / ❌ red (failure)
- [ ] If any RED: screenshot error, stop, investigate, DO NOT retry

---

## Post-submission audit

**Batch ID:** _______________  
**Submitted at:** _______________  
**Success count:** ___ / 5  
**Failure count:** ___ / 5  
**Verified by:** _______________

**Manual spot-checks (required):**
- [ ] Visited Q130623 (Apsītis) — confirmed VIAF 70659503 present with references (S854, S813, S248)
- [ ] Visited Q11300069 (Annuss) — confirmed VIAF 25737434 present with references
- [ ] Checked references section — all 3 reference properties present

**48-hour monitoring (CRITICAL):**
- [ ] Day 1: Check https://www.wikidata.org/wiki/User_talk:Arsaccordia for messages
- [ ] Day 1: Check watchlist for any reverts
- [ ] Day 2: Check User_talk:Arsaccordia again
- [ ] Day 2: Check watchlist again
- [ ] Day 3: Final check before marking complete

**Response to reverts:**
- If 1 revert: Read edit summary, respond politely, adjust methodology
- If 2-5 reverts: Post explanation on User_talk:Arsaccordia, wait for feedback
- If >5 reverts: STOP immediately, post on Wikidata:Project_chat

---

## Next steps (if successful)

✅ **After 48 hours with no issues:**
1. Mark this batch as verified ✓
2. Prepare next batch: 10 statements (double the size)
3. Continue with remaining artists from queue_20260528_105208
4. Gradually increase batch size: 5 → 10 → 20 → 50

---

## Notes

**Why these artists?**
- Aleksandrs Apsītis: Major historical figure, National Artist designation
- Augusts Annuss: Well-documented in Latvian art history
- Mix of birth years (1880s-1940s) shows range
- All part of LNMM collections (Latvian National Museum of Art)
- Low controversy risk — adding external IDs to established figures

**Safety features:**
- Only P214 (VIAF) — most trusted external identifier property
- Only artists with existing Wikidata items (no new item creation)
- All VIAF IDs independently verifiable at viaf.org
- Proper references on every statement
- Conservative batch size (5) for first test

**This is a test of the PROCESS, not the data quality.**
The goal is to verify QuickStatements authorization works and to establish baseline trust.
