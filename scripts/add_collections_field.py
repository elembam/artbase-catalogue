#!/usr/bin/env python3
"""
One-shot script: add 'collections' field to artist JSON files for known LNMM members.
Safe to re-run — only sets the field if the collection entry isn't already present.
"""

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ARTISTS_DIR = REPO_ROOT / "artbase_export" / "data" / "artists"

LNMM = {
    "id": "lnmm",
    "name": "Latvian National Museum of Art",
    "short_name": "LNMM",
    "url": "https://arsaccordia.com/collections/lnmm/",
}

# artbase_id → (work_count, display_name_in_collection)
LNMM_MEMBERS = {
    "ART-ROZENTALS-1866":   (39, "Janis Rozentāls"),
    "ART-VALTERS-1869":     (28, "Johann Walter"),
    "ART-PADEGS-1911":      (25, "Kārlis Padegs"),
    "ART-KAZAKS-1895":      (20, "Jēkabs Kazaks"),
    "ART-GROSVALDS-1891":   (19, "Jāzeps Grosvalds"),
    "ART-PURVITIS-1872":    (18, "Vilhelms Purvītis"),
    "ART-SUTA-1896":        (18, "Romans Suta"),
    "ART-PERLE-1875":       (16, "Rūdolfs Pērle"),
    "ART-KRASTINS-1882":    (12, "Pēteris Krastiņš"),
    "ART-ALKSNIS-1864":     (11, "Ādams Alksnis"),
    "ART-HUNS-1831":        (10, "Kārlis Hūns"),
    "ART-FEDERS-1838":      (9,  "Jūlijs Feders"),
    "ART-ZARINS-1869":      (9,  "Rihards Zariņš"),
    "ART-TIDEMANIS-1897":   (7,  "Jānis Tīdemanis"),
    "ART-UDERS-1868":       (7,  "Teodors Ūders"),
    "ART-LIEPINS-1894":     (6,  "Jānis Liepiņš"),
    "ART-KLUCIS-1895":      (5,  "Gustavs Klucis"),
    "ART-PLITE-PLEITA-1888":(5,  "Alfrēds Plīte-Pleita"),
    "ART-ELIASS-1887":      (4,  "Ģederts Eliass"),
    "ART-TONE-1892":        (2,  "Valdemārs Tone"),
    "ART-SVEMPS-1897":      (2,  "Leo Svemps"),
    "ART-LIBERTS-1895":     (1,  "Ludolfs Liberts"),
    "ART-STRUNKE-1894":     (1,  "Niklāvs Strunke"),
    "ART-CIRULIS-1883":     (1,  "Ansis Cīrulis"),
    "ART-FILKA-1891":       (1,  "Alberts Filka"),
    "ART-KALVE-1882":       (1,  "Pēteris Kalve"),
}

updated = []
for artbase_id, (work_count, display_name) in LNMM_MEMBERS.items():
    path = ARTISTS_DIR / f"{artbase_id}.json"
    if not path.exists():
        print(f"  MISSING: {path.name}")
        continue

    data = json.loads(path.read_text())

    # Fix Valters name_variants while we're here
    if artbase_id == "ART-VALTERS-1869":
        variants = data.get("identity", {}).get("name_variants") or []
        needed = ["Johann Walter", "Johann Walter-Kurau"]
        for v in needed:
            if v not in variants:
                variants.append(v)
        data["identity"]["name_variants"] = variants
        data["identity"]["preferred_name_language"] = "lv"

    # Build the collection entry
    entry = {
        "id": LNMM["id"],
        "name": LNMM["name"],
        "short_name": LNMM["short_name"],
        "url": LNMM["url"],
        "work_count": work_count,
        "display_name": display_name,
    }

    existing = data.get("collections") or []
    ids_present = {e.get("id") for e in existing}
    if "lnmm" not in ids_present:
        existing.append(entry)
    else:
        # Update in place
        existing = [entry if e.get("id") == "lnmm" else e for e in existing]
    data["collections"] = existing

    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    print(f"  ✓ {artbase_id}  ({work_count} works)")
    updated.append(artbase_id)

print(f"\nDone — {len(updated)} files updated.")
