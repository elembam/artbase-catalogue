"""
artbase_export/importer/lnma.py

LNMA-specific parsing and Airtable field mapping.
Source: lnmm.html  (354 records, headers: Title, Creator, Creator Lifespan,
        Date Created, Physical Dimensions, Type, Rights, Medium,
        Collection Name, Collection Number, URL, _sheet, _row_number)
"""

from __future__ import annotations

from pathlib import Path

from artbase_export.airtable.schema import (
    ArtistFields, ArtworkFields, CollectionFields,
    PassportStatus, ReviewStatus, Visibility, WikidataStatus,
)
from artbase_export.importer.base import (
    parse_html_table,
    parse_lifespan,
    parse_lnma_dimensions,
    parse_year,
    sort_name,
)

# ── Collection identity ────────────────────────────────────────────────────────

CLIENT_CODE   = "LNMA"
AA_ID_PREFIX  = "AA/LV/LNMA/"
SOURCE_SYSTEM = "LNMA / Google Arts & Culture"

COLLECTION_RECORD: dict = {
    CollectionFields.CLIENT_CODE:     CLIENT_CODE,
    CollectionFields.CLIENT_NAME:     "Latvian National Museum of Art",
    CollectionFields.COLLECTION_NAME: "LNMA Permanent Collection",
    CollectionFields.COLLECTION_TYPE: "Museum",
    CollectionFields.DEFAULT_LANGUAGE:"lv",
    CollectionFields.DEFAULT_RIGHTS:  "LNMA",
    CollectionFields.PRIVACY_DEFAULT: "private",
    CollectionFields.NOTES: (
        "Imported from LNMA_Latvia_National_Museum_Artworks.xlsx "
        "via lnmm.html. Source: Google Arts & Culture scrape."
    ),
}


# ── Parsing ────────────────────────────────────────────────────────────────────

def parse_rows(html_path: Path) -> list[dict[str, str]]:
    """Return all 354 LNMA rows as a list of header-keyed dicts."""
    return parse_html_table(html_path)


# ── Field builders ─────────────────────────────────────────────────────────────

def build_artist_fields(row: dict[str, str]) -> dict:
    """
    Map one LNMA artwork row to an Artists_Makers field dict.
    Birth/death years are parsed from the 'Creator Lifespan' column.
    """
    name     = row.get("Creator", "").strip()
    lifespan = row.get("Creator Lifespan", "").strip()
    birth, death = parse_lifespan(lifespan)

    # Birth Year / Death Year are read-only formula/lookup fields in this base.
    # Lifespan is preserved in Notes for manual entry or later update.
    return {
        ArtistFields.DISPLAY_NAME:    name,
        ArtistFields.PREFERRED_NAME:  name,
        ArtistFields.SORT_NAME:       sort_name(name),
        ArtistFields.NATIONALITY:     "Latvian",
        ArtistFields.WIKIDATA_STATUS: WikidataStatus.CANDIDATE,
        ArtistFields.REVIEW_STATUS:   ReviewStatus.DRAFT,
        ArtistFields.NOTES:           f"Lifespan: {lifespan}" if lifespan else "",
    }


def build_artwork_fields(
    row: dict[str, str],
    artist_rec_id: str | None,
    collection_rec_id: str,   # reserved — Collection ID field is read-only in this base
    passport_id: str,
) -> dict:
    """Map one LNMA artwork row to an Artworks Airtable field dict."""
    h, w = parse_lnma_dimensions(row.get("Physical Dimensions", ""))
    date_disp, date_start, date_end = parse_year(row.get("Date Created", ""))

    inventory = row.get("Collection Number", "").strip()
    title     = row.get("Title", "").strip()
    medium    = row.get("Medium", "").strip()
    obj_type  = row.get("Type", "").strip()
    rights    = row.get("Rights", "").strip()
    col_name  = row.get("Collection Name", "").strip()
    url       = row.get("URL", "").strip()

    notes_parts = []
    if col_name:
        notes_parts.append(f"Sub-collection: {col_name}")
    if url:
        notes_parts.append(f"Google Arts: {url}")

    # All fields except Artist are singleLineText — numeric values must be strings.
    fields: dict = {
        ArtworkFields.PASSPORT_ID:        passport_id,
        ArtworkFields.SOURCE_SYSTEM:      SOURCE_SYSTEM,
        ArtworkFields.SOURCE_RECORD_ID:   inventory,
        ArtworkFields.CLIENT_CODE:        CLIENT_CODE,
        ArtworkFields.COLLECTION_ID:      CLIENT_CODE,      # text field, not linked record
        ArtworkFields.INVENTORY_NUMBER:   inventory,
        ArtworkFields.WORK_TITLE:         title,
        ArtworkFields.ARTIST_DISPLAY:     row.get("Creator", "").strip(),
        ArtworkFields.DATE_DISPLAY:       date_disp,
        ArtworkFields.DATE_START:         str(date_start) if date_start else "",
        ArtworkFields.DATE_END:           str(date_end)   if date_end   else "",
        ArtworkFields.OBJECT_TYPE_LABEL:  obj_type,
        ArtworkFields.MEDIUM_DISPLAY:     medium,
        ArtworkFields.DIMENSIONS_DISPLAY: row.get("Physical Dimensions", "").strip(),
        ArtworkFields.HEIGHT_CM:          str(h) if h is not None else "",
        ArtworkFields.WIDTH_CM:           str(w) if w is not None else "",
        ArtworkFields.REPOSITORY:         "Latvian National Museum of Art",
        ArtworkFields.RIGHTS_STATEMENT:   rights,
        ArtworkFields.STATUS:             PassportStatus.DRAFT,
        ArtworkFields.VISIBILITY:         Visibility.PRIVATE,
        ArtworkFields.NOTES:              "\n".join(notes_parts),
    }

    if artist_rec_id:
        fields[ArtworkFields.ARTIST] = [artist_rec_id]

    return {k: v for k, v in fields.items() if v != "" and v != [] and v is not None}
