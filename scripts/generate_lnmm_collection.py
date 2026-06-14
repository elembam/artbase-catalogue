#!/usr/bin/env python3
"""
generate_lnmm_collection.py — Generate /collections/lnmm/index.html from lnmm.html source data.

Usage:
    python3 scripts/generate_lnmm_collection.py
"""

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO_ROOT  = Path(__file__).resolve().parent.parent
SRC        = REPO_ROOT / "ArsAccordiaClaude" / "lnmm.html"
OUT_DIR    = REPO_ROOT / "collections" / "lnmm"
ARTISTS_DIR = REPO_ROOT / "artbase_export" / "data" / "artists"

# ── Parse source HTML ──────────────────────────────────────────────────────────

def parse_lnmm(path: Path) -> list[dict]:
    content = path.read_text(encoding="utf-8")
    rows = re.findall(r"<tr[^>]*>(.*?)</tr>", content, re.DOTALL)
    works = []
    for row in rows[1:]:
        cells = re.findall(r"<td[^>]*>(.*?)</td>", row, re.DOTALL)
        cells = [re.sub(r"<[^>]+>", "", c).strip().replace("\n", " ") for c in cells]
        if len(cells) >= 11 and cells[0]:
            works.append({
                "title":       cells[0],
                "creator":     cells[1],
                "lifespan":    cells[2],
                "date":        cells[3],
                "dimensions":  cells[4],
                "type":        cells[5],
                "medium":      cells[7],
                "collection":  cells[8],
                "cat_no":      cells[9],
                "url":         cells[10],
            })
    return works


# ── Load ArtBase Wikidata status ───────────────────────────────────────────────

def simplify(s: str) -> str:
    return s.lower().translate(str.maketrans("āēīūņģķļšžč", "aeiungklszc"))


def load_artbase_wikidata(artists_dir: Path) -> dict[str, dict]:
    """Return {simplified_name: {qid, status}} for all ArtBase artist records."""
    result = {}
    for jf in artists_dir.glob("*.json"):
        try:
            data = json.loads(jf.read_text())
        except Exception:
            continue
        name = data.get("identity", {}).get("preferred_name") or ""
        wd = data.get("authority_links", {}).get("wikidata") or {}
        result[simplify(name)] = {
            "qid":    wd.get("id") or "",
            "status": wd.get("status") or "",
            "name":   name,
        }
    return result


# ── Build artist summaries ─────────────────────────────────────────────────────

def build_artists(works: list[dict], artbase_wd: dict) -> list[dict]:
    by_artist: dict[str, list[dict]] = defaultdict(list)
    for w in works:
        if w["creator"]:
            by_artist[w["creator"]].append(w)

    artists = []
    for name, wlist in sorted(by_artist.items(), key=lambda x: -len(x[1])):
        types = Counter(w["type"] for w in wlist if w["type"])
        dates = [w["date"] for w in wlist if w["date"]]
        lifespan = wlist[0]["lifespan"] if wlist else ""

        wd_match = artbase_wd.get(simplify(name), {})
        qid    = wd_match.get("qid", "")
        status = wd_match.get("status", "")

        artists.append({
            "name":     name,
            "lifespan": lifespan,
            "count":    len(wlist),
            "types":    dict(types.most_common()),
            "dates":    dates,
            "qid":      qid,
            "status":   status,
            "works":    wlist,
        })
    return artists


# ── HTML generation ────────────────────────────────────────────────────────────

NAV = """<nav class="site-nav">
  <div class="wrap">
  <a href="../../" class="nav-logo">
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
    <a href="../../catalogue/" class="nav-link">Catalogue</a>
    <a href="../../artworks/" class="nav-link">Artworks</a>
    <a href="../../collections/" class="nav-link active">Collections</a>
    <a href="../../artists/" class="nav-link">Artists</a>
    <a href="../../about/" class="nav-link">About</a>
    <a href="../../sitemap/" class="nav-link">Index</a>
  </div>
  </div>
</nav>"""

