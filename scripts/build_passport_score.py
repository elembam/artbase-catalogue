#!/usr/bin/env python3
"""
build_passport_score.py — Compute the Passport Score for one or all artwork passports.

Each passport receives a score from 0 to 100:

    Passport Score = 100 × Completeness

This is the atom of the collection score:
    Ars Accordia Score  = Σ passport_scores
    Average standard    = mean(passport_scores)

The full derivation (sections, fill values, arithmetic) is written to a "score"
block on the passport record so the page can show exactly how the number was reached.

There is no corroboration term. Cross-references to public authority records are
rewarded as completeness (the authority_links section), never as a separate judgement.

Usage:
    python3 scripts/build_passport_score.py AP-2026-000001
    python3 scripts/build_passport_score.py --all
    python3 scripts/build_passport_score.py AP-2026-000001 --print
    python3 scripts/build_passport_score.py --check

From copilot-spec-13-passport-score.md (AA_Scoring2 / weights-v3).
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# ── Shared constants (imported from Instruction 11 so the two never drift) ────

_SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPTS))

from build_collection_score import (  # noqa: E402
    WEIGHTS_V3,
    active_section_weights,
    work_completeness,
    round_half_up,
    _completeness_identity,
    _completeness_authority,
    _completeness_provenance,
    _completeness_structured,
    _completeness_condition,
    _completeness_image,
)

REPO_ROOT       = Path(__file__).resolve().parent.parent
ARTWORKS_DIR    = REPO_ROOT / "artbase_export" / "data" / "artworks"
COLLECTIONS_DIR = REPO_ROOT / "artbase_export" / "data" / "collections"


# ── Passport path resolution ──────────────────────────────────────────────────

def find_passport_path(passport_id: str) -> Path | None:
    # Flat: AP-2026-000001.json
    flat = ARTWORKS_DIR / f"{passport_id}.json"
    if flat.exists():
        return flat
    # Nested: AA/LV/LNMA/007.json  →  passport_id may contain slashes
    nested = ARTWORKS_DIR / f"{passport_id}.json"
    if nested.exists():
        return nested
    # Search recursively
    for p in ARTWORKS_DIR.rglob("*.json"):
        data = json.loads(p.read_text())
        if data.get("artbase_id") == passport_id:
            return p
    return None


def all_passport_paths() -> list[Path]:
    return sorted(ARTWORKS_DIR.rglob("*.json"))


# ── Collection membership & depth flags ──────────────────────────────────────

def find_depth_flags(passport_id: str) -> dict:
    """Return engagement_depth from the collection this passport belongs to, else {}."""
    for col_path in COLLECTIONS_DIR.glob("COL-*.json"):
        col = json.loads(col_path.read_text())
        if passport_id in (col.get("member_passports") or []):
            return col.get("engagement_depth") or {}
    return {}


# ── Human-readable section descriptions ──────────────────────────────────────

def _identity_present(oid: dict) -> str:
    fields = {
        "title":       oid.get("title"),
        "creator":     oid.get("maker_id") or oid.get("maker_display_name"),
        "date":        oid.get("date_display"),
        "medium":      oid.get("materials"),
        "dimensions":  oid.get("dimensions_display") or oid.get("height_cm"),
        "object type": oid.get("object_type"),
    }
    n = sum(1 for v in fields.values() if v)
    if n == 6:
        return "6 of 6 fields"
    missing = [k for k, v in fields.items() if not v]
    return f"{n} of 6 fields (missing: {', '.join(missing)})"


def _authority_present(passport: dict) -> str:
    links = passport.get("authority_links") or {}
    names = [
        k.upper()
        for k, v in links.items()
        if k != "artbase_id"
        and isinstance(v, dict)
        and v.get("status") in ("confirmed", "working")
    ]
    if not names:
        return "—"
    s = "public authority" if len(names) == 1 else "public authorities"
    return f"{len(names)} {s} — {', '.join(names)}"


def _provenance_present(passport: dict) -> str:
    prov = passport.get("provenance") or []
    if not prov:
        return "no chain"
    sourced = sum(1 for p in prov if p.get("source"))
    step = "step" if len(prov) == 1 else "steps"
    return f"{sourced} of {len(prov)} {step} sourced"


def _structured_present(passport: dict) -> str:
    structured = passport.get("structured_data") or {}
    exports    = passport.get("exports") or {}
    has_jsonld = bool(
        structured.get("json_ld") or structured.get("schema_org") or exports.get("json_ld")
    )
    has_eodem = bool(structured.get("eodem") or exports.get("eodem"))
    if has_jsonld and has_eodem:
        return "JSON-LD + EODEM"
    if has_jsonld:
        return "JSON-LD only"
    if has_eodem:
        return "EODEM only"
    return "—"


def _condition_present(passport: dict) -> str:
    cat = passport.get("cataloguing") or {}
    return "Condition report present" if cat.get("condition_note") else "—"


def _image_present(passport: dict) -> str:
    oid = passport.get("object_id") or {}
    return "Image present" if oid.get("has_photograph") else "—"


# ── Status badge ──────────────────────────────────────────────────────────────

def derive_status(passport: dict) -> str:
    """
    Objective cross-reference status — not a corroboration verdict.
    green   — cross-referenced to public authorities and human-reviewed
    amber   — cross-referenced but not yet human-reviewed
    grey    — no public-authority cross-reference yet
    pending — no data at all (should not be published)
    """
    links = passport.get("authority_links") or {}
    confirmed = any(
        isinstance(v, dict) and v.get("status") in ("confirmed", "working")
        for k, v in links.items() if k != "artbase_id"
    )
    review_status = (passport.get("cataloguing") or {}).get("review_status", "draft")

    if confirmed and review_status in ("reviewed", "published"):
        return "green"
    if confirmed:
        return "amber"
    # Use pending only when the passport has no title at all (truly empty)
    if not (passport.get("object_id") or {}).get("title"):
        return "pending"
    return "grey"


# ── Core passport scoring ─────────────────────────────────────────────────────

def score_passport(passport: dict, depth_flags: dict | None = None) -> dict:
    """
    Compute and return the full score block for a single passport.
    Passport Score = 100 × Completeness (no corroboration term).
    depth_flags: from the collection's engagement_depth; defaults to {} (core sections only).
    """
    if depth_flags is None:
        depth_flags = {}

    weights         = WEIGHTS_V3
    section_weights = active_section_weights(depth_flags, weights)
    oid             = passport.get("object_id") or {}

    _fill_fns = {
        "identity":   lambda: _completeness_identity(oid),
        "authority":  lambda: _completeness_authority(passport),
        "provenance": lambda: _completeness_provenance(passport),
        "structured": lambda: _completeness_structured(passport),
        "condition":  lambda: _completeness_condition(passport),
        "image":      lambda: _completeness_image(passport),
    }
    _present_fns = {
        "identity":   lambda: _identity_present(oid),
        "authority":  lambda: _authority_present(passport),
        "provenance": lambda: _provenance_present(passport),
        "structured": lambda: _structured_present(passport),
        "condition":  lambda: _condition_present(passport),
        "image":      lambda: _image_present(passport),
    }

    sections_data = []
    for sec_name in ("identity", "authority", "provenance", "structured", "condition", "image"):
        in_scope    = sec_name in section_weights
        norm_weight = section_weights[sec_name] if in_scope else 0.0

        if in_scope:
            fill    = round(_fill_fns[sec_name](), 4)
            present = _present_fns[sec_name]()
        else:
            fill    = None
            present = "not commissioned"

        contribution = round(norm_weight * (fill if fill is not None else 0.0), 4)

        sections_data.append({
            "section":      sec_name,
            "weight":       norm_weight,
            "fill":         fill,
            "present":      present,
            "contribution": contribution,
            "in_scope":     in_scope,
        })

    completeness_value = round(
        sum(s["contribution"] for s in sections_data if s["in_scope"]), 4
    )

    passport_score = round_half_up(100 * completeness_value)
    status         = derive_status(passport)

    return {
        "passport_score": passport_score,
        "status":         status,
        "completeness": {
            "value":    completeness_value,
            "sections": sections_data,
        },
        "excluded":       ["source_quality_judgement", "authenticity", "monetary_value"],
        "config_version": weights["config_version"],
    }


# ── I/O ───────────────────────────────────────────────────────────────────────

def save_passport(passport: dict, path: Path, score: dict):
    passport["score"] = score
    passport["score_generated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    path.write_text(json.dumps(passport, indent=2, ensure_ascii=False))


# ── Human-readable derivation card (--print) ──────────────────────────────────

def print_derivation(passport: dict, score: dict):
    ap_id  = passport.get("artbase_id", "—")
    oid    = passport.get("object_id") or {}
    title  = oid.get("title", "—")
    maker  = oid.get("maker_display_name", "—")
    date   = oid.get("date_display", "—")
    otype  = oid.get("object_type", "—")

    ps     = score["passport_score"]
    status = score["status"].upper()
    comp   = score["completeness"]

    print(f"\n{'═'*70}")
    print(f"  {title}")
    print(f"  {maker} · {date} · {otype}")
    print(f"  {ap_id}")
    print(f"{'─'*70}")
    print(f"  PASSPORT SCORE  {ps}  ·  Status: {status}")
    print(f"{'─'*70}")
    print(f"  Completeness  {comp['value']*100:.2f}%")
    print()
    in_scope  = [s for s in comp["sections"] if s["in_scope"]]
    out_scope = [s for s in comp["sections"] if not s["in_scope"]]
    for s in in_scope:
        w  = s["weight"]
        f  = s["fill"] if s["fill"] is not None else 0.0
        c  = s["contribution"]
        nm = s["section"].replace("_", " ").title()
        print(f"    {nm:<22} {w:.2f} × {f:.2f} = {c:.4f}  \"{s['present']}\"")
    print(f"    {'─'*44}")
    print(f"    {'Completeness':<22}              {comp['value']:.4f}")
    if out_scope:
        print()
        for s in out_scope:
            nm = s["section"].replace("_", " ").title()
            print(f"    {nm:<22} [not commissioned — excluded]")
    print(f"{'─'*70}")
    cv = comp["value"]
    print(f"  Passport Score = 100 × {cv:.4f} = {ps}")
    print(f"{'─'*70}")
    print(f"  Not scored: source quality judgement, authenticity, monetary value.")
    print(f"  Config: {score['config_version']}")
    print(f"{'═'*70}\n")


# ── Check mode ────────────────────────────────────────────────────────────────

def check_all() -> bool:
    ok = True

    # 1. Verify each stored passport score matches current data
    for path in sorted(all_passport_paths()):
        passport = json.loads(path.read_text())
        stored   = passport.get("score")
        if stored is None:
            continue
        ap_id       = passport.get("artbase_id", path.stem)
        depth_flags = find_depth_flags(ap_id)
        fresh       = score_passport(passport, depth_flags)

        if (fresh["passport_score"] != stored.get("passport_score")
                or fresh["config_version"] != stored.get("config_version")):
            print(f"DRIFT: {ap_id}  "
                  f"stored={stored.get('passport_score')}  "
                  f"computed={fresh['passport_score']}")
            ok = False
        else:
            print(f"  ok  {ap_id:<40} score={stored['passport_score']}  "
                  f"status={stored.get('status', '—')}")

    # 2. Cross-check: Σ recomputed raw passport values == stored collection score
    print()
    for col_path in sorted(COLLECTIONS_DIR.glob("COL-*.json")):
        col       = json.loads(col_path.read_text())
        col_id    = col.get("collection_id", col_path.stem)
        col_score = (col.get("score") or {}).get("ars_accordia_score")
        members   = col.get("member_passports") or []
        if col_score is None or not members:
            continue

        depth_flags     = col.get("engagement_depth") or {}
        section_weights = active_section_weights(depth_flags, WEIGHTS_V3)
        raw_sum         = 0.0

        for ap_id in members:
            pp = find_passport_path(ap_id)
            if pp is None:
                print(f"  WARN  {ap_id} not found — skipping from sum")
                continue
            p        = json.loads(pp.read_text())
            raw_sum += float(round_half_up(100.0 * work_completeness(p, section_weights)))

        raw_sum = round(raw_sum, 1)
        if abs(raw_sum - col_score) > 0.15:
            print(f"MISMATCH  {col_id}  Σ raw={raw_sum}  != collection={col_score}")
            ok = False
        else:
            print(f"  ok  {col_id:<30} Σ raw={raw_sum} == collection={col_score}")

    return ok


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "passport_id", nargs="?",
        help="Passport ID (e.g. AP-2026-000001), or omit with --all / --check",
    )
    parser.add_argument("--all",   action="store_true", help="Score all passports")
    parser.add_argument("--check", action="store_true",
                        help="Verify stored scores match data; exit 1 on drift")
    parser.add_argument("--print", dest="print_card", action="store_true",
                        help="Print human-readable derivation card (no write)")
    args = parser.parse_args()

    if args.check:
        sys.exit(0 if check_all() else 1)

    if args.all:
        targets = all_passport_paths()
    elif args.passport_id:
        path = find_passport_path(args.passport_id)
        if path is None:
            print(f"Not found: {args.passport_id}", file=sys.stderr)
            sys.exit(1)
        targets = [path]
    else:
        parser.print_help()
        sys.exit(1)

    for path in targets:
        passport    = json.loads(path.read_text())
        ap_id       = passport.get("artbase_id", path.stem)
        depth_flags = find_depth_flags(ap_id)
        score       = score_passport(passport, depth_flags)

        if args.print_card:
            print_derivation(passport, score)
            continue

        save_passport(passport, path, score)
        print(f"  {ap_id:<42} score={score['passport_score']}  "
              f"status={score['status']}  "
              f"(C={score['completeness']['value']:.2f})")


if __name__ == "__main__":
    main()
