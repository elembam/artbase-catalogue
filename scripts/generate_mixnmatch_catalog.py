#!/usr/bin/env python3
"""
Generate a Mix'n'match catalog TSV from artist JSON files.

Output: artbase_export/data/mixnmatch_artists.tsv
Submit this file when requesting catalog import at:
  https://mix-n-match.toolforge.org/#/import
"""

import json
import csv
from pathlib import Path

REPO_ROOT    = Path(__file__).resolve().parent.parent
ARTISTS_DIR  = REPO_ROOT / "artbase_export" / "data" / "artists"
ARTISTS_HTML = REPO_ROOT / "artists"
OUT_FILE     = REPO_ROOT / "artbase_export" / "data" / "mixnmatch_artists.tsv"
BASE_URL     = "https://arsaccordia.com/artists"


def describe(artist: dict) -> str:
    desc_parts = []
    nat  = (artist.get("descriptors") or {}).get("nationality")
    occs = (artist.get("descriptors") or {}).get("occupations") or []
    birth = ((artist.get("life") or {}).get("birth_date") or {}).get("value")
    death = ((artist.get("life") or {}).get("death_date") or {}).get("value")

    if nat:
        desc_parts.append(nat)
    if occs:
        desc_parts.append(", ".join(occs))
    if birth or death:
        dates = "–".join(filter(None, [birth, death]))
        desc_parts.append(dates)

    return "; ".join(desc_parts) if desc_parts else "artist"


rows = []
skipped = []

for path in sorted(ARTISTS_DIR.glob("*.json")):
    try:
        artist = json.loads(path.read_text())
    except Exception:
        continue

    artbase_id = artist.get("artbase_id", "")
    if not artbase_id:
        continue

    # Include if a live HTML page exists (visibility flag reflects Airtable export
    # layer, not actual web publication status)
    if not (ARTISTS_HTML / f"{artbase_id}.html").exists():
        skipped.append(artbase_id)
        continue

    name = (artist.get("identity") or {}).get("preferred_name", "")
    if not name:
        skipped.append(artbase_id)
        continue

    url = f"{BASE_URL}/{artbase_id}.html"
    desc = describe(artist)

    # Note pre-confirmed QID so Mix'n'match can auto-match these rows
    wikidata_id = ((artist.get("authority_links") or {}).get("wikidata") or {}).get("id")
    wikidata_status = ((artist.get("authority_links") or {}).get("wikidata") or {}).get("status", "")

    rows.append({
        "id":          artbase_id,
        "name":        name,
        "description": desc,
        "url":         url,
        "type":        "Q5",  # human
        "wikidata_id": wikidata_id or "",
        "wd_status":   wikidata_status,
    })

# Write TSV — Mix'n'match core columns only (id, name, description, url, type)
with OUT_FILE.open("w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f, delimiter="\t")
    writer.writerow(["id", "name", "description", "url", "type"])
    for r in rows:
        writer.writerow([r["id"], r["name"], r["description"], r["url"], r["type"]])

# Print summary
confirmed = [r for r in rows if r["wd_status"] == "confirmed"]
unmatched = [r for r in rows if not r["wikidata_id"]]
candidate = [r for r in rows if r["wd_status"] == "candidate_verify"]

print(f"Catalog rows written : {len(rows)}")
print(f"  Already confirmed  : {len(confirmed)}  (Mix'n'match can auto-match these)")
print(f"  Candidate / pending: {len(candidate)}")
print(f"  No QID yet         : {len(unmatched)}")
print(f"Skipped (not public) : {len(skipped)}")
print(f"\nOutput: {OUT_FILE}")
print()
print("Pre-confirmed artists (you can supply QIDs to Mix'n'match upfront):")
for r in confirmed[:20]:
    print(f"  {r['id']:30}  {r['wikidata_id']:12}  {r['name']}")
if len(confirmed) > 20:
    print(f"  ... and {len(confirmed) - 20} more")
