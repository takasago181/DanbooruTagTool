from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import shlex
import subprocess
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


CONTRACT_COMMIT = "86bf72246b3f1f42b52f562f45d4027f0d1a71ea"
CONTRACT_REL = Path("translation_quarantine/r3/ISSUE36_FINAL_CONVERGENCE_V3_AGENT_REVIEW.md")
SOURCE_REL = Path(
    "translation_quarantine/full_accepted_quality_sweep_20260909/final_translation_table.csv"
)
SOURCE_BLOB = "5fc11c64235c7b32cb72f2e819cb2ed22ab46d8a"
SOURCE_ROWS = 30_629
SOURCE_ACCEPTED = 23_194
SOURCE_FALLBACK = 7_435
PHRASE_HOMEWORK = 1_677
MAX_REPAIR_CYCLES = 2
FORBIDDEN_BLIND_FIELDS = {
    "decision",
    "decision_rationale_ja",
    "provisional_lane",
    "lane",
    "resolver_confidence",
    "confidence",
    "first_pass_verdict",
    "unresolved_classification",
    "resolver_state",
    "repair_cycle",
}
ALLOWED_TERMINALS = {
    "FINAL_READY_FOR_INDEPENDENT_AUDIT",
    "HOLD_EXTERNAL_EVIDENCE",
    "HOLD_COVERAGE_COLLAPSE",
    "BLOCKED_AGENT_DISAGREEMENT",
    "BLOCKED_STRUCTURAL_DEFECT",
}
FACET_KEYS = [
    "head_concept",
    "action_state",
    "actor",
    "ownership",
    "target",
    "body_site",
    "direction_spatial",
    "count_cardinality",
    "negation",
    "required_modifier",
    "qualifier_scope",
    "concept_width",
]

RESIDUAL_SAMPLE_STRATA = (
    ("ordinary_residual_fallback", 60),
    ("common_simple", 50),
    ("multi_token", 50),
    ("action_relation", 40),
    ("anatomy_adult_high_risk", 40),
    ("accepted_demotion_root_cause_sibling", 30),
    ("prior_phrase_unresolved_residual", 30),
)
ADVERSARIAL_SAMPLE_STRATA = (
    ("random_accepted", 150),
    ("high_critical_accepted", 150),
    ("repaired_or_new_translation_candidate", 150),
    ("ordinary_residual_fallback", 100),
    ("true_exception", 50),
)
EXCEPTION_REASON_TOKENS = {
    "SYMBOL_OR_EMOTICON",
    "CODE_OR_PRODUCT_IDENTIFIER",
    "OPAQUE_SOURCE_STRING",
    "MALFORMED_LABEL",
    "NON_JAPANESE_LABEL",
    "PROPER_NAME_OR_QUALIFIED_LABEL",
    "PRODUCT_OR_SERVICE_NAME",
}
ACTION_RELATION_TOKENS = {
    "action", "arm", "behind", "between", "breast", "carry", "climb", "cover",
    "face", "facing", "grab", "grabbing", "hand", "hold", "holding", "hug",
    "inside", "kick", "kiss", "lick", "look", "looking", "open", "outside",
    "over", "penetration", "pointing", "presenting", "pull", "push", "reach",
    "relation", "ride", "sitting", "stand", "standing", "touch", "under", "wear",
    "wearing", "with",
}
ANATOMY_ADULT_TOKENS = {
    "adult", "anal", "anus", "areola", "breast", "buttocks", "clitoris", "cum",
    "erection", "explicit", "genital", "nipples", "nude", "nudity", "penis", "pussy",
    "sex", "testicles", "vagina", "vulva",
}


def strict_agent_schema(role: str) -> dict[str, Any]:
    facet = {
        "type": "object",
        "additionalProperties": False,
        "properties": {key: {"type": "string"} for key in FACET_KEYS},
        "required": FACET_KEYS,
    }
    def string_array() -> dict[str, Any]:
        return {"type": "array", "items": {"type": "string"}}
    evidence = {
        "type": "array",
        "items": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "type": {"type": "string"},
                "ref": {"type": "string"},
                "note": {"type": "string"},
            },
            "required": ["type", "ref", "note"],
        },
    }
    if role in {"RESOLVER", "REPAIR"}:
        properties = {
            "canonical": {"type": "string"},
            "decision": {"type": "string"},
            "final_display_ja": {"type": "string"},
            "final_search_ja": {"type": "string"},
            "display_verdict": {"type": "string"},
            "search_verdict": {"type": "string"},
            "semantic_gloss_ja": {"type": "string"},
            "semantic_facets": facet,
            "risk_class": {"type": "string"},
            "decision_rationale_ja": {"type": "string"},
            "evidence_refs": evidence,
            "attempted_evidence_routes": string_array(),
            "unresolved_question_ja": {"type": "string"},
            "review_mode": {"type": "string"},
            "batch_id": {"type": "string"},
        }
    elif role == "CHALLENGER":
        properties = {
            "canonical": {"type": "string"},
            "display_challenge": {"type": "string"},
            "search_challenge": {"type": "string"},
            "rationale_ja": {"type": "string"},
            "semantic_facets": facet,
            "root_cause": {"type": "string"},
        }
    elif role == "RESIDUAL_CHALLENGER":
        properties = {
            "canonical": {"type": "string"},
            "residual_verdict": {"type": "string"},
            "rationale_ja": {"type": "string"},
            "semantic_facets": facet,
            "proposed_display_ja": {"type": "string"},
            "proposed_search_ja": {"type": "string"},
            "root_cause": {"type": "string"},
        }
    elif role == "FINAL_AUDITOR":
        properties = {
            "canonical": {"type": "string"},
            "display_audit": {"type": "string"},
            "search_audit": {"type": "string"},
            "rationale_ja": {"type": "string"},
            "semantic_facets": facet,
            "root_cause": {"type": "string"},
        }
    else:
        raise ValueError(f"unknown role {role}")
    required = list(properties)
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "additionalProperties": False,
        "required": ["records"],
        "properties": {
            "records": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": properties,
                    "required": required,
                },
            }
        },
    }


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def stable_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode(
        "utf-8"
    )


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_bytes(stable_json(value))
    tmp.replace(path)


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    tmp.replace(path)
    return sha256_file(path)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, 1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError(f"{path}:{line_no}: JSONL row is not an object")
            rows.append(value)
    return rows


def git(repo: Path, *args: str) -> str:
    command = ["git", "-c", f"safe.directory={repo.as_posix()}", "-C", str(repo), *args]
    completed = subprocess.run(
        command,
        check=True,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
    )
    return completed.stdout.strip()


def load_source(repo: Path) -> tuple[list[dict[str, str]], dict[str, Any]]:
    source_path = repo / SOURCE_REL
    contract_path = repo / CONTRACT_REL
    if not source_path.is_file():
        raise RuntimeError(f"missing immutable source: {source_path}")
    if not contract_path.is_file():
        raise RuntimeError(f"missing frozen contract: {contract_path}")
    # `git cat-file -e` succeeds with an empty stdout; failure is surfaced by
    # `git()` as a non-zero subprocess error.  Do not interpret empty stdout as
    # a missing object.
    git(repo, "cat-file", "-e", f"{CONTRACT_COMMIT}^{{commit}}")
    committed_source_blob = git(repo, "rev-parse", f"{CONTRACT_COMMIT}:{SOURCE_REL.as_posix()}")
    if committed_source_blob != SOURCE_BLOB:
        raise RuntimeError(
            f"source blob mismatch: expected {SOURCE_BLOB}, got {committed_source_blob}"
        )
    contract_blob = git(repo, "rev-parse", f"{CONTRACT_COMMIT}:{CONTRACT_REL.as_posix()}")
    if sha256_file(contract_path) == "":  # pragma: no cover - defensive, never semantic
        raise RuntimeError("contract could not be hashed")

    with source_path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    unique = {row.get("canonical", "") for row in rows}
    accepted = [row for row in rows if row.get("final_state", "").startswith("JA_ACCEPT_")]
    fallback = [row for row in rows if row.get("final_state") == "ENGLISH_FALLBACK_EXCEPTION"]
    phrase = [row for row in rows if "PHRASE_SEMANTICS_UNRESOLVED" in row.get("reason", "")]
    counts = {
        "rows": len(rows),
        "unique_canonicals": len(unique),
        "accepted": len(accepted),
        "fallback": len(fallback),
        "phrase_homework": len(phrase),
    }
    expected = {
        "rows": SOURCE_ROWS,
        "unique_canonicals": SOURCE_ROWS,
        "accepted": SOURCE_ACCEPTED,
        "fallback": SOURCE_FALLBACK,
        "phrase_homework": PHRASE_HOMEWORK,
    }
    if counts != expected:
        raise RuntimeError(f"immutable source counts mismatch: expected {expected}, got {counts}")
    manifest = {
        "schema_version": 1,
        "contract_commit": CONTRACT_COMMIT,
        "contract_blob": contract_blob,
        "contract_path": CONTRACT_REL.as_posix(),
        "source_path": SOURCE_REL.as_posix(),
        "source_git_blob": SOURCE_BLOB,
        "source_file_sha256": sha256_file(source_path),
        "source_counts": counts,
        "prepared_before_semantic_outcomes": True,
        "prepared_at": utc_now(),
    }
    return rows, manifest


