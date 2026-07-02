#!/usr/bin/env python3
"""
latvia_generator.py — Regenerate artists/latvia/index.html.

Preserves the established Ars Accordia site design (nav, CSS, artist blocks
with artwork cards) while populating works from canonical JSON.

Usage:
    python3 scripts/latvia_generator.py
    python3 scripts/latvia_generator.py --dry-run
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT    = Path(__file__).resolve().parent.parent
ARTISTS_DIR  = REPO_ROOT / "artbase_export" / "data" / "artists"
ARTWORKS_DIR = REPO_ROOT / "artbase_export" / "data" / "artworks"
OUT_PATH     = REPO_ROOT / "artists" / "latvia" / "index.html"


# ── Data loading ───────────────────────────────────────────────────────────────

def load_artists() -> list[dict]:
    artists = []
    for f in sorted(ARTISTS_DIR.glob("*.json")):
        try:
            a = json.load(open(f, encoding="utf-8"))
            if a.get("artbase_id") != "UNKNOWN":
                artists.append(a)
        except Exception:
            pass
    return sorted(artists, key=lambda a: a.get("identity", {}).get("sort_name", "ZZZZ").lower())


def load_artworks_by_maker() -> dict[str, list[dict]]:
    mapping: dict[str, list[dict]] = {}
    for f in sorted(ARTWORKS_DIR.glob("*.json")):
        try:
            aw = json.load(open(f, encoding="utf-8"))
        except Exception:
            continue
        oid = aw.get("object_id") or {}
        key = oid.get("maker_id") or oid.get("maker_display_name")
        if key:
            mapping.setdefault(key, []).append(aw)
    return mapping


# ── HTML fragments ──────────────────────────────────────────────────────────────

def _esc(s: str) -> str:
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


PLACEHOLDER_SVG = """\
<svg width="48" height="48" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect width="48" height="48" fill="none"/>
  <rect x="8" y="10" width="32" height="28" rx="2" stroke="#c7bca5" stroke-width="1.5" fill="none"/>
  <circle cx="18" cy="20" r="4" stroke="#c7bca5" stroke-width="1.5" fill="none"/>
  <path d="M8 32 L18 22 L26 30 L32 24 L40 32" stroke="#c7bca5" stroke-width="1.5" fill="none"/>
