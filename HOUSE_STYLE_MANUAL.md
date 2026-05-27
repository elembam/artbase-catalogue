# House Style Manual

*Professional cataloguing standards for European art collections*

Version 0.1 — draft outline

---

## 0. About this manual

**Purpose.** This manual codifies the cataloguing standards used in all our work. It serves three audiences:

- **Internal**: ensures consistency across every collection we catalogue, every collaborator, every year.
- **Clients**: demonstrates the rigour behind the deliverable, justifies the service fee, and gives them a reference for understanding their own catalogue.
- **Successors**: anyone who inherits a catalogue we produced should be able to maintain it without reverse-engineering our conventions.

**Foundation.** The manual rests on four established frameworks:

- **Object ID** (ICOM) for the minimum information required to identify any artwork.
- **Getty Vocabularies** (AAT, ULAN, TGN) for controlled terminology.
- **ICONCLASS** for iconographic subject classification.
- **LIDO 1.1 / EODEM** for standards-compliant export when needed.

These are not invented here. We adopt them, we apply them with discipline, and we document where we deviate.

**Maintenance.** This manual is versioned. Significant changes require a version bump and a note in the changelog at the end. Last reviewed: [date].

---

## 1. Cataloguing principles

The non-negotiable principles that govern every record we produce.

1.1 **Object-centric.** Every record describes one physical artwork. The artwork is the protagonist; everything else (people, places, events) supports its description.

1.2 **Sourced and verifiable.** Every non-obvious assertion has a source. "Acquired by the family in 1928" needs a citation: a letter, a receipt, an inventory entry, an oral history transcript, or an explicit note that the source is the current owner's recollection.

1.3 **Authoritative vocabulary first.** Where a controlled vocabulary exists, we use it. Free text is for what no vocabulary covers.

1.4 **Multilingual where it matters.** Titles and descriptions are recorded in the artist's working language, the client's language, and English at minimum.

1.5 **Conservative attribution.** "Attributed to," "studio of," "circle of," "after," and "follower of" mean different things and are used precisely (see §6.3). Uncertain attributions are flagged, never asserted.

1.6 **Photograph everything.** No record is complete without at least the seven standard views (see §7).

1.7 **Confidentiality by default.** Every record is private unless the client explicitly opts in to a sharing scope.

---

## 2. Artwork Archive account setup

What we configure on every new client account before cataloguing begins.

2.1 **Account tier.** Recommended minimum: Organization plan for institutional clients, Premier for private collectors with custom-field needs.

2.2 **Custom fields installed on every account.** Listed in §4 with their data types and intended use:
- `aat_object_type` (text + URI)
- `aat_medium` (text + URI)
- `aat_technique` (text + URI)
- `ulan_artist_id` (text)
- `ulan_artist_uri` (text)
- `tgn_place_uri` (text)
- `iconclass_codes` (text, comma-separated)
- `wikidata_qid` (text)
- `viaf_id` (text)
- `cat_raisonne_ref` (text)
- `object_id_inscriptions` (text, multiline)
- `object_id_distinguishing_features` (text, multiline)
- `provenance_chain` (text, multiline, structured — see §8)
- `confidentiality_level` (controlled list: Private / Client Portal / Public Site / Europeana-eligible)
- `condition_summary` (controlled list: Excellent / Good / Fair / Poor / Requires conservation)
- `last_reviewed` (date)
- `catalogued_by` (text)
- `cataloguing_notes` (text, multiline — internal use)

2.3 **Tag conventions.** Tags are used for:
- ICONCLASS codes (each code as a separate tag, prefixed `ic:`)
- Period (e.g. `period:Renaissance`, `period:Modern`)
- Movement (e.g. `movement:Impressionism`)
- Region (e.g. `region:Flemish`, `region:Italian-Renaissance`)

Tags are never used for things that belong in a structured field.

2.4 **Location structure.** Locations follow the pattern: `[Site] / [Building] / [Floor] / [Room] / [Specific position]`. E.g. "Headquarters / Tower / 12 / Boardroom / North wall, west of door".

2.5 **Contacts.** All people and organisations associated with a piece are entered as Contacts before being linked to the piece. We never enter "John Smith" as free text in a provenance field if John Smith can be a contact record.

