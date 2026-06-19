#!/usr/bin/env python3
"""
build_collection_score.py — Compute the Ars Accordia Score for a collection.

Per-passport value:
    v_i = 100 × (w_g × Completeness_i  +  w_r × Corroboration_i)    # 0–100 per passport

Collection outputs (always shown together):
    Ars Accordia Score  = Σ v_i                 # open-ended absolute figure
    Average standard    = mean(v_i)             # 0–100, size-independent; carries the band
    Works documented    = count(passports)

Optional (only when scope.total_extent is known and solid):
    Relative completeness = Σ v_i / (N × 100)  # 0–1

Completeness is measured exclusively on the Ars Accordia Passport (four core sections
always scored; two depth sections enter only when the engagement commissions them).
Weights renormalise to 1.0 over in-scope sections.

No denominator (total_extent) is required to score a collection. N feeds only the
optional relative-completeness view and is never forced or guessed.

Usage:
    python3 scripts/build_collection_score.py COL-LNMM
    python3 scripts/build_collection_score.py --all
    python3 scripts/build_collection_score.py COL-DEMO --print
    python3 scripts/build_collection_score.py COL-DEMO --gaps
    python3 scripts/build_collection_score.py --check

From copilot-spec-11-collection-score.md (AA_CollectionScore revision).
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

# ── Weights (config_version: "weights-v2") ────────────────────────────────────
# Passport-anchored absolute model.
# Core sections always in scope; depth sections only when commissioned.
# All reference weights renormalise to 1.0 over the in-scope set.

WEIGHTS_V2 = {
    "config_version": "weights-v2",

    # Passport sections with reference weights.
    # depth=False → always in scope; depth=True → only when engagement commissions it.
    "sections": {
        "identity":   {"weight": 0.35, "depth": False},  # title, creator, date, medium, dimensions, type
        "authority":  {"weight": 0.25, "depth": False},  # ≥1 corroborated authority link on the work
        "provenance": {"weight": 0.25, "depth": False},  # ownership chain with a cited source per step
        "structured": {"weight": 0.15, "depth": False},  # JSON-LD + EODEM export record
        "condition":  {"weight": 0.15, "depth": True},   # AA-produced condition report
        "image":      {"weight": 0.10, "depth": True},   # AA-captured or AA-verified image
    },

    # Per-passport quality blend
    "w_completeness":  0.60,
    "w_corroboration": 0.40,

    # Corroboration level blend (L1 = identity, L2 = provenance)
    "corr_blend_L1": 0.60,
    "corr_blend_L2": 0.40,

    # Level → numeric
    "level_values": {
        "FULLY_CORROBORATED":     1.00,
        "PARTIALLY_CORROBORATED": 0.50,
        "ENTITY_SUPPLIED_ONLY":   0.15,
        "PENDING":                0.00,
    },

    # Bands on the average_standard (0–100), not the absolute score.
    # Lower bound inclusive.
    "bands": [
        (85, "Fully Corroborated"),
        (65, "Substantially Corroborated"),
        (40, "Partially Corroborated"),
        (15, "Source-Supplied"),
        (0,  "Minimal Record"),
    ],
}

# Scope statuses that allow the optional relative-completeness view.
_SOLID_STATUSES = {"inventory_confirmed", "owner_declared"}


# ── Section weighting ─────────────────────────────────────────────────────────

def active_section_weights(depth_flags: dict, weights: dict) -> dict[str, float]:
    """
    Return {section: normalised_weight} for the sections in scope.
    depth_flags comes from collection.engagement_depth.
    Core sections always included; depth sections only when flagged.
    Weights normalised so they sum to 1.0 over the in-scope set.
    """
    in_scope = {}
    for name, cfg in weights["sections"].items():
        if not cfg["depth"] or depth_flags.get(name):
            in_scope[name] = cfg["weight"]
    total = sum(in_scope.values())
    return {k: v / total for k, v in in_scope.items()}


# ── Completeness per section ───────────────────────────────────────────────────

def _completeness_identity(oid: dict) -> float:
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


def _completeness_authority(passport: dict) -> float:
    links = passport.get("authority_links") or {}
    confirmed = any(
        isinstance(v, dict) and v.get("status") in ("confirmed", "working")
        for k, v in links.items() if k != "artbase_id"
    )
    return 1.0 if confirmed else 0.0


def _completeness_provenance(passport: dict) -> float:
    prov = passport.get("provenance") or []
    if not prov:
        return 0.0
    sourced = sum(1 for p in prov if p.get("source"))
    return sourced / len(prov)


def _completeness_structured(passport: dict) -> float:
    structured = passport.get("structured_data") or passport.get("exports") or {}
    return 1.0 if structured else 0.0


def _completeness_condition(passport: dict) -> float:
    cat = passport.get("cataloguing") or {}
    return 1.0 if cat.get("condition_note") else 0.0


def _completeness_image(passport: dict) -> float:
    return 1.0 if (passport.get("object_id") or {}).get("has_photograph") else 0.0


def work_completeness(passport: dict, section_weights: dict[str, float]) -> float:
    """Completeness of a single passport over in-scope sections (0–1)."""
    oid = passport.get("object_id") or {}
    fillers = {
        "identity":   _completeness_identity(oid),
        "authority":  _completeness_authority(passport),
        "provenance": _completeness_provenance(passport),
        "structured": _completeness_structured(passport),
        "condition":  _completeness_condition(passport),
        "image":      _completeness_image(passport),
    }
    return sum(section_weights[s] * fillers[s] for s in section_weights)


# ── Corroboration ─────────────────────────────────────────────────────────────

def derive_L1_level(passport: dict) -> str:
    vl = (passport.get("source_ledger") or {}).get("validation") or {}
    if vl.get("L1"):
        return vl["L1"]

    links = passport.get("authority_links") or {}
    if any(
        isinstance(v, dict) and v.get("status") == "confirmed"
        for k, v in links.items() if k != "artbase_id"
    ):
        return "FULLY_CORROBORATED"

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
    vl = (passport.get("source_ledger") or {}).get("validation") or {}
    if vl.get("L2"):
        return vl["L2"]

    prov = passport.get("provenance") or []
    if not prov:
        return "PENDING"

    sourced   = [p for p in prov if p.get("source")]
    has_gap   = any(p.get("is_gap") for p in prov)
    n_sourced = len(sourced)

    if n_sourced >= 2 and not has_gap:
        return "FULLY_CORROBORATED"
    if n_sourced >= 1:
        return "PARTIALLY_CORROBORATED"
    return "ENTITY_SUPPLIED_ONLY"


def work_corroboration(passport: dict, weights: dict) -> tuple[float, str, str]:
    lv = weights["level_values"]
    L1 = derive_L1_level(passport)
    L2 = derive_L2_level(passport)
    blended = (
        weights["corr_blend_L1"] * lv[L1] +
        weights["corr_blend_L2"] * lv[L2]
    )
    return blended, L1, L2


# ── Band (on average standard) ────────────────────────────────────────────────

def avg_to_band(avg_std: float | None, weights: dict) -> str | None:
    if avg_std is None:
        return None
    for threshold, label in weights["bands"]:
        if avg_std >= threshold:
            return label
    return "Minimal Record"


# ── Gap breakdown ─────────────────────────────────────────────────────────────

def compute_gaps(passports: list[dict], section_weights: dict[str, float]) -> dict:
    if not passports:
        return {}
    n = len(passports)

    def rate(fn) -> float:
        return sum(1 for p in passports if fn(p)) / n

    gaps: dict[str, float] = {}

    # Core sections always shown
    gaps["identity_complete"] = rate(
        lambda p: _completeness_identity(p.get("object_id") or {}) >= 0.99
    )
    gaps["authority_linked"]   = rate(lambda p: _completeness_authority(p) > 0)
    gaps["provenance_sourced"] = rate(lambda p: _completeness_provenance(p) >= 1.0)
    gaps["structured_export"]  = rate(lambda p: _completeness_structured(p) > 0)

    # Depth sections — only when commissioned
    if "condition" in section_weights:
        gaps["condition_documented"] = rate(lambda p: _completeness_condition(p) > 0)
    if "image" in section_weights:
        gaps["image_present"] = rate(lambda p: _completeness_image(p) > 0)

    gaps["fully_corroborated_L1"] = rate(lambda p: derive_L1_level(p) == "FULLY_CORROBORATED")
    gaps["fully_corroborated_L2"] = rate(lambda p: derive_L2_level(p) == "FULLY_CORROBORATED")

    return gaps


# ── Core scoring ──────────────────────────────────────────────────────────────

def score_collection(col: dict, passports: list[dict],
                     weights: dict) -> dict:
    """
    Compute the score block for a collection.
    Always returns a dict (no total_extent required to score).
    """
    scope           = col.get("scope") or {}
    total_extent    = scope.get("total_extent")
    scope_status    = scope.get("status", "unknown")
    depth_flags     = col.get("engagement_depth") or {}
    section_weights = active_section_weights(depth_flags, weights)
    sections_active = sorted(section_weights.keys())

    n = len(passports)

    if n == 0:
        return {
            "ars_accordia_score":   0,
            "average_standard":     None,
            "works_documented":     0,
            "band":                 None,
            "completeness":         None,
            "corroboration":        {"blended": None, "L1": None, "L2": None},
            "relative_completeness": None,
            "gaps":                 {},
            "sections_in_scope":    sections_active,
            "config_version":       weights["config_version"],
        }

    # Per-passport values
    v_list: list[float] = []
    g_list: list[float] = []
    corr_results: list[tuple[float, str, str]] = []

    for p in passports:
        g_i = work_completeness(p, section_weights)
        r_i, L1, L2 = work_corroboration(p, weights)
        v_i = 100.0 * (weights["w_completeness"] * g_i + weights["w_corroboration"] * r_i)
        v_list.append(v_i)
        g_list.append(g_i)
        corr_results.append((r_i, L1, L2))

    ars_accordia_score = round(sum(v_list), 1)
    average_standard   = round(sum(v_list) / n, 1)
    mean_completeness  = sum(g_list) / n
    mean_blended       = sum(r[0] for r in corr_results) / n
    lv                 = weights["level_values"]
    mean_L1            = sum(lv[r[1]] for r in corr_results) / n
    mean_L2            = sum(lv[r[2]] for r in corr_results) / n

    # Relative completeness: only when total_extent is known and solid
    relative_completeness = None
    if total_extent and scope_status in _SOLID_STATUSES:
        relative_completeness = round(ars_accordia_score / (total_extent * 100), 4)

    return {
        "ars_accordia_score":    ars_accordia_score,
        "average_standard":      average_standard,
        "works_documented":      n,
        "band":                  avg_to_band(average_standard, weights),
        "completeness":          round(mean_completeness, 4),
        "corroboration": {
            "blended": round(mean_blended, 4),
            "L1":      round(mean_L1, 4),
            "L2":      round(mean_L2, 4),
        },
        "relative_completeness": relative_completeness,
        "gaps":                  compute_gaps(passports, section_weights),
        "sections_in_scope":     sections_active,
        "config_version":        weights["config_version"],
    }


# ── I/O helpers ───────────────────────────────────────────────────────────────

def load_passports(ap_ids: list[str]) -> list[dict]:
    passports = []
    for ap_id in ap_ids:
        p = ARTWORKS_DIR / f"{ap_id}.json"
        if not p.exists():
            print(f"  warning: passport {ap_id} not found — skipping", file=sys.stderr)
            continue
        passports.append(json.loads(p.read_text()))
    return passports


def save_collection(col: dict, path: Path, score: dict):
    col["score"] = score
    col["score_generated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    path.write_text(json.dumps(col, indent=2, ensure_ascii=False))


# ── Human-readable output ──────────────────────────────────────────────────────

def print_scorecard(col: dict):
    name   = col.get("name", col.get("collection_id"))
    scope  = col.get("scope") or {}
    score  = col.get("score") or {}

    print(f"\n{'═'*66}")
    print(f"  {name}")
    print(f"  Scope: {scope.get('definition', '—')[:64]}")
    print(f"{'─'*66}")

    aa   = score.get("ars_accordia_score")
    avg  = score.get("average_standard")
    wks  = score.get("works_documented", 0)
    band = score.get("band") or "—"
    comp = score.get("completeness")
    corr = score.get("corroboration") or {}
    rel  = score.get("relative_completeness")
    secs = score.get("sections_in_scope") or []

    if wks == 0:
        print("  No passports yet — score is 0.")
    else:
        print(f"  ARS ACCORDIA SCORE  {aa}  ·  {wks} works  ·  avg standard {avg}")
        print(f"  Band (average standard): {band}")
    print(f"{'─'*66}")
    print(f"  Completeness    {_pct(comp)}  (sections: {', '.join(secs)})")
    print(f"  Corroboration   {_pct(corr.get('blended'))}  "
          f"(L1 identity: {_pct(corr.get('L1'))}  |  L2 provenance: {_pct(corr.get('L2'))})")

    if rel is not None:
        n = scope.get("total_extent", "?")
        print(f"  Relative        {_pct(rel)}  ({wks} of {n} works × quality)")

    gaps = score.get("gaps") or {}
    if gaps:
        print(f"{'─'*66}")
        print("  Gap breakdown (catalogued works):")
        for k, v in gaps.items():
            label = k.replace("_", " ").capitalize()
            bar   = "█" * int((v or 0) * 20)
            print(f"    {label:<32} {_pct(v)}  {bar}")

    cv = score.get("config_version", "—")
    at = col.get("score_generated_at", "—")
    print(f"{'─'*66}")
    print(f"  Config: {cv}   Generated: {at}")
    print(f"{'═'*66}\n")


def _pct(v) -> str:
    if v is None:
        return "    —  "
    return f"{v*100:5.1f}%"


# ── Check mode ────────────────────────────────────────────────────────────────

def check_all() -> bool:
    ok = True
    for path in sorted(COLLECTIONS_DIR.glob("COL-*.json")):
        col    = json.loads(path.read_text())
        stored = col.get("score")
        if stored is None:
            continue
        passports = load_passports(col.get("member_passports") or [])
        fresh = score_collection(col, passports, WEIGHTS_V2)
        if (fresh.get("ars_accordia_score") != stored.get("ars_accordia_score") or
                fresh.get("config_version") != stored.get("config_version")):
            print(f"DRIFT: {col['collection_id']}  "
                  f"stored={stored.get('ars_accordia_score')} "
                  f"computed={fresh.get('ars_accordia_score')}")
            ok = False
        else:
            print(f"  ok  {col['collection_id']}  "
                  f"score={stored.get('ars_accordia_score')}  "
                  f"avg={stored.get('average_standard')}  "
                  f"[{stored.get('band') or 'no passports'}]")
    return ok


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("collection_id", nargs="?",
                        help="Collection ID (e.g. COL-LNMM), or omit with --all/--check")
    parser.add_argument("--all",   action="store_true", help="Score all collections")
    parser.add_argument("--check", action="store_true",
                        help="Verify stored scores match member data; exit 1 on drift")
    parser.add_argument("--print", dest="print_card", action="store_true",
                        help="Print human-readable score card (does not write)")
    parser.add_argument("--gaps",  action="store_true",
                        help="Print gap breakdown only")
    args = parser.parse_args()

    if args.check:
        sys.exit(0 if check_all() else 1)

    if args.all:
        targets = sorted(COLLECTIONS_DIR.glob("COL-*.json"))
    elif args.collection_id:
        name = (args.collection_id if args.collection_id.endswith(".json")
                else f"{args.collection_id}.json")
        targets = [COLLECTIONS_DIR / name]
    else:
        parser.print_help()
        sys.exit(1)

    for path in targets:
        if not path.exists():
            print(f"Not found: {path}", file=sys.stderr)
            continue

        col       = json.loads(path.read_text())
        col_id    = col.get("collection_id", path.stem)
        passports = load_passports(col.get("member_passports") or [])
        score     = score_collection(col, passports, WEIGHTS_V2)

        if args.gaps:
            gaps = score.get("gaps") or {}
            print(f"\n{col_id} — gap breakdown:")
            for k, v in gaps.items():
                print(f"  {k:<32} {_pct(v)}")
            continue

        if args.print_card:
            col["score"] = score
            print_scorecard(col)
            continue

        save_collection(col, path, score)
        aa   = score.get("ars_accordia_score", 0)
        avg  = score.get("average_standard")
        band = score.get("band") or "no passports"
        n    = score.get("works_documented", 0)
        print(f"  {col_id:<25}  score={aa}  avg={avg}  [{band}]  ({n} works)")


if __name__ == "__main__":
    main()
