#!/usr/bin/env python3
"""
wikidata_preflight.py

Preflight checks for QuickStatements (.qs) contribution files.

Default mode checks changed .qs files only. Use --all to check every .qs under
artbase_export/data/contributions.

Checks:
  - Batch-size guardrail (<= 50 command lines per file)
  - Basic command shape (tab-separated, known entity token)
  - P973 reference guardrail (requires S854 and S813 on the line)
  - Duplicate command detection in the checked set
"""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
CONTRIB_DIR = REPO_ROOT / "artbase_export" / "data" / "contributions"


def _changed_qs_files() -> list[Path]:
    proc = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "status", "--porcelain"],
        check=True,
        capture_output=True,
        text=True,
    )
    files: list[Path] = []
    for line in proc.stdout.splitlines():
        if not line:
            continue
        raw = line[3:]
        if " -> " in raw:
            raw = raw.split(" -> ", 1)[1]
        p = REPO_ROOT / raw
        if p.suffix == ".qs" and p.exists():
            files.append(p)
    return sorted(files)


def _all_qs_files() -> list[Path]:
    return sorted(CONTRIB_DIR.glob("*.qs"))


def _is_entity_token(token: str) -> bool:
    return token == "LAST" or token == "CREATE" or token.startswith("Q")


def _command_lines(path: Path) -> list[tuple[int, str]]:
    lines: list[tuple[int, str]] = []
    for idx, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        lines.append((idx, line))
    return lines


def run_checks(files: list[Path], max_batch_size: int) -> int:
    if not files:
        print("No .qs files to check.")
        return 0

    errors: list[str] = []
    seen_commands: set[str] = set()

    for f in files:
        commands = _command_lines(f)
        if len(commands) > max_batch_size:
            errors.append(
                f"{f.relative_to(REPO_ROOT)} has {len(commands)} command lines "
                f"(max allowed: {max_batch_size})"
            )

        for line_no, line in commands:
            parts = line.split("\t")
            if len(parts) < 3:
                errors.append(
                    f"{f.relative_to(REPO_ROOT)}:{line_no} not tab-separated QS command"
                )
                continue
            if not _is_entity_token(parts[0]):
                errors.append(
                    f"{f.relative_to(REPO_ROOT)}:{line_no} unexpected entity token '{parts[0]}'"
                )

            if "\tP973\t" in f"\t{line}\t":
                if "S854" not in parts or "S813" not in parts:
                    errors.append(
                        f"{f.relative_to(REPO_ROOT)}:{line_no} P973 missing S854/S813 refs"
                    )

            if line in seen_commands:
                errors.append(
                    f"{f.relative_to(REPO_ROOT)}:{line_no} duplicate command in checked set"
                )
            seen_commands.add(line)

    if errors:
        print("Wikidata preflight failed:")
        for err in errors:
            print(f"  - {err}")
        return 1

    print(f"✓ Wikidata preflight passed for {len(files)} file(s).")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Run QuickStatements preflight checks")
    parser.add_argument("--all", action="store_true", help="check all .qs files in contributions/")
    parser.add_argument(
        "--max-batch-size",
        type=int,
        default=50,
        help="maximum allowed command lines per .qs file (default: 50)",
    )
    args = parser.parse_args()

    files = _all_qs_files() if args.all else _changed_qs_files()
    return run_checks(files, max_batch_size=args.max_batch_size)


if __name__ == "__main__":
    raise SystemExit(main())
