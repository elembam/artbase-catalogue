#!/usr/bin/env python3
"""
lido_generator.py — Generate LIDO 1.1 and EODEM XML from canonical artwork JSON.

Outputs:
  api/{artbase_id}/lido.xml     — LIDO 1.1
  api/{artbase_id}/eodem.xml    — EODEM profile (LIDO 1.1 with EODEM namespace)

Usage:
    python3 scripts/lido_generator.py                  # all artworks
    python3 scripts/lido_generator.py AP-2026-000001   # specific artwork
    python3 scripts/lido_generator.py --dry-run        # print XML, don't write
"""

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from xml.etree import ElementTree as ET
from xml.dom import minidom

# ── Paths ─────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent
DATA_ARTWORKS = ROOT / "artbase_export" / "data" / "artworks"
DATA_ARTISTS  = ROOT / "artbase_export" / "data" / "artists"
API_DIR       = ROOT / "api"

CATALOGUE_BASE = "https://arsaccordia.com"

# ── LIDO XML namespaces ───────────────────────────────────────────────────────
LIDO_NS    = "http://www.lido-schema.org"
LIDO_XSD   = "http://www.lido-schema.org http://www.lido-schema.org/schema/export/lido-v1.1.xsd"
XSI_NS     = "http://www.w3.org/2001/XMLSchema-instance"
EODEM_NS   = "http://www.eodem.eu/schema/eodem-v1"

ET.register_namespace("lido", LIDO_NS)
ET.register_namespace("xsi",  XSI_NS)
ET.register_namespace("eodem", EODEM_NS)


# ── Helpers ───────────────────────────────────────────────────────────────────

def L(tag: str) -> str:
    """Qualify a tag name with the LIDO namespace."""
    return f"{{{LIDO_NS}}}{tag}"


def sub(parent: ET.Element, tag: str, text: str = None, **attrs) -> ET.Element:
    """Create a LIDO-namespaced child element, optionally with text and lido: attrs."""
    el = ET.SubElement(parent, L(tag))
    qualified = {f"{{{LIDO_NS}}}{k}": v for k, v in attrs.items()}
    el.attrib.update(qualified)
    if text is not None:
        el.text = str(text)
    return el


def appellation(parent: ET.Element, wrap_tag: str, set_tag: str, value: str, lang: str = "en"):
    """Create an appellationValue inside a standardised wrap/set hierarchy."""
    wrap = ET.SubElement(parent, L(wrap_tag))
    s    = ET.SubElement(wrap, L(set_tag))
    av   = sub(s, "appellationValue", value, lang=lang)
    return wrap


def prettify(tree: ET.ElementTree) -> str:
    """Return indented, human-readable XML string."""
    raw = ET.tostring(tree.getroot(), encoding="unicode", xml_declaration=False)
    dom = minidom.parseString(raw)
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + "\n".join(
        line for line in dom.toprettyxml(indent="  ").splitlines()[1:]  # skip minidom's declaration
        if line.strip()
    )


# ── LIDO record builder ───────────────────────────────────────────────────────

