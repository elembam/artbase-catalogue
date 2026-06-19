# Instruction 12 — Collection Page & Score Display

*Hand to Copilot as a single component. It builds on Instruction 9 (contributors, verification, visibility), Instruction 10 (validation levels and the conformance badge), and Instruction 11 (the collection score). It defines how collections appear on the Ars Accordia website and how the score renders. The reference design is `ars-accordia-collection-page-mockup.html`. Where it conflicts with Copilot's instinct, the spec wins — ask before deviating.*

---

## Purpose

Define the public presentation of collections: how they are listed, claimed, and — once assessed — scored. The model is deliberately two-layer: an **open, claimable registry** for discovery (the IMDb/Goodreads layer) and an **earned Documentation Score** that appears only after assessment (the credential layer).

---

## The core principle: a listing is open, a score is earned

The registry may list any collection for discovery, and an owner may **claim** it — that is the open layer. But the Documentation Score is **not** an auto-generated rating that exists for everything. It is `Coverage × Quality`, and every term measures **Ars Accordia passports** (Instruction 11). So there is nothing to score until the cataloguing has been done.

- IMDb can rate any film because the rating is the crowd's opinion of a film that already exists — observable from outside, requiring no work on the film.
- Ars Accordia's score is an **expert assessment** — closer to a bond rating or a critic's review — and like those it requires the assessment to have *happened*. The score measures *our work on the collection*, not an external property of it.

**Therefore: list and claim broadly; score on assessment.** This is not a limitation — it is the source of the score's authority. A score that is earned and consistently measured means something; one auto-assigned to everyone is noise.

**The misleading-number rule (load-bearing):** an un-assessed collection **never** shows a number. If Ars Accordia published a score for a collection it has barely catalogued, the figure would read near-zero on coverage — which does not mean the collection is poorly documented, only that *we* have not catalogued it. That would be false, unfair to the owner, and self-serving. Un-assessed → "Not yet assessed," never "3%."

---

## Part A — The two page types

| | **Registry / catalogue page** | **Scored credential page** |
|---|---|---|
| When | Any collection Ars Accordia has listed or catalogued in part | Assessed (engaged) **and** consented to publish |
| Shows a score? | **No** — "Not yet assessed" | **Yes** — full score display |
| Purpose | Discovery, the works we've catalogued, an entry to claim | The Documentation Score as a public credential |
| Score block | Replaced by a "Not yet assessed — claim this collection" panel | The seal, three dimensions, band scale, gap map (per mockup) |
| Works | The works Ars Accordia has catalogued so far, each with its own conformance badge | All in-scope passports, each with its badge |
| Directory | Listed in the open registry | **Additionally** listed in the scored-collections directory (Part E) |

The two must be **visually distinct** so a visitor never mistakes an unscored catalogue page for a *low* score. The catalogue page leads with "Not yet assessed"; the scored page leads with the seal.

---

## Part B — The claim mechanism

A collection's owner or authorised representative (museum, corporate collection, estate, private collector) may **claim** its registry entry — as on Goodreads (an author claiming a book) or Google Business (a business claiming its listing).

**Claim states** (on the collection record):

```
unclaimed  →  claimed_pending  →  claimed_verified
```

- **Verification** reuses the Contributor model (Instruction 9): the claimant becomes the collection's `owner` Contributor with a `verification_level` (e.g. institutional email-domain match, or staff review). A claim is not active until `claimed_verified`.
- **What a verified claim grants:** manage the public listing metadata (name, description, scope definition), set `visibility` and `consent_to_publish_score`, and **commission an assessment**.
- **What a claim never grants:** setting, editing, or overriding the score. The score is Ars Accordia's assessment, computed from member passports (Instruction 11), independent of the claimant — exactly as an IMDb claimant manages metadata but not the rating. This is a hard rule.

The claim flow is also the commercial funnel: **claim → commission assessment → earn the score → publish the credential.**

---

## Part C — Binding the score display to data (the mockup, wired)

Every element of the scored page binds to the Instruction 11 `score` block. No value on the page is hand-entered.

| Mockup element | Bound to |
|---|---|
| Seal — the figure | `score.ars_accordia_score` (open-ended; **no "/100"** — it is not a percentage) |
| Seal — caption beneath the figure | `score.works_documented` works · `score.average_standard` standard |
| Seal / header band name | `score.band` (the band of the **average standard**, not the absolute figure) |
| "Assessed [date]" | `score_generated_at` |
| Quality panel — Completeness / Corroboration bars | `score.completeness`, `score.corroboration.blended` (Coverage is **not** shown — there is no denominator) |
| L1 / L2 sub-line | `score.corroboration.L1`, `score.corroboration.L2` |
| Average-standard scale marker | `score.average_standard` → highlight that band segment |
| Gap map bars | `score.gaps.*` — **in-scope passport dimensions only** (identity, authority, sourced provenance, structured/export, and condition/image only if commissioned) |
| "Not scored" line | the constant exclusions — authenticity, valuation, plus any depth section not commissioned |
| Scope line (works / corroborated) | `score.works_documented`, count at `FULLY_CORROBORATED` (no "of N" — N is optional and often unknown) |
| Relative % (optional) | `score.relative_completeness` — render **only if present** (i.e. only when `scope.total_extent` is known and solid) |
| Works grid — per-work badge | each member passport's conformance badge (Instruction 10): green `FULLY_CORROBORATED` + human-reviewed, amber partial/automated, grey `ENTITY_SUPPLIED_ONLY` |
| "How the score works →" | the published methodology (Instruction 11 client-facing section) |

