"""
wikidata_lib/airtable_sync.py

Atomic Airtable sync for Wikidata enrichment results.
Only updates the columns managed by wikidata_enrich.py.
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Optional

AIRTABLE_API = "https://api.airtable.com/v0"

# Column names we manage in Artists_Makers
FIELD_BIRTH_DATE        = "Birth Date"
FIELD_DEATH_DATE        = "Death Date"
FIELD_BIRTH_PLACE       = "Birth Place"
FIELD_DEATH_PLACE       = "Death Place"
FIELD_LNDB_ID           = "LNDB ID"
FIELD_IMAGE_URL         = "Wikimedia Image URL"
FIELD_DESCRIPTION_EN    = "Description (EN)"
FIELD_EDUCATION         = "Education"
FIELD_MOVEMENT          = "Movement"
FIELD_GENRE             = "Genre"
FIELD_LAST_WD_SYNC      = "Last Wikidata Sync"


class AirtableSync:
    def __init__(self, token: str, base_id: str, table_name: str = "Artists_Makers"):
        self._token      = token
        self._base_id    = base_id
        self._table_name = table_name
        self._headers    = {
            "Authorization":  f"Bearer {token}",
            "Content-Type":   "application/json",
        }

    def _url(self) -> str:
        table_enc = urllib.parse.quote(self._table_name)
        return f"{AIRTABLE_API}/{self._base_id}/{table_enc}"

    def _request(self, method: str, url: str, body: Optional[dict] = None, retries: int = 2) -> dict:
        data = json.dumps(body).encode() if body else None
        for attempt in range(retries + 1):
            req = urllib.request.Request(url, data=data, headers=self._headers, method=method)
            try:
                with urllib.request.urlopen(req, timeout=20) as r:
                    return json.loads(r.read())
            except urllib.error.HTTPError as e:
                if e.code == 429 and attempt < retries:
                    time.sleep(5.0)
                    continue
                body_text = e.read().decode(errors="replace")
                raise RuntimeError(f"Airtable {method} {url} → HTTP {e.code}: {body_text}") from e

    def find_record_id(self, artbase_id: str) -> Optional[str]:
        """Look up the Airtable record ID for an artist by their Ars Accordia ID."""
        formula = urllib.parse.quote(f'{{Artist ID}}="{artbase_id}"')
        url = f"{self._url()}?filterByFormula={formula}&maxRecords=1"
        data = self._request("GET", url)
        records = data.get("records", [])
        return records[0]["id"] if records else None

    def update_enrichment(self, airtable_record_id: str, fields: dict[str, Any]) -> dict:
        """Update a single artist record with enrichment fields."""
        url = f"{self._url()}/{airtable_record_id}"
        return self._request("PATCH", url, {"fields": fields})

    def build_fields(self, enriched: dict, sync_timestamp: str) -> dict[str, Any]:
        """
        Convert enriched data dict into Airtable field names.
        Only includes fields that have values (no None writes).
        """
        fields: dict[str, Any] = {}

        if enriched.get("birth_date"):
            fields[FIELD_BIRTH_DATE] = enriched["birth_date"]
        if enriched.get("death_date"):
            fields[FIELD_DEATH_DATE] = enriched["death_date"]
        if enriched.get("birth_place"):
            fields[FIELD_BIRTH_PLACE] = enriched["birth_place"].get("label", "")
        if enriched.get("death_place"):
            fields[FIELD_DEATH_PLACE] = enriched["death_place"].get("label", "")
        if enriched.get("lndb_id"):
            fields[FIELD_LNDB_ID] = enriched["lndb_id"]
        if enriched.get("image") and enriched["image"].get("thumb_url"):
            fields[FIELD_IMAGE_URL] = enriched["image"]["thumb_url"]
        if enriched.get("description_en"):
            fields[FIELD_DESCRIPTION_EN] = enriched["description_en"]

        # Tier 2 — comma-separated labels
        if enriched.get("education"):
            fields[FIELD_EDUCATION] = ", ".join(
                e.get("label", "") for e in enriched["education"] if e.get("label")
            )
        if enriched.get("movement"):
            fields[FIELD_MOVEMENT] = ", ".join(
                e.get("label", "") for e in enriched["movement"] if e.get("label")
            )
        if enriched.get("genre"):
            fields[FIELD_GENRE] = ", ".join(
                e.get("label", "") for e in enriched["genre"] if e.get("label")
            )

        fields[FIELD_LAST_WD_SYNC] = sync_timestamp
        return fields
