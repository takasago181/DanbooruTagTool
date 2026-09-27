from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

EXPECTED = 31_003
ROUTES = {
    "ACTION_CONTACT", "BODY_SITE", "CLOTHING_EXPOSURE", "COLOR_PATTERN_SHAPE", "COMPOSITION_CAMERA",
    "CONTENT_RATING", "EXPRESSION_GAZE", "FLUID_EXCRETION", "HAIR_FACE", "LIGHT_TIME_WEATHER",
    "LIVING", "NONHUMAN_TRANSFORM", "PEOPLE_COUNT", "POSE_POSITION", "RELATION_ROLE",
    "SCENE_BACKGROUND", "STYLE_PROCESSING", "TEXT_SYMBOL", "TOOL_OBJECT",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def jlist(value: str) -> list[str]:
    parsed = json.loads(value or "[]")
    if not isinstance(parsed, list):
        raise ValueError("expected JSON array")
    return parsed


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    args = ap.parse_args()
    root = Path(args.root)
    out = root / "docs/issue132/product-reconciliation"
    diff = read_csv(out / "pass_b_full_diff.csv")
    ledger = read_csv(out / "product_reconciliation_ledger.csv")
    candidates = read_csv(out / "ADD_SECONDARY_CANDIDATES.csv")
    candidate_review = read_csv(out / "ADD_SECONDARY_CANDIDATE_REVIEW.csv")
    upstream = read_csv(out / "UPSTREAM_REVIEW.csv")
    search_only = read_csv(out / "SEARCH_ONLY.csv")
    unresolved = read_csv(out / "SEMANTIC_UNRESOLVED.csv")
    shelves = read_csv(out / "shelf_before_after.csv")
    family = read_csv(out / "candidate_family_concentration.csv")
    facets = read_csv(out / "body_theme_architecture_findings.csv")
    summary = json.loads((out / "final_reconciliation_summary.json").read_text(encoding="utf-8"))

    assert len(diff) == EXPECTED and len(ledger) == EXPECTED
    keyset = {r["identity_key"] for r in ledger}
    assert len(keyset) == EXPECTED
    assert {r["identity_key"] for r in diff} == keyset
    assert len({r["identity_key"] for r in diff}) == EXPECTED
    dispositions = Counter(r["product_disposition"] for r in ledger)
    assert dispositions == Counter(summary["pass_c_disposition_identity_counts"])
    assert sum(dispositions.values()) == EXPECTED

    assert len(candidates) == 274 and len(candidate_review) == len(candidates)
    assert list(candidates[0].keys()) == ["identity_key", "route_id"]
    assert len({(r["identity_key"], r["route_id"]) for r in candidates}) == len(candidates)
    assert set(r["route_id"] for r in candidates) <= ROUTES
    ledger_by = {r["identity_key"]: r for r in ledger}
    diff_by = {r["identity_key"]: r for r in diff}
    for row in candidates:
        ident, route = row["identity_key"], row["route_id"]
        rec, d = ledger_by[ident], diff_by[ident]
        assert rec["browseable_before"] == "YES"
        assert not jlist(d["missing_local_refinements"])
        assert not jlist(d["current_routes_not_reproduced"])
        assert rec["route_vocabulary_gap"] != "YES"
        assert route in jlist(d["missing_core_routes"]) + jlist(d["missing_supporting_routes"])
        if route in jlist(d["missing_supporting_routes"]):
            assert rec["issue118_content_intent"] in {"SEXUAL", "CONTEXTUAL"}

    route_counts = Counter(r["route_id"] for r in candidates)
    assert route_counts == Counter({r["route_id"]: int(r["candidate_additions"]) for r in shelves})
    assert len(shelves) == len(ROUTES) == 19
    for row in shelves:
        assert int(row["current_identity_count"]) + int(row["candidate_additions"]) == int(row["after_identity_count"])
    assert sum(int(r["candidate_additions"]) for r in shelves) == len(candidates)
    assert len(upstream) == summary["pass_c_disposition_identity_counts"]["UPSTREAM_REVIEW"]
    assert len(search_only) == summary["pass_c_disposition_identity_counts"]["SEARCH_ONLY"]
    assert len(unresolved) == summary["pass_c_disposition_identity_counts"]["SEMANTIC_UNRESOLVED"]
    assert sum(int(r["candidate_additions"]) for r in family) == len(candidates)
    assert len(facets) == 8

    report = {
        "schema_version": "issue132-product-reconciliation-validation-v1",
        "status": "PASS",
        "pass_b_population": EXPECTED,
        "unique_identity_coverage": EXPECTED,
        "duplicate_identity_count": 0,
        "disposition_partition_total": EXPECTED,
        "disposition_counts": dict(sorted(dispositions.items())),
        "candidate_route_pairs": len(candidates),
        "candidate_route_pairs_unique": True,
        "candidate_browseability_and_owner_gates": "PASS",
        "existing_route_vocabulary_only": True,
        "supporting_candidate_lens_gate": "PASS",
        "route_shelf_count": len(shelves),
        "route_shelf_before_after_arithmetic": "PASS",
        "csv_parse_back": "PASS",
        "runtime_assets_created": False,
        "production_apply": False,
    }
    (out / "machine_validation_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
