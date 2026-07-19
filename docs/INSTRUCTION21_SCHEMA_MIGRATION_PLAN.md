# Instruction 21 — Schema Consistency Migration Plan

Author: Claude (branch `claude/instruction21-gap-fix`)
Date: 2026-07-19
Companion to: `docs/HANDOVER_20260719_INSTRUCTION21.md`

## 1. Why this exists

While remediating the HTML-without-JSON gap (41 artist pages with no
backing canonical record, see the handover for root cause), it became
clear the artist JSON store contains at least **three generations of
schema and template**, none formally versioned or migrated into the
others. This document inventories what exists, explains why, and proposes
a single target shape plus a safe migration path — it does not execute a
full migration; that is future work, scoped here so it can be picked up
without re-deriving the investigation.

## 2. What's actually in the store today

### 2a. Artist JSON — two shapes coexist

**"Full" shape** (majority of records, e.g. `ART-HEINRIHSONE-1970.json`,
`ART-ABOLINA-1910.json`):
- `sources[]`, `source_refs[]`, `conflicts[]`, `cataloguing{}` all present
- `authority_links` covers 9 systems (wikidata, viaf, ulan, isni, rkd,
  lc_naco, gnd, bnf, libris), each `{id, uri, status, verified_date, notes}`
- `descriptors.occupations` is an array
- `_schema: "artbase:artist:v1"` at the bottom of the file

**"Minimal" shape** (a small cohort, e.g. `ART-GULBIS-MADARA.json`,
`ART-KAULACA-VINETA.json`, `ART-SUBACS-1963.json` — all recent
Wikidata-ID-pattern records, likely from `wikidata_to_passports.py` or a
sibling script):
- No `sources`, `source_refs`, `conflicts`, or `cataloguing` keys at all
- `authority_links` covers only 3 systems (wikidata, ulan, viaf), each
  `{id, uri, status}` — no `verified_date`/`notes`
- `descriptors.occupation` is a **singular** string
- `_schema` at the **top** of the file

Both shapes are read by `scripts/artist_profile_generator.py` without
error (it uses `.get()` throughout), so neither breaks page generation —
but any script that assumes `sources` or `cataloguing` exists (several do,
including the enrichment script written for Instruction 20) will silently
under-serve minimal-shape records unless it defensively does
`artist.setdefault("sources", [])` first, as Instruction 20's writer had
to.

### 2b. Artist HTML — three template generations

1. **Oldest** ("Galerija Jēkabs" era, all dated `Exported 2026-05-30`):
   two sub-variants — one with a "Data Sources & Verification" block
   (source-ledger style, origin/authority/status/warning rows), one
   without any sources section at all (Authority Records + Artworks only).
   Both predate the current `source_ledger`/validation-badge design.
2. **Current** (`templates/artist_profile.html.j2`, what
   `artist_profile_generator.py` emits today): Authority Records grid,
   optional ULAN enrichment block, Collection Appearances, **Biography**
   (added in this Instruction 21 pass — see §4), Artworks in Catalogue,
   Sources.

All 72 pages touched in this Instruction 20/21 pass (31 Imago Mundi +
41 gap-reconstructed) now render from the current template, since running
`artist_profile_generator.py` always emits the current one regardless of
which JSON shape it reads. **Template drift is self-healing on
regeneration** — the outstanding problem is JSON shape drift, not
template drift, because nothing currently forces a full-store
regeneration after a schema-affecting change.

### 2c. Why this happened (git-log-derived timeline, not guessed)

- `24a71a3` Wikidata Tier 1+2 enrichment — early full-shape records
- `64b3065` / `6cf3682` rebrand + restructure — template changes
- `d6c2621` Instruction 8 — gallery-origin attestations / field-level
  provenance ledger (the "Data Sources & Verification" block)
