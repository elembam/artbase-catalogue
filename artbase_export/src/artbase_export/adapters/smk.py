"""
artbase_export/adapters/smk.py

SMKAdapter — first implementation of CollectionSourceAdapter.

Source: Statens Museum for Kunst Open API (api.smk.dk)
        OpenAPI docs: https://api.smk.dk/api/v1/docs/

Field names confirmed against live API 2026-06-26.

Discipline (from Spec 16):
- Ars Accordia cross-references and cites SMK; never invents data.
- Rights are read per-object from the public_domain flag; never assumed CC0.
- Scope tags each authority link; scope is never a scoring weight.
- Wikidata tasks are written to data/contributions/ for human review — never
  auto-committed.
"""

from __future__ import annotations

import json
import urllib.parse
import urllib.request
from datetime import date, timezone, datetime
from pathlib import Path
from typing import Optional

from .base import CollectionSourceAdapter

# ── SMK API constants ─────────────────────────────────────────────────────────

SMK_API_BASE    = "https://api.smk.dk/api/v1"
SMK_OPEN_BASE   = "https://open.smk.dk/artwork/image"

# Wikidata QID for Statens Museum for Kunst (confirmed)
SMK_WIKIDATA_QID = "Q671249"

# Authority scope values (mirrors AuthorityScope enum — kept as strings to
# avoid circular imports; the JSON output uses these strings directly)
SCOPE_ARTWORK   = "artwork_object"
SCOPE_ARTIST    = "artist_maker"

# Status values
STATUS_APPROVED = "approved_institutional_source"
STATUS_CONFIRMED = "confirmed"
STATUS_CANDIDATE = "candidate_verify"


# ── HTTP helpers ──────────────────────────────────────────────────────────────

def _get_json(url: str) -> dict | list:
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode())


# ── Dimension extraction ──────────────────────────────────────────────────────

def _dim_cm(dimensions: list[dict], type_name: str) -> Optional[float]:
    """Extract a dimension value in cm by Danish type name (højde/bredde/dybde)."""
    for d in dimensions:
        if d.get("type", "").lower() == type_name.lower() and d.get("unit", "").lower() == "centimeter":
            try:
                return float(d["value"])
            except (KeyError, ValueError, TypeError):
                pass
    return None


def _dim_display(dimensions: list[dict]) -> Optional[str]:
    h = _dim_cm(dimensions, "højde")
    w = _dim_cm(dimensions, "bredde")
    d = _dim_cm(dimensions, "dybde")
    if h and w:
        s = f"{h} × {w}"
        if d:
            s += f" × {d}"
        return s + " cm"
    return None


# ── Materials / technique ─────────────────────────────────────────────────────

def _make_materials_display(raw: dict) -> Optional[str]:
    """Combine techniques and materials into a single display string."""
    techniques = raw.get("techniques") or []
    materials  = raw.get("materials") or []
    if techniques:
        return "; ".join(techniques)
    if materials:
        return "; ".join(materials)
    return None


# ── Date extraction ───────────────────────────────────────────────────────────

def _parse_year(dt_str: Optional[str]) -> Optional[int]:
    if not dt_str:
        return None
    try:
        return int(dt_str[:4])
    except (ValueError, TypeError):
        return None


# ── SMKAdapter ────────────────────────────────────────────────────────────────

