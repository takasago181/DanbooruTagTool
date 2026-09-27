#!/usr/bin/env python3
"""Freeze the deterministic blind General Risk audit cohort from BUILD evidence."""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BUILD_REF = "origin/audit/issue132-final-build"
BUILD_DIR = "docs/issue132/final-audit"
OUT = ROOT / BUILD_DIR
FINAL_INPUT_HEAD = "aa6c745c35f59dc22700bd77ee1f015ba593faa3"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def git_bytes(ref: str, path: str) -> bytes:
    return subprocess.run(
        ["git", "show", f"{ref}:{path}"],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
    ).stdout


def load_json(ref: str, path: str) -> dict:
    return json.loads(git_bytes(ref, path))


def load_jsonl_bytes(payload: bytes) -> list[dict]:
    return [json.loads(line) for line in payload.splitlines() if line]


def family_sibling_candidates(rows: dict[str, dict]) -> set[str]:
    # Candidate generation only. These patterns never assign semantic answers.
    patterns = [
        re.compile(r"^licking_.+"),
        re.compile(r"^holding_.+"),
        re.compile(r"^naked_.+"),
        re.compile(r".+_panties$"),
        re.compile(r".+_bra$"),
        re.compile(r".+_cosplay$"),
        re.compile(r".+_on_pussy$"),
        re.compile(r".+_on_penis$"),
        re.compile(r".+_on_ass$"),
    ]
    signatures = {
        key: (
            tuple(row["core_routes"]),
            tuple(row["supporting_routes"]),
            tuple(row["local_refinements"]),
            tuple(row["body_facets"]),
            tuple(row["theme_facets"]),
        )
        for key, row in rows.items()
    }
    members: dict[int, list[str]] = collections.defaultdict(list)
    for key in rows:
        for index, pattern in enumerate(patterns):
            if pattern.fullmatch(key):
                members[index].append(key)
    candidates: set[str] = set()
    for family_rows in members.values():
        ordinary = [
            key
            for key in family_rows
            if rows[key]["issue118_content_intent"] not in {"SEXUAL", "CONTEXTUAL"}
        ]
        if len(ordinary) > 1 and len({signatures[key] for key in ordinary}) > 1:
            candidates.update(ordinary)
    return candidates


def risk_reasons(rows: dict[str, dict]) -> dict[str, set[str]]:
    signatures = {
        key: (
            tuple(row["core_routes"]),
            tuple(row["supporting_routes"]),
            tuple(row["local_refinements"]),
            tuple(row["body_facets"]),
            tuple(row["theme_facets"]),
        )
        for key, row in rows.items()
    }
    signature_counts = collections.Counter(signatures.values())
    result: dict[str, set[str]] = collections.defaultdict(set)
    for key, row in rows.items():
        if row["issue118_content_intent"] in {"SEXUAL", "CONTEXTUAL"}:
            continue
        if row["prior_semantic_repair_history"]:
            result[key].add("prior_semantic_repair")
        if row["discovery_mode"] in {"SEARCH_ORIENTED", "SEMANTIC_UNRESOLVED"}:
            result[key].add(row["discovery_mode"].lower())
        if signature_counts[signatures[key]] <= 3 and any(signatures[key]):
            result[key].add("rare_route_refinement_combination")
        if len(row["core_routes"]) + len(row["supporting_routes"]) > 1:
            result[key].add("multi_route")
        if row["supporting_routes"]:
            result[key].add("supporting_route")
        if row["body_facets"]:
            result[key].add("body_facet")
        if row["theme_facets"]:
            result[key].add("theme_facet")
        if any(item.startswith("CLOTHING_STATE_EXPOSURE/") for item in row["local_refinements"]):
            result[key].add("clothing_state")
        route_set = set(row["core_routes"] + row["supporting_routes"])
        if len(route_set & {"ACTION_CONTACT", "POSE_POSITION", "RELATION_ROLE"}) > 1:
            result[key].add("action_pose_relation_boundary")
        if any(item in {"CLOTHING/COSTUME", "OBJECT_PROP/WEAPON"} for item in row["local_refinements"]):
            result[key].add("named_costume_weapon_prop")
        if route_set & {"TOOL_OBJECT", "SCENE_BACKGROUND"}:
            result[key].add("object_scene_boundary")
        if route_set & {"BODY_SITE", "HAIR_FACE"}:
            result[key].add("body_feature_boundary")
    for key in family_sibling_candidates(rows):
        result[key].add("sibling_inconsistency_candidate")
    return result


