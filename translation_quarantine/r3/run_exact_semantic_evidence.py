"""Run the reusable exact-canonical mechanism against the first real dataset.

Default mode is frozen replay.  ``--acquire`` is the only mode that may call a
source adapter and it writes a new frozen snapshot before extraction.  Output
is constrained to the quarantine R3 subtree.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from collections import Counter
from pathlib import Path
from typing import Any

try:
    from .exact_semantic_evidence import (
        DanbooruWikiAdapter,
        FrozenEvidenceStore,
        process_frozen_rows,
        write_run_artifacts,
    )
    from .r3_common import classify_risk, file_hash, protected_snapshot, read_json, read_jsonl, write_json
    from .r3_bulk_batches import _validate_issue32
except ImportError:  # pragma: no cover
    from exact_semantic_evidence import DanbooruWikiAdapter, FrozenEvidenceStore, process_frozen_rows, write_run_artifacts
    from r3_common import classify_risk, file_hash, protected_snapshot, read_json, read_jsonl, write_json
    from r3_bulk_batches import _validate_issue32


SOURCE_DIR = "translation_quarantine/r3_bulk_review_reduction"
FROZEN_SOURCE = "translation_quarantine/r3_restricted_routes_20260909/wiki_evidence.jsonl"
OUTPUT_DIR = "translation_quarantine/r3_exact_semantic_evidence_20260909"


def _hash_artifacts(path: Path) -> dict[str, str]:
    names = ("propositions.jsonl", "validations.jsonl", "risk_gates.jsonl", "wording_search_handoff.jsonl")
    return {name: file_hash(path / name) for name in names if (path / name).exists()}


def _acquire(canonicals: list[str], path: Path) -> list[dict[str, Any]]:
    adapter = DanbooruWikiAdapter()
    rows = [dict(adapter.acquire(canonical)) for canonical in canonicals]
    rows.sort(key=lambda row: str(row.get("canonical", "")))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n" for row in rows), encoding="utf-8", newline="\n")
    return rows


def _summary(root: Path, output: Path, evidence: list[Any], rows: dict[str, list[dict[str, Any]]],
             replay: str, bridge: dict[str, Any], before: dict[str, str], after: dict[str, str]) -> dict[str, Any]:
    gates = rows["risk_gates"]
    validations = rows["validations"]
    source_exact = [item for item in evidence if item.http_status == 200 and item.exact_title_match and item.frozen]
    field_coverage = Counter()
    authority_field_coverage = Counter()
    authority_canonicals = {item.canonical for item in source_exact}
    for item in rows["propositions"]:
        for field, value in item["propositions"]["fields"].items():
            if value not in (None, "", [], {}):
                field_coverage[field] += 1
                if item["canonical"] in authority_canonicals:
                    authority_field_coverage[field] += 1
    statuses = Counter(str(item["status"]) for item in validations)
    risk_result: dict[str, dict[str, int]] = {}
    for item in gates:
        risk = str(item["risk_class"])
        risk_result.setdefault(risk, Counter())
        risk_result[risk][str(item["decision"])] += 1
    false_ready = [
        item["canonical"] for item in gates
        if item["decision"] == "READY" and (item["validation_status"] != "VALIDATED" or not item["exact_authority_satisfied"] or item["missing_fields"])
    ]
    contradictions = [item["canonical"] for item in validations if item["status"] == "CONTRADICTION"]
    reason_counts = Counter(reason for item in gates if item["decision"] != "READY" for reason in item["reason_codes"])
    unavailable = [item.canonical for item in evidence if not (item.http_status == 200 and item.exact_title_match and item.frozen)]
    human_review = sum(1 for item in gates if item["decision"] != "READY")
    summary = {
        "schema_version": "exact-semantic-evidence-run-summary-v1",
        "mechanism_schema": "exact-canonical-semantic-evidence-v1",
        "extractor_version": "deterministic-proposition-extractor-v1",
        "source": {
            "frozen_input": FROZEN_SOURCE,
            "records": len(evidence),
            "exact_authority_usable": len(source_exact),
            "unavailable_or_title_mismatch": len(unavailable),
            "source_adapter_counts": dict(Counter(item.adapter_id for item in evidence)),
            "http_status_counts": dict(sorted(Counter(str(item.http_status) for item in evidence).items())),
            "live_fetch_used_in_replay": False,
        },
        "evidence_source_counts": dict(Counter(item.adapter_id for item in evidence)),
        "route_counts": {
            "semantic_scope_acquisition": {"processed": len(evidence), "exact_authority": len(source_exact), "parked": len(evidence) - len(source_exact)},
            "wording_only": {"ready_for_review": sum(item["semantic_status"] == "READY" for item in rows["handoff"]), "parked": sum(item["semantic_status"] != "READY" for item in rows["handoff"])},
            "minimal_search_term": {"processed": len(evidence), "accepted": 0, "parked": len(evidence)},
        },
        "proposition_extraction": {
            "rows": len(rows["propositions"]),
            "authority_rows": len(source_exact),
            "field_coverage": dict(sorted(field_coverage.items())),
            "field_coverage_exact_authority_only": dict(sorted(authority_field_coverage.items())),
            "fully_validated_proposition_sets": sum(item["status"] == "VALIDATED" for item in validations),
            "status_counts": dict(sorted(statuses.items())),
            "incomplete": statuses.get("INCOMPLETE", 0),
            "ambiguous": statuses.get("AMBIGUOUS", 0),
            "contradiction": statuses.get("CONTRADICTION", 0),
        },
        "risk_gate": {
            "result_by_risk": {risk: dict(sorted(counts.items())) for risk, counts in sorted(risk_result.items())},
            "semantic_ready": sum(item["decision"] == "READY" for item in gates),
            "semantic_review": sum(item["decision"] == "REVIEW" for item in gates),
            "contradiction": len(contradictions),
            "semantic_ready_canonicals": sorted(item["canonical"] for item in gates if item["decision"] == "READY"),
            "new_ready_canonicals": [],
            "false_ready": len(false_ready),
            "false_ready_canonicals": false_ready,
        },
        "overall_decision": {
            "READY": 0,
            "REVIEW": sum(item["decision"] == "READY" or item["decision"] == "REVIEW" for item in gates) - len(contradictions),
            "CONTRADICTION": len(contradictions),
            "reason": "Semantic READY is a handoff only; wording and minimal-search equivalence are not established here.",
        },
        "handoff": {
            "wording_ready_for_review": sum(item["semantic_status"] == "READY" for item in rows["handoff"]),
            "search_eligible": 0,
            "all_non_ready_parked": all(item["semantic_status"] == "READY" or item["wording_route"] == "PARKED" for item in rows["handoff"]),
        },
        "residual_review_reason_distribution": dict(sorted(reason_counts.items())),
        "parked": {
            "count": sum(item["decision"] != "READY" for item in gates),
            "reason_counts": dict(sorted(reason_counts.items())),
            "authority_unavailable_canonicals": unavailable,
        },
        "human_review_estimate": {
            "semantic_or_gate_review_rows": human_review,
            "wording_and_search_followup_rows": sum(item["semantic_status"] == "READY" for item in rows["handoff"]),
            "note": "This is an upper-bound row count for human confirmation; no REVIEW row is promoted by estimation.",
        },
        "focused_reaudit": {
            "target": "uncensored",
            "result": "REVIEW",
            "source": "translation_quarantine/r3_restricted_routes_20260909/focused_reaudit.json",
            "reason": "wording candidate remains explanatory/unnatural; previous READY is not a teacher",
        },
        "bridge32": {
            "state": bridge["guard"]["state"], "resolved_count": bridge["guard"]["resolved_count"],
            "required_count": bridge["guard"]["required_count"], "read_only": True,
        },
        "false_ready": 0 if not false_ready else len(false_ready),
        "contradiction": len(contradictions),
        "replay": replay,
        "verifier": "PASS" if not false_ready and not (before != after) and bridge["guard"]["state"] == "READY" else "FAIL",
        "production_modified": False,
        "protected_boundary_changed": before != after,
        "promotion": "NOT_AUTHORIZED",
    }
    write_json(output / "run_summary.json", summary)
    return summary


def _write_report(output: Path, summary: dict[str, Any]) -> None:
    extraction = summary["proposition_extraction"]
    gate = summary["risk_gate"]
    overall = summary["overall_decision"]
    lines = [
        "# Issue #36 exact-canonical semantic evidence refresh",
        "",
        "This is a quarantine-only, deterministic semantic evidence run. Semantic READY is a downstream wording handoff, not final translation READY.",
        "",
        f"- Overall: READY {overall['READY']} / REVIEW {overall['REVIEW']} / CONTRADICTION {overall['CONTRADICTION']}",
        f"- Semantic gate: READY {gate['semantic_ready']} / REVIEW {gate['semantic_review']}",
        f"- Frozen source records: {summary['source']['records']} (usable exact authority {summary['source']['exact_authority_usable']}, unavailable/mismatch {summary['source']['unavailable_or_title_mismatch']})",
        f"- Proposition status: VALIDATED {extraction['fully_validated_proposition_sets']}, INCOMPLETE {extraction['incomplete']}, AMBIGUOUS {extraction['ambiguous']}, CONTRADICTION {extraction['contradiction']}",
        f"- false READY: {summary['false_ready']}; replay: {summary['replay']}; verifier: {summary['verifier']}; production_modified: {summary['production_modified']}",
        "",
        "## Semantic READY handoff canonicals",
        "",
        ", ".join(gate["semantic_ready_canonicals"]) if gate["semantic_ready_canonicals"] else "(none)",
        "",
        "## Overall new READY canonicals",
        "",
        "(none; wording/search gates are not promoted by this mechanism)",
        "",
        "## Field coverage",
        "",
        json.dumps(extraction["field_coverage"], ensure_ascii=False, sort_keys=True),
        "",
        "## Residual REVIEW reasons",
        "",
        json.dumps(summary["residual_review_reason_distribution"], ensure_ascii=False, sort_keys=True),
        "",
        "## Focused re-audit",
        "",
        "uncensored: REVIEW; explanatory/unnatural wording remains parked and the prior READY row was not used as a teacher.",
        "",
        "## Boundary",
        "",
        "#32 v2 was read-only; production, #35, CURRENT_DEV_TASK, main, and Stage10 production A/B were not modified.",
    ]
    (output / "EXACT_SEMANTIC_EVIDENCE_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def run(root: Path, *, acquire: bool = False) -> dict[str, Any]:
    root = root.resolve()
    output = (root / OUTPUT_DIR).resolve()
    allowed = (root / "translation_quarantine").resolve()
    try:
        output.relative_to(allowed)
    except ValueError as exc:
        raise ValueError("output must remain in quarantine") from exc
    output.mkdir(parents=True, exist_ok=True)
    selected = [row for row in read_jsonl(root / SOURCE_DIR / "rows.jsonl") if row.get("row_state") == "REVIEW"]
    selected.sort(key=lambda row: (int(row.get("pilot_ordinal", 0)), str(row.get("canonical", ""))))
    if len(selected) != 556:
        raise RuntimeError(f"expected 556 REVIEW rows, got {len(selected)}")
    frozen_path = root / FROZEN_SOURCE
    if acquire:
        _acquire([str(row["canonical"]) for row in selected], frozen_path)
    evidence = FrozenEvidenceStore(frozen_path).load()
    if len(evidence) != 556 or len({item.canonical for item in evidence}) != 556:
        raise RuntimeError("frozen exact evidence must contain 556 unique rows")
    risk_by = {str(row["canonical"]): str(row.get("risk_class") or classify_risk(str(row["canonical"]))) for row in selected}
    before = protected_snapshot(root)
    _, bridge = _validate_issue32(root)
    rows = process_frozen_rows(evidence, risk_by)
    write_run_artifacts(output, rows)
    after = protected_snapshot(root)
    # Two replay passes use the in-memory frozen evidence only.  The adapter is
    # deliberately not in this code path.
    replay_root = output / ".replay_work"
    if replay_root.exists():
        shutil.rmtree(replay_root)
    try:
        hashes: list[dict[str, str]] = []
        for ordinal in (1, 2):
            replay_dir = replay_root / f"replay{ordinal}"
            replay_rows = process_frozen_rows(evidence, risk_by)
            write_run_artifacts(replay_dir, replay_rows)
            hashes.append(_hash_artifacts(replay_dir))
        original = _hash_artifacts(output)
        replay = "PASS" if original == hashes[0] == hashes[1] else "FAIL"
        write_json(output / "replay_verification.json", {
            "schema_version": "exact-semantic-evidence-replay-v1", "replay": replay,
            "source_mode": "frozen_only", "live_fetch": False,
            "original_vs_replay1": "PASS" if original == hashes[0] else "FAIL",
            "replay1_vs_replay2": "PASS" if hashes[0] == hashes[1] else "FAIL",
        })
    finally:
        if replay_root.exists():
            shutil.rmtree(replay_root)
    summary = _summary(root, output, evidence, rows, replay, bridge, before, after)
    _write_report(output, summary)
    write_json(output / "campaign_manifest.json", {
        "schema_version": "exact-semantic-evidence-manifest-v1",
        "frozen_input": FROZEN_SOURCE, "frozen_input_hash": file_hash(frozen_path),
        "selected_membership_hash": hashlib.sha256("\n".join(sorted(risk_by)).encode("utf-8")).hexdigest(),
        "bridge32_state": bridge["guard"]["state"], "protected_before": before, "protected_after": after,
        "production_modified": False, "new_ready_used_as_teacher": False,
    })
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--acquire", action="store_true", help="live-fetch through the adapter and freeze a new snapshot")
    args = parser.parse_args()
    print(json.dumps(run(args.root, acquire=args.acquire), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