---

## 3. The nine Object ID categories

For each Object ID category, this section defines: which Artwork Archive field holds the data, the conventions we use, and what counts as "complete."

3.1 **Type of object** → `aat_object_type` + Artwork Archive's "Subject/Type" field
3.2 **Materials and techniques** → `aat_medium`, `aat_technique`, Artwork Archive's "Medium" field
3.3 **Measurements** → Artwork Archive's height/width/depth fields, in centimetres (see §5)
3.4 **Inscriptions and markings** → `object_id_inscriptions`
3.5 **Distinguishing features** → `object_id_distinguishing_features`
3.6 **Title** → Artwork Archive's "Title" field (see §6.1 for title conventions)
3.7 **Subject** → ICONCLASS tags + Artwork Archive's "Subject" field
3.8 **Date or period** → Artwork Archive's "Year" / "Date" fields (see §6.2)
3.9 **Maker** → Artwork Archive's "Artist" field, linked to a Contact

Plus the **primary photograph**: the front, plan-view, neutral-background image is always the first uploaded image and is marked as the public/default image.

A record that lacks data in any of these nine categories is **incomplete** and is flagged as such in `cataloguing_notes`.

---

## 4. Controlled vocabularies

4.1 **Getty Art & Architecture Thesaurus (AAT)**
- Where to look it up: `vocab.getty.edu/aat/`
- What we use it for: object type, medium, technique, support material, format
- How we record it: authoritative term in the local field, URI in the custom field
- Examples: oil paint (AAT 300015050), canvas (AAT 300014078), painting (AAT 300033618)

4.2 **Getty Union List of Artist Names (ULAN)**
- Where to look it up: `vocab.getty.edu/ulan/`
- What we use it for: artist identification, biographical anchoring, alternative-name reconciliation
- How we record it: ULAN ID in `ulan_artist_id`, full URI in `ulan_artist_uri`
- For unknown artists: use "Unknown" with a regional/period qualifier (e.g. "Unknown, Flemish, 17th century") and leave ULAN blank

4.3 **Getty Thesaurus of Geographic Names (TGN)**
- Where to look it up: `vocab.getty.edu/tgn/`
- What we use it for: places of creation, places of provenance, current location at city level
- How we record it: URI in `tgn_place_uri`, human-readable name in the relevant Artwork Archive field

4.4 **ICONCLASS**
- Where to look it up: `iconclass.org`
- What we use it for: depicted subject matter, iconographic themes, narrative content
- How we record it: codes in `iconclass_codes` (comma-separated), each code also as a tag prefixed `ic:`
- Coverage: aim for 2–5 codes per representational work; non-representational works may have 0–1

4.5 **Wikidata Q-numbers**
- Where to look it up: `wikidata.org`
- What we use it for: cross-reference hub for famous works, all artists where a Q-number exists, institutions
- How we record it: bare Q-number in `wikidata_qid` (e.g. `Q45585`, not the full URL)

4.6 **VIAF (Virtual International Authority File)**
- For artists, dealers, scholars, donors where a VIAF record exists
- Stored in `viaf_id`

4.7 **When no vocabulary covers it.** Free text in the relevant field, with a note explaining why no authoritative term was used.

---

## 5. Measurement conventions

5.1 **Units.** Centimetres for paintings, drawings, prints, photographs, textiles. Centimetres or millimetres for small objects, prints, jewellery. Always specify the unit, never assume.

5.2 **Order.** Height × Width × Depth. For irregular objects, specify which axis each dimension refers to.

5.3 **What is measured.** For paintings: the support (canvas, panel), not the frame. The frame is measured separately if relevant and recorded as a related-object dimension.

5.4 **Precision.** To the nearest millimetre for objects under 100 cm; to the nearest centimetre for objects over 100 cm. Always record the actual measurement, not a rounded one.

5.5 **Tools.** Steel tape for objects over 50 cm; rigid steel rule for smaller items; calipers for thickness. Never use a fabric tape (stretches).

5.6 **Sight measurements.** When a work cannot be removed from a frame, record the sight (visible) measurement and explicitly note that this is what was measured.

