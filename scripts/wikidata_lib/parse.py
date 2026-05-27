"""
wikidata_lib/parse.py

Claim parsing and date precision handling.
Never synthesises values — if Wikidata doesn't have it precisely, we store None.
"""

from __future__ import annotations

from typing import Any, Optional


# ── Precision constants ────────────────────────────────────────────────────────
PRECISION_CENTURY = 7
PRECISION_DECADE  = 8
PRECISION_YEAR    = 9
PRECISION_MONTH   = 10
PRECISION_DAY     = 11


def get_claim_snak(entity: dict, pid: str) -> Optional[dict]:
    """Return the best-rank mainsnak for a property, or None."""
    claims = entity.get("claims", {}).get(pid, [])
    if not claims:
        return None
    # Prefer preferred rank, then normal, ignore deprecated
    for rank in ("preferred", "normal"):
        for claim in claims:
            if claim.get("rank", "normal") == rank:
                snak = claim.get("mainsnak", {})
                if snak.get("snaktype") == "value":
                    return snak
    return None


def get_string_value(entity: dict, pid: str) -> Optional[str]:
    """Return the string value for a property (e.g. VIAF ID, LNDB)."""
    snak = get_claim_snak(entity, pid)
    if not snak:
        return None
    dv = snak.get("datavalue", {})
    if dv.get("type") == "string":
        return dv["value"]
    return None


def get_entity_id(entity: dict, pid: str) -> Optional[str]:
    """Return the QID value for a wikibase-entityid property (e.g. birth place)."""
    snak = get_claim_snak(entity, pid)
    if not snak:
        return None
    dv = snak.get("datavalue", {})
    if dv.get("type") == "wikibase-entityid":
        return dv["value"].get("id")
    return None


def get_all_entity_ids(entity: dict, pid: str) -> list[str]:
    """Return all QID values for a property (e.g. all occupations, all movements)."""
    claims = entity.get("claims", {}).get(pid, [])
    results = []
    for claim in claims:
        if claim.get("rank") == "deprecated":
            continue
        snak = claim.get("mainsnak", {})
        if snak.get("snaktype") == "value":
            dv = snak.get("datavalue", {})
            if dv.get("type") == "wikibase-entityid":
                qid = dv["value"].get("id")
                if qid:
                    results.append(qid)
    return results


def parse_time_value(entity: dict, pid: str) -> tuple[Optional[str], Optional[str]]:
    """
    Parse a Wikidata time claim into (iso_value, precision_label).

    Returns:
        ("1913-07-30", "day")    for precision 11
        ("1913-07",    "month")  for precision 10
        ("1913",       "year")   for precision 9
        (None, None)             if not present or lower precision

    Never synthesises — 1913 stays 1913, not 1913-01-01.
    """
    snak = get_claim_snak(entity, pid)
    if not snak:
        return None, None
    dv = snak.get("datavalue", {})
    if dv.get("type") != "time":
        return None, None
    tv = dv["value"]
    precision = tv.get("precision", 0)
    raw_time  = tv.get("time", "")  # e.g. "+1913-07-30T00:00:00Z"

    # Strip leading +/- and T... suffix
    # Format is ±YYYY-MM-DDT...
    raw = raw_time.lstrip("+-")
    parts = raw.split("T")[0]  # "YYYY-MM-DD"
    segments = parts.split("-")

    if precision >= PRECISION_DAY and len(segments) >= 3:
        return f"{segments[0]}-{segments[1]}-{segments[2]}", "day"
    elif precision >= PRECISION_MONTH and len(segments) >= 2:
        return f"{segments[0]}-{segments[1]}", "month"
    elif precision >= PRECISION_YEAR and len(segments) >= 1:
        return segments[0], "year"
    return None, None


def get_image_filename(entity: dict) -> Optional[str]:
    """Return the Commons filename for P18 (image), or None."""
    return get_string_value(entity, "P18")


def build_image_urls(filename: str) -> dict:
    """Build Commons URLs from a filename. Uses Special:FilePath to avoid MD5 hashing."""
    encoded = filename.replace(" ", "_")
    import urllib.parse
    safe = urllib.parse.quote(encoded, safe="")
    return {
        "commons_filename": filename,
        "commons_url":      f"https://commons.wikimedia.org/wiki/File:{encoded}",
        "thumb_url":        f"https://commons.wikimedia.org/wiki/Special:FilePath/{safe}?width=400",
    }


def get_description(entity: dict, lang: str) -> Optional[str]:
    """Return Wikidata's short description in the given language."""
    return entity.get("descriptions", {}).get(lang, {}).get("value")
