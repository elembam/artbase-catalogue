#!/usr/bin/env python3
"""
artist_pipeline.py — Reconcile an artist name against Wikidata, audit the
existing entry, and produce a QuickStatements file of proposed improvements
drawn from Wikipedia infobox data.

This is the operational tool referenced in the ArtBase Wikidata workflow.
Run it once per artist during cataloguing; review its output; submit the
QuickStatements via the web interface.

Usage:
    python3 artist_pipeline.py "Herberts Siliņš" --year 1926

Dependencies:
    pip install requests mwparserfromhell

Output:
    - Audit report (stdout): what Wikidata has, what's missing
    - QuickStatements file (artist_name.qs.txt): ready to submit
"""

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import re

try:
    import requests
    import mwparserfromhell
except ImportError:
    print("Install dependencies first:")
    print("    pip install requests mwparserfromhell")
    sys.exit(1)


# ---------- Configuration ----------

WIKIDATA_API = "https://www.wikidata.org/w/api.php"
WIKIDATA_SPARQL = "https://query.wikidata.org/sparql"
WIKIPEDIA_API = "https://en.wikipedia.org/w/api.php"
USER_AGENT = "ArtBaseCataloguer/0.1 (artbase.eu; contact@artbase.eu)"

# Language-code → Wikipedia API base URL (checked in order when no enwiki sitelink)
FALLBACK_WIKIS = [
    ("lv", "https://lv.wikipedia.org/w/api.php"),
    ("de", "https://de.wikipedia.org/w/api.php"),
    ("fr", "https://fr.wikipedia.org/w/api.php"),
    ("nl", "https://nl.wikipedia.org/w/api.php"),
    ("sv", "https://sv.wikipedia.org/w/api.php"),
]

# Properties we audit and propose
KEY_PROPERTIES = {
    "P31":   "instance of",
    "P21":   "sex or gender",
    "P27":   "country of citizenship",
    "P569":  "date of birth",
    "P570":  "date of death",
    "P19":   "place of birth",
    "P20":   "place of death",
    "P106":  "occupation",
    "P69":   "educated at",
    "P463":  "member of",
    "P135":  "movement",
    "P136":  "genre",
    "P101":  "field of work",
    "P245":  "Getty ULAN ID",
    "P214":  "VIAF ID",
    "P213":  "ISNI",
    "P650":  "RKDartists ID",
}

# Common artist-occupation Wikidata IDs (for proposed values)
OCCUPATION_TO_QID = {
    "painter":      "Q1028181",
    "sculptor":     "Q1281618",
    "photographer": "Q33231",
    "draughtsman":  "Q15296811",
    "printmaker":   "Q15296811",
}


# ---------- Data structures ----------

@dataclass
class WikidataEntry:
    qid: Optional[str] = None
    label: Optional[str] = None
    description: Optional[str] = None
    statements: dict = field(default_factory=dict)  # P-number → list of values
    refs_per_statement: dict = field(default_factory=dict)  # P-number → ref count
    wikipedia_title: Optional[str] = None       # English title if present
    sitelinks: dict = field(default_factory=dict)  # langcode → title


@dataclass
class ProposedEdit:
    pid: str          # Property
    value: str        # Value (Q-number, date, string)
    value_type: str   # "item", "time", "string", "monolingual"
    source_url: str   # The reference we'd cite
    rationale: str    # Why we propose this


# ---------- Wikidata reconciliation ----------

def search_wikidata(name: str, hint_year: Optional[int] = None) -> list[str]:
    """Search Wikidata for an artist by name; return matching QIDs."""
    params = {
        "action": "wbsearchentities",
        "search": name,
        "language": "en",
        "type": "item",
        "format": "json",
        "limit": 10,
    }
    r = requests.get(WIKIDATA_API, params=params,
                     headers={"User-Agent": USER_AGENT})
    r.raise_for_status()
    results = r.json().get("search", [])

    # Filter to likely-human matches
    matches = []
    for item in results:
        desc = item.get("description", "").lower()
        if any(k in desc for k in ["painter", "artist", "sculptor",
                                    "photographer", "draughtsman"]):
            qid = item["id"]
            if hint_year:
                # Naively check the description for the year
                if str(hint_year) in desc:
                    matches.insert(0, qid)  # prioritise
                    continue
            matches.append(qid)
    return matches


