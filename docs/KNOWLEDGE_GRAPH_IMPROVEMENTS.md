# Knowledge Graph Eligibility — Improvements for Ars Accordia

*Written against the current codebase state as of 2026-06-14.*

The advisory you received is correct: you have already built the eligibility stack.
This document maps each of its recommendations to the **specific gap in the current code**
and states exactly what needs to change — prioritised by leverage.

---

## Tier 1 — Highest leverage (do these first)

### 1. Wikidata artwork items for passported works

**Why it matters:** Wikidata is currently the dominant lever for Google Knowledge Graph
entity formation. For artworks, a well-sourced item with 15–20 properties is often the
tipping point that triggers a panel, and it makes any existing panel richer.

**Current state:** The Silins artwork (AP-2026-000002) is not yet a Wikidata item.
The passport exists and is the canonical source; the graph feed is missing.

**What to do (not a code change — Wikidata editing):**

Create a new Wikidata item for *Juras noskana (Sea Mood)*, 1979, with at minimum:

| Property | Value |
|---|---|
| P31 (instance of) | Q3305213 (painting) |
| P170 (creator) | Q23054868 (Herberts Siliņš) |
| P571 (inception) | 1979 |
| P186 (material) | oil paint (Q296955); canvas (Q4259259) |
| P2079 (fabrication method) | oil painting (Q174705) |
| P276 (location) | private collection |
| P195 (collection) | omit or mark "private collection" |
| P217 (inventory number) | AP-2026-000002 |
| P973 (described at URL) | https://arsaccordia.com/AP-2026-000002.html |
| P18 (image) | upload via Wikimedia Commons if owner permits |

Each statement should cite the passport as source (S854 = URL, S813 = access date).

Once the Wikidata item is created, **add its QID to the artwork JSON-LD** as `sameAs`
(see item 3 below).

---

### 2. Add `Person` JSON-LD to artist profile pages

**Current gap:** The artist profile template ([templates/artist_profile.html.j2](../templates/artist_profile.html.j2):6–7) emits no structured data at all, and the title/meta still say "ArtBase" rather than "Ars Accordia". Google cannot parse the artist as a named entity from these pages.

**What to add** — insert before `</head>` in [templates/artist_profile.html.j2](../templates/artist_profile.html.j2):

```html
<link rel="canonical" href="https://arsaccordia.com/artists/{{ artist.artbase_id }}.html">
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Person",
  "@id": "https://arsaccordia.com/artists/{{ artist.artbase_id }}",
  "name": "{{ artist.identity.preferred_name }}",
  "url": "https://arsaccordia.com/artists/{{ artist.artbase_id }}.html",
  {% if artist.identity.birth_year %}"birthDate": "{{ artist.identity.birth_year }}",{% endif %}
  {% if artist.identity.death_year %}"deathDate": "{{ artist.identity.death_year }}",{% endif %}
  {% if artist.identity.nationality %}"nationality": "{{ artist.identity.nationality }}",{% endif %}
  "sameAs": [
    {% set links = [] %}
    {% if wikidata_qid %}{% set _ = links.append("https://www.wikidata.org/wiki/" ~ wikidata_qid) %}{% endif %}
    {% set ulan = (artist.authority_links.ulan or {}).get("id") %}
    {% if ulan %}{% set _ = links.append("https://vocab.getty.edu/page/ulan/" ~ ulan) %}{% endif %}
    {% set viaf = (artist.authority_links.viaf or {}).get("id") %}
    {% if viaf %}{% set _ = links.append("https://viaf.org/viaf/" ~ viaf) %}{% endif %}
    {% set rkd = (artist.authority_links.rkd or {}).get("id") %}
    {% if rkd %}{% set _ = links.append("https://rkd.nl/en/explore/artists/" ~ rkd) %}{% endif %}
    {{ links | tojson | replace('[', '') | replace(']', '') }}
  ],
  "subjectOf": {
    "@type": "WebPage",
    "url": "https://arsaccordia.com/artists/{{ artist.artbase_id }}.html",
    "name": "{{ artist.identity.preferred_name }} — Ars Accordia Catalogue Record",
    "isPartOf": {"@id": "https://arsaccordia.com"}
  }
}
</script>
```

Also fix the title and meta on lines 6–7:
```html
<meta name="description" content="Artist record — {{ artist.identity.preferred_name }}. Ars Accordia scholarly catalogue with authority links to Wikidata, Getty ULAN, and VIAF.">
<title>{{ artist.identity.preferred_name }} — Ars Accordia</title>
```

---

## Tier 2 — High leverage

