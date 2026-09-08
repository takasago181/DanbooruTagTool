"""Run the R3 fresh-100 quarantine engine.

The default run creates conservative identity-only evidence.  Wording and
semantic-scope evidence must be supplied as a frozen JSONL manifest; the run
never fetches a live page and never writes outside ``translation_quarantine/r3``.
"""
from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

try:
    from .r3_common import (
        BLIND_QUOTAS,
        BRIDGE_AVAILABILITIES,
        ENGINE_VERSION,
        SCHEMA_VERSION,
        STATES,
        TERM_CLASSES,
        classify_risk,
        count_values,
        derive_row_state,
        disallowed_search_reason,
        ensure_r3_output,
        evidence_by_canonical,
        file_hash,
        issue32_fingerprint,
        issue32_propositions,
        issue32_state,
        bridge_conflict,
        json_hash,
        normalize_terms,
        protected_snapshot,
        read_csv,
        read_jsonl,
        semantic_class_for,
        search_equivalence_proven,
        stable_key,
        term_class,
        wording_candidates,
        write_json,
        write_jsonl,
    )
except ImportError:  # pragma: no cover - supports direct CLI execution
    from r3_common import (
    BLIND_QUOTAS,
    BRIDGE_AVAILABILITIES,
    ENGINE_VERSION,
    SCHEMA_VERSION,
    STATES,
    TERM_CLASSES,
    classify_risk,
    count_values,
    derive_row_state,
    disallowed_search_reason,
    ensure_r3_output,
    evidence_by_canonical,
    file_hash,
        issue32_fingerprint,
        issue32_propositions,
        issue32_state,
    bridge_conflict,
    json_hash,
    normalize_terms,
    protected_snapshot,
    read_csv,
    read_jsonl,
    semantic_class_for,
    search_equivalence_proven,
    stable_key,
    term_class,
    wording_candidates,
    write_json,
    write_jsonl,
    )
try:
    from .r3_select_pilot import load_overlap, select_pilot
except ImportError:  # pragma: no cover - supports direct CLI execution
    from r3_select_pilot import load_overlap, select_pilot


BASELINE_COMMIT = "a787ce39aa50f938f95612801e79f30bcdb63427"
REQUIRED_EVIDENCE_FIELDS = {
    "evidence_id", "canonical", "source_type", "source_ref", "scope_note",
    "content_identity", "evidence_role", "frozen",
}


def _relative(root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve())).replace("\\", "/")
    except ValueError:
        return str(path.resolve()).replace("\\", "/")


def _load_or_create_evidence(root: Path, selected: list[Mapping[str, Any]], path: Path | None) -> list[dict[str, Any]]:
    if path and path.exists():
        rows = read_jsonl(path)
        for row in rows:
            missing = REQUIRED_EVIDENCE_FIELDS - set(row)
            if missing or row.get("frozen") is not True:
                raise ValueError(f"frozen evidence is invalid for {row.get('evidence_id')}: {sorted(missing)}")
        return sorted(rows, key=lambda row: (str(row.get("canonical", "")), str(row.get("evidence_id", ""))))

    queue_path = root / "translation_quarantine" / "missing_candidates.csv"
    rows = []
    for item in selected:
        canonical = str(item["canonical"])
        rows.append({
            "evidence_id": f"identity:{canonical}",
            "canonical": canonical,
            "source_type": "pinned_candidate_queue",
            "source_ref": _relative(root, queue_path),
            "scope_note": "canonical identity only; this is not authoritative semantic scope",
            "content_identity": file_hash(queue_path) if queue_path.exists() else "",
            "evidence_role": "IDENTITY_ONLY",
            "frozen": True,
        })
    return rows


