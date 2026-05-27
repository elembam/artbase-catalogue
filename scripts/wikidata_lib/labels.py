"""
wikidata_lib/labels.py

QID → English label resolution with 30-day disk cache.
Batches up to 50 QIDs per call using wbgetentities.
"""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

from . import fetch as wdfetch

CACHE_TTL_DAYS = 30
CACHE_PATH = Path(__file__).resolve().parent.parent.parent / "artbase_export" / "data" / "_cache" / "wikidata_labels.json"

# in-memory cache for this run
_cache: dict[str, dict] = {}  # {qid: {"label": str, "fetched": iso_str}}
_dirty = False


def _load_cache() -> None:
    global _cache, _dirty
    if CACHE_PATH.exists():
        try:
            _cache = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            _cache = {}
    _dirty = False


def _save_cache() -> None:
    global _dirty
    if not _dirty:
        return
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(json.dumps(_cache, ensure_ascii=False, indent=2), encoding="utf-8")
    _dirty = False


def _is_fresh(entry: dict) -> bool:
    try:
        fetched = datetime.fromisoformat(entry["fetched"])
        return (datetime.now(timezone.utc) - fetched) < timedelta(days=CACHE_TTL_DAYS)
    except (KeyError, ValueError):
        return False


def _fetch_and_cache(qids: list[str]) -> None:
    """Fetch labels for QIDs not in cache (or stale) and update cache."""
    global _dirty
    to_fetch = [q for q in qids if q not in _cache or not _is_fresh(_cache[q])]
    if not to_fetch:
        return

    now = datetime.now(timezone.utc).isoformat()
    entities = wdfetch.fetch_entities(to_fetch, props="info|labels")
    for qid in to_fetch:
        entity = entities.get(qid, {})
        labels = entity.get("labels", {})
        # prefer en, then lv, then any available label
        label = (
            labels.get("en", {}).get("value")
            or labels.get("lv", {}).get("value")
            or next((v["value"] for v in labels.values() if v.get("value")), qid)
        )
        _cache[qid] = {"label": label, "fetched": now}
        _dirty = True


def resolve(qids: list[str]) -> dict[str, str]:
    """
    Return {qid: label} for all requested QIDs.
    Unknown QIDs fall back to the QID itself.
    """
    _fetch_and_cache(qids)
    _save_cache()
    return {q: _cache.get(q, {}).get("label", q) for q in qids}


def label_for(qid: str) -> str:
    """Resolve a single QID to its English label."""
    return resolve([qid]).get(qid, qid)


# Load cache on module import
_load_cache()
