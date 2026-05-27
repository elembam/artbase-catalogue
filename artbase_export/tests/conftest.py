"""
tests/conftest.py

Shared fixtures for the artbase_export test suite.
All fixtures use the Airtable field names from artbase_export.airtable.schema
so they exercise the real transform path.
"""

import pytest


# ── Artist fixtures ────────────────────────────────────────────────────────────

@pytest.fixture()
def minimal_artist_row():
    """Absolute minimum: only a name and an ID."""
    return {
        "Artist ID":        "ART-0001",
        "Display Name":     "Jan de Heem",
        "Preferred Name":   "Jan de Heem",
        "_airtable_record_id": "recABCDEF001",
        "_sources":         [],
        "_authority_links": [],
    }


@pytest.fixture()
def full_artist_row():
    """Complete artist row matching the starter-kit schema."""
    return {
        "Artist ID":        "ART-HERBERTS-SILINS-1926",
        "Display Name":     "Herberts Siliņš",
        "Preferred Name":   "Herberts Siliņš",
        "Sort Name":        "Siliņš, Herberts",
        "Birth Year":       1926,
        "Death Year":       2001,
        "Birth Place":      "Aizupes pagasts, Latvia",
        "Death Place":      "Rīga, Latvia",
        "Nationality/Culture": "Latvian",
        "Roles":            "painter; graphic artist",
        "Wikidata QID":     "Q123456",
        "Wikidata URL":     "https://www.wikidata.org/wiki/Q123456",
        "Wikidata Status":  "matched_existing",
        "VIAF ID":          "72345678",
        "ULAN ID":          "500123456",
        "ULAN URI":         "http://vocab.getty.edu/ulan/500123456",
        "ISNI":             "0000 0001 1234 5678",
        "RKD Artist ID":    None,
        "Source URLs":      "https://lvnb.lv/silins; https://rkd.nl/silins",
        "Review Status":    "Draft",
        "Notes":            "Latvian modernist painter",
        "_airtable_record_id": "recHERBERTS001",
        "_sources": [
            {
                "Source Document ID":  "SRC-SILINS-LNB-001",
                "Document Type":       "catalogue",
                "Citation":            "Latvijas Nacionālā bibliotēka — Siliņš, Herberts",
                "Source URL":          "https://lvnb.lv/silins",
                "Document Date":       "2021-01-01",
                "Notes":               "Primary biographic source",
                "_airtable_record_id": "recSRC001",
            }
        ],
        "_authority_links": [],
    }


# ── Artwork fixtures ───────────────────────────────────────────────────────────

@pytest.fixture()
def minimal_artwork_row():
    """Minimum viable artwork row."""
    return {
        "Passport ID":          "AP-2026-000001",
        "Work Title":           "Still Life with Flowers",
        "_airtable_record_id":  "recARTWORK001",
        "_sources":             [],
        "_authority_links":     [],
    }


@pytest.fixture()
def full_artwork_row():
    """Complete artwork row with all Object ID fields."""
    return {
        "Passport ID":              "AP-2026-000001",
        "Work Title":               "Portrait of a Merchant",
        "Object Type Label":        "paintings",
        "AAT Object Type URI":      "http://vocab.getty.edu/aat/300033618",
        "Medium Display":           "oil on panel",
        "Dimensions Display":       "42 × 34 cm",
        "Height cm":                42.0,
        "Width cm":                 34.0,
        "Depth cm":                 None,
        "Inscriptions and Markings": "Signed lower right: J.d.H.",
        "Distinguishing Features":  "Pentimento visible under UV",
        "Subject Display":          "Half-length portrait of an unknown man",
        "ICONCLASS Codes":          "61B2; 31A45",
        "Date Display":             "c. 1650",
        "Date Start":               1645,
        "Date End":                 1655,
        "Artist ID":                "ART-0001",
        "Artist Display Name":      "Jan de Heem",
        "Repository / Collection":  "Private collection, Stockholm",
        "Current Location Display": "Stockholm",
        "Inventory Number":         "SC-2019-042",
        "Passport Visibility":      "Private",
        "Passport Status":          "Draft",
        "Catalogued By":            "cataloguer@artbase.eu",
        "Cataloguing Notes":        "Needs provenance research",
        "_airtable_record_id":      "recARTWORK999",
        "_sources":                 [],
        "_authority_links":         [],
    }
