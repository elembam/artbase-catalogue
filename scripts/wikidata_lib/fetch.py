"""
wikidata_lib/fetch.py

Low-level Wikidata API access:
- wbgetentities with batching (50 per call)
- Rate limiting (1 req/s anonymous)
- Retry on 429
- User-Agent as required by Wikidata policy
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Optional

WIKIDATA_API  = "https://www.wikidata.org/w/api.php"
WIKIPEDIA_API = "https://{lang}.wikipedia.org/w/api.php"
USER_AGENT    = "Ars Accordia/1.0 (https://github.com/elembam/artbase-catalogue)"
BATCH_SIZE    = 50
RATE_SLEEP    = 1.05  # seconds between calls — stay under 1 req/s


def _get(params: dict, retries: int = 1) -> dict:
    """Make a single Wikidata API call with retry on 429."""
    params["format"] = "json"
    url = WIKIDATA_API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < retries:
                time.sleep(5.0)
                continue
            raise
    return {}


def _get_url(url: str, retries: int = 1) -> dict:
    """Make a raw GET request and return parsed JSON."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < retries:
                time.sleep(5.0)
                continue
            raise
        except Exception:
            return {}
    return {}


def fetch_entities(qids: list[str], props: str = "info|labels|descriptions|claims|sitelinks") -> dict[str, dict]:
    """
    Fetch up to BATCH_SIZE entities per call. Returns {qid: entity_dict}.
    Entities not found or missing are returned as empty dicts.
    """
    results: dict[str, dict] = {}
    for i in range(0, len(qids), BATCH_SIZE):
        batch = qids[i : i + BATCH_SIZE]
        data = _get({
            "action":    "wbgetentities",
            "ids":       "|".join(batch),
            "languages": "en|lv",
            "props":     props,
        })
        for qid, entity in data.get("entities", {}).items():
            # Wikidata returns {"missing": ""} for unknown QIDs
            if "missing" not in entity:
                results[qid] = entity
        time.sleep(RATE_SLEEP)
    return results


def fetch_entity(qid: str) -> Optional[dict]:
    """Fetch a single entity. Returns None if not found."""
    results = fetch_entities([qid])
    return results.get(qid)


def get_revision_id(entity: dict) -> Optional[int]:
    return entity.get("lastrevid")


def is_redirect(entity: dict) -> bool:
    """Wikidata redirects appear as entities with a 'redirects' key."""
    return "redirects" in entity


def fetch_wikipedia_summary(entity: dict, lang: str = "en") -> Optional[str]:
    """
    Fetch the lead-paragraph summary from Wikipedia for a Wikidata entity.
    Uses the entity's sitelinks to find the Wikipedia article title, then
    calls the Wikipedia REST summary API.
    Returns plain text (no markup), or None if not available.
    """
    sitelinks = entity.get("sitelinks", {})
    site_key  = f"{lang}wiki"
    title = sitelinks.get(site_key, {}).get("title")
    if not title:
        return None

    url = (
        f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/"
        + urllib.parse.quote(title.replace(" ", "_"))
    )
    try:
        data = _get_url(url)
        extract = data.get("extract") or data.get("extract_html")
        if extract:
            # Return first 600 chars — enough for a bio paragraph
            return extract[:600].strip()
    except Exception:
        pass
    return None
