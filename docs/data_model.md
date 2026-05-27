# ArtBase — Data Model

*Version 0.1 — covers the Airtable working layer and canonical JSON format.*

---

## Overview

ArtBase models art collections as a network of linked entities. The core entities are:

| Entity | Canonical ID prefix | Airtable table |
|---|---|---|
| **Artist / Maker** | `AR` (e.g. `AR9D2HK4Q8`) | `Artists_Makers` |
| **Artwork / Passport** | `AB` (e.g. `AB7F3KQ2X1`) | `Artworks` |
| **Collection** | `CO` (e.g. `CO3B7XJ5N1`) | `Collections` |
| **Provenance event** | — | `Provenance_Events` |
| **Source document** | `SRC-…` | `Source_Documents` |
| **Authority link** | — | `Authority_Links` |

During the Airtable working-layer phase, IDs use the human-readable format:
`ART-HERBERTS-SILINS-1926`, `AP-2026-000001`. Before any public deployment, these
migrate to the hash-based canonical scheme (see `ARTBASE_ARCHITECTURE.md §3`).

---

## Entity: Artist / Maker

Represents any person or corporate body who created, contributed to, or is otherwise
associated with an artwork as its maker.

### Identity fields

| Field | Type | Notes |
|---|---|---|
| `artbase_id` | string | Local working ID (e.g. `ART-0001`) |
| `artbase_canonical_id` | string \| null | `AR` + 8 base32 chars — set at first publication |
| `identity.preferred_name` | string | **Required.** Scholarly preferred form |
| `identity.preferred_name_language` | ISO 639-1 | Language of preferred name (e.g. `lv`, `nl`) |
| `identity.full_name` | string \| null | Expanded form if different from preferred |
| `identity.name_variants` | list[string] | Alternate spellings, diacritics, transliterations |
| `identity.sort_name` | string \| null | Inverted: `Siliņš, Herberts` |

### Life dates and places

| Field | Type | Notes |
|---|---|---|
| `life.birth_date.value` | ISO 8601 string | Year (`1926`), month (`1926-08`), or day (`1926-08-28`) |
| `life.birth_date.precision` | `year` \| `month` \| `day` \| `decade` \| `century` | |
| `life.birth_date.status` | string | `working`, `conflict`, `verified` |
| `life.birth_date.source_ids` | list[string] | Source document IDs supporting this value |
| `life.death_date.*` | same structure | |
| `life.birth_place.display` | string | Free-text display (e.g. `Antwerp, Spanish Netherlands`) |
| `life.birth_place.tgn_uri` | URI \| null | Getty TGN term URI |
| `life.birth_place.wikidata_qid` | string \| null | Wikidata Q-number |
| `life.death_place.*` | same structure | |

### Descriptors

| Field | Type | Notes |
|---|---|---|
| `descriptors.nationality` | string | Free text (e.g. `Latvian`, `Dutch`) |
| `descriptors.citizenship` | list[string] | For multiple citizenships |
| `descriptors.occupations` | list[string] | Free text (e.g. `painter`, `graphic artist`) |
| `descriptors.occupations_aat` | list[AatTerm] | Getty AAT controlled terms |
| `descriptors.media` | list[string] | Media worked in (e.g. `oil`, `lithography`) |
| `descriptors.subjects` | list[string] | Subject specialisms |
| `descriptors.biography_summary` | string \| null | Short scholarly biography |

### Authority links

| Field | Getty ULAN? | Notes |
|---|---|---|
| `authority_links.wikidata.id` | Q-number | e.g. `Q123456` |
| `authority_links.viaf.id` | VIAF number | e.g. `72345678` |
| `authority_links.ulan.id` | ULAN number | e.g. `500123456` |
| `authority_links.ulan.uri` | ULAN URI | `http://vocab.getty.edu/ulan/500123456` |
| `authority_links.isni.id` | ISNI | 16-digit: `0000 0001 1234 5678` |
| `authority_links.rkd.id` | RKD ID | Dutch art research institute |
| `authority_links.lc_naco.id` | LC NACO | Library of Congress name authority |
| `authority_links.gnd.id` | GND | Deutsche Nationalbibliothek |
| `authority_links.bnf.id` | BnF | Bibliothèque nationale de France |
| `authority_links.libris.id` | LIBRIS | Swedish national library |

Each authority link has:
- `status`: `confirmed` \| `candidate_verify` \| `search_needed` \| `not_found` \| `not_applicable`
- `verified_date`: ISO date when the link was confirmed
- `notes`: free text

### Visibility and workflow

| Field | Values | Default |
|---|---|---|
| `visibility` | `private`, `unlisted`, `public-unindexed`, `public` | `private` |
| `cataloguing.review_status` | `draft`, `review`, `published`, `archived` | `draft` |
| `cataloguing.catalogued_by` | string | email of cataloguer |
| `cataloguing.tasks` | list[string] | Outstanding tasks (auto-generated) |

---

## Entity: Artwork / Passport

An artwork record is the central document. It maps to an issued **passport** — a
versioned, publicly citable scholarly record.

### Identity

| Field | Notes |
|---|---|
| `artbase_id` | Local working ID (e.g. `AP-2026-000001`) |
| `artbase_canonical_id` | `AB` + 8 base32 chars — set at first publication |
| `version` | Integer, starts at 1 |
| `visibility` | Same four-state enum as Artist |

### Object ID fields (the nine categories)

These are the core of the Object ID standard. All nine should be completed before a
passport is considered publishable.

