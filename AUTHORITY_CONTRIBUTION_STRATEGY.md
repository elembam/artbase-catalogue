# Authority Contribution Strategy

*How ArtBase's contributions to Wikidata, Getty, and other public authorities become the platform's credibility infrastructure over time.*

Version 0.1

---

## The strategic frame

The artist-identity workflow already in the operations playbook is **a service to the client**: we establish the artist in public authorities as part of the cataloguing engagement.

This document elevates that work into something more: **the same activity is also brand-building, infrastructure investment, and platform credibility**. Every Wikidata entry we create cites ArtBase as a source. Every Getty submission lists ArtBase as a contributor. Every Wikipedia article that emerges from this work links back to the passport. Over five years, these accumulated citations make ArtBase a recognised name in the field — not through marketing spend, but through visible, verifiable contribution to shared infrastructure.

This is the same way Wikidata, ORCID, and Crossref became trusted: they consistently did real work in public view, attributed properly, over enough years that the field took notice.

---

## Goals (5-year horizon)

By end of Year 5, ArtBase aims to have:

- **500+ Wikidata entries** created or substantively improved
- **100+ Getty ULAN records** accepted with ArtBase as cited contributor
- **30+ Wikipedia articles** drafted or significantly contributed to
- **1,000+ external citations** of ArtBase passports in scholarly databases, exhibition catalogues, auction records
- **Recognised contributor status** with the Getty Vocabularies Program
- **First peer-reviewed academic citation** of an ArtBase passport as a primary source

None of these are vanity metrics. Each one is a measurable form of platform credibility that compounds over time.

---

## The contribution cadence

### Weekly (per-engagement work)

During active cataloguing, the artist-identity workflow produces:

- **Wikidata entries** for any artist meeting notability who lacks one
- **Wikidata improvements** for any artist whose existing entry is incomplete or unsourced
- **Cross-references added to Wikidata** — when an artwork has an existing Wikidata entry, we add ArtBase ID as an external identifier property (proposed property `P-ArtBase-ID`, to be submitted)
- **External-identifier additions to Wikidata** — VIAF, ULAN, ICONCLASS where we've researched them

Recorded in the per-engagement contribution log.

### Monthly (cross-engagement aggregation)

Once a month, the cataloguer:

- Reviews all artist records added that month
- Identifies candidates for Wikidata improvement, Getty submission, or Wikipedia drafting
- Updates the ArtBase public Contributions log
- Posts a contribution summary to the ArtBase Wikidata user page

### Quarterly (Getty batch submissions)

Every three months:

- Compile the queue of artists meeting Getty ULAN criteria (career documented in scholarly sources, life dates verified, multiple references)
- Prepare the Getty contribution spreadsheet
- Submit to ULAN@getty.edu with a cover note identifying ArtBase as the contributing organisation
- Track acceptances; update internal records when ULAN IDs are assigned
- Same cadence for AAT (term proposals) and TGN (place additions) when relevant

### Annually (program review)

Once a year:

- Audit the contribution metrics
- Identify gaps (artist nationalities under-represented, periods under-covered, etc.)
- Set targets for the next year
- Update this document if strategy needs adjustment
- Publish an annual report on the public site

---

## Where credit accumulates

Each contribution channel has its own form of attribution. We track them all:

| Channel | Attribution form | Where visible |
|---|---|---|
| **Wikidata** | Edit history under ArtBase user account; references citing artbase.eu | Wikidata user page, item edit history |
| **Getty ULAN** | "Contributor" field in vocabulary records | ULAN records, contributors list on Getty site |
| **Wikipedia** | Citation in article references, talk-page attribution | Article reference lists |
| **Europeana** | Provider field when records harvested | Europeana institutional pages |
| **VIAF** | Indirect, via national library records that cite us | VIAF aggregated records |
| **Scholarly citation** | Footnote, bibliography entry citing passport URL | Books, exhibition catalogues, journal articles |

**The ArtBase Wikidata user page** is the public consolidated record of this work — a single page on `wikidata.org` showing all contributions, with links to the ArtBase site for context.

---

## Integration with the existing workflow

