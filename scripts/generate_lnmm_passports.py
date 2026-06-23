#!/usr/bin/env python3
"""Generate HTML passport pages for the 6 documented LNMM works.

Usage: python3 scripts/generate_lnmm_passports.py
Outputs: passports/AA/LV/LNMA/{id}/index.html  (one per work)
"""
import json
import os
from pathlib import Path

ROOT = Path(__file__).parent.parent
JSON_DIR = ROOT / "artbase_export/data/artworks/AA/LV/LNMA"
OUT_BASE = ROOT / "passports/AA/LV/LNMA"

WORKS = ["001", "004", "006", "012", "017", "019"]

ARTIST_DATES = {
    "ART-ROZENTALS-1866": "1866–1916",
    "ART-TIDEMANIS-1897": "1897–1955",
    "ART-HUNS-1830":      "1830–1877",
    "ART-FEDERS-1838":    "1838–1909",
}

SCORE_BAND = [
    (85, "Complete Record"),
    (65, "Substantial Record"),
    (40, "Partial Record"),
    (15, "Outline Record"),
    (0,  "Minimal Record"),
]

def band(score):
    for threshold, label in SCORE_BAND:
        if score >= threshold:
            return label
    return "Minimal Record"

def status_badge(status):
    if status == "green":
        colour = "#2e7d32"
        label  = "Cross-referenced · verified"
    elif status == "amber":
        colour = "#b45309"
        label  = "Cross-referenced"
    else:
        colour = "#6b7280"
        label  = "No cross-reference"
    return f'<span style="display:inline-flex;align-items:center;gap:6px;font-size:0.78rem;color:{colour};font-weight:500"><span style="width:8px;height:8px;border-radius:50%;background:{colour};flex-shrink:0"></span>{label}</span>'

def auth_row(label, id_, uri, status=None):
    if not id_:
        return ""
    status_colour = "#2e7d32" if status == "confirmed" else "#b45309"
    dot = f'<span style="width:6px;height:6px;border-radius:50%;background:{status_colour};flex-shrink:0;margin-top:4px"></span>'
    return f'''
      <div style="display:grid;grid-template-columns:120px 1fr;gap:8px;padding:10px 0;border-bottom:1px solid var(--rule)">
        <dt style="font-size:0.7rem;letter-spacing:0.18em;text-transform:uppercase;color:var(--ink-faded);font-weight:500;padding-top:2px">{label}</dt>
        <dd style="display:flex;align-items:flex-start;gap:8px">{dot}<a href="{uri}" target="_blank" rel="noopener" style="font-family:'JetBrains Mono',monospace;font-size:0.8rem;color:var(--seal);text-decoration:none">{id_}</a></dd>
      </div>'''

def prov_step(step):
    src = step.get("source_note") or step.get("source") or ""
    src_html = f'<div style="font-size:0.7rem;color:var(--ink-faded);margin-top:4px;font-style:italic">{src}</div>' if src else ""
    return f'''
    <div style="display:flex;gap:16px;padding:12px 0;border-bottom:1px solid var(--rule)">
      <div style="font-family:'JetBrains Mono',monospace;font-size:0.7rem;color:var(--ink-faded);flex-shrink:0;padding-top:2px">{step['step']:02d}</div>
      <div>
        <div style="font-size:0.9rem;color:var(--ink)">{step['description']}</div>
        {src_html}
      </div>
    </div>'''

