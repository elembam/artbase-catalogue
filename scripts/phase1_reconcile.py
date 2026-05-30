#!/usr/bin/env python3
"""
Phase 1: Wikidata artist reconciliation — batch SPARQL lookup.

Reads artists from Airtable (no QID, has Birth Year), queries Wikidata,
and writes confirmed Q-numbers back.

Usage:
    python phase1_reconcile.py              # dry-run, 10 artists
    python phase1_reconcile.py --execute    # write to Airtable, 10 artists
    python phase1_reconcile.py --limit 25 --execute
"""

import sys
import time
import argparse
from pathlib import Path

import requests
from rich.console import Console
from rich.table import Table

# Allow running from project root or scripts/
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "artbase_export" / "src"))

import yaml
from pyairtable import Api
from artbase_export.airtable.schema import Tables, ArtistFields, WikidataStatus

SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"
USER_AGENT      = "ArsAccordia/1.0 (arsaccordia.com; contact@arsaccordia.com)"

# Wikidata guidance: one SPARQL request per 5 seconds for unauthenticated clients
SPARQL_DELAY    = 5   # seconds between queries
MAX_RETRIES     = 3   # retry on 429 / 502 / timeout

console = Console()


# ── Wikidata lookup ────────────────────────────────────────────────────────────

def sparql_lookup(name: str, birth_year: int) -> list[dict]:
    """
    Query Wikidata for a human (Q5) matching birth_year and whose label
    contains the artist's surname. Returns up to 5 candidates.

    Strategy: use the last word of the name as the surname filter. This
    handles 'Nikolajs Bogdanovs-Beļskis' → filter on 'bogdanovs' while still
    picking up Wikidata items with transliterated labels.

    Retries up to MAX_RETRIES times on 429 / 502 / timeout with exponential
    back-off, honouring the Retry-After header when present.
    """
    surname = name.strip().split()[-1].lower().replace('"', '')

    query = f"""
    SELECT DISTINCT ?item ?itemLabel ?birthYear ?deathYear ?itemDescription WHERE {{
      ?item wdt:P31 wd:Q5 ;
            wdt:P569 ?birth .
      BIND(YEAR(?birth) AS ?birthYear)
      OPTIONAL {{ ?item wdt:P570 ?death . BIND(YEAR(?death) AS ?deathYear) }}
      FILTER(?birthYear = {birth_year})
      SERVICE wikibase:label {{
        bd:serviceParam wikibase:language "en,lv,de,ru,fr" .
      }}
      FILTER(CONTAINS(LCASE(?itemLabel), "{surname}"))
    }}
    LIMIT 5
    """

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.get(
                SPARQL_ENDPOINT,
                params={"query": query, "format": "json"},
                headers={"User-Agent": USER_AGENT},
                timeout=45,
            )
            if resp.status_code == 429:
                wait = int(resp.headers.get("Retry-After", 15 * attempt))
                console.print(f"  [yellow]429 rate-limited — waiting {wait}s (attempt {attempt})[/]")
                time.sleep(wait)
                continue
            if resp.status_code in (502, 503):
                wait = 10 * attempt
                console.print(f"  [yellow]{resp.status_code} error — waiting {wait}s (attempt {attempt})[/]")
                time.sleep(wait)
                continue
            resp.raise_for_status()
            bindings = resp.json()["results"]["bindings"]
            return [
                {
                    "q":     b["item"]["value"].split("/")[-1],
                    "label": b.get("itemLabel", {}).get("value", ""),
                    "birth": int(b["birthYear"]["value"]) if "birthYear" in b else None,
                    "death": int(b["deathYear"]["value"]) if "deathYear" in b else None,
                    "desc":  b.get("itemDescription", {}).get("value", ""),
                }
                for b in bindings
            ]
        except requests.exceptions.Timeout:
            wait = 10 * attempt
            console.print(f"  [yellow]Timeout — waiting {wait}s (attempt {attempt})[/]")
            time.sleep(wait)

    raise RuntimeError(f"Wikidata SPARQL failed after {MAX_RETRIES} attempts")


def wikidata_url(qid: str) -> str:
    return f"https://www.wikidata.org/wiki/{qid}"


# ── Confidence scoring ─────────────────────────────────────────────────────────

