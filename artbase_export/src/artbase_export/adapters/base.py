"""
artbase_export/adapters/base.py

Abstract interface for collection source adapters.

Every adapter (SMK, Rijksmuseum, Met, Europeana, …) implements this
interface. The canonical passport schema and authority model never change
to accommodate a new source — adapters conform to this seam.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class CollectionSourceAdapter(ABC):
    """Fetch, normalise, and cite one collection API source."""

    # ── Core fetch ────────────────────────────────────────────────────────────

    @abstractmethod
    def fetch_object_by_id(self, object_id: str) -> dict:
        """Fetch a single raw object record from the source by inventory number.

        Returns the raw response dict. Raises ValueError if not found.
        """

    @abstractmethod
    def search_objects(self, query: str) -> list[dict]:
        """Search the source by keyword. Returns a list of raw records."""

    # ── Normalisation ─────────────────────────────────────────────────────────

    @abstractmethod
    def normalize_to_object_record(self, raw: dict) -> dict:
        """Map a raw source record to the canonical passport dict.

        Only fields present in the source record are populated.
        Absent fields are not invented — they remain gaps.
        """

    @abstractmethod
    def extract_authority_links(self, raw: dict) -> list[dict]:
        """Return a list of authority link dicts, each with:

            {scope, system, id, uri, status}

        scope: one of the AuthorityScope enum values
        system: human name of the authority ("SMK", "Wikidata", "ULAN", …)
        """

    @abstractmethod
    def extract_media(self, raw: dict) -> list[dict]:
        """Return media records, gated by per-object rights.

        Only returns records where the rights field allows reuse.
        Format: {type, uri, iiif_service, width, height, rights_verified}
        """

    @abstractmethod
    def extract_rights(self, raw: dict) -> dict:
        """Return the per-object rights block.

        Format: {public_domain, license, copyright_status, attribution, source}
        Never assumes CC0 — reads the per-object flag.
        Missing / ambiguous → treat as restricted.
        """

    @abstractmethod
    def extract_source_citation(self, raw: dict) -> dict:
        """Return a Source_Documents record for this source's API record.

        The citation attributes all imported fields to the source.
        Format matches SourceDocument: {source_id, source_type, title, url,
        access_date, publisher, license}
        """

    @abstractmethod
    def produce_import_report(self, raw: dict) -> str:
        """Return a human-readable import report string.

        Covers: fields imported / missing / needs-reconciliation.
        Used by the --report CLI mode.
        """
