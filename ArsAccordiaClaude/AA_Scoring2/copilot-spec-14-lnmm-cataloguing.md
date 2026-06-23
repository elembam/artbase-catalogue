# Instruction 14 — Cataloguing & Scoring the LNMM Collection (the Ars Accordia process, end to end)

*Hand to Copilot as an operational runbook. It ties together Instruction 10 (cross-reference status), Instruction 11 (collection score), Instruction 12 (collection page), Instruction 13 (passport score), and the Wikidata book-reference procedure. The scoring is the easy part — it falls out of the passports. **The work is the cataloguing and the authority links.** Where this conflicts with Copilot's instinct, the runbook wins — ask before deviating.*

---

## What we are doing, in one line

Build real **Artwork Passports** for a defined set of works held at the Latvian National Museum of Art (LNMM), each catalogued through the full Ars Accordia process — identity, **public authority cross-references (Wikidata, Getty, VIAF…)**, sourced provenance, structured data — and then **add them up** into the LNMM collection score. Passports first; the score is the roll-up.

---

## The honest framing (set this before anything else)

The LNMM collection here is **Ars Accordia's public-registry catalogue of works held at LNMM** — not a commissioned assessment of the museum, and not a verdict on the museum's own documentation. So:

- The collection is scored **absolutely** (the sum of the passport scores), with **no coverage percentage** — we are not claiming to have catalogued all of LNMM, and we set **no `total_extent`** (Instruction 11 Part A: no N is a normal, fully-scored state).
- The page must read as *"works held at LNMM, documented by Ars Accordia"* — never *"LNMM's documentation score."* This keeps us honest and inside the rule that we don't issue unsolicited institutional ratings.
- These are public museum works by (mostly) long-deceased artists — public reference data. The living-person privacy rules (Instruction 9) do not bite here.

---

## Phase 1 — Define the collection record

Create `data/collections/COL-LNMM.json` (Instruction 11 Part F):

```json
{
  "collection_id": "COL-LNMM",
  "name": "Latvian National Museum of Art — works documented by Ars Accordia",
  "segment": "institution",
  "scope": {
    "definition": "Works held by the Latvijas Nacionālais mākslas muzejs (LNMM) catalogued by Ars Accordia for the public registry.",
    "status": "unknown",
    "source": "Ars Accordia registry"
  },
  "member_passports": [],
  "visibility": "public",
  "consent_to_publish_score": true,
  "assessment_status": "assessing"
}
```

Note: **no `total_extent`** — deliberate. `page_type` will derive to `scored` once `assessment_status` is `assessed` and there are member passports (Instruction 12). Until then the existing `collections/lnmm/` page stays a catalogue page.

---

## Phase 2 — Select the first works

Do **not** try to do the whole museum. Pick a **small, finishable first set** (start with 5–10 works) so we get a real, complete, scored collection rather than a large thin one.

- Choose **specific works** (not just artists) that LNMM holds and that we can document well — favour works by artists we already have Wikidata QIDs for, so the authority step is fast:
  Rozentāls `Q466052`, Purvītis `Q2006026`, Suta `Q4120285`, Uga Skulme `Q4126087`, Tīlbergs `Q4100741`, and the less-famous targets already on file (Hūns `Q6154397`, Feders `Q12672009`, Tīdemanis `Q4457149`, Krastiņš `Q58456712`, Ūders `Q20565577`).
- For each chosen work, record which artist it is, its LNMM inventory number if known, and whether the work already has its own Wikidata item (Phase 3b).

List the chosen AP-IDs into `COL-LNMM.member_passports` as they are created.

---

## Phase 3 — Build each passport (the Ars Accordia process, per work)

For every work, run these steps and generate the passport (`passport_generator.py`). The section names map to the passport page (§ 01, § 02, § 04…) and to the four scored completeness sections (Instruction 13). **The score is computed from what these steps actually produce — so do the steps, don't pad the fields.**