def build_lido_record(artwork: dict, artist: dict | None, eodem: bool = False) -> ET.Element:
    artbase_id  = artwork.get("artbase_id", "")
    canonical_id = artwork.get("artbase_canonical_id") or artbase_id
    oid         = artwork.get("object_id", {})
    location    = artwork.get("location", {})
    iconography = artwork.get("iconography", {})
    provenance  = artwork.get("provenance", [])
    exported    = artwork.get("exported", date.today().isoformat())[:10]

    # Root <lido:lido>
    lido_el = ET.Element(L("lido"), {
        f"{{{XSI_NS}}}schemaLocation": LIDO_XSD,
    })
    if eodem:
        lido_el.set(f"{{{EODEM_NS}}}profile", "EODEM-v1")

    # ── lidoRecID ─────────────────────────────────────────────────────────────
    rec_id = sub(lido_el, "lidoRecID",
                 f"{CATALOGUE_BASE}/{artbase_id}",
                 type="URI", source="ArsAccordia")

    # ── category ─────────────────────────────────────────────────────────────
    cat = sub(lido_el, "category")
    sub(cat, "conceptID",
        "http://terminology.lido-schema.org/lido00223",
        type="URI", source="LIDO Terminology")
    sub(cat, "term", "Man-Made Object")

    # ════════════════════════════════════════════════════════════════════════
    # DESCRIPTIVE METADATA
    # ════════════════════════════════════════════════════════════════════════
    desc = sub(lido_el, "descriptiveMetadata", lang="en")

    # ── objectClassificationWrap ─────────────────────────────────────────────
    cls_wrap = sub(desc, "objectClassificationWrap")
    owt_wrap = sub(cls_wrap, "objectWorkTypeWrap")
    owt      = sub(owt_wrap, "objectWorkType")
    aat_type = (oid.get("object_type_aat") or {})
    if aat_type.get("uri"):
        sub(owt, "conceptID", aat_type["uri"], type="URI", source="AAT")
    sub(owt, "term", oid.get("object_type", "").capitalize() or "Unknown")

    # ── objectIdentificationWrap ─────────────────────────────────────────────
    id_wrap = sub(desc, "objectIdentificationWrap")

    # titleWrap
    title_wrap = sub(id_wrap, "titleWrap")
    title_set  = sub(title_wrap, "titleSet")
    sub(title_set, "appellationValue", oid.get("title") or artbase_id, lang="en")

    # repositoryWrap
    if location.get("collection"):
        repo_wrap = sub(id_wrap, "repositoryWrap")
        repo_set  = sub(repo_wrap, "repositorySet", type="current location")
        repo_name = sub(repo_set, "repositoryName")
        lbn       = sub(repo_name, "legalBodyName")
        sub(lbn,  "appellationValue", location["collection"])
        if location.get("collection_qid"):
            sub(repo_name, "legalBodyID",
                f"https://www.wikidata.org/wiki/{location['collection_qid']}",
                type="URI", source="Wikidata")
        if location.get("inventory_number"):
            sub(repo_set, "workID", location["inventory_number"], type="inventory number")
        if location.get("location_notes"):
            sub(repo_set, "repositoryLocation")  # placeholder for TGN if available

    # objectDescriptionWrap
    if oid.get("subject"):
        desc_wrap = sub(id_wrap, "objectDescriptionWrap")
        desc_set  = sub(desc_wrap, "objectDescriptionSet")
        sub(desc_set, "descriptiveNoteValue", oid["subject"], lang="en")

    # inscriptionsWrap
    if oid.get("inscriptions") and oid["inscriptions"].lower() not in ("none", "none visible", "n/a"):
        insc_wrap = sub(id_wrap, "inscriptionsWrap")
        insc_set  = sub(insc_wrap, "inscriptions")
        sub(insc_set, "inscriptionDescription")  # placeholder — full value in notes

    # objectMeasurementsWrap
    if oid.get("dimensions_display") or oid.get("height_cm"):
        meas_wrap = sub(id_wrap, "objectMeasurementsWrap")
        meas_set  = sub(meas_wrap, "objectMeasurementsSet")
        if oid.get("dimensions_display"):
            sub(meas_set, "displayObjectMeasurements", oid["dimensions_display"])
        obj_meas  = sub(meas_set, "objectMeasurements")
        meas_type = sub(obj_meas, "measurementsSet")
        if oid.get("height_cm"):
            sub(meas_type, "measurementValue",
                str(oid["height_cm"]), type="height", unit="cm")
        if oid.get("width_cm"):
            sub(meas_type, "measurementValue",
                str(oid["width_cm"]), type="width", unit="cm")

    # ── eventWrap — creation ─────────────────────────────────────────────────
    ev_wrap = sub(desc, "eventWrap")
    ev_set  = sub(ev_wrap, "eventSet")
    event   = sub(ev_set, "event")

    # eventType: creation
    ev_type = sub(event, "eventType")
    sub(ev_type, "conceptID",
        "http://vocab.getty.edu/aat/300054686", type="URI", source="AAT")
    sub(ev_type, "term", "creation")

    # eventActor (artist)
    if artist:
        ev_actor  = sub(event, "eventActor")
        act_role  = sub(ev_actor, "actorInRole")
        actor     = sub(act_role, "actor")
        auth      = artist.get("authority_links", {})
        # Actor IDs
        for source, id_key in [("ULAN", "ulan"), ("Wikidata", "wikidata"), ("VIAF", "viaf")]:
            link = auth.get(id_key, {})
            uid  = link.get("uri") or link.get("id")
            if uid:
                uri = uid if uid.startswith("http") else {
                    "Wikidata": f"https://www.wikidata.org/wiki/{uid}",
                    "VIAF":     f"https://viaf.org/viaf/{uid}",
                }.get(source, uid)
                sub(actor, "actorID", uri, type="URI", source=source)
        name_set = sub(actor, "nameActorSet")
        sub(name_set, "appellationValue",
            artist.get("identity", {}).get("preferred_name", "Unknown"), lang="en")
        # ArtBase canonical actor ID
        actor_cid = artist.get("artbase_canonical_id")
        if actor_cid:
            sub(actor, "actorID",
                f"{CATALOGUE_BASE}/artists/{artist['artbase_id']}",
                type="URI", source="ArsAccordia")
        # Role
        role_el = sub(act_role, "roleActor")
        sub(role_el, "term", "artist")

    # eventDate
    ev_date = sub(event, "eventDate")
    if oid.get("date_display"):
        sub(ev_date, "displayDate", oid["date_display"])
    if oid.get("date_earliest"):
        date_el = sub(ev_date, "date")
        sub(date_el, "earliestDate", str(oid["date_earliest"]))
        if oid.get("date_latest"):
            sub(date_el, "latestDate", str(oid["date_latest"]))

    # ── objectRelationWrap — ICONCLASS subjects ───────────────────────────────
    if iconography.get("iconclass_labels"):
        rel_wrap  = sub(desc, "objectRelationWrap")
        subj_wrap = sub(rel_wrap, "subjectWrap")
        for ic in iconography["iconclass_labels"]:
            subj_set  = sub(subj_wrap, "subjectSet")
            subj      = sub(subj_set, "subject", type="iconography")
            subj_conc = sub(subj, "subjectConcept")
            sub(subj_conc, "conceptID", ic.get("uri", ""), type="URI", source="ICONCLASS")
            sub(subj_conc, "term", ic.get("label", ""), lang="en")

    # ════════════════════════════════════════════════════════════════════════
    # ADMINISTRATIVE METADATA
    # ════════════════════════════════════════════════════════════════════════
    admin = sub(lido_el, "administrativeMetadata", lang="en")

    # ── rightsWorkWrap ────────────────────────────────────────────────────────
    rights_wrap = sub(admin, "rightsWorkWrap")
    rights_set  = sub(rights_wrap, "rightsWorkSet")
    rights_type = sub(rights_set, "rightsType")
    sub(rights_type, "conceptID",
        "http://creativecommons.org/publicdomain/zero/1.0/", type="URI", source="Creative Commons")
    sub(rights_type, "term", "Public Domain")

    # ── recordWrap ────────────────────────────────────────────────────────────
    rec_wrap  = sub(admin, "recordWrap")
    sub(rec_wrap, "recordID", artbase_id, type="local")
    if canonical_id != artbase_id:
        sub(rec_wrap, "recordID", canonical_id, type="global", source="ArsAccordia")
    rec_type  = sub(rec_wrap, "recordType")
    sub(rec_type, "term", "item")
    rec_src   = sub(rec_wrap, "recordSource")
    lbn2      = sub(rec_src, "legalBodyName")
    sub(lbn2, "appellationValue", "Ars Accordia")
    sub(rec_src, "legalBodyWeblink", CATALOGUE_BASE)
    sub(rec_wrap, "recordInfoLink", f"{CATALOGUE_BASE}/{artbase_id}.html")
    sub(rec_wrap, "recordMetadataDate", exported)

    # ── provenance as acquisitionFrom events (optional, EODEM-relevant) ───────
    if eodem and provenance:
        prov_wrap = sub(admin, "provenanceNotes")  # non-standard convenience element
        # EODEM allows provenance notes in administrativeMetadata
        for ev in provenance:
            pnote = sub(prov_wrap, "provenanceEvent")
            if ev.get("date_display"):
                sub(pnote, "date", ev["date_display"])
            if ev.get("owner") or ev.get("actor"):
                sub(pnote, "actor", ev.get("owner") or ev.get("actor"))
            if ev.get("detail") or ev.get("notes"):
                sub(pnote, "note", ev.get("detail") or ev.get("notes"))
            if ev.get("source"):
                sub(pnote, "source", ev["source"])

    return lido_el


