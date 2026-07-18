# Instruction 20 — Reconciliation Reports (Imago Mundi Latvia 2014)

Generated: 2026-07-18  
Source dataset: `ArsAccordiaClaude/References/imago-mundi-latvia-2014-corrected.json` (203 entries)

## Scope and reconstruction note

Claude's original cohort file was not present in local session logs, so this report reconstructs the working split from current canonical data using deterministic rules:

- **Matched (31):** existing artist JSON has `source_id = SRC-IMAGOMUNDI-LV-2014`
- **Review queue conflicts (23):** remaining entries where surname collides with an existing artist record but identity is not auto-safe
- **Contemporary-gap map (130):** unmatched entries after review-queue extraction, filtered to contemporary cohort (`birth_year >= 1953`, plus `1987–2014` range entry)

No artist/artwork records were created from the review queue or contemporary-gap sets in this step.

---

## A) Review queue conflicts (23) — human resolution required, untouched

Each row needs a curator decision before any write.

| Imago entry | Birth | PDF page | Existing conflicting candidate(s) |
|---|---:|---:|---|
| Andris Vītols | 1951 | 206 | Eduards Vītols (1877) [ART-VITOLS-1877] |
| Artūrs Bērziņš | 1983 | 34 | Boriss Bērziņš (1930) [ART-BERZINS-1930] |
| Dace Gaile | 1984 | 61 | Barbara Gaile (1968) [ART-GAILE-1968] |
| Daila Iltnere | 1961 | 74 | Ieva Iltnerē (1957) [ART-ILTNERE-1957] |
| Dita Lūse | 1972 | 125 | Irēna Lūse (1948) [ART-LUSE-1948] |
| Egils Mednis | 1968 | 134 | Jānis Mednis (1910) [ART-MEDNIS-1910] |
| Ieva Jurjāne | 1972 | 89 | Aija Jurjāne (1944) [ART-JURJANE-1944] |
| Ilze Lībiete | 1951 | 121 | Ilze Libiete (1952) [ART-LIBIETE-1952] |
| Jānis Andris Osis | 1943 | 143 | Jānis Osis (1926) [ART-OSIS-1926] |
| Jānis Spalviņš | 1948 | 177 | Arnolds Spalviņš (1911) [ART-SPALVINS-1911] |
| Kristians Brekte | 1981 | 41 | Jānis Brekte (1920) [ART-BREKTE-1920] |
| Kristīna Keire | 1968 | 95 | Kristīne Keire (?) [ART-KEIRE-KRISTINE] |
| Madara Māra Irbe | 1991 | 78 | Voldemārs Irbe (1893) [ART-IRBE-1893] |
| Marta Jurjāne | 1979 | 90 | Aija Jurjāne (1944) [ART-JURJANE-1944] |
| Matiass Jansons | 1973 | 84 | Ralfs Jansons (1946) [ART-JANSONS-1946] |
| Mārtiņš Cīrulis | 1987 | 47 | Kārlis Cīrulis (1925) [ART-CIRULIS-1925]; Ansis Cīrulis (1883) [ART-CIRULIS-1883] |
| Patrīcija Brekte | 1981 | 42 | Jānis Brekte (1920) [ART-BREKTE-1920] |
| Paula Zariņa | 1988 | 208 | Aija Zariņa (1954) [ART-ZARINA-1954]; Vija Zariņa (1961) [ART-ZARINA-1961] |
| Reinis Pētersons | 1981 | 151 | Ojārs Pētersons (?) [ART-PETERSONS-OJARS] |
| Vilnis Heinrihsons | 1958 | 73 | Ivars Heinrihsons (1945) [ART-HEINRIHSONS-1945] |
| Zane Iltnere | 1961 | 76 | Ieva Iltnerē (1957) [ART-ILTNERE-1957] |
| Zane Lūse | 1974 | 127 | Irēna Lūse (1948) [ART-LUSE-1948] |
| Zane Veldre | 1986 | 198 | Harijs Veldre (1927) [ART-VELDRE-1927] |

---

## B) Contemporary-gap map (130 unmatched) — no records created

### Cohort shape

- 1950s: 18
- 1960s: 30
- 1970s: 48
- 1980s: 33
- Range-form birth year (1987–2014): 1

### Full list (130)

`name_lv | birth_year | pdf_page | printed_pages`

