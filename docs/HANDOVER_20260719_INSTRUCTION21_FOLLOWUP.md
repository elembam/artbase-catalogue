# Claude Handover — 2026-07-19 (Instruction 21 follow-up)

Companion to: `docs/HANDOVER_20260719_INSTRUCTION21.md` (original
Instruction 21 landing, merged as PR #1 / `8cca5c7`).

## Scope of this follow-up

Requested tracks, all on `claude/instruction21-gap-fix`, rebased onto
merged `main`:

1. Validate the 41 reconstructed artist records against Instruction 21
   policy.
2. Produce a conformance report artifact.
3. Refine the schema migration plan into an execution-ready checklist.
4. Run and report verification (sitemap dry-run, quality gates, tests).
5. Keep scope isolated from Copilot-owned files.

## Branch state

```
$ git log --oneline 8cca5c7..HEAD
551c286 docs: refine schema migration plan into an execution-ready checklist
41eed45 test: add Instruction 21 conformance validator + report
```

Base: `main` at `8cca5c7` (merge of PR #1, itself on top of `f9550ca`,
Copilot's review-queue merge). Synced via `git merge --ff-only
origin/main` before starting — no rebase/replay was needed since the
previous branch state was already an ancestor of `main`.

## Changed files (this follow-up only)

```
$ git diff --stat 8cca5c7..HEAD
 artbase_export/data/contributions/instruction21_conformance_report_20260719.md | 140 ++++
 docs/INSTRUCTION21_SCHEMA_MIGRATION_PLAN.md                                    | 141 ++-
 scripts/instruction21_validate_reconstruction.py                               | 180 ++++
 3 files changed, 454 insertions(+), 7 deletions(-)
```

No `artists/*.html`, `artbase_export/data/artists/*.json`, `README.md`,
or any Copilot-owned file touched in this follow-up — only new docs/
scripts/reports. `git status --short` was checked clean before every
`git add` in this session.

## 1–2. Validation + conformance report

New script: `scripts/instruction21_validate_reconstruction.py`. Compares
each of the 41 reconstructed artist JSON records against the
**pre-reconstruction archived HTML** (`git show 9b9814a^:artists/<ID>.html`)
— not the current live page, which `artist_profile_generator.py` has
since rewritten from a different template. Using the live page as ground
truth was tried first and produced 21 false failures for exactly that
reason; documented in the report as a methodology note so it isn't
re-discovered the hard way next time.

```
$ python3 scripts/instruction21_validate_reconstruction.py
Total checked: 41
Pass: 41
Fail: 0
```

Report: `artbase_export/data/contributions/instruction21_conformance_report_20260719.md`
— policy table (P1–P7), full 41-row per-record result table, and one
flagged pre-existing (not Instruction-21-caused) exception: 21 records'
gallery-index sources lack a `citation` key, matching established
precedent in `ART-ABOLINA-1910.json`, and so aren't rendered by the
current Sources-section template (which filters on `citation` being
defined). Remediation suggested in the report (§ "Exception"), not
applied here since it's a store-wide template concern, not specific to
this batch.

## 3. Schema migration plan → execution-ready checklist

`docs/INSTRUCTION21_SCHEMA_MIGRATION_PLAN.md` §7 (new) adds:
- **Fresh cohort sizing** (re-measured today, not reused from the
  original plan draft): 354 total artist records — 328 full-shape
  (92.7%), 17 pure-minimal-shape (4.8%), 9 partially-migrated hybrids
  (2.5%, e.g. `ART-GULBIS-MADARA`, `ART-KEIRE-KRISTINE` — gained a
  `sources[]` array from Instruction 19/20 or the review-queue resolver
  but never the rest of the full shape).
- **Field mapping table** — every minimal/hybrid → full-shape field
  conversion, each with its exact rule (additive-only, never overwrite).
- **Script contract** for the not-yet-built `migrate_artist_schema_v2.py`:
  dry-run-gated, idempotent, fail-closed.
- **Sampling + validation protocol**: manual sample of 10 dry-run hits
  before `--apply`; post-apply re-run of the Instruction 21 validator
  (extended to `--all`) plus quality gates and sitemap dry-run; diff-count
  cross-check before commit.
- **Risk table** and **rollback plan** (single isolated commit; safe to
  `git revert` at any point since every write is additive).
- **Explicit boundary restated**: nothing in §7 has been executed. No
  migration script exists. This is planning only.

## 4. Verification run and reported

```
$ python3 scripts/sitemap_generator.py --dry-run
(dry-run) 731 URLs — 366 passports, 354 artist pages

$ python3 scripts/quality_gates.py
✓ sitemap coverage
✓ changed JSON sanity
✓ internal links
All quality gates passed.

$ python3 scripts/resolve_instruction20_review_queue.py validate
✓ Queue validation passed.

$ python3 -m pytest artbase_export/tests/ -q
107 passed in 0.48s
```

`tests/test_smk_parity.py` was **not** run — it fetches live from
`api.smk.dk` and tests SMK museum field-mapping parity, unrelated to any
file touched by Instruction 21 or this follow-up. Running it would add
an external network dependency to this verification pass for no
relevant coverage.

`resolve_instruction20_review_queue.py validate` was run in its
**read-only** mode only (no `apply`), specifically to confirm the 41
reconstructed records don't break Copilot's review-queue tooling, without
touching any file it owns.

## 5. Scope isolation

Confirmed via `git diff --stat 8cca5c7..HEAD` (above) and a `git status
--short` check before every commit in this session: zero edits to
`README.md`, `scripts/build_instruction20_review_queue.py`,
`scripts/resolve_instruction20_review_queue.py`,
`artbase_export/data/contributions/instruction20_review_queue_20260718.json`,
or any `ART-KEIRE-KRISTINE`/`ART-LIBIETE-1952`-style review-queue
resolution target. No README changes were needed in this follow-up, so
the "separate commit if touched" rule didn't come up.

## Not done in this follow-up (by design)

- `migrate_artist_schema_v2.py` was **not** built or run — §7.7 of the
  migration plan explicitly scopes that to separate future work, gated
  on Copilot's review-queue work being fully landed and quiet plus a
  fresh sizing run.
- No push in this follow-up yet — commits are local to
  `claude/instruction21-gap-fix` pending confirmation this handover looks
  right before pushing/opening a new PR (the original PR #1 is already
  merged and closed).