The score, the gap map, and the per-work badges therefore stay automatically consistent with the underlying passports — the collection seal is the visible roll-up of the badges in the works grid.

---

## Part D — Public / restricted / private rendering

Reuse the visibility model (Instruction 9 / 11). The **same score components** render in each context; only *where* differs:

| State | Where it renders |
|---|---|
| **Public** (`visibility: public` + `consent_to_publish_score: true`) | Full scored page on the public site; listed in the scored directory |
| **Restricted** | Scored page reachable by direct link only; not indexed, not in the directory |
| **Private** | **Never on the public site.** The identical score components render only in the owner's authenticated workspace |
| **Assessed, consent withheld** | Catalogue page publicly; score visible to the owner only |
| **Un-assessed** | Catalogue page only; "Not yet assessed"; claimable |

A private collection's score is a confidential KPI; a public score is a credential. The components are shared; the gate is `visibility` + consent.

---

## Part E — The scored-collections directory (the "how they stack up" view)

A public index of collections that are **assessed and consented** — the comparative view.

- Lists each scored collection with its **Ars Accordia Score**, **average-standard band**, **work count**, and segment-type (corporate / private / estate / institution).
- Sortable and filterable. Because the absolute score conflates size and quality, **sort by the average standard** for a like-for-like quality view, and treat the absolute score as a volume figure read in context — not a quality ranking. Present it as a **directory, not a league table**: per Instruction 11, the absolute score reflects how much documentation exists, the average standard reflects how good it is, and a 12-work corporate collection and a 4,000-work museum are not the same contest. Avoid a single ranked-by-size leaderboard; allow browsing and filtering instead.
- Un-assessed collections appear in the **open registry** but **not** in the scored directory. As more collections are assessed, the directory grows into the comparative registry over time.

---

## Part F — Data model

Extend the `collections` registry (Instruction 11):

```json
{
  "collection_id": "COL-MERIDIAN",
  "name": "The Meridian Collection",
  "segment": "corporate",                 // corporate | private | estate | institution
  "page_type": "scored",                  // registry | scored  (derived: scored iff assessed && consented)
  "listing": {                            // shown on the registry/catalogue page
    "description": "...",
    "public_works_catalogued": 96
  },
  "claim": {
    "status": "claimed_verified",         // unclaimed | claimed_pending | claimed_verified
    "claimant_contributor": "CON-...",
    "verified_at": "2026-05-DD"
  },
  "scope": { "definition": "...", "total_extent": 142, "status": "owner_declared", "source": "..." },
                                  // total_extent OPTIONAL (Instruction 11) — enables the relative % only
  "member_passports": [ "AP-..." ],
  "visibility": "public",
  "consent_to_publish_score": true,
  "assessment_status": "assessed",        // not_assessed | assessing | assessed
  "score": { ... },                       // present only when assessed (Instruction 11)
  "score_generated_at": "2026-05-DD"
}
```

`page_type` is **derived**, not authored: a page is `scored` only if `assessment_status == assessed` AND `consent_to_publish_score`; otherwise `registry`. (A known `total_extent` is *not* required — the Ars Accordia Score needs no denominator; it gates only the optional relative-% view.)

---

## Part G — Templates

- `collection_registry.html.j2` — the unscored catalogue page (identity, catalogued works, "Not yet assessed — claim this collection").
- `collection_scored.html.j2` — the scored credential page (the mockup).
- Or a single `collection.html.j2` with the score block behind `{% if page_type == 'scored' %}`.
- Build the score seal (figure + average-standard + count), the Completeness/Corroboration bars, the average-standard scale, and the gap map as **partials**, so the identical components render on the public page and in the private owner workspace.
- The collections directory: `collections/index.html` listing scored collections (Part E).

---

## Acceptance tests

1. A collection with `assessment_status: not_assessed` renders the registry page with "Not yet assessed" and no number anywhere; it is absent from the scored directory.
2. A collection becomes a scored page **only** when assessed AND `consent_to_publish_score`; dropping either reverts it to the catalogue page. A known `total_extent` is not required to be scored.
3. The seal figure, average standard, band, quality bars, and gap map all read from the `score` block; editing a member passport and recomputing changes them with no template edit. The relative-% renders only when `score.relative_completeness` is present.
4. Each work's badge reflects its own validation level; the collection's corroborated count equals the number of green badges.
5. The gap map shows only in-scope passport dimensions; authenticity and valuation never appear as bars, and appear in the "Not scored" line.
6. A claim is inactive until `claimed_verified`; a verified claimant can set visibility/consent and commission an assessment but cannot alter the score.
7. A `private` collection never appears on the public site or in the directory; its score renders only in the authenticated owner workspace.
8. The registry page and the scored page are visually distinct — an un-assessed collection cannot be mistaken for a low score.

---

## What this component does NOT do

- It does **not** show a score — not even a provisional or near-zero one — for a collection that has not been assessed. Un-assessed means "Not yet assessed," never a number.
- It does **not** let a claimant set, edit, or override the score; claiming manages the listing, not the rating.
- It does **not** publish a score without `visibility: public` + consent. (It needs no denominator — the Ars Accordia Score is absolute; a known extent gates only the optional relative-%.)
- It does **not** present the absolute score as a percentage or render a "/100" on the seal — the figure is open-ended and read beside the average standard and the work count.
- It does **not** rank all collections in one leaderboard as if comparable; the directory is browse-and-filter, and the score is primarily a collection's own measure over time.
- It does **not** render private scores anywhere public; the public page is the consented-public branch only.
- It does **not** invent page content — `page_type`, the score, and the badges are all derived from the collection record and its member passports.
