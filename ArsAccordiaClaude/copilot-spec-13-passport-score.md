# Instruction 13 — The Passport Score & Its On-Page Derivation

*Hand to Copilot as a single component. It builds on Instruction 10 (validation levels and the conformance badge) and Instruction 11 (the collection score). The **passport score defined here is the atom of the whole scoring system**: the collection's Ars Accordia Score is the *sum* of its passport scores, and the collection's average standard is their *mean*. This spec defines how a single passport's score is computed **and** — its main purpose — exactly how that derivation is shown on every passport page. Where it conflicts with Copilot's instinct, the spec wins — ask before deviating.*

---

## Purpose

Give every Artwork Passport a single **Passport Score** (0–100), and **show on every passport page how that score was derived** — the working, not just the number. The page must let any viewer see precisely why the score is what it is: which sections are complete, how well the record is corroborated, and what is deliberately not graded. A score whose working is visible is a score that can be trusted; an unexplained number is a vanity figure.

---

## Where this sits (one picture)

```
Passport Score (this spec)  =  the value of one passport, 0–100
        │
        ├── summed over a collection  →  Ars Accordia Score   (Instruction 11, open-ended)
        └── averaged over a collection →  Average standard     (Instruction 11, 0–100)
```

The passport score is computed **once, per passport**, and reused everywhere. The collection figures are nothing more than the sum and the mean of these. There is one definition, here.

---

## The formula (one line)

```
Passport Score = 100 × ( 0.6 × Completeness  +  0.4 × Corroboration )      # 0–100
                        defaults: completeness 0.6, corroboration 0.4 (tunable in config)
```

- **Completeness** — how full the passport is, across its own sections (Part A).
- **Corroboration** — how well the record is verified against independent authorities (Part B).

A passport that is fully complete and fully corroborated scores 100; one that is empty or unverified scores near 0.

---

## Part A — Completeness (how full the passport is)

Completeness is the weighted fill of the passport's sections, **renormalised over the sections in scope** for that passport's depth:

```
Completeness = Σ ( section_weight × section_fill )  /  Σ ( section_weight in scope )     # 0–1
```

| Section | Weight | `section_fill` is… |
|---|---|---|
| Identity | 0.35 | share of the six descriptive fields present and to standard: title, creator, date, medium, dimensions, object type → (present / 6) |
| Authority links | 0.25 | 1 if ≥1 authority link (work/creator reconciled to ULAN / Wikidata / national library / etc.) is present, else 0. *Whether those links are corroborated is scored under Corroboration, not here — this section asks only "is there a reconciliation."* |
| Provenance, sourced | 0.25 | share of recorded ownership-chain steps that carry a cited source → (sourced steps / total steps); 0 if no chain |
| Structured / export | 0.15 | share of {JSON-LD present, EODEM export present} → 0, 0.5, or 1 |

**Depth sections** — in scope **only when the engagement commissioned them** (Instruction 11):

| Section | `section_fill` is… |
|---|---|
| Condition | 1 if an Ars-Accordia-produced condition report is present, else 0 |
| Image | 1 if an Ars-Accordia captured/verified image is present, else 0 |

**In scope vs not commissioned — the crucial distinction:**
- A section **in scope but empty** counts against the score (it is a real gap — e.g. provenance with no sourced steps contributes 0).
- A section **not commissioned** (condition/image the engagement did not include) is **excluded from the denominator**, not counted as a zero. The passport is never scored down for a section it was never meant to contain.

> This is the difference between *missing* and *out of scope*, and the page must show it as such (Part D).

---

## Part B — Corroboration (how well it is verified)

From the Instruction 10 validation levels, scored separately for the two layers and blended:

| Level | Value |
|---|---|
| FULLY_CORROBORATED | 1.00 |
| PARTIALLY_CORROBORATED | 0.50 |
| ENTITY_SUPPLIED_ONLY | 0.15 |
| PENDING | 0.00 |

```
Corroboration = 0.6 × value(L1_level)  +  0.4 × value(L2_level)      # 0–1
   L1 = object-identity validation level   (Instruction 10)
   L2 = provenance / relationships level    (Instruction 10)
```