def fetch_wikidata_entry(qid: str) -> WikidataEntry:
    """Fetch the full Wikidata entry for a QID."""
    params = {
        "action": "wbgetentities",
        "ids": qid,
        "format": "json",
        "languages": "en",
    }
    r = requests.get(WIKIDATA_API, params=params,
                     headers={"User-Agent": USER_AGENT})
    r.raise_for_status()
    data = r.json()["entities"][qid]

    entry = WikidataEntry(qid=qid)
    entry.label = data.get("labels", {}).get("en", {}).get("value")
    entry.description = data.get("descriptions", {}).get("en", {}).get("value")

    # Parse statements
    claims = data.get("claims", {})
    for pid, statements in claims.items():
        entry.statements[pid] = []
        ref_count = 0
        for stmt in statements:
            mainsnak = stmt.get("mainsnak", {})
            datavalue = mainsnak.get("datavalue", {})
            value = datavalue.get("value")
            entry.statements[pid].append(value)
            ref_count += len(stmt.get("references", []))
        entry.refs_per_statement[pid] = ref_count

    # Find the English Wikipedia article if any
    sitelinks = data.get("sitelinks", {})
    entry.sitelinks = {k.replace("wiki", ""): v["title"] for k, v in sitelinks.items()}
    if "enwiki" in sitelinks:
        entry.wikipedia_title = sitelinks["enwiki"]["title"]

    return entry


# ---------- Wikipedia extraction ----------

def fetch_wikipedia_article(title: str, api_url: str = WIKIPEDIA_API) -> Optional[str]:
    """Fetch the raw wikitext of a Wikipedia article."""
    params = {
        "action": "query",
        "prop": "revisions",
        "rvprop": "content",
        "rvslots": "main",
        "format": "json",
        "titles": title,
    }
    r = requests.get(api_url, params=params,
                     headers={"User-Agent": USER_AGENT})
    r.raise_for_status()
    pages = r.json().get("query", {}).get("pages", {})
    for page_id, page_data in pages.items():
        revisions = page_data.get("revisions", [])
        if revisions:
            return revisions[0]["slots"]["main"]["*"]
    return None


def best_wikipedia(entry: WikidataEntry) -> tuple[Optional[str], Optional[str], str]:
    """
    Return (lang_code, article_title, wikipedia_url) for the best available
    Wikipedia article: English first, then FALLBACK_WIKIS in order.
    Returns (None, None, "") if no article is found.
    """
    if entry.wikipedia_title:
        url = f"https://en.wikipedia.org/wiki/{entry.wikipedia_title.replace(' ', '_')}"
        return "en", entry.wikipedia_title, url

    for lang, api_url in FALLBACK_WIKIS:
        title = entry.sitelinks.get(lang)
        if title:
            url = f"https://{lang}.wikipedia.org/wiki/{title.replace(' ', '_')}"
            return lang, title, url

    return None, None, ""


def parse_artist_infobox(wikitext: str) -> dict:
    """Extract structured fields from a Wikipedia artist infobox.

    Handles English (Infobox artist/person) and common non-English templates
    such as Latvian 'Mākslinieka infokaste', German 'Infobox Künstler', etc.
    Field names are normalised to English equivalents before returning.
    """
    # Latvian → English field-name map
    LV_FIELD_MAP = {
        "vārds":           "name",
        "dzimšanas_datums": "birth_date",
        "dzimšanas_vieta":  "birth_place",
        "miršanas_datums":  "death_date",
        "miršanas_vieta":   "death_place",
        "tautība":          "nationality",
        "kustība":          "movement",
        "žanrs":            "genre",
        "izglītība":        "education",
        "biedrības":        "member of",
    }
    # German → English
    DE_FIELD_MAP = {
        "geburtsdatum":    "birth_date",
        "geburtsort":      "birth_place",
        "sterbedatum":     "death_date",
        "sterbeort":       "death_place",
        "nationalität":    "nationality",
        "stilrichtung":    "movement",
        "ausbildung":      "education",
    }
    # Template names that identify an artist/person infobox
    INFOBOX_KEYWORDS = [
        "infobox",            # English, German
        "infokaste",          # Latvian
        "persondata",
        "artiste",            # French
    ]

    parsed = mwparserfromhell.parse(wikitext)
    for template in parsed.filter_templates():
        name = template.name.strip().lower()
        if any(k in name for k in INFOBOX_KEYWORDS):
            raw = {}
            for param in template.params:
                key = str(param.name).strip().lower()
                value = str(param.value).strip()
                value = re.sub(r"\[\[([^|\]]+\|)?([^\]]+)\]\]", r"\2", value)
                value = re.sub(r"<[^>]+>", "", value)
                value = re.sub(r"\{\{[^}]+\}\}", "", value)
                raw[key] = value.strip()

            # Normalise non-English keys
            fields = {}
            for k, v in raw.items():
                mapped = LV_FIELD_MAP.get(k) or DE_FIELD_MAP.get(k) or k
                fields[mapped] = v
            return fields
    return {}


