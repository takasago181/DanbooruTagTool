#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

AUTHORITY_REL = Path("docs/issue132/parallel/RUNTIME_AUTHORITY.json")


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def identity_order_sha(rows: list[dict[str, str]]) -> str:
    payload = "".join(row["identity_key"] + "\n" for row in rows).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def load_runtime(root: Path) -> tuple[dict, dict, dict, list[str]]:
    errors: list[str] = []
    try:
        authority = json.loads((root / AUTHORITY_REL).read_text(encoding="utf-8"))
    except Exception as exc:
        return {}, {}, {}, [f"runtime authority unreadable: {exc}"]

    if authority.get("schema_version") != "issue132-runtime-authority-v4-codex-direct":
        errors.append("runtime authority schema mismatch")
    if authority.get("branch") != "research/taxonomy-usability-audit":
        errors.append("runtime authority branch mismatch")
    if authority.get("execution_driver") != "CODEX":
        errors.append("execution driver must be CODEX")

    guide = authority.get("runtime_guide", {})
    guide_path = root / str(guide.get("path", ""))
    if not guide_path.is_file():
        errors.append("runtime guide missing")
    elif git_blob_sha(guide_path) != guide.get("git_blob_sha"):
        errors.append("runtime guide git blob mismatch")

    sem = authority.get("semantic_contract", {})
    sem_path = root / str(sem.get("path", ""))
    contract: dict = {}
    if not sem_path.is_file():
        errors.append("semantic contract missing")
    else:
        try:
            contract = json.loads(sem_path.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"semantic contract unreadable: {exc}")
        if git_blob_sha(sem_path) != sem.get("git_blob_sha"):
            errors.append("semantic contract git blob mismatch")
        if contract.get("schema_version") != sem.get("schema_version"):
            errors.append("semantic contract schema mismatch")

    qa_path = root / str(authority.get("qa_state_path", ""))
    qa: dict = {}
    if not qa_path.is_file():
        errors.append("QA state missing")
    else:
        try:
            qa = json.loads(qa_path.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"QA state unreadable: {exc}")
    if qa and qa.get("schema_version") != "issue132-codex-qa-state-v2-direct":
        errors.append("QA state schema mismatch")

    fixed = authority.get("fixed", {})
    neutral_path = root / str(fixed.get("neutral_path", ""))
    if not neutral_path.is_file():
        errors.append("neutral input missing")
    else:
        if sha256_file(neutral_path) != fixed.get("parent_neutral_sha256"):
            errors.append("neutral input SHA mismatch")
        rows = read_csv(neutral_path)
        if len(rows) != 31003:
            errors.append(f"neutral population mismatch: {len(rows)}")
        if rows and identity_order_sha(rows) != fixed.get("parent_identity_order_sha256"):
            errors.append("neutral identity-order SHA mismatch")


    baseline_meta = authority.get("baseline", {})
    baseline_manifest_path = root / str(baseline_meta.get("manifest_path", ""))
    if not baseline_manifest_path.is_file():
        errors.append("Codex baseline manifest missing")
    else:
        try:
            baseline_manifest = json.loads(
                baseline_manifest_path.read_text(encoding="utf-8")
            )
        except Exception as exc:
            errors.append(f"Codex baseline manifest unreadable: {exc}")
            baseline_manifest = {}
        if baseline_manifest:
            if baseline_manifest.get("schema_version") != "issue132-codex-baseline-manifest-v1":
                errors.append("Codex baseline manifest schema mismatch")
            if baseline_manifest.get("parent_neutral_sha256") != fixed.get("parent_neutral_sha256"):
                errors.append("Codex baseline neutral SHA mismatch")
            if (
                baseline_manifest.get("parent_identity_order_sha256")
                != fixed.get("parent_identity_order_sha256")
            ):
                errors.append("Codex baseline identity-order SHA mismatch")
            saved_ends = baseline_meta.get("saved_end_by_lane", {})
            for lane in ("1", "2", "3"):
                entry = baseline_manifest.get("lanes", {}).get(lane, {})
                if entry.get("lane_local_end") != saved_ends.get(lane):
                    errors.append(f"Codex baseline lane {lane} saved end mismatch")
                path = root / str(entry.get("path", ""))
                if not path.is_file():
                    errors.append(f"Codex baseline lane {lane} file missing")
                elif sha256_file(path) != entry.get("sha256"):
                    errors.append(f"Codex baseline lane {lane} SHA mismatch")

    if contract:
        current_policy_id = sem.get("current_policy_id")
        allowed_policies = sem.get("allowed_policies", {})
        if current_policy_id not in allowed_policies:
            errors.append("current semantic policy is not registered")
        else:
            current_meta = allowed_policies[current_policy_id]
            if current_meta.get("git_blob_sha") != sem.get("git_blob_sha"):
                errors.append("current semantic policy blob registry mismatch")
            if current_meta.get("path") != sem.get("path"):
                errors.append("current semantic policy path registry mismatch")
        if contract.get("population") != 31003:
            errors.append("semantic contract population mismatch")
        neutral = contract.get("neutral", {})
        if neutral.get("sha256") != fixed.get("parent_neutral_sha256"):
            errors.append("semantic contract neutral SHA mismatch")
        if neutral.get("identity_order_sha256") != fixed.get("parent_identity_order_sha256"):
            errors.append("semantic contract identity-order SHA mismatch")

    return authority, contract, qa, errors


def direct_start(authority: dict, lane: int) -> int:
    return int(authority["fixed"]["direct_staging_effective_from_lane_local"][str(lane)])


def allowed_forward_end(qa: dict, lane: int) -> int:
    return int(qa["allowed_forward_end_by_lane"][str(lane)])


def policy_id(authority: dict) -> str:
    return str(authority["semantic_contract"]["current_policy_id"])


def policy_blob(authority: dict) -> str:
    return str(authority["semantic_contract"]["git_blob_sha"])


def load_baseline_manifest(root: Path, authority: dict) -> dict:
    path = root / authority["baseline"]["manifest_path"]
    return json.loads(path.read_text(encoding="utf-8"))


def load_baseline_lane(root: Path, manifest: dict, lane: int) -> dict:
    entry = manifest["lanes"][str(lane)]
    path = root / entry["path"]
    return json.loads(path.read_text(encoding="utf-8"))
