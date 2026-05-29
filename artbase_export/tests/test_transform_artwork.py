"""
tests/test_transform_artwork.py

Tests for artbase_export.transform.artwork.transform_artwork().
"""

import pytest

from artbase_export.canonical.models import (
    CanonicalArtwork,
    ReviewStatus,
    Visibility,
)
from artbase_export.transform.artwork import transform_artwork


class TestTransformArtworkHappyPath:
    def test_returns_canonical_artwork(self, full_artwork_row):
        result = transform_artwork(full_artwork_row)
        assert isinstance(result, CanonicalArtwork)

    def test_artbase_id(self, full_artwork_row):
        result = transform_artwork(full_artwork_row)
        assert result.artbase_id == "AP-2026-000001"

    def test_airtable_id_set(self, full_artwork_row):
        result = transform_artwork(full_artwork_row)
        assert result.airtable_id == "recARTWORK999"


class TestTransformArtworkObjectIDFields:
    def test_title(self, full_artwork_row):
        result = transform_artwork(full_artwork_row)
        assert result.object_id.title == "Portrait of a Merchant"

    def test_object_type(self, full_artwork_row):
        result = transform_artwork(full_artwork_row)
        assert result.object_id.object_type == "paintings"

    def test_object_type_aat(self, full_artwork_row):
        result = transform_artwork(full_artwork_row)
        assert result.object_id.object_type_aat is not None
        assert result.object_id.object_type_aat.label == "paintings"
        assert "aat" in result.object_id.object_type_aat.uri

    def test_materials(self, full_artwork_row):
        result = transform_artwork(full_artwork_row)
        assert result.object_id.materials == "oil on panel"

    def test_dimensions_display(self, full_artwork_row):
        result = transform_artwork(full_artwork_row)
        assert result.object_id.dimensions_display == "42 × 34 cm"

    def test_dimensions_cm(self, full_artwork_row):
        result = transform_artwork(full_artwork_row)
        assert result.object_id.height_cm == 42.0
        assert result.object_id.width_cm == 34.0
        assert result.object_id.depth_cm is None

    def test_inscriptions(self, full_artwork_row):
        result = transform_artwork(full_artwork_row)
        assert "Signed" in result.object_id.inscriptions

    def test_distinguishing(self, full_artwork_row):
        result = transform_artwork(full_artwork_row)
        assert "Pentimento" in result.object_id.distinguishing

    def test_subject(self, full_artwork_row):
        result = transform_artwork(full_artwork_row)
        assert "portrait" in result.object_id.subject.lower()

    def test_date_display(self, full_artwork_row):
        result = transform_artwork(full_artwork_row)
        assert result.object_id.date_display == "c. 1650"

    def test_date_range(self, full_artwork_row):
        result = transform_artwork(full_artwork_row)
        assert result.object_id.date_earliest == 1645
        assert result.object_id.date_latest == 1655

    def test_maker_id(self, full_artwork_row):
        result = transform_artwork(full_artwork_row)
        assert result.object_id.maker_id == "ART-0001"

    def test_object_id_score_nine(self, full_artwork_row):
        result = transform_artwork(full_artwork_row)
        assert result.object_id.score() == 9


class TestTransformArtworkIconography:
    def test_iconclass_codes_split(self, full_artwork_row):
        result = transform_artwork(full_artwork_row)
        assert "61B2" in result.iconography.iconclass_codes
        assert "31A45" in result.iconography.iconclass_codes

    def test_iconclass_empty_when_absent(self, minimal_artwork_row):
        result = transform_artwork(minimal_artwork_row)
        assert result.iconography.iconclass_codes == []


class TestTransformArtworkLocation:
    def test_collection(self, full_artwork_row):
        result = transform_artwork(full_artwork_row)
        assert "Stockholm" in result.location.collection

    def test_inventory_number(self, full_artwork_row):
        result = transform_artwork(full_artwork_row)
        assert result.location.inventory_number == "SC-2019-042"

    def test_location_notes(self, full_artwork_row):
        result = transform_artwork(full_artwork_row)
        assert result.location.location_notes is not None


class TestTransformArtworkVisibility:
    def test_private_default(self, full_artwork_row):
        result = transform_artwork(full_artwork_row)
        assert result.visibility is Visibility.PRIVATE

    def test_public_mapped_correctly(self, full_artwork_row):
        full_artwork_row["Passport Visibility"] = "public"
        result = transform_artwork(full_artwork_row)
        assert result.visibility is Visibility.PUBLIC

    def test_unknown_visibility_falls_back_to_private(self, full_artwork_row):
        full_artwork_row["Passport Visibility"] = "???unknown???"
        result = transform_artwork(full_artwork_row)
        assert result.visibility is Visibility.PRIVATE


class TestTransformArtworkCataloguing:
    def test_catalogued_by(self, full_artwork_row):
        result = transform_artwork(full_artwork_row)
        assert result.cataloguing.catalogued_by == "cataloguer@arsaccordia.com"

    def test_review_status_draft(self, full_artwork_row):
        result = transform_artwork(full_artwork_row)
        assert result.cataloguing.review_status is ReviewStatus.DRAFT

    def test_review_status_unknown_fallback(self, full_artwork_row):
        full_artwork_row["Passport Status"] = "Bogus"
        result = transform_artwork(full_artwork_row)
        assert result.cataloguing.review_status is ReviewStatus.DRAFT


class TestTransformArtworkEdgeCases:
    def test_missing_passport_id_raises(self):
        row = {"Work Title": "Test", "_sources": [], "_authority_links": []}
        with pytest.raises(ValueError, match="Passport ID"):
            transform_artwork(row)

    def test_minimal_row_succeeds(self, minimal_artwork_row):
        result = transform_artwork(minimal_artwork_row)
        assert result.artbase_id == "AP-2026-000001"
        assert result.object_id.score() == 1  # only title
