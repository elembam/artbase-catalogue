"""
artbase_export/transform/artwork.py

Transforms an Airtable Artworks record into a CanonicalArtwork.
Field names match the artwork_passport_airtable_starter_kit exactly.
"""

from __future__ import annotations
import logging
from typing import Any

from artbase_export.airtable.schema import ArtworkFields, SourceFields
from artbase_export.canonical.models import (
    ArtistCataloguing, ArtworkAuthorityLinks, ArtworkIconography,
    ArtworkLocation, CanonicalArtwork, ConflictRecord,
    ObjectIDFields, ReviewStatus, SourceDocument, SourceReference,
    Visibility,
)

logger = logging.getLogger(__name__)


def transform_artwork(raw: dict[str, Any]) -> CanonicalArtwork:
    """
    Convert an enriched Airtable Artworks record to CanonicalArtwork.
    raw comes from AirtableClient.iter_artworks().
    """
    f = raw

    passport_id = _str(f, ArtworkFields.PASSPORT_ID)
    if not passport_id:
        raise ValueError("Artwork record has no Passport ID")

    # ── Object ID fields ─────────────────────────────────────────────────────
    object_id = ObjectIDFields(
        title               = _str(f, ArtworkFields.WORK_TITLE),
        object_type         = _str(f, ArtworkFields.OBJECT_TYPE_LABEL),
        object_type_aat     = _aat(f, ArtworkFields.OBJECT_TYPE_LABEL, ArtworkFields.AAT_OBJECT_TYPE_URI),
        materials           = _str(f, ArtworkFields.MEDIUM_DISPLAY),
        dimensions_display  = _str(f, ArtworkFields.DIMENSIONS_DISPLAY),
        height_cm           = _float(f, ArtworkFields.HEIGHT_CM),
        width_cm            = _float(f, ArtworkFields.WIDTH_CM),
        depth_cm            = _float(f, ArtworkFields.DEPTH_CM),
        inscriptions        = _str(f, ArtworkFields.INSCRIPTIONS),
        distinguishing      = _str(f, ArtworkFields.DISTINGUISHING),
        subject             = _str(f, ArtworkFields.SUBJECT_DISPLAY),
        date_display        = _str(f, ArtworkFields.DATE_DISPLAY),
        date_earliest       = _int(f, ArtworkFields.DATE_START),
        date_latest         = _int(f, ArtworkFields.DATE_END),
        maker_id            = _str(f, ArtworkFields.ARTIST_ID),
        maker_display_name  = _str(f, ArtworkFields.ARTIST_DISPLAY),
    )

    # ── Iconography ──────────────────────────────────────────────────────────
    iconography = ArtworkIconography(
        iconclass_codes = _semicolons(f, ArtworkFields.ICONCLASS_CODES),
    )

    # ── Location ─────────────────────────────────────────────────────────────
    location = ArtworkLocation(
        collection          = _str(f, ArtworkFields.REPOSITORY),
        inventory_number    = _str(f, ArtworkFields.INVENTORY_NUMBER),
        location_notes      = _str(f, ArtworkFields.LOCATION_DISPLAY),
    )

    # ── Authority links ───────────────────────────────────────────────────────
    authority_links = ArtworkAuthorityLinks()

    # ── Sources ───────────────────────────────────────────────────────────────
    sources = [_transform_source(s) for s in f.get("_sources", [])]

    # ── Visibility ────────────────────────────────────────────────────────────
    vis_raw = _str(f, ArtworkFields.VISIBILITY) or "Private"
    try:
        visibility = Visibility(vis_raw.lower().replace(" — ", "-").replace(" ", "-"))
    except ValueError:
        visibility = Visibility.PRIVATE

    # ── Cataloguing ───────────────────────────────────────────────────────────
    status_raw = _str(f, ArtworkFields.STATUS) or "Draft"
    try:
        review_status = ReviewStatus(status_raw.lower())
    except ValueError:
        review_status = ReviewStatus.DRAFT

    cataloguing = ArtistCataloguing(
        review_status   = review_status,
        catalogued_by   = _str(f, ArtworkFields.CATALOGUED_BY),
        notes           = _str(f, ArtworkFields.NOTES),
    )

    return CanonicalArtwork(
        artbase_id      = passport_id,
        airtable_id     = f.get("_airtable_record_id"),
        visibility      = visibility,
        object_id       = object_id,
        iconography     = iconography,
        location        = location,
        authority_links = authority_links,
        sources         = sources,
        source_refs     = [SourceReference(source_id=s.source_id) for s in sources],
        cataloguing     = cataloguing,
    )


# ── Helpers ────────────────────────────────────────────────────────────────────

def _transform_source(raw: dict) -> SourceDocument:
    return SourceDocument(
        source_id   = raw.get(SourceFields.ID, "UNKNOWN"),
        source_type = raw.get(SourceFields.DOCUMENT_TYPE),
        title       = raw.get(SourceFields.CITATION),
        url         = raw.get(SourceFields.URL),
        use_notes   = raw.get(SourceFields.NOTES),
    )


def _aat(f: dict, label_key: str, uri_key: str):
    from artbase_export.canonical.models import AatTerm
    label = _str(f, label_key)
    uri   = _str(f, uri_key)
    if label and uri:
        return AatTerm(label=label, uri=uri)
    return None


def _str(record: dict, key: str) -> str | None:
    val = record.get(key)
    if val is None:
        return None
    s = str(val).strip()
    return s if s else None


def _int(record: dict, key: str) -> int | None:
    val = record.get(key)
    try:
        return int(val) if val is not None else None
    except (ValueError, TypeError):
        return None


def _float(record: dict, key: str) -> float | None:
    val = record.get(key)
    try:
        return float(val) if val is not None else None
    except (ValueError, TypeError):
        return None


def _semicolons(record: dict, key: str) -> list[str]:
    raw = _str(record, key)
    if not raw:
        return []
    return [item.strip() for item in raw.split(";") if item.strip()]
