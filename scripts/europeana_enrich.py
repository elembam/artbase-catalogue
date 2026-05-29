#!/usr/bin/env python3
"""
europeana_enrich.py — Enrich artist records with museum holding references from Europeana.

For each artist with a confirmed Wikidata QID, searches the Europeana API
and writes confirmed institution references back to the canonical JSON under
artist["museum_holdings"]. Holdings are citations (name + URL), never copied content.

Requires a free Europeana API key:
    export EUROPEANA_API_KEY=your_key_here
    (or pass via --api-key)
    Get one at: https://apis.europeana.eu/en/account/register

CLI:
    python3 scripts/europeana_enrich.py --artist ART-SVEMPS-1897 --dry-run
    python3 scripts/europeana_enrich.py --all --dry-run
    python3 scripts/europeana_enrich.py --all
    python3 scripts/europeana_enrich.py --all --limit 50
    python3 scripts/europeana_enrich.py --all --force  # re-fetch already-enriched
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

# ── Config ─────────────────────────────────────────────────────────────────────
REPO_ROOT    = Path(__file__).resolve().parent.parent
DATA_DIR     = REPO_ROOT / "artbase_export" / "data" / "artists"
REPORTS_DIR  = REPO_ROOT / "reports"

EUROPEANA_SEARCH = "https://api.europeana.eu/record/v2/search.json"
USER_AGENT       = "Ars Accordia/1.0 (https://github.com/elembam/artbase-catalogue)"
RATE_SLEEP       = 0.5   # Europeana allows higher rate than Wikidata
MAX_ROWS         = 20    # results to fetch per artist


# ── API access ─────────────────────────────────────────────────────────────────

def europeana_search(query: str, api_key: str, rows: int = MAX_ROWS) -> list[dict]:
    """
    Search Europeana. Returns list of item dicts with title, dataProvider,
    edmIsShownAt (institution URL), and edmPreview (thumbnail).
    """
    params = {
        "wskey":   api_key,
        "query":   query,
        "rows":    rows,
        "profile": "rich",
        "qf":      "TYPE:IMAGE",   # artworks are typically images in Europeana
    }
    url = EUROPEANA_SEARCH + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            data = json.loads(r.read())
            return data.get("items", [])
    except urllib.error.HTTPError as e:
        if e.code in (400, 401):
            print("  ✗ Europeana API key invalid or missing. Get one at https://apis.europeana.eu")
            sys.exit(1)
        print(f"  ✗ Europeana HTTP {e.code}")
        return []
    except Exception as e:
        print(f"  ✗ Europeana error: {e}")
        return []


def extract_holdings(items: list[dict], artist_name: str) -> list[dict]:
    """
    From raw Europeana results, extract unique institution references.
    Returns list of {institution, record_url, title, europeana_id}.
    Deduplicates by institution name.
    """
    seen_institutions: set[str] = set()
    holdings = []

    for item in items:
        # dataProvider is the contributing institution
        providers = item.get("dataProvider") or item.get("edmDatasetName") or []
        if isinstance(providers, str):
            providers = [providers]

        institution = providers[0].strip() if providers else None
        if not institution or institution in seen_institutions:
            continue

        # edmIsShownAt is the record URL at the institution's own system
        shown_at = item.get("edmIsShownAt") or []
        if isinstance(shown_at, list):
            shown_at = shown_at[0] if shown_at else None

        # Europeana record URL
        europeana_id = item.get("id", "")
        europeana_url = f"https://europeana.eu/item{europeana_id}" if europeana_id else None

        titles = item.get("title") or item.get("dcTitle") or []
        title = titles[0] if isinstance(titles, list) and titles else str(titles) if titles else None

        seen_institutions.add(institution)
        holdings.append({
            "institution":    institution,
            "europeana_url":  europeana_url,
            "institution_url": shown_at,
            "title_example":  title,
            "source":         "europeana_auto",
        })

        if len(holdings) >= 5:  # cap at 5 institutions per artist
            break

    return holdings


# ── Per-artist enrichment ──────────────────────────────────────────────────────

def enrich_artist(path: Path, api_key: str, dry_run: bool, force: bool) -> dict:
    """
    Enrich a single artist file. Returns a report dict.
    """
    data = json.loads(path.read_text(encoding="utf-8"))
    artbase_id   = data.get("artbase_id") or path.stem
    artist_name  = data.get("identity", {}).get("preferred_name", "")

    # Skip if already enriched and not forcing
    existing_holdings = data.get("museum_holdings")
    if existing_holdings and not force:
        return {"id": artbase_id, "status": "skipped", "reason": "already_enriched"}

    # Must have a confirmed Wikidata QID to search reliably by identity
    wd = data.get("authority_links", {}).get("wikidata", {})
    if not wd.get("id") or wd.get("status") not in ("confirmed",):
        return {"id": artbase_id, "status": "skipped", "reason": "no_confirmed_wikidata"}

    if not artist_name:
        return {"id": artbase_id, "status": "skipped", "reason": "no_name"}

    # Build search query — use name + "painter" to reduce false positives
    nationality = data.get("descriptors", {}).get("nationality", "")
    query = f'"{artist_name}"'
    if nationality:
        query += f' AND {nationality}'

    items = europeana_search(query, api_key)
    time.sleep(RATE_SLEEP)

    if not items:
        # Try without nationality filter
        items = europeana_search(f'"{artist_name}"', api_key)
        time.sleep(RATE_SLEEP)

    if not items:
        return {"id": artbase_id, "status": "no_results", "name": artist_name}

    holdings = extract_holdings(items, artist_name)

    if not holdings:
        return {"id": artbase_id, "status": "no_holdings", "name": artist_name, "results": len(items)}

    if not dry_run:
        data["museum_holdings"] = holdings
        data.setdefault("_meta", {})["europeana_last_enriched"] = datetime.now(timezone.utc).isoformat()
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "id":       artbase_id,
        "status":   "enriched",
        "name":     artist_name,
        "holdings": [h["institution"] for h in holdings],
        "dry_run":  dry_run,
    }


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Europeana museum holdings enrichment for Ars Accordia artists"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--artist", metavar="ART-ID", help="Enrich a single artist")
    group.add_argument("--all",    action="store_true", help="Enrich all artists")

    parser.add_argument("--api-key", default=os.getenv("EUROPEANA_API_KEY", ""),
                        help="Europeana API key (or set EUROPEANA_API_KEY env var)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would change without writing")
    parser.add_argument("--force",   action="store_true",
                        help="Re-fetch even if already enriched")
    parser.add_argument("--limit",   type=int, default=0,
                        help="Process at most N artists (0 = all)")
    args = parser.parse_args()

    if not args.api_key:
        print("✗ No Europeana API key. Set EUROPEANA_API_KEY or pass --api-key.")
        print("  Get a free key at: https://apis.europeana.eu/en/account/register")
        sys.exit(1)

    if args.artist:
        paths = list(DATA_DIR.glob(f"{args.artist}.json"))
        if not paths:
            print(f"✗ Artist file not found: {args.artist}")
            sys.exit(1)
    else:
        paths = sorted(DATA_DIR.glob("ART-*.json"))
        if args.limit:
            paths = paths[:args.limit]

    label = "[DRY RUN] " if args.dry_run else ""
    print(f"Scanning {len(paths)} artist(s)  {label}...")

    stats   = {"enriched": 0, "skipped": 0, "no_results": 0, "errors": 0}
    reports = []
    start   = datetime.now()

    for path in paths:
        try:
            result = enrich_artist(path, args.api_key, args.dry_run, args.force)
            reports.append(result)
            status = result["status"]

            if status == "enriched":
                stats["enriched"] += 1
                institutions = ", ".join(result.get("holdings", []))
                marker = "~" if args.dry_run else "✓"
                print(f"  {marker} {result['id']}: {result['name']} → {institutions}")
            elif status == "skipped":
                stats["skipped"] += 1
            else:
                stats["no_results"] += 1
                print(f"  - {result['id']}: {result.get('name', '')} — {status}")

        except Exception as e:
            stats["errors"] += 1
            reports.append({"id": path.stem, "status": "error", "error": str(e)})
            print(f"  ✗ {path.stem}: {e}")

    elapsed = datetime.now() - start
    mins    = int(elapsed.total_seconds() // 60)
    secs    = int(elapsed.total_seconds() % 60)
    dry_tag = " (DRY RUN)" if args.dry_run else ""
    print(f"\nEnriched {stats['enriched']} artists, "
          f"{stats['skipped']} skipped, "
          f"{stats['no_results']} no results, "
          f"{stats['errors']} errors "
          f"in {mins}m{secs}s{dry_tag}")

    # Write report
    REPORTS_DIR.mkdir(exist_ok=True)
    report_path = REPORTS_DIR / f"europeana_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    report_path.write_text(json.dumps(reports, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Report: {report_path}")


if __name__ == "__main__":
    main()
