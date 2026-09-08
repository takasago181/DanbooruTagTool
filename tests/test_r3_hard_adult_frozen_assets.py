import json
from pathlib import Path

from translation_quarantine.r3.r3_hard_adult_gate import validate_files


ROOT = Path(__file__).resolve().parents[1]
R3 = ROOT / "translation_quarantine" / "r3"


def test_frozen_hard_adult_v1_assets_match_fixed_64_plus_16_design():
    challenge_path = R3 / "hard_adult_challenge_v1.jsonl"
    result = validate_files(
        challenge_path,
        R3 / "hard_adult_ambiguity_probes_v1.jsonl",
    )
    assert result["ok"], result["errors"]
    assert result["challenge_rows"] == 64
    assert result["ambiguity_probes"] == 16

    rows = [
        json.loads(line)
        for line in challenge_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    by_id = {row["challenge_id"]: row for row in rows}
    assert by_id["HAC-009"]["canonical"] == "anal object insertion"
    assert by_id["HAC-009"]["special_id"] == 149
    assert "masturbation" not in {row["canonical"] for row in rows}
