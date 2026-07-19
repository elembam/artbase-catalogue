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

1. ~~Land this Instruction 21 branch (41 reconstructed records + 1 retired
   duplicate + Biography template section) first~~ — **done**: merged to
   `main` as PR #1 (`8cca5c7`), after Copilot's `copilot/review-queue-batch1`
   (`f9550ca`).
2. Run the sizing query in §7.1 (below) before scheduling the migration —
   the cohort has moved since this plan was first drafted (see current
   count).
3. Execute per the checklist in §7.

---

## 7. Execution-ready checklist (status: **NOT EXECUTED** — plan only)

Everything below this line is a specification for a future, separately
reviewed pass. No migration script has been written or run as part of
this document. `migrate_artist_schema_v2.py` does not exist in the repo
yet.

### 7.1 Current sizing (measured 2026-07-19, from `main` post PR #1)

Re-run before executing, since both agents are still actively adding/
touching artist JSON:

```
python3 -c "
import json
from pathlib import Path
full, minimal, other = [], [], []
for f in sorted(Path('artbase_export/data/artists').glob('*.json')):
    d = json.loads(f.read_text())
    has_sources, has_cat = 'sources' in d, 'cataloguing' in d
    occ = d.get('descriptors', {}).get('occupations')
    occ_singular = 'occupation' in d.get('descriptors', {})
    n_auth = len([k for k in d.get('authority_links', {}) if k != 'artbase_id'])
    if has_sources and has_cat and isinstance(occ, list) and n_auth >= 9:
        full.append(f.stem)
    elif not has_sources and not has_cat and occ_singular:
        minimal.append(f.stem)
    else:
        other.append(f.stem)
print('full:', len(full), '| minimal:', len(minimal), '| partially-migrated hybrid:', len(other))
"
```

Result at time of writing: **354 total** — 328 full-shape (92.7%),
17 pure-minimal-shape (4.8%), 9 partially-migrated hybrids (2.5%,
e.g. `ART-GULBIS-MADARA`, `ART-KAULACA-VINETA`, `ART-KEIRE-KRISTINE` —
these gained a `sources[]` array via Instruction 19/20 enrichment or the
review-queue resolver, but never a `cataloguing` block or the 9-system
`authority_links`, so they sit between the two shapes today). The 41
records reconstructed by Instruction 21 were written directly in full
shape and are not part of either gap.

### 7.2 Field mapping (minimal/hybrid → target full shape)

| Field | Minimal-shape source | Target | Rule |
|---|---|---|---|
| `sources` | absent, or partial array (hybrid) | `[]` if absent, else unchanged | never overwrite existing entries |
| `source_refs` | absent | `[]` | additive only |
| `conflicts` | absent | `[]` | additive only |
| `cataloguing` | absent | `{"review_status": "draft", "catalogued_by": null, "notes": null, "tasks": [], "engagement_ids": []}` | additive only; never overwrite if any sub-key already present |
| `authority_links.{viaf,isni,rkd,lc_naco,gnd,bnf,libris}` | absent (only wikidata/ulan/viaf present in pure-minimal) | `{"id": null, "uri": null, "status": "search_needed", "verified_date": null, "notes": null}` per missing system | never touch `wikidata`/`ulan`/`viaf` if already populated |
| `authority_links.{wikidata,ulan,viaf}` shape | `{id, uri, status}` (3 keys) | `{id, uri, status, verified_date, notes}` (5 keys) | add the 2 missing keys as `null`; preserve existing `id`/`uri`/`status` values verbatim |
| `descriptors.occupation` (string) | e.g. `"painter"` | `descriptors.occupations: ["painter"]` | convert, then remove the singular key; skip entirely if `occupations` (plural) already exists |
| `_schema` | `"artbase:artist:v1"` (position varies) | unchanged value, normalize key position (cosmetic, low priority) | — |
| `biography` | n/a (independent of shape) | unchanged | out of scope for this migration — already consistent per §4 |

### 7.3 Script contract

`scripts/migrate_artist_schema_v2.py` (to be built):
- `--dry-run` (default): print one line per file that *would* change,
  plus a final `N files would change / M unchanged` summary. Writes
  nothing.
- `--apply`: performs the writes described in §7.2. Refuses to run
  without `--dry-run` having been invoked first in the same session
  unless `--force` is also passed (mirrors the two-step discipline
  already used for `resolve_instruction20_review_queue.py`).
- Idempotent: running it twice produces zero further changes the second
  time (every rule in §7.2 is a presence-check, not an unconditional
  write).
- Exits non-zero if any file fails to parse as JSON, before writing
  anything (fail closed, not partial).

### 7.4 Sampling + validation protocol

1. Before `--apply`: run `--dry-run`, sample **10** of the files it
   flags (spread across full/minimal/hybrid boundary cases, not just the
   first 10 alphabetically), and manually diff each against this
   document's field mapping table to confirm the tool's output matches
   the spec exactly.
2. After `--apply`: run `scripts/instruction21_validate_reconstruction.py`
   (extend its `--commit` handling, or add a `--all` mode, to check
   *every* artist record rather than just the 41 from this instruction)
   to confirm no `sources`/`life`/`descriptors` values changed — the
   migration must be purely additive/structural, never content-changing.
3. Re-run `scripts/quality_gates.py` and `scripts/sitemap_generator.py
   --dry-run` (see §7.6) after `--apply` — schema shape changes should
   not change page output at all (the template already reads
   defensively via `.get()`), so a diff in generated HTML after the
   migration is itself a bug signal, not an expected side effect.
4. `git status --short | awk '{print $1}' | sort | uniq -c` before
   committing — the change count should equal the "would change" count
   from step 1's dry run exactly. A mismatch means the script touched
   files outside its stated scope.

### 7.5 Risk assessment

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Script overwrites existing `cataloguing`/`sources` data on a hybrid record | Low (presence-checked, not blind write) | High (data loss) | §7.4 step 1 manual sample; §7.3 idempotency requirement |
| Store-wide regeneration required after migration touches all 354 files | Certain if pages are regenerated | Low (large diff, no content change) | Do **not** regenerate pages as part of this migration — JSON shape changes are invisible to `.get()`-based template reads (verified: `artist_profile_generator.py` never raises on either shape today). Regenerate only if/when a template change actually depends on the new shape. |
| Collision with Copilot's concurrent artist-JSON edits | Medium — review-queue resolution is still active | Medium (merge conflicts, not data loss, since both are additive) | Run only from a freshly-rebased `main`, after confirming `resolve_instruction20_review_queue.py`'s current batch is fully applied and committed |
| `--apply` run without `--dry-run` review first | Low (gated by script contract) | High | §7.3 refuses-without-dry-run requirement |

### 7.6 Rollback

- The migration commit should be a single, isolated commit (no other
  changes bundled in) specifically so `git revert <sha>` cleanly undoes
  it if `scripts/instruction21_validate_reconstruction.py --all` (once
  extended) or `quality_gates.py` fails post-migration.
- Because every write is additive (new keys/defaults only, per §7.2),
  a revert is safe even if other, unrelated commits have landed on top
  of it in the meantime — nothing downstream can depend on a key that
  didn't exist before the migration.

### 7.7 Explicit boundary

**This document specifies but does not execute the migration.** No
`migrate_artist_schema_v2.py` exists yet; no `--dry-run` has been run;
no artist JSON has been touched by this section. Building and running it
is separately-scoped future work, gated on: (a) Copilot's review-queue
work being fully landed and quiet, (b) a fresh sizing run per §7.1, and
(c) this checklist being reviewed by a human before `--apply` is used for
the first time.
