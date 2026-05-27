# ArtBase — Architecture Decisions

*The technical commitments that need to be made now to preserve the platform option later.*

Version 0.1

---

## Why this document exists

Most decisions in a young business can be deferred or reversed. A few cannot. Domain names get squatted. URL schemes that ship publicly are hard to change without breaking references. Identifier schemes that get cited externally become permanent obligations. This document records the decisions that cost almost nothing now but are expensive or impossible to undo later.

Every decision below has three parts: **the commitment**, **the reasoning**, and **what would have to be true to change it**. We change them only when those conditions are met.

---

## 1. Canonical domain

### Commitment

The canonical domain for ArtBase is **`artbase.eu`** — to be registered and held in perpetuity. All passport URLs, all internal documentation, all client deliverables reference this domain as the long-term home.

Supporting domains to also register and redirect to the canonical:

- `artbase.art` — the cultural-heritage TLD, increasingly recognised
- `getartbase.com` — defensive registration
- Country-specific (`artbase.se`, etc.) — defensive, redirect to canonical

### Reasoning

- The `.eu` extension positions the platform regionally without being country-specific
- `artbase.com` is owned and merged with Artlogic; not available
- A platform domain that we don't control is a single point of catastrophic failure ten years out
- Multiple supporting domains prevent typo-squatting and protect the brand

### Conditions for change

- Only if `artbase.eu` becomes unavailable through events outside our control
- Migration would require a full URL rewrite plan with permanent redirects for at least 10 years

---

## 2. URL structure

### Commitment

Passport URLs follow this scheme, permanently:

```
https://artbase.eu/p/{passport_id}
```

Supporting URL patterns:

```
https://artbase.eu/a/{artist_id}        — artist record
https://artbase.eu/c/{collection_id}    — collection page
https://artbase.eu/about                 — institutional pages
https://artbase.eu/api/p/{passport_id}  — machine-readable API
https://artbase.eu/api/p/{passport_id}/eodem  — EODEM XML
```

URLs are:

- **Opaque** — no titles, no dates, no human-readable content in the path
- **Stable** — once published, served forever (or returned as `301 Moved Permanently` to a new canonical location)
- **Version-aware** — `?v=2` appends a specific version; default URL serves latest
- **Format-negotiable** — `Accept: application/xml` on the same URL returns EODEM; `Accept: text/html` returns the passport

### Reasoning

- Encoding mutable data (titles, dates) in URLs creates broken-link debt every time something changes
- Opaque IDs match how Wikidata (Q-numbers) and Getty (numeric IDs) work — the only proven model for long-term reference systems
- Content negotiation on the same URL means a citation can resolve to the right format for any consumer

### Conditions for change

- Only with a full URL-migration plan including permanent 301 redirects from every old URL pattern
- New URL schemes can be added; old ones cannot be deprecated for at least 10 years after their last use

---

## 3. Identifier scheme

### Commitment

Passport IDs are generated as **prefixed base32-encoded short hashes**:

- Format: `AB` (ArtBase prefix) + 8 base32 characters (Crockford alphabet, no ambiguous characters)
- Example: `AB7F3KQ2X1`
- Generation: hash of the canonical record content at first publication, truncated to 8 chars, collision-checked
- Each artwork has one passport ID, permanent for the artwork's lifetime in the system

Artist IDs follow the same scheme with `AR` prefix: `AR9D2HK4Q8`.
Collection IDs with `CO`: `CO3B7XJ5N1`.

### Reasoning

- Short enough to print on a label, write in an email, read aloud over the phone
- Opaque — reveals no information about issuance date, sequence, or content
- Base32 Crockford alphabet avoids `I/L/O/U/0/1` ambiguity in print and speech
- Hash-derived means the same artwork can theoretically be re-generated to the same ID even if records are rebuilt
- Prefix makes ID type immediately recognisable

### Conditions for change

- Existing IDs are never reused, never reassigned, never changed
- A new ID scheme could be introduced in parallel; old IDs continue to resolve forever
- The current `AP-2026-000001` format used in mockups would migrate to the new scheme before any real-client deployment

### Migration from existing demo IDs

The Mona Lisa passport currently uses `AP-2026-000001`. Before any real client engagement:

1. Generate canonical IDs for all existing records using the new scheme
2. Set up permanent redirects from old IDs to new
3. Update internal documentation, passport HTML, and exports

---

## 4. Versioning

### Commitment

Every passport record has a **version number**, incremented when meaningful content changes:

- Version 1 is the first published version
- Minor edits (typos, formatting) do not bump version
- Substantive changes (new attribution, new provenance, new authority links) bump version
- Old versions remain accessible at versioned URLs forever
- The unversioned URL always serves the latest version

URL examples:

```
https://artbase.eu/p/AB7F3KQ2X1          — latest version
https://artbase.eu/p/AB7F3KQ2X1?v=1      — first published version
https://artbase.eu/p/AB7F3KQ2X1?v=2      — second version
https://artbase.eu/p/AB7F3KQ2X1/history  — full version history
```

Each version records:

- Date of issue
- What changed (a `change_summary` field)
- Who made the change (cataloguer ID)
- Reference to previous version

### Reasoning

- Scholarly citations made today must resolve to the same content years later — that requires versioned URLs
- A catalogue raisonné published in 2030 citing "ArtBase AB7F3KQ2X1 v3" must work in 2050
- Modern web habits assume single URLs; default-to-latest with optional version pinning gives both audiences what they need

