"""Pytest plugin for auditable full-suite setup-error classification.

Invoke with ``pytest -p translation_quarantine.r3.r3_pytest_capture``.  The
plugin records the complete long representation for every failed setup/call
phase and writes only under this quarantine directory.
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


OUTPUT_DIR = Path(__file__).resolve().parent
ERROR_TYPE_RE = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*(?:Error|Exception))\b")


def _text(report: Any) -> str:
    return str(getattr(report, "longreprtext", "") or getattr(report, "longrepr", "") or "")


def _classify(report: dict[str, Any]) -> dict[str, Any]:
    text = report["longrepr"]
    types = sorted(set(ERROR_TYPE_RE.findall(text)))
    permission = "PermissionError" in text
    winerror5 = "[WinError 5]" in text
    access_denied = "Access is denied" in text or "アクセスが拒否" in text
    temp_context = any(token in text.lower() for token in ("tmpdir", "temp-directory", "basetemp", "os.scandir", "pytest-of-"))
    if report["when"] == "setup" and permission and winerror5 and temp_context:
        root_cause = "WINDOWS_ACL_TEMP_SETUP"
    elif report["when"] == "setup" and (permission or winerror5 or access_denied):
        root_cause = "OTHER_PERMISSION_SETUP"
    elif report["when"] == "call":
        root_cause = "CALL_PHASE_FAILURE"
    else:
        root_cause = "NON_ACL_SETUP_FAILURE"
    return {
        "nodeid": report["nodeid"],
        "when": report["when"],
        "outcome": report["outcome"],
        "exception_types": types,
        "permission_error": permission,
        "winerror_5": winerror5,
        "access_denied": access_denied,
        "temp_directory_context": temp_context,
        "root_cause": root_cause,
        "longrepr": text,
    }


def pytest_configure(config: Any) -> None:
    config._r3_capture_reports = []
    config._r3_capture_started_utc = datetime.now(timezone.utc).isoformat()


def pytest_runtest_logreport(report: Any) -> None:
    if report.outcome != "failed" or report.when not in {"setup", "call", "teardown"}:
        return
    config = getattr(report, "config", None)
    # Pytest reports do not expose config on all versions; the plugin manager
    # is available through the current session object instead.
    session = getattr(report, "item", None)
    del config, session


def pytest_sessionfinish(session: Any, exitstatus: int) -> None:
    reports: list[dict[str, Any]] = []
    # Reconstruct from the terminal reporter's collected reports when present.
    terminal = session.config.pluginmanager.get_plugin("terminalreporter")
    if terminal is not None:
        seen: set[tuple[str, str]] = set()
        for category in ("failed", "error"):
            for report in terminal.stats.get(category, []):
                marker = (str(getattr(report, "nodeid", "")), str(getattr(report, "when", "")))
                if marker in seen:
                    continue
                seen.add(marker)
                if getattr(report, "when", "") in {"setup", "call", "teardown"}:
                    reports.append(_classify({
                        "nodeid": report.nodeid,
                        "when": report.when,
                        "outcome": report.outcome,
                        "longrepr": _text(report),
                    }))
    setup_errors = [report for report in reports if report["when"] == "setup"]
    call_failures = [report for report in reports if report["when"] == "call"]
    type_counts = Counter(type_name for report in reports for type_name in report["exception_types"])
    root_counts = Counter(report["root_cause"] for report in reports)
    environment_blocked = bool(setup_errors) and not call_failures and all(
        report["root_cause"] == "WINDOWS_ACL_TEMP_SETUP" for report in setup_errors
    )
    result = {
        "schema_version": "r3-full-pytest-1",
        "captured_at_utc": datetime.now(timezone.utc).isoformat(),
        "python": sys.version,
        "exit_status": int(exitstatus),
        "failed_phase_count": len(reports),
        "setup_error_count": len(setup_errors),
        "call_failure_count": len(call_failures),
        "teardown_failure_count": sum(report["when"] == "teardown" for report in reports),
        "exception_type_counts": dict(sorted(type_counts.items())),
        "root_cause_counts": dict(sorted(root_counts.items())),
        "all_setup_errors_match_windows_acl_temp": environment_blocked,
        "full_pytest_verdict": "ENVIRONMENT_BLOCKED" if environment_blocked else ("FAIL" if reports else "PASS"),
        "failed_reports": reports,
    }
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "full_pytest_report.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    first_three = setup_errors[:3]
    markdown = [
        "# R3 full pytest capture",
        "",
        f"- verdict: `{result['full_pytest_verdict']}`",
        f"- setup errors: `{len(setup_errors)}`",
        f"- call failures: `{len(call_failures)}`",
        f"- exception types: `{dict(sorted(type_counts.items()))}`",
        f"- root causes: `{dict(sorted(root_counts.items()))}`",
        "",
        "## First three setup errors",
        "",
    ]
    for ordinal, report in enumerate(first_three, 1):
        markdown_longrepr = "\n".join(line.rstrip() for line in report["longrepr"].splitlines())
        markdown.extend([f"### {ordinal}. `{report['nodeid']}`", "", "```text", markdown_longrepr, "```", ""])
    markdown.extend(["## All failed phases", "", "The complete records are in `full_pytest_report.json`.", ""])
    for report in reports:
        markdown.append(f"- `{report['when']}` `{report['nodeid']}`: `{report['root_cause']}` / `{report['exception_types']}`")
    (OUTPUT_DIR / "full_pytest_report.md").write_text("\n".join(markdown) + "\n", encoding="utf-8", newline="\n")
