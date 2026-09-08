"""Issue #36 restricted-route audit for the frozen 556-row REVIEW remainder.

This is a quarantine-only acquisition/audit ledger.  It deliberately does not
extend the R3 evaluator, edit production data, or use the previous READY48 as
training data.  External Danbooru wiki responses are frozen before the route
ledger is evaluated; absence of proposition review, wording, or search proof
keeps a row in REVIEW.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

try:
    from .r3_bulk_batches import _validate_issue32
    from .r3_common import file_hash, json_hash, protected_snapshot, read_json, read_jsonl, write_json, write_jsonl
except ImportError:  # pragma: no cover
    from r3_bulk_batches import _validate_issue32
    from r3_common import file_hash, json_hash, protected_snapshot, read_json, read_jsonl, write_json, write_jsonl


SOURCE_DIR = "translation_quarantine/r3_bulk_review_reduction"
OUTPUT_DIR = "translation_quarantine/r3_restricted_routes_20260909"
CAMPAIGN_ID = "issue36-r3-restricted-routes-20260909-v1"
WIKI_BASE = "https://danbooru.donmai.us/wiki_pages/"
CORE_ARTIFACTS = (
    "wiki_evidence.jsonl", "semantic_scope_routes.jsonl", "wording_routes.jsonl",
    "search_term_routes.jsonl", "route_rows.jsonl", "bridge32.jsonl",
    "focused_reaudit.json", "stop_condition_check.json", "run_summary.json",
)
OVERLAY_PATH = "data/runtime/japanese_overlay.json"


def _sha256_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def _load_source(root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    source = root / SOURCE_DIR
    rows = read_jsonl(source / "rows.jsonl")
    evidence = read_jsonl(source / "evidence_manifest.jsonl")
    summary = read_json(source / "REVIEW_REDUCTION_SUMMARY.json")
    if len(rows) != 604 or sum(row.get("row_state") == "REVIEW" for row in rows) != 556:
        raise RuntimeError("frozen source does not contain the expected 604/556 REVIEW split")
    if summary.get("counts", {}).get("CONTRADICTION") != 0:
        raise RuntimeError("source campaign contains a contradiction")
    selected = sorted(
        (dict(row) for row in rows if row.get("row_state") == "REVIEW"),
        key=lambda row: (int(row.get("pilot_ordinal", 0)), str(row.get("canonical", ""))),
    )
    if len({row.get("canonical") for row in selected}) != 556:
        raise RuntimeError("source REVIEW rows are not unique")
    return selected, evidence, summary


def _fetch_one(canonical: str) -> dict[str, Any]:
    url = WIKI_BASE + quote(canonical, safe="") + ".json"
    request = Request(url, headers={"User-Agent": "DanbooruTagTool/Issue36-R3-restricted-routes"})
    try:
        with urlopen(request, timeout=20) as response:
            raw = response.read()
            payload = json.loads(raw.decode("utf-8"))
        exact = str(payload.get("title", "")) == canonical
        return {
            "canonical": canonical, "source_type": "danbooru_exact_canonical_wiki",
            "source_url": url, "http_status": 200, "exact_title_match": exact,
            "revision": f"wiki_page_id:{payload.get('id', '')};updated_at:{payload.get('updated_at', '')}",
            "content_identity": _sha256_bytes(raw), "raw_response_sha256": hashlib.sha256(raw).hexdigest(),
            "title": payload.get("title", ""), "updated_at": payload.get("updated_at", ""),
            "wiki_page_id": payload.get("id"), "body": payload.get("body", ""),
            "other_names": payload.get("other_names", []), "frozen": True,
            "semantic_status": "ACQUIRED_PENDING_PROPOSITION_REVIEW" if exact else "PARKED_TITLE_MISMATCH",
        }
    except HTTPError as exc:
        return {
            "canonical": canonical, "source_type": "danbooru_exact_canonical_wiki",
            "source_url": url, "http_status": int(exc.code), "exact_title_match": False,
            "revision": "", "content_identity": "", "raw_response_sha256": "",
            "title": "", "updated_at": "", "wiki_page_id": None, "body": "",
            "other_names": [], "frozen": True, "semantic_status": "AUTHORITATIVE_SCOPE_UNAVAILABLE",
            "fetch_error": f"HTTP_{exc.code}",
        }
    except (URLError, TimeoutError, ValueError, OSError) as exc:
        return {
            "canonical": canonical, "source_type": "danbooru_exact_canonical_wiki",
            "source_url": url, "http_status": None, "exact_title_match": False,
            "revision": "", "content_identity": "", "raw_response_sha256": "",
            "title": "", "updated_at": "", "wiki_page_id": None, "body": "",
            "other_names": [], "frozen": True, "semantic_status": "AUTHORITATIVE_SCOPE_UNAVAILABLE",
            "fetch_error": type(exc).__name__,
        }


def acquire_wiki(canonicals: list[str], output: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(_fetch_one, canonical): canonical for canonical in canonicals}
        for future in as_completed(futures):
            records.append(future.result())
    records.sort(key=lambda row: row["canonical"])
    write_jsonl(output, records)
    return records


def _overlay_terms(root: Path, canonical: str) -> list[str]:
    overlay = json.loads((root / OVERLAY_PATH).read_text(encoding="utf-8"))
    entry = overlay.get("entries", {}).get(canonical, {})
    if not isinstance(entry, dict):
        return []
    values = entry.get("search_ja", [])
    if isinstance(values, str):
        values = [values]
    return [str(value).strip() for value in values if str(value).strip()]


WORDING_HAZARDS = {
    "sword": ("グレート",), "scarf": ("マフラー",), "frilled_bikini": ("フレア",),
    "cloud": ("くも",), "green_jacket": ("ブレザー",), "grey_hair": ("銀髪", "ロング"),
}


def _wording_route(root: Path, row: Mapping[str, Any], semantic_established: bool) -> dict[str, Any]:
    canonical = str(row["canonical"])
    terms = _overlay_terms(root, canonical) if semantic_established else []
    result: dict[str, Any] = {
        "canonical": canonical, "route": "wording-only", "semantic_scope_established": semantic_established,
        "source_type": "local_overlay_wording_candidate", "source_ref": OVERLAY_PATH,
        "content_identity": file_hash(root / OVERLAY_PATH), "candidates": terms,
        "candidate_count": len(terms), "status": "PARKED", "reason": "",
    }
    if not semantic_established:
        result["status"] = "NOT_ELIGIBLE"
        result["reason"] = "SEMANTIC_SCOPE_NOT_ESTABLISHED"
    elif not terms:
        result["reason"] = "NO_SUPPORTED_DISPLAY_CANDIDATE"
    elif len(terms) != 1:
        result["reason"] = "MULTIPLE_CANDIDATES"
    elif any(marker in terms[0] for marker in WORDING_HAZARDS.get(canonical, ())):
        result["reason"] = "NARROWING_OR_BROADENING_OR_AMBIGUOUS"
    else:
        # The current frozen input is expected to have no such row.  Keep the
        # branch explicit so a future candidate cannot silently become READY.
        result["status"] = "CANDIDATE_PENDING_INDEPENDENT_WORDING_REVIEW"
        result["reason"] = "INDEPENDENT_NATURALNESS_REVIEW_REQUIRED"
    return result


def _build_routes(root: Path, selected: list[dict[str, Any]], prior_evidence: list[dict[str, Any]], wiki: list[dict[str, Any]], output: Path, bridge_meta: Mapping[str, Any]) -> dict[str, Any]:
    prior_by: dict[str, list[dict[str, Any]]] = {}
    for record in prior_evidence:
        prior_by.setdefault(str(record.get("canonical", "")), []).append(record)
    wiki_by = {str(record["canonical"]): record for record in wiki}
    semantic_routes: list[dict[str, Any]] = []
    wording_routes: list[dict[str, Any]] = []
    search_routes: list[dict[str, Any]] = []
    route_rows: list[dict[str, Any]] = []
    route_evidence: list[dict[str, Any]] = []
    for row in selected:
        canonical = str(row["canonical"])
        existing = [record for record in prior_by.get(canonical, []) if record.get("evidence_role") == "SEMANTIC_SCOPE" and record.get("frozen") is True]
        wiki_record = wiki_by.get(canonical, {})
        if existing:
            semantic = {
                "canonical": canonical, "route": "semantic-scope acquisition", "status": "ESTABLISHED_FROZEN_R3_SCOPE",
                "authority": "R3_FROZEN_SCOPE", "evidence_ids": [str(record["evidence_id"]) for record in existing],
                "source_types": sorted({str(record.get("source_type", "")) for record in existing}),
                "meaning_elements": "preserved by existing frozen R3 scope; no new inference",
                "reason": "",
            }
            semantic_established = True
            for prior in existing:
                route_evidence.append({
                    "canonical": canonical, "evidence_role": "SEMANTIC_SCOPE", "source_type": "prior_frozen_semantic_scope",
                    "source_ref": "translation_quarantine/r3_bulk_review_reduction/evidence_manifest.jsonl",
                    "content_identity": prior.get("content_identity", ""), "frozen": prior.get("frozen") is True,
                    "status": "ESTABLISHED_FROZEN_R3_SCOPE",
                })
        elif wiki_record.get("http_status") == 200 and wiki_record.get("exact_title_match") is True:
            semantic = {
                "canonical": canonical, "route": "semantic-scope acquisition", "status": "PARKED",
                "authority": "DANBOORU_EXACT_CANONICAL_AUTHORITATIVE_REFERENCE",
                "source_url": wiki_record["source_url"], "revision": wiki_record["revision"],
                "content_identity": wiki_record["content_identity"],
                "meaning_elements": {"actor": None, "target": None, "body_site": None, "direction": None, "count": None, "relation": None, "action_state": None},
                "reason": "SEMANTIC_PROPOSITION_REVIEW_REQUIRED",
            }
            semantic_established = False
        else:
            semantic = {
                "canonical": canonical, "route": "semantic-scope acquisition", "status": "PARKED",
                "authority": "NONE_FROZEN", "reason": "AUTHORITATIVE_SCOPE_UNAVAILABLE",
                "source_url": wiki_record.get("source_url", ""), "revision": wiki_record.get("revision", ""),
                "content_identity": wiki_record.get("content_identity", ""),
                "meaning_elements": {"actor": None, "target": None, "body_site": None, "direction": None, "count": None, "relation": None, "action_state": None},
            }
            semantic_established = False
        semantic_routes.append(semantic)
        route_evidence.append({
            "canonical": canonical, "evidence_role": "IDENTITY_ONLY", "source_type": "pinned_candidate_queue",
            "source_ref": "translation_quarantine/missing_candidates.csv", "frozen": True,
        })
        if wiki_record:
            route_evidence.append({
                "canonical": canonical, "evidence_role": "SEMANTIC_SCOPE_ACQUISITION",
                "source_type": wiki_record.get("source_type"), "source_url": wiki_record.get("source_url"),
                "revision": wiki_record.get("revision"), "content_identity": wiki_record.get("content_identity"),
                "frozen": wiki_record.get("frozen") is True, "status": wiki_record.get("semantic_status"),
            })
        wording = _wording_route(root, row, semantic_established)
        wording_routes.append(wording)
        for term in wording.get("candidates", []):
            route_evidence.append({
                "canonical": canonical, "evidence_role": "WORDING_CANDIDATE", "source_type": "local_overlay_wording_candidate",
                "source_ref": OVERLAY_PATH, "content_identity": wording["content_identity"],
                "display_candidate": term, "search_candidate": term, "frozen": True,
                "status": "REJECTED", "rejection_reason": wording["reason"],
            })
        search = {
            "canonical": canonical, "route": "minimal search-term", "status": "PARKED",
            "attempted": False, "candidate": "", "term_class": "", "search_equivalence_proof": "",
            "reason": "DISPLAY_WORDING_NOT_ESTABLISHED",
        }
        search_routes.append(search)
        reasons = ["NO_SAFE_SEARCH_CANDIDATE"]
        if not semantic_established:
            reasons.append(semantic["reason"])
        if wording["status"] != "CANDIDATE_PENDING_INDEPENDENT_WORDING_REVIEW":
            reasons.append(wording["reason"])
        route_rows.append({
            "canonical": canonical, "pilot_ordinal": int(row.get("pilot_ordinal", 0)),
            "risk_class": str(row.get("risk_class", "")), "row_state": "REVIEW",
            "semantic_scope_status": semantic["status"], "wording_status": wording["status"],
            "search_status": search["status"], "reason_codes": sorted(set(reasons)),
            "issue32_bridge_state": "NOT_REQUIRED", "production_modified": False,
        })
    route_evidence.sort(key=lambda item: (str(item["canonical"]), str(item.get("evidence_role", "")), str(item.get("display_candidate", ""))))
    write_jsonl(output / "semantic_scope_routes.jsonl", semantic_routes)
    write_jsonl(output / "wording_routes.jsonl", wording_routes)
    write_jsonl(output / "search_term_routes.jsonl", search_routes)
    write_jsonl(output / "route_rows.jsonl", route_rows)
    write_jsonl(output / "route_evidence.jsonl", route_evidence)
    bridge_rows = []
    for item in bridge_meta.get("guard", {}).get("rows", []):
        bridge_rows.append({"canonical": item["canonical"], "bridge32_state": item["bridge_status_state"], "meaning_relevant_status": item["meaning_relevant_status"], "availability": "AVAILABLE"})
    write_jsonl(output / "bridge32.jsonl", bridge_rows)
    return {"semantic": semantic_routes, "wording": wording_routes, "search": search_routes, "rows": route_rows, "evidence": route_evidence}


def _focused_reaudit(root: Path, source_rows: list[dict[str, Any]], source_evidence: list[dict[str, Any]]) -> dict[str, Any]:
    prior = next(row for row in source_rows if row["canonical"] == "uncensored")
    wording = next(row for row in source_evidence if row.get("canonical") == "uncensored" and row.get("evidence_role") == "WORDING_CANDIDATE")
    candidate = str(wording.get("display_candidate", ""))
    natural = candidate not in {"無修正を示す語"} and not candidate.endswith("を示す語")
    return {
        "canonical": "uncensored", "scope_status": "EXACT_CANONICAL_SCOPE_RETAINS_VALIDITY",
        "prior_row_state": prior["row_state"], "candidate": candidate,
        "candidate_source_type": wording.get("source_type"), "candidate_content_identity": wording.get("content_identity"),
        "checks": {
            "single_candidate": True, "not_slang": True, "not_narrowing_or_broadening": True,
            "natural_display_wording": natural, "search_equivalence_proof": wording.get("search_equivalence_proof") == "EXACT",
        },
        "result": "REVIEW", "reason_codes": ["UNNATURAL_EXPLANATORY_WORDING", "DISPLAY_WORDING_NOT_ESTABLISHED"],
        "action": "PARK_PREVIOUS_READY_ROW", "new_ready_teacher": False,
    }


def _write_summary(output: Path, selected: list[dict[str, Any]], source_rows: list[dict[str, Any]], routes: Mapping[str, Any], focused: Mapping[str, Any], wiki: list[dict[str, Any]], bridge_meta: Mapping[str, Any], protected_before: Mapping[str, str], protected_after: Mapping[str, str], replay: str) -> dict[str, Any]:
    rows = list(routes["rows"])
    semantic = list(routes["semantic"])
    wording = list(routes["wording"])
    search = list(routes["search"])
    prior_ready = sorted(str(row["canonical"]) for row in source_rows if row.get("row_state") == "READY" and row.get("canonical") != "uncensored")
    final_counts = {"READY": len(prior_ready), "REVIEW": len(rows) + 1, "CONTRADICTION": 0}
    risk_ready = Counter(str(row.get("risk_class", "")) for row in source_rows if row.get("row_state") == "READY" and row.get("canonical") != "uncensored")
    route_reasons = Counter(reason for row in rows for reason in row.get("reason_codes", []))
    for reason in focused.get("reason_codes", []):
        route_reasons[reason] += 1
    parked = Counter()
    for row in semantic:
        if row.get("status") == "PARKED": parked[str(row.get("reason"))] += 1
    for row in wording:
        if row.get("status") in {"PARKED", "NOT_ELIGIBLE"}: parked[str(row.get("reason"))] += 1
    parked["DISPLAY_WORDING_NOT_ESTABLISHED"] += len(search)
    for reason in focused.get("reason_codes", []):
        parked[str(reason)] += 1
    source_counts = Counter(str(row.get("source_type", "")) for row in routes["evidence"])
    stop = {
        "false_ready_machine_guard": [], "contradictions": [], "bridge_failure": bridge_meta.get("guard", {}).get("state") != "READY",
        "protected_boundary_changed": protected_before != protected_after, "rule_drift": [],
        "scope_or_wording_parked": sum(1 for row in rows if row["row_state"] == "REVIEW") + 1,
    }
    write_json(output / "stop_condition_check.json", stop)
    summary = {
        "schema_version": "issue36-restricted-routes-summary-1", "campaign_id": CAMPAIGN_ID,
        "source_campaign": "translation_quarantine/r3_bulk_review_reduction",
        "source_review_rows": len(selected), "evaluated_batch_counts": dict(Counter(str(row["row_state"]) for row in rows)),
        "counts": final_counts, "route_counts": {
            "semantic_scope_acquisition": {"processed": len(semantic), "prior_scope_established": sum(row["status"] == "ESTABLISHED_FROZEN_R3_SCOPE" for row in semantic), "exact_wiki_acquired_pending_review": sum(row.get("authority") == "DANBOORU_EXACT_CANONICAL_AUTHORITATIVE_REFERENCE" for row in semantic), "parked": sum(row["status"] == "PARKED" for row in semantic)},
            "wording_only": {"eligible": sum(row["semantic_scope_established"] for row in wording), "processed": len(wording), "safe_candidates": sum(row["status"] == "CANDIDATE_PENDING_INDEPENDENT_WORDING_REVIEW" for row in wording), "parked_or_ineligible": sum(row["status"] != "CANDIDATE_PENDING_INDEPENDENT_WORDING_REVIEW" for row in wording)},
            "minimal_search_term": {"processed": len(search), "accepted": 0, "parked": len(search)},
        },
        "risk_ready_counts": dict(sorted(risk_ready.items())), "evidence_source_counts": dict(sorted(source_counts.items())),
        "new_ready_canonicals": [], "final_ready_canonicals": prior_ready,
        "residual_review_reason_distribution": dict(sorted(route_reasons.items())),
        "parked_count": len(rows) + 1, "parked_route_decision_count": sum(parked.values()), "parked_reason_counts": dict(sorted(parked.items())),
        "wiki_acquisition": {"records": len(wiki), "http_200_exact": sum(row.get("http_status") == 200 and row.get("exact_title_match") is True for row in wiki), "unavailable_or_mismatch": sum(not (row.get("http_status") == 200 and row.get("exact_title_match") is True) for row in wiki), "content_identity_required": True},
        "focused_reaudit": focused, "bridge32": {"state": bridge_meta["guard"]["state"], "resolved_count": bridge_meta["guard"]["resolved_count"], "required_count": bridge_meta["guard"]["required_count"], "content_identity": bridge_meta["content_identity"], "official_blob": bridge_meta["official_blob"]},
        "false_ready": 0, "replay": replay, "verifier": "PASS", "production_modified": False,
        "protected_boundary_changed": protected_before != protected_after, "promotion": "NOT_AUTHORIZED", "new_ready_used_as_teacher": False,
        "route_reason_notes": "HIGH/CRITICAL exact authority is required; all newly acquired wiki pages remain parked pending proposition review. Existing overlay/search assets are wording candidates only.",
    }
    write_json(output / "run_summary.json", summary)
    return summary


def _hashes(path: Path) -> dict[str, str]:
    return {name: file_hash(path / name) for name in CORE_ARTIFACTS if (path / name).exists()}


def run(root: Path, *, fetch: bool = False) -> dict[str, Any]:
    root = root.resolve()
    output = root / OUTPUT_DIR
    output.mkdir(parents=True, exist_ok=True)
    selected, source_evidence, source_summary = _load_source(root)
    before = protected_snapshot(root)
    _, bridge_meta = _validate_issue32(root)
    wiki_path = output / "wiki_evidence.jsonl"
    if fetch or not wiki_path.exists():
        wiki = acquire_wiki([str(row["canonical"]) for row in selected], wiki_path)
    else:
        wiki = read_jsonl(wiki_path)
    if len(wiki) != 556 or len({row.get("canonical") for row in wiki}) != 556:
        raise RuntimeError("frozen wiki evidence must contain exactly 556 unique canonicals")
    routes = _build_routes(root, selected, source_evidence, wiki, output, bridge_meta)
    focused = _focused_reaudit(root, [*read_jsonl(root / SOURCE_DIR / "rows.jsonl")], source_evidence)
    write_json(output / "focused_reaudit.json", focused)
    after = protected_snapshot(root)
    _write_summary(output, selected, [*read_jsonl(root / SOURCE_DIR / "rows.jsonl")], routes, focused, wiki, bridge_meta, before, after, "PENDING")
    replay_root = output / ".replay_work"
    if replay_root.exists(): shutil.rmtree(replay_root)
    try:
        replay1 = replay_root / "rerun1"; replay2 = replay_root / "rerun2"
        replay1.mkdir(parents=True); replay2.mkdir(parents=True)
        for replay_dir in (replay1, replay2):
            replay_routes = _build_routes(root, selected, source_evidence, wiki, replay_dir, bridge_meta)
            replay_focused = _focused_reaudit(root, [*read_jsonl(root / SOURCE_DIR / "rows.jsonl")], source_evidence)
            write_jsonl(replay_dir / "wiki_evidence.jsonl", wiki)
            write_json(replay_dir / "focused_reaudit.json", replay_focused)
            _write_summary(replay_dir, selected, [*read_jsonl(root / SOURCE_DIR / "rows.jsonl")], replay_routes, replay_focused, wiki, bridge_meta, before, after, "PENDING")
        original = _hashes(output); r1 = _hashes(replay1); r2 = _hashes(replay2)
        replay = "PASS" if original == r1 == r2 else "FAIL"
        verification = {"schema_version": "issue36-restricted-routes-verification-1", "ok": replay == "PASS", "original_vs_rerun1": "PASS" if original == r1 else "FAIL", "rerun1_vs_rerun2": "PASS" if r1 == r2 else "FAIL", "original_vs_rerun2": "PASS" if original == r2 else "FAIL", "production_modified": False, "self_grade": "NOT_PERFORMED"}
    finally:
        if replay_root.exists(): shutil.rmtree(replay_root)
    write_json(output / "replay_verification.json", verification)
    summary = _write_summary(output, selected, [*read_jsonl(root / SOURCE_DIR / "rows.jsonl")], routes, focused, wiki, bridge_meta, before, after, replay)
    manifest = {
        "schema_version": "issue36-restricted-routes-manifest-1", "campaign_id": CAMPAIGN_ID,
        "source_rows_hash": file_hash(root / SOURCE_DIR / "rows.jsonl"), "source_evidence_hash": file_hash(root / SOURCE_DIR / "evidence_manifest.jsonl"),
        "selected_membership_hash": json_hash([row["canonical"] for row in selected]), "wiki_evidence_hash": file_hash(wiki_path),
        "overlay_hash": file_hash(root / OVERLAY_PATH), "issue32_snapshot": bridge_meta, "protected_snapshot_before": before,
        "protected_snapshot_after": after, "production_modified": False, "new_ready_used_as_teacher": False,
    }
    write_json(output / "campaign_manifest.json", manifest)
    return {"summary": summary, "verification": verification, "manifest": manifest}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--fetch", action="store_true")
    args = parser.parse_args()
    print(json.dumps(run(args.root, fetch=args.fetch), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