# ---------- Mapping ----------

def map_infobox_to_proposals(
    infobox: dict, current: WikidataEntry, wikipedia_url: str
) -> list[ProposedEdit]:
    """Compare Wikipedia infobox to Wikidata; produce proposed additions."""
    proposed = []

    # Occupation
    field = infobox.get("field") or infobox.get("occupation")
    if field and "P106" not in current.statements:
        for keyword, qid in OCCUPATION_TO_QID.items():
            if keyword in field.lower():
                proposed.append(ProposedEdit(
                    pid="P106",
                    value=qid,
                    value_type="item",
                    source_url=wikipedia_url,
                    rationale=f"Wikipedia infobox: field='{field}'",
                ))
                break

    # Date of death
    death = infobox.get("death_date") or infobox.get("deathdate")
    if death and "P570" not in current.statements:
        date = extract_date(death)
        if date:
            proposed.append(ProposedEdit(
                pid="P570",
                value=date,
                value_type="time",
                source_url=wikipedia_url,
                rationale=f"Wikipedia infobox: death_date='{death}'",
            ))

    # Place of death
    place = infobox.get("death_place") or infobox.get("deathplace")
    if place and "P20" not in current.statements:
        proposed.append(ProposedEdit(
            pid="P20",
            value=place,  # Would need further Wikidata reconciliation
            value_type="string",
            source_url=wikipedia_url,
            rationale=f"Wikipedia infobox: death_place='{place}' (NEEDS QID LOOKUP)",
        ))

    # Education
    edu = infobox.get("education") or infobox.get("training")
    if edu and "P69" not in current.statements:
        proposed.append(ProposedEdit(
            pid="P69",
            value=edu,
            value_type="string",
            source_url=wikipedia_url,
            rationale=f"Wikipedia infobox: education='{edu}' (NEEDS QID LOOKUP)",
        ))

    # Movement
    movement = infobox.get("movement")
    if movement and "P135" not in current.statements:
        proposed.append(ProposedEdit(
            pid="P135",
            value=movement,
            value_type="string",
            source_url=wikipedia_url,
            rationale=f"Wikipedia infobox: movement='{movement}' (NEEDS QID LOOKUP)",
        ))

    return proposed


def extract_date(text: str) -> Optional[str]:
    """Best-effort extraction of a date in QuickStatements format."""
    # ISO-like: YYYY-MM-DD
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})", text)
    if m:
        return f"+{m.group(0)}T00:00:00Z/11"

    # Year only
    m = re.search(r"\b(1[89]\d{2}|20\d{2})\b", text)
    if m:
        return f"+{m.group(0)}-00-00T00:00:00Z/9"

    return None


# ---------- Output ----------

def print_audit(entry: WikidataEntry):
    print(f"\n{'='*60}")
    print(f"WIKIDATA AUDIT — {entry.qid}")
    print(f"{'='*60}\n")
    print(f"Label:       {entry.label}")
    print(f"Description: {entry.description}")
    if entry.wikipedia_title:
        print(f"Wikipedia:   {entry.wikipedia_title} (en)")
    wiki_langs = [k for k in entry.sitelinks if k != "en"]
    if wiki_langs:
        print(f"Other wikis: {', '.join(wiki_langs)}")
    print()

    print(f"{'-'*60}")
    print(f"STATEMENTS — present, with reference counts")
    print(f"{'-'*60}")
    for pid, label in KEY_PROPERTIES.items():
        if pid in entry.statements:
            ref_count = entry.refs_per_statement.get(pid, 0)
            ref_indicator = "✓" if ref_count > 0 else "✗ no refs"
            print(f"  {pid:6} {label:30} {ref_indicator}")

    print(f"\n{'-'*60}")
    print(f"STATEMENTS — missing")
    print(f"{'-'*60}")
    for pid, label in KEY_PROPERTIES.items():
        if pid not in entry.statements:
            print(f"  {pid:6} {label}")
    print()


