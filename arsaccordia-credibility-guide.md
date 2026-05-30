# Ars Accordia — Site Credibility & Coherence Guide

*A standing reference for keeping the public site, the catalogue artifacts, and the project's stated mission aligned. Written after review of the `/about/` page (arsaccordia.com/about/).*

---

## Why this document exists

Ars Accordia has reached the point where it makes strong public claims about its standards, methodology, and mission. The `/about/` page now positions the project as *"the reference registry for European art held in private and corporate collections,"* compliant with a serious museum-documentation stack (Object ID, CDWA, LIDO 1.1, EODEM, the Getty vocabularies, ICONCLASS, Wikidata, VIAF, Schema.org).

That is a real achievement. It is also a liability if the claims outrun the artifacts. A registry's only asset is trust, and trust is destroyed not by having little data, but by promising more than the data delivers. This document explains the specific places where claim and reality currently diverge, why each gap matters, and how to close it. It is meant to be handed to Copilot or used as a checklist before the next phase of growth.

**The governing principle:** *Every public claim must be true in the artifact a visitor can click into.* If the About page says passports record provenance and condition, the passports must record provenance and condition — or the page must say "where available." There is no third option that preserves credibility.

---

## Issue 1 — The claims-versus-reality gap

### What the About page promises

The page describes what an Artwork Passport contains: identity fields, authority links to six-plus registries, a provenance chain with dates and sources, a condition report, Schema.org structured data, and LIDO 1.1 / EODEM XML export formats. It presents this as the standard every record meets.

### What the artifacts currently deliver

There are two passports in existence. On inspection, the Siliņš passport (AP-2026-000002) had an empty provenance section, no condition data, and no image. The Mona Lisa passport (AP-2026-000001) carried ICONCLASS codes that were hardcoded demonstration values rather than researched iconography. None of the export formats (LIDO, EODEM) are visible as downloadable artifacts on the passport pages.

### Why this matters

The About page is written in the present tense, as a description of current practice. A visitor who reads the impressive standards list and then opens one of the two passports finds most of those fields empty. The gap is not neutral — it actively converts the page's strength (rigor) into a weakness (overpromising). A skeptical reader, which is exactly the kind of reader a "scholarly registry" attracts, will trust the empty artifact over the confident page and conclude the standards are aspirational marketing.

### How to close it

Two options. With only two passports in existence, the first is both achievable and far more persuasive:

1. **Make the two existing passports genuinely exemplary.** Fill provenance (even a minimal sourced chain), add a condition note, attach an image, replace demo ICONCLASS with real iconography, and generate the LIDO/EODEM exports the page claims. Two passports that *fully* embody the standards page are worth more than two hundred thin ones. They become the proof that the standards are real.

2. **Or, if completion must wait, reframe the page.** Change the passport-contents list from an implied universal ("a passport records…") to an explicit specification ("a complete passport records… ; coverage varies by record and is expanding"). This is weaker than option 1 but honest, and honesty is the non-negotiable.

The wrong move is to leave the page as a universal claim while the artifacts contradict it.

---

## Issue 2 — The mission-versus-content mismatch

### The stated mission

The About page defines the mission precisely: documenting *undocumented private and corporate-held European art* — works that are culturally significant but absent from national museum catalogues and Europeana. This is a sharp, defensible niche, and it is the best strategic decision the project has made.

### The current flagship content

The two showcased passports are the **Mona Lisa** and a work by **Herberts Siliņš**, and the catalogue index is ~288 Latvian painters. The Mona Lisa is the single most documented artwork in existence, held by the Louvre — the precise opposite of "undocumented private collection art." Many of the Latvian painters indexed are held in the Latvian National Museum of Art, i.e. already in public institutional catalogues.

### Why this is a contradiction

A registry whose headline example directly contradicts its own mission statement invites doubt about whether the mission is real or decorative. The mismatch is defensible *if framed as demonstration data* — but the page currently offers no such framing, so the reader is left to reconcile "we catalogue undocumented private art" with "here is the Mona Lisa" on their own.

### How to close it

- **Identify a genuinely private or corporate-held work and make it the flagship.** If the Siliņš sea painting is privately held, it already embodies the mission — invest in making it the exemplary, complete passport described in Issue 1, and lead with it.
- **Reframe the Mona Lisa explicitly as a standards demonstration** ("included to demonstrate the cataloguing standard against a universally known work"), or retire it from the front position once a mission-fit exemplar exists.
- **Treat the Latvian painter index as what it is** — a seed dataset and authority-reconciliation exercise — and say so, rather than letting it read as the catalogue's core deliverable.

---

## Issue 3 — The missing path for the target user

### The conversion gap

The mission is to bring *private and corporate collections* into documentation. That implies a specific target user: a collector, family office, company, or estate holding undocumented works. Yet the page offers that user no next step — no "how to submit a work," no contact, no description of how a private collection actually gets catalogued by Ars Accordia.