class SMKAdapter(CollectionSourceAdapter):
    """Adapter for the SMK Open API (api.smk.dk/api/v1/)."""

    def fetch_object_by_id(self, object_id: str) -> dict:
        url = f"{SMK_API_BASE}/art/?object_number={urllib.parse.quote(object_id)}"
        data = _get_json(url)
        items = data.get("items") or []
        if not items:
            raise ValueError(f"SMK: object '{object_id}' not found")
        return items[0]

    def search_objects(self, query: str) -> list[dict]:
        url = f"{SMK_API_BASE}/art/search/?keys={urllib.parse.quote(query)}"
        data = _get_json(url)
        return data.get("items") or []

    # ── Normalisation ─────────────────────────────────────────────────────────

    def normalize_to_object_record(self, raw: dict) -> dict:
        """Map a raw SMK record to the canonical passport dict.

        Only fields present in raw are populated — gaps stay gaps.
        """
        obj_num   = raw.get("object_number", "")
        today     = date.today().isoformat()

        # Title: take the first entry (primary museum title)
        titles    = raw.get("titles") or []
        title     = titles[0]["title"] if titles else None

        # Creator
        production = raw.get("production") or []
        maker_display = None
        if production:
            p = production[0]
            maker_display = p.get("creator")  # "Hunæus, Andreas Herman"

        # Date
        prod_dates = raw.get("production_date") or []
        date_display    = None
        date_earliest   = None
        date_latest     = None
        if prod_dates:
            pd = prod_dates[0]
            date_display  = pd.get("period")            # "1843-1847"
            date_earliest = _parse_year(pd.get("start"))
            date_latest   = _parse_year(pd.get("end"))
            # If period absent but start == end, use year only
            if not date_display and date_earliest:
                date_display = str(date_earliest) if date_earliest == date_latest else \
                               f"{date_earliest}–{date_latest}"

        # Medium / materials
        materials_display = _make_materials_display(raw)

        # Dimensions
        dims              = raw.get("dimensions") or []
        height_cm         = _dim_cm(dims, "højde")
        width_cm          = _dim_cm(dims, "bredde")
        depth_cm          = _dim_cm(dims, "dybde")
        dimensions_display = _dim_display(dims)

        # Object type
        obj_names  = raw.get("object_names") or []
        object_type = obj_names[0]["name"] if obj_names else None

        # Inventory number
        inventory_number = obj_num

        # Location / collection
        dept = raw.get("responsible_department")
        current_location = raw.get("current_location_name")

        # Provenance — acquisition step if acquisition_date present
        provenance_steps = []
        acq_date = raw.get("acquisition_date")
        if acq_date:
            acq_year = _parse_year(acq_date)
            provenance_steps.append({
                "step":        1,
                "description": "Acquired by Statens Museum for Kunst",
                "date":        str(acq_year) if acq_year else None,
                "holder":      "Statens Museum for Kunst",
                "type":        "acquisition",
                "source":      f"SRC-SMK-API-{obj_num}",
                "source_note": "Acquisition date per SMK Open API record",
            })

        # Object history note (provenance narrative) if present
        hist = raw.get("object_history_note")
        if hist:
            provenance_steps.append({
                "step":        len(provenance_steps) + 1,
                "description": hist,
                "type":        "historical_note",
                "source":      f"SRC-SMK-API-{obj_num}",
            })

        # Rights
        rights = self.extract_rights(raw)

        # Media (gated by rights)
        media = self.extract_media(raw)

        # Authority links
        authority_links = {
            "wikidata": {
                "scope":  SCOPE_ARTWORK,
                "system": "Wikidata",
                "id":     None,
                "uri":    None,
                "status": "search_needed",
                "notes":  "Wikidata artwork QID not yet reconciled",
            },
            "artbase_id": None,
            "work_level": self.extract_authority_links(raw),
        }

        # Source
        source_citation = self.extract_source_citation(raw)
        source_id = source_citation["source_id"]

        record = {
            "_schema":              "artbase:artwork:v1",
            "_source_adapter":      "SMKAdapter",
            "artbase_id":           f"SMK-{obj_num}",
            "artbase_canonical_id": None,
            "version":              1,
            "created":              today,
            "exported":             datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "visibility":           "private",

            "object_id": {
                "object_type":          object_type,
                "materials":            materials_display,
                "dimensions_display":   dimensions_display,
                "height_cm":            height_cm,
                "width_cm":             width_cm,
                "depth_cm":             depth_cm,
                "title":                title,
                "title_original":       title,
                "date_display":         date_display,
                "date_earliest":        date_earliest,
                "date_latest":          date_latest,
                "maker_id":             None,  # set after artist reconciliation
                "maker_display_name":   maker_display,
                "inventory_number":     inventory_number,
                "has_photograph":       bool(raw.get("has_image")),
            },

            "location": {
                "collection":       "Statens Museum for Kunst",
                "collection_qid":   SMK_WIKIDATA_QID,
                "inventory_number": inventory_number,
                "location_notes":   current_location,
                "department":       dept,
            },

            "provenance":        provenance_steps,
            "authority_links":   authority_links,
            "rights":            rights,
            "media":             media,

            "sources": [source_citation],
            "source_refs": [
                {"source_id": source_id, "role": "primary_record", "accessed": today}
            ],
            "conflicts":    [],
            "cataloguing": {
                "review_status":  "draft",
                "catalogued_by":  "SMKAdapter v0.1",
                "notes":          "Draft imported from SMK Open API. Requires human review before publication.",
                "tasks": [
                    "Reconcile creator to Wikidata / ULAN artist record",
                    "Verify title translation if publishing in English",
                    "Confirm provenance completeness against SMK catalogue",
                ],
            },

            "smk_raw": {
                "id":                   raw.get("id"),
                "object_number":        obj_num,
                "frontend_url":         raw.get("frontend_url"),
                "iiif_manifest":        raw.get("iiif_manifest"),
                "on_display":           raw.get("on_display"),
                "responsible_department": dept,
                "creator_lref":         (production[0].get("creator_lref") if production else None),
                "production_dates_notes": raw.get("production_dates_notes"),
            },
        }

        return record

    def extract_authority_links(self, raw: dict) -> list[dict]:
        """Return work-level authority links for an SMK record."""
        obj_num      = raw.get("object_number", "")
        frontend_url = raw.get("frontend_url") or f"{SMK_OPEN_BASE}/{obj_num}"
        api_url      = raw.get("object_url") or f"{SMK_API_BASE}/art/?object_number={obj_num}"

        return [
            {
                "scope":          SCOPE_ARTWORK,
                "system":         "SMK",
                "id":             obj_num,
                "uri":            frontend_url,
                "api_uri":        api_url,
                "status":         STATUS_APPROVED,
                "verified_date":  date.today().isoformat(),
                "notes":          "Work-level authority record: SMK Open collection entry",
            }
        ]

    def extract_rights(self, raw: dict) -> dict:
        """Read per-object rights. Never assumes CC0."""
        pd = raw.get("public_domain")
        license_uri = raw.get("rights")

        if pd is True:
            return {
                "public_domain":    True,
                "license":          license_uri or "https://creativecommons.org/publicdomain/mark/1.0/",
                "copyright_status": "public_domain",
                "attribution":      None,
                "source":           "SMK Open API public_domain field",
            }
        elif pd is False:
            return {
                "public_domain":    False,
                "license":          license_uri,
                "copyright_status": "in_copyright",
                "attribution":      f"Image: © Statens Museum for Kunst. See {raw.get('frontend_url', 'open.smk.dk')}",
                "source":           "SMK Open API public_domain field",
            }
        else:
            # Missing or ambiguous → treat as restricted (spec rule)
            return {
                "public_domain":    None,
                "license":          None,
                "copyright_status": "unknown",
                "attribution":      None,
                "source":           "SMK Open API — public_domain field absent; treated as restricted",
            }

    def extract_media(self, raw: dict) -> list[dict]:
        """Return media records, gated strictly on per-object public_domain flag."""
        pd = raw.get("public_domain")
        records = []

        # IIIF manifest — safe to reference regardless of rights (it's a pointer, not the image)
        manifest = raw.get("iiif_manifest")
        if manifest:
            records.append({
                "type":             "iiif_manifest",
                "uri":              manifest,
                "iiif_service":     None,
                "width":            None,
                "height":           None,
                "rights_verified":  True,
            })

        if pd is not True:
            # Not confirmed public domain → do not store image, only link
            return records

        # Public domain: store thumbnail and IIIF image service
        thumbnail = raw.get("image_thumbnail")
        if thumbnail:
            records.append({
                "type":             "image_thumbnail",
                "uri":              thumbnail,
                "iiif_service":     None,
                "width":            None,
                "height":           None,
                "rights_verified":  True,
            })

        iiif_id = raw.get("image_iiif_id")
        if iiif_id:
            records.append({
                "type":             "image_iiif",
                "uri":              iiif_id,
                "iiif_service":     iiif_id,
                "width":            raw.get("image_width"),
                "height":           raw.get("image_height"),
                "rights_verified":  True,
            })

        return records

    def extract_source_citation(self, raw: dict) -> dict:
        obj_num  = raw.get("object_number", "unknown")
        api_url  = raw.get("object_url") or f"{SMK_API_BASE}/art/?object_number={obj_num}"
        today    = date.today().isoformat()
        modified = raw.get("modified", "")[:10] if raw.get("modified") else None

        return {
            "source_id":        f"SRC-SMK-API-{obj_num}",
            "source_type":      "collection_api",
            "title":            f"SMK Open — {obj_num}",
            "publisher":        "Statens Museum for Kunst",
            "url":              api_url,
            "frontend_url":     raw.get("frontend_url"),
            "publication_date": modified,
            "access_date":      today,
            "license":          "https://creativecommons.org/licenses/by/4.0/",
            "use_notes":        "SMK Open data is CC BY 4.0. Image reuse governed by per-object public_domain flag.",
        }

    def produce_import_report(self, raw: dict) -> str:
        obj_num = raw.get("object_number", "?")
        lines   = [f"SMK Import Report — {obj_num}", "=" * 50]

        # Imported fields
        imported = []
        missing  = []
        needs_rec = []

        def chk(label, value):
            (imported if value else missing).append(label)

        chk("title",             raw.get("titles"))
        chk("object type",       raw.get("object_names"))
        chk("creator",           raw.get("production"))
        chk("production date",   raw.get("production_date"))
        chk("techniques",        raw.get("techniques"))
        chk("materials",         raw.get("materials"))
        chk("dimensions",        raw.get("dimensions"))
        chk("inventory number",  raw.get("object_number"))
        chk("acquisition date",  raw.get("acquisition_date"))
        chk("object history",    raw.get("object_history_note"))
        chk("image",             raw.get("has_image"))
        chk("rights / public domain", raw.get("public_domain") is not None)

        lines.append(f"\nImported ({len(imported)}):")
        for f in imported:
            lines.append(f"  ✓  {f}")

        lines.append(f"\nGaps — not in SMK record ({len(missing)}):")
        for f in missing:
            lines.append(f"  —  {f}")

        # Needs reconciliation
        production = raw.get("production") or []
        if production:
            for p in production:
                creator = p.get("creator", "?")
                needs_rec.append(f"Creator '{creator}' → reconcile to Wikidata / ULAN / RKD")

        pd = raw.get("public_domain")
        if pd is True:
            lines.append("\nRights: PUBLIC DOMAIN (CC0) — image may be stored and displayed")
        elif pd is False:
            lines.append("\nRights: IN COPYRIGHT — metadata stored, image linked (not redistributed)")
        else:
            lines.append("\nRights: UNKNOWN — treated as restricted; image not stored")

        if needs_rec:
            lines.append(f"\nNeeds reconciliation ({len(needs_rec)}):")
            for r in needs_rec:
                lines.append(f"  ⚠  {r}")

        lines.append(f"\nWork-level authority link: SMK '{obj_num}' → {raw.get('frontend_url')}")
        lines.append(f"Source citation: SRC-SMK-API-{obj_num}")
        return "\n".join(lines)

    # ── Wikidata reconciliation ───────────────────────────────────────────────

    def find_wikidata_item(self, object_number: str) -> Optional[str]:
        """Search Wikidata for an artwork with P217=object_number in P195=SMK.

        Returns the QID string if found, None otherwise.
        """
        sparql = f"""
SELECT ?item WHERE {{
  ?item wdt:P217 "{object_number}" .
  ?item wdt:P195 wd:{SMK_WIKIDATA_QID} .
}}
LIMIT 1
"""
        url = ("https://query.wikidata.org/sparql?format=json&query="
               + urllib.parse.quote(sparql.strip()))
        try:
            data = _get_json(url)
            bindings = data.get("results", {}).get("bindings", [])
            if bindings:
                entity_uri = bindings[0]["item"]["value"]
                return entity_uri.split("/")[-1]  # "Q12345"
        except Exception:
            pass
        return None

    def produce_wikidata_task(self, raw: dict, artwork_qid: Optional[str] = None) -> str:
        """Produce a reviewed QuickStatements task for SMK ↔ Wikidata reconciliation.

        If artwork_qid is known: adds P217 (SMK inventory number) if missing.
        If artwork_qid is None: generates a CREATE stub for human review.

        Output is paste-ready QS V1 format. Never auto-committed.
        """
        obj_num      = raw.get("object_number", "")
        frontend_url = raw.get("frontend_url") or f"{SMK_OPEN_BASE}/{obj_num}"
        today        = date.today().isoformat()
        ts           = f"+{today}T00:00:00Z/11"

        production   = raw.get("production") or []
        titles       = raw.get("titles") or []
        title_en     = None
        title_da     = None
        for t in titles:
            lang = t.get("language", "").lower()
            if lang in ("english", "en"):
                title_en = t["title"]
            elif lang in ("dansk", "da"):
                title_da = t["title"]
        title_da = title_da or (titles[0]["title"] if titles else None)

        prod_dates   = raw.get("production_date") or []
        date_str     = None
        if prod_dates:
            pd = prod_dates[0]
            start_year = _parse_year(pd.get("start"))
            if start_year:
                date_str = f"+{start_year}-00-00T00:00:00Z/9"

        lines = [
            f"#title SMK Wikidata task — {obj_num}",
            f"#summary Reviewed reconciliation task. Source: SMK Open API. Never auto-committed.",
            f"#prepared_by ArsAccordia SMKAdapter v0.1",
            f"#prepared_at {today}T00:00:00Z",
            f"# SMK Open record: {frontend_url}",
            "",
        ]

        if artwork_qid:
            # Item exists — add P217 if not already present
            lines += [
                f"# Artwork already on Wikidata as {artwork_qid}",
                f"# ACTION: verify P217 is present; add if missing",
                f"{artwork_qid}\tP217\t\"{obj_num}\"\tP195\tQ{SMK_WIKIDATA_QID[1:]}"
                f"\tS248\tQ{SMK_WIKIDATA_QID[1:]}\tS813\t{ts}",
                f"{artwork_qid}\tP973\t\"{frontend_url}\"\tS854\t\"{frontend_url}\"\tS813\t{ts}",
            ]
        else:
            # No Wikidata item — generate a CREATE stub for review
            lines += [
                "# No existing Wikidata item found for this SMK object.",
                "# Review the CREATE block below carefully before submission.",
                "# Confirm: no duplicate exists; labels are accurate; QIDs are correct.",
                "",
                "CREATE",
            ]
            if title_da:
                lines.append(f"LAST\tLda\t\"{title_da}\"")
            if title_en:
                lines.append(f"LAST\tLen\t\"{title_en}\"")
            if production:
                p = production[0]
                creator_name = p.get("creator", "")
                lines.append(f"# Creator: {creator_name} — find QID before submitting")
                lines.append(f"# LAST\tP170\t[ARTIST_QID]\tS248\tQ{SMK_WIKIDATA_QID[1:]}\tS217\t\"{obj_num}\"")
            if date_str:
                lines.append(f"LAST\tP571\t{date_str}\tS248\tQ{SMK_WIKIDATA_QID[1:]}")
            lines += [
                f"LAST\tP217\t\"{obj_num}\"\tP195\tQ{SMK_WIKIDATA_QID[1:]}"
                f"\tS248\tQ{SMK_WIKIDATA_QID[1:]}\tS813\t{ts}",
                f"LAST\tP195\tQ{SMK_WIKIDATA_QID[1:]}",
                f"LAST\tP973\t\"{frontend_url}\"\tS854\t\"{frontend_url}\"\tS813\t{ts}",
            ]

        return "\n".join(lines) + "\n"