def write_quickstatements(qid: str, proposals: list[ProposedEdit],
                          out_path: str):
    """Write a QuickStatements-format file ready to submit."""
    lines = []
    for prop in proposals:
        # QuickStatements format: QID|PID|VALUE|S854|"sourceURL"
        if prop.value_type == "item" and prop.value.startswith("Q"):
            value = prop.value
        elif prop.value_type == "time":
            value = prop.value
        else:
            value = f'"{prop.value}"'
        line = f'{qid}|{prop.pid}|{value}|S854|"{prop.source_url}"'
        lines.append(line)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
        f.write("\n")

    print(f"\n✓ QuickStatements file written: {out_path}")
    print(f"  {len(proposals)} proposed edits.")
    print(f"  Review the file, then submit at:")
    print(f"  https://quickstatements.toolforge.org/")


# ---------- Canonical JSON loader ----------

REPO_ROOT   = Path(__file__).resolve().parent.parent
DATA_DIR    = REPO_ROOT / "artbase_export" / "data"
ARTBASE_URL = "https://artbase.eu/artists"  # placeholder source URL


def load_canonical_artist(artist_id: str) -> dict:
    """Load data/artists/{artist_id}.json; raise SystemExit if not found."""
    path = DATA_DIR / "artists" / f"{artist_id}.json"
    if not path.exists():
        # Try a case-insensitive glob
        matches = list((DATA_DIR / "artists").glob(f"*{artist_id}*.json"))
        if not matches:
            sys.exit(f"✗ Canonical JSON not found for '{artist_id}'\n"
                     f"  Looked in: {DATA_DIR / 'artists'}")
        path = matches[0]
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def canonical_to_authority_proposals(
    canonical: dict, entry: WikidataEntry
) -> list[ProposedEdit]:
    """
    Compare authority_links in the canonical JSON against what Wikidata already
    has and return proposed additions for any confirmed IDs that are missing.
    """
    links = canonical.get("authority_links", {})
    name  = canonical.get("identity", {}).get("preferred_name", "")
    source_url = (
        f"{ARTBASE_URL}/{canonical.get('artbase_id', 'unknown')}"
    )

    # Mapping: canonical key → (Wikidata PID, human label)
    AUTHORITY_MAP = {
        "ulan":    ("P245", "Getty ULAN ID"),
        "viaf":    ("P214", "VIAF ID"),
        "isni":    ("P213", "ISNI"),
        "rkd":     ("P650", "RKDartists ID"),
        "lc_naco": ("P244", "Library of Congress authority ID"),
        "gnd":     ("P227", "GND ID"),
        "bnf":     ("P268", "Bibliothèque nationale de France ID"),
    }

    proposals = []
    for key, (pid, label) in AUTHORITY_MAP.items():
        rec = links.get(key, {})
        authority_id = rec.get("id")
        status       = rec.get("status", "")
        if not authority_id:
            continue
        if status not in ("confirmed", "working"):
            continue
        if pid in entry.statements:
            continue  # Already on Wikidata
        proposals.append(ProposedEdit(
            pid=pid,
            value=authority_id,
            value_type="string",
            source_url=source_url,
            rationale=f"ArtBase canonical record for {name} — status: {status}",
        ))

    return proposals


