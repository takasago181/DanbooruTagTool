import csv
import json
from pathlib import Path

from tools.issue30_calibration_pilot import load_profiles, load_cases, validate_cases
from tools.issue30_phase2_analysis import structural_class
from tools.issue30_machine_first_routing import marker_integrity, pair_routes, route_image


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs/testing/ISSUE30_PHASE2_TEST_MANIFEST.csv"
PHASE1_CASES = ROOT / "docs/testing/ISSUE30_REAL_IMAGE_CALIBRATION_CASES_20260910.csv"
COVERAGE = ROOT / "docs/testing/ISSUE30_PHASE2_STRUCTURAL_COVERAGE.json"
WAVE_RESULT = ROOT / "docs/testing/ISSUE30_PHASE2_WAVE1_RESULT.json"
WAVE2_MANIFEST = ROOT / "docs/testing/ISSUE30_PHASE2_WAVE2_TEST_MANIFEST.csv"
WAVE2_RESULT = ROOT / "docs/testing/ISSUE30_PHASE2_WAVE2_RESULT.json"
REUSE_MANIFEST = ROOT / "docs/testing/ISSUE30_PHASE2_REUSE_REVIEW_MANIFEST.csv"
REUSE_RESULT = ROOT / "docs/testing/ISSUE30_PHASE2_REUSE_REVIEW_RESULT.json"
REUSE_HUMAN_RESULT = ROOT / "docs/testing/ISSUE30_PHASE2_REUSE_REVIEW_HUMAN_RESULTS_20260911.json"
BATCH_MANIFEST = ROOT / "docs/testing/ISSUE30_PHASE2_GENERATION_BATCH_MANIFEST.csv"
BATCH_RESULT = ROOT / "docs/testing/ISSUE30_PHASE2_GENERATION_BATCH_RESULT.json"
BATCH_HUMAN_RESULT = ROOT / "docs/testing/ISSUE30_PHASE2_GENERATION_BATCH_HUMAN_RESULTS_20260911.json"
BATCH2_MANIFEST = ROOT / "docs/testing/ISSUE30_PHASE2_GENERATION_BATCH2_MANIFEST.csv"
BATCH2_RESULT = ROOT / "docs/testing/ISSUE30_PHASE2_GENERATION_BATCH2_RESULT.json"
TRIAGE_AUDIT = ROOT / "docs/testing/ISSUE30_PHASE2_MACHINE_TRIAGE_AUDIT.json"
HUMAN_REVIEW = ROOT / "docs/testing/ISSUE30_PHASE2_HUMAN_REVIEW_RESULTS_20260910.json"


def test_phase2_manifest_is_bounded_and_uses_current_special_ids():
    cases = load_cases(MANIFEST)
    assert len(cases) == 3
    assert len(cases) * 4 == 12
    validate_cases(cases, load_profiles())
    assert {int(case["special_ids"]) for case in cases} == {264, 750, 2024}
    assert all(case["target_prompt"] and case["contrast_prompt"] for case in cases)
    assert {(case["steps"], case["cfg"], case["width"], case["height"]) for case in cases} == {("25", "5", "1024", "1344")}


def test_phase1_structural_mapping_keeps_frozen_case_manifest_read_only():
    with PHASE1_CASES.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    by_id = {row["case_id"]: row for row in rows}
    assert structural_class(by_id["CAL-001"]) == "UNARY_OBJECT_OR_STATE"
    assert structural_class(by_id["CAL-014"]) == "BODY_SITE_STATE"
    assert structural_class(by_id["CAL-023"]) == "MULTI_OBJECT_OR_COUNT"
    assert structural_class(by_id["CAL-031"]) == "RESTRAINT_TOPOLOGY"
    assert structural_class(by_id["CAL-032"]) == "COMPOSITE_HARD"


def test_coverage_report_records_artifact_and_validity_boundaries():
    report = json.loads(COVERAGE.read_text(encoding="utf-8"))
    assert report["existing_image_count"] == 128
    assert report["evaluator_complete_image_count"] == 128
    assert report["human_review_record_count"] == 19
    assert report["artifact_gate"] == {"pass": 127, "blocked": 1}
    assert report["experiment_validity_failure_count"] == 1
    assert report["frozen_policy"]["relation_binding_auto"] is False


def test_wave_result_is_complete_but_stopped_for_human_review():
    report = json.loads(WAVE_RESULT.read_text(encoding="utf-8"))
    assert report["status"] == "FIRST_WAVE_COMPLETE_REVIEW_REQUIRED"
    assert report["image_count"] == report["new_images_generated"] == 12
    assert report["screen_only_reused_images"] == 12
    assert report["evaluator_runs"] == 36
    assert report["artifact_gate"] == {"PASS": 12}
    assert report["experiment_validity"]["status"] == "PENDING_HUMAN_REVIEW"
    assert report["decision"]["additional_generation"] == "STOP_UNTIL_REVIEW"
    assert report["human_review_pair_count"] == 6
    assert report["human_review_reviewed_image_count"] == 12
    assert report["review_display"]["display_check"] == "PASS"
    assert report["review_display"]["font_path"].endswith("meiryo.ttc")


