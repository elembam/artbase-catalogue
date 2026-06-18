# Instruction 11 — Collection Completeness Score

*Hand to Copilot as a single component. It builds directly on the validation levels (Instruction 10) and the visibility/privacy model (Instruction 9): the score is a roll-up of per-work validation and field data — never hand-set. The "Client-facing methodology" section near the end is written to be lifted out and published or shown to a collector. Where it conflicts with Copilot's instinct, the spec wins — ask before deviating.*

---

## Purpose

Score a **whole collection** for documentation completeness, aggregated over the works it contains, so a collector has a single ownable KPI ("your collection is *Partially Documented* — 38%") plus a gap map that shows what to improve. Private collections are scored privately; public collections are scored publicly *with consent*. The score is the commercial engine: it aligns the metric with the unit of sale (the collection), and the gap map writes the next proposal.

---

## The model in one line

```
Documentation Score  =  Coverage  ×  Quality
                        where Quality = (w_g · Completeness) + (w_r · Corroboration)
```

Three dimensions are computed and **displayed separately** (Coverage, Completeness, Corroboration), and combined into one headline Score. Coverage is a *multiplier*, not an average term — uncatalogued works cannot be hidden. All weights below are **defaults, tunable in config**, not hard constants.

---

## Part A — Scope and the denominator rule (the integrity core)

A score is only meaningful against a known total. Every collection has a **defined scope**:

```json
"scope": {
  "definition": "All works owned by the entity as of 2026-06-01",  // human-readable inclusion rule
  "total_extent": 142,                 // N — the denominator
  "status": "inventory_confirmed",     // inventory_confirmed | owner_declared | estimated
  "source": "On-site inventory, 2026-05"
}
```

- **Coverage is always measured against `total_extent` (N)** — never against the catalogued subset. This is the anti-gaming rule: you cannot raise the score by excluding uncatalogued works from the denominator.
- **No `total_extent` → no score.** The collection's status is `scope_undefined` and it shows "Scope not yet established," not a number. Establishing scope is therefore **engagement step 1** — and it's a real deliverable (a definitive inventory), not a chore.
- **Large collections are scoped as a defined subset** with its own N (e.g. "publicly displayed works," "post-1990 acquisitions"), so a 5,000-work museum isn't forced into one diluted number. The `definition` field records what the N covers.

---

## Part B — The three dimensions (precise computation)

### B1. Coverage

```
Coverage (C) = (works in scope that have a passport) / total_extent
```
Range 0–1.

### B2. Completeness (per catalogued work, then averaged)

Per-work completeness is the weighted fill-fraction of the passport's sections. Default section weights (sum to 1.0, tunable):

| Section | Weight | Filled when… |
|---|---|---|
| Identity (L1) | 0.30 | title, creator, date, medium, dimensions, object type present |
| Provenance (L2) | 0.25 | ownership chain recorded |
| Authority links | 0.15 | ≥1 confirmed authority link |
| Condition | 0.15 | condition statement present |
| Image | 0.10 | image present |
| Structured/export | 0.05 | JSON-LD + export record present |

```
work_completeness (g_i) = Σ ( section_weight × section_fill_fraction )
Completeness (Ḡ) = mean(g_i) over catalogued works
```

