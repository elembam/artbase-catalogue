"""
artbase_export/transform/artist.py

Transforms an enriched Airtable Artists_Makers record into a CanonicalArtist.
Field names match the artwork_passport_airtable_starter_kit exactly.
"""

from __future__ import annotations
import logging
from typing import Any

from artbase_export.airtable.schema import ArtistFields, SourceFields
from artbase_export.canonical.models import (
    AatTerm, ArtistAuthorityLinks, ArtistCataloguing, ArtistDescriptors,
    ArtistIdentity, ArtistLife, AuthorityLink, AuthorityStatus,
    CanonicalArtist, ConflictRecord, ConflictStatus, DateField,
    PlaceField, ReviewStatus, SourceDocument, SourceReference,
    Visibility,
)

logger = logging.getLogger(__name__)


def transform_artist(raw: dict[str, Any]) -> CanonicalArtist:
    """
    Convert an enriched Airtable artist record to CanonicalArtist.
    raw comes from AirtableClient.iter_artists() with _sources and _authority_links expanded.
    """
    f = raw

    preferred_name = _str(f, ArtistFields.PREFERRED_NAME) or _str(f, ArtistFields.DISPLAY_NAME)
    if not preferred_name:
        raise ValueError(f"Artist record {f.get(ArtistFields.ID, '?')} has no name")

    # ── Identity ─────────────────────────────────────────────────────────────
    identity = ArtistIdentity(
        preferred_name  = preferred_name,
        full_name       = _str(f, ArtistFields.PREFERRED_NAME),  # use full form if Display Name is shorthand
        name_variants   = [],
        sort_name       = _str(f, ArtistFields.SORT_NAME) or _derive_sort_name(preferred_name),
    )

    # ── Life dates ───────────────────────────────────────────────────────────
    # Starter kit uses integer Birth Year / Death Year, not full dates
    birth_year = _int(f, ArtistFields.BIRTH_YEAR)
    death_year = _int(f, ArtistFields.DEATH_YEAR)

    birth_date = DateField(
        value       = str(birth_year) if birth_year else None,
        precision   = "year",
        status      = "working",
    )
    death_date = DateField(
        value       = str(death_year) if death_year else None,
        precision   = "year",
        status      = "working",
    )

    life = ArtistLife(
        birth_date  = birth_date,
        death_date  = death_date,
        birth_place = PlaceField(display=_str(f, ArtistFields.BIRTH_PLACE)),
        death_place = PlaceField(display=_str(f, ArtistFields.DEATH_PLACE)),
    )

    # ── Descriptors ──────────────────────────────────────────────────────────
    descriptors = ArtistDescriptors(
        nationality = _str(f, ArtistFields.NATIONALITY),
        occupations = _semicolons(f, ArtistFields.ROLES),
    )

    # ── Authority links — inline in Artists_Makers in the starter kit ────────
    authority_links = ArtistAuthorityLinks(
        wikidata = AuthorityLink(
            id      = _str(f, ArtistFields.WIKIDATA_QID),
            uri     = _str(f, ArtistFields.WIKIDATA_URL),
            status  = _authority_status(f, ArtistFields.WIKIDATA_QID, ArtistFields.WIKIDATA_STATUS),
        ),
        viaf = AuthorityLink(
            id      = _str(f, ArtistFields.VIAF_ID),
            status  = AuthorityStatus.CONFIRMED if _str(f, ArtistFields.VIAF_ID) else AuthorityStatus.SEARCH_NEEDED,
        ),
        ulan = AuthorityLink(
            id      = _str(f, ArtistFields.ULAN_ID),
            uri     = _str(f, ArtistFields.ULAN_URI),
            status  = AuthorityStatus.CONFIRMED if _str(f, ArtistFields.ULAN_ID) else AuthorityStatus.SEARCH_NEEDED,
        ),
        isni = AuthorityLink(
            id      = _str(f, ArtistFields.ISNI),
            status  = AuthorityStatus.CONFIRMED if _str(f, ArtistFields.ISNI) else AuthorityStatus.SEARCH_NEEDED,
        ),
        rkd = AuthorityLink(
            id      = _str(f, ArtistFields.RKD_ID),
            status  = AuthorityStatus.CONFIRMED if _str(f, ArtistFields.RKD_ID) else AuthorityStatus.SEARCH_NEEDED,
        ),
    )

    # ── Sources ───────────────────────────────────────────────────────────────
    sources = [_transform_source(s) for s in f.get("_sources", [])]

    # Also capture Source URLs text field if no linked records
    source_urls_raw = _str(f, ArtistFields.SOURCE_URLS) or ""
    for i, url in enumerate(source_urls_raw.split(";"), start=1):
        url = url.strip()
        if url and not any(s.url == url for s in sources):
            sources.append(SourceDocument(
                source_id   = f"SRC-INLINE-{i:03}",
                source_type = "URL reference",
                url         = url,
            ))

    # ── Cataloguing ───────────────────────────────────────────────────────────
    review_raw = _str(f, ArtistFields.REVIEW_STATUS) or "Draft"
    try:
        review_status = ReviewStatus(review_raw.lower())
    except ValueError:
        review_status = ReviewStatus.DRAFT

    cataloguing = ArtistCataloguing(
        review_status   = review_status,
        notes           = _str(f, ArtistFields.NOTES),
    )

    # Wikidata improvement tasks
    tasks = []
    wikidata_status = _str(f, ArtistFields.WIKIDATA_STATUS)
    if wikidata_status == "create_candidate":
        tasks.append("Create Wikidata entry (candidate identified)")
    if not _str(f, ArtistFields.VIAF_ID):
        tasks.append("Search VIAF")
    if not _str(f, ArtistFields.ULAN_ID):
        tasks.append("Search Getty ULAN")
    cataloguing.tasks = tasks

    return CanonicalArtist(
        artbase_id      = _str(f, ArtistFields.ID) or "UNKNOWN",
        airtable_id     = f.get("_airtable_record_id"),
        visibility      = Visibility.PRIVATE,
        identity        = identity,
        life            = life,
        descriptors     = descriptors,
        authority_links = authority_links,
        sources         = sources,
        source_refs     = [SourceReference(source_id=s.source_id) for s in sources],
        cataloguing     = cataloguing,
    )


