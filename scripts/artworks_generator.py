#!/usr/bin/env python3
"""
artworks_generator.py — Regenerate artworks/index.html from canonical JSON.

Produces the flat passport-list page at arsaccordia.com/artworks/,
preserving the established design (OID score bar, "View →" rows).

Usage:
    python3 scripts/artworks_generator.py
    python3 scripts/artworks_generator.py --dry-run
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR   = Path(__file__).resolve().parent
REPO_ROOT    = SCRIPT_DIR.parent
ARTWORKS_DIR = REPO_ROOT / "artbase_export" / "data" / "artworks"
OUT_PATH     = REPO_ROOT / "artworks" / "index.html"


def oid_score(aw: dict) -> int:
    """Count filled Object ID fields (max 9, per ICOM Object ID standard)."""
    oid = aw.get("object_id", {})
    fields = [
        oid.get("title"),
        oid.get("object_type"),
        oid.get("materials"),
        oid.get("dimensions_display") or (oid.get("height_cm") and oid.get("width_cm")),
        oid.get("inscriptions"),
        oid.get("distinguishing_features"),
        oid.get("subject"),
        oid.get("date_display"),
        oid.get("maker_display_name") or oid.get("maker_id"),
    ]
    return sum(1 for f in fields if f)


def oid_class(score: int) -> str:
    if score >= 9:
        return "complete"
    if score >= 5:
        return "partial"
    return "draft"


def oid_label(score: int) -> str:
    if score >= 9:
        return "Complete"
    if score >= 5:
        return "Partial"
    return "Draft"


def passport_row(aw: dict) -> str:
    oid   = aw.get("object_id", {})
    aid   = aw.get("artbase_id", "")
    title = oid.get("title") or "Untitled"
    title_en = oid.get("title_en") or ""
    display_title = f"{title}" + (f" ({title_en})" if title_en and title_en != title else "")
    artist = oid.get("maker_display_name") or oid.get("maker_id") or ""
    date   = oid.get("date_display") or ""
    score  = oid_score(aw)
    cls    = oid_class(score)
    label  = oid_label(score)
    pct    = round(score / 9 * 100)

    return f"""\
    <a href="../{aid}.html" class="passport-item">
      <span class="passport-id">{aid}</span>
      <div class="passport-thumb"></div>
      <span class="passport-title">{display_title}</span>
      <span class="passport-artist">{artist}</span>
      <span class="passport-date">{date}</span>
      <div class="oid-score">
        <div class="oid-score-header">
          <span class="oid-score-num">{score}</span><span class="oid-score-denom">/9</span>
          <span class="oid-tag {cls}" style="margin-left:5px;">{label}</span>
        </div>
        <div class="oid-bar-wrap"><div class="oid-bar {cls}" style="width:{pct}%"></div></div>
      </div>
      <span class="passport-arrow">View →</span>
    </a>"""


def generate(artworks: list[dict], generated_at: str) -> str:
    count = len(artworks)
    rows  = "\n".join(passport_row(aw) for aw in artworks)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="Ars Accordia — All Artwork Passports. Standards-compliant identity records for European art.">
<title>Artwork Passports — Ars Accordia</title>
<link rel="canonical" href="https://arsaccordia.com/artworks/">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght,SOFT,WONK@9..144,300..900,0..100,0..1&family=Public+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  :root {{
    --paper:      #f6f1e6;
    --paper-deep: #ebe3d1;
    --ink:        #1c1814;
    --ink-soft:   #4a4338;
    --ink-faded:  #80766a;
    --seal:       #6e1818;
    --seal-light: #94342f;
    --gold:       #8a6f2e;
    --rule:       #c7bca5;
    --grid:       rgba(110, 24, 24, 0.04);
  }}

  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  html {{ scroll-behavior: smooth; }}

  body {{
    background: var(--paper);
    background-image:
      linear-gradient(var(--grid) 1px, transparent 1px),
      linear-gradient(90deg, var(--grid) 1px, transparent 1px);
    background-size: 32px 32px;
    color: var(--ink);
    font-family: 'Public Sans', -apple-system, sans-serif;
    font-weight: 400;
    line-height: 1.5;
    font-size: 15px;
    min-height: 100vh;
    padding: 40px 20px 80px;
  }}

  body::before {{
    content: '';
    position: fixed;
    inset: 0;
    pointer-events: none;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='200'%3E%3Cfilter id='n'%3E%3CfeTurbulence baseFrequency='0.9' numOctaves='3' stitchTiles='stitch'/%3E%3CfeColorMatrix values='0 0 0 0 0.1 0 0 0 0 0.08 0 0 0 0 0.05 0 0 0 0.08 0'/%3E%3C/filter%3E%3Crect width='200' height='200' filter='url(%23n)'/%3E%3C/svg%3E");
    opacity: 0.5;
    z-index: 1;
    mix-blend-mode: multiply;
  }}

  .page {{ max-width: 960px; margin: 0 auto; position: relative; z-index: 2; }}

  .site-nav {{
    max-width: 960px; margin: 0 auto 40px; padding: 0 0 16px;
    border-bottom: 1px solid var(--rule);
    display: flex; align-items: center; gap: 32px;
    position: relative; z-index: 2;
  }}
  .nav-logo {{ display: flex; align-items: center; gap: 10px; text-decoration: none; flex-shrink: 0; }}
  .nav-logo-mark {{
    width: 28px; height: 28px; background: var(--seal); border-radius: 3px;
    display: flex; align-items: center; justify-content: center;
  }}
  .nav-name {{ font-family: 'Fraunces', Georgia, serif; font-size: 1.1rem; font-weight: 600; color: var(--ink); letter-spacing: -0.01em; }}
  .nav-links {{ display: flex; gap: 24px; margin-left: auto; }}
  .nav-link {{ font-size: 0.875rem; color: var(--ink-soft); text-decoration: none; padding: 4px 0; border-bottom: 2px solid transparent; transition: color 0.15s, border-color 0.15s; }}
  .nav-link:hover {{ color: var(--seal); }}
  .nav-link.active {{ color: var(--seal); border-bottom-color: var(--seal); }}

  .page-header {{
    border-bottom: 2px solid var(--seal);
    padding-bottom: 24px;
    margin-bottom: 36px;
  }}
  .page-title {{
    font-family: 'Fraunces', Georgia, serif;
    font-size: 2rem; font-weight: 700; color: var(--ink);
    letter-spacing: -0.01em; margin-bottom: 6px;
  }}
  .page-subtitle {{ color: var(--ink-faded); font-size: 0.875rem; }}

  .passport-list {{
    display: flex;
    flex-direction: column;
    gap: 10px;
  }}
  .passport-item {{
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 14px 16px;
    background: white;
    border: 1px solid var(--rule);
    border-radius: 3px;
    text-decoration: none;
    color: var(--ink);
    transition: border-color 0.15s, box-shadow 0.15s;
  }}
  .passport-item:hover {{
    border-color: var(--seal);
    box-shadow: 0 2px 8px rgba(110, 24, 24, 0.08);
  }}
  .passport-id {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    color: var(--seal);
    flex-shrink: 0;
    width: 140px;
  }}
  .passport-thumb {{
    width: 48px;
    height: 36px;
    flex-shrink: 0;
    background: var(--paper-deep);
    border: 1px solid var(--rule);
    overflow: hidden;
    border-radius: 2px;
  }}
  .passport-thumb img {{ width: 100%; height: 100%; object-fit: cover; }}
  .passport-title {{
    font-family: 'Fraunces', Georgia, serif;
    font-size: 1rem;
    font-weight: 500;
    flex: 1;
    min-width: 0;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }}
  .passport-artist {{
    font-size: 0.875rem;
    color: var(--ink-soft);
    flex-shrink: 0;
    max-width: 160px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }}
  .passport-date {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    color: var(--ink-faded);
    flex-shrink: 0;
    width: 80px;
    text-align: right;
  }}
  .passport-arrow {{ color: var(--seal); font-size: 0.8rem; flex-shrink: 0; }}

  .oid-score {{
    flex-shrink: 0;
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 4px;
    width: 90px;
  }}
  .oid-score-header {{
    display: flex;
    align-items: baseline;
    gap: 2px;
  }}
  .oid-score-num {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 18px;
    font-weight: 700;
    line-height: 1;
    color: var(--ink);
  }}
  .oid-score-denom {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: var(--ink-faded);
  }}
  .oid-bar-wrap {{
    width: 100%;
    height: 4px;
    background: var(--paper-deep);
    border-radius: 2px;
    overflow: hidden;
    border: 1px solid var(--rule);
  }}
  .oid-bar {{ height: 100%; border-radius: 2px; }}
  .oid-bar.complete {{ background: var(--seal); }}
  .oid-bar.partial  {{ background: var(--gold); }}
  .oid-bar.draft    {{ background: var(--ink-faded); }}
  .oid-tag {{
    font-size: 8px;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 1px 5px;
    border-radius: 2px;
    color: #fff;
  }}
  .oid-tag.complete {{ background: var(--seal); }}
  .oid-tag.partial  {{ background: var(--gold); }}
  .oid-tag.draft    {{ background: var(--ink-faded); }}

  .site-footer {{
    margin-top: 64px; padding-top: 24px; border-top: 1px solid var(--rule);
    display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;
  }}
  .footer-text {{ font-size: 0.75rem; color: var(--ink-faded); }}
  .footer-generated {{ font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: var(--ink-faded); }}

  @media (max-width: 600px) {{
    body {{ padding: 20px 16px 60px; }}
    .site-nav {{ flex-wrap: wrap; gap: 8px; margin-bottom: 24px; }}
    .nav-links {{ gap: 14px; flex-wrap: wrap; }}
    .nav-link {{ font-size: 0.8rem; }}
    .passport-artist, .passport-date {{ display: none; }}
    .passport-id {{ width: 110px; font-size: 0.7rem; }}
    .oid-score {{ width: 72px; }}
    .oid-score-num {{ font-size: 14px; }}
  }}
</style>
</head>
<body>

<nav class="site-nav">
  <a href="../" class="nav-logo">
    <div class="nav-logo-mark">
      <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
        <rect x="3" y="3" width="6" height="6" fill="white" opacity="0.9"/>
        <rect x="11" y="3" width="6" height="6" fill="white" opacity="0.5"/>
        <rect x="3" y="11" width="6" height="6" fill="white" opacity="0.5"/>
        <rect x="11" y="11" width="6" height="6" fill="white" opacity="0.75"/>
      </svg>
    </div>
    <span class="nav-name">Ars Accordia</span>
  </a>
  <div class="nav-links">
    <a href="../artworks/" class="nav-link active">Artworks</a>
    <a href="../collections/" class="nav-link">Collections</a>
    <a href="../artists/" class="nav-link">Artists</a>
    <a href="../about/" class="nav-link">About</a>
    <a href="../contributions/" class="nav-link">Contributions</a>
    <a href="../sitemap/" class="nav-link">Index</a>
  </div>
</nav>

<div class="page">

  <header class="page-header">
    <h1 class="page-title">Artwork Passports</h1>
    <p class="page-subtitle">
      {count} passport{"s" if count != 1 else ""} published ·
      Standards-compliant identity records · Object ID · LIDO 1.1
    </p>
  </header>

  <div class="passport-list">
{rows}
  </div>

  <footer class="site-footer">
    <span class="footer-text">© 2026 Ars Accordia · Artwork Passports · Object ID compliant</span>
    <span class="footer-generated">Generated {generated_at}</span>
  </footer>

</div>
</body>
</html>"""


def main(dry_run: bool = False) -> None:
    files = sorted(ARTWORKS_DIR.glob("*.json"))
    if not files:
        sys.exit(f"No artwork JSONs found in {ARTWORKS_DIR}")

    artworks = []
    for f in files:
        try:
            aw = json.load(open(f, encoding="utf-8"))
            artworks.append(aw)
        except Exception as e:
            print(f"  Warning: could not load {f.name}: {e}", file=sys.stderr)

    # Sort by artbase_id (AP-2026-XXXXXX order)
    artworks.sort(key=lambda a: a.get("artbase_id", ""))

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    html = generate(artworks, now)

    if dry_run:
        print(f"(dry-run) Would write {len(html)//1024} KB to {OUT_PATH}")
        print(f"  {len(artworks)} artworks")
        return

    OUT_PATH.write_text(html, encoding="utf-8")
    print(f"✓ {OUT_PATH}  ({len(html)//1024} KB)  {len(artworks)} passports")


if __name__ == "__main__":
    main(dry_run="--dry-run" in sys.argv)
