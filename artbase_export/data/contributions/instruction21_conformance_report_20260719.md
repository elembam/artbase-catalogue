# Instruction 21 — Conformance Report

Generated: 2026-07-19
Scope: the 41 artist JSON records reconstructed in commit `9b9814a`
(`fix: Instruction 21 — restore JSON backing for 41 orphaned artist pages`)
Validator: `scripts/instruction21_validate_reconstruction.py` — an
independent re-parse of the pre-reconstruction archived HTML
(`git show 9b9814a^:artists/<ID>.html`), not the original reconstruction
script — this report checks the output against the original evidence a
second time, from scratch, rather than confirming the script's own logic.

Reproduce: `python3 scripts/instruction21_validate_reconstruction.py`
(exit code 0 iff all pass; add `--json out.json` for the full
machine-readable record).

## Policy checked

| # | Rule |
|---|---|
| P1 | `identity.preferred_name` matches the archived page's `<title>` exactly |
| P2 | `life.birth_date.value` matches the archived page's artist-dates block exactly (or is `null` if the page showed none) |
| P3 | `life.birth_date.status` is `"working"` wherever a birth year is asserted — never `"confirmed"` (this is gallery-sourced, unconfirmed data) |
| P4 | `sources[]` contains the page's Galerija Jēkabs origin URL if and only if the archived page carried one — nothing invented, nothing dropped |
| P5 | `descriptors.nationality` / `descriptors.occupations` match the page's "Nationality · Occupation" line exactly |
| P6 | No Airtable-pipeline contamination: `airtable_id` and `artbase_canonical_id` are `null`, `cataloguing.catalogued_by` is `null`, `cataloguing.review_status` is `"draft"`, no `authority_links` entry carries a resolved id |
| P7 | No asserted value for any field the archived page never displayed (`death_date`, `birth_place`, etc.) |

## Result

- **Total checked: 41**
- **Pass: 41**
- **Fail: 0**
- **Per-record exceptions: none**

## Per-record results

| artbase_id | name | birth_year | origin | status |
|---|---|---:|---|---|
| ART-AKOPJANS-1969 | Arturs Akopjans | 1969 | none captured | PASS |
| ART-AMELKOVICS-1969 | Andrejs Ameļkovičs | 1969 | none captured | PASS |
| ART-AVRAMENKO-1981 | Vladimirs Avramenko | 1981 | Galerija Jēkabs | PASS |
| ART-BAIDA-1958 | Valērijs Baida | 1958 | Galerija Jēkabs | PASS |
| ART-BALODE-1983 | Zane Balode | 1983 | none captured | PASS |
| ART-BRASLINS-1962 | Normunds Brasliņš | 1962 | none captured | PASS |
| ART-BREKTE-1952 | Ilona Brekte | 1952 | none captured | PASS |
| ART-CARUKA-1964 | Ieva Caruka | 1964 | Galerija Jēkabs | PASS |
| ART-CAUNE-1961 | Sarmīte Caune | 1961 | Galerija Jēkabs | PASS |
| ART-EGLITIS-1981 | Andris Eglītis | 1981 | Galerija Jēkabs | PASS |
| ART-FJODOROVA-1986 | Darja Fjodorova | 1986 | Galerija Jēkabs | PASS |
| ART-GERMANE-1964 | Agnija Ģērmane | 1964 | none captured | PASS |
| ART-JAKOBSONS-1985 | Atis Jākobsons | 1985 | none captured | PASS |
| ART-JANSONE-1973 | Agija Jansone | 1973 | Galerija Jēkabs | PASS |
| ART-KALNINS-1976 | Jānis Kalniņš | 1976 | Galerija Jēkabs | PASS |
| ART-KRUZE-1980 | Daiga Krūze | 1980 | none captured | PASS |
| ART-KVITKA-1983 | Kristīne Kvitka | 1983 | none captured | PASS |
| ART-LAICANE-1984 | Anna Laicāne | 1984 | Galerija Jēkabs | PASS |
| ART-LAIZANE-1966 | Ilze Laizāne | 1966 | Galerija Jēkabs | PASS |
| ART-LAPINA-1954 | Dace Lapiņa | 1954 | none captured | PASS |
| ART-LIEPINA-1967 | Ieva Liepiņa | 1967 | none captured | PASS |
| ART-LUSE-1975 | Zane Lūse | 1975 | Galerija Jēkabs | PASS |
| ART-MEDINA-1984 | Alise Mediņa | 1984 | none captured | PASS |
| ART-MEDVEDEVA-1987 | Neonilla Medvedeva | 1987 | Galerija Jēkabs | PASS |
| ART-MELBARZDE-1970 | Elizabete Melbārzde | 1970 | none captured | PASS |
| ART-MERCA-1951 | Vita Merca | 1951 | none captured | PASS |
| ART-NEIKENA-1988 | Madara Neikena | 1988 | Galerija Jēkabs | PASS |
| ART-PAKALNE-1982 | Līva Pakalne | 1982 | Galerija Jēkabs | PASS |
| ART-POSTAZS-1976 | Paulis Postažs | 1976 | none captured | PASS |
| ART-PREISA-1976 | Ilze Preisa | 1976 | none captured | PASS |
| ART-SEVERETNIKOVS-1962 | Andrejs Severetņikovs | 1962 | none captured | PASS |
| ART-SMILDZINA-1973 | Ilze Smildziņa | 1973 | Galerija Jēkabs | PASS |
| ART-STRELE-1991 | Sandra Strēle | 1991 | Galerija Jēkabs | PASS |
| ART-TOROPINS-1952 | Juris Toropins | 1952 | Galerija Jēkabs | PASS |
| ART-VORKALE-1953 | Irina Vorkale | 1953 | none captured | PASS |
| ART-ZALANS-1962 | Ilgvars Zalāns | 1962 | none captured | PASS |
| ART-ZALITIS-1976 | Kalvis Zālītis | 1976 | Galerija Jēkabs | PASS |
| ART-ZEMZARIS-1961 | Alvis Zemzaris | 1961 | Galerija Jēkabs | PASS |
| ART-ZINGITIS-1973 | Jānis Ziņģītis | 1973 | Galerija Jēkabs | PASS |
| ART-ZIRNITE-1959 | Nele Zirnīte | 1959 | none captured | PASS |
| ART-ZITMANIS-1980 | Otto Zitmanis | 1980 | Galerija Jēkabs | PASS |

