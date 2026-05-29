# Structured Wikidata Workflow

*How to do authority work efficiently — automate everything except the human review.*

Version 0.1

---

## The principle

**Automate data extraction and assembly. Keep humans as the gatekeepers of publication.**

The reason isn't conservatism; it's quality. Automated extraction from Wikipedia infoboxes makes predictable mistakes (wrong dates, ambiguous places, missing context). A trained cataloguer spots them in seconds. A bot replicates them at scale. Wikidata's data quality depends on this distinction.

In practice: a pipeline produces a *proposed edit set*; the cataloguer reviews it in 5–10 minutes; the publication happens via QuickStatements in one batch submission. **Total time per artist drops from ~75 minutes (hand-editing) to ~10 minutes (review-and-submit).**

---

## The four levels of automation

| Level | What it is | When to use | Wikidata's view |
|---|---|---|---|
| **1. Visual bulk editing** | OpenRefine + Wikidata extension; the Wikidata UI itself | Reviewing 50–500 items with full human judgement per record | Encouraged |
| **2. Semi-automated submission** | QuickStatements — submit a text file of statements through a web tool, one statement at a time, with the human attribution | Most operational use | Encouraged |
| **3. Programmatic API** | Pywikibot, mwclient, WikidataIntegrator — Python scripts that edit directly | Ongoing pipelines, custom logic | Encouraged for assisted edits; requires bot approval for autonomous edits |
| **4. Bot operation** | Registered bot account performing autonomous edits | Very large, repetitive, well-understood operations | Requires formal bot approval process |

For Ars Accordia, **Level 2 (QuickStatements) is the right default**. Level 3 is justified for the data-assembly side (running locally to prepare the QuickStatements file). Level 4 is overkill until we have proven need.

---

## The recommended pipeline

```
  CATALOGUING                  AUTOMATION                  REVIEW
   (cataloguer)                  (script)                (cataloguer)
        │                            │                        │
        ▼                            │                        │
  Artist name + ─────────────────────▶                        │
  basic facts                        │                        │
                                     ▼                        │
                       1. Search Wikidata for artist          │
                            ▶ found: get QID                  │
                            ▶ not found: flag for manual      │
                                     │                        │
                                     ▼                        │
                       2. Fetch full Wikidata entry           │
                            ▶ Audit: present/missing/         │
                              sourced/unsourced               │
                                     │                        │
                                     ▼                        │
                       3. If Wikipedia article exists:        │
                            ▶ Fetch wikitext                  │
                            ▶ Parse infobox                   │
                            ▶ Map fields to properties        │
                                     │                        │
                                     ▼                        │
                       4. Cross-check DBpedia                 │
                          (optional, catches errors)          │
                                     │                        │
                                     ▼                        │
                       5. Generate proposed edits             │
                          → QuickStatements file              │
                                     │                        │
                                     ▼                        │
                                                              │
                                                              ▼
                                                    6. Review proposed edits
                                                       (5–10 min per artist)
                                                       Approve / edit / reject
                                                              │
                                                              ▼
                                                    7. Submit via
                                                       QuickStatements web
                                                              │
                                                              ▼
                                                    8. Log contribution
```

The dividing line is clear: **the script proposes; the cataloguer disposes.**

---

## Tools by name and purpose

### Discovery and reconciliation

**OpenRefine** — `openrefine.org`
- Loads a spreadsheet of artist names; reconciles each against Wikidata
- Visual interface, batch operations
- The standard tool for "we have 200 artists in CatalogIt, are they on Wikidata?"
- Free, runs locally

**Mix'n'Match** — `mix-n-match.toolforge.org`
- For matching external identifiers (Getty ULAN, RKD, VIAF) to Wikidata items
- Especially useful when you have a list of ULAN IDs and want to add them to Wikidata
- Free, web-based

### Submission

**QuickStatements** — `quickstatements.toolforge.org`
- Submit a text file of proposed statements; review then publish
- Format: one line per statement, with QID, PID, value, source
- Best for batches of 10–1,000 statements
- Free, web-based

### Programmatic access

**Pywikibot** — `pywikibot.readthedocs.io`
- The official Python library for MediaWiki automation
- Heavy but capable; the right choice for production bots
- Free, Python

**WikidataIntegrator** — `github.com/SuLab/WikidataIntegrator`
- Higher-level Python library focused on Wikidata
- More ergonomic than raw Pywikibot for Ars Accordia-style work
- Free, Python

**mwclient** — `mwclient.readthedocs.io`
- Lighter Python library for MediaWiki API calls
- Good for read-only or single-edit operations
- Free, Python

### Extraction

**mwparserfromhell** — `mwparserfromhell.readthedocs.io`
- Parses Wikipedia wikitext, including infoboxes
- The standard Python library for extracting structured data from articles
- Free, Python

**DBpedia** — `dbpedia.org`
- Has already extracted structured data from every Wikipedia article
- SPARQL endpoint at `dbpedia.org/sparql`
- Useful as a cross-check against your own infobox parsing
- Free

**Wikidata's "Harvest Templates" tool** — `tools.wmflabs.org/pltools/harvesttemplates`
- Designed specifically for moving infobox data into Wikidata
- Less customisable than a Python pipeline but no code required
- Free, web-based

### Analysis

