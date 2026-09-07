import pytest
from tools.e2e_verdict import REQUIRED, build_result


@pytest.mark.parametrize("outcome,exit_code,expected", [
    ("passed", 0, "PASS"), ("failed", 1, "FAIL"),
    ("skipped", 0, "BLOCKED"), ("passed", 2, "FAIL"),
])
def test_machine_verdict(outcome, exit_code, expected):
    reports = [{"nodeid": n, "when": "call", "outcome": outcome} for n in REQUIRED]
    assert build_result(reports, exit_code, {})["verdict"] == expected


def test_absent_gui_or_teardown_failure_never_passes():
    assert build_result([], 5, {})["verdict"] == "BLOCKED"
    reports = [{"nodeid": n, "when": "call", "outcome": "passed"} for n in REQUIRED]
    reports.append({"nodeid": REQUIRED[0], "when": "teardown", "outcome": "failed"})
    assert build_result(reports, 1, {})["verdict"] == "FAIL"