### Note on methodology (why the first pass showed 21 false failures)

An initial run of this same check against the **current, already-regenerated**
`artists/*.html` (i.e. after `artist_profile_generator.py` had rewritten
every one of the 41 pages from the current template) produced 21 false
"missing origin" failures. Root cause: the current template's Sources
section renders from `.source-row` markup and only ever existed after
`artist_profile_generator.py` regenerated the page — it never carries the
old template's `.origin-chip` markup, regardless of what's in the JSON.
Comparing against the live page was comparing the reconstruction's own
downstream output against itself under a different template, not against
independent evidence. Re-run against the **pre-reconstruction archived
page** (`git show 9b9814a^:...`, the actual source material the
reconstruction script read from) instead, which is the correct ground
truth and produced a clean 41/41 pass.

## Exception: pre-existing, store-wide (not a P1–P7 fail, flagged separately)

21 of the 41 records carry a gallery-index source entry
(`SD-CON-GALERIJA-JEKABS-INDEX`) with no `citation` key — following the
established precedent already used for the same source type in
`ART-ABOLINA-1910.json` (a "full-shape" record that predates this
instruction). The current `templates/artist_profile.html.j2` Sources
section only renders entries where `citation` is defined
(`sources | selectattr('citation', 'defined')`), so **these 21 gallery
sources are present in the canonical JSON but not visibly disclosed on
the live page** — confirmed this is not something Instruction 21
introduced: `ART-ABOLINA-1910.html`'s own gallery-index source has the
same invisibility today.

**Remediation suggestion:** either (a) give gallery-index sources a
synthesized `citation` string (e.g. `"Galerija Jēkabs — Artist Index. <url>. Retrieved <date>."`,
which is already stored as `title` — a one-line copy would suffice) so
the existing filter naturally includes them, or (b) relax the template
filter to `sources | selectattr('url', 'defined')` (also true for MAB/
Imago Mundi book citations that lack a bare `url`, so this would need
an `or`, not a straight swap). Option (a) is the smaller, lower-risk
change and is consistent with the "citation" field's existing purpose
elsewhere in the store — recommended for the next store-wide pass, not
this one, since it touches every gallery-index source in the store, not
just these 41.

## Records with a recovered origin (21)

`AVRAMENKO-1981, BAIDA-1958, CARUKA-1964, CAUNE-1961, EGLITIS-1981,
FJODOROVA-1986, JANSONE-1973, KALNINS-1976, LAICANE-1984, LAIZANE-1966,
LUSE-1975, MEDVEDEVA-1987, NEIKENA-1988, PAKALNE-1982, SMILDZINA-1973,
STRELE-1991, TOROPINS-1952, ZALITIS-1976, ZEMZARIS-1961, ZINGITIS-1973,
ZITMANIS-1980` (prefix `ART-` omitted for brevity)

## Records with no recoverable origin (20)

`AKOPJANS-1969, AMELKOVICS-1969, BALODE-1983, BRASLINS-1962, BREKTE-1952,
GERMANE-1964, JAKOBSONS-1985, KRUZE-1980, KVITKA-1983, LAPINA-1954,
LIEPINA-1967, MEDINA-1984, MELBARZDE-1970, MERCA-1951, POSTAZS-1976,
PREISA-1976, SEVERETNIKOVS-1962, VORKALE-1953, ZALANS-1962, ZIRNITE-1959`
(prefix `ART-` omitted for brevity) — these 20 used the older
"minimal" archived template, which never captured an origin/source at
all. `sources: []` for all 20, per policy — nothing invented to fill
the gap.
