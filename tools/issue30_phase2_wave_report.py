#!/usr/bin/env python3
"""Create repository summaries and an A/B contact sheet for a Phase 2 wave."""
from __future__ import annotations

import argparse
import csv
import json
import textwrap
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


def label_font() -> tuple[ImageFont.FreeTypeFont | ImageFont.ImageFont, str, bool]:
    for path in JA_FONT_CANDIDATES:
        if path.is_file():
            try:
                return ImageFont.truetype(str(path), 12), str(path), True
            except OSError:
                continue
    return ImageFont.load_default(), "PIL default (Japanese-invalid)", False


DISPLAY_GLOSSARY = {
    "masterpiece": "傑作",
    "best quality": "最高品質",
    "1girl": "女の子1人",
    "solo": "1人",
    "simple background": "シンプルな背景",
    "lowres": "低解像度",
    "blurry": "ぼやけ",
    "text": "文字",
    "watermark": "透かし",
    "jpeg artifacts": "JPEGアーティファクト",
}
DISPLAY_QUESTIONS_JA = {
    "P2-001": "プロンプトは機器と身体部位の関係を維持したか？",
    "P2-002": "プロンプトは対象者が物体を手に持つ関係を維持したか？",
    "P2-003": "Negative追加は解剖変化を抑制または不安定化したか？",
}


def load_japanese_glossary(manifest: dict[str, dict[str, str]]) -> dict[str, str]:
    glossary = dict(DISPLAY_GLOSSARY)
    for row in manifest.values():
        if row.get("canonical") and row.get("canonical_ja"):
            glossary[row["canonical"]] = row["canonical_ja"]
    source = ROOT / "data/special2788/illustrious_tag_knowledge_base_2788.csv"
    if source.is_file():
        with source.open(encoding="utf-8-sig", newline="") as stream:
            for row in csv.DictReader(stream):
                if row.get("Tag") and row.get("日本語"):
                    glossary[row["Tag"]] = row["日本語"]
    return glossary


def display_tokens(value: str, glossary: dict[str, str]) -> str:
    return ", ".join(f"{token} ({glossary.get(token, '日本語未登録')})" for token in (part.strip() for part in value.split(",")) if token)


def wrap_label(value: str, width: int = 48) -> str:
    return "\n".join(textwrap.wrap(value, width=width, break_long_words=False, break_on_hyphens=False))


