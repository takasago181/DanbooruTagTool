"""Issue 28 pytest evidence aggregation; not an image experiment runner."""
from collections import Counter

REQUIRED = (
    "tests/test_e2e_functional.py::test_real_tk_search_candidates_and_output",
    "tests/test_e2e_functional.py::test_real_tk_variant_restoration",
    "tests/test_e2e_functional.py::test_real_tk_stale_and_invalid_protection",
)


def build_result(reports, exit_code, environment):
    failed = [r for r in reports if r["outcome"] == "failed"]
    passed = {r["nodeid"] for r in reports
              if r["when"] == "call" and r["outcome"] == "passed"}
    incomplete = [node for node in REQUIRED if node not in passed]
    # Missing collection, skips and xfails never satisfy the required GUI gate.
    verdict = "FAIL" if failed or exit_code not in (0, 5) else (
        "BLOCKED" if incomplete else "PASS")
    return {"schema_version": 1, "issue": 28, "verdict": verdict,
            "pytest_exit_code": int(exit_code), "environment": environment,
            "required": list(REQUIRED), "unexecuted_or_unsuccessful": incomplete,
            "call_counts": dict(Counter(r["outcome"] for r in reports if r["when"] == "call")),
            "reports": reports}


def markdown(result):
    lines = ["# Issue 28 automated functional E2E result", "",
             f"Machine verdict: **{result['verdict']}**", "",
             f"Pytest exit code: {result['pytest_exit_code']}",
             f"Call outcomes: {result['call_counts']}", "",
             "Local execution evidence, not GitHub Actions evidence.", "",
             "## Required production paths", ""]
    for node in result["required"]:
        status = "NOT PASSED" if node in result["unexecuted_or_unsuccessful"] else "PASS"
        lines.append(f"- {node}: {status}")
    for report in result["reports"]:
        if report.get("detail"):
            lines.extend(["", f"## {report['nodeid']} ({report['when']})", "",
                          "```text", report["detail"], "```"])
    lines.extend(["", "## Stop", "",
                  "DEV must verify remote evidence and record Issue #28. No Stage10 image A/B was run."])
    return "\n".join(lines) + "\n"
