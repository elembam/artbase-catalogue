#!/usr/bin/env python3
"""
oai_generator.py — Generate static OAI-PMH 2.0 XML responses for Ars Accordia.

Produces pre-built responses for the three core verbs:
  oai/identify.xml         — Identify
  oai/list-identifiers.xml — ListIdentifiers (oai_dc)
  oai/list-records.xml     — ListRecords (oai_dc)
  oai/index.xml            — redirects to ListRecords (default entry)

A Cloudflare Pages _redirects file maps query-string URLs:
  /oai?verb=Identify         →  /oai/identify.xml
  /oai?verb=ListIdentifiers  →  /oai/list-identifiers.xml
  /oai?verb=ListRecords      →  /oai/list-records.xml

Usage:
    python3 scripts/oai_generator.py
"""

import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET
from xml.dom import minidom

# ── Paths ─────────────────────────────────────────────────────────────────────
ROOT          = Path(__file__).parent.parent
DATA_ARTWORKS = ROOT / "artbase_export" / "data" / "artworks"
OAI_DIR       = ROOT / "oai"

CATALOGUE_BASE = "https://arsaccordia.com"
REPO_NAME      = "Ars Accordia Catalogue"
ADMIN_EMAIL    = "catalogue@arsaccordia.com"
OAI_BASE_URL   = f"{CATALOGUE_BASE}/oai/list-records.xml"

# ── Namespaces ────────────────────────────────────────────────────────────────
OAI_NS  = "http://www.openarchives.org/OAI/2.0/"
DC_NS   = "http://purl.org/dc/elements/1.1/"
DCTERMS = "http://purl.org/dc/terms/"
XSI_NS  = "http://www.w3.org/2001/XMLSchema-instance"
OAI_DC_NS = "http://www.openarchives.org/OAI/2.0/oai_dc/"

ET.register_namespace("",        OAI_NS)
ET.register_namespace("dc",      DC_NS)
ET.register_namespace("dcterms", DCTERMS)
ET.register_namespace("xsi",     XSI_NS)
ET.register_namespace("oai_dc",  OAI_DC_NS)


def O(tag):  return f"{{{OAI_NS}}}{tag}"
def DC(tag): return f"{{{DC_NS}}}{tag}"


def prettify(root: ET.Element) -> str:
    raw = ET.tostring(root, encoding="unicode")
    dom = minidom.parseString(raw)
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + "\n".join(
        line for line in dom.toprettyxml(indent="  ").splitlines()[1:]
        if line.strip()
    )


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_artworks() -> list[dict]:
    """Load all AP-*.json artwork files, sorted by artbase_id."""
    artworks = []
    for path in sorted(DATA_ARTWORKS.glob("AP-*.json")):
        try:
            artworks.append(json.loads(path.read_text(encoding="utf-8")))
        except Exception as e:
            print(f"  ⚠ Skipping {path.name}: {e}", file=sys.stderr)
    return artworks


def oai_response_root(verb: str) -> ET.Element:
    """Create the standard OAI-PMH 2.0 root element."""
    root = ET.Element(O("OAI-PMH"), {
        f"{{{XSI_NS}}}schemaLocation": (
            "http://www.openarchives.org/OAI/2.0/ "
            "http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd"
        )
    })
    ET.SubElement(root, O("responseDate")).text = now_utc()
    req = ET.SubElement(root, O("request"), verb=verb)
    req.text = f"{CATALOGUE_BASE}/oai"
    return root


def build_dc_record(artwork: dict) -> ET.Element:
    """Build an oai_dc:dc Dublin Core metadata block."""
    oid      = artwork.get("object_id", {})
    location = artwork.get("location", {})
    iconog   = artwork.get("iconography", {})
    artbase_id = artwork.get("artbase_id", "")
    exported = artwork.get("exported", date.today().isoformat())[:10]

    dc = ET.Element(f"{{{OAI_DC_NS}}}dc", {
        f"{{{XSI_NS}}}schemaLocation": (
            "http://www.openarchives.org/OAI/2.0/oai_dc/ "
            "http://www.openarchives.org/OAI/2.0/oai_dc.xsd"
        )
    })

    def dcel(tag, text):
        if text:
            ET.SubElement(dc, DC(tag)).text = str(text)

    dcel("identifier", f"{CATALOGUE_BASE}/{artbase_id}")
    dcel("title", oid.get("title") or artbase_id)
    dcel("creator", oid.get("maker_display_name"))
    dcel("type", oid.get("object_type", "").capitalize() or "Visual Artwork")
    dcel("description", oid.get("subject"))
    dcel("date", oid.get("date_display"))
    dcel("format", oid.get("materials"))
    dcel("source", location.get("collection"))
    dcel("coverage", location.get("location_notes") or location.get("collection"))
    dcel("rights", "Public Domain / Ars Accordia Catalogue Record")
    dcel("language", "en")

    # ICONCLASS subjects as dc:subject
    for ic in iconog.get("iconclass_labels", []):
        ET.SubElement(dc, DC("subject")).text = f"ICONCLASS:{ic['code']} {ic['label']}"

    return dc


