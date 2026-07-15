# Instruction 19 Phase 1 — Literature Match Report

Generated 2026-07-15. Input: 167 artist literature entries (compiled bibliography, MAB + other sources).

**Update 2026-07-15 — Part E complete.** The 154 matched entries below (155 matched minus GŪTMANS, held per the entry-name-mismatch finding in §2) were written to their artist JSON `sources[]` arrays and their pages regenerated. 215 citations written; re-run verified idempotent (0 new writes on a second pass). `SRC-MAB-I`–`IV` created in `artbase_export/data/sources/`. The 3 review-queue entries, GŪTMANS, the 2 excluded, and the 7 unmatched received **no writes**, per spec.

## Summary

| | Count |
|---|---|
| Matched (>=95%, auto-write eligible) | 155 |
| Review (ambiguous / needs a decision) | 3 |
| Unmatched (not in the artist store) | 7 |
| Excluded (pre-flagged, do not write) | 2 |
| **Total entries** | **167** |

Total citations parsed: 230 (book: 205, web: 19, periodical: 5, thesis: 1)

**`wikidata_batch_eligible` citations (matched artists only): 102** — the input figure for Phase 2, if/when that's commissioned separately.

---

## Needs your decision before Part E writes anything

### 1. Review queue — ambiguous match, not auto-written (3)

Surname matches a store record, but the birth year in the citation doesn't match any candidate — could be a second, not-yet-catalogued person, or a birth-year typo in the source list.

- **BREKTE Ilona (1952)** — surname matches ART-BREKTE-1920 but birth year differs. Citation: `Jāņa Brektes dzimtas izstāde // Laiks. – 2004. – Nr. 24. – 19. jūn.`
- **LŪSE Zane (1975)** — surname matches ART-LUSE-1948 but birth year differs. Citation: `www.zaneluse.com`
- **TOROPINS Juris (1952)** — surname matches ART-TOROPINS-1924 but birth year differs. Citation: `Vilsons A., Māksla un Arhitektūra biografijās. Rīga: Latvijas enciklopēdija, 1995`

### 2. New entry-name mismatch found (beyond the two pre-flagged in the spec)

The spec pre-flagged JAUNSUDRABIŅŠ and JURĶELIS as citing the wrong encyclopedia entry. The mechanical cross-check found one more:

- **GŪTMANS Naftolijs (1938)** — citation's entry title reads *"Gūtmanis, Naftolijs"* (Reihmane I., MAB I, p.189), one letter off from the artist's surname `GŪTMANS`/`ART-GUTMANS-1938`. Could be a spelling variant of the same person, or genuinely a different encyclopedia entry compiled against the wrong artist. **Currently matched but this citation is held out of the auto-write set pending your call — treat like the two pre-flagged cases unless you confirm it's a spelling variant.**

### 3. Volume/year inconsistencies (3 — 2 pre-flagged + 1 new)

- **IVAŅICKIS Staņislavs** — cites "3. grāmata" (vol III) dated 1995; vol III is actually 2000 (ed. Vanaga). Pre-flagged in the spec. Marked `inconsistent`, not `wikidata_batch_eligible`; site citation still fine to write (artist matched).
- **KOZINS Vladimirs** — inverted title ("Arhitektūra un māksla...") + "2. grāmata" dated 1995; vol II is actually 1996. Pre-flagged in the spec. Same treatment.
- **VORKALE Irina (1953)** — new find: cites "4. daļa" (vol IV, 2003 per table) dated 1996 in the string. Moot for writing since VORKALE isn't in the artist store at all (see unmatched list) — flagging for completeness only.

### 4. Unmatched — not in the artist JSON store (7), but two different reasons