def score_row(section):
    if not section.get("in_scope"):
        label = f'{section["section"].title()} <span style="font-size:0.65rem;color:var(--ink-faded)">(not in scope)</span>'
        fill_display = "—"
        contrib = "—"
        bar = ""
    else:
        label = section["section"].title()
        fill_pct = int((section["fill"] or 0) * 100)
        fill_display = f'{fill_pct}%'
        contrib = f'{section["contribution"]:.2f}'
        w = int((section["fill"] or 0) * 100)
        bar = f'<div style="height:4px;background:var(--rule);border-radius:2px;margin-top:4px"><div style="height:4px;width:{w}%;background:var(--seal);border-radius:2px"></div></div>'
    note = section.get("present", "")
    return f'''
    <tr style="border-bottom:1px solid var(--rule)">
      <td style="padding:10px 12px 10px 0;font-size:0.82rem;color:var(--ink)">{label}</td>
      <td style="padding:10px 12px;font-size:0.7rem;color:var(--ink-soft);width:220px">{note}<br>{bar}</td>
      <td style="padding:10px 0 10px 12px;font-family:'JetBrains Mono',monospace;font-size:0.78rem;color:var(--ink-faded);text-align:right;white-space:nowrap">{section['weight']:.2f} × {fill_display} = {contrib}</td>
    </tr>'''