def test_wave2_manifest_and_result_are_bounded_and_bilingual_review_ready():
    cases = load_cases(WAVE2_MANIFEST)
    assert len(cases) == 2
    assert len(cases) * 4 == 8
    validate_cases(cases, load_profiles())
    assert {int(value) for case in cases for value in case["special_ids"].split("|")} == {147, 269, 275, 1286}
    assert all(case["target_prompt"] and case["contrast_prompt"] for case in cases)
    report = json.loads(WAVE2_RESULT.read_text(encoding="utf-8"))
    assert report["status"] == "SECOND_WAVE_COMPLETE_REVIEW_REQUIRED"
    assert report["image_count"] == report["new_images_generated"] == 8
    assert report["evaluator_runs"] == 24
    assert report["artifact_gate"] == {"PASS": 8}
    assert report["human_review_pair_count"] == 4
    assert report["human_review_reviewed_image_count"] == 8
    assert report["review_display"]["display_check"] == "PASS"
    assert report["decision"]["additional_generation"] == "STOP_UNTIL_REVIEW"


def test_human_review_preserves_pair_outcomes_and_validity_boundaries():
    report = json.loads(HUMAN_REVIEW.read_text(encoding="utf-8"))
    assert report["summary"]["reviewed_images"] == 12
    assert report["summary"]["artifact_failures"] == 0
    assert report["summary"]["p2_001_relation_successes"] == 0
    assert report["summary"]["p2_002_contrast_contamination_pairs"] == 1
    assert report["summary"]["additional_generation"] == "STOP_UNTIL_DEV_REVIEW"
    assert {row["human_answer"] for row in report["pair_results"]} >= {"neither", "A", "both"}


def test_reuse_only_review_is_existing_four_image_bounded_and_stopped():
    with REUSE_MANIFEST.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 4
    assert {row["case_id"] for row in rows} == {"CAL-023"}
    assert {row["condition"] for row in rows} == {"A", "B"}
    assert {row["seed"] for row in rows} == {"30230", "30231"}
    report = json.loads(REUSE_RESULT.read_text(encoding="utf-8"))
    assert report["status"] == "REUSE_ONLY_REVIEW_READY"
    assert report["new_images_generated"] == report["new_seeds"] == report["evaluator_reruns"] == 0
    assert report["reused_image_count"] == 4
    assert report["reused_evaluator_count"] == 12
    assert report["review_pairs"] == 2
    assert report["reviewed_images"] == 4
    assert report["review_display"]["display_check"] == "PASS"
    assert report["decision"] == "STOP_FOR_USER_DEV_REVIEW"


def test_reuse_only_human_review_records_two_a_only_pass_pairs():
    report = json.loads(REUSE_HUMAN_RESULT.read_text(encoding="utf-8"))
    assert report["reviewed_pairs"] == 2
    assert report["reviewed_images"] == 4
    assert [row["result"] for row in report["pair_results"]] == ["A_ONLY_PASS", "A_ONLY_PASS"]
    assert report["summary"]["a_only_pass_pairs"] == 2
    assert report["summary"]["decision"] == "HOLD_FOR_DEV_PHASE2_CLOSE"


def test_generation_batch_is_bounded_and_keeps_review_display_separate():
    with BATCH_MANIFEST.open(encoding="utf-8-sig", newline="") as stream:
        cases = list(csv.DictReader(stream))
    assert len(cases) == 3
    assert len(cases) * 4 == 12
    validate_cases(cases, load_profiles())
    report = json.loads(BATCH_RESULT.read_text(encoding="utf-8"))
    assert report["status"] == "BATCH_COMPLETE_REVIEW_REQUIRED"
    assert report["new_images_generated"] == 12
    assert report["reused_images"] == 0
    assert report["evaluator_runs"] == 36
    assert report["review_pairs"] == 6
    assert report["reviewed_images"] == 12
    assert report["blocked_count"] == 0
    assert report["review_display"]["display_check"] == "PASS"
    assert report["review_display"]["question_font_px"] >= 24


def test_generation_batch_human_review_records_ambiguous_multi_special_identity():
    report = json.loads(BATCH_HUMAN_RESULT.read_text(encoding="utf-8"))
    assert report["reviewed_pairs"] == 6
    assert report["reviewed_images"] == 12
    assert report["new_images"] == 0
    assert report["summary"]["both_pass_pairs"] == 4
    assert report["summary"]["unclear_pairs"] == 2
    assert [row["result"] for row in report["pair_results"][:2]] == ["UNCLEAR", "UNCLEAR"]
    assert report["summary"]["decision"] == "HOLD_FOR_DEV_PHASE2_CLOSE"


