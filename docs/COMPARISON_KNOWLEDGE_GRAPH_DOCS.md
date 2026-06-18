# Comparison: Two Knowledge Graph Improvement Documents

*Written 2026-06-14 after receiving both analyses*

---

## Summary

Both documents identify the same **core truth**: ArsAccordia has built the eligibility stack, and the highest-leverage improvement is **Wikidata artwork items with `described at URL` (P973)** pointing to passports.

They diverge on **scope and what was actually checked**:

- **KNOWLEDGE_GRAPH_IMPROVEMENTS.md** (Claude's analysis) checked the codebase templates and found structural gaps across 288 artist pages
- **KNOWLEDGE_PANEL_READINESS.md** (Copilot's analysis) focused on passport-level improvements and strategic questions

**Neither document alone is complete.** The merge is:
1. Claude's **Tier 1** (artist template + org schema) — site-wide structural fixes
2. Copilot's **Priority 2** (richer passport JSON-LD with AAT URIs + encoding property) — per-passport depth
3. Both agree on **Wikidata artwork items** (Priority 1 / Tier 1 item 1)

---

## What Claude Found That Copilot Missed

### 1. Artist profile pages have no JSON-LD at all
**File:** `templates/artist_profile.html.j2`  
**Impact:** 288 pages, zero structured data  
**Fix:** One template change

Claude verified this with:
```bash
grep -n "application/ld+json\|schema.org" templates/artist_profile.html.j2
# Returns nothing — no JSON-LD block exists
```

**Why it matters:** The artist entity is half of every artwork's graph relationship. Without `Person` JSON-LD on artist pages, Google cannot:
- Reconcile the artist name on the passport with the artist record on the same site
- Follow `creator` → artist page navigation
- Build a corroborated artist entity from ArsAccordia's own structured data

**Copilot missed this because:** I didn't check the artist template — I focused on the two passport HTML files that already exist.

---

### 2. "ArtBase" vs "Ars Accordia" branding inconsistency
**File:** `templates/artist_profile.html.j2`, lines 6–7

Current:
```html
<meta name="description" content="Artist Profile — {{ artist.identity.preferred_name }}. ArtBase scholarly catalogue record.">
<title>{{ artist.identity.preferred_name }} — ArtBase</title>
```

Should be:
```html
<meta name="description" content="Artist record — {{ artist.identity.preferred_name }}. Ars Accordia scholarly catalogue with authority links to Wikidata, Getty ULAN, and VIAF.">
<title>{{ artist.identity.preferred_name }} — Ars Accordia</title>
```

**Why it matters for Knowledge Graph:**  
The Knowledge Graph builds entity confidence through **co-occurrence consistency**. If some pages say "ArtBase" and others say "Ars Accordia," Google's entity resolver has to decide whether these are the same organisation or different ones. Inconsistent naming dilutes the signal.

**Copilot missed this because:** I only viewed the generated HTML files (which are in `/passports/`), not the Jinja2 templates.

---

### 3. No canonical link tags on artist pages
**Implicit in Claude's doc:** The artist template lacks `<link rel="canonical">` tags.

**Why it matters:** Canonical tags tell Google which URL is the authoritative version when multiple URLs might show similar content. Without it, Google might split signals across variant URLs (with/without trailing slash, http vs https, www vs non-www).

**Copilot missed this because:** I didn't check the artist template at all.

---

### 4. Homepage/about page missing `Organization` JSON-LD
**Files:** `index.html` (has `WebSite` only, line 351–358), `about/index.html` (no JSON-LD at all)

Claude's recommended block:
```json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "@id": "https://arsaccordia.com",
  "name": "Ars Accordia",
  "url": "https://arsaccordia.com",
  "description": "Scholarly art cataloguing service issuing Artwork Passports for European private and corporate collections to international museum standards.",
  "email": "catalogue@arsaccordia.com",
  "foundingDate": "2026",
  "knowsAbout": [
    "https://www.wikidata.org/wiki/Q18969458",
    "https://www.wikidata.org/wiki/Q11798"
  ],
  "sameAs": []
}
```

**Why it matters:** Before Google can treat ArsAccordia's records as authoritative, it needs to understand what the organisation *is*. The `Organization` type provides that entity definition. The `knowsAbout` links (Q18969458 = art cataloguing, Q11798 = cultural heritage) help Google contextualise the domain.

**I mentioned this** in my doc (section "Priority 5"), but Claude provided the **actual JSON-LD block** and put it at higher priority (Tier 2).

---

### 5. Internal `sameAs` cross-links from passports → artist pages
**Current gap:** Passport JSON-LD `creator` object includes external `sameAs` (Wikidata, VIAF) but not the internal artist page URL.

Claude's fix:
```json
"creator": {
  "@type": "Person",
  "name": "Herberts Siliņš",
  "sameAs": [
    "https://www.wikidata.org/wiki/Q23054868",
    "https://viaf.org/viaf/15148752166141201333",
    "https://arsaccordia.com/artists/ART-SILINS-1926"  ← internal link
  ]
}
```

**Why it matters:** This creates a navigable graph *within the site*:
- Passport → artist page (via `creator.sameAs`)
- Artist page → passport (via eventual `subjectOf` on the artist's `Person` block)

Google can follow these links to understand the site's entity structure.

**I mentioned this** but didn't provide the specific implementation.

---

## What Copilot Found That Claude Missed or Underweighted

### 1. Getty AAT URIs in JSON-LD for materials and object types
**Why it matters:** Linking to controlled vocabularies (Getty AAT) gives stronger entity-anchoring signals than plain text strings.

**My recommendation:**
```json
"additionalType": "http://vocab.getty.edu/aat/300033618",
"material": [
  {
    "@type": "Thing",
    "name": "oil paint",
    "url": "http://vocab.getty.edu/aat/300015050"
  },
  {
    "@type": "Thing",
    "name": "poplar wood",
    "url": "http://vocab.getty.edu/aat/300012363"
  }
]
```

**Claude's doc doesn't mention this.** It's not essential, but it's a precision improvement that aligns with the strategic brief's emphasis on authority reconciliation.

---

### 2. `encoding` property for linking JSON-LD → LIDO/EODEM XML
**Why it matters:** The about page promises LIDO/EODEM exports, but they're not available as separate files. If/when they are generated, the JSON-LD should link to them.

**My recommendation:**
```json
"encoding": [
  {
    "@type": "MediaObject",
    "encodingFormat": "application/xml",
    "contentUrl": "https://arsaccordia.com/api/AP-2026-000001/lido.xml",
    "description": "LIDO 1.1 XML export"
  }
]
```

**Claude mentions the LIDO gap** in passing ("orthogonal to Knowledge Graph eligibility") but doesn't provide the schema.org property to fix it.

**Honest assessment:** This is lower priority than the structural fixes Claude identified. LIDO/EODEM is for museum exchange, not Google's crawler. But it's a credibility issue — the about page claims these exist.

---

### 3. Confirmed-only `sameAs` grep audit
**My recommendation:**
```bash
grep -A 20 '"sameAs"' AP-*.html | grep '⚠'  # should return nothing
```

**Why it matters:** The credibility guide (Issue 4b) explicitly states that candidate-status (⚠) authority URIs must **not** appear in `sameAs` because it's an unqualified identity assertion.

**Claude's doc doesn't provide a validation step.** This is a practical check to ensure the confirmed-only rule is enforced.

---

### 4. Effort estimates and strategic questions
**My doc includes:**
- Hour estimates per task (~15–20 hours total for two exemplars)
- Strategic questions at the end:
  - Wikidata account strategy (use `Arsaccordia` account or separate contributor identity?)
  - Image hosting (where will passport images be served from for the `image` property?)
  - LIDO/EODEM generation priority (automated pipeline or hand-crafted for exemplars first?)
  - Private works and Wikidata notability (how to navigate notability guidelines?)

**Claude's doc doesn't include these.** The questions are real decisions that need answering before implementation.

---

## One Factual Issue in Copilot's Doc

**Priority 1 says "create a Wikidata item for the Mona Lisa"** — but Q12418 already exists and is extremely rich.

What you actually do is **add P973 (described at URL)** pointing to the passport on the existing item. Creating a new item would be wrong.

**Correction:** For the Mona Lisa, the Wikidata work is:
1. Add P973 to Q12418 (if not already present)
2. Possibly add the passport as a reference to existing statements (S854)

For the Siliņš, **create a new item** because it likely doesn't exist yet.

**Claude's doc is correct on this** — it says "create a new Wikidata item for *Juras noskana (Sea Mood)*" (the Siliņš), not the Mona Lisa.

---

## Recommended Merge

**Tier 1 — Highest leverage (do these first):**

1. **Fix artist profile template** (Claude: Tier 1 item 2 + item 8)
   - Add `Person` JSON-LD
   - Fix "ArtBase" → "Ars Accordia" branding
   - Add canonical link tags
   - **Impact:** One template change, immediate effect across 288 artist pages

2. **Add `Organization` JSON-LD to homepage and about page** (Claude: Tier 2 item 4)
   - Defines what ArsAccordia *is* as an entity
   - **Impact:** Two files, establishes organisational authority

3. **Create Wikidata artwork item for Siliņš painting** (Both docs: Priority 1)
   - 15–20 sourced properties
   - P973 `described at URL` → passport
   - **Impact:** Makes the work Knowledge Graph-eligible

4. **Add Wikidata P973 to Mona Lisa Q12418** (Copilot: Priority 1, corrected)
   - Links existing rich item to the passport
   - **Impact:** Establishes ArsAccordia as authoritative source

---

**Tier 2 — High leverage:**

5. **Enrich passport JSON-LD** (Both docs, merged):
   - Artwork-level `sameAs` with Wikidata QID (both)
   - Structured `width`/`height` as `QuantitativeValue` (both)
   - `image` property (both)
   - `mainEntityOfPage` (Claude: Tier 4 item 9)
   - Getty AAT URIs for `additionalType` and `material` (Copilot)
   - `encoding` property linking to LIDO/EODEM (Copilot)
   - Internal `sameAs` from passport `creator` → artist page (Claude: Tier 2 item 5)
   - **Impact:** One template/generator change, makes passports Knowledge Graph-dense

---

**Tier 3 — Good hygiene:**

6. **Open Graph and Twitter Card tags** (Claude: Tier 3 item 6)
7. **Sitemap `<image:image>` blocks** (Claude: Tier 3 item 7)
8. **Generate actual LIDO/EODEM XML files** (Copilot: Priority 3)
9. **Validated confirmed-only `sameAs` audit** (Copilot: Priority 5)

---

## Which Document to Keep?

**Keep both.** They're complementary:

- **KNOWLEDGE_GRAPH_IMPROVEMENTS.md** (Claude) — codebase-specific structural gaps, implementation order, exact file references
- **KNOWLEDGE_PANEL_READINESS.md** (Copilot) — strategic context from the June 2026 analysis, effort estimates, strategic questions, Getty AAT + encoding property specifics

**Or create this comparison doc and archive both originals.** This comparison contains the merged roadmap.

---

## Implementation Checklist (Merged from Both Docs)

Before claiming "Knowledge Panel ready," verify:

- [ ] Artist profile template has `Person` JSON-LD with `sameAs` to Wikidata, VIAF, ULAN, RKD
- [ ] Artist profile template says "Ars Accordia" not "ArtBase" (title, meta description)
- [ ] Artist profile template has canonical link tags
- [ ] Homepage and about page have `Organization` JSON-LD for Ars Accordia
- [ ] Wikidata item exists for Siliņš artwork with 15+ sourced properties
- [ ] Wikidata P973 added to Mona Lisa Q12418 pointing to passport
- [ ] Passport JSON-LD includes:
  - [ ] Artwork-level `sameAs` with Wikidata QID
  - [ ] Structured `width` and `height` (not just text `size`)
  - [ ] `image` property with accessible URL
  - [ ] `mainEntityOfPage` declaring the passport as entity home
  - [ ] Getty AAT URIs for `additionalType` and `material`
  - [ ] `encoding` property linking to LIDO/EODEM XML (once generated)
  - [ ] Internal `sameAs` from `creator` → artist page URL
- [ ] Only confirmed (✓) authorities in `sameAs` (no ⚠ candidate links)
- [ ] All URIs resolve (no 404s)
- [ ] Open Graph tags on all page types
- [ ] Sitemap includes `<image:image>` blocks for passports
- [ ] Downloadable LIDO and EODEM XML files exist (or about page reworded)

---

## Final Recommendation

Start with **Tier 1** (artist template + org schema + Wikidata items). These are:
- High leverage
- One-time template changes that affect the entire site
- The foundation for all other improvements

Then **Tier 2** (enrich passport JSON-LD) to add depth.

The strategic questions from Copilot's doc need answering during Tier 1 implementation:
- Use `Arsaccordia` Wikidata account or separate contributor identity? (Affects sourcing credibility)
- Where will images be hosted for the `image` property? (Affects JSON-LD implementation)
- Automated LIDO/EODEM pipeline or hand-craft for exemplars? (Affects Tier 3 timeline)

---

**Estimated total effort for Tier 1 + Tier 2:** 20–25 hours  
**Result:** Two exemplar passports (Mona Lisa + Siliņš) fully Knowledge Graph-ready, plus 288 artist pages with proper structured data