</svg>"""


def artwork_card(aw: dict) -> str:
    oid  = aw.get("object_id") or {}
    aid  = aw.get("artbase_id", "")
    title = _esc(oid.get("title") or "Untitled")
    title_en = oid.get("title_en") or ""
    if title_en and title_en != oid.get("title", ""):
        title = f"{title} ({_esc(title_en)})"
    date   = _esc(oid.get("date_display") or "")
    medium = _esc(oid.get("materials") or "")
    dims   = _esc(oid.get("dimensions_display") or "")

    return f"""\
      <a class="artwork-card" href="/{aid}.html">
        <div class="card-image">
          <div class="card-image-placeholder">
            {PLACEHOLDER_SVG}
            <span>No image</span>
          </div>
        </div>
        <div class="card-body">
          <div class="card-title">{title}</div>
          <div class="card-date">{date}</div>
          {"<div class='card-medium'>" + medium + ("  ·  " + dims if dims else "") + "</div>" if medium or dims else ""}
          <div class="card-footer">
            <span class="card-passport-id">{aid}</span>
            <span class="card-arrow">
              <svg viewBox="0 0 10 10"><path d="M2 5h6M5 2l3 3-3 3" stroke="white" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" fill="none"/></svg>
            </span>
          </div>
        </div>
      </a>"""


def artist_block(artist: dict, artworks: list[dict]) -> str:
    aid   = artist.get("artbase_id", "")
    ident = artist.get("identity") or {}
    life  = artist.get("life") or {}
    desc  = artist.get("descriptors") or {}
    al    = artist.get("authority_links") or {}

    name  = _esc(ident.get("preferred_name") or aid)
    birth = ((life.get("birth_date") or {}).get("value") or "?")[:4]
    death = ((life.get("death_date") or {}).get("value") or "present")[:4]
    occ   = ", ".join(desc.get("occupations") or [])
    nat   = desc.get("nationality") or ""

    wd_id  = (al.get("wikidata") or {}).get("id") or ""
    wd_status = (al.get("wikidata") or {}).get("status") or ""
    ulan_id = (al.get("ulan") or {}).get("id") or ""
    viaf_id = (al.get("viaf") or {}).get("id") or ""

    candidate_notice = ""
    candidate_pill = ""
    if wd_status == "candidate_verify":
        candidate_pill = '<span class="pill pill-candidate">⚠ Candidate</span>'
        candidate_notice = (
            '<p class="candidate-notice">⚠ <strong>Candidate match — awaiting verification.</strong> '
            "Wikidata link was assigned by automated matching. Please verify before treating as authoritative.</p>"
        )

    wd_badge = (
        f'<a class="authority-badge" href="https://www.wikidata.org/wiki/{_esc(wd_id)}" target="_blank" rel="noopener">'
        f'<span class="auth-prefix">WD</span>{_esc(wd_id)}</a>'
    ) if wd_id else ""

    ulan_badge = (
        f'<a class="authority-badge" href="http://vocab.getty.edu/ulan/{_esc(ulan_id)}" target="_blank" rel="noopener">'
        f'<span class="auth-prefix">ULAN</span>{_esc(ulan_id)}</a>'
    ) if ulan_id else ""

    viaf_badge = (
        f'<a class="authority-badge" href="https://viaf.org/viaf/{_esc(viaf_id)}/" target="_blank" rel="noopener">'
        f'<span class="auth-prefix">VIAF</span>{_esc(viaf_id[:12])}…</a>'
    ) if viaf_id else ""

    profile_btn = (
        f'<a class="authority-badge" style="background:var(--seal);color:#fff;border-color:var(--seal);" '
        f'href="/artists/{_esc(aid)}.html">Profile →</a>'
    )

    sorted_works = sorted(artworks, key=lambda a: a.get("object_id", {}).get("date_earliest") or 9999)
    if sorted_works:
        cards = "\n".join(artwork_card(aw) for aw in sorted_works)
        artworks_html = f'<div class="artworks-grid">\n{cards}\n    </div>'
    else:
        artworks_html = '<div class="no-artworks">No artwork passports catalogued yet for this artist.</div>'

    return f"""\
  <section class="artist-block" id="{_esc(aid)}">
    <div class="artist-header">
      <div class="artist-portrait placeholder"></div>
      <div>
        <h2 class="artist-name">
          {"<a href='/artists/" + _esc(aid) + ".html' style='color:var(--seal);text-decoration:underline;text-underline-offset:3px;text-decoration-color:rgba(110,24,24,0.35);'>" + name + "</a>" if wd_id else name}
        </h2>
        <div class="artist-meta">
          {"<span class='pill pill-nationality'>" + _esc(nat) + "</span>" if nat else ""}
          {candidate_pill}
          <span class="artist-dates">{birth} — {death}</span>
          {"<span style='color:var(--ink-faded); font-size:0.8rem;'>" + _esc(occ) + "</span>" if occ else ""}
        </div>
        {candidate_notice}
      </div>
      <div class="artist-links">
        {wd_badge}
        {ulan_badge}
        {viaf_badge}
        {profile_btn}
      </div>
    </div>
    {artworks_html}
  </section>"""


# ── Page assembly ───────────────────────────────────────────────────────────────

def generate(artists: list[dict], artworks_by_maker: dict[str, list[dict]], now: str) -> str:
    total_artists = len(artists)
    total_passports = sum(
        1 for entries in artworks_by_maker.values()
        for _ in entries
    )

    blocks = "\n\n".join(
        artist_block(
            a,
            artworks_by_maker.get(a.get("artbase_id", ""), [])
            or artworks_by_maker.get(a.get("identity", {}).get("preferred_name", ""), [])
        )
        for a in artists
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="Ars Accordia — Latvian Artists A–Z. Authority records, Wikidata, ULAN, VIAF.">
<title>Latvian Artists — Ars Accordia</title>
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

  .catalogue {{ max-width: 960px; margin: 0 auto; position: relative; z-index: 2; }}

  .site-nav {{
    max-width: 960px; margin: 0 auto 40px; padding: 0 0 16px;
    border-bottom: 1px solid var(--rule);
    display: flex; align-items: center; gap: 32px;
    position: relative; z-index: 2;
  }}
  .nav-logo {{ display: flex; align-items: center; gap: 10px; text-decoration: none; flex-shrink: 0; }}
  .nav-logo-mark {{ width: 28px; height: 28px; background: var(--seal); border-radius: 3px; display: flex; align-items: center; justify-content: center; }}
  .nav-name {{ font-family: 'Fraunces', Georgia, serif; font-size: 1.1rem; font-weight: 600; color: var(--ink); letter-spacing: -0.01em; }}
  .nav-links {{ display: flex; gap: 24px; margin-left: auto; }}
  .nav-link {{ font-size: 0.875rem; color: var(--ink-soft); text-decoration: none; padding: 4px 0; border-bottom: 2px solid transparent; transition: color 0.15s, border-color 0.15s; }}
  .nav-link:hover {{ color: var(--seal); }}
  .nav-link.active {{ color: var(--seal); border-bottom-color: var(--seal); }}

  .page-header {{
    border-bottom: 2px solid var(--seal);
    padding-bottom: 24px;
    margin-bottom: 40px;
  }}
  .page-title {{ font-family: 'Fraunces', Georgia, serif; font-size: 2rem; font-weight: 700; color: var(--ink); letter-spacing: -0.01em; margin-bottom: 4px; }}
  .page-tagline {{ color: var(--ink-faded); font-size: 0.875rem; letter-spacing: 0.06em; text-transform: uppercase; margin-top: 4px; }}
  .page-stats {{ margin-top: 12px; display: flex; gap: 24px; flex-wrap: wrap; }}
  .stat {{ display: flex; flex-direction: column; gap: 2px; }}
  .stat-value {{ font-family: 'JetBrains Mono', monospace; font-size: 1.25rem; font-weight: 500; color: var(--seal); }}
  .stat-label {{ font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.08em; color: var(--ink-faded); }}

  .artist-block {{ margin-bottom: 56px; }}

  .artist-header {{
    display: grid;
    grid-template-columns: auto 1fr auto;
    align-items: start;
    gap: 16px;
    border-bottom: 1px solid var(--rule);
    padding-bottom: 14px;
    margin-bottom: 24px;
  }}

  .artist-portrait {{ width: 60px; height: 75px; flex-shrink: 0; }}
  .artist-portrait img {{ width: 60px; height: 75px; object-fit: cover; object-position: top center; border: 1px solid var(--rule); display: block; }}
  .artist-portrait.placeholder {{ background: var(--paper-deep); border: 1px dashed var(--rule); }}

  .artist-name {{ font-family: 'Fraunces', Georgia, serif; font-size: 1.5rem; font-weight: 600; color: var(--ink); line-height: 1.2; }}
  .artist-meta {{ margin-top: 5px; color: var(--ink-soft); font-size: 0.875rem; display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }}
  .artist-dates {{ font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; color: var(--ink-faded); }}

  .pill {{ display: inline-block; padding: 2px 8px; border-radius: 3px; font-size: 0.7rem; font-weight: 600; letter-spacing: 0.05em; text-transform: uppercase; }}
  .pill-nationality {{ background: var(--paper-deep); color: var(--ink-soft); border: 1px solid var(--rule); }}
  .pill-candidate {{ background: #fffbeb; color: #7a5c00; border: 1px solid #d4a800; }}
  .candidate-notice {{ margin-top: 6px; font-size: 0.78rem; color: #7a5c00; background: #fffbeb; border: 1px solid #d4a800; border-radius: 3px; padding: 5px 10px; max-width: 580px; }}

  .artist-links {{ display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }}
  .authority-badge {{
    display: inline-flex; align-items: center; gap: 5px;
    padding: 3px 9px; border: 1px solid var(--rule); border-radius: 3px;
    font-size: 0.7rem; font-family: 'JetBrains Mono', monospace;
    color: var(--ink-faded); text-decoration: none;
    transition: border-color 0.15s, color 0.15s;
  }}
  .authority-badge:hover {{ border-color: var(--seal); color: var(--seal); }}
  .authority-badge .auth-prefix {{ font-weight: 600; color: var(--gold); }}

  .artworks-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 16px; margin-top: 4px; }}
  .artwork-card {{ background: #fff; border: 1px solid var(--rule); border-radius: 4px; overflow: hidden; text-decoration: none; color: inherit; display: block; transition: box-shadow 0.15s, border-color 0.15s, transform 0.15s; }}
  .artwork-card:hover {{ border-color: var(--seal); box-shadow: 0 4px 16px rgba(110, 24, 24, 0.1); transform: translateY(-2px); }}
  .card-image {{ width: 100%; aspect-ratio: 4/3; background: var(--paper-deep); display: flex; align-items: center; justify-content: center; overflow: hidden; border-bottom: 1px solid var(--rule); }}
  .card-image img {{ width: 100%; height: 100%; object-fit: cover; }}
  .card-image-placeholder {{ display: flex; flex-direction: column; align-items: center; gap: 8px; color: var(--ink-faded); }}
  .card-image-placeholder svg {{ opacity: 0.35; }}
  .card-image-placeholder span {{ font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.08em; }}
  .card-body {{ padding: 14px 16px 16px; }}
  .card-title {{ font-family: 'Fraunces', Georgia, serif; font-size: 1rem; font-weight: 600; line-height: 1.3; color: var(--ink); margin-bottom: 4px; }}
  .card-date {{ font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: var(--ink-faded); margin-bottom: 8px; }}
  .card-medium {{ font-size: 0.8rem; color: var(--ink-soft); margin-bottom: 10px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
  .card-footer {{ display: flex; align-items: center; justify-content: space-between; margin-top: 10px; padding-top: 10px; border-top: 1px solid var(--rule); }}
  .card-passport-id {{ font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: var(--ink-faded); }}
  .card-arrow {{ width: 20px; height: 20px; background: var(--seal); border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }}
  .card-arrow svg {{ width: 10px; height: 10px; fill: white; }}

  .no-artworks {{ padding: 24px; border: 1px dashed var(--rule); border-radius: 4px; color: var(--ink-faded); font-size: 0.875rem; text-align: center; }}

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
    .page-title {{ font-size: 1.5rem; }}
    .artist-header {{ grid-template-columns: auto 1fr; }}
    .artist-links {{ grid-column: 1 / -1; display: flex; flex-wrap: wrap; gap: 6px; justify-content: flex-start; }}
    .artworks-grid {{ grid-template-columns: 1fr; }}
  }}
</style>
</head>
<body>

<nav class="site-nav">
  <a href="/" class="nav-logo">
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
    <a href="/artworks/" class="nav-link">Artworks</a>
    <a href="/artists/" class="nav-link active">Artists</a>
    <a href="/about/" class="nav-link">About</a>
  </div>
</nav>

<div class="catalogue">

  <header class="page-header">
    <h1 class="page-title">Latvian Artists</h1>
    <div class="page-tagline">Artist Records A–Z · Authority Links</div>
    <div class="page-stats">
      <div class="stat">
        <span class="stat-value">{total_artists}</span>
        <span class="stat-label">Artists</span>
      </div>
      <div class="stat">
        <span class="stat-value">{total_passports}</span>
        <span class="stat-label">Passports</span>
      </div>
    </div>
  </header>

{blocks}

  <footer class="site-footer">
    <span class="footer-text">© 2026 Ars Accordia · Latvian Artists · Authority Records</span>
    <span class="footer-generated">Generated {now}</span>
  </footer>

</div>
</body>
</html>"""


def main(dry_run: bool = False) -> None:
    artists = load_artists()
    artworks_by_maker = load_artworks_by_maker()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    html = generate(artists, artworks_by_maker, now)

    total_with_works = sum(
        1 for a in artists
        if artworks_by_maker.get(a.get("artbase_id", ""))
        or artworks_by_maker.get(a.get("identity", {}).get("preferred_name", ""))
    )

    if dry_run:
        print(f"(dry-run) {len(artists)} artists, {total_with_works} with artworks — {len(html)//1024} KB")
        return

    OUT_PATH.write_text(html, encoding="utf-8")
    print(f"✓ {OUT_PATH}  ({len(html)//1024} KB)  {len(artists)} artists, {total_with_works} with artworks")


if __name__ == "__main__":
    main(dry_run="--dry-run" in sys.argv)
