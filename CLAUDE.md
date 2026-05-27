# ArtBase — CLAUDE.md

Instructions for Claude (in VS Code, Claude Code, or claude.ai) working on this project.

## Project goal

**ArtBase** is a scholarly digital art catalogue platform built on **CollectiveAccess** (Providence + Pawtucket2) as the underlying collections management and publication system. ArtBase serves European corporate art collections and museum clients, with strong standards compliance (Object ID, LIDO 1.1, EODEM, Getty vocabularies, Wikidata cross-references).

### Design and structural reference

The visual and structural model is the **Kress Collection Digital Archive** at https://kress.nga.gov/. This site is itself built on CollectiveAccess Pawtucket2, so what we want is achievable within the stack — we are not fighting the framework.

Study the Kress site's information architecture before changing layout code. Key features to replicate:

- Top-level browse axes: **Objects**, **Archival Materials**, **Object History** (Acquisitions, Distributions), **People & Organizations** (Artists, Institutions, Dealers & Collectors, Historians & Conservators, All Names).
- Scholarly object pages: large image, full tombstone data, provenance as a structured timeline, exhibition history, bibliography, conservation notes, related archival materials.
- Cross-linking everywhere: every artist, dealer, institution, and provenance event is a linked entity, not free text.
- Restrained, content-first visual design: serif typography for object titles and labels, neutral palette, no decorative chrome.

## Technology stack

- **Backend**: CollectiveAccess Providence (PHP 8.x, MySQL/MariaDB, Apache or Nginx)
- **Frontend**: CollectiveAccess Pawtucket2 (PHP, Smarty templates, vanilla JS, CSS)
- **Local dev environment**: Docker Desktop on macOS (preferred) or Homebrew LAMP stack
- **Editor**: VS Code with PHP Intelephense, PHP Debug, Docker, and XML/XSD extensions
- **Version control**: Git, GitHub
- **Standards targets**: Object ID, LIDO 1.1, EODEM, Dublin Core, EDM (Europeana)
- **Controlled vocabularies**: Getty AAT, ULAN, TGN, ICONCLASS, Wikidata Q-numbers

## Repository layout

We do **not** modify the upstream CollectiveAccess code directly. Instead we maintain our customisations in a parallel structure that can be applied on top of a clean upstream checkout. This keeps us able to pull upstream updates without merge hell.

```
artbase/
├── CLAUDE.md                          # this file
├── README.md                          # human-facing project readme
├── docker-compose.yml                 # local dev environment
├── upstream/                          # git submodule: collectiveaccess/providence
├── pawtucket/                         # git submodule: collectiveaccess/pawtucket2
├── profile/                           # OUR CollectiveAccess installation profile
│   ├── artbase.xml                    # main installation profile
│   ├── artbase.xsd                    # validation schema
│   └── vocabularies/                  # AAT/ULAN/TGN/ICONCLASS imports
├── exports/                           # OUR LIDO and EODEM export configurations
│   ├── lido_1.1/
│   │   ├── mapping.xml                # CA → LIDO field mapping
│   │   └── samples/                   # validated sample outputs
│   └── eodem/
│       ├── mapping.xml
│       ├── schematron/
│       └── samples/
├── theme/                             # OUR Pawtucket2 theme (Kress-inspired)
│   ├── views/                         # Smarty templates
│   ├── css/
│   ├── js/
│   └── conf/
├── scripts/                           # data migration, validation, deployment
│   └── validate_lido.sh
└── docs/
    ├── data_model.md
    ├── standards_mapping.md
    └── deployment.md
```

## Initial setup tasks (in order)

When starting fresh, do these in sequence. Don't skip ahead.

### 1. Clone the repositories

```bash
git clone https://github.com/collectiveaccess/providence.git upstream
git clone https://github.com/collectiveaccess/pawtucket2.git pawtucket
```

Check the README in each for the current required PHP and MySQL versions. **Do not assume** — these change. Verify against the live README on GitHub before installing dependencies.

### 2. Set up Docker development environment

