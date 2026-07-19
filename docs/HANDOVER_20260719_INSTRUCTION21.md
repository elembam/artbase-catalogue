# Claude Handover — 2026-07-19 (Instruction 21: HTML-without-JSON gap)

## Scope
- Task: remediate the HTML-without-JSON pipeline gap deferred from
  Instruction 20 (`artbase_export/data/contributions/instruction20_imago_reconciliation_reports_20260718.md`,
  section C).
- Branch: `claude/instruction21-gap-fix` (isolated git worktree at
  `.claude/worktrees/claude+instruction21-gap-fix`, branched from local
  `main` at commit `c896967`, which already includes the Instruction 20
  Imago Mundi batch — 31 enriched artists + 31 new artworks).
- Coordination: per the stated file-ownership split, this branch touches
  only `artists/*.html`, `artbase_export/data/artists/*.json`,
  `templates/artist_profile.html.j2`, `sitemap.xml`, and new `docs/`
  files. Nothing under `artbase_export/data/contributions/instruction20_review_queue_20260718.json`,
  `scripts/resolve_instruction20_review_queue.py`,
  `scripts/build_instruction20_review_queue.py`, or `README.md` was
  touched — those remain Copilot's, currently uncommitted in the shared
  main working directory (not this worktree).

## What was found

The "HTML-without-JSON gap" was **42 artist pages** with no backing
canonical JSON (not ~19 as earlier-session estimates suggested — that
figure came from a narrower Imago-Mundi-name-only cross-check).
Root-caused via `git log --all -- <path>` on a sample file:

- Commit `daf45ed` (2026-06-02, "Remove 58 living artists (born ≥1950, no
  death date) to reduce Airtable usage") deliberately deleted 58 living
  artists' JSON records to manage an Airtable free-plan quota constraint.
  It touched **only** `.json` files — zero HTML deletions.
- 17 of those 58 were later legitimately re-added under other work
  (Hansabanka batch, this month's Imago Mundi batch, etc.) and are fine.
- The other **41** were never re-added: their HTML stayed live
  (`Exported 2026-05-30` in the footer of every one) with no canonical
  record behind them — unauditable, un-regenerable, and invisible to any
  script that walks `data/artists/*.json`.
- One of the 42, `ART-KAULACA-1971` (Vineta Kaulača, b.1971), turned out
  to be a **true duplicate**: same person, same birth year, already
  present under a different, actively-maintained ID
  (`ART-KAULACA-VINETA`, enriched in the Instruction 20 batch). A
  name+birth-year cross-check against the whole store (not just exact
  string match) found no other hidden duplicates among the remaining 41.
  A second near-miss, `ART-EGLITIS-1981`, was checked and ruled a
  **namesake**, not a duplicate — different birth year (1981 vs. the
  existing `ART-EGLITIS-1959`) and different origin source.

Given the deletion was a deliberate resource-management decision rather
than a data-quality correction, I surfaced this to the user before acting
further and confirmed the remediation approach (see decision below)
rather than assuming either "just restore everything" or "the pages
should never have stayed live."

## Decision (confirmed with user)

Restore lightweight JSON backing for the 41 genuine orphans. Each
reconstructed record re-encodes **only** what the already-published page
already displays (name, birth year, and — for ~21 of the 41 whose older
template captured it — a Galerija Jēkabs origin URL), explicitly flagged
`status: "working"` / gallery-sourced / not independently confirmed, and
kept outside the Airtable-driven pipeline so it doesn't reintroduce the
load `daf45ed` was managing. Nothing beyond what was already live is
asserted; genuinely unrecoverable fields (e.g. origin URL for the ~20
pages whose template never captured one) are left `null`, not guessed.

## What was done

1. Reconstructed JSON for all 41 genuine orphans
   (`artbase_export/data/artists/*.json`, full schema shape — see
   migration plan doc for what "full shape" means).
2. Retired `artists/ART-KAULACA-1971.html` as a redirect stub (meta
   refresh + canonical link) to `/artists/ART-KAULACA-VINETA.html`
   instead of deleting it outright, so any existing inbound link doesn't
   404.
3. Added a **Biography** section to `templates/artist_profile.html.j2` —
   Instruction 20 introduced `artist.biography` (31 Imago Mundi artists)
   but the template never rendered it, so that content was invisible on
   every one of those 31 live pages until this fix.
4. Regenerated all 72 affected artist pages (31 Imago Mundi + 41
   gap-reconstructed) and `sitemap.xml`.
5. Wrote `docs/INSTRUCTION21_SCHEMA_MIGRATION_PLAN.md`: inventories the
   two artist-JSON shapes and three HTML template generations found
   during this work, proposes a target schema (`biography` stays a
   single object, not an array, until a second biographical source
   actually exists), and specifies — but does not execute — a
   store-wide `migrate_artist_schema_v2.py` for a future, separately
   reviewed pass.
6. Committed to `claude/instruction21-gap-fix` (117 files, commit
   `456f3c5`). **Not merged to main, not pushed.**

## Verified before committing

- `git status --short` scope checked before `git add` — confirmed zero
  overlap with Copilot's in-progress uncommitted files.
- Cross-checked all 42 gap IDs by normalized-name + birth-year against
  the full store (not just exact string match) before treating any as a
  genuine orphan.
- Spot-read multiple raw archived HTML pages directly (not just regex
  output) to confirm the "Exported 2026-05-30" / Galerija Jēkabs pattern
  held before generalizing it into the reconstruction script.

## Remaining / next steps

- **Merge order**: per the stated plan, merge Copilot's
  `copilot/review-queue-batch1` first (smaller diff, lower risk), then
  rebase this branch (`claude/instruction21-gap-fix`) on the result
  before merging to `main`.
- **Schema migration** (`migrate_artist_schema_v2.py`): specified in the
  migration plan doc, not built or run. Should happen in its own
  reviewed pass after both branches land, since it's a store-wide
  structural change.
- **Re-measure the minimal-shape cohort** at that time — both this
  branch and Copilot's are actively adding/touching artist JSON, so the
  exact count will have moved.
- No Wikidata edits, no Airtable writes, and no image ingestion were
  part of this instruction — none were needed.

## Working tree / branch status

- Worktree: `.claude/worktrees/claude+instruction21-gap-fix`
- Branch: `claude/instruction21-gap-fix`, 1 commit ahead of the `c896967`
  base (`456f3c5`)
- Working tree in the worktree: clean after commit
- Main repo working directory (shared, not this worktree): still has
  Copilot's uncommitted review-queue changes (`README.md`,
  `ART-KEIRE-KRISTINE.json`, `ART-LIBIETE-1952.json`, plus new
  scripts/docs) — untouched by this work, as agreed.
