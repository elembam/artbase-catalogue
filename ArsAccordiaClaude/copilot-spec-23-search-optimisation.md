# Instruction 23 — Search Optimisation from Search Console Data

*Hand to Copilot as a site-wide metadata task (numbering is yours). Grounded in the real Google Search Console export for arsaccordia.com, 3 months to 2026-09-05. This is **not** a guess at what might help — every change below is aimed at a query or page that already appears in the data. The standing discipline holds: **no invented data, no valuation or authentication claims, no keyword stuffing.** Where this conflicts with Copilot's instinct, the spec wins — ask before deviating.*

---

## The diagnosis (read first — it decides everything below)

Over three months: **~1,000 impressions, ~10 clicks (~1% CTR)** — but the **average positions are good**: homepage 4.7, `/collections/lnmm/` **4.56**, `/artists/latvia/` 12.6, and dozens of artist pages between 5 and 15.

At position 4–5 a page normally earns 5–10% CTR. We earn ~0. **Google already ranks us; searchers see our result and choose something else.** That is a titles-and-snippets problem, not a ranking problem — and it is fixable with template changes that propagate to ~700 pages.

Three pieces of evidence:

| Evidence | Reading |
|---|---|
| `/collections/lnmm/` — **187 impressions, position 4.56, 0 clicks** | Our biggest page, on page one, converting nothing |
| `jekabs kazaks "three old women" 1916 dimensions` — **19 impr. @ pos 3.53**, plus 18 more @ 3.5 for the same query reworded | Searchers want an artwork's **attributes**; our snippet shows none, so they click Wikipedia |
| `sandra krastiņa official website` — 11 impr. @ 8.6, 0 clicks | Title reads like a database ID, so the result looks irrelevant |

**Principle for every template below: put the answer the searcher wants *into the title and description*.**

---

## Part A — Title templates (highest-value change)

Replace internal-ID-style titles. Target ~55–60 characters; front-load the identifying facts. All fields **conditional** — omit what a record lacks, never fill with placeholders.

**Artist pages** (`/artists/ART-*.html`)
```
{Name in Latvian form} ({birth}–{death}) — Latvian {painter|graphic artist|sculptor} | Ars Accordia
```
- Use the **Latvian name form with diacritics** as primary (queries arrive that way: `ģederts eliass`, `voldemārs irbe`, `kārlis hūns`).
- Where an English/transliterated form differs, include it in the meta description, not the title.
- Omit the dash-range if dates are unknown; never guess a date.

**Passport / artwork pages** (`/AP-*.html`)
```
{Title} ({year}), {Artist} — {medium}, {dimensions} | Artwork Passport
```
- This is the direct answer to the Kazaks-type query. If `dimensions` or `year` are absent from the record, drop them from the title — do **not** invent.

**Collection pages** (`/collections/*/`)
```
{Collection name} — {N} works documented | Ars Accordia
```

**Hub pages**
- `/artists/latvia/` → `Latvian Painters & Artists — Documented Catalogue | Ars Accordia`
- `/artists/` → `Artists — Documented Records | Ars Accordia`
- `/artworks/` → `Artworks — Documented Records | Ars Accordia`

**Insights articles** — keep the titles already specified in the insights handover.

---

## Part B — Meta description templates

~150–160 characters. **Contain the facts a searcher is looking for**, in plain prose. Conditional fields throughout.

**Artist page**
```
{Name} ({birth}–{death}), Latvian {role}. {N} works documented by Ars Accordia,
cross-referenced to Wikidata, Getty ULAN and public authority records.
```
- If the artist has **0 catalogued works**, omit the count entirely — do not write "0 works".

**Passport page**
```
{Title}, {year}, by {Artist}. {Medium}, {dimensions}. {Collection}. Permanent
Artwork Passport {AP-ID} with sourced provenance and authority cross-references.
```
- Lead with the object facts — that is what converts the attribute queries we already rank for.

**Collection page**
```
{N} works from {collection}, documented to standard by Ars Accordia — identity,
sourced provenance, and cross-references to public authority records.
```

---

## Part C — Fix `/collections/lnmm/` (187 impressions, 0 clicks)

1. In Search Console, filter Performance → Pages → this URL to list **its** queries; expect artwork-attribute searches like the Kazaks one. Report them.
2. Rewrite its title/description per Part A/B.
3. **Surface the individual works on the page** with their identifying data (title, artist, year, medium, dimensions) and links to each passport — so the page can actually answer the artwork queries it is ranking for, and so it passes link equity down to the passports.

---

## Part D — Build out `/artists/latvia/` (70 impressions @ 12.6)

Queries `famous latvian artists` and `latvian painters` already appear. This hub is close to a strong position:
- A real introduction (2–3 paragraphs) on Latvian painting and what this catalogue covers — substance, not a bare list.
- Group artists sensibly (by period or alphabetically) with life dates beside each name.
- Link from the homepage and from every artist page back up to the hub.

---

## Part E — Latvian-language metadata (low competition, real demand)

The data shows Latvian-language queries: `elita patmalniece biogrāfija`, `latviešu gleznotājs 1887-1975` (a search by **life dates**).
- Include the Latvian name form and life dates prominently in artist page titles/descriptions (Part A already does this).
- Add a short Latvian-language line to artist page descriptions where feasible (e.g. `Latviešu gleznotājs ({birth}–{death}).`).
- Do **not** machine-translate whole pages; a bad translation costs more than it gains.

---

## Part F — URL and ID consistency audit

- `/artists/ART-KROLLIS-1932` appears **without** `.html` while others have it → confirm one canonical form site-wide and that `rel=canonical` points to it (this is the earlier canonical issue resurfacing).
- `ART-KRIVENKOVA-TATJANA.html` breaks the `ART-NAME-YYYY` scheme (no birth year) → report it; fix the record if the year is known, otherwise flag, don't invent.
- Re-run the sitemap after any URL change.

---

## Guardrails

- **Never invent a field to fill a template.** Missing dimensions, dates, or roles are simply omitted. A short honest title beats a padded one.
- **Never imply we are an artist's official site.** Queries include `... official website`; our description says what the page *is* — a documented record of catalogued works — never "official".
- **No valuation or authentication language** anywhere in titles or descriptions.
- **No keyword stuffing.** One natural title, one readable sentence. Titles must match what the page actually contains.
- **Titles must match visible page content** — divergence reads as cloaking.

---

## Done criteria

1. Title and meta-description templates implemented for artist, passport, collection, hub, and insights page types; all fields conditional; all ~700 pages regenerated.
2. Spot-check 10 pages: titles ≤ ~60 chars, descriptions ~150–160, no empty placeholders, Latvian diacritics correct.
3. `/collections/lnmm/` rewritten and now lists its works with identifying data + passport links; its GSC queries reported.
4. `/artists/latvia/` expanded with real introductory content and linked from homepage + artist pages.
5. URL/ID inconsistencies reported and canonical form confirmed; sitemap regenerated.
6. Request indexing in Search Console for: homepage, `/collections/lnmm/`, `/artists/latvia/`, the three insights articles, and 5–10 top artist pages.

---

*Follow-on (not this task): the query data names the next insights articles — "what does attributed to mean in art", "certificate of provenance", "establishing provenance", "what is a catalogue raisonné". Same cluster as the provenance article already earning impressions; they will lift each other.*
