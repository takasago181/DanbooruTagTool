#!/usr/bin/env python3
"""Build Issue #76 integrated v2 browse mapping (v0.8).

This is analysis/design output only. It does not mutate canonical Special data,
Alias data, General taxonomy, search ranking, or production WPF data.

Pipeline:
  accepted Issue #56 full mapping
  -> Issue #76 v0.2 mechanical projection
  -> v0.3 buttock/anal facet resolution
  -> v0.4 chastity-control audit
  -> v0.5 former v1 unresolved audit / product-fit routing
  -> v0.6 practical-generation/knowledge-aligned patch
  -> v0.8 cleanup + invariant validation

The resulting CSV is deterministic from committed repository evidence.
"""

from __future__ import annotations

import argparse
import csv
import json
import tempfile
from collections import Counter
from pathlib import Path

from issue76_build_v2_candidate import build_candidate

ROOT = Path(__file__).resolve().parents[1]
GEN = ROOT / "docs" / "issue76" / "generated"
DEFAULT_OUTPUT = GEN / "issue76_v2_candidate_mapping_v0_8.csv"
DEFAULT_META = GEN / "issue76_v2_candidate_meta_v0_8.json"

SITE_PATCH = GEN / "issue76_v2_site_facet_patch_v0_3.csv"
CHASTITY_PATCH = GEN / "issue76_chastity_control_patch_v0_4.csv"
UNRESOLVED_AUDIT = GEN / "issue76_v1_unresolved_audit_v0_5.csv"
PRACTICAL_PATCH = GEN / "issue76_practical_generation_patch_v0_6.csv"

KIND_JA_TO_ID = {
    "身体・状態": "BODY_STATE",
    "衣服・露出": "CLOTHING_EXPOSURE",
    "行為・接触": "ACTION_CONTACT",
    "道具・物": "TOOL_OBJECT",
    "体液・排泄": "FLUID_EXCRETION",
    "ポーズ・構図・場面": "POSE_SCENE",
    "人物・関係": "PERSON_RELATION",
    "異形・変形": "NONHUMAN_TRANSFORMATION",
    "表現・メタ": "META_EXPRESSION",
}
BODY_JA_TO_ID = {
    "乳房・乳首": "BREAST_NIPPLE",
    "女性器": "FEMALE_GENITAL",
    "男性器": "MALE_GENITAL",
    "尻・肛門": "BUTTOCK_ANAL",
    "口・口内": "MOUTH_ORAL",
    "尿道": "URETHRA",
}

ALLOWED_KIND_IDS = set(KIND_JA_TO_ID.values())
ALLOWED_BODY_IDS = set(BODY_JA_TO_ID.values())
ALLOWED_THEME_IDS = {"BDSM_RESTRAINT", "INJURY_R18G", "REPRO_PREGNANCY_LACTATION"}
ALLOWED_STATUS = {
    "AUTO_CANDIDATE",
    "HUMAN_RESOLVED",
    "REFERENCE_ONLY_NO_DIRECT_BROWSE",
    "DEFER_PRODUCT_FIT_REVIEW",
    "OUT_OF_SCOPE_NO_BROWSE",
}
BROWSE_STATUS = {"AUTO_CANDIDATE", "HUMAN_RESOLVED"}

