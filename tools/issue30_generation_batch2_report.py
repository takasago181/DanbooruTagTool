#!/usr/bin/env python3
"""Verify Batch 2 evaluator artifacts, route images/pairs, and build the human-only sheet."""
from __future__ import annotations

import argparse
import csv
import json
import textwrap
from collections import Counter
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

from issue30_machine_first_routing import marker_integrity, pair_routes, route_image, verify_row_provenance
from issue30_phase2_wave_report import label_font


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_manifest(path: Path) -> dict[str, dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return {row["case_id"]: row for row in csv.DictReader(stream)}


def wrap(value: str, width: int = 22) -> str:
    return "\n".join(textwrap.wrap(value, width=width, break_long_words=True, break_on_hyphens=True))


def make_contact_sheet(rows: list[dict[str, Any]], manifest: dict[str, dict[str, str]], output: Path) -> dict[str, Any] | None:
    if not rows:
        return None
    ordered = sorted(rows, key=lambda row: (row["case_id"], row["seed"], row["condition"]))
    thumb_w, thumb_h, label_h = 700, 620, 190
    sheet = Image.new("RGB", (thumb_w * 2, ((len(ordered) + 1) // 2) * (thumb_h + label_h)), "white")
    draw = ImageDraw.Draw(sheet)
    font, font_path, font_valid = label_font()
    question_font = ImageFont.truetype(font_path, 30) if font_valid else font
    for index, row in enumerate(ordered):
        x = (index % 2) * thumb_w
        y = (index // 2) * (thumb_h + label_h)
        with Image.open(row["image_path"]) as image:
            image = image.convert("RGB")
            image.thumbnail((thumb_w - 16, thumb_h - 16))
            sheet.paste(image, (x + (thumb_w - image.width) // 2, y + (thumb_h - image.height) // 2))
        draw.text((x + 10, y + thumb_h + 5), f"#{index + 1:02d}   {row['condition']}   seed={row['seed']}", fill="black", font=question_font)
        draw.multiline_text((x + 10, y + thumb_h + 45), wrap(manifest[row["case_id"]]["question_ja"]), fill="black", font=question_font, spacing=4)
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output, format="PNG")
    return {"font_path": font_path, "question_font_px": 30, "display_check": "PASS" if font_valid else "FAIL", "question_sample": manifest[ordered[0]["case_id"]]["question_ja"]}


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Issue #30 Phase 2 Generation Batch 2 result — 2026-09-11",
        "",
        "## RESULT",
        "",
        "Status: `BATCH2_COMPLETE_MACHINE_FIRST_REVIEW_REQUIRED`",
        "",
        f"Batch 2 completed with {report['generated_images']} new images. Evaluator provenance and routing were verified after generation; only human-required pairs are placed on the contact sheet.",
        "",
        "## COUNTS",
        "",
        f"- Planned evaluator runs: **{report['planned_evaluator_runs']}**",
        f"- Actual successful evaluator runs: **{report['actual_successful_evaluator_runs']}**",
        f"- Failed/missing evaluator runs: **{report['actual_failed_or_missing_evaluator_runs']}**",
        f"- Per evaluator: WD14 **{report['per_evaluator_successes'].get('wd14', 0)}**, Kagami **{report['per_evaluator_successes'].get('kagami', 0)}**, CL **{report['per_evaluator_successes'].get('cl_v2_00', 0)}**",
        f"- Evaluator reference integrity: **{report['evaluator_reference_integrity_check']}**",
        f"- A/B marker integrity: **{report['ab_marker_integrity_check']}**",
        f"- Machine-handled: **{report['machine_handled_images']} images / {report['machine_handled_pairs']} pairs**",
        f"- Human-required: **{report['human_required_images']} images / {report['human_required_pairs']} pairs**",
        f"- Blocked: **{report['blocked_images']} images / {report['blocked_pairs']} pairs**",
        f"- Image-level review reduction: **{report['image_level_review_reduction_percent']}%**",
        f"- Pair-level review reduction: **{report['pair_level_review_reduction_percent']}%**",
        "",
        "## ROUTING",
        "",
        "Pair routing is computed from the two image routes. A pair stays complete for human comparison when either A or B is human-required.",
        "",
        "| Pair | Route | Image routes | Reasons |",
        "|---|---|---|---|",
    ]
    for key, item in sorted(report["pair_routes"].items()):
        lines.append(f"| `{key}` | `{item['route']}` | `{', '.join(item['image_routes'])}` | {'; '.join(item['reasons'])} |")
    lines += [
        "",
        "## REVIEW",
        "",
        f"Human-required contact sheet: `{report.get('contact_sheet') or 'not required; all pairs machine-handled'}`",
        f"Japanese font: `{(report.get('review_display') or {}).get('font_path', 'not required')}`; display check: **{(report.get('review_display') or {}).get('display_check', 'not required')}**.",
        "",
        "Machine-handled pairs are intentionally excluded from the mandatory user sheet. Detailed prompts, negatives, seeds, evaluator references, hashes, and per-image routing remain in the JSON result.",
        "",
        "## DECISION / LIMITATION / NEXT",
        "",
        "Machine triage remains narrow support only; it does not authorize relation, binding, body-site, count, actor-role, or compound semantic truth. Review the human-required pairs, then stop for DEV/ChatGPT Phase 2 close judgment. Do not add seeds or start Stage10 automatically.",
        "",
        f"Local-only artifact root: `{report['local_artifact_root']}`",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    parser.add_argument("--contact-sheet", type=Path, required=True)
    args = parser.parse_args()
    manifest = load_manifest(args.manifest)
    results = read_json(args.run_root / "calibration_results.json")
    records = []
    per_success = Counter()
    per_failure = Counter()
    for result in results:
        if result["case_id"] not in manifest:
            continue
        provenance = verify_row_provenance(args.run_root, result)
        condition = "A" if result["cell_type"].startswith("target_present") else "B"
        route, reasons = route_image({**result, "case": manifest[result["case_id"]]}, provenance["pass"])
        for name, item in provenance["evaluators"].items():
            (per_success if item["readable_non_error"] else per_failure)[name] += 1
        records.append({
            "image_id": result["image_id"], "case_id": result["case_id"], "condition": condition, "seed": result["generation"]["seed"],
            "image_path": result["image_artifact"]["path"], "sha256": result["image_artifact"]["sha256"], "bytes": result["image_artifact"]["bytes"],
            "screening_classes": result["screening"]["screening_classes"], "machine_route": route, "route_reasons": reasons,
            "provenance": provenance, "evaluators": result["evaluators"], "generation": result["generation"],
        })
    marker_pass, marker_errors = marker_integrity(records)
    pair_input = [{**result, "condition": "A" if result["cell_type"].startswith("target_present") else "B", "machine_route": record["machine_route"]} for result, record in zip([r for r in results if r["case_id"] in manifest], records)]
    pairs = pair_routes(pair_input)
    pair_key = {f"{key[0]}:{key[1]}": value for key, value in pairs.items()}
    machine_images = sum(row["machine_route"] == "MACHINE_HANDLED_CANDIDATE" for row in records)
    human_images = sum(row["machine_route"] == "HUMAN_REVIEW_REQUIRED" for row in records)
    blocked_images = sum(row["machine_route"] == "BLOCKED" for row in records)
    machine_pairs = sum(item["route"] == "MACHINE_HANDLED_PAIR" for item in pairs.values())
    human_pairs = sum(item["route"] == "HUMAN_REVIEW_REQUIRED_PAIR" for item in pairs.values())
    blocked_pairs = sum(item["route"] == "BLOCKED_PAIR" for item in pairs.values())
    review_rows = [row for row in records if pairs[(row["case_id"], int(row["seed"]))]["route"] == "HUMAN_REVIEW_REQUIRED_PAIR"]
    display = make_contact_sheet(review_rows, manifest, args.contact_sheet)
    reference_failures = [row for row in records for item in row["provenance"]["evaluators"].values() if not item["reported_matches_expected"]]
    report = {
        "schema_version": "issue30.phase2.generation_batch2_result.v1", "status": "BATCH2_COMPLETE_MACHINE_FIRST_REVIEW_REQUIRED",
        "run_id": results[0]["run_id"], "manifest": str(args.manifest), "local_artifact_root": str(args.run_root),
        "generated_images": sum(not bool(row.get("reused", False)) for row in read_json(args.run_root / "generation_records.json")), "reused_images": 0,
        "planned_evaluator_runs": len(records) * 3, "actual_successful_evaluator_runs": sum(per_success.values()), "actual_failed_or_missing_evaluator_runs": sum(per_failure.values()),
        "per_evaluator_successes": dict(per_success), "per_evaluator_failures": dict(per_failure),
        "evaluator_reference_integrity_check": "PASS" if not reference_failures and all(item["provenance"]["pass"] for item in records) else "FAIL",
        "reference_failures": reference_failures, "ab_marker_integrity_check": "PASS" if marker_pass else "FAIL", "ab_marker_errors": marker_errors,
        "machine_handled_images": machine_images, "machine_handled_pairs": machine_pairs, "human_required_images": human_images, "human_required_pairs": human_pairs,
        "blocked_images": blocked_images, "blocked_pairs": blocked_pairs, "image_level_review_reduction_percent": round(machine_images / len(records) * 100, 2),
        "pair_level_review_reduction_percent": round(machine_pairs / len(pairs) * 100, 2), "pair_routes": pair_key,
        "contact_sheet": str(args.contact_sheet) if display else None, "review_display": display, "image_records": records, "decision": "HOLD_FOR_HUMAN_REVIEW",
    }
    write_json(args.output_json, report)
    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.write_text(markdown(report), encoding="utf-8")
    print(json.dumps({"status": report["status"], "generated_images": report["generated_images"], "actual_successful_evaluator_runs": report["actual_successful_evaluator_runs"], "machine_handled_pairs": machine_pairs, "human_required_pairs": human_pairs, "blocked_pairs": blocked_pairs, "image_reduction_percent": report["image_level_review_reduction_percent"], "pair_reduction_percent": report["pair_level_review_reduction_percent"], "reference_integrity": report["evaluator_reference_integrity_check"], "ab_marker_integrity": report["ab_marker_integrity_check"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