### 3. Enrich VisualArtwork JSON-LD on passport pages

**Current state:** [passports/AP-2026-000002.html](../passports/AP-2026-000002.html):737–765 has a correct `VisualArtwork` block but is missing several properties that the advisory identifies as contributing to graph density.

**Gaps in the current passport JSON-LD:**

| Missing property | Why it matters |
|---|---|
| `sameAs` on the artwork itself | Without this, Google cannot reconcile the passport with the Wikidata artwork item |
| `width` / `height` as `QuantitativeValue` | Disambiguates works; `size: "81 x 81 cm"` is unstructured text |
| `image` | If an image URL exists, P18-equivalent signal for the graph |
| `artworkSurface` | Additional disambiguation |
| `about` / `genre` | Iconographic subject signal (maps to Wikidata P180) |
| `locationCreated` | Place of creation |
| `isPartOf` referencing the site | Entity anchoring |

**What the enriched block should look like** in [templates/passport.html.j2](../templates/passport.html.j2), replacing the current `{{ jsonld | tojson(indent=2) }}` pass-through with a structured block that the Python generator populates — or by extending the `jsonld` dict in the generator to include these fields:

```python
# In the passport generator, add to the jsonld dict:
jsonld["sameAs"] = [wikidata_artwork_qid]  # once QID exists
jsonld["width"]  = {"@type": "QuantitativeValue", "value": width_cm, "unitCode": "CMT"}
jsonld["height"] = {"@type": "QuantitativeValue", "value": height_cm, "unitCode": "CMT"}
if image_url:
    jsonld["image"] = image_url
jsonld["isPartOf"] = {"@id": "https://arsaccordia.com"}
jsonld["mainEntityOfPage"] = "https://arsaccordia.com/" + artwork.artbase_id + ".html"
```

The `sameAs` on the `creator` object is already correct and should be kept.

---

### 4. Add `Organization` JSON-LD to the homepage and about page

**Current state:** [index.html](../index.html):351–358 has only a bare `WebSite` block.
[about/index.html](../about/index.html) has no structured data at all.

Google needs to understand what Ars Accordia *is* as an organisation before it can
treat its records as authoritative. The `Organization` type provides that.

**Add to `index.html` and `about/index.html`** (alongside the existing `WebSite` block):

```json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "@id": "https://arsaccordia.com",
  "name": "Ars Accordia",
  "url": "https://arsaccordia.com",
  "description": "Scholarly art cataloguing service issuing Artwork Passports for European private and corporate collections to international museum standards.",
  "email": "catalogue@arsaccordia.com",
  "foundingDate": "2026",
  "knowsAbout": [
    "https://www.wikidata.org/wiki/Q18969458",
    "https://www.wikidata.org/wiki/Q11798"
  ],
  "sameAs": []
}
```

The `sameAs` array should be populated once Ars Accordia has its own Wikidata item
(which it should, as the registry itself is a notable cultural heritage entity).
`knowsAbout` Q18969458 = art cataloguing; Q11798 = cultural heritage — these
help Google contextualise the organisation's domain.

---

### 5. Add `sameAs` cross-links from passports to artist pages

**Current gap:** The `creator` node in each passport's JSON-LD provides Wikidata and VIAF
`sameAs` links for the artist, but does not link to the artist's own page on Ars Accordia.

This means Google cannot follow the internal entity graph from artwork → artist record
on the same site. Add to the `creator` object:

```json
"creator": {
  "@type": "Person",
  ...existing fields...,
  "sameAs": [
    "https://www.wikidata.org/wiki/Q23054868",
    "https://viaf.org/viaf/15148752166141201333",
    "https://arsaccordia.com/artists/ART-SILINS-1926"
  ]
}
```

The internal `sameAs` URL (without `.html`) matches the `@id` in the artist page's
`Person` block (once item 2 above is implemented), creating a navigable graph.

---

## Tier 3 — Medium leverage

### 6. Open Graph and Twitter Card meta tags

**Current state:** No OG or Twitter Card tags on any page.

While these primarily affect social sharing, several graph crawlers (and some structured
data testing tools) treat them as corroborating signals for page identity.

**Add to the `<head>` of each page type:**

*Homepage:*
```html
<meta property="og:type" content="website">
<meta property="og:title" content="Ars Accordia — Scholarly Art Catalogue">
<meta property="og:description" content="Cataloguing European art collections to international museum standards.">
<meta property="og:url" content="https://arsaccordia.com/">
<meta property="og:site_name" content="Ars Accordia">
```