---

## 6. Description writing

6.1 **Title conventions**
- Use the artist's own title if known and documented
- Otherwise use the title established in the literature (catalogue raisonné, major monograph)
- If neither exists, use a descriptive title in quotes (e.g. *"Standing female figure"*)
- Untitled works: "Untitled" with a parenthetical descriptor when helpful
- Multilingual titles: record in the original language and English at minimum

6.2 **Date conventions**
- Single year when documented: `1889`
- Approximate: `c. 1889` (use for ±2 years confidence)
- Range when uncertain: `1885–1890`
- Decade: `1880s`
- Century: `19th century` (only when finer dating is impossible)

6.3 **Attribution conventions** (after the standard scholarly hierarchy)
- **`[Artist Name]`** — by the artist's own hand, documented or unanimously accepted
- **`Attributed to [Artist Name]`** — probable but not certain
- **`Studio of [Artist Name]`** — produced in the artist's studio under direct supervision
- **`Circle of [Artist Name]`** — by a close associate, similar style and period
- **`Follower of [Artist Name]`** — by an unidentified artist working in the manner of, possibly later
- **`After [Artist Name]`** — a copy of a known work by the artist
- **`Manner of [Artist Name]`** — imitates the style, possibly much later

These distinctions matter and are not used loosely. When in doubt, ask. When the source disagrees, cite both.

6.4 **Condition language.** Standardised vocabulary for condition descriptions, with severity levels (see §9.3).

6.5 **Length.** A standard scholarly description is 150–400 words. Condition reports are separate and may be longer.

---

## 7. Photography standards

7.1 **Standard view set (seven minimum)**
1. Front, plan view, neutral background
2. Back / verso
3. Detail of signature, if present
4. Detail of any inscription
5. Detail of any damage or unusual feature
6. Raking light (oblique illumination to reveal surface texture)
7. In situ (showing current display environment)

For sculpture: add views from each cardinal direction (eight standard views). For multi-panel works: each panel individually plus assembled.

7.2 **Resolution and format**
- Capture: RAW format, minimum 24 megapixels for paintings, 36+ for highest-value works
- Archive copy: TIFF, full resolution, sRGB or AdobeRGB depending on use
- Delivery copy: high-quality JPEG, 4000 px on long side
- Working copy in Artwork Archive: JPEG, 2000 px on long side

7.3 **Colour reference.** Every photography session includes a colour reference card (X-Rite ColorChecker or equivalent). The reference shot is archived alongside the artwork shots.

7.4 **Lighting.** Even, diffused, daylight-balanced. Two-point minimum at 45° to the work's surface for paintings. No flash on the work directly.

7.5 **File naming.** `[clientCode]_[artworkID]_[viewType]_[YYYYMMDD].ext`
Examples: `BANK01_AW0042_front_20260315.tif`, `BANK01_AW0042_signature_20260315.jpg`

7.6 **Conservation imaging.** UV, IR, X-ray imaging is not part of standard service. Available on request, typically subcontracted to a partner conservator.

---

## 8. Provenance research

8.1 **What provenance means.** The documented chain of ownership of a work from creation to the present day, with sources for each transition.

8.2 **Structure of a provenance entry.**
- **Owner** (linked to a Contact)
- **Date acquired** (and source of that date)
- **Manner of acquisition** (purchase, gift, inheritance, commission, exchange, looting/restitution event)
- **Date disposed** (when known)
- **Source** (the document or testimony establishing this entry)
- **Notes** (uncertainty, gaps, disputes)

8.3 **Recording in Artwork Archive.** Provenance is recorded in `provenance_chain` as a structured multi-line text with one entry per line, following the format:
```
[YYYY or YYYY-YYYY] | [Owner name] | [Manner] | [Place] | [Source citation]
```

8.4 **Gaps.** Documented gaps are explicit: `[1940–1945] | UNKNOWN | gap during WWII | — | no records identified, see notes`.

8.5 **Sensitive periods.** Works that were in continental Europe between 1933 and 1945 receive a **looting check**: confirmation against the Art Loss Register, ERR Project records, and the relevant national restitution databases. The result of this check is recorded even if negative.