def select_controls(rows: dict[str, dict], route_ids: list[str], head: str) -> set[str]:
    route_candidates: dict[str, list[str]] = collections.defaultdict(list)
    for key, row in rows.items():
        if row["issue118_content_intent"] in {"SEXUAL", "CONTEXTUAL"}:
            continue
        for route_id in row["core_routes"] + row["supporting_routes"]:
            route_candidates[route_id].append(key)
    ordered = {
        route_id: sorted(
            route_candidates[route_id],
            key=lambda key: (sha256(f"{head}|ordinary-control|{route_id}|{key}".encode()), key),
        )
        for route_id in route_ids
    }
    cursor = collections.Counter()
    selected: set[str] = set()
    while len(selected) < 700:
        progressed = False
        for route_id in route_ids:
            candidates = ordered[route_id]
            while cursor[route_id] < len(candidates) and candidates[cursor[route_id]] in selected:
                cursor[route_id] += 1
            if cursor[route_id] >= len(candidates):
                continue
            selected.add(candidates[cursor[route_id]])
            cursor[route_id] += 1
            progressed = True
            if len(selected) == 700:
                break
        if not progressed:
            break
    if len(selected) != 700:
        raise SystemExit(f"Expected exactly 700 BUILD ordinary controls, got {len(selected)}")
    covered = {
        route_id
        for route_id in route_ids
        if any(key in selected for key in ordered[route_id])
    }
    if covered != set(route_ids):
        raise SystemExit(f"BUILD control route coverage mismatch: {sorted(set(route_ids) - covered)}")
    return selected


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--expected-total", type=int, default=5344)
    args = parser.parse_args()

    build_manifest_bytes = git_bytes(BUILD_REF, f"{BUILD_DIR}/BUILD_MANIFEST.json")
    build_manifest = json.loads(build_manifest_bytes)
    if build_manifest.get("final_input_head") != FINAL_INPUT_HEAD:
        raise SystemExit("BUILD FINAL_INPUT_HEAD does not match this audit role")
    if subprocess.run(
        ["git", "cat-file", "-e", f"{FINAL_INPUT_HEAD}^{{commit}}"], cwd=ROOT
    ).returncode:
        raise SystemExit("FINAL_INPUT_HEAD is not present in the local Git object database")

    ledger_bytes = git_bytes(BUILD_REF, f"{BUILD_DIR}/effective_semantic_ledger.jsonl")
    build_packet_bytes = git_bytes(BUILD_REF, f"{BUILD_DIR}/general_risk_blind.jsonl")
    ledger_hash = sha256(ledger_bytes)
    packet_hash = sha256(build_packet_bytes)
    expected_hashes = build_manifest["packet_sha256"]
    if ledger_hash != expected_hashes["effective_semantic_ledger.jsonl"]:
        raise SystemExit("BUILD effective ledger hash mismatch")
    if packet_hash != expected_hashes["general_risk_blind.jsonl"]:
        raise SystemExit("BUILD blind packet hash mismatch")

    ledger = load_jsonl_bytes(ledger_bytes)
    build_packet = load_jsonl_bytes(build_packet_bytes)
    by_key = {row["identity_key"]: row for row in ledger}
    if len(ledger) != 31003 or len(by_key) != 31003:
        raise SystemExit("BUILD ledger population/uniqueness mismatch")
    if len(build_packet) != 16176 or len({row["identity_key"] for row in build_packet}) != 16176:
        raise SystemExit("BUILD General Risk packet population/uniqueness mismatch")

    contract = load_json(BUILD_REF, "docs/issue132/parallel/pass_a_semantic_contract_v2.json")
    route_ids = contract["route_ids"]
    reasons = risk_reasons(by_key)
    build_risk_candidates = {
        key for key, row_reasons in reasons.items() if row_reasons and by_key[key]["issue118_content_intent"] not in {"SEXUAL", "CONTEXTUAL"}
    }
    if len(build_risk_candidates) != build_manifest["population"]["general_risk_candidates"]:
        raise SystemExit("Reconstructed BUILD risk candidates do not match manifest")

    universe = {row["identity_key"] for row in build_packet}
    signatures = {
        key: (
            tuple(row["core_routes"]),
            tuple(row["supporting_routes"]),
            tuple(row["local_refinements"]),
            tuple(row["body_facets"]),
            tuple(row["theme_facets"]),
        )
        for key, row in by_key.items()
    }
    signature_counts = collections.Counter(signatures.values())
    mandatory = {
        key
        for key in universe
        if by_key[key]["discovery_mode"] == "SEMANTIC_UNRESOLVED"
        or by_key[key]["route_vocabulary_gap"] == "YES"
        or bool(by_key[key]["prior_semantic_repair_history"])
        or "sibling_inconsistency_candidate" in reasons.get(key, set())
        or (signature_counts[signatures[key]] <= 3 and any(signatures[key]))
        or len(reasons.get(key, set())) >= 2
    }
    controls = select_controls(by_key, route_ids, FINAL_INPUT_HEAD)
    selected = mandatory | controls
    if len(mandatory) != 4825:
        raise SystemExit(f"Mandatory cohort count drift: expected 4825, got {len(mandatory)}")
    if len(selected) != args.expected_total:
        raise SystemExit(f"Reduced packet count drift: expected {args.expected_total}, got {len(selected)}")
    if len(selected - universe):
        raise SystemExit("Reducer selected an identity absent from the BUILD General Risk packet")

    blind_by_key = {row["identity_key"]: row for row in build_packet}
    ordered_keys = sorted(selected, key=lambda key: (sha256(f"{FINAL_INPUT_HEAD}|final-general-risk|{key}".encode()), key))
    reduced_packet = [blind_by_key[key] for key in ordered_keys]
    if any(set(row) != {"identity_key", "source_surfaces", "issue118_content_intent"} for row in reduced_packet):
        raise SystemExit("Reduced packet contains non-blind fields")
    if len({row["identity_key"] for row in reduced_packet}) != args.expected_total:
        raise SystemExit("Reduced packet identity uniqueness check failed")

    OUT.mkdir(parents=True, exist_ok=True)
    packet_bytes = ("".join(canonical_json(row) + "\n" for row in reduced_packet)).encode("utf-8")
    packet_path = OUT / "general_risk_reduced_blind.jsonl"
    packet_path.write_bytes(packet_bytes)
    manifest = {
        "schema_version": "issue132-final-general-risk-reducer-v1",
        "role": "FINAL-AUDIT-GENERAL-RISK",
        "final_input_head": FINAL_INPUT_HEAD,
        "build_ref": BUILD_REF,
        "build_ref_head": subprocess.check_output(["git", "rev-parse", BUILD_REF], cwd=ROOT, text=True).strip(),
        "build_manifest_sha256": sha256(build_manifest_bytes),
        "build_ledger_sha256": ledger_hash,
        "build_general_risk_packet_sha256": packet_hash,
        "reducer_sha256": sha256(Path(__file__).read_bytes()),
        "reduced_packet_sha256": sha256(packet_bytes),
        "reduced_packet_path": f"{BUILD_DIR}/general_risk_reduced_blind.jsonl",
        "population": {
            "build_general_risk_candidates": len(build_risk_candidates),
            "mandatory": len(mandatory),
            "build_ordinary_controls": len(controls),
            "mandatory_control_overlap": len(mandatory & controls),
            "reduced_unique_total": len(selected),
            "additional_fill_or_hash_sample": 0,
        },
        "selection": {
            "mandatory_cohorts": [
                "SEMANTIC_UNRESOLVED",
                "route_vocabulary_gap=YES",
                "prior_semantic_repair_history",
                "BUILD family sibling inconsistency candidates",
                "route/refinement/facet signature occurring <=3 times",
                "two or more BUILD high-risk reasons",
            ],
            "controls": "Reconstruct the exact BUILD 700-item round-robin deterministic control cohort across all 19 routes.",
            "deduplication": "identity_key set union; controls overlapping mandatory are counted once",
            "ordering": "SHA256(FINAL_INPUT_HEAD + '|final-general-risk|' + identity_key), then identity_key",
            "family_patterns_select_candidates_only": True,
            "semantic_verdicts_derived_by_reducer": False,
        },
        "blind_packet_fields": ["identity_key", "source_surfaces", "issue118_content_intent"],
        "validation": {
            "build_source_hashes_match_manifest": True,
            "mandatory_count_exact": True,
            "control_count_exact": True,
            "all_19_control_routes_covered": True,
            "unique_reduced_identity_count_exact": True,
            "only_blind_packet_fields": True,
            "passed": True,
        },
    }
    (OUT / "GENERAL_RISK_REDUCER_MANIFEST.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest["population"] | {"reduced_packet_sha256": manifest["reduced_packet_sha256"]}, indent=2))


if __name__ == "__main__":
    main()
