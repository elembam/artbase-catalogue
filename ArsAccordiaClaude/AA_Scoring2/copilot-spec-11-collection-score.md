# Instruction 11 — Collection Score (the Ars Accordia Score)

*Hand to Copilot as a single component. The per-passport value used here is exactly the **Passport Score** of Instruction 13 (`100 × Completeness`); this spec aggregates those scores to the collection. It also uses the visibility/privacy model (Instruction 9). The "Client-facing methodology" section near the end is written to be lifted out and shown to a collector. Where it conflicts with Copilot's instinct, the spec wins — ask before deviating.*

---

## The governing principle (read first)

**Ars Accordia compares publicly available reference data; it does not judge it.** The score measures how complete a record is — including whether a work is cross-referenced to public authority records (Getty, Wikidata, VIAF, national libraries) — and nothing more. We count cross-references and recorded fields; we never grade how trustworthy a source is, never rank source types, and never score authenticity or value. Those are opinions, and opinions are outside our competence. This holds at the collection level exactly as it does at the passport level.

---

## Purpose

Give a **whole collection** a single ownable figure — the **Ars Accordia Score** — aggregated over the passports it contains, read alongside an **average standard** and a **work count** that together say how much documentation exists and how complete it is, plus a gap map that shows what to improve. Private collections are scored privately; public collections are scored publicly *with consent*. The score is the commercial engine: it aligns the metric with the unit of sale (the collection), grows with every work catalogued, and the gap map writes the next proposal.

---

## Why the score is absolute, not a percentage

A percentage needs a denominator — the collection's *total extent* — and for most collections that number is genuinely unknowable: you cannot reliably enumerate every work a museum holds, or every work a living collector owns. A score resting on a guessed total is itself a guess. So the Ars Accordia Score is **absolute and open-ended**: each passport contributes its own score, and the collection's score is their **sum**. There is no denominator to establish and none to game. A collection Ars Accordia has barely catalogued simply has a small score — reflecting the little documentation that exists — never a misleadingly low "percentage" implying the collection itself is poorly kept.

To stop the absolute score being a pure size contest, it is always read alongside the **average standard** — the mean passport score — which is *size-independent*: a small, immaculately documented collection and a large one both read near the top. **The absolute score says how much; the average standard says how complete; the count says how many.**

---

## The model

```
Per-passport value   v_i = Passport Score = 100 × Completeness_i      # 0–100 (Instruction 13)

Ars Accordia Score   = Σ v_i                 # open-ended — the headline figure
Average standard     = mean(v_i)             # 0–100 — size-independent, carries the band
Works documented     = count(passports)      # the volume

# OPTIONAL, shown only where the total extent is genuinely known (e.g. a fixed corporate inventory):
Relative completeness = Σ v_i / (N × 100)    # 0–1 — never forced, never guessed
```

The three headline outputs — **Score, average standard, works documented** — are always displayed **together**; the absolute number alone is not interpretable without the standard and the count beside it.

---

## Part A — Scope (definition required, total optional)

Every collection records a **defined scope** — the human-readable rule for what counts as a member:

```json
"scope": {
  "definition": "All works owned by the entity as of 2026-06-01",  // inclusion rule — always recorded
  "total_extent": 142,              // N — OPTIONAL; enables the relative % only
  "status": "owner_declared",       // inventory_confirmed | owner_declared | estimated | unknown
  "source": "On-site inventory, 2026-05"
}
```

- The **definition** is always recorded — it states what the collection *is*, so the membership of `member_passports` is meaningful.
- **`total_extent` (N) is optional.** The Ars Accordia Score, the average standard, and the work count are all computed **without** it. N feeds **only** the optional relative-completeness view, shown only when `status` is `inventory_confirmed` or `owner_declared`.
- **No N is a normal, fully-scored state** — not an error. The collection shows its absolute score, standard, and count, simply without a percentage.

---

## Part B — The per-passport value (= the Passport Score)

