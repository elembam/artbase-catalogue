#!/usr/bin/env python3
"""
resolve_instruction20_review_queue.py

Operational workflow for Instruction 20 human-review queue decisions.

This script does NOT auto-enrich or create artists. It manages:
  1) decision capture on queue items
  2) validated application of approved match decisions into canonical artist JSON
     as explicit resolved conflict records.
"""

from __future__ import annotations

import argparse
import copy
import json
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_QUEUE = (
    REPO_ROOT
    / "artbase_export"
    / "data"
    / "contributions"
    / "instruction20_review_queue_20260718.json"
)
ARTISTS_DIR = REPO_ROOT / "artbase_export" / "data" / "artists"
SOURCE_ID = "SRC-IMAGOMUNDI-LV-2014"


DECISION_MATCH = "match_existing"
DECISION_DEFER_NEW = "defer_new_artist"
DECISION_REJECT = "reject_collision"
VALID_DECISIONS = {DECISION_MATCH, DECISION_DEFER_NEW, DECISION_REJECT}

STATUS_NEEDS_HUMAN = "needs_human_resolution"
STATUS_APPROVED_MATCH = "approved_match"
STATUS_DEFERRED_NEW = "deferred_new_artist"
STATUS_REJECTED = "rejected_collision"
STATUS_APPLIED = "applied"


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _today() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def _index_by_record_id(items: list[dict]) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for item in items:
        rid = item.get("record_id")
        if rid:
            out[rid] = item
    return out


def validate_queue(queue: dict) -> list[str]:
    errors: list[str] = []
    items = queue.get("items") or []

    for idx, item in enumerate(items, start=1):
        where = f"items[{idx}]/{item.get('record_id', '?')}"
        status = item.get("status")
        decision = item.get("decision")

        if decision is None:
            if status != STATUS_NEEDS_HUMAN:
                errors.append(f"{where}: undecided item must have status '{STATUS_NEEDS_HUMAN}'")
            continue

        action = decision.get("action")
        reviewer = decision.get("reviewer")
        if action not in VALID_DECISIONS:
            errors.append(f"{where}: invalid decision.action '{action}'")
            continue
        if not reviewer:
            errors.append(f"{where}: decision.reviewer is required")

        candidate_ids = {c.get("artbase_id") for c in (item.get("candidates") or []) if c.get("artbase_id")}
        selected_id = decision.get("selected_artbase_id")

        if action == DECISION_MATCH:
            if not selected_id:
                errors.append(f"{where}: match_existing requires decision.selected_artbase_id")
            elif selected_id not in candidate_ids:
                errors.append(
                    f"{where}: selected_artbase_id '{selected_id}' not in candidate list"
                )
            if status not in {STATUS_APPROVED_MATCH, STATUS_APPLIED}:
                errors.append(
                    f"{where}: match_existing must use status '{STATUS_APPROVED_MATCH}' or '{STATUS_APPLIED}'"
                )
        else:
            if selected_id is not None:
                errors.append(f"{where}: {action} must not set selected_artbase_id")
            expected = STATUS_DEFERRED_NEW if action == DECISION_DEFER_NEW else STATUS_REJECTED
            if status != expected:
                errors.append(f"{where}: {action} must use status '{expected}'")

    return errors


def print_summary(queue: dict) -> None:
    items = queue.get("items") or []
    by_status: dict[str, int] = {}
    by_action: dict[str, int] = {}
    for item in items:
        status = item.get("status") or "unknown"
        by_status[status] = by_status.get(status, 0) + 1
        decision = item.get("decision")
        if decision:
            action = decision.get("action") or "unknown"
            by_action[action] = by_action.get(action, 0) + 1

    print("Queue summary")
    print("-----------")
    print(f"items: {len(items)}")
    print("status counts:")
    for k in sorted(by_status):
        print(f"  {k}: {by_status[k]}")
    if by_action:
        print("decision action counts:")
        for k in sorted(by_action):
            print(f"  {k}: {by_action[k]}")


def apply_decision_update(
    queue: dict,
    record_id: str,
    action: str,
    reviewer: str,
    notes: str | None,
    selected_artbase_id: str | None,
) -> dict:
    updated = copy.deepcopy(queue)
    items = updated.get("items") or []
    idx = _index_by_record_id(items)
    item = idx.get(record_id)
    if not item:
        raise ValueError(f"record_id '{record_id}' not found in queue")

    if action not in VALID_DECISIONS:
        raise ValueError(f"invalid action '{action}'")

    if action == DECISION_MATCH and not selected_artbase_id:
        raise ValueError("match_existing requires --selected-artbase-id")
    if action != DECISION_MATCH and selected_artbase_id is not None:
        raise ValueError(f"{action} does not accept --selected-artbase-id")

    candidate_ids = {c.get("artbase_id") for c in (item.get("candidates") or []) if c.get("artbase_id")}
    if action == DECISION_MATCH and selected_artbase_id not in candidate_ids:
        raise ValueError(
            f"selected artist '{selected_artbase_id}' is not in this item's candidate list"
        )

    status = {
        DECISION_MATCH: STATUS_APPROVED_MATCH,
        DECISION_DEFER_NEW: STATUS_DEFERRED_NEW,
        DECISION_REJECT: STATUS_REJECTED,
    }[action]
    item["status"] = status
    item["decision"] = {
        "action": action,
        "selected_artbase_id": selected_artbase_id if action == DECISION_MATCH else None,
        "reviewer": reviewer,
        "decided_at": _now_iso(),
    }
    item["decision_notes"] = notes
    return updated


def _artist_path(artbase_id: str) -> Path:
    return ARTISTS_DIR / f"{artbase_id}.json"