- `b9ab2d2` Instruction 10 — four-grade validation levels
- `daf45ed` (2026-06-02) — 58 living artists' **JSON only** deleted to
  cut Airtable usage; **HTML untouched**, which is the direct cause of
  the 41-page gap this instruction fixes
- Instruction 19/20 (this month) — introduced `sources[]` MAB/Imago
  Mundi entries and, new in Instruction 20, a top-level `biography{}`
  object with no prior art in the schema to follow

Each phase added fields additively to *some* records without a pass to
backfill the rest — reasonable at each individual step, but the
accumulated effect is the two-shape split described in §2a.

## 3. Target shape (proposed, not yet applied)

Adopt the "full" shape as canonical going forward:

```
sources: []
source_refs: []
conflicts: []
cataloguing: { review_status, catalogued_by, notes, tasks: [], engagement_ids: [] }
authority_links: { <9 systems>, artbase_id }
descriptors.occupations: []   # array, even if single-valued
biography: { en, lv, source_id, pages, language_note } | absent
_schema: "artbase:artist:v2"  # bump only once the migration below has run
```

`biography` stays a **single object**, not an array. Rationale (YAGNI):
every record that has one today has exactly one source for it
(`SRC-IMAGOMUNDI-LV-2014`). Promoting to an array now would be designing
for a hypothetical second biographical source that doesn't exist yet. If
and when a second source contributes biography text to an already-enriched
record, that is the trigger to migrate `biography` → `biographies: []`
in one pass across the whole store — not before.

## 4. Biography placement — resolved for now

Instruction 20 introduced `artist.biography` (top-level, sibling of
`identity`/`life`/`descriptors`) with no template rendering, which meant
the enriched content was invisible on the 31 Imago Mundi artist pages.
This pass adds a **Biography** section to
`templates/artist_profile.html.j2` (renders `bio.en`, `bio.lv`, and a
citation line resolved against `sources_registry` by `bio.source_id`),
positioned after Collection Appearances and before Artworks in Catalogue.
This is additive to the template only — no JSON shape change was needed,
since `biography` already existed as a key.

## 5. Migration script (not built in this pass — specified for next)

`scripts/migrate_artist_schema_v2.py` (proposed):
- For every `artbase_export/data/artists/*.json`:
  - Add missing keys (`sources`, `source_refs`, `conflicts`, `cataloguing`)
    as empty defaults — never overwrite a key that already has data.
  - Expand `authority_links` to the full 9-system set, defaulting new
    entries to `{"id": null, "uri": null, "status": "search_needed",
    "verified_date": null, "notes": null}` — never touch an existing
    entry.
  - Convert `descriptors.occupation` (string) → `descriptors.occupations`
    (array), preserving the value; leave `occupations` alone if already
    an array.
  - Leave `biography` untouched either way (already consistent).
- `--dry-run` prints a per-file diff count; require it to be run and
  reviewed before `--apply`, per the project's established
  scoped-diff-before-commit discipline.
- After `--apply`, regenerate every touched artist page (scoped to the
  IDs actually changed — never `--all` on the generator for an unrelated
  reason) and run `sitemap_generator.py` once at the end.
- Estimated blast radius: the "minimal" shape currently covers a small,
  identifiable cohort (Wikidata-ID-pattern artbase_ids); the exact count
  should be re-measured at execution time since both pipelines are still
  actively adding records.

This is intentionally **not executed in this pass** — it is a
store-wide, structural change and belongs in its own reviewed commit,
separate from the HTML-without-JSON content fix, and should not be run
while Copilot's review-queue branch is also mutating artist JSON files
(coordinate merge order first).

## 6. Recommendation

1. Land this Instruction 21 branch (41 reconstructed records + 1 retired
   duplicate + Biography template section) first — it's a content-parity
   fix with a small, well-understood diff.
2. Merge Copilot's review-queue branch (per the stated merge order).
3. Run `migrate_artist_schema_v2.py --dry-run` from a rebased main to get
   a fresh, accurate diff count before deciding whether/when to apply it
   as its own change.
