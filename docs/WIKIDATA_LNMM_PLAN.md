# Wikidata Upload Plan — LNMM Collection

*Last updated: 2026-06-14*

Source: Latvia National Museum of Art (LNMA) open data — 354 works, 55 artists.

The goal is to make LNMM artists and their major works discoverable on Wikidata, linking back to Ars Accordia artist pages via **P973 (described at URL)**. This creates the third-party-verifiable authority trail that supports the Knowledge Panel strategy.

---

## What we have

| Status | Artists | Action needed |
|---|---|---|
| Confirmed Wikidata QID in ArtBase | 5 | Add P973 to their Wikidata items; verify data |
| In ArtBase, Wikidata search needed | 3 | Find QID, update ArtBase record, add P973 |
| Not in ArtBase at all | 47 | Create ArtBase artist record + find/create Wikidata item |

**Total top-priority artists (by LNMM representation):** 16 listed below.

---

## Phase 1 — Confirmed artists: add P973 and verify (do this week)

These 5 artists already have confirmed Wikidata QIDs in ArtBase. The only action needed is to open each Wikidata item, add **P973** pointing to the Ars Accordia artist page, and verify key facts are present.

| Works | Artist | QID | Ars Accordia page |
|---|---|---|---|
| 39 | Janis Rozentāls | [Q975168](https://www.wikidata.org/wiki/Q975168) | arsaccordia.com/artists/ART-ROZENTALS-1866.html |
| 25 | Kārlis Padegs | [Q4342040](https://www.wikidata.org/wiki/Q4342040) | arsaccordia.com/artists/ART-PADEGS-1911.html |
| 19 | Jāzeps Grosvalds | [Q4150307](https://www.wikidata.org/wiki/Q4150307) | arsaccordia.com/artists/ART-GROSVALDS-1891.html |
| 18 | Vilhelms Purvītis | [Q2663470](https://www.wikidata.org/wiki/Q2663470) | arsaccordia.com/artists/ART-PURVITIS-1872.html |
| 18 | Romans Suta | [Q6711504](https://www.wikidata.org/wiki/Q6711504) | arsaccordia.com/artists/ART-SUTA-1896.html |

**For each:** go to the Wikidata item → Add statement → P973 (described at URL) → paste the Ars Accordia artist page URL.

Also verify these standard properties are present on each item:
- P31 (instance of): Q5 (human)
- P21 (sex or gender)
- P27 (country of citizenship): Q211 (Latvia)
- P106 (occupation): Q1028181 (painter) or appropriate
- P569 (date of birth), P570 (date of death)
- P19 (place of birth), P20 (place of death) if known

**QuickStatements batch for P973 additions** (paste at https://quickstatements.toolforge.org/):

```
Q975168	P973	"https://arsaccordia.com/artists/ART-ROZENTALS-1866.html"	S854	"https://arsaccordia.com"
Q4342040	P973	"https://arsaccordia.com/artists/ART-PADEGS-1911.html"	S854	"https://arsaccordia.com"
Q4150307	P973	"https://arsaccordia.com/artists/ART-GROSVALDS-1891.html"	S854	"https://arsaccordia.com"
Q2663470	P973	"https://arsaccordia.com/artists/ART-PURVITIS-1872.html"	S854	"https://arsaccordia.com"
Q6711504	P973	"https://arsaccordia.com/artists/ART-SUTA-1896.html"	S854	"https://arsaccordia.com"
```

---

## Phase 2 — Search needed: resolve QIDs (this week)

These 3 artists are in ArtBase but their Wikidata IDs are unresolved. Search Wikidata for each, update the ArtBase JSON record, regenerate the artist page.

| Works | Artist | Lifespan | Search hint |
|---|---|---|---|
| 10 | Kārlis Hūns | 1830–1877 | Baltic German painter, trained Munich — likely exists as "Karl Hün" |
| 9 | Jūlijs Feders | 1838–1909 | Latvian landscape painter — search "Julius Feders" or "Julius Feders painter" |
| 7 | Jānis Tīdemanis | 1897–1964 | Latvian modernist — likely exists, search "Jānis Tīdemanis" |

**For each:**
1. Search `https://www.wikidata.org/w/index.php?search=<name>` and `https://www.wikidata.org/w/index.php?search=<latinised name>`
2. Confirm match via birth/death year and nationality
3. Update `artbase_export/data/artists/<ID>.json`: set `authority_links.wikidata.id` and `authority_links.wikidata.status: "confirmed"`
4. Regenerate artist page: `python3 scripts/artist_profile_generator.py ART-HUNS-1831` (etc.), then `cp passports/artists/<ID>.html artists/<ID>.html`
5. Add P973 to the confirmed Wikidata item

---

## Phase 3 — Missing from ArtBase: create records + Wikidata items (next 2 weeks)

These 8 high-representation artists have no ArtBase record at all. Priority order by LNMM work count.

| Works | Artist | Lifespan | Notes |
|---|---|---|---|
| 28 | Johann Walter | 1869–1932 | Baltic German painter; may appear as "Jānis Valters" in Latvian sources — likely has Wikidata item |
| 20 | Jēkabs Kazaks | 1895–1920 | Expressionist, died young; probably has Wikidata item |
| 16 | Rūdolfs Pērle | 1875–1917 | Graphic artist; search "Rūdolfs Pērle" and "Rudolf Perle" |
| 12 | Pēteris Krastiņš | 1882–1942 | Painter; search Wikidata |
| 11 | Ādams Alksnis | 1864–1897 | Early Latvian painter, died young |
| 9 | Rihards Zariņš | 1869–1939 | Painter and graphic artist; likely has Wikidata item |
| 7 | Teodors Ūders | 1868–1915 | Painter |
| 5 | Gustavs Klucis | 1895–1938 | Constructivist, executed in Stalin purges — very likely has Wikidata item |

**For each:**
1. Search Wikidata for existing item
2. If found: note QID, create ArtBase JSON record with `status: "confirmed"`
3. If not found: create minimal Wikidata item (see template below), note QID
4. Create ArtBase artist record JSON in `artbase_export/data/artists/`
5. Regenerate artist page

**Note on Johann Walter / Jānis Valters:** This is likely the same person as the painter known in Latvia as Jānis Valters (1869–1932). Check Wikidata for Q-number — if there is one, this links 28 works immediately.

**Note on Gustavs Klucis:** A prominent Constructivist artist internationally known. Almost certainly has a Wikidata item with substantial data. Priority.

---

## Phase 4 — Artwork items: create Wikidata items for exemplary works

After the artists are resolved, create Wikidata items for the top 5–8 LNMM works to catalogue as exemplary passports. Start with Rozentāls (largest representation, confirmed QID).

### Priority artworks (by artist prominence + data completeness)

| Title | Artist | Date | Cat. No. | Google Arts URL |
|---|---|---|---|---|
| From Church (After the Service) | Janis Rozentāls | 1894 | VMM GL-55 | https://artsandculture.google.com/asset/.../ZAHd0RC6Nrk3jw |
| Winter | Vilhelms Purvītis | 1910 | VMM GL-1568 | https://artsandculture.google.com/asset/.../fAF_qZJTFzsvJw |
| Carousel | Jānis Tīdemanis | 1932 | VMM GL-2822 | https://artsandculture.google.com/asset/.../0wEC4mFwbh4HEA |

### Wikidata item template for an LNMM artwork

```
CREATE
LAST	P31	Q3305213	/* instance of: painting */
LAST	Len	"From Church (After the Service)"
LAST	Den	"1894 painting by Janis Rozentāls"
LAST	P170	Q975168	/* creator: Rozentāls QID */
LAST	P571	+1894-00-00T00:00:00Z/9	/* inception: 1894 */
LAST	P127	Q675836	/* owned by: LNMA (verify QID) */
LAST	P276	Q675836	/* location: LNMA */
LAST	P973	"https://arsaccordia.com/AP-2026-000NNN.html"	/* after passport issued */
LAST	P856	"https://artsandculture.google.com/asset/.../ZAHd0RC6Nrk3jw"
```

**Note:** P973 can only be added once we have issued the Ars Accordia passport for the work (AP-2026-XXXXXX). This is why completing the exemplary passports (Business Roadmap Priority 1) must come first.

---

## Phase 5 — LNMA institution record on Wikidata

Verify that the LNMA institution itself has a correct Wikidata item and that it is up to date:
- Search: "Latvijas Nacionālais mākslas muzejs" or "Latvia National Museum of Art"
- Likely QID: Q675836 (verify)
- Ensure P856 (official website), P856 (collection URL), and key facts are present

---

## Execution sequence summary

| Week | Action | Outcome |
|---|---|---|
| Week 1 | Phase 1: Add P973 to 5 confirmed artists via QuickStatements | 5 Ars Accordia pages linked from Wikidata |
| Week 1 | Phase 2: Resolve QIDs for Hūns, Feders, Tīdemanis | 3 more artists confirmed |
| Week 2 | Phase 3: Create ArtBase records for Walter/Valters, Klucis, Kazaks (highest priority) | 3 high-representation artists in catalogue |
| Week 2–3 | Phase 3 continued: Pērle, Krastiņš, Alksnis, Zariņš, Ūders | Full top-16 artist set in ArtBase |
| Week 3–4 | Phase 4: Issue 3–5 exemplary passports from LNMM works | First publishable exemplary passport set |
| Week 4 | Phase 4: Add P973 to artwork Wikidata items | Bidirectional link: Wikidata → Ars Accordia |

---

## Reference

- Wikidata QuickStatements: https://quickstatements.toolforge.org/
- Wikidata property P973: https://www.wikidata.org/wiki/Property:P973
- LNMM collection page: https://arsaccordia.com/collections/lnmm/
- ArtBase artist records: `artbase_export/data/artists/`
- Business roadmap: `docs/BUSINESS_ROADMAP.md`
