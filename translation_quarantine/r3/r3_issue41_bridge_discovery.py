"""Discover the real Issue #41 fresh100 overlap with the #32 Special2788 lane.

The production generation profile is a read-only identity index here. This
module does not consume its generation verdicts as semantic authority; it only
identifies which fixed fresh100 canonicals have a #32/Special2788 identity and
therefore require a controlled bridge snapshot.
"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable, Mapping


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_jsonl(path: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    path.write_text(
        "".join(
            json.dumps(
                dict(row), ensure_ascii=False, sort_keys=True, separators=(",", ":")
            )
            + "\n"
            for row in rows
        ),
        encoding="utf-8",
        newline="\n",
    )


def _selected_rows(selection_path: Path) -> list[dict[str, Any]]:
    value = json.loads(selection_path.read_text(encoding="utf-8"))
    rows = value.get("selected", []) if isinstance(value, dict) else []
    result: list[dict[str, Any]] = []
    for index, row in enumerate(rows, 1):
        canonical = str(row.get("canonical", "")).strip()
        if not canonical:
            raise ValueError(f"pilot selection row {index} has blank canonical")
        ordinal = int(row.get("pilot_ordinal", index))
        result.append({"canonical": canonical, "pilot_ordinal": ordinal})
    if len(result) != 100:
        raise ValueError(f"fixed fresh pilot must contain 100 rows, got {len(result)}")
    if len({row["canonical"] for row in result}) != 100:
        raise ValueError("duplicate canonical in fixed fresh pilot")
    if {row["pilot_ordinal"] for row in result} != set(range(1, 101)):
        raise ValueError("fixed fresh pilot ordinals are not exactly 1..100")
    return sorted(result, key=lambda row: row["pilot_ordinal"])


def _profile_index(profile_path: Path) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    with profile_path.open(encoding="utf-8-sig", newline="") as stream:
        for row_number, row in enumerate(csv.DictReader(stream), 2):
            canonical = str(row.get("Tag", "")).strip()
            if not canonical:
                raise ValueError(f"generation profile row {row_number} has blank Tag")
            if canonical in result:
                raise ValueError(f"duplicate generation-profile Tag: {canonical}")
            result[canonical] = dict(row)
    if not result:
        raise ValueError("generation profile is empty")
    return result


def discover(
    root: Path,
    *,
    selection_path: Path | None = None,
    profile_path: Path | None = None,
    output_dir: Path | None = None,
) -> dict[str, Any]:
    r3 = root / "translation_quarantine" / "r3"
    selection_path = selection_path or (r3 / "pilot_selection.json")
    profile_path = profile_path or (
        root / "data" / "generation" / "special2788_generation_profile.csv"
    )
    output_dir = output_dir or r3

    selected = _selected_rows(selection_path)
    profile = _profile_index(profile_path)
    profile_hash = _sha256(profile_path)
    overlap: list[dict[str, Any]] = []
    for row in selected:
        canonical = row["canonical"]
        match = profile.get(canonical)
        if match is None:
            continue
        special_id = str(match.get("SpecialID", "")).strip()
        overlap.append(
            {
                "canonical": canonical,
                "pilot_ordinal": row["pilot_ordinal"],
                "special_id": int(special_id) if special_id.isdigit() else special_id,
                "bridge32_required": True,
                "frozen": True,
                "identity_match": "EXACT_CANONICAL",
                "source_ref": "data/generation/special2788_generation_profile.csv",
                "source_content_identity": f"sha256:{profile_hash}",
                "evidence_role": "BRIDGE32_REQUIREMENT",
                "scope_note": (
                    "Exact canonical identity overlaps the #32/Special2788 generation-profile lane; "
                    "this requirement does not certify Japanese wording or #32 semantic correctness."
                ),
            }
        )

    requirements_path = output_dir / "issue41_issue32_overlap_requirements.jsonl"
    _write_jsonl(requirements_path, overlap)
    summary = {
        "schema_version": "issue41-bridge-discovery-1",
        "fixed_fresh100": len(selected),
        "generation_profile_rows": len(profile),
        "exact_overlap_count": len(overlap),
        "non_overlap_count": len(selected) - len(overlap),
        "generation_profile_sha256": profile_hash,
        "requirements_file": requirements_path.name,
        "identity_only_discovery": True,
        "production_modified": False,
    }
    (output_dir / "issue41_issue32_overlap_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return summary


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    print(json.dumps(discover(args.root), ensure_ascii=False, indent=2))
