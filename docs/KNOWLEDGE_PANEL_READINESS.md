# Knowledge Panel Readiness — Technical Implementation Guide

*How to position ArsAccordia artworks for Google Knowledge Graph eligibility*

Based on the strategic analysis of June 2026, this document translates the six-step Knowledge Panel framework into specific technical actions for the ArtBase/ArsAccordia catalogue.

---

## Current State Assessment

### ✅ Already Implemented (Strong Foundation)

1. **Canonical entity home pages** — Every Artwork Passport serves as the definitive, comprehensive source for one work
2. **Schema.org `VisualArtwork` JSON-LD** — Embedded in every passport HTML file
3. **`sameAs` linking** — Artist URIs (Wikidata, VIAF, ULAN) included in creator objects
4. **Standards compliance** — Object ID, CDWA, LIDO 1.1 framework operational
5. **Permanent identifiers** — `AP-YYYY-NNNNNN` never reused or reassigned
6. **Stable URLs** — `arsaccordia.com/AP-YYYY-NNNNNN.html`

### ⚠️ Gaps to Close (High-Leverage Improvements)

1. **Wikidata items for artworks** — Currently missing; this is the single highest-priority lever
2. **Artwork-level `sameAs`** — No Wikidata QID in passport JSON-LD `sameAs` array
3. **Structured dimensions** — `size` is text ("77 × 53 cm"), not separate `width`/`height` properties
4. **Image property** — Schema.org `image` URL not included
5. **Machine-readable exports not linked** — LIDO/EODEM XML mentioned but not available as downloadable artifacts
6. **Missing `describedby` links** — Passport should link to its LIDO/EODEM representations

---

## Implementation Roadmap

### Priority 1: Wikidata Artwork Items (Essential)

**Why this matters most:**  
The guidance is explicit: "Wikidata is now the dominant lever… close to mandatory for entity-building… often the tipping point that triggers the panel." A well-referenced Wikidata item with 15–20 properties is usually sufficient for Google's Knowledge Graph to treat an entity seriously.

**What to create:**  
For each artwork (start with the Mona Lisa étalon, then the Siliņš), create a Wikidata item with:

**Core properties (minimum set):**
- `instance of` (P31) → painting (Q3305213)
- `title` (P1476) → "Mona Lisa" @en
- `creator` (P170) → Leonardo da Vinci (Q762)
- `inception` (P571) → 1503 (or date range)
- `collection` (P195) → Musée du Louvre (Q19675)
- `location` (P276) → Musée du Louvre (Q19675)
- `material used` (P186) → oil paint (Q296955), poplar wood (Q26909)
- `depicts` (P180) → Lisa del Giocondo (Q1130)
- `genre` (P136) → portrait (Q134307)
- `height` (P2048) → 77 cm
- `width` (P2049) → 53 cm
- `inventory number` (P217) → "779" (source: Louvre)
- `image` (P18) → commons file
- `described at URL` (P973) → `https://arsaccordia.com/AP-2026-000001.html`

**Each property must be sourced.** For the Mona Lisa, use:
- Louvre collection page
- Grove Art Online
- Any print reference in the bibliographic sources

For the Siliņš, use:
- LNMA collection record (if institutional)
- LNDB authority file
- Art history books cited

**Critical point:** The `described at URL` (P973) creates the bidirectional link:
- Wikidata → Passport (via P973)
- Passport → Wikidata (via `sameAs` in JSON-LD)

This is the reconciliation signal that tells Google "these two sources refer to the same entity."

---

### Priority 2: Enhanced Passport JSON-LD

Extend the existing `<script type="application/ld+json">` block in passport HTML:

**Current structure (AP-2026-000001.html, line 738):**
```json
{
  "@context": "https://schema.org",
  "@id": "https://arsaccordia.com/AP-2026-000001",
  "@type": "VisualArtwork",
  "name": "Mona Lisa",
  "creator": { ... },
  "dateCreated": "1503/1519",
  "artMedium": "Oil on poplar panel",
  "artform": "Painting",
  "owner": { "@type": "Organization", "name": "Musée du Louvre" },
  "size": "77 × 53 cm",
  "description": "Half-length portrait...",
  "url": "https://arsaccordia.com/AP-2026-000001.html"
}
```

**Add these properties:**

1. **Wikidata `sameAs` at artwork level** (once the item exists):
   ```json
   "sameAs": [
     "https://www.wikidata.org/wiki/Q12418",
     "https://collections.louvre.fr/ark:/53355/cl010062370"
   ]
   ```

2. **Structured dimensions** (replace text `size`):
   ```json
   "width": {
     "@type": "QuantitativeValue",
     "value": 53,
     "unitCode": "CMT"
   },
   "height": {
     "@type": "QuantitativeValue",
     "value": 77,
     "unitCode": "CMT"
   }
   ```

3. **Image URL** (once embedded images are extractable or served separately):
   ```json
   "image": "https://arsaccordia.com/images/AP-2026-000001.jpg"
   ```

4. **Links to machine-readable exports** (once generated):
   ```json
   "encoding": [
     {
       "@type": "MediaObject",
       "encodingFormat": "application/xml",
       "contentUrl": "https://arsaccordia.com/api/AP-2026-000001/lido.xml",
       "description": "LIDO 1.1 XML export"
     },
     {
       "@type": "MediaObject",
       "encodingFormat": "application/xml",
       "contentUrl": "https://arsaccordia.com/api/AP-2026-000001/eodem.xml",
       "description": "EODEM XML export"
     }
   ]
   ```

---

### Priority 3: Generate and Link LIDO/EODEM Exports

