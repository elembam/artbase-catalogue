#!/usr/bin/env python3
"""
build_source_ledger.py — Generate / verify the source ledger for artist records.

The source ledger is a DERIVED VIEW computed from attestations[] and
authority_links.*. It is never a second source of truth. If the ledger and
the attestations ever disagree, the attestations win and the ledger is rebuilt.

Structure written to artist["source_ledger"]:
  origin[]       — data_origin attestations (commercial_gallery etc, citable: false)
  authority[]    — citable attestations + authority_links (Wikidata, ULAN, VIAF…)
  provenance[]   — provenance-role attestations (currently mainly artworks)
  verification   — { status, basis, confirmed_by[] }
  field_provenance — per-field { value, sources[], has_citable_source, discrepancy }
  generated_at

CLI:
    python3 scripts/build_source_ledger.py              # build ledger for all artists
    python3 scripts/build_source_ledger.py --record ART-AIDE-1913
    python3 scripts/build_source_ledger.py --print ART-AIDE-1913   # human-readable stdout
    python3 scripts/build_source_ledger.py --check      # verify ledgers match attestations; exit 1 on drift
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any, Optional

# ── Paths ──────────────────────────────────────────────────────────────────────
REPO_ROOT   = Path(__file__).resolve().parent.parent
DATA_DIR    = REPO_ROOT / "artbase_export" / "data"
ARTISTS_DIR = DATA_DIR / "artists"
SOURCES_DIR = DATA_DIR / "sources"

# Authority links that are citable (all external authority files are citable)
AUTHORITY_LINK_NAMES = {
    "wikidata": "Wikidata",
    "viaf":     "VIAF",
    "ulan":     "Getty ULAN",
    "lndb":     "Latvian National Bibliography",
    "isni":     "ISNI",
    "rkd":      "RKDartists",
    "lc_naco":  "LC Name Authority",
    "gnd":      "GND (Deutsche Nationalbibliothek)",
    "bnf":      "Bibliothèque nationale de France",
    "libris":   "LIBRIS (Sweden)",
}

AUTHORITY_LINK_URIS = {
    "wikidata": "https://www.wikidata.org/wiki/{id}",
    "viaf":     "https://viaf.org/viaf/{id}/",
    "ulan":     "http://vocab.getty.edu/page/ulan/{id}",
    "lndb":     "https://lndb.lv/persona/{id}",
}


# ── Source registry ─────────────────────────────────────────────────────────────

def load_source_registry() -> dict[str, dict]:
    """Load all source definitions from data/sources/*.json."""
    registry: dict[str, dict] = {}
    if SOURCES_DIR.exists():
        for path in SOURCES_DIR.glob("*.json"):
            try:
                s = json.loads(path.read_text(encoding="utf-8"))
                registry[s["source_id"]] = s
            except (KeyError, json.JSONDecodeError):
                pass
    return registry


# ── Ledger builder ──────────────────────────────────────────────────────────────

def build_ledger(artist: dict, source_registry: dict[str, dict]) -> dict:
    """
    Compute the source ledger from an artist's attestations + authority_links.
    Pure function — reads only, returns the ledger dict.
    """
    today        = date.today().isoformat()
    attestations = artist.get("attestations", [])
    auth_links   = artist.get("authority_links", {})

    origin:     list[dict] = []
    authority:  list[dict] = []
    provenance: list[dict] = []

    # ── Attestations ─────────────────────────────────────────────────────────
    for att in attestations:
        sid  = att.get("source_id", "")
        role = att.get("role", "attestation")
        src  = source_registry.get(sid, {})

        # Resolve trust: source-document override if set, else contributor default.
        # Override values: "inherit" / "true" / "false"
        citable_raw = src.get("wikidata_citable_override", "inherit")
        if citable_raw == "true":
            citable = True
        elif citable_raw == "false":
            citable = False
        else:
            citable = src.get("wikidata_citable", True)   # unknown sources → assume citable

        can_confirm_raw = src.get("can_confirm_override", "inherit")
        if can_confirm_raw == "true":
            can_confirm = True
        elif can_confirm_raw == "false":
            can_confirm = False
        else:
            can_confirm = src.get("can_confirm", True)

        stype = src.get("source_type", "unknown")
        name  = src.get("name", sid)

        entry = {
            "source_id":  sid,
            "name":       name,
            "type":       stype,
            "citable":    citable,
            "url":        att.get("url"),
            "role":       role,
        }

        if role == "data_origin":
            origin.append(entry)
        elif role in ("owner_asserted", "user_submission"):
            # owner_asserted and user_submission go into origin (non-authoritative claims)
            # They are NEVER citable regardless of source trust settings.
            entry["citable"]    = False
            entry["can_confirm"] = False
            origin.append(entry)
        elif role.startswith("provenance"):
            provenance.append(entry)
        else:
            # attestation role — citable authority
            backed = list(att.get("asserts", {}).keys()) if att.get("asserts") else []
            entry["backs"] = backed
            if att.get("page"):
                entry["page"] = att["page"]
            if att.get("wikidata_qid"):
                entry["wikidata_qid"] = att["wikidata_qid"]
            authority.append(entry)

    # ── Authority links ───────────────────────────────────────────────────────
    for key, info in auth_links.items():
        if key == "artbase_id":
            continue
        if not isinstance(info, dict):
            continue
        aid = info.get("id")
        if not aid or info.get("status") not in ("confirmed",):
            continue

        uri_tpl = AUTHORITY_LINK_URIS.get(key)
        uri     = uri_tpl.format(id=aid) if uri_tpl else info.get("uri")

        authority.append({
            "source_id":  f"AUTH-{key.upper()}",
            "name":       AUTHORITY_LINK_NAMES.get(key, key.upper()),
            "type":       "authority_file",
            "citable":    True,
            "url":        uri,
            "id":         aid,
            "role":       "authority_link",
        })

    # ── Verification summary (LEGACY — kept for audit/migration) ─────────────────
    citable_sources = [s for s in authority if s.get("citable")]
    confirmed_by    = [s.get("source_id", s.get("name", "")) for s in citable_sources]

    # Determine basis
    if citable_sources:
        basis  = "authority"
        status = "confirmed"
    elif origin:
        # owner_asserted alone does not elevate to candidate — only data_origin does
        has_data_origin = any(e.get("role") == "data_origin" for e in origin)
        basis  = "origin_only"
        status = "candidate" if has_data_origin else "unverified"
    else:
        basis  = "none"
        status = "unverified"

    # Part G: staff confirmation must cite a basis.
    # If an existing record is marked 'confirmed' by staff but has no citable authority
    # sources in the ledger, demote it and flag it.
    existing_status = artist.get("verification_status")
    if existing_status == "confirmed" and not citable_sources:
        # Staff confirmation without any citable authority behind it is invalid.
        status = "confirmed_no_basis"   # surfaced as a flag; will appear in --check output
        basis  = "staff_only_no_authority_cited"

    verification = {
        "status":       status,
        "basis":        basis,
        "confirmed_by": confirmed_by,
    }

    # ── Field-level provenance ────────────────────────────────────────────────
    field_provenance = _build_field_provenance(artist, attestations, source_registry, auth_links)

    # ── Validation block (Instruction 10 — four-grade GLEIF-style model) ─────
    validation = _build_validation(
        artist=artist,
        field_provenance=field_provenance,
        citable_sources=citable_sources,
        origin=origin,
        authority=authority,
        provenance_list=provenance,
    )

    result = {
        "generated_at": today,
        "origin":       origin,
        "authority":    authority,
        "provenance":   provenance,
        "verification": verification,
        "validation":   validation,
        "field_provenance": field_provenance,
    }

    # Preserve legacy_status if already written by migrate_validation.py
    legacy = artist.get("source_ledger", {}).get("legacy_status")
    if legacy is not None:
        result["legacy_status"] = legacy

    return result



# ── Instruction 10: four-grade validation model ────────────────────────────────
# Level 1 key fields for artists. If a field is absent from field_provenance,
# it is not counted either for or against — only present fields are evaluated.
_ARTIST_L1_FIELDS = ("birth_year", "death_year", "nationality", "name")

def _compute_validation_level(
    field_provenance: dict,
    key_fields: tuple[str, ...],
    citable_sources: list[dict],
    has_any_origin: bool,
    publication_pending: bool,
) -> tuple[str, list[str]]:
    """
    Compute (ValidationLevel, authority_source_ids) for one level.

    Rules (Part D of spec-10):
    - PENDING if publication_status is pending_review
    - ENTITY_SUPPLIED_ONLY if no citable sources back any key field
    - PARTIALLY_CORROBORATED if some key fields have citable sources
    - FULLY_CORROBORATED if ALL present key fields have citable sources AND no discrepancy
    Integrity rule (Part B): PARTIALLY / FULLY require non-empty citable_sources list.
    """
    if publication_pending:
        return "PENDING", []

    # Collect which key fields have citable backing
    present_fields = [f for f in key_fields if f in field_provenance]
    if not present_fields:
        # Nothing to evaluate — treat as PENDING for now
        return "PENDING", []

    citable_ids = [s["source_id"] for s in citable_sources if s.get("source_id")]

    corroborated   = [f for f in present_fields if field_provenance[f].get("has_citable_source")]
    uncorroborated = [f for f in present_fields if not field_provenance[f].get("has_citable_source")]
    has_discrepancy = any(field_provenance[f].get("discrepancy") for f in present_fields)

    if not corroborated:
        return "ENTITY_SUPPLIED_ONLY", []

    # Integrity rule: if we'd assign PARTIALLY/FULLY, citable_sources must be non-empty
    if not citable_ids:
        return "ENTITY_SUPPLIED_ONLY", []

    if uncorroborated or has_discrepancy:
        return "PARTIALLY_CORROBORATED", list(dict.fromkeys(citable_ids))

    return "FULLY_CORROBORATED", list(dict.fromkeys(citable_ids))


def _conformance_badge(level1: str, validated_by: str) -> str:
    """Derive the public-facing conformance badge from Level 1 grade and who validated."""
    if level1 == "FULLY_CORROBORATED":
        # Green only when a human validated; amber if automated pipeline only
        return "green" if (validated_by and validated_by not in ("automated", "migrated")) else "amber"
    if level1 == "PARTIALLY_CORROBORATED":
        return "amber"
    if level1 == "ENTITY_SUPPLIED_ONLY":
        return "grey"
    return "none"  # PENDING


def _build_validation(
    artist: dict,
    field_provenance: dict,
    citable_sources: list[dict],
    origin: list[dict],
    authority: list[dict],
    provenance_list: list[dict],
) -> dict:
    """
    Build the `validation` block for a canonical artist record.

    Returns a dict with `level1` and `level2` sub-objects.
    """
    today = str(date.today())
    pub_status = artist.get("publication_status", "")
    publication_pending = pub_status == "pending_review"

    # ── Level 1: identity fields ───────────────────────────────────────────────
    l1_level, l1_authority = _compute_validation_level(
        field_provenance=field_provenance,
        key_fields=_ARTIST_L1_FIELDS,
        citable_sources=citable_sources,
        has_any_origin=bool(origin),
        publication_pending=publication_pending,
    )
    # validated_by: if we already have a human-validated flag in existing source_ledger,
    # preserve it; otherwise "automated" (script-derived)
    prev_validation = artist.get("source_ledger", {}).get("validation", {})
    prev_l1 = prev_validation.get("level1", {})
    validated_by_l1 = prev_l1.get("validated_by", "automated")
    validated_at_l1 = prev_l1.get("validated_at") or (today if l1_level != "PENDING" else None)

    # ── Level 2: relationships / provenance attestations ──────────────────────
    # Level 2 is corroborated if any provenance-role attestation comes from a citable source.
    has_citable_provenance = any(
        e.get("citable") or any(
            a.get("citable") for a in authority
            if a.get("role") == "provenance"
        )
        for e in provenance_list
    )
    # Simpler: check provenance_list entries for citable flag
    citable_prov = [e for e in provenance_list if e.get("citable")]

    # Level 2 logic: PENDING | ENTITY_SUPPLIED_ONLY | PARTIALLY_CORROBORATED | FULLY_CORROBORATED
    if publication_pending:
        l2_level = "PENDING"
        l2_authority = []
    elif not provenance_list:
        # No provenance data at all — not applicable for now, use PENDING
        l2_level = "PENDING"
        l2_authority = []
    elif citable_prov:
        l2_level = "FULLY_CORROBORATED"
        l2_authority = [e.get("source_id", "") for e in citable_prov if e.get("source_id")]
    elif origin:
        # Has provenance data but only from non-citable origin
        l2_level = "ENTITY_SUPPLIED_ONLY"
        l2_authority = []
    else:
        l2_level = "ENTITY_SUPPLIED_ONLY"
        l2_authority = []

    prev_l2 = prev_validation.get("level2", {})
    validated_by_l2 = prev_l2.get("validated_by", "automated")
    validated_at_l2 = prev_l2.get("validated_at") or (today if l2_level != "PENDING" else None)

    conformance = _conformance_badge(l1_level, validated_by_l1)

    return {
        "level1": {
            "level":        l1_level,
            "authority":    l1_authority,
            "validated_by": validated_by_l1,
            "validated_at": validated_at_l1,
        },
        "level2": {
            "level":        l2_level,
            "authority":    l2_authority,
            "validated_by": validated_by_l2,
            "validated_at": validated_at_l2,
        },
        "conformance_badge": conformance,
    }


def _build_field_provenance(
    artist: dict,
    attestations: list[dict],
    source_registry: dict[str, dict],
    auth_links: dict,
) -> dict:
    """Build per-field provenance mapping."""
    fp: dict[str, dict] = {}

    def _get_year(date_block) -> Optional[int]:
        if not isinstance(date_block, dict):
            return None
        val = date_block.get("value", "")
        try:
            return int(str(val)[:4]) if val else None
        except (ValueError, TypeError):
            return None

    life = artist.get("life", {})

    # Collect all gallery asserts keyed by field
    gallery_asserts: dict[str, list[str]] = {}
    citable_asserts: dict[str, list[str]] = {}

    for att in attestations:
        sid   = att.get("source_id", "")
        src   = source_registry.get(sid, {})
        citable = src.get("wikidata_citable", True)
        for field, _ in att.get("asserts", {}).items():
            bucket = citable_asserts if citable else gallery_asserts
            bucket.setdefault(field, []).append(sid)

    # birth_year
    birth_year = _get_year(life.get("birth_date", {}))
    if birth_year is not None:
        sources_for_birth = (
            gallery_asserts.get("birth_year", []) +
            citable_asserts.get("birth_year", [])
        )
        # Any confirmed authority link (Wikidata, ULAN, VIAF, etc.) authoritatively
        # records birth/death dates and counts as a citable source for those fields.
        confirmed_auths = [
            k for k, v in auth_links.items()
            if k != "artbase_id" and isinstance(v, dict) and v.get("status") == "confirmed" and v.get("id")
        ]
        for auth_key in confirmed_auths:
            sources_for_birth.append(f"AUTH-{auth_key.upper()}")

        has_citable = bool(
            citable_asserts.get("birth_year") or confirmed_auths
        )

        gallery_val = None
        for att in attestations:
            if att.get("source_id") == "SRC-GALERIJA-JEKABS":
                gallery_val = att.get("asserts", {}).get("birth_year")
        discrepancy = (gallery_val is not None and gallery_val != birth_year)

        fp["birth_year"] = {
            "value":             birth_year,
            "sources":           list(dict.fromkeys(sources_for_birth)),
            "has_citable_source": has_citable,
            "discrepancy":       discrepancy,
        }

    # death_year
    death_year = _get_year(life.get("death_date", {}))
    if death_year is not None:
        sources_for_death = (
            gallery_asserts.get("death_year", []) +
            citable_asserts.get("death_year", [])
        )
        confirmed_auths = [
            k for k, v in auth_links.items()
            if k != "artbase_id" and isinstance(v, dict) and v.get("status") == "confirmed" and v.get("id")
        ]
        for auth_key in confirmed_auths:
            sources_for_death.append(f"AUTH-{auth_key.upper()}")

        has_citable = bool(
            citable_asserts.get("death_year") or confirmed_auths
        )

        gallery_val = None
        for att in attestations:
            if att.get("source_id") == "SRC-GALERIJA-JEKABS":
                gallery_val = att.get("asserts", {}).get("death_year")
        discrepancy = (gallery_val is not None and gallery_val != death_year)

        fp["death_year"] = {
            "value":             death_year,
            "sources":           list(dict.fromkeys(sources_for_death)),
            "has_citable_source": has_citable,
            "discrepancy":       discrepancy,
        }

    return fp


# ── Human-readable rendering ────────────────────────────────────────────────────

def render_ledger(artbase_id: str, ledger: dict) -> str:
    lines = [f"{artbase_id} — source ledger"]

    # Origin
    if ledger["origin"]:
        names = ", ".join(e["name"] for e in ledger["origin"])
        lines.append(f"  Origin (internal):    {names:<40} [not citable]")
    else:
        lines.append(f"  Origin (internal):    —")

    # Authority
    if ledger["authority"]:
        auth_names = []
        for e in ledger["authority"]:
            label = e["name"]
            if e.get("page"):
                label += f", p.{e['page']}"
            auth_names.append(label)
        auth_str = "  ·  ".join(auth_names)
        lines.append(f"  Authority (citable):  {auth_str}")
    else:
        lines.append(f"  Authority (citable):  —")

    # Provenance
    if ledger["provenance"]:
        prov = ", ".join(e["name"] for e in ledger["provenance"])
    else:
        prov = "—"
    lines.append(f"  Provenance:           {prov}")

    # Verification
    v     = ledger["verification"]
    basis = v.get("basis", "?")
    conf  = ", ".join(v.get("confirmed_by", [])) or "—"
    if basis == "authority":
        lines.append(f"  Verification:         {v['status']}  (basis: authority — {conf})")
    elif basis == "origin_only":
        lines.append(f"  Verification:         {v['status']}  (basis: origin only — needs citable authority)")
    else:
        lines.append(f"  Verification:         {v['status']}  (no sources)")

    # Field provenance — only show gallery-only fields
    fp = ledger.get("field_provenance", {})
    gallery_only = [(f, d) for f, d in fp.items() if not d.get("has_citable_source")]
    if gallery_only:
        lines.append(f"  Gallery-only fields:")
        for field, d in gallery_only:
            disc = " ⚠ DISCREPANCY" if d.get("discrepancy") else ""
            lines.append(f"    {field}: {d['value']}  (sources: {', '.join(d['sources'])}){disc}")

    return "\n".join(lines)


# ── Drift check ─────────────────────────────────────────────────────────────────

def ledger_matches_attestations(stored: dict, recomputed: dict) -> bool:
    """
    Compare stored ledger to freshly recomputed one.
    Ignores generated_at timestamp.
    """
    def _strip(d: dict) -> dict:
        d = dict(d)
        d.pop("generated_at", None)
        return d

    return _strip(stored) == _strip(recomputed)


# ── Main ─────────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build or verify source ledgers for Ars Accordia artist records"
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--record",  metavar="ART-ID", help="Build ledger for one record")
    group.add_argument("--print",   metavar="ART-ID", dest="print_record",
                       help="Print human-readable ledger for one record to stdout")
    group.add_argument("--check",   action="store_true",
                       help="Verify stored ledgers match attestations; exit 1 on drift")
    args = parser.parse_args()

    source_registry = load_source_registry()

    if args.print_record:
        path = ARTISTS_DIR / f"{args.print_record}.json"
        if not path.exists():
            print(f"✗ Not found: {args.print_record}")
            sys.exit(1)
        artist = json.loads(path.read_text(encoding="utf-8"))
        ledger = build_ledger(artist, source_registry)
        print(render_ledger(args.print_record, ledger))
        return

    if args.record:
        paths = [ARTISTS_DIR / f"{args.record}.json"]
        if not paths[0].exists():
            print(f"✗ Not found: {args.record}")
            sys.exit(1)
    else:
        paths = sorted(ARTISTS_DIR.glob("ART-*.json"))

    drift_count = 0
    build_count = 0

    for path in paths:
        artist = json.loads(path.read_text(encoding="utf-8"))
        artbase_id = artist.get("artbase_id", path.stem)
        fresh_ledger = build_ledger(artist, source_registry)

        if args.check:
            stored = artist.get("source_ledger")
            if stored is None:
                print(f"  ⚠ {artbase_id}: no stored ledger")
                drift_count += 1
            elif not ledger_matches_attestations(stored, fresh_ledger):
                print(f"  ✗ {artbase_id}: ledger DRIFT detected")
                drift_count += 1
        else:
            artist["source_ledger"] = fresh_ledger
            path.write_text(json.dumps(artist, ensure_ascii=False, indent=2), encoding="utf-8")
            build_count += 1
            if args.record:  # verbose only for single record
                print(render_ledger(artbase_id, fresh_ledger))

    if args.check:
        if drift_count:
            print(f"\n✗ {drift_count} ledger(s) have drifted from attestations.")
            sys.exit(1)
        else:
            print(f"✓ All {len(paths)} ledgers match their attestations.")
    else:
        if not args.record:
            print(f"✓ Built source ledgers for {build_count} artist records.")


if __name__ == "__main__":
    main()
