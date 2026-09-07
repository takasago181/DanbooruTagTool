"""Apply the frozen Stage8C Phase1 Pilot001 delta and nothing else."""
from __future__ import annotations

from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from danbooru_tag_tool.knowledge import TagKnowledgeCore
from danbooru_tag_tool.stage8c_audit import (
    APPLICABILITY_FIELDS, FAMILY_PROPOSAL_FIELDS, FAMILY_REVIEW_FIELDS,
    REVIEW_FIELDS, read_rows, write_rows,
)


SEMANTIC = ROOT / "data/semantic"
BATCH = "STAGE8C_PHASE1_PILOT001"
SELF_ACTION = ("85", "86", "88", "89", "90", "92", "93", "94", "95",
               "512", "679", "704", "705", "778", "938")
MACHINE = ("310", "311", "312", "313", "314", "1159")
TARGETS = frozenset((*SELF_ACTION, *MACHINE))
BASELINE_HASHES = {
    "semantic_support_profiles.csv": "c243bc4bd7549d70548283865c5c9b5e3484f1835bfc1b05f740c7e9ca845910",
    "family_support_rules.csv": "07b1cd98195316bf8b2b6eec53e0bef19a7437cbb7ee54d8e68f6016a389d80b",
    "stage8c_review_status.csv": "e4ddfe88c9ef4cdce2af80ae77ec0d076f08c76808a9715527a88136eccaebb6",
    "stage8c_family_rule_review.csv": "4e4525fff4998990a967f09395ead1423f5bc6c6d4cc492285ac1d3204373d0a",
    "stage8c_family_relation_proposals.csv": "4cb45129dada9056bf03d4579b1fbe4d9a1710c8e52a1ae1054eecc21302ec48",
    "stage8c_family_candidate_applicability.csv": "46505e736b8980660ef3aec9f2b775973dc682436d7249f05acd5779357acd50",
}
SUPPORT_FIELDS = (
    "special_id", "support_slot", "support_class", "candidate_canonical", "priority",
    "reason_ja", "evidence_level", "evidence_source", "generation_test_status", "enabled",
    "intent_axis", "intent_direction", "combination_mode", "choice_group", "evidence_ref",
    "test_profile_id", "model_scope", "note",
)
FAMILY_SUPPORT_FIELDS = ("family_rule_id", *SUPPORT_FIELDS[1:])


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def row_hash(rows) -> str:
    payload = json.dumps(tuple(rows), ensure_ascii=False, sort_keys=True,
                         separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def support_row(special_id, slot, support_class, canonical, priority, reason,
                intent_axis, combination, *, direction="NEUTRAL", choice="", note=""):
    return {
        "special_id": special_id, "support_slot": slot, "support_class": support_class,
        "candidate_canonical": canonical, "priority": str(priority), "reason_ja": reason,
        "evidence_level": "SEMANTIC_CURATED",
        "evidence_source": "STAGE8C_PILOT001_CURATION",
        "generation_test_status": "NOT_TESTED", "enabled": "true",
        "intent_axis": intent_axis, "intent_direction": direction,
        "combination_mode": combination, "choice_group": choice,
        "evidence_ref": f"SPECIAL2788_ID_{special_id};STAGE8C_PILOT001",
        "test_profile_id": "", "model_scope": "", "note": note,
    }


MACHINE_ROWS = (
    support_row("310", "IMPLEMENT", "OPTIONAL_VARIATION", "breast_pump", 10,
                "搾乳用途として具体化する場合の器具候補", "SPECIFICITY", "CONTEXTUAL",
                direction="UP", note="乳房からの搾乳として描く場合のみ"),
    support_row("310", "STATE_REACTION", "OPTIONAL_VARIATION", "lactation", 20,
                "乳汁を搾出する場面として具体化する場合の状態候補", "SPECIFICITY", "CONTEXTUAL",
                direction="UP", note="乳汁を扱う場合のみ。精液搾出へ一般化しない"),
    support_row("313", "IMPLEMENT", "CORE_SUPPORT", "vibrator", 10,
                "Sybianの振動器具としての性質を明示する候補", "SPECIFICITY", "ADDITIVE",
                direction="UP", note="固有機械名の器具性を補助"),
    support_row("313", "IMPLEMENT", "CORE_SUPPORT", "sex_toy", 20,
                "性的刺激用器具であることを補う候補", "SPECIFICITY", "ADDITIVE",
                direction="UP", note="Special-specific relation; Family ruleではない"),
    support_row("313", "POSE", "OPTIONAL_VARIATION", "sitting", 30,
                "機械に座って使用する構図を選ぶ場合の姿勢候補", "COMPOSITION", "CONTEXTUAL",
                note="座位で描く場合のみ"),
    support_row("313", "POSE", "OPTIONAL_VARIATION", "straddling", 40,
                "機械へ跨る使用構図を選ぶ場合の姿勢候補", "COMPOSITION", "ALTERNATIVE",
                choice="sybian_use_pose", note="座位表現の代替候補"),
    support_row("314", "SUBJECT_BASIC", "CORE_SUPPORT", "robot", 10,
                "性的相互作用の主体または相手をロボットとして明示する候補", "STRUCTURE", "ADDITIVE",
                note="性別や人型形状は追加推定しない"),
    support_row("314", "ACTION_SUPPORT", "CORE_SUPPORT", "sex", 20,
                "ロボットとの相互作用が性的行為であることを補う候補", "STRUCTURE", "ADDITIVE",
                note="Pilot001 robot-sex structure"),
    support_row("314", "SUBJECT_BASIC", "OPTIONAL_VARIATION", "android", 30,
                "人型ロボットとして具体化する場合の主体候補", "SPECIFICITY", "CONTEXTUAL",
                direction="UP", note="人型として描く場合のみ"),
    support_row("1159", "IMPLEMENT", "CORE_SUPPORT", "beads", 10,
                "機械の刺激部にビーズ状部品を用いることを明示する候補", "SPECIFICITY", "ADDITIVE",
                direction="UP", note="Ruleset2の監査済み語義に基づく"),
    support_row("1159", "IMPLEMENT", "OPTIONAL_VARIATION", "anal_beads", 20,
                "肛門用ビーズとして具体化する場合の器具候補", "SPECIFICITY", "CONTEXTUAL",
                direction="UP", note="肛門用途として描く場合のみ"),
)


FAMILY_PROPOSAL = {
    "proposal_id": "FRP_P1_SELF_ACTION_SOLO_V1", "family_rule_id": "GFR_SELF_ACTION",
    "support_slot": "SUBJECT_BASIC", "support_class": "OPTIONAL_VARIATION",
    "candidate_canonical": "solo", "priority": "10",
    "reason_ja": "自己行為の主体を単独人物として構成する共通の任意補助候補",
    "evidence_level": "SEMANTIC_CURATED", "evidence_source": "SRC_STAGE8B_PILOT_CURATION",
    "intent_axis": "COMPOSITION", "intent_direction": "NEUTRAL",
    "combination_mode": "CONTEXTUAL", "choice_group": "",
    "evidence_ref": "STAGE8C_PILOT001_SELF_ACTION_15_MEMBER_REVIEW",
    "test_profile_id": "", "model_scope": "", "proposal_status": "PROMOTED",
    "note": "NOT_TESTED; explicit Special relation takes precedence for the same canonical",
}


def family_support_row():
    return {
        "family_rule_id": FAMILY_PROPOSAL["family_rule_id"],
        **{key: FAMILY_PROPOSAL[key] for key in (
            "support_slot", "support_class", "candidate_canonical", "priority", "reason_ja",
            "evidence_level", "evidence_source", "intent_axis", "intent_direction",
            "combination_mode", "choice_group", "evidence_ref", "test_profile_id", "model_scope",
        )},
        "generation_test_status": "NOT_TESTED", "enabled": "true",
        "note": FAMILY_PROPOSAL["note"],
    }


def _read(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return tuple(csv.DictReader(handle))


def main() -> int:
    knowledge = TagKnowledgeCore.load(ROOT)
    profiles = knowledge.load_generation_profile_store(ROOT)
    members = {
        family: tuple(sorted((sid for sid, profile in profiles.profiles.items()
                              if profile.FamilyRuleId == family), key=int))
        for family in ("GFR_SELF_ACTION", "GFR_MACHINE_STRUCTURED")
    }
    if members["GFR_SELF_ACTION"] != SELF_ACTION or members["GFR_MACHINE_STRUCTURED"] != MACHINE:
        raise ValueError(f"Pilot001 family membership drift: {members}")

    current_hashes = {name: sha256(SEMANTIC / name) for name in BASELINE_HASHES}
    baseline = current_hashes == BASELINE_HASHES
    support = _read(SEMANTIC / "semantic_support_profiles.csv")
    family_support = _read(SEMANTIC / "family_support_rules.csv")
    reviews = read_rows(SEMANTIC / "stage8c_review_status.csv", REVIEW_FIELDS)
    family_reviews = read_rows(SEMANTIC / "stage8c_family_rule_review.csv", FAMILY_REVIEW_FIELDS)
    proposals = read_rows(SEMANTIC / "stage8c_family_relation_proposals.csv", FAMILY_PROPOSAL_FIELDS)
    applicability = read_rows(
        SEMANTIC / "stage8c_family_candidate_applicability.csv", APPLICABILITY_FIELDS
    )
    before_id312_hash = row_hash(row for row in support if row["special_id"] == "312")
    unrelated_before = row_hash(row for row in reviews if row["special_id"] not in TARGETS)

    if baseline:
        if len(support) != 39 or family_support or proposals or applicability:
            raise ValueError("Pilot001 baseline structure mismatch")
        if len(tuple(row for row in support if row["special_id"] == "312")) != 5:
            raise ValueError("Pilot001 ID312 baseline must contain five rows")
        support = (*support, *MACHINE_ROWS)
        family_support = (family_support_row(),)

        updated_reviews = []
        for row in reviews:
            item = dict(row)
            sid = row["special_id"]
            if sid in TARGETS and sid not in {"88", "312"}:
                decision = "UNRESOLVED" if sid == "311" else "SUPPORT_DEFINED"
                item.update({
                    "review_decision": decision,
                    "review_reason_ja": (
                        "Pilot001で語義を確認したが、共通または安全な個別補助relationを確定できない。"
                        if sid == "311" else
                        "Stage8C Phase1 Pilot001の限定scopeでsupport relationを定義済み。"
                    ),
                    "evidence_ref": f"STAGE8C_PILOT001_SPECIAL_{sid}",
                    "review_batch_id": BATCH,
                    "note": ("support rows=0; no fabricated generic coverage" if sid == "311" else ""),
                })
            updated_reviews.append(item)
        reviews = tuple(updated_reviews)

        updated_family = []
        for row in family_reviews:
            item = dict(row)
            if row["family_rule_id"] == "GFR_SELF_ACTION":
                item.update({
                    "review_decision": "RULES_DEFINED", "reviewed_member_count": "15",
                    "review_reason_ja": "15 membersすべてでsoloの同一relationを確認。",
                    "evidence_ref": "FRP_P1_SELF_ACTION_SOLO_V1;15_MEMBER_APPLICABILITY",
                    "review_batch_id": BATCH,
                    "note": "Explicit Special relation wins for duplicate canonical.",
                })
            elif row["family_rule_id"] == "GFR_MACHINE_STRUCTURED":
                item.update({
                    "review_decision": "NO_COMMON_RULE", "reviewed_member_count": "6",
                    "review_reason_ja": "6 membersは機械概念の具体的構造が異なり、安全な共通supportを定義しない。",
                    "evidence_ref": "STAGE8C_PILOT001_MACHINE_6_MEMBER_REVIEW",
                    "review_batch_id": BATCH,
                    "note": "No generic machine/sex_toy Family relation.",
                })
            updated_family.append(item)
        family_reviews = tuple(updated_family)
        proposals = (FAMILY_PROPOSAL,)
        applicability = tuple({
            "proposal_id": FAMILY_PROPOSAL["proposal_id"], "special_id": sid,
            "special_term_snapshot": knowledge.special[sid].term,
            "relation_fit": "APPLIES_SAME_RELATION",
            "review_reason_ja": "自己行為を単独主体として構成する同一の任意補助relationが適用可能。",
            "evidence_ref": "STAGE8C_PILOT001_SELF_ACTION_15_MEMBER_REVIEW",
            "review_batch_id": BATCH, "note": "NOT_TESTED",
        } for sid in SELF_ACTION)

        write_rows(SEMANTIC / "semantic_support_profiles.csv", SUPPORT_FIELDS, support)
        write_rows(SEMANTIC / "family_support_rules.csv", FAMILY_SUPPORT_FIELDS, family_support)
        write_rows(SEMANTIC / "stage8c_review_status.csv", REVIEW_FIELDS, reviews)
        write_rows(SEMANTIC / "stage8c_family_rule_review.csv", FAMILY_REVIEW_FIELDS, family_reviews)
        write_rows(SEMANTIC / "stage8c_family_relation_proposals.csv", FAMILY_PROPOSAL_FIELDS, proposals)
        write_rows(SEMANTIC / "stage8c_family_candidate_applicability.csv", APPLICABILITY_FIELDS, applicability)

    support_after = _read(SEMANTIC / "semantic_support_profiles.csv")
    family_after = _read(SEMANTIC / "family_support_rules.csv")
    reviews_after = read_rows(SEMANTIC / "stage8c_review_status.csv", REVIEW_FIELDS)
    counts = Counter(row["review_decision"] for row in reviews_after)
    special_counts = Counter(row["special_id"] for row in support_after)
    id312_hash = row_hash(row for row in support_after if row["special_id"] == "312")
    unrelated_after = row_hash(row for row in reviews_after if row["special_id"] not in TARGETS)
    expected = {
        "SUPPORT_DEFINED": 28, "UNRESOLVED": 1, "NO_SUGGESTION": 0,
        "UNREVIEWED": 2759,
    }
    actual = {key: counts[key] for key in expected}
    if actual != expected or len(support_after) != 50 or len(family_after) != 1:
        raise ValueError(f"Pilot001 acceptance count mismatch: {actual}, special={len(support_after)}, family={len(family_after)}")
    if {sid: special_counts[sid] for sid in MACHINE} != {
            "310": 2, "311": 0, "312": 5, "313": 4, "314": 3, "1159": 2}:
        raise ValueError("Pilot001 machine per-Special count mismatch")
    if id312_hash != before_id312_hash or unrelated_before != unrelated_after:
        raise ValueError("Pilot001 protected ID312/unrelated review drift")
    if family_after[0]["candidate_canonical"] != "solo" or family_after[0]["family_rule_id"] != "GFR_SELF_ACTION":
        raise ValueError("Pilot001 family production row mismatch")

    result = {
        "stage": "Stage8C Phase1 Pilot001 implementation",
        "implementation_complete": True, "pilot001_acceptance": "NOT COMPLETE",
        "target_special_ids": sorted(TARGETS, key=int),
        "family_members": {key: list(value) for key, value in members.items()},
        "review_decision_counts": actual,
        "special_support_rows": len(support_after), "family_support_rows": len(family_after),
        "machine_special_relation_counts": {sid: special_counts[sid] for sid in MACHINE},
        "id312_five_row_content_hash": id312_hash,
        "unrelated_review_rows_hash": unrelated_after,
        "production_hashes": {
            "semantic_support_profiles.csv": sha256(SEMANTIC / "semantic_support_profiles.csv"),
            "family_support_rules.csv": sha256(SEMANTIC / "family_support_rules.csv"),
        },
        "stage8c_overall": "NOT FINAL", "stage9": "NOT STARTED", "stage10": "NOT STARTED",
        "runtime_external_calls": 0,
    }
    out = ROOT / "benchmarks/stage8c/pilot001_scope_diff.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
