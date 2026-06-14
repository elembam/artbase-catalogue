# Ars Accordia — Business Roadmap

*Last updated: 2026-06-14*

---

## The two questions that drive sequencing

Every priority below answers one of two questions:

1. **Is the value proposition proven?** — Does a prospect who reaches the site encounter a complete, flawless, museum-grade record that proves the service does what it claims?
2. **Can someone buy it?** — Is there a clear, packaged offer, a contact point, and a path to an engagement?

Until both questions are yes, discoverability improvements (SEO, Knowledge Graph, sitemap) have diminishing returns — they bring people to something that isn't yet ready to convert. Build the proof first, package the offer second, then scale discovery.

---

## Priority 1 — Produce 3–5 exemplary passports

**Why this is first:** The passport is your product. The primary sales tool for any prospect is being able to say "look at this" and send a link. A single perfect passport is worth more than a hundred thin ones.

**What "exemplary" means:**
- All nine Object ID fields complete
- Provenance documented with sources
- Condition note present
- Image (even a low-resolution placeholder)
- At least one confirmed Wikidata authority link (artist, ideally artwork)
- Validation badges showing green in the record
- Working links to all authority records (ULAN, VIAF, Wikidata)

**Immediate actions:**
1. Regenerate AP-2026-000001 (Mona Lisa) with the new generator — it still uses the pre-built HTML
2. Create a Wikidata item for AP-2026-000002 (*Juras noskana*) and add the confirmed QID to the JSON, then regenerate
3. Identify 3 additional works from the Hansabanka collection (see Priority 2) and catalogue them end-to-end as the exemplary set

---

## Priority 2 — Catalogue 3–5 Hansabanka works as corporate-collection proof

**Why this matters:** The Hansabanka book is a published, sourced corporate art collection catalogue — exactly the client segment Ars Accordia targets. Cataloguing works from it turns the abstract pitch ("we do this for corporate collections") into a clickable demonstration.

**What to produce:**
- 3–5 passports for Hansabanka works, catalogued from the book as source
- Source document recorded in the passport provenance/bibliography field
- A short catalogue note in the about page or catalogue page making this context visible: *"The Hansabanka Collection passports demonstrate the service applied to a documented corporate art holding."*

**Why it compounds:** A prospect from the Baltic corporate sector can see their exact collection type already catalogued. It's not abstract.

---

## Priority 3 — The offering package and landing page ✓ (this session)

**Done:** Offering package (`docs/OFFERING_PACKAGE.md`) and redesigned landing page (`index.html`) completed in session 2026-06-14. The landing page now:
- States the value proposition in the first screen
- Explains what the Artwork Passport is and what it contains
- Identifies the three client types
- Explains the four-step process
- Shows sample passports as proof
- Has a clear contact CTA

**Still needed:**
- Pricing review — confirm the indicative figures in OFFERING_PACKAGE.md
- About page update — add a "Catalogue your collection" section that mirrors the offering

---

## Priority 4 — Land the first pilot engagement

**Why this is non-negotiable:** The workflow is not proven until it has survived a real client. One end-to-end engagement gives you:
- Proof the process works on unfamiliar data
- A case study (even if confidential in detail)
- A third-party reference
- The start of the credibility flywheel

**Target profile for the first engagement:**
- Corporate collection, 10–50 works
- Collection already partly documented (easier to complete than to start cold)
- Client who values standards compliance (insurance, board reporting, loan eligibility)
- Baltic, Nordic, or Central European — where the Hansabanka proof applies geographically

**What to offer for the first engagement:**
- Preferential rate or deferred fee in exchange for: a testimonial, a case study right to mention the project (anonymously or named), and permission to reference the catalogue publicly
- Scope: a complete pilot of 10 works, full exemplary passports, delivered in 4–6 weeks

---

## Priority 5 — Build a visible Wikidata contribution cadence

**Why this matters for business:** When a prospect asks "have you done this before?" the Wikidata contribution history is independently verifiable, third-party evidence that the answer is yes. It's cheap to do and compounds over time.

**What to build:**
- Contribute sourced artist data from the Hansabanka book (birth/death dates, nationalities, occupations, authority IDs) — these are facts already in the catalogue
- Add `P973 (described at URL)` to existing Wikidata items for artists already in the catalogue with confirmed QIDs, pointing at their Ars Accordia artist pages
- Create the `artbase_export/data/contributions/` directory as the formal record of batches (already started)
- Publish a `/contributions` page on the site showing recent Wikidata batch activity

---

## Where the SEO/technical items land

The SEO infrastructure from session 2026-06-14 (JSON-LD, structured data, sitemap, Search Console) was the right groundwork — but it delivers value in proportion to what it makes discoverable.

| Technical item | Business value | When to prioritise |
|---|---|---|
| AP-2 Wikidata item | High — completes exemplary passport (Priority 1) | Now |
| Regenerate Mona Lisa | High — same reason | Now |
| Biography text in artist records | Medium — makes pages substantive for ranking | After Priority 2 |
| Getty AAT URIs | Low business priority now | After first pilot |
| Page size fix (AP-000001) | Medium — Core Web Vitals | After Priority 2 |
| EODEM export pipeline | Low until there is loan activity | Post-pilot |
| OAI-PMH feed | Low until there is an aggregator relationship | Post-pilot |

---

## Q3 2026 milestone targets

| By | Target |
|---|---|
| End June 2026 | 5 exemplary passports live; Hansabanka set started |
| End July 2026 | Offering package communicated to 3 warm contacts; first pilot proposal sent |
| End August 2026 | First pilot engagement under contract or in progress |
| End September 2026 | First pilot delivered; case study drafted; 20+ Wikidata contributions logged |

---

## Reference documents

- `docs/OFFERING_PACKAGE.md` — service description and pricing
- `docs/KNOWLEDGE_GRAPH_IMPROVEMENTS.md` — structured data implementation guide
- `docs/ARTBASE_WIKIDATA_PROFILE.md` — Wikidata contribution workflow
- `docs/HOUSE_STYLE_MANUAL.md` — cataloguing standards
