"""
artbase_export/importer/base.py

Shared utilities for HTML table parsing and field normalisation.
Used by both lnma.py and swedbank.py.
"""

from __future__ import annotations

import re
from html.parser import HTMLParser
from pathlib import Path


# ── HTML table parser ──────────────────────────────────────────────────────────

class _TableParser(HTMLParser):
    """Extract all <tbody> rows from an HTML file as lists of cell strings."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._in_head  = False
        self._in_body  = False
        self._in_row   = False
        self._in_cell  = False
        self._cell: list[str] = []
        self._row:  list[str] = []
        self.headers: list[str] = []
        self.rows:    list[list[str]] = []

    def handle_starttag(self, tag: str, attrs: list) -> None:
        if tag == "thead":
            self._in_head = True
        elif tag == "tbody":
            self._in_body = True
        elif tag == "tr":
            self._in_row = True
            self._row = []
        elif tag in ("td", "th"):
            self._in_cell = True
            self._cell = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "thead":
            self._in_head = False
        elif tag == "tbody":
            self._in_body = False
        elif tag == "tr":
            self._in_row = False
            if self._in_head and self._row:
                self.headers = self._row[:]
            elif self._in_body and self._row:
                self.rows.append(self._row[:])
        elif tag in ("td", "th"):
            self._in_cell = False
            self._row.append("".join(self._cell).strip())
            self._cell = []

    def handle_data(self, data: str) -> None:
        if self._in_cell:
            self._cell.append(data)


def parse_html_table(path: Path) -> list[dict[str, str]]:
    """
    Parse the first HTML <table> with a <thead>/<tbody> into a list of row dicts.
    Keys are the column headers; values are cell text (entities already decoded).
    """
    parser = _TableParser()
    parser.feed(path.read_text(encoding="utf-8"))
    if not parser.headers:
        raise ValueError(f"No table headers found in {path}")
    return [dict(zip(parser.headers, row)) for row in parser.rows]


# ── Field parsers ──────────────────────────────────────────────────────────────

def parse_lifespan(s: str) -> tuple[int | None, int | None]:
    """
    Parse artist lifespan strings into (birth_year, death_year).

    Handles:
        '1866–1916'  (en-dash)
        '1872/1945'  (slash)
        '1866-1916'  (hyphen)
        '1866–'      (open-ended, i.e. living at time of record)
    Returns (None, None) if unparseable.
    """
    if not s or not isinstance(s, str):
        return None, None
    s = s.strip().replace("/", "–").replace("-", "–")
    parts = s.split("–")
    birth = _to_int(parts[0]) if len(parts) >= 1 else None
    death = _to_int(parts[1]) if len(parts) >= 2 else None
    return birth, death


def parse_lnma_dimensions(s: str) -> tuple[float | None, float | None]:
    """
    Parse LNMA dimension strings into (height_cm, width_cm).

    Handles:
        '147.5 (h) x 71 (w) cm'
        '72 (h) x 101,3 (w) cm'   ← European comma decimal
        '66,5 (h) x 48 (w) cm'
    Returns (None, None) if the pattern is absent.
    """
    if not s or not isinstance(s, str):
        return None, None
    s = s.replace(",", ".")
    m = re.search(r"([\d.]+)\s*\(h\)\s*[xX×]\s*([\d.]+)\s*\(w\)", s)
    if m:
        return float(m.group(1)), float(m.group(2))
    return None, None


def parse_swedbank_dimensions(s: str) -> tuple[float | None, float | None]:
    """
    Parse Swedbank dimension strings into (height_cm, width_cm).

    Handles:
        '86 x 43.5'
        '150 x 220'
        '90.2 x 8.5'
    Skips and returns (None, None) for compound formats:
        '4 x (30 x 30)'    (multi-part works)
        '5 x (20 x 30)'
        '50 x 61; 41 x 24; ...'   (set of miniatures)
        'Ø 65 cm'          (diameter notation)
    """
    if not s or not isinstance(s, str):
        return None, None
    if "(" in s or ";" in s or "Ø" in s or s.count("x") > 1:
        return None, None
    s = s.replace(",", ".")
    m = re.match(r"^\s*([\d.]+)\s*[xX×]\s*([\d.]+)", s)
    if m:
        return float(m.group(1)), float(m.group(2))
    return None, None


def parse_year(s: str) -> tuple[str, int | None, int | None]:
    """
    Parse year strings into (display, date_start, date_end).

    '2003'              → ('2003', 2003, 2003)
    '2006/2007'         → ('2006–2007', 2006, 2007)
    '1988/1989'         → ('1988–1989', 1988, 1989)
    '1915/1916'         → ('c. 1915–1916', 1915, 1916)
    '20. gs. 30. gadi'  → ('1930s', None, None)    ← Latvian "20th c. 1930s"
    ''                  → ('', None, None)
    """
    if not s or not isinstance(s, str):
        return "", None, None
    s = s.strip()

    # Latvian decade notation: '20. gs. 30. gadi' → '1930s'
    if "gs." in s or "gadi" in s:
        m_decade   = re.search(r"(\d+)\.\s*gadi", s)
        m_century  = re.search(r"(\d+)\.\s*gs", s)
        if m_decade:
            decade_num  = int(m_decade.group(1))
            century_num = int(m_century.group(1)) if m_century else 20
            year_start  = (century_num - 1) * 100 + decade_num
            return f"{year_start}s", None, None
        return s, None, None

    # Year range with slash or dash: '2006/2007', '1988–1989'
    m = re.match(r"^(\d{4})[/–-](\d{4})$", s)
    if m:
        y1, y2 = int(m.group(1)), int(m.group(2))
        disp = f"c. {y1}–{y2}" if abs(y2 - y1) <= 3 else f"{y1}–{y2}"
        return disp, y1, y2

    # Single four-digit year
    m = re.match(r"^(\d{4})$", s)
    if m:
        y = int(m.group(1))
        return s, y, y

    # Fallback: keep display string, no parsed years
    return s, None, None


def sort_name(display: str) -> str:
    """
    Invert display name to sort form.
    'Janis Rozentāls' → 'Rozentāls, Janis'
    Single-word names are returned unchanged.
    """
    parts = display.strip().rsplit(" ", 1)
    if len(parts) == 2:
        return f"{parts[1]}, {parts[0]}"
    return display


def extract_medium_en(medium_raw: str) -> str:
    """
    Extract the English portion from a bilingual Latvian/English medium string.

    Page 222 pattern  (slash-separated):
        'papīrs / litogrāfija / lithograph on paper'  →  'lithograph on paper'
    Pages 223–229 pattern  (comma-only, no slash):
        'audekls, eļļa'  →  'audekls, eļļa'  (returned as-is; needs manual review)
    """
    if not medium_raw:
        return ""
    if " / " in medium_raw:
        return medium_raw.split(" / ")[-1].strip()
    return medium_raw.strip()


# ── Internal helpers ───────────────────────────────────────────────────────────

def _to_int(s: str) -> int | None:
    try:
        return int(s.strip())
    except (ValueError, AttributeError):
        return None