### Conditions for change

- The versioning scheme can be extended (add new fields) but cannot remove or rename existing fields
- Version numbers never reset, never reassign

---

## 5. Licensing

### Commitment

Two-track licensing applies to every record:

| Component | Default licence | Notes |
|---|---|---|
| **Catalogue text** (descriptions, provenance, scholarly notes) | CC BY 4.0 | Open for reuse with attribution |
| **Catalogue metadata** (Object ID fields, authority links, dimensions, structured data) | CC0 1.0 | Public domain — facts cannot be copyrighted, but explicit dedication clarifies |
| **Images** | Per source — varies | Photographer/owner retains rights; rights statement on each resource |
| **Passport HTML/PDF as a whole** | CC BY 4.0 | When the underlying components allow |

Clients choose at engagement whether their records are **published** (subject to the licences above) or **private** (no public licensing applies; record stays internal). Per-record visibility is configurable.

### Reasoning

- Open licensing is what turns ArtBase from "a private firm's archive" into "infrastructure others build on"
- Wikidata, Europeana, scholarly databases can only consume from us if licensing permits
- CC BY 4.0 requires attribution back to us — every reuse links back, which is brand-building
- CC0 on structured metadata is standard for linked-data infrastructure (Wikidata uses CC0)
- Images stay rights-managed because we can't safely license what we don't own

### Conditions for change

- Records published under existing licences remain so forever — those licences are irrevocable
- New defaults can be adopted for future records
- Per-record licensing exceptions (more restrictive or more permissive) are allowed at engagement

---

## 6. API and machine-readable access

### Commitment

Every passport is available in machine-readable form at its `/api/p/{id}` endpoint:

- **`/api/p/{id}`** — JSON representation of the full record
- **`/api/p/{id}/eodem`** — EODEM-conformant LIDO 1.1 XML
- **`/api/p/{id}/lido`** — full LIDO 1.1 XML (less constrained than EODEM)
- **`/api/p/{id}/dublin`** — Dublin Core (for legacy aggregators)

OAI-PMH endpoint at `/oai`, exposing all published passports for harvesting by Europeana and other aggregators.

A SPARQL endpoint at `/sparql` (eventually, once corpus justifies it).

### Reasoning

- Machine-readable access is what allows partner systems and scholarly tools to consume the data
- OAI-PMH is the standard harvesting protocol; supporting it makes us harvestable by every major aggregator without negotiation
- SPARQL is the linked-data standard; eventually warranted but not on day one

### Conditions for change

- New API formats can be added freely
- Existing endpoints, once public, remain stable forever — same URL-stability rule applies

---

## 7. Public-private boundary

### Commitment

Every record has a `visibility` field with these values:

| Value | Meaning |
|---|---|
| `private` | Internal only. Never appears on the public site. Default for corporate/private clients. |
| `unlisted` | Accessible by direct URL only. No index, no search, no discovery. For records that need to be sharable with specific parties (insurers, conservators) without being public. |
| `public-unindexed` | On the public site, retrievable by direct URL, but not in browse/search results. For records owners want available but not actively promoted. |
| `public` | Fully indexed, browsable, searchable, harvestable. The default for the publication corpus. |

The flag is set per record by the client at engagement. It can be changed by the client at any time (more public is always allowed; less public may require additional procedures if the record has already been harvested by external aggregators).

### Reasoning

- Different clients have radically different visibility needs in the same software
- The four-state model maps to real use cases without over-engineering
- Client control over their own records is non-negotiable; clients who can't trust this won't use the service

---

## 8. Commitments that follow from the above

By making these decisions, ArtBase implicitly commits to:

- Operating the `artbase.eu` domain in perpetuity
- Maintaining 200-OK responses (or correctly issued redirects) on every published URL forever
- Never reassigning an issued ID
- Honouring published licences forever (they are irrevocable)
- Maintaining version history of every published record forever
- Notifying external harvesters before any breaking change to API or schema

These are real obligations. They limit our freedom of action. They are also exactly what makes ArtBase trustworthy as long-term documentary infrastructure — the same obligations Wikidata, Getty, and ORCID make, and the reason scholars cite them.

---

## 9. Decisions to make immediately

Before any real client engagement, the following must be done:

- [ ] Register `artbase.eu` (and supporting domains)
- [ ] Set up DNS with placeholder landing page
- [ ] Generate canonical IDs for any existing demo records
- [ ] Update mockup HTML files to use canonical URL pattern
- [ ] Add licensing language to client engagement template
- [ ] Add visibility-flag selection to the cataloguing intake form
- [ ] Document the ID-generation algorithm in code (so future Claude/cataloguer can produce IDs)

These are low-cost, low-risk preparatory steps. None of them prevent the service business from operating; all of them preserve the platform option.

---

## 10. Decisions deferred

Explicitly deferred until corpus justifies the work:

- Building the public website (Year 1+, once 50+ records exist)
- Implementing the API endpoints (Year 1–2)
- OAI-PMH provider (Year 2+)
- SPARQL endpoint (Year 3+, optional)
- Federated partnership program (Year 2–3+, see partnership document)

These are deferred not because they're unimportant but because they cost real engineering effort and only earn their place once there's data to publish.

---

*This document is the source of truth for ArtBase's foundational technical commitments. Changes require explicit version bumps and justification entered in a changelog section at the bottom (when one exists).*
