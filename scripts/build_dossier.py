#!/usr/bin/env python3
"""
build_dossier.py — Generate a Collection Documentation Dossier HTML file.

Reads a collection JSON (COL-*.json) and its member passport JSONs;
renders a self-contained, print-ready HTML dossier in the Ars Accordia
brand language (Fraunces / Public Sans / JetBrains Mono, paper/oxblood/gilt).

The dossier is the advisor show-piece: one file, printable to PDF,
clearly labelled "Sample — demonstration of an Ars Accordia documentation
dossier."

Usage:
    python3 scripts/build_dossier.py COL-LNMM
    python3 scripts/build_dossier.py COL-HANSABANKA --out custom-name.html
    python3 scripts/build_dossier.py --all

From copilot-spec-15-lnmm-giveback-and-dossier.md (Part D).
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from html import escape

REPO_ROOT       = Path(__file__).resolve().parent.parent
COLLECTIONS_DIR = REPO_ROOT / "artbase_export" / "data" / "collections"
ARTWORKS_DIR    = REPO_ROOT / "artbase_export" / "data" / "artworks"
DOSSIERS_DIR    = REPO_ROOT / "artbase_export" / "data" / "dossiers"


# ── Helpers ───────────────────────────────────────────────────────────────────

def find_passport(ap_id: str) -> dict | None:
    """Locate a passport JSON by its ID (handles nested paths and flat filenames)."""
    parts = ap_id.split("/")
    candidates = [
        ARTWORKS_DIR / Path(*parts).with_suffix(".json"),
        ARTWORKS_DIR / f"{ap_id.replace('/', '_')}.json",
        ARTWORKS_DIR / f"{ap_id}.json",
    ]
    for c in candidates:
        if c.exists():
            return json.loads(c.read_text())
    return None


def status_label(status: str) -> tuple[str, str]:
    """Returns (css_class, text) for a cross-reference status."""
    return {
        "green": ("badge-green", "Cross-referenced · reviewed"),
        "amber": ("badge-amber", "Cross-referenced · pending review"),
        "grey":  ("badge-grey",  "No public authority cross-reference yet"),
    }.get(status, ("badge-grey", "—"))


def fmt_pct(v: float | None) -> str:
    if v is None:
        return "—"
    return f"{round(v * 100)}%"


def authority_links_html(authority_links: dict) -> str:
    """Render authority links as a compact list of clickable badges."""
    items = []
    label_map = {
        "wikidata":       ("Wikidata", "https://www.wikidata.org/wiki/{}"),
        "artist_wikidata":("Artist · Wikidata", "https://www.wikidata.org/wiki/{}"),
        "artist_ulan":    ("Artist · ULAN", "http://vocab.getty.edu/ulan/{}"),
        "ulan":           ("ULAN", "http://vocab.getty.edu/ulan/{}"),
        "viaf":           ("VIAF", "https://viaf.org/viaf/{}"),
        "isni":           ("ISNI", "https://isni.org/isni/{}"),
        "rkd":            ("RKD", "https://rkd.nl/en/explore/artists/{}"),
    }
    for key, (lbl, uri_tpl) in label_map.items():
        entry = authority_links.get(key) or {}
        if not isinstance(entry, dict):
            continue
        qid = entry.get("id")
        status = entry.get("status", "")
        if qid and status in ("confirmed", "working"):
            uri = uri_tpl.format(qid)
            items.append(
                f'<a href="{escape(uri)}" class="auth-badge" target="_blank">'
                f'{escape(lbl)} <span class="auth-id">{escape(str(qid))}</span></a>'
            )
    return "\n".join(items) if items else '<span class="none">—</span>'


def provenance_html(provenance: list[dict]) -> str:
    if not provenance:
        return '<p class="none">No provenance recorded.</p>'
    rows = []
    for step in provenance:
        desc = escape(step.get("description") or "—")
        src  = step.get("source") or ""
        note = step.get("source_note") or ""
        gap  = step.get("is_gap", False)
        src_cell = ""
        if src:
            src_cell = f'<span class="prov-src">{escape(src)}</span>'
            if note:
                src_cell += f' <span class="prov-note">{escape(note[:120])}{"…" if len(note) > 120 else ""}</span>'
        elif gap:
            src_cell = '<span class="prov-gap">⚠ source gap — citation pending verification</span>'
        gap_cls   = "  prov-gap-row" if gap else ""
        src_wrap  = f'<div class="prov-src-wrap">{src_cell}</div>' if src_cell else ""
        rows.append(
            f'<div class="prov-step{gap_cls}">'
            f'<div class="prov-desc">{desc}</div>'
            f'{src_wrap}'
            f'</div>'
        )
    return "\n".join(rows)


# ── CSS ───────────────────────────────────────────────────────────────────────

CSS = """
:root {
  --paper:       #F9F6F0;
  --seal:        #6E1818;
  --ink:         #2A2320;
  --ink-soft:    #5A4E4A;
  --ink-faded:   #9A8E8A;
  --rule:        #DDD8D0;
  --gold:        #B8960A;
  --amber-bg:    #FFF9ED;
  --amber-bd:    #B87C15;
  --green-bg:    #F0FAF4;
  --green-bd:    #1A7A3A;
  --grey-bd:     #9A8E8A;
}

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: 'Public Sans', sans-serif;
  font-size: 13px;
  color: var(--ink);
  background: var(--paper);
  line-height: 1.6;
}

