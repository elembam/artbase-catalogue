"""
tests/test_json_writer.py

Tests for artbase_export.writers.json_writer.
Exercises write/re-read round-trips, unchanged detection, and _schema serialisation.
"""

import json
from pathlib import Path

import pytest

from artbase_export.canonical.models import (
    ArtistIdentity,
    CanonicalArtist,
    CanonicalArtwork,
    ObjectIDFields,
    Visibility,
)
from artbase_export.writers.json_writer import (
    _entity_dir,
    _file_path,
    _serialize,
    write_entities,
    write_entity,
)


# ── Helpers ────────────────────────────────────────────────────────────────────

def _make_artist(artbase_id: str = "ART-0001") -> CanonicalArtist:
    return CanonicalArtist(
        artbase_id  = artbase_id,
        identity    = ArtistIdentity(preferred_name="Test Artist"),
    )


def _make_artwork(artbase_id: str = "AP-2026-000001") -> CanonicalArtwork:
    return CanonicalArtwork(artbase_id=artbase_id)


# ── Directory routing ──────────────────────────────────────────────────────────

class TestEntityDir:
    def test_artist_goes_to_artists_subdir(self, tmp_path):
        artist = _make_artist()
        d = _entity_dir(artist, tmp_path)
        assert d == tmp_path / "artists"

    def test_artwork_goes_to_artworks_subdir(self, tmp_path):
        artwork = _make_artwork()
        d = _entity_dir(artwork, tmp_path)
        assert d == tmp_path / "artworks"


class TestFilePath:
    def test_artist_path(self, tmp_path):
        artist = _make_artist("ART-TEST")
        p = _file_path(artist, tmp_path)
        assert p == tmp_path / "artists" / "ART-TEST.json"

    def test_artwork_path(self, tmp_path):
        artwork = _make_artwork("AP-9999-000099")
        p = _file_path(artwork, tmp_path)
        assert p == tmp_path / "artworks" / "AP-9999-000099.json"


# ── Serialisation ─────────────────────────────────────────────────────────────

class TestSerialize:
    def test_output_is_valid_json(self):
        artist = _make_artist()
        out = _serialize(artist)
        parsed = json.loads(out)
        assert isinstance(parsed, dict)

    def test_schema_key_present(self):
        artist = _make_artist()
        out = _serialize(artist)
        parsed = json.loads(out)
        assert "_schema" in parsed
        assert "artist" in parsed["_schema"]

    def test_schema_key_present_for_artwork(self):
        artwork = _make_artwork()
        out = _serialize(artwork)
        parsed = json.loads(out)
        assert "_schema" in parsed
        assert "artwork" in parsed["_schema"]

    def test_unicode_preserved(self):
        artist = _make_artist()
        artist.identity.preferred_name = "Herberts Siliņš"  # Latvian ņ
        out = _serialize(artist)
        assert "Siliņš" in out

    def test_indented(self):
        artist = _make_artist()
        out = _serialize(artist)
        assert "\n" in out  # pretty-printed


# ── write_entity ──────────────────────────────────────────────────────────────

class TestWriteEntity:
    def test_creates_file(self, tmp_path):
        artist = _make_artist("ART-NEW")
        path, changed = write_entity(artist, tmp_path)
        assert path.exists()
        assert changed is True

    def test_creates_parent_dir(self, tmp_path):
        artist = _make_artist("ART-DIRTEST")
        path, _ = write_entity(artist, tmp_path)
        assert (tmp_path / "artists").is_dir()

    def test_written_file_is_valid_json(self, tmp_path):
        artist = _make_artist("ART-JSON")
        path, _ = write_entity(artist, tmp_path)
        parsed = json.loads(path.read_text(encoding="utf-8"))
        assert parsed["artbase_id"] == "ART-JSON"

    def test_unchanged_returns_false(self, tmp_path):
        artist = _make_artist("ART-DUP")
        write_entity(artist, tmp_path)

        # Write the *same* content — but we need identical exported timestamps.
        # Re-read and reconstruct from the file to guarantee same content.
        path, changed = write_entity(artist, tmp_path)

        # changed should be False only if content is identical.
        # Because `exported` is set to utcnow() on construction, two separate
        # CanonicalArtist instances will have different timestamps.
        # The second write with the *same object* will be unchanged.
        # To test this properly, we read back and re-construct.
        raw     = json.loads(path.read_text(encoding="utf-8"))
        artist2 = CanonicalArtist.model_validate(raw)

        # Patch the exported field to exactly the same value as on disk
        from artbase_export.writers.json_writer import _serialize
        content_on_disk = _serialize(artist2)
        path.write_text(content_on_disk, encoding="utf-8")
        _, changed2 = write_entity(artist2, tmp_path)
        assert changed2 is False

    def test_updated_returns_true_when_content_changes(self, tmp_path):
        artist = _make_artist("ART-UPDT")
        write_entity(artist, tmp_path)

        artist2 = _make_artist("ART-UPDT")
        artist2.identity.preferred_name = "Different Name"

        _, changed = write_entity(artist2, tmp_path)
        assert changed is True


# ── write_entities ─────────────────────────────────────────────────────────────

class TestWriteEntities:
    def test_empty_list(self, tmp_path):
        result = write_entities([], tmp_path)
        assert result["created"] == []
        assert result["updated"] == []
        assert result["unchanged"] == []

    def test_multiple_artists_created(self, tmp_path):
        artists = [_make_artist(f"ART-{i:04}") for i in range(3)]
        result = write_entities(artists, tmp_path)
        assert len(result["created"]) == 3
        assert result["updated"] == []

    def test_mix_of_artists_and_artworks(self, tmp_path):
        entities = [_make_artist("ART-0001"), _make_artwork("AP-0001")]
        result = write_entities(entities, tmp_path)
        assert len(result["created"]) == 2
        assert (tmp_path / "artists" / "ART-0001.json").exists()
        assert (tmp_path / "artworks" / "AP-0001.json").exists()

    def test_round_trip_preserves_data(self, tmp_path):
        artist = CanonicalArtist(
            artbase_id  = "ART-ROUND",
            identity    = ArtistIdentity(preferred_name="Round-trip Test"),
            visibility  = Visibility.PUBLIC,
        )
        write_entities([artist], tmp_path)

        path    = tmp_path / "artists" / "ART-ROUND.json"
        raw     = json.loads(path.read_text(encoding="utf-8"))
        loaded  = CanonicalArtist.model_validate(raw)

        assert loaded.artbase_id == "ART-ROUND"
        assert loaded.identity.preferred_name == "Round-trip Test"
        assert loaded.visibility is Visibility.PUBLIC
        assert loaded.version == 1
