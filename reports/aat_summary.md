# AAT Vocabulary Linking — Implementation Summary

**Date:** 2026-05-27  
**Status:** ✅ Complete and deployed

## What Was Built

### 1. Curated AAT Mapping File
**Location:** `artbase_export/data/_vocab/aat_mapping.json`

A hand-curated mapping of common art cataloguing terms to Getty AAT URIs:

- **Materials & Techniques** (14 entries): oil on canvas, watercolor on paper, lithograph, etching, etc.
- **Object Types** (7 entries): painting, drawing, print, sculpture, photograph, etc.
- **Genres** (9 entries): landscape, portrait, still life, seascape, religious, abstract, etc.

Each material/technique entry breaks down into components (technique, medium, support) for precise LIDO export.

### 2. AAT Linking Script
**Location:** `scripts/aat_link.py`

CLI tool that reads artwork JSONs and adds AAT URI references based on the mapping:

```bash
python3 scripts/aat_link.py --all              # link all artworks
python3 scripts/aat_link.py --artwork AP-...   # single artwork
python3 scripts/aat_link.py --all --dry-run    # preview changes
```

**Features:**
- Case-insensitive, trimmed matching
- Tracks unmatched terms in `reports/aat_unmatched.json` for future mapping expansion
- Idempotent — can be re-run safely
- Preserves original human-readable text; adds URIs alongside

**Output format in canonical JSON:**
```json
{
  "aat_terms": {
    "type": {
      "label": "paintings (visual works)",
      "aat_uri": "http://vocab.getty.edu/aat/300033618"
    },
    "materials": [
      {"role": "technique", "label": "oil painting (technique)", "aat_uri": "..."},
      {"role": "medium", "label": "oil paint (paint)", "aat_uri": "..."},
      {"role": "support", "label": "poplar", "aat_uri": "..."}
    ]
  }
}
```

### 3. Passport Template Updates
**Modified:** `templates/passport.html.j2`

Added AAT vocabulary links to three Object ID fields:

- **i. Type of Object:** Shows AAT object type term below the free text
- **ii. Materials & Techniques:** Shows technique, medium, support components (separated by ·)
- **vii. Subject:** Shows AAT genre term when applicable

**Visual design:**
- Small grey text (11px Public Sans)
- Dotted underline on hover
- Links open in new tab to Getty AAT pages
- Does not replace readable text — augments it

## Results

**Artworks processed:** 2  
**Fields linked:** 4 (2 × type + 2 × materials)  
**AAT URIs added:** 8 total (2 type URIs + 6 material component URIs)

**Live examples:**
- https://elembam.github.io/artbase-catalogue/AP-2026-000001.html (Mona Lisa)
- https://elembam.github.io/artbase-catalogue/AP-2026-000002.html (Herberts Šiliņš artwork)

## Design Decisions

### Why Curated Mapping (Not Fuzzy Matching)?
- **Precision over coverage:** AAT has 54,000+ terms. Fuzzy matching produces noise.
- **Quality gate:** Every mapping is human-verified.
- **Extensibility:** As new terms appear, we review and add them intentionally.
- **No network dependency:** Mapping is local; works offline.

### Why Store AAT URIs Separately from Free Text?
- **Preserve original cataloguer language:** "Oil on poplar panel" is more human-readable than "oil painting (technique), oil paint (paint), poplar"
- **Enable dual export:** LIDO gets URIs, human passports get readable text
- **Audit trail:** We can see what the cataloguer wrote vs. what AAT matched

### Why Not Auto-Query AAT on Each Run?
- **AAT URIs are stable:** Getty maintains persistent identifiers
- **AAT updates are rare:** No need for live lookups
- **Performance:** Processing 10,000 artworks with network calls = slow
- **Reliability:** No dependency on external API availability

## Next Steps (When Needed)

1. **Expand mapping as collection grows:**
   - Check `reports/aat_unmatched.json` after each import
   - Research correct AAT terms at https://www.getty.edu/research/tools/vocabularies/aat/
   - Add to `data/_vocab/aat_mapping.json`
   - Re-run `aat_link.py --all`

2. **Use AAT terms in LIDO export:**
   - Material component URIs go into `<eventMaterialsTech>` with `@pref` on technique
   - Object type URI goes into `<objectWorkType>`
   - Genre URI goes into `<subjectConcept>`

3. **Consider adding AAT links for:**
   - Artist roles (currently free text "painter")
   - Conservation techniques
   - Exhibition types
   - Collection types

## Files Changed

**Created:**
- `artbase_export/data/_vocab/aat_mapping.json` (4.2 KB)
- `scripts/aat_link.py` (7.6 KB)

**Modified:**
- `artbase_export/data/artworks/AP-2026-000001.json` (added aat_terms)
- `artbase_export/data/artworks/AP-2026-000002.json` (added aat_terms)
- `templates/passport.html.j2` (added AAT link display + CSS)

**Deployed:**
- `passports/AP-2026-000001.html` (430 KB, with embedded image)
- `passports/AP-2026-000002.html` (22 KB)
