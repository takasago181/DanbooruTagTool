#!/usr/bin/env python3
"""Create the simplified user sheet and detailed traceability report for the batch."""
from __future__ import annotations

import argparse
import csv
import json
import textwrap
from collections import Counter
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

from issue30_phase2_analysis import artifact_gate
from issue30_phase2_wave_report import display_tokens, label_font, load_japanese_glossary


ROOT = Path(__file__).resolve().parents[1]


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_manifest(path: Path) -> dict[str, dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return {row["case_id"]: row for row in csv.DictReader(stream)}


def wrap(value: str, width: int = 43) -> str:
    return "\n".join(textwrap.wrap(value, width=width, break_long_words=True, break_on_hyphens=True))


def make_contact_sheet(rows: list[dict[str, Any]], manifest: dict[str, dict[str, str]], output: Path) -> dict[str, Any]:
    ordered = sorted(rows, key=lambda row: (row["case_id"], row["seed"], row["condition"]))
    thumb_w, thumb_h, label_h = 700, 620, 190
    cols = 2
    sheet = Image.new("RGB", (cols * thumb_w, ((len(ordered) + 1) // 2) * (thumb_h + label_h)), "white")
    draw = ImageDraw.Draw(sheet)
    font, font_path, font_valid = label_font()
    question_font = ImageFont.truetype(font_path, 30) if font_valid else font
    for index, row in enumerate(ordered):
        x = (index % cols) * thumb_w
        y = (index // cols) * (thumb_h + label_h)
        with Image.open(row["image_path"]) as image:
            image = image.convert("RGB")
            image.thumbnail((thumb_w - 16, thumb_h - 16))
            sheet.paste(image, (x + (thumb_w - image.width) // 2, y + (thumb_h - image.height) // 2))
        case = manifest[row["case_id"]]
        marker = f"#{index + 1:02d}   {row['condition']}   {row['case_id']}   seed={row['seed']}"
        question = wrap(case["question_ja"], 20)
        draw.text((x + 10, y + thumb_h + 5), marker, fill="black", font=question_font)
        draw.multiline_text((x + 10, y + thumb_h + 45), question, fill="black", font=question_font, spacing=4)
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output, format="PNG")
    return {"font_path": font_path, "question_font_px": 30, "display_check": "PASS" if font_valid else "FAIL", "question_sample": manifest[ordered[0]["case_id"]]["question_ja"]}


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Issue #30 Phase 2 Generation Batch Wave result — 2026-09-11",
        "",
        "## RESULT",
        "",
        "Status: `BATCH_COMPLETE_REVIEW_REQUIRED`",
        "",
        f"3 experiments completed in one bounded batch: {report['new_images_generated']} new images and {report['evaluator_runs']} evaluator runs. No automatic promotion is inferred before human review.",
        "",
        "## EVIDENCE",
        "",
        f"- New images: **{report['new_images_generated']}** / reused images: **{report['reused_images']}** / blocked: **{report['artifact_gate'].get('BLOCKED', 0)}**",
        f"- Review: **{report['review_pairs']} pairs / {report['reviewed_images']} images**",
        f"- Artifact gate: `{report['artifact_gate']}`",
        f"- Contact sheet: `{report['contact_sheet']}`",
        f"- Japanese font: `{report['review_display']['font_path']}`; display check: **{report['review_display']['display_check']}**; question font: **{report['review_display']['question_font_px']} px**",
        "",
        "| ID | Family | Special IDs | Question | Images |",
        "|---|---|---|---|---:|",
    ]
    for case in report["experiments"]:
        lines.append(f"| `{case['case_id']}` | `{case['calibration_role']}` | `{', '.join(str(x) for x in case['special_ids'])}` | {case['question_ja']} | {case['image_count']} |")
    lines += [
        "",
        "## Traceability",
        "",
        "The JSON result and manifest retain exact executed Positive/Negative prompts, English canonical tokens, Japanese display labels, seeds, settings, image hashes/paths, and evaluator references. The user-facing sheet intentionally contains only the large number, A/B marker, and concrete Japanese question.",
        "",
        "## DECISION / LIMITATION / NEXT",
        "",
        "All three families remain `HOLD_FOR_HUMAN_REVIEW`: multi-Special retention, one support tag effect, and broad-plus-specific interaction. Relation, body-site, count, and role semantics remain human-review protected. After the 6-pair review, DEV/ChatGPT decides Phase 2 close or a separately justified final experiment. Do not add seeds or start Stage10 automatically.",
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
    generation = {row["image_id"]: row for row in read_json(args.run_root / "generation_records.json")}
    rows = []
    for result in results:
        if result["case_id"] not in manifest:
            continue
        condition = "A" if result["cell_type"].startswith("target_present") else "B"
        rows.append({
            "image_id": result["image_id"], "case_id": result["case_id"], "condition": condition,
            "seed": result["generation"]["seed"], "prompt": result["generation"]["prompt"],
            "negative_prompt": result["generation"]["negative_prompt"], "image_path": result["image_artifact"]["path"],
            "sha256": result["image_artifact"]["sha256"], "bytes": result["image_artifact"]["bytes"],
            "width": result["image_artifact"]["width"], "height": result["image_artifact"]["height"],
            "artifact_gate": artifact_gate(result), "evaluator_references": {key: value.get("raw_output_artifact") for key, value in result["evaluators"].items()},
            "screening_classes": result["screening"]["screening_classes"], "reused": bool(generation[result["image_id"]].get("reused", False)),
        })
    if len(rows) != len(manifest) * 4:
        raise RuntimeError(f"expected {len(manifest) * 4} rows, found {len(rows)}")
    display = make_contact_sheet(rows, manifest, args.contact_sheet)
    glossary = load_japanese_glossary(manifest)
    experiments = []
    for case_id, case in manifest.items():
        case_rows = [row for row in rows if row["case_id"] == case_id]
        experiments.append({
            "case_id": case_id, "calibration_role": case["calibration_role"], "special_ids": [int(x) for x in case["special_ids"].split("|")],
            "canonical": case["canonical"], "canonical_ja": case["canonical_ja"], "question_ja": case["question_ja"], "image_count": len(case_rows),
            "condition_a": {"prompt": case["target_prompt"], "negative_prompt": case["target_negative_prompt"]},
            "condition_b": {"prompt": case["contrast_prompt"], "negative_prompt": case["contrast_negative_prompt"]},
            "traceability_tokens": {row["image_id"]: {"positive_ja": display_tokens(row["prompt"], glossary), "negative_ja": display_tokens(row["negative_prompt"], glossary)} for row in case_rows},
        })
    settings = results[0]["generation"]
    report = {
        "schema_version": "issue30.phase2.generation_batch_result.v1", "status": "BATCH_COMPLETE_REVIEW_REQUIRED",
        "manifest": str(args.manifest), "run_id": results[0]["run_id"], "local_artifact_root": str(args.run_root), "contact_sheet": str(args.contact_sheet),
        "new_images_generated": sum(not row["reused"] for row in rows), "reused_images": sum(row["reused"] for row in rows), "evaluator_runs": len(rows) * 3,
        "review_pairs": len({(row["case_id"], row["seed"]) for row in rows}), "reviewed_images": len(rows),
        "artifact_gate": dict(Counter(row["artifact_gate"]["status"] for row in rows)), "blocked_count": sum(row["artifact_gate"]["status"] == "BLOCKED" for row in rows),
        "review_display": display, "generation_profile": {key: settings[key] for key in ("model_family", "checkpoint", "checkpoint_hash", "forge_version", "sampler", "steps", "cfg", "resolution", "lora") if key in settings},
        "experiments": experiments, "image_records": rows, "decision": "HOLD_FOR_HUMAN_REVIEW",
    }
    write_json(args.output_json, report)
    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.write_text(markdown(report), encoding="utf-8")
    print(json.dumps({"status": report["status"], "new_images": report["new_images_generated"], "review_pairs": report["review_pairs"], "reviewed_images": report["reviewed_images"], "display_check": display["display_check"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