*Passport pages (add to template):*
```html
<meta property="og:type" content="article">
<meta property="og:title" content="Artwork Passport — {{ artwork.object_id.title }}">
<meta property="og:description" content="{{ artwork.object_id.title }} by {{ artwork.object_id.maker_display_name }}, {{ artwork.object_id.creation_date.display }}. Ars Accordia Catalogue.">
<meta property="og:url" content="https://arsaccordia.com/{{ artwork.artbase_id }}.html">
<meta property="og:site_name" content="Ars Accordia">
```

*Artist pages (add to template):*
```html
<meta property="og:type" content="profile">
<meta property="og:title" content="{{ artist.identity.preferred_name }} — Ars Accordia">
<meta property="og:url" content="https://arsaccordia.com/artists/{{ artist.artbase_id }}.html">
<meta property="og:site_name" content="Ars Accordia">
```

---

### 7. Sitemap: add `<image:image>` blocks for passports with images

**Current state:** [sitemap.xml](../sitemap.xml) lists passport URLs but no image data.
Google's image index is a separate feed; adding image metadata increases the surface area
for the entity to be discovered.

Once passports include images (base64-embedded is fine; a CDN URL is better for the
sitemap), add to each passport `<url>` entry:

```xml
<url>
  <loc>https://arsaccordia.com/AP-2026-000002.html</loc>
  <lastmod>2026-05-29</lastmod>
  <priority>0.9</priority>
  <image:image>
    <image:loc>https://arsaccordia.com/images/AP-2026-000002.jpg</image:loc>
    <image:title>Juras noskana (Sea Mood) — Herberts Siliņš</image:title>
  </image:image>
</url>
```

Namespace declaration needed on the root element:
`xmlns:image="http://www.google.com/schemas/sitemap-image/1.1"`

---

## Tier 4 — Good hygiene (low effort, worth doing)

### 8. Fix branding in artist profile template

**File:** [templates/artist_profile.html.j2](../templates/artist_profile.html.j2):6–7

The title and meta description say "ArtBase" — this is the old internal project name.
All public-facing pages should consistently say "Ars Accordia".

Current:
```html
<meta name="description" content="Artist Profile — {{ artist.identity.preferred_name }}. ArtBase scholarly catalogue record.">
<title>{{ artist.identity.preferred_name }} — ArtBase</title>
```

Should be:
```html
<meta name="description" content="Artist record — {{ artist.identity.preferred_name }}. Ars Accordia scholarly catalogue with authority links to Wikidata, Getty ULAN, and VIAF.">
<title>{{ artist.identity.preferred_name }} — Ars Accordia</title>
```

Inconsistent naming across pages undermines entity reconciliation — the Knowledge Graph
needs consistent co-occurrence of the name to build confidence.

---

### 9. Add `mainEntityOfPage` to passport JSON-LD

**Current state:** The `VisualArtwork` block does not declare that the passport page is the
canonical home page for this entity. This is the `mainEntityOfPage` / `isPartOf` signal.

The `@id` on the artwork is set to `https://arsaccordia.com/AP-2026-000002` (without
`.html`) — this is correct as an entity identifier. The page URL is the `.html` variant.
Add:

```json
"mainEntityOfPage": {
  "@type": "WebPage",
  "@id": "https://arsaccordia.com/AP-2026-000002.html",
  "isPartOf": {"@id": "https://arsaccordia.com"}
}
```

This explicitly declares the passport as the entity home page — which is the definition
of the "canonical entity home" the advisory identifies as the second highest-leverage step.

---

## What the advisory says you don't need to change

- The passport URL structure is already correct: stable, permanent, never redirected.
- The `VisualArtwork` type is already correct.
- The canonical link tags on passport pages are already in place.
- The `sameAs` on creator objects (Wikidata + VIAF) is already there.
- The sitemap is comprehensive and correctly declares priorities.
- The LIDO/EODEM export is orthogonal to Knowledge Graph eligibility (it serves museum
  exchange, not Google's crawler).

---

## Recommended implementation order

1. Fix artist profile template (item 2 + 8) — one template change, immediate effect across all 288 artist pages when regenerated.
2. Enrich passport JSON-LD (items 3 + 9) — one template/generator change, immediate effect on both passports.
3. Add homepage `Organization` JSON-LD (item 4).
4. Create Wikidata artwork item for AP-2026-000002 (item 1) — editorial, not code.
5. Add `sameAs` back-link from passports to artist pages (item 5) — depends on item 2 being live first.
6. Open Graph tags (item 6) — template change, low risk.
7. Sitemap image extension (item 7) — when images are available as URLs.