### B3. Corroboration (from Instruction 10 validation levels)

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
Corroboration (R̄) = mean(r_i) over catalogued works
```

Report **L1 and L2 corroboration separately** at collection level too — most collections are strong on identity (L1) and weak on provenance (L2), and showing that split honestly is the key insight for a collector.

### B4. The composite

```
Quality (Q) = (w_g × Ḡ) + (w_r × R̄)          # defaults w_g = 0.6, w_r = 0.4
Documentation Score (S) = C × Q                # range 0–1; ×100 for display
```

---

## Part C — Grade bands

Map the headline Score (0–100) to a memorable, credential-worthy band (thresholds tunable):

| Band | Score | Meaning |
|---|---|---|
| **Fully Documented** | ≥ 85 | Near-complete, well-corroborated, high coverage |
| **Substantially Documented** | 65–84 | Most works catalogued to good standard |
| **Partially Documented** | 35–64 | Meaningful coverage; clear gaps remain |
| **Catalogued** | 15–34 | Inventory plus early records |
| **Inventory Only** | < 15 | Scope defined; little catalogued yet |
| **Scope Not Established** | — | No `total_extent`; not scorable |

Display the **band + the percentage + the three sub-scores**, never the band alone — the number and the decomposition are what make it actionable.

---

## Part D — The gap breakdown (what drives the next engagement)

Alongside the score, compute a per-dimension coverage map across the catalogued works:

```json
"gaps": {
  "provenance_documented":  0.30,   // 30% of catalogued works have provenance
  "condition_documented":   0.60,
  "authority_linked":       0.80,
  "image_present":          0.55,
  "fully_corroborated_L1":  0.45,
  "fully_corroborated_L2":  0.10
}
```

This is the actionable layer: it shows *where* the score is lost, which is exactly the "here's what it takes to reach the next band" proposal.

---

## Part E — Public vs private methodology

Reuse the visibility model (Instruction 9). Each collection has:

```json
"visibility": "private",          // private | restricted | public
"consent_to_publish_score": false // must be true (owner-granted) to publish a public score
```

- **Private** (default) — score and gap map computed and shown **only in the owner's private workspace**. A confidential documentation-health KPI for insurance and succession readiness.
- **Restricted** — shared by direct link only.
- **Public** — score published as a **credential/badge** ("Ars Accordia Documented — Substantially, 71%") and optionally listed in a public directory. Requires **both** `visibility: public` **and** `consent_to_publish_score: true`, **and** `scope.status` ≥ `owner_declared` (a public score must not rest on a guessed denominator).

**Hard rule: Ars Accordia never publishes a score for a collection it was not engaged to assess and that has not consented.** No unsolicited third-party "ratings" — that standing has to be earned, and unilateral scoring of institutions is out of scope here.

**Methodology is always published** (this document's client-facing section), so any score — public or private — is interpretable and consistent. A score without a transparent method is just a vanity number.

---

## Part F — Data model & computation

**`collections` registry** (`data/collections/COL-*.json`), fields:
- `collection_id`, `name`, `owner` (Contributor ref)
- `scope` { definition, total_extent, status, source }
- `member_passports` [] (AP-IDs in scope)
- `visibility`, `consent_to_publish_score`
- `score` (computed block — see below), `score_generated_at`

**The score is computed, never authored** — like the source ledger and validation level. `build_collection_score.py` reads the member passports (their field population + Instruction 10 validation levels) and the scope, and writes:

```json
"score": {
  "documentation_score": 38,
  "band": "Partially Documented",
  "coverage": 0.60,
  "completeness": 0.62,
  "corroboration": { "blended": 0.34, "L1": 0.48, "L2": 0.12 },
  "gaps": { … },
  "config_version": "weights-v1"
}
```

Recompute on any member passport change or scope change. Store the `config_version` so a published score is reproducible under the weights in force when it was issued.

---

## Client-facing methodology *(lift-out — publishable / show to a collector)*

> **How Ars Accordia scores a collection.** Every collection is measured against its **full defined extent** — the total number of works in scope, agreed at the outset — not just the works we've catalogued, so the score can't be inflated by leaving works out. The score combines three things: **Coverage** (how much of the collection is catalogued), **Completeness** (how full each record is — identity, provenance, condition, authority links, image), and **Corroboration** (how well each record is verified against independent authorities, graded on our four-level standard). These produce a single **Documentation Score** and a band from *Inventory Only* to *Fully Documented*, plus a breakdown showing exactly where the gaps are. Private collections are scored confidentially for the owner; public collections are scored publicly only with the owner's consent. The method is the same for every collection and is published in full — a score you can trust is a score you can see the working of.

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

1. A collection with `total_extent` 100 and 60 catalogued works reports `coverage = 0.60`; adding 10 uncatalogued works to scope (extent 110) lowers coverage without any passport change.
2. A collection with no `total_extent` returns band `Scope Not Established` and no numeric score.
3. Cataloguing only the 10 easiest of 100 works cannot produce a "Fully Documented" band — coverage caps the score.
4. A work that is complete (all fields) but `ENTITY_SUPPLIED_ONLY` contributes high completeness and low corroboration, and the two show separately.
5. L1 and L2 corroboration are reported distinctly; a collection strong on identity and empty on provenance shows high L1, low L2.
6. The score is reproducible from member data (`--check` passes); editing a member passport and recomputing changes the score; a stale score fails `--check`.
7. A `private` collection's score appears only in the owner workspace, never in any public output or export.
8. A `public` score is emitted only when `visibility=public` AND `consent_to_publish_score=true` AND `scope.status` ≥ `owner_declared`.
9. Changing config weights changes scores only on recompute and bumps `config_version`.

---

## What this component does NOT do

- It does **not** score against the catalogued subset — always against the full defined extent `N`. No scope, no score.
- It does **not** publish any score without the owner's consent, and **never** scores a third-party collection it wasn't engaged to assess.
- It does **not** let a score be hand-set or overridden — it is computed from member passports and recomputed on change.
- It does **not** fold Level 2 (provenance) corroboration into the headline silently — L1 and L2 are always shown separately.
- It does **not** treat completeness as quality on its own — a complete but uncorroborated record scores low on corroboration, and the headline reflects both.
- It does **not** claim cross-collection comparability as a ranking; the score is primarily a collection's own measure and progress over time.