Each passport's value is its **Passport Score** from Instruction 13: `100 × Completeness`, where completeness is the weighted fill of the passport's own sections —

| Passport section | Weight | Filled by… |
|---|---|---|
| Identity | 0.35 | the six descriptive fields present to standard |
| Authority links | 0.25 | **cross-references to public authority records** (Getty ULAN/AAT, Wikidata, VIAF, national libraries) — counted by presence, never graded |
| Provenance, sourced | 0.25 | ownership-chain steps that carry a cited source |
| Structured / export | 0.15 | JSON-LD + EODEM export present |

(Condition and Image enter only when the engagement commissioned them; Instruction 13.) There is **no corroboration term** — the value is completeness alone. A passport richly cross-referenced to public authorities and fully recorded scores near 100; a bare entry scores near 0. The cross-referencing that gives a record its standing is rewarded *as completeness*, because it is a section of the passport — not as a separate judgement.

---

## Part C — Bands (on the average standard, describing record completeness)

The band describes the **average completeness of the records that exist** — *not* the collection's completeness against a total, which the score deliberately does not claim to measure. The absolute Ars Accordia Score is **unbanded** (a figure read in context of the standard and the count); the band attaches to the **average standard** (0–100):

| Band | Average standard | Meaning — the standard of the records |
|---|---|---|
| **Complete Record** | ≥ 85 | Records near-complete and richly cross-referenced |
| **Substantial Record** | 65–84 | Most fields present and cross-referenced |
| **Partial Record** | 40–64 | Core identity present; cross-references or provenance still thin |
| **Outline Record** | 15–39 | Basic entries, lightly referenced |
| **Minimal Record** | < 15 | Bare entries |

Always display the **Ars Accordia Score + the average-standard band + the work count + the section breakdown** — never the band alone. The count keeps the band honest: "Complete Record · 3 works" cannot be mistaken for a fully documented collection. (Band names and thresholds are tunable in config.)

---

## Part D — The gap breakdown (what drives the next engagement)

Alongside the score, compute a per-section fill map across the catalogued works:

```json
"gaps": {
  "identity_complete":   0.95,   // share of catalogued works with full identity
  "authority_linked":    0.80,   // share cross-referenced to ≥1 public authority
  "provenance_sourced":  0.30,
  "structured_export":   0.90
}
```

This is the actionable layer: it shows *where* completeness is being lost across the records — exactly the "here's what it takes to raise your score and your standard" proposal. (Condition and image fills appear here too, but only for engagements that include them.)

---

## Part E — Public vs private methodology

Reuse the visibility model (Instruction 9):

```json
"visibility": "private",          // private | restricted | public
"consent_to_publish_score": false // must be true (owner-granted) to publish a public score
```

- **Private** (default) — score and gap map shown **only in the owner's private workspace**. A confidential documentation-health KPI.
- **Restricted** — shared by direct link only.
- **Public** — published as a **credential** ("Ars Accordia Score 7,200 · 96 works · Substantial Record") and optionally listed in a public directory. Requires **both** `visibility: public` **and** `consent_to_publish_score: true`. (The optional relative-% view, if shown, additionally requires a known `total_extent`.)

**Hard rule: Ars Accordia never publishes a score for a collection it was not engaged to assess and that has not consented.** No unsolicited third-party "ratings."

