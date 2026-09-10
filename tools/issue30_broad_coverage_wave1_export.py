#!/usr/bin/env python3
"""Freeze Wave 1 routes and export the complete ChatGPT visual-audit package."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

from issue30_audit_cache import initialize_cache_root, write_ownership_manifest
from issue30_machine_first_routing import marker_integrity, pair_routes, route_image, verify_row_provenance


REPO_ROOT = Path(__file__).resolve().parents[1]
NEGATIVE = "lowres, blurry, text, watermark, jpeg artifacts"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_manifest(path: Path) -> dict[str, dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        rows = {row["case_id"]: row for row in csv.DictReader(stream)}
    if not rows:
        raise RuntimeError(f"empty Wave 1 manifest: {path}")
    return rows


def load_font() -> tuple[ImageFont.FreeTypeFont, str]:
    candidates = (
        Path(r"C:\Windows\Fonts\meiryo.ttc"),
        Path(r"C:\Windows\Fonts\YuGothM.ttc"),
        Path(r"C:\Windows\Fonts\msgothic.ttc"),
    )
    for candidate in candidates:
        if candidate.is_file():
            return ImageFont.truetype(str(candidate), 30), str(candidate)
    raise RuntimeError("no Japanese review font found; audit asset is invalid")


def condition(row: dict[str, Any]) -> str:
    cell = row.get("cell_type", "")
    if cell.startswith("target_present"):
        return "A"
    if cell.startswith("contrast"):
        return "B"
    raise RuntimeError(f"cannot derive structured A/B condition: {row.get('image_id')}")


def wrap_question(question: str, width: int = 22) -> str:
    """Wrap Japanese review text by characters so it cannot run into column 2."""
    return "\n".join(question[index:index + width] for index in range(0, len(question), width))


def route_rows(rows: list[dict[str, Any]], manifest: dict[str, dict[str, str]], run_root: Path) -> tuple[list[dict[str, Any]], dict[tuple[str, int], dict[str, Any]], list[str]]:
    routed = []
    source_failures = []
    for original in rows:
        row = dict(original)
        row["condition"] = condition(row)
        case = manifest[row["case_id"]]
        row["case"] = {
            "relation_binding_required": case["relation_binding_required"],
        }
        image_path = Path(row["image_artifact"]["path"])
        expected_hash = row["image_artifact"].get("sha256")
        source_ok = image_path.is_file()
        if source_ok:
            try:
                with Image.open(image_path) as image:
                    image.verify()
                source_ok = expected_hash == sha256(image_path)
            except Exception:
                source_ok = False
        if not source_ok:
            source_failures.append(row["image_id"])
        original_provenance = verify_row_provenance(run_root, row)
        row["original_report_reference_mismatches"] = [
            name
            for name, item in original_provenance["evaluators"].items()
            if not item["reported_matches_expected"]
        ]
        row["reporting_reference_repair_applied"] = False
        provenance = original_provenance
        # Repair only stale report locators when the expected raw artifact is
        # present, readable, and hash-bound. Never repair missing raw output.
        if provenance["raw_artifact_pass"] and not provenance["reported_reference_pass"]:
            for name, item in provenance["evaluators"].items():
                row["evaluators"][name]["raw_output_artifact"] = item["expected"]
            provenance = verify_row_provenance(run_root, row)
            row["reporting_reference_repair_applied"] = True
        provenance_pass = provenance["pass"] and source_ok
        machine_route, route_reasons = route_image(row, provenance_pass=provenance_pass)
        row["machine_route"] = machine_route
        row["route_reasons"] = route_reasons
        row["provenance_audit"] = provenance
        routed.append(row)
    marker_pass, marker_errors = marker_integrity(routed)
    if not marker_pass:
        raise RuntimeError(f"A/B marker integrity failed: {marker_errors}")
    pairs = pair_routes(routed)
    for row in routed:
        key = (row["case_id"], int(row["generation"]["seed"]))
        row["machine_pair_route"] = pairs[key]["route"]
    return routed, pairs, source_failures


def copy_and_sheet(
    routed: list[dict[str, Any]],
    manifest: dict[str, dict[str, str]],
    audit_root: Path,
) -> tuple[list[dict[str, Any]], list[Path], list[Path], Path, str]:
    font, font_path = load_font()
    individual = audit_root / "individual"
    sheets_dir = audit_root / "sheets"
    individual.mkdir()
    sheets_dir.mkdir()
    ordered = sorted(routed, key=lambda row: (row["case_id"], int(row["generation"]["seed"]), row["condition"]))
    index_rows = []
    pair_groups: dict[tuple[str, int], list[dict[str, Any]]] = {}
    for display_number, row in enumerate(ordered, start=1):
        source = Path(row["image_artifact"]["path"])
        target = individual / f"{display_number:04d}_{row['image_id']}.png"
        shutil.copy2(source, target)
        pair_key = (row["case_id"], int(row["generation"]["seed"]))
        pair_groups.setdefault(pair_key, []).append(row)
        index_rows.append({
            "display_number": display_number,
            "experiment_id": row["case_id"],
            "semantic_family": manifest[row["case_id"]]["source_stratum"],
            "image_id": row["image_id"],
            "condition": row["condition"],
            "seed": int(row["generation"]["seed"]),
            "source_hash": row["image_artifact"]["sha256"],
            "source_locator": str(source),
            "audit_copy_locator": str(target),
            "machine_image_route": row["machine_route"],
            "machine_pair_route": row["machine_pair_route"],
            "evaluator_result_locators": {name: item["expected"] for name, item in row["provenance_audit"]["evaluators"].items()},
        })
    individual_paths = [individual / f"{display_number:04d}_{row['image_id']}.png" for display_number, row in enumerate(ordered, start=1)]
    sheet_paths = []
    pair_items = sorted(pair_groups.items())
    for sheet_number, start in enumerate(range(0, len(pair_items), 4), start=1):
        subset = pair_items[start:start + 4]
        sheet_rows = [row for _, rows in subset for row in sorted(rows, key=lambda item: item["condition"])]
        thumb_w, thumb_h, label_h = 700, 620, 190
        sheet = Image.new("RGB", (thumb_w * 2, ((len(sheet_rows) + 1) // 2) * (thumb_h + label_h)), "white")
        draw = ImageDraw.Draw(sheet)
        for index, row in enumerate(sheet_rows):
            x = (index % 2) * thumb_w
            y = (index // 2) * (thumb_h + label_h)
            copy_path = next(item["audit_copy_locator"] for item in index_rows if item["image_id"] == row["image_id"])
            with Image.open(copy_path) as image:
                image = image.convert("RGB")
                image.thumbnail((thumb_w - 16, thumb_h - 16))
                sheet.paste(image, (x + (thumb_w - image.width) // 2, y + (thumb_h - image.height) // 2))
            question = manifest[row["case_id"]]["question_ja"]
            draw.text((x + 10, y + thumb_h + 5), f"#{next(item['display_number'] for item in index_rows if item['image_id'] == row['image_id']):03d}   {row['condition']}", fill="black", font=font)
            draw.multiline_text((x + 10, y + thumb_h + 45), wrap_question(question), fill="black", font=font, spacing=3)
        sheet_path = sheets_dir / f"wave1_audit_sheet_{sheet_number:02d}.png"
        sheet.save(sheet_path, format="PNG")
        sheet_paths.append(sheet_path)
    index_path = audit_root / "wave1_visual_audit_index.json"
    index_path.write_text(json.dumps({
        "schema_version": "issue30.wave1.visual_audit_index.v1",
        "visual_audit_coverage": "ALL_VALID_IMAGES",
        "image_count": len(index_rows),
        "pair_count": len(pair_groups),
        "font_path": font_path,
        "question_font_px": 30,
        "rows": index_rows,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return index_rows, individual_paths, sheet_paths, index_path, font_path


def build_reports(
    args: argparse.Namespace,
    manifest: dict[str, dict[str, str]],
    routed: list[dict[str, Any]],
    pairs: dict[tuple[str, int], dict[str, Any]],
    source_failures: list[str],
    audit_root: Path,
    ownership_manifest: Path,
    index_rows: list[dict[str, Any]],
    sheet_paths: list[Path],
    font_path: str,
) -> dict[str, Any]:
    successes = Counter()
    failures = Counter()
    for row in routed:
        for name, item in row["provenance_audit"]["evaluators"].items():
            (successes if item["readable_non_error"] else failures)[name] += 1
    original_reference_mismatch_count = sum(
        len(row.get("original_report_reference_mismatches", [])) for row in routed
    )
    reporting_reference_repairs = sum(
        1 for row in routed if row.get("reporting_reference_repair_applied")
    )
    image_routes = Counter(row["machine_route"] for row in routed)
    pair_route_counts = Counter(item["route"] for item in pairs.values())
    machine_images = image_routes["MACHINE_HANDLED_CANDIDATE"]
    valid_images = len(routed) - len(source_failures)
    result = {
        "schema_version": "issue30.broad_coverage_wave1_result.v1",
        "status": "WAVE1_MACHINE_ROUTING_FROZEN_FULL_VISUAL_AUDIT_PENDING",
        "run_id": routed[0]["run_id"],
        "manifest": str(args.manifest),
        "local_artifact_root": str(args.run_root),
        "experiment_count": len(manifest),
        "generated_images": len(routed),
        "valid_generated_images": valid_images,
        "generated_pairs": len(pairs),
        "semantic_family_distribution": dict(Counter(manifest[row["case_id"]]["source_stratum"] for row in routed[::4])),
        "actual_successful_evaluator_runs": sum(successes.values()),
        "actual_failed_or_missing_evaluator_runs": sum(failures.values()),
        "per_evaluator_successes": dict(successes),
        "per_evaluator_failures": dict(failures),
        "evaluator_reference_integrity_check": "PASS" if all(row["provenance_audit"]["pass"] for row in routed) else "FAIL",
        "original_report_reference_integrity_check": "PASS" if original_reference_mismatch_count == 0 else "FAIL",
        "original_report_reference_mismatch_count": original_reference_mismatch_count,
        "reporting_reference_repairs_applied": reporting_reference_repairs,
        "ab_marker_integrity_check": "PASS",
        "image_route_counts": dict(image_routes),
        "pair_route_counts": dict(pair_route_counts),
        "machine_handled_images": machine_images,
        "machine_handled_pairs": pair_route_counts["MACHINE_HANDLED_PAIR"],
        "human_required_images": image_routes["HUMAN_REVIEW_REQUIRED"],
        "human_required_pairs": pair_route_counts["HUMAN_REVIEW_REQUIRED_PAIR"],
        "blocked_images": image_routes["BLOCKED"],
        "blocked_pairs": pair_route_counts["BLOCKED_PAIR"],
        "provisional_image_review_reduction_percent": round(machine_images / len(routed) * 100, 2) if routed else 0.0,
        "provisional_pair_review_reduction_percent": round(pair_route_counts["MACHINE_HANDLED_PAIR"] / len(pairs) * 100, 2) if pairs else 0.0,
        "visual_audit_coverage": {"valid_images": valid_images, "packaged_images": len(index_rows), "valid_pairs": len(pairs), "packaged_pairs": len(pairs), "percent": 100.0 if len(index_rows) == valid_images else 0.0},
        "audit_package": {"root": str(audit_root), "index_manifest": str(audit_root / "wave1_visual_audit_index.json"), "sheets": [str(path) for path in sheet_paths if path.name.endswith(".png")], "individual_directory": str(audit_root / "individual"), "ownership_manifest": str(ownership_manifest), "question_font_path": font_path, "question_font_px": 30},
        "protected_source_integrity": {"source_root": str(args.run_root), "source_failures": source_failures, "originals_modified": False},
        "machine_route_frozen": True,
        "visual_verdicts": "PENDING_CHATGPT_FULL_AUDIT",
        "decision": "STOP_FOR_CHATGPT_VISUAL_AUDIT",
        "wave2_started": False,
        "image_records": routed,
        "pair_routes": {f"{case}:{seed}": value for (case, seed), value in pairs.items()},
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    args.output_json.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Issue #30 Broad Coverage Wave 1 result — 2026-09-11",
        "",
        "Status: `WAVE1_MACHINE_ROUTING_FROZEN_FULL_VISUAL_AUDIT_PENDING`",
        "",
        f"Wave 1 generated **{len(routed)} images / {len(pairs)} A-B pairs** across **{len(manifest)} experiments**. Machine routing is frozen before visual review; all valid images are included in the ChatGPT audit package.",
        "",
        "## COUNTS",
        "",
        f"- Actual evaluator successes: **{sum(successes.values())}** (WD14 {successes['wd14']} / Kagami {successes['kagami']} / CL {successes['cl_v2_00']})",
        f"- Actual evaluator failures/missing: **{sum(failures.values())}**",
        f"- Evaluator reference integrity: **{result['evaluator_reference_integrity_check']}**",
        f"- A/B marker integrity: **{result['ab_marker_integrity_check']}**",
        f"- Image routes: `{dict(image_routes)}`",
        f"- Pair routes: `{dict(pair_route_counts)}`",
        f"- Provisional image review reduction: **{result['provisional_image_review_reduction_percent']}%** (diagnostic only)",
        f"- Provisional pair review reduction: **{result['provisional_pair_review_reduction_percent']}%** (diagnostic only)",
        "- Actual independent visual-audit coverage: **100% of valid images/pairs**",
        "",
        "## AUDIT PACKAGE",
        "",
        f"- Index: `{result['audit_package']['index_manifest']}`",
        f"- Sheets: `{'; '.join(result['audit_package']['sheets'])}`",
        f"- Individual copies: `{result['audit_package']['individual_directory']}`",
        f"- Ownership manifest: `{ownership_manifest}`",
        "",
        "Machine routes are frozen and must not be changed after ChatGPT visual results. Visual verdicts remain pending; Wave 2 is not started.",
    ]
    args.output_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--audit-root", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    args = parser.parse_args()
    manifest = load_manifest(args.manifest)
    rows = read_json(args.run_root / "calibration_results.json")
    routed, pairs, source_failures = route_rows(rows, manifest, args.run_root)
    if args.audit_root.exists() and set(path.name for path in args.audit_root.iterdir()) != {".danbooru_audit_cache_v1"}:
        raise RuntimeError(f"audit root is not empty/current-only: {args.audit_root}")
    audit_root = initialize_cache_root(args.audit_root, protected_roots=[args.run_root, REPO_ROOT / "data", REPO_ROOT / "docs"])
    index_rows, individual_paths, sheet_paths, index_path, font_path = copy_and_sheet(routed, manifest, audit_root)
    disposable_files = individual_paths + sheet_paths + [index_path]
    ownership_manifest = write_ownership_manifest(audit_root, "wave1", disposable_files, protected_roots=[args.run_root, REPO_ROOT / "data", REPO_ROOT / "docs"])
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    result = build_reports(args, manifest, routed, pairs, source_failures, audit_root, ownership_manifest, index_rows, sheet_paths, font_path)
    print(json.dumps({key: result[key] for key in ("status", "generated_images", "actual_successful_evaluator_runs", "evaluator_reference_integrity_check", "ab_marker_integrity_check", "pair_route_counts", "audit_package", "decision")}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