Use Docker Compose to run PHP, MySQL, and the web server in containers. The host filesystem mounts the `upstream/` and `pawtucket/` directories so VS Code edits are immediately live.

Look for a community `docker-compose.yml` in the CollectiveAccess GitHub org or on the support forum as a starting point. If none is current, write our own — PHP-FPM container, MySQL 8 container, Nginx container with separate vhosts for Providence (admin) and Pawtucket (public).

### 3. Run Providence's web-based installer

Once the containers are up:
- Navigate to the Providence URL (e.g. http://localhost:8080)
- The installer asks which installation profile to use — for the first test run, pick a default like `dublin_core` to verify the environment works.
- Once confirmed, drop the database and reinstall using **our** profile (`profile/artbase.xml`) — but only after that profile exists. See section below.

### 4. Build our installation profile

This is the core intellectual work of the project. The profile is an XML file that defines:
- Which **tables** are active (objects, entities, places, occurrences, collections, loans, storage_locations, etc.)
- The **metadata elements** on each table (title, materials, dimensions, provenance event, etc.)
- The **controlled lists** and **vocabularies** used
- The **UI screens** and form layouts
- The **relationship types** between entities (e.g. "artist of", "previous owner of", "exhibited at")

Start by reading these existing profiles in `upstream/install/profiles/xml/` to understand the conventions:
- `dublin_core.xml` — minimal, easy to read
- `isad_g.xml` — archival, shows hierarchical thinking
- Any profile with `lido` in the name, if present

Our profile, `profile/artbase.xml`, should bake in:
- **Object ID's nine fields** as mandatory or strongly recommended (type, materials/techniques, measurements, inscriptions, distinguishing features, title, subject, date, maker).
- **Provenance modelled as events**, not free text. Each provenance entry is an occurrence record with date, actor (entity), place, and event type (acquisition, sale, gift, loan, inheritance).
- **Cross-reference ID fields** on objects: Wikidata Q-number, Getty ULAN (artist), VIAF, RKD ID, catalogue raisonné numbers (F-number, JH-number, etc.), museum accession number.
- **Getty vocabulary integration** for object type, materials, techniques, and place names. CollectiveAccess has built-in connectors for these — use them rather than typing terms manually.
- **Multilingual fields** for title, description, and place names — minimum: English, German, French, Dutch, Italian, Spanish, Swedish.
- **Per-record visibility flags** to support corporate clients who require non-public records alongside public museum records.

### 5. Build the LIDO 1.1 export

Use CollectiveAccess's export framework (`upstream/app/lib/Export/`). Define the mapping in `exports/lido_1.1/mapping.xml`.

Reference materials:
- LIDO Primer: https://lido-schema.org/documents/primer/latest/lido-primer.html
- LIDO 1.1 XSD: https://lido-schema.org/schema/v1.1/lido-v1.1.xsd
- LIDO Handbook "Painting and Sculpture" on the CIDOC documentation site

Validate every sample export against the official XSD before considering the mapping complete.

### 6. Layer EODEM on top

EODEM is a constrained LIDO 1.1 profile. Once the LIDO export is solid, write `exports/eodem/mapping.xml` that produces EODEM-conformant output.

Reference materials:
- EODEM XSD: https://lido-schema.org/profiles/v1.1/lido-v1.1-profile-EODEM-v1.0.xsd
- EODEM Schematron rules (validation beyond what XSD alone catches)
- CIDOC EODEM training module: https://cidoc.info/Training/Online/EODEM/

Validate against XSD **and** run the Schematron rules.

### 7. Build the Pawtucket2 theme

Pawtucket2 themes live in `pawtucket/themes/`. Create our theme in `theme/` at the project root and symlink or mount it in.

Match the Kress structure:
- Browse views: Objects, Archival Materials, Acquisitions, Distributions, Artists, Institutions, Dealers & Collectors, Historians & Conservators, All Names
- Object detail page layout: large image left, tombstone right, scrollable scholarly sections below (provenance, exhibitions, bibliography, conservation, related materials, archival references)
- Entity detail pages: biography, role in collection, list of related objects, related archival materials
- Restrained typography: serif for titles (e.g. a free font like EB Garamond or Cormorant Garamond), sans-serif for UI (e.g. Inter), generous whitespace, neutral palette

Do not invent new navigation patterns. Match Kress's information architecture closely — it is the result of significant scholarly thinking about how art catalogues should be navigated.

## Conventions Claude should follow

### Coding conventions
- Follow CollectiveAccess's existing PHP style — match the surrounding code in any file you modify.
- Smarty templates: keep logic in PHP, templates should be presentational only.
- All user-facing strings must be translatable. Use the `_t()` helper, never hardcode English.
- All database access via the framework (BaseModel, search engine), never raw SQL in templates or controllers.

### When making changes
- **Never modify `upstream/` or `pawtucket/` directly.** All customisations go in `profile/`, `exports/`, `theme/`, and `scripts/`.
- Before changing an installation profile, ask whether the change can be done in our theme or export mapping instead. Profile changes require careful migration.
- When adding fields, document them in `docs/data_model.md` and map them in `docs/standards_mapping.md` showing the equivalent in Object ID, LIDO, EODEM, and Dublin Core.
- Validate every LIDO/EODEM export against the official XSD after every meaningful change.

### Data handling — non-negotiable
- **GDPR**: provenance data may identify living people. Treat past-owner records as personal data unless clearly historical (pre-1950 default cutoff, configurable). Per-record and per-field visibility must be respected on every export.
- **Confidentiality**: corporate-client records default to non-public. Never expose a record to Pawtucket2 (public frontend) without an explicit `is_public = 1` flag.
- **No real client data in the repo.** Sample data goes in `scripts/sample_data/` and must be either fictional or drawn from public-domain museum collections.

### What to ask before doing
Ask before:
- Modifying database schema in the installation profile (irreversible without migration)
- Pulling upstream updates into the submodules (may conflict with our customisations)
- Adding new PHP dependencies (Composer)
- Adding new third-party JS libraries to the theme
- Touching anything in `exports/` after a successful validation run — re-validate before committing

Proceed without asking for:
- Writing Smarty templates in `theme/views/`
- CSS and frontend JS in `theme/`
- Documentation in `docs/`
- Sample data and validation scripts in `scripts/`
- Comments, docstrings, and tests

### What to look up rather than guess
- Current PHP and MySQL version requirements (check upstream README)
- Current LIDO and EODEM schema versions (check lido-schema.org and CIDOC site)
- Getty vocabulary API endpoints (they change occasionally)
- CollectiveAccess profile XML conventions (look at existing profiles in `upstream/install/profiles/xml/`)

## Useful references

- CollectiveAccess docs: https://docs.collectiveaccess.org/
- CollectiveAccess GitHub: https://github.com/collectiveaccess
- Providence repo: https://github.com/collectiveaccess/providence
- Pawtucket2 repo: https://github.com/collectiveaccess/pawtucket2
- CollectiveAccess support forum: https://support.collectiveaccess.org/
- LIDO schema and primer: https://lido-schema.org/
- CIDOC LIDO Working Group: https://cidoc.mini.icom.museum/working-groups/lido/
- EODEM home: https://cidoc.mini.icom.museum/working-groups/documentation-standards/eodem-home/
- Object ID (ICOM): https://icom.museum/en/resources/standards-guidelines/objectid/
- Getty Vocabularies: https://www.getty.edu/research/tools/vocabularies/
- Wikidata: https://www.wikidata.org/
- Design reference: https://kress.nga.gov/

## First session

If this is the first time Claude is opening the project, the first actions should be:

1. Read this file fully.
2. Check whether `upstream/`, `pawtucket/`, and `docker-compose.yml` exist.
   - If not: we are at the very beginning. Propose a plan and wait for confirmation before cloning anything.
   - If yes: read `docs/data_model.md` and `docs/standards_mapping.md` to understand the current state.
3. Run `git status` and `git log --oneline -20` to see what has happened recently.
4. Ask the user what they want to work on in this session.

Do not begin coding, cloning, or installing without confirming the plan with the user first.
