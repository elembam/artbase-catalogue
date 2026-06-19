# Instruction 11 — Collection Score (the Ars Accordia Score)

*Hand to Copilot as a single component. It builds directly on the validation levels (Instruction 10) and the visibility/privacy model (Instruction 9): the score is a roll-up of per-work validation and passport data — never hand-set. The "Client-facing methodology" section near the end is written to be lifted out and published or shown to a collector. Where it conflicts with Copilot's instinct, the spec wins — ask before deviating.*

---

## Purpose

Give a **whole collection** a single ownable figure — the **Ars Accordia Score** — aggregated over the passports it contains, read alongside an **average standard** and a **work count** that together say how much documentation exists and how good it is, plus a gap map that shows what to improve. Private collections are scored privately; public collections are scored publicly *with consent*. The score is the commercial engine: it aligns the metric with the unit of sale (the collection), grows with every work catalogued, and the gap map writes the next proposal.

---

## Why the score is absolute, not a percentage

A percentage needs a denominator — the collection's *total extent* — and for most collections that number is genuinely unknowable: you cannot reliably enumerate every work a museum holds, or every work a living collector owns. A score resting on a guessed total is itself a guess. So the Ars Accordia Score is **absolute and open-ended**: each passport contributes its own value, and the collection's score is their **sum**. There is no denominator to establish and none to game. A collection Ars Accordia has barely catalogued simply has a small score — reflecting the little documentation that exists — never a misleadingly low "percentage" implying the collection itself is poorly kept.

To stop the absolute score being a pure size contest, it is always read alongside the **average standard** — the mean passport value — which is *size-independent*: a small, perfectly documented collection and a large one both read near the top. **The absolute score says how much; the average standard says how good; the count says how many.**

---

## The model

```
Per-passport value   v_i = 100 × ( w_g · Completeness_i  +  w_r · Corroboration_i )    # 0–100 per passport
                           defaults  w_g = 0.6,  w_r = 0.4

Ars Accordia Score   = Σ v_i                 # open-ended — the headline figure
Average standard     = mean(v_i)             # 0–100 — size-independent quality, carries the band
Works documented     = count(passports)      # the volume

# OPTIONAL, shown only where the total extent is genuinely known (e.g. a fixed corporate inventory):
Relative completeness = Σ v_i / (N × 100)    # 0–1 — never forced, never guessed
```

The three headline outputs — **Score, average standard, works documented** — are always displayed **together**; the absolute number alone is not interpretable without the standard and the count beside it. All weights are **defaults, tunable in config**, not hard constants.

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
- **`total_extent` (N) is optional.** The Ars Accordia Score, the average standard, and the work count are all computed **without** it. N feeds **only** the optional relative-completeness view, which is shown only when `status` is `inventory_confirmed` or `owner_declared` — never on a guess.
- **No N is a normal, fully-scored state** — not an error and not "Scope Not Established." The collection shows its absolute score, standard, and count, simply without a percentage.

---

## Part B — Per-passport quality (the two components)

Each passport's value comes from two components, both computed **per passport** and also **averaged** across the collection for display.

### B1. Completeness — measured on the Passport, and only the Passport

**The anchor: the score measures the Ars Accordia Passport.** The passport is what we promise and produce, so it is both the unit of work and the unit of measurement. Completeness is *how complete the passport is* — across the passport's own defined sections — and **nothing outside the passport enters the score.** Valuation, authenticity certificates, insurance schedules, facility reports, market data: none of these are passport content, so none are scored. We don't have to reason case-by-case about "what we can verify" — the passport's schema already draws the line, because we never put into a passport anything we can't stand behind.

**The passport's scored sections:**

| Passport section | Weight | Complete when… |
|---|---|---|
| Identity | 0.35 | title, creator, date, medium, dimensions, object type recorded to standard, with creator/work reconciled to authorities |
| Authority links | 0.25 | ≥1 corroborated authority link |
| Provenance, sourced | 0.25 | ownership chain recorded **with a cited source for each step** |
| Structured / export | 0.15 | JSON-LD + EODEM export record present |

These four are the core passport and are always scored. Two further sections are **part of the passport only at greater depth**, and enter the score **only when the engagement produces them**:

| Depth section | Counts only when… |
|---|---|
| Condition | Ars Accordia (or its qualified conservator/registrar) produced the condition report as part of the passport — not a note merely supplied |
| Image | Ars Accordia captured or verified the image held in the passport — not an owner snapshot on file |

When the engagement's passport depth includes condition or imaging, those sections enter the weighting (weights renormalise to sum to 1.0). When it does not, they are **not part of the denominator** — a passport is never scored down for a section it was not commissioned to contain.