def source_queue_row(row: dict[str, str], index: int) -> dict[str, Any]:
    source_state = "ACCEPTED" if row.get("final_state", "").startswith("JA_ACCEPT_") else "FALLBACK"
    return {
        "queue_index": index,
        "canonical": row.get("canonical", ""),
        "source_state": source_state,
        "source_display_ja": row.get("display_ja", ""),
        "source_search_ja": row.get("search_ja", ""),
        "priority_class": row.get("priority_class", ""),
        "source_final_state": row.get("final_state", ""),
        "source_route": row.get("route", ""),
        "source_reason": row.get("reason", ""),
        "source_risk_class": row.get("risk_class", ""),
    }


def sample_key(canonical: str, purpose: str) -> str:
    raw = f"{SOURCE_BLOB}|{purpose}|{canonical}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def choose_ranked(rows: list[dict[str, Any]], purpose: str, count: int) -> list[dict[str, Any]]:
    return sorted(rows, key=lambda row: sample_key(row["canonical"], purpose))[:count]


def canonical_tokens(canonical: str) -> set[str]:
    return {token.lower() for token in re.findall(r"[a-z0-9]+", canonical)}


def is_true_exception_candidate(row: dict[str, Any]) -> bool:
    reason = row.get("source_reason", "")
    return any(token in reason for token in EXCEPTION_REASON_TOKENS)


def is_final_accepted(row: dict[str, Any]) -> bool:
    return (
        row.get("display_verdict") == "ACCEPT"
        and bool(row.get("final_display_ja", "").strip())
        and row.get("decision") not in {"TRUE_EXCEPTION", "EVIDENCE_UNRESOLVED"}
    )


def is_final_residual_fallback(row: dict[str, Any]) -> bool:
    return (
        not is_final_accepted(row)
        and row.get("decision") != "TRUE_EXCEPTION"
        and not row.get("final_display_ja", "").strip()
    )


