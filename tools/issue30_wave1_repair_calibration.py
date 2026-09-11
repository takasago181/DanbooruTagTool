#!/usr/bin/env python3
"""Repair Wave 1 evaluator serialization from existing raw artifacts only."""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from tools.issue30_calibration_pilot import (
    THRESHOLDS,
    evaluator_record,
    normalized_pairs,
    read_gzip_json,
    read_json,
    routing,
    screening,
    target_score,
)
from tools.issue30_machine_first_routing import pair_routes, route_image


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RUN_ROOT = Path(r"C:\Users\takas\Downloads\StabilityMatrix-win-x64\Data\Models\Issue30Evaluators\issue30_broad_coverage_wave1_20260911")
DEFAULT_SOURCE_RESULT = ROOT / "docs/testing/ISSUE30_BROAD_COVERAGE_WAVE1_RESULT.json"
DEFAULT_VISUAL_VERDICTS = ROOT / "docs/testing/ISSUE30_BROAD_COVERAGE_WAVE1_VISUAL_VERDICTS_20260911.json"
DEFAULT_OUTPUT_JSON = ROOT / "docs/testing/ISSUE30_BROAD_COVERAGE_WAVE1_REPAIRED_CALIBRATION.json"
DEFAULT_OUTPUT_MD = ROOT / "docs/testing/ISSUE30_BROAD_COVERAGE_WAVE1_REPAIRED_CALIBRATION.md"

