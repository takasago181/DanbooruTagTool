#!/usr/bin/env python3
"""Publish one Issue #70 checkpoint with fetch/rebase/push retries.

This helper is intended for a dedicated worker checkout. It never force-pushes,
never stages unrelated files, and treats same-file merge conflicts as a
retryable safety stop rather than overwriting another worker.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ALLOWED_PREFIXES = (
    "docs/issue70/data/queue_state.json",
    "docs/issue70/data/results/queue/",
    "docs/issue70/data/final_completion.json",
)


class PublishError(RuntimeError):
    pass


def git(repo: Path, *args: str, check: bool = True) -> str:
    result = subprocess.run(
        ["git", *args], cwd=repo, text=True, capture_output=True, encoding="utf-8"
    )
    if check and result.returncode:
        raise PublishError((result.stderr or result.stdout).strip())
    return result.stdout


def porcelain_paths(repo: Path) -> list[str]:
    paths: list[str] = []
    for line in git(repo, "status", "--porcelain=v1", "--untracked-files=all").splitlines():
        if not line:
            continue
        value = line[3:]
        if " -> " in value:
            value = value.split(" -> ", 1)[1]
        paths.append(value)
    return paths


def is_allowed_path(path: str) -> bool:
    return any(path == prefix or path.startswith(prefix) for prefix in ALLOWED_PREFIXES)


def ensure_only_issue70_changes(repo: Path) -> list[str]:
    paths = porcelain_paths(repo)
    unsafe = [path for path in paths if not is_allowed_path(path)]
    if unsafe:
        raise PublishError(f"refusing to publish unrelated changes: {unsafe}")
    if not paths:
        raise PublishError("no Issue #70 checkpoint changes to publish")
    return paths


def publish(repo: Path, message: str, retries: int) -> str:
    paths = ensure_only_issue70_changes(repo)
    git(repo, "fetch", "origin", "main")
    # Commit before rebasing so the worker change can be replayed as one unit.
    git(repo, "add", "--", *paths)
    git(repo, "commit", "-m", message)
    for attempt in range(1, retries + 1):
        git(repo, "fetch", "origin", "main")
        upstream = git(repo, "rev-parse", "origin/main").strip()
        head = git(repo, "rev-parse", "HEAD").strip()
        if head != upstream:
            rebase = subprocess.run(["git", "rebase", upstream], cwd=repo, text=True, capture_output=True, encoding="utf-8")
            if rebase.returncode:
                subprocess.run(["git", "rebase", "--abort"], cwd=repo, text=True, capture_output=True, encoding="utf-8")
                raise PublishError("rebase conflict with another Issue #70 writer; retry from latest main")
        pushed = subprocess.run(["git", "push", "origin", "HEAD:refs/heads/main"], cwd=repo, text=True, capture_output=True, encoding="utf-8")
        if pushed.returncode == 0:
            return git(repo, "rev-parse", "HEAD").strip()
        if attempt == retries:
            raise PublishError((pushed.stderr or pushed.stdout).strip())
    raise PublishError("checkpoint publish exhausted retries")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--message", default="Issue #70: publish translation checkpoint")
    parser.add_argument("--retries", type=int, default=4)
    args = parser.parse_args(argv)
    try:
        print(publish(Path(args.repo).resolve(), args.message, args.retries))
        return 0
    except PublishError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
