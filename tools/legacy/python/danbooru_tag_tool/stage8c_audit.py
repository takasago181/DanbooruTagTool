"""Stage 8C audit-only schemas and validators; never imported by runtime UI."""
from __future__ import annotations

import csv
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


REVIEW_FIELDS = (
    "special_id", "special_term_snapshot", "review_decision",
    "review_reason_ja", "evidence_ref", "review_batch_id", "note",
)
FAMILY_REVIEW_FIELDS = (
    "family_rule_id", "review_decision", "member_count",
    "reviewed_member_count", "review_reason_ja", "evidence_ref",
    "review_batch_id", "note",
)
APPLICABILITY_FIELDS = (
    "proposal_id", "special_id", "special_term_snapshot", "relation_fit",
    "review_reason_ja", "evidence_ref", "review_batch_id", "note",
)
FAMILY_PROPOSAL_FIELDS = (
    "proposal_id", "family_rule_id", "support_slot", "support_class",
    "candidate_canonical", "priority", "reason_ja", "evidence_level",
    "evidence_source", "intent_axis", "intent_direction", "combination_mode",
    "choice_group", "evidence_ref", "test_profile_id", "model_scope",
    "proposal_status", "note",
)
RESEARCH_SOURCE_FIELDS = (
    "source_id", "source_tier", "source_kind", "title",
    "model_or_tool_scope", "version_or_revision",
    "snapshot_or_retrieved_date", "url_or_ref", "allowed_claim_scope",
    "evidence_level_cap", "note",
)
MODEL_FAMILIARITY_FIELDS = (
    "model_scope", "exact_model_version", "source_checked_date",
    "latest_version_status", "training_cutoff_status", "training_cutoff_value",
    "candidate_canonical", "familiarity_status", "proxy_count_or_presence",
    "evidence_source_id", "test_priority", "reason_ja", "note",
)
NON_TAG_FIELDS = (
    "special_id", "special_term_snapshot", "trigger_reason", "strategy_kind",
    "strategy_tool_scope", "evidence_source_id", "stage_target",
    "review_reason_ja", "note",
)
TEST_SLOT_FIELDS = (
    "test_profile_id", "slot_id", "semantic_role", "insertion_location",
    "required_meaning_ja", "must_preserve", "must_not_change", "ab_role",
    "expected_visible_effect", "evaluation_axes", "note",
)
PRACTICAL_USE_FIELDS = (
    "owner_type", "owner_id", "candidate_canonical", "proposal_id", "practical_use",
    "stage9_operation_axis", "stage10_test_priority", "non_tag_fallback",
    "review_reason_ja", "note",
)
EVIDENCE_EVENT_FIELDS = (
    "evidence_event_id", "owner_kind", "owner_id", "candidate_canonical", "proposal_id",
    "evidence_level", "evidence_source", "evidence_ref", "test_profile_id",
    "model_scope", "seed_set_ref", "generation_condition_hash",
    "observed_effect", "observed_failures", "result_ref", "event_status",
    "supersedes_event_id", "note",
)

REVIEW_DECISIONS = frozenset({
    "UNREVIEWED", "SUPPORT_DEFINED", "NO_SUGGESTION", "UNRESOLVED",
})
FAMILY_DECISIONS = frozenset({
    "UNREVIEWED", "RULES_DEFINED", "NO_COMMON_RULE", "UNRESOLVED",
    "NOT_APPLICABLE_NO_MEMBERS",
})
PROPOSAL_STATUSES = frozenset({
    "DRAFT", "READY_FOR_MEMBER_REVIEW", "UNIVERSAL_PASS", "REJECTED",
    "UNRESOLVED", "PROMOTED",
})
RELATION_FITS = frozenset({
    "APPLIES_SAME_RELATION", "DOES_NOT_APPLY", "METADATA_DIFFERS", "UNRESOLVED",
})
EVIDENCE_LEVELS = frozenset({
    "SOURCE_VERIFIED", "SEMANTIC_CURATED", "MODEL_OBSERVED", "USER_ENV_VERIFIED",
})


def read_rows(path: Path, fields: tuple[str, ...]) -> tuple[dict[str, str], ...]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != fields:
            raise ValueError(f"{path.name}: invalid columns: {reader.fieldnames!r}")
        return tuple(reader)


