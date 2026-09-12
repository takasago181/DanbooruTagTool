from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]

def test_goal_lock_exists_and_mentions_current_special_dictionary():
    p = ROOT / "docs/PRODUCT_GOAL_LOCK.md"
    text = p.read_text(encoding="utf-8")
    assert "Special Core Dictionary" in text
    assert "Special2788" in text

def test_core_set_example_minimum_fields():
    p = ROOT / "templates/core_set.example.json"
    obj = json.loads(p.read_text(encoding="utf-8"))
    assert set(["core_set_id","core_set_name","special_tag_ids","memo","created_at"]) <= set(obj)
    assert isinstance(obj["special_tag_ids"], list)

def test_final_spec_exists():
    assert (ROOT / "docs/CODEX_IMPLEMENTATION_SPEC_JA_v1.3.md").exists()
