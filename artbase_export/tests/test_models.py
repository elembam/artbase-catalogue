"""
tests/test_models.py

Unit tests for artbase_export.canonical.models.
Tests focus on model construction, validation, scoring, and enums.
"""

import pytest
from pydantic import ValidationError

from artbase_export.canonical.models import (
    AatTerm,
    ArtistAuthorityLinks,
    ArtistCataloguing,
    ArtistDescriptors,
    ArtistIdentity,
    ArtistLife,
    AuthorityLink,
    AuthorityStatus,
    CanonicalArtist,
    CanonicalArtwork,
    ConflictRecord,
    ConflictStatus,
    DateField,
    ObjectIDFields,
    PlaceField,
    ReviewStatus,
    SourceDocument,
    Visibility,
)


# ── Enum validation ────────────────────────────────────────────────────────────

class TestVisibility:
    def test_all_values_exist(self):
        assert Visibility.PRIVATE.value == "private"
        assert Visibility.UNLISTED.value == "unlisted"
        assert Visibility.PUBLIC_UNINDEXED.value == "public-unindexed"
        assert Visibility.PUBLIC.value == "public"

    def test_parse_from_string(self):
        assert Visibility("private") is Visibility.PRIVATE
        assert Visibility("public") is Visibility.PUBLIC


class TestReviewStatus:
    def test_all_values_exist(self):
        assert ReviewStatus.DRAFT.value == "draft"
        assert ReviewStatus.REVIEW.value == "review"
        assert ReviewStatus.PUBLISHED.value == "published"
        assert ReviewStatus.ARCHIVED.value == "archived"


class TestAuthorityStatus:
    def test_confirmed(self):
        assert AuthorityStatus.CONFIRMED.value == "confirmed"

    def test_search_needed(self):
        assert AuthorityStatus.SEARCH_NEEDED.value == "search_needed"


# ── DateField ─────────────────────────────────────────────────────────────────

class TestDateField:
    def test_defaults_are_none(self):
        d = DateField()
        assert d.value is None
        assert d.precision is None
        assert d.status == "working"
        assert d.source_ids == []

    def test_with_value(self):
        d = DateField(value="1926", precision="year")
        assert d.value == "1926"
        assert d.precision == "year"


# ── PlaceField ────────────────────────────────────────────────────────────────

class TestPlaceField:
    def test_empty(self):
        p = PlaceField()
        assert p.display is None
        assert p.tgn_uri is None

    def test_with_display(self):
        p = PlaceField(display="Amsterdam", wikidata_qid="Q727")
        assert p.display == "Amsterdam"
        assert p.wikidata_qid == "Q727"


# ── AatTerm ───────────────────────────────────────────────────────────────────

class TestAatTerm:
    def test_construction(self):
        t = AatTerm(label="paintings", uri="http://vocab.getty.edu/aat/300033618")
        assert t.label == "paintings"
        assert "aat" in t.uri


# ── AuthorityLink ─────────────────────────────────────────────────────────────

class TestAuthorityLink:
    def test_defaults(self):
        a = AuthorityLink()
        assert a.id is None
        assert a.status is AuthorityStatus.SEARCH_NEEDED

    def test_confirmed(self):
        a = AuthorityLink(id="Q123456", status=AuthorityStatus.CONFIRMED)
        assert a.status == AuthorityStatus.CONFIRMED


# ── ObjectIDFields ────────────────────────────────────────────────────────────

class TestObjectIDFields:
    def test_score_zero_when_empty(self):
        obj = ObjectIDFields()
        assert obj.score() == 0

    def test_score_all_nine(self):
        obj = ObjectIDFields(
            object_type         = "paintings",
            materials           = "oil on panel",
            dimensions_display  = "42 × 34 cm",
            inscriptions        = "Signed lower right",
            distinguishing      = "Pentimento visible",
            title               = "Portrait of a Merchant",
            subject             = "Half-length portrait",
            date_display        = "c. 1650",
            maker_id            = "ART-0001",
        )
        assert obj.score() == 9

    def test_score_partial(self):
        obj = ObjectIDFields(title="Untitled", materials="oil")
        assert obj.score() == 2

    def test_missing_categories_empty(self):
        obj = ObjectIDFields(
            object_type         = "paintings",
            materials           = "oil on panel",
            dimensions_display  = "42 × 34 cm",
            inscriptions        = "none",
            distinguishing      = "none",
            title               = "Portrait",
            subject             = "Portrait subject",
            date_display        = "c. 1650",
            maker_id            = "ART-0001",
        )
        assert obj.missing_categories() == []

    def test_missing_categories_lists_missing(self):
        obj = ObjectIDFields(title="Untitled")
        missing = obj.missing_categories()
        assert "type of object" in missing
        assert "materials and techniques" in missing
        assert "maker" in missing
        assert "title" not in missing  # title is present

    def test_dimensions_via_height_width(self):
        # height_cm + width_cm counts as dimensions even without display string
        obj = ObjectIDFields(
            object_type     = "paintings",
            height_cm       = 42.0,
            width_cm        = 34.0,
            materials       = "oil",
            inscriptions    = "none",
            distinguishing  = "none",
            title           = "T",
            subject         = "S",
            date_display    = "1650",
            maker_id        = "ART-001",
        )
        assert obj.score() == 9