def _load_issue32_rows(path: Path | None) -> dict[str, dict[str, Any]]:
    if path is None or not path.exists():
        return {}
    if path.suffix.lower() == ".jsonl":
        rows = read_jsonl(path)
    elif path.suffix.lower() == ".json":
        value = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(value, list):
            rows = value
        else:
            metadata = value.get("metadata", {}) if isinstance(value.get("metadata", {}), dict) else {}
            rows = [{**metadata, **row} for row in value.get("rows", [])]
    else:
        rows = read_csv(path)
    result: dict[str, dict[str, Any]] = {}
    for raw in rows:
        raw = dict(raw)
        for field in ("frozen", "pinned", "immutable", "immutable_reference", "bridge_conflict", "independent_semantic_conflict", "semantic_conflict"):
            if isinstance(raw.get(field), str) and raw[field].strip().lower() in {"true", "false"}:
                raw[field] = raw[field].strip().lower() == "true"
        canonical = str(raw.get("canonical", raw.get("candidate_canonical", raw.get("canonical_tag", "")))).strip()
        if canonical:
            result[canonical] = dict(raw)
    return result


def _issue32_evidence_rows(evidence: list[Mapping[str, Any]]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for row in evidence:
        if row.get("evidence_role") == "BRIDGE32" and row.get("canonical"):
            result.setdefault(str(row["canonical"]), dict(row))
    return result


def _bridge_requirement_canonicals(evidence: list[Mapping[str, Any]]) -> set[str]:
    required: set[str] = set()
    for row in evidence:
        canonical = str(row.get("canonical", "")).strip()
        if not canonical:
            continue
        if row.get("evidence_role") == "BRIDGE32_REQUIREMENT" or any(
            row.get(field) is True for field in ("bridge32_required", "issue32_overlap_required", "required_overlap")
        ):
            required.add(canonical)
    return required


def _load_bridge_requirement_rows(path: Path | None) -> set[str]:
    if path is None or not path.exists():
        return set()
    if path.suffix.lower() == ".jsonl":
        rows = read_jsonl(path)
    elif path.suffix.lower() == ".json":
        value = json.loads(path.read_text(encoding="utf-8"))
        rows = value if isinstance(value, list) else value.get("rows", [])
    else:
        rows = read_csv(path)
    result: set[str] = set()
    for raw in rows:
        if isinstance(raw, str):
            if raw.strip():
                result.add(raw.strip())
            continue
        canonical = str(raw.get("canonical", raw.get("candidate_canonical", ""))).strip()
        if canonical:
            result.add(canonical)
    return result


def _bridge_metadata(snapshot: Mapping[str, Any], issue32_path: Path | None) -> dict[str, Any]:
    source_ref = str(snapshot.get("snapshot_ref") or snapshot.get("source_ref") or "").strip()
    if not source_ref and issue32_path is not None:
        source_ref = str(issue32_path).replace("\\", "/")
    content_identity = str(snapshot.get("content_identity") or snapshot.get("content_hash") or "").strip()
    frozen = snapshot.get("snapshot_frozen", snapshot.get("frozen")) is True
    pinned = snapshot.get("snapshot_pinned", snapshot.get("pinned")) is True
    immutable = snapshot.get("snapshot_immutable", snapshot.get("immutable")) is True or snapshot.get("immutable_reference") is True
    propositions = issue32_propositions(snapshot)
    if "semantic_support_relation" in propositions:
        # Carry the usage decision with the normalized propositions so a
        # replay can include this relation in the same fingerprint.
        propositions["semantic_support_used"] = True
    fingerprint = issue32_fingerprint(snapshot) if propositions else ""
    supplied_fingerprint = str(snapshot.get("meaning_fingerprint", "")).strip()
    if supplied_fingerprint and fingerprint and supplied_fingerprint != fingerprint:
        fingerprint = ""
    valid = bool(
        source_ref and content_identity and frozen and pinned and immutable and propositions
        and fingerprint and supplied_fingerprint and supplied_fingerprint == fingerprint
    )
    return {
        "snapshot_ref": source_ref,
        "content_identity": content_identity,
        "frozen": frozen,
        "pinned": pinned,
        "immutable": immutable,
        "propositions": propositions,
        "fingerprint": fingerprint,
        "valid": valid,
    }


def _evaluated_fingerprint(snapshot: Mapping[str, Any]) -> str:
    for field in (
        "evaluated_issue32_meaning_fingerprint", "issue32_evaluated_meaning_fingerprint",
        "evaluated_meaning_fingerprint", "previous_meaning_fingerprint", "prior_meaning_fingerprint",
    ):
        value = str(snapshot.get(field, "")).strip()
        if value:
            return value
    return ""


def _candidate_terms(records: list[Mapping[str, Any]], canonical: str) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    seen: set[str] = set()
    for record in records:
        if record.get("evidence_role") != "WORDING_CANDIDATE":
            continue
        terms: list[str] = []
        for field in ("search_candidate", "search_term", "term", "search_terms", "terms"):
            terms.extend(normalize_terms(record.get(field)))
        for term in terms:
            if term in seen:
                continue
            seen.add(term)
            explicit = str(record.get("term_class", ""))
            typed = term_class(term, canonical, explicit=explicit)
            rejection = disallowed_search_reason(term, canonical, record)
            if rejection:
                state = "REJECTED"
            elif typed == "BROAD_SEARCH_ALIAS":
                state = "REVIEW"
                rejection = "BROAD_ALIAS_CANNOT_BE_SEMANTIC_APPROVAL"
            elif explicit not in TERM_CLASSES:
                state = "REVIEW"
                rejection = "TERM_CLASS_NOT_EXPLICITLY_EVIDENCED"
            elif not search_equivalence_proven(record, typed):
                state = "REVIEW"
                rejection = "MISSING_MECHANICAL_SEARCH_EQUIVALENCE_PROOF"
            elif not any(r.get("evidence_role") == "SEMANTIC_SCOPE" for r in records):
                state = "REVIEW"
                rejection = "NO_AUTHORITATIVE_SEMANTIC_SCOPE"
            else:
                state = "ACCEPTED"
            output.append({
                "canonical": canonical,
                "term": term,
                "term_class": typed,
                "term_state": state,
                "evidence_ids": [str(record["evidence_id"])],
                "justification": str(record.get("justification", record.get("scope_note", ""))),
                "rejection_reason": rejection,
            })
    return output


def _make_pilot_rows(
    selected: list[Mapping[str, Any]],
    evidence: list[Mapping[str, Any]],
    issue32: Mapping[str, Mapping[str, Any]],
    issue32_path: Path | None,
    required_overlap: set[str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    by_canonical = evidence_by_canonical(evidence)
    pilot_rows: list[dict[str, Any]] = []
    search_rows: list[dict[str, Any]] = []
    bridge_rows: list[dict[str, Any]] = []
    for item in selected:
        canonical = str(item["canonical"])
        records = by_canonical.get(canonical, [])
        semantic = [record for record in records if record.get("evidence_role") == "SEMANTIC_SCOPE"]
        display = wording_candidates(records)
        risk = str(item.get("risk_class") or classify_risk(canonical))
        semantic_summary = " | ".join(str(record.get("scope_note", "")).strip() for record in semantic if record.get("scope_note"))
        display_evidence_ids = [str(record["evidence_id"]) for record in records if record.get("evidence_role") == "WORDING_CANDIDATE"]
        display_reasons: list[str] = []
        if not display:
            display_reasons.append("NO_SUPPORTED_DISPLAY_CANDIDATE")
        if risk in {"HIGH_POSE_ACTION", "HIGH_ANATOMY_ADULT", "CRITICAL"} and not semantic:
            display_reasons.append("HIGH_OR_CRITICAL_MISSING_EXACT_CANONICAL_SCOPE")
        if not semantic and display:
            display_reasons.append("NO_AUTHORITATIVE_SEMANTIC_SCOPE")
        display_state = "READY" if display and semantic and not display_reasons else "REVIEW"

        terms = _candidate_terms(records, canonical)
        search_rows.extend(terms)
        accepted = [term for term in terms if term["term_state"] == "ACCEPTED"]
        search_state = "READY" if accepted else "REVIEW"
        search_reasons = [] if accepted else ["NO_SAFE_SEARCH_CANDIDATE"]

        bridge_state = "READY"
        bridge_availability = "NOT_REQUIRED"
        bridge_ref = ""
        content_identity = ""
        fingerprint = ""
        evaluated_fingerprint = ""
        bridge_reasons: list[str] = []
        conflict = False
        metadata = {
            "snapshot_ref": "", "content_identity": "", "frozen": False,
            "pinned": False, "immutable": False, "propositions": {}, "fingerprint": "", "valid": False,
        }
        if canonical in required_overlap:
            snapshot = issue32.get(canonical)
            if snapshot is None:
                bridge_availability = "BRIDGE_MISSING"
                bridge_state = "REVIEW"
                bridge_reasons = ["BRIDGE32_MISSING_REQUIRED_SNAPSHOT"]
            else:
                metadata = _bridge_metadata(snapshot, issue32_path)
                bridge_ref = metadata["snapshot_ref"]
                content_identity = metadata["content_identity"]
                fingerprint = metadata["fingerprint"]
                evaluated_fingerprint = _evaluated_fingerprint(snapshot)
                conflict = bridge_conflict(snapshot)
                if not metadata["valid"]:
                    bridge_availability = "BLOCKED_BRIDGE"
                    bridge_state = "REVIEW"
                    bridge_reasons = ["BRIDGE32_SNAPSHOT_NOT_FROZEN_PINNED_IMMUTABLE"]
                else:
                    bridge_availability = "AVAILABLE"
                    if conflict:
                        bridge_state = "CONTRADICTION"
                        bridge_reasons = ["EXPLICIT_INDEPENDENT_SEMANTIC_CONFLICT"]
                    elif evaluated_fingerprint and evaluated_fingerprint != fingerprint:
                        bridge_state = "STALE_REVIEW"
                        bridge_reasons = ["TRANSLATION_VISIBLE_MEANING_FINGERPRINT_CHANGED"]
        bridge_rows.append({
            "canonical": canonical,
            "snapshot_ref": bridge_ref,
            "content_identity": content_identity,
            "frozen": metadata["frozen"],
            "pinned": metadata["pinned"],
            "immutable": metadata["immutable"],
            "meaning_fingerprint": fingerprint,
            "evaluated_issue32_meaning_fingerprint": evaluated_fingerprint,
            "meaning_relevant_propositions": metadata["propositions"],
            "bridge32_state": bridge_state,
            "bridge32_availability": bridge_availability,
            "conflict_signal": conflict,
            "reason_codes": bridge_reasons,
        })
        row_reasons = [*display_reasons, *search_reasons, *bridge_reasons]
        row_state = derive_row_state(display_state, search_state, bridge_state)
        pilot_rows.append({
            "pilot_ordinal": int(item["pilot_ordinal"]),
            "canonical": canonical,
            "lanes": str(item.get("lanes", "")),
            "priority": str(item.get("priority", "P0")),
            "post_count_or_reference": str(item.get("post_count_or_reference", "")),
            "semantic_class": semantic_class_for(canonical, str(item.get("lanes", ""))),
            "risk_class": risk,
            "semantic_scope_summary": semantic_summary,
            "semantic_evidence_ids": [str(record["evidence_id"]) for record in semantic],
            "display_candidate": display[0] if display else "",
            "display_state": display_state,
            "display_evidence_ids": display_evidence_ids,
            "search_state": search_state,
            "bridge32_state": bridge_state,
            "bridge32_availability": bridge_availability,
            "row_state": row_state,
            "issue32_overlap": "YES" if canonical in required_overlap else "NO",
            "issue32_snapshot_ref": bridge_ref,
            "issue32_content_identity": content_identity,
            "issue32_meaning_fingerprint": fingerprint,
            "evaluated_issue32_meaning_fingerprint": evaluated_fingerprint,
            "issue32_conflict_signal": conflict,
            "reason_codes": sorted(set(row_reasons)),
        })
    return pilot_rows, search_rows, bridge_rows


def run(
    root: Path,
    output_dir: Path,
    *,
    evidence_path: Path | None = None,
    issue32_path: Path | None = None,
    issue32_requirements_path: Path | None = None,
) -> dict[str, Any]:
    root = root.resolve()
    output = ensure_r3_output(root, output_dir)
    protected_before = protected_snapshot(root)
    frozen_input_evidence = read_jsonl(evidence_path) if evidence_path and evidence_path.exists() else []
    evidence_overlap = set(_issue32_evidence_rows(frozen_input_evidence))
    required_overlap = (
        set(_load_issue32_rows(issue32_path))
        | _load_bridge_requirement_rows(issue32_requirements_path)
        | evidence_overlap
        | _bridge_requirement_canonicals(frozen_input_evidence)
    )
    selection = select_pilot(
        root,
        # The normalized frozen bridge evidence is the replay input.  Keeping
        # the selection artifact independent of the live/source path makes a
        # replay from evidence_manifest.jsonl byte-for-byte equivalent.
        issue32_overlap=None,
        overlap_canonicals=required_overlap,
    )
    selected = selection["selected"]
    evidence = _load_or_create_evidence(root, selected, evidence_path)
    issue32 = _load_issue32_rows(issue32_path)
    for key, value in _issue32_evidence_rows(evidence).items():
        if key not in issue32:
            issue32[key] = value
        else:
            for field, field_value in value.items():
                issue32[key].setdefault(field, field_value)
    required_overlap |= _bridge_requirement_canonicals(evidence)
    required_overlap |= set(issue32)
    if issue32_path:
        selected_canonicals = {str(item["canonical"]) for item in selected}
        existing_ids = {str(row.get("evidence_id")) for row in evidence}
        for canonical, snapshot in issue32.items():
            if canonical not in selected_canonicals:
                continue
            evidence_id = f"bridge32:{canonical}"
            if evidence_id in existing_ids:
                continue
            evidence.append({
                "evidence_id": evidence_id,
                "canonical": canonical,
                "source_type": "frozen_issue32_snapshot",
                "source_ref": str(snapshot.get("snapshot_ref") or _relative(root, issue32_path)),
                "scope_note": "#32 meaning bridge snapshot; generation-only metadata is excluded",
                "content_identity": str(snapshot.get("content_identity") or snapshot.get("content_hash") or file_hash(issue32_path)),
                "evidence_role": "BRIDGE32",
                "frozen": True,
                "bridge32_required": True,
                "snapshot_frozen": snapshot.get("frozen") is True,
                "snapshot_pinned": snapshot.get("pinned") is True,
                "snapshot_immutable": snapshot.get("immutable") is True or snapshot.get("immutable_reference") is True,
                "pinned": snapshot.get("pinned") is True,
                "immutable": snapshot.get("immutable") is True or snapshot.get("immutable_reference") is True,
                "meaning_fingerprint": str(snapshot.get("meaning_fingerprint") or issue32_fingerprint(snapshot) if issue32_propositions(snapshot) else ""),
                "translation_visible_propositions": issue32_propositions(snapshot),
                "semantic_support_used": snapshot.get("semantic_support_used") is True,
                **{key: snapshot[key] for key in (
                    "identity", "entity_scope", "canonical", "count_cardinality", "count", "cardinality",
                    "actor", "ownership", "target", "body_site", "action_state", "action_vs_state",
                    "intrinsic_relation", "relation", "pose", "spatial_requirement", "required_modifier",
                    "required_qualifier", "qualifier", "canonical_meaning_width", "meaning_width",
                    "translation_visible_propositions", "evaluated_issue32_meaning_fingerprint",
                    "semantic_support_used", "semantic_context_used", "semantic_support_relation_used",
                    "semantic_support_relation", "support_relation", "support_class",
                    "bridge_conflict", "independent_semantic_conflict", "semantic_conflict",
                ) if key in snapshot},
            })
        evidence.sort(key=lambda row: (str(row.get("canonical", "")), str(row.get("evidence_id", ""))))
    if issue32_requirements_path and issue32_requirements_path.exists():
        selected_canonicals = {str(item["canonical"]) for item in selected}
        existing_ids = {str(row.get("evidence_id")) for row in evidence}
        for canonical in sorted(_load_bridge_requirement_rows(issue32_requirements_path) & selected_canonicals):
            evidence_id = f"bridge32-requirement:{canonical}"
            if evidence_id in existing_ids:
                continue
            evidence.append({
                "evidence_id": evidence_id,
                "canonical": canonical,
                "source_type": "frozen_bridge_requirement",
                "source_ref": _relative(root, issue32_requirements_path),
                "scope_note": "#32 overlap is required; snapshot availability is evaluated separately",
                "content_identity": file_hash(issue32_requirements_path),
                "evidence_role": "BRIDGE32_REQUIREMENT",
                "frozen": True,
                "bridge32_required": True,
            })
        evidence.sort(key=lambda row: (str(row.get("canonical", "")), str(row.get("evidence_id", ""))))
    # The frozen evidence manifest is itself a replay input.  Normalize its
    # order even when no issue32 source path was supplied, so the original run
    # and an evidence-only replay serialize the same artifact.
    evidence.sort(key=lambda row: (str(row.get("canonical", "")), str(row.get("evidence_id", ""))))
    pilot_rows, search_rows, bridge_rows = _make_pilot_rows(selected, evidence, issue32, issue32_path, required_overlap)

    write_json(output / "pilot_selection.json", selection)
    write_jsonl(output / "evidence_manifest.jsonl", evidence)
    write_jsonl(output / "pilot_rows.jsonl", pilot_rows)
    write_jsonl(output / "search_terms.jsonl", search_rows)
    write_jsonl(output / "bridge32.jsonl", bridge_rows)
    # The blind artifacts are generated by r3_build_blind_audit.py.  Keep the
    # expected filenames present even when the caller only runs this command.
    write_jsonl(output / "blind30_input.jsonl", [])
    write_json(output / "blind30_key.json", {"schema_version": SCHEMA_VERSION, "selected": [], "omitted_overlap": []})
    write_jsonl(output / "blind30_review.jsonl", [])

    artifact_paths = [
        "pilot_selection.json", "evidence_manifest.jsonl", "pilot_rows.jsonl",
        "search_terms.jsonl", "bridge32.jsonl", "blind30_input.jsonl",
        "blind30_key.json", "blind30_review.jsonl",
    ]
    summary = {
        "schema_version": SCHEMA_VERSION,
        # This reports the requested stratum assignment, including explicit
        # one-way fallback rows.  The actual row risk remains in pilot_rows.
        "selected_stratum_counts": selection["achieved_stratum_counts"],
        "artifact_state_counts": {
            "display": count_values(pilot_rows, "display_state"),
            "search": count_values(pilot_rows, "search_state"),
            "bridge32": count_values(pilot_rows, "bridge32_state"),
            "row": count_values(pilot_rows, "row_state"),
        },
        "row_state_counts": count_values(pilot_rows, "row_state"),
        "search_term_counts": {
            "state": count_values(search_rows, "term_state"),
            "class": count_values(search_rows, "term_class"),
        },
        "issue32_overlap_counts": selection["issue32_overlap_counts"],
        "bridge32_audit": {
            "required_overlap_count": sum(row["bridge32_availability"] != "NOT_REQUIRED" for row in bridge_rows),
            "available_count": sum(row["bridge32_availability"] == "AVAILABLE" for row in bridge_rows),
            "not_required_count": sum(row["bridge32_availability"] == "NOT_REQUIRED" for row in bridge_rows),
            "bridge_missing_count": sum(row["bridge32_availability"] == "BRIDGE_MISSING" for row in bridge_rows),
            "blocked_bridge_count": sum(row["bridge32_availability"] == "BLOCKED_BRIDGE" for row in bridge_rows),
            "stale_count": sum(row["bridge32_state"] == "STALE_REVIEW" for row in bridge_rows),
            "contradiction_count": sum(row["bridge32_state"] == "CONTRADICTION" for row in bridge_rows),
            "records": [
                {
                    "canonical": row["canonical"],
                    "bridge32_availability": row["bridge32_availability"],
                    "bridge32_state": row["bridge32_state"],
                    "current_fingerprint": row["meaning_fingerprint"],
                    "evaluated_fingerprint": row["evaluated_issue32_meaning_fingerprint"],
                    "snapshot_ref": row["snapshot_ref"],
                    "content_identity": row["content_identity"],
                }
                for row in bridge_rows
            ],
        },
        "deterministic_rerun_verification": "NOT_RUN",
        "blind30_gate_metrics": {"state": "NOT_BUILT", "selected": 0},
        "regression_fixture_count": selection["eligible_pool"]["excluded_count"],
        "remaining_925_p0_processed": False,
        "production_modified": False,
    }
    write_json(output / "run_summary.json", summary)
    generated_hashes = {name: file_hash(output / name) for name in [*artifact_paths, "run_summary.json"]}
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "engine_version": ENGINE_VERSION,
        "baseline_commit": BASELINE_COMMIT,
        "input_file_hashes": {
            "missing_candidates.csv": file_hash(root / "translation_quarantine" / "missing_candidates.csv"),
            "phase1a_review.csv": file_hash(root / "translation_quarantine" / "phase1a_review.csv"),
            **({"frozen_evidence_manifest": file_hash(evidence_path)} if evidence_path and evidence_path.exists() else {}),
            **({"frozen_issue32_input": file_hash(issue32_path)} if issue32_path and issue32_path.exists() else {}),
            **({"frozen_issue32_requirements": file_hash(issue32_requirements_path)} if issue32_requirements_path and issue32_requirements_path.exists() else {}),
        },
        "selection_seed": selection["selection_seed"],
        "pilot_algorithm_version": selection["pilot_algorithm_version"],
        "blind_algorithm_version": "r3-blind30-1",
        "evidence_manifest_hash": file_hash(output / "evidence_manifest.jsonl"),
        "generated_file_hashes": generated_hashes,
        "run_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "deterministic_replay_inputs": {
            "evidence_input_ref": _relative(root, evidence_path) if evidence_path and evidence_path.exists() else "generated:evidence_manifest.jsonl",
            "issue32_snapshot_ref": _relative(root, issue32_path) if issue32_path and issue32_path.exists() else "",
            "issue32_requirements_ref": _relative(root, issue32_requirements_path) if issue32_requirements_path and issue32_requirements_path.exists() else "",
            "input_hashes": {
                "evidence_input": file_hash(evidence_path) if evidence_path and evidence_path.exists() else file_hash(output / "evidence_manifest.jsonl"),
                "issue32_snapshot": file_hash(issue32_path) if issue32_path and issue32_path.exists() else "",
                "issue32_requirements": file_hash(issue32_requirements_path) if issue32_requirements_path and issue32_requirements_path.exists() else "",
            },
        },
        "production_modified": False,
        "protected_snapshot_before": protected_before,
    }
    write_json(output / "run_manifest.json", manifest)
    return {"output": output, "pilot_rows": pilot_rows, "search_rows": search_rows, "selection": selection}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--evidence", type=Path)
    parser.add_argument("--issue32", type=Path)
    parser.add_argument("--issue32-requirements", type=Path)
    args = parser.parse_args()
    run(
        args.root,
        args.output,
        evidence_path=args.evidence,
        issue32_path=args.issue32,
        issue32_requirements_path=args.issue32_requirements,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