def test_generation_batch2_is_machine_first_bounded_and_repair_audited():
    with BATCH2_MANIFEST.open(encoding="utf-8-sig", newline="") as stream:
        cases = list(csv.DictReader(stream))
    assert len(cases) == 4
    assert len(cases) * 4 == 16
    validate_cases(cases, load_profiles())
    report = json.loads(BATCH2_RESULT.read_text(encoding="utf-8"))
    assert report["status"] == "BATCH2_COMPLETE_MACHINE_FIRST_REVIEW_REQUIRED"
    assert report["generated_images"] == 16
    assert report["planned_evaluator_runs"] == report["actual_successful_evaluator_runs"] == 48
    assert report["actual_failed_or_missing_evaluator_runs"] == 0
    assert report["per_evaluator_successes"] == {"wd14": 16, "kagami": 16, "cl_v2_00": 16}
    assert report["evaluator_reference_integrity_check"] == "PASS"
    assert report["raw_artifact_image_binding_check"] == "PASS"
    assert report["original_report_reference_integrity_check"] == "FAIL"
    assert report["original_report_reference_mismatches"] == 45
    assert report["reporting_reference_repair_applied"] is True
    assert report["ab_marker_integrity_check"] == "PASS"
    assert report["machine_handled_images"] == 4
    assert report["machine_handled_pairs"] == 2
    assert report["human_required_images"] == 12
    assert report["human_required_pairs"] == 6
    assert report["blocked_images"] == report["blocked_pairs"] == 0
    assert report["image_level_review_reduction_percent"] == report["pair_level_review_reduction_percent"] == 25.0
    assert report["review_display"]["display_check"] == "PASS"


def test_machine_triage_audit_proves_raw_outputs_and_records_reporting_defect():
    report = json.loads(TRIAGE_AUDIT.read_text(encoding="utf-8"))
    assert report["new_images"] == 0
    assert report["actual_successful_evaluator_runs"] == 36
    assert report["actual_failed_or_missing_evaluator_runs"] == 0
    assert report["per_evaluator_successes"] == {"wd14": 12, "kagami": 12, "cl_v2_00": 12}
    assert report["raw_artifact_image_binding_check"] == "PASS"
    assert report["reported_reference_integrity_check"] == "FAIL"
    assert len(report["reported_reference_mismatches"]) == 33
    assert report["ab_marker_integrity_check"] == "PASS"
    assert report["machine_handled_images"] == 0
    assert report["human_required_images"] == 12
    assert report["human_review_reduction_percent"] == 0.0


def _routing_fixture(route_class="MACHINE", condition="A", image_id="X__a", case_id="X"):
    return {
        "image_id": image_id,
        "case_id": case_id,
        "cell_type": "target_present_seed_a" if condition == "A" else "contrast_seed_a",
        "condition": condition,
        "generation": {"seed": 1},
        "case": {"relation_binding_required": "false"},
        "screening": {"screening_classes": [] if route_class == "MACHINE" else ["RELATION_OR_BINDING"], "desk_relation_sensitive": route_class == "HUMAN", "high_confidence_eligible": route_class == "MACHINE"},
        "evaluators": {"wd14": {"execution_state": "OK"}, "kagami": {"execution_state": "OK"}, "cl_v2_00": {"execution_state": "OK"}},
    }


def test_machine_first_pair_routing_regression_covers_machine_human_blocked_and_marker_mismatch():
    machine_a = _routing_fixture(condition="A", image_id="X__target_present_seed_a")
    machine_b = _routing_fixture(condition="B", image_id="X__contrast_seed_a")
    for row in (machine_a, machine_b):
        row["machine_route"], row["route_reasons"] = route_image(row, provenance_pass=True)
    assert pair_routes([machine_a, machine_b][0:2])[("X", 1)]["route"] == "MACHINE_HANDLED_PAIR"
    human_a = _routing_fixture(route_class="HUMAN", condition="A", image_id="Y__target_present_seed_a", case_id="Y")
    human_b = _routing_fixture(route_class="HUMAN", condition="B", image_id="Y__contrast_seed_a", case_id="Y")
    for row in (human_a, human_b):
        row["machine_route"], row["route_reasons"] = route_image(row, provenance_pass=True)
    assert pair_routes([human_a, human_b])[("Y", 1)]["route"] == "HUMAN_REVIEW_REQUIRED_PAIR"
    blocked = _routing_fixture(condition="A", image_id="Z__target_present_seed_a", case_id="Z")
    blocked["machine_route"], blocked["route_reasons"] = route_image(blocked, provenance_pass=False)
    blocked_b = _routing_fixture(condition="B", image_id="Z__contrast_seed_a", case_id="Z")
    blocked_b["machine_route"], blocked_b["route_reasons"] = route_image(blocked_b, provenance_pass=True)
    assert pair_routes([blocked, blocked_b])[("Z", 1)]["route"] == "BLOCKED_PAIR"
    assert marker_integrity([machine_a, machine_b]) == (True, [])
    bad = dict(machine_b)
    bad["condition"] = "A"
    assert marker_integrity([machine_a, bad])[0] is False
