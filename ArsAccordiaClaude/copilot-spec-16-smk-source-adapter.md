# Instruction 16 — The SMK Source Adapter (and the work-level authority model)

*Hand to Copilot as a single component. It builds on the passport schema and the cross-reference / authority-links model (Instructions 10 and 13). It does two things: (A) refines the authority model so every authority link records its **scope** — making explicit the distinction that most public registers identify **people**, while a collection API like SMK's supplies the rarer **work-level** authority record; and (B) adds the first implementation of a generic **CollectionSourceAdapter**, with SMK as the first source. The standing discipline holds throughout: Ars Accordia **cross-references and cites** public reference data, **never invents** it, **never grades** it, and **respects per-object rights**. Where this conflicts with Copilot's instinct, the spec wins — ask before deviating.*

---

## Purpose

Connect SMK's open collection API (`api.smk.dk`) as the first authoritative **collection source**, so that for any SMK-held work Ars Accordia can:

1. attach the SMK object record as a counted **work-level** authority cross-reference (the KMS inventory number + the SMK Open URL);
2. **populate passport fields from SMK with SMK cited as the source** — title, creator, dating, technique, dimensions, inventory number, provenance/acquisition, image, rights;
3. **reconcile SMK ↔ Wikidata** and, where Wikidata lacks the link, generate a reviewed give-back task.

Build it as a **reusable adapter**, not an SMK feature. Ars Accordia is a passport engine that consumes authoritative collection sources; SMK is the first of several.

---

## Part A — The authority model refinement: **authority scope**

Today the passport's authority links are a flat list of cross-references. Add a **`scope`** to each link. There is no universal register of *paintings* — ULAN, VIAF, ISNI, RKDartists, and the artist side of Kunstindeks Danmark all identify **people**. A **work-level** authority record (an entry for the object itself) exists chiefly where a collection catalogues the work — which is exactly what SMK provides. Scope makes the passport honest about *what each link identifies*, and queryable.

**`authority_scope` enum:** `artist_maker` · `artwork_object` · `institution` · `place` · `subject` · `material_technique` · `source_document`.

**Each authority link records:**

```json
{
  "scope": "artwork_object",
  "system": "SMK",
  "id": "KMS4185",
  "uri": "https://open.smk.dk/en/artwork/image/KMS4185",
  "status": "approved_institutional_source"
}
```

Typical split for a single work:

```text
Person-level (scope: artist_maker)      Work-level (scope: artwork_object)
- Wikidata artist QID                   - SMK object number (KMS…)
- Getty ULAN                            - SMK Open URL
- VIAF / ISNI                           - Wikidata artwork QID (if present)
- RKDartists                            - museum inventory number
                                        - catalogue raisonné number
                                        - other collection-API links
```

**CRITICAL guardrail — scope is descriptive, never a scoring weight.** The completeness score still counts cross-references **by presence** (`authority fill = min(1, cross_references / 2)`, Instruction 13). A work-level link is **not worth more** than a person-level link. Ars Accordia **counts** cross-references; it does not **rank** them. Scope tags a link; it must never change its weight in the score. Do not add per-scope multipliers.

---

## Part B — The generic source-adapter interface

SMK is the **first implementation** of one interface that will later serve Rijksmuseum, the Met, Europeana, the Royal Danish Collection, and Kunstindeks Danmark. Build the seam once.

```text
CollectionSourceAdapter            # abstract base
├── fetch_object_by_id(id)         # → raw source record
├── search_objects(query)          # → [raw records]
├── normalize_to_object_record()   # raw → canonical passport ObjectRecord
├── extract_authority_links()      # → [{scope, system, id, uri, status}]
├── extract_media()                # → [{type, uri, iiif, w, h}]  (gated by rights)
├── extract_rights()               # → {public_domain, license, copyright_status, attribution}
├── extract_source_citation()      # → Source_Documents record
└── produce_import_report()        # → human-readable: imported / missing / needs-reconciliation
```

Implementations:

```text
SMKAdapter            # this instruction
RijksmuseumAdapter    # later
MetAdapter            # later
EuropeanaAdapter      # later
RoyalDanishCollectionAdapter   # later — likely holder of the Hunæus/Dagmar portrait
KunstindeksAdapter    # later
```

The canonical passport schema must not change shape per source — adding a second adapter later must require **no** change to the passport or the authority model.

---

## Part C — SMK API specifics

- **Base:** `https://api.smk.dk/api/v1/` · **OpenAPI/Swagger docs:** `https://api.smk.dk/api/v1/docs/`
- **Object by inventory number:** `https://api.smk.dk/api/v1/art/?object_number={KMS…}`
- **Search:** `https://api.smk.dk/api/v1/art/search/?keys={query}`
- **Responses:** JSON.
- **Human URL (SMK Open):** `https://open.smk.dk/…` — store as the work-level `uri`.
- **Rights:** marked **per object** — each work is flagged public domain (CC0) **or** under copyright.

**Confirm exact field names against the live OpenAPI schema** at `/api/v1/docs/` before mapping — the schema is the source of truth and may have changed. Do not hard-code field names from this spec without checking; map against the documented schema.

---

## Part D — Field mapping (SMK JSON → passport)

Map at the documented-schema level (confirm names in the Swagger doc). Intended mapping:

| SMK record | → Passport | Notes |
|---|---|---|
| `object_number` | inventory number **+ work-level authority link** | scope `artwork_object`, system `SMK`, uri = SMK Open URL |
| `titles[].title` | Identity · title | take the primary/preferred title; keep alternates |
| `production[]` (makers) | Identity · creator | **reconcile each maker to person-level authorities** (Wikidata/ULAN); use any external IDs SMK supplies, else flag for reconciliation |
| `production_date[]` (start/end) | Identity · date | record as given; a range is a legitimate value |
| `techniques[]` / `materials[]` | Identity · medium / technique | |
| `dimensions[]` | Identity · dimensions | |
| `object_names[]` | Identity · object type | |
| `inscriptions` / `signs` | Identity · inscriptions / signatures | |
| `provenance` / `object_history_note` / `acquisition_*` | Provenance | **sourced to SMK** — this is sourced provenance, which the score rewards |
| image fields (`image_native` / `image_iiif_id` / `iiif_manifest`) | Image / media | **store only if rights allow** (Part E) |
| rights / public-domain field | Rights block | per-object; always stored (Part E) |
| `frontend_url` | work-level authority `uri` (SMK Open) | |
| `id` | SMK internal id | reference only |

Only fields **present** in the SMK record are populated. Absent fields remain **gaps** — never filled by inference.

---

## Part E — Rights handling (per-object, never assume)

- **Read the per-object rights / public-domain field and store it in the passport rights block on every import.** Rights are a recorded fact about each work.
- **Public domain (CC0):** metadata and image are reusable — store and display the image.
- **Under copyright:** store the metadata, cite and **link** SMK, but **do not redistribute the image** — reference SMK's image/IIIF by link only, and carry the required attribution.
- **Missing or ambiguous rights → treat as restricted.** Do not reuse the image. **Never assume CC0.**

The API being "free to use" governs *access*, not *image reuse*. Reuse is governed by the per-object flag.

---

## Part F — Citation rule

- **Every field populated from SMK carries SMK as its source** — create a `Source_Documents` record (system: `SMK API`, the object URL, retrieved date) and reference it from the passport.
- **Ars Accordia cites SMK, never Ars Accordia itself.**
- **Only what SMK's record contains is recorded.** No claim is invented; gaps stay gaps. If SMK's record is silent on provenance, the passport is silent on provenance.

---

## Part G — Wikidata reconciliation (a reviewed give-back lever)

- If a **Wikidata artwork item** exists for the SMK object, add it as a work-level authority link (scope `artwork_object`, system `Wikidata`).
- If **Wikidata lacks the SMK identifier** for a work it does have, generate a **reviewed** Wikidata contribution task (human-reviewed QuickStatements, written to `data/contributions/`) — **never auto-committed**, per the give-back discipline (Instruction 15). SMK is an authoritative source for such a statement; Ars Accordia is not cited.

---

## Part H — Data model

The adapter writes into the canonical object model (the working store and its Git JSON export):

- **Artwork / ObjectRecord** — the passport record, with fields populated per Part D.
- **`Authority_Links`** — one row per cross-reference, each with `scope`, `system`, `id`, `uri`, `status` (Part A).
- **`Source_Documents`** — one row for the SMK API record (Part F).
- **Rights** — the per-object rights block (Part E).
- **Media** — image/IIIF references, present only where rights allow (Part E).

---

## CLI

```
python3 scripts/smk_adapter.py KMS4185 --draft        # fetch one object, emit a draft passport
python3 scripts/smk_adapter.py KMS4185 --report       # import report: imported / missing / needs-reconciliation
python3 scripts/smk_adapter.py --search "Hunæus"      # search SMK by keyword
python3 scripts/smk_adapter.py KMS4185 --wikidata     # prepare a reviewed SMK↔Wikidata task (never auto-commit)
```

---

## Acceptance tests

1. **The core case.** Input `KMS4185` produces: an Artwork record; a `Source_Documents` record for the SMK API record; an `Authority_Links` record with `scope = artwork_object`, `system = SMK`, `id = KMS4185`; a populated rights block; image/media **only if rights allow**; a draft passport; SMK cited as source; and **no claim invented** beyond SMK's record.
2. **Copyrighted work.** A copyrighted SMK object: the image is **linked, not redistributed**; the rights block reflects copyright; attribution is carried.
3. **Public-domain work.** A CC0 object: the image is stored and displayable; the rights block records public domain.
4. **Generic adapter.** Adding a second source (even a stub `RijksmuseumAdapter`) requires **no change** to the passport schema or the authority model.
5. **Scope is not graded.** Two works with the same number of cross-references score identically regardless of scope mix; no per-scope weight exists in the score.
6. **Not found.** An invalid or non-SMK `object_number` returns a clean "not found" — **no record is invented**.
7. **Idempotent.** Re-running on the same `object_number` updates the existing records rather than duplicating them.
8. **Verifiable.** The stored work-level `uri` resolves to the live SMK record (the cross-reference is real and checkable).

---

## What this component does NOT do

- It does **not** bulk-ingest SMK's collection — Ars Accordia catalogues works it documents and cross-references SMK where the work is SMK-held. Depth, not breadth.
- It does **not** assume CC0 — rights are read and stored **per object**, and image reuse is gated on them.
- It does **not** grade authority links by scope — it counts cross-references by presence; scope is descriptive only.
- It does **not** invent claims — only what SMK's record contains is recorded; gaps remain gaps.
- It does **not** hard-code to SMK — it is the first implementation of a generic adapter interface.
- It does **not** auto-commit Wikidata edits — reconciliation produces reviewed tasks only.
- It does **not** cite Ars Accordia as a source.

---

## First build step

**SMK source adapter v0.1:** fetch one SMK inventory number — `KMS4185` (Hunæus's self-portrait) — map it into the canonical object model, issue a draft Artwork Passport, store the SMK object record as an **approved work-level authority link** (scope `artwork_object`), populate the rights block, attach the image only if rights allow, and cite SMK as the source. That single exercise proves the connector and becomes the template for every collection API after it.
