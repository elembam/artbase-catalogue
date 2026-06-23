# Instruction 15 — LNMM Cleanup, the First Wikidata Give-Back, and the Sample Dossier

*Hand to Copilot as an operational runbook. It builds on Instruction 9 (privacy), 10 (cross-reference status), 11–13 (scoring), and 14 (the LNMM cataloguing process). **The cleanup in Part A is the shared precondition** for both the Wikidata give-back (Part B) and the dossier (Part D) — do it first. **No Wikidata or Mix'n'match edit is ever auto-committed: Copilot prepares review-then-run files; a human approves and runs them.** Where this conflicts with Copilot's instinct, the runbook wins — ask before deviating.*

---

## Why this order

The whole value of the Wikidata give-back is **credibility**, so pushing a wrong fact is worse than pushing nothing — it damages the thing we're building. The same clean records are what the sample dossier shows an advisor. So the data cleanup is not a separate chore; it is the foundation both other deliverables stand on. **Clean first, then contribute, then package.**

---

## Part A — Clean the LNMM data (do this first)

The six LNMM works (`artbase_export/data/artworks/AA/LV/LNMA/001, 004, 006, 012, 017, 019.json`) and `COL-LNMM.json` must be trustworthy before anything leaves the building.

**A1 — Fix the Hūns attribution (priority).** The records list artist "Ādams Hūns" — there is no such painter; the name conflates *Ādams Alksnis* and *Kārlis Hūns*. The QID used, `Q4152126`, is **Kārlis Hūns**.
- `017` (*Young Gypsy Woman*): the QID is correct and the work is genuinely by Kārlis Hūns — **fix only the name field to "Kārlis Hūns."**
- `012` (*Folk Festival at Kokmuiža*): **verify the attribution** against the museum record / Wikipedia / Wikidata. If it is by Kārlis Hūns, set name + `Q4152126`. If it is by another artist, correct both. **If it cannot be confirmed, flag it and exclude `012` from the Wikidata batch (Part B) until it is** — never publish an unverified attribution.