/* ── Brand fonts ── */
.serif  { font-family: 'Fraunces', Georgia, serif; }
.mono   { font-family: 'JetBrains Mono', monospace; }

/* ── Page model ── */
.page {
  width: 210mm;
  min-height: 297mm;
  margin: 0 auto 4mm;
  padding: 20mm 18mm 16mm;
  background: white;
  border: 1px solid var(--rule);
  position: relative;
  page-break-after: always;
}
.page:last-child { page-break-after: auto; }

/* ── Sample watermark ── */
.sample-banner {
  position: absolute;
  top: 8mm;
  right: 10mm;
  font-size: 9px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  color: white;
  background: var(--seal);
  padding: 3px 10px;
  border-radius: 2px;
}

/* ── Cover ── */
.cover-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 24mm;
}
.cover-logo-mark {
  width: 32px;
  height: 32px;
  background: var(--seal);
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 3px;
  padding: 4px;
  border-radius: 2px;
}
.cover-logo-mark span {
  background: white;
  border-radius: 1px;
  opacity: 0.9;
}
.cover-logo-name {
  font-family: 'Public Sans', sans-serif;
  font-size: 14px;
  font-weight: 600;
  color: var(--ink);
  letter-spacing: 0.04em;
}

.cover-collection {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--seal);
  font-weight: 600;
  margin-bottom: 8px;
}
.cover-title {
  font-family: 'Fraunces', Georgia, serif;
  font-size: 28px;
  font-weight: 700;
  font-style: italic;
  color: var(--ink);
  line-height: 1.15;
  letter-spacing: -0.02em;
  margin-bottom: 14mm;
}
.cover-score-block {
  border-left: 3px solid var(--seal);
  padding: 10px 0 10px 16px;
  margin-bottom: 12mm;
  display: flex;
  align-items: baseline;
  gap: 20px;
  flex-wrap: wrap;
}
.cover-score-number {
  font-family: 'Fraunces', Georgia, serif;
  font-size: 56px;
  font-weight: 700;
  color: var(--seal);
  line-height: 1;
  letter-spacing: -0.03em;
}
.cover-score-meta { display: flex; flex-direction: column; gap: 4px; }
.cover-score-label {
  font-size: 9px;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--ink-faded);
  font-weight: 600;
}
.cover-score-band {
  font-family: 'Fraunces', Georgia, serif;
  font-size: 18px;
  font-style: italic;
  color: var(--ink);
}
.cover-score-sub {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  color: var(--ink-soft);
}

