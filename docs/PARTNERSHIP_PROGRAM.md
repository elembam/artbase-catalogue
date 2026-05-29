# Partnership Program

*How independent cataloguers, registrars, and small institutions contribute records to Ars Accordia under shared standards — the federated model that allows the registry to grow without a single firm having to catalogue everything.*

Version 0.1 — program definition

---

## The federation principle

Ars Accordia is not built as a single firm cataloguing every artwork in Europe. That would never scale. The federated model says:

> **Independent cataloguers retain the client relationship and do the cataloguing work. Ars Accordia provides the publication infrastructure, the identifier authority, the shared standards, and the cross-institutional discoverability.**

Each partner is a small firm or independent professional (registrar, cataloguer, art consultant, conservation studio) operating in their own region or niche. They serve their clients directly; Ars Accordia aggregates their published records into a single registry that none of them could build alone.

This is the same model that lets Crossref handle DOIs (publishers register their content; Crossref provides the identifier system and resolution infrastructure) or ORCID work for researchers (institutions onboard their staff; ORCID provides the persistent IDs). It works because the value to each participant — discoverability, credibility, shared infrastructure — exceeds what they could build independently.

---

## Who is a partner

The partnership program is open to:

- **Independent cataloguers and registrars** working with private or corporate collections
- **Conservation studios** that maintain client records as part of their service
- **Art consultancies and advisory firms** that document their clients' collections
- **Small specialised institutions** (foundations, artist estates, regional museums) too small to build their own registry infrastructure

Not currently open to:

- **Galleries and dealers** for their inventory — different use case, conflicts with confidentiality posture
- **Auction houses** — likewise
- **Large museums** — they have their own infrastructure and aggregator relationships

---

## What partners commit to

A partner agreement requires:

**1. Standards compliance.** All records contributed to Ars Accordia must meet the Ars Accordia house standards: Object ID complete, Getty AAT used where applicable, ICONCLASS subject coding, structured provenance, photography to spec, sourced assertions. The Ars Accordia House Style Manual is the reference.

**2. Quality review.** Each partner appoints a senior reviewer responsible for sign-off before any record is contributed. Ars Accordia reserves the right to audit and, in cases of repeated quality failure, suspend contribution privileges.

**3. Authority work.** Partners follow the artist-identity workflow for their own clients' artists — establishing Wikidata, Getty ULAN, and Wikipedia entries where appropriate. Authority work is part of partner service delivery, not a separate Ars Accordia service.

**4. Per-record visibility flags.** Partner-contributed records carry the same visibility model as Ars Accordia-direct records. Partners and their clients control what is public, unlisted, or private.

**5. Attribution honesty.** Partner-contributed records are clearly attributed to the partner. The catalogue page shows "Contributed by [Partner Name]" alongside the Ars Accordia ID.

**6. Licensing compliance.** Records contributed for publication are released under the Ars Accordia licensing defaults (CC BY 4.0 for text, CC0 for metadata). Partners cannot contribute records they don't have the rights to license.

---

## What partners receive

**1. The Ars Accordia identifier scheme.** Every record they contribute gets a permanent `AB`-prefixed ID. This is something they could not credibly issue on their own behalf.

**2. The publication infrastructure.** Records appear on `arsaccordia.com` under the partner's attribution. The partner's clients see passports hosted at a recognised registry, not a one-firm website.

**3. Discoverability through aggregation.** Partner-contributed records become harvestable by Europeana, indexed by search engines, and cross-referenced from Wikidata. The partner's clients benefit from being part of a larger findable corpus.

**4. Standards and tooling.** Partners use the same House Style Manual, the same LIDO/EODEM transformation pipeline, the same passport templates as Ars Accordia Cataloguing. The infrastructure is shared.

**5. Cross-partner referrals.** When a client of Ars Accordia Cataloguing needs work outside Sweden — a Belgian provenance question, a Dutch artist research project — referral to a partner is the natural path. Same goes for partners with cross-border client needs.

**6. Visible attribution.** Every partner-contributed record links to the partner's profile page on Ars Accordia. Partner page shows their location, specialisation, contribution count, and contact link. This is real, ongoing brand visibility.

---

## The technical interface

Partners interact with Ars Accordia through one of three methods, depending on their sophistication:

### A. Spreadsheet upload (entry level)

Partner fills in an Ars Accordia-provided cataloguing spreadsheet (essentially the CSV format that the LIDO transformation pipeline already consumes). They upload via a secure partner portal. Ars Accordia processes the upload, assigns IDs, generates passports.

- Best for: small firms, occasional contributions, partners without technical staff
- Latency: 1–5 business days from upload to publication

### B. API contribution (intermediate)

Partner's own cataloguing system sends records to the Ars Accordia API in JSON or LIDO XML. Records are validated automatically; valid records get IDs assigned and are published; invalid records return an error report for the partner to fix.

- Best for: partners with their own CatalogIt, CollectiveAccess, or Artwork Archive setups
- Latency: real-time

### C. OAI-PMH harvest (advanced)

Partner publishes their own OAI-PMH endpoint exposing the records they want contributed. Ars Accordia harvests on a daily schedule. Validation, IDs, publication happen automatically.

- Best for: partners running CollectiveAccess or other museum-grade software
- Latency: up to 24 hours

All three methods produce identical results once published — partners can start with method A and migrate to B or C as their sophistication grows.

