# Instruction 19 — Artist Literature References: Match, Validate, Populate

*Hand to Copilot as a single component. Input: the compiled bibliography list (~150 artists, `NAME (dates) ||| 1) citation ~~~ 2) citation`, entries separated by `===`). Goal: populate each artist JSON's existing `sources[]` array (schema already present: `source_id`, `type`, `citation`) — **match-and-report first, write only confirmed matches.** This is Phase 1 only: no Wikidata edits, no QuickStatements. The Wikidata batch (Phase 2) happens after human verification decisions. Where this conflicts with Copilot's instinct, the spec wins — ask before deviating.*

---

## Part A — Parse

1. Split entries on `===`. Header: `SURNAME Firstname (birth[ - death])`. Citations follow `|||`, separated by `~~~`, each prefixed `n)`.
2. **Strip embedded numbering** (`1.`, `2.`) inside citation strings — compilation noise. **Always preserve the raw original string** in the citation object (`raw`).
3. **Concatenated citations**: some single items contain two references run together (known: GAILIS — MAB 1995 + Siliņš 1990 in one string; ZVIEDRIS — MAB 2003 + Zeile 1995). Detect a second `Rīga:`/`Stokholma:`/year pattern mid-string and split into two citations; flag every split for review rather than trusting it silently.
4. Classify each citation:
   - `type: "book"` — printed monographs, lexica, catalogues.
   - `type: "web"` — URLs (russkije.lv, makslinieki.lv, artists' own sites, delfi.lv, diena.lv, tvnet.lv, studija.lv, kulturaskanons.lv…). Record `url` and `accessed: null` (we did not access them; do not invent a date).
   - `type: "periodical"` — journal/newspaper articles (Māksla 1978, Laiks 2004, Klubs 2011, Mākslas Vēsture un Teorija 2019, Ilustrēts Žurnāls 1926).
   - `type: "thesis"` — the one LMA bachelor's thesis (Sietiņš #2).

## Part B — Identify MAB citations and normalize them

"Māksla un arhitektūra biogrāfijās" (MAB) appears in many spellings ("Māksla un Arhitektūra biografijās", "Arhitektūra un māksla biogrāfijās" [inverted — Kozins], with/without editor). Normalize to a structured sub-object:

```json
{ "series": "MAB", "volume": "I|II|III|IV|null", "pages": "48" | "83–84" | null,
  "entry_author": "Burāne I." | null, "entry_title": "Brekte, Jānis" | null }
```

Volume key (authoritative for validation):
| Vol | Year | Ed. | Publisher |
|---|---|---|---|
| I | 1995 | A. Vilsons | Latvijas enciklopēdija |
| II | 1996 | A. Vilsons | Latvijas enciklopēdija |
| III | 2000 | A. Vanaga | A/S Preses nams |
| IV | 2003 | A. Vanaga | A/S Preses nams |

Infer volume from stated volume, else from year, else from editor. If none stated (e.g. "MAB, Rīga, 1995.gads" → vol I by year), record the inference basis. If nothing infers → `volume: null`, flag `vague`.

## Part C — Validate (every citation, mechanically)

1. **Entry-name cross-check (critical):** where the citation contains an entry name (`Author. Name, Name //` pattern), the entry surname MUST match the artist's surname. Known failures, pre-flagged, DO NOT write their citations:
   - **JAUNSUDRABIŅŠ** — cites entry "Maldupe, Vija" (wrong entry)
   - **JURĶELIS** — cites entry "Skulme, Džemma" (wrong entry)
   Report any further mismatches the check finds.
2. **Volume/year consistency:** stated volume+year must agree with the table. Known failures, flag as `inconsistent` (record but mark not-batch-eligible):
   - **IVAŅICKIS** — "3. grāmata … 1995" (vol III is 2000)
   - **KOZINS** — inverted title + "2. grāmata … 1995" (vol II is 1996)
3. **Page sanity:** pages numeric/range; strip soft-hyphen artifacts (`81.­–82`).

## Part D — Match artists to the store

1. Normalize: uppercase surname + firstname + birth year (+ death year when present). Match against artist JSONs (name fields + life dates).
2. **Auto-write threshold ≥95%:** exact surname+firstname+birth-year match, no competing candidate. Anything less — diacritics variance, shared surnames (SKULME ×4, BREKTE ×2, BRENCĒNS ×2, SŪNIŅŠ ×2, TOROPINS ×2, AVOTIŅA ×2, DOBRĀJA/DOBRĀJS), known near-duplicates (`ART-CELMINA-1946` vs `-1946-2`) — goes to the review list, unmatched.
3. **Report before writing:** full match table (list-name → artbase_id, confidence, citations parsed, flags). Present to Jakob; write only after his OK on the flagged subset. Unmatched artists (in list but not in store) → separate report section; do NOT create artist records for them.

## Part E — Write (confirmed matches only)

Per citation, append to the artist JSON's `sources[]`:

```json
{ "source_id": "SRC-MAB-II" | "SRC-<derived>" | null,
  "type": "book|web|periodical|thesis",
  "citation": "<cleaned citation>", "raw": "<original string verbatim>",
  "mab": { …normalized block, when applicable },
  "flags": ["vague"|"inconsistent"|"split"|…],
  "wikidata_batch_eligible": true|false }
```

- Create the four series source records `SRC-MAB-I…IV` (one per volume, per the table) — same pattern as `SRC-HANSABANKA-2007`. Citations with `volume: null` reference the series only, no volume record.
- **`wikidata_batch_eligible: true` ONLY when:** MAB citation with volume + pages + passed all validations. Everything else `false`. (This is the two-tier gate: precise entries are candidates for the later reviewed QS batch; vague/inconsistent/web entries live on the site as bibliography only.)
- Idempotent: re-running must not duplicate citations (match on `raw`).
- Regenerate artist pages afterward so the new "Sources" section renders (bibliographic form; web links as links).

## Part F — Do NOT (Phase 1 boundaries)

- Do NOT generate any QuickStatements or touch Wikidata/Mix'n'match — Phase 2, separate instruction, after Jakob's provenance/verification decision.
- Do NOT write citations for JAUNSUDRABIŅŠ and JURĶELIS (hold until corrected source strings are supplied).
- Do NOT guess a match below threshold, invent page numbers, volumes, or access dates, or "fix" a citation beyond the normalizations specified (raw string always preserved).
- Do NOT create artist records for list entries not in the store.

## Done criteria

1. Match report delivered: N matched ≥95%, M flagged for review, K unmatched — with the full table.
2. All validation flags reported (entry-name mismatches beyond the two known; volume/year inconsistencies; splits).
3. After Jakob's OK: confirmed artists' JSONs populated, `SRC-MAB-I…IV` created, artist pages regenerated with Sources sections, re-run idempotent.
4. A summary count of `wikidata_batch_eligible` citations — the input figure for Phase 2.
