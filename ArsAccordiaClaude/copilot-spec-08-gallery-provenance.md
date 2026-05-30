# Instruction 8 — Commercial-Gallery Provenance (Galerija Jēkabs / paintings.lv)

*Hand to Copilot as a single component. It builds on Instruction 7 (sources & attestations). Where it conflicts with Copilot's instinct, the spec wins — ask before deviating.*

---

## Purpose

Record, honestly and in the data, that the ~288 Latvian artists currently in Ars Accordia were originally seeded from the artist index of **Galerija Jēkabs** (an auction house and gallery in Riga; website `paintings.lv`). This closes a real provenance gap: those artists' names and life dates are currently **unattributed** — exactly the kind of orphaned data `audit_provenance.py` exists to catch.

It also lays groundwork for eventually recording artworks **sold or auctioned through the gallery** as provenance events.

---

## The one distinction this whole spec turns on: ORIGIN ≠ AUTHORITY

A commercial gallery/auction house is a **data-origin** source, not a **scholarly authority**. These are different things and must be modelled differently:

- **Origin** answers: *"Why is this artist in our catalogue, and where did the initial data come from?"* → Galerija Jēkabs.
- **Authority** answers: *"Is this fact true?"* → Wikidata, ULAN, VIAF, LNDB, and the published catalogues (Instruction 7).

Because the gallery **sells the work it lists**, it is self-interested. Therefore the following are **hard rules**, not preferences:

1. **A gallery source is NEVER cited on Wikidata** as a reference for biographical/identity facts. (Unlike the ISBN catalogues, it does not become a Wikidata item and does not appear in `S248`.)
2. **A gallery source NEVER, on its own, upgrades a record to `confirmed`.** Life dates from the gallery remain candidate-level until an independent authority corroborates them.
3. **Gallery data is recorded as lineage, not asserted as truth.** It documents the *origin* of an entry; correctness still comes from the authorities.

Adding the gallery origin is **orthogonal to verification status**: a `candidate` artist stays `candidate`; a `confirmed` artist (confirmed via authorities/books) stays `confirmed` with the gallery noted as additional lineage.

---

## Part A — Extend the source model with type and trust flags

Add to the `Sources` schema (Instruction 7) the fields that let the pipeline treat sources differently by kind:

| Field | Values | Meaning |
|---|---|---|
| `source_type` | `published_catalogue` · `museum_record` · `authority_file` · `commercial_gallery` · `auction_record` | What kind of source this is |
| `wikidata_citable` | `true` / `false` | May this source back a Wikidata reference? |
| `can_confirm` | `true` / `false` | May this source contribute to `confirmed` status? |

Defaults by type:
- `published_catalogue`, `museum_record` → `wikidata_citable: true`, `can_confirm: true`
- `commercial_gallery`, `auction_record` → `wikidata_citable: false`, `can_confirm: false`

The contribution and verification pipelines must **read these flags**, not assume. Any code path that emits a Wikidata reference or sets `confirmed` must check `wikidata_citable` / `can_confirm` and skip sources that are false.

---

## Part B — Register Galerija Jēkabs as a source

```json
// data/sources/SRC-GALERIJA-JEKABS.json
{
  "source_id": "SRC-GALERIJA-JEKABS",
  "name": "Galerija Jēkabs",
  "also_known_as": ["Izsoļu nams Jēkabs", "Auction House Jēkabs"],
  "source_type": "commercial_gallery",
  "subtype": "auction house and gallery",
  "website": "https://paintings.lv",
  "artist_index_url": "https://paintings.lv/artists/list",
  "location": "Jēkaba iela 26/28, Rīga, LV-1050, Latvia",
  "wikidata_citable": false,
  "can_confirm": false,
  "wikidata_qid": null,
  "wikidata_note": "Not expected to have or need a Wikidata item; commercial entity, internal lineage source only.",
  "role_in_catalogue": "Data origin for the initial Latvian artist set; future provenance source for works sold/auctioned through the gallery.",
  "_meta": {
    "registered_at": null,
    "terms_note": "Factual data (names, life dates) used for attribution and seeding. Do not republish proprietary content (images, descriptions, prices). Respect robots.txt and rate limits."
  }
}
```

Note: unlike the ISBN catalogues, this source is **not** resolved to a Wikidata item — there is no find-or-create step for it. It exists only in the Ars Accordia registry.

