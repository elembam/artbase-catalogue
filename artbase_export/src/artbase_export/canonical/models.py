"""
artbase_export/canonical/models.py

Pydantic v2 models for the canonical ArtBase JSON format.

These models are the schema for everything written to data/.
They're also the input specification for the passport generator
and the LIDO pipeline.

Design notes:
- All fields have sensible defaults (None / [] / {}) so partial records
  can be written without validation errors.
- Required fields only exist at the top of the hierarchy — these are
  the things that truly must be present before any public use.
- The `conflicts` list makes data quality explicit in the record itself.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


# ── Controlled vocabularies ────────────────────────────────────────────────────

class Visibility(str, Enum):
    PRIVATE             = "private"
    UNLISTED            = "unlisted"
    PUBLIC_UNINDEXED    = "public-unindexed"
    PUBLIC              = "public"

class ReviewStatus(str, Enum):
    DRAFT       = "draft"
    REVIEW      = "review"
    PUBLISHED   = "published"
    ARCHIVED    = "archived"

class AuthorityStatus(str, Enum):
    CONFIRMED           = "confirmed"
    CANDIDATE           = "candidate_verify"
    SEARCH_NEEDED       = "search_needed"
    NOT_FOUND           = "not_found"
    NOT_APPLICABLE      = "not_applicable"

class ConflictStatus(str, Enum):
    UNRESOLVED  = "unresolved"
    RESOLVED    = "resolved"
    DEFERRED    = "deferred"


# ── Shared sub-models ──────────────────────────────────────────────────────────

class DateField(BaseModel):
    """A date with explicit precision and status — handles partial dates and conflicts."""
    value:          Optional[str]   = None  # ISO 8601: 1926-08-28, 1926-08, 1926
    precision:      Optional[str]   = None  # day / month / year / decade / century
    status:         str             = "working"
    source_ids:     list[str]       = Field(default_factory=list)
    notes:          Optional[str]   = None


class PlaceField(BaseModel):
    """A place with display name and optional Getty TGN reference."""
    display:        Optional[str]   = None
    tgn_uri:        Optional[str]   = None
    wikidata_qid:   Optional[str]   = None
    source_ids:     list[str]       = Field(default_factory=list)


class AatTerm(BaseModel):
    """A Getty AAT controlled-vocabulary term."""
    label:  str
    uri:    str     # e.g. http://vocab.getty.edu/aat/300033618


class AuthorityLink(BaseModel):
    """A link from a canonical record to an external authority."""
    id:             Optional[str]           = None
    uri:            Optional[str]           = None
    status:         AuthorityStatus         = AuthorityStatus.SEARCH_NEEDED
    verified_date:  Optional[str]           = None
    notes:          Optional[str]           = None


class SourceReference(BaseModel):
    """A reference to a source document, by source ID."""
    source_id:      str
    role:           Optional[str]   = None  # biography / career / dimensions / etc.
    accessed:       Optional[str]   = None  # ISO date


class ConflictRecord(BaseModel):
    """An explicit data conflict, preserved in the record until resolved."""
    field:          str             # dot-notation path: life.birth_date
    values:         list[dict]      # [{"value": "1926-08-25", "source_id": "SRC-..."}]
    status:         ConflictStatus  = ConflictStatus.UNRESOLVED
    created:        str             = Field(default_factory=lambda: datetime.utcnow().date().isoformat())
    resolved_by:    Optional[str]   = None
    resolution:     Optional[str]   = None


class SourceDocument(BaseModel):
    """A full source document record, embedded in the canonical JSON."""
    source_id:          str
    source_type:        Optional[str]   = None
    title:              Optional[str]   = None
    publisher:          Optional[str]   = None
    url:                Optional[str]   = None
    publication_date:   Optional[str]   = None
    access_date:        Optional[str]   = None
    use_notes:          Optional[str]   = None
    license:            Optional[str]   = None


# ── Artist canonical model ─────────────────────────────────────────────────────

class ArtistIdentity(BaseModel):
    preferred_name:         str                         # always required
    preferred_name_language:Optional[str]   = None      # ISO 639-1: lv, en, sv
    full_name:              Optional[str]   = None
    name_variants:          list[str]       = Field(default_factory=list)
    sort_name:              Optional[str]   = None      # Siliņš, Herberts


class ArtistLife(BaseModel):
    birth_date:     DateField   = Field(default_factory=DateField)
    death_date:     DateField   = Field(default_factory=DateField)
    birth_place:    PlaceField  = Field(default_factory=PlaceField)
    death_place:    PlaceField  = Field(default_factory=PlaceField)


class ArtistDescriptors(BaseModel):
    nationality:        Optional[str]   = None
    citizenship:        list[str]       = Field(default_factory=list)
    occupations:        list[str]       = Field(default_factory=list)    # painter / sculptor / etc.
    occupations_aat:    list[AatTerm]   = Field(default_factory=list)
    media:              list[str]       = Field(default_factory=list)
    subjects:           list[str]       = Field(default_factory=list)
    movement_notes:     Optional[str]   = None
    biography_summary:  Optional[str]   = None


class ArtistAuthorityLinks(BaseModel):
    wikidata:   AuthorityLink   = Field(default_factory=AuthorityLink)
    viaf:       AuthorityLink   = Field(default_factory=AuthorityLink)
    ulan:       AuthorityLink   = Field(default_factory=AuthorityLink)
    isni:       AuthorityLink   = Field(default_factory=AuthorityLink)
    rkd:        AuthorityLink   = Field(default_factory=AuthorityLink)
    lc_naco:    AuthorityLink   = Field(default_factory=AuthorityLink)
    gnd:        AuthorityLink   = Field(default_factory=AuthorityLink)
    bnf:        AuthorityLink   = Field(default_factory=AuthorityLink)
    libris:     AuthorityLink   = Field(default_factory=AuthorityLink)
    artbase_id: Optional[str]   = None                                   # AR + 8 base32


class ArtistCataloguing(BaseModel):
    review_status:  ReviewStatus    = ReviewStatus.DRAFT
    catalogued_by:  Optional[str]   = None
    notes:          Optional[str]   = None
    tasks:          list[str]       = Field(default_factory=list)
    engagement_ids: list[str]       = Field(default_factory=list)


class CanonicalArtist(BaseModel):
    """The complete canonical representation of an artist record."""

    # Envelope — always present
    _schema:        str     = "artbase:artist:v1"
    artbase_id:     str                         # the local Airtable-assigned ID
    airtable_id:    Optional[str]   = None      # the Airtable recXXXX
    artbase_canonical_id: Optional[str] = None  # AR + 8 base32, once generated
    version:        int             = 1
    created:        Optional[str]   = None
    exported:       str             = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    visibility:     Visibility      = Visibility.PRIVATE

    # Content
    identity:       ArtistIdentity
    life:           ArtistLife              = Field(default_factory=ArtistLife)
    descriptors:    ArtistDescriptors       = Field(default_factory=ArtistDescriptors)
    authority_links:ArtistAuthorityLinks    = Field(default_factory=ArtistAuthorityLinks)

    # Quality tracking
    sources:        list[SourceDocument]    = Field(default_factory=list)
    source_refs:    list[SourceReference]   = Field(default_factory=list)
    conflicts:      list[ConflictRecord]    = Field(default_factory=list)
    cataloguing:    ArtistCataloguing       = Field(default_factory=ArtistCataloguing)

    @field_validator("artbase_id")
    @classmethod
    def artbase_id_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("artbase_id is required and cannot be empty")
        return v.strip()

    def is_export_ready(self) -> bool:
        """Returns True if the record has the minimum for LIDO export."""
        return bool(
            self.identity.preferred_name
            and self.life.birth_date.value
            and self.descriptors.occupations
        )

    def object_id_score(self) -> int:
        """How many of the 9 Object ID categories are filled for artists (adapted)."""
        score = 0
        if self.descriptors.occupations: score += 1          # type of entity
        if self.descriptors.media: score += 1                # materials
        # artists don't have dimensions; we adapt remaining categories
        if self.identity.preferred_name: score += 1         # name
        if self.life.birth_date.value: score += 1           # date
        if self.life.birth_place.display: score += 1        # place
        if self.descriptors.nationality: score += 1         # nationality
        if self.descriptors.biography_summary: score += 1   # description
        if self.authority_links.wikidata.status.value in ("confirmed",): score += 1
        if self.sources: score += 1                         # documented
        return score


# ── Artwork canonical model ────────────────────────────────────────────────────

class ObjectIDFields(BaseModel):
    """The nine Object ID categories mapped to the artwork."""
    object_type:        Optional[str]           = None      # painting / sculpture / etc.
    object_type_aat:    Optional[AatTerm]       = None
    materials:          Optional[str]           = None      # display string
    materials_aat:      list[AatTerm]           = Field(default_factory=list)
    dimensions_display: Optional[str]           = None      # 81 × 81 cm
    height_cm:          Optional[float]         = None
    width_cm:           Optional[float]         = None
    depth_cm:           Optional[float]         = None
    inscriptions:       Optional[str]           = None
    distinguishing:     Optional[str]           = None
    title:              Optional[str]           = None
    subject:            Optional[str]           = None
    date_display:       Optional[str]           = None      # 1979 or c. 1965–1970
    date_earliest:      Optional[int]           = None
    date_latest:        Optional[int]           = None
    maker_id:           Optional[str]           = None      # references ArtBase artist ID
    has_photograph:     bool                    = False

    def score(self) -> int:
        """Count of Object ID categories populated (0–9)."""
        fields = [
            self.object_type, self.materials,
            self.dimensions_display or (self.height_cm and self.width_cm),
            self.inscriptions is not None,  # even "none" is a complete answer
            self.distinguishing is not None,
            self.title, self.subject, self.date_display, self.maker_id
        ]
        return sum(1 for f in fields if f)

    def missing_categories(self) -> list[str]:
        """Human-readable list of missing Object ID categories."""
        missing = []
        if not self.object_type:        missing.append("type of object")
        if not self.materials:          missing.append("materials and techniques")
        if not (self.dimensions_display or self.height_cm): missing.append("measurements")
        if self.inscriptions is None:   missing.append("inscriptions and markings")
        if self.distinguishing is None: missing.append("distinguishing features")
        if not self.title:              missing.append("title")
        if not self.subject:            missing.append("subject")
        if not self.date_display:       missing.append("date or period")
        if not self.maker_id:           missing.append("maker")
        return missing


class ArtworkIconography(BaseModel):
    iconclass_codes:    list[str]   = Field(default_factory=list)
    iconclass_labels:   list[str]   = Field(default_factory=list)
    depicts:            list[str]   = Field(default_factory=list)


class ArtworkLocation(BaseModel):
    collection:         Optional[str]   = None
    collection_qid:     Optional[str]   = None
    inventory_number:   Optional[str]   = None
    location_notes:     Optional[str]   = None


class ArtworkAuthorityLinks(BaseModel):
    wikidata:   AuthorityLink   = Field(default_factory=AuthorityLink)
    artbase_id: Optional[str]   = None   # AB + 8 base32


class CanonicalArtwork(BaseModel):
    """The complete canonical representation of an artwork record."""

    _schema:        str     = "artbase:artwork:v1"
    artbase_id:     str
    airtable_id:    Optional[str]   = None
    artbase_canonical_id: Optional[str] = None
    version:        int             = 1
    created:        Optional[str]   = None
    exported:       str             = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    visibility:     Visibility      = Visibility.PRIVATE

    object_id:      ObjectIDFields              = Field(default_factory=ObjectIDFields)
    iconography:    ArtworkIconography          = Field(default_factory=ArtworkIconography)
    location:       ArtworkLocation             = Field(default_factory=ArtworkLocation)
    provenance:     list[dict]                  = Field(default_factory=list)
    authority_links:ArtworkAuthorityLinks       = Field(default_factory=ArtworkAuthorityLinks)

    sources:        list[SourceDocument]        = Field(default_factory=list)
    source_refs:    list[SourceReference]       = Field(default_factory=list)
    conflicts:      list[ConflictRecord]        = Field(default_factory=list)
    cataloguing:    ArtistCataloguing           = Field(default_factory=ArtistCataloguing)

    def is_export_ready(self) -> bool:
        return self.object_id.score() >= 7

    @field_validator("artbase_id")
    @classmethod
    def artbase_id_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("artbase_id is required")
        return v.strip()