**A2 — Verify every artist QID and work→artist match against live Wikidata.** Rozentāls `Q975168` is confirmed correct (the spec's old `Q466052` was wrong). Verify Tīdemanis `Q4457149` and Feders `Q1977258`, and confirm each of the six works is actually by its stated artist. Record the verification. Anything unconfirmed is flagged and held back from Part B.

**A3 — Verify the provenance citations are real.** Each record cites `SRC-LNMM-PORTRAITS-2009` with page numbers. Confirm those pages and provenance statements are **real** (from the actual book), not generated to fill the field. **If a citation cannot be verified, remove it and mark that provenance section a gap** — let the score fall honestly. A true 70 beats an invented 88.

**A4 — Fix the score arithmetic.** In `build_collection_score.py`: (a) compute `ars_accordia_score` as the **sum of the rounded integer passport scores** (so the displayed per-work scores add up to the headline — per Instruction 13, Σ passport scores = Ars Accordia Score); (b) replace banker's rounding with **round-half-up** in `build_passport_score.py` so x.5 values round intuitively. Recompute. (Related: reconcile the two Mona Lisa pages — `AP-2026-000001` should match the populated demo version rather than scoring 60/grey — but this is secondary to the LNMM work.)

**A5 — Recompute.** Re-run `build_passport_score.py --all` and `build_collection_score.py COL-LNMM`; confirm `--check` passes (Σ = headline). The website will reflect the corrected numbers in Part C.

---

## Part B — The first Wikidata give-back batch (human-reviewed QuickStatements only)

Run on the **cleaned** six works. Copilot **generates** the files into `artbase_export/data/contributions/`; a human reviews and runs them. Copilot does **not** commit to Wikidata or Mix'n'match.

**B0 — Confirm the two gating QIDs** (without these, the citations and collection statements cannot be written):
- the **LNMM portraits book** Wikidata item for `SRC-LNMM-PORTRAITS-2009` → needed for the `S248` reference. *Confirm it exists or prepare a create-the-book QS first.*
- the **LNMM institution** Wikidata item → needed for `P195` (collection) on artwork items.
Parameterise the batch on these two QIDs; if either is missing, leave a clear placeholder and flag it — do not invent a QID.

**B1 — Generate the QuickStatements batch** (`lnmm_batch_01_<date>.qs`):
- **Lead with book-sourced facts**: for each artist/work, statements (date, creator, medium, etc.) sourced with `S248 <book-QID> + S304 "<page>"` — never citing Ars Accordia.
- **Create the missing artwork items** (works without their own Wikidata item) with a minimal block: `P31` (painting `Q3305213`) · `P170` creator `<verified artist QID>` · `P571`/`P577` inception · `P186` material · `P2048`/`P2049` dimensions · `P195` collection `<LNMM-QID>` · `P217` inventory number · label + description, with `S248/S304` on sourced statements.
- **Pace the P973 self-links** (`described at URL` → arsaccordia.com) — do not mass-add; lead with the sourced facts.

**B2 — Prepare Mix'n'match #8050 registrations** for any artist/work not already matched in the catalogue (https://mix-n-match.toolforge.org/#/catalog/8050) — as a review-then-submit list.

**B3 — Start the contribution log.** Append this batch to a running `data/contributions/CONTRIBUTION_LOG.md` (date, items, statements, references, status). The track record is the asset; record it so the cadence is visible and sustained.

**B4 — Close the loop after the human runs the batch.** Once the new artwork Wikidata items exist, update each passport's `authority_links` with its **work-level** Wikidata Q (in addition to the artist links), and recompute (Part A5). Scores will rise as works gain a second/independent public cross-reference — this is expected and correct.

**Not in scope:** the Wikidata **ID-property proposal**. It is deferred until the sourced edit-history is substantial; proposing it now is premature.

---

## Part C — Surface it on the website (LNMM and Hansabanka)

**C1 — LNMM collection page** (`collections/lnmm/index.html`), as a scored collection page (Instruction 12):
- the corrected **Ars Accordia Score / average standard / works documented / band**, and the gap map (prefer **average fill** per dimension over mere presence, so it points at the real next step rather than reading a flat 100%);
- per-work rows with the green/amber/grey **cross-reference status** badge, each linking to its work's Wikidata item where one now exists;
- a line: *"N works contributed to Wikidata · registered in Mix'n'match #8050"*;
- the honest framing ("works documented by Ars Accordia," no coverage %) and the `/method/` link.

**C2 — Each LNMM passport page** (§ 02): show the artist Wikidata Q + ULAN **and** the new artwork Wikidata item link, so the cross-references are visible and clickable.

**C3 — Hansabanka, in parallel (a small finishable slice).** Apply the same end-to-end treatment to **5–6 Hansabanka works** so the corporate collection also shows on the site as a scored, cross-referenced collection with its own page. Differences to respect:
- the Hansabanka catalogue already has a Wikidata item — **`Q139986317`** (`SRC-HANSABANKA-2007`) — usable for `S248`, so this slice is less blocked than LNMM;
- **living-artist privacy (Instruction 9):** these are contemporary works — keep owner/personal data private, lead with catalogue-sourced facts, and be cautious creating items about living people; when in doubt, hold for review.
Produce the Hansabanka slice's passports, score, collection page, and its own (human-reviewed) Wikidata/Mix'n'match batch the same way.

---

## Part D — The sample dossier (the advisor show-piece)

**D1 — Create `scripts/build_dossier.py`.** It reads a collection's computed `score` block (Instruction 11) and its member passports and renders a **Collection Documentation Dossier** — one self-contained HTML file, printable to PDF, in the brand language (Fraunces / Public Sans / JetBrains Mono, paper/oxblood/gilt). Sections:
- **Cover** — collection name, Ars Accordia Score, average standard, works documented, band, date; clearly marked *"Sample — demonstration of an Ars Accordia documentation dossier."*
- **Summary** — what the score means, the band, the `/method/` reference (plain language).
- **Gap map** — where the records are thin (the next-work plan).
- **Per-work records** — for each passport: identity, the authority cross-references (Wikidata/ULAN/artwork item), sourced provenance, structured-data/export note, and the cross-reference status badge.
- **Exports** — a note that each record is available as Schema.org JSON-LD and LIDO/EODEM for insurance, loans, and museum exchange.

**D2 — Generate the dossiers:** the cleaned **LNMM** dossier (and the **Hansabanka-slice** dossier from C3). These are the artifacts for advisor conversations.

**D3 — Surface it on the site:** add a *"Download the documentation dossier"* link on each scored collection page (or a `/dossier/<collection>/` route), so the dossier both shows on the website and stands alone as the show-piece.

---

## Guardrails (non-negotiable)

- **No score is hand-set** — computed from records, recompute on change, `--check` must pass.
- **No Wikidata/Mix'n'match edit is auto-committed** — Copilot prepares review-then-run files only; a human approves and runs them.
- **Never cite Ars Accordia as a source** on Wikidata — cite the books/authorities; AA's credit accrues through edit history.
- **Count cross-references, don't grade them** — no source ranked above another.
- **Reconcile before creating** — check Wikidata, Mix'n'match #8050, and candidate QIDs to avoid duplicate items.
- **Verify before publishing/contributing** — no unconfirmed attribution or QID goes to the website or to Wikidata.
- **Living-artist privacy** for the Hansabanka slice (Instruction 9).
- **Pending is not published** (Instruction 10).

---

## Sequencing (so the core is doable this week)

1. **This week's core:** Part A (LNMM cleanup) → Part B1–B3 (prepare the LNMM batch + Mix'n'match + log) → C1/C2 (refresh the LNMM page). This starts the credibility engine on clean data.
2. **In parallel / next:** Part D (the dossier generator + LNMM dossier) — the advisor artifact.
3. **Follow-on:** Part C3 (Hansabanka slice) and its batch; Part B4 (close the loop once the human has run the batch).

---

## Items to confirm before running (human)

- Wikidata QID for the **LNMM portraits book** (`SRC-LNMM-PORTRAITS-2009`) — for `S248`.
- Wikidata QID for **LNMM the institution** — for `P195`.
- The corrected **`012` attribution** (Folk Festival at Kokmuiža).
- Whether the **provenance page citations are real** (A3).
- Which **5–6 Hansabanka works** form the slice (C3).

---

## Done criteria

1. The six LNMM records have correct attributions and verified QIDs; provenance citations are confirmed real or marked as gaps; scores recompute consistently (`--check` passes, displayed scores sum to the headline).
2. A human-reviewed QuickStatements batch (book-sourced facts + artwork-item creations) and a Mix'n'match #8050 registration list are prepared in `data/contributions/`, with the contribution log started — nothing auto-committed.
3. The LNMM collection page shows the corrected score, the gap map, per-work cross-reference badges with Wikidata links, the Mix'n'match line, and the `/method/` link; passports show their artwork Wikidata links after the batch is run.
4. A Hansabanka slice is documented, scored, surfaced on its own collection page, and has its own prepared (privacy-respecting) contribution batch.
5. `build_dossier.py` generates a clearly-labelled sample dossier for LNMM (and the Hansabanka slice), linked from the collection page(s).
