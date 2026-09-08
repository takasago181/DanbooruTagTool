"""Normalize Issue #41 frozen batch decisions into the audited R3 evidence schema.

Inputs remain quarantine-only. Approved semantic/display/search records from
batch01..08 become ``SEMANTIC_SCOPE`` + ``WORDING_CANDIDATE`` evidence. The
explicit unresolved batch09 rows become ``IDENTITY_ONLY`` REVIEW evidence so
lack of scope cannot accidentally disappear during R3 execution.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable, Mapping

APPROVED_FILES = tuple(f"issue41_input_batch{i:02d}.jsonl" for i in range(1, 9))
REVIEW_FILE = "issue41_unresolved_review_batch09.jsonl"


def _canonical_bytes(value: Mapping[str, Any]) -> bytes:
    return json.dumps(
        dict(value), ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def _row_identity(row: Mapping[str, Any]) -> str:
    existing = str(row.get("content_identity", "")).strip()
    if existing:
        return existing
    return "sha256:" + hashlib.sha256(_canonical_bytes(row)).hexdigest()


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(path)
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        if not isinstance(row, dict):
            raise ValueError(f"{path}:{line_number}: JSONL record must be an object")
        rows.append(row)
    return rows


def _write_jsonl(path: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    path.write_text(
        "".join(
            json.dumps(
                dict(row), ensure_ascii=False, sort_keys=True, separators=(",", ":")
            )
            + "\n"
            for row in rows
        ),
        encoding="utf-8",
        newline="\n",
    )


def _source_type(scope_basis: str) -> str:
    if scope_basis == "TRANSPARENT_CANONICAL_COMPOSITION":
        return "transparent_canonical_composition"
    if scope_basis == "DANBOORU_WIKI_EXACT_CANONICAL":
        return "danbooru_wiki_exact_canonical"
    if scope_basis:
        return scope_basis.lower()
    return "issue41_frozen_semantic_review"


def _validate_input_row(
    row: Mapping[str, Any], *, review: bool
) -> tuple[str, int]:
    canonical = str(row.get("canonical", "")).strip()
    if not canonical:
        raise ValueError("Issue #41 input row has blank canonical")
    try:
        ordinal = int(row.get("pilot_ordinal"))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Issue #41 input row has invalid ordinal: {canonical}") from exc
    if row.get("frozen") is not True:
        raise ValueError(f"Issue #41 input row is not frozen: {canonical}")
    if review:
        if row.get("decision_state") != "REVIEW":
            raise ValueError(f"batch09 row is not explicit REVIEW: {canonical}")
    else:
        if not str(row.get("semantic_scope", "")).strip():
            raise ValueError(f"approved row lacks semantic_scope: {canonical}")
        if not str(row.get("display_candidate", "")).strip():
            raise ValueError(f"approved row lacks display_candidate: {canonical}")
    return canonical, ordinal


def normalize(root: Path, *, output_dir: Path | None = None) -> dict[str, Any]:
    source_dir = root / "translation_quarantine" / "r3"
    output_dir = output_dir or source_dir

    approved: list[tuple[Path, dict[str, Any]]] = []
    for name in APPROVED_FILES:
        path = source_dir / name
        approved.extend((path, row) for row in _read_jsonl(path))
    review_path = source_dir / REVIEW_FILE
    review = [(review_path, row) for row in _read_jsonl(review_path)]

    all_rows = [row for _, row in approved] + [row for _, row in review]
    canonicals: set[str] = set()
    ordinals: set[int] = set()
    for path, row in approved:
        canonical, ordinal = _validate_input_row(row, review=False)
        if canonical in canonicals:
            raise ValueError(f"duplicate canonical across Issue #41 batches: {canonical}")
        if ordinal in ordinals:
            raise ValueError(
                f"duplicate pilot ordinal across Issue #41 batches: {ordinal}"
            )
        canonicals.add(canonical)
        ordinals.add(ordinal)
    for path, row in review:
        canonical, ordinal = _validate_input_row(row, review=True)
        if canonical in canonicals:
            raise ValueError(f"duplicate canonical across Issue #41 batches: {canonical}")
        if ordinal in ordinals:
            raise ValueError(
                f"duplicate pilot ordinal across Issue #41 batches: {ordinal}"
            )
        canonicals.add(canonical)
        ordinals.add(ordinal)

    if len(all_rows) != 100:
        raise ValueError(
            f"Issue #41 frozen decision set must contain 100 rows, got {len(all_rows)}"
        )
    if ordinals != set(range(1, 101)):
        missing = sorted(set(range(1, 101)) - ordinals)
        extra = sorted(ordinals - set(range(1, 101)))
        raise ValueError(
            f"fixed pilot ordinals are not 1..100; missing={missing}, extra={extra}"
        )

    evidence: list[dict[str, Any]] = []
    ledger: list[dict[str, Any]] = []

    for path, row in approved:
        canonical = str(row["canonical"])
        ordinal = int(row["pilot_ordinal"])
        batch = str(row.get("issue41_batch", ""))
        row_identity = _row_identity(row)
        source_ref = str(
            row.get("source_url")
            or row.get("semantic_source")
            or path.relative_to(root).as_posix()
        )
        scope_basis = str(row.get("scope_basis", ""))
        evidence.append(
            {
                "evidence_id": f"issue41:scope:{ordinal:03d}:{canonical}",
                "canonical": canonical,
                "source_type": _source_type(scope_basis),
                "source_ref": source_ref,
                "scope_note": str(row["semantic_scope"]),
                "content_identity": row_identity,
                "evidence_role": "SEMANTIC_SCOPE",
                "frozen": True,
                "pilot_ordinal": ordinal,
                "issue41_batch": batch,
                "scope_basis": scope_basis,
            }
        )
        wording = {
            "evidence_id": f"issue41:wording:{ordinal:03d}:{canonical}",
            "canonical": canonical,
            "source_type": "issue41_frozen_wording_candidate",
            "source_ref": path.relative_to(root).as_posix(),
            "scope_note": (
                "Frozen Japanese display/search candidate; never semantic authority."
            ),
            "content_identity": row_identity,
            "evidence_role": "WORDING_CANDIDATE",
            "frozen": True,
            "pilot_ordinal": ordinal,
            "issue41_batch": batch,
            "display_candidate": str(row.get("display_candidate", "")),
            "term_class": str(row.get("term_class", "")),
        }
        search_candidate = str(row.get("search_candidate", "")).strip()
        if search_candidate:
            wording["search_candidate"] = search_candidate
        proof = str(row.get("search_equivalence", "")).strip()
        if proof:
            wording["search_equivalence_proof"] = proof
        for field in (
            "candidate_relation",
            "scope_relation",
            "search_scope_relation",
            "search_candidate_state",
            "display_candidate_state",
        ):
            if row.get(field) not in (None, ""):
                wording[field] = row[field]
        evidence.append(wording)
        ledger.append(
            {
                "pilot_ordinal": ordinal,
                "canonical": canonical,
                "input_state": "APPROVED_INPUT",
                "issue41_batch": batch,
                "scope_basis": scope_basis,
                "source_file": path.relative_to(root).as_posix(),
            }
        )

    for path, row in review:
        canonical = str(row["canonical"])
        ordinal = int(row["pilot_ordinal"])
        batch = str(row.get("issue41_batch", ""))
        scope_note = " | ".join(
            value
            for value in (
                str(row.get("review_reason", "")).strip(),
                str(row.get("note", "")).strip(),
            )
            if value
        )
        evidence.append(
            {
                "evidence_id": f"issue41:review:{ordinal:03d}:{canonical}",
                "canonical": canonical,
                "source_type": "issue41_insufficient_scope_review",
                "source_ref": path.relative_to(root).as_posix(),
                "scope_note": scope_note
                or "Insufficient semantic scope; explicit REVIEW.",
                "content_identity": _row_identity(row),
                "evidence_role": "IDENTITY_ONLY",
                "frozen": True,
                "pilot_ordinal": ordinal,
                "issue41_batch": batch,
                "decision_state": "REVIEW",
            }
        )
        ledger.append(
            {
                "pilot_ordinal": ordinal,
                "canonical": canonical,
                "input_state": "EXPLICIT_REVIEW",
                "issue41_batch": batch,
                "scope_basis": str(row.get("scope_basis", "")),
                "source_file": path.relative_to(root).as_posix(),
            }
        )

    evidence.sort(
        key=lambda row: (int(row["pilot_ordinal"]), str(row["evidence_id"]))
    )
    ledger.sort(key=lambda row: int(row["pilot_ordinal"]))
    evidence_path = output_dir / "issue41_frozen_evidence_manifest.jsonl"
    ledger_path = output_dir / "issue41_frozen_decision_ledger.jsonl"
    _write_jsonl(evidence_path, evidence)
    _write_jsonl(ledger_path, ledger)
    summary = {
        "schema_version": "issue41-frozen-input-1",
        "fixed_pilot_rows": 100,
        "approved_input_rows": len(approved),
        "explicit_review_rows": len(review),
        "evidence_rows": len(evidence),
        "semantic_scope_rows": len(approved),
        "wording_candidate_rows": len(approved),
        "identity_review_rows": len(review),
        "membership_and_ordinals_complete": True,
        "evidence_manifest": evidence_path.name,
        "decision_ledger": ledger_path.name,
    }
    (output_dir / "issue41_frozen_input_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return summary


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    print(
        json.dumps(
            normalize(args.root, output_dir=args.output_dir),
            ensure_ascii=False,
            indent=2,
        )
    )
