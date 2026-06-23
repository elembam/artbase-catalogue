# Instruction 13 — The Passport Score & Its On-Page Derivation

*Hand to Copilot as a single component. It builds on Instruction 9 (visibility) and Instruction 10 (the publication gate and the status badge). The **passport score defined here is the atom of the whole scoring system**: the collection's Ars Accordia Score is the *sum* of its passport scores, and the collection's average standard is their *mean* (Instruction 11). This spec defines how a single passport's score is computed **and** — its main purpose — exactly how that derivation is shown on every passport page. Where it conflicts with Copilot's instinct, the spec wins — ask before deviating.*

---

## The governing principle (read first)

**Ars Accordia compares publicly available reference data; it does not judge it.** The score measures one thing only — **how complete the passport record is** — and completeness is a property *of the passport*, read directly off its fields. Crucially, this includes **whether the work is cross-referenced to public authority records** (a Getty ULAN/AAT ID, a Wikidata Q, a VIAF number, a national-library identifier). The authority that those references carry was created and is maintained by Getty, Wikidata, and the rest — *not by us*. By linking them, the passport inherits that authority as a **counted fact**. We never grade how trustworthy a source is, never rank one source type above another, and never issue a verdict on how "corroborated" a record is. Those would be opinions, and **opinions are outside Ars Accordia's competence.** The presence of a public cross-reference is the signal; assembling and presenting it is the work.

---

## Where this sits (one picture)

```
Passport Score (this spec)   =  the value of one passport, 0–100  =  100 × Completeness
        │
        ├── summed over a collection  →  Ars Accordia Score   (Instruction 11, open-ended)
        └── averaged over a collection →  Average standard     (Instruction 11, 0–100)
```

The passport score is computed once, per passport, and reused everywhere. The collection figures are nothing more than the sum and the mean of these.

---

## The formula (one line)

```
Passport Score = 100 × Completeness        # 0–100
```

There is no second term. Completeness already rewards exactly the rigour that matters — being cross-referenced to public authorities and carrying sourced provenance — because those are sections of the passport (below). We do not layer a separate "corroboration" judgement on top: that was both off-passport and an opinion.

---

## Part A — Completeness (the whole score)

Completeness is the weighted fill of the passport's sections, **renormalised over the sections in scope** for that passport's depth:

```
Completeness = Σ ( section_weight × section_fill )  /  Σ ( section_weight in scope )     # 0–1
```

| Section | Weight | `section_fill` is… |
|---|---|---|
| Identity | 0.35 | share of the six descriptive fields present and to standard: title, creator, date, medium, dimensions, object type → (present / 6) |
| Authority links | 0.25 | the work/creator **cross-referenced to public authority records** — Getty ULAN/AAT, Wikidata, VIAF, national libraries. `fill` = a function of cross-references present (e.g. ≥1 → counts; more independent authorities → fuller). **Counted by presence, never graded by trustworthiness.** |
| Provenance, sourced | 0.25 | share of recorded ownership-chain steps that carry a cited source → (sourced steps / total steps); 0 if no chain. *Counts whether a source is cited, not how good the source is.* |
| Structured / export | 0.15 | share of {JSON-LD present, EODEM export present} → 0, 0.5, or 1 |

**Depth sections** — in scope **only when the engagement commissioned them** (Instruction 11):

| Section | `section_fill` is… |
|---|---|
| Condition | 1 if an Ars-Accordia-produced condition report is present, else 0 |
| Image | 1 if an Ars-Accordia captured/verified image is present, else 0 |

**In scope vs not commissioned — the crucial distinction:**
- A section **in scope but empty** counts against the score (a real gap — e.g. no authority cross-reference yet contributes 0).
- A section **not commissioned** (condition/image the engagement did not include) is **excluded from the denominator**, not counted as a zero.