None of these 7 have a JSON record in `artbase_export/data/artists/`, so per spec none get a citation written and none get a new record created. But direct search turned up something the spec's "match against the JSON store" scope wouldn't have surfaced on its own: **5 of the 7 already have a live, sitemap-indexed HTML page at `arsaccordia.com/artists/<id>.html` with no canonical JSON behind it** — a separate, pre-existing data-pipeline gap (published output with no source record), not a literature-matching problem. Only 2 are genuinely absent from the site altogether.

**5(a) — live page, no JSON (real gap, separate issue):**
- BRASLIŅŠ Normunds (1962) → `artists/ART-BRASLINS-1962.html` exists, indexed in sitemap.xml
- CARUKA Ieva (1964) → `artists/ART-CARUKA-1964.html` exists, indexed in sitemap.xml
- PREISA Ilze (1976) → `artists/ART-PREISA-1976.html` exists, indexed in sitemap.xml
- VORKALE Irina (1953) → `artists/ART-VORKALE-1953.html` exists, indexed in sitemap.xml
- ZIRNĪTE Nele (1959) → `artists/ART-ZIRNITE-1959.html` exists, indexed in sitemap.xml

These citations are ready to attach the moment each artist gets a real JSON record — that's a separate fix (regenerate or recreate the missing JSON, matching whatever's already on the live page), not something Instruction 19 should paper over by writing into a file that doesn't exist.

**5(b) — genuinely absent, no page anywhere (2):**
- VARŽAPETOVA Izabella (1931 - 2000)
- VASARIŅŠ Vilis (1906 - 1945)

If any of these 7 should be matched to a differently-spelled existing `artbase_id` you already know about, point me at it and I'll add it to the matched set.

### 5. Excluded per spec — do not write (2)

- **JAUNSUDRABIŅŠ Jānis (1877 - 1962)** — citation cites entry "Maldupe, Vija", held per Instruction 19 Part F until corrected source strings are supplied.
- **JURĶELIS Eduards (1910 - 1978)** — citation cites entry "Skulme, Džemma", held per Instruction 19 Part F until corrected source strings are supplied.

---

## Full match table