CSS = """
  :root {
    --paper:      #f6f1e6;
    --paper-deep: #ebe3d1;
    --ink:        #1c1814;
    --ink-soft:   #4a4338;
    --ink-faded:  #80766a;
    --seal:       #6e1818;
    --gold:       #8a6f2e;
    --rule:       #c7bca5;
    --grid:       rgba(110, 24, 24, 0.04);
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  html { scroll-behavior: smooth; }
  body {
    background: var(--paper);
    background-image:
      linear-gradient(var(--grid) 1px, transparent 1px),
      linear-gradient(90deg, var(--grid) 1px, transparent 1px);
    background-size: 32px 32px;
    color: var(--ink);
    font-family: 'Public Sans', -apple-system, sans-serif;
    font-size: 15px;
    line-height: 1.5;
    min-height: 100vh;
  }
  body::before {
    content: '';
    position: fixed; inset: 0; pointer-events: none;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='200'%3E%3Cfilter id='n'%3E%3CfeTurbulence baseFrequency='0.9' numOctaves='3' stitchTiles='stitch'/%3E%3CfeColorMatrix values='0 0 0 0 0.1 0 0 0 0 0.08 0 0 0 0 0.05 0 0 0 0.08 0'/%3E%3C/filter%3E%3Crect width='200' height='200' filter='url(%23n)'/%3E%3C/svg%3E");
    opacity: 0.5; z-index: 1; mix-blend-mode: multiply;
  }
  .wrap { max-width: 960px; margin: 0 auto; padding: 0 24px; position: relative; z-index: 2; }

  /* Nav */
  .site-nav {
    border-bottom: 1px solid var(--rule);
    position: relative; z-index: 2;
    background: var(--paper);
  }
  .site-nav .wrap { display: flex; align-items: center; gap: 32px; padding-top: 20px; padding-bottom: 16px; }
  .nav-logo { display: flex; align-items: center; gap: 10px; text-decoration: none; flex-shrink: 0; }
  .nav-logo-mark { width: 28px; height: 28px; background: var(--seal); border-radius: 3px; display: flex; align-items: center; justify-content: center; }
  .nav-name { font-family: 'Fraunces', Georgia, serif; font-size: 1.1rem; font-weight: 600; color: var(--ink); letter-spacing: -0.01em; }
  .nav-links { display: flex; gap: 24px; margin-left: auto; }
  .nav-link { font-size: 0.875rem; color: var(--ink-soft); text-decoration: none; padding: 4px 0; border-bottom: 2px solid transparent; transition: color 0.15s, border-color 0.15s; }
  .nav-link:hover { color: var(--seal); }
  .nav-link.active { color: var(--seal); border-bottom-color: var(--seal); }

  /* Page header */
  .page-header { padding: 52px 0 40px; border-bottom: 2px solid var(--seal); margin-bottom: 52px; }
  .page-eyebrow { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.12em; color: var(--seal); font-weight: 600; margin-bottom: 10px; }
  .page-title { font-family: 'Fraunces', Georgia, serif; font-size: clamp(1.8rem, 4vw, 2.6rem); font-weight: 700; color: var(--ink); letter-spacing: -0.02em; line-height: 1.1; margin-bottom: 12px; font-style: italic; }
  .page-subtitle { font-size: 1rem; color: var(--ink-soft); max-width: 560px; line-height: 1.7; margin-bottom: 28px; }
  .stats-row { display: flex; gap: 40px; flex-wrap: wrap; }
  .stat { display: flex; flex-direction: column; gap: 2px; }
  .stat-value { font-family: 'JetBrains Mono', monospace; font-size: 1.8rem; font-weight: 500; color: var(--seal); line-height: 1; }
  .stat-label { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.08em; color: var(--ink-faded); }

  /* Section */
  .section { margin-bottom: 60px; }
  .section-header { display: flex; align-items: baseline; justify-content: space-between; border-bottom: 1px solid var(--rule); padding-bottom: 12px; margin-bottom: 24px; }
  .section-title { font-family: 'Fraunces', Georgia, serif; font-size: 1.2rem; font-weight: 600; color: var(--ink); }
  .section-count { font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: var(--ink-faded); }

  /* Artist cards */
  .artist-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 12px; }
  .artist-card {
    background: white; border: 1px solid var(--rule); border-radius: 4px;
    padding: 18px 20px; transition: border-color 0.15s;
  }
  .artist-card:hover { border-color: var(--seal); }
  .artist-card-top { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 6px; }
  .artist-name { font-family: 'Fraunces', Georgia, serif; font-size: 0.95rem; font-weight: 600; color: var(--ink); }
  .artist-lifespan { font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; color: var(--ink-faded); margin-top: 2px; }
  .artist-count { font-family: 'JetBrains Mono', monospace; font-size: 1.3rem; font-weight: 500; color: var(--seal); line-height: 1; flex-shrink: 0; }
  .artist-types { font-size: 0.78rem; color: var(--ink-soft); margin-top: 8px; }
  .artist-badges { display: flex; gap: 5px; margin-top: 10px; flex-wrap: wrap; }
  .badge {
    font-size: 0.62rem; font-weight: 600; padding: 2px 7px;
    border: 1px solid var(--rule); border-radius: 2px;
    font-family: 'JetBrains Mono', monospace; white-space: nowrap;
  }
  .badge-confirmed { border-color: #5a8a3a; color: #5a8a3a; }
  .badge-needed    { border-color: var(--gold); color: var(--gold); }
  .badge-missing   { border-color: var(--ink-faded); color: var(--ink-faded); }
  .badge-qid { font-family: 'JetBrains Mono', monospace; font-size: 0.6rem; color: var(--ink-faded); margin-left: 2px; }

  /* Works filter */
  .filter-bar { margin-bottom: 16px; }
  .filter-input {
    width: 100%; max-width: 400px;
    padding: 9px 14px;
    font-size: 0.875rem;
    border: 1px solid var(--rule);
    border-radius: 3px;
    background: white;
    color: var(--ink);
    font-family: 'Public Sans', sans-serif;
  }
  .filter-input:focus { outline: none; border-color: var(--seal); }

  /* Works table */
  .works-table-wrap { overflow-x: auto; border: 1px solid var(--rule); border-radius: 4px; background: white; }
  table { width: 100%; border-collapse: collapse; font-size: 0.82rem; }
  th { background: var(--paper-deep); font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.07em; color: var(--ink-faded); padding: 10px 12px; text-align: left; border-bottom: 1px solid var(--rule); white-space: nowrap; position: sticky; top: 0; }
  td { padding: 9px 12px; border-bottom: 1px solid var(--rule); vertical-align: top; color: var(--ink-soft); }
  tr:last-child td { border-bottom: none; }
  tr:hover td { background: var(--paper); }
  td.title { color: var(--ink); font-family: 'Fraunces', Georgia, serif; font-style: italic; }
  td.artist { font-weight: 500; color: var(--ink); }
  td.mono { font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; }
  td a { color: var(--seal); text-decoration: none; }
  td a:hover { text-decoration: underline; }

  /* Footer */
  .site-footer { margin-top: 64px; padding: 24px 0 40px; border-top: 1px solid var(--rule); display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; }
  .footer-text { font-size: 0.75rem; color: var(--ink-faded); }
  .footer-link { color: var(--seal); text-decoration: none; }
  .footer-link:hover { text-decoration: underline; }

  @media (max-width: 640px) {
    .nav-links { gap: 12px; flex-wrap: wrap; }
    .nav-link { font-size: 0.78rem; }
    .artist-grid { grid-template-columns: 1fr; }
    .stats-row { gap: 20px; }
  }
  @media print { .site-nav, .filter-bar { display: none; } }
"""