---

## Revenue model

The default model is **no fee in either direction**:

- Ars Accordia does not pay partners for contributed records
- Partners do not pay Ars Accordia for the infrastructure

Both sides receive value in non-cash forms (publication infrastructure for the partner, registry growth for Ars Accordia). For most partners and most engagements, this is the right balance.

Two paid variants exist:

**Sponsorship tier** — small institutions or larger consultancies can become "supporting partners" with a modest annual fee (€500–€2,000) that funds infrastructure operating costs. In exchange they get a more prominent profile placement and priority support.

**Per-record service fee** — partners who want Ars Accordia to do the cataloguing work for their clients (rather than contributing existing records) pay a per-record fee. This is the standard service business model, branded as a partner-referral channel.

The non-paying model is intentional and important: it removes any economic barrier to partner participation, which is what allows the registry to grow. Money is a useful filter when you have too many applicants; we don't.

---

## Quality control

The federated model risks quality dilution. Three mechanisms manage that risk:

**1. Standards-based onboarding.** No partner is accepted without demonstrated competence in the standards. Onboarding includes a sample-record review: the prospective partner catalogues 3–5 sample works to the house standards and submits them for review. Approval is contingent on passing.

**2. Automated validation.** All records contributed via API or OAI-PMH are validated against the LIDO XSD, the EODEM Schematron, and the Ars Accordia completeness rules. Records failing validation are rejected with a detailed error report.

**3. Periodic audit.** Each partner's contributions are spot-audited quarterly. A random 5% of records is re-reviewed for compliance with house style. Repeated audit failures trigger a quality review with the partner's senior reviewer.

**4. Right of suspension.** Ars Accordia reserves the right to suspend a partner's contribution privileges in the case of repeated quality failures, attribution problems, or licensing issues. Existing published records are not retroactively removed; future contributions are paused pending remediation.

---

## Onboarding process

A new partner moves through these stages:

| Stage | Activity | Time |
|---|---|---|
| **1 · Inquiry** | Prospective partner contacts Ars Accordia, receives partnership brief | Hours |
| **2 · Self-assessment** | Partner confirms they meet the eligibility criteria | Days |
| **3 · Sample submission** | Partner catalogues 3–5 sample works to house standards, submits | 2–4 weeks |
| **4 · Sample review** | Ars Accordia reviewer evaluates samples, provides feedback | 1–2 weeks |
| **5 · Agreement** | Partnership agreement signed, including licensing and quality clauses | 1 week |
| **6 · Profile setup** | Partner profile created on `arsaccordia.com`, contribution channels provisioned | Days |
| **7 · First contribution** | First batch of real records contributed and published | Variable |

Total time from inquiry to first published partner record: typically 6–10 weeks. This is intentionally substantial. Federation works only when partners are genuinely capable, and the time invested in vetting is what makes the network credible.

---

## Integration with the existing workflow

For Ars Accordia Cataloguing itself, the partnership program changes nothing in day-to-day operations until the first partner is onboarded. The current workflow (CLAUDE.md project, House Style Manual, Artist Identity Workflow, etc.) is exactly what a partner would be expected to follow.

The bridge between Ars Accordia Cataloguing and partners is the **shared standards documents**. The House Style Manual, the workflow playbooks, the architecture decisions — these are the same for both. Ars Accordia Cataloguing is, in effect, the founding partner of its own federation: subject to the same standards it asks others to follow.

When the time comes to onboard the first external partner, the package they receive is the same package Ars Accordia Cataloguing already runs on:

- House Style Manual
- Artist Identity Workflow
- LIDO Pipeline (or its hosted equivalent)
- Passport templates
- Architecture Decisions (the URL and ID schemes they will use)
- Partnership Agreement (legal/contractual layer)

---

## Year-by-year plan

| Year | Status | Partners |
|---|---|---|
| **1** | Federation framework documented (this document). No external partners yet. Ars Accordia Cataloguing operates as the founding member. | 0 |
| **2** | First 1–2 partners onboarded after the registry has 200+ records and credible public profile. | 1–2 |
| **3** | Targeted recruitment in adjacent regions (Finland, Netherlands, Germany). | 3–5 |
| **4** | Federation begins to feel like one. Cross-partner referrals routine. Quality audit cadence established. | 6–10 |
| **5** | Ars Accordia recognised in the field as a registry-of-record for European private and corporate art. | 10–20 |

These numbers are deliberately modest. The goal is durability, not headline growth.

---

## What to set up immediately

To preserve the federation option without building it yet:

- [ ] Adopt this document as the program definition (this version of the file)
- [ ] Reference it in the architectural decisions and CLAUDE.md so future cataloguers know it exists
- [ ] When future client engagements occur, treat the contributing cataloguer (us, today; someone else, eventually) as a "partner" in the data model — i.e., every record has a `contributor` field, populated as `Ars Accordia Cataloguing` for direct work
- [ ] When designing the public site, include the partner profile page template — even if the only partner is Ars Accordia Cataloguing itself for the first year
- [ ] When designing the API, design it for partner contribution from day one, even if only used internally

The cost of doing this now is essentially zero. The cost of retrofitting partner support into a system designed only for in-house work is significant.

---

*The partnership program is the long-term scaling mechanism. It is not Year 1 work, but the Year 1 architecture must permit it.*
