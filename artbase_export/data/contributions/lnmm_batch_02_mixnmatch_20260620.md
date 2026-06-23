# LNMM Batch 02 — Mix'n'match #8050 Registration List
## 2026-06-20

**Catalogue:** Mix'n'match #8050 (Ars Accordia)
**URL:** https://mix-n-match.toolforge.org/#/catalog/8050
**Purpose:** Register the 5 artwork items from lnmm_batch_02 so they appear in Mix'n'match for
community curation and automatic reconciliation. This creates a bidirectional link between the
ArtBase passport and the Wikidata item.

---

## Pre-flight

- [ ] `lnmm_batch_02_artwork_items_20260620.qs` has been submitted and QIDs are returned
- [ ] All four CREATE items (004, 006, 017, 019) have confirmed Wikidata QIDs
- [ ] Q22043968 (001 enrich) was already in Mix'n'match — verify it is already marked as matched

---

## Items to register

| ArtBase ID | Passport title | Wikidata QID | Status |
|---|---|---|---|
| AA/LV/LNMA/001 | Princess with a Monkey | Q22043968 | Already exists — verify matched in #8050 |
| AA/LV/LNMA/004 | Carousel | _TBD after CREATE_ | Register after batch submitted |
| AA/LV/LNMA/006 | From Church (After the Service) | _TBD after CREATE_ | Register after batch submitted |
| AA/LV/LNMA/017 | Young Gipsy Woman | _TBD after CREATE_ | Register after batch submitted |
| AA/LV/LNMA/019 | Country Landscape | _TBD after CREATE_ | Register after batch submitted |
| AA/LV/LNMA/012 | Folk Festival at Kokmuiža | _Not yet_ | Hold until attribution confirmed |

---

## How to register

1. Go to https://mix-n-match.toolforge.org/#/catalog/8050
2. For each item listed above: search for the ArtBase ID or title
3. If the item already appears (from a previous import): confirm it is matched to the correct QID
4. If the item is not yet in the catalogue: use the "Add entry" button with:
   - **External ID:** the ArtBase ID (e.g., `AA/LV/LNMA/004`)
   - **Label:** the title in English
   - **Wikidata QID:** the QID from the batch submission
5. After registering: paste the QID into the "Submission status" table in `lnmm_batch_02_artwork_items_20260620.review.md`

---

## After registration

Update each passport's `authority_links` block:
```json
"wikidata": {
  "id": "Q<NEW>",
  "status": "confirmed",
  "verified_date": "2026-06-20",
  "note": "Wikidata item created via lnmm_batch_02"
}
```

Then recompute:
```bash
python3 scripts/build_passport_score.py --all
python3 scripts/build_collection_score.py COL-LNMM --check
```

Add a line to the LNMM collection page:
> 4 works contributed to Wikidata · registered in Mix'n'match #8050

---

## Registration status

- 001 (Q22043968): _______________
- 004: _______________
- 006: _______________
- 017: _______________
- 019: _______________
