# ArtBase Copilot Handover — 2026-07-19 (Instruction 20 progress)

## Scope
This handover captures the current implementation and decision status for:
- Spec: `ArsAccordiaClaude/copilot-spec-20-imago-mundi-catalogue.md`
- Instruction 20 review-queue workflow and first decision batch

---

## Current state summary

### Completed implementation in this working session
- Added quality gate script: `scripts/quality_gates.py`
- Added Wikidata QS preflight script: `scripts/wikidata_preflight.py`
- Added review queue builder: `scripts/build_instruction20_review_queue.py`
- Added review queue resolver/apply workflow:
  - `scripts/resolve_instruction20_review_queue.py`
- Updated usage docs in `README.md` for all of the above.

### Generated artifacts
- Review queue JSON:
  - `artbase_export/data/contributions/instruction20_review_queue_20260718.json`
  - Deterministic queue size: 23 items

### Health checks (latest run)
- `python3 scripts/quality_gates.py` → ✅ pass
- `python3 scripts/resolve_instruction20_review_queue.py summary` → ✅ works
- `python3 scripts/resolve_instruction20_review_queue.py validate` → ✅ pass

---

## Instruction 20 review-queue decision progress

Queue totals right now:
- `approved_match`: **2**
- `deferred_new_artist`: **9**
- `needs_human_resolution`: **12**

### Decisions already recorded

#### approved_match (2)
1. `IMLV-106` → `match_existing` to `ART-LIBIETE-1952`
2. `IMLV-080` → `match_existing` to `ART-KEIRE-KRISTINE`

#### deferred_new_artist (9)
1. `IMLV-190`
2. `IMLV-059`
3. `IMLV-119`
4. `IMLV-074`
5. `IMLV-128`
6. `IMLV-161`
7. `IMLV-075`
8. `IMLV-136`
9. `IMLV-058`

### Remaining undecided
- **12 items** still `needs_human_resolution`.

---

## Where the previous run stopped

The item-by-item workflow was in progress and stopped while prompting for:
- `IMLV-026` (Kristians Brekte vs ART-BREKTE-1920)

Recommended action on resume:
1. Continue decision capture via:
   - `python3 scripts/resolve_instruction20_review_queue.py decide ... --apply`
2. After enough `approved_match` items are collected, apply them with:
   - `python3 scripts/resolve_instruction20_review_queue.py apply --apply`
3. Re-run:
   - `python3 scripts/quality_gates.py`

---

## Working tree status (uncommitted)

Modified:
- `README.md`

Untracked:
- `artbase_export/data/contributions/instruction20_review_queue_20260718.json`
- `docs/HANDOVER_20260718_INSTRUCTION20.md`
- `scripts/build_instruction20_review_queue.py`
- `scripts/quality_gates.py`
- `scripts/resolve_instruction20_review_queue.py`
- `scripts/wikidata_preflight.py`

This handover file:
- `docs/HANDOVER_20260719_REVIEW_QUEUE_PROGRESS.md`