| Field | Object ID category | Notes |
|---|---|---|
| `object_id.title` | Title | Primary title, language of original |
| `object_id.object_type` | Type of object | e.g. `paintings`, `sculptures` |
| `object_id.object_type_aat` | Type of object | Getty AAT controlled term |
| `object_id.materials` | Materials and techniques | Display string (e.g. `oil on panel`) |
| `object_id.materials_aat` | Materials and techniques | List of Getty AAT terms |
| `object_id.dimensions_display` | Measurements | Human-readable (e.g. `42 × 34 cm`) |
| `object_id.height_cm` | Measurements | Numeric, centimetres |
| `object_id.width_cm` | Measurements | Numeric, centimetres |
| `object_id.depth_cm` | Measurements | Numeric, centimetres (optional) |
| `object_id.inscriptions` | Inscriptions and markings | Transcription + location; `"none"` is a valid answer |
| `object_id.distinguishing` | Distinguishing features | Damage, repairs, unusual features |
| `object_id.subject` | Subject | Brief iconographic description |
| `object_id.date_display` | Date or period | Human-readable (e.g. `c. 1650`, `c. 1503–1519`) |
| `object_id.date_earliest` | Date or period | Numeric year (start of range) |
| `object_id.date_latest` | Date or period | Numeric year (end of range) |
| `object_id.maker_id` | Maker | References `CanonicalArtist.artbase_id` |

### Iconography

| Field | Notes |
|---|---|
| `iconography.iconclass_codes` | ICONCLASS notation codes, semicolon-separated in Airtable |
| `iconography.iconclass_labels` | Human-readable ICONCLASS labels |
| `iconography.depicts` | Free-text list of depicted subjects |

### Location

| Field | Notes |
|---|---|
| `location.collection` | Current owner/repository name |
| `location.collection_qid` | Wikidata Q-number for the collection |
| `location.inventory_number` | Collection's accession/inventory number |
| `location.location_notes` | Display location (gallery, city) |

### Provenance

`provenance` is a list of structured event objects:

| Field | Notes |
|---|---|
| `sequence` | Integer ordering |
| `start_date` | ISO 8601 or partial |
| `end_date` | ISO 8601 or partial |
| `owner` | Display name of owner/holder |
| `owner_entity_id` | References an artist, institution, or person entity |
| `manner` | Controlled: `purchase`, `gift`, `inheritance`, `commission`, `loan`, `unknown` |
| `place` | Display name |
| `confidence` | `high`, `medium`, `low` |
| `is_gap` | Boolean — marks documented gaps |
| `wwii_status` | WWII 1933–1945 check status |
| `gdpr_public` | Boolean — whether the owner's name may be published |
| `public_summary` | Redacted public version if GDPR restricts the full record |

### Authority links (artworks)

| Field | Notes |
|---|---|
| `authority_links.wikidata.id` | Q-number if the artwork has a Wikidata entry |
| `authority_links.artbase_id` | `AB` + 8 base32 (the canonical passport ID) |

---

## Entity: Collection

Represents a client engagement — a named collection of artworks.

| Field | Notes |
|---|---|
| `collection_id` | `CO` + 8 base32, or working `COL-…` |
| `client_name` | Legal or trading name |
| `collection_name` | Named collection (may differ from client name) |
| `privacy_default` | Default visibility for records in this collection |
| `default_language` | ISO 639-1 |

---

## Shared sub-models

### DateField

Used wherever a date with explicit precision and provenance is needed.

```json
{
  "value":      "1926-08-28",
  "precision":  "day",
  "status":     "conflict",
  "source_ids": ["SRC-001"],
  "notes":      "Conflict between sources A and B"
}
```

### AuthorityLink

```json
{
  "id":            "Q123456",
  "uri":           "https://www.wikidata.org/wiki/Q123456",
  "status":        "confirmed",
  "verified_date": "2026-05-01",
  "notes":         null
}
```

### SourceDocument

```json
{
  "source_id":        "SRC-001",
  "source_type":      "monograph",
  "title":            "Herberts Siliņš",
  "publisher":        "Neputns",
  "url":              null,
  "publication_date": "2012",
  "license":          "in copyright"
}
```

### ConflictRecord

Explicit data conflicts are stored in the record until resolved:

```json
{
  "field":   "life.birth_date",
  "values":  [
    {"value": "1926-08-25", "source_id": "SRC-001"},
    {"value": "1926-08-28", "source_id": "SRC-002"}
  ],
  "status":  "unresolved",
  "created": "2026-05-27"
}
```

---

## Quality scoring

### Object ID score (artworks)

`ObjectIDFields.score()` counts how many of the nine Object ID categories are filled.
An artwork with score ≥ 7 is considered export-ready (`is_export_ready()` returns True).

### Artist Object ID score

`CanonicalArtist.object_id_score()` applies a comparable nine-point scale adapted for
persons: type of entity, media, name, date, place, nationality, biography, authority
confirmation, sources.

---

## Relationship types (CollectiveAccess profile)

These relationship types will be encoded in `profile/artbase.xml`:

| From | To | Relationship |
|---|---|---|
| Artwork | Artist/Maker | `made by` / `artist of` |
| Artwork | Place | `created in` / `creation place of` |
| Artwork | Occurrence (provenance event) | `subject of provenance event` |
| Provenance event | Entity (person/institution) | `owner / holder` |
| Provenance event | Place | `occurred in` |
| Artwork | Collection | `part of collection` |
| Artwork | Source document | `documented by` |
| Artist | Source document | `documented by` |