def datestamp(artwork: dict) -> str:
    exported = artwork.get("exported") or date.today().isoformat()
    return exported[:10]


# ── Identify ──────────────────────────────────────────────────────────────────

def build_identify(artworks: list[dict]) -> str:
    root = oai_response_root("Identify")
    id_el = ET.SubElement(root, O("Identify"))
    ET.SubElement(id_el, O("repositoryName")).text = REPO_NAME
    ET.SubElement(id_el, O("baseURL")).text = f"{CATALOGUE_BASE}/oai"
    ET.SubElement(id_el, O("protocolVersion")).text = "2.0"
    ET.SubElement(id_el, O("adminEmail")).text = ADMIN_EMAIL
    # Earliest datestamp from exported fields
    dates = [a.get("exported", "")[:10] for a in artworks if a.get("exported")]
    earliest = min(dates) if dates else date.today().isoformat()
    ET.SubElement(id_el, O("earliestDatestamp")).text = earliest
    ET.SubElement(id_el, O("deletedRecord")).text = "no"
    ET.SubElement(id_el, O("granularity")).text = "YYYY-MM-DD"
    return prettify(root)


# ── ListIdentifiers ───────────────────────────────────────────────────────────

def build_list_identifiers(artworks: list[dict]) -> str:
    root = oai_response_root("ListIdentifiers")
    li_el = ET.SubElement(root, O("ListIdentifiers"))
    for aw in artworks:
        header = ET.SubElement(li_el, O("header"))
        ET.SubElement(header, O("identifier")).text = f"{CATALOGUE_BASE}/{aw['artbase_id']}"
        ET.SubElement(header, O("datestamp")).text = datestamp(aw)
        ET.SubElement(header, O("setSpec")).text = "artworks"
    return prettify(root)


# ── ListRecords ───────────────────────────────────────────────────────────────

def build_list_records(artworks: list[dict]) -> str:
    root = oai_response_root("ListRecords")
    lr_el = ET.SubElement(root, O("ListRecords"))
    for aw in artworks:
        record = ET.SubElement(lr_el, O("record"))
        header = ET.SubElement(record, O("header"))
        ET.SubElement(header, O("identifier")).text = f"{CATALOGUE_BASE}/{aw['artbase_id']}"
        ET.SubElement(header, O("datestamp")).text = datestamp(aw)
        ET.SubElement(header, O("setSpec")).text = "artworks"
        metadata = ET.SubElement(record, O("metadata"))
        metadata.append(build_dc_record(aw))
    return prettify(root)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    OAI_DIR.mkdir(exist_ok=True)
    artworks = load_artworks()
    print(f"Loaded {len(artworks)} artwork(s)")

    files = {
        "identify.xml":         build_identify(artworks),
        "list-identifiers.xml": build_list_identifiers(artworks),
        "list-records.xml":     build_list_records(artworks),
    }
    for filename, xml_str in files.items():
        out = OAI_DIR / filename
        out.write_text(xml_str, encoding="utf-8")
        print(f"  ✓ oai/{filename}  ({len(xml_str):,} bytes)")

    # index.xml — synonym for ListRecords (default entry point)
    index = OAI_DIR / "index.xml"
    index.write_text(files["list-records.xml"], encoding="utf-8")
    print(f"  ✓ oai/index.xml  (copy of list-records)")

    # _redirects for Cloudflare Pages (query-string → static file)
    redirects = ROOT / "_redirects"
    redirect_lines = [
        "/oai?verb=Identify         /oai/identify.xml         200",
        "/oai?verb=ListIdentifiers  /oai/list-identifiers.xml 200",
        "/oai?verb=ListRecords      /oai/list-records.xml     200",
        "/oai                       /oai/list-records.xml     200",
    ]
    # Merge with existing _redirects if present
    existing_lines = []
    if redirects.exists():
        existing = redirects.read_text(encoding="utf-8").splitlines()
        existing_lines = [l for l in existing if "/oai" not in l and l.strip()]

    all_lines = existing_lines + ["", "# OAI-PMH verb routing"] + redirect_lines
    redirects.write_text("\n".join(all_lines) + "\n", encoding="utf-8")
    print(f"  ✓ _redirects  (OAI-PMH routes added)")

    print("\nDone.")


if __name__ == "__main__":
    main()
