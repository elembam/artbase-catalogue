# Ars Accordia

**Ars Accordia** is a standards-compliant cataloguing service for European art collections — corporate, private, and institutional. It produces **Artwork Passports**: per-artwork documents recording identity, provenance, condition, and authority links at museum standards.

The deliverable is human-readable (HTML), machine-readable (LIDO 1.1 / EODEM XML), and permanently identified. Long term, Ars Accordia becomes a public registry for art in private and corporate collections not yet on Europeana or in museum catalogues.

The stack is intentionally simple: **Airtable** (working layer) → **Python CLI** (`artbase-export`) → **canonical JSON in Git** → **static HTML/XML passports**. No database server. No Docker. No PHP.

---

## What's in this repository

```
artbase/
├── artbase_export/          Python pipeline: Airtable → canonical JSON → Git
│   ├── data/artists/        Canonical artist JSON (committed, version-controlled)
│   ├── data/artworks/       Canonical artwork JSON
│   └── src/artbase_export/  Python package: cli, transform, models, writers
├── docs/                    Operations library and standards documentation
├── scripts/                 Utility scripts (Wikidata lookup, image embedding)
├── demo/                    Demo passports (Mona Lisa example set)
├── wikidata/                Ars Accordia Wikidata EntitySchema
├── passports/               Generated HTML/XML output (not committed)
└── CLAUDE.md                Instructions for AI-assisted development
```

---

## Technology stack

| Layer | Technology |
|---|---|
| Working data | Airtable (artbase_passport_airtable_starter_kit schema) |
| Export pipeline | Python 3.11+, Pydantic v2, Typer, pyairtable |
| Canonical store | JSON files committed to Git |
| Published layer | Static HTML/XML passports on Cloudflare Pages / Netlify |
| Standards | Object ID, CDWA, LIDO 1.1, EODEM, Dublin Core, EDM |
| Vocabularies | Getty AAT, ULAN, TGN · ICONCLASS · Wikidata |

---

## Quick start — export pipeline

```bash
cd artbase_export
pip install -e ".[dev]"

# Configure (first time)
cp config.yaml.example config.yaml
# edit config.yaml — add Airtable token and base_id

# Dry run (preview without writing)
artbase-export run --dry-run

# Full export
artbase-export run

# Status table
artbase-export status

# Validate existing JSON files
artbase-export validate
```

See [`artbase_export/GETTING_STARTED.md`](artbase_export/GETTING_STARTED.md) for full setup instructions.

---

## Quality gates (site + canonical data)

Run this before commit/deploy to catch sitemap drift, broken internal links, and changed JSON issues:

```bash
python3 scripts/quality_gates.py
```

To scan all passport/artist HTML (slower):

```bash
python3 scripts/quality_gates.py --all-html
```

QuickStatements preflight (changed `.qs` files only):

```bash
python3 scripts/wikidata_preflight.py
```

Instruction 20 review-queue workflow:

```bash
# 1) See queue status
python3 scripts/resolve_instruction20_review_queue.py summary

# 2) Record a human decision (dry-run)
python3 scripts/resolve_instruction20_review_queue.py decide \
  --record-id IMLV-074 \
  --action match_existing \
  --selected-artbase-id ART-JURJANE-1944 \
  --reviewer your-id

# 3) Persist decision
python3 scripts/resolve_instruction20_review_queue.py decide \
  --record-id IMLV-074 \
  --action match_existing \
  --selected-artbase-id ART-JURJANE-1944 \
  --reviewer your-id \
  --apply

# 4) Apply approved_match decisions into canonical artist records
#    (adds resolved conflict markers, then marks queue entries as applied)
python3 scripts/resolve_instruction20_review_queue.py apply --apply
```

---

## Documentation

| File | Contents |
|---|---|
| `docs/data_model.md` | Entity types, field glossary, relationship types, quality scoring |
| `docs/standards_mapping.md` | Field → Object ID / LIDO 1.1 / EODEM / Dublin Core mapping |
| `docs/ARS ACCORDIA_ARCHITECTURE.md` | Technical commitments: domain, URLs, identifiers |
| `docs/EXPORT_ARCHITECTURE.md` | Export pipeline architecture |
| `docs/LIDO_PIPELINE_ARCHITECTURE.md` | LIDO/EODEM pipeline design |
| `docs/HOUSE_STYLE_MANUAL.md` | Cataloguing house style |
| `CLAUDE.md` | Instructions for AI-assisted development |

---

## Permanent identifiers

- Artists: `AR` + 8 Crockford base32 chars (e.g. `AR7F3KQ2X1`)
- Artworks/Passports: `AB` + 8 Crockford base32 chars (e.g. `AB7F3KQ2X1`)
- IDs are never reused or reassigned.

---

## Data and privacy

- **No real client data in this repository.** All sample data is fictional or public-domain.
- Provenance data may identify living people. Pre-1950 default cutoff for GDPR purposes.
- Credentials (`config.yaml`) are gitignored and must never be committed.

---

## Canonical domain

`arsaccordia.com` — all passport URLs, API endpoints, and OAI-PMH feed use this domain.
