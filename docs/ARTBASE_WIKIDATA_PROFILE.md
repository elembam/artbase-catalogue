# Ars Accordia Wikidata Application Profile

*The formal specification for how Ars Accordia uses Wikidata — what we require, what we recommend, how we structure statements, and how compliance is validated.*

Version 0.1

---

## Why an application profile

Wikidata is open infrastructure — flexible by design, with no enforced schema. That flexibility is its strength and also its weakness for any organisation that needs to use it operationally. Without a profile, you have to make ad-hoc decisions every time you touch an entry: which properties matter? Which references are acceptable? When is a statement "complete enough" to satisfy our needs?

An application profile answers those questions once, in writing. It does three things:

1. **Defines what Ars Accordia requires** from a Wikidata entry before linking to it from an Ars Accordia passport
2. **Defines what Ars Accordia contributes** when working on entries during cataloguing
3. **Defines how compliance is validated** so the pipeline can flag issues automatically

This document is the spec. It's the contract between Ars Accordia's catalogue and Wikidata. It also serves as the model that partners adopt and that the property proposals reference.

---

## Scope

This profile applies to two entity types on Wikidata:

- **Artists** — humans (or, occasionally, anonymous groups) responsible for creating artworks in Ars Accordia records
- **Artworks** — individual visual works that have their own Wikidata items

Other entities (institutions, places, movements, techniques) follow Wikidata's own existing conventions and aren't profiled here — we *use* them, we don't *define* them.

---

## Part 1 — Artist entries

### Required statements

An entry can be linked from an Ars Accordia passport only if it has all of the following. If any are missing, the pipeline flags it; the cataloguer adds the missing statements (with references) before linking.

| Property | Required value | Notes |
|---|---|---|
| `P31` instance of | `Q5` (human) | Or `Q15632617` (fictional human) where appropriate |
| `P21` sex or gender | Any | Most artist entries already have this |
| `P106` occupation | At least one of: `Q1028181` (painter), `Q1281618` (sculptor), `Q33231` (photographer), `Q15296811` (printmaker), `Q1925963` (draughtsman), etc. — see occupation table | Multiple values acceptable |
| `P27` country of citizenship | At least one country | Sometimes multiple if the artist's nationality changed |
| `P569` date of birth | A date (precision: at least year) | If unknown, must have explicit `unknown value` indicator, not just be missing |
| `P570` date of death (if deceased) | A date (precision: at least year) | If unknown but artist is known deceased, use `unknown value` |

Every required statement must have **at least one reference**. Unsourced required statements count as missing.

### Recommended statements

Added when sources allow. Their presence raises an entry's Ars Accordia compliance score but does not block linking.

| Property | Notes |
|---|---|
| `P19` place of birth | Linked to a place item (TGN-equivalent on Wikidata) |
| `P20` place of death | Linked to a place item |
| `P69` educated at | Each institution as a separate statement |
| `P463` member of | Artists' unions, academies, professional bodies |
| `P166` award received | Significant prizes, lifetime stipends, honorific titles |
| `P135` movement | Linked art movement items |
| `P136` genre | Painting genres (landscape, portrait, still life, etc.) |
| `P101` field of work | Discipline (painting, sculpture, printmaking) |
| `P800` notable work | Individual artwork items (linked to Ars Accordia passports if available) |
| `P26` spouse | When relevant to documented provenance or biography |
| `P40` child | When the child is also a notable cultural figure |

### Required external identifiers

Ars Accordia considers an artist entry "fully cross-referenced" only when at least three of these external IDs are present (or have been verifiably searched for and confirmed absent):

| Property | Authority |
|---|---|
| `P245` Getty ULAN ID | Getty Union List of Artist Names |
| `P214` VIAF ID | Virtual International Authority File |
| `P213` ISNI | International Standard Name Identifier |
| `P650` RKDartists ID | Netherlands Institute for Art History |
| `P244` Library of Congress (NACO) | LoC name authority file |
| `P227` GND ID | German Integrated Authority File |
| `P268` BnF ID | Bibliothèque nationale de France |

When `P-Ars Accordia-Artist-ID` is approved as a Wikidata property (see Part 4), it becomes a *required* identifier for any artist with an Ars Accordia record.

### Reference patterns

Every statement contributed by Ars Accordia has at least one reference following one of these standard patterns:

**Pattern A — Citation of an authoritative source.** Used for biographical facts.

```
Statement: P570 (date of death) = 2001-03
References:
  ▸ P248 (stated in): Q[encyclopedia item]
  ▸ P854 (reference URL): https://...
  ▸ P813 (retrieved): 2026-05-27
```

**Pattern B — Citation of a primary record.** Used for external authority IDs.

```
Statement: P245 (Getty ULAN) = 500017249
References:
  ▸ P248 (stated in): Q1520117 (Getty ULAN)
  ▸ P813 (retrieved): 2026-05-27
```