---

## Part C — The `data_origin` attestation on artists

Each artist that came from the gallery gets an attestation with `role: "data_origin"`, distinguishing it from a corroborating authority attestation:

```json
"attestations": [
  {
    "source_id": "SRC-GALERIJA-JEKABS",
    "role": "data_origin",
    "url": "https://paintings.lv/artists/view/87",
    "asserts": {
      "name": "Bruno Aide",
      "birth_year": 1913,
      "death_year": 1994
    },
    "authoritative": false,
    "retrieved": "2026-05-DD"
  }
]
```

Semantics:
- `role: "data_origin"` — this is *where the entry came from*, not corroboration of a fact.
- `authoritative: false` — explicitly flags that this attestation cannot be used to confirm or to cite on Wikidata.
- The `asserts` block records the name and dates **as the gallery lists them**, so that if an authority later disagrees, the discrepancy is visible (e.g. gallery says 1913, an authority says 1914 → surfaced, not silently merged).

---

## Part D — Match the gallery index to existing Ars Accordia artists (ingestion)

The gallery list is highly matchable: each entry is `SURNAME Firstname (birth - death)` with a stable per-artist URL `https://paintings.lv/artists/view/{id}`.

```
1. Fetch the artist index, paginated: /artists/list, /artists/list/2 … through the
   last page. Respect robots.txt; rate-limit (e.g. 1 request / 2s); identify the
   client honestly in the User-Agent.
2. Parse each entry → { surname, first_name, birth_year, death_year (nullable),
   gallery_url }.
3. Normalize the name (diacritics-aware: Ā, Č, Ē, Ģ, Ī, Ķ, Ļ, Ņ, Š, Ū, Ž) and
   build the match key: normalized_surname + birth_year.
4. Match against existing data/artists/*.json (whose IDs already follow
   ART-SURNAME-BIRTHYEAR — so this key aligns directly).
5. On a confident match (surname + birth year agree):
       add the data_origin attestation (Part C) to that artist's JSON
       (idempotent — keyed on source_id + gallery_url; never duplicate).
6. Gallery artist NOT in Ars Accordia → log to reports/gallery_unmatched.json
   as a discovery candidate. Do NOT auto-create; if later added, the artist is
   `candidate` status with the gallery as data_origin only.
7. Ars Accordia artist NOT on the gallery list → log to
   reports/artists_without_gallery_origin.json for review (they may have come
   from elsewhere, or the name normalization missed).
```

The gallery's life dates are **seed/candidate data**, never authoritative. If the gallery date and an existing authoritative date conflict, record a discrepancy in `_meta.discrepancies[]`; do not overwrite the authoritative value.

---

## Part E — Hard rules and how this interacts with the other pipelines

- **`wikidata_contribute.py`**: when assembling references, it must **skip any attestation whose source has `wikidata_citable: false`**. A `data_origin` attestation from Galerija Jēkabs can never appear in an `S248` reference. (If the only support for a fact is the gallery, that fact is **not contributable** — it needs a real authority first.)
- **`verify_candidates.py`**: a `data_origin` / `commercial_gallery` attestation contributes **zero** positive signal toward confirmation. Confirmation still requires the existing authority signals (description-language match, citizenship, LNDB presence, published-catalogue attestation, etc.).
- **`audit_provenance.py`**: after this runs, the seeded artists' names/dates are no longer "unattributed" — they trace to `SRC-GALERIJA-JEKABS`. But the audit must classify this as a **non-authoritative origin**, distinct from authority-backed fields, so the distinction stays visible in the report.

---

## Part F — Future: artworks sold/auctioned through the gallery