### Why this matters

For a registry whose entire purpose is bringing collections *in*, the absence of an intake path means the page describes a service nobody can actually request. Every other element of the page builds toward a value proposition, and then the proposition has no door.

### How to close it

Add a short, concrete intake section: who to contact, what the process looks like at a high level, and what a collector receives (a permanent passport, authority links, export formats). Even a single line — *"To enquire about cataloguing a collection, contact [address]"* — converts the mission from a statement into an offer. This also forces a useful clarity about whether the service is free, paid, or selective, which connects to Issue 5.

---

## Issue 4 — Public compliance claims that must be verified in the artifacts

Two items that were previously internal to-dos are now *public claims* on the About page. Publishing a claim raises the stakes: an unmet internal goal is a backlog item, but an unmet public claim is a misrepresentation.

### 4a — ICONCLASS compliance over demonstration data

The page lists ICONCLASS as a vocabulary the catalogue uses. The Mona Lisa passport's ICONCLASS codes were established earlier to be hardcoded demo values. If those are still present, the page is asserting ICONCLASS compliance over data that was never researched. The provenance-audit step (`audit_provenance.py`) exists precisely to catch unattributed fields like these; it should be run and the demo codes either replaced with real iconography or removed before the claim stands.

### 4b — Schema.org `sameAs` candidate exclusion

The page states plainly that candidate (⚠) links *"should not be treated as authoritative."* The Schema.org JSON-LD embedded in passport pages must honor this: candidate-status authority URIs must **not** appear in the machine-readable `sameAs` array, because `sameAs` is an unqualified identity assertion that aggregators and search engines treat as confident. If candidate QIDs still leak into `sameAs`, the structured data contradicts the standard the page itself defines — and worse, propagates unverified identity claims across the web where they are hard to retract.

### Verification

Both are checkable on a single passport. Fetch `AP-2026-000002.html`, inspect the embedded `<script type="application/ld+json">`, and confirm: (a) no demo ICONCLASS, (b) `sameAs` contains only confirmed authorities, (c) the holding institution is expressed as `owner`, not `locationCreated`. (See the earlier JSON-LD review for the full field-by-field correction list.)

---

## Issue 5 — Coherence between the commercial face and the Wikidata-citizen face

### The tension

The About page leans commercial in register: *"service," "at scale," "corporate boardroom."* That is a legitimate and probably necessary framing for a registry serving private collections. But Ars Accordia also operates a Wikidata contributor identity (the `Arsaccordia` account) that is positioned as a non-commercial, standards-respecting scholarly contributor. These two faces must stay coherent.

### Why it matters

The Wikidata community is actively wary of commercial entities that mine the platform to power a paid product, and of self-promotional sourcing. If the contribution work and the commercial service blur together — for example, if Ars Accordia were to cite its own commercial catalogue as a source on Wikidata claims — the community reaction would be swift and would damage both faces at once.

### How to keep them coherent

- Keep the **contribution work non-commercial and externally sourced**: every Wikidata statement references the underlying authority (LNDB, LIBRIS, ULAN, museum records), never the Ars Accordia catalogue itself. (This rule is already baked into the contribution pipeline; the point is to never relax it under commercial pressure.)
- Keep the **two faces clearly distinguishable** in public materials: the registry/catalogue is the service; the Wikidata account is a contributor that gives sourced data back to the commons. They share standards and rigor, not a sales funnel.
- Revisit this explicitly before any step that would make the commercial catalogue citable on Wikidata (the eventual property proposal), so the move is made transparently and with community input rather than unilaterally.

---

## Priority order

1. **Make the two existing passports exemplary** (Issue 1, option 1) — highest leverage, fully achievable with two records, and it simultaneously resolves the credibility gap and gives you a mission-fit flagship.
2. **Run `audit_provenance.py` and clean the demo ICONCLASS** (Issue 4a) — removes a live misrepresentation.
3. **Verify the JSON-LD** on a passport: confirmed-only `sameAs`, `owner` not `locationCreated`, no demo iconography (Issue 4b).
4. **Reframe the Mona Lisa as a standards demonstration** and label the Latvian index as seed data (Issue 2).
5. **Add an intake / contact path** for collectors (Issue 3).
6. **Add a coherence note** distinguishing the catalogue service from the Wikidata contribution work (Issue 5), and hold the line on external-only sourcing.

---

## The rule to carry forward

As the catalogue grows, re-read the About page against a randomly chosen live passport once per phase. The day the page describes something the passport does not contain is the day credibility starts leaking. Keep the page and the artifacts in lockstep: when a passport gains a capability, the page may claim it; until then, the page describes it as the standard a complete record meets, not as a universal fact. A registry is believed because its weakest record still honors its strongest claim.
