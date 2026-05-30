# Ars Accordia — Copilot Instructions

## Project overview

**Ars Accordia** is a European art authority catalogue, starting with Latvian and Swedish art,
that creates structured "art passports" — authoritative object records linking museum inventory
numbers, Wikidata Q-numbers, and a stable Ars Accordia identifier for each artwork and artist.

The long-term goal is for `Ars Accordia passport ID` to become a recognised Wikidata external
identifier property, making the project a peer authority alongside museum catalogues.

---

## Repository structure

```
/
├── data/
│   ├── raw/                        # Source scrapes, untouched
│   │   └── LNMA_Latvia_National_Museum_Artworks.xlsx
│   ├── processed/                  # Normalised working files
│   │   └── LNMA_Ars_Accordia_Artist_Register.xlsx
│   └── output/                     # Final deliverables
├── scripts/
│   ├── scrape/                     # Source collection scrapers
│   ├── normalise/                  # Data cleaning and normalisation
│   ├── reconcile/                  # Wikidata SPARQL reconciliation
│   └── contribute/                 # QuickStatements batch generators
├── passports/                      # Individual passport records (JSON)
└── docs/
    └── reconciliation-workflow.md  # The full reconciliation workflow
```

---

## Core data schemas

### Artwork record (the art passport)

| Field | Type | Example | Notes |
|---|---|---|---|
| `aa_passport_id` | string | `AA/LV/LNMA/001` | Stable, never changes |
| `title` | string | `Princess with a Monkey` | |
| `creator` | string | `Janis Rozentāls` | Normalised form |
| `creator_lifespan` | string | `1866–1916` | en-dash separator, always |
| `birth_year` | int | `1866` | Parsed from lifespan |
| `death_year` | int | `1916` | Parsed from lifespan |
| `date_created` | string | `1913` | May be range or `c.YYYY` |
| `type` | string | `Painting` | |
| `medium` | string | `Oil on canvas` | |
| `physical_dimensions` | string | `147.5 (h) x 71 (w) cm` | Source format preserved |
| `height_cm` | float | `147.5` | Parsed from dimensions |
| `width_cm` | float | `71.0` | Parsed from dimensions |
| `collection_name` | string | `Latvian Painting Collection...` | |
| `collection_number` | string | `VMM GL-5668` | Museum inventory number |
| `institution` | string | `LNMA` | |
| `wikidata_artwork_q` | string | `Q12345678` | May be empty |
| `wikidata_artist_q` | string | `Q123456` | May be empty |
| `tier` | int | `1` / `2` / `3` | Reconciliation tier |
| `source_url` | string | `https://artsandculture.google.com/...` | |

### Artist authority record

| Field | Type | Example |
|---|---|---|
| `aa_artist_id` | string | `AA/LV/ARTIST/001` |
| `name` | string | `Janis Rozentāls` |
| `canonical_lifespan` | string | `1866–1916` |
| `birth_year` | int | `1866` |
| `death_year` | int | `1916` |
| `work_count` | int | `39` |
| `wikidata_q` | string | `Q123456` |
| `notes` | string | Free text flags |

---

## ID conventions

```
Ars Accordia Passport ID:   AA/{country}/{institution}/{zero-padded-sequential}
Ars Accordia Artist ID:     AA/{country}/ARTIST/{zero-padded-sequential}

Country codes:   LV = Latvia, SE = Sweden
Institution:     LNMA, NM (Nationalmuseum), etc.

Examples:
  AA/LV/LNMA/001     First artwork in the LNMA batch
  AA/LV/ARTIST/001   Most prolific artist in the LNMA batch (Rozentāls)
  AA/SE/NM/001       First artwork in a future Swedish Nationalmuseum batch
```

IDs are assigned in collection-page order and never reassigned.

---

## Reconciliation tiers

| Tier | Condition | Action |
|---|---|---|
| 1 | Artist Q exists AND artwork Q exists on Wikidata | Enrich existing items |
| 2 | Artist Q exists, artwork Q does not | Create artwork item only |
| 3 | Neither artist Q nor artwork Q exists | Create both |

The tier field in the working spreadsheet drives which QuickStatements template to use.

---

## Wikidata property mappings

When generating QuickStatements or SPARQL, use these property mappings:

```python
WD_PROPS = {
    'instance_of':        'P31',
    'title':              'P1476',
    'creator':            'P170',
    'inception':          'P571',
    'collection':         'P195',
    'inventory_number':   'P217',
    'height':             'P2048',
    'width':              'P2049',
    'material_used':      'P186',
    'described_at_url':   'P973',
    'copyright_status':   'P6216',
    # artist properties
    'instance_human':     'P31',   # value: Q5
    'sex_gender':         'P21',
    'country_citizen':    'P27',
    'occupation':         'P106',
    'date_of_birth':      'P569',
    'date_of_death':      'P570',
}

WD_VALUES = {
    'painting':           'Q3305213',
    'drawing':            'Q93184',
    'watercolour':        'Q18761202',
    'pastel':             'Q12043905',
    'human':              'Q5',
    'painter':            'Q1028181',
    'latvia':             'Q211',
    'lnma':               'Q681819',    # Latvian National Museum of Art — verify
    'oil_paint':          'Q296955',
    'canvas':             'Q4259259',
    'cardboard':          'Q389782',
    'paper':              'Q11472',
    'watercolor_medium':  'Q22915256',
    'india_ink':          'Q177239',
    'gouache':            'Q204330',
    'cm_unit':            'Q174728',
}
```

---

## Common tasks and patterns

### Parsing dimensions

Dimensions in the source data use mixed formats. Always parse defensively:

```python
import re

def parse_dimensions(s):
    """
    Handles: '147.5 (h) x 71 (w) cm'
             '72 (h) x 101,3 (w) cm'   ← European comma decimal
             '21.7 (h) x 27.3 (w) cm'
    Returns: (height_cm: float, width_cm: float) or (None, None)
    """
    if not s or not isinstance(s, str):
        return None, None
    s = s.replace(',', '.')  # European decimal
    m = re.search(r'([\d.]+)\s*\(h\)\s*[xX×]\s*([\d.]+)\s*\(w\)', s)
    if m:
        return float(m.group(1)), float(m.group(2))
    return None, None
```

### Normalising lifespans

```python
import re

def normalise_lifespan(s):
    """Standardise to en-dash separator, strip whitespace."""
    if not s or (isinstance(s, float)):
        return ''
    return re.sub(r'/', '–', str(s).strip())

def parse_years(lifespan: str):
    """Returns (birth: int|None, death: int|None)."""
    if '–' not in lifespan:
        return None, None
    parts = lifespan.split('–')
    try: birth = int(parts[0].strip())
    except: birth = None
    try: death = int(parts[1].strip())
    except: death = None
    return birth, death
```

### SPARQL artist lookup

```python
import requests

SPARQL_ENDPOINT = 'https://query.wikidata.org/sparql'

def lookup_artist(name: str, birth_year: int = None) -> list[dict]:
    """
    Returns list of candidate Wikidata items for an artist.
    Each dict: {q, label, birth_year, death_year, description}
    """
    name_filter = name.lower().replace("'", "\\'")
    birth_clause = f'FILTER(?birthYear = {birth_year})' if birth_year else ''

    query = f"""
    SELECT ?item ?itemLabel ?birthYear ?deathYear ?itemDescription WHERE {{
      ?item wdt:P31 wd:Q5 .
      OPTIONAL {{ ?item wdt:P569 ?birth . BIND(YEAR(?birth) AS ?birthYear) }}
      OPTIONAL {{ ?item wdt:P570 ?death . BIND(YEAR(?death) AS ?deathYear) }}
      {birth_clause}
      SERVICE wikibase:label {{
        bd:serviceParam wikibase:language "en,lv,de,sv" .
      }}
      FILTER(CONTAINS(LCASE(?itemLabel), "{name_filter}"))
    }}
    LIMIT 5
    """

    resp = requests.get(
        SPARQL_ENDPOINT,
        params={'query': query, 'format': 'json'},
        headers={'User-Agent': 'ArsAccordia/1.0 (https://www.arsaccordia.com)'}
    )
    resp.raise_for_status()
    bindings = resp.json()['results']['bindings']

    results = []
    for b in bindings:
        results.append({
            'q':           b['item']['value'].split('/')[-1],
            'label':       b.get('itemLabel', {}).get('value', ''),
            'birth_year':  int(b['birthYear']['value']) if 'birthYear' in b else None,
            'death_year':  int(b['deathYear']['value']) if 'deathYear' in b else None,
            'description': b.get('itemDescription', {}).get('value', ''),
        })
    return results
```