# ── SourceDocument ────────────────────────────────────────────────────────────

class TestSourceDocument:
    def test_minimal(self):
        s = SourceDocument(source_id="SRC-001")
        assert s.source_id == "SRC-001"
        assert s.title is None

    def test_full(self):
        s = SourceDocument(
            source_id   = "SRC-001",
            source_type = "monograph",
            title       = "A Book",
            url         = "https://example.com",
        )
        assert s.source_type == "monograph"


# ── ConflictRecord ────────────────────────────────────────────────────────────

class TestConflictRecord:
    def test_defaults_to_unresolved(self):
        c = ConflictRecord(
            field="life.birth_date",
            values=[{"value": "1926-08-28", "source_id": "SRC-001"}],
        )
        assert c.status is ConflictStatus.UNRESOLVED
        assert c.created  # auto-populated


# ── CanonicalArtist ───────────────────────────────────────────────────────────

class TestCanonicalArtist:
    def _make(self, **kwargs):
        defaults = dict(
            artbase_id  = "ART-0001",
            identity    = ArtistIdentity(preferred_name="Jan de Heem"),
        )
        defaults.update(kwargs)
        return CanonicalArtist(**defaults)

    def test_minimal_construction(self):
        a = self._make()
        assert a.artbase_id == "ART-0001"
        assert a.identity.preferred_name == "Jan de Heem"
        assert a.visibility is Visibility.PRIVATE
        assert a.version == 1

    def test_artbase_id_required(self):
        with pytest.raises(ValidationError):
            CanonicalArtist(
                artbase_id = "",
                identity   = ArtistIdentity(preferred_name="Test"),
            )

    def test_artbase_id_stripped(self):
        a = self._make(artbase_id="  ART-0002  ")
        assert a.artbase_id == "ART-0002"

    def test_exported_is_set_automatically(self):
        a = self._make()
        assert a.exported.endswith("Z")

    def test_object_id_score_method(self):
        a = self._make(
            descriptors = ArtistDescriptors(
                occupations = ["painter"],
                nationality = "Dutch",
                biography_summary = "17th-century Flemish painter.",
                media = ["oil on panel"],
            ),
            life = ArtistLife(
                birth_date  = DateField(value="1606", precision="year"),
                birth_place = PlaceField(display="Antwerp"),
            ),
        )
        score = a.object_id_score()
        assert score >= 5

    def test_is_export_ready_false_when_empty(self):
        a = self._make()
        assert a.is_export_ready() is False

    def test_is_export_ready_true(self):
        a = self._make(
            identity    = ArtistIdentity(preferred_name="Jan de Heem"),
            life        = ArtistLife(birth_date=DateField(value="1606")),
            descriptors = ArtistDescriptors(occupations=["painter"]),
        )
        assert a.is_export_ready() is True


# ── CanonicalArtwork ──────────────────────────────────────────────────────────

class TestCanonicalArtwork:
    def _make(self, **kwargs):
        defaults = dict(artbase_id="AP-2026-000001")
        defaults.update(kwargs)
        return CanonicalArtwork(**defaults)

    def test_minimal_construction(self):
        aw = self._make()
        assert aw.artbase_id == "AP-2026-000001"
        assert aw.visibility is Visibility.PRIVATE
        assert aw.object_id.score() == 0

    def test_artbase_id_required(self):
        with pytest.raises(ValidationError):
            CanonicalArtwork(artbase_id="")

    def test_is_export_ready_false(self):
        aw = self._make()
        assert aw.is_export_ready() is False

    def test_is_export_ready_true_at_7(self):
        aw = self._make(
            object_id = ObjectIDFields(
                object_type     = "paintings",
                materials       = "oil on panel",
                dimensions_display = "42 × 34 cm",
                inscriptions    = "none",
                distinguishing  = "none",
                title           = "Portrait",
                subject         = "Portrait subject",
            )
        )
        assert aw.object_id.score() == 7
        assert aw.is_export_ready() is True