8.6 **Living persons in provenance.** Personal data of living previous owners is treated under §11 (GDPR).

---

## 9. Condition reporting

9.1 **Levels of detail**
- **Condition summary** (one of five levels) — every record
- **Condition note** (1–3 sentences) — every record
- **Full condition report** (multi-page document) — on request, typically for insurance or loan

9.2 **Standard observations checklist.** A checklist of conditions to look for on every type of work (paintings, works on paper, sculpture, photographs, textiles, etc.) so that nothing is missed. Detailed checklists appear in Appendix B.

9.3 **Vocabulary.** Standardised condition vocabulary with severity ratings:
- *cracking* (hairline / minor / major / structural)
- *flaking* (incipient / active / extensive)
- *foxing* (minor / moderate / extensive)
- *abrasion*, *retouching*, *overpainting*, *staining*, *tide marks*, *cockling*, *tears*, *losses*

Each term has a precise definition in Appendix C.

---

## 10. Deliverables

What the client receives at the end of an engagement.

10.1 **Populated Artwork Archive catalogue.** Every record complete per §3, photographed per §7, with all custom fields filled.

10.2 **Object ID PDF binder.** One page per artwork in the Object ID format, suitable for insurance and law enforcement use. Generated from Artwork Archive CSV via our pipeline.

10.3 **Condition summary report.** One PDF covering condition observations across the collection, flagging works requiring attention.

10.4 **Provenance dossier.** One PDF per artwork where provenance research was substantive, with citations and source documents appended.

10.5 **LIDO export** (on request). Standards-compliant LIDO 1.1 XML for the records flagged for it. EODEM profile output for museum loan exchange.

10.6 **Handover documentation.** A summary of what was done, what conventions were used (this manual + any client-specific variations), and recommendations for ongoing maintenance.

10.7 **Annual review** (offered separately). Update of measurements, condition, location changes, new acquisitions; refresh of valuations through partner appraisers.

---

## 11. Confidentiality and GDPR

11.1 **Default privacy.** No record is shared outside Artwork Archive's account without explicit per-record opt-in via the `confidentiality_level` field.

11.2 **Personal data in provenance.** Living previous owners are personal data under GDPR. We document with care, retain only what is necessary, and never include personal contact details in catalogue records.

11.3 **Cutoff convention.** Provenance involving people known or likely to be living is reviewed for GDPR compliance before any export. Pre-1950 provenance is generally treated as historical record; later than that, treated as personal data unless the person is documented as deceased or the information is already in the public domain.

11.4 **Client confidentiality.** No information about Client A's collection is ever shared with Client B. This includes anecdotes, learnings, and methodology refinements. Each engagement is sealed.

11.5 **Subprocessor disclosure.** Artwork Archive (the SaaS) is a subprocessor. Clients are informed in writing that their data is hosted in the United States by Artwork Archive Inc., with a link to Artwork Archive's privacy and security documentation, and the option to refuse this arrangement (in which case the engagement is declined or alternative software is proposed).

---

## 12. Quality control

12.1 **Two-pass review.** Every record is catalogued by one person and reviewed by another (or by the same person on a different day after a 48-hour gap).

12.2 **Completeness checklist.** Before a record is marked complete, it passes the checklist in Appendix D.

12.3 **Validation.** For records destined for LIDO export, the LIDO XML output is validated against the official XSD and the EODEM Schematron rules.

12.4 **Periodic audit.** A random 10% of records from each completed engagement is re-checked at handover.

---

## Appendices

**A. Custom field installation procedure for Artwork Archive** — step-by-step

**B. Condition observation checklists** — by object type

**C. Condition vocabulary glossary** — definitions of every term used

**D. Record completeness checklist** — pre-handover quality gate

**E. Photography setup procedures** — equipment, lighting diagrams, workflow

**F. Glossary** — terms used in this manual

**G. Bibliography** — Object ID documentation, ICOM resources, Getty vocabulary documentation, ICONCLASS resources, LIDO/EODEM specifications, CIDOC training materials, conservation reference works

**H. Changelog** — version history of this manual

---

*This manual is a working document. Suggestions, corrections, and additions are welcomed and reviewed quarterly.*
