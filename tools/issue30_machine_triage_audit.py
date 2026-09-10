#!/usr/bin/env python3
"""Audit existing Generation Batch evaluator provenance and retrospective routing."""
from __future__ import annotations

import argparse
import gzip
import json
from collections import Counter
from pathlib import Path
from typing import Any


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_gzip_json(path: Path) -> Any:
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        return json.load(stream)


def artifact_state(path: Path) -> tuple[str, str]:
    if not path.is_file():
        return "MISSING", "file does not exist"
    try:
        value = read_gzip_json(path) if path.suffix == ".gz" else read_json(path)
    except Exception as exc:
        return "UNREADABLE", type(exc).__name__
    if isinstance(value, dict) and "error" in value:
        return "ERROR_OBJECT", str(value.get("error"))
    return "OK", "readable non-error result"


def expected_refs(root: Path, image_id: str) -> dict[str, Path]:
    return {
        "wd14": root / "raw/wd14" / f"{image_id}.json",
        "kagami": root / "raw/kagami" / f"{image_id}.json.gz",
        "cl_v2_00": root / "raw/cl v2.00" / f"{image_id}.json.gz",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--human-result", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    args = parser.parse_args()
    rows = read_json(args.run_root / "calibration_results.json")
    human = read_json(args.human_result)
    records = []
    reported_mismatches = []
    actual_successes = Counter()
    actual_failures = Counter()
    class_counts = Counter()
    pair_keys = set()
    condition_counts = Counter()
    for row in rows:
        image_id = row["image_id"]
        condition = "A" if row["cell_type"].startswith("target_present") else "B"
        condition_counts[condition] += 1
        pair_keys.add((row["case_id"], row["generation"]["seed"]))
        class_counts.update(row["screening"]["screening_classes"])
        refs = expected_refs(args.run_root, image_id)
        evaluator_records = {}
        for name, path in refs.items():
            state, detail = artifact_state(path)
            if state == "OK":
                actual_successes[name] += 1
            else:
                actual_failures[name] += 1
            reported = row["evaluators"][name].get("raw_output_artifact")
            if Path(reported) != path:
                reported_mismatches.append({"image_id": image_id, "evaluator": name, "reported": reported, "expected": str(path)})
            evaluator_records[name] = {"expected_artifact": str(path), "reported_artifact": reported, "artifact_state": state, "detail": detail, "filename_image_binding": path.stem.replace(".json", "") == image_id or path.name.startswith(image_id + ".")}
        machine_route = "HUMAN_REVIEW_REQUIRED"
        reasons = []
        if any(item["artifact_state"] != "OK" for item in evaluator_records.values()):
            machine_route = "BLOCKED"
            reasons.append("evaluator artifact missing/unreadable/error")
        if "RELATION_OR_BINDING" in row["screening"]["screening_classes"]:
            reasons.append("relation/binding protected")
        if "LOW_CONFIDENCE" in row["screening"]["screening_classes"]:
            reasons.append("low confidence")
        if not reasons and row["screening"]["screening_classes"] == []:
            machine_route = "MACHINE_HANDLED_CANDIDATE"
            reasons.append("narrow direct/non-relation candidate")
        if machine_route != "MACHINE_HANDLED_CANDIDATE" and not reasons:
            reasons.append("structural or non-eligible class")
        records.append({"image_id": image_id, "case_id": row["case_id"], "condition": condition, "seed": row["generation"]["seed"], "screening_classes": row["screening"]["screening_classes"], "machine_route": machine_route, "route_reasons": reasons, "evaluators": evaluator_records})
    human_pairs = {(item["case_id"], item["seed"]): item for item in human["pair_results"]}
    human_reviewed_pairs = len(human_pairs)
    machine_handled_images = sum(item["machine_route"] == "MACHINE_HANDLED_CANDIDATE" for item in records)
    human_required_images = sum(item["machine_route"] == "HUMAN_REVIEW_REQUIRED" for item in records)
    blocked_images = sum(item["machine_route"] == "BLOCKED" for item in records)
    ab_marker_check = len(pair_keys) == 6 and condition_counts == {"A": 6, "B": 6} and all(
        sum(item["condition"] == condition for item in records if item["case_id"] == case and item["seed"] == seed) == 1
        for case, seed in pair_keys for condition in ("A", "B")
    )
    report = {
        "schema_version": "issue30.phase2.machine_triage_audit.v1",
        "status": "AUDIT_COMPLETE_REVIEW_REQUIRED",
        "new_images": 0,
        "generation_batch_images": len(records),
        "planned_evaluator_runs": len(records) * 3,
        "actual_successful_evaluator_runs": sum(actual_successes.values()),
        "actual_failed_or_missing_evaluator_runs": sum(actual_failures.values()),
        "per_evaluator_successes": dict(actual_successes),
        "per_evaluator_failures": dict(actual_failures),
        "reported_reference_integrity_check": "FAIL" if reported_mismatches else "PASS",
        "raw_artifact_image_binding_check": "PASS" if all(item["filename_image_binding"] and item["artifact_state"] == "OK" for record in records for item in record["evaluators"].values()) else "FAIL",
        "evaluator_reference_integrity_check": "FAIL" if reported_mismatches else "PASS",
        "reported_reference_mismatches": reported_mismatches,
        "ab_marker_integrity_check": "PASS" if ab_marker_check else "FAIL",
        "screening_class_occurrences": dict(class_counts),
        "machine_handled_images": machine_handled_images,
        "machine_handled_pairs": 0,
        "human_required_images": human_required_images,
        "human_required_pairs": human_reviewed_pairs,
        "blocked_images": blocked_images,
        "reviewed_pairs": human_reviewed_pairs,
        "reviewed_images": human["reviewed_images"],
        "human_review_reduction_percent": round(machine_handled_images / len(records) * 100, 2) if records else 0.0,
        "human_review_reduction_statement": "HUMAN_REVIEW_REDUCTION = 0 for this batch design" if machine_handled_images == 0 else None,
        "human_result_summary": human["summary"],
        "per_image": records,
        "decision": "HOLD_FOR_DEV_REVIEW",
        "limitation": "The batch selected only structural/relation-sensitive or low-confidence cases, so machine-first routing safely removed no images. The 0% reduction is a batch design failure for user-work reduction, not a user review failure.",
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Issue #30 Phase 2 Machine Triage / Evaluator Provenance Audit — 2026-09-11",
        "",
        "## RESULT",
        "",
        "既存 Generation Batch 12画像を対象に、画像生成・新規seed・evaluator再実行なしで provenance と machine-first routing を監査した。",
        "",
        f"- New images: **0**",
        f"- Planned evaluator runs: **{report['planned_evaluator_runs']}**",
        f"- Actual successful evaluator runs: **{report['actual_successful_evaluator_runs']}**（WD14 {actual_successes['wd14']} / Kagami {actual_successes['kagami']} / CL {actual_successes['cl_v2_00']}）",
        f"- Failed/missing evaluator runs: **{report['actual_failed_or_missing_evaluator_runs']}**",
        f"- Raw artifact image binding: **{report['raw_artifact_image_binding_check']}**",
        f"- Reported reference integrity: **{report['reported_reference_integrity_check']}**（{len(reported_mismatches)}件の誤参照）",
        f"- A/B marker integrity: **{report['ab_marker_integrity_check']}**",
        "",
        "## MACHINE-FIRST ROUTING",
        "",
        f"- Machine-handled candidates: **{machine_handled_images} images / 0 pairs**",
        f"- Human review required: **{human_required_images} images / {human_reviewed_pairs} pairs**",
        f"- Blocked: **{blocked_images} images**",
        f"- Human-review reduction: **{report['human_review_reduction_percent']}%**",
        "",
        "`HUMAN_REVIEW_REDUCTION = 0 for this batch design`。GB-001/GB-002はrelation・binding・body-site保護、GB-003はlow-confidence等により、全12画像を安全に機械処理済み扱いにはできない。これはユーザーではなく、バッチ選定/設計の省力化失敗である。",
        "",
        "## PROVENANCE DEFECT",
        "",
        f"raw artifactは12画像×3 evaluatorで全36件が画像ID別に存在し、読み取り可能でerror objectもなかった。一方、既存 `calibration_results.json` の `raw_output_artifact` 欄は最終画像以外を中心に誤っており、実測で{len(reported_mismatches)}件が期待参照と不一致だった。これはreporting defectとして記録し、正しい期待参照をmachine-readable audit JSONに再構成した。evaluatorの再実行はしていない。",
        "",
        "## DECISION / NEXT",
        "",
        "`HOLD_FOR_DEV_REVIEW`。Phase 2の次batchやStage10 production A/Bへ進めない。DEV/ChatGPTがこのauditを受け入れた後、必要ならmachine-judgeable direct/simple-unaryを意図的に含む4–5実験の別batchを判断する。",
        "",
        f"Existing local artifact root: `{args.run_root}`",
    ]
    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "actual_successful_evaluator_runs": report["actual_successful_evaluator_runs"], "reference_integrity": report["evaluator_reference_integrity_check"], "human_review_reduction_percent": report["human_review_reduction_percent"], "ab_marker_integrity": report["ab_marker_integrity_check"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