| List entry | artbase_id | Status | Citations | Flags |
|---|---|---|---|---|
| AIDE Bruno (1913 - 1994) | ART-AIDE-1913 | ✓ matched | 1 |  |
| ANDERSONS Edvīns (1929 - 1996) | ART-ANDERSONS-1929 | ✓ matched | 1 |  |
| ANMANIS Jānis (1943 - 2025) | ART-ANMANIS-1943 | ✓ matched | 1 |  |
| ANNUSS Augusts (1893 - 1984) | ART-ANNUSS-1893 | ✓ matched | 1 |  |
| ANTONOVS Sergejs (1884 - 1956) | ART-ANTONOVS-1884 | ✓ matched | 2 |  |
| APINIS Jēkabs (1899 - 1945) | ART-APINIS-1899 | ✓ matched | 3 | no-pages |
| ARTUMS Ansis (1908 - 1997) | ART-ARTUMS-1908 | ✓ matched | 2 | no-pages |
| AUZA Lidija (1914 - 1989) | ART-AUZA-1914 | ✓ matched | 1 |  |
| AVOTIŅA Ilze (1952) | ART-AVOTINA-1952 | ✓ matched | 2 |  |
| AVOTIŅA Kristīne Luīze (1983) | ART-AVOTINA-1983 | ✓ matched | 1 |  |
| BAKLĀNS Juris (1947 - 1989) | ART-BAKLANS-1947 | ✓ matched | 3 |  |
| BALTGAILIS Kārlis (1893 - 1979) | ART-BALTGAILIS-1893 | ✓ matched | 2 |  |
| BALTMANE Emma (1882 - 1969) | ART-BALTMANE-1882 | ✓ matched | 1 |  |
| BAUMA Dzidra (1930) | ART-BAUMA-1930 | ✓ matched | 1 |  |
| BAUMANE Biruta (1922 - 2017) | ART-BAUMANE-1922 | ✓ matched | 1 |  |
| BAUMANIS Artūrs (1892 - 1975) | ART-BAUMANIS-1892 | ✓ matched | 1 |  |
| BAUŠĶENIEKS Auseklis (1910 - 2007) | ART-BAUSKENIEKS-1910 | ✓ matched | 2 |  |
| BIRNBAUMS Staņislavs (1863 - 1944) | ART-BIRNBAUMS-1863 | ✓ matched | 1 |  |
| BOGDANOVS-BEĻSKIS Nikolajs (1868 - 1945) | ART-BOGDANOVS-BELSKIS-1868 | ✓ matched | 1 |  |
| BRASLIŅŠ Normunds (1962) | — | ✗ unmatched | 2 |  |
| BRAUNBERGS Emīls (1931 - 2018) | ART-BRAUNBERGS-1931 | ✓ matched | 1 |  |
| BREIKŠS Nikolajs (1911 - 1972) | ART-BREIKSS-1911 | ✓ matched | 2 |  |
| BREKTE Jānis (1920 - 1985) | ART-BREKTE-1920 | ✓ matched | 1 |  |
| BREKTE Ilona (1952) | — | ⚠ review | 2 |  |
| BRENCĒNS Eduards (1885 - 1929) | ART-BRENCENS-1885 | ✓ matched | 1 |  |
| BRENCĒNS Kārlis (1897 - 1951) | ART-BRENCENS-1897 | ✓ matched | 2 |  |
| BUŠS Valdis (1924 - 2014) | ART-BUSS-1924 | ✓ matched | 3 |  |
| BĪLENŠTEINS Zigfrīds (1869 - 1949) | ART-BILENSTEINS-1869 | ✓ matched | 1 |  |
| BĪNE Jēkabs (1895 - 1955) | ART-BINE-1895 | ✓ matched | 2 |  |
| CARUKA Ieva (1964) | — | ✗ unmatched | 1 |  |
| CELMIŅŠ Bruno (1927 - 1992) | ART-CELMINS-1927 | ✓ matched | 1 |  |
| CIELAVS Jānis (1890 - 1968) | ART-CIELAVS-1890 | ✓ matched | 1 |  |
| CĪRULIS Ansis (1883 - 1942) | ART-CIRULIS-1883 | ✓ matched | 2 |  |
| DIMITERS Juris (1947) | ART-DIMITERS-1947 | ✓ matched | 1 |  |
| DIŅĢELIS Staņislavs (1899 - 1988) | ART-DINGELIS-1899 | ✓ matched | 1 |  |
| DOBRĀJA Inta (1940 - 2020) | ART-DOBRAJA-1940 | ✓ matched | 1 |  |
| DOBRĀJS Kārlis (1943) | ART-DOBRAJS-1943 | ✓ matched | 1 |  |
| DONCOVS Hermanis (1916 - 2001) | ART-DONCOVS-1916 | ✓ matched | 1 |  |
| DRAGŪNE Maija (1945) | ART-DRAGUNE-1945 | ✓ matched | 1 |  |
| DUBURS Artūrs (1899 - 1973) | ART-DUBURS-1899 | ✓ matched | 1 |  |
| DZENIS Albīns (1907 - 1998) | ART-DZENIS-1907 | ✓ matched | 1 |  |
| EGLĪTE Laima (1945) | ART-EGLITE-1945 | ✓ matched | 1 |  |
| ELIASS Ģederts (1887 - 1975) | ART-ELIASS-1887 | ✓ matched | 3 | no-pages |
| FEDERS Jūlijs (1838 - 1909) | ART-FEDERS-1838 | ✓ matched | 2 |  |
| FRIDRIHSONS Kurts (1911 - 1991) | ART-FRIDRIHSONS-1911 | ✓ matched | 1 |  |
| GAILIS Jānis (1903 - 1975) | ART-GAILIS-1903 | ✓ matched | 2 | split |
| GEISTAUTE Erna (1911 - 1975) | ART-GEISTAUTE-1911 | ✓ matched | 2 |  |
| GRASMANIS Laimdonis (1916 - 1970) | ART-GRASMANIS-1916 | ✓ matched | 3 |  |
| GROSVALDS Jāzeps (1891 - 1920) | ART-GROSVALDS-1891 | ✓ matched | 1 |  |
| GROTUSS Hugo (1884 - 1951) | ART-GROTUSS-1884 | ✓ matched | 1 |  |
| GRŪBE Edvards (1935 - 2022) | ART-GRUBE-1935 | ✓ matched | 2 |  |
| GULBE Ērika (1916 - 2003) | ART-GULBE-1916 | ✓ matched | 1 |  |
| GŪTMANS Naftolijs (1938) | ART-GUTMANS-1938 | ✓ matched | 1 | entry-name-mismatch:Gūtmanis, Naftolijs |
| HEINRIHSONE Helēna (1948) | ART-HEINRIHSONE-1948 | ✓ matched | 1 |  |
| HŪNS Kārlis (1831 - 1877) | ART-HUNS-1831 | ✓ matched | 3 | no-pages |
| ILTNERS Edgars (1925 - 1983) | ART-ILTNERS-1925 | ✓ matched | 1 |  |
| IRBE Voldemārs (1893 - 1944) | ART-IRBE-1893 | ✓ matched | 2 |  |
| IVAŅICKIS Staņislavs (1908 - 1971) | ART-IVANICKIS-1908 | ✓ matched | 1 | inconsistent, inconsistent(known) |
| JAUNSUDRABIŅŠ Jānis (1877 - 1962) | — | ⛔ excluded | 1 | entry-name-mismatch:Maldupe, Vija |
| JUNKERS Aleksandrs (1899 - 1976) | ART-JUNKERS-1899 | ✓ matched | 1 |  |
| JUPATOVS Aleksejs (1911 - 1975) | ART-JUPATOVS-1911 | ✓ matched | 1 |  |
| JURJĀNS Juris (1944 - 2023) | ART-JURJANS-1944 | ✓ matched | 2 |  |
| JURĶELIS Eduards (1910 - 1978) | — | ⛔ excluded | 1 | entry-name-mismatch:Skulme, Džemma, no-pages |
| JĀŅKALNIŅŠ Voldemārs (1914 - 1990) | ART-JANKALNINS-1914 | ✓ matched | 1 |  |
| KALMĪTE Jānis (1907 - 1996) | ART-KALMITE-1907 | ✓ matched | 2 |  |
| KALVE Pēteris (1882 - 1913) | ART-KALVE-1882 | ✓ matched | 2 |  |
| KASPARSONS Reinholds (1889 - 1966) | ART-KASPARSONS-1889 | ✓ matched | 1 |  |
| KLĒBAHS Henrijs (1928 - 1998) | ART-KLEBAHS-1928 | ✓ matched | 1 |  |
| KORTI Igors (1922 - 1986) | ART-KORTI-1922 | ✓ matched | 2 |  |
| KOZINS Vladimirs (1922) | ART-KOZINS-1922 | ✓ matched | 1 | inconsistent, inconsistent(known), inverted-title, no-pages |
| KUGA Jānis (1878 - 1969) | ART-KUGA-1878 | ✓ matched | 1 |  |
| KUNDZIŅŠ Pēteris (1886 - 1958) | ART-KUNDZINS-1886 | ✓ matched | 2 | no-pages |
| KUPCIS Laimonis (1928 - 1976) | ART-KUPCIS-1928 | ✓ matched | 1 |  |
| LAUVA Jānis (1906 - 1986) | ART-LAUVA-1906 | ✓ matched | 1 | no-pages |
| LEJNIEKS Kārlis (1911 - 1984) | ART-LEJNIEKS-1911 | ✓ matched | 1 |  |
| LIBERTS Ludolfs (1895 - 1959) | ART-LIBERTS-1895 | ✓ matched | 1 |  |
| LIEPIŅŠ Jānis (1894 - 1964) | ART-LIEPINS-1894 | ✓ matched | 3 |  |
| LOGINA Zenta (1908 - 1983) | ART-LOGINA-1908 | ✓ matched | 1 |  |
| LŪCIS Edmunds (1959 - 2017) | ART-LUCIS-1959 | ✓ matched | 1 |  |
| LŪSE Zane (1975) | — | ⚠ review | 1 |  |
| MADERNIEKS Jūlijs (1870 - 1955) | ART-MADERNIEKS-1870 | ✓ matched | 1 |  |
| MALDUPE Vija (1947 - 1996) | ART-MALDUPE-1947 | ✓ matched | 2 |  |
| MANGOLDS Herberts (1901 - 1978) | ART-MANGOLDS-1901 | ✓ matched | 1 | no-pages |
| MASĻAKOVS Sergejs (1928 - 1979) | ART-MASLAKOVS-1928 | ✓ matched | 1 |  |
| MEDNIS Jānis (1910 - 1997) | ART-MEDNIS-1910 | ✓ matched | 1 |  |
| MEDNĪTIS Bernhards (1903 - 1982) | ART-MEDNITIS-1903 | ✓ matched | 1 |  |
| MEILERTE Ludmila (1908 - 1997) | ART-MEILERTE-1908 | ✓ matched | 2 |  |
| MELBĀRZDIS Kārlis (1902 - 1970) | ART-MELBARZDIS-1902 | ✓ matched | 2 |  |
| MELNĀRS Ādolfs (1908 - 1963) | ART-MELNARS-1908 | ✓ matched | 1 |  |
| METUZĀLS Eduards (1889 - 1978) | ART-METUZALS-1889 | ✓ matched | 1 |  |
| MEĻĶIS Ernests (1908 - 1977) | ART-MELKIS-1908 | ✓ matched | 1 | no-pages |
| MIESNIEKS Kārlis (1887 - 1977) | ART-MIESNIEKS-1887 | ✓ matched | 1 | no-pages |
| MILTS Fridrihs (1906 - 1993) | ART-MILTS-1906 | ✓ matched | 1 |  |
| NALOGINS Aleksandrs (1922 - 1993) | ART-NALOGINS-1922 | ✓ matched | 1 |  |
| NAUMOVS Aleksejs (1955) | ART-NAUMOVS-1955 | ✓ matched | 2 |  |
| NEMME Otomārs (1901 - 1947) | ART-NEMME-1901 | ✓ matched | 1 | no-pages |
| OSIS Jānis (1926 - 1991) | ART-OSIS-1926 | ✓ matched | 2 |  |
| OZOLS Vilis (1929 - 2014) | ART-OZOLS-1929 | ✓ matched | 2 |  |
| PADEGS Kārlis (1911 - 1940) | ART-PADEGS-1911 | ✓ matched | 3 | no-pages |
| PANKOKS Arnolds (1914 - 2008) | ART-PANKOKS-1914 | ✓ matched | 1 | no-pages |
| PAULIŅŠ Alberts (1948 - 2026) | ART-PAULINS-1948 | ✓ matched | 1 | no-pages |
| PEILĀNE Marianna (1915 - 1996) | ART-PEILANE-1915 | ✓ matched | 1 |  |
| PINNIS Rūdolfs (1902 - 1992) | ART-PINNIS-1902 | ✓ matched | 2 |  |
| POIKĀNS Ivars (1952) | ART-POIKANS-1952 | ✓ matched | 1 | no-pages |
| POSTAŽS Pēteris (1940) | ART-POSTAZS-1940 | ✓ matched | 1 |  |
| PREISA Ilze (1976) | — | ✗ unmatched | 1 |  |
| PUTRĀMS Juris (1956) | ART-PUTRAMS-1956 | ✓ matched | 2 |  |
| PĪGOZNIS Jāzeps (1934 - 2014) | ART-PIGOZNIS-1934 | ✓ matched | 1 | no-pages |
| PŪPOLS Jānis (1887 - 1956) | ART-PUPOLS-1887 | ✓ matched | 1 |  |
| RIEKSTIŅŠ Jānis (1928 - 1982) | ART-RIEKSTINS-1928 | ✓ matched | 1 | no-pages |
| RIKMANIS Jānis (1901 - 1968) | ART-RIKMANIS-1901 | ✓ matched | 1 | no-pages |
| ROZENS Kārlis (1864 - 1934) | ART-ROZENS-1864 | ✓ matched | 1 | no-pages |
| ROZENTĀLS Janis (1866 - 1916) | ART-ROZENTALS-1866 | ✓ matched | 1 |  |
| ROŽLAPA Dailis (1932 - 2014) | ART-ROZLAPA-1932 | ✓ matched | 1 |  |
| RUŅĢIS Pēteris (1893 - 1967) | ART-RUNGIS-1893 | ✓ matched | 1 | no-pages |
| SIETIŅŠ Guntars (1962) | ART-SIETINS-1962 | ✓ matched | 2 |  |
| SIPĀNS Bruno (1913 - 1973) | ART-SIPANS-1913 | ✓ matched | 1 |  |
| SKRIDE Ārijs (1906 - 1987) | ART-SKRIDE-1906 | ✓ matched | 1 |  |
| SKULME Jurģis (1928 - 2015) | ART-SKULME-1928 | ✓ matched | 1 | no-pages |
| SKULME Uga (1895 - 1963) | ART-SKULME-1895 | ✓ matched | 2 |  |
| SKULME Džemma (1925 - 2019) | ART-SKULME-1925 | ✓ matched | 2 |  |
| SKULME Oto (1889 - 1967) | ART-SKULME-1889 | ✓ matched | 2 |  |
| SKUČS Jānis (1908 - 1998) | ART-SKUCS-1908 | ✓ matched | 1 | no-pages |
| SPALVIŅŠ Arnolds (1911 - 1948) | ART-SPALVINS-1911 | ✓ matched | 1 | no-pages |
| SPRIŅĢIS Jēkabs (1907 - 2004) | ART-SPRINGIS-1907 | ✓ matched | 1 | no-pages |
| STRAUJA Arvīds (1907 - 1999) | ART-STRAUJA-1907 | ✓ matched | 1 |  |
| STRUNKE Niklāvs (1894 - 1966) | ART-STRUNKE-1894 | ✓ matched | 2 | no-pages |
| STUMBRIS Mārcis (1942 - 2014) | ART-STUMBRIS-1942 | ✓ matched | 3 |  |
| SUTA Romans (1896 - 1944) | ART-SUTA-1896 | ✓ matched | 1 | no-pages |
| SŪNIŅŠ Kārlis (1907 - 1979) | ART-SUNINS-1907 | ✓ matched | 2 | no-pages |
| SŪNIŅŠ Žanis (1904 - 1993) | ART-SUNINS-1904 | ✓ matched | 1 |  |
| TILLBERGS Jānis-Roberts (1880 - 1972) | ART-TILLBERGS-1880 | ✓ matched | 2 |  |
| TONE Valdemārs (1892 - 1958) | ART-TONE-1892 | ✓ matched | 1 |  |
| TOROPINS Aleksandrs (1924 - 1960) | ART-TOROPINS-1924 | ✓ matched | 1 | no-pages |
| TOROPINS Juris (1952) | — | ⚠ review | 1 | no-pages |
| TĪDEMANIS Jānis (1897 - 1964) | ART-TIDEMANIS-1897 | ✓ matched | 1 |  |
| ULDRIĶIS Teodors (1909 - 1973) | ART-ULDRIKIS-1909 | ✓ matched | 1 |  |
| VALDMANIS Edgars (1938 - 1999) | ART-VALDMANIS-1938 | ✓ matched | 1 | no-pages |
| VALTERS Jānis (1869 - 1932) | ART-VALTERS-1869 | ✓ matched | 3 | no-pages |
| VARŽAPETOVA Izabella (1931 - 2000) | — | ✗ unmatched | 1 |  |
| VASARIŅŠ Vilis (1906 - 1945) | — | ✗ unmatched | 1 | no-pages |
| VASIĻEVSKIS Bruno (1939 - 1990) | ART-VASILEVSKIS-1939 | ✓ matched | 1 |  |
| VECOZOLS Imants (1933) | ART-VECOZOLS-1933 | ✓ matched | 2 |  |
| VEITNERS Kārlis (1907 - 1994) | ART-VEITNERS-1907 | ✓ matched | 1 | no-pages |
| VELDRE Harijs (1927 - 1999) | ART-VELDRE-1927 | ✓ matched | 1 | no-pages |
| VIMBA Voldemārs (1904 - 1985) | ART-VIMBA-1904 | ✓ matched | 1 | no-pages |
| VINOGRADOVS Sergejs (1869 - 1938) | ART-VINOGRADOVS-1869 | ✓ matched | 1 |  |
| VINTERS Edgars (1919 - 2014) | ART-VINTERS-1919 | ✓ matched | 1 |  |
| VISOTSKIS Konstantīns (1864 - 1938) | ART-VISOTSKIS-1864 | ✓ matched | 1 |  |
| VORKALE Irina (1953) | — | ✗ unmatched | 1 | inconsistent, no-pages |
| VĪKA Hilda (1897 - 1963) | ART-VIKA-1897 | ✓ matched | 2 | no-pages |
| VĪNDEDZIS Oskars (1911 - 2002) | ART-VINDEDZIS-1911 | ✓ matched | 1 | no-pages |
| VĪTOLS Eduards (1877 - 1954) | ART-VITOLS-1877 | ✓ matched | 1 | no-pages |
| ZARIŅA Aija (1954 - 2025) | ART-ZARINA-1954 | ✓ matched | 2 |  |
| ZARIŅŠ Indulis (1929 - 1997) | ART-ZARINS-1929 | ✓ matched | 1 |  |
| ZEMZARIS Uldis (1928 - 2022) | ART-ZEMZARIS-1928 | ✓ matched | 1 |  |
| ZIRNĪTE Nele (1959) | — | ✗ unmatched | 1 |  |
| ZVIEDRIS Aleksandrs (1905 - 1993) | ART-ZVIEDRIS-1905 | ✓ matched | 2 | split |
| ZVIRBULIS Juris (1944) | ART-ZVIRBULIS-1944 | ✓ matched | 1 | no-pages |
| ZĀRDIŅŠ Ādolfs (1890 - 1967) | ART-ZARDINS-1890 | ✓ matched | 2 |  |
| ĀBOLIŅA Austra (1910 - 1967) | ART-ABOLINA-1910 | ✓ matched | 1 | no-pages |
| ĀBOLS Ojārs (1922 - 1983) | ART-ABOLS-1922 | ✓ matched | 2 |  |
| ĀRGALIS Māris (1954 - 2008) | ART-ARGALIS-1954 | ✓ matched | 2 |  |
| ĀRIŅŠ Leonīds (1907 - 1991) | ART-ARINS-1907 | ✓ matched | 1 |  |
| ĢĒRMANIS Juris (1941) | ART-GERMANIS-1941 | ✓ matched | 1 |  |
| ŠEGELMANS Semjons (1933 - 2025) | ART-SEGELMANS-1933 | ✓ matched | 1 |  |
| ŠPRENKS Pauls (1898 - 1988) | ART-SPRENKS-1898 | ✓ matched | 1 | no-pages |