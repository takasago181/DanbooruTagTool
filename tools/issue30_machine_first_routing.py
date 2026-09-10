"""Shared provenance and image/pair routing rules for Issue #30 Batch 2."""
from __future__ import annotations

import gzip
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


def expected_evaluator_artifacts(run_root: Path, image_id: str) -> dict[str, Path]:
    return {
        "wd14": run_root / "raw/wd14" / f"{image_id}.json",
        "kagami": run_root / "raw/kagami" / f"{image_id}.json.gz",
        "cl_v2_00": run_root / "raw/cl v2.00" / f"{image_id}.json.gz",
    }


def _read_artifact(path: Path) -> tuple[bool, str]:
    if not path.is_file():
        return False, "MISSING"
    try:
        with gzip.open(path, "rt", encoding="utf-8") if path.suffix == ".gz" else path.open(encoding="utf-8") as stream:
            value = json.load(stream)
    except Exception as exc:
        return False, f"UNREADABLE:{type(exc).__name__}"
    if isinstance(value, dict) and "error" in value:
        return False, "ERROR_OBJECT"
    return True, "OK"


def verify_row_provenance(run_root: Path, row: dict[str, Any]) -> dict[str, Any]:
    expected = expected_evaluator_artifacts(run_root, row["image_id"])
    checks = {}
    for name, path in expected.items():
        reported = row["evaluators"][name].get("raw_output_artifact")
        readable, state = _read_artifact(path)
        checks[name] = {
            "expected": str(path),
            "reported": reported,
            "reported_matches_expected": str(Path(reported)) == str(path),
            "artifact_state": state,
            "readable_non_error": readable,
        }
    return {"pass": all(item["reported_matches_expected"] and item["readable_non_error"] for item in checks.values()), "evaluators": checks}


def route_image(row: dict[str, Any], provenance_pass: bool) -> tuple[str, list[str]]:
    if not provenance_pass:
        return "BLOCKED", ["provenance/evaluator artifact gate failed"]
    classes = set(row.get("screening", {}).get("screening_classes", []))
    evaluators = row.get("evaluators", {})
    if any(value.get("execution_state") != "OK" for value in evaluators.values()):
        return "BLOCKED", ["evaluator execution failed"]
    if row.get("screening", {}).get("desk_relation_sensitive") or row.get("case", {}).get("relation_binding_required", "false").casefold() == "true":
        return "HUMAN_REVIEW_REQUIRED", ["relation/binding protected"]
    protected = {
        "RELATION_OR_BINDING", "LOW_CONFIDENCE", "DISAGREEMENT", "COMPONENT_ONLY",
    }
    reasons = [f"screening class: {value}" for value in sorted(classes & protected)]
    if reasons or not row.get("screening", {}).get("high_confidence_eligible", False):
        return "HUMAN_REVIEW_REQUIRED", reasons or ["narrow machine-handled eligibility not met"]
    return "MACHINE_HANDLED_CANDIDATE", ["direct/non-relation/simple-unary and calibrated confidence gate passed"]


def pair_routes(records: list[dict[str, Any]]) -> dict[tuple[str, int], dict[str, Any]]:
    grouped: dict[tuple[str, int], list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        grouped[(record["case_id"], int(record["generation"]["seed"]))].append(record)
    output = {}
    for key, rows in grouped.items():
        conditions = {row["cell_type"]: row for row in rows}
        routes = [row["machine_route"] for row in rows]
        if len(rows) != 2 or len({row.get("condition") for row in rows}) != 2:
            route = "BLOCKED_PAIR"
            reasons = ["A/B marker mismatch or incomplete pair"]
        elif "BLOCKED" in routes:
            route = "BLOCKED_PAIR"
            reasons = ["one image blocked"]
        elif all(value == "MACHINE_HANDLED_CANDIDATE" for value in routes):
            route = "MACHINE_HANDLED_PAIR"
            reasons = ["both A and B passed narrow machine route"]
        else:
            route = "HUMAN_REVIEW_REQUIRED_PAIR"
            reasons = ["at least one image requires human semantic judgment"]
        output[key] = {"case_id": key[0], "seed": key[1], "route": route, "image_routes": routes, "reasons": reasons}
    return output


def marker_integrity(records: list[dict[str, Any]]) -> tuple[bool, list[str]]:
    grouped: dict[tuple[str, int], list[dict[str, Any]]] = defaultdict(list)
    for row in records:
        grouped[(row["case_id"], int(row["generation"]["seed"]))].append(row)
    errors = []
    for key, rows in grouped.items():
        if len(rows) != 2 or {row.get("condition") for row in rows} != {"A", "B"}:
            errors.append(f"{key}: expected exactly one A and one B")
    return not errors, errors