# ── File writer ───────────────────────────────────────────────────────────────

def generate_for_artwork(artbase_id: str, dry_run: bool = False):
    artwork_path = DATA_ARTWORKS / f"{artbase_id}.json"
    if not artwork_path.exists():
        print(f"  ✗ Not found: {artwork_path}", file=sys.stderr)
        return

    artwork = json.loads(artwork_path.read_text(encoding="utf-8"))
    maker_id = artwork.get("object_id", {}).get("maker_id")
    artist = None
    if maker_id:
        artist_path = DATA_ARTISTS / f"{maker_id}.json"
        if artist_path.exists():
            artist = json.loads(artist_path.read_text(encoding="utf-8"))

    out_dir = API_DIR / artbase_id
    if not dry_run:
        out_dir.mkdir(parents=True, exist_ok=True)

    for is_eodem, suffix in [(False, "lido.xml"), (True, "eodem.xml")]:
        lido_el = build_lido_record(artwork, artist, eodem=is_eodem)
        tree = ET.ElementTree(lido_el)
        xml_str = prettify(tree)
        if dry_run:
            print(f"\n{'─'*60}")
            print(f"  {artbase_id}/{suffix}")
            print('─'*60)
            print(xml_str[:2000] + ("…" if len(xml_str) > 2000 else ""))
        else:
            out_path = out_dir / suffix
            out_path.write_text(xml_str, encoding="utf-8")
            print(f"  ✓ {out_path.relative_to(ROOT)}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Generate LIDO 1.1 and EODEM XML from canonical JSON")
    parser.add_argument("artbase_ids", nargs="*", help="Artwork IDs to process (default: all)")
    parser.add_argument("--dry-run", action="store_true", help="Print XML without writing files")
    args = parser.parse_args()

    if args.artbase_ids:
        ids = args.artbase_ids
    else:
        ids = [p.stem for p in sorted(DATA_ARTWORKS.glob("AP-*.json"))]

    print(f"Generating LIDO + EODEM XML for {len(ids)} artwork(s)...")
    for artbase_id in ids:
        print(f"\n{artbase_id}")
        generate_for_artwork(artbase_id, dry_run=args.dry_run)

    print("\nDone.")


if __name__ == "__main__":
    main()
