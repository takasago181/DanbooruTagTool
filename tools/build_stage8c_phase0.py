"""Build deterministic Stage 8C Phase 0 audit-only ledgers."""
from __future__ import annotations

from collections import Counter
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from danbooru_tag_tool.knowledge import TagKnowledgeCore
from danbooru_tag_tool.stage8b_support import SupportKnowledgeStore
from danbooru_tag_tool.stage8c_audit import (
    APPLICABILITY_FIELDS, EVIDENCE_EVENT_FIELDS, FAMILY_PROPOSAL_FIELDS, FAMILY_REVIEW_FIELDS,
    MODEL_FAMILIARITY_FIELDS, NON_TAG_FIELDS, PRACTICAL_USE_FIELDS,
    REVIEW_FIELDS, TEST_SLOT_FIELDS, family_members, write_rows,
)

PILOT_IDS = frozenset({"161", "416", "312", "325", "173", "16", "385", "488", "88", "122"})


def main() -> int:
    knowledge = TagKnowledgeCore.load(ROOT)
    profiles = knowledge.load_generation_profile_store(ROOT)
    support = SupportKnowledgeStore.load(ROOT, knowledge, profiles)
    directory = ROOT / "data/semantic"

    review_rows = []
    for special_id, special in knowledge.special.items():
        is_pilot = special_id in PILOT_IDS
        if is_pilot and not support.candidates((special_id,)):
            raise RuntimeError(f"Pilot resolver has no support: {special_id}")
        review_rows.append({
            "special_id": special_id,
            "special_term_snapshot": special.term,
            "review_decision": "SUPPORT_DEFINED" if is_pilot else "UNREVIEWED",
            "review_reason_ja": (
                "Stage 8B Pilotのenabled profileを現resolverで確認済み。" if is_pilot else ""
            ),
            "evidence_ref": "STAGE8B_PILOT" if is_pilot else "",
            "review_batch_id": "STAGE8C_PHASE0_SEED" if is_pilot else "STAGE8C_PHASE0_INITIAL",
            "note": "",
        })
    write_rows(directory / "stage8c_review_status.csv", REVIEW_FIELDS, review_rows)

    members = family_members(profiles)
    family_rows = []
    for family_id, rule in sorted(profiles.family_rules.items()):
        zero_member = not members[family_id]
        family_rows.append({
            "family_rule_id": family_id,
            "review_decision": "NOT_APPLICABLE_NO_MEMBERS" if zero_member else "UNREVIEWED",
            "member_count": len(members[family_id]),
            "reviewed_member_count": 0,
            "review_reason_ja": "現production Generation Profileにmemberがないため、Family relation promotionは適用外。" if zero_member else "",
            "evidence_ref": "PHASE0_PRODUCTION_FAMILY_MEMBERSHIP" if zero_member else "",
            "review_batch_id": "STAGE8C_PHASE0_CORRECTION_V16" if zero_member else "STAGE8C_PHASE0_INITIAL",
            "note": (f"StaticFamily={rule.GenerationFamily}; zero-member FamilyRuleId; no enabled family relation may be owned."
                     if zero_member else f"StaticFamily={rule.GenerationFamily}; applicability review not started"),
        })
    write_rows(directory / "stage8c_family_rule_review.csv", FAMILY_REVIEW_FIELDS, family_rows)

    # Phase 0 creates schemas only; no applicability, model, non-tag, test,
    # practicality, or evidence decision is asserted.
    for name, fields in (
        ("stage8c_family_relation_proposals.csv", FAMILY_PROPOSAL_FIELDS),
        ("stage8c_family_candidate_applicability.csv", APPLICABILITY_FIELDS),
        ("stage8c_model_familiarity.csv", MODEL_FAMILIARITY_FIELDS),
        ("stage8c_non_tag_strategy.csv", NON_TAG_FIELDS),
        ("stage10_test_slots.csv", TEST_SLOT_FIELDS),
        ("stage8c_practical_use.csv", PRACTICAL_USE_FIELDS),
        ("stage8c_relation_evidence_events.csv", EVIDENCE_EVENT_FIELDS),
    ):
        write_rows(directory / name, fields, ())

    decisions = Counter(row["review_decision"] for row in review_rows)
    print({
        "special_rows": len(review_rows),
        "review_decisions": dict(sorted(decisions.items())),
        "family_rule_rows": len(family_rows),
        "production_support_rows_changed": 0,
    })
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
