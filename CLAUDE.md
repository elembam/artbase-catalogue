# ArtBase — CLAUDE.md

Instructions for Claude (Claude Code, VS Code, or claude.ai) working on this project.
Read this file fully before doing anything else in a session.

---

## What ArtBase is

ArtBase is a **standards-compliant cataloguing service for European art collections** — corporate, private, and institutional. It is not a CRM, not a marketplace, not a gallery platform.

The deliverable is an **Artwork Passport**: a per-artwork document that records identity, provenance, condition, authority links, and export-ready data at museum standards. Passports are human-readable (HTML), machine-readable (LIDO 1.1 / EODEM XML), and permanently identified.

Long term, ArtBase becomes a public registry — the reference for art held in private and corporate collections that does not appear on Europeana or in museum catalogues.

---

## The actual technology stack

```
WORKING LAYER (where cataloguers edit daily)
  Airtable base — using the artwork_passport_airtable_starter_kit schema
  Tables: Collections, Artists_Makers, Artworks, Authority_Links,
          Object_ID_Checklist, Photography_Media, Provenance_Events,
          Condition_Conservation, Source_Documents, Passport_Issues,
          Imports, Export_Jobs

          ↓  artbase-export (Python CLI)

CANONICAL LAYER (the durable record)
  data/artists/*.json        one file per artist
  data/artworks/*.json       one file per artwork
  Committed to Git — every export run is one commit
  Version history = catalogue version history

          ↓  passport_generator.py (to be built)

PUBLISHED LAYER (what the world sees)
  Passport HTML    artbase.eu/p/{id}
  EODEM XML        artbase.eu/api/p/{id}/eodem
  LIDO XML         artbase.eu/api/p/{id}/lido
  OAI-PMH feed     artbase.eu/oai
  Static files — hosted on Cloudflare Pages / Netlify / similar
```

**No Docker. No PHP. No database server.**
The entire stack is: Airtable (SaaS) + Python scripts + static files + Git.

---

## Repository layout

```
artbase/
├── CLAUDE.md                        # this file
├── artbase_export/                  # the export pipeline package
│   ├── GETTING_STARTED.md           # setup guide
│   ├── pyproject.toml
│   ├── config.yaml.example
│   ├── config.yaml                  # gitignored — real credentials
│   ├── data/                        # canonical JSON store — committed to Git
│   │   ├── artists/
│   │   └── artworks/
│   └── src/artbase_export/
│       ├── cli.py                   # artbase-export run / status / validate
│       ├── config.py
│       ├── airtable/
│       │   ├── client.py            # Airtable API wrapper
│       │   └── schema.py            # ALL field names — edit here when Airtable changes
│       ├── canonical/
│       │   └── models.py            # Pydantic models for canonical JSON
│       ├── transform/
│       │   ├── artist.py            # Airtable → CanonicalArtist
│       │   └── artwork.py           # Airtable → CanonicalArtwork
│       └── writers/
│           ├── json_writer.py
│           └── git_handler.py
│
├── passports/                       # generated HTML/XML output (gitignored or separate repo)
│   └── (generated — do not edit manually)
│
├── docs/                            # operations library
│   ├── HOUSE_STYLE_MANUAL.md
│   ├── ARTIST_IDENTITY_WORKFLOW.md
│   ├── ARTBASE_ARCHITECTURE.md
│   ├── ARTBASE_WIKIDATA_PROFILE.md
│   ├── AUTHORITY_CONTRIBUTION_STRATEGY.md
│   ├── PARTNERSHIP_PROGRAM.md
│   ├── LIDO_PIPELINE_ARCHITECTURE.md
│   ├── EXPORT_ARCHITECTURE.md
│   ├── STRUCTURED_WIKIDATA_WORKFLOW.md
│   └── SCHEMA_PUBLICATION_GUIDE.md
│
├── scripts/
│   ├── artist_pipeline.py           # Wikidata lookup + QuickStatements generator
│   └── embed_image.py               # embed images into passport HTML
│
├── demo/                            # demo passports (Mona Lisa example set)
│   ├── artwork_passport_mona_lisa.html
│   ├── artwork_passport_mona_lisa.eodem.html
│   ├── artwork_passport_mona_lisa.eodem.xml
│   ├── catalogue.html
│   └── client_brief_authority_records.html
│
└── wikidata/
    └── artbase_wikidata_schema.shex  # EntitySchema for Wikidata publication
```

---

## Standards ArtBase implements

| Standard | What it does | Where used |
|---|---|---|
| **Object ID** (ICOM) | Nine-category minimum identification | Every artwork record |
| **CDWA** | Cataloguing rules for art | House style manual |
| **LIDO 1.1** | XML exchange for cultural objects | Export pipeline |
| **EODEM** | LIDO profile for museum loans | Export pipeline |
| **Getty AAT** | Controlled vocabulary for object types, materials | Airtable + canonical JSON |
| **Getty ULAN** | Artist name authority | Airtable Artists_Makers |
| **Getty TGN** | Geographic places | Canonical JSON |
| **ICONCLASS** | Iconographic subject classification | Airtable + canonical JSON |
| **Wikidata** | Cross-reference hub | Airtable + authority work |
| **VIAF / ISNI / ORCID / RKD** | Artist authority identifiers | Airtable Artists_Makers |