.cover-meta-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-top: 16mm;
  padding-top: 8px;
  border-top: 1px solid var(--rule);
}
.cover-meta-item { display: flex; flex-direction: column; gap: 2px; }
.cover-meta-label {
  font-size: 9px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--ink-faded);
  font-weight: 600;
}
.cover-meta-value {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  color: var(--ink);
}

.cover-footer {
  position: absolute;
  bottom: 14mm;
  left: 18mm;
  right: 18mm;
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  border-top: 1px solid var(--rule);
  padding-top: 8px;
}
.cover-footer-note {
  font-size: 9px;
  color: var(--ink-faded);
  font-style: italic;
  max-width: 120mm;
  line-height: 1.5;
}
.cover-footer-url {
  font-family: 'JetBrains Mono', monospace;
  font-size: 9px;
  color: var(--seal);
}

/* ── Section pages ── */
.section-eyebrow {
  font-size: 9px;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--seal);
  font-weight: 600;
  margin-bottom: 6px;
}
.section-heading {
  font-family: 'Fraunces', Georgia, serif;
  font-size: 20px;
  font-style: italic;
  color: var(--ink);
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--rule);
}
.section-body { line-height: 1.7; color: var(--ink-soft); }
.section-body p { margin-bottom: 10px; }
.section-body strong { color: var(--ink); }

/* ── Gap map ── */
.gap-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 12px;
}
.gap-table th {
  font-size: 9px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--ink-faded);
  font-weight: 600;
  text-align: left;
  padding: 6px 10px 6px 0;
  border-bottom: 1px solid var(--rule);
}
.gap-table td {
  padding: 8px 10px 8px 0;
  border-bottom: 1px solid var(--rule);
  font-size: 12px;
  vertical-align: top;
}
.gap-table .td-section { font-weight: 500; color: var(--ink); }
.gap-table .td-fill {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  color: var(--ink);
  width: 60px;
}
.gap-bar-wrap { width: 80px; padding-top: 4px; }
.gap-bar-bg {
  height: 4px;
  background: var(--rule);
  border-radius: 2px;
  overflow: hidden;
}
.gap-bar-fill {
  height: 100%;
  background: var(--seal);
  border-radius: 2px;
}
.gap-table .td-note { color: var(--ink-soft); font-size: 11px; }

/* ── Passport cards ── */
.passport-card {
  border: 1px solid var(--rule);
  border-radius: 3px;
  margin-bottom: 14px;
  padding: 14px 16px;
}
.passport-card-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 10px;
  gap: 12px;
}
.passport-card-title {
  font-family: 'Fraunces', Georgia, serif;
  font-size: 15px;
  font-style: italic;
  color: var(--ink);
  line-height: 1.2;
}
.passport-card-artist {
  font-size: 11px;
  color: var(--ink-soft);
  margin-top: 2px;
}
.passport-card-score {
  font-family: 'JetBrains Mono', monospace;
  font-size: 22px;
  font-weight: 600;
  color: var(--seal);
  white-space: nowrap;
}
.passport-card-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px 16px;
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid var(--rule);
}
.passport-card-field { display: flex; flex-direction: column; gap: 2px; }
.passport-card-label {
  font-size: 9px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--ink-faded);
  font-weight: 600;
}
.passport-card-value {
  font-size: 11px;
  color: var(--ink);
}
.passport-card-value.mono {
  font-family: 'JetBrains Mono', monospace;
}

.auth-links { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 4px; }
.auth-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 7px;
  border: 1px solid var(--rule);
  border-radius: 2px;
  font-size: 10px;
  color: var(--ink-soft);
  text-decoration: none;
  background: white;
}
.auth-badge:hover { border-color: var(--seal); color: var(--seal); }
.auth-id {
  font-family: 'JetBrains Mono', monospace;
  font-size: 9px;
  color: var(--seal);
}
.none { color: var(--ink-faded); font-style: italic; font-size: 11px; }

