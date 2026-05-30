#!/usr/bin/env python3
"""
submissions.py — Submission queue moderation for ArtBase.

User submissions are quarantined until a platform_staff reviewer accepts them.
While pending_review:
  - excluded from canonical export
  - excluded from public site
  - never eligible for Wikidata contribution
  - cannot be set to 'confirmed'

On accept:
  - entity becomes publishable (publication_status → published in canonical JSON)
  - attestation becomes active
  - owner_asserted attribution/provenance visible but NOT auto-confirmed

CLI:
    python3 scripts/submissions.py --list-pending
    python3 scripts/submissions.py --review SRC-USER-00001-0001 --accept --reviewer CON-STAFF-001
    python3 scripts/submissions.py --review SRC-USER-00001-0001 --reject \\
        --reason "Duplicate of ART-0123" --reviewer CON-STAFF-001
    python3 scripts/submissions.py --review SRC-USER-00001-0001 --needs-more-info \\
        --reason "Please provide provenance documentation" --reviewer CON-STAFF-001
    python3 scripts/submissions.py --show SRC-USER-00001-0001
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

REPO_ROOT   = Path(__file__).resolve().parent.parent
ARTBASE_PKG = REPO_ROOT / "artbase_export" / "src"
sys.path.insert(0, str(ARTBASE_PKG))

from artbase_export.airtable.schema import SubmissionStatus

DATA_DIR       = REPO_ROOT / "artbase_export" / "data"
SOURCES_DIR    = DATA_DIR / "sources"
ARTISTS_DIR    = DATA_DIR / "artists"
ARTWORKS_DIR   = DATA_DIR / "artworks"
SUBMISSIONS_DIR = DATA_DIR / "submissions"


def load_source(sid: str) -> tuple[Path, dict]:
    """Load a source document from the registry by source_id."""
    for p in SOURCES_DIR.glob("*.json"):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
            if d.get("source_id") == sid:
                return p, d
        except (KeyError, json.JSONDecodeError):
            pass
    return None, None


def save_source(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def find_pending_entities(sid: str) -> list[tuple[str, Path, dict]]:
    """
    Find artist/artwork records that have a pending attestation from this source.
    Returns list of (entity_type, path, record).
    """
    results = []
    for p in sorted(ARTISTS_DIR.glob("ART-*.json")):
        d = json.loads(p.read_text(encoding="utf-8"))
        for att in d.get("attestations", []):
            if att.get("source_id") == sid and att.get("status") == SubmissionStatus.PENDING_REVIEW:
                results.append(("artist", p, d))
                break
    for p in sorted(ARTWORKS_DIR.glob("AP-*.json")):
        d = json.loads(p.read_text(encoding="utf-8"))
        for att in d.get("attestations", []):
            if att.get("source_id") == sid and att.get("status") == SubmissionStatus.PENDING_REVIEW:
                results.append(("artwork", p, d))
                break
    return results


def list_pending() -> None:
    """Print all source documents with status=pending_review."""
    pending = []
    for p in sorted(SOURCES_DIR.glob("*.json")):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
            if d.get("status") == SubmissionStatus.PENDING_REVIEW:
                pending.append(d)
        except (KeyError, json.JSONDecodeError):
            pass

    if not pending:
        print("No pending submissions.")
        return

    print(f"{'Source ID':<28} {'Contributor':<22} {'Submitted':<12} {'Type'}")
    print("-" * 80)
    for d in sorted(pending, key=lambda x: x.get("submitted_at", "")):
        print(
            f"{d['source_id']:<28} "
            f"{d.get('contributor_id',''):<22} "
            f"{d.get('submitted_at',''):<12} "
            f"{d.get('source_type','')}"
        )
        payload_ref = d.get("submission_payload_ref")
        if payload_ref:
            print(f"  payload: {payload_ref}")


def show_submission(sid: str) -> None:
    """Show full details of a submission."""
    path, src = load_source(sid)
    if not src:
        print(f"✗ Submission {sid} not found.")
        sys.exit(1)

    print(json.dumps(src, indent=2, ensure_ascii=False))

    entities = find_pending_entities(sid)
    if entities:
        print(f"\nPending entities ({len(entities)}):")
        for etype, p, d in entities:
            eid = d.get("artbase_id", p.stem)
            print(f"  [{etype}] {eid}: publication_status={d.get('publication_status','')}")


def _apply_review(src: dict, status: str, reviewer: str, reason: str | None) -> dict:
    """Update a source document with review decision."""
    src["status"] = status
    src["reviewed_by"] = reviewer
    src["reviewed_at"] = date.today().isoformat()
    if reason:
        src["review_reason"] = reason
    return src


def _update_entity_status(entities: list, new_status: str) -> None:
    """Update publication_status and attestation status on linked entities."""
    for etype, path, record in entities:
        changed = False
        # Update publication_status
        old_pub = record.get("publication_status")
        if new_status == SubmissionStatus.ACCEPTED:
            record["publication_status"] = "published"
        elif new_status == SubmissionStatus.REJECTED:
            record["publication_status"] = "rejected"
        # else pending → leave as pending
        if record.get("publication_status") != old_pub:
            changed = True

        # Update attestation statuses
        for att in record.get("attestations", []):
            if att.get("status") == SubmissionStatus.PENDING_REVIEW:
                att["status"] = new_status
                changed = True

        if changed:
            path.write_text(
                json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            eid = record.get("artbase_id", path.stem)
            print(f"  ✓ Updated {etype} {eid}: publication_status={record.get('publication_status')}")


def review_submission(sid: str, decision: str, reviewer: str,
                      reason: str | None, dry_run: bool) -> None:
    """
    Accept, reject, or flag a submission for more info.

    decision: 'accepted' | 'rejected' | 'needs_more_info'
    reviewer: must be a CON-ID of a platform_staff contributor
    """
    if decision not in (SubmissionStatus.ACCEPTED, SubmissionStatus.REJECTED,
                        SubmissionStatus.NEEDS_MORE_INFO):
        print(f"✗ Invalid decision '{decision}'.")
        sys.exit(1)

    path, src = load_source(sid)
    if not src:
        print(f"✗ Submission {sid} not found.")
        sys.exit(1)

    if src.get("status") != SubmissionStatus.PENDING_REVIEW:
        print(f"⚠ {sid} is not pending_review (status={src.get('status')!r}). Proceed anyway? [y/N]: ", end="")
        if input().strip().lower() != "y":
            sys.exit(0)

    # Validate reviewer is known (ideally platform_staff)
    reviewer_src = None
    for p in SOURCES_DIR.glob("*.json"):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
            if d.get("contributor_id") == reviewer:
                reviewer_src = d
                break
        except (KeyError, json.JSONDecodeError):
            pass

    if reviewer_src and reviewer_src.get("contributor_type") != "platform_staff":
        print(f"⚠ Reviewer {reviewer} is not platform_staff "
              f"(type={reviewer_src.get('contributor_type')!r}).")
        print("   Only platform_staff can accept/reject submissions. Aborting.")
        sys.exit(1)

    entities = find_pending_entities(sid)

    if dry_run:
        print(f"~ Would set {sid} → {decision} (reviewer={reviewer})")
        print(f"  {len(entities)} entity/entities would be updated")
        return

    updated_src = _apply_review(src, decision, reviewer, reason)
    save_source(path, updated_src)
    print(f"✓ {sid} → {decision}")

    _update_entity_status(entities, decision)

    if decision == SubmissionStatus.ACCEPTED:
        print(f"\n  ℹ Entity is now publishable, but NOT auto-confirmed.")
        print(f"     owner_asserted attestations remain claims — need independent corroboration for confirmed status.")
    elif decision == SubmissionStatus.NEEDS_MORE_INFO:
        print(f"\n  ℹ Submission returned to submitter. Reason: {reason}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Submission queue moderation")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--list-pending", action="store_true",
                       help="Show all pending submissions")
    group.add_argument("--show", metavar="SRC-ID",
                       help="Show full detail of a submission")
    group.add_argument("--review", metavar="SRC-ID",
                       help="Review a pending submission")

    parser.add_argument("--accept", action="store_true",
                        help="Accept the submission (use with --review)")
    parser.add_argument("--reject", action="store_true",
                        help="Reject the submission (use with --review)")
    parser.add_argument("--needs-more-info", action="store_true",
                        help="Return for more info (use with --review)")
    parser.add_argument("--reason", help="Reason for decision (required for reject/needs-more-info)")
    parser.add_argument("--reviewer", metavar="CON-ID",
                        help="Platform staff contributor ID making the decision")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would change without writing")

    args = parser.parse_args()

    if args.list_pending:
        list_pending()

    elif args.show:
        show_submission(args.show)

    elif args.review:
        if not (args.accept or args.reject or args.needs_more_info):
            print("✗ --review requires --accept, --reject, or --needs-more-info")
            sys.exit(1)
        if sum([args.accept, args.reject, args.needs_more_info]) > 1:
            print("✗ Specify only one of --accept, --reject, --needs-more-info")
            sys.exit(1)
        if not args.reviewer:
            print("✗ --review requires --reviewer CON-ID")
            sys.exit(1)
        if (args.reject or args.needs_more_info) and not args.reason:
            print("✗ --reject and --needs-more-info require --reason")
            sys.exit(1)

        if args.accept:
            decision = SubmissionStatus.ACCEPTED
        elif args.reject:
            decision = SubmissionStatus.REJECTED
        else:
            decision = SubmissionStatus.NEEDS_MORE_INFO

        review_submission(args.review, decision, args.reviewer, args.reason, args.dry_run)


if __name__ == "__main__":
    main()
