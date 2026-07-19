#!/usr/bin/env python3
"""
build_instruction20_review_queue.py

Build a deterministic, human-resolution review queue for Instruction 20
from the corrected Imago Mundi extraction and current artist store.

Rule:
  - Exclude already matched artists (name_lv + birth_year where artist record
    already has source_id SRC-IMAGOMUNDI-LV-2014)
  - Remaining entries where surname collides with existing store surname
    become review-queue entries.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INPUT = REPO_ROOT / "ArsAccordiaClaude" / "References" / "imago-mundi-latvia-2014-corrected.json"
DEFAULT_ARTISTS_DIR = REPO_ROOT / "artbase_export" / "data" / "artists"
DEFAULT_OUTPUT = (
    REPO_ROOT
    / "artbase_export"
    / "data"
    / "contributions"
    / "instruction20_review_queue_20260718.json"
)


def _norm(s: str | None) -> str:
    trans = str.maketrans("āčēģīķļņšūž", "acegiklnsuz")
    return " ".join((s or "").strip().lower().translate(trans).split())


def _surname(s: str | None) -> str:
    tokens = _norm(s).split()
    return tokens[-1] if tokens else ""


def _load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def build_review_queue(
    corrected_path: Path,
    artists_dir: Path,
) -> dict:
    corrected = _load_json(corrected_path)
    artist_files = sorted(artists_dir.glob("ART-*.json"))
    artists = [_load_json(p) for p in artist_files]

    # Matched set (already enriched by Instruction 20)
    matched_keys: set[tuple[str, str]] = set()
    all_store_artists: list[dict] = []
    for artist in artists:
        preferred_name = (artist.get("identity") or {}).get("preferred_name") or ""
        birth_year = str(((artist.get("life") or {}).get("birth_date") or {}).get("value") or "")
        artbase_id = artist.get("artbase_id") or ""
        all_store_artists.append(
            {
                "artbase_id": artbase_id,
                "preferred_name": preferred_name,
                "birth_year": birth_year,
                "surname": _surname(preferred_name),
            }
        )
        if any(
            isinstance(src, dict) and src.get("source_id") == "SRC-IMAGOMUNDI-LV-2014"
            for src in (artist.get("sources") or [])
        ):
            matched_keys.add((_norm(preferred_name), birth_year))

    # Remaining extraction entries
    remaining = [
        item
        for item in corrected
        if (_norm(item.get("name_lv")), str(item.get("birth_year") or "")) not in matched_keys
    ]

    surname_index: dict[str, list[dict]] = {}
    for candidate in all_store_artists:
        surname_index.setdefault(candidate["surname"], []).append(candidate)

    queue_items = []
    for item in remaining:
        surname = _surname(item.get("name_lv"))
        candidates = surname_index.get(surname, [])
        if not candidates:
            continue
        queue_items.append(
            {
                "name_lv": item.get("name_lv"),
                "name_en": item.get("name_en"),
                "birth_year": str(item.get("birth_year") or ""),
                "pdf_page": item.get("pdf_page"),
                "printed_pages": item.get("printed_pages") or [],
                "record_id": item.get("record_id"),
                "reason": "surname_collision_with_existing_artist_store",
                "status": "needs_human_resolution",
                "decision": None,
                "decision_notes": None,
                "candidates": [
                    {
                        "artbase_id": c["artbase_id"],
                        "preferred_name": c["preferred_name"],
                        "birth_year": c["birth_year"] or None,
                    }
                    for c in sorted(candidates, key=lambda x: (x["preferred_name"], x["artbase_id"]))
                ],
            }
        )

    queue_items.sort(key=lambda x: (x["name_lv"] or "", x["birth_year"]))
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_dataset": str(corrected_path.relative_to(REPO_ROOT)),
        "method": "instruction20_review_queue_from_surname_collision_v1",
        "counts": {
            "corrected_total": len(corrected),
            "matched_existing": len(matched_keys),
            "review_queue": len(queue_items),
            "remaining_non_review": len(remaining) - len(queue_items),
        },
        "items": queue_items,
    }
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Instruction 20 review queue JSON")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="corrected extraction JSON")
    parser.add_argument("--artists-dir", type=Path, default=DEFAULT_ARTISTS_DIR, help="artists JSON directory")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT, help="output review-queue JSON path")
    parser.add_argument(
        "--expected-count",
        type=int,
        default=23,
        help="expected review queue size; exits non-zero if mismatched",
    )
    args = parser.parse_args()

    payload = build_review_queue(corrected_path=args.input, artists_dir=args.artists_dir)
    actual = payload["counts"]["review_queue"]
    if args.expected_count is not None and actual != args.expected_count:
        print(f"✗ review queue size mismatch: expected {args.expected_count}, got {actual}")
        return 1

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✓ wrote {args.out} ({actual} items)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