/* ── Status badges ── */
.badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 2px;
  border: 1px solid;
  font-size: 10px;
  font-weight: 500;
  white-space: nowrap;
}
.badge-green  { border-color: var(--green-bd); color: var(--green-bd); background: var(--green-bg); }
.badge-amber  { border-color: var(--amber-bd); color: var(--amber-bd); background: var(--amber-bg); }
.badge-grey   { border-color: var(--grey-bd);  color: var(--grey-bd);  background: white; }

/* ── Provenance ── */
.prov-step {
  padding: 7px 0;
  border-bottom: 1px solid var(--rule);
}
.prov-step:last-child { border-bottom: none; }
.prov-desc { font-size: 11px; color: var(--ink); margin-bottom: 3px; }
.prov-src-wrap { margin-top: 2px; }
.prov-src { font-family: 'JetBrains Mono', monospace; font-size: 9px; color: var(--seal); }
.prov-note { font-size: 10px; color: var(--ink-faded); margin-left: 6px; }
.prov-gap  { font-size: 10px; color: var(--amber-bd); }
.prov-gap-row { opacity: 0.7; }

/* ── Score section within card ── */
.score-row {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid var(--rule);
  align-items: center;
}
.score-number {
  font-family: 'JetBrains Mono', monospace;
  font-size: 28px;
  font-weight: 600;
  color: var(--seal);
}
.score-sections {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}
.score-sec {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.score-sec-label {
  font-size: 9px;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--ink-faded);
  font-weight: 600;
}
.score-sec-val {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  color: var(--ink);
}

/* ── Exports page ── */
.export-item {
  display: flex;
  gap: 14px;
  padding: 12px 0;
  border-bottom: 1px solid var(--rule);
}
.export-icon {
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px;
  color: var(--seal);
  font-weight: 600;
  white-space: nowrap;
  padding-top: 2px;
  min-width: 60px;
}
.export-text { font-size: 12px; color: var(--ink-soft); line-height: 1.5; }
.export-text strong { color: var(--ink); }

/* ── Page number ── */
.page-number {
  position: absolute;
  bottom: 10mm;
  right: 18mm;
  font-family: 'JetBrains Mono', monospace;
  font-size: 9px;
  color: var(--ink-faded);
}

/* ── Print ── */
@media print {
  body { background: white; }
  .page {
    width: 100%;
    margin: 0;
    border: none;
    padding: 16mm 16mm 14mm;
    page-break-after: always;
  }
  .page:last-child { page-break-after: auto; }
  a { color: inherit; text-decoration: none; }
}

