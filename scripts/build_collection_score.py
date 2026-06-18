#!/usr/bin/env python3
"""
build_collection_score.py — Compute the Documentation Score for a collection.

Score = Coverage × Quality
where Quality = (w_g × Completeness) + (w_r × Corroboration)

Coverage is always measured against total_extent (the denominator rule).
Completeness and Corroboration are means over catalogued works only.
L1 and L2 corroboration are reported separately.

Usage:
    python3 scripts/build_collection_score.py COL-LNMM
    python3 scripts/build_collection_score.py --all
    python3 scripts/build_collection_score.py COL-DEMO --print
    python3 scripts/build_collection_score.py COL-DEMO --gaps
    python3 scripts/build_collection_score.py --check

From copilot-spec-11-collection-score.md.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

REPO_ROOT       = Path(__file__).resolve().parent.parent
COLLECTIONS_DIR = REPO_ROOT / "artbase_export" / "data" / "collections"
ARTWORKS_DIR    = REPO_ROOT / "artbase_export" / "data" / "artworks"

# ── Default weights (config_version: "weights-v1") ────────────────────────────
# All tunable; stored alongside each score as config_version so results are
# reproducible under the weights that were in force at generation time.

WEIGHTS_V1 = {
    "config_version": "weights-v1",

    # Completeness section weights (must sum to 1.0)
    "completeness": {
        "identity":    0.30,   # title, creator, date, medium, dimensions, object type
        "provenance":  0.25,   # ownership chain recorded
        "authority":   0.15,   # ≥1 confirmed authority link
        "condition":   0.15,   # condition statement present
        "image":       0.10,   # image present
        "structured":  0.05,   # permanent ID + export record
    },

    # Quality blend
    "w_completeness": 0.60,    # weight of Completeness in Quality
    "w_corroboration": 0.40,   # weight of Corroboration in Quality

    # Per-level L1 corroboration blend
    "corr_blend_L1": 0.60,
    "corr_blend_L2": 0.40,

    # Corroboration level → numeric value
    "level_values": {
        "FULLY_CORROBORATED":     1.00,
        "PARTIALLY_CORROBORATED": 0.50,
        "ENTITY_SUPPLIED_ONLY":   0.15,
        "PENDING":                0.00,
    },

    # Grade band thresholds (lower bound, inclusive)
    "bands": [
        (85, "Fully Documented"),
        (65, "Substantially Documented"),
        (35, "Partially Documented"),
        (15, "Catalogued"),
        (0,  "Inventory Only"),
    ],
}


# ── Completeness ──────────────────────────────────────────────────────────────

def _completeness_identity(oid: dict) -> float:
    """Fill fraction for identity section (6 key fields)."""
    fields = [
        oid.get("title"),
        oid.get("maker_id") or oid.get("maker_display_name"),
        oid.get("date_display"),
        oid.get("materials"),
        oid.get("dimensions_display") or oid.get("height_cm"),
        oid.get("object_type"),
    ]
    present = sum(1 for f in fields if f)
    return present / len(fields)


def _completeness_provenance(passport: dict) -> float:
    prov = passport.get("provenance") or []
    if not prov:
        return 0.0
    # Partial if some entries lack source; full if all have sources and no gaps
    sourced = sum(1 for p in prov if p.get("source"))
    gap_free = all(not p.get("is_gap") for p in prov)
    fill = sourced / max(len(prov), 1)
    return fill * (1.0 if gap_free else 0.7)


def _completeness_authority(passport: dict) -> float:
    links = passport.get("authority_links") or {}
    confirmed = any(
        (v.get("status") if isinstance(v, dict) else None) in ("confirmed", "working")
        for k, v in links.items()
        if k != "artbase_id" and isinstance(v, dict)
    )
    return 1.0 if confirmed else 0.0


def _completeness_condition(passport: dict) -> float:
    cat = passport.get("cataloguing") or {}
    return 1.0 if cat.get("condition_note") else 0.0


def _completeness_image(passport: dict) -> float:
    return 1.0 if (passport.get("object_id") or {}).get("has_photograph") else 0.0


def _completeness_structured(passport: dict) -> float:
    # Permanent canonical ID = export-ready record
    return 1.0 if passport.get("artbase_canonical_id") else 0.0


def work_completeness(passport: dict, weights: dict) -> float:
    oid = passport.get("object_id") or {}
    w   = weights["completeness"]
    return (
        w["identity"]   * _completeness_identity(oid)   +
        w["provenance"] * _completeness_provenance(passport) +
        w["authority"]  * _completeness_authority(passport) +
        w["condition"]  * _completeness_condition(passport) +
        w["image"]      * _completeness_image(passport)  +
        w["structured"] * _completeness_structured(passport)
    )


# ── Corroboration ─────────────────────────────────────────────────────────────

def derive_L1_level(passport: dict) -> str:
    """
    L1 = identity corroboration.  Derived from authority_links and attestations.
    If the passport carries an explicit 'validation_level.L1', use it.
    """
    vl = (passport.get("source_ledger") or {}).get("validation") or {}
    if vl.get("L1"):
        return vl["L1"]

    # Derive from authority_links
    links = passport.get("authority_links") or {}
    confirmed_links = [
        k for k, v in links.items()
        if k != "artbase_id" and isinstance(v, dict)
        and v.get("status") in ("confirmed",)
    ]
    if confirmed_links:
        return "FULLY_CORROBORATED"

    # Check attestations for authoritative entries
    attestations = passport.get("attestations") or []
    authoritative = [a for a in attestations if a.get("authoritative")]
    origin_only   = all(a.get("role") == "data_origin" for a in attestations)

    if authoritative:
        return "PARTIALLY_CORROBORATED"
    if attestations and not origin_only:
        return "PARTIALLY_CORROBORATED"
    if attestations:
        return "ENTITY_SUPPLIED_ONLY"
    return "PENDING"


def derive_L2_level(passport: dict) -> str:
    """
    L2 = provenance corroboration.  Derived from the provenance chain quality.
    If the passport carries an explicit 'validation_level.L2', use it.
    """
    vl = (passport.get("source_ledger") or {}).get("validation") or {}
    if vl.get("L2"):
        return vl["L2"]

    prov = passport.get("provenance") or []
    if not prov:
        return "PENDING"

    sourced      = [p for p in prov if p.get("source")]
    has_gap      = any(p.get("is_gap") for p in prov)
    n_sourced    = len(sourced)

    if n_sourced >= 2 and not has_gap:
        return "FULLY_CORROBORATED"
    if n_sourced >= 1:
        return "PARTIALLY_CORROBORATED"
    return "ENTITY_SUPPLIED_ONLY"


def work_corroboration(passport: dict, weights: dict) -> tuple[float, str, str]:
    """Return (blended_score, L1_level, L2_level)."""
    lv = weights["level_values"]
    L1 = derive_L1_level(passport)
    L2 = derive_L2_level(passport)
    blended = (
        weights["corr_blend_L1"] * lv[L1] +
        weights["corr_blend_L2"] * lv[L2]
    )
    return blended, L1, L2


# ── Band ──────────────────────────────────────────────────────────────────────

def score_to_band(score_pct: float, weights: dict) -> str:
    for threshold, label in weights["bands"]:
        if score_pct >= threshold:
            return label
    return "Inventory Only"


# ── Gap breakdown ─────────────────────────────────────────────────────────────

def compute_gaps(passports: list[dict]) -> dict:
    if not passports:
        return {}
    n = len(passports)

    def rate(fn) -> float:
        return sum(1 for p in passports if fn(p)) / n

    lv = WEIGHTS_V1["level_values"]

    return {
        "provenance_documented":  rate(lambda p: bool(p.get("provenance"))),
        "condition_documented":   rate(lambda p: bool((p.get("cataloguing") or {}).get("condition_note"))),
        "authority_linked":       rate(lambda p: _completeness_authority(p) > 0),
        "image_present":          rate(lambda p: _completeness_image(p) > 0),
        "fully_corroborated_L1":  rate(lambda p: derive_L1_level(p) == "FULLY_CORROBORATED"),
        "fully_corroborated_L2":  rate(lambda p: derive_L2_level(p) == "FULLY_CORROBORATED"),
    }


# ── Core scoring ──────────────────────────────────────────────────────────────

def score_collection(col: dict, passports: list[dict],
                     weights: dict) -> Optional[dict]:
    """
    Compute the Documentation Score block for a collection.
    Returns None if scope is not defined (total_extent missing).
    """
    scope = col.get("scope") or {}
    total_extent = scope.get("total_extent")
    if not total_extent:
        return None  # Scope not established → not scorable

    n_catalogued = len(passports)

    # B1 Coverage
    coverage = n_catalogued / total_extent

    if n_catalogued == 0:
        # Zero catalogued: completeness and corroboration are vacuously 0
        return {
            "documentation_score": 0,
            "band": "Inventory Only",
            "coverage": round(coverage, 4),
            "completeness": None,
            "corroboration": {"blended": None, "L1": None, "L2": None},
            "gaps": {},
            "config_version": weights["config_version"],
        }

    # B2 Completeness
    comps = [work_completeness(p, weights) for p in passports]
    mean_completeness = sum(comps) / n_catalogued

    # B3 Corroboration
    corr_results = [work_corroboration(p, weights) for p in passports]
    mean_blended = sum(r[0] for r in corr_results) / n_catalogued
    lv = weights["level_values"]
    mean_L1 = sum(lv[r[1]] for r in corr_results) / n_catalogued
    mean_L2 = sum(lv[r[2]] for r in corr_results) / n_catalogued

    # B4 Composite
    quality = (weights["w_completeness"] * mean_completeness +
               weights["w_corroboration"] * mean_blended)
    raw_score = coverage * quality
    score_pct = round(raw_score * 100, 1)

    return {
        "documentation_score": score_pct,
        "band": score_to_band(score_pct, weights),
        "coverage": round(coverage, 4),
        "completeness": round(mean_completeness, 4),
        "corroboration": {
            "blended": round(mean_blended, 4),
            "L1": round(mean_L1, 4),
            "L2": round(mean_L2, 4),
        },
        "gaps": compute_gaps(passports),
        "config_version": weights["config_version"],
    }


# ── I/O helpers ───────────────────────────────────────────────────────────────

def load_collection(col_id: str) -> tuple[dict, Path]:
    name = col_id if col_id.endswith(".json") else f"{col_id}.json"
    path = COLLECTIONS_DIR / name
    if not path.exists():
        sys.exit(f"Collection not found: {path}")
    return json.loads(path.read_text()), path


def load_passports(ap_ids: list[str]) -> list[dict]:
    passports = []
    for ap_id in ap_ids:
        p = ARTWORKS_DIR / f"{ap_id}.json"
        if not p.exists():
            print(f"  warning: passport {ap_id} not found — skipping", file=sys.stderr)
            continue
        passports.append(json.loads(p.read_text()))
    return passports


def save_collection(col: dict, path: Path, score: Optional[dict]):
    col["score"] = score
    col["score_generated_at"] = (
        datetime.now(timezone.utc).isoformat(timespec="seconds") if score else None
    )
    path.write_text(json.dumps(col, indent=2, ensure_ascii=False))


# ── Human-readable output ──────────────────────────────────────────────────────

def print_scorecard(col: dict):
    name   = col.get("name", col.get("collection_id"))
    scope  = col.get("scope") or {}
    score  = col.get("score")

    print(f"\n{'═'*62}")
    print(f"  {name}")
    print(f"  Scope: {scope.get('definition', '—')[:60]}")
    print(f"  Total extent: {scope.get('total_extent', 'not set')}")
    print(f"{'─'*62}")

    if score is None:
        print("  SCORE: Scope Not Established — no total_extent defined")
        print(f"{'═'*62}\n")
        return

    band  = score.get("band", "—")
    pct   = score.get("documentation_score", "—")
    cov   = score.get("coverage")
    comp  = score.get("completeness")
    corr  = score.get("corroboration") or {}

    print(f"  DOCUMENTATION SCORE: {pct}%  [{band}]")
    print(f"{'─'*62}")
    print(f"  Coverage      {_pct(cov)}  ({int((cov or 0) * (scope.get('total_extent') or 0))} of {scope.get('total_extent')} works catalogued)")
    print(f"  Completeness  {_pct(comp)}  (mean field fill across catalogued works)")
    print(f"  Corroboration {_pct(corr.get('blended'))}  (L1 identity: {_pct(corr.get('L1'))}  |  L2 provenance: {_pct(corr.get('L2'))})")

    gaps = score.get("gaps") or {}
    if gaps:
        print(f"{'─'*62}")
        print("  Gap breakdown (catalogued works):")
        for k, v in gaps.items():
            label = k.replace("_", " ").capitalize()
            bar   = "█" * int((v or 0) * 20)
            print(f"    {label:<30} {_pct(v)}  {bar}")

    cv = score.get("config_version", "—")
    at = col.get("score_generated_at", "—")
    print(f"{'─'*62}")
    print(f"  Config: {cv}   Generated: {at}")
    print(f"{'═'*62}\n")


def _pct(v) -> str:
    if v is None:
        return "  —  "
    return f"{v*100:5.1f}%"


# ── Check mode ────────────────────────────────────────────────────────────────

def check_all() -> bool:
    """Recompute all scored collections; fail if stored score drifts."""
    ok = True
    for path in sorted(COLLECTIONS_DIR.glob("COL-*.json")):
        col = json.loads(path.read_text())
        stored = col.get("score")
        if stored is None:
            continue  # not yet scored — skip
        passports = load_passports(col.get("member_passports") or [])
        fresh = score_collection(col, passports, WEIGHTS_V1)
        if fresh is None:
            continue
        if (fresh.get("documentation_score") != stored.get("documentation_score") or
                fresh.get("config_version") != stored.get("config_version")):
            print(f"DRIFT: {col['collection_id']}  stored={stored.get('documentation_score')} "
                  f"computed={fresh.get('documentation_score')}")
            ok = False
        else:
            print(f"  ok  {col['collection_id']}  {stored.get('documentation_score')}%  [{stored.get('band')}]")
    return ok


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("collection_id", nargs="?",
                        help="Collection ID (e.g. COL-LNMM) or omit with --all/--check")
    parser.add_argument("--all",   action="store_true", help="Score all collections")
    parser.add_argument("--check", action="store_true",
                        help="Verify stored scores match member data; exit 1 on drift")
    parser.add_argument("--print", dest="print_card", action="store_true",
                        help="Print human-readable score card (does not write)")
    parser.add_argument("--gaps",  action="store_true",
                        help="Print gap breakdown only")
    args = parser.parse_args()

    if args.check:
        ok = check_all()
        sys.exit(0 if ok else 1)

    if args.all:
        targets = sorted(COLLECTIONS_DIR.glob("COL-*.json"))
    elif args.collection_id:
        targets = [COLLECTIONS_DIR / (
            args.collection_id if args.collection_id.endswith(".json")
            else f"{args.collection_id}.json"
        )]
    else:
        parser.print_help()
        sys.exit(1)

    for path in targets:
        if not path.exists():
            print(f"Not found: {path}", file=sys.stderr)
            continue

        col = json.loads(path.read_text())
        col_id = col.get("collection_id", path.stem)
        passports = load_passports(col.get("member_passports") or [])

        scope = col.get("scope") or {}
        if not scope.get("total_extent"):
            print(f"{col_id}: Scope Not Established (no total_extent) — not scored")
            continue

        score = score_collection(col, passports, WEIGHTS_V1)

        if args.gaps:
            gaps = (score or {}).get("gaps") or {}
            print(f"\n{col_id} — gap breakdown:")
            for k, v in gaps.items():
                print(f"  {k:<30} {_pct(v)}")
            continue

        if args.print_card:
            col["score"] = score  # inject for display, don't write
            print_scorecard(col)
            continue

        # Default: compute and write
        save_collection(col, path, score)
        band = (score or {}).get("band", "Scope Not Established")
        pct  = (score or {}).get("documentation_score", "—")
        n    = len(passports)
        total = scope.get("total_extent", "?")
        print(f"  {col_id:<25}  {pct}%  [{band}]  ({n}/{total} works)")


if __name__ == "__main__":
    main()
