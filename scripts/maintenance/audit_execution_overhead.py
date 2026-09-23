#!/usr/bin/env python3
"""Warn about repository patterns that can create execution overhead.

Issue #188 foundation checker.
Default mode is advisory: warnings do not fail the command.
Use --strict to return non-zero when warnings are present.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def warn(items: list[str], message: str) -> None:
    items.append(message)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()

    warnings: list[str] = []

    current_state = ROOT / "docs/project/CURRENT_STATE.md"
    if current_state.exists():
        text = read_text(current_state)
        size = len(text.encode("utf-8"))
        dated = re.findall(r"^## .*20\d{2}-\d{2}-\d{2}.*$", text, flags=re.M)
        if size > 12_000:
            warn(warnings, f"CURRENT_STATE is large ({size} bytes); keep current routing compact and archive history.")
        if len(dated) > 1:
            warn(warnings, f"CURRENT_STATE contains {len(dated)} dated top-level sections; current state should not accumulate routing history.")
        history = ROOT / "docs/project/CURRENT_STATE_HISTORY.md"
        if not history.exists():
            warn(warnings, "CURRENT_STATE_HISTORY.md is missing; historical state should not be stacked back into CURRENT_STATE.")

    routing = ROOT / "docs/project/CURRENT_ROUTING.json"
    if not routing.exists():
        warn(warnings, "docs/project/CURRENT_ROUTING.json is missing.")
    else:
        try:
            data = json.loads(read_text(routing))
            if data.get("schema_version") != "project-current-routing-v1":
                warn(warnings, "CURRENT_ROUTING schema_version is unexpected.")
            lanes = data.get("active_lanes")
            if not isinstance(lanes, list):
                warn(warnings, "CURRENT_ROUTING active_lanes must be a list.")
            else:
                issue_ids = [x.get("issue") for x in lanes if isinstance(x, dict)]
                if len(issue_ids) != len(set(issue_ids)):
                    warn(warnings, "CURRENT_ROUTING contains duplicate active issue IDs.")
                state_text = read_text(current_state) if current_state.exists() else ""
                for lane in lanes:
                    if not isinstance(lane, dict):
                        continue
                    issue = lane.get("issue")
                    branch = lane.get("branch")
                    if issue is not None and f"#{issue}" not in state_text:
                        warn(warnings, f"CURRENT_ROUTING issue #{issue} is missing from CURRENT_STATE summary.")
                    kind = lane.get("kind")
                    if kind != "project_infrastructure" and branch and branch.startswith(("research/", "dev/", "audit/", "codex/")) and branch not in state_text:
                        warn(warnings, f"CURRENT_ROUTING branch {branch} is missing from CURRENT_STATE summary.")
        except Exception as exc:
            warn(warnings, f"CURRENT_ROUTING is invalid JSON: {exc}")

    workflows = ROOT / ".github/workflows"
    if workflows.exists():
        for wf in sorted(workflows.glob("*.yml")):
            text = read_text(wf)
            # Advisory heuristic: branch-wide push workflows without paths/path-ignore
            # deserve review if they run heavy audit/build work on every tiny commit.
            if re.search(r"(?m)^\s*push:\s*$", text):
                has_paths = bool(re.search(r"(?m)^\s+paths(?:-ignore)?:\s*$", text))
                heavy_words = any(word in text.lower() for word in ("full", "audit", "artifact", "build"))
                if not has_paths and heavy_words:
                    warn(warnings, f"{wf.relative_to(ROOT)}: push workflow looks broad and heavy but has no paths filter.")

    dev_task = ROOT / "docs/project/CURRENT_DEV_TASK.md"
    if dev_task.exists() and len(read_text(dev_task).encode("utf-8")) > 4_000:
        warn(warnings, "CURRENT_DEV_TASK is growing into a second routing authority; keep it as a compact compatibility pointer.")

    docs = ROOT / "docs"
    state_like = []
    if docs.exists():
        for p in docs.rglob("*"):
            if p.is_file() and re.search(r"(status|progress|checkpoint|current_state|manifest)", p.name, re.I):
                state_like.append(p)
    if len(state_like) > 200:
        warn(warnings, f"Repository has {len(state_like)} state/progress/manifest/checkpoint-like files; keep authority/cache roles explicit.")

    print("Execution overhead audit")
    if warnings:
        for item in warnings:
            print(f"WARN: {item}")
    else:
        print("PASS: no advisory findings")

    print(f"warnings={len(warnings)}")
    return 1 if args.strict and warnings else 0


if __name__ == "__main__":
    raise SystemExit(main())
