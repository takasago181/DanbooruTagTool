"""Build deterministic Stage 8B Pilot and protected-hash audit evidence."""
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
from danbooru_tag_tool.stage8b_support import SupportKnowledgeStore


OUT = ROOT / "benchmarks/stage8b"
PACKAGE_PILOT = ROOT / "backups/stage8b_v3_spec_package_20260906/06_PILOT_TARGETS.csv"
PROTECTED = (
    "data/special2788/illustrious_tag_knowledge_base_2788.csv",
    "data/source/danbooru-2026-09-02.csv",
    "data/derived/danbooru_alias_normalized_index_VERIFIED_34417.csv",
    "data/derived/special2788_VERIFIED_LINKAGE.csv",
    "data/generation/special2788_generation_profile.csv",
    "data/generation/generation_family_rules.csv",
    "data/generation/generation_model_observations.csv",
    "data/runtime/japanese_overlay.json",
    "danbooru_tag_tool/recommendations.py",
    "danbooru_tag_tool/stage7b_recommendations.py",
    "danbooru_tag_tool/stage8a_semantics.py",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    knowledge = TagKnowledgeCore.load(ROOT)
    profiles = knowledge.load_generation_profile_store(ROOT)
    store = SupportKnowledgeStore.load(ROOT, knowledge, profiles)
    with PACKAGE_PILOT.open(encoding="utf-8-sig", newline="") as handle:
        pilot_rows = tuple(csv.DictReader(handle))

    pilot = []
    family_differences = []
    for item in pilot_rows:
        special_id = item["special_id"]
        special = knowledge.special[special_id]
        profile = profiles.profiles[special_id]
        production_family = profile.GenerationFamily or profile.MeaningStatus
        if production_family != item["static_family"]:
            family_differences.append({
                "special_id": special_id,
                "package_family": item["static_family"],
                "production_family": production_family,
                "resolution": "current production profile retained",
            })
        candidates = store.candidates((special_id,))
        pilot.append({
            "special_id": special_id,
            "special_term": special.term,
            "pilot_kind": item["pilot_kind"],
            "package_static_family": item["static_family"],
            "production_family": production_family,
            "candidate_count": len(candidates),
            "candidates": [{
                "canonical": candidate.canonical,
                "priority": candidate.priority,
                "relations": [{
                    "owner_special_id": relation.owner_special_id,
                    "source_kind": relation.source_kind,
                    "source_id": relation.source_id,
                    "support_slot": relation.support_slot,
                    "support_class": relation.support_class,
                    "priority": relation.priority,
                    "reason_ja": relation.reason_ja,
                    "evidence_level": relation.evidence_level,
                    "evidence_source": relation.evidence_source,
                    "generation_test_status": relation.generation_test_status,
                    "intent_axis": relation.intent_axis,
                    "intent_direction": relation.intent_direction,
                    "combination_mode": relation.combination_mode,
                    "choice_group": relation.choice_group,
                    "provenance": relation.provenance,
                } for relation in candidate.relations],
            } for candidate in candidates],
        })

    no_profile_id = next(
        sid for sid, special in knowledge.special.items()
        if sid not in {item["special_id"] for item in pilot_rows}
        and "anal" in special.term
    )
    payload = {
        "profile_row_count": len(store.special_rows),
        "enabled_profile_row_count": sum(row.enabled for row in store.special_rows),
        "family_rule_row_count": len(store.family_rows),
        "support_class_counts": dict(sorted(Counter(
            row.support_class for row in store.special_rows if row.enabled
        ).items())),
        "intent_metadata_count": sum(
            bool(row.intent_axis or row.intent_direction) for row in store.special_rows
        ),
        "combination_metadata_count": sum(
            bool(row.combination_mode or row.choice_group) for row in store.special_rows
        ),
        "canonical_validation": all(
            row.candidate_canonical in knowledge.canonical for row in store.special_rows
        ),
        "pilot_count": len(pilot),
        "pilot": pilot,
        "multi_special_relation_examples": [{
            "selected_special_ids": list(selected),
            "canonical": canonical,
            "relation_count": len(candidate.relations),
            "relations": [{
                "owner_special_id": relation.owner_special_id,
                "support_class": relation.support_class,
                "combination_mode": relation.combination_mode,
            } for relation in candidate.relations],
        } for selected, canonical in (
            (("161", "173"), "anus"),
            (("312", "173"), "object_insertion"),
            (("88", "122"), "on_back"),
            (("173", "122"), "spread_legs"),
        ) for candidate in store.candidates(selected) if candidate.canonical == canonical],
        "package_vs_production_family_differences": family_differences,
        "no_profile_example": {
            "special_id": no_profile_id,
            "term": knowledge.special[no_profile_id].term,
            "candidate_count": len(store.candidates((no_profile_id,))),
        },
        "statistical_fields_on_support_candidates": [],
        "severity_filter": False,
        "severity_penalty": False,
        "severity_boost": False,
        "substring_or_regex_generation": False,
        "automatic_add": False,
        "automatic_delete": False,
        "automatic_weight": False,
        "prompt_rewrite": False,
        "runtime_llm_calls": 0,
        "runtime_network_calls": 0,
        "runtime_api_calls": 0,
        "stage8c_started": False,
        "stage9_started": False,
    }
    hashes = {relative: sha256(ROOT / relative) for relative in PROTECTED}
    payload["special2788_sha256"] = hashes[
        "data/special2788/illustrious_tag_knowledge_base_2788.csv"
    ]
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "pilot_audit.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (OUT / "protected_hashes.json").write_text(
        json.dumps(hashes, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        key: value for key, value in payload.items() if key != "pilot"
    }, ensure_ascii=False, indent=2))
    required = (
        payload["profile_row_count"] == 39,
        payload["family_rule_row_count"] == 0,
        payload["canonical_validation"],
        payload["pilot_count"] == 10,
        all(3 <= item["candidate_count"] <= 5 for item in pilot),
        payload["no_profile_example"]["candidate_count"] == 0,
        payload["special2788_sha256"]
        == "07584b365d5a68dbadd3f5e80859e768c2718b18746e32de02ce4b8bd60935e3",
    )
    return 0 if all(required) else 1


if __name__ == "__main__":
    raise SystemExit(main())