def _ensure_conflict(artist: dict, queue_item: dict) -> bool:
    """
    Add resolved conflict marker for an applied queue item.
    Returns True if artist changed.
    """
    conflicts = artist.setdefault("conflicts", [])
    record_id = queue_item.get("record_id")
    if not record_id:
        return False

    for c in conflicts:
        if (
            isinstance(c, dict)
            and c.get("field") == "instruction20.review_queue"
            and any(isinstance(v, dict) and v.get("record_id") == record_id for v in (c.get("values") or []))
        ):
            return False

    decision = queue_item.get("decision") or {}
    values = [
        {
            "value": f"{queue_item.get('name_lv')} ({queue_item.get('birth_year')})",
            "source_id": SOURCE_ID,
            "record_id": record_id,
            "pdf_page": queue_item.get("pdf_page"),
        }
    ]
    conflicts.append(
        {
            "field": "instruction20.review_queue",
            "values": values,
            "status": "resolved",
            "created": _today(),
            "resolved_by": decision.get("reviewer"),
            "resolution": (
                f"Instruction 20 review queue: resolved as match_existing to "
                f"{decision.get('selected_artbase_id')}"
            ),
        }
    )
    return True


def apply_approved_matches(queue: dict, dry_run: bool) -> tuple[dict, int, int]:
    """
    Apply approved match decisions to canonical artist JSON files.
    Returns (updated_queue, applied_count, changed_artist_count).
    """
    updated = copy.deepcopy(queue)
    applied_count = 0
    artist_changed = 0

    for item in updated.get("items") or []:
        if item.get("status") != STATUS_APPROVED_MATCH:
            continue
        decision = item.get("decision") or {}
        selected_id = decision.get("selected_artbase_id")
        if not selected_id:
            continue
        artist_path = _artist_path(selected_id)
        if not artist_path.exists():
            raise FileNotFoundError(f"selected artist file not found: {artist_path}")

        artist = _load_json(artist_path)
        changed = _ensure_conflict(artist, item)
        if changed and not dry_run:
            _write_json(artist_path, artist)
            artist_changed += 1
        elif changed:
            artist_changed += 1

        item["status"] = STATUS_APPLIED
        item["applied_at"] = _now_iso()
        item["applied_to_artbase_id"] = selected_id
        applied_count += 1

    return updated, applied_count, artist_changed


def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve/apply Instruction 20 review queue decisions")
    parser.add_argument("--queue", type=Path, default=DEFAULT_QUEUE, help="review queue JSON path")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("summary", help="show queue status summary")

    decide = sub.add_parser("decide", help="record a human decision for one queue entry")
    decide.add_argument("--record-id", required=True, help="queue item record_id (e.g. IMLV-074)")
    decide.add_argument(
        "--action",
        required=True,
        choices=sorted(VALID_DECISIONS),
        help="decision action",
    )
    decide.add_argument("--selected-artbase-id", help="required for action=match_existing")
    decide.add_argument("--reviewer", required=True, help="reviewer identifier")
    decide.add_argument("--notes", help="optional decision notes")
    decide.add_argument("--apply", action="store_true", help="write queue file (default dry-run)")

    apply_cmd = sub.add_parser(
        "apply", help="apply approved_match decisions into artist records and mark queue items applied"
    )
    apply_cmd.add_argument("--apply", action="store_true", help="write changes (default dry-run)")

    validate_cmd = sub.add_parser("validate", help="validate queue consistency")
    validate_cmd.add_argument("--strict", action="store_true", help="exit 1 if any item remains unresolved")

    args = parser.parse_args()
    queue = _load_json(args.queue)

    if args.cmd == "summary":
        errors = validate_queue(queue)
        if errors:
            print(f"Queue has {len(errors)} validation issue(s):")
            for err in errors:
                print(f"  - {err}")
            return 1
        print_summary(queue)
        return 0

    if args.cmd == "validate":
        errors = validate_queue(queue)
        if args.strict:
            unresolved = sum(1 for i in (queue.get("items") or []) if i.get("status") == STATUS_NEEDS_HUMAN)
            if unresolved:
                errors.append(f"{unresolved} item(s) still unresolved")
        if errors:
            print("Queue validation failed:")
            for err in errors:
                print(f"  - {err}")
            return 1
        print("✓ Queue validation passed.")
        return 0

    if args.cmd == "decide":
        updated = apply_decision_update(
            queue=queue,
            record_id=args.record_id,
            action=args.action,
            reviewer=args.reviewer,
            notes=args.notes,
            selected_artbase_id=args.selected_artbase_id,
        )
        errors = validate_queue(updated)
        if errors:
            print("Decision update produced invalid queue state:")
            for err in errors:
                print(f"  - {err}")
            return 1
        if args.apply:
            _write_json(args.queue, updated)
            print(f"✓ decision written for {args.record_id}")
        else:
            print(f"~ dry-run: decision would be written for {args.record_id}")
        return 0

    if args.cmd == "apply":
        errors = validate_queue(queue)
        if errors:
            print("Queue must validate before apply:")
            for err in errors:
                print(f"  - {err}")
            return 1
        dry_run = not args.apply
        updated_queue, applied_count, artist_changed = apply_approved_matches(queue, dry_run=dry_run)
        if args.apply:
            _write_json(args.queue, updated_queue)
            print(
                f"✓ applied {applied_count} queue item(s); "
                f"updated {artist_changed} artist file(s); queue persisted"
            )
        else:
            print(
                f"~ dry-run: would apply {applied_count} queue item(s) "
                f"and update {artist_changed} artist file(s)"
            )
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
