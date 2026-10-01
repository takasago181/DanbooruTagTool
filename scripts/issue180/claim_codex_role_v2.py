#!/usr/bin/env python3
"""Atomically claim one Issue #180 Codex role from a detached managed worktree.

All five chats may start from the same canonical branch/commit.  Role claim uses
five dedicated remote refs as one-shot locks.  No git fetch is required.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import uuid
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CANONICAL_BRANCH = "research/issue180-single-home-pilot"

@dataclass(frozen=True)
class RoleSpec:
    role: str
    target_branch: str
    claim_branch: str
    slot: int | None

ROLE_SPECS = (
    RoleSpec("FORWARD_0", "research/issue180-forward-0", "research/issue180-claim-forward-0", 0),
    RoleSpec("FORWARD_1", "research/issue180-forward-1", "research/issue180-claim-forward-1", 1),
    RoleSpec("FORWARD_2", "research/issue180-forward-2", "research/issue180-claim-forward-2", 2),
    RoleSpec("FORWARD_3", "research/issue180-forward-3", "research/issue180-claim-forward-3", 3),
    RoleSpec("QA", "research/issue180-qa-integrator", "research/issue180-claim-qa", None),
)

def git(*args: str, check: bool = True, input_text: str | None = None, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        text=True,
        input=input_text,
        capture_output=True,
        env=env,
    )
    if check and proc.returncode:
        raise SystemExit(f"git {' '.join(args)} failed: {proc.stderr.strip() or proc.stdout.strip()}")
    return proc

def remote_sha(branch: str) -> str | None:
    proc = git("ls-remote", "--heads", "origin", f"refs/heads/{branch}", check=False)
    if proc.returncode:
        raise SystemExit(f"git ls-remote failed for {branch}: {proc.stderr.strip() or proc.stdout.strip()}")
    line = proc.stdout.strip()
    return line.split()[0] if line else None

def current_head() -> str:
    return git("rev-parse", "HEAD").stdout.strip()

def role_from_history() -> RoleSpec | None:
    proc = git("log", "-40", "--format=%B%x00", check=False)
    if proc.returncode:
        return None
    for message in proc.stdout.split("\x00"):
        if "issue180-role-claim-v2" not in message:
            continue
        fields: dict[str, str] = {}
        for line in message.splitlines():
            if "=" in line:
                key, value = line.split("=", 1)
                fields[key.strip()] = value.strip()
        branch = fields.get("target_branch")
        for spec in ROLE_SPECS:
            if spec.target_branch == branch:
                return spec
    return None

def emit(spec: RoleSpec, canonical_sha: str, claim_sha: str, reused: bool) -> None:
    print(json.dumps({
        "status": "ROLE_READY",
        "role": spec.role,
        "slot": spec.slot,
        "target_branch": spec.target_branch,
        "claim_branch": spec.claim_branch,
        "canonical_sha_at_claim": canonical_sha,
        "head": current_head(),
        "claim_commit": claim_sha,
        "reused_existing_claim": reused,
        "standard_git_fetch_required": False,
    }, ensure_ascii=False, indent=2))

def main() -> None:
    existing = role_from_history()
    canonical_sha = remote_sha(CANONICAL_BRANCH)
    if not canonical_sha:
        raise SystemExit("ROLE_CLAIM_BLOCKED: canonical branch is not visible through git ls-remote")

    if existing is not None:
        emit(existing, canonical_sha, current_head(), True)
        return

    head = current_head()
    if head != canonical_sha:
        raise SystemExit(
            "ROLE_CLAIM_BLOCKED: this managed worktree did not start from the current "
            f"{CANONICAL_BRANCH}. Start a new Worktree from that same branch. "
            f"HEAD={head} canonical={canonical_sha}"
        )

    tree = git("rev-parse", f"{head}^{{tree}}").stdout.strip()
    base_env = os.environ.copy()
    base_env.setdefault("GIT_AUTHOR_NAME", "Issue180 Codex Role Claim")
    base_env.setdefault("GIT_AUTHOR_EMAIL", "issue180-codex-role-claim@local.invalid")
    base_env.setdefault("GIT_COMMITTER_NAME", base_env["GIT_AUTHOR_NAME"])
    base_env.setdefault("GIT_COMMITTER_EMAIL", base_env["GIT_AUTHOR_EMAIL"])

    for spec in ROLE_SPECS:
        tip = remote_sha(spec.claim_branch)
        if tip is None:
            raise SystemExit(
                f"ROLE_CLAIM_BLOCKED: missing claim ref {spec.claim_branch}; "
                "the #180 launch baseline is incomplete"
            )
        if tip != canonical_sha:
            continue

        token = uuid.uuid4().hex
        message = (
            "issue180-role-claim-v2\n"
            f"role={spec.role}\n"
            f"target_branch={spec.target_branch}\n"
            f"claim_branch={spec.claim_branch}\n"
            f"canonical_sha={canonical_sha}\n"
            f"token={token}\n"
        )
        claim = git("commit-tree", tree, "-p", canonical_sha, input_text=message, env=base_env).stdout.strip()

        push = git(
            "push",
            "origin",
            f"{claim}:refs/heads/{spec.claim_branch}",
            check=False,
        )
        if push.returncode:
            # Another Codex chat won this role between ls-remote and push.
            continue

        git("checkout", "--detach", claim)
        emit(spec, canonical_sha, claim, False)
        return

    raise SystemExit(
        "ROLE_CLAIM_BLOCKED: all five Issue #180 roles are already claimed. "
        "Do not create a sixth worker."
    )

if __name__ == "__main__":
    main()