@media screen {
  body { padding: 12px; background: #E8E4DC; }
}
"""


# ── Per-section gap note ──────────────────────────────────────────────────────

GAP_NOTES = {
    "identity":   "Title, creator, date, medium, dimensions, and object type.",
    "authority":  "Cross-references to public authority records (Wikidata, ULAN, VIAF, etc.). Target: 2 independent authorities per work.",
    "provenance": "Ownership chain with a cited source per step.",
    "structured": "Schema.org JSON-LD and LIDO/EODEM export record.",
    "condition":  "Condition assessment (only when commissioned).",
    "image":      "Verified image (only when commissioned).",
}


# ── HTML builder ─────────────────────────────────────────────────────────────

def build_html(col: dict, passports: list[dict], today: str) -> str:
    score     = col.get("score") or {}
    aa_score  = score.get("ars_accordia_score", 0)
    avg_std   = score.get("average_standard")
    n_works   = score.get("works_documented", 0)
    band      = score.get("band") or "—"
    gaps      = score.get("gaps") or {}
    col_name  = col.get("name", "Collection")

    avg_display  = f"{avg_std:.1f}" if avg_std is not None else "—"
    score_display = f"{int(aa_score)}" if aa_score == int(aa_score) else f"{aa_score}"

    # ── Cover ────────────────────────────────────────────────────────────────
    cover = f"""
<div class="page" id="cover">
  <div class="sample-banner">Sample — demonstration</div>

  <div class="cover-logo">
    <div class="cover-logo-mark">
      <span></span><span style="opacity:.5"></span>
      <span style="opacity:.5"></span><span style="opacity:.75"></span>
    </div>
    <span class="cover-logo-name">Ars Accordia</span>
  </div>

  <div class="cover-collection">Collection Documentation Dossier</div>
  <div class="cover-title serif">{escape(col_name)}</div>

  <div class="cover-score-block">
    <div class="cover-score-number">{escape(score_display)}</div>
    <div class="cover-score-meta">
      <span class="cover-score-label">Ars Accordia Score</span>
      <span class="cover-score-band">{escape(band)}</span>
      <span class="cover-score-sub">{n_works} works documented · avg standard {avg_display}</span>
    </div>
  </div>

  <div class="cover-meta-grid">
    <div class="cover-meta-item">
      <span class="cover-meta-label">Prepared by</span>
      <span class="cover-meta-value">Ars Accordia</span>
    </div>
    <div class="cover-meta-item">
      <span class="cover-meta-label">Date</span>
      <span class="cover-meta-value">{escape(today)}</span>
    </div>
    <div class="cover-meta-item">
      <span class="cover-meta-label">Works documented</span>
      <span class="cover-meta-value">{n_works}</span>
    </div>
    <div class="cover-meta-item">
      <span class="cover-meta-label">Config</span>
      <span class="cover-meta-value">{escape(score.get("config_version", "weights-v3"))}</span>
    </div>
  </div>

  <div class="cover-footer">
    <div class="cover-footer-note">
      This dossier is a sample generated by Ars Accordia for demonstration purposes.
      All scores are computed from the records shown — no figure is hand-set.
      Scoring methodology: <strong>arsaccordia.com/method/</strong>
    </div>
    <div class="cover-footer-url">arsaccordia.com</div>
  </div>
  <div class="page-number">1</div>
</div>
"""

    # ── Summary ──────────────────────────────────────────────────────────────
    band_explanation = {
        "Complete Record":    "Records are fully identified, cross-referenced to two or more independent public authorities, provenance is sourced, and structured data is present. The collection is in a state where each work can be verified, exchanged, and published.",
        "Substantial Record": "Records are largely complete. Most works are identified and cross-referenced, but some gaps remain — typically in provenance sourcing or a second authority link. The priority next step is shown in the gap map below.",
        "Partial Record":     "Records establish a baseline identity for each work, but authority cross-references or provenance sourcing are incomplete. The gap map shows exactly where to invest next.",
        "Outline Record":     "A basic outline is in place, but significant cataloguing work remains across all sections. This is the starting point for a systematic documentation engagement.",
        "Minimal Record":     "Records are at an early stage. Identity fields need completion before authority or provenance work can proceed effectively.",
    }.get(band, "The band reflects the average standard across all documented works.")

    summary = f"""
<div class="page" id="summary">
  <div class="sample-banner">Sample — demonstration</div>
  <div class="section-eyebrow">About this dossier</div>
  <div class="section-heading serif">What this score means</div>
  <div class="section-body">
    <p>The <strong>Ars Accordia Score</strong> for <em>{escape(col_name)}</em> is <strong>{escape(score_display)}</strong> — the sum of the individual Passport Scores for the {n_works} work{"s" if n_works != 1 else ""} documented here.</p>
    <p>The <strong>average standard</strong> of <strong>{avg_display}</strong> places this collection in the <strong>{escape(band)}</strong> band. {escape(band_explanation)}</p>
    <p>The Passport Score for each work is computed from four sections:</p>
    <ul style="margin: 8px 0 12px 20px; line-height: 1.9;">
      <li><strong>Identity (35%)</strong> — title, creator, date, medium, dimensions, object type</li>
      <li><strong>Authority links (25%)</strong> — cross-references to independent public authority records (Wikidata, Getty ULAN, VIAF, etc.)</li>
      <li><strong>Provenance sourced (25%)</strong> — ownership chain with a cited, verifiable source per step</li>
      <li><strong>Structured / export (15%)</strong> — Schema.org JSON-LD and LIDO/EODEM exchange record</li>
    </ul>
    <p>No figure is hand-set. The score for each work follows directly from what is recorded in its passport — a higher score means more complete, more cross-referenced, and more verifiable documentation. Scores rise as gaps are filled.</p>
    <p style="color: var(--ink-faded); font-size: 11px; margin-top: 16px;">
      Full methodology: <strong style="color:var(--seal)">arsaccordia.com/method/</strong> · Config: {escape(score.get("config_version", "weights-v3"))}
    </p>
  </div>
  <div class="page-number">2</div>
</div>
"""

    # ── Gap map ──────────────────────────────────────────────────────────────
    # Compute average fill per section from the passports
    section_keys = ["identity", "authority", "provenance", "structured"]
    section_fills: dict[str, list[float]] = {k: [] for k in section_keys}
    for p in passports:
        sections = (p.get("score") or {}).get("completeness", {}).get("sections") or []
        for sec in sections:
            name = sec.get("section")
            fill = sec.get("fill")
            in_scope = sec.get("in_scope", True)
            if name in section_fills and in_scope and fill is not None:
                section_fills[name].append(fill)

    gap_rows = ""
    for sec in section_keys:
        fills = section_fills[sec]
        avg_fill = sum(fills) / len(fills) if fills else 0.0
        pct = f"{round(avg_fill * 100)}%"
        bar_width = round(avg_fill * 100)
        note = GAP_NOTES.get(sec, "")
        label = sec.replace("_", " ").title()
        if sec == "provenance":
            label = "Provenance sourced"
        elif sec == "structured":
            label = "Structured / export"
        gap_rows += f"""
      <tr>
        <td class="td-section">{escape(label)}</td>
        <td class="td-fill">{pct}</td>
        <td><div class="gap-bar-wrap"><div class="gap-bar-bg"><div class="gap-bar-fill" style="width:{bar_width}%"></div></div></div></td>
        <td class="td-note">{escape(note)}</td>
      </tr>"""

    gapmap = f"""
<div class="page" id="gapmap">
  <div class="sample-banner">Sample — demonstration</div>
  <div class="section-eyebrow">Where the records are thin</div>
  <div class="section-heading serif">Gap map</div>
  <p style="font-size:11px;color:var(--ink-soft);margin-bottom:14px;">
    Average fill per section across the {n_works} documented work{"s" if n_works != 1 else ""}. Gaps show where the next documentation action will raise scores most.
  </p>
  <table class="gap-table">
    <thead>
      <tr>
        <th style="width:140px">Section</th>
        <th style="width:60px">Avg fill</th>
        <th style="width:90px"> </th>
        <th>What this measures</th>
      </tr>
    </thead>
    <tbody>{gap_rows}
    </tbody>
  </table>
  <p style="margin-top:20px;font-size:11px;color:var(--ink-faded);line-height:1.6;">
    <strong style="color:var(--ink)">Reading this map:</strong> 100% means every documented work has a complete, verified entry for this section. 67% means 2 of 3 works have it. A section at 0% is the first priority for the next cataloguing phase.
  </p>
  <div class="page-number">3</div>
</div>
"""

    # ── Per-work records ──────────────────────────────────────────────────────
    work_pages = ""
    for i, passport in enumerate(passports, start=1):
        oi    = passport.get("object_id") or {}
        al    = passport.get("authority_links") or {}
        prov  = passport.get("provenance") or []
        loc   = passport.get("location") or {}
        sd    = passport.get("structured_data") or {}
        sc    = passport.get("score") or {}

        title   = oi.get("title") or "—"
        creator = oi.get("maker_display_name") or "—"
        date_d  = oi.get("date_display") or "—"
        medium  = oi.get("materials") or "—"
        obj_type= oi.get("object_type") or "—"
        dims    = oi.get("dimensions_display") or "—"
        inv     = loc.get("inventory_number") or "—"
        ap_id   = passport.get("artbase_id") or "—"

        ps      = sc.get("passport_score", "—")
        status  = sc.get("status", "grey")
        badge_cls, badge_txt = status_label(status)
        completeness = sc.get("completeness") or {}
        sections_sc  = completeness.get("sections") or []

        has_jld  = bool(sd.get("json_ld"))
        has_lido = bool(sd.get("lido") or sd.get("eodem"))
        exports_note = []
        if has_jld:
            exports_note.append("Schema.org JSON-LD")
        if has_lido:
            exports_note.append("LIDO/EODEM")
        exports_str = " · ".join(exports_note) if exports_note else "Not yet produced"

        # Section fills for this passport
        sec_display = ""
        for sec in sections_sc:
            if not sec.get("in_scope"):
                continue
            sname = sec.get("section", "").replace("_", " ").title()
            fill  = sec.get("fill")
            if fill is None:
                continue
            fill_pct = f"{round(fill * 100)}%"
            sec_display += f'<div class="score-sec"><span class="score-sec-label">{escape(sname)}</span><span class="score-sec-val">{fill_pct}</span></div>\n'

        work_pages += f"""
<div class="page" id="work-{i}">
  <div class="sample-banner">Sample — demonstration</div>
  <div class="section-eyebrow">Work {i} of {len(passports)}</div>

  <div class="passport-card">
    <div class="passport-card-header">
      <div>
        <div class="passport-card-title serif">{escape(title)}</div>
        <div class="passport-card-artist">{escape(creator)} · {escape(date_d)}</div>
      </div>
      <div style="text-align:right">
        <div class="passport-card-score">{escape(str(ps))}</div>
        <span class="badge {badge_cls}" style="margin-top:4px;display:inline-block;">● {escape(badge_txt)}</span>
      </div>
    </div>

    <div class="passport-card-grid">
      <div class="passport-card-field">
        <span class="passport-card-label">Object type</span>
        <span class="passport-card-value">{escape(obj_type)}</span>
      </div>
      <div class="passport-card-field">
        <span class="passport-card-label">Medium</span>
        <span class="passport-card-value">{escape(medium)}</span>
      </div>
      <div class="passport-card-field">
        <span class="passport-card-label">Dimensions</span>
        <span class="passport-card-value">{escape(dims)}</span>
      </div>
      <div class="passport-card-field">
        <span class="passport-card-label">Inventory</span>
        <span class="passport-card-value mono">{escape(inv)}</span>
      </div>
      <div class="passport-card-field" style="grid-column:1/-1">
        <span class="passport-card-label">Ars Accordia Passport ID</span>
        <span class="passport-card-value mono">{escape(ap_id)}</span>
      </div>
    </div>

    <div style="margin-top:12px;padding-top:12px;border-top:1px solid var(--rule)">
      <div class="passport-card-label" style="margin-bottom:6px">Authority cross-references</div>
      <div class="auth-links">{authority_links_html(al)}</div>
    </div>

    <div style="margin-top:12px;padding-top:12px;border-top:1px solid var(--rule)">
      <div class="passport-card-label" style="margin-bottom:6px">Provenance</div>
      {provenance_html(prov)}
    </div>

    <div style="margin-top:12px;padding-top:12px;border-top:1px solid var(--rule)">
      <div class="passport-card-label">Exports available</div>
      <div style="font-size:11px;color:var(--ink-soft);margin-top:3px;">{escape(exports_str)}</div>
    </div>

    <div class="score-row">
      <div class="score-number">{escape(str(ps))}</div>
      {sec_display}
    </div>
  </div>

  <div class="page-number">{3 + i}</div>
</div>
"""

    # ── Exports page ──────────────────────────────────────────────────────────
    exports_page = f"""
<div class="page" id="exports">
  <div class="sample-banner">Sample — demonstration</div>
  <div class="section-eyebrow">Machine-readable records</div>
  <div class="section-heading serif">Exports and exchange formats</div>
  <p style="font-size:12px;color:var(--ink-soft);margin-bottom:16px;line-height:1.7;">
    Each Ars Accordia passport is available in structured machine-readable formats for insurance,
    loans, museum exchange, and web discovery. These formats are generated from the same canonical
    record that drives the score — they are always consistent with the documented data.
  </p>

  <div class="export-item">
    <div class="export-icon">JSON-LD</div>
    <div class="export-text">
      <strong>Schema.org VisualArtwork</strong> — structured metadata for web discovery,
      Google Knowledge Panels, and aggregators such as Europeana. Embeds directly in the
      passport HTML and is consumable by any schema.org-aware indexer.
    </div>
  </div>

  <div class="export-item">
    <div class="export-icon">LIDO 1.1</div>
    <div class="export-text">
      <strong>Lightweight Information Describing Objects</strong> — the standard XML format
      for cultural object exchange between museums, registries, and aggregators.
      Used for OAI-PMH harvest and Europeana ingestion.
    </div>
  </div>

  <div class="export-item">
    <div class="export-icon">EODEM</div>
    <div class="export-text">
      <strong>Exhibition Object Data Exchange Model</strong> — the LIDO profile for loan
      documentation and facility reports, required by many European museums as a condition
      of incoming loans.
    </div>
  </div>

  <div class="export-item" style="border-bottom:none">
    <div class="export-icon">Wikidata</div>
    <div class="export-text">
      <strong>Public authority contribution</strong> — for each documented work, Ars Accordia
      contributes sourced facts back to Wikidata with book references (S248/S304), creating
      a permanent public record and bidirectional link from the Wikidata item to the passport.
      This is the give-back that makes the public graph richer for everyone.
    </div>
  </div>

  <div style="margin-top:24px;padding-top:12px;border-top:1px solid var(--rule);">
    <p style="font-size:11px;color:var(--ink-faded);line-height:1.6;">
      <strong style="color:var(--ink)">Ars Accordia</strong> · arsaccordia.com ·
      Scoring methodology: arsaccordia.com/method/ ·
      This dossier was generated on {escape(today)} and reflects the records as of that date.
      Scores will update as records are enriched.
    </p>
  </div>
  <div class="page-number">{3 + len(passports) + 1}</div>
</div>
"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Collection Documentation Dossier — {escape(col_name)} — Ars Accordia</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,ital,wght@9..144,0..1,300..900&family=Public+Sans:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap">
<style>
{CSS}
</style>
</head>
<body>
{cover}
{summary}
{gapmap}
{work_pages}
{exports_page}
</body>
</html>"""


# ── I/O ───────────────────────────────────────────────────────────────────────

def load_collection(col_id: str) -> tuple[dict, list[dict]]:
    col_path = COLLECTIONS_DIR / f"{col_id}.json"
    if not col_path.exists():
        raise FileNotFoundError(f"Collection not found: {col_path}")
    col = json.loads(col_path.read_text())
    members = col.get("member_passports") or []
    passports = []
    for ap_id in members:
        p = find_passport(ap_id)
        if p is None:
            print(f"  WARN  passport {ap_id} not found — skipped", file=sys.stderr)
        else:
            passports.append(p)
    return col, passports


def generate(col_id: str, out_path: Path | None = None) -> Path:
    col, passports = load_collection(col_id)
    today = date.today().isoformat()
    html  = build_html(col, passports, today)

    DOSSIERS_DIR.mkdir(parents=True, exist_ok=True)
    if out_path is None:
        out_path = DOSSIERS_DIR / f"{col_id}-dossier-{today}.html"
    out_path.write_text(html, encoding="utf-8")
    print(f"  dossier → {out_path.relative_to(REPO_ROOT)}")
    return out_path


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("collection", nargs="?", help="Collection ID (e.g. COL-LNMM)")
    parser.add_argument("--all", action="store_true", help="Generate dossiers for all collections")
    parser.add_argument("--out", type=Path, help="Output file path (single collection only)")
    args = parser.parse_args()

    if args.all:
        col_files = sorted(COLLECTIONS_DIR.glob("COL-*.json"))
        if not col_files:
            print("No collections found.", file=sys.stderr)
            sys.exit(1)
        for f in col_files:
            col_id = f.stem
            try:
                generate(col_id)
            except Exception as exc:
                print(f"  ERROR {col_id}: {exc}", file=sys.stderr)
    elif args.collection:
        generate(args.collection, args.out)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