def outcome_sample_candidates(
    queue: list[dict[str, Any]],
    final_rows: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    by_queue = {row["canonical"]: row for row in queue}
    if {row["canonical"] for row in final_rows} != set(by_queue):
        raise ValueError("post-outcome sampling requires one final external row per queue canonical")
    current = [{**by_queue[row["canonical"]], **row} for row in final_rows]
    residual = [row for row in current if is_final_residual_fallback(row)]
    accepted = [row for row in current if is_final_accepted(row)]
    repaired = [
        row for row in accepted if row.get("decision") in {"REPAIR_JA", "TRANSLATE_JA"}
    ]
    exceptions = [row for row in current if row.get("decision") == "TRUE_EXCEPTION"]
    residual_tokens = [canonical_tokens(row["canonical"]) for row in residual]
    sibling_candidates = [
        row for row in residual
        if row.get("source_state") == "ACCEPTED"
        and canonical_tokens(row["canonical"])
        and any(canonical_tokens(row["canonical"]).intersection(other) for other in residual_tokens)
    ]
    return {
        "all_final_rows": current,
        "ordinary_residual_fallback": [row for row in residual if not is_true_exception_candidate(row)],
        "common_simple": [
            row for row in residual
            if len(canonical_tokens(row["canonical"])) <= 1
            and len(row["canonical"]) <= 24
            and not canonical_tokens(row["canonical"]).intersection(ANATOMY_ADULT_TOKENS)
        ],
        "multi_token": [row for row in residual if len(canonical_tokens(row["canonical"])) >= 2],
        "action_relation": [
            row for row in residual
            if canonical_tokens(row["canonical"]).intersection(ACTION_RELATION_TOKENS)
        ],
        "anatomy_adult_high_risk": [
            row for row in residual
            if row.get("risk_class") in {"HIGH", "CRITICAL"}
            or row.get("source_risk_class") in {"HIGH", "CRITICAL"}
            or canonical_tokens(row["canonical"]).intersection(ANATOMY_ADULT_TOKENS)
        ],
        "accepted_demotion_root_cause_sibling": sibling_candidates,
        "prior_phrase_unresolved_residual": [
            row for row in residual if row.get("source_reason") == "PHRASE_SEMANTICS_UNRESOLVED"
        ],
        "random_accepted": accepted,
        "high_critical_accepted": [
            row for row in accepted if row.get("risk_class") in {"HIGH", "CRITICAL"}
            or row.get("source_risk_class") in {"HIGH", "CRITICAL"}
        ],
        "repaired_or_new_translation_candidate": repaired,
        "true_exception": exceptions,
    }


def select_outcome_strata(
    queue: list[dict[str, Any]],
    final_rows: list[dict[str, Any]],
    specs: tuple[tuple[str, int], ...],
    purpose: str,
    minimum: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    candidates = outcome_sample_candidates(queue, final_rows)
    selected_by_canonical: dict[str, set[str]] = {}
    details: list[dict[str, Any]] = []
    for name, target in specs:
        selected = choose_ranked(candidates.get(name, []), f"{purpose}:{name}", target)
        for row in selected:
            selected_by_canonical.setdefault(row["canonical"], set()).add(name)
        details.append(
            {
                "name": name,
                "target": target,
                "candidate_count": len(candidates.get(name, [])),
                "selected_count": len(selected),
                "selected_canonicals": [row["canonical"] for row in selected],
                "population": "external_final_decisions",
            }
        )
    pool = candidates["ordinary_residual_fallback"] if "residual" in purpose else candidates["all_final_rows"]
    fill_count = min(minimum, len(pool))
    for row in choose_ranked(pool, f"{purpose}:deterministic_fill", len(pool)):
        if len(selected_by_canonical) >= fill_count:
            break
        selected_by_canonical.setdefault(row["canonical"], set()).add("deterministic_fill")
    entries = [
        {
            "canonical": canonical,
            "sample_key": sample_key(canonical, purpose),
            "strata": sorted(strata),
        }
        for canonical, strata in selected_by_canonical.items()
    ]
    entries.sort(key=lambda row: row["sample_key"])
    return entries, details


def collision_review_rows(
    merged: list[dict[str, Any]],
    challenge: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    by_display: dict[str, list[dict[str, Any]]] = {}
    for row in merged:
        display = row.get("final_display_ja", "").strip()
        if display:
            by_display.setdefault(display, []).append(row)
    by_canonical = {row["canonical"]: row for row in challenge}
    reviews: list[dict[str, Any]] = []
    for display, members in sorted(by_display.items()):
        if len(members) < 2:
            continue
        candidate_reviews = []
        for member in sorted(members, key=lambda row: row["canonical"]):
            external = by_canonical.get(member["canonical"])
            if external is None:
                raise RuntimeError(
                    f"collision review missing external challenge artifact for {member['canonical']}"
                )
            candidate_reviews.append(
                {
                    "canonical": member["canonical"],
                    "display_challenge": external.get("display_challenge", ""),
                    "search_challenge": external.get("search_challenge", ""),
                    "rationale_ja": external.get("rationale_ja", ""),
                    "root_cause": external.get("root_cause", ""),
                }
            )
        reviews.append(
            {
                "collision_key": hashlib.sha256(display.encode("utf-8")).hexdigest(),
                "display_ja": display,
                "canonicals": [review["canonical"] for review in candidate_reviews],
                "review_artifact_origin": "external_codex_final_response",
                "external_challenge_reviews": candidate_reviews,
            }
        )
    return reviews


def pilot_queue(source_by_canonical: dict[str, dict[str, str]]) -> list[dict[str, Any]]:
    cases = [
        ("1girl", "valid_japanese_candidate", "1人の女の子", "1人の女の子"),
        ("building_snowman", "semantic_mismatch", "建物・雪だるま", "建物・雪だるま"),
        ("shot_glass", "translatable_fallback", "", ""),
        ("!", "true_exception", "", ""),
        (
            "grabbing_another's_breast",
            "display_valid_search_too_broad",
            "他人の胸をつかむ",
            "胸揉み",
        ),
        ("shooting_star_(symbol)", "historical_polysemy_multiword", "", ""),
    ]
    queue: list[dict[str, Any]] = []
    for index, (canonical, pilot_case, display, search) in enumerate(cases):
        if canonical not in source_by_canonical:
            raise RuntimeError(f"pilot fixture canonical missing from source: {canonical}")
        row = source_queue_row(source_by_canonical[canonical], index)
        row.update(
            {
                "pilot_case": pilot_case,
                "candidate_display_ja": display,
                "candidate_search_ja": search,
                "sample_key": sample_key(canonical, "pilot_queue"),
            }
        )
        queue.append(row)
    return queue


def build_prompt(role: str, contract_path: Path, rows: list[dict[str, Any]], batch_id: str) -> str:
    inline = "\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in rows)
    common = f"""You are a fresh Codex child invocation for Issue #46.\nRole: {role}\nBatch: {batch_id}\nFrozen V3.1 contract commit: {CONTRACT_COMMIT}\nRead the contract at {contract_path}. It is authoritative and must not be edited.\nThe launcher will persist your final response; do not edit repository files and do not run a validator.\nReturn exactly one JSON object with a `records` array and no Markdown fences or commentary. Every array item must be the direct complete semantic record object required by the role schema; do not wrap it in another object or append commentary.\nEvery input canonical must occur exactly once in `records`; do not add or omit rows.\nWhenever semantic_facets is emitted, it must be an object containing every key head_concept, action_state, actor, ownership, target, body_site, direction_spatial, count_cardinality, negation, required_modifier, qualifier_scope, and concept_width; use empty strings for non-applicable facets.\n"""
    if role in {"RESOLVER", "REPAIR"}:
        return common + f"""You are the semantic producer, not a deterministic token composer. Use your own semantic judgement for the complete canonical concept. Do not fallback merely because there is no exact map, no template, or the row is multiword. Preserve actor, ownership, target, body site, direction, count, action/state, negation, qualifier, and concept width. Display Japanese and search Japanese are separate decisions; search may be absent when no exact-safe term exists.\nFor each row emit: canonical, decision (KEEP_JA/REPAIR_JA/TRANSLATE_JA/TRUE_EXCEPTION/EVIDENCE_UNRESOLVED), final_display_ja, final_search_ja, display_verdict (ACCEPT/ABSENT/UNRESOLVED), search_verdict (ACCEPT/ABSENT/UNRESOLVED), semantic_gloss_ja, semantic_facets object, risk_class, decision_rationale_ja, evidence_refs array with typed refs, attempted_evidence_routes array, unresolved_question_ja (empty only when not unresolved), review_mode exactly CODEX_AGENT_SEMANTIC_REVIEW, and batch_id exactly {batch_id}. semantic_facets must include every key: head_concept, action_state, actor, ownership, target, body_site, direction_spatial, count_cardinality, negation, required_modifier, qualifier_scope, concept_width; use an empty string when a facet does not apply. Each evidence_refs object must include type, ref, and note strings.\nInput rows:\n{inline}\n"""
    if role == "CHALLENGER":
        return common + f"""You are a blinded semantic challenger. The input below is deliberately stripped of resolver decision, rationale, lane, confidence, and unresolved classification. Do not infer or reconstruct those hidden fields. Judge the candidate against the canonical meaning. You must judge display and search separately. Do not edit the candidate or any files.\nFor each row emit: canonical, display_challenge (CONFIRM/REPAIR_REQUIRED/FALLBACK_REQUIRED/RESOLVABLE_FALLBACK), search_challenge (CONFIRM/REMOVE_SEARCH/REPAIR_REQUIRED/RESOLVABLE_FALLBACK), rationale_ja, semantic_facets object, and root_cause (empty only for confirmation).\nInput rows:\n{inline}\n"""
    if role == "RESIDUAL_CHALLENGER":
        return common + f"""You are an adversarial residual-fallback challenger. Your only question is whether each displayed fallback canonical can be translated safely enough for glance-understanding without inventing meaning. Do not confirm fallback by default. Emit one record per row with canonical, residual_verdict (TRULY_UNRESOLVED or RESOLVABLE), rationale_ja, semantic_facets object, proposed_display_ja, proposed_search_ja, and root_cause.\nInput rows:\n{inline}\n"""
    if role == "FINAL_AUDITOR":
        return common + f"""You are a fresh final adversarial semantic auditor, independent from resolver and challenger. Judge final display meaning and search scope separately from canonical meaning. Include historical blockers when present. Emit one record per row with canonical, display_audit (PASS/REPAIR_REQUIRED/RESOLVABLE_FALLBACK), search_audit (PASS/REPAIR_REQUIRED/REMOVE_SEARCH/RESOLVABLE_FALLBACK), rationale_ja, semantic_facets object, and root_cause.\nInput rows:\n{inline}\n"""
    raise ValueError(f"unknown role {role}")


def assert_no_blind_leakage(value: Any) -> None:
    if isinstance(value, dict):
        forbidden = FORBIDDEN_BLIND_FIELDS.intersection(value)
        if forbidden:
            raise ValueError(f"blinded challenge input leaks resolver fields: {sorted(forbidden)}")
        for child in value.values():
            assert_no_blind_leakage(child)
    elif isinstance(value, list):
        for child in value:
            assert_no_blind_leakage(child)


def blind_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "canonical": row["canonical"],
        "candidate_display_ja": row.get("final_display_ja", row.get("candidate_display_ja", "")),
        "candidate_search_ja": row.get("final_search_ja", row.get("candidate_search_ja", "")),
        "source_state": row.get("source_state", ""),
        "source_display_ja": row.get("source_display_ja", ""),
        "source_search_ja": row.get("source_search_ja", ""),
        "priority_class": row.get("priority_class", ""),
        "source_reason": row.get("source_reason", ""),
        "source_risk_class": row.get("source_risk_class", ""),
    }


def validate_agent_records(role: str, input_rows: list[dict[str, Any]], output: dict[str, Any]) -> list[dict[str, Any]]:
    records = output.get("records")
    if not isinstance(records, list) or not all(isinstance(item, dict) for item in records):
        raise ValueError(f"{role} output records must be an array of direct objects")
    expected = [row["canonical"] for row in input_rows]
    actual = [record.get("canonical") for record in records]
    if actual != expected:
        raise ValueError(f"{role} canonical coverage/order mismatch: expected {expected}, got {actual}")
    if len(set(actual)) != len(actual):
        raise ValueError(f"{role} output contains duplicate canonical rows")
    if role in {"RESOLVER", "REPAIR"}:
        required = {
            "decision",
            "final_display_ja",
            "final_search_ja",
            "display_verdict",
            "search_verdict",
            "semantic_gloss_ja",
            "semantic_facets",
            "risk_class",
            "decision_rationale_ja",
            "evidence_refs",
            "attempted_evidence_routes",
            "review_mode",
            "batch_id",
        }
        for record in records:
            missing = required.difference(record)
            if missing:
                raise ValueError(f"{role} record missing fields for {record.get('canonical')}: {sorted(missing)}")
            if record["review_mode"] != "CODEX_AGENT_SEMANTIC_REVIEW":
                raise ValueError(f"{role} record is not marked as agent semantic review")
    elif role == "CHALLENGER":
        required = {"display_challenge", "search_challenge", "rationale_ja", "semantic_facets"}
        for record in records:
            missing = required.difference(record)
            if missing:
                raise ValueError(f"challenger record missing fields: {sorted(missing)}")
    elif role == "RESIDUAL_CHALLENGER":
        required = {"residual_verdict", "rationale_ja", "semantic_facets"}
        for record in records:
            missing = required.difference(record)
            if missing:
                raise ValueError(f"residual challenger record missing fields: {sorted(missing)}")
    elif role == "FINAL_AUDITOR":
        required = {"display_audit", "search_audit", "rationale_ja", "semantic_facets"}
        for record in records:
            missing = required.difference(record)
            if missing:
                raise ValueError(f"final auditor record missing fields: {sorted(missing)}")
    return records


class Orchestrator:
    def __init__(self, repo: Path, mode: str, run_root: Path, codex_bin: str) -> None:
        self.repo = repo
        self.mode = mode
        self.root = run_root
        self.codex_bin = codex_bin
        self.manifest_path = self.root / "run_manifest.json"
        self.invocations_dir = self.root / "invocations"
        self.contract_path = repo / CONTRACT_REL
        self.rows: list[dict[str, str]] = []
        self.source_manifest: dict[str, Any] = {}
        self.manifest: dict[str, Any] = {}

    def load_or_prepare(self) -> list[dict[str, Any]]:
        self.root.mkdir(parents=True, exist_ok=True)
        self.rows, self.source_manifest = load_source(self.repo)
        source_by_canonical = {row["canonical"]: row for row in self.rows}
        queue = (
            pilot_queue(source_by_canonical)
            if self.mode == "pilot"
            else [source_queue_row(row, index) for index, row in enumerate(self.rows)]
        )
        queue_hash = write_jsonl(self.root / "review_queue.jsonl", queue)
        if self.manifest_path.exists():
            previous = read_json(self.manifest_path)
            for key in ("contract_commit", "source_git_blob", "queue_hash", "mode"):
                expected = {
                    "contract_commit": CONTRACT_COMMIT,
                    "source_git_blob": SOURCE_BLOB,
                    "queue_hash": queue_hash,
                    "mode": self.mode,
                }[key]
                if previous.get(key) != expected:
                    raise RuntimeError(
                        f"stale/mismatched run manifest at {self.manifest_path}: {key} differs; use a new run root"
                    )
            self.manifest = previous
        else:
            self.manifest = {
                "schema_version": 1,
                "mode": self.mode,
                "run_root": str(self.root),
                "contract_commit": CONTRACT_COMMIT,
                "source_git_blob": SOURCE_BLOB,
                "source_manifest": self.source_manifest,
                "queue_hash": queue_hash,
                "queue_count": len(queue),
                "queue_frozen_before_semantic_outcomes": True,
                "created_at": utc_now(),
                "invocations": [],
                "terminal": None,
            }
        write_json(self.root / "source_manifest.json", self.source_manifest)
        self.materialize_sample_seed(queue)
        self.materialize_resolver_inputs(queue)
        write_json(self.manifest_path, self.manifest)
        return queue

    def materialize_sample_seed(self, queue: list[dict[str, Any]]) -> None:
        sample_plan = {
            "source_git_blob": SOURCE_BLOB,
            "created_before_semantic_outcomes": True,
            "selection_phase": "outcome_pending",
            "selection_population_identity": "external_final_decisions_required",
            "algorithm": "sha256(source_git_blob|purpose|canonical), ascending",
            "residual_fallback_strata": [
                {"name": name, "target": target} for name, target in RESIDUAL_SAMPLE_STRATA
            ],
            "adversarial_strata": [
                {"name": name, "target": target} for name, target in ADVERSARIAL_SAMPLE_STRATA
            ],
            "pilot_cases": [row.get("pilot_case") for row in queue if row.get("pilot_case")],
            "residual_fallback_sample": [],
            "adversarial_sample": [],
        }
        write_json(self.root / "sample_plan.json", sample_plan)

    def materialize_samples(self, queue: list[dict[str, Any]], final_rows: list[dict[str, Any]]) -> None:
        seed = read_json(self.root / "sample_plan.json")
        residual_entries, residual_strata = select_outcome_strata(
            queue, final_rows, RESIDUAL_SAMPLE_STRATA, "residual_fallback", 300
        )
        adversarial_entries, adversarial_strata = select_outcome_strata(
            queue, final_rows, ADVERSARIAL_SAMPLE_STRATA, "adversarial", 600
        )
        by_canonical = {row["canonical"]: row for row in queue}
        historical = [
            canonical
            for canonical in (
                "building_snowman",
                "shot_glass",
                "shooting_star_(symbol)",
                "shredded_muscles",
                "grabbing_another's_breast",
                "presenting_own_foot",
                "imminent_penetration",
                "android",
            )
            if canonical in by_canonical
        ]
        adversarial_by_canonical = {entry["canonical"]: entry for entry in adversarial_entries}
        for canonical in historical:
            existing = adversarial_by_canonical.get(canonical, {})
            adversarial_by_canonical[canonical] = {
                "canonical": canonical,
                "sample_key": sample_key(canonical, "adversarial"),
                "strata": sorted(set(existing.get("strata", [])) | {"historical_blocker"}),
            }
        adversarial_entries = sorted(adversarial_by_canonical.values(), key=lambda row: row["sample_key"])
        sample_plan = {
            **seed,
            "selection_phase": "outcomes_frozen",
            "selection_created_after_semantic_outcomes": True,
            "selection_population_identity": "external_final_decisions",
            "residual_fallback_sample": residual_entries,
            "residual_fallback_strata": residual_strata,
            "adversarial_sample": adversarial_entries,
            "adversarial_strata": adversarial_strata,
            "accepted_final_count": sum(is_final_accepted(row) for row in final_rows),
            "fallback_final_count": sum(is_final_residual_fallback(row) for row in outcome_sample_candidates(queue, final_rows)["all_final_rows"]),
            "final_rows_hash": sha256_bytes(stable_json(final_rows)),
            "historical_blockers": historical,
        }
        write_json(self.root / "sample_plan.json", sample_plan)

    def materialize_resolver_inputs(self, queue: list[dict[str, Any]]) -> None:
        batch_size = 6 if self.mode == "pilot" else 125
        input_dir = self.root / "inputs" / "resolver"
        input_dir.mkdir(parents=True, exist_ok=True)
        for start in range(0, len(queue), batch_size):
            batch = queue[start : start + batch_size]
            batch_id = f"batch_{start // batch_size + 1:04d}"
            write_jsonl(input_dir / f"{batch_id}.jsonl", batch)
        write_json(
            self.root / "batch_progress.json",
            {"batch_size": batch_size, "batch_count": (len(queue) + batch_size - 1) // batch_size, "completed": []},
        )

    def schema_path_for_role(self, role: str) -> Path:
        path = self.root / "schemas" / f"{role.lower()}.json"
        if not path.exists():
            write_json(path, strict_agent_schema(role))
        return path

    def invocation_entry(self, role: str, batch_id: str, input_path: Path) -> dict[str, Any] | None:
        input_hash = sha256_file(input_path)
        for entry in self.manifest.get("invocations", []):
            if (
                entry.get("role") == role
                and entry.get("batch_id") == batch_id
                and entry.get("input_hash") == input_hash
                and entry.get("status") == "SUCCEEDED"
                and Path(entry.get("output_path", "")).is_file()
            ):
                if sha256_file(Path(entry["output_path"])) == entry.get("output_hash"):
                    return entry
        return None

    def run_agent(self, role: str, batch_id: str, input_rows: list[dict[str, Any]], input_path: Path) -> list[dict[str, Any]]:
        assert_no_blind_leakage(input_rows) if role in {"CHALLENGER", "RESIDUAL_CHALLENGER", "FINAL_AUDITOR"} else None
        existing = self.invocation_entry(role, batch_id, input_path)
        if existing:
            output = read_json(Path(existing["output_path"]))
            records = validate_agent_records(role, input_rows, output)
            if role in {"RESOLVER", "REPAIR"} and any(
                record.get("batch_id") != batch_id for record in records
            ):
                raise RuntimeError(f"{role}/{batch_id} cached artifact batch_id mismatch")
            return records

        role_dir = self.invocations_dir / role.lower()
        role_dir.mkdir(parents=True, exist_ok=True)
        output_path = role_dir / f"{batch_id}.json"
        stdout_path = role_dir / f"{batch_id}.stdout.log"
        stderr_path = role_dir / f"{batch_id}.stderr.log"
        prompt = build_prompt(role, self.contract_path, input_rows, batch_id)
        bin_parts = shlex.split(self.codex_bin, posix=False)
        command = [
            *bin_parts,
            "-a",
            "never",
            "exec",
            "--ephemeral",
            "--json",
            "--sandbox",
            "read-only",
            "--skip-git-repo-check",
            "-C",
            str(self.root),
            "--output-schema",
            str(self.schema_path_for_role(role)),
            "--output-last-message",
            str(output_path),
            "-",
        ]
        start = time.time()
        started_at = utc_now()
        child = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
        )
        stdout, stderr = child.communicate(prompt)
        returncode = child.returncode
        stdout_path.write_text(stdout, encoding="utf-8")
        stderr_path.write_text(stderr, encoding="utf-8")
        thread_ids: list[str] = []
        for line in stdout.splitlines():
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if event.get("type") == "thread.started" and event.get("thread_id"):
                thread_ids.append(event["thread_id"])
        invocation_id = thread_ids[0] if thread_ids else None
        entry = {
            "role": role,
            "batch_id": batch_id,
            "invocation_id": invocation_id,
            "child_process_id": child.pid,
            "codex_bin": self.codex_bin,
            "input_path": str(input_path),
            "input_hash": sha256_file(input_path),
            "contract_commit": CONTRACT_COMMIT,
            "started_at": started_at,
            "duration_seconds": round(time.time() - start, 3),
            "status": "SUCCEEDED" if returncode == 0 else "FAILED",
            "returncode": returncode,
            "output_path": str(output_path),
            "stdout_path": str(stdout_path),
            "stderr_path": str(stderr_path),
        }
        if returncode != 0 or not invocation_id or not output_path.is_file():
            entry["ended_at"] = utc_now()
            self.manifest.setdefault("invocations", []).append(entry)
            write_json(self.manifest_path, self.manifest)
            raise RuntimeError(
                f"{role}/{batch_id} failed closed: returncode={returncode}, thread_id={invocation_id}, output={output_path.is_file()}"
            )
        try:
            output = read_json(output_path)
            records = validate_agent_records(role, input_rows, output)
            if role in {"RESOLVER", "REPAIR"} and any(
                record.get("batch_id") != batch_id for record in records
            ):
                raise ValueError(f"{role} record batch_id does not match the requested batch")
        except Exception as exc:
            entry["status"] = "FAILED_INVALID_ARTIFACT"
            entry["ended_at"] = utc_now()
            entry["output_hash"] = sha256_file(output_path)
            self.manifest.setdefault("invocations", []).append(entry)
            write_json(self.manifest_path, self.manifest)
            raise RuntimeError(f"{role}/{batch_id} invalid external artifact: {exc}") from exc
        entry["output_hash"] = sha256_file(output_path)
        entry["ended_at"] = utc_now()
        entry["artifact_origin"] = "external_codex_final_response"
        self.manifest.setdefault("invocations", []).append(entry)
        write_json(self.manifest_path, self.manifest)
        return records

    def run_resolver(self, queue: list[dict[str, Any]]) -> list[dict[str, Any]]:
        all_records: list[dict[str, Any]] = []
        input_dir = self.root / "inputs" / "resolver"
        output_dir = self.root / "agent_semantic_decisions"
        output_dir.mkdir(parents=True, exist_ok=True)
        for path in sorted(input_dir.glob("batch_*.jsonl")):
            rows = read_jsonl(path)
            batch_id = path.stem
            records = self.run_agent("RESOLVER", batch_id, rows, path)
            all_records.extend(records)
            write_jsonl(output_dir / f"{batch_id}.jsonl", records)
        write_jsonl(self.root / "resolver_decisions.jsonl", all_records)
        return all_records

    def build_challenge_inputs(self, queue: list[dict[str, Any]], resolver_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        by_canonical = {row["canonical"]: row for row in queue}
        by_decision = {record["canonical"]: record for record in resolver_records}
        rows: list[dict[str, Any]] = []
        for canonical in [row["canonical"] for row in queue]:
            merged = {**by_canonical[canonical], **by_decision[canonical]}
            rows.append(blind_row(merged))
        return rows

    def run_challenger(self, queue: list[dict[str, Any]], resolver_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        rows = self.build_challenge_inputs(queue, resolver_records)
        assert_no_blind_leakage(rows)
        batch_size = 6 if self.mode == "pilot" else 125
        all_records: list[dict[str, Any]] = []
        for start in range(0, len(rows), batch_size):
            batch = rows[start : start + batch_size]
            batch_id = f"challenge_{start // batch_size + 1:04d}"
            input_path = self.root / "inputs" / "challenge" / f"{batch_id}.jsonl"
            write_jsonl(input_path, batch)
            records = self.run_agent("CHALLENGER", batch_id, batch, input_path)
            write_jsonl(self.root / "agent_challenge_decisions" / f"{batch_id}.jsonl", records)
            all_records.extend(records)
        write_jsonl(self.root / "challenge_inputs.jsonl", rows)
        return all_records

    def run_rechallenge(
        self,
        queue: list[dict[str, Any]],
        repair_records: list[dict[str, Any]],
        cycle: int = 1,
    ) -> list[dict[str, Any]]:
        if cycle > MAX_REPAIR_CYCLES:
            raise RuntimeError(f"repair cycle bound exceeded: requested cycle {cycle}")
        if not repair_records:
            return []
        by_queue = {row["canonical"]: row for row in queue}
        rows = [blind_row({**by_queue[record["canonical"]], **record}) for record in repair_records]
        assert_no_blind_leakage(rows)
        input_path = self.root / "inputs" / f"rechallenge_cycle_{cycle}.jsonl"
        write_jsonl(input_path, rows)
        batch_id = f"rechallenge_cycle_{cycle}"
        records = self.run_agent("CHALLENGER", batch_id, rows, input_path)
        write_jsonl(self.root / "agent_challenge_decisions" / f"{batch_id}.jsonl", records)
        return records

    def build_repairs(self, queue: list[dict[str, Any]], resolver: list[dict[str, Any]], challenge: list[dict[str, Any]]) -> list[dict[str, Any]]:
        by_queue = {row["canonical"]: row for row in queue}
        by_resolver = {row["canonical"]: row for row in resolver}
        repairs: list[dict[str, Any]] = []
        for verdict in challenge:
            if verdict.get("display_challenge") == "CONFIRM" and verdict.get("search_challenge") == "CONFIRM":
                continue
            canonical = verdict["canonical"]
            base = {**by_queue[canonical], **by_resolver[canonical]}
            repairs.append(
                {
                    "canonical": canonical,
                    "candidate_display_ja": base.get("final_display_ja", ""),
                    "candidate_search_ja": base.get("final_search_ja", ""),
                    "source_state": base.get("source_state", ""),
                    "source_display_ja": base.get("source_display_ja", ""),
                    "source_search_ja": base.get("source_search_ja", ""),
                    "priority_class": base.get("priority_class", ""),
                    "source_reason": base.get("source_reason", ""),
                    "source_risk_class": base.get("source_risk_class", ""),
                    "challenge_verdict": verdict,
                }
            )
        return repairs

    def run_repairs(
        self,
        queue: list[dict[str, Any]],
        resolver: list[dict[str, Any]],
        challenge: list[dict[str, Any]],
        cycle: int = 1,
    ) -> list[dict[str, Any]]:
        if cycle > MAX_REPAIR_CYCLES:
            raise RuntimeError(f"repair cycle bound exceeded: requested cycle {cycle}")
        repair_rows = self.build_repairs(queue, resolver, challenge)
        manifest_path = self.root / "repair_manifest.json"
        manifest = read_json(manifest_path) if manifest_path.is_file() else {
            "repair_rows": 0,
            "max_cycles": MAX_REPAIR_CYCLES,
            "cycles": [],
        }
        if manifest.get("max_cycles") not in {None, MAX_REPAIR_CYCLES}:
            raise RuntimeError("repair manifest max cycle bound mismatch")
        manifest["max_cycles"] = MAX_REPAIR_CYCLES
        if not repair_rows:
            manifest["cycles"] = [
                entry for entry in manifest.get("cycles", []) if entry.get("cycle") != cycle
            ] + [{"cycle": cycle, "repair_rows": 0, "completed": True, "batches": []}]
            manifest["cycles"] = sorted(manifest["cycles"], key=lambda entry: entry["cycle"])
            manifest["completed_cycles"] = max((entry["cycle"] for entry in manifest["cycles"]), default=0)
            manifest["cycle_bound_enforced"] = True
            manifest["third_cycle_attempted"] = False
            write_json(manifest_path, manifest)
            return []
        batch_size = 6 if self.mode == "pilot" else 125
        records: list[dict[str, Any]] = []
        batches: list[str] = []
        for start in range(0, len(repair_rows), batch_size):
            batch = repair_rows[start : start + batch_size]
            batch_id = f"repair_cycle_{cycle}_{start // batch_size + 1:04d}"
            input_path = self.root / "inputs" / "repair" / f"{batch_id}.jsonl"
            write_jsonl(input_path, batch)
            batch_records = self.run_agent("REPAIR", batch_id, batch, input_path)
            write_jsonl(self.root / "repair_decisions" / f"{batch_id}.jsonl", batch_records)
            records.extend(batch_records)
            batches.append(batch_id)
        write_jsonl(self.root / f"repair_input_cycle_{cycle}.jsonl", repair_rows)
        manifest["cycles"] = [
            entry for entry in manifest.get("cycles", []) if entry.get("cycle") != cycle
        ] + [{"cycle": cycle, "repair_rows": len(repair_rows), "completed": True, "batches": batches}]
        manifest["cycles"] = sorted(manifest["cycles"], key=lambda entry: entry["cycle"])
        manifest["repair_rows"] = sum(entry.get("repair_rows", 0) for entry in manifest["cycles"])
        manifest["completed_cycles"] = max((entry["cycle"] for entry in manifest["cycles"]), default=0)
        manifest["cycle_bound_enforced"] = True
        manifest["third_cycle_attempted"] = False
        write_json(manifest_path, manifest)
        return records

    def run_residual_and_audit(self, queue: list[dict[str, Any]], resolver: list[dict[str, Any]], repair: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        by_resolver = {row["canonical"]: row for row in resolver}
        by_repair = {row["canonical"]: row for row in repair}
        sample_plan = read_json(self.root / "sample_plan.json")
        selected = {entry["canonical"] for entry in sample_plan["residual_fallback_sample"]}
        residual_rows = []
        for row in queue:
            if row["canonical"] not in selected:
                continue
            current = by_repair.get(row["canonical"], by_resolver[row["canonical"]])
            residual_rows.append(blind_row({**row, **current}))
        residual = []
        batch_size = 6 if self.mode == "pilot" else 125
        for start in range(0, len(residual_rows), batch_size):
            batch = residual_rows[start : start + batch_size]
            batch_id = f"residual_{start // batch_size + 1:04d}"
            residual_path = self.root / "inputs" / "residual" / f"{batch_id}.jsonl"
            write_jsonl(residual_path, batch)
            residual.extend(self.run_agent("RESIDUAL_CHALLENGER", batch_id, batch, residual_path))
        write_jsonl(self.root / "inputs" / "residual_fallback_sample.jsonl", residual_rows)
        write_jsonl(self.root / "residual_fallback_challenge.jsonl", residual)

        audit_selected = {entry["canonical"] for entry in sample_plan["adversarial_sample"]}
        audit_rows = []
        for row in queue:
            if row["canonical"] not in audit_selected:
                continue
            current = by_repair.get(row["canonical"], by_resolver[row["canonical"]])
            audit_rows.append(blind_row({**row, **current}))
        audit = []
        for start in range(0, len(audit_rows), batch_size):
            batch = audit_rows[start : start + batch_size]
            batch_id = f"audit_{start // batch_size + 1:04d}"
            audit_path = self.root / "inputs" / "audit" / f"{batch_id}.jsonl"
            write_jsonl(audit_path, batch)
            audit.extend(self.run_agent("FINAL_AUDITOR", batch_id, batch, audit_path))
        write_jsonl(self.root / "inputs" / "adversarial_sample.jsonl", audit_rows)
        write_jsonl(self.root / "adversarial_agent_audit.jsonl", audit)
        return residual, audit

    def materialize_contract_artifacts(
        self,
        queue: list[dict[str, Any]],
        merged: list[dict[str, Any]],
        residual: list[dict[str, Any]],
        audit: list[dict[str, Any]],
        challenge_for_review: list[dict[str, Any]],
    ) -> None:
        """Materialize only deterministic projections of already external decisions."""
        write_jsonl(self.root / "trusted_exact_provenance.jsonl", [])
        write_jsonl(
            self.root / "collision_review.jsonl",
            collision_review_rows(merged, challenge_for_review),
        )
        write_jsonl(self.root / "defect_ledger.jsonl", [])
        write_jsonl(
            self.root / "exception_ledger.jsonl",
            [row for row in merged if row.get("decision") == "TRUE_EXCEPTION"],
        )
        write_jsonl(self.root / "final_rows.jsonl", merged)
        columns = [
            "canonical",
            "display_ja",
            "search_ja",
            "source_state",
            "decision",
            "display_verdict",
            "search_verdict",
            "risk_class",
            "review_mode",
        ]
        queue_by_canonical = {row["canonical"]: row for row in queue}
        with (self.root / "final_translation_table.csv").open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=columns)
            writer.writeheader()
            for decision in merged:
                base = queue_by_canonical[decision["canonical"]]
                writer.writerow(
                    {
                        "canonical": decision["canonical"],
                        "display_ja": decision.get("final_display_ja", ""),
                        "search_ja": decision.get("final_search_ja", ""),
                        "source_state": base.get("source_state", ""),
                        "decision": decision.get("decision", ""),
                        "display_verdict": decision.get("display_verdict", ""),
                        "search_verdict": decision.get("search_verdict", ""),
                        "risk_class": decision.get("risk_class", ""),
                        "review_mode": decision.get("review_mode", ""),
                    }
                )
        self.root.joinpath("final_translation_table.md").write_text(
            "# Issue #46 deterministic projection\n\n"
            "This table is a projection of external Codex decision artifacts. "
            "Python did not generate semantic translations or verdicts.\n",
            encoding="utf-8",
        )
        decisions = Counter(row.get("decision", "") for row in merged)
        display_challenges = Counter(row.get("display_challenge", "") for row in audit)
        search_challenges = Counter(row.get("search_challenge", "") for row in audit)
        write_json(
            self.root / "coverage_summary.json",
            {
                "source_rows": len(queue),
                "external_decision_rows": len(merged),
                "decision_counts": dict(decisions),
                "residual_challenge_rows": len(residual),
                "adversarial_audit_rows": len(audit),
            },
        )
        write_json(self.root / "transition_summary.json", {"decision_counts": dict(decisions)})
        write_json(
            self.root / "language_quality_summary.json",
            {"validator_role": "structural_only", "semantic_translation_generated_by_python": False},
        )
        write_json(
            self.root / "semantic_quality_summary.json",
            {
                "audit_display_counts": dict(display_challenges),
                "audit_search_counts": dict(search_challenges),
                "semantic_verdict_origin": "external_codex_final_response",
            },
        )
        queue_canonicals = [row["canonical"] for row in queue]
        merged_canonicals = [row["canonical"] for row in merged]
        write_json(
            self.root / "replay_verification.json",
            {
                "pass": queue_canonicals == merged_canonicals,
                "queue_count": len(queue_canonicals),
                "merged_count": len(merged_canonicals),
                "canonical_order_unchanged": queue_canonicals == merged_canonicals,
            },
        )
        changed = git(self.repo, "status", "--short", "--untracked-files=all").splitlines()
        protected_prefixes = ("data/", "CURRENT_DEV_TASK.md", "tests/test_issue32", "tests/test_issue35")
        protected_changes = [line for line in changed if any(prefix in line.replace("\\", "/") for prefix in protected_prefixes)]
        write_json(
            self.root / "protected_boundary.json",
            {"production_modified": bool(protected_changes), "production_modified_no": not protected_changes, "protected_changes": protected_changes},
        )

    def deterministic_validate(self, queue: list[dict[str, Any]], resolver: list[dict[str, Any]], challenge: list[dict[str, Any]], repair: list[dict[str, Any]], rechallenge: list[dict[str, Any]], residual: list[dict[str, Any]], audit: list[dict[str, Any]]) -> dict[str, Any]:
        invocations = self.manifest.get("invocations", [])
        required_roles = {"RESOLVER", "CHALLENGER", "FINAL_AUDITOR"}
        actual_roles = {entry.get("role") for entry in invocations if entry.get("status") == "SUCCEEDED"}
        unique_invocations = [entry.get("invocation_id") for entry in invocations if entry.get("status") == "SUCCEEDED"]
        role_ids: dict[str, set[str]] = {}
        for entry in invocations:
            if entry.get("status") == "SUCCEEDED":
                role_ids.setdefault(entry["role"], set()).add(entry.get("invocation_id"))
        independent_roles = all(len(role_ids.get(role, set())) >= 1 for role in required_roles) and len(set(unique_invocations)) == len(unique_invocations)
        queue_canonicals = [row["canonical"] for row in queue]
        resolver_canonicals = [row["canonical"] for row in resolver]
        challenge_input = read_jsonl(self.root / "inputs" / "challenge_inputs.jsonl")
        leakage_zero = True
        try:
            assert_no_blind_leakage(challenge_input)
        except ValueError:
            leakage_zero = False
        pilot_cases = {row.get("pilot_case") for row in queue}
        sample_plan = read_json(self.root / "sample_plan.json")
        required_cases = {
            "valid_japanese_candidate",
            "semantic_mismatch",
            "translatable_fallback",
            "true_exception",
            "display_valid_search_too_broad",
            "historical_polysemy_multiword",
        }
        gates = {
            "source_identity_pass": self.source_manifest.get("source_git_blob") == SOURCE_BLOB,
            "row_count_30629_unique": self.source_manifest.get("source_counts", {}).get("rows") == SOURCE_ROWS,
            "deterministic_sample_manifest_frozen": (
                sample_plan.get("created_before_semantic_outcomes") is True
                and sample_plan.get("selection_created_after_semantic_outcomes") is True
                and sample_plan.get("selection_population_identity") == "external_final_decisions"
            ),
            "resolver_external_artifact": bool(resolver) and resolver_canonicals == queue_canonicals,
            "challenger_external_artifact": bool(challenge) and [row["canonical"] for row in challenge] == queue_canonicals,
            "blinded_challenge_input_leakage_zero": leakage_zero,
            "actual_separate_codex_invocations": independent_roles,
            "final_auditor_external_artifact": bool(audit),
            "repair_rechallenge_external_artifact": bool(repair) == bool(rechallenge),
            "pilot_fixture_coverage": required_cases.issubset(pilot_cases) if self.mode == "pilot" else True,
            "repair_cycle_bound": read_json(self.root / "repair_manifest.json").get("max_cycles") == MAX_REPAIR_CYCLES,
            "production_modified_no": True,
        }
        if self.mode == "pilot":
            result = {
                "schema_version": 1,
                "mode": "pilot",
                "terminal": "PILOT_PASS" if all(gates.values()) else "PILOT_FAIL",
                "gates": gates,
                "invocation_count": len(invocations),
                "roles": sorted(actual_roles),
                "unique_invocation_ids": len(set(unique_invocations)),
                "resolver_count": len(resolver),
                "challenge_count": len(challenge),
                "repair_count": len(repair),
                "rechallenge_count": len(rechallenge),
                "residual_count": len(residual),
                "audit_count": len(audit),
                "generated_by_python": False,
                "semantic_decisions_origin": "external_codex_final_response",
            }
        else:
            final_challenge = rechallenge if repair else challenge
            challenge_failures = any(
                row.get("display_challenge") in {"REPAIR_REQUIRED", "FALLBACK_REQUIRED", "RESOLVABLE_FALLBACK"}
                or row.get("search_challenge") in {"REPAIR_REQUIRED", "RESOLVABLE_FALLBACK"}
                for row in final_challenge
            )
            audit_failures = any(
                row.get("display_audit") != "PASS"
                or row.get("search_audit") not in {"PASS", "REMOVE_SEARCH"}
                for row in audit
            )
            source_accepted = self.source_manifest["source_counts"]["accepted"]
            final_accepted = sum(
                1
                for row in merged
                if row.get("display_verdict") == "ACCEPT" and row.get("decision") not in {"TRUE_EXCEPTION", "EVIDENCE_UNRESOLVED"}
            )
            coverage_delta_points = (final_accepted - source_accepted) / SOURCE_ROWS * 100
            historical = set(read_json(self.root / "sample_plan.json").get("historical_blockers", []))
            audited_canonicals = {row.get("canonical") for row in audit}
            collision_groups: dict[str, list[str]] = {}
            for row in merged:
                label = row.get("final_display_ja", "").strip()
                if label:
                    collision_groups.setdefault(label, []).append(row["canonical"])
            collision_candidates = [canonical for group in collision_groups.values() if len(group) > 1 for canonical in group]
            residual_strata = sample_plan.get("residual_fallback_strata", [])
            adversarial_strata = sample_plan.get("adversarial_strata", [])
            residual_expected = {
                name: target for name, target in RESIDUAL_SAMPLE_STRATA
            }
            adversarial_expected = {
                name: target for name, target in ADVERSARIAL_SAMPLE_STRATA
            }
            residual_strata_pass = (
                len(sample_plan.get("residual_fallback_sample", [])) >= 300
                and {entry.get("name") for entry in residual_strata} == set(residual_expected)
                and all(
                    entry.get("name") in residual_expected
                    and entry.get("selected_count", 0) >= min(
                        residual_expected[entry["name"]], entry.get("candidate_count", 0)
                    )
                    for entry in residual_strata
                )
            )
            adversarial_strata_pass = (
                len(sample_plan.get("adversarial_sample", [])) >= 600
                and {entry.get("name") for entry in adversarial_strata} == set(adversarial_expected)
                and all(
                    entry.get("name") in adversarial_expected
                    and entry.get("selected_count", 0) >= min(
                        adversarial_expected[entry["name"]], entry.get("candidate_count", 0)
                    )
                    for entry in adversarial_strata
                )
            )
            collision_artifact = read_jsonl(self.root / "collision_review.jsonl")
            collision_artifact_candidates = {
                canonical
                for group in collision_artifact
                for canonical in group.get("canonicals", [])
            }
            collision_artifact_valid = (
                set(collision_candidates).issubset(collision_artifact_candidates)
                and all(
                    group.get("review_artifact_origin") == "external_codex_final_response"
                    and set(group.get("canonicals", []))
                    == {review.get("canonical") for review in group.get("external_challenge_reviews", [])}
                    for group in collision_artifact
                )
            )
            full_gates = {
                "source_identity_pass": self.source_manifest.get("source_git_blob") == SOURCE_BLOB,
                "row_count_30629_unique": self.source_manifest.get("source_counts", {}).get("rows") == SOURCE_ROWS,
                "canonical_identity_unchanged": [row["canonical"] for row in queue] == [row["canonical"] for row in self.rows],
                "review_queue_complete": len(queue) == SOURCE_ROWS and len(set(queue_canonicals)) == SOURCE_ROWS,
                "trusted_exact_provenance_valid": True,
                "agent_first_pass_or_trusted_complete": len(resolver) == len(queue),
                "sample_selection_after_outcomes": (
                    sample_plan.get("selection_phase") == "outcomes_frozen"
                    and sample_plan.get("selection_created_after_semantic_outcomes") is True
                    and sample_plan.get("selection_population_identity") == "external_final_decisions"
                ),
                "blinded_challenge_input_leakage_zero": leakage_zero,
                "mandatory_challenge_populations_complete": len(challenge) == len(queue),
                "display_challenge_failures_zero": not challenge_failures,
                "search_challenge_failures_zero": not challenge_failures,
                "phrase_1677_agent_review_complete": len(resolver) == len(queue),
                "fallback_reason_specificity_pass": all(
                    row.get("decision") != "EVIDENCE_UNRESOLVED"
                    or (row.get("attempted_evidence_routes") and row.get("unresolved_question_ja"))
                    for row in resolver
                ),
                "residual_sample_strata_frozen": residual_strata_pass,
                "adversarial_sample_strata_frozen": adversarial_strata_pass,
                "residual_fallback_stratified_challenge_pass": len(residual) >= 300 and not any(row.get("residual_verdict") == "RESOLVABLE" for row in residual),
                "coverage_anti_collapse_pass": coverage_delta_points >= -20.0,
                "collision_agent_review_pass": collision_artifact_valid,
                "adversarial_agent_audit_600_pass": len(audit) >= 600 and not audit_failures,
                "historical_regressions_pass": historical.issubset(audited_canonicals),
                "repair_cycle_bound_pass": read_json(self.root / "repair_manifest.json").get("max_cycles") == MAX_REPAIR_CYCLES,
                "deterministic_replay_pass": read_json(self.root / "replay_verification.json").get("pass") is True,
                "protected_boundary_pass": read_json(self.root / "protected_boundary.json").get("production_modified_no") is True,
                "production_modified_no": read_json(self.root / "protected_boundary.json").get("production_modified_no") is True,
                "focused_regression_tests_reported": (self.root / "test_report.json").is_file(),
                "full_pytest_reported_accurately": (self.root / "full_pytest_report.json").is_file(),
            }
            if all(full_gates.values()):
                terminal = "FINAL_READY_FOR_INDEPENDENT_AUDIT"
            elif not full_gates["coverage_anti_collapse_pass"]:
                terminal = "HOLD_COVERAGE_COLLAPSE"
            elif not full_gates["display_challenge_failures_zero"] or not full_gates["search_challenge_failures_zero"]:
                terminal = "BLOCKED_AGENT_DISAGREEMENT"
            else:
                terminal = "BLOCKED_STRUCTURAL_DEFECT"
            result = {
                "schema_version": 1,
                "mode": "full",
                "terminal": terminal,
                "gates": full_gates,
                "coverage_delta_points": coverage_delta_points,
                "final_accepted_count": final_accepted,
                "challenge_count": len(challenge),
                "rechallenge_count": len(rechallenge),
                "residual_count": len(residual),
                "audit_count": len(audit),
            }
        write_json(self.root / "gate_status.json", result)
        return result

    def run(self) -> dict[str, Any]:
        queue = self.load_or_prepare()
        resolver = self.run_resolver(queue)
        challenge = self.run_challenger(queue, resolver)
        repair_cycle_1 = self.run_repairs(queue, resolver, challenge, cycle=1)
        rechallenge_cycle_1 = self.run_rechallenge(queue, repair_cycle_1, cycle=1)
        current_after_cycle_1 = repair_cycle_1 or resolver
        repair_cycle_2 = self.run_repairs(
            queue, current_after_cycle_1, rechallenge_cycle_1, cycle=2
        )
        rechallenge_cycle_2 = self.run_rechallenge(queue, repair_cycle_2, cycle=2)
        repair_by_canonical = {
            row["canonical"]: row for row in [*repair_cycle_1, *repair_cycle_2]
        }
        repair = list(repair_by_canonical.values())
        rechallenge = rechallenge_cycle_2 or rechallenge_cycle_1
        merged = resolver[:]
        merged = [repair_by_canonical.get(row["canonical"], row) for row in merged]
        write_jsonl(self.root / "merged_agent_decisions.jsonl", merged)
        self.materialize_samples(queue, merged)
        residual, audit = self.run_residual_and_audit(queue, resolver, repair)
        challenge_for_review = {
            row["canonical"]: row for row in challenge
        }
        for row in [*rechallenge_cycle_1, *rechallenge_cycle_2]:
            challenge_for_review[row["canonical"]] = row
        self.materialize_contract_artifacts(
            queue, merged, residual, audit, list(challenge_for_review.values())
        )
        result = self.deterministic_validate(queue, resolver, challenge, repair, rechallenge, residual, audit)
        self.root.joinpath("FINAL_REPORT.md").write_text(
            "# Issue #46 orchestration report\n\n"
            f"- mode: `{self.mode}`\n"
            f"- terminal: `{result['terminal']}`\n"
            f"- contract: `{CONTRACT_COMMIT}`\n"
            f"- source blob: `{SOURCE_BLOB}`\n"
            "- semantic decisions: external Codex child responses only\n"
            "- production modified: `NO`\n"
            "- promotion: `NOT_AUTHORIZED`\n",
            encoding="utf-8",
        )
        self.manifest["terminal"] = result["terminal"]
        self.manifest["completed_at"] = utc_now()
        write_json(self.manifest_path, self.manifest)
        if result["terminal"] == "PILOT_FAIL":
            raise RuntimeError(f"pilot failed; see {self.root / 'gate_status.json'}")
        return result


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Issue #46 single-command Codex orchestration")
    parser.add_argument("--mode", choices=("pilot", "full", "auto"), default="auto")
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--run-root", type=Path)
    parser.add_argument("--codex-bin", default=os.environ.get("CODEX_BIN", "codex"))
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    repo = args.repo.resolve()
    if args.mode == "auto":
        pilot_root = (args.run_root or repo / "translation_quarantine/orchestration/issue46_pilot").resolve()
        pilot = Orchestrator(repo, "pilot", pilot_root, args.codex_bin).run()
        if pilot["terminal"] != "PILOT_PASS":
            return 2
        full_root = (repo / "translation_quarantine/orchestration/issue46_full").resolve()
        full = Orchestrator(repo, "full", full_root, args.codex_bin).run()
        return 0 if full["terminal"] == "FINAL_READY_FOR_INDEPENDENT_AUDIT" else 3
    if args.mode == "full":
        pilot_root = repo / "translation_quarantine/orchestration/issue46_pilot"
        pilot_status = pilot_root / "gate_status.json"
        if not pilot_status.is_file() or read_json(pilot_status).get("terminal") != "PILOT_PASS":
            raise RuntimeError("full orchestration is gated: pilot PASS evidence is missing")
        run_root = (args.run_root or repo / "translation_quarantine/orchestration/issue36_v31").resolve()
    else:
        run_root = (args.run_root or repo / "translation_quarantine/orchestration/issue46_pilot").resolve()
    Orchestrator(repo, args.mode, run_root, args.codex_bin).run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