**Current state:**  
The about page (line 252) claims "Export formats — LIDO 1.1 and EODEM XML for museum exchange" and the passport HTML embeds *display* versions of LIDO/EODEM (lines 1133–1300 of AP-2026-000001.html), but there are no downloadable `.xml` files.

**What to do:**
1. Generate actual LIDO and EODEM XML files for each passport:
   - `/api/AP-2026-000001/lido.xml`
   - `/api/AP-2026-000001/eodem.xml`

2. Add download links in the passport "Machine-Readable Formats" section

3. Include `encoding` property in JSON-LD (see above)

4. This creates a "described by" relationship that aggregators and archives can follow

---

### Priority 4: Artwork-Level Authority Cross-References

**Museum collection pages:**  
If an artwork is in a museum catalogue, include that URL in `sameAs`:
```json
"sameAs": [
  "https://www.wikidata.org/wiki/Q12418",
  "https://collections.louvre.fr/ark:/53355/cl010062370"
]
```

**Getty vocabularies:**  
For object type and materials, link to AAT:
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

---

### Priority 5: Confirmed-Only `sameAs` Validation

**Critical rule from the credibility guide (line 91):**  
> "Candidate-status authority URIs must **not** appear in the machine-readable `sameAs` array, because `sameAs` is an unqualified identity assertion."

**Implementation:**
- Only green-badge (✓ Confirmed) authority links go in JSON-LD `sameAs`
- Amber/candidate (⚠) links appear in HTML display only, never in structured data
- This prevents unverified claims from propagating to search engines

**Audit step:**  
Check every passport's JSON-LD and confirm:
```bash
grep -A 20 '"sameAs"' AP-*.html | grep '⚠'  # should return nothing
```

---

## What This Achieves

### For famous works (Mona Lisa):
- **Enriches existing Knowledge Graph data** — Google likely already has a panel; your sourced Wikidata contributions improve its accuracy
- **Establishes ArsAccordia as an authoritative source** — the `described at URL` link positions the passport as a citable reference
- **Demonstrates full capability** — proves the standard works

### For private/undocumented works (Siliņš, future holdings):
- **Creates eligibility** — the work becomes *visible* to the Knowledge Graph
- **Pre-positions the canonical record** — when the work gains notability over time (exhibitions, sales, publications), the passport is already the authoritative reference Google can surface
- **Builds the supply side** — you're creating the entity infrastructure that doesn't otherwise exist

**Honest expectation:**  
Long-tail works won't get panels immediately — there's no timeline, no guarantee. But you're doing the only work that makes it *possible*, and you're becoming the definitive source when those works do get discovered.

---

## Validation Checklist

Before claiming "Knowledge Panel ready," verify each passport has:

- [ ] Wikidata item with 15+ sourced properties
- [ ] `described at URL` (P973) on Wikidata pointing to passport
- [ ] Passport JSON-LD includes Wikidata QID in `sameAs`
- [ ] Structured `width` and `height` (not just text `size`)
- [ ] `image` property with accessible URL
- [ ] Downloadable LIDO and EODEM XML files
- [ ] `encoding` property in JSON-LD linking to XML exports
- [ ] Only confirmed (✓) authorities in `sameAs`
- [ ] Creator `sameAs` includes Wikidata, VIAF, ULAN
- [ ] All URIs resolve (no 404s)

---

## Timeline and Effort Estimate

| Task | Effort | Notes |
|---|---|---|
| Create Wikidata item for Mona Lisa | 2–3 hours | Straightforward — sources readily available |
| Create Wikidata item for Siliņš | 3–4 hours | Requires LNMA/LNDB research for sourcing |
| Update passport JSON-LD template | 2 hours | One-time template change, applies to all |
| Generate LIDO/EODEM XML files | 4–6 hours | Build the export script (likely Python) |
| Add download links to passports | 1 hour | Template update |
| Audit `sameAs` for candidate leakage | 30 min | Run the grep check, manual review |
| Validate all URIs resolve | 30 min | Automated link checker |

**Total for the two exemplar passports:** ~15–20 hours  
**Leverage:** These two become the template for all future passports

---

## Long-Term Maintenance

Once the framework is in place:

1. **Every new passport follows the same template** — Wikidata item creation, JSON-LD with full property set, LIDO/EODEM generation
2. **Wikidata contributions remain externally sourced** — never cite ArsAccordia itself; preserve the neutral-contributor identity
3. **Periodic re-validation** — Run link checks quarterly, update Wikidata items when new authoritative sources become available
4. **Monitor for panel formation** — Search for `[artwork name] site:google.com` to see if a Knowledge Panel appears; document when it happens

---

## References

- Original strategic analysis (shared June 14, 2026)
- `arsaccordia-credibility-guide.md` (Issue 4b — `sameAs` candidate exclusion)
- `ars-accordia-strategic-brief.md` (API-first architecture, permanent IDs)
- Schema.org VisualArtwork: https://schema.org/VisualArtwork
- Wikidata property list for artworks: https://www.wikidata.org/wiki/Template:Painting
- Google's structured data guidelines: https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data

---

## Questions for Clarification

Before implementing, confirm:

1. **Wikidata account strategy** — Will artwork items be created under the `Arsaccordia` account, or a separate contributor identity?
2. **Image hosting** — Where will passport images be served from for the `image` property? (Currently base64-embedded in HTML, which search engines can't easily use)
3. **XML generation priority** — Should LIDO/EODEM generation be automated in the export pipeline, or hand-crafted for the two exemplars first?
4. **Private works and Wikidata notability** — For undocumented private works, how do we navigate Wikidata's notability guidelines? (May need to wait until the work has a published catalogue entry — i.e., the passport itself becomes the notability evidence)

