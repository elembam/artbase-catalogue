# ArtBase

**ArtBase** is a scholarly digital art catalogue platform for European corporate and museum collections. It combines a CollectiveAccess backend with a standalone export pipeline that produces standards-compliant metadata (Object ID, LIDO 1.1, EODEM, Dublin Core).

---

## What's in this repository

```
artbase/
├── artbase_export/          Python pipeline: Airtable → canonical JSON → Git
├── docs/                    Data model and standards-mapping documentation
├── profile/                 CollectiveAccess installation profile (artbase.xml)
├── exports/                 LIDO 1.1 and EODEM export mappings + validated samples
│   ├── lido_1.1/
│   └── eodem/
├── theme/                   Pawtucket2 frontend theme (Kress-inspired)
│   ├── views/               Smarty templates
│   ├── css/
│   ├── js/
│   └── conf/
├── scripts/                 Data migration, validation, deployment scripts
│   └── sample_data/         Fictional or public-domain sample records only
├── upstream/                git submodule — collectiveaccess/providence (not yet cloned)
└── pawtucket/               git submodule — collectiveaccess/pawtucket2 (not yet cloned)
```

---

## Technology stack

| Layer | Technology |
|---|---|
| Collections management | CollectiveAccess Providence (PHP 8.x, MySQL 8) |
| Public interface | CollectiveAccess Pawtucket2 (PHP, Smarty) |
| Export pipeline | Python 3.11+, Pydantic v2, Typer |
| Working data layer | Airtable (via `artbase_export`) |
| Dev environment | Docker Desktop + VS Code |
| Standards | Object ID, LIDO 1.1, EODEM, Dublin Core, EDM |
| Vocabularies | Getty AAT, ULAN, TGN · ICONCLASS · Wikidata |

---

## Quick start — Python export pipeline

The export pipeline converts Airtable records into standards-ready canonical JSON files.

```bash
cd artbase_export
pip install -e ".[dev]"

# Copy and configure
cp config.yaml.example config.yaml
# edit config.yaml — add your Airtable token and base ID

# Dry run (no writes)
artbase-export run --dry-run --verbose

# Full export
artbase-export run

# Status table
artbase-export status

# Validate existing JSON files
artbase-export validate
```

See [`artbase_export/GETTING_STARTED.md`](artbase_export/GETTING_STARTED.md) for a step-by-step setup guide.

---

## CollectiveAccess backend

The CollectiveAccess backend requires Docker Desktop.

```bash
# Clone upstream repos (first time only)
git clone https://github.com/collectiveaccess/providence.git upstream
git clone https://github.com/collectiveaccess/pawtucket2.git pawtucket

# Start containers
docker compose up -d

# Providence admin: http://localhost:8080
# Pawtucket public: http://localhost:8081
```

See [`docs/deployment.md`](docs/deployment.md) for full setup instructions.

---

## Documentation

| File | Contents |
|---|---|
| `docs/data_model.md` | Entity types, field glossary, relationship types |
| `docs/standards_mapping.md` | Field → Object ID / LIDO / EODEM / Dublin Core mapping |
| `docs/deployment.md` | Docker setup and installation guide |
| `ARTBASE_ARCHITECTURE.md` | Technical commitments: domain, URLs, identifiers |
| `EXPORT_ARCHITECTURE.md` | Export pipeline architecture diagram |
| `LIDO_PIPELINE_ARCHITECTURE.md` | LIDO/EODEM pipeline design |
| `CLAUDE.md` | Instructions for AI-assisted development |

---

## Design reference

The public-facing interface is modelled on the [Kress Collection Digital Archive](https://kress.nga.gov/), which is built on the same CollectiveAccess Pawtucket2 stack. Study it before changing any layout or navigation code.

---

## Data and privacy

- **No real client data in this repository.** Sample data in `scripts/sample_data/` is either fictional or drawn from public-domain museum collections.
- Records default to `visibility: private`. Nothing reaches the public frontend without an explicit `is_public = 1` flag.
- Provenance data may identify living people. Pre-1950 cutoff (configurable) applies for GDPR purposes.
- Credentials (`config.yaml`, `.env` files) are in `.gitignore` and must never be committed.

---

## Canonical domain

`artbase.eu` — all passport URLs, API endpoints, and client deliverables use this domain.