FIELDS = [
    "special_id",
    "primary_genre_id",
    "primary_subgenre_id",
    "secondary_paths",
    "classification_status",
    "ambiguity_note",
    "v2_kind_id",
    "v2_kind_ja",
    "v2_body_sites",
    "v2_body_sites_ja",
    "v2_themes",
    "v2_themes_ja",
    "v2_status",
    "v2_reason",
    "v2_review_note",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def split_pipe(value: str) -> list[str]:
    return [part.strip() for part in (value or "").split("|") if part.strip()]


def join_pipe(values: list[str]) -> str:
    return " | ".join(values)


def replace_token(value: str, old: str, new: str) -> str:
    return join_pipe([new if item == old else item for item in split_pipe(value)])


def append_reason(value: str, token: str) -> str:
    parts = split_pipe(value)
    if token not in parts:
        parts.append(token)
    return join_pipe(parts)


def dedupe_reason(value: str) -> str:
    result: list[str] = []
    for item in split_pipe(value):
        if item not in result:
            result.append(item)
    return join_pipe(result)


def ja_body_to_ids(value: str) -> str:
    return join_pipe([BODY_JA_TO_ID[item] for item in split_pipe(value)])


def index_rows(rows: list[dict[str, str]]) -> dict[int, dict[str, str]]:
    result = {int(row["special_id"]): row for row in rows}
    if len(rows) != 2788 or set(result) != set(range(1, 2789)):
        raise ValueError("Issue #76 requires exact Special ID coverage 1..2788")
    return result


def apply_v03(rows_by_id: dict[int, dict[str, str]]) -> None:
    for patch in read_csv(SITE_PATCH):
        row = rows_by_id[int(patch["special_id"])]
        row["v2_body_sites"] = replace_token(
            row["v2_body_sites"], patch["old_body_facet_id"], patch["new_body_facet_id"]
        )
        row["v2_body_sites_ja"] = replace_token(
            row["v2_body_sites_ja"], patch["old_body_facet_ja"], patch["new_body_facet_ja"]
        )


def apply_v04(rows_by_id: dict[int, dict[str, str]]) -> None:
    for patch in read_csv(CHASTITY_PATCH):
        row = rows_by_id[int(patch["special_id"])]
        row["v2_kind_id"] = patch["resolved_kind_id"]
        row["v2_kind_ja"] = patch["resolved_kind_ja"]
        row["v2_body_sites"] = patch["resolved_body_site_id"]
        row["v2_body_sites_ja"] = patch["resolved_body_site_ja"]
        row["v2_themes"] = patch["resolved_theme_id"]
        row["v2_themes_ja"] = patch["resolved_theme_ja"]
        row["v2_status"] = "AUTO_CANDIDATE"
        row["v2_reason"] = "issue76_chastity_control_audit_v0_4"
        row["v2_review_note"] = ""


def apply_v05(rows_by_id: dict[int, dict[str, str]]) -> None:
    for patch in read_csv(UNRESOLVED_AUDIT):
        row = rows_by_id[int(patch["special_id"])]
        for field in (
            "v2_kind_id",
            "v2_kind_ja",
            "v2_body_sites",
            "v2_body_sites_ja",
            "v2_themes",
            "v2_themes_ja",
        ):
            row[field] = patch[field]

        resolution = patch["v2_resolution"]
        if resolution == "BROWSE_RESOLVED":
            row["v2_status"] = "HUMAN_RESOLVED"
            row["v2_reason"] = "issue76_v0_5_manual_review"
            row["v2_review_note"] = patch["rationale"]
        elif resolution == "REFERENCE_ONLY_NO_DIRECT_BROWSE":
            row["v2_status"] = resolution
            row["v2_reason"] = "product_fit_keep_reference_only"
            row["v2_review_note"] = (
                "Issue #63 product-fit policy: retain exact/alias/reference/search access "
                "but do not surface as an independent default browse candidate when "
                "canonical/product-facing identity is available."
            )
        elif resolution == "DEFER_PRODUCT_FIT_REVIEW":
            row["v2_status"] = resolution
            row["v2_reason"] = "product_fit_review_gate"
            row["v2_review_note"] = (
                "Issue #63 product-fit REVIEW must remain inspectable and must not be "
                "silently promoted to an ordinary resolved browse candidate."
            )
        elif resolution == "OUT_OF_SCOPE_NO_BROWSE":
            row["v2_status"] = resolution
            row["v2_reason"] = "product_fit_out_of_scope"
            row["v2_review_note"] = (
                "Issue #63 product-fit policy excludes OUT_OF_SCOPE_PRODUCT from normal "
                "product-facing browse surfaces."
            )
        else:
            raise ValueError(f"Unknown v0.5 resolution: {resolution}")


def apply_v06(rows_by_id: dict[int, dict[str, str]]) -> None:
    for patch in read_csv(PRACTICAL_PATCH):
        row = rows_by_id[int(patch["special_id"])]
        dimension = patch["dimension"]
        if dimension == "kind":
            row["v2_kind_ja"] = patch["after"]
            row["v2_kind_id"] = KIND_JA_TO_ID.get(patch["after"], "")
            row["v2_reason"] = append_reason(row["v2_reason"], "practical_generation_v0_6")
        elif dimension == "body_site":
            row["v2_body_sites_ja"] = patch["after"]
            row["v2_body_sites"] = ja_body_to_ids(patch["after"])
            row["v2_reason"] = append_reason(
                row["v2_reason"], "intrinsic_generation_site_v0_6"
            )
        else:
            raise ValueError(f"Unknown v0.6 dimension: {dimension}")


def cleanup_v08(rows_by_id: dict[int, dict[str, str]]) -> None:
    stale = "BUTTOCK_ANUS v1 route conflates buttock and anus"
    for row in rows_by_id.values():
        if row["v2_status"] == "AUTO_CANDIDATE" and row["v2_review_note"] == stale:
            row["v2_review_note"] = ""
        row["v2_reason"] = dedupe_reason(row["v2_reason"])


def validate(rows: list[dict[str, str]]) -> dict[str, object]:
    ids = [int(row["special_id"]) for row in rows]
    invalid_kind = sorted(
        {row["v2_kind_id"] for row in rows if row["v2_kind_id"] and row["v2_kind_id"] not in ALLOWED_KIND_IDS}
    )
    invalid_body = sorted(
        {item for row in rows for item in split_pipe(row["v2_body_sites"]) if item not in ALLOWED_BODY_IDS}
    )
    invalid_theme = sorted(
        {item for row in rows for item in split_pipe(row["v2_themes"]) if item not in ALLOWED_THEME_IDS}
    )
    invalid_status = sorted({row["v2_status"] for row in rows if row["v2_status"] not in ALLOWED_STATUS})

    browse_without_route: list[int] = []
    nonbrowse_with_route: list[int] = []
    stale_review: list[int] = []
    duplicate_reason: list[int] = []

    for row in rows:
        sid = int(row["special_id"])
        has_route = bool(row["v2_kind_id"] or row["v2_body_sites"] or row["v2_themes"])
        if row["v2_status"] in BROWSE_STATUS and not has_route:
            browse_without_route.append(sid)
        if row["v2_status"] not in BROWSE_STATUS and has_route:
            nonbrowse_with_route.append(sid)
        if "BUTTOCK_ANUS v1 route conflates buttock and anus" in row["v2_review_note"]:
            stale_review.append(sid)
        reasons = split_pipe(row["v2_reason"])
        if len(reasons) != len(set(reasons)):
            duplicate_reason.append(sid)

    result = {
        "rows": len(rows),
        "unique_ids": len(set(ids)),
        "exact_ids_1_2788": ids == list(range(1, 2789)),
        "invalid_kind_ids": invalid_kind,
        "invalid_body_ids": invalid_body,
        "invalid_theme_ids": invalid_theme,
        "invalid_status": invalid_status,
        "browse_rows_without_route": browse_without_route,
        "nonbrowse_rows_with_route": nonbrowse_with_route,
        "stale_buttock_anal_review_note_rows": stale_review,
        "duplicate_reason_rows": duplicate_reason,
        "status_counts": dict(Counter(row["v2_status"] for row in rows)),
    }
    passed = (
        result["rows"] == 2788
        and result["unique_ids"] == 2788
        and result["exact_ids_1_2788"]
        and not invalid_kind
        and not invalid_body
        and not invalid_theme
        and not invalid_status
        and not browse_without_route
        and not nonbrowse_with_route
        and not stale_review
        and not duplicate_reason
    )
    result["verdict"] = "PASS" if passed else "FAIL"
    if not passed:
        raise ValueError(json.dumps(result, ensure_ascii=False, indent=2))
    return result


def build(output: Path, meta_path: Path) -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix="issue76-v02-") as tmp:
        tmpdir = Path(tmp)
        build_candidate(tmpdir)
        rows = read_csv(tmpdir / "issue76_v2_candidate_mapping_v0_2.csv")

    rows_by_id = index_rows(rows)
    apply_v03(rows_by_id)
    apply_v04(rows_by_id)
    apply_v05(rows_by_id)
    apply_v06(rows_by_id)
    cleanup_v08(rows_by_id)

    final_rows = [rows_by_id[sid] for sid in range(1, 2789)]
    validation = validate(final_rows)
    write_csv(output, final_rows)

    meta = {
        "version": "issue76-v2-integrated-candidate-v0.8",
        "source_total": 2788,
        "pipeline": ["v0.2", "v0.3", "v0.4", "v0.5", "v0.6", "v0.8 cleanup"],
        "validation": validation,
        "notes": [
            "Knowledge #44 + current official/primary web evidence outrank historical WAI17 local-image samples.",
            "v0.8 makes no semantic route changes beyond v0.6; it materializes and cleans the full 2,788 candidate.",
            "This is browse-taxonomy design evidence, not production WPF data.",
        ],
    }
    meta_path.parent.mkdir(parents=True, exist_ok=True)
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return meta


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--meta", type=Path, default=DEFAULT_META)
    args = parser.parse_args()
    meta = build(args.output, args.meta)
    print(json.dumps(meta, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
