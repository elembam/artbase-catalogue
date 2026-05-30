# Instruction 10 — Validation Levels & Data Quality

*Hand to Copilot as a single component. It replaces the `confirmed` / `candidate` binary used since the beginning with a four-grade corroboration model adapted from the Global LEI System (GLEIF), threading through the source ledger (Instruction 8), the contributor trust flags (Instruction 9), and the Wikidata-contribution gate. This is a core-concept change and touches the live site — read the migration section (Part G) before running anything. Where it conflicts with Copilot's instinct, the spec wins — ask before deviating.*

---

## Purpose

`confirmed` / `candidate` was the right instinct but too coarse. GLEIF — the closest working precedent for this kind of registry — grades every record on a four-level **corroboration** scale and records *which authority* corroborated it. This instruction adopts that:

1. replace the binary with **four validation levels** (`PENDING` · `ENTITY_SUPPLIED_ONLY` · `PARTIALLY_CORROBORATED` · `FULLY_CORROBORATED`),
2. add **`validation_authority`** — the source(s) that corroborate the record,
3. validate **Level 1 (object identity)** and **Level 2 (relationships / provenance)** *separately*, and
4. define a **conformance badge** — the visible, honest quality signal on every passport.

---

## The conceptual shift: corroboration, not just "someone checked"

The old binary mixed two ideas. The new model separates them cleanly:

- **Validation level** measures *corroboration*: how much of the record is backed by an **authoritative source**, with no unresolved conflict.
- **`validated_by`** records *who* performed the validation (a `platform_staff`/`institutional` contributor, or `automated`) — the analogue of GLEIF's ManagingLOU.

**What counts as an authoritative source** (this is the whole hinge): the authority files (**Wikidata, Getty ULAN, Getty AAT, VIAF, ISNI, LNDB**) and **published catalogues / museum records** (the ISBN books from Instruction 7). It explicitly does **not** include commercial galleries, owner submissions, or Ars Accordia itself. This maps directly onto the contributor trust flags: only `can_confirm: true` sources can lift a record above `ENTITY_SUPPLIED_ONLY`.

---

## Part A — The four validation levels

| Level | Meaning | Published? | Wikidata-contributable? |
|---|---|---|---|
| `PENDING` | Not yet validated (e.g. a fresh user submission awaiting review). | **No** — never published or exported | No |
| `ENTITY_SUPPLIED_ONLY` | Rests only on a non-authoritative origin (commercial gallery, owner submission, hand-entry); no authoritative corroboration. | Yes, but labelled uncorroborated | No |
| `PARTIALLY_CORROBORATED` | Some key fields corroborated by an authoritative source; others uncorroborated or in conflict. | Yes | Only the corroborated fields |
| `FULLY_CORROBORATED` | All key fields of the layer corroborated by ≥1 authoritative source, no unresolved discrepancy. | Yes | Yes |

`PENDING` is the quarantine state from Instruction 9: <em>records at this level SHALL NOT be published</em> — same rule GLEIF applies.

**Key fields** (what must be corroborated to reach `FULLY_CORROBORATED`), per layer:
- Level 1, artist: name, birth date, death date, nationality.
- Level 1, artwork: title, creator, date, medium, dimensions.
- Level 2: each provenance / ownership / collection assertion, validated individually.

---

## Part B — `validation_authority` and the integrity rule

Every corroborated record names the authority/authorities that corroborate it, e.g. `["wikidata", "ulan", "SRC-LNMM-PORTRAITS-2009"]`.

**The integrity rule (borrowed directly from GLEIF):** a record may **not** be marked `FULLY_CORROBORATED` (or `PARTIALLY_CORROBORATED`) unless `validation_authority` is non-empty and every listed authority is a `can_confirm: true` source. If the level claims corroboration but the authority field is empty or contains only non-authoritative sources, the data-quality check **fails** and the level is forced down to `ENTITY_SUPPLIED_ONLY`. This is the formal version of "staff confirmation must cite a basis" (Instruction 9, Part G): a level is never a bare label — it always points at what justifies it.

`validated_by` records the contributor (or `automated`) that performed the validation, plus `validated_at`. Automated corroboration is allowed to *compute* a level, but the conformance badge requires human review (Part E).

---

## Part C — Level 1 / Level 2: validate identity and relationships separately

The most useful idea from GLEIF: an entity's **identity** and its **relationships** are validated independently. So an artwork can have well-corroborated identity and owner-supplied provenance — and the record says so honestly.

- **Level 1 — object identity.** *What it is.* Artwork: title, creator, date, medium, dimensions, Object ID. Artist: name, dates, nationality.
- **Level 2 — relationships.** *Who owns/owned it; what it belongs to.* Provenance/ownership chain, collection membership, creator↔work links.

Each layer carries its own `level`, `authority`, `validated_by`, `validated_at`, and optional `revalidate_by`:

```json
"validation": {
  "level1": {
    "level": "FULLY_CORROBORATED",
    "authority": ["wikidata", "ulan", "SRC-LNMM-PORTRAITS-2009"],
    "validated_by": "CON-STAFF-AB",
    "validated_at": "2026-05-DD",
    "revalidate_by": "2027-05-DD"
  },
  "level2": {
    "level": "ENTITY_SUPPLIED_ONLY",
    "authority": [],
    "validated_by": "automated",
    "validated_at": "2026-05-DD"
  }
}
```

This is the realistic shape for private-collection art: the *object* is established, the *ownership* is owner-asserted. The passport shows both, separately, instead of collapsing them into one misleading status.

`revalidate_by` is the freshness signal (GLEIF's renewal idea, adapted): art identity is static so there's no mandatory lapse, but Level 2 data and machine-validated records carry a re-check date, because the authorities they rest on (Wikidata especially) change over time.

---

## Part D — The level is computed from the source ledger, not hand-set

The validation level is a **derived summary of the source ledger** (Instruction 8, Part G), so the two can never disagree. The logic:

```
for each layer (level1, level2):
    key_fields   = the layer's key fields that have a value
    corroborated = key fields backed by ≥1 authority-bucket source (can_confirm: true),
                   with no unresolved discrepancy
    if record is pending review (Instruction 9)         → PENDING
    elif corroborated == key_fields and key_fields > 0   → FULLY_CORROBORATED
    elif corroborated > 0                                → PARTIALLY_CORROBORATED
    else                                                 → ENTITY_SUPPLIED_ONLY
    authority = the distinct authority sources that did the corroborating
    apply the Part B integrity rule (no corroborated level without a valid authority)
```

`verify_candidates.py` becomes the engine that runs this computation. The old source-ledger `verification` block (status/basis) is **superseded** by this `validation` block; regenerate ledgers so they emit `validation` with `level1`/`level2`. The per-field `has_citable_source` flag in the ledger lines up exactly with "field is corroborated."

Contributor flags gate what can raise the level: a `can_confirm: false` contributor's attestation (gallery `data_origin`, user `owner_asserted`) can never push a layer above `ENTITY_SUPPLIED_ONLY` on its own.

---

## Part E — The conformance badge

A single visible indicator on every passport, derived from Level 1 (identity), with Level 2 shown separately. Modelled on GLEIF's "policy conforming" mark.

| Badge | Condition | Public label |
|---|---|---|
| ✓ green | Level 1 `FULLY_CORROBORATED` **and** `validated_by` is human (staff/institutional) **and** `validation_authority` non-empty | "Corroborated against authoritative sources" |
| ◐ amber | Level 1 `PARTIALLY_CORROBORATED`, **or** `FULLY_CORROBORATED` by `automated` only (not yet human-reviewed) | "Partially corroborated" |
| ○ grey | Level 1 `ENTITY_SUPPLIED_ONLY` | "Source-supplied; not independently corroborated" |
| (none) | `PENDING` | not displayed (unpublished) |

Notes:
- The green badge preserves the old `confirmed` meaning as its bar: full corroboration **plus** a human sign-off. Machine-only full corroboration sits at amber until a cataloguer reviews it — efficient to compute, honest to display.
- **Level 2 (provenance) renders its own small level next to the provenance section**, never folded into the headline badge — so a green-badged work with owner-supplied provenance reads truthfully ("identity corroborated; provenance owner-supplied").
- The badge legend and the `/about/` "Authority Verification" section must be rewritten from the Confirmed/Candidate language to this four-grade model (see Part G).

---

## Part F — Threading through the existing pipeline

- **Source ledger (Instr. 8):** emits the `validation` block; `verification` (status/basis) is retired in favour of it.
- **Contributor flags (Instr. 9):** `can_confirm` defines which sources can corroborate; `wikidata_citable` still governs Wikidata references. `validated_by` points at the contributor that validated.
- **Moderation gate (Instr. 9):** unreviewed submissions are `PENDING` → unpublished, unexported, never contributed.
- **Wikidata contribution (Instr. 7):** now **field-level and level-aware** — contribute a fact only if that field is corroborated by a `wikidata_citable` authority. Freely from `FULLY_CORROBORATED`; only the corroborated fields from `PARTIALLY_CORROBORATED`; **never** from `ENTITY_SUPPLIED_ONLY` or `PENDING`. (Sharper than the old "only confirmed records" rule.)
- **`audit_provenance.py`:** enforces the Part B integrity rule across the dataset — flags any record whose claimed level exceeds what its authorities actually support, and any field with no source at all.

---

## Part G — Migration from `confirmed` / `candidate`

This replaces a status used throughout the data **and shown on the live site**. Migrate deliberately.

**Mapping (run as a one-time script that reads each record's attestations + authority links):**

| Old status | New Level 1 | `validated_by` | Note |
|---|---|---|---|
| `confirmed` | `FULLY_CORROBORATED` if all key fields are authority-backed; else `PARTIALLY_CORROBORATED` | the confirming staff, else `migrated` | was human-reviewed → eligible for the green badge when fully corroborated |
| `candidate` (has authority match) | `PARTIALLY_CORROBORATED` | `automated` | machine-matched, not yet human-reviewed |
| `candidate` (origin-only: gallery/owner) | `ENTITY_SUPPLIED_ONLY` | `automated` | no authoritative corroboration |
| (new, unreviewed submission) | `PENDING` | — | unpublished |

- **Level 2** for existing records is almost all `ENTITY_SUPPLIED_ONLY` or empty (provenance is owner-supplied or absent today).
- Ambiguous cases (e.g. a `confirmed` record whose authority backing can't be reconstructed) are flagged for human review, not silently downgraded.

**Public-facing changes that ship with the migration** (do not skip — this is the credibility-guide principle):
- Replace the Confirmed/Candidate ⚠ badges on artist/artwork pages with the three-tier conformance badge.
- Rewrite the `/about/` "Authority Verification" section to describe the four-grade model (it currently defines Confirmed/Candidate).
- Update the JSON-LD: only authority-corroborated identifiers in `sameAs` (already the rule; now tie it to the validation level).
- Update the credibility guide so claims and artifacts stay in lockstep.

---

## Data model / Airtable

**Entity tables (`Artists_Makers`, `Artworks`)** — replace the single status field with:
- `validation_level1` (single select: PENDING / ENTITY_SUPPLIED_ONLY / PARTIALLY_CORROBORATED / FULLY_CORROBORATED)
- `validation_authority_l1` (text or linked: the corroborating authorities/sources)
- `validated_by_l1` (link → Contributors, or `automated`), `validated_at_l1`, `revalidate_by_l1`
- the same quartet for `*_l2` (Level 2 / relationships)
- `conformance_badge` (computed: green / amber / grey / none) — derived, not hand-edited

Retire the old `confirmed`/`candidate` field after migration (keep a `legacy_status` column briefly for audit).

---

## CLI

```
python3 scripts/verify_candidates.py                       # (re)compute validation levels for all records
python3 scripts/verify_candidates.py --record ART-ANNUSS-1893
python3 scripts/migrate_validation.py --dry-run            # show old→new mapping, write nothing
python3 scripts/migrate_validation.py                      # apply the one-time migration
python3 scripts/audit_provenance.py --check-levels         # fail on any level unsupported by its authorities
python3 scripts/build_source_ledger.py --check             # ledger 'validation' block matches the data
```

---

## Acceptance tests

1. A record whose key Level-1 fields are all backed by Wikidata + a published catalogue computes to `FULLY_CORROBORATED` with those authorities listed.
2. A record with one corroborated field and one uncorroborated field computes to `PARTIALLY_CORROBORATED`.
3. A record supported only by a gallery `data_origin` or `owner_asserted` attestation computes to `ENTITY_SUPPLIED_ONLY`, regardless of how complete it looks.
4. Setting `FULLY_CORROBORATED` with an empty `validation_authority` fails the integrity check and is forced to `ENTITY_SUPPLIED_ONLY`.
5. An artwork with corroborated identity and owner-supplied provenance shows `level1: FULLY_CORROBORATED`, `level2: ENTITY_SUPPLIED_ONLY`.
6. The conformance badge is green only when Level 1 is `FULLY_CORROBORATED` **and** `validated_by` is human; automated full corroboration shows amber.
7. `wikidata_contribute.py` contributes a field only when that field is corroborated by a `wikidata_citable` authority; nothing is contributed from `ENTITY_SUPPLIED_ONLY` or `PENDING`.
8. Migration maps a human-`confirmed` record with full authority backing to green-eligible `FULLY_CORROBORATED`, and an origin-only `candidate` to `ENTITY_SUPPLIED_ONLY`.
9. `audit_provenance.py --check-levels` flags any record whose level exceeds its authority support.
10. Regenerating the source ledger yields a `validation` block identical to the computed levels (no drift).

---

## What this component does NOT do

- It does **not** allow a level above `ENTITY_SUPPLIED_ONLY` without a named, `can_confirm: true` authority — no bare "corroborated" labels.
- It does **not** let a `can_confirm: false` contributor (gallery, private user) raise a validation level on their own.
- It does **not** show a green conformance badge for machine-only validation — human review is the bar for green.
- It does **not** fold Level 2 (provenance) into the headline badge — relationships are shown with their own level.
- It does **not** contribute uncorroborated or partially-uncorroborated fields to Wikidata.
- It does **not** silently downgrade ambiguous legacy records during migration — they are flagged for review.
- It does **not** leave the public site describing the retired Confirmed/Candidate model — the badge legend, the `/about/` page, and the credibility guide change with the data.