### QuickStatements: enrich existing artwork (Tier 1)

```python
def qs_enrich_artwork(artwork_q: str, record: dict, lnma_q: str = 'Q681819') -> str:
    """Generate QuickStatements lines to enrich an existing artwork item."""
    lines = []
    q = artwork_q

    if record.get('collection_number'):
        lines.append(f'{q}\tP217\t"{record["collection_number"]}"\tP195\t{lnma_q}')
    if record.get('source_url'):
        lines.append(f'{q}\tP973\t"{record["source_url"]}"')
    if record.get('height_cm'):
        lines.append(f'{q}\tP2048\t{record["height_cm"]}U174728')
    if record.get('width_cm'):
        lines.append(f'{q}\tP2049\t{record["width_cm"]}U174728')

    return '\n'.join(lines)
```

### QuickStatements: create new artwork item (Tier 2)

```python
def qs_create_artwork(record: dict, artist_q: str, lnma_q: str = 'Q681819') -> str:
    """Generate QuickStatements block to create a new artwork item."""
    lines = ['CREATE']
    lines.append(f'LAST\tLen\t"{record["title"]}"')
    lines.append(f'LAST\tP31\t{record["wd_type"]}')       # from WD_VALUES
    lines.append(f'LAST\tP170\t{artist_q}')
    if record.get('date_created'):
        year = record['date_created'][:4]
        lines.append(f'LAST\tP571\t+{year}-00-00T00:00:00Z/9')
    lines.append(f'LAST\tP195\t{lnma_q}')
    if record.get('collection_number'):
        lines.append(f'LAST\tP217\t"{record["collection_number"]}"\tP195\t{lnma_q}')
    if record.get('height_cm'):
        lines.append(f'LAST\tP2048\t{record["height_cm"]}U174728')
    if record.get('width_cm'):
        lines.append(f'LAST\tP2049\t{record["width_cm"]}U174728')
    if record.get('source_url'):
        lines.append(f'LAST\tP973\t"{record["source_url"]}"')
    return '\n'.join(lines)
```

---

## Data quality rules

When writing any data processing code, enforce these rules:

1. **Lifespan separator is always en-dash `–`**, never slash `/` or hyphen `-`
2. **Dimensions**: always convert European comma-decimals to dot before parsing
3. **Before creating any Wikidata item**, run a SPARQL check on the VMM inventory number — a result means the item already exists
4. **Tier 3 artists**: always search exhaustively (name variants, Latvian/German/Swedish spellings) before creating new items
5. **Batch size for QuickStatements**: maximum 50 items per batch until a track record is established
6. **AA Passport IDs are immutable** — never reassign or reuse a retired ID

---

## Current status (LNMA pilot)

| Phase | Description | Status |
|---|---|---|
| 0 | Normalise dataset, assign IDs | ✅ Complete |
| 1 | Artist SPARQL lookups | 🔄 In progress |
| 2 | Artwork reconciliation, tier classification | ⏳ Pending |
| 3 | Wikidata enrichment (Tier 1) | ⏳ Pending |
| 4 | Artwork creation (Tier 2) | ⏳ Pending |
| 5 | Artist + artwork creation (Tier 3) | ⏳ Pending |
| 6 | Passport finalisation | ⏳ Pending |
| 7 | QA and project page log | ⏳ Pending |

**Working files:**
- `data/processed/LNMA_Ars_Accordia_Artist_Register.xlsx` — 56 artists, 328 artworks, Wikidata Q column blank
- `docs/reconciliation-workflow.md` — full step-by-step workflow

**Known data issues (resolved):**
- Johann Walter `1869–1832` → corrected to `1869–1932` (7 records)
- Jāzeps Grosvalds `1895/1920` → corrected to `1891–1920` (2 records)
- Johann Heinrich Baumann split into (I) 1753–1832 and (II) 1873–1930
- 26 building-documentation records separated from artwork records

---

## Style conventions

- Python 3.10+
- Type hints on all function signatures
- `pandas` for bulk data operations, `openpyxl` for formatted xlsx output
- SPARQL queries: add `User-Agent: ArsAccordia/1.0` header on all Wikidata requests
- All output xlsx files use Arial 10pt, dark navy (`#1F3864`) header rows
- Log every Wikidata write (create or enrich) to a `contributions.log` with timestamp, Q-number, and action type