---

## Permanent identifiers

Every entity gets a stable ArtBase ID once the identifier scheme is finalised:
- Artists: `AR` + 8 Crockford base32 characters (e.g. `AR7F3KQ2X1`)
- Passports/Artworks: `AB` + 8 Crockford base32 characters (e.g. `AB7F3KQ2X1`)
- Collections: `CO` + 8 Crockford base32 characters

Airtable local IDs during development:
- Artists: `ART-0001`, `ART-NEW-001`, etc.
- Artworks/Passports: `AP-2026-000001`, etc.

**IDs are never reused, never reassigned.** Once a record has an ID, it keeps it forever.

---

## Running the export pipeline

```bash
# Install
cd artbase_export
pip install -e ".[dev]"

# Configure (first time)
cp config.yaml.example config.yaml
# edit config.yaml — add Airtable token and base_id

# Run
artbase-export run --dry-run    # preview without writing
artbase-export run              # export to data/
artbase-export status           # show state of all records
artbase-export validate         # validate existing JSON files
```

VS Code: use the Run and Debug panel (F5) — launch.json has five pre-configured profiles.

---

## Conventions Claude should follow

### When making changes to the export pipeline

- **`airtable/schema.py` is the single source of truth** for field names. When an Airtable field name changes, update `schema.py` only — the transform layer reads from it. Never hardcode field name strings elsewhere.
- **Do not modify canonical JSON files directly.** They are always generated by the export pipeline from Airtable. If a JSON file needs a correction, fix it in Airtable, re-export.
- **Pydantic validation is the quality gate.** If a transform produces a validation error, fix the Airtable data or the transform logic — do not silence the error with `try/except`.
- **Keep transforms readable, not clever.** A new cataloguer should be able to read `transform/artist.py` and understand what each field does.

### When working on passport HTML/CSS

- Match the established visual language: Fraunces (italic serif) for titles, Public Sans for body, JetBrains Mono for IDs and codes, paper/seal-red/gold colour palette.
- Passports are **print-friendly** — always include a `@media print` block.
- Images are **base64-embedded** — no external image dependencies in delivered HTML files.
- Every authority link is a **working hyperlink** to the external authority page.

### When working on LIDO / EODEM

- The LIDO 1.1 XSD and EODEM Schematron are the validation authority, not our own assumptions.
- Validate every sample output against both before committing.
- Reference schemas live in `wikidata/` and the LIDO pipeline architecture doc.

### What to ask before doing

Ask before:
- Changing field names in `airtable/schema.py` (affects all transform logic)
- Adding new Pydantic models (check they don't duplicate existing structures)
- Modifying canonical JSON that has already been "published" (visibility ≠ private)
- Any write operation back to Airtable (pipeline is read-only by default)

Proceed without asking for:
- Adding new transform helper functions
- Improving error messages and logging
- Writing tests and fixtures
- Documentation and comments
- Adding new CLI options that default to safe behaviour (dry-run, verbose)

### What to look up rather than guess

- Current pyairtable API patterns (the library evolves — check its docs)
- Airtable field names (check `schema.py` — they must match Airtable exactly)
- LIDO / EODEM element names and cardinality (check the official XSD)
- Getty vocabulary URIs (verify at `vocab.getty.edu`)

---

## Key external references

| Resource | URL |
|---|---|
| Airtable API docs | https://airtable.com/developers/web/api/introduction |
| pyairtable docs | https://pyairtable.readthedocs.io/ |
| LIDO schema | https://lido-schema.org/ |
| EODEM | https://cidoc.mini.icom.museum/working-groups/documentation-standards/eodem-home/ |
| Object ID (ICOM) | https://icom.museum/en/resources/standards-guidelines/objectid/ |
| Getty Vocabularies | https://www.getty.edu/research/tools/vocabularies/ |
| ICONCLASS browser | https://iconclass.org/ |
| Wikidata | https://www.wikidata.org/ |
| ArtBase Wikidata profile | docs/ARTBASE_WIKIDATA_PROFILE.md |
| House Style Manual | docs/HOUSE_STYLE_MANUAL.md |
| Getting Started | artbase_export/GETTING_STARTED.md |

---

## First session checklist

When opening this project for the first time:

1. Read this file fully.
2. Check whether `artbase_export/config.yaml` exists.
   - If yes: run `artbase-export status` to see current state.
   - If no: follow `artbase_export/GETTING_STARTED.md` from the top.
3. Run `git log --oneline -10` in `artbase_export/` to see recent export history.
4. Ask the user what they want to work on.

Do not write any code, run any exports, or make any Airtable calls without confirming the plan with the user first.
