"""Safely promote the audited Issue #32 FIX subset into the production profile.

The quarantine branch is consumed as read-only evidence through ``git show``.
This module deliberately understands both field-level candidate rows and the
later compact ``problem_fields`` blocks; an unknown status or compact change
is a hard error rather than an inferred promotion.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import re
import subprocess
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import Iterable


ACTIVE_STATUSES = frozenset({"QUARANTINED_CANDIDATE", "QUARANTINE_CANDIDATE"})
EXCLUDED_STATUSES = frozenset({
    "WITHDRAWN_AFTER_SIBLING_CHECK", "SUPERSEDED", "HISTORY_ONLY",
    "NON_EFFECTIVE", "WITHDRAWN",
})
KNOWN_STATUSES = ACTIVE_STATUSES | EXCLUDED_STATUSES
APPROVED_PROFILE_STATUSES = frozenset({
    "APPROVED_STATIC", "APPROVED_IDENTITY_ONLY", "APPROVED_SEMANTIC_ROLE",
    "APPROVED_CORRECTION_METADATA",
})
REJECTED_COMPLETENESS_TAGS = frozenset({
    "cervix_removal", "fallopian_tubes_removal", "ovaries_removal",
    "uterus_removal", "spread_eagle",
})
STANDARD_COLUMNS = (
    "special_id", "tag", "field", "current_value", "proposed_value",
    "rule_version", "risk_priority", "evidence_refs", "reason", "status",
    "notes",
)
COMPACT_COLUMNS = (
    "sequence", "special_id", "tag", "rule_version", "risk_priority",
    "problem_fields", "proposed_change", "reason", "evidence_refs", "status",
)
PROMOTION_FIELDS = frozenset({
    "GenerationFamily", "GenerationRole", "PromptUseMode", "FamilyRuleId",
    "CompositionRoleOverride", "ActorRequirementOverride",
    "BodypartRequirementOverride", "ImplementRequirementOverride",
    "PoseRequirementOverride", "CameraRequirementOverride",
    "SpatialAssignmentOverride", "SpecialFlags",
})


class PromotionError(ValueError):
    """Raised for a failed pre-write gate."""


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _git_args(*args: str) -> list[str]:
    root = _repo_root().resolve().as_posix()
    return ["git", "-c", f"safe.directory={root}", *args]


def _run_git(*args: str, text: bool = False):
    return subprocess.run(
        _git_args(*args), cwd=_repo_root(), stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, text=text,
        close_fds=True,
    ).stdout


def _git_bytes(ref: str, path: str) -> bytes:
    try:
        return _run_git("show", f"{ref}:{path}")
    except subprocess.CalledProcessError as exc:
        raise PromotionError(f"Cannot read evidence {ref}:{path}") from exc


def _git_blob(ref: str, path: str) -> str:
    try:
        return _run_git("rev-parse", f"{ref}:{path}", text=True).strip()
    except subprocess.CalledProcessError as exc:
        raise PromotionError(f"Cannot resolve evidence blob {ref}:{path}") from exc


def _candidate_paths(ref: str) -> tuple[str, ...]:
    raw = _run_git(
        "ls-tree", "-r", "--name-only", ref, "validation_quarantine", text=True
    )
    paths = [
        path for path in raw.splitlines()
        if path == "validation_quarantine/candidate_fixes.csv"
        or re.fullmatch(r"validation_quarantine/candidate_fix_blocks/[^/]+\.csv", path)
    ]
    if "validation_quarantine/candidate_fixes.csv" not in paths:
        raise PromotionError("candidate_fixes.csv is missing from evidence ref")
    return tuple(sorted(paths))


def _read_candidate_bytes(
    ref: str | None, candidate_root: Path | None, relative: str,
) -> tuple[bytes, str | None]:
    if ref:
        data = _git_bytes(ref, relative)
        return data, _git_blob(ref, relative)
    assert candidate_root is not None
    path = candidate_root / relative
    if not path.is_file():
        raise PromotionError(f"Candidate file is missing: {path}")
    data = path.read_bytes()
    return data, None


def _status_index(row: list[str], path: str, line: int) -> int:
    indexes = [index for index, value in enumerate(row) if value in KNOWN_STATUSES]
    if len(indexes) != 1:
        raise PromotionError(f"{path}:{line}: expected exactly one known status")
    return indexes[0]


def _standard_candidate(row: list[str], path: str, line: int) -> dict:
    index = _status_index(row, path, line)
    if index < 8:
        raise PromotionError(f"{path}:{line}: malformed standard candidate row")
    # Some quarantine rows left commas in evidence_refs unquoted. The status
    # token is authoritative for recovering the otherwise fixed-width row.
    if len(row) < 11:
        raise PromotionError(f"{path}:{line}: short standard candidate row")
    return {
        "special_id": row[0],
        "tag": row[1],
        "field": row[2],
        "current_value": row[3],
        "proposed_value": row[4],
        "rule_version": row[5],
        "risk_priority": row[6],
        "evidence_refs": ",".join(row[7:index - 1]),
        "reason": row[index - 1],
        "status": row[index],
        "notes": ",".join(row[index + 1:]),
        "source_path": path,
        "source_line": line,
        "source_format": "field-level",
    }


def _compact_value(field: str, change: str, path: str, line: int) -> str:
    if field == "GenerationFamily":
        if "SELF_ACTION" in change:
            return "SELF_ACTION"
        raise PromotionError(f"{path}:{line}: cannot normalize GenerationFamily")
    if field == "SpecialFlags":
        for value in ("ACTOR_SEPARATION_REQUIRED", "SELF_ACTOR_ROLE"):
            if value in change:
                return value
        raise PromotionError(f"{path}:{line}: cannot normalize SpecialFlags")
    short = {
        "ActorRequirementOverride": "actor",
        "BodypartRequirementOverride": "bodypart",
        "ImplementRequirementOverride": "implement",
        "SpatialAssignmentOverride": "spatial",
    }.get(field)
    if field in {"ActorRequirementOverride", "BodypartRequirementOverride"}:
        if re.search(r"actor/bodypart", change, flags=re.IGNORECASE):
            return "true"
    if re.search(rf"(?:{re.escape(field)}|{short or '$^'})\s*=\s*true", change,
                 flags=re.IGNORECASE):
        return "true"
    raise PromotionError(f"{path}:{line}: cannot normalize {field}: {change}")


def _compact_candidates(rows: Iterable[dict], path: str) -> list[dict]:
    result = []
    for line, row in enumerate(rows, 2):
        status = row["status"]
        if status not in KNOWN_STATUSES:
            raise PromotionError(f"{path}:{line}: unknown status {status!r}")
        fields = [field for field in row["problem_fields"].split("+") if field]
        if not fields:
            raise PromotionError(f"{path}:{line}: empty problem_fields")
        for field in fields:
            if field not in PROMOTION_FIELDS:
                raise PromotionError(f"{path}:{line}: unknown candidate field {field}")
            result.append({
                "special_id": row["special_id"],
                "tag": row["tag"],
                "field": field,
                "current_value": None,
                "proposed_value": _compact_value(
                    field, row["proposed_change"], path, line
                ),
                "rule_version": row["rule_version"],
                "risk_priority": row["risk_priority"],
                "evidence_refs": row["evidence_refs"],
                "reason": row["reason"],
                "status": status,
                "notes": row["proposed_change"],
                "source_path": path,
                "source_line": line,
                "source_format": "compact-field-expansion",
                "source_sequence": row["sequence"],
            })
    return result


def load_candidates(
    *, ref: str | None = "origin/dict-validation/quarantine",
    candidate_root: Path | None = None,
) -> tuple[list[dict], list[dict]]:
    if bool(ref) == bool(candidate_root):
        raise PromotionError("Specify exactly one candidate evidence source")
    if ref:
        paths = _candidate_paths(ref)
    else:
        assert candidate_root is not None
        root = candidate_root / "validation_quarantine"
        paths = ("validation_quarantine/candidate_fixes.csv",) + tuple(
            sorted(
                path.relative_to(candidate_root).as_posix()
                for path in (root / "candidate_fix_blocks").glob("*.csv")
            )
        )
    all_candidates: list[dict] = []
    source_files = []
    for path in paths:
        data, blob = _read_candidate_bytes(ref, candidate_root, path)
        source_files.append((path, data, blob))
        text = data.decode("utf-8-sig")
        reader = csv.reader(io.StringIO(text, newline=""))
        header = next(reader, None)
        if header == list(STANDARD_COLUMNS):
            for line, row in enumerate(reader, 2):
                if row:
                    all_candidates.append(_standard_candidate(row, path, line))
        elif header == list(COMPACT_COLUMNS):
            all_candidates.extend(_compact_candidates(
                csv.DictReader(io.StringIO(text, newline="")), path
            ))
        else:
            raise PromotionError(f"{path}: unexpected candidate header")
    return all_candidates, [
        {
            "path": path,
            "blob": blob,
            "bytes": len(data),
            "sha256": _sha256_bytes(data),
        }
        for path, data, blob in source_files
    ]


def _load_profile(path: Path) -> tuple[list[str], list[dict]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames is None:
            raise PromotionError("Production profile has no header")
        rows = list(reader)
        if any(None in row or any(value is None for value in row.values()) for row in rows):
            raise PromotionError("Production profile contains a malformed row")
        return list(reader.fieldnames), rows


def _load_special_identity(path: Path) -> list[tuple[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != [
            "ID", "Tag", "日本語", "Layer", "主カテゴリ", "関連カテゴリ",
            "元カテゴリ", "性別スコープ", "Danbooru種別", "post_count",
            "件数帯", "canonical_target", "元の日本語説明", "検索キー",
        ]:
            raise PromotionError("Unexpected Special identity source schema")
        return [(row["ID"], row["Tag"]) for row in reader]


def _load_family_rule_families(path: Path) -> dict[str, str]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames is None or "FamilyRuleId" not in reader.fieldnames \
                or "GenerationFamily" not in reader.fieldnames:
            raise PromotionError("Unexpected family-rule schema")
        return {row["FamilyRuleId"]: row["GenerationFamily"] for row in reader}


def _identity_hash(identity: list[tuple[str, str]]) -> str:
    return _sha256_bytes(
        "".join(f"{special_id}\t{tag}\n" for special_id, tag in identity).encode()
    )


def _git_file_blob(path: Path) -> str | None:
    try:
        return _run_git(
            "hash-object", "--", path.resolve().as_posix(), text=True
        ).strip()
    except subprocess.CalledProcessError:
        return None


def _protected_paths(root: Path) -> list[Path]:
    paths = sorted(list((root / "data/generation").glob("*")) +
                   list((root / "data/semantic").glob("*")))
    paths += [root / "data/runtime/japanese_overlay.json"]
    paths += [root / "data/special2788/illustrious_tag_knowledge_base_2788.csv"]
    return [path for path in paths if path.is_file()]


def _protected_manifest(root: Path) -> list[dict]:
    result = []
    for path in _protected_paths(root):
        result.append({
            "path": path.relative_to(root).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": _sha256_file(path),
            "git_blob": _git_file_blob(path),
        })
    return result


def _assert_profile_gate(
    profile_path: Path, special_source: Path, candidates: list[dict],
) -> tuple[list[str], list[dict], list[dict], dict]:
    columns, rows = _load_profile(profile_path)
    if len(rows) != 2788:
        raise PromotionError(f"Production profile rows={len(rows)}, expected 2788")
    if len(set(columns)) != len(columns):
        raise PromotionError("Production profile has duplicate columns")
    source_identity = _load_special_identity(special_source)
    profile_identity = [(row["SpecialID"], row["Tag"]) for row in rows]
    if len(set(profile_identity)) != 2788:
        raise PromotionError("Production profile identity is not 2,788 unique rows")
    if profile_identity != source_identity:
        raise PromotionError("Production profile identity/order differs from Special source")
    for candidate in candidates:
        if candidate["field"] not in columns:
            raise PromotionError(
                f"Candidate field {candidate['field']} is not a production column"
            )
    by_id = {row["SpecialID"]: row for row in rows}
    family_rule_families = _load_family_rule_families(
        _repo_root() / "data/generation/generation_family_rules.csv"
    )
    active = [candidate for candidate in candidates if candidate["status"] in ACTIVE_STATUSES]
    excluded = [candidate for candidate in candidates if candidate["status"] in EXCLUDED_STATUSES]
    non_effective = []
    effective = []
    for candidate in active:
        profile_status = by_id[candidate["special_id"]]["PromotionStatus"] if candidate["special_id"] in by_id else None
        if profile_status not in APPROVED_PROFILE_STATUSES:
            candidate = dict(candidate)
            candidate["non_effective_reason"] = (
                f"target profile PromotionStatus={profile_status!r} is not approved"
            )
            non_effective.append(candidate)
        else:
            effective.append(candidate)
    assignments: dict[tuple[str, str], dict] = {}
    for candidate in effective:
        key = (candidate["special_id"], candidate["field"])
        if key in assignments:
            previous = assignments[key]
            if previous["proposed_value"] != candidate["proposed_value"]:
                raise PromotionError(f"Conflicting effective assignment: {key}")
            raise PromotionError(f"Duplicate effective assignment: {key}")
        if candidate["special_id"] not in by_id:
            raise PromotionError(f"Unknown target SpecialID: {candidate['special_id']}")
        if candidate["tag"] != by_id[candidate["special_id"]]["Tag"]:
            raise PromotionError(f"Candidate tag drift for SpecialID {candidate['special_id']}")
        if candidate["tag"] in REJECTED_COMPLETENESS_TAGS:
            raise PromotionError(f"Rejected completeness candidate is present: {candidate['tag']}")
        current = by_id[candidate["special_id"]][candidate["field"]]
        if candidate["current_value"] not in (None, "") and candidate["current_value"] != current:
            raise PromotionError(
                f"Current-value drift for {key}: evidence={candidate['current_value']!r} "
                f"profile={current!r}"
            )
        candidate["current_value"] = current
        assignments[key] = candidate
    for candidate in excluded + non_effective:
        if candidate["special_id"] not in by_id:
            raise PromotionError(f"Unknown excluded target SpecialID: {candidate['special_id']}")
        if candidate["tag"] != by_id[candidate["special_id"]]["Tag"]:
            raise PromotionError(f"Excluded candidate tag drift: {candidate['special_id']}")
        if candidate["tag"] in REJECTED_COMPLETENESS_TAGS:
            raise PromotionError(f"Rejected completeness candidate is present: {candidate['tag']}")
    invalid_specials = {}
    grouped: dict[str, list[dict]] = defaultdict(list)
    for candidate in effective:
        grouped[candidate["special_id"]].append(candidate)
    for special_id, assignments_for_special in grouped.items():
        staged = dict(by_id[special_id])
        for candidate in assignments_for_special:
            staged[candidate["field"]] = candidate["proposed_value"]
        family_rule = staged["FamilyRuleId"]
        if family_rule and family_rule_families.get(family_rule) != staged["GenerationFamily"]:
            invalid_specials[special_id] = (
                "staged GenerationFamily does not match staged FamilyRuleId"
            )
    if invalid_specials:
        retained = []
        for candidate in effective:
            reason = invalid_specials.get(candidate["special_id"])
            if reason:
                parked = dict(candidate)
                parked["non_effective_reason"] = reason
                non_effective.append(parked)
            else:
                retained.append(candidate)
        effective = retained
    assignments = {(candidate["special_id"], candidate["field"]): candidate
                   for candidate in effective}
    affected = []
    for special_id in (row["SpecialID"] for row in rows):
        if special_id in {sid for sid, _ in assignments}:
            affected.append(special_id)
    source_active_rows = {
        (candidate["source_path"], candidate["source_line"])
        for candidate in active
    }
    source_excluded_rows = {
        (candidate["source_path"], candidate["source_line"])
        for candidate in excluded
    }
    counts = {
        "profile_rows": len(rows),
        "profile_unique_identities": len(set(profile_identity)),
        "source_special_rows": len(source_identity),
        "candidate_source_active_rows": len(source_active_rows),
        "candidate_source_excluded_rows": len(source_excluded_rows),
        "candidate_source_active_field_assignments": len(active),
        "candidate_source_excluded_field_assignments": len(excluded),
        "source_non_effective_candidate_rows": len(non_effective),
        "effective_field_assignments": len(effective),
        "affected_specials": len(affected),
        "conflicting_effective_assignments": 0,
        "target_specials_exactly_once": len(affected),
    }
    return columns, rows, effective, {
        "counts": counts,
        "identity_hash": _identity_hash(profile_identity),
        "affected_special_ids": affected,
        "excluded_candidates": excluded,
        "non_effective_candidates": non_effective,
    }


def _write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _write_profile_atomic(path: Path, columns: list[str], rows: list[dict]) -> None:
    fd, temporary = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".building", dir=path.parent
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=columns, lineterminator="\r\n")
            writer.writeheader()
            writer.writerows(rows)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except Exception:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def _write_bytes_atomic(path: Path, data: bytes) -> None:
    fd, temporary = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".building", dir=path.parent
    )
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except Exception:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def _apply_and_report(
    profile_path: Path, columns: list[str], rows: list[dict], effective: list[dict],
    before_rows: list[dict], before_protected: list[dict], integrity_path: Path,
    diff_path: Path, before_sha256: str,
) -> dict:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for candidate in effective:
        grouped[candidate["special_id"]].append(candidate)
    staged = [dict(row) for row in rows]
    indexes = {row["SpecialID"]: index for index, row in enumerate(rows)}
    for special_id, assignments in grouped.items():
        staged_row = dict(rows[indexes[special_id]])
        for candidate in assignments:
            if (candidate["current_value"] not in (None, "")
                    and staged_row[candidate["field"]] != candidate["current_value"]):
                raise PromotionError(
                    f"Atomic group current-value drift for SpecialID {special_id}"
                )
            staged_row[candidate["field"]] = candidate["proposed_value"]
        staged[indexes[special_id]] = staged_row
    _write_profile_atomic(profile_path, columns, staged)
    after_hash = _sha256_file(profile_path)
    after_columns, after_rows = _load_profile(profile_path)
    if after_columns != columns or len(after_rows) != 2788:
        raise PromotionError("Post-write profile schema/row-count gate failed")
    before_identity = [(row["SpecialID"], row["Tag"]) for row in before_rows]
    after_identity = [(row["SpecialID"], row["Tag"]) for row in after_rows]
    if before_identity != after_identity:
        raise PromotionError("Post-write identity/order gate failed")
    changed = []
    candidate_keys = {(c["special_id"], c["field"]): c for c in effective}
    for before, after in zip(before_rows, after_rows):
        for field in columns:
            if before[field] != after[field]:
                key = (before["SpecialID"], field)
                candidate = candidate_keys.get(key)
                if candidate is None:
                    raise PromotionError(f"Non-candidate field changed: {key}")
                if after[field] != candidate["proposed_value"]:
                    raise PromotionError(f"Candidate value mismatch after write: {key}")
                changed.append({
                    "special_id": before["SpecialID"],
                    "tag": before["Tag"],
                    "field": field,
                    "before": before[field],
                    "after": after[field],
                    "source_path": candidate["source_path"],
                    "source_line": candidate["source_line"],
                    "evidence_refs": candidate["evidence_refs"],
                    "reason": candidate["reason"],
                })
    if len(changed) != len({(c["special_id"], c["field"]) for c in effective if c["current_value"] != c["proposed_value"]}):
        raise PromotionError("Applied changed-cell count does not match effective assignments")
    after_protected = _protected_manifest(_repo_root())
    before_by_path = {item["path"]: item for item in before_protected}
    after_by_path = {item["path"]: item for item in after_protected}
    if set(before_by_path) != set(after_by_path):
        raise PromotionError("Protected file set changed during promotion")
    protected_changes = [
        path for path in before_by_path
        if before_by_path[path]["sha256"] != after_by_path[path]["sha256"]
        and path != profile_path.relative_to(_repo_root()).as_posix()
    ]
    if protected_changes:
        raise PromotionError(f"Protected non-target files changed: {protected_changes}")
    semantic_paths = [item["path"] for item in before_protected
                      if item["path"].startswith("data/semantic/")]
    if any(before_by_path[path]["sha256"] != after_by_path[path]["sha256"] for path in semantic_paths):
        raise PromotionError("Semantic data changed during promotion")
    diff = {
        "issue": 49,
        "profile": profile_path.relative_to(_repo_root()).as_posix(),
        "before_sha256": before_sha256,
        "after_sha256": after_hash,
        "changed_cell_count": len(changed),
        "effective_assignment_count": len(effective),
        "no_non_candidate_field_changes": True,
        "identity_order_unchanged": True,
        "semantic_data_unchanged": True,
        "rejected_completeness_candidates_added": 0,
        "changed_cells": changed,
    }
    _write_json(integrity_path, {
        "issue": 49,
        "protected_before": before_protected,
        "protected_after": after_protected,
        "non_target_protected_changes": protected_changes,
        "semantic_paths_unchanged": semantic_paths,
    })
    _write_json(diff_path, diff)
    return {
        "after_sha256": after_hash,
        "changed_cell_count": len(changed),
        "diff_report": diff_path.relative_to(_repo_root()).as_posix(),
        "integrity_report": integrity_path.relative_to(_repo_root()).as_posix(),
    }


def run(args: argparse.Namespace) -> dict:
    root = _repo_root()
    profile_path = (root / args.profile).resolve()
    special_source = (root / args.special_source).resolve()
    candidate_root = (root / args.candidate_root).resolve() if args.candidate_root else None
    if args.restore_baseline_ref:
        profile_relative = Path(args.profile).as_posix()
        data = _git_bytes(args.restore_baseline_ref, profile_relative)
        if profile_relative == "data/generation/special2788_generation_profile.csv":
            data = data.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
        _write_bytes_atomic(profile_path, data)
        print(json.dumps({"restored": profile_relative, "sha256": _sha256_bytes(data)}))
        return {"verdict": "BASELINE_RESTORED"}
    candidates, source_files = load_candidates(ref=args.candidate_ref, candidate_root=candidate_root)
    columns, rows, effective, gate = _assert_profile_gate(
        profile_path, special_source, candidates
    )
    before_profile_bytes = profile_path.read_bytes()
    before_profile = {
        "path": profile_path.relative_to(root).as_posix(),
        "bytes": len(before_profile_bytes),
        "sha256": _sha256_bytes(before_profile_bytes),
        "git_blob": _git_file_blob(profile_path),
        "row_count": len(rows),
        "identity_hash": gate["identity_hash"],
    }
    protected_before = _protected_manifest(root)
    manifest = {
        "schema_version": "issue49-effective-candidate-v1",
        "issue": 49,
        "source_ref": args.candidate_ref,
        "source_files": source_files,
        "production_base": before_profile,
        "counts": gate["counts"],
        "affected_special_ids": gate["affected_special_ids"],
        "effective_candidates": effective,
        "excluded_candidates": gate["excluded_candidates"],
        "non_effective_candidates": gate["non_effective_candidates"],
        "excluded_statuses": sorted(EXCLUDED_STATUSES),
        "rejected_completeness_tags": sorted(REJECTED_COMPLETENESS_TAGS),
        "protected_before": protected_before,
        "conflicting_effective_assignments": [],
    }
    manifest_path = root / args.manifest
    _write_json(manifest_path, manifest)
    if args.apply:
        result = _apply_and_report(
            profile_path, columns, rows, effective, rows, protected_before,
            root / args.integrity_report, root / args.diff_report,
            before_profile["sha256"],
        )
        manifest["production_after"] = result
        manifest["verdict"] = "READY_FOR_POST_WRITE_AUDIT"
        _write_json(manifest_path, manifest)
    else:
        manifest["verdict"] = "PREFLIGHT_PASS"
        _write_json(manifest_path, manifest)
    return manifest


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", default="data/generation/special2788_generation_profile.csv")
    parser.add_argument("--special-source", default="data/special2788/illustrious_tag_knowledge_base_2788.csv")
    parser.add_argument("--candidate-ref", default="origin/dict-validation/quarantine")
    parser.add_argument("--candidate-root")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--integrity-report", default="docs/issue49/protected_data_integrity.json")
    parser.add_argument("--diff-report", default="docs/issue49/applied_diff_report.json")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--restore-baseline-ref")
    return parser


if __name__ == "__main__":
    try:
        result = run(build_parser().parse_args())
    except PromotionError as exc:
        raise SystemExit(f"HOLD_PROMOTION_IMPLEMENTATION: {exc}")
    print(json.dumps({
        "verdict": result.get("verdict"),
        "counts": result.get("counts"),
        "manifest": result.get("schema_version"),
    }, ensure_ascii=False))