**On the Authority links section — the only subtlety, kept clean:** `fill` rewards *how many independent public authorities the work is cross-referenced to* (one is good; several independent ones is fuller), because more public cross-references is a richer record. This is still a **count of public references present**, not a judgement of their quality. A reasonable default: `fill = min(1, cross_references / 2)` (two independent public authorities = full), tunable in config. No source is ever scored as "better" than another — only present or absent.

---

## Part B — The score and its status badge

- **Passport Score** = `100 × Completeness`, rounded to an integer for display.
- **Status badge** (from Instruction 10, **reframed as objective status — not a corroboration verdict**), shown beside the score:
  - **green** — cross-referenced to independent public authorities **and** human-reviewed;
  - **amber** — linked but automated-only / not yet human-reviewed;
  - **grey** — no public-authority cross-reference yet.
  The badge reports *facts about the record's cross-reference status*, not a judgement about how believable it is. (See "Note on Instruction 10" below.)
- PENDING (not yet processed) passports are not published (Instruction 10), so the panel appears on every *published* passport, **including low-scoring ones** — showing honestly why a record scores 60, and what would raise it, is more credible than hiding it, and doubles as that work's to-do list.

---

## Part C — The on-page derivation (the requirement)

Every passport page carries a **"How this score is derived"** section, rendered from the passport's computed `score` block (Part E) — never recomputed in the template, never hand-written. It contains, in order:

**1. The headline** — the Passport Score (0–100) and the status badge.

**2. The completeness breakdown** — one row per **in-scope** section:

| Section | Weight | What's present | Contribution |
|---|---|---|---|
| Identity | 0.35 | "6 of 6 fields" | 0.35 |
| Authority links | 0.25 | "2 public authorities — Getty ULAN, Wikidata" | 0.25 |
| Provenance (sourced) | 0.25 | "3 of 4 steps sourced" | 0.19 |
| Structured / export | 0.15 | "JSON-LD + EODEM" | 0.15 |
| **Completeness** | | | **0.94** |

- Show **filled and unfilled in-scope sections alike** (an empty in-scope section shows "—" and a 0.00 contribution, so the gap is visible).
- Show **not-commissioned** sections separately and explicitly as *"not commissioned — excluded"*, never as a zero that appears to penalise.

**3. The combination — shown explicitly:**

> Passport Score = 100 × **0.94** = **94**

**4. The "what is not scored" line** — a constant, on every page:

> *We measure how complete and cross-referenced the record is. We do not grade how trustworthy a source is, nor a work's authenticity or its value — Ars Accordia compares publicly available reference data, it does not pass judgement on it. Authenticity is a connoisseur's question and value a valuer's; neither is part of this score.*

**5. A link to the published method** (Part D): *"How we score a passport →"*.

The breakdown must be legible to a non-specialist: contributions, not just weights, so the arithmetic visibly adds up to the number shown.

---

## Part D — The method (lift-out — shown on / linked from every passport page)

> **How Ars Accordia scores a passport.** Each Artwork Passport earns a score from 0 to 100 that measures one thing: **how complete the record is.** That means its identity (title, maker, date, medium, dimensions, type), its **cross-references to public authority records** (Getty, Wikidata, VIAF, national libraries), a provenance chain with a cited source for each step, and structured data for exchange between institutions. The cross-references matter because they are *public* — created and maintained by those authorities, not by us; by linking them, the passport draws on that standing without our adding any opinion. We do **not** grade how trustworthy a source is, and we do **not** judge a work's authenticity or its value. Ars Accordia compares publicly available information; it does not pass judgement on it. Every passport shows the full breakdown, so the number is never a black box, and the method is the same for every passport, published in full.

---

## Part E — Data model & computation

The score is **computed, never authored**. `build_passport_score.py` reads the passport's section data (Part A) and writes a `score` block onto the passport record:

```json
"score": {
  "passport_score": 94,
  "status": "green",
  "completeness": {
    "value": 0.94,
    "sections": [
      { "section": "identity",          "weight": 0.35, "fill": 1.00, "present": "6 of 6 fields",                    "contribution": 0.35, "in_scope": true },
      { "section": "authority_links",   "weight": 0.25, "fill": 1.00, "present": "2 public authorities — Getty ULAN, Wikidata", "contribution": 0.25, "in_scope": true },
      { "section": "provenance",        "weight": 0.25, "fill": 0.75, "present": "3 of 4 steps sourced",             "contribution": 0.19, "in_scope": true },
      { "section": "structured_export", "weight": 0.15, "fill": 1.00, "present": "JSON-LD + EODEM",                  "contribution": 0.15, "in_scope": true },
      { "section": "condition",         "weight": 0.00, "fill": null, "present": "not commissioned",                 "contribution": 0.00, "in_scope": false },
      { "section": "image",             "weight": 0.00, "fill": null, "present": "not commissioned",                 "contribution": 0.00, "in_scope": false }
    ]
  },
  "excluded": [ "source_quality_judgement", "authenticity", "monetary_value" ],
  "config_version": "weights-v3"
}
```

- `contribution` = `weight × fill` (renormalised); the in-scope contributions sum to `completeness.value`, and `passport_score = round(100 × completeness.value)`. The page renders straight from this — the arithmetic shown to the viewer is the arithmetic stored.
- Recompute on any change to the passport's fields. Store `config_version` so a displayed derivation is reproducible under the weights in force when it was issued.
- **These weights are the same constants as Instruction 11** (section weights 0.35 / 0.25 / 0.25 / 0.15). One config, both specs — never two copies that can drift.

**Note on Instruction 10.** The four-level validation vocabulary (FULLY_CORROBORATED … PENDING) was built to *grade* corroboration; that grading no longer feeds the score. Instruction 10's remaining jobs are still valid: the **publication gate** (PENDING is never published) and an **objective status** (is the work cross-referenced to public authorities? was it human-reviewed?), which drives the badge above. A follow-up reframe of Instruction 10 should rename its output from a corroboration *grade* to a cross-reference *status* and drop the believe-ranked levels — but that is a separate edit; until then, derive the badge from the objective facts only.

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

1. A passport with all in-scope sections fully filled scores 100; an empty published passport scores 0.
2. The contributions shown on the page sum to `completeness.value`, and `round(100 × completeness.value)` equals the displayed `passport_score` exactly.
3. The score has **no** second term — removing/altering any "corroboration" input has no effect, because none exists; the score moves only when a passport section's fill changes.
4. The Authority links section is scored by **count of public cross-references present**, never by source type or trustworthiness; two records each citing one public authority score that section identically regardless of which authority.
5. A section **in scope but empty** appears as a 0.00-contribution row (a visible gap); a **not-commissioned** section appears as "not commissioned — excluded" and does **not** lower the score.
6. Removing condition from scope (not commissioned) raises the score versus counting it as a zero — renormalisation works, and the page reflects the change.
7. Source quality, authenticity, and monetary value never appear as scored rows; the "what is not scored" line is present on every passport page.
8. The page renders entirely from the stored `score` block — no recomputation in the template; editing a field and recomputing changes both the number and the breakdown; a stale score fails `--check`.
9. The badge reports cross-reference status (green/amber/grey) as objective fact; it is not described anywhere as a measure of how believable the record is.
10. Σ of passport scores in a collection equals the collection's Ars Accordia Score, and their mean equals the average standard.

---

## What this component does NOT do

- It does **not** grade, rank, or judge sources — it counts whether public authority cross-references and provenance citations are present, nothing more.
- It does **not** add a corroboration term to the score — the score is completeness alone, measured on the passport.
- It does **not** grade authenticity or monetary value — they are structurally absent and named as not scored.
- It does **not** count a not-commissioned section as a zero — out-of-scope sections are excluded from the denominator and shown as excluded.
- It does **not** show the score without its derivation — the breakdown is mandatory on every passport page.
- It does **not** hand-write or hard-code any figure in the template — the page renders from the computed `score` block only.
- It does **not** keep its own copy of the weights — it shares Instruction 11's config, so the passport score and the collection score can never diverge.
