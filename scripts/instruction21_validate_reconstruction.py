#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Instruction 21 -- independently validate the artist JSON records
reconstructed in commit RECON_COMMIT against policy. Re-parses each
record's source HTML page fresh from git history (does not import/reuse
the original reconstruction script), so this is a genuine second check,
not a tautological confirmation of its own output.

Ground truth is the PRE-reconstruction archived page
(`git show <RECON_COMMIT>^:artists/<ID>.html`), not the current
working-tree file -- artist_profile_generator.py was run after
reconstruction and rewrites every page from the current template, which
uses different Sources-section markup than the archived "Galerija Jekabs
era" pages the reconstruction actually read from. Diffing against the
live page would wrongly flag every gallery-sourced record as unsupported.

Policy checked per record:
  P1  identity.preferred_name matches the archived page's <title> exactly
  P2  life.birth_date.value matches the archived page's artist-dates
      block exactly (or is null if the page showed none)
  P3  life.birth_date.status is "working" wherever a birth year is
      asserted -- never "confirmed" (this is gallery-sourced, unconfirmed
      data)
  P4  sources[] contains the page's Galerija Jekabs origin URL if and
      only if the archived page carried one -- nothing invented, nothing
      dropped
  P5  descriptors.nationality / descriptors.occupations match the page's
      "Nationality . Occupation" line exactly
  P6  no Airtable-pipeline contamination: airtable_id and
      artbase_canonical_id are null, cataloguing.catalogued_by is null,
      cataloguing.review_status is "draft", no authority_links entry
      carries a resolved id
  P7  no asserted value for any field the archived page never displayed
      (death_date, birth_place, etc.)

Usage:
    python3 scripts/instruction21_validate_reconstruction.py [--commit SHA] [--json OUT.json]
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ARTISTS_DIR = REPO / "artbase_export" / "data" / "artists"

DEFAULT_RECON_COMMIT = "9b9814a"


def reconstructed_ids(commit: str) -> list[str]:
    out = subprocess.run(
        ["git", "show", commit, "--diff-filter=A", "--name-only"],
        cwd=REPO, capture_output=True, text=True, check=True,
    ).stdout
    ids = []
    for line in out.splitlines():
        if line.startswith("artbase_export/data/artists/ART-") and line.endswith(".json"):
            ids.append(Path(line).stem)
    return sorted(ids)


def validate(commit: str) -> list[dict]:
    results = []
    for aid in reconstructed_ids(commit):
        json_path = ARTISTS_DIR / f"{aid}.json"
        rec = json.loads(json_path.read_text())
        txt = subprocess.run(
            ["git", "show", f"{commit}^:artists/{aid}.html"],
            cwd=REPO, capture_output=True, text=True, check=True,
        ).stdout

        m_title = re.search(r"<title>([^<]*)—", txt)
        m_dates = re.search(r'artist-dates">\s*([^<]*?)\s*</div>', txt)
        m_origin = re.search(r'origin-chip">\s*<a href="([^"]*)"[^>]*>([^<]*)</a>', txt)
        m_nat = re.search(r'artist-nationality">([^<]*)</div>', txt)

        page_name = m_title.group(1).strip() if m_title else None
        page_birth = (re.search(r"\d{4}", m_dates.group(1)).group(0)
                      if m_dates and re.search(r"\d{4}", m_dates.group(1)) else None)
        page_origin_url = m_origin.group(1) if m_origin else None
        page_origin_label = m_origin.group(2).strip() if m_origin else None
        page_nat = m_nat.group(1).strip() if m_nat else None

        exceptions = []

        if rec.get("identity", {}).get("preferred_name") != page_name:
            exceptions.append(
                f"P1 name mismatch: json={rec.get('identity', {}).get('preferred_name')!r} page={page_name!r}")

        json_birth = rec.get("life", {}).get("birth_date", {}).get("value")
        if json_birth != page_birth:
            exceptions.append(f"P2 birth_year mismatch: json={json_birth!r} page={page_birth!r}")

        status = rec.get("life", {}).get("birth_date", {}).get("status")
        if json_birth is not None and status != "working":
            exceptions.append(
                f"P3 birth_date.status should be 'working' for unconfirmed page-derived data, got {status!r}")
        if status == "confirmed":
            exceptions.append("P3 birth_date.status is 'confirmed' -- policy forbids asserting confirmation for gallery-only data")

        sources = rec.get("sources") or []
        src_urls = [s.get("url") for s in sources if isinstance(s, dict)]
        if page_origin_url:
            if page_origin_url not in src_urls:
                exceptions.append(f"P4 page has origin chip {page_origin_url!r} not reflected in sources[]")
        elif sources:
            exceptions.append(f"P4 page has NO origin chip but sources[] is non-empty: {src_urls}")

        nationality = rec.get("descriptors", {}).get("nationality")
        occupations = rec.get("descriptors", {}).get("occupations") or []
        if page_nat:
            expected_nat, _, expected_occ = page_nat.partition(" · ")
            if nationality != expected_nat.strip():
                exceptions.append(f"P5 nationality mismatch: json={nationality!r} page={expected_nat.strip()!r}")
            if occupations != [expected_occ.strip()]:
                exceptions.append(f"P5 occupations mismatch: json={occupations!r} page={[expected_occ.strip()]!r}")

        if rec.get("airtable_id") is not None:
            exceptions.append(f"P6 airtable_id is not null: {rec.get('airtable_id')!r}")
        if rec.get("artbase_canonical_id") is not None:
            exceptions.append(f"P6 artbase_canonical_id is not null: {rec.get('artbase_canonical_id')!r}")
        cat = rec.get("cataloguing") or {}
        if cat.get("catalogued_by") is not None:
            exceptions.append(f"P6 cataloguing.catalogued_by is not null: {cat.get('catalogued_by')!r}")
        if cat.get("review_status") != "draft":
            exceptions.append(f"P6 cataloguing.review_status should be 'draft', got {cat.get('review_status')!r}")
        al = rec.get("authority_links") or {}
        bad_auth = [k for k, v in al.items() if isinstance(v, dict) and v.get("id") is not None]
        if bad_auth:
            exceptions.append(f"P6 authority_links has non-null ids (should all be unresolved): {bad_auth}")

        if rec.get("life", {}).get("death_date", {}).get("value") is not None:
            exceptions.append("P7 death_date has a value -- not present on any of these pages")
        if rec.get("life", {}).get("birth_place", {}).get("display") is not None:
            exceptions.append("P7 birth_place.display has a value -- not present on any of these pages")

        results.append({
            "artbase_id": aid,
            "status": "PASS" if not exceptions else "FAIL",
            "page_derived": {
                "name": page_name, "birth_year": page_birth,
                "origin_url": page_origin_url, "origin_label": page_origin_label,
                "nationality_occupation": page_nat,
            },
            "exceptions": exceptions,
        })
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--commit", default=DEFAULT_RECON_COMMIT,
                         help=f"Reconstruction commit to validate against (default: {DEFAULT_RECON_COMMIT})")
    parser.add_argument("--json", default=None, help="Write full machine-readable results to this path")
    args = parser.parse_args()

    results = validate(args.commit)
    total = len(results)
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = total - passed

    print(f"Total checked: {total}")
    print(f"Pass: {passed}")
    print(f"Fail: {failed}")
    for r in results:
        if r["exceptions"]:
            print(f"\n{r['artbase_id']} -- {r['status']}")
            for e in r["exceptions"]:
                print(f"  - {e}")

    if args.json:
        Path(args.json).write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