### 3a. Identity — § 01, Object ID / CDWA  *(scores 0.35)*
Record the Object ID categories to standard: title (and English title), creator, date, medium, dimensions, object type, subject, inscriptions, current location (LNMM). Six core descriptive fields drive the Identity fill (Instruction 13 Part A).

### 3b. Authority links — § 02 — **the Wikidata & authority reconciliation (the heart)**  *(scores 0.25)*
This is the step that gives a record its standing, and the one not to shortcut. For each work:

1. **Reconcile the artist** to public authorities and link them on the passport: Wikidata Q (use the QIDs above), **Getty ULAN**, **VIAF**, **ISNI**, **Latvian National Library (LNB)**.
2. **Reconcile the work itself.** Search Wikidata for an existing item for the artwork (many canonical works have one).
   - **If it exists** → link it (this is the strongest single cross-reference).
   - **If it does not** → this is where Ars Accordia *creates* a Wikidata item for the work (Phase 4) — which both earns the authority link and contributes to the public graph.
3. **Add term-level authorities:** **Getty AAT** for medium/technique, **ICONCLASS** for subject.
4. **Reconcile, never duplicate.** Check the **Mix'n'match catalog #8050** ("Ars Accordia — Latvian artists") and the open candidate-verify QIDs before creating anything; verify a candidate against the actual Wikidata record before trusting it.

The more **independent public authorities** a work is cross-referenced to, the fuller this section scores — counted by presence, **never graded by trustworthiness** (Instruction 13).

### 3c. Provenance — § 04 — sourced chain  *(scores 0.25)*
Record the ownership chain, and **cite a source for each step** (the fill is the share of steps that carry a citation). For LNMM works the chain usually resolves into the museum's acquisition; cite it to a real source — the LNMM catalogue, or the LNMM portraits book `SRC-LNMM-PORTRAITS-2009` (page numbers), following the book-reference procedure. Counting whether a step is *sourced* is objective; we do not rank the sources.

### 3d. Structured / export  *(scores 0.15)*
Generate the **Schema.org VisualArtwork JSON-LD** (for discovery) and the **LIDO/EODEM export record** (for museum exchange). Both present → full fill.

### 3e. Condition — § 05  *(not scored here)*
We are **not** commissioned to do physical condition assessment of museum-held works, so condition is **not in scope** for these passports — mark it *not commissioned — excluded* (Instruction 13). It is excluded from the denominator, not counted as a zero.

### 3f. Compute the passport score
Run `build_passport_score.py AP-...`. The Passport Score = `100 × Completeness`, with the § 06 derivation panel rendered from the computed block (Instruction 13). The score is whatever the real record earns — a work that is fully identified, cross-referenced to several public authorities, with sourced provenance and structured data, will score high; thin records score low and the panel shows exactly why.

---

## Phase 4 — The Wikidata contribution (do this *as* you catalogue, with discipline)