**What this deliberately leaves out:** the passport carries no authenticity ruling and no monetary value — those are a connoisseur's and a valuer's province, not ours — so they are *structurally* absent from the score. We grade that a work is correctly *identified and linked*, never that the attribution is genuine or what it is worth. A forgery can carry a flawless passport; the passport, and so the score, measures documentation, not authenticity or value.

```
# Completeness is computed over the passport sections IN SCOPE for that engagement's depth,
# with weights renormalised to sum to 1.0 across the sections actually in the passport.
work_completeness (g_i) = Σ ( section_weight × section_fill_fraction )   # passport sections in scope
```

### B2. Corroboration (from Instruction 10 validation levels)

Map each work's validation level to a numeric value:

| Level | Value |
|---|---|
| FULLY_CORROBORATED | 1.00 |
| PARTIALLY_CORROBORATED | 0.50 |
| ENTITY_SUPPLIED_ONLY | 0.15 |
| PENDING | 0.00 |

Per work, blend Level 1 and Level 2 (defaults: L1 0.6, L2 0.4):

```
work_corroboration (r_i) = (0.6 × value(L1_level)) + (0.4 × value(L2_level))
```

Report **L1 and L2 corroboration separately** at collection level too (as means) — most collections are strong on identity (L1) and weak on provenance (L2), and showing that split honestly is the key insight for a collector.

### B3. Per-passport value and collection aggregation

```
v_i = 100 × (0.6 × g_i + 0.4 × r_i)        # each passport, 0–100
Ars Accordia Score = Σ v_i                  # open-ended
Average standard   = mean(v_i)              # 0–100 — carries the band
Works documented   = count(passports)
Relative completeness = Σ v_i / (N × 100)   # OPTIONAL; only when total_extent is known and solid
```

A perfect passport — complete and fully corroborated — is worth 100; a half-complete, source-only passport is worth little. The score rises only by adding passports or improving them, and because a weak passport contributes little, **volume alone cannot inflate it** — the average standard would expose it.

---

## Part C — Bands (on the average standard, not the collection)

The band describes the **average standard of the records that exist** — *not* the collection's completeness, which the score deliberately does not claim to measure. The absolute Ars Accordia Score is **unbanded** (a figure read in context of the standard and the count); the band attaches to the **average standard** (0–100):

| Band | Average standard | Meaning — the standard of the records |
|---|---|---|
| **Fully Corroborated** | ≥ 85 | Records near-complete and independently corroborated |
| **Substantially Corroborated** | 65–84 | Most records full and well-corroborated |
| **Partially Corroborated** | 40–64 | Solid on identity, lighter on corroboration / provenance |
| **Source-Supplied** | 15–39 | Recorded, but largely uncorroborated |
| **Minimal Record** | < 15 | Bare entries |

Always display the **Ars Accordia Score + the average-standard band + the work count + the Completeness/Corroboration split** — never the band alone. The count is what keeps the band honest: "Fully Corroborated · 3 works" cannot be mistaken for a fully documented collection. (Band names and thresholds are tunable in config.)

---

## Part D — The gap breakdown (what drives the next engagement)

Alongside the score, compute a per-dimension fill map across the catalogued works:

```json
"gaps": {
  "identity_complete":      0.95,   // share of catalogued works with full identity
  "authority_linked":       0.80,
  "provenance_sourced":     0.30,
  "structured_export":      0.90,
  "fully_corroborated_L1":  0.45,
  "fully_corroborated_L2":  0.10
}
```

This is the actionable layer: it shows *where* value is being lost across the records, which is exactly the "here's what it takes to raise your score and your standard" proposal. (Condition and image fills appear here too, but only for engagements that include them.)

---

## Part E — Public vs private methodology

Reuse the visibility model (Instruction 9). Each collection has:

```json
"visibility": "private",          // private | restricted | public
"consent_to_publish_score": false // must be true (owner-granted) to publish a public score
```

- **Private** (default) — score and gap map computed and shown **only in the owner's private workspace**. A confidential documentation-health KPI for insurance and succession readiness.
- **Restricted** — shared by direct link only.
- **Public** — score published as a **credential** ("Ars Accordia Score 7,240 · 96 works · Substantially Corroborated") and optionally listed in a public directory. Requires **both** `visibility: public` **and** `consent_to_publish_score: true`. (The optional relative-% view, if shown at all, additionally requires a known `total_extent` — but the Score, average standard, and count do not.)

**Hard rule: Ars Accordia never publishes a score for a collection it was not engaged to assess and that has not consented.** No unsolicited third-party "ratings" — that standing has to be earned, and unilateral scoring of institutions is out of scope here.

