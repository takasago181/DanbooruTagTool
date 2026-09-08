import csv
import json
from pathlib import Path

from translation_quarantine.r3.r3_issue41_bridge_discovery import discover


def test_exact_identity_overlap_only(tmp_path: Path):
    r3 = tmp_path / "translation_quarantine" / "r3"
    r3.mkdir(parents=True)
    generation = tmp_path / "data" / "generation"
    generation.mkdir(parents=True)

    selected = [
        {"pilot_ordinal": index, "canonical": f"c{index}"}
        for index in range(1, 101)
    ]
    (r3 / "pilot_selection.json").write_text(
        json.dumps({"selected": selected}),
        encoding="utf-8",
    )

    profile_path = generation / "special2788_generation_profile.csv"
    with profile_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=["SpecialID", "Tag", "MeaningStatus"],
        )
        writer.writeheader()
        for index in (1, 3, 50, 100):
            writer.writerow(
                {
                    "SpecialID": index,
                    "Tag": f"c{index}",
                    "MeaningStatus": "ANY",
                }
            )
        writer.writerow(
            {
                "SpecialID": 200,
                "Tag": "C1",
                "MeaningStatus": "CASE_MISMATCH",
            }
        )

    summary = discover(tmp_path)
    assert summary["exact_overlap_count"] == 4
    rows = [
        json.loads(line)
        for line in (r3 / "issue41_issue32_overlap_requirements.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    ]
    assert [row["canonical"] for row in rows] == ["c1", "c3", "c50", "c100"]
    assert all(row["bridge32_required"] is True for row in rows)
    assert all(row["identity_match"] == "EXACT_CANONICAL" for row in rows)