**Pattern C — Citation of Ars Accordia as source.** Used only when Ars Accordia's house records are the primary source (typical for under-documented contemporary artists).

```
Statement: [any]
References:
  ▸ P248 (stated in): Q[Ars Accordia item, once approved]
  ▸ P854 (reference URL): https://arsaccordia.com/a/AR9D2HK4Q8
  ▸ P813 (retrieved): 2026-05-27
```

### Rank usage

Ars Accordia uses Wikidata's statement-rank system explicitly:

- **Preferred** — the most precise / most authoritative value when multiple exist. E.g., date of birth `1926-08-25` is preferred over `1926`.
- **Normal** — the default for most statements
- **Deprecated** — an existing value that is wrong, but we keep it for historical traceability. Always paired with a note in the edit summary explaining why.

### Statement qualifiers

When relevant, Ars Accordia adds qualifiers:

- `P518` (applies to part) — for properties that apply to specific phases
- `P580` / `P582` (start/end time) — for relationships with durations (member of, represented by)
- `P1480` (sourcing circumstances) — for `circa`, `presumably`, `disputed`

---

## Part 2 — Artwork entries

### Required statements

| Property | Required value |
|---|---|
| `P31` instance of | At least one of: `Q3305213` (painting), `Q860861` (sculpture), `Q860792` (photograph), `Q11060274` (print), etc. |
| `P170` creator | Linked to artist Wikidata item |
| `P571` inception | Date of creation (precision: at least year, or year range) |
| `P186` material used | At least one material (oil paint, canvas, marble, etc.) |
| `P195` collection (or `P276` location) | Where the work currently is |
| `P217` inventory number | If held by an institution |

### Recommended statements