**Methodology is always published** (this document's client-facing section), so any score — public or private — is interpretable and consistent. A score without a transparent method is just a vanity number.

---

## Part F — Data model & computation

**`collections` registry** (`data/collections/COL-*.json`), fields:
- `collection_id`, `name`, `owner` (Contributor ref)
- `scope` { definition, total_extent *(optional)*, status, source }
- `member_passports` [] (AP-IDs in scope)
- `visibility`, `consent_to_publish_score`
- `score` (computed block — see below), `score_generated_at`

**The score is computed, never authored** — like the source ledger and validation level. `build_collection_score.py` reads the member passports (their passport-section population + Instruction 10 validation levels), and writes:

```json
"score": {
  "ars_accordia_score": 7240,
  "average_standard": 75,
  "works_documented": 96,
  "band": "Substantially Corroborated",
  "completeness": 0.74,
  "corroboration": { "blended": 0.60, "L1": 0.78, "L2": 0.34 },
  "relative_completeness": 0.51,   // present ONLY when scope.total_extent is known and solid
  "gaps": { … },
  "config_version": "weights-v2"
}
```

Recompute on any member passport change or scope change. Store `config_version` so a published score is reproducible under the weights in force when it was issued.

---

## Client-facing methodology *(lift-out — publishable / show to a collector)*

> **How Ars Accordia scores a collection.** We measure the **Ars Accordia Passport** — the record we produce for each work — and nothing outside it. Each passport earns a value from how *complete* it is (identity, authority links, sourced provenance, structured data, and, where commissioned, condition and image) and how well it is *corroborated* against independent authorities. Your collection's **Ars Accordia Score** is the sum of those values: an open figure that grows as more of your collection is documented and as records are strengthened. Beside it we report the **average standard** of your records — so the score is never merely a measure of size — and the **number of works documented**. We don't express this as a percentage of your whole collection, because the true total is rarely knowable with confidence, and a percentage built on a guess is a guess; an honest open figure, with the standard of the records beside it, tells you more. The score measures *documentation* — it does not certify a work's authenticity or its monetary value, which belong to connoisseurs and valuers and never enter a passport or the score. The method is the same for every collection and is published in full — a score you can trust is a score you can see the working of.

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

1. A collection's `ars_accordia_score` equals the sum of its passport values; adding a new passport raises it, and improving an existing passport raises it.
2. `average_standard` equals the mean passport value and is independent of collection size — it behaves as a mean (adding an average-quality passport barely moves a large collection's average, but moves a small one's).
3. A collection with no `total_extent` is fully scored (Score, average standard, count) and shows **no** percentage; setting a solid `total_extent` additionally enables the relative-% view.
4. Cataloguing only the 10 easiest works yields a small Score and a work count of 10 — the band may be high, but the count and absolute Score reveal the limited volume; nothing implies the collection is complete.
5. A passport that is complete but `ENTITY_SUPPLIED_ONLY` contributes high completeness and low corroboration to its value, and the two components show separately.
6. L1 and L2 corroboration are reported distinctly; a collection strong on identity and empty on provenance shows high L1, low L2.
7. The score is reproducible from member data (`--check` passes); editing a member passport and recomputing changes the Score; a stale score fails `--check`.
8. A `private` collection's score appears only in the owner workspace, never in any public output or export.
9. A `public` score is emitted only when `visibility=public` AND `consent_to_publish_score=true`; the optional relative-% additionally requires a known `total_extent`.
10. Condition and image do not affect a passport's value unless the engagement marks them Ars-Accordia-produced; an owner-supplied condition note left ungraded does not lower completeness.
11. Authenticity and monetary value are never inputs; a record with no valuation and no authentication certificate is not penalised.
12. The band attaches to the `average_standard`, not the absolute Score; a small collection of flawless records reads "Fully Corroborated" with a low absolute Score and a low work count.

---

## What this component does NOT do

- It does **not** express the score as a percentage of the collection's total extent — that total is rarely knowable, and the score is an open absolute figure, read with the average standard and the work count.
- It does **not** show a misleading low figure for a barely-catalogued collection — the absolute Score reflects the documentation that exists, and the work count makes the volume explicit.
- It does **not** let volume alone inflate the score — a low-quality passport contributes little, and the average standard exposes thin quality.
- It does **not** publish any score without the owner's consent, and **never** scores a third-party collection it wasn't engaged to assess.
- It does **not** let a score be hand-set or overridden — it is computed from member passports and recomputed on change.
- It does **not** fold Level 2 (provenance) corroboration into the headline silently — L1 and L2 are always shown separately.
- It does **not** score anything outside the Ars Accordia Passport — authenticity/attribution, monetary value, and any non-passport material are excluded by construction.
- It does **not** penalise a collection for a passport section outside the engagement's depth — uncommissioned sections are excluded, not counted as zero.
- It does **not** claim cross-collection ranking by absolute score as a quality judgement — the average standard is the size-independent comparator; the absolute score reflects volume.
