"""Generate deterministic Stage 8C coverage and boundary evidence."""
from __future__ import annotations

from collections import Counter, defaultdict
import csv
import hashlib
import json
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
    RESEARCH_SOURCE_FIELDS, REVIEW_FIELDS, TEST_SLOT_FIELDS, family_members,
    read_rows, validate_evidence_events, validate_family_applicability,
    validate_family_review, validate_family_state, validate_model_familiarity, validate_non_tag,
    validate_practical_use, validate_research_sources, validate_review_ledger,
    validate_test_slots, write_rows, validate_family_proposals, effective_relation_records,
)

OUT = ROOT / "benchmarks/stage8c"
SEMANTIC = ROOT / "data/semantic"
EXPECTED_STAGE8B_PACKAGE = {
    "danbooru_tag_tool/stage8b_support.py": "83f5617a36d48dfb730e21e2ac2957c8e4f6c00857b0971f6af6724f4e105dd2",
    "danbooru_tag_tool/ui.py": "5c83f6ca7dae2f164403cb13d3112a8ad85a8f201de351354c980daf31f98450",
    "tests/test_stage8b_support.py": "792eab534dfb971d4f05b8a116b7b9ff8f98a41229a73f7d958e9e9aa40e02d7",
}
PROTECTED_EXTRA = (
    "data/semantic/semantic_support_profiles.csv",
    "data/semantic/family_support_rules.csv",
    "danbooru_tag_tool/stage8b_support.py",
    "danbooru_tag_tool/ui.py",
    "tests/test_stage8b_support.py",
)
COVERAGE_FIELDS = (
    "special_id", "special_term", "layer", "static_family", "family_rule_id",
    "review_decision", "effective_coverage_mode", "effective_relation_count",
    "special_relation_count", "family_relation_count", "core_support_count",
    "optional_variation_count", "spatial_relation_count", "source_verified_count",
    "semantic_curated_count", "model_observed_count", "user_env_verified_count",
    "validation_status", "validation_note",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def json_cell(counter: Counter) -> str:
    return json.dumps(dict(sorted(counter.items())), ensure_ascii=False,
                      separators=(",", ":"))


def main() -> int:
    knowledge = TagKnowledgeCore.load(ROOT)
    profiles = knowledge.load_generation_profile_store(ROOT)
    support = SupportKnowledgeStore.load(ROOT, knowledge, profiles)
    review = read_rows(SEMANTIC / "stage8c_review_status.csv", REVIEW_FIELDS)
    review_by_id = {row["special_id"]: row for row in review}
    review_counts = validate_review_ledger(review, knowledge, support)
    family_review = read_rows(SEMANTIC / "stage8c_family_rule_review.csv", FAMILY_REVIEW_FIELDS)
    validate_family_review(family_review, profiles)
    research = read_rows(SEMANTIC / "stage8c_research_sources.csv", RESEARCH_SOURCE_FIELDS)
    validate_research_sources(research)
    source_ids = {row["source_id"] for row in research}
    proposals = validate_family_proposals(read_rows(
        SEMANTIC / "stage8c_family_relation_proposals.csv", FAMILY_PROPOSAL_FIELDS
    ), knowledge, profiles, source_ids)
    applicability_rows = read_rows(
        SEMANTIC / "stage8c_family_candidate_applicability.csv", APPLICABILITY_FIELDS
    )
    applicability = validate_family_applicability(
        applicability_rows, proposals, support.family_rows, knowledge, profiles
    )
    validate_family_state(family_review, proposals, support.family_rows, knowledge, profiles)
    familiarity = read_rows(SEMANTIC / "stage8c_model_familiarity.csv", MODEL_FAMILIARITY_FIELDS)
    validate_model_familiarity(familiarity, knowledge, source_ids)
    non_tag = read_rows(SEMANTIC / "stage8c_non_tag_strategy.csv", NON_TAG_FIELDS)
    validate_non_tag(non_tag, knowledge, source_ids)
    test_slots = read_rows(SEMANTIC / "stage10_test_slots.csv", TEST_SLOT_FIELDS)
    validate_test_slots(test_slots)
    practical = read_rows(SEMANTIC / "stage8c_practical_use.csv", PRACTICAL_USE_FIELDS)
    validate_practical_use(practical, knowledge, profiles, support, proposals)
    evidence_events = read_rows(
        SEMANTIC / "stage8c_relation_evidence_events.csv", EVIDENCE_EVENT_FIELDS
    )
    validate_evidence_events(evidence_events, knowledge, profiles, source_ids, support, proposals,
                             {row["source_id"]: row["source_kind"] for row in research})

    with (ROOT / "data/generation/audit/PROMOTION_PLAN_v1.csv").open(
            encoding="utf-8-sig", newline="") as handle:
        static_rows = tuple(csv.DictReader(handle))
    if (len(static_rows) != len(knowledge.special)
            or {row["SpecialID"] for row in static_rows} != set(knowledge.special)):
        raise ValueError("Static audit grouping does not cover exact Special IDs")
    static_by_id = {}
    for row in static_rows:
        sid = row["SpecialID"]
        if row["Tag"] != knowledge.special[sid].term:
            raise ValueError(f"Static audit identity mismatch: {sid}")
        static_by_id[sid] = row["GenerationFamily"]

    coverage = []
    for sid, special in knowledge.special.items():
        profile = profiles.profiles[sid]
        candidates = support.candidates((sid,))
        relations = tuple(r for candidate in candidates for r in candidate.relations)
        special_count = sum(r.source_kind == "special" for r in relations)
        family_count = sum(r.source_kind == "family" for r in relations)
        mode = ("SPECIAL_PLUS_FAMILY" if special_count and family_count else
                "SPECIAL_PROFILE" if special_count else
                "FAMILY_RULE" if family_count else "NONE")
        decision = review_by_id[sid]["review_decision"]
        valid = ((decision == "SUPPORT_DEFINED" and relations) or
                 (decision in {"NO_SUGGESTION", "UNRESOLVED"} and not relations) or
                 decision == "UNREVIEWED")
        evidence = Counter(r.evidence_level for r in relations)
        classes = Counter(r.support_class for r in relations)
        coverage.append({
            "special_id": sid, "special_term": special.term, "layer": special.layer,
            "static_family": static_by_id[sid],
            "family_rule_id": profile.FamilyRuleId,
            "review_decision": decision, "effective_coverage_mode": mode,
            "effective_relation_count": len(relations),
            "special_relation_count": special_count,
            "family_relation_count": family_count,
            "core_support_count": classes["CORE_SUPPORT"],
            "optional_variation_count": classes["OPTIONAL_VARIATION"],
            "spatial_relation_count": sum(r.support_slot == "SPATIAL_ASSIGNMENT" for r in relations),
            "source_verified_count": evidence["SOURCE_VERIFIED"],
            "semantic_curated_count": evidence["SEMANTIC_CURATED"],
            "model_observed_count": evidence["MODEL_OBSERVED"],
            "user_env_verified_count": evidence["USER_ENV_VERIFIED"],
            "validation_status": "PASS" if valid else "FAIL",
            "validation_note": "" if valid else "review decision/effective relation mismatch",
        })

    with (SEMANTIC / "stage8c_static_family_coverage_strategy.csv").open(
            encoding="utf-8-sig", newline="") as handle:
        strategy = {row["StaticFamily"]: row for row in csv.DictReader(handle)}
    groups = defaultdict(list)
    for row in coverage:
        groups[row["static_family"]].append(row)
    if set(groups) != set(strategy):
        raise ValueError("StaticFamily strategy/current production mismatch")
    static_summary = []
    for family in sorted(groups):
        rows = groups[family]
        decision = Counter(row["review_decision"] for row in rows)
        modes = Counter(row["effective_coverage_mode"] for row in rows)
        special_ids = {row["special_id"] for row in rows}
        effective_records = effective_relation_records(support, special_ids)
        relations = [relation for _, _, relation in effective_records]
        slots = Counter(row.support_slot for row in relations)
        intents = Counter(row.intent_axis or "UNASSERTED" for row in relations)
        combinations = Counter(row.combination_mode or "UNASSERTED" for row in relations)
        evidence = Counter(row.evidence_level for row in relations)
        s = strategy[family]
        if len(rows) != int(s["total_special"]):
            raise ValueError(f"StaticFamily total mismatch: {family}")
        static_summary.append({
            "static_family": family, "total": len(rows),
            "reviewed": len(rows) - decision["UNREVIEWED"],
            "support_defined": decision["SUPPORT_DEFINED"],
            "no_suggestion": decision["NO_SUGGESTION"],
            "unresolved": decision["UNRESOLVED"], "unreviewed": decision["UNREVIEWED"],
            "special_profile_coverage": modes["SPECIAL_PROFILE"],
            "family_rule_coverage": modes["FAMILY_RULE"],
            "special_plus_family_coverage": modes["SPECIAL_PLUS_FAMILY"],
            "core_support_relations": sum(r.support_class == "CORE_SUPPORT" for r in relations),
            "optional_variation_relations": sum(r.support_class == "OPTIONAL_VARIATION" for r in relations),
            "spatial_relation_count": slots["SPATIAL_ASSIGNMENT"],
            "static_spatial_yes": int(s["spatial_yes"]),
            "static_spatial_conditional": int(s["spatial_conditional"]),
            "support_slot_distribution": json_cell(slots),
            "intent_distribution": json_cell(intents),
            "combination_distribution": json_cell(combinations),
            "evidence_distribution": json_cell(evidence),
            "canonical_validation_failures": sum(
                canonical not in knowledge.canonical for _, canonical, _ in effective_records
            ),
        })

    members = family_members(profiles)
    family_review_by_id = {row["family_rule_id"]: row for row in family_review}
    family_summary = []
    for fid, rule in sorted(profiles.family_rules.items()):
        enabled = [row for row in support.family_rows if row.enabled and row.owner_id == fid]
        scoped_proposals = {
            proposal_id: proposal for proposal_id, proposal in proposals.items()
            if proposal["family_rule_id"] == fid
        }
        scoped_proposal_ids = set(scoped_proposals)
        scoped_applicability = [
            row for row in applicability_rows if row["proposal_id"] in scoped_proposal_ids
        ]
        family_applicability = validate_family_applicability(
            scoped_applicability, scoped_proposals, enabled, knowledge, profiles
        )
        family_summary.append({
            "family_rule_id": fid, "generation_family": rule.GenerationFamily,
            "member_count": len(members[fid]),
            "review_decision": family_review_by_id[fid]["review_decision"],
            "reviewed_member_count": int(family_review_by_id[fid]["reviewed_member_count"]),
            "enabled_family_relation_count": len(enabled),
            "universal_enabled_relation_count": family_applicability.universally_applicable,
            "blocked_enabled_relation_count": family_applicability.blocked,
            "missing_member_review_count": family_applicability.missing_member_reviews,
        })

    preview = []
    for row in sorted((r for r in support.special_rows if r.enabled),
                      key=lambda r: (int(r.owner_id), r.candidate_canonical)):
        preview.append({
            "evidence_event_id": f"EV_STAGE8B_{row.owner_id}_{row.candidate_canonical}",
            "owner_kind": "SPECIAL", "owner_id": row.owner_id,
            "candidate_canonical": row.candidate_canonical, "proposal_id": "",
            "evidence_level": row.evidence_level,
            "evidence_source": "SRC_STAGE8B_PILOT_CURATION",
            "evidence_ref": row.evidence_ref or "STAGE8B_PILOT",
            "test_profile_id": row.test_profile_id or "", "model_scope": row.model_scope or "",
            "seed_set_ref": "", "generation_condition_hash": "",
            "observed_effect": "INCONCLUSIVE", "observed_failures": "",
            "result_ref": "", "event_status": "ACTIVE", "supersedes_event_id": "",
            "note": "Dry-run preview only; production evidence ledger remains empty.",
        })
    validate_evidence_events(preview, knowledge, profiles, source_ids, support, proposals,
                             {row["source_id"]: row["source_kind"] for row in research})

    with (ROOT / "benchmarks/stage8b/protected_hashes.json").open(encoding="utf-8") as handle:
        stage8b_protected = json.load(handle)
    protected_paths = tuple(sorted(set(stage8b_protected) | set(PROTECTED_EXTRA)))
    protected = {path: sha256(ROOT / path) for path in protected_paths}
    protected_mismatches = {
        path: {"expected": expected, "actual": protected[path]}
        for path, expected in stage8b_protected.items() if protected[path] != expected
    }
    package_baseline = {
        path: {
            "expected": expected, "actual": protected[path],
            "status": ("MATCH" if protected[path] == expected else
                       "APPROVED_POST_PACKAGE_STAGE8B_RELATION_FIX"),
        } for path, expected in EXPECTED_STAGE8B_PACKAGE.items()
    }
    production_hashes = {
        path: protected[path] for path in (
            "data/semantic/semantic_support_profiles.csv",
            "data/semantic/family_support_rules.csv",
        )
    }
    expected_production = {
        "data/semantic/semantic_support_profiles.csv": "ec4d367053a3f92f6d9de85fc0f80e1be9c1b4f0a17d8786e5695be7e711a2b1",
        "data/semantic/family_support_rules.csv": "59609aadc82f9f4be97b82008159b55e4d738f41dbb9625c59be8a826fe7c4fd",
    }

    OUT.mkdir(parents=True, exist_ok=True)
    write_rows(OUT / "coverage_audit.csv", COVERAGE_FIELDS, coverage)
    write_rows(OUT / "static_family_summary.csv", tuple(static_summary[0]), static_summary)
    write_rows(OUT / "family_rule_summary.csv", tuple(family_summary[0]), family_summary)
    write_rows(OUT / "pilot_evidence_seed_preview.csv", EVIDENCE_EVENT_FIELDS, preview)
    extension_rows = [{
        "tool": name, "responsibility": responsibility,
        "reimplemented_in_stage8c": "false", "runtime_integration": "false",
    } for name, responsibility in (
        ("TagComplete Neo", "autocomplete/alias/translation/count/LoRA trigger"),
        ("Forge Couple", "regional conditioning and feature separation"),
        ("ControlNet", "pose and layout guidance"),
        ("ADetailer Neo", "local detection and inpaint"),
        ("Dynamic Prompts Neo", "wildcard and combinatorial syntax"),
        ("WD14 Tagger", "image interrogation aid"),
    )]
    write_rows(OUT / "extension_boundary_audit.csv", tuple(extension_rows[0]), extension_rows)
    (OUT / "protected_hashes.json").write_text(
        json.dumps(protected, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    summary = {
        "stage": "8C Phase1 Pilot001 implementation", "stage8c_final_decision": False,
        "pilot001_acceptance": "NOT COMPLETE",
        "total_special": len(coverage), "unique_special_ids": len({r["special_id"] for r in coverage}),
        "special_identity_mismatches": 0, "review_decision_counts": review_counts,
        "pilot_support_defined": sum(r["review_decision"] == "SUPPORT_DEFINED" for r in coverage),
        "static_family_count": len(static_summary), "family_rule_count": len(family_summary),
        "production_special_relation_rows": len(support.special_rows),
        "production_family_relation_rows": len(support.family_rows),
        "production_relation_hashes": production_hashes,
        "production_relation_hashes_match_pilot001_expected": production_hashes == expected_production,
        "family_applicability": applicability.__dict__ if hasattr(applicability, "__dict__") else {
            "enabled_family_relations": applicability.enabled_family_relations,
            "universally_applicable": applicability.universally_applicable,
            "blocked": applicability.blocked,
            "missing_member_reviews": applicability.missing_member_reviews,
        },
        "family_proposal_rows": len(proposals),
        "static_needs_spatial_yes": sum(int(r["static_spatial_yes"]) for r in static_summary),
        "static_needs_spatial_conditional": sum(int(r["static_spatial_conditional"]) for r in static_summary),
        "actual_spatial_relations": sum(int(r["spatial_relation_count"]) for r in coverage),
        "research_source_count": len(research),
        "primary_model_scope": "WAI-illustrious-SDXL v17",
        "primary_runtime": "Forge Neo", "wai_v17_training_cutoff": "UNKNOWN",
        "model_familiarity_rows": len(familiarity), "non_tag_strategy_rows": len(non_tag),
        "test_slot_rows": len(test_slots), "practical_use_rows": len(practical),
        "production_evidence_event_rows": len(evidence_events),
        "pilot_evidence_dry_run_rows": len(preview),
        "external_feature_reimplementations": 0,
        "runtime_external_calls": 0, "stage8c_phase1_started": True,
        "pilot001_implementation_complete": True, "pilot002_started": False,
        "stage9_started": False, "stage10_started": False,
        "stage8b_protected_mismatches": protected_mismatches,
        "package_stage8b_baseline_comparison": package_baseline,
        "validation_failures": sum(r["validation_status"] != "PASS" for r in coverage),
    }
    (OUT / "validation_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    required = (
        len(coverage) == 2788, len(static_summary) == 25,
        review_counts == {"SUPPORT_DEFINED": 28, "UNRESOLVED": 1, "UNREVIEWED": 2759},
        production_hashes == expected_production,
        len(support.special_rows) == 50, len(support.family_rows) == 1,
        not protected_mismatches, summary["validation_failures"] == 0,
        summary["static_needs_spatial_yes"] == 216,
        summary["static_needs_spatial_conditional"] == 677,
        summary["actual_spatial_relations"] == 0,
    )
    return 0 if all(required) else 1


if __name__ == "__main__":
    raise SystemExit(main())
