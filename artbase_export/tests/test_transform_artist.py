"""
tests/test_transform_artist.py

Tests for artbase_export.transform.artist.transform_artist().
"""

import pytest

from artbase_export.canonical.models import (
    AuthorityStatus,
    CanonicalArtist,
    ReviewStatus,
    Visibility,
)
from artbase_export.transform.artist import transform_artist


class TestTransformArtistHappyPath:
    def test_returns_canonical_artist(self, full_artist_row):
        result = transform_artist(full_artist_row)
        assert isinstance(result, CanonicalArtist)

    def test_artbase_id_set(self, full_artist_row):
        result = transform_artist(full_artist_row)
        assert result.artbase_id == "ART-HERBERTS-SILINS-1926"

    def test_airtable_id_set(self, full_artist_row):
        result = transform_artist(full_artist_row)
        assert result.airtable_id == "recHERBERTS001"

    def test_preferred_name(self, full_artist_row):
        result = transform_artist(full_artist_row)
        assert result.identity.preferred_name == "Herberts Siliņš"

    def test_sort_name(self, full_artist_row):
        result = transform_artist(full_artist_row)
        assert result.identity.sort_name == "Siliņš, Herberts"

    def test_birth_year_as_string(self, full_artist_row):
        result = transform_artist(full_artist_row)
        assert result.life.birth_date.value == "1926"
        assert result.life.birth_date.precision == "year"

    def test_death_year_as_string(self, full_artist_row):
        result = transform_artist(full_artist_row)
        assert result.life.death_date.value == "2001"

    def test_birth_place(self, full_artist_row):
        result = transform_artist(full_artist_row)
        assert "Latvia" in result.life.birth_place.display

    def test_nationality(self, full_artist_row):
        result = transform_artist(full_artist_row)
        assert result.descriptors.nationality == "Latvian"

    def test_occupations_split_on_semicolons(self, full_artist_row):
        result = transform_artist(full_artist_row)
        assert "painter" in result.descriptors.occupations
        assert "graphic artist" in result.descriptors.occupations

    def test_visibility_defaults_to_private(self, full_artist_row):
        result = transform_artist(full_artist_row)
        assert result.visibility is Visibility.PRIVATE

    def test_review_status_draft(self, full_artist_row):
        result = transform_artist(full_artist_row)
        assert result.cataloguing.review_status is ReviewStatus.DRAFT

    def test_notes_preserved(self, full_artist_row):
        result = transform_artist(full_artist_row)
        assert "Latvian" in result.cataloguing.notes


class TestTransformArtistAuthorityLinks:
    def test_wikidata_confirmed(self, full_artist_row):
        result = transform_artist(full_artist_row)
        assert result.authority_links.wikidata.id == "Q123456"
        assert result.authority_links.wikidata.status is AuthorityStatus.CONFIRMED

    def test_viaf_confirmed_when_present(self, full_artist_row):
        result = transform_artist(full_artist_row)
        assert result.authority_links.viaf.id == "72345678"
        assert result.authority_links.viaf.status is AuthorityStatus.CONFIRMED

    def test_ulan_confirmed_when_present(self, full_artist_row):
        result = transform_artist(full_artist_row)
        assert result.authority_links.ulan.id == "500123456"
        assert result.authority_links.ulan.uri == "http://vocab.getty.edu/ulan/500123456"

    def test_rkd_search_needed_when_absent(self, full_artist_row):
        result = transform_artist(full_artist_row)
        assert result.authority_links.rkd.status is AuthorityStatus.SEARCH_NEEDED

    def test_missing_wikidata_sets_search_needed(self, minimal_artist_row):
        result = transform_artist(minimal_artist_row)
        assert result.authority_links.wikidata.status is AuthorityStatus.SEARCH_NEEDED


class TestTransformArtistSources:
    def test_linked_source_transformed(self, full_artist_row):
        result = transform_artist(full_artist_row)
        assert len(result.sources) >= 1
        src = result.sources[0]
        assert src.source_id == "SRC-SILINS-LNB-001"
        assert src.source_type == "catalogue"

    def test_inline_source_urls_parsed(self, full_artist_row):
        result = transform_artist(full_artist_row)
        # "Source URLs" has two semicolon-separated URLs.
        # The first (lvnb.lv/silins) is already present in _sources, so deduplication
        # skips it — only the second (rkd.nl/silins) is added as SRC-INLINE-*.
        inline = [s for s in result.sources if s.source_id.startswith("SRC-INLINE")]
        assert len(inline) == 1
        assert "rkd.nl" in inline[0].url

    def test_source_refs_match_sources(self, full_artist_row):
        result = transform_artist(full_artist_row)
        source_ids = {s.source_id for s in result.sources}
        ref_ids    = {r.source_id for r in result.source_refs}
        assert source_ids == ref_ids


class TestTransformArtistEdgeCases:
    def test_missing_name_raises(self):
        row = {
            "Artist ID": "ART-0001",
            "_sources": [],
            "_authority_links": [],
        }
        with pytest.raises(ValueError, match="no name"):
            transform_artist(row)

    def test_minimal_row_succeeds(self, minimal_artist_row):
        result = transform_artist(minimal_artist_row)
        assert result.artbase_id == "ART-0001"
        assert result.identity.preferred_name == "Jan de Heem"

    def test_sort_name_derived_when_absent(self, minimal_artist_row):
        # minimal_artist_row has no Sort Name field
        result = transform_artist(minimal_artist_row)
        # _derive_sort_name("Jan de Heem") → "Heem, Jan de"
        assert result.identity.sort_name == "Heem, Jan de"

    def test_birth_year_none_when_absent(self, minimal_artist_row):
        result = transform_artist(minimal_artist_row)
        assert result.life.birth_date.value is None

    def test_tasks_populated_for_missing_authorities(self, minimal_artist_row):
        result = transform_artist(minimal_artist_row)
        # no VIAF, no ULAN → tasks should mention them
        task_text = " ".join(result.cataloguing.tasks)
        assert "VIAF" in task_text
        assert "ULAN" in task_text

    def test_review_status_unknown_falls_back_to_draft(self, full_artist_row):
        full_artist_row["Review Status"] = "XyzUnknown"
        result = transform_artist(full_artist_row)
        assert result.cataloguing.review_status is ReviewStatus.DRAFT

    def test_display_name_used_as_fallback(self):
        row = {
            "Artist ID":    "ART-0002",
            "Display Name": "Anonymous",
            "_sources":     [],
            "_authority_links": [],
        }
        result = transform_artist(row)
        assert result.identity.preferred_name == "Anonymous"
