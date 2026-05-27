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
import sys
from dataclasses import dataclass, field
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
    wikipedia_title: Optional[str] = None


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
    if "enwiki" in sitelinks:
        entry.wikipedia_title = sitelinks["enwiki"]["title"]

    return entry


# ---------- Wikipedia extraction ----------

def fetch_wikipedia_article(title: str) -> Optional[str]:
    """Fetch the raw wikitext of a Wikipedia article."""
    params = {
        "action": "query",
        "prop": "revisions",
        "rvprop": "content",
        "rvslots": "main",
        "format": "json",
        "titles": title,
    }
    r = requests.get(WIKIPEDIA_API, params=params,
                     headers={"User-Agent": USER_AGENT})
    r.raise_for_status()
    pages = r.json().get("query", {}).get("pages", {})
    for page_id, page_data in pages.items():
        revisions = page_data.get("revisions", [])
        if revisions:
            return revisions[0]["slots"]["main"]["*"]
    return None


def parse_artist_infobox(wikitext: str) -> dict:
    """Extract structured fields from a Wikipedia artist infobox."""
    parsed = mwparserfromhell.parse(wikitext)
    for template in parsed.filter_templates():
        name = template.name.strip().lower()
        if "infobox" in name and ("artist" in name or "person" in name):
            fields = {}
            for param in template.params:
                key = str(param.name).strip().lower()
                # Strip wikitext markup from values, basic clean
                value = str(param.value).strip()
                value = re.sub(r"\[\[([^|\]]+\|)?([^\]]+)\]\]", r"\2", value)
                value = re.sub(r"<[^>]+>", "", value)
                value = re.sub(r"\{\{[^}]+\}\}", "", value)
                fields[key] = value.strip()
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
        print(f"Wikipedia:   {entry.wikipedia_title}")
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


# ---------- Main ----------

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("name", help="Artist name to look up")
    parser.add_argument("--year", type=int, help="Optional birth year hint")
    parser.add_argument("--qid", help="Skip search, use this QID directly")
    parser.add_argument("--no-quickstatements", action="store_true",
                        help="Skip generating QuickStatements file")
    args = parser.parse_args()

    # Step 1: Find the Wikidata entry
    if args.qid:
        qid = args.qid
        print(f"Using QID: {qid}")
    else:
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

    # Step 2: Fetch and audit
    entry = fetch_wikidata_entry(qid)
    print_audit(entry)

    # Step 3: If there's a Wikipedia article, extract proposals
    if entry.wikipedia_title and not args.no_quickstatements:
        print(f"{'-'*60}")
        print(f"FETCHING WIKIPEDIA: {entry.wikipedia_title}")
        print(f"{'-'*60}")
        wikitext = fetch_wikipedia_article(entry.wikipedia_title)
        if wikitext:
            infobox = parse_artist_infobox(wikitext)
            print(f"  Found infobox with {len(infobox)} fields")
            wp_url = f"https://en.wikipedia.org/wiki/{entry.wikipedia_title.replace(' ', '_')}"
            proposals = map_infobox_to_proposals(infobox, entry, wp_url)

            if proposals:
                print(f"\n{'-'*60}")
                print(f"PROPOSED EDITS ({len(proposals)})")
                print(f"{'-'*60}")
                for p in proposals:
                    print(f"  + {p.pid} ({KEY_PROPERTIES.get(p.pid, '?')}) = {p.value}")
                    print(f"    rationale: {p.rationale}")

                # Write QuickStatements file
                safe_name = re.sub(r"[^\w]", "_", args.name)
                out_path = f"{safe_name}.qs.txt"
                write_quickstatements(qid, proposals, out_path)
            else:
                print("  No new proposals (entry already covers infobox fields)")
        else:
            print("  Could not fetch Wikipedia article")
    elif not entry.wikipedia_title:
        print("  No English Wikipedia article exists for this entry.")
        print("  → Check other language Wikipedias manually for source data.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
