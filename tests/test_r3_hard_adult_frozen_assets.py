from pathlib import Path

from translation_quarantine.r3.r3_hard_adult_gate import validate_files


ROOT = Path(__file__).resolve().parents[1]
R3 = ROOT / "translation_quarantine" / "r3"


def test_frozen_hard_adult_v1_assets_match_fixed_64_plus_16_design():
    result = validate_files(
        R3 / "hard_adult_challenge_v1.jsonl",
        R3 / "hard_adult_ambiguity_probes_v1.jsonl",
    )
    assert result["ok"], result["errors"]
    assert result["challenge_rows"] == 64
    assert result["ambiguity_probes"] == 16