EVALUATOR_ORDER = ("wd14", "kagami", "cl_v2_00")
VISUAL_TRUTH = {
    "BOTH_PASS": {"A": True, "B": True},
    "B_ONLY_PASS": {"A": False, "B": True},
    "A_ONLY_PASS": {"A": True, "B": False},
    "BOTH_FAIL": {"A": False, "B": False},
    "UNCLEAR": {"A": None, "B": None},
    "ASSET_INVALID": {"A": None, "B": None},
}


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_manifest(path: Path) -> dict[str, dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        rows = {row["case_id"]: row for row in csv.DictReader(stream)}
    if len(rows) != 16:
        raise RuntimeError(f"expected the frozen 16-case Wave 1 manifest, got {len(rows)}")
    return rows


def expected_paths(run_root: Path, image_id: str) -> dict[str, Path]:
    return {
        "wd14": run_root / "raw/wd14" / f"{image_id}.json",
        "kagami": run_root / "raw/kagami" / f"{image_id}.json.gz",
        "cl_v2_00": run_root / "raw/cl v2.00" / f"{image_id}.json.gz",
    }


def read_artifact(path: Path) -> Any:
    if path.suffix == ".gz":
        return read_gzip_json(path)
    return read_json(path)


def rebuild_evaluator(name: str, path: Path, case: dict[str, str]) -> dict[str, Any]:
    if not path.is_file():
        raise RuntimeError(f"missing raw evaluator artifact: {path}")
    obj = read_artifact(path)
    if isinstance(obj, dict) and "error" in obj:
        raise RuntimeError(f"raw evaluator artifact is an error object: {path}")
    if name == "wd14":
        pairs = normalized_pairs(obj)
        score, observed, basis = target_score(pairs, case)
        tags = [{"tag": tag, "score": score} for tag, score in pairs[:200]]
        return evaluator_record("WD14", "wd14-eva02.v3.large", "runtime-interrogator", "OK", score, tags, basis, observed, path, THRESHOLDS["WD14"])
    top_tags = obj.get("top_tags") if isinstance(obj, dict) else None
    if not isinstance(top_tags, list):
        raise RuntimeError(f"raw {name} artifact lacks top_tags: {path}")
    pairs = [(str(tag), float(score)) for tag, score in top_tags]
    score, observed, basis = target_score(pairs, case)
    threshold = THRESHOLDS["Kagami"] if name == "kagami" else THRESHOLDS["CL"]
    visible = [{"tag": tag, "score": score} for tag, score in pairs[:500] if score >= threshold]
    if name == "kagami":
        return evaluator_record("Kagami", "Kagami-24k", "fbf04252c68c9cbf03c8b343e537e3cd7594c8a1", "OK", score, visible, basis, observed, path, threshold)
    return evaluator_record("CL v2.00", "v2.00", "b57909e9c63f71e208a26473e7aabdf45ed6b6:v2_00", "OK", score, visible, basis, observed, path, threshold)


def condition(cell_type: str) -> str:
    if cell_type.startswith("target_present"):
        return "A"
    if cell_type.startswith("contrast"):
        return "B"
    raise RuntimeError(f"invalid structured A/B marker: {cell_type}")


def rebuild_rows(raw_rows: list[dict[str, Any]], manifest: dict[str, dict[str, str]], run_root: Path) -> tuple[list[dict[str, Any]], dict[str, int]]:
    repaired: list[dict[str, Any]] = []
    source_pointer_mismatches = 0
    for original in raw_rows:
        row = dict(original)
        case = manifest[row["case_id"]]
        image_id = row["image_id"]
        image_path = Path(row["image_artifact"]["path"])
        if not image_path.is_file():
            raise RuntimeError(f"missing generated image: {image_path}")
        if file_sha256(image_path) != row["image_artifact"]["sha256"]:
            raise RuntimeError(f"generated image hash mismatch: {image_id}")
        rebuilt = {}
        original_evaluators = row.get("evaluators", {})
        for name, path in expected_paths(run_root, image_id).items():
            reported = original_evaluators.get(name, {}).get("raw_output_artifact")
            if str(Path(reported)) != str(path):
                source_pointer_mismatches += 1
            rebuilt[name] = rebuild_evaluator(name, path, case)
        screen = screening({"case": case}, rebuilt)
        row["condition"] = condition(row["cell_type"])
        row["evaluators"] = rebuilt
        row["screening"] = {
            "automatically_screened": True,
            "screening_classes": screen["classes"],
            "high_confidence_eligible": screen["high"],
            "provenance_complete": True,
            "desk_classification": case["desk_recommendation"],
            "desk_relation_sensitive": screen["relation"],
            "score_band": screen["band"],
        }
        row["evaluator_agreement"] = {
            "wd14_vote": rebuilt["wd14"]["target_observed"],
            "kagami_vote": rebuilt["kagami"]["target_observed"],
            "cl_v2_00_vote": rebuilt["cl_v2_00"]["target_observed"],
            "agreement_class": (
                "ABSTAINED" if any(rebuilt[name]["target_observed"] is None for name in EVALUATOR_ORDER)
                else "UNANIMOUS_POSITIVE" if all(rebuilt[name]["target_observed"] for name in EVALUATOR_ORDER)
                else "UNANIMOUS_NEGATIVE" if not any(rebuilt[name]["target_observed"] for name in EVALUATOR_ORDER)
                else "SPLIT"
            ),
        }
        row["routing_evaluations"] = routing(rebuilt, screen)
        route_input = {
            "evaluators": rebuilt,
            "screening": row["screening"],
            "case": {"relation_binding_required": case["relation_binding_required"]},
        }
        row["machine_route"], row["route_reasons"] = route_image(route_input, provenance_pass=True)
        row["serialization_repair"] = {
            "rebuilt_from_raw_artifact": True,
            "raw_artifact_locators": {name: str(path) for name, path in expected_paths(run_root, image_id).items()},
            "original_report_locators": {name: original_evaluators.get(name, {}).get("raw_output_artifact") for name in EVALUATOR_ORDER},
        }
        repaired.append(row)
    return repaired, {"source_pointer_mismatches": source_pointer_mismatches}


def evaluator_metrics(rows: list[dict[str, Any]], visual_by_pair: dict[tuple[str, int], str]) -> dict[str, dict[str, Any]]:
    metrics = {}
    for name in EVALUATOR_ORDER:
        counts = Counter()
        for row in rows:
            verdict = visual_by_pair[(row["case_id"], int(row["generation"]["seed"]))]
            truth = VISUAL_TRUTH[verdict][row["condition"]]
            observed = row["evaluators"][name]["target_observed"]
            if truth is None:
                counts["visual_unknown"] += 1
            elif observed is None:
                counts["abstained"] += 1
            elif observed == truth:
                counts["exact_agreement"] += 1
            elif observed and not truth:
                counts["false_positive"] += 1
            else:
                counts["false_negative"] += 1
        known = counts["exact_agreement"] + counts["false_positive"] + counts["false_negative"] + counts["abstained"]
        comparable = counts["exact_agreement"] + counts["false_positive"] + counts["false_negative"]
        metrics[name] = {
            **dict(counts),
            "visual_known_images": known - counts["abstained"],
            "comparable_images": comparable,
            "agreement_percent": round(counts["exact_agreement"] / comparable * 100, 2) if comparable else None,
        }
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", type=Path, default=DEFAULT_RUN_ROOT)
    parser.add_argument("--source-result", type=Path, default=DEFAULT_SOURCE_RESULT)
    parser.add_argument("--visual-verdicts", type=Path, default=DEFAULT_VISUAL_VERDICTS)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    args = parser.parse_args()
    raw_report_path = args.run_root / "calibration_results.json"
    raw_rows = read_json(raw_report_path)
    if len(raw_rows) != 64:
        raise RuntimeError(f"expected 64 existing Wave 1 rows, got {len(raw_rows)}")
    manifest_path = ROOT / "docs/testing/ISSUE30_BROAD_COVERAGE_WAVE1_MANIFEST.csv"
    manifest = load_manifest(manifest_path)
    visual_payload = read_json(args.visual_verdicts)
    visual_by_pair = {(item["case_id"], int(item["seed"])): item["verdict"] for item in visual_payload["pairs"]}
    if len(visual_by_pair) != 32:
        raise RuntimeError(f"expected 32 visual A/B verdicts, got {len(visual_by_pair)}")
    repaired, repair_counts = rebuild_rows(raw_rows, manifest, args.run_root)
    grouped: dict[tuple[str, int], list[dict[str, Any]]] = defaultdict(list)
    for row in repaired:
        grouped[(row["case_id"], int(row["generation"]["seed"]))].append(row)
    pairs = pair_routes(repaired)
    for row in repaired:
        row["machine_pair_route"] = pairs[(row["case_id"], int(row["generation"]["seed"]))]["route"]
        verdict = visual_by_pair[(row["case_id"], int(row["generation"]["seed"]))]
        row["visual_reference"] = {"pair_verdict": verdict, "expected_target_observed": VISUAL_TRUTH[verdict][row["condition"]]}
    pair_records = []
    for key, pair in sorted(grouped.items()):
        case_id, seed = key
        verdict = visual_by_pair[key]
        route = pairs[key]["route"]
        protected = manifest[case_id]["relation_binding_required"].casefold() == "true" or manifest[case_id]["desk_recommendation"] != "AUTO_CANDIDATE"
        pair_records.append({
            "case_id": case_id,
            "seed": seed,
            "source_stratum": manifest[case_id]["source_stratum"],
            "machine_pair_route": route,
            "visual_verdict": verdict,
            "visual_safe_for_machine_pair": verdict == "BOTH_PASS",
            "protected_human_route": protected,
            "image_ids": [row["image_id"] for row in sorted(pair, key=lambda item: item["condition"])],
        })
    machine_pairs = [item for item in pair_records if item["machine_pair_route"] == "MACHINE_HANDLED_PAIR"]
    visual_safe_pairs = [item for item in pair_records if item["visual_safe_for_machine_pair"]]
    human_both_pass = [item for item in pair_records if item["machine_pair_route"] == "HUMAN_REVIEW_REQUIRED_PAIR" and item["visual_safe_for_machine_pair"]]
    nonprotected_human_both_pass = [item for item in human_both_pass if not item["protected_human_route"]]
    source_result = read_json(args.source_result)
    frozen = {row["image_id"]: row for row in source_result["image_records"]}
    route_comparison = {
        "image_route_matches_frozen": sum(row["machine_route"] == frozen[row["image_id"]]["machine_route"] for row in repaired),
        "pair_route_matches_frozen": sum(item["machine_pair_route"] == source_pair["route"] for item in pair_records for source_pair in [next(row for row in source_result["pair_routes"].values() if row.get("case_id") == item["case_id"] and int(row.get("seed", -1)) == item["seed"])]) if source_result.get("pair_routes") else None,
    }
    result = {
        "schema_version": "issue30.wave1.repaired_calibration.v1",
        "status": "REPAIRED_FROM_EXISTING_RAW_ARTIFACTS_MACHINE_VS_VISUAL_CALIBRATION_COMPLETE_STOPPED",
        "run_id": repaired[0]["run_id"],
        "source_reports": {
            "raw_serialized_report": str(raw_report_path),
            "raw_serialized_report_sha256": file_sha256(raw_report_path),
            "previous_wave1_result": str(args.source_result),
            "previous_wave1_result_sha256": file_sha256(args.source_result),
            "visual_verdicts": str(args.visual_verdicts),
        },
        "repair_scope": {
            "images_regenerated": 0,
            "evaluator_reruns": 0,
            "rows_rebuilt": len(repaired),
            "raw_artifacts_consumed": len(repaired) * 3,
            **repair_counts,
            "repaired_fields": ["evaluators", "evaluator_agreement", "routing_evaluations", "screening", "machine_route", "machine_pair_route"],
        },
        "raw_artifact_integrity": {
            "image_count": len(repaired),
            "evaluator_artifact_count": len(repaired) * 3,
            "all_rebuilt_evaluators_ok": all(item["execution_state"] == "OK" for row in repaired for item in row["evaluators"].values()),
            "all_image_hashes_match_source_report": True,
        },
        "visual_summary": dict(Counter(item["visual_verdict"] for item in pair_records)),
        "machine_pair_summary": dict(Counter(item["machine_pair_route"] for item in pair_records)),
        "machine_vs_visual": {
            "machine_handled_pairs": len(machine_pairs),
            "machine_handled_visual_safe_pairs": sum(item["visual_safe_for_machine_pair"] for item in machine_pairs),
            "machine_handled_false_safe_pairs": sum(not item["visual_safe_for_machine_pair"] for item in machine_pairs),
            "machine_handled_precision_percent": round(sum(item["visual_safe_for_machine_pair"] for item in machine_pairs) / len(machine_pairs) * 100, 2) if machine_pairs else None,
            "machine_handled_false_safe_percent": round(sum(not item["visual_safe_for_machine_pair"] for item in machine_pairs) / len(machine_pairs) * 100, 2) if machine_pairs else None,
            "visual_safe_pairs": len(visual_safe_pairs),
            "machine_capture_of_visual_safe_pairs_percent": round(sum(item["visual_safe_for_machine_pair"] for item in machine_pairs) / len(visual_safe_pairs) * 100, 2) if visual_safe_pairs else None,
            "human_route_both_pass_pairs_diagnostic": len(human_both_pass),
            "protected_human_route_both_pass_pairs": sum(item["protected_human_route"] for item in human_both_pass),
            "nonprotected_human_route_both_pass_candidates": len(nonprotected_human_both_pass),
            "note": "Human/structural routes are not relabeled as over-routing merely because visual verdict is BOTH_PASS.",
        },
        "per_evaluator_machine_vs_visual": evaluator_metrics(repaired, visual_by_pair),
        "route_recalculation_comparison": route_comparison,
        "family_metrics": {
            family: {
                "pair_count": sum(item["source_stratum"] == family for item in pair_records),
                "visual_verdicts": dict(Counter(item["visual_verdict"] for item in pair_records if item["source_stratum"] == family)),
                "machine_pair_routes": dict(Counter(item["machine_pair_route"] for item in pair_records if item["source_stratum"] == family)),
                "machine_false_safe_pairs": sum(item["machine_pair_route"] == "MACHINE_HANDLED_PAIR" and not item["visual_safe_for_machine_pair"] for item in pair_records if item["source_stratum"] == family),
            }
            for family in sorted({item["source_stratum"] for item in pair_records})
        },
        "pair_records": pair_records,
        "image_records": repaired,
        "machine_route_frozen": True,
        "visual_verdicts_frozen": True,
        "decision": "STOP_AFTER_REPAIR_AND_MACHINE_VS_VISUAL_CALIBRATION",
        "wave2_started": False,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md = [
        "# Issue #30 Wave 1 repaired calibration — 2026-09-11",
        "",
        "Status: `REPAIRED_FROM_EXISTING_RAW_ARTIFACTS_MACHINE_VS_VISUAL_CALIBRATION_COMPLETE_STOPPED`",
        "",
        "The stale per-row evaluator serialization was repaired from the existing image-specific WD14/Kagami/CL raw artifacts. No image was regenerated and no evaluator was rerun.",
        "",
        "## Repair",
        "",
        f"- Rebuilt rows: **{len(repaired)}**; raw evaluator artifacts consumed: **{len(repaired) * 3}**",
        f"- Original stale evaluator locators detected: **{repair_counts['source_pointer_mismatches']}**",
        "- Raw evaluator execution state: **64/64 per evaluator; 192/192 total**",
        "- Image hash binding: **PASS**",
        "",
        "## Visual calibration",
        "",
        f"- Visual verdicts: `{dict(Counter(item['visual_verdict'] for item in pair_records))}`",
        f"- Machine pair routes: `{dict(Counter(item['machine_pair_route'] for item in pair_records))}`",
        f"- Machine-handled false-safe: **{result['machine_vs_visual']['machine_handled_false_safe_pairs']}/{result['machine_vs_visual']['machine_handled_pairs']} ({result['machine_vs_visual']['machine_handled_false_safe_percent']}%)**",
        f"- Machine-handled precision against `BOTH_PASS`: **{result['machine_vs_visual']['machine_handled_precision_percent']}%**",
        f"- Human-route `BOTH_PASS` diagnostic: **{result['machine_vs_visual']['human_route_both_pass_pairs_diagnostic']}**; protected subset **{result['machine_vs_visual']['protected_human_route_both_pass_pairs']}**",
        "- Structural/protected human routes are not called over-routing solely from a `BOTH_PASS` visual result.",
        "",
        "## Decision",
        "",
        "Machine route remains frozen. This calibration evidence is too small to promote structural/pair-delta semantics to AUTO. Wave 2 and Stage10 production A/B remain unstarted.",
    ]
    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps({key: result[key] for key in ("status", "repair_scope", "visual_summary", "machine_pair_summary", "machine_vs_visual", "per_evaluator_machine_vs_visual", "route_recalculation_comparison", "decision")}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
