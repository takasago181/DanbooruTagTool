#!/usr/bin/env python3
"""Deterministically build blind Issue #132 final-audit packets from FINAL_INPUT_HEAD."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
NEUTRAL = ROOT / "docs/issue132/parallel/input/luna_neutral_review_input_v2.csv"
INTENT = ROOT / "docs/issue118/production_candidate/sexual_intent_v2.csv"
CONTRACT = ROOT / "docs/issue132/parallel/pass_a_semantic_contract_v2.json"
AUTHORITY = ROOT / "docs/issue132/parallel/RUNTIME_AUTHORITY.json"
QA_STATE = ROOT / "docs/issue132/parallel/CODEX_QA_STATE.json"
BASELINE_MANIFEST = ROOT / "docs/issue132/parallel/codex-baseline/manifest.json"
OUT = ROOT / "docs/issue132/final-audit"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def write_jsonl(path: Path, rows: list[dict]) -> str:
    payload = "".join(canonical_json(row) + "\n" for row in rows).encode("utf-8")
    path.write_bytes(payload)
    return sha256_bytes(payload)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--final-input-head", required=True)
    args = parser.parse_args()
    head = args.final_input_head.lower()
    if not re.fullmatch(r"[0-9a-f]{40}", head):
        raise SystemExit("FINAL_INPUT_HEAD must be a 40-character lowercase commit SHA")

    authority = load_json(AUTHORITY)
    contract = load_json(CONTRACT)
    qa = load_json(QA_STATE)
    baseline_manifest = load_json(BASELINE_MANIFEST)
    neutral_rows = load_csv(NEUTRAL)
    intent_rows = load_csv(INTENT)
    if len(neutral_rows) != 31003 or len(intent_rows) != 31003:
        raise SystemExit("Expected 31,003 neutral and Issue #118 identity rows")
    if qa.get("final_internal_qa_passed") is not True:
        raise SystemExit("Canonical final internal QA is not complete")
    expected_lane_ends = authority["fixed"]["lane_lengths"]
    if any(int(qa["last_codex_qa_by_lane"][lane]) != int(expected_lane_ends[lane]) for lane in ("1", "2", "3")):
        raise SystemExit("Internal QA cursors are not at every live lane end")

    neutral_by_seq = {int(row["review_seq"]): row for row in neutral_rows}
    intent_by_key = {row["identity_key"]: row for row in intent_rows}
    if len(neutral_by_seq) != 31003 or len(intent_by_key) != 31003:
        raise SystemExit("Duplicate sequence or canonical identity in source authority")
    if set(row["identity_key"] for row in neutral_rows) != set(intent_by_key):
        raise SystemExit("Neutral input and Issue #118 authority identity sets differ")

    # Build effective current semantic rows from frozen baseline plus valid direct windows.
    effective: dict[int, tuple[dict, dict]] = {}
    repair_history: dict[int, list[str]] = defaultdict(list)
    manual_patch = load_json(ROOT / "docs/issue132/parallel/manual_audit_semantic_patches_v1.json")
    for entry in manual_patch.get("entries", []):
        seqs = [int(entry["lane_local_index"])]
        lane = int(entry["lane"])
        local = seqs[0]
        review_seq = (local - 1) * 3 + lane
        repair_history[review_seq].append("manual_audit_semantic_patch_v1")

    for lane in (1, 2, 3):
        manifest_entry = baseline_manifest["lanes"][str(lane)]
        baseline = load_json(ROOT / manifest_entry["path"])
        for row in baseline["rows"]:
            seq = int(row["review_seq"])
            effective[seq] = (row, {"lane": lane, "lane_local_index": int(row["lane_local_index"]), "surface": manifest_entry["path"], "sha256": manifest_entry["sha256"]})
            if row.get("repair_trace"):
                repair_history[seq].append("baseline_repair_trace")
        for local_index in baseline.get("repair_trace", {}):
            review_seq = (int(local_index) - 1) * 3 + lane
            if review_seq in effective:
                repair_history[review_seq].append("baseline_repair_trace")

        stage_dir = ROOT / f"docs/issue132/parallel/lane-{lane}/staging"
        for path in sorted(stage_dir.glob("window_*.json")):
            match = re.fullmatch(r"window_(\d{6})_(\d{6})\.json", path.name)
            if not match:
                continue
            start, end = map(int, match.groups())
            boundary = int(authority["fixed"]["direct_staging_effective_from_lane_local"][str(lane)])
            if end < boundary:
                continue
            if start < boundary:
                raise SystemExit(f"Direct window crosses frozen baseline: {path}")
            obj = load_json(path)
            for row in obj["rows"]:
                seq = int(row["review_seq"])
                effective[seq] = (row, {"lane": lane, "lane_local_index": int(row["lane_local_index"]), "surface": path.relative_to(ROOT).as_posix(), "sha256": sha256_file(path)})
                if row.get("repair_trace"):
                    repair_history[seq].append("direct_window_repair_trace")

    if len(effective) != 31003 or set(effective) != set(range(1, 31004)):
        raise SystemExit(f"Effective semantic coverage mismatch: {len(effective)}")

    neutral_sha = sha256_file(NEUTRAL)
    intent_sha = sha256_file(INTENT)
    contract_blob = hashlib.sha1(f"blob {CONTRACT.stat().st_size}\0".encode() + CONTRACT.read_bytes()).hexdigest()
    authority_blob = hashlib.sha1(f"blob {AUTHORITY.stat().st_size}\0".encode() + AUTHORITY.read_bytes()).hexdigest()
    qa_blob = hashlib.sha1(f"blob {QA_STATE.stat().st_size}\0".encode() + QA_STATE.read_bytes()).hexdigest()
    source_shas = {
        "neutral_input_sha256": neutral_sha,
        "issue118_content_intent_sha256": intent_sha,
        "semantic_contract_git_blob_sha": contract_blob,
        "runtime_authority_git_blob_sha": authority_blob,
        "qa_state_git_blob_sha": qa_blob,
        "baseline_manifest_sha256": sha256_file(BASELINE_MANIFEST),
        "manual_audit_semantic_patches_sha256": sha256_file(ROOT / "docs/issue132/parallel/manual_audit_semantic_patches_v1.json"),
        "build_script_sha256": sha256_file(Path(__file__)),
    }
    validator = subprocess.run(
        [sys.executable, str(ROOT / "scripts/issue132/validate_flat_pass_a.py")],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    snapshot_line = next((line for line in validator.stdout.splitlines() if line.startswith("FLAT_SNAPSHOT_JSON=")), None)
    if not snapshot_line:
        raise SystemExit("Flat validator did not emit its machine-readable snapshot")
    flat_snapshot = json.loads(snapshot_line.split("=", 1)[1])
    if not flat_snapshot.get("ready_for_final_chatgpt_audit"):
        raise SystemExit("Canonical flat validator does not authorize final audit")

    ledger: list[dict] = []
    by_key: dict[str, dict] = {}
    route_vocab = set(contract["route_ids"])
    for seq in range(1, 31004):
        neutral = neutral_by_seq[seq]
        identity = neutral["identity_key"]
        row, binding = effective[seq]
        intent = intent_by_key[identity]["sexual_intent"]
        if not intent and intent_by_key[identity].get("review_status") == "UNCLASSIFIED":
            intent = "UNCLASSIFIED"
        if intent not in {"SEXUAL", "CONTEXTUAL", "NON_SEXUAL", "UNCLASSIFIED"}:
            raise SystemExit(f"Unknown Issue #118 content intent: {intent}")
        routes = row.get("routes", [])
        if any(route.get("id") not in route_vocab for route in routes):
            raise SystemExit(f"Unknown route vocabulary at {identity}")
        record = {
            "identity_key": identity,
            "identity_sha256": row.get("identity_sha256") or sha256_bytes(identity.encode("utf-8")),
            "review_seq": seq,
            "lane": binding["lane"],
            "lane_local_index": binding["lane_local_index"],
            "source_surfaces": json.loads(neutral["source_surfaces"]),
            "discovery_mode": row["discovery_mode"],
            "core_routes": [route["id"] for route in routes if route["strength"] == "CORE"],
            "supporting_routes": [route["id"] for route in routes if route["strength"] == "SUPPORTING"],
            "local_refinements": row.get("local_refinement_ids", []),
            "body_facets": row.get("body_site_ids", []),
            "theme_facets": row.get("theme_ids", []),
            "review_depth": row["review_depth"],
            "route_vocabulary_gap": row["route_vocabulary_gap"],
            "issue118_content_intent": intent,
            "semantic_contract_id": authority["semantic_contract"]["current_policy_id"],
            "semantic_contract_git_blob_sha": authority["semantic_contract"]["git_blob_sha"],
            "source_provenance": {**source_shas, "effective_row_source": binding["surface"], "effective_row_source_sha256": binding["sha256"]},
            "prior_semantic_repair_history": sorted(set(repair_history.get(seq, []))),
        }
        ledger.append(record)
        by_key[identity] = record

    critical = [row for row in ledger if row["issue118_content_intent"] in {"SEXUAL", "CONTEXTUAL"}]
    critical.sort(key=lambda row: (sha256_bytes(row["identity_key"].encode("utf-8")), row["identity_key"]))
    midpoint = len(critical) // 2

    def blind(row: dict) -> dict:
        return {
            "identity_key": row["identity_key"],
            "source_surfaces": row["source_surfaces"],
            "issue118_content_intent": row["issue118_content_intent"],
        }

    priority_a = [blind(row) for row in critical[:midpoint]]
    priority_b = [blind(row) for row in critical[midpoint:]]
    critical_keys = {row["identity_key"] for row in critical}

    # Candidate-only family checks; patterns select rows for human semantic review and never assign labels.
    family_patterns = [
        ("licking", re.compile(r"^licking_.+")),
        ("holding", re.compile(r"^holding_.+")),
        ("naked", re.compile(r"^naked_.+")),
        ("panties", re.compile(r".+_panties$")),
        ("bra", re.compile(r".+_bra$")),
        ("cosplay", re.compile(r".+_cosplay$")),
        ("on_pussy", re.compile(r".+_on_pussy$")),
        ("on_penis", re.compile(r".+_on_penis$")),
        ("on_ass", re.compile(r".+_on_ass$")),
    ]
    signatures: dict[str, tuple] = {}
    family_members: dict[str, list[str]] = defaultdict(list)
    for key, row in by_key.items():
        signatures[key] = (tuple(row["core_routes"]), tuple(row["supporting_routes"]), tuple(row["local_refinements"]), tuple(row["body_facets"]), tuple(row["theme_facets"]))
        for label, pattern in family_patterns:
            if pattern.fullmatch(key):
                family_members[label].append(key)

    risk_reasons: dict[str, set[str]] = defaultdict(set)
    rare_counts = Counter(signatures[key] for key in by_key)
    for key, row in by_key.items():
        if key in critical_keys:
            continue
        if row["prior_semantic_repair_history"]:
            risk_reasons[key].add("prior_semantic_repair")
        if row["discovery_mode"] in {"SEARCH_ORIENTED", "SEMANTIC_UNRESOLVED"}:
            risk_reasons[key].add(row["discovery_mode"].lower())
        if rare_counts[signatures[key]] <= 3 and (row["core_routes"] or row["supporting_routes"] or row["local_refinements"]):
            risk_reasons[key].add("rare_route_refinement_combination")
        if len(row["core_routes"]) + len(row["supporting_routes"]) > 1:
            risk_reasons[key].add("multi_route")
        if row["supporting_routes"]:
            risk_reasons[key].add("supporting_route")
        if row["body_facets"]:
            risk_reasons[key].add("body_facet")
        if row["theme_facets"]:
            risk_reasons[key].add("theme_facet")
        if any(item.startswith("CLOTHING_STATE_EXPOSURE/") for item in row["local_refinements"]):
            risk_reasons[key].add("clothing_state")
        routes = set(row["core_routes"] + row["supporting_routes"])
        if len(routes & {"ACTION_CONTACT", "POSE_POSITION", "RELATION_ROLE"}) > 1:
            risk_reasons[key].add("action_pose_relation_boundary")
        if any(item in {"CLOTHING/COSTUME", "OBJECT_PROP/WEAPON"} for item in row["local_refinements"]):
            risk_reasons[key].add("named_costume_weapon_prop")
        if routes & {"TOOL_OBJECT", "SCENE_BACKGROUND"}:
            risk_reasons[key].add("object_scene_boundary")
        if routes & {"BODY_SITE", "HAIR_FACE"}:
            risk_reasons[key].add("body_feature_boundary")

    sibling_inconsistent = set()
    for label, members in family_members.items():
        ordinary = [key for key in members if key not in critical_keys]
        if len(ordinary) > 1 and len({signatures[key] for key in ordinary}) > 1:
            sibling_inconsistent.update(ordinary)
            for key in ordinary:
                risk_reasons[key].add("sibling_inconsistency_candidate:" + label)

    # Risk packet reasons are recorded in the manifest; blind rows do not disclose these current-answer-derived selectors.
    risk_keys = sorted(risk_reasons, key=lambda key: (sha256_bytes((head + "|risk|" + key).encode()), key))
    selected_control: list[str] = []
    route_candidates: dict[str, list[str]] = defaultdict(list)
    for key, row in by_key.items():
        if key in critical_keys:
            continue
        for route in row["core_routes"] + row["supporting_routes"]:
            route_candidates[route].append(key)
    control_order: dict[str, list[str]] = {}
    for route in contract["route_ids"]:
        control_order[route] = sorted(
            route_candidates[route],
            key=lambda key: (sha256_bytes((head + "|ordinary-control|" + route + "|" + key).encode()), key),
        )
    cursors = Counter()
    selected_set: set[str] = set()
    routes = list(contract["route_ids"])
    while len(selected_set) < 700:
        progressed = False
        for route in routes:
            candidates = control_order[route]
            while cursors[route] < len(candidates) and candidates[cursors[route]] in selected_set:
                cursors[route] += 1
            if cursors[route] >= len(candidates):
                continue
            key = candidates[cursors[route]]
            cursors[route] += 1
            selected_set.add(key)
            if key not in selected_control:
                selected_control.append(key)
            progressed = True
            if len(selected_set) == 700:
                break
        if not progressed:
            break
    if len(selected_set) < 600:
        raise SystemExit(f"Only {len(selected_set)} ordinary controls available; expected 600-800")
    control_routes = {route for route, candidates in control_order.items() if any(key in selected_set for key in candidates)}
    if len(control_routes) != len(contract["route_ids"]):
        missing_routes = sorted(set(contract["route_ids"]) - control_routes)
        raise SystemExit(f"Ordinary controls fail to cover all 19 route IDs; missing={missing_routes}")

    general_keys = sorted(set(risk_keys) | selected_set, key=lambda key: (sha256_bytes((head + "|general-risk|" + key).encode()), key))
    general_packet = [blind(by_key[key]) for key in general_keys]

    OUT.mkdir(parents=True, exist_ok=True)
    ledger_hash = write_jsonl(OUT / "effective_semantic_ledger.jsonl", ledger)
    a_hash = write_jsonl(OUT / "priority_a_blind.jsonl", priority_a)
    b_hash = write_jsonl(OUT / "priority_b_blind.jsonl", priority_b)
    general_hash = write_jsonl(OUT / "general_risk_blind.jsonl", general_packet)
    population = {
        "identity_total": len(ledger),
        "sexual": sum(row["issue118_content_intent"] == "SEXUAL" for row in ledger),
        "contextual": sum(row["issue118_content_intent"] == "CONTEXTUAL" for row in ledger),
        "non_sexual": sum(row["issue118_content_intent"] == "NON_SEXUAL" for row in ledger),
        "unclassified": sum(row["issue118_content_intent"] == "UNCLASSIFIED" for row in ledger),
        "purpose_critical": len(critical),
        "priority_a": len(priority_a),
        "priority_b": len(priority_b),
        "general_risk_total": len(general_packet),
        "general_risk_candidates": len(risk_keys),
        "ordinary_controls": len(selected_set),
        "ordinary_control_routes_covered": sorted(control_routes),
    }
    manifest = {
        "schema_version": "issue132-final-audit-build-manifest-v1",
        "final_input_head": head,
        "semantic_repair": "none; build-only role",
        "source_hashes": source_shas,
        "algorithm": {
            "ledger_order": "review_seq ascending",
            "critical_split": "sort by SHA256(identity_key UTF-8), then identity_key; split at floor(n/2)",
            "general_risk_candidates": "bounded attribute/family candidate rules; classification is never inferred from family patterns",
            "ordinary_controls": "round-robin deterministic hash order across current route assignments, exclude purpose-critical/risk-candidate identities, target 700 unique identities",
            "blind_packet_fields": ["identity_key", "source_surfaces", "issue118_content_intent"],
        },
        "population": population,
        "machine_validation": {
            "flat_validator_snapshot": flat_snapshot,
            "coverage": len(effective) == 31003,
            "unique_identity": len(by_key) == 31003,
            "issue118_join_exact": set(by_key) == set(intent_by_key),
            "route_vocabulary_valid": all(set(row["core_routes"] + row["supporting_routes"]) <= route_vocab for row in ledger),
            "semantic_contract_hash_valid": contract_blob == authority["semantic_contract"]["git_blob_sha"],
            "lane_binding_valid": all(row["lane"] == ((row["review_seq"] - 1) % 3) + 1 for row in ledger),
            "all_priority_blind": all(set(row) == {"identity_key", "source_surfaces", "issue118_content_intent"} for row in priority_a + priority_b),
            "all_general_blind": all(set(row) == {"identity_key", "source_surfaces", "issue118_content_intent"} for row in general_packet),
            "all_critical_in_priority": len(priority_a) + len(priority_b) == len(critical),
            "priority_disjoint": not ({row["identity_key"] for row in priority_a} & {row["identity_key"] for row in priority_b}),
            "controls_600_800": 600 <= len(selected_set) <= 800,
            "control_19_routes": len(control_routes) == 19,
            "passed": True,
        },
        "packet_sha256": {
            "effective_semantic_ledger.jsonl": ledger_hash,
            "priority_a_blind.jsonl": a_hash,
            "priority_b_blind.jsonl": b_hash,
            "general_risk_blind.jsonl": general_hash,
        },
    }
    if not all(value for key, value in manifest["machine_validation"].items() if key != "passed"):
        manifest["machine_validation"]["passed"] = False
        raise SystemExit("BUILD machine validation failed; inspect generated manifest")
    (OUT / "BUILD_MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"population": population, "packet_sha256": manifest["packet_sha256"], "machine_validation": manifest["machine_validation"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
