#!/usr/bin/env python3
"""Analyze the frozen Issue #30 pilot for the Phase 2 coverage checkpoint.

The input is the local-only Phase 1 run root.  This tool never generates
images, invokes an evaluator, or writes under ``data/**``.  It emits a
repository-readable structural coverage report while keeping artifact paths
and raw evaluator files local-only.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from PIL import Image, ImageStat


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CASE_MANIFEST = ROOT / "docs/testing/ISSUE30_REAL_IMAGE_CALIBRATION_CASES_20260910.csv"
DEFAULT_REVIEW_RESULTS = ROOT / "docs/testing/ISSUE30_MINIMAL_REVIEW_RESULTS_20260910.json"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_cases(path: Path) -> dict[str, dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    if not rows:
        raise ValueError(f"case manifest is empty: {path}")
    cases = {row["case_id"]: row for row in rows}
    if len(cases) != len(rows):
        raise ValueError("case manifest contains duplicate case_id values")
    return cases


def load_results(run_root: Path) -> list[dict[str, Any]]:
    path = run_root / "calibration_results.json"
    rows = read_json(path)
    if not isinstance(rows, list) or not rows:
        raise ValueError(f"calibration result must be a non-empty list: {path}")
    return rows


def structural_class(case: dict[str, str]) -> str:
    """Map the frozen desk strata to the Phase 2 capability vocabulary."""
    canonical = case["canonical"].casefold()
    role = case.get("calibration_role", "").casefold()
    if "|" in case.get("special_ids", ""):
        return "COMPOSITE_HARD"
    if "compound" in role or case.get("source_stratum") == "compound":
        return "COMPOSITE_HARD"
    if "quantity" in role or "count" in case.get("source_stratum", "").casefold():
        return "MULTI_OBJECT_OR_COUNT"
    if "restraint" in role or "restraint" in case.get("source_stratum", "").casefold():
        return "RESTRAINT_TOPOLOGY"
    if "tentacle" in canonical or "tail" in canonical:
        return "NONHUMAN_APPENDAGE_RELATION"
    if "insertion" in role or case.get("source_stratum") == "bodypart":
        return "BODY_SITE_STATE"
    if case.get("source_stratum") in {"relation", "components_only", "actor_subject_object", "spatial"}:
        return "SIMPLE_RELATION"
    if any(word in canonical for word in ("inflation", "expansion", "growth", "pregnant")):
        return "ANATOMY_CHANGING"
    if case.get("source_stratum") in {"simple_unary", "rare_or_no_vocab", "outcome_auto_candidate", "outcome_blocked"}:
        return "UNARY_OBJECT_OR_STATE"
    return "SIMPLE_RELATION"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def artifact_gate(row: dict[str, Any]) -> dict[str, Any]:
    """Check only objective artifact/provenance properties before semantics."""
    artifact = row.get("image_artifact", {})
    generation = row.get("generation", {})
    path = Path(str(artifact.get("path", "")))
    reasons: list[str] = []
    if not path.is_file():
        return {"status": "BLOCKED", "reasons": ["MISSING_IMAGE"]}
    try:
        with Image.open(path) as image:
            image.verify()
        with Image.open(path) as image:
            actual_size = image.size
            sample = image.convert("L").resize((64, 64))
            stats = ImageStat.Stat(sample)
            spread = stats.extrema[0][1] - stats.extrema[0][0]
            variance = stats.var[0]
    except Exception as exc:  # pragma: no cover - exact decoder error is runtime-specific
        return {"status": "BLOCKED", "reasons": ["CORRUPT_IMAGE", type(exc).__name__]}
    if actual_size != (artifact.get("width"), artifact.get("height")):
        reasons.append("DIMENSION_MISMATCH")
    if path.stat().st_size != artifact.get("bytes"):
        reasons.append("BYTE_COUNT_MISMATCH")
    expected_hash = str(artifact.get("sha256", "")).casefold()
    if expected_hash and sha256(path) != expected_hash:
        reasons.append("HASH_MISMATCH")
    if spread <= 8 and variance <= 1.0:
        reasons.append("NEAR_UNIFORM_IMAGE")
    metadata_artifact = Path(str(generation.get("png_info_raw_artifact", "")))
    if not metadata_artifact.is_file():
        reasons.append("MISSING_METADATA")
    if row.get("screening", {}).get("provenance_complete") is not True:
        reasons.append("INCOMPLETE_PROVENANCE")
    return {"status": "BLOCKED" if reasons else "PASS", "reasons": reasons}


def review_index(path: Path) -> dict[str, dict[str, Any]]:
    if not path.is_file():
        return {}
    payload = read_json(path)
    return {str(row["image_id"]): row for row in payload.get("records", [])}


def summarize_case(case: dict[str, str], rows: list[dict[str, Any]], reviews: dict[str, dict[str, Any]]) -> dict[str, Any]:
    classes = Counter(cls for row in rows for cls in row.get("screening", {}).get("screening_classes", []))
    artifact_rows = [artifact_gate(row) for row in rows]
    reviewed = [reviews[row["image_id"]] for row in rows if row["image_id"] in reviews]
    validity_failures = [
        row["image_id"] for row in reviewed
        if row.get("contrast_realized") is False
        or str(row.get("contrast_realized", "")).casefold() == "no"
    ]
    target_presence = Counter(row.get("human_target_concept_present", "not_recorded") for row in reviewed)
    return {
        "case_id": case["case_id"],
        "special_ids": [int(value) for value in case["special_ids"].split("|")],
        "canonical": case["canonical"],
        "structural_class": structural_class(case),
        "existing_image_count": len(rows),
        "evaluator_complete_image_count": sum(
            all(item.get("execution_state") == "OK" for item in row.get("evaluators", {}).values())
            for row in rows
        ),
        "high_confidence_image_count": sum(
            "HIGH_CONFIDENCE_AUTO_LIKELY" in row.get("screening", {}).get("screening_classes", [])
            for row in rows
        ),
        "machine_disagreement_image_count": classes["DISAGREEMENT"],
        "screening_class_counts": dict(classes),
        "human_reviewed_image_count": len(reviewed),
        "human_target_presence": dict(target_presence),
        "experiment_validity_failure_image_ids": validity_failures,
        "artifact_gate": {
            "pass": sum(item["status"] == "PASS" for item in artifact_rows),
            "blocked": sum(item["status"] == "BLOCKED" for item in artifact_rows),
            "reasons": dict(Counter(reason for item in artifact_rows for reason in item["reasons"])),
        },
        "semantic_scope": "target_presence_only" if reviewed else "not_human_reviewed",
        "additional_image_value": (
            "TARGETED"
            if structural_class(case) in {"SIMPLE_RELATION", "BODY_SITE_STATE", "RESTRAINT_TOPOLOGY", "COMPOSITE_HARD"}
            else "NARROW_ONLY"
        ),
    }


def markdown_report(report: dict[str, Any]) -> str:
    lines = [
        "# Issue #30 Phase 2 structural coverage — 2026-09-10",
        "",
        "This report reuses the frozen Phase 1 pilot. It does not reinterpret the Phase 1 verdicts or promote any production AUTO rule.",
        "",
        "## Reused evidence",
        "",
        f"- Run: `{report['run_id']}`",
        f"- Existing images: **{report['existing_image_count']}**",
        f"- Evaluator records: **{report['evaluator_record_count']}**",
        f"- Complete three-evaluator images: **{report['evaluator_complete_image_count']}**",
        f"- Human review records reused: **{report['human_review_record_count']}**",
        f"- Artifact gate PASS / BLOCKED: **{report['artifact_gate']['pass']} / {report['artifact_gate']['blocked']}**",
        f"- Experiment-validity failures recorded by human review: **{report['experiment_validity_failure_count']}**",
        "",
        "## Capability coverage",
        "",
        "| Class | Cases | Images | Human-reviewed | Evaluator complete | High-confidence | Disagreement | Artifact BLOCKED | Additional value |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for item in report["structural_classes"]:
        lines.append(
            f"| `{item['structural_class']}` | {item['case_count']} | {item['image_count']} | "
            f"{item['human_reviewed_image_count']} | {item['evaluator_complete_image_count']} | "
            f"{item['high_confidence_image_count']} | {item['machine_disagreement_image_count']} | "
            f"{item['artifact_blocked_image_count']} | {item['additional_image_value']} |"
        )
    lines += [
        "",
        "## Evidence boundaries",
        "",
        "- The 19 human records answer only whether the target concept was visible; unasked relation, ownership, count, spatial, compound, and Stage10-preference dimensions remain unlabelled.",
        "- Evaluator disagreement and component-only observations remain triage signals. They do not authorize structural Special success.",
        "- Artifact failures are reported as `BLOCKED` before semantic evaluation. A failed target/contrast realization is reported separately as experiment-validity failure.",
        "- Existing evidence supports only narrow targeted questions; broad AUTO calibration is not justified.",
        "",
        "## Recommended first-wave questions",
        "",
        "See `ISSUE30_PHASE2_TEST_DESIGN.md` and `ISSUE30_PHASE2_TEST_MANIFEST.csv`. The selected wave is capped at 12 images: three questions, A/B paired conditions, two predetermined seeds per condition.",
        "",
        "## Local-only source",
        "",
        f"`{report['local_artifact_root']}`",
        "",
    ]
    return "\n".join(lines)


def build_report(run_root: Path, case_path: Path, review_path: Path) -> dict[str, Any]:
    cases = load_cases(case_path)
    rows = load_results(run_root)
    reviews = review_index(review_path)
    by_case: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        case_id = str(row.get("case_id", ""))
        if case_id not in cases:
            raise ValueError(f"result references case absent from manifest: {case_id}")
        by_case[case_id].append(row)
    summaries = [summarize_case(cases[case_id], by_case[case_id], reviews) for case_id in cases]
    class_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in summaries:
        class_groups[item["structural_class"]].append(item)
    class_summaries = []
    for name in sorted(class_groups):
        group = class_groups[name]
        class_summaries.append({
            "structural_class": name,
            "case_count": len(group),
            "image_count": sum(item["existing_image_count"] for item in group),
            "human_reviewed_image_count": sum(item["human_reviewed_image_count"] for item in group),
            "evaluator_complete_image_count": sum(item["evaluator_complete_image_count"] for item in group),
            "high_confidence_image_count": sum(item["high_confidence_image_count"] for item in group),
            "machine_disagreement_image_count": sum(item["machine_disagreement_image_count"] for item in group),
            "artifact_blocked_image_count": sum(item["artifact_gate"]["blocked"] for item in group),
            "additional_image_value": "TARGETED" if any(item["additional_image_value"] == "TARGETED" for item in group) else "NARROW_ONLY",
            "case_ids": [item["case_id"] for item in group],
        })
    artifact = Counter()
    validity_failures = []
    for item in summaries:
        artifact.update({"pass": item["artifact_gate"]["pass"], "blocked": item["artifact_gate"]["blocked"]})
        validity_failures.extend(item["experiment_validity_failure_image_ids"])
    return {
        "schema_version": "issue30.phase2.structural_coverage.v1",
        "source": "frozen_phase1_local_pilot",
        "run_id": str(rows[0].get("run_id", "unknown")),
        "local_artifact_root": str(run_root),
        "case_manifest": str(case_path),
        "review_results": str(review_path),
        "existing_image_count": len(rows),
        "evaluator_record_count": sum(len(row.get("evaluators", {})) for row in rows),
        "evaluator_complete_image_count": sum(
            all(item.get("execution_state") == "OK" for item in row.get("evaluators", {}).values())
            for row in rows
        ),
        "human_review_record_count": len(reviews),
        "artifact_gate": dict(artifact),
        "experiment_validity_failure_count": len(validity_failures),
        "experiment_validity_failure_image_ids": validity_failures,
        "structural_classes": class_summaries,
        "cases": summaries,
        "frozen_policy": {
            "taggers_are_assistive_triage_only": True,
            "relation_binding_auto": False,
            "phase1_evidence_reinterpreted": False,
            "production_data_modified": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--case-manifest", type=Path, default=DEFAULT_CASE_MANIFEST)
    parser.add_argument("--review-results", type=Path, default=DEFAULT_REVIEW_RESULTS)
    parser.add_argument("--output-json", type=Path, default=ROOT / "docs/testing/ISSUE30_PHASE2_STRUCTURAL_COVERAGE.json")
    parser.add_argument("--output-md", type=Path, default=ROOT / "docs/testing/ISSUE30_PHASE2_STRUCTURAL_COVERAGE.md")
    args = parser.parse_args()
    report = build_report(args.run_root, args.case_manifest, args.review_results)
    write_json(args.output_json, report)
    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.write_text(markdown_report(report), encoding="utf-8")
    print(json.dumps({
        "status": "COVERAGE_COMPLETE",
        "existing_images": report["existing_image_count"],
        "artifact_pass": report["artifact_gate"]["pass"],
        "artifact_blocked": report["artifact_gate"]["blocked"],
        "experiment_validity_failures": report["experiment_validity_failure_count"],
        "output_json": str(args.output_json),
        "output_md": str(args.output_md),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
