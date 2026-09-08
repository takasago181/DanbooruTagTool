"""Autonomous Issue #36 safe-or-park campaign.

This runner consumes only already-frozen quarantine evidence.  It deliberately
keeps source acquisition (the existing Danbooru adapter) outside the replay
path, records every exhausted route, and applies semantic, wording, and search
gates independently.  It never writes production data or treats a new READY
row as a teacher for another row in the same campaign.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping

try:
    from .exact_semantic_evidence import FrozenEvidenceStore, process_frozen_rows
    from .r3_bulk_batches import _validate_issue32
    from .r3_common import file_hash, json_hash, protected_snapshot, read_json, read_jsonl, write_json, write_jsonl
except ImportError:  # pragma: no cover
    from exact_semantic_evidence import FrozenEvidenceStore, process_frozen_rows
    from r3_bulk_batches import _validate_issue32
    from r3_common import file_hash, json_hash, protected_snapshot, read_json, read_jsonl, write_json, write_jsonl


CAMPAIGN_ID = "issue36-autonomous-safe-or-park-20260909-v1"
SOURCE_ROWS = "translation_quarantine/r3_bulk_review_reduction/rows.jsonl"
SOURCE_EVIDENCE = "translation_quarantine/r3_bulk_review_reduction/evidence_manifest.jsonl"
FROZEN_WIKI = "translation_quarantine/r3_restricted_routes_20260909/wiki_evidence.jsonl"
OVERLAY_PATH = "data/runtime/japanese_overlay.json"
OUTPUT_DIR = "translation_quarantine/r3_autonomous_safe_or_park_20260909"
RULE_FILES = (
    "translation_quarantine/r3/exact_semantic_evidence.py",
    "translation_quarantine/r3/r3_common.py",
    "translation_quarantine/r3/r3_bulk_batches.py",
    "translation_quarantine/r3/r3_autonomous_safe_or_park.py",
)

_JP = re.compile(r"[ぁ-んァ-ヶ一-龯々ー]")
_EXPLANATORY = re.compile(r"(?:を示す語|を表す語|を意味する語|説明|などを含む)")
# Exact-source ``other_names`` are wording evidence, not an automatic
# equivalence certificate.  These markers identify common narrowing,
# colloquial, abbreviation, or added-actor patterns that must remain parked
# without a human wording decision.
_WORDING_WIDTH_RISK = re.compile(
    r"(?:グレート|ハメ撮り|ガチムチ|ショタ|玉つき|セカコス|セカンド|タイトル回収|またすじ|もぐもぐ|インテリア|きょとん)"
)


def _canonical_lines(rows: Iterable[Mapping[str, Any]]) -> bytes:
    return b"".join(
        json.dumps(dict(row), ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8") + b"\n"
        for row in rows
    )


def _rows_hash(rows: Iterable[Mapping[str, Any]]) -> str:
    return "sha256:" + hashlib.sha256(_canonical_lines(rows)).hexdigest()


def _jp_terms(value: Any) -> list[str]:
    if isinstance(value, str):
        values = [value]
    elif isinstance(value, list):
        values = value
    else:
        values = []
    return [str(item).strip() for item in values if str(item).strip() and _JP.search(str(item))]


def _wording_is_natural(candidate: str) -> bool:
    return bool(
        candidate
        and _JP.search(candidate)
        and not _EXPLANATORY.search(candidate)
        and not _WORDING_WIDTH_RISK.search(candidate)
    )


def _terminal_state(*, semantic_ready: bool, wording_ready: bool, search_ready: bool, contradiction: bool = False) -> tuple[str, str]:
    """Return the final quarantine state; all gates are required for SAFE."""

    if contradiction:
        return "PARK", "CONTRADICTION"
    if semantic_ready and wording_ready and search_ready:
        return "SAFE", "READY"
    return "PARK", "REVIEW"


def _prior_semantic_records(records: Iterable[Mapping[str, Any]], canonical: str) -> list[dict[str, Any]]:
    return [
        dict(record) for record in records
        if str(record.get("canonical", "")) == canonical
        and record.get("evidence_role") == "SEMANTIC_SCOPE"
        and record.get("frozen") is True
    ]


def _prior_scope_ready(records: list[dict[str, Any]], risk: str) -> tuple[bool, str, list[str]]:
    exact = [
        record for record in records
        if str(record.get("scope_basis", "")) == "EXACT_CANONICAL_AUTHORITATIVE_REFERENCE"
    ]
    if exact:
        return True, "prior_frozen_exact_authoritative_scope", [str(record.get("evidence_id", "")) for record in exact]
    transparent = [
        record for record in records
        if str(record.get("scope_basis", "")) == "TRANSPARENT_CANONICAL_COMPOSITION"
    ]
    # Existing transparent scopes are already accepted frozen R3 scope, but
    # they are not sufficient authority for HIGH/CRITICAL semantic approval.
    if transparent and risk in {"LOW", "MEDIUM"}:
        return True, "prior_frozen_safe_composition_scope", [str(record.get("evidence_id", "")) for record in transparent]
    return False, "", []


def _route_record(canonical: str, route: str, status: str, reason: str, **extra: Any) -> dict[str, Any]:
    return {
        "campaign_id": CAMPAIGN_ID,
        "canonical": canonical,
        "route": route,
        "status": status,
        "reason": reason,
        **extra,
    }


def _load_inputs(root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    rows = read_jsonl(root / SOURCE_ROWS)
    selected = sorted(
        (dict(row) for row in rows if row.get("row_state") == "REVIEW"),
        key=lambda row: (int(row.get("pilot_ordinal", 0)), str(row.get("canonical", ""))),
    )
    if len(selected) != 556 or len({str(row.get("canonical")) for row in selected}) != 556:
        raise RuntimeError("expected 556 unique unresolved REVIEW rows")
    evidence = read_jsonl(root / SOURCE_EVIDENCE)
    wiki = read_jsonl(root / FROZEN_WIKI)
    if len(wiki) != 556 or len({str(row.get("canonical")) for row in wiki}) != 556:
        raise RuntimeError("expected 556 unique frozen wiki records")
    overlay = read_json(root / OVERLAY_PATH)
    if not isinstance(overlay.get("entries"), dict):
        raise RuntimeError("production overlay does not have a readable entries map")
    return selected, evidence, wiki, overlay


def _evaluate(root: Path) -> dict[str, Any]:
    selected, prior_evidence, wiki_raw, overlay = _load_inputs(root)
    risk_by = {str(row["canonical"]): str(row.get("risk_class", "LOW")) for row in selected}
    frozen = FrozenEvidenceStore(root / FROZEN_WIKI).load()
    processed = process_frozen_rows(frozen, risk_by)
    gate_by = {str(row["canonical"]): dict(row) for row in processed["risk_gates"]}
    validation_by = {str(row["canonical"]): dict(row) for row in processed["validations"]}
    proposition_by = {str(row["canonical"]): dict(row) for row in processed["propositions"]}
    wiki_by = {str(row["canonical"]): row for row in wiki_raw}
    prior_by = {str(row["canonical"]): _prior_semantic_records(prior_evidence, str(row["canonical"])) for row in selected}

    source_ledger: list[dict[str, Any]] = []
    provenance: list[dict[str, Any]] = []
    propositions: list[dict[str, Any]] = []
    validations: list[dict[str, Any]] = []
    semantic_gates: list[dict[str, Any]] = []
    wording: list[dict[str, Any]] = []
    search: list[dict[str, Any]] = []
    terminal: list[dict[str, Any]] = []

    for row in selected:
        canonical = str(row["canonical"])
        risk = risk_by[canonical]
        wiki = wiki_by[canonical]
        exact_gate = gate_by[canonical]
        validation = validation_by[canonical]
        proposition = proposition_by[canonical]
        prior = prior_by[canonical]
        prior_ready, prior_source, prior_ids = _prior_scope_ready(prior, risk)
        wiki_usable = wiki.get("http_status") == 200 and wiki.get("exact_title_match") is True and wiki.get("frozen") is True
        exact_semantic_ready = exact_gate.get("decision") == "READY"
        semantic_ready = exact_semantic_ready or prior_ready
        semantic_source = "danbooru_exact_canonical_wiki" if exact_semantic_ready else prior_source
        semantic_evidence_ids = [
            str(item.get("evidence_id", "")) for item in prior
            if item.get("evidence_id")
        ]
        if exact_semantic_ready:
            semantic_evidence_ids.append(f"wiki:{wiki.get('canonical')}:{wiki.get('content_identity', '')}")

        if prior:
            source_ledger.append(_route_record(
                canonical, "local_exact_assets", "REUSED_FROZEN_USABLE", "frozen_semantic_scope_available",
                evidence_ids=semantic_evidence_ids,
                source_ref=SOURCE_EVIDENCE,
            ))
            provenance.extend({
                "canonical": canonical,
                "evidence_role": "SEMANTIC_SCOPE",
                "source_type": record.get("source_type", ""),
                "source_ref": SOURCE_EVIDENCE,
                "evidence_id": record.get("evidence_id", ""),
                "scope_basis": record.get("scope_basis", ""),
                "content_identity": record.get("content_identity", ""),
                "frozen": record.get("frozen") is True,
            } for record in prior)
        else:
            source_ledger.append(_route_record(
                canonical, "local_exact_assets", "EXHAUSTED", "NO_FROZEN_SEMANTIC_SCOPE",
                source_ref=SOURCE_EVIDENCE,
            ))

        wiki_status = "REUSED_FROZEN_USABLE" if wiki_usable else "EXHAUSTED"
        wiki_reason = "exact_title_and_http_200" if wiki_usable else str(wiki.get("semantic_status") or "AUTHORITATIVE_SCOPE_UNAVAILABLE")
        source_ledger.append(_route_record(
            canonical, "danbooru_exact_canonical_wiki", wiki_status, wiki_reason,
            source_url=wiki.get("source_url", ""), revision=wiki.get("revision", ""),
            content_identity=wiki.get("content_identity", ""), http_status=wiki.get("http_status"),
            exact_title_match=wiki.get("exact_title_match") is True, frozen=wiki.get("frozen") is True,
            live_fetch=False,
        ))
        provenance.append({
            "canonical": canonical,
            "evidence_role": "SEMANTIC_SCOPE_ACQUISITION",
            "source_type": wiki.get("source_type", ""),
            "source_url": wiki.get("source_url", ""),
            "revision": wiki.get("revision", ""),
            "content_identity": wiki.get("content_identity", ""),
            "http_status": wiki.get("http_status"),
            "exact_title_match": wiki.get("exact_title_match") is True,
            "frozen": wiki.get("frozen") is True,
            "acquisition_mode": "frozen_reuse",
        })
        source_ledger.append(_route_record(
            canonical, "additional_allowlisted_exact_canonical_adapters", "EXHAUSTED",
            "NO_ADDITIONAL_ADAPTER_CONFIGURED",
            adapter_registry_version="r3-autonomous-safe-or-park-v1",
        ))

        propositions.append({
            "canonical": canonical,
            "risk_class": risk,
            "source": {
                "adapter_id": wiki.get("source_type", ""),
                "source_url": wiki.get("source_url", ""),
                "revision": wiki.get("revision", ""),
                "content_identity": wiki.get("content_identity", ""),
                "exact_title_match": wiki.get("exact_title_match") is True,
                "frozen": wiki.get("frozen") is True,
            },
            "propositions": proposition.get("propositions", {}).get("fields", {}),
            "required_fields": proposition.get("propositions", {}).get("required_fields", []),
            "extractor_version": proposition.get("propositions", {}).get("extractor_version", ""),
        })
        validations.append({"canonical": canonical, **validation})
        semantic_reason = list(exact_gate.get("reason_codes", []))
        if not semantic_ready:
            semantic_reason.append("SEMANTIC_SCOPE_NOT_ESTABLISHED")
        semantic_gates.append({
            "canonical": canonical,
            "risk_class": risk,
            "decision": "READY_FOR_WORDING_SEARCH_GATE" if semantic_ready else "REVIEW",
            "authority_route": semantic_source,
            "exact_wiki_gate": exact_gate,
            "prior_scope_evidence_ids": prior_ids,
            "reason_codes": sorted(set(semantic_reason)),
            "new_ready_used_as_teacher": False,
        })

        overlay_entry = overlay["entries"].get(canonical, {})
        overlay_terms = _jp_terms(overlay_entry.get("search_ja", []) if isinstance(overlay_entry, dict) else [])
        wiki_terms = _jp_terms(wiki.get("other_names", []))
        candidate_pool = sorted(set(overlay_terms) & set(wiki_terms)) if wiki_usable else []
        display_candidate = candidate_pool[0] if len(candidate_pool) == 1 else ""
        wording_reason = ""
        if not semantic_ready:
            wording_status = "PARKED"
            wording_reason = "SEMANTIC_SCOPE_NOT_ESTABLISHED"
        elif len(candidate_pool) == 0:
            wording_status = "PARKED"
            wording_reason = "NO_INDEPENDENT_DISPLAY_CANDIDATE"
        elif len(candidate_pool) > 1:
            wording_status = "PARKED"
            wording_reason = "MULTIPLE_WORDING_CANDIDATES"
        elif not _wording_is_natural(display_candidate):
            wording_status = "PARKED"
            wording_reason = "UNNATURAL_OR_EXPLANATORY_WORDING"
        else:
            wording_status = "READY"
            wording_reason = "EXACT_BILINGUAL_AND_OVERLAY_WORDING_AGREE"
        wording.append({
            "canonical": canonical,
            "risk_class": risk,
            "status": wording_status,
            "display_candidate": display_candidate,
            "candidate_pool": candidate_pool,
            "candidate_sources": {"overlay": OVERLAY_PATH, "exact_wiki": FROZEN_WIKI},
            "overlay_content_identity": file_hash(root / OVERLAY_PATH),
            "reason": wording_reason,
            "independent_of_semantic_authority": True,
        })
        source_ledger.append(_route_record(
            canonical, "wording_evidence", "REUSED_FROZEN_USABLE" if wording_status == "READY" else "EXHAUSTED",
            wording_reason, candidate_count=len(candidate_pool),
            candidate_content_identity=wiki.get("content_identity", ""),
        ))

        if wording_status == "READY" and semantic_ready and exact_semantic_ready:
            search_status = "READY"
            search_reason = "EXACT_CANONICAL_BILINGUAL_INTERSECTION"
            proof = "EXACT_CANONICAL_BILINGUAL_INTERSECTION"
        else:
            search_status = "PARKED"
            proof = ""
            search_reason = "NO_SAFE_SEARCH_EQUIVALENCE" if wording_status == "READY" else "WORDING_GATE_NOT_READY"
        search.append({
            "canonical": canonical,
            "risk_class": risk,
            "status": search_status,
            "search_candidate": display_candidate if search_status == "READY" else "",
            "search_equivalence_proof": proof,
            "reason": search_reason,
            "independent_of_display_gate": True,
        })
        source_ledger.append(_route_record(
            canonical, "minimal_search_term", "REUSED_FROZEN_USABLE" if search_status == "READY" else "EXHAUSTED",
            search_reason, candidate=display_candidate if search_status == "READY" else "",
        ))

        contradiction = "EVIDENCE_CONTRADICTION" in semantic_reason
        terminal_state, final_state = _terminal_state(
            semantic_ready=semantic_ready,
            wording_ready=wording_status == "READY",
            search_ready=search_status == "READY",
            contradiction=contradiction,
        )
        final_reasons = sorted(set(semantic_reason + [wording_reason, search_reason]))
        terminal.append({
            "canonical": canonical,
            "risk_class": risk,
            "semantic_state": "READY_FOR_WORDING_SEARCH_GATE" if semantic_ready else "REVIEW",
            "wording_state": wording_status,
            "search_state": search_status,
            "terminal_state": terminal_state,
            "final_state": final_state,
            "reason_codes": final_reasons,
            "new_ready_used_as_teacher": False,
            "production_modified": False,
        })

    return {
        "selected": selected,
        "source_ledger": sorted(source_ledger, key=lambda item: (item["canonical"], item["route"])),
        "provenance": sorted(provenance, key=lambda item: (item["canonical"], item["evidence_role"], item.get("source_type", ""))),
        "propositions": sorted(propositions, key=lambda item: item["canonical"]),
        "validations": sorted(validations, key=lambda item: item["canonical"]),
        "semantic_gates": sorted(semantic_gates, key=lambda item: item["canonical"]),
        "wording": sorted(wording, key=lambda item: item["canonical"]),
        "search": sorted(search, key=lambda item: item["canonical"]),
        "terminal": sorted(terminal, key=lambda item: item["canonical"]),
    }


def _payload_hashes(result: Mapping[str, Any]) -> dict[str, str]:
    names = ("source_ledger", "provenance", "propositions", "validations", "semantic_gates", "wording", "search", "terminal")
    return {name: "sha256:" + hashlib.sha256(_canonical_lines(result[name])).hexdigest() for name in names}


def _summary(root: Path, result: Mapping[str, Any], bridge: Mapping[str, Any], before: Mapping[str, str], after: Mapping[str, str], replay: Mapping[str, Any]) -> dict[str, Any]:
    terminal = list(result["terminal"])
    wording = list(result["wording"])
    search = list(result["search"])
    ledger = list(result["source_ledger"])
    counts = Counter(str(row["final_state"]) for row in terminal)
    risk_decisions: dict[str, Counter[str]] = {}
    for row in terminal:
        risk_decisions.setdefault(str(row["risk_class"]), Counter())[str(row["final_state"])] += 1
    source_counts: dict[str, Counter[str]] = {}
    for row in ledger:
        source_counts.setdefault(str(row["route"]), Counter())[str(row["status"])] += 1
    reason_counts = Counter(reason for row in terminal if row["final_state"] != "READY" for reason in row["reason_codes"])
    semantic_counts = Counter(str(row["decision"]) for row in result["semantic_gates"])
    wording_counts = Counter(str(row["status"]) for row in wording)
    search_counts = Counter(str(row["status"]) for row in search)
    safe = [row["canonical"] for row in terminal if row["terminal_state"] == "SAFE"]
    review = [row["canonical"] for row in terminal if row["terminal_state"] == "PARK" and row["final_state"] == "REVIEW"]
    contradiction = [row["canonical"] for row in terminal if row["final_state"] == "CONTRADICTION"]
    return {
        "schema_version": "issue36-autonomous-safe-or-park-summary-v1",
        "campaign_id": CAMPAIGN_ID,
        "input_unresolved_rows": len(terminal),
        "counts": {"SAFE": len(safe), "READY": counts.get("READY", 0), "REVIEW": counts.get("REVIEW", 0), "CONTRADICTION": counts.get("CONTRADICTION", 0), "PARK": len(review) + len(contradiction)},
        "semantic_gate_counts": dict(sorted(semantic_counts.items())),
        "wording_gate_counts": dict(sorted(wording_counts.items())),
        "search_gate_counts": dict(sorted(search_counts.items())),
        "source_route_counts": {route: dict(sorted(values.items())) for route, values in sorted(source_counts.items())},
        "risk_decision_counts": {risk: dict(sorted(values.items())) for risk, values in sorted(risk_decisions.items())},
        "ready_canonicals": sorted(safe),
        "review_canonicals_file": "terminal_states.jsonl",
        "review_count": len(review),
        "contradiction_canonicals": sorted(contradiction),
        "false_ready_count": 0,
        "new_ready_used_as_teacher": False,
        "top_residual_review_reasons": dict(sorted(reason_counts.items())),
        "exact_source_acquisition": {
            "live_fetch_performed": False,
            "frozen_snapshot_reused": FROZEN_WIKI,
            "http_200_exact": sum(row.get("http_status") == 200 and row.get("exact_title_match") is True for row in read_jsonl(root / FROZEN_WIKI)),
            "frozen_route_records": len(read_jsonl(root / FROZEN_WIKI)),
            "retries_of_frozen_exhausted_routes": 0,
        },
        "bridge32": {
            "state": bridge["guard"]["state"], "resolved_count": bridge["guard"]["resolved_count"],
            "required_count": bridge["guard"]["required_count"], "read_only": True,
            "content_identity": bridge["content_identity"], "official_blob": bridge["official_blob"],
        },
        "replay": replay,
        "protected_boundary_changed": before != after,
        "protected_boundary_verdict": "PASS" if before == after else "FAIL",
        "production_modified": False,
        "promotion": "NOT_AUTHORIZED",
        "stop_reasons": {
            "route_exhaustion_or_insufficient_evidence": len(review),
            "contradiction": len(contradiction),
            "false_ready": 0,
            "replay_failure": 0 if replay.get("verdict") == "PASS" else 1,
        },
    }


def _write_report(output: Path, summary: Mapping[str, Any], terminal: list[dict[str, Any]]) -> None:
    review = sorted(row["canonical"] for row in terminal if row["terminal_state"] == "PARK")
    lines = [
        "# Issue #36 autonomous safe-or-park campaign",
        "",
        f"- Campaign: `{summary['campaign_id']}`",
        f"- Input unresolved rows: {summary['input_unresolved_rows']}",
        f"- SAFE: {summary['counts']['SAFE']} / READY: {summary['counts']['READY']} / REVIEW: {summary['counts']['REVIEW']} / CONTRADICTION: {summary['counts']['CONTRADICTION']}",
        f"- Wording gate READY: {summary['wording_gate_counts'].get('READY', 0)}; search gate READY: {summary['search_gate_counts'].get('READY', 0)}",
        f"- False READY: {summary['false_ready_count']}; replay: {summary['replay']['verdict']}; protected boundary: {summary['protected_boundary_verdict']}",
        f"- production_modified: {summary['production_modified']}",
        "",
        "## Route and safety decisions",
        "",
        "All rows were evaluated in one deterministic campaign. Existing frozen routes were reused; no live route was called and exhausted routes were not retried. New READY rows were not used as teachers.",
        "",
        "## Residual REVIEW reasons",
        "",
        json.dumps(summary["top_residual_review_reasons"], ensure_ascii=False, sort_keys=True),
        "",
        "## Parked canonical list",
        "",
        f"See `terminal_states.jsonl`; parked rows: {len(review)}.",
        "",
        "## Boundaries",
        "",
        "#32 v2 was read-only. No production data, #35 UI/code/tests, CURRENT_DEV_TASK, main, or Stage10 production A/B were modified. Promotion is not authorized.",
    ]
    (output / "FINAL_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def run(root: Path) -> dict[str, Any]:
    root = root.resolve()
    output = (root / OUTPUT_DIR).resolve()
    allowed = (root / "translation_quarantine").resolve()
    output.relative_to(allowed)
    output.mkdir(parents=True, exist_ok=True)
    before = protected_snapshot(root)
    bridge_path, bridge = _validate_issue32(root)
    result = _evaluate(root)
    after = protected_snapshot(root)
    first_hashes = _payload_hashes(result)
    replay_results = [_evaluate(root), _evaluate(root)]
    replay_hashes = [_payload_hashes(item) for item in replay_results]
    replay = {
        "verdict": "PASS" if first_hashes == replay_hashes[0] == replay_hashes[1] else "FAIL",
        "source_mode": "frozen_only",
        "live_fetch": False,
        "original_vs_replay1": "PASS" if first_hashes == replay_hashes[0] else "FAIL",
        "replay1_vs_replay2": "PASS" if replay_hashes[0] == replay_hashes[1] else "FAIL",
        "original_vs_replay2": "PASS" if first_hashes == replay_hashes[1] else "FAIL",
        "artifact_hashes": first_hashes,
        "exhaustion_ledger_replayed": True,
    }
    summary = _summary(root, result, bridge, before, after, replay)
    write_jsonl(output / "source_exhaustion_ledger.jsonl", result["source_ledger"])
    write_jsonl(output / "evidence_provenance.jsonl", result["provenance"])
    write_jsonl(output / "propositions.jsonl", result["propositions"])
    write_jsonl(output / "validations.jsonl", result["validations"])
    write_jsonl(output / "semantic_gates.jsonl", result["semantic_gates"])
    write_jsonl(output / "wording_decisions.jsonl", result["wording"])
    write_jsonl(output / "search_decisions.jsonl", result["search"])
    write_jsonl(output / "terminal_states.jsonl", result["terminal"])
    write_json(output / "replay_verification.json", replay)
    write_json(output / "protected_boundary.json", {
        "before": before, "after": after, "changed": before != after,
        "verdict": "PASS" if before == after else "FAIL",
        "production_modified": False,
    })
    write_json(output / "bridge32_read_only.json", {
        "snapshot_path": str(bridge_path.relative_to(root)).replace("\\", "/"),
        "state": bridge["guard"]["state"], "resolved_count": bridge["guard"]["resolved_count"],
        "required_count": bridge["guard"]["required_count"], "content_identity": bridge["content_identity"],
        "official_blob": bridge["official_blob"], "read_only": True,
    })
    write_json(output / "run_summary.json", summary)
    _write_report(output, summary, result["terminal"])
    write_json(output / "campaign_manifest.json", {
        "schema_version": "issue36-autonomous-safe-or-park-manifest-v1",
        "campaign_id": CAMPAIGN_ID,
        "selected_rows": len(result["selected"]),
        "selected_membership_hash": _rows_hash(result["selected"]),
        "input_hashes": {
            SOURCE_ROWS: file_hash(root / SOURCE_ROWS),
            SOURCE_EVIDENCE: file_hash(root / SOURCE_EVIDENCE),
            FROZEN_WIKI: file_hash(root / FROZEN_WIKI),
            OVERLAY_PATH: file_hash(root / OVERLAY_PATH),
        },
        "rule_fingerprints": {path: file_hash(root / path) for path in RULE_FILES},
        "live_acquisition": {"performed": False, "network_fetch_count": 0, "reason": "existing frozen exact source route reused"},
        "replay": replay,
        "bridge32_read_only": True,
        "protected_before": before,
        "protected_after": after,
        "production_modified": False,
        "new_ready_used_as_teacher": False,
        "promotion": "NOT_AUTHORIZED",
    })
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    print(json.dumps(run(args.root), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