L1 and L2 are always shown distinctly on the page — most records are strong on identity (L1) and lighter on provenance (L2), and that split is the honest insight.

---

## Part C — The score and its badge

- **Passport Score** = `100 × (0.6 × Completeness + 0.4 × Corroboration)`, rounded to an integer for display.
- **Conformance badge** (Instruction 10), shown beside the score: **green** (FULLY_CORROBORATED L1 + human-reviewed), **amber** (partial / automated-only), **grey** (ENTITY_SUPPLIED_ONLY). PENDING passports are never published (Instruction 10), so the panel appears on every *published* passport.
- The panel shows on **every** published passport, **including low-scoring ones** — showing honestly why a record scores 60, and what would raise it, is more credible than hiding it, and doubles as that work's improvement list.

---

## Part D — The on-page derivation (the requirement)

Every passport page carries a **"How this score is derived"** section, rendered from the passport's computed `score` block (Part F) — never recomputed in the template, never hand-written.

It contains, in order:

**1. The headline** — the Passport Score (0–100) and the conformance badge.

**2. Completeness breakdown** (label it: *weighted 60% of the score*) — one row per **in-scope** section:

| Section | Weight | What's present | Contribution |
|---|---|---|---|
| Identity | 0.35 | "6 of 6 fields" | 0.35 |
| Authority links | 0.25 | "2 links — ULAN, Wikidata" | 0.25 |
| Provenance (sourced) | 0.25 | "3 of 4 steps sourced" | 0.19 |
| Structured / export | 0.15 | "JSON-LD + EODEM" | 0.15 |
| **Completeness** | | | **0.94** |

- Show **filled and unfilled in-scope sections alike** (an empty in-scope section shows "—" and a 0.00 contribution, so the gap is visible).
- Show **not-commissioned** sections separately and explicitly as *"not commissioned — excluded"*, never as a zero row that appears to penalise.

**3. Corroboration breakdown** (label it: *weighted 40% of the score*):

| Layer | Level | Value |
|---|---|---|
| Identity (L1) | Fully corroborated | 1.00 |
| Provenance (L2) | Partially corroborated | 0.50 |
| **Corroboration** (0.6 × L1 + 0.4 × L2) | | **0.80** |

**4. The combination — shown explicitly:**

> Passport Score = 100 × (0.6 × **0.94** + 0.4 × **0.80**) = 100 × (0.564 + 0.320) = **88**

**5. The "not scored" line** — a constant, on every page:

> *Not scored: authenticity and monetary value. A passport records that a work is correctly identified and linked, not that an attribution is genuine or what it is worth — those are a connoisseur's and a valuer's judgement.*

**6. A link to the published method** (Part E): *"How we score a passport →"*.

The breakdown must be legible to a non-specialist: contributions, not just weights, so the arithmetic visibly adds up to the number shown.

---

## Part E — The method (lift-out — shown on / linked from every passport page)

> **How Ars Accordia scores a passport.** Each Artwork Passport earns a score from 0 to 100 built from two things. The first is **how complete the record is** — its identity (title, maker, date, medium, dimensions, type), its links to independent authority records, a provenance chain with a cited source for each step, and structured data for exchange. The second is **how well it is corroborated** — how far its identity and its provenance stand up against independent authorities, graded on a four-level scale from source-supplied to fully corroborated. We weight completeness 60% and corroboration 40%, and we show the full breakdown on every passport so the number is never a black box. We do **not** grade a work's authenticity or its monetary value — those belong to connoisseurs and valuers and are not part of the score. The method is the same for every passport and is published in full: a score you can trust is one whose working you can see.

---

## Part F — Data model & computation

The score is **computed, never authored**. `build_passport_score.py` reads the passport's section data (Part A) and its Instruction 10 validation levels (Part B), and writes a `score` block onto the passport record:

