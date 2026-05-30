# Ars Accordia — Strategic Context for Development

*A short brief so development decisions align with what this project actually is. Read this before reasoning about architecture or features.*

---

## What we are building (one line)

A **reference-data utility for art** — *the DOI / cbonds / Bloomberg/refinitiv for artworks*. Every work gets a permanent identifier (`AP-YYYY-NNNNNN`) and a canonical reference passport, built **programmatically** by reconciling the authoritative registries (Wikidata, Getty ULAN/AAT/TGN, VIAF, LNDB, LIBRIS, ICONCLASS) into one standards-compliant record.

The intro line holds: *"An art cataloguing service for European art collections — bringing each work to international museum standards. Each work receives an Artwork Passport: a standards-based, authoritative identity document for cultural heritage."*

## What it is NOT

- **Not** collection-management software (inventory/CRM/sales).
- **Not** a marketplace.
- **Not** a competitor to Artwork Archive, Artlogic, Collector Systems, etc. Those are *potential API customers* — they lack an authority-reconciliation/standards layer and could embed ours. We are infrastructure they cite, not an app we fight them on.

## The category and its proven analogs

We are a **utility**, not a feature-competing product. Templates to keep in mind:

- **cbonds / Bloomberg / Refinitiv** — reference data for financial instruments, keyed on a permanent ID (ISIN).
- **DOI / Crossref** — permanent IDs + reconciled metadata for scholarly works. *Closest analog.*
- **LEI / GLEIF, ISNI / ORCID** — permanent identity for entities and people.

Each succeeds by being trusted, neutral infrastructure. The data integrity *is* the asset.

## What this means for how we build

- **API-first / programmatic.** The enrichment engine is the core product; the human-readable web passports are its face (cbonds has both). Architect so the reconciliation + passport generation can be called programmatically, not just run as a site build.
- **Permanent identifiers**, never reused or reassigned (`AP-YYYY-NNNNNN`, `ART-NAME-YYYY`). Stable URLs.
- **Standards-compliant outputs** — Object ID, CDWA, LIDO 1.1 / EODEM, Schema.org JSON-LD. (Already in scope.)
- **The reconciliation ("accordia") engine** — pulling scattered authority data and condensing it into one clean passport — is the moat. Treat it as the central asset.
- **Confirmed vs Candidate trust model is preserved everywhere**, including machine-readable output: candidate links must never be asserted as authoritative (e.g. excluded from JSON-LD `sameAs`).
- **Clean separation of layers**: public registry (open) · private client workspace · premium/verification services.

## Revenue shape (so technical priorities align)

- **API access + data feeds** (B2B licensing) — primary.
- **Per-passport issuance + human verification** services.
- **Private client workspaces** — a client's view of the passports they hold/track.

Customers: insurers, art lenders/art-finance, auction houses, museums, estates, and management platforms (embed). Adoption tailwind: tightening art-market provenance / AML requirements + insurer documentation demands.

## Future development pathways

1. **Enrichment API** — *"feed a thin record (or an identifier) → get a museum-standard passport back."* The programmatic version of what the pipeline does today.
2. **The Ars Accordia Terminal** — a Bloomberg/Refinitiv-style professional reference terminal for art:
   - Instant lookup of any artwork or artist → canonical passport + all reference data
   - Screening / filtering across the registry (artist, period, medium, collection, authority-completeness)
   - Watchlists of tracked works and artists
   - Side-by-side comparison of works
   - **Completeness scoring** of each passport against the museum-grade standard (the Mona Lisa étalon as the 100% reference)
   - Linked-entity navigation (creator → other works; collection → other holdings)
   - Data export and feed access
   - Dense, fast, keyboard-driven UI — built for professional power users, not casual browsing
3. **Data feeds / bulk endpoints** for institutional clients.
4. **Private client workspaces** with étalon completeness scoring and gap analysis (the gaps surfaced here drive the verification/research upsell).
5. **Embed / SDK** so management platforms can call our enrichment as a service.

## Guardrails

- Stay **neutral, trusted infrastructure** — never let commercial interest override data integrity.
- Keep the **commercial service and the non-commercial Wikidata-citizen identity coherent**: every Wikidata contribution is sourced to external authorities, never to Ars Accordia itself. This stays absolute.
- Keep public claims true in the artifacts (see the separate credibility guide): the étalon is the one record that must always be complete; other records may be in progress with that status disclosed.
