#!/usr/bin/env python3
"""
sitemap_generator.py — Regenerate sitemap.xml from what actually exists on disk.

Usage:
    python3 scripts/sitemap_generator.py
    python3 scripts/sitemap_generator.py --dry-run
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BASE_URL  = "https://arsaccordia.com"
TODAY     = date.today().isoformat()


def url(loc: str, lastmod: str, changefreq: str, priority: str) -> str:
    return (
        f"  <url>\n"
        f"    <loc>{BASE_URL}{loc}</loc>\n"
        f"    <lastmod>{lastmod}</lastmod>\n"
        f"    <changefreq>{changefreq}</changefreq>\n"
        f"    <priority>{priority}</priority>\n"
        f"  </url>"
    )


def generate() -> str:
    entries: list[str] = []

    # ── Static hub pages ───────────────────────────────────────────────────────
    static = [
        ("/",                "1.0", "weekly"),
        ("/artworks/",       "0.9", "weekly"),
        ("/artists/",        "0.8", "monthly"),
        ("/artists/latvia/", "0.8", "weekly"),
        ("/artists/sweden/", "0.8", "monthly"),
        ("/collections/",    "0.8", "monthly"),
        ("/collections/lnmm/","0.7","monthly"),
        ("/collections/hansabanka/","0.7","monthly"),
        ("/contributions/",  "0.6", "monthly"),
        ("/about/",          "0.5", "monthly"),
        ("/sitemap/",        "0.3", "monthly"),
    ]
    for loc, pri, freq in static:
        entries.append(url(loc, TODAY, freq, pri))

    # ── Artwork passports (AP-*.html at repo root) ─────────────────────────────
    passports = sorted(REPO_ROOT.glob("AP-2026-*.html"))
    for p in passports:
        entries.append(url(f"/{p.name}", TODAY, "monthly", "0.9"))

    # ── Artist profile pages ───────────────────────────────────────────────────
    artist_pages = sorted((REPO_ROOT / "artists").glob("ART-*.html"))
    for p in artist_pages:
        entries.append(url(f"/artists/{p.name}", TODAY, "monthly", "0.7"))

    body = "\n\n".join(entries)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n\n{body}\n\n</urlset>\n'


def main(dry_run: bool = False) -> None:
    xml = generate()
    total = xml.count("<url>")
    passports = xml.count("AP-2026-")
    artists   = xml.count("/artists/ART-")

    if dry_run:
        print(f"(dry-run) {total} URLs — {passports} passports, {artists} artist pages")
        return

    out = REPO_ROOT / "sitemap.xml"
    out.write_text(xml, encoding="utf-8")
    print(f"✓ {out}  ({total} URLs — {passports} passports, {artists} artist pages)")


if __name__ == "__main__":
    main(dry_run="--dry-run" in sys.argv)