def write_rows(path: Path, fields: tuple[str, ...], rows: Iterable[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def validate_review_ledger(rows, knowledge, support_store) -> dict[str, int]:
    if len(rows) != len(knowledge.special) or len({r["special_id"] for r in rows}) != len(rows):
        raise ValueError("review ledger must contain exact unique Special IDs")
    if {r["special_id"] for r in rows} != set(knowledge.special):
        raise ValueError("review ledger Special ID set mismatch")
    counts = Counter()
    for row in rows:
        sid = row["special_id"]
        if row["special_term_snapshot"] != knowledge.special[sid].term:
            raise ValueError(f"Special term snapshot mismatch: {sid}")
        decision = row["review_decision"]
        if decision not in REVIEW_DECISIONS or not row["review_batch_id"]:
            raise ValueError(f"Invalid review row: {sid}")
        relation_count = len(support_store.candidates((sid,)))
        if decision == "SUPPORT_DEFINED" and relation_count == 0:
            raise ValueError(f"SUPPORT_DEFINED without relation: {sid}")
        if decision in {"NO_SUGGESTION", "UNRESOLVED"}:
            if relation_count or not row["review_reason_ja"] or not row["evidence_ref"]:
                raise ValueError(f"Invalid terminal no-relation review: {sid}")
        counts[decision] += 1
    return dict(sorted(counts.items()))


def family_members(profile_store) -> dict[str, tuple[str, ...]]:
    result = {}
    for family_id in profile_store.family_rules:
        result[family_id] = tuple(sorted(
            (sid for sid, profile in profile_store.profiles.items()
             if profile.FamilyRuleId == family_id),
            key=lambda value: int(value),
        ))
    return result


def validate_family_review(rows, profile_store) -> None:
    members = family_members(profile_store)
    if len(rows) != len(members) or {r["family_rule_id"] for r in rows} != set(members):
        raise ValueError("family review inventory mismatch")
    for row in rows:
        fid = row["family_rule_id"]
        if row["review_decision"] not in FAMILY_DECISIONS:
            raise ValueError(f"Invalid family review decision: {fid}")
        if int(row["member_count"]) != len(members[fid]):
            raise ValueError(f"Family member count mismatch: {fid}")
        member_count = len(members[fid])
        reviewed = int(row["reviewed_member_count"])
        if not 0 <= reviewed <= member_count:
            raise ValueError(f"Invalid reviewed member count: {fid}")
        decision = row["review_decision"]
        if decision == "NOT_APPLICABLE_NO_MEMBERS":
            if member_count or reviewed or not row["review_reason_ja"] or not row["evidence_ref"]:
                raise ValueError(f"Invalid zero-member terminal family: {fid}")
        elif decision in {"RULES_DEFINED", "NO_COMMON_RULE", "UNRESOLVED"}:
            if not member_count or reviewed != member_count or not row["review_reason_ja"] or not row["evidence_ref"]:
                raise ValueError(f"Incomplete terminal family review: {fid}")


@dataclass(frozen=True, slots=True)
class ApplicabilityValidation:
    enabled_family_relations: int
    universally_applicable: int
    blocked: int
    missing_member_reviews: int


def validate_family_proposals(rows, knowledge, profile_store, source_ids) -> dict[str, dict[str, str]]:
    """Validate audit-only full family relation definitions before promotion."""
    from danbooru_tag_tool.stage8b_support import (
        COMBINATION_MODES, EVIDENCE_LEVELS as SUPPORT_EVIDENCE_LEVELS,
        INTENT_AXES, INTENT_DIRECTIONS, SUPPORT_CLASSES, SUPPORT_SLOTS,
    )
    proposals = {}
    for row in rows:
        proposal_id = row["proposal_id"]
        if not proposal_id or proposal_id in proposals:
            raise ValueError("Missing/duplicate family proposal ID")
        if row["family_rule_id"] not in profile_store.family_rules or row["candidate_canonical"] not in knowledge.canonical:
            raise ValueError("Unknown family proposal identity")
        if row["support_slot"] not in SUPPORT_SLOTS or row["support_class"] not in SUPPORT_CLASSES:
            raise ValueError("Invalid family proposal support metadata")
        if row["evidence_level"] not in SUPPORT_EVIDENCE_LEVELS or row["evidence_source"] not in source_ids:
            raise ValueError("Invalid family proposal evidence")
        if row["intent_axis"] and row["intent_axis"] not in INTENT_AXES:
            raise ValueError("Invalid family proposal intent axis")
        if row["intent_direction"] and row["intent_direction"] not in INTENT_DIRECTIONS:
            raise ValueError("Invalid family proposal intent direction")
        if row["combination_mode"] not in COMBINATION_MODES:
            raise ValueError("Invalid family proposal combination mode")
        if row["combination_mode"] == "ALTERNATIVE" and not row["choice_group"]:
            raise ValueError("Alternative family proposal requires choice group")
        if row["proposal_status"] not in PROPOSAL_STATUSES or not row["reason_ja"] or not row["evidence_ref"]:
            raise ValueError("Incomplete family proposal")
        if (row["evidence_level"] in {"MODEL_OBSERVED", "USER_ENV_VERIFIED"}
                and not (row["test_profile_id"] and row["model_scope"])):
            raise ValueError("Observed family proposal requires test profile and model scope")
        if (not family_members(profile_store)[row["family_rule_id"]]
                and row["proposal_status"] in {"READY_FOR_MEMBER_REVIEW", "UNIVERSAL_PASS", "PROMOTED"}):
            raise ValueError("Zero-member family cannot have promotable proposal")
        try:
            int(row["priority"])
        except ValueError as error:
            raise ValueError("Invalid family proposal priority") from error
        proposals[proposal_id] = row
    return proposals


def _relation_metadata_matches(proposal, relation) -> bool:
    metadata = {
        "support_slot": relation.support_slot,
        "support_class": relation.support_class or "",
        "priority": str(relation.priority), "reason_ja": relation.reason_ja,
        "evidence_level": relation.evidence_level, "evidence_source": relation.evidence_source,
        "intent_axis": relation.intent_axis or "", "intent_direction": relation.intent_direction or "",
        "combination_mode": relation.combination_mode or "", "choice_group": relation.choice_group or "",
        "evidence_ref": relation.evidence_ref or "", "test_profile_id": relation.test_profile_id or "",
        "model_scope": relation.model_scope or "",
    }
    return all(proposal[field] == value for field, value in metadata.items())


def _validate_active_proposal_uniqueness(proposals) -> None:
    active = Counter(
        (proposal["family_rule_id"], proposal["candidate_canonical"])
        for proposal in proposals.values()
        if proposal["proposal_status"] in {"READY_FOR_MEMBER_REVIEW", "UNIVERSAL_PASS", "PROMOTED"}
    )
    if any(count > 1 for count in active.values()):
        raise ValueError("Duplicate active/promotable family proposal")


def validate_family_applicability(rows, proposals, family_support_rows, knowledge,
                                  profile_store) -> ApplicabilityValidation:
    members = family_members(profile_store)
    _validate_active_proposal_uniqueness(proposals)
    indexed = {}
    for row in rows:
        key = (row["proposal_id"], row["special_id"])
        if key in indexed:
            raise ValueError(f"Duplicate applicability review: {key}")
        proposal_id, sid = key
        if proposal_id not in proposals or sid not in knowledge.special:
            raise ValueError(f"Unknown applicability identity: {key}")
        proposal = proposals[proposal_id]
        fid = proposal["family_rule_id"]
        if sid not in members[fid]:
            raise ValueError(f"Special is not a FamilyRuleId member: {key}")
        if row["special_term_snapshot"] != knowledge.special[sid].term:
            raise ValueError(f"Applicability Special term mismatch: {key}")
        if row["relation_fit"] not in RELATION_FITS or not row["review_reason_ja"] or not row["evidence_ref"]:
            raise ValueError(f"Invalid applicability review: {key}")
        indexed[key] = row
    enabled = [row for row in family_support_rows if row.enabled]
    enabled_by_identity = {}
    for relation in enabled:
        identity = (relation.owner_id, relation.candidate_canonical)
        if identity in enabled_by_identity:
            raise ValueError("Duplicate enabled production family relation")
        if not members[relation.owner_id]:
            raise ValueError("Zero-member family cannot own enabled production relation")
        enabled_by_identity[identity] = relation

    # UNIVERSAL_PASS and PROMOTED are earned from current, complete member
    # applicability before promotion; neither is merely a CSV assertion.
    for proposal in proposals.values():
        status = proposal["proposal_status"]
        member_ids = members[proposal["family_rule_id"]]
        proposal_reviews = [indexed.get((proposal["proposal_id"], sid)) for sid in member_ids]
        if status in {"UNIVERSAL_PASS", "PROMOTED"}:
            if not member_ids or any(review is None for review in proposal_reviews):
                raise ValueError("UNIVERSAL_PASS requires exact complete current member applicability")
            if any(review["relation_fit"] != "APPLIES_SAME_RELATION" for review in proposal_reviews):
                raise ValueError("UNIVERSAL_PASS requires all APPLIES_SAME_RELATION")
        if status == "PROMOTED":
            relation = enabled_by_identity.get((proposal["family_rule_id"], proposal["candidate_canonical"]))
            if relation is None or not _relation_metadata_matches(proposal, relation):
                raise ValueError("PROMOTED proposal requires exact enabled production relation")

    universal = blocked = missing = 0
    for relation in enabled:
        matching = [p for p in proposals.values() if p["proposal_status"] in {"UNIVERSAL_PASS", "PROMOTED"}
                    and p["family_rule_id"] == relation.owner_id
                    and p["candidate_canonical"] == relation.candidate_canonical
                    and _relation_metadata_matches(p, relation)]
        if len(matching) != 1:
            raise ValueError("Enabled production family relation requires one exact proven proposal")
        proposal = matching[0]
        fid = proposal["family_rule_id"]
        fits = []
        for sid in members[fid]:
            review = indexed.get((proposal["proposal_id"], sid))
            if review is None:
                missing += 1
            else:
                fits.append(review["relation_fit"])
        if len(fits) == len(members[relation.owner_id]) and all(
                fit == "APPLIES_SAME_RELATION" for fit in fits):
            universal += 1
        else:
            blocked += 1
    return ApplicabilityValidation(len(enabled), universal, blocked, missing)


def validate_family_state(rows, proposals, family_support_rows, knowledge, profile_store) -> None:
    """Cross-check terminal Family review decisions against proposal lifecycle."""
    members = family_members(profile_store)
    rows_by_id = {row["family_rule_id"]: row for row in rows}
    for family_id, member_ids in members.items():
        decision = rows_by_id[family_id]["review_decision"]
        enabled = [row for row in family_support_rows if row.enabled and row.owner_id == family_id]
        family_proposals = [p for p in proposals.values() if p["family_rule_id"] == family_id]
        proven = [p for p in family_proposals if p["proposal_status"] in {"UNIVERSAL_PASS", "PROMOTED"}]
        promoted = [p for p in family_proposals if p["proposal_status"] == "PROMOTED"]
        promotable = [p for p in family_proposals if p["proposal_status"] in {"READY_FOR_MEMBER_REVIEW", "UNIVERSAL_PASS", "PROMOTED"}]
        if decision == "RULES_DEFINED" and not proven:
            raise ValueError("RULES_DEFINED requires proven family proposal")
        if decision == "NO_COMMON_RULE" and (enabled or proven):
            raise ValueError("NO_COMMON_RULE cannot coexist with enabled/proven family relation")
        if decision == "UNRESOLVED" and promoted:
            raise ValueError("UNRESOLVED cannot coexist with PROMOTED relation")
        if decision == "NOT_APPLICABLE_NO_MEMBERS" and (member_ids or enabled or promotable):
            raise ValueError("NOT_APPLICABLE_NO_MEMBERS cannot have relations/proposals")


def validate_research_sources(rows) -> None:
    allowed_tiers = {"TIER_A", "TIER_B", "TIER_C", "TIER_D"}
    allowed_kinds = {
        "MODEL_CARD", "TOOL_DOC", "DANBOORU_WIKI", "DANBOORU_ALIAS",
        "DANBOORU_IMPLICATION", "DANBOORU_API", "DATASET_SNAPSHOT",
        "COMMUNITY_PRACTICE", "CONTROLLED_TEST", "USER_TEST",
    }
    ids = set()
    for row in rows:
        if row["source_id"] in ids or row["source_tier"] not in allowed_tiers:
            raise ValueError("Invalid/duplicate research source")
        if row["source_kind"] not in allowed_kinds or row["evidence_level_cap"] not in EVIDENCE_LEVELS:
            raise ValueError("Invalid research source kind/evidence cap")
        if not all(row[name] for name in (
            "source_id", "title", "model_or_tool_scope", "version_or_revision",
            "snapshot_or_retrieved_date", "url_or_ref", "allowed_claim_scope",
        )):
            raise ValueError("Incomplete research source")
        ids.add(row["source_id"])


def validate_model_familiarity(rows, knowledge, source_ids) -> None:
    statuses = {
        "EXACT_VERSION_SOURCE_CONFIRMED", "VERSION_LINEAGE_SUPPORT",
        "TRAINING_ERA_PROXY_PRESENT", "POST_TRAINING_RISK", "UNKNOWN",
    }
    latest_statuses = {"CURRENT_CONFIRMED", "BRANCH_CURRENT_CONFIRMED", "NOT_CURRENT", "UNKNOWN"}
    cutoff_statuses = {"KNOWN", "UNKNOWN"}
    for row in rows:
        if row["candidate_canonical"] not in knowledge.canonical:
            raise ValueError("Unknown familiarity canonical")
        if row["familiarity_status"] not in statuses or row["test_priority"] not in {"HIGH", "MEDIUM", "LOW"}:
            raise ValueError("Invalid model familiarity status")
        if row["latest_version_status"] not in latest_statuses or row["training_cutoff_status"] not in cutoff_statuses:
            raise ValueError("Invalid model familiarity version/cutoff status")
        if row["evidence_source_id"] not in source_ids:
            raise ValueError("Unknown familiarity evidence source")
        if row["training_cutoff_status"] == "UNKNOWN" and row["training_cutoff_value"]:
            raise ValueError("UNKNOWN exact-model cutoff must remain blank")


def validate_non_tag(rows, knowledge, source_ids) -> None:
    triggers = {"TAG_SUPPORT_INSUFFICIENT", "SPATIAL_COMPLEXITY", "POSE_LAYOUT_COMPLEXITY", "DETAIL_FAILURE", "IDENTITY_STYLE", "VARIATION", "UNKNOWN"}
    strategies = {"REGIONAL_CONDITIONING", "CONTROL_GUIDANCE", "INPAINT_DETAIL", "VARIATION_ENGINE", "LORA_IDENTITY_OR_STYLE", "MODEL_CHANGE_OR_PROFILE", "NONE", "UNKNOWN"}
    for row in rows:
        sid = row["special_id"]
        if sid not in knowledge.special or row["special_term_snapshot"] != knowledge.special[sid].term:
            raise ValueError("Invalid non-tag Special identity")
        if row["trigger_reason"] not in triggers or row["strategy_kind"] not in strategies:
            raise ValueError("Invalid non-tag strategy")
        if row["stage_target"] not in {"STAGE9", "STAGE10"} or row["evidence_source_id"] not in source_ids:
            raise ValueError("Invalid non-tag target/source")


def validate_test_slots(rows) -> None:
    keys = set()
    for row in rows:
        key = (row["test_profile_id"], row["slot_id"])
        if key in keys or row["ab_role"] not in {"FIXED", "A_ONLY", "B_ONLY", "CHANGED_FACTOR"}:
            raise ValueError("Invalid/duplicate test slot")
        if not all(row[name] for name in TEST_SLOT_FIELDS[:-1]):
            raise ValueError("Incomplete test slot")
        keys.add(key)


def _relation_identities(support_store, proposals):
    identities = set()
    for row in (*support_store.special_rows, *support_store.family_rows):
        if row.enabled:
            identities.add((row.owner_kind.upper(), row.owner_id, row.candidate_canonical))
    for proposal in proposals.values():
        if proposal["proposal_status"] in {"DRAFT", "READY_FOR_MEMBER_REVIEW", "UNIVERSAL_PASS"}:
            identities.add(("FAMILY", proposal["family_rule_id"], proposal["candidate_canonical"]))
    return identities


def validate_practical_use(rows, knowledge, profile_store, support_store=None, proposals=None) -> None:
    uses = {"CORE_ESTABLISHMENT", "VISIBLE_VARIATION", "STAGE9_OPERATION", "STAGE10_TEST", "NON_TAG_ROUTING"}
    if rows and (support_store is None or proposals is None):
        raise ValueError("Nonempty practical-use requires relation/proposal context")
    for row in rows:
        owner_ok = (row["owner_type"] == "SPECIAL" and row["owner_id"] in knowledge.special) or (
            row["owner_type"] == "FAMILY" and row["owner_id"] in profile_store.family_rules)
        if not owner_ok or row["candidate_canonical"] not in knowledge.canonical:
            raise ValueError("Invalid practical-use identity")
        if row["practical_use"] not in uses or row["stage10_test_priority"] not in {"HIGH", "MEDIUM", "LOW"}:
            raise ValueError("Invalid practical-use row")
        if not row["review_reason_ja"]:
            raise ValueError("Practical-use reason required")
        proposal_id = row["proposal_id"]
        identity = (row["owner_type"], row["owner_id"], row["candidate_canonical"])
        production = {
            (relation.owner_kind.upper(), relation.owner_id, relation.candidate_canonical)
            for relation in (*support_store.special_rows, *support_store.family_rows) if relation.enabled
        }
        if row["owner_type"] == "SPECIAL" and proposal_id:
            raise ValueError("SPECIAL practical-use cannot reference family proposal")
        if proposal_id:
            proposal = proposals.get(proposal_id)
            if not proposal or identity != ("FAMILY", proposal["family_rule_id"], proposal["candidate_canonical"]):
                raise ValueError("Practical-use proposal reference mismatch")
            if proposal["proposal_status"] not in {
                "DRAFT", "READY_FOR_MEMBER_REVIEW", "UNIVERSAL_PASS", "PROMOTED",
            }:
                raise ValueError("Practical-use requires active family proposal")
        elif identity not in production:
            raise ValueError("Practical-use must reference enabled production relation")


def validate_evidence_events(rows, knowledge, profile_store, source_ids, support_store=None, proposals=None,
                             source_kinds=None) -> None:
    effects = {"POSITIVE", "NEUTRAL", "NEGATIVE", "MIXED", "INCONCLUSIVE"}
    statuses = {"ACTIVE", "RETRACTED", "SUPERSEDED"}
    ids = {row["evidence_event_id"] for row in rows}
    if len(ids) != len(rows):
        raise ValueError("Duplicate evidence event ID")
    if rows and (support_store is None or proposals is None):
        raise ValueError("Nonempty evidence events require relation/proposal context")
    for row in rows:
        owner_ok = (row["owner_kind"] == "SPECIAL" and row["owner_id"] in knowledge.special) or (
            row["owner_kind"] == "FAMILY" and row["owner_id"] in profile_store.family_rules)
        if not owner_ok or row["candidate_canonical"] not in knowledge.canonical:
            raise ValueError("Invalid evidence event identity")
        if row["evidence_level"] not in EVIDENCE_LEVELS or row["observed_effect"] not in effects or row["event_status"] not in statuses:
            raise ValueError("Invalid evidence event enum")
        if row["evidence_source"] not in source_ids:
            raise ValueError("Unknown evidence event source")
        proposal_id = row["proposal_id"]
        if proposal_id:
            proposal = (proposals or {}).get(proposal_id)
            if not proposal or (row["owner_kind"], row["owner_id"], row["candidate_canonical"]) != (
                    "FAMILY", proposal["family_rule_id"], proposal["candidate_canonical"]):
                raise ValueError("Evidence event proposal reference mismatch")
            if proposal["proposal_status"] not in {"DRAFT", "READY_FOR_MEMBER_REVIEW", "UNIVERSAL_PASS", "PROMOTED"}:
                raise ValueError("Evidence event requires active family proposal")
        elif (row["owner_kind"], row["owner_id"], row["candidate_canonical"]) not in _relation_identities(support_store, {}):
            raise ValueError("Evidence event must reference production relation or proposal")
        if row["evidence_level"] in {"MODEL_OBSERVED", "USER_ENV_VERIFIED"} and not (
                row["test_profile_id"] and row["model_scope"] and row["evidence_ref"] and
                row["seed_set_ref"] and row["generation_condition_hash"] and row["result_ref"]):
            raise ValueError("Observed evidence requires reproducible test metadata")
        if row["evidence_level"] in {"MODEL_OBSERVED", "USER_ENV_VERIFIED"} and source_kinds is None:
            raise ValueError("Observed evidence requires source-kind context")
        if row["evidence_level"] == "MODEL_OBSERVED" and source_kinds.get(row["evidence_source"]) != "CONTROLLED_TEST":
            raise ValueError("MODEL_OBSERVED requires CONTROLLED_TEST source")
        if row["evidence_level"] == "USER_ENV_VERIFIED" and source_kinds.get(row["evidence_source"]) != "USER_TEST":
            raise ValueError("USER_ENV_VERIFIED requires USER_TEST source")
        if row["event_status"] in {"RETRACTED", "SUPERSEDED"} and row["supersedes_event_id"] not in ids:
            raise ValueError("Retracted/superseded event must reference existing event")


def effective_relation_records(support_store, special_ids):
    """Return resolver-effective relations, preserving family precedence and provenance."""
    records = []
    for special_id in sorted(special_ids, key=int):
        for candidate in support_store.candidates((special_id,)):
            records.extend((special_id, candidate.canonical, relation) for relation in candidate.relations)
    return tuple(records)
