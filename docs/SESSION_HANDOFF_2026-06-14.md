# Session Handoff — 2026-06-14

Knowledge Graph eligibility improvements, SEO infrastructure, and site index.
Commit: `ea0559b` pushed to `main` → GitHub Pages live.

---

## What was done

### 1. Passport generator — JSON-LD builder added

**File:** `scripts/passport_generator.py`

Added two new functions:

- `_confirmed_id(authority_links, key)` — returns an authority ID only when its status is `"confirmed"`, preventing unverified IDs from leaking into structured data
- `build_jsonld(artwork, artist, image_src)` — builds the complete `VisualArtwork` JSON-LD dict, now passed to the template as `jsonld`

**What the generated JSON-LD now includes vs. before:**

| Property | Before | After |
|---|---|---|
| `width` / `height` | text string in `size` | `QuantitativeValue` with `unitCode: "CMT"` |
| `mainEntityOfPage` | absent | declares passport as canonical entity home |
| `creator["@id"]` | absent | `arsaccordia.com/artists/{artbase_id}` |
| `creator["sameAs"]` | Wikidata + VIAF | Wikidata + VIAF + internal artist page URL |
| `creator["birthDate/deathDate"]` | absent | from artist `life` data |
| `sameAs` on artwork | absent | populated when `authority_links.wikidata.id` is confirmed |
| `isPartOf` | absent | `{"@id": "https://arsaccordia.com"}` |

**To regenerate a passport after this change:**
```bash
python3 scripts/passport_generator.py AP-2026-000002
cp passports/AP-2026-000002.html AP-2026-000002.html
```

> **AP-2026-000001 (Mona Lisa) not yet regenerated** — it still uses the pre-built HTML. Run the command above for `AP-2026-000001` to update it, but note the 565 KB page size issue (see Outstanding Work).

---

### 2. Artist profile generator — Person JSON-LD added

**File:** `scripts/artist_profile_generator.py`

Added:

- `_confirmed_id()` — same helper as in passport generator
- `build_person_jsonld(artist)` — builds `Person` schema, passed to template as `person_jsonld`

**What the generated JSON-LD includes:**

```json
{
  "@context": "https://schema.org",
  "@type": "Person",
  "@id": "https://arsaccordia.com/artists/{artbase_id}",
  "name": "...",
  "url": "https://arsaccordia.com/artists/{artbase_id}.html",
  "birthDate": "1926",
  "deathDate": "2001",
  "birthPlace": {"@type": "Place", "name": "..."},
  "nationality": "Latvian",
  "hasOccupation": [{"@type": "Role", "roleName": "painter"}],
  "mainEntityOfPage": {"@id": "...", "isPartOf": {"@id": "https://arsaccordia.com"}},
  "sameAs": [
    "https://www.wikidata.org/wiki/Q...",
    "https://viaf.org/viaf/...",
    "https://vocab.getty.edu/page/ulan/..."
  ]
}
```

Only `"confirmed"` authority IDs appear in `sameAs`. Candidate/unverified IDs are silently omitted.

**To regenerate all artist pages:**
```bash
python3 scripts/artist_profile_generator.py --all
cp passports/artists/*.html artists/
```

All 289 artist pages regenerated and deployed in this session.

---

### 3. Artist profile template — head fixes

**File:** `templates/artist_profile.html.j2`

Three changes to the `<head>`:

1. **Title** — `{{ artist.identity.preferred_name }} — ArtBase` → `{{ artist.identity.preferred_name }} — Ars Accordia`
2. **Meta description** — updated to mention authority links (Wikidata, ULAN, VIAF)
3. **Canonical link** — `<link rel="canonical" href="https://arsaccordia.com/artists/{{ artist.artbase_id }}.html">` added
4. **JSON-LD block** — `<script type="application/ld+json">{{ person_jsonld | tojson(indent=2) }}</script>` added before `</head>`

---

### 4. Homepage — Organization JSON-LD + footer link

**Files:** `index.html`, `templates/index.html.j2`

- Replaced bare `WebSite` JSON-LD with a JSON-LD array containing both `WebSite` and `Organization` types
- `Organization` includes `name`, `url`, `description`, `email`, `foundingDate`, `knowsAbout` (Wikidata concept URIs for art cataloguing and cultural heritage)
- Added `Site Index` link to the footer alongside the existing About link

---

### 5. About page — Organization JSON-LD

**File:** `about/index.html`

Same `Organization` JSON-LD block added before `</head>`. No other changes.

---

### 6. New: robots.txt

**File:** `robots.txt` (repo root, previously absent)

```
User-agent: *
Allow: /

Sitemap: https://arsaccordia.com/sitemap.xml
```

