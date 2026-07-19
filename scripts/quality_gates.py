#!/usr/bin/env python3
"""
quality_gates.py — lightweight preflight checks for static site/data integrity.

Checks:
1) sitemap contains all generated AP-*.html and artists/ART-*.html pages
2) sitemap URLs for AP/artist pages resolve to files on disk
3) changed HTML files do not contain broken internal links
4) changed canonical JSON files parse and contain core required keys

Usage:
    python3 scripts/quality_gates.py
    python3 scripts/quality_gates.py --all-html
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse


REPO_ROOT = Path(__file__).resolve().parent.parent
SITEMAP_PATH = REPO_ROOT / "sitemap.xml"
BASE_URL = "https://arsaccordia.com"
HREF_RE = re.compile(r'href="([^"]+)"')
LOC_RE = re.compile(r"<loc>([^<]+)</loc>")


def _git_changed_files() -> list[Path]:
    proc = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "status", "--porcelain"],
        check=True,
        capture_output=True,
        text=True,
    )
    changed: list[Path] = []
    for line in proc.stdout.splitlines():
        if not line:
            continue
        # format: XY <path> or XY <old> -> <new>
        raw = line[3:]
        if " -> " in raw:
            raw = raw.split(" -> ", 1)[1]
        changed.append(REPO_ROOT / raw)
    return changed


def _load_sitemap_paths() -> set[str]:
    if not SITEMAP_PATH.exists():
        raise FileNotFoundError(f"Missing sitemap.xml at {SITEMAP_PATH}")
    text = SITEMAP_PATH.read_text(encoding="utf-8")
    paths: set[str] = set()
    for loc in LOC_RE.findall(text):
        if loc.startswith(BASE_URL):
            p = loc[len(BASE_URL) :]
            paths.add(p if p.startswith("/") else f"/{p}")
    return paths


def _resolve_site_path(path: str) -> Path:
    clean = path.split("#", 1)[0].split("?", 1)[0]
    rel = clean.lstrip("/")
    candidate = REPO_ROOT / rel
    if clean.endswith("/"):
        return candidate / "index.html"
    if candidate.is_dir():
        return candidate / "index.html"
    return candidate


def check_sitemap_coverage() -> list[str]:
    errors: list[str] = []
    sitemap_paths = _load_sitemap_paths()

    expected_ap = {f"/{p.name}" for p in sorted(REPO_ROOT.glob("AP-2026-*.html"))}
    expected_art = {
        f"/artists/{p.name}" for p in sorted((REPO_ROOT / "artists").glob("ART-*.html"))
    }

    missing_ap = sorted(expected_ap - sitemap_paths)
    missing_art = sorted(expected_art - sitemap_paths)
    if missing_ap:
        errors.append(f"sitemap missing {len(missing_ap)} passport URLs")
    if missing_art:
        errors.append(f"sitemap missing {len(missing_art)} artist URLs")

    for path in sorted(sitemap_paths):
        if path.startswith("/AP-2026-") or path.startswith("/artists/ART-"):
            resolved = _resolve_site_path(path)
            if not resolved.exists():
                errors.append(f"sitemap URL points to missing file: {path}")

    return errors


def _iter_html_targets(all_html: bool) -> list[Path]:
    if all_html:
        return sorted(REPO_ROOT.glob("AP-2026-*.html")) + sorted(
            (REPO_ROOT / "artists").glob("ART-*.html")
        )

    changed = _git_changed_files()
    return sorted([p for p in changed if p.suffix.lower() == ".html" and p.exists()])


def _is_ignorable_link(href: str) -> bool:
    if not href:
        return True
    if href.startswith(("#", "mailto:", "tel:", "javascript:", "data:")):
        return True
    parsed = urlparse(href)
    return parsed.scheme in ("http", "https")


def _resolve_href(current_file: Path, href: str) -> Path:
    clean = href.split("#", 1)[0].split("?", 1)[0]
    if clean.startswith("/"):
        return _resolve_site_path(clean)
    rel = (current_file.parent / clean).resolve()
    if clean.endswith("/") or rel.is_dir():
        return rel / "index.html"
    return rel


def check_internal_links(all_html: bool) -> list[str]:
    errors: list[str] = []
    targets = _iter_html_targets(all_html=all_html)
    if not targets:
        return errors

    for html_file in targets:
        text = html_file.read_text(encoding="utf-8", errors="replace")
        for href in HREF_RE.findall(text):
            if _is_ignorable_link(href):
                continue
            resolved = _resolve_href(html_file, href)
            if not resolved.exists():
                errors.append(
                    f"broken link in {html_file.relative_to(REPO_ROOT)} -> {href}"
                )
    return errors


def check_changed_json() -> list[str]:
    errors: list[str] = []
    changed = _git_changed_files()
    json_targets = [
        p
        for p in changed
        if p.suffix.lower() == ".json"
        and "artbase_export/data/" in str(p)
        and p.exists()
    ]

    required_keys_by_bucket = {
        "artists": ("artbase_id", "identity", "life"),
        "artworks": ("artbase_id", "object_id", "rights"),
        "sources": ("source_id", "citation", "title"),
    }

    for path in json_targets:
        rel = path.relative_to(REPO_ROOT)
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"invalid JSON {rel}: {exc}")
            continue

        bucket = None
        for key in required_keys_by_bucket:
            marker = f"/{key}/"
            if marker in f"/{rel.as_posix()}":
                bucket = key
                break
        if not bucket:
            continue

        missing = [k for k in required_keys_by_bucket[bucket] if k not in data]
        if missing:
            errors.append(f"{rel} missing required keys: {', '.join(missing)}")
            continue

        # Legacy-compatible source container checks.
        if bucket in {"artists", "artworks"}:
            has_sources = "sources" in data and isinstance(data.get("sources"), list)
            has_source_refs = "source_refs" in data and isinstance(data.get("source_refs"), list)
            if not (has_sources or has_source_refs):
                errors.append(
                    f"{rel} missing source container (expected sources[] or source_refs[])"
                )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Run static-site/data quality gates")
    parser.add_argument(
        "--all-html",
        action="store_true",
        help="scan all AP/artist HTML files for internal broken links (default: changed files only)",
    )
    args = parser.parse_args()

    checks = [
        ("sitemap coverage", check_sitemap_coverage),
        ("changed JSON sanity", check_changed_json),
        ("internal links", lambda: check_internal_links(args.all_html)),
    ]

    all_errors: list[str] = []
    for label, fn in checks:
        errors = fn()
        if errors:
            print(f"✗ {label}: {len(errors)} issue(s)")
            all_errors.extend(errors)
        else:
            print(f"✓ {label}")

    if all_errors:
        print("\nIssues:")
        for err in all_errors:
            print(f"  - {err}")
        return 1

    print("\nAll quality gates passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
