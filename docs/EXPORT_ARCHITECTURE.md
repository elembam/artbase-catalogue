# Ars Accordia Export Pipeline — Architecture

*How Airtable rows become canonical JSON files that drive passports, LIDO exports, and the public registry.*

Version 0.1

---

## The fundamental problem

Airtable is a productivity tool. The passport is a commitment to 2046. These two things cannot be the same system, but they need to stay in sync.

The export pipeline is the bridge. It runs on demand (or on schedule) and converts Airtable's relational rows into a flat, portable, version-controlled canonical record that belongs entirely to you.

---

## Data flow

```
┌─────────────────────────────────────────────────────────────────┐
│  AIRTABLE (working layer)                                       │
│  Artists_Makers, Artworks, Source_Documents, Authority_Links   │
│  Cataloguers edit here daily                                    │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                    artbase-export
                    (this pipeline)
                           │
              ┌────────────▼────────────┐
              │  1. Fetch               │  pyairtable API calls
              │  2. Join                │  link authorities + sources into artist
              │  3. Transform           │  Airtable schema → canonical model
              │  4. Validate            │  check required fields, flag conflicts
              │  5. Assign IDs          │  generate Ars Accordia IDs if not yet present
              │  6. Write               │  one JSON file per entity
              │  7. Commit              │  git commit with meaningful message
              │  8. Report              │  what changed, what needs review
              └────────────┬────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│  CANONICAL STORE (data/ directory, committed to Git)            │
│                                                                 │
│  data/artists/ART-HERBERTS-SILINS-1926.json                    │
│  data/artworks/AP-WORK-SILINS-0001.json                        │
│  data/collections/COL-NORDIC-CORP-001.json                     │
└──────────────────────────┬──────────────────────────────────────┘
                           │
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
   passport_generator.py         lido_pipeline.py
   (HTML passports)               (EODEM XML)
              │                         │
              ▼                         ▼
   arsaccordia.com/p/AB7F3KQ2X1      arsaccordia.com/api/p/AB7F3KQ2X1/eodem
```

---

## The canonical JSON format

Every entity has the same envelope structure regardless of type:

```json
{
  "_schema":       "artbase:artist:v1",
  "_artbase_id":   "ART-HERBERTS-SILINS-1926",
  "_airtable_id":  "recXXXXXXXXXXXXXX",
  "_version":      1,
  "_created":      "2026-05-27T12:00:00Z",
  "_exported":     "2026-05-27T12:00:00Z",
  "_status":       "draft",
  "_visibility":   "private",
  "data":          { ... },
  "authority_links": { ... },
  "sources":       [ ... ],
  "conflicts":     [ ... ],
  "cataloguing":   { ... }
}
```

The `data` block is schema-specific (different fields for artists vs artworks). The envelope is identical so tooling can process any entity type.

---

## Module structure

```
artbase-export/
├── pyproject.toml
├── config.yaml.example          — copy to config.yaml, fill in secrets
├── data/                        — the canonical store (committed to Git)
│   ├── artists/
│   ├── artworks/
│   └── collections/
├── src/
│   └── artbase_export/
│       ├── __init__.py
│       ├── cli.py               — typer CLI: export, validate, status
│       ├── config.py            — load config.yaml + env vars
│       ├── airtable/
│       │   ├── client.py        — pyairtable wrapper
│       │   └── schema.py        — Airtable table names + field IDs
│       ├── canonical/
│       │   ├── models.py        — Pydantic v2 models for canonical JSON
│       │   └── ids.py           — Ars Accordia ID generation
│       ├── transform/
│       │   ├── artist.py        — Airtable record → CanonicalArtist
│       │   └── artwork.py       — Airtable record → CanonicalArtwork
│       └── writers/
│           ├── json_writer.py   — write canonical files to data/
│           └── git_handler.py   — commit changed files to Git
└── tests/
    ├── fixtures/
    │   └── airtable_artist.json — sample Airtable API response
    └── test_transform_artist.py
```

---

## The key design decision: denormalisation on export

Airtable stores artists, authority links, and sources in separate tables (linked records). The canonical JSON **denormalises** these into one document.

Why: the canonical JSON must be self-contained. An artist's passport must include authority links and sources without requiring joins. It must be readable by humans, parseable by scripts, and archivable as a standalone file.

The denormalisation is handled in the transform layer. When exporting an artist:
1. Fetch the artist row
2. Expand linked Source_Documents (via Airtable's linked-records API)
3. Expand linked Authority_Links rows
4. Merge into one CanonicalArtist model
5. Write as one JSON file

---

## Git as version history

The `data/` directory lives in a Git repository. Every export run that produces changes creates one Git commit:

```
commit 7f3a2b1
Author: Ars Accordia Export <export@arsaccordia.com>
Date:   2026-05-27T12:00:00Z

Export 2026-05-27T12:00:00Z

Changed: 3 artists, 2 artworks
  - ART-HERBERTS-SILINS-1926: authority_links.viaf status → confirmed
  - ART-ANNA-LINDGREN-1972: created (draft)
  - AP-WORK-SILINS-0001: created (draft)
  - AP-WORK-LINDGREN-0003: object_id_completeness 6 → 9
  - AP-WORK-LINDGREN-0004: visibility private → public
```

`git diff` on any two commits shows exactly what changed between catalogue versions. That's the version history the architecture document committed to.

---

## Running the pipeline

```bash
# First time setup
cp config.yaml.example config.yaml   # fill in AIRTABLE_TOKEN, BASE_ID
pip install -e .

# Export everything
artbase-export run

# Export a single artist (useful during cataloguing)
artbase-export run --artist ART-HERBERTS-SILINS-1926

# Check what would change without writing
artbase-export run --dry-run

# Validate existing canonical files (no Airtable call)
artbase-export validate

# Show status summary
artbase-export status
```

---

## What the pipeline does NOT do

- It does not write back to Airtable (read-only from Airtable)
- It does not push the Git repo (do this manually or in CI)
- It does not regenerate passports (a separate step — `passport_generator.py`)
- It does not validate LIDO (a separate step — `lido_pipeline.py`)

Each step in the chain is a separate script with a clear input/output boundary.
