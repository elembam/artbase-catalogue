# LIDO Transformation Pipeline — Architecture

*Converting Artwork Archive CSV exports into validated LIDO 1.1 and EODEM XML*

Version 0.1 — engineering specification

---

## Purpose and scope

This document specifies a small, durable command-line tool that:

1. Reads a CSV (or XLSX) export from Artwork Archive
2. Validates input completeness against our cataloguing rules
3. Transforms each row into a LIDO 1.1 XML record
4. Optionally constrains output to the EODEM profile of LIDO 1.1
5. Validates the output against the official LIDO XSD and (for EODEM) the EODEM Schematron rules
6. Emits a clean, deliverable XML file per record or as a batch

The tool is operator-driven, not a service. It runs locally on demand when a client deliverable requires LIDO output. No daemon, no API, no scheduled jobs — at least not in v1.

## Non-goals

- Real-time sync with Artwork Archive (CSV export is fine; the SaaS doesn't expose a true API in v1 scope anyway)
- Import *into* Artwork Archive (one-way, out only)
- A GUI (the operator is technical enough to run a Python CLI)
- Multi-tenant SaaS hosting (this is internal tooling for our service business)

---

## Inputs

### Artwork Archive CSV export

Standard fields exported by Artwork Archive (subject to confirmation from a live export — field names may differ slightly):

- `Piece ID`, `Title`, `Artist`, `Year`, `Medium`, `Subject`, `Dimensions`, `Inventory Number`
- `Description`, `Notes`, `Location`, `Acquired From`, `Date Acquired`
- `Current Value`, `Insurance Value`, `Donor`, `Status`
- `Tags`, image filenames

### Custom fields (per our house style — see HOUSE_STYLE_MANUAL.md §2.2)

- `aat_object_type`, `aat_medium`, `aat_technique` — Getty AAT terms + URIs
- `ulan_artist_id`, `ulan_artist_uri` — Getty ULAN
- `tgn_place_uri` — Getty TGN
- `iconclass_codes` — comma-separated ICONCLASS codes
- `wikidata_qid` — Wikidata Q-number
- `viaf_id`, `cat_raisonne_ref`
- `object_id_inscriptions`, `object_id_distinguishing_features`
- `provenance_chain` — structured multi-line text, our pipe-delimited format
- `confidentiality_level` — controlled list including "Europeana-eligible"
- `condition_summary`

### Configuration

A YAML config file per engagement specifying:

- Client identifier and contact details (for the LIDO `<recordSource>`)
- Default rights statement for images (CC0 / CC BY / In Copyright / etc.)
- Default language for record content
- Which records to include (filter by `confidentiality_level`)
- Output mode: `lido_full` or `eodem`
- Output directory

---

## Outputs

### Primary: LIDO 1.1 XML

One of:

- **Per-record files**: `[clientCode]_[pieceID].xml` in the output directory
- **Batch file**: one `<lidoWrap>` document containing many `<lido>` records, named `[clientCode]_lido_[YYYYMMDD].xml`

### Optional: EODEM profile output

Same content, additionally validated against the EODEM XSD and Schematron rules. Used when the deliverable is for museum loan exchange (where EODEM is the expected format) rather than general LIDO usage.

### Validation report

A plain-text report alongside the XML output, listing:

- Records successfully transformed
- Records rejected with reasons (missing required fields, invalid vocabulary URIs, etc.)
- XSD validation results
- Schematron validation results (for EODEM mode)
- Summary statistics

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│  artwork-archive-export.csv          config.yaml                 │
│             │                            │                        │
│             ▼                            ▼                        │
│  ┌──────────────────────┐    ┌──────────────────────┐            │
│  │ csv_loader.py        │    │ config_loader.py     │            │
│  │ pandas-based reader  │    │ pydantic schema      │            │
│  └──────────┬───────────┘    └──────────┬───────────┘            │
│             │                            │                        │
│             └────────────┬───────────────┘                        │
│                          ▼                                        │
│             ┌────────────────────────┐                            │
│             │ record_validator.py    │  ← input completeness      │
│             │ enforces house style   │    checks                  │
│             └────────────┬───────────┘                            │
│                          ▼                                        │
│             ┌────────────────────────┐                            │
│             │ lido_builder.py        │  ← maps record → LIDO      │
│             │ lxml.etree composer    │    XML tree                │
│             └────────────┬───────────┘                            │
│                          ▼                                        │
│             ┌────────────────────────┐                            │
│             │ vocabulary_resolver.py │  ← Getty/ICONCLASS URI     │
│             │ (offline cache + API)  │    expansion, validation   │
│             └────────────┬───────────┘                            │
│                          ▼                                        │
│             ┌────────────────────────┐                            │
│             │ xsd_validator.py       │  ← against lido-v1.1.xsd  │
│             └────────────┬───────────┘                            │
│                          ▼                                        │
│         ┌────────────────┴─────────────────┐                      │
│         │                                  │                      │
│         ▼ (mode = lido_full)               ▼ (mode = eodem)       │
│  ┌────────────────┐               ┌──────────────────────┐        │
│  │ writer.py      │               │ eodem_constrain.py   │        │
│  │ writes LIDO    │               │ + schematron_check.py│        │
│  └────────────────┘               └─────────┬────────────┘        │
│                                              │                    │
│                                              ▼                    │
│                                     ┌────────────────┐            │
│                                     │ writer.py      │            │
│                                     │ writes EODEM   │            │
│                                     └────────────────┘            │
└──────────────────────────────────────────────────────────────────┘
```

---

## Technology choices

- **Language**: Python 3.11+
- **CSV/XLSX reading**: `pandas` (`openpyxl` for Excel)
- **XML construction**: `lxml.etree` (not `xml.etree.ElementTree` — `lxml` is faster, supports XSD validation, and produces cleaner output)
- **XSD validation**: `lxml.etree.XMLSchema`
- **Schematron validation**: `lxml.isoschematron`
- **Configuration**: `pydantic` v2 for type-safe config loading
- **CLI**: `typer` or `click`
- **HTTP for vocabulary APIs**: `httpx` with a local SQLite cache
- **Testing**: `pytest` with fixture-based test artworks (Starry Night, Mona Lisa, plus synthetic edge cases)
- **Linting/formatting**: `ruff`

---

## Module breakdown

### `csv_loader.py`

Reads the CSV/XLSX, normalises column names (Artwork Archive's export header can vary), produces a list of dictionaries — one per piece. Returns a typed `RawRecord` Pydantic model.

Responsibilities:
- Handle UTF-8 BOM, quoted fields with embedded newlines, multi-line custom field values
- Resolve Artwork Archive's idiosyncrasies (e.g. dimensions stored as a single string "H × W × D cm" rather than separate fields)
- Parse the `provenance_chain` field's pipe-delimited structure into a list of provenance event objects

### `config_loader.py`

Loads and validates the engagement YAML. Provides typed access to all configuration values via a `Config` Pydantic model.

### `record_validator.py`

Applies the house-style rules to each `RawRecord` and emits a `ValidatedRecord` or a `ValidationError` listing missing required fields.

Rules:
- Object ID nine categories must all be populated (warn if any are missing)
- `aat_object_type` and `aat_medium` are required for export
- If `iconclass_codes` is present, each code is checked against the ICONCLASS regex pattern
- If `wikidata_qid` is present, it matches `^Q\d+$`
- Dimensions must be parseable into structured height/width/depth values
- Provenance entries must be parseable per our format

### `vocabulary_resolver.py`

Given an AAT, ULAN, TGN, or ICONCLASS reference, returns:
- The authoritative label
- The full URI
- The labels in available languages (for `<term xml:lang="en">`, `<term xml:lang="de">`, etc.)

Uses an offline SQLite cache that is pre-populated for the terms our practice uses most. Falls back to live API calls for unknown terms; caches results.

Pre-populated cache covers approximately: 500 AAT terms (object types, media, techniques common to European painting and sculpture), 100 ICONCLASS top-level categories, the most common European TGN entries.

### `lido_builder.py`

The heart of the tool. Given a `ValidatedRecord`, constructs a `lido:lido` XML element following LIDO 1.1 conventions.

LIDO has six top-level descriptive blocks. Our mapping:

| LIDO block | Our source |
|---|---|
| `descriptiveMetadata/objectClassificationWrap` | `aat_object_type` |
| `descriptiveMetadata/objectIdentificationWrap` | Title, inscriptions, distinguishing features, materials, measurements, repository (Artwork Archive Inventory Number) |
| `descriptiveMetadata/eventWrap` | Production event (artist + date + place), provenance events, exhibition history |
| `descriptiveMetadata/objectRelationWrap` | Related works, ICONCLASS subject concepts |
| `administrativeMetadata/rightsWorkWrap` | Rights statement from config |
| `administrativeMetadata/recordWrap` | Record source (us / the client), record ID, record type |
| `administrativeMetadata/resourceWrap` | Image references |

The builder uses helper functions per block to keep the code readable. Each helper takes the relevant slice of the record and returns the corresponding `lxml.etree.Element` tree.

### `xsd_validator.py`

Wraps `lxml.etree.XMLSchema` against the official LIDO 1.1 XSD. The XSD is shipped with the tool (not fetched at runtime) for reliability.

### `eodem_constrain.py`

Takes a full LIDO record and removes / re-orders elements to conform to the EODEM profile (which is a *subset* of LIDO). Most of the work is dropping non-EODEM elements; some involves enforcing required fields that LIDO marks optional.

### `schematron_check.py`

Runs the EODEM Schematron rules against EODEM-mode output. Reports any business-rule violations (which the XSD alone can't catch).

### `writer.py`

Serialises the validated XML tree to disk with proper formatting (UTF-8, indented, XML declaration), per-record files or batched `<lidoWrap>` as configured.

---

## CLI usage

```bash
# Standard LIDO export of a client engagement
artbase-lido transform \
  --input ./exports/client_X_export_20260601.csv \
  --config ./engagements/client_X.yaml \
  --output ./deliverables/client_X/lido/ \
  --mode lido_full

# EODEM export, batch file
artbase-lido transform \
  --input ./exports/client_X_export_20260601.csv \
  --config ./engagements/client_X.yaml \
  --output ./deliverables/client_X/eodem/ \
  --mode eodem \
  --batch

# Validate an existing LIDO file
artbase-lido validate ./deliverables/client_X/lido/PIECE_001.xml

# Vocabulary cache management
artbase-lido vocab refresh --source aat
artbase-lido vocab lookup --term "oil paint"
```

---

## Repository layout

```
artbase-lido/
├── README.md
├── pyproject.toml
├── src/
│   └── artbase_lido/
│       ├── __init__.py
│       ├── cli.py
│       ├── csv_loader.py
│       ├── config_loader.py
│       ├── record_validator.py
│       ├── vocabulary_resolver.py
│       ├── lido_builder.py
│       ├── eodem_constrain.py
│       ├── xsd_validator.py
│       ├── schematron_check.py
│       ├── writer.py
│       └── schemas/
│           ├── lido-v1.1.xsd
│           ├── lido-v1.1-profile-EODEM-v1.0.xsd
│           └── eodem.sch
├── tests/
│   ├── fixtures/
│   │   ├── starry_night.csv
│   │   ├── mona_lisa.csv
│   │   ├── synthetic_edge_cases.csv
│   │   └── expected_outputs/
│   ├── test_csv_loader.py
│   ├── test_record_validator.py
│   ├── test_lido_builder.py
│   ├── test_xsd_validation.py
│   └── test_eodem_validation.py
├── data/
│   └── vocab_cache.sqlite
└── docs/
    ├── field_mapping.md         # CSV column → LIDO element
    ├── eodem_subset.md          # which LIDO elements EODEM uses
    └── house_style_integration.md
```

---

## Validation and testing strategy

**Unit tests** for each module, especially `lido_builder.py` — every LIDO block has its own test that constructs a fragment and asserts the resulting XML structure.

**Integration tests** using public-domain artworks (Starry Night, Mona Lisa) as fixtures. The fixture CSV produces an expected LIDO XML; the test asserts byte-level (or after normalization) equality.

**Validation tests** confirm:
- Every fixture's output passes the LIDO XSD
- Every EODEM fixture additionally passes the Schematron rules
- Invalid inputs raise descriptive errors

**Manual review**: at least one expert-reviewed manual diff between our output and the LIDO Primer's example records, to catch semantic errors the validators won't.

---

## Versioning and standards drift

The LIDO and EODEM schemas evolve. The tool pins specific schema versions in `src/artbase_lido/schemas/` and surfaces the version in every output file's metadata. When CIDOC releases a new version:

1. Pull the new XSD/Schematron
2. Run fixture tests against the new schema
3. Identify breaking changes
4. Update the `lido_builder.py` mappings
5. Bump our tool's major version

This is a small task once or twice a year, not a maintenance burden.

---

## Future extensions (post-v1)

- Direct Artwork Archive API integration when (if) they expose one, removing the CSV step
- Round-trip: import LIDO back into Artwork Archive (e.g. when accepting EODEM from a loan partner)
- Web-based diff viewer for QC reviews
- Europeana EDM direct export (one step further than LIDO, if a client wants to bypass an aggregator's transformation)
- Bulk-mode performance optimization (only relevant beyond 10,000 records per run)

---

## Operational notes

**Where this runs.** Locally on the operator's Mac (or any Linux/Windows machine with Python). No server. No cloud. Output files are delivered to the client by whatever mechanism the engagement specifies (encrypted email, secure file transfer, USB drive for the most sensitive clients).

**Dependencies vendored where reasonable.** The LIDO XSD and EODEM Schematron files are committed to the repository, not downloaded at runtime, so the tool works offline and produces reproducible output across years.

**Configuration in version control.** Per-engagement YAML configs are tracked in a private repository alongside the tool itself. Each client's deliverable is reproducible from their CSV and their config.

**Audit trail.** Every transformation run writes a log file alongside the output containing: tool version, input file hash, config hash, schema versions, validation results, timestamp. This is what allows you to credibly answer "what exactly did you deliver to Client X on date Y?" three years later.

---

*This is engineering specification, not finished code. The first implementation milestone is the CSV loader and a minimal `lido_builder` covering the seven LIDO blocks with the simplest possible content. Validation against the LIDO XSD is the v1 acceptance criterion.*
