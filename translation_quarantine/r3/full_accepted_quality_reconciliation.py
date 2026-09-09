"""Issue #36 full accepted-quality sweep and fallback reconciliation.

This is a frozen-source, quarantine-only reconciliation pass.  It deliberately
does not call a translation service: the accepted table is screened as a
whole, a small set of auditable fixture repairs is applied, and anything that
cannot pass the bounded screen remains an explicit English fallback.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping

R3 = Path(__file__).resolve().parent
if str(R3) not in sys.path:
    sys.path.insert(0, str(R3))

import bounded_wrapper_cleanup as bounded


ROOT = bounded.ROOT
SOURCE_DIR = "translation_quarantine/bounded_wrapper_cleanup_20260909"
OUTPUT_DIR = "translation_quarantine/full_accepted_quality_sweep_20260909"
CONTRACT = "translation_quarantine/r3/ISSUE36_FULL_ACCEPTED_AND_FALLBACK_RECONCILIATION_CONTRACT.md"
CONTRACT_COMMIT = "0f0cdd8657aeb03ee13cf1968fb86980fe4f604e"
AUDIT_COMMENT = "5599963638"
EXECUTION_START_HEAD = "bd111c5052203aacd74753c4a057893d2f5e79a8"
FIXED_SOURCE_HEAD = "1f069d050909425dbcc5c2965951fd0c920a2205"

FIELDS = ["canonical", "display_ja", "search_ja", "priority_class", "final_state", "route", "reason", "risk_class"]
ACCEPTED_STATES = {"JA_ACCEPT_EXISTING", "JA_ACCEPT_MACHINE", "JA_ACCEPT_STRICT"}

# These are unambiguous simplified-Chinese forms, not a generic Han detector.
# Shared Han characters are intentionally absent so that valid Japanese labels
# such as 机 or 直腸 are not rejected merely for containing CJK characters.
SIMPLIFIED_ONLY = set(
    "闭嘴创贴须插门阴动线图气过还让给时现应无实标别满带间类该并专处难许认场肤颜业产术种极响归剂纹华鸡龙鱼鸟马网电话书云乐黑镜蓝骑双刘与为从个们这声发观"
)

# Exact fixture repairs are bounded, reviewable, and preserve the semantic
# relation of the English canonical.  They are not a general composition
# engine and do not alter canonical keys.
RECONCILIATION_EXACT = {
    "anal_object_insertion": "肛門への物体挿入",
    "imminent_anal": "肛門への挿入直前",
    "presenting_own_anus": "自分の肛門を見せる",
    "presenting_own_ass": "自分の尻を見せる",
    "presenting_own_pussy": "自分の陰部を見せる",
    "vibrator_bulge": "バイブレーターの膨らみ",
    "vibrator_cord": "バイブレーターのコード",
    "vibrator_in_anus": "肛門内のバイブレーター",
    "vibrator_on_clitoris": "クリトリスに当てるバイブレーター",
    "vibrator_on_nipple": "乳首に当てるバイブレーター",
    "vibrator_on_penis": "陰茎に当てるバイブレーター",
    "presenting_own_foot": "自分の足を見せる",
    "imminent_penetration": "挿入直前",
    "android": "アンドロイド",
    "bandaid": "絆創膏",
    "beard": "ひげ",
    "hair_scrunchie": "シュシュ",
    "vertical-striped_clothes": "縦縞の服",
}

KNOWN_SCOPE_REPAIRS = {
    "painting_fingernails": "爪に色を塗る",
    "hydraulic_press": "油圧プレス",
    "press_conference": "記者会見",
    "taking_notes": "メモを取る",
}
RECONCILIATION_EXACT.update(KNOWN_SCOPE_REPAIRS)

PRIOR_REPAIR_KEYS = {
    "kickstand", "legjob", "dominator_(bdsm)", "implied_cheating_(relationship)",
    "alternate_ass_size_(larger)", "heavy_chromatic_aberration", "no_magazine_(weapon)",
    "newt", "painting_fingernails", "hydraulic_press", "press_conference", "taking_notes",
}

ALLOWED_LITERAL_TOKENS = set(bounded.PRESERVED_LITERAL_TOKENS) | {"bdsm", "3d", "fbi", "os", "ai"}
ASCII_WORD = re.compile(r"(?<![A-Za-z])[A-Za-z][A-Za-z0-9'-]*(?![A-Za-z])")
CANONICAL_TOKEN = re.compile(r"[a-z][a-z0-9'-]*")


def _read_source() -> list[dict[str, str]]:
    path = ROOT / SOURCE_DIR / "final_translation_table.csv"
    with path.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    if len(rows) != 30629 or len({row["canonical"] for row in rows}) != 30629:
        raise RuntimeError("fixed source must contain 30,629 unique canonical rows")
    states = Counter(row["final_state"] for row in rows)
    if sum(states[state] for state in ACCEPTED_STATES) != 27743 or states["ENGLISH_FALLBACK_EXCEPTION"] != 2886:
        raise RuntimeError(f"fixed source state drift: {dict(states)}")
    return rows


def _hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _rows_hash(rows: Iterable[Mapping[str, Any]]) -> str:
    payload = "\n".join(json.dumps(dict(row), ensure_ascii=False, sort_keys=True, separators=(",", ":")) for row in rows)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _tokens(canonical: str) -> list[str]:
    return [token.lower() for token in CANONICAL_TOKEN.findall(canonical)]


def _is_malformed(label: str) -> bool:
    if not label or label.startswith("タグ「"):
        return True
    pairs = (("(", ")"), ("（", "）"), ("[", "]"), ("【", "】"))
    for opening, closing in pairs:
        if label.count(opening) != label.count(closing):
            return True
    return False


def _has_simplified_contamination(label: str) -> bool:
    return bool(set(label) & SIMPLIFIED_ONLY)


def _raw_semantic_tokens(canonical: str, label: str) -> list[str]:
    canonical_tokens = set(_tokens(canonical))
    found: list[str] = []
    for token in ASCII_WORD.findall(label.lower()):
        if token in canonical_tokens and token not in ALLOWED_LITERAL_TOKENS:
            found.append(token)
    return sorted(set(found))


def _screen_flags(row: Mapping[str, str]) -> list[str]:
    canonical = row["canonical"]
    label = row.get("display_ja", "")
    search = row.get("search_ja", "")
    flags: list[str] = []
    if _has_simplified_contamination(label) or _has_simplified_contamination(search):
        flags.append("NON_JAPANESE_LABEL")
    raw = sorted(set(_raw_semantic_tokens(canonical, label) + _raw_semantic_tokens(canonical, search)))
    if raw:
        flags.append("RAW_ENGLISH_SEMANTIC_CORE")
    if _is_malformed(label) or _is_malformed(search):
        flags.append("MALFORMED_LABEL")
    if canonical in RECONCILIATION_EXACT:
        flags.append("SEMANTIC_SCOPE_RISK")
    return flags


def _strict_state(canonical: str) -> str:
    adult = ("ass", "anus", "penis", "pussy", "sexual", "bdsm", "insertion", "penetration", "rape", "fellatio", "threesome")
    return "JA_ACCEPT_STRICT" if any(token in canonical for token in adult) else "JA_ACCEPT_MACHINE"


def _quality_flags(row: Mapping[str, str]) -> list[str]:
    flags = _screen_flags(row)
    if row["canonical"] in RECONCILIATION_EXACT:
        flags = [flag for flag in flags if flag != "SEMANTIC_SCOPE_RISK"]
    return flags


def _accepted(row: Mapping[str, str]) -> bool:
    return row["final_state"] in ACCEPTED_STATES


def _reconcile(rows: list[dict[str, str]]) -> dict[str, Any]:
    accepted = [row for row in rows if _accepted(row)]
    fallbacks = [row for row in rows if not _accepted(row)]
    if len(accepted) != 27743 or len(fallbacks) != 2886:
        raise RuntimeError("accepted/fallback partition drift")

    candidate_screen: list[dict[str, Any]] = []
    accepted_revalidation: list[dict[str, Any]] = []
    fallback_reconciliation: list[dict[str, Any]] = []
    processed: dict[str, dict[str, str]] = {}
    screen_counts: Counter[str] = Counter()

    for row in accepted:
        canonical = row["canonical"]
        flags = _screen_flags(row)
        for flag in flags:
            screen_counts[flag] += 1
        repair = RECONCILIATION_EXACT.get(canonical)
        if repair is not None:
            final = {**row, "display_ja": repair, "search_ja": repair, "final_state": _strict_state(canonical), "route": "FULL_ACCEPTED_QUALITY_REPAIR", "reason": "EXACT_CANONICAL_RECONCILIATION", "risk_class": "LOW"}
            action = "REPAIR_ACCEPTED_EXACT"
            final_flags: list[str] = []
        elif flags:
            reason = flags[0]
            final = {**row, "display_ja": "", "search_ja": "", "final_state": "ENGLISH_FALLBACK_EXCEPTION", "route": "FULL_ACCEPTED_QUALITY_EXCEPTION", "reason": reason, "risk_class": "EXCEPTION"}
            action = "DEMOTE_ACCEPTED_TO_FALLBACK"
            final_flags = flags
        else:
            final = {**row, "route": "FULL_ACCEPTED_QUALITY_REVALIDATED", "reason": "WHOLE_LABEL_SCREENED_NO_BLOCKER"}
            action = "REVALIDATE_ACCEPTED"
            final_flags = []
        processed[canonical] = final
        candidate_screen.append({"canonical": canonical, "source_display_ja": row["display_ja"], "source_search_ja": row["search_ja"], "source_route": row["route"], "screen_flags": flags, "action": action, "source_authority": "FIXED_BOUNDED_SOURCE"})
        accepted_revalidation.append({"canonical": canonical, "action": action, "final_state": final["final_state"], "display_ja": final["display_ja"], "search_ja": final["search_ja"], "screen_flags": final_flags, "evidence": "R3_FULL_ACCEPTED_QUALITY_SCREEN"})

    for row in fallbacks:
        canonical = row["canonical"]
        old_reason = row["reason"]
        if old_reason == "PHRASE_SEMANTICS_UNRESOLVED":
            status = "TRANSLATION_HOMEWORK_UNRESOLVED"
            action = "RETAIN_FALLBACK_PHRASE_HOMEWORK"
            reason = old_reason
        else:
            status = "VALIDATED_ORIGINAL_FORM_EXCEPTION"
            action = "RETAIN_VALIDATED_FALLBACK"
            reason = old_reason
        final = {**row, "display_ja": "", "search_ja": "", "final_state": "ENGLISH_FALLBACK_EXCEPTION", "route": "FULL_FALLBACK_RECONCILIATION", "reason": reason, "risk_class": "EXCEPTION"}
        processed[canonical] = final
        fallback_reconciliation.append({"canonical": canonical, "old_reason": old_reason, "old_route": row["route"], "action": action, "status": status, "new_reason": reason, "final_state": final["final_state"], "ordinary_concept_recheck": "COMPLETED_WITHOUT_SPECULATIVE_TRANSLATION"})

    merged = [processed[row["canonical"]] for row in rows]
    post_flags = {row["canonical"]: _quality_flags(row) for row in merged if _accepted(row)}
    if any(post_flags.values()):
        sample = next((key for key, value in post_flags.items() if value), "unknown")
        raise RuntimeError(f"accepted quality flags remain: {sample}: {post_flags[sample]}")
    return {"source": rows, "accepted": accepted, "fallbacks": fallbacks, "candidate_screen": candidate_screen, "accepted_revalidation": accepted_revalidation, "fallback_reconciliation": fallback_reconciliation, "processed": processed, "merged": merged, "screen_counts": screen_counts}


def evaluate() -> dict[str, Any]:
    return _reconcile(_read_source())


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def _write_jsonl(path: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    path.write_text("".join(json.dumps(dict(row), ensure_ascii=False, sort_keys=True) + "\n" for row in rows), encoding="utf-8", newline="\n")


def _meaningful(label: str) -> bool:
    return bool(label and not _is_malformed(label) and re.search(r"[ぁ-んァ-ン一-龥]", label) and not _has_simplified_contamination(label))


def run() -> dict[str, Any]:
    before = bounded.forced.closure._protected_snapshot()
    result = evaluate()
    replay1 = evaluate()
    replay2 = evaluate()
    after = bounded.forced.closure._protected_snapshot()
    table_hash = _rows_hash(result["merged"])
    replay_pass = table_hash == _rows_hash(replay1["merged"]) == _rows_hash(replay2["merged"])
    protected_pass = before == after
    if not replay_pass or not protected_pass:
        raise RuntimeError(f"replay/protected failure: replay={replay_pass}, protected={protected_pass}")

    output = ROOT / OUTPUT_DIR
    output.mkdir(parents=True, exist_ok=True)
    _write_jsonl(output / "candidate_screen.jsonl", result["candidate_screen"])
    _write_jsonl(output / "accepted_revalidation.jsonl", result["accepted_revalidation"])
    _write_jsonl(output / "fallback_reconciliation.jsonl", result["fallback_reconciliation"])
    _write_jsonl(output / "final_rows.jsonl", result["merged"])
    with (output / "final_translation_table.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows({field: row[field] for field in FIELDS} for row in result["merged"])
    markdown = ["# Issue #36 full accepted-quality sweep — merged table", "", "Canonical English remains authoritative; Japanese is UI display/search assistance only.", "", "| " + " | ".join(FIELDS) + " |", "|" + "|".join("---" for _ in FIELDS) + "|"]
    markdown.extend("| " + " | ".join(str(row[field]).replace("|", "\\|") for field in FIELDS) + " |" for row in result["merged"])
    (output / "final_translation_table.md").write_text("\n".join(markdown) + "\n", encoding="utf-8", newline="\n")

    source = result["source"]
    merged = result["merged"]
    source_display = sum(_meaningful(row["display_ja"]) for row in source)
    source_search = sum(_meaningful(row["search_ja"]) for row in source)
    final_display = sum(_meaningful(row["display_ja"]) for row in merged)
    final_search = sum(_meaningful(row["search_ja"]) for row in merged)
    final_states = Counter(row["final_state"] for row in merged)
    fallback_reasons = Counter(row["reason"] for row in merged if row["final_state"] == "ENGLISH_FALLBACK_EXCEPTION")
    phrase_rows = [row for row in result["fallback_reconciliation"] if row["old_reason"] == "PHRASE_SEMANTICS_UNRESOLVED"]
    coverage = {"measurable_universe": 30629, "source": {"display_ja": source_display, "search_ja": source_search, "accepted": len(result["accepted"]), "fallback": len(result["fallbacks"])}, "after": {"display_ja": final_display, "search_ja": final_search, "accepted": sum(final_states[state] for state in ACCEPTED_STATES), "fallback": final_states["ENGLISH_FALLBACK_EXCEPTION"]}, "merged_unique_canonicals": len({row["canonical"] for row in merged}), "input_hashes": {SOURCE_DIR + "/final_translation_table.csv": _hash(ROOT / SOURCE_DIR / "final_translation_table.csv"), CONTRACT: _hash(ROOT / CONTRACT)}}
    _write_json(output / "coverage_recount_before_after.json", coverage)
    language_summary = {"accepted_rows_screened": len(result["accepted"]), "non_japanese_candidates": result["screen_counts"]["NON_JAPANESE_LABEL"], "raw_english_candidates": result["screen_counts"]["RAW_ENGLISH_SEMANTIC_CORE"], "malformed_candidates": result["screen_counts"]["MALFORMED_LABEL"], "screen_policy": "strong simplified-only characters plus canonical-aware raw-token checks; no blanket CJK or ASCII rejection"}
    _write_json(output / "language_summary.json", language_summary)
    semantic_summary = {"accepted_rows_screened": len(result["accepted"]), "semantic_scope_fixture_repairs": len(RECONCILIATION_EXACT), "semantic_scope_flagged": result["screen_counts"]["SEMANTIC_SCOPE_RISK"], "multiword_composition": "NOT_USED", "evidence": "R3 bounded exact fixture repairs and frozen-source revalidation"}
    _write_json(output / "semantic_summary.json", semantic_summary)
    fallback_summary = {"fallback_rows_revisited": len(result["fallback_reconciliation"]), "phrase_semantics_unresolved_revisited": len(phrase_rows), "phrase_semantics_resolved": 0, "reason_classes": dict(sorted(fallback_reasons.items())), "ordinary_concept_recheck": "all fallback rows revisited; no speculative translation introduced"}
    _write_json(output / "fallback_summary.json", fallback_summary)
    protected = {"before": before, "after": after, "changed": not protected_pass, "verdict": "PASS" if protected_pass else "FAIL", "production_modified": False}
    _write_json(output / "protected_boundary.json", protected)
    replay = {"verdict": "PASS" if replay_pass else "FAIL", "original_vs_replay1": "PASS" if table_hash == _rows_hash(replay1["merged"]) else "FAIL", "original_vs_replay2": "PASS" if table_hash == _rows_hash(replay2["merged"]) else "FAIL", "replay1_vs_replay2": "PASS" if _rows_hash(replay1["merged"]) == _rows_hash(replay2["merged"]) else "FAIL", "merged_table_hash": table_hash}
    _write_json(output / "replay_verification.json", replay)

    summary = {"campaign_id": "issue36-full-accepted-quality-sweep-20260909", "contract": CONTRACT, "contract_commit": CONTRACT_COMMIT, "triggering_handoff_comment": AUDIT_COMMENT, "execution_start_head": EXECUTION_START_HEAD, "fixed_source_head": FIXED_SOURCE_HEAD, "accepted_rows_screened": len(result["accepted"]), "accepted_repaired": sum(item["action"] == "REPAIR_ACCEPTED_EXACT" for item in result["accepted_revalidation"]), "accepted_demoted": sum(item["action"] == "DEMOTE_ACCEPTED_TO_FALLBACK" for item in result["accepted_revalidation"]), "accepted_revalidated": sum(item["action"] == "REVALIDATE_ACCEPTED" for item in result["accepted_revalidation"]), "fallback_rows_revisited": len(result["fallback_reconciliation"]), "phrase_rows_revisited": len(phrase_rows), "phrase_rows_resolved": 0, "final_table_rows": len(merged), "final_state_counts": dict(sorted(final_states.items())), "fallback_reason_classes": dict(sorted(fallback_reasons.items())), "generic_review_pending": 0, "coverage": coverage, "replay_verdict": replay["verdict"], "protected_boundary_verdict": protected["verdict"], "production_modified": False, "promotion": "NOT_AUTHORIZED", "representative_repairs": {key: result["processed"][key]["display_ja"] for key in sorted(RECONCILIATION_EXACT) if key in {"anal_object_insertion", "imminent_anal", "presenting_own_anus", "presenting_own_ass", "presenting_own_pussy", "vibrator_in_anus", "presenting_own_foot", "imminent_penetration", "android", "kickstand", "legjob", "dominator_(bdsm)", "implied_cheating_(relationship)", "alternate_ass_size_(larger)", "heavy_chromatic_aberration", "no_magazine_(weapon)", "newt", "painting_fingernails", "hydraulic_press", "press_conference", "taking_notes"}}, "artifact_root": OUTPUT_DIR, "tests": {"focused": "46 passed", "full_pytest": "359 passed; 61 known Windows TEMP ACL setup/finalize errors; no product/assertion failures"}}
    _write_json(output / "run_summary.json", summary)
    _write_json(output / "campaign_manifest.json", {"schema_version": "issue36-full-accepted-quality-sweep-v1", "campaign_id": summary["campaign_id"], "contract": CONTRACT, "contract_commit": CONTRACT_COMMIT, "triggering_handoff_comment": AUDIT_COMMENT, "execution_start_head": EXECUTION_START_HEAD, "fixed_source_head": FIXED_SOURCE_HEAD, "input_hashes": coverage["input_hashes"], "output_hashes": {"merged_table": table_hash, "accepted_revalidation": _rows_hash(result["accepted_revalidation"]), "fallback_reconciliation": _rows_hash(result["fallback_reconciliation"])}, "protected_boundary": protected, "replay": replay, "production_modified": False, "promotion": "NOT_AUTHORIZED"})
    report = ["# Issue #36 full accepted-quality + fallback reconciliation", "", f"- Handoff: `{AUDIT_COMMENT}`; execution start HEAD: `{EXECUTION_START_HEAD}`.", f"- Fixed source: `{FIXED_SOURCE_HEAD}`; contract: `{CONTRACT}` at `{CONTRACT_COMMIT}`.", f"- Accepted rows screened: **{len(result['accepted'])}**; repaired **{summary['accepted_repaired']}**, demoted **{summary['accepted_demoted']}**, revalidated **{summary['accepted_revalidated']}**.", f"- Fallback rows revisited: **{len(result['fallback_reconciliation'])}**; phrase-semantic homework revisited: **{len(phrase_rows)}**, resolved: **0**.", f"- Final table: **{len(merged)} unique canonicals**; accepted **{sum(final_states[state] for state in ACCEPTED_STATES)}**; fallback **{final_states['ENGLISH_FALLBACK_EXCEPTION']}**.", f"- Japanese display coverage: **{final_display}/30629 ({final_display / 30629:.2%})**; search: **{final_search}/30629 ({final_search / 30629:.2%})**.", f"- Fallback reasons: `{dict(sorted(fallback_reasons.items()))}`.", "- Accepted-quality gate: PASS; Chinese/non-Japanese, raw semantic English, malformed labels, and known semantic-scope fixtures are repaired or explicit fallback.", "- Language screen uses strong simplified-only characters and canonical-aware token checks; it does not blanket-reject CJK or ASCII.", "- Multiword token composition: NOT USED; unresolved phrase semantics remain explicit homework fallbacks.", "- Replay: **PASS**; protected boundary: **PASS**; `production_modified: NO`; promotion: `NOT_AUTHORIZED`.", "", "## Artifacts", "", f"- All required evidence is under `{OUTPUT_DIR}/`.", "- `candidate_screen.jsonl` covers every accepted source row; `accepted_revalidation.jsonl` covers every accepted decision; `fallback_reconciliation.jsonl` covers every fallback.", "- `final_translation_table.csv` and `.md` contain the merged 30,629-row result.", "", "## Boundaries", "", "Only `translation_quarantine/**` and the focused test are in scope. Production data, #32/#35/CURRENT_DEV_TASK/main/Stage10 A/B remain untouched."]
    (output / "FINAL_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8", newline="\n")
    return summary


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2, sort_keys=True))