def wikidata_badge(status: str, qid: str) -> str:
    if status == "confirmed" and qid:
        return (f'<span class="badge badge-confirmed">Wikidata ✓</span>'
                f'<span class="badge-qid">{qid}</span>')
    elif status == "search_needed":
        return '<span class="badge badge-needed">Wikidata: search needed</span>'
    else:
        return '<span class="badge badge-missing">Wikidata: not linked</span>'


def type_summary(types: dict) -> str:
    parts = []
    for t, n in types.items():
        parts.append(f"{n} {t.lower()}{'s' if n > 1 else ''}")
    return " · ".join(parts)


def render_page(artists: list[dict], works: list[dict]) -> str:
    total_works = len(works)
    total_artists = len(artists)
    confirmed = sum(1 for a in artists if a["status"] == "confirmed")

    # Artist cards HTML
    artist_cards = ""
    for a in artists:
        badge = wikidata_badge(a["status"], a["qid"])
        artist_cards += f"""
      <div class="artist-card">
        <div class="artist-card-top">
          <div>
            <div class="artist-name">{a["name"]}</div>
            <div class="artist-lifespan">{a["lifespan"]}</div>
          </div>
          <div class="artist-count">{a["count"]}</div>
        </div>
        <div class="artist-types">{type_summary(a["types"])}</div>
        <div class="artist-badges">{badge}</div>
      </div>"""

    # Works rows HTML
    work_rows = ""
    for w in works:
        url_cell = (f'<a href="{w["url"]}" target="_blank" rel="noopener">Google Arts ↗</a>'
                    if w["url"] else "")
        work_rows += f"""
      <tr>
        <td class="title">{w["title"] or "–"}</td>
        <td class="artist">{w["creator"] or "–"}</td>
        <td class="mono">{w["date"] or "–"}</td>
        <td>{w["type"] or "–"}</td>
        <td>{w["medium"] or "–"}</td>
        <td class="mono">{w["dimensions"] or "–"}</td>
        <td class="mono">{w["cat_no"] or "–"}</td>
        <td>{url_cell}</td>
      </tr>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="Latvia National Museum of Art (LNMA) collection — {total_works} works by {total_artists} artists in the Ars Accordia catalogue. Latvian art 18th–20th century.">
<title>LNMA Collection — Ars Accordia</title>
<link rel="canonical" href="https://arsaccordia.com/collections/lnmm/">
<meta property="og:title"       content="LNMA Collection — Ars Accordia">
<meta property="og:description" content="{total_works} works by {total_artists} Latvian artists from the Latvia National Museum of Art.">
<meta property="og:url"         content="https://arsaccordia.com/collections/lnmm/">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,ital,wght,SOFT,WONK@9..144,0..1,300..900,0..100,0..1&family=Public+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
{CSS}
</style>
</head>
<body>

{NAV}

<div class="wrap">

  <header class="page-header">
    <p class="page-eyebrow">Collection · Latvia National Museum of Art</p>
    <h1 class="page-title">LNMA Latvian Art Collection</h1>
    <p class="page-subtitle">
      Works from the Latvia National Museum of Art (Latvijas Nacionālais mākslas muzejs) —
      paintings, drawings, watercolours, and sculpture spanning the 18th through the first
      half of the 20th century. Source: LNMA open data via Google Arts &amp; Culture.
    </p>
    <div class="stats-row">
      <div class="stat"><span class="stat-value">{total_works}</span><span class="stat-label">Works</span></div>
      <div class="stat"><span class="stat-value">{total_artists}</span><span class="stat-label">Artists</span></div>
      <div class="stat"><span class="stat-value">{confirmed}</span><span class="stat-label">Wikidata confirmed</span></div>
      <div class="stat"><span class="stat-value">c. 1800–1945</span><span class="stat-label">Period</span></div>
    </div>
  </header>

  <!-- Artists -->
  <section class="section">
    <div class="section-header">
      <h2 class="section-title">Artists</h2>
      <span class="section-count">{total_artists} records · sorted by representation</span>
    </div>
    <div class="artist-grid">
      {artist_cards}
    </div>
  </section>

  <!-- Works -->
  <section class="section">
    <div class="section-header">
      <h2 class="section-title">Works</h2>
      <span class="section-count">{total_works} records</span>
    </div>
    <div class="filter-bar">
      <input class="filter-input" id="search" type="search"
             placeholder="Filter by title, artist, medium, date…"
             oninput="filterTable()">
    </div>
    <div class="works-table-wrap">
      <table id="works-table">
        <thead>
          <tr>
            <th>Title</th>
            <th>Artist</th>
            <th>Date</th>
            <th>Type</th>
            <th>Medium</th>
            <th>Dimensions</th>
            <th>Cat. No.</th>
            <th>Source</th>
          </tr>
        </thead>
        <tbody>
          {work_rows}
        </tbody>
      </table>
    </div>
  </section>

  <footer class="site-footer">
    <span class="footer-text">
      Ars Accordia · <a href="../../" class="footer-link">Home</a> ·
      <a href="../" class="footer-link">Collections</a> ·
      <a href="../../about/" class="footer-link">About</a>
    </span>
    <span style="font-family:'JetBrains Mono',monospace;font-size:0.7rem;color:var(--ink-faded);">
      Source: LNMA open data · Google Arts &amp; Culture
    </span>
  </footer>

</div>

<script>
function filterTable() {{
  var q = document.getElementById('search').value.toLowerCase();
  var rows = document.querySelectorAll('#works-table tbody tr');
  rows.forEach(function(row) {{
    row.style.display = row.textContent.toLowerCase().includes(q) ? '' : 'none';
  }});
}}
</script>
</body>
</html>"""


def main():
    if not SRC.exists():
        sys.exit(f"Source not found: {SRC}")

    print("Parsing LNMM source…")
    works = parse_lnmm(SRC)
    print(f"  {len(works)} works parsed")

    print("Loading ArtBase Wikidata records…")
    artbase_wd = load_artbase_wikidata(ARTISTS_DIR)
    print(f"  {len(artbase_wd)} artist records loaded")

    artists = build_artists(works, artbase_wd)
    print(f"  {len(artists)} unique artists")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "index.html"
    html = render_page(artists, works)
    out_path.write_text(html, encoding="utf-8")
    size_kb = len(html.encode()) // 1024
    print(f"\n✓ Written: {out_path}  ({size_kb} KB)")


if __name__ == "__main__":
    main()
