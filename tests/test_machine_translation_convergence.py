from pathlib import Path

from translation_quarantine.r3.machine_translation_convergence import (
    evaluate,
    lightweight_audit,
    machine_candidate,
)


ROOT = Path(__file__).resolve().parents[1]


def test_transparent_machine_candidate_is_deterministic_and_lightweight_safe():
    first = machine_candidate("pink_hair")
    second = machine_candidate("pink_hair")
    assert first == second
    assert first[0] == "ピンク髪"
    assert lightweight_audit("pink_hair", "MEDIUM", first[0]) == ("ACCEPT", [])


def test_high_risk_candidate_is_never_lightweight_accepted():
    candidate, _, _ = machine_candidate("holding_staff")
    decision, reasons = lightweight_audit("holding_staff", "CRITICAL", candidate)
    assert candidate == "杖を持つ"
    assert decision == "REJECT"
    assert "STRICT_ROUTE_REQUIRED" in reasons


def test_unknown_and_symbol_rows_fail_closed():
    candidate, route, _ = machine_candidate("uncensored")
    assert candidate == ""
    assert route == "MACHINE_UNRESOLVED"
    decision, reasons = lightweight_audit("uncensored", "LOW", candidate)
    assert decision == "REJECT"
    assert "NO_MACHINE_CANDIDATE" in reasons


def test_real_campaign_evaluation_is_complete_and_keeps_prior_ready_separate():
    result = evaluate(ROOT)
    assert len(result["rows"]) == 556
    assert sum(row["final_state"] == "STRICT_ACCEPT" for row in result["rows"]) == 14
    assert sum(row["final_state"] != "STRICT_ACCEPT" for row in result["rows"]) == 542
    assert all(row["new_ready_used_as_teacher"] is False for row in result["provenance"])
    assert all(row["canonical_authoritative"] is True for row in result["rows"])