# ── Helpers ────────────────────────────────────────────────────────────────────

def _transform_source(raw: dict) -> SourceDocument:
    return SourceDocument(
        source_id       = raw.get(SourceFields.ID, "UNKNOWN"),
        source_type     = raw.get(SourceFields.DOCUMENT_TYPE),
        title           = raw.get(SourceFields.CITATION),
        url             = raw.get(SourceFields.URL),
        publication_date= raw.get(SourceFields.DOCUMENT_DATE),
        use_notes       = raw.get(SourceFields.NOTES),
    )


def _authority_status(f: dict, id_field: str, status_field: str | None = None) -> AuthorityStatus:
    """Determine AuthorityStatus from presence of ID and optional status field."""
    id_val = _str(f, id_field)
    if not id_val:
        return AuthorityStatus.SEARCH_NEEDED
    if status_field:
        raw = (_str(f, status_field) or "").lower()
        if "candidate" in raw:
            return AuthorityStatus.CANDIDATE
    return AuthorityStatus.CONFIRMED


def _str(record: dict, key: str) -> str | None:
    val = record.get(key)
    if val is None:
        return None
    s = str(val).strip()
    return s if s else None


def _int(record: dict, key: str) -> int | None:
    val = record.get(key)
    if val is None:
        return None
    try:
        return int(val)
    except (ValueError, TypeError):
        return None


def _semicolons(record: dict, key: str) -> list[str]:
    raw = _str(record, key)
    if not raw:
        return []
    return [item.strip() for item in raw.split(";") if item.strip()]


def _derive_sort_name(preferred_name: str) -> str:
    parts = preferred_name.strip().split()
    if len(parts) >= 2:
        return f"{parts[-1]}, {' '.join(parts[:-1])}"
    return preferred_name
