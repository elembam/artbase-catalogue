#!/usr/bin/env python3
"""
ingest_gallery_origin.py — Attach data_origin attestations from Galerija Jēkabs.

Fetches the paintings.lv artist index, parses each entry, matches against
existing Ars Accordia artist records (by normalised surname + birth year),
and writes idempotent data_origin attestations to the canonical JSONs.

The gallery is an ORIGIN source, not an authority:
  - wikidata_citable: false
  - can_confirm: false
  - authoritative: false
  Conflicts with existing authoritative dates are surfaced in _meta.discrepancies[],
  never overwrite authoritative values.

CLI:
    python3 scripts/ingest_gallery_origin.py               # match + write
    python3 scripts/ingest_gallery_origin.py --dry-run     # report only, no writes
    python3 scripts/ingest_gallery_origin.py --artist ART-AIDE-1913
    python3 scripts/ingest_gallery_origin.py --report      # write reports only
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
import urllib.error
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Optional
from html.parser import HTMLParser

# ── Paths ──────────────────────────────────────────────────────────────────────
REPO_ROOT   = Path(__file__).resolve().parent.parent
DATA_DIR    = REPO_ROOT / "artbase_export" / "data"
ARTISTS_DIR = DATA_DIR / "artists"
REPORTS_DIR = REPO_ROOT / "reports"

SOURCE_ID        = "SRC-GALERIJA-JEKABS"
GALLERY_BASE_URL = "https://paintings.lv"
ARTIST_LIST_URL  = "https://paintings.lv/artists/list"
USER_AGENT       = "Ars Accordia/1.0 (https://arsaccordia.com; catalogue@arsaccordia.com)"
RATE_SLEEP       = 2.0


# ── HTML parser ─────────────────────────────────────────────────────────────────

class ArtistListParser(HTMLParser):
    """
    Parse the paintings.lv/artists/list page.

    Structure (for each artist):
      <a href="/artists/view/{id}">
        <h3 class="mb-8">SURNAME Firstname</h3>
        <p class="font-16">(YYYY - YYYY)</p>   ← death year may be absent
      </a>
    """

    def __init__(self):
        super().__init__()
        self.artists: list[dict] = []
        self._in_artist_link = False
        self._current_href   = None
        self._in_h3          = False
        self._in_dates_p     = False
        self._current_name   = None
        self._next_p_is_dates = False

    def handle_starttag(self, tag, attrs):
        attrs_d = dict(attrs)

        if tag == "a":
            href = attrs_d.get("href", "")
            if re.match(r"^/artists/view/\d+$", href):
                self._in_artist_link = True
                self._current_href   = GALLERY_BASE_URL + href
                self._current_name   = None

        if self._in_artist_link and tag == "h3":
            classes = attrs_d.get("class", "")
            if "mb-8" in classes:
                self._in_h3 = True

        if self._in_artist_link and tag == "p":
            classes = attrs_d.get("class", "")
            if "font-16" in classes:
                self._in_dates_p = True

    def handle_endtag(self, tag):
        if tag == "h3":
            self._in_h3 = False
        if tag == "p":
            self._in_dates_p = False
        if tag == "a" and self._in_artist_link:
            self._in_artist_link = False
            self._current_href   = None

    def handle_data(self, data):
        if self._in_h3:
            self._current_name = data.strip()

        if self._in_dates_p and self._current_href:
            text = data.strip()
            # Match "(YYYY - YYYY)" or "(YYYY)" or "(YYYY - )"
            m = re.match(r"\((\d{4})(?:\s*[-–]\s*(\d{4}))?\)", text)
            if m and self._current_name:
                birth = int(m.group(1))
                death = int(m.group(2)) if m.group(2) else None
                self.artists.append({
                    "raw_name":   self._current_name,
                    "birth_year": birth,
                    "death_year": death,
                    "gallery_url": self._current_href,
                })
                self._current_name = None


# ── Normalisation ──────────────────────────────────────────────────────────────

def normalise(text: str) -> str:
    """
    Lower-case, strip diacritics, keep only alphanumeric.
    Ā→a, Č→c, Ē→e, Ģ→g, Ī→i, Ķ→k, Ļ→l, Ņ→n, Š→s, Ū→u, Ž→z.
    """
    nfkd = unicodedata.normalize("NFKD", text.lower())
    return re.sub(r"[^a-z0-9]", "", "".join(c for c in nfkd if not unicodedata.combining(c)))


def parse_gallery_name(raw_name: str) -> tuple[str, str]:
    """
    Split "SURNAME Firstname" (gallery always lists surname first, ALL-CAPS).
    Returns (surname, firstname). If no all-caps word found, treat whole as surname.
    """
    parts = raw_name.strip().split()
    # surname = consecutive ALL-CAPS tokens at start
    surname_parts = []
    first_parts   = []
    for part in parts:
        # Remove any diacritics for caps-check
        ascii_part = unicodedata.normalize("NFKD", part)
        ascii_part = "".join(c for c in ascii_part if not unicodedata.combining(c))
        if ascii_part.isupper() and len(ascii_part) > 1:
            surname_parts.append(part)
        else:
            first_parts.append(part)
    surname   = " ".join(surname_parts) if surname_parts else raw_name
    firstname = " ".join(first_parts)
    return surname, firstname


def make_match_key(surname: str, birth_year: int) -> str:
    return f"{normalise(surname)}-{birth_year}"


def artbase_id_match_key(artbase_id: str) -> str:
    """
    ART-SURNAME-BIRTHYEAR → normalised_surname-birthyear.
    Strips ART- prefix and last -YEAR segment, leaves middle as surname.
    """
    parts = artbase_id.replace("ART-", "").rsplit("-", 1)
    if len(parts) == 2 and parts[1].isdigit():
        return f"{normalise(parts[0])}-{parts[1]}"
    return normalise(artbase_id)


# ── Load source registry ────────────────────────────────────────────────────────

def load_source(source_id: str) -> dict:
    path = DATA_DIR / "sources" / f"{source_id}.json"
    if not path.exists():
        raise FileNotFoundError(f"Source registry file not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


# ── Fetch gallery list ──────────────────────────────────────────────────────────

def fetch_gallery_artists() -> list[dict]:
    """
    Fetch the complete Galerija Jēkabs artist index.

    paintings.lv renders artists by first letter — the default page (no param)
    returns the "A" group.  We iterate every letter that could appear as a
    Latvian/European surname initial, deduplicate by gallery_url, and return
    the merged list.
    """
    # All initials that appear in the gallery (Latin + Latvian extended)
    LETTERS = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ") + list("ĀČĒĢĪĶĻŅŠŪŽ")

    seen_urls: set[str] = set()
    all_artists: list[dict] = []

    for letter in LETTERS:
        url = f"{ARTIST_LIST_URL}?firstLetter={urllib.parse.quote(letter)}"
        req = urllib.request.Request(
            url,
            headers={"User-Agent": USER_AGENT, "Accept-Language": "lv,en;q=0.9"},
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                html = r.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as e:
            print(f"  ⚠ HTTP {e.code} for letter {letter!r} — skipping")
            time.sleep(RATE_SLEEP)
            continue
        except Exception as e:
            print(f"  ⚠ Error for letter {letter!r}: {e} — skipping")
            time.sleep(RATE_SLEEP)
            continue

        parser = ArtistListParser()
        parser.feed(html)

        new_this_letter = 0
        for entry in parser.artists:
            if entry["gallery_url"] not in seen_urls:
                seen_urls.add(entry["gallery_url"])
                all_artists.append(entry)
                new_this_letter += 1

        if new_this_letter:
            print(f"  Letter {letter}: {new_this_letter} artist(s)")
        time.sleep(RATE_SLEEP)

    print(f"  Total from gallery: {len(all_artists)} artists")
    return all_artists


# ── Attestation helpers ─────────────────────────────────────────────────────────

def build_attestation(gallery_entry: dict, today: str) -> dict:
    surname, firstname = parse_gallery_name(gallery_entry["raw_name"])
    full_name = f"{firstname} {surname}".strip() if firstname else surname
    asserts: dict = {"name": full_name}
    if gallery_entry["birth_year"]:
        asserts["birth_year"] = gallery_entry["birth_year"]
    if gallery_entry["death_year"]:
        asserts["death_year"] = gallery_entry["death_year"]
    return {
        "source_id":     SOURCE_ID,
        "role":          "data_origin",
        "url":           gallery_entry["gallery_url"],
        "asserts":       asserts,
        "authoritative": False,
        "retrieved":     today,
    }


def attestation_exists(artist_data: dict, gallery_url: str) -> bool:
    """Idempotency check — keyed on source_id + gallery_url."""
    for att in artist_data.get("attestations", []):
        if att.get("source_id") == SOURCE_ID and att.get("url") == gallery_url:
            return True
    return False


def check_date_discrepancy(artist_data: dict, gallery_entry: dict) -> Optional[dict]:
    """
    Compare gallery birth/death years against existing authoritative dates.
    Returns a discrepancy dict if conflict found, else None.
    Only compares against dates that have an explicit authoritative source.
    """
    life = artist_data.get("life", {})

    def get_year(date_block) -> Optional[int]:
        if not isinstance(date_block, dict):
            return None
        val = date_block.get("value", "")
        if not val:
            return None
        try:
            return int(str(val)[:4])
        except (ValueError, TypeError):
            return None

    def has_authority(date_block) -> bool:
        if not isinstance(date_block, dict):
            return False
        sources = date_block.get("source_ids", [])
        return bool(sources)

    discrepancies = []

    birth_block = life.get("birth_date", {})
    existing_birth = get_year(birth_block)
    if existing_birth and has_authority(birth_block):
        if gallery_entry.get("birth_year") and gallery_entry["birth_year"] != existing_birth:
            discrepancies.append({
                "field":    "birth_year",
                "gallery":  gallery_entry["birth_year"],
                "authority": existing_birth,
                "note":     "Gallery value differs from authoritative birth year — gallery NOT used.",
            })

    death_block = life.get("death_date", {})
    existing_death = get_year(death_block)
    if existing_death and has_authority(death_block):
        if gallery_entry.get("death_year") and gallery_entry["death_year"] != existing_death:
            discrepancies.append({
                "field":    "death_year",
                "gallery":  gallery_entry["death_year"],
                "authority": existing_death,
                "note":     "Gallery value differs from authoritative death year — gallery NOT used.",
            })

    if discrepancies:
        return {
            "source_id":   SOURCE_ID,
            "detected_at": datetime.now(timezone.utc).isoformat(),
            "conflicts":   discrepancies,
        }
    return None


# ── Process one artist ──────────────────────────────────────────────────────────

def process_artist(path: Path, gallery_entry: dict, dry_run: bool, today: str) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    artbase_id = data.get("artbase_id", path.stem)

    # Idempotency — don't add duplicate attestation
    if attestation_exists(data, gallery_entry["gallery_url"]):
        return {"id": artbase_id, "status": "already_attested"}

    attestation = build_attestation(gallery_entry, today)

    # Check for date discrepancies before writing
    discrepancy = check_date_discrepancy(data, gallery_entry)

    if not dry_run:
        # Add attestation
        if "attestations" not in data:
            data["attestations"] = []
        data["attestations"].append(attestation)

        # Record discrepancy if any
        if discrepancy:
            meta = data.setdefault("_meta", {})
            if "discrepancies" not in meta:
                meta["discrepancies"] = []
            meta["discrepancies"].append(discrepancy)

        # Update meta timestamp
        data.setdefault("_meta", {})["gallery_origin_attached"] = today
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    result: dict = {
        "id":          artbase_id,
        "status":      "matched",
        "gallery_url": gallery_entry["gallery_url"],
        "dry_run":     dry_run,
    }
    if discrepancy:
        result["discrepancy"] = discrepancy
    return result


# ── Main ────────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Attach Galerija Jēkabs data_origin attestations to Ars Accordia artists"
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--artist", metavar="ART-ID",
                       help="Process a single artist only")
    group.add_argument("--report", action="store_true",
                       help="Write match/unmatched reports only, do not modify JSONs")

    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would change without writing")
    args = parser.parse_args()

    if args.report:
        args.dry_run = True

    # Verify source is registered
    try:
        load_source(SOURCE_ID)
    except FileNotFoundError as e:
        print(f"✗ {e}")
        sys.exit(1)

    # Fetch gallery list — iterates all letters, returns deduplicated list
    gallery_artists = fetch_gallery_artists()

    # Build gallery lookup: match_key → gallery_entry
    gallery_by_key: dict[str, dict] = {}
    for entry in gallery_artists:
        surname, _ = parse_gallery_name(entry["raw_name"])
        key = make_match_key(surname, entry["birth_year"])
        gallery_by_key[key] = entry

    # Load Ars Accordia artists
    if args.artist:
        artist_files = [ARTISTS_DIR / f"{args.artist}.json"]
        if not artist_files[0].exists():
            print(f"✗ Artist file not found: {args.artist}")
            sys.exit(1)
    else:
        artist_files = sorted(ARTISTS_DIR.glob("ART-*.json"))

    today = date.today().isoformat()

    # Stats
    matched_ids:   set[str] = set()  # gallery keys matched to Ars Accordia
    results        = []
    unmatched_gallery = []
    without_gallery   = []

    for path in artist_files:
        artbase_id = path.stem
        ak = artbase_id_match_key(artbase_id)

        if ak in gallery_by_key:
            matched_ids.add(ak)
            gallery_entry = gallery_by_key[ak]
            result = process_artist(path, gallery_entry, args.dry_run, today)
            results.append(result)
            marker = "~" if args.dry_run else "✓"
            status = result["status"]
            disc   = " ⚠ DATE CONFLICT" if result.get("discrepancy") else ""
            if status == "already_attested":
                print(f"  = {artbase_id}: already attested")
            else:
                print(f"  {marker} {artbase_id}: matched → {gallery_entry['gallery_url']}{disc}")
        else:
            without_gallery.append(artbase_id)

    # Gallery entries not found in Ars Accordia
    for key, entry in gallery_by_key.items():
        if key not in matched_ids:
            unmatched_gallery.append({
                "raw_name":   entry["raw_name"],
                "birth_year": entry["birth_year"],
                "death_year": entry["death_year"],
                "gallery_url": entry["gallery_url"],
                "match_key":  key,
                "note":       "Gallery artist absent from Ars Accordia — discovery candidate; do NOT auto-create.",
            })

    # Report
    REPORTS_DIR.mkdir(exist_ok=True)
    matched_count    = sum(1 for r in results if r["status"] == "matched")
    attested_count   = sum(1 for r in results if r["status"] == "already_attested")
    discrepancy_count = sum(1 for r in results if r.get("discrepancy"))
    dry_tag = " (DRY RUN)" if args.dry_run else ""

    print(f"\nMatched:          {matched_count} artists attached{dry_tag}")
    print(f"Already attested: {attested_count}")
    print(f"Date conflicts:   {discrepancy_count}")
    print(f"Unmatched gallery:{len(unmatched_gallery)}")
    print(f"Without gallery:  {len(without_gallery)}")

    # Write reports
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    if unmatched_gallery:
        out = REPORTS_DIR / f"gallery_unmatched_{ts}.json"
        out.write_text(json.dumps(unmatched_gallery, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Gallery-unmatched: {out}")

    if without_gallery:
        out = REPORTS_DIR / f"artists_without_gallery_origin_{ts}.json"
        out.write_text(json.dumps(without_gallery, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Without gallery:   {out}")

    if results:
        out = REPORTS_DIR / f"gallery_ingest_{ts}.json"
        out.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Ingest report:     {out}")


if __name__ == "__main__":
    main()
