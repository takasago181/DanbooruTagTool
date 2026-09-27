#!/usr/bin/env python3
"""Apply and exactly verify the Issue #132 final semantic repair ledger.

This mutates only the frozen effective baseline rows and validator-read direct
staging rows named by FINAL_SEMANTIC_REPAIRS_V2.jsonl. Historical checkpoints and
forensic repair artifacts are never loaded as write targets.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

from codex_runtime import (
    direct_start,
    load_baseline_lane,
    load_baseline_manifest,
    load_runtime,
    read_csv,
)
from codex_semantic import validate_compact_row

ROOT = Path(__file__).resolve().parents[2]
ARTIFACT = ROOT / "docs/issue132/final-audit/FINAL_SEMANTIC_REPAIRS_V2.jsonl"
RECONCILIATION = ROOT / "docs/issue132/final-audit/FINAL_RECONCILIATION.jsonl"
QA_PATH = ROOT / "docs/issue132/parallel/CODEX_QA_STATE.json"
MANIFEST = ROOT / "docs/issue132/parallel/codex-baseline/manifest.json"
VALIDATOR = ROOT / "scripts/issue132/validate_flat_pass_a.py"
EXPECTED_COUNT = 683
EXPECTED_INPUT_HEAD = "10ff0986444528e58a8ccec7c44d539235d17175"
EXPECTED_ARTIFACT_SHA256 = "8f41759e4d34f6a527b5ce776bd8d10de983d124d1da544417ca402fe4b0549a"
EXPECTED_RECONCILIATION_SHA256 = "79e8c57b70dc34aafa7358afc6bd1883b34bfa25ec48039f5f91ca26e580698a"
SEMANTIC_FIELDS = (
    "discovery_mode", "core_routes", "supporting_routes", "local_refinements",
    "body_facets", "theme_facets", "route_vocabulary_gap",
)
CHANGE_FIELDS = set(SEMANTIC_FIELDS)
WINDOW_RE = re.compile(r"^window_(\d{6})_(\d{6})\.json$")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, obj: dict, *, indent: int | None = None) -> None:
    path.write_text(
        json.dumps(obj, ensure_ascii=False, separators=None if indent else (",", ":"), indent=indent) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def load_repairs() -> list[dict]:
    if digest(ARTIFACT) != EXPECTED_ARTIFACT_SHA256:
        raise ValueError("repair artifact SHA-256 differs from finalizer manifest")
    if digest(RECONCILIATION) != EXPECTED_RECONCILIATION_SHA256:
        raise ValueError("reconciliation SHA-256 differs from finalizer manifest")
    lines = ARTIFACT.read_text(encoding="utf-8").splitlines()
    rows = [json.loads(line) for line in lines if line.strip()]
    keys = [r.get("identity_key") for r in rows]
    if len(rows) != EXPECTED_COUNT or len(set(keys)) != EXPECTED_COUNT:
        raise ValueError(f"expected {EXPECTED_COUNT} unique repairs; got {len(rows)} rows / {len(set(keys))} keys")
    for row in rows:
        if row.get("schema_version") != "issue132-final-semantic-repair-v2":
            raise ValueError(f"schema mismatch: {row.get('identity_key')}")
        if row.get("fixed_input_head") != EXPECTED_INPUT_HEAD:
            raise ValueError(f"fixed input mismatch: {row.get('identity_key')}")
        if not row.get("review_reason") or row.get("worker_role") not in {"RECONCILE-0", "RECONCILE-1", "RECONCILE-2", "RECONCILE-3"}:
            raise ValueError(f"provenance invalid: {row.get('identity_key')}")
        changes = row.get("changes")
        if not isinstance(changes, dict) or not changes or set(changes) - CHANGE_FIELDS:
            raise ValueError(f"change field-set invalid: {row.get('identity_key')}")
        for field, pair in changes.items():
            if not isinstance(pair, dict) or set(pair) != {"before", "after"}:
                raise ValueError(f"before/after schema invalid: {row['identity_key']} {field}")
            if isinstance(pair["before"], list) != isinstance(pair["after"], list):
                raise ValueError(f"before/after type differs: {row['identity_key']} {field}")
    return rows


def route_parts(row: dict, strength: str) -> list[str]:
    return [r["id"] for r in row["routes"] if r["strength"] == strength]


def value(row: dict, field: str):
    if field == "core_routes":
        return route_parts(row, "CORE")
    if field == "supporting_routes":
        return route_parts(row, "SUPPORTING")
    source_field = {
        "local_refinements": "local_refinement_ids",
        "body_facets": "body_site_ids",
        "theme_facets": "theme_ids",
    }.get(field, field)
    return row[source_field]


def normalized(field: str, item):
    return sorted(item) if isinstance(item, list) else item


def semantic_projection(row: dict) -> dict:
    return {field: normalized(field, value(row, field)) for field in SEMANTIC_FIELDS}


def load_effective(authority: dict, neutral: list[dict], manifest: dict):
    rows: dict[str, dict] = {}
    locs: dict[str, tuple[Path, int, int, bool]] = {}
    lanes = {}
    for lane in (1, 2, 3):
        assigned = [r for r in neutral if ((int(r["review_seq"]) - 1) % 3) + 1 == lane]
        lanes[lane] = assigned
        baseline_path = ROOT / manifest["lanes"][str(lane)]["path"]
        baseline = load_baseline_lane(ROOT, manifest, lane)
        for row in baseline.get("rows", []):
            idx = int(row["lane_local_index"])
            key = assigned[idx - 1]["identity_key"]
            rows[key] = row
            locs[key] = (baseline_path, idx, lane, True)
        stage_dir = ROOT / f"docs/issue132/parallel/lane-{lane}/staging"
        boundary = direct_start(authority, lane)
        for path in stage_dir.glob("window_*.json"):
            match = WINDOW_RE.match(path.name)
            if not match or int(match.group(1)) < boundary:
                continue
            obj = json.loads(path.read_text(encoding="utf-8"))
            for row in obj.get("rows", []):
                idx = int(row["lane_local_index"])
                key = assigned[idx - 1]["identity_key"]
                if key in rows:
                    raise ValueError(f"duplicate effective source identity {key}")
                rows[key] = row
                locs[key] = (path, idx, lane, False)
    return rows, locs, lanes


def normalized_source_matches(row: dict, field: str, expected) -> bool:
    return normalized(field, value(row, field)) == normalized(field, expected)


def validate_artifact(rows: list[dict], sources: dict, locs: dict, neutral_by_key: dict, contract: dict):
    missing, conflicts, representation_differences = [], [], []
    for repair in rows:
        key = repair["identity_key"]
        current = sources.get(key)
        if current is None or key not in neutral_by_key:
            missing.append(key)
            continue
        for field, pair in repair["changes"].items():
            actual = value(current, field)
            if actual != pair["before"]:
                if normalized(field, actual) == normalized(field, pair["before"]):
                    representation_differences.append({"identity_key": key, "field": field, "source": str(locs[key][0].relative_to(ROOT))})
                else:
                    conflicts.append({"identity_key": key, "field": field, "expected_before": pair["before"], "actual": actual, "source": str(locs[key][0].relative_to(ROOT))})
    if missing or conflicts:
        raise ValueError(json.dumps({"missing": missing[:20], "semantic_conflicts": conflicts[:20]}, ensure_ascii=False))

    route_vocab = set(contract["route_ids"])
    ref_vocab = set(contract["local_refinement_parent"])
    body_vocab = set(contract["body_site_ids"])
    theme_vocab = set(contract["theme_ids"])
    for repair in rows:
        for field, pair in repair["changes"].items():
            after = pair["after"]
            if field == "discovery_mode" and after not in contract["allowed_discovery_modes"]:
                raise ValueError(f"invalid discovery mode: {repair['identity_key']} {after}")
            vocab = {"core_routes": route_vocab, "supporting_routes": route_vocab, "local_refinements": ref_vocab, "body_facets": body_vocab, "theme_facets": theme_vocab}.get(field)
            if vocab is not None and (not isinstance(after, list) or len(after) != len(set(after)) or not set(after) <= vocab):
                raise ValueError(f"invalid frozen vocabulary: {repair['identity_key']} {field}={after}")
            if field == "route_vocabulary_gap" and after not in {"YES", "NO"}:
                raise ValueError(f"invalid route/refinement gap value: {repair['identity_key']} {after}")

    return {"matched": len(rows), "semantic_mismatches": 0, "representation_only_differences": representation_differences, "source_counts": {"baseline": sum(locs[r["identity_key"]][3] for r in rows), "direct_staging": sum(not locs[r["identity_key"]][3] for r in rows)}}


def apply_one(row: dict, repair: dict) -> None:
    changes = repair["changes"]
    core = changes.get("core_routes", {}).get("after")
    supporting = changes.get("supporting_routes", {}).get("after")
    if core is not None or supporting is not None:
        rewritten = []
        if core is not None:
            rewritten.extend({"id": route, "strength": "CORE"} for route in core)
        else:
            rewritten.extend(r for r in row["routes"] if r["strength"] == "CORE")
        if supporting is not None:
            rewritten.extend({"id": route, "strength": "SUPPORTING"} for route in supporting)
        else:
            rewritten.extend(r for r in row["routes"] if r["strength"] == "SUPPORTING")
        row["routes"] = rewritten
    for field, pair in changes.items():
        if field in {"core_routes", "supporting_routes"}:
            continue
        target = {"local_refinements": "local_refinement_ids", "body_facets": "body_site_ids", "theme_facets": "theme_ids"}.get(field, field)
        row[target] = pair["after"]


def validator_snapshot() -> dict:
    proc = subprocess.run([sys.executable, str(VALIDATOR)], cwd=ROOT, capture_output=True, text=True)
    if proc.returncode:
        raise RuntimeError(f"validator failed ({proc.returncode}):\n{proc.stdout}\n{proc.stderr}")
    marker = "FLAT_SNAPSHOT_JSON="
    line = next((line for line in proc.stdout.splitlines() if line.startswith(marker)), None)
    if line is None:
        raise RuntimeError(f"validator omitted {marker}:\n{proc.stdout}")
    return json.loads(line[len(marker):])


def assert_structural(snapshot: dict) -> None:
    required = {"processed_slot_total": 31003, "accepted_total": 31003, "remaining_unprocessed_total": 0, "baseline_hold_count": 0,
                "baseline_semantic_lint_count": 0, "forward_hold_count": 0, "invalid_window_count": 0,
                "duplicate_coverage_count": 0, "internal_qa_limit_violation_count": 0, "fatal_contract_error_count": 0}
    bad = {k: (snapshot.get(k), v) for k, v in required.items() if snapshot.get(k) != v}
    if bad:
        raise RuntimeError(f"structural validator counts not clean: {bad}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--preflight-only", action="store_true")
    ap.add_argument("--batch-size", type=int, default=50)
    args = ap.parse_args()
    if args.apply == args.preflight_only:
        raise SystemExit("Choose exactly one of --preflight-only or --apply.")
    repairs = load_repairs()
    authority, contract, _, errors = load_runtime(ROOT)
    if errors:
        raise ValueError(f"runtime authority errors: {errors}")
    manifest = load_baseline_manifest(ROOT, authority)
    neutral = read_csv(ROOT / authority["fixed"]["neutral_path"])
    neutral_by_key = {r["identity_key"]: r for r in neutral}
    sources, locations, lanes = load_effective(authority, neutral, manifest)
    before_report = validate_artifact(repairs, sources, locations, neutral_by_key, contract)
    before_projection = {key: semantic_projection(row) for key, row in sources.items()}

    reconciliation = [json.loads(line) for line in RECONCILIATION.read_text(encoding="utf-8").splitlines() if line.strip()]
    decisions = {r["identity_key"]: r for r in reconciliation}
    if len(reconciliation) != 7285 or len(decisions) != 7285:
        raise ValueError(f"reconciliation must contain 7,285 unique identities, got {len(reconciliation)} / {len(decisions)}")
    repair_keys = {r["identity_key"] for r in repairs}
    retained = {r["identity_key"] for r in repairs if r.get("reconciliation_review", {}).get("decision_class") == "current_retained"}
    reviewed = {r["identity_key"] for r in repairs if r.get("reconciliation_review")}
    if len(reviewed) != 20 or len(retained) != 1 or retained != {"pelvic_curtain"}:
        raise ValueError(f"V2 review coverage/classification invalid reviewed={len(reviewed)} retained={sorted(retained)}")
    wrong_repair = [k for k in repair_keys-retained if decisions.get(k, {}).get("finalizer_action") != "REPAIR_CURRENT_DEFECT" or decisions[k].get("repair_id") != k]
    wrong_retained = [k for k in retained if decisions.get(k, {}).get("finalizer_action") != "RETAIN_CURRENT" or decisions[k].get("repair_id") is not None]
    repair_actions = {k for k, d in decisions.items() if d.get("finalizer_action") == "REPAIR_CURRENT_DEFECT"}
    if wrong_repair or wrong_retained or repair_actions != repair_keys-retained:
        raise ValueError(f"repair/reconciliation decision mismatch repair={wrong_repair[:10]} retained={wrong_retained[:10]} actions_only={sorted(repair_actions-(repair_keys-retained))[:10]}")

    contract_conflicts = []
    for repair in repairs:
        key = repair["identity_key"]
        path, idx, lane, _ = locations[key]
        candidate = copy.deepcopy(sources[key])
        apply_one(candidate, repair)
        row_errors = validate_compact_row(candidate, lanes[lane][idx - 1], idx, contract)
        if row_errors:
            contract_conflicts.append({
                "identity_key": key,
                "lane": lane,
                "lane_local_index": idx,
                "source": str(path.relative_to(ROOT)),
                "changed_fields": list(repair["changes"]),
                "validator_errors": row_errors,
                "artifact_after": {field: pair["after"] for field, pair in repair["changes"].items()},
            })
    if contract_conflicts:
        blocker = {
            "schema_version": "issue132-final-semantic-application-blocker-v1",
            "pre_repair_finalizer_head": "c1014b31cbfc22004b43e7788ca742a0868d2825",
            "repair_artifact_sha256": digest(ARTIFACT),
            "expected_repairs": EXPECTED_COUNT,
            "before_state": before_report,
            "before_semantic_conflicts": 0,
            "post_change_frozen_contract_conflicts": len(contract_conflicts),
            "conflicts": contract_conflicts,
            "reconciliation": {"identities": len(reconciliation), "repair_decisions": len(repair_actions), "retained_current": len(retained), "unresolved_p0": 0, "unresolved_p1": 0},
            "applied": 0,
            "canonical_push": False,
            "reason": "Artifact after-state conflicts with frozen Pass-A row validation. Applying companion changes to unspecified fields would violate the user's preserve-unchanged-fields requirement.",
        }
        write_json(ROOT / "docs/issue132/final-audit/FINAL_APPLY_BLOCKER.json", blocker, indent=2)
        raise SystemExit(f"BLOCKED: {len(contract_conflicts)} final repair after-states violate the frozen semantic contract; see docs/issue132/final-audit/FINAL_APPLY_BLOCKER.json")

    if args.preflight_only:
        print(json.dumps({"preflight": "PASS", "repair_expected": len(repairs), "before_state": before_report,
                          "frozen_contract_conflicts": 0, "reviewed_blockers": len(reviewed),
                          "repair_revised": sum(r.get("reconciliation_review", {}).get("decision_class") == "repair_revised" for r in repairs),
                          "current_retained": len(retained), "reconciliation_identities": len(reconciliation),
                          "repair_decisions": len(repair_actions), "source_files": len({str(locations[r["identity_key"]][0].relative_to(ROOT)) for r in repairs})}, ensure_ascii=False))
        return

    qa = json.loads(QA_PATH.read_text(encoding="utf-8"))
    qa["status"] = "FINAL_SEMANTIC_QA_PENDING_APPLICATION"
    qa["final_chatgpt_semantic_qa_passed"] = False
    qa.pop("final_chatgpt_semantic_qa_evidence", None)
    write_json(QA_PATH, qa, indent=2)

    total_applied = 0
    for start in range(0, len(repairs), args.batch_size):
        batch = repairs[start:start + args.batch_size]
        loaded: dict[Path, dict] = {}
        baseline_touched = False
        for repair in batch:
            path, idx, lane, is_baseline = locations[repair["identity_key"]]
            if path not in loaded:
                loaded[path] = json.loads(path.read_text(encoding="utf-8"))
            obj = loaded[path]
            candidates = obj.get("rows", []) if is_baseline else obj.get("rows", [])
            target = next((r for r in candidates if int(r["lane_local_index"]) == idx), None)
            if target is None:
                raise ValueError(f"source row missing during write: {repair['identity_key']} {path}")
            apply_one(target, repair)
            baseline_touched |= is_baseline
        for path, obj in loaded.items():
            write_json(path, obj)
        if baseline_touched:
            for lane, entry in manifest["lanes"].items():
                lane_path = ROOT / entry["path"]
                if lane_path in loaded:
                    entry["sha256"] = digest(lane_path)
            write_json(MANIFEST, manifest, indent=2)
        total_applied += len(batch)
        snapshot = validator_snapshot()
        assert_structural(snapshot)
        print(json.dumps({"batch": start // args.batch_size + 1, "applied_cumulative": total_applied, "validator": "PASS", "population": snapshot["expected_total"], "accepted": snapshot["accepted_total"]}, ensure_ascii=False))

    final_manifest = load_baseline_manifest(ROOT, authority)
    after_sources, after_locations, _ = load_effective(authority, neutral, final_manifest)
    repair_by_key = {r["identity_key"]: r for r in repairs}
    after_mismatches = []
    unexpected = []
    for repair in repairs:
        row = after_sources[repair["identity_key"]]
        for field, pair in repair["changes"].items():
            if not normalized_source_matches(row, field, pair["after"]):
                after_mismatches.append({"identity_key": repair["identity_key"], "field": field, "expected": pair["after"], "actual": value(row, field)})
    for key, before in before_projection.items():
        after = semantic_projection(after_sources[key])
        allowed = {f for f in repair_by_key.get(key, {}).get("changes", {})}
        for field in SEMANTIC_FIELDS:
            if before[field] != after[field]:
                repair = repair_by_key.get(key)
                expected = normalized(field, repair["changes"][field]["after"]) if repair and field in repair["changes"] else None
                if field not in allowed or after[field] != expected:
                    unexpected.append({"identity_key": key, "field": field, "before": before[field], "after": after[field]})
    if after_mismatches or unexpected:
        raise RuntimeError(json.dumps({"after_state_mismatches": after_mismatches[:20], "unexpected_semantic_changes": unexpected[:20]}, ensure_ascii=False))

    final_snapshot = validator_snapshot()
    assert_structural(final_snapshot)
    report = {
        "schema_version": "issue132-final-semantic-application-report-v1",
        "pre_repair_finalizer_head": "c1014b31cbfc22004b43e7788ca742a0868d2825",
        "repair_artifact": "docs/issue132/final-audit/FINAL_SEMANTIC_REPAIRS_V2.jsonl",
        "repair_artifact_sha256": digest(ARTIFACT),
        "repair_expected": EXPECTED_COUNT,
        "applied": total_applied,
        "reviewed_blockers": {"resolved": len(reviewed), "repair_revised": sum(r.get("reconciliation_review", {}).get("decision_class") == "repair_revised" for r in repairs), "current_retained": len(retained)},
        "before_state": before_report,
        "before_semantic_conflicts": 0,
        "after_state_mismatches": 0,
        "unexpected_semantic_changes": 0,
        "source_file_counts": {"modified_semantic_source_files": len({str(locations[r["identity_key"]][0].relative_to(ROOT)) for r in repairs}), "baseline_files": len({str(locations[r["identity_key"]][0].relative_to(ROOT)) for r in repairs if locations[r["identity_key"]][3]}), "direct_staging_files": len({str(locations[r["identity_key"]][0].relative_to(ROOT)) for r in repairs if not locations[r["identity_key"]][3]})},
        "repair_identity_source_counts": before_report["source_counts"],
        "reconciliation": {"identities": len(reconciliation), "repair_decisions": len(repair_actions), "retained_current": len(retained), "unresolved_p0": 0, "unresolved_p1": 0, "contradictory_repairs": 0},
        "full_structural_validator": {"status": "PASS", "population": final_snapshot["expected_total"], "accepted": final_snapshot["accepted_total"], "remaining": final_snapshot["remaining_unprocessed_total"], "hold": final_snapshot.get("baseline_hold_count", 0) + final_snapshot.get("forward_hold_count", 0), "semantic_lint": final_snapshot.get("baseline_semantic_lint_count", 0), "invalid_windows": final_snapshot.get("invalid_window_count", 0), "duplicates": final_snapshot.get("duplicate_coverage_count", 0), "qa_violations": final_snapshot.get("internal_qa_limit_violation_count", 0), "fatal_contract_errors": final_snapshot.get("fatal_contract_error_count", 0)},
        "final_semantic_qa_status": "PENDING_QA_EVIDENCE_COMMIT",
    }
    write_json(ROOT / "docs/issue132/final-audit/FINAL_APPLY_REPORT.json", report, indent=2)
    print(json.dumps({"complete": True, "report": "docs/issue132/final-audit/FINAL_APPLY_REPORT.json", "applied": total_applied, "after_mismatches": 0, "unexpected_changes": 0, "population": final_snapshot["expected_total"], "accepted": final_snapshot["accepted_total"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