def score_match(artist_name: str, birth_year: int, candidate: dict) -> str:
    """
    Return confidence level for a SPARQL candidate.

    HIGH    — birth year matches + candidate label contains artist's surname
    MEDIUM  — birth year matches but label doesn't contain surname
              (e.g. transliteration difference)
    LOW     — birth year doesn't match exactly (shouldn't happen with our query,
              but guard anyway)
    """
    surname = artist_name.strip().split()[-1].lower()
    label_lc = candidate["label"].lower()

    birth_ok  = candidate["birth"] == birth_year
    name_ok   = surname in label_lc

    if birth_ok and name_ok:
        return "HIGH"
    if birth_ok:
        return "MEDIUM"
    return "LOW"


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true",
                        help="Write HIGH-confidence Q-numbers to Airtable (default: dry-run)")
    parser.add_argument("--limit", type=int, default=10,
                        help="Number of artists to process (default: 10)")
    parser.add_argument("--config", default="config.yaml",
                        help="Path to config.yaml")
    args = parser.parse_args()

    cfg_path = Path(__file__).parent.parent / "artbase_export" / args.config
    if not cfg_path.exists():
        cfg_path = Path(args.config)
    cfg = yaml.safe_load(cfg_path.read_text())

    api     = Api(cfg["airtable"]["token"])
    base_id = cfg["airtable"]["base_id"]
    artists = api.table(base_id, Tables.ARTISTS)

    # Fetch eligible artists: have birth year, no QID yet
    recs = artists.all(
        formula='AND({Wikidata QID} = "", {Birth Year} != "")',
        fields=[
            ArtistFields.DISPLAY_NAME,
            ArtistFields.BIRTH_YEAR,
            ArtistFields.DEATH_YEAR,
            ArtistFields.WIKIDATA_QID,
        ],
    )
    recs = recs[: args.limit]

    mode = "[green]EXECUTE[/]" if args.execute else "[yellow]DRY-RUN[/]"
    console.print(f"\n[bold]Phase 1 reconciliation[/] — {mode} — {len(recs)} artists\n")

    results_table = Table(show_lines=True)
    results_table.add_column("Artist",      style="cyan",   min_width=28)
    results_table.add_column("Born",        style="dim",    width=6)
    results_table.add_column("QID",         style="green",  width=12)
    results_table.add_column("WD Label",    min_width=24)
    results_table.add_column("Confidence",  width=10)
    results_table.add_column("WD Desc",     min_width=24, overflow="fold")

    written = 0
    no_match = []

    for rec in recs:
        f          = rec["fields"]
        name       = f.get(ArtistFields.DISPLAY_NAME, "")
        birth_str  = f.get(ArtistFields.BIRTH_YEAR, "")

        try:
            birth_year = int(birth_str)
        except (ValueError, TypeError):
            results_table.add_row(name, birth_str, "—", "Birth year unparseable", "SKIP", "")
            continue

        # Respect Wikidata's guideline: one SPARQL request per 5 seconds
        time.sleep(SPARQL_DELAY)
        try:
            candidates = sparql_lookup(name, birth_year)
        except Exception as e:
            results_table.add_row(name, str(birth_year), "ERROR", str(e), "ERROR", "")
            continue

        if not candidates:
            results_table.add_row(name, str(birth_year), "—", "No match found", "NONE", "")
            no_match.append(name)
            continue

        # Take the best candidate (first result, already birth-year filtered)
        best       = candidates[0]
        confidence = score_match(name, birth_year, best)

        results_table.add_row(
            name,
            str(birth_year),
            best["q"],
            best["label"],
            f"[green]{confidence}[/]" if confidence == "HIGH" else
            f"[yellow]{confidence}[/]" if confidence == "MEDIUM" else
            f"[red]{confidence}[/]",
            best["desc"][:60],
        )

        if len(candidates) > 1:
            console.print(
                f"  [dim]  {name}: {len(candidates)} candidates "
                f"({', '.join(c['q'] for c in candidates)})[/]"
            )

        # Write HIGH confidence matches back to Airtable
        if confidence == "HIGH" and args.execute:
            artists.update(rec["id"], {
                ArtistFields.WIKIDATA_QID:    best["q"],
                ArtistFields.WIKIDATA_URL:    wikidata_url(best["q"]),
                ArtistFields.WIKIDATA_STATUS: WikidataStatus.MATCHED,
            })
            written += 1

    console.print(results_table)

    # Summary
    console.print(f"\n[bold]Summary[/]")
    console.print(f"  Processed:       {len(recs)}")
    console.print(f"  Written to AT:   {written}" if args.execute else
                  f"  Would write:     [dim](dry-run — add --execute)[/]")
    if no_match:
        console.print(f"  No match found:  {len(no_match)}")
        for n in no_match:
            console.print(f"    [dim]· {n}[/]")

    if not args.execute:
        console.print(
            "\n[yellow]Dry-run complete. Add --execute to write Q-numbers to Airtable.[/]"
        )


if __name__ == "__main__":
    main()