def generate_passport(work_id):
    data = json.loads((JSON_DIR / f"{work_id}.json").read_text())
    oid    = data["object_id"]
    loc    = data["location"]
    al     = data["authority_links"]
    prov   = data.get("provenance", [])
    srcs   = data.get("sources", [])
    score  = data["score"]
    jld    = data.get("structured_data", {}).get("json_ld", {})
    ab_id  = data["artbase_id"]

    title     = oid["title"]
    artist    = oid["maker_display_name"]
    maker_id  = oid.get("maker_id", "")
    dates     = ARTIST_DATES.get(maker_id, "")
    year      = oid["date_display"]
    medium    = oid.get("materials", "")
    dims      = oid.get("dimensions_display", "")
    inv       = loc.get("inventory_number", "")
    obj_type  = oid.get("object_type", "")
    collection = loc.get("collection", "")

    ps    = score["passport_score"]
    band_ = band(ps)
    badge = status_badge(score["status"])

    wd         = al.get("wikidata", {})
    awd        = al.get("artist_wikidata", {})
    ulan       = al.get("artist_ulan", {})

    auth_html = ""
    if wd.get("id"):
        auth_html += auth_row("Artwork (Wikidata)", wd["id"], wd["uri"], wd.get("status"))
    if awd.get("id"):
        auth_html += auth_row("Artist (Wikidata)", awd["id"], awd["uri"], awd.get("status"))
    if ulan.get("id"):
        auth_html += auth_row("Artist (Getty ULAN)", ulan["id"], ulan["uri"], ulan.get("status"))

    prov_html = "".join(prov_step(s) for s in prov)

    sources_html = ""
    for s in srcs:
        sources_html += f'<div style="padding:10px 0;border-bottom:1px solid var(--rule);font-size:0.85rem;color:var(--ink)">{s["citation"]}<span style="display:inline-block;margin-left:8px;font-family:\'JetBrains Mono\',monospace;font-size:0.65rem;color:var(--ink-faded)">{s["source_id"]}</span></div>'

    sections = score["completeness"]["sections"]
    score_rows = "".join(score_row(s) for s in sections)

    jld_script = f'\n<script type="application/ld+json">\n{json.dumps(jld, indent=2, ensure_ascii=False)}\n</script>' if jld else ""

    # authority section heading
    auth_count = sum(1 for x in [wd.get("id"), awd.get("id"), ulan.get("id")] if x)
    auth_label = f"{auth_count} authorit{'y' if auth_count == 1 else 'ies'} linked"

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="Artwork Passport — {title} by {artist}. Documented by Ars Accordia. ArtBase ID {ab_id}.">
<title>Passport — {title} · Ars Accordia</title>
<link rel="canonical" href="https://arsaccordia.com/passports/{ab_id}/">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,ital,wght,SOFT,WONK@9..144,0..1,300..900,0..100,0..1&family=Public+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  :root {{
    --paper:      #f6f1e6;
    --paper-deep: #ebe3d1;
    --ink:        #1c1814;
    --ink-soft:   #4a4338;
    --ink-faded:  #80766a;
    --seal:       #6e1818;
    --gold:       #8a6f2e;
    --rule:       #c7bca5;
    --grid:       rgba(110,24,24,0.04);
  }}
  * {{ box-sizing:border-box; margin:0; padding:0; }}
  html {{ scroll-behavior:smooth; }}
  body {{
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
  }}
  body::before {{
    content:'';
    position:fixed; inset:0; pointer-events:none;
    background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='200'%3E%3Cfilter id='n'%3E%3CfeTurbulence baseFrequency='0.9' numOctaves='3' stitchTiles='stitch'/%3E%3CfeColorMatrix values='0 0 0 0 0.1 0 0 0 0 0.08 0 0 0 0 0.05 0 0 0 0.08 0'/%3E%3C/filter%3E%3Crect width='200' height='200' filter='url(%23n)'/%3E%3C/svg%3E");
    opacity:0.5; z-index:1; mix-blend-mode:multiply;
  }}
  .wrap {{ max-width:880px; margin:0 auto; padding:40px 24px; position:relative; z-index:2; }}

  .breadcrumb {{ font-size:0.75rem; color:var(--ink-faded); margin-bottom:24px; }}
  .breadcrumb a {{ color:var(--seal); text-decoration:none; }}
  .breadcrumb a:hover {{ text-decoration:underline; }}
  .breadcrumb span {{ margin:0 6px; }}

  .passport {{
    background: var(--paper);
    border: 1px solid var(--rule);
    box-shadow:
      0 1px 0 rgba(28,24,20,0.04),
      0 20px 40px -20px rgba(28,24,20,0.15),
      0 60px 100px -60px rgba(28,24,20,0.1);
  }}

  /* HEADER */
  .pp-header {{
    padding: 28px 40px 24px;
    border-bottom: 2px solid var(--ink);
    display: flex; justify-content:space-between; align-items:flex-start; gap:24px;
    position:relative;
  }}
  .pp-header::after {{
    content:''; position:absolute; left:40px; right:40px; bottom:-7px;
    border-bottom:1px solid var(--ink);
  }}
  .pp-issuer {{
    font-family:'Fraunces',serif; font-weight:600; font-size:10px;
    letter-spacing:0.28em; text-transform:uppercase; color:var(--seal); margin-bottom:5px;
  }}
  .pp-doc-title {{
    font-family:'Fraunces',serif; font-weight:400; font-style:italic;
    font-size:26px; line-height:1; color:var(--ink);
  }}
  .pp-subtitle {{
    margin-top:3px; font-size:10px; letter-spacing:0.18em;
    text-transform:uppercase; color:var(--ink-faded);
  }}
  .pp-seal {{
    width:80px; height:80px; border-radius:50%;
    border:1.5px solid var(--seal); flex-shrink:0;
    display:flex; flex-direction:column; align-items:center; justify-content:center;
    text-align:center; color:var(--seal);
    background:radial-gradient(circle at center, var(--paper) 60%, rgba(110,24,24,0.06));
    position:relative;
  }}
  .pp-seal::before {{
    content:''; position:absolute; inset:5px; border-radius:50%;
    border:0.5px solid var(--seal);
  }}
  .pp-seal-label {{ font-family:'Fraunces',serif; font-style:italic; font-size:8px; letter-spacing:0.12em; text-transform:uppercase; line-height:1.2; }}
  .pp-seal-score {{ font-family:'JetBrains Mono',monospace; font-size:18px; font-weight:700; margin-top:2px; }}
  .pp-seal-unit  {{ font-family:'Fraunces',serif; font-style:italic; font-size:9px; color:var(--gold); }}

  /* META BAR */
  .pp-meta {{
    padding:12px 40px;
    background:var(--paper-deep);
    display:flex; gap:32px; flex-wrap:wrap;
    border-bottom:1px solid var(--rule);
  }}
  .pp-meta dl {{ display:flex; flex-direction:column; gap:2px; }}
  .pp-meta dt {{ font-size:8px; letter-spacing:0.2em; text-transform:uppercase; color:var(--ink-faded); font-weight:500; }}
  .pp-meta dd {{ font-family:'JetBrains Mono',monospace; font-size:11px; color:var(--ink); font-weight:500; }}

  /* HERO */
  .pp-hero {{
    padding:36px 40px 28px;
    display:grid; grid-template-columns:200px 1fr; gap:36px;
    border-bottom:1px solid var(--rule);
  }}
  @media (max-width:640px) {{ .pp-hero {{ grid-template-columns:1fr; }} }}
  .no-image {{
    width:100%; aspect-ratio:3/4; background:var(--paper-deep);
    border:1px solid var(--rule); display:flex; align-items:center;
    justify-content:center; font-family:'Fraunces',serif;
    font-style:italic; color:var(--ink-faded); font-size:12px; text-align:center;
    padding:16px;
  }}
  .tombstone-label {{
    font-size:9px; letter-spacing:0.22em; text-transform:uppercase;
    color:var(--ink-faded); font-weight:500; margin-bottom:6px;
  }}
  .tombstone-title {{
    font-family:'Fraunces',serif; font-style:italic; font-weight:400;
    font-size:36px; line-height:1.05; letter-spacing:-0.01em;
    color:var(--ink); margin-bottom:4px;
  }}
  .tombstone-artist {{
    font-family:'Fraunces',serif; font-weight:500; font-size:17px;
    color:var(--ink-soft); margin-bottom:2px;
  }}
  .tombstone-dates {{
    font-size:12px; color:var(--ink-faded); letter-spacing:0.04em; margin-bottom:16px;
  }}
  .tombstone-grid {{
    display:grid; grid-template-columns:100px 1fr;
    row-gap:6px; column-gap:12px;
    padding-top:16px; border-top:1px solid var(--rule);
  }}
  .tombstone-grid dt {{ font-size:9px; letter-spacing:0.18em; text-transform:uppercase; color:var(--ink-faded); font-weight:500; padding-top:2px; }}
  .tombstone-grid dd {{ font-size:13px; color:var(--ink); }}

  /* SECTIONS */
  .pp-section {{ padding:28px 40px; border-bottom:1px solid var(--rule); }}
  .pp-section:last-child {{ border-bottom:none; }}
  .pp-section-title {{
    font-size:9px; letter-spacing:0.24em; text-transform:uppercase;
    color:var(--ink-faded); font-weight:600; margin-bottom:16px;
  }}

  .score-table {{ width:100%; border-collapse:collapse; }}

  /* FOOTER */
  .pp-footer {{
    padding:20px 40px;
    background:var(--paper-deep);
    border-top:1px solid var(--rule);
    display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:12px;
  }}
  .pp-footer-id {{ font-family:'JetBrains Mono',monospace; font-size:11px; color:var(--ink-faded); }}
  .pp-footer-link {{ font-size:11px; color:var(--seal); text-decoration:none; }}
  .pp-footer-link:hover {{ text-decoration:underline; }}

  @media print {{
    body {{ background:white; background-image:none; }}
    body::before {{ display:none; }}
    .breadcrumb {{ display:none; }}
    .passport {{ box-shadow:none; border:1px solid #ccc; }}
  }}
</style>
{jld_script}
</head>
<body>
<div class="wrap">

  <nav class="breadcrumb">
    <a href="/">Ars Accordia</a>
    <span>›</span>
    <a href="/collections/">Collections</a>
    <span>›</span>
    <a href="/collections/lnmm/">LNMM Portrait Collection</a>
    <span>›</span>
    {title}
  </nav>

  <article class="passport">

    <header class="pp-header">
      <div>
        <div class="pp-issuer">Ars Accordia · Artwork Passport</div>
        <div class="pp-doc-title">{title}</div>
        <div class="pp-subtitle">{artist} · {year} · {collection}</div>
      </div>
      <div class="pp-seal">
        <div class="pp-seal-label">Ars Accordia Score</div>
        <div class="pp-seal-score">{ps}</div>
        <div class="pp-seal-unit">{band_}</div>
      </div>
    </header>

    <div class="pp-meta">
      <dl><dt>ArtBase ID</dt><dd>{ab_id}</dd></dl>
      <dl><dt>Object type</dt><dd>{obj_type}</dd></dl>
      <dl><dt>Inventory no.</dt><dd>{inv}</dd></dl>
      <dl><dt>Score</dt><dd>{ps} / 100</dd></dl>
      <dl><dt>Status</dt><dd>{badge}</dd></dl>
    </div>

    <section class="pp-hero">
      <div>
        <div class="no-image">No photograph<br>on record</div>
      </div>
      <div>
        <div class="tombstone-label">Work identity</div>
        <div class="tombstone-title">{title}</div>
        <div class="tombstone-artist">{artist}</div>
        <div class="tombstone-dates">{dates}</div>
        <dl class="tombstone-grid">
          <dt>Date</dt><dd>{year}</dd>
          <dt>Medium</dt><dd>{medium}</dd>
          <dt>Dimensions</dt><dd>{dims}</dd>
          <dt>Inventory</dt><dd>{inv}</dd>
          <dt>Collection</dt><dd>{collection}</dd>
        </dl>
      </div>
    </section>

    <section class="pp-section">
      <div class="pp-section-title">Authority links · {auth_label}</div>
      <dl style="margin:0">
        {auth_html if auth_html else '<div style="font-size:0.85rem;color:var(--ink-faded);font-style:italic">No authority links recorded</div>'}
      </dl>
    </section>

    <section class="pp-section">
      <div class="pp-section-title">Provenance · {len(prov)} step{'s' if len(prov) != 1 else ''}</div>
      {prov_html if prov_html else '<div style="font-size:0.85rem;color:var(--ink-faded);font-style:italic">No provenance recorded</div>'}
    </section>

    {'<section class="pp-section"><div class="pp-section-title">Sources</div>' + sources_html + '</section>' if sources_html else ''}

    <section class="pp-section">
      <div class="pp-section-title">Documentation score · {band_}</div>
      <table class="score-table">
        <thead>
          <tr style="border-bottom:2px solid var(--ink)">
            <th style="text-align:left;padding:6px 12px 6px 0;font-size:0.7rem;letter-spacing:0.14em;text-transform:uppercase;color:var(--ink-faded);font-weight:600">Section</th>
            <th style="text-align:left;padding:6px 12px;font-size:0.7rem;letter-spacing:0.14em;text-transform:uppercase;color:var(--ink-faded);font-weight:600">Coverage</th>
            <th style="text-align:right;padding:6px 0 6px 12px;font-size:0.7rem;letter-spacing:0.14em;text-transform:uppercase;color:var(--ink-faded);font-weight:600">Weight × Fill = Contrib</th>
          </tr>
        </thead>
        <tbody>
          {score_rows}
          <tr>
            <td colspan="2" style="padding:12px 12px 0 0;font-size:0.8rem;font-weight:600;color:var(--ink)">Passport score</td>
            <td style="padding:12px 0 0 12px;text-align:right;font-family:'JetBrains Mono',monospace;font-size:1rem;font-weight:700;color:var(--seal)">{ps} / 100</td>
          </tr>
        </tbody>
      </table>
      <p style="margin-top:12px;font-size:0.7rem;color:var(--ink-faded)">Weights-v3 · condition and image out of scope for museum-held works not commissioned for physical assessment · <a href="/method/" style="color:var(--seal)">methodology</a></p>
    </section>

    <footer class="pp-footer">
      <span class="pp-footer-id">{ab_id}</span>
      <a href="/collections/lnmm/" class="pp-footer-link">← LNMM Portrait Collection</a>
    </footer>

  </article>
</div>
</body>
</html>
'''
    out_dir = OUT_BASE / work_id
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "index.html"
    out_path.write_text(html, encoding="utf-8")
    return out_path

if __name__ == "__main__":
    for w in WORKS:
        p = generate_passport(w)
        print(f"  wrote {p}")
    print("Done.")