```json
"score": {
  "passport_score": 88,
  "conformance": "green",
  "completeness": {
    "value": 0.94,
    "sections": [
      { "section": "identity",          "weight": 0.35, "fill": 1.00, "present": "6 of 6 fields",        "contribution": 0.35, "in_scope": true },
      { "section": "authority_links",   "weight": 0.25, "fill": 1.00, "present": "2 links — ULAN, Wikidata", "contribution": 0.25, "in_scope": true },
      { "section": "provenance",        "weight": 0.25, "fill": 0.75, "present": "3 of 4 steps sourced",  "contribution": 0.19, "in_scope": true },
      { "section": "structured_export", "weight": 0.15, "fill": 1.00, "present": "JSON-LD + EODEM",       "contribution": 0.15, "in_scope": true },
      { "section": "condition",         "weight": 0.00, "fill": null, "present": "not commissioned",      "contribution": 0.00, "in_scope": false },
      { "section": "image",             "weight": 0.00, "fill": null, "present": "not commissioned",      "contribution": 0.00, "in_scope": false }
    ]
  },
  "corroboration": {
    "value": 0.80,
    "L1": { "level": "FULLY_CORROBORATED",     "value": 1.00 },
    "L2": { "level": "PARTIALLY_CORROBORATED", "value": 0.50 },
    "weights": { "L1": 0.6, "L2": 0.4 }
  },
  "weights": { "completeness": 0.6, "corroboration": 0.4 },
  "excluded": [ "authenticity", "monetary_value" ],
  "config_version": "weights-v2"
}
```

- `contribution` = `weight × fill` (renormalised); the in-scope contributions sum to `completeness.value`. The page renders straight from this — the arithmetic shown to the viewer is the arithmetic stored.
- Recompute on any change to the passport's fields or validation levels. Store `config_version` so a displayed derivation is reproducible under the weights in force when it was issued.
- **Config weights here are the same constants as Instruction 11** (completeness 0.6 / corroboration 0.4; section weights 0.35 / 0.25 / 0.25 / 0.15; L1 0.6 / L2 0.4; level values 1.00 / 0.50 / 0.15 / 0.00). One config, both specs — never two copies that can drift.

---

## CLI

```
python3 scripts/build_passport_score.py AP-2026-000118
python3 scripts/build_passport_score.py --all
python3 scripts/build_passport_score.py AP-... --print     # human-readable derivation card
python3 scripts/build_passport_score.py --check            # scores match passport data; fail on drift
```

`--check` must also confirm that **Σ passport_score over a collection equals that collection's Ars Accordia Score** (Instruction 11) — the atom and the aggregate cannot disagree.

---

## Acceptance tests

1. A complete, fully-corroborated passport (all in-scope sections filled, L1 and L2 FULLY) scores 100; an empty PENDING passport scores 0.
2. The contributions shown on the page sum to `completeness.value`, and `100 × (0.6 × completeness + 0.4 × corroboration)` equals the displayed `passport_score` exactly.
3. A passport complete on identity but `ENTITY_SUPPLIED_ONLY` on both layers shows high completeness, low corroboration, and a middling score — the two components visibly separate.
4. A section **in scope but empty** appears as a 0.00-contribution row (a visible gap); a **not-commissioned** section appears as "not commissioned — excluded" and does **not** lower the score.
5. Removing condition from scope (not commissioned) raises the score versus counting it as a zero — renormalisation works, and the page reflects the change.
6. L1 and L2 levels are shown distinctly with their numeric values, and the blend `0.6×L1 + 0.4×L2` matches `corroboration.value`.
7. Authenticity and monetary value never appear as scored rows; the "not scored" line is present on every passport page.
8. The page renders entirely from the stored `score` block — no recomputation in the template; editing a field and recomputing changes both the number and the breakdown; a stale score fails `--check`.
9. The panel appears on every published passport, including amber and grey ones; a PENDING passport is not published and shows no panel.
10. Σ of passport scores in a collection equals the collection's Ars Accordia Score, and their mean equals the average standard.

---

## What this component does NOT do

- It does **not** show the score without its derivation — the breakdown is mandatory on every passport page, not optional.
- It does **not** hand-write or hard-code any figure in the template — the page is rendered from the computed `score` block only.
- It does **not** grade authenticity or monetary value — they are structurally absent and named as not scored.
- It does **not** count a not-commissioned section as a zero — out-of-scope sections are excluded from the denominator and shown as excluded, not as gaps.
- It does **not** keep its own copy of the weights — it shares Instruction 11's config, so the passport score and the collection score can never diverge.
- It does **not** hide a low score — every published passport shows its working, and the gaps are the improvement list.