Without this file, Google's crawler had no guidance and the sitemap was not auto-discoverable by crawlers other than ones it was manually submitted to.

---

### 7. New: /sitemap/ — human-readable site index

**File:** `sitemap/index.html`

A styled HTML page (matching the Ars Accordia paper/seal-red/gold palette) listing:
- All main navigation sections with descriptions and URLs
- All 2 published Artwork Passports with links
- Artist directory summary (289 records) with sub-links (Latvia, Sweden, A–Z)
- Machine-readable feeds (sitemap.xml, OAI-PMH)

Accessible at `arsaccordia.com/sitemap/`.
Also added to `sitemap.xml` at priority 0.5.

---

### 8. Google Search Console

Sitemap submitted manually at `https://search.google.com/search-console` for `arsaccordia.com`.
Initial status showed "Couldn't fetch" — this resolves once `robots.txt` and the latest deploy propagate (usually within 15–30 minutes of the push).

**Next action in Search Console:** use the URL Inspection tool on `https://arsaccordia.com` and click "Request Indexing" to kick off crawling immediately rather than waiting for the natural cycle.

---

## Files changed in this session

| File | Change |
|---|---|
| `scripts/passport_generator.py` | Added `build_jsonld()`, `_confirmed_id()`; `jsonld` now in context |
| `scripts/artist_profile_generator.py` | Added `build_person_jsonld()`, `_confirmed_id()`; `person_jsonld` now in context |
| `templates/artist_profile.html.j2` | Title, meta, canonical, JSON-LD block |
| `templates/index.html.j2` | Organization + WebSite JSON-LD array |
| `index.html` | Organization JSON-LD, Site Index footer link, date |
| `about/index.html` | Organization JSON-LD |
| `AP-2026-000002.html` | Regenerated with new JSON-LD |
| `artists/*.html` (289 files) | Regenerated with Person JSON-LD, canonical, branding |
| `sitemap.xml` | Added `/sitemap/` entry |
| `robots.txt` | New file |
| `sitemap/index.html` | New file |
| `docs/KNOWLEDGE_GRAPH_IMPROVEMENTS.md` | New — technical implementation guide |
| `docs/KNOWLEDGE_PANEL_READINESS.md` | New — copilot readiness checklist (for reference) |

---

## Outstanding work

### High priority

**Wikidata artwork item for AP-2026-000002** (Juras noskana / Herberts Siliņš)
This is the single highest-leverage remaining action. Create a Wikidata item with 15–20 sourced properties (see `docs/KNOWLEDGE_GRAPH_IMPROVEMENTS.md` §1 for the exact property list), including `P973 (described at URL)` → `https://arsaccordia.com/AP-2026-000002.html`.

Once the QID exists:
1. Add it to `artbase_export/data/artworks/AP-2026-000002.json` under `authority_links.wikidata.id` with `status: "confirmed"`
2. Run `python3 scripts/passport_generator.py AP-2026-000002 && cp passports/AP-2026-000002.html AP-2026-000002.html`
3. The `sameAs` on the artwork will appear in the JSON-LD automatically

**Regenerate AP-2026-000001**
The Mona Lisa passport still uses a pre-built HTML from before the new generator. Run:
```bash
python3 scripts/passport_generator.py AP-2026-000001
cp passports/AP-2026-000001.html AP-2026-000001.html
```
Note: this passport is 565 KB due to a base64-embedded image (405 KB). See page size note below.

### Medium priority

**Page size — AP-2026-000001**
The Mona Lisa passport is 565 KB; 405 KB is a base64-embedded image. Google's Core Web Vitals ranking signal will penalise this. Options:
- Serve a separate low-resolution preview image externally and reference it via `<img src="...">` for the public page
- Keep the base64 version as the downloadable/client deliverable, serve a lighter public version

**Biography text in artist records**
The `descriptors.biography_summary` field is `null` for all records. Even 50–100 words of text per artist page transforms a thin page into content Google can rank for queries like "Herberts Siliņš painter Latvia". Populate this in Airtable → re-export → regenerate.

**Getty AAT URIs for materials**
The `object_id.materials_aat` field exists in the artwork JSON but is empty (`[]`) for current records. Populating these would allow the passport generator to emit `additionalType` and structured `material` objects with Getty AAT URIs — stronger entity anchoring for the Knowledge Graph.

### Reference documents

- `docs/KNOWLEDGE_GRAPH_IMPROVEMENTS.md` — full technical guide, ranked by leverage
- `docs/KNOWLEDGE_PANEL_READINESS.md` — per-passport validation checklist
- `docs/ARTBASE_WIKIDATA_PROFILE.md` — Wikidata contribution workflow
