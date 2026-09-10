#!/usr/bin/env python3
"""Create repository summaries and an A/B contact sheet for a Phase 2 wave."""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

from issue30_phase2_analysis import artifact_gate


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "docs/testing/ISSUE30_PHASE2_TEST_MANIFEST.csv"
JA_FONT_CANDIDATES = (
    Path(r"C:\Windows\Fonts\meiryo.ttc"),
    Path(r"C:\Windows\Fonts\YuGothM.ttc"),
    Path(r"C:\Windows\Fonts\msgothic.ttc"),
)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_manifest(path: Path) -> dict[str, dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    return {row["case_id"]: row for row in rows}


def label_font() -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in JA_FONT_CANDIDATES:
        if path.is_file():
            try:
                return ImageFont.truetype(str(path), 14)
            except OSError:
                continue
    return ImageFont.load_default()


def make_contact_sheet(rows: list[dict[str, Any]], output: Path, canonical_ja: dict[str, str]) -> None:
    ordered = sorted(rows, key=lambda row: (row["case_id"], row["generation"]["seed"], row["cell_type"]))
    thumb_w, thumb_h, label_h = 384, 384, 70
    cols = 2
    sheet = Image.new("RGB", (cols * thumb_w, ((len(ordered) + 1) // 2) * (thumb_h + label_h)), "white")
    draw = ImageDraw.Draw(sheet)
    font = label_font()
    for index, row in enumerate(ordered):
        x = (index % cols) * thumb_w
        y = (index // cols) * (thumb_h + label_h)
        with Image.open(row["image_artifact"]["path"]) as image:
            image = image.convert("RGB")
            image.thumbnail((thumb_w - 8, thumb_h - 8))
            sheet.paste(image, (x + (thumb_w - image.width) // 2, y + (thumb_h - image.height) // 2))
        condition = "A" if row["cell_type"].startswith("target_present") else "B"
        label = f"#{index + 1:02d}  {row['case_id']}  {condition}  seed={row['generation']['seed']}\n{row['canonical']}\n{canonical_ja.get(row['case_id'], '')}"
        draw.multiline_text((x + 6, y + thumb_h + 3), label, fill="black", font=font, spacing=2)
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output, format="PNG")


def build_report(run_root: Path, manifest_path: Path, contact_sheet: Path, generated_count: int | None = None) -> dict[str, Any]:
    manifest = load_manifest(manifest_path)
    results = read_json(run_root / "calibration_results.json")
    generation = read_json(run_root / "generation_records.json")
    generation_by_id = {row["image_id"]: row for row in generation}
    image_rows = []
    for row in results:
        generation_row = generation_by_id[row["image_id"]]
        gate = artifact_gate(row)
        image_rows.append({
            "image_id": row["image_id"],
            "case_id": row["case_id"],
            "canonical": row["canonical"],
            "canonical_ja": manifest[row["case_id"]].get("canonical_ja", ""),
            "cell_type": row["cell_type"],
            "seed": row["generation"]["seed"],
            "prompt": row["generation"]["prompt"],
            "negative_prompt": row["generation"]["negative_prompt"],
            "sha256": row["image_artifact"]["sha256"],
            "bytes": row["image_artifact"]["bytes"],
            "width": row["image_artifact"]["width"],
            "height": row["image_artifact"]["height"],
            "image_path": row["image_artifact"]["path"],
            "reused": bool(generation_row.get("reused", False)),
            "artifact_gate": gate,
            "screening_classes": row["screening"]["screening_classes"],
            "agreement_pattern": row["evaluator_agreement"]["agreement_class"],
            "selected_for_human_review": row["human_review_selection"]["selected_for_human_review"],
            "experiment_validity": "PENDING_HUMAN_REVIEW",
        })
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in image_rows:
        grouped[row["case_id"]].append(row)
    experiments = []
    for case_id, case in manifest.items():
        case_rows = sorted(grouped[case_id], key=lambda row: (row["seed"], row["cell_type"]))
        classes = Counter(cls for row in case_rows for cls in row["screening_classes"])
        experiments.append({
            "case_id": case_id,
            "special_ids": [int(value) for value in case["special_ids"].split("|")],
            "canonical": case["canonical"],
            "canonical_ja": case.get("canonical_ja", ""),
            "question": case["question"],
            "condition_a": {"prompt": case["target_prompt"], "negative_prompt": case["target_negative_prompt"]},
            "condition_b": {"prompt": case["contrast_prompt"], "negative_prompt": case["contrast_negative_prompt"]},
            "seeds": [int(case["seed_a"]), int(case["seed_b"])],
            "image_count": len(case_rows),
            "artifact_gate": dict(Counter(row["artifact_gate"]["status"] for row in case_rows)),
            "screening_class_occurrences": dict(classes),
            "human_review_image_ids": [row["image_id"] for row in case_rows if row["selected_for_human_review"]],
            "experiment_validity": "PENDING_HUMAN_REVIEW",
        })
    settings = results[0]["generation"]
    return {
        "schema_version": "issue30.phase2.wave1_result.v1",
        "status": "FIRST_WAVE_COMPLETE_REVIEW_REQUIRED",
        "run_id": results[0]["run_id"],
        "manifest": str(manifest_path),
        "local_artifact_root": str(run_root),
        "review_asset": str(contact_sheet),
        "image_count": len(image_rows),
        "new_images_generated": generated_count if generated_count is not None else sum(not row["reused"] for row in image_rows),
        "screen_only_reused_images": sum(row["reused"] for row in image_rows),
        "evaluator_runs": len(image_rows) * 3,
        "evaluator_complete_images": sum(
            all(item["execution_state"] == "OK" for item in source["evaluators"].values())
            for source in results
        ),
        "artifact_gate": dict(Counter(row["artifact_gate"]["status"] for row in image_rows)),
        "experiment_validity": {"status": "PENDING_HUMAN_REVIEW", "failures_recorded": 0},
        "screening_class_occurrences": dict(Counter(cls for row in image_rows for cls in row["screening_classes"])),
        "human_review_image_count": sum(row["selected_for_human_review"] for row in image_rows),
        "human_review_image_ids": [row["image_id"] for row in image_rows if row["selected_for_human_review"]],
        "generation_profile": {
            "model_family": settings["model_family"],
            "checkpoint": settings["checkpoint"],
            "checkpoint_hash": settings["checkpoint_hash"],
            "forge_version": settings["forge_version"],
            "sampler": settings["sampler"],
            "steps": settings["steps"],
            "cfg": settings["cfg"],
            "resolution": settings["resolution"],
            "lora": settings["lora"],
        },
        "experiments": experiments,
        "image_records": image_rows,
        "decision": {
            "device_contact": "HOLD_HUMAN_REVIEW_REQUIRED",
            "source_ownership": "HOLD_HUMAN_REVIEW_REQUIRED",
            "negative_collision": "HOLD_HUMAN_REVIEW_REQUIRED",
            "additional_generation": "STOP_UNTIL_REVIEW",
        },
    }


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Issue #30 Phase 2 first-wave result — 2026-09-10",
        "",
        "Status: `FIRST_WAVE_COMPLETE_REVIEW_REQUIRED`",
        "",
        "The bounded first wave completed with 12 new images and 36 evaluator runs. Machine screening is triage only; no structural success is inferred before human review.",
        "",
        "## Counts",
        "",
        f"- Images generated: **{report['new_images_generated']}**",
        f"- Evaluator-complete images: **{report['evaluator_complete_images']}**",
        f"- Artifact gate: **{report['artifact_gate'].get('PASS', 0)} PASS / {report['artifact_gate'].get('BLOCKED', 0)} BLOCKED**",
        f"- Human review queue: **{report['human_review_image_count']}** protected/low-confidence images",
        f"- Experiment validity: **pending human review; failures recorded 0**",
        "",
        "## Experiments",
        "",
        "| ID | Special | Question | Images | Artifact | Screening classes | Review |",
        "|---|---|---|---:|---|---|---:|",
    ]
    for item in report["experiments"]:
        classes = ", ".join(f"{key}={value}" for key, value in item["screening_class_occurrences"].items())
        artifact = ", ".join(f"{key}={value}" for key, value in item["artifact_gate"].items())
        lines.append(f"| `{item['case_id']}` | `{item['canonical']}` | {item['question']} | {item['image_count']} | {artifact} | {classes} | {len(item['human_review_image_ids'])} |")
    lines += [
        "",
        "## Generation identity",
        "",
        f"- Checkpoint: `{report['generation_profile']['checkpoint']}`",
        f"- Checkpoint hash: `{report['generation_profile']['checkpoint_hash']}`",
        f"- Forge: `{report['generation_profile']['forge_version']}`",
        f"- Sampler/schedule: `{report['generation_profile']['sampler']}` / `Automatic`",
        f"- Steps / CFG: `{report['generation_profile']['steps']}` / `{report['generation_profile']['cfg']}`",
        f"- Resolution: `{report['generation_profile']['resolution']['width']}×{report['generation_profile']['resolution']['height']}`",
        "- Hires / ADetailer / LoRA / Control / regional / Couple: OFF",
        "",
        "## User review",
        "",
        f"Review asset: `{report['review_asset']}`",
        "",
        "Review all 12 numbered A/B images in the contact sheet. For each question, compare the same seed's A and B condition and answer `A / B / both / neither / tie / unclear`. Do not inspect raw evaluator logs.",
        "",
        "## Decision and limitation",
        "",
        "All three questions remain `HOLD_HUMAN_REVIEW_REQUIRED`. P2-001 and P2-002 are relation-sensitive; evaluator agreement cannot prove device/site or ownership binding. P2-003 has not yet been judged for target realization or Negative collision. No additional seeds or experiments are authorized before review.",
        "",
        f"Local-only artifact root: `{report['local_artifact_root']}`",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output-json", type=Path, default=ROOT / "docs/testing/ISSUE30_PHASE2_WAVE1_RESULT.json")
    parser.add_argument("--output-md", type=Path, default=ROOT / "docs/testing/ISSUE30_PHASE2_WAVE1_RESULT.md")
    parser.add_argument("--contact-sheet", type=Path, default=None)
    parser.add_argument("--generated-count", type=int, default=None, help="initially generated image count when a later screen-only recheck rewrote reuse flags")
    args = parser.parse_args()
    contact_sheet = args.contact_sheet or (args.run_root / "review_queue" / "phase2_wave1_ab_contact_sheet.png")
    raw = read_json(args.run_root / "calibration_results.json")
    manifest = load_manifest(args.manifest)
    make_contact_sheet(raw, contact_sheet, {case_id: row.get("canonical_ja", "") for case_id, row in manifest.items()})
    report = build_report(args.run_root, args.manifest, contact_sheet, args.generated_count)
    write_json(args.output_json, report)
    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.write_text(markdown(report), encoding="utf-8")
    print(json.dumps({
        "status": report["status"],
        "images": report["image_count"],
        "evaluator_runs": report["evaluator_runs"],
        "artifact_gate": report["artifact_gate"],
        "human_review_images": report["human_review_image_count"],
        "contact_sheet": str(contact_sheet),
        "output_json": str(args.output_json),
        "output_md": str(args.output_md),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
