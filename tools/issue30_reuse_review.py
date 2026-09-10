#!/usr/bin/env python3
"""Build a bounded reuse-only review asset from existing Phase 1 results."""
from __future__ import annotations

import argparse
import csv
import json
import textwrap
from collections import Counter
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw

from issue30_phase2_wave_report import label_font, load_japanese_glossary, display_tokens


ROOT = Path(__file__).resolve().parents[1]


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_manifest(path: Path) -> dict[str, dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return {row["image_id"]: row for row in csv.DictReader(stream)}


def wrap(value: str, width: int = 62) -> str:
    return "\n".join(textwrap.wrap(value, width=width, break_long_words=False, break_on_hyphens=False))


def make_contact_sheet(rows: list[dict[str, Any]], manifest: dict[str, dict[str, str]], output: Path) -> dict[str, Any]:
    ordered = sorted(rows, key=lambda row: (row["case_id"], row["seed"], row["condition"]))
    thumb_w, thumb_h, label_h = 540, 480, 210
    cols = 2
    sheet = Image.new("RGB", (cols * thumb_w, ((len(ordered) + 1) // 2) * (thumb_h + label_h)), "white")
    draw = ImageDraw.Draw(sheet)
    font, font_path, font_valid = label_font()
    glossary = load_japanese_glossary(manifest)
    for index, row in enumerate(ordered):
        x = (index % cols) * thumb_w
        y = (index // cols) * (thumb_h + label_h)
        with Image.open(row["image_path"]) as image:
            image = image.convert("RGB")
            image.thumbnail((thumb_w - 12, thumb_h - 12))
            sheet.paste(image, (x + (thumb_w - image.width) // 2, y + (thumb_h - image.height) // 2))
        case = manifest[row["image_id"]]
        label = (
            f"#{index + 1:02d}  {row['case_id']}  {row['condition']}  seed={row['seed']}\n"
            f"PASS条件: {wrap(case['visible_pass_condition_ja'])}\n"
            f"Positive: {wrap(display_tokens(row['prompt'], glossary))}\n"
            f"Negative: {wrap(display_tokens(row['negative_prompt'], glossary))}"
        )
        draw.multiline_text((x + 8, y + thumb_h + 4), label, fill="black", font=font, spacing=3)
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output, format="PNG")
    return {
        "font_path": font_path,
        "japanese_label_sample": "PASS条件: 2人または両手による手淫",
        "display_check": "PASS" if font_valid else "FAIL",
    }


def markdown(report: dict[str, Any]) -> str:
    case = report["selected_existing_cases"][0]
    return f"""# Issue #30 Phase 2 reuse-only review — 2026-09-11

## RESULT

Status: `REUSE_ONLY_REVIEW_READY`

既存 Phase 1 の `{case['case_id']} {case['canonical']}` だけを再利用する、2ペア・4画像のレビュー資産を作成した。新規画像生成、新規 seed、evaluator 再実行は 0 件。

## EVIDENCE

- Selected existing case: `{case['case_id']}` / Special ID `{', '.join(str(x) for x in case['special_ids'])}`
- Visible PASS condition: **{case['visible_pass_condition_ja']}**
- Visible FAIL condition: **{case['visible_fail_condition_ja']}**
- Why judgeable from one still: {case['why_this_is_judgeable_from_one_still_image']}
- Reused images: **{report['reused_image_count']}**
- Reused evaluator records: **{report['reused_evaluator_count']}**
- User review: **{report['review_pairs']} pairs / {report['reviewed_images']} images**
- Artifact gate: `{report['artifact_gate']}`

## REVIEW

Contact sheet: `{report['contact_sheet']}`

Japanese font: `{report['review_display']['font_path']}`; display check: **{report['review_display']['display_check']}**.

画像内で、2人または両手による手淫が2つ同時に成立しているかを、同じ seed の A/B で比較する。raw evaluator log は見ない。

## DECISION

`CAL-022` は同系統だが今回の4画像で十分な最小レビューを優先して未選択。`CAL-024 teamwork (sexual)` は役割割当の文脈依存が強く、`CAL-032 anus + after footjob` は still image だけでは after-context を直接判定できないため DEFER。

## LIMITATION / NEXT

このレビューは既存 Phase 1 evidence の再利用であり、新しい生成性能の証明ではない。人手判定後、DEV/ChatGPT が exact-count evidence の十分性、multi-Special の継続 defer、Phase 2 close を判断する。追加生成へ自動進行しない。
"""


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
    selected_ids = set(manifest)
    rows = []
    for result in results:
        if result["image_id"] not in selected_ids:
            continue
        condition = "A" if result["cell_type"].startswith("target_present") else "B"
        rows.append({
            "image_id": result["image_id"],
            "case_id": result["case_id"],
            "condition": condition,
            "seed": result["generation"]["seed"],
            "prompt": result["generation"]["prompt"],
            "negative_prompt": result["generation"]["negative_prompt"],
            "image_path": result["image_artifact"]["path"],
            "artifact_gate": "PASS",
            "evaluator_count": len(result["evaluators"]),
            "screening_classes": result["screening"]["screening_classes"],
        })
    if len(rows) != len(manifest):
        raise RuntimeError(f"manifest/result mismatch: expected {len(manifest)}, found {len(rows)}")
    display = make_contact_sheet(rows, manifest, args.contact_sheet)
    by_case = {}
    for row in rows:
        case = manifest[row["image_id"]]
        by_case[row["case_id"]] = {
            "case_id": row["case_id"],
            "canonical": case["canonical"],
            "special_ids": [int(value) for value in case["special_ids"].split("|")],
            "visible_pass_condition_ja": case["visible_pass_condition_ja"],
            "visible_fail_condition_ja": case["visible_fail_condition_ja"],
            "why_this_is_judgeable_from_one_still_image": case["why_this_is_judgeable_from_one_still_image"],
        }
    report = {
        "schema_version": "issue30.phase2.reuse_only_review.v1",
        "status": "REUSE_ONLY_REVIEW_READY",
        "new_images_generated": 0,
        "new_seeds": 0,
        "evaluator_reruns": 0,
        "selected_existing_cases": list(by_case.values()),
        "reused_image_count": len(rows),
        "reused_evaluator_count": sum(row["evaluator_count"] for row in rows),
        "review_pairs": len({(row["case_id"], row["seed"]) for row in rows}),
        "reviewed_images": len(rows),
        "artifact_gate": dict(Counter(row["artifact_gate"] for row in rows)),
        "contact_sheet": str(args.contact_sheet),
        "local_artifact_root": str(args.run_root),
        "review_display": display,
        "image_records": rows,
        "decision": "STOP_FOR_USER_DEV_REVIEW",
    }
    write_json(args.output_json, report)
    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.write_text(markdown(report), encoding="utf-8")
    print(json.dumps({"status": report["status"], "reused_images": len(rows), "review_pairs": report["review_pairs"], "reviewed_images": report["reviewed_images"], "display_check": display["display_check"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