Adriāna Vīgnere \| 1986 \| 201 \| 404,405  
Agija Audere \| 1973 \| 24 \| 46,47  
Agnese Bule \| 1972 \| 44 \| 88,89  
Agnija Ģērmane \| 1964 \| 64 \| 128,129  
Aija Bāliņa \| 1959 \| 28 \| 54,55  
Alise Mediņa \| 1984 \| 133 \| 266,267  
Anda Lāce \| 1982 \| 113 \| 226,227  
Anda Poikāne \| 1972 \| 155 \| 310,311  
Andris Abiļevs \| 1955 \| 17 \| 32,33  
Anita Inša \| 1968 \| 77 \| 154,155  
Anitra Bērziņa \| 1968 \| 32 \| 62,63  
Anna Fanigina \| 1973 \| 58 \| 116,117  
Anna Laicāne \| 1984 \| 115 \| 230,231  
Ansis Butnors \| 1977 \| 45 \| 90,91  
Antra Ivdra \| 1966 \| 80 \| 160,161  
Armands Zēfelds \| 1965 \| 212 \| 426,427  
Arnis Martinelli \| 1973 \| 130 \| 260,261  
Artūrs Akopjans \| 1969 \| 19 \| 36,37  
Asnate Blankveina \| 1986 \| 37 \| 72,73  
Atis Jākobsons \| 1985 \| 81 \| 162,163  
Ausma Šmite \| 1986 \| 174 \| 350,351  
Baiba Apsīte \| 1978 \| 23 \| 44,45  
Baiba Kalna \| 1978 \| 93 \| 186,187  
Baiba Sprance \| 1963 \| 178 \| 358,359  
Daiga Krūze \| 1980 \| 108 \| 216,217  
Didzis Albergs \| 1973 \| 20 \| 38,39  
Didzis Grodzs \| 1976 \| 67 \| 134,135  
Dmitrijs Lavrentjevs \| 1970 \| 118 \| 236,237  
Einārs Kvilis \| 1958 \| 111 \| 222,223  
Elga Grīnvalde \| 1966 \| 66 \| 132,133  
Elīna Alka \| 1986 \| 21 \| 40,41  
Elīna Zunde \| 1982 \| 217 \| 436,437  
Ernests Kļaviņš \| 1977 \| 99 \| 198,199  
Eva Vēvere \| 1981 \| 200 \| 402,403  
Evija Ķirsone \| 1977 \| 98 \| 196,197  
Gints Strēlis \| 1962 \| 183 \| 368,369  
Gita Treice \| 1969 \| 188 \| 378,379  
Gita Šmite \| 1973 \| 175 \| 352,353  
Gustavs Filipsons \| 1974 \| 59 \| 118,119  
Harita Strazdiņa \| 1972 \| 181 \| 364,365  
Ieva Bondare \| 1972 \| 38 \| 74,75  
Ieva Kalēja \| 1978 \| 92 \| 184,185  
Ieva Liepiņa \| 1967 \| 123 \| 246,247  
Ieva Markēviča–Caruka \| 1964 \| 128 \| 256,257  
Igors Bernāts \| 1965 \| 31 \| 60,61  
Ilgvars Zalāns \| 1962 \| 207 \| 416,417  
Ilona Abiļeva \| 1983 \| 16 \| 30,31  
Ilze Aulmane \| 1982 \| 25 \| 48,49  
Ilze Dilāne \| 1970 \| 52 \| 104,105  
Ilze Jaunberga \| 1978 \| 85 \| 170,171  
Ilze Krūmiņa–Karlsone \| 1953 \| 107 \| 214,215  
Ilze Laizāne \| 1966 \| 116 \| 232,233  
Ilze Preisa \| 1976 \| 157 \| 314,315  
Ilze Smildziņa \| 1973 \| 173 \| 348,349  
Inese Gūtmane \| 1965 \| 69 \| 138,139  
Ineta Freidenfelde \| 1971 \| 60 \| 120,121  
Inga Jurova \| 1972 \| 91 \| 182,183  
Inga Ģibiete \| 1979 \| 65 \| 130,131  
Ingemāra Treija \| 1963 \| 189 \| 380,381  
Ingrīda Pičukāne \| 1978 \| 152 \| 304,305  
Ingrīda Sūna \| 1954 \| 186 \| 374,375  
Inguna Krolle–Irbe \| 1965 \| 105 \| 210,211  
Iveta Laure \| 1962 \| 117 \| 234,235  
Iveta Vecenāne \| 1962 \| 195 \| 392,393  
Juris Utāns \| 1959 \| 191 \| 384,385  
Jānis Dukāts \| 1985 \| 53 \| 106,107  
Jānis Murovskis \| 1961 \| 139 \| 278,279  
Jānis Nedēļa \| 1955 \| 140 \| 280,281  
Jānis Ziņģītis \| 1973 \| 213 \| 428,429  
Karinē Paronjanca \| 1982 \| 145 \| 290,291  
Karīna Rungenfelde \| 1978 \| 163 \| 328,329  
Katrīna Sauškina \| 1985 \| 166 \| 334,335  
Katrīna Taivāne \| 1976 \| 187 \| 376,377  
Krista Dzudzilo \| 1989 \| 56 \| 112,113  
Kristīne Jansone \| 1973 \| 82 \| 164,165  
Kristīne Kvitka \| 1983 \| 112 \| 224,225  
Kristīne Markus \| 1986 \| 129 \| 258,259  
Larisa Šellare \| 1959 \| 169 \| 340,341  
Laura Ozola \| 1981 \| 144 \| 288,289  
Laura Prikule \| 1977 \| 159 \| 318,319  
Leonards Laganovskis \| 1955 \| 114 \| 228,229  
Liena Bondare \| 1980 \| 39 \| 76,77  
Liene Abaroniņa \| 1986 \| 15 \| 28,29  
Liene Bernāte \| 1971 \| 30 \| 58,59  
Linda Daņiļevska \| 1971 \| 49 \| 98,99  
Linda Stepīte \| 1966 \| 179 \| 360,361  
Lāsma Pujāte \| 1984 \| 161 \| 324,325  
Līga Jukša \| 1975 \| 87 \| 174,175  
Līga Ķempe \| 1975 \| 96 \| 192,193  
Magone Šarkovska \| 1985 \| 165 \| 332,333  
Marta Zariņa–Ģelze \| 1987–2014 \| 210 \| 422,423  
Maruta Raude \| 1965 \| 162 \| 326,327  
Modris Sapuns \| 1979 \| 164 \| 330,331  
Māra Viška \| 1982 \| 204 \| 410,411  
Māris Abiļevs \| 1956 \| 18 \| 34,35  
Natālija Ušakova \| 1979 \| 190 \| 382,383  
Nele Zirnīte \| 1959 \| 214 \| 430,431  
Neonilla Medvedeva \| 1987 \| 135 \| 270,271  
Nikolajs Krivošeins \| 1960 \| 104 \| 208,209  
Oskars Pavlovskis \| 1985 \| 149 \| 298,299  
Otto Zitmanis \| 1980 \| 215 \| 432,433  
Oļegs Dzjubenko \| 1964 \| 55 \| 110,111  
Rasa Jansone \| 1975 \| 83 \| 166,167  
Rasa Šulca \| 1979 \| 185 \| 372,373  
Rauls Zitmanis \| 1959 \| 216 \| 434,435  
Reinis Dzudzilo \| 1987 \| 57 \| 114,115  
Reinis Virtmanis \| 1976 \| 203 \| 408,409  
Rihards Delvers \| 1968 \| 51 \| 102,103  
Roberts Koļcovs \| 1966 \| 100 \| 200,201  
Romāns Korovins \| 1973 \| 101 \| 202,203  
Sabīne Vekmane \| 1984 \| 197 \| 396,397  
Sandra Strēle \| 1961 \| 182 \| 366,367  
Sarmīte Caune \| 1961 \| 46 \| 92,93  
Sergejs Djomins \| 1974 \| 54 \| 108,109  
Sigita Daugule \| 1971 \| 50 \| 100,101  
Signe Vanadziņa \| 1973 \| 193 \| 388,389  
Signe Štrauss \| 1973 \| 180 \| 362,363  
Sofija Šellare \| 1985 \| 167 \| 336,337  
Solveiga Vasiļjeva \| 1954 \| 194 \| 390,391  
Uģis Šēnbergs \| 1954 \| 168 \| 338,339  
Valdis Brože \| 1974 \| 43 \| 86,87  
Velta Emīlija Platupe \| 1981 \| 153 \| 306,307  
Verners Lazdāns \| 1965 \| 119 \| 238,239  
Viktorija Matisone \| 1972 \| 131 \| 262,263  
Vitauts Pronckus \| 1975 \| 160 \| 320,321  
Vitolds Kucins \| 1955 \| 109 \| 218,219  
Vladimirs Neilands \| 1954 \| 142 \| 284,285  
Zane Balode \| 1983 \| 29 \| 56,57  
Zigurds Poļikovs \| 1955 \| 156 \| 312,313  
Zoja Geraskina \| 1954 \| 63 \| 126,127  

---

## C) HTML-without-JSON gap note (deferred)

The HTML-without-JSON pipeline integrity gap remains **untouched** in this execution and is explicitly deferred to **Instruction 21**.

No remediation writes were made for this deferred item in this step.