# ---------- Main ----------

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("name", nargs="?", help="Artist name to look up")
    parser.add_argument("--year", type=int, help="Optional birth year hint")
    parser.add_argument("--qid", help="Skip search, use this QID directly")
    parser.add_argument(
        "--from-canonical",
        metavar="ARTIST_ID",
        help=(
            "Read data/artists/{ARTIST_ID}.json, use its Wikidata QID directly, "
            "and treat confirmed authority IDs (ULAN, VIAF, etc.) as proposed edits. "
            "Skips the Wikidata name-search step."
        ),
    )
    parser.add_argument("--no-quickstatements", action="store_true",
                        help="Skip generating QuickStatements file")
    args = parser.parse_args()

    canonical: Optional[dict] = None

    # ── Resolve QID ───────────────────────────────────────────────────────────
    if args.from_canonical:
        canonical = load_canonical_artist(args.from_canonical)
        wd = canonical.get("authority_links", {}).get("wikidata", {})
        qid = wd.get("id")
        if not qid:
            sys.exit(
                f"✗ No Wikidata QID in canonical record '{args.from_canonical}'.\n"
                f"  Run the pipeline without --from-canonical to search and assign one."
            )
        # Use preferred name for output files
        preferred_name = canonical.get("identity", {}).get("preferred_name") or args.from_canonical
        print(f"Reading canonical record: {args.from_canonical}")
        print(f"  Artist:  {preferred_name}")
        print(f"  QID:     {qid}  (status: {wd.get('status', '?')})")
        # Report known authority IDs
        auth_links = canonical.get("authority_links", {})
        for key in ("ulan", "viaf", "isni", "rkd", "lc_naco", "gnd", "bnf"):
            rec = auth_links.get(key, {})
            if rec.get("id"):
                print(f"  {key.upper():8} {rec['id']}  ({rec.get('status', '?')})")
    elif args.qid:
        qid = args.qid
        preferred_name = args.name or qid
        print(f"Using QID: {qid}")
    elif args.name:
        preferred_name = args.name
        print(f"Searching Wikidata for: {args.name}")
        candidates = search_wikidata(args.name, hint_year=args.year)
        if not candidates:
            print(f"✗ No artist found matching '{args.name}'.")
            print(f"  → Consider creating a new Wikidata entry.")
            return 1
        qid = candidates[0]
        print(f"✓ Best match: {qid}")
        if len(candidates) > 1:
            print(f"  Other candidates: {', '.join(candidates[1:5])}")
    else:
        parser.print_help()
        return 1

    # ── Fetch and audit ───────────────────────────────────────────────────────
    entry = fetch_wikidata_entry(qid)
    print_audit(entry)

    all_proposals: list[ProposedEdit] = []

    # ── Authority ID proposals from canonical record ───────────────────────────
    if canonical:
        auth_proposals = canonical_to_authority_proposals(canonical, entry)
        if auth_proposals:
            print(f"{'-'*60}")
            print(f"AUTHORITY IDs FROM CANONICAL RECORD ({len(auth_proposals)})")
            print(f"{'-'*60}")
            for p in auth_proposals:
                print(f"  + {p.pid:6} ({KEY_PROPERTIES.get(p.pid, p.pid)}) = {p.value}")
                print(f"    {p.rationale}")
        all_proposals.extend(auth_proposals)

    # ── Wikipedia proposals ───────────────────────────────────────────────────
    lang, wiki_title, wp_url = best_wikipedia(entry)
    if wiki_title and not args.no_quickstatements:
        wiki_api = WIKIPEDIA_API if lang == "en" else \
            dict(FALLBACK_WIKIS).get(lang, WIKIPEDIA_API)
        print(f"{'-'*60}")
        print(f"FETCHING WIKIPEDIA [{lang}]: {wiki_title}")
        print(f"{'-'*60}")
        wikitext = fetch_wikipedia_article(wiki_title, api_url=wiki_api)
        if wikitext:
            infobox = parse_artist_infobox(wikitext)
            print(f"  Found infobox with {len(infobox)} fields")
            wiki_proposals = map_infobox_to_proposals(infobox, entry, wp_url)

            if wiki_proposals:
                print(f"\n{'-'*60}")
                print(f"PROPOSED EDITS FROM WIKIPEDIA ({len(wiki_proposals)})")
                print(f"{'-'*60}")
                for p in wiki_proposals:
                    print(f"  + {p.pid} ({KEY_PROPERTIES.get(p.pid, '?')}) = {p.value}")
                    print(f"    rationale: {p.rationale}")
            all_proposals.extend(wiki_proposals)
        else:
            print("  Could not fetch Wikipedia article")
    elif not wiki_title:
        print("  No Wikipedia article found (checked: en, lv, de, fr, nl, sv).")
        print("  → Check other language Wikipedias manually for source data.")

    # ── Write QuickStatements ─────────────────────────────────────────────────
    if all_proposals and not args.no_quickstatements:
        safe_name = re.sub(r"[^\w]", "_", preferred_name)
        out_path = f"{safe_name}.qs.txt"
        write_quickstatements(qid, all_proposals, out_path)
    elif not all_proposals:
        print("\n  No proposals generated — Wikidata entry appears complete.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