Galerija Jēkabs is also an auction house, so works passing through it generate **provenance events** — and provenance is legitimate, valuable data (it's the chain of custody, not a truth-claim about identity). When artwork ingestion begins:

- Record a sale/auction through the gallery as a provenance entry on the artwork, e.g.
  `{ "event": "offered/sold", "agent": "Galerija Jēkabs", "source_id": "SRC-GALERIJA-JEKABS", "url": "<lot URL>", "date": "<auction date>", "lot": "<n>" }`.
- This is **internal provenance documentation**. Do **not** publish prices, and do **not** push contemporary commercial-gallery provenance to Wikidata. (Auction provenance *can* be relevant on Wikidata in some cases, but treat that as a separate, deliberate decision — default is internal.)
- The auction archive (`paintings.lv/auctions/archive/...`) is the structured place to harvest these later.

---

## Part G — The Source Ledger (traceability view)

The attestations and authority links give Ars Accordia complete lineage, but it lives scattered across `attestations[]` and `authorities.*` and is hard to read at a glance. The **source ledger** is a per-record summary that groups every source behind an entity by **role** and **trust**, so the full provenance of any artist or artwork — and how its verification was reached — is visible in one view. This is the explicit "trace and distinguish where the data comes from" capability, for Ars Accordia's own structure first, independent of whether anything is ever sent to Wikidata.

### It is a derived view, never a second source of truth

The ledger is **computed** from data that already exists — `attestations[]`, `authorities.*`, the `sources/` registry's trust flags (`source_type`, `wikidata_citable`, `can_confirm`), and `verification_status`. It is regenerated, not hand-edited, so it can never drift from the underlying attestations. It may be materialized into the record (written on export for fast display), but it is always reproducible from the primary data. **If the ledger and the attestations ever disagree, the attestations win and the ledger is rebuilt.**

### Structure

```json
"source_ledger": {
  "generated_at": "2026-05-DD",

  "origin": [
    {
      "source_id": "SRC-GALERIJA-JEKABS",
      "name": "Galerija Jēkabs",
      "type": "commercial_gallery",
      "citable": false,
      "url": "https://paintings.lv/artists/view/87"
    }
  ],

  "authority": [
    {
      "source_id": "SRC-LNMM-PORTRAITS-2009",
      "name": "Mākslinieks. Portrets. Pašportrets (LNMM, 2009)",
      "type": "published_catalogue",
      "citable": true,
      "wikidata_qid": "Qxxxxxxx",
      "backs": ["birth_year", "death_year"],
      "page": "NN"
    },
    {
      "source_id": "AUTH-ULAN",
      "name": "Getty ULAN",
      "type": "authority_file",
      "citable": true,
      "backs": ["birth_date", "death_date", "nationality"]
    }
  ],

  "provenance": [],

  "verification": {
    "status": "confirmed",
    "basis": "authority",
    "confirmed_by": ["SRC-LNMM-PORTRAITS-2009", "AUTH-VIAF"]
  }
}
```

Three role buckets, each carrying the trust flag so the distinction is explicit:
- **`origin`** — where the entry came from. Sources whose attestation `role` is `data_origin` (the gallery). Almost always `citable: false`.
- **`authority`** — sources that back facts and can be cited. Citable-source attestations (the books, `role: attestation`) **and** the external authority links from `authorities.*` (Wikidata, ULAN, VIAF, LNDB).
- **`provenance`** — chain-of-custody events (mainly artworks; e.g. an auction through the gallery, `role: provenance_*`).

Plus a **`verification`** summary: the status, whether it was reached by `authority` (or is still `candidate`/`rejected`), and exactly which authority sources justified it — so "confirmed" is never a bare label; you can see what confirmed it.

### Additional deepest layer — field-level provenance

For audit-grade traceability, the ledger may also carry per-field provenance, so every fact traces to its source(s):

```json
"field_provenance": {
  "birth_year": { "value": 1893, "sources": ["SRC-GALERIJA-JEKABS", "SRC-LNMM-PORTRAITS-2009"], "has_citable_source": true,  "discrepancy": false },
  "death_year": { "value": 1984, "sources": ["SRC-GALERIJA-JEKABS"],                              "has_citable_source": false, "discrepancy": false }
}
```

`has_citable_source: false` is the useful flag: it marks a fact that *only* a non-citable origin (the gallery) supports — i.e. not yet contributable to Wikidata and not yet authority-confirmed. That is the "what's merely traceable vs what's verified" distinction, made per fact.

### Human-readable rendering

The same ledger renders as a glanceable block for the admin/passport view and audit reports:

```
ART-ANNUSS-1893 — source ledger
  Origin (internal):    Galerija Jēkabs                         [not citable]
  Authority (citable):  LNMM Portraits 2009, p.NN  ·  ULAN  ·  VIAF
  Provenance:           —
  Verification:         confirmed  (basis: authority — LNMM Portraits 2009, VIAF)
```

### Why this matters for the overlap scenario

When an artist seeded from the gallery later appears in one of the published catalogues, the ledger shows both, correctly scoped: the gallery under `origin` (internal, not citable), the book under `authority` (citable, Wikidata-eligible) — and the verification summary shows the book is what moved the record to `confirmed`. Origin and authority side by side, each doing its job, legible at a glance. That is the internal clarity this component exists to provide.

### Interaction with `audit_provenance.py`

`audit_provenance.py` consumes the same primary data; the ledger is its legible output form. A record whose ledger has no field resting only on a non-citable origin (outside those intentionally origin-only) is "clean." The audit's job becomes: flag any field with no source at all, and surface any fact still standing on a non-citable origin alone.

---

## Public display guidance

Default to recording the gallery origin as **internal lineage / audit metadata**, not a prominent public credit. Reasons: it's a commercial entity that currently sells the work, and surfacing it publicly risks reading as advertising or affiliation — which cuts against the neutral-registry, "not a marketplace" positioning.

If displayed publicly at all, do so **neutrally and without commercial linkage**: e.g. a small data-provenance note ("Initial record data sourced from the Galerija Jēkabs artist index"), never prices, "buy here," or endorsement. This is a deliberate decision to make consciously, not a default to switch on.

---

## CLI

```
python3 scripts/ingest_gallery_origin.py                 # match + attach data_origin attestations
python3 scripts/ingest_gallery_origin.py --dry-run       # report matches/conflicts, write nothing
python3 scripts/ingest_gallery_origin.py --artist ART-AIDE-1913
python3 scripts/ingest_gallery_origin.py --report        # write match/unmatched/conflict reports only

python3 scripts/build_source_ledger.py                   # (re)generate the source ledger for every record
python3 scripts/build_source_ledger.py --record ART-ANNUSS-1893
python3 scripts/build_source_ledger.py --print ART-ANNUSS-1893   # human-readable ledger to stdout
python3 scripts/build_source_ledger.py --check           # verify ledgers match underlying attestations; exit 1 on drift
```

---

## Acceptance tests

1. Registering the source writes `data/sources/SRC-GALERIJA-JEKABS.json` with `wikidata_citable: false`, `can_confirm: false`.
2. Ingestion matches "AIDE Bruno (1913–1994)" → `ART-AIDE-1913` and adds a `data_origin` attestation with the correct `/artists/view/87` URL and `authoritative: false`.
3. Re-run is idempotent — the attestation is not duplicated.
4. A gallery date that conflicts with an existing authoritative date produces a `_meta.discrepancies[]` entry and does **not** overwrite the authoritative value.
5. `wikidata_contribute.py` run on an artist whose *only* support for a fact is the gallery attestation: that fact is **not** emitted (no `S248` to the gallery, no contribution).
6. `verify_candidates.py`: adding the gallery attestation does **not** change any artist's verification status.
7. A gallery artist absent from Ars Accordia is logged as a discovery candidate, not auto-created.
8. `audit_provenance.py` reports the seeded artists' names/dates as attributed-but-non-authoritative (origin), not as confirmed authority data.
9. The source ledger for an artist with both a gallery origin and a book attestation lists the gallery under `origin` (`citable: false`) and the book under `authority` (`citable: true`), with `verification.basis` = `authority`.
10. The ledger is reproducible: deleting and regenerating it from the attestations yields an identical result (`--check` passes).
11. `field_provenance` marks a gallery-only fact with `has_citable_source: false`, and a book/authority-backed fact with `true`.
12. Editing an attestation and regenerating updates the ledger; `--check` fails when a stale ledger no longer matches its attestations.

---

## What this component does NOT do

- It does **not** make the gallery a Wikidata item or a Wikidata citation. Ever.
- It does **not** confirm any record or contribute any positive verification signal.
- It does **not** overwrite authoritative data with gallery data; conflicts are surfaced.
- It does **not** auto-create artists from the gallery list (discovery candidates are logged for human decision).
- It does **not** republish the gallery's proprietary content (images, descriptions, prices) — only factual names/dates for attribution and seeding, with robots.txt and rate limits respected.
- It does **not** turn the public registry into a sales channel or affiliate of the gallery.
- The source ledger does **not** store new facts — it is a derived view of the attestations and authority links, always regenerable; if it ever drifts, the attestations are authoritative and the ledger is rebuilt.