**Methodology is always published** (this document's client-facing section), so any score is interpretable and consistent.

---

## Part F — Data model & computation

**`collections` registry** (`data/collections/COL-*.json`):
- `collection_id`, `name`, `owner` (Contributor ref)
- `scope` { definition, total_extent *(optional)*, status, source }
- `member_passports` [] (AP-IDs in scope)
- `visibility`, `consent_to_publish_score`
- `score` (computed block — below), `score_generated_at`

**The score is computed, never authored.** `build_collection_score.py` reads the member passports' Passport Scores (Instruction 13) and writes:

```json
"score": {
  "ars_accordia_score": 7200,
  "average_standard": 75,
  "works_documented": 96,
  "band": "Substantial Record",
  "relative_completeness": 0.51,   // present ONLY when scope.total_extent is known and solid
  "gaps": { … },
  "config_version": "weights-v3"
}
```

Recompute on any member passport change or scope change. Store `config_version` so a published score is reproducible.

---

## Client-facing methodology *(lift-out — publishable / show to a collector)*

> **How Ars Accordia scores a collection.** Each work we document earns a **Passport Score** from 0 to 100 — a measure of how complete its record is: its identity, its cross-references to public authority records (Getty, Wikidata, VIAF, national libraries), a provenance chain with a cited source for each step, and structured data for exchange. Your collection's **Ars Accordia Score** is the sum of those scores: an open figure that grows as more of the collection is documented and as records are made more complete. Beside it we report the **average standard** of your records — so the score is never merely a measure of size — and the **number of works documented**. We don't express this as a percentage of your whole collection, because the true total is rarely knowable, and a percentage built on a guess is a guess. And we measure only the record: we compare publicly available reference data, we do not pass judgement on it — so the score never grades how trustworthy a source is, nor a work's authenticity or value. The method is the same for every collection and is published in full.

---

## CLI

```
python3 scripts/build_collection_score.py COL-NORDIC-BANK-A
python3 scripts/build_collection_score.py --all
python3 scripts/build_collection_score.py COL-... --print        # human-readable score card
python3 scripts/build_collection_score.py COL-... --gaps         # gap breakdown only
python3 scripts/build_collection_score.py --check                # scores match member data; fail on drift
```

---

## Acceptance tests

1. `ars_accordia_score` equals the sum of member Passport Scores; adding a passport raises it, and improving an existing passport's completeness raises it.
2. `average_standard` equals the mean Passport Score and is independent of collection size (it behaves as a mean).
3. A collection with no `total_extent` is fully scored (Score, average standard, count) and shows **no** percentage; setting a solid `total_extent` additionally enables the relative-% view.
4. Cataloguing only the 10 easiest works yields a small Score and a work count of 10 — the band may be high, but the count and absolute Score reveal the limited volume.
5. The score has no corroboration term anywhere — it is the sum of completeness-only Passport Scores; no source is graded or ranked.
6. The Authority links contribution reflects **count of public cross-references**, not source type; the gap map's `authority_linked` is the share of works cross-referenced to ≥1 public authority.
7. The score is reproducible from member data (`--check` passes); editing a member passport and recomputing changes the Score; a stale score fails `--check`.
8. A `private` collection's score appears only in the owner workspace, never in any public output or export.
9. A `public` score is emitted only when `visibility=public` AND `consent_to_publish_score=true`; the optional relative-% additionally requires a known `total_extent`.
10. Σ of member Passport Scores equals `ars_accordia_score`, and their mean equals `average_standard`.

---

## What this component does NOT do

- It does **not** add a corroboration term, grade sources, or rank source types — the value is completeness alone, and cross-references are counted, not judged.
- It does **not** express the score as a percentage of the collection's total extent — that total is rarely knowable; the score is an open absolute figure read with the average standard and the work count.
- It does **not** show a misleading low figure for a barely-catalogued collection — the absolute Score reflects the documentation that exists, and the work count makes the volume explicit.
- It does **not** let volume alone inflate the score — a sparse passport contributes little, and the average standard exposes thin completeness.
- It does **not** publish any score without consent, and **never** scores a third-party collection it wasn't engaged to assess.
- It does **not** let a score be hand-set or overridden — computed from member passports, recomputed on change.
- It does **not** score authenticity or monetary value — they are structurally absent.
- It does **not** penalise a collection for a passport section outside the engagement's depth — uncommissioned sections are excluded, not counted as zero.
- It does **not** claim cross-collection ranking by absolute score as a quality judgement — the average standard is the size-independent comparator.
