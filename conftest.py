"""Opt-in machine verdict for the Issue 28 real-application pytest gate."""
import json
import hashlib
import platform
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone

from tools.e2e_verdict import build_result, markdown


def pytest_addoption(parser):
    parser.addoption("--e2e-report", metavar="PATH", help="Write Issue 28 JSON and sibling Markdown verdict")


def pytest_configure(config):
    if config.getoption("--e2e-report"):
        config.pluginmanager.register(E2EReport(config), "issue28-evidence")


class E2EReport:
    def __init__(self, config):
        self.config = config
        self.reports = []
        self.path = Path(config.getoption("--e2e-report"))
        # Invalidate an older PASS before any tests start. A crash/interruption
        # must leave an incomplete verdict, never a stale green artifact.
        self.write(build_result([], 0, {"state": "started; run not completed"}))

    def write(self, result):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.with_suffix(".md").write_text(markdown(result), encoding="utf-8")
        self.path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def pytest_runtest_logreport(self, report):
        self.reports.append({"nodeid": report.nodeid, "when": report.when,
                             "outcome": report.outcome, "duration": report.duration,
                             "detail": str(report.longrepr) if report.longrepr else "",
                             "evidence": dict(report.user_properties) if report.when == "call" else {}})

    def pytest_sessionfinish(self, session, exitstatus):
        root = str(self.config.rootpath)
        git = ["git", "-c", f"safe.directory={root}", "-C", root]
        def read_git(*args):
            return subprocess.run([*git, *args], stdin=subprocess.DEVNULL,
                                  capture_output=True, text=True, check=True).stdout.strip()
        environment = {"platform": platform.platform(), "python": sys.version,
                       "utc": datetime.now(timezone.utc).isoformat(),
                       "command": [sys.executable, "-m", "pytest", *self.config.invocation_params.args],
                       "commit": read_git("rev-parse", "HEAD"),
                       "working_tree": read_git("status", "--short"),
                       "scope": "local protected-data environment; withdrawn real Tk; no mocks"}
        paths = ["conftest.py", "tools/e2e_verdict.py", "tests/test_e2e_functional.py",
                 "danbooru_tag_tool/ui.py", "danbooru_tag_tool/stage9c_session.py",
                 "danbooru_tag_tool/stage9b_runtime.py", "danbooru_tag_tool/prompt_composer.py"]
        environment["tested_file_sha256"] = {
            name: hashlib.sha256((Path(root) / name).read_bytes()).hexdigest() for name in paths}
        result = build_result(self.reports, int(exitstatus), environment)
        self.write(result)
        # A skip-only run must not look green to a caller checking exit status.
        if result["verdict"] == "BLOCKED" and int(exitstatus) in (0, 5):
            session.exitstatus = 2
