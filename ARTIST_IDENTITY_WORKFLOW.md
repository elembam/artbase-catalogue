# Workflow: Establishing a New Artist's Identity Online

*A playbook for cataloguers — follow when starting work on an artist not found in major authority systems.*

Version 0.1

---

## When to use

You are cataloguing a work by an artist who returns nothing useful in initial Wikidata / Getty ULAN / VIAF lookups. The goal is to either **(a) register the artist** in appropriate authorities so future records can reference them, or **(b) document that they fall below notability** and proceed with internal-only identifiers — both are valid outcomes.

**Time budget**: 30–90 minutes for the standard path. Wikipedia, if attempted, is a separate engagement of 4–20 hours.

---

## Phase 1 — Search exhaustively before creating anything (15 min)

Artists are often present in ways that aren't obvious. Search every authority before assuming an artist is missing.

- **Wikidata** — try the name, alternative spellings, and any pseudonyms; check the artist's birth year as a disambiguator
- **Getty ULAN** — `vocab.getty.edu/ulan`
- **VIAF** — `viaf.org`
- **Your national library** — Libris (Sweden), BnF (France), LoC (US), DNB (Germany), KB (Netherlands)
- **RKD** — for European, especially Dutch/Flemish artists
- **ISNI** — `isni.org`
- **Their gallery's website** — often links to existing authority records
- **Google** — `"Artist Name" + biographical phrase` catches what catalogues miss

Record findings (positive *or* negative) in `cataloguing_notes`. A documented "not found in any system as of [date]" is itself important information.

---

## Phase 2 — Gather documentary evidence (15–30 min)

Without sources, no contribution will hold up. Before creating any entry, assemble:

- Full legal name plus any professional or working names
- Date of birth (and death, if applicable), and locations
- Nationality / country of citizenship
- Primary discipline (painter, sculptor, photographer, mixed-media, etc.)
- **At least two reliable external references** — gallery representation page, exhibition record at a named institution, press article from established publication, auction record, museum collection listing, or catalogue raisonné mention
- A 3–5 sentence biographical summary
- An image of the artist with documented rights (optional but valuable)

**Decision point**: If you cannot find two reliable references, the artist likely does not meet Wikidata notability. Skip directly to Phase 6.

---

## Phase 3 — Wikidata entry (20–40 min)

The workhorse step. Wikidata is the most accessible authority and the most strategically valuable because it cross-references everything else.

1. Sign in at `wikidata.org` (create an account if needed; use a stable identity, not anonymous)
2. *Create a new item*
3. Add **label** (preferred name) and **description** (one factual sentence, e.g. "Swedish painter (born 1972)")
4. Add **aliases** — alternative spellings, maiden names, working names
5. Add core **statements**, each with a reference:
   - `instance of` → human (Q5)
   - `sex or gender`
   - `country of citizenship`
   - `date of birth` *(cite source)*
   - `date of death` if applicable
   - `occupation` — painter, sculptor, photographer, etc.
   - `place of birth`
   - `educated at` if known
   - `represented by` (gallery)
   - `official website`
6. Add **external identifiers** if any exist — gallery ID, Instagram, ORCID, ISNI
7. Save and note the **Q-number**
8. Update the cataloguing system: set `wikidata_qid` to the new `Qxxxxxx`

Once saved, you can immediately link the artwork records to this artist.

---

## Phase 4 — Wikipedia (assess; do only if clearly justified)

Wikipedia is *substantially* harder than Wikidata. Only attempt if the artist has demonstrable coverage in independent secondary sources — multiple reviews in established art publications, solo exhibitions at named institutions, acquisitions by significant museums, awards, or scholarly mentions.

- **If clearly notable**: quote as a separate deliverable (typically €2,000–€5,000). Use the Articles for Creation process. Expect 1–3 rounds of reviewer feedback over 2–6 weeks.
- **If borderline**: don't attempt now. Re-evaluate in 2–3 years.
- **If clearly not yet notable**: skip and document the reasoning.

A Wikipedia article almost always pulls richer data into the existing Wikidata entry, so Wikidata should already exist before Wikipedia is attempted.

---

## Phase 5 — Getty ULAN submission (batched, quarterly)

Do not submit one artist at a time. Maintain a running queue and submit batches.

**Inclusion criteria** for a queued submission:
- Career documented in scholarly or institutional sources
- Life dates verified from primary or secondary sources
- Nationality verified
- Two or more published references beyond gallery materials

**Submission process**:
1. Use Getty's contribution spreadsheet template (`getty.edu/research/tools/vocabularies/contribute.html`)
2. Fill required fields: preferred name, source of name, life dates, nationality, life role
3. Add optional fields supported by sources
4. Submit to **ULAN@getty.edu** with a cover note identifying the contributing institution (us)
5. Track in the submission log; follow up after 30 days if no acknowledgment
6. On acceptance, update `ulan_artist_id` in the cataloguing system

Getty also accepts contributions to **AAT** (concepts) and **TGN** (places) via the same channel where relevant.

---

## Phase 6 — When no public authority is achievable

Two reliable references couldn't be found, or the artist falls below notability across all systems. **This is acceptable.** Document properly:

- Assign an internal authority ID — `artbase_artist_id` = `ARTIST-2026-XXXX`
- Leave `ulan_artist_id`, `wikidata_qid`, `viaf_id` blank
- Add `cataloguing_notes`: *"External authority entries not established as of [date]. Re-evaluate annually."*
- Build the most complete internal biographical record you can: sourced life events, exhibition history, bibliography, contact provenance

**Your house record becomes the de facto authority** for this artist. Treat it accordingly: anyone cataloguing this artist in future — including possibly the artist's eventual catalogue raisonné editor — will work from your documentation first. That is real scholarly value, not a workaround.

---

## Closing checklist

Before marking an artist's authority work complete:

- [ ] All claims in any external entry are sourced
- [ ] Names verified against the artist's own materials or gallery representation
- [ ] No promotional language used in any submission
- [ ] `wikidata_qid`, `ulan_artist_id`, `viaf_id`, `artbase_artist_id` populated where applicable
- [ ] All artworks by this artist in the system now link to the authority record
- [ ] `cataloguing_notes` documents what was created, when, and by whom
- [ ] Time spent recorded for billing reconciliation

---

## Fee guidance for client engagements

| Deliverable | Inclusion |
|---|---|
| Wikidata entry creation | Included in standard cataloguing fee |
| Getty ULAN batch submission | Included; processed quarterly across all clients |
| RKD or national library outreach | Included if the artist qualifies |
| Wikipedia article (when justified) | **Separate engagement, 4–20 hours**, quoted per artist |
| Multi-artist research project | Quoted separately at hourly rate |

---

*Maintained as part of the ArtBase house standards. Update the version line at the top when material changes are made.*
