"""
artbase_export/airtable/client.py

Thin wrapper around pyairtable that handles:
- Authentication and table access
- Fetching with retries and rate-limit awareness
- Expanding linked records (sources, authority links)
- Returning typed dictionaries ready for the transform layer
"""

from __future__ import annotations

import logging
from typing import Any, Generator

from pyairtable import Api
from pyairtable.models.schema import TableSchema

from artbase_export.airtable.schema import (
    ArtistFields, ArtworkFields, AuthorityFields, SourceFields, Tables
)

logger = logging.getLogger(__name__)


class AirtableClient:
    """
    Wraps pyairtable with ArtBase-specific conventions.

    Usage:
        client = AirtableClient(token="patXXXX", base_id="appXXXX")
        for artist in client.iter_artists():
            print(artist[ArtistFields.PREFERRED_NAME])
    """

    def __init__(self, token: str, base_id: str, table_names: dict | None = None):
        self._api      = Api(token)
        self._base     = self._api.base(base_id)
        self._names    = table_names or {}

    def _table_name(self, default: str, key: str) -> str:
        """Resolve a table name from config override or fall back to default."""
        return self._names.get(key, default)

    def _artists_table(self):
        name = self._table_name(Tables.ARTISTS, "artists")
        return self._api.table(self._base.id, name)

    def _artworks_table(self):
        name = self._table_name(Tables.ARTWORKS, "artworks")
        return self._api.table(self._base.id, name)

    def _sources_table(self):
        name = self._table_name(Tables.SOURCES, "sources")
        return self._api.table(self._base.id, name)

    def _authority_links_table(self):
        name = self._table_name(Tables.AUTHORITY_LINKS, "authority_links")
        return self._api.table(self._base.id, name)

    # ── Fetching ───────────────────────────────────────────────────────────────

    def iter_artists(
        self,
        artist_id: str | None = None,
    ) -> Generator[dict[str, Any], None, None]:
        """
        Iterate over all artist records, yielding enriched dicts.

        If artist_id is given, fetch only that one artist (by the
        "Artist ID" field value, e.g. ART-HERBERTS-SILINS-1926).

        Each yielded dict has:
          - All Airtable fields (via record["fields"])
          - "_airtable_record_id": the Airtable rec-ID
          - "_sources": list of expanded source document dicts
          - "_authority_links": list of expanded authority link dicts
        """
        table = self._artists_table()

        if artist_id:
            formula = f'{{Artist ID}} = "{artist_id}"'
            records = table.all(formula=formula)
        else:
            records = table.all()

        logger.info(f"Fetched {len(records)} artist record(s) from Airtable")

        # Pre-fetch all sources and authority links to avoid N+1 queries
        all_sources     = self._index_sources()
        all_authorities = self._index_authority_links()

        for record in records:
            fields = record["fields"]
            enriched = dict(fields)
            enriched["_airtable_record_id"] = record["id"]

            # Expand linked sources
            linked_source_ids = fields.get(ArtistFields.SOURCES, [])
            enriched["_sources"] = [
                all_sources[rid] for rid in linked_source_ids
                if rid in all_sources
            ]

            # Expand linked authority links
            linked_auth_ids = fields.get(ArtistFields.AUTHORITY_LINKS, [])
            enriched["_authority_links"] = [
                all_authorities[rid] for rid in linked_auth_ids
                if rid in all_authorities
            ]

            yield enriched

    def iter_artworks(
        self,
        artwork_id: str | None = None,
    ) -> Generator[dict[str, Any], None, None]:
        """Iterate over all artwork records, yielding enriched dicts."""
        table = self._artworks_table()

        if artwork_id:
            formula = f'{{Artwork ID}} = "{artwork_id}"'
            records = table.all(formula=formula)
        else:
            records = table.all()

        logger.info(f"Fetched {len(records)} artwork record(s) from Airtable")

        all_sources     = self._index_sources()
        all_authorities = self._index_authority_links()

        for record in records:
            fields = record["fields"]
            enriched = dict(fields)
            enriched["_airtable_record_id"] = record["id"]

            linked_source_ids = fields.get(ArtworkFields.SOURCES, [])
            enriched["_sources"] = [
                all_sources[rid] for rid in linked_source_ids
                if rid in all_sources
            ]

            linked_auth_ids = fields.get(ArtworkFields.AUTHORITY_LINKS, [])
            enriched["_authority_links"] = [
                all_authorities[rid] for rid in linked_auth_ids
                if rid in all_authorities
            ]

            # Expand the linked Artist field (a linked record to Artists_Makers)
            artist_links = fields.get(ArtworkFields.ARTIST, [])
            enriched["_artist_airtable_id"] = artist_links[0] if artist_links else None

            yield enriched

    # ── Pre-fetch helpers ──────────────────────────────────────────────────────

    def _index_sources(self) -> dict[str, dict]:
        """Return all source documents indexed by Airtable record ID."""
        table   = self._sources_table()
        records = table.all()
        return {r["id"]: {**r["fields"], "_airtable_record_id": r["id"]}
                for r in records}

    def _index_authority_links(self) -> dict[str, dict]:
        """Return all authority link records indexed by Airtable record ID."""
        table   = self._authority_links_table()
        records = table.all()
        return {r["id"]: {**r["fields"], "_airtable_record_id": r["id"]}
                for r in records}

    # ── Optional: write ArtBase IDs back to Airtable ──────────────────────────

    def write_artbase_id(
        self, table_key: str, airtable_record_id: str, artbase_id: str
    ) -> None:
        """
        Write a generated ArtBase ID back to the Airtable record.
        Only called when the field is empty — never overwrites existing IDs.

        table_key: "artists" or "artworks"
        """
        if table_key == "artists":
            table       = self._artists_table()
            field_name  = ArtistFields.ARTBASE_ID
        elif table_key == "artworks":
            table       = self._artworks_table()
            field_name  = ArtworkFields.ARTBASE_ID
        else:
            raise ValueError(f"Unknown table_key: {table_key}")

        table.update(airtable_record_id, {field_name: artbase_id})
        logger.info(f"Wrote {artbase_id} → Airtable {airtable_record_id}")