This is the reciprocal half of the process and must not be skipped: Ars Accordia **consumes** authority data (which raises passport scores) and **contributes sourced data back** (which builds the public graph and Ars Accordia's standing). The discipline matters as much as the act:

- **Lead with book-sourced facts.** Where cataloguing establishes a fact from the LNMM book (a date, a creator, a medium), contribute it to the relevant Wikidata item with a proper book reference: **`S248 <LNMM-book-QID> + S304 "<page>"`** (Instruction: the book-reference procedure). *Confirm the LNMM book QID for `SRC-LNMM-PORTRAITS-2009` before citing it.*
- **Create artwork items where missing** (Phase 3b) via **human-reviewed QuickStatements** — never auto-commit. A minimal artwork item:
  `P31` (painting `Q3305213` or appropriate) · `P170` creator `<artist QID>` · `P571`/`P577` inception · `P186` material · `P2048`/`P2049` dimensions · `P195` collection `<LNMM institution QID — confirm>` · `P217` inventory number · label + description, with `S248/S304` references on sourced statements.
- **Register in Mix'n'match #8050** any artist/work not already matched.
- **Pace the P973 self-links** (`described at URL` → arsaccordia.com). Do *not* mass-add them; they are low-value from a young account and lead with the sourced facts instead.
- **Never cite Ars Accordia as a Wikidata source.** Cite the books and the authorities; Ars Accordia's credit accrues through edit history and the eventual ID property, not through self-citation.
- **Every Wikidata edit is human-reviewed before it is committed.** Generate QuickStatements; a person approves and runs them.

---

## Phase 5 — Add the collection score (the roll-up)

Once the first set of passports exists and is in `COL-LNMM.member_passports`:

1. Set `assessment_status: "assessed"`.
2. Run `build_collection_score.py COL-LNMM`. It reads the member Passport Scores and writes (Instruction 11 Part F): `ars_accordia_score` (the **sum**), `average_standard` (the **mean** → the band, e.g. *Substantial Record*), `works_documented` (the **count**), the `gaps` map, and **no `relative_completeness`** (no `total_extent`).
3. Confirm the atom and aggregate agree: `--check` must show **Σ passport scores = `ars_accordia_score`** (Instruction 13).

That is the entire collection evaluation — the works' scores, added up.

---

## Phase 6 — Publish the collection page

Render the LNMM page as a **scored collection page** (Instruction 12), with the honest framing from the top of this runbook:

- Seal shows the **Ars Accordia Score** (open figure, no "/100"), with **average standard** and **work count** beside it; band from the average standard.
- The panel shows the four completeness sections; the gap map shows where the records are thin (likely provenance early on).
- Title/credential read *"works held at LNMM, documented by Ars Accordia"* — not an institutional rating. No coverage percentage anywhere.
- Each work links to its passport, with its green/amber/grey **cross-reference status** badge (Instruction 10 / 13).
- Link to **`/method/`** for how the score is built.

---

## Guardrails (non-negotiable)

- **No score is hand-set.** Passport scores and the collection score are computed from the records; recompute on change (`--check` fails on drift).
- **No Wikidata edit is auto-committed.** Human-reviewed QuickStatements only.
- **Never cite Ars Accordia as a source** on Wikidata; cite books/authorities.
- **Count cross-references, don't grade them.** No source is scored as better than another (Instruction 13).
- **No coverage claim for LNMM** — absolute score only, no `total_extent`, framed as Ars Accordia's catalogue.
- **Reconcile before creating** — check Wikidata, Mix'n'match #8050, and candidate-verify QIDs to avoid duplicate items.
- **Pending is not published** (Instruction 10): a work that is not yet properly catalogued does not appear on the public page.

---

## Done criteria

1. `COL-LNMM.json` exists with a scope definition and **no `total_extent`**.
2. The chosen first works each have a passport with: identity recorded, ≥1 public authority cross-reference, sourced provenance where available, and structured/export records — and a computed § 06 score panel.
3. Sourced facts have been contributed to Wikidata with **book references (S248/S304)**, artwork items created where missing (human-reviewed), and entries registered in Mix'n'match #8050 — with P973 paced, not mass-added.
4. `build_collection_score.py COL-LNMM` produces an Ars Accordia Score, average standard, and work count; `--check` confirms the sum equals the headline figure.
5. The LNMM page renders as a scored collection page with the honest framing, the cross-reference badges, and a link to `/method/`.

---

## Items to confirm before running

- The **Wikidata QID for the LNMM portraits book** (`SRC-LNMM-PORTRAITS-2009`) — needed for `S248`.
- The **Wikidata QID for LNMM the institution** — needed for `P195` (collection) on artwork items.
- The **specific works** chosen for the first set, with their LNMM inventory numbers where available.
- Any **candidate-verify QIDs** to be relied on (verify each against its live Wikidata record first).
