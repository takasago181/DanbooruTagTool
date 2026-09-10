import csv
import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "data/generation/special2788_generation_profile.csv"
EXPECTED_PROFILE_SHA256 = "55490940378e15d8e41454e701d0c202abbab307a08fb6e56841171e0edec1fd"


def test_final_naming_records_define_distinct_concepts():
    decision = (ROOT / "docs/decisions/SPECIAL_CORE_DICTIONARY_NAMING.md").read_text(encoding="utf-8")
    freeze = (ROOT / "docs/project/SPECIAL_CORE_DICTIONARY_FREEZE.md").read_text(encoding="utf-8")
    for text in (decision, freeze):
        assert "Special Core Dictionary" in text
        assert "Core Tag Set" in text
        assert "Special2788" in text
    assert "FINAL" in decision


def test_production_profile_identity_and_hash_are_frozen():
    rows = list(csv.DictReader(PROFILE.open(newline="", encoding="utf-8")))
    identities = [row["SpecialID"] for row in rows]
    assert len(rows) == 2788
    assert len(set(identities)) == 2788
    assert identities == [str(i) for i in range(1, 2789)]
    assert hashlib.sha256(PROFILE.read_bytes()).hexdigest() == EXPECTED_PROFILE_SHA256


def test_inventory_declares_complete_baseline_scan_and_zero_unsafe_rename():
    inventory = (ROOT / "docs/issue43/SPECIAL_CORE_DICTIONARY_REFERENCE_INVENTORY.md").read_text(encoding="utf-8")
    assert "95 paths / 316 matching lines" in inventory
    assert "No unsafe rename was identified" in inventory
    assert "data/**` content" in inventory
