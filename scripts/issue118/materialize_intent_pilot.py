#!/usr/bin/env python3
"""Materialize a deterministic, read-only 700-identity pilot for Issue #118.

This script does NOT classify sexual intent. It only joins current accepted General
and Special discovery metadata, reuses Issue #104 risk-review evidence as a
challenge signal, and selects a reproducible stratified pilot for semantic review.
Production data is never modified.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

PILOT_SIZE = 700
SEED = "issue118-intent-pilot-v1"

GENERAL_BOUNDARY_ROOTS = {
    "BODY_PART",
    "CLOTHING_STATE_EXPOSURE",
    "ACTION_CONTACT",
    "CLOTHING",
}

# Deliberately conservative negative-control pools. Membership here is a sampling
# signal only, never a NON_SEXUAL decision.
GENERAL_CONTROL_ROOTS = {
    "PLACE_BACKGROUND",
    "LIGHT_TIME_WEATHER",
    "STYLE_QUALITY_META",
    "TEXT_SYMBOL",
    "COLOR_APPEARANCE",
    "COMPOSITION_CAMERA",
    "GAZE_ORIENTATION",
    "HAIR_FACE",
    "EXPRESSION_EMOTION",
    "PERSON_COUNT",
    "LIVING_NATURE",
}

SPECIAL_BOUNDARY_FAMILIES = {
    "BODY_ATTRIBUTE",
    "BODY_STATE",
    "REPRO_BODY_STATE",
    "CLOTHING_EXPOSURE",
    "ACTION_INTERACTION",
    "MULTI_ACTOR_INTERACTION",
    "SELF_ACTION",
    "INSERTION_STRUCTURED",
    "RESTRAINT_ACTION",
    "RESTRAINT_IMPLEMENT",
    "FLUID_STATE_ACTION",
    "RELATION_ROLE_CONTEXT",
    "POSE_COMPOSITION",
    "CONTEXT_MODIFIER",
    "DIRECT_COMPOSITE",
    "IMPLEMENT_OBJECT",
    "REACTION_STATE",
}


def normalize_tag(value: str) -> str:
    # Same normalization used by Issue #109's accepted reverse-audit materializer.
    return "_".join(value.strip().lower().replace("_", " ").split())


def hash_rank(key: str) -> str:
    return hashlib.sha256(f"{SEED}|{key}".encode("utf-8")).hexdigest()


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def primary_root(row: dict[str, str] | None) -> str:
    if not row:
        return ""
    path = (row.get("primary_path") or "").strip()
    return path.split("/", 1)[0] if path else ""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--general", default="docs/issue64/production_candidate/effective_sidecar.csv")
    ap.add_argument("--special", default="data/generation/special2788_generation_profile.csv")
    ap.add_argument("--issue104", default="docs/issue104/product_fit_review_v1.csv")
    ap.add_argument("--out-dir", default="docs/issue118")
    args = ap.parse_args()

    general_path = Path(args.general)
    special_path = Path(args.special)
    issue104_path = Path(args.issue104)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    general_rows = read_csv(general_path)
    special_rows = read_csv(special_path)
    issue104_rows = read_csv(issue104_path)

    if len(general_rows) != 30629:
        raise SystemExit(f"expected current General 30629, got {len(general_rows)}")
    if len(special_rows) != 3059:
        raise SystemExit(f"expected current Special 3059, got {len(special_rows)}")

    gindex: dict[str, dict[str, str]] = {}
    for row in general_rows:
        key = normalize_tag(row["canonical"])
        if not key or key in gindex:
            raise SystemExit(f"invalid/duplicate normalized General canonical: {key!r}")
        gindex[key] = row

    sindex: dict[str, dict[str, str]] = {}
    sid_seen: set[int] = set()
    for row in special_rows:
        sid = int(row["SpecialID"])
        if sid in sid_seen:
            raise SystemExit(f"duplicate SpecialID: {sid}")
        sid_seen.add(sid)
        key = normalize_tag(row["Tag"])
        if not key or key in sindex:
            raise SystemExit(f"invalid/duplicate normalized Special surface: {key!r}")
        sindex[key] = row

    i104: dict[str, dict[str, str]] = {}
    for row in issue104_rows:
        key = normalize_tag(row["canonical_tag"])
        if key in i104:
            raise SystemExit(f"duplicate Issue104 review canonical: {key}")
        i104[key] = row

    all_keys = set(gindex) | set(sindex)
    overlap_keys = set(gindex) & set(sindex)

    records: dict[str, dict[str, str]] = {}
    for key in all_keys:
        g = gindex.get(key)
        s = sindex.get(key)
        r104 = i104.get(key)
        records[key] = {
            "identity_key": key,
            "is_general": "YES" if g else "NO",
            "is_special": "YES" if s else "NO",
            "general_canonical": (g or {}).get("canonical", ""),
            "general_status": (g or {}).get("classification_status", ""),
            "general_primary_path": (g or {}).get("primary_path", ""),
            "general_secondary_paths": (g or {}).get("secondary_paths", ""),
            "general_confidence": (g or {}).get("confidence", ""),
            "special_id": (s or {}).get("SpecialID", ""),
            "special_tag": (s or {}).get("Tag", ""),
            "generation_family": (s or {}).get("GenerationFamily", ""),
            "generation_role": (s or {}).get("GenerationRole", ""),
            "promotion_status": (s or {}).get("PromotionStatus", ""),
            "meaning_status": (s or {}).get("MeaningStatus", ""),
            "issue104_reviewed": "YES" if r104 else "NO",
            "issue104_review_source": (r104 or {}).get("review_source", ""),
            "issue104_product_fit_decision": (r104 or {}).get("product_fit_decision", ""),
            "issue104_adult_domains": (r104 or {}).get("canonical_adult_domains", ""),
            "issue104_post_count": (r104 or {}).get("post_count", ""),
            "sample_stratum": "",
            "sample_rank": hash_rank(key),
            "candidate_class": "",
            "candidate_status": "",
            "reviewed_class": "",
            "review_reason": "",
            "signal_conflict": "",
        }

    selected: list[str] = []
    selected_set: set[str] = set()
    stratum_counts = Counter()

    def choose(name: str, candidates: list[str], limit: int | None) -> None:
        pool = [k for k in candidates if k not in selected_set]
        pool.sort(key=lambda k: (records[k]["sample_rank"], k))
        if limit is not None:
            pool = pool[:limit]
        for k in pool:
            selected.append(k)
            selected_set.add(k)
            records[k]["sample_stratum"] = name
            stratum_counts[name] += 1

    # Preserve the entire currently-relevant #104 reviewed challenge set first.
    choose(
        "ISSUE104_REVIEWED_RISK",
        [k for k in i104 if k in records and k in gindex],
        None,
    )

    choose(
        "BOUNDARY_OVERLAP",
        [
            k for k in overlap_keys
            if k not in selected_set
            and (
                primary_root(gindex.get(k)) in GENERAL_BOUNDARY_ROOTS
                or (sindex.get(k) or {}).get("GenerationFamily", "") in SPECIAL_BOUNDARY_FAMILIES
            )
        ],
        120,
    )

    choose(
        "BOUNDARY_GENERAL_ONLY",
        [
            k for k in set(gindex) - set(sindex)
            if k not in selected_set and primary_root(gindex.get(k)) in GENERAL_BOUNDARY_ROOTS
        ],
        120,
    )

    choose(
        "BOUNDARY_SPECIAL_ONLY",
        [
            k for k in set(sindex) - set(gindex)
            if k not in selected_set
            and (sindex.get(k) or {}).get("GenerationFamily", "") in SPECIAL_BOUNDARY_FAMILIES
        ],
        80,
    )

    choose(
        "ORDINARY_GENERAL_CONTROL",
        [
            k for k in set(gindex) - set(sindex)
            if k not in selected_set and primary_root(gindex.get(k)) in GENERAL_CONTROL_ROOTS
        ],
        100,
    )

    # Deterministic union fill keeps the artifact exactly 700 without pretending
    # that the filler is a semantically safe/unsafe class.
    remaining = PILOT_SIZE - len(selected)
    if remaining < 0:
        # #104 is currently bounded to 236, so this should not happen. Fail rather
        # than silently truncate the highest-value challenge set.
        raise SystemExit(f"fixed strata exceed pilot size: {len(selected)} > {PILOT_SIZE}")
    choose("UNION_FILL", [k for k in all_keys if k not in selected_set], remaining)

    if len(selected) != PILOT_SIZE or len(selected_set) != PILOT_SIZE:
        raise SystemExit(f"pilot size mismatch: {len(selected)}")

    pilot = [records[k] for k in selected]
    fields = list(pilot[0].keys())
    pilot_path = out_dir / "intent_pilot_sample_v1.csv"
    with pilot_path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(pilot)

    summary = {
        "issue": 118,
        "mode": "READ_ONLY_DETERMINISTIC_INTENT_PILOT_SAMPLING",
        "seed": SEED,
        "pilot_size": PILOT_SIZE,
        "general_rows": len(general_rows),
        "special_rows": len(special_rows),
        "normalized_union_rows": len(all_keys),
        "normalized_exact_overlap_rows": len(overlap_keys),
        "issue104_review_rows_total": len(issue104_rows),
        "issue104_review_rows_in_current_general": sum(1 for k in i104 if k in gindex),
        "stratum_counts": dict(sorted(stratum_counts.items())),
        "general_boundary_roots": sorted(GENERAL_BOUNDARY_ROOTS),
        "general_control_roots": sorted(GENERAL_CONTROL_ROOTS),
        "special_boundary_families": sorted(SPECIAL_BOUNDARY_FAMILIES),
        "input_sha256": {
            str(general_path): sha256(general_path),
            str(special_path): sha256(special_path),
            str(issue104_path): sha256(issue104_path),
        },
        "output_sha256": {str(pilot_path): sha256(pilot_path)},
        "boundaries": {
            "sexual_intent_classification_performed": "NO",
            "production_data_mutated": "NO",
            "issue117_code_mutated": "NO",
            "user_db_mutated": "NO",
        },
    }
    summary_path = out_dir / "intent_pilot_sample_summary_v1.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
