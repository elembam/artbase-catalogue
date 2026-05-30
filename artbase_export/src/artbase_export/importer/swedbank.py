"""
artbase_export/importer/swedbank.py

Hansabanka / Swedbank-specific parsing and Airtable field mapping.
Source: swedbank.html  (386 records, headers: id, page, catalogue_no, artist,
        title_lv, title_en, year, medium_raw, dimensions_cm, notes)
"""

from __future__ import annotations

from pathlib import Path

from artbase_export.airtable.schema import (
    ArtistFields, ArtworkFields, CollectionFields,
    PassportStatus, ReviewStatus, Visibility, WikidataStatus,
)
from artbase_export.importer.base import (
    extract_medium_en,
    parse_html_table,
    parse_swedbank_dimensions,
    parse_year,
    sort_name,
)

# ── Collection identity ────────────────────────────────────────────────────────

CLIENT_CODE   = "SWB"
AA_ID_PREFIX  = "AA/LV/SWB/"
SOURCE_SYSTEM = "Hansabanka / Swedbank catalogue OCR"

COLLECTION_RECORD: dict = {
    CollectionFields.CLIENT_CODE:     CLIENT_CODE,
    CollectionFields.CLIENT_NAME:     "Swedbank Latvia (formerly Hansabanka)",
    CollectionFields.COLLECTION_NAME: "Hansabanka Contemporary Art Collection",
    CollectionFields.COLLECTION_TYPE: "Corporate",
    CollectionFields.DEFAULT_LANGUAGE:"lv",
    CollectionFields.DEFAULT_RIGHTS:  "Swedbank Latvia",
    CollectionFields.PRIVACY_DEFAULT: "private",
    CollectionFields.NOTES: (
        "Imported from catalogue pages 222–229 via swedbank.html OCR export. "
        "No artist lifespan data in source — birth/death years to be added "
        "after Wikidata reconciliation (Phase 1)."
    ),
}


# ── Parsing ────────────────────────────────────────────────────────────────────

def parse_rows(html_path: Path) -> list[dict[str, str]]:
    """Return all 386 Swedbank rows as a list of header-keyed dicts."""
    return parse_html_table(html_path)


# ── Field builders ─────────────────────────────────────────────────────────────

def build_artist_fields(name: str) -> dict:
    """
    Build an Artists_Makers field dict for a Swedbank artist.
    No lifespan data is present in the source — birth/death years will be
    populated later during Wikidata reconciliation (Phase 1).
    """
    return {
        ArtistFields.DISPLAY_NAME:    name,
        ArtistFields.PREFERRED_NAME:  name,
        ArtistFields.SORT_NAME:       sort_name(name),
        ArtistFields.NATIONALITY:     "Latvian",
        ArtistFields.WIKIDATA_STATUS: WikidataStatus.CANDIDATE,
        ArtistFields.REVIEW_STATUS:   ReviewStatus.DRAFT,
        ArtistFields.NOTES: (
            "Imported from Hansabanka/Swedbank catalogue. "
            "No lifespan in source — add birth/death years after Phase 1 reconciliation."
        ),
    }


def build_artwork_fields(
    row: dict[str, str],
    artist_rec_id: str | None,
    collection_rec_id: str,   # reserved — Collection ID field is read-only in this base
    passport_id: str,
) -> dict:
    """Map one Swedbank row to an Artworks Airtable field dict."""
    h, w = parse_swedbank_dimensions(row.get("dimensions_cm", ""))
    date_disp, date_start, date_end = parse_year(row.get("year", ""))

    medium_raw = row.get("medium_raw", "").strip()
    medium_en  = extract_medium_en(medium_raw)
    title_en   = row.get("title_en", "").strip()
    title_lv   = row.get("title_lv", "").strip()
    cat_no     = row.get("catalogue_no", "").strip()
    src_notes  = row.get("notes", "").strip()
    page       = row.get("page", "").strip()

    notes_parts = [f"Catalogue page: {page}", f"Raw medium: {medium_raw}"]
    if src_notes:
        notes_parts.append(src_notes)

    # All fields except Artist are singleLineText — numeric values must be strings.
    fields: dict = {
        ArtworkFields.PASSPORT_ID:        passport_id,
        ArtworkFields.SOURCE_SYSTEM:      SOURCE_SYSTEM,
        ArtworkFields.SOURCE_RECORD_ID:   row.get("id", "").strip(),
        ArtworkFields.CLIENT_CODE:        CLIENT_CODE,
        ArtworkFields.COLLECTION_ID:      CLIENT_CODE,      # text field, not linked record
        ArtworkFields.INVENTORY_NUMBER:   cat_no,
        ArtworkFields.WORK_TITLE:         title_en or title_lv,
        ArtworkFields.ALTERNATE_TITLES:   title_lv if title_en else "",
        ArtworkFields.ARTIST_DISPLAY:     row.get("artist", "").strip(),
        ArtworkFields.DATE_DISPLAY:       date_disp,
        ArtworkFields.DATE_START:         str(date_start) if date_start else "",
        ArtworkFields.DATE_END:           str(date_end)   if date_end   else "",
        ArtworkFields.MEDIUM_DISPLAY:     medium_en,
        ArtworkFields.DIMENSIONS_DISPLAY: row.get("dimensions_cm", "").strip(),
        ArtworkFields.HEIGHT_CM:          str(h) if h is not None else "",
        ArtworkFields.WIDTH_CM:           str(w) if w is not None else "",
        ArtworkFields.REPOSITORY:         "Swedbank Latvia (formerly Hansabanka)",
        ArtworkFields.STATUS:             PassportStatus.DRAFT,
        ArtworkFields.VISIBILITY:         Visibility.PRIVATE,
        ArtworkFields.NOTES:              "\n".join(notes_parts),
    }

    if artist_rec_id:
        fields[ArtworkFields.ARTIST] = [artist_rec_id]

    return {k: v for k, v in fields.items() if v != "" and v != [] and v is not None}
