# Publishing and Using the Ars Accordia Wikidata Schema

*Practical guide to taking the ShEx schema from a text file to a published EntitySchema, and using it operationally.*

Version 0.1

---

## The schema in three sentences

The file `artbase_wikidata_schema.shex` is a Shape Expressions document that defines the structural requirements for any Wikidata entry referenced by an Ars Accordia record. It's the machine-readable expression of the Ars Accordia Wikidata Application Profile. Once published on Wikidata as an EntitySchema, validation tools and automated workflows can use it to check compliance of any Wikidata entry against Ars Accordia standards.

---

## Step 1 — Validate the schema before publishing

Before submitting to Wikidata, sanity-check the ShEx syntax locally.

Two tools work well:

**Online ShEx validator** at `http://rdfshape.weso.es/shexValidate`
- Paste the schema into the "Shapes" tab
- Optionally provide test data in the "Data" tab
- The "Validate" button reports syntax errors

**Command-line tool** `shex.js` (Node.js):

```bash
npm install -g shex
shex-validator -s artbase_wikidata_schema.shex
```

Fix any reported syntax errors before submitting.

---

## Step 2 — Submit the schema to Wikidata

Wikidata EntitySchemas live at URLs like `https://www.wikidata.org/wiki/EntitySchema:E12345`. Submitting one is a normal Wikidata page creation by anyone logged in.

The mechanics:

1. **Sign in** to Wikidata with the Ars Accordia contributor account
2. Navigate to **Special:NewEntitySchema** (`https://www.wikidata.org/wiki/Special:NewEntitySchema`)
3. Fill in the form:
   - **Label (English)**: `Ars Accordia Application Profile for Visual Artists and Artworks`
   - **Description (English)**: `Structural requirements for Wikidata entries referenced by Ars Accordia records — defines artists and artworks per Ars Accordia v0.1 profile`
   - **Aliases**: `Ars Accordia artist schema`, `Ars Accordia artwork schema`, `Ars Accordia Wikidata profile`
   - **Schema text**: Paste the full content of `artbase_wikidata_schema.shex`
4. **Submit**

Wikidata assigns an `E` number (e.g., `E12345`). The published URL becomes the canonical reference for this schema, citable from documentation and tools.

**Before submission**, post a notice on the **Wikidata talk page for WikiProject Visual arts** describing the schema and inviting feedback. This is community-norm and prevents the schema being challenged after publication.

---

## Step 3 — Reference the schema everywhere it matters

Once published, update these documents to reference the EntitySchema URL:

- **ARS ACCORDIA_WIKIDATA_PROFILE.md** — add the EntitySchema URL to Part 3 (currently a placeholder)
- **STRUCTURED_WIKIDATA_WORKFLOW.md** — reference it in the pipeline tooling section
- **artist_pipeline.py** — add a constant pointing to the schema URL
- The Ars Accordia public website (when it exists) — link from the `/standards` or `/about` page

---

## Step 4 — Validate Wikidata entries against the schema

Once published, anyone can validate any Wikidata entry against your schema.

**Web interface**:
- Open the schema page on Wikidata
- Click the **"Validate"** button (or use the ShEx validator gadget)
- Enter a QID to check
- The tool reports which constraints are satisfied and which are not

**Programmatic validation** in the artist pipeline:

```python
import requests

SCHEMA_URL = "https://www.wikidata.org/wiki/Special:EntitySchemaText/E12345"

def validate_entry(qid: str, shape: str = "Ars AccordiaArtist") -> dict:
    """Validate a Wikidata entry against the published Ars Accordia schema."""
    # Use the rdfshape.weso.es API or a local shex.js process
    # Returns a compliance report: which constraints pass, which fail
    ...
```

The pipeline's audit feature in `artist_pipeline.py` can be extended to use this validator for the formal compliance check, rather than the ad-hoc "key properties" list it currently uses.

---

## Step 5 — Build dashboards from the schema

Once the schema is in production, you can produce useful reports:

**"Compliance overview"** — query Wikidata via SPARQL for all items with an Ars Accordia ID property, validate each against the schema, produce a percentage compliance metric per quarter. Published on the `/contributions` page of the Ars Accordia site.

**"Top gaps"** — for items that fail validation, aggregate which constraints fail most often. This tells you where to focus the next batch of improvement work.

**"Backlog burndown"** — track the number of non-compliant items over time. Each improvement session reduces the backlog; the chart goes down and to the right.

These reports are what turn the schema from a passive standard into an active operational instrument.

---

## Maintaining the schema

When the schema needs to change:

1. Edit the source `.shex` file in your operations repository
2. Bump the version in the header comment
3. Update **ARS ACCORDIA_WIKIDATA_PROFILE.md** with the change in the changelog
4. Edit the Wikidata EntitySchema page with the new content
5. Re-run dashboard validation — items that were compliant under the old version may not be under the new one

Wikidata preserves the full edit history of every EntitySchema, so previous versions remain accessible. For substantial changes, you can also publish a parallel schema (e.g., `E12345-v2`) and migrate references gradually.

---

## How the schema fits the rest of the stack

```
   PROFILE LAYER

   ARS ACCORDIA_WIKIDATA_PROFILE.md         (human-readable spec)
              │
              ▼
   artbase_wikidata_schema.shex        (machine-readable spec)
              │
              ▼
   Published EntitySchema E[xxxxx]     (canonical authority on Wikidata)
              │
              │ validated by
              ▼
   ─────────────────────────────────────────────────────────────
   TOOLING LAYER

   artist_pipeline.py                  (assembles proposals)
              │
              ▼
   QuickStatements submission          (human reviews, then submits)
              │
              ▼
   Wikidata entries                    (compliant with profile)
              │
              │ measured against
              ▼
   ─────────────────────────────────────────────────────────────
   REPORTING LAYER

   /contributions page                 (public compliance dashboard)
              │
              ▼
   Annual contribution report          (year-over-year metrics)
```

The schema is the bridge between the human spec (which a person reads) and the operational tooling (which uses it programmatically). Without it, you have documentation; with it, you have an enforceable standard.

---

## Why publish at all (rather than just keep it internal)

Three reasons:

**1. Other contributors can use it.** A partner cataloguer onboarding to Ars Accordia can validate their contributions against the published schema with no additional tooling. The schema is itself the onboarding standard.

**2. The Wikidata community sees the commitment.** A published EntitySchema is a public commitment to a particular quality standard. It's what serious institutional contributors do. The schema is part of what justifies the eventual Ars Accordia ID property proposal — "we have a documented profile, here it is, here's the validator that proves we follow it."

**3. The schema is itself a contribution to shared infrastructure.** Even if no one else uses it directly, it's an example for other small registries thinking about the same problems. Open publication of profiles is how the linked-data community improves over time.

---

## Submission timing

The schema can be published as soon as the profile is finalised — there's no minimum-contribution gate the way there is for property proposals. Two reasonable approaches:

- **Publish early (now)**: get the schema out, refine it as you learn, treat early versions as drafts
- **Publish after first cohort** (~30 days, 20+ records): submit a schema that's already been tested against real contributions

I'd lean toward **publish early** since the schema itself is annotated as v0.1 and the changelog mechanism makes iteration straightforward. Wikidata schemas are expected to evolve.

---

*The published EntitySchema is the formal handoff point between Ars Accordia's internal standards and the public Wikidata infrastructure. Treat it with the same care as any other public-facing technical artefact.*