def make_contact_sheet(rows: list[dict[str, Any]], output: Path, manifest: dict[str, dict[str, str]]) -> dict[str, Any]:
    ordered = sorted(rows, key=lambda row: (row["case_id"], row["generation"]["seed"], row["cell_type"]))
    thumb_w, thumb_h, label_h = 420, 360, 290
    cols = 2
    sheet = Image.new("RGB", (cols * thumb_w, ((len(ordered) + 1) // 2) * (thumb_h + label_h)), "white")
    draw = ImageDraw.Draw(sheet)
    font, font_path, font_valid = label_font()
    glossary = load_japanese_glossary(manifest)
    for index, row in enumerate(ordered):
        x = (index % cols) * thumb_w
        y = (index // cols) * (thumb_h + label_h)
        with Image.open(row["image_artifact"]["path"]) as image:
            image = image.convert("RGB")
            image.thumbnail((thumb_w - 8, thumb_h - 8))
            sheet.paste(image, (x + (thumb_w - image.width) // 2, y + (thumb_h - image.height) // 2))
        condition = "A" if row["cell_type"].startswith("target_present") else "B"
        case = manifest[row["case_id"]]
        question = case.get("question_ja", DISPLAY_QUESTIONS_JA.get(row["case_id"], case.get("question", "")))
        label = (
            f"#{index + 1:02d}  {row['case_id']}  {condition}  seed={row['generation']['seed']}\n"
            f"問い: {wrap_label(question)}\n"
            f"Positive: {wrap_label(display_tokens(row['generation']['prompt'], glossary))}\n"
            f"Negative: {wrap_label(display_tokens(row['generation']['negative_prompt'], glossary))}"
        )
        draw.multiline_text((x + 6, y + thumb_h + 3), label, fill="black", font=font, spacing=2)
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output, format="PNG")
    return {
        "font_path": font_path,
        "font_priority": [str(path) for path in JA_FONT_CANDIDATES],
        "japanese_label_sample": "Positive: vibrator (バイブレーター)",
        "display_check": "PASS" if font_valid else "FAIL",
        "display_check_reason": "Japanese-capable installed font selected" if font_valid else "No Japanese-capable font selected",
    }


def build_report(run_root: Path, manifest_path: Path, contact_sheet: Path, generated_count: int | None = None, display: dict[str, Any] | None = None, wave_name: str = "wave1") -> dict[str, Any]:
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
    review_pairs = len({(row["case_id"], row["seed"]) for row in image_rows})
    return {
        "schema_version": f"issue30.phase2.{wave_name}_result.v1",
        "status": "SECOND_WAVE_COMPLETE_REVIEW_REQUIRED" if wave_name == "wave2" else "FIRST_WAVE_COMPLETE_REVIEW_REQUIRED",
        "run_id": results[0]["run_id"],
        "manifest": str(manifest_path),
        "local_artifact_root": str(run_root),
        "review_asset": str(contact_sheet),
        "review_display": display or {},
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
        "human_review_pair_count": review_pairs,
        "human_review_reviewed_image_count": len(image_rows),
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
    wave_name = "second-wave" if "wave2" in report["schema_version"] else "first-wave"
    wave_label = "second" if wave_name == "second-wave" else "first"
    lines = [
        f"# Issue #30 Phase 2 {wave_name} result — 2026-09-10",
        "",
        f"Status: `{report['status']}`",
        "",
        f"The bounded {wave_label} wave completed with {report['new_images_generated']} new images and {report['evaluator_runs']} evaluator runs. Machine screening is triage only; no structural success is inferred before human review.",
        "",
        "## Counts",
        "",
        f"- Images generated: **{report['new_images_generated']}**",
        f"- Evaluator-complete images: **{report['evaluator_complete_images']}**",
        f"- Artifact gate: **{report['artifact_gate'].get('PASS', 0)} PASS / {report['artifact_gate'].get('BLOCKED', 0)} BLOCKED**",
        f"- Human review: **{report['human_review_pair_count']} pairs / {report['human_review_reviewed_image_count']} images**",
        f"- Machine-selected review queue: **{report['human_review_image_count']}** images",
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
        f"Japanese font: `{report['review_display'].get('font_path', 'not recorded')}`; display check: **{report['review_display'].get('display_check', 'not recorded')}**.",
        "",
        f"Review all {report['human_review_reviewed_image_count']} numbered A/B images ({report['human_review_pair_count']} pairs) in the contact sheet. For each question, compare the same seed's A and B condition and answer `A / B / both / neither / tie / unclear`. Do not inspect raw evaluator logs.",
        "",
        "## Decision and limitation",
        "",
        "All declared questions remain `HOLD_HUMAN_REVIEW_REQUIRED` until human review. Evaluator output is assistive only; exact count, alias-trigger equivalence, and relation/binding semantics are not auto-promoted. No additional seeds or experiments are authorized before review.",
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
    display = make_contact_sheet(raw, contact_sheet, manifest)
    wave_name = "wave2" if "WAVE2" in args.manifest.name.upper() else "wave1"
    report = build_report(args.run_root, args.manifest, contact_sheet, args.generated_count, display, wave_name)
    write_json(args.output_json, report)
    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.write_text(markdown(report), encoding="utf-8")
    print(json.dumps({
        "status": report["status"],
        "images": report["image_count"],
        "evaluator_runs": report["evaluator_runs"],
        "artifact_gate": report["artifact_gate"],
        "human_review_images": report["human_review_image_count"],
        "human_review_pairs": report["human_review_pair_count"],
        "reviewed_images": report["human_review_reviewed_image_count"],
        "japanese_font": report["review_display"]["font_path"],
        "display_check": report["review_display"]["display_check"],
        "contact_sheet": str(contact_sheet),
        "output_json": str(args.output_json),
        "output_md": str(args.output_md),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