This strategy doesn't replace the artist-identity playbook — it sits on top of it.

| Existing workflow phase | What's added |
|---|---|
| Phase 1 (Search) | Same, but findings are also entered into the monthly summary |
| Phase 2 (Gather evidence) | Same |
| Phase 3 (Wikidata) | Edit signed under the ArtBase account, not personal account |
| Phase 4 (Wikipedia) | Same, but tracked centrally |
| Phase 5 (Getty) | Aggregated into the quarterly batch — no individual submissions |
| Phase 6 (Internal authority) | Cross-checked monthly: has this artist become notable enough since? |

The new operational artefact is the **contribution log** — a simple structured file maintained per engagement and aggregated for public reporting.

---

## The contribution log

Each engagement produces a contribution log entry in this shape:

```yaml
engagement: ENG-2026-007
client_anonymised: "Nordic Bank A"
period: 2026-Q2

wikidata_created:
  - artist: "Anna Lindgren"
    qid: Q1287445
    date: 2026-05-22
    contributor: K. Andersson

wikidata_improved:
  - artist: "Karin Mamma Andersson"
    qid: Q453219
    changes: ["life dates added", "ULAN cross-reference", "represented_by"]
    date: 2026-05-11

ulan_batched:
  - artist: "Bjarke Ahlstedt"
    queued_for: 2026-Q3-batch
  - artist: "Marja Salonen"
    queued_for: 2026-Q3-batch

wikipedia_drafted:
  - artist: "Bjarke Ahlstedt"
    article: "Bjarke Ahlstedt"
    status: "accepted 2026-04-30"

external_ids_added:
  - artwork: AB7F3KQ2X1
    added: ["wikidata Q12418", "viaf 24604287", "louvre cl010066723"]
```

These logs are aggregated quarterly into the public contribution summary displayed on `artbase.eu/contributions`.

---

## What stays private vs. what becomes public

The contribution log itself is **mostly public** — it demonstrates the platform's contribution to shared infrastructure. The exceptions:

- **Client identity is anonymised** in the public log (e.g., "Nordic Bank A" not the actual bank name) unless the client has explicitly authorised attribution
- **Internal artist records** that did not result in an external contribution are not published — Phase 6 outcomes stay in client records
- **Submission failures** (rejected Getty submissions, deleted Wikidata items) are recorded internally but not paraded publicly

The principle: be visibly generous about what we contribute, discreet about who paid for it.

---

## Why this matters for the business

Three concrete reasons:

**1. Sales credibility.** A prospective client asking "have you done this before?" can be answered with a public, third-party-verifiable contribution record. "Look at our Wikidata user page" or "see our Getty contributor credit" is qualitatively different from "trust us." This shortens sales cycles and justifies premium pricing.

**2. Talent attraction.** Cataloguers who care about doing serious work want to work for an organisation visibly contributing to the field. Public contribution credit is a recruiting tool money can't buy.

**3. Long-term moat.** Most service businesses can be replicated. The reputation built from five years of consistent, attributed contributions to shared authorities is genuinely hard to replicate from a standing start. By Year 5, a competitor would have to begin Year 0 of the same work — a multi-year head start is what makes ArtBase defensible.

---

## What to set up immediately

To enable this strategy:

- [ ] Create the ArtBase Wikidata user account (use a stable, professional name — e.g., `User:ArtBase`)
- [ ] Set up the user page with project description, contribution principles, and contact
- [ ] Establish the per-engagement contribution log file format
- [ ] Add a public `/contributions` page on the ArtBase site (template ready; populated as engagements complete)
- [ ] Submit a property proposal to Wikidata for `ArtBase ID` (the property that will let other Wikidata items link to us)
- [ ] Open dialogue with Getty Vocabularies Program (email Patricia Harpring's office, introduce the project, ask about institutional contributor status)

None of these require building software or website infrastructure — they're administrative and relationship steps. They cost almost nothing and they unlock the credibility infrastructure that takes years to build otherwise.

---

*The contributions program is recognised as one of the four foundational pillars of ArtBase (alongside the service offering, the public registry, and the partnership network). It is not a marketing function — it is operational core.*