**Wikidata Query Service (SPARQL)** — `query.wikidata.org`
- Run queries against the Wikidata graph
- Find gaps ("which Latvian painters have no occupation set?")
- Free, web-based

---

## The Ars Accordia pipeline: artist_pipeline.py

The companion script (`artist_pipeline.py`) implements steps 1–5 of the recommended pipeline as a single command-line tool. Usage:

```bash
python3 artist_pipeline.py "Herberts Siliņš" --year 1926
```

What it does:

1. Searches Wikidata for the artist by name (and optionally birth year)
2. Fetches the matched entry's full data
3. Prints an audit: what statements are present (with reference counts) and what's missing from the key property list
4. If the entry has an English Wikipedia article, fetches the wikitext
5. Parses the artist infobox
6. Maps infobox fields to Wikidata properties
7. Generates a QuickStatements file ready to submit

What it doesn't do:

- Edit Wikidata directly (deliberately — the human gate is preserved)
- Look up Wikidata items for places, schools, movements, etc. (this is the *cataloguer's review step* — they confirm "Esslingen" maps to the right place QID)
- Handle creation of new entries (only audits and improves existing ones)
- Anything beyond English Wikipedia (extend to lvwiki, dewiki, frwiki as needed)

The script is intentionally simple — about 250 lines of Python with two external dependencies. It's a starting point you'll extend as you learn what's actually useful in operation.

### Typical session

```bash
$ python3 artist_pipeline.py "Herberts Siliņš" --year 1926
Searching Wikidata for: Herberts Siliņš
✓ Best match: Q23054868

============================================================
WIKIDATA AUDIT — Q23054868
============================================================
Label:       Herberts Siliņš
Description: Latvian painter (1926-2001)
Wikipedia:   (no enwiki article)

----------------------------------------------------------------
STATEMENTS — present, with reference counts
----------------------------------------------------------------
  P31    instance of                    ✗ no refs
  P21    sex or gender                  ✗ no refs
  P27    country of citizenship         ✓
  P569   date of birth                  ✓

----------------------------------------------------------------
STATEMENTS — missing
----------------------------------------------------------------
  P570   date of death
  P19    place of birth
  P20    place of death
  P106   occupation
  P69    educated at
  P463   member of
  P135   movement
  ...

  No English Wikipedia article exists for this entry.
  → Check other language Wikipedias manually for source data.
```

The audit tells you exactly what needs work without you having to read through the whole Wikidata page. For artists with English Wikipedia articles, the script goes further and generates the proposed edits.

---

## How this integrates with the rest of the operation

The pipeline runs **as part of the cataloguing workflow**, not separately. The right moment is during Phase 3 of the Artist Identity Workflow — the Wikidata stage.

The flow becomes:

1. **(Workflow Phase 1)** Search exhaustively
2. **(Workflow Phase 2)** Gather documentary evidence
3. **(Workflow Phase 3 — automated)** Run `artist_pipeline.py` against the artist name
   - The script's audit tells you what's there
   - The script's QuickStatements file is the proposed edit set
4. **(Workflow Phase 3 — human)** Review the proposals (5–10 min)
   - Verify each is sourced correctly
   - Look up place/school/movement Wikidata items to replace string values with QIDs
   - Reject anything unsupported
5. **(Workflow Phase 3 — submission)** Submit via QuickStatements web interface
6. **(AUTHORITY_CONTRIBUTION_STRATEGY)** Log the contribution

Phases 4–7 of the existing workflow (Wikipedia, Getty ULAN, etc.) are unchanged.

---

## Scaling considerations

For Year 1, the pipeline is run **one artist at a time** during cataloguing. This is fine — your throughput is constrained by client engagements, not by the pipeline.

For Year 2+, two extensions become useful:

**Batch reconciliation.** Once you have CatalogIt or Artwork Archive populated with a client's full artist list, you can run the pipeline over all artists in one pass and produce a single QuickStatements file for review. OpenRefine is the natural tool for this: load the CSV, reconcile names, identify gaps, batch-submit.

**Periodic gap-finding via SPARQL.** Once a quarter, query Wikidata for "artists Ars Accordia has linked to, where statement X is missing" and produce a queue of low-effort improvements. This is how you turn the contribution program into a sustained operation rather than only doing what comes through engagements.

---

## A note on the deliberately limited scope

The pipeline currently only proposes edits for entries that *already exist* on Wikidata. Creating new entries from scratch is a different problem — it requires generating an entire item structure, not just additions. That's a Year-2 extension. For now, the pipeline focuses on the most common case (improving existing entries) and flags missing artists for manual creation following the Artist Identity Workflow.

---

## Setup once, use indefinitely

The setup is minimal:

```bash
pip install requests mwparserfromhell
```

That's it. No services to provision, no accounts to register beyond the existing Ars Accordia Wikidata account, no infrastructure to maintain. The pipeline is a small local tool that does its job in a few seconds and produces output you can review immediately.

Future extensions (place/school QID lookup, multi-language Wikipedia, DBpedia cross-check, batch mode) build on the same foundation. The principle stays the same: assemble automatically; review humanly; submit through QuickStatements.

---

*Maintained as part of the Ars Accordia operations library, alongside ARTIST_IDENTITY_WORKFLOW.md and WIKIDATA_WORKED_EXAMPLE.md.*