| Property | Notes |
|---|---|
| `P180` depicts | Subjects depicted (especially helpful when ICONCLASS isn't sufficient) |
| `P136` genre | Portrait, landscape, still life, etc. |
| `P2079` fabrication method | Painting, casting, etching, etc. |
| `P2049` width / `P2048` height | In structured form, in cm |
| `P276` location | Sometimes paired with `P195` (the institution owns it, but it's on loan to a specific location) |
| `P127` owned by | Current owner if different from holding institution |
| `P1071` location of creation | Where it was made |
| `P1684` inscription | Verbatim transcription of inscriptions |

### Cross-reference to Ars Accordia

When `P-Ars Accordia-Passport-ID` is approved as a Wikidata property, every artwork in Ars Accordia's catalogue with a corresponding Wikidata item gets this identifier added. This is the formal link that lets a Wikidata user click through to the Ars Accordia passport.

---

## Part 3 — EntitySchema

Ars Accordia publishes its profile as a formal Wikidata EntitySchema using Shape Expressions (ShEx). The schema lives on Wikidata at `EntitySchema:E[number]` once submitted.

The schema is machine-readable: anyone can validate any artist or artwork entry against it using the Wikidata schema validator. Tools and dashboards can produce reports like "X% of items linked from Ars Accordia are fully compliant with the Ars Accordia artist profile."

### Artist schema sketch

```shex
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>

<#Ars AccordiaArtist> {
  wdt:P31 [wd:Q5 wd:Q15632617] ;       # instance of human (or fictional human)
  wdt:P21 .  ;                           # sex or gender (any value)
  wdt:P106 IRI+ ;                        # occupation (at least one)
  wdt:P27 IRI+ ;                         # citizenship (at least one)
  wdt:P569 xsd:dateTime ;                # date of birth
  wdt:P570 xsd:dateTime? ;               # date of death (optional)
}
```

A real schema is longer than this and includes cardinality constraints, datatype restrictions, and references-required indicators. The first version of the schema is committed alongside this profile.

---

## Part 4 — Proposed Wikidata properties

Ars Accordia proposes two new properties for Wikidata. Each follows the standard property proposal process (community discussion, vote, technical creation).

### Property 1 — Ars Accordia Artist ID

- **Label**: Ars Accordia artist ID
- **Description**: Identifier for an artist in the Ars Accordia registry of art in private and corporate collections
- **Datatype**: External identifier
- **Format**: `^AR[A-Z0-9]{8}$` (matching Ars Accordia's artist ID scheme)
- **Formatter URL**: `https://arsaccordia.com/a/$1`
- **Allowed values**: One per artist
- **Source**: Ars Accordia Cataloguing Services

Justification: Each authority cross-reference adds a piece of infrastructure to the Wikidata graph. Ars Accordia's records will, over time, include thousands of artist entries — especially in the corporate and private-collection space where Wikidata coverage is currently weak. A dedicated property allows future-proof cross-referencing and prevents the use of generic `P973` (described at URL) which is a less useful structural pattern.

### Property 2 — Ars Accordia Passport ID

- **Label**: Ars Accordia passport ID
- **Description**: Identifier for an artwork in the Ars Accordia registry
- **Datatype**: External identifier
- **Format**: `^AB[A-Z0-9]{8}$`
- **Formatter URL**: `https://arsaccordia.com/p/$1`
- **Allowed values**: One per artwork (artworks with multiple historical IDs use the canonical one)
- **Source**: Ars Accordia Cataloguing Services

Justification: The artwork-level equivalent of the artist ID, allowing Wikidata entries for artworks to cross-reference their Ars Accordia passports.

### Submission timing

Property proposals require justification through demonstrated use. The right time to submit:

- **Artist ID**: After Ars Accordia has ~50 artist records and at least 20 of those have made improvements to existing Wikidata entries — so the community sees concrete contribution before considering a new property. Realistic timing: end of Year 1.
- **Passport ID**: After Artist ID is approved and 200+ artwork records exist. Realistic timing: Year 2.

---

## Part 5 — Validation and compliance scoring

The pipeline (`artist_pipeline.py` and successors) measures compliance per entry:

| Compliance level | Criteria |
|---|---|
| **Fully compliant** | All required statements present, all sourced, at least 3 external IDs present (or confirmed absent) |
| **Substantially compliant** | All required statements present and sourced; fewer than 3 external IDs |
| **Linkable** | Required statements present; some unsourced |
| **Pre-publication** | Missing required statements; not yet linkable from an Ars Accordia passport |

The Ars Accordia contribution log records compliance level per entry at the time of last touch, allowing year-over-year reporting on quality improvement.

---

## Part 6 — Alignment with existing WikiProjects

Ars Accordia's profile aligns with two existing Wikidata WikiProjects:

### Visual arts WikiProject
- Defines artist entity conventions (occupations, movements, education patterns)
- Ars Accordia profile is a superset — adds required cross-reference IDs and statement-sourcing requirements
- We follow their conventions for properties not specifically required by Ars Accordia

### Sum of all paintings WikiProject
- Defines artwork entity conventions (especially paintings)
- Specifies properties for inventory numbers, collections, materials, dimensions
- Ars Accordia profile aligns and adds Ars Accordia-specific identifiers

Alignment means: where existing WikiProjects have made decisions, we follow them. Where they're silent or under-specified, Ars Accordia defines our usage. Where we want changes, we propose them through the WikiProject's discussion process, not unilaterally.

---

## Part 7 — Update procedure for this profile

Changes to this profile follow a defined process:

1. **Proposal** — anyone can propose a change. Document it in the changelog with rationale.
2. **Pipeline impact assessment** — what existing entries would become non-compliant?
3. **Community review** — discuss with the contribution team and (for substantive changes) Wikidata WikiProject participants
4. **Version bump** — change accepted, version incremented, this document updated
5. **Pipeline update** — `artist_pipeline.py` and validation logic updated to match new spec
6. **Bulk re-validation** — existing Ars Accordia contributions re-checked against new profile

Backward compatibility: old profile versions remain available as reference. Entries compliant under v0.1 remain valid until explicitly re-validated under a later version.

---

## Part 8 — What this enables

With this profile in place:

- **The pipeline can fully automate compliance checking.** Every entry the cataloguer touches is automatically scored.
- **Partners can adopt the same standards.** When a partner cataloguer joins the federation, they receive this profile as the spec to follow.
- **Wikidata users see Ars Accordia as a serious contributor.** A documented profile published as an EntitySchema is the calling card that distinguishes serious institutional contributions from drive-by edits.
- **Quality compounds over time.** Each year's compliance metrics improve as we work through the backlog of partially-populated entries.
- **The relationship is reciprocal, not dependent.** Ars Accordia doesn't depend on Wikidata to function; Wikidata doesn't depend on Ars Accordia. We exchange data under documented terms.

---

## Initial actions required

To make this profile real:

- [ ] Adopt this document (publish v0.1 in the operations library)
- [ ] Reference it from `STRUCTURED_WIKIDATA_WORKFLOW.md` and `ARTIST_IDENTITY_WORKFLOW.md`
- [ ] Extend `artist_pipeline.py` to score entries against the required-statement list
- [ ] Draft the ShEx schema (Part 3 sketch is the starting point)
- [ ] Once 50 artist contributions are logged, submit the Artist ID property proposal
- [ ] Establish a presence on the Visual arts and Sum of all paintings WikiProject talk pages

Most of these are zero-cost initially. The pipeline extension is a few hours of code. The property proposals only make sense after demonstrated contribution. The WikiProject engagement is just being visible in the existing community.

---

*This profile is the schema layer of Ars Accordia's Wikidata relationship. It is independent of the Ars Accordia passport format itself (which uses Object ID / LIDO / EODEM) and serves as the bridge between our internal records and the public knowledge graph.*
