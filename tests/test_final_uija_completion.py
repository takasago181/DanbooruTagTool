from pathlib import Path

from translation_quarantine.r3.final_uija_completion import evaluate


ROOT = Path(__file__).resolve().parents[1]


def test_finalization_has_only_contract_terminal_states():
    result = evaluate(ROOT)
    states = {row["final_state"] for row in result["final"]}
    assert len(result["final"]) == 556
    assert states <= {"JA_ACCEPT", "ENGLISH_FALLBACK_EXCEPTION"}
    assert sum(row["final_state"] == "JA_ACCEPT" for row in result["final"]) == 547
    assert sum(row["final_state"] == "ENGLISH_FALLBACK_EXCEPTION" for row in result["final"]) == 9


def test_strict_candidate_is_accepted_and_symbols_are_explicit_exceptions():
    result = evaluate(ROOT)
    by_canonical = {row["canonical"]: row for row in result["final"]}
    assert by_canonical["holding_staff"]["display_ja"] == "杖を持つ"
    assert by_canonical["holding_staff"]["final_state"] == "JA_ACCEPT"
    assert by_canonical["!"]["final_state"] == "ENGLISH_FALLBACK_EXCEPTION"
    assert by_canonical["!"]["display_ja"] == ""
    assert by_canonical["v"]["display_ja"] == "Vサイン"


def test_final_table_preserves_canonical_authority_and_no_production_flags():
    result = evaluate(ROOT)
    assert all(row["canonical_authoritative"] is True for row in result["final"])
    assert all(row["production_modified"] is False for row in result["final"])
    assert all(row["new_ready_used_as_teacher"] is False for row in result["decisions"])
